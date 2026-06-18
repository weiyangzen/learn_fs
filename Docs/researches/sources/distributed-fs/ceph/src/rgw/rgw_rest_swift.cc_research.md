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
