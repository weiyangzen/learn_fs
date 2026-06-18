# subset-b-008293 Research

Grouped research for RustFS utility HTTP, object metadata, IO, OS, path, retry, string, network helpers, and the `rustfs-zip` benchmark manifest/harness. Each section is source-tree-aligned and wrapped for deterministic reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/http/header_compat.rs -->
# sources/object-store/rustfs/crates/utils/src/http/header_compat.rs

## Purpose
Provides MinIO/RustFS compatibility helpers for internal HTTP headers. Callers work with suffix constants such as `force-delete` or `source-version-id`; the module constructs `x-rustfs-*` and `x-minio-*` keys so reads accept either ecosystem and writes emit both.

## Important APIs, Types, And Functions
The public suffix constants cover force-delete, replication reset/status, source object version/mtime/etag/deletemarker, proxy/replication request markers, and replication SSEC CRC. `is_encryption_metadata_key` classifies `x-rustfs-encryption-*` and `x-minio-encryption-*` metadata case-insensitively. `get_header` reads from an `http::HeaderMap`, preferring RustFS over MinIO and returning a borrowed `Cow<str>` when the header value is valid UTF-8. `insert_header` writes both prefixes using `HeaderValue::from_bytes`. HashMap equivalents are `get_header_map`, `insert_header_map`, and `remove_header_map`.

## Control Flow And State
The module is stateless. Helper functions build string keys on demand; read flow is RustFS key first, MinIO fallback. Insert flow validates the value and parsed header names before inserting each prefixed key, silently skipping invalid inputs.

## Dependencies And Integration Points
Depends on the `http` crate for `HeaderMap`, `HeaderValue`, and `HeaderName` parsing. It is re-exported through `utils/src/http/mod.rs` and feeds object/replication paths that must interoperate with existing MinIO metadata and request headers.

## Risks And Test Signals
Risk is mainly silent failure in `insert_header` when values are not valid header bytes, plus exact-case HashMap lookup in `get_header_map` while `HeaderMap` itself is case-insensitive. Unit tests cover encryption prefix classification and HeaderMap fallback/preference basics, but not invalid header bytes or case variants in HashMap keys.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/http/header_compat.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/http/headers.rs -->
# sources/object-store/rustfs/crates/utils/src/http/headers.rs

## Purpose
Centralizes HTTP/S3 header constants and classification helpers used across RustFS object APIs, metadata handling, signing, encryption, object lock, restore, checksum, replication, and Snowball import paths.

## Important APIs, Types, And Functions
The file exports a large constant catalog for standard HTTP headers, S3 `x-amz-*` headers, SSE/SSE-C headers, request IDs, checksums, object attributes, tagging, object lock, and Snowball compatibility keys. `HeaderExt` adds `lookup` to `HashMap<String, String>`, checking the given name, lowercase form, and Train-Case form. Static `LazyLock<HashMap<String, bool>>` tables hold supported response query values, metadata-copy headers, and SSE headers. Public predicates include `is_standard_query_value`, `is_storageclass_header`, `is_standard_header`, `is_sse_header`, `is_amz_header`, `is_rustfs_header`, and `is_minio_header`.

## Control Flow And State
Runtime state is limited to lazily initialized immutable lookup tables. Classifiers normalize input to lowercase before table checks or prefix checks. `HeaderExt::lookup` tries three concrete spellings rather than scanning all map keys.

## Dependencies And Integration Points
Uses `convert_case` for Train-Case key generation and is re-exported by the HTTP module. `obj/metadata.rs` imports the RustFS/MinIO/internal classification helpers to filter user metadata. The constants are integration glue for S3-compatible request parsing, response emission, and metadata persistence.

## Risks And Test Signals
The constant list is broad but not self-validating; drift against AWS S3 behavior or internal callers is possible. `HeaderExt::lookup` can miss uncommon casing because it does not compare all keys case-insensitively. There are no local unit tests in this file, so coverage is indirect through consumers such as object metadata filtering.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/http/headers.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/http/ip.rs -->
# sources/object-store/rustfs/crates/utils/src/http/ip.rs

## Purpose
Extracts client source IP and scheme from reverse-proxy headers. It supports de-facto `X-Forwarded-*` and `X-Real-IP` headers plus RFC 7239 `Forwarded`.

## Important APIs, Types, And Functions
Constants define `x-forwarded-for`, `x-forwarded-proto`, `x-forwarded-scheme`, and `x-real-ip`. `get_source_scheme` checks `X-Forwarded-Proto`, `X-Forwarded-Scheme`, then parses `Forwarded` for `proto=http|https`. `get_source_ip_from_headers` checks `X-Forwarded-For` when `_RUSTFS_API_XFF_HEADER` is `on`, falls back to `X-Real-IP`, then `Forwarded for=...`. `get_source_ip_raw` falls back to `remote_addr` and strips socket ports when possible. `get_source_ip` brackets IPv6-like results.

## Control Flow And State
Two `LazyLock<Regex>` values parse `Forwarded` fields. The only external state is `_RUSTFS_API_XFF_HEADER`, defaulting to enabled. The XFF parser only splits on comma-space, not a bare comma, and the Forwarded parser extracts the first `for=` value.

## Dependencies And Integration Points
Depends on `http::HeaderMap`, `regex`, `std::env`, and socket parsing. This module is re-exported via `http/mod.rs` for request logging, auditing, policy, or API handlers that need client identity behind proxies.

## Risks And Test Signals
Trusting forwarded headers is security-sensitive; correctness depends on deployment-level trusted proxy controls. XFF comma parsing may retain multiple values if proxies emit `a,b` without a space. Unit tests cover basic scheme/IP extraction, remote fallback parsing, and IPv6 bracketing but not disabled XFF, malformed Forwarded forms, or proxy trust boundaries.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/http/ip.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/http/metadata_compat.rs -->
# sources/object-store/rustfs/crates/utils/src/http/metadata_compat.rs

## Purpose
Implements dual-prefix internal system metadata compatibility between RustFS `x-rustfs-internal-*` keys and MinIO `x-minio-internal-*` keys for persisted object metadata and xl.meta migration/interoperability.

## Important APIs, Types, And Functions
Exports prefix constants, many internal suffix constants for inline data, healing, compression, actual sizes, CRC, transition/tiering, free versions, purge/replica/replication status, object-lock timestamps, tagging timestamp, and replication reset. `is_internal_key`, `has_internal_suffix`, `strip_internal_prefix`, `internal_key_starts_with`, `internal_key_strip_suffix_prefix`, and `internal_key_rustfs` classify or construct keys. `insert_str`, `get_str`, `contains_key_str`, and `remove_str` operate on `HashMap<String, String>`. Byte-map equivalents support `HashMap<String, Vec<u8>>`.

## Control Flow And State
The module is stateless. String-map reads prefer RustFS then MinIO and finally scan keys case-insensitively. String removal deletes exact keys and retains away any case-insensitive matches. Byte-map helpers only use exact key lookup/removal.

## Dependencies And Integration Points
Uses only `std::collections::HashMap`. It is re-exported through `http/mod.rs` and is directly relevant to object metadata persistence, replication, healing, transition, and MinIO-compatible imports.

## Risks And Test Signals
Writing both prefixes duplicates persisted metadata and requires consumers to handle paired values consistently. Byte-map helpers do not perform case-insensitive fallback, unlike string helpers. Tests cover prefix classification, suffix detection, and mixed-case MinIO string metadata lookup/removal, but not byte-map casing or conflict resolution when RustFS and MinIO values differ.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/http/metadata_compat.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/http/mod.rs -->
# sources/object-store/rustfs/crates/utils/src/http/mod.rs

## Purpose
Defines the public HTTP utility module surface for the `rustfs-utils` crate.

## Important APIs, Types, And Functions
Declares `header_compat`, `headers`, `ip`, and `metadata_compat`, then glob re-exports all four modules. This lets callers import HTTP constants, metadata compatibility helpers, proxy source-IP helpers, and dual-prefix header helpers from `rustfs_utils::http::*`.

## Control Flow And State
There is no runtime control flow or state. Its behavior is compile-time module composition.

## Dependencies And Integration Points
Depends on sibling HTTP modules. It is gated by `#[cfg(feature = "http")]` in `lib.rs`, so the whole API surface appears only when the crate's `http` feature is enabled.

## Risks And Test Signals
Glob re-exports make naming conflicts possible as the HTTP utility surface grows. There are no direct tests; validation is through successful compilation and tests in child modules.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/http/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/io.rs -->
# sources/object-store/rustfs/crates/utils/src/io.rs

## Purpose
Provides async IO helpers and unsigned varint encoding/decoding utilities used by RustFS streaming and binary metadata code.

## Important APIs, Types, And Functions
`write_all` loops over `AsyncWrite::write` until all bytes are written or the writer returns zero, returning the total bytes written. `read_full_or_eof` reads into a buffer until full, EOF, or error, returning `None` for EOF before any bytes and `Some(n)` for partial or full reads. `read_full` wraps that helper and maps initial EOF to `UnexpectedEof`. `put_uvarint`, `put_uvarint_len`, and `uvarint` implement Go-style unsigned varint encode/decode with overflow and incomplete-buffer signaling.

## Control Flow And State
The async read/write helpers are stateless loops over caller-owned reader/writer values. `read_full_or_eof` preserves `InvalidData` errors after partial reads but wraps other post-partial errors as `UnexpectedEof`. `uvarint` accumulates seven-bit chunks and returns `(0, 0)` for incomplete data or `(0, negative_count)` on overflow.

## Dependencies And Integration Points
Depends on `tokio::io::{AsyncRead, AsyncReadExt, AsyncWrite, AsyncWriteExt}`. Exported through `lib.rs` under the `io` feature; `retry.rs` is only compiled when both `net` and `io` features are enabled.

## Risks And Test Signals
`write_all` returns short success if a writer yields `Ok(0)`, which differs from Tokio's usual `write_all` error semantics and may hide stalled writers. `read_full` intentionally allows short reads after some data, despite its name. Tests cover exact, short, empty, large reads, partial writes, and varint zero/max/overflow/incomplete cases.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/io.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/ip.rs -->
# sources/object-store/rustfs/crates/utils/src/ip.rs

## Purpose
Provides simple local-machine IP discovery helpers with a loopback fallback.

## Important APIs, Types, And Functions
`get_local_ip` attempts `local_ip_address::local_ip()` first and then `local_ip_address::local_ipv6()`, returning `Option<IpAddr>`. `get_local_ip_with_default` converts the result to a string and falls back to `127.0.0.1`.

## Control Flow And State
No persistent state is kept. Each call queries the `local_ip_address` crate. Fallback behavior is deterministic only when no address is found.

## Dependencies And Integration Points
Uses `std::net::{IpAddr, Ipv4Addr}` and the `local_ip_address` crate. It is exposed from `lib.rs` under the `ip` feature and is a smaller counterpart to the richer `net.rs` local-interface helpers.

## Risks And Test Signals
Tests assume the host can discover at least one local IP and that repeated calls are stable; those are environment-sensitive in containers, CI, or systems with dynamic interfaces. Functional risk is low, but the selected IP may not match the desired bind or advertise address on multi-homed hosts.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/ip.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/lib.rs -->
# sources/object-store/rustfs/crates/utils/src/lib.rs

## Purpose
Defines the root module graph and public re-export policy for `rustfs-utils`.

## Important APIs, Types, And Functions
Feature gates expose `ip`, `net`, `http`, `retry`, `io`, `hash`, `os`, `path`, `string`, `crypto`, `compress`, `dirs`, and `obj`. Several modules are glob re-exported at crate root: `net`, `hash`, `io`, `ip`, `crypto`, `compress`, `dunce`, `envs`, and `logging`. `logging` and `envs` are always compiled; `obj` is feature-gated but not glob re-exported.

## Control Flow And State
No runtime behavior. Compile-time feature selection controls dependency surface and visible APIs. `retry` is gated by both `net` and `io`, reflecting its dependency on network/http retry classification and stream behavior.

## Dependencies And Integration Points
Integrates all utility submodules into a single crate-level public API. Downstream crates can either use feature-qualified modules or root-level glob exports depending on enabled features.

## Risks And Test Signals
Glob re-exports can create API ambiguity and semver friction when modules add names. Feature combinations need compile coverage because some modules depend on others conditionally. There are no tests in this file; compile checks across feature matrices are the primary signal.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/logging.rs -->
# sources/object-store/rustfs/crates/utils/src/logging.rs

## Purpose
Provides display/debug masking for access keys or similar secrets before they are written to logs.

## Important APIs, Types, And Functions
`MaskedAccessKey<'a>(pub &'a str)` is a lightweight wrapper. Its `Display` implementation emits an empty string for empty input, `***` for one to four characters, first and last character with `***` for five to eight characters, and first four plus last four with `***` for longer values. `Debug` delegates to `Display`.

## Control Flow And State
The wrapper is stateless and allocates a `Vec<char>` to mask by character count rather than raw byte index, avoiding UTF-8 slicing bugs.

## Dependencies And Integration Points
Uses only `std::fmt` and is always exported from `lib.rs`. It should be used at log call sites that include access keys or derived identifiers.

## Risks And Test Signals
Masking preserves length class and edge characters, so it reduces accidental disclosure but is not anonymization. Very short secrets are fully hidden. Unit tests cover empty, short, medium, long, and `Debug` formatting.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/logging.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/net.rs -->
# sources/object-store/rustfs/crates/utils/src/net.rs

## Purpose
Provides network utility functions for local address validation, hostname resolution, endpoint URL construction, available-port discovery, stream truncation, and host display/parsing.

## Important APIs, Types, And Functions
`is_socket_addr` validates IP/socket strings, including scoped IPv6 zone identifiers. `check_local_server_addr`, `is_local_host`, `must_get_local_ips`, `get_host_ip`, `parse_and_resolve_address`, and `get_available_port` support bind/listen address validation. `get_endpoint_url`, `get_default_location`, and `is_custom_query_value` support S3 endpoint/query handling. `XHost` stores a resolved host name, port, and port-set flag, with `Display` and `TryFrom<String>`. `bytes_stream` truncates an async bytes stream to a declared content length.

## Control Flow And State
`LOCAL_IPS` is a process-global lazy snapshot from `must_get_local_ips` with loopback fallback. DNS resolution uses a global `DNS_CACHE` with five-minute TTL and a test-only custom resolver behind `RwLock`. `get_host_ip` checks the cache for domains, resolves, caches up to about 1000 entries, and logs misses/errors. `parse_and_resolve_address` treats `:port` as IPv6 unspecified bind and replaces port zero with an ephemeral port. `bytes_stream` decreases a remaining counter and truncates oversized chunks.

## Dependencies And Integration Points
Uses `bytes`, `futures`, `transform_stream`, `url`, `netif`, standard sockets, and `tracing`. It is exported under the `net` feature and is central to server startup validation and network-aware endpoint behavior.

## Risks And Test Signals
`LOCAL_IPS` is fixed after first access, so interface changes are not reflected. `get_available_port` has an inherent race after releasing the listener. `bytes_stream` can underflow if the stream continues after remaining reaches zero and a nonempty chunk is seen. Domain resolution tests use a mock resolver with a global lock; other tests still depend on local interfaces and localhost resolution. Unit tests cover socket parsing, local host checks, DNS mock paths, XHost formatting/parsing, bind parsing, and IPv6 zones.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/net.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/obj/metadata.rs -->
# sources/object-store/rustfs/crates/utils/src/obj/metadata.rs

## Purpose
Extracts user-defined object metadata from a larger metadata map by removing system, S3, RustFS, and MinIO internal keys.

## Important APIs, Types, And Functions
`extract_user_defined_metadata` takes `&HashMap<String, String>` and returns a new map. It excludes standard headers such as content type, cache control, length, MD5, date, ETag, and last-modified; skips internal RustFS/MinIO metadata via `is_internal_key`; strips `x-amz-meta-` and `x-rustfs-meta-` prefixes into user keys; skips other `x-amz-*`, `x-rustfs-*`, and `x-minio-*` headers; and preserves all other keys as user-defined.

## Control Flow And State
The function is a single pass with a fresh output map. It lowercases keys for classification and inserts stripped user-metadata keys in lowercase, while unprefixed user keys retain their original spelling.

## Dependencies And Integration Points
Imports HTTP classification helpers from `crate::http`, so it depends on HTTP feature availability within the `obj` feature configuration. It is re-exported by `obj/mod.rs` and used wherever object metadata must be shown or propagated without system internals.

## Risks And Test Signals
Lowercasing prefixed user metadata can change key spelling, and collisions can overwrite values when differently cased/prefixed keys normalize to the same user key. The doc note correctly warns returned keys may differ from input keys. Tests cover system-header exclusion, AMZ/RustFS prefix stripping, MinIO exclusion, mixed cases, empty input, and case-insensitive filtering.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/obj/metadata.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/obj/mod.rs -->
# sources/object-store/rustfs/crates/utils/src/obj/mod.rs

## Purpose
Defines the public object utility module surface.

## Important APIs, Types, And Functions
Declares the private `metadata` module and re-exports its public items, currently `extract_user_defined_metadata`.

## Control Flow And State
No runtime logic or state. This is a compile-time module wrapper.

## Dependencies And Integration Points
Enabled by `#[cfg(feature = "obj")]` in `lib.rs`. It gives downstream callers a stable `rustfs_utils::obj::*` location for object-related helpers.

## Risks And Test Signals
Glob re-export is small today but can become ambiguous as object utilities grow. There are no direct tests; the child metadata module carries the behavioral tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/obj/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/os/fs_type.rs -->
# sources/object-store/rustfs/crates/utils/src/os/fs_type.rs

## Purpose
Maps Linux filesystem magic numbers from `statfs` into human-readable filesystem type strings for disk diagnostics.

## Important APIs, Types, And Functions
`get_fs_type(fs_type: u64) -> &'static str` is crate-private and returns names for TMPFS, MSDOS, NFS, EXT4, ecryptfs, overlayfs, REISERFS, XFS, BTRFS, CEPH, EXFAT, EROFS, F2FS, ISOFS, FUSE, SQUASHFS, CIFS, SMB2, V9FS, and BCACHEFS, with `UNKNOWN` fallback. Comments list unverified magic values deliberately left out.

## Control Flow And State
Pure match expression, no state or IO.

## Dependencies And Integration Points
Compiled on Linux and in tests through `os/mod.rs`; `linux.rs::get_info` uses it to populate `DiskInfo.fstype`.

## Risks And Test Signals
The mapping can drift as new filesystems appear or magic constants differ. Unknown values remain safe but less informative. Tests verify representative common and verified Linux UAPI magic numbers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/os/fs_type.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/os/linux.rs -->
# sources/object-store/rustfs/crates/utils/src/os/linux.rs

## Purpose
Implements Linux disk information, physical-device identity, nested mount validation, and block IO statistics.

## Important APIs, Types, And Functions
`get_info` uses `rustix::fs::statfs` and `stat` to build `DiskInfo` with total/free/used bytes, inode counts, filesystem type, and device major/minor. `calculate_space_usage` handles reserved blocks and caps anomalous `bavail > bfree`. `same_disk` compares `st_dev`. `get_physical_device_ids` resolves `/sys/dev/block/<major>:<minor>` and recursively follows `slaves` to leaf devices. `check_cross_device_mounts` parses `/proc/mounts` and rejects nested child mount points under export paths. `get_drive_stats` reads `/sys/dev/block/<major>:<minor>/stat` into `IOStats`.

## Control Flow And State
The only persistent state is `BAVAIL_GT_BFREE_WARNING_PATHS`, a `OnceLock<Mutex<BTreeSet<PathBuf>>>` that limits warnings to once per path. Sysfs traversal falls back to `major:minor` when the sysfs link is absent. Mount validation normalizes paths to trailing-slash form before prefix comparisons.

## Dependencies And Integration Points
Uses `rustix`, `/sys`, `/proc/mounts`, `std::fs`, and `tracing::warn`. Re-exported from `os/mod.rs` on Linux and used by storage startup and health/diagnostic code that needs disk identity and capacity.

## Risks And Test Signals
Prefix mount checks are string-based and rely on normalized absolute paths; symlink/canonical path policy must be handled by callers. Device ID resolution depends on Linux sysfs layout and permissions. Tests cover device-mapper flattening, partition normalization, mount parsing, invalid export paths, fallback IDs, and several space-accounting edge cases.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/os/linux.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/os/mod.rs -->
# sources/object-store/rustfs/crates/utils/src/os/mod.rs

## Purpose
Provides the cross-platform OS/disk utility facade and shared data structures.

## Important APIs, Types, And Functions
Conditionally declares `fs_type`, `linux`, `unix`, and `windows` modules and re-exports platform-specific `get_info`, `same_disk`, `get_physical_device_ids`, `check_cross_device_mounts`, and `get_drive_stats`; Windows additionally exports `get_volume_serial_number`. `IOStats` models Linux-style block IO counters. `DiskInfo` models capacity, inode counts, filesystem type, device major/minor, name, rotational flag, and request depth.

## Control Flow And State
No runtime state in the facade. Compile-time cfg selects the implementation backend.

## Dependencies And Integration Points
Enabled from `lib.rs` under the `os` feature. Storage initialization, disk validation, monitoring, and platform diagnostics consume the exported functions and shared structs.

## Risks And Test Signals
Semantics differ by platform: Linux has real nested mount and IO stat behavior, while other platforms have no-op/default parts. Tests validate valid/invalid disk info, same-disk behavior, and include an ignored drive-stats default test due to CI instability.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/os/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/os/unix.rs -->
# sources/object-store/rustfs/crates/utils/src/os/unix.rs

## Purpose
Implements non-Linux Unix disk utilities using POSIX `statvfs`/`stat`, with simplified physical-device and mount checks.

## Important APIs, Types, And Functions
`get_info` uses `rustix::fs::statvfs` to compute total/free/used bytes from fragment size, available blocks, and reserved blocks, then uses `stat` for major/minor. `same_disk` compares `st_dev`. `get_physical_device_ids` returns a single `major:minor` string. `check_cross_device_mounts` is a no-op. `get_drive_stats` returns default `IOStats` on non-Linux.

## Control Flow And State
Stateless. `get_info` validates `bavail <= bfree`, reserved blocks not exceeding total blocks, and free not exceeding total before returning `DiskInfo`.

## Dependencies And Integration Points
Compiled for Unix targets other than Linux. Uses `rustix::fs::{statvfs, stat}` and shared `DiskInfo`/`IOStats` from `os/mod.rs`.

## Risks And Test Signals
Filesystem type is always `UNKNOWN`, nested mount validation is absent, and physical identity is less precise than Linux leaf-device traversal. Shared facade tests exercise basic `get_info` and `same_disk` behavior; platform-specific edge coverage is limited.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/os/unix.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/os/windows.rs -->
# sources/object-store/rustfs/crates/utils/src/os/windows.rs

## Purpose
Implements Windows disk capacity, filesystem type, volume identity, and platform-compatible stubs for mount/stat APIs.

## Important APIs, Types, And Functions
`get_info` calls `GetDiskFreeSpaceExW` and `GetDiskFreeSpaceW` to populate total/free/used bytes and cluster counts, and `get_windows_fs_type` to populate filesystem type. `get_volume_name` wraps `GetVolumePathNameW`. `same_disk` compares volume root paths. `get_physical_device_ids` returns the volume path string. `get_volume_serial_number` returns the Windows volume serial. `check_cross_device_mounts` and `get_drive_stats` are no-op/default equivalents.

## Control Flow And State
No persistent state. Path strings are converted to null-terminated UTF-16 with `to_wide_path`; unsafe Windows API calls write into stack variables and fixed `MAX_PATH` buffers. `get_info` rejects free space greater than total.

## Dependencies And Integration Points
Uses the `windows` crate and `std::os::windows::ffi::OsStrExt`. Re-exported by `os/mod.rs` on Windows for storage/disk diagnostics.

## Risks And Test Signals
Fixed `MAX_PATH` buffers can limit unusual long-path scenarios. Physical device identity is volume-based rather than true underlying disk topology. Mount validation and IO stats are placeholders. Coverage is mostly through shared OS facade tests; unsafe API paths need Windows CI to validate.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/os/windows.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/path.rs -->
# sources/object-store/rustfs/crates/utils/src/path.rs

## Purpose
Implements object-path and filesystem-path helpers, including MinIO-style directory object encoding, slash normalization, path cleaning, bucket/object splitting, and ETag trimming.

## Important APIs, Types, And Functions
Constants define `GLOBAL_DIR_SUFFIX`, `/`, and `__XLDIR__/`. `is_separator`, `has_suffix`, `has_prefix`, and `strings_has_prefix_fold` handle platform-aware separators/casing. `encode_dir_object`, `is_dir_object`, and `decode_dir_object` translate trailing-slash directory objects to `__XLDIR__`. `retain_slash`, `path_join`, `path_join_buf`, `clean`, `split`, `dir`, `path_to_bucket_object_with_base_path`, `path_to_bucket_object`, `base_dir_from_prefix`, and `trim_etag` provide path manipulation. `LazyBuf` supports allocation-on-change during `clean`.

## Control Flow And State
The module is stateless. `path_join` concatenates components with `/`, detects whether cleaning is needed, and preserves a trailing slash from the final element. `clean` follows Go path-cleaning rules: collapse repeated separators, remove `.`, resolve inner `..`, and keep leading `..` on relative paths. Windows branches treat backslash as a separator and compare prefixes/suffixes case-insensitively.

## Dependencies And Integration Points
Uses `std::path::{Path, PathBuf}` and is exposed under the `path` feature. It is likely consumed by storage layout, bucket/object parsing, and compatibility with MinIO directory-marker semantics.

## Risks And Test Signals
`split` returns `(path, "")` when no separator, which differs from common dirname/basename APIs and is relied on by `dir`. Manual byte-based cleaning assumes separators are ASCII and treats non-ASCII as needing cleaning before copying bytes unchanged. Tests are extensive for Unix-style cleaning, joining, ETag trimming, and Windows-specific separator/unicode cases under Windows cfg.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/path.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/retry.rs -->
# sources/object-store/rustfs/crates/utils/src/retry.rs

## Purpose
Provides retry timing and retryability classification for S3/HTTP/request errors.

## Important APIs, Types, And Functions
Constants include `MAX_RETRY`, jitter bounds, and default retry unit/cap durations. `RetryTimer` is a `Stream<Item = ()>` with configurable max retries, base sleep, cap, jitter, and random factor. Retry classifiers are `is_s3code_retryable`, `is_s3code_in_message_retryable`, `is_http_status_retryable`, and `is_request_error_retryable`. Static retryable S3 codes include throttling, timeout, internal error, expired token, and slowdown variants; HTTP statuses include 408, 429, 500, 502, 503, and 504.

## Control Flow And State
`RetryTimer::poll_next` computes exponential backoff from remaining attempts, caps it, optionally subtracts jitter, initializes or resets a Tokio interval, and yields until attempts are exhausted. Classifiers use immutable `LazyLock<Vec<_>>` lists. Request error classification matches selected transient `ErrorKind` values.

## Dependencies And Integration Points
Uses `futures::Stream`, `hyper::http::StatusCode`, and `tokio::time::Interval`. Compiled only when `net` and `io` features are enabled.

## Risks And Test Signals
The timer uses `base_sleep * (1 << attempt)`, so very large retry counts can overflow shift/multiplication before the cap is applied. Substring S3 matching is intentionally case-sensitive and can produce false positives if retryable code text appears in unrelated messages. Tests cover stream retry count/zero retries and S3 message matching behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/retry.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/string.rs -->
# sources/object-store/rustfs/crates/utils/src/string.rs

## Purpose
Implements string parsing and pattern helpers for booleans, wildcard matching, suffix checks, case-insensitive prefixes, and MinIO-style ellipsis expansion.

## Important APIs, Types, And Functions
`parse_bool` and `parse_bool_with_default` accept selected true/false spellings. `match_simple`, `match_pattern`, `has_pattern`, `match_as_pattern_prefix`, and private `deep_match_rune` implement `*`/`?` wildcard matching. `has_string_suffix_in_slice` performs case-insensitive suffix matching with `*` wildcard. `Pattern` stores an ellipsis prefix/suffix and sequence; `ArgPattern` stores multiple patterns and expands cartesian products. `has_ellipses`, `find_ellipses_patterns`, and `parse_ellipses_range` detect and expand `{N...M}` decimal/hex ranges up to 10,000 entries.

## Control Flow And State
Only `ELLIPSES_RE` is global lazy state. Wildcard matching is recursive and byte-based. Ellipsis parsing uses regex captures from the rightmost matching group, builds patterns, rejects leftover braces, detects hex by A-F characters, preserves padding based on the end bound width, and rejects descending/oversized ranges.

## Dependencies And Integration Points
Uses `regex` and `std::io::Error`. Exposed under the `string` feature and likely feeds command-line/config expansion and matching logic elsewhere in RustFS.

## Risks And Test Signals
Wildcard matching operates on bytes, not Unicode scalar values; `?` can split UTF-8. Recursive `*` matching can be expensive on adversarial patterns. Boolean parsing is not fully case-insensitive for words like `Enabled`. Ellipsis expansion can still generate large cartesian products across multiple ranges because the per-range cap is 10,000. Tests heavily cover ellipsis detection/parsing, hex/padded ranges, invalid formats, oversize rejection, and Windows GUID false positives.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/utils/src/string.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/zip/Cargo.toml -->
# sources/object-store/rustfs/crates/zip/Cargo.toml

## Purpose
Defines the `rustfs-zip` crate package metadata, dependencies, benchmark target, and Linux-specific dependency feature extension.

## Important APIs, Types, And Functions
Package metadata uses workspace edition/license/repository/rust-version/version/homepage, documents the crate as ZIP handling for RustFS, and disables doctests for the library. The `zip_benchmark` Criterion bench is registered with `harness = false`. Runtime dependencies are `async-compression` with Tokio and bzip2/gzip/zlib/zstd/xz features, `tokio` with fs/io-util/macros, `tokio-stream`, `astral-tokio-tar`, `thiserror`, and `zip`. Dev dependencies are `criterion` with HTML reports and `tempfile`. On Linux, Tokio also enables `io-uring`.

## Control Flow And State
No runtime control flow. Cargo feature resolution controls available compression formats and Linux async IO behavior.

## Dependencies And Integration Points
This manifest ties the zip crate to the workspace dependency versions and lint policy. The benchmark file in `benches/zip_benchmark.rs` depends on the bench declaration and dev dependencies here.

## Risks And Test Signals
Linux target-specific Tokio feature unification can affect behavior or dependency graph only on Linux. Broad compression feature enablement increases build surface. Benchmark presence is the main performance signal; tests are in other crate sources not part of this work item.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/zip/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/zip/benches/zip_benchmark.rs -->
# sources/object-store/rustfs/crates/zip/benches/zip_benchmark.rs

## Purpose
Provides Criterion benchmarks for tar-family extraction, zip creation/extraction round trips, extraction hotspot breakdowns, and object-archive extraction scenarios.

## Important APIs, Types, And Functions
`build_runtime` creates a current-thread Tokio runtime. `build_tar_payload` builds in-memory tar data through a duplex stream; `build_compressed_tar_payload` compresses it with `rustfs_zip::Compressor`. `bench_tar_family_extract` benchmarks gzip/zstd tar extraction with callback counting. `bench_zip_helper_round_trip` creates and extracts matrices of flat/nested/deep zip files. `bench_zip_helper_hotspot_breakdown` isolates tempdir setup, zip creation, zip extraction, summary-only extraction, raw `zip::ZipArchive` reading, and file-write costs. `build_object_archive_files` constructs synthetic object metadata/payload layouts. `bench_zip_object_archive_extract` benchmarks full and summary-only extraction for metadata-heavy and mixed archives.

## Control Flow And State
Benchmarks build deterministic payload vectors, use temp directories per iteration to isolate filesystem side effects, and wrap result counts/byte totals in `black_box`. Async crate APIs are driven through `runtime.block_on`. Atomic counters are used for tar callback counts.

## Dependencies And Integration Points
Depends on Criterion, `rustfs_zip` public APIs, `tempfile`, `tokio_tar`, and the upstream `zip` crate. It is registered by the crate manifest and provides performance visibility for archive helper APIs.

## Risks And Test Signals
The benchmark measures tempdir and filesystem overhead as part of several cases; the hotspot group intentionally breaks this down. Payloads are synthetic repeated bytes, so compression ratios may not reflect real object data. Bench assertions validate enclosed names and entry size limits in the reader-only path, but this is performance coverage rather than correctness testing.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/zip/benches/zip_benchmark.rs -->
