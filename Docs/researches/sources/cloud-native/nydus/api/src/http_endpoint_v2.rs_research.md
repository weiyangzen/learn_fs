# sources/cloud-native/nydus/api/src/http_endpoint_v2.rs

Purpose: implements Nydus HTTP API v2 endpoint handlers below `HTTP_ROOT_V2 = "/api/v2"`, mainly daemon information/configuration and blob cache object lifecycle operations.

Important APIs/types/functions: `InfoV2Handler` maps daemon GET/PUT to `ApiRequest::GetDaemonInfoV2` and `ConfigureDaemon`. `BlobObjectListHandlerV2` supports `GET`, `PUT`, and `DELETE` for `/api/v2/blobs`. It constructs `BlobCacheObjectId { domain_id, blob_id }` from query strings and parses `Box<BlobCacheEntry>` from request bodies. The private `convert_to_response` accepts `Empty`, `DaemonInfo`, and `BlobObjectList` payloads.

Control flow: v2 handlers use the same `EndpointHandler` contract as v1. Blob GET requires `domain_id` and treats missing `blob_id` as an empty string, allowing domain-wide queries. Blob PUT parses a `BlobCacheEntry`, calls `prepare_configuration_info()`, rejects invalid entries as `BadRequest`, and sends `CreateBlobObject`. DELETE prefers `domain_id` deletion/object deletion when present; otherwise it accepts `blob_id` alone for `DeleteBlobFile`.

State and persistence: the handler owns no persistent state. It validates and dispatches blob cache object operations to the API backend, where actual cache state is created or removed.

Dependencies and integration points: depends on `BlobCacheEntry` from the crate root, `ApiRequest`/`BlobCacheObjectId`, and shared HTTP helper functions. Registered by `HTTP_ROUTES` as `/api/v2/daemon` and `/api/v2/blobs`.

Risks: unexpected response payloads panic. DELETE semantics are parameter-sensitive: `domain_id` wins over `blob_id`-only deletion, so clients must choose query strings carefully. PUT rejects configs only after JSON parse succeeds and `prepare_configuration_info()` runs.

Test signals: unit tests cover daemon GET/PUT/bad method, blob GET required domain, invalid PUT config, both delete forms, unsupported POST, and API error conversion.
