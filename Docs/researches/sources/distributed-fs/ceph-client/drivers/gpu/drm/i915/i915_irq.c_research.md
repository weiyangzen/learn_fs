# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_irq.c

## Purpose
Implements top-level i915 interrupt installation, teardown, suspend/resume, generation-specific IRQ handlers, common gen2-style IRQ/error register helpers, PMU IRQ accounting, and Ivybridge L3 parity error notification.

## Important APIs, types, and functions
Public APIs are `intel_irq_init()`, `intel_irq_fini()`, `intel_irq_install()`, `intel_irq_uninstall()`, `intel_irq_suspend()`, `intel_irq_resume()`, `intel_irqs_enabled()`, `intel_synchronize_irq()`, `intel_synchronize_hardirq()`, `gen2_irq_reset()`, `gen2_irq_init()`, `gen2_error_reset()`, `gen2_error_init()`, and `gen2_assert_iir_is_zero()`. Handler families include legacy `i915_irq_handler()`, `i965_irq_handler()`, `ilk_irq_handler()`, `valleyview_irq_handler()`, `cherryview_irq_handler()`, `gen8_irq_handler()`, `gen11_irq_handler()`, and `dg1_irq_handler()`.

## Control flow
Install marks IRQs enabled before postinstall, resets generation-specific registers, requests the shared PCI IRQ with the selected handler, and postinstalls GT/display/PM/GU interrupt masks. Handlers generally verify `irqs_enabled`, disable master interrupt delivery or mask level sources, sample pending source registers, acknowledge IIR/status bits in hardware-safe order, dispatch GT/RPS/display/hotplug/audio/error handlers, re-enable master delivery, and increment PMU IRQ count only for handled device interrupts. Suspend resets hardware, flips `irqs_enabled` false, and synchronizes; resume flips true, resets, and postinstalls.

## State and persistence
Persistent state includes `dev_priv->irqs_enabled`, `dev_priv->gen2_imr_mask`, PMU `irq_count`, L3 parity tracking arrays, GT PM GuC event masks, and hardware interrupt mask/identity/error registers. L3 parity work stores pending slice bits until userspace uevents are emitted and parity interrupts are re-enabled.

## Dependencies and integration points
Depends on GT IRQ handlers, display IRQ/hotplug/audio handlers, runtime PM wakeref assertions, PCI IRQ APIs, uncore raw/MMIO access, RPS/GuC PM interrupts, DRM PMU, and display parent IRQ interface `i915_display_irq_interface`.

## Risks
IRQ ordering is race-sensitive: master disable, source sampling, ack, dispatch, and re-enable differ by platform. Some status bits are level/single-buffered, requiring clear-last behavior. DG1 only supports tile 0 in this path. Legacy error bits can stick and are masked to avoid interrupt storms. PMU accounting must not count shared-line interrupts. Runtime suspend relies on IRQ synchronization instead of wakerefs.

## Test signals
Boot and suspend/resume across gen2 through DG1-era hardware, hotplug displays, trigger vblank/pipe events, GT breadcrumbs, RPS interrupts, LPE audio, legacy master errors, and IVB L3 parity paths. Watch for interrupt storms, lost hotplugs, stale IIR warnings, PMU IRQ counts, and correct `synchronize_irq()` behavior during uninstall/suspend.
