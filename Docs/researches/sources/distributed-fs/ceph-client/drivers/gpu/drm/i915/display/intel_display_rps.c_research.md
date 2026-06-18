# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_rps.c

## Purpose
This file connects display activity to render power-state/RPS behavior. It can request an RPS boost after the next vblank when a fence is still not started, mark atomic commits as interactive, and wire Ironlake-era display PCU events into the parent RPS handler.

## Important APIs, Types, and Functions
`struct wait_rps_boost` stores a vblank wait entry, target CRTC, and fence. `intel_display_rps_boost_after_vblank()` registers a waitqueue callback for the CRTC vblank. `do_rps_boost()` performs the actual boost through `intel_parent_rps_boost_if_not_started()`, releases fence/vblank references, removes the wait entry, and frees it. `intel_display_rps_mark_interactive()` forwards interactivity changes to the parent. `ilk_display_rps_enable()`, `ilk_display_rps_disable()`, and `ilk_display_rps_irq_handler()` manage `DE_PCU_EVENT`.

## Control Flow
Boost registration first checks parent RPS availability, display generation, and vblank reference acquisition. If allocation succeeds it holds a fence reference and queues a wait entry on the CRTC vblank waitqueue. At vblank, the callback boosts only if the request has not started, then tears down all references. Interactive marking avoids duplicate parent calls by comparing `state->rps_interactive`.

## State and Persistence Behavior
Transient state is held in the allocated `wait_rps_boost` until the next vblank callback. The atomic state records whether the current commit has already marked RPS interactive. IRQ enable/disable state is in display interrupt masks guarded by `display->irq.lock`.

## Dependencies and Integration Points
Dependencies include DMA fences, DRM vblank, display IRQ helpers, `intel_parent` RPS callbacks, `intel_display_regs.h`, and display atomic state. Integration points are page-flip/commit code, vblank waitqueues, and ILK display interrupt setup.

## Risks
The callback must always drop the fence and vblank references or it leaks resources. If vblank is disabled or unavailable, boosting is skipped. Races around fence start/completion are intentionally handled by the parent `boost_if_not_started` predicate. IRQ enable/disable must hold `display->irq.lock` to avoid corrupting display interrupt state.

## Test Signals
Signals include interactive workload latency, fence boost behavior across missed vblanks, no vblank ref leaks, no waitqueue use-after-free, correct ILK PCU event handling, and power/performance tests showing RPS transitions during display-driven work.
