## sources/control-plane/longhorn-engine/pkg/types/error.go

### Purpose
`error.go` defines Longhorn engine structured errors and helper functions for preserving function and rollback outcomes across local and gRPC boundaries.

### Important APIs, Types, And Functions
`ErrorCode` enumerates `ResultUnknown`, `FunctionFailedWithoutRollback`, `FunctionFailedRollbackSucceeded`, and `FunctionFailedRollbackFailed`. `Error` carries `Code`, `Message`, and `RollbackMessage`, implements `error`, and can serialize itself with `ToJSONString`. `WrapError` prefixes structured or unstructured errors, `CombineErrors` concatenates non-nil errors, `GenerateFunctionErrorWithRollback` maps function/rollback result pairs to a structured error, and `UnmarshalGRPCError` decodes a gRPC status message containing the JSON form.

### Control Flow
Callers build structured errors with `NewError` or by wrapping failures. Rollback-aware callers pass both primary and rollback errors to `GenerateFunctionErrorWithRollback`, which selects the most specific code. gRPC clients call `UnmarshalGRPCError` to recover structured fields from a status message.

### State, Persistence, And Dependencies
No state is persisted. The durable contract is the JSON shape embedded in status messages or logs. Dependencies are `encoding/json`, standard `errors`/`fmt`, and `google.golang.org/grpc/status`.

### Integration Points
The constants are used by engine APIs and rollback-capable workflows. `ErrNoSpaceLeftOnDevice` and `CannotRequestHashingSnapshotPrefix` are shared sentinel/message fragments used elsewhere in sync and replica logic.

### Risks
`WrapError` mutates an existing `*Error` in place, so sharing the same error object across callers can unexpectedly rewrite its message. `UnmarshalGRPCError` assumes the gRPC status message is JSON and returns `ResultUnknown` if not. `CombineErrors` loses structured fields by formatting combined strings.

### Test Signals
Tests should cover JSON serialization, rollback outcome mapping, wrapping structured versus unstructured errors, malformed gRPC statuses, and nil handling in `WrapError`/`CombineErrors`.
