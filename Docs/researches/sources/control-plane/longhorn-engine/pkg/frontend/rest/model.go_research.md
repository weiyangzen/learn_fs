# sources/control-plane/longhorn-engine/pkg/frontend/rest/model.go

Purpose: defines Rancher API schemas and request/response models for the REST frontend.

Important APIs/types/functions: `Volume` describes the exposed volume resource. `ReadInput` accepts string-encoded `offset` and `length`; `ReadOutput` returns base64 `Data`. `WriteInput` accepts `Offset`, `Length`, and base64 `Data`; `WriteOutput` is empty aside from resource metadata. `NewVolume` creates volume resources with `readat` and `writeat` action links. `EncodeID`/`DecodeID` and `EncodeData`/`DecodeData` use standard base64. `NewSchema` registers the API resource types and action contracts. `Server` holds the `Device`.

Control flow: schema construction is static. Runtime handlers use base64 IDs to match the single configured volume and base64 data to move arbitrary bytes through JSON.

State and persistence: no persistence. Resource IDs are deterministic encodings of volume names.

Dependencies and integration points: used by `router.go` and `server.go`. Depends on `github.com/rancher/go-rancher/api` and `client` resource/schema types.

Risks: base64 standard encoding includes `/`, `+`, and `=`, which can be awkward in path segments unless URL escaped by clients. `ReadInput.Length` is int64 but later passed directly to `make([]byte, input.Length)` in `server.go`, risking bad allocation if negative or huge. `WriteInput.Offset` lacks `,string` while `ReadInput.Offset` uses it, making JSON conventions inconsistent.

Test signals: no direct tests. Encoding helpers and schema action presence are easy unit-test candidates.
