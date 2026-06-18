<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager_windows.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/manager_windows.go

## Purpose
Provides Windows stubs for manager lifecycle internals.

## Important APIs, Types, And Functions
Stubbed functions include `enable`, `initSpec`, `disable`, `restore`, `Shutdown`, and `recursiveUnmount`.

## Control Flow
Lifecycle methods return `fmt.Errorf("Not implemented")`, `Shutdown` is a no-op, and `recursiveUnmount` returns nil.

## State, Dependencies, And Integration Points
No state is mutated. This file preserves package shape for Windows builds where the Linux managed-plugin runtime is unavailable.

## Risks And Test Signals
The error text is capitalized and generic. Backend unsupported stubs are the public surface; these internal stubs guard compile compatibility. Windows build tests are the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager_windows.go -->
