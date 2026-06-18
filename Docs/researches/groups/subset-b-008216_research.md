# subset-b-008216 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/list_endpoints.py -->
# sources/object-store/openstack-swift/swift/common/middleware/list_endpoints.py

Purpose: WSGI middleware exposing an unauthenticated `/endpoints/` REST API that maps a Swift account, container, or object to the internal storage-node endpoint URLs that would serve it. It is intended for trusted in-cluster clients such as Hadoop locality integrations.

Important APIs and control flow: `ListEndpointsMiddleware` loads account and container rings at construction, lazily gets object rings with `POLICIES.get_object_ring`, parses optional `v1` or `v2` response versions, and rejects non-GET requests with `HTTPMethodNotAllowed`. `__call__` unquotes account/container/object names, queries the appropriate ring, builds `http://ip:port/device/partition/...` endpoints, and formats v1 as a JSON list or v2 as a JSON object with backend headers. Object lookups call `get_container_info(..., swift_source='LE')` to discover the storage policy before choosing the object ring.

State, dependencies, and integration: Persistent state is ring files under `swift_dir`; request-time state is only local variables. It integrates with Swift rings, storage policies, and proxy controller container-info lookups.

Risks and test signals: The module deliberately bypasses auth, so pipeline placement and network exposure are critical. Tests should cover version parsing, default version fallback, invalid versions, percent-encoding, object policy headers, custom endpoint paths, non-GET rejection, and account/container/object ring selection.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/list_endpoints.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/listing_formats.py -->
# sources/object-store/openstack-swift/swift/common/middleware/listing_formats.py

Purpose: Normalizes Swift account and container listings so clients can request `text/plain`, JSON, or XML while downstream Swift apps are forced to return JSON for conversion.

Important APIs and control flow: `get_listing_content_type` honors `format=` and `Accept`, raising `HTTPBadRequest` for invalid Accept parsing and `HTTPNotAcceptable` when no supported type matches. `account_to_xml`, `container_to_xml`, and `listing_to_text` convert JSON listing records. `ListingFilter.__call__` only handles valid account/container `GET` and `HEAD` requests, injects `format=json`, sets `swift.format_listing`, calls the downstream app, and only rewrites successful JSON responses below `MAX_CONTAINER_LISTING_CONTENT_LENGTH`. It adds `Vary: Accept` when negotiation was by Accept header, rewrites HEAD content metadata without consuming the body, filters reserved names unless `req.allow_reserved_names`, and returns 204 when the converted body is empty.

State, dependencies, and integration: No persistent state. It depends on swob requests, `HeaderKeyDict`, `valid_api_version`, `RESERVED`, and downstream JSON listing contracts.

Risks and test signals: Conversion mutates listing dictionaries with `pop`, so tests should pass fresh structures. Staticweb or non-JSON responses are intentionally passed through. Cover Accept negotiation, bad JSON fallback, large content-length fallback, reserved-name warnings, XML shape for account/container records, HEAD behavior, and empty-list 204 handling.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/listing_formats.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/memcache.py -->
# sources/object-store/openstack-swift/swift/common/middleware/memcache.py

Purpose: Minimal WSGI middleware that loads Swift's configured memcache client once and injects it into each request environment as `swift.cache`.

Important APIs and control flow: `MemcacheMiddleware.__init__` records the downstream app, creates a route-specific logger, and calls `load_memcache(conf, logger)`. `__call__` assigns the resulting client to `env['swift.cache']` before delegating. `filter_factory` merges global and local PasteDeploy config and returns the filter wrapper.

State, dependencies, and integration: The only long-lived state is the loaded memcache client object. It is consumed by other middleware such as ratelimit, auth, account/container info caches, and request helper code via `cache_from_env` or direct `swift.cache` access.

Risks and test signals: Because every request gets the same client reference, tests should verify initialization happens once and request environ injection happens every time. Misconfiguration or unavailable memcache is mostly handled inside `load_memcache`; integration tests should cover downstream middleware behavior when `swift.cache` is absent versus present.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/memcache.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/name_check.py -->
# sources/object-store/openstack-swift/swift/common/middleware/name_check.py

Purpose: Rejects account, container, or object paths containing forbidden characters, excessive path length, or forbidden path substrings such as `/.` and `/..`.

Important APIs and control flow: `NameCheckMiddleware` reads `forbidden_chars`, `maximum_length`, and `forbidden_regexp` from config, compiles the regexp when set, registers its config through `register_swift_info`, and logs through the `name_check` route. `check_character`, `check_length`, and `check_regexp` operate on `Request.path_info`. `__call__` wraps the environ in `Request`, returns `HTTPBadRequest` with a specific message on the first failed check, or delegates to the downstream app.

State, dependencies, and integration: State is immutable middleware configuration plus the compiled regex. It depends on `swift.common.swob`, `get_logger`, and the Swift info registry. It is designed to sit early in the proxy pipeline after initial proxy logging.

Risks and test signals: Regex configuration can make otherwise valid Swift names unavailable or impose CPU-heavy matching if poorly chosen. Tests should cover default forbidden characters, disabled regex, custom regex, maximum length boundaries, WSGI `path_info` encoding behavior, and that downstream is not called on rejection.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/name_check.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/proxy_logging.py -->
# sources/object-store/openstack-swift/swift/common/middleware/proxy_logging.py

Purpose: Implements Swift proxy access logging and StatsD metrics, including request/response byte counts, timing, time-to-first-byte, policy labels, anonymization, sensitive-header redaction, and support for double proxy-logging pipeline placement.

Important APIs and control flow: `CallbackInputProxy` wraps `wsgi.input` so reads can trigger byte-transfer callbacks. `BufferXferEmitCallback` accumulates streaming byte counts and periodically emits labeled metrics. `ProxyLoggingMiddleware.__init__` builds the log template, anonymization settings, header logging policy, valid method list, access logger, labeled statsd client, and streaming metric interval. `__call__` creates request labels, avoids duplicate access logs via `swift.proxy_access_log_made`, wraps input, captures downstream `start_response`, enforces content length with `ByteEnforcer`, emits first-byte metrics for GET, streams response bytes, records disconnects as 499 and exceptions as 500, and logs in a `finally` block.

State, dependencies, and integration: Per-process state includes PID, log config, statsd clients, and storage-domain config. Per-request state lives in environ keys such as `swift.base_labels`, `swift.proxy_logging_status`, `swift.backend_path`, and `swift.source`. It integrates with S3 request detection, storage policies, sensitive header registries, and catch-errors byte enforcement.

Risks and test signals: Logging must not leak sensitive values and must not double-count subrequests. Tests should cover template validation, anonymization, HEAD content length, generator close, downstream exceptions, invalid content-length, labeled S3 base-label updates, policy metrics, `access_log_headers_only`, and streaming metric flush on EOF.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/proxy_logging.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/ratelimit.py -->
# sources/object-store/openstack-swift/swift/common/middleware/ratelimit.py

Purpose: Enforces account, container, listing, and account-wide write rate limits using memcache as a distributed leaky-bucket clock.

Important APIs and control flow: `interpret_conf_limits` parses size-threshold config into interpolation functions; `get_maxrate` chooses the applicable rate by container size. `RateLimitMiddleware` loads account, container, listing, whitelist, blacklist, clock, buffer, and sleep settings. `get_ratelimitable_key_tuples` derives memcache keys for account container PUT/DELETE, object writes, container listings, and account sysmeta `global-write-ratelimit`. `_get_sleep_time` increments a memcache timestamp key, calculates required sleep, resets stale buckets, decrements on max-sleep rejection, and ignores memcache connection failures. `handle_ratelimit` fetches account info, honors whitelist/blacklist sysmeta, sleeps when needed, and returns custom 497/498 responses on hard denials.

State, dependencies, and integration: Persistent coordination is in memcache keys. Request state includes `swift.ratelimit.handled` to avoid duplicate handling. It depends on `cache_from_env`, account/container info helpers, and Swift info registration.

Risks and test signals: Missing memcache disables protection. Clock accuracy, max sleep, and stale bucket resets are subtle. Tests should cover interpolation, black/white lists, sysmeta overrides, duplicate handling, memcache errors, max-sleep rollback, global write limits, and pipeline behavior without valid Swift paths.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/ratelimit.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/read_only.py -->
# sources/object-store/openstack-swift/swift/common/middleware/read_only.py

Purpose: Blocks write methods for an entire cluster or for individual accounts marked read-only through account sysmeta.

Important APIs and control flow: `ReadOnlyMiddleware.__init__` reads cluster `read_only`, builds the write-method set as `COPY`, `POST`, `PUT`, and optionally `DELETE`, and records a logger. `__call__` passes through non-write methods and non-Swift paths, parses the account from `/v1/...`, handles `COPY` with `Destination-Account` by validating the destination account, then calls `account_read_only`. If read-only applies, it returns `HTTPMethodNotAllowed`; otherwise it delegates. `account_read_only` calls `get_info(..., swift_source='RO')` and lets account sysmeta `read-only` override the cluster default when present.

State, dependencies, and integration: State is config-only. It depends on account info cache/proxy lookups, `check_account_format`, `valid_api_version`, and optional registration of `read_only` in `/info`.

Risks and test signals: COPY destination semantics are easy to miss because the write target may differ from the source account. Tests should cover cluster read-only true/false, account sysmeta true/false overrides, `allow_deletes`, invalid paths, invalid API versions, and Destination-Account validation.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/read_only.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/recon.py -->
# sources/object-store/openstack-swift/swift/common/middleware/recon.py

Purpose: Provides unauthenticated `/recon/...` monitoring endpoints for Swift account, container, and object servers, aggregating local system metrics, recon-cache JSON files, ring hashes, device state, and service version information.

Important APIs and control flow: `ReconMiddleware.__init__` derives devices, swift_dir, recon cache paths, and all ring paths including policy-specific object rings. `_from_recon_cache` reads selected keys from JSON cache files and returns `None` values on failures. Getter methods expose `/proc` load, memory, mounts, sockstat, current time, device listings, unmounted/disk usage via `check_mount`, quarantine counts via directory link counts, ring and swift.conf md5 sums, and recon cache groups for async, replication, reconstruction, updater, expirer, auditor, sharding, driveaudit, and relinker. `GET` dispatches based on `/recon/<check>/<type>`, serializes JSON, returns 404 for unknown paths, and 500 when a known handler returns `None`.

State, dependencies, and integration: Persistent inputs are recon cache JSON files, ring files, swift.conf, device directories, and `/proc`. It integrates with daemon-written recon files and storage policy configuration.

Risks and test signals: Endpoints reveal operational topology and should stay on trusted networks. Tests should cover missing and malformed cache files, ENOENT ignore behavior, device mount errors, ring hash IOError handling, quarantine link-count math, dispatch status codes, and policy ring inclusion.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/recon.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/__init__.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/__init__.py

Purpose: Empty package initializer for `swift.common.middleware.s3api`.

Important APIs and control flow: The file defines no runtime symbols, exports, imports, or side effects. Its role is to mark the `s3api` directory as a Python package so sibling modules such as `s3api.py`, `s3request`, `s3response`, controllers, ACL helpers, and XML utilities can be imported by fully qualified Swift module paths.

State, dependencies, and integration: No state or dependencies are present. Integration is purely package-structure related.

Risks and test signals: Functional risk is low. Packaging tests should ensure this module can be imported and that PasteDeploy entry points resolve the s3api package in the expected environment.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/acl_handlers.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/acl_handlers.py

Purpose: Provides per-controller ACL enforcement logic for S3 API requests, keeping permission checks out of controller business logic.

Important APIs and control flow: `get_acl_handler` maps controller names to handler classes. `BaseAclHandler` creates scoped handler copies, dispatches method-specific ACL logic, HEADs object or container resources to retrieve ACLs, maps S3 method plus Swift method/resource through `ACL_MAP`, and checks the current user against the required permission. `get_acl` parses canned grant headers or XML bodies into `ACL` objects. Specialized handlers implement bucket creation ACL writes, object PUT ACL capture, S3 ACL subresource read/write, multi-object delete bucket-write checks, and multipart upload behavior where base bucket ACLs are checked once and temporary object ACL metadata is copied from upload markers to final manifests.

State, dependencies, and integration: State is per-request handler context, request headers, and flags like multipart `acl_checked`. It depends on `subresource.ACL`, sysmeta header helpers, XML validation, and `req.get_acl_response`.

Risks and test signals: ACL logic is security-sensitive, and several paths intentionally skip checks for internal multipart segment cleanup. Tests should cover each `ACL_MAP` entry, missing permissions, malformed ACL XML, mixed XML and headers, owner preservation, multipart tmpacl propagation, versionId query handling, and AccessDenied behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/acl_handlers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/acl_utils.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/acl_utils.py

Purpose: Translates limited S3 canned or XML ACL forms into Swift container ACL headers for the non-`s3_acl` compatibility path.

Important APIs and control flow: `swift_acl_translate` maps `public-read`, `public-read-write`, `private`, `bucket-owner-full-control`, and `bucket-owner-read` to `X-Container-Read` and `X-Container-Write` values. For XML ACL input it validates `AccessControlPolicy`, inspects grants, and classifies the ACL as private, public-read, public-read-write, unsupported, or unknown. `authenticated-read` and `log-delivery-write` raise `S3NotImplemented`; unrecognized ACLs raise `ACLError`. `handle_acl_header` consumes `HTTP_X_AMZ_ACL`, clears the query string, translates the ACL, raises `InvalidArgument` on invalid canned ACLs, and injects translated Swift headers into the request.

State, dependencies, and integration: No persistent state. It depends on s3api XML helpers, XML namespace constants, and s3response exceptions. Controllers call it before Swift `POST` ACL updates.

Risks and test signals: Translation is lossy because Swift has no full per-object ACL model and public write is explicitly limited. Tests should cover XML grant combinations, unsupported grants, header deletion, query clearing, and each canned ACL mapping.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/acl_utils.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/__init__.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/__init__.py

Purpose: Collects and re-exports S3 API controller classes from the controllers package.

Important APIs and control flow: Imports the base `Controller` and `UnsupportedController`, account service, bucket, object, ACL, S3 ACL, multi-delete, multipart upload, location, logging, versioning, tagging, and object-lock controllers. `__all__` defines the public names used by request routing and imports elsewhere in s3api.

State, dependencies, and integration: No runtime state beyond module imports. It is an integration point for `s3request` controller resolution and keeps controller names centralized.

Risks and test signals: Adding a controller without updating this file can break request dispatch or package exports. Tests should import every `__all__` symbol and verify request routing still maps subresources to the expected controller classes.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/acl.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/acl.py

Purpose: Implements legacy/non-`s3_acl` S3 ACL subresource support by deriving S3 ACL XML from Swift container ACL headers and translating bucket ACL writes into Swift POSTs.

Important APIs and control flow: `get_acl` builds an `AccessControlPolicy` XML document granting the account full control, then uses Swift ACL parsing and referrer checks to add AllUsers READ or WRITE grants when `x-container-read` or `x-container-write` allows public access. `AclController.GET` HEADs the target resource and returns generated ACL XML. `AclController.PUT` rejects object ACL updates as unimplemented, validates that exactly one of `x-amz-acl` or ACL XML body is present, translates XML ACLs through `swift_acl_translate`, issues a Swift `POST`, forces status 200, and sets `Location` to the bucket name.

State, dependencies, and integration: No persistent state. It depends on Swift ACL parsing, s3api XML builders, and request helpers for body parsing and Swift response translation.

Risks and test signals: This path cannot represent full S3 ACL semantics, especially object ACLs. Tests should cover public-read/write derivation, missing security header, unexpected content when both header and XML exist, malformed XML, object PUT unimplemented, and response status/location normalization.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/acl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/base.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/base.py

Purpose: Defines shared decorators and base classes for S3 API controllers.

Important APIs and control flow: `bucket_operation` ensures a handler acts on a bucket, either clearing `req.object_name` when a key was provided or raising a configured S3 error. `object_operation` requires an object key and raises `InvalidRequest` otherwise. `check_container_existence` forces `req.get_container_info(self.app)` before running the decorated handler. `Controller` stores `app`, `conf`, and `logger`, and exposes `resource_type` by converting the class name without `Controller` to upper snake case. `UnsupportedController` raises `S3NotImplemented` during construction.

State, dependencies, and integration: State is controller instance references only. The decorators mutate request attributes or trigger container-info side effects used by downstream Swift request construction.

Risks and test signals: Decorator order matters for access checks and error semantics. Tests should cover bucket handlers with accidental object keys, object handlers without keys, custom `err_resp`, container existence failures, and resource type strings used in `MethodNotAllowed`.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/base.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/bucket.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/bucket.py

Purpose: Implements S3 bucket metadata, create, delete, and object-listing APIs on top of Swift containers.

Important APIs and control flow: `HEAD` returns Swift container headers as S3 OK. `_parse_request_options` validates `encoding-type`, handles v1 listings, v2 listings, and object-version listings, and translates S3 markers into Swift query params. Listing builders create `ListBucketResult` or `ListVersionsResult`, including pagination markers, owner data, common prefixes, delete markers, S3 timestamps, quoted ETags, SLO-derived ETags, and storage class. `GET` requests JSON listings from Swift with `limit=max_keys+1`, detects truncation, and serializes XML. `PUT` validates optional `CreateBucketConfiguration` against configured location, then creates the Swift container and normalizes status/location. `DELETE` optionally deletes the multipart segments container before deleting the main bucket. `_delete_segments_bucket` refuses non-empty/versioned buckets and deletes segment objects iteratively.

State, dependencies, and integration: Persistent state is Swift containers, segment containers, object versioning sysmeta, and storage policy info. It depends on XML validation, Swift listing JSON, S3 timestamps, and multipart suffix conventions.

Risks and test signals: Segment cleanup has race warnings around concurrent complete uploads. Tests should cover v1/v2/version listing pagination, encoding URL behavior, invalid version markers, SLO ETag handling, bucket location mismatch, non-empty/versioned delete failures, segment deletion errors, and malformed Swift listing responses.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/bucket.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/location.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/location.py

Purpose: Implements `GET ?location` for buckets.

Important APIs and control flow: `LocationController.GET` is public and bucket-scoped. It HEADs the bucket through Swift to verify existence and authorization, builds a `LocationConstraint` XML document, leaves it empty for the S3 default `us-east-1`, otherwise writes the configured `self.conf.location`, and returns `HTTPOk` with `application/xml`.

State, dependencies, and integration: No persistent state is changed. It depends on the bucket operation decorator, `req.get_response`, and the s3api XML helpers.

Risks and test signals: The empty-body semantics for `us-east-1` are compatibility-sensitive. Tests should cover existing bucket verification, object-key requests being coerced to bucket requests, default versus non-default region output, and correct XML namespace/declaration behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/location.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/logging.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/logging.py

Purpose: Provides partial bucket logging subresource compatibility.

Important APIs and control flow: `LoggingStatusController.GET` is public, bucket-scoped, verifies bucket existence with a Swift HEAD, and always returns an empty `BucketLoggingStatus` XML document, representing logging disabled. `PUT` is public and bucket-scoped but raises `S3NotImplemented`. Both methods use `bucket_operation(err_resp=NoLoggingStatusForKey)` so key-qualified logging requests produce the S3-specific error instead of silently coercing.

State, dependencies, and integration: No persistent logging state is read or written. It depends on the common controller decorator and XML serialization.

Risks and test signals: The controller advertises read compatibility but not configuration support. Tests should cover GET for bucket and key paths, PUT 501 behavior, missing bucket error propagation, and XML body shape for disabled logging.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/logging.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/multi_delete.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/multi_delete.py

Purpose: Implements S3 Delete Multiple Objects by parsing an XML delete request and issuing concurrent Swift object deletes.

Important APIs and control flow: `MultiObjectDeleteController.POST` is public and bucket-scoped. It bounds request-body size by configured max objects and object-name length, requires a body and Content-MD5, validates `Delete` XML, parses `Quiet`, and builds `(key, version)` pairs. It HEADs the bucket, returns per-key AccessDenied XML if the bucket check fails, and rejects non-null version IDs unless Swift object versioning is available. `do_delete` shallow-copies the request, sets `object_name`, handles version queries, asks the request for multipart manifest delete query data, deletes with `Accept: application/json`, parses synchronous SLO bulk-delete responses, and converts `NoSuchKey` to success. `StreamingPile` runs deletes with configured concurrency and the response XML includes either `Error` elements or, unless quiet, `Deleted` elements.

State, dependencies, and integration: Persistent changes are Swift object deletes and optional SLO segment cleanup. It depends on object versioning feature registration, multipart delete helpers, and the concurrency utility.

Risks and test signals: Error aggregation must preserve S3 semantics while Swift bulk delete has different response formats. Tests should cover missing body, bad XML, max-object limits, quiet mode, AccessDenied bucket HEAD, versioning unavailable, SLO delete errors, concurrent partial failures, and request-copy isolation.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/multi_delete.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/multi_upload.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/multi_upload.py

Purpose: Implements S3 Multipart Upload using Swift Static Large Objects and a companion segment container named `<bucket>+segments`.

Important APIs and control flow: `_get_upload_info` HEADs the upload marker at `<bucket>+segments/<object>/<upload_id>` and falls back to the final manifest object carrying matching upload-id sysmeta. `_make_complete_body` builds the `CompleteMultipartUploadResult` and repairs malformed host URLs from some clients. `PartController.PUT` validates `uploadId` and part number, verifies upload existence, rewrites the request into the segment container path, supports upload-part-copy with range validation, clears stale SLO/etag sysmeta on copy, and returns copy XML when applicable. `UploadsController.GET` lists upload markers, filters part objects, supports prefix/delimiter and markers, and emits `ListMultipartUploadsResult`; `POST` initiates uploads by creating the segment container when needed, preserving storage policy and ACLs, storing content-type metadata on the marker, and returning an upload id. `UploadController.GET` lists parts by collecting all segment objects, sorting numerically, applying markers and limits, and emitting `ListPartsResult`. `DELETE` aborts by verifying the marker, listing and deleting parts, then returning 204. `POST` completes by validating ordered parts and ETags, building an SLO manifest, recording S3 multipart ETag sysmeta and container-update override, installing an SLO manifest hook to reject undersized non-final parts, streaming heartbeat-aware completion, cleaning the marker, and returning the completion XML.

State, dependencies, and integration: Persistent state spans segment containers, upload marker objects, part objects, final SLO manifests, sysmeta ACL/content-type/upload-id/etag headers, storage policies, and SLO middleware callbacks.

Risks and test signals: This is race- and compatibility-sensitive: clock skew, retried completes, concurrent abort/complete, undersized segments, copy-source range handling, and marker cleanup all need coverage. Tests should cover initiation container creation races, storage policy preservation, part validation, list pagination, complete XML validation, SLO 202 heartbeat parsing, EntityTooSmall and InvalidPart mapping, idempotent complete, and abort deleting all parts.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/multi_upload.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/obj.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/obj.py

Purpose: Implements S3 object GET, HEAD, PUT, DELETE, and copy behavior over Swift object operations.

Important APIs and control flow: `_gen_head_range_resp` synthesizes partial-content headers for HEAD range requests because Swift does not handle Range on HEAD. `GETorHEAD` expands S3 multipart-style ETag conditionals, updates the ETag comparison header to S3 sysmeta, validates versionId and partNumber, checks versioning container state, fetches the Swift object, adjusts non-SLO part-number behavior, strips the body for HEAD, maps `x-amz-meta-deleted` to `NoSuchKey`, and honors response header overrides such as `response-content-type`. `PUT` enforces object-name length, rejects copy-source-range with copy-source on regular object copy, checks copy source, supplies default content-type, performs the Swift request, appends S3 copy XML, removes user metadata from copy responses, and returns 200. `DELETE` handles versioning availability, builds multipart-manifest delete queries, drains synchronous SLO deletes, resets request input for possible follow-up operations, restores older versions when deleting a null delete marker, and treats missing keys as successful after bucket existence validation.

State, dependencies, and integration: Persistent state is Swift object data, SLO manifests, object versioning containers, and S3 ETag sysmeta. It depends on request helpers, versioning feature registration, timestamps, and SLO delete helpers.

Risks and test signals: Conditional ETag compatibility and version delete semantics are subtle. Tests should cover HEAD ranges, partNumber for SLO and non-SLO objects, versionId disabled/enabled paths, response header overrides, object copy metadata stripping, copy-source invalid headers, multipart delete draining, restore-on-delete, and NoSuchKey versus NoSuchBucket behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/obj.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/object_lock.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/object_lock.py

Purpose: Provides explicit object-lock subresource responses for unsupported S3 Object Lock configuration.

Important APIs and control flow: `ObjectLockController.GET` is public and bucket-scoped, but always raises `ObjectLockConfigurationNotFoundError` for the bucket. `PUT` is public and bucket-scoped, and raises `S3NotImplemented` with the generic unimplemented resource message.

State, dependencies, and integration: No persistent state is read or written. It depends on base controller decorators and s3response exception classes.

Risks and test signals: The controller must return the S3-compatible "not configured" error for GET while returning 501 for configuration attempts. Tests should cover bucket-only coercion, missing bucket propagation if ACL/existence checks happen before dispatch, GET error code/body, and PUT unimplemented behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/object_lock.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/s3_acl.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/s3_acl.py

Purpose: Implements S3 ACL subresource behavior for the full `s3_acl` mode where ACLs are stored as Swift sysmeta and represented by `subresource.ACL`.

Important APIs and control flow: `S3AclController.GET` HEADs the object or bucket, selects `resp.object_acl` or `resp.bucket_acl`, serializes `acl.elem()` to XML, and returns OK. `PUT` updates object ACLs by issuing a self-copy with `X-Copy-From` and zero content length because object sysmeta cannot be changed by POST; bucket ACLs are updated via Swift `POST`. ACL parsing and permission enforcement are performed by `S3AclHandler` before controller execution.

State, dependencies, and integration: Persistent ACL state lives in object or container sysmeta encoded by the request/response layer. It depends on URL quoting for self-copy paths, XML serialization, and ACL handlers to set `req.object_acl` or `req.bucket_acl`.

Risks and test signals: Object ACL updates rely on copy semantics and can interact with object metadata, versioning, or large-object behavior. Tests should cover GET bucket/object ACL XML, PUT bucket ACL POST, PUT object ACL self-copy headers, quoted object names, and handler rejection before mutation.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/s3_acl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/service.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/service.py

Purpose: Implements account-level `GET Service`, listing the user's S3 buckets based on Swift account container listings.

Important APIs and control flow: `ServiceController.GET` requests the Swift account listing as JSON, filters container names through `validate_bucket_name` with the configured DNS-compliance mode, builds `ListAllMyBucketsResult`, and emits owner and bucket XML. Bucket creation dates are synthetic and fixed because Swift container listings do not preserve S3 creation timestamps. When `s3_acl` and `check_bucket_owner` are enabled, each candidate bucket is HEADed and hidden if it returns `AccessDenied` or `NoSuchBucket`.

State, dependencies, and integration: No state is changed. It depends on Swift account listing JSON, bucket-name validation, ACL-aware HEAD behavior, and XML helpers.

Risks and test signals: Owner filtering can add many HEAD subrequests and may hide buckets based on transient access results. Tests should cover bucket-name filtering, malformed listing JSON behavior, owner XML, fixed creation date, ACL owner filtering, and AccessDenied/NoSuchBucket skip behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/service.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/tagging.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/tagging.py

Purpose: Provides minimal tagging subresource compatibility.

Important APIs and control flow: `TaggingController.GET` returns an empty `Tagging` XML document containing an empty `TagSet` for either bucket or object tagging requests. `PUT` and `DELETE` both raise `S3NotImplemented`.

State, dependencies, and integration: No tag state is stored or read. It depends only on controller base classes, XML helpers, and s3response exceptions. Access control and resource routing are handled outside this file by s3request and ACL handlers.

Risks and test signals: Returning empty tags for GET while rejecting writes may be acceptable for clients that probe tags but can surprise clients expecting persisted tag state. Tests should cover GET XML for bucket and object forms, content type behavior, PUT/DELETE 501 responses, and access-control prechecks.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/tagging.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/versioning.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/versioning.py

Purpose: Implements S3 bucket versioning subresource behavior using Swift object-versioning support.

Important APIs and control flow: `VersioningController.GET` is bucket-scoped, reads container sysmeta through `req.get_container_info`, and returns `VersioningConfiguration` with `Status` set to `Enabled` or `Suspended` when `versions-enabled` sysmeta exists. `PUT` requires Swift's `object_versioning` feature in the Swift info registry, parses and validates `VersioningConfiguration` XML with a bounded body size, accepts only `Enabled` or `Suspended`, sets `X-Versions-Enabled` to a lowercase boolean, POSTs the container, and returns OK.

State, dependencies, and integration: Persistent state is container sysmeta managed by Swift's object versioning middleware. It depends on `/info` feature registration, XML schema validation, and the bucket operation decorator.

Risks and test signals: Versioning availability and status mapping must align with the versioned-writes middleware. Tests should cover unavailable feature 501, malformed or missing XML, invalid statuses, sysmeta true/false GET mapping, POST header value, and object-key coercion to bucket requests.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/versioning.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/etree.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/etree.py

Purpose: Central XML utility layer for s3api, wrapping lxml parsing, namespace cleanup, RelaxNG validation, serialization, and UTF-8 text handling.

Important APIs and control flow: `cleanup_namespaces` strips the S3 default namespace and any document default namespace recursively while ignoring comment nodes. `fromstring` parses with a hardened parser (`resolve_entities=False`, `no_network=True`), raises s3api-specific `XMLSyntaxError`, optionally loads `schema/<root_tag>.rng` through `importlib.resources` or `pkg_resources`, validates the cleaned tree, and raises `DocumentInvalid` on RelaxNG failures. `tostring` optionally reconstructs the root with the S3 namespace and serializes with UTF-8 and optional XML declaration. `_Element` overrides `text` assignment to UTF-8-decode byte values, and parser globals expose `Element` and `SubElement` constructors.

State, dependencies, and integration: Global parser and lookup objects are shared by all s3api controllers. Schema files are package resources. It depends on `lxml`, resource APIs, and utility functions such as `camel_to_snake` and `utf8decode`.

Risks and test signals: XML security depends on parser options and schema loading paths. Tests should cover namespace stripping, schema validation success/failure, missing schema logging, byte text assignment, serialization with and without S3 namespace, comments, and Python resource backend compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/etree.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/exception.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/exception.py

Purpose: Defines internal exception types used by s3api request parsing, ACL utilities, XML helpers, and input stream validation.

Important APIs and control flow: `S3Exception` is the normal internal base for parse and ACL errors. `NotS3Request`, `ACLError`, `InvalidBucketNameParseError`, `InvalidURIParseError`, and `InvalidSubresource` carry request classification failures or diagnostics. `S3InputError` intentionally inherits `BaseException`, not `Exception`, so stream-read failures raised while downstream Swift apps consume `wsgi.input` can cut back through middleware layers to s3api and be converted to S3 responses. Subclasses represent incomplete input, size mismatch, too-small streaming chunks, malformed trailers, chunk signature mismatch, missing signing secret, SHA256 mismatch, checksum mismatch, and invalid checksum trailers; some carry expected/provided values or trailer names.

State, dependencies, and integration: These classes hold only constructor attributes. They integrate with s3request input wrappers, `S3ApiMiddleware.__call__`, and s3response error mapping.

Risks and test signals: Because `S3InputError` bypasses broad `except Exception`, callers must catch it deliberately. Tests should cover attribute preservation, BaseException behavior, middleware conversion to correct S3 errors, and that non-S3 parse exceptions do not leak raw internals.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/exception.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/s3api.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/s3api.py

Purpose: Main Swift middleware that translates S3-compatible requests into Swift requests, handles dispatch to S3 controllers, validates pipeline shape, emits metrics, and adds S3 request IDs to responses.

Important APIs and control flow: `ListingEtagMiddleware` wraps downstream container listings and rewrites JSON listing item hashes that contain `s3_etag` parameters so bucket listings can expose S3 multipart ETags. `S3ApiMiddleware.__init__` fills a `Config` object from PasteDeploy options, creates logging/statsd clients, checks pipeline order, and records checksum implementation. `is_s3_cors_preflight` detects likely S3 CORS preflight requests, and `__call__` handles configured preflight origins before request parsing. `_make_req_header_labels` classifies checksum, aws-chunked, trailer, content-md5, and checksum-algorithm headers into bounded metric labels; `_emit_response_header_stats` adds status, method, Swift backend path type, account, and container labels. Main request flow selects an S3Request class, creates a request, calls `handle_request`, falls through for `NotS3Request`, converts s3response errors, logs internal errors, adds `x-amz-id-2` and `x-amz-request-id` from `swift.trans_id`, promotes `s3api.backend_path` to `swift.backend_path`, emits checksum metrics, and invokes the response. `handle_request` builds the routed controller, installs the matching ACL handler, requires handlers to be marked public, invokes the method, and adds policy-index headers when known.

State, dependencies, and integration: Persistent state is configuration, logger, and statsd clients. It integrates with PasteDeploy pipeline loading, SLO availability, auth middleware order, s3request/s3response modules, ACL handlers, listing formats, sensitive header registries, and Swift info registration.

Risks and test signals: Pipeline order and auth placement are operationally critical. Tests should cover non-S3 fallthrough, invalid subresources, public handler enforcement, SLO-disabled multipart behavior, CORS allow/deny, checksum metric labels, listing ETag rewrite fallback, response request IDs, sensitive registration, config validation, and auth pipeline checks for tempauth, keystone, and third-party auth.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/s3api.py -->
