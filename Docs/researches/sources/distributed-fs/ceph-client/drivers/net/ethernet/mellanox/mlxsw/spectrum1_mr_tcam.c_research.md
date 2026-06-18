# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum1_mr_tcam.c

## Purpose

`spectrum1_mr_tcam.c` implements Spectrum-1 multicast routing TCAM operations. It maintains separate IPv4 and IPv6 multicast TCAM regions, uses `parman` to place routes by priority while supporting resize and move operations, and programs route entries through `RMFT2`, region allocation/resizing through `RTAR`, and TCAM moves through `RRCR`.

## Important APIs, Types, and Functions

The exported operation table is `mlxsw_sp1_mr_tcam_ops`. It provides private sizes, `init`, `fini`, `route_create`, `route_destroy`, and `route_update`.

`struct mlxsw_sp1_mr_tcam_region` stores the owning `mlxsw_sp`, RTAR key type, parman instance, and priority array. `struct mlxsw_sp1_mr_tcam` stores one region per L3 protocol. `struct mlxsw_sp1_mr_tcam_route` stores the parman item and selected parman priority.

Route programming helpers are `mlxsw_sp1_mr_tcam_route_replace()` and `mlxsw_sp1_mr_tcam_route_remove()`. Region helpers allocate/deallocate/resize hardware regions and move TCAM ranges. `mlxsw_sp1_mr_tcam_region_parman_ops` configures base count 16, resize step 16, and `PARMAN_ALGO_TYPE_LSORT`.

## Control Flow

Initialization first requires `ACL_MAX_TCAM_RULES`, then allocates an IPv4 multicast region and an IPv6 multicast region using `RTAR`. Each region creates a parman instance and initializes priority objects for all multicast route priorities.

Route creation adds a parman item to the protocol-specific region and priority. Parman assigns an index and may call resize/move callbacks. The route is then written to `RMFT2` with group/source addresses and masks plus the first action set from the AFA block. On write failure the parman item is removed. Destroy removes the hardware route and removes the parman item. Update rewrites the existing index with a new action block.

Finalization destroys IPv6 then IPv4 regions, finalizing priorities, destroying parman, and deallocating hardware regions.

## State and Persistence Behavior

In-memory state consists of per-protocol parman placement state and one private route object per multicast route. Hardware state includes allocated RTAR regions, RMFT2 route records, and RRCR moves performed during parman compaction/resizing. Route indexes are stable only through the parman item and may change when moves occur.

## Dependencies and Integration Points

This backend is selected by Spectrum-1 init and called by shared multicast routing code in `spectrum_mr.c`. It depends on Linux `parman`, register helpers from `reg.h`, AFA action blocks, L3 protocol and multicast route key definitions from `spectrum.h` / `spectrum_mr.h`, and the `ACL_MAX_TCAM_RULES` resource.

## Risks and Edge Cases

- The IPv4/IPv6 switch statements have no default branch; callers must provide only supported protocols.
- Region resize is limited by global `ACL_MAX_TCAM_RULES`, so multicast route scaling competes conceptually with ACL TCAM capacity.
- `mlxsw_sp1_mr_tcam_region_free()` and parman move callbacks ignore write failures, which can hide teardown or compaction hardware errors.
- Route destroy removes hardware before parman state; a failed remove write is ignored by the void destroy path.
- Priority ordering depends on parman and the enum order in `mlxsw_sp_mr_route_prio`.

## Test Signals

Test IPv4 and IPv6 multicast route add/update/delete, all priorities including catchall, route counts crossing 16-entry resize boundaries, forced parman moves, exhaustion beyond `ACL_MAX_TCAM_RULES`, AFA block changes, and failure injection for RTAR, RMFT2, RRCR, parman allocation, and priority allocation.
