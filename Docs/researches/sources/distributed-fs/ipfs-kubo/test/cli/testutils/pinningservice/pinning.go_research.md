# sources/distributed-fs/ipfs-kubo/test/cli/testutils/pinningservice/pinning.go

Purpose: provides an in-memory Remote Pinning API implementation for CLI tests.

Important APIs and types: `NewRouter` registers `/api/v1/pins` routes for list/add/get/replace/delete and wraps them in `authHandler`. `PinningService` stores pins, a mutex, and a `PinAdded` callback. `Pin`, `PinStatus`, `AddPinRequest`, and `ListPinsResponse` model API payloads. Constants define match modes, statuses, and timestamp layout. `PinStatus.MarshalJSON` locks per-pin state during JSON marshaling.

Control flow: `authHandler` requires `Authorization: Bearer <token>` and returns structured JSON errors for missing/wrong tokens. `addPin` decodes a request, creates a queued `PinStatus` with UUID and timestamp, appends it under lock, writes HTTP 202, then invokes `PinAdded`. `listPins` parses filters for CID, name/match mode, status, before/after timestamps, limit, and meta, clones pin state for filtering, and returns original pointers up to the limit. `getPin`, `replacePin`, and `removePin` search by request ID and return success or 404 JSON errors.

State and persistence: pins live in memory. Service-level and per-pin mutexes protect concurrent test mutations, especially when tests change statuses while Kubo polls. `Clone` copies current fields but does not deep-copy nested maps/slices.

Dependencies and integration points: uses `httprouter`, Google UUIDs, JSON, HTTP status codes, reflection for meta comparison, and the Kubo remote pinning client.

Risks and test signals: the service is intentionally incomplete and only approximates the Remote Pinning API. It defaults list status to `pinned`, so tests must request queued/pinning/failed explicitly. The callback happens after the HTTP response, which lets tests simulate asynchronous transitions.
