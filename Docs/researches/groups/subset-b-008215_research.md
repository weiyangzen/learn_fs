# Grouped Research: subset-b-008215

This grouped report covers OpenStack Swift middleware files from `swift/common/middleware`. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/bulk.py -->
# sources/object-store/openstack-swift/swift/common/middleware/bulk.py

## Purpose
`bulk.py` implements the Swift bulk operations middleware. It turns a single client request into many internal subrequests for two features: archive extraction with `PUT ?extract-archive=<tar|tar.gz|tar.bz2>` and bulk deletion with `POST` or `DELETE ?bulk-delete`. It deliberately returns an outer `200 OK` for accepted bulk workflows and reports true operation status in a heartbeat response body formatted as text, JSON, or XML.

## Important APIs, Types, and Functions
`CreateContainerError` carries failed auto-container creation status. `pax_key_to_swift_header()` maps tar pax extended attributes for `user.mime_type` and `user.meta.*` into object headers. `Bulk` is the WSGI app exposed by `filter_factory()`. Its core methods are `create_container()`, `get_objs_to_delete()`, `handle_delete_iter()`, `handle_extract_iter()`, `_process_delete()`, and `__call__()`.

## Control Flow
`__call__()` detects `extract-archive` PUTs and `bulk-delete` POST/DELETEs, negotiates response format through `Accept`, and returns an `HTTPOk` whose `app_iter` is a generator. Archive extraction streams a tar file, derives destination paths, creates containers on first use, then sends object PUT subrequests with whitelisted metadata and pax-derived headers. Bulk delete reads newline-delimited URL-encoded names, deletes objects before containers, and runs deletes through `StreamingPile` with bounded concurrency and optional conflict retry.

## State and Persistence
The middleware does not persist local state. It mutates request environ for heartbeat flushing, uses in-memory counters and failure lists per request, and persists only through downstream Swift subrequests that create containers, PUT objects, or DELETE objects/containers. Container auto-creation tracking is per request via `containers_accessed`.

## Dependencies and Integration Points
It depends on Swift `swob`, constraints, `make_subrequest`, `StreamingPile`, heartbeat response formatting, and registry publication for `/info` capabilities. It must sit before middleware that should see internal subrequests as normal Swift requests. It uses `swift.source` values `EA` and `BD` for logging and auth-token forwarding for internal requests.

## Risks and Edge Cases
Outer `200 OK` can hide failures from clients that do not parse the body. Tar streaming must defend against invalid paths, oversized objects, invalid UTF-8, too many created containers, and too many failures. Bulk delete request bodies can be large or malformed, so path-length and operation-count guards are important. Retrying container deletes on conflict can amplify backend load if misconfigured. Archive extraction applies request metadata to every object, which can surprise users if headers are broad.

## Test Signals
Useful tests cover accept negotiation, invalid archive formats, tar/gzip/bzip2 errors, pax metadata mapping, content-length and chunked enforcement, max delete and max extraction limits, object-before-container delete ordering, conflict retry behavior, 5xx to `502 Bad Gateway` aggregation, auth failure short-circuiting, and heartbeat body formats.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/bulk.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/catch_errors.py -->
# sources/object-store/openstack-swift/swift/common/middleware/catch_errors.py

## Purpose
`catch_errors.py` is top-of-pipeline safety middleware. It assigns a transaction id to every request, catches unhandled exceptions from lower middleware/apps, emits a generic `500` response, and enforces response byte counts so malformed WSGI iterables do not leave client connections in ambiguous states.

## Important APIs, Types, and Functions
`BadResponseLength` marks response-body length mismatches. `ByteEnforcer` wraps an iterable and yields exactly the declared byte count, truncating overlong output and raising on short output. `CatchErrorsContext.handle_request()` performs the transaction-id and exception boundary work. `CatchErrorMiddleware` and `filter_factory()` expose the PasteDeploy filter.

## Control Flow
For each request, `CatchErrorsContext` builds a transaction id, optionally appending truncated `X-Trans-Id-Extra`, stores it in `env['swift.trans_id']`, and updates the logger. It calls the downstream app through `WSGIContext._app_call()`. Exceptions are logged and converted into `HTTPServerError` with both `X-Trans-Id` and `X-Openstack-Request-Id`. Successful downstream responses are wrapped with `ByteEnforcer` for HEAD requests or for a single valid `Content-Length`, then transaction id headers are appended before `start_response()`.

## State and Persistence
Per-request state is held in the WSGI environ, context response fields, and logger transaction id. No durable state is written. `ByteEnforcer` always closes the inner iterable when iteration ends or fails.

## Dependencies and Integration Points
It relies on `generate_trans_id`, `get_logger`, `close_if_possible`, `Request`, `HTTPServerError`, and `WSGIContext`. It should be the first middleware so all downstream errors and malformed response iterators are caught at one boundary.

## Risks and Edge Cases
The bare `except` intentionally catches everything, including unexpected exceptions, so sensitive details are hidden from clients but must be visible in logs. Incorrect downstream `Content-Length` causes `BadResponseLength` during iteration, after headers may already be sent, relying on the WSGI server to close the connection. HEAD responses are forced to zero bytes even if downstream yields data.

## Test Signals
Tests should assert transaction id propagation, `X-Trans-Id-Extra` truncation, generic 500 conversion, header injection on success and failure, exact-length iteration, truncation on overlong bodies, exception on short bodies, HEAD zero-body enforcement, and inner iterable closing.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/catch_errors.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/cname_lookup.py -->
# sources/object-store/openstack-swift/swift/common/middleware/cname_lookup.py

## Purpose
`cname_lookup.py` rewrites requests for vanity hostnames by following DNS CNAME records until a configured Swift storage domain is found. When a match is resolved, it rewrites `HTTP_HOST` and uses `RewriteContext` so downstream middleware sees the storage host while client-visible response locations can be adjusted.

## Important APIs, Types, and Functions
`lookup_cname(domain, resolver)` performs a CNAME query and returns `(ttl, result)`, with `False` representing no record and `None` representing transient DNS failure. `_CnameLookupContext` specializes `RewriteContext`. `CNAMELookupMiddleware` validates configuration, owns the resolver and cache, and performs request rewriting.

## Control Flow
Initialization requires `dnspython`, normalizes configured storage domains, validates optional nameserver IP/port strings, and builds a resolver. On each call it extracts the host, preserves an optional port, ignores IP addresses and hosts already in storage domains, then follows up to `lookup_depth` CNAME hops. It uses memcache when available, caching negative and positive results by TTL. A successful storage-domain match rewrites `HTTP_HOST`; failure returns `400 Bad Request`.

## State and Persistence
The middleware lazily stores a memcache client reference and caches CNAME results in external memcache under `cname-...` keys. Resolver configuration is process-local. No Swift metadata is persisted.

## Dependencies and Integration Points
It depends on `dns.resolver`, `dns.exception`, Swift cache discovery, socket-string parsing, IP validation, `RewriteContext`, and `/info` registration. It should run before domain remapping or proxy routing that depends on host-derived account/container data.

## Risks and Edge Cases
DNS failures can return immediate `400` depending on lookup result. The code caches using the original given domain in one branch and looks up using the current chain domain, so cache behavior across deep CNAME chains is subtle. Nameserver validation rejects hostnames and accepts only valid IPs with optional ports. Very large lookup depths increase latency and DNS/cache load.

## Test Signals
Tests should cover missing `dnspython`, storage-domain normalization, host-with-port preservation, IP bypass, nameserver validation, positive CNAME chains, no-record and transient-DNS failure behavior, memcache hit/miss and TTL caching, lookup-depth exhaustion, and `RewriteContext` location rewriting.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/cname_lookup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/container_quotas.py -->
# sources/object-store/openstack-swift/swift/common/middleware/container_quotas.py

## Purpose
`container_quotas.py` enforces simple per-container byte and object-count quotas configured as container metadata. It blocks object PUTs that would exceed `X-Container-Meta-Quota-Bytes` or `X-Container-Meta-Quota-Count`, and validates quota metadata when users set it.

## Important APIs, Types, and Functions
`ContainerQuotaMiddleware` is the WSGI middleware. `bad_response()` re-runs write authorization before returning `413`, preventing unauthenticated users from learning quota-protected container existence. `filter_factory()` registers `container_quotas` in Swift info and returns the filter.

## Control Flow
The middleware parses requests as account/container/object paths. Container `PUT` or `POST` requests validate quota headers are digit strings. Object `PUT` requests fetch container info through `get_container_info(..., swift_source='CQ')`; if the container cannot be confirmed, the request passes through for normal handling. It compares cached `bytes` plus request `Content-Length` against the bytes quota, and cached `object_count` plus one against the count quota. Exceeding either quota returns `bad_response()`.

## State and Persistence
Quota values are persisted as container metadata by normal Swift metadata writes. This middleware only reads cached container info and mutates no local state.

## Dependencies and Integration Points
It depends on `get_container_info`, `is_success`, `swift.authorize`, and Swift metadata naming conventions. It should run after auth so `swift.authorize` exists and before object writes reach storage.

## Risks and Edge Cases
Quota checks are eventually consistent because container stats and cache may lag. Chunked uploads with unknown content length are treated as zero for the request, so they cannot be rejected up front for byte quota. Count quota assumes every PUT creates one new object and does not distinguish overwrites. Invalid metadata values already stored in containers are ignored rather than enforced.

## Test Signals
Tests should cover valid and invalid quota metadata updates, byte quota enforcement, count quota enforcement, auth-leak prevention via `bad_response()`, pass-through on missing or failed container info, chunked/unknown-length behavior, overwrites, and stale metadata/stat scenarios.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/container_quotas.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/container_sync.py -->
# sources/object-store/openstack-swift/swift/common/middleware/container_sync.py

## Purpose
`container_sync.py` validates incoming container-sync requests that use Swift realm/cluster configuration. It also validates `X-Container-Sync-To` metadata updates and advertises configured realms through `/info`.

## Important APIs, Types, and Functions
`ContainerSync` owns a `ContainerSyncRealms` instance, configuration flags, current realm/cluster info, and WSGI request handling. `register_info()` publishes available realms/clusters and marks the current cluster when configured. `filter_factory()` builds the middleware.

## Control Flow
Initialization loads `container-sync-realms.conf` from `swift_dir`, parses `allow_full_urls`, parses `current`, and registers info. `/info` requests refresh registration before pass-through. Swift API requests fetch container info with `swift_source='CS'`. Container `PUT`/`POST` requests are rejected if they attempt to configure sync on a versioned container. If full URLs are disabled, non-realm `X-Container-Sync-To` values are rejected. Requests with `X-Container-Sync-Auth` are split into realm, nonce, and signature; signatures are checked with primary and secondary realm keys plus the container sync key. Valid sync requests set authorize, SLO, and symlink override flags.

## State and Persistence
Persistent data lives in `container-sync-realms.conf` and container metadata such as sync key and sync destination. The middleware stores current config in memory and appends log-info markers to the request environ.

## Dependencies and Integration Points
It depends on realm configuration, `get_container_info`, constant-time signature comparison, `append_log_info`, Swift API-version parsing, and `/info` registry. It integrates with gatekeeper via `x-backend-inbound-x-timestamp`, with auth via `swift.authorize_override`, and with SLO/symlink middleware via override flags.

## Risks and Edge Cases
Bad realm config or current cluster naming only logs errors but may affect `/info`. Missing local realm key, missing user sync key, malformed auth header, or invalid signature all deny with a SwiftContainerSync authenticate challenge. Clock/timestamp behavior depends on upstream sync clients. Enabling full URL sync destinations widens the configuration surface.

## Test Signals
Tests should cover `/info` refresh, realm/cluster publication, invalid `current`, versioning conflict rejection, full-url disabled validation, valid and invalid sync auth signatures, key2 rotation, timestamp shunting from gatekeeper, authorize/SLO/symlink override flags, and log-info markers for failure causes.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/container_sync.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/copy.py -->
# sources/object-store/openstack-swift/swift/common/middleware/copy.py

## Purpose
`copy.py` implements server-side object copy. It supports `PUT` with `X-Copy-From`, native `COPY` with `Destination`, cross-account copy headers, optional heartbeat responses, and large-object manifest copy semantics.

## Important APIs, Types, and Functions
Header validators `_check_copy_from_header()` and `_check_destination_header()` validate path-style headers. `_copy_headers()` transfers user/system/transient metadata and delete-at headers. `ServerSideCopyWebContext` performs source GET, sink PUT, heartbeat wrapping, and OPTIONS response augmentation. `ServerSideCopyMiddleware` handles method routing and request rewriting.

## Control Flow
Object requests are inspected for `PUT` plus `X-Copy-From`, `COPY`, or `OPTIONS`. `COPY` is rewritten into a destination `PUT`, moving destination account/container/object into `PATH_INFO` and setting `X-Copy-From`. `handle_PUT()` rejects request bodies, optionally enables heartbeat flushing, resolves source account and path, fetches the source with `X-Newest`, refuses chunked or too-large source objects, builds a sink request preserving environment, copies metadata according to `x-fresh-metadata`, adjusts multipart-manifest and version-id params, streams source app_iter as sink `wsgi.input`, and adds copied-from response headers.

## State and Persistence
No local state is persisted. The destination object and metadata are persisted by the downstream PUT. Source app iterators are explicitly closed after streaming.

## Dependencies and Integration Points
It depends on `make_subrequest`, `WSGIContext`, `FileLikeIter`, Swift request helper metadata predicates, account format checks, `MAX_FILE_SIZE`, eventlet heartbeat spawning, and heartbeat response body generation. Pipeline placement is after auth and before quotas and large-object middleware so authorization and size policies apply correctly.

## Risks and Edge Cases
Pipeline order is critical: if copy runs on the wrong side of encryption or large-object middleware, stored crypto metadata or manifest behavior can be wrong. Source responses without `Content-Length` are refused. Partial/ranged copies intentionally omit source ETag validation. Heartbeat mode returns `202 Accepted` while the true copy status is embedded later in the body. Metadata copying must avoid backend/private headers and container-update override leakage.

## Test Signals
Tests should cover both COPY styles, cross-account headers, malformed source/destination headers, zero-body enforcement, source error propagation, max-size refusal, heartbeat success and error bodies, metadata preservation and `x-fresh-metadata`, SLO/DLO manifest parameter handling, version-id stripping, copied-from response headers, OPTIONS Allow/CORS augmentation, and iterator cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/copy.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/crossdomain.py -->
# sources/object-store/openstack-swift/swift/common/middleware/crossdomain.py

## Purpose
`crossdomain.py` serves a static `/crossdomain.xml` policy document for legacy browser/plugin clients such as Flash, Java, and Silverlight. It lets operators configure the policy body inserted into a cross-domain-policy XML wrapper.

## Important APIs, Types, and Functions
`CrossDomainMiddleware.GET()` builds the XML response. `__call__()` intercepts only `GET /crossdomain.xml`. `filter_factory()` merges config, registers Swift info, and returns the filter.

## Control Flow
Initialization records the downstream app and chooses `cross_domain_policy`, defaulting to a permissive wildcard policy. Requests to `/crossdomain.xml` with method GET are answered directly with `application/xml`; all other requests pass through unchanged.

## State and Persistence
The configured policy is process-local immutable state. No request state is persisted.

## Dependencies and Integration Points
The module uses `Request`, `Response`, and `register_swift_info`. It is intended to be early in the proxy pipeline, before auth, so unauthenticated clients can fetch the policy.

## Risks and Edge Cases
The default policy is intentionally permissive and may be inappropriate for private deployments. The configured policy text is interpolated directly into XML, so malformed config yields malformed XML. Only GET is handled; HEAD or OPTIONS pass through.

## Test Signals
Tests should assert default policy output, configured multiline policy output, content type, GET-only behavior, pass-through for other paths/methods, and `/info` registration.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/crossdomain.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/crypto/__init__.py -->
# sources/object-store/openstack-swift/swift/common/middleware/crypto/__init__.py

## Purpose
`crypto/__init__.py` is the PasteDeploy entry point for Swift object encryption middleware. It composes the write-side `Encrypter` and read-side `Decrypter` into a single `encryption` filter.

## Important APIs, Types, and Functions
`filter_factory(global_conf, **local_conf)` merges config, registers encryption capability data in Swift info, and returns `encryption_filter(app)`, which constructs `Decrypter(Encrypter(app, conf), conf)`.

## Control Flow
At load time, the factory computes `enabled` from `disable_encryption` and publishes `register_swift_info('encryption', admin=True, enabled=enabled)`. At pipeline construction, the returned closure wraps the downstream app with `Encrypter`, then wraps that with `Decrypter`, making decryption the outermost crypto component for client responses.

## State and Persistence
This file has no persistent state. It passes configuration to the two crypto middlewares, which persist encryption metadata through object sysmeta/transient sysmeta.

## Dependencies and Integration Points
It depends on `Decrypter`, `Encrypter`, `config_true_value`, and Swift registry. It must be paired with a keymaster middleware earlier in the pipeline so crypto contexts can call `swift.callback.fetch_crypto_keys`.

## Risks and Edge Cases
Disabling encryption only disables new writes in `Encrypter`; the `Decrypter` remains necessary for existing encrypted data. Pipeline order relative to keymaster, copy, SLO/DLO, and gatekeeper is security-sensitive.

## Test Signals
Tests should cover factory composition order, info registration for enabled and disabled states, config merging, and continued read/decrypt behavior when `disable_encryption` is true.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/crypto/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/crypto/crypto_utils.py -->
# sources/object-store/openstack-swift/swift/common/middleware/crypto/crypto_utils.py

## Purpose
`crypto_utils.py` provides shared primitives for Swift encryption middleware: AES-CTR encryption/decryption, random IV/key generation, simple key wrapping, crypto metadata validation/serialization, and WSGI context helpers for retrieving keys from keymaster callbacks.

## Important APIs, Types, and Functions
`CRYPTO_KEY_CALLBACK` names the environ key `swift.callback.fetch_crypto_keys`. `Crypto` exposes `create_encryption_ctxt()`, `create_decryption_ctxt()`, `create_iv()`, `create_crypto_meta()`, `check_crypto_meta()`, `create_random_key()`, `wrap_key()`, `unwrap_key()`, and `check_key()`. `CryptoWSGIContext` adds `get_keys()` and `get_multiple_keys()`. Utility functions include `dump_crypto_meta()`, `load_crypto_meta()`, `append_crypto_meta()`, and `extract_crypto_meta()`.

## Control Flow
`Crypto` memoizes the cryptography backend and uses AES-CTR with 256-bit keys and block-sized IVs. Decryption supports range offsets by incrementing the CTR IV by block offset and discarding bytes inside the first block. Metadata serialization JSON-encodes nested dicts, base64-encodes `iv` and `key` fields, sorts keys for deterministic output, and URL-quotes the JSON. Metadata extraction uses Swift header parsing to find `swift_meta`.

## State and Persistence
Process-local state is limited to the logger and crypto backend. Persistent state is serialized crypto metadata stored by encrypter in headers/sysmeta and later parsed by decrypter. No keys are stored by this module.

## Dependencies and Integration Points
It depends on `cryptography`, Swift exceptions, `HTTPInternalServerError`, `parse_header`, and `WSGIContext`. `CryptoWSGIContext` is the common integration point between encrypter/decrypter and keymaster middleware.

## Risks and Edge Cases
Missing key callbacks or malformed returned key dicts are converted to 500s. Unknown secret ids propagate for callers that can decide whether to mask listing entries or fail object decrypts. Metadata parsing must reject non-string, non-dict, bad JSON, and bad base64 inputs. AES-CTR does not authenticate ciphertext; integrity is handled separately through ETags/HMACs and storage behavior.

## Test Signals
Tests should cover key-length validation, IV length/cipher validation, offset decryption equivalence, key wrapping/unwrapping, metadata round trips with nested key/iv values, malformed metadata errors, callback missing/failing behavior, required-key validation, multiple-key retrieval across all ids, and URL/base64 encoding compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/crypto/crypto_utils.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/crypto/decrypter.py -->
# sources/object-store/openstack-swift/swift/common/middleware/crypto/decrypter.py

## Purpose
`decrypter.py` restores encrypted Swift object responses and encrypted container-listing ETags to client-visible plaintext. It handles object GET/HEAD metadata and body decryption, ranged and multipart byte-range responses, and JSON container listings.

## Important APIs, Types, and Functions
`purge_crypto_sysmeta_headers()` strips crypto private headers. `BaseDecrypterContext` provides crypto metadata extraction, wrapped-key unwrapping, encrypted-header decryption, and key retrieval. `DecrypterObjContext` handles object responses with `decrypt_resp_headers()`, `response_iter()`, and `multipart_response_iter()`. `DecrypterContContext` decrypts JSON listing hashes. `Decrypter` routes supported requests.

## Control Flow
For valid Swift container/object paths, `Decrypter` handles object GET/HEAD and container GET. Object handling calls the downstream app, reads body and metadata crypto headers, fetches keys using stored key ids, decrypts encrypted ETag and user metadata headers, purges crypto sysmeta, optionally exposes backend crypto cipher, and decrypts body streams for successful GETs. Range responses compute the correct AES-CTR offset from `Content-Range`; multipart byteranges decrypt each part from its first byte. Container GET JSON bodies are fully read, parsed, and each object `hash` with appended crypto meta is decrypted using the container key.

## State and Persistence
No local state is persisted. It consumes persistent crypto metadata stored in object sysmeta/transient sysmeta and container listing hash values. Container listing responses are materialized in memory to update JSON and content length.

## Dependencies and Integration Points
It depends on `CryptoWSGIContext`, crypto metadata utilities, Swift header helpers, `HeaderKeyDict`, content-range/type parsers, multipart byterange parsing, and keymaster callbacks. It is composed outside `Encrypter` by the crypto package factory.

## Risks and Edge Cases
Malformed or missing required crypto metadata yields 500s for object decrypts. Unknown secret ids in container listings are masked as `<unknown>` after logging, preserving listability but losing exact ETag. JSON listings are fully buffered, so very large listings have memory implications. Multipart decryption must preserve MIME framing exactly. Override mode skips decryption entirely.

## Test Signals
Tests should cover encrypted ETag restoration, user metadata restoration, CORS exposed-header updates, body decryption for full and ranged GETs, multipart byteranges, HEAD without body decryption, crypto sysmeta purge, container JSON hash decryption, unknown secret handling, malformed metadata 500s, override bypass, invalid path/API bypass, and content-length recalculation for listings.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/crypto/decrypter.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/crypto/encrypter.py -->
# sources/object-store/openstack-swift/swift/common/middleware/crypto/encrypter.py

## Purpose
`encrypter.py` encrypts new object bodies and user metadata on PUT/POST, masks conditional ETags on GET/HEAD so encrypted on-disk objects can still satisfy plaintext ETag conditions, and writes crypto metadata needed for future decryption.

## Important APIs, Types, and Functions
`encrypt_header_val()` encrypts a header value and returns ciphertext plus crypto meta. `_hmac_etag()` computes the stored plaintext ETag MAC. `EncInputWrapper` encrypts request body chunks and installs a footer callback. `EncrypterObjContext` handles object PUT, POST, and GET/HEAD. `Encrypter` routes requests and honors `disable_encryption` and `swift.crypto.override`.

## Control Flow
PUT handling validates metadata before encryption, fetches object and container keys, encrypts user metadata into transient sysmeta, wraps `wsgi.input` with `EncInputWrapper`, and calls downstream. The wrapper lazily creates a random body key, wraps it with the object key, AES-CTR encrypts chunks, computes plaintext and ciphertext MD5s, validates any client ETag against plaintext, writes ciphertext ETag plus encrypted plaintext ETag/body metadata into footers, and encrypts container-listing ETag override with the container key. POST encrypts metadata only. GET/HEAD masks `If-Match` and `If-None-Match` values by appending HMACs for all known root secrets and sets an ETag-is-at header for object-server comparison.

## State and Persistence
Per-request encryption contexts, MD5 digests, and body crypto metadata live in memory. Persistent outputs are object sysmeta/transient sysmeta headers and footer metadata: encrypted ETag, body crypto meta, body key wrap, key id, ETag MAC, encrypted user metadata, and encrypted container listing override ETag.

## Dependencies and Integration Points
It depends on `CryptoWSGIContext`, `Crypto`, Swift metadata helpers, footer callback chaining, request `InputProxy`, conditional header helpers, keymaster callbacks, and container update override headers. It must run where downstream proxy controllers support footer callbacks.

## Risks and Edge Cases
If no body bytes are read, no body crypto sysmeta is written and any client ETag is restored. Metadata length is checked before encryption, but encoded/encrypted values can still change downstream header sizes. Conditional masking must include historic keys for key rotation. Pipeline order with copy and large-object middleware is critical. AES-CTR encryption is not authenticated; ETag/MAC handling is the primary integrity signal used by Swift paths.

## Test Signals
Tests should cover PUT body encryption and footer metadata, empty-body behavior, client ETag validation failure, response ETag plaintext replacement, metadata encryption on PUT/POST, disabled encryption, crypto override, conditional ETag masking with current and historic keys, container-listing ETag override encryption, footer callback chaining, and downstream error behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/crypto/encrypter.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/crypto/keymaster.py -->
# sources/object-store/openstack-swift/swift/common/middleware/crypto/keymaster.py

## Purpose
`keymaster.py` provides the default Swift encryption keymaster. It loads one or more high-entropy root secrets and installs a request-local callback that derives account/container/object encryption keys from request paths using HMAC-SHA256.

## Important APIs, Types, and Functions
`KeyMasterContext.fetch_crypto_keys()` is the callback installed under `swift.callback.fetch_crypto_keys`. `BaseKeyMaster` provides config-file loading, root-secret validation, request routing, and `create_key()`. `KeyMaster` loads base64 `encryption_root_secret*` options and decodes them. `filter_factory()` exposes the filter.

## Control Flow
`BaseKeyMaster.__init__()` optionally loads a separate keymaster config, calls subclass `_get_root_secret()`, normalizes single secret to a dict, validates `active_root_secret_id`, and validates metadata-version configuration. For PUT/POST/GET/HEAD Swift requests, `__call__()` creates a `KeyMasterContext`, which preserves any alternate upstream key callback, installs its own callback, then calls downstream. `fetch_crypto_keys()` derives keys for requested or stored key ids, handles metadata versions 1, 2, and 3, includes key ids and `all_ids` for rotation, and falls back to alternate callbacks for unknown secret ids when present.

## State and Persistence
Root secrets are held in process memory. Persistent crypto metadata contains opaque key ids with version, path, and optional secret id. No derived keys are persisted. `KeyMasterContext` caches derived key dicts per request.

## Dependencies and Integration Points
It depends on Swift config reading, strict base64 decoding, multikey option loading, path splitting, `WSGIContext`, and `UnknownSecretIdError`. It must appear before the encryption middleware so crypto code can fetch keys.

## Risks and Edge Cases
Changing or losing root secrets makes encrypted data unreadable. Metadata-version compatibility handles historic path bugs, including object names starting with slash and old py3 WSGI-string metadata. `keymaster_config_path` forbids overlapping keymaster options in the filter section to avoid ambiguous config. Unknown active secret ids and short/non-bytes secrets fail at startup.

## Test Signals
Tests should cover root secret decoding and minimum length, multikey loading, active secret selection, config-file conflict detection, metadata versions, path derivation for account/container/object, historic path bug compatibility, all_ids rotation behavior, alternate callback fallback, request-method routing, and unknown secret errors.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/crypto/keymaster.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/crypto/kmip_keymaster.py -->
# sources/object-store/openstack-swift/swift/common/middleware/crypto/kmip_keymaster.py

## Purpose
`kmip_keymaster.py` adapts `BaseKeyMaster` to fetch root encryption secrets from a KMIP service via PyKMIP. It lets operators reference one or more KMIP key ids instead of storing root secrets directly in Swift config.

## Important APIs, Types, and Functions
`KmipKeyMaster` defines `log_route`, supported config options, config section name, `_load_keymaster_config_file()`, and `_get_root_secret()`. `filter_factory()` returns the keymaster filter.

## Control Flow
Config loading delegates to `BaseKeyMaster`, then determines the actual config section, rejects directory-style proxy config, attaches Swift logger handlers to the `kmip` logger, and installs filters that prevent sensitive DEBUG logging from PyKMIP protocol/config loggers. It creates `ProxyKmipClient` from the chosen config. `_get_root_secret()` iterates `key_id*` multikey options, fetches each KMIP object, verifies it is AES-256, caches duplicate KMIP ids to avoid extra round trips, and returns secret bytes keyed by Swift secret id.

## State and Persistence
Root secrets fetched from KMIP are stored in memory by the base class. KMIP keys remain external persistent state. The module itself writes no Swift metadata beyond what base keymaster/encryption later persist.

## Dependencies and Integration Points
It depends on `kmip.pie.client.ProxyKmipClient`, Python logging, Swift `LogLevelFilter`, multikey option parsing, and all `BaseKeyMaster` behavior. It replaces the default keymaster in the proxy pipeline.

## Risks and Edge Cases
Startup depends on KMIP availability and valid client TLS/auth config. Incorrect KMIP algorithm or key length is rejected. Sensitive logging filters are important because PyKMIP debug logs may include key material or passwords. Directory config is unsupported without `keymaster_config_path`.

## Test Signals
Tests should cover external config loading, directory-config rejection, logger/filter setup, multikey and duplicate KMIP id handling, AES-256 validation, invalid algorithm/length errors, active secret selection inherited from base, and client context-manager failures.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/crypto/kmip_keymaster.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/crypto/kms_keymaster.py -->
# sources/object-store/openstack-swift/swift/common/middleware/crypto/kms_keymaster.py

## Purpose
`kms_keymaster.py` adapts `BaseKeyMaster` to retrieve root encryption secrets from an external KMS through Castellan, commonly Barbican. It supports Keystone password credentials and multikey rotation.

## Important APIs, Types, and Functions
`KmsKeyMaster` defines config option names, section name, and `_get_root_secret()`. The factory returns `KmsKeyMaster(app, conf)`.

## Control Flow
`_get_root_secret()` builds a Castellan Keystone password context from auth, user, project, domain, trust, and reauthentication options. It creates an `oslo_config.cfg.ConfigOpts`, sets Castellan defaults including auth endpoint, Barbican endpoint, API class, and optional Barbican region, enables Castellan logging, then creates `key_manager.API`. For each `key_id*` option, it retrieves the key, rejects missing values, verifies AES algorithm, at least 256 bits, and RAW format, encodes returned secret material to bytes if needed, and returns root secrets keyed by Swift secret id.

## State and Persistence
KMS secrets are external persistent state. Retrieved root secrets are held in memory by `BaseKeyMaster`; derived keys and crypto metadata are handled by base keymaster and encryption middleware.

## Dependencies and Integration Points
It depends on Castellan, Keystone password credentials, Oslo config, Swift multikey parsing, and `BaseKeyMaster`. It is a drop-in replacement for local root-secret keymaster in the proxy pipeline.

## Risks and Edge Cases
Startup and reload depend on external KMS reachability and credentials. The broad `except Exception` around key validation converts any validation-time error into a symmetric-key type error, which can obscure the exact cause. RAW format and AES length checks are essential because base key derivation assumes raw high-entropy secret bytes. Region and endpoint misconfiguration will fail at retrieval time.

## Test Signals
Tests should cover construction of Keystone context, Castellan defaults, Barbican region handling, missing key returns, invalid algorithm/bit length/format, non-bytes encoded secret conversion, multikey parsing, active-root-secret validation from base, and external API exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/crypto/kms_keymaster.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/dlo.py -->
# sources/object-store/openstack-swift/swift/common/middleware/dlo.py

## Purpose
`dlo.py` implements Dynamic Large Object support. It validates DLO manifest headers on PUT and, on GET/HEAD of manifest objects, dynamically lists segment objects and streams them as one logical object.

## Important APIs, Types, and Functions
`GetContext` handles manifest GET/HEAD. Key methods are `_get_container_listing()`, `_segment_listing_iterator()`, `get_or_head_response()`, and `handle_request()`. `DynamicLargeObject` stores rate-limit and timeout config, migrates old proxy config settings, validates `X-Object-Manifest`, and exposes the WSGI entry point.

## Control Flow
For object GET/HEAD without `multipart-manifest=get`, `GetContext` first calls downstream and checks for `X-Object-Manifest`. Manifest responses are closed, optionally drained, and replaced with a generated response. The manifest value is split into segment container and prefix. The middleware lists segment objects using container GET subrequests with prefix and marker, computes content length and aggregate ETag when the listing is complete, handles single byte ranges when enough listing data is available, and builds a `SegmentedIterable` over segment paths. PUT requests only validate that `X-Object-Manifest` has `container/prefix` form without query separators or leading slash in prefix.

## State and Persistence
DLO manifests are persisted as object metadata by normal Swift PUT/POST flows. This middleware keeps only request-local segment listings and iterators. Config values are process-local.

## Dependencies and Integration Points
It depends on container listings, `SegmentedIterable`, `RateLimitedIterator`, `make_subrequest`, `load_app_config`, Swift constraints, range helpers, MD5 ETag construction, and object response headers. It integrates with copy and SLO behavior through `multipart-manifest=get` conventions.

## Risks and Edge Cases
Incomplete listings prevent full length/ETag calculation and can cause range requests to be ignored. Listing or segment errors after response streaming starts can only close the connection via exceptions. Manifest objects whose names match their own prefix can include their own body as a segment. Segment integrity is based on response headers rather than manifest-declared size/hash. Large listings and high segment counts are rate-limited to protect backends.

## Test Signals
Tests should cover manifest PUT validation, pass-through on non-manifest GET/HEAD, complete and paged segment listings, aggregate content length and ETag, satisfiable/unsatisfiable/ignored ranges, segment iterator marker progression, listing failure before and during streaming, first-segment validation failures, rate limiting, old config migration, and `multipart-manifest=get` bypass.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/dlo.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/domain_remap.py -->
# sources/object-store/openstack-swift/swift/common/middleware/domain_remap.py

## Purpose
`domain_remap.py` translates account and optional container names embedded in the request host into Swift path components. It supports virtual-host style URLs such as `container.AUTH-account.example.com/object` and account-only hosts.

## Important APIs, Types, and Functions
`_DomainRemapContext` specializes `RewriteContext`. `DomainRemapMiddleware` parses storage domains, path root, reseller prefixes, default reseller prefix, and client path mangling settings. `filter_factory()` registers `domain_remap` info and returns the filter.

## Control Flow
On each request, the middleware extracts `HTTP_HOST` or `SERVER_NAME`, strips a port, and finds a configured storage-domain suffix. The host prefix must contain one or two labels: account or container plus account. Account names have one hyphen converted to underscore and reseller prefix case normalized. If the account prefix is unknown, a configured default reseller prefix may be prepended; otherwise the request passes through. The new path is built as `/<path_root>/<account>/<container?>/<old path>`, optionally stripping an existing path root from the client path, then `PATH_INFO` is updated and `RewriteContext` handles response rewriting.

## State and Persistence
All state is process-local configuration. The middleware mutates the request environ path for downstream handling and persists no Swift metadata.

## Dependencies and Integration Points
It uses Swift `RewriteContext`, `Request`, `HTTPBadRequest`, `wsgi_quote`, config parsing, CSV list parsing, and Swift registry. It commonly runs after CNAME lookup so vanity domains first map to a storage domain.

## Risks and Edge Cases
Host-derived account and container names must be DNS-compatible and are best-effort only. More than two host labels before the storage domain returns `400`. Browser lowercasing requires prefix case repair. `mangle_client_paths` changes how existing `/v1` path roots are treated and can affect compatibility. Host header trust and proxy configuration are security-sensitive.

## Test Signals
Tests should cover account-only and container/account hosts, bad label counts, storage-domain normalization, ports, reseller prefix case repair, hyphen-to-underscore conversion, default reseller prefix, unknown-prefix pass-through, path-root insertion and mangling, no storage-domain pass-through, and rewrite context behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/domain_remap.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/etag_quoter.py -->
# sources/object-store/openstack-swift/swift/common/middleware/etag_quoter.py

## Purpose
`etag_quoter.py` conditionally makes object response ETag headers RFC-compliant by double-quoting bare ETags. The behavior can be enabled globally, at account level, or at container level, with container settings overriding account settings.

## Important APIs, Types, and Functions
`EtagQuoterMiddleware.__call__()` handles both metadata translation on account/container requests and ETag quoting on object responses. `filter_factory()` registers `etag_quoter` info with the `enable_by_default` value.

## Control Flow
The middleware parses Swift API paths. Account or container PUT/POST-style requests translate client headers such as `X-Account-Rfc-Compliant-Etags` into sysmeta headers, and translate sysmeta response headers back to client-visible names. Object requests fetch container info; if it has no `rfc-compliant-etags` sysmeta, account info is fetched; if neither has a flag, config default is used. When enabled, the middleware calls the downstream app, scans response headers, and wraps any ETag that is not already quoted or weak-quoted.

## State and Persistence
The enablement flags are persisted as account/container sysmeta via normal metadata writes. The middleware keeps only config in memory and mutates request/response headers.

## Dependencies and Integration Points
It depends on API-version validation, container/account info lookup, `config_true_value`, and Swift registry. It must run after cache so info lookups are available and before clients see object responses.

## Risks and Edge Cases
Only object response ETags are quoted; metadata translation paths must avoid exposing sysmeta. Empty client metadata values and `X-Remove-...` clear sysmeta. If info lookups fail, object responses pass through unmodified. Quoting weak ETags is avoided when already in `W/"..."` form.

## Test Signals
Tests should cover account and container client-to-sysmeta translation, remove header behavior, response sysmeta-to-client translation, config default enablement, container override over account flag, failed info lookup pass-through, already quoted and weak quoted ETags, bare ETag quoting, non-Swift pass-through, and registry data.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/etag_quoter.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/formpost.py -->
# sources/object-store/openstack-swift/swift/common/middleware/formpost.py

## Purpose
`formpost.py` translates signed browser multipart form uploads into one or more pre-authorized Swift object PUT subrequests. It enables HTML form uploads without exposing full auth credentials, using TempURL-style keys and HMAC signatures.

## Important APIs, Types, and Functions
`FormInvalid` and `FormUnauthorized` distinguish bad request from bad signature/auth. `_CappedFileLikeObject` enforces per-file size while streaming. `FormPost.__call__()` detects multipart POSTs. `_translate_form()` parses fields and file parts. `_perform_subrequest()` validates policy/signature and issues a PUT. `_get_keys()` retrieves account and container TempURL keys.

## Control Flow
POST requests with `multipart/form-data` and a boundary are parsed incrementally. Non-file form fields are read up to `MAX_VALUE_LENGTH` and stored lowercased. Each file part increments file count, copies current attributes, applies per-file content headers, and calls `_perform_subrequest()`. The subrequest is pre-authed, chunked, has query string removed, appends filename to `PATH_INFO`, copies delete-at/delete-after and content headers, validates expiry, computes the canonical HMAC body of path, redirect, max file size/count, and expires, and checks the signature against all account/container TempURL keys using allowed digest algorithms. Final response is either plain text or a 303 redirect with status/message parameters.

## State and Persistence
The middleware persists uploaded objects through downstream PUT subrequests. All form attributes, counters, and response state are request-local. It increments digest metric counters through the logger.

## Dependencies and Integration Points
It depends on Swift multipart parsers, TempURL key metadata helpers, digest policy helpers, pre-authed environ creation, account/container info lookups, WSGIContext, and Swift registry. It integrates with auth by making pre-authorized subrequests and typically relies on keystoneauth allowing middleware overrides.

## Risks and Edge Cases
Form field order matters: fields after file parts are not available to those file subrequests. Large fields are truncated at 4096 bytes while the remaining part is drained. Filename is appended directly to the destination path after WSGI conversion. Expired forms, unsupported digest algorithms, invalid signatures, and missing keys deny. File size excess is detected during streaming and converted to a bad request.

## Test Signals
Tests should cover multipart boundary errors, no-file forms, max file count and size enforcement, invalid integer fields, expiry, account/container key retrieval, digest algorithm allow/deprecation info, signature validation with multiple keys, redirect and non-redirect responses, CORS header preservation, per-file content headers, delete-at/delete-after handling, field truncation/draining, and subrequest body/error propagation.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/formpost.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/gatekeeper.py -->
# sources/object-store/openstack-swift/swift/common/middleware/gatekeeper.py

## Purpose
`gatekeeper.py` protects Swift internal metadata and backend control headers from clients. It strips inbound private headers, strips outbound private headers, optionally shunts client `X-Timestamp` into an internal backend header, and can convert absolute Location headers to relative locations for configured flows.

## Important APIs, Types, and Functions
`inbound_exclusions` and `outbound_exclusions` define regex prefixes for account/container/object sysmeta, object transient sysmeta, and `x-backend`. `make_exclusion_test()` compiles the matcher. `GatekeeperMiddleware.__call__()` applies request filtering and response filtering. `filter_factory()` exposes the filter.

## Control Flow
For each request, `Request(env)` builds mutable headers. Matching inbound headers are removed and logged at debug. If enabled, `X-Timestamp` is moved to `X-Backend-Inbound-X-Timestamp`, preserving the value for trusted downstream middleware such as container sync while keeping direct client timestamp writes out of normal paths. If `X-Allow-Reserved-Names` is allowed, it is moved to `X-Backend-Allow-Reserved-Names`. The wrapped `start_response` optionally rewrites `Location` to relative when `swift.leave_relative_location` is set, then removes matching outbound private headers before returning to the client.

## State and Persistence
No durable state is stored. The middleware mutates request and response headers in memory and logs removed/shunted headers.

## Dependencies and Integration Points
It depends on Swift request helpers for sysmeta prefixes and header removal, `Request`, `config_true_value`, URL splitting, and regex matching. It must be early in the pipeline, immediately after `catch_errors`, so later middleware can safely use internal headers.

## Risks and Edge Cases
Regex prefixes must stay aligned with Swift internal header namespaces. Allowing reserved-name headers is a privileged compatibility mode. Relative Location rewriting preserves path, query, and fragment but drops scheme/host. Debug logs can include header names and values, so log exposure should be considered.

## Test Signals
Tests should cover inbound sysmeta/transient/backend stripping, outbound stripping, `X-Timestamp` shunting on/off, reserved-name header shunting on/off, relative Location rewriting, no-op absolute Location behavior, case-insensitive matching, and debug logging of removed headers.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/gatekeeper.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/healthcheck.py -->
# sources/object-store/openstack-swift/swift/common/middleware/healthcheck.py

## Purpose
`healthcheck.py` provides a lightweight operational endpoint at `/healthcheck`. It returns `200 OK` with `OK` unless a configured disable file exists, in which case it returns `503` with `DISABLED BY FILE`.

## Important APIs, Types, and Functions
`HealthCheckMiddleware.GET()` returns the healthy response. `DISABLED()` returns the disabled response. `__call__()` intercepts `/healthcheck`. `filter_factory()` exposes the filter.

## Control Flow
Initialization stores an optional `disable_path`. Each request is wrapped as a `Request`; only `/healthcheck` is handled directly. If a disable path is configured and exists on disk, `DISABLED` is selected, otherwise `GET` is selected. Other paths pass through.

## State and Persistence
The only persistent signal is the operator-controlled disable file. The middleware performs a filesystem existence check per healthcheck request and stores no other state.

## Dependencies and Integration Points
It depends on `os.path.exists`, Swift `Request`, and `Response`. It is typically placed early enough that monitors do not require auth or backend availability.

## Risks and Edge Cases
Filesystem checks on every healthcheck are simple but depend on path availability and permissions. The endpoint handles `/healthcheck` regardless of method by selecting the healthy/disabled handler, so method-specific behavior should be considered by operators/tests. Missing or unreadable disable-path parents simply appear as enabled if the file does not exist.

## Test Signals
Tests should cover healthy response body/status/content type, disabled file response, pass-through for other paths, configured and empty disable paths, and method behavior for non-GET requests to `/healthcheck`.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/healthcheck.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/keystoneauth.py -->
# sources/object-store/openstack-swift/swift/common/middleware/keystoneauth.py

## Purpose
`keystoneauth.py` is Swift's authorization middleware for Keystone-authenticated identities. It consumes identity headers produced by `keystonemiddleware.auth_token`, maps Keystone projects to reseller-prefixed Swift accounts, installs `swift.authorize`, and implements role, ACL, service-token, system-reader, and anonymous/referrer authorization rules.

## Important APIs, Types, and Functions
Constants define project domain-id client and sysmeta headers plus an unknown sentinel. `KeystoneAuth.__call__()` extracts identity and installs authorization hooks. `_keystone_identity()` parses Keystone v2/v3 identity and service roles. `_set_project_domain_id()` persists account project-domain sysmeta when possible. `_authorize_cross_tenant()`, `authorize()`, `authorize_anonymous()`, `_authorize_unconfirmed_identity()`, and `denied_response()` implement access policy.

## Control Flow
On each request, the middleware honors `swift.authorize_override` when configured, otherwise extracts confirmed identity and service identity headers. Confirmed users get `REMOTE_USER`, `keystone.identity`, `swift.authorize`, optional `reseller_request`, access-log user id, and ACL cleaning. Anonymous users get `authorize_anonymous`. The start_response wrapper exposes project-domain sysmeta as a client header. Authorization parses the Swift path, handles OPTIONS, sets project-domain id metadata on account/container create/update paths, grants reseller-admin and read-only system-reader access, denies non-admin own-account DELETE, checks cross-tenant ACLs, referrer/container-sync ACLs, account/project match, operator roles plus optional service roles, project-reader roles for GET/HEAD, and finally ACL role matches before returning 401/403.

## State and Persistence
Configuration is process-local. Project domain id may be persisted as account sysmeta to support name-based ACL compatibility. Request-local authorization state is stored in environ keys such as `swift.authorize`, `swift_owner`, `reseller_request`, `keystone.identity`, and `swift.access_logging`.

## Dependencies and Integration Points
It depends on Keystone auth-token headers and token info, Swift ACL parsing/cleaning, reseller option parsing, account info lookup, system metadata prefixes, and Swift HTTP response classes. It integrates with formpost/tempurl through authorize overrides and with container sync through unconfirmed identity checks.

## Risks and Edge Cases
Role configuration is prefix-specific and backwards-compatible defaults can be subtle. Name-based ACL compatibility is domain-sensitive and can be disabled. Project-domain metadata may be unknown when reseller admins create accounts for other projects. Service-token requirements change owner semantics. Anonymous authorization is authoritative only for configured reseller prefixes. Incorrect pipeline ordering with authtoken or override-capable middleware changes security behavior.

## Test Signals
Tests should cover identity extraction for v2/v3 and service tokens, override behavior, reseller admin and system reader grants, own-account DELETE denial, account/project matching, operator roles with and without service roles, project reader GET/HEAD behavior, cross-tenant id/name/wildcard ACLs with domain compatibility, referrer ACLs, container-sync key authorization, project-domain sysmeta set/expose paths, anonymous auth, 401 vs 403 denial, and prefix-specific config.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/keystoneauth.py -->
