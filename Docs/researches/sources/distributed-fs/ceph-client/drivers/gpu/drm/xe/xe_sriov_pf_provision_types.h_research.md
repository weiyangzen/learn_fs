<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_provision_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_provision_types.h

## Purpose

`xe_sriov_pf_provision_types.h` defines the small persistent type surface for PF provisioning mode.

## Important APIs, Types, and Functions

`enum xe_sriov_provisioning_mode` has `XE_SRIOV_PROVISIONING_MODE_AUTO` and `XE_SRIOV_PROVISIONING_MODE_CUSTOM`; a static assertion guarantees auto remains zero. `struct xe_sriov_pf_provision` stores the selected mode.

## Control Flow

The mode drives `xe_sriov_pf_provision_vfs()` and unprovisioning behavior. Auto mode lets VF enable/disable implicitly allocate and release resources. Custom mode makes allocations explicit through uABI/sysfs/debugfs paths and preserves them across VF disable.

## State and Persistence Behavior

`struct xe_device_pf` embeds `struct xe_sriov_pf_provision`, so the mode persists for the PF device lifetime. There is no serialization in this header; users must rely on PF provisioning functions for coordinated changes.

## Dependencies and Integration Points

The header only needs `linux/build_bug.h`. It is included by PF provisioning, PF type definitions, and the provisioning API header.

## Risks and Test Signals

Changing enum values would alter default mode and break assumptions in initialization. Tests should verify newly initialized PF state defaults to auto and that user-visible mode transitions preserve the semantics documented here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_provision_types.h -->
