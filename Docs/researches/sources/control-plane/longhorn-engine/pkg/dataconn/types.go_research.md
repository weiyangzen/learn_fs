# sources/control-plane/longhorn-engine/pkg/dataconn/types.go

Purpose: defines the in-memory message model and numeric command/status constants for the Longhorn data connection protocol.

Important APIs/types/functions: message types include `TypeRead`, `TypeWrite`, `TypeResponse`, `TypeError`, `TypeEOF`, `TypeClose`, `TypePing`, `TypeUnmap`, and `TypeENOSPC`. `MagicVersion` is `0x1b01` and is checked by `Wire.Read`. `Message` carries `Complete`, protocol header fields, payload `Data`, a private `transportErr`, and `journal.OpID` for sparse-tools operation tracking.

Control flow: this file has no executable control flow. The constants drive dispatch in `server.go`, client-side request handling, and wire serialization.

State and persistence: no persistence. `Message` is a transient request/response envelope. `Seq` and `ID` provide correlation/tracing state while the connection is live.

Dependencies and integration points: imports `github.com/longhorn/sparse-tools/stats` for operation IDs. `Wire` serializes a subset of `Message` fields; `Complete`, `transportErr`, and `ID` are local-only.

Risks: `messageSize` is marked unused and can drift from the actual header size computed in `wire.go`. Numeric message constants are untyped and not range-checked by `Wire.Read`, so callers must validate semantics. Adding fields to `Message` does not change the wire format unless `getRequestHeaderSize` and read/write code are also updated.

Test signals: no direct tests. The constants are compile-time inputs to dataconn client/server behavior.
