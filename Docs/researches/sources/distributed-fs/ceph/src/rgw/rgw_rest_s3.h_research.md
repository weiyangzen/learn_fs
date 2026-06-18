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
