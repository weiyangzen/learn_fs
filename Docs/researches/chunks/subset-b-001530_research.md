# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h lines 2498-5107

## Chunk Scope

This chunk is a generated AMD DCE 12.0 register-offset header segment. It contains 2,406 `#define` lines representing 1,203 MMIO register offset macros plus one `_BASE_IDX` companion macro for each register. The range starts at `mmDCRX_PHY_MACRO_CNTL_RESERVED16` on line 2498 and ends at `mmDCP2_GRPH_SURFACE_OFFSET_Y` on line 5106. It is partial at both ends: DCRX/DP receiver definitions begin in the preceding chunk, and the `DCP2` display pipe instance continues after this chunk.

## Purpose

The chunk provides symbolic register addresses for the DCE 12.0 display engine in AMDGPU. These offsets are consumed by DCE 12 display, interrupt, GPIO, resource, and memory-management code through `dce/dce_12_0_offset.h`, typically together with `dce/dce_12_0_sh_mask.h`, `soc15_hw_ip.h`, and `vega10_ip_offset.h`. The macros are not functions; they are compile-time constants that let shared DCE helper code address the correct SOC15 display registers for Vega-era DCE 12 hardware.

The generated pattern is:

- `mm<REGISTER_NAME>`: a register offset in the DCE register space.
- `mm<REGISTER_NAME>_BASE_IDX`: the register base-index selector, almost always `2` in this chunk.

## Register Families Covered

The first large section is the tail of the DCRX/DisplayPort receiver physical macro control space. Lines 2498-3257 define `mmDCRX_PHY_MACRO_CNTL_RESERVED16` through `mmDCRX_PHY_MACRO_CNTL_RESERVED379` at offsets `0x2c16` through `0x2d81`. The reserved naming indicates hardware-reserved or PHY-internal controls exposed by the ASIC register database. These should be treated as ABI-like hardware addresses even though most higher-level driver code should not directly program them without an ASIC-specific sequence.

Lines 3258-3271 define display audio transport controls and CRC test registers:

- `mmI2S0_CNTL`, `mmI2S1_CNTL`, and status/CRC data registers.
- `mmSPDIF0_CNTL`, `mmSPDIF1_CNTL`, and CRC test data registers.
- `mmCRC_I2S_CONT_REPEAT_NUM` and `mmCRC_SPDIF_CONT_REPEAT_NUM`.
- `mmZCAL_MACRO_CNTL_RESERVED0` through `mmZCAL_MACRO_CNTL_RESERVED4`.

Lines 3272-3527 define Azalia audio index/data windows:

- `AZF0STREAM0` through `AZF0STREAM15`, each with `AZALIA_STREAM_INDEX` and `AZALIA_STREAM_DATA`.
- `AZF0ENDPOINT0` through `AZF0ENDPOINT7`, each with `AZALIA_F0_CODEC_ENDPOINT_INDEX` and `AZALIA_F0_CODEC_ENDPOINT_DATA`.
- `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7`, each with `AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` and `AZALIA_F0_CODEC_INPUT_ENDPOINT_DATA`.

Lines 3528-4305 define the first full display pipe instance, pipe 0:

- `DCP0` graphics plane, cursor, color pipeline, LUT, gamma, regamma, CRC, DVMM/PTE, flip, XDMA, alpha, and surface counter registers.
- `LB0` line buffer format, memory, vline/vblank status, keyer color, buffer urgency/status, and MVP control registers.
- `DCFE0` clock, reset, memory power, misc, and flush registers.
- `DC_PERFMON3` display performance counter and performance monitor registers.
- `DMIF_PG0` display memory interface pipe arbitration, watermark, urgency, stutter, low-power, repeater, and DVMM status registers.
- `SCL0` scaler coefficient RAM, mode, tap/filter setup, viewport, overscan, update, and mode-change detection registers.
- `BLND0` blender control, update, underflow interrupt, update lock, and status registers.
- `CRTC0` timing generator registers for horizontal/vertical timing, sync, trigger, flow control, blanking, interlace, status counters, snapshots, update locks, test patterns, MVP, vertical interrupts, CRC windows/data, external timing sync, static screen, 3D, GSL, range timing, and DRR.
- `FMT0` formatter clamp, dynamic expansion, bit-depth, dither seeds, CRC masks/signatures, side-by-side stereo, and 4:2:0 hblank early-start registers.

Lines 4306-5083 repeat the same pipe topology for pipe 1 at the `0x800` instance base: `DCP1`, `LB1`, `DCFE1`, `DC_PERFMON4`, `DMIF_PG1`, `SCL1`, `BLND1`, `CRTC1`, and `FMT1`. The offsets advance by `0x200` from the corresponding pipe-0 macro values in this chunk, while the address-block comments show the hardware instance base as `0x800`.

Lines 5084-5107 begin pipe 2 at base address `0x1000`, defining only the opening `DCP2` graphics-plane registers visible in this chunk: graphics enable/control, LUT bypass, swap control, primary/secondary surface addresses and high parts, pitch, and surface X/Y offsets.

## Important APIs, Types, And Macros

No C functions, structs, or enums are declared in this range. The important exported interface is the macro namespace itself. Downstream code uses macros such as `mmCRTC0_CRTC_CONTROL`, `mmCRTC1_CRTC_CONTROL`, `mmDCP0_GRPH_ENABLE`, and their `_BASE_IDX` constants in SOC15 register access helpers.

Representative integration patterns visible elsewhere in the tree:

- `display/dc/resource/dce120/dce120_resource.c` builds `dce120_tg_offsets[]` by subtracting `mmCRTC0_CRTC_CONTROL` from each pipe's `mmCRTCx_CRTC_CONTROL`. This makes the generated per-pipe spacing part of the timing-generator object model.
- `display/dc/dce120/dce120_timing_generator.c` reads `mmCRTC0_CRTC_CONTROL` with a per-instance offset through `dm_read_reg_soc15()` and decodes fields using `dce_12_0_sh_mask.h`.
- `display/dc/irq/dce120/irq_service_dce120.c`, GPIO factory/translation code, and hardware sequencing code include this header so DCE 12 register lists resolve to numeric SOC15 addresses.

## Control Flow

This header has no runtime control flow. Its operational flow is indirect:

1. DCE 12 modules include this file and the matching shift/mask header.
2. Resource construction computes per-instance offsets from a canonical pipe-0 macro.
3. Register helper macros and functions combine the base register macro, `_BASE_IDX`, SOC15 IP base, and instance offset.
4. Display code reads or writes hardware state for timing generation, plane programming, scaler setup, color management, interrupts, and audio endpoint access.

Because the offset macros are constant inputs to register access, a wrong value changes runtime behavior silently: code still compiles, but it reads or writes a different hardware register.

## State And Persistence Behavior

The file itself stores no software state and performs no persistence. The macros describe stateful hardware registers. Relevant hardware state categories exposed in this chunk include:

- Persistent-until-reprogrammed display pipe configuration: plane surface addresses, pitch, viewport, scaler coefficients, color matrices, LUT/regamma data, cursor state, timing totals, sync positions, blanking, formatter bit depth, and blender controls.
- Volatile hardware status: line buffer levels, vblank/vline status, CRTC counters, interrupt status, CRTC snapshots, performance counter values, CRC data, underflow status, and DMIF/DVMM status.
- Power/reset controls: `DCFE*_DCFE_CLOCK_CONTROL`, `DCFE*_DCFE_SOFT_RESET`, memory power controls/status, DCRX clock/light-sleep/gate controls inherited from the adjacent DCRX section, and the reserved PHY/ZCAL regions.

Many registers in DCE are double-buffered or latched by update-lock/update-control registers. The header only names the offsets; correctness depends on callers observing the programming sequence in the display core.

## Dependencies

This chunk depends on the ASIC register generator contract and the DCE 12 register map. The immediate compile-time dependencies are consumers that expect:

- Stable macro names shared with generated register-list macros in DCE 12 display objects.
- Matching field definitions in `dce_12_0_sh_mask.h`.
- SOC15 addressing helpers that understand `_BASE_IDX` values and DCE IP base selection.
- Instance spacing consistency between pipe blocks, especially the pipe offset computations from `mmCRTCx_CRTC_CONTROL - mmCRTC0_CRTC_CONTROL`.

The chunk has no include dependencies of its own beyond the file-level include guard defined earlier in the header.

## Integration Points

Primary integration is the AMDGPU display core for DCE 12:

- Timing generator: `CRTC0` and `CRTC1` offsets support mode timing, blanking, vblank/vupdate interrupts, CRC capture, DRR, test pattern, stereo/3D, and external timing sync.
- Plane and color management: `DCP0`/`DCP1` offsets support scanout surface programming, flips, cursor programming, input/output CSC, gamut remap, degamma/regamma, LUT access, alpha, dithering, and CRC.
- Memory/display fetch: `DMIF_PG0`/`DMIF_PG1`, `LB0`/`LB1`, and `DCFE0`/`DCFE1` support buffer fetch arbitration, watermarks, urgency, low-power, line buffer status, and display frontend flush/reset.
- Scaler and formatter: `SCL0`/`SCL1`, `BLND0`/`BLND1`, and `FMT0`/`FMT1` support viewport scaling, overscan, blending, output formatting, clamping, bit depth, dithering, stereo, and output CRC.
- Audio: `I2S`, `SPDIF`, and `AZF0*` stream/endpoint index/data windows expose display audio routing/control surfaces.
- Diagnostics: `DC_PERFMON3` and `DC_PERFMON4`, DCP/FMT/CRTC CRC registers, audio CRC registers, and numerous status registers are test and debug hooks.

## Risks

The main risk is offset drift. These constants are hardware ABI data; hand edits or generator mistakes can cause register writes to hit the wrong block, especially because pipe instances are regular and errors may look like programming the wrong CRTC or plane.

The `_BASE_IDX` values are as important as the offsets. A correct hex offset with a wrong base index can address the wrong SOC15 segment.

Reserved DCRX PHY and ZCAL registers are risky because their names do not document semantics. Any caller using them must rely on vendor sequencing or adjacent shift/mask documentation. Blind use can affect link training, receiver PHY state, or display/audio stability.

Partial chunk boundaries are a reconciliation risk. The DCRX block begins before line 2498, and `DCP2` continues after line 5107, so file-level conclusions about the complete DCE 12 register map require adjacent chunk reports.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware/display runtime signals:

- Kernel build of AMDGPU display code succeeds with `dce_12_0_offset.h` and `dce_12_0_sh_mask.h` included together.
- Static checks confirm every non-`_BASE_IDX` macro in this chunk has a companion `_BASE_IDX`; this chunk has 1,203 such pairs.
- Pipe-offset sanity checks confirm `CRTC1`, `DCP1`, `LB1`, `SCL1`, `BLND1`, and `FMT1` offsets maintain the expected pipe spacing from pipe 0 and match `dce120_tg_offsets[]` assumptions.
- Display smoke tests on DCE 12 hardware: modeset, page flip, cursor update, vblank interrupt, CRC capture, scaling, color/gamma programming, and suspend/resume.
- Audio-over-display tests for I2S/SPDIF/Azalia stream and endpoint programming.
- Debug/perf validation through `DC_PERFMON3/4`, CRTC/FMT/DCP CRC reads, and underflow/urgency status monitoring.
