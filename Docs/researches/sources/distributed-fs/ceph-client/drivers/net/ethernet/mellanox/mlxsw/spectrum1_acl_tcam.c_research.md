# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum1_acl_tcam.c

## Purpose

`spectrum1_acl_tcam.c` implements the Spectrum-1 ACL TCAM backend. It adapts shared ACL TCAM code to the older C-TCAM model, installs a per-region catchall continue rule, exposes region/chunk/entry private storage sizes, adds and deletes entries through common C-TCAM helpers, and reads rule activity through the `PTCE2` register.

## Important APIs, Types, and Functions

The exported object is `mlxsw_sp1_acl_tcam_ops`. Its key type is `MLXSW_REG_PTAR_KEY_TYPE_FLEX`, `priv_size` is zero, and its callbacks are backed by local wrappers.

Local private types are `mlxsw_sp1_acl_tcam_region`, `mlxsw_sp1_acl_tcam_chunk`, and `mlxsw_sp1_acl_tcam_entry`. The region embeds `struct mlxsw_sp_acl_ctcam_region`, stores the generic region pointer, and owns a catchall chunk, entry, and rule info pointer.

Important helpers include `mlxsw_sp1_acl_ctcam_region_catchall_add()`, `mlxsw_sp1_acl_ctcam_region_catchall_del()`, `mlxsw_sp1_acl_tcam_region_init()`, `mlxsw_sp1_acl_tcam_entry_add()`, `mlxsw_sp1_acl_tcam_entry_del()`, and `mlxsw_sp1_acl_tcam_entry_activity_get()`.

## Control Flow

TCAM initialization itself is a no-op for Spectrum-1. Region initialization initializes the embedded C-TCAM region, creates a catchall chunk at `MLXSW_SP_ACL_TCAM_CATCHALL_PRIO`, creates an ACL rule info object, adds a continue action, commits it, and inserts it into the C-TCAM region. On failure it destroys the rule info and finalizes the catchall chunk before finalizing the C-TCAM region.

Normal chunks simply wrap `mlxsw_sp_acl_ctcam_chunk_init()` and `mlxsw_sp_acl_ctcam_chunk_fini()`. Entry add wraps `mlxsw_sp_acl_ctcam_entry_add()` with `fillup_priority=false`; entry delete calls the matching C-TCAM delete helper. Action replacement returns `-EOPNOTSUPP`, so callers must delete/re-add or avoid replacement on this backend.

Activity reads derive the C-TCAM entry offset, pack a `PTCE2` query with clear-on-read operation, query hardware, and return the activity bit.

## State and Persistence Behavior

State is per ACL region/chunk/entry and lives in the private objects allocated by shared ACL code according to the sizes in `mlxsw_sp1_acl_tcam_ops`. The catchall rule is persistent hardware TCAM state for each region until region finalization. Activity reads are clear-on-read, so querying activity mutates hardware activity state.

## Dependencies and Integration Points

The backend depends on shared ACL TCAM helpers in `spectrum_acl_tcam.h`, ACL rule info creation/action/commit helpers from the ACL core, and register access to `PTCE2`. It is selected by `mlxsw_sp1_init()` in `spectrum.c` and used by shared ACL ruleset/rule code.

## Risks and Edge Cases

- Catchall rule creation has multiple failure labels; leaks or double-finalization here would affect every ACL region.
- `entry_action_replace` is unsupported. TC offload paths must handle `-EOPNOTSUPP` gracefully for rule action changes.
- Activity query clears the activity bit, so polling frequency changes user-visible `last_used` behavior.
- Region association is a no-op; shared code must not expect a hardware association step on Spectrum-1.
- The C-TCAM region entry insert/remove hooks are empty by design, unlike Spectrum-2 where mask/ERP state is allocated.

## Test Signals

Exercise TC flower rule add/delete on Spectrum-1, region creation/destruction with an empty ruleset, catchall continue behavior, activity polling, action replacement failure handling, and error injection for rule info allocation, commit, and C-TCAM entry add.
