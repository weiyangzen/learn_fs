<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_types.h

## Purpose

`xe_sriov_vf_types.h` defines VF-mode persistent SR-IOV state embedded in `struct xe_device`.

## Important APIs, Types, and Functions

`struct xe_sriov_vf_relay_version` stores negotiated PF ABI major/minor. `struct xe_device_vf` stores `pf_version`, migration disabled state, and `struct xe_sriov_vf_ccs` CCS state.

## Control Flow

VF initialization fills or updates this state as the VF negotiates with the PF, checks migration prerequisites, and initializes CCS save/restore support.

## State and Persistence Behavior

All fields persist for the VF device lifetime. `migration.disabled` is sticky once prerequisites fail. `ccs.initialized` marks available CCS resources.

## Dependencies and Integration Points

The header includes workqueue types and CCS type definitions. It is the VF half of the SR-IOV union in device state and is consumed by VF init, relay, migration, and CCS code.

## Risks and Test Signals

Callers must only interpret this structure in VF mode. Tests should cover default zero initialization, PF version negotiation storage, migration disable persistence, and CCS state cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_types.h -->
