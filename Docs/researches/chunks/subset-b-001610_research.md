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
