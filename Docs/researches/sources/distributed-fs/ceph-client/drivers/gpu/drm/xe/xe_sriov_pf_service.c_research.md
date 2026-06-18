<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_service.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_service.c

## Purpose

`xe_sriov_pf_service.c` implements PF-side negotiation of the VF/PF GuC relay ABI version. It records the PF's base/latest supported versions and tracks the negotiated ABI for each VF.

## Important APIs, Types, and Functions

`xe_sriov_pf_service_init()` initializes base and latest ABI versions from `guc_relay_actions_abi.h`. `xe_sriov_pf_service_handshake_vf()` negotiates a VF-requested version, stores it with `pf_connect()`, or clears it with `pf_disconnect()`. `xe_sriov_pf_service_is_negotiated()` checks whether a VF can use a feature requiring a specific ABI. `xe_sriov_pf_service_reset_vf()` clears per-VF negotiation state. `xe_sriov_pf_service_print_versions()` emits base/latest and per-VF negotiated versions.

## Control Flow

During PF service initialization, compile-time checks ensure a nonzero base ABI and sane major ordering. On handshake, a VF may request "any" and receive latest, request a newer major and receive the PF latest, request an older-than-base version and get `-EPERM`, or request the same major and receive the lower common minor. Previous major support is currently rejected with `-ENOPKG` unless the driver grows true multi-version support.

## State and Persistence Behavior

PF-wide base/latest versions live in `xe->sriov.pf.service.version`. Per-VF negotiated versions live in `xe->sriov.pf.vfs[vfid].version` and remain until reset, failed negotiation, VF reset, or PF teardown.

## Dependencies and Integration Points

The file integrates with GuC relay ABI constants, SR-IOV PF helper validation, debug printing, and debugfs/service diagnostics. It includes the KUnit service test when built with Xe KUnit support.

## Risks and Test Signals

The major-version path is intentionally not multi-version capable and asserts if base/latest majors diverge. Tests should cover `ANY`, newer-than-latest, older-than-base, same-major minor clamping, reset behavior, and printed version output. Consumers should check `xe_sriov_pf_service_is_negotiated()` before using ABI-gated relay features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_service.c -->
