# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_irq.h

## Purpose
`intel_display_irq.h` declares the display interrupt API used by platform IRQ installation, vblank support, power-well management, hotplug/AUX handlers, and error reporting. It abstracts generation-specific display IRQ details behind common names.

## Important APIs, Types, And Functions
The header declares IRQ update helpers for ILK/PCH/BDW, VLV display IRQ runtime toggles, vblank enable/disable variants, master disable/enable for ILK-style display IRQs, top-level handlers for ILK/gen8/gen11/GU misc, reset and postinstall functions for major generations, pipestat helpers, VLV error ack/handler, IRQ initialization, i915gm C-state workaround toggling, PICA AUX mask helper, and IRQ snapshot capture/print. It forward declares `struct drm_crtc`, `struct drm_printer`, `struct intel_display`, and `struct intel_display_irq_snapshot`.

## Control Flow And State
The header does not implement logic, but it defines call points that the parent interrupt code must sequence: reset before install/uninstall, postinstall after core IRQ setup, handler calls from master IRQ dispatch, and vblank callbacks from DRM CRTC funcs. Snapshot allocation/capture is separated from printing to support error-state reporting.

## Dependencies And Integration Points
It includes `intel_display_limits.h` for `enum pipe` and pipe array sizes. It is consumed by display driver probe, parent IRQ code, power management, vblank setup, and error-state code. Implementations rely on `display->irq` state from `intel_display_core.h`.

## Risks And Test Signals
Risks come from mismatched generation selection by callers, especially selecting the wrong vblank or postinstall hooks for a platform. Build coverage catches signature drift; runtime signals include working vblank counters, hotplug/AUX interrupts, no spurious master IRQ logs, and successful error-state IRQ snapshot printing.
