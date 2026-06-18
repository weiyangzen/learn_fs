# sources/cloud-native/buildkit/client/status.go

## Purpose
This file converts BuildKit control API status protobufs to client-facing status structs and can marshal accumulated client status back into one or more protobuf `StatusResponse` messages. It is the client-side status adapter for solve progress, logs, warnings, and vertex metadata.

## Important APIs, Types, and Functions
- `NewSolveStatus(resp)` converts protobuf `Vertex`, `VertexStatus`, `VertexLog`, and `VertexWarning` values into `SolveStatus` fields.
- `SolveStatus.Marshal()` converts the client struct back to protobuf messages and chunks large logs.
- Helper functions convert digest slices and optional timestamps: `digestSliceFromPB`, `digestSliceToPB`, `timestampFromPB`, and `timestampToPB`.
- `emptyLogVertexSize` caches the VT protobuf size overhead used for log chunking.

## Control Flow
`NewSolveStatus` iterates each repeated protobuf field and appends converted client values. `Marshal` builds a response with all vertexes and statuses, then appends logs until the accumulated approximate log size exceeds 1 MiB. When the threshold is crossed, it clears already-emitted vertex/status fields, slices consumed logs off `ss.Logs`, appends the partial response, and repeats until all logs are emitted. Warnings are included in each generated response pass after logs are processed.

## State and Persistence Behavior
The file has no persistent storage. `Marshal` mutates the receiver when log splitting occurs by clearing `Vertexes`/`Statuses` and advancing `Logs`, so callers should not assume the original `SolveStatus` remains intact after marshaling large logs.

## Dependencies and Integration Points
It depends on the control API protobuf types, OpenContainers digests, protobuf timestamps, and status structs from the client package. `solve.go` uses `NewSolveStatus` to send streamed daemon status into the caller-provided channel.

## Risks and Edge Cases
The main behavioral risk is mutation during `Marshal`, which may surprise callers that reuse a `SolveStatus`. Timestamp conversion assumes non-nil protobuf timestamps for statuses/logs where `AsTime` is called directly. Log chunking is approximate and based on message bytes plus empty-log protobuf overhead.

## Test Signals
No direct tests are listed for this file in this work item. Indirect coverage comes from integration tests that read solve logs, such as proxy-network policy tests, and any callers that marshal status for replay or frontend communication.
