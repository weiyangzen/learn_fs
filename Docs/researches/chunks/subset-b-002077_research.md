# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 46527-48843

## Scope

This chunk is part of the generated DCN 3.5.0 ASIC register field header for the AMDGPU display stack. It contains only preprocessor constants: 2,218 `#define`s, arranged as 1,109 `__SHIFT` macros paired with 1,109 mask macros for bitfields in display/audio/power/color-management registers. The chunk is not executable code, but it is consumed by the register-access macro layer to build typed shift/mask tables used by DC, DMUB, hubbub, hubp, irq, and MPC code.

## Purpose

The macros encode bit positions and masks for the tail of the DCN 3.5.0 register map. Drivers combine these constants with register offsets from the sibling `dcn_3_5_0_offset.h` file through helpers such as `FD_MASK`, `FD_SHIFT`, `REG_UPDATE`, `REG_GET`, `HUBBUB_SF`, `HUBP_SF`, and `SF`. This chunk covers:

- Azalia/HDA command, response, stream, global capability, interrupt, and DMA-position fields.
- Display clock, symbol clock, stream synchronization, DCCG, DMU, DMCUB, and DWB clock-gating controls.
- DCHUBBUB arbitration, watermark, P-state, C-state, USR retraining, SDPIF security, and MALL controls.
- HUBP0-HUBP3 page-table, MALL, debug, pstate-force, status, and read-line fields.
- Display power-gating domains 22-25 and DCPG interrupt status/control fields.
- MPCC/MCM color-management registers, especially shaper LUTs, 3DLUT/1DLUT RAM programming fields, region descriptors, and memory power-state controls.

## Important API Surface

There are no functions or types in the chunk. The API surface is macro names with the pattern:

- `REGISTER__FIELD__SHIFT`, whose value is the starting bit number.
- `REGISTER__FIELD_MASK`, whose value is the field mask in the register.

Important register families visible in this range include:

- `AZCONTROLLER1_*`, `AZENDPOINT1_*`, `AZINPUTENDPOINT1_*`, `AZALIA_*`, `GLOBAL_*`, `INTERRUPT_*`, `STREAM_SYNCHRONIZATION`, and `WALL_CLOCK_COUNTER` for HDA/Azalia command rings, RIRB/CORB DMA, immediate commands, payload capability, interrupts, stream sync, and wall clock state.
- `DCCG_GATE_DISABLE_CNTL*`, `DPPCLK_CTRL`, `DSCCLK_DTO_CTRL`, `PHY*SYMCLK_CLOCK_CNTL`, `SYMCLK*`, `DMU_CLK_CNTL`, `DMCUB_SMU_INTERRUPT_CNTL`, `ZSC_CNTL`, `ZPR_CLK_UNGATE_DELAY`, and `DWB_ENABLE_CLK_CTRL` for clock source selection, DTO enables, fine-grain clock-gating repetition disables, clock-stop allowance, and low-power LONO controls.
- `DCHUBBUB_ARB_*`, `DCHUBBUB_SDPIF_*`, `COMPBUF_MEM_PWR_CTRL_2`, `MMHUBBUB_CLOCK_CNTL`, `MCIF_WB_*`, and `SDPIF_REQUEST_RATE_LIMIT` for display memory arbitration, pstate watermark programming, security levels, compression-buffer latency, writeback pstate latency, and request throttling.
- `HUBP[0-3]_*`, `HUBPREQ[0-3]_*`, and `HUBPRET[0-3]_*` for each display pipe's HUBP VM/page-table behavior, MALL selection and status, debug status, UCLK pstate forcing, self-refresh/pstate/USR status signals, and vblank read-line limits.
- `DOMAIN22_PG_*` through `DOMAIN25_PG_*`, `DCPG_INTERRUPT_STATUS_3`, `DCPG_INTERRUPT_CONTROL_2`, and `DCPG_INTERRUPT_CONTROL_3` for power-gating state and interrupt mask/clear pairs.
- `MPCC[0-3]_MPCC_MOVABLE_CM_LOCATION_CONTROL` and `MPCC_MCM[0-1]_*` for movable color-management location, shaper controls, offsets/scales, shaper LUT RAM A/B regions, 3DLUT mode/read-write/data/index, post-1DLUT RAM A/B region tables, and MPCC MCM memory power controls.

## Control Flow and Data Flow

This header contributes compile-time constants only. Runtime control flow happens in consumers:

- DCN 3.5 initialization code includes this header beside `dcn_3_5_0_offset.h`, then expands register-list macros into per-block register, mask, and shift structures. For example, `dmub_srv_dcn35_regs_init()` initializes DMUB/DCN35 register offsets and fills `mask`/`shift` fields using `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)`.
- Display block code uses macros such as `HUBBUB_SF(...)`, `HUBP_SF(...)`, and `SF(...)` to map these constants into block-specific `*_shift` and `*_mask` structures. Later `REG_UPDATE_*`, `REG_GET`, `REG_SET_*`, and similar helpers apply the masks and shifts to memory-mapped I/O reads/writes.
- Color-management programming in the MPC path depends on the MPCC/MCM fields here to write LUT indices, LUT data, 3DLUT RAM selection, shaper region descriptors, and post-1DLUT RAM A/B tables. The generated constants decide the exact bit packing, but the algorithms and sequencing live in MPC source files.
- Hubbub and HUBP watermarks/MALL/pstate decisions are made elsewhere; this chunk only provides the bit positions for controls and status reads such as `DCHUBBUB_ARB_USR_RETRAINING_CNTL`, `HUBP*_HUBP_MALL_STATUS`, and `HUBPREQ*_HUBPREQ_STATUS_REG*`.

## State and Persistence

The header itself stores no state and persists nothing at runtime. The values describe persistent hardware register fields:

- Writes to control bits persist in MMIO registers until reset, power-gate transitions, firmware, or later driver writes alter them.
- Status bits expose current hardware state, interrupt latch state, or clear-on-write behavior depending on the register family. Examples in this chunk include RBBMIF invalid-access status, CORB/RIRB memory-error/response interrupts, domain power up/down status, DMCUB interrupt status, HUBP MALL status, and HUBPREQ pstate/self-refresh/flip status.
- LUT and color-management data fields drive hardware RAM programming. Index/data/write-enable fields are stateful hardware interfaces, so incorrect shift/mask constants would corrupt LUT writes rather than just a local software value.
- Power and clock-gating fields such as `*_PWR_FORCE`, `*_PWR_DIS`, `*_LOW_PWR_MODE`, `*_CLK_GATE_DISABLE`, and `*_ALLOW_DS_CLKSTOP` directly affect low-power behavior and can change power/performance stability.

## Dependencies and Integration Points

Key dependencies are the generated register offset header for the same ASIC and the display register-access macros that expect the exact naming convention used here. The chunk integrates with:

- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`, which includes `dcn_3_5_0_sh_mask.h` and fills DMUB register masks/shifts.
- DC hubbub headers such as `display/dc/hubbub/dcn35/dcn35_hubbub.h`, where the DCHUBBUB fields in this chunk are selected into hubbub mask/shift tables.
- HUBP headers derived from DCN32/DCN35 patterns, which use `HUBP0_*` names as template fields for per-instance HUBP programming.
- MPC headers and implementations, especially the DCN32-era MPC color-management surface, which reference `MPCC_MCM0_*` shaper, 3DLUT, 1DLUT, and memory-power fields.
- IRQ service code that includes the DCN35 mask header and uses display interrupt status/control masks to decode and clear hardware events.
- Firmware/DMUB paths where DMCUB scratch, interrupt, security, SMU-message, and clock fields must match firmware-visible register semantics.

## Risks

The primary risk is silent hardware misprogramming: these constants are usually trusted by generated accessors, so a one-bit shift or mask error can write the wrong field without compiler warnings. High-risk groups in this chunk are:

- MPCC/MCM LUT region and data fields, because color pipeline corruption can appear as subtle display color errors, failed HDR/gamma programming, or invalid RAM writes.
- DCHUBBUB and HUBPREQ pstate/watermark fields, because bad masks can cause underruns, stutter, hangs during memory-clock changes, or incorrect self-refresh gating.
- HUBP MALL and SubVP fields, because misuse can break static-screen optimization, cursor retrieval, MALL prefetch/retrieve sequencing, or sub-viewport memory fetch behavior.
- Power/clock-gating and DCPG interrupt fields, because incorrect mask/clear bits can leave domains powered unexpectedly, fail to clear interrupts, or disable needed clocks.
- Azalia/CORB/RIRB/immediate-command fields, because ring pointer, DMA-enable, and response-status bit errors affect HDMI/DP audio command transport.
- The chunk ends mid-family at `MPCC_MCM1_MPCC_MCM_SHAPER_RAMA_REGION_10_11__...__SHIFT`, so whole-file research must reconcile continuation chunks before drawing final conclusions about complete MPCC_MCM1 coverage.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- Build-time: compile configurations that include DCN 3.5.0 display support should catch missing or renamed macros when register-list macros expand.
- Static consistency: for each field, `MASK >> SHIFT` should form the expected field width; every `__SHIFT` in this chunk has a corresponding mask macro in the same range.
- Cross-version checks: compare against `dcn_3_5_1_sh_mask.h` and adjacent DCN versions for expected identical fields or deliberate differences. This chunk appears structurally aligned with DCN 3.5.1 for sampled fields such as `AZCONTROLLER1_CORB_CONTROL`, `DCHUBBUB_ARB_USR_RETRAINING_CNTL`, `HUBP0_DCHUBP_MALL_CONFIG`, and `MPCC_MCM0_MPCC_MCM_SHAPER_CONTROL`.
- Runtime display tests: modeset, multi-plane, cursor, SubVP/MALL, pstate-change, self-refresh, writeback, and suspend/resume paths exercise HUBP/DCHUBBUB/clock/power fields.
- Color tests: gamma, shaper, 3DLUT, post-1DLUT, HDR, and color-management validation exercise the MPCC/MCM field set.
- Audio tests: HDMI/DP audio enumeration and playback exercise Azalia CORB/RIRB, immediate command, stream interrupt, and DMA-position fields.
- Interrupt tests: hotplug, vblank, DCPG power up/down, DMCUB power/resync triggers, and interrupt clear/mask behavior indicate whether status/control fields are correctly packed.
