# sources/distributed-fs/glusterfs/xlators/features/quota/src/quotad.c

## Purpose
`quotad.c` implements the quotad translator lifecycle and its nameless lookup helper. Quotad hosts the aggregator RPC service and routes quota validation lookups to the child subvolume matching the requested volume UUID.

## Important APIs and Functions
- `qd_init()`, `qd_fini()`, `qd_reconfigure()`, `qd_notify()`, `mem_acct_init()`, `xlator_api` implement translator lifecycle.
- `qd_notify()` starts the aggregator service when a parent-up event arrives.
- `qd_find_subvol()` scans child xlator options for `<child-name>.volume-id` matching the requested `volume_uuid`.
- `qd_nameless_lookup()` creates a loc with a new inode and supplied GFID, marks xdata with `QUOTA_READ_ONLY_KEY`, finds the target subvolume, and winds a child lookup with `qd_lookup_cbk`.
- `qd_lookup_cbk()` converts lower-layer lookup callback arguments into a `gfs3_lookup_rsp`, serializes xdata, and invokes the aggregator callback.

## Control Flow
Initialization validates at least one child, allocates `quota_priv_t`, and initializes its lock. On `GF_EVENT_PARENT_UP`, `quotad_aggregator_init()` starts the RPC service. Incoming aggregator handlers call `qd_nameless_lookup()`, which selects a subvolume by volume UUID and winds `lookup` to fetch quota metadata. The callback serializes the result for RPC reply submission.

## State and Persistence
`quota_priv_t` is stored in `this->private` and holds rpcsvc state initialized by the aggregator. No persistent quota metadata is written here; lower layers answer xattr requests. `qd_fini()` frees rpcsvc and private state. `qd_reconfigure()` currently does nothing because quotad is expected to restart on volfile alteration.

## Dependencies and Integration Points
This file integrates with `quotad-aggregator.c`, `quotad-helpers.c`, child xlators carrying volume-id options, GlusterFS sync/stack lookup interfaces, XDR response structs, and quota xdata keys. It exposes an empty FOP table because its primary role is RPC service and lookup routing rather than normal client FOP processing.

## Risks
- Volume routing depends on option key naming (`<child>.volume-id`) and exact UUID string match.
- `qd_lookup_cbk()` unconditionally `inode_unref(inode)`, so callback contracts must provide a valid inode when expected.
- `qd_fini()` frees `priv->rpcsvc` directly rather than using a richer rpcsvc shutdown path; lifecycle changes need care.
- The translator starts service on parent-up, not during `init()`, so event delivery is required for availability.

## Test Signals
Test quotad with multiple child volumes and matching/missing volume UUIDs, nameless lookup success/failure, xdata serialization failure, parent-up service initialization, and fini cleanup. End-to-end quota validation confirms `QUOTA_READ_ONLY_KEY` prevents mutating side effects from the lookup.
