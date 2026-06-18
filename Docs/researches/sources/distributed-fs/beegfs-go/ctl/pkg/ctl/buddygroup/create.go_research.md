# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/create.go

Purpose: creates buddy mirror groups directly or automatically from eligible metadata/storage targets.

Important APIs/types/functions: `Create`; `AutoCreateConfig`; `AutoCreate`.

Control flow: `Create` forwards a protobuf request to management. `AutoCreate` gets logger, node store, existing buddy groups, and targets; filters targets by node type, existing group membership, and equal inode/space constraints unless ignored; checks minimum and even count; greedily pairs primaries and secondaries while enforcing same storage pool for storage and preferring different nodes; swaps meta primary if the root inode owner would otherwise become secondary; creates groups with generated aliases; returns created responses plus warnings for recoverable pairing/creation issues.

State and persistence: mutates management configuration by creating buddy groups. Auto-create can create multiple groups in one call.

Dependencies and integration points: uses management gRPC, target listing, node store root metadata information, BeeGFS entity/pool fields, and sorting/containment helpers.

Risks: greedy pairing may not find an optimal global matching. Documentation says constraint 3 can be removed by `IgnoreSpace`, but code uses `IgnoreUneven` for uneven counts. Results append `res` even if `Create` returns an error, potentially adding nil responses. Auto-generated aliases may collide. Same-node secondary is allowed with warning if no better target exists.

Test signals: no direct tests. Valuable tests would cover filtering, uneven handling, storage-pool pairing, root meta swap, warning accumulation, nil response on creation error, and duplicate/existing group exclusion.
