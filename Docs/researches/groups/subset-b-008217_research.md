<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/s3request.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/s3request.py

## Purpose
Implements the S3-facing request object used by Swift's `s3api` middleware. It detects SigV2 versus SigV4 requests, parses virtual-host and path-style bucket/key addressing, validates S3 headers and request bodies, converts S3 operations into internal Swift `Request` objects, and translates Swift responses/errors back into S3 response classes. It is the central adapter between S3 protocol semantics and Swift proxy semantics.

## Important APIs, types, and functions
`get_request_class(env, s3_acl)` chooses `S3Request`, `SigV4Request`, `S3AclRequest`, or `SigV4S3AclRequest`. `S3Request.__init__` parses auth, bucket/key, validates headers, installs body wrappers, and publishes `environ['s3api.auth_details']` for auth middleware. `SigV4Mixin`, `SigCheckerV2`, and `SigCheckerV4` build canonical strings and validate signatures. `StreamingInput`, `ChunkReader`, `HashingInput`, and `ChecksummingInput` enforce aws-chunked framing, chunk signatures, `x-amz-content-sha256`, and S3 checksum headers/trailers. `to_swift_req`, `_get_response`, `get_response`, `get_container_info`, and `gen_multipart_manifest_delete_query` are the main Swift integration methods. `S3AclRequest` adds pre-authentication and ACL handler dispatch.

## Control flow
Construction first parses credentials from query/header auth, resolves `bucket_in_host` and path components, then validates content length, copy-source, storage class, SSE, MD5, SHA256, checksum, and unsupported headers. For PUT/POST it wraps `wsgi.input` before downstream Swift reads so body validation happens during streaming. The selected signature checker's string-to-sign is frozen before request mutation. Controllers are chosen from subresources such as `acl`, `delete`, `uploadId`, `uploads`, `partNumber`, `tagging`, and `object-lock`. `to_swift_req` rewrites metadata, copy-source headers, path, query, method, and logging/source environ entries. `_get_response` calls the downstream app, records backend path and policy index, builds an `S3Response`, accepts only operation-specific success codes, and maps known Swift status codes to S3 errors.

## State and persistence behavior
The object keeps per-request state: account, user id, policy index, signing timestamp, signature checker, bucket/object names, and ACL handler. It mutates the WSGI environ with `s3api.auth_details`, `swift.access_logging`, `swift.leave_relative_location`, `swift.source`, `s3api.backend_path`, and sometimes auth override fields. Persistent storage is indirect: encoded ACL sysmeta can be attached through `bucket_acl` and `object_acl`; multipart/SLO delete decisions depend on stored object sysmeta and headers. Body wrappers are stateful stream validators and close the underlying input on protocol errors.

## Dependencies and integration points
Depends on Swift `swob`, request helpers, container info, registry info, checksum helpers, and S3 API controllers/exceptions. It integrates with `s3token` via `s3api.auth_details`, with Keystone/tempauth through downstream TEST/HEAD calls, with SLO via `MULTIUPLOAD_SUFFIX` and multipart manifest delete query generation, with ACL handlers through `handle_acl_header` and `decode_acl`, and with proxy logging via mutable `swift.access_logging`.

## Risks and test signals
High-risk paths are SigV4 canonicalization, duplicated raw header handling, old boto host-port compatibility, aws-chunked trailer parsing, checksum header/trailer cardinality, query mutation after signing, and Swift-to-S3 error translation. Tests should cover SigV2/SigV4 header and query auth, clock skew and expiry errors, chunk signature mismatch, trailer checksum mismatch, malformed content length/MD5/SHA256, virtual-host bucket parsing, metadata underscore preservation, copy-source version handling, ACL pre-authentication, multipart part-number range behavior, and all Swift status mappings including 429/503/409/404 variants.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/s3request.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/s3response.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/s3response.py

## Purpose
Defines the S3 response layer for `s3api`: normal response header normalization, Swift-to-S3 header translation, SLO/multipart ETag presentation, copy response bodies, and a large catalog of XML-formatted S3 error responses.

## Important APIs, types, and functions
`HeaderKeyDict` preserves S3 casing expectations, notably `ETag` and lowercase `x-amz-*`. `translate_swift_to_s3(key, val)` converts Swift object/container headers into S3-compatible headers and drops internal-only headers. `S3Response` wraps `swob.Response`, extracts S3 sysmeta, handles legacy `swift3` sysmeta, records `sw_headers` and `sysmeta_headers`, and exposes `from_swift_resp`. `append_copy_resp_body` emits `CopyObjectResult`/`CopyPartResult` XML. `ErrorResponse` serializes S3 error XML and produces metric names; subclasses encode specific S3 status/code/message combinations.

## Control flow
On response construction, all incoming headers are split into S3 sysmeta and ordinary Swift headers. Ordinary headers are translated, sysmeta can override multipart ETag, and SLO responses without stored AWS-style ETags get a `-N` suffix to discourage client-side validation assumptions. Errors lazily generate XML bodies in `_body_iter`, adding `RequestId` after WSGI environ is available, then render nested info dictionaries as XML tags.

## State and persistence behavior
`S3Response` stores translated public headers, raw Swift headers, and S3 sysmeta headers for later ACL and multipart decisions. It does not persist data itself, but it interprets persisted sysmeta such as `x-object-sysmeta-s3api-etag` and old `swift3` keys. `ErrorResponse` stores per-instance `_msg`, `reason`, and structured `info` used for response bodies and metrics.

## Dependencies and integration points
Used by `s3request` and all S3 controllers as the common response/error vocabulary. It depends on Swift header utilities, `is_sys_meta`, S3 XML helpers, S3 utility naming functions, server-side encryption cipher conversion, and object-versioning delete-marker content type. It is also the bridge that exposes SLO/multipart fields as `x-amz-mp-parts-count`, `x-amz-version-id`, `x-amz-copy-source-version-id`, and delete-marker headers.

## Risks and test signals
Risks include leaking Swift/internal headers, incorrect casing for client SDKs, stale legacy sysmeta precedence, malformed XML from invalid info values, and mismatched SLO ETag semantics. Tests should assert header allow/drop behavior, user metadata underscore restoration, CORS header translation, expiration and encryption header translation, copy response XML, RequestId injection, metric names, and constructor behavior for error subclasses that require bucket/key/version arguments.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/s3response.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/s3token.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/s3token.py

## Purpose
Provides the WSGI middleware that authenticates S3 requests against Keystone's `s3tokens` API. It consumes the auth details prepared by `s3request`, validates or locally revalidates the signature using a cached EC2 secret, injects Keystone identity headers, and rewrites the Swift account path to the authenticated tenant account.

## Important APIs, types, and functions
`parse_v2_response` and `parse_v3_response` map Keystone token responses to `X-Identity-Status`, roles, user, tenant/project, and domain headers. `S3Token.__init__` validates config, builds the Keystone `.../s3tokens` endpoint, configures TLS verification, optional service auth, and optional secret caching. `_json_request` posts credentials to Keystone. `__call__` is the middleware path. `filter_factory` wires paste.deploy configuration.

## Control flow
The middleware purges client-supplied Keystone auth headers unless a prior token has already been set. It ignores non-Swift paths or requests without `s3api.auth_details`. It base64-url encodes the string-to-sign as the Keystone token payload, splits access keys with an optional forced tenant suffix, and checks memcache for `(headers, tenant, secret)`. Cached secrets are accepted only if `check_signature(secret)` succeeds. On cache miss it posts credentials to Keystone, parses v2/v3 JSON, optionally caches the EC2 secret via a Keystone v3 client, stores `keystone.token_info`, injects identity headers, and rewrites `PATH_INFO` from the access-key account to `reseller_prefix + tenant_id`.

## State and persistence behavior
Process state includes request URI, timeout, reseller prefix, TLS verification, service Keystone client, and cache duration. Per-request state is carried in environ and headers. Optional persistence is memcache key `s3secret/<access>` containing parsed headers, tenant, and secret for a bounded duration. It intentionally removes untrusted identity headers from the request boundary.

## Dependencies and integration points
Depends on `requests`, `keystoneauth1`, `keystoneclient.v3`, Swift `Request`, memcache helpers, logging, and `s3request`'s `s3api.auth_details`. Downstream middleware receives Keystone-compatible identity headers and a rewritten account path. The service auth path integrates with Keystone installations that require an authenticated caller for `s3tokens`.

## Risks and test signals
Risks include accepting stale or wrong cached secrets, path rewrite mistakes when account names repeat in the path, service-auth misconfiguration silently disabling caching, and `delay_auth_decision` changing security behavior by forwarding failed auth downstream. Tests should cover v2/v3 response parsing, auth URI validation, TLS option precedence, header purge, cache hit with valid/invalid signature, Keystone non-2xx responses with and without delayed auth, malformed Keystone JSON, forced tenant access keys, and PATH_INFO rewriting with reseller prefix.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/s3token.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/subresource.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/subresource.py

## Purpose
Implements S3 ACL subresource data structures and conversions. It translates between S3 ACL XML/header models and compact JSON stored in Swift sysmeta, defines canonical users and predefined groups, and checks owner/permission access when S3 ACL enforcement is enabled.

## Important APIs, types, and functions
`encode_acl(resource, acl)` writes ACL JSON to `x-*-sysmeta-s3api-acl`; `decode_acl(resource, headers, allow_no_owner)` reconstructs an `ACL`. `Grantee`, `User`, `Group`, `AuthenticatedUsers`, `AllUsers`, and `LogDelivery` model S3 grantees. `Grant` pairs a grantee with a permission. `ACL` serializes XML, parses XML with `from_elem`, builds ACLs from request headers with `from_headers`, and enforces `check_owner`/`check_permission`. `canned_acl` and `ACLPrivate`/`ACLPublicRead`/... produce AWS canned ACLs.

## Control flow
Incoming ACL XML is parsed into owner and grants. Incoming grant headers are parsed by `Grantee.from_header`; canned ACLs expand through `canned_acl_grantees`. Supplying both canned ACL and explicit grant headers raises `InvalidRequest`. ACL persistence encodes owner id and grant tuples as JSON. Permission checks first bypass enforcement when `s3_acl` is false, then allow owners full control, then scan grants for `FULL_CONTROL` or the requested permission.

## State and persistence behavior
The persistent representation is a JSON object with `Owner` and `Grant` entries stored in Swift sysmeta. In-memory `ACL` instances hold owner, grant list, `s3_acl`, and `allow_no_owner` flags. `allow_no_owner` can make missing owner metadata effectively public for compatibility. `LogDelivery` membership is derived from the user portion of the Swift user id and the `.log_delivery` marker.

## Dependencies and integration points
Used by `s3request` ACL properties and `S3AclRequest.get_acl_response`, and by ACL controllers/handlers. It depends on S3 XML helpers, S3 response errors, `sysmeta_header`, Swift JSON utilities, and `InvalidSubresource` for corrupt stored ACLs. It also interacts with bucket logging through the `LogDelivery` predefined group.

## Risks and test signals
Risks include overly broad public access because `AllUsers` and `AuthenticatedUsers` both return true in this signed-request model, no support for email grantees, malformed or legacy sysmeta causing `InvalidSubresource`, and permission strings outside the fixed set raising not implemented. Tests should cover canned ACL expansion, explicit grant headers, conflict between canned and explicit grants, XML parse/render, encode/decode round trip, corrupt JSON handling, owner bypass, missing-owner compatibility, and log-delivery membership.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/subresource.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/utils.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/utils.py

## Purpose
Collects small S3 API helpers for sysmeta names, naming conversions, request detection, bucket/key parsing, cipher mapping, S3 timestamp formatting, time parsing, and typed middleware configuration.

## Important APIs, types, and functions
`sysmeta_prefix` and `sysmeta_header` centralize S3 sysmeta header names. `camel_to_snake`, `snake_to_camel`, and `make_header_label` support XML/error/header conversions. `unique_id`, `utf8encode`, and `utf8decode` are encoding helpers. `classify_checksum_header_value` categorizes checksum-looking values. `validate_bucket_name`, `get_s3_access_key_id`, `is_s3_req`, `parse_host`, `parse_path`, and `extract_bucket_and_key` implement S3 request identification and bucket/key extraction. `convert_swift_to_s3_cipher` exposes Swift crypto ciphers as S3 SSE values. `S3Timestamp` adds S3 XML and AWS date formats. `mktime` parses RFC2822/S3 date strings. `Config` supplies default typed config.

## Control flow
Bucket parsing first detects bucket-in-host from configured storage domains, strips host ports, then validates path or host bucket names using DNS-compatible rules when enabled. Invalid URI or bucket names are raised as parse exceptions for callers to translate. `Config.update` and `__setitem__` preserve boolean and integer types based on existing defaults.

## State and persistence behavior
There is no external persistence. `Config` is mutable per middleware/request configuration and defaults include storage domains, region, multipart enablement, no-owner behavior, clock skew, rate-limit error style, and max upload part number. Timestamp helpers convert between Swift timestamps and S3/API wire formats.

## Dependencies and integration points
Used broadly by `s3request`, `s3response`, ACL code, and controllers. It depends on Swift constraints for UTF-8 path validation, Swift `Timestamp`, config parsing, and S3 parse exceptions. Cipher mapping integrates with Swift encryption metadata translated by `s3response`.

## Risks and test signals
Risks include bucket-name compatibility differences when DNS compliance is disabled, host suffix ambiguity for storage domains, weak base64 validation that only decodes without strict size checks, and integer config values silently retaining defaults when set to empty strings. Tests should cover DNS and legacy bucket names, IP-address rejection, invalid UTF-8 paths, virtual-host parsing with ports and multiple storage domains, SigV2/SigV4 access-key extraction, S3 date parsing with timezone offsets, timestamp round trips, and typed `Config` overrides.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/utils.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/slo.py -->
# sources/object-store/openstack-swift/swift/common/middleware/slo.py

## Purpose
Implements Swift Static Large Object middleware. It lets clients store a manifest that references object segments and inline data, validates manifests on PUT, serves concatenated large objects on GET/HEAD, exposes raw/transformed manifests, supports part-number and range reads, deletes segments synchronously or asynchronously, and adjusts container listings to expose SLO ETags.

## Important APIs, types, and functions
`parse_and_validate_input` validates uploaded manifest JSON. `_annotate_segments`, `calculate_byterange_for_part_num`, and `calculate_byteranges` prepare segment metadata for reads. `RespAttrs` extracts SLO state from response headers and calculates legacy size/ETag when needed. `SloGetContext` handles GET/HEAD, manifest refetching, sub-SLO recursion, range slicing, and `SegmentedIterable` construction. `StaticLargeObject` is the WSGI middleware with handlers for multipart PUT, GET/HEAD, DELETE, async delete, segment discovery, and container listings. `filter_factory` registers cluster-visible SLO capabilities.

## Control flow
Manifest PUT enforces content length/size limits, parses JSON, validates object-backed and inline segments, HEADs each unique object path concurrently, normalizes ranges, checks size/ETag constraints, applies optional `swift.callback.slo_manifest_hook`, calculates the SLO ETag, stores JSON plus `X-Static-Large-Object`, `SYSMETA_SLO_ETAG`, `SYSMETA_SLO_SIZE`, manifest MD5 ETag, and content-type `swift_bytes`. Heartbeat mode returns early `202 Accepted` and later embeds final status in the body. GET/HEAD first asks object servers to ignore Range for manifests and to use SLO ETag sysmeta for conditionals. If needed, it refetches the full manifest, annotates segments, handles part-number and range math, recursively expands sub-SLOs to depth 10, and streams segments through `SegmentedIterable`. DELETE with `multipart-manifest=delete` walks nested manifests and uses bulk delete, or async delete when allowed and all segments are simple objects in one container.

## State and persistence behavior
Persistent state is the manifest object body plus object sysmeta `slo-etag` and `slo-size`, `X-Static-Large-Object`, and content-type `swift_bytes`. Container listings carry `slo_etag` as an ETag parameter that `handle_container_listing` exposes separately. Runtime state includes rate-limit settings, max manifest size/segments, concurrency, bulk deleter, expirer config, sub-SLO LRU cache, and response header/status captured by `WSGIContext`. Inline data is stored base64 in the manifest and decoded to `raw_data` for serving.

## Dependencies and integration points
Integrates with Swift WSGI, object-server manifest metadata, `SegmentedIterable`, bulk delete middleware, object expirer, container listings, request helper ETag/range utilities, container authorization, and proxy logging via `swift.source='SLO'`. It is also consumed by S3 multipart flows through S3 request/response handling and multipart-manifest query generation.

## Risks and test signals
High-risk areas are manifest validation edge cases, concurrent HEAD validation, legacy manifest fallback, recursive sub-SLO expansion, ranged and part-number responses, heartbeat response formatting, async delete authorization and expirer enqueueing, and content-type `swift_bytes` accounting. Tests should cover invalid JSON and schema errors, self-referential manifests, inline-only rejection, base64 normalization, object segment size/ETag/range mismatches, max segment and manifest size limits, client ETag mismatch, GET/HEAD conditionals, 206/416 part-number behavior, range slicing across inline/object/sub-SLO segments, recursion-depth failure, broken segment 409, sync and async delete restrictions, and JSON container listing ETag rewriting.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/slo.py -->
