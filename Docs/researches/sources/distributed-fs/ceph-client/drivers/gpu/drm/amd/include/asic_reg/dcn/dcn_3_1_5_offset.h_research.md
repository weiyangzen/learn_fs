# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001859`: lines 1-2652, `Docs/researches/chunks/subset-b-001859_research.md`
- `subset-b-001860`: lines 2653-5162, `Docs/researches/chunks/subset-b-001860_research.md`
- `subset-b-001861`: lines 5163-7647, `Docs/researches/chunks/subset-b-001861_research.md`
- `subset-b-001862`: lines 7648-10228, `Docs/researches/chunks/subset-b-001862_research.md`
- `subset-b-001863`: lines 10229-12818, `Docs/researches/chunks/subset-b-001863_research.md`
- `subset-b-001864`: lines 12819-15195, `Docs/researches/chunks/subset-b-001864_research.md`

## Chunk Research

### subset-b-001859: lines 1-2652

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h lines 1-2652

## Scope

This chunk covers lines 1-2652 of the generated AMD DCN 3.1.5 register offset header. The range starts at the file license and include guard `_dcn_3_1_5_OFFSET_HEADER`, then defines generated `reg*` register-offset constants grouped by `// addressBlock:` comments.

The source is a C preprocessor interface only. It contains no C functions, structs, enums, variables, inline helpers, allocation paths, or executable statements. The requested range contains 2,357 `reg*` `#define` entries: 1,179 register-offset macros and 1,178 `reg*_BASE_IDX` companion macros. The count is intentionally uneven for this chunk because line 2652 is `regHUBPREQ1_DCSURF_FLIP_CONTROL2`; its `_BASE_IDX` companion is the next line outside the assigned range.

## Purpose

This header provides the offset half of the generated DCN 3.1.5 display-controller register ABI used by AMDGPU display code. Consumers combine these offsets with DCN base segment constants, register access helper macros, and the companion `dcn_3_1_5_sh_mask.h` field definitions to read or program display hardware.

Although the tree path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

This opening chunk maps low-address DCN 3.1.5 hardware areas:

- Display clock generator (`DCCG`) and DCCG perfmon: pixel/DP/DSC/DPP/DTB/audio DTO controls, PHY PLL pixel-rate/resync controls, clock gates, GTC/current time-base registers, vsync latch/count registers, soft reset, and perfmon instances 0-1.
- DMU, DMCU, RBBMIF, interrupt-host-controller, foreground-security, display power-gating, and DMCUB: firmware memory windows, ERAM/IRAM access, master/slave communication, interrupt routing, power state, DMCUB region/code-window/inbox/outbox/timer/scratch/fault/control registers, and DMU perfmon.
- Display writeback and MCIF/MMHUBBUB: DWB top controls, DWB color/gamut/OGAM programming, writeback perfmon, MCIF writeback buffer address/status/pitch/watermark/QoS/VMID registers, MMHUBBUB warmup, memory power, clocks, reset, outstanding counters, and error status.
- Legacy VGA direct MMHUBBUB/VGA aliases: VGA memory page, render/control/status, CRTC/ATTR/GRPH/SEQ/DAC/GEN register windows, source-select, source-split, and related compatibility controls.
- Azalia/HDA audio direct registers: controller clock/DMA/CORB/RIRB/CRC controls, F0 codec root parameters, stream index/data windows for streams 0-15, endpoint index/data windows for output endpoints 0-7 and input endpoints 0-7, plus AZ perfmon.
- DCHUBBUB and request/return paths: arbitration watermarks A-D, self-refresh/DRAM clock-change controls, host VM and SDPIF address-window registers, DCC return-path config/statistics, CRC, compbuf/DET controls, VM context page-table registers, VM fault/status registers, hubbub perfmon, HUBP0 and HUBP1 surface/viewport/request registers, HUBPREQ0/HUBPREQ1 address/flip/prefetch/timing registers, HUBPRET0 read-line registers, and cursor0/DMDATA registers.

## Important APIs, Types, And Macros

There are no callable APIs or type definitions in this range. The public interface is the generated macro namespace:

- `reg<REGISTER_NAME>`: a direct DCN 3.1.5 register offset.
- `reg<REGISTER_NAME>_BASE_IDX`: the base-address segment selector used by helpers that compute the final MMIO address.
- `// addressBlock: ...` and `// base address: ...`: generated grouping comments that identify the hardware block and local block base represented by the following register names.

The main access contract is visible in DCN315 consumers. They define segment constants such as `DCN_BASE__INST0_SEG0` through `DCN_BASE__INST0_SEG5`, then use token-pasting helpers equivalent to `BASE(regNAME_BASE_IDX) + regNAME`. `display/dmub/src/dmub_dcn315.c` names this pattern explicitly as `REG_OFFSET_EXP(reg_name)`.

All direct registers in this chunk use base index values 0, 1, or 2:

- Base index 0 appears on early VGA memory page registers.
- Base index 1 appears on DCCG and many direct VGA compatibility registers.
- Base index 2 dominates DMU/DMCUB/DWB/MMHUBBUB/AZ/DCHUBBUB/HUBP/HUBPREQ/HUBPRET/cursor and perfmon registers.

The chunk does not contain `ix*` indexed-register constants. Every visible hardware symbol in the assigned range is a `reg*` direct offset, with the one line-boundary exception noted above for `regHUBPREQ1_DCSURF_FLIP_CONTROL2_BASE_IDX`.

## Control Flow

This header has no local runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes this offset header with its matching shift/mask header.

The normal flow is:

1. DCN315-specific code includes `dcn/dcn_3_1_5_offset.h` and `dcn/dcn_3_1_5_sh_mask.h`.
2. A register-list macro chooses a symbolic register, such as `DMCUB_INBOX0_WPTR`, `DCHUBBUB_ARB_WATERMARK_CHANGE_CNTL`, `HUBP0_DCSURF_SURFACE_CONFIG`, `HUBPREQ0_DCSURF_PRIMARY_SURFACE_ADDRESS`, or `AZALIA_CONTROLLER_CLOCK_GATING`.
3. Token-pasting helpers form the final MMIO address from `BASE(reg..._BASE_IDX) + reg...`.
4. Field helpers from `dcn_3_1_5_sh_mask.h` pack or unpack individual bits.
5. Driver paths use register helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and wait/poll helpers to program clocks, firmware mailboxes, power domains, interrupts, audio, writeback, memory arbitration, scanout surfaces, cursor, and VM state.

The macros do not encode hardware ordering. Consumers must still sequence clock enables, power gating, firmware setup, DMCUB mailbox initialization, interrupt clear/ack, display hub watermarks, VM context programming, surface flips, cursor updates, writeback buffer programming, and Azalia stream/endpoint setup according to the hardware spec.

## State And Persistence Behavior

The header stores no software state and persists nothing to disk. It describes MMIO-backed GPU display state.

State domains represented in this range include:

- DCCG clock state: DTO phase/modulo values, clock enables/gates, pixel-rate controls, GTC/current time-base counters, audio DTOs, vsync latch/count state, and soft reset.
- DMU/DMCU/DMCUB firmware state: firmware address ranges, ERAM/IRAM access windows, checksums, scratch registers, interrupt masks/status/selectors, master/slave communication registers, region/code-window mappings, inbox/outbox pointers, timers, GPINT data, undefined-address fault reporting, wake interrupt state, and DMCUB control registers.
- Writeback/MMHUBBUB state: DWB flow/color/CRC/output controls, OGAM/gamut/LUT programming, MCIF writeback buffer addresses and status, watermarks, VMID/QoS, DRAM/SCLK speed-change handling, warmup controls, memory power, clocks, reset, and outstanding counters.
- HDA/Azalia state: controller clock and DMA controls, codec root parameters, stream index/data windows, endpoint index/data windows, audio DTO, CRC controls/results, memory power, and stream/endpoint codec access.
- DCHUBBUB/HUBP state: arbitration watermarks, self-refresh and DRAM-clock-change gating, host VM policy, VM context page-table base/start/end registers, fault status/address, return-path DCC and compbuf/DET controls, surface format/tiling/viewport, primary/secondary/meta surface addresses, flip control, prefetch/timing/watermark parameters, cursor surface/position/hotspot/DMDATA, and read-line/interrupt status.

Persistence is hardware-defined. Configuration registers usually retain values until modeset, reprogramming, power gating, suspend/resume, firmware action, or ASIC reset. Status, counter, interrupt, fault, debug, clear/ack, mailbox, and power-status registers may be read-only, sticky, self-clearing, write-one-to-clear, or asynchronously updated by hardware or firmware. This offset header does not express access type or side effects.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h`, which supplies field shifts and masks for the registers addressed here. The offset and mask headers must come from the same generated DCN 3.1.5 register database.

Observed direct include sites in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`, which builds `dmub_srv_dcn315_regs` using `REG_OFFSET_EXP(reg_name)` and field tables from the matching mask header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which includes the offset/mask pair while constructing DCN315 resource tables for DCCG, hubbub, HUBP, audio, GPIO/AUX/I2C, stream encoders, IRQ, DMUB, and related display blocks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`, which includes the pair for interrupt-service register programming and maps DCN interrupt source IDs to DAL IRQ sources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.c`, which use generated register metadata for GPIO, DDC, AUX, HPD, panel, and related pin translation/factory setup.

Additional integration is through shared DCN31/DCN314/DCN315 display block code. Many names in this chunk are consumed by common register-list macros for DCCG, hubbub, HUBP, DMCUB, DWB, HDA/audio, perfmon, power-gating, and hardware sequencing. DCN315-specific resource selection is what binds those shared block implementations to these generated numeric offsets.

## Risks And Edge Cases

- Offset or base-index drift is the main risk. These are untyped integer constants, so an incorrect `reg...` value or `reg..._BASE_IDX` can compile successfully while accessing the wrong MMIO segment or register.
- The base index is part of the address, not metadata for humans. A correct hex offset paired with the wrong base index can target a different register aperture.
- The chunk boundary creates one apparent pair mismatch: `regHUBPREQ1_DCSURF_FLIP_CONTROL2` is in this range and its `_BASE_IDX` is immediately outside it. Whole-file reconciliation should treat this as a chunking artifact.
- Repeated instance families are copy-sensitive. DCCG perfmons, DMCUB regions/code windows, streams 0-15, endpoints 0-7, input endpoints 0-7, VM contexts, watermarks A-D, HUBP0/HUBP1, HUBPREQ0/HUBPREQ1, and perfmon instances are similar but not interchangeable.
- DMCUB registers are firmware-contract sensitive. Inbox/outbox offsets, scratch registers, GPINT, fault, security, timer, region, and control registers must match both the host driver and the firmware image.
- VM and surface-address registers are high-impact. A wrong VM context or HUBPREQ surface/meta address offset can cause GPU page faults, scanout corruption, stale flips, memory-security issues, or display hangs.
- Interrupt/status/clear registers are side-effect-sensitive. Wrong offsets can miss vblank/page-flip/HPD/AUX/DCHUBBUB/DMCUB/AZ events or clear the wrong status bit.
- Clock, power, and watermark registers are sequencing-sensitive. Bad DCCG, power-gating, MMHUBBUB, DCHUBBUB, or HUBPREQ offsets can appear as intermittent underruns, blanking, resume failures, audio loss, writeback corruption, or display instability under multi-display and low-power transitions.

## Test Signals

Useful validation for this chunk is mostly build, generated-data, and hardware smoke coverage:

- Build coverage for DCN315 translation units that include this header, especially `dmub_dcn315.c`, `dcn315_resource.c`, `irq_service_dcn315.c`, `hw_factory_dcn315.c`, and `hw_translate_dcn315.c`.
- Static/generated checks that each direct `reg*` offset has the expected `reg*_BASE_IDX`, accounting for the line-boundary exception at `regHUBPREQ1_DCSURF_FLIP_CONTROL2`.
- Diff or regeneration checks against AMD's authoritative DCN 3.1.5 register database, with special attention to base indices, repeated instance strides, and differences from neighboring DCN 3.1.4/DCN 3.1.6 headers.
- DMUB/DMCUB bring-up tests that exercise firmware load/control, region/window programming, inbox/outbox traffic, GPINT handling, scratch registers, timer reads, fault reporting, and wake interrupts.
- Display clock tests covering DCCG DTO programming, DP/DSC/DPP/DTB/audio clocks, pixel-rate controls, GTC/current time-base reads, vsync latch/count programming, clock gating, and soft reset.
- IRQ tests for vblank, vupdate, page flip, HPD, AUX, DIO/DCIO, DCCG, DMU, MMHUBBUB, writeback, DCHUB, MPC/OPP/OPTC, DSC, HPO, and AZ interrupt routing/status behavior.
- Plane and memory tests covering HUBP/HUBPREQ surface format, tiling, viewport, pitch, primary/secondary/meta addresses, DCC, VMID, prefetch/timing parameters, flips, cursor position/surface/DMDATA, and HUBPRET read-line interrupts.
- Low-power and bandwidth tests covering DCHUBBUB watermarks A-D, self-refresh entry/exit, DRAM clock-change gating, host VM controls, compbuf/DET state, memory power, and warmup behavior.
- HDMI/DP audio and writeback tests covering Azalia controller/stream/endpoint access, audio DTO, CRC, memory power, DWB flow/color/OGAM/gamut/CRC/output controls, and MCIF writeback buffer programming/readback.

## Cross-Chunk Notes

This is the opening chunk of a 15,195-line generated offset header. It establishes the file guard and covers common low-address DCN 3.1.5 register maps through the beginning of `dce_dc_dcbubp1_dispdec_hubpreq_dispdec`. Later chunks are required to complete HUBPREQ1 and cover additional HUBP instances, DPP/DSCL/CM, MPC/OPP/OPTC, DIO/AUX/I2C/HPD, DSC/HPO, panel/backlight, and remaining generated register spaces before making whole-file claims.

### subset-b-001860: lines 2653-5162

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

### subset-b-001861: lines 5163-7647

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h lines 5163-7647

## Purpose

This chunk is generated AMD DCN 3.1.5 display register-address metadata. It contains no executable C logic; it publishes preprocessor constants that map symbolic register names to MMIO offsets plus a matching `<register>_BASE_IDX` selector. AMDGPU display code combines each offset with `DCN_BASE__INST0_SEG*` base constants to build runtime register tables for DCN315 hardware blocks.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver ASIC metadata and has no Ceph or distributed filesystem behavior.

The requested range covers 2,401 `#define` lines across 21 address-block markers or continuation regions. It starts in the middle of the `CM2` color-management block, continues through DPP2 and DPP3 display pipe register groups, includes the MPC/MPCC compositor and RMU color-LUT register space, and ends inside the first ABM0 backlight/ambient-light block. The major hardware surfaces are:

- Tail of `CM2` color management: gamma-correction RAM B region entries, blender gamma LUT programming, HDR multiplier, coefficient/dealpha controls, shaper LUTs, 3D LUTs, memory power, and debug index/data.
- DPP2 top and perfmon registers: DPP control, soft reset, CRC readback/control, host-read control, and `DC_PERFMON13`.
- DPP3 CNVC, cursor, scaler, color-management, top, and perfmon registers: pixel-format conversion, color keying, pre-CSC, DSCL filter/scaler/line-buffer controls, full `CM3` gamma/shaper/3DLUT programming, DPP top controls, and `DC_PERFMON14`.
- MPC register space: MPCC0 through MPCC3 blending/composition state, global MPC clock/reset/CRC/pending/vupdate-lock/DWB mux controls, `DC_PERFMON15`, out muxes, output CSC, output gamma/OGAM, and RMU0/RMU1 shaper plus 3DLUT registers.
- Start of `ABM0`: BL1 PWM/ABM backlight registers and the beginning of `DC_ABM1` ambient backlight management histogram/luma-statistics registers.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, locks, allocations, or direct persistence APIs in this line range. The public interface is the generated macro convention:

- `reg<block>_<register>` gives the register offset inside the selected DCN base segment.
- `reg<block>_<register>_BASE_IDX` gives the base-segment index used by local `BASE(reg..._BASE_IDX)` helper macros in DCN315 resource code.

Important macro families in this chunk:

- `regCM2_CM_*`: continuation of DPP pipe 2 color-management offsets. The chunk starts after earlier `CM2` post-CSC, gamut-remap, bias, and most gamma-correction definitions; this range includes the remaining gamma-correction RAM B region slots, blender gamma, HDR multiplier, memory power, dealpha/coefficient format, shaper RAM A/B, 3DLUT, and test debug registers. All have base index `2`.
- `regDPP_TOP2_*` and `regDC_PERFMON13_*`: DPP2 top-level control/CRC/host-read registers and DPP2 perfmon counter controls. All have base index `2`.
- `regCNVC_CFG3_*` and `regCNVC_CUR3_*`: DPP3 converter and cursor offsets for surface pixel format, format control, floating-point bias/scale, color keyer, alpha LUT, pre-dealpha, pre-CSC matrices, pre-degamma, pre-realpha, and cursor color/control state. All have base index `2`.
- `regDSCL3_*`: DPP3 scaler/filter offsets for coefficient RAM access, SCL/DSCL modes, tap control, manual replicate, horizontal/vertical ratios and initial phases for luma/chroma, black color, update/autocal, overscan, OTG blanking, recout/MPC sizes, line-buffer format and memory control, counters, DSCL memory power, and output-buffer memory power. All have base index `2`.
- `regCM3_CM_*`: full DPP3 color-management offset set. It mirrors the CM2 pattern for control, post-CSC, gamut remap, bias, gamma-correction LUT and RAM A/B, blender-gamma LUT and RAM A/B, HDR multiplier, memory power, dealpha/coefficient format, shaper LUT and RAM A/B, 3DLUT, and test debug registers. All have base index `2`.
- `regDPP_TOP3_*` and `regDC_PERFMON14_*`: DPP3 top-level control/CRC/host-read registers and DPP3 perfmon counter controls. All have base index `2`.
- `regMPCC0_*` through `regMPCC3_*`: compositor pipe instances for top/bottom input selection, OPP routing, MPCC control, state-machine control, update-lock selection, top/bottom gain, background color, memory power, and status. These offsets use base index `3`.
- `regMPC_*`, `regADR_*`, `regCFG_*`, and `regCUR_*`: global MPC control, reset, CRC, perfmon event selection, bypass backgrounds, host-read, DPP/pending status, vupdate locks for four sets, DWB mux, and `DC_PERFMON15`. These offsets use base index `3`.
- `regMPC_OUT_MUX*_*`: output mux routing, status, alpha control, and selected-output readback for MPC output instances 0 through 3. These use base index `3`.
- `regMPC_OCSC_*` and `regMPC_OGAM_*`: MPC output color space conversion and output gamma/shaper/LUT registers, including output CSC A/B matrices, OGAM RAM A/B start/end/region registers, memory power, and test debug. These use base index `3`.
- `regMPC_RMU0_*` and `regMPC_RMU1_*`: RMU shaper and 3DLUT programming registers for two RMU instances. RMU0 is mostly in the middle of this chunk, while RMU1 is complete from shaper control through 3DLUT output offsets. These use base index `3`.
- `regABM0_BL1_PWM_*` and `regABM0_DC_ABM1_*`: beginning of ABM0 backlight and ambient backlight management offsets, including ambient/user/target/current/final/minimum duty cycle, PWM ABM control, update sample rate, register lock, ABM control, IPCSC coefficient selection, ACE offsets/thresholds, luma-stat readback, histogram sample/bin controls, and histogram result registers 1 through 5. These use base index `3`.

The companion `dcn_3_1_5_sh_mask.h` file supplies bit-field masks and shifts for many of these register names. Consumers normally use both headers through helper macros such as `SR`, `SRI`, `SRII`, `SRII_MPC_RMU`, `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

## Control Flow

This header has no runtime branches, loops, callbacks, or call graph. Control flow is supplied by AMDGPU display code that includes the generated offset and mask headers and expands register-list macros into typed register tables.

Typical runtime path:

1. DCN315 resource code includes `dcn/dcn_3_1_5_offset.h` and `dcn/dcn_3_1_5_sh_mask.h`.
2. Local helper macros in `dcn315_resource.c` compute absolute addresses as `BASE(reg..._BASE_IDX) + reg...`.
3. Register-list macros such as `DPP_REG_LIST_DCN30(id)`, `ABM_DCN302_REG_LIST(id)`, `MPC_REG_LIST_DCN3_0(inst)`, `MPC_OUT_MUX_REG_LIST_DCN3_0(inst)`, and related mask/shift lists initialize per-block structs.
4. Runtime display code programs those structs through block-specific modules: DPP/CNVC/DSCL/CM code for pipe color and scaling, MPC/MPCC code for blending and routing, ABM code for backlight management, perfmon code for counters, and HWSS/resource sequencing code for modeset and power transitions.
5. DMUB DCN315 code also includes the same generated offset/mask headers to populate `dmub_srv_dcn315_regs` through `DMUB_DCN31_REGS()`, `DMCUB_INTERNAL_REGS()`, and field-list expansions, although the specific chunked CM/DPP/MPC/ABM registers are primarily consumed by DC resource and hardware block tables.

The offset macros do not encode hardware access ordering. Driver code must still sequence indexed LUT accesses, register locks, vupdate locks, memory power transitions, soft resets, and CRC/perfmon counter operation according to each block's hardware rules.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes MMIO-backed GPU display state that lives in hardware until changed by the driver, reset by block/ASIC reset, or lost through power-gating/suspend/resume transitions.

State represented by the offsets includes:

- DPP pipe color state: post-CSC/gamut/bias configuration, gamma-correction RAM A/B, blender gamma RAM A/B, HDR multiplier, dealpha, coefficient format, shaper RAM A/B, 3DLUT index/data/control, memory power controls, and debug windows for CM2 and CM3.
- DPP top/scaler/converter state: DPP enable/control, soft reset, CRC control and values, host-read control, CNVC surface pixel format and color keying, cursor color/control, DSCL filter coefficients, scaling ratios, initial phases, line-buffer format, recout/MPC geometry, memory power, and output-buffer control.
- Perfmon state: DPP2 `DC_PERFMON13`, DPP3 `DC_PERFMON14`, and MPC `DC_PERFMON15` counter controls, run/configuration state, interrupt miscellaneous state, and high/low counter readback registers.
- MPCC/MPC composition state: per-MPCC top/bottom source selection, OPP routing, blending gains, background color, update-lock selection, memory power, MPCC status, global MPC clock/reset/CRC, pending statuses, vupdate lock sets, DWB muxing, output mux routing/status, output CSC coefficients, output gamma RAM, and MPC test debug windows.
- RMU state: two RMU shaper LUT/region programming blocks plus RMU 3DLUT index/data/read-write/out-normalization/out-offset registers.
- ABM state: PWM brightness request and status levels, minimum/final duty cycle, update cadence, register locking, ABM control, ACE contrast-enhancement parameters, luminance statistics, histogram sample controls, bin shifting, and initial histogram result registers.

Some registers are configuration registers, some are read-only or readback status, some are indexed data ports, some are register-lock or vupdate synchronization controls, and some likely have self-clearing or write-one-to-clear behavior. The generated offset header does not express those access classes; the paired mask header, hardware programming manuals, and consuming driver code provide that context.

## Dependencies And Integration Points

This chunk must remain consistent with the generated DCN 3.1.5 register database and its paired field-layout header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h`

Direct include sites found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.c`

Key integration points:

- `dcn315_resource.c` defines `BASE`, `SR`, `SRI`, `SRII`, and `SRII_MPC_RMU` macros that token-paste these generated `reg...` symbols into absolute register addresses.
- `dcn315_resource.c` builds `dpp_regs[]` with `DPP_REG_LIST_DCN30(id)`, which consumes the DPP top, CNVC, DSCL, and CM register families represented here for pipe instances 2 and 3.
- `dcn315_resource.c` builds `abm_regs[]` with `ABM_DCN302_REG_LIST(id)` and `abm_shift`/`abm_mask` with `ABM_MASK_SH_LIST_DCN30()`, integrating ABM0 offsets from the end of this chunk with ABM hardware programming paths.
- `dcn315_resource.c` builds `mpc_regs` with `MPC_REG_LIST_DCN3_0()`, `MPC_OUT_MUX_REG_LIST_DCN3_0()`, and `MPC_DWB_MUX_REG_LIST_DCN3_0()`, integrating the MPCC, MPC global, output mux, and DWB mux offsets from this range. DCN315 defines `SRII_MPC_RMU`, but unlike adjacent DCN31/DCN314 resource files in this tree, this specific resource table does not visibly instantiate the `MPC_RMU_*` list in the searched excerpt.
- DPP color code uses the CM, shaper, gamma, and 3DLUT register tables to implement color transforms exposed through DC color-management state, including shaper LUTs and 3D LUTs.
- MPC/MPCC code uses composition and mux registers for plane blending, top/bottom tree wiring, OPP output routing, background colors, CRC, output CSC/gamma, and update-lock coordination.
- ABM/backlight code uses the ABM0 offsets to drive panel backlight PWM and ambient-backlight-management calculations.
- `dmub_dcn315.c` uses the same generated namespace for DCN315 DMUB register maps, keeping firmware-service register addressing in sync with the resource code's DCN base segments.

## Risks And Edge Cases

- Generated offset drift is the main risk. A wrong offset or base index compiles cleanly but can direct the driver to the wrong MMIO register, potentially corrupting color programming, scaler state, compositor routing, backlight state, or unrelated display hardware.
- This chunk has artificial boundaries. It starts in the middle of `CM2_CM_GAMCOR_RAMB_REGION_*`, so the complete CM2 gamma-correction context is in the previous chunk. It ends at `ABM0_DC_ABM1_HG_RESULT_5`, before the rest of the ABM0 histogram results and backlight-lock registers in the next chunk.
- Indexed LUT registers are sequencing-sensitive. `*_LUT_INDEX`, `*_LUT_DATA`, `*_3DLUT_INDEX`, `*_3DLUT_DATA`, `*_READ_WRITE_CONTROL`, and RAM A/B region registers must be programmed with the expected bank, index, and write-enable order. A bad offset can load the wrong bank or leave color transforms partially updated.
- Color pipeline offsets are high impact. Bad CM2/CM3 post-CSC, gamut-remap, shaper, gamma, blender-gamma, 3DLUT, or HDR multiplier addresses can cause wrong color output, banding, black screens, or failures that only appear with HDR, color-managed desktops, overlays, or multi-plane composition.
- DSCL/CNVC mistakes can break mode timing and format conversion. Incorrect scaling ratios, filter RAM access, line-buffer format, recout/MPC size, or pixel-format conversion offsets can cause underflow, corrupted scanout, clipped output, or failed plane validation symptoms.
- MPCC and MPC routing registers affect active composition. Wrong top/bottom selection, OPP ID, output mux, vupdate-lock, pending-status, or DWB mux offsets can misroute planes, leave updates stuck, break writeback, or produce inconsistent debug state.
- Memory power and soft-reset registers can disrupt live hardware if programmed while a pipe or compositor block is active. The header does not indicate which registers require disable, lock, or idle sequencing.
- Perfmon registers are diagnostic but stateful. Wrong counter control or interrupt-misc offsets can produce misleading performance data or leave counter interrupts/status bits stuck.
- ABM/PWM offsets are user-visible. A wrong duty-cycle, user-level, target-level, sample-rate, or lock offset can produce brightness jumps, ignored backlight requests, stalled ABM transitions, or incorrect luma histogram feedback.
- Base-index mismatches are as dangerous as offset mismatches. This range crosses base index `2` DPP blocks and base index `3` MPC/ABM blocks; using the wrong base segment would send otherwise-correct offsets into the wrong address aperture.

## Test Signals

Useful validation should combine generated-header consistency checks, build coverage, and hardware behavior:

- Build AMDGPU/DC with DCN315 enabled. Missing or renamed macros should fail in `dcn315_resource.c`, `dmub_dcn315.c`, IRQ/GPIO DCN315 files, or shared DPP/MPC/ABM register-list expansions.
- Mechanically verify that every `reg...` definition in this range has a matching `_BASE_IDX` definition and that the expected base indices are preserved: DPP/CM/CNVC/DSCL/perfmon13/14 entries use `2`, while MPCC/MPC/RMU/ABM entries use `3`.
- Compare this offset range against AMD's authoritative DCN 3.1.5 register database and adjacent generated DCN 3.1.x headers where the same register families should remain compatible.
- Exercise DPP2/DPP3 color-management paths: post-CSC, gamut remap, degamma/gamma, blender gamma, shaper LUT, 3DLUT host loads, HDR multiplier, dealpha, memory power transitions, and debug readback.
- Exercise DPP3 scaling/conversion paths: pixel-format changes, color keying, cursor color/control, DSCL coefficient RAM loads, luma/chroma scaling ratios, overscan, line-buffer formats, recout/MPC sizing, CRC values, and host-read control.
- Exercise MPCC/MPC composition: multi-plane blending, MPCC top/bottom tree changes, OPP assignment, update locks, background color, output mux status, output CSC/gamma, DWB muxing, pending-status readback, and CRC selection/result readback.
- Exercise RMU shaper/3DLUT programming if enabled by the DCN315 resource configuration or later changes. Validate bank selection, index/data writes, 30-bit data paths, output normalization, and per-channel offsets.
- Exercise ABM/backlight behavior: user brightness changes, ambient-light updates, target/current/final duty-cycle reporting, sample-rate changes, group register locking, ACE configuration, luma-statistics readback, histogram bin controls, and histogram result readback beyond this chunk after merge.
- Exercise suspend/resume and display off/on transitions. Confirm that CM, DSCL, MPC, RMU, and ABM memory-power/status registers restore or reinitialize correctly without stale LUT banks, stuck locks, or incorrect PWM output.

## Cross-Chunk Notes

The previous chunk owns the start of the `CM2` color-management block, including the earlier gamma-correction register definitions that precede `regCM2_CM_GAMCOR_RAMB_REGION_8_9_BASE_IDX`. The next chunk owns the remainder of `ABM0_DC_ABM1_*`, including histogram results after result 5 and later ABM/backlight control registers. The final per-file research document should merge adjacent chunks before making complete claims about CM2 or ABM0 coverage.

### subset-b-001862: lines 7648-10228

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h lines 7648-10228

## Purpose

This chunk is generated AMD DCN 3.1.5 register-address metadata. It contains no executable C logic; it publishes `#define` constants for register offsets and their associated base-index selectors. The companion `dcn_3_1_5_sh_mask.h` header provides field masks and shifts, while this offset header gives the address half used by display-driver register helper macros.

Although this file lives under a local `ceph-client` source mirror, the content is AMDGPU display-engine hardware metadata and has no Ceph or distributed-filesystem behavior.

The requested range starts in the middle of the ABM0 ambient-backlight histogram-result block and ends in the middle of the DIG2 HDMI/audio packet block. Within those boundaries, it covers:

- The tail of `ABM0` histogram readback and backlight master lock offsets.
- Full `ABM1`, `ABM2`, and `ABM3` ambient-backlight/PWM blocks.
- OPP blocks for pipes 0 through 3: display pipe generator (`DPG`), formatter (`FMT`), OPP buffer, OPP pipe control, and OPP pipe CRC registers.
- DSC remap/forwarding (`DSCRM0` through `DSCRM2`), OPP top-level controls, and `DC_PERFMON16`.
- ODM input controls 0 through 3 and OTG timing generator blocks 0 through 3.
- OPTC miscellaneous controls and `DC_PERFMON17`.
- Hotplug-detect blocks `HPD0` through `HPD4`.
- DisplayPort link/PHY/secondary-data/MST/DSC/ALPM/GSP offsets for `DP0`, `DP1`, and `DP2`.
- Digital front-end/HDMI/audio formatter offsets for `DIG0` and `DIG1`, plus the beginning of `DIG2`.

This slice has 2,385 `#define reg...` lines: 1,193 register-offset constants and 1,192 `_BASE_IDX` constants. The one-count mismatch is intentional for the chunk boundary: line 10228 includes `regDIG2_HDMI_DB_CONTROL`, while its `_BASE_IDX` appears after this range.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocations, locks, or direct persistence APIs in this chunk. Its public interface is the generated macro naming convention:

- `reg<REGISTER_OR_INSTANCE>`: register offset within a DCN base segment.
- `reg<REGISTER_OR_INSTANCE>_BASE_IDX`: selector for the base segment used by `BASE(reg..._BASE_IDX)` in DCN315 consumers.

Important register families in this range:

- ABM/PWM: `regABM*_BL1_PWM_*`, `regABM*_DC_ABM1_*`, ACE slopes/thresholds, luma statistics, histogram sample/bin/result registers, and backlight master locks. These are the address constants for adaptive backlight management and panel backlight PWM state.
- OPP/display formatter: `regDPG*_*`, `regFMT*_*`, `regOPPBUF*_*`, `regOPP_PIPE*_*`, and `regOPP_PIPE_CRC*_*`. These support output-pixel formatting, clipping/clamping, 4:2:2 conversion, dithering, pipe blank/control, buffer controls, and CRC diagnostics.
- DSC/OPP top/perfmon: `regDSCRM*_*`, `regOPP_TOP_*`, `regOPP_ABM_CONTROL`, and `regDC_PERFMON16_*`. These support DSC forwarding/remap, shared OPP controls, ABM selection, and OPP-side performance counters.
- OPTC/ODM/OTG: `regODM*_*`, `regOTG*_*`, `regOPTC_*`, `regDWB_SOURCE_SELECT`, and `regDC_PERFMON17_*`. These are timing-compositor addresses for ODM input selection, OTG totals/blanking/sync, vertical interrupts, trigger controls, CRC, lock/unlock, global swap lock, generated test signals, stereo, static-screen, double-buffer controls, and timing perf counters.
- HPD: `regHPD*_DC_HPD_*` for interrupt status/control, control, fast-training status, interrupt filter, RX interrupt timer, and toggle filter control.
- DP link encoders: `regDP*_DP_LINK_CNTL`, training controls, MSA/MSE timing and allocation registers, DPHY symbols/scrambling/CRC/fast-training, secondary-data packet controls, audio N/M timestamp registers, DSC, DB, ALPM, and GSP packet controls/status.
- DIG/HDMI front ends: `regDIG*_DIG_*`, `regDIG*_HDMI_*`, `regDIG*_AFMT_*`, `regDIG*_TMDS_*`, `regDIG*_DIG_BE_*`, and `regDIG*_FORCE_DIG_DISABLE` for digital encoder setup, output CRC/test patterns, HDMI metadata/audio/infoframes/generic packets, ACR values, audio formatter, backend enable, TMDS, and forced disable. `DIG2` is incomplete in this slice and stops at `regDIG2_HDMI_DB_CONTROL`.

The `_BASE_IDX` values map most OPP/OPTC/HPD/DP/DIG instance registers to segment 2 or 3. DCN315 users define constants such as `DCN_BASE__INST0_SEG2` and `DCN_BASE__INST0_SEG3`, then compute absolute MMIO addresses with expressions like `BASE(regX_BASE_IDX) + regX`.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code that includes this generated offset header and the matching shift/mask header.

Typical flow:

1. DCN315 DMUB, IRQ, GPIO, and resource code include `dcn_3_1_5_offset.h` and `dcn_3_1_5_sh_mask.h`.
2. Those source files define DCN base segment constants such as `DCN_BASE__INST0_SEG0` through `DCN_BASE__INST0_SEG5`.
3. Token-paste helper macros such as `REG_OFFSET_EXP`, `REG`, `SRI`, `SRI_DMUB`, `REGI`, and block-specific register-list macros combine `reg..._BASE_IDX` and `reg...` values into absolute MMIO offsets.
4. Higher-level display objects use the resulting register tables to program hardware during resource construction, modesets, interrupt acknowledgment, HPD/DDC/GPIO handling, DMUB setup, link training, timing generation, stream encoding, audio packet generation, panel backlight adjustment, diagnostics, and suspend/resume restore.

The offsets alone do not encode ordering or access side effects. Consumers must still follow hardware programming sequences for pipe disable/enable, OTG locking, vertical blank updates, double-buffer commits, HPD interrupt acknowledgment, DP link training, audio packet setup, ABM updates, CRC/perfmon readback, and power/clock gating.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on disk. It describes addresses for MMIO-backed GPU display state. State represented by these definitions includes:

- ABM and backlight state: ambient-light level, user/target/current/final PWM duty, minimum duty cycle, update sample rate, ABM control, register locks, ACE coefficients, luma statistics, histogram configuration, histogram bins/results, and master locks.
- OPP pipe state: DPG control/status, formatter clamp/dynamic-expansion/dither/bit-depth/420 memory controls, OPP buffer controls, pipe enable/control, and per-pipe CRC controls/results.
- Shared OPP and perfmon state: DSC forwarding, OPP clock/debug/spare/ABM controls, and performance counter selection, run state, repeat count, interrupt status/ack, and counter high/low values.
- OPTC/OTG state: ODM input sources, H/V totals, blanking, sync timing, control flags, vertical interrupt positions, dynamic timing controls, global swap lock, CRC windows/results, generated test pattern state, static-screen controls, double-buffer controls, trigger controls, and timing generator spare registers.
- HPD state: hotplug status, interrupt enable/ack/filter, RX interrupt timer, control bits, fast-training status, and debounce/toggle filtering.
- DP/DIG state: DP link control, main-stream attributes, training patterns, DPHY symbols/scrambler/CRC/fast-training, secondary-data packet framing, audio N/M/timestamp, MST allocation, DSC/MSO/ALPM/GSP controls, digital front-end controls, HDMI infoframes/generic packets/metadata/audio, ACR values, audio formatter, TMDS, backend enable, and forced-disable state.

Persistence is hardware-defined. Some registers hold configuration until a modeset, link retrain, panel power transition, suspend/resume, clock/power-gating event, or ASIC reset. Others are read-only status, sticky interrupt, write-one-to-clear, double-buffered, self-clearing, or diagnostic readback registers. This generated offset header does not distinguish those access classes; consumer code and hardware documentation provide that context.

## Dependencies And Integration Points

This chunk must match AMD's generated DCN 3.1.5 register database and its companion field header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h`

Direct include sites found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.c`

Key integration points:

- `dmub_dcn315.c` builds `dmub_srv_dcn315_regs` by expanding register and field lists through DCN315 base/offset macros. Although the DMUB list is mostly outside this specific OPP/OPTC/DIO slice, it depends on the same generated offset/field scheme and base-index mapping.
- `dmub_srv.c` selects `dmub_srv_dcn315_regs` for `DMUB_ASIC_DCN315`, allowing common DMUB service code to issue register reads/writes through the populated DCN31 register table.
- `irq_service_dcn315.c` maps hardware interrupt source IDs to DAL IRQ sources and uses `SRI`/`SRI_DMUB` expansions for enable and ack registers. The HPD and OTG families in this chunk are directly relevant to hotplug, HPDRX, vblank, vline, and vupdate interrupt plumbing.
- `hw_factory_dcn315.c` and `hw_translate_dcn315.c` use generated offsets/masks to build HPD/DDC/generic GPIO register tables and to translate GPIO IDs to MMIO offsets. The HPD blocks in this chunk are the register-address side for that hotplug handling.
- `dcn315_resource.c` constructs the DCN315 resource pool, IRQ service, DIO, and stream encoders. Its display objects ultimately rely on these generated offsets for timing generators, OPPs, link encoders, digital encoders, audio/HDMI packet registers, and panel/backlight control paths, even when the register tables are assembled through inherited DCN3.x macros.
- Clock-manager, DML, and HWSS code do not necessarily include this header directly, but their modeset and bandwidth decisions are realized through the OPP/OPTC/DIO/ABM register programming described by these offsets.

## Risks And Edge Cases

- Generated macro drift is the main risk. A wrong offset or base index compiles cleanly but can program the wrong MMIO address, causing display corruption, missed interrupts, bad link training, audio failure, or hangs.
- The chunk boundaries are artificial. The previous chunk owns the start of the ABM0 block, and the next chunk owns the `_BASE_IDX` for `DIG2_HDMI_DB_CONTROL` plus the rest of DIG2. File-level reconciliation must merge adjacent chunks before making complete claims about ABM0 or DIG2.
- Base-index mistakes are as dangerous as offset mistakes. The same small register offset added to the wrong `DCN_BASE__INST0_SEG*` segment targets a different hardware island.
- ABM/PWM offsets are panel-facing. Bad address constants can produce incorrect brightness transitions, broken adaptive backlight behavior, stale histogram reads, or register-lock misuse.
- OPP/FMT/CRC offsets affect pixel output. Wrong formatter or OPP pipe addresses can break color expansion, dithering, 4:2:0/4:2:2 behavior, pipe enablement, blanking, or CRC diagnostics.
- OTG/OPTC offsets are timing-critical. Misaddressed totals, blanking, sync, trigger, lock, vline, or vupdate registers can create unstable modesets, missed flips, stuck interrupts, or visible timing glitches.
- HPD offsets are interrupt-sensitive. Incorrect status, control, filter, or ack addresses can cause lost hotplug events, repeated HPD storms, failed HPDRX/AUX handling, or slow connect/disconnect detection.
- DP/DIG offsets are link- and audio-critical. Mistakes in training, MSA/MSE, secondary-data, DSC/MSO, ALPM, GSP, HDMI infoframe, ACR, AFMT, or TMDS addresses can prevent displays from lighting, break MST/DSC, corrupt metadata, or lose HDMI/DP audio.
- Perfmon and CRC blocks are diagnostic but side-effectful. Bad run, select, status, or ack offsets can make validation data misleading or leave performance/CRC interrupt state uncleared.

## Test Signals

Useful validation combines generated-header consistency checks, build checks, and hardware behavior:

- Build AMDGPU/DC with DCN315 enabled. Missing or renamed macros should fail at compile time in DCN315 DMUB, IRQ, GPIO, and resource code.
- Mechanically verify that every complete register macro in this chunk has a paired `_BASE_IDX`, allowing the known boundary exception for `regDIG2_HDMI_DB_CONTROL`.
- Compare this chunk against AMD's authoritative DCN 3.1.5 register database and adjacent DCN 3.1.x/DCN 3.6 offset headers where the hardware blocks are expected to stay layout-compatible.
- Exercise panel brightness and ABM paths: PWM duty programming, ambient/user/target/current/final level reads, histogram/luma readback, ABM lock behavior, and suspend/resume restore.
- Exercise OPP and formatter paths: modesets across color depths and pixel encodings, dithering, dynamic expansion, 420/422 conversion, CRC generation/readback, pipe blank/unblank, and multi-pipe operation.
- Exercise OTG/OPTC timing: vblank/vline/vupdate interrupts, global swap lock, vertical interrupt controls, double-buffer update timing, test-pattern generation, CRC windows, and static-screen controls across four timing generators.
- Exercise HPD handling on ports 0 through 4: connect/disconnect debounce, HPD IRQ acknowledgement, HPDRX interrupt routing, fast-training status reads, and repeated plug/unplug stress.
- Exercise DP link training and stream setup for DP0 through DP2: link control, training pattern transitions, MSA timing, MST allocation, DSC/MSO, secondary-data packets, ALPM, GSP packet controls, and link CRC diagnostics.
- Exercise DIG/HDMI paths: HDMI metadata, audio packet controls, infoframes, generic packets, ACR values, AFMT controls, TMDS setup, backend enable/disable, and forced digital disable. For DIG2, include the next chunk before validating the complete HDMI/audio register set.
- Exercise suspend/resume and display hotplug while active streams are running to catch stale base-index mappings, lost restore state, and interrupt ack mistakes.

## Cross-Chunk Notes

The previous chunk owns the beginning of `dce_dc_opp_abm0_dispdec`, including ABM0 PWM controls, ACE/luma setup, histogram bin controls, and `HG_RESULT_1` through `HG_RESULT_5`. This chunk starts at `regABM0_DC_ABM1_HG_RESULT_6`.

The next chunk owns `regDIG2_HDMI_DB_CONTROL_BASE_IDX` and the rest of the DIG2 HDMI/audio formatter/TMDS/backend register block. The final per-file research document should merge these boundaries before summarizing the complete ABM0 or DIG2 register inventories.

### subset-b-001863: lines 10229-12818

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h lines 10229-12818

## Purpose

This chunk is generated AMD DCN 3.1.5 display-controller register metadata. It is a C preprocessor offset header: each `reg...` macro names a hardware MMIO register offset, and each matching `reg..._BASE_IDX` macro selects the DCN base segment used to form the final address. The companion `dcn_3_1_5_sh_mask.h` header supplies field shifts and masks; this file supplies the register addresses consumed by AMDGPU display resource construction, GPIO/AUX/DDC helpers, IRQ setup, DMUB register access, link and stream encoders, panel control, DSC, and diagnostics.

Although the source path is under a local `ceph-client` mirror, this chunk is AMDGPU display-driver hardware metadata and has no distributed filesystem or Ceph behavior.

The requested range contains 2,378 `#define` lines: 1,189 register-offset macros and 1,189 `_BASE_IDX` macros. The equal count hides two artificial chunk-boundary splits: line 10229 starts with `regDIG2_HDMI_DB_CONTROL_BASE_IDX` while the corresponding offset is on line 10228, and line 12818 contains `regDME5_DME_CONTROL` while its `_BASE_IDX` is on line 12819.

## Register Blocks Covered

The chunk begins in the middle of the `DIG2` stream-encoder register block. It includes the base-index half of `DIG2_HDMI_DB_CONTROL`, then the rest of the DIG2 HDMI audio-clock-regeneration/status, AFMT top control, DIG backend control, TMDS, DIG version, and force-disable offsets.

It then covers full DisplayPort and DIG stream-encoder instances for `DP3`/`DIG3` and `DP4`/`DIG4`. The DP blocks include link control, pixel format, MSA colorimetry and timing, video stream control, DPHY controls, training pattern selection, symbols, 8b/10b, PRBS, scrambler, CRC, fast training, secondary-data packet/audio timing, MST/MSE scheduling, MSO, DSC handoff, metadata packet controls, DSC bytes-per-pixel, ALPM, GSP packet controls, and double-buffer status. The DIG blocks include front-end/backend controls, output CRC, clock/test/random pattern registers, FIFO/status, HDMI metadata and audio controls, infoframe and generic-packet controls, ACR programming for 32/44/48 kHz families, AFMT control, TMDS patterns/control characters/DC balance, version, and forced-disable.

The slice includes `AFMT0` through `AFMT5` audio-format blocks. `AFMT0` to `AFMT4` correspond to the legacy DIG instances, while `AFMT5` is under `dce_dc_hpo_hdmi_stream_enc0_afmt_afmt_dispdec`. These offsets cover VBI packet control, audio packet control, audio info registers, IEC 60958 channel-status registers, audio CRC, ramp controls, AFMT status, infoframe control, audio source control, and AFMT memory power.

It includes legacy `DME0` through `DME4` control offsets and `VPG0` through `VPG4` metadata/generic-packet blocks. The DME blocks are one control register per DIG instance in this range. The VPG blocks include generic packet access/data, frame-update control, immediate-update control, generic status, memory power, ISRC access/data, MPEG info, and SMU generic-packet status registers. The range also starts the HPO HDMI `DME5` block with `regDME5_DME_CONTROL`, but its base-index and memory-control lines are in the following chunk.

The `DP_AUX0` through `DP_AUX4` blocks provide per-channel AUX engine offsets for DisplayPort AUX/DDC-over-AUX transactions. Each includes AUX control, software control, arbitration, interrupt control, software/link-service status and data, DPHY TX/RX controls and status, GTC sync controls/status, and PHY wake control.

The shared DOUT I2C block provides display DDC/I2C controller offsets, including arbitration, control, interrupt, software status, DDC1 through DDC5 hardware status/speed/setup, transaction descriptors, data, EDID detect control, and read-request interrupt state.

The DIO miscellaneous block includes DIO scratch registers, memory-power status/control, clock controls, power-management control, DIG soft reset, HDMI RX-status timer control, generic interrupt message/clear, and link-type controls for DIO links A through F. The adjacent DIO perfmon block defines `DC_PERFMON18` counter-control, state, value, and high/low readback offsets.

The shared DCIO block exposes top-level display I/O controls: generic registers, clock/reference-clock controls, UNIPHY A through E link and channel crossbar controls, write-command delay, pinstraps, intercept state, BL PWM frame-start display select, genlock/swaplock pad controls, and DCIO soft reset. The DCIO-chip block exposes GPIO/pad registers for generic GPIO, DDC1 through DDC5, DDCVGA, genlock, HPD, panel power-sequence enables, pad strengths, AUX controls, TX/RX enables, pullups, PHY AUX control, and AUX/I2C pad power-good status.

The `UNIPHY0` through `UNIPHY4` address blocks publish `DCIO_UNIPHYx_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57`. The generated names intentionally do not describe individual PHY-control semantics; they provide stable addresses for per-PHY macro slots used by low-level PHY programming, debug, dumps, or silicon bring-up.

The `PWRSEQ0` and `PWRSEQ1` blocks cover panel power sequencing and backlight PWM. They include power-sequence GPIO controls, panel sequence control/state/delays/reference dividers, backlight PWM control/control2/period, PWM group-register lock, second reference divider, and spare state.

The `DSCC0`, `DSCC1`, and `DSCC2` blocks provide Display Stream Compression compressor offsets, including config/status, interrupt-control/status, PPS config 0 through 22, memory-power control, squared-error readbacks, max-absolute-error readbacks, rate-buffer fullness, rate-control-buffer fullness, and debug-bus rotate. The matching `DSCCIF0` through `DSCCIF2` blocks provide input-interface config offsets, `DSC_TOP0` through `DSC_TOP2` provide top-level DSC control/debug offsets, and `DC_PERFMON19` through `DC_PERFMON21` provide DSC perfmon register sets.

The final complete HPO-related blocks in this chunk are `HPO_TOP`, `DP_STREAM_MAPPER`, and HPO perfmon `DC_PERFMON22`. `HPO_TOP` provides top-level HPO clock and hardware control. `DP_STREAM_MAPPER_CONTROL0` through `CONTROL3` are shared by HPO DP stream encoders to route stream data to HPO links. `DC_PERFMON22` provides HPO performance-counter control and readback.

## Important APIs, Types, And Macros

This header has no functions, structs, enums, variables, includes, locks, allocations, or direct persistence APIs in this range. Its API is the generated macro naming contract:

- `reg<INSTANCE>_<REGISTER>` gives a register offset.
- `reg<INSTANCE>_<REGISTER>_BASE_IDX` gives the base segment index used by `BASE(...)`.
- Address-block comments identify the generated hardware block and its local base address.
- Instance prefixes such as `DP3`, `DIG4`, `AFMT5`, `DP_AUX2`, `DSCC1`, `PWRSEQ0`, and `DC_PERFMON22` are part of the public register-table contract.

The main include sites for this exact DCN315 header in this tree are:

- `display/dc/resource/dcn315/dcn315_resource.c`
- `display/dc/irq/dcn315/irq_service_dcn315.c`
- `display/dc/gpio/dcn315/hw_factory_dcn315.c`
- `display/dc/gpio/dcn315/hw_translate_dcn315.c`
- `display/dmub/src/dmub_dcn315.c`

`dcn315_resource.c` expands these offsets into static register tables. For this chunk, important table macros include `VPG_DCN31_REG_LIST(id)`, `AFMT_DCN31_REG_LIST(id)`, stream-encoder register lists, `DCN2_AUX_REG_LIST(id)`, `LE_DCN31_REG_LIST(id)`, `UNIPHY_DCN2_REG_LIST(phyid)`, `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST(id)`, HPO link-encoder register lists, and `DSC_REG_LIST_DCN20(id)`. The generated offsets are bound to block constructors such as VPG, AFMT, AUX, link encoder, stream encoder, HPO stream/link encoder, and `dsc2_construct()`.

`dcn31_afmt.h` consumes the AFMT offsets through `AFMT_DCN31_REG_LIST(id)`, selecting address macros such as `AFMTx_AFMT_INFOFRAME_CONTROL0`, `AFMTx_AFMT_AUDIO_PACKET_CONTROL`, `AFMTx_AFMT_AUDIO_SRC_CONTROL`, `AFMTx_AFMT_60958_0/1/2`, and `AFMTx_AFMT_MEM_PWR`. The fields are taken from instance-0 names in the sh/mask header, while these offset macros select the per-instance MMIO addresses.

`dcn31_vpg.h` consumes VPG offsets through `VPG_DCN31_REG_LIST(id)`, selecting generic-packet status/access/data/update and memory-power registers. HPO stream creation in `dcn315_resource.c` maps HPO DP stream encoders to VPG instances beyond the legacy DIG instances, so instance ordering in the generated VPG/AFMT/DME namespace is a real runtime contract.

`dcn20_dsc.h` defines `DSC_REG_LIST_DCN20(id)`, which uses the DSCC, DSCCIF, and DSC_TOP offsets from this chunk. DCN315 resource construction creates three DSC instances with `dsc2_construct(dsc, ctx, inst, &dsc_regs[inst], &dsc_shift, &dsc_mask)`, so the DSCC0/1/2 offsets are the address layer for the generic DCN20 DSC implementation on DCN 3.1.5 hardware.

`dcn301_panel_cntl.h` defines the panel-control register-list pattern for `PANEL_PWRSEQx_*` and `BL_PWMx_*` registers. The PWRSEQ offsets in this chunk are the DCN315 address surface for embedded-panel power sequencing and backlight PWM programming.

`dcn31_hpo_dp_stream_encoder.h` consumes the HPO DP stream mapper offsets with `SR(DP_STREAM_MAPPER_CONTROL0)` through `CONTROL3`, and per-HPO stream encoder offsets in later chunks. In this range, the stream mapper registers are the shared routing controls that connect HPO stream encoders to HPO links.

`dmub_dcn315.c` includes this header and computes register offsets with `REG_OFFSET_EXP(reg_name)`, which expands to `BASE(reg##reg_name##_BASE_IDX) + reg##reg_name`. Only the subset named by DMUB register-list macros is used there, but DMUB participates in the same generated DCN315 address namespace.

`irq_service_dcn315.c` includes this header and its sh/mask companion for interrupt-source address and field metadata. GPIO factory/translate code includes the header for HPD, DDC, generic GPIO, and related DCIO-chip register mappings.

## Control Flow

This chunk has no runtime control flow. It is pure macro data. Runtime control flow is table driven:

1. DCN315 resource, IRQ, GPIO, and DMUB code include `dcn_3_1_5_offset.h` and `dcn_3_1_5_sh_mask.h`.
2. Register-list helper macros such as `SR`, `SRI`, `SRIR`, and `SRII` paste instance IDs into generated macro names.
3. Static register tables store resolved offsets for VPG, AFMT, stream encoders, AUX engines, link encoders, HPO encoders, DSC, panel control, GPIO, IRQ, and DMUB-visible blocks.
4. Runtime block code uses those tables with register helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and DMUB register-access macros.

The header does not encode sequencing rules. Driver code and hardware documentation must supply ordering for DP link training, AUX transactions, HDMI/AFMT packet updates, DME/VPG metadata programming, panel power sequencing, DSC PPS setup, HPO stream/link mapping, clock/power gating, interrupt acknowledgement, and perfmon control.

## State And Persistence Behavior

The file stores no software state and persists nothing on disk. It describes MMIO-backed hardware state in DCN 3.1.5 display blocks.

Configuration state represented by this chunk includes DP link and DPHY programming, DIG/HDMI/TMDS stream-encoder setup, AFMT audio packet setup, DME and VPG metadata packet setup, AUX DPHY timing and arbitration, DOUT I2C/DDC setup, DIO clock/reset/memory-power controls, DCIO link and pin routing, GPIO/HPD/DDC/AUX pad controls, UNIPHY macro slots, panel power and backlight PWM timing, DSC PPS/config/memory power, HPO top controls, and HPO stream mapping.

Live status and telemetry represented by this chunk includes DP CRC/training/MSE status, DIG output CRC and FIFO/status state, AFMT status and CRC results, VPG generic-packet conflict/status bits, AUX software/link-service/DPHY/GTC status, DDC/I2C hardware and software status, DIO memory-power status, DCIO pad/power-good state, panel power-sequence current/target state, DSCC status/interrupt/error/fullness counters, and perfmon counter state/readbacks.

Persistence is hardware-defined. Some registers remain programmed until modeset, suspend/resume restore, power gating, block reset, or ASIC reset. Others are read-only status, sticky status, write-one-to-clear interrupt/status, self-clearing request, indexed-window data, double-buffered packet state, or counter readback. The offset header alone does not distinguish those access classes.

## Dependencies And Integration Points

The highest-impact dependency is synchronization with `dcn_3_1_5_sh_mask.h`. Register tables combine offsets from this file with fields from the sh/mask header. A stale offset with a valid field mask can compile while programming the wrong register or interpreting the wrong status bit.

The DCN315 resource path is the primary integration point. `dcn315_resource.c` builds arrays for VPG instances 0 through 9, AFMT instances 0 through 5, stream encoders 0 through 4, AUX engines 0 through 4, link encoders, HPO stream encoders, HPO link encoders, and DSC instances 0 through 2. This chunk supplies a large portion of those address surfaces, especially for legacy DIO, DCIO, PWRSEQ, DSC, HPO top/mapper, and HPO HDMI AFMT.

The GPIO path integrates the DCIO-chip DDC, HPD, AUX, generic GPIO, PWRSEQ enable, pad strength, pullup, TX/RX enable, and power-good offsets. These addresses are used for connector detection, hotplug routing, DDC line control, AUX pad state, and panel-related GPIO behavior.

The AUX and DOUT I2C paths integrate with EDID reads, DisplayPort link training, DisplayPort sideband/AUX transactions, I2C-over-AUX behavior, and legacy DDC. AUX registers are per-channel; DOUT I2C provides a shared controller with per-DDC speed/setup/status registers.

The link and stream encoder paths integrate DP, DIG, AFMT, DME, VPG, DCIO, and UNIPHY offsets with VBIOS connector data and runtime engine allocation. A single connector path can involve a DIG stream encoder, DP link block, AUX channel, DCIO UNIPHY/link/xbar controls, HPD GPIOs, AFMT audio block, VPG/DME metadata block, and possibly DSC or PWRSEQ state.

The panel-control path integrates `PWRSEQ0`/`PWRSEQ1` and `BL_PWM0`/`BL_PWM1` offsets with embedded-panel power and backlight operations. The field-level code lives in the panel-control implementation, but this chunk provides the DCN315 addresses for target/current state, DIGON/BLON, PWM enable, period, fractional count, lock, and reference-divider programming.

The DSC path integrates DSCC/DSCCIF/DSC_TOP offsets with Display Mode Library decisions and the generic DCN20 DSC hardware implementation. Higher layers decide whether DSC is needed and calculate PPS values; the register tables from this chunk are what allow the implementation to program PPS/config/status/memory-power and read compression diagnostics.

The HPO path integrates `HPO_TOP` and `DP_STREAM_MAPPER_CONTROL0-3` with HPO DP stream/link encoders. DCN315 advertises HPO DP capability in resource setup, and HPO stream creation maps stream encoders, VPG/APG metadata/audio resources, and stream-mapper controls together.

The DMUB path integrates generated offsets into firmware service register access. `dmub_dcn315.c` maps DCN315 register names to `struct dmub_srv_dcn31_regs`; common DCN31 DMUB operations then use those addresses for reset, firmware windows, mailboxes, GPINT, diagnostics, and timing.

The IRQ path integrates generated offsets and masks into DCN315 interrupt-service tables. AUX/DDC, HPD, DIO, DSC, perfmon, or related display events depend on the offset/mask namespace matching the silicon register map.

## Risks And Edge Cases

Generated-header drift is the main risk. A wrong offset or base index can compile cleanly but point register helpers at the wrong MMIO address. In this chunk, likely symptoms include DP link-training failures, AUX/DDC timeouts, wrong connector hotplug state, HDMI audio or infoframe breakage, metadata packet corruption, panel power/backlight failures, DSC enable failures, HPO stream-routing failures, or misleading diagnostics.

Instance ordering is fragile. `DP3`/`DP4`, `DIG3`/`DIG4`, `AFMT0-5`, `VPG0-4`, `AUX0-4`, `UNIPHY0-4`, `PWRSEQ0-1`, `DSCC0-2`, and HPO resources are assembled into arrays and selected by engine IDs, channel IDs, transmitter IDs, or instance arithmetic. An off-by-one mapping can target a different physical connector or encoder while all macro names remain valid.

The range starts and ends at split definitions. The previous chunk owns the offset for `DIG2_HDMI_DB_CONTROL`; this chunk owns its `_BASE_IDX`. This chunk owns the offset for `DME5_DME_CONTROL`; the next chunk owns its `_BASE_IDX` and `DME5_DME_MEMORY_CONTROL`. File-level reconciliation must merge adjacent chunks before claiming complete coverage of those registers.

UNIPHY reserved registers are intentionally opaque. The `RESERVED0` through `RESERVED57` names should be treated as address-window coverage, not self-documenting behavior. Over-interpreting those names in tests or documentation can lead to incorrect claims.

DP/AUX programming is timing-sensitive. AUX arbitration, DPHY timing, wake controls, interrupt/status handling, and DP training controls can fail due to stale status, incorrect clear semantics, power-state changes, or wrong channel routing. Offset errors here often appear as timeouts rather than clear software faults.

HDMI/AFMT/VPG/DME programming is stateful and often double-buffered or update-triggered. Wrong packet, infoframe, audio-source, channel-status, DME, or generic-packet offsets can cause silent audio loss, incorrect infoframes, HDR/metadata failure, or compliance failures without a kernel crash.

Panel PWRSEQ and BL PWM offsets are high risk because bad writes can produce black screen, flicker, long delays, or unsafe embedded-panel sequencing. The target/current-state readbacks must be interpreted with the right instance and timing.

DSC offsets are high impact for high-bandwidth modes. PPS/config mismatch, memory-power mistakes, or wrong DSCCIF/DSC_TOP addresses can make modes fail only when compression is required, and error/fullness counters can become misleading if read from the wrong instance.

HPO stream-mapper offsets affect DP 2.x style routing. Incorrect HPO top or stream-mapper addresses can map the stream to the wrong link target or prevent HPO stream encoder activation, especially because HPO stream and link resources are allocated separately.

## Test Signals

Useful validation starts with build coverage. A DCN315-enabled AMDGPU build should catch missing or renamed macros in `dcn315_resource.c`, `irq_service_dcn315.c`, `hw_factory_dcn315.c`, `hw_translate_dcn315.c`, and `dmub_dcn315.c`.

Generated-header consistency checks should verify that every register offset has a matching `_BASE_IDX`, allowing the known boundary exceptions at `DIG2_HDMI_DB_CONTROL` and `DME5_DME_CONTROL`. Checks should also compare offsets and base indexes against AMD's authoritative DCN 3.1.5 register database and adjacent generated DCN 3.1.x headers where instances are expected to match.

Runtime display validation should exercise DP and HDMI modes on all covered DIG/DP/AUX channels, including link training, EDID reads, HPD, DDC fallback, audio packet generation, HDMI infoframes, output CRC, compliance patterns, and suspend/resume restore.

AUX/DDC validation should include AUX native transactions, I2C-over-AUX, legacy DDC reads on DDC1 through DDC5, arbitration conflict handling, interrupt clear behavior, wake/power transitions, and error paths that expose stale or misrouted status.

Panel validation should exercise eDP or embedded-panel power sequencing, DIGON/BLON transitions, backlight PWM period and fractional brightness programming, register-lock/update-pending behavior, and suspend/resume or backlight restore.

DSC validation should enable compressed modes on DSC instances 0 through 2, verify PPS programming, DSCCIF/top enablement, memory-power transitions, interrupt/status behavior, squared-error and max-abs-error readbacks, and rate-buffer/fullness counters.

HPO validation should exercise HPO DP stream allocation, stream mapper target selection, HPO top clock/hardware control, HPO perfmon counters, and mixed legacy/HPO resource use.

Diagnostic validation should read DIO, DSC, and HPO perfmon counters; DIO scratch/memory-power state; AFMT/VPG status; AUX status; and DSCC error/fullness counters to confirm that register tables point at the expected hardware instances.

## Cross-Chunk Notes

The previous chunk must be consulted for the `regDIG2_HDMI_DB_CONTROL` offset paired with the first line of this range. The next chunk must be consulted for `regDME5_DME_CONTROL_BASE_IDX` and the rest of the HPO HDMI DME5 block. The final per-file research document should merge those boundaries before making complete claims about DIG2 HDMI DB control or HPO HDMI DME5 coverage.

### subset-b-001864: lines 12819-15195

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h lines 12819-15195

## Purpose

This chunk is generated AMD DCN 3.1.5 register-address metadata. It contains no executable C logic; it publishes preprocessor constants for hardware register offsets, indexed-register offsets, and per-register base-segment selectors used by AMDGPU display code. The companion `dcn_3_1_5_sh_mask.h` header supplies field shifts and masks for the same register namespace.

Although this source tree is under a local `ceph-client` mirror, this file is AMDGPU display-driver hardware metadata and has no Ceph or distributed filesystem behavior.

The requested range is the tail of the file. It starts inside the HPO HDMI stream encoder 0 DME block, then covers HPO HDMI VPG5, HPO DP stream encoders 0 through 3, APG0 through APG3, DME6 through DME9, VPG6 through VPG9, DP 32-symbol encoders 0 through 3, HPO DP link encoders 0 through 1, DP DPHY SYM32 blocks 0 through 1, DCHVM, HDA/Azalia controller/root/stream/endpoint/input-endpoint registers, legacy VGA indexed windows, and indexed Azalia endpoint windows. The chunk has 2,042 `#define` lines: 1,555 register or indexed-register offset constants and 487 `_BASE_IDX` constants.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, locks, allocations, or direct persistence APIs in this line range. Its public interface is the generated macro naming convention:

- `reg<REGISTER_OR_BLOCK_REGISTER>`: MMIO register offset within a generated base segment.
- `reg<REGISTER_OR_BLOCK_REGISTER>_BASE_IDX`: segment selector consumed by `BASE(reg..._BASE_IDX)` helper macros.
- `ix<INDEXED_REGISTER>`: indexed-register offset used through an index/data register window rather than direct MMIO.

Important register families in this chunk:

- HPO HDMI residual blocks: the chunk begins with the final `DME5_DME_CONTROL` base selector and `DME5_DME_MEMORY_CONTROL`, then lists `VPG5` generic packet access/data, frame/immediate update controls, status, memory power, ISRC data, and MPEG info registers for HPO HDMI stream encoder 0.
- HPO DP stream encoders 0 through 3: `DP_STREAM_ENC*_DP_STREAM_ENC_CLOCK_CONTROL`, input mux, audio control, clock-ramp FIFO status/control, and spare registers.
- DP APG and DME blocks: `APG0` through `APG3` audio packet generator control/status/debug/CRC/memory-power/spare registers and `DME6` through `DME9` control and memory-control registers.
- DP VPG blocks: `VPG6` through `VPG9` generic packet access/data, GSP update controls, status, memory power, ISRC, and MPEG info registers.
- DP SYM32 encoders 0 through 3: control, FIFO control, MSA double-buffer and MSA0 through MSA8, pixel format, HBLANK, SDP/GSP controls, audio/metadata packet controls, stream/VBID/panel replay, CRC control/results/status, memory-power, and spare registers.
- HPO DP link and DPHY blocks: link-encoder control, vid/audio stream enables, link-test pattern, training, error-status, CRC, clock controls, main-link channel coding, PHY control, and DPHY SYM32 control/status/debug/test/CRC/memory-power registers.
- `DCHVM`: display core host-VM control, aperture, fault address, VMID, and memory power registers.
- HDA/Azalia direct registers: controller capability/status/control, DMA/RIRB/CORB, stream descriptors 0 through 7, root codec parameters, audio DTO, audio wall-clock, clock gating, CRC controls/results, endpoint and input-endpoint index/data windows, and memory-power control/status.
- Legacy VGA indexed windows: sequencer, CRT controller, graphics controller, and attribute-controller indexed constants.
- Azalia indexed windows: codec function, descriptor, sink info, stream 0 through 15, endpoint 0 through 7, and input endpoint 0 through 7 indexed register constants.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code that includes this generated DCN 3.1.5 offset header and expands register-list macros.

Typical flow:

1. DCN315 resource, DMUB, IRQ, and GPIO code include `dcn_3_1_5_offset.h` together with `dcn_3_1_5_sh_mask.h`.
2. Resource code expands `SR`, `SRI`, `SF`, `SE_SF`, and related token-paste helpers into register tables. For example, `dcn315_resource.c` builds audio, VPG, AFMT, APG, stream encoder, HPO DP stream encoder, HPO DP link encoder, hardware sequencer, and VMID register tables.
3. HPO DP stream-encoder helpers use `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST(id)` with `SRI(DP_STREAM_ENC_..., DP_STREAM_ENC, id)` and `SRI(DP_SYM32_ENC_..., DP_SYM32_ENC, id)`, so the DP stream and SYM32 offsets in this chunk become concrete addresses for instances 0 through 3.
4. Audio helpers use `AUD_COMMON_REG_LIST(id)` and DCN315-specific masks to create Azalia endpoint register tables. Indexed `ixAZF0ENDPOINT*` and `ixAZF0INPUTENDPOINT*` constants describe the codec windows reached through endpoint index/data registers.
5. Runtime display, link, audio, interrupt, and firmware paths then use the populated tables through register access helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_GET`, and Azalia index/data access wrappers.

The offsets do not encode ordering or access side effects. Consumers must still follow hardware programming sequences around clock enablement, reset assertion/release, FIFO reset completion, stream disable/enable, packet double buffering, indexed-window address/data ordering, audio DMA/ring management, hotplug behavior, memory power gating, and suspend/resume restore.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on disk. It names MMIO and indexed registers whose values live in GPU display hardware.

State represented by these definitions includes:

- HPO DP and HDMI packet state: generic packet RAM access, GSP frame/immediate update controls, ISRC and MPEG metadata, VPG/DME memory power, and stream packet status.
- HPO DP stream and symbol state: stream encoder clocks, pixel/audio input muxing, clock-ramp FIFO reset/enable/status, DP SYM32 reset/enable, pixel format, MSA data, HBLANK policy, SDP/GSP packet controls, audio sideband packet enables, metadata packet enables, VBID and panel replay state, CRC controls/results, and memory power.
- DP link/PHY state: link-encoder enable and training controls, channel coding, test patterns, CRC, error status, DPHY test/debug/status controls, and link/PHY memory power.
- HDA/Azalia state: controller command/status, CORB/RIRB/DMA positions, stream descriptor buffer and format registers, codec root parameters, audio wall-clock and DTO configuration, audio CRC, endpoint/input endpoint index/data windows, sink-info and descriptor indexed data, and codec power/reset/connectivity fields.
- Legacy VGA indexed state: sequencer, CRT controller, graphics controller, and attribute-controller index spaces that can still be exposed for VGA compatibility paths.
- DCHVM state: host VM aperture, fault address/VMID reporting, and host-VM memory power/control registers.

Persistence is hardware-defined. Some registers are configuration values that remain until modeset, reset, power gating, suspend/resume, or ASIC reset. Others are read-only status, sticky error, write-one-to-clear, self-clearing request, or index/data window entries. This generated offset header does not express those access classes; the display code and ASIC documentation supply that context.

## Dependencies And Integration Points

This chunk must match the generated DCN 3.1.5 register database and its companion field-layout header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h`

Direct include sites found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`

Key integration points:

- `dmub_dcn315.c` expands `DMUB_DCN31_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_DCN315_FIELDS()` into `dmub_srv_dcn315_regs`. This chunk is mostly outside the DMCUB-specific register list, but it shares the same `BASE(reg..._BASE_IDX) + reg...` contract used throughout the generated file.
- `dcn315_resource.c` directly uses HPO DP stream encoder offsets from this chunk via `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST(id)` and `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST`. It also uses Azalia endpoint offsets through `audio_regs[]`, `DCE120_AUD_COMMON_MASK_SH_LIST`, `AZALIA_AUDIO_DTO`, and hardware sequencer register lists.
- `dcn31_hpo_dp_stream_encoder.h` defines the common DCN3.1 HPO DP stream-encoder register and field lists that token-paste names such as `DP_STREAM_ENC0_DP_STREAM_ENC_CLOCK_CONTROL` and `DP_SYM32_ENC0_DP_SYM32_ENC_CONTROL`; those exact instance-0 names and instance-specific offsets are present in this chunk.
- `dce_audio.h` and `dce_audio.c` use `AZF0ENDPOINT*` endpoint index/data registers to program codec capabilities, rates, power-state bits, hotplug control, ELD/sink information, and audio format behavior.
- `irq_service_dcn315.c` and GPIO translation/factory code include the same offset header to build IRQ and GPIO register tables. Their direct use is mostly in earlier line ranges, but they depend on the whole header remaining a coherent generated unit.

## Risks And Edge Cases

- Generated offset drift is the main risk. A wrong constant compiles cleanly but causes register helpers to access the wrong MMIO address or indexed slot.
- The chunk starts in the middle of the `dce_dc_hpo_hdmi_stream_enc0_dme_dme_dispdec` block. The `regDME5_DME_CONTROL` offset and address-block comment are in the previous chunk, while `regDME5_DME_CONTROL_BASE_IDX` and `regDME5_DME_MEMORY_CONTROL` are here. File-level reconciliation must merge the adjacent chunk before treating DME5 as complete.
- HPO DP stream/SYM32 offsets are modeset critical. Bad clock-control, input-mux, FIFO reset/status, reset-done, pixel-format, MSA, stream-enable, VBID, HBLANK, or packet-control offsets can cause a blank display, link-training failures, malformed sideband data, incorrect audio packetization, or CRC diagnostics that point at the wrong block.
- VPG/APG/DME packet registers are update-order sensitive. Generic packet RAM access and frame/immediate update controls must be programmed with the expected double-buffer or frame-boundary semantics, otherwise infoframes, ISRC data, MPEG metadata, and audio packets can be stale or torn.
- HPO DP link and DPHY offsets affect physical link behavior. Wrong training, test-pattern, channel-coding, CRC, or error-status addresses can make link bring-up fail or hide real PHY faults.
- Azalia has both direct MMIO and indexed-register windows. Mixing endpoint instances, index constants, or data-window offsets can program the wrong codec node, stream descriptor, sink info, channel allocation, hotplug control, or power-state register.
- Audio stream descriptor registers are DMA-facing. Incorrect `AZSTREAM*` buffer, length, format, control, status, or LPIB offsets can corrupt audio playback/capture state or leave DMA/ring interrupts stuck.
- Legacy VGA indexed constants may look obsolete but still participate in compatibility paths. Wrong VGA index values can disturb low-level display state during firmware handoff, resume, or fallback modes.
- Memory power control registers for VPG/APG/SYM32/DPHY/Azalia/DCHVM must be touched only when the corresponding block is idle or in the documented transition sequence.

## Test Signals

Useful validation combines build checks, generated-header consistency checks, and hardware behavior:

- Build AMDGPU/DC with DCN315 enabled. Missing or renamed macros should fail in `dmub_dcn315.c`, `irq_service_dcn315.c`, `hw_factory_dcn315.c`, `hw_translate_dcn315.c`, and `dcn315_resource.c`.
- Mechanically verify that every direct `reg...` macro in this chunk that represents an MMIO register has the expected `_BASE_IDX` companion, while allowing indexed `ix...` constants and the known DME5 boundary split.
- Compare the offsets against AMD's authoritative DCN 3.1.5 register database and adjacent generated DCN 3.1.x headers where register layouts are expected to remain compatible.
- Exercise HPO DP modesets on all available stream/link encoder instances: clock enable, FIFO reset/done polling, pixel/audio stream muxing, MSA programming, SDP/GSP metadata packets, audio sideband packets, stream enable/disable, HBLANK control, panel replay bits, and CRC readback.
- Exercise HPO HDMI/DP packet paths: VPG generic packet RAM access, ISRC/MPEG infoframes, GSP frame/immediate updates, APG audio packet control/status, and DME memory-control transitions.
- Exercise DP link and PHY diagnostics: link training, test patterns, channel coding, CRC, DPHY status/error/debug registers, and memory power transitions.
- Exercise HDMI/DP audio through Azalia: endpoint index/data accesses, codec capability reads, supported rate/power-state reads, stream descriptor setup, CORB/RIRB behavior, DMA position/LPIB reporting, hotplug control, channel allocation, ELD/sink info, audio DTO, and audio CRC.
- Exercise suspend/resume and display power-gating paths that touch VPG/APG/SYM32/DPHY/Azalia/DCHVM memory-power registers and ensure registers are restored or reprogrammed in the expected order.
- Exercise legacy VGA handoff or fallback modes, if supported, to catch regressions in sequencer/CRT/graphics/attribute indexed windows.

## Cross-Chunk Notes

The previous chunk owns the beginning of the HPO HDMI stream encoder 0 DME5 block, including the address-block comment and `regDME5_DME_CONTROL` offset. This chunk owns the DME5 tail, the rest of the file's offset/index definitions, and the final `#endif`. The final per-file research document should merge adjacent chunks before making complete claims about DME5 coverage or full-file generated-header structure.
