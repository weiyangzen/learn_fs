# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx10.h

## Purpose
`clearstate_gfx10.h` is a generated/static AMDGPU clear-state data table for GFX10 devices. It defines the default context-register payload used to initialize the graphics clear-state block so the CP/RLC can restore known baseline graphics context state. The file contains no executable functions; its interface is the `gfx10_cs_data` static section table consumed by `gfx_v10_0.c`.

## Important APIs, Types, and Data
The file relies on `struct cs_extent_def` and `struct cs_section_def` from `clearstate_defs.h`. It defines eight `static const unsigned int gfx10_SECT_CONTEXT_def_*[]` arrays and combines them in `gfx10_SECT_CONTEXT_defs[]`, terminated by `{ 0, 0, 0 }`. The exported-to-include-unit table is `gfx10_cs_data[]`, with one `SECT_CONTEXT` section and a `{ 0, SECT_NONE }` terminator.

The context extents are `{reg_index, reg_count}` clusters starting at `0x0000a000` (215 registers), `0x0000a0d8` (272), `0x0000a1f5` (4), `0x0000a1ff` (158), `0x0000a2a0` (2), `0x0000a2a3` (1), `0x0000a2a5` (66), and `0x0000a2f5` (203). The register comments show coverage across depth buffer, scissor/viewport, shader/primitive, VGT, PA, and color-buffer registers, including CB DCC/FMASK/CMASK/base/attribute registers for eight color targets. Most values are zero, but required hardware defaults include scissor bounds such as `0x40004000`, full target/shader masks, viewport `ZMAX` values of `0x3f800000`, cache-control defaults such as `DB_RMI_L2_CACHE_CONTROL` and `CB_RMI_GL2_CACHE_CONTROL`, and geometry defaults such as `VGT_GS_PER_ES`.

## Control Flow and Integration
There is no local control flow. At compile time `gfx_v10_0.c` includes this header, assigns `adev->gfx.rlc.cs_data = gfx10_cs_data`, and uses it in clear-state sizing/building paths. `gfx_v10_0_get_csb_size()` walks each `cs_section_def` and `cs_extent_def`, adding `2 + reg_count` dwords per context extent. `gfx_v10_0_cp_gfx_start()` emits `PACKET3_SET_CONTEXT_REG` packets over the graphics ring by subtracting `PACKET3_SET_CONTEXT_REG_START` from each extent `reg_index`, then writes every payload dword. GFX10 also appends `PA_SC_TILE_STEERING_OVERRIDE` from runtime config outside this static table.

## State and Persistence Behavior
The arrays are immutable kernel text/rodata. They do not persist state independently and are not updated at runtime. Their values are copied into the RLC clear-state buffer or written to the CP ring during graphics startup/resume. The persistent effect is on GPU hardware context initialization: after clear-state setup, command processor/RLC operations can restore these baseline context registers.

## Dependencies
The table depends on the `clearstate_defs.h` ABI, GFX10 context-register numbering, and the packet-building code in `gfx_v10_0.c`. It assumes the register offsets and array lengths match the hardware generation. The comments are register-name documentation only; the actual contract is positional data plus `reg_index` and `reg_count`.

## Risks
The primary risk is table drift from hardware definitions. A bad `reg_count`, wrong start index, missing hole, or misplaced nonzero default will shift every subsequent register write and can cause rendering failures, GPU hangs, or reset/resume bugs. Because the arrays are static and consumed by pointer walking until a null extent, terminator integrity is also critical. The file lacks an include guard, so it is intended for single inclusion from the matching GFX10 implementation.

## Test Signals
Useful signals are successful boot/resume on GFX10 ASICs, successful RLC clear-state block allocation, clean `gfx_v10_0_cp_gfx_start()` ring submission, absence of GPU hangs after clear-state preamble execution, and graphics validation covering depth/stencil, viewport/scissor, DCC, FMASK/CMASK, and multi-render-target paths. Static review should verify extent counts against array lengths and register ranges.
