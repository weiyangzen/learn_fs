# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_irq.c

## Purpose
`intel_display_irq.c` implements display interrupt reset, postinstall, mask updates, acknowledgment, handling, vblank enable/disable, power-well IRQ reinitialization, fault reporting, and lightweight IRQ snapshot capture for i915 display generations from legacy i8xx/i9xx through gen11+ and Xe display IP.

## Important APIs, Types, And Functions
Public functions include mask updaters (`ilk_update_display_irq()`, `bdw_update_port_irq()`, `bdw_enable/disable_pipe_irq()`, `ibx_display_interrupt_update()`), vblank controls (`i8xx`, `i915gm`, `i965`, `ilk`, `bdw` variants), IRQ handlers (`ilk_display_irq_handler()`, `gen8_de_irq_handler()`, `gen11_display_irq_handler()`, GU misc handlers), reset/postinstall routines for i9xx/ilk/vlv/gen8/gen11/dg1, VLV display IRQ runtime enable/disable, pipestat helpers, power-well hooks, and `intel_display_irq_snapshot_capture/print()`. Internal helpers handle IIR zero assertions, pipe faults, CRC delivery, flip-done events, PCH IRQs, GTT/page-table faults, PSR, AUX, HPD, GMBUS, DSB, PM demand, DSI TE, and underruns.

## Control Flow And State
Interrupt setup masks everything, clears queued IIR/EIR bits, then postinstall enables generation-specific sources. Runtime updates are serialized by `display->irq.lock` and often assert that the parent IRQ is enabled. Cached masks in `display->irq` avoid unsafe reads or preserve state across power domains. Handlers ack IIR bits before dispatch, then route to subhandlers based on generation and source group. Vblank enabling toggles pipestat or DE pipe bits, handles PSR frame-counter restore, and notifies PSR when BDW+ vblank enable count transitions.

## Dependencies And Integration Points
The file integrates display MMIO access (`intel_de`), DRM vblank/event delivery, HPD IRQ helpers, AUX, GMBUS, opregion ASLE, PSR, DMC/PipeDMC, DSB, FIFO underrun, plane fault capture, PCH handlers, parent IRQ state, runtime PM assertions, and pipe CRC debugfs support. Its generation-specific branches rely heavily on `DISPLAY_VER()`, platform flags, PCH type, and runtime pipe/transcoder masks.

## Risks And Test Signals
Risks include lost interrupts due to wrong ack order, stale cached masks, accessing powered-down pipe/transcoder registers, missed PCH/PICA forwarding, lock misuse in interrupt context, incorrect fault-bit-to-plane mapping, and vblank/PSR interactions causing stuck frame counters. Test signals include DRM vblank tests, page-flip completion, hotplug/AUX storm testing, pipe CRC capture, FIFO underrun injection, suspend/runtime-PM power-well cycling, fault reporting logs, PICA/PCH IRQ tests on newer platforms, lockdep, and IRQ reset/postinstall behavior during driver load/unload.
