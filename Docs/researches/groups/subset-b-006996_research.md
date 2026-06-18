# Research: subset-b-006996

Grouped research for Ceph RGW REST client, REST connection, admin metadata/config/info/dedup endpoints, and IAM account/user/group/OIDC operations under `sources/distributed-fs/ceph/src/rgw/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_client.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_client.cc

## Purpose

`rgw_rest_client.cc` implements RGW's outbound HTTP/REST request machinery. It turns RGW request metadata, S3 object identifiers, HTTP headers, query parameters, ACLs, and bufferlists into signed HTTP requests that can be sent synchronously or through `RGWHTTPManager`. This is the low-level client used by multisite replication, remote zone forwarding, metadata forwarding, object pull/push, and helper wrappers in `rgw_rest_conn.cc`.

## Important APIs, Types, and Functions

The file defines behavior for the classes declared in `rgw_rest_client.h`: `RGWHTTPSimpleRequest`, `RGWRESTSimpleRequest`, `RGWRESTGenerateHTTPHeaders`, `RGWHTTPStreamRWRequest`, `RGWRESTStreamRWRequest`, `RGWRESTStreamS3PutObj`, and the internal `RGWRESTStreamOutCB`. The core signing helpers are `sign_request_v2()`, `sign_request_v4()`, `sign_request()`, `identify_scope()`, and `scope_from_api_name()`.

`RGWHTTPSimpleRequest` parses response headers, maps HTTP status to RGW errno with `rgw_http_error_to_errno()`, buffers bounded response data, and can stream a request body from a `bufferlist::iterator`. `RGWRESTSimpleRequest::forward_request()` rebuilds a forwarded request, signs it, applies query parameters, sends it, and returns either the remote HTTP status or a transport errno through `tl::expected<int,int>`. `RGWRESTGenerateHTTPHeaders` builds the environment and `req_info` used by RGW S3 signing code. `RGWHTTPStreamRWRequest` handles streaming request/response bodies, pause/resume, header callbacks, and embedded RGWX metadata headers.

## Control Flow

Header parsing begins in `receive_header()`: status lines update `http_status` and `status`, ordinary headers are uppercased with dash transformation and stored in `out_headers`, and an empty line calls `handle_headers()`. Simple response bodies are copied into `response` only up to `max_response`, normally learned from `CONTENT_LENGTH`.

For forwarding, `forward_request()` rebuilds `req_info`, URL-encodes the bucket component, appends this request's params, sets date and selected content headers, infers signing scope, signs with v2 or v4, appends generated headers, composes the final URL, optionally sets a request body iterator, and calls `process()`. If no HTTP status is received, it reports `-ERR_SERVICE_UNAVAILABLE`.

For streaming requests, callers must run `send_prepare()` before `send()`. `do_send_prepare()` computes path-style or virtual-host-style URL/resource layout, initializes `RGWRESTGenerateHTTPHeaders`, records an optional signing key, and attaches buffered send data. `send()` signs over the outgoing buffer when the full body is known, copies generated environment headers into the HTTP request, then queues or sends the request. `complete_request()` waits for the request, extracts `ETAG`, `RGWX_MTIME`, `RGWX_OBJECT_SIZE`, and `RGWX_ATTR_*` headers, and returns the mapped RGW status.

## State and Persistence Behavior

The file does not persist repository state directly. Runtime state lives in request objects: output headers protected by `out_headers_lock`, body buffers (`response`, `outbl`, `in_data`), signing environments (`RGWEnv` and `req_info`), stream offsets, pause flags, and optional generated headers/signing keys. These objects are short-lived per outbound HTTP operation.

The persistent effects are remote: signed requests may create or mutate objects, IAM resources, metadata, or zone state on another RGW endpoint. The code also carries object metadata across endpoints by translating RGW attrs to `x-amz-meta-*` and ACL grants to `x-amz-grant-*` headers.

## Dependencies and Integration Points

This file depends on RGW's HTTP client base, S3 auth/signing, ACL conversion, HTTP error mapping, metadata naming, Ceph bufferlists, and `req_info`/`RGWEnv`. It is consumed directly by `RGWRESTConn` and indirectly by multisite sync, IAM forwarding, remote object replication, and resource wrappers such as `RGWRESTReadResource`.

The signature path integrates with `rgw_s3_client_max_sig_ver`, AWS endpoint naming conventions, `rgw_zonegroup` fallback scope, and service-specific signing differences for S3 versus IAM. Virtual-host-style addressing rewrites both host and URL, so it must match endpoint DNS configuration.

## Risks and Edge Cases

Important risks include mismatched signing scope, especially for non-AWS endpoints, IAM forwarding, and configured `api_name`. Query parameters are encoded and merged in several places; regressions can break signatures. `RGWHTTPSimpleRequest` buffers response data rather than streaming it, so callers must set safe `max_response` values. `RGWHTTPStreamRWRequest::handle_header()` assumes `cb` is valid when `RGWX_EMBEDDED_METADATA_LEN` appears. Stream pause state and `outbl` manipulation are lock-sensitive and can deadlock if callbacks re-enter improperly.

Object paths intentionally do not encode slash characters in keys; changing that would break folder-like object names. Header case handling is also delicate: some non-`x-amz` attrs are stored in uppercase form because signing expects names such as `CONTENT_TYPE`.

## Test Signals

Useful tests include unit or integration coverage for SigV2/SigV4 generation, path-style and virtual-host-style URLs, IAM forwarding with `PayloadHash` removal, object keys containing slashes, bounded response reads, embedded RGWX metadata extraction, streaming upload pause/resume, and endpoint behavior when `process()` returns transport failure or no HTTP status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_client.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_client.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_client.h

## Purpose

`rgw_rest_client.h` declares the outbound RGW REST client abstraction. It exposes simple buffered requests, signed REST forwarding, streaming read/write requests, S3 object upload helpers, and header generation used by remote RGW connections.

## Important APIs and Types

`RGWHTTPSimpleRequest` extends `RGWHTTPClient` with HTTP status tracking, captured response headers, query parameters, optional request body iteration, bounded buffered response storage, and overrides for header/body callbacks. `RGWRESTSimpleRequest` adds an optional API name and `forward_request()` for forwarding an existing `req_info`.

`RGWRESTGenerateHTTPHeaders` is a `DoutPrefix` helper that initializes signing state and applies extra headers, RGW object attrs, HTTP attrs, ACL policy grants, and final S3 auth signatures. `RGWHTTPStreamRWRequest` adds receive callbacks, write-drain callbacks, streamed input/output buffers, pause flags, and `complete_request()` metadata extraction. `RGWRESTStreamRWRequest` wraps streaming HTTP requests with signed RGW REST URL preparation. The concrete read/head/send subclasses select HTTP methods. `RGWRESTStreamS3PutObj` specializes streaming PUT for S3 objects and object-iteration callbacks.

## Control Flow

Callers build one of the request classes, configure params and headers, and either call the simple `forward_request()` path or the streaming `send_prepare()` then `send()` path. Completion flows through `wait()` in the base HTTP layer and then file-specific extraction in `complete_request()`.

The streaming types separate URL/signing preparation from actual submission so callers can enqueue requests in an `RGWHTTPManager`, attach callbacks, and provide body chunks asynchronously through `add_send_data()` and `finish_write()`.

## State and Persistence Behavior

Objects declared here hold transient network state only: headers, buffers, offsets, callbacks, signing context, and host style. `RGWRESTStreamS3PutObj` owns and deletes its `RGWGetDataCB` callback. No class persists data locally; persistence occurs through the remote HTTP operation represented by the request.

## Dependencies and Integration Points

The declarations depend on `rgw_http_client.h`, Ceph `expected`, bufferlists, `req_info`, `RGWEnv`, ACL policy types, and `RGWHTTPManager`. They are integrated by `rgw_rest_conn.h/.cc`, multisite sync, admin forwarding, and S3 object transfer paths.

## Risks and Test Signals

The main API risks are lifecycle and ordering: streaming requests must be prepared before sending, callbacks must outlive request processing, and callers must not use deleted `RGWRESTStreamS3PutObj` pointers after `complete_request()`. Tests should compile all call sites, verify callback delivery, cover both `PathStyle` and `VirtualStyle`, and assert that `complete_request()` populates requested ETag, mtime, size, attrs, and headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_config.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_config.cc

## Purpose

`rgw_rest_config.cc` implements the admin REST endpoint that returns RGW zone configuration. It is a small handler used by authenticated admin clients that call the config resource with `type=zone`.

## Important APIs and Functions

`RGWOp_ZoneConfig_Get::send_response()` fetches `RGWZoneParams` from the RADOS-backed zone service and serializes it as JSON under `zone_params`. `RGWHandler_Config::op_get()` dispatches GET requests to `RGWOp_ZoneConfig_Get` only when the query argument `type` equals `zone`.

## Control Flow

The REST manager creates an `RGWHandler_Config`. For GET, the handler inspects `s->info.args`. A zone request constructs `RGWOp_ZoneConfig_Get`; any other type returns `nullptr` and lets higher-level REST dispatch handle the unsupported operation. The operation's `execute()` is empty because the data is already available through the driver/service layer; response generation performs the actual fetch and formatter output.

## State and Persistence Behavior

The endpoint is read-only. It does not mutate zone state. It reads zone params from `static_cast<rgw::sal::RadosStore*>(driver)->svc()->zone->get_zone_params()`, so it assumes the configured driver is the RADOS store implementation.

## Dependencies and Integration Points

The file depends on `rgw_rest_config.h`, `rgw_rest_s3.h`, `driver/rados/rgw_sal_rados.h`, and `services/svc_zone.h`. It integrates with admin auth through `RGWHandler_Auth_S3` and requires the `zone=read` capability declared in the header.

## Risks and Test Signals

The explicit RADOS-store cast is a portability risk for alternate SAL drivers. A useful test should call the authenticated config endpoint with `type=zone`, verify a 200 response containing `zone_params`, verify missing or different `type` does not dispatch this op, and verify users without `zone` read caps are rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_config.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_config.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_config.h

## Purpose

`rgw_rest_config.h` declares the authenticated admin REST config resource for RGW. Its current surface is the zone configuration GET operation.

## Important APIs and Types

`RGWOp_ZoneConfig_Get` derives from `RGWRESTOp`, requires `zone` read caps, returns the operation name `get_zone_config`, and leaves `execute()` empty because `send_response()` emits the zone params. `RGWHandler_Config` derives from `RGWHandler_Auth_S3`, dispatches GET operations, and skips extra permission loading by returning 0 from `read_permissions()`. `RGWRESTMgr_Config` creates the handler for this REST mount.

## Control Flow and Integration

The manager is asked for a handler, the handler authenticates through S3 admin auth, and `op_get()` chooses the zone-config operation based on query args. This follows the standard RGW admin REST manager/handler/op layering.

## State, Risks, and Tests

The header declares read-only behavior; state access happens in the implementation. Risks are mostly capability and dispatch correctness: wrong caps would expose zone parameters, and an overbroad `op_get()` would accept unsupported config types. Tests should cover manager creation, authenticated GET dispatch, and cap rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_conn.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_conn.cc

## Purpose

`rgw_rest_conn.cc` implements `RGWRESTConn`, the higher-level connection object that selects remote endpoints, signs requests with zone credentials, retries transient I/O failures, marks endpoints temporarily unconnectable, and exposes convenience APIs for forwarding requests, object transfer, and generic resource GET/POST/PUT/DELETE.

## Important APIs and Functions

The file implements constructors, move operations, endpoint selection (`get_url()`), failure marking (`set_url_unconnectable()`), sys-param population, request forwarding (`forward()`, `forward_iam()`), object upload/download helpers (`put_obj_*`, `get_obj()`, `complete_request()`), generic resource helpers (`get_resource()`, `send_resource()`), and the `RGWRESTReadResource`/`RGWRESTSendResource` wrapper methods.

`get_obj()` is the densest API. It maps replication and conditional-read options into query parameters and headers: `prepend-metadata`, `stat`, `sync-manifest`, `sync-cloudtiered`, `skip-decrypt`, `if-not-replicated-to`, `versionId`, permission-check uid, conditional dates, ETag match, destination zone/PG version, and byte ranges.

## Control Flow

Construction records endpoints and initializes each endpoint status to `real_clock::zero()`. With a driver, it also pulls the local zone system key and zonegroup id. `get_url()` round-robins with an atomic counter and skips endpoints marked failed in the last two seconds. If every endpoint is still marked failed, it returns `-EINVAL`.

`forward()` and `forward_iam()` try up to 20 endpoint I/O retries. They build params, create an `RGWRESTSimpleRequest`, call `forward_request()`, return successful HTTP status values, and only retry on `-EIO`. Object and resource helpers follow the same pattern: pick URL, build params and headers, prepare a streaming request, send, wait, and mark the endpoint unconnectable on `-EIO`.

`RGWRESTReadResource` and `RGWRESTSendResource` wrap a single request object for synchronous and asynchronous resource access. Their `wait()` methods decode JSON responses or expose raw bufferlists depending on template usage.

## State and Persistence Behavior

Connection state includes endpoint list, per-endpoint atomic last-failure timestamps, remote id, system credentials, self zonegroup, optional API name, host style, and atomic selection counter. The two-second failure window is in-memory only. Remote persistence occurs through forwarded object/resource/IAM requests. Local persistence is not changed except for any caller-controlled side effects of remote metadata and object sync.

## Dependencies and Integration Points

The implementation depends on `rgw_zone.h`, SAL driver zone access, `rgw_rest_client.h`, HTTP errno mapping, and object/zone types. It is an integration layer between RGW multisite metadata/object logic and the lower HTTP request classes. `S3RESTConn` in the header overrides parameter population, while the base connection injects RGW system params for admin-style remote RGW APIs.

## Risks and Edge Cases

Endpoint selection returns `-EINVAL` both for no endpoints and all endpoints temporarily failed, which can obscure failure classification. The two-second unconnectable TTL is short and may cause rapid retries against a bad endpoint under persistent failure. Several constructors for resource wrappers call `conn->get_url()` as a string and ignore a possible `get_url()` error path. Move operations copy only selected fields and do not move `api_name` or `host_style`, which is a maintenance risk if moved connections are used.

Object retrieval has many coupled flags; incorrect parameter/header translation can break multisite sync semantics. Range formatting uses signed casts from unsigned fields. Callers own request pointers until `complete_request()`, which deletes them.

## Test Signals

Tests should cover round-robin endpoint selection, endpoint failure expiry, retry-on-`-EIO` only, no-endpoint errors, forwarded IAM service signing, object GET/HEAD parameter/header construction, versioned object paths, range and conditional headers, and async wrapper `wait()` behavior with JSON decode success/failure. Multisite sync integration tests are the strongest signal because they exercise credentials, zonegroup params, and endpoint failover together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_conn.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_conn.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_conn.h

## Purpose

`rgw_rest_conn.h` declares the high-level RGW REST connection facade used to talk to remote RGW endpoints. It also defines JSON decode helpers, param-list helpers, streaming receive-to-buffer callbacks, and refcounted resource wrappers for remote resource reads and writes.

## Important APIs and Types

`parse_decode_json()` parses a `bufferlist` into a `JSONParser` and decodes it into a caller-provided object. `rgw_http_param_pair`, `append_param_list()`, and `make_param_list()` convert C-style null-terminated param arrays or maps into `param_vec_t`.

`RGWRESTConn` owns endpoint configuration, credentials, zone identity, API name, host style, and endpoint health. Public methods cover request forwarding, IAM forwarding, S3 object PUT/GET, generic resource send/get, and JSON resource fetches. `get_obj_params` centralizes optional object-transfer flags. `S3RESTConn` is a base-connection variant that suppresses RGW sys-param injection.

`RGWRESTReadResource` and `RGWRESTSendResource` are `RefCountedObject`/`RGWIOProvider` wrappers around stream requests. `RGWRESTPostResource`, `RGWRESTPutResource`, and `RGWRESTDeleteResource` select write methods.

## Control Flow

Callers create a connection from zone endpoints and credentials, then either use one-shot helpers or instantiate resource wrappers. Template helpers fetch raw data, call `parse_decode_json()`, and return typed results. Asynchronous flows call `aio_read()` or `aio_send()` and later `wait()`.

## State and Persistence Behavior

The header exposes in-memory connection state only. Endpoint status is an unordered map of atomics recording when endpoints became unconnectable. Resource wrappers hold one request, one receive callback, request params/headers, and accumulated response buffer. Persistent effects are remote and depend on the HTTP operation.

## Dependencies and Integration Points

This header depends on `rgw_rest_client.h`, Ceph JSON utilities, refcounting, SAL forward declarations, and `RGWHTTPManager`. It is included by multisite and admin code that needs remote RGW communication. The `RGWIOProvider` methods allow these requests to participate in RGW I/O accounting.

## Risks and Test Signals

Template JSON decode errors collapse to `-EINVAL`, so callers lose detailed parse diagnostics. The C-style `rgw_http_param_pair` lists require null termination. Resource wrappers contain request objects initialized from `conn->get_url()`, so construction with no valid endpoint can produce weak diagnostics. Compile-time tests should instantiate all templates used by callers; runtime tests should cover raw and typed waits, async send/read, IO provider ids, and endpoint error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_conn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_dedup.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_dedup.cc

## Purpose

`rgw_rest_dedup.cc` implements authenticated admin REST operations for RGW deduplication control. It exposes stats, throttle inspection/update, scan start, and abort/pause/resume controls by dispatching `GET` and `POST` requests under the dedup resource.

## Important APIs and Functions

The file defines internal operations: `RGWOp_Dedup_Stats`, `RGWOp_Dedup_Throttle_Get`, `RGWOp_Dedup_Scan`, `RGWOp_Dedup_Control`, and `RGWOp_Dedup_Throttle_Set`. `RGWHandler_Dedup::op_get()` maps `op=stats` and `op=throttle`; `op_post()` maps `estimate`, `exec`, `abort`, `pause`, `resume`, and `throttle`.

All operations require the RADOS SAL driver through `get_rados_store()`. Read operations check `dedup` read caps, while mutation/control operations check `dedup` write caps.

## Control Flow

Stats and throttle GET start the response flusher, then call `rgw::dedup::cluster::collect_all_shard_stats()` or `dedup_control_bl()`. Estimate and exec scans call `dedup_restart_scan()` with the selected request type. Exec additionally requires `yes-i-really-mean-it=true` and is compiled behind `FULL_DEDUP_SUPPORT`. Control operations send urgent messages to the dedup cluster code. Throttle SET parses optional `max-bucket-index-ops` and `max-metadata-ops`, encodes a throttle message, and echoes the applied control response.

## State and Persistence Behavior

This file does not maintain state itself. It triggers persistent or cluster-wide dedup state through `rgw::dedup::cluster` and encoded urgent messages. Throttle settings, scan restarts, pause/resume/abort, and stats collection are delegated to the dedup subsystem and RADOS-backed store.

## Dependencies and Integration Points

It depends on `rgw_dedup_cluster.h`, `rgw_dedup_utils.h`, `rgw_sal_rados.h`, and RGW REST auth/operation classes. It is tightly coupled to the RADOS store and returns `-EPERM` when invoked with a non-RADOS driver.

## Risks and Test Signals

The `URGENT_MSG_PASUE` spelling is used as a constant and must match the dedup subsystem. Throttle parsing casts signed `int64_t` values to `uint32_t` without explicit negative-range validation. `op=exec` is deliberately guarded by both confirmation and compile-time support. Tests should verify cap checks, non-RADOS rejection, invalid throttle values, missing throttle params, exec confirmation behavior, and each `op` dispatch path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_dedup.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_dedup.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_dedup.h

## Purpose

`rgw_rest_dedup.h` declares the authenticated admin REST handler and manager for RGW deduplication endpoints.

## Important APIs and Types

`RGWHandler_Dedup` derives from `RGWHandler_Auth_S3`, dispatches GET and POST operations, and returns 0 from `read_permissions()`. `RGWRESTMgr_Dedup` creates a dedup handler for the registered REST resource.

## Control Flow and Integration

The manager returns a handler, S3 admin auth authenticates the request, and the implementation maps query argument `op` to a dedup operation. Operation-level caps enforce read or write permission.

## State, Risks, and Tests

The header itself has no state. The main risk is overbroad handler registration because all behavior is selected by query args. Tests should verify the manager constructs `RGWHandler_Dedup`, GET/POST dispatches only known ops, and unknown ops return no operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_dedup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_iam.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_iam.cc

## Purpose

`rgw_rest_iam.cc` is the central IAM REST dispatcher and shared IAM utility implementation for RGW. It maps AWS IAM `Action` names to `RGWOp` objects, initializes IAM request handling and S3 authorization, validates IAM names/paths/ARNs, formats IAM user/group ARNs, parses forwarded AWS error responses, and forwards IAM mutations to the metadata master zone in multisite deployments.

## Important APIs and Functions

The `op_generators` map connects IAM actions to constructors from role, user policy, OIDC provider, account, user, and group files. `RGWHandler_REST_IAM::action_exists()`, `op_post()`, `init()`, and `authorize()` implement dispatch and auth. Validation helpers include `validate_iam_policy_name()`, `validate_iam_policy_arn()`, `validate_iam_user_name()`, `validate_iam_role_name()`, `validate_iam_group_name()`, and `validate_iam_path()`.

`iam_user_arn()` and `iam_group_arn()` produce IAM ARNs from RGW metadata. `parse_aws_error_response()` extracts `Code` and `Message` from XML error bodies. `forward_iam_request_to_master()` sends a signed IAM request to the master zonegroup and parses the XML response.

## Control Flow

IAM requests enter through `RGWRESTMgr_IAM::get_handler()`, which constructs `RGWHandler_REST_IAM`. `init()` marks the dialect as `iam` and sets `RGW_REST_IAM`. `authorize()` uses S3 auth. `op_post()` reads `Action`, looks it up in `op_generators`, and constructs the concrete operation, passing the saved post body for operations that may forward to a master zone.

Validation helpers are called by concrete operations during `init_processing()`. Forwarding checks whether the current site has a period and whether it is already the metadata master. If forwarding is required, it locates the master zone, selects a user access key from the authenticated user info, builds an `RGWRESTConn` to master endpoints, calls `forward_iam()`, maps the HTTP status to errno, and parses successful XML into the caller's parser.

## State and Persistence Behavior

This file owns no persistent state. It mutates request state by setting dialect/protocol flags and by removing/rewriting args in concrete callers before forwarding. Persistent changes occur in operations created by the dispatcher or on the master zone reached through forwarding.

## Dependencies and Integration Points

It integrates many IAM submodules: roles, user policies, OIDC providers, groups, users, account summary, REST connections, and zone configuration. It depends on RGW S3 auth, XML parsing, Boost string replacement, regex validation, and SAL site configuration.

## Risks and Edge Cases

The post-body member is copied by value into the handler constructor from a local buffer in `get_handler()`, so it is currently empty unless another layer fills request args independently. Forwarding chooses the first access key in `user.access_keys`; a user without keys may forward with empty credentials, relying on downstream behavior. `validate_iam_policy_arn()` checks length but not full ARN grammar. `validate_iam_path()` requires `/` or a slash-delimited printable path and may reject AWS edge cases.

Forwarded XML has `&quot;` replaced before parsing. Any new forwarded operation must strip consumed args consistently before forwarding, or signatures and action handling can diverge between zones.

## Test Signals

Tests should cover every action name in `op_generators`, unknown/missing `Action`, IAM auth flags, all name/path validation boundaries, ARN formatting for root and non-root users, XML error parsing, non-multisite no-op forwarding, master-zone no-op forwarding, and non-master forwarding with parsed success and error responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_iam.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_iam.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_iam.h

## Purpose

`rgw_rest_iam.h` declares shared IAM REST utilities, forwarding helpers, optimistic metadata write retry helpers, and the IAM handler/manager classes.

## Important APIs and Types

The validation helpers enforce IAM limits for policy names, policy ARNs, user names, role names, group names, and paths. `iam_user_arn()` and `iam_group_arn()` format metadata as AWS-style IAM ARNs. `forward_iam_request_to_master()` is the common multisite forwarding function for IAM operations.

`retry_raced_user_write()`, `retry_raced_group_write()`, and `retry_raced_role_write()` wrap atomic read-modify-write loops. They retry up to 10 times on `-ECANCELED`, reload metadata/version trackers, and map persistent races to `-ERR_CONCURRENT_MODIFICATION`.

`RGWHandler_REST_IAM` holds the auth registry and saved POST body, dispatches IAM POST actions, sets IAM protocol flags, and authorizes through S3 auth. `RGWRESTMgr_IAM` returns itself for subresources and creates IAM handlers.

## Control Flow and State

Concrete IAM operations call validation in `init_processing()`, permission helpers in `verify_permission()`, optional master forwarding in `execute()`, and retry helpers around metadata updates. The retry helpers operate on SAL user/group/role objects and their version trackers but do not persist independently.

## Dependencies and Integration Points

The header depends on RGW auth filters, REST, role, SAL, XML, concepts, and `RGWUserInfo`/`RGWGroupInfo`. It is included by IAM role, user, group, policy, OIDC, and account operation implementations.

## Risks and Test Signals

New IAM operations must use the retry helpers for versioned metadata writes or risk exposing raw `-ECANCELED`. The template helpers require invocable lambdas that are safe to repeat after metadata reload. Tests should force store races to verify retry and final 409 mapping, and compile all concrete IAM files against the shared declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_iam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_account.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_account.cc

## Purpose

`rgw_rest_iam_account.cc` implements the IAM `GetAccountSummary` operation. It returns quota and count summary entries for the authenticated account.

## Important APIs and Functions

`RGWGetAccountSummary::verify_permission()` derives the account from `s->auth.identity`, builds the account root ARN with `rgw::account::root_arn()`, and checks `iamGetAccountSummary`. `add_entry()` writes one `SummaryMap` entry with `key` and `value`. `execute()` counts account users and groups when corresponding quotas are finite, then emits XML-like formatter sections for response metadata and summary values.

## Control Flow

The IAM dispatcher constructs this operation for `Action=GetAccountSummary`. Permission verification rejects callers without an authenticated account. Execution reads the authenticated user/account metadata, optionally calls `driver->count_account_users()` and `driver->count_account_groups()`, then writes `Users`, `Groups`, `UsersQuota`, `GroupsQuota`, and `AccessKeysPerUserQuota`.

## State and Persistence Behavior

The operation is read-only. It reads account limits from the identity account and counts users/groups through the SAL driver. No metadata is stored.

## Dependencies and Integration Points

The file depends on account helpers, process environment, IAM permission evaluation, and the SAL driver counting APIs. It integrates with `rgw_rest_iam.cc` through the action map and with account quota enforcement used by user/group creation.

## Risks and Test Signals

Counts remain zero when quotas are unlimited because counting is skipped for negative limits. That may be intentional for cost but can surprise clients expecting current counts. Tests should cover permission denial, no account identity, finite and unlimited quotas, count-driver failures, and response keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_account.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_account.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_account.h

## Purpose

`rgw_rest_iam_account.h` declares the IAM account-summary operation.

## Important APIs and Types

`RGWGetAccountSummary` derives from `RGWRESTOp`, exposes `verify_permission()`, `execute()`, operation name `get_account_summary`, and op type `RGW_OP_GET_ACCOUNT_SUMMARY`. Its private `add_entry()` helper writes summary map entries.

## Control Flow, State, and Integration

The operation is created by the IAM action dispatcher for `GetAccountSummary`. It uses IAM permissions rather than admin caps and reads account state through the request identity and SAL driver. It does not mutate state.

## Risks and Test Signals

The declaration is narrow. Compile tests should verify the action map can instantiate it, and request tests should verify it is recognized as the expected op type for audit/logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_account.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_group.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_group.cc

## Purpose

`rgw_rest_iam_group.cc` implements IAM group operations for RGW: create/get/update/delete/list groups, add/remove/list group users, inline group policies, managed policy attachments, and factory functions used by the IAM dispatcher.

## Important APIs and Operations

The file defines concrete `RGWOp` classes for `CreateGroup`, `GetGroup`, `UpdateGroup`, `DeleteGroup`, `ListGroups`, `AddUserToGroup`, `RemoveUserFromGroup`, `ListGroupsForUser`, `PutGroupPolicy`, `GetGroupPolicy`, `DeleteGroupPolicy`, `ListGroupPolicies`, `AttachGroupPolicy`, `DetachGroupPolicy`, and `ListAttachedGroupPolicies`. Helpers `make_resource_name()`, `dump_iam_group()`, and local `dump_iam_user()` produce response fields.

At the bottom, factory functions such as `make_iam_create_group_op()` expose these classes to `rgw_rest_iam.cc`.

## Control Flow

Each operation follows the same pattern: `init_processing()` derives account id from the authenticated identity, validates required names, paths, policy names, policy ARNs, markers, or max items, and loads group/user metadata through the SAL driver. `verify_permission()` builds an IAM ARN for the group or user and checks the specific IAM action. Mutation operations forward to the metadata master when `site.is_meta_master()` is false, then apply local changes.

Create checks the account's `max_groups` quota, generates a UUID group id and tenant, optionally forwards to master to reuse the master-generated id, and stores the group exclusively. Update uses `retry_raced_group_write()` to change path/name. Delete verifies on the master that inline policies, managed policies, and users are removed before deleting. Membership operations update `RGWUserInfo::group_ids` through `retry_raced_user_write()`. Listing operations stream or format IAM XML response sections with truncation markers.

Inline policies are stored in group attrs under `RGW_ATTR_IAM_POLICY` as an encoded map of policy name to document. Managed policy ARNs are stored under `RGW_ATTR_MANAGED_POLICY` as `rgw::IAM::ManagedPolicies`.

## State and Persistence Behavior

Persistent state is group metadata (`RGWGroupInfo`), group attrs, object version trackers, user `group_ids`, and account group counts. Writes use exclusive create or versioned read-modify-write with retry on `-ECANCELED`. Non-master zones forward mutating IAM calls to the master before applying local mirrored updates, and they treat some missing deletes as success if the master already succeeded.

## Dependencies and Integration Points

This file depends on RGW ARN formatting, IAM policy parsing and managed-policy lookup, SAL group/user/account APIs, process environment site config, the shared IAM validation/forwarding helpers, and formatter XML output. It integrates with account quota settings and with user metadata because group membership is stored on users.

## Risks and Edge Cases

Deletion conflict checks depend on decoding attr blobs; corrupt policy attrs return `-EIO`. Managed policy attach validates the policy ARN against built-in managed policies but the ARN grammar check itself is light. Some log/error messages say "user policies" in group paths, which can mislead debugging. `CreateGroup` logs account load failure but does not immediately return before inspecting `account.max_groups`, which is a risk if the account load failed. Membership updates only store group ids on users, so list/group queries depend on SAL indexes honoring that model.

Pagination uses map/set ordering and marker lower bounds; marker semantics should be kept stable for AWS compatibility. Forwarding strips consumed args before sending to the master, so any new request parameter must be handled consistently.

## Test Signals

Tests should cover all required parameter validation, path/name constraints, quota exceedance, IAM permission denial, create/update/delete forwarding, concurrent update retries, delete conflicts for users/inline/managed policies, idempotent add/remove membership, inline policy parse errors and 100-policy limit, managed policy attach/detach/list, pagination markers, and root/account identity edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_group.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_group.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_group.h

## Purpose

`rgw_rest_iam_group.h` declares factory functions for IAM group-related `RGWOp` objects. It keeps concrete group operation classes private to the implementation while exposing constructors to the central IAM dispatcher.

## Important APIs

Factories cover group lifecycle, membership, groups-for-user listing, inline group policies, managed policy attach/detach, and attached policy listing: `make_iam_create_group_op()`, `make_iam_get_group_op()`, `make_iam_update_group_op()`, `make_iam_delete_group_op()`, `make_iam_list_groups_op()`, `make_iam_add_user_to_group_op()`, `make_iam_remove_user_from_group_op()`, `make_iam_list_groups_for_user_op()`, `make_iam_put_group_policy_op()`, `make_iam_get_group_policy_op()`, `make_iam_delete_group_policy_op()`, `make_iam_list_group_policies_op()`, `make_iam_attach_group_policy_op()`, `make_iam_detach_group_policy_op()`, and `make_iam_list_attached_group_policies_op()`.

## Control Flow and Integration

`rgw_rest_iam.cc` stores these function pointers in its `Action` map. Mutating factories accept the original POST body for multisite forwarding. Read-only factories ignore the body.

## Risks and Test Signals

The header is a dispatcher contract. Missing a factory in the action map makes a compiled operation unreachable; changing a signature breaks central IAM dispatch. Compile/link tests and action-dispatch tests should cover every declared factory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_group.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_user.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_user.cc

## Purpose

`rgw_rest_iam_user.cc` implements IAM user and access-key operations for RGW. It supports user lifecycle, user listing, access key create/update/delete/list, XML response formatting, multisite forwarding for mutations, account quota enforcement, and factory functions for the central IAM action dispatcher.

## Important APIs and Operations

Concrete operations are `RGWCreateUser_IAM`, `RGWGetUser_IAM`, `RGWUpdateUser_IAM`, `RGWDeleteUser_IAM`, `RGWListUsers_IAM`, `RGWCreateAccessKey_IAM`, `RGWUpdateAccessKey_IAM`, `RGWDeleteAccessKey_IAM`, and `RGWListAccessKeys_IAM`. Helpers `make_resource_name()`, `dump_iam_user()`, and `dump_access_key()` format IAM response bodies.

Factories at the bottom expose the operations as `make_iam_create_user_op()`, `make_iam_get_user_op()`, and similar access-key factories.

## Control Flow

User operations derive account id from `s->auth.identity->get_account()`, validate IAM names and paths, load users by account/name through the SAL driver, hide the root user from named user APIs, verify IAM permissions against the target user ARN, and then execute the requested operation.

Create enforces `account.max_users`, generates a UUID user id and tenant, sets create date, optionally forwards to the metadata master to receive the authoritative id, then stores the user exclusively. Get returns either a named user or the signing user when `UserName` is omitted. Update changes path/display name under `retry_raced_user_write()`. Delete optionally forwards, checks on the master that access keys, inline user policies, and managed policies are removed, then removes the user. List streams users with chunked transfer and skips root users.

Access-key operations can target the signing user when `UserName` is omitted. Create enforces account `max_access_keys`, generates key id/secret locally or uses master-forwarded credentials, then stores the key in `RGWUserInfo::access_keys`. Update toggles `active`. Delete erases an access key and treats missing keys as success on non-master after master success. List paginates the user's access-key map and emits `AccessKeyMetadata`.

## State and Persistence Behavior

Persistent state is stored in `RGWUserInfo`: user id, tenant, account id, path, display name, create date, access key map, attrs for policies, and group ids. Mutations use versioned read-modify-write via `retry_raced_user_write()` except exclusive creates and removes. Non-master zones forward mutating IAM requests to the metadata master before applying local state, which keeps generated ids and secrets consistent.

## Dependencies and Integration Points

The file depends on RGW ARN helpers, IAM validation/forwarding/retry helpers, account quota metadata, SAL user/account APIs, access-key generation, policy attr names, managed policy encoding, and formatter output. It integrates with user policy code through `RGW_ATTR_USER_POLICY`, managed policy code through `RGW_ATTR_MANAGED_POLICY`, group code through `group_ids`, and multisite site config through `s->penv.site`.

## Risks and Edge Cases

Forwarding methods strip request args before calling the master; new parameters must be added to strip lists. `RGWCreateAccessKey_IAM::forward_to_master()` checks `if (!user)` instead of the parsed `access_key` XML pointer, which looks like a bug risk around malformed master responses. Delete conflict checks only run on the master; non-master paths rely on master success. List operations use lower-bound markers over maps and can expose ordering differences if key ordering changes.

Quota checks race with concurrent creates but the subsequent metadata write retry narrows only per-user races, not account-wide count races. Access-key create inserts the key before checking `max_keys`; the lambda returns limit exceeded before store, but the in-memory object now contains the extra key for that operation's response path.

## Test Signals

Tests should cover name/path validation, missing account identity, root-user hiding, user quota and access-key quota, master forwarding for creates with returned user id/key secret, update/delete race retries, delete conflict conditions, idempotent access-key update/delete behavior, active/inactive status validation, list pagination, `UserName` omitted behavior for root/account credentials, and malformed forwarded XML handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_user.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_user.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_user.h

## Purpose

`rgw_rest_iam_user.h` declares factory functions for IAM user and access-key operations while keeping the concrete operation classes local to `rgw_rest_iam_user.cc`.

## Important APIs

User factories include create, get, update, delete, and list. Access-key factories include create, update, delete, and list. Factories that mutate state accept the POST body so the operation can forward the original IAM request to the metadata master in multisite deployments.

## Control Flow and Integration

The central IAM dispatcher maps AWS `Action` names to these factories. The returned `RGWOp` instances then participate in standard RGW init, permission verification, execution, and response handling.

## Risks and Test Signals

The declarations are part of the action-dispatch ABI inside RGW. Tests should verify that every declared factory is present in `op_generators`, that read-only factories tolerate an unused body, and that mutating factories preserve the body argument for forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_info.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_info.cc

## Purpose

`rgw_rest_info.cc` implements the admin REST info endpoint. It returns general RGW backend information, currently the accessible storage backend name and cluster id.

## Important APIs and Functions

`RGWOp_Info_Get` is a local `RGWRESTOp` requiring `info` read caps. `execute()` writes an `info.storage_backends` array with one object containing `driver->get_name()` and `driver->get_cluster_id()`. `RGWHandler_Info::op_get()` always returns this operation for GET requests.

## Control Flow

After admin authentication and cap verification, execution starts formatter output with the flusher, opens the expected object/array sections, emits backend data, closes sections, and flushes. There is no separate custom `send_response()`; normal RGW op handling finishes the response.

## State and Persistence Behavior

The endpoint is read-only. It queries driver identity and cluster id and does not mutate metadata or object state.

## Dependencies and Integration Points

It depends on `rgw_op.h`, `rgw_rest_info.h`, and SAL driver methods. It integrates with admin REST mounts through `RGWRESTMgr_Info` in the header and with capability checks through `caps.check_cap("info", RGW_CAP_READ)`.

## Risks and Test Signals

The response schema is intentionally extensible but currently has only one backend object. Tests should verify cap enforcement, valid cluster id output, JSON/XML formatter shape, and behavior when `driver->get_cluster_id()` returns an error-like or empty string.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_info.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_info.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_info.h

## Purpose

`rgw_rest_info.h` declares the authenticated admin REST info handler and manager.

## Important APIs and Types

`RGWHandler_Info` derives from `RGWHandler_Auth_S3`, dispatches GET requests, and skips extra permission loading. `RGWRESTMgr_Info` creates the handler for the info resource.

## Control Flow, State, and Integration

The manager produces a handler, S3 admin auth is applied, and the implementation returns an info GET operation. The endpoint is read-only and state access is delegated to the SAL driver.

## Risks and Test Signals

The header is small. Tests should ensure handler creation, GET dispatch, and authenticated cap enforcement remain wired when REST resources are registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_metadata.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_metadata.cc

## Purpose

`rgw_rest_metadata.cc` implements authenticated admin REST access to RGW metadata entries. It supports listing metadata keys, reading entries, writing entries with sync-apply modes, deleting entries, and the special `myself` lookup.

## Important APIs and Functions

`frame_metadata_key()` builds the metadata key from the URL bucket/init-state section and the `key` query arg. Operations implemented are `RGWOp_Metadata_Get`, `RGWOp_Metadata_Get_Myself`, `RGWOp_Metadata_List`, `RGWOp_Metadata_Put`, and `RGWOp_Metadata_Delete`. `RGWHandler_Metadata` dispatches GET to list/get/myself, PUT to write, and DELETE to remove.

`RGWOp_Metadata_Put::get_data()` reads fixed-length or chunked request bodies into a bufferlist. `string_to_sync_type()` maps `update-type` strings to `RGWMDLogSyncType`.

## Control Flow

GET with `myself` appends the authenticated owner id as `key` and reuses normal get. GET with `key` calls the metadata manager's `get()`. GET without `key` decodes an optional base64 marker, parses optional `max-entries`, initializes metadata listing, loops through `meta_list_keys_next()`, and emits either legacy `keys` output or an extended response with truncation/count/marker.

PUT reads the body, completes AWS4 auth after body read, frames the metadata key, parses `update-type` (`update-by-version`, `update-by-timestamp`, or `always`), and calls the RADOS metadata manager `put()`. `send_response()` maps internal apply/skipped statuses to 204 and emits `RGWX_UPDATE_STATUS` and `RGWX_UPDATE_VERSION` headers. DELETE frames the metadata key and calls metadata manager `remove()`.

## State and Persistence Behavior

GET/list are read-only. PUT and DELETE mutate RADOS-backed RGW metadata through `static_cast<rgw::sal::RadosStore*>(driver)->ctl()->meta.mgr`. PUT persists the new metadata blob and records the on-disk object version returned by the metadata manager. The sync type controls whether incoming metadata is always applied, only newer by timestamp, or by version.

## Dependencies and Integration Points

This file depends on RADOS SAL metadata control, mdlog sync types, request body I/O, base64 marker encoding, strict integer parsing, and AWS auth completion. It is used by admin tools and multisite metadata synchronization flows.

## Risks and Edge Cases

The implementation assumes a RADOS store via static cast. `get_data()` manually allocates request buffers and relies on `s->length` or exact `HTTP_TRANSFER_ENCODING == "chunked"`. In list mode, errors before `meta_list_keys_complete()` can leak the listing handle because early returns bypass completion. Base64 marker decode catches all exceptions and silently resets the marker. `max-entries` is parsed with `strict_strtol()` then cast to unsigned.

## Test Signals

Tests should cover key framing from URL bucket plus `key`, `myself`, fixed and chunked PUT bodies, missing length errors, AWS4 body auth completion, all update-type modes, update status/version headers, list legacy versus extended response formats, base64 marker round trips, delete behavior, cap enforcement, and handle cleanup on listing failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_metadata.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_metadata.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_metadata.h

## Purpose

`rgw_rest_metadata.h` declares RGW admin REST operations for metadata list/get/put/delete and the handler/manager that exposes them.

## Important APIs and Types

Read operations `RGWOp_Metadata_List`, `RGWOp_Metadata_Get`, and `RGWOp_Metadata_Get_Myself` require `metadata` read caps. `RGWOp_Metadata_Put` requires `metadata` write caps, has private body-reading state, records update status and on-disk version, and reports op type `RGW_OP_ADMIN_SET_METADATA`. `RGWOp_Metadata_Delete` requires `metadata` write caps. `RGWHandler_Metadata` dispatches GET/PUT/DELETE. `RGWRESTMgr_Metadata` creates the handler.

## Control Flow and State

Operation dispatch is query-sensitive for GET: `myself`, `key`, or list. PUT stores response header state (`update_status`, `ondisk_version`) for `send_response()`. The header itself does not persist metadata.

## Dependencies and Integration Points

The declarations depend on RGW REST and S3 auth headers. The implementation integrates with RADOS metadata managers and admin tools.

## Risks and Test Signals

The operation classes expose cap boundaries for powerful metadata mutation APIs. Tests should verify read/write cap separation, correct op type for PUT audit handling, and dispatch priority where `myself` takes precedence over `key`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_metadata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_oidc_provider.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_oidc_provider.cc

## Purpose

`rgw_rest_oidc_provider.cc` implements IAM OpenID Connect provider operations for RGW. It supports create, delete, get, list, add/remove client id, and replace thumbprint list, with IAM permission checks and optional forwarding to the metadata master zone.

## Important APIs and Functions

`forward_oidc_iam_request()` wraps shared IAM forwarding. `RGWRestOIDCProvider::verify_permission()`, `check_caps()`, and `send_response()` provide common base behavior. `format_creation_date()` formats AWS-style creation timestamps. `validate_provider_arn()` parses and validates OIDC provider ARNs while allowing provider URLs with ports.

Concrete operations are `RGWCreateOIDCProvider`, `RGWDeleteOIDCProvider`, `RGWGetOIDCProvider`, `RGWListOIDCProviders`, `RGWAddClientIdToOIDCProvider`, `RGWRemoveClientIdFromOIDCProvider`, and `RGWUpdateOIDCProviderThumbprint`.

## Control Flow

Create reads `Url`, `ClientIDList.member.*`, and `ThumbprintList.member.*`, enforces maximum lengths/counts, derives tenant/account, builds an ARN from `url_remove_prefix(provider_url)`, sets creation date, forwards if not metadata master, and stores the provider exclusively. Delete/get parse `OpenIDConnectProviderArn`, validate the account component against the authenticated account or tenant, and call the SAL driver's delete/load API. List fetches all providers for the account and emits their ARNs.

Add/remove client id and update thumbprints validate ARN and request fields, load the provider with a version tracker, optionally forward to master, mutate `client_ids` or `thumbprints`, and store non-exclusively with the version tracker. Add is idempotent for an existing client id. Remove is a no-op success if the client id is absent. Thumbprint update replaces the full list.

## State and Persistence Behavior

Persistent state is `RGWOIDCProviderInfo`: tenant/account, provider URL, ARN, creation date, client ids, and thumbprints. The SAL driver stores, loads, lists, and deletes provider records. Mutations use `RGWObjVersionTracker`, but this file does not use the shared retry helper for raced writes, so version conflicts may surface directly.

## Dependencies and Integration Points

The file depends on RGW IAM permission evaluation, shared IAM forwarding, OIDC provider metadata types, SAL OIDC APIs, request identity/account data, and formatter output. It is instantiated from `rgw_rest_iam.cc` action mappings.

## Risks and Edge Cases

ARN validation is custom and only accepts `arn:aws:iam::<tenant>:oidc-provider/...`, with account matching the caller. Create validates max thumbprints and max client ids, but thumbprint update validates non-empty and per-item length without enforcing the max count. Client-id add does not enforce the max total count after appending. Response section names for add/remove/update include duplicated or incorrect names in places, including thumbprint update using `AddClientIDToOpenIDConnectProviderResponse`.

Non-master operations load the provider before forwarding for add/remove/update. If the master changes state, local mutation uses the pre-forward loaded state and version tracker. Error mapping converts unexpected load/delete failures to `ERR_INTERNAL_ERROR` but leaves `-ENOENT` and `-EINVAL` as-is.

## Test Signals

Tests should cover URL/client/thumbprint length and count limits, ARN parser variants including localhost ports, account mismatch rejection, IAM permission fallback to caps, create exclusive conflict, list formatting, add idempotency, remove absent idempotency, thumbprint replacement, multisite forwarding, concurrent version conflicts, and exact XML response section names expected by IAM clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_oidc_provider.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_oidc_provider.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_oidc_provider.h

## Purpose

`rgw_rest_oidc_provider.h` declares IAM OIDC provider operation classes used by the central IAM dispatcher.

## Important APIs and Types

`RGWRestOIDCProvider` is the common base carrying the IAM action id, admin cap permission, and target ARN resource used by `verify_permission()`. Derived classes represent create, delete, get, list, add client id, remove client id, and update thumbprint operations. Mutating operations store the original POST body for master-zone forwarding. Each class declares `init_processing()` where request parsing is needed, `execute()`, operation name, and `RGWOpType`.

## Control Flow and State

The dispatcher constructs these classes by action name. `init_processing()` must initialize the protected `resource` before permission verification. Execution then uses SAL OIDC provider APIs and optional master forwarding. Per-operation members store parsed URL, client id, thumbprints, or provider info.

## Dependencies and Integration Points

The header depends on ARN support, RGW REST base classes, and `RGWOIDCProviderInfo`. It integrates with `rgw_rest_iam.cc`, IAM permission checks, and SAL provider persistence.

## Risks and Test Signals

The base class permission flow depends on derived classes setting `resource` early. Missing that initialization can evaluate permissions against an empty ARN or fall back to broad caps. Tests should exercise init-before-verify ordering for every OIDC action and verify op type mappings for audit/logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_oidc_provider.h -->
