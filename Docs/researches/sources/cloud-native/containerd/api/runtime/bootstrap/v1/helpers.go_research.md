# sources/cloud-native/containerd/api/runtime/bootstrap/v1/helpers.go

Purpose: hand-written convenience helpers around the generated bootstrap protocol.

Important APIs/types/functions: `LogLevelFromString` converts logrus-style strings and numeric strings into `LogLevel`, defaulting unknown values to info. `(*BootstrapParams).AddExtension` appends a protobuf message as an `Extension`, avoiding double wrapping when the input is already `*anypb.Any`. `(*BootstrapParams).FindExtension` searches extensions for a message type matching `dst` and unmarshals into it.

Control flow: `LogLevelFromString` uses a switch for known strings, then `strconv.ParseInt` for numeric input. `AddExtension` type-checks for `*anypb.Any` or calls `anypb.New`. `FindExtension` nil-checks the receiver, derives the destination full name for errors, iterates extensions, uses `MessageIs`, and returns on the first successful unmarshal.

State/persistence: mutates `BootstrapParams.Extensions` in memory. Does not persist outside the eventual serialized bootstrap params.

Dependencies/integration: imports `fmt`, `strconv`, protobuf `proto`, and `anypb`. Integrates generated `BootstrapParams` with callers that need typed extension configuration.

Risks/test signals: `FindExtension` assumes `dst` is non-nil; passing nil would panic via `ProtoReflect`. Unknown textual log levels silently become info, which may hide typoed configuration. Tests in `helpers_test.go` cover add/find, missing extensions, and pre-wrapped Any values.
