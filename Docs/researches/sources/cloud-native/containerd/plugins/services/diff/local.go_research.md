# sources/cloud-native/containerd/plugins/services/diff/local.go

## Purpose
Registers and implements the local diff service client that selects an ordered chain of differs for apply and diff operations.

## Important APIs, Types, And Functions
`config` controls differ order and global `sync_fs`. `differ` combines comparer and applier. `local.Apply` and `local.Diff` implement the API client by translating protobuf mounts/descriptors/options and trying differs in order.

## Control Flow
Startup loads all diff plugins, validates configured order names and interfaces, and returns `local`. Apply converts the descriptor and mounts, decodes payloads, enforces global syncfs if configured, calls each differ until an error other than `ErrNotImplemented`, and returns the applied descriptor. Diff converts mounts, maps media/ref/labels/source-date options, tries compares in order, and returns the diff descriptor.

## State And Persistence
No direct persistence. Underlying differs write content store blobs or snapshot layer files depending on operation.

## Dependencies And Integration Points
Depends on diff plugins, mount/proto conversion, OCI descriptor conversion, typeurl payloads, errgrpc, and platform-specific default config files.

## Risks
If configured differ order references a missing plugin, startup fails. Fallback only works for errors recognized as `ErrNotImplemented`. Global syncfs overrides request behavior.

## Test Signals
No direct tests in this subset.
