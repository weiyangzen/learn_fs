# sources/cloud-native/containerd/core/mount/manager.go

Purpose: defines mount manager interfaces and shared data structures for activating, tracking, transforming, and deactivating mount sets.

Important APIs and types: `Manager`, `Handler`, `Transformer`, `ActivateOptions`, `ActivateOpt`, `WithTemporary`, `WithLabels`, `WithAllowMountType`, `ActiveMount`, and `ActivationInfo`.

Control flow: this file is interface and option definitions only. Option helpers mutate `ActivateOptions`. Implementations elsewhere use `Manager.Activate` to turn a mount array into manager-handled active mounts plus remaining system mounts, and use `Deactivate`, `Info`, `Update`, and `List` for lifecycle/state.

State and persistence: defines the in-memory shape of activation state. `ActivationInfo` includes unique name, active manager-handled mounts, remaining system mounts, and labels. `ActiveMount` records mount data, mountpoint, mounted time, and type-specific metadata.

Dependencies and integration: core contract for custom mount plugins such as loopback handlers and any bbolt-backed manager implementation. Uses context and time only.

Risks: interface comments establish important semantics: manager-handled mounts occur outside the container namespace, and returned system mounts are expected to be mounted by the runtime/container side. `AllowMountTypes` supports suffix matching by convention, which implementations must enforce consistently.

Test signals: no direct tests in subset.
