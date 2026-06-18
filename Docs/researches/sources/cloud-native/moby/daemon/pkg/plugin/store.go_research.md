<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/store.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/store.go

## Purpose
Implements the in-memory managed plugin inventory plus compatibility lookups for legacy v1 plugins.

## Important APIs, Types, And Functions
Key methods include `GetV2Plugin`, `validateName`, `GetAll`, `SetAll`, `SetState`, `Add`, `Remove`, `Get`, `GetAllManagedPluginsByCap`, `GetAllByCap`, `Handle`, `CallHandler`, and plugin ID/name resolution helpers. `pluginType` formats Docker capability identifiers.

## Control Flow
Lookups resolve name, full ID, or partial ID, then filter by capability and enabled state. `Get` increments refcount only after an enabled plugin passes capability filtering, and falls back to legacy plugins when allowed. Handlers are registered by capability and called when matching plugins become available.

## State, Dependencies, And Integration Points
State is protected by `Store`'s RW mutex and includes managed plugins, spec options, and legacy callbacks. It integrates with `plugingetter`, legacy `pkg/plugins`, and manager lifecycle.

## Risks And Test Signals
Partial ID/name ambiguity is a user-facing risk. Reference counts must not change on failed capability checks; `store_test.go` covers that.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/store.go -->
