# subset-b-006987 RGW CORS, crypto, REST, data access, dmclock, and env research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cors.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_cors.cc

## Purpose
Implements the shared RGW CORS rule/configuration model used by S3 and Swift frontends. It serializes CORS state, builds rules from delimited header values, matches origins and headers including simple wildcard patterns, formats response headers, and removes origin-specific rules.

## Important APIs, types, and functions
`RGWCORSRule::create_rule()` validates origin/header names, parses method flags, optional exposed headers, and `MaxAgeSeconds`. `lowercase_http_attr()` normalizes HTTP header names for case-insensitive matching. `is_string_in_set()` implements exact, global wildcard, prefix wildcard, suffix wildcard, and single embedded wildcard matching. `is_header_allowed()`, `is_origin_present()`, `has_wildcard_origin()`, and `format_exp_headers()` are the runtime checks. `RGWCORSConfiguration::host_name_rule()` selects the first matching rule.

## Control flow
Admin/update paths construct rules, persist them via `encode()`, and later RGW request handling scans rules in list order for a matching origin and method/header set. Header matching lazily builds a lowercase cache from `allowed_hdrs` on first use.

## State and persistence
State lives in `RGWCORSRule` fields and `RGWCORSConfiguration::rules`, encoded into Ceph `bufferlist`s. `lowercase_allowed_hdrs` is derived cache only; changing `allowed_hdrs` requires discarding it.

## Dependencies and integration points
Uses Ceph encode/decode, `Formatter`, JSON helpers, debug logging, `for_each_substr()`, `get_str_list()`, and Boost string helpers. S3 XML and Swift adapters reuse this core.

## Risks and test signals
Risks include wildcard overmatching, empty or malformed delimiter input, stale lowercase cache, and response-header injection. Tests should cover exact/wildcard origin and header matches, invalid multiple `*`, newline escaping in exposed headers, encode/decode round trips, and deletion of the last origin in a rule.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cors.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cors.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_cors.h

## Purpose
Declares the common CORS data model, method bit flags, validation helpers, and serialization contract used by RGW bucket CORS configuration.

## Important APIs, types, and functions
`RGWCORSRule` owns max age, allowed method flags, optional id, allowed headers, allowed origins, and exposed headers. It exposes rule construction, matching, formatting, dumping, and encode/decode. `RGWCORSConfiguration` owns a list of rules and provides lookup, origin-list extraction, deletion, dumping, and `stack_rule()` insertion. `validate_name_string()` rejects empty names and names with more than one wildcard. `get_cors_method_flags()` maps one method string, while `get_multi_cors_method_flags()` parses a delimited list.

## Control flow
Callers parse protocol-specific configuration into `RGWCORSRule` instances, push them into `RGWCORSConfiguration`, persist the config as encoded attrs, then consult the list during preflight and actual request handling.

## State and persistence
The header defines versioned `ENCODE_START`/`DECODE_START` layouts for both rule and configuration, making this file part of the bucket metadata compatibility surface.

## Dependencies and integration points
Depends on Ceph `bufferlist` encoding, `include/types.h`, string-list splitting, and protocol adapters such as `rgw_cors_s3.*` and `rgw_cors_swift.h`.

## Risks and test signals
Because method flags are `uint8_t`, future methods must fit the bitset. Tests should validate method parsing delimiters, unsupported method behavior, encode compatibility, wildcard validation, and mutable-header-cache behavior noted by the class comment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cors_s3.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_cors_s3.cc

## Purpose
Implements S3 XML parsing and rendering for RGW CORS configuration, translating AWS-style XML elements into the shared `RGWCORSRule` model.

## Important APIs, types, and functions
`RGWCORSRule_S3::to_xml()` emits `CORSRule`, optional `ID`, method entries, origins, allowed headers, max age, and exposed headers. `RGWCORSRule_S3::xml_end()` validates and consumes child XML objects, enforcing allowed method names, id length <= 255, at least one origin, valid wildcard names, and numeric `MaxAgeSeconds`. `RGWCORSConfiguration_S3::xml_end()` requires at least one `CORSRule`. `RGWCORSXMLParser_S3::alloc_obj()` maps XML tags to parser objects.

## Control flow
The XML parser allocates typed objects per element. On close of a `CORSRule`, child element data is folded into the inherited rule fields. On close of `CORSConfiguration`, rule objects are copied into the configuration list. Rendering walks persisted rules and emits AWS XML.

## State and persistence
This file does not persist directly; it materializes the shared CORS state that `rgw_cors.h` encodes elsewhere.

## Dependencies and integration points
Uses `RGWXMLParser`, `XMLObj`, `XMLFormatter`, S3 XML namespace constants, and RGW debug prefix logging.

## Risks and test signals
Risks include case-insensitive method parsing differences, missing origin rejection, integer overflow mapping to invalid max-age sentinel, and static casts from base rules to S3-derived rules during XML output. Tests should include invalid methods, long IDs, malformed max age, wildcard names, multi-rule configs, and XML round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cors_s3.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cors_s3.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_cors_s3.h

## Purpose
Declares S3-specific XML adapters around the shared CORS model.

## Important APIs, types, and functions
`RGWCORSRule_S3` inherits `RGWCORSRule` and `XMLObj`, adding XML close-time parsing and `to_xml()`. `RGWCORSConfiguration_S3` inherits `RGWCORSConfiguration` and `XMLObj`, adding configuration-level XML parsing and stream output. `RGWCORSXMLParser_S3` subclasses `RGWXMLParser` and owns `DoutPrefixProvider`/`CephContext` pointers for logging and parser allocation.

## Control flow
Protocol code instantiates `RGWCORSXMLParser_S3`, parses request XML into `RGWCORSConfiguration_S3`, then stores the inherited common configuration. GET CORS paths call `to_xml()`.

## State and persistence
State is inherited from `RGWCORSRule` and `RGWCORSConfiguration`; the S3 classes add only logging/context pointers.

## Dependencies and integration points
This header binds `rgw_xml.h`, `common/XMLFormatter.h`, `common/dout.h`, and `rgw_cors.h`. It is the S3-facing bridge for bucket CORS handlers.

## Risks and test signals
The derived objects are copied into base-rule lists, so output paths assume stored rules can be safely treated as `RGWCORSRule_S3`. Tests should cover parser allocation for every supported tag and S3 output from parsed and persisted rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cors_s3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cors_swift.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_cors_swift.h

## Purpose
Provides the Swift-facing CORS configuration adapter for RGW.

## Important APIs, types, and functions
`RGWCORSConfiguration_SWIFT` inherits `RGWCORSConfiguration` and exposes `create_update()`. It calls `RGWCORSRule::create_rule()` with `allowed_methods="*"`, then pushes the resulting rule to the front of the rule list.

## Control flow
Swift metadata update paths provide allow-origins, allow-headers, expose-headers, and max-age strings. The adapter validates and converts them into a common CORS rule. A failed conversion returns `-EINVAL`; success stacks the rule before older rules.

## State and persistence
No Swift-only state is stored. The created `RGWCORSRule` is persisted through the shared CORS configuration encoding.

## Dependencies and integration points
Includes shared CORS and Ceph string-list helpers. It is intentionally header-only because the adapter is a small wrapper.

## Risks and test signals
Since Swift grants all RGW CORS methods when CORS metadata is valid, tests should confirm this is intended for Swift semantics. Cover invalid origin/header strings, omitted optional headers, max-age parsing, and rule ordering after repeated updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cors_swift.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cr_rest.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_cr_rest.cc

## Purpose
Implements coroutine helpers for streaming REST resources between RGW components over HTTP, including read backpressure, write backpressure, request lifetime cleanup, and stream splicing.

## Important APIs, types, and functions
`RGWCRHTTPGetDataCB` buffers received body data and optional prepended metadata. `RGWStreamReadHTTPResourceCRF::init/read/decode_rest_obj()` drives async HTTP reads and extracts headers/extra data. `RGWStreamWriteHTTPResourceCRF::send/write/drain_writes()` sends headers and body chunks while honoring pending-write limits. `RGWStreamSpliceCR::operate()` connects a read resource to a write resource.

## Control flow
Read setup registers a receive callback, sends the request, then `read()` yields until data or completion events arrive. Write setup sends a request, `write()` yields when pending sends exceed the window, and `drain_writes()` finalizes the stream and handles response headers. Splice initializes the input, waits for attrs before sending output headers, copies chunks, then drains writes.

## State and persistence
State is transient coroutine state: request pointers, callback buffers, timers/IO ids, buffered data, flags for attrs/extra data, pending write state, and total bytes read. No durable storage is modified.

## Dependencies and integration points
Depends on RGW coroutine environment, HTTP manager/request classes, Boost.Asio stackless coroutine macros, and `bufferlist`.

## Risks and test signals
Risks include request cancellation ordering, callback locking, pause/unpause thresholds, extra-data framing, empty reads before EOF, and write drain races. Tests should simulate slow readers/writers, cancellation, HTTP errors, extra metadata decoding, and large stream splices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cr_rest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cr_rest.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_cr_rest.h

## Purpose
Declares coroutine wrappers for REST read, write, delete, and bidirectional streaming operations used by RGW cloud/remote resource flows.

## Important APIs, types, and functions
`rgw_rest_obj` carries object key, length, attrs, custom attrs, and ACLs. `RGWReadRawRESTResourceCR` and `RGWReadRESTResourceCR<T>` wrap async HTTP GET/read operations. `RGWSendRawRESTResourceCR<T,E>`, `RGWSendRESTResourceCR<S,T,E>`, `RGWPostRESTResourceCR`, `RGWPutRESTResourceCR`, `RGWPutRawRESTResourceCR`, `RGWPostRawRESTResourceCR`, and `RGWDeleteRESTResourceCR` wrap send verbs. `RGWStreamReadResourceCRF` and `RGWStreamWriteResourceCRF` define streaming interfaces, with HTTP implementations and `RGWStreamSpliceCR`.

## Control flow
Simple coroutine classes create an HTTP operation in `send_request()`, wait in `request_complete()`, and release intrusive references in cleanup/destructors. Streaming classes expose reentrant `read()`, `write()`, and drain methods for composed coroutines.

## State and persistence
All state is request-local: connection pointers, method/path/params, headers, attrs, input buffers, result pointers, request refs, range/multipart settings, and callback buffers.

## Dependencies and integration points
Integrates `RGWSimpleCoroutine`, `RGWCoroutine`, `RGWRESTConn`, `RGWREST*Resource`, `RGWHTTPManager`, `RGWHTTPStreamRWRequest`, Boost.Asio, and JSON formatting for typed sends.

## Risks and test signals
Manual `put()`/intrusive pointer ownership is a key risk. Tests should validate send failure cleanup, null result paths, error-result decoding, DELETE behavior, range setup, multipart writes, cancellation destructors, and streaming backpressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cr_rest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_crc_digest.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_crc_digest.h

## Purpose
Provides small digest wrappers for RGW checksum calculation: CRC32, CRC32C, and NVMe CRC64.

## Important APIs, types, and functions
`rgw::digest::byteswap()` is a constexpr C++23-style byte swap. `Crc32` uses `boost::crc_optimal` for IEEE CRC32 and reports a 4-byte digest. `Crc32c` uses Ceph's hardware-specialized `ceph_crc32c()` with standard initial/final xor. `Crc64Nvme` uses SPDK `spdk_crc64_nvme()` and reports an 8-byte digest. Each type exposes `Restart()`, `Update()`, `Final()`, and `digest_size`.

## Control flow
Callers instantiate a digest, feed chunks with `Update()`, and copy the final big-endian byte representation into the output buffer via `Final()`.

## State and persistence
State is only the current CRC accumulator. No persistence occurs, but output byte ordering affects persisted/user-visible checksum metadata.

## Dependencies and integration points
Depends on Boost CRC, Ceph CRC32C, SPDK CRC64, C++20 endian/bit utilities, and standard `memcpy`.

## Risks and test signals
Endian handling is explicitly called out by comments, especially for CRC64/NVMe and ARM/big-endian platforms. Tests should compare against AWS/S3 checksum vectors, incremental update equivalence, restart behavior, zero-length input, and big-endian builds or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_crc_digest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_crypt.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_crypt.cc

## Purpose
Implements RGW server-side encryption for PUT/POST/GET/COPY paths, including legacy AES-256-CBC, AES-256-GCM AEAD, KMS/SSE-S3/SSE-C request processing, crypto context canonicalization, object/range filters, and bucket-key management.

## Important APIs, types, and functions
`make_canonical_context()` normalizes KMS encryption context JSON with ICU NFC normalization, deterministic key ordering, and injected object ARN. `AES_256_CBC` implements 4 KiB chunked CBC with offset-derived IVs and partial-block xor handling. `AES_256_GCM` implements 4 KiB AEAD chunks, 16-byte tags, part-number/chunk-index IV layout, chunk-index AAD, accelerator fallback, random salt, HMAC-derived object keys, and per-part keys. `RGWGetObj_BlockDecrypt` maps requested plaintext ranges to encrypted ranges and decrypts cached chunks, including multipart part boundaries. `RGWPutObj_BlockEncrypt` encrypts streaming PUT data and tracks expanded encrypted offsets. `rgw_s3_prepare_encrypt()` and `rgw_s3_prepare_decrypt()` validate headers, retrieve/derive keys, set response headers, and write/read encryption attrs. `rgw_get_aead_original_size()` and `rgw_get_aead_decrypted_size()` support size accounting. `rgw_remove_sse_s3_bucket_key()` cleans bucket KEKs when safe.

## Control flow
Encryption preparation first handles SSE-C, then SSE-KMS, then SSE-S3, then default RGW auto encryption. Each branch validates required headers/config, obtains or derives a 256-bit key, chooses CBC or GCM from `rgw_crypt_sse_algorithm`, writes mode/key metadata attrs, and optionally returns a configured `BlockCrypt`. PUT data then flows through `RGWPutObj_BlockEncrypt`, which buffers to block boundaries and flushes the final partial block. Decryption preparation reads `RGW_ATTR_CRYPT_MODE`, validates request headers for SSE-C, reconstitutes KMS/SSE-S3 keys or default keys, reconstructs GCM salt and identity, and returns a decryptor. GET range fixup projects plaintext/compressed ranges to encrypted chunk reads before decryption.

## State and persistence
Persistent state is object/bucket metadata: `RGW_ATTR_CRYPT_MODE`, key id/selector/context/key MD5, salt, original size, crypt parts, prefetch alignment, and bucket encryption key id. GCM ciphertext stores an auth tag per encrypted chunk, so encrypted object size differs from plaintext size. Sensitive in-memory keys are zeroized in destructors and after use where practical.

## Dependencies and integration points
Uses OpenSSL EVP, Ceph crypto/HMAC/MD5/base64, crypto accelerator plugins, RGW KMS helpers, object manifests, range projection, SAL request state, compression filters, bucket attrs, ICU, RapidJSON, and RGW request/environment abstractions.

## Risks and test signals
This is security-critical. Risks include GCM range projection errors, wrong copy-source identity during key derivation, multipart part-number mapping, malformed or missing salt/original-size attrs, accelerator/authentication failure handling, integer overflow in expanded sizes, logging of sensitive material, and compatibility with legacy CBC attrs. Tests should cover SSE-C/KMS/SSE-S3/auto CBC and GCM, multipart non-contiguous part numbers, GET ranges across chunk and part boundaries, copy-object decrypt/re-encrypt, compression plus encryption, KMS context canonicalization, auth tag corruption, wrong key/object identity failures, bucket key create/remove races, and size accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_crypt.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_crypt.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_crypt.h

## Purpose
Declares RGW encryption interfaces, AEAD geometry helpers, encryption/decryption filters, S3 preparation functions, and small attr helpers.

## Important APIs, types, and functions
`BlockCrypt` is the polymorphic block cipher interface with plaintext and encrypted block sizes, `encrypt()`, `decrypt()`, and optional part-number selection. Constants define AES-256 key size and GCM salt/IV/tag/chunk sizes. `is_aead_mode()`, `is_cbc_mode()`, and AEAD size/offset helpers define shared geometry. `RGWGetObj_BlockDecrypt` is a GET filter that fixes ranges, decrypts data, handles multipart part lengths/numbers, and exposes plaintext size conversion. `RGWPutObj_BlockEncrypt` is a PUT data processor. `rgw_s3_prepare_encrypt()` and `rgw_s3_prepare_decrypt()` are the main S3 integration APIs.

## Control flow
Operation handlers call prepare functions to populate attrs and obtain a `BlockCrypt`, then insert PUT/GET filters around the normal object data pipeline. Helpers keep range and content-length logic consistent for size-expanding AEAD modes.

## State and persistence
The header defines attr-facing size behavior but not the attrs themselves. It captures decrypt filter state for offsets, caches, multipart lengths, part numbers, encrypted total size, and compression presence.

## Dependencies and integration points
Depends on RGW op/rest/put object APIs, SAL data processors, Ceph yields, and Ceph `bufferlist`. It is consumed by S3 operations, copy paths, object writes, and object reads.

## Risks and test signals
Incorrect geometry helpers will affect range reads, object size, bucket index, quotas, and cls prefetch. Tests should exercise all AEAD helper edge cases, zero-sized objects, malformed encrypted remainders, compression interaction, multipart fallback behavior, and `BlockCrypt` implementations with equal and expanded block sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_crypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_crypt_sanitize.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_crypt_sanitize.cc

## Purpose
Implements stream insertion wrappers that suppress SSE-C customer keys in logs when `rgw_crypt_suppress_logs` is enabled.

## Important APIs, types, and functions
Overloaded `operator<<` functions handle `env`, `x_meta_map`, `s3_policy`, `auth`, and `log_content`. They compare environment/header/policy field names against SSE-C key and copy-source-key names and print a fixed suppression message instead of the original value.

## Control flow
Logging code wraps potentially sensitive values in the appropriate type. The operator checks the global config flag and either writes `=suppressed due to key presence=` or forwards the raw value.

## State and persistence
No state is persisted. The only state read is global config and request environment contents.

## Dependencies and integration points
Depends on `rgw_common.h`, request state, global Ceph context, and Boost case-insensitive/eager substring predicates. It integrates with request logging, environment dumps, S3 POST policy logs, and civetweb-originated content logs.

## Risks and test signals
Risks include missing a header variant, suppressing only when exact wrappers are used, global-context access during early logging, and query-string substring false positives/negatives. Tests should cover every wrapper, case-insensitive names, copy-source key names, disabled suppression, query-string detection, and auth logs when key env vars exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_crypt_sanitize.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_crypt_sanitize.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_crypt_sanitize.h

## Purpose
Declares lightweight wrapper types for redacting encryption customer keys from RGW logs.

## Important APIs, types, and functions
`rgw::crypt_sanitize::env`, `x_meta_map`, `s3_policy`, `auth`, and `log_content` each capture the context needed to decide whether an output value may contain an SSE-C key. The header declares insertion operators for each wrapper.

## Control flow
Callers construct wrappers inline in log statements. The implementation decides whether to write the sensitive value or a suppression marker.

## State and persistence
Wrappers hold string views or request pointers only for the duration of the log expression. Nothing is persisted.

## Dependencies and integration points
Includes `rgw_common.h` for `req_state`. This is a small interface consumed by RGW request parsing and logging code that handles environment variables, metadata maps, S3 policy variables, auth strings, and raw logs.

## Risks and test signals
Because values are mostly `string_view`, caller lifetime must outlive streaming. Tests should ensure wrappers do not outlive temporaries, all sensitive field names are handled, non-sensitive values still print, and the config flag gates behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_crypt_sanitize.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_d3n_cacherequest.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_d3n_cacherequest.h

## Purpose
Defines D3N L1 cache read support for RGW object reads backed by local files and POSIX AIO.

## Important APIs, types, and functions
`D3nGetObjData` provides a mutex container. `D3nL1CacheRequest::AsyncFileReadOp` owns an `aiocb`, result buffer, and Ceph async completion. `init_async_read()` opens the cache file, applies configured `posix_fadvise`, allocates a buffer, and initializes `aio_read` state. `libaio_cb_aio_dispatch()` converts POSIX callback completion into Ceph async dispatch. `async_read()` exposes a Boost.Asio initiation function. `generate_oid_digest()` maps object ids to XXH3 128-bit hex filenames. `file_aio_read_abstract()` submits the cache read and returns results through RGW AIO throttling.

## Control flow
The cache path hashes the object oid, opens the file under the cache location, submits `aio_read()`, and later dispatches the completion to a handler that fills `rgw::AioResult` and returns it to the throttle.

## State and persistence
Persistent state is external cache files. In-memory state includes file descriptor ownership, result buffer, and completion pointer.

## Dependencies and integration points
Uses POSIX AIO, Boost.Asio, Ceph async completions, RGW AIO, RGW cache logging, `xxhash`, and global RGW D3N configuration.

## Risks and test signals
Risks include file descriptor cleanup, negative errno conversion, callback ownership after `release()`, partial reads, cache-file naming collisions, and portability of POSIX AIO. Tests should cover cache hit/miss, open/read errors, fadvise modes, concurrent reads, cancellation/lifetime, and digest stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_d3n_cacherequest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_data_access.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_data_access.cc

## Purpose
Implements a small SAL-backed data access helper for loading buckets and writing complete objects with ACL, compression, etag, and atomic-writer handling.

## Important APIs, types, and functions
`RGWEtag` computes hex etags, with MD5 marked non-FIPS cryptographic use. `RGWDataAccess::Bucket::init()` loads bucket info and attrs through SAL or accepts preloaded metadata. `finish_init()` decodes bucket ACL attrs. `Bucket::get_object()` creates an object wrapper. `Object::put()` creates an atomic writer, optionally wraps compression, streams data in `rgw_max_chunk_size` pieces, computes/sets etag and ACL attrs, then completes the write.

## Control flow
A caller obtains a bucket, gets an object wrapper, configures metadata setters, and calls `put()`. The write path prepares the atomic writer, pushes data through optional compression and writer filters, flushes with an empty buffer, fills missing etag/ACL attrs, and calls `complete()` with object size, mtime, attrs, delete-at, user data, no checksum, and log-op flag.

## State and persistence
Persistent effects are object data, object attrs including etag/ACL, version instance generation, bucket index/log updates through SAL writer completion, and optional compression-transformed storage.

## Dependencies and integration points
Depends on SAL driver/bucket/object/writer, RGW ACL, compression plugins, AIO throttle config, checksum API, request context, and Ceph `bufferlist`.

## Risks and test signals
Risks include modifying caller data/attrs, compression plugin load failures, etag differences when caller supplies etag, versioned instance generation, ACL defaults, and completion failure after data streaming. Tests should cover preloaded buckets, ACL decode errors, compressed/uncompressed writes, supplied etag, default ACL, versioning, delete-at/user-data fields, and writer prepare/process/complete failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_data_access.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_data_access.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_data_access.h

## Purpose
Declares `RGWDataAccess`, a compact abstraction for bucket lookup and object PUT operations using RGW SAL.

## Important APIs, types, and functions
`RGWDataAccess` stores a `rgw::sal::Driver*`. `Bucket` stores bucket info, tenant/name/id, mtime, attrs, and ACL policy, and exposes `get_object()`. `Object` stores bucket reference, object key, mtime, etag, OLH epoch, delete-at, user data, and optional ACL buffer. It exposes `put()` plus setters for metadata and policy. Two `get_bucket()` overloads support loading by names or using existing bucket info/attrs.

## Control flow
Callers construct `RGWDataAccess`, acquire a `BucketRef`, create an `ObjectRef`, set optional metadata, and write object data. Bucket initialization decodes ACL before object writes need an owner.

## State and persistence
The header describes in-memory handles that lead to persistent writes in the implementation. Shared pointers keep bucket state alive for objects.

## Dependencies and integration points
Depends on RGW common types, SAL forward declarations, ACL policy, Ceph times, `bufferlist`, and optional yield.

## Risks and test signals
The interface relies on a non-owning driver pointer and private constructors. Tests should check lifetime assumptions, bucket ACL availability, object metadata setter propagation, and both bucket initialization paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_data_access.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_dencoder.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_dencoder.cc

## Purpose
Registers RGW encode/decode test instances for selected types used by Ceph's dencoder tooling.

## Important APIs, types, and functions
`obj_version::generate_test_instances()` returns a populated version/tag and an empty instance. `RGWBucketEncryptionConfig::generate_test_instances()` returns KMS with bucket key enabled, AES256, and default instances.

## Control flow
Dencoder tests call these static generators to produce representative values for encode/decode round-trip verification.

## State and persistence
No runtime state is persisted here. The file supports persistence compatibility by supplying test samples for encoded classes.

## Dependencies and integration points
Includes many RGW type headers so dencoder can instantiate encoders. The current concrete functions relate to object versions and bucket encryption config.

## Risks and test signals
The sample set is intentionally small. Risks are missing coverage for newer encoded fields or edge values. Tests should ensure these generated instances round-trip and should add samples when `RGWBucketEncryptionConfig` or `obj_version` encoding evolves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_dencoder.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_dmclock.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_dmclock.h

## Purpose
Defines RGW dmClock scheduling basics: client classes, imported dmClock types, scheduler selection enum, and config-based scheduler type lookup.

## Important APIs, types, and functions
`client_id` classifies RGW traffic as `admin`, `auth`, `data`, or `metadata`. `Cost` and `ClientInfo` alias crimson dmClock types. `scheduler_t` distinguishes no scheduler, simple throttler, and dmClock. `get_scheduler_t()` reads `rgw_scheduler_type`.

## Control flow
RGW initialization reads scheduler config, builds context/scheduler objects accordingly, and request paths classify work by `client_id`.

## State and persistence
No persistent state. This header defines enum values that must match counter arrays and client config ordering.

## Dependencies and integration points
Depends on the dmClock submodule and Ceph config. It is shared by async/sync scheduler implementations and scheduler context.

## Risks and test signals
Adding client classes requires updating static assertions, counters, config readers, and arrays. Tests should cover config strings `dmclock`, `throttler`, unknown/none, and mapping of each client class to configured reservations/weights/limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_dmclock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_dmclock_async_scheduler.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_dmclock_async_scheduler.cc

## Purpose
Implements Boost.Asio-based asynchronous dmClock scheduling for RGW requests, including cancellation, config updates, throttle accounting, and ready-request processing.

## Important APIs, types, and functions
`AsyncScheduler::~AsyncScheduler()` cancels queued work and unregisters config observation. `handle_conf_change()` updates delegated client info and max concurrent requests, refreshes dmClock client infos, and schedules processing. `schedule_request_impl()` bridges blocking coroutine/yield callers to `async_request()`. `request_complete()` returns a throttle unit. `cancel()` and `cancel(client)` abort queued requests and update counters. `schedule()` arms the timer. `process()` pulls ready requests while under `max_requests`, posts completions, tracks reservation/priority latency, and schedules future work.

## Control flow
Requests enter the pull priority queue from the header template. Processing runs in the Asio executor via timer callbacks. Each ready completion grants capacity until the caller's returned completer calls `request_complete()`.

## State and persistence
State is in-memory queue contents, timer, outstanding count, max request limit, client config, and perf counters.

## Dependencies and integration points
Uses crimson dmClock pull queue, Ceph async completion, Boost.Asio timers/executors, Ceph config observation, and RGW scheduler interface.

## Risks and test signals
Risks include timer callbacks after destruction, outstanding underflow, cancellation races, executor-thread assertions, and config changes while requests are queued. Tests should cover reservation vs priority phases, future timers, max concurrency, cancellation, config reload, and error translation to `-EAGAIN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_dmclock_async_scheduler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_dmclock_async_scheduler.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_dmclock_async_scheduler.h

## Purpose
Declares the asynchronous RGW dmClock scheduler and a simple max-concurrency throttler alternative.

## Important APIs, types, and functions
`AsyncScheduler` inherits `md_config_obs_t` and `Scheduler`, owns a dmClock `PullPriorityQueue`, Asio timer, counters, max/outstanding request atomics, and observer pointer. `async_request()` allocates a completion-backed request, queues it, schedules processing, and updates queue/limit counters. `SimpleThrottler` implements `Scheduler` with only `rgw_max_concurrent_requests` accounting.

## Control flow
Async request submission is nonblocking and completes handlers when dmClock grants a request. Scheduler users receive a `SchedulerCompleter` from the base class and must let it destruct to release capacity.

## State and persistence
All state is transient scheduling state. Perf counters expose queued cost, granted phases, limits, throttle count, and outstanding requests.

## Dependencies and integration points
Uses Boost.Asio, Ceph async completion, dmClock queue types, config observers, and scheduler context counters.

## Risks and test signals
`SimpleThrottler::schedule_request_impl()` increments outstanding before checking the limit, so error paths rely on completer semantics to unwind. Tests should validate capacity release on success and failure, counter deltas, config changes, and handler executor affinity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_dmclock_async_scheduler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_dmclock_scheduler.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_dmclock_scheduler.h

## Purpose
Defines the common RGW scheduler interface used by dmClock and simple throttling implementations.

## Important APIs, types, and functions
`Request` carries client id, start time, and cost. `ReqState` models blocking request state. `Completer<F>` is an RAII callback wrapper whose destructor calls its stored function. `Scheduler::schedule_request()` calls implementation-specific scheduling and returns both status and a `SchedulerCompleter` bound to `request_complete()`.

## Control flow
Callers schedule before processing a request. If accepted, holding the completer represents a granted unit; when the completer destructs, capacity is returned.

## State and persistence
The interface itself stores no state. Implementations maintain queue and throttle state.

## Dependencies and integration points
Depends on Ceph context/config/yield helpers and dmClock request parameter/time types. Used by sync, async, and simple throttler schedulers.

## Risks and test signals
The RAII completer is powerful but can call `request_complete()` even when scheduling failed unless callers handle the returned pair correctly. Tests should verify accepted and rejected request lifecycles, move-only completer behavior, and no double completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_dmclock_scheduler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_dmclock_scheduler_ctx.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_dmclock_scheduler_ctx.cc

## Purpose
Implements dmClock client configuration, perf counter construction, and counter accounting helpers for RGW schedulers.

## Important APIs, types, and functions
`ClientConfig` loads reservation, weight, and limit values for admin/auth/data/metadata clients and observes config keys. `ClientCounters` builds per-client queue counters plus global scheduler throttle counters. `inc()`, `on_cancel()`, and `on_process()` aggregate counter updates. `queue_counters::build()` and `throttle_counters::build()` register perf counters when enabled.

## Control flow
Scheduler context constructs config/counters when dmClock is enabled. Config changes call `ClientConfig::handle_conf_change()`. Schedulers call `on_cancel()` for aborted queued work and `on_process()` for granted requests.

## State and persistence
State is in-memory config vectors and perf counter refs. No persistent storage changes.

## Dependencies and integration points
Uses Ceph config proxy, perf counters collection, dmClock `ClientInfo`, and shared RGW dmClock client ids.

## Risks and test signals
Client ordering is guarded by static assertions and must match enum values. Counter functions must avoid null refs when counters are disabled. Tests should cover config reloads, disabled counters, cancellation cost accounting, reservation/priority latency increments, and per-client/global counter registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_dmclock_scheduler_ctx.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_dmclock_scheduler_ctx.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_dmclock_scheduler_ctx.h

## Purpose
Declares perf counter ids, counter containers, client config observer, and scheduler context wiring for RGW dmClock.

## Important APIs, types, and functions
`queue_counters` and `throttle_counters` define perf counter ids/builders. `ClientCounters` stores counter refs for each client plus global scheduler stats. `ThrottleCounters` wraps simple throttler counters. `ClientSum`/`ClientSums` aggregate counts and costs. `ClientConfig` observes config and returns `ClientInfo*` by `client_id`. `SchedulerCtx` conditionally owns dmClock config and counters based on `rgw_scheduler_type`.

## Control flow
RGW setup constructs `SchedulerCtx`; dmClock schedulers consume `get_dmc_client_config()` and `get_dmc_client_counters()` to initialize queues and counter callbacks.

## State and persistence
State is process-local counters and config snapshots. No persistent state.

## Dependencies and integration points
Depends on Ceph perf counter collections, config observer APIs, and `rgw_dmclock.h`.

## Risks and test signals
`get_dmc_client_counters()` assumes dmClock mode initialized the optional. Tests should verify no access in non-dmClock modes, config-observer lifetimes, and counter id stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_dmclock_scheduler_ctx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_dmclock_sync_scheduler.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_dmclock_sync_scheduler.cc

## Purpose
Implements the blocking/synchronous dmClock scheduler for RGW request paths that cannot use asynchronous completion directly.

## Important APIs, types, and functions
`SyncScheduler::add_request()` queues a stack-owned `SyncRequest`, updates counters, calls `request_completed()` to drive the dmClock push queue, and waits on a condition variable until ready or cancelled. `handle_request_cb()` marks a request ready, notifies the waiter, and updates latency/phase counters. `cancel(client)` and `cancel()` mark queued requests cancelled and notify waiters.

## Control flow
The caller blocks in `add_request()` until the dmClock callback fires. Cancellation removes matching queued requests, sets their state under their mutex, and wakes blocked callers.

## State and persistence
State is in-memory queue contents and per-request condition variables. No persistence occurs.

## Dependencies and integration points
Uses crimson dmClock push queue, scheduler context counters, Ceph perf counters, mutex/condition_variable, and the common scheduler interface.

## Risks and test signals
The queue stores references to synchronization objects whose lifetime is tied to the blocking stack frame, so callbacks must occur before `add_request()` returns. Tests should cover normal readiness, cancellation all/by client, limit rejection, counter decrements, spurious wakeups, and concurrent cancel while waiting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_dmclock_sync_scheduler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_dmclock_sync_scheduler.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_dmclock_sync_scheduler.h

## Purpose
Declares the synchronous dmClock scheduler used for blocking RGW request scheduling.

## Important APIs, types, and functions
`SyncRequest` extends `Request` with references to a mutex, condition variable, mutable request state, and counters. `SyncScheduler` owns a dmClock `PushPriorityQueue`, exposes `add_request()`, cancellation APIs, and a static queue callback `handle_request_cb()`. Its scheduler implementation simply delegates `schedule_request_impl()` to `add_request()`.

## Control flow
Callers submit a request and block. The push queue invokes the static callback when dmClock chooses the request, which wakes the waiter.

## State and persistence
All state is transient queue state. Request synchronization members are non-owning references.

## Dependencies and integration points
Depends on common scheduler types, scheduler context counters, and crimson dmClock queue types.

## Risks and test signals
Because `SyncRequest` references stack locals, queue ownership/lifetime behavior is critical. Tests should validate no dangling callback after cancel/destruction, correct `ReqState` transitions, and callback cost/phase accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_dmclock_sync_scheduler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_env.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_env.cc

## Purpose
Implements RGW request environment/config map helpers used by frontends to access CGI/HTTP environment values and RGW logging options.

## Important APIs, types, and functions
`RGWEnv::init()` loads `char** envp` into a case-insensitive map and initializes `RGWConf`. `set()`, `get()`, `get_optional()`, `get_int()`, `get_bool()`, `get_size()`, `exists()`, `exists_prefix()`, and `remove()` provide typed access. Free helpers `rgw_conf_get*()` operate on generic config maps. `RGWConf::init()` snapshots ops/usage log enablement and bucket-ACL defer mode.

## Control flow
Frontend request setup populates `RGWEnv`, then request/auth/operation code reads headers and flags by name. `exists_prefix()` uses map lower_bound to efficiently detect prefixed variables.

## State and persistence
State is request-local environment map plus copied config booleans/mode. No durable storage.

## Dependencies and integration points
Uses `rgw_common.h`, `rgw_log.h`, Ceph config, case-insensitive comparator, and boolean parsing. It includes crypt sanitization because environment logging may redact keys elsewhere.

## Risks and test signals
Risks include `atoi()` accepting malformed ints, size parse fallback, case-insensitive ordering assumptions for prefix detection, and stale config snapshots after runtime config changes. Tests should cover malformed env entries, duplicate/case-variant keys, prefix lookups, bool parsing, size overflow, and ACL defer modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_env.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_es_main.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_es_main.cc

## Purpose
Provides a small utility executable that compiles an RGW Elasticsearch query expression and prints its JSON representation.

## Important APIs, types, and functions
`main()` initializes Ceph global context, reads the expression from `argv[1]` or defaults to `age >= 30`, constructs `ESQueryCompiler`, sets field aliases, generic entity type map, and custom metadata type map, then calls `compile()` and emits JSON via `JSONFormatter`.

## Control flow
Initialization happens first, then compiler setup, compile validation, error print/`EINVAL` return on failure, or JSON serialization on success.

## State and persistence
No persistent state is modified. The process only reads command-line args and prints to stdout/stderr.

## Dependencies and integration points
Uses Ceph global init/argparse/json helpers and `rgw_es_query.h`. The utility helps test/debug ES query parsing outside the main RGW daemon.

## Risks and test signals
Risks include uncaught exceptions from compiler/global init, default expression hiding missing args, and alias/type-map drift from production code. Tests should run valid/invalid expressions, alias fields, custom metadata fields, date/int typing, and compare emitted JSON with expected query trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_es_main.cc -->
