# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum2_acl_tcam.c

## Purpose

`spectrum2_acl_tcam.c` implements the Spectrum-2-and-newer ACL TCAM backend using A-TCAM and ERP masks. It reserves KVDL action-set space for default region actions, initializes default continue actions in hardware, hooks C-TCAM mask insertion/removal to ERP mask references, delegates region/chunk/entry operations to shared A-TCAM helpers, supports action replacement, and reports activity via the stored AFA action block.

## Important APIs, Types, and Functions

The exported object is `mlxsw_sp2_acl_tcam_ops` with key type `MLXSW_REG_PTAR_KEY_TYPE_FLEX2`. Private types are `mlxsw_sp2_acl_tcam`, `mlxsw_sp2_acl_tcam_region`, `mlxsw_sp2_acl_tcam_chunk`, and `mlxsw_sp2_acl_tcam_entry`.

Initialization is handled by `mlxsw_sp2_acl_tcam_init()`. It allocates KVDL action-set entries, builds an uncommitted continue AFA block, writes default actions with `PEFA`, writes the base with `PGCR`, and initializes shared A-TCAM state. Entry add/delete/replace wrap `mlxsw_sp_acl_atcam_*()` helpers. Activity uses `mlxsw_afa_block_activity_get()` on the entry's current action block.

## Control Flow

During TCAM init the backend determines how many default action KVDL entries to reserve. It uses the generic TCAM max-region count unless the `ACL_MAX_DEFAULT_ACTIONS` resource is available. It allocates `ACTSET` KVDL entries, creates a continue action block, obtains the current encoded action set, writes one default action per exposed host region using `PEFA`, writes `PGCR` with the KVDL base, and initializes A-TCAM.

Region initialization stores the generic region pointer and calls `mlxsw_sp_acl_atcam_region_init()` with rehash hints and C-TCAM region ops. The C-TCAM entry insert hook obtains an ERP mask for the rule mask and stores it in the A-TCAM entry; the remove hook puts that ERP mask. Chunk and entry lifecycle are thin A-TCAM wrappers. Action replacement updates the stored action block pointer and delegates replacement to A-TCAM.

## State and Persistence Behavior

The backend owns a KVDL range for default TCAM actions over its lifetime. Region private state owns A-TCAM region state; entries own A-TCAM entry state and a pointer to the current AFA block used for activity reporting. ERP mask references are acquired per inserted C-TCAM entry and released on removal.

Hardware state includes KVDL action-set records, PGCR default action base, A-TCAM entries, and ERP mask programming performed by shared helpers. KVDL space is freed on TCAM finalization.

## Dependencies and Integration Points

This backend is used by Spectrum-2, Spectrum-3, and Spectrum-4 init paths. It depends on generic KVDL allocation, AFA action block creation/encoding/activity, A-TCAM/ERP helpers, `PEFA` and `PGCR` registers, and ACL resource discovery. Shared TC flower/matchall offload code reaches it through `mlxsw_sp_acl_tcam_ops`.

## Risks and Edge Cases

- The code may allocate more KVDL entries than host-exposed regions when `ACL_MAX_DEFAULT_ACTIONS` exceeds `_tcam->max_regions`; only exposed regions are initialized with `PEFA`, while hidden device regions are intentionally reserved.
- The continue AFA block is not committed; the code relies on `mlxsw_afa_block_cur_set()` encoding being valid for `PEFA`.
- Error unwinding must free KVDL after failures in AFA creation, PEFA writes, PGCR write, or A-TCAM init.
- Entry activity depends on `entry->act_block` being updated on add and action replacement; stale pointers would break stats/last-use reporting.
- ERP mask get/put balance is critical during rehash and entry removal.

## Test Signals

Test TCAM init/fini with and without `ACL_MAX_DEFAULT_ACTIONS`, PEFA/PGCR write failures, A-TCAM init failure unwind, rule add/delete with shared masks, rehash hint paths, action replacement, activity reporting after replacement, and KVDL leak checks under ACL rule churn.
