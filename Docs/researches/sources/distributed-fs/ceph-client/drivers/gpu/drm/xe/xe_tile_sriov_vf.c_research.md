<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_vf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_vf.c

## Purpose

`xe_tile_sriov_vf.c` stores and retrieves VF self-configuration for tile-local LMEM and GGTT assignment, including GGTT base needed after migration.

## Important APIs, Types, and Functions

The public getters/setters are `xe_tile_sriov_vf_lmem()`, `xe_tile_sriov_vf_lmem_store()`, `xe_tile_sriov_vf_ggtt()`, `xe_tile_sriov_vf_ggtt_store()`, `xe_tile_sriov_vf_ggtt_base()`, and `xe_tile_sriov_vf_ggtt_base_store()`.

## Control Flow

VF provisioning queries from GuC or PF/VF relay update the self config through store functions. Consumers read these values for GGTT sizing, LMEM sizing, and post-migration GGTT node rebasing.

## State and Persistence Behavior

Values persist in `tile->sriov.vf.self_config`. `ggtt_base` uses `READ_ONCE`/`WRITE_ONCE`, reflecting that it can be observed across recovery paths without heavier locking.

## Dependencies and Integration Points

The file integrates tile assertions, SR-IOV mode checks, GGTT/WOPCM layout concepts, and VF post-migration recovery. It includes GTT definitions and WOPCM headers for the documented GGTT layout context.

## Risks and Test Signals

Risks include stale GGTT base after migration, assuming identical total GGTT layout across source/destination, and using these helpers outside VF mode. Tests should cover store/get round trips, concurrent GGTT base reads, migration rebase flows, and VF-mode assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_vf.c -->
