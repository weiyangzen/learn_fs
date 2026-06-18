<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_lrc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_lrc.h

Purpose: declares the logical-ring-context API, context-image layout constants, descriptor bit definitions, runtime helpers, and DG2 predicate workaround offsets.

Important APIs and types: `LRC_PPHWSP_*`, `LRC_STATE_OFFSET`, and scratch offsets define context image layout. Lifecycle functions include `lrc_alloc`, `lrc_pre_pin`, `lrc_pin`, `lrc_unpin`, `lrc_post_unpin`, `lrc_fini`, and `lrc_destroy`. State programming functions include `lrc_init_state`, `lrc_init_regs`, `lrc_reset_regs`, `lrc_update_regs`, `lrc_update_offsets`, and `lrc_check_regs`. Runtime helpers `lrc_runtime_start()` and `lrc_runtime_stop()` update `intel_context_stats`. Enums and defines encode context addressing modes, fault behaviors, descriptor validity/privilege/priority bits, SW context ID fields, and DG2 predicate workaround slots.

Control flow: engine context code calls the allocation/pin/update functions during context creation and submission. Runtime start/stop guard barrier contexts, avoid nested activation, sample context timestamps, and clear the active marker.

State and persistence: constants describe persistent hardware context image offsets. The inline runtime helpers update per-context software runtime totals, active timestamp, and EWMA through `lrc_update_runtime()`.

Dependencies and integration points: includes `intel_context.h`, priority list types, bitfield helpers, and Linux integer types. Integrated by engine context ops, request submission, reset, and runtime accounting.

Risks: descriptor bit constants are hardware ABI. `LRC_STATE_OFFSET` assumes the PPHWSP is exactly one page; changing it breaks context image access. Runtime helpers rely on callers pairing start/stop around actual execution.

Test signals: build coverage, LRC selftests, runtime accounting tests, context descriptor validation, and Gen12 priority/fault-mode submission tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_lrc.h -->
