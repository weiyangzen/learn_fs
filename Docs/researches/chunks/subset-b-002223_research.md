# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 12777-15093

## Scope And Purpose

This chunk is part of the generated AMD DCN 4.2.0 register shift/mask header. It contains preprocessor constants that describe bit positions and bit masks for display microcontroller, power-gating, interrupt-status, timer-position, and interrupt-destination registers. The companion offset header provides register addresses; this header provides the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants used by AMDGPU Display Core and DMUB register helpers to access individual hardware fields.

The range contains 2,190 `#define` lines across 116 register names: 1,096 shift definitions and 1,094 mask definitions. The mismatch is expected for this chunk because it starts in the middle of `DC_PERFMON1_PERFCOUNTER_STATE` mask definitions and ends in the middle of `DIG_INTERRUPT_DEST` shift definitions. There are no C functions, structs, or executable code in this range.

## Register Families In This Chunk

The first section completes the `DC_PERFMON1` block, covering perfmon control, report count, counter-off interrupt enable/status/ack, clock/run-enable selection, counter interrupt status/ack bits, and low/high counter value read fields.

The `dce_dc_dmu_dc_pg_dispdec` address block defines display power-gating controls. `DOMAIN*_PG_CONFIG` and `DOMAIN*_PG_STATUS` fields cover force-on, gate request, desired power state, and PGFSM power status for domains 0-3, 16-19, and 22-26. `DCPG_INTERRUPT_STATUS*` and `DCPG_INTERRUPT_CONTROL_*` expose power-up/power-down interrupt occurrence, mask, and clear bits for those domains. `DC_IP_REQUEST_CNTL` and `LONO_MEM_PWR_REQ_CNTL` provide small control fields for IP requests and LONO memory power request disablement.

The `dce_dc_dmu_dmu_dcperfmon_dc_perfmon_dispdec` block defines a complete `DC_PERFMON2` instance. It mirrors the perfmon counter-control shape used by `DC_PERFMON1`: event selection, counted-value source/type, increment mode, hardware stop controls, restart and interrupt enable, counter state selection, perfmon state/report controls, cvalue interrupt/status/ack fields, and low/high counter reads.

The `dce_dc_dmu_dmu_misc_dispdec` block contains miscellaneous DMU controls: `CC_DC_PIPE_DIS`, `DMU_CLK_CNTL`, DMCUB/SMU interrupt messaging, ZSC control/status, down-spread/deep-sleep allowance forcing, CGTT block control for display and SOC clocks, and ZPR clock ungate delay.

The `dce_dc_dmu_ihc_dispdec` block dominates the rest of the chunk. It defines GPU timer start-position/read controls, `DISP_INTERRUPT_STATUS` plus `DISP_INTERRUPT_STATUS_CONTINUE` through `CONTINUE25`, and interrupt-destination registers. The status chain covers OPTC underflow, OTG snapshot/force-vsync/force-count/TRIGA/TRIGB/vsync/vstartup/vready/vupdate/vertical/DRR events, DIGA-DIGH fast-training and video-stream-disable events, HPD and HPD RX events, AUX software/link-service done events, DIO ALPM, RBBMIF timeout, I2C events, HPO ALPM wake, MCIF CWB/DWB events, perfmon interrupts for DCCG/DMU/DIO/WB/DPP/DWB/MPC/OPP/DSC/HPO, histogram-ready interrupts, DCCG vsync latch and OTG DRR timing updates, ODM underflow, AZ audio endpoint events, I2C DDC hardware/read-request events, DCPG power events, DMCUB mailbox/timer/general-data/fault events, DSC core errors, DPIA, and DMCUB register inbox/outbox interrupts.

The interrupt-destination section maps interrupt sources to destination selector bits for DCCG, DMU, DCPG, MMHUBBUB, writeback, DCHUB, DCHUB perf counters, DPP perf counters, MPC, OPP, OPTC, OTG0-OTG5, and the beginning of DIG destination routing.

## Important APIs, Types, And Macros

This chunk's API surface is the generated macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the bit offset for a hardware field.
- `REGISTER__FIELD_MASK` gives the unshifted mask used to isolate or update that field.
- Register names are grouped by generated address-block comments, while actual MMIO addresses come from `dcn_4_2_0_offset.h`.

These macros are consumed by AMD register helper idioms such as `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `REG_GET`, `REG_SET`, and `REG_UPDATE`. For DCN 4.2, `display/dmub/src/dmub_dcn42.c` includes both `dcn_4_2_0_offset.h` and this header, then initializes DMUB register tables by expanding field masks and shifts through `FD_MASK` and `FD_SHIFT`. `display/dc/irq/dcn42/irq_service_dcn42.c` also includes this header for DCN 4.2 interrupt programming.

## Control Flow And Hardware Behavior

The file has no software control flow. It describes hardware state machines and interrupt-routing surfaces that other code drives through read-modify-write and polling sequences.

Power-gating fields model a control/status flow: software or firmware can request force-on/gate states, observe desired power state and PGFSM status, then use DCPG interrupt status/control fields to detect and clear power-up or power-down transitions.

Perfmon fields model counter configuration and reporting flow. Callers select an event and counted-value source, choose increment/run-enable behavior, optionally enable restart or counter-off interrupts, then read low/high counter values and acknowledge counter interrupts.

The IHC interrupt-status chain is a hardware event fan-in. Each `DISP_INTERRUPT_STATUS_CONTINUE*` register exposes a subset of latched display events and usually reserves bit 31 as the continuation bit for the next status register. IRQ handling code can walk or decode this chain to identify events from timing generators, display pipes, hotplug/AUX/I2C, DMCUB mailbox/fault paths, performance counters, power-gating domains, and display compression blocks.

The interrupt-destination registers are routing controls. Their fields select where a given interrupt source is delivered, which is distinct from status, clear, and mask semantics in the interrupt-control registers.

GPU timer start-position registers encode per-pipe event positions for vupdate, vstartup, vready, flip, vupdate-no-lock, and flip-away events. These fields support precise timing of display events relative to OTG and pipe timing.

## State And Persistence Behavior

The header itself stores no runtime state and persists no data; it is a compile-time hardware ABI description.

The underlying registers represent live device state. Status fields are transient or latched hardware observations, such as perf counter interrupts, power-gating transitions, DMCUB mailbox readiness, HPD/AUX/I2C events, OTG timing events, underflow/error events, and perfmon counter events. Control fields such as perfmon configuration, interrupt masks/clears, destination routing, clock-gating controls, power-gating requests, and timer start-position encodings persist in hardware until reset, power transition, firmware update, or another kernel/firmware writer changes them.

The macros do not encode access type, reset value, write-one-to-clear behavior, self-clearing behavior, or firmware ownership. Callers must rely on hardware register specs and existing DCN/DMUB sequencing when deciding whether a field can be written, polled, acknowledged, or preserved.

## Dependencies And Integration Points

The direct dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h`, which must remain synchronized with this shift/mask file. Offset/header drift would make otherwise-correct field operations hit the wrong register or bit.

DCN 4.2 integration points in this source tree include:

- `display/dmub/src/dmub_dcn42.c`, which builds DMUB register tables from `FD_MASK` and `FD_SHIFT`.
- `display/dc/irq/dcn42/irq_service_dcn42.c`, which maps DCN interrupt source IDs into DAL interrupt sources and includes this header for register programming.
- `display/dc/resource/dcn42/dcn42_resource.c`, `display/dc/clk_mgr/dcn42/dcn42_clk_mgr.c`, and DCN 4.2 GPIO factory/translation code, which include the same offset and mask headers for display resource, clock, and GPIO register access.
- Firmware integration through the DCN 4.2 DMCUB binary path and DMCUB mailbox/outbox interrupt fields represented in this chunk.

The chunk also depends on broader AMDGPU Display Core conventions: generated field macros must match register helper naming, repeated instance layouts must remain consistent across OTG/DIG/DPP/DSC/HPO instances, and interrupt source naming must match the `ivsrcid/dcn` definitions used by IRQ services.

## Risks And Edge Cases

Generated-header drift is the primary risk. A wrong shift, mask, register name, or stale offset pairing can silently corrupt unrelated hardware fields because register helpers compile cleanly even when the hardware map is wrong.

This chunk contains several similarly named interrupt concepts: status, continuation, control mask/clear, and destination. Confusing these can drop interrupts, route them to the wrong consumer, fail to acknowledge latched events, or create interrupt storms.

The range starts and ends mid-register. Any per-register completeness analysis must merge adjacent chunks before concluding that `DC_PERFMON1_PERFCOUNTER_STATE` or `DIG_INTERRUPT_DEST` is missing fields or masks.

Power-gating and clock-gating fields are sensitive to firmware and hardware ownership. Incorrect writes can keep display domains forced on, gate active hardware, break low-power entry/exit, or race with DMUB/SMU-managed power transitions.

Perfmon and timer-position fields are low-level diagnostics/timing surfaces. Incorrect event selection, start-position encoding, or interrupt enablement can cause misleading telemetry, missed timing events, or excessive interrupts without obvious functional failure.

Reserved or absent bits are not described by these macros. Callers should update fields with read-modify-write helpers and preserve unrelated bits rather than writing whole-register literals.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for DCN 4.2 display, DMUB, IRQ, resource, clock manager, and GPIO code that includes `dcn_4_2_0_sh_mask.h`.
- Generated-register consistency checks that verify each complete `REGISTER__FIELD__SHIFT` has a matching `REGISTER__FIELD_MASK`, while allowing the known chunk-boundary partials.
- Cross-header checks that every register represented here has a matching DCN 4.2 offset definition and that instance families such as `OTG0_INTERRUPT_DEST` through `OTG5_INTERRUPT_DEST` preserve identical bit layouts where expected.
- IRQ smoke tests for vblank/vupdate/vline, page flip, HPD/HPDRX, AUX/I2C, DMCUB outbox/inbox, DSC error, DPIA, underflow, and DCPG power events.
- Suspend/resume and display idle tests that exercise DCPG domain transitions, DMU clock gating/deep-sleep allowance, and DMCUB/SMU interrupt messaging.
- Hardware or simulator perfmon tests that program DC perf counters, trigger counter-off interrupts, read low/high values, and verify status/ack behavior.
- Mode-set and variable-refresh tests that exercise OTG DRR timing, vstartup/vready/vupdate-no-lock, GPU timer start-position fields, and interrupt routing under multi-display configurations.
