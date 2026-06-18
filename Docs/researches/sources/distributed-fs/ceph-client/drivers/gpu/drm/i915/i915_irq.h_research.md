# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_irq.h

## Purpose
Declares i915 top-level IRQ lifecycle APIs and common gen2-style IRQ/error register helpers.

## Important APIs, types, and functions
Exports install/init/fini/uninstall/suspend/resume/synchronize functions, `intel_irqs_enabled()`, gen2 IRQ/error reset/init helpers, `gen2_assert_iir_is_zero()`, and the display IRQ parent interface. It also declares several GT/RPS interrupt helpers implemented elsewhere.

## Control flow
No runtime flow exists in the header; it defines the callable surface for driver lifecycle and display/GT integration.

## State and persistence
No local state. Declared functions operate on `drm_i915_private`, `intel_uncore`, and hardware IRQ registers.

## Dependencies and integration points
Includes `i915_reg_defs.h` for register struct types and is included by interrupt, GT PM, display, and driver lifecycle code.

## Risks
Because the header mixes top-level and GT/RPS declarations, stale prototypes can affect multiple subsystems. Register helper callers must pass the correct register tuple for the platform.

## Test signals
Build coverage plus suspend/resume, driver load/unload, and RPS interrupt tests validate the API wiring.
