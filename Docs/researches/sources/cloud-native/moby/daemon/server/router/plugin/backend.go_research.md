# sources/cloud-native/moby/daemon/server/router/plugin/backend.go

## Purpose
`backend.go` defines the plugin router backend contract for plugin lifecycle, registry operations, and local plugin creation.

## Important APIs, Types, And Functions
`Backend` includes `Disable`, `Enable`, `List`, `Inspect`, `Remove`, `Set`, `Privileges`, `Pull`, `Push`, `Upgrade`, and `CreateFromContext`.

## Control Flow
Route handlers parse HTTP fields, decode auth/meta headers, then delegate plugin state changes and registry streaming operations to this interface.

## State And Persistence
Implementations persist plugin installation/configuration state and may perform registry push/pull/upgrade side effects.

## Dependencies And Integration Points
Depends on distribution references, API plugin/registry types, daemon filters, plugin creation options, and server backend option structs.

## Risks
The interface mixes local lifecycle and remote registry operations; streaming operations must be careful about progress output and late errors.

## Test Signals
Compile-time satisfaction by plugin manager implementations and plugin API integration tests validate the contract.
