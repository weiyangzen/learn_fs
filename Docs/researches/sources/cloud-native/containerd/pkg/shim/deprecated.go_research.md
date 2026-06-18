<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/deprecated.go -->
# sources/cloud-native/containerd/pkg/shim/deprecated.go

## Purpose
Deprecated shim Manager API wrapper retained for older shim implementations.

## Important APIs, Types, And Functions
StartOpts, BootstrapParams, Manager, managerShim, and Run bridge the old Manager interface to the new Shim interface.

## Control Flow
Run wraps a Manager in managerShim and calls the shared run path. managerShim.Start maps BootstrapParams to StartOpts and maps the old result back to bootapi.BootstrapResult.

## State And Persistence
No state beyond wrapped manager references.

## Dependencies And Integration Points
Integrates legacy shim binaries with bootapi-based RunShim.

## Risks And Edge Cases
Deprecated fields and protocol strings must remain compatible until callers are migrated.

## Test Signals
Indirectly covered by older shim integration paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/deprecated.go -->
