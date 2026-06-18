# sources/cloud-native/containerd/api/runtime/bootstrap/v1/helpers_test.go

Purpose: unit tests for bootstrap extension helpers.

Important APIs/types/functions: `TestExtensions` verifies adding a typed runc options message and finding/unmarshaling it. `TestExtensionNotFound` verifies a missing extension returns `found=false` without error. `TestAddExtensionWithAny` verifies pre-wrapped `anypb.Any` is accepted without double wrapping and that its type URL still contains `Options`.

Control flow: each test creates a fresh `BootstrapParams`, calls helper methods, and uses `t.Fatalf` on unexpected errors or field values.

State/persistence: test-only in-memory state; no files or external services.

Dependencies/integration: imports `github.com/containerd/containerd/api/types/runc/options` as a concrete extension message, `anypb`, `strings`, and `testing`. These tests validate integration with generated protobuf Any behavior.

Risks/test signals: coverage does not include `LogLevelFromString`, nil receiver behavior beyond `FindExtension`, nil destination panic behavior, or malformed Any unmarshal errors. Existing tests are strong signals for typed extension round trips.
