<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_erp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_erp.c

## Purpose

`spectrum_acl_erp.c` manages eRP masks and eRP tables for A-TCAM regions. It aggregates compatible masks through `objagg`, programs region master masks and eRP table entries, coordinates Bloom filter updates, handles C-TCAM lookup enablement, and provides rehash hints that allow the TCAM layer to rebuild regions with fewer roots.

## Important APIs, Types, And Functions

- `struct mlxsw_sp_acl_erp_core` owns per-region-type entry sizes, a `gen_pool` for eRP table rows, the Bloom filter, ERP-bank count, and device pointer.
- `struct mlxsw_sp_acl_erp_table` owns master mask accounting, ERP id/index bitmaps, A-TCAM ERP list, objagg, counters, and region linkage.
- `mlxsw_sp_acl_erp_mask_get()` / `put()` expose mask references as `struct mlxsw_sp_acl_erp_mask`.
- `mlxsw_sp_acl_erp_delta_*()` exposes delta start/mask/value/clear helpers used by A-TCAM key encoding.
- `mlxsw_sp_acl_erp_bf_insert()` and `remove()` update Bloom bits for table-backed ERP roots.
- `mlxsw_sp_acl_erp_region_init()` and `fini()` create/destroy per-region ERP state.
- `mlxsw_sp_acl_erp_rehash_hints_get()` / `put()` create objagg hints for TCAM rehash.
- `mlxsw_sp_acl_erps_init()` and `fini()` own global ERP resources.

## Control Flow

Global init queries ERP bank resources, creates a best-fit `gen_pool`, initializes Bloom, and stores hardware entry sizes for 2/4/8/12KB region types. Region init creates an objagg table, initializes the hardware master mask to zero with `PERCR`, and disables table lookup with `PERERP`. Mask acquisition asks objagg for a root or delta. The first A-TCAM mask uses only the master mask. A second mask transitions the region to an eRP table: it allocates table rows, writes the existing root to `PERPT`, populates Bloom for existing entries, and enables `PERERP`. Additional masks expand the table by bank-sized rows when needed and program new roots and vectors. C-TCAM masks increment C-TCAM counters, set master mask bits, and enable C-TCAM lookup through `PERERP`.

Deltas are permitted only when two masks differ by up to eight consecutive bits that are set in the child but not the parent. Delta create increments delta counters, updates the master mask, and stores the bit location so A-TCAM can clear those key bits and send the delta field in `PTCE3`. Rehash hints are generated with `OBJAGG_OPT_ALGO_SIMPLE_GREEDY`; if hint root count is lower than current root count, the TCAM layer can rebuild the region using those hints.

## State And Persistence

Software state includes gen-pool allocations, ERP ids, ERP indexes, root/delta objagg objects, master-mask per-bit reference counts, C-TCAM/delta counters, and Bloom references. Hardware state includes `PERCR` master masks, `PERPT` table rows, `PERERP` enable/vector state, and Bloom entries. It is persistent only for the driver/device lifetime.

## Dependencies And Integration Points

ERP is called by A-TCAM region initialization and entry add/delete, C-TCAM spill paths, Bloom filter code, and TCAM rehash. It depends on Linux `objagg`, `genalloc`, bitmaps, `rtnl`-safe driver context, Spectrum resource IDs for ERP/Bloom sizing, and `PERCR`/`PERPT`/`PERERP` register packers.

## Risks

- State transitions between no mask, master-mask-only, two masks, multiple masks, C-TCAM lookup, and deltas are intricate and require exact counter balance.
- Bloom updates during table transition must be ordered before enabling table lookup.
- `gen_pool_alloc()` uses an artificial offset because zero means failure; mistakes around the offset corrupt table indexes.
- Delta compatibility is intentionally narrow; unexpected mask shapes increase root count and can force rehash or spill.
- Error unwinds during table expansion/transition must restore old base indexes and bitmaps correctly.

## Test Signals

Test first/second/many mask insertion, C-TCAM masks, delta-compatible and incompatible masks, ERP table expansion to `MLXSW_SP_ACL_ERP_MAX_PER_REGION`, Bloom updates during transitions, rehash hints and region migration, resource exhaustion, and register write failure unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_erp.c -->
