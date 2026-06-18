<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/cache_node.cpp -->
# Research: sources/user-network-fs/s3fs-fuse/src/cache_node.cpp

Purpose: implementation of s3fs's in-memory stat cache tree. It stores object type, stat data, selected S3 metadata, symlink targets, negative lookup entries, child directory maps, and cached `S3ObjList` directory listings so FUSE path operations can avoid repeated S3 HEAD/LIST calls.

Important APIs: implements `StatCacheNode` and derived `FileStatCache`, `DirStatCache`, `SymlinkStatCache`, and `NegativeStatCache` declared in `cache_node.h`. Public entry points are `Add`, `AddS3ObjList`, `Find`, `Get`, `GetExtra`, `GetChildMap`, `GetS3ObjList`, `Update`, `Set`, `RemoveChild`, `Clear`, `ClearData`, `TruncateCache`, `PreventExpireCheck`, `ResumeExpireCheck`, expiration configuration, negative-cache toggles, counters, and debug `Dump`.

Control flow: `StatCacheNode` constructors normalize paths by appending a slash for directories and removing one for non-directories, then stamp monotonic cache time and increment total counters. Directory `AddHasLock` first determines whether the target is this directory, a direct child, or a descendant; it then updates existing children, replaces stale negative/type-mismatched nodes, or creates intermediate `DirStatCache` nodes recursively. `FindHasLock` walks the same tree, validates expiration and optional ETag, and removes direct children when stale or mismatched. `RemoveChildHasLock` walks to the target, clears data for directory leaves but erases file/symlink/negative leaves, and synchronizes the cached `S3ObjList`. `TruncateCacheHasLock` recursively clears expired data and erases removable children, updating `last_check_date` only when something was actually truncated.

State and persistence: state is process-local only. Static state includes cache counters, expiration flags, negative-cache setting, the global `cache_lock`, and the `DisableCheckingExpire` suppression window used by `PreventStatCacheExpire`. Per-node state includes path, type, hit count, monotonic cache date, no-truncate bit, stat buffer, filtered metadata headers, and optional extra value. Directory nodes add `dir_cache_lock`, `last_check_date`, a child map keyed by leaf names, and an optional `S3ObjList`. No state is persisted to disk; correctness depends on cache invalidation and later S3 refreshes.

Dependencies/integration: depends on `s3fs_logger.h` for diagnostics, `string_util.h` for formatting/comparison helpers, `metaheader.h` for metadata format predicates, `s3objlist.h` for directory listing snapshots, and `types.h` object-type macros such as `IS_DIR_OBJ`. Consumers elsewhere in s3fs use this cache to answer getattr/readdir/symlink/object-type checks and to store negative lookup results.

Concurrency behavior: most base-node fields are protected by one static `StatCacheNode::cache_lock`; directory child/list state has a per-directory `dir_cache_lock`. Methods generally take the global lock first and then directory locks, and annotations in the header document that order. Shared pointers allow recursive tree traversal while children may be erased from maps.

Risks: the global cache lock serializes all stat-cache operations and may become a scalability point under high FUSE concurrency. `DirStatCache::NeedTruncateProcessing` reads the private base `cache_date` field despite it being declared private in the header; that relies on the actual class-access relationship compiling as written and is a maintenance hazard. The recursive remove/truncate paths call child methods while holding parent directory locks, so any future lock-order change could deadlock. Negative caches intentionally ignore ETags, so stale nonexistence can persist until timeout. Metadata copying filters headers, which is good for memory but can surprise callers expecting arbitrary headers.

Test signals: unit tests should cover path normalization, direct versus nested add/find/remove, UNKNOWN type inference from stat and metadata, negative-cache enable/disable, replacement of negative entries by real objects, stale ETag removal, expiration interval mode updating cache dates on reads, `PreventStatCacheExpire` suppression, `S3ObjList` invalidation when child maps change, and recursive truncation of empty directories. Threaded tests should stress add/find/remove under concurrent FUSE-style operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/cache_node.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/cache_node.h -->
# Research: sources/user-network-fs/s3fs-fuse/src/cache_node.h

Purpose: declares the stat-cache tree abstraction used by s3fs to represent cached S3 object metadata and directory hierarchy. It defines base and derived node types, expiration control, negative-cache support, counters, locking annotations, and an RAII guard for temporarily preventing expiration checks.

Important APIs/types: `StatCacheNode` is the base class and `enable_shared_from_this` owner for cached objects. `FileStatCache`, `DirStatCache`, `SymlinkStatCache`, and `NegativeStatCache` specialize object behavior. `statcache_map_t` maps child leaf names to node pointers. `stat_counter_pos` maps `objtype_t` categories to counter slots. `PreventStatCacheExpire` calls `StatCacheNode::PreventExpireCheck` in its constructor and `ResumeExpireCheck` in its destructor.

Control flow surface: public methods wrap protected `HasLock` methods with the global cache mutex. External callers add stat/meta data with `Add`, store cached listings with `AddS3ObjList`, query nodes with `Find`/`Get`, get symlink extra values with `GetExtra`, enumerate children with `GetChildMap`, and force invalidation with `RemoveChild`/`TruncateCache`. Directory overrides perform recursive path routing and maintain child/list state; negative nodes override ETag and expiration semantics.

State and persistence: declares static cache-wide state for counters, expiration settings, negative-cache setting, the global mutex, and expiration-suppression bookkeeping. Base nodes store full path, type, hit count, cache timestamp, no-truncate flag, stat buffer, filtered metadata, and optional extra value. Directory nodes store an independent mutex, last truncate-check time, destructor-time type backup, children, and optional `S3ObjList`. Everything is in-memory and rebuilt from S3 or filesystem actions.

Dependencies/integration: includes `common.h` for thread-safety annotation macros and global types, `metaheader.h` for `headers_t`, `s3objlist.h` for directory listing cache, and `types.h` for `objtype_t`/object-type macros. The annotations are intended for clang thread-safety analysis and document lock requirements across implementation methods.

Risks: the class exposes many overloaded operations with subtly different semantics, especially `Update` versus `Set`, directory `ClearData`, and extra-value handling only for symlinks. Lock annotations help, but one static mutex for all base state makes future fine-grained changes easy to get wrong. The friend relationship grants `DirStatCache` access to protected members for recursive maintenance, increasing coupling. Directory path invariants require trailing slashes and child keys without slashes; callers must pass normalized full paths or rely on constructor/add logic.

Test signals: compile-time thread-safety checks under clang are valuable for this header. Behavioral tests should instantiate each node class, verify counter movement through construction/destruction/type update, ensure public wrappers acquire locks and delegate correctly, validate path suffix invariants, and check RAII expiration suppression nests and resumes properly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/cache_node.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/common.h -->
# Research: sources/user-network-fs/s3fs-fuse/src/common.h

Purpose: shared global declarations and cross-file constants/macros for the s3fs codebase. It centralizes mount/request configuration globals, request counters, multipart size constants, weak-function attributes, and clang thread-safety annotation compatibility macros.

Important APIs/types: exports constants `FIVE_GB` and `MIN_MULTIPART_SIZE`. Declares global mount/config variables such as `foreground`, `nomultipart`, `pathrequeststyle`, `noxmlns`, `insecure_logging`, `program_name`, `service_path`, `s3host`, `mount_prefix`, `region`, `cipher_suites`, and `instance_name`. Declares atomic request counters for HEAD/PUT/GET/DELETE/LIST and multipart phases. Defines `S3FS_FUNCATTR_WEAK` and thread-safety macros `GUARDED_BY`, `PT_GUARDED_BY`, `REQUIRES`, `RETURN_CAPABILITY`, `ACQUIRED_BEFORE`, `ACQUIRED_AFTER`, and `NO_THREAD_SAFETY_ANALYSIS`.

Control flow: this header contains no runtime control flow. Its compile-time flow is conditional: under clang, thread annotations expand to attributes; under other compilers, they are no-ops. The included generated `config.h` controls version and feature symbols used elsewhere.

State and persistence: no storage is defined here, but the `extern` globals are mutable process-wide state used by request construction, logging, credential/signing behavior, and statistics. Request counters are atomics, which makes increments safe across FUSE threads, but other string/bool globals rely on initialization-time mutation or external discipline.

Dependencies/integration: heavily included by cache, curl, auth, and utility code. `FIVE_GB` and `MIN_MULTIPART_SIZE` integrate with multipart upload limits. Thread annotations are consumed by headers such as `cache_node.h`, `curl.h`, and `curl_share.h` to document mutex discipline without requiring clang.

Risks: global mutable configuration makes tests and long-running process reconfiguration sensitive to initialization order and teardown leakage. The `TODO: namespace these` comment is apt: symbol collisions are possible in a large C++ codebase. Non-atomic globals read by request paths should be set before worker threads start. On non-clang compilers, thread-safety annotations disappear, so lock-contract regressions can slip through unless clang analysis is part of CI.

Test signals: build with clang thread-safety warnings enabled, verify generated `config.h` supplies expected symbols, and run integration tests that assert request counters increment under concurrent S3 operations. Configuration tests should ensure globals are initialized once before request-handling threads start.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/common_auth.cpp -->
# Research: sources/user-network-fs/s3fs-fuse/src/common_auth.cpp

Purpose: small authentication/hash helper implementation for computing request payload hashes used by S3 HTTP headers and AWS signature generation.

Important APIs: `s3fs_get_content_md5(int fd)` computes an MD5 digest over an entire file descriptor and returns base64. `s3fs_sha256_hex_fd(int fd, off_t start, off_t size)` computes a SHA-256 digest over a file descriptor range and returns lowercase hex.

Control flow: each function delegates to lower-level crypto/file helpers from `s3fs_auth.h`, checks the boolean success result, returns an empty string on failure, and encodes the raw digest via `s3fs_base64` or `s3fs_hex_lower` from `string_util.h`.

State and persistence: stateless except for reading from the supplied file descriptor. No persistent data is written. Callers treat an empty string as failure; in `curl.cpp`, this maps to `-EIO` for MD5/SHA256 setup failures.

Dependencies/integration: used by `S3fsCurl::PutRequest` for `Content-MD5` and by Signature V4 payload hash calculation for full PUTs and multipart parts. Depends on digest typedefs (`md5_t`, `sha256_t`) and helpers `s3fs_md5_fd`, `s3fs_sha256_fd`, `s3fs_base64`, and `s3fs_hex_lower`.

Risks: empty string conflates digest failure with a theoretically empty textual result, though these encodings are never empty for valid hashes. Hash helpers must preserve file descriptor offsets or callers must reset around them; `curl.cpp` separately duplicates/rewinds file descriptors for upload. Large-file hashing is synchronous and can be expensive before upload.

Test signals: verify MD5/base64 and SHA256/hex against known files, partial ranges, zero-length ranges, invalid descriptors, and descriptor-offset behavior. Curl request tests should confirm failures propagate to `-EIO` and successful hashes appear in signing/header paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/common_auth.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl.cpp -->
# Research: sources/user-network-fs/s3fs-fuse/src/curl.cpp

Purpose: primary S3/libcurl transport implementation for s3fs. It owns global libcurl initialization, per-request handle setup, request signing, retry/error mapping, server-side encryption headers, MIME/user-agent/proxy/client-cert configuration, IAM metadata/token calls, object HEAD/GET/PUT/DELETE, bucket LIST/check, and multipart upload/copy workflows.

Important APIs: class-level setup includes `InitS3fsCurl`, `DestroyS3fsCurl`, `InitCredentialObject`, `InitMimeType`, `InitUserAgent`, `LoadEnvSse`, `SetSseCKeys`, `SetSseKmsid`, `FinalCheckSse`, timeout/retry/proxy/cert/storage-class/signature toggles, and multipart size setters. Request APIs include `DeleteRequest`, `HeadRequest`, `PutHeadRequest`, `PutRequest`, `PreGetObjectRequest`, `GetObjectRequest`, `CheckBucket`, `ListBucketRequest`, `PreMultipartUploadRequest`, `MultipartUploadPartSetup`, `MultipartUploadPartRequest`, `MultipartUploadComplete`, `MultipartListRequest`, `AbortMultipartUpload`, `MultipartPutHeadRequest`, IAM token/credential methods, and response/error accessors.

Control flow: callers configure global static options, create an `S3fsCurl` instance, then call a specific request method. Request methods build URL/resource data via `MakeUrlResource` and `prepare_url`, populate `requestHeaders`, set `op` and `REQTYPE`, install libcurl options either immediately or through a lazy setup function, then call `RequestPerform`. `RequestPerform` signs headers unless disabled, applies the slist to the handle, performs curl, maps HTTP and libcurl errors to negative errno values, and retries transient failures by `RemakeHandle`, which rebuilds options from saved backup fields. Signature V4 computes payload hashes for PUT and multipart body types, adds host/date/content-sha256 headers, and signs canonical headers/query. Signature V2 builds the legacy string-to-sign using sorted `x-amz` headers.

State and persistence: static state stores global libcurl/configuration and request policy: certificate checks, timeouts, retry count, public-bucket flag, default ACL, storage class, SSE-C keys, SSE-KMS id, SSE type, MD5/verbose/body dump flags, credential object pointer, client certificate options, MIME table, user agent, multipart sizes, signature mode, unsigned payload flag, ListObjectsV2/requester-pays flags, proxy settings, and IP resolution. Per-instance state stores handle, request type, path/url, response headers/body/head data, post/upload file data, retry backups, operation verb, query string, lazy setup callback, and last curl code/response code. Persistent remote state is changed by S3 object, bucket, and multipart operations; local persistent state is limited to reading/writing supplied file descriptors.

Dependencies/integration: depends on libcurl, `S3fsCurlShare` for DNS/SSL-session sharing, `curl_util` for sorted header lists and URL/canonicalization helpers, `s3fs_auth` for hashes/HMACs, `S3fsCred` for credentials and bucket name, `s3fs_util`/`string_util` for path/date/encoding helpers, `AdditionalHeader` for configured extra headers, `s3fs_xml` for parsing S3 XML errors and multipart IDs, and globals/counters from `common.h`.

Request/error behavior: `RequestPerform` treats 2xx as success; parses XML `<Code>` for `EntityTooLarge`, `InvalidObjectState`, and `KeyTooLongError`; maps common HTTP errors to errno (`400` HEAD to `EPERM` or long-name `ENAMETOOLONG`, `403` to `EPERM`, `404` to `ENOENT`, `429/503` to retry then `EAGAIN`, `500` to retry then `EIO`, `502` to retry then `EWOULDBLOCK`, `504` to retry then `ETIMEDOUT`). Curl communication failures generally sleep and retry. PUT/copy requests also inspect a 200 response body for XML errors via `MapPutErrorResponse`.

Multipart flow: initiate upload sends `POST ?uploads` and parses `UploadId`. Part setup handles either file uploads with `UploadReadCallback` and optional part MD5/ETag verification, or server-side copy parts with `x-amz-copy-source` and XML ETag parsing. Completion posts a generated `CompleteMultipartUpload` XML document. Abort sends `DELETE ?uploadId=...`. Query `uploadId` is URL encoded for S3-compatible services that return characters needing escaping.

Risks: large synchronous payload hashing for Signature V4 can add latency before upload, especially multipart when unsigned payloads are disabled. `WaitBeforeRetry` uses exponential backoff without an upper cap and depends on `random()` global state. Many request methods return early after curl setup failures without always clearing partially allocated headers/handle state until destruction or later cleanup. Header matching is case-sensitive in `MultipartUploadContentPartComplete` (`ETag`) while callbacks preserve non-`x-amz` header case from the server, so lowercase `etag` responses from compatible services could fail. `SetProxy` appears to invert the `proxy_http` flag for `"http://"` input, which could skip proxy credentials for HTTP proxies and merits review. `extractURI` always appends a trailing slash, which may affect path-style signing with non-root service paths. Global configuration is mutable and mostly unsynchronized after initialization.

Test signals: integration tests should cover Signature V4 and V2 canonicalization, public bucket unsigned behavior, requester-pays, SSE-S3/SSE-C/SSE-KMS headers and validation, IAM metadata/IAMv2 flows without auth-header deadlock, proxy and client certificate options, MIME detection, HEAD fallback through SSE-C keys, range GET writes and XML error buffering, PUT with zero-byte and file bodies, 200-with-error-body copy handling, multipart upload/copy/complete/abort, retry handling for 429/5xx and curl transient failures, CA bundle fallback, and S3-compatible services with unusual ETag casing or upload IDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl.h -->
# Research: sources/user-network-fs/s3fs-fuse/src/curl.h

Purpose: public and private interface for `S3fsCurl`, the libcurl-backed S3 transport wrapper. It exposes configuration knobs, request methods, response accessors, and compatibility shims for libcurl options that may be absent at compile time.

Important APIs/types: defines `curlprogress`, `CurlUniquePtr`, `s3fscurl_lazy_setup`, `sseckeymap_t`, and `sseckeylist_t`. The private `REQTYPE` enum class classifies every request flavor for signing, retry reconstruction, and setup logic. Static setters/getters control certificate checking, timeouts, retries, public bucket mode, ACL, storage class, SSE, content MD5, verbose/debug body, hostname verification, SSL client certs, multipart sizes, signature mode, unsigned payload, user agent, ListObjectsV2, requester pays, proxy, and IP resolution. Public methods implement IAM, object, bucket, and multipart operations.

Control flow surface: callers initialize global curl and credentials once, then construct `S3fsCurl` objects for request batches. Per-request methods populate internal fields and either perform immediately or expose pre-setup/lazy setup for parallel multipart workers. `RequestPerform` is the common execution path. Response data is retrieved through `GetResponseCode`, `GetCurlErrorString`, `GetResponseHeaders`, `GetBodyData`, `GetHeadData`, and related accessors.

State and persistence: declares extensive static process-wide configuration and per-instance request state. The handle is stored as `CurlUniquePtr` protected by `curl_handles_lock`; `curl_progress` maps raw handles to timeout progress records. Per-request members retain raw `curl_slist*` headers and raw pointers into strings or file buffers for upload bodies, so object lifetime and retry backup fields matter. Remote persistence occurs only when implementation request methods hit S3.

Dependencies/integration: includes libcurl, `common.h`, `metaheader.h`, `s3fs_util.h`, and `types.h`. Forward-declares `S3fsCred` to avoid exposing credential implementation. Compatibility macros map newer libcurl options to numeric placeholders so older build environments can compile and fail gracefully at runtime.

Risks: the class mixes global configuration, low-level handle management, signing, and high-level S3 operations, so changes can have broad blast radius. Static mutable state is not generally synchronized except curl handle/progress tracking. Raw `curl_slist*` ownership is manual and must be cleared on all paths. The lazy setup function pointer is powerful but requires each setup method to leave the object in a complete, retryable state.

Test signals: compile against older and newer libcurl headers to exercise compatibility macros. API-level tests should validate each setter/getter old-value behavior, initialization failure paths, per-request type transitions, header cleanup after repeated requests on one object, and lazy multipart setup followed by `RequestPerform`/completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl_share.cpp -->
# Research: sources/user-network-fs/s3fs-fuse/src/curl_share.cpp

Purpose: implements per-thread libcurl share handles so S3fsCurl instances can share DNS cache and SSL session cache within a thread while using explicit locks required by libcurl's share API.

Important APIs: `SetDnsCache` and `SetSslSessionCache` toggle which share data types are enabled. `SetCurlShareHandle(CURL*)` obtains or creates the current thread's `CURLSH` and attaches it to an easy handle. `DestroyCurlShareHandleForThread` removes the current thread's share handle and associated locks. Internal callbacks `LockCurlShare` and `UnlockCurlShare` lock DNS or SSL-session mutexes based on `curl_lock_data`.

Control flow: `SetCurlShareHandle` constructs a temporary `S3fsCurlShare`, asks it for a handle tied to `std::this_thread::get_id()`, and sets `CURLOPT_SHARE`. `GetCurlShareHandle` returns an existing per-thread handle from static maps or creates a new `curl_share_init` handle plus lock bundle, initializes lock/unlock/userdata callbacks, enables requested share data, stores both in maps, and returns the raw handle. Initialization tolerates libcurl builds that lack DNS or SSL session sharing by warning and continuing for those options.

State and persistence: static booleans control DNS and SSL cache sharing. Static maps store one `CurlSharePtr` and one `ShareLocksPtr` per thread id, protected by `curl_share_lock`. State is process-local and persists until explicitly destroyed for the thread or process exit.

Dependencies/integration: used by `S3fsCurl::ResetHandle` during handle setup. Depends on libcurl share APIs and `s3fs_logger.h`. The per-thread design avoids sharing the same `CURLSH` across unrelated FUSE threads while still allowing multiple easy handles in one thread to reuse DNS/TLS data.

Risks: cleanup requires `DestroyCurlShareHandleForThread`; otherwise maps can retain entries for dead thread ids in long-running thread-pool churn. Lock callbacks assume `useptr` is a valid `curl_share_locks` for the share lifetime. Only DNS and SSL-session lock data are handled; if future share types are enabled, callbacks must be extended. The temporary object pattern hides the fact that state is static and keyed by thread id.

Test signals: tests should enable/disable DNS and SSL sharing, attach share handles to multiple easy handles in the same thread and different threads, destroy per-thread handles, and simulate libcurl returning `CURLSHE_BAD_OPTION`/`CURLSHE_NOT_BUILT_IN`. Threaded tests should verify no map races under concurrent handle creation and teardown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl_share.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl_share.h -->
# Research: sources/user-network-fs/s3fs-fuse/src/curl_share.h

Purpose: declares the `S3fsCurlShare` helper that manages libcurl `CURLSH` share handles and their lock bundles for DNS and SSL session reuse.

Important APIs/types: `curl_share_locks` contains separate mutexes for DNS and SSL session data. `CurlSharePtr` and `ShareLocksPtr` are unique pointers with libcurl cleanup semantics. `S3fsCurlShare` exposes static toggles `SetDnsCache`, `SetSslSessionCache`, `SetCurlShareHandle`, and `DestroyCurlShareHandleForThread`.

Control flow surface: external code never directly owns `S3fsCurlShare` state. `SetCurlShareHandle` creates a short-lived object to use the current thread id, then private methods create/find the thread's persistent share handle. Private callbacks satisfy libcurl's lock/unlock contract and `InitializeCurlShare` wires callbacks/userdata/share types.

State and persistence: declares static process-wide maps from `std::thread::id` to share handles and lock structures, protected by `curl_share_lock`. Each object instance stores only the current thread id. State is in-memory and should be cleaned when a worker thread is done.

Dependencies/integration: includes libcurl, STL map/memory/mutex/thread, and `common.h` for lock annotations. Integrated by `S3fsCurl::ResetHandle` to set `CURLOPT_SHARE` on each easy handle.

Risks: map lifetime and thread-id reuse need care if worker threads are short-lived. The `NO_THREAD_SAFETY_ANALYSIS` callbacks bypass clang checking because libcurl controls the call boundary. If libcurl invokes callbacks after cleanup due to misuse, `useptr` would dangle.

Test signals: compile with clang annotations, verify one share handle per thread, verify cleanup removes both maps, and run a multithreaded smoke test using easy handles with DNS/SSL sharing enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl_share.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl_util.cpp -->
# Research: sources/user-network-fs/s3fs-fuse/src/curl_util.cpp

Purpose: utility implementation for S3/libcurl request construction: sorted header-list manipulation, AWS canonical-header formatting, bucket URL transformation, host extraction, MD5 helper, curl debug labels, and ETag comparison.

Important APIs: `curl_slist_sort_insert` inserts or replaces a header in case-insensitive sorted order; `curl_slist_remove` deletes matching headers; `get_sorted_header_keys`, `get_header_value`, and `get_canonical_headers` support Signature V2/V4 signing; `MakeUrlResource` builds encoded S3 resource paths and base URLs; `prepare_url` converts service-path URL form into virtual-hosted or path-style request URLs; `make_md5_from_binary` computes base64 MD5; `url_to_host` and `get_bucket_host` support host headers; `getCurlDebugHead` labels curl debug traffic; `etag_equals` compares quoted/unquoted ETags case-insensitively.

Control flow: header insertion trims key/value, allocates a new `curl_slist` node with `malloc`, walks the sorted list, replaces on equal key, or inserts before the first greater key. Canonicalization walks the sorted list, drops empty-value headers because libcurl discards them, lowercases keys, trims values, and optionally filters to `x-amz` headers. URL construction encodes `service_path + bucket + realpath`, appends it to `s3host`, then `prepare_url` rewrites into either `bucket.host/path` virtual-hosted style or `host/bucket/path` path-request style. Host extraction requires `http://` or `https://` and aborts on invalid schemes.

State and persistence: no owned persistent state. Functions read global configuration (`service_path`, `s3host`, `pathrequeststyle`) and bucket name from `S3fsCred`. Header functions allocate/finalize memory in libcurl-compatible lists that callers must free with `curl_slist_free_all`.

Dependencies/integration: used heavily by `curl.cpp` signing and request setup. Depends on libcurl slist structures, `s3fs_auth` for MD5, `S3fsCred` for bucket, `string_util` for trim/lower/url encode/peeloff helpers, and logger macros. Also declares integration points implemented elsewhere (`get_object_sse_type`, `put_headers`) in the header.

Risks: `curl_slist_sort_insert` builds `strnew` from the original `key` expression rather than the trimmed `strkey`, so leading/trailing spaces in key arguments could be retained in the stored header while sorting uses the trimmed key. Manual allocation must exactly match libcurl's free behavior; replacement frees `data` correctly, but callers must not mix with ownership outside libcurl conventions. `prepare_url` assumes the bucket token exists in `url_str`; malformed input could produce surprising substr ranges. `url_to_host` aborts the process for invalid schemes, which is harsh for configuration errors.

Test signals: unit tests should cover sorted insertion/replacement/removal, empty-header omission in signed header lists, V2 `only_amz` canonicalization, host/path style URL rewrites with service paths and encoded object names, invalid URL scheme behavior, MD5 base64 from binary data, quoted/unquoted ETag comparison, and compatibility with `curl_slist_free_all`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl_util.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl_util.h -->
# Research: sources/user-network-fs/s3fs-fuse/src/curl_util.h

Purpose: declares curl/S3 request utility functions shared by `curl.cpp` and other s3fs modules. It keeps header-list, canonicalization, URL, host, SSE-header lookup, and ETag helper prototypes out of the large transport class.

Important APIs: exposes `curl_slist_sort_insert`, `curl_slist_remove`, `get_sorted_header_keys`, `get_canonical_headers`, `get_header_value`, `MakeUrlResource`, `prepare_url`, `get_object_sse_type`, `put_headers`, `make_md5_from_binary`, `url_to_host`, `get_bucket_host`, `getCurlDebugHead`, and `etag_equals`. Forward declares `sse_type_t` and includes `metaheader.h` for `headers_t`.

Control flow surface: consumers use these helpers before signing and sending requests. `get_object_sse_type` and `put_headers` are declared here but implemented in `s3fs.cpp`, making this header part of a broader integration contract between transport utilities and filesystem/object metadata logic.

State and persistence: functions are mostly stateless by contract, but URL/host helpers read global s3fs configuration and bucket state. Header-list helpers mutate and return `curl_slist*` chains that callers own.

Dependencies/integration: includes libcurl for `curl_slist` and `curl_infotype`, C++ strings, and `metaheader.h`. `curl.cpp` depends on these declarations for signing and request setup; filesystem code can call the externally implemented SSE/header helpers without including the transport implementation.

Risks: this header exposes raw libcurl list ownership, so misuse can leak or double-free headers. Cross-file declarations for functions implemented in `s3fs.cpp` create coupling that can be missed by isolated tests of the curl module. `sse_type_t` is only forward declared, so callers needing enum values must include the defining header as well.

Test signals: compile/link tests should ensure `s3fs.cpp` provides `get_object_sse_type` and `put_headers`. Unit tests for the implementation should be paired with ownership/leak checks around the raw `curl_slist*` helpers and URL helpers under both virtual-hosted and path-request styles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl_util.h -->
