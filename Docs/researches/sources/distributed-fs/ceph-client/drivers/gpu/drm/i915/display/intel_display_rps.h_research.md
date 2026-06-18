# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_rps.h

## Purpose
This header declares the display-to-RPS integration API for vblank-delayed boosting, interactive commit marking, and Ironlake display RPS interrupt control.

## Important APIs, Types, and Functions
The declared APIs are `intel_display_rps_boost_after_vblank(struct drm_crtc *, struct dma_fence *)`, `intel_display_rps_mark_interactive(struct intel_display *, struct intel_atomic_state *, bool)`, `ilk_display_rps_enable()`, `ilk_display_rps_disable()`, and `ilk_display_rps_irq_handler()`.

## Control Flow
The header has no control flow. It defines the contract that callers can ask display RPS code to defer boost decisions until vblank and to reflect commit interactivity into parent RPS state.

## State and Persistence Behavior
No state is stored here. Callers pass the atomic state that records interactivity and, for boost, the fence whose lifetime is managed by the implementation.

## Dependencies and Integration Points
It forward-declares `struct dma_fence`, `struct drm_crtc`, `struct intel_atomic_state`, and `struct intel_display`, allowing display commit and IRQ code to include it with minimal dependencies.

## Risks
The API implies the fence pointer must remain valid for `dma_fence_get()`, and callers must only use the ILK IRQ helpers on hardware paths that expose `DE_PCU_EVENT`.

## Test Signals
Build integration across display commit and IRQ code, plus runtime validation of RPS boosting and ILK PCU interrupt handling.
