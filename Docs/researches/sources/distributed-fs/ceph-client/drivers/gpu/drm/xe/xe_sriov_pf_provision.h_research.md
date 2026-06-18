<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_provision.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_provision.h

## Purpose

`xe_sriov_pf_provision.h` is the PF provisioning public interface. It exports the functions used by PF setup, sysfs, debugfs, and VF lifecycle code to allocate or query SR-IOV resources.

## Important APIs, Types, and Functions

The header declares bulk and per-VF operations for execution quantum (`eq`), preemption timeout (`pt`), scheduling priority, and VRAM quota. It also exposes `xe_sriov_pf_provision_vfs()`, `xe_sriov_pf_unprovision_vfs()`, and `xe_sriov_pf_provision_set_mode()`. The inline `xe_sriov_pf_provision_set_custom_mode()` is a convenience wrapper for callers that should preserve manual allocations.

## Control Flow

Callers parse user or policy input, then call these APIs rather than touching GT config directly. Bulk APIs affect all VFs and, where supported, PF policy. Per-VF APIs use 1-based VF identifiers with `PFID` equal to zero where the implementation allows PF priority handling.

## State and Persistence Behavior

The header does not own state, but it exposes operations that mutate persistent PF provisioning mode and backend GT/tile resource configuration. The included `xe_sriov_pf_provision_types.h` makes the mode enum part of the public contract.

## Dependencies and Integration Points

It depends on Linux integer types and the provisioning types header. Integration points include `xe_sriov_pf_sysfs.c`, `xe_tile_sriov_pf_debugfs.c`, PF SR-IOV enable/disable control, and tests of GT provisioning policy.

## Risks and Test Signals

The API relies on callers to pass a PF device and valid VF IDs; most validation is in implementation asserts. Compile tests should catch signature drift, and behavioral tests should verify all declared operations remain wired to sysfs/debugfs consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_provision.h -->
