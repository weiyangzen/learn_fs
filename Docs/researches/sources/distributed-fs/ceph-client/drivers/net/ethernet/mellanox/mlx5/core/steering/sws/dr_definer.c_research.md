# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_definer.c

Purpose: caches firmware match definer objects by selector/mask tuple and provides refcounted get/put operations.

Important APIs/functions/types: `mlx5dr_definer_get`, `mlx5dr_definer_put`, and internal `dr_definer_object` containing firmware id, format id, DW/byte selectors, match mask, and refcount.

Control flow: get scans the domain xarray for an identical definer. On miss, it allocates a new object, creates the firmware definer, rejects IDs beyond the 8-bit STE encoding limit, copies selectors/mask, sets refcount, and inserts it by ID into `dmn->definers_xa`. On hit, it increments the refcount. Put loads by ID, logs if missing, and destroys/erases the object when the refcount reaches zero.

State/persistence: definers are firmware general objects cached in `dmn->definers_xa` for the domain lifetime or until the last user releases them. No disk persistence.

Dependencies/integration: used by range action creation and any code needing SELECT definers. Depends on command create/destroy helpers, DR STE match-tag size, xarray, and refcount APIs.

Risks: find and insert are not locally locked; callers need domain-level synchronization to avoid duplicate creation races. Firmware definer IDs greater than 255 are unusable by STE format and cause cleanup. Put with a stale/missing ID only logs, so caller lifecycle bugs may leak references elsewhere.

Test signals: duplicate get returns same ID and increments refcount, put destroys only after final release, selector/mask mismatch creates distinct objects, high firmware ID rejection, and concurrent get race coverage under expected locks.
