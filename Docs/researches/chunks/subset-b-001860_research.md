# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h lines 2653-5162

## Scope And Purpose

This chunk is part of the generated AMD DCN 3.1.5 register-offset header. It exports C preprocessor constants that map named display-controller registers to MMIO offsets, paired one-for-one with `<register>_BASE_IDX` constants. The companion `dcn_3_1_5_sh_mask.h` header supplies field shifts and masks; this file supplies the register addresses that DCN 3.1.5 resource construction expands into hardware-block register tables.

The requested range contains 1,197 register-offset macros and 1,197 matching base-index macros. It has partial logical boundaries. It starts at the `_BASE_IDX` half of `regHUBPREQ1_DCSURF_FLIP_CONTROL2`, so the matching offset define is in the previous chunk. It then covers the remainder of HUBP1 request-side flip/in-use/timing offsets, complete HUBPRET1, CURSOR0_1, and HUBP perfmon 8 blocks; complete HUBP/HUBPREQ/HUBPRET/CURSOR/perfmon blocks for HUBP2 and HUBP3; complete DPP0 and DPP1 converter, scaler, color-management, top, and perfmon blocks; complete DPP2 converter and scaler blocks; and the beginning of DPP2 color-management offsets through `regCM2_CM_GAMCOR_RAMB_REGION_14_15`.

There are no functions, structs, branches, loops, or direct runtime side effects in this range. Its exported surface is generated register metadata. Runtime behavior appears when DCN 3.1.5 code includes this header, expands register-list macros such as `HUBP_REG_LIST_DCN30(id)` and `DPP_REG_LIST_DCN30(id)`, and later uses `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and related helpers through block-specific register structures.

## Register Blocks Covered

The range begins in the middle of `dce_dc_dcbubp1_dispdec_hubpreq_dispdec`, whose address-block comment is before the requested line window. The covered HUBPREQ1 tail includes surface flip interrupt, surface in-use and earliest-in-use addresses for luma and chroma, DCN expansion mode, TTU/QoS controls, VM system aperture, MX L1 TLB control, blank and destination timing, prefetch settings, vblank, flip, nominal delivery parameters, cursor settings, reference-to-pixel frequency, destination DRQ limit, HUBPREQ memory-power control/status, and additional vblank/flip VM request/group parameters.

`dce_dc_dcbubp1_dispdec_hubpret_dispdec` at base address `0x370` covers HUBPRET1 control, memory-power control/status, read-line controls, read-line values, interrupt state, and read-line status.

`dce_dc_dcbubp1_dispdec_cursor0_dispdec` at base address `0x370` covers the HUBP1 cursor and cursor-side dynamic-metadata registers: cursor control, surface address low/high, size, position, hot spot, stereo control, destination offset, cursor memory-power control/status, DMDATA address high/low, DMDATA control, QoS, status, software control, and software data.

`dce_dc_dcbubp1_dispdec_hubp_dcperfmon_dc_perfmon_dispdec` at base address `0x1de4` covers DC perfmon 8 for the HUBP1 side: counter control, secondary counter control, counter state, perfmon control, secondary perfmon control, test debug index/data, high readback, and low readback.

`dce_dc_dcbubp2_dispdec_hubp_dispdec` at base address `0x6e0` covers HUBP2 core registers: surface config, tiling and address config, viewport start/dimension for primary/secondary luma and chroma planes, request-size config for luma/chroma, HUBP control, clock control, underflow debug, and measurement-window controls for DCFCLK and DPPCLK.

`dce_dc_dcbubp2_dispdec_hubpreq_dispdec` at base address `0x6e0` covers the full HUBPREQ2 request-side address surface. This includes pitches, primary/secondary surface and metadata addresses for luma and chroma, surface control, flip controls, flip interrupt, in-use and earliest-in-use addresses, expansion, TTU/QoS, DMDATA VM control, system aperture, TLB control, blank/destination/prefetch parameters, vblank/flip/nominal timing parameters, delivery timing, cursor settings, refclk-to-pixel ratio, destination DRQ limit, memory-power state, and VM-specific vblank/flip extension registers.

`dce_dc_dcbubp2_dispdec_hubpret_dispdec`, `dce_dc_dcbubp2_dispdec_cursor0_dispdec`, and `dce_dc_dcbubp2_dispdec_hubp_dcperfmon_dc_perfmon_dispdec` mirror the HUBPRET1, cursor, and perfmon shapes for HUBP2, with DC perfmon 9 at base address `0x2154`.

`dce_dc_dcbubp3_dispdec_hubp_dispdec`, `dce_dc_dcbubp3_dispdec_hubpreq_dispdec`, `dce_dc_dcbubp3_dispdec_hubpret_dispdec`, `dce_dc_dcbubp3_dispdec_cursor0_dispdec`, and `dce_dc_dcbubp3_dispdec_hubp_dcperfmon_dc_perfmon_dispdec` mirror the HUBP2 groups for HUBP3 at base address `0xa50`, with DC perfmon 10 at base address `0x24c4`.

`dce_dc_dpp0_dispdec_cnvc_cfg_dispdec` at base address `0x0` covers DPP0 converter configuration: surface pixel format, format control, alpha LUT, floating-point bias/scale per channel, pre-degamma, color-keyer controls and color values, pre-dealpha, pre-realpha, pre-CSC mode and matrix registers, and the B-matrix variants.

`dce_dc_dpp0_dispdec_cnvc_cur_dispdec` covers DPP0 CNVC cursor composition state: cursor control, cursor color 0/1, and cursor floating-point scale/bias.

`dce_dc_dpp0_dispdec_dscl_dispdec` covers DPP0 scaler and line-buffer state: scaler coefficient RAM select/data, mode, LB data format and memory control, horizontal/vertical blank timing, overscan, autocal, DSCL control, tap control, two-tap control, MPC size, horizontal/vertical scale ratios and initial phases for luma/chroma, recout start/size, DSCL memory-power status/control, and output-buffer memory-power control.

`dce_dc_dpp0_dispdec_cm_dispdec` covers the full DPP0 color-management address set. It includes CM control, post-CSC matrices and B-matrices, gamut remap matrices and B-matrices, bias registers, GAMCOR control/LUT index/data/LUT control, GAMCOR RAM A and RAM B start/slope/base/end/offset/region registers for B/G/R channels, blend-gamma control and LUT registers, blend-gamma RAM A/B start-slope registers, memory-power control/status pairs, CM dealpha, HDR multiplier coefficients, shaper LUT index/data/control, shaper controls and offsets, 3D LUT controls, 3D LUT memory offsets, 3D LUT read/write data and index registers, 3D LUT mode and transfer controls, 3D LUT debug, 3D LUT memory-power control/status, and CM test-debug index/data.

`dce_dc_dpp0_dispdec_dpp_top_dispdec` covers DPP0 top-level controls: DPP control, CRC control, CRC value pairs, debug control, and host read control. `dce_dc_dpp0_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` covers DC perfmon 11.

DPP1 blocks at base address `0x5ac` mirror DPP0: `CNVC_CFG1`, `CNVC_CUR1`, `DSCL1`, `CM1`, `DPP_TOP1`, and DC perfmon 12.

DPP2 blocks at base address `0xb58` begin with complete `CNVC_CFG2`, `CNVC_CUR2`, and `DSCL2` register groups, then enter `dce_dc_dpp2_dispdec_cm_dispdec`. The covered CM2 portion includes CM control, post-CSC and gamut-remap matrices/B-matrices, bias, GAMCOR control/LUT registers, GAMCOR RAM A start/slope/base/end/offset/region registers, and the beginning of GAMCOR RAM B through `CM_GAMCOR_RAMB_REGION_14_15`. The remaining CM2 region registers, blend-gamma, shaper, 3D LUT, memory-power, DPP_TOP2, and DPP2 perfmon offsets continue after this chunk.

## Important APIs, Types, And Macros

The important API is the generated naming contract:

- `reg<register_name>` gives the register offset inside the selected DCN 3.1.5 base segment.
- `reg<register_name>_BASE_IDX` gives the segment/base index passed through the local `BASE()` macro in `dcn315_resource.c`.
- Address-block comments such as `// addressBlock: dce_dc_dcbubp2_dispdec_hubpreq_dispdec` and `// base address: 0x6e0` delimit generated hardware address windows.
- Instance prefixes are part of the ABI between generated headers and resource code: `HUBP1` through `HUBP3`, `HUBPREQ1` through `HUBPREQ3`, `HUBPRET1` through `HUBPRET3`, `CURSOR0_1` through `CURSOR0_3`, `CNVC_CFG0` through `CNVC_CFG2`, `CNVC_CUR0` through `CNVC_CUR2`, `DSCL0` through `DSCL2`, `CM0` through the covered portion of `CM2`, `DPP_TOP0`/`DPP_TOP1`, and `DC_PERFMON8` through `DC_PERFMON12`.

`display/dc/resource/dcn315/dcn315_resource.c` is the main consumer. It includes `dcn/dcn_3_1_5_offset.h` and `dcn/dcn_3_1_5_sh_mask.h`, defines `BASE(seg)` over `DCN_BASE__INST0_SEG*`, and uses `SR()`/`SRI()` style macros to turn generated register offsets into absolute register addresses. In this file, `hubp_regs(id)` expands `HUBP_REG_LIST_DCN30(id)` for four HUBP instances, and `dpp_regs(id)` expands `DPP_REG_LIST_DCN30(id)` for four DPP instances.

`display/dc/hubp/dcn30/dcn30_hubp.h` defines `HUBP_REG_LIST_DCN30(id)` as `HUBP_REG_LIST_DCN21(id)` plus `SRI(DCN_DMDATA_VM_CNTL, HUBPREQ, id)`. Its field list, extended by `display/dc/hubp/dcn31/dcn31_hubp.h`, maps these offsets to HUBP programming fields for surface format, tiling, viewport, addresses, flip, update lock, request sizing, DLG/TTU delivery, VM system aperture, DMDATA, cursor, underflow, and read-line state.

`display/dc/dpp/dcn30/dcn30_dpp.h` defines `DPP_REG_LIST_DCN30(id)`. This macro binds the DPP-side offsets in this chunk to the `dcn3_dpp` register structure: CNVC format/color-key/pre-CSC registers, CNVC cursor registers, DSCL scaler registers, CM post-CSC/gamut/gamma/shaper/3D-LUT registers, DPP top registers, and memory-power/status registers.

The runtime constructors are `hubp31_construct()` and `dpp3_construct()`, invoked from `dcn31_hubp_create()` and `dcn31_dpp_create()` in `dcn315_resource.c`. These constructors receive `&hubp_regs[inst]` or `&dpp_regs[inst]` plus the companion shift/mask tables, then install function tables used by DC modeset, plane update, cursor update, color pipeline, scaling, and validation paths.

`display/dmub/src/dmub_dcn315.c`, `display/dc/irq/dcn315/irq_service_dcn315.c`, and DCN315 GPIO translation/factory files also include the DCN 3.1.5 generated headers. This particular chunk is most directly tied to HUBP and DPP resource tables, but the same generated address namespace is shared across DMUB services, IRQ tables, GPIO translation, and hardware diagnostics.

## Functional Behavior Represented By The Registers

The HUBP/HUBPREQ/HUBPRET groups represent the memory-fetch side of display pipes. HUBP core registers describe surface layout, tiling, viewport, request size, clocking, underflow state, and pipe measurement windows. HUBPREQ registers describe address, flip, VM, prefetch, vblank, nominal, flip, TTU/QoS, and delivery timing state. HUBPRET registers cover return/read-line controls and DET-buffer routing details. Together these offsets back plane scanout, DCC/meta-surface fetch, luma/chroma handling, cursor timing alignment, VM aperture configuration, underflow detection, and watermarked delivery scheduling.

The CURSOR0_x blocks describe cursor fetch and dynamic metadata state associated with each HUBP instance. The cursor registers hold the cursor memory address, size, position, hot spot, format/control, destination offsets, memory-power state, and DMDATA programming/status. These registers integrate with atomic cursor updates and with hardware-assisted metadata paths that are synchronized to a pipe.

The HUBP perfmon blocks expose per-HUBP diagnostic counters. They provide counter selection/control, state, threshold/control, test-debug access, and high/low readback. They are not normal scanout configuration, but they are useful for bring-up, performance validation, and underflow or bandwidth investigations.

The CNVC_CFG and CNVC_CUR blocks are the DPP converter front end. They define source pixel format, fixed/floating conversion bias and scale, alpha conversion, color keying, pre-degamma, pre-dealpha/pre-realpha, pre-CSC matrix programming, and DPP-side cursor composition color/scale/bias. These offsets are used before scaling and color-management operations.

The DSCL blocks are the DPP scaler and line-buffer address surface. They include coefficient RAM selection/data, scaler mode, tap counts, two-tap sharpness controls, scale ratios and initial phases for luma/chroma, line-buffer format and memory control, overscan, recout, MPC output size, blank timing, autocal controls, and DSCL memory-power state.

The CM blocks are the DPP color pipeline. Covered registers represent post-CSC, gamut remap, channel bias, GAMCOR LUT programming, piecewise-linear RAM A/B region definitions, blend-gamma, shaper LUT, 3D LUT, HDR multiplier, dealpha, memory power, current-mode status, and debug access. DPP0 and DPP1 are complete in this chunk; DPP2 CM is only partially covered.

The DPP_TOP blocks expose top-level DPP enable/control, CRC generation, CRC result readback, debug, and host-read control. DPP perfmon blocks mirror the generic DC perfmon shape for DPP-side performance instrumentation.

## Control Flow And State Behavior

This header has no direct control flow. Runtime flow is table driven: DCN315 resource construction expands generated offset macros into register-address structures, constructs HUBP and DPP objects for each instance, and the display core later calls block methods that perform MMIO reads/writes through those structures.

Most state described here is persistent hardware register state. Surface addresses, pitches, tiling, viewport dimensions, VM aperture limits, scaler coefficients, scale ratios, CSC/gamut matrices, gamma/shaper/3D-LUT data, cursor addresses, memory-power controls, DPP top state, and perfmon selections persist until changed by the driver, reset, power-gated, or overwritten by firmware/hardware sequencing.

Status and telemetry registers are live hardware state. Examples include surface in-use and earliest-in-use addresses, flip pending/update lock status, HUBP underflow status, no-outstanding-request state, read-line values, cursor DMDATA done/status, memory-power status, current color-mode fields, CRC readback, and perfmon counter values.

Several programming paths are ordering-sensitive. Surface updates and flips must coordinate address registers, flip-control state, update locks, VMIDs, and timing windows. DLG/TTU parameters must match the mode and bandwidth calculations or scanout can underflow. Cursor updates must program address/size/position/hot spot coherently. DSCL programming must load coefficient RAM and scaler ratios in the right mode. CM LUT and 3D-LUT updates must select the correct host side, index, bank/RAM, and control mode. Memory-power controls must respect block idle and status bits.

State is distributed across blocks. One display pipe can involve HUBP fetch/register state, DPP converter/scaler/color state, MPC/OPP/OTG state outside this range, and DMUB or IRQ paths that observe or update adjacent state. Correct behavior depends on per-instance register tables preserving the intended pipe mapping.

## Dependencies And Integration Points

This chunk depends on `dcn_3_1_5_sh_mask.h` staying synchronized with the offsets. Offset macros choose the MMIO register; shift/mask macros choose fields inside that register. A mismatch can compile if symbol names still exist but write the wrong register or wrong field.

The DCN315 resource pool is the primary integration point. `dcn315_resource.c` creates four HUBPs and four DPPs; this chunk supplies most of the generated address constants for HUBP1-HUBP3, DPP0-DPP1, and the covered portion of DPP2. Constructor calls such as `hubp31_construct(... &hubp_regs[inst], &hubp_shift, &hubp_mask)` and `dpp3_construct(... &dpp_regs[inst], &tf_shift, &tf_mask)` turn this generated data into operational hardware blocks.

The HUBP path integrates with plane addressing, tiling, DCC/meta-surface programming, VM setup, vblank/flip watermarks, cursor fetch, dynamic metadata, and underflow handling. Higher-level code computes DLG/TTU/RQ parameters from the Display Mode Library and then programs the HUBPREQ timing registers covered here.

The DPP path integrates with source format conversion, scaling, cursor composition, color management, HDR/gamma programming, CRC/debug, and DPP memory-power management. Higher-level color code relies on the DPP CM register map for post-CSC, gamut, gamma, shaper, and 3D LUT programming.

The diagnostic path integrates through DC perfmon and CRC registers. HUBP perfmon 8-10 and DPP perfmon 11-12 can be selected and read by debug or validation tooling, while DPP_TOP CRC controls/results can validate DPP output data.

The DMUB path includes the same generated header in `dmub_dcn315.c`. Even when not every macro in this chunk is used directly in the DMUB register table, DMUB firmware commands for cursor, power, replay/PSR, or diagnostic interactions operate in the same generated DCN315 register namespace.

The IRQ path includes the same offset/mask pair in `irq_service_dcn315.c`. HUBP flip interrupts, underflow conditions, or other DCN315 IRQ sources rely on generated addresses and masks matching hardware.

## Risks And Edge Cases

The highest risk is generated-header drift from the silicon register specification or from the companion sh/mask header. Wrong offsets can produce valid C builds that program the wrong MMIO address. In this range, visible failures can include black screens, plane corruption, incorrect color, broken scaling, cursor corruption, flip stalls, underflows, invalid DCC/meta-surface fetches, wrong VM fault reporting, or misleading perfmon/CRC data.

Partial boundaries matter for reconciliation. The first line is only `regHUBPREQ1_DCSURF_FLIP_CONTROL2_BASE_IDX`; the matching offset define is before the chunk. The DPP2 CM block is incomplete at the end; later region, blend-gamma, shaper, 3D LUT, memory-power, DPP_TOP2, and DPP2 perfmon offsets are outside this chunk. A merged per-file report should combine adjacent chunks before making complete claims about HUBPREQ1 or DPP2.

Instance ordering is a recurring edge case. DCN315 arrays construct HUBPs and DPPs by instance index. If `HUBP2`/`HUBP3`, `CM1`/`CM2`, `DSCL1`/`DSCL2`, or related base offsets are shifted, the driver can program a different pipe than intended while the code still compiles.

Surface-flip state is sensitive. Address, meta-address, in-use, earliest-in-use, flip-control, VMID, and update-lock registers must agree with the atomic plane update sequence. A wrong address or stale flip/control register can produce tearing, stuck flips, wrong-buffer scanout, or hard-to-debug intermittent corruption.

Bandwidth and timing state is dense. HUBPREQ vblank, flip, nominal, TTU, prefetch, delivery, and DRQ-limit registers are populated from mode and bandwidth calculations. Incorrect offsets or fields can cause underflow only under specific modes, scaling ratios, memory clocks, cursor usage, or multi-plane composition.

Cursor and DMDATA programming crosses HUBP and DPP concepts. HUBP cursor fetch registers and DPP CNVC cursor composition registers both appear in this range. A mismatch between cursor fetch position/address and DPP cursor conversion/composition state can create cursors with correct memory but wrong placement, format, colors, or timing.

Color-management programming is banked and stateful. GAMCOR RAM A/B, shaper LUT, blend-gamma LUT, and 3D LUT registers require correct index/data/control sequencing. Errors may appear as subtle color inaccuracies, HDR regressions, or broken color-management transitions rather than obvious faults.

Memory-power controls can mask register programming bugs. HUBPREQ, HUBPRET, cursor, DSCL, CM, GAMCOR, 3D LUT, and DPP-related memory-power status/control registers appear in this chunk. Writes made while a block memory is powered down, or reads interpreted without checking status, can create intermittent failures around idle, suspend/resume, or power-gating transitions.

Perfmon and CRC registers are diagnostic state. They can contain stale values unless selected, cleared, enabled, and read in the correct order. Bad offsets may primarily affect validation and debug signal quality rather than immediate display output.

## Test Signals

Build-time coverage should catch missing or renamed generated macros in `dcn315_resource.c`, `dcn30_hubp.h`, `dcn31_hubp.h`, `dcn30_dpp.h`, `dmub_dcn315.c`, and `irq_service_dcn315.c`. High-signal failures include unresolved `regHUBP*`, `regHUBPREQ*`, `regHUBPRET*`, `regCURSOR0_*`, `regCNVC_CFG*`, `regCNVC_CUR*`, `regDSCL*`, `regCM*`, `regDPP_TOP*`, or `regDC_PERFMON*` symbols.

Plane scanout validation should exercise all physical HUBP/DPP instances available on DCN315, including single-plane, multi-plane, luma/chroma formats, DCC-enabled surfaces, rotated or mirrored surfaces, stereo/secondary viewport paths where supported, and repeated atomic flips. Useful signals are successful modesets, correct surface content, no underflow interrupts, correct in-use address readback, and bounded flip latency.

VM and memory-fetch validation should cover VM system aperture programming, VMID selection, DMDATA VM control, surface/meta-address updates, prefetch and delivery timing under multiple memory-clock states, and suspend/resume. Good signals are no VM fault/underflow/late status, no stale DMDATA done state, and clean recovery after power transitions.

Cursor validation should cover cursor enable/disable, position and hot spot changes, size/pitch/mode variants, high/low address changes, stereo/destination offsets where supported, DPP cursor color and FP scale/bias, and cursor updates during flips. Signals include correct cursor shape/color/position and no corruption during rapid updates.

Scaler validation should cover unity scaling, upscaling, downscaling, chroma scaling, overscan, recout changes, coefficient RAM programming, two-tap paths, and line-buffer memory-power transitions. Expected signals are correct output geometry, no scaler artifacts, and stable behavior across mode changes.

Color validation should cover pre-CSC, post-CSC, gamut remap, GAMCOR RAM A/B, blend gamma, shaper LUT, 3D LUT, HDR multiplier, dealpha, and memory-power transitions on DPP0/DPP1 and on DPP2 once the later chunk is merged. High-value signals are deterministic register dumps, expected CRC changes, and colorimetry or pixel-capture matches against known test patterns.

Diagnostic validation should exercise HUBP perfmon 8-10, DPP perfmon 11-12, and DPP_TOP CRC controls/readbacks. Tests should explicitly clear/select/enable/read counters and CRCs to avoid stale values, and should verify that per-instance counters change only for the active pipe.
