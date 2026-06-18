# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc.h

### Purpose
`intel_guc.h` defines the top-level `struct intel_guc`, inline messaging helpers, status predicates, GuC GGTT validation, and public APIs used across i915 GuC firmware, submission, CT, SLPC, capture, TLB invalidation, and reset code.

### Important APIs, Types, And Functions
The central type is `struct intel_guc`, containing firmware/log/CT/SLPC/capture state, debugfs node, scheduler and stalled request state, IRQ/message state, submission ID allocators and workers, ADS pointers/sizes, LRC descriptor pool, context lookup, params, send registers, timestamp tracking, and selftest fields. Inline helpers include `intel_guc_send()`, `intel_guc_send_nb()`, `intel_guc_send_and_receive()`, `intel_guc_send_busy_loop()`, `intel_guc_to_host_event_handler()`, `intel_guc_ggtt_offset()`, status predicates, interrupt wrappers, sanitize, and message mask helpers.

### Control Flow
The header's inline send helpers route to CT send, optionally busy-looping on `-EBUSY` with sleep or `cpu_relax()` depending on context. Event handling only dispatches CT events when interrupts are enabled. `intel_guc_ggtt_offset()` asserts GuC-visible memory is above the pin bias and below `GUC_GGTT_TOP`. Sanitization resets firmware status, disables interrupts, sanitizes CT, and clears pending MMIO messages.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
The structure persists for the GT lifetime and is shared by many modules with explicit spinlocks, mutexes, work structs, atomics, and xarrays. Dependencies include GuC CT/log/fwif/reg/slpc types, VMA/GEM utilities, xarray/ida, and uncore APIs. Integration is broad: submission, HuC auth, reset recovery, TLB invalidation, ADS, engine usage accounting, debugfs, and G2H processing. Risks include lock-order mistakes, stale GuC ID/context state, busy-looping in atomic contexts, invalid GGTT placement, and inconsistent firmware status predicates. Test signals include compile coverage across GuC modules, CT send behavior, sanitize/resume paths, and assertions in GGTT offset helpers.
