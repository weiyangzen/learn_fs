<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/configs.go -->
# sources/cloud-native/moby/daemon/configs.go

## Purpose
Adds swarm config references to an existing daemon container.

## Important APIs, Types, And Functions
`Daemon.SetContainerConfigReferences` resolves a container by name/id and appends `*swarmtypes.ConfigReference` values to `c.ConfigReferences`.

## Control Flow
The method calls `GetContainer`; on success it appends all refs and returns nil.

## State And Persistence Behavior
Mutates the in-memory container object only. This function does not lock the container or checkpoint to disk by itself.

## Dependencies And Integration Points
Integrates daemon container lookup with swarm config reference handling used later by container mount generation.

## Risks And Test Signals
Risks include no explicit locking/checkpointing and duplicate refs if called repeatedly. Mount-related container code is the downstream signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/configs.go -->
