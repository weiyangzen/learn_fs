# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001865`: lines 1-2400, `Docs/researches/chunks/subset-b-001865_research.md`
- `subset-b-001866`: lines 2401-4862, `Docs/researches/chunks/subset-b-001866_research.md`
- `subset-b-001867`: lines 4863-7527, `Docs/researches/chunks/subset-b-001867_research.md`
- `subset-b-001868`: lines 7528-10046, `Docs/researches/chunks/subset-b-001868_research.md`
- `subset-b-001869`: lines 10047-12576, `Docs/researches/chunks/subset-b-001869_research.md`
- `subset-b-001870`: lines 12577-15089, `Docs/researches/chunks/subset-b-001870_research.md`
- `subset-b-001871`: lines 15090-17598, `Docs/researches/chunks/subset-b-001871_research.md`
- `subset-b-001872`: lines 17599-20110, `Docs/researches/chunks/subset-b-001872_research.md`
- `subset-b-001873`: lines 20111-22625, `Docs/researches/chunks/subset-b-001873_research.md`
- `subset-b-001874`: lines 22626-25141, `Docs/researches/chunks/subset-b-001874_research.md`
- `subset-b-001875`: lines 25142-27729, `Docs/researches/chunks/subset-b-001875_research.md`
- `subset-b-001876`: lines 27730-30207, `Docs/researches/chunks/subset-b-001876_research.md`
- `subset-b-001877`: lines 30208-32632, `Docs/researches/chunks/subset-b-001877_research.md`
- `subset-b-001878`: lines 32633-35011, `Docs/researches/chunks/subset-b-001878_research.md`
- `subset-b-001879`: lines 35012-37422, `Docs/researches/chunks/subset-b-001879_research.md`
- `subset-b-001880`: lines 37423-39826, `Docs/researches/chunks/subset-b-001880_research.md`
- `subset-b-001881`: lines 39827-42175, `Docs/researches/chunks/subset-b-001881_research.md`
- `subset-b-001882`: lines 42176-44691, `Docs/researches/chunks/subset-b-001882_research.md`
- `subset-b-001883`: lines 44692-47145, `Docs/researches/chunks/subset-b-001883_research.md`
- `subset-b-001884`: lines 47146-49525, `Docs/researches/chunks/subset-b-001884_research.md`
- `subset-b-001885`: lines 49526-52127, `Docs/researches/chunks/subset-b-001885_research.md`
- `subset-b-001886`: lines 52128-55341, `Docs/researches/chunks/subset-b-001886_research.md`
- `subset-b-001887`: lines 55342-57717, `Docs/researches/chunks/subset-b-001887_research.md`
- `subset-b-001888`: lines 57718-60079, `Docs/researches/chunks/subset-b-001888_research.md`
- `subset-b-001889`: lines 60080-62071, `Docs/researches/chunks/subset-b-001889_research.md`

## Chunk Research

### subset-b-001865: lines 1-2400

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

### subset-b-001866: lines 2401-4862

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 2401-4862

## Purpose

This chunk is generated AMD DCN 3.1.5 register field metadata. It contains no executable C logic; it publishes preprocessor constants that describe bit positions and bit masks for display-controller MMIO registers. Consumers pair these `__SHIFT` and `_MASK` macros with the matching register offsets from `dcn_3_1_5_offset.h` so generic register helpers can read, write, update, poll, and acknowledge individual hardware fields.

The requested range starts inside the `DC_PERFMON2` field family, covers DMU/IHC interrupt routing, DMU and DMCUB control/status/mailbox fields, DWB writeback and color-processing fields, then ends at the beginning of the `DC_PERFMON3` field family. The range has 2,153 `#define` macros: 1,074 shift definitions and 1,079 mask definitions. The mismatch is from artificial chunk boundaries and a few register comments whose companion fields fall in adjacent chunks.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this range. The chunk's interface is its generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position of a field within a 32-bit MMIO register.
- `<REGISTER>__<FIELD>_MASK`: the field mask before shifting or after alignment, depending on the register-helper macro being used.
- Register-family comment markers such as `//DMCUB_CNTL` and address-block markers such as `// addressBlock: dce_dc_dmu_dmcub_dispdec`; these are generated documentation aids, not C constructs.

Major macro families in this slice:

- `DC_PERFMON2_*` tail: performance counter state, perfmon control, count-off interrupt control, current-value status/ack fields, and high/low counter value selection.
- `DC_GPU_TIMER_*`: display pipe start-position fields for vupdate, vstartup, vready, flip, flip-away, no-lock vupdate, readback selection, and nominal vsync positions.
- `*_INTERRUPT_DEST` fields under `dce_dc_dmu_ihc_dispdec`: interrupt destination selectors for DCCG, DMU, DCPG, MMHUBBUB, WB, DCHUB, DCHUB perf counters, DPP perf counters, MPC, OPP, OPTC, OTG0-OTG5, DIG, I2C/DDC/HPD, DIO, DCIO, HPD, AZ audio, AUX, DSC, and HPO.
- `CC_DC_PIPE_DIS`, `DMU_CLK_CNTL`, `DMU_MEM_PWR_CNTL`, `DMCU_SMU_INTERRUPT_CNTL`, `ZSC_*`, and `DMU_MISC_ALLOW_DS_FORCE`: DMU clock, memory power, SMU interrupt, zero-shutter/sleep-control, and display-pipe/DMCUB enable fields.
- `DOMAIN*_PG_CONFIG` and `DOMAIN*_PG_STATUS`: power-gating control and status fields for selected display power domains, plus `DC_IP_REQUEST_CNTL`.
- `DMCUB_*`: DMCUB memory-region base/top/offset/high fields, code-window enable fields, interrupt enable/ack/type/context fields, fault addresses, security/memory controls, inbox/outbox ring pointers and sizes, timers, scratch registers, core control, GPINT data paths, low-speed wake interrupt enable, processor ID, and soft reset.
- `DWB_*` top fields: writeback clock/memory power, frame-capture mode and flow control, capture window/source sizing, update control, CRC control/masks/values, output format/alpha/depth control, backpressure counters, host read control, overflow status/counters, soft reset, and debug selection.
- `DWB_HDR_*`, `DWB_GAMUT_REMAP*`, and `DWB_OGAM_*`: HDR multiplier, gamut remap matrix format and coefficients, output gamma mode/LUT access/control, RAM A and RAM B start/end/offset parameters for B/G/R channels, and piecewise-linear region descriptors for regions 0 through 33.
- `DC_PERFMON3_*` beginning: WB-local perf counter control, counted-value type, counter state, perfmon control, and the first `PERFMON_CNTL2` fields.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMD display code:

1. DCN 3.1.5 resource, IRQ, and DMUB code includes `dcn_3_1_5_offset.h` and this `dcn_3_1_5_sh_mask.h` file.
2. Register-list macros paste symbolic register names into offset names and field names. For example, DCN resource code uses `SR(...)`, `SRI(...)`, and related macros, while DMUB code uses `DMUB_SR(...)` and `DMUB_SF(...)`.
3. Offset helpers build absolute register addresses from the offset header and DCN base segments. Field helpers such as `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` expand to the macros in this header.
4. Driver code later applies `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and wait/poll helpers to manipulate individual fields in the correct hardware order.

The field macros do not encode sequencing requirements. Consumers still need to handle clock and memory power enablement, power-domain transitions, DMCUB reset and boot order, DMCUB ring-buffer initialization, interrupt masking and acknowledgement, writeback programming, color LUT programming, and perf-counter start/stop sequencing.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed hardware state:

- Perfmon state covers selected counter state, event/countoff behavior, interrupt status/ack bits, and 48-bit or split high/low counter-value readback.
- GPU timer and IHC interrupt-destination fields control where display timing and block interrupts are routed, including per-pipe vblank/vupdate/flip sources and block-specific interrupts.
- DMU, power-gating, and clock fields represent display block enablement, memory power state, deep-sleep controls, DMCUB availability, and selected power-domain requests/status.
- DMCUB fields represent persistent firmware-facing setup while the display microcontroller is running: memory windows, code-window top addresses and enables, inbox/outbox base/size/rptr/wptr rings, scratch state, GPINT payloads, timer values, fault addresses, interrupt routing, reset status, and security controls.
- DWB fields represent writeback configuration and live capture state: frame-capture geometry, output packing, CRC capture, overflow/backpressure status, host read state, memory power, and soft reset.
- DWB color fields represent programmable writeback color transforms: HDR scale, gamut-remap matrices, output gamma LUT host access, active RAM selection, LUT format/mode, PWL start/end/offset values, and per-region LUT offsets/segment counts.

Persistence is hardware-defined. Configuration fields generally retain values until a modeset, writeback reconfiguration, power gate, firmware reset, suspend/resume, or ASIC reset changes them. Status, counter, interrupt, fault, ack, wake, and reset fields may be read-only, sticky, self-clearing, or write-one-to-clear; this generated header only provides bit layout, not access semantics.

## Dependencies And Integration Points

This chunk must match AMD's generated DCN 3.1.5 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`
- The DCN base segment constants defined in the consuming C files, such as `DCN_BASE__INST0_SEG0` through `DCN_BASE__INST0_SEG5`.

Direct integration points found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`, which includes this header and builds `dmub_srv_dcn315_regs`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.h`, whose `DMUB_DCN315_FIELDS()` macro consumes fields from this range such as `DMCUB_CNTL.DMCUB_ENABLE`, `DMCUB_CNTL2.DMCUB_SOFT_RESET`, `DMCUB_SEC_CNTL.*`, `DMCUB_REGION3_CW*_TOP_ADDRESS.*`, `CC_DC_PIPE_DIS.DC_DMCUB_ENABLE`, and DMCUB interrupt fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`, which includes this header for interrupt-source setup, acknowledgement, and DAL IRQ mapping for vblank, vline, page-flip, vupdate, DMCUB outbox, HPD, and HPD RX sources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which includes this header while constructing DCN 3.1.5 hardware register tables for hubs, pipes, timing generators, stream encoders, DWB, MMHUBBUB, DMUB-backed features, and other display resources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_srv.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.c`, which select the `DMUB_ASIC_DCN315` register set.

The DWB field families integrate with the DCN 3.0/3.1 DWB and MMHUBBUB code included by `dcn315_resource.c` (`dcn30_dwb.h`, `dcn30_mmhubbub.h`). The generated field names are also tied to enum definitions in AMD SOC enum headers for values such as DWB OGAM LUT mode, host RAM selection, read color selection, and OGAM enable/bypass modes.

## Risks And Edge Cases

- Field drift is the central risk. A wrong shift or mask can compile cleanly but update the wrong bits in a live display register.
- The chunk boundaries are artificial. It begins after some `DC_PERFMON2_PERFCOUNTER_CNTL2` masks and ends immediately after `DC_PERFMON3_PERFMON_CNTL2`, so adjacent chunks are required for complete `DC_PERFMON2` and `DC_PERFMON3` coverage.
- Interrupt-destination fields are sensitive because a one-bit mistake can route vblank, vline, page-flip, HPD, AUX, DSC, DMCUB, or block error interrupts to the wrong destination, leave them masked, or make acknowledgement ineffective.
- DMU and power-gating fields are sequencing-sensitive. Writes made while clocks are off, memory is gated, or the DMCUB is held in reset can be ignored or can leave firmware-visible state inconsistent.
- DMCUB ring and memory-window fields are high risk. Incorrect base/top/offset, high-address, code-window enable, inbox/outbox pointer, interrupt, or scratch fields can break DMUB firmware boot, command submission, outbox notifications, PSR/ABM/replay features, or debug collection.
- DWB writeback fields affect captured pixels rather than scanout. Bugs may only appear in screen recording, capture, virtual display, CRC validation, or pipe-specific writeback workloads.
- DWB color programming is format-sensitive. Bad OGAM/gamut/HDR fields can produce subtle color errors, incorrect LUT bank selection, broken host LUT access, or only fail for particular color depths and matrix/LUT modes.
- Many status and ack fields have side effects not visible in this file. Treating read-only, sticky, self-clearing, or write-one-to-clear bits as ordinary writable fields can cause lost interrupts, stale faults, or stuck status.

## Test Signals

Useful validation is a mix of generated-header consistency, build coverage, and hardware behavior:

- Build AMDGPU display support with DCN 3.1.5 enabled; missing or renamed macros should fail in DMUB, IRQ, resource, DWB, and register-table construction.
- Mechanically verify that every complete field in lines 2401-4862 has both a `__SHIFT` and `_MASK` definition, allowing for the known first and last partial register families.
- Diff this chunk against AMD's authoritative DCN 3.1.5 register database and against nearby generated DCN 3.1.x headers where field compatibility is expected.
- Boot a DCN 3.1.5 system and verify DMCUB firmware initialization, reset release, command submission, inbox/outbox pointer movement, GPINT handling, scratch/debug capture, and DMUB outbox interrupts.
- Exercise IRQ-heavy display paths: vblank, vline, page flips, vupdate no-lock, HPD plug/unplug, HPD RX, AUX/DDC activity, DSC-capable links, and suspend/resume.
- Exercise DWB paths if hardware and driver features expose them: capture enable/disable, window/source-size changes, output format/depth changes, CRC readback, overflow/backpressure counters, host read behavior, and DWB soft reset.
- Validate writeback color processing with known ramps and matrices: HDR multiplier, gamut remap coefficients, OGAM LUT host programming, RAM A/B bank selection, per-channel PWL start/end/offset fields, and region 0-33 descriptors.
- Watch kernel logs and display diagnostics for DMCUB boot failures, stuck interrupts, HPD storms, lost vblank/page-flip events, AUX timeouts, writeback overflows, CRC mismatches, color corruption, and resume failures.

## Cross-Chunk Notes

Adjacent chunks should be merged before making complete file-level claims about `DC_PERFMON2`, `DC_PERFMON3`, or any full DCN 3.1.5 perfmon namespace. This chunk owns the middle DMU/IHC/DMCUB/DWB field-layout coverage for `dcn_3_1_5_sh_mask.h`, while the final per-file document should reconcile it with earlier and later field families in the same generated header.

### subset-b-001867: lines 4863-7527

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 4863-7527

## Purpose

This chunk is generated AMD DCN 3.1.5 register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit positions and masks inside display-engine MMIO registers. The companion `dcn_3_1_5_offset.h` header supplies register offsets, while this file supplies the field layouts consumed by AMDGPU display register helpers such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Although the tree path is under a local `ceph-client` source mirror, this range is AMDGPU display-driver hardware metadata and has no Ceph or distributed filesystem behavior.

The requested range covers the tail of `DC_PERFMON3`, legacy VGA and VGAIF/MMHUBBUB-facing registers, MCIF writeback buffer-manager fields, `DC_PERFMON4`, MMHUBBUB control/power/warmup fields, HDA/Azalia controller/root/stream/endpoint fields, `DC_PERFMON5`, DCHUBBUB arbitration/watermark/VM/SDPIF/return-path/diagnostic fields, and the beginning of DCN VM context page-table fields. This slice has 2,665 source lines, including 2,079 `#define` lines: 1,040 `__SHIFT` definitions and 1,039 `_MASK` definitions across 45 generated address-block sections. The count imbalance and incomplete register groups are chunk-boundary artifacts.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, callbacks, or direct persistence APIs in this line range. Its public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: field bit offset.
- `<REGISTER>__<FIELD>_MASK`: field mask for the same field.

Important register families in this chunk:

- `DC_PERFMON3`, `DC_PERFMON4`, and `DC_PERFMON5`: performance-counter control, event select, increment/run controls, per-counter state, repeat count, count-off interrupt controls, high/low counter readback, and interrupt status/ack fields.
- Legacy VGA and VGAIF fields: page-selection addresses, render control, sequencer reset behavior, VGA mode/surface/base address fields, HDP/cache controls, per-pipe `D1VGA_CONTROL` through `D6VGA_CONTROL`, VGA status/clear, indexed CRTC/SEQ/GRPH/DAC/attribute ports, source selection, QoS, and VGA split controls.
- MCIF writeback instance 0: buffer-manager software control/status, buffer pitch, four Y/C buffer address pairs with high address halves, buffer status/status2 groups, per-buffer resolution, arbitration, clock/p-state/self-refresh controls, watermark/QoS fields, VCE handoff controls, VMID selection, and minimum time-to-output.
- MMHUBBUB fields: writeback p-state latency and watermark controls, warmup base/region/status, WBIF/SMU watermark-change handshake, WBIF0 misc/outstanding counters, memory power status/control, clock gating, soft reset, DMU interface error status, client unit ID, and warmup VMID control.
- HDA/Azalia fields: controller clock gating, DTO/SOCCLK, DMA/BDL/RIRB/CORB/cyclic-buffer controls, stream arbitration, CRC setup/results, memory power control/status, root codec vendor/revision/capability/power/reset/subsystem/synchronization fields, port connectivity fields, GTC group offsets, 16 stream index/data windows, 8 output endpoint index/data windows, and 8 input endpoint index/data windows.
- DCHUBBUB hub fields: outstanding request limits, saturation and QoS forcing, DRAM-state controls, A/B/C/D watermark sets for urgency, memory trip time, self-refresh entry/exit including Z8, DRAM clock change, fractional urgent bandwidth, host-VM controls, watermark-change request/status, timeout enable, global timer, surface-check addresses, VTG controls, soft reset, clock controls, DCFCLK gating delay, performance measurement, vline snapshot, overflow/underflow status, timeout detection, FMON controls, and test debug windows.
- DCHUBBUB SDPIF and VM aperture fields: SDPIF credit/status/error/limit/snoop controls, physical VM request selection, forced IO status and address reporting, framebuffer base/top/offset, AGP aperture, local HBM address range and lock control, pipe security levels, metadata security levels, and SDPIF memory power state.
- DCHUBBUB return path and compression state: DCC configuration for pipes 0 through 7, return-path memory power, CRC controls and result values, DCC statistic controls/counters, compression-buffer control, DET controls, memory power mode/status, compression-buffer memory power controls, and reserved compression-buffer space.
- DCN VM context fields: complete control/base/start/end page-table fields for contexts 0 through 7, plus the start of context 8 through `DCN_VM_CONTEXT8_PAGE_TABLE_BASE_ADDR_LO32`.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code that includes the generated DCN 3.1.5 offset and mask headers.

Typical flow:

1. DCN315 DMUB, IRQ, and resource code include `dcn/dcn_3_1_5_offset.h` and `dcn/dcn_3_1_5_sh_mask.h`.
2. Resource code builds ASIC-specific register tables by expanding `SR`, `SRI`, `SRII`, and field-list helper macros over these names.
3. `dmub_dcn315.c` builds `dmub_srv_dcn315_regs` by expanding DCN315 field lists through `FD_MASK` and `FD_SHIFT`; fields from this chunk include `MMHUBBUB_SOFT_RESET`, `DCN_VM_FB_LOCATION_BASE`, and `DCN_VM_FB_OFFSET`.
4. Runtime paths use the generated offsets, shifts, and masks to program display hub power, VM apertures, writeback, audio, VGA disable/control paths, watermarks, performance counters, CRC/statistics, and timeout/diagnostic blocks.

The masks do not encode access ordering or side effects. Consumers still have to follow hardware sequences around reset assertion/release, clock and memory power transitions, indexed register windows, DMA/ring enablement, write-one-to-clear status, self-clearing request bits, watermark commits, VM aperture setup, and suspend/resume restore.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk. It describes MMIO-backed GPU state:

- Perfmon state includes selected events, counter run/increment controls, current counter values, high/low readback selection, interrupt status, and acknowledgement bits.
- VGA state includes legacy aperture/page mapping, render and sequencer behavior, per-pipe VGA enable/timing/polarity/rotation, indexed legacy register windows, status/clear bits, cache/HDP controls, and source selection.
- Writeback and MMHUBBUB state includes buffer ownership/status, Y/C addresses, resolutions, VMID, arbitration, p-state/watermark controls, self-refresh, outstanding request counters, warmup configuration, memory power state, clock gating, and soft reset.
- HDA/Azalia state includes controller DMA/ring/cyclic-buffer controls, stream and endpoint indexed-register access, DTO/SOCCLK generation, codec root parameters, audio power/reset state, CRC diagnostics, connectivity registers, GTC offsets, and memory power state.
- DCHUBBUB state includes memory-service arbitration, watermark sets A through D, host-VM policy, VM apertures and local HBM ranges, SDPIF credits/security/power state, CRC/DCC statistics, DET/compression-buffer allocation, timeout detection, vline snapshots, global timers, and debug windows.
- DCN VM context state includes page-table depth, block size, page-directory base, and logical page start/end ranges for contexts 0 through 7, with context 8 continuing in the next chunk.

Persistence is hardware-defined. Some fields remain configured until modeset, reset, power gating, suspend/resume, or ASIC reset. Others are read-only status, sticky error, interrupt status, write-one-to-clear acknowledgements, self-clearing requests, or indexed-window data fields. This generated header does not distinguish those access classes.

## Dependencies And Integration Points

This chunk must match the generated DCN 3.1.5 register database and companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h`

Direct include sites found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`

Key integration points:

- `dmub_dcn315.c` expands `DMUB_DCN315_FIELDS()` into mask and shift tables. This chunk backs DMUB-facing fields for MMHUBBUB soft reset and DCN VM framebuffer base/offset programming.
- `dcn315_resource.c` uses this namespace to build HW sequencer, DWB/MCIF writeback, audio, hub, and power-management register tables. The local `HWSEQ_DCN31_REG_LIST()` and `HWSEQ_DCN31_MASK_SH_LIST()` reference fields from this chunk including `DCHUBBUB_GLOBAL_TIMER_CNTL`, `DCHUBBUB_ARB_HOSTVM_CNTL`, `MMHUBBUB_MEM_PWR_CNTL`, `DCHUBBUB_CRC_CTRL`, `D1VGA_CONTROL` through `D6VGA_CONTROL`, `AZALIA_AUDIO_DTO`, and `AZALIA_CONTROLLER_CLOCK_GATING`.
- `dcn315_resource.c` also builds `dcn30_mmhubbub`/MCIF writeback tables with `MCIF_WB_COMMON_REG_LIST_DCN30()` and `MCIF_WB_COMMON_MASK_SH_LIST_DCN30()`, which rely on the MCIF writeback field names in this chunk.
- `irq_service_dcn315.c` includes the header for DCN315 interrupt-source status and acknowledge metadata; nearby perfmon, DCHUBBUB timeout, audio, and hub status fields are part of the same generated field namespace.
- Older AMDGPU paths outside DCN315 show direct use of compatible VGA masks such as `VGA_RENDER_CONTROL__VGA_VSTATUS_CNTL_MASK`, confirming that these generated constants are consumed by generic register-field helpers and direct read/modify/write paths.

## Risks And Edge Cases

- Generated macro drift is the primary risk. A wrong shift or mask compiles cleanly but can program the wrong bit, corrupt adjacent fields, or misread status.
- This chunk starts inside the `DC_PERFMON3` register family. The preceding chunk owns earlier `DC_PERFMON3_PERFMON_CNTL` definitions; file-level reconciliation should merge the adjacent chunk before making full claims about perfmon instance 3.
- This chunk ends inside the DCN VM context 8 field group after the context 8 page-table base low word. The next chunk owns the remaining context 8 start/end fields and later contexts.
- VGA fields are legacy but still high impact during boot, handoff, and disable sequences. Incorrect VGA render, sequencer reset, cache/HDP, page, or per-pipe control fields can leave legacy decode active, blank display unexpectedly, or interfere with display ownership.
- MCIF writeback and MMHUBBUB fields influence memory traffic and power state. Bad buffer address, high-address, pitch, VMID, arbitration, watermark, self-refresh, clock-gating, or memory power masks can cause writeback corruption, underflow, failed p-state changes, or resume problems.
- HDA/Azalia indexed stream and endpoint windows are sequencing-sensitive. Incorrect index/data/write-enable fields can target the wrong stream or codec node and break HDMI/DP audio setup, DMA ring operation, or codec power reporting.
- DCHUBBUB watermark and arbitration fields govern display memory-service latency. Incorrect A/B/C/D watermarks, urgent bandwidth, host-VM policy, timeout, or surface-check fields can produce underflow, false timeout interrupts, excessive power use, or stalls that are hard to attribute.
- VM aperture and context fields must agree with GPU memory-manager state. Bad framebuffer/AGP/HBM apertures or page-table base/start/end fields can translate display requests to the wrong memory.
- Soft reset and memory power fields are live-hardware controls. Applying these masks outside the expected quiesce/reset/power sequence can drop active writeback, hub, audio, or VGA state.
- Perfmon fields are diagnostic but side-effectful. Wrong run-enable, event, state, or ack masks can produce misleading measurements or stuck performance-counter interrupts.

## Test Signals

Useful validation combines build checks, generated-header consistency checks, and hardware behavior:

- Build AMDGPU/DC with DCN315 enabled. Missing or renamed macros should fail in `dmub_dcn315.c`, `irq_service_dcn315.c`, or `dcn315_resource.c`.
- Mechanically verify paired `__SHIFT` and `_MASK` definitions for complete fields in this range, while allowing the known boundary split at `DC_PERFMON3` and the partial `DCN_VM_CONTEXT8` group.
- Compare field values against AMD's authoritative DCN 3.1.5 register database and adjacent generated DCN 3.1.x/DCN 3.2.x headers where fields are expected to remain compatible.
- Exercise DMUB/DCN315 boot and service setup: MMHUBBUB soft reset release, framebuffer base/top/offset programming, inbox/outbox traffic from neighboring chunks, GPINT acknowledgement, and suspend/resume restore.
- Exercise VGA handoff/disable paths, including `VGA_RENDER_CONTROL`, sequencer reset, `D1VGA_CONTROL` through `D6VGA_CONTROL`, VGA status clear, and legacy indexed register access.
- Exercise MCIF writeback with luma/chroma buffers, high address halves, pitch/resolution programming, VMID selection, buffer-status transitions, p-state changes, self-refresh, outstanding-counter readback, and memory power transitions.
- Exercise HDMI/DP audio: controller DTO/SOCCLK, stream index/data programming, RIRB/CORB/BDL/cyclic-buffer DMA, endpoint index/data windows, codec power/reset, connectivity registers, and CRC diagnostics.
- Exercise DCHUBBUB watermarks and VM paths under bandwidth stress, p-state changes, host-VM traffic, AGP/FB/HBM aperture changes, timeout detection, surface-check diagnostics, CRC/DCC statistic collection, and suspend/resume.
- Exercise perfmon instances 3 through 5 by selecting events, enabling counters, reading high/low values, causing and clearing counter interrupts, and verifying state transitions.

## Cross-Chunk Notes

The previous chunk owns the earlier `DC_PERFMON3_PERFMON_CNTL` fields immediately before this range. The next chunk owns the remainder of `DCN_VM_CONTEXT8` and later VM context fields. The final per-file research document should reconcile adjacent chunks before drawing complete conclusions about `DC_PERFMON3` or the full DCN VM context table.

### subset-b-001868: lines 7528-10046

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 7528-10046

## Purpose

This chunk is generated AMD DCN 3.1.5 register field metadata. It contains no executable C logic; it publishes preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for display-controller MMIO registers. Driver code includes this header with the matching `dcn_3_1_5_offset.h` so register-table builders can compute addresses from the offset header and manipulate individual fields from this mask header.

The requested range starts in the middle of the `DCN_VM_CONTEXT8_CNTL` group, then covers VM context page-table fields for contexts 8 through 15, DCN VM default/fault registers, `DC_PERFMON6`, HUBP/HUBPREQ/HUBPRET/cursor blocks for HUBP instances 0 and 1, `DC_PERFMON7` and `DC_PERFMON8`, all visible HUBP2 fields, and the beginning of `HUBPREQ2`. It defines 2,099 macros and 394 register/address-block comments in this slice.

Although the path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or direct register reads/writes in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate or update that field.
- Address-block comments such as `// addressBlock: dce_dc_dcbubp0_dispdec_hubpreq_dispdec`: generated grouping metadata that identifies the hardware block owning the following registers.

Major register families in this range:

- `DCN_VM_CONTEXT8` through `DCN_VM_CONTEXT15`: page table depth/block-size fields plus page directory base, start logical page, and end logical page high/low fields. Context 8 begins mid-group because line 7528 is already inside the context-8 control mask definitions.
- `DCN_VM_DEFAULT_ADDR_MSB/LSB`, `DCN_VM_FAULT_CNTL`, `DCN_VM_FAULT_STATUS`, and `DCN_VM_FAULT_ADDR_MSB/LSB`: default address, VM fault control, sticky/status, faulting VMID/table-level/pipe, interrupt status, and fault address fields.
- `DC_PERFMON6`, `DC_PERFMON7`, and `DC_PERFMON8`: display perfmon counter control, counter selection, clear/freeze/enable controls, state, accumulator values, high/low counter values, interrupt/mask controls, and overflow/interrupt status fields.
- `HUBP0`, `HUBP1`, and visible `HUBP2`: surface format/address/tiling/viewport fields, request sizing, blanking/soft reset/underflow/timeout controls, HUBP clock gating/status controls, virtual memory page size, debug windows, and DCFCLK/DPPCLK performance measurement windows.
- `HUBPREQ0` and `HUBPREQ1`: surface pitch and VMID fields, primary/secondary luma and chroma surface addresses, metadata addresses, DCC/TMZ surface-control fields, flip controls and interrupts, in-use and earliest-in-use address latches, TTU/QoS controls, VM aperture and L1 TLB controls, blanking/destination/prefetch/vblank/flip/nominal timing parameters, cursor request settings, memory power control/status, and later vblank/flip parameter extensions.
- `HUBPRET0` and `HUBPRET1`: HUBPRET control, memory power, read-line control/value/status, and interrupt status/ack/mask fields.
- `CURSOR0_0` and `CURSOR0_1`: cursor control, surface address, size, position, hot spot, stereo control, destination offset, memory power, and DMDATA address/control/QoS/status/software data fields.
- Beginning of `HUBPREQ2`: surface pitch, VMID, primary/secondary surface address, and primary/secondary metadata address fields through `HUBPREQ2_DCSURF_SECONDARY_META_SURFACE_ADDRESS_HIGH`.

Representative field groups include:

- VM context masks using full 32-bit low address fields and 4-bit high logical-page fields.
- Fault controls such as `DCN_VM_ERROR_STATUS_CLEAR`, `DCN_VM_ERROR_STATUS_MODE`, `DCN_VM_ERROR_INTERRUPT_ENABLE`, `DCN_VM_RANGE_FAULT_DISABLE`, and `DCN_VM_PRQ_FAULT_DISABLE`.
- HUBP control/status fields such as `HUBP_BLANK_EN`, `HUBP_NO_OUTSTANDING_REQ`, `HUBP_SOFT_RESET`, `HUBP_VTG_SEL`, `HUBP_DISABLE_STOP_DATA_DURING_VM`, `HUBP_UNBOUNDED_REQ_MODE`, `HUBP_SEG_ALLOC_ERR_STATUS`, `HUBP_TIMEOUT_STATUS`, and `HUBP_UNDERFLOW_STATUS`.
- Surface/request fields such as `PITCH`, `META_PITCH`, primary/secondary address low/high halves, DCC enable/block size fields, TMZ protection fields, `SURFACE_FLIP_PENDING`, and flip interrupt status/enable/clear bits.
- TTU and prefetch fields that encode delivery time, QoS watermark, vblank timing, flip timing, and per-line delivery parameters used by display memory scheduling.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code:

1. DCN 3.1.5 resource, IRQ, and DMUB code includes `dcn_3_1_5_offset.h` and this `dcn_3_1_5_sh_mask.h` file.
2. Register-list macros paste symbolic register names into offset names and field names. Offsets come from the companion offset header; field masks and shifts come from this file.
3. Macros such as `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `HUBBUB_SF(...)`, `TF_SF(...)`, `IPP_SF(...)`, `DMUB_SF(...)`, and IRQ register-entry helpers materialize per-ASIC register tables.
4. Driver code later uses those tables with register helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and polling/wait helpers to configure VM fault handling, HUBP surface fetching, cursor planes, flip interrupts, memory power, perf counters, and DMUB-visible register state.

The macros do not encode hardware ordering requirements. Consumers must still sequence page-table setup, VM fault clearing, HUBP blanking/reset, plane address updates, flip locking, DCC/TMZ programming, cursor updates, memory power transitions, clock gating, interrupt clear/ack, and suspend/resume restoration correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing in files or memory. It describes MMIO-backed GPU state. The represented state includes:

- DCN VM context configuration for page table depth, block size, base page-directory address, and logical page ranges for contexts 8 through 15.
- DCN VM default address and VM fault state, including status bits, VMID, translation response VMID, table level, pipe, interrupt status, and fault address.
- Perfmon state for counter-source selection, counter enable, clear, freeze, accumulation, interrupt masking, and overflow/interrupt reporting.
- HUBP plane-fetch state for surface format/layout, tiling, viewport coordinates, request granularity, clock/power/debug controls, outstanding-request status, timeout, underflow, and virtual-memory page size.
- HUBPREQ state for active and pending surface addresses, metadata addresses, surface pitch, VMID selection, DCC/TMZ protection, flip control, in-use address latching, TTU/QoS/prefetch timing, VM aperture/TLB behavior, cursor request adjustment, and memory power status.
- HUBPRET read-line and memory power state.
- Cursor position, size, format, address, hot spot, stereo, memory power, and DMDATA sideband state.

Persistence is hardware-defined. Many configuration registers retain values until modeset, plane update, power gating, suspend/resume, or ASIC reset. Status, interrupt, overflow, clear, ack, in-use, earliest-in-use, timeout, underflow, and memory-power status fields may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This generated header only gives bit positions and masks; it does not express access type or side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.5 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`, which supplies the matching MMIO register offsets.
- DCN base-address definitions such as `DCN_BASE__INST0_SEG*` in the DCN 3.1.5 resource, IRQ, and DMUB translation units.
- Common AMD display register helper macros that derive field masks/shifts from generated names.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`

Important consumer areas:

- HUBBUB code uses `DCN_VM_FAULT_*` masks/shifts through `HUBBUB_SF(...)` field lists to read and control display VM fault reporting.
- HUBP and IPP/DPP code uses `HUBP*`, `HUBPREQ*`, and `CURSOR0_*` fields for plane fetch, cursor programming, surface pitch/address, DCC/TMZ, request sizing, blanking, reset, and memory power.
- IRQ service code uses `HUBPREQ` flip interrupt registers to map HUBP flip events to DC IRQ sources.
- DMUB code uses `DMUB_DCN315_FIELDS()` with `FD_MASK`/`FD_SHIFT` to expose the same generated fields to firmware-facing register tables.
- Display mode, watermarks, and validation logic feed values that ultimately land in TTU, prefetch, vblank, flip, nominal, and per-line delivery registers described here.

## Risks And Edge Cases

- Field drift is the central risk. These macros are untyped constants, so an incorrect shift or mask can compile cleanly while setting the wrong bit field in MMIO.
- The chunk boundary is artificial. The first line is only the tail of `DCN_VM_CONTEXT8_CNTL`, and the last line stops inside `HUBPREQ2`; adjacent chunks are required for complete file-level claims.
- Repeated instance families are copy-sensitive. `HUBP0`/`HUBP1`/`HUBP2`, `HUBPREQ0`/`HUBPREQ1`/`HUBPREQ2`, `HUBPRET0`/`HUBPRET1`, `CURSOR0_0`/`CURSOR0_1`, and `DC_PERFMON6`/`7`/`8` are structurally similar but not interchangeable.
- VM context and VM fault fields affect GPU/display memory translation. Wrong masks can hide faults, clear the wrong sticky state, misreport VMID/pipe/table level, or program incorrect page-table ranges.
- Surface address and pitch fields are high impact. Bad masks can corrupt plane fetch addresses, chroma addresses, metadata addresses, DCC metadata, or pitch values, causing blank displays, corruption, underflow, or GPU faults.
- Flip-control and interrupt fields are sequencing-sensitive. Incorrect pending, lock, clear, or enable masks can cause missed page flips, stuck IRQs, frame pacing problems, or races during atomic commits.
- DCC and TMZ fields mix compression and protected-memory behavior. Incorrect values can produce display corruption, protection faults, or security-sensitive protected-surface exposure.
- TTU, prefetch, vblank, nominal, and per-line delivery fields are timing-sensitive. Incorrect masks can cause underflow only under specific modes, memory clocks, scaling, multi-plane, or multi-display workloads.
- Clock, reset, blank, memory-power, timeout, underflow, and perfmon fields may have side effects. Writes while a block is gated, reset, or actively scanning can be ignored or disruptive.

## Test Signals

Useful validation combines generated-header consistency checks and hardware behavior:

- Build AMDGPU/DC with DCN 3.1.5 support enabled. Missing or renamed masks/shifts should fail in `dcn315_resource.c`, `irq_service_dcn315.c`, `dmub_dcn315.c`, and shared HUBBUB/HUBP/DPP/IPP users.
- Mechanically verify that each visible `__SHIFT` macro in lines 7528-10046 has the expected companion `_MASK` macro for the same register field where the generated schema defines one.
- Diff this slice against AMD's authoritative DCN 3.1.5 register database and adjacent generated headers such as DCN 3.1/3.2 where hardware compatibility is expected.
- Exercise systems with enough active planes to use HUBP/HUBPREQ instances 0, 1, and 2: primary plane, overlays, chroma formats, cursor plane, page flips, scaling, DCC-enabled buffers, protected buffers, and suspend/resume.
- Validate DCN VM behavior by checking VM fault logging, fault clear behavior, fault interrupt enable/disable, VMID reporting, and page-table range programming under display memory pressure.
- Run display modes that stress request timing: high resolution, high refresh, multiple displays, DCC, cursor movement, overlays, bandwidth-limited memory clocks, and rapid atomic commits.
- Check flip IRQ behavior through DRM page-flip tests and kernel logs for missed/stuck flip interrupts.
- Monitor for HUBP underflow, timeout, no-outstanding-request hangs, DCC corruption, cursor artifacts, page-flip stalls, VM faults, and resume-only failures.
- Validate perfmon fields by enabling display perf counters and confirming counter source selection, clear/freeze, overflow, interrupt status, and high/low values behave plausibly.

## Cross-Chunk Notes

The previous chunk owns the beginning of the DCN VM context area, including the start of `DCN_VM_CONTEXT8_CNTL`. Later chunks continue `HUBPREQ2` after `HUBPREQ2_DCSURF_SECONDARY_META_SURFACE_ADDRESS_HIGH` and cover the rest of the generated DCN 3.1.5 shift/mask namespace. The final per-file report should merge adjacent chunks before making complete statements about all VM contexts, all HUBP/HUBPREQ instances, or the full `dcn_3_1_5_sh_mask.h` hardware map.

### subset-b-001869: lines 10047-12576

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 10047-12576

## Scope

This chunk is part of the generated AMD DCN 3.1.5 shift/mask header. It covers 2,530 source lines and defines 1,054 `__SHIFT` macros paired with 1,054 `_MASK` macros for 386 hardware register fields. The range starts in the middle of the HUBP pipe 2 request block and continues through HUBP/HUBPREQ/HUBPRET/cursor/perfmon pipe 3 plus the beginning of DPP0 CNVC, cursor converter, DSCL scaler, and CM color-management registers.

Address blocks present in this chunk:

- `dce_dc_dcbubp2_dispdec_hubpret_dispdec`
- `dce_dc_dcbubp2_dispdec_cursor0_dispdec`
- `dce_dc_dcbubp2_dispdec_hubp_dcperfmon_dc_perfmon_dispdec`
- `dce_dc_dcbubp3_dispdec_hubp_dispdec`
- `dce_dc_dcbubp3_dispdec_hubpreq_dispdec`
- `dce_dc_dcbubp3_dispdec_hubpret_dispdec`
- `dce_dc_dcbubp3_dispdec_cursor0_dispdec`
- `dce_dc_dcbubp3_dispdec_hubp_dcperfmon_dc_perfmon_dispdec`
- `dce_dc_dpp0_dispdec_cnvc_cfg_dispdec`
- `dce_dc_dpp0_dispdec_cnvc_cur_dispdec`
- `dce_dc_dpp0_dispdec_dscl_dispdec`
- `dce_dc_dpp0_dispdec_cm_dispdec`

## Purpose

The file does not implement functions or runtime control flow. Its purpose is to provide compile-time field metadata for DCN 3.1.5 memory-mapped display registers. Each field gets a bit shift and bit mask constant named as:

`<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.

Display code includes this header together with `dcn_3_1_5_offset.h` to build register tables for DCN 3.1.5 hardware. Helper macros such as `HUBP_SF(...)`, `TF_SF(...)`, and local `SF(...)` variants expand these definitions into structures that the driver later uses with register read/modify/write helpers.

## Important Macro Families

This chunk contributes several major hardware domains:

- `HUBPREQ2_*`: tail of pipe 2 request-side surface programming, including surface control, flip control, flip interrupts, in-use addresses, expansion modes, TTU/QoS timing, VM aperture/TLB controls, prefetch/blank/flip/nominal timing parameters, cursor request timing, and request-memory power controls.
- `HUBPRET2_*`: pipe 2 return-side packing/crossbar, read-line windows, vblank/read-line interrupt control, read-line value/status, and memory power state fields.
- `CURSOR0_2_*`: pipe 2 cursor enable/mode, surface address, size, position, hot spot, stereo offsets, destination offset, cursor memory power, and DMDATA address/control/QoS/status/software data fields.
- `DC_PERFMON9_*`: performance counter 9 control, counter state selectors, perfmon global control, interrupt/status/ack fields, and high/low counter value fields.
- `HUBP3_*`, `HUBPREQ3_*`, `HUBPRET3_*`, `CURSOR0_3_*`, and `DC_PERFMON10_*`: the same HUBP/request/return/cursor/perfmon pattern for pipe 3. These include primary/secondary luma and chroma surface addresses, DCC/TMZ flags, VM fault/underflow/done bits, TTU/QoS settings, flip/prefetch/vblank/nominal timing, and memory power state bits.
- `CNVC_CFG0_*`: DPP0 format/color-conversion configuration, including pixel format, format-control clamps and conversion modes, FP bias/scale registers, color keyer ranges, alpha LUT, pre-dealpha/realpha, pre-CSC matrix A/B banks, coefficient format, and pre-degamma mode/select fields.
- `CNVC_CUR0_*`: DPP0 cursor converter fields for cursor enable, expansion, pixel inversion, ROM enable, cursor mode, alpha modulation, update pending, cursor colors, and FP scale/bias.
- `DSCL0_*`: DPP0 scaler and line-buffer fields covering coefficient RAM tap select/data, scaler mode and tap count, 2-tap hardcoded/sharp controls, manual replicate factors, luma/chroma horizontal/vertical scale ratios and filter init values, black color, update pending, autocal, overscan, OTG blanking, recout/MPC sizes, line-buffer format/memory/v-counter, DSCL/OBUF memory power, and OBUF behavior.
- `CM0_*`: start of DPP0 color-management fields, including CM bypass/update pending, post-CSC matrices, gamut-remap matrices, color bias, gamma-correction control/LUT access, RAMA region programming for segments 0 through 33, and the beginning of RAMB start/end controls.

## APIs, Types, and Functions

No C APIs, functions, structs, or enums are declared in this chunk. The externally consumed interface is the macro namespace itself. The macros are used indirectly through generated register-list initializers in AMD display code.

Important integration patterns visible outside this chunk:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes `dcn/dcn_3_1_5_offset.h` and this header, then defines `SR`, `SRI`, `SRII`, and related helpers for register addresses.
- DCN HUBP headers such as `display/dc/hubp/dcn31/dcn31_hubp.h` define `HUBP_MASK_SH_LIST_DCN31(mask_sh)` using `HUBP_SF(register, field, mask_sh)` entries. For pipe instances, the same field layout is instantiated across `HUBPREQ0`, `HUBPREQ1`, `HUBPREQ2`, `HUBPREQ3`, cursor, HUBPRET, and HUBP register names.
- DPP headers such as `display/dc/dpp/dcn10/dcn10_dpp.h` and later DPP variants use `TF_SF(...)` for many `DSCL0_*`, `CM0_*`, `CNVC_CFG0_*`, and `CNVC_CUR0_*` fields supplied in this chunk.
- DCN 3.1.5 specific users include `dmub/src/dmub_dcn315.c`, `dc/irq/dcn315/irq_service_dcn315.c`, `dc/gpio/dcn315/*`, and `dc/resource/dcn315/dcn315_resource.c`.

## Control Flow

This chunk has no executable branches. Its control-flow role is compile-time token expansion:

1. DCN315 source files include this header and the matching offset header.
2. Hardware-object headers expand register-address macros and field shift/mask macros into per-block register and shift/mask tables.
3. Runtime display code calls generic register helpers that consume those tables when programming plane addresses, flips, cursors, scaler ratios, color conversion, gamma LUTs, interrupts, perf counters, or memory-power controls.

For example, a `HUBP_SF(HUBPREQ0_DCSURF_SURFACE_CONTROL, PRIMARY_SURFACE_DCC_EN, mask_sh)` style entry depends on a matching `HUBPREQ*_DCSURF_SURFACE_CONTROL__PRIMARY_SURFACE_DCC_EN__SHIFT` and `_MASK` pair in this header. The runtime path does not know the literal bit value; it relies on the generated table.

## State and Persistence

The macros themselves are stateless and persistent only as compiled constants. The hardware fields they describe are stateful DCN registers. This chunk covers state with several lifetimes:

- Frame/flip state: surface base addresses, metadata addresses, `SURFACE_UPDATE_LOCK`, `SURFACE_FLIP_PENDING`, stereo flip bits, flip interrupt clear/status, and current/earliest in-use address snapshots.
- Plane memory interpretation: pixel format, tiling, pitch, viewport dimensions, DCC enable/independent block fields, TMZ protected-memory bits, VMID, VM aperture, and L1 TLB behavior.
- Timing/QoS state: TTU, vblank, flip, nominal, prefetch, per-line delivery, reference-frequency-to-pixel-frequency, and request expansion fields.
- Cursor and DMDATA state: cursor address/size/position/hotspot, cursor memory power, DMDATA address/control/QoS/status, and software payload data.
- Interrupt/perf state: HUBPRET vblank/read-line interrupt mask/type/clear/status fields and perfmon counter control/status/ack/value registers.
- DPP processing state: CNVC format/color keying/CSC/degamma/alpha settings, DSCL coefficient RAM and scaler/line-buffer configuration, and CM post-CSC/gamut/gamma-correction LUT state.
- Power state: HUBPREQ, HUBPRET, cursor, DSCL, and OBUF memory power force/disable/mode/status fields.

Because these are display engine registers, persistence is generally limited to the current hardware programming epoch and is reset or reprogrammed during mode set, pipe construction, plane updates, power transitions, or GPU reset.

## Dependencies

Direct dependencies are structural rather than `#include` dependencies inside this chunk:

- It must stay synchronized with `dcn_3_1_5_offset.h`, which supplies the corresponding register addresses and base indices.
- It depends on AMD's generated register naming convention. Consumer macros concatenate register and field tokens, so spelling changes are ABI-like changes for the driver source.
- It depends on the DCN 3.1.5 hardware register specification. The numerical masks and shifts must match silicon, firmware expectations, and the display microcontroller's view of the same registers.
- It depends on common register helper infrastructure such as `reg_helper.h`, `HUBP_SF`, `TF_SF`, and block-specific `*_MASK_SH_LIST_*` macros that materialize these constants into structures.

## Integration Points

Key integration surfaces for fields in this range:

- HUBP/HUBPREQ programming for plane setup, surface flips, DCC/TMZ, VM/DLG/TTU timing, prefetch, and memory-request sizing.
- HUBPRET programming for detector-buffer base selection, component crossbar mapping, read-line tracking, and vblank/read-line interrupts.
- Cursor programming for address, position, format/mode, pitch, magnification, stereo offset, DMDATA, and cursor memory power management.
- DC perfmon programming for display performance counter selection, run/stop conditions, interrupt status/ack, and counter readback.
- DPP CNVC programming for pixel conversion, clamping, color keying, pre-CSC matrices, degamma, and alpha processing.
- DPP DSCL programming for scaler coefficients, ratios, taps, recout/MPC geometry, line-buffer layout, autocal, and memory power.
- DPP CM programming for post-CSC, gamut remap, gamma correction LUT and piecewise region programming.

## Risks

- A wrong shift or mask silently programs the wrong hardware bits. Effects can range from display corruption, underflow, missed flips, or broken cursor to VM faults, bad protected-memory handling, or hangs.
- Register-family symmetry is important. Pipe 2 and pipe 3 fields mirror earlier pipe instances; a mismatch across instances can cause bugs that appear only on specific display pipes or multi-display configurations.
- Many fields are multi-bit packed values. Off-by-one masks can truncate high bits for dimensions, addresses, LUT regions, scale ratios, or timing quantities.
- Several fields are status/clear/ack bits. Incorrect masks for `*_CLEAR`, `*_ACK`, or interrupt status fields can lose interrupts, repeatedly signal stale events, or clear unrelated status.
- Power-control fields can force or disable internal memories. Bad masks here can leave display subblocks powered down while active, or prevent low-power entry.
- The chunk ends in the middle of the `CM0_CM_GAMCOR_RAMB_*` sequence, so any merged per-file analysis must continue into later chunks before making whole-file conclusions about CM gamma-correction coverage.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/driver behavior:

- Build coverage for DCN315 display code, especially `dcn315_resource.c`, DPP, HUBP, IRQ, GPIO, and DMUB users that include this header.
- Macro-expansion coverage: references through `HUBP_MASK_SH_LIST_DCN31`, DPP `TF_SF` lists, perfmon, IRQ, and GPIO tables should compile without missing macro names.
- KMS/display smoke tests on DCN 3.1.5 hardware: mode set, multi-plane composition, cursor movement, flips, stereo/flip interrupt paths, multi-display pipe allocation, suspend/resume, and GPU reset.
- Plane feature tests: DCC enabled/disabled, protected memory/TMZ surfaces, luma/chroma planar formats, rotation/mirror/alpha plane, scaling, and color-management/gamma/gamut changes.
- Runtime diagnostics: no HUBP underflow, DMDATA VM fault/underflow/late status, unexpected flip-pending stalls, repeated vblank/read-line interrupts, or perfmon readback anomalies.
- Register trace comparison against known-good DCN 3.1.5 tables or vendor-generated register dumps can catch accidental mask/shift drift.

## Cross-Chunk Notes

This chunk starts after earlier `HUBPREQ2` surface address definitions and ends before the full CM RAMB gamma-correction region is complete. The final per-file report should merge this with neighboring chunks to cover the entire generated header, the include guard, all address blocks, and the complete DPP color-management macro set.

### subset-b-001870: lines 12577-15089

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 12577-15089

## Purpose

This chunk is generated AMD DCN 3.1.5 register field metadata for the display pipe color and scaler blocks. It contains no executable C; it publishes preprocessor constants mapping hardware register fields to bit shifts and masks. The display driver consumes these constants with the matching DCN 3.1.5 offset header to build register tables for DPP color processing, scaling, cursor, performance counter, and per-pipe state.

The range covers 2,513 physical lines and 2,112 `#define` entries: 1,057 `__SHIFT` macros and 1,064 `_MASK` macros. It starts inside the `CM0_CM_GAMCOR_RAMB` register family, continues through the rest of the DPP0 color-management and scaler-related fields, then enters DPP1 converter/scaler/color-management fields. It ends inside `CM1_CM_BLNDGAM_RAMA_REGION_6_7`, so the next chunk must complete that register and the remaining DPP1 blend-gamma RAMA/RAMB region definitions.

Although the repository path is under a `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or direct MMIO operations in this slice. Its public interface is the generated register-field macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

Important field families in this chunk:

- `CM0_CM_GAMCOR_RAMB_*`: final green/red end-control fields, RGB offsets, and 34 piecewise-linear region descriptors for gamma-correction RAM bank B on DPP0.
- `CM0_CM_BLNDGAM_*`: DPP0 blend-gamma control, LUT index/data/control, RAMA and RAMB start/end/base/offset fields, and region descriptors from `REGION_0_1` through `REGION_32_33`.
- `CM0_CM_HDR_MULT_COEF`, `CM0_CM_MEM_PWR_CTRL`, `CM0_CM_MEM_PWR_STATUS`, `CM0_CM_DEALPHA`, `CM0_CM_COEF_FORMAT`: DPP0 color multiplier, memory power force/status, alpha/dealpha, and coefficient format controls.
- `CM0_CM_SHAPER_*`: DPP0 shaper-LUT mode, RGB offsets/scales, LUT index/data/write-enable, RAMA/RAMB start/end controls, and region descriptors.
- `CM0_CM_MEM_PWR_CTRL2`, `CM0_CM_MEM_PWR_STATUS2`, `CM0_CM_3DLUT_*`, `CM0_CM_TEST_DEBUG_*`: DPP0 HDR 3D LUT and shaper memory-power controls, 3D LUT addressing/data/read-write controls, output normalization/offsets, and test/debug access.
- `DPP_TOP0_*`: DPP0 top-level clock enable, bypass, global alpha, soft reset, CRC values/control, and host read-control fields.
- `DC_PERFMON11_*`: performance counter and perfmon control/state/value fields for a DPP-related performance monitor instance.
- `CNVC_CFG1_*` and `CNVC_CUR1_*`: DPP1 surface pixel format, format expansion, fixed-point conversion bias/scale, color keying, alpha lookup, pre-dealpha/pre-realpha, pre-CSC matrices, coefficient format, pre-degamma selection, and cursor format/color/scale-bias fields.
- `DSCL1_*`: DPP1 scaler coefficient RAM access, scaler mode/taps, DSCL control, manual replication, horizontal/vertical/chroma ratios and initial phases, black color, update/autocal, overscan, OTG blank, recout/MPC size, line-buffer format/memory, LUT memory power, output buffer, and memory-power status/force fields.
- `CM1_CM_*`: DPP1 color-management control, post-CSC matrices, gamut remap matrices, bias controls, gamma-correction LUT/RAMA/RAMB fields, blend-gamma control/LUT, and the beginning of blend-gamma RAMA region descriptors.

The values are designed for token-pasting helpers in AMD display code. In `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, DCN315 includes `dcn/dcn_3_1_5_offset.h` and this shift/mask header, then initializes `dpp_regs[]`, `tf_shift`, and `tf_mask` from `DPP_REG_LIST_DCN30()` and `DPP_REG_LIST_SH_MASK_DCN30()`. Those macros are defined in `drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h`, where `SRI()` builds register addresses and `TF_SF()` pastes generated names such as `CM0_CM_GAMCOR_RAMB_REGION_0_1__CM_GAMCOR_RAMB_EXP_REGION0_LUT_OFFSET_MASK` into typed field tables.

## Control Flow

This header has no runtime control flow. The runtime flow is provided by AMD display resource construction and DPP programming code:

1. DCN315 resource construction includes the generated offset and shift/mask headers.
2. `dcn315_resource.c` expands `DPP_REG_LIST_DCN30(id)` for DPP instances 0 through 3, creating per-instance register address tables from the offset macros.
3. The same file expands `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)` once into `tf_shift` and `tf_mask`.
4. `dcn31_dpp_create()` passes those tables to `dpp3_construct()`, which gives each DPP object the addresses and field metadata needed by the shared DPP color/scaler implementation.
5. Runtime modeset, plane update, color-management, scaling, cursor, and power-management flows use register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and table-driven DPP operations to program the hardware.

The macros do not encode ordering. Consumers still need the hardware sequence for LUT access and bank switching: select host/config mode, write LUT indices/data, program start/end/region fields, handle current-vs-requested mode fields, avoid updating active banks incorrectly, and respect memory power state before touching shaper, blend-gamma, gamma-correction, or 3D LUT RAMs.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes fields whose state is held in DCN display hardware registers.

Hardware state represented here includes gamma-correction and blend-gamma PWL RAM selection, LUT index/data windows, RGB start/end/base/slope/offset values, region-to-LUT segmentation, shaper LUT configuration, HDR multiplier and 3D LUT output normalization/offsets, CSC and gamut-remap matrices, alpha/color-key/cursor/converter state, scaler taps/ratios/viewport sizing, DPP CRC/debug/perfmon state, and memory-power force/status for color and scaler RAMs.

Persistence is hardware-defined. Programmed color and scaler configuration normally survives until the next modeset/plane update, DPP reprogramming, display power gating, suspend/resume, or ASIC reset. Status fields such as `*_CURRENT`, `*_STATE`, `*_DONE`, `*_ERROR`, `*_CRC_*`, `*_READ_BUSY`, and memory-power status fields may be read-only, sticky, self-clearing, or write-sensitive depending on the underlying register specification. This generated header only provides bit layout; it does not describe access type or side effects.

## Dependencies And Integration Points

The constants in this range must match the generated DCN 3.1.5 register-offset file at `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`. A shift/mask macro is only useful when the corresponding `reg...` offset macro exists for the same register instance.

Important in-tree integration points:

- `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`: includes this header, creates DPP register tables for four DPP instances, and sets DCN315 color capabilities. The capabilities explicitly advertise gamma correction, hardware 3D LUT, output gamma RAM, post-CSC, and shaper/blend-gamma related color features that depend on these register definitions.
- `drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h`: defines `DPP_REG_LIST_DCN30_COMMON()`, `DPP_REG_LIST_DCN30()`, `DPP_REG_LIST_SH_MASK_DCN30_COMMON()`, and `DPP_REG_LIST_SH_MASK_DCN30_UPDATED()`. These macros consume many fields in this chunk for gamma correction, blend gamma, shaper, 3D LUT, converter, cursor, scaler, and DPP top-level control.
- `drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.h`: supplies shared transform-field lists used by the DCN30 DPP definitions, especially the exhaustive blend-gamma RAMA/RAMB region field list.
- `reg_helper.h` and the DPP implementation files: consume the generated `tf_shift` and `tf_mask` structures indirectly through register helper macros and DPP methods.
- DC color-management and DRM color pipeline entry points: user-visible gamma/CSC/gamut/shaper/3D-LUT changes ultimately rely on this register metadata when programmed on DCN315 hardware.

The chunk boundary is important. Lines before this chunk define the beginning of `CM0_CM_GAMCOR_RAMB_END_CNTL1_B` and `END_CNTL2_B`; this chunk begins at the green channel end-base field. Lines after this chunk complete `CM1_CM_BLNDGAM_RAMA_REGION_6_7` and continue the remaining DPP1 blend-gamma region definitions. The final per-file document should merge neighboring chunks before making complete claims about these two boundary families.

## Risks And Edge Cases

- Shift/mask drift is the primary risk. These macros are untyped constants, so incorrect generated values can compile cleanly while corrupting adjacent hardware fields.
- The generated names are consumed through token pasting. A missing, renamed, or instance-mismatched macro can fail builds in resource construction, while a wrong value can pass builds and fail only on hardware.
- `CM0` and `CM1` families are structurally similar but apply to different DPP instances. Copy/paste or generation errors can affect only one pipe, producing pipe-specific color, scaling, cursor, or CRC failures.
- PWL region fields are dense and repetitive. LUT offsets use 9-bit masks, segment counts use three-bit masks at bits 12 and 28, start/end/base fields commonly use 18-bit masks, end/slope pairs share one register, and RGB offsets use 19-bit masks. A one-bit mismatch can break only specific transfer-function segments.
- LUT access registers (`*_LUT_INDEX`, `*_LUT_DATA`, `*_LUT_CONTROL`, `*_3DLUT_READ_WRITE_CONTROL`) are sequencing-sensitive. Incorrect host selection, read/write mode, or index handling can update the wrong color bank or read stale data.
- Memory power controls interact with color RAM availability. Forcing or disabling gamma, blend-gamma, shaper, 3D LUT, scaler LUT, line-buffer, or output-buffer RAM power at the wrong time can cause blanking, corruption, underflow-like symptoms, or lost LUT writes.
- Scaler and converter fields are highly mode-dependent. Incorrect ratios, initial phases, taps, recout/MPC sizing, pixel format, alpha handling, or CSC matrix fields can create visual corruption that only appears for scaled, chroma, cursor, FP16, alpha, or color-keyed planes.
- Perfmon and debug fields may have side effects or require precise select/clear ordering. The header does not identify which fields are counters, status, clear bits, or readback windows.

## Test Signals

Useful validation combines generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU display support with DCN315 enabled so `dcn315_resource.c`, `dcn30_dpp.h`, and `dcn20_dpp.h` expansions catch missing or renamed macros.
- Mechanically verify that complete registers in this range have expected `__SHIFT` and `_MASK` pairs, while accounting for intentional chunk-boundary partials at the start and end.
- Compare this DCN 3.1.5 chunk against AMD's authoritative register database and adjacent DCN generation headers where DPP color/scaler layouts are expected to remain compatible.
- Exercise color-management paths on DCN315 hardware: gamma correction, blend gamma, shaper LUT, 3D LUT, post-CSC, gamut remap, HDR multiplier, alpha/dealpha, color keying, and bypass/current-mode transitions.
- Test LUT programming across RAMA/RAMB bank switching and suspend/resume to catch stale bank select, host select, memory power, or current-mode issues.
- Validate DPP1-specific scaler/converter behavior with scaled planes, chroma formats, cursor planes, alpha planes, FP16 conversion, color-keyed planes, and multi-plane composition.
- Use CRC and perfmon/debug readback where available to confirm that DPP top-level and perfmon fields remain readable and that field masks do not overlap unexpectedly.

## Cross-Chunk Notes

This chunk is source-tree-aligned to `dcn_3_1_5_sh_mask.h` and intentionally writes only the chunk research file. The previous chunk should cover the first part of `CM0_CM_GAMCOR_RAMB_END_CNTL*`; the next chunk should complete `CM1_CM_BLNDGAM_RAMA_REGION_6_7` and continue DPP1 blend-gamma RAMA/RAMB definitions. The later merge/reconciliation lane should combine these boundaries before producing final per-file conclusions.

### subset-b-001871: lines 15090-17598

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 15090-17598

## Scope

This chunk covers lines 15090-17598 of the generated AMD DCN 3.1.5 shift/mask header. It is preprocessor register metadata only: 2,113 `#define` entries across 2,509 source lines, with 1,056 `__SHIFT` constants, 1,065 `_MASK` constants, and generated register/address-block comments. There are no functions, structs, enums, variables, includes, allocations, locks, or executable statements in this range.

The range starts in the middle of the DPP1 color-management blend-gamma RAMA region table, continues through DPP1 blend-gamma RAMB, DPP1 shaper, DPP1 3DLUT, DPP1 DPP top, DPP1 performance monitor, DPP2 CNVC converter/cursor, DPP2 DSCL scaler, and DPP2 color-management blocks, then ends in the DPP2 blend-gamma RAMB region table. The first and last logical register groups are split across neighboring chunks.

## Purpose

The purpose of this header slice is to publish exact bit positions and masks for DCN 3.1.5 display-pipe hardware registers. AMDGPU display code combines these macros with the matching DCN 3.1.5 offset header and register helper macros to pack MMIO writes, read status fields, and instantiate per-ASIC DPP register tables without hard-coding raw bit positions in driver logic.

This file is a generated hardware contract. Runtime behavior lives in consumers such as the DCN 3.x DPP, color-management, scaler, converter, cursor, performance-monitor, resource-pool, IRQ, and DMUB code. This chunk only describes field layout.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask.
- `//<REGISTER>` comments group fields under a logical register.
- `// addressBlock: ...` comments identify the decoded display hardware block.

Major constant families in this chunk include:

- `CM1_CM_BLNDGAM_RAMA_REGION_8_9` through `CM1_CM_BLNDGAM_RAMA_REGION_32_33`, plus the split tail of `CM1_CM_BLNDGAM_RAMA_REGION_6_7`, covering DPP1 blend-gamma RAM A region LUT offsets and segment counts.
- `CM1_CM_BLNDGAM_RAMB_*`, covering DPP1 blend-gamma RAM B per-channel start, start segment, start slope, start base, end base, end value, end slope, offset, and region descriptors from regions 0-33.
- `CM1_CM_HDR_MULT_COEF`, `CM1_CM_MEM_PWR_CTRL`, `CM1_CM_MEM_PWR_STATUS`, `CM1_CM_DEALPHA`, `CM1_CM_COEF_FORMAT`, `CM1_CM_SHAPER_*`, `CM1_CM_MEM_PWR_CTRL2`, `CM1_CM_MEM_PWR_STATUS2`, `CM1_CM_3DLUT_*`, and `CM1_CM_TEST_DEBUG_*`, covering DPP1 color-management scalar controls, memory power, dealpha, shaper LUT setup, HDR 3D LUT mode/index/data, output normalization/offset, and test debug access.
- `DPP_TOP1_DPP_*` and `DPP_TOP1_HOST_READ_CONTROL`, covering DPP1 clock enable, global alpha, input/output color keyer controls, CRC control/results, soft reset, and host-read controls.
- `DC_PERFMON12_*`, covering DPP1/display performance counter event selection, counter control/state, perfmon control, interrupt/status, and high/low counter values.
- `CNVC_CFG2_*` and `CNVC_CUR2_*`, covering DPP2 converter surface format, format control, floating-point bias/scale, color keyer thresholds, alpha 2-bit LUT, pre-dealpha, pre-CSC matrix fields, pre-degamma, pre-realpha, and cursor control/colors/FP scale-bias.
- `DSCL2_*`, covering DPP2 scaler coefficient RAM, scaler mode/taps/ratios/initial phases, DSCL update/autocal, overscan, OTG blanking, recout/MPC sizing, line-buffer format/memory partitioning, line-buffer counters, DSCL/OBUF memory power, and OBUF controls.
- `CM2_CM_*`, covering DPP2 color-management bypass, post-CSC, gamut remap, bias, gamma correction RAMA/RAMB, blend-gamma control/LUT/RAMA/RAMB, and the beginning of blend-gamma RAMB region descriptors.

Many register families are structurally repeated across pipe instances. In this range, the suffixes `CM1`, `CNVC_CFG2`, `DSCL2`, `DPP_TOP1`, and `CM2` distinguish DPP/display-pipe instances while preserving field names consumed by common DPP helper macros.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time token expansion:

1. DCN 3.1.5 resource code includes the DCN 3.1.5 offset and shift/mask headers.
2. Resource tables such as `dcn315_resource.c` expand DPP register-list macros into `dpp_regs`, `tf_shift`, and `tf_mask` tables using `DPP_REG_LIST_DCN30(...)` and `DPP_REG_LIST_SH_MASK_DCN30(...)`.
3. DPP constructors such as `dpp3_construct()` store pointers to those tables in `struct dcn3_dpp`.
4. Runtime DPP code uses helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG`, and transfer-function helpers to concatenate register/field names and resolve the `__SHIFT`/`_MASK` constants from this header.
5. The resolved values drive MMIO register reads, writes, read-modify-write updates, indexed LUT writes, and status decoding.

The declaration order mirrors hardware organization rather than software call order: DPP1 color management, DPP1 top/perf blocks, then DPP2 converter/scaler/color-management blocks. Repeated per-channel and per-region definitions are intentionally expanded as independent symbols so common code can address a specific instance/register/field combination at compile time.

## State And Persistence Behavior

The header stores no software state and persists no data. It describes bit locations for state held in DCN 3.1.5 display hardware registers.

Writable fields in this chunk can program transfer-function RAM descriptors, shaper curves, blend-gamma curves, 3D LUT mode/index/data, color matrices, color keying, alpha handling, format conversion, cursor format/color controls, scaler coefficients and geometry, DPP top-level clock/reset/CRC controls, performance counter configuration, and memory power controls for color-management, scaler, line-buffer, and OBUF memories.

Hardware-updated fields expose current mode/select state, memory power state, CRC results, soft-reset state, scaler update state, line-buffer counters, performance counter state, performance interrupt/status, and readback/debug data. This header does not encode access type, reset values, read-clear/write-one-to-clear behavior, required polling, or programming sequences.

Programmed values persist according to the relevant display block power and reset domains. They may remain in hardware until a modeset rewrite, plane update, display block reset, DPP power gating, suspend/resume restore, GPU reset, or full ASIC reset. Status fields can change asynchronously relative to the driver code that includes these macros.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.5 offset header for register addresses. The shift/mask header identifies bit placement only; it does not provide MMIO addresses or base indices.

Primary consumers are AMDGPU display register helpers and generated register tables:

- `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes this ASIC register metadata and expands DPP register lists into `dpp_regs`, `tf_shift`, and `tf_mask`.
- `drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.c` and `dcn30_dpp_cm.c` use the stored shift/mask tables to program post-CSC, gamut remap, gamma correction, blend gamma, shaper, 3D LUT, memory power, converter, cursor, and scaler-related fields.
- `dpp3_construct()` wires the per-instance register table and shared shift/mask table into each `struct dcn3_dpp`.
- `dmub/src/dmub_dcn315.c` also includes `dcn_3_1_5_sh_mask.h` for DCN315 DMUB register definitions, though the DPP/color-management fields in this specific range are mainly consumed by display-pipe code.

Key functional integration areas are:

- Plane color pipeline setup: pre-CSC/pre-degamma/pre-dealpha in `CNVC_CFG2`, post-CSC/gamut remap/bias/gamma/blend/shaper/3DLUT in `CM1` and `CM2`.
- Transfer-function programming: `CM*_CM_GAMCOR_*`, `CM*_CM_BLNDGAM_*`, and `CM1_CM_SHAPER_*` define RAM A/B start, end, slope, base, offset, and region descriptor fields used by common transfer-function helpers.
- LUT access paths: `CM1_CM_SHAPER_LUT_INDEX/DATA/WRITE_EN_MASK`, `CM1_CM_3DLUT_INDEX/DATA/DATA_30BIT/READ_WRITE_CONTROL`, and `CM2_CM_GAMCOR/BLNDGAM_LUT_*` fields are used to sequence indexed RAM writes and reads.
- Scaler and viewport programming: `DSCL2_*` fields back coefficient RAM loading, tap selection, scaling ratios, initial phases, autocal, recout/MPC sizing, blanking, and line-buffer partitioning.
- Cursor and conversion paths: `CNVC_CUR2_*` and `CNVC_CFG2_*` fields configure cursor enable/mode/color, surface format, alpha, keying, FP bias/scale, and channel crossbar/clamping behavior.
- Diagnostics and debug: `DPP_TOP1_DPP_CRC_*`, `DC_PERFMON12_*`, and `CM*_CM_TEST_DEBUG_*` expose CRC, performance-counter, and test/debug control/status.
- Power management: `CM1_CM_MEM_PWR_*`, `CM1_CM_MEM_PWR_CTRL2/STATUS2`, `DSCL2_DSCL_MEM_PWR_*`, and `DSCL2_OBUF_MEM_PWR_CTRL` fields control or observe subblock memory power states.

The generated DCN 3.1.5 offset and shift/mask headers must come from the same ASIC register database. Mixing a DCN315 shift/mask header with DCN314/DCN316/DCN32 offsets or resource tables is especially risky because many field names and layouts are visually similar while instance counts, offsets, or high-bit fields can differ.

## Risks And Edge Cases

- The chunk starts mid-register. Only the final mask for `CM1_CM_BLNDGAM_RAMA_REGION_6_7__CM_BLNDGAM_RAMA_EXP_REGION7_NUM_SEGMENTS_MASK` is present here; the rest of `CM1_CM_BLNDGAM_RAMA_REGION_6_7` is in the previous chunk.
- The chunk ends inside the DPP2 blend-gamma RAMB region table. It includes `CM2_CM_BLNDGAM_RAMB_REGION_24_25` completely and starts `CM2_CM_BLNDGAM_RAMB_REGION_26_27`, `28_29`, and `30_31` in the visible range; the later field definitions continue in the next chunk.
- Repeated region macros are copy-sensitive. The region tables use the same pattern for pairs of regions, with LUT offset fields at shifts `0x0` and `0x10`, segment-count fields at `0xc` and `0x1c`, and masks such as `0x000001FFL`, `0x00007000L`, `0x01FF0000L`, and `0x70000000L`. A generator or hand-edit mistake can compile but misplace gamma curve regions.
- Many control and status fields share nearby registers. Examples include DPP soft reset vs. reset status, memory power force/disable vs. state, current mode/select fields vs. requested mode/select fields, perf-counter interrupt controls vs. status, and DSCL update/autocal fields. The access semantics are not represented by the masks.
- Full-width or high-bit masks such as LUT data, 3D LUT data, performance counter values, CSC coefficients, scale ratios, and packed geometry fields require 32-bit unsigned handling. Signed assumptions around constants ending in `L` can be hazardous in nonstandard helper code.
- Indexed LUT programming is sequence-sensitive. `CM*_LUT_INDEX`, `CM*_LUT_DATA`, LUT write color masks, host-select fields, config-mode fields, and 3D LUT read/write control must be coordinated by higher-level code; these macros do not protect against writing the wrong RAM bank or color component.
- Color-pipeline fields are user-visible. Incorrect masks for CSC, gamut remap, gamma, blend-gamma, shaper, 3D LUT, format conversion, or alpha fields can present as color shifts, banding, clipping, incorrect HDR behavior, cursor artifacts, or alpha blending regressions rather than obvious kernel faults.
- Scaler and line-buffer fields are modeset-critical. Bad DSCL masks for taps, ratios, initial phases, recout size, MPC size, line-buffer partitions, or memory power can cause scaling artifacts, underflow, blank output, or intermittent display failures.
- Performance monitor fields are diagnostic-sensitive. Wrong event-selection, counter-state, or interrupt masks can make perf telemetry misleading while normal display output still appears functional.

## Test Signals

Useful validation is mostly build-time consistency plus hardware integration:

- Build AMDGPU display code with DCN315 support to catch missing or renamed macros used by `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)` expansion in `dcn315_resource.c`.
- Mechanically verify that each complete register group in this range has paired `__SHIFT` and `_MASK` entries for every field, accounting for the intentionally partial first and last register groups.
- Compare this slice against the authoritative DCN 3.1.5 register database and the matching offset header to ensure every field has the intended bit position and every logical register maps to the intended address.
- Exercise color-management paths on DCN315 hardware: SDR/HDR transfer functions, degamma, gamma correction, blend gamma, shaper LUT, 3D LUT, post-CSC, gamut remap, bias, dealpha/realpha, and format conversion. Look for banding, channel swaps, clipping, alpha errors, and incorrect current-mode reporting.
- Exercise indexed LUT programming with nontrivial curves and alternating RAM A/RAM B use so region descriptors, start/end/base/slope/offset fields, LUT indices, data registers, write color masks, host-select fields, and config-mode fields all move through real values.
- Exercise DPP2 scaler modes with luma/chroma scaling, different tap counts, coefficient RAM programming, overscan, recout/MPC sizing, line-buffer partition changes, and memory power transitions. Watch for underflow, scaler-update stalls, and corrupted output.
- Exercise cursor formats and color-key/alpha paths through `CNVC_CUR2` and `CNVC_CFG2`, including cursor enable/disable, color0/color1, FP scale/bias, color keyer ranges, alpha plane enable, pre-dealpha, and pre-realpha.
- Exercise diagnostics by reading DPP CRC results, DC_PERFMON12 counter values/states, and CM test-debug registers where available. Verify that control bits and status bits decode as expected.
- Exercise suspend/resume, display hotplug, modeset, plane updates, and power-gating paths to ensure memory-power force/disable/status fields and restored color/scaler state behave consistently after block reset or power transitions.

## Open Cross-Chunk Notes

The merge lane should combine this chunk with the previous chunk to describe `CM1_CM_BLNDGAM_RAMA_REGION_6_7` completely. It should combine this chunk with the next chunk to complete the DPP2 blend-gamma RAMB region table after `CM2_CM_BLNDGAM_RAMB_REGION_24_25`, especially the later `26_27`, `28_29`, `30_31`, and `32_33` definitions. Whole-file analysis should reconcile this chunk with neighboring DCN 3.1.5 generated-header chunks before making final claims about the complete DPP1/DPP2 color, converter, scaler, perfmon, and memory-power register coverage.

### subset-b-001872: lines 17599-20110

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 17599-20110

## Chunk Scope

This chunk is a generated AMD DCN 3.1.5 register shift/mask header fragment. It contains 2,114 preprocessor definitions: 1,057 `__SHIFT` constants and 1,057 matching `_MASK` constants. There is no executable C code, no structs, and no functions in this range. Its API surface is the macro namespace consumed by AMD display register helpers to pack, unpack, and update hardware register fields.

The slice covers the tail of DPP2 color management, DPP2 top/perfmon controls, DPP3 converter/cursor/scaler controls, and the beginning-to-mid section of DPP3 color management. The requested boundary ends at line 20110 in the middle of `CM3_CM_SHAPER_RAMB_END_CNTL_G`; later fields for that register and later CM3 shaper RAMB registers are outside this chunk.

## Purpose

The purpose of this chunk is to describe bit positions and masks for display pipe processor register fields. These constants let driver code use generic AMD DC helpers such as field-write/read macros without hardcoding numeric bit ranges at each call site. The values are hardware ABI, not algorithmic behavior: correctness depends on matching the silicon register specification for DCN 3.1.5.

Major covered hardware areas:

- `CM2_*`: DPP2 color management tail, including blend gamma RAMB regions, HDR multiplier, memory power control/status, dealpha, coefficient formats, shaper LUT/RAM A/B definitions, 3D LUT, and debug registers.
- `DPP_TOP2_*`: DPP2 top-level clock gates, soft reset, CRC value/control, and host read-rate fields.
- `DC_PERFMON13_*`: DPP2 display performance monitor counter control, state, interrupt/status, counter value, high/low readback fields.
- `CNVC_CFG3_*` and `CNVC_CUR3_*`: DPP3 converter format, color keyer, pre-CSC, pre-degamma, realpha, and cursor format/color fields.
- `DSCL3_*`: DPP3 scaler coefficient RAM, mode/taps, ratios, init phases, overscan, recout/MPC geometry, line-buffer state, memory power, and output buffer controls.
- `CM3_*`: DPP3 color management controls for post-CSC, gamut remap, bias, gamma correction RAM A/B, blending gamma RAM A/B, HDR multiplier, memory power, dealpha, coefficient format, and the beginning of shaper LUT/RAM A/B.

## Important APIs and Macro Patterns

Every field is exported as two macros:

- `<REGISTER>__<FIELD>__SHIFT`: the least significant bit position for the field.
- `<REGISTER>__<FIELD>_MASK`: the register mask for that field.

Driver-side register helpers combine these two values to clear, shift, set, and read fields. The include is pulled into DCN 3.1.5 integration files including `display/dmub/src/dmub_dcn315.c`, `display/dc/irq/dcn315/irq_service_dcn315.c`, `display/dc/gpio/dcn315/hw_factory_dcn315.c`, `display/dc/gpio/dcn315/hw_translate_dcn315.c`, and `display/dc/resource/dcn315/dcn315_resource.c`. General helper macros in `display/dc/dm_services.h` construct references such as `reg_name__reg_field_MASK` and `reg_name__reg_field__SHIFT`, so spelling and suffix format are part of the public compile-time contract.

Notable macro groups in this chunk:

- Gamma/shaper region pairs use a repeated two-region packing layout: region `N` LUT offset at bit 0 or 16, region segment count at bit 12 or 28, with masks like `0x000001FFL`, `0x00007000L`, `0x01FF0000L`, and `0x70000000L`.
- Color-matrix coefficient pairs pack two 16-bit fields per register, for example `C11_C12`, `C13_C14`, through `C33_C34`, with masks `0x0000FFFFL` and `0xFFFF0000L`.
- Many status/control fields have corresponding current or pending status bits, such as `CM*_UPDATE_PENDING`, `*_MODE_CURRENT`, `SCL_UPDATE_PENDING`, and `CUR0_UPDATE_PENDING`.
- Full-register read/value fields use `0xFFFFFFFFL`, for example performance monitor low values and debug data.

## Control Flow

There is no runtime control flow in the chunk. The effective control flow is at compile time:

1. A DCN 3.1.5 C source includes this header together with matching offset headers.
2. Register-list macros in resource or block-specific source files expand field names into the corresponding `_MASK` and `__SHIFT` constants.
3. Runtime code calls register access helpers to update memory-mapped display registers.
4. The helper uses the constants to preserve unrelated fields, encode new field values, or extract current hardware state.

Because the constants are generated, review should focus on structural consistency: every shift should have a mask, each register field should fit within 32 bits, and mirrored pipes/blocks should keep the same layout unless the ASIC spec says otherwise.

## State and Persistence Behavior

The file itself persists no state. The state described by the macros is hardware state in display registers:

- Color management state includes LUT indices/data, RAM A/B region tables, CSC/gamut matrices, bias, HDR multiplier, shaper and 3D LUT modes.
- Power-management state includes memory force/disable bits and status fields for gamma correction, blending gamma, shaper, 3D LUT, scaler LUT/line-buffer groups, and OBUF memory.
- Synchronization/readback state includes update-pending, mode-current, CRC, perfmon active, counter state, interrupt status/ack, and cursor/scaler update-pending bits.

Persistence is therefore governed by hardware register lifetime, display pipeline programming sequences, resets, and power gating. Wrong masks can persist incorrect hardware state until the affected block is reprogrammed or reset.

## Dependencies and Integration Points

This chunk depends on:

- Matching DCN 3.1.5 offset headers that define the register addresses for these field masks.
- AMD display helper macros in `display/dc/dm_services.h`, especially helpers that concatenate register and field names with `_MASK` and `__SHIFT`.
- DC resource construction for DCN 3.1.5, where block register lists and mask/shift lists are assembled into per-block register tables.
- Block implementations for color management, cursor/converter, scaler, CRC, perfmon, and power management that expect these fields to match the actual hardware.

Integration boundaries visible in the chunk:

- `addressBlock: dce_dc_dpp2_dispdec_dpp_top_dispdec` starts DPP2 top-level fields after CM2 color-management fields.
- `addressBlock: dce_dc_dpp2_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` starts performance-monitor fields.
- `addressBlock: dce_dc_dpp3_dispdec_cnvc_cfg_dispdec`, `cnvc_cur`, `dscl`, and `cm` start DPP3 converter, cursor, scaler, and color-management field definitions.

## Risks

- A wrong shift or mask silently corrupts neighboring bits in memory-mapped registers. This can break color processing, scaling, cursor display, CRC testing, perf counters, power gating, or pipeline reset behavior.
- Generated naming is fragile: helper macros rely on exact `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` spelling. Renames or missing definitions become compile failures in downstream register-list expansions.
- Mirrored blocks such as CM2/CM3, RAMA/RAMB, and channel-specific R/G/B controls are highly repetitive. Copy-generation mistakes are easy to miss by eye but can affect only one pipe, one RAM bank, or one color channel.
- The chunk boundary is mid-`CM3_CM_SHAPER_RAMB_END_CNTL_G`; any final merged research must reconcile this chunk with the next one before claiming complete coverage of CM3 shaper RAMB behavior.
- Many fields control memory power or reset. Incorrect masks for `*_MEM_PWR_FORCE`, `*_MEM_PWR_DIS`, `*_MEM_PWR_STATE`, or `*_SOFT_RESET` can lead to hangs, blank output, readback timeouts, or display corruption that appears far from the original register write.
- CRC and perfmon masks are test/debug infrastructure. Bugs here may not affect normal display output but can invalidate diagnostics, automated display tests, or performance analysis.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/display integration tests:

- Build coverage for DCN 3.1.5 display code catches missing or misspelled macros used by resource, IRQ, GPIO, DMUB, or block register-list code.
- Static consistency checks can verify that the chunk has paired `__SHIFT` and `_MASK` definitions; this slice has 1,057 of each.
- Register-generation diff tests against the authoritative ASIC register database should flag changed bit positions, masks, or omitted fields.
- Display smoke tests should exercise DPP2/DPP3 paths with scaling, cursor, CSC/gamut/color management, gamma/blending LUT programming, and power transitions.
- CRC tests can validate `DPP_TOP2_DPP_CRC_*` fields by enabling one-shot or continuous CRC and comparing stable expected values for known frames.
- Perfmon tests can program `DC_PERFMON13_*` counters, check active/state transitions, interrupt status/ack behavior, and high/low counter readback.
- Suspend/resume, hotplug, and modeset tests are important for memory power and soft-reset fields because stale or incorrect power state masks can cause intermittent failures after block gating or reinitialization.

### subset-b-001873: lines 20111-22625

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 20111-22625

## Purpose

This chunk is generated AMD DCN 3.1.5 register field metadata. It contains no executable C logic; it publishes preprocessor constants for MMIO register field shifts and masks used by AMDGPU display code when programming color-management, DPP, MPC, MPCC, output-gamma, performance-monitor, update-lock, DWB, and related display-composition blocks.

The requested range covers 2,515 physical lines with 2,101 `#define` entries: 1,052 `__SHIFT` macros and 1,057 `_MASK` macros. It begins inside the `CM3` shaper RAMB register family, after neighboring lines already defined the CM3 shaper RAMB start controls and most B/G end controls. It then covers CM3 shaper RAMB region descriptors, CM3 shaper/3DLUT memory-power and LUT access fields, DPP top and CRC/control fields for DPP3, DC performance-monitor block 14, MPCC0 through MPCC3 blend/composition controls, global MPC control/update-lock/DWB mux fields, DC performance-monitor block 15, complete MPCC_OGAM0 and MPCC_OGAM1 output-gamma/gamut-remap register families, and the beginning of MPCC_OGAM2 through `MPCC_OGAM2_MPCC_OGAM_RAMB_REGION_12_13`.

Although the repository path is under a `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, or allocation paths in this chunk. The interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

These constants are consumed with the matching DCN 3.1.5 offset header and register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, `FD_SHIFT`, `SF`, and `SRI`. Direct DCN 3.1.5 users include `dmub_dcn315.c`, `irq_service_dcn315.c`, `hw_factory_dcn315.c`, `hw_translate_dcn315.c`, and `dcn315_resource.c`; the color and MPC families are also matched by generic DPP/MPC register-list and field-list macros under `display/dc/dpp` and `display/dc/mpc`.

Major register families in this slice:

- `CM3_CM_SHAPER_RAMB_*`, `CM3_CM_MEM_PWR_CTRL2`, `CM3_CM_MEM_PWR_STATUS2`, and `CM3_CM_3DLUT_*`: DPP instance 3 color-management shaper RAM B piecewise-linear region layout, shaper/HDR 3DLUT memory power control/status, 3DLUT mode/size/current mode, index/data writes, 30-bit data access, RAM selection, read/write control, output normalization, output offsets, and debug index/data.
- `DPP_TOP3_*`: DPP instance 3 top-level enable, clock gating, soft reset, CRC values/control, and host-read control.
- `DC_PERFMON14_*` and `DC_PERFMON15_*`: performance-counter and performance-monitor control/state/value registers for the DPP3 and MPC performance-monitor address blocks.
- `MPCC0_*` through `MPCC3_*`: MPCC top/bottom source selection, OPP routing, composition mode, alpha/blend control, update-lock selection, top/bottom gains, background color components, memory power controls for the MPCC and OGAM memories, and status fields.
- `MPC_*`, `ADR_CFG_*`, `ADR_VUPDATE_*`, `CFG_VUPDATE_*`, `CUR_VUPDATE_*`, and `MPC_DWB0_MUX`: global MPC clock/reset/CRC/perf controls, bypass background, host-read control, DPP pending status, update-lock set address/config/current state for sets 0 through 3, DWB mux selection/status, and pending/vertical-update coordination fields.
- `MPCC_OGAM0_*` and `MPCC_OGAM1_*`: complete output-gamma blocks for MPCC instances 0 and 1, including OGAM control/current state, LUT index/data/control, RAM A and RAM B start/end/base/slope/offset/region descriptors, gamut-remap coefficient format/mode, and two banks of gamut-remap matrix coefficients.
- `MPCC_OGAM2_*`: start of the same output-gamma family for MPCC instance 2, from OGAM control/LUT controls through RAM A and the beginning of RAM B region descriptors. The chunk ends before the instance-2 RAMB region table and gamut-remap matrix are complete.

## Control Flow

This header has no runtime control flow. Runtime sequencing is provided by AMD display code:

1. DCN 3.1.5 resource, GPIO, IRQ, and DMUB code include `dcn_3_1_5_offset.h` and this `dcn_3_1_5_sh_mask.h` header.
2. Register-list macros paste instance, register, and field names into constants such as `CM3_CM_3DLUT_MODE__CM_3DLUT_MODE_MASK`, `MPCC0_MPCC_CONTROL__MPCC_MODE_MASK`, or `MPCC_OGAM1_MPCC_OGAM_RAMA_REGION_0_1__MPCC_OGAM_RAMA_EXP_REGION0_LUT_OFFSET_MASK`.
3. Hardware abstraction tables store offsets plus field shifts/masks, then `REG_*` helper calls perform MMIO reads, writes, waits, and read-modify-write updates against those fields.
4. Display runtime paths use those tables during modeset, pipe composition, DPP color programming, MPCC blend programming, output-gamma and gamut-remap updates, memory power transitions, CRC/debug capture, performance monitoring, vertical-update lock coordination, DWB routing, and suspend/resume restoration.

The macros do not encode ordering or access semantics. Consumers must still respect hardware sequencing: power OGAM/3DLUT memories before writing LUT RAM, select the correct RAM bank before loading or switching LUTs, coordinate update locks with vupdate timing, wait on current/status fields before assuming a bank or mode is active, and avoid unsafe writes to status or debug fields.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on its own. It describes hardware register fields whose values live in the display ASIC.

Hardware state represented by these fields includes CM3 shaper region tables, CM3 3DLUT index/data/output normalization state, DPP3 enable/reset/CRC/debug state, MPCC source selection and blending state, MPCC memory power state, MPCC background colors and gains, MPC clock/reset/CRC/performance state, pending DPP/update-lock state, DWB mux routing state, MPCC_OGAM LUT bank selection and contents, PWL region geometry, gamut-remap matrix values, and current-mode/status fields.

Persistence is hardware-defined. Programming fields generally remain until another modeset/color update changes them, display blocks are power-gated, suspend/resume reinitializes the display engine, or the ASIC is reset. Status-like fields such as `*_CURRENT`, `*_STATUS`, `*_STATE`, `*_PENDING`, `*_MEM_PWR_STATE`, CRC values, and performance-counter values may be read-only, sticky, self-clearing, or write-one-to-clear depending on the register specification. This generated header only gives bit positions and masks; it does not define access type or side effects.

## Dependencies And Integration Points

The constants in this range must match `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h` and the DCN base-address definitions in the consumers. They are token-pasted by the display register helpers, so spelling, instance prefix, and mask width are part of the ABI between the generated register database and the C hardware-block tables.

Important in-tree integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which includes this header, defines DCN base segments, and expands resource register tables for DCN 3.1.5 hardware blocks.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`, which expands DMUB register masks and shifts through `DMUB_DCN315_FIELDS()` using `FD_MASK` and `FD_SHIFT`.
- `drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`, which includes the same offset and shift/mask headers for interrupt enable/ack register descriptions.
- `drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c` and `hw_translate_dcn315.c`, which use the generated DCN 3.1.5 register metadata for GPIO/AUX/DDC translation even though this specific chunk is mostly color/MPC-oriented.
- `drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.h`, whose color-management field lists include CM shaper, 3DLUT, memory-power, debug, and DPP top fields that map to the CM3/DPP_TOP3 families in this chunk.
- `drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h` and `dcn30_mpc.c`, whose MPCC/OGAM register lists and functions consume the MPCC, MPCC_OGAM, MPC update-lock, DWB, and memory-power fields represented here.

The chunk is boundary-sensitive. The previous chunk owns the earlier CM3 shaper RAMA/RAMB setup fields, including the start of RAMB end controls. The next chunk must finish MPCC_OGAM2 RAMB regions and the remaining instance-2 gamut-remap fields before final file-level research makes complete claims about MPCC_OGAM2.

## Risks And Edge Cases

- Shift/mask drift is the primary risk. These are untyped preprocessor constants; an incorrect mask can compile cleanly while writing the wrong hardware bits.
- The repeated MPCC and MPCC_OGAM families are copy-sensitive. A prefix error between MPCC0/1/2/3 or RAMA/RAMB can affect only one pipe, one LUT bank, or one color path, making failures mode-dependent.
- LUT programming is stateful. CM3 and MPCC_OGAM index/data/control fields depend on host selection, color write masks, active RAM bank, PWL enable/disable state, and memory power state. Updating the wrong bank or writing while memory is powered down can cause visible color corruption or failed updates.
- Update-lock and vupdate fields are timing-sensitive. Incorrect address/config/current update-lock masks can leave pipe state stuck pending, applied outside vblank, or mismatched across multi-plane composition.
- MPCC composition fields affect blending and routing. Bad top/bottom selection, OPP ID, gain, alpha, background, or mode fields can produce missing planes, incorrect blending, wrong output routing, or artifacts that only appear with overlays, MPO, or DWB.
- Status, CRC, perfmon, and debug registers may have non-obvious read/clear behavior. Generic read-modify-write against fields with side effects can lose events or corrupt counters.
- Full-width or broad masks such as background colors, coefficients, CRC values, and debug data need value-range discipline from consumers; the header does not validate fixed-point formats or coefficient sign/scale.

## Test Signals

Useful validation combines generated-header consistency, build coverage, and display behavior:

- Build AMDGPU display paths for DCN 3.1.5 so includes of `dcn_3_1_5_sh_mask.h`, `dcn315_resource.c`, DMUB, IRQ, GPIO, DPP, and MPC tables catch missing or renamed macros.
- Mechanically verify that complete fields in lines 20111-22625 have matching `__SHIFT` and `_MASK` definitions, while accounting for intentional boundary exceptions at the start of CM3 RAMB end controls and the end of MPCC_OGAM2 RAMB regions.
- Compare this chunk against AMD's authoritative DCN 3.1.5 register database and adjacent DCN generation headers where MPCC, OGAM, DPP, and perfmon layouts are expected to match.
- Exercise color-management paths on DCN 3.1.5 hardware: shaper LUT, 3DLUT, OGAM LUT, RAM A/RAM B bank switching, gamut-remap matrices, bypass modes, HDR/SDR transitions, and suspend/resume with color state restored.
- Test MPCC composition behavior with single-plane, multi-plane overlay, alpha blending, underlay/background color, pipe split, and DWB capture/routing scenarios.
- Validate vupdate/update-lock behavior during page flips, modesets, MPO transitions, and color updates, watching for stuck pending status or updates applied on the wrong frame.
- Validate memory-power sequencing by enabling/disabling OGAM and 3DLUT paths across blank/unblank and power-management transitions, checking waits on memory state and absence of LUT write failures.
- Use CRC, perfmon, and debug paths where available to detect whether DPP3/MPC register programming produces expected counters, CRC values, and no unexpected pending/error states.

## Cross-Chunk Notes

This chunk starts at `CM3_CM_SHAPER_RAMB_END_CNTL_R`; `CM3_CM_SHAPER_RAMB_START_CNTL_*` and the B/G end-control definitions are in the previous chunk. It ends inside `MPCC_OGAM2_MPCC_OGAM_RAMB_REGION_12_13`; the next chunk should continue with the remaining MPCC_OGAM2 RAMB region descriptors and then cover the instance-2 gamut-remap fields. The final per-file document should merge those boundaries before summarizing complete CM3 shaper RAMB or MPCC_OGAM2 behavior.

### subset-b-001874: lines 22626-25141

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 22626-25141

## Scope

This chunk covers lines 22626-25141 of the generated AMD DCN 3.1.5 shift/mask header. It is entirely preprocessor register metadata: 2,104 `#define` entries across 2,516 source lines, with 1,053 `__SHIFT` constants and 1,058 `_MASK` constants plus generated register and `addressBlock` comments. There are no functions, structs, enums, variables, includes, allocation paths, locks, or executable statements in this range.

The range starts in the middle of `MPCC_OGAM2_MPCC_OGAM_RAMB_REGION_4_5` with its final masks, then covers the tail of MPCC OGAM instance 2, the complete visible MPCC OGAM instance 3 block, MPC output mux/output CSC/denorm masks, MPC RMU global and RMU instance 0/1 shaper and 3DLUT masks, ABM0 backlight and adaptive backlight statistics masks, and the beginning of ABM1. It ends mid-register at `ABM1_DC_ABM1_HGLS_REG_READ_PROGRESS`; the masks and clear fields for that register continue in the next chunk.

## Purpose

The purpose of this header slice is to publish exact bit positions and masks for DCN 3.1.5 display hardware registers. AMDGPU display code combines these constants with the matching `dcn_3_1_5_offset.h` addresses and register helper macros to pack MMIO writes, perform read-modify-write updates, and decode status fields without embedding raw bit positions in driver logic.

This is a generated hardware contract. Runtime behavior is implemented by consumers such as DCN315 resource construction, MPC color-management code, ABM/backlight code, DMUB, IRQ, and GPIO setup paths. This file only supplies the field layout that those consumers paste into `REG_*`, `FD_SHIFT`, and `FD_MASK` style helpers.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives a field's low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within a 32-bit register value.
- `//<REGISTER>` comments group fields for one logical register.
- `// addressBlock: ...` comments group registers by decoded hardware block.

Major constant families in this chunk include:

- `MPCC_OGAM2_MPCC_OGAM_RAMB_REGION_6_7` through `MPCC_OGAM2_MPCC_OGAM_RAMB_REGION_32_33`, plus `MPCC_OGAM2_MPCC_GAMUT_REMAP_*` and `MPCC_OGAM2_MPC_GAMUT_REMAP_*`, covering the tail of MPCC output-gamma RAMB region descriptors and MPCC gamut remap matrix programming for coefficient banks A and B.
- `MPCC_OGAM3_MPCC_OGAM_*`, covering output gamma control, LUT index/data/control, RAMA/RAMB start, slope, base, end, offset, region descriptor, and gamut remap fields for MPCC instance 3.
- `MPC_OUT0_*` through `MPC_OUT3_*`, covering MPC output mux selection, rate/flow-control fields, denorm mode and RGB/YCbCr clamp fields, output CSC coefficient format, CSC mode, and paired 16-bit CSC matrix coefficients for banks A and B.
- `MPC_RMU_CONTROL` and `MPC_RMU_MEM_PWR_CTRL`, covering RMU enable and memory-power controls.
- `MPC_RMU0_*` and `MPC_RMU1_*`, covering shaper control, per-channel offset/scale, shaper LUT index/data/write-enable, RAMA/RAMB region descriptors, 3DLUT mode/index/data/read-write controls, 30-bit data packing, output normalization, and output offset/scale fields.
- `ABM0_BL1_PWM_*` and `ABM1_BL1_PWM_*`, covering ambient/user/target/current/final/minimum PWM levels, ABM enable and auto-update controls, backlight-update sample rate, group register locking, and frame-start update selection.
- `ABM0_DC_ABM1_*` and the beginning of `ABM1_DC_ABM1_*`, covering ABM enable/bypass, IPS color-space coefficient select, ACE slope/offset and threshold programming, HGLS read-progress status, histogram/luma-stat sampling controls, luma-stat counters, histogram bin shift/index registers, histogram result registers, and backlight master lock.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time token expansion:

1. DCN315 code includes `dcn_3_1_5_offset.h` and `dcn_3_1_5_sh_mask.h`.
2. Resource-table macros such as `SRII`, `SRII_MPC_RMU`, `MPC_REG_LIST_DCN3_0`, `MPC_OUT_MUX_REG_LIST_DCN3_0`, `MPC_RMU_REG_LIST_DCN3AG`, and ABM register-list macros resolve register addresses from the offset header.
3. Field-list macros paste register and field names into `__SHIFT` and `_MASK` symbols from this header to initialize per-block shift/mask tables.
4. Runtime code calls register helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_SET_3`, `REG_GET`, `REG_GET_2`, `REG_WAIT`, and direct `REG_WRITE`/`REG_READ`; those helpers use the populated masks and shifts to access hardware fields.

The declaration order mirrors hardware organization. MPCC OGAM and RMU blocks intentionally duplicate nearly identical field layouts per instance so instance-indexed resource tables can map each MPCC/RMU to the correct hardware symbols.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes bit locations for state in DCN 3.1.5 display registers.

Writable fields in this range can program MPCC output gamma and gamut remap state, MPC output routing and color conversion, RMU shaper and 3D LUT state, RMU memory power behavior, PWM backlight state, ABM enable/bypass, ACE curve parameters, histogram/luma-stat sampling cadence, and ABM lock/update behavior. These programmed values persist according to the underlying display block power and reset domains, and can be lost or reinitialized across modesets, display block reset, suspend/resume, GPU reset, or ASIC reset.

Hardware-updated fields expose current OGAM/gamut modes, MPC output status, RMU memory power state, ABM current/final levels, update-pending flags, read-progress flags, missed-frame flags, luma-stat observations, histogram results, and lock/update status. Access type, reset values, read-clear behavior, write-one-to-clear behavior, and required polling sequences are not encoded here.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.5 register offset header for MMIO addresses. The shift/mask header says how to pack fields; the offset header says where each register lives. Mixing this file with a different DCN generation is risky because many register and field names are structurally similar while addresses or bit layouts can diverge.

Primary integration points include:

- `display/dc/resource/dcn315/dcn315_resource.c`, which includes the DCN 3.1.5 offset and mask headers and constructs `mpc_regs`, `mpc_shift`, and `mpc_mask` using DCN3 MPC, output mux, and RMU register-list macros. The chunk's MPC/MPCC/RMU symbols feed `dcn30_mpc_construct()`.
- `display/dc/mpc/dcn30/dcn30_mpc.[ch]`, where MPCC OGAM fields are used to power OGAM LUT memory, select RAM A/B, load output gamma LUTs, read current OGAM state, and program gamut/output CSC state through register helpers.
- `display/dc/dce/dce_abm.[ch]` and `display/dc/dce/dmub_abm_lcd.c`, where ABM masks drive initialization of histogram/luma-stat sample rates, IPS coefficient selection, PWM levels, luma thresholds, missed-frame clear fields, and current/target backlight reads.
- DCN315 DMUB, IRQ, and GPIO code that includes the same generated header for their own generated register tables, even though most fields in this particular line range are consumed by MPC and ABM paths.
- Higher-level color-management and modeset paths that select MPCC OGAM, gamut remap, output CSC, shaper, and 3DLUT programming through the MPC abstraction rather than using these macros directly.

## Risks And Edge Cases

- The chunk starts mid-register. The shift definitions and earlier masks for `MPCC_OGAM2_MPCC_OGAM_RAMB_REGION_4_5` are in the previous chunk; this range only contains the last four masks for region 4/5.
- The chunk ends mid-register. `ABM1_DC_ABM1_HGLS_REG_READ_PROGRESS` has only six shift definitions here; its masks and any later clear/status fields continue in the next chunk.
- Several register families are copy-sensitive: MPCC OGAM2 versus OGAM3, MPC_OUT0-3, RMU0 versus RMU1, and ABM0 versus ABM1 have mostly repeated field layouts. A generator drift or copy error can compile while routing a field to the wrong hardware instance.
- Some runtime code uses only a subset of the generated region registers. For example, generic DCN3 MPC register lists name `MPCC_OGAM_RAMA_REGION_0_1` and `32_33` directly for PWL programming, while this chunk also exposes all intermediate region pairs. Whole-file analysis should avoid assuming every generated macro is actively used by the current driver.
- Control and status bits are often adjacent. Examples include OGAM current-mode fields near programmed-mode fields, RMU memory power control/status, ABM update-pending/readback/lock bits, and ABM missed-frame clear/status bits. Consumers must preserve unrelated bits and follow hardware sequencing that this header does not document.
- Full-width histogram and LUT data masks use `0xFFFFFFFFL`, while many packed coefficients use paired 16-bit fields. Incorrect signedness or width assumptions in consumers would not be caught by the header itself.
- ABM backlight fields are 17-bit PWM values, while some driver paths convert from or to user-facing brightness and BIOS scratch state. Mask errors here can produce visibly wrong brightness, stuck ramping, or stale current/target backlight reads.
- RMU shaper and 3DLUT programming is color-critical. Wrong offsets, segment counts, RAM bank selection, 30-bit packing, or output normalization fields can cause subtle color corruption that may only appear with nontrivial HDR/3D LUT workloads.

## Test Signals

Useful validation is mostly build-time consistency plus hardware integration:

- Build AMDGPU display code for a DCN315-enabled configuration to catch missing, renamed, or mismatched macros used by generated register-helper expansion.
- Mechanically verify that complete registers in this line range have matching `__SHIFT` and `_MASK` symbols for each field, while accounting for the partial first and last registers.
- Compare this slice against the authoritative DCN 3.1.5 register database and the matching offset header to ensure each `addressBlock`, register name, field name, shift, and mask aligns.
- Exercise MPCC output gamma and gamut remap programming across MPCC instances 2 and 3, including RAM A/B switching, bypass/current-mode reads, nontrivial PWL transfer functions, and gamut matrices in coefficient banks A and B.
- Exercise MPC output mux, denorm, and output CSC paths for all four MPC outputs, checking modeset, color conversion, and clamp behavior.
- Exercise RMU shaper and 3DLUT programming on RMU instances 0 and 1 with 1D shaper curves, 3D LUT writes/reads, 30-bit data mode, memory power transitions, and HDR/color-management workloads.
- Exercise ABM and backlight flows through both legacy DCE ABM and DMUB ABM paths: ABM initialization, PWM user/current/target/final levels, fractional PWM, sample-rate programming, luma thresholds, missed-frame clear, histogram/luma-stat reads, panel on/off, suspend/resume, and brightness ramping.
- Watch for stuck update-pending/read-progress bits, missed-frame flags, incorrect histogram bins, unexpected luma-stat values, RMU memory power wait failures, visible gamma/color artifacts, and backlight values outside the expected 17-bit hardware range.

## Open Cross-Chunk Notes

The merge lane should combine this chunk with the previous chunk to describe `MPCC_OGAM2_MPCC_OGAM_RAMB_REGION_4_5` completely. It should combine this chunk with the next chunk for the complete `ABM1_DC_ABM1_HGLS_REG_READ_PROGRESS` register and the remainder of ABM1. Whole-file analysis should reconcile this chunk with neighboring DCN 3.1.5 generated-header chunks before making final claims about the complete MPCC OGAM, MPC OCSC/RMU, and ABM register coverage of `dcn_3_1_5_sh_mask.h`.

### subset-b-001875: lines 25142-27729

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 25142-27729

## Purpose

This chunk is generated AMD DCN 3.1.5 register field metadata. It contains no executable C logic; it exposes preprocessor constants that describe bit positions and masks for fields in DCN display MMIO registers. Runtime code combines these `__SHIFT` and `_MASK` constants with the matching DCN 3.1.5 register-offset header to build field tables and read/modify/write hardware registers.

The requested range covers 2,588 source lines and 2,109 `#define` entries: 1,054 `__SHIFT` constants and 1,055 `_MASK` constants across 384 register names. The count is intentionally unbalanced because the artificial chunk boundaries cut through register definitions. The range starts inside `ABM1_DC_ABM1_HGLS_REG_READ_PROGRESS`, after some earlier shift definitions, and ends inside the `OTG0_OTG_CRC_CNTL` shift list before the remaining shifts and masks.

Although this file is under a local `ceph-client` source mirror, the content is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or exported runtime symbols in this range. The public surface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the hardware field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK`: the hardware field mask within the register.

These macros are meaningful only with the matching register offsets from `dcn_3_1_5_offset.h` and AMD display register helpers such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Major register families in this chunk:

- Tail of `ABM1_*`: histogram/readback, local statistics, ambient/backlight management sample-rate controls, histogram bins/results, missed-frame/read-progress bits, and BL master lock.
- Full repeated `ABM2_*` and `ABM3_*` blocks: PWM ambient/user/target/current/final/minimum duty-cycle fields, ABM PWM control/sample-rate/lock fields, ACE offset/slope and threshold fields, IPCSC coefficient selection, HGLS read progress, HG/LS statistics, histogram bin/result windows, and BL master lock.
- `DPG0` through `DPG3`: display pattern generator enable/mode/dynamic range/bit depth/resolution fields, ramp control, dimensions, color channels, segment offsets, and double-buffer pending status.
- `FMT0` through `FMT3`: formatter clamp ranges, dynamic expansion, pixel encoding/subsampling, truncation, spatial/temporal dithering, random seeds, clamp format, side-by-side stereo width, 4:2:0 memory power controls, and 4:2:2 edge handling.
- `OPPBUF0` through `OPPBUF3` and `OPP_PIPE0` through `OPP_PIPE3`: OPP buffer active width, segmentation, overlap, pixel repetition, 3D parameters, padded-pixel count, pipe clock enable/on status, and digital bypass.
- `OPP_PIPE_CRC0` through `OPP_PIPE_CRC3`: CRC enable/continuous/stereo/interlace/pixel-source controls, CRC masks, and CRC result registers.
- `DSCRM0` through `DSCRM2`: DSC remapper forwarding configuration for slice-width and buffer-memory format.
- OPP top-level and perfmon registers: clock-gating/test-clock fields, ABM BLPWM routing, performance counter event/control/state/interrupt/ack/value fields.
- `ODM0` through `ODM3`: OPTC input soft reset, underflow interrupt/status/clear fields, segment source selection, DSC data format and bytes-per-pixel, segment/slice width, input clock control, memory selection, and spare register fields.
- Beginning of `OTG0`: horizontal/vertical timing totals, blanks, syncs, dynamic refresh-rate total control/status, trigger A/B controls, force-count controls, flow control, stereo/interlace, pixel readback, timing status/counts, forced vsync, snapshot, update lock, double-buffer pending bits, master enable, vertical interrupt 0-2 controls, and the first five CRC control shifts.

## Control Flow

This header has no runtime control flow. The practical control flow is supplied by DCN315 display code that includes this generated mask header:

1. DCN315-specific files include both `dcn/dcn_3_1_5_offset.h` and `dcn/dcn_3_1_5_sh_mask.h`.
2. Token-pasting helper macros resolve register/field names into offset, mask, and shift constants. For example, `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` expand against generated names such as `OTG0_OTG_STATUS__OTG_V_BLANK_MASK`.
3. Higher-level display code performs the actual sequencing: programming ABM/PWM, configuring formatter and OPP state, enabling clocks, selecting ODM input segments, setting OTG timings, arming vertical interrupts, reading CRCs, and polling or clearing pending/status bits.

The masks do not encode access ordering, read-only/write-only semantics, sticky status behavior, or write-one-to-clear semantics. Consumers must follow hardware programming sequences from the display driver and ASIC specification.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk or in memory. It describes hardware register fields whose values live in the display engine.

Hardware state represented here includes:

- ABM/backlight state: ambient/user/target/current/final/minimum PWM levels, automatic ABM update/calculation controls, PWM update sample-rate counters, grouped register locks, ACE thresholds/slopes, HG/LS histogram and luma statistics, readback-in-progress flags, missed-frame flags, clear bits, and master locks.
- OPP/formatter state: pattern generator settings, clamp ranges, pixel encoding, chroma subsampling, bit-depth truncation and dithering controls, random seeds, 4:2:0 memory power state, OPP buffer segmentation and 3D parameters, OPP pipe clock/bypass state, and per-pipe CRC results.
- DSC/ODM state: DSC forwarding and remapping configuration, OPTC segment routing, DSC data format and bytes-per-pixel, segment/slice widths, input memory selection/status, input clock enable/on status, underflow occurrence/current/status bits, and double-buffer pending state.
- OTG0 state: timing totals and sync positions, dynamic vertical-total update status, trigger arm/delay/select state, force-count-now and flow-control state, stereo/interlace state, live pixel/timing counters, snapshot positions, update locks, timing double-buffer pending bits, master enable, vertical interrupt positions/status/clear bits, and the beginning of CRC configuration.
- Perfmon state: selected events, counter state, run-enable/stop selections, interrupt status/ack bits, and high/low counter values.

Persistence is hardware-defined. Configuration fields generally remain until a modeset, power-gating transition, suspend/resume restore, or ASIC reset changes them. Status, pending, interrupt, ack, clear, trigger, and missed-frame fields may be volatile, sticky, self-clearing, or write-one-to-clear depending on the register. This generated header only names the bit layout.

## Dependencies And Integration Points

Primary dependency:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`, which provides the companion register offsets and base-index information.

Observed include/integration sites in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c` includes the DCN 3.1.5 offset and mask headers and builds `dmub_srv_dcn315_regs` using `DMUB_DCN315_FIELDS()`, `FD_MASK`, and `FD_SHIFT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c` includes the generated headers for DCN315 interrupt source descriptors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c` and `hw_translate_dcn315.c` include the same generated headers for GPIO register translation/factory setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes the DCN 3.1.5 headers while constructing DCN315 display resources, including DIO and stream encoder resources.

Broader integration is with AMDGPU display programming paths for backlight/ABM, output pixel processing, formatter programming, ODM/OPTC routing, OTG timing, display interrupts, CRC diagnostics, and performance monitoring. Repeated instance prefixes (`ABM2`, `ABM3`, `FMT0`-`FMT3`, `OPPBUF0`-`OPPBUF3`, `ODM0`-`ODM3`, `OTG0`) must stay aligned with the matching offset header and register tables.

## Risks And Edge Cases

- Shift/mask drift is the main risk. These are untyped integer constants, so a wrong bit position can compile cleanly while corrupting adjacent hardware fields at runtime.
- This chunk starts and ends mid-register. Final file-level reconciliation must merge the previous chunk's `ABM1_DC_ABM1_HGLS_REG_READ_PROGRESS` opening definitions and the following chunk's remaining `OTG0_OTG_CRC_CNTL` definitions before making complete-register claims.
- ABM and PWM fields include lock bits, pending bits, missed-frame flags, clear bits, sample-rate counters, and automatic update controls. Incorrect read/modify/write handling can leave brightness updates stale, lose missed-frame diagnostics, or program backlight levels on the wrong frame.
- Formatter and OPP fields are replicated for four pipes. A copy-generation error in only one instance may appear as a one-display or one-plane artifact, especially with 4:2:0/4:2:2 formats, dithering, stereo, segmentation, or CRC validation.
- Memory power fields such as formatter map420 memory controls must be coordinated with active use; forcing low-power state during active scanout can produce stale data or visible corruption.
- ODM/OPTC fields govern DSC data format, segment routing, slice width, input clocks, and underflow signaling. Wrong values can produce underflow interrupts, blank output, bad DSC slicing, or failures limited to multi-segment/ODM modes.
- OTG timing fields are highly order-sensitive. Misprogrammed totals, blanking, sync, dynamic refresh-rate limits, double-buffer update timing, or master enable state can cause lost vblank, unstable refresh, frame timing glitches, or hangs during modeset.
- Vertical interrupt fields combine enable, status, clear, type, and line-position controls. Incorrect ack/clear behavior can create stuck interrupts or missed vblank-style notifications.
- Perfmon fields include run gating and interrupt/ack controls. They are useful for diagnostics but can perturb measurement or produce stale counts if counter state and ack fields are not sequenced correctly.

## Test Signals

Useful validation for this chunk combines generated-header consistency checks with hardware-level display tests:

- Build DCN315 AMDGPU display code. Missing or renamed macros should fail at include sites such as DMUB register table construction, IRQ descriptors, GPIO translation, resource construction, and any direct register helper use.
- Mechanically verify that complete registers in lines 25142-27729 have paired `__SHIFT` and `_MASK` definitions. Expected exceptions are the opening `ABM1_DC_ABM1_HGLS_REG_READ_PROGRESS` partial register and the closing `OTG0_OTG_CRC_CNTL` partial register.
- Diff this slice against AMD's authoritative DCN 3.1.5 generated register database and neighboring DCN generation headers where repeated block layouts should remain compatible.
- Exercise backlight and ABM paths: brightness changes, ambient/user/target levels, automatic current-level updates, sample-rate changes, frame-start updates, suspend/resume, and panel power transitions.
- Validate formatter and OPP behavior across RGB/YCbCr, 4:2:0, 4:2:2, bit-depth truncation/dithering, stereo, segmented output, and CRC capture modes; watch for pipe-specific artifacts.
- Test ODM/DSC scenarios, including single-segment and multi-segment modes, DSC on/off, slice-width changes, clock gating transitions, and underflow interrupt reporting/clearing.
- Exercise OTG0 timing paths: modesets, vblank and vertical interrupt handling, dynamic refresh-rate changes, interlace/stereo modes, forced vsync, snapshot capture, update locks, double-buffer pending polling, and CRC enable/one-shot modes.
- Monitor kernel logs and display diagnostics for underflow, stuck pending bits, missed-frame flags, stale CRCs, lost vertical interrupts, timing update timeouts, brightness anomalies, or failures isolated to one repeated OPP/ODM/ABM instance.

## Cross-Chunk Notes

The previous chunk owns the start of `ABM1_DC_ABM1_HGLS_REG_READ_PROGRESS`, including the earlier in-progress and missed-frame shift fields. This chunk contains the clear shifts and masks plus the remaining ABM1 HG/LS statistics and histogram results. The next chunk continues `OTG0_OTG_CRC_CNTL` after line 27729 with additional CRC shifts and the mask definitions, then likely continues the rest of the OTG0/OPTC timing metadata. The final per-file report should reconcile these boundaries before summarizing complete address blocks for `dcn_3_1_5_sh_mask.h`.

### subset-b-001876: lines 27730-30207

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 27730-30207

## Scope

This chunk covers lines 27730-30207 of the generated AMD DCN 3.1.5 shift/mask header. It is preprocessor-only register metadata: 2,138 `#define` entries across 2,478 source lines, plus generated register and `addressBlock` comments. There are no functions, structs, enums, variables, locks, allocations, or executable statements in this range.

The range starts partway through `OTG0_OTG_CRC_CNTL`, after the first five CRC control shifts are defined by the previous chunk, and continues through the tail of OTG0 output timing generator fields, all OTG1 fields, all OTG2 fields, and most of OTG3 fields. It ends partway through `OTG3_OTG_CRC_SIG_BLUE_CONTROL_MASK`, with the remaining shift/mask lines for that register and later OTG3 fields in the next chunk.

## Purpose

This header slice publishes exact bit positions and masks for DCN 3.1.5 OTG, or output timing generator, hardware registers. AMDGPU display code combines these macros with the matching DCN 3.1.5 offset header and register-helper macros to pack MMIO writes, decode MMIO reads, configure timing-generator behavior, and build IRQ/register tables without embedding raw bit numbers in driver logic.

The chunk is a generated hardware contract. Its correctness depends on each macro name and numeric value matching the ASIC register database for DCN 3.1.5. Runtime behavior is implemented by consumers such as OPTC and IRQ code; this file only supplies field layout.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within a 32-bit register value.
- `//<REGISTER>` comments group fields belonging to a logical register.
- `// addressBlock: ...` comments group per-instance OTG registers by decoded hardware block.

Major constant families in this chunk include:

- OTG CRC capture and readback fields for OTG0 through OTG3: `OTG_CRC_CNTL`, `OTG_CRC_CNTL2`, CRC window A/B start/end coordinates, CRC0/1/2/3 data readbacks, and CRC signal masks. These fields cover CRC enablement, continuous/one-shot behavior, capture-source selection, DSC/data-stream modes, window bounds, and 16-bit component results.
- Static-screen and stereo/3D fields: `OTG_STATIC_SCREEN_CONTROL`, `OTG_3D_STRUCTURE_CONTROL`, `OTG_STEREO_CONTROL`, `OTG_STEREO_STATUS`, and `OTG_STEREO_FORCE_NEXT_EYE`, covering static-screen detection, CPU interrupt status/clear bits, 3D structure enable/update/reset state, stereo eye selection, DP stereo-output controls, and current-eye/status bits.
- Global synchronization, update, and lock fields: `OTG_VSTARTUP_PARAM`, `OTG_VUPDATE_PARAM`, `OTG_VREADY_PARAM`, `OTG_GLOBAL_SYNC_STATUS`, `OTG_MASTER_UPDATE_LOCK`, `OTG_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_GLOBAL_CONTROL0` through `OTG_GLOBAL_CONTROL4`, `OTG_VUPDATE_KEEPOUT`, `OTG_TRIG_MANUAL_CONTROL`, and `OTG_MANUAL_FLOW_CONTROL`. These fields describe vstartup/vupdate/vready timing, interrupt enable/status/clear fields, master-update locks, pending double-buffer updates, global update lock windows, manual trigger/flow control, and keepout windows.
- Global swap lock and multi-OTG coordination fields: `OTG_GSL_CONTROL`, `OTG_GSL_WINDOW_X`, `OTG_GSL_WINDOW_Y`, and `OTG_GSL_VSYNC_GAP`, covering GSL enable/master mode, delay/check controls, master-update-lock integration, GSL window coordinates, and vsync gap detection/status/clear fields.
- Timing and variable-refresh fields: `OTG_H_TOTAL`, `OTG_H_BLANK_START_END`, `OTG_H_SYNC_A`, `OTG_H_SYNC_A_CNTL`, `OTG_H_TIMING_CNTL`, `OTG_V_TOTAL`, `OTG_V_TOTAL_MIN`, `OTG_V_TOTAL_MAX`, `OTG_V_TOTAL_MID`, `OTG_V_TOTAL_CONTROL`, `OTG_V_TOTAL_INT_STATUS`, `OTG_VSYNC_NOM_INT_STATUS`, `OTG_DRR_TIMING_INT_STATUS`, `OTG_DRR_V_TOTAL_REACH_RANGE`, `OTG_DRR_V_TOTAL_CHANGE`, `OTG_DRR_TRIGGER_WINDOW`, and `OTG_DRR_CONTROL`.
- Trigger, force-count, flow-control, and status fields: `OTG_TRIGA_CNTL`, `OTG_TRIGB_CNTL`, manual trigger registers, `OTG_FORCE_COUNT_NOW_CNTL`, `OTG_FLOW_CONTROL`, `OTG_CONTROL`, `OTG_INTERLACE_CONTROL`, `OTG_INTERLACE_STATUS`, pixel-data readback, `OTG_STATUS`, `OTG_STATUS_POSITION`, nominal/current counters, frame/VF/HV counters, count reset, manual force-vsync, and vertical sync control.
- Interrupt and pipe-update fields: `OTG_VERTICAL_INTERRUPT0/1/2_POSITION`, `OTG_VERTICAL_INTERRUPT0/1/2_CONTROL`, `OTG_PIPE_UPDATE_STATUS`, and `INTERRUPT_DEST`-related fields included near the per-instance OTG register blocks. These map line-triggered interrupt positions, enable/status/clear/type bits, and update-pending status fields used by IRQ and debug paths.
- DSC/output routing support fields: `OTG_DSC_START_POSITION`, `OTG_REQUEST_CONTROL`, `OTG_MASTER_EN`, `OTG_CLOCK_CONTROL`, `OTG_SPARE_REGISTER`, and output/control fields such as `OTG_OUT_MUX`, `OTG_MASTER_EN`, clock enable/on/gate-disable/busy, and soft reset.

The same logical layout is repeated by instance. OTG1 begins at the `dce_dc_optc_otg1_dispdec` address block, OTG2 begins at `dce_dc_optc_otg2_dispdec`, and OTG3 begins at `dce_dc_optc_otg3_dispdec`. OTG0 is already underway at the start of this chunk.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time token expansion:

1. DCN 3.1.5 display components include `dcn_3_1_5_sh_mask.h` and the matching offset header.
2. Register table macros such as `SRI(OTG_* , OTG, inst)` select instance-specific register addresses from the offset header.
3. Field macros such as `SF(OTG0_OTG_CRC_CNTL, OTG_CRC_EN, mask_sh)` resolve to the `__SHIFT` and `_MASK` values defined here.
4. Runtime helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and IRQ register descriptors use those resolved positions to perform MMIO writes, read-modify-write updates, polling, and field decoding.

The declaration order mirrors the hardware register map. OTG0 in this chunk covers CRC through spare/update state. OTG1 and OTG2 each present a full timing-generator instance from basic horizontal/vertical timing through CRC/static-screen/GSL/DRR/update fields. OTG3 starts with the same full timing, status, interrupt, and CRC layout, but this chunk stops before its static-screen and later fields are complete.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes bit locations for state held in DCN 3.1.5 display hardware registers.

Writable fields in this range can program timing totals and blank/sync ranges, vstartup/vupdate/vready positions, dynamic refresh bounds and trigger windows, CRC capture windows and modes, static-screen detection thresholds, GSL synchronization windows, master-update locking, double-buffer update behavior, stereo/3D behavior, flow-control sources, interrupt enables/types/clears, DSC start position, OTG clock enable/reset, and OTG master enablement.

Hardware-updated fields expose CRC result data, one-shot CRC pending state, static-screen status and interrupt status, 3D reset pending/count state, GSL gap status, global sync event/status fields, update-lock status, double-buffer pending bits, DRR timing events, force-count and forced-vsync events, flow-control input status, current master-enable state, interlace current/next field, pixel-data readback, live horizontal/vertical blank/active/sync state, counters, stereo current-eye/status, snapshot/update/pipe-update pending state, and vertical interrupt status bits.

Programmed values persist according to the underlying hardware power and reset domains. They may survive until rewritten, OTG clock/reset sequencing, display pipe reinitialization, suspend/resume restore, GPU reset, or ASIC reset. Status, pending, and counter fields can change asynchronously relative to the C code that includes this header.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.5 register offset header for register addresses. The shift/mask header identifies bit placement only; it does not say where a register is mapped.

Primary source consumers of this specific header include:

- `display/dmub/src/dmub_dcn315.c`, which includes the generated DCN 3.1.5 register metadata for DMUB-facing display support.
- `display/dc/irq/dcn315/irq_service_dcn315.c`, which uses generated OTG field names in IRQ descriptors for vupdate-no-lock, vblank/vstartup, and vertical-line interrupts.
- `display/dc/resource/dcn315/dcn315_resource.c`, which assembles DCN 3.1.5 resource/register tables.
- `display/dc/gpio/dcn315/hw_factory_dcn315.c` and `display/dc/gpio/dcn315/hw_translate_dcn315.c`, which share the generated register metadata for DCN 3.1.5 GPIO/display integration.

The OTG fields in this chunk align with the generic OPTC register abstractions in `display/dc/optc/dcn31/dcn31_optc.h` and related OPTC implementation files. Those files list OTG registers with `SRI`, list field masks/shifts with `SF`, and implement timing-generator operations such as enable/disable, update locks, DRR programming, CRC configuration/readback, state snapshots, and debug register-state reads.

Key integration areas are:

- Modeset and timing programming: horizontal/vertical totals, blanking, sync, interlace, master enable, clock control, and DSC start-position fields define the scanout timing that the rest of the pipe must match.
- Atomic update synchronization: vstartup/vupdate/vready, global update locks, master-update locks, double-buffer pending fields, keepout windows, and manual flow control coordinate when pending register changes become visible.
- Variable refresh and DRR: `OTG_V_TOTAL_*`, `OTG_DRR_*`, and `OTG_DOUBLE_BUFFER_CONTROL` fields support min/max/mid vtotal changes, trigger windows, timing interrupts, and last-used DRR vtotal readback.
- IRQ service: `OTG_GLOBAL_SYNC_STATUS` and `OTG_VERTICAL_INTERRUPT*` fields are used to enable, clear, and classify vblank/vstartup, vupdate-no-lock, and vertical-line interrupts.
- CRC and validation/debug: `OTG_CRC_*` fields configure CRC capture windows and modes, then expose component CRC results for display validation, debugfs-style CRC capture, and hardware diagnostics.
- Multi-pipe synchronization: GSL control/window/vsync-gap fields are used for synchronized updates across multiple OTGs, especially where master/slave timing generators must coordinate frame timing.
- Power and idle behavior: static-screen fields, clock control, and update-pending/status fields participate in idle detection, power-saving decisions, and safe sequencing around clock gating or reset.

The generated offset and shift/mask headers must come from the same DCN 3.1.5 register database. Mixing this file with a nearby ASIC generation is risky because OTG register names are highly similar while bit layouts, omitted fields, or instance counts can differ.

## Risks And Edge Cases

- The chunk starts mid-register. Lines 27725-27729 contain the first `OTG0_OTG_CRC_CNTL` shifts, but this work item begins at line 27730, so a chunk-only reader sees the rest of `OTG0_OTG_CRC_CNTL` without its earliest `OTG_CRC_EN`, dual-link, blank-only, and continuous-enable shift definitions.
- The chunk ends mid-register at `OTG3_OTG_CRC_SIG_BLUE_CONTROL_MASK__OTG_CRC_SIG_BLUE_MASK__SHIFT`. The companion control-mask shift and both masks continue after line 30207.
- Repeated per-OTG layouts are copy-sensitive. OTG1, OTG2, and OTG3 are largely identical, so generator drift or manual edits can leave one instance with a subtly wrong field while the others still look correct.
- Many registers mix control, status, clear, pending, and interrupt type bits in the same 32-bit word. Consumers must respect hardware access semantics that are not encoded by the mask file, especially write-one-to-clear and status/pending bits.
- Several fields use high-bit or wide masks such as `0xFFFF0000L`, `0x7FFF0000L`, `0xFF000000L`, and `0x80000000L`. Incorrect integer width handling or signed assumptions can corrupt adjacent fields or misread status.
- Timing and synchronization masks are hardware-sensitive. Bad shifts in vtotal, vupdate, GSL, DRR, or master-update-lock fields can produce missed flips, visible glitches, stuck pending bits, interrupt storms, or hangs waiting for an update/lock condition.
- CRC fields are validation-sensitive. Wrong CRC window, component, DSC, or data-stream masks can make CRC diagnostics misleading even when the display appears functional.
- Clock/reset and master-enable fields can affect live display output. Misprogramming `OTG_CLOCK_CONTROL`, `OTG_CONTROL`, or `OTG_MASTER_EN` may blank a pipe, leave `OTG_BUSY` stuck, or break disable/enable sequencing.

## Test Signals

Useful validation is mostly build-time consistency plus DCN 3.1.5 hardware integration:

- Build AMDGPU display code for a DCN 3.1.5-enabled configuration to catch missing or renamed symbols used by `SRI`, `SF`, `IRQ_REG_ENTRY`, and `REG_*` helper expansion.
- Mechanically verify that each complete register in this line range has matching `__SHIFT` and `_MASK` symbols for every field, while accounting for the partial `OTG0_OTG_CRC_CNTL` start and partial `OTG3_OTG_CRC_SIG_BLUE_CONTROL_MASK` end.
- Compare this slice against the authoritative DCN 3.1.5 register database and the matching offset header to ensure every per-instance OTG register comment maps to the intended address and every field has the intended bit layout.
- Exercise modeset, DP/eDP scanout, blank/unblank, suspend/resume, GPU reset recovery, and multi-display enable/disable paths on DCN 3.1.5 hardware while watching for timing-generator stuck states and unexpected blanking.
- Exercise atomic flips, cursor updates, vblank/vstartup interrupts, vupdate-no-lock interrupts, vertical-line interrupts, update locks, and pipe-update status readback.
- Exercise DRR/VRR paths using varying min/max/mid vtotal ranges, DRR trigger windows, and timing-update double-buffer modes; watch for stuck `OTG_DRR_*` events or incorrect last-used-vtotal readback.
- Exercise CRC capture with full-frame and windowed modes, DSC-related CRC modes, one-shot and continuous capture where supported, and compare stable reference patterns across OTG instances.
- Exercise multi-OTG synchronized updates/GSL where hardware and topology allow it, checking gap-detection status, master/slave update behavior, and absence of missed or delayed flips.
- Use debug state dumps that read `OTG_MASTER_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_DRR_*`, `OTG_GLOBAL_SYNC_STATUS`, `OTG_GSL_VSYNC_GAP`, `OTG_STATIC_SCREEN_CONTROL`, and CRC/status registers to confirm decoded fields match observed hardware behavior.

## Open Cross-Chunk Notes

The merge lane should combine this chunk with the previous chunk to describe `OTG0_OTG_CRC_CNTL` completely. It should combine this chunk with the next chunk to describe `OTG3_OTG_CRC_SIG_BLUE_CONTROL_MASK` and the remainder of OTG3 completely. Whole-file analysis should reconcile this chunk with neighboring DCN 3.1.5 generated-header chunks before making final claims about the complete set of OTG0-OTG3 registers exposed by `dcn_3_1_5_sh_mask.h`.

### subset-b-001877: lines 30208-32632

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h

Chunk: `subset-b-001877`
Covered source range: lines 30208-32632 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h`

## Purpose

This chunk is a generated AMD DCN 3.1.5 register-field mask header section. It contains C preprocessor constants for register bit positions and bit masks; it is not executable code and does not define functions, structs, storage, or runtime algorithms.

The requested range covers 2,425 source lines and 2,165 `#define` entries: 1,088 `__SHIFT` macros and 1,089 `_MASK` macros. It starts at the tail of the `OTG3_OTG_CRC_SIG_BLUE_CONTROL_MASK` register-family block, then covers the remainder of the `OTG3` timing-generator field surface, OPTC misc/memory-power fields, `DC_PERFMON17`, HPD0 through HPD4 hotplug-detect blocks, a complete DP0 transmitter field group, a complete DIG0 digital encoder/HDMI/TMDS field group, and the beginning of the DP1 transmitter field group through `DP1_DP_SEC_CNTL1`.

The chunk boundary matters. The first two macros in this range complete a register whose comment and first fields are in the previous chunk. The range ends in the middle of DP1 secondary-data-packet support: later `DP1_DP_SEC_FRAMING*`, DP1 audio, MSE/MST/MSO/DSC/ALPM/GSP, and subsequent display-output blocks are outside this work item.

## Important APIs, Types, And Macros

There are no callable APIs or data types here. The public interface is the generated macro contract used by AMD display register helpers:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask.
- The matching address/base-index constants live in `dcn_3_1_5_offset.h`; this file supplies only field layout.

Important macro families in this range include:

- `OTG3_OTG_*`: static-screen interrupt/status fields, 3D/stereo structure fields, GSL vsync-gap and GSL window controls, master update mode/lock/keepout fields, OTG clock/reset/busy fields, vstartup/vupdate/vready event fields, global sync interrupt/status/clear fields, manual trigger/flow controls, dynamic refresh-rate timing interrupts, vertical-total reach/change/trigger-window fields, constant-M DTO fields, DSC start position, pipe update status, and spare register bits.
- `DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`, `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS`: shared OPTC-side source-selection, clock, and output-data-merger memory-power controls.
- `DC_PERFMON17_*`: performance counter/event selection, run/active/interrupt controls, count-value configuration, state readback, and high/low counter registers for the DC perfmon17 block.
- `HPD0_DC_HPD_*` through `HPD4_DC_HPD_*`: hotplug interrupt status, delayed sense, HPD RX interrupt status/control, interrupt ack/mask/polarity/timer fields, HPD enable/connection timer, fast-training delay/select/enables, and connect/disconnect toggle-filter timers.
- `DP0_DP_*`: complete DisplayPort main-link field definitions for link status, pixel format, MSA colorimetry/misc/timing, DP configuration and lane count, video stream enable/deferred-disable/status, FIFO steering, video M/N timing, link framing, HBR2 eye/test patterns, VBID, video disable interrupts, DPHY training/symbol/scrambler/PRBS/CRC/FEC controls, fast training, secondary-data packet controls, audio N/M and timestamp fields, MSE stream-allocation-table programming/status, MSA timing parameters, MSO, DSC, metadata transmission, ALPM, GSP8-GSP11, and GSP enable double-buffer status.
- `DIG0_*`: digital encoder frontend/backend control, output CRC, clock/test/random pattern generation, FIFO status/recalibration/error fields, HDMI metadata and core control/status, HDMI audio/ACR/VBI/infoframe/generic packet controls, generic-control packets, HDMI double-buffering, AFMT audio clock control, TMDS controls, stereo sync, sync character patterns, DC balancing, DIG version, and force-disable.
- `DP1_DP_*`: the beginning of the second DisplayPort main-link instance with the same generated shape as DP0, but only through `DP1_DP_SEC_CNTL1` in this chunk.

## Control Flow

This header has no internal control flow. All behavior occurs in code that includes the generated masks and shifts and passes them to register access helpers.

The runtime pattern is:

1. DCN315 display code includes `dcn_3_1_5_offset.h` and `dcn_3_1_5_sh_mask.h`.
2. Register-list macros choose addresses from the offset header.
3. Mask/shift-list macros choose field definitions from this header.
4. Block constructors store those addresses, masks, and shifts in per-block register tables.
5. Runtime display code uses helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, field extractors, and polling helpers to perform MMIO read/modify/write operations.

Concrete consumers in this tree include `display/dc/resource/dcn315/dcn315_resource.c`, `display/dc/irq/dcn315/irq_service_dcn315.c`, `display/dc/gpio/dcn315/hw_factory_dcn315.c`, `display/dc/gpio/dcn315/hw_translate_dcn315.c`, and `display/dmub/src/dmub_dcn315.c`. `dcn315_resource.c` builds DCN315 resource tables and uses generated field-list expansion for hardware sequencer and DIO-related fields. `irq_service_dcn315.c` builds HPD, HPD RX, pflip, GPIO, and underflow IRQ source tables. The generic IRQ code reads HPD sense/status fields and writes HPD interrupt polarity/ack fields using these generated definitions. DMUB support includes the same ASIC-specific mask namespace for firmware-facing register definitions.

## State And Persistence Behavior

The header itself is stateless. It performs no I/O, allocates no memory, and persists only as constants compiled into display-driver objects.

The hardware fields described here are persistent register state in the DCN display hardware until changed by driver writes, firmware writes, block reset, display power gating, ASIC reset, suspend/resume restore, or link/modeset reprogramming. Important state categories include:

- OTG3 timing and update state: static-screen status/interrupts, 3D/stereo counters, global sync event latches, vstartup/vupdate/vready interrupt state, master update lock, GSL status, DRR/VRR vertical-total programming, constant-M DTO phase/module values, DSC start coordinates, and pipe update status.
- Shared OPTC/ODM state: DWB/GSL source routing, OPTC clock enable/reset/busy status, ODM memory power control requests, and memory power status.
- Perfmon17 state: selected performance events, run/active mode, interrupt/latch behavior, counter state, and high/low counter readbacks.
- HPD state: current and delayed hotplug sense, HPD and HPD RX interrupt latches, ack/mask/polarity fields, debounce/toggle filter timers, and fast-training delay controls.
- DP0/DP1 link state: link training/status, pixel/MSA attributes, stream enable/deferred-disable, DPHY training and test-pattern state, scrambler/FEC/PRBS/CRC state, fast-training state, MST/MSE scheduling, MSO/DSC controls, ALPM controls, and secondary-packet/audio/metadata/GSP state.
- DIG0 HDMI/TMDS state: encoder enable/routing, output CRC/test pattern state, FIFO status, HDMI packet scheduling, audio/ACR timing, infoframe/generic-packet double buffering, deep-color/scrambling controls, AFMT audio source, and TMDS balancing/control-character state.

Several fields are status or write-one-clear/ack style rather than plain configuration. Examples include HPD interrupt acks, DP video stream-disable ack/status, DPHY CRC result-valid/status, fast-training complete ack, HDMI error ack/status, generic-packet pending/deadline status, MSE SAT update/status, and OTG global-sync/static-screen event clear fields. The generated macros do not encode access type or ordering; the calling driver sequences must do that correctly.

## Dependencies And Integration Points

Direct dependencies are small:

- the C preprocessor;
- the matching generated address header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`;
- AMD display register helper conventions such as `SF`, `SR`, `SRI`, `SRII`, `HWS_SF`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `get_reg_field_value`, and `set_reg_field_value`.

Functional integration is broader:

- OPTC and hardware sequencer paths depend on the `OTG3`, OPTC clock, GSL, DWB, ODM memory-power, and pipe-update fields for modeset timing, atomic-update synchronization, dynamic refresh-rate behavior, pipe status, and power management.
- IRQ service and GPIO/HPD translation paths depend on the `HPD0` through `HPD4` fields for connector hotplug, HPD RX, polarity inversion after ack, and debounce/filter behavior.
- DP link and stream encoder paths depend on the `DP0` and `DP1` fields for DisplayPort SST/MST link training, MSA/VBID programming, stream enable/disable, link compliance patterns, FEC/scrambler/CRC, DSC/MSO, secondary packets, audio timing, ALPM, and generic packet double buffering.
- DIG/HDMI/TMDS paths depend on `DIG0` fields for HDMI mode setup, packet scheduling, ACR/audio clocking, deep color, scrambling, TMDS control symbols, test patterns, output CRC, and force-disable behavior.
- DMUB code includes this mask header alongside offset definitions so DCN315 firmware-service register structures can share the same ASIC-specific field layout.

Instance prefixes are part of the ABI between generated headers and register-list macros. `OTG3`, `HPD0`-`HPD4`, `DP0`, `DIG0`, and `DP1` must remain aligned with the matching offset-header instances and the resource pool's declared hardware counts.

## Risks And Edge Cases

The primary risk is silent register-field drift. A wrong shift or mask can still compile and can make register helpers modify the wrong bits. High-impact examples in this chunk include OTG3 update locks and DRR timing, HPD interrupt ack/polarity, DP stream enable and DPHY training fields, DSC/MSO controls, HDMI packet controls, and ODM memory-power fields.

Chunk boundaries split logical blocks. The first lines complete `OTG3_OTG_CRC_SIG_BLUE_CONTROL_MASK` from the previous chunk, and the DP1 block continues after this chunk. Merge/reconciliation must avoid treating this slice as complete coverage for the OTG3 CRC-signal mask register or for DP1.

Repeated instance families are easy to miswire. HPD0-HPD4, DP0/DP1, and DIG0 share similar field names with different prefixes. A token-paste or table-index mistake can send hotplug handling, link training, packet programming, or HDMI controls to the wrong connector or encoder.

Status/ack/clear fields require access-type discipline. Treating latches, acks, reset-done bits, event-clear bits, or readback fields as ordinary configuration can drop HPD events, fail to clear interrupts, race fast-training completion, or misreport CRC/FIFO/MSE state.

DisplayPort and HDMI behavior is mode-sensitive. Some fields are only exercised with MST, DSC, MSO, FEC, high bit rates, deep color, audio, generic secondary packets, panel replay/ALPM, or compliance patterns, so field-layout errors may escape basic single-monitor modeset tests.

Generated macro consumers rely on exact names. Renaming or removing a field can break compile-time table initialization; worse, a same-shaped field with a different instance prefix can compile if selected accidentally by a macro expansion pattern.

## Test Signals

Useful validation signals are mostly build-time and hardware-facing:

- Build DCN315 display code with `dcn315_resource.c`, `irq_service_dcn315.c`, GPIO HPD translation/factory code, DMUB DCN315 support, stream/link encoder code, and OPTC/HWSEQ paths enabled. Missing or renamed macros should fail at compile time.
- Compare `dcn_3_1_5_sh_mask.h` against `dcn_3_1_5_offset.h` and adjacent generated ASIC versions for expected register names, instance counts, and field-layout continuity at chunk boundaries.
- Exercise OTG3 modesets and atomic updates: timing totals, vstartup/vupdate/vready interrupts, master update lock, GSL/global-sync behavior, DRR/VRR vertical-total changes, DSC start position, pipe update status, static-screen events, and CRC readbacks.
- Validate HPD0 through HPD4 with connect/disconnect and HPD RX events, checking debounce/toggle filtering, delayed sense, ack, polarity updates, interrupt masking, and absence of interrupt storms.
- Run DP0 and DP1 link tests where routed: SST/MST modes, multiple link rates/lane counts, FEC, scrambler, PRBS/compliance patterns, DPHY CRC, fast training, stream enable/deferred-disable, MSA/VBID programming, DSC/MSO, ALPM, and GSP/secondary-packet scheduling.
- Exercise DIG0 HDMI/TMDS paths: HDMI enable/status, deep color, scrambling, audio/ACR packet timing, VBI/infoframe/generic packet scheduling, double-buffer updates, AFMT audio clocking, TMDS control symbols, FIFO status, output CRC, and force-disable.
- Check suspend/resume and power-gating restoration for OTG3, OPTC/ODM memory-power state, HPD filters, DP/DIG stream state, and HDMI/DP packet-generation state.
- Use perfmon17 smoke tests by selecting known display events, starting/stopping the counter, reading high/low values, and checking interrupt/active/state fields behave consistently.

## Notes For Final Merge

Merge this chunk with adjacent chunks for the same source file before producing the final per-file report. The previous chunk owns the beginning of `OTG3_OTG_CRC_SIG_BLUE_CONTROL_MASK`; this chunk owns the remainder of OTG3, shared OPTC/perfmon/HPD blocks, complete DP0 and DIG0 blocks, and the start of DP1; the next chunk owns the rest of DP1 and later DIO blocks. The final file-level document should describe the full header as generated DCN315 register-field metadata rather than as handwritten runtime logic.

### subset-b-001878: lines 32633-35011

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 32633-35011

## Scope And Purpose

This chunk is part of the generated AMD DCN 3.1.5 register shift/mask header. It exports preprocessor constants that describe bit positions and masks for display-controller MMIO registers. The companion `dcn_3_1_5_offset.h` header supplies the register addresses; this file supplies field layout so AMDGPU display helpers can pack writes and decode reads through `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, `FD_MASK`, and `FD_SHIFT`.

The range starts in the middle of the `DP1_DP_SEC_CNTL1` field definitions, covers the remaining DP1 secondary-data, MST/MSE, DPHY, MSA, MSO, DSC, ALPM, and GSP field definitions, then enters `dce_dc_dio_dig1_dispdec` for DIG1 HDMI/TMDS stream-encoder fields. It continues into complete DP2 field groups and the beginning of DIG2 HDMI/TMDS fields, ending at `DIG2_HDMI_GC__HDMI_PACKING_PHASE_MASK`. The final `HDMI_PACKING_PHASE_OVERRIDE_MASK` for `DIG2_HDMI_GC` is outside this chunk.

There are no functions, structs, enums, variables, includes, branches, loops, allocations, locks, or direct side effects here. The exported interface is generated macro metadata:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask.
- `//<REGISTER>` comments delimit logical registers.
- `// addressBlock: ...` comments delimit generated hardware blocks.

Runtime behavior is created by the DCN315 display code that combines these symbols with register offsets and register helper macros. A wrong numeric value can compile but program or read the wrong hardware bits.

## Register Blocks Covered

The first partial section is the tail of `DP1_DP_SEC_CNTL1`. It contains GSP0 send, pending, missed-deadline, any-line, GSP1-7 line-reference, and GSP0 line-number masks. The corresponding shifts and earlier `DP_SEC_CNTL1` fields are in the previous chunk.

The DP1 secondary-data and audio groups include `DP1_DP_SEC_FRAMING1` through `DP1_DP_SEC_FRAMING4`, `DP1_DP_SEC_AUD_N`, `DP1_DP_SEC_AUD_M`, their readback registers, `DP1_DP_SEC_TIMESTAMP`, and `DP1_DP_SEC_PACKET_CNTL`. These fields control secondary-data packet frame/start positions, vblank/hblank/idle transmit widths, SST SDP splitting, collision/audio-mute status, DP audio N/M values, timestamp mode, and ASP coding/priority/version/channel-count override.

The DP1 MST/MSE groups include `DP1_DP_MSE_RATE_CNTL`, `DP1_DP_MSE_RATE_UPDATE`, `DP1_DP_MSE_SAT0` through `SAT2`, `DP1_DP_MSE_SAT_UPDATE`, `DP1_DP_MSE_LINK_TIMING`, `DP1_DP_MSE_MISC_CNTL`, and matching `SAT*_STATUS` registers. They define MSE X/Y rate fields, update-pending state, slot allocation table entries for sources 0-5, encryption flags/types, slot counts, link frame/line timing, timestamp/blank-code controls, and status readbacks.

The DP1 physical/link-diagnostic groups include `DP1_DP_DPHY_BS_SR_SWAP_CNTL` and `DP1_DP_DPHY_HBR2_PATTERN_CONTROL`. These fields expose bitstream/symbol-realignment swap load/count/done state and HBR2 pattern selection.

The DP1 MSA and stream-output groups include `DP1_DP_MSA_TIMING_PARAM1` through `PARAM4`, `DP1_DP_MSO_CNTL`, `DP1_DP_MSO_CNTL1`, `DP1_DP_DSC_CNTL`, `DP1_DP_DB_CNTL`, `DP1_DP_MSA_VBID_MISC`, `DP1_DP_SEC_METADATA_TRANSMISSION`, `DP1_DP_DSC_BYTES_PER_PIXEL`, and `DP1_DP_ALPM_CNTL`. These fields describe DP main-stream timing totals/starts/sync widths/polarities/active size, multi-stream output selection and pixel overlap, DSC mode, double-buffer disable, VBID6 scheduling, metadata packet enable/line scheduling, DSC bytes-per-pixel, and ALPM capability/status/enable.

The extended DP1 generic sideband packet groups include `DP1_DP_SEC_CNTL2` through `CNTL7`, `DP1_DP_GSP8_CNTL` through `GSP11_CNTL`, and `DP1_DP_GSP_EN_DB_STATUS`. They define send, pending, deadline-missed, any-line, line-reference, line-number, and PPS-related fields for GSP4 through GSP11, plus double-buffer status for GSP enable bits.

The `dce_dc_dio_dig1_dispdec` block covers DIG1 stream-encoder fields. It includes front-end control, output CRC control/result, clock/test/random patterns, FIFO status, HDMI metadata/control/status, HDMI audio/ACR/VBI/infoframe/generic-packet controls, HDMI GC, HDMI DB control, ACR N/CTS programming/status for 32/44/48 kHz families, AFMT top control, backend enable/control, TMDS control characters, TMDS feedback/stereo/sync/DC-balance/control-bit generators, DIG version, and force-disable fields.

The `dce_dc_dio_dp2_dispdec` block repeats the DP transmitter layout for DP2. It starts at `DP2_DP_LINK_CNTL` and covers link control, pixel format, MSA colorimetry/config/misc/timing, stream enable/status, steering FIFO, video timing/N/M, link framing, DPHY internal/training/symbol/8b10b/PRBS/scrambler/CRC/fast-training controls, secondary-data/audio metadata controls, MSE/SAT status, MSO, DSC, double buffering, ALPM, GSP8-11, and GSP enable double-buffer status.

The final `dce_dc_dio_dig2_dispdec` block begins DIG2 stream-encoder fields. It covers DIG2 front-end, output CRC, pattern/FIFO, HDMI metadata/control/status, audio/ACR/VBI/infoframe controls, HDMI generic packet send/continuous/line-reference/update-lock fields for packet slots 0-14, immediate-send/pending fields for those slots, and most of `DIG2_HDMI_GC`.

## Important APIs, Types, And Constants

This file does not define callable APIs or C types. Its API is the macro naming contract consumed by generated register-list code.

`display/dc/resource/dcn315/dcn315_resource.c` is the main display consumer for this ASIC family. It includes `dcn/dcn_3_1_5_offset.h` and `dcn/dcn_3_1_5_sh_mask.h`, defines `SR`, `SRI`, `FD_MASK`, and `FD_SHIFT` expansion helpers, and builds static register/field tables. In this chunk, the most relevant tables are `stream_enc_regs[]`, `se_shift`, and `se_mask`, which are passed to `dcn30_dio_stream_encoder_construct()` by `dcn315_stream_encoder_create()`.

The stream-encoder register-list interface is inherited from the DCN314/DCN30 stream encoder family. `display/dc/dio/dcn314/dcn314_dio_stream_encoder.h` maps logical stream-encoder fields to generated macro names such as `DPx_DP_MSA_TIMING_PARAM*`, `DPx_DP_MSE_RATE_CNTL`, `DPx_DP_MSE_RATE_UPDATE`, `DPx_DP_SEC_CNTL*`, `DPx_DP_SEC_METADATA_TRANSMISSION`, `DPx_DP_SEC_FRAMING4`, `DPx_DP_GSP11_CNTL`, `DIGx_HDMI_GC`, `DIGx_HDMI_GENERIC_PACKET_CONTROL*`, `DIGx_HDMI_ACR_*`, and `DMEx_DME_CONTROL`. The generic field table often names instance 0 fields, while instance-specific addresses come from per-instance offset tables.

`display/dc/dio/dcn30/dcn30_dio_stream_encoder.c`, `display/dc/dio/dcn314/dcn314_dio_stream_encoder.c`, `display/dc/dio/dcn20/dcn20_stream_encoder.c`, and older `dcn10_stream_encoder.c` contain the runtime operations that use these field definitions. Examples include programming MSA timing, waiting for `DP_MSE_RATE_UPDATE_PENDING`, configuring DSC PPS sideband packet `GSP11`, reading DP metadata packet scheduling, toggling HDMI AVMUTE through `HDMI_GC_AVMUTE`, controlling generic HDMI packets, and setting `DP_SST_SDP_SPLITTING`.

`display/dmub/src/dmub_dcn315.c` includes the same generated headers and builds `dmub_srv_dcn315_regs` with `REG_OFFSET_EXP()` and `DMUB_DCN315_FIELDS()`. This chunk's DP/DIG fields are not the primary DMUB field list, but they live in the same generated DCN315 namespace and must stay synchronized with the offsets used by DMUB-visible register access.

`display/dc/irq/dcn315/irq_service_dcn315.c` also includes the generated DCN315 headers for interrupt source registration. IRQ tables that touch DIO/DIG/DP state rely on this register field namespace matching the silicon layout.

`display/dc/gpio/dcn315/hw_translate_dcn315.c` and `display/dc/gpio/dcn315/hw_factory_dcn315.c` include these headers for GPIO/DDC/AUX/HPD translation and object construction. They are not the direct consumers of the DP1/DP2/DIG1/DIG2 stream fields in this chunk, but they share the same generated DCN315 register contract.

## Control Flow And Runtime Use

This header has no runtime control flow. Its effective flow is compile-time token expansion:

1. DCN315 display code includes the generated offset and sh/mask headers.
2. Register-list macros paste a register token, field token, and instance token into symbols from this file.
3. Constructors bind generated offsets and field tables into hardware block objects.
4. Runtime stream-encoder, link, audio, metadata, DSC, and diagnostics code uses helper macros to read, write, update, or poll the mapped registers.

For DP MSA programming, runtime code writes fields in `DP_MSA_TIMING_PARAM1` through `PARAM4` to describe totals, starts, sync widths, polarities, and active width/height. For MST/MSE, it writes rate fields and then observes update-pending state. For secondary data, it toggles GSP send/enable/line-number fields and packet scheduling bits. For HDMI, it uses `HDMI_CONTROL`, `HDMI_GC`, VBI/infoframe/generic packet controls, ACR fields, and audio packet fields to send HDMI metadata and audio.

The order in the file mirrors generated hardware organization, not execution order. Ordering-sensitive behavior is defined by the consumers and hardware programming manuals, not by this header.

## State And Persistence Behavior

The header stores no software state and persists no data. It describes bit locations for hardware state held in DP1, DP2, DIG1, and DIG2 registers.

Writable state described here includes DP secondary-data packet scheduling, audio N/M and timestamp mode, MSE rate and SAT slot allocation, MSA timing, MSO routing/overlap, DSC mode and bytes-per-pixel, metadata packet scheduling, ALPM controls, DPHY test/training fields, HDMI packet generation, HDMI AVMUTE/default/packing phase, HDMI ACR N/CTS programming, TMDS control patterns, and DIG frontend/backend enables.

Hardware-updated state described here includes send-pending and deadline-missed flags, collision and audio-mute status, MSE/SAT status readbacks, swap-done flags, stream/FIFO/CRC status, fast-training and DPHY CRC/status fields, ALPM status, GSP enable double-buffer status, HDMI status, ACR status, output CRC results, and DIG version/disable state.

Programmed values persist according to the underlying display power/reset domains. They can survive until rewritten, link or stream reinitialization, display block reset, power-gating, suspend/resume restore, GPU reset, or firmware/hardware sequencing. Status bits can change asynchronously relative to CPU code and may have write-one-to-clear, read-clear, pending, or latch semantics not encoded in this generated header.

## Dependencies And Integration Points

This chunk depends on `dcn_3_1_5_offset.h` for register addresses. Shift/mask values alone are insufficient; consumers need the matching offset header from the same register database. Mixing DCN 3.1.5 shifts with DCN 3.1.4, DCN 3.1.6, or generic DCN31 offsets is risky because many register and field names are structurally similar while positions or availability can differ.

The primary integration point is stream encoder construction in `dcn315_resource.c`. `stream_enc_regs[]` supplies instance-specific DP/DIG/DME addresses, while `se_shift` and `se_mask` supply fields like MSA timing, MSE rate, secondary-data controls, HDMI GC, generic packet controls, DSC/metadata fields, and FIFO controls. The constructed `dcn10_stream_encoder` then serves higher-level modeset, audio, infoframe, metadata, and DSC operations.

DisplayPort output integrates multiple register groups from this chunk. A DP stream can involve MSA timing, pixel format, video stream enable, DPHY training/CRC/status, secondary-data audio/metadata packets, MSE/MST slot allocation, DSC fields, ALPM, and GSP double-buffer status. Correct operation depends on the DP instance number in the offset table matching the logical engine selected by resource construction.

HDMI/TMDS output integrates DIG fields from this chunk with AFMT and VPG/DME blocks outside or adjacent to the range. The HDMI packet controls in DIG1/DIG2 schedule audio infoframes, MPEG/ACP/ISRC/null/GC packets, generic packet slots 0-14, and immediate sends. Audio clock regeneration depends on ACR control and N/CTS fields.

DSC and metadata paths depend on `DP_DSC_CNTL`, `DP_DSC_BYTES_PER_PIXEL`, `DP_SEC_METADATA_TRANSMISSION`, `DP_GSP11_CNTL`, and related GSP line-number/enable fields. Higher-level DSC mode validation and Display Mode Library logic decide whether compressed transport is used; these field definitions are the hardware packing layer for stream-encoder programming.

IRQ, DMUB, GPIO, and diagnostic code share the same generated DCN315 namespace. Even if they do not directly use every DP/DIG field in this slice, register database drift can surface across resource construction, firmware service access, interrupt registration, connector detection, and debug register dumps.

## Risks And Edge Cases

The chunk begins and ends mid-register. It starts after the shifts and early masks for `DP1_DP_SEC_CNTL1`; only the final GSP masks are present here. It ends before the final `DIG2_HDMI_GC__HDMI_PACKING_PHASE_OVERRIDE_MASK`. The merge lane must combine neighboring chunks before making complete-register claims for those registers.

Repeated instance layouts are copy-sensitive. DP1 and DP2, and DIG1 and DIG2, largely duplicate field names with only the instance prefix changed. A generator or merge error can leave a field present for one instance but wrong for the next, and reviews may miss it because the blocks are visually repetitive.

Wrong shifts or masks in this file can compile cleanly. If macro names still exist, the driver may write a plausible 32-bit value with a wrong field position. Likely symptoms include broken DP link training, MST slot allocation errors, invalid MSA timing, incorrect DSC packetization, missing HDR/metadata packets, stuck GSP pending bits, HDMI audio or infoframe failures, or misleading CRC/status diagnostics.

Packed high-bit fields are particularly sensitive. Examples include line-number fields using upper 16 bits, MSE rate X/Y splits, MSA timing packed into low/high 16-bit halves, sync polarity high bits, and generic packet controls that pack four per-slot bits across the whole register.

Status and command fields sit close together. For example, send bits are adjacent to pending/deadline-missed bits, collision status is adjacent to collision ACK, immediate-send fields are adjacent to immediate-send-pending fields, and enable fields are adjacent to double-buffer status. Blind read-modify-write operations must respect hardware access rules that are not documented in this header.

Generic sideband packet slots are easy to misindex. DP GSP4-11 fields and HDMI generic packet slots 0-14 are represented through repeated bit layouts. Off-by-one slot selection can route PPS, metadata, audio, ISRC/MPEG, or vendor packets to the wrong hardware packet slot.

DSC state is cross-field dependent. `DP_DSC_CNTL`, `DP_DSC_BYTES_PER_PIXEL`, GSP11 PPS scheduling, MSA/VBID fields, and secondary-data timing must be coherent with the selected stream timing and link bandwidth. Bad field metadata may show up as sink corruption rather than an obvious kernel failure.

ALPM, DPHY, CRC, and fast-training fields describe live link state. Tests that read these fields must account for asynchronous hardware updates, stale diagnostic state, and power-management transitions.

## Test Signals

Build-time coverage should catch missing or renamed macros in DCN315 builds that compile `dcn315_resource.c`, `dcn314_dio_stream_encoder.h`, `dcn30_dio_stream_encoder.c`, `dcn20_stream_encoder.c`, `dmub_dcn315.c`, `irq_service_dcn315.c`, and DCN315 GPIO translation/factory code. A successful build does not prove numeric correctness, but missing field macros fail early.

A mechanical consistency check should verify that complete registers in this line range have matching `__SHIFT` and `_MASK` definitions for each field, while excluding the partial first and last registers. It should also compare DP1 versus DP2 and DIG1 versus DIG2 repeated fields for expected structural equivalence.

DisplayPort validation should exercise DCN315 DP1/DP2-capable routes across multiple modes, lane counts, link rates, MST/MSE allocations, DSC-required modes, HDR/static metadata, audio packets, ALPM transitions, suspend/resume, hotplug, and link retraining. Useful signals are stable modesets, no AUX or training timeouts, correct DPCD/EDID reads, no unexpected CRC/training/status errors, and no stuck MSE/GSP update-pending bits.

HDMI/TMDS validation should exercise DIG1/DIG2 routes with audio, AVMUTE transitions, ACR programming, infoframes, generic packet slots, immediate packet sends, VBI packets, deep color, DVI/TMDS fallback, output CRC, and hotplug/resume. Good signals are correct sink-reported infoframes, stable audio/channel status, expected ACR values, no FIFO/status anomalies, and clean packet analyzer captures.

Metadata and DSC validation should cover dynamic metadata enable/disable, DP metadata packet line scheduling, HDMI metadata packets, GSP11 PPS enable/line selection, DSC bytes-per-pixel programming, DSC compressed modes, and mode changes between DSC and non-DSC streams. Signals include correct PPS/metadata captures, successful high-bandwidth modesets, no corrupted compressed output, and sane status readbacks.

Diagnostic validation should cover output CRC, DPHY CRC, MSE SAT status, fast-training status, ALPM status, HDMI status, ACR status, and generic packet pending bits. Tests should clear or initialize diagnostic state before reading it so stale status does not hide field-layout errors.

## Open Cross-Chunk Notes

The previous chunk is needed to describe `DP1_DP_SEC_CNTL1` completely. This chunk only contains the final masks for that register. The next chunk is needed to complete `DIG2_HDMI_GC`, because this range ends after `DIG2_HDMI_GC__HDMI_PACKING_PHASE_MASK` and before the override mask. Whole-file research should also reconcile this slice with adjacent DCN315 sh/mask chunks that contain the offset-matched DP0, DIG0, later DIG2, AFMT, AUX, DCIO, DIO, PWRSEQ, and DSC blocks.

### subset-b-001879: lines 35012-37422

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 35012-37422

## Scope

This chunk is part of AMDGPU DCN 3.1.5 generated register metadata. It contains C preprocessor constants for register field shifts and masks, not executable code. The exact chunk spans line 35012 through line 37422 of `dcn_3_1_5_sh_mask.h`; line 35012 starts mid-register with the `DIG2_HDMI_GC__HDMI_PACKING_PHASE_OVERRIDE_MASK` constant, and line 37422 ends mid-register inside `DP4_DP_SEC_METADATA_TRANSMISSION`.

The definitions are consumed by AMD display driver register access helpers that combine an address header with these `__SHIFT` and `_MASK` constants to read, write, and update individual DCN register fields. The values are hardware ABI: they encode bit positions in the DCN display I/O, HDMI/TMDS, DisplayPort, secondary packet, MST/MSE, DSC, CRC, and double-buffer control registers.

## Purpose

The purpose of this chunk is to expose bitfield layout for several display encoder instances:

- Tail of the `DIG2` HDMI/TMDS back-end block, including HDMI generic packet line selection, HDMI double-buffer status/control, HDMI audio clock regeneration values, AFMT audio clock gating, DIG back-end enable/source selection, TMDS control-symbol generation, sync patterns, and forced DIG disable.
- Complete `DP3` DisplayPort register field set for the `dce_dc_dio_dp3_dispdec` address block, covering link control, pixel/MSA/video timing, DPHY training and test controls, secondary data packets, MST stream allocation, DSC, ALPM, GSP8-GSP11, and double-buffer status.
- Complete `DIG3` front-end/back-end HDMI/TMDS register field set for the `dce_dc_dio_dig3_dispdec` address block, covering DIG front-end control, output CRC/test pattern/FIFO status, HDMI metadata/control/status, generic packet scheduling, TMDS generation, and back-end enable/source selection.
- Start-to-tail `DP4` DisplayPort register field set for the `dce_dc_dio_dp4_dispdec` address block through the first three fields of `DP4_DP_SEC_METADATA_TRANSMISSION`.

These constants let common DC code address replicated hardware pipes by selecting a register block (`DIG2`, `DIG3`, `DP3`, `DP4`) while using stable field names for the operations.

## Important Definitions

The public surface is macro-only. Every meaningful item has one of two forms:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset for the field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for the same field.

Important groups in this chunk:

- HDMI generic packet controls for `DIG2` and `DIG3`: `HDMI_GENERIC_PACKET_CONTROL0/1/2/3/4/5/6/7/8/9/10` define send, continuous send, line reference, update-lock-disable, immediate-send, immediate-send-pending, line number, and enable-double-buffer-pending bits for generic packets 0-14. `DIG2` has only the tail of this group in this chunk; `DIG3` has the full group.
- HDMI packet/status controls: `HDMI_CONTROL`, `HDMI_STATUS`, `HDMI_AUDIO_PACKET_CONTROL`, `HDMI_ACR_PACKET_CONTROL`, `HDMI_VBI_PACKET_CONTROL`, `HDMI_INFOFRAME_CONTROL0/1`, `HDMI_GC`, `HDMI_DB_CONTROL`, and ACR N/CTS registers define data scrambling, deep color, AVMUTE, audio/VBI packet triggers, infoframe line numbers, ACR sample-rate parameters, and vupdate/double-buffer handshakes.
- DIG/TMDS controls: `DIG_FE_CNTL`, `DIG_BE_CNTL`, `DIG_BE_EN_CNTL`, `DIG_OUTPUT_CRC_*`, `DIG_TEST_PATTERN`, `DIG_FIFO_STATUS`, `TMDS_*`, and `FORCE_DIG_DISABLE` define frontend start/symclk state, Dolby Vision metadata status, back-end source and HPD selection, output CRC selection/result, test pattern generation, FIFO calibration/error fields, TMDS control character generation, DC balance, sync characters, and control-lane data selection.
- DisplayPort link/video/DPHY controls for `DP3` and `DP4`: `DP_LINK_CNTL`, `DP_PIXEL_FORMAT`, `DP_CONFIG`, `DP_VID_STREAM_CNTL`, `DP_STEER_FIFO`, `DP_MSA_*`, `DP_VID_*`, `DP_DPHY_*`, and `DP_LINK_FRAMING_CNTL` define stream enable, pixel encoding, MSA timing/colorimetry, VBID/MSA location, FIFO overflow reporting, lane test patterns, FEC, scrambler, 8b/10b, PRBS, CRC, MST CRC slot selection, and fast training.
- DisplayPort secondary packet and audio controls: `DP_SEC_CNTL`, `DP_SEC_CNTL1` through `DP_SEC_CNTL7`, `DP_SEC_FRAMING1` through `DP_SEC_FRAMING4`, `DP_SEC_AUD_N/M`, readbacks, timestamp mode, `DP_SEC_PACKET_CNTL`, and `DP_SEC_METADATA_TRANSMISSION` define ASP/ATP/AIP/ACM/GSP/MPG/ISRC enables, send/pending/deadline/idle status, packet framing windows, audio N/M values, coding type, metadata packet enable, and line references.
- MST/MSE/MSO and DSC controls: `DP_MSE_RATE_*`, `DP_MSE_SAT*`, `DP_MSE_SAT*_STATUS`, `DP_MSE_LINK_TIMING`, `DP_MSO_CNTL*`, `DP_DSC_CNTL`, and `DP_DSC_BYTES_PER_PIXEL` define stream allocation table entries, encryption flags, slot counts, update status, link timing, multi-stream-output secondary packet enables, DSC mode/slice width, and bytes-per-pixel.
- Low-power and extra GSP controls: `DP_ALPM_CNTL`, `DP_GSP8_CNTL` through `DP_GSP11_CNTL`, and `DP_GSP_EN_DB_STATUS` are visible for `DP3`, defining PHY sleep/standby signaling and extended generic secondary packet scheduling. The `DP4` part of this chunk does not reach the corresponding GSP8-GSP11 section before the chunk ends.

## Control Flow and State

There is no runtime control flow in this header. Runtime behavior emerges when driver code includes this file and passes these constants to register helpers. Typical flow is:

1. The driver selects a display encoder/link instance and a register address from the matching DCN 3.1.5 address header.
2. It prepares a field value by shifting it by `<REGISTER>__<FIELD>__SHIFT` and masking with `<REGISTER>__<FIELD>_MASK`, usually through local register helper macros rather than manual arithmetic.
3. It writes a memory-mapped register or reads one and extracts the field with the same shift/mask pair.
4. Hardware state changes asynchronously, and status fields such as `*_PENDING`, `*_TAKEN`, `*_ACTIVE`, `*_DEADLINE_MISSED`, `*_RESULT_VALID`, `*_FIFO_LEVEL_ERROR`, and `*_FAST_TRAINING_COMPLETE_OCCURRED` are observed by later driver reads.

The chunk describes several stateful hardware protocols:

- Double buffering: `DIG*_HDMI_DB_CONTROL`, `DP*_DP_DB_CNTL`, `HDMI_GENERIC*_EN_DB_PENDING`, `DP_SEC_GSP*_EN_DB_DISABLE`, and `DP_GSP_EN_DB_STATUS` govern or report when updates are pending, taken, locked, disabled, or synchronized to vupdate.
- Packet scheduling: HDMI generic packets and DP secondary/GSP packets have send, continuous, immediate, pending, active, deadline missed, idle-send, line-reference, and line-number fields. Driver sequencing must account for pending bits and missed-deadline status before assuming packet delivery.
- Link training and DPHY test state: `DP_DPHY_FAST_TRAINING*`, `DP_DPHY_TRAINING_PATTERN_SEL`, CRC, PRBS, 8b/10b, HBR2 pattern, and BS/SR swap fields describe hardware modes where writes initiate training/test actions and reads confirm completion/status.
- Stream allocation and timing: `DP_MSE_SAT*`, `DP_MSE_RATE_*`, `DP_MSO_CNTL*`, `DP_MSA_TIMING_PARAM*`, and `DP_VID_*` fields persist as programmed register state controlling current video and MST/MSO stream behavior.

## Dependencies and Integration Points

This header depends on the generated AMD ASIC register naming contract. It is useful only alongside:

- The corresponding DCN 3.1.5 register address definitions that name the same registers without the `__FIELD` suffix.
- AMDGPU display register helper macros/functions that accept register fields as shift/mask pairs, such as the DC `REG_GET`, `REG_SET`, `REG_UPDATE`, or similar generated macro layers used elsewhere in the driver.
- DC link encoder, stream encoder, audio, HDMI, DP, MST, DSC, and diagnostics code that needs per-generation field layouts.

Integration is intentionally compile-time. These macros become literal constants in C expressions, so there is no symbol linkage or persistence within the header itself. The persistence is in hardware registers after memory-mapped writes.

The replicated prefixes matter for integration:

- `DIG2` and `DIG3` identify separate digital encoder instances.
- `DP3` and `DP4` identify separate DisplayPort link/PHY instances.
- Shared suffixes with identical masks across `DP3` and `DP4` allow common code to operate on indexed register tables while preserving per-instance register names.

## Risks and Edge Cases

- Generated-header drift is the main risk. If a mask or shift is wrong, the driver can silently program the wrong bitfield, causing display blanking, packet loss, audio issues, failed link training, incorrect DSC/MST allocation, or missed interrupts.
- Chunk boundaries are not semantic boundaries. This chunk starts after the `DIG2_HDMI_GC` shift constants and ends before the `DP4_DP_SEC_METADATA_TRANSMISSION` mask constants. A per-file merge must combine neighboring chunks before making whole-register claims about those two registers.
- Field names ending in `MASK_MASK`, such as `DPHY_CRC_MASK_MASK` and `DPHY_FAST_TRAINING_COMPLETE_MASK_MASK`, are intentional generated names for fields named `*_MASK`; reviewers should not simplify them without changing all users.
- Several fields represent write-one-to-clear or handshake behavior by name (`*_ACK`, `*_CLR`, `*_PENDING`, `*_TAKEN`). The header does not encode access semantics; driver code and hardware documentation must enforce correct read/write sequencing.
- Many packet-line fields are 16-bit or 6-bit line selectors. Passing out-of-range values through raw helpers can truncate into neighboring fields if callers do not mask/validate before update.
- The `DP3` and `DP4` blocks are similar but not identical in this chunk due to chunk truncation and because `DP3` includes `DP_DSC_BYTES_PER_PIXEL`, `DP_ALPM_CNTL`, and `DP_GSP8` through `DP_GSP11` before `DIG3`; `DP4` does not reach those definitions here. Merge logic should avoid interpreting absence in this chunk as absence from the full source file.

## Test Signals

There are no unit-testable functions in this chunk. Useful validation signals are structural and integration-focused:

- Compile coverage: AMDGPU/DC code that includes `dcn_3_1_5_sh_mask.h` must build with no undefined register-field macros for DCN 3.1.5.
- Generated consistency checks: for each field, the mask should align with the shift and expected width; duplicated `DP3`/`DP4` and `DIG2`/`DIG3` register families should keep identical field layouts where the hardware block is replicated.
- Runtime display validation: HDMI and DP modes should light up across affected links, with audio infoframes/ACR, generic packets, DSC, MST/MSO, and fast training paths exercised.
- Diagnostics: CRC/test-pattern/PRBS paths and FIFO/overflow/error status fields can be checked with display test tooling or kernel debug traces.
- Hardware handshakes: tests should observe that `*_PENDING`, `*_TAKEN`, `*_ACTIVE`, `*_DEADLINE_MISSED`, and `*_RESULT_VALID` bits transition as expected after the corresponding driver writes.

## Chunk Notes for Merge Lane

- This chunk contains 2,411 source lines and 2,168 `#define` lines by prefix distribution: 221 `DIG2`, 756 `DP3`, 560 `DIG3`, and 631 `DP4`.
- The merge lane should combine this with adjacent chunks before writing the final per-file research document for `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h`.
- The chunk has no local includes, typedefs, structs, enums, functions, or writable software state.

### subset-b-001880: lines 37423-39826

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 37423-39826

## Purpose

This chunk is a generated DCN 3.1.5 ASIC register field header segment for AMD display hardware. It provides C preprocessor constants for register bit shifts and masks, not executable logic. The constants are consumed with the companion `dcn_3_1_5_offset.h` register-offset header by AMDGPU display code to build typed register tables and to drive `REG_GET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT` helper paths.

The range contains 2,166 macro definitions across 197 visible register names: 1,082 `__SHIFT` constants and 1,084 `_MASK` constants. It starts inside the `DP4_DP_SEC_METADATA_TRANSMISSION` register definition, after some field shifts were emitted in the previous chunk, and ends after the first `VPG3_VPG_MPEG_INFO0__VPG_MPEG_INFO_CHECKSUM__SHIFT` definition, before the rest of that register appears in the next chunk.

## Covered Hardware Blocks

- `DP4` tail fields: DisplayPort secondary-data metadata transmission, DSC bytes-per-pixel, ALPM PHY sleep/standby control, generic secondary packet controls for GSP8-GSP11, and generic packet enable double-buffer status.
- `DIG4` display encoder/front-end block: source selection, stereosync, start control, bypass, input pixel selection, Dolby Vision status, TMDS encoding/color, output CRC, test/random patterns, FIFO status, HDMI metadata/audio/VBI/infoframe/generic-packet/ACR/general-control registers, HDMI double-buffer controls, AFMT selection, backend enable/control, TMDS control characters, DC-balance, sync characters, generated control bits, version, and force-disable.
- `AFMT0` through `AFMT4`: repeated audio formatter field maps for VBI/audio packet controls, audio infoframes, IEC 60958 channel-status words, audio CRC controls/results, test ramps, status, audio source select, and memory power control.
- `DME0` through `DME3`: metadata engine controls and memory power controls for DIO instances 0-3.
- `VPG0` through `VPG3`: visual/generic packet generator packet data indexing, byte data, frame-update and immediate-update controls for generic packets 0-14, conflict/status bits, memory power controls, ISRC packet byte access, and MPEG infoframe fields. `VPG3_MPEG_INFO0` is incomplete in this chunk because of the line boundary.

## Important APIs, Types, and Macros

The header itself exposes macros only. The naming scheme is:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register value space.

Important consumers visible in this tree include:

- `display/dmub/src/dmub_dcn315.c`, where `dcn_3_1_5_sh_mask.h` is included and `FD_MASK(reg, field)` / `FD_SHIFT(reg, field)` populate `dmub_srv_dcn315_regs`.
- `display/dc/resource/dcn315/dcn315_resource.c`, where `SRI`, `SRII`, `SE_SF`, and related macros combine offsets from `dcn_3_1_5_offset.h` with masks/shifts from this file to instantiate DCN 3.1.5 hardware objects.
- `display/dc/dcn31/dcn31_vpg.h` and `display/dc/dcn31/dcn31_afmt.h`, whose `DCN31_VPG_MASK_SH_LIST` and `DCN31_AFMT_MASK_SH_LIST` macros reference representative instance-0 field names such as `VPG0_VPG_*` and `AFMT0_AFMT_*`; `dcn315_resource.c` uses the generated register and field tables for all DIO instances.
- `display/dc/dcn31/dcn31_vpg.c` and `display/dc/dcn31/dcn31_afmt.c`, where fields from this chunk such as `VPG_MEM_PWR`, `VPG_GSP_MEM_LIGHT_SLEEP_DIS`, `VPG_GSP_LIGHT_SLEEP_FORCE`, `VPG_GSP_MEM_PWR_STATE`, `AFMT_MEM_PWR_DIS`, `AFMT_MEM_PWR_FORCE`, and `AFMT_MEM_PWR_STATE` are used by register helper calls.

There are no functions, structs, enums, storage objects, syscalls, or direct control-flow statements in this chunk.

## Control Flow and State

Runtime control flow is indirect. Build-time macro expansion copies these constants into register descriptor structures. Later, display code calls register helper macros that use those descriptors to read, mask, shift, update, poll, or clear hardware registers.

The visible state is hardware state:

- Double-buffer lifecycle bits: `*_DB_PENDING`, `*_DB_TAKEN`, `*_DB_TAKEN_CLR`, `*_DB_LOCK`, `*_DB_DISABLE`, `*_VUPDATE_DB_PENDING`, and `*_VUPDATE_DB_TAKEN*` in DP, HDMI, DME, and generic-packet paths. These fields synchronize software writes with vblank/vupdate or packet-generator update points.
- Packet send state: `SEND`, `CONT`, `IMMEDIATE_SEND`, `SEND_PENDING`, `SEND_ACTIVE`, `SEND_DEADLINE_MISSED`, `LINE_REFERENCE`, and line-number fields for HDMI generic packets and DP GSP packets.
- Error and clear/ack state: HDMI error/status bits, metadata packet missed bits, DME metadata transmission missed/clear fields, VPG generic conflict/clear fields, audio FIFO overflow/ack, and audio-enable change ack.
- Power state: `AFMT_MEM_PWR_*`, `DME_MEM_PWR_*`, and `VPG_GSP_MEM_*` fields expose block-local memory power force/disable/state/default-low-power controls.
- Indexed payload state: VPG generic, ISRC, and MPEG infoframe data fields expose byte-wide packet payload storage behind an access index. Payload contents persist in hardware packet RAM/register state until overwritten or reset by display hardware sequencing.

## Dependencies and Integration Points

This file depends on exact DCN 3.1.5 hardware register layout. It must stay aligned with:

- `dcn_3_1_5_offset.h` for register addresses and base-index selection.
- DCN 3.1/3.0 display object headers such as `dcn31_vpg.h`, `dcn31_afmt.h`, `dcn30_dio_stream_encoder.h`, and stream encoder/resource constructors that expect particular field names.
- Register helper macros in `reg_helper.h` and DMUB register helpers that interpret these masks and shifts.
- DRM/AMDGPU display bring-up, hotplug/IRQ, audio, HDMI/DP stream encoder, DMUB service, and resource-pool construction code that includes the DCN 3.1.5 generated headers.

The repeated instance prefixes are significant. `AFMT0`-`AFMT4`, `DME0`-`DME3`, and `VPG0`-`VPG3` are separate hardware instances. Resource code maps VPG/AFMT/DME blocks to DIO stream encoders, and later comments in `dcn315_resource.c` also map higher VPG instances to HPO DP stream encoders outside this chunk.

## Risks and Edge Cases

- A wrong mask or shift silently writes the wrong hardware bits. Failure modes include blank output, broken HDMI/DP metadata, missing HDR/Dolby Vision metadata, audio channel/status corruption, packet deadline misses, FIFO overflow, or display power-management regressions.
- The chunk boundaries split complete register definitions. `DP4_DP_SEC_METADATA_TRANSMISSION` begins in a previous chunk, and `VPG3_VPG_MPEG_INFO0` continues in a later chunk; the merge lane must combine adjacent research to avoid treating those registers as incomplete in the final per-file report.
- Repeated instance blocks are easy to mix up. Instance-0 field names are often used to define common masks/shifts for object classes, while offsets select the concrete instance. Manual edits that copy `AFMT0` fields into `AFMT4` or vice versa could compile but program the wrong table.
- Clear/ack fields such as `*_CLR`, `*_ACK`, and conflict clear bits may have write-one-to-clear semantics in hardware. Generic read-modify-write code must avoid unintentionally asserting them.
- Pending/status fields are hardware-synchronized. Poll loops or update paths need timeouts and must account for vblank/vupdate timing, disabled streams, and power-gated memories.
- Some fields represent line numbers or packet slots with limited masks. Out-of-range line placement or packet index values can be truncated by the mask and may only show up as missed/deadline status bits.

## Test and Validation Signals

- Kernel build coverage for DCN 3.1.5 display code verifies that every referenced field macro still exists and has the expected naming shape.
- Register-table initialization in `dcn315_resource.c` and `dmub_dcn315.c` should compile without missing `FD_MASK`, `FD_SHIFT`, `SE_SF`, or `SRI` expansions.
- Display smoke tests should cover HDMI and DP link bring-up, mode sets, vblank/vupdate behavior, suspend/resume, and stream disable/enable cycles.
- Feature tests should cover HDMI audio, audio channel layouts, IEC 60958 channel-status updates, audio CRC/test paths, infoframes, generic packets, HDR/Dolby Vision metadata, DP secondary-data packets, DSC bytes-per-pixel programming, and ALPM PHY sleep/standby transitions.
- Useful runtime diagnostics include HDMI/DP packet missed/deadline bits, audio FIFO overflow/status bits, VPG generic conflict status, DME metadata transmission missed status, double-buffer pending/taken fields, and VPG/AFMT/DME memory power state reads.

### subset-b-001881: lines 39827-42175

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 39827-42175

## Scope

This chunk is a generated DCN 3.1.5 register-field mask/shift slice. It contains only C preprocessor constants and address-block/register comments: `_SHIFT` macros encode field bit positions, and `_MASK` macros encode raw 32-bit register masks. There are no C functions, structs, enums, allocations, branches, loops, or direct MMIO operations in this range.

The range starts in the tail of `VPG3_VPG_MPEG_INFO0`, covers `VPG3_VPG_MPEG_INFO1`, then fully defines the DIG4 DME/VPG4 blocks, DP AUX instances 0 through 4, the shared DOUT I2C/DDC controller block, and DIO scratch registers 0 through 6. The next source lines continue with `DIO_SCRATCH7` and DIO memory-power registers, so DIO scratch coverage is intentionally partial at this chunk boundary.

## Purpose And Hardware Surface

This header section supplies the bit-layout ABI used by AMDGPU Display Core for DCN 3.1.5 display-I/O hardware. Companion generated headers provide register offsets; this file provides the field masks and shifts consumed by register-helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`.

Major hardware areas represented here:

- VPG packet generation: `VPG3_VPG_MPEG_INFO*` tail fields and full `VPG4_*` generic packet, frame-update, immediate-update, status, memory-power, ISRC, and MPEG-info fields used for HDMI/DP info packets and metadata injection.
- DIG4 DME metadata engine: `DME4_DME_CONTROL` and `DME4_DME_MEMORY_CONTROL` fields for enabling dynamic metadata, selecting metadata stream/requestor behavior, observing double-buffer handshakes, clearing missed transmissions, and controlling DME SRAM power.
- DP AUX channels 0-4: repeated `DP_AUXn_*` field groups for AUX enable/reset, software and link-service transfers, AUX arbitration, interrupt status/ack/masking, software/link-service data windows, AUX DPHY TX/RX timing, GTC sync control/status, and AUX PHY wake handshakes.
- DC I2C/DDC controller: `DC_I2C_*` fields for software I2C transactions, register arbitration with firmware/hardware users, DDC1-5 hardware/EDID detection status, per-DDC speed/setup timing, transaction descriptors 0-3, indexed data buffer access, EDID-detect control, and read-request interrupt handling for DDC1-6 plus DDCVGA.
- DIO scratch registers: full-width scratch masks for `DIO_SCRATCH0` through `DIO_SCRATCH6`.

## Important Definitions

The exported interface is the generated naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bitmask for that field in the register value.
- `// addressBlock: ...` comments group register instances by hardware block.
- `//<REGISTER>` comments group the fields belonging to each register.

Important macro families in this chunk:

- `DME4_DME_CONTROL` defines metadata requestor ID, engine enable, stream type, double-buffer pending/taken status, clear bits, DB disable, transmission-missed status, and missed clear fields. `DME4_DME_MEMORY_CONTROL` defines force/disable/state/default-low-power fields for DME memory.
- `VPG4_VPG_GENERIC_PACKET_ACCESS_CTRL` and `VPG4_VPG_GENERIC_PACKET_DATA` expose the indexed generic packet RAM window, with four packed data bytes per write. `VPG4_VPG_GSP_FRAME_UPDATE_CTRL` and `VPG4_VPG_GSP_IMMEDIATE_UPDATE_CTRL` provide update and pending bits for generic packets 0-14. `VPG4_VPG_GENERIC_STATUS` exposes lock/conflict state and conflict clear. `VPG4_VPG_MEM_PWR` controls and reports VPG GSP memory light-sleep state. ISRC and MPEG registers expose packed metadata bytes and MPEG update controls.
- Each `DP_AUXn_AUX_CONTROL` block has channel enable/reset, reset-done, link-service read enable, HPD disconnect handling, AUX mode detection, HPD select, impedance calibration request enable, test mode, deglitch enable, and spare bits.
- Each `DP_AUXn_AUX_SW_CONTROL`, `AUX_SW_STATUS`, and `AUX_SW_DATA` group describes software AUX transactions: go/start delay/write-byte count, done/request/error status, reply-byte count, arbitration status, data read/write byte, indexed data access, and autoincrement disable.
- Each `DP_AUXn_AUX_LS_STATUS` and `AUX_LS_DATA` group provides the link-service side of AUX traffic, including done/request/error status, reply-byte count, CP IRQ, updated/ack state, and indexed data access.
- Each `DP_AUXn_AUX_ARB_CONTROL` group coordinates AUX register ownership among software and DMCU/firmware paths through priority, queued-go controls, use-reg requests, pending request state, and done-using-reg bits.
- Each `DP_AUXn_AUX_INTERRUPT_CONTROL` group defines SW done, LS done, GTC sync lock done, and GTC sync error interrupt status/ack/mask fields.
- Each `DP_AUXn_AUX_DPHY_*` group defines AUX physical-layer TX reference/rate/divider, precharge and output-enable timing, mode-detect delay, RX detection windows/threshold/filtering, timeout length, TX active/state/half-symbol period, and RX state/sync/half-symbol period readbacks.
- Each `DP_AUXn_AUX_GTC_SYNC_*` group defines GTC sync enable/impedance calibration/interval/retry/lock timing controls, potential/definite error thresholds, lock acquisition and maintenance status, critical and max-error ack bits, detailed AUX transaction error status, NACK state, and master-request state.
- Each `DP_AUXn_AUX_PHY_WAKE_CNTL` group provides wake go/pending/priority/ack fields for AUX PHY wake sequencing.
- `DC_I2C_CONTROL`, `DC_I2C_ARBITRATION`, and `DC_I2C_SW_STATUS` define software I2C transaction start/reset/DDC select/count fields, ownership/arbitration and abort controls, and completion/timeout/NACK/buffer-overflow status.
- `DC_I2C_DDC1..5_HW_STATUS`, `DC_I2C_DDC1..5_SPEED`, and `DC_I2C_DDC1..5_SETUP` repeat per-DDC hardware status, EDID-detect status/tries/state, threshold/filter/start-stop/prescale timing, line drive, reset length, EDID detection mode, enable, clock drive, byte/transaction delay, and time-limit fields.
- `DC_I2C_TRANSACTION0..3` define read/write, stop-on-NACK, start, stop, and byte-count fields for up to four queued I2C transaction descriptors. `DC_I2C_DATA` exposes the indexed transfer buffer. `DC_I2C_EDID_DETECT_CTRL` sets EDID detect wait time, valid-try count, and reset-send behavior. `DC_I2C_READ_REQUEST_INTERRUPT` packs occurred/int/ack/mask fields for DDC1-6 and DDCVGA plus global ack-enable and interrupt-type controls.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when DCN 3.1.5 display code combines these macros with matching offset registers and register access helpers. The typical flow is:

1. Driver code selects a VPG, DME, AUX, I2C/DDC, or DIO register offset from the generated DCN 3.1.5 offset header or a local register table.
2. The register helper layer uses this header's mask/shift constants to pack fields, perform read/modify/write updates, or decode status fields.
3. MMIO writes program hardware state or trigger side effects; MMIO reads observe volatile status, counters, handshakes, or scratch values.

The state represented here is hardware register state, not persistent driver-owned memory:

- Persistent configuration includes VPG packet RAM contents, generic packet update mode, VPG/DME memory-power controls, DME metadata enable/requestor/stream-type selections, AUX channel enable/timing/arbitration/interrupt mask settings, AUX DPHY timing windows, GTC sync thresholds and retry periods, DDC speed/setup timing, I2C transaction descriptors, EDID detect parameters, and read-request interrupt masks.
- Volatile readback includes VPG conflict/lock status, VPG/DME memory power state, DME double-buffer and missed-transmission state, AUX reset-done, SW/LS/GTC transaction status and errors, AUX arbitration state, DPHY TX/RX state, PHY wake pending/ack, I2C software completion/error/NACK status, DDC hardware/EDID detect state, read-request interrupt state, and DIO scratch values.
- Side-effecting bits include DME clear bits, VPG conflict clear, VPG frame/immediate update triggers, AUX reset/go/ack/done-using-reg/LS updated ack/GTC error acks/PHY wake go, I2C go/reset/status reset/abort/done-using-reg, indexed-data write controls, EDID reset-send, and DDC read-request acks.

## Dependencies And Integration Points

This chunk depends on generated-name consistency across the DCN 3.1.5 register header family. It is consumed with `dcn_3_1_5_offset.h` by DCN 3.1.5 resource, IRQ, GPIO, and DMUB code, and by shared Display Core modules that use chip-specific register tables.

Primary integration points include:

- `display/dc/dcn31/dcn31_vpg.*`: the VPG register and mask tables consume `VPG*_VPG_GENERIC_*`, update-control, status, and memory-power fields. Runtime code writes infoframe/generic-packet bytes through the indexed packet data window, clears conflicts, triggers immediate or frame updates, and controls VPG memory light sleep.
- Display link training and capability paths: DP AUX masks back the low-level AUX engine used for DPCD reads/writes, I2C-over-AUX, link-service status, HPD disconnect behavior, AUX error diagnostics, CP IRQ handling, LTTPR/sink probing, and GTC sync support.
- GPIO/DDC code: `display/dc/gpio/ddc_regs.h` and `hw_ddc.c` use DDC setup fields such as `DC_I2C_DDC1_ENABLE`, `DC_I2C_DDC1_EDID_DETECT_ENABLE`, and `DC_I2C_DDC1_EDID_DETECT_MODE` to configure DDC pins and EDID detection. Software I2C command paths use the control, arbitration, transaction, status, and data-buffer fields.
- IRQ service and firmware coordination: AUX and I2C arbitration/interrupt fields coordinate software, hardware, and DMCU/DMUB users. Incorrect ownership or ack handling can block display detection or lose interrupts.
- Dynamic metadata and info packet paths: DME4 and VPG4 fields integrate with HDMI/DP metadata, generic packets, ISRC, MPEG infoframes, and frame/immediate update scheduling.
- Power-management sequences: DME/VPG memory-power fields, AUX PHY wake fields, and DDC/AUX enable/reset state must be consistent across runtime power transitions, suspend/resume, and display link reinitialization.

Because this file is only macro definitions, missing names usually fail at compile time where referenced. Wrong numeric shifts or masks generally compile successfully but can misprogram MMIO at runtime.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.5 register specification is the main risk. A wrong field value can corrupt DME/VPG metadata programming, AUX transaction timing, I2C/DDC EDID reads, interrupt acks, or power gating.
- The DP AUX blocks are highly repetitive across instances 0-4. Prefix or copy-generation mistakes can silently bind an otherwise valid field layout to the wrong AUX channel.
- Several fields are side-effecting or handshake-based. Clear/ack/go/reset/update bits must be written deliberately; broad read/modify/write helpers can accidentally retrigger updates or clear latched diagnostics if masks are wrong.
- AUX and I2C arbitration fields coordinate multiple clients. Mishandling `*_USE_*_REG_REQ`, pending-request, and done-using fields can deadlock access between driver software and firmware paths.
- Indexed data windows require ordering discipline. VPG packet data, AUX SW/LS data, and DC I2C data all pair an index field with byte/data fields; callers must preserve autoincrement semantics and byte order.
- DDC and AUX timing fields are hardware-contract values. Prescale, timeout, threshold, phase-detect, precharge, and RX window mistakes may surface only with marginal cables, retimers, sinks, or I2C-over-AUX transactions.
- The chunk begins and ends inside logical register families. It starts after the first VPG3 MPEG checksum field and ends before `DIO_SCRATCH7`, so final per-file reconciliation must merge neighboring chunks for a complete file-level account.
- `DIO_SCRATCH*` fields are full-width and generic. Their meaning depends on firmware/driver convention outside this header, so consumers must not assume persistence or ownership from the mask alone.

## Test Signals

Useful validation is generated-header consistency plus hardware behavior:

- Build DCN 3.1.5 AMDGPU display code and ensure all generated macro names referenced by VPG, GPIO/DDC, IRQ, DMUB, and resource tables resolve.
- Run generated-header checks that every in-scope field has a matching `_SHIFT` and `_MASK`, masks fit in 32 bits, and fields do not overlap unexpectedly inside each register.
- Compare this range against the authoritative DCN 3.1.5 register specification, especially repeated DP AUX0-4 and DDC1-5 blocks.
- Exercise VPG generic packet programming by writing infoframes/metadata, clearing conflicts, triggering immediate and frame updates, and verifying pending/status behavior.
- Validate DME4 metadata operation with metadata engine enable, requestor selection, double-buffer pending/taken handshakes, missed-transmission clear, and DME memory-power state transitions.
- Run DP AUX DPCD read/write, I2C-over-AUX, link training, HPD disconnect, CP IRQ, and error-path tests on ports mapped to AUX0-4; confirm timeout, overflow, invalid symbol/start/stop, and reply-byte-count decoding.
- Test AUX arbitration with software and firmware users active, checking request/pending/done-using handshakes and interrupt ack/mask behavior.
- Validate AUX DPHY and GTC sync fields through link bring-up, low-power wake, and GTC sync lock/loss/error scenarios.
- Exercise DDC software I2C EDID reads on DDC1-5, including transaction descriptors 0-3, stop-on-NACK paths, buffer indexing, prescale/timing setup, reset/status reset, and timeout behavior.
- Test hardware EDID detect and DDC read-request interrupts across DDC1-6/DDCVGA, confirming occurred/int/ack/mask/global ack-enable semantics.
- Include suspend/resume and runtime power tests with active displays to verify VPG/DME memory-power, AUX PHY wake, DDC enable, and volatile status fields recover correctly.

## Chunk-Specific Summary

Lines 39827-42175 define DCN 3.1.5 display-I/O mask and shift constants for the end of VPG3 MPEG info, all DIG4 DME/VPG4 metadata and packet-generation fields, DP AUX0-4 software/link-service/DPHY/GTC/PHY-wake fields, the shared DC I2C/DDC controller and EDID-detect fields, and DIO scratch registers 0-6. Correctness depends on exact generated bit positions, instance-correct macro use, careful treatment of trigger/ack/clear fields, and hardware validation that covers info packet updates, dynamic metadata, AUX/DPCD and I2C-over-AUX traffic, DDC EDID reads, interrupt handling, arbitration, and power transitions.

### subset-b-001882: lines 42176-44691

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 42176-44691

## Purpose

This chunk is generated AMD DCN 3.1.5 register field metadata. It contains no executable logic; it publishes `#define` constants for field shifts and bit masks used to encode and decode MMIO register values in the AMDGPU display driver.

The requested range starts in the `dce_dc_dio_dio_misc_dispdec` block at the mask half of `DIO_SCRATCH6`, covers DIO memory power, clock gating, soft reset, link control, and a DC perfmon instance, then covers DCIO link/GPIO/AUX pad control, five UNIPHY macro reserved blocks (`DCIO_UNIPHY0` through `DCIO_UNIPHY4`, reserved registers 0 through 57), and enters `dce_dc_pwrseq0_dispdec_pwrseq_dispdec` through the first `PWRSEQ0_BL_PWM_GRP1_REG_LOCK` shift macro. The range contains 2,086 `#define` lines, normally organized as pairs or groups of `__SHIFT` and `_MASK` macros.

Although the file lives under a local `ceph-client` source mirror, this path is AMDGPU display-controller hardware metadata, not Ceph or distributed-filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, local includes, allocation paths, locks, or callbacks in this range. The public surface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position used when placing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field in the 32-bit MMIO register.
- Full-width scratch or reserved fields such as `DIO_SCRATCH7__DIO_SCRATCH7_MASK` and `DCIO_UNIPHY*_UNIPHY_MACRO_CNTL_RESERVED*__UNIPHY_MACRO_CNTL_RESERVED_MASK` expose all 32 bits.

Major register families in this chunk:

- DIO misc: `DIO_SCRATCH6` tail, `DIO_SCRATCH7`, `DIO_MEM_PWR_STATUS`, `DIO_MEM_PWR_CTRL`, `DIO_MEM_PWR_CTRL2`, `DIO_CLK_CNTL`, `DIO_POWER_MANAGEMENT_CNTL`, `DIG_SOFT_RESET`, `DIO_CLK_CNTL2`, `DIO_CLK_CNTL3`, HDMI RX status timer control, PSP/generic interrupt clear/message registers, and `DIO_LINKA_CNTL` through `DIO_LINKF_CNTL`.
- `DC_PERFMON18`: perf counter enable/reset/clear/start/stop, event selectors, state flags, overflow/underflow/current-value interrupt fields, and high/low counter-value registers.
- DCIO display core: generic `DC_GENERICA`/`DC_GENERICB`, `DCIO_CLOCK_CNTL`, `DC_REF_CLK_CNTL`, `UNIPHYA` through `UNIPHYE` link control and channel crossbar fields, `DCIO_WRCMD_DELAY`, `DC_PINSTRAPS`, `INTERCEPT_STATE`, backlight PWM frame-start display selection, genlock/swaplock pad control, and `DCIO_SOFT_RESET`.
- DCIO chip GPIO and pads: generic GPIO mask/A/en/Y registers, DDC1 through DDC5 and DDCVGA mask/A/en/Y registers, GENLK and HPD mask/A/en/Y registers, `DC_GPIO_PWRSEQ0_EN`, pad strength registers, `PHY_AUX_CNTL`, `DC_GPIO_PWRSEQ1_EN`, TX12/RXEN/pull-up controls, AUX control registers 0 through 5, and `AUXI2C_PAD_ALL_PWR_OK`.
- UNIPHY macro reserved ranges: five address blocks, each defining 58 full-width `UNIPHY_MACRO_CNTL_RESERVED` fields. These are opaque 32-bit macro-control slots rather than named functional fields in this generated header.
- PWRSEQ0 and backlight PWM: GPIO power-sequencer enable/control/mask/A/Y fields, panel power-sequence control and state, power-up/down delay fields, reference dividers, backlight PWM duty/enable/fractional/frame-start fields, PWM period fields, and the first shift definition for `BL_PWM_GRP1_REG_LOCK`.

## Control Flow

This header has no runtime control flow. Runtime behavior is created by token-pasting helpers in DCN 3.1.5 display code:

1. DCN 3.1.5 resource, IRQ, and DMUB code include `dcn_3_1_5_offset.h` with this matching `dcn_3_1_5_sh_mask.h`.
2. Register table macros such as `SR(...)`, `SRI(...)`, and DMUB `DMUB_SF(...)` combine offset macros with these field masks and shifts.
3. The resulting tables are consumed through `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_GET`, IRQ ack helpers, DIO helpers, DMUB service code, and panel-control paths.
4. Hardware sequencing is owned by the consumers. This generated header does not know when a field may be read, written, polled, write-one-to-clear, or left untouched.

One direct consumer visible in `dcn315_resource.c` is `DIO_MEM_PWR_CTRL`: it is added to hardware-sequencer and DIO register tables, and its `I2C_LIGHT_SLEEP_FORCE` field is exposed through mask/shift structs. `dcn10_dio.c` then writes `DIO_MEM_PWR_CTRL` and optionally sets `I2C_LIGHT_SLEEP_FORCE` in `dcn10_dio_mem_pwr_ctrl()`. The PWRSEQ0/PWM fields in this chunk are part of the same ASIC field namespace; on DCN 3.1 panel control, `dcn31_panel_cntl.c` largely delegates backlight/panel state operations to DMUB commands and persists PWM register values in `stored_backlight_registers`.

## State And Persistence Behavior

The chunk stores no software state. It describes bit positions in MMIO-backed display hardware state:

- DIO power and clock state: I2C and DP link memory power status, light-sleep force/disable bits, DISPCLK/REFCLK/SOCCLK/SYMCLK gate-disable controls, and DIO power-management busy/reset flags.
- Digital encoder reset and link state: DIG front-end/back-end soft reset fields, DIO link enable/swap fields, HDMI RX status timer controls, and generic interrupt clear/message fields.
- Perfmon state: counter enable, event selection, trigger mode, reset/clear, overflow/underflow/current-value status and interrupt mask/ack fields, and latched counter values.
- DCIO routing and pad state: UNIPHY link controls and crossbars, pinstrap/intercept states, DCIO soft resets, GPIO mask/output/enable/readback fields, DDC/HPD/GENLK/power-sequence pins, AUX pad controls, pull-up/RX/TX controls, pad drive strength, and AUX/I2C power-good bits.
- UNIPHY reserved state: opaque full-width reserved registers for UNIPHY macro control. Since the field name is generic, correctness depends on hardware documentation and generated register databases outside this header.
- Panel and backlight state: PWRSEQ0 GPIO routing, target/current panel power states, DIGON/SYNCEN/BLON polarity and override bits, sequencing delays, reference dividers, PWM active count, fractional enable, enable, period, and frame-start update behavior.

Persistence is hardware-defined. Many configuration fields retain values until modeset, power gating, suspend/resume, DMUB intervention, or ASIC reset. Status, interrupt, clear, pending, and readback fields may be sticky, read-only, write-one-to-clear, self-clearing, or timing-sensitive. The macros do not encode those semantics.

## Dependencies And Integration Points

This chunk must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`, which supplies the matching register offsets and base-index selectors.
- DCN 3.1.5 base segment definitions in include sites such as `dcn315_resource.c`, `irq_service_dcn315.c`, and `dmub_dcn315.c`.
- `reg_helper.h` and AMD display register-table structs that expect exact mask/shift names from generated headers.
- DMUB firmware command contracts for panel control and backlight state on DCN 3.1-class hardware.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`

Integration is mostly compile-time token pasting. For example, `HWS_SF(, DIO_MEM_PWR_CTRL, I2C_LIGHT_SLEEP_FORCE, _MASK)` resolves to `DIO_MEM_PWR_CTRL__I2C_LIGHT_SLEEP_FORCE_MASK`, while `HWS_SF(..., __SHIFT)` resolves to the matching shift. IRQ and DMUB code use the same generated namespace for other registers in the full header. The repeated GPIO, DDC, HPD, AUX, UNIPHY, and PWRSEQ fields integrate with display link bring-up, hotplug detection, EDID/DDC/AUX access, embedded-panel power sequencing, backlight PWM handling, genlock/swaplock pads, and low-power display transitions.

## Risks And Edge Cases

- Mask/shift drift is the main risk. These are untyped constants; a wrong bit position compiles cleanly but can program the wrong hardware field.
- The range is an artificial slice. It starts after the `DIO_SCRATCH6` shift macro and stops before the rest of `PWRSEQ0_BL_PWM_GRP1_REG_LOCK`; adjacent chunks are required for complete file-level claims.
- Repeated pin and link families are copy-sensitive. DDC1-DDC5/DDCVGA, HPD, GENLK, PWRSEQ pins, AUX controls, UNIPHY A-E link controls, and UNIPHY0-4 reserved ranges are easy to misalign by instance.
- Power and reset bits are high risk. Incorrect DIO memory power, clock-gate, soft-reset, or light-sleep fields can produce blank links, failed AUX/DDC transactions, resume failures, or blocks that never enter/leave low-power state.
- GPIO and pad fields have board-level effects. Wrong masks or enables can break HPD, EDID, AUX, panel power rails, backlight enables, genlock/swaplock pads, or pin pull-ups.
- Full-width reserved UNIPHY fields are opaque. Accidental writes may affect PHY behavior in ways not explained by the generated field name.
- Panel power sequencing and PWM fields are timing-sensitive. Bad delay, reference-divider, enable, override, polarity, or double-buffer lock fields can cause flicker, no backlight, stuck panel power state, or suspend/resume brightness loss.
- Perfmon fields may be clear/ack/pending sensitive. Misusing overflow, underflow, or current-value interrupt masks can create stuck interrupts or misleading performance counters.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU display support for DCN 3.1.5; missing or renamed macros should fail in `dmub_dcn315.c`, `irq_service_dcn315.c`, `dcn315_resource.c`, and shared DIO/panel-control code.
- Mechanically compare each `__SHIFT`/`_MASK` pair in lines 42176-44691 against AMD's source register database and the matching `dcn_3_1_5_offset.h` register names.
- Verify the known chunk-boundary exceptions: `DIO_SCRATCH6` is partial at the start and `PWRSEQ0_BL_PWM_GRP1_REG_LOCK` is partial at the end.
- Exercise display link bring-up across available DCN 3.1.5 connectors: DP/HDMI modesets, link training, hotplug, HPD RX, EDID/DDC, AUX DPCD reads/writes, multi-display, and suspend/resume.
- Validate DIO low-power behavior by watching for AUX/DDC timeouts, link-training failures, stuck display clocks, resume failures, or abnormal power-management logs when I2C light sleep and DIO memory power controls are touched.
- Test embedded-panel paths where present: panel power on/off, backlight restore after boot and resume, PWM frequency override, brightness changes, BLON/DIGON/SYNCEN behavior, and no visible flicker during frame-start PWM updates.
- Check GPIO and pad behavior through HPD storms, DDC bus recovery, AUX/I2C pad power-good status, pull-up configuration, genlock/swaplock use cases, and board-specific power-sequence pins.
- Validate perfmon register definitions with counter start/stop/reset/clear, overflow/underflow interrupt handling, and stable high/low counter reads if DC perfmon 18 is exposed by diagnostics.

## Cross-Chunk Notes

Previous chunks own the beginning of the DCN 3.1.5 DIO misc block, including `DIO_SCRATCH0` through the `DIO_SCRATCH6__SHIFT` macro. Later chunks continue `PWRSEQ0_BL_PWM_GRP1_REG_LOCK`, `PWRSEQ0_PANEL_PWRSEQ_REF_DIV2`, `PWRSEQ0_PWRSEQ_SPARE`, and additional power-sequencer blocks. The final per-file research document should merge adjacent chunks before making complete claims about all DIO, DCIO, UNIPHY, GPIO, PWRSEQ, or backlight-PWM field coverage in `dcn_3_1_5_sh_mask.h`.

### subset-b-001883: lines 44692-47145

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 44692-47145

## Scope

This chunk is a generated AMD DCN 3.1.5 register-field shift/mask header slice. It contains preprocessor constants only: `_SHIFT` macros for hardware bit positions, `_MASK` macros for raw register bit masks, register grouping comments, and address-block comments. There are no functions, structs, enums, local variables, branches, loops, allocations, software locks, or file-backed persistence in this range.

The requested range contains 2,142 `#define` lines: 1,071 shift definitions and 1,071 mask definitions. It starts in the tail of the `PWRSEQ0_BL_PWM_GRP1_REG_LOCK` definitions, covers complete `PWRSEQ1`, `DSCC0..2`, `DSCCIF0..2`, `DSC_TOP0..2`, DSC-related `DC_PERFMON19..21`, HPO top/mapper/perfmon, `AFMT5`, `DME5`, `VPG5`, `DP_STREAM_ENC0`, and the beginning of `APG0`. It ends at `APG0_APG_AUDIO_CRC_RESULT`; the remaining APG0 status/memory/spare definitions are in the following chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU display-controller hardware metadata, not Ceph filesystem code.

## Purpose

The purpose of this header range is to provide the DCN 3.1.5 bit-layout ABI used by AMDGPU Display Core and DMUB code when programming MMIO registers. Matching offset definitions in `dcn_3_1_5_offset.h` identify register addresses and base indices; this file identifies the bit fields inside those registers. Runtime code combines both sets of macros through register helpers and generated register-table initializers to pack writes, build read/modify/write masks, decode readbacks, and poll status bits.

The major hardware surfaces represented here are:

- Panel power sequencing and backlight PWM for `PWRSEQ1`, plus the end of `PWRSEQ0`.
- Display Stream Compression controller blocks `DSCC0`, `DSCC1`, and `DSCC2`, their DSCCIF interfaces, top-level DSC controls, and per-DSC performance monitors.
- High Performance Output control: HPO top clock/hardware control, DP stream mapper controls, and HPO performance monitor 22.
- HDMI/DIO stream support blocks for instance 5: AFMT audio/infoframe registers, DME dynamic metadata registers, and VPG generic packet/video packet registers.
- HPO DP stream encoder 0 and the start of APG0 audio packet generator definitions.

This chunk is data, but it is not passive in practice. A wrong mask or shift can compile successfully and then program the wrong hardware bits during panel power transitions, DSC PPS setup, HPO stream creation, audio packet generation, metadata transmission, CRC/debug capture, or performance monitoring.

## Important APIs, Types, And Macros

The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for the field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register-positioned form.
- `//<REGISTER>` comments group field macros by register.
- `// addressBlock: ...` comments identify the hardware aperture for following registers.

There are no C APIs or types defined in this slice. The important definition families are the register namespaces below.

### PWRSEQ And Backlight PWM

The chunk starts after the beginning of `PWRSEQ0_BL_PWM_GRP1_REG_LOCK`, then completes `PWRSEQ0_PANEL_PWRSEQ_REF_DIV2` and `PWRSEQ0_PWRSEQ_SPARE`. The `PWRSEQ1` block defines a complete second panel power-sequencer instance:

- `PWRSEQ1_DC_GPIO_PWRSEQ_EN`, `PWRSEQ1_DC_GPIO_PWRSEQ_CTRL`, `PWRSEQ1_DC_GPIO_PWRSEQ_MASK`, and `PWRSEQ1_DC_GPIO_PWRSEQ_A_Y` describe VARY_BL, DIGON, and BLON GPIO enable, TX/RX/pull-up/drive-strength, mask/pull-down/receiver, and A/Y state fields.
- `PWRSEQ1_PANEL_PWRSEQ_CNTL` and `PWRSEQ1_PANEL_PWRSEQ_STATE` expose panel power-sequence enable, target state, SYNCEN/DIGON/BLON signal control, override/polarity fields, current target/state readback, and done/status bits.
- `PWRSEQ1_PANEL_PWRSEQ_DELAY1`, `PWRSEQ1_PANEL_PWRSEQ_DELAY2`, `PWRSEQ1_PANEL_PWRSEQ_REF_DIV1`, and `PWRSEQ1_PANEL_PWRSEQ_REF_DIV2` define power-up/down timing, minimum power-down length, variable-backlight override, panel and PWM reference divisors, XTAL reference divisor, and microsecond time base divisor.
- `PWRSEQ1_BL_PWM_CNTL`, `PWRSEQ1_BL_PWM_CNTL2`, `PWRSEQ1_BL_PWM_PERIOD_CNTL`, and `PWRSEQ1_BL_PWM_GRP1_REG_LOCK` define active PWM count, PWM enable/fractional-enable bits, frame-start update recognition, post-frame-start update delay, debug reference-clock selection, period/bit-count, double-buffer readback, update-pending, frame-start update, master-lock bypass, and lock fields.

These definitions are paired with legal values documented in enum headers such as `soc21_enum.h` and `soc24_enum.h`, including PWM enable/fractional-enable, frame-start update, register lock, target panel state, and PWM override meanings.

### DSC, DSCC, DSCCIF, And DSC_TOP

For `DSCC0`, `DSCC1`, and `DSCC2`, this chunk repeats the same Display Stream Compression controller field layout:

- `DSCC*_DSCC_CONFIG0` covers ICH reset at end of line, slices per line, alternate ICH encoding, and vertical slice count.
- `DSCC*_DSCC_CONFIG1` carries the rate-control buffer model size.
- `DSCC*_DSCC_STATUS` exposes double-buffer register update pending.
- `DSCC*_DSCC_INTERRUPT_CONTROL_STATUS` exposes rate-buffer overflow/underflow occurred bits for buffers 0-3, rate-control buffer model overflow bits for models 0-3, and the corresponding interrupt-enable bits.
- `DSCC*_DSCC_PPS_CONFIG0` through `DSCC*_DSCC_PPS_CONFIG22` pack DSC Picture Parameter Set fields: DSC version, PPS identifier, line buffer depth, bits per component, bits per pixel, VBR/simple/native 4:2:2/4:2:0/RGB conversion flags, chunk size, picture and slice geometry, initial transmit/decode delays, scale values and intervals, line BPG offsets, NFL/NSL/slice BPG offsets, initial/final offsets, flatness and RC model fields, edge factor, quantization increment limits, target offsets, RC buffer thresholds 0-13, and range min/max QP plus range BPG offsets 0-14.
- `DSCC*_DSCC_MEM_POWER_CONTROL` defines default low-power state, memory power force/disable/state fields, and native-422 memory power force/disable/state fields.
- `DSCC*_DSCC_R_Y/G_CB/B_CR_SQUARED_ERROR_*`, `DSCC*_DSCC_MAX_ABS_ERROR*`, `DSCC*_DSCC_RATE_BUFFER*_MAX_FULLNESS_LEVEL`, and `DSCC*_DSCC_RATE_CONTROL_BUFFER*_MAX_FULLNESS_LEVEL` expose quality/statistics/debug counters for reconstructed-channel error and rate-buffer fullness.
- `DSCC*_DSCC_TEST_DEBUG_BUS_ROTATE` selects and rotates DSCC debug bus output.

`DSCCIF0..2` provides interface-level `DSCCIF_CONFIG0` and `DSCCIF_CONFIG1` fields for DSC pixel-rate/slice-width, DSCCIF enable, status, underrun, block-prediction enable, BPP decrement, and pass-through reporting. `DSC_TOP0..2` provides the top-level DSC reset/clock-enable/disconnect state and debug display selection.

### DC_PERFMON19 Through DC_PERFMON22

The range defines four performance monitor instances:

- `DC_PERFMON19` is associated with the DSC0 address block.
- `DC_PERFMON20` is associated with DSC1.
- `DC_PERFMON21` is associated with DSC2.
- `DC_PERFMON22` is associated with HPO.

Each block follows the same pattern: `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW`. The fields cover counter enable, clear, stop modes, test debug index selection, state/version/read-window status, performance monitor enable/continuous/start modes, clear-on-read and clear-on-start behavior, manual load, windowed trigger masks, low/high current values, and interrupt/status metadata.

### HPO Top And DP Stream Mapper

`HPO_TOP_CLOCK_CONTROL` defines HPO DP stream, link, PHY, HDMI stream, and HDMI character clock gate-disable fields, plus clock-on status readbacks for DP stream/link/PHY, HDMI stream, and HDMI character clocks. `HPO_TOP_HW_CONTROL` exposes `HPO_IO_EN`.

`DP_STREAM_MAPPER_CONTROL0..3` map four stream encoders to DP stream sources through `DP_STREAM_SOURCE_SELECT0..3` fields. These fields are part of the HPO routing path and must match resource-layer stream encoder allocation.

### AFMT5 Audio And Infoframe

`AFMT5` is the audio formatter/infoframe block for stream instance 5. Important field groups include:

- `AFMT5_AFMT_VBI_PACKET_CONTROL` for null, GC, generic stream, ACP, and ISRC packet sending.
- `AFMT5_AFMT_AUDIO_PACKET_CONTROL2` for ACR packet send, layout override, HBR packet behavior, audio channel count, and HBR sample-readiness enable.
- `AFMT5_AFMT_AUDIO_INFO0` and `AFMT5_AFMT_AUDIO_INFO1` for HDMI/DP audio infoframe fields such as CC, CT, checksum offset, CXT, channel allocation, level shift value, downmix inhibit, and LFEPBL.
- `AFMT5_AFMT_60958_0`, `_1`, and `_2` for IEC 60958 channel-status fields: CS A-D, mode, category, source number, sampling frequency, clock accuracy, word length, original sampling frequency, validity bits, and channel numbers.
- `AFMT5_AFMT_AUDIO_CRC_CONTROL` and `AFMT5_AFMT_AUDIO_CRC_RESULT` for audio CRC enable/continuous/source/channel/count and result/done readback.
- `AFMT5_AFMT_RAMP_CONTROL0..3` for audio ramp test generation limits and increment/decrement values.
- `AFMT5_AFMT_STATUS`, `AFMT5_AFMT_AUDIO_PACKET_CONTROL`, `AFMT5_AFMT_INFOFRAME_CONTROL0`, `AFMT5_AFMT_AUDIO_SRC_CONTROL`, and `AFMT5_AFMT_MEM_PWR` for audio enable/HBR/FIFO overflow/change status, sample send, double-buffered sample send, FIFO reset when audio disables, test mode, overflow/change acks, 60958 update, blanking behavior, audio-info source/update, audio source select, and AFMT memory power force/disable/state.

### DME5 And VPG5

`DME5_DME_CONTROL` defines metadata requestor ID, metadata engine enable, stream type, double-buffer pending/taken/clear/disable, metadata transmission missed, and missed-clear fields. `DME5_DME_MEMORY_CONTROL` defines DME memory power force/disable/state and default low-power state.

`VPG5` defines the video packet generator instance used with the same stream family:

- `VPG5_VPG_GENERIC_PACKET_ACCESS_CTRL` and `VPG5_VPG_GENERIC_PACKET_DATA` expose indexed generic packet data bytes.
- `VPG5_VPG_GSP_FRAME_UPDATE_CTRL` provides frame-update request and pending bits for generic packets 0-14.
- `VPG5_VPG_GSP_IMMEDIATE_UPDATE_CTRL` provides immediate-update request and pending bits for generic packets 0-14.
- `VPG5_VPG_GENERIC_STATUS` exposes generic packet lock, conflict occurred, and conflict clear fields.
- `VPG5_VPG_MEM_PWR` controls VPG/GSP memory light sleep and reports memory power state.
- `VPG5_VPG_ISRC1_2_ACCESS_CTRL`, `VPG5_VPG_ISRC1_2_DATA`, `VPG5_VPG_MPEG_INFO0`, and `VPG5_VPG_MPEG_INFO1` define indexed ISRC data bytes and MPEG info checksum/metadata/update fields.

### DP_STREAM_ENC0 And APG0

`DP_STREAM_ENC0` defines the first HPO DP stream encoder's clock, mux, audio, FIFO, and spare fields:

- `DP_STREAM_ENC0_DP_STREAM_ENC_CLOCK_CONTROL` exposes stream encoder clock enable plus clock-on readbacks for DISPCLK, SOCCLK, DPSTREAMCLK, and SYMCLK32.
- `DP_STREAM_ENC0_DP_STREAM_ENC_INPUT_MUX_CONTROL` selects the pixel stream source.
- `DP_STREAM_ENC0_DP_STREAM_ENC_AUDIO_CONTROL` selects the audio stream source.
- `DP_STREAM_ENC0_DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL0` controls FIFO enable/reset, read start level, read clock source, reset done, video stream active, and FIFO error status.
- `DP_STREAM_ENC0_DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL1` controls overwrite/recalculation/recompute behavior and exposes overwrite/min/max/calibrated average level and calibrated status.

The chunk then begins `APG0`, the audio packet generator for HPO DP stream encoder 0. It covers reset/reset-done, APG enable, DP audio stream ID, ASP channel count override, debug generator enable/reset/channel/test-disable fields, ACP/audio-info source selection, audio CRC control/count/default count, and audio CRC done/clear/result readback. `APG0_APG_STATUS`, `APG0_APG_STATUS2`, `APG0_APG_MEM_PWR`, and `APG0_APG_SPARE` follow after this chunk.

## Control Flow

This header has no direct control flow. Runtime flow is supplied by AMDGPU display code:

1. DCN315 source includes `dcn_3_1_5_offset.h` and `dcn_3_1_5_sh_mask.h`.
2. Token-pasting macros such as `SF`, `SR`, `SRI`, and block-specific list macros select a register, shift, and mask by generated name.
3. DCN315 resource construction stores those offsets/shifts/masks in block-specific tables.
4. Display hardware code uses the tables through register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WRITE`, wait/poll helpers, DMUB service tables, GPIO translation, IRQ service code, and stream encoder/audio/DSC abstractions.
5. Hardware latches, reports, clears, or consumes the represented fields according to the block-specific sequencing rules.

The macros do not encode access type, reset value, volatile behavior, double-buffering semantics, clear-on-write behavior, or ordering. Callers must still sequence panel power, backlight PWM updates, DSC PPS programming, DSCCIF enablement, HPO clocking, stream mapper routing, VPG/AFMT/APG packet updates, DME metadata double-buffering, FIFO reset/calibration, memory power transitions, and performance counter capture according to DCN hardware requirements.

## State And Persistence Behavior

No software state is stored by this file. It describes MMIO-backed hardware state whose lifetime is controlled by display hardware, power management, modesets, suspend/resume, resets, and firmware/driver ownership.

Persistent or latched configuration fields include panel power target/override/polarity, GPIO power sequence control, panel timing delays, PWM reference divisors/period/count/enable, DSC PPS parameters, DSCC memory power policy, DSCCIF enable/configuration, DSC top reset/clock/disconnect controls, perfmon configuration, HPO clock gate controls, stream mapper selections, AFMT packet/source/audio-info/60958 controls, DME metadata engine controls, VPG packet data/update controls, DP stream encoder mux/audio/FIFO controls, and APG enable/audio stream/debug/CRC controls.

Volatile readback or status fields include panel state/done, PWM update pending/frame-start recognition, DSCC double-buffer update pending, DSCC overflow/underflow/RC-buffer overflow occurred bits, DSCC error and fullness counters, DSCCIF status/underrun/pass-through status, DSC clock-on/current reset status, perfmon counter values and state readbacks, HPO clock-on and IO status, AFMT audio/FIFO/change status and CRC done/result, DME double-buffer taken/pending and missed-transmission status, VPG update pending/conflict/memory-power state, DP stream encoder clock-on/FIFO reset-done/active/error/calibrated status, and APG reset-done/CRC result.

Side-effecting write fields include reset bits, missed/clear bits, FIFO overflow and change acknowledgements, VPG conflict clear, DME taken/missed clears, APG CRC done clear, perfmon clear/manual load controls, DSCC interrupt enable bits, memory power force/disable fields, PWM lock/update fields, and generic packet frame/immediate update bits. Treating these fields as ordinary persistent booleans can cause lost events, stale status, or unintended hardware state changes.

## Dependencies And Integration Points

This chunk depends on the matching generated offset header at `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`. For the visible field families, that header supplies offsets and base indices for registers such as `regPWRSEQ1_PANEL_PWRSEQ_CNTL`, `regDSCC0_DSCC_PPS_CONFIG0`, `regDSCC2_DSCC_INTERRUPT_CONTROL_STATUS`, `regHPO_TOP_CLOCK_CONTROL`, `regDP_STREAM_MAPPER_CONTROL0`, `regAFMT5_AFMT_AUDIO_PACKET_CONTROL`, `regDME5_DME_CONTROL`, `regVPG5_VPG_GSP_FRAME_UPDATE_CTRL`, `regDP_STREAM_ENC0_DP_STREAM_ENC_CLOCK_CONTROL`, and `regAPG0_APG_CONTROL`.

Known direct include sites for the DCN 3.1.5 generated headers are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`, which includes the offset and mask headers for DMUB register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`, which includes them for DCN315 IRQ service register definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c` and `hw_translate_dcn315.c`, which include them for GPIO register translation and factory setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which builds many of the runtime register/shift/mask tables.

The strongest source-tree integration points visible for this chunk are in `dcn315_resource.c`:

- `vpg_regs[]`, `vpg_shift`, and `vpg_mask` use `VPG_DCN31_REG_LIST(id)` and `DCN31_VPG_MASK_SH_LIST(...)`; this covers VPG instances including `VPG5` and HPO-related `VPG6..9`.
- `afmt_regs[]`, `afmt_shift`, and `afmt_mask` use `AFMT_DCN31_REG_LIST(id)` and `DCN31_AFMT_MASK_SH_LIST(...)`; this covers AFMT instances 0-5, including the `AFMT5` fields in this range.
- `apg_regs[]`, `apg_shift`, and `apg_mask` use `APG_DCN31_REG_LIST(id)` and `DCN31_APG_MASK_SH_LIST(...)`; this covers APG instances 0-3, including `APG0`.
- `hpo_dp_stream_enc_regs[]`, `hpo_dp_se_shift`, and `hpo_dp_se_mask` use `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST(id)` and `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST(...)`; this covers `DP_STREAM_ENC0`.
- `dsc_regs[]`, `dsc_shift`, and `dsc_mask` use `DSC_REG_LIST_DCN20(id)` and `DSC_REG_LIST_SH_MASK_DCN20(...)`; this covers DSC instances 0-2.
- `hwseq_reg`, `hwseq_shift`, and `hwseq_mask` include `HPO_TOP_HW_CONTROL`, `HPO_TOP_CLOCK_CONTROL__HPO_HDMISTREAMCLK_G_GATE_DIS`, and `HPO_TOP_HW_CONTROL__HPO_IO_EN`.
- HPO DP stream encoder creation maps HPO DP stream instances to VPG and APG subblocks: `VPG[6] -> HPO_DP[0]` through `VPG[9] -> HPO_DP[3]`, and `APG[0] -> HPO_DP[0]` through `APG[3] -> HPO_DP[3]`. This is important context for the `DP_STREAM_ENC0` and `APG0` fields in this range.

Other integration is indirect through common display block implementations for DSC, VPG, AFMT, APG, HPO DP stream encoders, hardware sequencing, audio, GPIO, IRQ handling, DMUB, diagnostics, and power management. The repeated generated names also align with nearby DCN 3.1.x and later generated headers, so mechanical regeneration and cross-revision comparison are normal maintenance tools.

## Risks And Edge Cases

- Bitfield drift is the primary risk. A wrong numeric shift or mask can compile but corrupt the wrong hardware field at runtime.
- The chunk has artificial boundaries. It starts in the middle of `PWRSEQ0_BL_PWM_GRP1_REG_LOCK` and ends before the end of `APG0`; neighboring chunks are required for full file-level conclusions about those registers.
- `PWRSEQ1` fields are timing-sensitive. Incorrect target state, override, polarity, delay, reference divider, PWM period, or lock/update-pending handling can break panel power sequencing, backlight behavior, or frame-synchronized PWM updates.
- GPIO power sequence fields are easy to confuse because VARY_BL, DIGON, and BLON fields share the same register shapes. A valid mask can still target the wrong panel signal.
- DSC PPS fields are dense and standards-driven. Mistakes in BPP, chunk size, slice geometry, RC model, thresholds, QP range, BPG offset, or native 4:2:2/4:2:0 flags can produce visual corruption, link bandwidth mismatch, sink rejection, or failures limited to compressed display modes.
- DSCC interrupt/status fields combine occurred bits and interrupt-enable bits in one namespace. Maintenance must preserve status versus enable semantics.
- DSCCIF and DSC_TOP enable/reset/underrun fields are sequencing-sensitive around modesets and stream enablement. Polling the wrong status bit can hide an underrun or release reset too early.
- Perfmon registers are diagnostic but stateful. Clear-on-read, clear-on-start, windowing, manual load, and counter selection fields can make performance data misleading if masks drift.
- HPO clock gate and stream mapper fields sit on display routing and clocking paths. Incorrect masks can leave clocks gated, route a stream to the wrong encoder, or make HPO IO unavailable.
- AFMT, VPG, DME, and APG packet/control fields are packetization and metadata surfaces. Wrong update, pending, clear, source, or data-index fields can drop HDMI/DP audio packets, generic packets, ISRC/MPEG info, dynamic metadata, or infoframe updates while leaving the display link otherwise active.
- `VPG5` has both frame-update and immediate-update request/pending fields for generic packets 0-14. Confusing request and pending bits or frame versus immediate update can produce stale packet data or update conflicts.
- DP stream encoder FIFO fields expose both control and calibrated/status values. Reset/calibration/read-level mistakes can cause underflow, FIFO error, or stream instability during clock ramping.
- Generated fields whose hardware names include `MASK` can produce names ending in `_MASK_MASK` in other chunks. Cleanup scripts should not normalize generated names by hand.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU Display Core with DCN315 enabled. Missing, malformed, or renamed macros should fail in `dcn315_resource.c`, `irq_service_dcn315.c`, `dmub_dcn315.c`, GPIO translation, or common block headers that expand the generated names.
- Mechanically compare this range against a regenerated `dcn_3_1_5_sh_mask.h` or the authoritative DCN 3.1.5 register database, checking every shift/mask pair and preserving boundary partials.
- Cross-check against adjacent DCN 3.1.x generated headers where hardware is expected to be compatible, while treating DCN315-specific instance counts and offsets as authoritative.
- Exercise panel power and backlight on DCN315 hardware: power on/off, suspend/resume, brightness changes, PWM fractional mode, frame-start PWM updates, and no stuck update-pending or incorrect GPIO signal states.
- Exercise DSC on all three instances with compressed display modes, multiple slice counts, native RGB and YCbCr formats, DSC disable/enable transitions, underrun handling, and DSC PPS readback/register dumps.
- Validate HPO DP stream creation and routing, including HPO top clock enablement, stream mapper selection, DP stream encoder clock status, pixel/audio mux selection, FIFO reset/calibration, and multi-stream configurations.
- Test HDMI/DP audio and packet paths for AFMT/VPG/APG: audio playback, HBR and channel-count modes, IEC 60958 status updates, audio infoframe updates, ACR/sample packet send, generic packet frame/immediate updates, ISRC/MPEG packet data, CRC result paths, and FIFO overflow/change acknowledgements.
- Test DME metadata updates, including double-buffer pending/taken behavior and missed-transmission clear paths during HDR/dynamic metadata changes.
- Use perfmon/debug tests to confirm DC_PERFMON19-22 counter programming, clear behavior, readback windows, and source selection remain meaningful after changes.
- Inspect runtime register dumps before and after operations. Packed writes should only affect bits covered by the intended mask and should preserve unrelated fields.

## Cross-Chunk Notes

The previous chunk owns the beginning of `PWRSEQ0_BL_PWM_GRP1_REG_LOCK`; this chunk should not be treated as the complete `PWRSEQ0` story. The next chunk owns the rest of `APG0`, starting with status, output-active, memory-power, and spare definitions. The final merged report for `dcn_3_1_5_sh_mask.h` should reconcile these artificial boundaries and avoid claiming complete PWRSEQ0 or APG0 coverage from this chunk alone.

### subset-b-001884: lines 47146-49525

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 47146-49525

## Scope

This chunk is a generated AMD DCN 3.1.5 register-field shift/mask slice. It contains C preprocessor constants only: `_SHIFT` macros for field low-bit positions, `_MASK` macros for raw register bit masks, register-name comments, and address-block comments. There are no functions, structs, enums, branches, loops, allocations, locks, or driver-owned state containers in this range.

The slice starts at the `APG0` audio packet generator status/memory-power tail, then defines the HPO DisplayPort stream encoder instance 0 metadata engine (`DME6`), video packet generator (`VPG6`), and full `DP_SYM32_ENC0` field layout. It continues through full HPO stream encoder instance 1 coverage (`DP_STREAM_ENC1`, `APG1`, `DME7`, `VPG7`, `DP_SYM32_ENC1`) and then begins instance 2 (`DP_STREAM_ENC2`, `APG2`, `DME8`, `VPG8`, and the opening `DP_SYM32_ENC2` fields). The chunk ends inside `DP_SYM32_ENC2_DP_SYM32_ENC_SDP_AUDIO_CONTROL1`; the remainder of instance 2 is in the next chunk.

## Purpose And Hardware Surface

The purpose of this header range is to publish the bit-layout ABI between AMDGPU Display Core code and DCN 3.1.5 HPO DisplayPort hardware. The matching `dcn_3_1_5_offset.h` header supplies register addresses and base indices; this file supplies the field masks and shifts used by register helper macros to pack writes and decode readbacks.

Major hardware areas represented here:

- `APG0`, `APG1`, and `APG2` audio packet generator fields for audio enable/HBR status, FIFO overflow status and clear, output-active status, memory power control, packet/debug/audio CRC control, and spare registers.
- `DME6`, `DME7`, and `DME8` metadata engines for HPO stream encoders. They expose metadata HUBP requestor IDs, engine enable, stream type, double-buffer pending/taken status, clear/disable bits, missed-transmission status/clear bits, and DME memory power controls.
- `VPG6`, `VPG7`, and `VPG8` video packet generators. They define generic packet data-index/data-byte windows, frame-update and immediate-update controls for generic slots 0-14, lock/conflict status, memory power fields, ISRC data windows, and MPEG infoframe words.
- `DP_STREAM_ENC1` and `DP_STREAM_ENC2` stream encoder front-end fields for clock gate/enable controls, stream source muxing, audio stream selection, clock ramp adjuster FIFO status, and spare fields.
- `DP_SYM32_ENC0`, `DP_SYM32_ENC1`, and the beginning of `DP_SYM32_ENC2` symbol encoders for HPO DP video, secondary data packets, audio packets, metadata packets, CRC, and memory power.

This is hardware-definition data rather than active logic. Its correctness matters because the display stack treats these constants as the source of truth for MMIO field packing on DCN 3.1.5.

## Important Definitions

The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask within the 32-bit register.
- `//<REGISTER>` comments group macros by hardware register.
- `// addressBlock: ...` comments identify the hardware aperture for the following register group.

Important field families in this chunk:

- `APG*_APG_STATUS`, `APG*_APG_STATUS2`, `APG*_APG_MEM_PWR`, and `APG*_APG_SPARE` expose audio packet generator status and power-management fields. Instance 0 begins in the previous chunk, while instances 1 and 2 include their control, debug, packet, CRC, status, power, and spare groups here.
- `APG*_APG_CONTROL` and `APG*_APG_CONTROL2` define reset/reset-done, APG enable, DP audio stream ID, channel-count override, HBR audio stream ID, and layout override fields for instances 1 and 2.
- `APG*_APG_DBG_GEN_CONTROL`, `APG*_APG_PACKET_CONTROL`, `APG*_APG_AUDIO_CRC_CONTROL`, `APG*_APG_AUDIO_CRC_CONTROL2`, and `APG*_APG_AUDIO_CRC_RESULT` define debug audio generation, audio info source selection, CRC enable/continuous/channel/count programming, CRC done/clear, and 16-bit CRC result fields.
- `DME*_DME_CONTROL` packs metadata routing and state fields: `METADATA_HUBP_REQUESTOR_ID`, `METADATA_ENGINE_EN`, `METADATA_STREAM_TYPE`, `METADATA_DB_PENDING`, `METADATA_DB_TAKEN`, `METADATA_DB_TAKEN_CLR`, `METADATA_DB_DISABLE`, `METADATA_TRANSMISSION_MISSED`, and `METADATA_TRANSMISSION_MISSED_CLR`.
- `DME*_DME_MEMORY_CONTROL` exposes DME memory power force, disable, state, and default low-power-state fields.
- `VPG*_VPG_GENERIC_PACKET_ACCESS_CTRL` and `VPG*_VPG_GENERIC_PACKET_DATA` define the indexed generic packet payload window with 8-bit index and four 8-bit data-byte fields.
- `VPG*_VPG_GSP_FRAME_UPDATE_CTRL` and `VPG*_VPG_GSP_IMMEDIATE_UPDATE_CTRL` define generic packet slot update triggers for slots 0-14 and corresponding pending bits at bits 16-30.
- `VPG*_VPG_GENERIC_STATUS` exposes generic packet lock status, conflict status, and conflict clear fields. `VPG*_VPG_MEM_PWR` exposes VPG GSP memory light-sleep disable, force, and state fields.
- `VPG*_VPG_ISRC1_2_ACCESS_CTRL`, `VPG*_VPG_ISRC1_2_DATA`, `VPG*_VPG_MPEG_INFO0`, and `VPG*_VPG_MPEG_INFO1` provide ISRC and MPEG packet data windows, checksum and payload-byte fields, update flags, and frame-rate/mode metadata.
- `DP_SYM32_ENC*_DP_SYM32_ENC_CONTROL` defines enable, reset, and reset-done bits for symbol encoder instances.
- `DP_SYM32_ENC*_DP_SYM32_ENC_VID_FIFO_CONTROL` defines pixel-to-symbol FIFO enable/reset/reset-done and overflow status bits.
- `DP_SYM32_ENC*_DP_SYM32_ENC_VID_PIXEL_FORMAT` and its double-buffer control define pixel encoding type, uncompressed encoding, component depth, double-buffer enable, and pending status.
- `DP_SYM32_ENC*_DP_SYM32_ENC_VID_MSA0` through `VID_MSA8` expose full 32-bit MSA data words. `VID_MSA_CONTROL` and `VID_MSA_DOUBLE_BUFFER_CONTROL` add line-number/SOF control and double-buffer enable/pending fields.
- `DP_SYM32_ENC*_DP_SYM32_ENC_HBLANK_CONTROL` defines the minimum hblank symbol width.
- `DP_SYM32_ENC*_DP_SYM32_ENC_SDP_GSP_CONTROL0` through `CONTROL14` repeat a common layout for 15 generic secondary data packet slots: video-continuous enable, idle-continuous enable, one-shot trigger, one-shot position, double-buffer enable, payload size, SOF reference, deadline missed, transmission pending, double-buffer pending, and 16-bit transmission line number.
- `DP_SYM32_ENC*_DP_SYM32_ENC_SDP_CONTROL` exposes SDP stream enable, GSP0 priority, and CRC16 enable fields.
- `DP_SYM32_ENC*_DP_SYM32_ENC_SDP_AUDIO_CONTROL0` exposes ASP/ATP/AIP/ACM/ISRC enables, ASP priority, ATP version number, audio mute, and audio mute status. `SDP_AUDIO_CONTROL1` adds ASP concatenation enable and max sample-count fields for 2-channel, 8-channel, and HBR layouts.
- For instances fully covered in this chunk, later `DP_SYM32_ENC*` fields define metadata packet control, MSA/VBID line controls, stream enable/status/deferred-disable, panel replay tunneling optimization, video CRC enable/results/status, memory power control, and spare fields. For instance 2, those later groups continue in the next chunk.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when AMDGPU Display Core and DMUB code combine these constants with matching `reg*` offsets and register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, generated `SE_SF` field tables, or `DMUB_SF` field tables.

A typical use path is:

1. Select a DCN 3.1.5 register address and base index from `dcn_3_1_5_offset.h`.
2. Select the matching field mask and shift from this header.
3. Pack a value, decode a readback, or build a read/modify/write operation through the display register abstraction.
4. Let hardware latch, report, clear, or consume the field.

The state represented here is hardware state:

- Persistent configuration fields include APG enable/audio stream selection/debug generation, DME metadata routing and memory-power controls, VPG packet data and update controls, stream encoder source muxing, DP symbol encoder enable, video pixel format, MSA contents, VBID control, SDP/GSP transmission mode, audio packet enables, metadata packet control, panel replay optimization, CRC mode, and memory power policy.
- Volatile readback fields include reset-done, APG output-active, FIFO overflow, CRC done/result, DME double-buffer pending/taken and missed-transmission status, VPG update-pending/lock/conflict status, stream enable/status, audio mute status, CRC valid/result words, and memory-power state readbacks.
- Side-effecting write fields include reset bits, clear bits such as APG FIFO overflow clear, APG CRC done clear, DME double-buffer taken clear, DME missed-transmission clear, VPG conflict clear, generic packet update triggers, immediate-update triggers, one-shot GSP sends, and CRC enable/continuous mode controls.
- Double-buffered state appears repeatedly in DME metadata, VPG generic packet update controls, MSA and pixel-format controls, GSP packet controls, and metadata packet controls. Callers must respect frame/SOF timing and pending-bit semantics; those sequencing rules are not encoded in the macros.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.5 register-address definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`.

Known integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`, which includes `dcn_3_1_5_offset.h` and this header to build DMUB register offset/mask/shift tables through `DMUB_DCN315_FIELDS()`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`, which includes the DCN315 generated offset and mask headers for interrupt service register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h` and `.c`, whose HPO DP stream encoder register and mask/shift lists use `DP_SYM32_ENC0_*` field names for generic register-field table construction. Those tables are later instanced by resource code for concrete HPO stream encoder instances.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h` and `.c`, which define APG register lists and mask/shift lists such as `APG0_APG_CONTROL`, `APG0_APG_CONTROL2`, `APG0_APG_DBG_GEN_CONTROL`, and `APG0_APG_MEM_PWR`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h` and `.c`, plus resource-list macros such as `VPG_DCN3_REG_LIST_RI`, which map VPG generic packet and update-control fields into per-instance VPG objects.
- DCN31/DCN314/DCN316/DCN32/DCN35/DCN36/DCN321/DCN401 resource code patterns that allocate HPO stream encoders and map VPG, APG, DME, and DP_SYM32 register blocks to HPO DP instances. The common mapping pattern is VPG6/APG0/DME6/SYM32_ENC0 for HPO DP instance 0, VPG7/APG1/DME7/SYM32_ENC1 for instance 1, and VPG8/APG2/DME8/SYM32_ENC2 for instance 2.
- Display audio, generic SDP/infoframe, DP metadata, panel replay, CRC diagnostics, and HPO stream programming paths that indirectly consume these fields through the above register tables.

Because the header is generated, most use is indirect. A missing or misspelled macro usually fails compilation through `SE_SF`, `SRI`, `SRI_ARR`, `REG_FIELD`, or `DMUB_SF` expansion. A wrong numeric mask or shift can compile cleanly and cause runtime MMIO misprogramming.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.5 register database is the main risk. Incorrect masks or shifts can corrupt HPO DP stream setup, packet scheduling, metadata routing, audio packet generation, CRC diagnostics, or memory-power programming.
- This chunk starts in the middle of the APG0 register family and ends in the middle of the DP_SYM32_ENC2 audio-control family. The merge lane must combine adjacent chunks before making complete statements about APG0 or DP_SYM32_ENC2.
- The instance numbering is easy to confuse: APG instances use 0/1/2 while DME and VPG instances use 6/7/8 for the same HPO stream encoder slots. A valid macro for the wrong instance can compile and target the wrong hardware block.
- GSP controls are highly repetitive across slots 0-14 and across DP_SYM32 instances. Copy/paste mistakes among GSP slot numbers, pending bits, line-number fields, and payload-size fields are difficult to catch by type checking.
- Clear bits share registers with status bits. APG FIFO overflow clears, APG CRC done clears, DME status clears, and VPG conflict clears must be treated as write-side effects rather than normal persistent configuration.
- Double-buffer and SOF/line-number controls are timing-sensitive. Incorrect update ordering can leave pending bits set, miss a desired frame boundary, or transmit stale metadata/infoframes.
- Audio packet fields combine ASP/ATP/AIP/ACM/ISRC enables, mute state, HBR stream IDs, version fields, and concatenation sample-count limits. Wrong bit packing may produce silent audio failures or malformed display-audio packets.
- CRC and diagnostic fields can be mistaken for production data-path controls. CRC enable/continuous mode and result clear/status fields should be isolated to validation and debug flows.
- Memory power controls for APG, DME, VPG, and DP_SYM32 blocks expose force/disable/state fields. Writes must be coordinated with stream enable/disable sequencing so register accesses do not race a powered-down block.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Compile coverage for AMDGPU Display Core with DCN 3.1.5 enabled. This catches missing macro names, malformed generated constants, and broken macro syntax.
- Static comparison against the authoritative DCN 3.1.5 register database or a regenerated `dcn_3_1_5_sh_mask.h`, especially for instance numbering, repeated GSP slot fields, audio packet fields, and clear/status masks.
- Cross-revision spot checks against nearby generated headers such as DCN 3.1.4, 3.1.6, 3.2.0, and 3.5.1 where HPO DP register layout is expected to remain compatible, while preserving intentional DCN315 differences.
- HPO DP functional testing on DCN 3.1.5 hardware: stream enable/disable, pixel format changes, MSA programming, VBID/compressed-stream signaling, panel replay tunneling optimization, and link stability at expected modes.
- Generic SDP/infoframe testing: VPG packet payload writes through index/data windows, frame-update and immediate-update triggers, GSP packet scheduling by line/SOF, metadata packet double-buffering, and pending bits clearing after frame boundaries.
- Display audio testing: APG enable/disable, stream ID selection, HBR paths, audio mute/unmute, ASP/ATP/AIP/ACM/ISRC packet transmission, and audio CRC done/result behavior.
- Metadata engine testing for DME6/DME7/DME8: HUBP requestor routing, metadata enable/disable, double-buffer taken/pending behavior, missed-transmission detection, and clear-bit behavior.
- Runtime register dumps around HPO stream setup, packet updates, audio changes, CRC reads, and power transitions. Packed values should affect only the intended masked bits and preserve unrelated fields.

## Open Questions For Merge

- The exact DCN315 resource constructor mapping for HPO stream encoder instances is outside this generated header and should be reconciled with resource chunks before final per-file claims.
- Later chunks complete `DP_SYM32_ENC2` and likely continue additional HPO stream/link/audio definitions. The final per-file document should avoid treating this chunk as complete coverage of all HPO DP instance 2 fields.

### subset-b-001885: lines 49526-52127

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 49526-52127

## Scope

This chunk is a large middle/tail slice of the generated DCN 3.1.5 register-field shift/mask header `dcn_3_1_5_sh_mask.h`. It contains C preprocessor constants only: `_SHIFT` macros for field low-bit positions, `_MASK` macros for raw register masks, register grouping comments, and `addressBlock` grouping comments. There are no functions, structs, enums, allocations, branches, loops, locks, or driver-owned state objects in this range.

The slice starts in the tail of `DP_SYM32_ENC2` sideband/audio/video stream definitions and then covers the third HPO DisplayPort stream encoder stack, the third HPO DP symbol encoder, two HPO DP link/DPHY symbol blocks, DCHVM host-VM fields, display HDA/Azalia controller and stream descriptor fields, several RSMU empty address blocks, DC perfmon debug fields, legacy VGA indexed registers, writeback/debug fields, and the beginning of DPG3 debug fields. The span contains 2,087 `#define` lines across 386 register groups.

## Purpose And Hardware Surface

The purpose of this header range is to provide the bit-layout ABI between AMDGPU Display Core code and DCN 3.1.5 display hardware. Companion offset headers, especially `dcn_3_1_5_offset.h`, map register names to MMIO offsets and base indices; this file maps register fields to bit shifts and masks. Display code combines both pieces through generated register-list macros and helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WAIT`, `SE_SF`, `HUBBUB_SF`, `SF`, and `DMUB_SF`.

Major hardware areas represented here:

- `DP_SYM32_ENC2_*` tail fields for symbol encoder 2 metadata sideband packets, MSA/VBID timing, video stream enable/status, panel replay tunneling, video CRC, and encoder memory power.
- `dce_dc_hpo_dp_stream_enc3_dispdec` fields for HPO DP stream encoder 3 clock gating, pixel/audio input muxing, and clock-ramp-adjuster FIFO control/status.
- `dce_dc_hpo_dp_stream_enc3_apg_apg_dispdec`, `dme_dme_dispdec`, and `vpg_vpg_dispdec` fields for APG3 audio packet generation, DME9 metadata engine state, and VPG9 generic sideband packet storage/update.
- `dce_dc_hpo_dp_sym32_enc3_dispdec` fields for DP symbol encoder 3: enable/reset, pixel-to-symbol FIFO, MSA and pixel format double buffering, MSA payload words, generic sideband packet controls 0-14, audio/metadata sideband controls, video stream controls, CRC, and memory power.
- `dce_dc_hpo_dp_link_enc0/1_dispdec` and `dce_dc_hpo_dp_dphy_sym320/321_dispdec` fields for HPO DP link clocks, DPHY control/status, virtual-channel rate/slot allocation, training pattern generation, PRBS/custom patterns, error status, symbol override, and DPHY CRC.
- `dce_dc_dchvm_hvm_dispdec` fields for host-VM initialization, memory power request/status, clock gating request modes, RIOMMU prefetch/power state, and RIOMMU status.
- `dce_dc_hda_azcontroller_azdec`, endpoint, input endpoint, root, and stream blocks for display HDA/Azalia CORB/RIRB rings, immediate command/response paths, DMA position buffer address, and output stream descriptors 0-7.
- `dc_perfmon_dc_perfmondebugind`, `vga_*`, `mcif_wb0_mcif_wbdebugind`, and `dpg*_dpgdebugind` fields for debug/perfmon, legacy VGA sequencing/CRTC/graphics/attribute registers, writeback debug windows, and DPG debug registers.

The file is hardware-definition data rather than active logic. Its values are still runtime-critical because callers rely on these macros to preserve unrelated register bits while programming display link, audio, packet, power, VM, and debug state.

## Important Definitions

The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register-native position.
- `//<REGISTER>` comments group adjacent field macros by register.
- `// addressBlock: ...` comments group following registers by hardware aperture.

Important field families in this chunk:

- `DP_SYM32_ENC2_DP_SYM32_ENC_SDP_METADATA_PACKET_CONTROL` exposes metadata packet enable, double-buffer enable, SOF reference, double-buffer pending, and transmission line number. The preceding `DP_SYM32_ENC2` GSP/audio fields are partly in the previous chunk, so this chunk begins mid encoder-2 sideband coverage.
- `DP_SYM32_ENC2_DP_SYM32_ENC_VID_MSA_CONTROL`, `VID_VBID_CONTROL`, `VID_STREAM_CONTROL`, and `VID_PANEL_REPLAY_CONTROL` cover MSA line scheduling, compressed-stream VBID line scheduling, video stream enable/deferred-disable/status, and panel replay tunneling optimization.
- `DP_SYM32_ENC2_DP_SYM32_ENC_VID_CRC_*` expose video CRC enable/continuous mode, four 16-bit result fields, and a valid bit. `DP_SYM32_ENC2_DP_SYM32_ENC_MEM_POWER_CONTROL` exposes default low-power state, force, disable, and current power state fields.
- `DP_STREAM_ENC3_DP_STREAM_ENC_CLOCK_CONTROL` exposes the stream encoder clock enable and readback/status bits for DISPCLK, SOCCLK, DPSTREAMCLK, and SYMCLK32. `INPUT_MUX_CONTROL` and `AUDIO_CONTROL` select pixel and audio stream sources.
- `DP_STREAM_ENC3_DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL0/1` expose FIFO enable/reset/read start level/read clock source, reset done, active-stream, error, overwrite level, recalibration/recompute triggers, min/max/calibrated levels, and average calibration state.
- `APG3_APG_CONTROL` and `APG3_APG_CONTROL2` expose APG reset/done, APG enable, DP audio stream ID, and ASP channel-count override. `APG3_APG_DBG_GEN_CONTROL` configures debug audio generation and per-channel test enable/disable. `APG3_APG_PACKET_CONTROL` chooses packet/audio info sources.
- `APG3_APG_AUDIO_CRC_CONTROL`, `CONTROL2`, and `RESULT` expose audio CRC enable/continuous mode/channel selection/count, default forced count, done/done-clear, and 16-bit CRC result. `APG3_APG_STATUS` exposes audio enable, HBR enable, FIFO overflow status, and overflow clear. `APG3_APG_MEM_PWR` mirrors the common memory power disable/force/state/default low-power pattern.
- `DME9_DME_CONTROL` covers metadata hubp requestor ID, engine enable, stream type, double-buffer pending/taken/taken-clear, DB disable, transmission missed, and missed-clear. `DME9_DME_MEMORY_CONTROL` covers DME memory power force/disable/state/default low-power.
- `VPG9_VPG_GENERIC_PACKET_ACCESS_CTRL` and `VPG9_VPG_GENERIC_PACKET_DATA` provide indexed byte access to generic sideband packet RAM. `VPG9_VPG_GSP_FRAME_UPDATE_CTRL` and `IMMEDIATE_UPDATE_CTRL` contain update bits and pending bits for generic packet slots 0-14. `VPG9_VPG_GENERIC_STATUS` exposes lock/conflict status and conflict clear. `VPG9_VPG_ISRC1_2_*` and `VPG9_VPG_MPEG_INFO*` expose indexed ISRC bytes and MPEG infoframe bytes/update bits.
- `DP_SYM32_ENC3_DP_SYM32_ENC_CONTROL`, `VID_FIFO_CONTROL`, `VID_MSA_DOUBLE_BUFFER_CONTROL`, `VID_PIXEL_FORMAT_DOUBLE_BUFFER_CONTROL`, and `VID_PIXEL_FORMAT` define symbol encoder 3 enable/reset, FIFO reset/done/overflow, MSA/pixel-format DB enable/pending, pixel encoding type, uncompressed encoding, and component depth.
- `DP_SYM32_ENC3_DP_SYM32_ENC_VID_MSA0..8` provide full 32-bit MSA payload data words. `DP_SYM32_ENC3_DP_SYM32_ENC_HBLANK_CONTROL` exposes minimum hblank symbol width.
- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL0..14` repeat the same generic sideband control layout per packet slot: video/idle continuous transmission, one-shot trigger and position, double-buffer enable, payload size, SOF reference, missed-deadline status, trigger pending, double-buffer pending, and 16-bit transmission line number.
- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_CONTROL` exposes SDP stream enable, GSP0 priority, and CRC16 enable. `SDP_AUDIO_CONTROL0/1` expose ASP/ATP/AIP/ACM/ISRC enables, ASP priority, ATP version, audio mute/status, ASP concatenation enable, and sample count limits for 2-channel, 8-channel, and HBR layouts.
- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_METADATA_PACKET_CONTROL`, `VID_MSA_CONTROL`, `VID_VBID_CONTROL`, `VID_STREAM_CONTROL`, `VID_PANEL_REPLAY_CONTROL`, `VID_CRC_*`, and `MEM_POWER_CONTROL` mirror the encoder-2 tail fields for encoder 3.
- `DP_LINK_ENC0/1_DP_LINK_ENC_CLOCK_CONTROL` expose HPO link encoder clock enable and SYMCLK32 clock-on status. The associated `SPARE` registers are full-width fields.
- `DP_DPHY_SYM320/321_DP_DPHY_SYM32_CONTROL` expose DPHY enable/reset, precoder enable, mode, and lane count. `STATUS` exposes active/reset status, current mode, encryption enabled, rate update pending, and SAT update pending.
- `DP_DPHY_SYM320/321_DP_DPHY_SYM32_VC_RATE_CNTL0..3`, `SAT_VC0..3`, and `SAT_VC_STATUS0..3` define stream virtual channel rate X/Y values, stream source selection, encryption enable/type, and slot count for four virtual channels.
- `DP_DPHY_SYM320/321_DP_DPHY_SYM32_TP_CONFIG`, `TP_PRBS_SEED0..3`, `TP_SQ_PULSE`, and `TP_CUSTOM0..10` define training-pattern selection, PRBS selection/seeds, square-pulse width, and custom symbol patterns.
- `DP_DPHY_SYM320/321_DP_DPHY_SYM32_ERROR_STATUS`, `SYMBOL_OVERRIDE`, and `CRC_*` expose link-level error flags, per-stream symbol override controls, CRC enable/reset/source/start/end/length configuration, CRC done/value, and symbol count.
- `DCHVM_CTRL0`, `DCHVM_CTRL1`, `DCHVM_CLK_CTRL`, `DCHVM_MEM_CTRL`, `DCHVM_RIOMMU_CTRL0`, and `DCHVM_RIOMMU_STAT0` expose host-VM init, memory power requests/status, DISPCLK/DCFCLK clock gate disables, request/response clock request modes, host-VM prefetch request/power status, RIOMMU active, and prefetch done.
- HDA/Azalia controller fields include `CORB_*` write/read pointers, ring reset/control/status/size; `RIRB_*` lower/upper base address, write pointer/reset, response interrupt count, control/status/size; immediate command output/data/index, immediate response input, command busy/result-valid, and DMA position buffer base address/enable.
- `AZENDPOINT_*`, `AZINPUTENDPOINT_*`, and `AZROOT_*` immediate command data/index fields provide endpoint/root windows into codec command paths.
- `AZSTREAM0..7_OUTPUT_STREAM_DESCRIPTOR_*` repeat the HDA output stream descriptor layout: stream reset/run, interrupt enables, stripe control, traffic priority, stream number, FIFO/descriptor error status, FIFO ready, link position, cyclic buffer length, last valid index, FIFO size, audio format, BDL lower/upper base address, and link position alias.
- `PERFMON_DEBUG_ID` and `PERFMON_DEBUG01..12` expose debug index/data fields and control-like bits such as `PERFMON_TEST_DEBUG_INDEX`, `PERFMON_TEST_DEBUG_DATA`, `TEST_DEBUG_OUT_EN`, and timeout/counter fields in `PERFMON_DEBUG12`.
- `SEQ00..04`, `CRT00..22`, `GRA00..08`, and `ATTR00..14` define legacy VGA sequencer, CRTC, graphics, and attribute indexed-register bit fields. These include reset/clocking, map mask, character/font select, memory mode, CRTC timing/cursor/start-address/line-compare, graphics set/reset/read/write/mode, and attribute palette/mode/color-select fields.
- `VGADCC_DBG_DCCIF_C`, `IDDCCIF*_DBG_DCCIF_*`, `MCIF_WB_DEBUG_ID`, `ID*_WB_*`, `DPG0..3_DPG_DEBUG*`, and `FMT0/1_FMT_DEBUG*` are debug/index windows. Many expose only a single shift at bit 0 because the full register payload is consumed as debug data by external debug selection logic.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when DCN 3.1.5 display code combines these constants with offsets and base indices from `dcn_3_1_5_offset.h` and routes them through AMD Display Core register helpers.

A typical use path is:

1. A hardware block implementation selects a register address and base index from the generated offset header.
2. The block's field-list macro expands a shift/mask pair from this header into a register descriptor table.
3. Code calls a helper such as `REG_UPDATE`, `REG_SET`, `REG_GET`, or `REG_WAIT`.
4. The helper packs, masks, reads, modifies, writes, polls, or decodes the actual MMIO register field.

The represented state is hardware state:

- Persistent configuration fields include stream/audio/pixel mux selection, stream enable, packet enable, double-buffer enable, packet transmission line numbers, APG audio stream ID, debug generator controls, DME/VPG/APG memory power policy, DPHY mode/lane count, VC rates, SAT slot allocations, HDA ring bases/sizes/control bits, HDA stream descriptor format and BDL addresses, DCHVM clock/memory control, legacy VGA mode/timing fields, and perf/debug selection.
- Volatile readback fields include stream status, FIFO reset done/error/active/calibrated states, double-buffer pending, trigger pending, missed-deadline flags, APG CRC done/result, APG FIFO overflow, DME DB taken/transmission missed, VPG update pending/conflict, DPHY current mode/rate/SAT pending/error/CRC status, RIOMMU active/prefetch done, HDA busy/result-valid/FIFO-ready/error, CORB/RIRB status, and debug payload registers.
- Side-effecting write fields include reset bits, done-clear/status-clear bits, APG audio CRC done clear, APG FIFO overflow clear, DME DB taken clear, metadata missed clear, VPG conflict clear, HDA CORB/RIRB resets, immediate command output windows, stream reset/run bits, and DPHY CRC reset.
- Double-buffer and pending semantics are a recurring theme. Metadata, MSA, pixel format, generic sideband packets, and encoder packet controls expose enable/pending bits, so software must write in the order expected by the display hardware and usually coordinate with stream timing, vblank, or packet update boundaries.

The macros do not encode sequencing constraints. Callers must still know whether a bit is write-one-to-clear, read-only, latched at frame start, double-buffered, power-gated, indexed through an access/data register pair, or valid only while a link/audio engine is enabled.

## Dependencies And Integration Points

This chunk depends on the matching register-offset definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`. The shift/mask names here are useful only when paired with the corresponding `reg*`/base-index definitions for the same DCN revision.

Known source integration points for this exact DCN 3.1.5 header include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`, which includes `dcn_3_1_5_offset.h` and `dcn_3_1_5_sh_mask.h` to build the DCN 3.1.5 DMUB register interface.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`, which includes the same generated headers for interrupt service register definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which includes this header while constructing the DCN 3.1.5 resource pool and display objects, including stream encoders.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c` and `hw_translate_dcn315.c`, which include this header for GPIO/DDC/AUX-related register translation and construction.

Related cross-revision consumers show how the field families in this chunk are normally used:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.h` and `.c` use `SE_SF` field lists and `REG_UPDATE`, `REG_GET`, and `REG_SET` flows for HPO DP link/DPHY fields such as `DP_LINK_ENC_CLOCK_CONTROL`, `DP_DPHY_SYM32_CONTROL`, `DP_DPHY_SYM32_STATUS`, `SAT_VC0`, `VC_RATE_CNTL0`, `TP_CONFIG`, and `TP_CUSTOM*`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn31/dcn31_hubbub.h` and related hubbub code use `HUBBUB_SF` and register helpers for `DCHVM_CTRL0`, `DCHVM_MEM_CTRL`, `DCHVM_CLK_CTRL`, `DCHVM_RIOMMU_CTRL0`, and `DCHVM_RIOMMU_STAT0`.
- HDA/audio and stream encoder code paths use the AZ controller/endpoint/stream and DP/APG/VPG/DME/SYM32 field families indirectly through generated register tables, resource construction, and display/audio packet programming.
- Legacy VGA, perfmon, writeback, DPG, and FMT debug fields integrate mainly through diagnostic, register-dump, or indexed debug access paths rather than high-level display feature code.

Because this file is generated, most direct dependencies are compile-time macro expansions. Missing names usually break compilation where a field list expands. Incorrect numeric shifts or masks can compile cleanly and become runtime MMIO corruption.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.5 hardware register database is the main risk. A wrong mask or shift can silently program the wrong bit in stream enable, packet scheduling, link training, DPHY rate, HDA DMA, or DCHVM power/RIOMMU state.
- This chunk starts mid `DP_SYM32_ENC2` and ends mid DPG3 debug block. The final per-file merge should connect the preceding and following chunks rather than treating this span as a complete logical unit.
- Repeated instance names are easy to confuse. `DP_SYM32_ENC2` versus `DP_SYM32_ENC3`, `DP_DPHY_SYM320` versus `DP_DPHY_SYM321`, `AZSTREAM0..7`, and packet slots `GSP_CONTROL0..14` all have nearly identical field layouts but target different hardware instances or slots.
- Double-buffer pending and update-pending fields are timing-sensitive. Misusing `*_DOUBLE_BUFFER_ENABLE`, `*_DOUBLE_BUFFER_PENDING`, VPG frame/immediate update bits, or GSP trigger-pending fields can create stale packets, missed metadata transmission, or packet updates at an unintended frame boundary.
- Status and clear fields share nearby names. Examples include `APG_AUDIO_CRC_DONE` versus `APG_AUDIO_CRC_DONE_CLEAR`, `APG_AUDIO_FIFO_OVERFLOW_STATUS` versus clear, `METADATA_DB_TAKEN` versus clear, `METADATA_TRANSMISSION_MISSED` versus clear, and `VPG_GENERIC_CONFLICT_OCCURED` versus clear. Treating clear bits as persistent state is a common MMIO hazard.
- Indexed data windows require correct access ordering. VPG generic packet data, ISRC data, VGA indexed registers, perf/debug windows, and HDA immediate command data/index registers can all compile correctly while addressing the wrong indexed byte or register if software uses an incorrect index.
- DPHY link training and CRC fields are link-state-sensitive. Programming training pattern, PRBS, custom symbol, symbol override, VC rate, or SAT slot fields while the link is active can produce transient link errors unless sequenced by the HPO link encoder logic.
- HDA stream descriptors contain split lower/upper base address fields and low unimplemented/alignment bits. Incorrect BDL or DMA position base packing can break audio DMA or corrupt the position buffer protocol.
- Legacy VGA fields use 8-bit masks and historical indexed-register semantics. They are not interchangeable with modern DCN timing-generator fields even when names like horizontal/vertical total look similar.
- Debug-only registers often expose only a bit-0 shift with no explicit mask in this chunk. They should not be assumed to be normal typed configuration fields; many are debug selector/data windows whose interpretation depends on separate hardware debug mux state.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU Display Core with DCN 3.1.5 enabled. This catches missing macros, malformed macro names, and include/field-list expansion failures in DMUB, IRQ, GPIO, resource, HPO, and hubbub code.
- Regenerate `dcn_3_1_5_sh_mask.h` from the authoritative register database and compare this chunk byte-for-byte or by structured field name/shift/mask tuples.
- Cross-revision spot checks against adjacent DCN headers where the hardware block is expected to be compatible, especially HPO DP, DCHVM, HDA/AZ, VGA, and debug field families.
- DisplayPort HPO bring-up tests on DCN 3.1.5 hardware: stream enable/disable, link training, lane count/mode changes, DSC/compressed-stream VBID behavior, generic sideband packet transmission, metadata packets, panel replay tunneling, and DPHY error counters staying clear.
- Audio-over-DP/HDMI validation: APG enable/reset, audio packet generation, HBR status, audio CRC done/result, no APG FIFO overflow, CORB/RIRB command transport, immediate command busy/result-valid, output stream descriptor run/reset, and DMA position updates.
- Metadata and packet update validation: VPG generic packet RAM writes, frame/immediate update pending bits clearing, DME DB taken/pending behavior, no metadata transmission missed flags, and correct ISRC/MPEG infoframe bytes on the wire.
- Host-VM/hubbub validation where DCHVM is used: host VM init request, RIOMMU active/prefetch done polling, memory power request/status, and clock request mode programming.
- Runtime register dumps around feature operations. Writes should modify only fields covered by the intended masks and preserve unrelated fields in the same register.

## Open Questions For Merge

- The final per-file report should connect this chunk with the neighboring chunks that contain the start of `DP_SYM32_ENC2` and the continuation of DPG3/FMT debug definitions.
- This chunk documents field layout only. The final report should avoid inferring higher-level packet, audio, link, or VM sequencing beyond what is corroborated by functional source files.

### subset-b-001886: lines 52128-55341

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 52128-55341

## Scope

This chunk is a large middle slice of the generated DCN 3.1.5 register shift/mask header `dcn_3_1_5_sh_mask.h`. It contains C preprocessor constants only: `_SHIFT` macros for field low-bit positions, `_MASK` macros for raw register bit masks, register-name comments, and generated `// addressBlock:` comments. There are no functions, structs, enums, branches, loops, allocations, or direct software state transitions in this range.

The slice starts in the tail of the `dpg3_dpgdebugind` block with `DPG3_DPG_DEBUG0..2` shift definitions, then covers debug-indirect field definitions for FMT, OPP buffer, OPP pipe, OPP top, ODM, DMCU, RBBMIF, IHC, DMU, DC power-gating, DisplayPort/DIG/AUX/DIO/HPO debug, and APG debug surfaces. The second half defines Azalia/HDA codec, endpoint, descriptor, sink-info, CRC, input-endpoint, root, and stream field masks. It ends mid-block at `AZF0STREAM15_AZALIA_FIFO_SIZE_CONTROL__MIN_FIFO_SIZE_MASK`; the rest of stream 15 continues in the following chunk.

This file is generated hardware-description data. The useful API is the macro namespace, not executable behavior. Runtime behavior appears when AMD display code combines these symbols with matching register offsets from `dcn_3_1_5_offset.h` and MMIO helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WRITE`, `REG_FIELD`, `SF`, or `DMUB_SF`.

## Purpose And Hardware Surface

The purpose of this chunk is to define the bit layout for DCN 3.1.5 display debug and display-audio registers. Companion offset headers identify where each register lives; this header tells consumers how to pack values for writes and decode readbacks from the same registers.

Major hardware areas represented here:

- Display debug buses for DPG, FMT, OPP, ODM, RBBMIF, IHC, DMU, DCPG, DP, DIG, AUX, DIO, HPO, HDMI, DP stream/symbol/link encoders, DP DPHY symbol blocks, and APG clocks.
- DMCU debug buses exposing microcontroller reset/interrupt status, ERAM/IRAM/SFR accesses, internal register access, RBBM/MBUS handshakes, address-decoder hits, request-state machines, last read/write values, scratch registers, condition-code bits, clock-enable indicators, and ABM interrupt wiring for multiple ABM instances.
- Azalia/HDA function-2 codec output controls for converter format, stream/channel ID, digital converter bits, stripe control, ramp rate, GTC presentation-time embedding, codec/pin capabilities, pin widget controls, unsolicited responses, pin sense, default configuration, speaker/channel allocation, downmix, ACP/audio descriptors, multichannel enable/mute/channel IDs, IEC 60958 channel-status override bytes, LPIB snapshot/readback, coding type, format-change status, remote keepalive, and wireless-display identification.
- Azalia endpoint descriptor and sink-info windows for ELD-like audio descriptors, manufacturer/product IDs, port IDs, and sink description bytes.
- Azalia controller CRC result windows for input and output channel CRCs.
- Azalia input endpoint controls mirroring many output codec concepts for input converter/pin paths, including input activity, channel layout, infoframe/status readback, and channel-status low/high words.
- Azalia root/function controls for vendor/device/revision/subordinate-node parameters, function power state, subsystem ID bytes, converter synchronization, codec reset, group type, supported rates/stream formats, and power-state capability bits.
- Azalia stream debug and latency counters for streams 0 through 14, plus the first field definitions for stream 15.

## Important Definitions

The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field low bit.
- `<REGISTER>__<FIELD>_MASK` gives the raw in-register bit mask.
- `//<REGISTER>` comments group fields by hardware register.
- `// addressBlock: <block>` comments identify the generated address block that owns the following registers.

Most debug-bus registers in the first half are single-field, full-register or zero-shift definitions. Examples include `FMTx_FMT_DEBUG*__FMT_DEBUG*__SHIFT`, `OPPBUFx_OPPBUF_DEBUG*__OPPBUF_DEBUG*__SHIFT`, `DPx_DP_DEBUG_*__DP_DEBUG_*__SHIFT`, `DP_AUXx_DP_AUX_DEBUG_*__DP_AUX_DEBUG_*__SHIFT`, `HDMI_STREAM_ENC_*_DEBUG_*__...__SHIFT`, and DP/HPO/APG debug ID macros. These are mainly decode selectors or opaque debug payload fields where the generated header exposes a single shift value of `0x0`.

The DMCU block is denser and exposes named bit positions for internal microcontroller debug words:

- `DMCU_DEBUG_00` reports reset/IRQ/XIRQ pins, ABM0/1/2 interrupt lines, IHC-to-DMCU interrupts, SCP/MCP interrupt lines, CP1 copies of selected signals, power/ack signals, and the DMCU clock-enable bit.
- `DMCU_DEBUG_01..0B` cover ERAM and IRAM arbitration, chip-select/read/write strobes, address fragments, read/write data fragments, write-enable masks, and XA request-handler state.
- `DMCU_DEBUG_0C..0F` cover internal register write/read control and data, including write byte enables, accepted flags, read wait/data-valid state, register addresses, and ABM2 interrupt bits.
- `DMCU_DEBUG_10..18` cover DMCU-to-RBBM arbitration and MBUS access handshakes, request/data FIFO states, MBUS request/complete/write/address fields, and address-decoder hit bits for DCREG, interrupt, perfmon, DPRX, ERAM, and IRAM targets.
- `DMCU_DEBUG_19..2C` expose full MBUS/RBBM read/write data and last-address/data/readback values.
- `DMCU_DEBUG_2D..31` expose ERAM/IRAM/SFR TDM debug group offsets.
- `DMCU_DEBUG_32..3C` expose CP2 reset/gating/read-delay state, microcontroller registers (`index`, accumulators, math registers, condition-code bits), SFR scratch bytes, IRQ/XIRQ disable bits, and ABM3 interrupt signals.
- `DMCU_DEBUG_CONSTANT` provides two 16-bit constant fields, `DBG_DMCU_5a5a` and `DBG_DMCU_beef`, used as debug signature readbacks.

The DisplayPort/DIG/AUX/DIO debug families are instance-repeated:

- `DP0..DP4` have a `dpdebugind` block for `DP_DEBUG_K/L/M/G/O/P/Q/R/S` and a `dpfedebugind` block for `DP_DEBUG_T/U/V/W/X/Y/I/J/N/H/A/B/C/D/E/F`.
- `DIG0..DIG4` have DIG front-end debug ID plus AFMT and VPG debug registers.
- `DP_AUX0..DP_AUX4` expose AUX debug ID and debug buses A through Q.
- `DIO_MISC` exposes I2C debug, DIO/DIG RBBMIF debug buses, DME debug buses, and packed HPD debug fields where `HPD_1_2_DEBUG`, `HPD_3_4_DEBUG`, and `HPD_5_6_DEBUG` place paired HPD values at shifts `0x0` and `0x10`.

The HDMI/HPO/DP high-performance output definitions cover mostly debug selector IDs:

- `HPO_TOP_DEBUG_ID`, `HDMI_LINK_ENC_DEBUG_ID`, and `HDMI_FRL_ENC_DEBUG_ID`.
- `HDMI_STREAM_ENC_HDMISTREAMCLK_DEBUG_ID` plus debug words 0 through 15.
- `HDMI_STREAM_ENC_DISPCLK_DEBUG_ID` plus debug words 0 through 4.
- DP stream encoder debug IDs for streams 0 through 3 across dispclk, dpstreamclk, and symclk32 domains.
- DP symbol32 encoder debug IDs for symclk32 and dpstreamclk domains.
- DP link encoder 0/1 debug IDs and debug buses 0 through 3.
- DP DPHY symbol32 debug blocks 0/1 with debug buses 0 through 18.
- APG socclk and encclk debug IDs/words.

The Azalia output endpoint fields are the main non-debug field-pack definitions in this chunk:

- `AZALIA_F2_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT` packs number of channels, bits per sample, sample divisor/multiple/base rate, and PCM/non-PCM stream type into a 16-bit stream format value.
- `AZALIA_F2_CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID` packs 4-bit channel and stream IDs.
- `AZALIA_F2_CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER` exposes digital enable, validity/config/pre-emphasis/copyright/non-audio/professional/channel-status low bits, and keepalive.
- `AZALIA_F2_CODEC_CONVERTER_STRIPE_CONTROL`, `RAMP_RATE`, and `GTC_EMBEDDING` cover stripe programming, ramp rate, and presentation-time embedding.
- Audio widget capability and supported-size/rate macros define HDA capability readback fields, including digital, power-control, LR-swap, delay, type, rate capabilities, and bit-depth capabilities.
- Pin control fields include output enable, unsolicited-response tag/enable, pin sense presence, default configuration nibbles, speaker allocation, channel allocation, downmix, ACP index/data, audio descriptor fields, LPIB snapshot, coding type, format-change status/reason/response, wireless display ID, and remote keepalive.
- Multichannel enable registers appear as paired `01/23/45/67` controls and odd-channel `1/3/5/7` controls, each with enable, mute, and channel ID fields.
- `AZALIA_F2_PIN_CONTROL_CODEC_CS_OVERRIDE_0..8` provide IEC 60958 channel-status override fields for mode/source, clock accuracy, word length, sampling frequency, original sampling frequency, coefficient/MPEG/CGMS-A, and per-channel channel numbers.
- Pin parameter capability fields expose impedance sense, trigger/jack/headphone/output/input/balanced-I/O/HDMI/VREF/EAPD/DP capability bits.

The Azalia descriptor and sink-info blocks expose repeated data windows:

- `AUDIO_DESCRIPTOR0..13` each provide max channels, supported frequencies, descriptor byte 2, and stereo frequency fields.
- `AZALIA_F2_CODEC_PIN_CONTROL_MANUFACTURER_ID`, `PRODUCT_ID`, `SINK_DESCRIPTION_LEN`, `PORTID0`, and `PORTID1` provide sink identity fields.
- `SINK_DESCRIPTION0..17` provide one 8-bit description byte per register.

The Azalia CRC and stream blocks are repeated telemetry surfaces:

- `AZALIA_INPUT_CRC0_CHANNEL0..7`, `AZALIA_INPUT_CRC1_CHANNEL0..7`, `AZALIA_CRC0_CHANNEL0..7`, and `AZALIA_CRC1_CHANNEL0..7` expose full 32-bit channel CRC results.
- `AZF0STREAM0..14` each expose FIFO min/max size and max latency support, latency counter reset, worst-case latency count, cumulative latency count, cumulative request count, and stream debug data. The chunk begins the same pattern for `AZF0STREAM15` but includes only the FIFO size-control shifts and `MIN_FIFO_SIZE_MASK` before the requested range ends.

## Control Flow And State Behavior

There is no executable control flow in this header. The runtime flow is table-driven:

1. A DCN 3.1.5 consumer includes `dcn_3_1_5_offset.h` and `dcn_3_1_5_sh_mask.h`.
2. Register-list macros bind an offset such as `regAZALIA_F2_CODEC_*`, `regDP_AUX*_...`, or a debug register offset to the matching shift/mask constants in this file.
3. Hardware-block code reads or writes MMIO through AMD display register helpers.
4. Hardware latches configuration fields, returns live status/debug values, or clears counters/status according to the register's real side effects.

Most state represented here is hardware state rather than software-owned persistence:

- Persistent or semi-persistent configuration fields include Azalia converter format, stream/channel ID, digital converter flags, keepalive, stripe, ramp rate, GTC embedding, pin widget output enable, unsolicited-response enable/tag, speaker/channel allocation, downmix policy, ACP/audio descriptor selection, multichannel enable/mute/channel IDs, IEC 60958 channel-status overrides, remote keepalive, codec power-state set, converter synchronization, codec reset, and per-stream FIFO sizing/latency support controls.
- Volatile telemetry fields include debug bus readbacks, DMCU internal signal snapshots, RBBMIF/IHC/DMU/DCPG/DP/DIG/AUX/DIO/HPO/APG debug data, pin sense, output active status, format changed/reason/response, LPIB snapshots, input activity and infoframe validity, CRC results, latency counters, cumulative request counters, and stream debug data.
- Side-effecting or sequencing-sensitive fields include latency counter reset, codec reset, power-state settings reset, format-change acknowledgment/UR enable, unsolicited response enable, LPIB snapshot lock, input activity/CL-CS infoframe change UR enables, and any debug selector/register that changes which internal bus is sampled.

The macros do not encode ordering. Callers must still respect display power state, audio codec command protocol, HDA stream setup rules, AUX/DIG/DIO routing, hotplug timing, and any hardware-specific requirements around reading debug buses or clearing counters. A value can be correctly masked and still be wrong if written while the relevant block is power-gated, reset, clock-gated, routed to another encoder, or in the middle of an audio stream transition.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.5 register-address definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`. The offset header supplies the `reg...` constants and base indices; this file supplies the bit positions and masks for fields in those registers. A mismatch between the two can compile in some cases but produce wrong MMIO programming or bad readback decoding.

Known direct include sites for DCN 3.1.5 generated offsets and masks include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`, which builds the DMUB DCN315 register interface using `DMUB_DCN315_FIELDS()`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`, which uses the generated register namespace for DCN315 interrupt-service tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c` and `hw_translate_dcn315.c`, which bind DCN315 GPIO/HPD/DDC/AUX-related hardware translation to generated register definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which constructs the DCN315 resource pool and register tables for display hardware blocks.

Functional integration points include:

- DMUB service code, where generated masks/shifts populate firmware-visible register tables. Although this chunk is mostly debug/audio definitions, incorrect generated constants can affect diagnostics and any firmware-service reads that depend on these fields.
- IRQ and GPIO/hotplug paths, especially where DIO, HPD, AUX, and related debug/status fields help diagnose connector and link behavior.
- Display resource construction and hardware block constructors for DCN315. These register definitions are part of the same namespace used to build stream encoders, link encoders, AUX engines, APG/VPG/AFMT/audio objects, HPO blocks, and diagnostics.
- Audio-over-display code paths that program or inspect Azalia/HDA display-audio state. The `AZALIA_F2_CODEC_*`, descriptor, sink-info, CRC, root/function, and `AZF0STREAM*` fields are the register-field ABI for display audio capability reporting, stream setup, codec status, and latency/CRC diagnostics.
- Debugging and silicon bring-up flows that read debug indirect registers. The many zero-shift debug-bus fields are intentionally opaque payload windows whose exact decoded meaning is usually in hardware documentation, register databases, or debug tooling rather than in driver C code.

## Risks And Maintenance Notes

- Generated-header drift is the primary risk. Wrong numeric masks or shifts can compile cleanly while corrupting audio stream format, channel allocation, channel-status overrides, codec reset/power-state fields, or latency counter control.
- This chunk has partial boundaries. It begins after the start of `dpg3_dpgdebugind` and ends in the middle of `azf0stream15_streamind`; the merge lane should combine neighboring chunks before making file-level completeness claims.
- Many debug registers are single-field `SHIFT 0x0` definitions. They look trivial but still name specific hardware windows. Deleting or renaming them can break register-list expansion, debug tooling, or compile-time consumers even when no ordinary driver path writes the field.
- DMCU debug fields expose internal microcontroller, memory, bus, and ABM interrupt state. These are observational fields, not stable software contracts for normal control flow. Tests and diagnostics should avoid making policy decisions based solely on transient debug bus values.
- DMCU field names include CP1/CP2 copies, split address/data fragments, and similarly named ERAM/IRAM/SFR/RBBM/MBUS state. It is easy to decode the wrong field or join split fields in the wrong order during manual debugging.
- DP/DIG/AUX/DIO debug blocks are heavily instance-repeated. Confusing instance 0-4, link encoder 0/1, stream encoder 0-3, or symbol32 block 0/1 can produce valid reads from the wrong physical/logical link.
- HPD paired debug fields share registers with 16-bit spacing. Consumers must use the correct shift for HPD1 versus HPD2, HPD3 versus HPD4, and HPD5 versus HPD6.
- Azalia output and input endpoint fields have near-identical names. Output converter/pin controls and input converter/pin controls are not interchangeable even when their masks match.
- Several Azalia fields are HDA protocol surfaces rather than arbitrary driver flags. Stream format, channel IDs, IEC 60958 channel status, widget capabilities, pin capabilities, unsolicited response, LPIB, and power-state fields must remain consistent with HDA/display-audio expectations.
- Full-width CRC, LPIB, latency, cumulative latency, cumulative request, descriptor, and port-ID fields use `0xFFFFFFFFL` masks. Truncating, sign-extending, or treating them as small fields can produce misleading diagnostics.
- The stream 15 definitions in this chunk are incomplete. A report or tool generated from this chunk alone should not infer that stream 15 lacks the latency-counter, count, request, or debug registers.

## Test Signals

High-signal validation for changes touching this chunk includes:

- Compile coverage for AMDGPU Display Core with DCN315 enabled. Missing or malformed macros should be caught in `dmub_dcn315.c`, `irq_service_dcn315.c`, `hw_factory_dcn315.c`, `hw_translate_dcn315.c`, and `dcn315_resource.c`.
- Static comparison against the authoritative DCN 3.1.5 register database or a regenerated `dcn_3_1_5_sh_mask.h`, especially for Azalia masks/shifts and DMCU debug bit positions.
- Cross-revision spot checks against adjacent generated headers such as DCN 3.1.4, DCN 3.1.6, and DCN 3.2.0 where the hardware block is expected to be compatible, while preserving intentional DCN315 differences.
- Display-audio functional testing on DCN315 hardware: HDMI/DP audio playback, stream format changes, channel count changes, HBR/non-audio modes where supported, silent-stream/keepalive behavior, multichannel enable/mute/channel IDs, and suspend/resume with audio active.
- Audio diagnostics that read codec capabilities, pin capabilities, sink descriptors, manufacturer/product/port IDs, LPIB snapshots, CRC channels, and latency counters. Expected signals are sane field values, stable counter reset behavior, and no corruption of unrelated bits after masked updates.
- Hotplug/link diagnostic testing for DP/DIG/AUX/DIO/HPO/APG debug surfaces. Useful signals are successful HPD detection, EDID/DPCD reads, AUX transaction recovery, link training, and debug register reads that do not fault or target the wrong instance.
- DMCU/DMUB diagnostic readback during display bring-up, ABM/backlight events, suspend/resume, and interrupt handling. Expected signals include coherent reset/interrupt/bus-state debug values and no reliance on stale sampled debug buses.
- Register-dump comparison before and after audio or debug operations. Packed writes should affect only intended masked bits, and readback decoding should match the mask/shift definitions in this chunk.

## Open Questions For Merge

- The final per-file report should reconcile this chunk with the previous DPG3 lines and the following stream 15 lines so partial block boundaries are not mistaken for missing hardware support.
- This chunk documents generated field layout only. Any final behavioral claims about HDA command sequencing, DMCU debug interpretation, or debug-bus selector programming should be corroborated with the functional display/audio source files that use these macros.

### subset-b-001887: lines 55342-57717

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 55342-57717

## Scope And Purpose

This chunk is part of the generated AMD DCN 3.1.5 register-field shift/mask header. It contains C preprocessor constants only: `_SHIFT` macros for bit positions, `_MASK` macros for raw register masks, register-name comments, and address-block comments. There are no functions, structs, enums, branches, loops, allocations, locks, or software-owned state objects in the range.

The chunk starts in the tail of the `AZF0STREAM15` stream-indirect Azalia definitions, then covers the indexed Azalia display-audio endpoint field layout for endpoint instances 0 through 3, and ends in the beginning of endpoint instance 4. Endpoints 0 through 3 are complete in this range; endpoint 4 is partial and continues after line 57717. The definitions describe the hardware ABI used to pack and decode fields in HDA/Azalia codec converter and pin-control registers for HDMI/DisplayPort audio over display links.

The exported surface is generated metadata. The matching offset header supplies register/index addresses such as `mmAZF0ENDPOINTx_AZALIA_F0_CODEC_ENDPOINT_INDEX`, `mmAZF0ENDPOINTx_AZALIA_F0_CODEC_ENDPOINT_DATA`, and `ixAZF0ENDPOINTx_AZALIA_F0_*`; this header supplies the bit layout for values read from or written through those indirect endpoint windows.

## Hardware Surface Covered

The first few definitions finish `AZF0STREAM15` stream latency/debug layout:

- `AZF0STREAM15_AZALIA_FIFO_SIZE_CONTROL` tail masks for maximum FIFO size and maximum latency support.
- `AZF0STREAM15_AZALIA_LATENCY_COUNTER_CONTROL` reset bit.
- `AZF0STREAM15_AZALIA_WORSTCASE_LATENCY_COUNT`, `AZF0STREAM15_AZALIA_CUMULATIVE_LATENCY_COUNT`, and `AZF0STREAM15_AZALIA_CUMULATIVE_REQUEST_COUNT`, each exposing a full 32-bit counter field.
- `AZF0STREAM15_AZALIA_STREAM_DEBUG` exposing a debug data shift.

The bulk of the range is repeated endpoint-indirect layout for `azf0endpoint0_endpointind` through `azf0endpoint4_endpointind`. Endpoint instances 0 through 3 include the same broad register families:

- Converter widget capability and control registers, including audio widget capabilities, converter format, channel/stream ID, digital converter status/control, supported stream formats, supported size/rates, stripe control, ramp rate, GTC presentation-time embedding/debug, and GTC counter delta/min/max readbacks.
- Pin widget capability and control registers, including pin audio widget capabilities, pin capabilities, unsolicited response, pin sense, widget output enable, channel/speaker allocation, ACP packet data, audio descriptors 0 through 13, multichannel enable/mute/channel-ID controls, lipsync response, HBR response, sink information registers, hot-plug/audio-enable control, forced unsolicited response payload, configuration default response, multichannel enable2/mode, IEC 60958 channel-status override registers 0 through 8, association info, digital output status, LPIB snapshot/LPIB/timer snapshot, coding type, format-changed response, wireless display identification, remote keepalive, and audio enable/disable/format-changed interrupt status.

Endpoint 4 is present only through the early pin-capability fields in this chunk. The covered endpoint 4 definitions include converter debug/capabilities/control, supported formats/rates, stripe/ramp/GTC fields, pin audio widget capabilities, and the beginning of pin parameter capabilities through `TRIGGER_REQUIRED__SHIFT`. The remaining endpoint 4 fields are outside this work item.

## Important Macros And Field Groups

The generated API follows the standard register-field naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- `// addressBlock: ...` comments identify the hardware index/data aperture for following definitions.
- `AZF0ENDPOINT<n>_` prefixes are instance-specific. The field layouts are mostly identical across endpoints, but callers must select the right endpoint's index/data MMIO registers and the right indirect register index from the companion offset header.

Important converter fields include:

- `*_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` advertises HDA widget traits such as channel capability, amplifier presence, format override, stripe support, processing widget, unsolicited response, connection list, digital widget, power control, LR swap, delay, and widget type.
- `*_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT` packs number of channels, bits per sample, sample base divisor/multiple/rate, and PCM/non-PCM stream type. These fields map directly to audio stream format programming.
- `*_CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID` packs channel ID and stream ID.
- `*_CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER` exposes `DIGEN`, validity/config/preemphasis/copy/non-audio/professional bits, channel status category code, and `KEEPALIVE`.
- `*_CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` and `*_PARAMETER_SUPPORTED_SIZE_RATES` advertise stream format, sample-rate, and sample-size support.
- `*_CODEC_CONVERTER_CONTROL_GTC_EMBEDDING`, `*_GTC_COUNTER_DELTA`, `*_GTC_COUNTER_DELTA_MIN`, and `*_GTC_COUNTER_DELTA_MAX` support presentation-time embedding and timing-delta diagnostics.

Important pin-control fields include:

- `*_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `*_CODEC_PIN_PARAMETER_CAPABILITIES` describe the exposed HDA pin widget, including HDMI/DP capability, output/input capability, jack-detect-style flags, VREF control, EAPD, and widget type.
- `*_CODEC_PIN_CONTROL_CHANNEL_SPEAKER` packs speaker allocation, channel allocation, HDMI/DP connection flags, extra connection information, LFE playback level, level shift, and downmix inhibit.
- `*_CODEC_PIN_CONTROL_ACP_DATA` packs ACP packet index, audio-info support, ACP packet enable, ACP type, and type-dependent bytes.
- `*_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0..13` expose short audio descriptor fields. Descriptor 0 has an additional `SUPPORTED_FREQUENCIES_STEREO` byte; all descriptors share max channels, supported frequencies, and descriptor byte 2 fields.
- `*_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` packs enable/mute/channel-ID controls for channel pairs 01, 23, 45, and 67. `*_MULTICHANNEL_ENABLE2` covers odd-numbered channel controls 1, 3, 5, and 7. `*_MULTICHANNEL_MODE` selects multichannel mode.
- `*_CODEC_PIN_CONTROL_RESPONSE_LIPSYNC` exposes video and audio latency response bytes. `*_RESPONSE_HBR` exposes HBR capability and enable.
- `*_CODEC_PIN_CONTROL_SINK_INFO0..8` pack monitor manufacturer/product ID, sink description length, port IDs, and up to 18 display-name bytes.
- `*_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL` controls clock gating disable, reports clock-on state, and carries the `AUDIO_ENABLED` bit.
- `*_CODEC_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT` exposes HDA default-configuration fields such as sequence, default association, misc, color, connection type, default device, location, and port connectivity.
- `*_PIN_CONTROL_CODEC_CS_OVERRIDE_0..8` expose IEC 60958 channel-status override fields for mode/source, clock accuracy, word length, sampling frequency, original sampling frequency, coefficients, MPEG surround, CGMS-A, and channel numbers.
- `*_CODEC_PIN_CONTROL_LPIB*`, `*_CODING_TYPE`, `*_FORMAT_CHANGED`, `*_WIRELESS_DISPLAY_IDENTIFICATION`, and `*_REMOTE_KEEPALIVE` provide playback position, format-change, wireless-display, and keepalive surfaces.
- `*_AUDIO_ENABLED_INT_STATUS`, `*_AUDIO_DISABLED_INT_STATUS`, and `*_AUDIO_FORMAT_CHANGED_INT_STATUS` pack flag, mask, and type bits for endpoint audio events.

## Control Flow And State Behavior

This header has no executable control flow. Runtime flow is indirect:

1. DCN resource code builds an audio register table for each audio instance using endpoint index/data MMIO offsets.
2. Audio code writes an indirect endpoint register index through `AZALIA_F0_CODEC_ENDPOINT_INDEX`.
3. It reads or writes endpoint data through `AZALIA_F0_CODEC_ENDPOINT_DATA`.
4. Register helpers and `set_reg_field_value()` use these `_SHIFT` and `_MASK` constants to pack fields into the endpoint data value.
5. Hardware latches, reports, or clears the represented Azalia/HDA codec state.

The state represented by this chunk is hardware state. Persistent configuration includes converter format, channel/stream ID, digital converter enable/status bits, speaker/channel allocation, ACP enable/data, short audio descriptors, multichannel enable/mute/channel IDs, lipsync response values, HBR capability/enable, sink information, audio enable, configuration default, IEC 60958 override fields, coding type, wireless display ID, and remote keepalive. Volatile readback and telemetry include latency counters, GTC counter deltas, pin sense, digital output status, LPIB snapshots, format-changed state, audio enable status, and interrupt/status flag fields. Side-effect-prone fields include latency counter reset, clear-style GTC/min/max controls, unsolicited response force, interrupt flags/masks, LPIB snapshot lock, and hot-plug/audio-enable sequencing.

The macros do not encode ordering. Callers must still obey HDA/Azalia endpoint access sequencing, choose the correct endpoint instance, avoid racing display hotplug/modeset state, preserve unrelated fields during read/modify/write updates, and respect whether a field is read-only, write-only, latched, or side-effecting according to the hardware specification.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.5 offset header, which provides the concrete endpoint index/data MMIO addresses and indirect `ixAZF0ENDPOINT*`/`ixAZF0STREAM15*` register indices. A shift/mask constant from this file is only meaningful when paired with the correct generated offset/index symbol.

The main software integration path is the Display Core audio implementation:

- `drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` defines the audio register, shift, and mask structures. `AUD_COMMON_REG_LIST(id)` binds each audio instance to `AZALIA_F0_CODEC_ENDPOINT_INDEX` and `AZALIA_F0_CODEC_ENDPOINT_DATA`. The mask/shift list includes `AZALIA_ENDPOINT_REG_INDEX`, `AZALIA_ENDPOINT_REG_DATA`, and global codec function fields.
- `drivers/gpu/drm/amd/display/dc/dce/dce_audio.c` implements indirect endpoint access through `write_indirect_azalia_reg()` and `read_indirect_azalia_reg()`. It then uses endpoint registers covered by this chunk to enable/disable audio, configure speaker allocation, ACP data, audio descriptors, HBR capability, lipsync values, sink information, hot-plug/audio-enable state, and display-name/port-ID information.
- DCN resource files such as `display/dc/resource/dcn31/dcn31_resource.c` and `display/dc/resource/dcn314/dcn314_resource.c` build `audio_regs[]`, `audio_shift`, and `audio_mask` tables using `AUD_COMMON_REG_LIST(id)` and `DCE120_AUD_COMMON_MASK_SH_LIST(...)`, then call `dce_audio_create(ctx, inst, &audio_regs[inst], &audio_shift, &audio_mask)`.
- Stream encoder and AFMT code integrate with this endpoint state by selecting Azalia audio sources and programming HDMI/DP audio packet and IEC 60958 channel-status transmission. Endpoint programming describes the codec/pin surface exposed to the OS audio stack, while AFMT/stream-encoder programming controls packet insertion on the display link.
- Older amdgpu DCE paths use similar Azalia endpoint indirect programming and the same conceptual register families for response configuration, lipsync, channel/speaker allocation, descriptors, and hot-plug audio enable.

Because this file is generated, most direct references are macro-expansion based. Missing or renamed macros tend to fail compilation where a resource table or helper macro expands. Incorrect numeric masks or shifts can compile cleanly and cause runtime audio misconfiguration.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.5 register specification is the main risk. A wrong shift/mask can silently write the wrong endpoint bits, corrupting audio format, channel mapping, HBR capability, sink information, hot-plug state, or interrupt masking.
- This chunk starts in the middle of `AZF0STREAM15_AZALIA_FIFO_SIZE_CONTROL`; its low-field shifts/masks are in the previous chunk. The final merged report should preserve that neighboring context.
- This chunk ends in the middle of endpoint 4 pin capability definitions. Endpoint 4 should not be treated as complete until the next chunk is reconciled.
- Endpoint blocks are highly repetitive. Copy/paste or generation errors that swap endpoint numbers can still produce valid macro names but target the wrong audio endpoint.
- The display audio code often uses endpoint 0 shift/mask names in resource mask tables for the generic index/data fields, while the register address table selects the endpoint instance. The final report should distinguish generic endpoint index/data masks from per-endpoint indirect register field masks.
- Several fields describe read-only hardware capabilities or status, while driver code writes some related registers as part of endpoint exposure. For example, `dce_audio.c` comments that `LFE_PLAYBACK_LEVEL` is specified as read-only yet is written in one path. Hardware-version differences around such fields need careful validation.
- Audio descriptor 0 has a stereo supported-frequency byte not present in the same way for descriptors 1 through 13. Treating all descriptor registers as identical can lose stereo-rate information for LPCM.
- Hot-plug audio enable and clock-gating fields are sequencing-sensitive. `dce_aud_az_enable()` and `dce_aud_az_disable()` temporarily set `CLOCK_GATING_DISABLE`, update `AUDIO_ENABLED`, then clear clock gating disable. A mask error here can leave audio disabled or clocks unexpectedly gated.
- Interrupt/status fields use flag, mask, and type bits in the same register. Tests and diagnostics should avoid treating mask bits as event flags or vice versa.
- Full-width telemetry fields such as GTC deltas, latency counts, LPIB, and sink port IDs should be handled as unsigned 32-bit values. Partial extraction would produce misleading diagnostics.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build coverage for AMDGPU Display Core with DCN 3.1.5 headers included. This catches malformed macros, missing generated names, and include-time syntax errors.
- Generated-header comparison against the authoritative DCN 3.1.5 register database, especially for endpoint instance repetition and endpoint 4 continuation across chunk boundaries.
- Runtime display-audio smoke tests on DCN 3.1.5 hardware: HDMI audio enumeration, DisplayPort audio enumeration, hotplug enable/disable, audio playback after modeset, and audio recovery after suspend/resume or link retraining.
- EDID/audio capability propagation tests. Programmed short audio descriptors, speaker allocation, HBR capability, sample rates, and sink information should match the connected sink and appear correctly to the OS audio stack.
- HBR and multichannel playback tests for 2-channel, 6-channel, 8-channel, and high-sample-rate modes. These exercise descriptor, HBR, channel allocation, multichannel enable, and IEC 60958 fields.
- Register dump checks around `dce_aud_az_configure()`, `dce_aud_az_enable()`, and `dce_aud_az_disable()`. Only intended masked fields should change, and endpoint instance selection should match the active stream/audio object.
- Interrupt/status observation for audio enabled, audio disabled, and audio format changed events. Flag/mask/type bits should decode consistently with hardware events.
- Latency/GTC/LPIB diagnostics during playback. Counter reset and readback fields should behave monotonically or reset only when explicitly requested.

## Open Questions For Merge

- The final per-file report should connect this chunk with the preceding stream chunks and following endpoint 4 chunk so `AZF0STREAM15` and `AZF0ENDPOINT4` are not described as incomplete hardware blocks.
- The exact DCN 3.1.5 product resource file that includes this generated header may be outside this chunk's immediate search surface; the merge lane should tie the header to the full ASIC include chain used by the relevant DCN 3.1.5 resource module.

### subset-b-001888: lines 57718-60079

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 57718-60079

## Scope

This chunk is generated AMD DCN 3.1.5 display register field metadata. It contains C preprocessor constants only: paired `__SHIFT` and `_MASK` macros for fields inside Azalia/HDA display-audio indexed registers, plus generated register and address-block comments. There are no functions, structs, enums, branches, loops, allocations, includes, or software-owned state in this range.

The reviewed span contains 2,041 `#define` entries: 1,041 shift definitions and 1,012 mask definitions. The mismatch is caused by chunk boundaries: the range begins in the middle of `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_PARAMETER_CAPABILITIES`, so some endpoint-4 shifts precede their masks in this chunk, and it ends inside `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, before the rest of that input endpoint block.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU Display Core hardware metadata rather than distributed filesystem code.

## Purpose And Hardware Surface

The purpose of this header slice is to describe bit layouts for DCN 3.1.5 Azalia F0 display-audio codec endpoint registers. The companion `dcn_3_1_5_offset.h` header supplies register/index addresses such as the `ixAZF0ENDPOINT<n>_*` and `ixAZF0INPUTENDPOINT<n>_*` names; this file supplies the masks and shifts used by AMD display register helpers to pack writes and decode readbacks.

The hardware surface covered here is the repeated HDA/Azalia endpoint namespace:

- The tail of output endpoint 4, starting at pin parameter capabilities and covering pin control, audio descriptors, multichannel controls, sink information, hotplug, channel-status overrides, LPIB snapshots, coding/format status, keepalive, audio-enable status, and interrupt-status fields.
- Complete output endpoint blocks 5, 6, and 7, each containing converter capability/control fields and the same pin-control/status layout used for display audio over HDMI/DisplayPort sinks.
- The complete input endpoint 0 block, including input converter controls, input pin capabilities, input multichannel routing, HBR, hotplug/audio-enable, LPIB snapshots, input activity/status, and audio infoframe readback.
- The beginning of input endpoint 1, through the input converter audio-widget capability fields.

The field layouts let higher-level display-audio code treat endpoint instances uniformly while still targeting endpoint-specific generated macro names.

## Important Definitions

The exported API is the generated macro naming convention:

- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` gives the low-bit position for a field in output endpoint `n`.
- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` and `_MASK` do the same for input endpoint `n`.
- `//AZF0ENDPOINT...` comments group field macros by generated register name.
- `// addressBlock: azf0endpoint<n>_endpointind` and `// addressBlock: azf0inputendpoint<n>_inputendpointind` mark the indexed endpoint register aperture.

Important output endpoint families in this range:

- `CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` reports converter widget properties: channel capability, input/output amplifier presence, override support, stripe/processing flags, unsolicited response capability, connection-list, digital, power-control, left/right swap, delay, and widget type.
- `CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT` packs channel count, bits per sample, sample base divisor/multiple/rate, and stream type.
- `CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID` maps channel ID and stream ID into the converter.
- `CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER` contains digital audio status/control bits such as enable, V, VCFG, pre-emphasis, copyright, non-audio, professional, level, category code, generation level, and copy-protection level.
- `CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` and `PARAMETER_SUPPORTED_SIZE_RATES` expose supported PCM/non-PCM formats, sample sizes, and sample rates.
- `CODEC_CONVERTER_STRIPE_CONTROL`, `CONTROL_RAMP_RATE`, `CONTROL_GTC_EMBEDDING`, `GTC_COUNTER_DELTA`, `GTC_COUNTER_DELTA_MIN`, and `GTC_COUNTER_DELTA_MAX` define converter striping, ramp, and global time counter embedding/readback fields.
- `CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `CODEC_PIN_PARAMETER_CAPABILITIES` describe the endpoint pin widget, including impedance sense, jack detection, output/input capability, HDMI, DP, VREF, EAPD, and related capability bits.
- `CODEC_PIN_CONTROL_UNSOLICITED_RESPONSE` and `UNSOLICITED_RESPONSE_FORCE` define unsolicited-response tag/enable and forced payload/trigger fields.
- `CODEC_PIN_CONTROL_RESPONSE_PIN_SENSE`, `WIDGET_CONTROL`, `CHANNEL_SPEAKER`, `ACP_DATA`, `RESPONSE_LIPSYNC`, `RESPONSE_HBR`, `HOT_PLUG_CONTROL`, and `RESPONSE_CONFIGURATION_DEFAULT` cover sink presence/sense, output enable, speaker/channel allocation, ACP packet data, audio/video lipsync, high-bit-rate audio capability/enable, audio hotplug enable/clock gating, and default pin configuration.
- `CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13` describe per-format audio descriptor fields: max channels, supported frequencies, descriptor byte 2, and for descriptor 0 the stereo frequency byte.
- `CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2` map channel-pair enable/mute/channel-ID fields for channels 0-7.
- `CODEC_PIN_CONTROL_SINK_INFO0` through `SINK_INFO8` expose ELD/sink information payload fields such as manufacturer, product ID, sink description, port ID, audio latency, video latency, and HDMI/DP sink flags.
- `PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8` define IEC 60958 channel-status override bytes and word select/readback fields.
- `CODEC_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `LPIB`, and `LPIB_TIMER_SNAPSHOT` expose link-position-in-buffer snapshot lock, wrap count, LPIB, and timer snapshot readbacks.
- `CODEC_PIN_CONTROL_FORMAT_CHANGED`, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS` define interrupt state, mask, ack, and polarity fields.

Important input endpoint families in this range:

- `CODEC_INPUT_CONVERTER_*` mirrors the converter capability, format, channel/stream ID, digital converter, stream format, and supported-size/rate fields for input-side audio capture/receive paths.
- `CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `CODEC_INPUT_PIN_PARAMETER_CAPABILITIES` describe the input pin widget and its HDA capabilities.
- `CODEC_INPUT_PIN_CONTROL_RESPONSE_INPUT_PIN_SENSE` adds `PRESENCE_DETECT` at bit 31 on top of the impedance-sense field.
- `CODEC_INPUT_PIN_CONTROL_WIDGET_CONTROL` exposes `IN_ENABLE`, while output endpoint widget control exposes `OUT_ENABLE`.
- `CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2` provide one channel per byte for input channels 0-7, with enable, mute, and channel-ID fields.
- `CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL` exposes input activity, channel layout, input activity unsolicited-response enable, and channel-layout/channel-status infoframe-change unsolicited-response enable.
- `CODEC_INPUT_PIN_CONTROL_INFOFRAME` exposes input audio infoframe channel count, channel allocation, byte 5, and valid flag.

## Control Flow

This header has no executable control flow. Runtime sequencing is supplied by AMDGPU Display Core code that includes `dcn_3_1_5_offset.h` and `dcn_3_1_5_sh_mask.h`, constructs register and field tables through token-pasting macros, and then calls MMIO/indexed-register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, or related generated field helpers.

A typical use path is:

1. A DCN315 display-audio or resource path selects an Azalia endpoint instance, such as endpoint 5 or input endpoint 0.
2. The companion offset header supplies the indexed register selector for that endpoint register.
3. This shift/mask header supplies the field position and mask.
4. Register helpers pack a new field value, preserve unrelated bits, read a status field, or acknowledge an interrupt/status bit.
5. Hardware latches, reports, clears, or consumes the represented endpoint state according to the Azalia/HDA register protocol.

The macros do not encode HDA command ordering, codec verb sequencing, hotplug timing, ELD update timing, stream disable/enable ordering, or write-one-to-clear semantics. Callers must still follow those rules in functional driver code.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes MMIO/indexed hardware state in the GPU display-audio block.

Configuration-like hardware fields include converter format, stream ID, channel ID, digital converter control, stripe control, GTC embedding control, pin widget output/input enable, speaker/channel allocation, ACP packet data, multichannel enable/mute/channel mapping, HBR enable, hotplug audio enable, unsolicited response enable/tag, default configuration, channel-status override bytes, remote keepalive, and audio-enable controls.

Readback/status fields include audio widget and pin capabilities, supported stream formats and size/rates, pin sense/impedance/presence, sink info/ELD data, lipsync delay values, HBR capability, LPIB and timer snapshots, format-changed flags, audio enabled/disabled/format-changed interrupt status, input activity, input channel layout, and input audio infoframe validity.

Several fields are likely side-effecting when written, based on their names and HDA register conventions: interrupt acknowledge fields, interrupt masks/polarities, forced unsolicited response trigger, LPIB snapshot lock, hotplug/audio enable, remote keepalive, and channel-status override selection/control. The generated masks do not distinguish read-only, sticky, self-clearing, or write-one-to-clear behavior; that behavior must be inferred from the hardware specification and the driver code using the fields.

## Dependencies And Integration Points

This chunk must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`. The offset header defines the indexed register numbers and base selectors; this header defines the bit layouts. A missing macro name generally fails compilation, while an incorrect numeric mask or shift can compile and silently program or decode the wrong hardware bits.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`, which includes the DCN315 offset and shift/mask headers for DMUB-facing register metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`, which includes the same generated headers for DCN315 interrupt/register field definitions.
- DCN315 resource construction reached from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_resource.c`, which creates the DCN315 resource pool and binds generated register metadata into display hardware objects.

Functional consumers are indirect. Display-audio helpers and stream encoders select Azalia audio instances, enable audio packets, configure audio source/channel mapping, program infoframes and IEC 60958 channel-status data, react to hotplug and format changes, and service audio-related interrupts using register tables built from generated headers. Local code also documents sink-description handling around `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT` in `display/dc/core/dc_resource.c`.

The endpoint macros are highly instance-specific. `AZF0ENDPOINT5`, `AZF0ENDPOINT6`, and `AZF0ENDPOINT7` have nearly identical layouts, while `AZF0INPUTENDPOINT0` and `AZF0INPUTENDPOINT1` use input-specific register names and field names. Resource and audio code must bind the correct generated prefix to the intended audio endpoint.

## Risks And Maintenance Notes

- The primary risk is generated-header drift from the DCN 3.1.5 register database. A wrong mask or shift can corrupt audio format programming, channel routing, HBR enablement, sink/ELD interpretation, LPIB readback, or interrupt acknowledge behavior without producing a compile error.
- This range starts mid-register family. `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_PARAMETER_CAPABILITIES` has earlier shift definitions before line 57718; the final per-file report should merge adjacent chunks before presenting endpoint 4 as complete.
- This range ends inside input endpoint 1. Only `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_CONVERTER_PIN_DEBUG` and the beginning of `CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` are visible here; later chunks own the rest of input endpoint 1.
- Output endpoint blocks 5-7 are repetitive. A generator error affecting only one instance can still compile and only fail on connector/audio paths routed through that endpoint.
- Output and input endpoint names are similar but not interchangeable. Confusing `CODEC_PIN_CONTROL_WIDGET_CONTROL__OUT_ENABLE` with `CODEC_INPUT_PIN_CONTROL_WIDGET_CONTROL__IN_ENABLE`, or `RESPONSE_PIN_SENSE` with `RESPONSE_INPUT_PIN_SENSE`, can target a valid-looking but wrong field.
- Channel mapping fields are dense and repeated. The multichannel enable registers pack enable, mute, and channel ID into byte-sized groups; off-by-one channel or pair mapping errors can appear as swapped, muted, or missing audio channels.
- Interrupt/status fields expose mask, ack, polarity, and status bits in the same family. Treating an acknowledge bit like ordinary persistent state can clear events unexpectedly, while failing to preserve mask/polarity bits can break audio hotplug or format-change notification.
- Sink information and descriptor fields are protocol-facing. Bad masks can make the driver advertise the wrong speaker allocation, channel allocation, latency, HBR capability, HDMI/DP connection type, or supported sample rates to higher display-audio logic.

## Test Signals

Useful validation for changes touching this chunk includes:

- Compile AMDGPU Display Core with DCN315 enabled. This catches missing or malformed generated macro names referenced by DCN315 resource, IRQ, DMUB, audio, and stream-encoder code.
- Regenerate or mechanically compare `dcn_3_1_5_sh_mask.h` against the authoritative DCN 3.1.5 register database, especially for `AZF0ENDPOINT4` tail fields, complete `AZF0ENDPOINT5`-`7`, and `AZF0INPUTENDPOINT0`/`1` boundary fields.
- Check that each complete register group in this slice has expected paired `__SHIFT` and `_MASK` definitions, while allowing boundary exceptions at the beginning and end of the chunk.
- Preprocess representative `REG_GET`, `REG_SET`, `REG_UPDATE`, field-table, and audio register-list macros to ensure token concatenation resolves to the intended `AZF0ENDPOINT<n>` or `AZF0INPUTENDPOINT<n>` symbols.
- Runtime HDMI/DP audio tests on DCN315 hardware for endpoints routed through output endpoints 5-7: modeset, hotplug, audio enable/disable, PCM playback, channel mapping, multichannel playback, sample-rate changes, HBR/encoded audio where supported, and suspend/resume.
- Sink/ELD validation by comparing reported monitor audio capabilities, speaker allocation, latency, manufacturer/product/port fields, and audio descriptors against known-good EDID/ELD data.
- Interrupt and status validation for audio enabled, audio disabled, format changed, unsolicited response, input activity, and infoframe-change paths, including checking that status bits clear only when expected.
- Register-dump validation before and after audio setup. Writes should affect only the intended masked bits and preserve neighboring fields in dense registers such as multichannel enables, channel-status overrides, hotplug control, and interrupt status/control.

## Cross-Chunk Notes

Previous chunks own the beginning of endpoint 4, including earlier converter and pin parameter fields before line 57718. Later chunks continue input endpoint 1 after the partial audio-widget capability block. The final per-file research document should merge adjacent chunk reports before making complete claims about all DCN 3.1.5 Azalia output endpoints or the full input endpoint namespace.

### subset-b-001889: lines 60080-62071

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 60080-62071

## Purpose

This chunk is the tail of AMD DCN 3.1.5 generated register field metadata. It contains no executable C logic; it publishes preprocessor constants that describe hardware bit positions (`__SHIFT`) and bit masks (`_MASK`) for DCN 3.1.5 display-controller MMIO registers. Consumers combine these constants with the matching `dcn_3_1_5_offset.h` register offsets and AMD display register-helper macros to read, write, set, update, or decode individual fields.

The requested range starts in the middle of the `AZF0INPUTENDPOINT1` Azalia F0 codec input endpoint block, fully covers `AZF0INPUTENDPOINT2` through `AZF0INPUTENDPOINT7`, then ends the header with DSCC, DSCCIF, and DSC_TOP debug-register shift definitions plus the include guard terminator. It defines 1,707 macros in this slice: 897 `__SHIFT` constants and 810 `_MASK` constants.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or direct MMIO operations in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate or update that field.
- `// addressBlock: ...` comments: generated grouping markers for indexed hardware blocks.

Major register families in this range:

- `AZF0INPUTENDPOINT1` tail: remaining input converter and input pin field masks/shifts for converter format, channel/stream ID, digital converter control, supported formats/rates, pin capabilities, unsolicited responses, pin sense, widget enable, multichannel routing, HBR, channel allocation, hotplug/audio enable, forced unsolicited response payloads, configuration default, LPIB snapshots, input activity, and infoframe data.
- `AZF0INPUTENDPOINT2` through `AZF0INPUTENDPOINT7`: six complete repeated Azalia F0 codec input endpoint blocks. Each endpoint exposes the same converter, pin-parameter, pin-control, stream-format, multichannel, hotplug, LPIB, status, and infoframe field layout.
- `DSCC_DEBUG_ID` and `DSCC_DEBUG_0` through `DSCC_DEBUG_76`: debug register selectors and status fields for the DSCC compressor/debug block. Most are single full-register fields at shift 0; `DSCC_DEBUG_8` exposes four individual `DSCC_RATE_BUFFER*_INITIAL_XMIT_DELAY_REACHED` bits.
- `DSCCIF_DEBUG_ID` and `DSCCIF_DEBUG_0` through `DSCCIF_DEBUG_4`: debug selector/data fields for the DSC client interface debug block.
- `DSC_TOP_DEBUG_ID` and `DSC_TOP_DEBUG_0` through `DSC_TOP_DEBUG_4`: top-level DSC debug selector/data fields.
- Final `#endif`: closes `_dcn_3_1_5_SH_MASK_HEADER`, confirming this chunk reaches end-of-file.

Representative Azalia endpoint fields include:

- Audio widget capability fields: channel capability, input/output amplifier presence, format override, stripe, processing widget, unsolicited response capability, connection list, digital, power control, LR swap, delay, and type.
- Converter controls: channel count, bits per sample, sample base divisor/multiple/rate, stream type, channel ID, stream ID, digital enable, validity/configuration/copyright/non-audio/pro bits, category code, and keepalive.
- Pin controls: impedance/presence detect, input enable, multichannel enables/mutes/channel IDs for channels 0 through 7, HBR capable/enable, channel allocation, clock gating, clock-on state, audio enabled, and configuration default fields.
- Runtime/status fields: forced unsolicited response payloads, LPIB lock and wrap count, LPIB value, LPIB timer snapshot, input activity, channel layout, unsolicited-response enables, infoframe channel count/allocation/byte 5, and infoframe-valid.

## Control Flow

This header chunk has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code:

1. DCN 3.1.5 translation units include `dcn_3_1_5_offset.h` and `dcn_3_1_5_sh_mask.h`.
2. Register-list macros paste symbolic register and field names into offset, mask, and shift macro names.
3. Helper macros such as `FD_MASK`, `FD_SHIFT`, block-specific field-list macros, and `REG_*` helpers materialize per-ASIC register tables.
4. Driver code later uses those tables to program or inspect audio endpoints, codec pin/converter state, hotplug/audio enable state, infoframes, LPIB snapshots, and DSC debug state.

The generated constants do not encode access ordering. Consumers must still handle hardware sequencing for display audio stream setup, pin/control updates, unsolicited responses, HBR/multichannel enablement, hotplug/audio enable transitions, LPIB snapshot locking, DSC debug selection, interrupt/status clearing, power gating, suspend/resume, and reset.

## State And Persistence Behavior

The chunk stores no software state and persists nothing in memory or files. It describes MMIO-backed GPU state. The represented hardware state includes:

- Azalia input converter capabilities and active audio stream format/channel/stream controls for endpoints 1 through 7.
- Digital converter flags that describe whether an endpoint is enabled, valid, non-audio, professional, copyright-marked, category-coded, or using keepalive behavior.
- Input pin capabilities and controls for jack/presence sense, input enablement, multichannel routing/mute/channel IDs, HBR, channel allocation, audio enablement, and default configuration metadata.
- LPIB and timer snapshots used to observe audio buffer position and wrap count.
- Input activity, channel layout, infoframe change signaling, and infoframe payload status.
- DSCC, DSCCIF, and DSC_TOP debug selector/data state for display stream compression diagnostics.

Persistence is hardware-defined. Configuration fields usually retain programmed values until modeset, stream reconfiguration, power gating, suspend/resume, or ASIC reset. Status, sense, interrupt, unsolicited-response, LPIB, debug, and counter-like fields may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This generated header only supplies field geometry; it does not distinguish access type or side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.5 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`, which supplies matching MMIO offsets.
- DCN base-address definitions used with the offset header to address the correct register segment.
- Common AMD display register helpers that derive masks and shifts by token pasting generated names.

Direct include sites in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`

Important integration areas:

- Display audio and Azalia/HDA-codec paths use the endpoint fields to advertise and control stream format, sample rate/size, digital converter state, pin capabilities, channel allocation, HBR, multichannel routing, infoframes, and hotplug/audio enable state.
- IRQ or status paths can use unsolicited-response, input activity, infoframe-change, and hotplug-related fields to report audio endpoint changes.
- Firmware-facing DMUB register tables depend on the same masks/shifts when exposing DCN 3.1.5 register fields to firmware service code.
- DSC diagnostics use the DSCC, DSCCIF, and DSC_TOP debug shift constants to select and read display stream compression debug signals.

## Risks And Edge Cases

- Field drift is the central risk. These are untyped preprocessor constants, so a wrong shift or mask can compile cleanly while targeting the wrong MMIO bits.
- The chunk boundary is artificial. The first line begins mid-block in `AZF0INPUTENDPOINT1`, so adjacent chunks are required for complete endpoint-1 coverage and whole-file conclusions.
- Repeated endpoint families are copy-sensitive. `AZF0INPUTENDPOINT2` through `AZF0INPUTENDPOINT7` are structurally similar but not interchangeable; an instance-specific typo may only fail on one physical/logical audio endpoint.
- Audio format and channel fields are user-visible. Incorrect sample size/rate/channel count, stream ID, channel allocation, HBR, or multichannel masks can cause silence, channel swaps, distorted audio, or failures limited to specific HDMI/DP audio formats.
- Digital converter control fields include validity, non-audio, professional, copyright, category-code, and keepalive bits. Misprogramming can affect sink negotiation, audio compliance behavior, or keepalive during blanking/idle periods.
- Hotplug, unsolicited response, input activity, and infoframe-change fields are event-sensitive. Bad masks can cause missed audio endpoint events, spurious notifications, stuck status bits, or resume-only audio failures.
- LPIB snapshot fields are timing-sensitive. Incorrect lock/wrap-count/value interpretation can produce wrong audio position reporting or races when snapshotting active streams.
- DSC debug registers are mostly shift-only in this chunk. Consumers must pair them with offsets and access semantics from other generated files and hardware documentation; these macros do not tell whether the debug data is stable, latched, or selector-dependent.
- The final `#endif` means any accidental edit near this chunk can break the entire header's include guard, affecting all DCN315 display builds.

## Test Signals

Useful validation combines generated-header consistency checks and display/audio behavior:

- Build AMDGPU/DC with DCN 3.1.5 support enabled. Missing or renamed masks/shifts should fail in `dcn315_resource.c`, `irq_service_dcn315.c`, `dmub_dcn315.c`, `hw_factory_dcn315.c`, `hw_translate_dcn315.c`, or shared display-register-table users.
- Mechanically verify that Azalia endpoint fields in lines 60080-62071 have expected `__SHIFT` and `_MASK` pairs where the generated schema defines both, and that shift-only debug fields are intentionally shift-only.
- Diff this slice against AMD's authoritative DCN 3.1.5 register database and neighboring DCN generated headers where compatibility is expected.
- Exercise HDMI/DP audio across endpoints: stereo and multichannel PCM, different sample rates and bit depths, HBR-capable formats, plug/unplug, stream start/stop, blanking, suspend/resume, and rapid display modesets.
- Validate channel allocation, infoframe-valid, input activity, unsolicited response, and hotplug/audio-enable behavior through sink-side audio tests and kernel logs.
- Monitor for audio dropouts, wrong channel mapping, no-sound-on-one-connector bugs, hotplug storms, missed audio endpoint changes, stuck interrupts/status bits, LPIB position anomalies, and resume-only failures.
- For DSC debug fields, enable DSC-capable display modes and confirm debug selectors/data paths remain readable and plausible when investigating compression issues.

## Cross-Chunk Notes

Previous chunks own the beginning of the Azalia F0 codec input endpoint section, including the start of `AZF0INPUTENDPOINT1`. This chunk completes the file after endpoint 7 and the DSCC/DSCCIF/DSC_TOP debug blocks. The final per-file report should merge adjacent chunks before making complete claims about all Azalia endpoint macros, all DSC debug macros, or the full `dcn_3_1_5_sh_mask.h` generated namespace.
