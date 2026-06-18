<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_ctcam.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_ctcam.c

## Purpose

`spectrum_acl_ctcam.c` implements conventional TCAM entry placement for ACL regions. It uses `parman` to maintain priority-ordered entries, resizes/moves hardware regions as needed, writes `PTCE2` entries, and supports action replacement.

## Important APIs, Types, And Functions

- `mlxsw_sp_acl_ctcam_region_init()` and `fini()` create/destroy a `parman` instance for a TCAM region.
- `mlxsw_sp_acl_ctcam_chunk_init()` and `fini()` map logical priority chunks to `parman_prio`.
- `mlxsw_sp_acl_ctcam_entry_add()` and `entry_del()` add/remove `parman_item`s and write/remove hardware entries.
- `mlxsw_sp_acl_ctcam_entry_action_replace()` updates the first action set in-place.
- `mlxsw_sp_acl_ctcam_region_resize()` writes `PTAR` resize operations.
- `mlxsw_sp_acl_ctcam_region_move()` writes `PRCR` moves.

## Control Flow

Region initialization creates a `parman` object with base count 16, resize step 16, LSORT ordering, and callbacks that resize `PTAR` regions or move `PRCR` ranges. Entry add first obtains a priority-ordered index from `parman_item_add()`, encodes key and mask with AFK into a `PTCE2` payload, lets backend ops observe/insert the mask, copies the first AFA action set into the entry, and writes the entry. If the write fails it removes backend state and the parman item. Delete disables the `PTCE2` entry, calls backend remove, and removes the parman item.

## State And Persistence

Software state lives in the `parman` object, priority chunks, and per-entry item indexes. Hardware state lives in resized TCAM region allocation, moved entries, and `PTCE2` records. The file itself does not persist state across driver lifetime.

## Dependencies And Integration Points

The module is used directly as the C-TCAM backend and as the spill/fallback path for A-TCAM. It depends on AFK encoding, AFA first action sets, TCAM region metadata from `spectrum_acl_tcam.h`, `parman`, resource `ACL_MAX_TCAM_RULES`, and `PTAR`/`PRCR`/`PTCE2` register packers.

## Risks

- `parman` and hardware movement must stay synchronized; a failed or ignored `PRCR` write can desynchronize software indexes from hardware entries.
- Region resizing is bounded by `ACL_MAX_TCAM_RULES`, but exhaustion propagates as insertion failures.
- The action replacement helper passes `rulei->priority` directly as hardware priority, unlike initial insertion which may invert/fill priority through `mlxsw_sp_acl_tcam_priority_get()`.
- Backend mask insert/remove callbacks must be balanced on all error paths.

## Test Signals

Exercise insert/delete at many priorities, region growth and movement, maximum TCAM rule capacity, C-TCAM spill from A-TCAM, action replacement, failure of `PTCE2` writes, and mixed chunk priority ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_ctcam.c -->
