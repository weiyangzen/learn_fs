# sources/cloud-native/moby/daemon/cluster/convert/task.go

## Purpose
Converts swarmkit tasks to Docker API swarm task objects, including status, networks, volumes, generic resources, job iteration, and port status.

## Important APIs, Types, And Functions
Exports `TaskFromGRPC`.

## Control Flow
`TaskFromGRPC` first converts embedded task spec via `taskSpecFromGRPC`, then copies IDs, annotations, service/slot/node, status strings, desired state, generic resources, metadata timestamps, container status, network attachments, job iteration, volume attachments, and optional published port status.

## State And Persistence
No local state. It reads swarmkit task state that is stored and updated by swarmkit.

## Dependencies And Integration Points
Used by task list/inspect APIs and service logs/selectors. Depends on `networkAttachmentFromGRPC`, `GenericResourcesFromGRPC`, and gogo timestamp conversion.

## Risks And Test Signals
Enum conversion lower-cases swarmkit names; unknown values may produce unexpected API strings. `taskSpecFromGRPC` errors propagate for malformed plugin payloads. Service tests cover network attachment task specs; broader task API tests should cover status and ports.
