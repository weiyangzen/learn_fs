# subset-b-006999 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_s3.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_s3.h

## Purpose
`rgw_rest_s3.h` is the main declaration point for Ceph RGW's S3 REST dialect. It binds generic RGW object-store operations to S3-specific request parsing, XML/HTTP response formatting, bucket and object subresource routing, S3 bucket/object name validation, and AWS-compatible authentication engines.

The file is primarily an interface header. Concrete behavior is implemented in companion `.cc` files, but this header exposes the operation classes and routing/auth contracts that make S3 the default RGW protocol surface.

## Important APIs, Types, and Functions
`rgw_http_error` and `rgw_get_errno_s3()` map RGW errors to S3 HTTP status and S3 error codes.

The `RGW*_ObjStore_S3` classes derive from generic RGW ops in `rgw_op.h` and override `get_params()`, `send_response()`, `send_response_data()`, and encryption/decryption hooks to implement S3 wire behavior. They cover object GET/PUT/POST/COPY/DELETE, ACLs, tags, lifecycle, CORS, encryption, ownership controls, request payment, multipart upload, object lock, retention/legal hold, metadata search, bucket policy status, and bucket public-access-block subresources.

`RGWHandler_REST_S3`, `RGWHandler_REST_Service_S3`, `RGWHandler_REST_Bucket_S3`, and `RGWHandler_REST_Obj_S3` define S3 request routing. The service handler handles service-level GET/HEAD/OPTIONS and usage; bucket/object handlers inspect query subresources such as `acl`, `tagging`, `lifecycle`, `policy`, `notification`, `replication`, `encryption`, `ownershipControls`, `publicAccessBlock`, `retention`, `legal-hold`, and `select-type` to choose the concrete operation.

`RGWRESTMgr_S3` owns optional nested managers for S3Control and S3Website and exposes `get_resource_mgr_as_default()` for URI dispatch. Its constructor parameters gate S3Control, website, STS, IAM, and pubsub support.

`looks_like_ip_address()`, `valid_s3_object_name()`, and `valid_s3_bucket_name()` enforce S3 naming constraints, including UTF-8 checks, length bounds, lowercase bucket rules, dot/dash placement, relaxed mode, and IP-address rejection.

The `rgw::auth::s3` namespace declares `AWSEngine`, version abstractors for AWS signature v2/v4/browser uploads, `AWSSignerV4`, `LDAPEngine`, `LocalEngine`, `STSEngine`, and `S3AnonymousEngine`. These translate request auth data into local/remote/role identity appliers.

## Control Flow
An S3 frontend request is dispatched by `RGWRESTMgr_S3::get_handler()`, then `RGWHandler_REST_S3::init()` and `init_from_header()` parse URI/header state into `req_state`. `authorize()` delegates to `RGW_Auth_S3::authorize()`, which applies the S3 strategy registry. `postauth_init()` finalizes bucket/object state after identity resolution.

After handler initialization, the HTTP method and query subresources select an `RGWOp`. For example, bucket GET can become bucket listing, ACL retrieval, lifecycle retrieval, CORS retrieval, replication retrieval, encryption retrieval, ownership controls retrieval, policy status, public access block, or object GET depending on parsed state. Object methods similarly branch to object data, tags, ACLs, retention, legal hold, select, multipart, copy, or delete operations.

Authentication flow runs through a `VersionAbstractor` that extracts access key id, client signature, optional session token, canonical string-to-sign, and completer factory. `AWSEngine::authenticate()` then calls the selected concrete engine to resolve credentials and verify server-side signatures. `STSEngine` additionally interprets session tokens.

## State and Persistence Behavior
The header itself persists no data, but its operation classes are the protocol-specific front doors to persistent RGW state. Their base classes mutate buckets, objects, bucket metadata, object attrs, user-visible XML responses, multipart metadata, lifecycle configuration, CORS configuration, object lock/retention state, encryption attrs, and bucket-level public access flags.

Per-request state is held in `req_state`, handler members, and operation members. Examples include response encryption headers, checksum mode, S3 POST policy environment, multipart flags, list pagination tokens, and custom website HTTP status overrides. Authentication state is passed through `req_state::auth`, strategy registries, identity appliers, and optional session tokens.

## Dependencies and Integration Points
The header depends on RGW core operation and REST abstractions, S3 ACL/policy/lifecycle types, Keystone, REST connections, LDAP, token and STS support, RGW auth filters, and Ceph utility types. It is included by many concrete S3, STS, S3Website, usage, and admin files.

Integration points include the RGW frontend dispatch table, SAL driver object/bucket/user implementations, IAM permission checks, auth strategy registry construction, S3 website and S3Control nested managers, pubsub notification routing, encryption/decryption filters, and XML/HTTP formatter code.

## Risks
The header concentrates many S3 subresource branch predicates. Adding a query parameter or changing method selection can accidentally shadow object operations or route a bucket operation to an object operation.

Name validation must remain compatible with AWS while preserving Ceph's relaxed modes. Misclassifying IP-like names, UTF-8, uppercase, or dot/dash adjacency can break client compatibility or permit invalid bucket names.

Auth abstractions are sensitive to canonicalization. Differences between general, boto2-compatible, and browser-upload canonical header handling can produce signature mismatches. STS session token handling also ties S3 auth to token persistence and role applier behavior.

## Test Signals
Useful signals include S3 API tests for each bucket/object subresource, AWS signature v2/v4 header and query signing, browser POST upload signing, temporary credentials, anonymous requests, bucket-name/object-name validation edge cases, website/S3Control nested manager routing, and response XML/status compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_s3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_s3control.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_s3control.cc

## Purpose
`rgw_rest_s3control.cc` implements the currently registered S3Control account-level public access block API under `/v20180820/configuration/publicAccessBlock`. It supports GET, PUT, and DELETE of `PublicAccessBlockConfiguration` on RGW account metadata.

The file also contains retry logic for account metadata write races and the REST handler/manager wiring needed to serve the S3Control dialect with S3 authentication.

## Important APIs, Types, and Functions
`retry_raced_account_write()` executes an account write closure and retries up to ten times when `store_account()` returns `-ECANCELED`. Each retry clears the object version tracker and reloads account info/attrs before reapplying the closure.

`get_account_id()` reads `x-amz-account-id` from request metadata, rejects missing or empty values, and for non-admin callers verifies that the requested account id matches `s->auth.identity->get_account()`.

`RGWGetPublicAccessBlock_S3Control` loads the account, decodes `RGW_ATTR_PUBLIC_ACCESS` into `PublicAccessBlockConfiguration`, verifies `s3GetAccountPublicAccessBlock`, and emits XML.

`RGWPutPublicAccessBlock_S3Control` reads and XML-decodes the request body within `rgw_max_put_param_size`, verifies `s3PutAccountPublicAccessBlock`, forwards the request to the metadata master, encodes the public-access config into `RGW_ATTR_PUBLIC_ACCESS`, and stores the account with race retry.

`RGWDeletePublicAccessBlock_S3Control` verifies the same write permission, forwards to the master, erases `RGW_ATTR_PUBLIC_ACCESS` if present, and returns `204 No Content` on success.

`RGWHandler_PublicAccessBlock` sets `s->dialect = "s3control"`, enables `RGW_REST_S3CONTROL`, allocates XML formatting, and delegates authorization to `RGW_Auth_S3::authorize()`. `RGWRESTMgr_S3Control_PublicAccessBlock` returns that handler, and `RGWRESTMgr_S3Control` registers it under `configuration/publicAccessBlock`.

## Control Flow
A request routed to S3Control reaches `RGWRESTMgr_S3Control`, then `configuration`, then `publicAccessBlock`. The handler picks GET, PUT, or DELETE and performs ordinary RGW op lifecycle: init processing, permission verification, execute, and response.

GET only loads and decodes current account attrs. PUT first validates account id and XML body, then loads the account, forwards the original request/body to the metadata master, and updates attrs locally using optimistic object-version retry. DELETE follows the same load/forward/retry pattern but erases the attr.

## State and Persistence Behavior
The durable state is account metadata attribute `RGW_ATTR_PUBLIC_ACCESS`, containing an encoded `PublicAccessBlockConfiguration`. Writes use `driver->store_account()` with `exclusive = false`, previous account info, attrs, and `RGWObjVersionTracker`.

The implementation is zone-aware. Mutating operations call `rgw_forward_request_to_master()` before local mutation, ensuring account metadata is coordinated through the master zone. Race retries reload the account and reapply the attr update to current attrs.

## Dependencies and Integration Points
The file depends on `rgw_account.h`, `rgw_auth_s3.h`, `rgw_process_env.h`, SAL account load/store APIs, RGW XML decoder/formatter helpers, IAM permission checks, and S3 auth strategy registry. It is registered as a nested manager by `RGWRESTMgr_S3` when S3Control is enabled.

## Risks
The `x-amz-account-id` header is the authority for target account; any change to identity/account matching could expose cross-account metadata. PUT and DELETE use a placeholder root ARN construction marked with `XXX`, so permission resource semantics should be reviewed with account IAM changes.

Forward-to-master happens before local attr mutation. If forwarding succeeds but local retry later fails, client-visible behavior depends on master propagation and error handling. Decode failures of stored public-access attrs are treated as `-EIO`.

## Test Signals
Tests should cover missing/empty/mismatched `x-amz-account-id`, admin bypass, account without public access block, malformed XML, permission allow/deny for get and put/delete actions, master-zone forwarding, concurrent account metadata updates returning `-ECANCELED`, and idempotent delete when the attr is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_s3control.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_s3control.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_s3control.h

## Purpose
`rgw_rest_s3control.h` declares `RGWRESTMgr_S3Control`, the REST manager that serves S3Control resources under `/v20180820`.

## Important APIs, Types, and Functions
`RGWRESTMgr_S3Control` derives from `RGWRESTMgr`, grants `RGWRESTMgr_S3` friend access to protected resource-manager lookup, and exposes a constructor that registers nested S3Control resources in the `.cc` file.

## Control Flow
The manager is created by the S3 REST manager when S3Control is enabled. URI dispatch descends through its registered resources, currently `configuration/publicAccessBlock`, and then returns a resource-specific handler.

## State and Persistence Behavior
The header owns no persistent state. The manager's registration tree is in-memory process state. Durable account public-access configuration is handled by `rgw_rest_s3control.cc`.

## Dependencies and Integration Points
It depends only on `rgw_rest.h` for `RGWRESTMgr`. The integration point is `RGWRESTMgr_S3`, which can expose this manager as a nested resource under the S3 frontend.

## Risks
Because the class is small, most risk is in registration coverage. If the constructor is not updated when adding S3Control APIs, requests will not dispatch even if operation classes exist.

## Test Signals
Dispatch tests should confirm that S3Control-enabled frontends route `/v20180820/configuration/publicAccessBlock` to the correct handler and that disabled S3Control does not expose the route.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_s3control.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_s3website.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_s3website.h

## Purpose
`rgw_rest_s3website.h` declares the S3 static website REST dialect. It specializes S3 handlers so website endpoints serve objects, index documents, redirects, and custom error documents while disallowing mutating bucket/object APIs.

## Important APIs, Types, and Functions
`RGWHandler_REST_S3Website` derives from `RGWHandler_REST_S3`. It stores the original object name before retargeting, overrides `retarget()`, `op_get()`, `op_head()`, and `error_handler()`, and makes PUT/DELETE/POST/COPY/OPTIONS unsupported. `serve_errordoc()` serves configured error objects.

`RGWHandler_REST_Service_S3Website`, `RGWHandler_REST_Obj_S3Website`, and `RGWHandler_REST_Bucket_S3Website` all provide website-specific `get_obj_op()` behavior. The bucket handler deliberately derives through the website base rather than normal bucket operation semantics because website endpoints do not support bucket operations.

`RGWRESTMgr_S3Website` returns website handlers and is friend-accessed by `RGWRESTMgr_S3` for nested resource routing.

`RGWGetObj_ObjStore_S3Website` extends S3 GET. It can mark an error-document request, override data/error response behavior, ignore range and conditional headers for error pages, and change the canonical op name to `WEBSITE.<method>.OBJECT`.

## Control Flow
Website requests are routed to the website manager and initialized as S3-derived handlers. Only GET and HEAD produce operations. The handler can retarget a bucket or object request to an index object, error document, or original object depending on website configuration and request path.

When serving a configured error page, `RGWGetObj_ObjStore_S3Website::get_params()` clears range and conditional request members so the error object is fetched as an unconditional body while the status line can represent the original error.

## State and Persistence Behavior
The header persists no state. It reads bucket website configuration and object data through normal RGW bucket/object state. Per-request mutable state includes `original_object_name`, retargeted `s->object`, and `is_errordoc_request`.

## Dependencies and Integration Points
It depends on `rgw_rest_s3.h`, normal S3 object GET behavior, website configuration stored on buckets, RGW handler retargeting, and formatter/error handling. It is integrated as an optional manager under the S3 REST manager.

## Risks
Retargeting mutates request object state. Incorrect restoration or object-name handling can serve the wrong key or create bad redirects. Error-document fetches intentionally bypass conditional headers, so that behavior must stay limited to error-document requests.

## Test Signals
Coverage should include website GET/HEAD only, PUT/DELETE/POST rejection, index document routing, slash redirect behavior, custom error document serving with original status, missing error page fallback, conditional/range headers on normal versus error-page requests, and bucket/object path edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_s3website.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_sts.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_sts.cc

## Purpose
`rgw_rest_sts.cc` implements Ceph RGW's STS REST API and web identity authentication engine. It handles OIDC/JWT validation for `AssumeRoleWithWebIdentity`, ordinary S3-authenticated STS actions, trust-policy evaluation, credential/session issuance, and STS XML responses.

## Important APIs, Types, and Functions
`rgw::auth::sts::WebTokenEngine` validates web identity tokens. It parses role ARN tenant/name, loads OIDC provider metadata, extracts token claims and principal tags, validates audience/client id, fetches OIDC discovery/JWKS data, verifies JWKS endpoint thumbprints, validates JWT signatures, loads the target role/account, and returns a `WebIdentityApplier`.

`get_cert_url()` retrieves `/.well-known/openid-configuration` and extracts `jwks_uri`. `verify_oidc_thumbprint()` optionally connects to the JWKS host, extracts the last TLS certificate in the chain, and compares its SHA1 thumbprint to registered provider thumbprints. `validate_signature()` supports RSA, ECDSA, and PSS algorithms with `x5c` certificates and bare RSA `n`/`e` JWKs; HMAC JWT algorithms are rejected.

`RGWREST_STS::verify_permission()` loads role info through `STS::STSService`, parses the role trust policy, optionally enforces `stsTagSession`, and evaluates either `stsAssumeRoleWithWebIdentity` or `stsAssumeRole` against the authenticated identity.

`RGWSTSGetSessionToken`, `RGWSTSAssumeRoleWithWebIdentity`, `RGWSTSAssumeRole`, and `RGWSTSGetCallerIdentity` parse STS action parameters, call `STS::STSService`, and write AWS-style XML response sections.

`RGW_Auth_STS::authorize()` applies the STS auth strategy. `RGWHandler_REST_STS` maps `Action` values to operation constructors and uses STS auth only for `AssumeRoleWithWebIdentity`; other actions use normal S3 auth. `RGWRESTMgr_STS` returns this handler.

## Control Flow
For `AssumeRoleWithWebIdentity`, the handler sees `Action=AssumeRoleWithWebIdentity` and authorizes with the STS strategy. `WebTokenEngine` extracts `WebIdentityToken`, decodes JWT claims, loads the OIDC provider based on issuer and role ARN tenant, validates client id/audience and signature, loads the role and optional account, then grants a web-identity applier. The op then validates parameters/trust policy and calls `sts.assumeRoleWithWebIdentity()`.

For `AssumeRole`, the handler authorizes with S3 credentials, builds an `STS::STSService`, validates role trust policy, parses duration/external id/policy/MFA fields, and calls `sts.assumeRole()`.

For `GetSessionToken`, permission is checked with `stsGetSessionToken` on an S3 ARN. The op validates optional duration bounds and calls `sts.getSessionToken()`.

For `GetCallerIdentity`, no permission is required. The op builds account, user id, and caller ARN from the authenticated identity and environment and returns them.

## State and Persistence Behavior
The file mostly reads persistent state and asks `STS::STSService` to create credentials. It reads OIDC provider records through `driver->load_oidc_provider()`, roles through `driver->get_role()->load_by_name()`, accounts through `driver->load_account_by_id()`, and role trust policies from role metadata.

Issued credentials and session token persistence are delegated to `STS::STSService` and related STS types. Request-local state includes extracted token claims, principal tags, `s->principal_tags`, role session name, policy strings, and XML formatter output.

Network-derived JWKS/OIDC data is not persisted here. It is fetched per validation path through `RGWHTTPTransceiver` and OpenSSL socket/TLS helpers.

## Dependencies and Integration Points
The implementation depends on OpenSSL, `jwt-cpp`, JSON parsing, RGW HTTP transceiver, OIDC provider storage, IAM policy parser/evaluator, STS service types, auth strategy registry, S3 auth for non-web-identity actions, SAL driver role/account/OIDC provider APIs, and RGW XML formatter helpers.

It integrates with IAM trust policies, role tags, principal tags, account-based role ARNs, web identity appliers, and frontend REST dispatch through `RGWRESTMgr_STS`.

## Risks
OIDC validation performs outbound HTTP and TLS connections in the request path and calls `maybe_warn_about_blocking()`. DNS, network latency, JWKS availability, and certificate-chain parsing can directly affect STS latency and reliability.

Thumbprint logic is configuration-sensitive. `rgw_enable_jwks_url_verification` changes whether JWKS endpoint certificate verification is enforced, and the local `skip_thumbprint_verification` variable naming in `validate_signature()` is easy to misread.

JWT claim recursion flattens nested objects and arrays into multimaps/sets. Collisions or unexpected claim types can affect IAM condition evaluation. HMAC JWT algorithms are explicitly unsupported.

Trust-policy evaluation is parsed at request time with a TODO noting that role creation could validate it earlier. Bad stored policies therefore fail at assumption time.

## Test Signals
Tests should cover missing/invalid tokens, issuer normalization, OIDC provider lookup by tenant/account role ARN, audience/client_id/azp matching, principal tags, expired JWTs, unsupported algorithms, x5c and bare RSA JWK validation, JWKS thumbprint enforcement toggles, broken discovery/JWKS JSON, missing roles/accounts, trust policy allow/deny, `stsTagSession`, malformed session policies, duration bounds, caller identity for account and tenant users, and unknown/missing `Action`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_sts.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_sts.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_sts.h

## Purpose
`rgw_rest_sts.h` declares the STS REST handler, STS operation classes, and web-identity authentication strategy used by RGW STS endpoints.

## Important APIs, Types, and Functions
`rgw::auth::sts::WebTokenEngine` derives from `rgw::auth::Engine` and declares helpers for OIDC provider loading, JWT claim extraction, signature validation, certificate/thumbprint validation, role parsing, and web identity applier creation.

`rgw::auth::sts::DefaultStrategy` combines a `TokenExtractor`, `WebIdentityApplier::Factory`, and `WebTokenEngine`. Its extractor reads `WebIdentityToken` from request args, and its applier factory wraps `WebIdentityApplier` with `add_sysreq()`.

`RGWREST_STS` is the common base for STS ops and owns an `STS::STSService` member. Derived ops are `RGWSTSAssumeRoleWithWebIdentity`, `RGWSTSAssumeRole`, `RGWSTSGetSessionToken`, and `RGWSTSGetCallerIdentity`.

`RGW_Auth_STS`, `RGWHandler_REST_STS`, and `RGWRESTMgr_STS` declare authorization, action routing, handler initialization, and manager integration.

## Control Flow
The manager always returns `RGWHandler_REST_STS`. The handler parses POST actions, checks whether the action exists, selects one of the operation classes, and chooses STS web-token auth only for `AssumeRoleWithWebIdentity`. All other actions reuse S3 authorization.

Operation classes use `get_params()`, `verify_permission()`, `execute()`, and `send_response()` from the RGW op lifecycle. `RGWREST_STS::verify_permission()` centralizes role trust-policy checks for assume-role variants.

## State and Persistence Behavior
The header declares request-local parameter storage for duration, role ARN/session name, provider id, web identity claims, external id, MFA fields, and inline session policy. Persistent state is accessed in the implementation through roles, OIDC providers, account info, and STS-issued credentials.

## Dependencies and Integration Points
It depends on RGW auth, auth filters, REST base classes, STS service definitions, web identity provider support, OIDC provider types, and `jwt-cpp`. The declared classes integrate STS into the RGW REST manager tree and auth strategy registry.

## Risks
The auth split between web identity and S3 credentials is action-name dependent. If new STS actions are added without updating routing and authorization selection, they may get the wrong auth mechanism or no operation.

The header exposes many private web-token helper declarations, indicating a large security-sensitive implementation surface. Changes must preserve token validation, provider lookup, and applier semantics together.

## Test Signals
Header-level compatibility is exercised by STS action dispatch tests, auth strategy registry construction, web identity applier creation, and build coverage for JWT/OpenSSL dependencies. Behavior tests belong with the `.cc` implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_sts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_swift.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_swift.cc

## Purpose
`rgw_rest_swift.cc` implements Ceph RGW's OpenStack Swift-compatible REST dialect. It maps Swift account, container, object, bulk, tempurl/formpost, static large object, CORS, static website, `/info`, cross-domain, and health-check semantics onto RGW's generic operations and SAL storage layer.

The file is both a protocol adapter and a compatibility layer. It rewrites URLs, headers, metadata names, status codes, error bodies, object expiration fields, ACLs, and listing formats to match Swift expectations while reusing RGW object-store primitives.

## Important APIs, Types, and Functions
`FormPostSignatureT` and `RGWFormPost::SignatureHelper` implement Swift form POST HMAC signature verification for bare hex and named base64 SHA1/SHA256/SHA512 signatures.

`RGWListBuckets_ObjStore_SWIFT` parses account listing params (`prefix`, `marker`, `end_marker`, `reverse`, `limit`, `stats`), dumps account metadata headers, filters listing chunks by prefix, and supports reversed output buffering.

`dump_account_metadata()` and `dump_container_metadata()` translate RGW stats, quota, ACLs, temp URL keys, placement/storage policy, versioning, website config, user metadata, and generic attrs into Swift `X-Account-*` and `X-Container-*` headers.

`RGWListBucket_ObjStore_SWIFT` parses container listing params including Swift `path`, enforces `limit <= 10000`, and emits object/subdir entries in Swift JSON/XML/plain formatter shape.

`get_swift_container_settings()`, `get_rmattrs_from_headers()`, and `get_swift_versioning_settings()` parse Swift ACL, CORS, metadata removal, storage policy, and versions-location headers for container create/update paths.

`RGWPutObj_ObjStore_SWIFT` handles object PUT, content length/chunked checks, guessed content type, object expiration, custom user data header, dynamic large object manifest, and static large object manifest validation/ETag calculation.

`RGWFormPost` implements Swift tempurl form POST: it parses multipart control fields before the first file, validates expiration and signature against bucket owner's temp URL keys, streams file parts, and supports redirect responses.

`RGWSwiftWebsiteHandler` implements static web retargeting and custom error documents for Swift containers. It can redirect directory requests, serve index objects, generate HTML listings, or serve error documents.

`RGWBulkDelete_ObjStore_SWIFT`, `RGWBulkUploadOp_ObjStore_SWIFT`, `RGWInfo_ObjStore_SWIFT`, `RGWGetCrossDomainPolicy_ObjStore_SWIFT`, and `RGWGetHealthCheck_ObjStore_SWIFT` implement Swift bulk and auxiliary endpoints.

`RGWHandler_REST_SWIFT::init_from_header()` parses Swift URL prefixes, version/account/container/object path components, request args, account names, and object version id extension. Handler subclasses then select service, bucket, or object operations.

## Control Flow
Swift requests first pass through `RGWRESTMgr_SWIFT::get_handler()`, which calls `init_from_header()`. That function verifies the configured Swift URL prefix, strips optional `AUTH_`/`KEY_` account prefixes, sets request args/formatter/protocol flags, saves the URL bucket in `init_state`, and constructs an object when an object path exists.

Handler `init()` handles Swift copy semantics: `X-Copy-From` records a source for PUT copy, and COPY requests with `Destination` are rewritten into PUT requests with source/destination state swapped. `postauth_init()` assigns bucket tenant/name, validates tenant, container, and object names, and validates source copy names.

Service-level operations list/stat account, bulk delete, bulk upload, or update account metadata. Bucket-level operations list/stat/create/delete containers, update container metadata, CORS options, form POST, ACL no-ops, and archive extraction. Object-level operations get/head/put/delete/copy/post metadata/options and form POST.

Response flow is Swift-specific. Many operations remap success to `201 Created`, `202 Accepted`, or `204 No Content`, expose object/account/container metadata in headers, and use chunked response bodies for bulk delete/upload summaries.

Static website retargeting runs after operation selection. For eligible anonymous or `X-Web-Mode: true` GET/HEAD requests, bucket/object handlers can replace the selected op with redirect, index GET, or generated listing operations. Error handlers can fetch configured error documents while preserving the original HTTP status.

## State and Persistence Behavior
Persistent storage is still RGW bucket/object/user state. This file drives persistence through base operations by setting operation fields: metadata attrs/removal sets, ACL policies, CORS configs, placement rules, `swift_ver_location`, delete-at timestamps, DLO/SLO manifests, object user data, and copy attr modes.

Account metadata updates read and write user attrs and account ACL policy. Container metadata updates mutate bucket attrs, CORS, ACL, versioning location, placement/storage class, quota headers, and website config attrs parsed elsewhere. Object PUT/POST/COPY updates object attrs including content type, delete-at, DLO/SLO indicators, and user metadata.

SLO PUT reads a JSON manifest, loads every referenced segment object to verify existence and size, computes the large-object ETag from segment ETags, and stores manifest raw data/total size in the base PUT path. Bulk delete and archive extract stream request bodies and delegate per-object persistence to bulk base classes.

The Swift zero-copy state is request-local except for `RGWListBuckets_ObjStore_SWIFT::reverse_buffer`, formpost control/current parts, and website retarget mutations to `s->object`/`s->object_key`.

## Dependencies and Integration Points
The file depends on Swift ACL/CORS/auth helpers, RGW formatters, client IO, compression attrs, auth registry, request/process infrastructure, zone placement config, SAL driver bucket/object/user APIs, RGW bulk operation base classes, TempURL keys in user info, and website listing formatter support.

It integrates with frontend Swift URL configuration (`rgw_swift_url_prefix`, `rgw_swift_account_in_url`, `rgw_swift_tenant_name`), stats/content-length options, Swift versioning config, placement targets, object expiration, object compression metadata, and S3-compatible backend operations.

## Risks
Swift compatibility depends on many subtle status/header differences. Changing generic RGW operation behavior without updating Swift overrides can break clients that expect `X-Account-*`, `X-Container-*`, TempURL, SLO, or `204` semantics.

Request body loops subtract `recv_body()`/`dump_body()` return values from unsigned counters. Negative returns are caught by exceptions in some paths but not uniformly checked before subtraction in all loops, so IO error paths need careful review.

Form POST validates against bucket owner temp URL keys after partially parsing multipart data. Incorrect owner lookup, account-name parsing, or prefix handling can reject valid uploads or permit wrong-key signatures.

SLO validation loads segment objects and handles compressed size adjustments. Mistakes in segment path parsing, size verification, or ETag composition can persist invalid large-object manifests.

Static website retargeting mutates request object state and sometimes takes over errors from earlier auth/setup failures. That path must avoid serving website content for authenticated requests unless `X-Web-Mode` explicitly opts in.

## Test Signals
Coverage should include Swift account/container/object listings with JSON/XML/plain formats, prefix/path/reverse/marker/end_marker/limit, account and container metadata headers, temp URL key visibility, quota headers, ACL headers, storage policy, versioning headers, object expiration, metadata removal, CORS options, DLO/SLO PUT/GET/DELETE, compressed SLO segments, bulk delete/upload streaming, form POST signatures and expiration, COPY and `X-Copy-From`, static website redirects/index/listings/error docs, URL prefix/account parsing, anonymous permission status mapping, and `/info`, cross-domain, and health-check endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_swift.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_swift.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_swift.h

## Purpose
`rgw_rest_swift.h` declares the Swift REST dialect classes used by RGW. It provides Swift-specific operation subclasses, form POST support, static website retargeting, service/bucket/object handlers, REST managers, and auxiliary public Swift endpoints.

## Important APIs, Types, and Functions
Operation subclasses include object GET/PUT/DELETE/COPY, account/container listing/stat/create/delete, metadata update operations, ACL placeholders, CORS OPTIONS, bulk delete/upload, and Swift `/info`. Most override `get_params()`, `verify_permission()`, `send_response()`, or metadata/expiration flags to match Swift behavior.

`RGWFormPost` derives from `RGWPostObj_ObjStore` and declares multipart parsing, tempurl signature verification, owner lookup, current-file accessors, data streaming, error mapping, response handling, and `is_formpost_req()`.

`RGWSwiftWebsiteHandler` is a helper owned by bucket/object handlers. It declares web-mode detection, directory marker/index checks, error document serving, and retargeting methods for bucket and object requests.

`RGWHandler_REST_SWIFT` is the common Swift handler with auth strategy reference, URL header parsing, bucket-name validation, initialization, authorization, and postauth setup. Service, bucket, object, info, cross-domain, and health-check handlers derive from it or `RGWHandler_REST`.

`RGWRESTMgr_SWIFT`, `RGWRESTMgr_SWIFT_CrossDomain`, `RGWRESTMgr_SWIFT_HealthCheck`, and `RGWRESTMgr_SWIFT_Info` expose protocol managers for Swift endpoint families.

## Control Flow
The manager chooses a service, bucket, or object handler based on URL parsing. The selected handler maps HTTP method plus request args to a concrete operation. Bucket/object handlers construct `RGWSwiftWebsiteHandler` during init and delegate retarget/error handling to it.

Form POST is selected by content type and boundary detection. Bulk upload/delete are selected by `extract-archive` and `bulk-delete` query args. COPY is converted to PUT in handler initialization.

## State and Persistence Behavior
The header declares request-local state such as reverse listing buffers, prefixes, SLO ETag, form parts, website handler optionals, and response status overrides. Durable state is updated by base RGW operations using parameters populated by these subclasses.

`RESTMgr_` classes keep no durable state. Website helper state is a set of non-owning pointers to driver, request state, and handler for one request.

## Dependencies and Integration Points
It depends on RGW op/rest base classes, Swift auth, HTTP errors, Boost optional/in-place helpers, and Swift ACL/CORS/auth implementation in the `.cc` file. It is integrated into the RGW auth strategy registry and frontend resource manager dispatch.

## Risks
Many classes are thin protocol overrides around generic RGW operations; missing an override can silently fall back to S3-like behavior. The website handler stores raw request pointers, so lifetime is tied to handler/request lifecycle.

ACL operation classes have empty responses, reflecting Swift ACL behavior through metadata headers rather than S3 ACL documents. Changes to generic ACL handling should not assume these classes produce bodies.

## Test Signals
Compile and dispatch coverage should instantiate each operation through service, bucket, and object handlers. Behavioral tests should exercise method-to-op mapping, formpost detection, website retargeting, bulk endpoint selection, metadata update paths, and auxiliary manager routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_swift.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_usage.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_usage.cc

## Purpose
`rgw_rest_usage.cc` implements admin-style REST operations for reading and trimming RGW usage records. It exposes GET for usage reporting and DELETE for usage log trimming through `RGWHandler_Usage`.

## Important APIs, Types, and Functions
`RGWOp_Usage_Get` derives from `RGWRESTOp`, requires `usage` read caps, parses `uid`, `bucket`, `tenant`, `start`, `end`, `show-entries`, `show-summary`, and comma-separated `categories`, optionally loads the target bucket, and calls `RGWUsage::show()`.

`RGWOp_Usage_Delete` requires `usage` write caps, parses the same target/time filters, optionally loads the bucket, requires `remove-all=true` for an unscoped full trim, and calls `RGWUsage::trim()`.

`RGWHandler_Usage::op_get()` and `op_delete()` allocate the two operation classes.

## Control Flow
The usage handler is S3-authenticated through its base class. GET builds filters and category map, then streams usage output through `flusher`. DELETE builds filters and either rejects an unqualified delete without explicit `remove-all`, or trims matching records.

## State and Persistence Behavior
GET is read-only and accesses persistent usage records through `RGWUsage::show()`. DELETE mutates usage-log persistence through `RGWUsage::trim()`. Bucket scoping uses `driver->load_bucket()` if a bucket name is provided; user scoping uses `driver->get_user(rgw_user(uid_str))`.

## Dependencies and Integration Points
The file depends on `rgw_usage.h`, REST arg helpers, SAL user/bucket APIs, `str_list` category parsing, and `RGWHandler_Usage` declarations. It integrates with admin caps and S3 auth via `RGWHandler_Auth_S3`.

## Risks
The delete operation has a guard against deleting all usage without `remove-all=true`; keeping that guard intact is important for operational safety. User objects are constructed even when `uid` is empty, so downstream `RGWUsage` behavior determines how empty users are interpreted.

## Test Signals
Tests should cover GET with user, bucket, tenant, time range, categories, entries/summary toggles, missing bucket errors, DELETE scoped by user/bucket/time, unscoped DELETE rejection without `remove-all`, and successful unscoped trim only with `remove-all=true`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_usage.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_usage.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_usage.h

## Purpose
`rgw_rest_usage.h` declares the S3-authenticated usage REST handler and manager for RGW usage reporting/trimming endpoints.

## Important APIs, Types, and Functions
`RGWHandler_Usage` derives from `RGWHandler_Auth_S3`, overrides GET and DELETE op factories, and bypasses `read_permissions()` by returning success.

`RGWRESTMgr_Usage` returns a new `RGWHandler_Usage` using the S3 auth registry.

## Control Flow
The manager produces a handler, the inherited S3 auth path authorizes the request, and method selection maps GET/DELETE to usage ops implemented in the `.cc` file.

## State and Persistence Behavior
The header contains no persistent state. It exposes read/write usage behavior through operation objects.

## Dependencies and Integration Points
It depends on `rgw_rest.h` and `rgw_rest_s3.h`. Integration is through S3 auth and whichever frontend resource path registers `RGWRESTMgr_Usage`.

## Risks
Because `read_permissions()` always returns 0, capability checks must remain in operation classes. Adding methods without explicit cap checks would bypass admin authorization expectations.

## Test Signals
Dispatch tests should verify GET/DELETE creation, S3 auth application, and operation-level caps for usage read/write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_usage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_user_policy.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_user_policy.cc

## Purpose
`rgw_rest_user_policy.cc` implements IAM-style user policy operations for RGW users. It supports inline user policies (`PutUserPolicy`, `GetUserPolicy`, `ListUserPolicies`, `DeleteUserPolicy`) and managed policy attachment operations (`AttachUserPolicy`, `DetachUserPolicy`, `ListAttachedUserPolicies`).

The file bridges IAM query parameters to RGW user attributes, account-aware user lookup, IAM permission evaluation, metadata-master forwarding, and XML IAM responses.

## Important APIs, Types, and Functions
`RGWRestUserPolicy` is the common base. It validates `UserName`, resolves account users by account id and name or tenant users by uid, constructs a user ARN, checks admin caps, and falls back to IAM permission evaluation against that ARN.

`RGWPutUserPolicy` validates `PolicyName` and `PolicyDocument`, parses the policy document, forwards mutating requests to the metadata master when needed, decodes the `RGW_ATTR_USER_POLICY` map, inserts/replaces the inline policy, enforces `rgw_user_policies_max_num`, encodes attrs, and stores the user through `retry_raced_user_write()`.

`RGWGetUserPolicy` and `RGWListUserPolicies` decode `RGW_ATTR_USER_POLICY` and emit one policy or a paginated policy-name list. `RGWDeleteUserPolicy` forwards to the master if needed, removes the inline policy, and treats missing policy as success after successful non-master forwarding.

`RGWAttachUserPolicy_IAM` validates a managed policy ARN, verifies the managed policy exists, forwards to the master if needed, decodes/updates `RGW_ATTR_MANAGED_POLICY`, and stores the user. `RGWDetachUserPolicy_IAM` removes an ARN from that attr. `RGWListAttachedUserPolicies_IAM` lists attached policy ARNs with pagination.

`RGWRestAttachedUserPolicy` rejects managed policy operations unless the authenticated identity belongs to an account, because managed policies are supported only for account users.

Factory functions `make_iam_attach_user_policy_op()`, `make_iam_detach_user_policy_op()`, and `make_iam_list_attached_user_policies_op()` expose these IAM operations to the IAM REST dispatcher.

## Control Flow
Every op first runs `init_processing()`: parse params, identify account-vs-tenant context, load the target user, and compute the target ARN. `verify_permission()` rejects anonymous callers, accepts users with `user-policy` caps, or evaluates IAM action permission against the target user ARN.

Mutating inline and managed policy ops validate input, forward the original IAM request body to the metadata master if this zone is not master, and then update user attrs under `retry_raced_user_write()`. Read/list ops decode attrs and directly emit XML.

Pagination uses `std::map`/`std::set` ordering with `lower_bound(marker)` and `MaxItems` capped at 1000. Truncated responses return the next marker value.

## State and Persistence Behavior
Inline user policies are persisted as an encoded `std::map<std::string, std::string>` in `RGW_ATTR_USER_POLICY` on the user. Managed policy attachments are persisted as encoded `rgw::IAM::ManagedPolicies` in `RGW_ATTR_MANAGED_POLICY`.

All user attr mutations call `user->store_user()` inside `retry_raced_user_write()`, preserving concurrent metadata updates. Mutating requests are forwarded to the metadata master via `forward_iam_request_to_master()` with IAM action/version/user/policy args removed from forwarded args.

Request-local state includes `account_id`, loaded `user`, `user_arn`, policy names/documents, managed policy ARN, marker/max item fields, and the original POST body for forwarding.

## Dependencies and Integration Points
The file depends on IAM validation helpers, managed policy lookup, policy parser, RGW process environment, IAM REST forwarding, SAL user/account APIs, site metadata-master config, RGW user attrs, and IAM XML namespace formatting.

It integrates with `rgw_rest_iam` via factory functions and with account identity through `s->owner.id` and `s->auth.identity->get_account()`.

## Risks
There are subtle sign conventions: some paths assign positive `ERR_NO_SUCH_ENTITY` while most use negative `-ERR_*`. Response/error translation must continue to handle these correctly.

Forwarding strips query args before forwarding. If new required parameters are added and not stripped or preserved correctly, master-zone replay may diverge from local validation.

Managed policies are intentionally limited to account users. Relaxing that check could attach broad account policy semantics to tenant users. Inline policy tenant restriction differs between account and non-account users, so policy parsing must preserve that boundary.

## Test Signals
Tests should cover account user lookup by `UserName`, tenant uid lookup, invalid user/policy names and ARNs, anonymous denial, admin cap allow, IAM permission allow/deny, malformed policy documents, policy count limits, metadata-master forwarding, raced user writes, get/list/delete missing policy behavior, attach unknown managed policy, account-only managed policy enforcement, pagination markers/max items, and decoding errors for corrupted attrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_user_policy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_user_policy.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_user_policy.h

## Purpose
`rgw_rest_user_policy.h` declares IAM user policy operation classes and factory functions used by RGW's IAM REST layer.

## Important APIs, Types, and Functions
`RGWRestUserPolicy` derives from `RGWRESTOp` and stores the IAM action id, required admin cap, account id, loaded SAL user, target user ARN, policy name, user name, and policy document. It declares common parameter parsing, initialization, caps, permission verification, and response handling.

`RGWPutUserPolicy`, `RGWGetUserPolicy`, `RGWListUserPolicies`, and `RGWDeleteUserPolicy` declare inline policy operations and operation type/name overrides. Mutating classes store the POST body for metadata-master forwarding.

The three factory functions expose managed-policy attach/detach/list operations without publishing their concrete implementation classes in the header.

## Control Flow
IAM dispatch code constructs these operations from action names. Common initialization resolves the target user and permissions before each concrete `execute()` reads or mutates policy attrs.

## State and Persistence Behavior
The header declares state needed to persist inline policy maps and managed policy sets in user attrs. Actual encoding/store logic is implemented in the `.cc` file.

## Dependencies and Integration Points
It depends on ARN types, REST base classes, user types, and SAL forward declarations. Integration is through IAM REST action factories and RGW user metadata storage.

## Risks
The base class declares `validate_input()` but this file's implementation does not define/use it in the visible source, so callers should rely on `get_params()`/IAM validation helpers instead. Concrete managed-policy classes are hidden, limiting compile-time coupling but making factory behavior important.

## Test Signals
Build and dispatch tests should ensure IAM action factories return the right operation types, base initialization remains shared, and operation names/types match IAM audit and response expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_user_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_zero.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_zero.cc

## Purpose
`rgw_rest_zero.cc` implements a lightweight unauthenticated REST endpoint for benchmarking the RGW HTTP frontend without backend object IO. It models a single in-memory resource whose only durable-for-process property is a byte size; GET returns that many zero bytes, HEAD reports the size, PUT consumes and discards a request body while setting size, and DELETE resets size to zero.

## Important APIs, Types, and Functions
`ZeroResource` contains a mutex and `std::size_t size`. All paths handled by the manager share this one resource.

`ZeroOp` is the base operation. It permits all requests and sends headers using `response_content_type` and `response_content_length`.

`ZeroDeleteOp` locks the resource and sets size to zero. `ZeroHeadOp` locks and reports current size with `application/octet-stream`. `ZeroGetOp` locks to read size, sends headers, then writes zero-filled chunks up to `rgw_max_chunk_size`. `ZeroPutOp` requires `Content-Length`, parses it, reads and discards exactly that many bytes in chunks, and on success stores the new size.

`ZeroHandler` disables auth/permission checks and maps DELETE/GET/HEAD/PUT to the zero operations. `RESTMgr_Zero` owns the shared `ZeroResource` and returns a `ZeroHandler`.

## Control Flow
The manager returns a handler for any path under the endpoint. The handler creates an operation by HTTP method. PUT validates and drains the body before updating shared size. GET sends response headers first and then streams zero bytes until the recorded size is exhausted. HEAD does not send a body. DELETE is immediate.

## State and Persistence Behavior
State is process-local only. `ZeroResource::size` is protected by a mutex but is not stored in RADOS or any external backend. It resets when the RGW process restarts. PUT changes size only after the whole request body is read successfully.

## Dependencies and Integration Points
The file depends on RGW REST base classes, body IO helpers `recv_body()` and `dump_body()`, `rgw_max_chunk_size`, and Ceph `parse<size_t>()`. It lives in namespace `rgw` and integrates through `RESTMgr_Zero`.

## Risks
The GET and PUT loops subtract the return value from `dump_body()`/`recv_body()` without explicitly handling non-exception negative returns. If those helpers can return negative integers without throwing, the unsigned `remaining` counter could underflow. The endpoint is unauthenticated by design, so it should only be exposed intentionally.

Large `Content-Length` values can drive long drain/send loops and frontend bandwidth use even though there is no backend IO. This is expected for benchmarking but risky on public endpoints.

## Test Signals
Tests should cover PUT missing/invalid content length, PUT with zero and nonzero lengths, HEAD after PUT/DELETE, GET byte count and content type, concurrent PUT/GET/DELETE mutex behavior, request body read failures, response body write failures, and process-local reset semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_zero.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_zero.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_rest_zero.h

## Purpose
`rgw_rest_zero.h` declares the zero REST manager, an unauthenticated benchmarking endpoint that avoids backend reads/writes and serves a shared in-memory zero-byte resource.

## Important APIs, Types, and Functions
`ZeroResource` is forward declared. `RESTMgr_Zero` derives from `RGWRESTMgr`, owns a `std::unique_ptr<ZeroResource>`, constructs it, and overrides `get_handler()` to create a request handler.

## Control Flow
Frontend registration creates one `RESTMgr_Zero`. Each request asks it for a handler, and the handler uses the shared resource to service GET/HEAD/PUT/DELETE as implemented in the `.cc` file.

## State and Persistence Behavior
The manager owns process-local state only. `ZeroResource` is not persisted and exists for the lifetime of the manager.

## Dependencies and Integration Points
It depends on `<memory>` and `rgw_rest.h`. It integrates with RGW REST manager registration and uses the auth strategy registry only as an unused `get_handler()` parameter.

## Risks
The endpoint intentionally bypasses authentication and backend storage. It should remain isolated from normal object namespaces and only be enabled for benchmarking or diagnostics.

## Test Signals
Tests should confirm manager construction, handler creation with unused auth registry, shared state across paths handled by one manager, and no backend SAL calls for zero endpoint operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_rest_zero.h -->
