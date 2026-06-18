<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_types.h

## Purpose

`xe_sriov_types.h` defines the common SR-IOV mode and function-ID constants shared by PF and VF code.

## Important APIs, Types, and Functions

`VFID(n)` represents the 1-based PCI VF identifier convention, and `PFID` aliases `VFID(0)`. `enum xe_sriov_mode` distinguishes bare-metal, PF, and VF modes, intentionally starting `XE_SRIOV_MODE_NONE` at one to catch premature zero-initialized checks.

## Control Flow

Mode probes set `xe->sriov.__mode` to one of these enum values. Helpers and logging macros then branch on PF versus VF mode. VFID/PFID values index PF metadata and drive sysfs/debugfs naming.

## State and Persistence Behavior

The header owns no state, but its constants define how persistent SR-IOV mode and per-VF arrays are interpreted.

## Dependencies and Integration Points

It only depends on build assertions. It is included broadly by PF, VF, logging, and tile SR-IOV code.

## Risks and Test Signals

Changing enum or ID values would break array indexing and mode checks. Tests should include early mode-probe behavior and boundary checks around VFID zero versus real VFs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_types.h -->
