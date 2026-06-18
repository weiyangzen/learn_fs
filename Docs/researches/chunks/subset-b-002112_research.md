# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h lines 1-2652

## Scope

This chunk covers the opening 2,652 lines of the generated AMD DCN 3.6.0 register-offset header. The full source file continues after this chunk; this report only describes the address blocks and macros visible in lines 1-2652.

The chunk defines a guarded C preprocessor header, `_dcn_3_6_0_OFFSET_HEADER`, and then emits register address constants for AMD display hardware. There is no executable C logic, no functions, and no runtime data allocation in this chunk. The useful API surface is the macro namespace: each visible hardware register is represented as `reg...` and normally paired with `reg..._BASE_IDX`. In this range I counted 1,183 non-`BASE_IDX` register offset macros and 1,182 `BASE_IDX` macros; the remaining `#define` is the include guard.

## Purpose

The header gives DCN 3.6 display-driver code compile-time names for memory-mapped hardware register offsets. Consumers do not use the raw numeric offsets alone. They combine each `reg...` offset with its `reg..._BASE_IDX` through `ctx->dcn_reg_offsets[]` to compute a final MMIO register address for the active ASIC instance.

This chunk covers these functional areas:

- HDA/Azalia controller, endpoint, stream, and audio codec register windows.
- DCCG display clock generation, DTO, clock-gating, soft-reset, audio DTO, and perfmon registers.
- DMU, RBBMIF, display interrupt controller, display power-gating domains, and DMCUB firmware-visible registers.
- DWB display writeback top/color-pipeline registers, MCIF writeback memory interface registers, and MMHUBBUB registers.
- DCHUBBUB arbitration, SDPIF/VM aperture, return path, VM request interface, and perfmon registers.
- HUBP0 and the beginning of HUBP1 surface-fetch register groups, including HUBPREQ, HUBPRET, cursor, flip, VM, timing, prefetch, and performance registers.

## Macro API And Data Model

Every register definition follows the generated pattern:

- `regNAME` is a register offset, often relative to an address block.
- `regNAME_BASE_IDX` selects a base segment from `ctx->dcn_reg_offsets[]`.
- The address block comments preserve generator metadata: `// addressBlock: ...` and `// base address: ...`.

The key consumer-side expansion pattern is visible in DCN 3.6 code:

- `dmub/src/dmub_dcn36.c` defines `REG_OFFSET_EXP(reg_name)` as `BASE(reg##reg_name##_BASE_IDX) + reg##reg_name`, then fills DMUB register tables in `dmub_srv_dcn36_regs_init`.
- `dc/resource/dcn36/dcn36_resource.c` defines `SR`, `SRI`, `SRII`, `SRII_DWB`, and related helper macros that token-paste these `reg...` names into typed register tables for hardware blocks.
- `dc/irq/dcn36/irq_service_dcn36.c` uses `SRI` and `SRI_DMUB` to build IRQ enable/ack register entries from the same offset/base-index namespace.

The header depends on matching field masks/shifts in `dcn_3_6_0_sh_mask.h`; offsets alone identify register locations, while the sibling mask header identifies bitfields inside those registers.

## Address Block Map In This Chunk

The chunk starts with an absolute-looking HDA/Azalia decoder window at base `0x1300000` and base index `3`, then shifts mostly to display-register base indices `1` and `2`. Some HDA controller aliases also use base indices `0` and `1`. The main block counts are:

- HDA/Azalia decoder blocks: global controller registers, endpoint immediate command data/index windows, input endpoint immediate command windows, CORB/RIRB DMA queues, immediate command/response registers, DMA position buffers, wall clock aliasing, and duplicated controller windows for controller 0 and 1.
- DCCG: 110 visible DCCG display clock registers plus `DENTIST_DISPCLK_CNTL`; includes pixel-rate controls for OTG0-3, DP DTO phase/modulo, PHY PLL resync controls, DSC/DPP/DTB clock DTO controls, clock-gating controls, global timers, audio DTO controls, VSYNC latch/counter registers, soft reset, and SYMCLK controls.
- DC perfmon instances: `DC_PERFMON0` through `DC_PERFMON7` appear at different block bases, each with the standard counter control, state, value, high, and low register pattern.
- DMU/RBBMIF/IHC/power: RBBMIF timeout/status/error status registers, display interrupt status continuation registers `DISP_INTERRUPT_STATUS_CONTINUE` through `CONTINUE25`, interrupt destinations for major display subunits, DMU misc clocks/interrupts/ZSC, and `DOMAIN*_PG_CONFIG`/`DOMAIN*_PG_STATUS` power-gating registers.
- DMCUB: region offsets/top-address registers, region 3 code-window base/top/offset pairs, interrupt enable/ack/status/type, fault addresses, security/memory controls, inbox/outbox base/size/read/write pointers, timer triggers, scratch registers 0-23, GPINT data registers, low-power wake, memory power, processor ID, and control registers.
- DWB and MCIF writeback: DWB clock/memory/update/CRC/output/overflow/soft-reset controls, gamut-remap matrix registers, output gamma LUT control and RAM A/B piecewise region tables, MCIF writeback buffer manager state, buffer addresses and high-address halves, luma/chroma sizes, VMID/security/QOS/P-state/watermark controls.
- MMHUBBUB: warmup config/address region, writeback watermarks, memory power and clock controls, client unit ID, SMU watermark control, outstanding counters, and interface error status.
- Azalia display audio: controller clocking, DTO, DMA, payload, CRC, stream arbiter, memory power, codec root parameters, channel/count/control registers, GTC group offsets, port connectivity, 16 stream index/data windows, 8 output endpoint index/data windows, and 8 input endpoint index/data windows.
- DCHUBBUB: arbitration outstanding/saturation/QOS, per-watermark-set A-D urgency and retraining watermarks, self-refresh enter/exit including Z8 variants, UCLK/FCLK P-state watermarks, fractional urgent bandwidth, host VM, MALL, timeout, global timer, surface-check addresses, VTG controls, soft reset, DCF clock, performance measurement, vline snapshot, and timeout interrupt status.
- DCHUBBUB SDPIF/VM/return-path: SDPIF config, physical VM request, forced IO status, framebuffer and AGP aperture bounds, local HBM address lock/ranges, per-pipe security/noalloc settings, request rate limit, memory power status, return path memory power, CRC values, DCC stats, compbuf/detector controls, debug control, and VM fault registers.
- VM request interface: contexts 0-15 each expose control, page-table base high/low, page-table start high/low, and page-table end high/low. The block also includes default address and fault status/address registers.
- HUBP0 and start of HUBP1: HUBP0 surface config/address/tiling/viewports/request-size/control/clock/MALL/debug/measurement/status registers; HUBPREQ0 surface pitch/address/meta address/flip/in-use/TTU/VM/prefetch/vblank/flip/nominal/per-line/cursor/status registers; HUBPRET0 read-line and interrupt registers; CURSOR0 surface, size, position, hot spot, memory power, and DMDATA registers. The chunk ends in the middle of the HUBP1 block after `regHUBP1_HUBP_MEASURE_WIN_CTRL_DCFCLK`.

## Control Flow

There is no runtime control flow in this header. The effective flow is preprocessor expansion:

1. A DCN 3.6 source file includes `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`.
2. That source defines local token-pasting helpers such as `SR`, `SRI`, `SRII`, or `REG_OFFSET_EXP`.
3. Hardware object register-list macros expand through those helpers.
4. The generated `reg...` and `reg..._BASE_IDX` constants become concrete offsets in driver register tables.
5. Later runtime code reads/writes those computed addresses through the AMD display register access helpers.

Because the addresses are created at compile time and table-initialization time, wrong macros generally manifest as misprogrammed MMIO rather than normal C control-flow failures.

## State And Persistence Behavior

The header itself holds no mutable software state and persists nothing. It names persistent hardware state locations:

- DMCUB inbox/outbox pointers and scratch registers are persistent hardware/firmware communication state while the device is running.
- HUBP/HUBPREQ surface address, flip, in-use, cursor, VM, and prefetch registers describe display scanout state.
- DCHUBBUB arbitration, VM, watermark, P-state, and memory-power registers influence memory fetch behavior and power transitions.
- Azalia CORB/RIRB, stream, endpoint, DTO, and codec registers represent audio command, DMA, stream, and codec state.
- Perfmon and CRC registers expose measurement/test state that can be read by diagnostics.

Reset, suspend/resume, power-gating, display mode set, flip, audio enablement, and DMCUB firmware initialization paths rely on these addresses matching the ASIC register map.

## Dependencies And Integration Points

Primary dependencies:

- `dcn_3_6_0_sh_mask.h` must define compatible bit masks and shifts for the same register names.
- DCN 3.6 resource construction uses this header to populate per-block register tables in `dcn36_resource.c`.
- DMUB service initialization uses DMCUB-visible offsets in `dmub_dcn36.c`.
- DCN 3.6 IRQ setup uses interrupt control/status offsets in `irq_service_dcn36.c`.
- Hardware object headers from DCN 3.5/3.6 families provide register-list macros that expect exact token names such as `HUBP0_DCSURF_SURFACE_CONFIG`, `DMCUB_INBOX0_BASE_ADDRESS`, and `DCHUBBUB_ARB_DATA_URGENCY_WATERMARK_A`.

The base-index indirection is a critical integration point. For example, many visible display registers use base index `2`, DCCG registers often use base index `1`, and the initial HDA decoder window uses base index `3`. Consumers must initialize `ctx->dcn_reg_offsets[]` correctly for the ASIC; this header assumes that mapping is valid.

## Risks

- Offset/base-index drift: If a `reg...` offset is correct but its `BASE_IDX` is wrong, the computed MMIO address targets the wrong segment. This is especially risky where similar numeric offsets recur under different base indices, such as the HDA/Azalia decoder and display-register windows.
- Token-name contract: Consumer macros rely on token pasting. Renaming or omitting a generated macro breaks compilation or silently excludes a register from a table if a higher-level list macro changes.
- Cross-header mismatch: `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h` must be generated from the same register source. A stale mask header can compile but write wrong bitfields into otherwise correct offsets.
- Repeated instance patterns: Blocks such as Azalia streams/endpoints, VM contexts 0-15, perfmon instances, and HUBP instances are easy to mis-generate by one index. The visible HUBP1 block is incomplete in this chunk, so whole-file reconciliation must verify later chunks finish the repeated HUBP1 pattern and subsequent instances.
- Hardware behavior risk: Many macros address memory power, clock gating, power-gating, VM page tables, security levels, and firmware communication. Wrong values in these areas can cause display hangs, memory faults, audio failures, or suspend/resume regressions.
- Generated-file review risk: The file is large and mostly repetitive, so line-by-line human review is unlikely. Automated diffing against authoritative register XML or previous ASIC headers is more important than style review.

## Test Signals

Useful validation signals for this chunk are mostly build-time, boot-time, and hardware-display behavior:

- Compile DCN 3.6 display code with `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`; token-paste macros in DMUB, IRQ, and resource initialization should resolve without missing-register errors.
- Compare generated offsets/base indices against AMD's source register database or adjacent DCN headers for expected deltas. Spot checks in this chunk show common anchors shared with nearby ASIC generations, such as `regDMCUB_INBOX0_BASE_ADDRESS` at `0x01d0`, `regDCHUBBUB_ARB_DATA_URGENCY_WATERMARK_A` at `0x04fe`, and `regHUBP0_DCSURF_SURFACE_CONFIG` at `0x05e5`.
- Exercise display mode set, page flip, cursor movement, DMCUB command submission, hotplug/HPD interrupt handling, and audio stream enablement on DCN 3.6 hardware.
- Check debug/perf counters, CRC registers, DMCUB outbox interrupts, VM fault status, and DCHUBBUB timeout status under stress tests for signs of bad register targeting.
- Run suspend/resume and power-management tests that cover DCCG clock gating, DMCUB memory power, DCHUBBUB/HUBPREQ memory power, DCPG domains, and Azalia memory power controls.

## Chunk Boundary Notes

The chunk begins at the SPDX/license/header guard and ends after the first 21 register macros in `dce_dc_dcbubp1_dispdec_hubp_dispdec`. Later chunks must continue HUBP1 and likely additional HUBP/DPP/OPP/OTG/DIO/DSC-related register blocks. Merge should preserve that this chunk establishes the global header shape, base-index convention, and the early display/audio/memory/firmware register groups.
