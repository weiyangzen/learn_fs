# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h

## Scope
This chunk covers lines 5108-7637 of `dce_12_0_offset.h`, the third generated slice of the AMD DCE 12.0 display-controller offset header. The covered region starts inside the `DCP2` register block at `mmDCP2_GRPH_X_START` and ends at `mmDCP5_DVMM_PTE_CONTROL_BASE_IDX`, so it is primarily the repeated register vocabulary for display pipes 2, 3, 4, and the beginning of pipe 5.

## Purpose
The chunk defines preprocessor constants for memory-mapped DCE 12.0 register offsets and their SOC15 base-segment indices. It has no executable code; its purpose is to let AMDGPU display code refer to hardware registers by generated symbolic names such as `mmDCP3_GRPH_PRIMARY_SURFACE_ADDRESS`, `mmCRTC4_CRTC_CONTROL`, or `mmSCL2_SCL_MODE` instead of hard-coded numeric offsets.

Every register name in this chunk has a paired `*_BASE_IDX` macro, and all paired base indices in this slice are `2`. Consumers combine `DCE_BASE__INST0_SEG2` from `vega10_ip_offset.h` with the `mm...` offset to form the final MMIO address used by SOC15 register helpers.

## Important APIs, types, and functions
There are no C functions, types, enums, or variables. The API surface is the macro namespace guarded by `_dce_12_0_OFFSET_HEADER`.

The important register groups in this chunk are:

- `mmDCP2_*`, `mmDCP3_*`, `mmDCP4_*`, and partial `mmDCP5_*`: display controller pipe registers for primary graphics surfaces, flip/update control, surface addresses, compression metadata, outstanding request limits, prescale values, input and output color-space conversion, gamut remap, dithering, cursor registers, LUT access, CRC, DVMM PTE controls, regamma LUT programming, and surface counters.
- `mmLB2_*`, `mmLB3_*`, and `mmLB4_*`: line-buffer and MVP line-buffer registers for data format, memory power control/status, debug state, vertical counter state, blanking control, and MVP output format.
- `mmDCFE2_*`, `mmDCFE3_*`, and `mmDCFE4_*`: front-end clock control, memory power control/status, power-on delay, debug, and flush registers.
- `mmDMIF_PG2_*`, `mmDMIF_PG3_*`, and `mmDMIF_PG4_*`: display memory interface pipe arbitration, watermark mask, urgency, stutter, low-power, buffer, DVMM debug, and status registers.
- `mmDC_PERFMON5_*`, `mmDC_PERFMON6_*`, and `mmDC_PERFMON7_*`: display performance monitor control, counter state, counter-value, and high/low counter registers.
- `mmSCL2_*`, `mmSCL3_*`, and `mmSCL4_*`: scaler coefficient RAM, tap/control, viewport, scale ratio, filter init, recout, overscan, bypass, and mode-change mask registers.
- `mmBLND2_*`, `mmBLND3_*`, and `mmBLND4_*`: blender control, VGA control, memory power, underflow, and update status registers.
- `mmCRTC2_*`, `mmCRTC3_*`, and `mmCRTC4_*`: timing-generator and scanout registers for blanking, totals, sync, active area, interlace, stereo, master update, vertical interrupt positions, status, count, trigger delay, black/color, overscan, static screen, 3D structure, global swap lock, manual flow control, CRC, test pattern, double-buffering, and dynamic refresh-rate control.
- `mmFMT2_*`, `mmFMT3_*`, and `mmFMT4_*`: output formatter clamp, dynamic expansion, bit depth, dithering seeds, temporal dithering pattern, memory control, 420 memory control, and early hblank registers.

## Control flow
This header chunk has no runtime control flow. Its only local control-flow effect is participation in the header include guard declared near the start of the file.

Runtime control flow is in consumers that expand register-list macros. `dce120_resource.c` includes this offset header with `dce_12_0_sh_mask.h`, `soc15_hw_ip.h`, and `vega10_ip_offset.h`. It defines `BASE(seg)` as `DCE_BASE__INST0_SEG##seg`, then expands macros such as `SRI(reg_name, block, id)` into `BASE(mm..._BASE_IDX) + mm...`. That is how instance-specific structures such as `mi_regs[]`, `ipp_regs[]`, `xfm_regs[]`, timing-generator offsets, and hardware sequencer register tables receive concrete MMIO offsets.

For this chunk specifically, `dce120_resource.c` builds six pipe instances. Entries for instance IDs 2, 3, and 4 consume the complete `DCP/LB/DCFE/DMIF/SCL/BLND/CRTC/FMT` sets in this slice, while instance 5 starts here and continues in the next chunk. `dce120_timing_generator.c` then uses the computed CRTC offset in helpers such as `dm_read_reg_soc15()`, `generic_reg_update_soc15()`, and `generic_reg_set_soc15()` so common CRTC0 field definitions can be applied to CRTC2/3/4 by adding the pipe offset.

## State and persistence behavior
The macros persist no software state. They address volatile GPU hardware state in the DCE display pipeline. The state reachable through this chunk includes:

- scanout framebuffer addresses, pitches, format, compression surfaces, and in-use surface-address state;
- flip/update and lock state used to coordinate surface updates with vblank;
- cursor position, hotspot, size, colors, address, stereo, request filtering, and cursor update lock state;
- input gamma, degamma, LUT, regamma, color-space conversion, gamut remap, clamp, rounding, dither, and CRC state;
- scaler coefficients, viewport dimensions, scaling ratios, filter setup, recout dimensions, and overscan;
- timing-generator totals, sync, blanking, trigger, interrupt, status, CRC, test pattern, dynamic refresh-rate, and global swap-lock state;
- DMIF pipe arbitration, watermark, urgency, stutter, low-power, DVMM, and buffer state;
- DCFE/LB/FMT/BLND power and formatting state;
- display performance counter configuration and counter values.

Any persistence across suspend/resume, GPU reset, modeset, or display hotplug is owned by higher-level AMDGPU DC resource, hardware-sequencer, timing-generator, memory-input, transform, IPP, OPP, and DMIF programming paths. The header only supplies the generated numeric ABI those paths use.

## Dependencies
The chunk itself depends only on the C preprocessor and the file-level include guard. Correct use depends on:

- `dce_12_0_sh_mask.h`, which supplies field shifts and masks matching these DCE 12.0 register names;
- `vega10_ip_offset.h`, especially `DCE_BASE__INST0_SEG2`, used by `BASE(mm..._BASE_IDX)` in DCE120 resource setup;
- `soc15_hw_ip.h` and AMDGPU SOC15 register helper infrastructure;
- display DC headers that define the register-list expansion macros, including `dce_mem_input.h`, `dce_ipp.h`, `dce_transform.h`, `dce_opp.h`, `dce_hwseq.h`, and DCE120 timing-generator/resource code;
- ASIC/IP selection that actually uses the DCE 12.0 layout. Cross-generation DCE and DCN headers carry similar names but not necessarily identical offsets.

## Integration points
The direct include sites for this header include `amdgpu/gmc_v9_0.c`, `display/dc/resource/dce120/dce120_resource.c`, `display/dc/dce120/dce120_timing_generator.c`, and `display/dc/hwss/dce120/dce120_hwseq.c`.

`dce120_resource.c` is the main structural integration point. It turns the `mm...` constants into `struct dce_mem_input_registers`, `struct dce_ipp_registers`, `struct dce_transform_registers`, hardware sequencer registers, stream encoder registers, audio registers, and timing-generator offsets. For the registers in this chunk:

- memory input setup uses DCP and DMIF_PG macros from `MI_DCE12_REG_LIST(id)`;
- IPP setup uses DCP cursor, prescale, gamma, degamma, and LUT macros;
- transform setup uses LB, DCP color/remap/regamma, SCL, and related formatting macros;
- OPP/output formatting uses FMT macros;
- timing-generator code uses CRTC offsets for pipe-specific register reads and updates;
- hardware sequencing and modeset paths rely on the same generated offsets when coordinating display pipe updates.

`dce120_timing_generator.c` shows the pipe-offset model clearly: it reads `mmCRTC0_CRTC_STATUS` plus `tg110->offsets.crtc`, where `offsets.crtc` is calculated as `mmCRTCn_CRTC_CONTROL - mmCRTC0_CRTC_CONTROL`. Thus the CRTC2/3/4 constants in this chunk are part of the arithmetic that maps generic CRTC0-oriented helper code onto a selected pipe.

## Risks and edge cases
The main risk is generated-register drift. These values are hardware ABI data; a single wrong offset or base index can redirect reads and writes to the wrong display pipe or wrong register within a pipe. That can cause black screens, unstable modesets, missed vblank/update events, corrupted color processing, stale cursor state, broken scaling, or unsafe power/clock behavior.

The repeated pipe layout is regular but should not be inferred by consumers. This chunk shows mostly complete blocks for instances 2-4 and only the beginning of instance 5. Code must continue to use generated symbols rather than deriving offsets from a fixed stride unless the owning register-list code already encodes that relationship.

All base indices in this chunk are `2`. Consumers that open-code offsets without adding `DCE_BASE__INST0_SEG2` will address the wrong MMIO location. Conversely, any future regenerated header that changes a base index requires the resource-list expansion macros to keep using `BASE(mm..._BASE_IDX)`.

Some register names imply side effects or synchronization-sensitive access. Surface update, flip, interrupt status/control, CRC, test pattern, master update lock, global swap lock, DMIF low-power/stutter, memory power control, and DVMM/PTE registers should be programmed only through the display-core sequencing that understands vblank, double-buffering, power state, and reset ordering.

The chunk boundary is inside a repeated DCP instance. `DCP2` begins in the previous chunk and `DCP5` continues in the next chunk, so per-file reconciliation must merge adjacent chunk research before making whole-file conclusions about complete instance coverage.

## Test signals
Useful validation signals are mostly compile-time and display integration oriented:

- Build AMDGPU DC with DCE12 support and confirm `dce120_resource.c`, `dce120_timing_generator.c`, `dce120_hwseq.c`, and `gmc_v9_0.c` compile with this offset header and `dce_12_0_sh_mask.h`.
- Modeset testing on DCE 12.0 hardware with active pipes 2, 3, and 4, checking that scanout, scaling, color management, cursor, vblank, and page flips work on each pipe.
- Multi-monitor tests that exercise pipe instances beyond 0/1, since this chunk primarily covers instances 2-4 and the start of 5.
- Suspend/resume and GPU reset tests verifying that DCP, CRTC, SCL, FMT, DMIF, LB, DCFE, BLND, and color/LUT state is restored by higher-level DC sequences.
- Hardware register traces comparing `BASE(mm..._BASE_IDX) + mm...` for representative registers such as `mmDCP3_GRPH_PRIMARY_SURFACE_ADDRESS`, `mmCRTC4_CRTC_CONTROL`, `mmSCL2_SCL_MODE`, and `mmFMT4_FMT_BIT_DEPTH_CONTROL` against AMD's generated register database.
- Negative signals include wrong-pipe register writes, cursor only failing on higher-index pipes, incorrect color transform after enabling CRTC2-4, missed vblank interrupts, underruns/underflows in BLND/DMIF status, or scaler/FMT behavior diverging only on pipe instances covered by this chunk.
