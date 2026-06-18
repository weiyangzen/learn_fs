# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/seq.h

## Purpose
Wraps the bus hardware-sequencer API with clock-specific macros used by the NV50 clock implementation.

## Important APIs, types, and functions
Macros include `clk_init`, `clk_exec`, `clk_have`, `clk_rd32`, `clk_wr32`, `clk_mask`, `clk_setf`, `clk_wait`, and `clk_nsec`.

## Control flow
Macros expand directly to hwsq operations on the embedded `base` script and named register descriptors.

## State and persistence
No state is defined. The macros operate on an hwsq object supplied by the caller.

## Dependencies and integration points
Depends on `<subdev/bus/hwsq.h>`. Used by `nv50.c` to build and execute safe reclocking scripts.

## Risks
The token-pasting register names require the hwsq struct fields to be named `r_<name>`. A typo compiles only if a matching field exists and otherwise breaks build.

## Test signals
Build coverage and NV50 reclocking script execution.
