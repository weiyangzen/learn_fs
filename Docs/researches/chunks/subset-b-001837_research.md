# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 9705-12036

## Scope

This chunk is a generated DCN 3.1.4 register-field shift/mask slice from `dcn_3_1_4_sh_mask.h`. It contains preprocessor constants only: `_SHIFT` macros for field low-bit positions, `_MASK` macros for raw 32-bit register masks, and generated comments that group fields by MMIO register and address block. There are no C functions, structs, enums, loops, branches, allocations, or driver-owned state objects in this range.

The slice starts in the tail of `DC_PERFMON0_PERFCOUNTER_CNTL`, completes `DC_PERFMON0`, defines full `DC_PERFMON1` and `DC_PERFMON2` blocks, covers DC power-gating (`DCPG`) domain control/status and interrupt controls, covers DMU miscellaneous controls, covers the DMCU firmware/register/interrupt/mailbox register surface, and ends in the first `DISP_INTERRUPT_STATUS` fields in the DMU IHC block.

## Purpose And Hardware Surface

The purpose of this header range is to provide the bit-layout ABI between AMDGPU Display Core code and DCN 3.1.4 display hardware. Companion generated offset headers identify the MMIO register addresses; this header identifies each field's bit shift and mask so callers can pack values, decode readbacks, and perform read/modify/write updates through the display register helpers without embedding magic bit numbers.

Major hardware areas represented here:

- Display perfmon instances `DC_PERFMON0`, `DC_PERFMON1`, and `DC_PERFMON2`, including event selection, counter value selection, increment mode, hardware start/stop/count-off controls, per-counter state readback, global perfmon state, counter interrupts, and low/high counter readback windows.
- `dce_dc_dmu_dc_pg_dispdec` power-gating controls for domains 0-3 and 16-19, with force-on/gate controls, desired power-state readback, PGFSM power status, power-up/down interrupt status, interrupt mask/clear controls, and `DC_IP_REQUEST_CNTL`.
- `dce_dc_dmu_dmu_misc_dispdec` miscellaneous DMU controls, including DC pipe disable/DMCUB enable, DMU/DMCU/RBBMIF clock gating/status, DMCU ERAM/IRAM memory power controls, DMCU-to-SMU and SMU-to-DC interrupt registers, Z-state/SOC access controls, and deep-sleep force controls.
- `dce_dc_dmu_dmcu_dispdec` DMCU microcontroller controls, including reset, clock/soft reset, firmware address/checksum, RAM access windows for ERAM/IRAM, event triggers, uC internal/static-screen interrupt status, ABM, vblank, DCPG, OTG range timing, perfmon, DPRX, DCIO DPCS, and mailbox/communication registers.
- `dce_dc_dmu_ihc_dispdec` interrupt-host-controller fields, including GPU timer start-position/read controls and the first `DISP_INTERRUPT_STATUS` bits for OPTC underflow, OTG1 events, DP fast-training/stream-disable, HPD/AUX/I2C, DIO ALPM, RBBMIF timeout, DMCU, and ABM events.

## Important Definitions

The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a register field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit mask for that field.
- `// addressBlock: ...` comments identify the display hardware aperture for following registers.
- `//<REGISTER>` comments group field macros by MMIO register.

Important field families in this chunk:

- `DC_PERFMON*_PERFCOUNTER_CNTL` fields expose `PERFCOUNTER_EVENT_SEL`, `PERFCOUNTER_CVALUE_SEL`, `PERFCOUNTER_INC_MODE`, `PERFCOUNTER_HW_CNTL_SEL`, `PERFCOUNTER_RUNEN_MODE`, `PERFCOUNTER_CNTOFF_START_DIS`, `PERFCOUNTER_RESTART_EN`, `PERFCOUNTER_INT_EN`, `PERFCOUNTER_OFF_MASK`, `PERFCOUNTER_ACTIVE`, and selector bits. Instance 0 begins mid-register at this chunk boundary; instances 1 and 2 are complete.
- `DC_PERFMON*_PERFCOUNTER_CNTL2` fields define counted value type, hardware stop selectors, count-off selector, and a high-bit selector. `DC_PERFMON*_PERFCOUNTER_STATE` packs eight 2-bit counter states with per-counter select bits.
- `DC_PERFMON*_PERFMON_CNTL` and `CNTL2` fields define perfmon state, report count, count-off interrupt AND/OR, interrupt enable/status/ack, clock enable, and run-enable start/stop selection. `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW` provide counter interrupt status/ack and 48-bit-style readback windows split across low/high registers.
- `DOMAIN{0,1,2,3,16,17,18,19}_PG_CONFIG` and `DOMAIN*_PG_STATUS` fields expose `DOMAIN_POWER_FORCEON`, `DOMAIN_POWER_GATE`, `DOMAIN_DESIRED_PWR_STATE`, and `DOMAIN_PGFSM_PWR_STATUS`.
- `DCPG_INTERRUPT_STATUS`, `DCPG_INTERRUPT_STATUS_2`, `DCPG_INTERRUPT_CONTROL_1`, and `DCPG_INTERRUPT_CONTROL_3` fields cover power-up/down events and mask/clear controls for power domains 0-3 and 16-19.
- `CC_DC_PIPE_DIS` fields disable DC pipes and expose `DC_DMCUB_ENABLE`. `DMU_CLK_CNTL` controls and reports clock-gating state for DMU, DMCU, and RBBMIF display clocks. `DMU_MEM_PWR_CNTL` controls DMCU ERAM/IRAM memory power force/disable/state.
- `DMCU_CTRL`, `DMCU_STATUS`, firmware address/checksum, and RAM access registers define the legacy display microcontroller control surface: uC reset/enable/status bits, PC/start/end/ISR addresses, checksum words, ERAM/IRAM read/write auto-increment windows, and host-read/write access controls.
- `DMCU_EVENT_TRIGGER`, `DMCU_UC_INTERNAL_INT_STATUS`, and `DMCU_SS_INTERRUPT_CNTL_STATUS` define event and microcontroller interrupt state for ABM, static screen, external SW, DCPG, vblank, and internal exception/read-timeout conditions.
- `DMCU_INTERRUPT_STATUS`, `DMCU_INTERRUPT_STATUS_1`, `DMCU_INTERRUPT_STATUS_CONTINUE`, and `DMCU_INTERRUPT_STATUS_2` are latched interrupt-status/clear registers. They cover ABM1-3 histogram/luma/backlight update events, MCP/external/SCP/uC events, DCPG domain power transitions for domains 0-21 across base/continue/2 registers, vblank 1-6, OTG range timing update 0-5, and DCIO DPCS TXA-TXG events.
- `DMCU_INTERRUPT_TO_HOST_EN_MASK`, `DMCU_INTERRUPT_TO_UC_EN_MASK*`, and `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL*` route the same display events either to host interrupt handling or to the DMCU/uC path and select XIRQ versus IRQ delivery.
- `MASTER_COMM_*` and `SLAVE_COMM_*` registers define 32-bit communication payload words split into two 16-bit fields, command bytes plus byte-valid bits, and simple control bits for host/uC mailbox-style command exchange.
- `DMCU_PERFMON_INTERRUPT_STATUS*`, `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK*`, and `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL*` expose perfmon counter interrupts and routing for DMU, DIO, DCCG, HPO, HUBP0-7, HUBBUB, DPP0-7, WB0-2, MMHUBBUB, MPC, OPP, OPTC, HDA, and DSC0-5 blocks.
- `DMCU_DPRX_INTERRUPT_STATUS1`, `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1`, and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1` expose DisplayPort receiver-side events for two stream decoders (`SD0P0`, `SD1P0`) and DPHY/AUX conditions such as MSA received, VBID stream-status toggled, vertical interrupts, SDP received, BS/SR/symbol/disparity/training/test-pattern/ECF errors, SR lock detect, loss of align/deskew, excessive errors, deskew FIFO overflow, AUX/I2C/CPU interrupts, and AUX message timeouts.
- `DMCU_INT_CNT`, `DMCU_INT_CNT_CONTINUE`, `DMCU_INT_CNT_CONT2`, and `DMCU_INT_CNT_CONT3` provide 8-bit interrupt counters for ABM histogram/luma/backlight events across ABM instances.
- `DC_GPU_TIMER_START_POSITION_V_UPDATE`, `DC_GPU_TIMER_START_POSITION_VSTARTUP`, `DC_GPU_TIMER_READ`, and `DC_GPU_TIMER_READ_CNTL` define GPU timer start-position selection/readback fields for display pipes D1-D6 and VUpdate/VStartup/VSync nominal timing points.
- The trailing `DISP_INTERRUPT_STATUS` fields define top-level display interrupt bits for OPTC1 underflow, OTG1 snapshot/force-vsync/force-count/trigger/vsync-nom/DRR minimum-total events, DIGA DP fast-training and stream-disable events, HPD1/HPD1_RX, AUX1 SW/LS done, DIO ALPM, RBBMIF timeout, DC I2C SW done, DMCU internal/SCP, ABM1, and continuation chaining.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when AMDGPU Display Core code combines these constants with matching register offsets and helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, generated `DMUB_SR`/`DMUB_SF` tables, or similar display register-access wrappers.

A typical runtime path is:

1. Select the DCN 3.1.4 register address from the companion offset/header tables.
2. Use this chunk's `_SHIFT` and `_MASK` macros to pack a write value, extract a readback field, or build a read/modify/write mask.
3. Access the MMIO register through the AMD display register abstraction.
4. Let display hardware retain, consume, latch, clear, or report the represented state.

The state represented here is hardware state rather than driver-owned memory:

- Persistent configuration fields include perfmon event/routing controls, power-gate force/gate requests, DMU clock-gating override bits, DMCU memory power controls, DMCU firmware and RAM access setup, interrupt enable/routing masks, XIRQ/IRQ selection bits, host/uC mailbox command/data fields, and GPU timer read/start-position selectors.
- Volatile readback fields include perfmon active/state/counter readbacks, domain desired/power FSM state, DMU/DMCU/RBBMIF clock-on bits, ERAM/IRAM power state, DMCU running/sleeping/stalled status, internal exception bits, interrupt occurrence bits, DPRX/DPCS error/status bits, ABM interrupt counters, and GPU timer readback values.
- ACK, clear, reset, trigger, and command fields are side-effecting write paths. Examples include perfmon counter interrupt ACKs, DCPG interrupt clear bits, DMCU interrupt clear bits, DMCU event trigger bits, software reset/uc reset controls, ERAM/IRAM write/read access windows, mailbox command byte-valid bits, DPRX interrupt clears, and DMCU internal interrupt clears.
- Many interrupt status and clear fields intentionally share the same bit position/mask. A write used to clear an event is not equivalent to setting persistent configuration; call sites must avoid read/modify/write patterns that accidentally acknowledge pending status.
- The chunk includes both host-facing and uC-facing routing controls for the same event families. Misrouting an interrupt can remove host visibility, wake the wrong DMCU path, or select the wrong XIRQ/IRQ delivery mode even when the top-level `DISP_INTERRUPT_STATUS` source bit is correct.

Correct sequencing is imposed by hardware and functional driver code, not by these macros. Callers still need to respect display power state, DMCU/DMUB ownership, interrupt locking, firmware load/start ordering, RAM-access handshakes, power-gate transition polling, vblank/vupdate timing, and perfmon counter lifecycle rules.

## Dependencies And Integration Points

This chunk integrates with:

- The matching DCN 3.1.4 offset/address headers in the same `asic_reg/dcn` namespace. The mask/shift macros are meaningful only when paired with the correct register address for the same ASIC revision.
- AMDGPU Display Core register helper macros and generated register tables that consume `<register>__<field>__SHIFT` and `<register>__<field>_MASK` names for `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_GET_2`, and related accessors.
- DMUB/DMCU code paths that instantiate DCN 3.1.4 register tables. DCN 3.1.4 DMUB setup includes this generated mask header through register-list macros, so changed names or bit positions can break compile-time macro expansion or runtime firmware-register programming.
- Display interrupt handling and IRQ source mapping. The top-level `DISP_INTERRUPT_STATUS` fields correspond to interrupt source definitions under `include/ivsrcid/dcn`, while DMCU interrupt/routing registers decide whether events are exposed to the host, the uC, or both.
- Power-management code that drives DCPG domains, clock gating, memory power state, Z-state/SOC access, and deep sleep. The domain power-gate fields in this chunk are paired with status and interrupt bits used to confirm transitions.
- Firmware bring-up and diagnostics paths that reset/enable DMCU, configure firmware start/end/ISR addresses and checksums, access ERAM/IRAM windows, and poll DMCU status.
- Mailbox and command exchange paths using `MASTER_COMM_*` and `SLAVE_COMM_*` data/command/control registers for host-to-uC and uC-to-host signaling.
- ABM/static-screen/backlight paths using DMCU ABM histogram/luma/backlight update interrupts, interrupt counters, host/uC routing masks, and top-level `DISP_INTERRUPT_STATUS` ABM bits.
- Perfmon/debug tooling that programs DCCG/DMU perfmon instances, routes perfmon counter interrupts to DMCU/uC, reads low/high counter values, and clears counter interrupts.
- DisplayPort diagnostics and AUX/DPRX handling that observe and route the DPRX/DPCS interrupt fields for stream-status, DPHY errors, AUX/I2C/CPU events, and timeouts.
- Timing and IHC code that reads GPU timer values and tracks OTG/OPTC/HPD/AUX/I2C/DMCU events through `DISP_INTERRUPT_STATUS` and continuation status registers in later chunks.

Because this is generated preprocessor data, name mismatches usually fail at compile time only when a macro is referenced. Numeric drift in shifts or masks can compile cleanly and then misprogram live MMIO fields at runtime.

## Risks And Maintenance Notes

- Generated-header drift is the main risk. A stale or wrong `_SHIFT`/`_MASK` value can silently write the wrong hardware bit, especially for packed interrupt routing, counter state, mailbox command, and power-gate control registers.
- Chunk boundary risk exists at both ends. This slice starts in the middle of `DC_PERFMON0_PERFCOUNTER_CNTL` and ends in the middle of `DISP_INTERRUPT_STATUS`; final per-file reconciliation must merge neighboring chunks to avoid presenting those registers as incomplete.
- Status/clear aliasing is pervasive. Fields such as `*_OCCURRED` and `*_CLEAR`, or perfmon status and ACK bits, often share masks. Treating these as ordinary stored booleans can clear events before service or lose interrupt evidence.
- Host/uC interrupt routing has duplicated families across status, enable, and XIRQ/IRQ selector registers. Updating one register family without the corresponding enable/selector/status definition can leave events stuck, unhandled, or delivered to the wrong consumer.
- Power-gate and clock-gate fields are live hardware controls. Incorrect force/gate values or missing status polling can produce display hangs, failed DMCU access, broken ABM/static-screen handling, or timeouts during suspend/resume.
- DMCU RAM access fields are side-effecting indexed windows. Incorrect auto-increment, address, or write/read sequencing can corrupt firmware-visible memory or read the wrong diagnostic data.
- Perfmon counter readback is split across low/high/misc registers and selector fields. Callers must use the intended read-selection order to avoid mixing high/low halves or acknowledging counter interrupts unexpectedly.
- Interrupt source naming must remain aligned with `ivsrcid` tables and display IRQ code. For example, `DISP_INTERRUPT_STATUS` bits for HPD1, AUX1, DMCU, ABM, RBBMIF timeout, and OTG1 events are part of host-visible IRQ source mapping.

## Test Signals

Useful validation signals for changes touching this generated range include:

- Build coverage for DCN 3.1.4 display code that includes `dcn_3_1_4_sh_mask.h` and expands register/field macros in DMUB, interrupt, power, and perfmon tables.
- Compile-time failures for renamed or missing macros in generated register tables; these catch symbol drift but not wrong numeric masks.
- Suspend/resume and display power-management tests that exercise DCPG domain force/gate transitions, DMU/DMCU clock gating, ERAM/IRAM memory power state, and Z-state/SOC access controls.
- Firmware bring-up or DMUB/DMCU diagnostics that confirm DMCU reset/start/status behavior, firmware address/checksum programming, RAM window access, and host/uC mailbox command exchange.
- IRQ tests for HPD1/HPD1_RX, AUX1 SW/LS done, DC I2C SW done, OTG1 events, vblank/range-timing events, DMCU internal/SCP, ABM histogram/luma/backlight events, and RBBMIF timeout handling.
- Perfmon tests that configure `DC_PERFMON0/1/2`, start/stop counters, read low/high values, trigger counter-value interrupts, acknowledge them, and verify routing through `DMCU_PERFMON_INTERRUPT_*` fields.
- DP/DPRX diagnostic or error-injection tests that verify DPRX stream, DPHY, AUX/I2C/CPU, and timeout status/clear/routing bits.
- Register readback comparison against hardware documentation or known-good generated headers for DCN 3.1.4, especially for packed fields where bit offsets are non-contiguous or have continuation registers.
