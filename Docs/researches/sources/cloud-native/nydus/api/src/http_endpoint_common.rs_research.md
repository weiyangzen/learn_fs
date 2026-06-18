# sources/cloud-native/nydus/api/src/http_endpoint_common.rs

## Purpose
This module implements common HTTP endpoint handlers for daemon start/exit/events, backend/blobcache metrics, mount/remount/umount, and FUSE fd upgrade handoff operations.

## Important APIs, Types, and Functions
- `convert_to_response()` maps an `ApiResponse` into a `dbs_uhttp::Response`, accepting only `Empty`, `Events`, `BackendMetrics`, and `BlobcacheMetrics` payloads and converting errors through a supplied `HttpError` constructor.
- `StartHandler`, `ExitHandler`, `EventsHandler`, `MetricsBackendHandler`, `MetricsBlobcacheHandler`, `MountHandler`, `SendFuseFdHandler`, and `TakeoverFuseFdHandler` implement `EndpointHandler`.
- Handlers use `extract_query_part`, `parse_body`, `success_response`, `error_response`, and `translate_status_code` from `http_handler`.

## Control Flow
Each handler pattern-matches request method and body presence. Valid requests create an `ApiRequest` and call `kicker`, a callback into the API service. The response is converted to HTTP success/error. Mount handling additionally requires `mountpoint` query parameter and dispatches POST to `Mount`, PUT to `Remount`, and DELETE to `Umount`. Metrics handlers optionally extract `id`.

## State and Persistence
Handlers are stateless structs. They can trigger daemon state changes through `ApiRequest` variants: start, exit, mount lifecycle, and FUSE fd transfer/takeover. They do not persist data directly.

## Dependencies and Integration Points
This module depends on `dbs-uhttp`, `crate::http`, and `crate::http_handler`. It implements server-side behavior corresponding to parts of the v1 OpenAPI contract and daemon upgrade lifecycle.

## Risks and Edge Cases
`convert_to_response()` panics on unexpected successful payload variants, so incorrect service-handler pairing can crash the API server. Request validation is strict about body absence/presence; clients sending harmless bodies on PUT start/exit or DELETE mount receive bad request. Mountpoint extraction is required even before method/body matching in `MountHandler`.

## Test Signals
The module has focused unit tests for valid and invalid methods across handlers, missing mountpoint, mount POST/PUT/DELETE with bodies, metrics responses, and FUSE fd handlers. These validate request dispatch but not full status-code/error-body serialization.
