# Research: subset-b-008218

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/staticweb.py -->
# sources/object-store/openstack-swift/swift/common/middleware/staticweb.py

Purpose: Implements the `staticweb` WSGI middleware, allowing Swift containers to behave like static web sites for GET/HEAD requests. It resolves container metadata such as `web-index`, `web-error`, `web-listings`, `web-listings-css`, `web-listings-label`, and `web-directory-type` into index-object lookup, custom error pages, generated HTML listings, and directory-marker handling.

Important APIs and types: `_StaticWebContext` is the per-request `WSGIContext` that owns subrequests and response transformation. `StaticWeb` is the paste filter object and `filter_factory()` registers `staticweb` in Swift info. Key methods are `_get_container_info()`, `_listing()`, `_error_response()`, `_redirect_with_slash()`, `handle_container()`, and `handle_object()`.

Control flow: `StaticWeb.__call__()` only engages after auth middleware has installed `swift.authorize`, on valid `/v1/account/container[/object]` GET/HEAD requests, and normally only for anonymous or `.wsgi.tempurl` users unless `X-Web-Mode: true` is present. Container requests authorize read ACLs before serving listings or index objects. Object requests first try the object, then treat configured directory-marker content types as not found, then attempt `index` lookup and listing/redirect fallback. Custom error handling replays selected 401/404 responses through an error object named by status code plus configured suffix.

State and persistence: No durable state is owned by this middleware. It reads persisted container metadata and object metadata through `get_container_info()` and proxy subrequests, then stores transient metadata fields on the context for the current request. Generated listings are synthetic responses with `X-Backend-Content-Generator: staticweb`, which TempURL later recognizes.

Dependencies and integration points: Depends on Swift WSGI helpers, `get_container_info`, `tempurl.get_temp_url_info`, `swift.authorize`, and standard Swift listing JSON. It must be placed after auth in the proxy pipeline. It cooperates with TempURL prefix signatures by preserving tempurl query parameters in generated listing links, and with logging through `swift.source = SW`.

Risks: HTML listing generation depends on correct escaping and quote behavior; path prefix and tempurl prefix interactions are easy to regress. Redirects intentionally drop TempURL parameters in some cases, so broad prefix URLs need careful testing. Directory-marker detection treats content length `<= 1` as a directory object. Error-page lookup reuses previous response state and must avoid replacing successful app responses incorrectly.

Test signals: Coverage should exercise anonymous versus authenticated access, `X-Web-Mode`, index resolution, listing disabled/enabled flows, custom CSS path construction, error object fallback, tempurl prefix listings, directory-marker handling, slash redirects, and non-GET/HEAD pass-through. Local source tree search found integration references in proxy pipeline ordering, but no local `test/` directory in this checkout.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/staticweb.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/symlink.py -->
# sources/object-store/openstack-swift/swift/common/middleware/symlink.py

Purpose: Implements Swift object symlinks. A symlink is a zero-byte object whose user-visible `X-Symlink-*` headers are stored as object sysmeta and can redirect GET/HEAD traversal to a target object, optionally enforcing a static target ETag. It also augments JSON container listings with symlink target metadata.

Important APIs and types: Constants define user headers and sysmeta equivalents, including `TGT_OBJ_SYMLINK_HDR`, `TGT_ACCT_SYMLINK_HDR`, `TGT_ETAG_SYMLINK_HDR`, `TGT_BYTES_SYMLINK_HDR`, `SYMLOOP_EXTEND`, and `ALLOW_RESERVED_NAMES`. `_validate_and_prep_request_headers()` validates PUT headers. `symlink_usermeta_to_sysmeta()` and `symlink_sysmeta_to_usermeta()` translate namespaces. `SymlinkContainerContext`, `SymlinkObjectContext`, `SymlinkMiddleware`, and `filter_factory()` implement container/object dispatch.

Control flow: Container GET responses that are JSON are parsed and rewritten so any symlink metadata embedded in the listing hash becomes `symlink_path`, `symlink_etag`, and `symlink_bytes`. Object GET/HEAD either returns symlink metadata for `?symlink=get` or recursively follows sysmeta targets via subrequests, enforcing `symloop_max`, static ETag matching, and `Content-Location`. PUT with `X-Symlink-Target` requires a zero-byte body, validates target syntax and optional target account, optionally HEADs the target for static symlinks, then stores target sysmeta and container-update override ETag metadata. POST to a stored symlink returns `307 Temporary Redirect` while still allowing object-server metadata update semantics.

State and persistence: Symlink state is persisted as object sysmeta and as extra semicolon-delimited metadata in the container listing hash override. The middleware has per-request recursion counters only; no external state is stored by the filter itself.

Dependencies and integration points: Uses Swift request helpers for path/header validation, container update override keys, reserved-name access, and range suppression. It is intentionally placed after SLO/DLO/versioned_writes and before encryption. Object versioning imports symlink constants and relies on static symlinks, `SYMLOOP_EXTEND`, and `ALLOW_RESERVED_NAMES`. Container sync also needs this middleware in its internal client pipeline to preserve symlink objects.

Risks: Recursive traversal is security-sensitive because it reuses request headers and may become pre-authorized for reserved names when sysmeta allows it. Static symlink ETag validation must drain or close response bodies correctly to avoid leaks. Container-listing metadata is encoded in ETag parameters, so downgrade or non-JSON listing behavior can expose confusing hash suffixes. PUT with a missing `X-Symlink-Target-Bytes` after setting static sysmeta can raise `KeyError`, noted explicitly in code.

Test signals: Important scenarios are malformed/self-targeting target paths, cross-account target validation, zero-byte PUT enforcement, dynamic versus static symlink GET/HEAD, loop-limit conflict, `?symlink=get`, POST redirect headers, container listing JSON rewrite, SLO metadata propagation, tempurl scope behavior, versioned-container overwrite semantics, and reserved-name paths.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/symlink.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/tempauth.py -->
# sources/object-store/openstack-swift/swift/common/middleware/tempauth.py

Purpose: Provides Swift's simple built-in authentication and authorization middleware. It parses configured users, issues tokens through `/auth/` endpoints, validates request tokens, installs `swift.authorize` and `swift.clean_acl`, and enforces account/container/object access rules including account ACLs and reseller roles.

Important APIs and types: `TempAuth` is the middleware. Key methods include `__call__()`, `get_groups()`, `groups_from_fernet()`, `groups_from_compressed_fernet()`, `groups_from_memcache()`, `authorize()`, `denied_response()`, `handle_get_token()`, and `_create_new_token()`. Constants and helpers include `DEFAULT_TOKEN_LIFE`, reseller-prefix parsing, `clean_acl`, `parse_acl`, `referrer_allowed`, and `acls_from_account_info`.

Control flow: Initialization reads reseller prefixes, account rules, user entries (`user_` and base64 `user64_`), optional Fernet keys, token lifetime, auth prefix, and storage URL behavior. Normal requests bypass if an override is set, route auth-prefix paths to `handle()`, otherwise validate S3 auth details or `X-Auth-Token`/`X-Storage-Token`. Valid groups set `REMOTE_USER`, logging user id, authorization callback, and reseller flags. Invalid definitive tokens return 401; unrelated prefixes fall back or deny depending on reseller configuration. Auth endpoint GETs validate account/user/key headers and return a reusable or newly created token plus storage URL.

State and persistence: User credentials and groups are in static middleware config. Token state is either persisted in memcache (`reseller/token/...` and `reseller/user/...`) or embedded in Fernet/possibly compressed Fernet tokens. Account ACLs are stored in account sysmeta through `X-Account-Access-Control` translation to an internal sysmeta header.

Dependencies and integration points: Depends on memcache, optional cryptography Fernet, account metadata lookups, Swift ACL helpers, reseller-prefix configuration, and S3 middleware-provided `check_signature`. It is usually early in the proxy pipeline and is expected to collaborate with downstream middleware via `swift.authorize`, `swift_owner`, `reseller_request`, and access-logging fields.

Risks: Auth behavior differs for empty versus non-empty reseller prefixes, definitive versus fallback tokens, and service-token composition. Memcache absence is fatal unless active Fernet tokens are configured. Account ACL parsing is authoritative and rejects unknown keys. Token group reuse depends on set equality and token lifetime. Dot accounts and account PUT/DELETE admin restrictions are subtle security boundaries.

Test signals: Exercise token issuance formats (`/v1/account/auth`, `/auth`, `/v1.0`), wrong user/key paths, memcache reuse and expiration, Fernet and compressed Fernet validation, S3 auth path rewriting, service token group merge, reseller admin/reader behavior, `.admin` with `require_group`, account ACL read-only/read-write/admin grants, referrer ACLs, OPTIONS pass-through, and invalid ACL rejection.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/tempauth.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/tempurl.py -->
# sources/object-store/openstack-swift/swift/common/middleware/tempurl.py

Purpose: Implements signed temporary URLs for object access. It validates HMAC signatures over method, expiration, path, optional prefix scope, and optional IP range, then overrides authorization for the signed account or container scope while sanitizing request and response headers.

Important APIs and types: Public exports include `TempURL`, `filter_factory`, default header configuration constants, `get_tempurl_keys_from_metadata()`, `normalize_temp_url_expires()`, `get_temp_url_info()`, `disposition_format()`, `authorize_same_account()`, and `authorize_same_container()`. `TempURL.__call__()` is the main validator; `_get_path_parts()`, `_get_keys()`, `_get_hmacs()`, `_clean_disallowed_headers()`, `_clean_incoming_headers()`, and `_clean_outgoing_headers()` handle the detailed mechanics.

Control flow: OPTIONS bypasses. Requests without both TempURL signature and expiration bypass or fail if only one is present. Expiration accepts Unix time or ISO-8601 UTC but signs with normalized numeric time. The digest algorithm is extracted and compared with configured allowed digests. The path must be an object path, except GET/HEAD with empty prefix may target a container root for staticweb. Optional IP range is checked against `REMOTE_ADDR`. Account and container tempurl keys are fetched from metadata, expected HMACs are generated, and a constant-time comparison selects account or container scope. Valid requests strip disallowed unsafe headers, remove configured incoming headers, set `swift.authorize`, `swift.authorize_override`, and `.wsgi.tempurl`, then call the app and clean outgoing headers. Successful GET/HEAD responses get `Content-Disposition` and `Expires`.

State and persistence: TempURL keys are persisted in account/container metadata. The middleware owns no durable state. It mutates the request environment, including `QUERY_STRING`, authorization callback, and `REMOTE_USER`, only for the current request.

Dependencies and integration points: Uses account/container info lookups, Swift digest helpers, WSGIContext, sensitive parameter registration for `temp_url_sig`, and StaticWeb's `X-Backend-Content-Generator: staticweb` marker. It blocks unsafe TempURL uploads that try to create DLO manifests or symlinks using `x-object-manifest` or `x-symlink-target`.

Risks: Signature scope is security-critical: prefix strings, HEAD method equivalence, IP range parsing, and account/container key precedence must remain stable. Header cleaning determines what untrusted clients can set or observe. StaticWeb container-root handling is an exception that must still reject non-staticweb successful responses. Digest deprecation and base64/hex forms can cause compatibility regressions.

Test signals: Cover all configured methods, HEAD fallback to GET/POST/PUT signatures, expired and malformed expires values, digest algorithm parsing, account versus container key scopes, prefix TempURLs, IP allow/deny, empty-prefix staticweb listing, filename and inline disposition behavior, incoming/outgoing header removal and allow-list exceptions, unsafe PUT header rejection, and `/info` registration including allowed/deprecated digests.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/tempurl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/versioned_writes/__init__.py -->
# sources/object-store/openstack-swift/swift/common/middleware/versioned_writes/__init__.py

Purpose: Provides the paste filter factory for Swift versioning. It composes the legacy `VersionedWritesMiddleware` with the newer `ObjectVersioningMiddleware` when configured, and registers public capability flags in Swift info.

Important APIs and types: The module imports `CLIENT_VERSIONS_LOC`, `CLIENT_HISTORY_LOC`, and `VersionedWritesMiddleware` from `legacy.py`, plus `ObjectVersioningMiddleware` from `object_versioning.py`. The only local API is `filter_factory(global_conf, **local_conf)`.

Control flow: The factory merges global and local config. If `allow_versioned_writes` is true, it registers `versioned_writes` with allowed flags for `x-versions-location` and `x-history-location`. If `allow_object_versioning` is true, it registers `object_versioning`. The returned `versioning_filter()` wraps the app in `ObjectVersioningMiddleware` first when object versioning is enabled, after verifying that `symlink` is registered in Swift info, then always wraps with `VersionedWritesMiddleware`.

State and persistence: This file persists nothing directly. It controls which middleware layers are in the request path and what capability metadata appears in `/info`.

Dependencies and integration points: Depends on `config_true_value`, `register_swift_info`, and `get_swift_info`. The explicit symlink capability check encodes a hard runtime dependency of object versioning on static symlink support. It is the integration point that allows legacy and new versioning modes to coexist in the configured pipeline while retaining backwards compatibility.

Risks: Middleware wrapping order matters. Object versioning relies on symlink behavior, while legacy versioned writes still needs to run for legacy headers and objects. If `symlink` has not registered itself before this factory runs, enabling object versioning raises `ValueError`. Capability registration is configuration-driven; disabling flags can hide features from clients even if older container-server compatibility behavior remains elsewhere.

Test signals: Validate factory behavior for all config combinations, `/info` capability registration, `ValueError` when object versioning is enabled without symlink, and wrapping order where object versioning is inside legacy versioned writes. Tests should also ensure legacy-only deployments still work when `allow_object_versioning` is false.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/versioned_writes/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/versioned_writes/legacy.py -->
# sources/object-store/openstack-swift/swift/common/middleware/versioned_writes/legacy.py

Purpose: Implements Swift's two legacy object versioning modes. `X-Versions-Location` stack mode restores older versions on DELETE, while `X-History-Location` history mode writes delete markers and preserves all prior data. Existing objects are copied into an archive container before overwrites or deletes.

Important APIs and types: Constants include `DELETE_MARKER_CONTENT_TYPE`, client headers, and sysmeta names. `VersionedWritesContext` contains backend operations and listing traversal. `VersionedWritesMiddleware` handles container header translation and object PUT/DELETE interception. Important methods include `_listing_pages_iter()`, `_in_proxy_reverse_listing()`, `_get_source_object()`, `_put_versioned_obj()`, `_copy_current()`, `handle_obj_versions_put()`, `handle_obj_versions_delete_push()`, `handle_obj_versions_delete_pop()`, `handle_container_request()`, `container_request()`, and `object_request()`.

Control flow: Container PUT/POST validates that only one legacy mode is set, translates user headers to container sysmeta, handles remove headers, and exposes sysmeta back as client headers on responses. Object PUT/DELETE loads container info to find the versions container and mode. PUT copies the current object to the archive before allowing the original write. History DELETE copies current data, writes a zero-byte delete marker in the archive, then deletes the live object. Stack DELETE reverse-lists archived versions, restores the newest data version into the live container or handles delete markers, and redirects the actual delete to the archive object that was restored or marker consumed.

State and persistence: Versioning config is persisted in container sysmeta, with backwards-compatible support for the older `versions` container-info field. Archived versions are real objects named `<hex-length><object-name>/<timestamp>`. Delete markers are zero-byte objects with `DELETE_MARKER_CONTENT_TYPE`. No middleware-local durable state exists.

Dependencies and integration points: Uses pre-authorized Swift subrequests, `get_container_info`, JSON container listings, `Timestamp`, `FileLikeIter`, copy-header helpers, and `?symlink=get` when reading source objects. It intentionally preserves old behavior allowing write-authorized clients to version objects without read permission. It is integrated by `versioned_writes/__init__.py` and by proxy pipeline placement.

Risks: DELETE behavior is complex and race-prone. Reverse listing has fallback code for old container servers that do not honor `reverse`, potentially loading an entire prefix listing into memory. Large or chunked source objects are guarded by `MAX_FILE_SIZE`, but response draining/closing must be exact. Archive container absence, permissions, or partial failures surface as precondition/service errors and can affect data preservation. Legacy and new object-versioning headers must not be mixed.

Test signals: Cover container header validation/removal, disabled `allow_versioned_writes`, sysmeta response translation, PUT archiving, stack DELETE restore and delete-marker edge cases, history DELETE marker creation, missing archive container, source object not found, oversized source response, reverse-listing fallback, old container-info `versions` compatibility, and authorization before backend data movement.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/versioned_writes/legacy.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/versioned_writes/object_versioning.py -->
# sources/object-store/openstack-swift/swift/common/middleware/versioned_writes/object_versioning.py

Purpose: Implements Swift's newer object versioning mode. It stores actual versions in hidden reserved-name containers and exposes the current object through static symlinks, enabling version IDs, version-aware object operations, and version listings without repeatedly copying large data between user containers.

Important APIs and types: Constants define client/sysmeta headers and delete marker content type. Helpers include `validate_version()`, `build_listing()`, `non_expiry_header()`, and `ByteCountingReader`. `ObjectVersioningContext` defines reserved-name builders and splitters. `ObjectContext` handles object CRUD and `?version-id`. `ContainerContext` manages enable/disable, container delete, listing rewrite, and version listing. `AccountContext` merges hidden version containers into account listings. `ObjectVersioningMiddleware` dispatches account/container/object requests.

Control flow: Container PUT/POST with `X-Versions-Enabled` validates that legacy versioning and container sync are not active, creates a hidden versions container with matching storage policy, sets sysmeta, and cleans up on failure. Object PUT to an enabled container first copies an existing unversioned current object into the versions container, then writes client data to the versions container and writes a static symlink in the primary container with `X-Object-Version-Id`. DELETE writes a delete-marker version and deletes the current symlink/object. POST follows versioning symlink redirects to update current backing metadata. GET/HEAD/OPTIONS decorate responses with `X-Object-Version-Id` and rewrite symlink targets/content locations. `?version-id` rewrites requests to specific backing objects, permits GET/HEAD/PUT/DELETE semantics described in code, and maps delete markers to 404. Container `?versions` merges primary null-version objects, hidden versions, delete markers, subdirs, and broken symlink fallbacks into a JSON listing.

State and persistence: Container sysmeta stores enabled state, hidden versions container name, and parent-container links. Version objects are stored under reserved names using inverted timestamps so sorting returns newest first. Current objects are persisted as symlinks with versioning sysmeta. Delete markers are persisted as zero-byte objects with `DELETE_MARKER_CONTENT_TYPE`. Account/container bytes in listings are adjusted by reading hidden versions containers.

Dependencies and integration points: Requires symlink middleware and imports symlink constants. Uses reserved-name helpers, storage policies, `get_container_info`, pre-authorized subrequests, JSON listings, `Timestamp`, `FileLikeIter`, and Swift constraints. S3 API controllers and container sync reference object-versioning behavior; container sync skips versioning symlinks.

Risks: This file crosses many consistency boundaries: creating hidden containers, moving client bodies through subrequests, symlink metadata, version listings, and delete markers. Reserved-name parsing and delimiter restrictions protect internal names. Container delete must verify old versions are gone before removing the hidden container. Listing merge behavior must handle missing hidden containers and broken symlink references. Byte counting is needed for chunked client PUTs, and response body draining must avoid leaked app iterators.

Test signals: Cover enabling/disabling, legacy conflict, deprecated storage policy rejection, versioned PUT with normal and chunked bodies, copy-up of unversioned current objects, static symlink creation, POST through symlink redirect, delete marker creation, GET/HEAD current version headers, `?version-id=null`, GET/HEAD/PUT/DELETE specific versions, delete latest versus non-latest versions, delete-marker 404 mapping, `?versions` pagination/marker/version_marker/delimiter/reverse behavior, account listing bytes merge, and hidden-container cleanup on container delete.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/versioned_writes/object_versioning.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/x_profile/__init__.py -->
# sources/object-store/openstack-swift/swift/common/middleware/x_profile/__init__.py

Purpose: Marks `swift.common.middleware.x_profile` as a Python package for the profiling UI/model support modules. The file is empty and intentionally exports no symbols.

Important APIs and types: There are no functions, classes, constants, or imports in this file. Its API surface is the package namespace itself, allowing modules such as `x_profile.exceptions`, `x_profile.html_viewer`, and `x_profile.profile_model` to be imported.

Control flow: None. Importing the package has no side effects.

State and persistence: None. No package-level state, configuration, or persistence behavior exists here.

Dependencies and integration points: The package is consumed by `swift.common.middleware.xprofile` and submodules under `x_profile`. Its presence is required for conventional package imports in Python environments that do not rely only on implicit namespace packages.

Risks: The main risk is accidental addition of import-time side effects to this file, which would affect profiling middleware imports. Because it is empty, there is no direct runtime risk in the current implementation.

Test signals: Import tests should verify `swift.common.middleware.x_profile` and concrete submodules import cleanly. No behavioral unit tests are needed for this file itself beyond package import coverage.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/x_profile/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/x_profile/exceptions.py -->
# sources/object-store/openstack-swift/swift/common/middleware/x_profile/exceptions.py

Purpose: Defines the exception taxonomy used by Swift's xprofile profiling middleware and viewer/model helpers. The exceptions provide user-facing profiling error messages and distinguish missing resources, unsupported methods, missing optional plotting/export dependencies, and data-load failures.

Important APIs and types: `ProfileException` is the base class and stores `msg`; its `__str__()` renders `Profiling Error: <msg>`. Derived marker classes are `NotFoundException`, `MethodNotAllowed`, `ODFLIBNotInstalled`, `PLOTLIBNotInstalled`, and `DataLoadFailure`.

Control flow: There is no runtime dispatch in this file beyond exception construction and string conversion. Other xprofile modules raise these classes and catch `ProfileException` or specific subclasses to map profiling failures to HTTP responses or rendered error pages.

State and persistence: The only state is the per-exception `msg` attribute. No durable state or global mutable data exists.

Dependencies and integration points: The file has no imports. It is imported by `swift.common.middleware.xprofile`, `x_profile.html_viewer`, and `x_profile.profile_model`. `html_viewer` raises the optional dependency exceptions for odfpy/matplotlib and not-found/data-load cases; `xprofile` catches `NotFoundException` and generic `ProfileException` while serving profiling endpoints.

Risks: These exceptions do not call `Exception.__init__()`, so code that relies on standard `args` may not see the message. This is existing behavior but should be considered before adding serialization or logging integrations. Messages may be shown to clients, so callers should avoid placing sensitive data in `msg`.

Test signals: Unit tests should assert string formatting, subclass identity, and that xprofile callers map `NotFoundException`, `MethodNotAllowed`, dependency exceptions, and `DataLoadFailure` to the intended HTTP/UI behavior. Optional dependency tests should monkeypatch imports rather than requiring odfpy or matplotlib.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/x_profile/exceptions.py -->
