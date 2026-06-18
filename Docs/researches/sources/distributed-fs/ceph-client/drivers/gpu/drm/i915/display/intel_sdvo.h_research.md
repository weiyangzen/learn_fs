# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sdvo.h

## Purpose
`intel_sdvo.h` is the small public interface for i915 SDVO support. It declares the SDVO initialization and hardware-state query functions used by the rest of the display driver and provides no-op inline stubs when the i915 build guard is absent.

## Important APIs, Types, And Functions
- Forward declarations: `enum pipe`, `enum port`, and `struct intel_display`.
- `intel_sdvo_port_enabled(struct intel_display *display, i915_reg_t sdvo_reg, enum pipe *pipe)` reads whether an SDVO port register is enabled and reports the selected pipe.
- `intel_sdvo_init(struct intel_display *display, i915_reg_t reg, enum port port)` probes and registers one SDVO encoder instance.
- The `#ifdef I915` section exposes real declarations for the driver build; the `#else` section returns `false` from both helpers.

## Control Flow
The header has no runtime control flow beyond compile-time selection. Callers can unconditionally reference SDVO helpers; non-i915 builds compile to disabled behavior through static inline stubs.

## State And Persistence
The header owns no state. It passes through `intel_display`, MMIO register, port, and pipe pointer arguments to the implementation.

## Dependencies And Integration Points
It depends on Linux integer types and `i915_reg_defs.h` for `i915_reg_t`. It is included by SDVO implementation code and by broader display initialization/readout code that probes legacy ports.

## Risks And Edge Cases
The stubbed functions always return false, so code compiled without `I915` must not expect SDVO hardware support. The `pipe` output in the real implementation is meaningful even when a port is disabled, but the stub does not write it; callers in stubbed builds must tolerate that.

## Test Signals
Build coverage should include both `I915` and non-`I915` configurations. Runtime testing is covered through `intel_sdvo.c`; this header's direct signal is successful compilation and correct call-site behavior when SDVO support is disabled.
