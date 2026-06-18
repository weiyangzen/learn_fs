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
