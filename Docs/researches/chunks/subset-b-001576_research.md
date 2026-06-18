# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h lines 2771-5323

## Scope And Purpose

This chunk is part 2 of the generated DCN 1.0 register offset header for the AMDGPU display driver. It contains C preprocessor constants mapping DCN display-controller register names to register offsets and base-segment indices. The chunk is not executable code; it is a hardware address contract consumed by AMD Display Core resource construction code to build per-block MMIO register tables.

The visible range starts mid-HUBPREQ1 with a trailing `mmHUBPREQ1_DST_AFTER_SCALER_BASE_IDX` from the previous chunk, then covers the remaining HUBPREQ1 prefetch/timing registers, HUBPRET1, CURSOR1, HUBP/HUBPREQ/HUBPRET/CURSOR instances 2 and 3, DPP instances 0 through most of 3, DSCL scaler blocks, CNVC input pixel/cursor blocks, CM color-management blocks, and DC perfmon blocks up through `mmCM3_CM_DENORM_CONTROL`. The next chunk continues at line 5324 with the rest of the DPP3 CM/perfmon register map.

Within this range there are 2,411 `#define mm...` entries: 1,205 register offset constants and 1,206 `_BASE_IDX` constants. The one-extra base-index definition is caused by the chunk boundary starting at the base index for `mmHUBPREQ1_DST_AFTER_SCALER`, whose offset is in the previous chunk.

## Register Families Covered

The chunk is organized by generated `addressBlock` comments and repeated instance prefixes:

- `HUBPREQ1` tail: prefetch settings, vblank/nominal delivery parameters, per-line delivery, cursor settings, reference-to-pixel frequency conversion, and HUBPREQ memory power control/status.
- `HUBPRET1`, `HUBPRET2`, `HUBPRET3`: request-return/read-line control, read-line values/status, interrupts, and memory power control/status.
- `CURSOR1`, `CURSOR2`, `CURSOR3`: cursor surface address high/low, size, position, hot spot, stereo control, destination offset, and cursor memory power status/control.
- `HUBP2` and `HUBP3`: surface config, address/tiling config, primary/secondary luma/chroma viewports, request-size config, HUBP control/clock, VMPG config, debug registers, and clock measurement windows.
- `HUBPREQ2` and `HUBPREQ3`: surface pitch, primary/secondary luma/chroma addresses, meta-surface addresses, flip/surface control, in-use and earliest-in-use addresses, TLB/VM aperture registers, TTU/QoS programming, blank/destination geometry, prefetch and delivery programming, and memory power control/status.
- `DPP_TOP0` through `DPP_TOP3`: DPP control and host read control.
- `CNVC_CFG0` through `CNVC_CFG3`: format control and surface pixel format.
- `CNVC_CUR0` through `CNVC_CUR3`: cursor color/control and FP scale/bias registers.
- `DSCL0` through `DSCL3`: scaler coefficient RAM selection/data, overscan, output timing blanking, line-buffer format/memory, autocal, tap counts, 2-tap controls, scaler mode, filter ratios/initial conditions, recout/MPC size, and DSCL memory power control/status.
- `CM0`, `CM1`, `CM2`, and most of `CM3`: gamut remap, input/output color-space conversion matrices, degamma and regamma LUT controls, piecewise-linear region descriptors for R/G/B RAM A/B banks, bias/scale, HDR multiplier, clamp/denorm/output controls, shared CM memory power, and debug index/data.
- `DC_PERFMON9` through `DC_PERFMON14`: perfcounter/perfmon control, state, current value, high, and low registers for HUBP and DPP perfmon blocks. The comment for DPP3 perfmon appears just after this chunk, so `DC_PERFMON15` is outside this range except as an integration concern for the next chunk.

Every register offset in the chunk has a matching `_BASE_IDX` value of `2`, indicating that consumers should add the offset to `DCE_BASE__INST0_SEG2` through the DC resource helper macros.

## Important APIs, Types, And Macros

This file only defines preprocessor constants. There are no functions, structs, or runtime control-flow constructs in the chunk. The important "API" is the stable naming convention used by the rest of the display driver:

- Register offsets use `mm<block><instance>_<register>`, for example `mmHUBPREQ2_DCSURF_PRIMARY_SURFACE_ADDRESS` or `mmCM3_CM_RGAM_RAMB_REGION_32_33`.
- Address-base selectors use the matching `mm<block><instance>_<register>_BASE_IDX`.
- Consumers combine those constants through resource macros such as `SRI(reg_name, block, id)`, which expands to `BASE(mm ## block ## id ## _ ## reg_name ## _BASE_IDX) + mm ## block ## id ## _ ## reg_name`.
- The sibling `dcn_1_0_sh_mask.h` header supplies the corresponding bit shifts and masks, such as `HUBPREQ0_CURSOR_SETTINS` or `CM0_CM_DGAM_CONTROL` field definitions. This offset header provides address identity; the sh/mask header provides bitfield layout.

Concrete downstream macro lists that rely on names from this chunk include:

- `HUBP_REG_LIST_DCN10(id)` in `display/dc/hubp/dcn10/dcn10_hubp.h`, which references many `HUBP`, `HUBPREQ`, `HUBPRET`, and `CURSOR` offsets from this range.
- `IPP_REG_LIST_DCN10(id)` in `display/dc/dcn10/dcn10_ipp.h`, which uses `CNVC_CFG`, `CNVC_CUR`, `HUBPREQ`, and `CURSOR` register names for input pixel processing and cursor programming.
- `TF_REG_LIST_DCN10(id)` in `display/dc/dpp/dcn10/dcn10_dpp.h`, which uses the `CM`, `DSCL`, `CNVC`, and `DPP_TOP` offsets to initialize DPP color/scaler register tables.
- The `SR`, `SRI`, and `SRII` macros in `display/dc/resource/dcn10/dcn10_resource.c`, which materialize generated offsets into runtime register-address structs.

Several names intentionally preserve generated spelling, including `PREFETCH_SETTINS` and `CURSOR_SETTINS`. These spellings are part of the compile-time token contract; "correcting" them in the offset header without changing all macro-list consumers would break compilation.

## Control Flow And Runtime Use

The header itself has no branches or function calls. Runtime control flow enters indirectly when the DCN 1.0 resource layer constructs hardware object register tables:

1. `dcn10_resource.c` includes `dcn/dcn_1_0_offset.h` and `dcn/dcn_1_0_sh_mask.h`.
2. It defines `BASE(seg)` and `SRI(reg_name, block, id)` helpers. `BASE(mm..._BASE_IDX)` selects the DCE base segment, and the `mm...` offset is added to produce an absolute register index.
3. It builds arrays such as `hubp_regs[]` for four HUBP instances and `tf_regs[]` for four DPP instances.
4. Constructors such as `dcn10_hubp`, `dpp1_construct`, and `dcn10_ipp_construct` receive those register structs.
5. Later display paths program memory input, cursor, scaler, and color-management hardware via `REG_SET`, `REG_UPDATE`, `REG_GET`, and related helpers against the precomputed addresses.

Because the register tables are constructed at driver initialization time, an incorrect offset in this header becomes a persistent bad address in the hardware object for the lifetime of the driver instance. There is no runtime validation in this header that the offset matches the ASIC register map.

## State And Persistence Behavior

The constants are compile-time state. They do not allocate memory, mutate software state, or persist data themselves. Their persistence effect is indirect:

- At initialization, resource constructors copy the computed register addresses into static or heap-backed hardware object structs.
- During modesets and page flips, the HUBP/HUBPREQ registers in this chunk point the display engine at framebuffer, chroma, metadata, and cursor surfaces. Bad values can persist across flips until the affected pipe is reprogrammed.
- CM and DSCL registers in this chunk hold display-pipe programming for color conversion, gamma LUT access, scaler coefficients, viewport sizing, and line-buffer state. Those hardware registers retain programmed values until reset or overwritten by later display programming.
- Memory power control/status registers (`*_MEM_PWR_CTRL`, `*_MEM_PWR_STATUS`) affect block SRAM or LUT memory power state; incorrect addressing can leave blocks powered incorrectly or read the wrong status.
- VM/aperture and TLB-related HUBPREQ registers affect display fetch address translation for scanout surfaces. Incorrect programming can produce protection faults, underflow, or blank output.

There is no on-disk persistence and no distributed filesystem interaction despite the repository path prefix. This is Linux DRM/AMDGPU display hardware metadata.

## Dependencies And Integration Points

The direct dependencies are purely preprocessor-level:

- `soc15_hw_ip.h` and ASIC base-address headers provide symbols such as `DCE_BASE__INST0_SEG2`, consumed through `BASE(mm..._BASE_IDX)`.
- `dcn_1_0_sh_mask.h` must stay in sync with this offset header so each address has compatible field shift/mask definitions.
- DCN 1.0 display code under `display/dc/resource/dcn10`, `display/dc/hubp/dcn10`, `display/dc/dpp/dcn10`, and `display/dc/dcn10` depends on the exact generated symbol names.
- Later DCN generation headers follow the same naming shape but different address maps; copy/paste across generations is unsafe unless the consuming resource file includes the matching generation-specific offset and sh/mask headers.

Functional integration points by hardware block are:

- HUBP/HUBPREQ/HUBPRET: surface fetch, VM, viewport, flip timing, TTU/QoS, cursor fetch setup, read-line status, and display memory power control.
- CURSOR and CNVC_CUR: hardware cursor surface, positioning, color, scale/bias, hot spot, and enable state.
- CNVC_CFG: input pixel format and format expansion configuration before DPP processing.
- DSCL: scaler tap programming, line-buffer configuration, overscan, recout sizing, and memory power control.
- CM: gamut remap, input/output CSC, degamma/regamma LUT index/data windows, HDR multiplier, range clamp, denorm, output selection, and CM memory power.
- DC_PERFMON: display block performance counter programming and readback for diagnostics/performance tracing.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These constants are normally generated from ASIC register descriptions, and the compiler can only verify that names exist. It cannot verify that `0x0705` is the right address for `mmHUBPREQ2_DCSURF_PRIMARY_SURFACE_ADDRESS`.

High-impact risk areas in this chunk include:

- Surface address registers: bad `DCSURF_*_SURFACE_ADDRESS*` offsets can make scanout fetch from the wrong VRAM location, causing corruption, blank displays, GPU faults, or security-sensitive memory exposure.
- Flip/in-use registers: bad `DCSURF_SURFACE_CONTROL`, `DCSURF_FLIP_CONTROL`, `DCSURF_SURFACE_INUSE*`, or earliest-in-use offsets can break page-flip synchronization and tear-free updates.
- VM registers: incorrect `DCN_VM_*` or TLB offsets can cause display fetch protection faults or mask real address-translation issues.
- Timing and prefetch registers: wrong `VBLANK_PARAMETERS_*`, `NOM_PARAMETERS_*`, `PER_LINE_DELIVERY*`, `PREFETCH_SETTINS*`, or TTU/QoS offsets can cause underflow, flicker, or unstable high-resolution modes.
- Cursor registers: cursor offsets span both HUBPREQ cursor settings and CURSOR surface/position registers; cross-instance errors show up as missing cursors, cursors on the wrong pipe, or cursor memory faults.
- DSCL/CM LUT registers: LUT index/data windows and scaler coefficient RAM registers are stateful; wrong offsets can corrupt adjacent DPP state or make color/scaler programming appear to succeed while affecting the wrong register.
- Instance stride assumptions: instances 0-3 are similar but not derived at runtime. Each offset is an explicit constant, so a single generated value can be wrong even if surrounding instances look correct.
- Chunk-boundary risk: this chunk begins and ends inside larger generated register families. Review or regeneration must consider adjacent chunks to avoid orphaning the initial trailing `_BASE_IDX` and the final `CM3` continuation.

## Test Signals

There are no unit tests for this header alone. Useful signals come from build coverage, display bring-up, and hardware validation:

- Compile-time signal: AMDGPU display code must compile with `dcn_1_0_offset.h` and `dcn_1_0_sh_mask.h`; missing or renamed macros are caught by resource-list expansion in files such as `dcn10_resource.c`, `dcn10_hubp.h`, `dcn10_ipp.h`, and `dcn10_dpp.h`.
- Register-table sanity: debug dumps or targeted assertions can compare constructed register addresses for `hubp_regs[]`, `tf_regs[]`, and IPP register tables against the expected DCN 1.0 ASIC register map.
- Display functional tests: modeset, multi-plane scanout, page flip, cursor movement, cursor format changes, rotation/mirroring, scaling, chroma formats, and multi-display use exercise HUBP, CURSOR, CNVC, DSCL, and CM offsets from this chunk.
- Stress signals: high-refresh or high-bandwidth modes, dynamic page flips, cursor updates during flips, VRR-like timing changes, and memory-pressure scenarios are likely to expose prefetch, vblank, in-use, TTU/QoS, or VM-addressing mistakes.
- Color/scaler validation: degamma/regamma LUT programming, gamut remap, CSC, HDR multiplier, range clamp, and scaler coefficient tests can reveal CM/DSCL address mistakes that simple scanout may not catch.
- Power-management signal: suspend/resume, display blank/unblank, DC power gating, and memory power status readback exercise the `*_MEM_PWR_CTRL` and `*_MEM_PWR_STATUS` offsets.
- Diagnostics signal: perfmon tools or driver traces that program `DC_PERFMON9` through `DC_PERFMON14` should return plausible counter values and interrupt/status behavior.

For regression review, the strongest evidence is a combination of successful AMDGPU DCN 1.0 build, hardware modeset on an affected ASIC, cursor/page-flip/scaler/color tests, and comparison against the authoritative generated register database.
