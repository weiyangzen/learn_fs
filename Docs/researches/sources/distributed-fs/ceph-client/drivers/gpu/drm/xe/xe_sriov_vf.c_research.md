<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf.c

## Purpose

`xe_sriov_vf.c` implements VF-side SR-IOV initialization, migration capability gating, migration-disable logging, and VF debugfs registration. It also contains the design documentation for VF restore and post-migration resource fixups.

## Important APIs, Types, and Functions

`xe_sriov_vf_migration_supported()` reports the inverse of the VF migration disabled flag. `xe_sriov_vf_migration_disable()` logs a formatted reason and permanently disables migration support for the VF. `xe_sriov_vf_init_early()` rejects migration when memory-based IRQs are missing. `xe_sriov_vf_init_late()` requires GuC ABI 1.27.0 or newer and initializes CCS support through `xe_sriov_vf_ccs_init()`. `xe_sriov_vf_debugfs_register()` registers `sa_info_vf_ccs`.

## Control Flow

Early init checks hardware prerequisites. Late init skips work if migration has already been disabled, reads GuC versions from the root MMIO GT, disables migration on too-old firmware, and otherwise initializes VF CCS save/restore helpers. Debugfs printing delegates to CCS printing.

## State and Persistence Behavior

The migration disabled flag lives in `xe->sriov.vf.migration.disabled`. Once set, later checks return unsupported and late CCS initialization is skipped. CCS initialization persists in `xe->sriov.vf.ccs`.

## Dependencies and Integration Points

The file integrates VF GT GuC version queries, memory IRQ capability, CCS migration code, SR-IOV logging, DRM debugfs, and DRM managed cleanup from CCS setup. The documented restore flow ties PF VFIO migration, GuC VF states, and VF post-migration recovery together.

## Risks and Test Signals

Risks include silent migration disable on missing prerequisites, dependency on exact GuC ABI thresholds, and debugfs output being empty when CCS is not initialized. Tests should cover memirq absence, GuC ABI below/above threshold, repeated disable calls, late init success/failure, and debugfs registration on VF devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf.c -->
