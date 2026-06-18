# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/list.go

## Purpose
Retrieves and converts storage pool information from management into BeeGFS-native entity ID sets and quota-limit pointers for CTL display or downstream mapping.

## Important APIs, Types, And Functions
Exports `GetStoragePools_Result`, `GetStoragePools_Config`, and `GetStoragePools`.

## Control Flow
`GetStoragePools` obtains management client, calls `GetPools` with optional quota limits, converts each protobuf pool ID, target ID, and buddy-group ID using `beegfs.EntityIdSetFromProto`, and appends quota limit pointer fields directly from the response.

## State And Persistence
No local state. It reads management state and returns an in-memory snapshot.

## Dependencies And Integration Points
Used by utilities such as `util.GetMappings` and entry migration/set operations. Depends on management protobuf API and common BeeGFS entity conversion.

## Risks And Edge Cases
A single malformed entity ID aborts the entire list. Quota limit pointers use nil versus `-1` semantics from management; consumers must preserve this distinction. The local variable `buddy_groups` is stylistically non-Go but behaviorally harmless.

## Test Signals
No direct tests. Tests should cover conversion failures and `WithLimits` propagation.
