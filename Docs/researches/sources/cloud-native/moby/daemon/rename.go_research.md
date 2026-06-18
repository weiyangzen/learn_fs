# sources/cloud-native/moby/daemon/rename.go

## Purpose
Implements container rename, including name reservation, linked-container alias updates, checkpoint persistence, sandbox rename, endpoint DNS name updates, rollback on failure, and event emission.

## Important APIs, Types, And Functions
`Daemon.ContainerRename(oldName, newName string)` is the public operation. It uses `GetContainer`, container locking, `reserveName`/`releaseName`, `linkIndex`, `containersReplica`, `CheckpointTo`, libnetwork sandbox/endpoint methods, `buildEndpointDNSNames`, and rename events.

## Control Flow
The function trims and validates names, loads and locks the container, canonicalizes the new name, rejects same-name renames, snapshots linked child suffixes, reserves new names for the container and links, updates container name and link index, checkpoints state, then for running containers renames the sandbox and updates endpoint DNS names. Deferred rollback restores names, reservations, link index entries, checkpoint state, sandbox name, and DNS names if a later step fails.

## State And Persistence
Mutates in-memory container name, name indexes, link indexes, network endpoint settings, and sandbox state. Persists the new container name to disk with `CheckpointTo`; rollback attempts to persist the old name if a post-checkpoint error occurs.

## Dependencies And Integration Points
Integrates with container store, name reservation replica, legacy links, libnetwork sandbox and endpoints, daemon event service, and persistent container metadata.

## Risks And Edge Cases
The function has multiple partial-mutation stages and relies heavily on deferred rollback. Rollback of sandbox and DNS failures is logged but cannot be guaranteed. Linked child names must be prefixed by the old container name or the operation aborts. Running containers have more external state to coordinate than stopped containers.

## Test Signals
No listed direct test, but rename API and network integration tests should assert name reservation conflicts, persistent metadata, event attributes, and DNS alias updates.
