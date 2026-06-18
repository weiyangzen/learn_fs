# subset-b-008246 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/local.rs -->
# sources/object-store/rustfs/crates/ecstore/src/disk/local.rs

## Purpose
This file implements the concrete local filesystem backend for the `DiskAPI` abstraction used by RustFS erasure-coded object storage. It maps bucket/object/version operations to directories, `xl.meta` metadata files, erasure data directories, temporary staging paths, and the `.rustfs.sys` control tree on a mounted local disk. It is the main persistence boundary for local disks: it validates endpoint identity against `format.json`, performs object part verification, writes and updates RustFS file metadata, walks object namespaces, handles delete/trash cleanup, and exposes disk capacity/state information.

## Important APIs, types, and functions
`LocalDisk` holds the disk root, `.rustfs.sys/format.json` path, cached `FormatInfo`, endpoint identity, disk-info cache, scan counter, path cache, startup-cleanup latch, and background cleanup exit signal. `FormatInfo` caches the disk UUID, serialized format bytes, filesystem metadata, and last freshness check. `InternalBuf` allows internal writes from borrowed bytes or owned `Bytes`.

`FileCacheReclaimReader` and `FileCacheReclaimWriter` wrap `tokio::fs::File` and optionally call Linux `fadvise(DontNeed)` after large reads/writes or macOS `F_NOCACHE`; metrics are emitted through `rustfs_page_cache_reclaim_*`. The reclaim thresholds are driven by `rustfs_config` environment variables.

`LocalDisk::new` is the constructor. It resolves the endpoint root, ensures the data-usage layout, optionally moves stale startup temp state aside, loads and validates `format.json`, builds a one-second `Cache<DiskInfo>`, creates required metadata volumes, and spawns the deleted-object cleanup loop.

Path helpers include `resolve_local_disk_root`, `resolve_abs_path`, `get_object_path`, `get_bucket_path`, `check_valid_path`, `get_object_paths_batch`, and `normalize_path_components`. These enforce root confinement and optimize repeated path construction through a `parking_lot::RwLock<HashMap<...>>`.

Persistence helpers include `read_raw`, `read_metadata_with_dmtime`, `read_all_data_with_dmtime`, `write_all_meta`, `write_all_public`, `write_all_private`, `write_all_internal`, `open_file`, and `read_file_exists`. Object metadata operations are implemented through `rustfs_filemeta::FileMeta`, `FileInfo`, `RawFileInfo`, and helpers such as `get_file_info`.

Cleanup and deletion are handled by `cleanup_tmp_on_startup`, `cleanup_stale_tmp_objects`, `cleanup_deleted_objects`, `cleanup_deleted_objects_loop`, `move_to_trash`, and recursive `delete_file`. Deletions normally move paths into `.rustfs.sys/tmp/.trash` using generated UUID names, with disk-full fallback to direct removal.

The `DiskAPI for LocalDisk` implementation supplies all local disk behavior: volume management, object metadata reads/writes, version deletion, data rename, part rename, part checks, raw file reads/writes, directory listing/walking, multi-file reads, disk info, and scan lifecycle.

## Control flow
Startup first canonicalizes or resolves the endpoint path, creates required data-usage state, optionally renames `.rustfs.sys/tmp` to `.rustfs.sys/tmp-old/<uuid>`, recreates `.rustfs.sys/tmp/.trash`, and asynchronously removes the old tmp root. It then reads `.rustfs.sys/format.json`. If format bytes exist, `FormatV3` is decoded and the disk UUID must match the endpoint set/disk indexes. The constructor records disk capacity/static metadata, creates meta volumes, and launches a cleanup loop whose first tick is delayed by `DELETED_OBJECTS_CLEANUP_INTERVAL`.

Read flows start by resolving a bucket/object path and checking volume access unless the path is in internal metadata buckets. `read_version` reads `xl.meta`, converts it into `FileInfo`, and optionally inlines data. Small single-part objects under `DEFAULT_INLINE_BLOCK` may have the shard loaded from `part.N`; missing shard paths cause fallback to metadata-only inline representation. `read_file_stream` and `read_file_zero_copy` validate `offset + length` overflow and file bounds before seeking or mmaping.

Write flows resolve and validate paths, create missing parents under a skip-parent boundary, then write either asynchronously or through `spawn_blocking` for owned `Bytes`. Metadata writes append or replace versions in `FileMeta` and persist `xl.meta`; `write_all_meta` stages bytes under `.rustfs.sys/tmp/<uuid>` then renames to the destination. The `sync` parameter is deliberately ignored by `write_all_internal`, preserving the current durability contract without fsync.

Rename flows distinguish plain files, part files, directory markers, inline object metadata, and non-inline erasure data. `rename_part` enforces source/destination directory-vs-file compatibility, renames the part, writes a sidecar `.meta`, and prunes empty source parents. `rename_file` is the simpler generic path rename. `rename_data` merges the incoming `FileInfo` into destination `xl.meta`; for non-inline data it writes metadata at the source, renames the data directory, then renames `xl.meta`, with cleanup on failure. For inline data it performs read/merge/write/rename in one blocking task.

Deletion flows load `FileMeta`, remove targeted versions, move unshared data directories to trash, rewrite `xl.meta` if versions remain, or remove the metadata path when no versions remain. Batch deletion loops over `FileInfoVersions`. Generic deletes and path deletes also move targets to trash and recursively prune empty parent directories while refusing to operate on filesystem roots or paths outside the volume root.

Namespace walking waits for startup cleanup, emits explicit directory objects when present, lists directories recursively, filters by prefix and `forward_to`, reads `xl.meta` entries into `MetaCacheEntry`, tracks object counts for limits, deduplicates explicit directory markers with real directories, skips multipart data directories discovered from metadata, and writes results through `MetacacheWriter`.

Verification flows either stat each erasure part (`check_parts`) or run full bitrot verification (`verify_file`). `bitrot_verify` retries only the known "bitrot shard file size mismatch" error for an environment-controlled count/delay before converting errors into `CHECK_PART_*` status integers.

## State and persistence behavior
Persistent on-disk state is rooted at the endpoint path. Buckets are directories, objects are directories containing `xl.meta`, non-inline erasure data lives under object data-dir UUIDs with `part.N` files, multipart/internal state lives under `.rustfs.sys`, and deleted/stale paths are moved into `.rustfs.sys/tmp/.trash` for asynchronous cleanup. `format.json` stores the disk identity and erasure set membership; `LocalDisk` caches it but invalidates the cache when the file disappears or changes.

The cleanup state is partially asynchronous. Startup cleanup can continue after construction, and `walk_dir` waits up to `STARTUP_CLEANUP_WAIT_TIMEOUT` for the latch before scanning. Background cleanup runs every five minutes after an initial delay and removes trash entries plus temp directories older than one day.

The disk-info cache updates at most once per second and records capacity, inode counts, filesystem type, root-disk detection, physical device ids, and disk id. `start_scan` increments an atomic counter and `ScanGuard::drop` decrements it, exposing scanner activity in `DiskInfo`.

## Dependencies and integration points
This module depends on the broader `disk` contract (`DiskAPI`, `DiskInfo`, options/response structs, error conversion, filesystem helpers, OS helpers, and constants), `endpoint::Endpoint`, `format::FormatV3`, `rustfs_filemeta` metadata encoding/decoding, erasure bitrot verification, data-usage layout initialization, RustFS global root-disk thresholds, `rustfs_utils` path/OS helpers, `bytes`, `tokio`, `parking_lot`, `metrics`, `tracing`, `uuid`, and platform-specific `libc`, `memmap2`, and `rustix` calls.

The implementation is consumed through `disk/mod.rs` and `disk_store::LocalDiskWrapper`, while remote peers use the same trait shape through RPC. It integrates with bucket scanners through `MetacacheWriter`, with healing/check code through `check_parts` and `verify_file`, with lifecycle/delete code through version deletion, and with startup/format loading through `get_disk_id`.

## Risks and edge cases
Path confinement relies on lexical normalization before `starts_with(root)`. That is fast but should remain sensitive to symlinks, Windows prefixes, and cache entries that are not revalidated against changing filesystem topology. The cache eviction policy is simple and does not check path validity in `get_object_paths_batch`.

Durability may be weaker than callers expect because `write_all_internal` ignores `sync`; atomicity depends primarily on temp-write-plus-rename where used, and direct writes elsewhere can leave partial files if the process exits mid-write. Rename flows are multi-step and have best-effort rollback/cleanup, so crash consistency around object overwrite and old data-dir restoration is a key risk area.

Delete behavior intentionally moves most data to trash and later removes it. Disk-full fallback switches to direct deletion. Background cleanup failures are logged but not escalated, so trash growth or stale temp directories can accumulate if permissions or filesystem errors persist.

`read_file_zero_copy` is described as zero-copy but currently copies mmap contents into `Bytes` for safe ownership. That avoids unsafe lifetime hazards but affects performance expectations. Offset arithmetic overflow is guarded in both stream and mmap reads.

Volume-name validation is minimal on non-Windows platforms and allows names containing slashes/colons in tests, so higher layers must enforce S3 bucket rules. Access checks are skipped for internal metadata prefixes, which is necessary for system maintenance but expands the trusted surface.

## Test signals
The in-file tests cover format-id cache invalidation after `format.json` removal, startup temp cleanup and trash recreation, stale tmp movement, cleanup interval not ticking immediately, cleanup barrier notification and timeout, recursive scan inclusion and deduplication, `forward_to` behavior with repeated prefixes, hidden delete marker limit accounting, multipart data-dir filtering in walks, basic volume/file operations, disk info shape, read offset overflow rejection, volume-name validation, helper file reads/metadata reads, root-path and lexical normalization behavior, file-cache reclaim threshold environment handling, and bitrot size-mismatch string classification.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/local.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/mod.rs -->
# sources/object-store/rustfs/crates/ecstore/src/disk/mod.rs

## Purpose
This file defines the public disk subsystem boundary for `ecstore`. It declares disk-related submodules, shared constants for RustFS metadata paths and file names, the local-or-remote `Disk` enum, the `DiskAPI` trait that storage code uses, and the request/response/options structs shared across local disk, remote disk, RPC, healing, scanning, and metadata paths.

## Important APIs, types, and functions
The module exports metadata constants such as `RUSTFS_META_BUCKET`, `RUSTFS_META_MULTIPART_BUCKET`, `RUSTFS_META_TMP_BUCKET`, `RUSTFS_META_TMP_DELETED_BUCKET`, `BUCKET_META_PREFIX`, `FORMAT_CONFIG_FILE`, `STORAGE_FORMAT_FILE`, and `STORAGE_FORMAT_FILE_BACKUP`.

`DiskStore` is `Arc<Disk>`. `FileReader` and `FileWriter` are boxed async read/write trait objects. `Disk` has `Local(Box<LocalDiskWrapper>)` and `Remote(Box<RemoteDisk>)` variants, giving one enum type for both local filesystem disks and RPC-backed peer disks.

`DiskAPI` is the core async trait. It covers identity and health (`to_string`, `is_online`, `is_local`, `host_name`, `endpoint`, `close`, `get_disk_id`, `set_disk_id`, `path`, `get_disk_location`), volume operations, metadata operations (`write_metadata`, `update_metadata`, `read_version`, `read_xl`, `read_metadata`, `rename_data`, version deletes), file operations (`read_file`, stream/zero-copy reads, append/create/rename, `rename_part`, generic delete), verification (`verify_file`, `check_parts`, `read_parts`), bulk reads, raw read/write-all, disk info, and scan guard creation.

`new_disk` selects the implementation from `Endpoint::is_local`: local endpoints instantiate `LocalDisk`, wrap it in `LocalDiskWrapper` with optional health checks, and return `Disk::Local`; remote endpoints build internode data transport from environment and create `RemoteDisk`.

Data structs include `DiskInfo`, `Info`, `FileInfoVersions`, `WalkDirOptions`, `DiskOption`, `RenameDataResp`, `DeleteOptions`, `ReadMultipleReq`, `ReadMultipleResp`, `VolumeInfo`, `ReadOptions`, `UpdateMetadataOpts`, `CheckPartsResp`, and `DiskLocation`. Constants and helpers for part verification are `CHECK_PART_UNKNOWN`, `CHECK_PART_SUCCESS`, `CHECK_PART_DISK_NOT_FOUND`, `CHECK_PART_VOLUME_NOT_FOUND`, `CHECK_PART_FILE_NOT_FOUND`, `CHECK_PART_FILE_CORRUPT`, `conv_part_err_to_int`, `has_part_err`, and `count_part_not_success`.

## Control flow
Every `DiskAPI for Disk` method is a dispatch shim: it matches on `Disk::Local` or `Disk::Remote` and forwards the call to the wrapped implementation with the same arguments. Runtime health helpers outside the trait (`runtime_state`, `offline_duration_secs`, `last_capacity_snapshot`, `record_capacity_probe`, `reset_health_for_store_init_retry`, and `enable_health_check`) follow the same delegation model.

`new_disk` is the construction choke point. Local construction stays in-process and canonicalizes/initializes the local disk through `LocalDisk::new`. Remote construction configures the internode data transport before creating `RemoteDisk`, so failures to build transport surface before the disk store enters the pool.

`FileInfoVersions::find_version_index` parses a requested version UUID and searches the `versions` vector for a matching `FileInfo.version_id`; empty input returns `None`. `DiskLocation::valid` requires pool, set, and disk indexes all to be populated. `conv_part_err_to_int` maps selected `DiskError` values and `None` into stable integer status codes, warning and returning `CHECK_PART_UNKNOWN` for anything else.

## State and persistence behavior
This module itself does not persist state. It defines the state contracts carried by implementors. `DiskInfo` is the serialized/call-returned snapshot of capacity, filesystem identity, health flags, endpoint/mount path, physical devices, disk UUID, media type, metrics, and error string. `FileInfoVersions` models the version set and free-version set for one object. `DeleteOptions` carries recursive/immediate/undo-write behavior plus an old data-dir UUID for rollback. `WalkDirOptions` carries scanner cursor and filtering state.

Because the enum delegates to either local or remote implementations, persistence semantics depend on the selected variant: local writes hit filesystem state under a disk root, remote writes cross RPC to a peer. The trait is designed so callers can treat both uniformly.

## Dependencies and integration points
This file ties together `disk_store::LocalDiskWrapper`, `local::LocalDisk`/`ScanGuard`, `rpc::RemoteDisk`, `endpoint::Endpoint`, disk health state, file metadata types, admin `DiskMetrics`, `bytes`, `serde`, `tokio::io`, `time`, and `uuid`. It is the common contract used by erasure sets, healing, object metadata code, scanners, RPC services, and admin info calls.

The status integer constants explicitly warn that changing their order can cause data loss during mixed-version operation, making this module part of the wire/storage compatibility surface.

## Risks and edge cases
The dispatch layer is repetitive; adding a trait method requires updating the trait, the enum implementation, local implementation, remote implementation, and wrapper layers together. Missing or inconsistent delegation would cause local/remote behavior drift.

`find_version_index` uses `Uuid::parse_str(v).unwrap_or_default()`, so malformed UUID strings search for the nil UUID rather than immediately failing. That may be intentional tolerance but can surprise callers if nil version ids are possible.

`DiskInfoOptions` includes `disk_id`, `metrics`, and `noop`, but individual implementations may ignore some fields; callers should not assume every option is honored uniformly.

Part status constants are compatibility-sensitive. Any reordering or reinterpretation risks corrupting healing decisions when nodes run different versions.

## Test signals
The tests validate `DiskLocation::valid`, `FileInfoVersions::find_version_index`, part-error conversion and detection helpers, option/response struct construction, metadata constants, local `new_disk` construction, enum method behavior for local disks, and health-reset delegation for both local and remote variants. The remote delegation test constructs a `RemoteDisk` with `TcpHttpInternodeDataTransport` and checks that runtime state resets to online.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/os.rs -->
# sources/object-store/rustfs/crates/ecstore/src/disk/os.rs

## Purpose
This file provides small OS/filesystem utility functions used by the disk layer. It centralizes path-length validation, root-disk detection, directory creation, directory listing, and reliable rename behavior with error conversion into the disk error model.

## Important APIs, types, and functions
`check_path_length` validates a path string against platform limits and rejects trivial dangerous Unix paths `"."`, `".."`, and `"/"`. It enforces macOS whole-path length of 1016, Windows whole-path length of 1024, and per-segment length of 255 characters on all platforms.

`is_root_disk` checks whether a disk path is the same device as the root path using `rustfs_utils::os::same_disk`; Windows always returns false.

`make_dir_all` validates path length then calls `reliable_mkdir_all`. `is_empty_dir` reads at most one entry using `read_dir`. `read_dir` returns visible file names and directory names with a trailing slash, skipping empty, `"."`, and `".."` entries and honoring a count limit where `0` means stop after the first accepted entry and negative values effectively mean unlimited in current callers.

`rename_all` wraps `reliable_rename` and converts IO errors to disk file errors. `rename_all_ignore_missing_source` uses the same inner rename but turns source `NotFound` into success, which is useful for cleanup paths.

`reliable_rename_inner` creates the destination parent if missing, retries a failed `rename_std` once, optionally logs a warning, and returns the final IO result. `reliable_mkdir_all` retries directory creation once after walking the base directory upward if the first attempt fails with `NotFound`. `os_mkdir_all` tries direct `mkdir`, creates missing parents only after direct failure, and never creates paths under `base_dir` when `base_dir` starts with the requested directory path. `file_exists` is a simple synchronous metadata probe.

## Control flow
Directory creation flows through `make_dir_all -> reliable_mkdir_all -> os_mkdir_all`. The code first validates path length, then tries to create the target. On missing parents, it creates the parent chain and retries the final mkdir. `reliable_mkdir_all` handles a first `NotFound` by adjusting the base dir to its parent once before retrying.

Rename flows through `rename_all` or `rename_all_ignore_missing_source` into `reliable_rename_inner`. Before rename, the destination parent is created if absent. The first `rename_std` failure is retried once unconditionally. On the second failure, normal `rename_all` logs and returns the error; the ignore-missing variant suppresses only `NotFound`.

Directory listing uses `tokio::fs::read_dir`, filters non-useful names, classifies entries by async `file_type`, appends a slash to directories, decrements the counter for each accepted entry, and breaks when the counter reaches zero.

## State and persistence behavior
The module does not keep in-memory state. It mutates filesystem state by creating directories and renaming files/directories. `read_dir`, `is_empty_dir`, `file_exists`, and `is_root_disk` are observational. Rename behavior depends on underlying filesystem atomicity for `rename_std`, while parent creation can introduce extra directories as a side effect.

## Dependencies and integration points
It depends on `DiskError`, disk `Result`, `to_file_error`, `rustfs_utils::path::SLASH_SEPARATOR`, `rustfs_utils::os::same_disk`, `tokio::fs`, tracing warnings, and lower-level `disk::fs` wrappers (`rename_std`, `mkdir`, `make_dir_all`). `local.rs` uses these helpers heavily for object writes, metadata writes, trash movement, startup cleanup, stale tmp cleanup, and volume creation.

## Risks and edge cases
`check_path_length` is byte/character-count based and does not canonicalize paths, so callers still need root-confinement checks. It rejects only `"."`, `".."`, and `"/"` as whole paths, not embedded traversal; `local.rs` handles that separately through normalization.

`read_dir` treats `count == 0` as "break after first accepted entry" because the counter is decremented before the equality check, while its comment says count `0` is unlimited. Current callers use `1` for emptiness and `-1` for unlimited; a future caller passing `0` could get surprising results.

`reliable_rename_inner` retries any first rename failure, regardless of kind. This can mask transient parent-creation races but also repeats permanent permission or cross-device errors. It creates destination parents before knowing whether the source exists.

`os_mkdir_all` has non-obvious `base_dir.starts_with(dir_path)` guard behavior. Callers must pass the correct base boundary to avoid skipping required creation or creating too much of the tree.

## Test signals
The tests assert that `rename_all` returns `DiskError::FileNotFound` and does not create a destination when the source is missing, while `rename_all_ignore_missing_source` returns success and also leaves the destination absent. Broader behavior is covered indirectly by `local.rs` tests that create volumes, write metadata, move temp directories, and rename/delete filesystem paths.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disk/os.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disks_layout.rs -->
# sources/object-store/rustfs/crates/ecstore/src/disks_layout.rs

## Purpose
This file parses RustFS disk/endpoint command-line layouts into erasure pools and sets. It supports both legacy explicit endpoint lists and ellipses-based expansion such as `data{1...64}` or distributed host/disk patterns, then chooses a symmetric supported erasure set size. The result tells later initialization code how many pools, sets, and drives per set exist and which endpoint strings belong to each set.

## Important APIs, types, and functions
`SET_SIZES` lists supported erasure set sizes from 2 through 16. `ENV_RUSTFS_ERASURE_SET_DRIVE_COUNT` optionally forces a specific set drive count.

`PoolDisksLayout` stores the original command-line string for one pool plus a `Vec<Vec<String>>` layout where each inner vector is one erasure set. It exposes `iter`, plus private `new`, `count`, and `get_cmd_line`.

`DisksLayout` stores whether parsing used legacy mode and the list of pools. `DisksLayout::from_volumes` is the public parser. `is_empty_layout`, `is_single_drive_layout`, `get_single_drive_layout`, `get_set_count`, `get_drives_per_set`, and `get_cmd_line` expose parsed topology.

`get_all_sets` is the main conversion helper. It either expands ellipses through `EndpointSet::from_volumes` or builds an `EndpointSet` from explicit args, then rejects duplicate expanded endpoints.

`EndpointSet` holds parsed `ArgPattern`s, expanded endpoint strings, and `set_indexes`. `EndpointSet::from_volumes` parses ellipses, computes total pattern sizes, computes set indexes, expands every pattern into endpoint strings, and returns the set. `EndpointSet::get` slices the flattened endpoint list according to `set_indexes` to produce `Vec<Vec<String>>` sets.

Set-size helpers are `get_divisible_size`, `possible_set_counts`, `is_valid_set_size`, `common_set_drive_count`, `possible_set_counts_with_symmetry`, `get_set_indexes`, and `get_total_sizes`.

## Control flow
`DisksLayout::from_volumes` rejects empty input, detects whether any argument has ellipses, reads `RUSTFS_ERASURE_SET_DRIVE_COUNT` with default `"0"`, and parses it as `usize`. Without ellipses it treats all args as one legacy pool and calls `get_all_sets` with all endpoints. With ellipses it requires all args to have ellipses when multiple args are supplied, then parses each argument as a separate pool.

`get_all_sets` constructs an `EndpointSet`, calls `get` to build set vectors, then scans every endpoint string with a `HashSet` to reject duplicates. For non-ellipses multi-arg input, `get_set_indexes` is called with total size equal to the number of explicit args. A single explicit endpoint becomes one set of one drive.

For ellipses, `EndpointSet::from_volumes` calls `find_ellipses_patterns` for each argument, computes each argument's total expansion size, calls `get_set_indexes`, expands all patterns, and flattens expansions into the endpoint list. `EndpointSet::get` then walks `set_indexes`, slicing consecutive endpoints into sets.

`get_set_indexes` validates each total size against minimum supported set size and the forced set count. It computes the greatest common divisor of all total sizes, filters supported set sizes that divide that common size, filters again for symmetry against each ellipses pattern, then either accepts the forced set-drive count or chooses `common_set_drive_count`. Finally it maps each total size to repeated `set_size` entries.

## State and persistence behavior
No filesystem or persistent state is written. The only external state read is `RUSTFS_ERASURE_SET_DRIVE_COUNT`, which can force layout selection or cause parsing to fail if incompatible with the endpoint count and symmetry constraints. Parsed layout state is held in `DisksLayout`/`PoolDisksLayout` values and consumed by store initialization.

## Dependencies and integration points
The parser depends on `rustfs_utils::string::{has_ellipses, find_ellipses_patterns, ArgPattern}` for ellipses parsing/expansion, `serde::Deserialize` for config deserialization, `std::env`, `std::io::Error/Result`, `HashSet`, and tracing `debug` for environment default logging. It feeds endpoint topology into the erasure store initialization path and must remain compatible with endpoint parsing in `disk::endpoint`.

## Risks and edge cases
The forced set-drive-count environment variable is parsed directly and any non-numeric value fails layout parsing. That is useful for surfacing misconfiguration but can make startup sensitive to environment drift.

The single-drive explicit layout bypasses normal erasure minimums by returning `vec![vec![args.len()]]` when only one arg is provided. Callers must distinguish single-drive mode from erasure-coded multi-drive mode.

`possible_set_counts_with_symmetry` mutates a `symmetry` flag while iterating patterns; for complex multi-pattern arguments, the final value for each candidate can depend on the last checked pattern element. The test matrix covers many representative cases, but symmetry logic is subtle and startup-critical.

Duplicate detection happens after expansion, so very large ellipses inputs allocate all endpoints before discovering duplicates. Error messages use `std::io::Error::other`, which loses structured error kinds.

Changing `SET_SIZES` or `common_set_drive_count` selection changes the physical erasure layout derived from the same command line. That is a compatibility-sensitive startup behavior.

## Test signals
Tests cover greatest common divisor calculation, many `get_set_indexes` layouts including invalid too-large/unsupported cases, host/disk/rack ellipses, Kubernetes-style zero-based ranges, padded numeric ranges, more than two ellipses, standalone multi-ellipsis paths, and invalid pattern forms. The expected indexes assert the selected erasure set size and number of sets for each topology.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/disks_layout.rs -->
