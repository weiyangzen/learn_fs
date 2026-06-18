<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/mount/mount.go -->
# sources/cloud-native/moby/api/types/mount/mount.go

## Purpose
Defines container mount specifications for bind, volume, tmpfs, named pipe, image, and cluster mount
modes.

## Important APIs, Types, And Functions
- Exported types: Type, Mount, Propagation, Consistency, BindOptions, VolumeOptions, ImageOptions, Driver, TmpfsOptions, ClusterOptions.
- Constants: TypeBind, TypeVolume, TypeTmpfs, TypeNamedPipe, TypeCluster, TypeImage, PropagationRPrivate, PropagationPrivate, PropagationRShared, PropagationShared, PropagationRSlave, PropagationSlave, ConsistencyFull, ConsistencyCached, ConsistencyDelegated, ConsistencyDefault.
- Exported variables: Propagations.
- `Mount` fields include Type, Source, Target, ReadOnly, Consistency, BindOptions, VolumeOptions, ImageOptions, TmpfsOptions, ClusterOptions.
- `BindOptions` fields include Propagation, NonRecursive, CreateMountpoint, ReadOnlyNonRecursive, ReadOnlyForceRecursive.
- `VolumeOptions` fields include NoCopy, Labels, Subpath, DriverConfig.
- `ImageOptions` fields include Subpath.
- `Driver` fields include Name, Options.
- Source comments highlight: Type represents the type of a mount. Mount represents a mount (volume). Propagation represents the propagation of a mount.
- The nested option structs hold propagation, consistency, copy, label, subpath, tmpfs, and cluster-volume behavior.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.

## Dependencies And Integration Points
- Imports: `os`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- No direct test file is paired with this source; coverage is mostly integration-level through daemon/client API tests and compile-time use by downstream packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/mount/mount.go -->
