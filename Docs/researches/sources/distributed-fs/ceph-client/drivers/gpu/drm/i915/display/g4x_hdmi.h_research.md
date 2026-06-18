# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/g4x_hdmi.h

## Purpose
`g4x_hdmi.h` declares the public entry points for legacy G4x-family HDMI support and provides fallback stubs for builds without `I915`.

## Important APIs, Types, and Functions
The header exports `g4x_hdmi_init()`, which creates an HDMI encoder/connector for a hardware register and port, and `g4x_hdmi_connector_atomic_check()`, which performs connector validation and G4x-specific state expansion for HDMI infoframe/audio selection.

## Control Flow and State
The header contains only declarations and conditional stubs. It forward-declares `enum port`, `struct drm_atomic_state`, `struct drm_connector`, and `struct intel_display`. No state is stored here.

## Dependencies and Integration Points
It includes `linux/types.h` and `i915_reg_defs.h` for basic types and MMIO register identifiers. HDMI initialization in `intel_display.c` consumes `g4x_hdmi_init()`, while connector setup can use the atomic-check helper. Non-I915 stubs return `false` or success (`0`) to keep shared builds linkable.

## Risks and Test Signals
Risk is mainly declaration drift between the header and implementation. Build tests with `I915` enabled and disabled verify the conditional interface. Runtime coverage belongs to `g4x_hdmi.c`.
