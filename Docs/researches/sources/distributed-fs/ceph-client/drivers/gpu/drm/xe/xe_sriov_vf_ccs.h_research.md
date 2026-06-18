<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_ccs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_ccs.h

## Purpose

`xe_sriov_vf_ccs.h` declares the VF CCS migration API and readiness helper.

## Important APIs, Types, and Functions

The header exposes CCS init, BO attach/detach, GuC context registration, GGTT rebase, debug printing, and LRC batch-buffer address update. `xe_sriov_vf_ccs_ready()` asserts VF mode and returns `xe->sriov.vf.ccs.initialized`. `IS_VF_CCS_READY()` combines SR-IOV VF mode and readiness.

## Control Flow

Callers use `IS_VF_CCS_READY()` to skip CCS operations on unsupported configurations. Runtime resume re-registers contexts, GGTT rebase updates rings, and BO paths attach/detach CCS copy command buffers.

## State and Persistence Behavior

The header accesses persistent VF CCS state embedded in `struct xe_device_vf`.

## Dependencies and Integration Points

It includes Xe device and SR-IOV headers plus CCS types. Integration points include BO code, migration code, VF init, runtime PM resume, and debugfs.

## Risks and Test Signals

Readiness checks must not be bypassed. Compile tests should cover all call sites under SR-IOV/VF and non-ready configurations; runtime tests should verify no CCS operation runs when `initialized` is false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_ccs.h -->
