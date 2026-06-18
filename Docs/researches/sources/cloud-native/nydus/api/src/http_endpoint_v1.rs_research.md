# sources/cloud-native/nydus/api/src/http_endpoint_v1.rs

Purpose: implements Nydus HTTP API v1 endpoint handlers below `HTTP_ROOT_V1 = "/api/v1"`. It translates `dbs_uhttp::Request` objects into typed `ApiRequest` messages and translates `ApiResponse` values back into JSON HTTP responses.

Important APIs/types/functions: `InfoHandler`, `FsBackendInfo`, `MetricsFsGlobalHandler`, `MetricsFsAccessPatternHandler`, `MetricsFsFilesHandler`, `MetricsFsInflightHandler`, and `ConfigHandler` all implement `EndpointHandler`. The private `convert_to_response` accepts only v1-compatible payloads: `Empty`, daemon info, filesystem metrics, backend info, inflight metrics, access patterns, and config maps.

Control flow: every handler pattern matches `(req.method(), req.body.as_ref())`, validates required query parameters or JSON body, calls the provided `kicker` closure with a concrete `ApiRequest`, then wraps the result through `convert_to_response`. `GET /daemon/backend` requires `mountpoint`; metrics endpoints optionally read `id`; file metrics also parses `latest` as bool with invalid values falling back to false. `PUT /config` parses `Config` and optionally accepts `id`.

State and persistence: the file is stateless. It only reads HTTP body/query values and forwards operations to the API server; durable state changes happen behind `ApiRequest::ConfigureDaemon` and `ApiRequest::UpdateConfig`.

Dependencies and integration points: depends on `dbs_uhttp`, common HTTP helpers in `http_handler`, and API enums/errors in `crate::http`. It is registered from `HTTP_ROUTES` in `http_handler.rs`.

Risks: unexpected `ApiResponsePayload` variants panic, so API service/handler response contracts must stay synchronized. Query extraction is string-based and boolean parse failures are silently treated as false. `Config` responses stringify a map manually before returning a body.

Test signals: unit tests cover happy and bad-method paths, required `mountpoint`, config get/put, metrics query options, and API errors returning HTTP error responses without failing the micro-http processing layer.
