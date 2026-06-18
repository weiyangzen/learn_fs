# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 1-2400

## Purpose

This chunk is generated AMD DCN 3.1.5 register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit positions and masks inside display-engine MMIO registers. The companion `dcn_3_1_5_offset.h` header supplies register addresses, while this file supplies the field layout consumed by register helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Although this file is located under a local `ceph-client` source mirror, it is AMDGPU display-driver hardware metadata and has no Ceph or distributed filesystem behavior.

The requested range covers the file prologue and the beginning of the DCN 3.1.5 field database: DCCG display clocking, pixel/stream clock DTOs, clock gating, soft resets, DCCG perfmon controls, DC perfmon instances 0 and 1, the DMCU register block, DMCUB RBBMIF security, RBBMIF timeout/status controls, and the start of DC perfmon instance 2. This slice has 2,164 `#define` lines: 1,084 `__SHIFT` definitions, 1,079 `_MASK` definitions, and 191 register-name groups. The count imbalance is expected because the chunk ends inside `DC_PERFMON2_PERFCOUNTER_STATE`, whose remaining shifts and masks continue after line 2400.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocations, locks, or direct persistence APIs in this line range. Its interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: field bit offset.
- `<REGISTER>__<FIELD>_MASK`: field bit mask.

Important register families in this chunk:

- DCCG display clock controls: `DENTIST_DISPCLK_CNTL`, `DISPCLK_FREQ_CHANGE_CNTL`, `DCCG_GATE_DISABLE_CNTL`, `DCCG_GATE_DISABLE_CNTL2`, `DCCG_GATE_DISABLE_CNTL3`, `DCCG_GATE_DISABLE_CNTL4`, clock-gating delay registers for DISPCLK, SOCCLK, DPREFCLK, REFCLK, DPPCLK, and SYMCLK, plus `DCCG_SOFT_RESET`.
- Pixel and stream clock routing: PHYPLL pixel-clock resync controls for PHYPLL A through E, `DPREFCLK_CNTL`, `DPSTREAMCLK_CNTL`, OTG0 through OTG3 pixel-rate controls, OTG PHYPLL source controls, DP DTO phase/modulo registers, DTBCLK DTO phase/modulo registers, HDMI character/stream clock controls, and DPP/DSC/HDMI/DTB clock DTO enable and parameter fields.
- DCCG measurement and synchronization: DCCG perfmon enable controls, CAC status readbacks, GTC DTO/current registers, deep-sleep DTO and calibration controls, millisecond/microsecond time-base dividers, SYMCLK32 source/enables, forced symclk disables, test clock selection, DCCG vsync counter control, per-OTG latch values, and latch interrupt status/clear fields.
- DC perfmon instances 0 and 1: event selection, counted value selection, increment mode, run/interrupt controls, per-counter state readback, repeat/count-off controls, counter interrupt status/ack, and high/low counter readback.
- DMCU control and firmware access: `DMCU_CTRL`, status, program-counter/firmware start/end/ISR addresses, firmware checksums, ERAM/IRAM read/write control and data, event trigger, internal interrupt status, static-screen interrupt status/clear, scratch, interrupt counters, clock-gating controls, and master/slave communication registers.
- DMCU interrupt routing: host enable masks; microcontroller enable masks; XIRQ/IRQ select masks; continuation masks for DCPG power-domain events, vblank, range timing updates, DCCG vsync counter events, ABM events, DPRX/AUX/I2C/CPU/message-timeout events, and perfmon counter interrupts from DMU, DIO, DCCG, HPO, HUBP, HUBBUB, DPP, WB, MMHUBBUB, MPC, OPP, OPTC, HDA, and DSC blocks.
- DMU security and RBBM interface: `DMCUB_RBBMIF_SEC_CNTL` security/trust/source fields, RBBMIF timeout delay/status/ack/mask fields, per-client timeout-disable masks for clients 0 through 38, and invalid-access/status flags.
- DC perfmon instance 2 begins at the end of the chunk with `DC_PERFMON2_PERFCOUNTER_CNTL`, `DC_PERFMON2_PERFCOUNTER_CNTL2`, and the first `DC_PERFMON2_PERFCOUNTER_STATE` shift definitions.

## Control Flow

This header has no runtime control flow. Runtime sequencing comes from AMDGPU display code that includes the generated DCN 3.1.5 offset and mask headers.

Typical flow:

1. DCN315 resource, IRQ, GPIO, and DMUB code include `dcn_3_1_5_offset.h` and `dcn_3_1_5_sh_mask.h`.
2. Those files define DCN base segments, then build block-specific register tables with generated register and field macros.
3. Consumers expand field-list macros into offset, mask, and shift tables. For example, `dmub_dcn315.c` expands `DMUB_DCN315_FIELDS()` with `FD_MASK` and `FD_SHIFT`.
4. Runtime code uses the generated constants when programming display clocks, DCCG DTOs, OTG pixel-rate routing, perfmon instances, DMCU firmware windows, DMCU interrupt routing, RBBMIF security/timeout policy, and diagnostic readback paths.

The masks do not encode ordering or side effects. Driver code must still follow hardware sequences around clock enabling, DTO programming, double-buffering, soft reset assertion/release, interrupt acknowledgement, indexed firmware/RAM access, timeout clearing, and suspend/resume restore.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk. It describes fields for MMIO-backed GPU display state. State represented by these definitions includes:

- Clock configuration: DISPCLK/DPPCLK divisors, ramp status, DPREFCLK source, REFCLK/DPREFCLK/SOCCLK/DPPCLK/DISPCLK/SYMCLK gate disables, clock-gating delays, soft-reset bits, and test clock muxes.
- Pixel, stream, and DTO state: OTG pixel-rate sources, DP/DTB DTO enables and dividers, DP/DTB/DPP/DSC/HDMI/audio DTO phase/modulo values, PHYPLL resync and deep-color DTO status, stream clock gating, and HDMI/PHY symbol-clock source selection.
- DCCG timing and diagnostics: deep-sleep clock calibration, GTC current count, millisecond/microsecond time bases, CAC status, vsync counter control, per-OTG latch values, latch interrupt status/clear bits, and perfmon enable paths.
- Perfmon state: event select, counted-value type, run/stop criteria, active state, repeat count, count-off interrupt state, per-counter interrupt status/ack, and counter high/low readbacks for instances 0 and 1 plus the start of instance 2.
- DMCU firmware and microcontroller state: control/status bits, PC/start/end/ISR addresses, firmware checksum fields, ERAM/IRAM access windows, event triggers, internal interrupt status, static-screen events, scratch registers, master/slave communication mailboxes, ABM interrupt counts, and DMCU read clock gating.
- Interrupt-routing state: host and microcontroller enable bits and XIRQ/IRQ selection for ABM, SCP/MCP, DCPG power domain, vblank, OTG range timing update, DCCG vsync counter, DPRX, AUX/I2C/CPU, and perfmon counter events.
- RBBMIF and security state: security/trust/source identity, timeout delay and hold policy, timeout status clients, timeout address/op/read-write/ack/mask fields, per-client timeout-disable bits, FIFO/status flags, and invalid-access reporting.

Persistence is hardware-defined. Some fields are configuration bits that remain until a modeset, reset, power transition, suspend/resume cycle, or ASIC reset. Other fields are read-only status, sticky error, write-one-to-clear, self-clearing request, or interrupt acknowledge bits. The generated header does not express those access classes; consumers and hardware documentation provide that context.

## Dependencies And Integration Points

This chunk must match the generated DCN 3.1.5 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h`

Direct include sites found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.c`

Key integration points:

- `dmub_dcn315.c` includes this header and expands `DMUB_DCN315_FIELDS()` through `FD_MASK` and `FD_SHIFT` while building `dmub_srv_dcn315_regs`. Most DMUB-specific fields are later in the file, but this same generated namespace must be coherent for the DCN315 DMUB service table.
- `dmub_srv.c` selects `dmub_srv_dcn315_regs` for `DMUB_ASIC_DCN315`, then uses common DCN31 DMUB operations for reset, mailbox, GPINT, diagnostic, and timer behavior.
- `dcn315_resource.c` includes this header while constructing the DCN315 resource pool. The DCCG fields in this chunk feed DCN31 DCCG/resource code paths for display clock, DPP clock, DP/DTB DTO, stream clock, and timing-generator integration.
- `irq_service_dcn315.c` includes this namespace for interrupt status, acknowledge, and enable definitions used by DCN315 IRQ source tables. The DMCU and perfmon interrupt masks in this chunk are especially relevant to interrupt routing and diagnostic events.
- GPIO factory/translate code includes the same generated header so DCN315 pin, AUX, HPD, and DDC register tables can share the ASIC-specific register namespace.
- DCN315 clock-manager and SMU code do not necessarily include this header directly, but their clock requests depend on DCCG/DPP/DTB/DISPCLK state programmed through these field definitions.

## Risks And Edge Cases

- Generated macro drift is the main risk. A wrong mask or shift compiles cleanly but can program the wrong bit, corrupt adjacent fields, or misread status.
- The chunk boundary splits `DC_PERFMON2_PERFCOUNTER_STATE`: this range includes the first shift definitions but not the complete mask set. File-level reconciliation must merge the next chunk before making complete claims about DC perfmon instance 2.
- DCCG and clock DTO fields are high impact. Incorrect clock source, divisor, gate-disable, soft-reset, DTO phase/modulo, or double-buffer-enable fields can cause blank displays, underflow, invalid link clocks, broken HDMI/DP timing, or resume failures.
- OTG pixel-rate controls mix enable, status, error, add/drop pixel, source select, and divider fields. Consumers must avoid treating status/error fields as ordinary writable configuration.
- Interrupt fields reuse bit positions for status/occurred/clear or status/ack semantics in several registers. Incorrect read-modify-write behavior can drop events, leave interrupts stuck, or clear unrelated conditions.
- DMCU ERAM/IRAM access fields are indexed access windows. Incorrect address, byte-enable, byte-mode, or auto-increment sequencing can read/write the wrong firmware memory location.
- DMCU interrupt routing is broad and sparse. Enabling the wrong ABM, DCPG, vblank, DPRX, AUX, or perfmon bit can route unexpected interrupts to the microcontroller or mask events needed by the host.
- RBBMIF timeout and security fields affect register access diagnostics and access control. Over-broad timeout disables or incorrect trust/source fields can hide bus faults or interfere with protected DMCUB/RBBMIF access.
- Perfmon fields are diagnostic but side-effectful. Wrong event selects, run-enable controls, interrupt enables, or ack masks can make performance data misleading or leave counter interrupts asserted.

## Test Signals

Useful validation combines build checks, generated-header consistency checks, and hardware behavior:

- Build AMDGPU/DC with DCN315 enabled. Missing or renamed macros should fail in `dmub_dcn315.c`, `irq_service_dcn315.c`, `dcn315_resource.c`, and DCN315 GPIO translation/factory code.
- Mechanically verify that complete fields in lines 1-2400 have paired `__SHIFT` and `_MASK` definitions, while allowing the known boundary exception for the incomplete `DC_PERFMON2_PERFCOUNTER_STATE` group.
- Compare values against AMD's authoritative DCN 3.1.5 register database and adjacent generated DCN 3.1.x headers where fields are expected to remain compatible.
- Exercise DCN315 modesets across HDMI/DP/eDP paths while changing display clocks, DPP clocks, DTBCLK, DP DTO, PHYPLL pixel sources, and OTG pixel-rate sources. Watch for blanking, underflow, FIFO errors, link-training regressions, and incorrect pixel rate.
- Exercise suspend/resume and clock/power gating transitions, including DCCG soft reset, gate-disable fields, DPP/DSC/DP/HDMI DTO double-buffering, DPREFCLK/REFCLK source changes, and deep-sleep clock calibration.
- Exercise IRQ behavior for vblank, OTG range timing updates, static-screen/ABM events, DPRX/AUX/I2C/CPU events, DCCG vsync counter latches, and perfmon interrupts. Watch for missing, duplicated, or stuck events.
- Exercise DMCU firmware access paths: control/status, firmware address/checksum fields, ERAM/IRAM read/write windows, master/slave communication registers, event trigger, scratch register, and internal interrupt status.
- Exercise RBBMIF timeout diagnostics by validating timeout status, timeout address/op/read-write reporting, ack/mask behavior, invalid-access flags, FIFO empty/full flags, and per-client timeout-disable behavior.
- Exercise perfmon instances 0 and 1 by selecting events, enabling counters, reading high/low values, causing/clearing counter interrupts, and verifying stable counter state transitions.

## Cross-Chunk Notes

This is the first chunk of `dcn_3_1_5_sh_mask.h` and includes the file guard and initial DCCG/DMCU field families. The next chunk owns the remainder of `DC_PERFMON2_PERFCOUNTER_STATE` and later register families. The final per-file research document should merge adjacent chunks before drawing complete-file conclusions about DC perfmon instance 2 or the full DCN315 generated field database.
