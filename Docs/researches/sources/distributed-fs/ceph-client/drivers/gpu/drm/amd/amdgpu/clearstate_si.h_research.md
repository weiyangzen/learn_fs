# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_si.h

## Purpose
`clearstate_si.h` contains Southern Islands/GFX6 clear-state context defaults. It is included by `gfx_v6_0.c` and provides `si_cs_data`, the static data source used when programming clear-state packets for SI-generation GPUs.

## Important APIs, Types, and Data
The file defines seven `static const u32 si_SECT_CONTEXT_def_*[]` arrays, `si_SECT_CONTEXT_defs[]`, and `si_cs_data[]`. The extent table covers `0x0000a000` for 212 registers, `0x0000a0d8` for 272, `0x0000a1f5` for 6, `0x0000a200` for 157, `0x0000a2a1` for 1, `0x0000a2a3` for 1, and `0x0000a2a5` for 233. It uses `NULL` sentinels rather than plain zero for pointer fields.

The register comments cover early DB/depth state, PA scissor/window/viewport arrays, CB masks, SPI state, VGT defaults, clip/raster state, and SI-era color target registers using pitch/slice naming rather than newer base-extension naming. Defaults include nonzero scissor bounds, full CB masks, viewport `ZMAX` values, maximum vertex index, clip control, GS/ES/VS ratios, and vertex reuse/deallocation controls.

## Control Flow and Integration
The header has no functions. `gfx_v6_0.c` assigns `adev->gfx.rlc.cs_data = si_cs_data` for SI ASICs and later walks the table in `gfx_v6_0_cp_gfx_start()`. That path emits `PACKET3_PREAMBLE_BEGIN_CLEAR_STATE`, then for each `SECT_CONTEXT` extent emits `PACKET3_SET_CONTEXT_REG`, the adjusted register offset, and all data dwords before ending the clear-state preamble.

## State and Persistence Behavior
The arrays are immutable and carry no runtime state. Their values are transferred into hardware context registers during CP graphics startup. Persistence is hardware-side only: after the preamble, CP/RLC clear-state behavior uses these defaults until the device is reset or reinitialized.

## Dependencies
Dependencies include `clearstate_defs.h`, SI/GFX6 context-register layout, `gfx_v6_0.c` graphics startup, and packet definitions such as `PACKET3_SET_CONTEXT_REG_START`. The use of `u32` assumes an includer has already made Linux integer typedefs available.

## Risks
SI hardware is older and register layouts differ from VI/GFX9+, so porting entries between generations is risky. A shifted hole or incorrect count can misprogram large register ranges. Since this file uses `NULL` sentinels while newer headers often use `0`, consumers must treat both as null pointers; current pointer checks do. Missing nonzero defaults can break legacy rendering paths that rely on established clear-state behavior.

## Test Signals
Signals include successful `gfx_v6_0_cp_gfx_start()`, ring tests passing after clear-state preamble, no GPU lockups on SI devices, and rendering correctness across depth/stencil, scissor/viewport, geometry shader defaults, and color-buffer pitch/slice/CMASK/FMASK paths. Static checks should verify all seven extents against actual array lengths and confirm sentinel termination.
