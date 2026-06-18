<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_service_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_service_types.h

## Purpose

`xe_sriov_pf_service_types.h` defines persistent PF service ABI version state.

## Important APIs, Types, and Functions

`struct xe_sriov_pf_service_version` contains `major` and `minor`. `struct xe_sriov_pf_service` contains `version.base` and `version.latest`, representing the lowest and newest VF/PF ABI the PF can negotiate.

## Control Flow

These types are written during PF service init and read during handshakes and diagnostics. Per-VF metadata reuses `xe_sriov_pf_service_version` to record each VF's selected ABI.

## State and Persistence Behavior

The data persists in `struct xe_device_pf` for the PF lifetime. A zero per-VF version means disconnected or not negotiated.

## Dependencies and Integration Points

The type header depends on Linux integer types. It is embedded by `xe_sriov_pf_types.h` and consumed by PF service code and per-VF metadata.

## Risks and Test Signals

Width changes could affect ABI display and storage. Tests should verify initialization stores expected GuC relay constants and reset clears per-VF version fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_service_types.h -->
