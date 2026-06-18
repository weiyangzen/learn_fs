# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001610`: lines 1-2495, `Docs/researches/chunks/subset-b-001610_research.md`
- `subset-b-001611`: lines 2496-4768, `Docs/researches/chunks/subset-b-001611_research.md`
- `subset-b-001612`: lines 4769-7154, `Docs/researches/chunks/subset-b-001612_research.md`
- `subset-b-001613`: lines 7155-9821, `Docs/researches/chunks/subset-b-001613_research.md`
- `subset-b-001614`: lines 9822-12326, `Docs/researches/chunks/subset-b-001614_research.md`
- `subset-b-001615`: lines 12327-14826, `Docs/researches/chunks/subset-b-001615_research.md`
- `subset-b-001616`: lines 14827-17349, `Docs/researches/chunks/subset-b-001616_research.md`
- `subset-b-001617`: lines 17350-19866, `Docs/researches/chunks/subset-b-001617_research.md`
- `subset-b-001618`: lines 19867-22386, `Docs/researches/chunks/subset-b-001618_research.md`
- `subset-b-001619`: lines 22387-24908, `Docs/researches/chunks/subset-b-001619_research.md`
- `subset-b-001620`: lines 24909-27383, `Docs/researches/chunks/subset-b-001620_research.md`
- `subset-b-001621`: lines 27384-29960, `Docs/researches/chunks/subset-b-001621_research.md`
- `subset-b-001622`: lines 29961-32471, `Docs/researches/chunks/subset-b-001622_research.md`
- `subset-b-001623`: lines 32472-34932, `Docs/researches/chunks/subset-b-001623_research.md`
- `subset-b-001624`: lines 34933-37347, `Docs/researches/chunks/subset-b-001624_research.md`
- `subset-b-001625`: lines 37348-39691, `Docs/researches/chunks/subset-b-001625_research.md`
- `subset-b-001626`: lines 39692-42127, `Docs/researches/chunks/subset-b-001626_research.md`
- `subset-b-001627`: lines 42128-44549, `Docs/researches/chunks/subset-b-001627_research.md`
- `subset-b-001628`: lines 44550-46976, `Docs/researches/chunks/subset-b-001628_research.md`
- `subset-b-001629`: lines 46977-49385, `Docs/researches/chunks/subset-b-001629_research.md`
- `subset-b-001630`: lines 49386-51950, `Docs/researches/chunks/subset-b-001630_research.md`
- `subset-b-001631`: lines 51951-54426, `Docs/researches/chunks/subset-b-001631_research.md`
- `subset-b-001632`: lines 54427-56984, `Docs/researches/chunks/subset-b-001632_research.md`
- `subset-b-001633`: lines 56985-59503, `Docs/researches/chunks/subset-b-001633_research.md`
- `subset-b-001634`: lines 59504-62232, `Docs/researches/chunks/subset-b-001634_research.md`
- `subset-b-001635`: lines 62233-64601, `Docs/researches/chunks/subset-b-001635_research.md`
- `subset-b-001636`: lines 64602-66921, `Docs/researches/chunks/subset-b-001636_research.md`
- `subset-b-001637`: lines 66922-68033, `Docs/researches/chunks/subset-b-001637_research.md`

## Chunk Research

### subset-b-001610: lines 1-2495

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 1-2495

## Scope

This chunk covers the first 2495 lines of the generated AMD DCN 2.0 register shift/mask header. It contains the license, include guard, and a large set of C preprocessor constants. There are no functions, structs, enums, inline helpers, or executable statements in this range.

The exported surface is a collection of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros. Callers combine these field descriptors with companion register-offset macros from the DCN 2.0 ASIC register headers and the AMD display register access helpers.

## Purpose

The chunk describes bit positions and masks for several display controller register blocks:

- `dce_dc_mmhubbub_vga_dispdec`: legacy VGA decode, memory aperture/pageing, rendering, cache, interrupt/status, indexed VGA registers, DAC palette registers, and VGA enable/source controls for display instances D1-D6.
- `dce_dc_dccg_dccg_dispdec`: DC clock generator controls for PHY PLL pixel-clock resync, DisplayPort DTOs, DSC and DPP clock DTOs, reference clocks, display-clock frequency ramping, global time counter, pixel-rate controls for OTG0-OTG5, symbol clocks, soft resets, audio DTOs, vertical-sync latch values, clock gating, and DCCG performance monitoring.
- `dce_dc_dccg_dccg_dfs_dispdec`: DFS bypass display-clock control.
- `dce_dc_dccg_dccg_dcperfmon0_dc_perfmon_dispdec` and `dce_dc_dccg_dccg_dcperfmon1_dc_perfmon_dispdec`: two DCCG-side DC performance monitor instances.
- `dce_dc_dccg_dccg_pll_dispdec`: reserved PLL macro control registers.
- `dce_dc_dmu_rbbmif_dispdec`: RBBM interface interrupt, timeout-disabling, and invalid-access status fields.
- `dce_dc_dmu_dc_pg_dispdec`: display power-gating domain config/status registers, power up/down interrupt status and control fields, and DC IP request control.
- `dce_dc_dmu_dmu_dcperfmon_dc_perfmon_dispdec`: a DMU-side `DC_PERFMON2` block.
- `dce_dc_dmu_dmu_misc_dispdec`: DMU pipe disable, clock gating/status, DMCU RAM power, SMU/static-screen interrupt, and deep-sleep force controls.
- `dce_dc_dmu_dmcu_dispdec`: the beginning of DMCU control, firmware address/checksum, ERAM/IRAM host access, event trigger, and internal interrupt status fields. The chunk ends inside `DMCU_UC_INTERNAL_INT_STATUS`.

## Important Macro Families

Every field is represented as a pair of constants:

- `REGISTER__FIELD__SHIFT` is the bit offset.
- `REGISTER__FIELD_MASK` is the already-positioned field mask.

The VGA section provides register fields used to disable or control legacy VGA paths during display bring-up and mode changes. It includes VGA memory read/write page addresses, render control, sequencer reset handling across D1-D6, linear/aperture/text/deep-sleep mode controls, base and surface addresses, HDP/cache controls, per-pipe VGA control registers, status/interrupt/clear fields, main/test/QOS controls, source selection, and byte-wide VGA indexed register fields such as CRTC, sequencer, graphics, attribute, DAC, and general status/misc registers.

The DCCG section is the largest part of this chunk. It defines PHY PLL pixel-clock resynchronizers, DP DTO enable bits and phase/modulo registers, DSC and DPP clock DTO phase/modulo controls, reference-clock selection and clock-gating delay fields, display-clock frequency ramp fields, memory global power request disable, DCCG clock-gate disable bits, DFS bypass controls, global time counter DTO/current values, pixel-rate controls for OTG0 through OTG5, and PHYPLL source selection for each OTG. It also includes symbol-clock enable/force-source fields for links A-F, DCCG soft-reset bits, audio DTO source/phase/module fields, per-OTG vsync latch registers, and DCCG CAC/status and display control fields.

The perfmon blocks `DC_PERFMON0`, `DC_PERFMON1`, and `DC_PERFMON2` share a repeated layout. Each block exposes counter event selection, counted-value source selection, increment mode, hardware control selection, run-enable mode, count-off and restart controls, interrupt enable/status/ack fields, per-counter state fields for counters 0-7, perfmon state/report count, run-enable start/stop selectors, combined high/low counter-value readback, and read-select fields.

The PLL macro control block is intentionally reserved: `PLL_MACRO_CNTL_RESERVED0` through later reserved entries are full-width `PLL_MACRO_CNTL_RESERVED` fields. These should be treated as generated hardware definitions, not as permission for generic driver code to write arbitrary values.

The RBBMIF block contains timeout and error-observation fields. It can report an interrupt status with masked client ID and timeout flags, disable timeouts per client across two registers, and expose interface state, read timeout, FIFO empty/full, invalid access flag/type/address.

The DC power-gating block defines paired `DOMAINn_PG_CONFIG` and `DOMAINn_PG_STATUS` fields for domains 0-11 and 16-21 in this slice. Config fields use `DOMAINn_POWER_FORCEON` and `DOMAINn_POWER_GATE`; status fields expose desired power state and PGFSM power status. Interrupt status/control registers pack power-up and power-down occurred, mask, and clear fields for domains 0-21. `DC_IP_REQUEST_CNTL` exposes IP-request override and IP_REQUEST state bits.

The DMU/DMCU tail defines fields for disabling DC pipes and enabling DMCUB, DMU clock gating and clock-on status, ERAM/IRAM memory power mode/force/disable/state, SMU interrupt status/event fields, static-screen interrupt signaling, deep-sleep force override, DMCU reset/enable/IRQ masking/read-timeout controls, uC status, firmware/PC start/end/checksum registers, ERAM/IRAM host access controls, data ports, software interrupt/event trigger, and the start of internal interrupt status bits.

## APIs, Types, and Functions

There are no callable APIs, C types, or functions in this chunk. The macros are an ABI-like hardware description consumed by hand-written AMDGPU display code.

The source is included directly by DCN 2.0 display firmware-facing code, for example `display/dmub/src/dmub_dcn20.c`. The register field names also match the conventions used by AMD display helpers such as `REG_UPDATE`, `REG_GET`, `REG_SET`, `REG_WAIT`, `set_reg_field_value`, `dm_read_reg_soc15`, and `dm_write_reg_soc15`. Those helpers depend on the generated shift/mask constants to update individual MMIO fields without hard-coding bit arithmetic at each call site.

## Control Flow

The header itself has no runtime control flow. The implied hardware programming flow is:

1. Select the target DCN 2.0 block and register via the companion offset/header data.
2. Use the matching `*_SHIFT` and `*_MASK` constants to extract or compose field values.
3. Access the register through AMD display MMIO or indexed-register helpers.
4. For control registers, preserve unrelated and reserved bits while changing only the intended fields.
5. For status and interrupt registers, obey the hardware clear/ack semantics rather than treating all fields as ordinary read/write storage.
6. For clock, DTO, pixel-rate, and power-gating fields, sequence writes with the surrounding display pipeline state so clocks and domains are stable before dependent blocks are used.

Sequencing-sensitive flows include disabling VGA paths per pipe during mode setup, programming DCCG DTO phase/modulo values before enabling generated clocks, waiting for display-clock ramp completion, checking OTG pixel-rate FIFO error/status bits, power-gating domains and polling PGFSM status, clearing power up/down interrupts, enabling DMCU host RAM access before ERAM/IRAM transactions, and using DMCU event trigger fields for host/uC signaling.

## State and Persistence

This file stores no software state and persists nothing itself. The constants describe hardware state held in display registers. That state persists until reset, power transitions, firmware action, modeset sequencing, suspend/resume, or an explicit driver register write.

Important state domains represented in the chunk are:

- Legacy VGA state: aperture/page selection, render behavior, indexed VGA register data, per-pipe VGA enables, source selection, status and interrupt latches, memory/cache controls, and VGA test/QOS settings.
- Clocking state: DCCG reference-clock selection, PHY PLL pixel-clock resync, symbol-clock enables, DP/DSC/DPP/audio DTO phase and modulo values, OTG pixel-rate sources, display-clock ramp state, DFS bypass, GTC current value, and DCCG clock gates/soft resets.
- Performance-monitor state: event selectors, run state, counter active/state bits, count-off behavior, interrupt latches/acks, and high/low counter readbacks for perfmon instances 0-2.
- RBBMIF state: timeout masks, client timeout interrupt status, FIFO state, invalid access type/address, and read-timeout indication.
- Power-management state: domain force-on/gate controls, desired power state, PGFSM power status, domain power up/down interrupt masks and clears, IP request override/status, DMU/DMCU memory power modes, and deep-sleep force override.
- DMCU state: microcontroller reset/enable and interrupt masking, firmware location/checksum registers, ERAM/IRAM access enable/address/data state, host-to-uC event triggers, and internal interrupt flags.

Because many fields are latches, status bits, or power/clock controls, software must not assume read/modify/write is harmless. Preserving reserved bits and writing only documented clear/ack bits is required to avoid losing interrupt information or changing hardware state unexpectedly.

## Dependencies and Integration Points

The header depends only on the C preprocessor, but it is meaningful only with the rest of the DCN 2.0 generated ASIC register set: offset headers, register alias headers, and AMD display register helper macros.

Primary integration points include:

- DCN 2.0 DMUB/DMCU and display bring-up code, which includes this mask header and uses DMCU, DMU, DCCG, and power/control fields during firmware and display initialization.
- Timing-generator and modeset paths that disable legacy VGA per pipe before programming modern display timings. The same field names are used in older DCE timing generator code to clear `D1VGA_CONTROL`-style fields through register helpers.
- DCCG clock manager logic that programs display, DPP, DSC, DP, audio, symbol, reference, and pixel-rate clocks using DTO phase/modulo and enable/source fields.
- Power-gating code that maps domain config/status fields into higher-level display block power transitions and polls PGFSM state after changing `DOMAIN_POWER_GATE`.
- Performance and diagnostics paths that select DC perfmon events, run counters, handle counter interrupts, and read split high/low counter values.
- RBBMIF error-handling or debug paths that inspect timeout/invalid access status and per-client timeout-disable fields.
- SMU/DMU/DMCU integration paths that coordinate static-screen, deep-sleep, pipe-disable, DMCUB enable, microcontroller memory loading, and host/uC interrupt signaling.

## Risks

The main risk is silent hardware misprogramming. A wrong mask or shift compiles cleanly but can target an adjacent bit, corrupt a packed field, fail to clear an interrupt, gate a required clock, or power down a needed display block.

Clocking fields are high impact. Incorrect DTO phase/modulo, source selection, half-rate, deep-color, ramp, or gate-disable values can produce blank displays, unstable modes, audio clock drift, FIFO errors, link training failures, or resume-only failures.

Power-management fields are also high risk. `DOMAINn_POWER_GATE`, `DOMAINn_POWER_FORCEON`, PGFSM status, DMU memory power, and IP-request override bits can make blocks unavailable if programmed in the wrong order or interpreted with the wrong polarity.

Status and interrupt fields require hardware-specific semantics. Power-gating interrupt clear bits, perfmon interrupt acks, VGA interrupt clear bits, SMU interrupt status/event fields, and DMCU interrupt/event bits should not be manipulated by generic read/modify/write code without checking whether the field is write-one-to-clear, latched, or status-only.

The chunk boundary matters. It begins at the file start but ends inside `DMCU_UC_INTERNAL_INT_STATUS`, so the merge lane must combine this with the following chunk before treating DMCU interrupt coverage as complete.

Reserved PLL macro fields should not be normalized into ordinary driver controls. They are generated names for reserved register space and likely exist to preserve the hardware register map.

The macros have global preprocessor names. Any manual additions or renames can create collisions or break existing `REG_FIELD`, `SF`, and generated-table patterns that assume exact ASIC database naming.

## Test Signals

Useful validation signals are mostly build, generated-data, and hardware integration tests:

- Build coverage for DCN 2.0 AMD display code that includes `dcn_2_0_0_sh_mask.h`, especially DMUB/DMCU, DCCG, power, timing-generator, and perfmon users.
- Generated-header consistency checks that every `REGISTER__FIELD__SHIFT` has a matching positioned mask, repeated instances preserve equivalent layouts, masks fit inside 32-bit registers, and macro names remain unique.
- Regeneration or diff checks against the authoritative DCN 2.0 ASIC register database.
- Modeset and suspend/resume tests that verify VGA paths are disabled as expected and do not re-enable across boot, modeset, hotplug, or resume.
- Clocking tests over multiple display configurations, including OTG0-OTG5 pixel-rate source selection, DP DTO enable/phase/modulo, DPP/DSC clock DTOs, display-clock ramp completion, symbol clocks, audio DTOs, and DCCG soft reset/gating behavior.
- Power-gating tests that toggle domains 0-11 and 16-21 where supported, poll PGFSM power status, validate power up/down interrupt status/control fields, and check that DC IP request override does not strand hardware in an unexpected state.
- DMCU/DMU firmware-load tests that exercise reset/enable sequencing, ERAM/IRAM host access and auto-increment, firmware address/checksum programming, memory power state, and host/uC event triggers.
- Perfmon tests for instances 0-2 that select events, start/stop counters, observe active/state fields, read low/high values, and verify interrupt ack behavior.
- RBBMIF diagnostic tests that induce or simulate timeout/invalid access paths where possible and confirm client ID, timeout, FIFO, invalid-access type, and address fields decode correctly.

## Cross-Chunk Notes

This is the opening slice of a much larger generated header. The final per-file research document should merge this with later chunks to cover the remainder of `DMCU_UC_INTERNAL_INT_STATUS` and the many subsequent DCN 2.0 display blocks that are outside lines 1-2495.

### subset-b-001611: lines 2496-4768

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 2496-4768

## Purpose

This chunk is part of AMDGPU's generated DCN 2.0 register field mask header. It contains no executable C code; it publishes preprocessor constants for bit positions and already-positioned masks used by DCN 2.0 display-controller register helpers.

The range begins in the `dce_dc_dmcu_dispdec` address block, at the tail of `DMCU_UC_INTERNAL_INT_STATUS`, and continues through DMCU interrupt, mailbox, performance-monitor, DisplayPort receiver, and DMCU interrupt-routing registers. It then switches to the `dce_dc_dmu_ihc_dispdec` address block and defines DMU/IHC GPU timer and display interrupt status registers through the beginning of `DISP_INTERRUPT_STATUS_CONTINUE22`.

The primary hardware domains described here are:

- DMCU internal interrupt status and static-screen interrupt status.
- DMCU interrupt occurrence/clear registers for ABM, MCP/SCP, UC internal events, DCPG power up/down, vblank, OTG range timing, and vupdate-no-lock events.
- DMCU host/UC interrupt masks and UC XIRQ/IRQ selection bits.
- DMCU scratch, interrupt counters, firmware checksum sampling, and UC clock gating controls.
- Master/slave communication mailbox registers used for DMCU, ABM, PSR, and command handshakes.
- DMCU performance monitor and DisplayPort receiver interrupt status/routing registers.
- DMU IHC GPU timer start/read controls and the top-level display interrupt status chain, including HUBP flip/detile/underflow, HPD/HPDRX, DMCU, OTG, DCIO, AUX/I2C, DP training/stream disable, audio endpoint, DCPG, ABM, and vupdate-no-lock interrupt status bits.

Each field appears as a `REGISTER__FIELD__SHIFT` macro and a matching `REGISTER__FIELD_MASK` macro. Driver code combines these values with register-address constants from `dcn_2_0_0_offset.h` and wrapper macros such as `REG_GET`, `REG_UPDATE`, `REG_WRITE`, `FD_MASK`, `FD_SHIFT`, and generation-specific register lists.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or object definitions in this chunk. The API surface is the generated macro namespace.

The DMCU interrupt status registers include:

- `DMCU_UC_INTERNAL_INT_STATUS` for UC IRQ, XIRQ, software interrupt, illegal opcode trap, timer compare/overflow/capture, real-time interrupt, and pulse accumulator status bits.
- `DMCU_SS_INTERRUPT_CNTL_STATUS` for static-screen interrupt status, occurred, and clear bits for static screen channels 1 through 6.
- `DMCU_INTERRUPT_STATUS`, `DMCU_INTERRUPT_STATUS_1`, `DMCU_INTERRUPT_STATUS_CONTINUE`, and `DMCU_INTERRUPT_STATUS_2` for DMCU-visible interrupt occurrence and clear bits covering ABM ready/update, MCP/SCP, external software, UC internal, UC register read timeout, DCPG IHC domain power up/down, vblank, OTG range timing, DIO/DCCG, DWB, DP link, FEC, HPD/HPDRX, DCIO, SDMA, DMCU I2C, and OTG vupdate-no-lock events.

The DMCU routing registers include `DMCU_INTERRUPT_TO_HOST_EN_MASK`, `DMCU_INTERRUPT_TO_UC_EN_MASK`, `DMCU_INTERRUPT_TO_UC_EN_MASK_1`, `DMCU_INTERRUPT_TO_UC_EN_MASK_CONTINUE`, and `DMCU_INTERRUPT_TO_UC_EN_MASK_2`. These expose interrupt delivery enables for host-facing and microcontroller-facing paths. The matching `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL`, `_1`, `_CONTINUE`, and `_CONT2` registers select whether routed events use the UC XIRQ or IRQ path for the same event families.

The DMCU command and mailbox families include:

- `DC_DMCU_SCRATCH`, `DMCU_INT_CNT`, `DMCU_INT_CNT_CONTINUE`, `DMCU_FW_CHECKSUM_SMPL_BYTE_POS`, and `DMCU_UC_CLK_GATING_CNTL` for scratch/debug, interrupt counters, firmware checksum sampling byte positions, and UC clock-gating controls.
- `MASTER_COMM_DATA_REG1..3`, `MASTER_COMM_CMD_REG`, and `MASTER_COMM_CNTL_REG` for host-to-DMCU payload bytes, command bytes, and the master communication interrupt bit.
- `SLAVE_COMM_DATA_REG1..3`, `SLAVE_COMM_CMD_REG`, and `SLAVE_COMM_CNTL_REG` for DMCU-to-host payload, command, and slave communication interrupt state.

The performance-monitor and DPRX register groups include:

- `DMCU_PERFMON_INTERRUPT_STATUS1..5` for display pipe performance-monitor interrupt status across HUBP, DPP, MPC, OPP, OTG, DIO, and secondary interrupt groups.
- `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK1..5` and `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1..5` for enabling and selecting the UC interrupt line for those performance-monitor sources.
- `DMCU_DPRX_INTERRUPT_STATUS1` for DisplayPort receiver sideband, training, service IRQ, AUX reply/timeout/error, sink request, and DPCD/automated test style events across HPD RX instances.
- `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1` and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1` for routing the DPRX event set to the UC.

The DMU/IHC timer macros include `DC_GPU_TIMER_START_POSITION_V_UPDATE`, `DC_GPU_TIMER_START_POSITION_VSTARTUP`, `DC_GPU_TIMER_READ`, and `DC_GPU_TIMER_READ_CNTL`. These describe per-display start-position fields for GPU timer capture around vupdate and vstartup, a 32-bit readback register, and read-control fields for reference-clock selection, read mode, and selected display signal.

The `DISP_INTERRUPT_STATUS*` chain is the top-level display interrupt status map. In this chunk it covers `DISP_INTERRUPT_STATUS` through the beginning of `DISP_INTERRUPT_STATUS_CONTINUE22`. The chain includes:

- HUBP flip, detile, and underflow events for multiple pipes.
- DC HPD and HPD RX events, DMCU SCP, DMCU software, and DMIF/DCPG-style power events.
- DIO, DCCG, DWB, GPIO pad, DCIO, SDMA, and DMCU I2C events.
- OTG static-screen, vupdate, GSL vsync gap, vstartup, and vready status for six timing generators, plus vupdate-no-lock entries for OTG0 through OTG5 at the end of the chunk.
- AUX/DIO, DC I2C DDC/VGA/generic read request, and DOUT I2C hardware-done events.
- DisplayPort fast training complete and video-stream disable events for DIG instances.
- Audio endpoint format-changed, enabled, and disabled events for endpoints 0 through 7.
- DCPG IHC domain 8 through 15 power up/down events and ABM0 high-gain, low-sense, and backlight-update events.

The `DISP_INTERRUPT_STATUS_CONTINUE*__DISP_INTERRUPT_STATUS_CONTINUE*` fields at bit 31 are continuation indicators linking the status-register chain.

## Control Flow

This chunk has no runtime control flow. It is compile-time hardware metadata.

A typical runtime path is:

1. DCN 2.0 component code includes `dcn_2_0_0_offset.h` for register addresses and this file for field masks and shifts.
2. Per-generation tables or helper structures materialize the generated constants through macros such as `SR`, `SRI`, `FD_MASK`, `FD_SHIFT`, `DMCU_SF`, `ABM_SF`, `REG_OFFSET`, and `REG_FIELD` style lists.
3. Register helper calls read, write, extract, or update the target register field by pairing the address with the `*_MASK` and `*__SHIFT` constants.
4. Hardware then performs the interrupt routing, event status latching/clearing, mailbox handshake, timer read/capture, or diagnostic counter behavior.

The direct DCN 2.0 include points in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

The most obvious control-sensitive consumer in this range is the display IRQ service. `irq_service_dcn20.c` maps IV source IDs from `ivsrcid/dcn/irqsrcs_dcn_1_0.h` to DAL IRQ sources such as vblank, vline, page flip, HPD, HPDRX, and vupdate. It also builds per-source enable and ack metadata with generated address/mask constants. Some display interrupt status bits from this chunk are also mirrored in `irqsrcs_dcn_1_0.h` comments, for example I2C hardware-done, audio endpoint state changes, OTG static-screen/vupdate/vstartup/vready events, and continuation status registers.

The DMCU mailbox fields are consumed through the older DCE DMCU/ABM abstractions. `dce_dmcu.h`, `dce_dmcu.c`, `dce_abm.h`, and `dce_abm.c` define register lists and field lists for `MASTER_COMM_*`, `SLAVE_COMM_*`, and `DMCU_INTERRUPT_TO_UC_EN_MASK`, then use waits and read/modify/write helpers to send PSR, ABM, backlight, PHY sync, EDID, and related commands to the microcontroller. For DCN 2.0-specific files, DMUB supersedes many firmware interactions, but this generated DMCU namespace remains part of the shared register contract.

## State And Persistence Behavior

The header stores no software state. It describes hardware state in display controller registers.

The represented state classes include:

- Sticky interrupt occurrence and clear bits in DMCU and display IHC status registers. Many `*_OCCURRED` and `*_CLEAR` fields deliberately share the same bit position and mask, implying write-one-to-clear behavior for the clear alias while reads report the occurred alias.
- Enable masks that persist in hardware until changed by the driver, reset, suspend/resume restore, power gating, or ASIC reset.
- UC interrupt line selection bits that determine whether an enabled event is signaled through XIRQ or IRQ.
- Communication mailbox state, including command bytes, payload bytes, and master/slave interrupt handshakes. These fields must be sequenced with polling/wait helpers so host and microcontroller do not overwrite each other's in-flight messages.
- Counter/readback state such as DMCU interrupt counters, firmware checksum sample byte positions, GPU timer readback, and performance/DPRX interrupt status.
- Live top-level display interrupt status chain state. These bits reflect hardware events from many display subblocks and may be level, pulse, sticky, or continuation status depending on the event.

Persistence is hardware-defined and not encoded by the generated macros. Some fields are read-only status, some are write-one-to-clear, some are read/write enables, and some are self-clearing triggers or latches. Driver code must preserve unrelated bits during read/modify/write operations and must know the access type from hardware documentation and the surrounding DC/DCE sequencing code.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.0 register header set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h` supplies the matching register addresses and base-index constants.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h` supplies the field masks and shifts described here.
- SOC base headers such as `navi10_ip_offset.h`, `vega10_ip_offset.h`, and `soc15_hw_ip.h` provide block base information used by generated address macros.
- Display helper headers under `drivers/gpu/drm/amd/display/` convert these macros into per-generation register, shift, and mask structures.

Integration points by functional area:

- Display IRQ handling: `display/dc/irq/dcn20/irq_service_dcn20.c` uses the DCN 2.0 generated headers with `SRI` and `IRQ_REG_ENTRY` macros to construct IRQ source metadata. The `DISP_INTERRUPT_STATUS_CONTINUE*` fields in this chunk correspond to source IDs documented in `include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, even when the DCN 2.0 IRQ table acknowledges more specific subblock registers for common sources.
- DMCU and ABM command paths: `display/dc/dce/dce_dmcu.*`, `display/dc/dce/dce_abm.*`, and `display/dc/dce/dce_link_encoder.h` define reusable register/field lists for the `MASTER_COMM_*`, `SLAVE_COMM_*`, and `DMCU_INTERRUPT_TO_UC_EN_MASK` names present in this chunk.
- DMUB path: `display/dmub/src/dmub_dcn20.c` includes the same generated headers and uses the field-mask infrastructure for DMCUB registers. This particular chunk's legacy DMCU mailbox fields are distinct from the DMCUB register set, but the include contributes to the shared generated namespace used by DMUB DCN 2.0 support.
- Power and clock/display-resource setup: DCN 2.0 resource, clock manager, and GPIO factory files include the header for the same generation-specific register map. Their direct field usage is mostly outside this chunk, but compile-time namespace consistency matters across the whole generated file.
- GMC path: `amdgpu/gmc_v10_0.c` includes the DCN 2.0 header alongside MMHUB and ATHUB headers. The chunk itself is display-focused and does not implement memory-management behavior.

Although this repository path is under a local `ceph-client` source tree, the file is AMDGPU display hardware metadata. It has no Ceph, filesystem, or distributed-storage logic.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. Incorrect generated masks or shifts can compile successfully while enabling the wrong interrupt, clearing the wrong sticky bit, corrupting unrelated enable bits, or routing an event to the wrong microcontroller interrupt line.

High-risk fields in this chunk include:

- `*_OCCURRED` and `*_CLEAR` aliases that share a bit. Misusing the clear alias can drop pending interrupts; failing to clear sticky events can cause interrupt storms or repeated work.
- DMCU interrupt enable and XIRQ/IRQ selection registers. A one-bit error can strand PSR, ABM, DP RX, HPD RX, vblank, DCPG, or firmware events on the wrong target.
- `MASTER_COMM_*` and `SLAVE_COMM_*` mailbox fields. Wrong byte shifts or interrupt bits can hang DMCU/ABM/PSR command handshakes, corrupt firmware commands, or make wait loops time out.
- Top-level `DISP_INTERRUPT_STATUS_CONTINUE*` fields. The register chain is dense, repeated, and instance-indexed; copy-generation mistakes can isolate failures to one pipe, one HPD/DDC instance, one audio endpoint, or one DIG instance.
- Power-domain and vupdate/vstartup/vready status bits. Misreported power events or timing events can affect suspend/resume, runtime power management, modesets, vblank accounting, page flips, and atomic update pacing.
- DPRX/AUX/I2C events. Incorrect status or routing can break link training, DPCD access, EDID reads, HPD RX service IRQ handling, or automated test responses.

This chunk starts after the `DMCU_UC_INTERNAL_INT_STATUS` register declaration has already begun in the previous lines and ends in the middle of `DISP_INTERRUPT_STATUS_CONTINUE22`, before its full mask list and the following `DC_GPU_TIMER_START_POSITION_VREADY` block. The final merged per-file document should treat those as chunk boundaries, not missing definitions.

The generated macros do not encode access type, reset value, valid enum values, locking requirements, or ordering constraints. Consumers must know whether a field is read-only, write-one-to-clear, level-sensitive, pulse-sensitive, self-clearing, or double-buffered from hardware documentation and the surrounding driver code.

## Test Signals

Useful validation signals include both generated-header checks and hardware/display behavior:

- AMDGPU/DCN 2.0 builds should compile all direct include users of `dcn_2_0_0_sh_mask.h`, especially `irq_service_dcn20.c`, `dmub_dcn20.c`, `dcn20_resource.c`, `dcn20_clk_mgr.c`, `hw_factory_dcn20.c`, and `gmc_v10_0.c`.
- Register-generation validation should compare every `*_MASK` and `*__SHIFT` pair in this range against AMD's source register database and the matching addresses in `dcn_2_0_0_offset.h`.
- Static checks can verify that every `*_CLEAR` alias that shares a mask with `*_OCCURRED` is intentional and that continuation bits remain at bit 31 where present.
- IRQ tests should exercise HPD, HPD RX, I2C/DDC hardware-done, AUX/DPCD, DP training complete, DP stream disable, vblank/vstartup/vupdate/vready, vupdate-no-lock, static-screen, page-flip, underflow, DCPG power, ABM, and audio endpoint interrupts.
- DMCU/ABM/PSR command tests should validate mailbox waits, command byte packing, payload register writes, master/slave interrupt handshakes, and timeout behavior.
- Suspend/resume and runtime power-management stress should verify that DCPG domain power events and interrupt enable/clear state are restored without stale status bits or lost notifications.
- Multi-display stress should cover all six OTG/HUBP/HPD/DDC style instances and all relevant audio endpoints, because the register chains are heavily repeated and instance-specific.
- Link training and hotplug tests should watch for DPRX/AUX/HPDRX status correctness, service IRQ handling, and EDID/I2C completion.
- Regression symptoms from bad constants include missed or repeated interrupts, stuck DMCU mailbox waits, broken backlight or PSR commands, link training failures, hotplug failures, bad audio endpoint notifications, vblank/page-flip timing failures, underflow handling failures, and failures isolated to one display pipe or connector.

## Cross-Chunk Notes

The previous chunk contains the DMCU RAM access and event-trigger definitions and the beginning of `DMCU_UC_INTERNAL_INT_STATUS`. This chunk continues through the DMCU interrupt and mailbox region, then enters the DMU IHC display interrupt status region. The next chunk continues `DISP_INTERRUPT_STATUS_CONTINUE22` and the later GPU timer/display interrupt mask definitions. The final per-file merge should describe the whole header as a generated DCN 2.0 hardware register layout contract rather than algorithmic code.

### subset-b-001612: lines 4769-7154

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 4769-7154

## Purpose

This chunk is part of AMDGPU's generated DCN 2.0 register field mask header. It contains no executable C logic; it publishes compile-time `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants for display hardware registers. Driver code combines these field constants with the matching register-address definitions from `dcn_2_0_0_offset.h` and the DC register helper macros.

The assigned range covers three related regions of the DCN 2.0 display register map:

- The tail of display interrupt status and GPU timer-position registers, including `DISP_INTERRUPT_STATUS_CONTINUE22`, timer start positions for vready, flip, no-lock v-update, and flip-away events, plus `DISP_INTERRUPT_STATUS_CONTINUE23` and `DISP_INTERRUPT_STATUS_CONTINUE24`.
- Interrupt destination registers for many display sub-blocks: DCCG, DMU/DMCUB/DMCU, DCPG, MMHUBBUB, WB/WBSCL, DCHUB/HUBP, DPP, MPC, OPP, OPTC/OTG, DIG, I2C/DDC/HPD, DIO, DCIO, HPD, AZ audio, AUX, and DSC.
- The beginning of writeback and memory-hubbub field definitions: WB0 converter, WB scaler, WB perfmon, MCIF writeback instances 0 and 1, WBIF0, VGA split, MMHUBBUB memory power, and the first fields of `MMHUBBUB_CLOCK_CNTL`.

Although this repository path is under a local `ceph-client` source tree, this header chunk is AMD display-driver hardware metadata. It has no Ceph filesystem protocol behavior, distributed filesystem state, or storage persistence.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or variables in this chunk. The macro namespace is the API surface.

Each field appears as a pair:

- `REGISTER__FIELD__SHIFT` gives the low bit position.
- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.

The interrupt status groups expose live/sticky event bits. `DISP_INTERRUPT_STATUS_CONTINUE22` covers DCPG domain 8-15 power up/down events, ABM0 ready/backlight update events, OTG0-OTG5 v-update-no-lock events, and the continuation bit into `DISP_INTERRUPT_STATUS_CONTINUE23`. `DISP_INTERRUPT_STATUS_CONTINUE23` covers DCPG domain 16-21 power events, DSC0-DSC5 input-underflow and core-error events, and continuation into `DISP_INTERRUPT_STATUS_CONTINUE24`. `DISP_INTERRUPT_STATUS_CONTINUE24` covers DSC perfmon counter interrupts and DMCUB timer, inbox, outbox, general-data, and undefined-address-fault events.

The `DC_GPU_TIMER_START_POSITION_*` registers pack per-pipe timer trigger positions. `VREADY` and `V_UPDATE_NO_LOCK` expose D1-D6 fields; `FLIP` and `FLIP_AWAY` expose D1-D8 fields. These fields are small packed selectors used by display interrupt/timer logic around scanout and page-flip timing.

The interrupt destination groups define routing selectors for display interrupt sources. They include:

- `DCCG_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST`, `DCPG_INTERRUPT_DEST`, and `DCPG_INTERRUPT_DEST2` for clock-generator, display microcontroller, and display clock/power-gating interrupts.
- `MMHUBBUB_INTERRUPT_DEST`, `WB_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST`, `DCHUB_PERFCOUNTER_INTERRUPT_DEST`, and `DCHUB_INTERRUPT_DEST2` for memory-hubbub, writeback, HUBP vblank/vline/VM-context, perfmon, flip, flip-away, and VM-fault routing.
- `DPP_PERFCOUNTER_INTERRUPT_DEST`, `MPC_INTERRUPT_DEST`, `OPP_INTERRUPT_DEST`, `OPTC_INTERRUPT_DEST`, and `OTG0_INTERRUPT_DEST` through `OTG5_INTERRUPT_DEST` for pixel pipe, composition, output, timing-generator, and underflow/range/vupdate/snapshot events.
- `DIG_INTERRUPT_DEST`, `I2C_DDC_HPD_INTERRUPT_DEST`, `DIO_INTERRUPT_DEST`, `DCIO_INTERRUPT_DEST`, `HPD_INTERRUPT_DEST`, `AZ_INTERRUPT_DEST`, `AUX_INTERRUPT_DEST`, and `DSC_INTERRUPT_DEST` for display I/O, hotplug, AUX, audio, and DSC interrupt routing.

The WB0 converter block under `dce_dc_wb0_dispdec_cnv_dispdec` includes `WB_ENABLE`, `WB_EC_CONFIG`, `CNV_MODE`, source/window size and start registers, update control, test CRC registers, debug controls, soft reset, and warm-up controls. These fields describe writeback capture enablement, format/conversion setup, source and output geometry, update latching, diagnostics, and reset behavior.

The WBSCL block under `dce_dc_wb0_dispdec_wbscl_dispdec` includes coefficient RAM select/data, scaler mode, tap control, destination size, horizontal and vertical filter scale ratios and initial phases, round offsets, overflow/conflict status, test CRCs, backpressure counters, clamp ranges, outside-pixel strategy, and debug access. These constants support the writeback scaler pipeline.

The WB perfmon block `DC_PERFMON3_*` exposes counter control, counter state, perfmon control, and current/high/low counter values for writeback performance monitoring.

The MCIF writeback blocks `MCIF_WB0_*` and `MCIF_WB1_*` expose memory-interface writeback control. Important families include software buffer-manager control and status, current line, pitch, four luma/chroma buffer status and address registers, address offsets, high address bits, resolution fields, VCE buffer-manager lock/interrupt/slice controls, SCLK/NB-pstate watermark controls, client watermark, clock gating override, warm-up pitch, self-refresh behavior, multi-level QoS, luma/chroma sizes, and test-debug access. `MCIF_WB0_MCIF_WB_SECURITY_LEVEL` is present for instance 0 in this range.

The final MMHUBBUB block begins with `WBIF0_MISC_CTRL`, `WBIF0_SMU_WM_CONTROL`, `WBIF0_PHASE0_OUTSTANDING_COUNTER`, `WBIF0_PHASE1_OUTSTANDING_COUNTER`, `VGA_SRC_SPLIT_CNTL`, `MMHUBBUB_MEM_PWR_STATUS`, `MMHUBBUB_MEM_PWR_CNTL`, and the first `MMHUBBUB_CLOCK_CNTL` shift fields through `DISPCLK_G_WBIF0_GATE_DIS`. These fields cover writeback interface timeout/deep-sleep controls, SMU watermark-change handshaking, outstanding request counters, legacy VGA split selection, memory power status/control for VGA and MCIF DWB0 memories, and MMHUBBUB/VGA/WBIF clock-gate controls.

## Control Flow

This header range has no runtime control flow. It is preprocessor data consumed by DCN 2.0 display code.

A typical consumer flow is:

1. Include `dcn_2_0_0_offset.h` for register addresses and `dcn_2_0_0_sh_mask.h` for field layouts.
2. Bind fields into a block-specific register descriptor with macros such as `SF(reg, field, mask_sh)` or `FD(reg__field)`.
3. Use display register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, or SOC15-specific wrappers to read, modify, and write packed fields.
4. Let hardware interpret the programmed value as interrupt routing, interrupt status, writeback/scaler configuration, memory-interface buffer state, power-management policy, or debug/perfmon setup.

The control-sensitive behaviors represented here include interrupt routing to the correct interrupt handler, acknowledging or inspecting display status events, selecting GPU timer positions for scanout events, enabling/disabling writeback, latching writeback converter/scaler updates, programming buffer addresses and sizes, responding to writeback backpressure or overrun, coordinating p-state and self-refresh watermarks, and disabling/enabling MMHUBBUB/VGA/WBIF clock gates.

## State And Persistence Behavior

The file stores no software state and has no persistence mechanism. It describes state held in DCN 2.0 display hardware registers.

The represented hardware state includes:

- Interrupt state: live or sticky status bits for DCPG, DSC, DMCUB, ABM, OTG, HUBP, WBSCL, WB, AUX, HPD, DIG, AZ, and other display sub-block events.
- Interrupt routing state: destination bits that determine which interrupt path receives events from each display block.
- Timer-position state: compact per-pipe trigger positions for vready, flip, v-update-no-lock, and flip-away handling.
- Writeback pipeline state: enable, conversion mode, input/output geometry, update latches, scaler coefficients, scaling ratios, clamp ranges, CRC/debug controls, soft reset, and warm-up setup.
- MCIF writeback state: buffer-manager enable/locks/interrupts, buffer pitch/address/offset/high bits, four-buffer status, resolution, QoS/watermarks, p-state handling, self-refresh behavior, security level, and memory client clock gating.
- MMHUBBUB state: writeback interface handshake/status, VGA split, memory power status/control, and clock-gate control.

Persistence is hardware-defined. Some fields are programmed configuration that remains until reset or reprogramming; some are status/readback fields; some are interrupt status bits that may be sticky or write-one-to-clear; and some are handshake or acknowledge bits that can be self-clearing. Values can be changed by the display driver, DMCUB/firmware, BIOS initialization, hotplug/modeset paths, power-gating, suspend/resume, or ASIC reset. This generated header does not encode access type, reset value, volatile behavior, or sequencing constraints.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.0 register header set. The companion address definitions live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h`; this file supplies only the field layout inside those addresses.

Direct include points for `dcn_2_0_0_sh_mask.h` found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

The writeback and MMHUBBUB fields are integrated through DCN 2.0 display-resource descriptors. For example, `display/dc/mmhubbub/dcn20/dcn20_mmhubbub.h` maps `MCIF_WB0_MCIF_WB_BUFMGR_SW_CONTROL` fields such as `MCIF_WB_BUFMGR_ENABLE`, software interrupt enable/ack bits, lock bits, VMID, and address-fence enable into the `dcn20_mmhubbub` register/mask structures. Older or shared writeback declarations such as `display/dc/dcn10/dcn10_dwb.h` use the same MCIF WB field names where the hardware layout is compatible.

The interrupt fields integrate with `display/dc/irq/dcn20/irq_service_dcn20.c`, which builds IRQ source tables for DCN 2.0 display events. The destination/status masks in this chunk are part of the low-level contract that lets IRQ service code route, enable, clear, or inspect display interrupt sources.

The DMCUB-related interrupt fields integrate with DMUB firmware communication in `display/dmub/src/dmub_dcn20.c`. The `DISP_INTERRUPT_STATUS_CONTINUE24` and `DMU_INTERRUPT_DEST` fields describe the hardware event surface for DMCUB timers, inbox/outbox readiness/completion, general data, and undefined-address faults.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A wrong shift or mask can compile successfully while changing the wrong bit, failing to update the intended field, corrupting an adjacent field during read-modify-write, or routing an interrupt to the wrong destination.

Interrupt fields are sensitive because routing/status mistakes can cause missed vblank, vline, HPD, AUX, underflow, DSC, DMCUB mailbox, VM-fault, or writeback events. Symptoms can include lost hotplug notifications, stuck DMUB communication, unacknowledged interrupts, interrupt storms, missed page-flip completion, incorrect underflow reporting, or broken display diagnostics.

Writeback and scaler fields are sensitive to geometry and buffer programming. Incorrect masks for `CNV_WINDOW_*`, `CNV_SOURCE_SIZE`, WBSCL scale ratios/phases, clamp/outside-pixel strategy, MCIF buffer addresses, pitch, offsets, high address bits, luma/chroma sizes, or resolution fields can produce corrupt captures, out-of-bounds memory writes, wrong color/chroma layout, bad CRC diagnostics, or hangs in the writeback path.

MCIF and MMHUBBUB power/performance fields affect memory traffic and display power management. Bad watermarks, p-state controls, self-refresh bits, QoS settings, clock-gate overrides, memory power controls, or SMU watermark handshakes can lead to writeback underrun/overrun, backpressure, missed watermark updates, higher power use, or display instability around suspend/resume and clock changes.

The repeated instance layout is a maintenance risk. `MCIF_WB0_*` and `MCIF_WB1_*` are nearly mirrored, but not identical in this range because `MCIF_WB0_MCIF_WB_SECURITY_LEVEL` appears while the analogous WB1 security-level register is not present before the next instance's luma/chroma size fields. Copying constants across instances without checking the generated source can introduce subtle instance-specific bugs.

The chunk boundaries are artificial. It starts inside the `DISP_INTERRUPT_STATUS_CONTINUE22` macro group, after earlier shift fields for that register, and ends before the remaining `MMHUBBUB_CLOCK_CNTL` shift and mask fields. The final per-file merge should treat these as chunk boundaries, not as source omissions.

## Test Signals

Useful validation is mostly compile-time plus display hardware behavior:

- AMDGPU builds for DCN 2.0 paths should compile all generated field names referenced by IRQ, DMUB, MMHUBBUB, writeback, and GMC/DC integration code.
- Generated-register validation should compare every `*_MASK` and `*__SHIFT` pair in this range against AMD's DCN 2.0 register database and the matching addresses in `dcn_2_0_0_offset.h`.
- IRQ tests should exercise vblank/vline, page-flip, flip-away, HPD, AUX, DMCUB inbox/outbox, DSC, underflow, writeback, and VM-fault events and verify that status bits, destination routing, and clear/ack behavior match expectations.
- DMUB mailbox tests should confirm timer and inbox/outbox ready/done interrupts are delivered and cleared correctly.
- Writeback tests should enable WB0 capture across representative pixel formats, source/window sizes, scaling ratios, luma/chroma layouts, and four-buffer rotations, then compare captured frames or CRCs.
- Stress tests should combine writeback with modesets, page flips, hotplug, MST, suspend/resume, runtime power management, and clock/p-state changes to expose bad MCIF watermarks, self-refresh controls, or MMHUBBUB clock/memory power fields.
- Perfmon and debug tests should verify WB/DC perfmon counters, scaler conflict/overflow status, test CRC registers, and MCIF debug-index/data access.

Regression symptoms from bad constants include blank or flickering display, missed page-flip completion, interrupt storms, stuck DMUB mailbox traffic, lost HPD/AUX notifications, false underflow or DSC errors, corrupt writeback frames, GPU memory faults from bad capture addresses, writeback hangs, failed suspend/resume, and unexpected clock or power-management behavior.

## Cross-Chunk Notes

Earlier chunks of `dcn_2_0_0_sh_mask.h` define the start of `DISP_INTERRUPT_STATUS_CONTINUE22` and the earlier DCN 2.0 display register field families. Later chunks complete `MMHUBBUB_CLOCK_CNTL` and continue through the remaining DCN 2.0 generated register mask definitions. The final per-file report should describe the whole header as a generated hardware layout contract rather than as algorithmic driver code.

### subset-b-001613: lines 7155-9821

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 7155-9821

## Scope

This chunk is a middle slice of AMDGPU's generated DCN 2.0.0 register shift/mask header. It is not executable C; it exports preprocessor constants of the form `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` for display-controller MMIO fields. These macros are paired with register addresses from `dcn_2_0_0_offset.h` and consumed by AMD display helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WAIT`, `FD_MASK`, `FD_SHIFT`, `SF`, and `SRI`.

The range starts inside the `MMHUBBUB_CLOCK_CNTL` field list, covers MMHUBBUB reset/error/client-ID controls, VGAIF/MCIF counters, DC perfmon instances, the HDA/Azalia display-audio register blocks, DCHUBBUB SDPIF/return-path/arbitration/VM blocks, DCN VM request contexts 0-15, the beginning of HUBP0, and most of the first HUBPREQ0 surface/request programming block. It ends at the chunk boundary on the `HUBPREQ0_NOM_PARAMETERS_6` comment before that register's field definitions.

## Purpose

The header range describes the bit layout for DCN 2.0 display hub, memory-request, VM, audio, and performance-monitor hardware. Its purpose is to let generic DCN20 code use stable logical field names while the generated register database supplies ASIC-specific bit positions and masks.

Major hardware areas covered here are:

- `MMHUBBUB_*`, `MCIF_*`, `WBIF0_*`, and `DMU_IF_*` fields for MMHUBBUB clock gating, soft reset, outstanding counters, write-combine timeout, memory power state, client unit IDs, and DMU interface error reporting.
- `DC_PERFMON4_*`, `DC_PERFMON5_*`, and `DC_PERFMON6_*` fields for performance-counter event selection, counter state, run/stop control, interrupts, counted values, high/low reads, and control selection.
- `AZF0STREAM*`, `AZF0ENDPOINT*`, `AZF0INPUTENDPOINT*`, and `AZALIA_*` fields for display HDA/Azalia stream-index/data windows, codec endpoint windows, controller clocking, audio DTO, DMA, cyclic buffer, payload capability, CRC diagnostics, memory power, codec root parameters, audio port connectivity, stream formats, power/reset state, and GTC group offsets.
- `DCHUBBUB_SDPIF_*`, `DCN_VM_*`, and local memory aperture fields for display hub access to framebuffer, AGP/system apertures, HBM/local ranges, pipe security levels, and SDPIF power status.
- `DCHUBBUB_RET_PATH_*` fields for DCC return-path configuration, memory power, and CRC capture/readback.
- `DCHUBBUB_ARB_*`, `VTG*_CONTROL`, `DCFCLK_CNTL`, timeout, timer, soft reset, performance-measurement, status, interrupt, and FMON fields for the common display hub's arbitration and timing behavior.
- `DCN_VM_CONTEXT0` through `DCN_VM_CONTEXT15` fields for page-table depth/block-size and per-context page table base/start/end programming, plus system/protection-fault default addresses and fault status/address fields.
- `HUBP0_*` fields for surface configuration, address/tiling layout, primary/secondary viewport dimensions, request-size calculation, HUBP control, clock gating, VM page configuration, debug DB, and DCFCLK/DPPCLK measurement windows.
- `HUBPREQ0_*` fields for pitch, VMID, surface and metadata addresses, flip control, queue behavior, frame pacing, flip interrupt status/ack/mask, current and earliest in-use addresses, request expansion modes, TTU/QoS, aperture and context0 VM defaults, L1 TLB control, blanking/destination geometry, prefetch settings, and vblank/flip/nominal request timing parameters.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or persistent software objects in this chunk. The macro namespace is the API surface:

- `*_SHIFT` values provide the low bit number for a field.
- `*_MASK` values provide the already-positioned mask used for extraction and read/modify/write.
- Address-block comments identify generated hardware blocks such as `dce_dc_mmhubbub_vgaif_dispdec`, `dce_dc_hda_azf0controller_dispdec`, `dce_dc_dchubbub_hubbub_dispdec`, `dce_dc_dchubbub_hubbub_vmrq_if_dispdec`, `dce_dc_dcbubp0_dispdec_hubp_dispdec`, and `dce_dc_dcbubp0_dispdec_hubpreq_dispdec`.

The MMHUBBUB/MCIF macros expose low-level infrastructure controls. `MMHUBBUB_CLOCK_CNTL` gates display, VGAIF, VGA, WBIF0, and XFC clocks. `MMHUBBUB_SOFT_RESET` can reset VGA, VGAIF, WBIF0, and DMUIF. `MMHUBBUB_MEM_PWR_CNTL` and `MMHUBBUB_MEM_PWR_STATUS` describe VGA and display writeback memory power state. `MCIF_*` phase counters and write-combine controls expose memory-interface diagnostics for the VGAIF-side block.

The DC perfmon macros are repeated for perfmon instances 4, 5, and 6. Each instance has `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW`. These fields select events and count modes, gate counting by run-enable or hardware start/stop selectors, report active/counter state, raise or acknowledge interrupts, and expose counter values.

The Azalia/HDA macros include simple index/data windows for streams 0-15 and endpoint/input-endpoint 0-7, plus controller-wide fields. Controller fields cover clock gating, DTO module/phase, SOCCLK controls, underflow filler samples, DMA enable/response, BDL/RIRB/CORB settings, payload capability, stream arbitration, CRC controls/results, and memory power force/disable/status. Codec-root fields expose vendor/device/revision IDs, channel count, resync FIFO, supported rates/formats/power states, reset/power control, subsystem ID response, converter synchronization, audio port connectivity, and GTC group offsets.

The DCHUBBUB macros define common display hub and memory-fabric behavior. SDPIF fields program framebuffer and AGP apertures, VM physical request mode, forced IO status, local HBM ranges, per-pipe security levels, and memory power. Return-path fields carry DCC configuration for up to twelve slices/pipes, CRC enable/mode/mask/region controls, and CRC readbacks. Arbiter fields expose outstanding-request limits, saturation levels, QoS forcing, DRAM state counters, watermarks A-D for data urgency, PTE/meta urgency, self-refresh entry/exit, DRAM clock changes, watermark-change request/done status, timeout enabling, global timers, VTG enable/field/status, DCHUBBUB reset, clock control, DCF clock deep-sleep, performance measurements, vline snapshots, timeout detection, timeout interrupts, indexed debug access, and FMON measurements.

The `DCN_VM_CONTEXT<n>` macros are a generated set for VM request contexts 0-15. Each context has a control register with page-table depth and block size, plus high/low page-table base, start, and end address fields. The shared VM fields include default system/protection-fault addresses, fault control bits for dummy page handling and retry/default behavior, fault status bits for invalid/PDE/PTE/read/write/faulted context, and fault address capture.

The `HUBP0_*` macros describe the first hub pipe's surface-facing programming. Important fields include surface type, alternate metadata usage, surface array mode, pipe/number-of-banks/bank-width/bank-height/tile-split/meta layout, viewport x/y/width/height for luma/chroma and primary/secondary planes, chunk/min-chunk/meta/PTE-group request sizing for luma and chroma, hubp enable/blanks/underflow/urgent state, deadlock detection, clock gating, VMPG enable, debug DB, and DCFCLK/DPPCLK measurement windows.

The `HUBPREQ0_*` macros describe the first hub pre-request generator. Surface-address fields cover primary/secondary luma/chroma and metadata addresses, high address words, current in-use address readbacks, and earliest-in-use readbacks. `DCSURF_SURFACE_CONTROL`, `DCSURF_FLIP_CONTROL`, `DCSURF_FLIP_CONTROL2`, `DCSURF_QUEUE_CONTROL`, `FRAME_PACING_TIME`, and `SURFACE_FLIP_INTERRUPT` define flip timing, swap locking, immediate/near/immediate-disable behavior, queue depth, pacing, interrupt status, interrupt type, ack, and masks. TTU/QoS and timing fields include expansion mode, TTU watermarks, fixed QoS and ramp disable for surfaces and cursors, VM aperture defaults, context0 fault/default/page-table fields, L1 TLB control, blank offsets, destination dimensions, after-scaler coordinates, prefetch ratios, vblank parameters, flip parameters, and nominal PTE/meta request timing through `HUBPREQ0_NOM_PARAMETERS_5`.

## Control Flow

This header has no runtime control flow. Runtime behavior appears only in consumers that combine these generated fields with register addresses and MMIO helper functions.

A typical control sequence is:

1. A DCN20 resource, DMUB, IRQ, VMID, hubbub, HUBP, IPP, audio, or GMC file includes `dcn_2_0_0_offset.h` and this shift/mask header.
2. Register tables are built with macros such as `SRI(...)`, `SF(...)`, `HWS_SF(...)`, `FD_MASK(...)`, and `FD_SHIFT(...)`.
3. Driver code calls helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_WAIT`, `RREG32_SOC15`, or `REG_GET_FIELD`.
4. The helpers use these generated shifts and masks to extract a field, clear a field, or insert a new field value in a read/modify/write sequence.
5. Hardware then performs the real state transition: reset, clock gate, VM translation, page fault capture, surface flip, request scheduling, watermark change, audio DMA update, CRC capture, or perf counter update.

Control-sensitive flows represented by this chunk include DMUB reset through `MMHUBBUB_SOFT_RESET__DMUIF_SOFT_RESET`, framebuffer base/offset discovery through `DCN_VM_FB_LOCATION_BASE` and `DCN_VM_FB_OFFSET`, VMID page-table setup through `DCN_VM_CONTEXT0_*` field aliases, HUBPREQ flip interrupt/ack handling through `HUBPREQ0_DCSURF_SURFACE_FLIP_INTERRUPT`, hubbub soft reset and arbitration/watermark programming, HDA/Azalia audio clock/DMA setup, DCHUBBUB CRC capture, timeout detection, and display writeback/MMHUBBUB memory power management.

The macros do not encode ordering constraints. Callers must still know when a field is read-only, write-one-to-clear, self-clearing, sticky, double-buffered, safe only during blank, safe only while disabled, or owned by firmware.

## State And Persistence Behavior

The file stores no software state and performs no persistence. It describes hardware register state that persists according to DCN/MMIO semantics until rewritten, reset, power-gated, or changed by hardware/firmware.

State represented in this chunk includes:

- MMHUBBUB and MCIF state: clock gate disables, soft resets, memory power force/disable/status, outstanding-request counters, write-combine timeout, DMU read outstanding error and clear bits, and client unit IDs.
- Performance-monitor state: selected events, count modes, run-enable and start/stop selectors, active state, interrupt enable/status/ack bits, high/low counter values, and count-off behavior.
- Audio/HDA state: stream index/data ports, endpoint command windows, controller clocking and DTO, DMA enable/status, cyclic buffer position, payload capabilities, arbitration policy, CRC settings/results, Azalia memory power, codec identity/capability/power/reset registers, and port connectivity.
- DCHUBBUB state: framebuffer/aperture address windows, HBM/local-memory ranges, security levels, return-path DCC configuration, CRC windows/results, arbitration watermarks, DRAM/self-refresh/clock-change controls, timeout and interrupt status, global timer/VTG state, clock/DCFCLK controls, and performance measurement readbacks.
- VM state: per-context page-table base/start/end ranges for contexts 0-15, context depth/block-size, default addresses for system and protection-fault handling, fault enable/default behavior, fault status, faulted context, and fault address capture.
- HUBP/HUBPREQ0 state: surface format/tiling/viewport, request sizing, underflow/urgent/deadlock status, clock gating, VM page config, surface and metadata addresses, flip locks and flip timing, queue and pacing state, flip interrupt status/ack/mask, current and earliest in-use addresses, TTU/QoS policy, TLB and aperture configuration, and vblank/flip/nominal prefetch request timing.

Some fields are latched programming values, some are live status readbacks, some are counters, and some are sticky interrupt/fault bits that require explicit clear or acknowledgement. Reset, suspend/resume, runtime power management, display mode set, page flip, DMUB firmware execution, memory-controller setup, HDA audio handling, and GPU VM faults can all alter the underlying hardware state. The generated header does not document access permissions, default values, lock ordering, or volatility.

## Dependencies And Integration Points

The direct generated companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h`, which provides the register addresses and base indexes. This file provides the bit positions inside those addresses.

Direct include and usage points visible in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`, which includes the DCN 2.0 offset and mask headers, builds DMUB register field tables through `FD_MASK`/`FD_SHIFT`, reads DCN VM framebuffer base/offset fields, and toggles `MMHUBBUB_SOFT_RESET.DMUIF_SOFT_RESET` during DMUB reset/release.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`, which includes this header and uses `HUBPREQ0_DCSURF_SURFACE_PITCH.PITCH` to derive visible framebuffer pitch.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_vmid.h`, which maps `DCN_VM_CONTEXT0_*` shift/mask fields into DCN20 VMID register tables used by VM page-table setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`, which includes the header and builds IRQ register entries for DCN20 display interrupts, including HUBP/HUBPREQ flip-related sources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn20/dcn20_mmhubbub.h` and `.c`, which map MMHUBBUB/MCIF writeback fields used for display writeback buffer management, watermarking, address programming, security, and memory power behavior.
- Shared DCE/DCN hardware sequencing and audio code, including `display/dc/hwss/dce/dce_hwseq.h` and `display/dc/dce/dce_audio.c`, which use DCHUBBUB, Azalia, and display-audio field families through generation-specific register tables.
- HUBP/HUBPREQ and IPP-related code, including `display/dc/dcn10/dcn10_ipp.h` and later IRQ services, which rely on the repeated `HUBPREQ0_*` field shape for cursor settings and page-flip interrupt handling across DCN generations.

Although the repository path sits under `sources/distributed-fs/ceph-client`, this chunk is AMDGPU display hardware metadata. It has no Ceph protocol logic, filesystem cache state, network messaging, or distributed-storage persistence behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A generated shift or mask can be wrong while all C code still compiles, causing a read/modify/write helper to alter the wrong bit, fail to clear a sticky bit, corrupt an adjacent field, or poll a status bit that never changes.

High-risk reset and clock fields include `MMHUBBUB_SOFT_RESET`, `MMHUBBUB_CLOCK_CNTL`, `DCHUBBUB_SOFT_RESET`, `DCHUBBUB_CLOCK_CNTL`, and `DCFCLK_CNTL`. Incorrect masks here can leave display firmware, hubbub, VGAIF, writeback, or request fabric blocks stuck in reset, ungated at the wrong time, or clock-gated while active.

VM and aperture fields are especially sensitive. Incorrect masks in `DCN_VM_FB_LOCATION_BASE`, `DCN_VM_FB_OFFSET`, `DCN_VM_CONTEXT<n>_*`, `DCN_VM_FAULT_*`, `HUBPREQ0_DCN_VM_SYSTEM_APERTURE_*`, `HUBPREQ0_DC_VM_CONTEXT0_*`, or `HUBPREQ0_DCN_VM_MX_L1_TLB_CNTL` can translate display memory through the wrong page tables, hide protection faults, trigger dummy-page behavior unexpectedly, display stale/wrong memory, or break DMUB address translation.

Surface and flip fields can fail visibly. Bad constants in `HUBP0_DCSURF_*`, `HUBPREQ0_DCSURF_*`, `HUBPREQ0_DCSURF_FLIP_CONTROL*`, `HUBPREQ0_DCSURF_QUEUE_CONTROL`, or `HUBPREQ0_DCSURF_SURFACE_FLIP_INTERRUPT` can cause black frames, corrupted tiling, wrong chroma addresses, page flips at the wrong vblank, missed flip interrupts, hung page flips, underflow, or frame-pacing errors.

Watermark, TTU, and arbitration fields affect bandwidth and power. Incorrect `DCHUBBUB_ARB_*`, `HUBPREQ0_DCN_TTU_QOS_WM`, `HUBPREQ0_DCN_GLOBAL_TTU_CNTL`, `HUBPREQ0_*_TTU_CNTL*`, vblank/flip/nominal parameter, and prefetch masks can allow self-refresh or clock changes too aggressively, block power savings, or cause underflow/flicker under memory pressure.

Audio and Azalia fields have protocol-visible risk. Errors in stream index/data, endpoint index/data, audio DTO, DMA, payload capability, CRC, codec capability, power/reset, and connectivity fields can produce missing HDMI/DP audio, wrong channel/rate advertisement, endpoint access failures, CRC diagnostic mismatches, or audio power-management regressions.

The range contains several repeated generated patterns: DC perfmon instances, Azalia streams/endpoints, DCC return-path instances, VM contexts 0-15, VTG controls, and luma/chroma surface-address families. Instance suffix mistakes are hard to catch at compile time because the macro names remain valid and structurally similar.

Chunk-boundary risk is present at both ends. The chunk begins inside the existing `MMHUBBUB_CLOCK_CNTL` register's shift/mask group and ends at the `HUBPREQ0_NOM_PARAMETERS_6` comment before that register's definitions. The final merge lane should treat those as artificial chunk boundaries, not missing source content.

## Test Signals

Useful validation signals are mostly generated-header checks plus DCN20 display behavior:

- Build coverage for DCN20 display, DMUB, GMC, VMID, IRQ, hubbub/MMHUBBUB, HUBP/HUBPREQ, and audio code that includes `dcn_2_0_0_sh_mask.h`.
- Generated-register validation that every `*_MASK` in this chunk matches its corresponding `*__SHIFT`, does not overlap unintended fields, and matches AMD's authoritative DCN 2.0.0 register database and the companion `dcn_2_0_0_offset.h`.
- DMUB boot/reset tests that exercise `MMHUBBUB_SOFT_RESET.DMUIF_SOFT_RESET`, framebuffer base/offset translation, inbox/outbox pointer reset, and firmware response handling.
- GPU memory-controller and framebuffer tests that verify `HUBPREQ0_DCSURF_SURFACE_PITCH.PITCH`, VM framebuffer base/offset, AGP/system aperture, and local/HBM address handling.
- VMID tests that program DCN VM contexts, validate page-table base/start/end ranges, trigger expected display VM faults, and confirm fault status/address fields identify invalid, PDE/PTE, read/write, and context information correctly.
- Display modeset, page-flip, and cursor stress tests that exercise HUBP0 surface config, viewport, tiling, request sizing, HUBPREQ0 address flips, flip locks, queue controls, flip interrupts, current/earliest in-use readbacks, and cursor timing.
- Bandwidth and power-management tests under high-resolution, multi-plane, cursor, writeback, and memory-clock-change workloads, watching for underflow, timeout, watermark-change, self-refresh, and TTU/QoS regressions.
- HDA/HDMI/DP audio tests that validate Azalia controller clocking, DTO, endpoint access, stream DMA state, advertised codec capabilities, channel/rate handling, hotplug audio enablement, and audio CRC diagnostics.
- DCHUBBUB CRC, performance counter, timeout, VTG, FMON, and debug-index/data diagnostics that confirm status bits, interrupt ack/clear behavior, counter values, and readback fields move as expected.

Regression symptoms from bad constants include blank display, corrupted scanout, wrong framebuffer pitch, missed page-flip completion, flip timeout, display underflow, VM faults on valid scanout buffers, failure to report VM faults, DMUB reset/load failure, bad display audio, broken suspend/resume, excessive display power, unreliable memory-clock changes, or perf/CRC/debug tools reporting impossible values.

## Cross-Chunk Notes

This is not a standalone source module; it is one chunk of a large generated DCN 2.0.0 register layout contract. Neighboring chunks own the preceding MMHUBBUB/WBIF register definitions and the continuation of `HUBPREQ0_NOM_PARAMETERS_6` plus the remaining HUBPREQ/HUBP/DCN register families. The later merge/reconciliation lane should combine the chunks into a single per-file view and avoid treating this artificial line range as a hardware boundary.

### subset-b-001614: lines 9822-12326

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 9822-12326

## Scope

This chunk is part of the generated AMD DCN 2.0.0 ASIC register mask/shift header. It covers lines 9822-12326 and contributes register field metadata for DC display hub pipe blocks, mostly pipes 0, 1, and 2. The chunk contains 2,104 `#define` entries: 1,052 `__SHIFT` constants and 1,052 `_MASK` constants. There are no C functions, structs, enums, or runtime control-flow constructs in this slice; the exported surface is preprocessor constants consumed by register accessor macros elsewhere in the AMDGPU display driver.

## Purpose

The purpose of this chunk is to define exact bit positions and bit masks for DCN 2.0.0 display front-end register fields. These definitions let the display core encode, update, poll, and decode fields inside memory-mapped hardware registers without hard-coded literal bit arithmetic in functional code.

The visible hardware domains are:

- Late `HUBPREQ0` request metadata fields for nominal timing, per-line delivery, cursor request adjustment, ref-clock-to-pixel-clock ratio, destination Y request limits, and HUBPREQ memory power control/status.
- `HUBPRET0`, `HUBPRET1`, and `HUBPRET2` return path fields for detile buffer routing, memory power, read-line windows, vblank/read-line interrupts, current read-line value, and read-line status.
- `CURSOR0_0`, `CURSOR0_1`, and `CURSOR0_2` fields for cursor enable/mode/pitch/position/hotspot/stereo, cursor memory power, and DMDATA address/QoS/status/software data.
- `DC_PERFMON7`, `DC_PERFMON8`, and the start of `DC_PERFMON9` performance monitor fields for counter selection, state, run/stop control, interrupt status/acknowledge, and counter readout.
- `HUBPXFC0` and `HUBPXFC1` fields for cross-fabric/XFC enablement, XBUF read base addresses, pitch, delay/precharge/prefetch margins, underflow status, slave VTG/scaler timing, and MPC destination placement.
- `HUBP1` and `HUBP2` pipe-local hub pixel processor fields for surface format, tiling, viewports, request sizes, hubp enable/blank/underflow/timeout, clock control/status, VMPG page size, debug, and measurement window controls.
- `HUBPREQ1` and `HUBPREQ2` request path fields for surface pitch, VMID, primary/secondary and chroma/luma surface addresses, DCC/TMZ surface control, flip control, queuing, pacing, in-use addresses, VM aperture/context controls, TTU/QoS timing, prefetch/vblank/flip/nominal timing parameters, cursor settings, and request-side memory power.

## Important API Surface

The API surface is macro naming, not callable symbols. Each hardware field follows the pattern:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Examples from the chunk include:

- `HUBP1_DCSURF_SURFACE_CONFIG__SURFACE_PIXEL_FORMAT__SHIFT` and `_MASK` for extracting or programming pipe 1 surface format.
- `HUBPREQ1_DCSURF_FLIP_CONTROL__SURFACE_UPDATE_LOCK__SHIFT` and `_MASK` for the pipe 1 surface update lock bit.
- `HUBPREQ1_DC_VM_CONTEXT0_CNTL__ENABLE_CONTEXT__SHIFT` and `_MASK` for display VM context enablement.
- `CURSOR0_1_CURSOR_CONTROL__CURSOR_ENABLE__SHIFT` and `_MASK` for enabling pipe 1 cursor composition.
- `HUBPRET2_HUBPRET_INTERRUPT__PIPE_VBLANK_INT_CLEAR__SHIFT` and `_MASK` for clearing pipe 2 return-path vblank interrupt state.
- `DC_PERFMON8_PERFCOUNTER_CNTL__PERFCOUNTER_EVENT_SEL__SHIFT` and `_MASK` for selecting pipe 1/DC perfmon events.
- `HUBPXFC1_HUBP_XFC_UNDERFLOW_STATUS__XFC_UNDERFLOW_CLR__SHIFT` and `_MASK` for acknowledging XFC underflow state.

The constants are intended to be included by higher-level display code using register helper macros such as `HUBP_SF`, `IPP_SF`, `TF_SF`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_READ`, and register table initializers. Inclusion sites found for this DCN 2.0.0 mask header include DC resource setup, IRQ service, clock manager, GPIO factory, DMUB DCN20 support, and GMC 10 code.

## Control Flow

There is no local control flow in this header chunk. Runtime control flow is external:

- Resource initialization code includes this header and expands mask/shift list macros into field tables. For DCN-style hubp code, `HUBP_MASK_SH_LIST_*(__SHIFT)` and `HUBP_MASK_SH_LIST_*(_MASK)` build `shift` and `mask` tables from these constants.
- Functional hubp/cursor/interrupt code calls register access helpers with symbolic field names. The helpers combine the register address, this chunk's mask, and this chunk's shift to write field values or decode register contents.
- IRQ code uses fields such as `HUBPRETn_HUBPRET_INTERRUPT` or surface flip interrupt fields to mask, clear, and query vblank/read-line/flip events.
- Power and validation paths can poll status fields such as `HUBP*_DCHUBP_CNTL__HUBP_NO_OUTSTANDING_REQ`, `*_UNDERFLOW_STATUS`, `*_MEM_PWR_STATUS`, and `*_CLOCK_ON` after programming the control fields.

The observable ordering contract is implicit: callers must program related fields in hardware-required order. This chunk only supplies bit locations and does not enforce ordering between surface address updates, update locks, VM context setup, clock enables, memory power transitions, or interrupt clears.

## State and Persistence

The file itself has no persistent software state. The macros map to persistent hardware state while the GPU is powered:

- Surface address, pitch, format, viewport, tiling, DCC, TMZ, VMID, and VM context fields determine which memory the display pipe fetches and how it interprets it.
- Flip, queue, pacing, in-use, and earliest-in-use fields expose or control surface update sequencing across frame boundaries.
- Prefetch, vblank, nominal, TTU, per-line delivery, and ref-clock conversion fields persist as timing parameters used by the HUBPREQ scheduler.
- Clock, blank, disable, timeout, underflow, memory power control, and status fields represent live pipe state and hardware health.
- Interrupt status/acknowledge/clear fields persist until software clears them or hardware transitions state.
- Perfmon counter registers hold selected measurement configuration and sampled/counted values.

Because these are memory-mapped hardware fields, stale or incorrect masks can produce persistent display corruption, faults, underflow state, or missed interrupt acknowledgements until the driver reprograms the block or the hardware is reset.

## Dependencies and Integration Points

This chunk depends on the generated register address header for matching register offsets, usually `dcn_2_0_0_offset.h`, and on AMD display helper macros that paste register and field names into `_MASK` and `__SHIFT` identifiers. The constants are tightly coupled to the DCN 2.0.0 hardware specification.

Important integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`, which includes this header for DCN 2.0 resource construction.
- `drivers/gpu/drm/amd/display/dc/hubp/dcn10` and `dcn20` hubp helpers, whose register and mask/shift list macros include many HUBP/HUBPREQ/CURSOR fields represented here.
- `drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`, which uses this generation family for interrupt source setup and clearing.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`, where generated DCN register metadata is shared with DMUB-facing display code.
- Cross-generation DCN headers such as `dcn_2_0_1_sh_mask.h`, `dcn_2_1_0_sh_mask.h`, and later `dcn_3_*`/`dcn_4_*` headers, which preserve many similarly named fields but may change masks, presence, or register coverage.

The pipe suffixes are part of the integration contract. This chunk covers pipe-specific copies such as `HUBPREQ1` and `HUBPREQ2`; generic driver code commonly uses macro indirection like `SRI(..., HUBPREQ, id)` and field-list macros based on the pipe instance.

## Risks

- A wrong shift/mask pair can silently write the wrong hardware bits. This is especially risky for surface addresses, VM aperture/context controls, DCC/TMZ flags, update-lock bits, interrupt acknowledgements, and memory power controls.
- Pipe instance copy/paste drift is a major risk. `HUBPREQ1` and `HUBPREQ2` blocks are nearly identical; a single mismatched field width or mask between instances could affect only one display pipe and be hard to reproduce.
- Address-high masks are typically 16-bit while address-low masks are 32-bit. Treating them uniformly would truncate or corrupt 48-bit surface, metadata, VM, or DMDATA addresses.
- Clear/ack fields share registers with status and mask/type bits. Incorrect use of `_MASK` constants in read-modify-write paths can clear interrupts unexpectedly or fail to clear sticky status.
- Timing fields have narrow widths, often 10-23 bits depending on the field. Overflow before masking can convert a calculated prefetch/vblank/nominal timing value into a low wrapped value and cause underflow or missed deadlines.
- Power and clock fields combine force, disable, low-power mode, and live status bits. Confusing control and status masks can leave memories or clocks gated while the pipe is expected to fetch.
- The chunk starts and ends mid-logical-region: it begins with the tail of `HUBPREQ0` and ends at the start of `DC_PERFMON9_PERFCOUNTER_STATE`. Whole-file reconciliation must merge adjacent chunks to describe the full DCN 2.0.0 register map.

## Test Signals

Useful validation signals for changes to this chunk are primarily build-time and hardware/display behavior:

- Full AMDGPU/display driver compilation should catch missing, renamed, or syntactically invalid macros in resource, hubp, irq, dmub, and clock manager code.
- Static comparison against the vendor register database or adjacent generated DCN headers can catch accidental mask/shift drift, especially across the repeated pipe 1 and pipe 2 blocks.
- Runtime display validation should exercise multi-pipe modes, cursor enable/position/hotspot changes, primary and secondary plane flips, DCC-enabled scanout, rotated/mirrored surfaces, VM-enabled display fetches, and secure/TMZ surfaces.
- Interrupt tests should verify vblank, read-line, and surface flip interrupt mask/status/clear behavior for the affected pipe instances.
- Stress signals include absence of HUBP/HUBPXFC underflow, timeout, VM fault, DMDATA underflow, and lost-command counters during mode set, page flip, cursor movement, suspend/resume, and memory power/clock gating transitions.
- Perfmon sanity checks should confirm `DC_PERFMON7/8/9` counter selection, run/stop, interrupt status/ack, and high/low readout behavior when using DC performance monitoring tooling.

## Chunk Notes

This is a generated constants-only slice. The substantive behavior lives in the display core code that consumes the constants and in the DCN 2.0.0 hardware. The key research value of this chunk is the exact register-field coverage and the high-risk domains represented by the masks: display memory fetch setup, VM/DCC/TMZ security and compression controls, flip synchronization, pipe timing, interrupts, power/clock status, cursor metadata, XFC underflow tracking, and performance monitor state.

### subset-b-001615: lines 12327-14826

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 12327-14826

## Purpose

This chunk is part of AMDGPU's generated DCN 2.0 register field mask header. It contains no executable C logic; it publishes compile-time bit positions and already-shifted masks for Display Core Next 2.0 hardware registers. Consumers combine these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros with matching register offsets from `dcn_2_0_0_offset.h` and the display register helper macros.

The assigned range spans 2,105 macros. It starts inside the `DC_PERFMON9` block for the HUBP2 display pipe, covers the HUBP XFC tail for pipe 2, then defines the repeated HUBP/HUBPREQ/HUBPRET/cursor/perfmon/XFC field layouts for pipes 3 and 4. It ends at the start of pipe 5 HUBP fields, after `HUBP5_DCHUBP_CNTL`.

Major hardware areas represented here are:

- `DC_PERFMON9`, `DC_PERFMON10`, and `DC_PERFMON11` display performance monitor fields for HUBP instances 2, 3, and 4.
- `HUBPXFC2`, `HUBPXFC3`, and `HUBPXFC4` cross-FIFO/compressed-buffer read, delay, slave timing, scaler, MPC, and underflow-status fields.
- `HUBP3`, `HUBP4`, and the start of `HUBP5` DCSURF/DCHUBP fields for surface format, tiling, viewport, request sizing, hubp control, clock control, virtual memory page size, debug, and clock-domain measurement windows.
- `HUBPREQ3` and `HUBPREQ4` fields for pitch, VMID, surface and metadata addresses, flip and queue controls, pacing, in-use address readback, TTU/QoS, VM apertures and page-table registers, TLB control, blank/prefetch/nominal delivery parameters, cursor fetch settings, memory power control, and status.
- `HUBPRET3` and `HUBPRET4` return-path fields for memory power, read-line control/readback, interrupts, and status.
- `CURSOR0_3` and `CURSOR0_4` fields for cursor image addressing, size, position, hot spot, stereo offsets, destination offset, cursor memory power, and DMDATA memory/software payload control.

Although the repository path is under `ceph-client`, this chunk is AMDGPU display hardware metadata. It has no Ceph filesystem protocol behavior and no distributed filesystem state.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or storage objects in this range. The macro namespace is the API surface.

Every field appears as a pair:

- `REGISTER__FIELD__SHIFT`: the field's low bit position within a 32-bit MMIO register.
- `REGISTER__FIELD_MASK`: the field mask in its final register position.

The pipe-specific prefixes are the main structure:

- `HUBP3_*`, `HUBP4_*`, and `HUBP5_*` describe the hub pipe's local DCSURF/DCHUBP register fields. Key fields include pixel format, rotation, mirror, address configuration, tiling mode, primary/secondary viewport rectangles, luma/chroma request sizes, blank/disable/underflow control, VTG selection, TTU mode, timeout handling, clock gating status, virtual-memory page size, debug, and measurement-window controls for DCFCLK and DPPCLK.
- `HUBPREQ3_*` and `HUBPREQ4_*` describe the request side of a hub pipe. They expose surface pitch, primary/secondary luma and chroma base addresses, metadata addresses, surface control, flip control, flip interrupt/status, in-use and earliest-in-use addresses, expansion mode, TTU watermarks, global TTU controls, per-surface and per-cursor TTU controls, VM system apertures, VM context page-table/protection-fault registers, L1 TLB control, prefetch and vblank timing parameters, flip/nominal delivery timing, cursor settings, and memory power control/status.
- `HUBPRET3_*` and `HUBPRET4_*` describe the return path. They include enable/control, memory power control/status, read-line controls, line readback values, interrupt fields, and status fields.
- `CURSOR0_3_*` and `CURSOR0_4_*` describe the first cursor plane attached to HUBP3/HUBP4. They cover enable/mode/pitch/lines-per-chunk, surface address high/low, size, position, hot spot, stereo offsets, destination offset, memory power, and DMDATA address/control/QoS/status/software data registers.
- `DC_PERFMON9_*`, `DC_PERFMON10_*`, and `DC_PERFMON11_*` describe display performance counters. They include counter event selection, counted-value selection, increment mode, hardware/run-enable controls, counter-off interrupt controls, counter state selection, current value readback, high/low counter registers, and interrupt status/ack fields for counters 0-7.
- `HUBPXFC2_*`, `HUBPXFC3_*`, and `HUBPXFC4_*` describe XFC-related buffering. They include MXFC/SXFC enable, 64-bpp and bandwidth-reduction modes, read VMID, chunk size, XBUF base0/base1 addresses, pitch, delay configuration, prefetch margin, underflow watermark/status/clear counters, slave VTG offsets, slave scaler ratio/init, and MPC destination start.

The chunk also contains repeated luma/chroma variants with `_C` suffixes, for example `DCSURF_SURFACE_PITCH_C`, `DCSURF_PRIMARY_SURFACE_ADDRESS_C`, `DCHUBP_REQ_SIZE_CONFIG_C`, `PREFETCH_SETTINGS_C`, and chroma viewport fields. These are part of planar or multi-plane surface programming.

## Control Flow

This header has no runtime control flow. It is preprocessor data used by runtime display-driver code.

A typical consumer flow is:

1. The DCN 2.0 resource code selects an instance register address from `dcn_2_0_0_offset.h`.
2. The matching shift/mask value from this header is placed into a per-block register table, commonly through macros such as `HUBP_MASK_SH_LIST_DCN20(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN20(_MASK)`.
3. HUBP, cursor, VM, IRQ, DMUB, or GMC code uses register helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, or `REG_WAIT`.
4. Those helpers apply the stored shift/mask values to read, insert, clear, wait for, or write the desired hardware field.

The control-sensitive hardware actions represented by this chunk include enabling/disabling hub pipes, blanking, waiting for outstanding requests to drain, programming surface format/tiling/viewport/pitch/address metadata, switching luma/chroma surfaces on flips, programming VM apertures and page-table ranges, clearing underflow or timeout status, setting cursor location and image memory, programming DMDATA payload delivery, configuring prefetch/TTU timing, controlling memory power states, and collecting perfmon counter values. The macros themselves do not enforce valid sequencing or legal values.

## State And Persistence Behavior

The file stores no software state and has no persistence mechanism. It describes state held in DCN 2.0 hardware registers.

The hardware state represented here includes:

- Surface state: pixel format, rotation, mirroring, tiling, address layout, viewport rectangles, pitch, base addresses, metadata addresses, stereo surface controls, surface control bits, flip mode, flip status, and in-use address readback.
- Fetch and timing state: request sizes, chunk/group sizes, prefetch parameters, vblank/flip/nominal delivery timing, per-line delivery, TTU watermarks, TTU enable/mode, reference-clock to pixel-clock ratios, and cursor fetch adjustments.
- VM state: VMID selection, system apertures, default addresses, context0 page-table base/start/end, protection-fault default/fault addresses, and L1 TLB controls.
- Cursor and DMDATA state: cursor enable/mode/pitch/position/hot spot, stereo offsets, destination offset, cursor memory power, DMDATA address, DMDATA update/repeat/mode/size, QoS, underflow, and software-injected data.
- Power/status/debug state: HUBP clock enables/gating status, HUBP/HUBPREQ/HUBPRET/CURSOR memory power controls and status, read-line status, debug registers, timeout/underflow status and clear bits.
- Performance monitor state: counter event selection, run modes, counted values, interrupt enable/status/ack, counter high/low values, and read selectors.
- XFC state: XBUF read addresses/pitch, transfer and precharge delays, underflow watermark/status/counters, slave timing offsets, scaler ratio/init, and MPC destination start.

Persistence follows hardware reset and power-management semantics rather than file semantics. Some fields are latched programming values, some are live status bits, some are readback-only addresses or counters, some are sticky status bits requiring explicit clear/ack writes, and some may be reset by display power gating, mode set, suspend/resume, firmware activity, or ASIC reset. This generated header does not encode read-only, write-one-to-clear, self-clearing, or ordering rules.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.0 register-header ecosystem:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h` supplies the matching MMIO register addresses and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h` supplies the field layouts, including this chunk.
- Display core register helpers consume these constants through generated field macros and per-block shift/mask tables.

Direct include sites found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

The closest high-level integration point for the fields in this chunk is the DCN 2.0 HUBP resource setup. `dcn20_resource.c` builds six `dcn_hubp2_registers` entries with `HUBP_REG_LIST_DCN20(id)` and fills `dcn_hubp2_shift`/`dcn_hubp2_mask` with `HUBP_MASK_SH_LIST_DCN20(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN20(_MASK)`. `dcn20_hubp.h` defines those lists by mapping generic fields such as `CURSOR_ENABLE`, `DMDATA_UPDATED`, `VMID`, `HUBP_VREADY_AT_OR_AFTER_VSYNC`, and `SURFACE_TRIPLE_BUFFER_ENABLE` to concrete register-field macros from this generated header.

Runtime users are mainly HUBP code under `display/dc/hubp/`. The lower-level HUBP implementation uses `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT` for `DCHUBP_CNTL`, `DCSURF_*`, `HUBPRET_CONTROL`, TTU/prefetch parameters, VM aperture/page-table registers, cursor registers, and DMDATA registers. IRQ integration also depends on matching generated field names for flip, vblank/vline, VM fault, underflow, and perfmon interrupt status/ack fields.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong shift or mask compiles cleanly but can update the wrong bit, leave the intended field unchanged, corrupt an adjacent field during read-modify-write, or cause wait loops to observe the wrong status bit.

High-risk fields in this chunk include:

- Surface addressing and metadata fields, because incorrect low/high address or pitch masks can fetch from the wrong framebuffer or compression metadata.
- Format, tiling, viewport, request-size, and chunk/group-size fields, because they affect memory layout, swath fetch, and bandwidth calculations.
- Flip and in-use fields, because incorrect flip programming can cause tearing, stale-frame display, incorrect flip interrupts, or use-after-free of scanout buffers.
- VM aperture, page-table, VMID, and protection-fault fields, because mismatches can cause GPU VM faults, memory isolation failures, or invalid display fetches.
- Underflow, timeout, memory-power, and clock-gating bits, because incorrect status/clear or power sequencing can hide real failures or produce intermittent blanking.
- Cursor/DMDATA fields, because bad cursor addressing or size can display corrupt cursors and bad DMDATA update/QoS fields can trigger underflow or missed metadata delivery.
- TTU, vblank, prefetch, and per-line delivery fields, because they are timing-sensitive and depend on mode timing, clocks, memory latency, and bandwidth model output.
- Perfmon fields, because wrong counter select, status, or ack fields can break diagnostics without affecting normal modeset behavior.
- XFC fields, because read base, delay, prefetch margin, and underflow watermark/status fields affect compressed-buffer transfer behavior and underflow reporting.

The repetition across instances 3 and 4 creates copy-generation risk. `HUBP3` and `HUBP4`, `HUBPREQ3` and `HUBPREQ4`, `HUBPRET3` and `HUBPRET4`, `CURSOR0_3` and `CURSOR0_4`, `DC_PERFMON10` and `DC_PERFMON11`, and `HUBPXFC3` and `HUBPXFC4` largely mirror each other. A mismatched suffix, missing chroma variant, or one-off mask width error may only fail on a specific pipe or display topology.

The chunk boundaries are artificial. The first lines continue `DC_PERFMON9_PERFCOUNTER_STATE` from the previous chunk, and the final lines stop after `HUBP5_DCHUBP_CNTL` before the remaining `HUBP5` fields. The final per-file reconciliation should treat these as line-splitting artifacts, not logical source omissions.

## Test Signals

Useful validation is mostly build-time, generated-header consistency, and hardware behavior:

- Kernel/driver builds for DCN 2.0 display paths should compile all generated field names referenced by DCN 2.0 resource, HUBP, IRQ, GPIO, clock, DMUB, and GMC code.
- A generated-register audit should compare every `*_MASK`/`*__SHIFT` pair in this line range against AMD's source register database and the companion addresses in `dcn_2_0_0_offset.h`.
- Static checks should verify each mask is consistent with its shift and field width, and that mirrored instance families remain symmetric where the hardware database expects symmetry.
- Display modeset tests should exercise pipes 3 and 4, plus pipe 5 once later chunks provide the remaining fields, across primary and overlay-like surface programming.
- Plane tests should cover luma/chroma pitch, viewport, metadata address, tiling, rotation, mirror, stereo, and flip-control combinations.
- Cursor tests should cover enable/disable, hotspot, negative/edge positions, different cursor sizes and pitches, stereo cursor offsets, memory power state transitions, and DMDATA delivery.
- VM tests should exercise VMID programming, system aperture boundaries, page-table base/start/end, protection-fault handling, and suspend/resume restoration.
- Bandwidth/timing tests should verify prefetch, vblank, flip, nominal, TTU, per-line delivery, and request-size fields under high-resolution, multi-plane, high-refresh, and memory-pressure scenarios.
- IRQ and status tests should verify flip, underflow, timeout, VM fault, read-line, DMDATA underflow, and perfmon status/ack bits transition as expected.
- Power-management tests should stress clock gating, HUBP/HUBPREQ/HUBPRET/CURSOR memory power controls, hotplug, modeset, runtime suspend, and system suspend/resume.
- Perfmon diagnostics should confirm event selection, counter running state, count-off interrupts, counter high/low reads, and interrupt ack behavior for the covered performance monitor instances.
- XFC-specific tests should verify XBUF base/pitch programming, prefetch margin, delay settings, underflow watermark/status/counter behavior, and slave timing/scaler/MPC configuration.

Regression symptoms from bad constants include blank or flickering display, wrong colors or format, corrupt scanout, cursor corruption, lost or repeated flips, spurious underflow/timeout reports, missed interrupts, GPU VM faults, broken DMDATA delivery, failed resume, unstable high-refresh modes, inaccurate perfmon data, or failures isolated to HUBP3/HUBP4/HUBP5 instance-specific display configurations.

## Cross-Chunk Notes

Earlier chunks of `dcn_2_0_0_sh_mask.h` define preceding DCN 2.0 display register field families, HUBP0-HUBP2 portions, and the start of `DC_PERFMON9_PERFCOUNTER_STATE`. Later chunks complete the remainder of `HUBP5` and continue through subsequent DCN 2.0 register field groups. The final merged per-file research document should describe this source as one generated hardware register layout contract, with this chunk contributing the mid-file HUBP/HUBPREQ/HUBPRET/cursor/perfmon/XFC instance coverage.

### subset-b-001616: lines 14827-17349

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 14827-17349

## Purpose

This chunk is part of AMDGPU's generated DCN 2.0 register field mask header. It contains no executable C code; it publishes preprocessor constants that describe bit shifts and already-positioned bit masks for hardware registers in one late HUBP5 pipe and the beginning of DPP0/color-management register space.

The range starts at the tail of the `HUBP5_DCHUBP_CNTL` field definitions, then covers address blocks for the fifth hub pipe request path and its companion cursor/performance/XFC logic:

- `HUBP5` clock, blanking, disable, timeout, underflow, virtual-memory page, request-debug, and DCFCLK/DPPCLK measurement-window controls.
- `HUBPREQ5` surface pitch, VMID, primary/secondary luma/chroma surface addresses, primary/secondary metadata addresses, DCC/TMZ surface control, flip control, flip interrupts, current/earliest in-use addresses, TTU/QoS controls, VM aperture and context0 page-table fields, prefetch/vblank/flip/nominal timing parameters, cursor request settings, and HUBPREQ memory power controls.
- `HUBPRET5` return-path controls, memory power state, read-line configuration/readback, and interrupt fields.
- `CURSOR0_5` cursor surface, size, position, hot spot, stereo, memory power, and display metadata (`DMDATA`) fields.
- `DC_PERFMON12` perf-counter and perf-monitor control, state, interrupt/misc status, and counter value fields for the HUBP performance monitor slice.
- `HUBPXFC5` crossbar/frame-cache style control, XBUF read-base addresses, delay, underflow, slave VTG/scaler, and MPC configuration fields.

The second half switches to `DPP0` and related display pixel processor blocks:

- `DPP_TOP0` top-level DPP control, soft reset, CRC value/control, and host-read control.
- `CNVC_CFG0` and `CNVC_CUR0` input format conversion, alpha expansion, color keying, 2-bit alpha LUT, and cursor conversion fields.
- `DSCL0` scaler coefficient RAM, mode/tap controls, ratios, initial phases, recout/MPC dimensions, line-buffer configuration, autocalculation, overscan, memory power, output-buffer control, and OTG blanking pass-through fields.
- `CM0` color-management control, input CSC and gamut-remap matrices, biases, degamma LUT/RAM A/RAM B, blend-gamma LUT/RAM A/RAM B, HDR multiplier, CM memory power, de-alpha, coefficient format, and the start of shaper LUT/RAM A/RAM B region programming.

Each field is represented by `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros. Driver code pairs these values with register addresses from `dcn_2_0_0_offset.h` and uses generated register-helper tables to pack, update, and extract individual fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or persistent software objects in this chunk. The API surface is the generated macro namespace consumed by DCN component register tables.

The `HUBP5_DCHUBP_CNTL` fields expose blank enable, outstanding-request and disable status, VTG selection, TTU disable/mode, XRQ outstanding request status, timeout status/threshold/clear/interrupt enable, and underflow status/clear. `HUBP5_HUBP_CLK_CNTL` adds clock enable, clock-gating disable bits, live clock-on bits, and test clock selection. `HUBP5_HUBP_MEASURE_WIN_CTRL_DCFCLK` and `HUBP5_HUBP_MEASURE_WIN_CTRL_DPPCLK` define measurement-window enable, period, event start/stop selectors, mode/source selection, and perfmon integration fields.

The `HUBPREQ5_DCSURF_*` families define the plane fetch contract for a surface attached to HUBP5. They include luma/chroma pitch and metadata pitch, VMID selection, low/high 48-bit-style surface addresses for primary/secondary luma/chroma planes, low/high metadata addresses, DCC enable and 64-byte block indication bits, Trusted Memory Zone bits for surface and metadata, surface update locking, flip type, stereo flip mode, pending status, pending delay, minimum pending time, GSL enable/mask, triple buffering, queue control, frame pacing, and flip interrupt enable/status/clear fields.

The `HUBPREQ5_DCN_*`, `DC_VM_*`, and timing-parameter families cover memory request scheduling and translation. They describe TTU QoS watermarking, global TTU enable/disable, per-surface and per-cursor TTU min/max QoS and deadline values, VM system aperture low/high/default addresses, context0 protection-fault default and fault address fields, context0 page-table base/start/end fields, VM context enable/depth/range/protection-fault behavior, L1 TLB controls, blank offsets, destination dimensions, prefetch values, vblank delivery parameters, flip delivery parameters, nominal delivery parameters, per-line delivery parameters, reference-frequency-to-pixel-frequency conversion, and DRQ limit fields.

`HUBPREQ5_HUBPREQ_MEM_PWR_CTRL` and `HUBPREQ5_HUBPREQ_MEM_PWR_STATUS` expose request-side SRAM/LUT memory power-down, light-sleep, force, and state reporting bits. `HUBPRET5_HUBPRET_MEM_PWR_CTRL` and `HUBPRET5_HUBPRET_MEM_PWR_STATUS` do the same for the return path, while `HUBPRET5_HUBPRET_INTERRUPT` covers read-line/zero-delta interrupt enable, status, clear, and current-read-line event bits.

The `CURSOR0_5_*` fields define cursor mode, expansion mode, pitch, line chunking, enable, 2x magnification, address, size, position, hot spot, stereo force/shift/invert, cursor destination offset, cursor memory power, and DMData address, mode, repeat, size, QoS, done, software update, and software data fields.

`DC_PERFMON12_*` fields expose a DC performance counter/monitor programming surface: counter enable/reset, counter source select, clear, end-of-period behavior, state selection, test debug fields, stop/restart manual control, mode, auto start/stop, watermark selectors, event/occurrence/status/clear bits, and high/low counter value registers.

The `HUBPXFC5_*` fields describe XFC enable/format/swap controls, XBUF base addresses and pitch, refcycle/pipeline/slave-delay settings, underflow status/clear/force/interrupt bits, slave VTG totals/blanking, slave scaler recout dimensions, and MPC line timing.

`DPP_TOP0_*`, `CNVC_*`, and `DSCL0_*` fields are the front end of the DPP processing pipe. They include DPP enable/clock/reset/CRC controls; input surface pixel format, clamping, alpha, output floating-point selection, expansion mode, and color key ranges; scaler RAM tap selection/data, mode, tap counts, 2-tap controls, manual replication, horizontal/vertical ratios and init phases for luma/chroma/bottom fields, black offset, update/autocal controls, recout and MPC sizes, line-buffer format/memory, memory power state, and output-buffer bypass/clock-gate controls.

The `CM0_CM_*` fields define color pipeline programming. Matrix registers provide A/B banks for input CSC and gamut remap. LUT families include degamma, blend gamma, and shaper index/data/write-enable controls plus RAM A/RAM B piecewise-linear regions, start/end bases, slopes, per-channel B/G/R values, LUT offsets, and segment counts. The chunk ends in the middle of `CM0_CM_SHAPER_RAMB_REGION_10_11`: it includes the region comment and three shift macros, while the fourth shift and the corresponding masks continue at line 17350 in the next chunk.

## Control Flow

This chunk has no runtime control flow. It is preprocessor metadata used by DCN register helper code.

A typical runtime path is:

1. DCN 2.0 resource construction includes `dcn_2_0_0_offset.h` and `dcn_2_0_0_sh_mask.h`.
2. Resource tables populate per-component register, shift, and mask structures, such as `dcn_hubp2_registers`, `dcn_hubp2_shift`, `dcn_hubp2_mask`, `dcn2_dpp_shift`, and `dcn2_dpp_mask`.
3. Component code references logical field names through helper macros such as `HUBP_SF`, `TF_SF`, `IPP_SF`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and multi-field variants.
4. Those helpers use the shift/mask constants from this header to modify hardware registers for plane programming, flips, VM/TLB setup, cursor metadata, scaling, color conversion, gamma/shaper LUTs, CRC/perfmon diagnostics, interrupts, and power management.

The control-sensitive operations represented here include arming and observing page flips, locking surface updates, enabling or clearing flip and underflow interrupts, programming VM page-table/aperture behavior, controlling HUBP blanking/disable and TTU request scheduling, setting scaler coefficients and dimensions, choosing input conversion/color-management modes, writing gamma and shaper LUT entries, collecting DPP CRC/perf counters, and forcing or observing memory power states. The macros themselves do not encode ordering, access type, double-buffer timing, or legal value ranges.

## State And Persistence Behavior

The header stores no software state. It describes state held in DCN hardware registers.

The represented hardware state includes:

- Latched plane-fetch state: surface addresses, metadata addresses, pitch, VMID, DCC/TMZ attributes, surface queue configuration, current and earliest in-use addresses, flip lock/pending/delay state, triple-buffer and GSL state, and frame pacing.
- Request scheduling and VM state: TTU/QoS watermarks, per-surface and per-cursor QoS/deadline values, aperture/default/protection-fault addresses, page-table base/start/end, context0 control, L1 TLB configuration, prefetch/vblank/flip/nominal delivery budgets, and DRQ limits.
- Cursor and metadata state: cursor image address, dimensions, position, hot spot, stereo behavior, enable/mode bits, cursor memory power state, and DMData transport/software override state.
- Diagnostic and event state: HUBP underflow/timeout bits, flip interrupt status, HUBPRET read-line interrupt state, XFC underflow bits, perf counter state/value/status, DPP CRC controls and results, live clock-on bits, read-line values, and debug registers.
- Pixel-processing state: DPP reset/enable, input format and color keying, scaler coefficients and ratios, recout/MPC/line-buffer configuration, color matrices, degamma/blend/shaper LUTs and RAM regions, HDR multiplier, de-alpha, coefficient format, and CM/DSCL memory power state.

Persistence is hardware-defined. Programming fields generally persist while the display engine remains powered and configured; many values are reloaded during modeset, plane update, power-gating exit, suspend/resume, or ASIC reset. Status, interrupt, pending, underflow, timeout, done, and clear fields may be live read-only, sticky write-one-to-clear, self-clearing, or latched on a double-buffer boundary. This generated header does not distinguish those access classes, so consumers must rely on hardware sequencing code and register documentation.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.0 register-header set. `dcn_2_0_0_sh_mask.h` supplies bit layouts; `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h` supplies the matching register addresses.

Direct include points for the DCN 2.0 offset and mask headers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

The HUBP fields integrate most directly with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`, where six `hubp_regs` instances are built and shared `hubp_shift`/`hubp_mask` tables are initialized. The functional users are under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/`, especially the DCN10/DCN20-style HUBP code that programs surfaces, flips, VM, cursors, blanking, and underflow handling through `dcn_hubp2` register tables.

The DPP, CNVC, DSCL, and CM fields integrate with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.h` and `dcn20_dpp.c`, where `TF_SF` maps these field constants into `dcn2_dpp_shift` and `dcn2_dpp_mask`. Shared DPP code uses them for scaling, input CSC, gamut remap, degamma, blend gamma, shaper LUTs, DPP CRC, and memory power control. `CNVC_CFG0`/`CNVC_CUR0` fields are also part of the input pixel processor naming used from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_ipp.h`.

IRQ integration includes the HUBP5 flip interrupt source in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c` and later-generation IRQ services that retain the `HUBP5_FLIP_INTERRUPT` source ID naming. Diagnostic integration includes DPP CRC register tables in HW sequencer/resource code and DC perfmon fields consumed by debug/performance tooling.

Although the repository path is under a local `ceph-client` tree, this file is AMDGPU display-controller hardware metadata. It has no Ceph protocol, filesystem, or distributed-storage behavior.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong shift or mask can compile cleanly while updating the wrong bits, failing to update intended bits, or corrupting adjacent fields during read/modify/write operations.

High-risk HUBP/HUBPREQ fields include surface address high/low words, metadata address high/low words, pitch and metadata pitch, VMID, DCC/TMZ controls, flip pending/lock/mode/status, triple-buffer and GSL bits, TTU/QoS deadlines, VM aperture/page-table/protection-fault controls, L1 TLB configuration, vblank/flip/prefetch delivery timing, and underflow/timeout clear bits. Mistakes here can cause memory faults, secure-surface exposure, wrong frame fetches, stale page flips, missed flip interrupts, underflows, display corruption, hangs during modeset, or page-table faults isolated to one pipe.

High-risk DPP/DSCL/CM fields include scaler tap/phase/ratio values, coefficient RAM indexing/data enable bits, line-buffer memory config, recout/MPC dimensions, CNVC format/alpha expansion, CSC and gamut matrices, gamma/shaper LUT index/data/write-enable bits, RAM region offsets/segment counts, memory power force/state fields, DPP reset/enable, and CRC controls. Errors here can cause incorrect colors, broken HDR/gamma output, bad scaling, clipped or shifted images, CRC mismatches, blank output, or power-management failures.

Generated instance suffixes are a copy-generation risk. This chunk is specific to HUBP instance 5 and DPP instance 0; most register layouts are structurally similar to other instances, but a wrong `5`, `12`, or `0` suffix can affect only systems using the affected pipe or diagnostic counter.

Several fields represent status, interrupt clear, event force, memory power state, or self-clearing trigger bits. The header does not encode read-only/write-one-to-clear semantics. Consumers must avoid treating status bits as ordinary writable state or clearing sticky events while enabling interrupts.

The line range begins after the `HUBP5_DCHUBP_CNTL__HUBP_TIMEOUT_STATUS_MASK` macro was already emitted in the previous chunk, so this chunk contains the remaining `HUBP5_DCHUBP_CNTL` masks before `HUBP5_HUBP_CLK_CNTL`. It also ends mid-register in `CM0_CM_SHAPER_RAMB_REGION_10_11`, before the `REGION11_NUM_SEGMENTS` shift and all masks for that register. The final merged per-file report should treat both as chunk boundaries, not missing definitions.

## Test Signals

Useful validation signals are compile-time generated-header checks plus display hardware behavior:

- AMDGPU/DCN 2.0 builds should compile all users of `dcn_2_0_0_sh_mask.h`, especially DCN20 resource, IRQ, GPIO, clock-manager, DMUB, GMC, HUBP, IPP, and DPP code.
- Register-generation validation should compare every `*_MASK` and `*__SHIFT` pair in this chunk against AMD's source register database and the corresponding addresses in `dcn_2_0_0_offset.h`.
- Multi-pipe modeset and plane-update tests should exercise HUBP5 specifically, including primary/secondary planes, DCC-enabled surfaces, metadata surfaces, TMZ surfaces, cursor planes, page flips, triple buffering, and GSL-enabled flips.
- VM/IOMMU tests should validate VMID, aperture, page-table, protection-fault, L1 TLB, and default-address behavior under valid mappings, invalid mappings, suspend/resume, and repeated modesets.
- Flip IRQ and event tests should check `HUBP5` flip pending/status/clear, underflow clear/status, timeout status/clear, HUBPRET read-line interrupts, and XFC underflow interrupt behavior.
- Bandwidth and timing tests should observe stable TTU/QoS, prefetch, vblank, flip, nominal, per-line, DRQ, and frame-pacing behavior across high-resolution, high-refresh, chroma, DCC, and cursor-heavy workloads.
- DPP tests should verify input format conversion, alpha/keying, scaler ratios/coefs, recout/MPC dimensions, line-buffer configuration, DPP CRC output, and DSCL/CM memory power state transitions.
- Color-management tests should exercise input CSC, gamut remap, degamma, blend gamma, HDR multiplier, de-alpha, coefficient formats, shaper LUT programming, RAM A/B bank selection, and region offset/segment programming.
- Runtime power-management, suspend/resume, hotplug, and repeated atomic update stress should not leave HUBP/DPP memory power forced incorrectly, clocks gated unexpectedly, update locks stuck, interrupts uncleared, or LUT banks partially programmed.

Regression symptoms from bad constants include blank or unstable display output, page flips that never complete, missed vblank/flip interrupts, GPU VM faults during scanout, HUBP underflows or timeouts, incorrect cursor position or metadata transport, XFC underflows, wrong scaling, bad colors/HDR/gamma, CRC mismatches, and failures isolated to HUBP5 or DPP0.

## Cross-Chunk Notes

Earlier chunks define preceding DCN 2.0 register families and the beginning of the HUBP5/HUBPREQ5 sequence, including the first part of `HUBP5_DCHUBP_CNTL`. This chunk continues through the remaining HUBP5/HUBPREQ5/HUBPRET5/CURSOR0_5/perfmon/XFC fields and then covers DPP0/CNVC/DSCL/CM0 through the start of `CM0_CM_SHAPER_RAMB_REGION_10_11`. The next chunk continues that shaper RAMB register and the remaining color-management/output-pixel-processing register mask definitions. The final per-file merge should describe the whole header as a generated DCN 2.0 hardware register layout contract, not as algorithmic code.

### subset-b-001617: lines 17350-19866

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 17350-19866

## Purpose

This chunk is part of AMDGPU's generated DCN 2.0 register field shift/mask header. It contains no executable C logic; it publishes compile-time bit layout constants for DCN display pipeline registers. Each register field is represented as paired preprocessor macros: `REGISTER__FIELD__SHIFT` gives the field's low bit position, and `REGISTER__FIELD_MASK` gives the already-positioned bit mask used by AMD display register helpers.

The range covers the tail of DPP0 color-management fields, a DPP0 performance-monitor block, most of DPP1's DPP/CNVC/DSCL/CM field layout, and the beginning of DPP2 scaler fields:

- Tail of `CM0` shaper RAMB region programming, memory power controls/status, 3D LUT programming, output normalization/offset, and CM test-debug registers.
- `DC_PERFMON13` performance-counter and performance-monitor registers associated with the DPP0 display pipeline.
- `DPP_TOP1` top-level DPP1 control, soft reset, CRC value/control, and host-read controls.
- `CNVC_CFG1` and `CNVC_CUR1` input/cursor formatter fields for DPP1, including surface pixel format, format conversion, FP bias/scale, color keying, alpha LUT, and cursor color/control.
- `DSCL1` scaler fields for DPP1, including coefficient RAM programming, scaler mode, tap counts, ratios, initial phases, overscan/recout/MPC sizes, line-buffer controls, memory power controls/status, and output-buffer controls.
- `CM1` color-management fields for DPP1, including input CSC, gamut remap, bias, degamma, blend gamma, shaper LUT, HDR multiplier, memory power controls/status, de-alpha, coefficient format, 3D LUT, and test-debug registers.
- `DC_PERFMON14` performance-counter and performance-monitor registers associated with DPP1.
- Start of `DPP_TOP2`, `CNVC_CFG2`, `CNVC_CUR2`, and `DSCL2` fields for the DPP2 pipeline, ending at the first two shifts of `DSCL2_DSCL_MEM_PWR_CTRL`.

Although this repository path is nested under a `ceph-client` source tree, this chunk is AMD GPU display hardware metadata. It has no Ceph filesystem protocol behavior, no distributed filesystem state, and no storage persistence semantics.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or global objects in this chunk. The API surface is the generated macro namespace consumed by AMD display code.

Important macro families include:

- `CM0_CM_SHAPER_RAMB_REGION_*`, `CM0_CM_MEM_PWR_CTRL2`, `CM0_CM_MEM_PWR_STATUS2`, `CM0_CM_3DLUT_*`, and `CM0_CM_TEST_DEBUG_*`: finish DPP0 color-management shaper/3D-LUT/test-debug field metadata.
- `DC_PERFMON13_*` and `DC_PERFMON14_*`: performance counter control, counter state, monitor control, captured counter values, high/low readback, and interrupt/status/mask fields.
- `DPP_TOP1_*` and `DPP_TOP2_*`: DPP enable/control, soft reset, CRC value/control, and host-read control fields for pipeline instances 1 and 2.
- `CNVC_CFG1_*` and `CNVC_CFG2_*`: input formatter and converter fields, including `CNVC_SURFACE_PIXEL_FORMAT`, `CNVC_BYPASS`, alpha enable, expansion mode, floating-point conversion bias/scale, color key compare values, and alpha lookup table fields.
- `CNVC_CUR1_*` and `CNVC_CUR2_*`: cursor enable, expansion, pixel-invert, ROM enable, cursor mode, alpha modulation, update-pending, cursor color, and floating-point cursor scale/bias fields.
- `DSCL1_*` and `DSCL2_*`: scaler coefficient RAM select/data, scaler mode, tap control, 2-tap sharpness, manual replication, luma/chroma horizontal and vertical ratios, filter init values, black offset, update/autocal, overscan, output rectangle, MPC size, line-buffer data format/memory partitioning, vertical counters, and memory power controls.
- `CM1_*`: the largest section in the chunk. It describes DPP1 color-management programming for input CSC matrices, gamut remap matrices, bias registers, degamma LUT, blend-gamma LUT, shaper LUT, HDR multiplier coefficients, shared/shaper/3D-LUT memory power controls, coefficient format, de-alpha, and test-debug access.

The macro names are instance-specific (`CM1_`, `DSCL1_`, `CNVC_CFG1_`, etc.), but many runtime consumers store instance-neutral field names in register tables. For example, DPP setup code builds per-instance register addresses with `SRI(..., CM, id)` and uses field shifts/masks generated from instance 0 names through macros such as `TF_REG_LIST_SH_MASK_DCN20(__SHIFT)` and `TF_REG_LIST_SH_MASK_DCN20(_MASK)`. This works because the repeated DPP instances share the same bit layout even when their register addresses differ.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior is introduced by consumers that combine these field constants with register addresses from `dcn_2_0_0_offset.h` and register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`.

A typical runtime path is:

1. DCN 2.0 resource setup creates per-pipeline register tables for DPP, IPP/CNVC, DSCL, and CM blocks.
2. The register table selects the correct instance address, such as `CM1_CM_3DLUT_MODE` or `DSCL1_SCL_MODE`, using generated offset macros.
3. Driver code uses an instance-neutral field name, such as `CM_3DLUT_MODE`, `SCL_H_SCALE_RATIO`, `CNVC_SURFACE_PIXEL_FORMAT`, or `LUT_MEM_PWR_FORCE`.
4. Register helper macros insert or extract the value using the generated `*_SHIFT` and `*_MASK` constants from this header.
5. Hardware applies the write according to the register's own timing, latch, self-clear, or power-gating semantics.

Control-sensitive operations represented by this chunk include scaler coefficient RAM updates, scaler mode transitions, line-buffer and output-buffer power control, DPP soft reset, CRC capture, host-read access, cursor format/color updates, CNVC bypass and pixel format changes, color-keying, gamma/shaper/3D-LUT programming, performance-counter start/stop/restart/interrupt handling, and color pipeline test-debug access. The macros do not enforce sequencing or valid ranges.

## State And Persistence Behavior

The file stores no software state and has no persistence mechanism. It describes bit positions for state held in display hardware registers.

The represented hardware state includes:

- Color-management programming: CSC and gamut-remap matrices, bias values, degamma/blend-gamma/shaper region descriptors, LUT indices/data/write masks, 3D-LUT mode/index/data/read-write control, 3D-LUT output normalization, and output scale/offset values.
- Pixel and cursor formatting: CNVC surface format, alpha handling, expansion/bypass, FP conversion scale/bias, color-key compare values, cursor enable/mode/color/scale/bias, and update-pending status.
- Scaler state: coefficient RAM address/data, tap counts, luma/chroma scale ratios and initial phases, 2-tap sharpness, manual replication, boundary/autocal mode, overscan, recout/MPC size, black offset, line-buffer format/partitioning, vertical counters, and update-pending status.
- Power and reset state: DPP soft reset bits, CM shared/shaper/3D-LUT memory power force/disable/status, DSCL LUT/line-buffer memory power force/disable/status, and output-buffer memory power controls.
- Diagnostics and telemetry: DPP CRC values/control, CM test-debug index/data, performance-counter event selection, active/run/interrupt bits, counter readbacks, and counter compare/status fields.

Persistence is hardware-defined. Some fields are latched programming values that survive until reprogrammed or reset, some are live status bits, some are sticky interrupt/status bits that require explicit acknowledgement or clearing, and some are self-clearing request/update bits. Values may be changed by modesets, plane updates, cursor updates, color-management updates, power management, hotplug recovery, suspend/resume, firmware/DMUB involvement, or ASIC reset. The generated header does not encode read-only, write-one-to-clear, self-clearing, or safe-update rules.

## Dependencies And Integration Points

The companion address definitions are in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h`; this chunk supplies field layout inside those addresses. Consumers include both headers together.

Direct include points for `dcn_2_0_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

The most relevant integration point for this chunk is the DPP stack. `dcn20_resource.c` builds `tf_regs`, `tf_shift`, and `tf_mask` tables from `TF_REG_LIST_DCN20`, `TF_REG_LIST_SH_MASK_DCN20(__SHIFT)`, and `TF_REG_LIST_SH_MASK_DCN20(_MASK)`. Those tables are consumed by DPP code under `display/dc/dpp/dcn10` and `display/dc/dpp/dcn20` for color-management, CNVC, DSCL, memory-power, and scaler programming.

The IPP/CNVC integration uses register-list and field-list macros from `dcn10_ipp.h`, including `IPP_REG_LIST_DCN20` and `IPP_MASK_SH_LIST_DCN20`. DSCL fields are used by scaler code in `dcn10_dpp_dscl.c` for coefficient loading, scale ratio/init programming, tap setup, autocal, black offset, line-buffer handling, and memory-power waits. CM fields are used by `dcn10_dpp_cm.c`, `dcn10_dpp.c`, and `dcn20_dpp.c` for color matrices, gamma/shaper programming, 3D LUT status/configuration, and DPP power setup.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong shift or mask can compile cleanly while updating the wrong bits, failing to update the intended bits, or corrupting adjacent fields during read-modify-write operations.

High-risk fields in this chunk include:

- Scaler coefficient RAM select/data, tap counts, scale ratios, initial phases, and mode fields. Bad values can cause distorted scaling, chroma misalignment, underflow/overflow symptoms, or blank output.
- Memory power force/disable/status fields for CM, DSCL, line buffer, LUT, and output buffer memories. Incorrect constants can leave memories powered down while being accessed, prevent expected power savings, or break resume/modeset sequences that wait on status bits.
- CNVC pixel format, bypass, expansion, alpha, and FP scale/bias fields. Errors can produce wrong colors, alpha handling bugs, bad cursor format, or incorrect fixed/floating conversion.
- CM LUT, shaper, 3D-LUT, CSC, gamut-remap, bias, and coefficient-format fields. Errors can produce color regressions, bad HDR/SDR transforms, LUT upload failures, or incorrect readback/status.
- DPP soft reset, CRC, host-read, test-debug, and perfmon fields. Errors can break diagnostics, cause stuck reset states, corrupt debug access, or make performance counters report misleading data.

The generated instance pattern is another risk. DPP0, DPP1, and DPP2 register fields are largely repeated with different prefixes, while DPP runtime tables often use instance 0 field definitions as canonical masks/shifts for every instance. If a later instance ever diverged, that assumption would fail outside the C type system.

This chunk is also bounded in the middle of repeated generated blocks. It starts in the middle of `CM0_CM_SHAPER_RAMB_REGION_10_11` and ends after only the first two `DSCL2_DSCL_MEM_PWR_CTRL` shift definitions. Those are chunking artifacts for research generation, not evidence that the source register block is incomplete.

## Test Signals

Useful validation signals are mostly compile-time checks plus display hardware behavior:

- Kernel builds for DCN 2.0 display paths should compile all generated field names referenced by DPP, IPP, DSCL, CM, IRQ, GPIO, clock, DMUB, and GMC code.
- Generated-header validation should compare every `*_MASK` and `*__SHIFT` pair in this line range against AMD's register database and the matching offsets in `dcn_2_0_0_offset.h`.
- Modeset and plane-scaling tests should exercise DPP1 and DPP2 paths with no scaling, luma/chroma scaling, 4:4:4 and 4:2:0 formats, different tap counts, underscan/overscan, and cursor updates.
- Color-management tests should upload and switch degamma, blend-gamma, shaper, 3D-LUT, CSC, gamut-remap, HDR multiplier, and bias programming while checking expected CRCs or visual output.
- Power-management tests should cover blanking, idle, hotplug, suspend/resume, and repeated modesets while checking that CM/DSCL memory status fields reach expected states and do not time out.
- Perfmon and CRC/debug tests should verify that `DC_PERFMON13`, `DC_PERFMON14`, DPP CRC, and CM test-debug fields produce plausible counters/readbacks and do not target the wrong instance.
- Regression symptoms from bad constants include blank or flickering displays, wrong color conversion, cursor corruption, scaler artifacts, failed LUT programming, stuck power-gating waits, resume failures, bad CRCs, and misleading performance-counter values.

## Cross-Chunk Notes

Earlier chunks of `dcn_2_0_0_sh_mask.h` define the preceding DCN 2.0 display register field families and the start of the DPP0 color-management section. Later chunks complete `DSCL2_DSCL_MEM_PWR_CTRL`, continue through the rest of the DPP2 scaler/color-management blocks, and cover subsequent DCN 2.0 register families. The final per-file report should treat this source as one generated hardware register-layout contract rather than independent algorithmic code.

### subset-b-001618: lines 19867-22386

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 19867-22386

## Purpose

This chunk is part of AMDGPU's generated DCN 2.0.0 register field header. It contains C preprocessor `__SHIFT` and `_MASK` constants for display pipe and plane (DPP) hardware fields, specifically the end of DPP2 scaler memory/output-buffer fields, most of the DPP2 color-management block, DPP2 perfmon fields, and the beginning of DPP3 top/config/cursor/scaler/color-management fields.

There are no functions, structs, enums, global variables, or executable statements in this range. The exported surface is a large macro namespace used by DCN display code to build typed register shift/mask tables. Runtime code combines these field constants with paired register-offset constants from `dcn_2_0_0_offset.h` and then performs MMIO through DC register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WAIT`, and indexed debug helpers.

Although this repository path is under a `ceph-client` source mirror, the chunk is AMD DCN display-driver hardware metadata and has no Ceph filesystem behavior.

## Important APIs, Types, And Macros

The important interface is the generated field macro set. Each hardware field normally has two constants:

- `REGISTER__FIELD__SHIFT`: bit position used to align a field value.
- `REGISTER__FIELD_MASK`: bit mask used to isolate or update that field.

The chunk starts mid-register at `DSCL2_DSCL_MEM_PWR_CTRL__LB_G1_MEM_PWR_FORCE__SHIFT`, so the first register family is completed from the previous chunk. The main covered families are:

- `DSCL2_DSCL_MEM_PWR_CTRL`, `DSCL2_DSCL_MEM_PWR_STATUS`, `DSCL2_OBUF_CONTROL`, and `DSCL2_OBUF_MEM_PWR_CTRL`: DPP2 scaler LUT/line-buffer memory power control and status, output-buffer bypass/full-buffer/half-width/hold-count control, and OBUF memory power force/disable/mode/state fields.
- `CM2_CM_CONTROL` and `CM2_CM_ICSC_*`: DPP2 color-management bypass/update status and input color-space conversion mode plus A/B coefficient banks. The coefficient registers pack two signed/fixed-point coefficients per register, for example `CM_ICSC_C11` and `CM_ICSC_C12` in the low/high 16-bit halves.
- `CM2_CM_GAMUT_REMAP_*`: DPP2 gamut-remap control and A/B coefficient banks with the same paired 16-bit coefficient layout as ICSC.
- `CM2_CM_BIAS_*`, `CM2_CM_DEALPHA`, `CM2_CM_COEF_FORMAT`, and `CM2_CM_HDR_MULT_COEF`: DPP2 color bias, coefficient-format selection, dealpha/additive-blending controls, and HDR multiplier coefficient fields.
- `CM2_CM_DGAM_*`: DPP2 degamma LUT control, LUT index/data ports, write-enable/mask/status fields, and RAM A/RAM B piecewise-linear region programming. RAM programming fields include per-channel start values and start segments, linear slopes, region end points, end slopes/bases, and region-pair LUT offset/segment-count descriptors.
- `CM2_CM_BLNDGAM_*`: DPP2 blend/output-gamma LUT control and RAM A/RAM B programming. It mirrors the DGAM shape but has a larger region set, running through `REGION_32_33` for both RAM banks.
- `CM2_CM_SHAPER_*`: DPP2 shaper LUT control, offset/scale, LUT index/data, write-enable/status, and RAM A/RAM B region descriptors through `REGION_32_33`.
- `CM2_CM_MEM_PWR_CTRL`, `CM2_CM_MEM_PWR_STATUS`, `CM2_CM_MEM_PWR_CTRL2`, and `CM2_CM_MEM_PWR_STATUS2`: DPP2 shared, degamma, blend-gamma, shaper, 3D LUT, and 3D LUT RAM-slice memory power force/disable/mode/status fields.
- `CM2_CM_3DLUT_*`: DPP2 3D LUT mode, index, data, 30-bit data access, read/write control, normalization factor, and per-channel output offsets.
- `CM2_CM_TEST_DEBUG_INDEX` and `CM2_CM_TEST_DEBUG_DATA`: indexed CM debug/status accessors. DCN color code uses this path to read live coefficient-bank selection and config status that may not be represented by ordinary direct reads.
- `DC_PERFMON15_*`: DPP2/DC perfmon 15 counter control, state, perfmon control, latched/current values, and interrupt/misc fields.
- `DPP_TOP3_*`: DPP3 top-level clock enable, clock-gate-disable, test clock select, soft reset, CRC values/control, and host-read control fields.
- `CNVC_CFG3_*` and `CNVC_CUR3_*`: DPP3 converter/config fields for surface pixel format, alpha-plane enable, format conversion/bypass/expansion/clamping, fixed-point bias/scale values, color-keyer controls/ranges, 2-bit alpha LUT, and cursor mode/color/expansion/enable fields.
- `DSCL3_*`: beginning of DPP3 scaler fields for coefficient RAM tap selection/data, scaler mode/taps, DSCL control, 2-tap control, manual replicate, horizontal/vertical luma and chroma ratios/initial phases, black offset, update/autocal, overscan, OTG blanking, recout/MPC sizes, line-buffer format/memory/v-counter, DSCL memory power, and OBUF control/power.
- `CM3_CM_CONTROL` through `CM3_CM_BLNDGAM_RAMA_REGION_30_31`: beginning of DPP3 color-management fields. The covered range includes control, ICSC A/B matrices, gamut-remap A/B matrices, bias, degamma RAM A/B setup, and blend-gamma RAM A setup through `REGION_30_31`. The next chunk continues the DPP3 CM blend-gamma table.

The macros in this file are consumed indirectly by tables such as `tf_shift`, `tf_mask`, `ipp_shift`, and `ipp_mask`. In `dcn20_dpp.h`, macros like `TF_REG_LIST_SH_MASK_DCN20_COMMON`, `TF_REG_LIST_SH_MASK_DCN20_UPDATED`, and related register-list macros select many of the `CM*_CM_BLNDGAM_*`, `CM*_CM_3DLUT_*`, `CM*_CM_SHAPER_*`, `DSCL*_DSCL_MEM_PWR_CTRL`, `CNVC_CFG*_COLOR_KEYER_*`, and `CNVC_CFG*_ALPHA_2BIT_LUT` fields represented in this chunk. In `dcn10_ipp.h`, `IPP_MASK_SH_LIST_DCN` uses `CNVC_CFG0_*` and `CNVC_CUR0_*` fields with the same generated naming scheme for per-instance CNVC/IPP programming.

## Control Flow

This header has no runtime control flow. It changes driver behavior by determining which bit positions and masks generated register helpers use when updating hardware fields.

A typical DCN20 DPP path is:

1. `dcn20_resource.c` creates DPP/IPP instances with per-instance register tables and the generated shift/mask tables.
2. A high-level display operation calls a DPP or IPP function through `struct dpp_funcs` or `struct ipp_funcs`.
3. That function uses register macros such as `REG_SET`, `REG_SET_2`, `REG_UPDATE`, `REG_GET`, `REG_GET_2`, `REG_WAIT`, or `IX_REG_GET`.
4. The helper looks up the register offset and the field shift/mask, then performs the MMIO read/modify/write or indexed debug read.

Representative flows tied to this chunk include:

- `dpp20_read_state()` in `dcn20_dpp.c` reads `DPP_CONTROL.DPP_CLOCK_ENABLE`, `CM_DGAM_CONTROL.CM_DGAM_LUT_MODE`, `CM_SHAPER_CONTROL.CM_SHAPER_LUT_MODE`, `CM_3DLUT_READ_WRITE_CONTROL.CM_3DLUT_CONFIG_STATUS`/`CM_3DLUT_30BIT_EN`, `CM_3DLUT_MODE.CM_3DLUT_SIZE`, and `CM_BLNDGAM_LUT_WRITE_EN_MASK.CM_BLNDGAM_CONFIG_STATUS`.
- `dpp2_power_on_obuf()` updates `CM_MEM_PWR_CTRL.SHARED_MEM_PWR_DIS`, `OBUF_MEM_PWR_CTRL.OBUF_MEM_PWR_FORCE`, and `DSCL_MEM_PWR_CTRL.LUT_MEM_PWR_FORCE` to control DPP memory and OBUF/scaler memory power.
- `dpp1_power_on_dscl()` in the shared DSCL implementation uses `DSCL_MEM_PWR_CTRL.LUT_MEM_PWR_FORCE` and waits on `DSCL_MEM_PWR_STATUS.LUT_MEM_PWR_STATE`; the DPP2 and DPP3 field definitions in this chunk provide the instance-specific bit layout.
- `dpp2_cnv_setup()` programs `FORMAT_CONTROL` and `CNVC_SURFACE_PIXEL_FORMAT` fields to configure conversion bypass, expansion mode, clamp behavior, alpha enable, and pixel format.
- `dpp2_program_input_csc()` writes `CM_ICSC_CONTROL` and the `CM_ICSC_*` coefficient fields, alternating A/B coefficient banks after reading current selection via `CM_TEST_DEBUG_INDEX`/`CM_TEST_DEBUG_DATA`.
- `read_gamut_remap()` and `dpp2_cm_get_gamut_remap()` read gamut-remap mode through CM test/debug fields and then read either the A or B gamut-remap coefficient bank.
- The blend-gamma, degamma, shaper, and 3D LUT programming routines in `dcn20_dpp_cm.c` use the RAM start/slope/end/region/index/data/write-enable fields described by this chunk to build piecewise-linear transfer functions and 3D LUT state.

## State And Persistence Behavior

The header stores no software state. The state represented by its macros lives in DCN hardware registers inside DPP2, DPP3, DSCL, CNVC, CM, OBUF, and perfmon blocks.

The hardware state covered by this chunk includes:

- DPP clock enable, clock-gating disable, dynamic gating disable, soft reset, CRC, and host-read behavior.
- DSCL scaler mode, luma/chroma tap counts, ratios, initial phases, overscan, recout size, MPC size, line-buffer layout, vertical counters, coefficient RAM access, and scaler/line-buffer memory power.
- OBUF bypass/full-buffer/half-width/hold-count settings and OBUF memory power state.
- CNVC surface pixel format, alpha-plane enable, format conversion, expansion/clamp mode, fixed-point scale/bias, color-keying ranges, 2-bit alpha LUT values, and cursor mode/color/enable state.
- CM bypass/update status, input CSC coefficients, gamut-remap coefficients, color bias, degamma LUT state, blend/output-gamma LUT state, shaper LUT state, 3D LUT state, HDR multiplier, dealpha/additive blending, CM memory power state, and debug/status index-data reads.
- Perfmon counter configuration, counter state, current/latched values, high/low data, and interrupt/misc state for perfmon block 15.

Persistence is hardware-defined. Some fields are ordinary sticky configuration bits that remain until another modeset, color update, power-management operation, suspend/resume path, display core reset, or GPU reset changes them. LUT RAM contents and coefficient banks are programmed through index/data windows and can be double-buffered or selected by A/B bank mode fields. Status fields such as memory-power state, update-pending/config-status, v-counter, CRC, and perfmon values are readback/counter/status state rather than durable configuration. The header does not encode which fields are read-only, write-one-to-clear, self-clearing, double-buffered, or timing-sensitive; that sequencing is handled in the DCN DPP/IPP/CM/DSCL code and firmware/hardware specifications.

## Dependencies And Integration Points

The file's direct dependency is only the C preprocessor. Practical integration depends on the generated AMD register-header set:

- `dcn_2_0_0_offset.h` provides the matching register offsets and base-index information.
- `dcn_2_0_0_sh_mask.h` provides the field shifts and masks in this chunk.
- Other generated DCN headers provide enum values and neighboring ASIC-version definitions.
- DC register-access macros in the display driver combine offsets, masks, and shifts for typed MMIO access.

Important integration points in the local tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.h`: declares DCN20 DPP register lists and field-list macros that consume many CM, CNVC, DSCL, OBUF, 3D LUT, shaper, and blend-gamma fields represented here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.c`: reads DPP state, controls DPP/DSCL/OBUF memory power, and programs CNVC setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp_cm.c`: programs input CSC, gamut remap, degamma, blend gamma, shaper, 3D LUT, CM bias, dealpha, and related color state.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp_dscl.c`: shared DSCL scaler code that uses DSCL memory power/status and line-buffer/scaler fields across DCN DPP versions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_ipp.h` and `dcn10_ipp.c`: converter/cursor field tables and IPP setup paths for CNVC/IPP state.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`: constructs DPP and IPP instances with generated register, shift, and mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dpp.h`: documents the DPP pipeline as CNVC, DSCL, CM, OBUF, and DPB modules and defines the high-level DPP state and function interface that the generated fields support.

The chunk is source-tree-aligned with a large generated hardware register map. It should be reconciled with adjacent chunks rather than treated as a standalone module because it starts in the middle of `DSCL2_DSCL_MEM_PWR_CTRL` and ends in the middle of the `CM3_CM_BLNDGAM_RAMA_*` region table.

## Risks And Edge Cases

The main risk is silent bitfield corruption. A wrong shift or mask can compile cleanly while causing register helpers to update the wrong bits within the right register. For display hardware, that can manifest as blank planes, bad scaling, wrong colors, cursor artifacts, unstable clocks/power state, or intermittent failures on only one DPP instance.

High-impact areas in this chunk are:

- Memory power fields: incorrect `DSCL*_DSCL_MEM_PWR_CTRL`, `DSCL*_DSCL_MEM_PWR_STATUS`, `OBUF_MEM_PWR_CTRL`, or `CM*_CM_MEM_PWR_CTRL*` fields can make power-on/off waits time out, leave LUT/line-buffer/OBUF/CM memory powered down while in use, or block low-power optimizations.
- LUT RAM programming fields: degamma, blend-gamma, shaper, and 3D LUT programming depends on index/data windows, write-enable masks, A/B bank selection, region offsets, segment counts, start values, slopes, and end bases. A mask width error can corrupt transfer functions even when the selected register address is correct.
- Double-buffered coefficient banks: ICSC and gamut-remap A/B matrix fields are paired with debug/status selection reads. If A/B field masks or debug fields are wrong, updates may target the wrong bank or read back stale selection, causing frame-boundary color changes to fail.
- CNVC format fields: bad pixel-format, alpha enable, expansion, clamp, scale/bias, color-keyer, or 2-bit alpha LUT masks can break primary plane interpretation or blending without producing a build failure.
- DSCL scaler fields: wrong tap count, ratio, initial phase, viewport/recout, line-buffer, or coefficient RAM fields can produce scaling artifacts, underflow symptoms, or failures only for chroma/4:2:0 paths.
- DPP3 instance fields: this chunk switches from DPP2 to DPP3. Instance-numbered generated names must remain consistent with offset tables and DPP instance construction; copy/paste or generator drift could make one pipe differ from another.
- Cross-chunk boundaries: the start lacks the first `DSCL2_DSCL_MEM_PWR_CTRL` field lines, and the end stops at `CM3_CM_BLNDGAM_RAMA_REGION_30_31`. Merge/reconciliation should join this with chunks 8 and 10 before drawing final per-file conclusions.

Because generated mask headers are often included indirectly, removing or renaming an apparently unused field can still break macro expansion in versioned register-list code. Some debug, status, and perfmon fields may be used only by diagnostics, validation, or future code paths.

## Test Signals

Useful validation signals are a mix of build-time checks, register-map comparison, and display behavior:

- Build AMDGPU DCN20 paths with display enabled. This catches missing or renamed field macros in `dcn20_dpp.h`, `dcn20_dpp.c`, `dcn20_dpp_cm.c`, shared DSCL code, IPP code, and resource construction.
- Generate or compare the `dcn_2_0_0_offset.h` and `dcn_2_0_0_sh_mask.h` pair against AMD's source register database. Field masks should match their documented widths and should not overlap unexpectedly within the same register.
- Exercise modesets on all DPP instances that exist on the target ASIC. DPP2 and DPP3 coverage is important because this chunk spans both instance groups.
- Run plane format tests for ARGB/RGB/FP formats, alpha-plane enable, 2-bit alpha LUT, format expansion, clamp, color keying, and cursor color/enable behavior.
- Run scaler tests covering bypass, luma/chroma scaling, 4:2:0 paths, horizontal and vertical ratios, tap counts, overscan, line-buffer partitioning, and recout/MPC sizing.
- Run color-management tests for ICSC, gamut remap, degamma, blend/output gamma, shaper, 3D LUT, HDR multiplier, CM bias, and dealpha/additive blending. Visual CRC or hardware CRC comparisons should catch many bitfield errors.
- Run suspend/resume, display power-gating, and low-power-memory tests while verifying `REG_WAIT` paths for DSCL/CM/OBUF memory power status do not time out.
- Read DPP state through debugfs or driver instrumentation after programming color/scaler state and compare readback with expected `dcn_dpp_state` and `dcn_dpp_reg_state` values.
- Exercise perfmon block 15 counter programming and readback to verify counter control/state/value fields are mapped to the intended perfmon block.

Regression symptoms from bad constants include build failures in generated register-list expansion, `REG_WAIT` timeouts, black or corrupted planes, incorrect color transforms, banding or gamma errors, broken 3D LUT programming, cursor color/enable artifacts, scaling artifacts, underflow, CRC mismatch, a single DPP pipe failing, or power-management failures during modeset and resume.

## Cross-Chunk Notes

This is chunk 9 of 28 for `dcn_2_0_0_sh_mask.h`. It begins inside the DPP2 DSCL memory-power register family, completes DPP2 CM and related DPP2 perfmon fields, begins DPP3 top/CNVC/DSCL/CM fields, and ends inside the DPP3 blend-gamma RAM A region table. The final per-file research document should merge this with the adjacent chunks so the repeated DPP0-DPPn generated patterns and the split register families are described as one continuous DCN 2.0.0 mask/shift map.

### subset-b-001619: lines 22387-24908

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 22387-24908

## Scope

This chunk covers 2,522 lines from the generated DCN 2.0 register shift/mask header. It begins inside the `CM3_CM_BLNDGAM_RAMA` region table at `REGION_30_31`, completes the `CM3_CM_BLNDGAM_RAMA_REGION_32_33` and full `CM3_CM_BLNDGAM_RAMB` region/programming definitions, then covers the remaining DPP3 color-management blocks, `DC_PERFMON16`, MPCC0 through MPCC7 compositor masks, MPC global/update/output masks, and the start of the `MPCC_OGAM0` output-gamma block through `MPCC_OGAM_RAMB_REGION_30_31`.

The source is not executable C. It exports preprocessor constants of the form `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` for bitfield packing and extraction. These macros pair with address definitions in `dcn_2_0_0_offset.h` and are consumed by AMD display register helper layers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `TF_SF`, `SF`, `SRI`, and `SRII`.

## Purpose

The chunk describes register bit layouts for DCN 2.0 display color processing, composition, monitoring, and output-gamma control:

- `CM3_CM_BLNDGAM_*` fields define the DPP3 blend-gamma PWL LUT RAM A/B programming surface: per-channel start points, start segments, linear slopes, end points, end slopes/bases, and 34 exponential regions encoded two regions per register.
- `CM3_CM_HDR_MULT_COEF`, `CM3_CM_MEM_PWR_*`, `CM3_CM_DEALPHA`, and `CM3_CM_COEF_FORMAT` describe DPP color-management multiplier, memory power, alpha handling, and coefficient format controls.
- `CM3_CM_SHAPER_*` provides another double-buffered PWL LUT surface around the 3D LUT path, including offsets/scales, LUT index/data/write enables, RAM A/B start/end/region maps, and mode/configuration status.
- `CM3_CM_3DLUT_*` defines 3D LUT mode, index, data, 30-bit data, read/write controls, output normalization, and per-channel output offsets.
- `DC_PERFMON16_*` defines a perfmon counter/control/value block for DPP3-related performance observation.
- `MPCC0_*` through `MPCC7_*` define repeated MPC compositor channel controls: top/bottom selectors, OPP routing, blending/alpha/gain/background fields, memory power controls, stall status, and status readback.
- `MPC_*`, `ADR_*`, `CFG_*`, and `CUR_*` fields define global MPC control, CRC, perfmon event selection, pending/taken update bookkeeping, vertical-update locks, output muxes, and output denormalization clamps.
- `MPCC_OGAM0_MPCC_OGAM_*` starts the first MPCC output-gamma block: output gamma mode, LUT address/data/RAM selection, and PWL RAM A/B region descriptors.

## Important Macro Families

`CM3_CM_BLNDGAM_RAMA/RAMB` is the DPP blend-gamma transfer-function surface for instance 3. Each RAM has B/G/R start controls with 18-bit start values and 7-bit start-segment fields, per-channel 18-bit linear-slope controls, end controls with 16-bit end values plus slope/base fields, and `REGION_0_1` through `REGION_32_33` pairs. Each region pair encodes two 9-bit LUT offsets and two 3-bit segment counts at shifts `0`, `0xc`, `0x10`, and `0x1c`.

`CM3_CM_SHAPER_RAMA/RAMB` mirrors the double-buffered PWL pattern for the shaper LUT, but its start/end controls are slightly different from blend gamma: shaper end controls pack the end coordinate and end base, while shaper LUT data is programmed through `CM_SHAPER_LUT_INDEX`, `CM_SHAPER_LUT_DATA`, and `CM_SHAPER_LUT_WRITE_EN_MASK`.

`CM3_CM_3DLUT_*` exposes three-dimensional LUT controls. `CM_3DLUT_MODE` contains enable/mode and size selection, `CM_3DLUT_INDEX` chooses entries, `CM_3DLUT_DATA` and `CM_3DLUT_DATA_30BIT` carry 12-bit-pair and 30-bit packed data paths, and `CM_3DLUT_READ_WRITE_CONTROL` carries RAM selection, write mask, config status, and 30-bit enable state.

`DC_PERFMON16_*` is a self-contained performance counter block with enable/start/stop/clear style controls, counter event selection, mode/state, current value, high/low result registers, and interrupt/status bits. It is generated in the same header because DC perfmon registers are address-block-specific hardware registers rather than standalone driver logic.

`MPCC[0-7]_*` masks are replicated per MPCC instance. They cover layer routing (`TOP_SEL`, `BOT_SEL`, `OPP_ID`), blend mode and alpha controls (`MPCC_CONTROL`), state-machine control/status, update-lock selection, gain/background values, memory power, stall detection, and compositor status. The repeated field layouts let generic MPC code index by `mpcc_id`.

`MPC_*` global masks cover clock/reset, CRC setup/results, event selection, bypass background colors, stall timing, host read controls, pending/taken status registers, vupdate lock sets, and six output mux/denorm blocks. The update status registers are wide bit collections, so a single incorrect mask can misreport many pipe or OPP update states.

`MPCC_OGAM0_MPCC_OGAM_*` is the MPCC-side output-gamma LUT for compositor output. In this DCN 2.0 chunk it uses `MPCC_OGAM_MODE`, `MPCC_OGAM_LUT_INDEX`, 19-bit `MPCC_OGAM_LUT_DATA`, `MPCC_OGAM_LUT_RAM_CONTROL`, and RAM A/B PWL region descriptors. The next chunk continues the tail of `MPCC_OGAM0` and subsequent OGAM instances.

## APIs, Types, and Functions

There are no functions, structs, or enums defined in this header chunk. The macros are the generated hardware-description API used by typed register tables in the DC driver:

- `*_SHIFT` constants hold field bit offsets.
- `*_MASK` constants hold already-positioned field masks.
- Address-block comments such as `dce_dc_mpc_mpcc0_dispdec`, `dce_dc_mpc_mpc_cfg_dispdec`, and `dce_dc_mpc_mpcc_ogam0_dispdec` group registers by hardware block.

Representative consumers include `display/dc/dpp/dcn20/dcn20_dpp.h`, `display/dc/dpp/dcn20/dcn20_dpp_cm.c`, `display/dc/mpc/dcn20/dcn20_mpc.h`, and `display/dc/mpc/dcn20/dcn20_mpc.c`. The DPP side maps `CM0_*`/`CM3_*` generated masks into `dcn20_dpp` transfer-function fields with `TF_SF(...)`; the MPC side maps `MPCC0_*`, `MPC_OUT0_*`, and `MPCC_OGAM0_*` fields into `dcn20_mpc_shift` and `dcn20_mpc_mask` structures with `SF(...)`.

At runtime, DPP functions such as `dpp20_program_blnd_lut`, `dpp20_program_shaper`, and `dpp20_program_3dlut` use these masks through `REG_SET`, `REG_SET_2`, `REG_SET_4`, `REG_UPDATE`, and `REG_GET`. MPC functions such as `mpc2_program_luta`, `mpc2_program_lutb`, `mpc20_configure_ogam_lut`, `mpc20_get_ogam_current`, and `mpc20_power_on_ogam_lut` use the MPCC OGAM masks to select RAM A/B, write PWL entries, program region descriptors, and read active configuration state.

## Control Flow

This header has no branches or callable control flow. The operational flow appears in the DCN20 DPP and MPC code that consumes the fields:

1. DCN resource construction includes the generated offset and shift/mask headers, then initializes per-instance register address arrays and per-field shift/mask tables.
2. DPP blend gamma programming selects a RAM through `CM_BLNDGAM_LUT_WRITE_EN_MASK`, resets `CM_BLNDGAM_LUT_INDEX`, streams packed RGB and delta entries through `CM_BLNDGAM_LUT_DATA`, writes RAM A/B PWL start/end/region descriptors, and switches `CM_BLNDGAM_CONTROL` to the newly programmed mode.
3. DPP shaper programming follows the same double-buffer pattern with `CM_SHAPER_LUT_WRITE_EN_MASK`, `CM_SHAPER_LUT_INDEX`, `CM_SHAPER_LUT_DATA`, RAM A/B start/end/region registers, and `CM_SHAPER_CONTROL`.
4. DPP 3D LUT programming reads current mode/status, selects the target RAM and bit depth through `CM_3DLUT_READ_WRITE_CONTROL`, writes LUT entries through either `CM_3DLUT_DATA` or `CM_3DLUT_DATA_30BIT`, then updates `CM_3DLUT_MODE` and output normalization/offset fields.
5. MPC/MPCC composition code programs MPCC selector/control/gain/background fields per plane composition tree, routes MPCCs to OPPs, and uses update lock/vupdate fields to coordinate hardware-visible changes.
6. MPCC OGAM programming selects the inactive output-gamma RAM, resets the LUT index, streams RGB/delta data through `MPCC_OGAM_LUT_DATA`, writes RAM A/B PWL descriptors, then changes `MPCC_OGAM_MODE`/RAM control state.
7. Diagnostic or debug paths read perfmon counters, CRC results, stall/status registers, MPCC status, and update-pending/taken registers to validate hardware state.

## State and Persistence

The header stores no software state, but the fields describe persistent MMIO state in display hardware. Color LUTs and region descriptors persist until overwritten, reset, power-gated, or reinitialized by a modeset. RAM A/B selection fields are persistent and are used to avoid changing the active LUT while programming a new one.

DPP state includes blend-gamma mode/config status, LUT index auto-advance state, LUT RAM contents, memory power state, dealpha enable/mode, shaper offsets/scales, shaper LUT state, 3D LUT size/mode/RAM selection/bit depth, output normalization, and test-debug selector/data registers.

MPC state includes MPCC routing and blend configuration, OPP assignment, MPCC state-machine controls, background colors, gain values, memory power controls, stall and disabled status, global clock/reset, CRC controls and results, output mux choices, denormalization clamp values, update pending/taken state, and vupdate locks.

Perfmon state includes selected events, counter enable/state, interrupt/mask state, current count, high/low latched result words, and misc current-value fields. These fields can be read-only, write-one-to-clear, or mode-dependent in hardware, but the generated masks do not encode that semantic distinction beyond field names.

## Dependencies and Integration Points

This chunk depends on the companion offset header `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h` for concrete register addresses. The offset names and these shift/mask names must match exactly for the register helper tables to be correct.

Key integration points are:

- `display/dc/dpp/dcn20/dcn20_dpp.h`, which lists DPP transfer-function registers and maps generated color-management field masks into DPP shift/mask structs.
- `display/dc/dpp/dcn20/dcn20_dpp_cm.c`, which programs blend gamma, shaper, and 3D LUT hardware through these fields and the shared `cm_helper_program_xfer_func` PWL helper.
- `display/dc/dpp/dcn20/dcn20_dpp.c`, which reads shaper, 3D LUT, and blend-gamma status fields into DPP state snapshots.
- `display/dc/mpc/dcn20/dcn20_mpc.h`, which builds MPC register and mask lists for MPCC, output denorm, vupdate lock, and MPCC OGAM fields.
- `display/dc/mpc/dcn20/dcn20_mpc.c`, which programs MPCC blending and output-gamma LUT RAMs using the generated masks.
- `display/dc/hwss/dce/dce_hwseq.h` and DCN hardware sequence code, which reference MPC CRC registers for diagnostics.

Later DCN generations keep similar conceptual blocks but sometimes rename, split, or remove fields. For example, later MPC OGAM control fields add more status/select bits, while DCN3.2 comments indicate DPP blend gamma was removed from that DPP path. That makes the DCN 2.0 generated field layout generation-specific rather than a universal schema.

## Risks

The primary risk is silent MMIO misprogramming. A wrong shift or mask can compile cleanly while writing a neighboring bitfield in a live color, blend, routing, or diagnostic register.

Chunk-boundary risk is present at both ends. The chunk starts after the earlier `CM3_CM_BLNDGAM_RAMA` controls and most `RAMA_REGION_*` definitions, so this document only covers the tail of RAM A. It ends at `MPCC_OGAM0_MPCC_OGAM_RAMB_REGION_30_31`; `REGION_32_33` and following OGAM blocks continue in the next chunk.

Repeated-block risk is high. `MPCC0` through `MPCC7` and `MPC_OUT0` through `MPC_OUT5` are structurally similar, as are RAM A/B LUT descriptors. Pairing an instance's offset array with another instance's masks can produce valid-looking register writes against the wrong compositor/output block.

Double-buffer sequencing is order-sensitive. Blend gamma, shaper, and MPCC OGAM programming must choose the inactive RAM, enable the correct write mask, reset the LUT index, write the full table, program region descriptors, then switch mode. Incorrect masks for RAM selection, config status, LUT index, or mode fields can cause visible color corruption or flip to partially programmed LUT contents.

Color precision fields are sensitive. LUT data masks, 3D LUT 30-bit enable/data masks, normalization factors, offsets, slopes, bases, and region segment counts directly affect transfer-function accuracy. Small field-width errors can produce banding, clipping, color shifts, or failed HDR/color-management validation.

Update and status fields can hide synchronization bugs. `MPC_PENDING_TAKEN_STATUS_REG*`, `MPC_UPDATE_ACK_REG*`, `CUR_VUPDATE_LOCK_SET*`, MPCC stall/status, and CRC/perfmon fields are often used to prove that hardware accepted a change. Incorrect masks may make the driver believe a transition completed when it did not, or may force unnecessary waits.

Power-management masks can be disruptive. `CM3_CM_MEM_PWR_CTRL`, `MPCC*_MPCC_MEM_PWR_CTRL`, and MPCC OGAM memory power bits can gate memories that hold LUT or compositor state. A bad mask can drop state, keep memories powered unnecessarily, or make subsequent color programming fail.

## Test Signals

Useful validation signals include:

- Build coverage for DCN20 DPP and MPC code that includes `dcn_2_0_0_sh_mask.h`, especially `dcn20_dpp_cm.c`, `dcn20_dpp.c`, `dcn20_mpc.c`, and their generated register-list headers.
- Generated-header checks that every `REGISTER__FIELD__SHIFT` has a matching `REGISTER__FIELD_MASK`, masks align with shifts, and repeated MPCC/output/color RAM blocks remain structurally equivalent where hardware intends equivalence.
- Diff checks against AMD's authoritative DCN 2.0 register database or known-good upstream generated headers.
- Color pipeline tests for blend gamma, shaper LUT, and 3D LUT programming, including RAM A/B flips, bypass mode, 17x17x17 versus 9x9x9 3D LUT size, 10-bit versus 12-bit/30-bit paths, HDR curves, and gamut/color-management validation patterns.
- Plane composition tests covering MPCC top/bottom selection, alpha blend modes, premultiplied alpha, global alpha/gain, background color, bottom gain modes, OPP routing, and multi-plane update locks.
- Output-gamma tests that program MPCC OGAM RAM A/B and verify that `MPCC_OGAM_CONFIG_STATUS`, LUT data, slopes, bases, region offsets, and segment counts produce expected ramp output.
- CRC and perfmon smoke tests that enable MPC CRC, read `MPC_CRC_RESULT_*`, select perfmon events, and verify counter transitions and interrupt/status bits.
- Power-management tests that toggle DPP CM and MPCC/OGAM memory power states, then reprogram or read back LUT/configuration state after power transitions.
- Modeset and cursor/plane-update tests that exercise `MPC_PENDING_TAKEN_STATUS_REG*`, `MPC_UPDATE_ACK_REG*`, and `CUR_VUPDATE_LOCK_SET*` fields under concurrent updates and vblank synchronization.

## Cross-Chunk Notes

This is a middle slice of `dcn_2_0_0_sh_mask.h`, not a standalone module boundary. The preceding chunk owns the beginning of `CM3_CM_BLNDGAM` and earlier DPP3 color-management definitions. The following chunk continues the `MPCC_OGAM0` region table and subsequent output-gamma instances. The final per-file report should reconcile those boundaries so `CM3_CM_BLNDGAM_RAMA` and `MPCC_OGAM0` are not described as incomplete hardware blocks.

### subset-b-001620: lines 24909-27383

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 24909-27383

## Purpose

This chunk is part of the generated AMD DCN 2.0 register shift/mask header. It contains preprocessor constants only; there are no C functions, structs, storage objects, branches, or executable algorithms in this source slice. Each hardware register field is exposed as a bit-position macro ending in `__SHIFT` and a positioned bit mask ending in `_MASK`.

The covered hardware area is the MPC MPCC output gamma block (`MPCC_OGAM`) for DCN 2.0. `MPCC` is the multi-plane compositor component, and this chunk describes the programmable output/blend gamma LUT registers attached to MPCC instances:

- The chunk starts in the tail of `MPCC_OGAM0`, covering `MPCC_OGAM_RAMB_REGION_30_31` and `MPCC_OGAM_RAMB_REGION_32_33`.
- It then defines complete `dce_dc_mpc_mpcc_ogam1_dispdec` through `dce_dc_mpc_mpcc_ogam5_dispdec` address blocks.
- It begins `dce_dc_mpc_mpcc_ogam6_dispdec` and continues through `MPCC_OGAM6_MPCC_OGAM_RAMB_REGION_18_19` within the requested line range.

Although the repository path is under a `ceph-client` source mirror, this source chunk is AMD GPU display register metadata. It does not implement Ceph filesystem behavior, distributed storage state, network protocol handling, or filesystem persistence.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The public interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low bit number for a field.
- `<REGISTER>__<FIELD>_MASK`: already-positioned mask for the same field.

The chunk contains 2,091 `#define` entries: 1,047 shift constants and 1,044 mask constants. The small count mismatch is because the selected range begins and ends in the middle of repeated register groups, so some paired definitions are outside the chunk.

Important register families are:

- `MPCC_OGAMn_MPCC_OGAM_MODE`: output gamma mode selection. Local DCN20 code writes this field with `0` for bypass and `1` or `2` for RAM A/RAM B selection.
- `MPCC_OGAMn_MPCC_OGAM_LUT_INDEX`: 9-bit LUT index field (`0x000001FF`) used to set the host programming cursor before writing LUT data.
- `MPCC_OGAMn_MPCC_OGAM_LUT_DATA`: 19-bit LUT data field (`0x0007FFFF`) used for red/green/blue and delta entries in the PWL LUT stream.
- `MPCC_OGAMn_MPCC_OGAM_LUT_RAM_CONTROL`: host programming control with `MPCC_OGAM_LUT_WRITE_EN_MASK`, `MPCC_OGAM_LUT_RAM_SEL`, and `MPCC_OGAM_CONFIG_STATUS`. The write-enable mask occupies bits 0..2, RAM select is bit 3, and config status occupies bits 4..5.
- `MPCC_OGAMn_MPCC_OGAM_RAMA_*` and `MPCC_OGAMn_MPCC_OGAM_RAMB_*`: duplicate RAM-bank register sets for double-buffered LUT programming.
- `*_START_CNTL_[BGR]`: per-channel exponential-region start value and start segment. Start is 18 bits (`0x0003FFFF`), and start segment is 7 bits at bit 20 (`0x07F00000`).
- `*_SLOPE_CNTL_[BGR]`: per-channel 18-bit linear slope.
- `*_END_CNTL1_[BGR]`: per-channel 16-bit region end value.
- `*_END_CNTL2_[BGR]`: per-channel 16-bit end slope and 16-bit end base packed in one register.
- `*_REGION_<even>_<odd>`: packed descriptors for PWL regions 0 through 33. Each register carries two region descriptors: a 9-bit LUT offset and a 3-bit segment-count code for each region, at shifts `0`, `0xc`, `0x10`, and `0x1c`.

The full repeated instances in this chunk are `MPCC_OGAM1` through `MPCC_OGAM5`. For each of those instances, both RAM A and RAM B have per-channel start/slope/end registers and 17 packed region registers (`REGION_0_1` through `REGION_32_33`), covering 34 regions. `MPCC_OGAM6` is partial in this chunk, and `MPCC_OGAM0` is only represented by the tail of RAM B.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior is created by Display Core code that combines these generated masks and shifts with matching register addresses from `dcn_2_0_0_offset.h`.

The local DCN20 MPC integration follows this pattern:

1. `display/dc/resource/dcn20/dcn20_resource.c` includes `dcn/dcn_2_0_0_offset.h` and `dcn/dcn_2_0_0_sh_mask.h` while constructing DCN 2.0 resources.
2. `display/dc/mpc/dcn20/dcn20_mpc.h` uses `SRII(MPCC_OGAM_*, MPCC_OGAM, inst)` to build per-instance register-address arrays and `SF(MPCC_OGAM0_*, field, mask_sh)` to populate the shared shift/mask tables.
3. `display/dc/mpc/dcn20/dcn20_mpc.c` maps the generated fields into `struct xfer_func_reg` in `mpc2_ogam_get_reg_field()`.
4. `mpc2_set_output_gamma()` chooses the next LUT bank, powers the OGAM LUT memory, configures the host RAM select, programs RAM A or RAM B region registers, streams LUT entries through `MPCC_OGAM_LUT_DATA`, and finally writes `MPCC_OGAM_MODE` to make the selected bank active.
5. `mpc2_read_mpcc_state()` reads `MPCC_OGAM_CONFIG_STATUS` through `MPCC_OGAM_LUT_RAM_CONTROL` into the MPCC state snapshot.

The implied hardware sequencing is important even though this file only contains constants:

- The driver alternates RAM A and RAM B so a new output gamma curve can be programmed without overwriting the currently active bank.
- `MPCC_OGAM_LUT_RAM_CONTROL` selects the host-visible RAM and enables per-channel writes.
- `MPCC_OGAM_LUT_INDEX` resets the LUT write cursor before the PWL data stream.
- Region start/slope/end registers describe the PWL segmentation, while `MPCC_OGAM_LUT_DATA` carries the actual RGB and delta entries.
- `MPCC_OGAM_MODE` switches the hardware between bypass, RAM A, and RAM B after programming is complete.

## State And Persistence Behavior

The header itself stores no state and persists nothing. The state represented by these macros lives in GPU display registers and in caller-maintained Display Core objects.

Hardware state represented in this chunk includes:

- Active MPCC output gamma mode for each covered MPCC instance.
- Host programming cursor state through `MPCC_OGAM_LUT_INDEX`.
- Host-write control, selected RAM bank, write-enable channel mask, and hardware config-status readback through `MPCC_OGAM_LUT_RAM_CONTROL`.
- RAM A and RAM B PWL metadata: per-channel region starts, start segments, linear slopes, region ends, end slopes, end bases, region LUT offsets, and segment-count codes.
- RAM A and RAM B LUT entry contents written through `MPCC_OGAM_LUT_DATA`.

Persistence is hardware-scoped:

- Programmed RAM A/RAM B LUT contents and PWL region metadata persist until overwritten, reset, or lost through display block power/reset.
- `MPCC_OGAM_MODE` persists as the active bypass/RAM-bank selection until changed by the driver or reset.
- `MPCC_OGAM_CONFIG_STATUS` is readback/status state, not durable software state.
- The source file gives bit layout only. It does not encode reset values, legal enum meanings beyond field widths, access type, bank latch timing, or power-domain behavior.

Display Core mirrors part of this state in higher-level structures. For example, `dc.h` has MPCC OGAM snapshot fields for mode, selected bank, and PWL disable state, while `dcn20_mpc.c` reads the hardware config status into `struct mpcc_state`.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.0 register contract. The constants are meaningful only with sibling generated headers and Display Core register helpers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h` provides matching `MPCC_OGAMn_*` register addresses and base-index metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi10_enum.h` provides related enum values for `MPCC_OGAM_LUT_RAM_SEL` and `MPCC_OGAM_MODE`.
- `display/dc/mpc/dcn20/dcn20_mpc.h` binds these generated field names into MPC register, mask, and shift tables.
- `display/dc/mpc/dcn20/dcn20_mpc.c` is the primary local runtime consumer for DCN20 output gamma programming.
- `display/dc/resource/dcn20/dcn20_resource.c` declares DCN2 color capabilities, including programmable output gamma RAM support and the absence of OGAM ROM curves on DCN2.
- `display/dc/hwss/dcn20/dcn20_hwseq.c` coordinates higher-level color programming and notes that OGAM is programmed only for the top pipe.
- `display/dc/core/dc.c` captures or synthesizes MPCC OGAM state for active pipes in broader display state snapshots.

Other files include `dcn_2_0_0_sh_mask.h` for DCN20 interrupt, GPIO, DMUB, clock-manager, and GMC code, but the OGAM fields in this chunk are specifically consumed by the MPC/display color-management path.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These are raw preprocessor constants; a wrong shift, wrong mask, stale generated value, or mismatch against the offset header can compile successfully while programming the wrong display bits.

Important risk areas in this chunk are:

- Instance repetition. `MPCC_OGAM1` through `MPCC_OGAM6` repeat nearly identical fields. A register-address prefix or MPCC index mismatch can program the wrong compositor pipe with no type-system protection.
- Chunk boundaries. The slice starts after most of `MPCC_OGAM0` and ends before the rest of `MPCC_OGAM6`, so final per-file analysis must merge neighboring chunks before describing all MPCC OGAM instances.
- Bank switching. Runtime code depends on correctly selecting inactive RAM A or RAM B, programming it fully, and then changing `MPCC_OGAM_MODE`. Selecting the active bank or switching early can expose partially programmed gamma curves.
- LUT cursor and write-mask handling. `MPCC_OGAM_LUT_INDEX`, `MPCC_OGAM_LUT_WRITE_EN_MASK`, and `MPCC_OGAM_LUT_DATA` form a write stream. Wrong index reset, channel mask, or data width can scramble red/green/blue entries or deltas.
- PWL region consistency. Region start, segment count, LUT offset, slope, end, end slope, and end base fields must match the transfer-function generator's expectations. Bad values can produce banding, clipping, color shifts, or visibly discontinuous gamma ramps.
- Field width truncation. LUT offsets are 9 bits, LUT data is 19 bits, starts/slopes are 18 bits, ends and bases are 16 bits, and region segment counts are 3 bits. Callers must clamp/encode values before register writes.
- Status interpretation. `MPCC_OGAM_CONFIG_STATUS` is read from the same control register used for write enable and RAM selection. Generic read-modify-write sequences must avoid disturbing write-enable or selected-bank fields while polling status.
- Power sequencing. DCN20 code powers OGAM LUT memory via `MPCC_MEM_PWR_CTRL` before programming. Programming while the block is powered down or before status is stable can lose writes or make polling unreliable.
- Hardware workaround interaction. `dcn20_mpc.c` has a DEDCN20-305 workaround around `MPCC_OGAM_MODE`; mode transitions can depend on OTG/update-lock conditions outside this header.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Build coverage for DCN20 display code that includes `dcn_2_0_0_sh_mask.h` and instantiates `dcn20_mpc` resources.
- Static generated-header checks that every field has aligned shift/mask values, masks are positioned consistently, and repeated `MPCC_OGAM1-6` families match the authoritative register database.
- Diff checks against `dcn_2_0_0_offset.h` to ensure each `MPCC_OGAMn_*` field family has the expected matching register address.
- Unit or emulation coverage for `mpc2_set_output_gamma()` exercising bypass, RAM A programming, RAM B programming, bank alternation, and NULL transfer-function paths.
- Tests or hardware validation that `MPCC_OGAM_CONFIG_STATUS` reports bypass, RAM A, and RAM B consistently after mode changes.
- Color-management tests with identity, sRGB-like, PQ/HLG-like, and custom PWL curves to catch broken region descriptors, LUT offsets, segment counts, slopes, or data widths.
- Visual validation for banding, clipping, channel swaps, and discontinuities after output gamma changes on active pipes.
- Multi-pipe and multi-plane tests verifying OGAM is programmed on the intended top pipe/MPCC instance and does not affect unrelated pipes.
- Suspend/resume, display reset, and runtime power-management tests that confirm OGAM LUT contents are restored or safely reprogrammed after power loss.
- Regression coverage for DEDCN20-305 workaround paths and update-lock sequencing around `MPCC_OGAM_MODE` changes.

## Cross-Chunk Notes

This chunk is a middle slice of the `MPCC_OGAM` register area. The full per-file report should merge adjacent chunks to cover the beginning of `MPCC_OGAM0`, the remaining `MPCC_OGAM6` definitions after line 27383, and any subsequent MPCC OGAM or MPC color-register families.

### subset-b-001621: lines 27384-29960

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 27384-29960

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register field metadata. It contains no executable C logic; its purpose is to publish preprocessor constants for register bit shifts and masks in the DCN 2.0 display engine. The constants are consumed with the matching register-offset header so AMDGPU Display Core code can pack, update, and decode MMIO register fields through `REG_SET`, `REG_UPDATE`, `REG_GET`, `SF`, `SRI`, `SRII`, and related table-building macros.

The path is under a local `ceph-client` source mirror, but the content is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The requested range covers:

- The tail of `MPCC_OGAM6` RAM B region descriptors, specifically output-gamma RAMB regions 18 through 33.
- Full `MPCC_OGAM7` output-gamma field definitions: mode, LUT index/data/RAM control, RAM A and RAM B per-channel start/slope/end controls, and paired region descriptors 0 through 33.
- `dce_dc_mpc_mpc_ocsc_dispdec`: MPC output color-space-conversion coefficient format, output CSC mode, two coefficient banks for MPC outputs 0 through 5, and OCSC debug index/data fields.
- `dce_dc_mpc_mpc_dcperfmon_dc_perfmon_dispdec`: `DC_PERFMON17` performance counter control, state, value, interrupt, watermark, and status fields.
- `dce_dc_opp_abm0_dispdec`: backlight/PWM and ABM1 adaptive backlight management fields, including histogram/gain/low-scale controls and readback results.
- OPP output pipeline instances 0 through 4: formatter (`FMT`), display pattern generator (`DPG`), output buffer (`OPPBUF`), OPP pipe control, and OPP pipe CRC fields.
- The beginning of OPP formatter instance 5, covering only `FMT5_FMT_CLAMP_COMPONENT_R` and `FMT5_FMT_CLAMP_COMPONENT_G` within this chunk.

The chunk boundary is not semantic. It starts after earlier `MPCC_OGAM6` definitions and ends before the rest of `FMT5`, so complete per-block interpretation requires adjacent chunks.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, or persistence objects in this range. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` defines the bit position for a field.
- `<REGISTER>__<FIELD>_MASK` defines the 32-bit mask for that field.
- Register names are prefixed by hardware instance where applicable, for example `MPCC_OGAM7_`, `MPC_OUT3_`, `FMT4_`, `DPG2_`, `OPPBUF1_`, and `OPP_PIPE_CRC0_`.

Important macro families:

- `MPCC_OGAM6_MPCC_OGAM_RAMB_REGION_18_19` through `MPCC_OGAM6_MPCC_OGAM_RAMB_REGION_32_33` describe paired RAM B piecewise-linear output-gamma region descriptors. Each register packs an even and odd region with `LUT_OFFSET` at bits 0 and 16 and `NUM_SEGMENTS` at bits 12 and 28.
- `MPCC_OGAM7_MPCC_OGAM_MODE`, `MPCC_OGAM7_MPCC_OGAM_LUT_INDEX`, `MPCC_OGAM7_MPCC_OGAM_LUT_DATA`, and `MPCC_OGAM7_MPCC_OGAM_LUT_RAM_CONTROL` define the MPCC 7 output-gamma operating mode, 9-bit LUT index, 19-bit LUT data, write-enable color mask, RAM select, and configuration status fields.
- `MPCC_OGAM7_MPCC_OGAM_RAMA_*` and `MPCC_OGAM7_MPCC_OGAM_RAMB_*` define the two output-gamma RAM banks. They include per-channel blue/green/red start control, linear slope, end control, end slope/base, and 34 region descriptors per RAM. Start fields use 18-bit starts plus 7-bit start-segment values; end controls pack 16-bit end, slope, and base values; region descriptors use the repeated 9-bit offset plus 3-bit segment-count shape.
- `MPC_OUT_CSC_COEF_FORMAT` exposes `MPC_OCSC_COEF_FORMAT`; `MPC_OUT[0-5]_CSC_MODE` exposes `MPC_OCSC_MODE`; and `MPC_OUT[0-5]_CSC_Cxx_Cyy_[AB]` registers pack signed or fixed-point output CSC coefficients into low/high 16-bit fields for A and B coefficient banks.
- `MPC_OCSC_TEST_DEBUG_INDEX` and `MPC_OCSC_TEST_DEBUG_DATA` provide indexed debug access fields for the MPC output CSC block.
- `DC_PERFMON17_*` defines display performance monitor controls: enable, clear, select, trigger mode, interrupt generation/clear/status, counter mode, state, current value, high/low latched values, and watermark fields.
- `BL1_PWM_*` defines ambient/user/target/current/final/minimum backlight/PWM levels, ABM/PWM enable and clock controls, update sample rate, and grouped register lock/master-update controls.
- `DC_ABM1_*` defines ABM image processing and histogram collection fields: IPCSC coefficient select, ACE offset/slope tables, ACE thresholds, control flags, histogram/low-scale read-progress gating, min/max luma/pixel counters, sample rates, histogram-bin shift flags/indexes, 32 histogram result registers, and the backlight master lock.
- `FMT[0-4]_*` and the partial `FMT5_*` fields define formatter clamp lower/upper values, dynamic expansion, pixel encoding, subsampling, bit-depth truncation, spatial and temporal dithering controls, random seeds and offsets, clamp color format, side-by-side stereo width, 4:2:0 memory low-power controls, and 4:2:2 edge handling.
- `DPG[0-4]_*` defines display pattern generator enable, mode, dynamic range, bit depth, active resolution, field polarity, ramp increments, color values, offset/segment dimensions, and double-buffer-pending status.
- `OPPBUF[0-4]_*` defines output-buffer active width, display segmentation, overlap pixels, pixel repetition, double-buffer pending, 3D dummy data and VACT spacing, and padded segment pixel count.
- `OPP_PIPE[0-4]_OPP_PIPE_CONTROL` defines output pipe clock enable/on and digital bypass fields.
- `OPP_PIPE_CRC[0-4]_*` defines output-pipe CRC enable, continuous mode, stereo/interlace modes, pixel and source selection, one-shot pending status, CRC mask, and A/R/G/B/C result fields.

## Control Flow

This header chunk has no runtime control flow. Data flow is compile-time macro substitution:

1. DCN 2.0 resource and block headers include the generated offset and mask headers.
2. Register-list macros map hardware register offsets to per-block register structs.
3. Shift/mask macros are collected into per-block field structs through `SF`, `OPP_SF`, `ABM_SF`, and similar macros.
4. Runtime code calls register helpers, which use these constants to read-modify-write MMIO fields or decode status values.

Representative consumer flows in this tree:

- MPC color and gamma code uses MPCC OGAM and MPC OCSC masks through MPC register tables. Output gamma programming selects the MPCC OGAM mode/RAM bank, writes LUT index/data, and programs PWL region descriptors; output CSC programming selects an MPC output CSC mode and writes coefficient pairs into A or B coefficient banks.
- ABM/backlight code in `display/dc/dce/dce_abm.c` and `display/dc/dce/dmub_abm_lcd.c` writes `DC_ABM1_HG_SAMPLE_RATE`, `DC_ABM1_LS_SAMPLE_RATE`, `BL1_PWM_BL_UPDATE_SAMPLE_RATE`, `DC_ABM1_HG_MISC_CTRL`, `DC_ABM1_IPCSC_COEFF_SEL`, `BL1_PWM_CURRENT_ABM_LEVEL`, `BL1_PWM_TARGET_ABM_LEVEL`, and `BL1_PWM_USER_LEVEL`, using the matching masks for field packing.
- OPP formatter code in `display/dc/dce/dce_opp.c` programs `FMT_BIT_DEPTH_CONTROL` fields for truncation, spatial dithering, temporal dithering, randomization, and FRC selection.
- DCN20 OPP code in `display/dc/opp/dcn20/dcn20_opp.c` uses `DPG_CONTROL` and related fields to configure and disable display test patterns, reads DPG status, and captures OPP register state.
- OPP buffer and pipe code in `display/dc/opp/dcn10/dcn10_opp.c` writes `OPPBUF_CONTROL` active width and `OPP_PIPE_CONTROL` clock enable, then reads OPP pipe, CRC, and buffer registers for debug snapshots.
- Debug and validation paths read `OPP_PIPE_CRC_CONTROL`, `OPP_PIPE_CRC_RESULT*`, `DC_PERFMON17_*`, ABM histogram/results, and OPP register snapshots to validate displayed output or hardware state.

The header does not encode sequencing constraints. Consumers must still honor hardware-specific requirements such as LUT RAM selection before LUT writes, double-buffer update timing, ABM lock/update behavior, backlight/PWM enable ordering, OPP clock availability, CRC one-shot/continuous capture state, and perfmon clear/enable ordering.

## State And Persistence Behavior

The header itself stores no state and has no persistence behavior. It describes hardware MMIO fields that live in DCN 2.0 display registers.

State represented by this chunk includes:

- MPCC output-gamma state: selected mode, LUT index/data, active RAM bank, RAM configuration status, per-channel PWL start/end/slope settings, and 34 region descriptors for MPCC 7 plus the end of MPCC 6 RAM B.
- MPC output CSC state: coefficient format, per-output CSC mode, and A/B coefficient banks for six MPC outputs.
- MPC perfmon state: counter enable/clear/select, trigger and interrupt state, current value, high/low latched values, and watermark thresholds.
- Backlight and ABM state: PWM/user/target/current/final duty levels, ABM enable and clock settings, register locks, histogram/gain controls, sample rates, luma statistics, histogram bins, and master lock state.
- OPP formatter state: clamp limits, dynamic expansion, pixel/subsampling controls, bit-depth truncation, dithering seeds and modes, stereo width, 4:2:0 memory power state, and 4:2:2 edge handling.
- DPG state: generated-pattern enable/mode, resolution, dynamic range, colors, ramp settings, offset/segment configuration, and pending double-buffer updates.
- OPPBUF/OPP pipe state: active output width, segmentation, overlap, repetition, 3D dummy/spacer values, clock enable/on state, digital bypass, and pending update bits.
- OPP pipe CRC state: CRC capture enable, modes, selected source/pixels, pending one-shot capture, result mask, and channel result registers.

Persistence is hardware-defined. Many fields are programmed state that remains until modeset, suspend/resume, power-gating transition, reset, or explicit rewrite. Other fields are read-only status, sticky interrupt status, clear-on-write controls, pending bits, or latched readback values. The macro names expose likely semantics (`*_STATUS`, `*_PENDING`, `*_CLEAR`, `*_INT_STATUS`, `*_LOCK`, `*_STATE`, `*_RESULT`), but access type, reset value, and side effects are not described in this header.

## Dependencies And Integration Points

This chunk depends on the generated AMD DCN 2.0 register contract:

- `dcn_2_0_0_offset.h` supplies the corresponding MMIO register offsets and base indices.
- This `dcn_2_0_0_sh_mask.h` chunk supplies shifts and masks for fields in those registers.
- AMD Display Core block headers collect these constants into register/field tables for MPC, OPP, ABM, and resource construction.

Notable local integration points found in the tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h`, which demonstrates the MPCC OGAM and MPC output CSC field-table pattern also used by generated DCN-family resource tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_abm.h`, `dce_abm.c`, and `dmub_abm_lcd.c`, which map and use the ABM/PWM fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_opp.h` and `dce_opp.c`, which map and use formatter bit-depth, dither, and clamp fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn10/dcn10_opp.h` and `dcn10_opp.c`, which map OPPBUF, OPP pipe, and OPP pipe CRC fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn20/dcn20_opp.h` and `dcn20_opp.c`, which map and program DPG fields for test-pattern output.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc.h`, which includes debug/state capture members corresponding to MPCC OGAM, MPC output CSC, DPG, OPP pipe, OPP CRC, and OPPBUF state.

Practical integration surfaces are DRM/KMS modesets, color-management programming, HDR/SDR output transforms, output gamma LUT programming, display test patterns, panel backlight and adaptive backlight management, output bit-depth/dithering, multi-stream or segmented output buffering, pipe clock control, CRC-based validation, perfmon sampling, and display debug state collection.

## Risks And Edge Cases

- These constants are a hardware ABI. A wrong shift or mask can compile cleanly while silently writing the wrong bits, producing color corruption, broken backlight behavior, invalid test patterns, CRC mismatches, or display hangs.
- The chunk starts and ends inside larger generated families. `MPCC_OGAM6` RAM B is partial at the start, and `FMT5` is partial at the end; a final file-level report must merge adjacent chunks before claiming full block coverage.
- MPCC OGAM region definitions are repetitive and instance-indexed. Off-by-one region, RAMA/RAMB, or channel naming drift can affect only a narrow segment of a gamma curve and appear as banding or inaccurate color rather than an obvious failure.
- MPC output CSC coefficients are packed in 16-bit halves and duplicated across outputs 0 through 5 and banks A/B. Mask drift can swap coefficients, truncate sign/fraction bits, or update the wrong bank.
- ABM/PWM fields affect panel brightness. Incorrect masks for duty cycle, update sample rate, register locks, or current/target levels can cause visible flicker, stuck brightness, unsafe brightness jumps, or failed adaptive backlight updates.
- Histogram and luma statistic fields may be status/readback or gated by read-progress controls. Treating readback fields as ordinary writable state can clear or corrupt diagnostic data.
- Formatter bit-depth and dithering fields are highly visible. Incorrect truncation depth, temporal/spatial dither enable, random seed, or FRC selection can cause banding, noise, flicker, or unstable CRC output.
- `FMT_MAP420_MEMORY_CONTROL` contains memory power control/state fields. Wrong force/disable/state masks can interact with low-power transitions or 4:2:0 output programming.
- DPG, OPPBUF, and OPP pipe controls are double-buffered or clock-sensitive in places. Updating widths, segmentation, pattern dimensions, or clocks at the wrong time can create transient corruption or pending bits that never clear.
- CRC control has mode, interlace/stereo, source, pixel-select, and one-shot-pending fields. Misprogramming can make CRC validation meaningless even when output looks correct.
- Perfmon control includes interrupt and clear bits. Incorrect clear/status masks can drop performance events or leave interrupts asserted.

## Test Signals

Useful validation signals combine build-time coverage with DCN20 hardware behavior:

- Build AMDGPU/DC with DCN 2.0 support enabled. Missing or renamed macros should fail in MPC, OPP, ABM, resource, and debug-state register table paths.
- Diff this generated mask chunk against the matching `dcn_2_0_0_offset.h` families and adjacent DCN mask headers to catch unintended instance, field-width, or bank drift.
- Exercise output color programming on DCN20 hardware: gamma LUT updates through MPCC OGAM, output CSC matrix changes, SDR/HDR-like transforms, and visible color correctness across multiple pipes.
- Validate panel backlight and ABM behavior: brightness changes, ABM enable/disable, suspend/resume brightness restore, histogram readbacks, sample-rate changes, and absence of flicker or stuck duty-cycle state.
- Exercise formatter modes: truncation, spatial and temporal dithering, 6/8/10-bit style output depths, 4:2:0 and 4:2:2 output paths, stereo width where applicable, and clamp behavior.
- Exercise DPG test patterns for OPP instances 0 through 4, including enable/disable, ramp, color, dimensions, and double-buffer-pending status.
- Validate OPPBUF and OPP pipe state under normal and segmented output: active width, overlap, pixel repetition, MSO-style segmentation, pipe clock enable/on status, and digital bypass state.
- Validate OPP pipe CRC capture in one-shot and continuous modes, including interlace/stereo settings, selected source, pixel selection, result masks, and expected CRC stability.
- Sample `DC_PERFMON17` counters around known display workloads and confirm clear/enable/status/interrupt behavior.
- Watch kernel logs and display output for black screens, color shifts, banding, flicker, missed vblank/page-flip completion, underflow messages, EDID-independent modeset failures, CRC mismatches, perfmon interrupt noise, ABM failures, or resume regressions.

### subset-b-001622: lines 29961-32471

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 29961-32471

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register field metadata. It contains no executable C code; its interface is a set of preprocessor constants that name bit shifts and bit masks for memory-mapped display hardware registers.

The source path is under a local `ceph-client` mirror, but this file is Linux AMDGPU display-driver ASIC metadata. It does not implement Ceph filesystem behavior.

The range covers the tail of the output pixel processor instance 5 mask list and the beginning of the OPTC timing-generator mask list:

- `FMT5_*` formatter fields for blue-channel clamp, dynamic expansion, format control, bit-depth/truncation/dither, random dither seeds, clamp enable/color format, side-by-side stereo, 4:2:0 memory power, and 4:2:2 left-edge chroma handling.
- `DPG5_*` display pattern generator fields for enable/mode, dynamic range, bit depth, resolution, ramp control, active dimensions, two pattern colors in RGB/YUV component registers, segment offset/width, and double-buffer pending status.
- `OPPBUF5_*`, `OPP_PIPE5_*`, and `OPP_PIPE_CRC5_*` fields for OPP buffer segmentation/3D dummy data, OPP pipe clock/bypass control, and output-pipe CRC enable/modes/masks/results.
- `OPP_TOP_CLK_CONTROL` and `DSCRM[0-5]_DSCRM_DSC_FORWARD_CONFIG` fields for OPP-level clock gating and DSC forwarding control per output.
- `DC_PERFMON18_*` fields for the OPP display performance monitor control, counter state, current values, interrupt status/acknowledge bits, and high/low readback.
- `ODM[0-5]_OPTC_*` fields for OPTC input routing, data format/DSC mode, bytes per pixel, segment/slice width, input clock state, memory selection, underflow status/clear, and spare registers.
- Full `OTG0_*` and `OTG1_*` timing-generator field definitions, spanning horizontal/vertical timings, VRR/DRR totals, trigger controls, flow control, stereo/interlace state, timing status/readback, update locks, master enable, blank/black colors, vertical interrupts, CRC windows/results, static-screen controls, 3D structure, global sync lock, vstartup/vupdate/vready events, DSC start position, and pipe-update status.
- The beginning of `OTG2_*`, from horizontal total through `OTG2_OTG_V_TOTAL_CONTROL`, before the OTG2 interrupt/status section continues in the next chunk.

Each field appears as a pair of generated constants:

- `<REGISTER>__<FIELD>__SHIFT`: the bit position used to pack or unpack a field.
- `<REGISTER>__<FIELD>_MASK`: the field mask within the 32-bit register value.

These constants are paired with register offsets from `dcn_2_0_0_offset.h` and consumed through AMD display register-access helpers. They are hardware ABI data: correctness depends on matching the DCN 2.0 register specification.

## Important APIs, Types, And Macros

There are no functions, structs, enums, typedefs, variables, or storage objects in this range. The important API is the generated macro namespace used by register table initializers and access helpers.

Important macro families in this chunk:

- `FMT5_FMT_CONTROL__*` describes output format controls such as stereo sync override, PTI field polarity, spatial dither frame counter settings, pixel encoding, subsampling mode/order, CbCr bit-reduction bypass, double-buffer pending status, and PTI enable. These fields inform formatter programming for the sixth OPP instance.
- `FMT5_FMT_BIT_DEPTH_CONTROL__*` describes truncation, spatial dithering, temporal dithering, randomization, temporal reset, and FRC selection fields. Consumers use these masks when configuring panel/output bit depth and dithering behavior.
- `FMT5_FMT_DITHER_RAND_{R,G,B}_SEED__*`, `FMT5_FMT_CLAMP_*`, `FMT5_FMT_MAP420_MEMORY_CONTROL__*`, and `FMT5_FMT_422_CONTROL__*` define seed, offset, clamp, 4:2:0 memory-power, and 4:2:2 extra-left-pixel controls.
- `DPG5_DPG_CONTROL__*`, `DPG5_DPG_RAMP_CONTROL__*`, `DPG5_DPG_DIMENSIONS__*`, and `DPG5_DPG_COLOUR_*__*` define pattern-generator configuration used for test output and diagnostics.
- `OPPBUF5_OPPBUF_CONTROL__*`, `OPPBUF5_OPPBUF_3D_PARAMETERS_*__*`, and `OPPBUF5_OPPBUF_CONTROL1__*` define active width, display segmentation, overlap, pixel repetition, 3D vactive spacing, dummy RGB data, and segment padding.
- `OPP_PIPE5_OPP_PIPE_CONTROL__*` describes OPP pipe clock enable/on status and digital bypass.
- `OPP_PIPE_CRC5_OPP_PIPE_CRC_*__*` describes CRC enable, continuous/one-shot mode, stereo/interlace mode, pixel/source select, mask, and A/R/G/B/C result fields for output validation.
- `OPP_TOP_CLK_CONTROL__OPP_TOP_CLOCK_ENABLE` and `OPP_TOP_CLK_CONTROL__OPP_TOP_CLOCK_ON` expose top-level OPP clock state.
- `DSCRM[0-5]_DSCRM_DSC_FORWARD_CONFIG__DSCRM_DSC_FORWARD_EN` and `DSCRM_DSC_OPP_SOURCE_SELECT` expose DSC forwarding and source selection for each descrambler instance.
- `DC_PERFMON18_PERFCOUNTER_*` and `DC_PERFMON18_PERFMON_*` describe event selection, current-value selection, increment mode, hardware start/stop/counter-off controls, active state, interrupt enable/status/ack bits, report count, clock enable, current-value high/low, and readback selector fields.
- `ODM[0-5]_OPTC_INPUT_GLOBAL_CONTROL__*` exposes input soft reset, underflow interrupt enable/type/status, underflow clear/current status, and double-buffer pending bits for each OPTC input.
- `ODM[0-5]_OPTC_DATA_SOURCE_SELECT__*`, `OPTC_DATA_FORMAT_CONTROL__*`, `OPTC_BYTES_PER_PIXEL__*`, and `OPTC_WIDTH_CONTROL__*` describe ODM segmentation, source selection, DSC mode, compressed bytes per pixel, segment width, and DSC slice width.
- `OTG[0-2]_OTG_H_TOTAL__OTG_H_TOTAL`, `OTG_H_BLANK_START_END__*`, `OTG_H_SYNC_A__*`, `OTG_V_TOTAL__*`, `OTG_V_BLANK_START_END__*`, and `OTG_V_SYNC_A__*` are the core timing fields for horizontal/vertical totals, blanking windows, and sync windows.
- `OTG[0-2]_OTG_V_TOTAL_CONTROL__*` describes variable-refresh and dynamic refresh behavior: min/max total selection, mid-total substitution, lock-on-event, DRR active period, set-min mask enable/value, and mid-frame count.
- `OTG0_*` and `OTG1_*` include additional timing-generator fields for interrupts, triggers, flow control, stereo, interlace, status, snapshots, update locks, double buffering, CRC, static-screen detection, global sync lock, master update lock, manual flow control, range timing update, DRR readback, DSC start position, and pipe update status.

The local consumers do not generally reference instance 5 names directly. Instead, common field tables use instance 0 field names and indexed register-offset macros to describe all instances. For example, `display/dc/opp/dcn20/dcn20_opp.h` builds `struct dcn20_opp_shift` and `struct dcn20_opp_mask` through `OPP_MASK_SH_LIST_DCN20(__SHIFT)` and `OPP_MASK_SH_LIST_DCN20(_MASK)`, while `display/dc/optc/dcn10/dcn10_optc.h` builds timing-generator mask/shift tables through `TG_COMMON_MASK_SH_LIST_DCN(...)`. The repeated instance 5 and OTG1/OTG2 field definitions must remain numerically consistent with instance 0 for indexed helpers to be valid.

## Control Flow

This chunk has no runtime control flow. It is declarative mask/shift data.

Runtime control flow appears in consumers that include `dcn_2_0_0_sh_mask.h` and use these fields through generated tables:

- `display/dc/resource/dcn20/dcn20_resource.c` includes this header and initializes DCN20 block register, shift, and mask tables. For OPP, it populates `opp_shift` and `opp_mask` with `OPP_MASK_SH_LIST_DCN20`; for OPTC it uses timing-generator masks through DCN10/DCN20 OPTC structures.
- `display/dc/opp/dcn20/dcn20_opp.c` updates formatter 4:2:2 behavior with `REG_UPDATE(FMT_422_CONTROL, FMT_LEFT_EDGE_EXTRA_PIXEL_COUNT, count)` and reads OPP state with `REG_READ(DPG_CONTROL)`, `REG_READ(FMT_CONTROL)`, `REG_READ(OPP_PIPE_CONTROL)`, `REG_READ(OPP_PIPE_CRC_CONTROL)`, `REG_READ(OPPBUF_CONTROL)`, and `REG_READ(DSCRM_DSC_FORWARD_CONFIG)`.
- `display/dc/optc/dcn10/dcn10_optc.c` writes horizontal timing via `REG_SET(OTG_H_TOTAL, OTG_H_TOTAL, patched_crtc_timing.h_total - 1)`, writes sync fields with `REG_UPDATE_2`, programs variable refresh behavior through `REG_UPDATE_5(OTG_V_TOTAL_CONTROL, ...)`, reads hardware timing and underflow status with `REG_GET`, clears underflow with `REG_UPDATE(OPTC_INPUT_GLOBAL_CONTROL, OPTC_UNDERFLOW_CLEAR, 1)`, and derives `max_h_total`/`max_v_total` from the mask values.
- `display/dc/irq/dcn20/irq_service_dcn20.c` maps vupdate and vblank IRQ entries through `OTG_GLOBAL_SYNC_STATUS` fields such as `VUPDATE_NO_LOCK_INT_EN`, `VUPDATE_NO_LOCK_EVENT_CLEAR`, `VSTARTUP_INT_EN`, and `VSTARTUP_EVENT_CLEAR`.
- `display/dmub/src/dmub_dcn20.c`, `display/dc/gpio/dcn20/hw_factory_dcn20.c`, and `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c` include the same generated mask header for DCN20 service and hardware-resource integration.

The generated constants do not enforce sequencing. Correct sequencing is in the block drivers: modeset code must program timings and source routing in the right order, use update locks and double-buffer controls around latched registers, handle underflow clear bits as side-effecting operations, and avoid reading CRC/perfmon/status fields before hardware has produced stable values.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. It defines how software encodes and decodes hardware register state.

The represented hardware state includes:

- Persistent display programming state, such as formatter clamp/dither/bit-depth controls, OPP buffer segmentation, ODM source routing, DSC mode, segment width, OTG timing totals, blank/sync windows, master enable, black/blank colors, stereo/interlace controls, and DSC start position.
- Double-buffered state, indicated by fields such as `FMT_DOUBLE_BUFFER_REG_UPDATE_PENDING`, `DPG_DOUBLE_BUFFER_PENDING`, `OPPBUF_DOUBLE_BUFFER_PENDING`, `OPTC_DOUBLE_BUFFER_PENDING`, `OTG_UPDATE_PENDING`, `OTG_MASTER_UPDATE_LOCK`, and `UPDATE_LOCK_STATUS`. These values may be staged and latched at vertical update boundaries rather than taking effect immediately.
- Status and counter state, such as OPP pipe CRC result registers, OTG pixel/status/readback counters, frame counts, snapshot status, perfmon current values, perfmon counter state, and `OTG_PIPE_UPDATE_STATUS` flip/DC/cursor update bits.
- Interrupt and sticky event state, such as underflow interrupt/status/clear, `OTG_V_TOTAL_INT_STATUS`, `OTG_GLOBAL_SYNC_STATUS`, vertical interrupt controls, range timing update status, and perfmon interrupt status/ack fields.
- Power and clock state, such as `FMT_MAP420MEM_PWR_*`, `OPP_PIPE_CLOCK_EN/ON`, `OPP_TOP_CLOCK_ENABLE/ON`, and `OPTC_INPUT_CLK_EN/ON/GATE_DIS`.

Persistence is hardware-defined. Some fields remain programmed until modeset, suspend/resume, reset, power gating, or explicit rewrite. Other fields are read-only status, sticky status cleared by writing a clear/ack bit, self-clearing trigger bits, or current counter snapshots. The macro names reveal likely behavior but not access permissions, reset values, write-one-to-clear semantics, or clock-domain timing requirements.

## Dependencies And Integration Points

This chunk depends on the AMD generated ASIC register-header contract:

- `dcn_2_0_0_offset.h` supplies the matching MMIO register offsets and base indices.
- This `dcn_2_0_0_sh_mask.h` range supplies the bit packing contract for the same registers.
- AMD display register helpers such as `REG_READ`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `SF`, `SRI`, `OPP_SF`, and indexed register-list macros consume the generated constants.
- DCN20 resource construction wires offsets, shifts, and masks into block-specific structs such as OPP and timing-generator register tables.

Important local integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn20/dcn20_opp.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn20/dcn20_opp.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn10/dcn10_optc.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn10/dcn10_optc.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn20/dcn20_optc.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`

Functional integration points are display modeset programming, page-flip/vblank timing, variable refresh and DRR, ODM combine/split routing, DSC output positioning, formatter color/depth/chroma programming, output diagnostics through pattern generation and CRC, OPP/OPTC performance monitoring, underflow detection/clear, global-sync lock behavior, and IRQ routing for vblank/vupdate/vline-style events.

## Risks And Edge Cases

- Generated mask/shift values are hardware ABI. A wrong mask or shift can compile cleanly and still program the wrong bits, causing black screens, flicker, timing instability, bad color, invalid CRCs, stuck interrupts, or hangs.
- The chunk boundary is not semantic. It starts after earlier `FMT5` fields already appeared in the previous chunk and ends in the middle of the `OTG2` register bank. Per-file synthesis must merge adjacent chunk results before making complete claims about FMT5 or OTG2 coverage.
- Repeated per-instance banks are vulnerable to instance drift. `FMT5`, `DPG5`, `OPPBUF5`, `OPP_PIPE5`, `OPP_PIPE_CRC5`, `DSCRM[0-5]`, `ODM[0-5]`, `OTG0`, `OTG1`, and `OTG2` fields must remain aligned with their offset-header instance mappings and with the field tables that often use instance 0 as the canonical mask source.
- OTG fields are timing critical. Incorrect horizontal/vertical totals, blanking, sync polarity, vtotal min/max/mid, update-lock, trigger, global-sync, or DSC start-position masks can produce modeset failures, missed vblank, bad VRR/DRR pacing, multi-display sync failures, or invalid DSC output.
- Underflow fields have side effects. `OPTC_UNDERFLOW_CLEAR` and related interrupt bits must be handled as hardware status/clear controls; using a regular read-modify-write without understanding semantics can lose diagnostic state or fail to clear sticky status.
- CRC and perfmon fields mix control, status, and acknowledge semantics. Bad masks can leave CRC one-shot pending, sample the wrong channel/window, acknowledge the wrong counter interrupt, or report misleading diagnostic data.
- Formatter and dither fields directly affect visible output. Wrong bit-depth, truncation, temporal/spatial dithering, random seed, clamp, 4:2:0 memory, or 4:2:2 left-edge masks can cause banding, chroma artifacts, incorrect color range, or power-state bugs that only appear on particular output formats.
- Clock and power bits can be asynchronous or status-only. `*_CLOCK_EN`, `*_CLOCK_ON`, memory power state, and clock-gate-disable fields should be treated according to block driver sequencing rather than inferred solely from names.
- The header has no type checking. Masks are `L` integer constants and shifts are untyped preprocessor values, so invalid cross-register use may not be caught by the compiler if names happen to fit helper macros.

## Test Signals

Useful validation signals are mostly compile-time and hardware/display behavioral checks:

- Build AMDGPU/DC with DCN20 enabled. Missing or renamed macros should fail in DCN20 resource, OPP, OPTC, IRQ, DMUB, GPIO, and clock-manager code paths.
- Diff this generated chunk against the matching `dcn_2_0_0_offset.h` register names and adjacent DCN family mask headers to catch accidental register-bank omissions, instance drift, or unexpected field-width changes.
- Exercise DCN20 modesets on hardware across single-display, multi-display, ODM/split, DSC, stereo/interlace where supported, suspend/resume, and hotplug paths.
- Validate OTG behavior: vblank delivery, page-flip completion, vline interrupts, frame counters, horizontal/vertical active size readback, update-lock behavior, global-sync/vupdate/vstartup/vready events, VRR/DRR min/max/mid changes, and DSC start position.
- Validate OPP/formatter behavior: output bit depth, truncation/dither modes, random seed effects, clamp configuration, RGB/YUV pixel encodings, 4:2:0/4:2:2 output formats, and absence of visible banding or chroma-edge artifacts.
- Validate diagnostics: DPG pattern output on pipe 5, OPP pipe CRC one-shot and continuous modes, OTG CRC windows/results, perfmon counter start/stop/interrupt/ack behavior, and debug state readbacks.
- Watch kernel logs and display symptoms for negative signals: underflow reports, missed vblank/page-flip timeouts, stuck update pending bits, black screens, flicker, bad colors, CRC mismatches, HPD or resume regressions caused by broader DCN20 integration, and clock/power transition warnings.

### subset-b-001623: lines 32472-34932

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 32472-34932

## Scope

This chunk is a generated register field shift/mask slice for AMD DCN 2.0 output timing generator (OTG) blocks. It covers the end of the `dce_dc_optc_otg2_dispdec` address block, full repeated field definitions for `OTG3` and `OTG4`, and the first timing fields for `OTG5`. The content is entirely preprocessor data: each hardware field has a `__SHIFT` value and a matching `_MASK` value used by the display core register-access macros.

## Purpose

The macros describe the bit layout of DCN 2.0 OTG registers. The OTG is the timing side of OPTC: it generates horizontal/vertical timing, blanking, sync, update, trigger, CRC, dynamic refresh, global sync lock, and status signals for each display pipe. Driver code does not manipulate these constants directly in this header; instead, resource setup expands `SF(...)` lists into `struct dcn_optc_shift` and `struct dcn_optc_mask` tables, and OPTC code uses `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and related helpers to program/read the selected hardware instance.

## Register Families In This Chunk

- `OTG2` continuation from vertical total interrupt status through `OTG_SPARE_REGISTER`.
- Complete `OTG3` block: horizontal/vertical timing, trigger, force-count, flow control, stereo, enable/blanking, interlace, status/counters, snapshot, interrupts, double buffering, colors, vertical interrupts, CRC engines, static screen, 3D, GSL/global sync, master update lock, DRR, DSC start, pipe update, and spare register.
- Complete `OTG4` block with the same layout and fields as `OTG3`.
- Initial `OTG5` timing fields through the `OTG5_OTG_H_SYNC_A_CNTL` comment at the chunk boundary.

The chunk is highly repetitive by hardware instance. For example, `OTG3_OTG_STATUS_POSITION__OTG_VERT_COUNT_MASK` and `OTG4_OTG_STATUS_POSITION__OTG_VERT_COUNT_MASK` have identical bit positions but apply to different register addresses in the generated address header.

## Important APIs, Types, And Consumers

No C functions or types are defined here. The important integration contract is the macro naming shape:

- `OTGx_REGISTER__FIELD__SHIFT` gives the field lsb.
- `OTGx_REGISTER__FIELD_MASK` gives the field mask.
- `SF(OTG0_REGISTER, FIELD, __SHIFT)` and `SF(OTG0_REGISTER, FIELD, _MASK)` in OPTC headers select these generated constants into runtime tables.

Key consumers observed in the tree:

- `display/dc/inc/hw/optc.h` defines `struct optc`, which stores `tg_regs`, `tg_shift`, and `tg_mask` pointers plus timing limits and state used by the timing-generator functions.
- `display/dc/optc/dcn10/dcn10_optc.h` defines the base OTG register and field lists. It includes many fields in this chunk such as `OTG_V_TOTAL_CONTROL`, `OTG_TRIGA_CNTL`, `OTG_CRC_CNTL`, status, interrupt, blanking, stereo, and static-screen fields.
- `display/dc/optc/dcn20/dcn20_optc.h` extends the DCN1 list for DCN2 with fields in this chunk: `OTG_GLOBAL_CONTROL1`, `OTG_GLOBAL_CONTROL2`, `OTG_GSL_WINDOW_X/Y`, `OTG_VUPDATE_KEEPOUT`, `OTG_DSC_START_POSITION`, `OTG_CRC_CNTL2`, `OTG_MANUAL_FLOW_CONTROL`, `OTG_DRR_CONTROL`, and `OTG_PIPE_UPDATE_STATUS`.
- `display/dc/optc/dcn10/dcn10_optc.c` and `display/dc/optc/dcn20/dcn20_optc.c` use these fields through register helper macros for CRTC enable/disable, reset triggers, dynamic refresh rate, manual triggers, CRC, blanking, and status polling.

## Functional Areas

### Timing And Dynamic Refresh

The timing fields include:

- Horizontal totals and sync/blank windows: `OTG_H_TOTAL`, `OTG_H_BLANK_START_END`, `OTG_H_SYNC_A`, `OTG_H_SYNC_A_CNTL`, `OTG_H_TIMING_CNTL`.
- Vertical totals and sync/blank windows: `OTG_V_TOTAL`, `OTG_V_TOTAL_MIN`, `OTG_V_TOTAL_MAX`, `OTG_V_TOTAL_MID`, `OTG_V_TOTAL_CONTROL`, `OTG_V_BLANK_START_END`, `OTG_V_SYNC_A`, `OTG_V_SYNC_A_CNTL`.
- DRR status/control: `OTG_DRR_CONTROL` exposes `OTG_DRR_AVERAGE_FRAME` and `OTG_V_TOTAL_LAST_USED_BY_DRR`.

`optc1_set_drr()` programs `OTG_V_TOTAL_MIN/MAX/MID` and updates `OTG_V_TOTAL_CONTROL` selectors. `optc2_setup_manual_trigger()` also updates `OTG_V_TOTAL_CONTROL` so DMCUB/manual trigger flows can alter OTG timings. The relevant masks in this chunk are therefore timing-critical: a wrong bit position can corrupt vtotal selection, frame pacing, or variable refresh behavior.

### Trigger And Reset Control

The trigger family includes `OTG_TRIGA_CNTL`, `OTG_TRIGA_MANUAL_TRIG`, `OTG_TRIGB_CNTL`, `OTG_TRIGB_MANUAL_TRIG`, `OTG_FORCE_COUNT_NOW_CNTL`, `OTG_VERT_SYNC_CONTROL`, `OTG_TRIG_MANUAL_CONTROL`, and `OTG_MANUAL_FLOW_CONTROL`.

The driver uses trigger A heavily:

- `optc1_enable_reset_trigger()` selects a source pipe, chooses vsync edge detection based on polarity, and enables force-count behavior.
- `optc1_enable_crtc_reset()` configures trigger edge and either next-line vsync force or immediate count force.
- `optc1_disable_reset_trigger()` clears trigger and force-vsync state.
- `optc2_setup_manual_trigger()` programs trigger A source 21 with the current OTG instance and sets `OTG_SET_V_TOTAL_MIN_MASK` to use TRIGA.
- `optc2_program_manual_trigger()` writes `OTG_TRIGA_MANUAL_TRIG`.

The chunk includes both control bits and sticky/status bits such as `OTG_TRIGA_OCCURRED`, `OTG_TRIGA_CLEAR`, `OTG_FORCE_COUNT_NOW_OCCURRED`, and `OTG_FORCE_COUNT_NOW_CLEAR`. These fields affect synchronization between pipes and controlled timing changes.

### Enable, Blanking, Interlace, Stereo, And Status

The core state fields include:

- `OTG_CONTROL`: master enable, start/disable point control, current enable state, field polarity, read request disable, and AV sync bits.
- `OTG_BLANK_CONTROL`, `OTG_MASTER_EN`, `OTG_BLANK_DATA_COLOR(_EXT)`, and `OTG_BLACK_COLOR(_EXT)` for blanking and output color state.
- `OTG_INTERLACE_CONTROL` and `OTG_INTERLACE_STATUS`.
- `OTG_STEREO_FORCE_NEXT_EYE`, `OTG_STEREO_STATUS`, and `OTG_STEREO_CONTROL`.
- `OTG_STATUS`, `OTG_STATUS_POSITION`, `OTG_STATUS_FRAME_COUNT`, `OTG_STATUS_VF_COUNT`, and `OTG_STATUS_HV_COUNT`.

These are consumed by functions such as `optc1_is_tg_enabled()`, `optc1_wait_for_state()`, position readers, blanking helpers, stereo helpers, and timing reads. Several fields are read-only hardware state or sticky status rather than ordinary writable configuration.

### Snapshot, Interrupt, And Update Lock

The chunk defines snapshot fields (`OTG_SNAPSHOT_STATUS`, `OTG_SNAPSHOT_CONTROL`, `OTG_SNAPSHOT_POSITION`, `OTG_SNAPSHOT_FRAME`), interrupt controls (`OTG_INTERRUPT_CONTROL`, vertical interrupt position/control registers, `OTG_V_TOTAL_INT_STATUS`, `OTG_VSYNC_NOM_INT_STATUS`, `OTG_RANGE_TIMING_INT_STATUS`), and synchronization/update controls (`OTG_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_MASTER_UPDATE_LOCK`, `OTG_GLOBAL_CONTROL0/1/2/3`, `OTG_VUPDATE_KEEPOUT`, `OTG_PIPE_UPDATE_STATUS`).

DCN2-specific code uses:

- `OTG_GLOBAL_CONTROL1` and `OTG_GLOBAL_CONTROL2` in double-buffer lock/unlock helpers.
- `OTG_VUPDATE_KEEPOUT` to avoid unsafe update windows.
- `OTG_PIPE_UPDATE_STATUS` to report pending/taken flip, DC register, cursor, and vupdate keepout state.

Interrupt/status fields often pair an event bit, an interrupt status bit, a clear/ack bit, a mask bit, and sometimes type/position selectors. These must be handled as write-one-to-clear or hardware-sticky semantics in consuming code; this header only supplies bit locations.

### CRC And Test Signals

CRC fields include:

- `OTG_CRC_CNTL` and `OTG_CRC_CNTL2`.
- Window controls for CRC engines 0 and 1: `OTG_CRC0_WINDOWA/B_X/Y_CONTROL`, `OTG_CRC1_WINDOWA/B_X/Y_CONTROL`.
- Data readbacks for engines 0 through 3: `OTG_CRC{0..3}_DATA_RG` and `OTG_CRC{0..3}_DATA_B`.
- Signature masks: `OTG_CRC_SIG_RED_GREEN_MASK` and `OTG_CRC_SIG_BLUE_CONTROL_MASK`.

`optc1_configure_crc()` writes window controls and enables CRC0 or CRC1 selection through `OTG_CRC_CNTL`. `optc2_configure_crc()` first programs `OTG_CRC_CNTL2` with DSC/ODM mode information, then delegates to the base implementation. `optc1_get_crc()` reads the RGB/YCbCr component CRC fields. Incorrect masks here would break debugfs/validation CRC capture or cause mismatched CRC values under DSC/ODM modes.

### Global Sync Lock, GSL, DSC, And ODM-Adjacent Timing

The chunk includes global sync lock support:

- `OTG_GSL_VSYNC_GAP`, `OTG_GSL_CONTROL`, `OTG_GSL_WINDOW_X`, `OTG_GSL_WINDOW_Y`.
- `OTG_GLOBAL_SYNC_STATUS` for startup/update/ready events, no-lock status, interrupt enables/types, clear bits, stereo, and field number status.
- `OTG_MASTER_UPDATE_MODE`, `OTG_MASTER_UPDATE_LOCK`, and global controls for master update lock windows.

It also includes `OTG_DSC_START_POSITION`, which coordinates DSC start x/line position with the timing generator, and `OTG_REQUEST_CONTROL`, which affects request mode for horizontal duplicate behavior. DCN2 resource and OPTC code add these registers to the common OTG tables.

## Control Flow

This header has no executable control flow. Runtime control flow is indirect:

1. DCN resource initialization builds per-OTG register address arrays and per-field shift/mask tables from generated macros like those in this chunk.
2. `struct optc` instances receive pointers to those tables.
3. Timing-generator functions call register helper macros, which use the current OTG instance's register address plus the field shift/mask to modify only the selected field.
4. Hardware state changes asynchronously with scanout, vblank, vupdate, interrupts, CRC capture, DRR, and trigger events; driver code polls or clears status fields using the same masks.

The repeated `OTG2`, `OTG3`, `OTG4`, and `OTG5` prefixes are not loop logic. They are separate hardware-instance namespaces that the generated address/mask tables map into a uniform software interface.

## State And Persistence Behavior

The state represented by this chunk is MMIO hardware state. It persists in GPU registers while the display block is powered and is normally reprogrammed during modesets, DPMS transitions, resume, or pipe reconfiguration. Important state categories:

- Latched configuration: timing totals, sync/blank windows, trigger source selection, blank colors, CRC setup, global sync/update-lock configuration.
- Live counters/status: horizontal/vertical count, frame count, blank/active/sync status, interlace/stereo status, pipe update pending/taken status.
- Sticky events and clear bits: vtotal min events, vsync nominal events, trigger occurred bits, global sync events, range timing events, CRC one-shot pending bits.

The header itself has no persistence layer and no defaults. Hardware reset values and power-gating behavior come from the ASIC, firmware, and display driver init paths.

## Dependencies And Integration Points

- Depends on generated companion address headers, especially `dcn_2_0_0_offset.h`, for register addresses matching these field definitions.
- Depends on display core register-helper macros that combine register address, shift, and mask tables.
- Integrates with `dcn10_optc.h` base OTG mask lists and `dcn20_optc.h` DCN2 extensions.
- Integrates with `dcn20_resource.c` style resource construction that binds the generated masks into arrays for each timing generator.
- Integrates with DMCUB/firmware-managed timing changes through fields such as `OTG_V_TOTAL_CONTROL`, manual trigger fields, and DRR controls.
- Integrates with IRQ service code through global sync and vupdate/vstartup/vready event fields on later DCN families with the same register model.

## Risks And Edge Cases

- Generated-header drift: if this mask header and the matching offset/header tables are from different ASIC register database revisions, the driver can write valid field names to wrong bits or wrong addresses.
- Instance-copy mistakes: the `OTG2`, `OTG3`, `OTG4`, and `OTG5` blocks must remain consistent. A single copied mask error for one instance can affect only that pipe, making failures topology-dependent.
- Read/write semantic confusion: status, clear, ack, interrupt mask, and enable bits coexist in the same registers. Treating sticky clear bits as persistent config can lose interrupts or hide events.
- Timing-window hazards: update lock, vupdate keepout, double-buffer mode, global sync, and DRR fields interact with scanout timing. Incorrect masks may only fail under high refresh, VRR/DRR, multi-display, ODM, or DSC.
- CRC limitations: CRC window fields are 15-bit x/y style fields and result fields are 16-bit components. Out-of-range values are masked by hardware/register helpers rather than validated here.
- Boundary chunking: this slice starts mid-`OTG2` and ends at the beginning of `OTG5`; final file-level research must reconcile adjacent chunks to describe full `OTG2` and `OTG5` coverage.

## Test Signals

Useful validation signals for code that consumes this chunk:

- Build coverage: compile AMDGPU DCN2 display code with generated mask tables enabled; missing or renamed macros should fail at compile time in OPTC mask list expansion.
- Modeset smoke: enable displays on OTG2, OTG3, OTG4, and OTG5-capable hardware paths and verify timing, vblank, and scanout position are sane.
- DRR/VRR tests: exercise `optc1_set_drr()` and `optc2_get_last_used_drr_vtotal()` and confirm vtotal min/max/mid behavior and last-used vtotal readback.
- Trigger/reset synchronization: validate multi-pipe timing synchronization, manual trigger setup/programming, and triggered reset occurrence/clear behavior.
- CRC capture: enable CRC0/CRC1 with windowed capture and, on DCN2 DSC/ODM modes, verify `OTG_CRC_CNTL2` mode fields produce expected CRC stability.
- Interrupt/status tests: verify vstartup/vupdate/vready, vertical interrupt, vsync nominal, range timing, and pipe update status events can be observed and cleared without losing subsequent events.
- Suspend/resume and power-gating tests: confirm OTG state is reinitialized rather than relying on stale register contents after display block reset.

### subset-b-001624: lines 34933-37347

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 34933-37347

## Scope

This chunk covers lines 34933-37347 of `dcn_2_0_0_sh_mask.h`, a generated AMD DCN 2.0 register shift/mask header. The slice contains 2,165 preprocessor definitions: 1,083 `__SHIFT` constants and 1,082 `__MASK` constants. It starts in the OPTC/OTG5 timing-generator block, crosses several display-controller address blocks, and ends in the beginning of DP AUX0 interrupt-control definitions.

The file does not define C functions or runtime data structures. Its "API" is the collection of macro names that other AMDGPU DC/DCN code uses to pack, unpack, read, write, and poll memory-mapped display hardware registers.

## Purpose

The macros map named hardware bitfields to stable bit positions and masks for DCN 2.0 display registers. Driver code can then use register helper macros, generated register tables, or direct `REG_SET`, `REG_UPDATE`, `REG_GET`, and equivalent accessors without hard-coding numeric bit layouts at call sites.

This chunk is especially tied to:

- OTG5 output timing generator state, synchronization, dynamic refresh, CRC, stereo/3D, global sync lock, update lock, and pipe-update status.
- OPTC miscellaneous controls for DWB source selection, GSL source selection, OPTC clocking, and ODM memory power.
- DC performance monitor instances 19 and 20.
- DIO I2C/DDC controller setup, transaction, status, and interrupt fields.
- DIO scratch, memory power, clock gate, soft reset, PSP/generic interrupt, and power-management fields.
- HPD0 through HPD5 hot-plug-detect status, interrupt, control, fast-training, and toggle-filter fields.
- The opening DP AUX0 control, software-control, arbitration, and interrupt-control fields.

## Important Macro Groups

### OTG5 timing and synchronization

The OTG5 section defines fields for core display timing:

- Horizontal and vertical timing: `OTG5_OTG_H_SYNC_A_CNTL`, `OTG5_OTG_H_TIMING_CNTL`, `OTG5_OTG_V_TOTAL`, `OTG5_OTG_V_TOTAL_MIN`, `OTG5_OTG_V_TOTAL_MAX`, `OTG5_OTG_V_TOTAL_MID`, `OTG5_OTG_V_BLANK_START_END`, `OTG5_OTG_V_SYNC_A`, and `OTG5_OTG_V_SYNC_A_CNTL`.
- Dynamic refresh / DRR support: `OTG5_OTG_V_TOTAL_CONTROL`, `OTG5_OTG_V_TOTAL_INT_STATUS`, `OTG5_OTG_DRR_CONTROL`, and range-timing update interrupt status.
- Trigger and force-count paths: `OTG5_OTG_TRIGA_CNTL`, `OTG5_OTG_TRIGB_CNTL`, their manual trigger registers, `OTG5_OTG_FORCE_COUNT_NOW_CNTL`, `OTG5_OTG_TRIG_MANUAL_CONTROL`, and `OTG5_OTG_MANUAL_FLOW_CONTROL`.
- Main OTG enable and blanking controls: `OTG5_OTG_CONTROL`, `OTG5_OTG_MASTER_EN`, `OTG5_OTG_BLANK_CONTROL`, `OTG5_OTG_PIPE_ABORT_CONTROL`, `OTG5_OTG_CLOCK_CONTROL`, and blank/black color registers.
- Readback and status: `OTG5_OTG_STATUS`, `OTG5_OTG_STATUS_POSITION`, frame/VF/HV count registers, pixel readback registers, interlace status, snapshot status/control/position/frame, and pipe update status.
- Interrupt scheduling: `OTG5_OTG_INTERRUPT_CONTROL`, vertical interrupt 0/1/2 position/control, `OTG5_OTG_GLOBAL_SYNC_STATUS`, and range timing interrupt status.
- Update-lock and double-buffering: `OTG5_OTG_UPDATE_LOCK`, `OTG5_OTG_DOUBLE_BUFFER_CONTROL`, `OTG5_OTG_MASTER_UPDATE_LOCK`, `OTG5_OTG_GLOBAL_CONTROL0` through `OTG5_OTG_GLOBAL_CONTROL3`, and `OTG5_OTG_VUPDATE_KEEPOUT`.
- Stereo, 3D, and global sync lock: `OTG5_OTG_STEREO_FORCE_NEXT_EYE`, `OTG5_OTG_STEREO_STATUS`, `OTG5_OTG_STEREO_CONTROL`, `OTG5_OTG_3D_STRUCTURE_CONTROL`, `OTG5_OTG_GSL_CONTROL`, `OTG5_OTG_GSL_VSYNC_GAP`, and GSL window X/Y registers.
- CRC and static-screen detection: `OTG5_OTG_CRC_CNTL`, `OTG5_OTG_CRC_CNTL2`, CRC window/data registers 0-3, CRC signature masks, and `OTG5_OTG_STATIC_SCREEN_CONTROL`.

The OTG5 block is a repeated timing-generator instance. The `5` suffix identifies the hardware instance; other chunks in the same header likely define equivalent OTG0-OTG4 and later OTG blocks.

### OPTC miscellaneous and ODM power

The `dce_dc_optc_optc_misc_dispdec` address block starts at line 35752. It defines:

- `DWB_SOURCE_SELECT` fields for selecting which OPTC feeds DWB0-DWB2.
- `GSL_SOURCE_SELECT` fields for GSL ready-source and timing-sync selection.
- `OPTC_CLOCK_CONTROL` fields for display clock gating and test-clock selection.
- `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL2`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS` fields for up to 12 ODM memory slices plus unassigned/vblank power modes.
- `OPTC_MISC_SPARE_REGISTER` as a full-width spare field.

These macros are integration points for display writeback, multi-pipe synchronization, and ODM memory power policy.

### DC perfmon instances 19 and 20

Two nearly identical DC performance monitor blocks appear:

- `DC_PERFMON19_*` under the OPTC perfmon address block.
- `DC_PERFMON20_*` under the DIO perfmon address block.

Each instance exposes performance counter select/mask controls, counter state selectors, run/stop control, report count, count-off interrupt enable/status/ack, 32-bit value readback split into low/high fields, and per-counter interrupt status/ack bits. Consumers can program counter sources, gate counting windows, read accumulated values, and service count-off interrupts.

### DIO I2C/DDC controller

The `dce_dc_dio_dout_i2c_dispdec` address block defines the display I2C/DDC controller interface:

- `DC_I2C_CONTROL` for software go, send-reset, sw status reset, transaction count, DDC selection, and shutdown.
- `DC_I2C_ARBITRATION` for software, DMCU, and hardware-request arbitration status/requests/done bits.
- `DC_I2C_INTERRUPT_CONTROL` for done, NACK, arbitration-done/lost, DDC1-6 HW-done, and DDCVGA HW-done interrupt/ack/mask/type fields.
- `DC_I2C_SW_STATUS` for DC I2C used-by-sw, software stop, NACK, timeout, abort, done, and byte-count status.
- Per-DDC hardware status registers for DDC1 through DDC6, each with used-by-HW, EDID detect, done, NACK, timeout, and abort fields.
- Per-DDC speed/setup registers for DDC1 through DDC6, including threshold, filter-during-stall, start/stop timing control, prescale, data/clock drive controls, reset length, EDID detect mode/enable, intra-byte delay, intra-transaction delay, and time limit.
- Four transaction descriptor registers `DC_I2C_TRANSACTION0` through `DC_I2C_TRANSACTION3`, each carrying read/write, stop-on-NACK, start, stop, and byte count fields.
- `DC_I2C_DATA` for indexed data access and `DC_I2C_EDID_DETECT_CTRL` for EDID detect timing/retry/reset behavior.
- `DC_I2C_READ_REQUEST_INTERRUPT` for DDC1-6 and DDCVGA read-request occurred/int/ack/mask fields plus global ack-enable and interrupt type.

This area is central to EDID reads, DDC transactions, display detection, and firmware/software arbitration over the I2C engine.

### DIO miscellaneous, clocks, reset, power, and interrupts

The `dce_dc_dio_dio_misc_dispdec` block defines:

- Eight full-width DIO scratch registers.
- `DCE_VCE_CONTROL` audio-stream select.
- `DIO_MEM_PWR_STATUS`, `DIO_MEM_PWR_STATUS1`, `DIO_MEM_PWR_CTRL`, `DIO_MEM_PWR_CTRL2`, and `DIO_MEM_PWR_CTRL3` for I2C, DP A-G, HDMI0-6, AFMT0-5, DPHY, and AUX memory/light-sleep force/disable/state fields.
- `DIO_CLK_CNTL`, `DIO_CLK_CNTL2`, and `DIO_CLK_CNTL3` for display/ref clock gating across DIO, DAC, DIG A-G, DP stream encoder, DP link encoder, PHY symclk, DP alt, AUX, and audio format blocks.
- `DIO_POWER_MANAGEMENT_CNTL` for global power-management enable.
- `DIG_SOFT_RESET` for DIG frontend, DP stream encoder, DP link encoder, AUX, FEC, PHY symclk, and related soft-reset bits across links.
- `DIO_HDMI_RXSTATUS_TIMER_CONTROL` for HDMI RX status timer interval and enable.
- PSP and generic DIO interrupt status/clear/message fields.

These fields are lower-level than the DC core timing fields; mistakes here can affect clock availability, PHY/link reset sequencing, AUX/I2C availability, and audio/link sideband behavior.

### HPD0-HPD5 hot plug detect

The chunk contains six repeated HPD blocks, `HPD0` through `HPD5`. Each block defines:

- `DC_HPD_INT_STATUS` fields for interrupt status, sense, acknowledge, polarity, and mask.
- `DC_HPD_INT_CONTROL` fields for interrupt acknowledge, polarity, mask, detection timer, and interrupt-detected flags.
- `DC_HPD_CONTROL` fields for enable, connection timer, and RX interrupt timer.
- `DC_HPD_FAST_TRAIN_CNTL` fields for min/max wait count, legacy fast train enable, and fast-train complete status.
- `DC_HPD_TOGGLE_FILT_CNTL` fields for toggle-filter timer control.

These macros support connector hotplug detection, DP fast-training coordination, and debounce/toggle filtering across multiple physical outputs.

### DP AUX0 opening block

The final address block begins `dce_dc_dio_dp_aux0_dispdec`. This chunk includes:

- `DP_AUX0_AUX_CONTROL` for AUX enable/reset/reset-done, low-speed read, update-disable, ignore-HPD-disconnect, mode detect, HPD selection, impedance calibration request, test mode, deglitch enable, and spare bits.
- `DP_AUX0_AUX_SW_CONTROL` for software AUX go, low-speed read trigger, start delay, and software write-byte count.
- `DP_AUX0_AUX_ARB_CONTROL` for AUX arbitration priority/status, queued-go controls, software/DMCU register-use request and done bits. Some names intentionally alias the same bit positions, such as `AUX_SW_USE_AUX_REG_REQ` and `AUX_SW_PENDING_USE_AUX_REG_REQ`.
- `DP_AUX0_AUX_INTERRUPT_CONTROL` for software done, low-speed done, GTC sync lock done, and GTC sync error interrupt/ack/mask fields. The chunk ends while this register's masks are still being listed, so later DP AUX0 fields continue in the next chunk.

## Control Flow and Runtime Behavior

There is no executable control flow in this header. Runtime behavior emerges when DCN code includes this file and uses the macros with register accessor helpers:

1. A driver path selects a register address from the paired generated address header or a DCN register table.
2. The caller supplies field values by name.
3. Register helper macros combine `__SHIFT` and `__MASK` values to clear, insert, or extract the appropriate bits.
4. The resulting memory-mapped register read/write changes hardware state or observes status.

The same pattern applies to interrupt service paths and polling loops: status fields are extracted with masks/shifts, then clear/ack fields are written using the matching `*_ACK`, `*_CLEAR`, or event-clear masks.

The most important ordering constraints are not encoded here. They are imposed by hardware programming sequences in the consuming driver code, for example enabling clocks before touching dependent blocks, taking update locks before programming timing, clearing interrupts after observing status, and arbitrating AUX/I2C ownership before software transactions.

## State and Persistence Behavior

These macros describe persistent hardware register state, not software-owned persistence. Relevant state classes in this chunk include:

- Configuration state: timing totals, blank/sync positions, DDC speed/setup, HPD timers, clock gating, power modes, update-lock locations, CRC windows, perfmon counter sources, and AUX control options.
- Live status state: current OTG/blank/master enable status, frame/count positions, interlace/stereo state, update pending/taken bits, I2C/AUX done/error flags, HPD sense/status, memory power states, clock-on/busy state, and perfmon current values.
- Interrupt/event latch state: vertical interrupts, V_TOTAL/min events, global-sync events, range-timing update, I2C done/NACK/arbitration/read-request events, HPD events, PSP/generic DIO interrupts, and AUX done/GTC events.
- Clear/ack write state: many registers have paired `*_ACK`, `*_CLEAR`, or event-clear fields that are normally write-one-to-clear or write-controlled by hardware semantics.

The persistence boundary is the display hardware register file. Values may reset on GPU reset, block soft reset, power-gate transitions, suspend/resume, or display engine reinitialization. The header itself stores no state and cannot validate whether a field is safe to write at a given time.

## Dependencies and Integration Points

This header depends on the generated DCN 2.0 register naming scheme being consistent with:

- The paired address/offset header for DCN 2.0 registers.
- AMDGPU DC register accessor infrastructure that expects `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macro names.
- ASIC-specific register tables that bind generic DC resource code to concrete DCN 2.0 register instances.
- Hardware documentation or generator inputs that define bit positions, widths, reset behavior, and access semantics.

Integration surfaces visible from this chunk include:

- Timing-generator and OPTC code that programs OTG5 for mode set, vblank/vupdate, DRR, CRC capture, stereo/3D, master update lock, and global sync lock.
- Display writeback and ODM code that uses DWB source selection and ODM memory power fields.
- Power-management code that gates display clocks, controls memory light sleep, manages HDMI/DP/DIO power states, and sequences soft resets.
- Connector management code that uses HPD and DDC/I2C fields for EDID detection, hotplug interrupts, and DP link training readiness.
- DP AUX code that arbitrates AUX register access among software and DMCU paths and services AUX done/error interrupts.
- Performance/debug paths that program DC perfmon instances 19/20 and read counters.

## Risks and Edge Cases

- Generated macro drift is high risk. A single wrong shift or mask silently writes the wrong hardware bits, which can break modesets, clocks, hotplug, AUX/I2C transactions, or interrupt handling.
- Repeated-instance blocks invite copy/paste or generator-index mistakes. OTG5, HPD0-HPD5, DDC1-DDC6, and perfmon19/20 are structurally repetitive but instance-specific.
- Some fields intentionally alias the same bit, especially in AUX arbitration pending/request names. Consumers must understand read-versus-write semantics rather than assuming distinct storage.
- Interrupt fields often include status, ack/clear, mask, and type bits in one register. Incorrect helper use can clear pending events, leave interrupts masked, or acknowledge the wrong event.
- Clear/ack naming is inconsistent across blocks (`ACK`, `CLEAR`, `EVENT_CLEAR`, `*_INT_CLEAR`, `*_TAKEN_CLEAR`). Tests and reviews should verify hardware semantics in the consuming paths, not just macro spelling.
- Clock, reset, and memory-power fields can race with register access if callers do not first ensure the target block is powered and ungated.
- DDC/I2C and DP AUX arbitration fields coordinate software, hardware, and firmware/DMCU users. Incorrect ownership handling can deadlock transactions or corrupt EDID/AUX exchanges.
- Dynamic timing fields such as V_TOTAL min/max/mid, GSL, vupdate keepout, and master update locks are sensitive to vertical timing windows. Incorrect sequencing can cause flicker, underflow, missed vblank events, or synchronization loss.
- The chunk ends mid-DP-AUX0 address block. Any whole-file analysis must merge this with the following chunk before treating DP AUX0 coverage as complete.

## Test and Validation Signals

Useful validation for this chunk is mostly indirect because the header has no standalone executable behavior:

- Build coverage: compile AMDGPU/DCN code paths that include `dcn_2_0_0_sh_mask.h` and instantiate DCN 2.0 register tables.
- Macro consistency checks: generated tests or scripts can verify every `__SHIFT` has a corresponding `_MASK`, mask width matches shift/field width, and repeated instances have consistent layouts where expected.
- Modeset and vblank tests: exercise OTG5 timing, vblank/vupdate interrupt, DRR, update-lock, and CRC paths on DCN 2.0 hardware or emulation.
- Connector tests: hotplug/unplug cycles across HPD0-HPD5, EDID reads over DDC1-DDC6, DDC read-request interrupts, and DP AUX transactions.
- Power-management tests: suspend/resume, display off/on, clock-gating, light-sleep, memory power, and DIG/AUX soft-reset sequences.
- Perf/debug tests: configure perfmon19 and perfmon20 counters, read low/high values, and verify count-off interrupts and acknowledgements.
- Register trace comparison: compare MMIO writes generated by driver operations against known-good traces or hardware-programming guides for DCN 2.0.
- Static review signal: because this is generated hardware metadata, any hand edit in this chunk should be treated as suspicious unless backed by updated generator input or vendor register documentation.

## Open Questions for Merge Lane

- Confirm the previous chunk supplies the start of `OTG5_OTG_H_SYNC_A_CNTL`, since this chunk begins with that register's field definitions before the next comment marker.
- Merge with the next chunk for the remainder of DP AUX0 and subsequent AUX/register blocks before producing the final per-file document.
- Cross-check whether perfmon instance numbering 19/20 aligns with address block placement in the paired DCN 2.0 offset header.

### subset-b-001625: lines 37348-39691

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 37348-39691

## Purpose

This chunk is generated AMD DCN 2.0 register shift/mask metadata. It contains only C preprocessor constants; there are no functions, structs, variables, branches, allocation paths, or executable algorithms in this range. Each hardware field is represented by a bit-position macro ending in `__SHIFT` and a positioned mask macro ending in `_MASK`.

The covered hardware area is the connector-side display I/O path:

- The chunk begins in the tail of `DP_AUX0_AUX_INTERRUPT_CONTROL`, after the corresponding register comment and some earlier fields in the previous chunk.
- It then defines the remaining `DP_AUX0` AUX status, data, DPHY, GTC sync, and PHY wake fields.
- It defines full repeated AUX register field sets for `DP_AUX1` through `DP_AUX5`.
- It enters `DIG0`, the first digital front-end / stream-encoder instance, covering front-end selection, output CRC, test patterns, FIFO status, HDMI packet controls, HDMI audio control, generic packets, general control, audio-format/ISRC fields, double-buffer controls, metadata engine controls, MPEG infoframe payload fields, generic packet headers, and the first generic payload register.

The file is under a local `ceph-client` source mirror, but this path is AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior, distributed filesystem state, network storage protocols, or persistent filesystem data handling.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low bit number for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: already-positioned bit mask for the same field.

Important macro families in this chunk:

- `DP_AUX0_AUX_INTERRUPT_CONTROL`: tail fields for AUX low-speed done interrupt/ack/mask and AUX GTC sync lock/error interrupt/ack/mask handling. The chunk begins after this register's first fields.
- `DP_AUXn_AUX_CONTROL` for `n=1..5`: AUX enable/reset/reset-done, low-speed read/update disable, HPD disconnect handling, mode detection, HPD selection, impedance calibration request, test mode, deglitch, and spare bits.
- `DP_AUXn_AUX_SW_CONTROL`: software AUX start delay, write byte count, and software go trigger.
- `DP_AUXn_AUX_ARB_CONTROL`: AUX register arbitration state, software request/done handshake, command-delay control, reset flag, and MCUI selection.
- `DP_AUXn_AUX_INTERRUPT_CONTROL`: software AUX done, low-speed done, GTC sync lock-done, and GTC sync error interrupt/status/ack/mask fields.
- `DP_AUXn_AUX_SW_STATUS`: software AUX transaction completion/request state, timeout state, RX timeout/overflow, HPD disconnect, partial byte, non-AUX mode, min-count violation, invalid stop/start/sync/recovery flags, reply byte count, and arbitration status.
- `DP_AUXn_AUX_LS_STATUS`: low-speed AUX transaction completion/request, receive error flags, reply byte count, CP IRQ, update state, and update ack.
- `DP_AUXn_AUX_SW_DATA` and `DP_AUXn_AUX_LS_DATA`: indexed byte data windows for software and low-speed AUX transfers, including software read/write selection and autoincrement disable.
- `DP_AUXn_AUX_DPHY_TX_REF_CONTROL`, `TX_CONTROL`, `RX_CONTROL0`, and `RX_CONTROL1`: AUX physical-layer transmit reference selection/rate/divider, TX precharge timing, output-enable timing, mode-detect delay, RX start/receive windows, half-symbol/phase detection, transition filtering, below-threshold allowances, detection threshold, RX precharge skip, and timeout length/multiplier.
- `DP_AUXn_AUX_DPHY_TX_STATUS` and `RX_STATUS`: live TX active/state/half-symbol period and RX state/sync/half-symbol period readback.
- `DP_AUXn_AUX_GTC_SYNC_CONTROL`, `ERROR_CONTROL`, `CONTROLLER_STATUS`, and `STATUS`: AUX global-time-code sync enable and calibration/lock parameters, potential/definite error thresholds, lock acquisition timeout and retries, lock/error controller state, GTC sync transfer status, NACK, master request, and ack fields.
- `DP_AUXn_AUX_PHY_WAKE_CNTL`: PHY wake request, pending, priority, and ack bits.
- `DIG0_DIG_FE_CNTL`: stream-encoder source selection, stereo sync selection/gating, start, bypass/input-pixel selection, Dolby Vision enable/missed metadata status, front-end symbol-clock status, TMDS pixel encoding, and TMDS color format.
- `DIG0_DIG_OUTPUT_CRC_*`: digital output CRC enable, link/data selection, and result readback.
- `DIG0_DIG_CLOCK_PATTERN`, `DIG0_DIG_TEST_PATTERN`, and `DIG0_DIG_RANDOM_PATTERN_SEED`: test-pattern and random/static pattern controls for stream-encoder diagnostics.
- `DIG0_DIG_FIFO_STATUS`: FIFO error, overwrite level, error ack, calibrated/min/max/average levels, read clock source, calibration state, and recalculation/recompute triggers.
- `DIG0_HDMI_METADATA_PACKET_CONTROL`: HDMI metadata packet enable, line reference, missed status, and target line. This is relevant to dynamic metadata paths such as HDR/Dolby Vision-style metadata.
- `DIG0_HDMI_GENERIC_PACKET_CONTROL0`, `2`, `3`, and `4`: generic packet send/continuous/line-reference controls and line-number programming for packet slots in this chunk.
- `DIG0_HDMI_CONTROL` and `DIG0_HDMI_STATUS`: HDMI keepout, data scrambling, clock-channel rate, null packet filling, packet-generator version, error ack/mask, deep-color enable/depth, AVMUTE status, packet errors, and HDMI error interrupt status.
- `DIG0_HDMI_AUDIO_PACKET_CONTROL`, `DIG0_HDMI_ACR_PACKET_CONTROL`, and `DIG0_AFMT_AUDIO_PACKET_CONTROL2`: HDMI audio packet cadence/delay, ACR send/source/auto-send/N-multiple/priority, AFMT audio layout override, channel enable, DP audio stream ID, HBR override, and 60958 override.
- `DIG0_HDMI_VBI_PACKET_CONTROL`, `DIG0_HDMI_INFOFRAME_CONTROL0/1`, `DIG0_HDMI_GC`, `DIG0_AFMT_MPEG_INFO0/1`, `DIG0_AFMT_GENERIC_HDR`, and `DIG0_AFMT_GENERIC_0`: HDMI null/GC/ISRC/ACP/infoframe/generic-packet send and line controls plus packet header/payload byte fields.
- `DIG0_AFMT_ISRC1_0` through `DIG0_AFMT_ISRC2_3`: ISRC status/continue/valid fields and 32 bytes of UPC/EAN/ISRC payload.
- `DIG0_HDMI_DB_CONTROL` and `DIG0_DME_CONTROL`: HDMI and metadata-engine double-buffer pending/taken/clear/lock/disable state and metadata engine requestor, enable, stream type, and double-buffer controls.

Several generated names repeat terms such as `MASK`, for example fields whose hardware names include mask bits and generated macro names ending in `_MASK`. This is expected in AMD register headers.

## Control Flow

This header chunk has no runtime control flow. Driver control flow is created by consumers that combine these masks and shifts with register offsets from `dcn_2_0_0_offset.h` and access helpers such as `REG_READ`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT`.

Representative runtime use:

1. DCN20 resource setup includes `dcn_2_0_0_offset.h` and `dcn_2_0_0_sh_mask.h`.
2. Register-list macros select instance-specific offsets for AUX engines, stream encoders, GPIO, IRQ, DMUB, clock, and display resources.
3. Field-list macros such as `DCN_AUX_MASK_SH_LIST` and stream-encoder `SE_*_MASK_SH_LIST` materialize shift/mask structs from names in this generated header.
4. Display Core code requests DPCD/EDID AUX transactions, link training, HPD-sensitive sideband operations, HDMI packet programming, stream start/stop, audio packet setup, metadata packet updates, CRC reads, or test-pattern output.
5. Hardware-specific code programs registers using these generated fields while polling done/status bits or writing ack/clear bits as needed.

Concrete local consumers include:

- `display/dc/resource/dcn20/dcn20_resource.c`, which includes this DCN 2.0 mask header and builds the six AUX engine register entries. Its `aux_engine_regs(id)` macro also stores `DP_AUX0_AUX_CONTROL__AUX_RESET_MASK` in the AUX register table, showing direct use of this header's AUX control masks.
- `display/dc/dce/dce_aux.h`, where `DCN_AUX_MASK_SH_LIST` maps `DP_AUX0_AUX_CONTROL`, `DP_AUX0_AUX_ARB_CONTROL`, `DP_AUX0_AUX_SW_CONTROL`, `DP_AUX0_AUX_SW_DATA`, `DP_AUX0_AUX_SW_STATUS`, `DP_AUX0_AUX_INTERRUPT_CONTROL`, and AUX DPHY RX timeout fields into per-AUX shift/mask structures. Instance-specific register addresses bind these generic DP_AUX0 field definitions to AUX engines 0 through 5.
- `display/dc/dce/dce_stream_encoder.h`, where stream-encoder field lists map `DIG0_HDMI_*`, `DIG0_AFMT_*`, `DIG0_DIG_FE_CNTL`, and related fields into the stream-encoder mask/shift structures used by DCE/DCN stream encoder code.
- `display/dmub/src/dmub_dcn20.c`, which includes the same offset and mask headers and uses generated field macros through `FD_MASK` and `FD_SHIFT` for DMUB service register definitions.
- Other DCN20 include points such as `display/dc/irq/dcn20/irq_service_dcn20.c`, `display/dc/gpio/dcn20/hw_factory_dcn20.c`, `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`, and `amdgpu/gmc_v10_0.c`.

The hardware sequencing implied by the fields is significant even though the header does not encode it:

- AUX transactions require ownership/arbitration, request/go programming, data-window access, done polling, reply-byte counting, error status inspection, and interrupt/status ack.
- AUX DPHY and GTC sync fields affect link-side timing and synchronization behavior and must be programmed consistently with the link encoder and DP AUX protocol timing.
- HDMI and AFMT packet fields are latched into stream output, often through double-buffer pending/taken controls or frame/line scheduling.
- Status, ack, clear, reset, and missed/error bits must be handled according to hardware semantics that are not described by the macro values alone.

## State And Persistence Behavior

The header itself stores no state and persists nothing. The represented state lives in DCN 2.0 display hardware registers and in caller-owned Display Core objects that cache register addresses, masks, and stream/AUX state.

Hardware state represented by this chunk includes:

- AUX engine state: enable/reset status, software transfer parameters, arbitration ownership, transaction done/request flags, reply byte counts, error flags, low-speed update state, interrupt status/masks/acks, indexed transfer data, DPHY TX/RX configuration and status, GTC sync configuration/status/error state, and PHY wake pending/ack state.
- Connector sideband state: HPD-disconnect reactions, AUX timeout windows, low-speed AUX update handling, CP IRQ indication, GTC sync lock/lock-lost/error signals, and PHY wake requests.
- Digital front-end state: selected stream source, stereo sync, start/bypass state, Dolby Vision enable and missed-metadata status, symbol-clock status, TMDS encoding/color format, output CRC enable/select/result, clock/static/random test pattern state, and FIFO calibration/error state.
- HDMI stream state: keepout mode, data scrambling, clock-channel rate, null-packet behavior, packet-generator version, deep color, packet errors, active AVMUTE, audio packet cadence, ACR behavior, VBI packet sends, infoframe sends, generic packet sends, line references, and general-control AVMUTE/packing phase.
- Audio-format and metadata state: AFMT channel enable/layout/HBR/60958 overrides, ISRC valid/status/payload bytes, MPEG infoframe bytes, generic packet header/payload bytes, HDMI double-buffer pending/taken/lock/disable state, and metadata engine enable/requestor/stream-type/double-buffer state.

Persistence is hardware-specific:

- Configuration fields such as AUX timing, HDMI packet controls, TMDS/deep-color settings, AFMT channel enable, generic packet bytes, and metadata-engine enable generally persist until explicitly rewritten, reset, power-gated, or restored during modeset/resume.
- Status fields such as AUX transaction errors, FIFO errors, HDMI packet errors, metadata missed status, pending/taken flags, and GTC sync controller status are live or sticky hardware state.
- Ack/clear/reset/go fields are action-oriented and may be self-clearing, edge-sensitive, or write-one-to-clear depending on the register specification.
- Indexed AUX and packet payload data windows expose transient transfer/payload staging state, not durable software storage.

The generated macros do not say whether a field is read-only, write-only, write-one-to-clear, self-clearing, latched on vblank, or double-buffered. Consumers must rely on Display Core sequencing and hardware documentation.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.0 register contract and is meaningful together with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h`, which provides the matching `mm*` register offsets and base-index macros.
- Adjacent sections of `dcn_2_0_0_sh_mask.h`, because this range starts inside `DP_AUX0_AUX_INTERRUPT_CONTROL` and ends inside the DIG0 AFMT/generic packet region.
- DCN/DCE Display Core register-list and field-list macros, especially AUX and stream-encoder macros that turn these generated constants into typed shift/mask structs.
- Register helper infrastructure in AMDGPU Display Core and DMUB service code.

Primary integration points are:

- DP AUX and DPCD access: link training, EDID-over-AUX paths for DP/eDP, sideband transactions, AUX timeout/error handling, and HPD-disconnect-sensitive AUX cancellation.
- AUX low-speed/GTC sync paths: low-speed status/update handling, GTC sync lock/error interrupts, global-time-code synchronization, and link-side timing diagnostics.
- Power and wake sequencing: AUX PHY wake request/pending/ack handling and AUX reset/enable behavior around suspend/resume, HPD, and link bring-up.
- Stream encoder programming: source selection, stream start, stereo sync, TMDS encoding/color format, HDMI deep-color/scrambling/clock-channel control, Dolby Vision metadata enable, and HDMI packet-generation behavior.
- HDMI audio and metadata: audio packet timing, ACR generation, AFMT audio channel/layout/HBR controls, ISRC/MPEG/generic packet payload programming, metadata engine double-buffering, and HDMI general-control AVMUTE behavior.
- Diagnostics and validation: digital output CRC, test patterns, random patterns, FIFO status/calibration, HDMI packet error status, and metadata missed status.

## Risks And Edge Cases

- These constants are hardware ABI. A wrong shift, wrong mask, stale generated value, or mismatch with `dcn_2_0_0_offset.h` can compile successfully while programming the wrong bit in display hardware.
- The chunk boundary is not semantic. It starts in the middle of `DP_AUX0_AUX_INTERRUPT_CONTROL`, so the full interrupt-control field set requires the previous chunk. It ends after `DIG0_AFMT_GENERIC_0`, while later generic packet payload registers and additional DIG instances continue outside this range.
- AUX instances are repetitive. `DP_AUX1` through `DP_AUX5` are near-identical macro families, and many consumers use `DP_AUX0` field names with instance-specific offsets. An instance mismatch can route a transaction to the wrong AUX engine or read the wrong connector's sideband status.
- AUX status/error handling is timing-sensitive. Timeout, overflow, HPD disconnect, invalid sync/start/stop, partial byte, NACK, CP IRQ, and reply-byte-count fields drive recovery decisions. Misinterpreting them can cause failed EDID/DPCD reads, link-training failures, or bad retry behavior.
- Ack and clear fields can have side effects. `*_ACK`, `*_CLEAR`, `*_RESET`, `*_GO`, `*_DONE_USING_AUX_REG`, and similar fields should not be touched by generic read-modify-write code unless the driver intends the side effect.
- DPHY timing masks are protocol-critical. Bad AUX precharge, start/receive window, timeout multiplier, detection threshold, or phase-detect settings can make AUX unreliable only on specific monitors, cables, bit rates, power states, or HPD timing windows.
- GTC sync fields are synchronization-critical. Incorrect lock acquisition, maintenance period, interval reset, threshold, retry, and ack handling can break synchronization or hide real link timing faults.
- HDMI packet scheduling is frame/line-sensitive. Wrong generic packet line, infoframe line, VBI packet send/continuous flags, or double-buffer handling can produce missing audio/infoframes, stale metadata, or compliance failures.
- HDMI deep color, scrambling, TMDS encoding, and clock-channel-rate fields affect sink interoperability. Incorrect settings can produce black screens, link errors, color format mismatches, or unstable HDMI 2.x-style operation.
- AFMT and audio packet fields are externally visible. Bad channel enable/layout, ACR source/N-multiple, HBR override, 60958 override, or packets-per-line settings can cause no audio, wrong channel mapping, dropouts, or sink audio-format rejection.
- Diagnostic and test-pattern fields can disturb normal output if left enabled. CRC, static/random test patterns, FIFO override/recalibration, and output test paths should be isolated to debug or validation flows.
- Full-byte payload fields are densely packed. Packet header/payload programming must preserve byte order and checksum expectations; masks alone do not validate HDMI/CEA packet semantics.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Build AMDGPU/DC with DCN20 support enabled so missing or renamed masks fail in DCN20 resource, AUX, stream encoder, IRQ, GPIO, DMUB, and clock-manager paths.
- Static generated-header checks that every `__SHIFT` has a corresponding `_MASK`, masks align with shifts, and repeated `DP_AUX1` through `DP_AUX5` layouts remain consistent with `DP_AUX0` where hardware expects shared field layouts.
- Diff checks against the authoritative DCN 2.0 register database and `dcn_2_0_0_offset.h`, especially around this chunk's beginning and ending boundaries.
- DP/eDP AUX tests: EDID reads, DPCD reads/writes, link training, retry paths, HPD disconnect during AUX, timeout/overflow handling, CP IRQ handling, and suspend/resume or runtime power transitions.
- AUX PHY timing tests across varied displays, cables, and power states, watching for intermittent AUX timeout, invalid start/stop/sync, NACK, and reply-byte-count anomalies.
- GTC sync validation on hardware paths that use AUX GTC synchronization: lock acquisition, lock loss, error thresholds, retry behavior, and interrupt/ack delivery.
- HDMI modeset tests across TMDS encoding/color formats, deep-color depths, scrambling enabled/disabled paths, clock-channel-rate changes, and high-bandwidth modes.
- HDMI packet tests for AVI/audio/MPEG/generic/infoframe metadata, line scheduling, continuous/send behavior, checksums, ISRC payloads, and metadata missed status.
- HDMI audio tests for 2-channel and multichannel layouts, channel-enable masks, HBR, 60958 override behavior, ACR generation, and audio stability over modesets and hotplug cycles.
- Double-buffer tests that verify `HDMI_DB_*`, `VUPDATE_DB_*`, and `METADATA_DB_*` pending/taken/clear behavior drains as expected and does not expose stale or partially updated metadata.
- Diagnostic tests using DIG output CRC, test patterns, FIFO status/error ack, HDMI packet error status, and metadata missed status, with confirmation that debug features are disabled after use.

## Cross-Chunk Notes

This source slice starts after the `DP_AUX0_AUX_INTERRUPT_CONTROL` register comment and after some of that register's earlier fields. It should be merged with the previous chunk for a complete `DP_AUX0` interrupt-control description. It ends immediately after the first `DIG0_AFMT_GENERIC_0` payload byte register, so the final per-file report should merge later chunks before describing the full DIG0 generic packet payload space and additional digital stream-encoder instances.

### subset-b-001626: lines 39692-42127

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 39692-42127

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register field metadata. It contains only C preprocessor constants: `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` definitions. There are no functions, structs, enums, variables, allocation paths, locks, or executable control flow.

The range covers a display I/O section of the DCN 2.0 mask header:

- The tail of the `DIG0` stream encoder/audio formatter/TMDS field definitions, starting inside `DIG0_AFMT_GENERIC_1`.
- The complete `DP0` DisplayPort field block.
- The complete `DIG1` stream encoder/audio formatter/TMDS field block.
- The first part of the `DP1` DisplayPort field block, ending inside `DP1_DP_MSE_SAT2_STATUS`.

This file lives under a local `ceph-client` source mirror, but this header is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior, distributed storage state, or client-side filesystem logic.

The macros in this chunk provide bit positions and positioned masks for HDMI/AFMT audio and packet generation, DIG front-end/back-end control, TMDS output controls, DisplayPort link setup, DP stream timing, DP DPHY training and diagnostics, DP secondary-data packets, DP audio timing, DP MST/MSE virtual-channel allocation, DP MSO controls, DSC enablement, metadata packet transmission, ALPM, and selected status/readback surfaces.

## Important APIs, Types, And Macro Families

There are no callable APIs or C types in this range. The public interface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives the low bit index of a hardware field.
- `REGISTER__FIELD_MASK` gives the already-positioned mask for that field.

The `DIG0` tail covers HDMI/AFMT and TMDS fields for stream encoder 0. Important families include:

- `DIG0_AFMT_GENERIC_1` through `DIG0_AFMT_GENERIC_7`, which pack bytes 4-31 of generic HDMI/AFMT packets.
- `DIG0_HDMI_GENERIC_PACKET_CONTROL1`, `DIG0_HDMI_GENERIC_PACKET_CONTROL5`, and `DIG0_AFMT_VBI_PACKET_CONTROL1`, which control generic packet line selection, continue/send/update behavior, frame update, and packet-indexed VBI behavior.
- `DIG0_HDMI_ACR_32_*`, `DIG0_HDMI_ACR_44_*`, `DIG0_HDMI_ACR_48_*`, and `DIG0_HDMI_ACR_STATUS_*`, which expose CTS/N values and readback fields for HDMI audio clock regeneration.
- `DIG0_AFMT_AUDIO_INFO*`, `DIG0_AFMT_60958_*`, `DIG0_AFMT_AUDIO_PACKET_CONTROL`, `DIG0_AFMT_AUDIO_SRC_CONTROL`, `DIG0_AFMT_AUDIO_CRC_*`, `DIG0_AFMT_RAMP_CONTROL*`, and `DIG0_AFMT_STATUS`, which describe HDMI/DP audio infoframes, IEC 60958 channel-status words, audio packet/sample/channel controls, test ramp generation, CRC diagnostics, and audio enable/layout state.
- `DIG0_DIG_BE_CNTL`, `DIG0_DIG_BE_EN_CNTL`, `DIG0_DIG_VERSION`, `DIG0_DIG_LANE_ENABLE`, `DIG0_AFMT_CNTL`, and `DIG0_FORCE_DIG_DISABLE`, which describe stream encoder back-end routing, enablement, mode/source selection, DIO output disable, lane enables, AFMT audio clocking, and force-disable behavior.
- `DIG0_TMDS_*`, which describe TMDS control characters, control-bit generation, DC balancer programming, sync/DC-balance characters, stereosync selection, and per-control-symbol generation settings.

The `DP0` block is complete in this chunk. It includes:

- Link and stream controls: `DP0_DP_LINK_CNTL`, `DP0_DP_CONFIG`, `DP0_DP_VID_STREAM_CNTL`, `DP0_DP_LINK_FRAMING_CNTL`, `DP0_DP_PIXEL_FORMAT`, `DP0_DP_MSA_COLORIMETRY`, `DP0_DP_MSA_MISC`, `DP0_DP_VID_TIMING`, `DP0_DP_VID_N`, `DP0_DP_VID_M`, `DP0_DP_VID_MSA_VBID`, and `DP0_DP_MSA_VBID_MISC`.
- DPHY training and diagnostics: `DP0_DP_DPHY_CNTL`, training pattern selection, symbol registers, 8b/10b control, PRBS, scrambler, CRC enable/control/result, MST CRC, fast-training controls/status, BS/SR swap controls, and HBR2 pattern control.
- Secondary-data and audio transport: `DP0_DP_SEC_CNTL`, `DP0_DP_SEC_CNTL1` through `DP0_DP_SEC_CNTL7`, `DP0_DP_SEC_FRAMING1` through `DP0_DP_SEC_FRAMING4`, `DP0_DP_SEC_AUD_N`, `DP0_DP_SEC_AUD_M`, readback registers, timestamp mode, packet control, and metadata transmission.
- MST/MSE/MSO allocation and status: `DP0_DP_MSE_RATE_CNTL`, `DP0_DP_MSE_RATE_UPDATE`, `DP0_DP_MSE_SAT0` through `SAT2`, `DP0_DP_MSE_SAT_UPDATE`, `DP0_DP_MSE_LINK_TIMING`, `DP0_DP_MSE_MISC_CNTL`, `DP0_DP_MSE_SAT*_STATUS`, `DP0_DP_MSO_CNTL`, and `DP0_DP_MSO_CNTL1`.
- Compression, double-buffer, and low-power controls: `DP0_DP_DSC_CNTL`, `DP0_DP_DSC_BYTES_PER_PIXEL`, `DP0_DP_DB_CNTL`, and `DP0_DP_ALPM_CNTL`.

The `DIG1` block repeats the stream encoder/audio formatter/TMDS layout for instance 1 and is complete in this range. It starts at `DIG1_DIG_FE_CNTL`, includes output CRC, clock/test/random pattern controls, FIFO status, HDMI packet/audio/ACR/infoframe/generic controls, metadata and DME controls, AFMT MPEG/generic/audio/60958/CRC/ramp/status controls, DIG back-end controls, TMDS controls, version/lane enable, AFMT VBI controls, and force-disable.

The `DP1` block repeats the `DP0` DisplayPort layout for instance 1 but is partial here. This chunk includes link, pixel/MSA, stream, DPHY, secondary-data, audio, MSE allocation, and MSE status fields through `DP1_DP_MSE_SAT2_STATUS`; `DP1_DP_MSA_TIMING_PARAM1` and later DP1 fields continue after the requested line range.

## Control Flow And Data Flow

The header has no runtime control flow. Its effective data flow is compile-time macro substitution:

1. DCN 2.0 display code includes `dcn_2_0_0_offset.h` for register addresses and `dcn_2_0_0_sh_mask.h` for field layouts.
2. Resource and block headers use generated table macros such as `SE_SF()` and `LE_SF()` to copy `__SHIFT` and `_MASK` constants into per-block shift/mask structures.
3. Runtime code uses `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, `REG_READ`, `REG_WRITE`, or SOC15 register helpers to compose or decode the fields.
4. Hardware interprets the resulting register values as stream encoder, link encoder, audio packet, DP link, MST, metadata, DSC, timing, diagnostic, or low-power state.

Representative local consumers show this pattern. `display/dc/dio/dcn10/dcn10_stream_encoder.h` maps many fields from this chunk into the stream encoder register/mask tables, including AFMT generic packet bytes, HDMI ACR values, DP pixel format, DP MSA timing, DP MSE rate/update, DP secondary-data controls, DP audio N/M readbacks, and HDMI/AFMT audio controls. `display/dc/dio/dcn10/dcn10_link_encoder.h` maps DP link encoder fields such as `DIG_BE_CNTL`, `TMDS_CTL_BITS`, `DP_DPHY_*`, `DP_LINK_CNTL`, `DP_LINK_FRAMING_CNTL`, `DP_MSE_SAT*`, `DP_MSE_SAT_UPDATE`, `DP_SEC_CNTL`, and `DP_VID_STREAM_CNTL`. `display/dc/resource/dcn20/dcn20_resource.c` includes the DCN 2.0 generated headers and instantiates the shift/mask tables used by DCN20 resources.

The chunk also aligns with older DCE/DCE10-style direct uses in this tree. For example, DCE HDMI audio code uses `HDMI_ACR_32_0__HDMI_ACR_CTS_32__SHIFT` and related ACR fields to program HDMI N/CTS values, while DCN link encoder code uses the `DP_MSE_SAT*` and `DP_MSE_SAT_UPDATE` fields to program DP MST stream allocation tables and wait for the SAT update/keepout status to clear.

## State And Persistence Behavior

This file stores no software state and persists nothing itself. The constants describe state held in DCN 2.0 display hardware registers. That hardware state can persist until modeset, link retraining, audio reconfiguration, MST payload update, suspend/resume restore, power-gating transition, GPU reset, firmware action, or an explicit register write changes it.

State represented by this chunk includes:

- HDMI/AFMT packet state: generic packet payload bytes, packet header bytes, packet send/update/continue controls, metadata packet controls, infoframe controls, VBI packet controls, and double-buffer status bits.
- Audio state: HDMI ACR CTS/N programming and status readback, AFMT audio infoframe payload, IEC 60958 channel-status values, audio layout/channel/sample controls, audio source selection, CRC/test-ramp controls, and audio enable/status bits.
- Stream encoder and TMDS state: DIG source/backend selection, enable bits, lane enables, force-disable flags, TMDS control characters, TMDS control symbols, DC balancer configuration, sync characters, and test/CRC/pattern controls.
- DisplayPort link and stream state: lane count, enhanced framing, link training complete, stream enable, pixel encoding/depth, MSA timing/colorimetry/misc/VBID values, video timing, M/N values, FIFO steering, and DP double-buffer controls.
- DisplayPort PHY state: DPHY reset/bypass/test selections, training patterns, programmed symbols, PRBS and scrambler controls, CRC selection/results, MST CRC status, fast-training status, HBR2 pattern selection, and BS/SR swap state.
- DisplayPort secondary-data and audio state: SDP stream/ASP/ATP/AIP/ACM/GSP/MPG enables, send/pending/deadline flags, line references and line numbers, packet framing widths, audio N/M/readback, timestamp mode, audio packet coding/version/channel-count fields, and metadata transmission line/enable fields.
- MST/MSO/DSC/ALPM state: MSE rate numerator/denominator, SAT source/slot count rows and status readbacks, SAT update and 16-MTP keepout state, MSO per-SST-link enables, DSC mode/bytes-per-pixel fields, and ALPM enable/timing controls.

Some fields are durable configuration bits; others are live status bits, readback counters, update-pending bits, self-clearing command bits, sticky error/status bits, or write-one-to-clear acknowledgements. The header does not encode access type or reset value, so callers must rely on hardware documentation and existing block helpers when deciding whether read-modify-write is safe.

## Dependencies And Integration Points

This chunk depends on the generated AMD DCN 2.0 ASIC register set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h` supplies the matching `mm...` register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/soc15/navi10_ip_offset.h` and related base helpers supply the IP segment bases used with the offsets.
- AMD display register helper layers provide `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `SE_SF`, `LE_SF`, `SRI`, and related table-building macros.

Direct include points for `dcn_2_0_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

Practical integration points are DRM/KMS stream encoder setup, HDMI mode programming, HDMI/DP audio enablement, infoframe and generic metadata packet transmission, DP link training, DP stream enable/disable, DP MST virtual-channel payload programming, DP MSO configuration, DP DSC setup, ALPM, link diagnostics/CRC, stream encoder output CRC, force-disable/recovery paths, hotplug-driven modesets, suspend/resume state restoration, and debug register snapshots.

## Risks And Edge Cases

- A wrong shift or mask can compile cleanly while corrupting the wrong hardware bit. In this chunk that can break HDMI audio clocking, infoframes, DP stream timing, link training, MST payload allocation, DSC/MSO setup, ALPM, metadata packets, or diagnostic readback.
- The chunk boundaries are artificial. The first line is inside `DIG0_AFMT_GENERIC_1` and the last line is inside `DP1_DP_MSE_SAT2_STATUS`; the final per-file report must merge adjacent chunks before claiming complete `DIG0` or `DP1` coverage.
- `DIG0`/`DIG1` and `DP0`/`DP1` are repeated instance blocks. Copy or generator drift can affect one connector/stream instance while the other continues to work, so validation must cover more than instance 0.
- Status and command fields require careful semantics. `*_SEND_PENDING`, `*_SEND_DEADLINE_MISSED`, `*_UPDATE_PENDING`, `DP_MSE_SAT_UPDATE`, `DP_MSE_16_MTP_KEEPOUT`, CRC done/result fields, fast-training status, DB pending/taken fields, and force-disable controls should not be treated as ordinary read/write storage.
- Audio fields are tightly packed. Incorrect ACR CTS/N, 60958 channel-status, audio layout, channel enable, sample-send, or source-selection masks can produce silent audio, drift, wrong channel mapping, or failures only for specific sample rates.
- DP MST fields are sequencing-sensitive. SAT source/slot rows must be programmed consistently, then committed through `DP_MSE_SAT_UPDATE`, and software must wait for update and keepout status before depending on the allocation. Bad masks here can produce bandwidth allocation failures that only appear with MST docks or multi-stream displays.
- DP MSA/timing fields are display-critical. Incorrect horizontal/vertical total/start/sync/active width, polarity, pixel format, M/N, or VBID masks can cause black screens, unstable timing, wrong color depth, or receiver-side link errors.
- TMDS and HDMI packet controls interact with link mode. Bad TMDS control/DC-balance/encoding or HDMI deep-color/scrambling/infoframe fields can cause HDMI-only failures, especially at high pixel clocks or deep-color modes.
- Some fields are present for diagnostics or test modes, including PRBS, CRC, random/test pattern, ramp, and HBR2 pattern controls. Accidentally enabling them through wrong masks can disrupt normal scanout or link training.

## Test Signals

Useful validation combines generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU/DC with DCN 2.0 support enabled. Missing or renamed macros should fail in DCN20 resource, stream encoder, link encoder, DMUB, IRQ, GPIO, clock-manager, and GMC/DC integration paths.
- Diff every `__SHIFT`/`_MASK` pair in this range against AMD's authoritative DCN 2.0 register database or a known-good upstream header. Check that masks fit 32-bit registers and match the bit widths implied by the field names.
- Exercise both stream/link instances represented here: HDMI and DP modes on ports using DIG0/DP0 and DIG1/DP1, including hotplug, modeset, blank/unblank, suspend/resume, and GPU reset restore.
- Validate HDMI/AFMT behavior with AVI/audio infoframes, generic packets, metadata packets, ACR generation at 32/44.1/48 kHz families, IEC 60958 channel status, multi-channel audio, audio CRC/status readback, and high-clock TMDS modes.
- Validate DP link behavior with lane-count changes, link training patterns, enhanced framing, scrambler/PRBS paths where testable, stream enable/disable, pixel format/depth changes, MSA timing, M/N values, and DPHY CRC/debug readback.
- Validate MST/MSO paths with MST hubs or docks: SAT source/slot programming, SAT update completion, 16-MTP keepout handling, MSE rate programming, MSE status readback, per-stream allocation changes, and teardown/reallocation.
- Validate DSC and ALPM where supported by hardware and sink capabilities, including DSC enable/disable, bytes-per-pixel programming, metadata transmission, low-power transitions, and link recovery.
- Monitor negative signals in kernel logs and user-visible behavior: black screens, flicker, bad color depth, missed vblank or page-flip completion, DP link-training failure, MST allocation failure, no HDMI/DP audio, audio drift/channel-map errors, malformed infoframes, AUX/HPD recovery loops, interrupt storms, CRC mismatches, or resume-only display failures.

## Cross-Chunk Notes

Adjacent chunks are required for the final per-file research document. Earlier lines define the start of the `DIG0` stream encoder block and `DIG0_AFMT_GENERIC_0`; later lines complete `DP1` with MSA timing, MSO, DSC, secondary-data, double-buffer, metadata, and ALPM fields before moving on to later DIG/DP instances. This chunk should be reconciled as a DIO/DIG/DP field-layout slice, not as an independently complete hardware block.

### subset-b-001627: lines 42128-44549

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 42128-44549

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register bitfield metadata. It contains no executable C logic. Its purpose is to publish compile-time `__SHIFT` and `_MASK` constants used by AMDGPU display-core register helpers to pack, update, and read fields inside MMIO registers.

The file is under a local `ceph-client` source mirror, but this path is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The range contains 2,166 macros: 1,083 field shifts and 1,083 matching masks. The chunk starts at the tail of the DP1 DisplayPort block, covers the full DIG2/DP2 instance pair, and enters the DIG3 block:

- `DP1_DP_MSA_TIMING_PARAM*`, `DP1_DP_MSO_*`, `DP1_DP_DSC_*`, `DP1_DP_SEC_*`, `DP1_DP_DB_CNTL`, `DP1_DP_MSA_VBID_MISC`, `DP1_DP_SEC_METADATA_TRANSMISSION`, `DP1_DP_DSC_BYTES_PER_PIXEL`, and `DP1_DP_ALPM_CNTL`.
- `DIG2_*` display encoder front-end/back-end, HDMI, audio formatter, generic packet, ACR, ISRC, MPEG, CRC, FIFO, TMDS, lane enable, and force-disable fields.
- `DP2_*` DisplayPort link, pixel format, MSA, stream, DPHY, CRC, secondary packet, audio timestamp, MST slot allocation, MSO, DSC, metadata, double-buffer, and ALPM fields.
- The beginning of `DIG3_*`, covering the same display encoder/HDMI/audio/TMDS families as `DIG2` through `DIG3_DIG_BE_EN_CNTL`.

Every macro follows the generated naming contract `<INSTANCE>_<REGISTER>__<FIELD>__SHIFT` or `<INSTANCE>_<REGISTER>__<FIELD>_MASK`. The corresponding register offsets are in `dcn_2_0_0_offset.h`, including `mmDP1_DP_MSO_CNTL`, `mmDIG2_DIG_FE_CNTL`, `mmDP2_DP_LINK_CNTL`, and `mmDIG3_DIG_FE_CNTL`.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or storage objects in this range. The public interface is the macro set consumed by register-table initializers and register access helpers.

Important macro families:

- DP MSA timing fields: `DP*_DP_MSA_TIMING_PARAM1` through `PARAM4` pack vertical/horizontal totals, starts, sync widths, sync polarities, active height, and active width. These fields are used when software explicitly writes DP main stream attribute timing values.
- DP MSO/DSC fields: `DP*_DP_MSO_CNTL`, `DP*_DP_MSO_CNTL1`, `DP*_DP_DSC_CNTL`, and `DP*_DP_DSC_BYTES_PER_PIXEL` describe multi-stream output link grouping, secondary-packet enable routing per SST link, DSC mode, DSC slice width, and compressed bytes-per-pixel programming.
- DP secondary packet and metadata fields: `DP*_DP_SEC_CNTL2` through `CNTL7`, `DP*_DP_SEC_METADATA_TRANSMISSION`, `DP*_DP_SEC_FRAMING*`, `DP*_DP_SEC_PACKET_CNTL`, and audio `N`/`M`/timestamp fields cover GSP packet send requests, pending/deadline status, line targeting, active/idle state, metadata packet mode, audio packet coding, and DP secondary-packet framing.
- DP link and DPHY fields: `DP2_DP_LINK_CNTL`, `DP2_DP_PIXEL_FORMAT`, `DP2_DP_CONFIG`, `DP2_DP_VID_STREAM_CNTL`, `DP2_DP_STEER_FIFO`, `DP2_DP_DPHY_*`, `DP2_DP_DPHY_CRC_*`, `DP2_DP_DPHY_FAST_TRAINING*`, `DP2_DP_MSE_*`, and `DP2_DP_ALPM_CNTL` cover training status, lane count, stream enable/deferred disable, steering FIFO status/ack/masks, training patterns, scrambler/PRBS/test symbols, CRC capture, fast training, MST slot allocation, and alternate low-power mode.
- DIG front/back end fields: `DIG[2-3]_DIG_FE_CNTL`, `DIG[2-3]_DIG_BE_CNTL`, `DIG[2-3]_DIG_BE_EN_CNTL`, `DIG[2-3]_DIG_LANE_ENABLE`, `DIG[2-3]_DIG_OUTPUT_CRC_*`, `DIG[2-3]_DIG_FIFO_STATUS`, `DIG[2-3]_DIG_TEST_PATTERN`, and `DIG[2-3]_DIG_VERSION` cover stream source select, stereo sync, digital bypass, TMDS encoding/color format, back-end enable, mode/HPD select, lane enables, output CRC, FIFO underflow/overflow, random test patterns, and version/status fields.
- HDMI packet fields: `DIG[2-3]_HDMI_METADATA_PACKET_CONTROL`, `HDMI_GENERIC_PACKET_CONTROL*`, `HDMI_CONTROL`, `HDMI_STATUS`, `HDMI_AUDIO_PACKET_CONTROL`, `HDMI_ACR_PACKET_CONTROL`, `HDMI_INFOFRAME_CONTROL*`, `HDMI_GC`, and `HDMI_DB_CONTROL` define HDMI infoframe/generic-packet send modes, ACR packet behavior, audio layout/sample controls, deep-color and YCbCr420 indications, VBI packet update state, and HDMI double-buffer controls.
- AFMT/audio fields: `DIG[2-3]_AFMT_AUDIO_PACKET_CONTROL*`, `AFMT_AUDIO_INFO*`, `AFMT_60958_*`, `AFMT_AUDIO_CRC_*`, `AFMT_RAMP_CONTROL*`, `AFMT_STATUS`, `AFMT_AUDIO_SRC_CONTROL`, `AFMT_CNTL`, and `AFMT_VBI_PACKET_CONTROL*` define audio channel enable/layout overrides, IEC 60958 channel-status words, audio infoframe payload, audio CRC/ramp test controls, FIFO overflow/ack, generic packet lock/conflict/update state, and audio source selection.
- Generic packet payload fields: `DIG[2-3]_AFMT_GENERIC_HDR` and `AFMT_GENERIC_0` through `AFMT_GENERIC_7` provide byte-level masks for generic packet header bytes and payload bytes 0 through 31. ISRC and MPEG infoframe families similarly expose byte or bitfield packing for their payloads.
- TMDS fields: `DIG[2-3]_TMDS_CNTL`, `TMDS_CONTROL_CHAR`, `TMDS_CONTROL0_FEEDBACK`, `TMDS_STEREOSYNC_CTL_SEL`, `TMDS_SYNC_CHAR_PATTERN_*`, `TMDS_CTL_BITS`, `TMDS_DCBALANCER_CONTROL`, `TMDS_SYNC_DCBALANCE_CHAR`, and `TMDS_CTL*_GEN_CNTL` describe HDMI/DVI TMDS sync/control character generation, DC balancer settings, control-bit outputs, per-control data selection/delay/invert/modulation, and feedback paths.

Consumer-side APIs are macro-driven rather than function calls:

- `SE_SF(...)` and `LE_SF(...)` in stream/link encoder headers store field shifts and masks into per-block `mask_sh` structs.
- `SRI(...)` and related register-list macros pair offsets from `dcn_2_0_0_offset.h` with these bitfield constants.
- `REG_SET`, `REG_SET_2`, `REG_SET_4`, `REG_UPDATE`, `REG_UPDATE_3`, `REG_GET`, and `REG_WAIT` use the masks/shifts to modify or poll fields without hand-written bit arithmetic.

## Control Flow

This header chunk has no internal runtime control flow. Its data flow is compile-time substitution: DCN 2.0 code includes `dcn_2_0_0_sh_mask.h`, expands the generated macro names into field masks and shifts, and then the DC register helpers use those constants during MMIO reads, writes, updates, and waits.

Representative runtime flows in local consumers:

- `display/dc/dce/dce_stream_encoder.h` and `display/dc/dio/dcn10/dcn10_stream_encoder.h` list the DIG/DP/AFMT/HDMI registers and field names consumed by stream encoder code. The chunk supplies many of the backing masks for fields such as `DP_MSA_HTOTAL`, `DP_SEC_GSP4_SEND`, `HDMI_ACR_CTS_32`, `AFMT_60958_CS_CHANNEL_NUMBER_*`, `AFMT_AUDIO_SAMPLE_SEND`, and `DIG_SOURCE_SELECT`.
- `display/dc/dio/dcn10/dcn10_stream_encoder.c` programs DP MSA timing with `REG_SET_2` and `REG_SET_4`, triggers DP secondary GSP packets through `DP_SEC_CNTL2`, waits for packet send pending state, and programs HDMI ACR `CTS`/`N` values using the masks provided here.
- `display/dc/dce/dce_stream_encoder.c` has parallel DCE stream-encoder flows for MSA timing, HDMI ACR, and AFMT/audio/infoframe programming.
- `display/dc/dio/dcn10/dcn10_link_encoder.h` maps link-encoder register fields for DP link training, stream enable, DP lane count, MSE slot allocation, DPHY training, scrambler, PRBS, HBR2 pattern, and DIG back-end enable/mode/source fields. This chunk supplies the DP2 and DIG2/DIG3 instance-specific field constants for those generic field names.
- `display/dc/dio/dcn20/dcn20_link_encoder.h` extends the link-encoder masks for DCN2 features such as FEC and lane enable, while still relying on the generated DCN2 mask/header convention used by this chunk.
- `display/dmub/src/dmub_dcn20.c`, `display/dc/resource/dcn20/dcn20_resource.c`, `display/dc/irq/dcn20/irq_service_dcn20.c`, `display/dc/gpio/dcn20/hw_factory_dcn20.c`, and `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c` include the DCN 2.0 offset and mask headers as part of DCN20 device/resource integration.

Because this file is declarative, it does not enforce required sequencing. Consumers must decide when to take update locks, program timing before stream enable, wait for packet pending bits, clear sticky status bits, avoid writing status-only fields, sequence DP link training, and coordinate HDMI/audio metadata updates with vblank or frame boundaries.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. The macros describe fields in hardware MMIO registers.

The represented hardware state includes:

- DP link and stream state: link training complete/status, eDP mode, lane count, stream enable/status, deferred disable, video timing, MSA misc/VBID, pixel encoding/depth/range, DPHY training/scrambler/PRBS/test/CRC state, fast-training status, FEC-adjacent DPHY control fields, and ALPM controls.
- DP secondary data state: audio `N`/`M` programming and readbacks, secondary timestamps, packet coding/category/channel overrides, GSP send/pending/deadline/line-number state, metadata packet enable/mode, and packet-active/idle indicators.
- MST/MSO/DSC state: MSE rate programming, slot allocation table entries and status readbacks, link timing, blank/timestamp modes, MSO SST-link mapping, DSC mode/slice width, and DSC bytes-per-pixel.
- DIG routing/encoding state: source selection, stereo sync, bypass, stream-start/symclock indicators, back-end mode and HPD selection, lane enable bits, output CRC configuration/results, test/random patterns, and FIFO status.
- HDMI state: metadata and generic packet sends, infoframe updates, audio packet control, ACR auto-send/source/priority and `CTS`/`N` values, deep color, YCbCr420, VBI state, double-buffer lock/update behavior, and HDMI status.
- AFMT/audio state: audio sample send enable, audio source selection, channel layout and channel enables, IEC 60958 channel status, audio infoframe payload, CRC/ramp test configuration/results, FIFO overflow/ack bits, generic packet payload buffers, ISRC and MPEG infoframes, and audio-clock/status fields.
- TMDS state: sync/control character patterns, control-bit generation, feedback delay/select, stereo sync select, DC balancer enable/test/force settings, and per-control signal generation.

Persistence is hardware-specific and not encoded in this file. Some fields are durable programming knobs that remain until a modeset, reset, power-gating transition, suspend/resume, or explicit rewrite. Others are read-only status, sticky interrupt/status, write-one-to-clear acknowledgements, self-clearing send/update requests, pending bits, line-number latches, CRC result fields, or double-buffered values latched at frame boundaries. Names such as `*_STATUS`, `*_ACK`, `*_CLR`, `*_PENDING`, `*_SEND`, `*_UPDATE`, `*_LOCK`, `*_DONE`, and `*_READBACK` signal possible side effects but do not define access type by themselves.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header contract:

- `dcn_2_0_0_offset.h` supplies the matching MMIO register offsets for these field masks and shifts.
- DCN/DCE enum headers and DisplayPort/HDMI/DSC protocol definitions supply legal symbolic field values.
- AMD display register helper macros in `drivers/gpu/drm/amd/display/dc` use the mask/shift structs initialized from these macros.

Direct and practical integration points include:

- Stream encoder setup for DP, HDMI, and audio formatter programming in `display/dc/dio/dcn10/dcn10_stream_encoder.*` and `display/dc/dce/dce_stream_encoder.*`.
- Link encoder setup for DP link training, DPHY, MST slot allocation, DIG back-end routing, HDMI/TMDS mode, lane enable, and hotplug-linked back-end selection in `display/dc/dio/dcn10/dcn10_link_encoder.*` and `display/dc/dio/dcn20/dcn20_link_encoder.*`.
- DCN20 resource construction in `display/dc/resource/dcn20/dcn20_resource.c`, which ties the generated offsets/masks to instantiated display resources.
- DMUB, IRQ, GPIO, and clock-manager integration that includes the DCN2 generated headers for hardware-service and display-resource operation.
- Diagnostic and validation paths that read output CRC, DPHY CRC, AFMT audio CRC, FIFO status, link status, MSE status, packet pending/deadline flags, and HDMI/AFMT status fields.

## Risks And Edge Cases

- These constants are hardware ABI. A wrong mask or shift can compile cleanly but write the wrong bits in a live display register.
- The chunk boundary is not semantic. It starts after the first two `DP1_DP_MSE_SAT2_STATUS` lines and ends after `DIG3_DIG_BE_EN_CNTL`, leaving complete DP1 context before the chunk and the rest of DIG3 after it to adjacent chunks.
- Instance repetition is easy to damage manually. `DIG2` and `DIG3` share many field layouts, while `DP1` and `DP2` share the later DP register families. One incorrect instance prefix or copied mask can affect only one physical encoder or connector path.
- DP MSA timing masks are timing-critical. Incorrect total/start/sync/active fields can cause black screens, bad link timing, incorrect sink-reported video parameters, flicker, or failed modesets.
- DP secondary packet fields have request, pending, deadline, and line-target side effects. Bad masks can leave HDR/metadata/audio packets unsent, sent on the wrong line, repeatedly pending, or reported as deadline-missed.
- MST/MSO/DSC fields are bandwidth and packetization critical. Slot-count, source, MSO link-count, DSC mode, slice-width, or bytes-per-pixel drift can produce corrupted MST streams, broken DSC output, or link bandwidth mismatches.
- HDMI ACR and AFMT fields are audio-critical. Bad `CTS`/`N`, channel status, layout, sample-send, FIFO-ack, or audio-source masks can cause silent audio, wrong channel mapping, audio drift, or FIFO overflow loops.
- Generic packet and infoframe byte masks directly shape HDMI/DP metadata payloads. Incorrect payload-byte masks can corrupt AVI, audio, HDR/generic, ISRC, or MPEG packets while leaving video otherwise functional.
- TMDS control/DC-balancer fields are encoding-critical for HDMI/DVI. Wrong bit positions can produce sink compatibility failures, intermittent display loss, or subtle link errors.
- Status/ack/clear fields are intermixed with programming fields in the same generated header. Using a `_MASK` without respecting hardware access semantics can accidentally clear sticky state or fail to acknowledge a condition.

## Test Signals

Useful validation is build coverage plus hardware/display behavior:

- Build AMDGPU/DC with DCN20 support enabled. Missing or renamed macros should fail in DCN20 stream encoder, link encoder, resource, DMUB, IRQ, GPIO, or clock-manager paths.
- Compare this generated mask range against the matching `dcn_2_0_0_offset.h` range and adjacent DCN family headers such as `dcn_2_0_1_sh_mask.h`, `dcn_2_1_0_sh_mask.h`, and `dcn_3_0_0_sh_mask.h` to catch unintended instance or field-layout drift.
- Exercise DP modesets on DCN20 hardware through the relevant DP1/DP2 paths: link training, stream enable/disable, lane-count changes, MST slot allocation, DSC where supported, MSO where supported, suspend/resume, and hotplug.
- Validate DP timing and metadata: correct MSA values at the sink, stable vblank/page flips, HDR or other GSP metadata delivery, audio over DP, no stuck `DP_SEC_*_PENDING`, and no repeated deadline-missed status.
- Exercise HDMI/DVI on DIG2/DIG3 paths: TMDS mode, deep color, YCbCr420, generic/infoframe packets, HDMI audio ACR, AFMT channel layout, audio source selection, and audio FIFO overflow recovery.
- Run diagnostic reads for output CRC, DPHY CRC, AFMT audio CRC, FIFO status, HDMI/AFMT status, MSE slot status, and link status; mismatches or stuck status bits are strong signals of mask/shift issues.
- Watch kernel logs and display behavior for black screens, flicker, failed link training, MST topology failures, DSC corruption, missed vblank/page-flip completion, audio silence or drift, EDID/hotplug instability on encoder paths, CRC mismatches, FIFO overflow messages, and suspend/resume regressions.

### subset-b-001628: lines 44550-46976

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 44550-46976

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register field metadata. It contains no executable C logic. Its purpose is to publish compile-time bit shifts and masks for DCN 2.0 digital display encoder (`DIG`) and DisplayPort (`DP`) MMIO registers so AMDGPU display code can compose, update, and decode register fields without hard-coded bit positions.

The file is under a local `ceph-client` source mirror, but this path is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The covered range is a DIO/display-decoder slice:

- Tail of `DIG3`: TMDS control/generation fields, DIG lane/audio-clock controls, AFMT generic packet update state, HDMI generic immediate-send state, and force-disable.
- Full `DP3`: DisplayPort link, video, DPHY, secondary-data/audio, MST/MSE, MSO, DSC, metadata, double-buffer, VBID, and ALPM field definitions.
- Full `DIG4`: stream encoder/front-end fields, HDMI metadata/generic/audio/infoframe/ACR/GC fields, AFMT audio and generic infoframe payload fields, back-end and TMDS fields, lane/audio controls, and force-disable.
- Full `DP4`: another repeated DisplayPort instance with the same field surface as `DP3`.
- Beginning of `DIG5`: only the first `DIG5_DIG_FE_CNTL` shifts/masks for source selection, stereo sync, start, bypass/input pixel selection, Dolby Vision state, symbol clock, and TMDS pixel/color format. The rest of `DIG5` continues in the next chunk.

Every register field appears as a pair of preprocessor definitions: `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or storage objects in this range. The public interface is the generated preprocessor naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Instance-qualified register prefixes (`DIG3`, `DP3`, `DIG4`, `DP4`, and partial `DIG5`) let common stream/link encoder code bind the same generic field names to one hardware encoder instance.

Important macro families in this chunk:

- `DIG3_TMDS_*` and `DIG4_TMDS_*`: HDMI/DVI TMDS synchronization, control characters, feedback selection/delay, stereo sync selection, sync character patterns, per-control-bit output selection/delay/invert/modulation, DC balancer controls, and 2-bit counter enable.
- `DIG3_DIG_VERSION`, `DIG3_DIG_LANE_ENABLE`, `DIG4_DIG_VERSION`, and `DIG4_DIG_LANE_ENABLE`: DIG type, lane enables, and DIG clock-enable bits used by link encoder setup and enable/disable logic.
- `DIG3_AFMT_CNTL`, `DIG4_AFMT_CNTL`, `DIG3_AFMT_VBI_PACKET_CONTROL1`, and `DIG4_AFMT_VBI_PACKET_CONTROL1`: audio formatter clock enable/status plus per-generic-packet frame/immediate update and pending bits for generic packet slots 0-7.
- `DIG3_HDMI_GENERIC_PACKET_CONTROL5` and `DIG4_HDMI_GENERIC_PACKET_CONTROL5`: immediate-send and pending bits for HDMI generic packet slots 0-7.
- `DIG4_DIG_FE_CNTL` and partial `DIG5_DIG_FE_CNTL`: stream source select, stereo sync select/gating, DIG start, bypass/input pixel selection, Dolby Vision enable/missed metadata, front-end symbol-clock status, and TMDS pixel encoding/color format.
- `DIG4_DIG_OUTPUT_CRC_*`, `DIG4_DIG_CLOCK_PATTERN`, `DIG4_DIG_TEST_PATTERN`, `DIG4_DIG_RANDOM_PATTERN_SEED`, and `DIG4_DIG_FIFO_STATUS`: output CRC, clock/test pattern, pseudo-random seed, and FIFO diagnostic fields.
- `DIG4_HDMI_*`: HDMI metadata packet line/reference/enable fields, generic packet line/send/continue controls, HDMI enable/status/deep-color/packing/scrambler settings, audio sample layout and HBR packet controls, ACR select/enable/CTS/N, VBI packet enables, AVI/audio/MPEG infoframe update controls, GC fields, and double-buffer status/clear/lock fields.
- `DIG4_AFMT_*`: audio packet/channel layout controls, ISRC fields, MPEG/HDR/generic packet header/body bytes, IEC 60958 channel status fields, ramp controls, AFMT audio CRC controls/results, AFMT status flags, generic packet control/index/conflict bits, and audio source selection.
- `DIG4_DIG_BE_CNTL` and `DIG4_DIG_BE_EN_CNTL`: back-end dual-link/swap/RB switch, front-end source selection, DIG mode, HPD select, enable, and back-end symbol-clock status.
- `DP3_*` and `DP4_*`: repeated DisplayPort instance fields covering link-training completion/status, embedded panel mode, pixel format/depth/combine, MSA colorimetry/misc/VBID/timing parameters, lane count, stream enable, steer FIFO, video timing N/M, link framing, HBR2 eye pattern, interrupts, DPHY training/test/scrambler/CRC/FEC-related diagnostics, fast training, secondary-data packet controls, audio M/N/readback/timestamp, MST/MSE rate and slot allocation, MSO, DSC mode/slice width/bytes per pixel, generic secondary packet send/line scheduling, double-buffer lock/taken/pending state, metadata transmission, and ALPM sleep/standby scheduling.

## Control Flow

This chunk has no runtime control flow. It is declarative metadata consumed by register-table construction and register helper macros such as `SRI`, `SE_SF`, `LE_SF`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`.

Representative runtime flows in local consumers:

1. DCN20 resource construction includes `dcn_2_0_0_sh_mask.h` and binds these shifts/masks into stream encoder, link encoder, clock, GPIO, IRQ, and DMUB resource tables.
2. DCE/DCN stream encoder code maps `DIG{id}` AFMT/HDMI/DIG front-end registers and `DP{id}` secondary-data registers through `SE_DCN2_REG_LIST(id)` and `SE_COMMON_MASK_SH_LIST_DCN20(mask_sh)`. `enc2_stream_encoder_update_hdmi_info_packets()` writes HDMI generic packet fields, while DSC, dynamic metadata, Dolby Vision, audio clock, GSP/PPS, and DP secondary-data helpers use the DP/DIG fields defined here.
3. Link encoder code maps back-end and DP link fields through `LINK_ENCODER_MASK_SH_LIST_DCN10(mask_sh)` and DCN20 extensions. It uses these masks for DIG enable, HPD select, DIG mode, front-end selection, TMDS clock/control bits, DPHY training/test/scrambler fields, link framing, DP stream enable, lane count, MST slot allocation, and hotplug/AUX-related setup.
4. Audio formatter and HDMI/DP audio code programs AFMT audio source, channel layout, IEC 60958 channel-status fields, DP audio secondary packets, ACR N/CTS, HBR packet enables, and audio CRC/status fields.
5. Diagnostic paths use output CRC, DPHY CRC, FIFO status, MSE status, fast-training status, double-buffer status, missed metadata, and deadline-missed/pending fields to validate or debug link and stream behavior.

Because the header only supplies constants, it does not enforce sequencing. Consumers must order operations around link training, DIG front-end/back-end routing, HDMI/DP packet memory conflicts, AFMT clock enable, DP secondary packet scheduling, DSC enablement, MST slot updates, double-buffer locks, ALPM requests, and reset/power/clock transitions.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. The macros describe hardware MMIO state.

The represented hardware state includes:

- Stream routing and front-end state: source select, stereo sync, DIG start, bypass/input pixel select, Dolby Vision enable/missed-metadata flag, symbol-clock state, and TMDS encoding/color-format state.
- Link/back-end state: DIG enable, HPD select, DIG mode, front-end source binding, lane enables, lane count, link-training completion/status, embedded-panel mode, and DP stream enable.
- HDMI/TMDS state: HDMI enable, deep color, packing phase, scrambler/clock ratio, generic packet line/send/continue/immediate flags, metadata packet scheduling, VBI/infoframe update bits, ACR parameters, audio sample/HBR controls, guard band/control period settings, and TMDS control/DC-balance/test settings.
- AFMT/audio state: audio clock enable/status, audio source/channel enables, IEC 60958 channel-status values, ISRC/MPEG/HDR/generic packet payload bytes, ramp controls, audio CRC, and audio FIFO/status flags.
- DisplayPort transport state: pixel encoding/depth/combine, MSA/VBID/timing fields, video timing N/M, link framing, DPHY training/test/scrambler/CRC/fast-training state, secondary-data packet enables and scheduling, audio M/N/timestamp/readbacks, MST MSE rates and slot allocation tables, MSO controls, DSC mode/slice/bytes-per-pixel, metadata packet line scheduling, double-buffer state, and ALPM sleep/standby requests.

Persistence is hardware-specific and not encoded here. Some fields are durable programming knobs that remain until modeset, reset, suspend/resume, link retraining, power-gating transition, or an explicit rewrite. Other fields are read-only status, sticky flags, pending bits, deadline-missed indicators, self-clearing send/update requests, write-one-to-clear controls, double-buffered latches, or line-scheduled packet triggers. Names such as `*_STATUS`, `*_PENDING`, `*_CLR`, `*_LOCK`, `*_TAKEN`, `*_DEADLINE_MISSED`, `*_READBACK`, `*_SEND`, and `*_UPDATE` hint at side effects, but access type and reset values require the hardware register specification and the matching generated offset/enum headers.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header contract for DCN 2.0. It is meaningful together with:

- `dcn_2_0_0_offset.h` for the matching MMIO register offsets and base indices.
- DCN 2.0 enum/value headers for symbolic field values.
- AMD display register helper macros and per-block register/mask/shift tables in `drivers/gpu/drm/amd/display/dc`.

Direct include points found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

Practical integration surfaces are HDMI and DisplayPort stream encoder programming, link encoder enable/link-training/MST programming, DSC PPS and bytes-per-pixel setup, Dolby Vision and dynamic metadata packet scheduling, HDMI and DP infoframe/generic packet emission, HDMI/DP audio packet and IEC 60958 programming, hotplug/routing association through DIG back-end fields, DP ALPM, and stream/link diagnostics through CRC/status/readback fields.

## Risks And Edge Cases

- Masks and shifts are hardware ABI. A one-bit error can compile cleanly but update the wrong field, causing link-training failures, black screens, bad HDMI/DP packets, corrupted audio metadata, incorrect DSC configuration, or unstable hotplug/routing behavior.
- The range is generated and highly repetitive. `DP3`/`DP4` and `DIG3`/`DIG4` instance families are easy to skew by hand; regeneration from the authoritative register database is safer than manual edits.
- The chunk boundary is not semantic. It starts after earlier `DIG3_DIG_BE_EN_CNTL` shift definitions and ends after only the first `DIG5_DIG_FE_CNTL` fields, so complete per-instance analysis requires adjacent chunks.
- Stream and link roles overlap. `DIG` front-end fields route pixel streams and metadata, while `DIG` back-end and `DP` fields drive physical/link transport. Mismatched instance IDs can bind one stream to the wrong back-end or DP link.
- Packet-control fields have pending, conflict, lock, immediate, frame-update, and line-number semantics. Updating AFMT/HDMI/DP packet memory without respecting these flags can drop HDR/Dolby/AVI/audio infoframes or race hardware packet reads.
- DP secondary-data scheduling is timing-sensitive. Wrong line references, line numbers, GSP send flags, PPS flags, or metadata packet enables can miss packet deadlines or place packets on invalid lines.
- DSC fields are display-mode critical. Wrong DSC mode, slice width, or bytes-per-pixel fields can produce blank output or decompression artifacts on DSC-capable sinks.
- MST/MSE and MSO fields are allocation-critical. Incorrect slot counts, source IDs, rate updates, link timing, or MSO segment settings can break multi-stream or multi-segment DisplayPort output.
- ALPM and DPHY training/test fields can affect link stability. Misprogramming sleep/standby requests, training patterns, scrambler state, PRBS, CRC, or HBR2 pattern fields can lead to failed training, flicker, or resume failures.
- Status, clear, reset-like, and pending bits often have side effects that are invisible in this header. Consumers must not infer access type from the mask alone.

## Test Signals

Useful validation is compile-time plus hardware/display behavior:

- Build AMDGPU/DC with DCN20 support; generated macro drift should fail in DCN20 resource construction, stream encoder, link encoder, audio, IRQ, GPIO, DMUB, or clock-manager paths.
- Compare this chunk against `dcn_2_0_0_offset.h` and adjacent DCN-family mask headers to catch instance drift, missing `DP3`/`DP4` symmetry, and unintended `DIG4`/`DIG5` field differences.
- Exercise HDMI and DP modesets on DCN20 hardware across multiple encoder instances, including hotplug, blank/unblank, suspend/resume, link retraining, and routing between front-end and back-end encoders.
- Validate HDMI infoframes and generic packets: AVI, vendor/HF-VSIF, HDR static metadata, VTEM, metadata packet line scheduling, double-buffer behavior, and packet stop/start transitions.
- Validate DisplayPort stream behavior: link training, stream enable/disable, enhanced framing, MSA/VBID values, MST slot allocation where available, MSO paths, DSC PPS/bytes-per-pixel programming, and secondary-data packet scheduling.
- Validate audio paths: HDMI ACR, DP audio M/N and timestamp packets, AFMT audio clock, channel layout, IEC 60958 channel status, HBR audio, and audio CRC/status behavior.
- Validate diagnostics and negative signals: output CRC/DPHY CRC, FIFO status, DPHY fast-training status, MSE status, metadata deadline-missed flags, AFMT generic conflict flags, kernel underflow/link-training messages, black screens, flicker, color/format mismatches, missing HDR/Dolby metadata, silent HDMI/DP audio, and resume/hotplug regressions.

### subset-b-001629: lines 46977-49385

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 46977-49385

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register field metadata. It contains preprocessor constants only: each field is represented by a `__SHIFT` macro and usually a matching `_MASK` macro. The constants are consumed by AMDGPU display-core register helpers to pack, update, read, and decode fields in DCN 2.0 display hardware registers.

The source path lives under a local `ceph-client` source mirror, but this file is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

This range starts inside the `dce_dc_dio_dig5_dispdec` address block and ends inside the HPD GPIO field list. The chunk boundary is not semantic:

- It begins at line 46977 after the first four `DIG5_DIG_FE_CNTL` shift fields already appeared in the previous chunk.
- It includes the rest of `DIG5_DIG_FE_CNTL`, the complete DIG5 HDMI/AFMT/TMDS/backend/display-output-control field groups, the complete DP5 DisplayPort stream/PHY/secondary-data field groups, DCIO global/link/power/backlight field groups, and most GPIO/DDC/GENLK/HPD field groups.
- It ends at line 49385 after the `DC_GPIO_HPD_EN` shift fields and before the matching `DC_GPIO_HPD_EN` mask fields, which continue in the next chunk.

The represented hardware surface is the sixth DIO/DIG instance (`DIG5` and `DP5`) plus shared DCIO and GPIO blocks. In display-core terms these fields cover one link encoder/stream encoder instance and the supporting physical link, DisplayPort packetization, HDMI packet/audio formatter, UNIPHY routing, panel/backlight sequencing, DDC/AUX pad behavior, and hotplug/general-purpose GPIO control.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, variables, callbacks, or storage objects in this range. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low-bit position of a register field.
- `<REGISTER>__<FIELD>_MASK` gives the bitmask used by `REG_SET`, `REG_UPDATE`, `REG_GET`, `LE_SF`, `SF_DDC`, `SF_HPD`, and related generated-table helpers.
- Register address macros live in the matching `dcn_2_0_0_offset.h`; this file supplies the field-level metadata.

Important macro families in this chunk:

- `DIG5_DIG_FE_CNTL`, `DIG5_DIG_OUTPUT_CRC_*`, `DIG5_DIG_CLOCK_PATTERN`, `DIG5_DIG_TEST_PATTERN`, `DIG5_DIG_RANDOM_PATTERN_SEED`, and `DIG5_DIG_FIFO_STATUS`: DIG5 front-end source routing, stereo sync, start/bypass/pixel selection, Dolby Vision flags, TMDS encoding/color-format fields, output CRC control/result, test pattern generation, random pattern seed, and FIFO status/calibration/error fields.
- `DIG5_HDMI_*`: HDMI metadata packet control, generic packet line controls, core HDMI control/status, audio packet control, ACR packet control/status for 32/44/48 kHz families, VBI packets, infoframe controls, generic packet controls, gamut/control packet data, HDMI debug/DB control, and DME metadata control.
- `DIG5_AFMT_*`: audio formatter fields for IEC 60958 channel status words, audio infoframe and MPEG infoframe payload fields, ISRC packet payloads, generic HDR/generic packet payloads, audio CRC control/result, ramp/test audio controls, audio status, packet control, VBI generic-packet conflict/index controls, infoframe source/update controls, and audio source selection.
- `DIG5_DIG_BE_*` and `DIG5_TMDS_*`: DIG5 backend enable, dual-link/swap/interlace/control flags, TMDS control-character, feedback, stereo-sync, sync-character, control-bit, DC-balancer, and control-bit generator fields.
- `DIG5_DIG_VERSION`, `DIG5_DIG_LANE_ENABLE`, `DIG5_AFMT_CNTL`, `DIG5_AFMT_VBI_PACKET_CONTROL1`, `DIG5_HDMI_GENERIC_PACKET_CONTROL5`, and `DIG5_FORCE_DIG_DISABLE`: version/lane clock enable, AFMT enable/status, larger generic-packet line/control groups, and force-disable fields.
- `DP5_DP_*`: DisplayPort link control, pixel format, MSA colorimetry/misc/timing/VBID fields, stream control, steering FIFO setup, video timing/N/M values, link framing, HBR2 eye pattern, video interrupt controls, DPHY control/training/symbol/8b10b/PRBS/scrambler/CRC/fast-training fields, secondary-data packet/audio/timestamp/framing controls, MST/MSE rate and slot-allocation tables, MSO control, DSC control and bytes-per-pixel, DP debug/DB controls, metadata transmission, ALPM sleep/standby fields, and security/secondary stream control registers through `DP5_DP_SEC_CNTL7`.
- `DC_GENERICA`, `DC_GENERICB`, and `DC_REF_CLK_CNTL`: generic DC pin or scratch-style controls and reference-clock source controls.
- `UNIPHYA` through `UNIPHYF`: per-UNIPHY link enable, HPD mask, lane stagger, channel crossbar source, and lane inversion fields. These are the physical transmitter routing controls used by link encoder code.
- `DCIO_WRCMD_DELAY`, `DC_PINSTRAPS`, `LVTMA_PWRSEQ_*`, `BL_PWM_*`, and `BL_PWM_GRP1_REG_LOCK`: write-command delay, strap readout, LVTM/eDP-style panel power sequence control/state/delays/reference divider, backlight PWM enable/debug/period/group lock fields.
- `DCIO_GSL_*`, `DCIO_CLOCK_CNTL`, and `DCIO_SOFT_RESET`: genlock/swaplock pad controls, clock enable fields, and soft reset bits for AUX, I2C, DIG, SYMCLK, and UNIPHY blocks.
- `DC_GPIO_GENERIC_*`: generic GPIO mask, output value (`A`), output enable (`EN`), and input/readback (`Y`) fields for generic pins A through G, plus receive, pull, mask, and mux selector fields.
- `DC_GPIO_DDC1_*` through `DC_GPIO_DDC6_*` and `DC_GPIO_DDCVGA_*`: DDC/AUX GPIO mask, output, enable, and input fields for six DDC pads and VGA DDC. Mask registers include CLK/DATA mask bits, pull-down enables, receiver state fields, AUX pad mode, polarity, hardware pull-down allowance, and drive strength fields.
- `DC_GPIO_GENLK_*`: genlock clock, genlock vsync, and swaplock A/B mask/output/enable/input fields.
- `DC_GPIO_HPD_MASK`, `DC_GPIO_HPD_A`, and the shift half of `DC_GPIO_HPD_EN`: HPD1 through HPD6 masking, pull disable, receive status, output values, and enable/schmitt/slew/spare/selector controls. The HPD enable masks begin immediately after this chunk.

## Control Flow

This chunk has no runtime control flow. It is declarative register-field metadata used by display driver code at compile time.

Runtime control flow appears in consumers that combine these field macros with register offsets and typed register tables:

- Link encoder setup uses `display/dc/dio/dcn20/dcn20_link_encoder.h` macros such as `LINK_ENCODER_MASK_SH_LIST_DCN20`, `UNIPHY_MASK_SH_LIST`, `DPCS_DCN2_MASK_SH_LIST`, and `UNIPHY_DCN2_REG_LIST`. Those lists reference fields from this chunk for DIG lane enable, TMDS control bits, UNIPHY channel crossbar/link enable, and `DCIO_SOFT_RESET` reset bits.
- DCN20 link encoder implementation programs DIG/DP/UNIPHY state while mapping BIOS transmitter objects such as `TRANSMITTER_UNIPHY_A` through `TRANSMITTER_UNIPHY_F/G` to hardware blocks. The masks here make those read-modify-write operations target the intended fields.
- DDC GPIO setup uses `display/dc/gpio/ddc_regs.h`. `DDC_GPIO_REG_LIST_ENTRY`, `DDC_REG_LIST_DCN2`, and `DDC_MASK_SH_LIST_DCN2` combine `DC_GPIO_DDCx_MASK/A/EN/Y` masks from this chunk with DDC setup and AUX pad control registers to build GPIO/DDC descriptors.
- HPD GPIO setup uses `display/dc/gpio/hpd_regs.h`. `HPD_GPIO_REG_LIST_ENTRY`, `HPD_REG_LIST`, and `HPD_MASK_SH_LIST` consume `DC_GPIO_HPD_MASK/A/EN/Y` fields to expose hotplug GPIO state and interrupt filtering to the HPD service path.
- Resource construction in DCN20 display code includes the generated offset and mask headers to populate per-block register structures. Later modeset, hotplug, audio, DP link-training, HDMI infoframe, and debug/CRC paths use those structures through `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, and field-list macros.

Because this header only supplies constants, it does not enforce sequencing. Consumers must provide the ordering around link disable/enable, HPD masking, DDC pad switching between I2C and AUX, DP link training, DP secondary-data programming, HDMI/AFMT packet updates, FIFO/error acknowledgment, panel power sequencing, PWM updates, and soft-reset assertion/deassertion.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. The macros describe hardware MMIO state.

Hardware state represented by these fields includes:

- DIG5 front-end/backend routing, enablement, lane-clock state, FIFO status, and CRC/test-pattern state.
- HDMI packet-generation state, including metadata, infoframes, generic packets, ACR, VBI, audio packet limits, deep color, scramble, keepout, error status, and debug/DB controls.
- AFMT audio packet state, IEC 60958 channel-status fields, audio test/ramp/CRC state, audio enable/status, high-bit-rate status, FIFO overflow indicators, and generic packet lock/conflict status.
- TMDS encoding and balancing state for HDMI/DVI-style signaling.
- DP5 stream configuration, MSA fields, MST/MSE slot allocation, secondary-data/audio packet framing, PHY training and CRC diagnostics, PRBS/scrambler controls, FEC/DSC-related state where present, metadata transmission, MSO, and ALPM low-power link state.
- UNIPHY channel routing and link enable state for physical transmitters A through F.
- DCIO clock and reset state for AUX, I2C, DIG, SYMCLK, and UNIPHY blocks.
- Panel/backlight state in LVTM power sequencing and PWM controls.
- GPIO state for generic pins, DDC/AUX pads, VGA DDC, genlock/swaplock, and HPD pins.

Persistence is hardware-defined rather than encoded in this file. Some fields are durable programming knobs that remain until a modeset, hotplug reconfiguration, suspend/resume, power-gating transition, reset, or explicit rewrite. Other fields are read-only status, sticky status, write-one-to-clear acknowledgments, self-clearing requests, latched counters, or debug/test controls. Names such as `*_STATUS`, `*_ACK`, `*_INT`, `*_ERROR`, `*_RESET`, `*_SEND`, `*_PENDING`, `*_UPDATE`, `*_MASK`, and `*_LOCK` identify likely side effects, but the exact access type and reset value require the hardware register specification and the consumers' access patterns.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header contract for DCN 2.0. It is meaningful together with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h` for register addresses and base indices.
- Adjacent chunks of `dcn_2_0_0_sh_mask.h`, because this range starts and ends inside register-field groups.
- AMD display register helper macros and generated field-list helpers in `drivers/gpu/drm/amd/display/dc`.
- DCN20 resource, link encoder, stream encoder, GPIO, IRQ, DMUB, clock-manager, and hardware sequencer code that includes the generated headers.

Direct or practical integration points visible in this tree include:

- `display/dmub/src/dmub_dcn20.c`, which includes `dcn/dcn_2_0_0_sh_mask.h` for DMUB/DCN20 register operations.
- `display/dc/dio/dcn20/dcn20_link_encoder.h` and `display/dc/dio/dcn20/dcn20_link_encoder.c`, which use DIG lane, TMDS, UNIPHY, DPCS, AUX, and soft-reset fields for physical link control.
- `display/dc/gpio/ddc_regs.h` and `display/dc/gpio/hpd_regs.h`, which turn the DDC and HPD GPIO macros into typed register/mask tables.
- `display/dc/gpio/dcn20/hw_factory_dcn20.c`, which instantiates GPIO objects for DCN20 hardware.
- `display/dc/resource/dcn20/dcn20_resource.c`, which builds the DCN20 resource pool and register maps.
- `display/dc/hwss/dcn20/dcn20_hwseq.c`, `display/dc/link/link_dpms.c`, and common link code, which use transmitter/UNIPHY indices during power sequencing and link enablement.

The important cross-file contract is that field names in this mask header must match the symbolic field names expected by `LE_SF`, `SF_DDC`, `SF_HPD`, stream-encoder tables, and generic `REG_*` helper call sites. A field rename or value drift breaks either the build or the target hardware programming.

## Risks And Edge Cases

- This is hardware ABI data. A wrong shift or mask can compile cleanly while causing a read-modify-write to touch the wrong bit, leave stale bits set, or clear an unrelated status/control field.
- The chunk boundary is partial at both ends. `DIG5_DIG_FE_CNTL` is missing its first four shift definitions in this chunk, and `DC_GPIO_HPD_EN` is missing all mask definitions. Merge/reconciliation must combine adjacent chunks for complete per-register analysis.
- DIG5 and DP5 are instance-specific copies of repetitive DIO/DIG/DP blocks. Copy/paste drift from other instances can affect only the sixth display link, making failures connector- or board-dependent.
- HDMI/AFMT fields have many send/continuous/update/source bits. Incorrect masks can produce missing audio, incorrect ACR/N/M behavior, invalid infoframes, HDR metadata loss, generic-packet conflicts, or HDMI compliance failures.
- DP secondary-data and MSE/MSO fields are packetization-critical. Bad fields can break MST allocation, audio timestamps, metadata packets, DSC/MSO modes, or secondary-data framing without obvious compile-time failures.
- DPHY/training/CRC fields are link-critical. Wrong training pattern, scrambler, PRBS, fast-training, CRC, or ALPM masks can cause link-training failures, intermittent display loss, CRC mismatches, or low-power link exit failures.
- `DCIO_SOFT_RESET` fields control many shared blocks. An incorrect mask can reset the wrong AUX/I2C/DIG/SYMCLK/UNIPHY instance or fail to reset a stuck block, producing hard-to-debug hotplug or modeset failures.
- DDC/AUX pad mode and pull/drive-strength fields affect external electrical interfaces. Bad programming can cause EDID read failures, AUX/I2C contention, HPD flapping, signal-integrity problems, or failure to detect a display.
- HPD fields are split across this and the next chunk. Using only the visible shift half of `DC_GPIO_HPD_EN` without the corresponding masks would be incomplete for generated register tables.
- Status and acknowledgment fields such as FIFO errors, HDMI errors, AFMT overflow/change flags, DP CRC done/status, fast-training status, and metadata-missed flags may be sticky or write-one-to-clear; generic read/write code must avoid accidental clears.
- Backlight and panel-power fields are platform-visible. Incorrect LVTMA power-sequence or PWM masks can cause panel blanking, brightness failures, resume flicker, or delayed power-on/off behavior.

## Test Signals

Useful validation is a combination of compile-time checks and hardware behavior on DCN20-class systems:

- Build AMDGPU/DC with DCN20 enabled. Missing or renamed fields should fail in link encoder, GPIO/DDC/HPD, resource, DMUB, clock, and stream-encoder code paths.
- Diff generated shifts/masks against adjacent instances (`DIG0` through `DIG4`, `DP0` through `DP4`) and adjacent DCN headers when hardware is expected to match, paying special attention to instance suffix drift and chunk-boundary fields.
- Exercise the sixth display link where available: hotplug, modeset, suspend/resume, DPMS off/on, HDMI/DVI output, DP SST, DP MST, eDP/panel paths, and connector combinations that map to `DIG5`/`DP5`.
- Validate HDMI behavior: audio playback, ACR stability, infoframe contents, HDR/Dolby metadata delivery where applicable, deep color/scrambling, generic packets, and absence of HDMI audio/VBI error interrupts.
- Validate DP behavior: link training at supported rates/lane counts, MST slot allocation, DSC/MSO paths if supported, secondary-data/audio packets, ALPM entry/exit, FEC/CRC diagnostics where exposed, and stable video after retraining.
- Validate GPIO sideband behavior: EDID reads on DDC1-DDC6 and DDCVGA, AUX-vs-I2C pad mode switching, HPD connect/disconnect detection for HPD1-HPD6, and stable HPD debounce/filter behavior.
- Validate panel/backlight behavior on platforms using these fields: power sequencing delays, PWM period/duty programming, lock behavior, suspend/resume brightness restoration, and no panel flicker during enable/disable.
- Watch negative signals in kernel logs and display state: black screens, link-training failures, missed vblank/page flips, EDID/AUX/I2C timeouts, HPD flapping, audio dropouts, infoframe/HDR metadata failures, CRC mismatches, underflow or FIFO errors, and resume or DPMS regressions.

### subset-b-001630: lines 49386-51950

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 49386-51950

## Purpose

This chunk is part of AMDGPU's generated DCN 2.0 register field mask/shift header. It contains no executable C logic; it publishes compile-time bit layout constants for display-controller MMIO registers. Each field has paired macros:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position.
- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.

Driver code combines these macros with matching register addresses from `dcn_2_0_0_offset.h` and AMD display helper macros such as `SF(...)`, `REG_SET`, `REG_UPDATE`, and MMIO read/write helpers. Correctness is therefore a hardware ABI contract. A wrong mask or shift can compile cleanly but program the wrong GPIO, AUX, HPD, Display Stream Compression, or performance-monitor bit.

The range covers three main register surfaces:

- Tail fields for DC GPIO/HPD/AUX and panel power-sequencing controls, including HPD enable/output status, BLON/DIGON/ENA_BL/VSYNC/HSYNC power-sequence GPIO fields, pad strength, PHY AUX controls, AUX channel muxing, pull-ups, RX enables, TX enables, and AUX/I2C pad power status.
- Seven repeated `DCIO_UNIPHY<N>_UNIPHY_MACRO_CNTL_RESERVED0..47` blocks for UNIPHY instances 0-6. These expose full-width reserved control words rather than decoded named fields.
- DSC instance 0 and 1 register fields, including DSC top clock/debug controls, DSCCIF interface configuration, DSCC slice/PPS programming, DSCC rate-buffer overflow/underflow interrupt status, DSCC memory power controls, error counters, fullness-level diagnostics, test debug bus rotation, and DSC performance monitor counters. The chunk ends partway through `DC_PERFMON22_PERFMON_CVALUE_INT_MISC`; later fields belong to the next chunk.

Although this source tree is stored under a local `ceph-client` path, this header is AMDGPU display-driver hardware metadata. It has no Ceph filesystem protocol behavior, no distributed filesystem control flow, and no filesystem persistence semantics.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or runtime APIs in this chunk. The macro namespace is the public surface consumed by generated register tables.

The GPIO and AUX section exposes:

- `DC_GPIO_HPD_EN` and `DC_GPIO_HPD_Y` fields for HPD pad enablement, Schmitt/slew controls, select bits, spare bits, and observed/output HPD values for HPD1-HPD6. This chunk starts with `DC_GPIO_HPD_EN` mask definitions; the corresponding shift definitions are in the previous chunk.
- `DC_GPIO_PWRSEQ_MASK`, `DC_GPIO_PWRSEQ_A`, `DC_GPIO_PWRSEQ_EN`, and `DC_GPIO_PWRSEQ_Y` fields for panel power sequence pins such as `BLON`, `DIGON`, `ENA_BL`, `VSYNC_IN`, and `HSYNC_IN`. These macros define mask, pull-down disable, receiver, output assignment, enable, and value fields.
- `DC_GPIO_PAD_STRENGTH_1` and `DC_GPIO_PAD_STRENGTH_2` fields for pad drive strength, including GENLK, RX/TX HPD, sync, generic strength, external reset, 27 MHz reference, power-sequence pads, and reference source selection.
- `PHY_AUX_CNTL` fields for AUX/DDC pad wake, receive select, mode, pull-down/enable controls, per-AUX RX selection for AUX1-AUX6, and AUX calibration/bias controls.
- `DC_GPIO_TX12_EN`, `DC_GPIO_RXEN`, and `DC_GPIO_PULLUPEN` fields for data/clock/HPD/AUX/power-sequence transmit, receive, and pull-up enables.
- `DC_GPIO_AUX_CTRL_0` through `DC_GPIO_AUX_CTRL_5` fields for AUX/DDC muxing and pad control across AUX/DDC channels and generic GPIO-backed AUX routes.
- `AUXI2C_PAD_ALL_PWR_OK` fields indicating whether AUX/I2C pads for DDC1-6 and AUX1-6 report all-power-OK.

The UNIPHY section is mechanically repeated:

- `DCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED0..47` through `DCIO_UNIPHY6_UNIPHY_MACRO_CNTL_RESERVED0..47` each define a full-width `UNIPHY_MACRO_CNTL_RESERVED` field with shift 0 and mask `0xFFFFFFFFL`.
- These are placeholders for PHY macro control words without decoded bit names in this generated header. Their presence still matters because address and mask tables can expose them for low-level PHY workarounds or diagnostic access.

The DSC/DSCC section exposes two parallel DSC engines:

- `DSC_TOP0_DSC_TOP_CONTROL` and `DSC_TOP1_DSC_TOP_CONTROL` define `DSC_CLOCK_EN`, display-clock gating disable, and DSCC clock gating disable fields. `DSC_TOP*_DSC_DEBUG_CONTROL` defines debug enable and test-clock mux selection.
- `DSCCIF0_DSCCIF_CONFIG0/1` and `DSCCIF1_DSCCIF_CONFIG0/1` define input interface underflow recovery/status/interrupt enable, input pixel format, double-buffer update pending, group mode, and slice-in-line counters.
- `DSCC0_DSCC_CONFIG0/1` and `DSCC1_DSCC_CONFIG0/1` define slice topology, ICH reset/encoding controls, and rate-control buffer model size. `DSCC*_DSCC_STATUS` exposes double-buffer update pending.
- `DSCC*_DSCC_INTERRUPT_CONTROL_STATUS` defines rate-buffer overflow and underflow status bits for buffers 0-3, rate-control buffer model overflow status bits for models 0-3, matching interrupt enables, native 4:2:2 buffer overflow/underflow status and interrupt enables, DSC picture-finished and slice-finished interrupt enable/status bits, and a double-buffer update request.
- `DSCC*_DSCC_PPS_CONFIG0..22` encode most of the Display Stream Compression picture parameter set: DSC version, PPS identifier, line-buffer depth, bits per component/pixel, VBR/simple/native format flags, RGB conversion, block prediction, chunk size, picture and slice dimensions, initial transmit/decode delays, scale values and intervals, BPG offsets, initial/final offsets, flatness QP, rate-control model size, edge factor, quantization increment limits, target offsets, rate-control buffer thresholds 0-13, and range min/max QP plus BPG offsets for ranges 0-14.
- `DSCC*_DSCC_MEM_POWER_CONTROL` defines default memory low-power state, memory power force/disable/state, and native 4:2:2 memory power force/disable/state.
- `DSCC*_DSCC_*_SQUARED_ERROR_*`, `DSCC*_DSCC_MAX_ABS_ERROR*`, `DSCC*_DSCC_RATE_BUFFER*_MAX_FULLNESS_LEVEL`, and `DSCC*_DSCC_RATE_CONTROL_BUFFER*_MAX_FULLNESS_LEVEL` expose quality/error and buffer fullness diagnostics.
- `DSCC*_DSCC_TEST_DEBUG_BUS_ROTATE` defines debug bus rotation fields for debug buses 0-3.
- `DC_PERFMON21_*` and `DC_PERFMON22_*` define performance counter controls, counter state selection, perfmon control, run-enable start/stop selectors, interrupt status bits, and counter value registers for the DSC0 and DSC1 performance-monitor address blocks.

## Control Flow

This header chunk has no runtime control flow. It is preprocessor data.

Runtime control appears in consumers that instantiate register descriptors:

1. DCN 2.0 display code includes `dcn/dcn_2_0_0_offset.h` and `dcn/dcn_2_0_0_sh_mask.h`.
2. Resource and hardware-object headers use macro expansion patterns such as `SRI(...)`, `SF(...)`, and `DSC_SF(...)` to bind register addresses, masks, and shifts into typed register tables.
3. DSC setup code uses those tables to enable DSC clocks, program DSCCIF/DSCC PPS registers from `drm_dsc`/AMD DSC configuration structures, request double-buffered updates, and check status or error registers.
4. GPIO/DDC/HPD factory code uses the same generated mask/shift pattern to build HPD and DDC register tables for physical connectors, AUX/I2C pads, and generic GPIO paths.
5. IRQ, hotplug, modeset, panel power, DSC enable/disable, and diagnostic paths perform MMIO read-modify-write operations through the generated tables.

The macros themselves do not enforce legal sequencing. For example, they cannot ensure that DSC clock enable precedes PPS writes, that double-buffer update requests are acknowledged before stream enable, that interrupt status bits are cleared with the correct write semantics, or that AUX/HPD GPIO pad changes happen only while the link is in a safe state.

## State And Persistence Behavior

The file stores no software state and has no persistence mechanism. It describes state held in GPU display hardware registers.

The represented state includes:

- Connector and pad state: HPD enable/value, AUX/DDC muxing, receiver and pull-up enables, pad power-good status, and PHY AUX calibration/control.
- Panel power-sequence state: BLON/DIGON/ENA_BL/VSYNC/HSYNC masks, output assignments, enables, receiver state, and observed/output values.
- PHY state: UNIPHY reserved macro control words for seven PHY instances.
- DSC programming state: clock/debug controls, interface format and group mode, slice topology, full PPS register payload, memory power mode, double-buffer update pending/request status, overflow/underflow interrupt status, and native 4:2:2 memory or buffer state.
- Diagnostics and counters: squared-error accumulators, max absolute error, rate-buffer fullness, rate-control buffer fullness, debug bus rotation, perfmon counter control/state, interrupt status, and counter values.

Persistence depends on hardware semantics outside this header. Some fields are normal read/write control bits, some are read-only status or diagnostic counters, some are sticky interrupt bits that require acknowledgement, some are self-clearing requests, and many are reset by display power gating, link disable, suspend/resume, mode reset, DSC block reset, or ASIC reset. The generated macros do not record access type, reset value, volatility, write-one-to-clear behavior, or whether a field is safe to access while clocks are gated.

## Dependencies And Integration Points

This chunk depends on the matching generated address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h`

Direct include points for `dcn_2_0_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

The most direct consumer for the DSC part of this chunk is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h`. Its `DSC_REG_LIST_DCN20(id)` lists the DSC top, DSCC, DSCCIF, error, fullness, and debug registers represented here, while `DSC_REG_LIST_SH_MASK_DCN20(mask_sh)` expands fields such as `DSC_TOP0_DSC_TOP_CONTROL__DSC_CLOCK_EN`, `DSCC0_DSCC_PPS_CONFIG*`, `DSCC0_DSCC_MEM_POWER_CONTROL`, and `DSCCIF0_DSCCIF_CONFIG0` into shift and mask tables.

The GPIO/AUX/HPD part integrates through `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c` and related headers such as `hpd_regs.h`, `ddc_regs.h`, and GPIO register definitions. That code constructs arrays of HPD and DDC register descriptors for six physical HPD/DDC instances plus VGA/generic fallback entries.

The broader display resource integration is in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`, which includes this generated header while assembling the DCN 2.0 resource pool for pipes, links, clocks, DSC objects, AUX/I2C, audio, panel controls, interrupts, and memory hub/display blocks.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A bad generated constant usually does not cause a compile error; it causes the register helper layer to update the wrong bit or fail to preserve adjacent bits during read-modify-write.

GPIO/AUX/HPD risks include broken hotplug detection, incorrect HPD polarity/value sampling, AUX/I2C transactions routed to the wrong pad, missing DDC access, stuck pull-ups, incorrect pad receiver enables, or panel power pins asserted in the wrong order. These failures surface as missing displays, unreliable hotplug, EDID read failures, blank embedded panels, or unstable link training.

Pad strength and PHY AUX controls are electrical-risk fields. Incorrect drive-strength, wake, receive-select, mode, or calibration masks can produce board-specific failures that appear only on long cables, marginal sinks, or low-power transitions. UNIPHY reserved fields are especially risky because the header provides no semantic names; any consumer must rely on external hardware documentation or workaround tables.

DSC PPS fields are high-impact. Incorrect shifts for bits per pixel/component, picture size, slice size, chunk size, delays, BPG offsets, QP ranges, buffer thresholds, or native 4:2:0/4:2:2 flags can make compressed streams fail to light, produce corrupted pixels, violate DisplayPort DSC requirements, or trigger rate-buffer overflows and underflows.

Interrupt/status fields are sensitive to access semantics not captured here. Misusing `DSCC*_DSCC_INTERRUPT_CONTROL_STATUS` or perfmon status masks can leave stale status bits, miss real buffer overflows, cause repeated interrupts, or acknowledge the wrong condition.

Memory-power and clock-control fields have sequencing risk. Incorrect `DSC_CLOCK_EN`, clock-gating disable, or DSCC memory power masks can make later DSC register writes ineffective, read stale diagnostic state, or cause resume/modeset-only failures.

The repeated structure creates copy-generation risk. DSCC0 and DSCC1 fields should be equivalent with only the instance prefix changed. UNIPHY0-6 reserved blocks are 48-register repeats. A single off-by-one instance, missing field, or copied mask from the wrong register would only fail on a specific PHY or DSC engine.

The line range boundaries are artificial. This chunk begins after the `DC_GPIO_HPD_EN` shift definitions and ends before the complete `DC_PERFMON22_PERFMON_CVALUE_INT_MISC` field list. The final per-file merge should treat those as chunk boundaries, not missing source content.

## Test Signals

Useful validation signals are mostly compile-time plus hardware behavior:

- Kernel or module build coverage for DCN 2.0 display paths that include `dcn_2_0_0_sh_mask.h`.
- Generated-header consistency checks comparing every `*_MASK` and `*__SHIFT` pair in this range against AMD's register database and the matching addresses in `dcn_2_0_0_offset.h`.
- Static checks that every field referenced by `DSC_REG_LIST_SH_MASK_DCN20(...)`, HPD/DDC mask lists, IRQ tables, and resource tables has both mask and shift macros.
- DisplayPort DSC enablement tests at multiple resolutions, refresh rates, bits per component, slice counts, and native 4:2:0/4:2:2/RGB modes. Good signals include stable link training, correct image output, no DSCC rate-buffer overflow/underflow status, and no double-buffer update stuck pending.
- Hotplug and AUX/DDC tests across all physical connectors, including EDID reads, HPD storm handling, link retraining, suspend/resume, DPMS, and connector unplug/replug stress.
- Embedded panel power-sequence tests for BLON/DIGON/ENA_BL behavior, backlight enable, panel wake/sleep, and resume from low-power states.
- DSC diagnostic reads for squared-error, max-absolute-error, rate-buffer fullness, and rate-control buffer fullness. Values should be sane for known streams and not show persistent overflow/underflow after modeset.
- Perfmon tests that configure `DC_PERFMON21` and `DC_PERFMON22` events, start/stop counters, observe active/state bits, read low/high values, and verify interrupt status/ack behavior where supported.
- Hardware lab or compliance tests for DisplayPort DSC streams and AUX/HPD electrical behavior, especially on marginal cables and high-bandwidth modes.

Regression symptoms from bad constants include missing connector detection, EDID read failures, blank or flickering DSC modes, corruption only when DSC is enabled, failures isolated to one DSC engine or one connector, interrupt storms, stale overflow status, stuck double-buffer updates, resume-only display failures, and perf counters that never start or report impossible values.

## Cross-Chunk Notes

Earlier chunks of `dcn_2_0_0_sh_mask.h` define the preceding DC GPIO fields and the beginning of `DC_GPIO_HPD_EN`, including shifts paired with the initial masks in this chunk. Later chunks continue from `DC_PERFMON22_PERFMON_CVALUE_INT_MISC` and proceed through the remaining DCN 2.0 register mask namespace. The final per-file research document should treat the full header as one generated DCN 2.0 hardware register-layout contract rather than as independent algorithmic code.

### subset-b-001631: lines 51951-54426

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 51951-54426

## Scope

This chunk is a generated AMD DCN 2.0 register shift/mask header slice. It does not define executable code, structs, enums, or functions. Its public surface is a dense set of C preprocessor constants named as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`, used by AMDGPU display register helpers to compose, update, and decode memory-mapped hardware registers.

The line range starts in the middle of the `DC_PERFMON22_PERFMON_CVALUE_INT_MISC` definition and ends in the middle of `DMCUB_INTERRUPT_TYPE`; adjacent chunks own the omitted leading and trailing fields. Within this chunk the complete major blocks are DSC/DSCC instances 2 through 5, perfmon instances 23 through 26, and most DMCUB region/interrupt masks.

## Purpose

The constants describe bit positions and bit masks for DCN 2.0 display hardware:

- Tail of `DC_PERFMON22`: performance monitor interrupt status/acknowledge bits and counter value readback fields.
- `DSC_TOP[2-5]`: Display Stream Compression top-level clock/debug controls for DSC instances 2, 3, 4, and 5.
- `DSCCIF[2-5]`: DSC input interface configuration, including underflow recovery/status, pixel format, component depth, picture width/height, and double-buffer update pending state.
- `DSCC[2-5]`: DSC codec configuration, PPS programming fields, rate-control tables, overflow/underflow interrupt status enables, memory power controls, error counters, fullness telemetry, and debug bus rotation.
- `DC_PERFMON[23-26]`: perf counter controls and value/status readback blocks associated with the DSC display decoder perfmon address blocks.
- `DMCUB_*`: Display Microcontroller Unit (DMUB/DMCUB) address translation windows for regions 0, 1, 2, 4, 5, 6, 7 and region 3 code-window slots 0 through 7, plus interrupt enable, ack, status, and partial interrupt type fields.

## Important APIs, Types, and Macro Families

There are no callable APIs in this file. The relevant interface is the macro naming contract consumed by the AMD display register access layer:

- `REG_SET`, `REG_UPDATE`, `REG_GET`, and related helpers concatenate a register name and field name through helper macros such as `FN(reg_name, field)` in `display/dmub/src/dmub_reg.h`.
- Register offset headers such as `dcn_2_0_0_offset.h` provide `reg<REGISTER>` addresses; this header provides the paired field shifts and masks.
- `DMUB_SR(...)` and `DMUB_SF(...)` style lists in DMUB generation headers collect offsets and field definitions into per-ASIC register tables.

Important field groups in this chunk:

- `DSC_TOPn_DSC_TOP_CONTROL`: `DSC_CLOCK_EN`, `DSC_DISPCLK_R_GATE_DIS`, and `DSC_DSCCLK_R_GATE_DIS`.
- `DSCCIFn_DSCCIF_CONFIG0/1`: input underflow controls/status, pixel format, bits per component, double-buffer pending, picture width, and picture height.
- `DSCCn_DSCC_CONFIG0/1`: ICH reset policy, slice counts, alternate ICH encoding, rate control buffer model size, and ICH disable.
- `DSCCn_DSCC_INTERRUPT_CONTROL_STATUS`: status and interrupt-enable bits for rate buffer overflow/underflow and rate-control model overflow lanes 0 through 3.
- `DSCCn_DSCC_PPS_CONFIG0` through `PPS_CONFIG22`: DSC PPS fields including version, PPS identifier, line buffer depth, bits per component/pixel, chroma/RGB mode flags, picture/slice size, initial delays, scale intervals, BPG offsets, flatness QPs, RC model size, RC target offsets, RC buffer thresholds, and range min/max QP plus BPG offsets for ranges 0 through 14.
- `DSCCn_DSCC_MEM_POWER_CONTROL`: default low-power state plus force/disable/state fields for normal and native 4:2:2 memories.
- `DSCCn` telemetry registers: squared error lower/upper per component, max absolute error, rate buffer max fullness, rate control buffer max fullness, and test debug bus rotation.
- `DC_PERFMONn_*`: counter enable/clear/freeze, perfmon selection, counter state, high/low value halves, interrupt status/ack bits, and read selection fields.
- `DMCUB_REGION*`: low/high offset halves, top address plus enable bit, and region 3 CW base/top/offset controls.
- `DMCUB_INTERRUPT_ENABLE`, `DMCUB_INTERRUPT_ACK`, `DMCUB_INTERRUPT_STATUS`, and partial `DMCUB_INTERRUPT_TYPE`: timer, inbox, outbox, GPINT, undefined address fault, instruction fetch fault, and data write fault bit definitions.

## Control Flow

This header has no runtime branches or direct control flow. Runtime behavior emerges when driver code includes this header and calls the register helper macros:

1. A block-specific driver chooses a hardware register by symbolic name.
2. The helper uses the corresponding `reg<REGISTER>` offset from the offset header.
3. The helper applies this header's `SHIFT` and `MASK` constants to pack or extract a field value.
4. MMIO read/write helpers perform the actual hardware transaction.

For DSC programming, higher-level display code computes DSC PPS and rate-control parameters from the negotiated mode and compression settings, then writes the relevant `DSCCn_DSCC_PPS_CONFIG*`, `DSCCIFn_*`, and `DSC_TOPn_*` fields. For DMCUB programming, DMUB code configures memory windows and enables/acknowledges mailbox and GPINT interrupts through the DMCUB region and interrupt registers.

## State and Persistence Behavior

The macros themselves are compile-time constants and hold no state. The state they address is hardware state:

- DSC/DSCC fields persist in display engine registers until reset, power gating, or explicit reprogramming.
- Several DSC blocks advertise double-buffer update-pending fields; these indicate staged register updates that become active on the relevant display timing boundary rather than immediately.
- Underflow, overflow, fault, interrupt status, max-fullness, and error counters are hardware-observed state. Some status bits pair with interrupt enable and ack bits in the same or sibling register families.
- DMCUB region registers define address translation/protection windows for firmware-visible memory ranges. Top-address enable bits make those windows active or inactive.
- DMCUB interrupt enable bits persist as interrupt routing policy until driver changes or hardware reset. Ack masks clear latched interrupt sources when written according to the register helper semantics.

## Dependencies and Integration Points

This header is paired with `dcn_2_0_0_offset.h` and is included by DCN 2.0 display-related code, including DMUB, clock manager, IRQ service, GPIO factory, resource setup, and GMC code under the AMDGPU tree. It also follows the same generated naming schema used by later DCN headers, so shared driver macros can target different ASIC generations by swapping offset/mask tables.

The most direct integration points for this chunk are:

- DSC encoder setup paths that program `DSC_TOPn`, `DSCCIFn`, and `DSCCn` registers for compressed DisplayPort/eDP links.
- IRQ service tables that need enable/status/ack masks for DMCUB outbox, inbox, GPINT, and fault interrupts.
- DMUB initialization and diagnostic paths that configure and inspect DMCUB region windows and interrupt state.
- Performance monitor tooling or debug paths that use `DC_PERFMON23` through `DC_PERFMON26` counters to observe display decoder or DSC behavior.

## Risks and Maintenance Notes

- The file is generated and highly repetitive. Manual edits risk creating a mismatch between `SHIFT`, `MASK`, and the hardware register specification.
- The chunk boundary cuts through `DC_PERFMON22_PERFMON_CVALUE_INT_MISC` and `DMCUB_INTERRUPT_TYPE`; reviewers should consult adjacent chunks before drawing conclusions about those complete registers.
- DSC PPS fields are tightly packed. A wrong shift or mask can silently corrupt compression parameters, causing link training failures, visual corruption, bandwidth underestimation, or DSC underflow/overflow interrupts.
- DMCUB region masks control firmware-visible address windows. Incorrect address masks, high/low offset handling, or enable bits can break firmware boot, command mailboxes, trace buffers, or fault isolation.
- Interrupt enable/status/ack bits must remain aligned with IRQ service tables. A mismatch can leave interrupts stuck, unacknowledged, or invisible to the driver.
- Several field names are replicated across instances 2 through 5. Instance numbering mistakes can program the wrong DSC engine when multiple pipes are active.

## Test Signals

Useful validation signals for changes touching this area include:

- Successful compile of AMDGPU display and DMUB code using `dcn_2_0_0_sh_mask.h`; undefined field names or duplicate macro errors catch naming drift.
- Display modes requiring DSC on DCN 2.0 hardware light up reliably, especially multi-monitor and high-bandwidth modes that exercise DSC instances beyond 0 and 1.
- No DSC input underflow, rate buffer overflow/underflow, or rate-control model overflow bits are observed during mode set, hotplug, suspend/resume, or bandwidth stress.
- DMCUB firmware boots, mailboxes work, and outbox/inbox/GPINT interrupts are delivered and acknowledged without interrupt storms.
- DMCUB fault status bits for undefined address, instruction fetch, and data write faults remain clear during normal boot and display operation.
- Perfmon readback returns sane high/low counter values and interrupt status/ack behavior when perf counters are enabled for the DSC/perfmon blocks.

### subset-b-001632: lines 54427-56984

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 54427-56984

## Scope And Purpose

This chunk is a generated AMD DCN 2.0 register shift/mask header segment. It does not define executable code; it defines preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for hardware registers used by the AMD display driver. The constants are paired with register offsets from `dcn_2_0_0_offset.h` and consumed through display register helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and object-specific register tables.

The covered lines begin in the DMCUB interrupt/control area, continue through MCIF writeback buffer-manager instance 2, XFC/MMHUBBUB crossbar and write-buffer controls, and then cover DPP instance 4 top-level, converter, cursor, scaler, output-buffer, and color-management fields. The source-tree contract is that these names exactly match the generated register names expected by DCN 2.0 display code; changing a constant changes how driver field helpers pack and unpack MMIO values.

## Register Groups Covered

The first section completes DMCUB interrupt type masks and then defines DMCUB external interrupt, fault, security, memory, mailbox, timer, scratch, control, GPINT, low-power wake, memory-power, timer-current, and processor-ID fields. Important fields include `DMCUB_EXT_INTERRUPT_STATUS` count/ID extraction, fault address registers for instruction fetch/data write/undefined address faults, `DMCUB_SEC_CNTL` security reset and fault-clear bits, `DMCUB_MEM_CNTL` QoS/read-write address-space fields, inbox/outbox base/size/read-write pointer registers for channels 0 and 1, `DMCUB_CNTL` enable/soft-reset/trace/light-sleep/gating fields, GPINT data in/out registers, and `DMCUB_MEM_PWR_CNTL` force/disable/state fields.

The `dce_dc_mmhubbub_mcif_wb2_dispdec` block defines the writeback buffer-manager instance 2 surface. It includes software control and VCE control bits, current-line/status fields, luma/chroma pitch, buffer 1-4 status and status2 registers, arbitration and SCLK/P-state/watermark controls, test-debug index/data, per-buffer Y/C base addresses and offsets, high address bytes, luma/chroma sizes, and per-buffer resolution. Status fields expose active, locked, overflow, disabled, mode, tag, next-buffer, field, current line, line-length error, frame-length error, color-depth, TMZ, Y/C overrun, and eye-flag state.

The `dce_dc_mmhubbub_xfcp0_dispdec` through `xfcp5_dispdec` blocks repeat an identical XFC per-pipe layout for instances 0 through 5. Each instance has `MMHUBBUB_XFC_CNTL` fields for master/slave enable, 64bpp pixels, XBUF full enable, bandwidth-reduction mode, alpha position, local GPU ID, target pipe ID, and slave-to-master GPU ID. Each instance also supplies two XBUF write base addresses split into LSB/MSB, XBUF software mode and pitch, and XBUF width/height.

The shared `dce_dc_mmhubbub_xfc_dispdec` block defines XFC memory power control, XBUF write surface tiling/configuration, VMID/AWCACHE/QoS/stall controls, backpressure release timing, GPU write attributes, loopback and BRESP flags, VM initialization control and base/pixel values, per-GPU base addresses, and XFC monitor counters for requests and backpressure. These fields are used to configure and observe cross-GPU/display fabric writeback behavior.

The `dce_dc_dpp4_dispdec_dpp_top_dispdec` block defines DPP instance 4 top controls: DPP clock enable, clock-gate disable bits, test clock selection, per-subblock soft reset for CNVC/DSCL/CM/OBUF, CRC value/control fields, and host-read throttling. This is the root control surface for display pipe processor instance 4.

The `cnvc_cfg` and `cnvc_cur` blocks define DPP4 pixel conversion and cursor fields. Conversion fields include surface pixel format, format expansion/CNV16/alpha/bypass/clamp/update-pending state, floating-point bias/scale per channel, color-key enable/mode and low/high thresholds for ARGB channels, and the 2-bit alpha LUT. Cursor fields control enable, expansion, pixel inversion, ROM mode, cursor mode, pixel alpha modulation, update-pending state, two cursor colors, and cursor FP scale/bias.

The `dscl` block defines DPP4 scaler and line-buffer fields. It includes coefficient RAM tap select/data, scaler mode and coefficient bank selection, luma/chroma tap counts, 2-tap sharpen controls, manual replicate controls, horizontal/vertical scale ratios and initial phases for luma/chroma/bottom-field paths, black offsets, update-pending and autocal fields, overscan, OTG blanking, recout/MPC geometry, line-buffer data format and partitioning, line-buffer vertical counters, DSCL memory power state/control, OBUF control, and OBUF memory power state/control.

The final `cm` block defines DPP4 color-management fields. It includes color-management bypass/update state, input CSC mode and matrix coefficients for current and B sets, gamut remap matrices for current and B sets, bias registers, degamma controls and LUT access, blend gamma controls and LUT access, HDR multiplier coefficient, memory power state/control, dealpha enable, coefficient format selectors, and shaper controls/LUT access. The chunk ends in the shaper RAMB region definitions after listing RAMA and part of RAMB region metadata.

## Important APIs, Types, And Macros

There are no C functions, structs, or runtime APIs in this chunk. The important exported interface is the macro namespace itself:

- `<REGISTER>__<FIELD>__SHIFT` constants provide the bit offset for a register field.
- `<REGISTER>__<FIELD>_MASK` constants provide the already-shifted mask for the same field.
- Register names are paired with `mm<REGISTER>` offsets from `dcn_2_0_0_offset.h`.
- Consumer code expands these constants through generated helper macros such as `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)`, then uses register access wrappers to read, write, or update fields safely.

Representative consumers include `display/dmub/src/dmub_dcn20.c`, `display/dc/irq/dcn20/irq_service_dcn20.c`, `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`, `display/dc/resource/dcn20/dcn20_resource.c`, and `display/dc/gpio/dcn20/hw_factory_dcn20.c`, all of which include this header alongside the matching DCN 2.0 offset header.

## Control Flow And State Behavior

This header has no local control flow. The control flow is in callers that use these masks to perform MMIO sequences. For example, DMUB DCN 2.0 setup reads `DMCUB_CNTL.DMCUB_SOFT_RESET`, writes GPINT commands, toggles `DMCUB_CNTL.DMCUB_ENABLE` and `DMCUB_CNTL.DMCUB_SOFT_RESET`, resets DMCUB inbox/outbox pointers, programs DMCUB security/memory control, and writes DMCUB window registers. Those operations rely on the DMCUB field positions in this chunk being correct.

The state represented here is hardware state, not persisted kernel data. Writes alter GPU display engine registers, firmware mailbox pointers, buffer-manager state, XFC write/monitor configuration, DPP4 scaler/color/cursor registers, and memory power controls. Some fields are status-only or handshake-like, such as `*_UPDATE_PENDING`, `*_INIT_DONE`, `*_STATS_VALID`, fault address/status bits, current-line counters, CRC values, memory-power state fields, and monitor statistics.

Persistence is limited to the device register state until reset, power-gating, modeset reprogramming, or driver teardown. LUT-related registers (`CM4_CM_DGAM_*`, `CM4_CM_BLNDGAM_*`, `CM4_CM_SHAPER_*`, and scaler coefficient RAM) represent programmed hardware tables and their bank/selection/status bits; callers must follow the correct index/data/write-enable sequencing because this header only supplies bit layout.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.0 register naming scheme and the matching offset header. It is integrated through AMD display register helpers and hardware object initialization tables. The same field names also appear in related ASIC headers for other DCN generations, but the exact masks can differ; consumers must include the header for the selected ASIC generation.

Integration points by subsystem:

- DMUB firmware service: DMCUB control, mailbox, scratch, GPINT, security, memory, timer, and fault fields support firmware boot/reset, window setup, interrupts, and diagnostics.
- IRQ service: interrupt status/type/context fields provide decoding and acknowledge support for DCN 2.0 interrupt handling.
- Display writeback and memory hub: MCIF_WB2 and XFC/MMHUBBUB fields configure display writeback buffers, crossbar routing, write surfaces, VM initialization, QoS, P-state watermarks, and monitoring.
- DPP instance 4: DPP_TOP4, CNVC4, DSCL4, OBUF, and CM4 fields are used by resource construction and pipe programming for one display pipe processor instance.
- Color and scaling programming: LUT index/data/write-enable masks and scaler coefficient RAM masks are the low-level contract for higher-level color-management and scaling algorithms.

## Risks And Failure Modes

The primary risk is silent hardware misprogramming. If a shift or mask is wrong, helper macros can write the wrong bits while the code still compiles. Consequences include failed DMUB boot/reset, stuck mailbox pointers, missed or uncleared interrupts, invalid fault handling, writeback corruption, wrong display format conversion, incorrect scaler coefficients, broken cursor/color-key behavior, invalid color transforms, power-gating hangs, or display pipe underruns.

Generated headers also carry naming and versioning risk. A field name mismatch breaks compile-time macro expansion in register table initializers; a mask copied from a different ASIC generation can compile but program an incompatible register layout. Repeated instance blocks such as XFC0-5 and patterned LUT region blocks are especially prone to mechanical generation or merge errors because most lines look identical except the instance or region number.

Runtime sequencing remains a caller responsibility. This header does not encode whether a field is read-only, write-one-to-clear, latched on update, double-buffered, or requires polling. Fields such as interrupt ACKs, fault clears, LUT write enables, VM init done, stats valid ACK, and update-pending bits require the surrounding driver logic to use the right order and wait conditions.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- Build signal: AMD display code must compile with this header and `dcn_2_0_0_offset.h`; undefined `FD_MASK`/`FD_SHIFT` expansions reveal missing or renamed fields.
- Static comparison signal: generated DCN 2.0 masks should match the authoritative register database and remain consistent with adjacent instance blocks and matching offset names.
- DMUB signal: DCN 2.0 hardware should boot/reset DMUB, exchange GPINT commands, and move inbox/outbox pointers without hangs or fault interrupts.
- Display pipeline signal: modesets using DPP4 should produce correct CRCs, scaling geometry, cursor rendering, pixel format conversion, color keying, gamma/shaper behavior, and memory power transitions.
- Writeback/XFC signal: MCIF_WB2 and XFC paths should produce valid writeback buffers, report sensible current-line/status/overrun fields, and avoid backpressure or P-state watermark regressions.
- Runtime diagnostics: fault address registers, XFC monitor counters, CRC registers, memory-power status fields, update-pending bits, and interrupt status/ACK fields are observable indicators that the masks line up with real hardware behavior.

### subset-b-001633: lines 56985-59503

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 56985-59503

## Scope And Purpose

This chunk is part of AMDGPU's generated DCN 2.0 register field mask/shift header. It contains no executable C logic. Its purpose is to publish compile-time bit layout constants for DCN 2.0 display and display-audio MMIO registers.

Each exposed field follows the generated AMD register-header convention:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position for a field.
- `REGISTER__FIELD_MASK` gives the already-positioned mask for that field.

The constants are meaningful together with the matching register-address macros in `dcn_2_0_0_offset.h` and with AMD display register helpers such as `SF(...)`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and lower-level MMIO read/write wrappers. The repository path is under a local `ceph-client` source tree, but this file is AMDGPU display-driver hardware metadata and has no Ceph filesystem behavior.

The covered range spans several hardware blocks:

- Tail of the DPP4 color-management (`CM4`) block, including shaper RAMB regions 18-33, shaper/HDR 3D LUT memory power control/status, 3D LUT programming fields, output normalization/offset/scale fields, and CM test-debug index/data.
- DPP4 display performance monitor `DC_PERFMON27`.
- DPP5 top-level DPP control, soft reset, CRC, and host-read controls.
- DPP5 CNVC format-conversion, color keying, alpha LUT, and cursor fields.
- DPP5 DSCL scaler, line-buffer, output-buffer, memory-power, and geometry fields.
- DPP5 color-management (`CM5`) matrix, degamma, blend gamma, shaper, 3D LUT, memory-power, coefficient-format, dealpha, HDR multiplier, and test-debug fields.
- DPP5 display performance monitor `DC_PERFMON28`.
- HDA/Azalia controller, endpoint/root immediate-command windows, input-endpoint command windows, and output stream descriptors for streams 0-3 plus the beginning of stream 4.

## Important APIs, Types, And Macros

There are no functions, structs, enums, storage objects, or runtime APIs in this chunk. The macro namespace is the API surface consumed by generated register-table code.

Important macro families:

- `CM4_CM_SHAPER_RAMB_REGION_20_21` through `CM4_CM_SHAPER_RAMB_REGION_32_33` complete the chunk-local tail of CM4 shaper RAMB region metadata. Each paired-region register packs an even and odd exponential region's LUT offset and segment count. The range begins with the final masks for `CM4_CM_SHAPER_RAMB_REGION_18_19`, whose matching comment and earlier shifts are in the previous chunk.
- `CM4_CM_MEM_PWR_CTRL2`, `CM4_CM_MEM_PWR_STATUS2`, `CM4_CM_3DLUT_*`, and `CM4_CM_TEST_DEBUG_*` describe CM4 shaper/HDR 3D LUT RAM power gating, 3D LUT mode/index/data/write/read status, output normalization and RGB offset/scale, and CM debug access.
- `DC_PERFMON27_*` and `DC_PERFMON28_*` define identical display performance counter layouts for DPP4 and DPP5 perfmon blocks: event selection, counted value type, hardware stop/count-off selection, counter state selector/status pairs, global perfmon enable/start/clear/counting mode, current-value interrupt thresholds and status, and high/low counter reads.
- `DPP_TOP5_DPP_CONTROL`, `DPP_TOP5_DPP_SOFT_RESET`, `DPP_TOP5_DPP_CRC_*`, and `DPP_TOP5_HOST_READ_CONTROL` expose DPP5 enable/output mux, per-subblock soft-reset, CRC control/result fields, and host read-enable fields for scaler, line buffer, gamut remap, cursor, input/output CSC, 3D LUT, shaper, degamma, format-converter, and output-buffer paths.
- `CNVC_CFG5_*` exposes DPP5 format conversion state: surface pixel format, component expansion, output CSC mode, floating-point bias/scale, color-keyer enable/alpha/RGB low-high bounds, and 2-bit alpha LUT entries.
- `CNVC_CUR5_CURSOR0_*` exposes cursor enable, expansion, pixel inversion, ROM/mode, pixel alpha modulation, update-pending status, cursor colors, and floating-point cursor scale/bias.
- `DSCL5_*` exposes DPP5 scaler and line-buffer layout: coefficient RAM tap select/data, scaler mode, tap counts, 2-tap hardcoded/sharp controls, manual replication, horizontal/vertical luma and chroma ratios/init phases, black offsets, update pending, autocal pipe selection, overscan, OTG blanking mirrors, recout/MPC sizes, line-buffer memory format/partitioning/counters, DSCL memory power controls/status, output-buffer controls, and output-buffer memory power state.
- `CM5_CM_*` is the largest group. It covers CM bypass/update status, input CSC and gamut remap coefficient banks A/B, bias fields, degamma control/LUT/index/write-enable plus RAM A/B region tables, blend-gamma control/LUT/index/write-enable plus RAM A/B region tables, HDR multiplier, shared/blend/shaper/3D-LUT memory-power controls and status, dealpha enable, coefficient format selections, shaper control/offset/scale/LUT/write-enable plus RAM A/B regions, 3D LUT mode/index/data/30-bit/write-read control/output normalization/RGB output offset-scale, and CM test-debug index/data.
- `CORB_*`, `RIRB_*`, `IMMEDIATE_*`, `DMA_POSITION_*`, and `WALL_CLOCK_COUNTER_ALIAS` expose HDA/Azalia controller command/response ring, immediate command/response, DMA position buffer, and wall-clock fields.
- `AZENDPOINT_*`, `AZROOT_*`, and `AZENDPOINT_IMMEDIATE_COMMAND_INPUT_*` expose endpoint/root immediate-command index/data windows.
- `AZSTREAM[0-3]_OUTPUT_STREAM_DESCRIPTOR_*` define complete HDA output stream descriptor layouts: control/status, link position, cyclic buffer length, last valid index, FIFO size, stream format, buffer descriptor list lower/upper base addresses, and link-position alias.
- `AZSTREAM4_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS` begins at the end of the chunk and includes control/status shifts plus the first masks through `TRAFFIC_PRIORITY_MASK`; remaining stream 4 masks and descriptor fields are in the following chunk.

## Control Flow

This chunk has no runtime control flow. It is declarative bitfield metadata.

Runtime control appears in AMDGPU/DCN consumers that include `dcn_2_0_0_sh_mask.h` and pair these masks/shifts with offset macros:

1. DCN20 resource and hardware-object setup code builds register, shift, and mask tables for display pipes, color modules, scalers, performance monitors, IRQ/GPIO, clock, DMUB, and related blocks.
2. DC color-management code programs degamma, shaper, 3D LUT, gamut remap, input CSC, blend gamma, and related coefficient/register RAM windows by selecting indices or RAM banks, writing data fields, and checking update/config status bits.
3. DPP/scaler code programs DSCL ratios, initialization phases, taps, coefficient RAMs, line-buffer partitions, recout/MPC sizes, overscan, and memory-power controls during plane programming and modeset.
4. Cursor and CNVC code programs cursor state, surface format conversion, alpha/color-keying, floating-point scale/bias, and component format controls as planes are enabled or updated.
5. Perfmon/debug code selects events and counter modes, starts/stops counters, reads high/low counter values, or uses CRC/test-debug registers for diagnostics.
6. HDA/Azalia audio code programs CORB/RIRB DMA rings, immediate commands, stream descriptors, BDL base addresses, cyclic lengths, sample format, stream run/reset, and interrupt/status bits during display audio enablement and teardown.

The header does not enforce sequencing. Consumers must know when fields are double-buffered, read-only, sticky, self-clearing, write-one-to-clear, reset-sensitive, or power-gating dependent. Names such as `*_UPDATE_PENDING`, `*_CONFIG_STATUS`, `*_MEM_PWR_STATE`, `*_SOFT_RESET`, `*_RUN`, `*_RESET`, `*_INTERRUPT_STATUS`, and `*_DMA_ENABLE` identify control-sensitive fields, but access semantics are outside this generated mask header.

## State And Persistence Behavior

The file stores no software state and has no persistence mechanism. The macros describe hardware MMIO state.

The represented hardware state includes:

- CM4 and CM5 color pipeline state: input CSC coefficients, gamut remap matrices, bias, degamma LUTs, blend gamma LUTs, shaper LUTs, 3D LUT data, RGB offsets/scales, HDR multiplier, coefficient formats, dealpha enablement, and bypass/update status.
- DPP5 scaler and composition state: scale ratios, filter phases, coefficient RAM contents, tap modes, line-buffer memory configuration and counters, recout/MPC dimensions, overscan, blanking mirror values, output-buffer controls, and DPP enable/reset/output muxing.
- Plane format and cursor state: CNVC pixel format, component expansion, output CSC mode, floating-point conversion bias/scale, color keying, alpha LUT entries, cursor enable/mode/colors/scale/bias, and cursor update-pending status.
- Diagnostic and monitoring state: DPP CRC values/control, CM test-debug windows, and DPP4/DPP5 perfmon event/counter/cvalue interrupt registers.
- Power-gating state: CM shared/blend/shaper/HDR3DLUT memory power controls/status, DSCL LUT/line-buffer group memory power controls/status, and OBUF memory power controls/status.
- HDA/Azalia state: command output/response input ring pointers, ring base addresses, DMA enable bits, immediate command busy/result status, DMA position buffer base, wall clock, endpoint/root immediate-command windows, stream run/reset/interrupt enables/status, stream number, FIFO readiness/errors, cyclic buffer length, last valid descriptor index, stream format, BDL addresses, and link-position counters.

Persistence is hardware-specific. Some fields are persistent programming knobs until rewritten, modeset, power transition, suspend/resume, or ASIC reset. Other fields are live counters, snapshots, interrupt status bits, command/status handshakes, or power-state/status readbacks. This generated header does not encode reset values, volatility, read/write permissions, or side effects.

## Dependencies And Integration Points

This chunk depends on the generated AMD DCN 2.0 register-header set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h` supplies matching register addresses/base indices.
- Other generated DCN/DCE enum headers supply legal symbolic values for many fields.
- AMD display/DC register helper macros convert the mask/shift constants into read-modify-write operations and per-block register tables.

Direct include points for `dcn_2_0_0_sh_mask.h` found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

Practical integration points are DRM plane programming, DCN20 resource construction, DPP/scaler setup, color-management application, HDR/3D-LUT programming, cursor updates, perf counter sampling, DPP CRC/debug collection, memory power-gating transitions, display audio command/stream setup, hotplug/modeset audio enablement, and suspend/resume restore paths.

## Risks And Edge Cases

- These macros are hardware ABI. A wrong mask or shift can compile cleanly while updating the wrong bits in a live display or audio register.
- The chunk boundaries are artificial. It starts inside `CM4_CM_SHAPER_RAMB_REGION_18_19` and ends inside `AZSTREAM4_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS`; adjacent chunks are required for complete source-file coverage.
- The repeated region tables are easy to corrupt manually. `*_RAMA_REGION_*` and `*_RAMB_REGION_*` entries pack two regions per register with fixed offsets and segment-count fields. Off-by-one region drift can affect only part of a LUT and be visible as color banding or incorrect transfer functions.
- CM5 color-management fields are color-critical. Bad CSC/gamut/remap/coefficient-format, degamma, blend-gamma, shaper, or 3D-LUT masks can cause wrong color conversion, incorrect HDR behavior, clipping, banding, or failure to update the intended RAM bank.
- DSCL fields are timing and image-quality sensitive. Incorrect ratios, init phases, taps, coefficient RAM selection, line-buffer partitioning, recout/MPC sizes, or update-pending handling can produce scaling artifacts, underflow, black frames, or pipe-update failures.
- Memory power fields interact with register availability. Forcing or disabling CM, DSCL, line-buffer, OBUF, shaper, blend-gamma, or HDR3DLUT memory power at the wrong time can lose programmed tables or cause reads/status polling to misbehave.
- Perfmon and debug registers can be status/clear sensitive. Wrong `*_INT_STATUS`, clear, active, restart, or counter-selection masks can hide real performance events or create misleading debug captures.
- HDA/Azalia controller and stream fields are side-effect heavy. CORB/RIRB pointer reset, DMA enable, immediate command busy/result-valid, stream reset/run, interrupt status, descriptor error, FIFO error, and BDL base fields must be sequenced with audio hardware expectations. Bad masks can cause missing HDMI/DP audio, stuck command rings, descriptor DMA faults, or interrupt storms.
- Stream descriptors repeat across `AZSTREAM0` through `AZSTREAM4`. Instance suffix drift or copied masks from a neighboring stream could affect only one audio stream and evade broad compile-only checks.

## Test Signals

Useful validation combines generated-header consistency, compile coverage, and hardware behavior:

- Build AMDGPU/DC with DCN20 support enabled; missing or renamed macros should fail in DCN20 resource, IRQ, GPIO, clock-manager, DMUB, GMC, and display hardware-object paths.
- Check generated mask/shift consistency against AMD's register database and the matching `dcn_2_0_0_offset.h` entries. For each field, `(mask >> shift)` should match the intended field width and should not overlap unrelated fields in the same register.
- Compare repeated DPP4/DPP5, CM4/CM5, perfmon, DSCL, and AZ stream blocks against adjacent instances and adjacent ASIC families where hardware is expected to remain compatible.
- Exercise DCN20 modesets with scaling enabled and disabled, luma/chroma scaling, cursor updates, color keying, format conversion, SDR/HDR-like color-management changes, 3D LUT programming, gamma/shaper updates, blank/unblank, hotplug, and suspend/resume.
- Validate visual signals: no black screens, no scaling artifacts, no color shifts, no banding from LUT region programming, correct cursor rendering, correct alpha/color-key behavior, and stable page-flip/vblank completion.
- Validate diagnostics: DPP CRC values, CM test-debug access, `DC_PERFMON27`/`DC_PERFMON28` counter programming and reads, update-pending/config-status polling, and absence of unexpected underflow or power-gating errors in kernel logs.
- Validate HDMI/DP audio: CORB/RIRB command handling, immediate command completion, stream reset/run sequencing, BDL programming, cyclic buffer length/last valid index handling, link-position reporting, stereo and multichannel sample formats, hotplug audio recovery, and suspend/resume audio restore.
- Negative signals include compile failures in generated register tables, silent color mismatch, LUT update failures, scaler underflow, stuck update-pending bits, perf counters that never start/stop, command ring timeouts, descriptor/FIFO errors, missing audio after modeset, or interrupt storms.

## Cross-Chunk Notes

Earlier chunks contain the start of the CM4 shaper RAMB region list and preceding DPP4 color-management definitions. Later chunks continue the `AZSTREAM4_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS` masks and the rest of stream 4 plus subsequent HDA/display register metadata. The final per-file research document should treat this chunk as one slice of a generated DCN 2.0 hardware register-layout contract, not as standalone algorithmic code.

### subset-b-001634: lines 59504-62232

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 59504-62232

## Purpose

This chunk is part of AMDGPU's generated DCN 2.0 register field mask header. It contains no executable C logic; it publishes compile-time bit layouts for DCN 2.0 hardware registers as paired `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros.

The range is centered on Azalia/HDA audio and legacy indexed display registers:

- The tail of `AZSTREAM4` output stream descriptor fields, then complete `AZSTREAM5`, `AZSTREAM6`, and `AZSTREAM7` descriptor field layouts.
- Legacy VGA sequencer, CRTC, graphics-controller, and attribute-controller indexed registers: `SEQ00`-`SEQ04`, `CRT00`-`CRT22`, `GRA00`-`GRA08`, and `ATTR00`-`ATTR14`.
- Function group 2 Azalia codec endpoint, descriptor, sink-info, CRC result, input endpoint, and root codec indexed fields.
- Sixteen `AZF0STREAM<n>` stream-indirect blocks that expose FIFO sizing and latency counter fields.
- The start of the F0 endpoint-indirect blocks, including all of `AZF0ENDPOINT0` and the beginning of `AZF0ENDPOINT1`.

These macros are a hardware contract for code that packs and extracts fields from memory-mapped or indexed registers. They must line up with the matching address definitions in `dcn_2_0_0_offset.h` and with the enum values in generated Navi10 register enum headers.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, or storage objects in this chunk. The macro namespace is the API surface.

The `AZSTREAM4` tail and `AZSTREAM5`-`AZSTREAM7` groups describe HDA output stream descriptor registers. Each complete stream block has fields for:

- `OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS`: reset/run, interrupt-on-completion enable, FIFO and descriptor error interrupt enables, stripe control, traffic priority, stream number, completion/error status bits, and FIFO-ready status.
- `LINK_POSITION_IN_CURRENT_BUFFER`, `CYCLIC_BUFFER_LENGTH`, `LAST_VALID_INDEX`, and `FIFO_SIZE`.
- `FORMAT`: channel count, bits per sample, sample-base divisor, sample-base multiple, and sample-base rate.
- `BDL_POINTER_LOWER_BASE_ADDRESS` and `BDL_POINTER_UPPER_BASE_ADDRESS`, including the unimplemented low address bits in the lower pointer.
- `LINK_POSITION_IN_CURRENT_BUFFER_ALIAS`.

The VGA indexed register groups expose the classic VGA programming model inside DCN 2.0's generated address space. `SEQ*` covers reset, clocking, map masks, character map select, and memory mode bits. `CRT*` covers horizontal/vertical timing fields, cursor location, start address, offset, underline/row scan controls, mode control, line compare, and other CRTC state. `GRA*` covers set/reset, enable set/reset, color compare, data rotate, read map select, graphics mode, miscellaneous mode, color-don't-care, and bit mask fields. `ATTR*` covers palette entries, mode control, overscan, color plane enable, horizontal pixel panning, and color-select fields.

The `AZALIA_F2_CODEC_*` groups describe a function group 2 HDA codec endpoint. Converter fields include audio format, channel/stream ID, digital converter channel-status bits, keepalive, stripe control, ramp rate, GTC embedding, widget capabilities, supported rates/sizes, and stream-format capabilities. Pin fields include connection list response, widget control, unsolicited response, pin sense, default configuration words, speaker and channel allocation, down-mix info, audio descriptor indexing/data, multichannel enable/mute bits, lipsync, HBR, sink-info access, IEC 60958 channel-status override words, LPIB snapshots, coding type, format-change reporting, wireless display identification, remote keepalive, and pin capabilities.

The descriptor and sink-info blocks are data-style indexed registers. `AUDIO_DESCRIPTOR0`-`AUDIO_DESCRIPTOR13` expose audio descriptor payload fields such as maximum channels, sample-rate mask, byte-oriented audio descriptor fields, and speaker information. `SINK_DESCRIPTION0`-`SINK_DESCRIPTION17`, manufacturer/product IDs, description length, and port IDs expose monitor/sink identity data used by audio enumeration.

The CRC blocks define per-channel full-width result fields for `AZALIA_INPUT_CRC0`, `AZALIA_INPUT_CRC1`, `AZALIA_CRC0`, and `AZALIA_CRC1`. These are diagnostic readback fields for audio data paths.

The `AZALIA_F2_CODEC_INPUT_*` groups mirror the output codec model for input-side converter and pin controls. They include input converter format, channel/stream ID, digital converter status, widget capabilities, supported formats, pin widget control, unsolicited response, pin sense, default configuration, channel allocation, per-channel multichannel enables, HBR, LPIB snapshot/readback, input status control, infoframe fields, channel status low/high, and input pin capabilities.

The `AZALIA_F2_CODEC_ROOT_*` and `AZALIA_F2_CODEC_FUNCTION_*` groups expose root/function identity and control fields: vendor/device ID, revision ID, subordinate node counts, power-state set/read status, subsystem ID words, converter synchronization, reset, group type, supported rates/formats, and power-state capabilities.

The `AZF0STREAM0` through `AZF0STREAM15` groups repeat the same stream-indirect layout for sixteen stream instances. Each has `AZALIA_FIFO_SIZE_CONTROL` fields for FIFO allocation, `AZALIA_LATENCY_COUNTER_CONTROL`, and readback counters for worst-case latency, cumulative latency, and cumulative request count.

The `AZF0ENDPOINT0` group is a large endpoint-indirect layout. It includes converter capabilities/control, audio format, digital converter channel-status bits, stream/rate support, stripe/ramp/GTC controls, GTC counter delta statistics, pin capabilities, unsolicited response and pin sense, widget control, channel/speaker allocation, fourteen audio descriptor registers, multichannel enables, lipsync/HBR response fields, sink-info fields, hot-plug control, forced unsolicited response, default configuration, channel-status override words, LPIB snapshot/readback, coding type, format-change state, wireless display and remote keepalive controls, audio-enable status, and audio enable/disable/format-change interrupt status.

The chunk ends after the start of `AZF0ENDPOINT1`; it includes that endpoint's converter widget capabilities, converter format, channel/stream ID, digital converter bits, and stream-format field, while later lines continue the remaining supported-size/rate and endpoint fields.

## Control Flow

This header range has no runtime control flow. It is preprocessor metadata consumed by display and audio hardware programming paths.

A typical consumer flow is:

1. Select a DCN 2.0 register address or index from `dcn_2_0_0_offset.h`, such as `mmAZSTREAM5_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS`, `ixAZALIA_F2_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT`, or `ixAZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_WIDGET_CONTROL`.
2. Use this header's matching mask and shift macros to pack, clear, or extract the desired register field.
3. Access the register through AMDGPU/DC display register helpers, HDA/Azalia indexed-register paths, DMUB paths, or low-level SOC15 register helpers.
4. Let hardware execute the requested state change, such as stream start/stop, FIFO allocation, audio format update, unsolicited-response enable, hotplug reporting, LPIB snapshot, or CRC capture.

Control-sensitive actions represented here include resetting and running HDA stream descriptors, enabling stream completion/error interrupts, programming HDA BDL pointers and cyclic buffer lengths, assigning stream IDs/channels, changing PCM/non-PCM format fields, enabling digital audio transmission, muting or enabling multichannel lanes, reporting HBR and lipsync data, exposing sink descriptors, forcing or acknowledging unsolicited responses, controlling hotplug status delivery, and reading latency or CRC diagnostics. The macros do not enforce the required ordering, ownership, polling, clear-on-write, or read-only restrictions for those actions.

## State And Persistence Behavior

The file stores no software state and has no persistence mechanism. It describes state held in DCN 2.0 hardware registers.

The represented state includes:

- HDA stream descriptor state: run/reset bits, interrupt enables and status, stream number, FIFO readiness, current buffer position, cyclic buffer length, last valid BDL index, FIFO size, stream format, and BDL base addresses.
- Legacy VGA state: indexed sequencer, CRTC, graphics-controller, and attribute-controller fields used for VGA compatibility and early/legacy display modes.
- Codec and pin identity state: vendor/device IDs, revision IDs, subordinate-node counts, function group type, pin default configuration, association information, sink manufacturer/product/port IDs, sink description strings, audio descriptors, supported rates, supported bit depths, and stream-format capability masks.
- Audio transport state: converter format, channel/stream IDs, IEC 60958 channel-status bits and override enables, digital converter enable/status bits, keepalive, non-audio/pro/copy/pre-emphasis bits, speaker/channel allocation, HBR, lipsync, coding type, and wireless display identification.
- Interrupt and event state: unsolicited response enable/tag, hotplug enable/status, audio enabled/disabled/format-changed flags and masks, format-change reason/response fields, and forced unsolicited response controls.
- Diagnostics and counters: LPIB snapshots and timers, CRC results, FIFO allocation, latency counter control, worst-case latency, cumulative latency, cumulative request counts, and GTC counter deltas.

Persistence is hardware-defined. Some fields are programmed values that persist until mode-set, reset, power-gating, suspend/resume, or firmware intervention; some are live status readbacks; some are sticky interrupt/status bits; and some are read-only capability or identity values. This generated header does not encode which fields are read-only, write-one-to-clear, self-clearing, latched, indexed, or side-effecting.

## Dependencies And Integration Points

The direct companion for these field masks is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h`, which supplies the matching `mm...` and `ix...` register addresses and base indices. This chunk's address blocks match offset-header blocks such as `dce_dc_hda_azstream5_azdec`, `vga_vgaseqind`, `azendpoint_f2codecind`, `azendpoint_descriptorind`, `azendpoint_sinkinfoind`, `azf0controller_azcrc*resultind`, `azinputendpoint_f2codecind`, `azroot_f2codecind`, `azf0stream<n>_streamind`, and `azf0endpoint<n>_endpointind`.

Known include points for `dcn_2_0_0_sh_mask.h` in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`

The generated `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi10_enum.h` file provides semantic enum values for many Azalia fields in this chunk, including converter format sample-rate, bit-depth, channel-count, stream-type, digital converter status bits, widget control, unsolicited response, down-mix, and multichannel mute/enable fields. Consumers use those enum values with these masks/shifts to make packed register values readable and hardware-correct.

Although this path sits under a local `ceph-client` source tree, this source file is AMDGPU display/audio hardware metadata. It has no Ceph filesystem protocol logic, distributed filesystem state, or storage persistence behavior.

## Risks And Edge Cases

The main risk is silent register misprogramming. A wrong shift or mask can compile cleanly while changing the wrong hardware bit, corrupting adjacent fields during read-modify-write, or returning misleading status from diagnostics.

High-risk Azalia stream fields include `STREAM_RUN`, `STREAM_RESET`, interrupt enable/status bits, `STREAM_NUMBER`, `FORMAT`, BDL pointer fields, cyclic buffer length, last valid index, and FIFO size. Bad constants in these fields can prevent audio playback/capture, point DMA at the wrong BDL address, report incorrect buffer positions, trigger spurious interrupts, or mask real FIFO/descriptor errors.

Codec and pin fields are also sensitive. Incorrect converter format, channel/stream ID, digital converter bits, speaker/channel allocation, HBR, lipsync, channel-status override, sink-info, or audio descriptor fields can cause missing HDMI/DP audio, wrong channel count, wrong sample rate/depth, broken non-PCM passthrough, failed sink enumeration, or compliance failures.

Interrupt and event fields need conservative handling. Unsolicited response, hotplug, audio enabled/disabled, and format-change flags may be sticky, masked, or side-effecting. Using these masks without the correct clear/ack protocol can drop notifications or leave interrupt status stuck.

The repeated stream and endpoint patterns create copy-generation risk. `AZSTREAM5`-`AZSTREAM7`, `AZF0STREAM0`-`AZF0STREAM15`, CRC channel 0-7 groups, audio descriptor arrays, sink description arrays, and multichannel enable groups are highly repetitive. A single instance suffix, channel number, or mask-width mismatch would likely affect only one stream, endpoint, channel, or descriptor and may be hard to catch through compilation alone.

The VGA indexed-register block is legacy-sensitive. These fields may be touched in bring-up, VGA compatibility, firmware handoff, or diagnostic paths rather than normal atomic display mode-setting. Incorrect masks here can affect legacy console modes or boot-time display behavior in ways that are not covered by modern HDMI/DP tests.

This chunk has artificial boundaries. It starts partway through `AZSTREAM4_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS` and ends after the first `AZF0ENDPOINT1_AZALIA_F0_CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` masks, before the rest of endpoint 1's converter and pin fields. The final per-file research pass should treat those as chunking artifacts, not missing source content.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Kernel/driver builds for DCN 2.0/Navi10 display paths should compile every referenced field name and include this header together with `dcn_2_0_0_offset.h`.
- Generated-register validation should compare every `*_MASK` and `*__SHIFT` pair in this line range against AMD's register database and against the matching `mm...`/`ix...` addresses in `dcn_2_0_0_offset.h`.
- HDMI/DP audio playback tests should verify channel count, sample rate, bit depth, PCM/non-PCM passthrough, HBR, speaker allocation, channel-status values, and sink descriptor enumeration.
- Audio hotplug and format-change tests should exercise unsolicited responses, audio enable/disable interrupts, format-change flags, hotplug control/status, and forced response paths.
- DMA-style HDA stream tests should exercise stream reset/run, BDL pointer programming, cyclic buffer length, last valid index, LPIB readback/snapshot, FIFO ready, and completion/error interrupt behavior for streams 4-7 where hardware exposes them.
- Latency and diagnostics tests should confirm `AZF0STREAM0`-`AZF0STREAM15` FIFO allocation, latency counter controls/readbacks, CRC channel results, and GTC delta fields transition as expected.
- VGA compatibility testing should cover boot console, firmware handoff, and legacy VGA modes enough to detect broken `SEQ*`, `CRT*`, `GRA*`, or `ATTR*` field layouts.
- Suspend/resume, runtime power management, hotplug stress, and modeset stress should not lose audio routing, leave stale interrupt flags, corrupt HDA stream descriptors, or report inconsistent sink/descriptor data after power transitions.

Regression symptoms from bad constants include missing HDMI/DP audio, wrong audio format or channel mapping, silent non-PCM passthrough failure, repeated audio hotplug or format-change events, stuck stream-run/reset state, DMA descriptor errors, FIFO underrun/overrun reporting anomalies, incorrect LPIB position, invalid sink descriptors, broken boot VGA output, and mismatches in audio CRC or latency diagnostics.

## Cross-Chunk Notes

Earlier chunks of `dcn_2_0_0_sh_mask.h` define the beginning of `AZSTREAM4` and the preceding DCN 2.0 register-mask families. Later chunks complete `AZF0ENDPOINT1` and continue through subsequent generated DCN 2.0 hardware register definitions. The final per-file document should describe the whole source as a generated mask/shift contract for DCN 2.0 display, audio, and supporting hardware blocks rather than as algorithmic code.

### subset-b-001635: lines 62233-64601

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 62233-64601

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register field metadata for Azalia/HD-audio output endpoint registers. It contains only C preprocessor constants; there are no functions, structs, enums, variables, or executable control paths. Its purpose is to publish compile-time `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants used by AMDGPU display audio code when it composes or decodes 32-bit payloads accessed through Azalia endpoint index/data registers.

The path is under a local `ceph-client` source mirror, but this file is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior, distributed filesystem state, or storage persistence.

The assigned range covers 2,048 `#define` lines across repeated output endpoint blocks:

- Tail of `AZF0ENDPOINT1`, beginning at `AZALIA_F0_CODEC_CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES` and continuing through audio enable, audio enabled/disabled, and audio format-changed interrupt status.
- Complete `AZF0ENDPOINT2`, `AZF0ENDPOINT3`, and `AZF0ENDPOINT4` output endpoint field layouts.
- Beginning of `AZF0ENDPOINT5`, from converter audio-widget capability through the first mask of `AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR11`.

The chunk is repetitive by design. Each endpoint instance exposes the same HD-audio style converter and pin-widget fields so display code can bind logical display-audio objects to per-link hardware endpoints. The chunk boundaries are artificial: earlier lines contain the start of endpoint 1, and later lines complete endpoint 5.

## Important APIs, Types, And Macros

The macro namespace is the API surface:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned 32-bit field mask.
- Register names are endpoint-qualified, for example `AZF0ENDPOINT3_AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL__AUDIO_ENABLED_MASK`.

Important register/field families in this chunk:

- `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: converter widget capability bits such as channel count capability, input/output amplifier presence, format override, stripe, processing widget, unsolicited response support, connection-list support, digital/power-control flags, LR swap, delay, and widget type. This family is complete for endpoints 2-5 and starts before the chunk for endpoint 1.
- `...CONVERTER_CONTROL_CONVERTER_FORMAT`: HDA stream format fields for number of channels, bits per sample, sample base divisor/multiple/rate, and stream type.
- `...CONVERTER_CONTROL_CHANNEL_STREAM_ID`: channel ID and stream ID fields used to bind the endpoint converter to an HDA stream.
- `...CONVERTER_CONTROL_DIGITAL_CONVERTER`: digital converter enable and IEC-style status/control bits including validity, validity configuration, pre-emphasis, copyright, non-audio, professional, level, category code, and keepalive.
- `...CONVERTER_PARAMETER_STREAM_FORMATS` and `...CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES`: capability bitmaps for supported stream formats, sample rates, and bit depths. Endpoint 1 coverage begins at supported size/rates.
- `...CONVERTER_STRIPE_CONTROL`, `...CONTROL_RAMP_RATE`, `...CONTROL_GTC_EMBEDDING`, and `...GTC_COUNTER_DELTA*`: stripe capability/control, ramp rate, presentation-time/GTC embedding, clear-min/max-delta, group selection, and GTC counter delta/min/max fields.
- `...CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `...CODEC_PIN_PARAMETER_CAPABILITIES`: output pin widget and connector capability fields including jack detection, output/input capability, balanced I/O, HDMI, DP, VREF, and EAPD capability.
- `...CODEC_PIN_CONTROL_UNSOLICITED_RESPONSE`, `...RESPONSE_PIN_SENSE`, and `...WIDGET_CONTROL`: unsolicited response tag/enable, impedance-sense response, and output-enable control.
- `...CODEC_PIN_CONTROL_CHANNEL_SPEAKER`: speaker allocation, channel allocation, HDMI/DP connection flags, extra connection info, LFE playback level, level shift, and downmix inhibit.
- `...CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0` through `...AUDIO_DESCRIPTOR13`: EDID/SAD-derived audio descriptor fields. Descriptor 0 has stereo frequency support in the high byte; descriptors 1-13 carry max channels, supported frequencies, and descriptor byte 2. Endpoint 5 is cut off at descriptor 11.
- `...CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` and `...MULTICHANNEL_ENABLE2`: enable/mute/channel ID fields for channel pairs 01, 23, 45, 67 and additional multichannel extension fields.
- `...CODEC_PIN_CONTROL_RESPONSE_LIPSYNC` and `...RESPONSE_HBR`: video/audio lip-sync latency bytes and high-bit-rate audio capable/enable fields.
- `...CODEC_PIN_CONTROL_SINK_INFO0` through `...SINK_INFO8`: manufacturer ID, product ID, sink description length, two port-ID words, and packed sink description bytes.
- `...CODEC_PIN_CONTROL_HOT_PLUG_CONTROL`: `CLOCK_GATING_DISABLE`, `CLOCK_ON_STATE`, and `AUDIO_ENABLED`. This field set is directly used by the common display audio enable/disable path.
- `...CODEC_PIN_CONTROL_UNSOLICITED_RESPONSE_FORCE` and `...RESPONSE_CONFIGURATION_DEFAULT`: forced unsolicited response payloads, port connectivity, location, default device, connection type, color, miscellaneous, default association, and sequence.
- `...PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8`: IEC 60958 channel-status override fields for mode, source number, clock accuracy, word length, sampling frequency, original sampling frequency, sampling-frequency coefficient, MPEG surround, CGMS-A, and channel numbers for left/right plus channels 2-7.
- `...CODEC_PIN_ASSOCIATION_INFO`, `...DIGITAL_OUTPUT_STATUS`, `...LPIB_SNAPSHOT_CONTROL`, `...LPIB`, `...LPIB_TIMER_SNAPSHOT`, `...CODING_TYPE`, `...FORMAT_CHANGED`, `...WIRELESS_DISPLAY_IDENTIFICATION`, and `...REMOTE_KEEPALIVE`: association, output-active status, position/timer snapshots, coding type, format-change acknowledgement/reason/response, wireless-display ID, and remote keepalive fields.
- `AZF0ENDPOINTn_AZALIA_F0_AUDIO_ENABLE_STATUS`, `...AUDIO_ENABLED_INT_STATUS`, `...AUDIO_DISABLED_INT_STATUS`, and `...AUDIO_FORMAT_CHANGED_INT_STATUS`: endpoint enable state plus flag/mask/type fields for enable, disable, and format-change interrupts.

## Control Flow

This header chunk has no runtime control flow. It is preprocessor data consumed by DCN 2.0 display code through generated register descriptor tables and shared register helpers.

The runtime pattern for these fields is indexed Azalia endpoint access:

1. Select an endpoint-local indexed register through `AZALIA_F0_CODEC_ENDPOINT_INDEX`.
2. Read or write the endpoint-local 32-bit payload through `AZALIA_F0_CODEC_ENDPOINT_DATA`.
3. Use this header's shifts and masks to update or decode individual fields in that payload.

Local integration points show this pattern clearly. `display/dc/dce/dce_audio.h` defines `AUD_COMMON_REG_LIST(id)` with `SRI(AZALIA_F0_CODEC_ENDPOINT_INDEX, AZF0ENDPOINT, id)` and `SRI(AZALIA_F0_CODEC_ENDPOINT_DATA, AZF0ENDPOINT, id)`. `display/dc/resource/dcn20/dcn20_resource.c` instantiates `audio_regs[]` for endpoint instances 0 through 6 and builds common `dce_audio_shift`/`dce_audio_mask` structures using endpoint-data fields from this mask header. `display/dc/dce/dce_audio.c` then uses helpers such as `AZ_REG_READ`, `AZ_REG_WRITE`, and `set_reg_field_value` to validate endpoints, enable/disable Azalia audio, program EDID-derived audio descriptors, set speaker/channel allocation, configure HBR, fill sink metadata, and manage format-change and hotplug-related state.

Because this header is declarative, it does not enforce sequencing. Callers must order endpoint index selection, endpoint-data read-modify-write, clock-gating disable/restore, `AUDIO_ENABLED` updates, stream/channel binding, link/modeset bring-up, and interrupt/status handling.

## State And Persistence Behavior

The header itself stores no software state and has no persistence mechanism. It describes state held in DCN 2.0 display audio hardware.

The represented hardware state includes:

- Converter state: stream format, stream/channel IDs, digital converter control, supported format/rate/bit-depth capabilities, striping, ramp rate, GTC embedding, and GTC counter delta/min/max tracking.
- Pin capability and control state: widget and connector capabilities, unsolicited response configuration, pin sense, output enable, speaker/channel allocation, audio descriptors, multichannel channel-pair controls, lip-sync latency, HBR capability/enable, and HDMI/DP sink metadata.
- Hotplug/audio enable state: clock gating disable, clock-on state, `AUDIO_ENABLED`, forced unsolicited response data, configuration-default reporting, digital output active status, wireless display identification, and remote keepalive.
- IEC 60958 channel-status override state: sampling frequency, original sampling frequency, word length, clock accuracy, source and channel numbers, CGMS-A, MPEG surround, and override-enable bits.
- Position/timing state: LPIB snapshot lock, cyclic buffer wrap count, current LPIB, and LPIB timer snapshot.
- Event state: coding type, format-change flag/ack/reason/response, audio enable status, and audio-enabled/audio-disabled/audio-format-changed interrupt flag/mask/type bits.

Persistence is hardware-defined and not encoded in this generated file. Some fields are stable programming knobs until rewritten, modeset, reset, suspend/resume, power-gating transition, or GPU reset. Other fields are read-only capabilities/status, latched snapshots, sticky interrupt flags, self-clearing control bits, or write-sensitive acknowledgement fields. Names such as `*_STATUS`, `*_FLAG`, `*_MASK`, `*_TYPE`, `*_ENABLE`, `*_CAPABILITY`, `*_SNAPSHOT_LOCK`, `*_ACK_UR_ENABLE`, and `*_RESPONSE` indicate likely semantics, but access type, reset value, and side effects require the hardware register specification and surrounding driver usage.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.0 ASIC register header set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h` supplies the matching endpoint index/data register addresses and indexed endpoint register IDs.
- This file supplies only field layouts for packed endpoint payloads.
- AMD display register helpers (`SRI`, `SF`, `AZ_REG_READ`, `AZ_REG_WRITE`, `set_reg_field_value`, `get_reg_field_value`, and related macros) combine offset and mask/shift metadata into MMIO operations.
- Shared display-audio types in `display/include/audio_types.h`, `display/dc/dc_types.h`, and EDID/ELD handling feed the descriptor, speaker-allocation, latency, and HBR fields represented here.

Direct integration points visible in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`: includes the DCN 2.0 offset and mask headers, creates `audio_regs[]` for endpoint instances, and passes `audio_shift`/`audio_mask` into `dce_audio_create()`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h`: declares the common audio register, shift, and mask structures and maps endpoint index/data registers by instance.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c`: programs the hardware endpoint fields represented here during audio validation, enable/disable, descriptor setup, channel allocation, HBR setup, sink-info programming, DTO setup, and format-change handling.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_helpers.c` and DRM EDID paths: populate display audio capability data that is later reflected into the endpoint audio descriptor and speaker/channel fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.c`: exposes HDMI/DP audio ELD integration to the DRM audio component, which depends on the display audio endpoint programming being correct.

Functional integration surfaces are HDMI/DisplayPort audio bring-up, EDID/ELD-derived capability propagation, sink manufacturer/product/description reporting, HDA stream binding, multichannel speaker allocation, HBR audio, audio position reporting, audio format-change notification, hotplug audio enable/disable, and display-audio debug.

## Risks And Edge Cases

- Masks and shifts are hardware ABI. A one-bit error can compile successfully while programming the wrong HDA field, corrupting adjacent endpoint state, leaving audio disabled, misreporting sink capabilities, or breaking HDMI/DP audio.
- The range is generated and highly repetitive. Endpoint 2, 3, and 4 should be structurally identical, endpoint 1 is only a tail in this chunk, and endpoint 5 is only a prefix. Manual edits can easily introduce instance skew.
- The chunk boundaries are not semantic. Final per-file reconciliation must merge the preceding endpoint 1 converter prefix and the following endpoint 5 descriptor/status tail before drawing whole-file conclusions.
- DCN20 resource code exposes a finite set of audio endpoint instances through `audio_regs[]`; the presence of generated macros does not by itself prove every endpoint is active on every ASIC, board, link, or display topology.
- Indexed endpoint access is sequencing-sensitive. Selecting the wrong endpoint index/data pair, sharing the indexed window incorrectly, or racing another indexed access can read or write the wrong endpoint-local register.
- `HOT_PLUG_CONTROL` mixes clock-gating and audio-enable fields. Existing code disables clock gating around `AUDIO_ENABLED` changes; bypassing that pattern risks writes being dropped or audio state becoming inconsistent.
- Audio descriptors and speaker/channel allocation are EDID-derived. Bad masks for `MAX_CHANNELS`, `SUPPORTED_FREQUENCIES`, descriptor byte 2, speaker allocation, or channel allocation can expose invalid formats, hide valid formats, produce silence, or create wrong channel layouts.
- IEC 60958 override fields are format-sensitive. Incorrect sample frequency, original sample frequency, word length, channel number, CGMS-A, professional/non-audio, or validity settings can cause sink rejection, compressed-audio failures, or incorrect receiver metadata.
- Interrupt/status fields mix flag, mask, and type terminology. Misinterpreting them can lose audio enable/disable/format-change notifications, cause repeated unsolicited responses, or hide format-change events.
- LPIB and timer snapshot fields are likely latch-style state. Incorrect snapshot-lock handling can produce inconsistent audio position reporting.

## Test Signals

Useful validation is mainly build-time plus hardware display-audio behavior:

- Build AMDGPU/DC with DCN 2.0 support. Macro drift should fail in `dcn20_resource.c`, `dce_audio.h`, or shared audio helper code that consumes the generated shift/mask names.
- Cross-check the generated `*_SHIFT` and `*_MASK` pairs against the matching endpoint indexed register names in `dcn_2_0_0_offset.h` and against adjacent DCN/DCE generated headers where the Azalia endpoint layout is expected to be compatible.
- Exercise HDMI and DisplayPort audio on DCN 2.0 hardware across hotplug, modeset, stream start/stop, suspend/resume, multi-monitor endpoint selection, and audio enable/disable transitions.
- Validate EDID/ELD-derived audio capabilities: stereo fallback, multichannel layouts, compressed formats, HBR-capable formats, sample-rate and word-length exposure, speaker allocation, and sink manufacturer/product/description metadata.
- Test active format changes and verify descriptor, converter format, channel/stream ID, IEC 60958 status, HBR, and audio format-changed status/interrupt behavior update coherently.
- Check LPIB/position behavior during playback, especially around snapshot locking, cyclic buffer wrap count, resume, and stream restarts.
- Watch negative signals in kernel logs and user-visible behavior: missing HDMI/DP audio devices, silent playback, wrong channel layout, invalid sample-rate exposure, HBR formats unavailable, hotplug audio regressions, repeated audio enable/disable interrupts, audio format-change storms, LPIB position anomalies, or resume leaving `AUDIO_ENABLED` cleared.

## Cross-Chunk Notes

Earlier chunks of `dcn_2_0_0_sh_mask.h` contain the beginning of the Azalia endpoint region, including endpoint 0 and the start of endpoint 1 converter fields. Later chunks complete endpoint 5 and continue with later endpoint/input-endpoint definitions. The final per-file research document should treat this header as a generated DCN 2.0 hardware field-layout contract rather than algorithmic driver code, and should preserve the distinction between endpoint index/data addresses from the offset header and packed field definitions from this mask header.

### subset-b-001636: lines 64602-66921

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 64602-66921

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register field metadata. It contains no executable C logic; its interface is a large set of `#define` constants that map Azalia/HD-audio codec endpoint register fields to bit shifts and masks.

The path sits inside a local `ceph-client` source mirror, but the content belongs to the Linux AMDGPU display stack. In this line range it describes HDMI/DisplayPort audio codec endpoint state, not Ceph filesystem behavior.

The range starts in the middle of output endpoint 5 audio descriptor coverage, then covers the tail of output endpoint 5, all of output endpoints 6 and 7, and the beginning of input endpoints 0 through 3. The chunk ends inside `AZF0INPUTENDPOINT3_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE2`, so full endpoint 3 input-pin coverage continues in the next chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or storage objects in this chunk. The public API is the generated preprocessor naming scheme:

- `<register>__<field>__SHIFT` gives the bit position for a field.
- `<register>__<field>_MASK` gives the field mask used by `REG_SET_FIELD`, `REG_GET_FIELD`, `AZ_REG_READ`, `AZ_REG_WRITE`, and related AMD display register helpers.
- Prefixes such as `AZF0ENDPOINT6_...` and `AZF0INPUTENDPOINT1_...` distinguish repeated Azalia codec endpoint instances that otherwise expose nearly identical field layouts.

Important macro families in this range:

- `AZF0ENDPOINT5_AZALIA_F0_CODEC_PIN_CONTROL_*`: tail of an output pin endpoint, including audio descriptors 12 and 13, multi-channel channel-pair enable/mute/channel-id fields, lipsync, high-bit-rate audio capability/enable, sink manufacturer/product/port/description fields, hotplug/audio enable, forced unsolicited response payload, default pin configuration, IEC 60958 channel-status override bytes 0 through 8, association info, digital output activity, LPIB snapshot/timer fields, coding type, format-change state, wireless display identification, remote keepalive, and audio enable/disable/format-change interrupt status fields.
- `AZF0ENDPOINT6_AZALIA_F0_CODEC_CONVERTER_*`: complete output converter fields for endpoint 6, including widget capabilities, converter format, stream/channel identifiers, digital converter bits (`DIGEN`, validity, pre-emphasis, copy, non-audio, professional, level, category code, keepalive), supported stream/size/rate capabilities, stripe control, ramp rate, global-time-counter embedding, and GTC delta/min/max measurements.
- `AZF0ENDPOINT6_AZALIA_F0_CODEC_PIN_*`: complete output pin fields for endpoint 6, mirroring output endpoint 5 pin functionality: pin widget and pin capabilities, unsolicited response control, pin sense, output widget control, channel/speaker allocation, audio descriptors 0 through 13, multi-channel enable banks, lipsync, HBR, sink info, hotplug, forced unsolicited responses, default configuration, IEC 60958 channel status override, LPIB, coding/format-change, keepalive, and audio interrupt status.
- `AZF0ENDPOINT7_AZALIA_F0_CODEC_CONVERTER_*` and `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_*`: complete output endpoint 7 converter and pin field masks/shifts with the same structure as endpoint 6.
- `AZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_CONVERTER_*`: first input endpoint converter capabilities and controls, including audio widget capabilities, converter format, channel/stream IDs, digital converter status bits, supported formats, and supported sample sizes/rates.
- `AZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_PIN_*`: first input endpoint pin fields: input pin widget and pin capabilities, unsolicited response, input pin sense, input-enable widget control, multi-channel enable banks for channels 0-7, HBR response, channel allocation, hotplug/audio enable, forced unsolicited response payload, default configuration, LPIB snapshot/timer, input activity/status control, and audio infoframe fields.
- `AZF0INPUTENDPOINT1_*`, `AZF0INPUTENDPOINT2_*`, and the visible start of `AZF0INPUTENDPOINT3_*`: repeated input converter and pin field masks for additional input endpoints. Endpoint 3 reaches converter format, stream ID, digital converter, stream/rate capabilities, input pin capabilities, unsolicited response, input pin sense, widget input enable, multi-channel enable, and the start of multi-channel enable2 in this chunk.

## Control Flow

This header has no runtime control flow. It is declarative hardware metadata. Runtime behavior emerges when display/audio code combines these masks with the matching offset/index headers and register access helpers.

Representative flows in local consumers:

- `drivers/gpu/drm/amd/display/dc/dce/dce_audio.c` writes Azalia endpoint index/data registers, then uses field masks from this header to program HBR enablement, lipsync values, hotplug/audio enable, channel speaker allocation, audio descriptors from EDID SAD data, and sink identity/description fields.
- Older DCE paths such as `drivers/gpu/drm/amd/amdgpu/dce_v8_0.c` and `drivers/gpu/drm/amd/amdgpu/dce_v10_0.c` use the same indexed endpoint model with `RREG32_AUDIO_ENDPT` and `WREG32_AUDIO_ENDPT`, plus `REG_SET_FIELD`, to configure audio pin defaults, lipsync, speaker allocation, audio descriptors, and hotplug/audio-enable state.
- DCN20 integration files (`display/dc/resource/dcn20/dcn20_resource.c`, `display/dc/irq/dcn20/irq_service_dcn20.c`, `display/dc/gpio/dcn20/hw_factory_dcn20.c`, `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`, `display/dmub/src/dmub_dcn20.c`, and `amdgpu/gmc_v10_0.c`) include `dcn_2_0_0_sh_mask.h` with the matching offset header so generated register tables and service code can compile against the DCN20 register contract.

Because this file only provides constants, it does not enforce endpoint sequencing. Consumers must select the right endpoint index/data window, program fields in the order required by the Azalia codec interface, and preserve reserved bits when updating packed registers.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. The masks describe fields in MMIO-backed or indexed hardware registers whose values are owned by the DCN/Azalia hardware.

The represented state includes:

- Output endpoint audio capabilities and current programming: converter format, stream/channel IDs, supported formats/rates, digital converter channel status, HBR capability and enablement, multi-channel mute/enable/channel ID maps, speaker/channel allocation, audio coding descriptors, and IEC 60958 channel-status override fields.
- Output pin and sink metadata: manufacturer/product ID, port ID, sink description bytes, default pin configuration, DP/HDMI pin capabilities, hotplug/audio-enable state, pin sense, unsolicited-response configuration, and remote keepalive.
- Timing and synchronization aids: lipsync fields, GTC embedding enable/group, presentation time offset change, GTC delta/min/max fields, and LPIB/timer snapshot fields.
- Interrupt and event status: audio enabled/disabled/format-changed flags, masks, and types; input activity and channel-layout status; unsolicited response tags/enables; forced unsolicited response payloads.
- Input endpoint state: input converter format/stream/digital controls, input pin presence/impedance sensing, input widget enable, HBR/channel allocation, input activity state, and infoframe channel-count/allocation/valid bits.

Hardware persistence is not encoded here. Some fields are durable configuration until a modeset, audio stream reconfiguration, power transition, or codec reset. Other fields are status, interrupt, latch, snapshot, or force/ack controls with side effects. Names such as `*_INT_STATUS`, `*_FORMAT_CHANGED`, `*_LPIB_SNAPSHOT_LOCK`, `*_UNSOLICITED_RESPONSE_FORCE`, `*_CLEAR_GTC_COUNTER_MIN_MAX_DELTA`, and `*_PRESENCE_DETECT` signal behavior that must be confirmed against the hardware specification and surrounding driver logic before changing access patterns.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header contract:

- `dcn_2_0_0_offset.h` supplies the MMIO offsets and indexed-register addresses.
- `dcn_2_0_0_sh_mask.h` supplies these field masks and shifts.
- AMD display register helpers consume the macros through `REG_SET_FIELD`, `REG_GET_FIELD`, `REG_UPDATE`, `REG_READ`, `REG_WRITE`, `AZ_REG_READ`, `AZ_REG_WRITE`, and endpoint-specific indexed access wrappers.

Integration points include:

- DC display audio programming in `drivers/gpu/drm/amd/display/dc/dce/dce_audio.c`.
- Legacy AMDGPU display/audio programming in `drivers/gpu/drm/amd/amdgpu/dce_v8_0.c` and `drivers/gpu/drm/amd/amdgpu/dce_v10_0.c`.
- DCN20 register-table and service construction in `display/dc/resource/dcn20`, `display/dc/irq/dcn20`, `display/dc/gpio/dcn20`, `display/dc/clk_mgr/dcn20`, and `display/dmub/src`.
- Higher-level DRM/Display Core flows that derive audio state from connector EDID, ELD/SAD audio descriptors, link type, stream timing, hotplug state, suspend/resume, and modeset/audio-enable transitions.

## Risks And Edge Cases

- The macros are a hardware ABI. Incorrect mask or shift values can compile cleanly while programming the wrong bitfield, causing silent HDMI/DP audio failures, bad channel maps, invalid sample-rate/bit-depth advertisement, lost HBR audio, or broken sink detection.
- Endpoint families are highly repetitive. Manual edits can easily drift one instance (`ENDPOINT6` versus `ENDPOINT7`, or `INPUTENDPOINT1` versus `INPUTENDPOINT2`) while leaving adjacent instances correct, producing connector- or stream-count-specific failures.
- The chunk boundary is not semantic. It starts after earlier endpoint 5 descriptor fields and ends mid-way through input endpoint 3 multi-channel enable2, so whole-file analysis must merge adjacent chunks before drawing complete endpoint coverage conclusions.
- Packed bitfields require read-modify-write discipline. Fields such as channel status override, default configuration, multi-channel enable/mute/channel IDs, interrupt mask/type/flag bits, and input status controls share registers; writing a full literal without preserving unrelated bits can corrupt neighboring state.
- Interrupt and event fields can have side effects. Audio enabled/disabled/format-change status, unsolicited response force, snapshot lock, and GTC min/max clear fields may be sticky, self-clearing, write-one-to-clear, or latch-triggering depending on hardware semantics outside this generated header.
- Output and input endpoint naming is similar but not interchangeable. Using output pin masks on input endpoint registers, or vice versa, can produce plausible-looking code that targets the wrong indexed register layout.
- Sink information fields pack EDID-derived identity and descriptions into byte lanes. Bad masks or lengths can expose wrong ELD/sink metadata to userspace or audio clients.
- HBR, IEC 60958, channel allocation, and audio descriptor fields affect standards-visible audio behavior. Regressions may appear only with specific receivers, formats, channel counts, compressed streams, or DisplayPort/HDMI link modes.

## Test Signals

Useful validation is mostly compile-time plus hardware behavior:

- Build AMDGPU/DC with DCN20 support; missing or renamed macros should fail in DCN20 resource/service code and audio paths that include the generated headers.
- Diff this generated mask chunk against adjacent ASIC families or regenerated headers to catch unintended endpoint-instance drift, especially for repeated endpoint 6/7 and input endpoint 0-3 families.
- Exercise HDMI and DisplayPort audio on DCN20 hardware across multiple connectors and streams: enable/disable audio, hotplug displays, modeset with audio active, suspend/resume, and switch between HDMI and DP sinks.
- Validate EDID/SAD-derived programming by checking supported audio formats, sample rates, bit depths, speaker allocation, channel count, and sink identity as observed by ALSA/ELD userspace.
- Test HBR and compressed/high-channel-count formats where available, plus basic PCM stereo and multi-channel PCM.
- Watch for kernel log errors, missing audio devices, wrong ELD contents, EDID/audio descriptor parsing anomalies, hotplug flapping, lost audio after modeset, stale audio after unplug, format-change interrupt storms, and failures limited to high endpoint counts.
- For input endpoint coverage, validate input activity/status, infoframe validity, channel allocation, and multichannel mapping on hardware or test paths that expose Azalia input endpoints.

### subset-b-001637: lines 66922-68033

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 66922-68033

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register field metadata. It contains no executable C code, functions, structs, or variables. Its purpose is to publish compile-time bit shifts and bit masks for Azalia/HD-audio codec input endpoint registers used by the AMDGPU display stack.

The path is inside a local `ceph-client` source mirror, but this file is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem logic.

The range covers the end of `AZF0INPUTENDPOINT3` and the full repeated mask/shift definitions for `AZF0INPUTENDPOINT4`, `AZF0INPUTENDPOINT5`, `AZF0INPUTENDPOINT6`, and `AZF0INPUTENDPOINT7`. These are the Azalia function 0 codec input endpoint indirect-register views used for display audio. Each endpoint is exposed through endpoint index/data MMIO registers in the companion offset header; the macros in this chunk describe how to pack and unpack the data values read or written through those indirect registers.

The repeated endpoint families describe:

- Input converter capabilities and stream format controls.
- Converter channel/stream IDs and digital converter status/control bits.
- Supported stream formats, sample rates, and bit depths.
- Input pin widget capabilities and pin capabilities for HDMI/DP-style audio pins.
- Unsolicited response control and forced unsolicited response payloads.
- Input pin sense and widget input-enable state.
- Multichannel enable, mute, and channel ID fields for channels 0 through 7.
- HBR capability/enable state, channel allocation, hot-plug audio enable/clock-gating state, pin configuration defaults, link-position-in-buffer snapshots, input status, and audio infoframe status.

The source chunk starts in the middle of the `AZF0INPUTENDPOINT3_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE2` masks. The preceding shifts for endpoint 3 multichannel-enable2 live immediately before this range, so final per-file reconciliation must merge adjacent chunks for complete endpoint 3 coverage. Endpoint 4 through endpoint 7 are complete in this chunk.

## Important APIs, Types, And Macros

There are no local APIs or types in this range. The public interface is the generated preprocessor naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for a field in the 32-bit indirect register payload.
- The companion offset header provides `ixAZF0INPUTENDPOINT*_...` indirect indices and `mmAZF0INPUTENDPOINT*_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX/DATA` MMIO register offsets.
- Display audio code uses these through register helper macros such as `SF`, `REG_SET`, `REG_READ`, `REG_UPDATE`, `set_reg_field_value`, and `get_reg_field_value`.

Important macro families in this chunk:

- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: describes converter widget properties. Fields include audio channel capability, input/output amplifier presence, amplifier-parameter override, format override, striping, processing widget, unsolicited response capability, connection list, digital flag, power control, LR swap, widget delay, and widget type.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`: describes stream format programming with number of channels, bits per sample, sample base divisor, sample base multiple, sample base rate, and stream type.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`: maps 4-bit channel ID and 4-bit stream ID fields.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`: contains digital-converter status/control fields such as `DIGEN`, validity, validity configuration, pre-emphasis, copy, non-audio, professional mode, level, category code, and keepalive.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS`: exposes the full 32-bit stream-format support bitmap.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES`: splits supported audio rates and bit capabilities into low and high fields.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: describes pin widget capabilities, similar to converter widget capabilities but without the converter-only format-override field in this chunk.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_CAPABILITIES`: describes pin sense/output/input/HDMI/DP capability bits, VREF control, EAPD capability, and balanced I/O capability.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE`: packs a 6-bit tag and enable bit.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_INPUT_PIN_SENSE`: exposes impedance sense and presence detect.
- `AZF0INPUTENDPOINT[4-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_WIDGET_CONTROL`: currently only the input-enable bit in this generated range.
- `AZF0INPUTENDPOINT[3-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` and `...ENABLE2`: pack enable, mute, and 4-bit channel ID fields for multichannel lanes 0-3 and 4-7 respectively. This chunk includes endpoint 3's tail masks for channels 4-7 and complete endpoint 4-7 definitions.
- `AZF0INPUTENDPOINT[3-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR`: exposes HBR capable and HBR enable bits.
- `AZF0INPUTENDPOINT[3-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_CHANNEL_ALLOCATION`: exposes the 8-bit HDMI/CEA channel-allocation value.
- `AZF0INPUTENDPOINT[3-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL`: contains clock-gating disable, clock-on state, and audio-enabled bits.
- `AZF0INPUTENDPOINT[3-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE_FORCE`: provides a 26-bit unsolicited-response payload and a force bit.
- `AZF0INPUTENDPOINT[3-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`: maps HD-audio pin default configuration fields: sequence, default association, misc, color, connection type, default device, location, and port connectivity.
- `AZF0INPUTENDPOINT[3-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `...LPIB`, and `...LPIB_TIMER_SNAPSHOT`: define fields for locking an LPIB snapshot, cyclic-buffer wrap count, full LPIB value, and timer snapshot.
- `AZF0INPUTENDPOINT[3-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL`: exposes input activity, channel layout, and unsolicited-response enable bits for input activity and channel-layout/channel-status-infoframe changes.
- `AZF0INPUTENDPOINT[3-7]_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME`: exposes channel count, channel allocation, infoframe byte 5, and infoframe-valid status.

## Control Flow

This header chunk has no runtime control flow. It is declarative field metadata. Runtime sequencing is implemented by consumers in the display audio path.

The important runtime pattern is indirect Azalia register access:

1. The display audio resource table selects an audio endpoint instance, using `AUD_COMMON_REG_LIST(id)` in `display/dc/dce/dce_audio.h` and the DCN20 `audio_regs[]` table in `display/dc/resource/dcn20/dcn20_resource.c`.
2. `dce_audio.c` writes an indirect register index to `AZALIA_F0_CODEC_ENDPOINT_INDEX`.
3. It reads or writes the register payload through `AZALIA_F0_CODEC_ENDPOINT_DATA`.
4. Field helpers use masks and shifts from generated `*_sh_mask.h` headers to set or extract fields in that payload.

Representative consumers found in this tree:

- `display/dc/resource/dcn20/dcn20_resource.c` includes `dcn_2_0_0_sh_mask.h`, builds `audio_regs[]` for audio instances 0 through 6, and initializes `audio_shift`/`audio_mask` from generated field macros. The DCN20 table only names endpoint index/data and common function fields directly; per-pin/per-converter indirect register fields are reached through the generic Azalia helper macros.
- `display/dc/dce/dce_audio.h` defines `AUD_COMMON_REG_LIST`, `AUD_COMMON_MASK_SH_LIST`, `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask` used by DCE/DCN audio blocks.
- `display/dc/dce/dce_audio.c` defines `AZ_REG_READ` and `AZ_REG_WRITE`, which call `read_indirect_azalia_reg()` and `write_indirect_azalia_reg()`. These helpers program `AZALIA_ENDPOINT_REG_INDEX` and move payloads through `AZALIA_ENDPOINT_REG_DATA`.
- `dce_aud_az_enable()` and `dce_aud_az_disable()` read `AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL`, change `CLOCK_GATING_DISABLE` and `AUDIO_ENABLED`, and write the value back. Those generic field names correspond to per-endpoint hot-plug-control fields represented in this chunk for input endpoints 3-7.
- `set_high_bit_rate_capable()` reads `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_HBR`, updates `HBR_CAPABLE`, and writes it back. This chunk defines the same HBR bit layout for input endpoint 3 tail state and endpoints 4-7.
- `dce_aud_az_configure()` and related audio configuration code use EDID-derived audio information, DP/HDMI signal type, channel count, sample rates, and latency data to configure Azalia codec state and expose capabilities to the audio driver.

Because the header only supplies masks and shifts, it does not impose operation ordering. Callers must know when endpoint state is valid, when the audio endpoint is assigned to a pipe/connector, when hotplug/audio enable should be toggled, and how hardware treats read-only, write-one-to-clear, self-clearing, sticky, and latched fields.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. It describes hardware register fields.

The represented hardware state includes:

- Converter capability state: widget type, digital capability, stream-format capability, rate/bit-depth capability, power-control capability, LR swap capability, and processing/connection/unsolicited-response support.
- Converter runtime state: number of channels, bits per sample, sample-rate encoding, stream type, channel ID, stream ID, digital converter enable, status bits, category code, and keepalive.
- Pin capability state: HDMI/DP capability bits, input/output capability bits, jack/presence/impedance capability, EAPD capability, VREF capability, and default pin configuration fields.
- Pin runtime state: unsolicited-response enable/tag, forced unsolicited response payload, pin sense presence, input-enable bit, multichannel enable/mute/channel mapping, HBR exposed capability and enable state, channel allocation, and hot-plug audio enable/clock gating state.
- Audio stream status state: LPIB snapshot controls and values, input activity, channel-layout state, infoframe change unsolicited-response enable, infoframe channel count/allocation/byte 5, and infoframe valid bit.

Persistence is hardware-defined. Some fields are capability/status fields that software reads to expose behavior to the OS audio stack. Other fields are programming knobs that remain active until modeset reconfiguration, endpoint reassignment, audio disable, display power gating, GPU reset, suspend/resume, or driver teardown. Snapshot and status fields may be transient or latched. Unsolicited response, hot-plug, clock-gating, and forced-response fields can have side effects when written.

Software-visible persistence around these registers appears in higher layers:

- `amdgpu_dm_audio_init()` initializes `adev->mode_info.audio` pin state from `dc->res_pool->audio_count`.
- `amdgpu_dm_commit_audio()` updates connector-to-audio-instance mappings under `audio_lock` and notifies the DRM audio component of ELD changes.
- DC hardware sequencing disables and releases dynamic audio endpoints when a stream is torn down, including `pipe_ctx->stream_res.audio->funcs->az_disable()` and `update_audio_usage()` in DCN hardware sequencing paths.

The masks in this header are therefore part of a hardware ABI boundary. They must match the endpoint data payload format or those higher-level audio state transitions will manipulate the wrong bits.

## Dependencies And Integration Points

This chunk depends on the generated AMD DCN 2.0 register-header ecosystem:

- `dcn_2_0_0_offset.h` supplies the matching `ixAZF0INPUTENDPOINT*_...` indirect register indices and endpoint index/data MMIO offsets.
- `dcn_2_0_0_sh_mask.h` supplies the field masks and shifts in this chunk plus the earlier/later field families.
- AMD display register helper macros (`SR`, `SRI`, `SF`, `REG_SET`, `REG_READ`, `REG_UPDATE`, `set_reg_field_value`, and related helpers) consume the masks and shifts.
- Audio resource setup in `display/dc/resource/dcn20/dcn20_resource.c` ties DCN20 instances to the common DCE audio helper.
- Shared display audio logic in `display/dc/dce/dce_audio.c` performs endpoint indirect reads/writes and programs HDMI/DP display-audio state.
- DRM audio component integration in `display/amdgpu_dm/amdgpu_dm.c` exposes ELD/audio instance changes to the OS audio side.

Direct include points for `dcn_2_0_0_sh_mask.h` in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`

Functional integration points include display audio endpoint allocation, HDMI/DP audio enable/disable, HBR audio capability exposure, EDID/ELD audio capability propagation, channel allocation and multichannel mapping, audio status/infoframe reporting, hotplug-audio state, and LPIB snapshot/status observation.

## Risks And Edge Cases

- These masks and shifts are hardware ABI. A wrong mask or shift can compile cleanly while silently programming the wrong bit in an indirect register.
- The chunk boundary is non-semantic. It begins after endpoint 3 multichannel-enable2 shifts and includes only endpoint 3 tail masks plus later endpoint 3 pin-control families. Adjacent chunks are required for a complete endpoint 3 summary.
- Repetition across endpoints 4-7 creates off-by-one and copy/paste risk. Endpoint field layouts are expected to stay identical, but each macro name encodes a specific endpoint instance. A single generated drift can affect only one audio endpoint and only when that endpoint is selected.
- Indirect register access increases blast radius. Software writes an index first and a data payload second; a stale or wrong index combined with correct-looking masks can update a different Azalia register.
- Some names imply side effects, but the header does not encode access type. `UNSOLICITED_RESPONSE_FORCE`, `HOT_PLUG_CONTROL`, `LPIB_SNAPSHOT_CONTROL`, and status/control fields may be read-only, write-sensitive, sticky, self-clearing, or latched depending on hardware documentation.
- HBR, channel allocation, multichannel enable, and stream-format fields are interoperability-sensitive. Bad values can cause no audio, channel swapping, muted channels, incorrect surround layout, receiver incompatibility, or failures with high-bit-rate compressed audio formats.
- `AUDIO_ENABLED` and `CLOCK_GATING_DISABLE` sequencing matters. Toggling hot-plug/audio state while the endpoint is assigned or while the display/audio clock path is changing can cause transient audio loss or stale state exposed to the OS audio driver.
- LPIB and timer snapshot fields describe live stream position state. Misinterpreting snapshot lock or wrap-count bits can produce incorrect buffer-position reporting and audio synchronization bugs.
- Pin configuration default fields affect how the codec presents topology/configuration to the audio driver. Bad port connectivity, default device, association, or sequence fields can expose the wrong jack/port layout.
- Because DCN20 code creates only the resource tables and relies heavily on shared DCE audio helpers, build tests catch missing macro names but not necessarily wrong numeric bit definitions.

## Test Signals

Useful validation combines generated-header checks, build coverage, and display-audio behavior on DCN20 hardware:

- Build AMDGPU/DC with DCN20 enabled. Missing or renamed fields should break `dcn20_resource.c`, shared DCE audio helpers, or related generated field initialization paths.
- Diff this chunk against adjacent generated families such as `dcn_2_1_0_sh_mask.h`, `dcn_3_0_0_sh_mask.h`, and `dcn_3_2_0_sh_mask.h` where endpoint register layouts are expected to remain compatible.
- Verify endpoint index/data access by reading/writing non-destructive Azalia endpoint fields through debug or instrumented driver paths and confirming the expected bit positions.
- Exercise HDMI and DisplayPort audio on hardware across endpoint instances, including hotplug, modeset, suspend/resume, and audio stream enable/disable cycles.
- Validate common audio formats: stereo PCM, multichannel PCM, high sample rates, different bits-per-sample settings, and HBR/compressed formats where supported by sink and link.
- Check channel mapping and channel allocation with multichannel test content; failures may show as swapped channels, silent channels, or incorrect receiver speaker layout.
- Confirm ELD/audio component notifications after connector hotplug and modeset. User-visible signals include `aplay -l`, desktop audio device presence, and correct ELD content for the active connector.
- Watch kernel logs for audio endpoint allocation/release issues, HPD flapping, EDID/ELD changes without audio device updates, audio disable paths leaving endpoints acquired, or GPU reset/suspend resume regressions.
- Monitor runtime symptoms: no HDMI/DP audio, HBR formats missing from the audio driver, clicks/pops during modeset, audio clock instability, stale connected state, incorrect LPIB position reporting, or receiver channel layout mismatch.
