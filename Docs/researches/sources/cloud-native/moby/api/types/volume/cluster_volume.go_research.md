<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/volume/cluster_volume.go -->
# sources/cloud-native/moby/api/types/volume/cluster_volume.go

## Purpose
Defines Swarm cluster volume API models, including availability, access mode, topology, capacity,
publish status, secrets, and volume info.

## Important APIs, Types, And Functions
- Exported types: ClusterVolume, ClusterVolumeSpec, Availability, AccessMode, Scope, SharingMode, TypeBlock, TypeMount, TopologyRequirement, Topology, CapacityRange, Secret, PublishState, PublishStatus, Info.
- Constants: AvailabilityActive, AvailabilityPause, AvailabilityDrain, ScopeSingleNode, ScopeMultiNode, SharingNone, SharingReadOnly, SharingOneWriter, SharingAll, StatePending, StatePublished, StatePendingNodeUnpublish, StatePendingUnpublish.
- `ClusterVolume` fields include ID, Spec, PublishStatus, Info.
- `ClusterVolumeSpec` fields include Group, AccessMode, AccessibilityRequirements, CapacityRange, Secrets, Availability.
- `AccessMode` fields include Scope, Sharing, MountVolume, BlockVolume.
- `TypeBlock` fields include FsType, MountFlags.
- `TopologyRequirement` fields include Requisite, Preferred.
- Source comments highlight: ClusterVolume contains options and information specific to, and only present on, Swarm CSI cluster volumes. ClusterVolumeSpec contains the spec used to create this volume. Availability specifies the availability of the volume.
- These structs bridge Docker volume APIs with Swarm orchestration and CSI-like scheduling concepts.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `github.com/moby/moby/api/types/swarm`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- No direct test file is paired with this source; coverage is mostly integration-level through daemon/client API tests and compile-time use by downstream packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/volume/cluster_volume.go -->
