# subset-b-009798 Research

Grouped research for the listed s3fs-fuse files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/fdcache_untreated.cpp -->
# sources/user-network-fs/s3fs-fuse/src/fdcache_untreated.cpp

## Purpose
Implements `UntreatedParts`, the mutable range tracker used by the file descriptor cache to remember byte ranges that still need follow-up treatment, typically upload or multipart synchronization. The implementation keeps ranges ordered, merges adjacent or overlapping intervals, tags the most recent update, and lets callers clear or replace tracked ranges after work is completed.

## Important APIs, Types, And Functions
The public methods are declared in `fdcache_untreated.h`; this file supplies their behavior. `empty()` reports whether the protected `untreated_list_t` is empty. `AddPart(start, size)` validates a positive range, increments `last_tag`, and either stretches an existing `untreatedpart`, inserts before the first later range, or appends a new range. `RowGetPart()` is the private selector behind `GetLastUpdatedPart()`, returning the most recent tagged range when it is at least `min_size`, capped by `max_size`. `ClearParts(start, size)` removes a byte span, with `size == 0` meaning clear everything from `start` onward. `GetLastUpdatePart()`, `ReplaceLastUpdatePart()`, and `RemoveLastUpdatePart()` operate on the currently `last_tag`-marked range. `Duplicate()` snapshots the vector, and `Dump()` logs the range list.

## Control Flow
All methods take `untreated_list_lock` before touching the vector or tag. `AddPart()` walks the list once. On overlap or adjacency, `untreatedpart::stretch()` widens the current interval and applies the new tag, then the implementation keeps stretching across following intervals until the next range no longer overlaps. Without overlap, the function inserts before the first interval whose start is greater than the new range end. `ClearParts()` also walks the vector, considering four cases: no more overlap, deletion/trimming at the start side, trimming or splitting when the clear span begins inside a range, and no overlap behind the current range. Last-update operations linearly scan for `untreated_tag == last_tag`.

## State And Persistence Behavior
State is process-local and in memory only: `untreated_list` stores `untreatedpart{start,size,untreated_tag}` entries and `last_tag` monotonically identifies the latest add or merged update. There is no disk persistence. `Duplicate()` is the escape hatch for callers needing an immutable copy outside the mutex. `Dump()` emits state to the s3fs logger but does not alter it.

## Dependencies And Integration Points
The code depends on `types.h` for `untreatedpart` and `untreated_list_t`, `common.h` constants via the header, and `s3fs_logger.h` for diagnostics. Its natural integration point is `FdEntity`/fdcache writeback logic: callers can mark dirty file ranges, request an upload-sized chunk via `GetLastUpdatedPart()`, and clear or adjust the range after multipart upload progress.

## Risks
`start + size` arithmetic is unchecked and can overflow `off_t` for extreme inputs, affecting ordering and overlap decisions. The split branch of `ClearParts()` mutates `iter->size` before computing `next_size` from `iter->start + iter->size`, so clearing a middle slice from a range can compute the tail length from the shortened front range rather than the original end; this is a concrete boundary-risk area for tests. The `last_tag` model assumes a single latest update is meaningful after merges; if merged ranges inherit the newest tag, older dirty spans can become hidden from `GetLastUpdatedPart(lastpart=true)` until additional calls clear/replace the latest range. `Dump()` logs `{start - size}` rather than `{start - end}`, which may confuse debugging.

## Test Signals
Useful tests should cover adding adjacent intervals, overlapping intervals, insertion before/after, `GetLastUpdatedPart()` with min/max thresholds, clearing prefixes/suffixes/whole ranges, clearing with `size == 0`, and splitting a range in the middle. Concurrency tests can verify `Duplicate()` snapshots are consistent while multiple threads add/clear. Boundary tests should exercise zero/negative inputs, maximum `off_t`-adjacent ranges, and the suspected `ClearParts()` split arithmetic.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/fdcache_untreated.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/fdcache_untreated.h -->
# sources/user-network-fs/s3fs-fuse/src/fdcache_untreated.h

## Purpose
Declares the `UntreatedParts` range-tracking class used by s3fs-fuse cache code to manage byte ranges that are pending treatment. It presents a small synchronized API for adding, selecting, clearing, replacing, removing, duplicating, and dumping dirty ranges.

## Important APIs, Types, And Functions
`UntreatedParts` owns a `mutable std::mutex untreated_list_lock`, an `untreated_list_t untreated_list`, and a `long last_tag`. Copy and move are deleted to avoid unsafe mutex/vector transfer. Public API includes `empty()`, `AddPart()`, `GetLastUpdatedPart()`, `ClearParts()`, `ClearAll()`, `GetLastUpdatePart()`, `ReplaceLastUpdatePart()`, `RemoveLastUpdatePart()`, `Duplicate()`, and `Dump()`. `GetLastUpdatedPart()` is an inline wrapper around private `RowGetPart()` and defaults `min_size` to `MIN_MULTIPART_SIZE`, making the class directly aware of multipart upload sizing.

## Control Flow
The header exposes a lock-protected, non-copyable object with inline adapters for common operations. Selection of ranges flows through `RowGetPart(start, size, max_size, min_size, lastpart)`, with the header only exposing the `lastpart=true` path as `GetLastUpdatedPart()`. `ClearAll()` delegates to `ClearParts(0, 0)`, following the implementation convention that zero size clears from the start position to the end.

## State And Persistence Behavior
All state is in memory. `untreated_list` is annotated with `GUARDED_BY(untreated_list_lock)` and stores vector entries from `types.h`. `last_tag` identifies the latest updated range; it starts at zero and is incremented by adds in the `.cpp`. There is no serialization or external persistence contract.

## Dependencies And Integration Points
The header depends on `common.h` for thread-safety annotations/constants and on `types.h` for `untreated_list_t`. It is included by fd-cache implementation files that need to track pending byte ranges for writeback and multipart upload decisions. The default `MIN_MULTIPART_SIZE` ties callers to S3 multipart constraints unless they override `min_size`.

## Risks
The public name pair `GetLastUpdatedPart()` and `GetLastUpdatePart()` is easy to confuse: the former applies min/max chunk sizing through `RowGetPart()`, while the latter returns the whole last-tagged part. Because only a latest-update selector is exposed, callers that need global dirty-range ordering must rely on `Duplicate()`. Header-level thread annotations help static analysis only if the build enables compatible tooling.

## Test Signals
Compile tests should ensure non-copyability, default construction, and access through inline methods. Behavioral tests belong mostly to `fdcache_untreated.cpp` but should explicitly validate the differing semantics of `GetLastUpdatedPart()` versus `GetLastUpdatePart()` and the `ClearAll()` zero-size convention.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/fdcache_untreated.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/filetimes.cpp -->
# sources/user-network-fs/s3fs-fuse/src/filetimes.cpp

## Purpose
Implements portable helpers for POSIX `timespec` and `stat` timestamp handling, plus the `FileTimes` value object used by s3fs cache and FUSE operations to carry ctime, atime, and mtime updates. It normalizes `UTIME_NOW` to an actual realtime timestamp and treats `UTIME_OMIT` as "do not change this field."

## Important APIs, Types, And Functions
Utility functions include `valid_timespec()`, `compare_timespec(timespec,timespec)`, `compare_timespec(stat,type,timespec)`, `set_timespec_to_stat()`, `set_stat_to_timespec()`, `str_stat_time()`, `s3fs_realtime()`, and `s3fs_str_realtime()`. `FileTimes::Clear()` and typed clear helpers set fields to `{0, UTIME_OMIT}`. `GetTime()` and typed getters return or copy a field. `ReflectFileTimes()` writes non-omitted fields into a `struct stat`. `SetTime()` resolves `UTIME_NOW`; `SetAllNow()` uses a single realtime sample; `SetAll()` overloads populate the object from `stat`, raw timespecs, or another `FileTimes`; `IsOmit()` checks the sentinel.

## Control Flow
`set_timespec_to_stat()` and `set_stat_to_timespec()` branch on `stat_time_type` and on `__APPLE__` to use `st_atimespec`/`st_mtimespec`/`st_ctimespec` on macOS or `st_atim`/`st_mtim`/`st_ctim` elsewhere. `s3fs_realtime()` tries `clock_gettime(CLOCK_REALTIME)` and falls back to `time(nullptr)` with nanoseconds zero on failure. `FileTimes::SetAll()` samples current time once, then resolves each argument: `UTIME_NOW` becomes that shared sample, and `UTIME_OMIT` is skipped unless `no_omit` allows setting omitted values.

## State And Persistence Behavior
`FileTimes` stores three `timespec` fields in memory only. The default state and cleared state are all omitted. Calling `SetTime()` with `UTIME_NOW` persists the resolved timestamp, not the sentinel, so later reflection is deterministic. The class itself performs no locking; callers such as `FdEntity` protect it when stored in shared cache state.

## Dependencies And Integration Points
This file depends on `filetimes.h`, `s3fs_logger.h`, and `string_util.h`. It integrates with metadata conversion in `metaheader.cpp`, cache entity timestamp storage in `fdcache_entity`, and FUSE operations that need `utimens`-style semantics. `str_stat_time()` and `s3fs_str_realtime()` provide string formatting through the project `str(timespec)` helper.

## Risks
`valid_timespec()` rejects negative seconds and sentinel nanoseconds but does not validate the normal nanosecond range below one billion. Unknown `stat_time_type` values log and either skip writes or return zero, which is safe but can hide enum misuse. `SetAll(..., no_omit)` semantics are subtle: when `no_omit` is false, omitted values may be propagated into the object; when true, omitted values are skipped. Any caller expecting `UTIME_NOW` to remain symbolic will be surprised because it is eagerly resolved.

## Test Signals
Tests should compare timestamps across equal, earlier, and later nanosecond values; verify macOS/non-macOS stat field mapping under platform builds; check `UTIME_NOW` resolution and `UTIME_OMIT` skipping; verify `ReflectFileTimes()` leaves omitted stat fields unchanged; and simulate `clock_gettime` failure if the test harness supports it. Integration tests around `utimens`, file creation, cache open, and metadata round-trip should observe correct atime/mtime/ctime behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/filetimes.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/filetimes.h -->
# sources/user-network-fs/s3fs-fuse/src/filetimes.h

## Purpose
Declares timestamp utilities and the `FileTimes` container used throughout s3fs-fuse for stat timestamp comparison, formatting, reflection, and update propagation.

## Important APIs, Types, And Functions
`enum class stat_time_type : uint8_t` identifies `ATIME`, `MTIME`, and `CTIME`. Free functions expose validation, comparison, stat-to-timespec conversion, timespec-to-stat conversion, stat time formatting, realtime acquisition, and realtime formatting. `FileTimes` owns `ft_ctime`, `ft_atime`, and `ft_mtime`; public helpers clear, get, reflect into `struct stat`, set individual times, set all times from now/stat/raw values/another `FileTimes`, and test omission.

## Control Flow
The class is a thin state container with inline typed wrappers delegating to private typed implementations in the `.cpp`. Construction initializes all fields to `UTIME_OMIT`. Public setters accept `timespec` by value so `SetTime()` can rewrite `UTIME_NOW` without mutating the caller's object. `SetAll()` defaults `no_omit` to true, so omitted source fields normally do not overwrite existing stored values.

## State And Persistence Behavior
`FileTimes` state is only the three `timespec` fields. There is no ownership of external resources, no dynamic allocation, no locking, and no disk persistence. The object is copyable by default because no special members are deleted; callers are responsible for synchronization when shared.

## Dependencies And Integration Points
The header depends on standard `cstdint`, `string`, and `sys/stat.h`. It is included by fd-cache and metadata conversion code, especially `fdcache_entity`, `fdcache_auto`, `fdcache`, `metaheader`, and `s3fs.cpp`. It bridges FUSE/system timestamp semantics with S3 metadata values.

## Risks
The API includes both reference-returning getters and copy getters; references are safe only as long as the `FileTimes` object remains alive and unmodified. The default `no_omit=true` behavior in `SetAll()` can be misread, so tests should document whether omitted source values are preserved or skipped. `ctime` is treated as a settable timestamp even though POSIX ctime is normally kernel-managed, which is appropriate for object metadata but can differ from local filesystem expectations.

## Test Signals
Header-level tests should compile across C++ standards and target platforms, assert initial omission for all fields, verify each inline wrapper maps to the correct `stat_time_type`, and exercise copy behavior if `FileTimes` is passed by value in cache operations. Integration tests should use the public API rather than private helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/filetimes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/gnutls_auth.cpp -->
# sources/user-network-fs/s3fs-fuse/src/gnutls_auth.cpp

## Purpose
Provides the GnuTLS-backed implementation of the common s3fs cryptographic API declared in `s3fs_auth.h`. It supplies library identity, global crypto initialization/teardown, HMAC-SHA1, HMAC-SHA256, MD5, and SHA256 over memory buffers and file descriptors. It supports two build variants: GnuTLS with nettle primitives or GnuTLS with libgcrypt.

## Important APIs, Types, And Functions
`s3fs_crypt_lib_name()` returns either `GnuTLS(nettle)` or `GnuTLS(gcrypt)`. `s3fs_init_global_ssl()` calls `gnutls_global_init()` and, in the gcrypt variant, `gcry_check_version()`. `s3fs_destroy_global_ssl()` calls `gnutls_global_deinit()`. Crypt mutex init/destroy are no-ops. `s3fs_HMAC()` computes SHA1 HMAC and `s3fs_HMAC256()` computes SHA256 HMAC. `s3fs_md5()` and `s3fs_sha256()` hash memory; `s3fs_md5_fd()` and `s3fs_sha256_fd()` hash a range of a file descriptor using 512-byte `pread()` loops.

## Control Flow
Compile-time `USE_GNUTLS_NETTLE` selects nettle contexts (`hmac_sha1_ctx`, `hmac_sha256_ctx`, `md5_ctx`, `sha256_ctx`) or GnuTLS/libgcrypt APIs (`gnutls_hmac_fast`, `gcry_md_open`, `gcry_md_write`, `gcry_md_read`). File hashing treats `size == -1` as "hash the whole file" after `fstat()`. Each loop computes the next read length as `min(512, size - total)`, reads at `start + total`, stops on EOF, returns false on read errors, and finalizes the digest into project fixed-size arrays.

## State And Persistence Behavior
Global state belongs to GnuTLS and optionally libgcrypt. Per-call digest contexts are stack or library handles and are closed before return. HMAC returns heap-owned buffers via `std::unique_ptr<unsigned char[]>`; callers receive digest length through `digestlen`. No secrets or digests are persisted by this file.

## Dependencies And Integration Points
This file depends on GnuTLS, optionally nettle or gcrypt, POSIX `pread`/`fstat`, and project headers `common.h`, `s3fs.h`, `s3fs_auth.h`, and `s3fs_logger.h`. The common API is used by `curl.cpp` for AWS signature v2/v4 HMAC derivation and payload hashing, by multipart upload code for MD5/ETag work, and by `common_auth.cpp`/`curl_util.cpp` for hex digest helpers.

## Risks
The nettle `s3fs_sha256_fd()` path does not implement the `size == -1` whole-file convention that the gcrypt, NSS, and OpenSSL paths implement; a caller passing `-1` would skip the loop and return the digest of an empty stream. Some memory hashing functions do not validate null `data` or result pointers, so callers must honor the API. The read loop stops on short EOF without treating it as an error, which is acceptable for changing files only if callers can tolerate hashing fewer bytes. Digest buffers in gnutls-fast HMAC allocate `len + 1` though the extra byte is not used as a terminator.

## Test Signals
Cross-backend tests should compare HMAC-SHA1, HMAC-SHA256, MD5, and SHA256 against known vectors for all configured crypto libraries. File hashing tests should cover full-file `size == -1`, ranged hashing with nonzero `start`, zero-length input, invalid fd, and a short/truncated file. A specific regression test should assert nettle SHA256 fd hashing honors whole-file behavior if that path is fixed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/gnutls_auth.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/metaheader.cpp -->
# sources/user-network-fs/s3fs-fuse/src/metaheader.cpp

## Purpose
Converts S3/GCS object headers and s3fs metadata headers into filesystem attributes. It parses times, sizes, modes, UID/GID, object type, Last-Modified/IAM expiry timestamps, incomplete metadata detail hints, header merges, and full `struct stat` population.

## Important APIs, Types, And Functions
Time helpers include private `cvt_string_to_time()` and `get_time()`, plus public `get_mtime()`, `get_ctime()`, and `get_atime()`. Attribute parsers include `get_size()`, `get_mode()`, `get_uid()`, `get_gid()`, and `get_blocks()`. Type helpers include private `convert_meta_to_mode_fmt()`, public `is_reg_fmt()`, `is_symlink_fmt()`, `is_dir_fmt()`, and `derive_object_type()`. Date parsers are `cvtIAMExpireStringToTime()` and `get_lastmodified()`. `is_need_check_obj_detail()` decides if a zero-length object may require directory-detail probing. `merge_headers()` overlays metadata maps. `convert_header_to_stat()` builds a `struct stat` from headers.

## Control Flow
Timestamp lookup prefers explicit s3fs metadata (`x-amz-meta-mtime`, `x-amz-meta-ctime`, `x-amz-meta-atime`), supports GCS reserved mtime, and falls back to `Last-Modified` when `overcheck` is true. Mode parsing prioritizes `x-amz-meta-mode`, then s3sync permissions, then GCS POSIX mode, then defaults to 0750 for slash-terminated paths or 0640 otherwise. If file-type bits are absent, directory inference uses forced-dir flags, directory MIME types, slash-terminated zero-size keys, or regular-file fallback. Object type derivation examines only the file-type bits and special folder suffix/path cases. `convert_header_to_stat()` zeroes the stat, sets `st_nlink`, mode, block size, timestamps, size, UID, and GID.

## State And Persistence Behavior
The file is stateless. It consumes `headers_t` maps and emits values or mutates caller-owned maps/stat structures. Defaults use current process effective UID/GID when headers omit ownership, so stat results can vary by runtime user. `merge_headers()` mutates the base map and returns whether anything was updated.

## Dependencies And Integration Points
Dependencies include `metaheader.h`, `string_util.h` for numeric/time parsing, and `filetimes.h` for stat timestamp writes. `headers_t` is a case-insensitive `std::map` declared in the header. Integration is broad: `s3fs.cpp`, `s3fs_threadreqs.cpp`, and `fdcache_entity.cpp` call `convert_header_to_stat()`, `get_mtime()`, `derive_object_type()`, and `is_need_check_obj_detail()` to turn HTTP response headers into FUSE directory entries, attributes, cache metadata, and object-type decisions.

## Risks
`cvt_string_to_time()` parses fractional seconds as the raw digits after the decimal instead of scaling/truncating to nanoseconds; values like `123.45` become `tv_nsec = 45`, not 450,000,000. `convert_header_to_stat()` computes `st_blocks` for regular files before it assigns `st_size`, so regular-file block counts are based on the zeroed size and likely remain zero. `derive_object_type()` dereferences `strpath.rbegin()` without checking for an empty path when the mode is directory. Parsing helpers generally treat malformed numeric strings as whatever `cvt_strtoofft()` returns, with limited validation. Ownership defaults to effective IDs, which can make metadata-less objects appear owned by the mounting user rather than a stable configured identity.

## Test Signals
Tests should feed representative S3, s3sync, and GCS header maps through each parser. Important cases include explicit metadata times, missing metadata with Last-Modified fallback, fractional mtime values, GCS reserved mode/uid/gid, directory MIME types with optional `;charset`, slash-terminated zero-size keys, symlink/file mode bits, metadata-less objects, and forced directory conversion. Regression tests should assert regular-file `st_blocks` follows `Content-Length` and that empty paths are handled safely.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/metaheader.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/metaheader.h -->
# sources/user-network-fs/s3fs-fuse/src/metaheader.h

## Purpose
Declares the case-insensitive HTTP/object metadata header map and the conversion utilities that turn object metadata into s3fs filesystem attributes and object-type decisions.

## Important APIs, Types, And Functions
`headers_t` is `std::map<std::string, std::string, case_insensitive_compare_func>`, matching HTTP header case-insensitivity. The API exposes time extraction (`get_mtime`, `get_ctime`, `get_atime`), size/mode/owner/group parsing, object format probes (`is_reg_fmt`, `is_symlink_fmt`, `is_dir_fmt`), `derive_object_type()`, block count calculation, IAM and Last-Modified timestamp parsing, `is_need_check_obj_detail()`, `merge_headers()`, and `convert_header_to_stat()`.

## Control Flow
The header is pure declarations and default arguments. Defaults are significant: time getters overcheck by falling back to Last-Modified, `get_mode()` does not check directory markers unless requested, `derive_object_type()` defaults to `UNKNOWN`, and `convert_header_to_stat()` does not force directory mode unless told.

## State And Persistence Behavior
No state is owned by the header. All persistence semantics are caller-driven through HTTP headers and resulting stat/cache metadata. `headers_t` ordering is stable by case-insensitive key comparison, which affects deterministic iteration in callers such as header merging.

## Dependencies And Integration Points
The header depends on `types.h` for `case_insensitive_compare_func` and `objtype_t`, plus standard `map`, `string`, and `sys/stat.h`. It is a central metadata API for the FUSE layer, cache layer, curl response handling, and thread request code.

## Risks
Default arguments can hide important behavior: callers may unknowingly accept Last-Modified fallback as real atime/ctime/mtime, or may fail to enable directory checks when inferring modes. Because `headers_t` is case-insensitive, inserting differently cased duplicate keys overwrites by comparator equivalence, which is desirable for HTTP but should be understood in merge tests.

## Test Signals
Compile and unit tests should verify `headers_t` case-insensitive lookup and overwrite behavior, default argument behavior, and conversion API results for S3, GCS, and s3sync metadata conventions. Integration tests should confirm FUSE `getattr`, `readdir`, rename, symlink, and directory placeholder flows use the expected defaults.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/metaheader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/mpu_util.cpp -->
# sources/user-network-fs/s3fs-fuse/src/mpu_util.cpp

## Purpose
Implements s3fs utility-mode handling for incomplete multipart uploads. It can list outstanding multipart uploads or abort uploads older than a caller-provided age threshold.

## Important APIs, Types, And Functions
The file defines global `utility_incomp_type utility_mode`, initialized to `NO_UTILITY_MODE`. Private `print_incomp_mpu_list()` formats an `incomp_mpu_list_t` to stdout. Private `abort_incomp_mpu_list(list, abort_time)` filters by upload age and calls `abort_multipart_upload_request()` for matching entries. Public `s3fs_utility_processing(abort_time)` performs the list request, XML parsing, and mode-specific output or abort work.

## Control Flow
`s3fs_utility_processing()` rejects calls unless `utility_mode` is set to list or abort. It creates an `S3fsCurl`, calls `MultipartListRequest(body)`, parses the XML response with `xmlReadMemory()`, converts it with `get_incomp_mpu_list()`, then branches on `utility_mode`. Listing prints all parsed entries. Aborting checks each upload date: `abort_time == 0` means abort all, otherwise ISO8601 parsing must succeed and the upload must be older than `now - abort_time`. The function calls `s3fs_destroy_global_ssl()` before returning.

## State And Persistence Behavior
State is mostly external: S3 multipart upload state is read and optionally modified through S3 API requests. Local global `utility_mode` controls behavior. The XML document is managed by a `unique_ptr` with `xmlFreeDoc`. Output goes to stdout and s3fs logs. There is no local persistent state or checkpointing.

## Dependencies And Integration Points
Dependencies include `S3fsCurl::MultipartListRequest`, `get_incomp_mpu_list()` from `s3fs_xml`, `abort_multipart_upload_request()` from thread/curl request helpers, `get_unixtime_from_iso8601()` from `string_util`, libxml2, and global SSL initialization/teardown from the configured auth backend. This code is reached when s3fs is invoked in incomplete-multipart utility modes rather than mounted as a filesystem.

## Risks
`utility_mode` is a mutable global, so command-line parsing must set it exactly once before utility processing. `s3fs_utility_processing()` always destroys global SSL, which is appropriate for one-shot utility mode but would be risky if invoked from a longer-lived initialized context. Failure to parse an upload date skips that entry rather than aborting or failing the whole operation. Abort errors set an overall failure while continuing iteration, which is useful operationally but can leave partial cleanup. User-facing output is produced with `printf`, bypassing structured logging.

## Test Signals
Tests should mock `MultipartListRequest`, XML parsing, and abort calls to cover empty lists, list mode formatting, abort-all, abort-by-age, malformed dates, individual abort failures, XML parse failure, and list request failure. Integration tests can run against a test bucket with staged multipart uploads and verify that only old uploads are aborted when `abort_time` is nonzero.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/mpu_util.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/mpu_util.h -->
# sources/user-network-fs/s3fs-fuse/src/mpu_util.h

## Purpose
Declares data structures and the public entry point for s3fs incomplete multipart upload utility mode.

## Important APIs, Types, And Functions
`INCOMP_MPU_INFO` stores one upload's `key`, `id`, and `date`. `incomp_mpu_list_t` is a vector of those records. `enum class utility_incomp_type : uint8_t` represents no utility mode, list mode, and abort mode. `extern utility_incomp_type utility_mode` is the process-global mode flag. `s3fs_utility_processing(time_t abort_time)` is the public executor.

## Control Flow
The header does not implement behavior, but it defines the mode contract consumed by option parsing and `mpu_util.cpp`. Callers set `utility_mode`, then invoke `s3fs_utility_processing()` with an abort threshold in seconds; list mode ignores the threshold and abort mode uses it.

## State And Persistence Behavior
Only `utility_mode` is declared as shared local state. Multipart upload state itself lives in S3 and is represented transiently by `INCOMP_MPU_INFO` values. No local persistence is declared.

## Dependencies And Integration Points
The header depends on standard `cstdint`, `ctime`, `string`, and `vector`. It is integrated with command-line utility processing, S3 XML parsing that fills `incomp_mpu_list_t`, and request code that aborts multipart upload IDs.

## Risks
The global mode flag is not thread-local or synchronized; utility mode should remain one-shot/single-threaded. `INCOMP_MPU_INFO::date` is a string rather than a parsed time, so malformed date handling is deferred until abort processing. The enum values are simple but should stay aligned with command-line parser expectations.

## Test Signals
Compile tests should verify enum usage and linkage of `utility_mode`. Behavioral tests in `mpu_util.cpp` should create representative `incomp_mpu_list_t` records, including invalid dates and duplicate keys with different upload IDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/mpu_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/nss_auth.cpp -->
# sources/user-network-fs/s3fs-fuse/src/nss_auth.cpp

## Purpose
Provides the NSS-backed implementation of the common s3fs cryptographic API. It supplies the library identity, NSS/NSPR initialization and teardown, HMAC-SHA1, HMAC-SHA256, MD5, and SHA256 for memory buffers and file descriptor ranges.

## Important APIs, Types, And Functions
`s3fs_crypt_lib_name()` returns `NSS`. `s3fs_init_global_ssl()` initializes NSPR with `PR_Init()` and NSS without a database using `NSS_NoDB_Init(nullptr)`. `s3fs_destroy_global_ssl()` calls `NSS_Shutdown()`, `PL_ArenaFinish()`, and `PR_Cleanup()`. Crypt mutex init/destroy are no-ops. Private `s3fs_HMAC_RAW()` creates an internal key slot, imports a symmetric HMAC key, digests data, and returns a heap digest. Public `s3fs_HMAC()` and `s3fs_HMAC256()` select SHA1 or SHA256. `s3fs_md5()`, `s3fs_md5_fd()`, `s3fs_sha256()`, and `s3fs_sha256_fd()` use `PK11_CreateDigestContext()` and `PK11_Digest*()` calls.

## Control Flow
HMAC allocation proceeds through `PK11_GetInternalKeySlot()`, `PK11_ImportSymKey()`, `PK11_CreateContextBySymKey()`, `PK11_DigestBegin()`, `PK11_DigestOp()`, and `PK11_DigestFinal()`, freeing NSS resources on each failure path. File digest functions use the same 512-byte `pread()` loop pattern as the other backends, with `size == -1` resolved by `fstat()`. Digest finalization writes into fixed-size project arrays.

## State And Persistence Behavior
Global state lives inside NSS/NSPR. Per-call NSS contexts, keys, and slots are freed before return. HMAC output is heap-owned by the caller through `unique_ptr`. The file does not persist keys, digest contexts, or output.

## Dependencies And Integration Points
Dependencies include NSS headers (`nss.h`, `pk11pub.h`, `hasht.h`), NSPR (`prinit.h`), POSIX file APIs, and project headers `common.h`, `s3fs.h`, `s3fs_auth.h`, and `s3fs_logger.h`. It is one selectable backend behind the same auth surface consumed by AWS signing and checksum code in `curl.cpp`, `common_auth.cpp`, and upload paths.

## Risks
`s3fs_md5()` and `s3fs_sha256()` do not check `PK11_CreateDigestContext()` for null before using it, so allocation/provider failure could crash. The one-shot memory digest functions do not validate null `data` or result pointers. `PK11_DigestOp()`/`PK11_DigestFinal()` return values are ignored in MD5/SHA256 helpers, so failures can be reported as success. NSS global teardown can be unsafe if other code still depends on NSS in the process.

## Test Signals
Known-vector tests should compare NSS output to OpenSSL/GnuTLS for HMAC-SHA1, HMAC-SHA256, MD5, and SHA256. Fault-injection or wrapper tests should cover digest-context creation failure and PK11 operation failures. File tests should cover invalid fd, `size == -1`, ranged hashes, and read errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/nss_auth.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/openssl_auth.cpp -->
# sources/user-network-fs/s3fs-fuse/src/openssl_auth.cpp

## Purpose
Provides the OpenSSL-backed implementation of the common s3fs cryptographic API. It identifies the backend, exposes no-op global initialization/teardown for modern OpenSSL, and implements HMAC-SHA1, HMAC-SHA256, MD5, and SHA256 over memory and file descriptors using the EVP API.

## Important APIs, Types, And Functions
`s3fs_crypt_lib_name()` returns `OpenSSL`. `s3fs_init_global_ssl()`, `s3fs_destroy_global_ssl()`, `s3fs_init_crypt_mutex()`, and `s3fs_destroy_crypt_mutex()` all return true. Private `s3fs_HMAC_RAW()` wraps `HMAC()` with either `EVP_sha1()` or `EVP_sha256()`. Private `s3fs_digest()` hashes memory with `EVP_MD_CTX_new()`, `EVP_DigestInit_ex()`, `EVP_DigestUpdate()`, and `EVP_DigestFinal_ex()`. Private `s3fs_digest_fd()` applies the same EVP flow to a 512-byte `pread()` loop. Public `s3fs_md5*` and `s3fs_sha256*` select the EVP digest.

## Control Flow
HMAC validates `key`, `data`, and `digestlen`, allocates `EVP_MAX_MD_SIZE`, and lets OpenSSL write the actual digest length. Memory digest helpers allocate an `EVP_MD_CTX` with RAII `unique_ptr`, return false on any EVP failure, and log OpenSSL error strings. File digesting rejects `fd == -1`, resolves `size == -1` with `fstat()`, initializes the context, updates it for each read block, stops on EOF, and finalizes into caller storage.

## State And Persistence Behavior
The OpenSSL backend relies on OpenSSL 1.1+ internal global initialization and threading. Per-call state is local and freed through RAII. Digest outputs are caller-owned arrays or `unique_ptr` buffers. There is no local persistent state.

## Dependencies And Integration Points
Dependencies include OpenSSL EVP/HMAC/ERR headers, POSIX `pread()`/`fstat()`, and `s3fs_auth.h`/`s3fs_logger.h`. It implements the same common API used by curl signing, payload hashing, common hex helpers, and multipart checksum code.

## Risks
Memory digest functions do not check null `data` or output pointers before passing them to OpenSSL. `s3fs_HMAC_RAW()` casts `keylen` to `int`; extremely large keys could truncate. `ERR_get_error()` may return zero when the failure did not populate the error queue, resulting in a null or unhelpful reason string. As with other backends, file hashing can silently hash fewer bytes if EOF occurs before the requested size.

## Test Signals
Known-vector tests should cover HMAC-SHA1, HMAC-SHA256, MD5, and SHA256, including empty input. File hashing tests should compare memory and fd hashes for full files and slices. Error-path tests should cover invalid fd, `fstat()` failure, and read errors. Cross-backend tests are valuable because the same API must behave identically across OpenSSL, NSS, and GnuTLS builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/openssl_auth.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/psemaphore.h -->
# sources/user-network-fs/s3fs-fuse/src/psemaphore.h

## Purpose
Defines a portable `Semaphore` abstraction for s3fs-fuse. It uses C++20 `std::counting_semaphore` when available, Grand Central Dispatch semaphores on macOS for pre-C++20 builds, and POSIX `sem_t` elsewhere.

## Important APIs, Types, And Functions
For C++20 and newer, `using Semaphore = std::counting_semaphore<INT_MAX>`. On macOS, the class wraps `dispatch_semaphore_t` with constructor, destructor, deleted copy/move, `acquire()`, `try_acquire()`, and `release()`. On non-Apple pre-C++20 platforms, the class wraps `sem_t` with `sem_init()`, `sem_destroy()`, `sem_wait()` retrying on `EINTR`, `sem_trywait()` retrying on `EINTR`, and `sem_post()`.

## Control Flow
Preprocessor selection is the main control flow. The POSIX `acquire()` loop blocks until `sem_wait()` succeeds or fails for an error other than `EINTR`, but it does not surface non-EINTR failures. `try_acquire()` retries on interrupt and returns true only on immediate acquisition. The macOS destructor posts `value` times before `dispatch_release()` because the comment states macOS cannot destroy a semaphore with fewer posts than its initializer.

## State And Persistence Behavior
Semaphore state is in process memory and owned by the underlying standard library, dispatch object, or POSIX semaphore. The wrapper is non-copyable and non-movable in custom implementations. There is no file or interprocess persistence; POSIX `sem_init()` uses `pshared = 0`.

## Dependencies And Integration Points
The C++20 path depends on `<semaphore>` and `INT_MAX`; the Apple path depends on `<dispatch/dispatch.h>`; the POSIX path depends on `<cerrno>` and `<semaphore.h>`. This header can be included by request/thread coordination code that needs a uniform counting semaphore across Linux, macOS, and newer C++ builds.

## Risks
The C++20 branch uses `INT_MAX` without including `<climits>` in this header, relying on prior includes or implementation leakage. The POSIX constructor and destructor ignore `sem_init()`/`sem_destroy()` return values, and `acquire()` ignores non-EINTR failures. The macOS destructor's forced releases can wake waiting threads during object destruction if lifetime is not externally quiesced. The C++20 alias lacks deleted copy/move declarations from the custom classes, so exact type traits differ by standard version.

## Test Signals
Build tests should cover C++20, macOS pre-C++20, and POSIX pre-C++20 configurations. Runtime tests should verify acquire/release counting, failed `try_acquire()` on zero count, retry after signal interruption on POSIX, and safe destruction only after users stop waiting. Static checks should confirm `<climits>` availability or add it if the C++20 path fails in isolation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/psemaphore.h -->
