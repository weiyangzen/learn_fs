<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/newbt.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/newbt.h

Purpose: Defines the shared state and API for replacement-btree staging used by XFS online repair.

Important APIs, types, and functions: `struct xrep_newbt_resv` records a reserved extent, perag reference, autoreap handle, AG block start, length, and used count. `struct xrep_newbt` records scrub context, optional allocator callback, reservation list, fake btree root, owner info, bload geometry, allocation hint, and reservation type. The header declares all initialization, allocation, claim, commit/cancel, and unused-block helpers.

Control flow: Repair code initializes an `xrep_newbt`, configures its `bload` callbacks, allocates or adds extents, lets the bulk loader claim blocks, then calls commit after publishing the new root or cancel on failure.

State and persistence: The structs hold transient reservation accounting for blocks that may become durable btree blocks once a caller commits staged roots. Autoreap state is critical for crash-safe cleanup if the repair does not commit.

Dependencies and integration points: Depends on list heads, `xfs_perag`, allocation autoreap, fake btree roots, owner info, bload geometry, fsblock/agblock types, and reservation classes. It is the contract between specific repair algorithms and `newbt.c`.

Risks and test signals: Misconfigured owner info or reservation type can corrupt rmap/accounting. Test API consumers for balanced commit/cancel, correct fake-root flavor, valid allocation hints, reserved extent ownership, and no remaining unused blocks when geometry estimates are exact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/newbt.h -->
