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
