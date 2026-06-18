# Research: subset-b-009799

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs.cpp -->
# sources/user-network-fs/s3fs-fuse/src/s3fs.cpp

## Purpose

This file is the main executable and FUSE operation implementation for `s3fs`, a filesystem that projects an S3 bucket or bucket prefix as a POSIX-like filesystem. It owns the command-line parser, process initialization, the `fuse_operations` table, service/bucket validation, and almost every high-level filesystem operation: attribute lookup, directory creation/removal/listing, object creation/deletion/rename, symlink handling, chmod/chown/utimens, truncate/open/read/write/flush/fsync/release, statfs, access checks, and optional extended attributes.

The implementation translates filesystem state into S3 objects plus S3 user metadata. Object bodies store regular file data and symlink targets; metadata headers store POSIX-ish fields such as uid, gid, mode, atime, mtime, ctime, content type, and optional xattrs. It relies heavily on stat and file caches to mask S3 latency and to preserve local semantics for files that are open, dirty, or not yet uploaded.

## Important APIs, Types, and Functions

The public surface in this file is mostly the `main()` function plus a few non-static helpers used by other compilation units:

- `main(int argc, char* argv[])`: initializes XML, SSL, curl, credentials, options, cache/disk policy, FUSE operation callbacks, enters `fuse_main`, then destroys curl/SSL/XML state.
- `put_headers(const char* path, const headers_t& meta, bool is_copy, bool use_st_size)`: updates object metadata through copy-style PUT header requests, switching to multipart metadata copy for large objects.
- `get_object_sse_type(const char* path, sse_type_t& ssetype, std::string& ssevalue)`: reads object metadata and reports SSE-S3, SSE-KMS, SSE-C, or disabled state.

Most implementation functions are static FUSE callbacks or helpers:

- Metadata and access: `get_object_attribute`, `chk_dir_object_type`, `remove_old_type_dir`, `check_object_access`, `check_object_owner`, `check_parent_object_access`.
- Object creation/removal: `create_file_object`, `s3fs_mknod`, `s3fs_create`, `create_directory_object`, `s3fs_mkdir`, `s3fs_unlink`, `s3fs_rmdir`, `directory_empty`.
- Rename/copy: `rename_object`, `rename_object_nocopy`, `rename_large_object`, `clone_directory_object`, `rename_directory`, `s3fs_rename`.
- Metadata mutation: `s3fs_chmod`, `s3fs_chmod_nocopy`, `s3fs_chown`, `s3fs_chown_nocopy`, `s3fs_utimens`, `s3fs_utimens_nocopy`, `update_mctime_parent_directory`.
- Data path: `s3fs_truncate`, `s3fs_open`, `s3fs_read`, `s3fs_write`, `s3fs_flush`, `s3fs_fsync`, `s3fs_release`.
- Directories: `s3fs_opendir`, `s3fs_readdir`, `readdir_multi_head`, `list_bucket`, `remote_mountpath_exists`.
- Xattrs: `get_meta_xattr_value`, `get_parent_meta_xattr_value`, `get_xattr_posix_key_value`, `build_inherited_xattr_value`, `build_xattrs`, `set_xattrs_to_header`, `s3fs_setxattr`, `s3fs_getxattr`, `s3fs_listxattr`, `s3fs_removexattr`.
- Startup and options: `s3fs_init`, `s3fs_destroy`, `s3fs_check_service`, `set_mountpoint_attribute`, `set_bucket`, `parse_bucket_size`, `my_fuse_opt_proc`.

Important local state includes mountpoint uid/gid/mode/umask, FUSE uid/gid/umask overrides, `mountpoint`, `nocopyapi`, `norenameapi`, `support_compat_dir`, multipart thresholds, `singlepart_copy_limit`, `max_dirty_data`, `fake_diskfree_size`, `update_parent_dir_stat`, `bucket_block_count`, `s3fs_block_size`, and atomic `has_mp_stat`.

## Control Flow

Startup begins in `main()`. It initializes libxml and platform sysconf data, configures the credential object on `S3fsCurl`, parses top-level long options, loads SSE environment settings, initializes SSL and curl, then lets `fuse_opt_parse` call `my_fuse_opt_proc` for s3fs-specific `-o` options and non-option bucket/mountpoint arguments. After option validation, it checks credential consistency, mountpoint presence, temp/cache directories, disk-space policy, utility mode, and multipart/cache mode interactions. It then fills `struct fuse_operations`; xattr callbacks are only registered when `use_xattr` is enabled, and chmod/chown/utimens choose copy or nocopy implementations based on `nocopyapi`.

FUSE initialization calls `s3fs_init()`, which optionally removes cache directories, initializes the thread pool, loads IAM role metadata, validates bucket access through `s3fs_check_service()`, enables atomic truncation where available, and installs signal handling. `s3fs_check_service()` issues a service check and handles region mismatch, invalid credentials, permanent redirect, and invalid SSE argument responses with targeted retry or fatal messages.

Attribute lookup centers on `get_object_attribute()`. It normalizes mountpoint cases, recognizes directory encodings (`dir/`, `dir`, `dir_$folder$`, and implicit directories with only children), checks `StatCache`, sends HEAD requests, performs compatible-directory overchecks only after `-ENOENT`, optionally does list checks through `directory_empty`, converts headers into `struct stat`, and writes positive or negative cache entries. Permission checks layer on top of this metadata with FUSE context uid/gid and configured uid/gid/umask overrides.

Object mutation generally follows S3 constraints. Creating files or directories builds metadata headers and either creates an empty object or creates an open dirty `FdEntity` that is uploaded later. Metadata-only changes normally use `x-amz-copy-source` with `x-amz-metadata-directive: REPLACE`; when copy APIs are disabled, they load the whole object through `FdEntity`, mutate local metadata, and flush/reupload. Large copies route through multipart copy. Directory changes may rebuild legacy directory objects into normalized `dir/` objects.

The file data path is cache-backed. `s3fs_open()` resolves permissions and metadata, pins stat cache with the no-truncate flag, opens an `FdEntity`, and handles `O_TRUNC`. `s3fs_read()` and `s3fs_write()` operate on an existing pseudo fd from `fi->fh`; writes update ctime/mtime and may trigger `RowFlush()` when `BytesModified()` exceeds `max_dirty_data`, then punch holes to reclaim cache disk space. `flush`, `fsync`, and `release` coordinate content upload, pending metadata upload, stat cache updates, and parent directory timestamp updates.

Directory listing uses `list_bucket()` to issue ListObjects v1/v2 requests with delimiter/prefix/max-keys parameters, parse XML with libxml, append objects into `S3ObjList`, and follow continuation tokens or markers. `s3fs_readdir()` fills `.` and `..`, then `readdir_multi_head()` issues batched HEAD requests through `multi_head_request` and `ThreadPoolMan`-backed machinery to populate stat data for entries. It also merges entries that exist only in `StatCache`, covering newly created but not yet uploaded files.

## State and Persistence Behavior

Persistent filesystem state is stored in S3 object bodies and headers. Regular file contents are object bodies; symlink targets are stored as object bodies with symlink mode metadata; directories are represented as zero-length directory objects, usually normalized to keys ending with `/`. POSIX attributes live in `x-amz-meta-*` headers: uid, gid, mode, atime, ctime, mtime, xattr, and content type.

In-memory and local state is equally important. `StatCache` stores positive stats, negative entries, xattr/symlink data, directory object lists, and no-truncate entries for open/new files. `FdManager`, `FdEntity`, and `AutoFdEntity` manage local temporary or cache files, pseudo fds, dirty page tracking, multipart upload state, pending metadata, and cache file renames/deletes. Startup options control cache deletion, cache directory use, disk-space guarantees, multipart thresholds, thread counts, and xattr registration.

The file explicitly handles S3's lack of atomic POSIX operations. Rename copies to the destination then deletes the source. Directory rename enumerates all children, creates destination directories first, copies files, then removes old directories bottom-up. Chmod/chown/utimens and xattr changes are metadata replacement copies unless `nocopyapi` forces a full object reload/reupload. Parent directory timestamps are optional and disabled unless `update_parent_dir_stat` is set.

## Dependencies and Integration Points

This file integrates with:

- FUSE/libfuse through `fuse.h`, `struct fuse_operations`, FUSE context, `fuse_main`, and `fuse_exit`.
- Curl/S3 wrappers from `curl.h`, `curl_share.h`, `curl_util.h`, and credential classes from `s3fs_cred.h`.
- Metadata utilities from `metaheader.h`, including header/stat conversion, object type detection, and xattr parsing/building.
- Cache and fd layers from `fdcache.h`, `fdcache_auto.h`, `fdcache_stat.h`, and `cache.h`.
- S3 listing/XML support through `s3objlist.h`, `s3fs_xml.h`, and libxml calls.
- Multipart utilities through `mpu_util.h` and thread coordination through `s3fs_threadreqs.h` and `threadpoolman.h`.
- Logging, help, signal, string, and platform utility modules.
- Crypto/auth init functions declared in `s3fs_auth.h` for SSL lifecycle and reporting the crypto backend.

The code also depends on many global configuration variables declared elsewhere, such as `mount_prefix`, `region`, `s3host`, `service_path`, `pathrequeststyle`, `nomultipart`, `noxmlns`, `foreground`, `utility_mode`, request counters, and logging flags.

## Risks and Edge Cases

The highest-risk area is the semantic mismatch between POSIX and S3. Rename and metadata updates are non-atomic copy/delete sequences. A failure after destination copy but before source delete can leave duplicates; a failure during directory rename can leave a partially copied tree. Concurrent writers across processes or hosts can observe stale stat/list cache or overwrite metadata with copy-replace operations.

The stat path is intentionally complex and should be regression-tested carefully. It handles mountpoint stat objects, bucket-root `//` special cases, negative cache, compatible directory suffixes, implicit directories, and backend quirks where HEAD on `dir` succeeds when only `dir/` exists. The code explicitly avoids compatible-directory overchecks after transient non-ENOENT errors to avoid recreating objects during temporary failures.

Open-file state is delicate. Newly created files may exist only in no-truncate stat cache until flush/release uploads them. Metadata mutations on open files merge into `FdEntity` pending metadata, so bugs in `MergeOrgMeta`, `UploadPending`, or stat cache refresh can expose stale attributes. FUSE can call `release` without prior `flush`, so `release` has to upload modified content defensively.

Directory listing depends on XML parsing and continuation token logic. `list_bucket()` must handle empty XML bodies, v1/v2 marker differences, delimiter and prefix encoding, CR encoding, and `check_content_only` short-circuit behavior. `readdir_multi_head()` has stack-local objects shared with scheduled requests and therefore must drain already scheduled work on scheduling failure.

Option parsing is broad and mutates global state directly. Conflicts among SSE modes, storage class, signature mode, cache/disk options, public bucket/nocopy behavior, and multipart settings can produce subtle behavior changes. `is_cmd_exists()` builds a shell command from a string, but current callers pass hardcoded command names only.

`parse_bucket_size()` appears fragile: the digit-validation loop uses `for(size_t i = 0; i < pos; ++i)`, but `pos` is not initialized when no unit suffix is present. That deserves focused review or tests because `bucket_size=12345` without a suffix may exercise undefined or unintended behavior.

## Test Signals

Useful tests should mount against a controllable S3-compatible backend and cover:

- `getattr` on files, symlinks, `dir/`, legacy `dir`, `dir_$folder$`, implicit directories, root mountpoint, and bucket-prefix mountpoint with and without `compat_dir`.
- Negative cache behavior, stat cache expiration, no-truncate cache for newly created/open files, and cache invalidation after unlink/rmdir/rename/truncate.
- File create/open/write/read/flush/fsync/release, including `O_TRUNC`, sparse/large writes, `max_dirty_data`, no cache directory, cache directory, multipart, `nomultipart`, and disk-space pressure.
- Rename for regular files, > `singlepart_copy_limit` files, open dirty files, symlinks, directories with nested children, and injected failures between copy and delete.
- chmod/chown/utimens in normal and `nocopyapi` modes, including open-file pending metadata.
- xattr set/get/list/remove, POSIX ACL inheritance from parent default ACLs, xattr deletion that removes the S3 metadata key, and xattrs on directories requiring legacy directory replacement.
- `s3fs_check_service()` response handling for wrong region, permanent redirect, invalid credentials, invalid SSE argument, missing bucket, missing mount prefix, and public bucket mode.
- Option parsing for SSE variants, credential options, cache/disk options, bucket prefix syntax, `bucket_size` with and without suffixes, and incompatible combinations.

<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs.h -->
# sources/user-network-fs/s3fs-fuse/src/s3fs.h

## Purpose

This header provides the small FUSE-facing compatibility layer used by the s3fs main implementation. It selects the libfuse API version, disables FUSE-T's Darwin-specific operation overloading on macOS, includes `fuse.h`, defines a fallback fill-dir flag constant for older FUSE versions, and defines a convenience macro for exiting the active FUSE loop.

## Important APIs, Types, and Functions

- `FUSE_USE_VERSION 30`: requests the libfuse 3 API surface before including `fuse.h`.
- `FUSE_DARWIN_ENABLE_EXTENSIONS 0` and `FUSE_DARWIN_OVERLOAD_OPERATIONS 0`: on Apple platforms, opt out of FUSE-T overloads so callback signatures continue to match upstream libfuse3 signatures used in `s3fs.cpp`.
- `S3FS_FUSE_FILL_DIR_DEFAULTS`: a `constexpr fuse_fill_dir_flags` value set to zero. The comment notes that `FUSE_FILL_DIR_DEFAULTS` requires FUSE 3.17, so this constant preserves compatibility with older libfuse3 headers.
- `S3FS_FUSE_EXIT()`: macro that obtains `fuse_get_context()`, checks it, and calls `fuse_exit(pcxt->fuse)`.

## Control Flow

There is no runtime control flow besides the macro expansion. Consumers include this header before declaring or assigning FUSE callbacks. Directory-reading code passes `S3FS_FUSE_FILL_DIR_DEFAULTS` to the FUSE filler callback when inserting `.` and `..`. Error paths that want to terminate the FUSE loop can use `S3FS_FUSE_EXIT()`, although `s3fs.cpp` currently has a local `s3fs_exit_fuseloop()` helper for startup failures.

## State and Persistence Behavior

This header owns no persistent state and no process state beyond compile-time preprocessor configuration. Its choices affect ABI compatibility with libfuse and platform-specific callback signatures, not filesystem metadata or S3 persistence.

## Dependencies and Integration Points

The direct dependency is `<fuse.h>`. The header must be included in translation units that need libfuse declarations after `FUSE_USE_VERSION` is set. It is included by `s3fs.cpp`, where the `fuse_operations` table is populated and where `S3FS_FUSE_FILL_DIR_DEFAULTS` is used in `s3fs_readdir()`.

The Apple-specific defines are an integration point with FUSE-T's libfuse3 fork. They reduce platform divergence by forcing standard libfuse3 signatures instead of Darwin-specific overloaded types such as `fuse_darwin_attr`.

## Risks and Edge Cases

Because `FUSE_USE_VERSION` must be defined before `fuse.h`, include order matters. A translation unit that includes `fuse.h` first with a different version could see incompatible declarations. The zero-valued fill-dir constant is intentionally compatible with older FUSE headers, but it also means newer named defaults are not used directly. The exit macro is safe against a null FUSE context, but it silently does nothing when called outside a FUSE callback context.

## Test Signals

Build tests should cover Linux, macOS/FUSE-T, and any WinFsp/MSYS build variants that include this header. Compile checks should verify that all callback signatures in `s3fs.cpp` match the selected libfuse headers. Runtime smoke tests for `readdir` should verify that `.` and `..` are filled correctly with the zero fill-dir flags on older and newer FUSE 3 versions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_auth.h -->
# sources/user-network-fs/s3fs-fuse/src/s3fs_auth.h

## Purpose

This header declares the cryptographic and digest primitives used by s3fs authentication, payload hashing, and request signing. It abstracts the concrete crypto backend behind a stable set of functions for MD5, SHA-256, HMAC, SSL/global crypto initialization, and crypto mutex lifecycle. The implementation is split across common auth code and backend-specific auth files.

## Important APIs, Types, and Functions

- `using md5_t = std::array<unsigned char, 16>` and `using sha256_t = std::array<unsigned char, 32>` define fixed-size binary digest containers.
- `s3fs_get_content_md5(int fd)`: declared as a common auth helper that computes the Content-MD5 representation for a file descriptor.
- `s3fs_sha256_hex_fd(int fd, off_t start, off_t size)`: common helper that returns a hex SHA-256 digest over a file descriptor range.
- `s3fs_crypt_lib_name()`: reports the active crypto library/backend name; `s3fs.cpp` uses this in startup logging.
- `s3fs_init_global_ssl()` and `s3fs_destroy_global_ssl()`: initialize and tear down global SSL/crypto library state around curl/FUSE process lifetime.
- `s3fs_init_crypt_mutex()` and `s3fs_destroy_crypt_mutex()`: manage backend mutex support, typically relevant for crypto libraries or versions requiring explicit thread-safety callbacks.
- `s3fs_HMAC()` and `s3fs_HMAC256()`: compute HMAC digests using caller-provided key/data buffers and return owned byte arrays plus digest length.
- `s3fs_md5()`, `s3fs_md5_fd()`, `s3fs_sha256()`, and `s3fs_sha256_fd()`: compute binary MD5 or SHA-256 digests for memory buffers or file descriptor ranges.

## Control Flow

This file contains declarations only. The expected process flow is: startup initializes global SSL/crypto state before curl/S3 operations, request-signing code calls HMAC and SHA-256 helpers as needed, upload code can compute MD5/SHA-256 over file contents or ranges, and shutdown destroys curl and then global SSL/crypto state. `s3fs.cpp` follows that lifecycle by calling `s3fs_init_global_ssl()` before `S3fsCurl::InitS3fsCurl()` and `s3fs_destroy_global_ssl()` after destroying curl.

## State and Persistence Behavior

The header declares functions that may manage global crypto/SSL state and mutex state in their implementations, but it defines no state itself. Digest functions operate on caller-provided buffers or file descriptors and return computed digests; they do not persist data. The `unique_ptr<unsigned char[]>` return values make ownership explicit for HMAC result buffers.

## Dependencies and Integration Points

The header depends on `<array>`, `<memory>`, `<string>`, and `<sys/types.h>` for digest containers, owned buffers, string return values, and `off_t`. It is included by `s3fs.cpp` for crypto backend reporting and SSL lifecycle, and it is likely included by curl/auth/signing modules that need SigV2/SigV4 HMACs, payload hashes, SSE-C key checks, or Content-MD5 generation.

The comments indicate a split implementation: common file-descriptor digest helpers live in `common_auth.cpp`, while backend-specific functions live in `xxxxxx_auth.cpp` implementations, such as OpenSSL or alternative crypto-library adapters.

## Risks and Edge Cases

The API returns null-like `unique_ptr` values or `bool` status for failures, so callers must consistently check results and digest lengths. File-descriptor digest functions accept `off_t start` and `off_t size`; implementations must preserve the fd offset or document changes, handle negative/overflowing ranges, partial reads, EINTR, sparse files, and very large objects. Global SSL lifecycle ordering matters: destroying SSL before curl or worker threads finish using crypto would be unsafe. Thread-safety mutex setup must match the selected backend's requirements.

MD5 remains present because S3 uses Content-MD5 and SSE-C key MD5 workflows, but it is not collision-resistant for general integrity decisions. Callers should prefer SHA-256/HMAC-SHA256 for authentication and signing where the protocol allows it.

## Test Signals

Unit tests should verify MD5 and SHA-256 against known vectors for memory buffers and fd ranges, including empty input, partial ranges, unaligned offsets, and large files. HMAC and HMAC-SHA256 should be checked against standard test vectors and should validate digest length outputs. Lifecycle tests should call init/destroy repeatedly where supported and run digest/HMAC work concurrently under thread sanitizer or equivalent. Integration tests should validate SigV4 signing, Content-MD5 upload headers, unsigned-payload mode, and SSE-C metadata/key-MD5 behavior against a local S3-compatible service.

<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/s3fs_auth.h -->
