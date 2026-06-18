# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/g4x_dp.h

## Purpose
`g4x_dp.h` declares the public interface for the legacy G4x through CHV DisplayPort encoder implementation. It hides the implementation behind `#ifdef I915` and provides inert stubs for builds where the i915 display code is not compiled.

## Important APIs, Types, and Functions
The exported functions are `vlv_get_dpll()`, `g4x_dp_port_enabled()`, and `g4x_dp_init()`. `vlv_get_dpll()` lets other display code obtain the VLV/CHV DP DPLL table. `g4x_dp_port_enabled()` reads whether a DP port is enabled and returns the selected pipe. `g4x_dp_init()` creates and wires the encoder/connector for a hardware DP register and port.

## Control Flow and State
The header carries no state. It forward-declares `enum pipe`, `enum port`, and the display/encoder/DP structs used by the C file, keeping consumers independent of the full type definitions unless they include implementation headers.

## Dependencies and Integration Points
It includes `linux/types.h` and `i915_reg_defs.h` for `bool` and `i915_reg_t`. `intel_display.c` and other display initialization/readout code use these declarations. The non-I915 stubs return `NULL`, `false`, or no-op-equivalent values so shared code can compile without linking the DP implementation.

## Risks and Test Signals
The header is low risk, but prototypes must remain synchronized with `g4x_dp.c`. A notable maintenance issue is that the stub versions take `int port` while the real versions use `enum port`, which is ABI-compatible in C but can mask type drift. Build coverage with and without `I915` is the main test signal.
