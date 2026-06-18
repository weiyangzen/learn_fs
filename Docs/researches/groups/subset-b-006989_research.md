# subset-b-006989 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_http_client.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_http_client.cc

## Purpose

`rgw_http_client.cc` implements RGW's libcurl-backed HTTP transport. It provides one-shot synchronous/coroutine request processing, background multi-handle processing, pooled curl easy handles, header/data callbacks, cancellation, pause/resume, and global `RGWHTTP::send()`/`RGWHTTP::process()` entry points used by Keystone, external services, and other RGW subsystems.

## Important APIs, Types, and Functions

The private `rgw_http_req_data` owns per-request runtime state: curl handle, header list, return status, HTTP status propagation, callback completion, condition variable, pause flags, manager pointer, and registration state. `RGWCurlHandles` pools `RGWCurlHandle` wrappers and reclaims idle handles after `MAXIDLE`. `RGWHTTPClient::init_request()` converts the higher-level client object into curl options. `RGWHTTPManager` owns the `CURLM` multi handle, request maps, unregister queues, state-change queue, signal pipe, and worker thread. `RGWHTTPHeadersCollector` and `RGWHTTPTransceiver` implement common header capture and buffer-backed request/response bodies.

## Control Flow and Data Flow

Callers configure an `RGWHTTPClient`, then `RGWHTTP::send()` asks the global manager to allocate `rgw_http_req_data`, initialize curl callbacks/options, register it, and signal the manager thread. The thread waits in `curl_multi_wait()` with an extra pipe fd for wakeups, links newly registered handles, performs curl work, consumes `CURLMSG_DONE`, converts HTTP/libcurl/user callback failures to Ceph errno values, finishes the request, releases headers/handles, and wakes waiters or coroutine completions. Receive/send callbacks dispatch into virtual `receive_header()`, `receive_data()`, and `send_data()` methods and can convert negative user returns into curl errors.

## State and Persistence Behavior

State is in memory only. Persistent external effects are the outbound HTTP requests and response bodies appended to caller-provided buffers. Curl handles are reset and reused until idle cleanup or global shutdown. Request completion is protected by `rgw_http_req_data::lock`; manager request structures use a shared mutex plus queues for unregister and pause/resume changes.

## Dependencies and Integration Points

The implementation depends on libcurl easy/multi APIs, Ceph mutex/thread/condition primitives, `ceph::async::Completion`, RGW errno/error mapping, and optional `RGWCompletionManager` callbacks under RADOS builds. Keystone token requests and other RGW clients use `RGWHTTPTransceiver`; callers can provide custom subclasses for streaming or pause-aware I/O.

## Risks and Edge Cases

Important risks are global lifecycle ordering (`rgw_http_client_init()`/cleanup versus `rgw::curl::setup_curl()`), races between cancellation and curl callbacks, pause/resume state changes while callbacks hold request locks, low-speed timeout behavior, `send_len` narrowing to `long`, and security changes when SSL verification is disabled or environment-provided `CURL_CA_BUNDLE` is accepted. Signal-pipe write failures and curl multi failures are fatal to request progress.

## Test Signals

Useful tests include GET/POST/PUT/HEAD success, 4xx/5xx errno mapping, SSL verification on/off and custom CA/client certs, callback-injected read/write failures, cancellation before and after link, coroutine and blocking waits, pause/resume streaming, low-speed timeout, handle reuse/cleanup, and manager shutdown with live/unregistered requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_http_client.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_http_client.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_http_client.h

## Purpose

`rgw_http_client.h` declares the public and protected HTTP-client surface for RGW. It abstracts request configuration, virtual data callbacks, response/header collection, body transceiving, request lifecycle, and the manager facade used by libcurl-backed implementation code.

## Important APIs, Types, and Functions

`RGWHTTPClient` stores method, URL, parsed protocol/host/resource prefix, headers, send length hints, SSL options, timeout settings, HTTP status, user info, and `rgw_http_req_data`. It exposes `append_header()`, `set_send_length()`, `set_send_data_hint()`, `set_verify_ssl()`, `set_req_timeout()`, `set_req_connect_timeout()`, `process()`, `wait()`, `cancel()`, and `get_req_retcode()`. Subclasses override `receive_header()`, `receive_data()`, and `send_data()`. `RGWHTTPHeadersCollector` captures a configured case-insensitive set of headers. `RGWHTTPTransceiver` sends a string body and appends response data into a `bufferlist`. `RGWHTTPManager` declares request add/remove/state control and thread startup/shutdown. `RGWHTTP` is the static global facade.

## Control Flow and Data Flow

The header defines a template method pattern: callers use concrete subclasses for body/header behavior, while the implementation wires static curl callbacks back into virtual methods. `RGWHTTPManager` owns actual scheduling; clients are passive request descriptors until `RGWHTTP::send()` or `process()` is invoked. Pause/resume calls are protected by the request lock and are only valid once the threaded manager owns the request.

## State and Persistence Behavior

The types do not persist data themselves. `RGWHTTPTransceiver` stores transient post data and appends transient response bytes to a caller-owned `bufferlist`. User-info and `rgw_io_id` integration provide correlation with completion managers. `http_status` starts at `HTTP_STATUS_NOSTATUS` and is updated on completion.

## Dependencies and Integration Points

The header depends on Ceph async yield contexts, RGW common/string helpers, `bufferlist`, and `rgw_http_client_types.h`. It is consumed by Keystone and any RGW component that needs outbound HTTP. It also exposes `RGWPostHTTPData` as an alias for legacy callers.

## Risks and Edge Cases

Subclasses must keep referenced `bufferlist` and any callback-owned data alive through completion. `get_header_value()` throws on missing headers, so callers should use `get_headers()` or handle exceptions. `set_url()` changes only the effective URL after initial parsing, so code using parsed `host`/`resource_prefix` must be careful. Request objects should not be destroyed while external code still expects callbacks.

## Test Signals

Compile tests should cover subclass overrides and no-op base callbacks. Runtime tests should exercise header collection case-insensitivity, empty header values, post data streaming, timeout setters, SSL option propagation, cancellation through destructor, and `RGWHTTP::process()` wait semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_http_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_http_client_curl.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_http_client_curl.cc

## Purpose

`rgw_http_client_curl.cc` centralizes process-level curl/OpenSSL setup and cleanup for RGW HTTP clients. It hides old OpenSSL thread-callback requirements, determines whether frontend SSL setup should be left to Beast in legacy builds, and starts/stops the saved curl easy-handle pool.

## Important APIs, Types, and Functions

For OpenSSL builds with pre-1.1.0 APIs, `openssl::RGWSSLSetup` owns a vector of mutexes used by `CRYPTO_set_locking_callback()`, and `rgw_ssl_thread_id_callback()` reports `pthread_self()`. `rgw::curl::fe_inits_ssl()` scans frontend configs for Beast SSL certificates and can remove `CURL_GLOBAL_SSL` from curl init flags. `rgw::curl::setup_curl()` is protected by `std::once_flag`, calls `curl_global_init()`, and invokes `rgw_setup_saved_curl_handles()`. `cleanup_curl()` releases saved handles and calls `curl_global_cleanup()`.

## Control Flow and Data Flow

Startup computes `CURL_GLOBAL_ALL`, optionally installs legacy OpenSSL locking callbacks, initializes curl once, and starts the handle cleaner thread. Cleanup flushes the handle pool and deinitializes curl globals. Frontend configuration is read only to decide legacy SSL ownership.

## State and Persistence Behavior

The module holds process-global curl initialization state through `curl_init_flag`; this cannot be reset after cleanup. Saved easy handles are managed by the companion HTTP client implementation. No persistent storage is modified.

## Dependencies and Integration Points

Dependencies are libcurl, optional OpenSSL crypto APIs, `rgw_frontend.h`, and the HTTP handle-pool functions in `rgw_http_client.cc`. It integrates with RGW process startup paths that configure frontends before outbound HTTP use.

## Risks and Edge Cases

The once-only init flag means repeated setup/cleanup cycles in one process may not behave like a fresh init. Legacy OpenSSL callback paths are compile-condition sensitive. Beast SSL detection is frontend-name specific. Cleanup order matters because active HTTP requests or saved handles must be gone before `curl_global_cleanup()`.

## Test Signals

Tests should cover setup/cleanup in curl/OpenSSL build variants, frontend maps with and without Beast SSL certificate configuration, repeated setup calls, cleanup after idle handle creation, and legacy OpenSSL callback installation where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_http_client_curl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_http_client_curl.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_http_client_curl.h

## Purpose

`rgw_http_client_curl.h` declares the small setup/cleanup interface for RGW's curl subsystem and the frontend map type used during initialization.

## Important APIs, Types, and Functions

`rgw::curl::fe_map_t` is a `std::multimap<std::string, RGWFrontendConfig*>` matching RGW frontend configuration containers. `setup_curl(boost::optional<const fe_map_t&>)` initializes curl/OpenSSL support and the saved easy-handle pool. `cleanup_curl()` tears those resources down.

## Control Flow and Data Flow

Callers pass optional frontend configuration into setup; the implementation may inspect it to decide SSL initialization behavior. No request data flows through this header.

## State and Persistence Behavior

The header declares process-global lifecycle operations only. All state lives in the implementation and libcurl/OpenSSL globals.

## Dependencies and Integration Points

It depends on `boost::optional` and `rgw_frontend.h`. It integrates with RGW startup/shutdown code and with `rgw_http_client.cc` via the saved-handle pool functions.

## Risks and Edge Cases

The API is intentionally global, so callers must coordinate it with all HTTP client use. Passing dangling frontend config pointers would be unsafe during setup inspection.

## Test Signals

Build coverage should include users that call setup with `boost::none` and with a frontend map. Lifecycle tests should verify that cleanup is paired with setup and occurs after HTTP manager shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_http_client_curl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_http_client_types.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_http_client_types.h

## Purpose

`rgw_http_client_types.h` defines lightweight I/O identity helpers shared by HTTP clients and completion machinery. The goal is to correlate related read, write, and control activities for a logical request.

## Important APIs, Types, and Functions

`rgw_io_id` contains an integer request id and a channel bitmask. It implements ordering for map/set use and `intersects()` for detecting same-id overlapping channel activity. `RGWIOIDProvider` atomically allocates monotonically increasing ids with `get_next()`. `RGWIOProvider` stores one id per provider, assigns it lazily via `assign_io()`, returns channel-specific `rgw_io_id` values, and requires subclasses to expose `set_io_user_info()`/`get_io_user_info()`.

## Control Flow and Data Flow

A manager or caller gives an `RGWIOProvider` an `RGWIOIDProvider`; the provider keeps the first assigned id and ignores later assignments. Callers then request typed ids such as HTTP read/write/control and pass optional user info through completion callbacks.

## State and Persistence Behavior

State is in memory only. `RGWIOIDProvider::max` is atomic process-local state; `RGWIOProvider::id` is per-object state. No storage or wire format is involved.

## Dependencies and Integration Points

The file depends only on `<atomic>`. `RGWHTTPClient` inherits `RGWIOProvider`, and `RGWHTTPManager` uses `HTTPCLIENT_IO_CONTROL` ids for completion manager notifications.

## Risks and Edge Cases

`intersects()` uses `(channels | rhs.channels) != 0`; that checks whether either channel mask is nonzero rather than whether masks overlap, so readers must understand its actual behavior. The initial `id` value is `-1`, while `assign_io()` only assigns when `id == 0`, so construction/assignment expectations need validation in callers.

## Test Signals

Unit tests should cover monotonic id allocation, ordering, channel retrieval, repeated assignment behavior, and the exact `intersects()` semantics for same/different ids and zero/nonzero channel masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_http_client_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_http_errors.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_http_errors.h

## Purpose

`rgw_http_errors.h` declares RGW HTTP error mapping tables and provides a common helper for translating HTTP response codes to negative Ceph/Linux errno-style return values.

## Important APIs, Types, and Functions

`rgw_http_errors` aliases the constant map type used by S3, Swift, STS, and IAM error tables declared as externs. `rgw_http_error_to_errno(int http_err)` treats 2xx responses as success and maps selected status codes: 304 to `-ERR_NOT_MODIFIED`, 400 to `-EINVAL`, 401 to `-EPERM`, 403 to `-EACCES`, 404 to `-ENOENT`, 405 to `-ERR_METHOD_NOT_ALLOWED`, 409 to `-ENOTEMPTY`, and 503 to `-EBUSY`. Other statuses become `-ERR_INTERNAL_ERROR`.

## Control Flow and Data Flow

The helper is called after curl completion in the HTTP manager. The HTTP status code flows into local request completion as the errno-like status returned to callers.

## State and Persistence Behavior

The header has no mutable state. External maps are defined elsewhere and persist as static program data.

## Dependencies and Integration Points

It depends on `rgw_common.h` for RGW-specific error constants. It integrates directly with `rgw_http_client.cc` and indirectly with all outbound HTTP users.

## Risks and Edge Cases

Many HTTP statuses collapse to internal error, so callers needing retryability or specific behavior must either inspect `http_status` separately or extend the map. 3xx codes other than 304 are treated as internal errors, which may be surprising if redirects are encountered.

## Test Signals

Tests should assert exact mappings for success, known client/server statuses, unknown 3xx/4xx/5xx statuses, and compatibility with request code paths that separately store the raw HTTP status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_http_errors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_iam_managed_policy.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_iam_managed_policy.cc

## Purpose

`rgw_iam_managed_policy.cc` embeds a small supported set of AWS managed IAM policy documents and exposes lookup/serialization helpers for RGW IAM policy attachment.

## Important APIs, Types, and Functions

The file defines static JSON policy text for `IAMFullAccess`, `IAMReadOnlyAccess`, `AmazonSNSFullAccess`, `AmazonSNSReadOnlyAccess`, `AmazonS3FullAccess`, and `AmazonS3ReadOnlyAccess`. `get_managed_policy(CephContext*, std::string_view arn)` compares an input ARN against those exact managed-policy ARNs and returns a parsed `rgw::IAM::Policy` in `std::optional`. `encode()` and `decode()` serialize `ManagedPolicies::arns` with Ceph's versioned encoding macros.

## Control Flow and Data Flow

Managed policy resolution is a fixed if/else chain: ARN in, parsed `Policy` out, empty optional on unsupported ARN. Embedded JSON flows through the normal IAM policy parser, so the same action wildcard expansion and resource validation apply. Attached managed policy ARN sets flow to and from `bufferlist` for persistence in RGW metadata.

## State and Persistence Behavior

Policy JSON is compile-time static data. The persistent state is the serialized set of attached ARNs in `ManagedPolicies`; actual policy documents are reconstructed by lookup rather than stored per attachment.

## Dependencies and Integration Points

The file depends on `rgw_iam_policy.h` for parsing/evaluation and Ceph `bufferlist` encoding. It integrates with RGW IAM user/role/group managed policy attachment code.

## Risks and Edge Cases

Only the listed AWS managed policies are recognized; unsupported valid AWS ARNs return empty optional. Embedded policies can become stale relative to AWS. Parse failures from changes in `rgw_iam_policy` would surface at lookup time. Tenant is null and invalid principals are not rejected, matching AWS-managed global policy behavior.

## Test Signals

Tests should cover every supported ARN, unsupported ARN behavior, successful parse/evaluation of wildcard actions, encode/decode round trips for multiple ARNs, and compatibility when stored attachments reference no-longer-supported names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_iam_managed_policy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_iam_managed_policy.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_iam_managed_policy.h

## Purpose

`rgw_iam_managed_policy.h` declares the managed-policy lookup API and the serializable container used to persist attached managed policy ARNs.

## Important APIs, Types, and Functions

`get_managed_policy(CephContext*, std::string_view arn)` returns `std::optional<Policy>` for a supported managed policy ARN. `ManagedPolicies` contains a `boost::container::flat_set<std::string> arns`, giving deterministic, unique storage of attached ARN strings. Free `encode()` and `decode()` functions integrate the type with Ceph serialization.

## Control Flow and Data Flow

Callers store just ARNs in `ManagedPolicies`, then resolve each ARN to a concrete `Policy` when evaluating permissions. Serialization passes the ARN set through Ceph's `bufferlist` API.

## State and Persistence Behavior

The type is persistent when embedded in user/role/group metadata. The policy documents themselves are not persisted in this struct.

## Dependencies and Integration Points

The header forward-declares `Policy`, includes `CephContext`, `buffer_fwd`, and Boost flat set, and is used by IAM metadata and permission evaluation paths.

## Risks and Edge Cases

Because only ARNs are persisted, behavior can change if the embedded implementation of a managed policy changes. The flat set removes duplicates silently, which is desirable for attachment semantics but should be expected by callers.

## Test Signals

Tests should verify duplicate suppression, binary encoding compatibility, empty-set behavior, lookup integration, and failure handling for ARNs that remain stored but are not supported by `get_managed_policy()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_iam_managed_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_iam_policy.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_iam_policy.cc

## Purpose

`rgw_iam_policy.cc` implements parsing, validation, formatting, condition evaluation, principal matching, action-string mapping, and full policy evaluation for RGW IAM/S3/STS/SNS/Organizations policies.

## Important APIs, Types, and Functions

`actpairs[]` maps AWS action strings and wildcard-matchable patterns to action bit positions declared in the header. `PolicyParser` is a RapidJSON SAX handler with a stack of `ParseState` objects and a generated keyword hash from `rgw_iam_policy_keywords.frag.cc`. `ParseState::do_string()` handles versions, effects, principals, actions/notactions, resources/notresources, conditions, and runtime interpolation values. `Condition::eval()` implements string, numeric, date, bool, binary, IP, ARN, Null, ForAny, ForAll, and IfExists semantics. `Statement::eval()` checks principal, resource, action/notaction, and all conditions. `Policy::eval()` applies explicit deny precedence and allow/pass aggregation. `is_public()` detects wildcard-allow statements whose conditions pass against a representative environment.

## Control Flow and Data Flow

Policy text is parsed with RapidJSON using comments and numbers-as-strings flags. Parser callbacks enforce legal keyword context, duplicate constraints, array/object allowance, tenant-owned resources, principal syntax, and NotPrincipal restrictions. Evaluation receives an environment multimap, optional identity, action bit, optional resource ARN, and optional output principal type. Data flows through statement checks in AWS order: principal/resource/action/conditions, with explicit deny returning immediately.

## State and Persistence Behavior

The file creates immutable in-memory `Policy` objects from stored JSON text. It does not persist directly, but the original `Policy::text` and parsed vectors/sets drive later authorization decisions. Runtime condition interpolation reads values from the request environment.

## Dependencies and Integration Points

Dependencies include RapidJSON, RGW auth principals/identities, ARN parsing/matching, wildcard helpers, ISO8601 parsing, bufferlist base64 decode, and generated IAM keyword tables. It is central to bucket policies, IAM identity policies, STS trust policies, managed policies, and public-access checks.

## Risks and Edge Cases

This is security-critical. Risks include action table omissions, wildcard expansion mistakes, condition semantics diverging from AWS, tenant resource validation bypasses, invalid-principal compatibility mode, `Allow` with `NotPrincipal` rejection, runtime interpolation edge cases, IP/netmask comparison, and deny/allow/pass precedence bugs. The parser accepts comments, which may differ from strict JSON expectations.

## Test Signals

Tests should include valid/invalid policy grammar, duplicate keys, every effect/version/principal type, wildcard and service-wide actions, action-to-bit mapping, tenant resource validation, explicit deny precedence, NotAction/NotResource, all condition operator families, IfExists/Null missing-key behavior, runtime `${...}` interpolation, IPv4/IPv6 CIDR matching, ARN condition matching, public-policy detection, and backwards invalid-principal handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_iam_policy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_iam_policy.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_iam_policy.h

## Purpose

`rgw_iam_policy.h` defines RGW IAM policy's public data model: action bit positions, permission mapping, environment representation, condition helpers, statements, parse exceptions, and policy evaluation APIs.

## Important APIs, Types, and Functions

The large anonymous enum assigns stable bit indexes for S3, S3 Object Lambda, IAM, STS, SNS, Organizations, and aggregate `*All` actions. `Action_t`/`NotAction_t` are `std::bitset<allCount>`, with constexpr helpers building service-wide masks. `op_to_perm()` maps selected S3 actions to legacy RGW ACL permission bits. `Environment` is an `unordered_multimap<string,string>`. `MaskedIP` and `Condition` provide typed conversions and matcher helpers. `Statement` stores principals, effect, action/notaction masks, resource/notresource ARN sets, and conditions. `Policy` parses text in its constructor and exposes `eval()`, `eval_principal()`, `eval_conditions()`, and conditional-inspection helpers.

## Control Flow and Data Flow

Callers construct `Policy` from JSON text, then evaluate request context by action bit and optional resource/identity. Conditions convert request/environment strings into typed values only during evaluation, preserving AWS's loosely typed policy values.

## State and Persistence Behavior

`Policy` stores the original text and parsed structures in memory. The header defines no direct encoding; policies are typically stored elsewhere as JSON text. `ManagedPolicies` stores policy ARNs separately.

## Dependencies and Integration Points

The header depends on Boost containers/optional, RapidJSON errors, Ceph time/buffer helpers, RGW ACL permission constants, ARN, auth identity forward declarations, IAM keywords, and string matching utilities. It bridges IAM policies with legacy S3 ACL permission concepts via `op_to_perm()`.

## Risks and Edge Cases

Action enum order is a compatibility-sensitive contract because bit positions drive parsing/evaluation and string conversion. The constexpr bitmask helpers assume service ranges are contiguous. Typed conversions intentionally skip invalid comparison values, which can affect condition outcomes. `PolicyPrincipal` classification is output-sensitive for role/session matching.

## Test Signals

Tests should cover action enum/string parity, aggregate mask construction, `op_to_perm()` documentation parity, `Condition` typed conversions, multimap any/all/none helpers, `MaskedIP` equality, policy construction failures with `PolicyParseException`, and conditional key/value inspection helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_iam_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_iam_policy_keywords.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_iam_policy_keywords.h

## Purpose

`rgw_iam_policy_keywords.h` defines token categories and token ids used by the generated IAM policy keyword hash and parser state machine.

## Important APIs, Types, and Functions

`TokenKind` separates pseudo, top-level, statement, condition-operator, condition-key, version, effect, and principal-type tokens. `TokenID` enumerates policy grammar elements such as `Version`, `Statement`, `Principal`, `Action`, condition operators, dynamic `CondKey`, version constants, effects, and principal subtypes. `Version`, `Effect`, and `Type` are smaller semantic enums used by parsed policies and conditions.

## Control Flow and Data Flow

The parser receives JSON keys/values, looks them up in the generated keyword hash, then uses `TokenKind`/`TokenID` to decide which contexts accept them and which parsed fields to populate.

## State and Persistence Behavior

The file is static compile-time metadata only. Parsed policies persist the `Version`, `Effect`, and condition operator `TokenID` values in memory.

## Dependencies and Integration Points

It is included by `rgw_iam_policy.h` and the implementation that includes the generated `rgw_iam_policy_keywords.frag.cc`. It must stay synchronized with the generated keyword table and parser switch statements.

## Risks and Edge Cases

Adding a condition operator or principal type requires updates in several places: keyword generation, parse context rules, condition evaluation, printing, and tests. Condition keys are runtime strings via `CondKey`; the disabled static-key block documents older/static expectations but is not active.

## Test Signals

Tests should compile the generated keyword fragment against this enum, parse every named token, verify valid/invalid context errors, and exercise every `Effect`, `Version`, and condition operator value through parsing and evaluation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_iam_policy_keywords.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_jsonparser.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_jsonparser.cc

## Purpose

`rgw_jsonparser.cc` is a standalone JSON parser/decode utility for RGW data structures. It reads JSON from stdin, displays top-level and selected child nodes, decodes RGW user info, and dumps the decoded object as formatted JSON.

## Important APIs, Types, and Functions

`dump_array(JSONObj*)` prints the data values of array children. Local `Key` and `UserInfo` structs demonstrate `decode_json()` methods for primitive fields and lists, though the main path decodes into `RGWUserInfo`. `main()` drives `JSONParser::parse()`, `JSONObjIter`, `JSONDecoder::decode_json()`, and `JSONFormatter`.

## Control Flow and Data Flow

The program reads stdin in 1024-byte chunks and feeds each chunk to the incremental parser. At EOF it iterates all parsed root children, optionally drills into a `conditions` object, then attempts to decode the entire parser into `RGWUserInfo` and dumps the result.

## State and Persistence Behavior

All state is process-local and temporary. It does not write persistent files or RGW metadata; output goes to stdout/stderr.

## Dependencies and Integration Points

It depends on Ceph JSON helpers, formatter APIs, RGW common/user types, and standard stdio/stdout streams. It is best understood as a developer/test tool rather than production RGW server code.

## Risks and Edge Cases

The local `bufferlist bl` is appended only at EOF and otherwise unused. Parse errors are reported but do not immediately abort; later decode may throw and exit. The comment notes an uncaught-exception pattern at root scope. Large or malformed input depends on parser behavior rather than defensive utility logic.

## Test Signals

Useful signals are successful parsing of representative RGW user JSON, graceful messages for malformed JSON, decoding failures for missing fields, array dumping under `conditions`, and formatter output matching `RGWUserInfo::dump()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_jsonparser.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kafka.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_kafka.cc

## Purpose

`rgw_kafka.cc` implements RGW notification publishing to Kafka using librdkafka. It manages producer connections, security configuration, an asynchronous message queue, delivery callbacks, idle connection cleanup, and process-global manager accessors.

## Important APIs, Types, and Functions

`connection_id_t` equality/hash includes broker list, user/password, CA, mechanism, SSL flags, client cert/key, and key password so distinct security endpoints get distinct producers. `connection_t` owns `rd_kafka_t`, cached topic handles, delivery callback tags, status, config values, and idle timestamp. `new_producer()` builds librdkafka configuration for plaintext, SSL, SASL_PLAINTEXT, SASL_SSL, CA verification, mTLS, timeouts, batch/message size, log callbacks, and delivery callbacks. `message_callback()` translates delivery results and fires user callbacks. `Manager` owns connections, a lock-free fixed-size message queue, counters, limits, and runner thread.

## Control Flow and Data Flow

`connect()` parses endpoint authority, merges credentials from URL and topic attributes, enforces no cleartext secrets unless configured, validates mTLS pair presence, optionally appends extra brokers, reuses or creates a producer, and returns a connection id. `publish()` enqueues a heap message wrapper. The runner drains queued messages, creates/reuses topics, calls `rd_kafka_produce()`, tracks callback tags, polls producers for acks, deletes idle connections, and sleeps when idle.

## State and Persistence Behavior

State is process-local: singleton `s_manager`, connection map, topic cache, callback vector, queued/dequeued counters, and in-flight callbacks. Kafka broker delivery is the persistent external effect. No RGW metadata is stored here.

## Dependencies and Integration Points

Dependencies include librdkafka, RGW URL parsing, Ceph config/logging/time, Boost hashing and lock-free queue. It integrates with bucket notification code that initializes the manager, connects endpoints, publishes events, and inspects counters/limits.

## Risks and Edge Cases

Security risks include credential logging/handling and cleartext SASL opt-in. Concurrency risks include connection iterator validity assumptions, callback vector access from poll thread, manager shutdown while publishers hold shared locks, and queue ownership. Delivery callback overflow returns `-EBUSY` to the caller callback after production has already succeeded, so later broker ack is unsolicited. Idle cleanup destroys connections and invokes pending callbacks with status-derived errno.

## Test Signals

Tests should cover URL/credential precedence, SSL/SASL/mTLS config, verification off/on, max connection/queue/inflight limits, unknown topic and timeout errors, callback success/failure paths, publish without callback, idle deletion, shutdown cleanup, and metrics for connection count/inflight/queued/dequeued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kafka.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kafka.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_kafka.h

## Purpose

`rgw_kafka.h` declares RGW's Kafka notification client API: manager lifecycle, endpoint connection, asynchronous publish, confirmed publish, status conversion, and runtime counters.

## Important APIs, Types, and Functions

`reply_callback_t` is a `std::function<void(int)>` receiving errno-style completion. `connection_id_t` captures all attributes that define a reusable producer: broker, credentials, CA, mechanism, SSL verification, client certificate/key, and key password. `init()`/`shutdown()` manage the global manager. `connect()` resolves an endpoint and returns a `connection_id_t`. `publish()` queues fire-and-forget messages; `publish_with_confirm()` queues messages with delivery callback. Counter APIs expose current connection count, in-flight callbacks, queued/dequeued counters, and configured maxima.

## Control Flow and Data Flow

Callers initialize once, connect a topic endpoint to get a connection id, then publish messages by connection id and topic. Callback results flow asynchronously from the manager thread.

## State and Persistence Behavior

The header declares in-memory manager state only. Kafka delivery is external; no source-level persistence is defined here.

## Dependencies and Integration Points

It depends on Ceph forward declarations, Boost optional, and STL strings/functions. It is used by RGW notification modules that abstract endpoint type-specific publishing.

## Risks and Edge Cases

`connection_id_t` includes secrets, so stringification and hashing must avoid accidental disclosure beyond the implementation's `broker:user` summary. Callers must handle `-ESRCH` when the manager is not initialized or already shut down and `-EBUSY` when queues are full.

## Test Signals

API-level tests should cover manager not initialized, duplicate init, connection-id equality for security variations, fire-and-forget publish, confirmed callback publish, and counter values before and after shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kafka.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_keystone.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_keystone.cc

## Purpose

`rgw_keystone.cc` implements Keystone token utilities, admin/Barbican token acquisition over RGW HTTP, token parsing, role annotation, token caching, and JSON serialization of Keystone auth requests.

## Important APIs, Types, and Functions

`rgw_is_pki_token()` detects PKI tokens by prefix and `rgw_get_token_id()` MD5-hashes PKI tokens for cache keys. `CephCtxConfig` normalizes Keystone endpoint URL and reads admin password from config or a secret file. `Service::get_admin_token()` uses `TokenCache` then `issue_admin_token_request()`. `Service::get_keystone_barbican_token()` mirrors that for Barbican credentials. `TokenEnvelope::parse()` decodes Keystone JSON into token, user, project, domain, roles, and optional application credential. `TokenCache` stores normal and service token maps with LRU lists and max size. `AdminTokenRequest::dump()` and `BarbicanTokenRequest::dump()` emit Keystone v3 password-scope request JSON.

## Control Flow and Data Flow

Token acquisition builds JSON, posts to `v3/auth/tokens` using `RGWHTTPTransceiver`, captures `X-Subject-Token`, handles unauthorized status before parse, parses the response body, and caches the envelope. Cache lookup removes expired entries, refreshes LRU position, and increments Keystone cache perf counters. Invalidate removes tokens by id.

## State and Persistence Behavior

State is process-local cache data keyed by token id, plus stored admin and Barbican token ids. Secret file contents are read on demand and trimmed. No tokens are persisted by this file, but outbound requests and cached token ids are security-sensitive runtime state.

## Dependencies and Integration Points

Dependencies include RGW HTTP client, Ceph JSON/Formatter, MD5 helper, ISO8601 time parsing, RGW perf counters, config options, and Keystone scope/token classes. It integrates with RGW Keystone authentication engines, Barbican/KMS integration, and role authorization checks.

## Risks and Edge Cases

Security-sensitive risks include MD5 use only for non-cryptographic cache ids, secret-file trimming on empty file (`s.back()`), token expiration clock skew, missing `X-Subject-Token`, malformed Keystone JSON, unauthorized handling differences, wildcard role matching with `fnmatch`, and cache invalidation missing service-token maps. Static endpoint string normalization may not reflect runtime config changes.

## Test Signals

Tests should cover PKI/UUID token id handling, endpoint slash normalization, password file and direct config precedence, admin and Barbican request JSON, unauthorized and malformed responses, role admin/reader updates, token expiry/LRU eviction, invalidate/admin invalidate, service-token cache paths, and perf hit/miss increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_keystone.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_keystone.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_keystone.h

## Purpose

`rgw_keystone.h` declares RGW's Keystone authentication support types: configuration abstraction, token service helpers, token envelope model, LRU token cache, and request serializers.

## Important APIs, Types, and Functions

Top-level helpers detect PKI tokens and derive token ids. `Config` abstracts endpoint/admin credentials; `CephCtxConfig` binds it to global Ceph config. `Service::RGWKeystoneHTTPTransceiver` is an HTTP transceiver that captures `X-Subject-Token` and applies Keystone SSL verification config. `TokenEnvelope` models domain, project, token, role, user, and optional application credential; it exposes identity/project/domain accessors, `expired()`, `parse()`, and `update_roles()`. `TokenCache` is a singleton-per-config cache with normal/service maps, LRU lists, admin/Barbican shortcuts, add/find/invalidate operations, and a shutdown flag. `AdminTokenRequest` and `BarbicanTokenRequest` dump JSON.

## Control Flow and Data Flow

Authentication engines use config to request tokens, parse JSON into `TokenEnvelope`, classify roles, then cache envelopes by token id. Later auth paths look up token envelopes and check expiry before using them.

## State and Persistence Behavior

`TokenCache` holds process-local token maps and LRU state sized by `rgw_keystone_token_cache_size`. The header does not define persistent encoding; Keystone identity data is runtime authentication state.

## Dependencies and Integration Points

It depends on RGW common/HTTP, Ceph mutex/time/global config, optional/yield support, and JSON decode/dump functions implemented elsewhere. It integrates with Keystone auth engines and `rgw_keystone_scope` through `TokenEnvelope`.

## Risks and Edge Cases

Singleton caches are tied to template config type and global context. Callers must not treat cached tokens as valid without expiry checks, which `find_locked()` handles. The transceiver returns an empty static string for missing subject tokens, so callers must validate parse result.

## Test Signals

Build/API tests should cover mock `Config` implementations, token envelope decode for project/user/roles/app credentials, cache singleton access, find/add/invalidate behavior, admin and Barbican shortcuts, and HTTP transceiver header capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_keystone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_keystone_scope.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_keystone_scope.cc

## Purpose

`rgw_keystone_scope.cc` implements JSON dumping and construction of `ScopeInfo`, the compact Keystone authorization-scope record used for logging/auditing.

## Important APIs, Types, and Functions

`ScopeInfo::dump(Formatter*)` emits a `keystone_scope` object containing project, optional user, optional roles, and optional application credential sections. `build_scope_info(CephContext*, const TokenEnvelope&)` checks `rgw_keystone_scope_enabled`, copies project/domain ids, conditionally includes names and user based on `rgw_keystone_scope_include_user`, conditionally includes role names based on `rgw_keystone_scope_include_roles`, and includes app credential id/name/restricted when present.

## Control Flow and Data Flow

Keystone token data flows from `TokenEnvelope` into a `ScopeInfo` value only when scope logging is enabled. The dump path serializes the already built structure for file/socket-style log output.

## State and Persistence Behavior

The implementation creates transient scope values. Persistent behavior is defined by callers that encode `ScopeInfo` into RADOS logs or emit formatted logs. Configuration controls how much identity data is included.

## Dependencies and Integration Points

It depends on `rgw_keystone_scope.h`, `rgw_keystone.h`, `CephContext`, and `Formatter`. It integrates with authentication and operation logging code that wants Keystone project/user/role context.

## Risks and Edge Cases

Privacy and payload-size behavior depends on config: enabling names/user/roles can expose identity details in logs. `include_user` also controls project/domain names, not only user fields. App credential id and restricted flag are included even when names are suppressed.

## Test Signals

Tests should cover disabled scope returning nullopt, ids-only output, include-user names/user output, include-roles output, app credential output, and formatter structure for absent optional fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_keystone_scope.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_keystone_scope.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_keystone_scope.h

## Purpose

`rgw_keystone_scope.h` defines the serializable Keystone scope data model used to carry project, user, role, and application-credential context into logs and RADOS-backed records.

## Important APIs, Types, and Functions

`ScopeInfo` contains nested `domain_t`, `project_t`, `user_t`, and `app_cred_t` structs, each with versioned Ceph `encode()`/`decode()`. The top-level fields are required `project`, optional `user`, vector `roles`, and optional `app_cred`. Inline free `encode()`/`decode()` wrappers make nested/optional types visible to Ceph templates. Top-level `ScopeInfo::encode()`/`decode()` serialize all fields under version 1. `dump()` and `build_scope_info()` are declared.

## Control Flow and Data Flow

Callers build `ScopeInfo` from a token, then either encode it into a `bufferlist` for RADOS-style persistence or dump it as JSON through a formatter. Decode reverses persisted binary state back into the same structure.

## State and Persistence Behavior

This header defines a persistent wire/storage format with `ENCODE_START(kEncV, kEncV, ...)` for all nested types and the top-level type. Any future field changes need versioning care.

## Dependencies and Integration Points

It depends on Ceph buffer/encoding helpers and forward-declared `TokenEnvelope`. It integrates with Keystone auth code, operation logging, and any backend storing scope data.

## Risks and Edge Cases

Changing nested struct order or version constants can break decode compatibility. Optional encoding requires the free wrapper functions to remain visible. The comments state privacy controls, but enforcement lives in `build_scope_info()`, not the type itself.

## Test Signals

Tests should cover encode/decode round trips for ids-only, user-present, roles-present, app-credential-present, and all-fields cases; dump output; and backward compatibility if future versions are introduced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_keystone_scope.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kmip_client.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_kmip_client.cc

## Purpose

`rgw_kmip_client.cc` provides the public request lifecycle for RGW KMIP operations and the global KMIP manager pointer used by transceivers.

## Important APIs, Types, and Functions

`RGWKMIPTransceiver::send()` submits the request to `rgw_kmip_manager`. `process()` combines send and wait. `wait()` blocks on the request condition variable until `done` and returns `ret`. The destructor frees `out`, each string in `outlist`, and zeroizes/frees `outkey->data`. `rgw_kmip_client_init(RGWKMIPManager&)` stores the global manager reference and starts it. `rgw_kmip_client_cleanup()` stops and deletes the manager.

## Control Flow and Data Flow

Callers create a transceiver, fill operation-specific inputs such as name or unique id, call `process()` or `send()`/`wait()`, then read outputs. The implementation manager later marks `done`, sets `ret`, and signals the condition variable.

## State and Persistence Behavior

State is in-memory request input/output buffers and the global manager pointer. The key material output path is treated as sensitive and zeroized on destruction. No persistent storage is modified here.

## Dependencies and Integration Points

It depends on Ceph threading/error helpers, RGW coroutine blocking warnings, and `RGWKMIPManager` implementations such as `RGWKMIPManagerImpl`. It integrates with RGW crypt/KMS code that needs create/locate/get operations against a KMIP server.

## Risks and Edge Cases

`wait()` does not implement coroutine suspension despite taking `optional_yield`. Global manager ownership is strict: cleanup deletes the manager pointer it was handed. Input `name`/`unique_id` ownership is not freed here, while output ownership is. Shutdown failures can leave callers with manager-specific error codes.

## Test Signals

Tests should cover send failure without manager/start, blocking wait wakeup, destructor cleanup for each output shape, key zeroization, process success/failure, and cleanup ownership of a concrete manager.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kmip_client.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kmip_client.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_kmip_client.h

## Purpose

`rgw_kmip_client.h` declares RGW's KMIP client request object and abstract manager interface for external key-management operations.

## Important APIs, Types, and Functions

`RGWKMIPTransceiver` supports operations `CREATE`, `LOCATE`, `GET`, `GET_ATTRIBUTES`, `GET_ATTRIBUTE_LIST`, and `DESTROY`. It carries input fields `name` and `unique_id`, output fields `out`, `outlist`, and `outkey`, result `ret`, completion flag, mutex, and condition variable. It exposes `send()`, `wait()`, and `process()`. `RGWKMIPManager` is an abstract base with `start()`, `stop()`, and `add_request()`. Global init/cleanup functions bind a manager implementation.

## Control Flow and Data Flow

Callers populate operation inputs and submit through the manager. A background implementation processes KMIP protocol requests and fills the relevant output union-like fields before signalling completion.

## State and Persistence Behavior

The request object owns output allocations after completion and frees them in the destructor. It does not itself persist keys; persistence is on the KMIP server side.

## Dependencies and Integration Points

The header assumes Ceph context, mutex, condition variable, and optional yield declarations are available through surrounding includes. It is implemented by `rgw_kmip_client.cc` and `rgw_kmip_client_impl.cc` and used by RGW crypt/KMS code.

## Risks and Edge Cases

The output layout is manual C-style ownership, so callers must respect object lifetime. Some declared operations are not fully implemented in the current manager implementation. `name` and `unique_id` are raw mutable pointers with external ownership.

## Test Signals

API tests should construct each operation type, verify manager mock submission, output cleanup, key buffer cleanup, and error propagation through `ret`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kmip_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kmip_client_impl.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_kmip_client_impl.cc

## Purpose

`rgw_kmip_client_impl.cc` implements the concrete KMIP manager, worker thread, TLS/KMIP handle construction and pooling, and request encoding/decoding for selected KMIP operations.

## Important APIs, Types, and Functions

`RGWKmipHandle` stores SSL context/BIO, KMIP context, credentials, encoding buffer metadata, and reusable connection state. `RGWKmipHandleBuilder` configures TLS client cert/key, CA path, host/port, username/password credentials, creates `BIO_new_ssl_connect()`, connects, initializes KMIP protocol state, allocates encoding buffers, and installs credentials. `RGWKmipHandles` pools connected handles and reclaims idle ones. `RGWKMIPManagerImpl` starts/stops `RGWKmipWorker` and queues intrusive `Request` nodes. `RGWKmipHandles::do_one_entry()` builds KMIP request messages for create/get/locate, sends them over BIO, decodes responses, validates result/operation, and copies outputs into `RGWKMIPTransceiver`.

## Control Flow and Data Flow

Requests are pushed under manager lock and the worker is signalled. The worker owns a handle pool, pops requests, processes them outside the queue lock, then signals the request condition. Create sends AES-256 symmetric-key attributes plus optional name. Locate sends attributes. Get sends optional unique id and expects a raw symmetric key response. Responses copy unique ids and key bytes into caller-owned transceiver output fields.

## State and Persistence Behavior

Handle pool state is in memory and tied to configured KMIP server address and credentials. Created/destroyed keys persist on the KMIP server, not locally. Key bytes in request outputs are later zeroized by `RGWKMIPTransceiver` destructor, but intermediate KMIP buffers also need careful cleanup.

## Dependencies and Integration Points

Dependencies include OpenSSL SSL/BIO/error APIs, the C KMIP library, Ceph threads/mutex/time/config/logging, and RGW KMIP abstractions. It integrates with RGW cryptographic key management through `rgw_crypt_kmip_*` config options.

## Risks and Edge Cases

Only CREATE, LOCATE, and GET have request logic; GET_ATTRIBUTES, GET_ATTRIBUTE_LIST, and DESTROY are declared but fall through to `-EINVAL` before request send despite response decode cases existing. Request nodes allocated with `new Request` are intrusive and not visibly deleted after processing, so ownership deserves scrutiny. TLS hostname verification behavior is not explicit. `flush_kmip_handles()` calls `stop()` and `join()` even though `stop()` may already join when active. Shutdown marks pending requests with `-666`, which is not a normal errno.

## Test Signals

Tests should cover handle build failures for bad cert/key/CA/host, default port parsing, username/password credentials, buffer growth on `KMIP_ERROR_BUFFER_FULL`, create/locate/get success against a KMIP test server, non-success and operation-mismatch responses, missing server availability, unsupported operations, worker shutdown with pending requests, handle reuse/idle cleanup, and key material zeroization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kmip_client_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kmip_client_impl.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_kmip_client_impl.h

## Purpose

`rgw_kmip_client_impl.h` declares the concrete KMIP manager used by RGW to queue transceiver requests onto a worker thread.

## Important APIs, Types, and Functions

`RGWKMIPManagerImpl` derives from `RGWKMIPManager`. It owns a mutex, condition variable, intrusive `requests` list of `Request` wrappers, `going_down` flag, and `RGWKmipWorker*`. The nested `Request` stores a reference to `RGWKMIPTransceiver` and has intrusive list hooks. Public methods implement `add_request()`, `start()`, and `stop()`, with `RGWKmipWorker` as a friend.

## Control Flow and Data Flow

External callers submit transceivers through `add_request()`. The implementation pushes a request wrapper into the intrusive list and signals the worker. The worker consumes the list and writes results back to the referenced transceiver.

## State and Persistence Behavior

All state is process-local queue/worker state. Persistent key effects happen through the implementation's KMIP protocol calls, not in this header.

## Dependencies and Integration Points

It depends on Boost intrusive lists, Ceph synchronization primitives, and the abstract classes from `rgw_kmip_client.h`. It integrates with `rgw_kmip_client_init()` as the manager implementation object.

## Risks and Edge Cases

The intrusive list wrapper is heap allocated in the implementation and ownership is non-obvious from the header. Because `Request` holds a reference, submitted transceivers must remain alive until completion. `going_down` prevents new requests but callers must still handle `-ECANCELED`.

## Test Signals

Tests should cover start idempotency/error, add while running, add while stopping, worker signal behavior, pending request completion on shutdown, and lifetime assumptions for referenced transceivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_kmip_client_impl.h -->
