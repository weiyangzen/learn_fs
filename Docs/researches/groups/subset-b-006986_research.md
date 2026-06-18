# Research: subset-b-006986

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_client_io.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_client_io.h

## Purpose
`rgw_client_io.h` defines the RGW front-end IO abstraction used by request handlers to receive client bodies and emit REST responses without binding the core gateway code to a specific front end such as Beast, civetweb, FastCGI, or load generators. It separates a minimal `BasicClient` interface from the REST-specific `RestfulClient`, provides a decorator base for filter pipelines, and exposes the high-level `RGWRestfulIO` wrapper used from `req_state::cio`.

## Important APIs, Types, And Functions
`rgw::io::BasicClient` owns initialization through `init(CephContext*)`, delegates front-end-specific setup to `init_env()`, exposes `get_env()`, and finishes work through `complete_request()`. Its `init()` implementation lives in `rgw_client_io.cc` and logs sanitized environment variables at debug level 20.

`rgw::io::RestfulClient` extends `BasicClient` with the ordered HTTP response lifecycle: optional `send_100_continue()`, exactly one `send_status()`, headers and either content length or chunked transfer, `complete_header()`, body writes, flush, and request completion. Methods throw `rgw::io::Exception` on transport errors.

`DecoratedRestfulClient<DecorateeT>` is the static/dynamic decorator base. It can hold either a decoratee object or pointer, forwards all `RestfulClient` calls, and lets pointer-based decorators be rewired through `set_decoratee()`. `RGWRestfulIO` derives from `AccountingFilter<RestfulClient*>`, keeps `shared_ptr<DecoratedRestfulClient>` filters alive, and inserts filters by setting each new filter's decoratee to the current chain head.

`BuffererSink` and `StaticOutputBufferer<BufferSizeV>` provide stack-backed buffering for small output fragments such as HTTP headers. `RGWClientIOStreamBuf` adapts `RGWRestfulIO::recv_body()` into a C++ `std::streambuf` with putback support; `RGWClientIOStream` exposes it as `std::istream`.

## Control Flow
The request path constructs a front-end `RestfulClient`, wraps it in `RGWRestfulIO`, optionally adds filters, stores it in `req_state::cio`, and request handlers call through `RESTFUL_IO(s)` or `ACCOUNTING_IO(s)`. The response lifecycle is deliberately ordered, but the base classes do not enforce it; front ends and filters rely on callers to honor the contract.

`RGWClientIOStreamBuf::underflow()` preserves the putback window, reads a new window from `rio.recv_body()`, and returns EOF if the read returns zero or throws. This makes body parsing code consume client data through standard stream extraction while the real source remains the RGW client IO pipeline.

## State And Persistence Behavior
This file defines transient request IO state only. It does not persist data to RADOS. `RGWRestfulIO` owns filter objects for the lifetime of the wrapper, while the underlying front-end engine is supplied externally. `StaticOutputBufferer` stores a fixed char array inside the streambuf and flushes to its sink during `sync()` and `overflow()`.

## Dependencies And Integration Points
The header depends on `rgw_common.h` for `RGWEnv` and `req_state`, and includes `rgw_client_io_filters.h` mid-file because the filter templates derive from types declared earlier in this same header. It is included broadly by REST handlers, auth code, process code, logging, checksum pipes, and front-end client implementations. The helper casts assert that `req_state::cio` actually implements the expected IO interface.

## Risks And Edge Cases
The response ordering contract is documented but not enforced, so filter behavior can become incorrect if handlers send headers or body out of order. Pointer decorators can be rewired without synchronization, and the comments explicitly put atomicity/thread-safety on callers. `RGWClientIOStreamBuf::underflow()` catches all `rgw::io::Exception` and reports EOF, which can collapse transport errors into normal stream exhaustion for stream consumers. `StaticOutputBufferer::overflow()` writes to `*pptr()` before syncing, so the setp end pointer intentionally reserves one character of space.

## Test Signals
Useful tests exercise request initialization logging with sanitized env values, ordered response generation through decorator chains, `RGWRestfulIO::add_filter()` chaining order, accounting through `ACCOUNTING_IO()`, and body stream extraction across multiple `recv_body()` windows including zero-length EOF and thrown exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_client_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_client_io_filters.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_client_io_filters.h

## Purpose
`rgw_client_io_filters.h` implements reusable `RestfulClient` decorators for RGW response and request IO. These filters adapt imperfect caller behavior, add byte accounting, synthesize missing content length headers, emit HTTP chunked transfer framing, and suppress prohibited `Content-Length` headers for selected statuses.

## Important APIs, Types, And Functions
`AccountingFilter<T>` counts bytes sent and received while accounting is enabled. It wraps `send_status()`, `send_100_continue()`, header calls, body sends, body receives, and `complete_request()`, adding returned byte counts to `total_sent` or `total_received`.

`BufferingFilter<T>` buffers response body data in a `ceph::bufferlist` when callers complete headers without declaring a length or chunked transfer. On `complete_request()`, it sends the calculated `Content-Length`, completes the header, then replays buffered body segments.

`ChunkingFilter<T>` turns `send_chunked_transfer_encoding()` into `Transfer-Encoding: chunked` and wraps each `send_body()` payload with hexadecimal size and CRLF delimiters. `complete_request()` writes the terminal `0\r\n\r\n` chunk.

`ConLenControllingFilter<T>` records the status sent and inhibits `send_content_length()` for HTTP 204 and 304 unless `rgw_print_prohibited_content_length` is enabled.

`ReorderingFilter<T>` buffers headers and an early content length until status has been sent and header completion begins. This is a compatibility shim for callers that invoke the REST IO methods in the wrong order.

## Control Flow
Filters are stacked via `RGWRestfulIO::add_filter()`, so each override usually does local state handling and forwards to `DecoratedRestfulClient<T>`. Accounting is passive and depends on wrapped calls returning accurate byte counts. Buffering turns `complete_header()` into a no-op when content length is unknown, then defers header completion until `complete_request()`. Chunking is enabled by a single call and remains active until request completion.

## State And Persistence Behavior
All state is per-request and in memory. Accounting counters survive enable/disable toggles but are not reset by `set_account()`. Buffering stores all deferred body bytes in memory until completion, then clears the buffer and disables buffering. Chunking stores only a boolean. Reordering stores vectors of copied header strings plus an optional content length until `complete_header()`.

## Dependencies And Integration Points
The filters depend on `DecoratedRestfulClient` from `rgw_client_io.h`, `CephContext` logging, `ceph::bufferlist`, `boost::optional`, and global configuration through `g_conf()`. They integrate with the high-level `RGWRestfulIO` chain and therefore affect all REST handlers that emit responses through `req_state::cio`.

## Risks And Edge Cases
`BufferingFilter` can accumulate large responses in memory when no length/chunked marker is provided, so callers should avoid relying on it for large bodies. Its synthetic header bytes are deliberately not counted as body/accounting bytes after it forces `sent = 0`, making byte accounting semantics subtle. `ConLenControllingFilter::send_content_length()` returns `-EINVAL` if status has not been observed, even though the method returns `size_t`; callers expecting exceptions or signed errors must handle this carefully. `ChunkingFilter` does not support chunk extensions or trailers. Reordering can mask caller bugs and may preserve header order differently than direct emission.

## Test Signals
Tests should verify byte counters across enabled/disabled intervals, synthetic content length generation, memory replay of multiple bufferlist segments, chunk framing including the terminal chunk, 204/304 content-length suppression under both config settings, and early header/content-length reordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_client_io_filters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_common.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_common.cc

## Purpose
`rgw_common.cc` implements large shared pieces of RGW request handling and metadata behavior declared across `rgw_common.h` and related headers. It covers protocol error mapping, request initialization, metadata extraction, HTTP/query parsing, time and URL utilities, HMAC/SHA helpers, IAM/ACL permission evaluation, object lock checks, user/bucket/account JSON and binary codec support, bucket instance parsing, global initialization, and version tag generation.

## Important APIs, Types, And Functions
The global `rgw_http_*_errors` maps translate RGW/internal errno values into S3, Swift, STS, and IAM HTTP status/code pairs. `set_req_state_err()` normalizes negative errors, selects protocol-specific mappings from `req_state::prot_flags`, and falls back to S3 or `UnknownError`.

`req_info::req_info()` derives method, URI, query string, host, and parameters from `RGWEnv`, including absolute-URI normalization and stripping numeric host ports. `req_info::init_meta_info()` scans CGI-style environment headers with accepted metadata prefixes, canonicalizes them into `x_meta_map`, combines duplicates with commas, and separately tracks server-side-encryption metadata in `crypt_attribute_map`.

`RGWHTTPArgs::parse()`, `append()`, `get_bool()`, `get_int()`, and `sys_get()` parse URL query arguments, identify S3/Swift subresources and response modifiers, split system parameters with `rgwx-`, and mask password-like values in logs.

Permission flow centers on `evaluate_iam_policies()`, `verify_user_permission()`, `verify_bucket_permission()`, `verify_object_permission()`, and their no-policy ACL fallbacks. These functions account for explicit deny precedence, resource/identity/session policy interaction, account root, cross-account requests requiring separate allows, requester-pays, Block Public Access, object ownership mode, deferred bucket ACL checks, and Swift ACL enforcement.

Utility implementations include RFC2616/ISO8601 parsing, URL encode/decode, whitespace/quote trimming, HMAC-SHA1/SHA256, streaming SHA256 helpers, wildcard policy matching by colon-delimited components, cap/op parsing, and pool/object string conversions.

Codec and dump implementations include `RGWBucketInfo`, `RGWUserInfo`, `RGWAccountInfo`, `RGWGroupInfo`, `RGWBucketEnt`, `RGWStorageStats`, `RGWSubUser`, `RGWAccessKey`, `rgw_obj_key`, `rgw_raw_obj`, and related test-instance generators.

## Control Flow
A typical request starts with `req_state` construction, which embeds `req_info`, copies logging flags and ACL deferral config from `RGWEnv`, and records a coarse start time for log prefixes. Handlers parse query args and metadata, authenticate identity elsewhere, then call verification helpers. Permission helpers first evaluate IAM policy effects, short-circuit explicit denies/allows, and fall back to ACL checks only when policy did not decide and policy is not mandatory. Error paths call `set_req_state_err()` and `dump()` to render protocol-specific error objects.

Bucket and user metadata flows call binary `encode()`/`decode()` methods declared inline in `rgw_common.h` plus JSON dump/decode functions here. `RGWBucketInfo::decode()` contains substantial compatibility logic across layout versions, owner encoding changes, website/versioning/object-lock/sync-policy additions, and synthesized log layout defaults.

## State And Persistence Behavior
This file manipulates persistent metadata structures but does not itself perform RADOS IO. Encoded structs are persisted by other layers as bucket/user/account metadata objects or attrs. Compatibility is critical: `RGWBucketInfo::encode()` writes version 24 with owner duplicated in old user fields, while `decode()` supports legacy versions and reconstructs new layouts. `RGWUserInfo` encodes version 23 with account, path, create date, tags, and group ids while maintaining older access-key fields. `RGWObjVersionTracker::generate_new_write_ver()` creates a new random tag and version sequence used by RADOS versioned writes in other files.

## Dependencies And Integration Points
The implementation depends on Ceph JSON/Formatter, crypto wrappers, global init, OpenSSL setup, IAM policy classes, ACLs, object lock, bucket layout/sync policy, SAL bucket/object interfaces, and `rgw_http_errors.h`. It is central infrastructure used by almost every RGW REST operation and admin path.

## Risks And Edge Cases
Permission ordering is high risk: explicit deny, cross-account policy intersection, session policy behavior, requester-pays, public access block, and object-ownership ACL suppression must match S3 semantics. Query parsing uses string indexing such as `name[0]` after parsing; empty query names should be considered in tests. `url_decode()` returns an empty string on malformed hex, which is ambiguous with a valid empty result. `rgw_string_unquote()` indexes `s[0]` before checking size, so empty input would be unsafe if callers pass it. Legacy decode paths and duplicated owner fields are compatibility-sensitive. `RGWCompletionInfo` is not here, but compression attrs and object lock attrs consumed elsewhere rely on constants from the header.

## Test Signals
Test signals include encode/decode round trips from `generate_test_instances()`, dbstore tests using `RGWUserInfo` and `RGWBucketInfo`, protocol error mapping tests for S3/Swift/IAM/STS flags, permission matrix tests for IAM/ACL/session/cross-account/public-access/requester-pays/object-ownership, URL and query parser fuzz cases, and bucket instance parse cases with and without shard ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_common.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_common.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_common.h

## Purpose
`rgw_common.h` is the core shared declaration header for RGW. It defines attribute names, protocol and internal error/status constants, request environment/query state, user/account/group/bucket metadata structures, request state, permission helper declarations, utility APIs, and inline encode/decode logic for several persistent metadata types.

## Important APIs, Types, And Functions
The top of the file declares the RGW attr namespace (`RGW_ATTR_*`) for ACLs, lifecycle, CORS, object lock, encryption, compression, cloud tiering, replication, IAM policy, bucket logging, ownership controls, and metadata headers. These constants are the stable keys used in RADOS attrs and HTTP header mapping.

`RGWFormat`, REST protocol bitmasks, internal status/error constants, capability flags, and operation-type flags provide common vocabulary for handlers and error mappers. `NameVal` and `RGWHTTPArgs` define query parsing and subresource tracking. `RGWEnv` and `RGWConf` wrap CGI/front-end environment variables and request-level logging/ACL-defer configuration.

Persistent metadata structures include `RGWRateLimitInfo`, `RGWUserInfo`, `RGWAccountInfo`, `RGWGroupInfo`, `RGWBucketInfo`, `RGWBucketEntryPoint`, `RGWBucketEnt`, `multipart_upload_info`, and `RGWStorageStats`. They expose Ceph `encode()`/`decode()`, `dump()`, `decode_json()`, and `generate_test_instances()` where appropriate. `RGWObjVersionTracker` declares RADOS version-guard helpers implemented elsewhere, plus inline helpers to expose read/write version pointers.

`req_info` captures request method, host, URI, query args, metadata maps, and storage class. `req_state` is the central per-request object passed through RGW operations: it carries client IO, op type, rate-limit state, formatter, parsed bucket/object/source names, SAL bucket/object pointers, authenticated identity, ACLs, IAM policies, object ownership, tracing, yield context, tags, and request identifiers.

The bottom of the file declares permission APIs, URL/time/HMAC/hash helpers, policy matching, header canonicalization transforms, global init, IAM policy attr extraction, object locator helpers, and bufferlist append/truncate helpers.

## Control Flow
Most RGW operations build on this header by creating a `req_state`, parsing `RGWHTTPArgs`, populating bucket/object/user/auth fields, then invoking permission helpers and operation-specific logic. Persistent metadata flows rely on inline encode/decode version blocks in this header and JSON implementations in `rgw_common.cc`. Request utilities such as `RESTFUL_IO()` in `rgw_client_io.h` depend on `req_state::cio` declared here.

## State And Persistence Behavior
Several structures declared here are persisted directly. `RGWUserInfo` has versioned encoding up to v23 and preserves legacy single access/swift key fields while storing maps, quotas, MFA ids, account metadata, tags, and groups. `RGWBucketInfo` persists bucket identity, owner, flags, placement, layout, website, Swift versioning, requester-pays, object lock, sync policy, and resharding state. `RGWBucketEntryPoint`, `RGWBucketEnt`, and `multipart_upload_info` have backward-compatible decoders. `req_state`, `req_info`, and `RGWEnv` are transient request state only.

## Dependencies And Integration Points
The header is a dependency hub for RGW and includes Ceph crypto, tracing, async yield context, ACL, bucket layout, IAM policy, quota, website, object lock, object ownership, tags, sync policy, cls rgw/user/version types, librados/neorados, public access block, and SAL forward declarations. Because it is included broadly, changes can have large compile-time and behavioral blast radius.

## Risks And Edge Cases
Binary encoding version changes are high risk and must preserve backward compatibility. `req_state` owns several raw pointers (`formatter`, `cio`) and many unique pointers; lifetime boundaries are spread across request processing code. Constants in this file are protocol contracts and attr keys, so renaming or reusing them can break persisted data or client compatibility. Inline helpers that transform headers and object locators are used in signing, metadata, and storage paths, so subtle canonicalization changes can affect authentication or object lookup.

## Test Signals
Good signals include encode/decode round trips for every `WRITE_CLASS_ENCODER` type, JSON dump/decode compatibility for admin outputs, request-state construction tests with mocked `RGWEnv`, permission helper matrix tests, object locator tests for bucket markers and locators, and compile coverage of modules that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_compression.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_compression.cc

## Purpose
`rgw_compression.cc` implements RGW object compression and decompression filters. It decodes persisted compression metadata, compresses incoming PUT data before handing it to the next data processor, and decompresses GET data while projecting requested logical ranges onto compressed storage ranges.

## Important APIs, Types, And Functions
`rgw_compression_info_from_attr()` decodes `RGWCompressionInfo` from a bufferlist attr, rejects malformed or empty block metadata, and sets `need_decompress` based on `compression_type != "none"`. `rgw_compression_info_from_attrset()` looks up `RGW_ATTR_COMPRESSION` in an attr map and treats absence as no decompression required.

`RGWPutObj_Compress::process()` receives logical object data, calls `Compressor::compress()`, tracks whether the stream remains compressed, appends `compression_block` entries mapping original offsets to compressed offsets/lengths, and forwards either compressed or original data to `Pipe::process()` at the correct physical offset.

`RGWGetObj_Decompress::handle_data()` accumulates partial compressed blocks in `waiting`, extracts complete compressed blocks, calls `compressor->decompress()`, and streams decompressed output to the next `RGWGetObj_Filter` in chunks capped by `rgw_max_chunk_size`. `fixup_range()` calls `project_compress_range()` to map the requested logical range onto compressed block indices and physical byte range.

`compression_block::dump()`, `RGWCompressionInfo::dump()`, and `generate_test_instances()` provide formatter and encoding test support.

## Control Flow
On PUT, the first non-empty chunk attempts compression. If first-part compression fails, the object is stored uncompressed. If a later chunk fails after compression already started, the operation fails with `-EIO` because mixed compressed/uncompressed continuation would invalidate the block map. Empty chunks only advance the compressed offset to the end of the last block.

On GET, callers first decode compression attrs and call `fixup_range()` so lower layers fetch the compressed byte range that contains all needed blocks. As data arrives, `handle_data()` merges any prior incomplete block, waits until the full compressed block is present, decompresses it, skips `q_ofs`, emits up to `q_len`, and updates `cur_ofs`.

## State And Persistence Behavior
`RGWCompressionInfo` and its `compression_block` vector are persisted as `RGW_ATTR_COMPRESSION` by higher-level PUT code. This file mutates only per-operation filter state: current compressed offset, compressor message, block vector, range projection iterators, pending bytes, and remaining output range. The compressor-specific optional message is preserved in metadata and passed back to decompression.

## Dependencies And Integration Points
The file depends on Ceph `Compressor`, `rgw_putobj` pipelines, `RGWGetObj_Filter`, `RGW_ATTR_COMPRESSION` from `rgw_common.h`, and `rgw_range_projection.h`. It is integrated by RGW operation and SAL paths that optionally install compression on PUT and decompression on GET or copy/read workflows.

## Risks And Edge Cases
Range projection and block iterator arithmetic are correctness-critical; invalid or empty block metadata returns `-EIO`, but corrupted offsets could still lead to bad seeks or output truncation if not validated upstream. `handle_data()` stores incomplete compressed block tails in memory and adjusts `cur_ofs` with `cur_ofs -= tail`, so unsigned/offset interactions deserve tests. Compression fallback is asymmetric: first-part failure stores uncompressed, later failure aborts. Missing compressor plugins make reads fail with `-EIO`.

## Test Signals
Tests should cover attr absence, malformed attr decode, `compression_type == "none"`, first-chunk compression failure fallback, later-chunk failure abort, block map offset generation, full and partial range decompression, multi-input chunks that split compressed blocks, and max-chunk-size output splitting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_compression.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_compression.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_compression.h

## Purpose
`rgw_compression.h` declares the RGW compression/decompression filter interfaces used by object PUT and GET paths. It connects persistent compression metadata to the runtime data processor/filter pipeline.

## Important APIs, Types, And Functions
`rgw_compression_info_from_attr()` and `rgw_compression_info_from_attrset()` expose metadata decoding and a `need_decompress` decision to callers that have object attrs. `RGWGetObj_Decompress` derives from `RGWGetObj_Filter` and overrides `handle_data()` plus `fixup_range()` to transform compressed storage bytes into logical object bytes. Its state includes the compressor, compression metadata, partial-content mode, selected first/last blocks, requested output offset/length, current compressed offset, and a `waiting` buffer for incomplete blocks.

`RGWPutObj_Compress` derives from `rgw::putobj::Pipe` and overrides `process()` to compress incoming data before passing it to the next `DataProcessor`. It exposes `is_compressed()`, `get_compression_blocks()`, and `get_compressor_message()` so higher-level PUT code can persist `RGWCompressionInfo`.

## Control Flow
Callers insert `RGWPutObj_Compress` into the PUT pipeline when a compression policy selected a `CompressorRef`. After all data is processed, the caller inspects whether compression actually occurred and persists the resulting block map. For reads, callers decode attrs, construct `RGWGetObj_Decompress` when needed, call `fixup_range()` before fetching data, and pass fetched compressed chunks through `handle_data()`.

## State And Persistence Behavior
The header itself declares transient filter state. The persistent representation is `RGWCompressionInfo` from `rgw_compression_types.h`; `RGWPutObj_Compress` exposes the pieces needed to build that attr. `RGWGetObj_Decompress` holds a raw pointer to `RGWCompressionInfo`, so the metadata object must outlive the filter.

## Dependencies And Integration Points
The declarations depend on `compressor/Compressor.h`, `rgw_putobj.h`, `rgw_op.h`, and `rgw_compression_types.h`. This couples compression to both the PUT data processor pipeline and the GET object filter abstraction.

## Risks And Edge Cases
`RGWGetObj_Decompress` stores iterators into `cs_info->blocks`; mutating or destroying `cs_info` while the filter is active would invalidate them. The PUT filter assumes logical offsets are supplied consistently by upstream processors. API consumers must not persist compression metadata unless `is_compressed()` is true and the block vector is valid.

## Test Signals
Header-level integration tests should instantiate filters in realistic GET/PUT chains, verify lifetime expectations for `RGWCompressionInfo`, and assert that callers persist block metadata only after successful compressed writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_compression.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_compression_types.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_compression_types.h

## Purpose
`rgw_compression_types.h` defines the persistent metadata format for RGW object compression. The metadata lets RGW map logical object offsets to compressed storage offsets and reconstruct the original object during reads.

## Important APIs, Types, And Functions
`compression_block` stores one compressed block mapping: `old_ofs` is the original logical offset, `new_ofs` is the compressed object offset, and `len` is the compressed block length. It has versioned Ceph encode/decode and `dump()`.

`RGWCompressionInfo` stores `compression_type`, `orig_size`, optional `compressor_message`, and a vector of `compression_block`s. It encodes version 2, preserving compatibility with version 1 metadata that did not include `compressor_message`. The default constructor represents no compression with type `"none"` and size zero. `generate_test_instances()` supplies encode/decode coverage data.

## Control Flow
PUT compression code builds a block vector as chunks are compressed and then persists an `RGWCompressionInfo` attr. GET code decodes this attr, uses the block map to project ranges, and passes `compressor_message` back to the compressor for algorithms that need side-channel state.

## State And Persistence Behavior
This is a persisted wire/storage contract. `RGWCompressionInfo` is stored under `RGW_ATTR_COMPRESSION` by object write paths and later decoded by read paths, admin dump paths, and SAL drivers. Version changes must be additive and compatible with old objects.

## Dependencies And Integration Points
The file depends on Ceph `include/encoding.h`, `bufferlist`, optional/string/vector, and formatter declarations. `rgw_compression.cc`, object operation code, SAL drivers, and admin decode/dump code consume these types.

## Risks And Edge Cases
A block vector with zero entries is rejected by `rgw_compression_info_from_attr()` even if the type says compressed, so writers must not persist empty compressed metadata. The block map does not by itself encode decompressed block lengths; consumers infer range behavior from ordered `old_ofs` and compressed lengths, making ordering and offset consistency important. Optional `compressor_message` must remain compatible with the chosen compressor type.

## Test Signals
Tests should include encode/decode for v1 and v2 metadata, formatter dumps with and without `compressor_message`, empty block rejection at decode time, and range projection against multi-block maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_compression_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_coroutine.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_coroutine.cc

## Purpose
`rgw_coroutine.cc` implements RGW's cooperative coroutine scheduler and completion bridge. It coordinates stacks of `RGWCoroutine` operations, child stack spawning/collection, asynchronous RADOS completion notifications, timer wakeups, admin-socket dumps, deadlock detection, and the `RGWSimpleCoroutine` request lifecycle helper.

## Important APIs, Types, And Functions
`RGWCompletionManager` owns a completion queue, a set of active `RGWAioCompletionNotifier`s, a timer, and waiter mapping. `complete()`, `get_next()`, `try_get_next()`, `wait_interval()`, `wakeup()`, and `go_down()` coordinate IO/timer completions with scheduler wakeups.

`RGWAioCompletionNotifier` wraps a single librados `AioCompletion`. Its callback unregisters itself, completes the associated stack through `RGWCompletionManager`, and balances intrusive references.

`RGWCoroutinesStack::operate()` runs the current coroutine, unwinds finished calls, propagates retcodes, and marks done/error states. `spawn()`, `collect()`, `collect_next()`, `wait()`, `io_complete()`, `try_io_unblock()`, and `consume_io_finish()` manage child stacks and IO completion masks.

`RGWCoroutinesManager::run()` is the main scheduler loop. It tracks a run context, scheduled stacks, blocked counts, interval-wait counts, and completion events. It reschedules runnable stacks, waits when too many real IOs are outstanding (`ops_window`), unblocks dependent stacks, cancels on shutdown, and asserts if stacks remain with no progress.

`RGWCoroutinesManagerRegistry` publishes scheduler state through the admin socket. `RGWSimpleCoroutine` provides a template state machine: `init()`, `send_request()`, wait for IO, `request_complete()`, optional retry for `-ERR_INTERNAL_ERROR`, `finish()`, drain children, and cleanup.

## Control Flow
Callers allocate a manager and run either a single coroutine or a list of stacks. A coroutine can `call()` another coroutine on the same stack, `spawn()` a child stack, `wait()` on a timer, or `io_block()` until its assigned IO id completes. The manager repeatedly pops scheduled stacks, runs one coroutine step, records whether the stack is done, blocked, sleeping, or runnable, then drains queued completions. Completion events carry a `user_info` pointer to the stack and an `rgw_io_id`; masks that do not match the current blocked id are stored for later consumption.

`drain_children()` is itself a boost coroutine state machine. It yields until children finish, calls `collect()`, records errors in the coroutine error stream, and optionally lets callbacks force an exit after all children are drained.

## State And Persistence Behavior
All state is in-memory process state. There is no persistent storage. Correctness depends on intrusive reference counts on coroutines, stacks, notifiers, completion managers, and registries. The manager's `run_contexts` map exists for active scheduler runs and admin dumps only.

## Dependencies And Integration Points
The implementation depends on Boost.Asio coroutine macros, librados AIO completions, Ceph `SafeTimer`, admin socket hooks, Ceph locks/condition variables, debug formatting, and `rgw_asio_thread` blocking warnings. It is used by RGW RADOS coroutine code, REST replication/resource coroutines, metadata log services, admin operations, and SAL drivers with coroutine registry support.

## Risks And Edge Cases
Reference-counting and cancellation are high risk: notifiers call `get()`/`put()` around callbacks and destructors unregister under locks. `RGWCompletionManager::_complete()` checks `complete_reqs_set` but does not insert into it in the shown implementation, so duplicate suppression depends on behavior outside this set or may be incomplete. Deadlock detection asserts if no scheduled or blocked progress remains while context stacks still exist. Blocked counters must stay balanced when stacks are interval waits versus real IO waits. Raw `void*` stack pointers in completion user data require stack lifetime to be protected by scheduler references.

## Test Signals
Tests should cover single coroutine completion, nested `call()` unwind, child `spawn()` with wait and collect, IO completion before and after `io_block()`, completion masks/channels, interval wait wakeup, shutdown cancellation, admin dump output, deadlock detection scenarios, and `RGWSimpleCoroutine` retry/cleanup semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_coroutine.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_coroutine.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_coroutine.h

## Purpose
`rgw_coroutine.h` declares the cooperative coroutine framework used by RGW asynchronous services. It defines the scheduler-facing abstractions for coroutines, stacks, completion notifications, manager registries, consumer coroutines, and a simple request coroutine base class.

## Important APIs, Types, And Functions
`RGWCompletionManager` exposes completion queue operations and timer wakeups. `RGWAioCompletionNotifier` and `RGWAioCompletionNotifierWith<T>` adapt librados completions to that queue.

`RGWCoroutinesEnv` carries the active run context, manager, scheduled stack list, and current stack. `RGWCoroutineState` defines run/done/error states. `rgw_spawned_stacks` tracks child stacks that must be collected.

`RGWCoroutine` derives from `RefCountedObject` and `boost::asio::coroutine`. Subclasses implement `operate()`. The base class provides status/history reporting, error logging, `call()`, `spawn()`, `collect()`, `collect_next()`, `wait()`, child draining helpers, sleep/wakeup, IO blocking/completion, and IO provider initialization. Macros such as `yield_until_true`, `drain_all`, and `yield_spawn_window` encode common Boost.Asio coroutine patterns.

`RGWConsumerCR<T>` is a coroutine with an in-memory product queue and wakeup-on-receive behavior. `RGWCoroutinesStack` is the executable stack of coroutine calls plus child-stack and IO-blocking state. `RGWCoroutinesManagerRegistry` tracks active managers and implements `AdminSocketHook`. `RGWCoroutinesManager` owns completion management, run contexts, IO/stack id providers, scheduling, notifier creation, and stack allocation. `RGWSimpleCoroutine` is a base for one-shot async requests with init/send/complete/finish/cleanup hooks.

## Control Flow
Subclasses generally use Boost.Asio `reenter/yield` macros in `operate()`. A coroutine can yield on `io_block()`, wait on child completion through drain macros, or sleep until another component calls `receive()` or `wakeup()`. The stack and manager track whether the coroutine is runnable, IO-blocked, sleeping, blocked by a child stack, or waiting for any child to complete.

## State And Persistence Behavior
All declared state is transient scheduler state. Status history stores the last ten status strings by default for diagnostics. Stacks own lists of coroutine pointers and spawned stack refs. Managers own active run contexts and id counters. No data is persisted across process restarts.

## Dependencies And Integration Points
The header depends on Boost.Asio coroutine support, Ceph refcounting, timers, admin socket, debug locks, `rgw_common.h`, and `rgw_http_client_types.h` for IO identifiers/providers. It is inherited by many RGW async RADOS, REST, metadata, and service coroutines.

## Risks And Edge Cases
The framework exposes raw pointers and intrusive refs, so caller ownership discipline is central. Macros hide control flow and require callers to understand Boost coroutine reentry semantics. Child draining callbacks can request exit but still drain remaining children. IO id masks allow completion before blocking and channel-specific unblocking, which is powerful but easy to misuse. `RGWConsumerCR` stores products unboundedly unless producers/consumers apply backpressure.

## Test Signals
Header-level test signals include subclass compile coverage, coroutine macro behavior in representative subclasses, status dump history, consumer receive/wakeup behavior, IO provider id assignment, child-drain callbacks, and admin registry add/remove lifetime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_coroutine.h -->
