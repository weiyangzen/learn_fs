<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_tcam.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_tcam.c

## Purpose

`spectrum_acl_tcam.c` is the generic TCAM virtualization layer for Spectrum ACL profiles. It allocates ACL/TCAM region and group IDs, groups regions by priority, creates virtual regions and chunks based on flexible-key usage, inserts virtual entries through chip-specific backend ops, handles delayed A-TCAM rehash migration, exposes a devlink rehash interval parameter, and registers profile ops for TC flower and multicast-router ACL users.

## Important APIs, Types, And Functions

- `struct mlxsw_sp_acl_tcam` stores used-region/group IDAs, hardware limits, virtual-region list, rehash interval, lock, and backend-private storage.
- `struct mlxsw_sp_acl_tcam_vgroup`, `vregion`, `vchunk`, and `ventry` model profile rulesets, compatible key layouts, priority chunks, and entries.
- `mlxsw_sp_acl_tcam_init()` / `fini()` initialize resources, devlink params, and chip backend ops.
- `mlxsw_sp_acl_tcam_priority_get()` converts Linux priority to hardware priority when requested.
- Region helpers allocate/free IDs, associate/allocate/enable/free hardware regions, and attach/detach them from groups.
- Rehash helpers create a second region, migrate entries with a credit budget, roll back on errors, and destroy the old region when complete.
- Flower profile ops bind groups to ports and support activity reads.
- MR profile ops pre-create a chunk, skip port binding, and allow action replacement for multicast routes.

## Control Flow

Ruleset creation creates a virtual group and hardware group. When the first rule for a priority arrives, the layer finds a compatible virtual region by priority and AFK element usage; if none exists, it chooses a configured pattern, creates key-info, allocates and enables a hardware region, and attaches it to the group. It then creates or reuses a virtual chunk for that priority and asks backend ops to create a concrete entry. Group updates write `PAGT`; port binds write `PPBT`.

For rehash-capable backends, each virtual region has delayed work. Rehash asks the backend for hints, creates a new hardware region with those hints, attaches it next to the old region, then migrates chunks and entries under a credit budget. If migration fails, it swaps back and rolls entries back to the old region. If credits run out, context markers let the next work item resume. On success, the old region is detached/destroyed and hints are released. A devlink runtime parameter can disable rehash or force immediate scheduling after interval changes.

## State And Persistence

State is mostly in memory: IDA allocations, virtual groups/regions/chunks/entries, refcounts, AFK key-info references, and rehash context markers. Hardware state includes `PTAR` regions, `PACL` enables, `PAGT` groups, `PPBT` binds, and backend entries. Rehash temporarily duplicates region state through `region2` and `chunk2`.

## Dependencies And Integration Points

The layer depends on chip-specific `mlxsw_sp_acl_tcam_ops`, AFK key-info APIs, devlink params, tracepoints, resource IDs, the ACL high-level profile API, and backend files `spectrum_acl_atcam.c`/`ctcam.c`/`erp.c`. It is the main integration point between Linux flow rules and hardware TCAM programming.

## Risks

- Region splitting for incompatible key usage inside an existing priority span is explicitly unsupported and returns `-EOPNOTSUPP`.
- Rehash migration is complex: list changes during migration reset markers, but bugs can duplicate, lose, or misorder entries.
- Group region attach/detach writes hardware state while holding group locks; failed group updates must restore lists exactly.
- Hardware resource limits for regions, groups, group size, and priorities can fail late under scale.
- Devlink interval changes cancel/reschedule work while region locks and TCAM locks interact.

## Test Signals

Run TC flower rules with diverse key usages and priorities, chain/group binding to multiple ports, region/group exhaustion, region rehash under load, add/delete during rehash, migration rollback injection, devlink interval changes including zero, MR profile route add/update/delete, and hardware activity polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_tcam.c -->
