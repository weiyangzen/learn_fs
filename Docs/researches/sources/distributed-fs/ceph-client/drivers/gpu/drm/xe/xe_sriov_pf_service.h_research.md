<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_service.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_service.h

## Purpose

`xe_sriov_pf_service.h` exposes the PF service ABI negotiation API.

## Important APIs, Types, and Functions

The declarations cover service initialization, version printing, VF handshake, negotiated-version checks, and VF reset. The interface uses `u32` requested/selected major and minor values while persistent storage uses the service type struct's `u16` fields.

## Control Flow

PF initialization calls `xe_sriov_pf_service_init()` before any VF handshakes. Relay handling calls `xe_sriov_pf_service_handshake_vf()` when a VF connects, and feature handlers can call `xe_sriov_pf_service_is_negotiated()` to gate newer functionality. VF reset paths call `xe_sriov_pf_service_reset_vf()`.

## State and Persistence Behavior

No state is stored here; it is a stable contract over `xe->sriov.pf.service` and `xe->sriov.pf.vfs[].version`.

## Dependencies and Integration Points

It depends only on Linux types and forward declarations. Integration points include PF relay message handling, debugfs printing, and KUnit coverage in the implementation.

## Risks and Test Signals

Callers must pass PF devices and valid VF IDs. Build coverage should catch ABI signature drift, while handshake tests should verify the header remains synchronized with implementation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_service.h -->
