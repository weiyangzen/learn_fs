# sources/cloud-native/moby/daemon/secrets.go

## Purpose
Stores swarm secret references on a container by name.

## Important APIs, Types, And Functions
`Daemon.SetContainerSecretReferences(name string, refs []*swarmtypes.SecretReference) error` resolves a container and assigns `c.SecretReferences`.

## Control Flow
The function calls `GetContainer`; on success it replaces the container's secret reference slice and returns nil.

## State And Persistence
Mutates the in-memory container object. Persistence, if required, is handled by callers or later checkpoint paths, not in this function.

## Dependencies And Integration Points
Integrates with swarm secret types and daemon container lookup. It is likely called during service/task container setup.

## Risks And Edge Cases
The assignment is not protected by an explicit container lock in this function, so callers must ensure safe timing. Existing references are replaced wholesale.

## Test Signals
No direct tests in the listed set; integration tests around swarm secret injection should validate correct references.
