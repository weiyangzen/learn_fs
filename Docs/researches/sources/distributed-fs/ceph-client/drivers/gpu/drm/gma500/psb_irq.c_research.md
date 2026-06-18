
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_irq.c

## Purpose
`psb_irq.c` implements interrupt installation, masking, dispatch, vblank enable/disable, page-flip event completion, SGX fault logging, hotplug dispatch, and vblank counter reads for the GMA500 DRM driver.

## Important APIs, Types, And Functions
Exported functions are `gma_irq_preinstall()`, `gma_irq_postinstall()`, `gma_irq_install()`, `gma_irq_uninstall()`, `gma_crtc_enable_vblank()`, `gma_crtc_disable_vblank()`, `gma_crtc_get_vblank_counter()`, `gma_enable_pipestat()`, and `gma_disable_pipestat()`. Internal helpers are `gma_pipestat()`, `gma_pipeconf()`, `gma_pipe_event_handler()`, `gma_vdc_interrupt()`, `gma_sgx_interrupt()`, and the IRQ top half `gma_irq_handler()`.

## Control Flow
`gma_irq_install()` optionally enables MSI, rejects disconnected IRQs, masks and clears hardware in `gma_irq_preinstall()`, requests a shared PCI IRQ, and calls `gma_irq_postinstall()`. The postinstall step enables SGX 2D/MMU-fault interrupts, enables the VDC interrupt mask, configures per-pipe vblank pipestat bits for already enabled vblank users, and enables hotplug if the platform ops provide it.

The IRQ handler reads `PSB_INT_IDENTITY_R` under `irqmask_lock`, classifies display, SGX, and hotplug causes, applies the current `vdc_irq_mask`, then dispatches display events to `gma_vdc_interrupt()`, SGX events to `gma_sgx_interrupt()`, and hotplug to `dev_priv->ops->hotplug()`. Display pipe handling reads the relevant pipe status register, intersects enabled and status bits, repeatedly writes back the register to clear sticky bits, calls `drm_handle_vblank()`, and sends any pending page-flip vblank event under `dev->event_lock`.

Vblank enable checks that the pipe is enabled, updates `vdc_irq_mask`, writes interrupt mask/enable registers, and enables the pipe vblank status bit. Disable clears the corresponding pipe interrupt bit and disables pipestat. The vblank counter reads the high and low frame counter registers with a high-register stability loop.

## State And Persistence
Software state is held in `dev_priv->vdc_irq_mask`, `dev_priv->pipestat[]`, `dev_priv->irq_enabled`, `dev_priv->use_msi`, and each CRTC's pending `page_flip_event`. Hardware state includes VDC interrupt mask/enable/identity registers, pipe status registers, SGX host interrupt enable/clear/status registers, hotplug status, and per-pipe frame counters.

## Dependencies And Integration Points
The file depends on GMA500 register accessors from `psb_drv.h`, power gating helpers from `power.h`, display constants from `psb_intel_reg.h`, SGX constants from `psb_reg.h`, DRM vblank/event helpers, PCI IRQ/MSI APIs, and platform operations for hotplug and hotplug enable. It is declared by `psb_irq.h`.

## Risks
Pipe selection helpers call `BUG()` for invalid pipe indexes. Clearing pipe status uses a large retry loop for sticky bits and may still fail, producing errors. Interrupt mask updates are protected by `irqmask_lock`, but power-gated display access can fail and leave software masks out of sync with hardware. The hotplug identity bit is noted as overloaded on some devices. `gma_irq_uninstall()` preserves some non-display masks, so ordering with other engines matters.

## Test Signals
Useful tests include IRQ install/uninstall across MSI and shared-IRQ paths, vblank enable failure on disabled pipes, correct vblank event delivery and `drm_crtc_vblank_put()` balancing for page flips, stable frame counter increments, SGX fault logs and clears on induced faults, hotplug callback execution and `PORT_HOTPLUG_STAT` clearing, and no interrupt storms after repeated DPMS or suspend/resume cycles.
