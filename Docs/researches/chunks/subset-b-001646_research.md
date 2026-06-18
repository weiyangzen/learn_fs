# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h lines 12632-15144

## Purpose

This chunk is part of AMDGPU Display Core Next 2.0.1 generated register field metadata. It contains no executable C logic; it publishes compile-time bit positions and masks for DCN hardware registers. Each field is represented by paired `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros. Runtime display code combines these constants with companion address macros from `dcn_2_0_1_offset.h` and register helper macros such as `SF`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`.

The assigned range covers several display-pipeline blocks:

- The tail of the `MPCC_OGAM2` output-gamma RAM B region table for regions 20-33.
- Full `MPCC_OGAM3` and `MPCC_OGAM4` output-gamma blocks, including mode, LUT index/data/control, RAM A and RAM B start/slope/end controls, and paired region descriptors for regions 0-33.
- `MPC_OUT0` and `MPC_OUT1` output color-space-conversion fields for two coefficient banks, plus the MPC OCSC debug index register.
- Output pixel processor blocks for OPP/FMT/DPG/OPPBUF/OPP_PIPE instances 0 and 1, covering clamping, dithering, pixel format, 4:2:0/4:2:2 handling, display-pattern-generator controls, OPP buffer sizing/3D parameters, and OPP pipe clock gating.
- OPP top clock-control bits.
- ODM/OPTC input blocks for instances 0 and 1, including underflow/double-buffer status, data source selection, DSC data format, bytes-per-pixel, width, input clock control, and spare registers.
- The `OTG0` timing-generator block and the beginning of the `OTG1` block, covering horizontal/vertical timing, dynamic refresh-rate controls, trigger controls, enable/blank/interlace/status fields, CRC/signature capture, static-screen/3D/GSL/global-update controls, range timing interrupts, DRR/request/DSC positions, and early `OTG1` timing/control fields through `OTG1_OTG_INTERLACE_STATUS`.

Although this repository path is under a local `ceph-client` tree, this source is AMDGPU display hardware metadata. It has no Ceph filesystem protocol behavior, distributed filesystem state, or storage persistence.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or storage objects in this chunk. The macro namespace is the API.

The `MPCC_OGAM*` macros describe per-MPCC output gamma LUT programming. Important field families include `MPCC_OGAM_MODE`, `MPCC_OGAM_LUT_INDEX`, `MPCC_OGAM_LUT_DATA`, `MPCC_OGAM_LUT_RAM_CONTROL`, per-channel RAM A/B start controls, linear slopes, end bases/slopes, and repeated region descriptors. The region descriptors pack two regions per register: a low-half LUT offset and segment count, then a high-half LUT offset and segment count. The repeated masks are consistent across instances and RAM banks: LUT offsets use 9-bit fields, segment counts use 3-bit fields, and start/end/slope/base fields use wider 16-18 bit ranges depending on the register.

The `MPC_OUT*_CSC_*` macros expose the output color-space-conversion matrix. `MPC_OUT_CSC_COEF_FORMAT` selects coefficient format per output path, `MPC_OUT0_CSC_MODE` and `MPC_OUT1_CSC_MODE` select the OCSC mode, and the `C11_C12` through `C33_C34` registers carry packed 16-bit coefficients for banks A and B. `MPC_OCSC_TEST_DEBUG_INDEX` exposes a debug selector field for MPC OCSC diagnostics.

The `FMT0` and `FMT1` macros describe the formatter side of OPP. They cover clamp lower/upper bounds for R/G/B, dynamic expansion enable/mode, pixel encoding and subsampling controls, bit-depth truncation, spatial/temporal dithering controls, random seeds, clamp data enable/color format, side-by-side stereo, 4:2:0 memory power and phase status, and 4:2:2 left-edge extra pixel control.

The `DPG0` and `DPG1` macros describe display pattern generator state: enable/mode, dynamic range, bit depth, vertical/horizontal resolution, ramp offsets/increments, active dimensions, color values, segment offset/width, and double-buffer pending status.

The `OPPBUF0`, `OPPBUF1`, `OPP_PIPE0`, and `OPP_PIPE1` macros describe OPP buffer and pipe controls: active width, pixel repetition, display segmentation, overlap pixels, 3D active-space sizes, and OPP pipe clock enable/status bits. `OPP_TOP_CLK_CONTROL` provides top-level OPP clock-gating override bits.

The `ODM0` and `ODM1` macros expose OPTC/ODM input state. `OPTC_INPUT_GLOBAL_CONTROL` contains enable, double-buffer, underflow status/clear, and current-status fields. `OPTC_DATA_SOURCE_SELECT` chooses source segments and segment count. `OPTC_DATA_FORMAT_CONTROL`, `OPTC_BYTES_PER_PIXEL`, and `OPTC_WIDTH_CONTROL` carry DSC/data-format related fields. `OPTC_INPUT_CLOCK_CONTROL` controls and reports input clocks.

The `OTG0` and `OTG1` macros expose timing-generator fields. Core fields include totals, blanking, sync start/end/polarity, `OTG_CONTROL` enable/reset/start/disable/current-state bits, `OTG_BLANK_CONTROL`, interlace controls/status, status position/frame counters, trigger A/B controls and manual triggers, force-count and force-vsync controls, vertical interrupt controls, CRC windows/data, static-screen controls, 3D structure controls, global sync lock controls, master update locks, global-control update-lock windows, DRR and request controls, and DSC start position. This chunk includes the complete `OTG0` set in the range and the first part of `OTG1` through interlace status.

## Control Flow

This header range has no runtime control flow. It is preprocessor data.

Runtime behavior appears through consumers that bind these field layouts into component-specific register tables. A typical flow is:

1. A DCN201 module includes `dcn_2_0_1_offset.h` for register addresses and this file for field masks/shifts.
2. A component header lists the fields it needs with `SF(register, field, mask_sh)` or related helper macros.
3. Initialization code stores the selected masks/shifts in component structures for MPC, OPP, OPTC/timing-generator, IRQ, or clock-management paths.
4. Runtime code uses `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, `REG_READ`, `REG_WRITE`, or `REG_WAIT` to pack/unpack register values using the generated masks and shifts.
5. Hardware applies the resulting MMIO writes according to display engine sequencing rules, double-buffer update modes, vblank/update locks, or self-clearing status/ack behavior.

Control-sensitive behavior represented by this chunk includes programming output gamma LUTs, selecting MPC output CSC modes and coefficients, configuring formatter bit depth and dithering, enabling pattern generators, configuring OPP buffers and clocks, selecting ODM/OPTC inputs and DSC widths, enabling OTG timing, changing dynamic refresh-rate totals, handling vertical/range interrupts, using OTG triggers, synchronizing global updates, and reading CRC/status counters. The macros themselves do not enforce legal values, sequencing, read-only status semantics, or write-one-to-clear behavior.

## State And Persistence Behavior

The file stores no software state and has no persistence mechanism. It describes state held in display hardware registers.

The represented state spans several display subsystems:

- MPCC output gamma state: LUT mode, selected RAM, LUT index/data payloads, RAM A/B region segmentation, per-channel starts, slopes, end bases, and end slopes.
- MPC output CSC state: output CSC mode, coefficient format, double-buffered A/B matrix coefficient banks, and OCSC debug selection.
- OPP/FMT state: clamp bounds, dynamic expansion, pixel encoding, subsampling, truncation, spatial and temporal dithering, random seed values, 4:2:0/4:2:2 handling, pattern generator programming, OPP buffer geometry, and pipe clock state.
- ODM/OPTC state: data source routing, DSC data format and slice width, bytes-per-pixel, input clock gating/status, double-buffer pending, and underflow sticky status/clear bits.
- OTG state: active timing, blank/sync windows, trigger configuration/status, frame/line counters, vertical interrupt windows, CRC capture windows/results, static-screen counters, stereo/3D settings, global sync lock, master update locks, DRR timing bounds, request controls, and DSC start position.

Persistence is hardware-specific. Some fields are persistent programming values until reset or power gating; some are double-buffered and take effect only at a selected update point; some are live status bits; some are sticky interrupt/status bits requiring explicit clear/ack fields; and some are self-clearing trigger fields. Values can be changed by modesets, atomic commits, vblank/update-lock sequences, hotplug handling, suspend/resume, firmware/BIOS handoff, power management, or ASIC reset. This generated header does not encode those access rules.

## Dependencies

This chunk depends on the generated DCN 2.0.1 register-header ecosystem:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_offset.h` supplies matching register addresses and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn201/dcn201_resource.c` includes both offset and mask headers and declares DCN201 display-resource capabilities, including `max_num_otg = 2`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn20/dcn20_mpc.h` consumes `MPC_OUT0_CSC_*` and `MPCC_OGAM0_*` style mask/shift fields through `MPC_COMMON_MASK_SH_LIST_DCN2_0`; this chunk provides the same generated field layout for later MPCC/OPP instances.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn10/dcn10_opp.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn20/dcn20_opp.h` consume FMT, OPPBUF, OPP_PIPE, and DPG field names through `OPP_SF`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn10/dcn10_optc.h`, `dcn20_optc.h`, and `dcn201_optc.h` consume OTG and ODM fields through `SF` entries used by timing-generator code.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn201/dcn201_clk_mgr.c` also include this mask header for DCN201-specific register field access.

The generated constants assume the AMD DC register helper convention where `REGISTER__FIELD_MASK` is already positioned and `REGISTER__FIELD__SHIFT` is the low bit. Any consumer that computes `(value << SHIFT) & MASK` or extracts `(reg & MASK) >> SHIFT` depends on that invariant.

## Integration Points

The main integration point is the DCN201 display-resource construction path. `dcn201_resource.c` includes this header during resource setup, and the component factories use the selected register lists and mask/shift lists to instantiate MPC, OPP, OPTC/timing-generator, IRQ, and clock-manager objects.

MPC/MPCC integration covers plane composition and post-blend color processing. Output gamma macros are used by MPC code that programs output transfer functions and LUT RAMs. CSC macros are used by output color-space-conversion paths that program RGB/YCbCr conversion or gamut/range transformations.

OPP/FMT/DPG integration covers final pixel formatting before timing generation and link output. Formatter masks influence truncation, dithering, clamping, pixel encoding, stereo, and chroma-subsampling behavior. DPG fields support internal pattern generation for bring-up, diagnostics, and test modes. OPPBUF and OPP_PIPE fields control buffering, segmentation, and pipe clocking.

ODM/OPTC integration covers output data routing into timing generators and DSC-aware output paths. The DCN201 OPTC header directly references `ODM0_OPTC_DATA_SOURCE_SELECT`, `ODM0_OPTC_DATA_FORMAT_CONTROL`, `ODM0_OPTC_BYTES_PER_PIXEL`, and `ODM0_OPTC_WIDTH_CONTROL`, which are defined in this chunk for instances 0 and 1.

OTG integration covers modesets, vblank timing, dynamic refresh rate, global update synchronization, CRC capture, interrupts, stereo/3D state, and stream enable/disable. Runtime code in the DC timing-generator implementation updates fields such as `OTG_CONTROL.OTG_MASTER_EN`, `OTG_V_TOTAL_CONTROL`, `OTG_DOUBLE_BUFFER_CONTROL`, and `OTG_GSL_CONTROL` using masks with this naming pattern.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong mask or shift can compile cleanly while clearing the wrong bits, failing to update the intended field, corrupting adjacent fields during read-modify-write, or misreading status.

High-risk MPCC/MPC fields include output gamma LUT index/data/control, RAM A/B region descriptors, start/slope/end values, OCSC modes, coefficient formats, and packed CSC coefficients. Errors can cause wrong transfer functions, color shifts, clipping, banding, incorrect RGB/YCbCr conversion, or failed color-management programming.

High-risk OPP/FMT fields include bit-depth truncation, dither enable/depth/mode, pixel encoding, subsampling mode, 4:2:0 memory control, clamp bounds, and DPG controls. Bad constants can cause visible artifacts, wrong color range, chroma placement errors, disabled clocks, bad test patterns, or OPP underflow.

High-risk ODM/OPTC fields include segment source selection, DSC mode, DSC bytes-per-pixel, slice width, input clock enable/status, double-buffer pending, and underflow status/clear. Mistakes can route the wrong data stream into an OTG, break DSC output, leave underflow status stuck, or gate clocks unexpectedly.

OTG fields are especially sequencing-sensitive. `OTG_MASTER_EN`, sync/blank totals, DRR min/max/mid controls, trigger clear/status bits, vertical interrupt clear/status bits, CRC controls, global sync lock, master update locks, and double-buffer update modes affect live scanout. Incorrect values can cause blank display, unstable refresh timing, missed vblank interrupts, CRC test failures, deadlocks waiting for update pending bits, or hangs during enable/disable.

The repeated instance layout creates generator-copy risk. `MPCC_OGAM3` and `MPCC_OGAM4`, `FMT0` and `FMT1`, `DPG0` and `DPG1`, `ODM0` and `ODM1`, and `OTG0` and `OTG1` are mostly mirrored. A suffix mismatch can affect only one display pipe and may only surface on dual-display, ODM, or multi-pipe configurations.

This chunk starts and ends on artificial line boundaries. It begins after the earlier `MPCC_OGAM2` RAM B region table has already started, and it ends inside the `OTG1_OTG_INTERLACE_STATUS` register after the shift fields and before the remaining masks and following `OTG1` fields. The final per-file merge should treat these as chunk boundaries rather than source omissions.

## Test Signals

Useful validation is mostly compile-time, generated-register consistency, and display hardware behavior:

- Kernel/driver builds for DCN201 paths should compile all `SF`/`OPP_SF`/component register-list references that rely on this mask header.
- Generated-register validation should compare every `*_MASK` and `*__SHIFT` pair in this range against AMD's register database and the companion address definitions in `dcn_2_0_1_offset.h`.
- Color-management tests should exercise MPCC output gamma programming and MPC output CSC programming, including LUT uploads, coefficient-bank swaps, RGB/YCbCr conversion, HDR/SDR transfer behavior, and visible banding/clipping checks.
- Formatter tests should cover truncation, spatial and temporal dithering, clamping, pixel encoding, 4:2:0 and 4:2:2 modes, and side-by-side stereo where supported.
- Pattern-generator diagnostics should verify DPG enable/mode, active dimensions, color values, ramp increments, offsets, and double-buffer pending behavior.
- ODM/DSC tests should verify data source selection, DSC mode, bytes-per-pixel, slice width, segment width, input clock status, and underflow clear/status handling on both supported pipes.
- Timing tests should exercise OTG0 and OTG1 modesets across multiple timings, interlace, blanking/sync polarity, DRR, vblank interrupts, vertical interrupt windows, trigger A/B, force-count/force-vsync, CRC windows/results, master update locks, GSL, and DSC start position.
- Suspend/resume, hotplug, display blank/unblank, dual-display, and atomic modeset stress tests should not leave OTG update locks pending, clocks gated incorrectly, underflow bits stuck, or scanout enabled with stale timing.

Regression symptoms from bad constants include blank or flickering display, wrong colors or gamma, visible dithering artifacts, failed DSC modes, underflow storms, missed vblank/range interrupts, CRC mismatches, DRR instability, stuck update-pending waits, failed dual-pipe/ODM routing, or behavior that fails only on the second OTG/OPP/ODM instance.

## Cross-Chunk Notes

Earlier chunks of `dcn_2_0_1_sh_mask.h` define preceding DCN201 display register mask families and the beginning of `MPCC_OGAM2`. Later chunks complete `OTG1_OTG_INTERLACE_STATUS` and continue through the rest of the `OTG1` and subsequent DCN register field families. The final per-file report should describe this source as one generated DCN201 hardware layout contract rather than as algorithmic driver code.
