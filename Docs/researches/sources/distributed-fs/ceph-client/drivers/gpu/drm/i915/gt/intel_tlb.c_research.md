# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_tlb.c

## Purpose
`intel_tlb.c` implements full GT TLB invalidation for modern i915 platforms, using GuC invalidation where available or MMIO invalidation registers otherwise.

## Important APIs, Types, And Functions
Public functions are `intel_gt_invalidate_tlb_full()`, `intel_gt_init_tlb()`, and `intel_gt_fini_tlb()`. Internal helpers are `wait_for_invalidate()`, `mmio_invalidate_full()`, and `tlb_seqno_passed()`.

## Control Flow
Callers pass a seqno barrier. The public invalidation path skips mock or wedged GTs and already-passed barriers, then runs only if the GT is awake. Under `gt->tlb.invalidate_lock`, it rechecks the seqno, asks GuC to invalidate engines if supported and ready, otherwise writes invalidate requests to awake engines through per-engine MMIO or MCR registers, waits for done bits, applies an OA invalidation workaround on affected Gen12 platforms, and advances the seqcount barrier.

## State, Persistence, And Dependencies
Persistent GT state is `gt->tlb.invalidate_lock` plus the seqcount used as an invalidation barrier. Hardware state is per-engine TLB invalidate registers and optional OA TLB invalidation control. Dependencies include GT PM, forcewake, MCR locking, uncore lock serialization with reset, GuC readiness, engine PM awake checks, and wait helpers.

## Integration Points
VM invalidation callers use `intel_gt_next_invalidate_tlb_full()` from the header to request a future full invalidation and then call this function to satisfy it. GuC, engine PM, GT reset, and OA workarounds intersect in the invalidation path.

## Risks
Skipping sleeping engines is intentional but relies on power transitions flushing state as needed. Register writes must be serialized with GT reset. MCR versus non-MCR register selection is per engine. GuC not-ready during reset is treated as safe because reset clobbers TLBs.

## Test Signals
Selftests include `selftest_tlb.c`. Useful runtime signals include page-table update stress, GuC and non-GuC modes, reset races, Gen12 OA workaround platforms, MCR platforms, and timeout logs for engines that fail to clear done bits.
