# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h lines 5583-8099

## Purpose

This chunk is part of the generated AMDGPU DCN 4.2.0 register-offset header. It defines C preprocessor constants that map display hardware register names to numeric offsets, plus a paired `_BASE_IDX` constant for each register. The values are consumed by DCN 4.2 display code to compute MMIO addresses as `BASE(reg..._BASE_IDX) + reg...`, using the matching `dcn_4_2_0_sh_mask.h` field definitions when individual bitfields are read or written.

The range contains constants only. There are no functions, structs, enums, branches, loops, allocation paths, or direct persistence operations in these lines. Its behavioral role is nevertheless critical: it is the register-address contract for the third HUBP pipe, all visible DPP pipes 0-2, and the beginning of DPP pipe 3.

The requested boundaries are not semantic boundaries. The chunk starts at the tail of `HUBPREQ2`, after earlier `HUBPREQ2` surface and timing registers, and ends inside the `CM3` gamma-correction RAM A sequence at `regCM3_CM_GAMCOR_RAMA_OFFSET_B`; later `CM3` gamma, histogram, memory-power, and debug registers are outside this chunk.

## Covered Register Blocks

The chunk defines 1,197 register-offset constants and 1,196 paired `_BASE_IDX` constants. Every paired base index visible in this range is `2`, meaning the register offset must be resolved through DCN base segment index 2. The only unpaired offset at the exact chunk end is `regCM3_CM_GAMCOR_RAMA_OFFSET_B`, because its `_BASE_IDX` line falls after line 8099.

- Tail of `HUBPREQ2`: `regHUBPREQ2_FLIP_PARAMETERS_5`, `regHUBPREQ2_FLIP_PARAMETERS_6`, `regHUBPREQ2_UCLK_PSTATE_FORCE`, and `regHUBPREQ2_HUBPREQ_STATUS_REG0..2`.
- `HUBPRET2` at address block `dce_dc_dcbubp2_dispdec_hubpret_dispdec`, base `0x6e0`: HUBP return control, memory-power control/status, read-line control, interrupt, read-line value, and status.
- `CURSOR0_2` at address block `dce_dc_dcbubp2_dispdec_cursor0_dispdec`, base `0x6e0`: cursor control, address high/low, size, position, hot spot, stereo control, destination offset, cursor memory power/status, DMDATA programming, and HUBP 3D LUT address/control/DLG parameter registers.
- `DC_PERFMON8` at address block `dce_dc_dcbubp2_dispdec_hubp_dcperfmon_dc_perfmon_dispdec`, base `0x2154`: performance-counter control, state, counter-value, high, and low registers for the pipe-2 HUBP/perfmon block.
- `HUBP3`, `HUBPREQ3`, `HUBPRET3`, `CURSOR0_3`, and `DC_PERFMON9`: the corresponding pipe-3 fetch, request, return, cursor, DMDATA, 3D LUT, and performance-monitor register blocks. `HUBPREQ3` is the largest HUBP block in this chunk, covering surface pitch, VMID, primary/secondary and chroma luma/meta addresses, flip control, in-use/earliest-in-use readbacks, TTU/QoS, VM aperture/TLB controls, prefetch/vblank/flip/nominal timing parameters, per-line delivery, cursor settings, memory power, UCLK pstate force, and status registers.
- DPP pipe 0 through pipe 2 complete visible groups: `DPP_TOP0..2`, `CNVC_CFG0..2`, `CM_CUR0..2`, `DSCL0..2`, `CM0..2`, and `DC_PERFMON10..12`.
- DPP pipe 3 partial groups: complete `DPP_TOP3`, `CNVC_CFG3`, `CM_CUR3`, and `DSCL3`, followed by the beginning of `CM3` through gamma-correction RAM A offset B.

## Important APIs, Types, and Macros

There are no callable APIs or types in this header slice. The important interface is the generated macro namespace:

- `reg<block>_<register>` expands to a register offset. Examples include `regHUBPREQ3_DCSURF_PRIMARY_SURFACE_ADDRESS`, `regDSCL2_SCL_MODE`, `regCM0_CM_GAMCOR_LUT_DATA`, and `regCM3_CM_CONTROL`.
- `reg<block>_<register>_BASE_IDX` expands to the base segment selector. In this chunk the visible base index value is consistently `2`.
- Address-block comments such as `// addressBlock: dce_dc_dpp2_dispdec_dscl_dispdec` and `// base address: 0xb58` document the generated hardware block grouping but do not create C symbols.
- DCN 4.2 consumers include `display/dmub/src/dmub_dcn42.c`, `display/dc/resource/dcn42/dcn42_resource.c`, `display/dc/irq/dcn42/irq_service_dcn42.c`, `display/dc/clk_mgr/dcn42/dcn42_clk_mgr.c`, and DCN 4.2 GPIO translation/factory code, all of which include this offset header with the companion shift/mask header.

The broader AMD display code uses helper macros such as `REG_OFFSET_EXP(reg_name) (BASE(reg##reg_name##_BASE_IDX) + reg##reg_name)` and service macros in `dm_services.h` to translate these generated constants into MMIO addresses for register reads, writes, and masked updates.

## Control Flow and Runtime Use

This chunk has no local control flow. Runtime behavior appears when DCN resource construction and block-specific programming tables paste logical register names onto these generated symbols:

1. A DCN 4.2 component includes `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h`.
2. Register-list macros or per-block register structs select an instance, such as HUBP3, DSCL1, or CM2.
3. The register access helper combines `BASE(reg..._BASE_IDX)` with the `reg...` offset and writes fields using masks from the shift/mask header.
4. Hardware consumes the resulting MMIO programming on update, flip, clock, memory-power, or vblank boundaries, depending on the block.

The most important programming sequences represented by this range are:

- HUBP fetch setup: surface format and tiling are partly outside this chunk for pipe 2, but pipe 3 includes surface address, pitch, viewport, request sizing, VM/TLB, flip, TTU, prefetch, and status addresses needed to fetch scanout surfaces and cursor/DMDATA payloads.
- Cursor setup: `CURSOR0_2` and `CURSOR0_3` provide cursor surface addresses, dimensions, position, hot spot, stereo, and memory-power status offsets.
- DPP conversion and cursor color setup: `CNVC_CFG*` registers cover pixel format, fixed-point bias/scale, color keying, alpha LUTs, pre-dealpha, pre-CSC matrix A/B, coefficient format, pre-degamma, and pre-realpha. `CM_CUR*` covers cursor color and cursor matrix registers inside the DPP color path.
- Scaling and sharpening: `DSCL0..3` cover coefficient RAM access, scaler mode, tap control, 2-tap/manual replicate controls, luma/chroma ratios and initial phases, black color, update/autocal, overscan, OTG blanking, recout/MPC size, line-buffer data/memory/counter registers, scaler and output-buffer memory power, EASF modes and ring-estimator controls, bilateral-filter PWL segments, image-sharpening mode/delta/noise/LBA controls, and sharpen delta LUT memory power.
- Color management: `CM0..2` are complete in this chunk for post-CSC, bias, gamma-correction LUT and RAM A/B region metadata, HDR multiplier, memory-power/status, dealpha, coefficient format, test-debug, and histogram control/data/status/interrupt registers. `CM3` begins the same pattern but stops during gamma-correction RAM A.
- Perfmon: `DC_PERFMON8..12` expose performance-counter control, state, current value, high, and low registers for HUBP and DPP instances represented here.

## State and Persistence Behavior

The macros themselves are compile-time constants and hold no state. They describe hardware state locations:

- Surface state lives in HUBP/HUBPREQ registers: current and earliest in-use surface addresses, flip-control registers, VM aperture/TLB registers, and timing parameters.
- Cursor and DMDATA state lives in cursor address/control/status registers and may reference GPU memory through programmed addresses.
- Memory-power state is controlled and observed through `*_MEM_PWR_CTRL` and `*_MEM_PWR_STATUS` registers for HUBPREQ, HUBPRET, cursor, DSCL, OBUF, CM, and sharpen LUT memories.
- DPP color and scaler state is stored in hardware registers and indexed LUT memories. Gamma-correction LUT, CM histogram, DSCL coefficient RAM, EASF PWL, and sharpen delta controls must be reprogrammed after hardware reset or power gating if the hardware does not retain them.
- Perfmon counters are transient hardware counters; offset mistakes affect observability rather than persistent storage.

No filesystem or driver-private persistent data is created by this header. Persistence across suspend/resume depends on higher-level DCN state reconstruction using these addresses.

## Dependencies and Integration Points

This file depends on the generated DCN base-address model used by AMD display register helpers. The `_BASE_IDX` constants must match `DCE_BASE` segment definitions and the ASIC's register aperture layout. A wrong base index can redirect otherwise-correct offsets into the wrong MMIO segment.

The field-level interpretation depends on `dcn_4_2_0_sh_mask.h`. Offset and mask headers must be generated from the same register database; mixing DCN 4.2 offsets with a different generation's masks can compile but program incorrect fields.

Integration points include:

- DCN 4.2 DMUB register tables in `display/dmub/src/dmub_dcn42.c`.
- DCN 4.2 display resource construction in `display/dc/resource/dcn42/dcn42_resource.c`.
- DCN 4.2 interrupt, clock manager, and GPIO code that include this header for register access.
- Shared display block implementations for HUBP/HUBPREQ/HUBPRET, DPP top, CNVC, CM cursor, DSCL, CM, and perfmon that are parameterized by generated register tables.
- The Linux AMDGPU display mode-setting path, which ultimately exercises these constants through plane updates, flips, cursor movement, scaling, color management, power management, and debug/perfmon paths.

## Risks and Edge Cases

- Chunk-boundary incompleteness is significant. The first six lines are only the tail of `HUBPREQ2`; the end omits the `_BASE_IDX` for `regCM3_CM_GAMCOR_RAMA_OFFSET_B` and all later `CM3` registers. The merge lane must combine adjacent chunks before making whole-block claims.
- Repeated instance families invite generator or manual-review errors. `HUBP3` must stay paired with `HUBPREQ3`, `HUBPRET3`, `CURSOR0_3`, and `DC_PERFMON9`; DPP instances must keep `DPP_TOPn`, `CNVC_CFGn`, `CM_CURn`, `DSCLn`, `CMn`, and `DC_PERFMON10+n` aligned.
- Offset gaps are intentional in generated hardware maps, for example gaps in `HUBPREQ3` around `DCSURF_FLIP_CONTROL2` to `DCSURF_SURFACE_FLIP_INTERRUPT` and VM aperture/TLB ranges. Treating the list as densely sequential can create false positives in validation scripts.
- Address reuse across logical subregister names is possible elsewhere in the file and should not be normalized away. This chunk primarily presents one offset per visible register symbol, but the generated style relies on symbol identity, not just numeric uniqueness.
- A bad surface-address, pitch, or VM offset can cause scanout corruption, GPU VM faults, black screens, stale flips, or failures isolated to pipe 3.
- A bad scaler, CNVC, or CM offset can produce wrong scaling, clipped or shifted image geometry, bad color conversion/gamma, broken cursor color conversion, histogram readback errors, or DPP CRC mismatches.
- A bad memory-power offset can cause hangs waiting for status convergence, lost LUT contents after power gating, or resume-only display failures.
- A wrong perfmon offset can silently corrupt diagnostics by reading counters from the wrong block.

## Test Signals

Useful validation signals for changes touching these constants include:

- Build coverage for DCN 4.2 display code with both `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h` included, catching missing symbols such as an omitted `_BASE_IDX`.
- Register-table sanity checks that every `reg...` used by DCN 4.2 resource, DMUB, IRQ, clock, GPIO, HUBP, DPP, DSCL, CM, and perfmon code has a matching base index in the full file.
- Plane modeset and page-flip tests on configurations that use HUBP/DPP instance 3, including luma/chroma formats, meta surfaces, VM-backed scanout, SubVP/MALL paths, vblank flips, and UCLK pstate transitions.
- Cursor tests on pipes 2 and 3 covering movement, hot spot, large cursor sizes, stereo fields where supported, and cursor memory power transitions.
- Scaling tests across DPP0-3, including luma/chroma scaling, tap changes, overscan, recout/MPC sizing, line-buffer partitioning, EASF/sharpening paths, and suspend/resume after scaler memory power transitions.
- Color-management tests for DPP0-2 complete CM blocks and the early CM3 path: pre/post CSC, gamma-correction LUT programming, HDR multiplier, dealpha, coefficient-format changes, histogram readback/interrupts, and DPP CRC comparison against expected output.
- Perfmon smoke tests that program `DC_PERFMON8..12`, read low/high/current counter values, and verify counters correspond to the expected HUBP/DPP instance.
