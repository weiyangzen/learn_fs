<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/backend_unsupported.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/backend_unsupported.go

## Purpose
Provides non-Linux stubs for plugin backend API methods on platforms that do not support managed plugins.

## Important APIs, Types, And Functions
Defines `errNotSupported` and stubs for `Disable`, `Enable`, `Inspect`, `Privileges`, `Pull`, `Upgrade`, `List`, `Push`, `Remove`, `Set`, and `CreateFromContext`.

## Control Flow
Every method immediately returns `errNotSupported` or nil result plus that error.

## State, Dependencies, And Integration Points
No state. Build tags select this file for `!linux`, preserving API compatibility for daemon builds while disabling functionality.

## Risks And Test Signals
Callers must handle unsupported errors consistently. The file prevents accidental Linux-only dependency leakage into unsupported builds; platform compile tests are the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/backend_unsupported.go -->
