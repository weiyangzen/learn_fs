<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_atcam.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_atcam.c

## Purpose

`spectrum_acl_atcam.c` implements the algorithmic TCAM backend used by Spectrum-2 and newer ACL regions. It maps encoded rule keys and ERP masks to `PTCE3` entries, tracks duplicate keys, manages large-key IDs for 12-block regions, and spills entries to the C-TCAM backend when A-TCAM insertion is not possible.

## Important APIs, Types, And Functions

- `struct mlxsw_sp_acl_atcam_region` owns the A-TCAM entry hash/list, C-TCAM fallback region, ERP table, type-specific operations, and backend-private state.
- `struct mlxsw_sp_acl_atcam_entry` stores the hash key, delta metadata, C-TCAM fallback entry, large-key id, and ERP mask.
- Generic region ops use a dummy large-key id; 12KB region ops allocate/refcount real large-key IDs from a bitmap and hash table.
- `mlxsw_sp_acl_atcam_region_associate()` maps ACL region ids to hardware regions using `PERAR`.
- `mlxsw_sp_acl_atcam_region_init()` initializes entry hash/list, type-specific state, ERP state, and C-TCAM fallback.
- `mlxsw_sp_acl_atcam_entry_add()`, `entry_del()`, and `entry_action_replace()` are the exported backend entry operations.
- `mlxsw_sp_acl_atcam_rehash_hints_get()` and `put()` delegate rehash hint handling to ERP.

## Control Flow

Region initialization classifies the region by number of AFK key blocks: 2KB, 4KB, 8KB, or 12KB. It initializes A-TCAM entry tracking, large-key state if needed, ERP tables, and a C-TCAM region for fallback. Entry add first encodes key and mask with AFK, obtains or creates an ERP mask, computes any ERP delta bits, clears those delta bits from the encoded key, and inserts the entry into the A-TCAM entry hash. Duplicate hash keys or ERP/Bloom failures cause the entry to be removed from the A-TCAM tracking structures and then inserted into C-TCAM. Successful A-TCAM inserts update Bloom before writing `PTCE3`; deletes remove `PTCE3`, Bloom, hash/list entries, and ERP references. Action replacement writes either `PTCE3` update or C-TCAM `PTCE2` update depending on where the entry landed.

## State And Persistence

A-TCAM state is the software entry hash/list, ERP mask references, large-key-id references, and hardware `PTCE3` records. C-TCAM spill entries persist in the fallback `parman` region. ERP and Bloom state are shared with `spectrum_acl_erp.c` and `spectrum_acl_bloom_filter.c`. There is no disk persistence.

## Dependencies And Integration Points

The file depends on AFK key encoding, TCAM region metadata, `PTCE3`/`PERAR` register packers, C-TCAM helpers, ERP mask/delta/Bloom helpers, tracepoints, and core resource queries for large-key ids. It is selected through `mlxsw_sp_acl_tcam_ops` in chip-specific Spectrum code and used by the generic TCAM virtual region allocator.

## Risks

- A-TCAM cannot store identical effective keys; duplicate handling must reliably spill to C-TCAM.
- Bloom must be updated before `PTCE3` insertion and unwound on failure, or lookups can become false-negative-prone.
- Large-key-id reference counts affect the shared-key flag written to hardware; wrong counts can corrupt 12KB-region lookups.
- Delta computation mutates the encoded key by clearing bits; ordering around hash insertion and ERP reference management is fragile.
- Fallback to C-TCAM changes ordering and capacity behavior, so mixed A-TCAM/C-TCAM regions need stress testing.

## Test Signals

Exercise rules with identical keys, many distinct masks, 2/4/8/12-block key sizes, C-TCAM spill, action replacement for both A-TCAM and C-TCAM entries, region rehash, large-key-id exhaustion, and failure injection for ERP mask allocation, Bloom update, and `PTCE3` writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_atcam.c -->
