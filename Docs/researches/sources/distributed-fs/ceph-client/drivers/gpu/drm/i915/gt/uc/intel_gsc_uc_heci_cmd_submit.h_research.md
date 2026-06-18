# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_heci_cmd_submit.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_heci_cmd_submit.h

### Purpose
`intel_gsc_uc_heci_cmd_submit.h` declares GSC HECI packet submission APIs and the MTL GSC message header format.

### Important APIs, Types, And Functions
It defines `GSC_HECI_REPLY_LATENCY_MS`, `struct intel_gsc_mtl_header` with validity marker, client IDs, host-session flags, message size, flags, and status, plus `struct intel_gsc_heci_non_priv_pkt`. It declares packet submission, header emission, and nonprivileged submission helpers.

### Control Flow
The header has no executable flow; it documents the fields consumed by GSC firmware and submit code.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
State is caller-owned packet/header memory. Integration includes GSC firmware load queries, proxy, PXP, HDCP, and nonprivileged clients. Risks are duplicated prototype declaration, message-size upper-bit reservation, host-session bit misuse, and client ID drift. Test signals are correct GSC replies for each client and clean timeout behavior.
