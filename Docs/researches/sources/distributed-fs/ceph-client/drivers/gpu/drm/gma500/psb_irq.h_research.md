
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_irq.h

## Purpose
`psb_irq.h` declares the GMA500 interrupt and vblank support functions implemented in `psb_irq.c`.

## Important APIs, Types, And Functions
It forward-declares `struct drm_crtc` and `struct drm_device` and exposes IRQ lifecycle functions `gma_irq_preinstall()`, `gma_irq_postinstall()`, `gma_irq_install()`, and `gma_irq_uninstall()`. It also exposes CRTC vblank hooks `gma_crtc_enable_vblank()`, `gma_crtc_disable_vblank()`, `gma_crtc_get_vblank_counter()`, plus pipe status mask helpers `gma_enable_pipestat()` and `gma_disable_pipestat()`.

## Control Flow
There is no executable flow in the header. The DRM driver and CRTC/vblank setup code include it to wire IRQ lifecycle callbacks and vblank operations into probe, teardown, and atomic/page-flip paths.

## State And Persistence
The header owns no state. The declared functions manipulate `struct drm_psb_private` interrupt masks, pipe status software shadows, PCI IRQ state, SGX interrupt registers, VDC interrupt registers, and DRM vblank/event state.

## Dependencies And Integration Points
The prototypes require `u32` and `struct drm_psb_private` to be visible or forward-declared by including code, even though this header only forward-declares DRM core types. It integrates `psb_irq.c` with the rest of the GMA500 DRM driver.

## Risks
Because `struct drm_psb_private` is not forward-declared here, include ordering matters for users of `gma_enable_pipestat()` and `gma_disable_pipestat()`. Prototype drift from `psb_irq.c` would break the driver's IRQ wiring at compile time.

## Test Signals
Compile coverage of all including translation units is the main signal. Runtime validation is inherited from `psb_irq.c`: successful IRQ install, working vblank hooks, and clean uninstall.
