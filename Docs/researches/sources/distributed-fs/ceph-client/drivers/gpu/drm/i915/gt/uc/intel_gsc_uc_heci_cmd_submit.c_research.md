# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_heci_cmd_submit.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_heci_cmd_submit.c

### Purpose
`intel_gsc_uc_heci_cmd_submit.c` emits GSC HECI command packets through the GSC command streamer for privileged and non-privileged clients, and builds MTL GSC message headers.

### Important APIs, Types, And Functions
Exports are `intel_gsc_uc_heci_cmd_submit_packet()`, `intel_gsc_uc_heci_cmd_emit_mtl_header()`, and `intel_gsc_uc_heci_cmd_submit_nonpriv()`. Internal helpers include `struct gsc_heci_pkt`, `emit_gsc_heci_pkt()`, and `emit_gsc_heci_pkt_nonpriv()`.

### Control Flow
Privileged submission creates a request on `gsc->ce`, optionally emits an init breadcrumb, emits `GSC_HECI_CMD_PKT` with input/output GGTT addresses and sizes, flushes, submits, waits for request start and then completion, and returns `-ETIME` on timeout. Header emission fills validity marker, client ID, host session bits, version, size, and PXP single-session marking. Nonpriv submission locks batch and packet VMAs under ww context, pins the supplied context, writes a batch with HECI packet plus batch end, marks VMAs active, emits BB start and flush, waits interruptibly, and backs off on `-EDEADLK` up to ten trials.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
State is transient request/batch state plus caller-owned packet VMAs. Dependencies include GSC engine contexts, GEM ww locking, VMA active tracking, ring command emission, request waits, and GSC header protocol. Integration points are GSC firmware compatibility queries, proxy exchange, PXP/HDCP-style clients, and nonprivileged command submission paths. Risks include timeout semantics, request not starting due to GuC arbitration, unbalanced context pinning, ww retry exhaustion, invalid packet buffer sizes, and duplicated header declaration in the header. Test signals are successful MKHI/proxy/PXP replies, timeout logs, and nonprivileged path error propagation.
