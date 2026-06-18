# sources/cloud-native/cri-o/internal/factory/container/namespaces.go

## Purpose
Exposes the managed PID namespace associated with a container factory object after target-PID namespace setup.

## Important APIs, Types, And Functions
- `(*container).PidNamespace() nsmgr.Namespace` returns the `c.pidns` field.

## Control Flow
There is no branching. Linux `SpecAddNamespaces` may set `c.pidns` when `NamespaceMode_TARGET` is requested, and this accessor exposes it to callers/tests for cleanup or inspection.

## State And Persistence
No persistence occurs. It reads in-memory container factory state. The returned namespace may represent a managed namespace requiring removal by the caller.

## Dependencies And Integration Points
Depends on `internal/config/nsmgr.Namespace`. Used by namespace tests to verify and clean up target PID namespaces.

## Risks And Edge Cases
May return nil when no target PID namespace was configured. Callers must guard nil and must not assume ownership unless the namespace was created by the namespace manager.

## Test Signals
`namespaces_test.go` checks that `PidNamespace()` becomes non-nil for target PID namespace mode and uses it for cleanup.
