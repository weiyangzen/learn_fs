# sources/cloud-native/cri-o/server/server_test_inject.go

## Purpose
Test-only injection helper compiled with the `test` build tag.

## Important APIs, Types, And Functions
`(*StreamService).SetRuntimeServer(server *Server)` assigns the private `runtimeServer` field so tests can wire a streaming service without going through production construction paths.

## Control Flow
No branching; the setter directly mutates the `StreamService`.

## State And Persistence
Process-local test state only. It does not persist data.

## Dependencies And Integration Points
Used by `server/suite_test.go` when constructing a `k8s.io/cri-streaming` server backed by the CRI-O stream service.

## Risks And Test Signals
Because this bypasses encapsulation, it must remain test-build-only. A signature or field-name drift in `StreamService` will break tests at compile time.
