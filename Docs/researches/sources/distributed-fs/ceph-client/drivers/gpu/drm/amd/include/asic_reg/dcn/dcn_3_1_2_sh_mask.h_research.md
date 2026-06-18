# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001802`: lines 1-2466, `Docs/researches/chunks/subset-b-001802_research.md`
- `subset-b-001803`: lines 2467-4750, `Docs/researches/chunks/subset-b-001803_research.md`
- `subset-b-001804`: lines 4751-7217, `Docs/researches/chunks/subset-b-001804_research.md`
- `subset-b-001805`: lines 7218-9886, `Docs/researches/chunks/subset-b-001805_research.md`
- `subset-b-001806`: lines 9887-12399, `Docs/researches/chunks/subset-b-001806_research.md`
- `subset-b-001807`: lines 12400-14927, `Docs/researches/chunks/subset-b-001807_research.md`
- `subset-b-001808`: lines 14928-17438, `Docs/researches/chunks/subset-b-001808_research.md`
- `subset-b-001809`: lines 17439-19949, `Docs/researches/chunks/subset-b-001809_research.md`
- `subset-b-001810`: lines 19950-22457, `Docs/researches/chunks/subset-b-001810_research.md`
- `subset-b-001811`: lines 22458-24978, `Docs/researches/chunks/subset-b-001811_research.md`
- `subset-b-001812`: lines 24979-27504, `Docs/researches/chunks/subset-b-001812_research.md`
- `subset-b-001813`: lines 27505-30069, `Docs/researches/chunks/subset-b-001813_research.md`
- `subset-b-001814`: lines 30070-32536, `Docs/researches/chunks/subset-b-001814_research.md`
- `subset-b-001815`: lines 32537-34973, `Docs/researches/chunks/subset-b-001815_research.md`
- `subset-b-001816`: lines 34974-37370, `Docs/researches/chunks/subset-b-001816_research.md`
- `subset-b-001817`: lines 37371-39761, `Docs/researches/chunks/subset-b-001817_research.md`
- `subset-b-001818`: lines 39762-42177, `Docs/researches/chunks/subset-b-001818_research.md`
- `subset-b-001819`: lines 42178-44529, `Docs/researches/chunks/subset-b-001819_research.md`
- `subset-b-001820`: lines 44530-47039, `Docs/researches/chunks/subset-b-001820_research.md`
- `subset-b-001821`: lines 47040-49469, `Docs/researches/chunks/subset-b-001821_research.md`
- `subset-b-001822`: lines 49470-51864, `Docs/researches/chunks/subset-b-001822_research.md`
- `subset-b-001823`: lines 51865-54474, `Docs/researches/chunks/subset-b-001823_research.md`
- `subset-b-001824`: lines 54475-56841, `Docs/researches/chunks/subset-b-001824_research.md`
- `subset-b-001825`: lines 56842-59188, `Docs/researches/chunks/subset-b-001825_research.md`
- `subset-b-001826`: lines 59189-60782, `Docs/researches/chunks/subset-b-001826_research.md`

## Chunk Research

### subset-b-001802: lines 1-2466

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 1-2466

## Purpose

This chunk is generated C preprocessor metadata for AMD DCN 3.1.2 display hardware registers. It defines `_SHIFT` and `_MASK` constants for register fields so AMDGPU/DC display code can pack, extract, and update MMIO bitfields without embedding raw bit positions in call sites. The covered range starts with the copyright/header guard, then maps early DCN 3.1.2 register blocks for HDA audio controller endpoints, legacy VGA registers, the Display Clock Generator (DCCG), DCCG perfmon instances, and the Display Microcontroller Unit (DMCU).

There are no functions, structs, enums, or executable algorithms here. The file is still part of the driver/hardware ABI: every constant must match the vendor register database for DCN 3.1.2, or otherwise register-helper code can write the wrong hardware bits while still compiling cleanly.

## Important APIs, Types, And Register Groups

- Header guard `_dcn_3_1_2_SH_MASK_HEADER` scopes the generated macro set for this ASIC generation.
- `AZCONTROLLER0_*` describes the primary HDA/azalia audio controller. It includes global capabilities/version, stream payload capabilities, reset/flush/unsolicited-response control, wake and state-change status, stream/controller/global interrupt enable and status bits, wall clock and stream synchronization bits, CORB/RIRB DMA ring base addresses, read/write pointers, sizes, DMA enables, memory error/response interrupt bits, immediate command/response registers, DMA position-buffer base address, and wall-clock alias.
- `AZENDPOINT0_*`, `AZINPUTENDPOINT0_*`, `AZENDPOINT1_*`, and `AZINPUTENDPOINT1_*` define immediate command data/index fields for output and input audio endpoints.
- `AZCONTROLLER1_*` provides a second HDA controller subset focused on CORB/RIRB, immediate command/response, DMA position, and wall-clock alias fields. Unlike controller 0 in this chunk, the controller 1 block does not repeat the global capability/control/status definitions before its ring and command fields.
- `VGA_MEM_*`, `CRTC8_*`, `SEQ8_*`, `GRPH8_*`, `GEN*`, `ATTR*`, and `DAC_*` define masks for legacy VGA memory page, CRTC, sequencer, graphics, attribute, DAC, sync-polarity, status, and miscellaneous-control registers.
- `DENTIST_DISPCLK_CNTL` exposes DISPCLK/DPPCLK divider programming and change/done toggles.
- `PHYPLL[A-E]_PIXCLK_RESYNC_CNTL` defines per-PHY pixel-clock resync, deep-color DTO status/control, pixel-clock enable, and double-rate enable fields.
- DCCG clock source/gating blocks include `DP_DTO_DBUF_EN`, `DTBCLK_DTO_DBUF_EN`, `DCCG_GATE_DISABLE_CNTL[1-4]`, `*_CGTT_BLK_CTRL_REG`, `DPSTREAMCLK_CNTL`, `HDMISTREAMCLK_CNTL`, `HDMICHARCLK0_CLOCK_CNTL`, `SYMCLK32_*`, `SYMCLK[A-E]_CLOCK_ENABLE`, `PHY[A-E]SYMCLK_CLOCK_CNTL`, and `FORCE_SYMCLK_DISABLE`.
- DCCG DTO/timebase blocks include `DCCG_DS_DTO_*`, `DCCG_DS_CNTL`, `DCCG_GTC_*`, `DP_DTO[0-3]_*`, `DTBCLK_DTO[0-3]_*`, `DPPCLK[0-3]_DTO_PARAM`, `DPPCLK_DTO_CTRL`, `DSCCLK[0-2]_DTO_PARAM`, `DSCCLK_DTO_CTRL`, `HDMISTREAMCLK0_DTO_PARAM`, `DCCG_AUDIO_DTO*`, `DCCG_AUDIO_DTBCLK_DTO_*`, `MILLISECOND_TIME_BASE_DIV`, and `MICROSECOND_TIME_BASE_DIV`.
- `OTG[0-3]_PIXEL_RATE_CNTL`, `OTG[0-3]_PHYPLL_PIXEL_RATE_CNTL`, and the related DP/DTB DTO phase/modulo registers define pixel-rate source selection, DP/DTB DTO enables and status bits, add/drop pixel controls, half-rate output, DTO source selection, FIFO/error counters, and PLL source selection for four timing generators.
- `DCCG_PERFMON_CNTL`, `DCCG_PERFMON_CNTL2`, `DCCG_CAC_STATUS*`, `DCCG_VSYNC_*`, and `DCCG_VSYNC_CNT_*` expose DCCG performance/debug state, clock measurement gates, CAC readback, and vsync latch/counter interrupt controls.
- `DC_PERFMON0_*` and `DC_PERFMON1_*` define two DCCG perfmon instances. Each has event selection, counted-value selection, increment mode, hardware stop selection, run-enable mode, count-off/restart/interrupt controls, counter active and selector fields, per-counter state multiplexing for counters 0-7, perfmon state/report count, count-off interrupt status/ack, clock enable, run start/stop selectors, per-counter interrupt status/ack, and high/low counter readback.
- `DMCU_*` defines DMCU reset/enable/status, firmware start/end/ISR/checksum registers, ERAM/IRAM host access controls, software/internal interrupt triggers and status, static-screen interrupts, ABM and DCPG power-domain interrupt status/clear bits, vblank and OTG range-timing update interrupts, interrupt masks to host and to UC, IRQ/XIRQ routing, scratch storage, interrupt counters, firmware-checksum byte positions, and microcontroller clock-gating controls.
- `MASTER_COMM_*` and `SLAVE_COMM_*` define byte-packed mailbox data, command, and interrupt/progress fields for host-to-DMCU and DMCU-to-host communication.
- `DMCU_PERFMON_INTERRUPT_STATUS[1-3]` begins an aggregated perfmon interrupt-status map for DMU, DIO, DCCG, HPO, HUBP0-7, HUBBUB, and DPP0-5 counters. The chunk ends at `DMCU_PERFMON_INTERRUPT_STATUS3__DPP5_PERFMON_COUNTER_INT_CLEAR_MASK`, so the DPP6/DPP7 masks and any later fields continue outside this work item.

All exported names follow the generated convention `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. They are meant to be paired with generated register-address headers and AMD display register helper macros.

## Control Flow

This chunk has no direct C control flow. Runtime behavior appears in callers that:

1. Select a DCN 3.1.2 register address for a block instance.
2. Use the matching `_SHIFT` and `_MASK` macro to encode or extract a field value.
3. Perform MMIO read/modify/write, polling, or interrupt-ack operations through AMDGPU/DC register helpers.

The register groups imply several hardware programming flows. HDA setup uses controller reset/flush, ring base and size programming, CORB/RIRB DMA enable, immediate command submission, busy/result-valid polling, and interrupt/status handling. DCCG setup programs clock sources, DTO phase/modulo values, dividers, gating disables, soft resets, and status/done polling before display pipes consume clocks. OTG pixel-rate programming selects PLL/DTO sources, enables DP/DTB DTOs, and may inspect FIFO/error counters. DMCU setup controls microcontroller reset and host RAM access, loads firmware-related addresses/checksums, enables communication interrupts, routes events to the host or UC IRQ/XIRQ pins, and clears interrupt status bits.

## State And Persistence Behavior

The macros themselves are compile-time constants and carry no runtime state. The MMIO registers they describe are persistent device state until overwritten by the driver, hardware reset, power-gating transitions, suspend/resume, firmware actions, or display mode changes.

Stateful hardware represented in this chunk includes HDA CORB/RIRB ring pointers and base addresses, immediate command busy/result state, stream interrupt state, audio DMA position-buffer address and enable state, VGA register state, DISPCLK/DPPCLK/DCCG divider and clock gating state, DTO phase/modulo accumulators, OTG pixel-rate source and error counters, DCCG perfmon counter programming/readback, vsync latch values and interrupt masks, DMCU reset/running state, DMCU ERAM/IRAM host-access windows, interrupt pending/clear/mask/routing state, mailbox bytes and command bits, and aggregated perfmon interrupt pending/clear fields.

Several definitions share the same bit for status and clear names, for example `*_INT_OCCURRED` and `*_INT_CLEAR`, or perfmon counter interrupt occurred/clear fields. The masks do not encode access semantics, so callers must know whether a field is read-only, write-one-to-clear, write-one-to-set, latched, or ordinary read/write from the hardware specification and existing driver conventions.

## Dependencies And Integration Points

This header depends on the rest of the generated DCN 3.1.2 ASIC register set: address headers, offset headers, register-list tables, and AMDGPU/DC helper macros that combine `*_MASK` and `*_SHIFT` with MMIO reads and writes. It is not useful as a standalone API.

The integration points are AMDGPU DRM display code paths for:

- DC audio/HDA programming and HDMI/DP audio command transport.
- Legacy VGA compatibility register access during early display bring-up or VGA modes.
- DCCG clock selection, display clock changes, DP/HDMI stream clocks, PHY symbol clocks, DSC/DPP DTOs, audio DTOs, and timing-generator pixel-rate programming.
- Display debug/performance monitor setup and readback.
- DMCU/DMU firmware communication, interrupt routing, ABM/static-screen events, DCPG power-domain notifications, vblank/range-timing events, and perfmon interrupt aggregation.

The repeated suffixes and instance numbers matter. Controller, endpoint, PHY, OTG, DTO, perfmon, HUBP, DPP, and interrupt-bank macros are consumed by per-instance register tables; changing a generated name or mask can break compile-time references or, worse, route writes to an adjacent bitfield while preserving a valid C expression.

## Risks And Edge Cases

- Shift/mask drift is high impact because packed MMIO registers often mix enables, status, clears, selectors, and counters in one 32-bit word. A wrong mask can corrupt neighboring fields during read/modify/write.
- HDA ring programming is sensitive to alignment and width. CORB/RIRB lower-base masks reserve low unimplemented bits and expose upper 32-bit address halves; misuse can point audio DMA at an invalid buffer.
- Immediate command fields combine codec address and verb/payload, while status exposes busy/result-valid bits. Callers need correct polling and timeout behavior; the macros only identify bit positions.
- Clock and DTO fields are tightly coupled. Incorrect DCCG dividers, DTO phase/modulo values, or source selections can produce bad pixel/audio clocks, link underflow, or blank displays even when masks are syntactically valid.
- Gating and soft-reset fields can disable clocks used by active display paths or firmware. Programming order and status polling are outside this header.
- OTG pixel-rate controls include add/drop pixel and error-count fields. Treating status/error bits as normal writable configuration could hide real timing or FIFO issues.
- DMCU interrupt fields often use matching occurred/clear masks on the same bit. Generic read/modify/write helpers can accidentally clear latched events if not used with write-one-to-clear semantics.
- DMCU host access to ERAM/IRAM has byte-enable, address auto-increment, and host-access enable controls. Incorrect sequencing can corrupt firmware RAM or read stale data.
- Mailbox registers are byte-packed. Host and firmware must agree on byte order, command ownership, and in-progress/interrupt handshakes; the masks do not enforce protocol state.
- This chunk ends mid-DMCU perfmon interrupt-status group. Whole-file reconciliation must merge later chunks before treating `DMCU_PERFMON_INTERRUPT_STATUS3` as complete.

## Test Signals

- Build coverage should catch missing, renamed, or malformed macro names referenced by DCN 3.1.2 register tables and helper macros.
- Generated-header validation against AMD's register database is the strongest signal for shift/mask correctness, especially for repeated OTG, PHY, perfmon, interrupt, and endpoint blocks.
- Audio runtime tests should exercise HDA reset, CORB/RIRB command transport, immediate codec commands, unsolicited response enablement, stream interrupts, DMA position buffer programming, and HDMI/DP audio playback.
- Display clock and modeset tests should cover DISPCLK/DPPCLK changes, DP/HDMI stream-clock enablement, PHY pixel-clock resync, DTO programming, DSC/DPP DTO controls, and multi-OTG pixel-rate selection.
- Suspend/resume and power-management tests should verify DCCG gate/soft-reset state, DMCU reset/status, DCPG power-domain interrupt handling, and restored mailbox/interrupt masks.
- Debug/perf tests should configure `DC_PERFMON0` and `DC_PERFMON1`, start/stop counters, trigger count-off interrupts, read high/low counter values, and observe DMCU perfmon aggregate interrupt bits.
- Interrupt tests should induce or simulate vblank, OTG range timing update, ABM/static-screen, UC internal, register-read-timeout, and perfmon events, then confirm occurred/status bits are observed and clear bits acknowledge without losing unrelated events.

### subset-b-001803: lines 2467-4750

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 2467-4750

## Purpose

This chunk is generated AMD DCN 3.1.2 register field metadata. It contains no executable C logic; it exposes `__SHIFT` and `_MASK` preprocessor constants that describe bit positions and bit masks for display microcontroller, interrupt, timeout, timer, and display interrupt-controller registers.

The range starts at the tail of `DMCU_PERFMON_INTERRUPT_STATUS3`, covers complete DMCU perfmon interrupt status/routing groups, DMCU DPRX and continued interrupt groups, RBBMIF security/timeout/status fields, DC perfmon2 fields, GPU timer start/read fields, the display interrupt-status continuation chain through `DISP_INTERRUPT_STATUS_CONTINUE25`, and ends at the first field of `DCPG_INTERRUPT_DEST`. The requested range has 2,284 source lines, including 2,193 `#define` lines, 1,095 shift macros, and 1,213 mask macros.

Although the path is under a local `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocation paths, or locks in this range. The interface is the generated field macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: the field mask before callers shift values into or out of the register.

Consumers normally pair these definitions with `dcn_3_1_2_offset.h` register-offset macros through helper APIs such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_READ`, `REG_WRITE`, and the generated `FD_SHIFT`/`FD_MASK` tables.

Major field families in this slice:

- `DMCU_PERFMON_INTERRUPT_STATUS4/5`: occurred/clear bits for writeback, DCCG perfmon2, MMHUBBUB, MPC, OPP, OPTC, HDA, and DSC0-DSC5 perfmon counter interrupts.
- `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK1` through `5`: enable bits that route perfmon counter interrupts to the display microcontroller for DMU, DIO, DCCG, HPO, HUBP0-HUBP7, HUBBUB, DPP0-DPP7, WB0-WB2, MMHUBBUB, MPC, OPP, OPTC, HDA, and DSC blocks.
- `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1` through `5`: XIRQ/IRQ selection bits for the same perfmon interrupt sources.
- `DMCU_DPRX_INTERRUPT_STATUS1`, `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1`, and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1`: occurred/clear, microcontroller-enable, and route-selection fields for DCIO HDP/DPCS, DMUB, I2C, and DPHY fast-training interrupts.
- `DMCU_INTERRUPT_STATUS_CONTINUE`, `DMCU_INTERRUPT_TO_UC_EN_MASK_CONTINUE`, and `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONTINUE`: ABM0/ABM1 ready/update, DCPG domain power up/down, DIO FIFO underflow, DCIO CM/PHY, and DCIO DPCS TX interrupt status and routing fields.
- `DMCU_INT_CNT_CONTINUE`, `DMCU_INT_CNT_CONT2`, and `DMCU_INT_CNT_CONT3`: 8-bit ABM interrupt counters for high-gain ready, local-scene ready, and backlight update events.
- `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONT2`, `DMCU_INTERRUPT_STATUS_2`, and `DMCU_INTERRUPT_TO_UC_EN_MASK_2`: additional DCPG domain16-domain21 power and DCIO DPCS TXA-TXG interrupt route/status/enable fields.
- `DMCUB_RBBMIF_SEC_CNTL`: trust-level and source-ID fields for DMCUB RBBMIF security configuration.
- `RBBMIF_TIMEOUT`, `RBBMIF_STATUS`, `RBBMIF_STATUS_2`, `RBBMIF_INT_STATUS`, `RBBMIF_TIMEOUT_DIS`, `RBBMIF_TIMEOUT_DIS_2`, and `RBBMIF_STATUS_FLAG`: timeout delay/hold, timeout-client decode, operation/read-write status, ACK/mask, per-client timeout disables for clients 0-38, state, FIFO status, read-timeout, and invalid-access diagnostic fields.
- `DC_PERFMON2_*`: perf counter event selection, counted-value type, state selectors for eight counters, perfmon mode/run/clear/start/count-status controls, current-value interrupt status/clear/ack/enable, and 64-bit high/low counter value fields.
- `DC_GPU_TIMER_*`: start-position fields for vupdate, vstartup, vready, flip, no-lock vupdate, and flip-away timing, plus timer read and read-select fields.
- `DISP_INTERRUPT_STATUS` through `DISP_INTERRUPT_STATUS_CONTINUE25`: the IHC display interrupt pending chain for OTG timing events, HUBP flips, DSC/DWB/ABM/DMUB/perfmon interrupts, underflow, HPD and DDC/I2C-related events, AUX/DP sink paths, DMCUB mailbox/timer/general-data interrupts, and continuation-bit links between status registers.
- `DCCG_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST`, and `DMU_INTERRUPT_DEST2`: destination fields for DCCG VSYNC/perfmon events, DMCUB timers/GPINT/mailboxes/outboxes, DMU perfmon, ABM0-ABM5, undefined-address fault, RBBMIF timeout, DMCU internal, and SCP interrupts.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code:

1. DCN 3.1 code includes `dcn_3_1_2_offset.h` and this mask header.
2. Register table initializers use token-pasting helpers such as `SR`, `SRI`, `SRI_DMUB`, `FD_SHIFT`, and `FD_MASK` to turn the generated names into addresses, masks, and shifts.
3. IRQ, resource, HW sequencer, perfmon, and DMUB code use those tables with register helper macros to read, write, update, acknowledge, or route hardware fields.
4. Hardware then interprets the programmed bits as interrupt status, interrupt enable, interrupt destination, timeout, security, timer, or perf counter state.

The macros do not express ordering rules. Callers must still manage DMCUB boot/reset, interrupt mask/ack ordering, write-one-to-clear semantics, timer latch sequencing, perf counter start/stop/reset, and power-domain readiness before touching these registers.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU state:

- DMCU/DMCUB interrupt state: occurred bits, clear bits, routing bits, microcontroller enable bits, IRQ/XIRQ selection, mailbox readiness, GPINT, undefined-address fault, timer, and general-data events.
- Display interrupt-controller state: pending flags across the `DISP_INTERRUPT_STATUS*` continuation chain and destination fields that steer events to the selected interrupt path.
- RBBMIF security and timeout state: trust level/source ID, timeout delay and request hold, timeout client decode, ACK/mask, per-client timeout disable, FIFO state, read-timeout, and invalid-access diagnostics.
- DC perfmon state: event/counter selection, counter run/active state, counter values, interrupt status/clear/ack/mask, and counter-low/high value fields.
- GPU timer state: programmed start positions for vertical update/startup/ready/flip-related timestamps and selected timer-read channels.
- ABM and power-domain interrupt counters/status for ready/update and DCPG domain power transitions.

Persistence is hardware-defined. Configuration fields generally remain until reset, modeset, power gating, suspend/resume, or explicit reprogramming. Status, ACK, clear, interrupt, timeout, and counter fields may be sticky, write-one-to-clear, read-only, self-clearing, latched, or dependent on clock/power state. This header only provides bit layouts; consuming driver code and hardware documentation define the side effects.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.1.2 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h` for the corresponding register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/yellow_carp_offset.h` and DCN base-address definitions used by `BASE(reg..._BASE_IDX)`.
- Common AMD display register helpers in `reg_helper.h` and DMUB register helpers in `dmub_reg.h`.
- IRQ source IDs in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, which name events such as RBBMIF timeout and DMCUB outbox interrupts.

Direct include sites in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`

Important integration patterns:

- `dmub_dcn31.c` builds `dmub_srv_dcn31_regs` using `DMUB_DCN31_REGS()`, `DMCUB_INTERNAL_REGS()`, `FD_MASK`, and `FD_SHIFT`, then uses `REG_GET`, `REG_UPDATE`, `REG_WRITE`, and related helpers for DMCUB reset, mailbox pointers, scratch registers, GPINT, firmware windows, and fault/debug state.
- `irq_service_dcn31.c` maps hardware source IDs to DAL IRQ sources and builds interrupt register entries with `IRQ_REG_ENTRY` and `IRQ_REG_ENTRY_DMUB`. The DMCUB outbox path uses DMUB interrupt enable/ack field definitions from the same generated header family.
- `dcn31_resource.c` includes this mask header for broad DCN register tables. In this chunk specifically, `HWSEQ_DCN31_REG_LIST()` references `RBBMIF_TIMEOUT_DIS` and `RBBMIF_TIMEOUT_DIS_2`, so the timeout-disable masks are part of display hardware-sequencer configuration.

## Risks And Edge Cases

- Generated field drift is the central risk. A wrong shift or mask compiles cleanly but makes `REG_UPDATE`/`REG_GET` touch the wrong bits in MMIO registers.
- Interrupt fields are side-effect-sensitive. Confusing occurred, clear, ack, mask, enable, route-select, and destination fields can cause stuck interrupts, missed interrupts, interrupt storms, or routing to the wrong handler.
- Many status and clear fields intentionally share the same bit position and mask. Generic read/modify/write code must respect write-one-to-clear and ACK semantics rather than treating every field as normal storage.
- The `DISP_INTERRUPT_STATUS*` chain uses continuation bits. Incorrect masks for continuation fields can hide pending interrupts in later status registers or make software believe no further status register needs inspection.
- DMCUB mailbox/timer/GPINT/undefined-address-fault bits sit on firmware communication paths. Incorrect masks can break command completion, outbox notification, diagnostics, or firmware recovery.
- RBBMIF timeout controls are diagnostic and fault-containment sensitive. Bad timeout-disable masks can either hide real bus timeouts or falsely report hangs and invalid accesses.
- Perfmon masks affect debug and telemetry paths. Incorrect event, active, interrupt, or counter-value fields can corrupt performance counters or leave perfmon interrupts uncleared.
- ABM and DCPG power-domain interrupt fields span multiple continuation registers and destination registers. Instance-number mistakes can affect only higher ABM instances or specific display power domains, making issues hardware-configuration dependent.
- This is an artificial chunk. It starts at the tail of `DMCU_PERFMON_INTERRUPT_STATUS3` and stops after the first `DCPG_INTERRUPT_DEST` field; adjacent chunks are required for complete file-level claims.

## Test Signals

Useful validation combines generated-header consistency checks with hardware behavior:

- Build AMDGPU/DC with DCN 3.1 support enabled; missing or renamed field macros should fail in `dmub_dcn31.c`, `irq_service_dcn31.c`, `dcn31_resource.c`, and their register-table initializers.
- Mechanically compare every `__SHIFT`/`_MASK` pair in lines 2467-4750 against AMD's authoritative DCN 3.1.2 register database and the matching `dcn_3_1_2_offset.h` register names.
- Validate that every field used by `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_SHIFT`, and `FD_MASK` in DCN 3.1 paths has the expected mask width and shift position.
- Exercise DMCUB boot/reset, GPINT commands, inbox/outbox notification, firmware diagnostics, undefined-address fault reporting, suspend/resume, and recovery from forced DMCUB hangs.
- Exercise interrupt delivery for vblank/vstartup, vupdate no-lock, page flip, HPD/HPDRX, DMCUB outbox, ABM ready/update, DCPG power transitions, DSC/perfmon, and RBBMIF timeout events.
- Trigger and verify RBBMIF timeout diagnostics where possible: timeout client decode, timeout ACK, mask behavior, invalid-access flags, and per-client timeout-disable programming.
- Run display modesets across one to six pipes, DSC-capable modes, backlight/ABM paths, multi-display configurations, and suspend/resume while watching for stuck interrupts, lost vblank/pageflip events, hotplug storms, DMCUB mailbox stalls, RBBMIF timeout messages, and perfmon interrupt leaks.

## Cross-Chunk Notes

Previous chunks own the beginning of the DMCU perfmon interrupt status area, including most of `DMCU_PERFMON_INTERRUPT_STATUS3`. Later chunks continue `DCPG_INTERRUPT_DEST` and the remaining DCN 3.1.2 shift/mask namespace. The final per-file research document should merge adjacent chunks before making complete claims about all DMCU, DCPG, DMUB, IRQ destination, or display interrupt-controller fields in `dcn_3_1_2_sh_mask.h`.

### subset-b-001804: lines 4751-7217

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 4751-7217

## Purpose

This chunk is generated AMD DCN 3.1.2 register field metadata. It contains no executable C logic; it publishes `#define` constants for bit shifts and bit masks used to access fields inside display-controller MMIO registers. Consumers include this file together with `dcn_3_1_2_offset.h`, build register tables, and then use helpers such as `REG_GET`, `REG_UPDATE`, `REG_SET`, and DMUB `FD_MASK`/`FD_SHIFT` expansions to read or program individual hardware fields.

The requested range starts in the tail of the interrupt-destination field block and then covers complete field definitions for DC interrupt routing, DMU miscellaneous control, display-controller power-gating control, DMCUB memory/window/mailbox/control registers, display writeback top/control/color-processing registers, a writeback perfmon instance, and the beginning of legacy VGA control. The range has 2,153 `#define` lines: 1,077 `__SHIFT` macros and 1,076 `_MASK` macros. The one-count mismatch is caused by the artificial chunk boundary beginning after `DCPG_INTERRUPT_DEST__DCPG_IHC_DOMAIN0_POWER_UP_INTERRUPT_DEST__SHIFT`, while its mask is still present in this chunk.

Although the path is under a local `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocation paths, or locks in this range. The public interface is the generated macro naming scheme:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

These macros are consumed through register-helper token pasting. Examples include `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `REG_GET(reg, field, ...)`, and `REG_UPDATE(reg, field, value)`. The offset header identifies which MMIO register to touch; this mask header identifies which bits inside that register are meaningful.

Major field families in this chunk:

- Interrupt destination fields for `DCPG`, `MMHUBBUB`, `WB`, `DCHUB`, `DPP`, `MPC`, `OPP`, `OPTC`, `OTG0` through `OTG5`, `DIG`, `I2C_DDC_HPD`, `DIO`, `DCIO`, `HPD`, `AZ`, `AUX`, `DSC`, and `HPO`. These fields route display, hotplug, audio, AUX, DSC, high-performance output, perfmon, vblank, vline, timeout, underflow, and power-transition interrupts.
- `dce_dc_dmu_dmu_misc_dispdec`: `CC_DC_PIPE_DIS`, `DMU_CLK_CNTL`, `DMU_MEM_PWR_CNTL`, SMU/DMCU interrupt controls, zero-shutdown controls/status, and deep-sleep force allowance.
- `dce_dc_dmu_dc_pg_dispdec`: power-gating config/status for domains 0 through 3 and 16 through 18, DCPG interrupt status/control registers, and `DC_IP_REQUEST_CNTL`.
- `dce_dc_dmu_dmcub_dispdec`: DMCUB region offsets/top addresses, region-3 code-window base/top/offset registers, interrupt enable/status/ack/type, external interrupt context, fault-address registers, security and memory control, inbox/outbox ring base/size/read/write pointers, timers, scratch registers, general-purpose interrupt data, low-speed wake enable, processor ID, and DMCUB enable/reset control.
- `dce_dc_wb0_dispdec_dwb_top_dispdec`: DWB clock and memory power, frame-capture mode/flow/window/source geometry, update control, CRC masks/values, output control, backpressure counters, host-read control, overflow status/counter, soft reset, and debug control.
- `dce_dc_wb0_dispdec_dwbcp_dispdec`: DWB HDR multiplier, gamut remap controls and coefficient matrices, output gamma LUT access/control, and RAM A/RAM B piecewise region/start/end/offset fields for red/green/blue channels.
- `dce_dc_wb0_dispdec_wb_dcperfmon_dc_perfmon_dispdec`: `DC_PERFMON3` counter-select/control/state/counter-value/high/low fields and interrupt status/ack fields.
- `dce_dc_mmhubbub_vga_dispdec`: initial VGA render, sequencer reset, mode, surface pitch/height, memory base, dispbuf surface address, HDP, cache, and D1/D2 VGA control fields.

## Control Flow

This header has no runtime control flow. Runtime control is supplied by AMDGPU display code that includes the generated register maps:

1. DCN 3.1 resource, IRQ, and DMUB code include `yellow_carp_offset.h`, `dcn/dcn_3_1_2_offset.h`, and `dcn/dcn_3_1_2_sh_mask.h`.
2. Resource and IRQ code build register-address tables with `SR`, `SRI`, `SRII`, and related macros using the offset header.
3. Field tables and register helpers use this chunk's `__SHIFT` and `_MASK` constants to isolate or update register fields.
4. Driver runtime paths sequence operations such as DMCUB reset/release, DMCUB firmware backdoor load, inbox/outbox ring updates, IRQ acknowledgement, display power gating, DWB capture, perfmon setup, hotplug/AUX servicing, and VGA fallback control.

The masks do not encode register ordering. Consumers still must obey hardware sequencing around clock enables, power gating, reset assertion/release, interrupt clear/ack semantics, ring-buffer pointer ordering, secure-window setup, writeback update locking, LUT access sequencing, and suspend/resume restoration.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on disk. It describes fields in MMIO-backed GPU state. The represented hardware state includes:

- Interrupt routing and delivery state for display pipes, hub, writeback, audio, hotplug, AUX/DDC, DSC, HPO, and performance counters.
- DMU and DCPG state for clock control, memory power, zero-shutdown, SMU/DMCU interrupt interaction, display-domain power-gating config/status, and DC IP request handshake bits.
- DMCUB persistent runtime state while the display microcontroller is active: code/data window layout, top/base/offset values, inbox/outbox ring pointers, scratch registers, timer registers, GPINT command/status fields, fault addresses, security control, and reset/enable bits.
- DWB state for capture geometry, output format/alpha/depth/packing, CRC generation, overflow/backpressure accounting, host-read behavior, memory/clock power, and soft reset.
- DWB color-processing state for HDR multiplier, gamut remap coefficients, output gamma LUT index/data, LUT mode, piecewise curve regions, offsets, bases, and slopes.
- Perfmon state for selected counters, event/state selections, repeat count, counter high/low values, overflow/counter-off interrupt status, and ack bits.
- VGA state for blink/render behavior, sequencer reset behavior per display, legacy memory aperture/base/addressing, cache behavior, HDP reset/memory disable, and per-display VGA enable/timing/rotation.

Persistence is hardware-defined. Many configuration fields remain until modeset, power-gating transition, firmware reset, suspend/resume, or ASIC reset. Status, ack, fault, overflow, timer, pointer, and interrupt fields may be sticky, write-one-to-clear, self-clearing, read-only, or sequencing-sensitive. This generated header does not label those semantics; the consuming driver code and hardware programming guide determine safe access patterns.

## Dependencies And Integration Points

This chunk must match the DCN 3.1.2 generated register database and the companion offset file:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h`
- SOC base-address headers such as `yellow_carp_offset.h`
- Register helper layers in AMD display and DMUB code that define field-access macros from the `__SHIFT` and `_MASK` constants.

Direct include sites found in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`

The integration pattern is field-table construction and token-pasted register access. `dcn31_resource.c` uses field macros for display block setup, including DWB, DMCUB/DMUB-assisted features, pipe/resource programming, and register helper accessors. `irq_service_dcn31.c` maps interrupt sources and uses the same register map for display IRQ status/ack plumbing. `dmub_dcn31.c` builds `dmub_srv_dcn31_regs` with both register offsets and `DMUB_DCN31_FIELDS()` shift/mask arrays, then uses those fields in reset, firmware loading, mailbox/ring, GPINT, scratch, and framebuffer-address translation paths.

## Risks And Edge Cases

- Generated macro drift is the central risk. A wrong shift or mask compiles as an integer constant but can silently read, clear, or update the wrong hardware bits.
- Interrupt destination and ack/status fields are side-effect-sensitive. Bad masks can misroute interrupts, leave sticky status uncleared, acknowledge unrelated events, or break vblank/vline/page-flip/hotplug/AUX/audio/DSC/HPO handling.
- The chunk starts in the middle of `DCPG_INTERRUPT_DEST`; file-level reconciliation must combine adjacent chunks before making complete claims about that register.
- DMCUB fields are high impact. Region windows, top/base/offset values, ring pointers, security/reset controls, fault addresses, scratch registers, and GPINT fields are involved in firmware boot and command exchange. Incorrect fields can cause firmware load failure, hangs, lost mailbox messages, or bad fault diagnosis.
- Power-gating fields interact with active display state. Incorrect domain config/status or DC IP request fields can leave blocks powered unexpectedly, gate active hardware, or break resume/low-power paths.
- DWB and DWBCP fields affect capture correctness. Incorrect window/source/update/output/color/LUT/gamut fields can produce corrupted writeback, wrong color, stale LUT values, CRC mismatches, overflow, or host-read failures.
- Perfmon fields are shared diagnostic infrastructure. Bad event selects, counter status, or ack masks can make performance data misleading or leave interrupts stuck.
- VGA fields are legacy but still risky for fallback and early boot paths; mistakes can disable memory access, blank syncs/de, change aperture addressing, or corrupt legacy display output.

## Test Signals

Useful validation combines generated-header consistency checks with hardware behavior:

- Build AMDGPU/DC with DCN 3.1 support enabled; missing or renamed macros should fail in `dcn31_resource.c`, `irq_service_dcn31.c`, and `dmub_dcn31.c`.
- Mechanically verify that each complete field in this line range has both a `__SHIFT` and `_MASK` definition, while allowing the known boundary split for `DCPG_INTERRUPT_DEST`.
- Compare this chunk against AMD's authoritative DCN 3.1.2 register database and adjacent generated headers where compatible fields are expected.
- Exercise DMCUB boot and reset paths: firmware backdoor load, code-window setup, inbox/outbox ring traffic, GPINT stop/ack, scratch registers, timer reads, fault reporting, and suspend/resume.
- Exercise IRQ paths: vblank, vline, page flip, hotplug and HPD RX, AUX/DDC, audio, DSC, HPO, perfmon, and power-transition interrupts. Watch for stuck, missing, or misrouted interrupts.
- Exercise power-management paths involving display-domain power gating, zero shutdown, memory power controls, deep sleep, and DC IP request/status handshakes.
- Test DWB capture with varied source sizes, output formats, alpha/depth packing, CRC, host reads, overflow/backpressure counters, and repeated update programming.
- Validate DWB color processing through gamut remap, HDR multiplier, output gamma LUT programming, and RAM A/RAM B curve selection.
- Run perfmon counter setup/read/interrupt tests for `DC_PERFMON3` and verify counter values and clear/ack behavior.
- Check legacy VGA behavior only where hardware and platform firmware still expose it: sequencer reset blanking, aperture/base addressing, cache invalidate, memory disable, and D1/D2 VGA control.

## Cross-Chunk Notes

Previous chunks own the beginning of the interrupt-destination field area, including the missing first `DCPG_INTERRUPT_DEST` shift in this range. Later chunks continue the VGA field block beyond `D2VGA_CONTROL` and cover the remaining DCN 3.1.2 mask namespace. The final per-file research document should merge adjacent chunks before making complete file-level claims about all interrupt fields, all DWB instances, or the full VGA register set.

### subset-b-001805: lines 7218-9886

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 7218-9886

## Purpose

This chunk is generated AMD DCN 3.1.2 register field metadata. It contains no executable C logic; it publishes preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for memory-mapped display-controller registers. Driver code pairs these constants with offsets from `dcn_3_1_2_offset.h` and uses register helpers to read, write, update, poll, and decode individual fields without hard-coding bit layouts at each call site.

The requested range starts inside the `D2VGA_CONTROL` field group, covers VGA status/interrupt/control fields, MCIF/VGA interface and MCIF writeback fields, MMHUBBUB and DCHUBBUB memory-hub/display-hub fields, Azalia display-audio controller/root/stream/endpoint fields, DCN VM and SDPIF fields, return-path/DCC/CRC/compression-buffer fields, VM context 0 through 15 page-table fields, VM fault reporting fields, and begins the `DC_PERFMON6` performance-monitor block. Although the path is under a local `ceph-client` mirror, this file is AMDGPU display-driver hardware metadata, not Ceph or distributed-filesystem logic.

Within lines 7218-9886 there are 2,062 `#define` lines: 1,032 shift macros and 1,030 mask macros. The imbalance is due to chunk boundaries: the first two visible lines are masks from a preceding `D2VGA_CONTROL` group, and the final line stops before the rest of `DC_PERFMON6_PERFMON_CNTL` and subsequent perfmon masks in the next chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocation paths, or locking primitives in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit index for a field inside the register value.
- `<REGISTER>__<FIELD>_MASK`: already-shifted mask for isolating or updating that field.
- Register families are grouped by comment headers such as `//VGA_STATUS` and generated address-block comments such as `// addressBlock: dce_dc_dchubbubl_hubbub_dispdec`.

Major field families in this chunk:

- VGA and legacy display routing: `D2VGA_CONTROL` tail, `VGA_STATUS`, `VGA_INTERRUPT_CONTROL`, `VGA_STATUS_CLEAR`, `VGA_INTERRUPT_STATUS`, `VGA_MAIN_CONTROL`, `VGA_TEST_CONTROL`, `VGA_QOS_CTRL`, `D3VGA_CONTROL` through `D6VGA_CONTROL`, and `VGA_SOURCE_SELECT`.
- MCIF and display writeback: `MCIF_CONTROL`, write-combine timeout, phase outstanding counters, `MCIF_WB_BUFMGR_SW_CONTROL`, buffer-manager status, buffer pitch, four buffer status/status2 groups, buffer Y/C low/high addresses, luma/chroma size, per-buffer resolution, arbitration, SCLK/NB p-state/self-refresh/clock-gater controls, VMID control, and minimum time-to-outstanding fields.
- DC perfmon blocks: complete `DC_PERFMON4` and `DC_PERFMON5` counter/control/state/value fields and the beginning of `DC_PERFMON6`.
- MMHUBBUB: writeback watermarks, warmup configuration/control/base/region, minimum TTO, memory power status/control, clock control, soft reset, DMU error status, client unit ID, and warmup VMID control.
- Azalia display audio: controller clock/DMA/RIRB/CORB/DTO/status/CRC/memory-power fields; codec root parameters and controls; global audio port connectivity; stream index/data pairs for streams 0 through 15; output endpoint index/data pairs 0 through 7; and input endpoint index/data pairs 0 through 7.
- DCHUBBUB arbitration and hub control: outstanding request limits, saturation/QoS force, DRAM self-refresh and p-state forcing, watermark sets A through D, host-VM pressure/credit/QoS fields, watermark-change handshakes, timeout controls/interrupts, global timer, surface-check addresses, VTG controls, soft reset, clock/DCFCLK controls, latency measurement, ROB overflow status, FMON, and debug index/data.
- DCHUBBUB SDPIF and VM location: SDPIF credit/status/error/snoop fields, physical request controls, forced-IO diagnostics, framebuffer/AGP/HBM address fields, local HBM lock, and SDPIF memory-power state.
- DCHUBBUB return path, DCC, CRC, DET, and compbuf: DCC constant fields for return-path slices, return-path memory-power fields, CRC control/value fields, DCC statistic fields, compbuf settings, DET controls, hub memory-power mode/status, compbuf memory-power controls, and reserved-space fields.
- DCN VM request interface: repeated `DCN_VM_CONTEXT0` through `DCN_VM_CONTEXT15` page-table depth/block-size, base address hi/lo, start logical page hi/lo, and end logical page hi/lo fields, plus default address and VM fault control/status/address fields.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code:

1. DCN 3.1 resource, interrupt, DMUB, hubbub, audio, writeback, and diagnostics code includes `dcn_3_1_2_offset.h` and `dcn_3_1_2_sh_mask.h`.
2. Register-list macros paste register names into offset and mask/shift symbols. Examples from the include sites include `SR(DCHUBBUB_GLOBAL_TIMER_CNTL)`, `SR(DCHUBBUB_ARB_HOSTVM_CNTL)`, `SR(DCHUBBUB_CRC_CTRL)`, `SR(AZALIA_AUDIO_DTO)`, and `MCIF_WB_COMMON_MASK_SH_LIST_DCN30`.
3. Field helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, and generated `SF(...)`/`HWS_SF(...)` lists use the `__SHIFT` and `_MASK` constants to pack writes and decode reads.
4. Hardware sequencing occurs in consumers: modeset and plane programming update DCHUBBUB watermarks and clocks; DMUB reads DCN VM framebuffer base/offset fields; writeback code controls MCIF buffers; audio code programs Azalia/AFMT-facing state; IRQ paths handle status, clear, and interrupt-mask fields.

The macros do not encode ordering requirements. Consumers must still respect display clock and power domains, register access ordering, write-one-to-clear behavior, interrupt acknowledgement, watermarks and p-state handshakes, VM context programming order, and suspend/resume restore sequencing.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU state. The represented hardware state includes:

- Sticky and current VGA access, display-switch, and auto-trigger status plus interrupt masks and clear bits.
- MCIF writeback buffer manager state: active/current/next buffer, software and VCE locks, overrun/overflow, buffer tags, line counters, pitch, dimensions, addresses, and address fencing.
- Memory-hub and display-hub performance state: outstanding request counters, QoS, saturation, watermark programming, self-refresh and p-state permission, clock gating, soft reset, timeout detection, ROB overflow, frame/vline snapshots, debug buses, and perf counters.
- Audio state in Azalia registers: DMA stream control, ring-buffer/CORB/RIRB behavior, cyclic-buffer position/synchronization, payload capabilities, endpoint index/data windows, codec power/reset/control fields, CRC controls/results, and memory-power state.
- DCN VM state: framebuffer aperture, AGP aperture, local HBM bounds/lock, per-VMID page-table roots and address ranges, default/fault address, VM fault status, faulting VMID/table-level/pipe, and interrupt enable/clear policy.
- DCHUBBUB return-path state: DCC configuration constants, CRC capture source and values, DCC statistics, DET/compbuf allocation and reserved-space controls, and related memory-power status.

Persistence is hardware-defined. Configuration registers typically retain values until modeset reprogramming, power gating, suspend/resume, or ASIC reset. Status, fault, debug, counter, clear, ack, and memory-power fields may be read-only, sticky, self-clearing, write-one-to-clear, or sequencing-sensitive. This generated header only states field locations; it does not identify access type or side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.2 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h`, which supplies the matching MMIO offsets and base indices.
- SOC15/DCN base-address definitions such as `DCN_BASE__INST0_SEG*`, used by `BASE(...)` and `REG_OFFSET(...)` helpers.
- Common DC register helper macros that consume shift/mask pairs, including `REG_GET`, `REG_SET`, `REG_UPDATE`, generated field-list macros, and DMUB register access wrappers.

Direct include sites found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`

Notable integration examples:

- `dmub_dcn31.c` includes this header and uses `REG_GET(DCN_VM_FB_LOCATION_BASE, FB_BASE, ...)` and `REG_GET(DCN_VM_FB_OFFSET, FB_OFFSET, ...)`, so the `DCN_VM_*` masks in this range directly affect DMUB framebuffer address discovery.
- `dcn31_resource.c` builds hubbub/hardware sequencer register tables around `DCHUBBUB_GLOBAL_TIMER_CNTL`, `DCHUBBUB_ARB_HOSTVM_CNTL`, `DCHUBBUB_CRC_CTRL`, `AZALIA_AUDIO_DTO`, and `AZALIA_CONTROLLER_CLOCK_GATING`, and pulls MCIF writeback shifts/masks via `MCIF_WB_COMMON_MASK_SH_LIST_DCN30`.
- `irq_service_dcn31.c` includes the same offset and mask headers so generated interrupt-source tables can bind symbolic status/enable/ack fields to the correct hardware bits.

## Risks And Edge Cases

- Field drift is the central risk. These are untyped constants; a wrong shift or mask compiles cleanly but updates or decodes the wrong bits in live hardware.
- Chunk boundaries split field groups. `D2VGA_CONTROL` is incomplete at the start, and `DC_PERFMON6_PERFMON_CNTL` continues after line 9886. File-level conclusions must be reconciled with adjacent chunks.
- Many registers contain mixed read/write and status/clear fields in the same word. Incorrect masks around `*_STATUS`, `*_CLEAR`, `*_ACK`, `*_INT_STATUS`, `ROB_OVERFLOW_CLEAR`, VM fault clear, or SDPIF error clear can lose diagnostics or leave interrupts stuck.
- Watermark, p-state, self-refresh, and host-VM fields are timing-sensitive. Bad DCHUBBUB/MMHUBBUB masks can produce underflow, stutter, p-state transition failures, self-refresh entry/exit bugs, or blanking under memory pressure.
- VM context fields are repeated for VMIDs 0 through 15 and split into high/low halves. A shifted high-page, base, start, or end field can cause display-page-table faults, wrong aperture interpretation, or failures only for specific VMIDs.
- MCIF writeback buffer fields combine ownership, lock, address, size, pitch, and interrupt state. Bad masks can corrupt captured frames, overrun buffers, wedge software/VCE ownership, or mis-handle high address bits.
- Azalia audio fields include DMA, ring-buffer, codec, endpoint index/data, CRC, and memory-power controls. Incorrect field positions can cause HDMI/DP audio loss, underrun, bad channel capability reporting, failed endpoint access, or resume-only audio failures.
- Perfmon, FMON, CRC, DCC statistic, and debug fields are diagnostic surfaces. Incorrect definitions may not break normal display output but can invalidate validation, performance tuning, or automated failure triage.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN 3.1 support enabled. Missing or renamed macros should fail in `dcn31_resource.c`, `irq_service_dcn31.c`, DMUB register code, MCIF writeback tables, hubbub tables, and audio-related tables.
- Mechanically verify shift/mask pairing for lines 7218-9886 while allowing the known boundary exceptions at the beginning and end of this chunk.
- Diff this generated range against AMD's authoritative DCN 3.1.2 register source and nearby generated headers such as later DCN 3.x variants where compatibility is expected.
- Exercise modesets across multiple pipes and display combinations while monitoring hubbub/DCHUBBUB underflow, ROB overflow, timeout, watermark-change, p-state, and self-refresh diagnostics.
- Validate writeback paths with MCIF enabled: buffer rotation, pitch/dimension programming, high/low addresses, lock ownership, interrupt acknowledgement, overrun handling, and captured-frame integrity.
- Validate HDMI/DP audio through Azalia: stream start/stop, DMA/RIRB/CORB behavior, codec power/reset, endpoint index/data access, payload capability reporting, CRC paths, suspend/resume, and underrun handling.
- Exercise VM and fault handling with display surfaces in local framebuffer, AGP/GART-style apertures, and high addresses; watch VM fault status, fault address, VMID, table-level, and pipe fields.
- Enable diagnostic captures where available: DCHUBBUB CRC, DCC statistics, FMON/perfmon counters, timeout interrupts, and debug index/data paths. The observed values should change consistently with workload and clear/ack sequences.
- Watch kernel logs and display diagnostics for stuck interrupts, underflow, audio dropouts, writeback overruns, VM faults, bad framebuffer base discovery by DMUB, resume failures, and validation mismatches in CRC/perf counters.

## Cross-Chunk Notes

Previous chunks own the beginning of the generated DCN 3.1.2 shift/mask file, including most of `D2VGA_CONTROL`. Later chunks continue `DC_PERFMON6` after `DC_PERFMON6_PERFMON_CNTL` and cover the remaining field namespace. The final per-file research document should merge adjacent chunks before making complete claims about all VGA fields, all perfmon fields, or the full `dcn_3_1_2_sh_mask.h` hardware map.

### subset-b-001806: lines 9887-12399

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 9887-12399

## Scope And Purpose

This chunk is generated AMD DCN 3.1.2 register shift/mask metadata. It contains preprocessor constants that describe bit positions (`__SHIFT`) and masks (`_MASK`) for display-controller MMIO registers. The matching `dcn_3_1_2_offset.h` header supplies register offsets; this header supplies the field layout consumed by AMD display register helpers.

The requested range contains 2,106 `#define` lines: 1,052 shift macros and 1,054 mask macros. It starts in the tail of the `DC_PERFMON6_PERFMON_CNTL` mask definitions, completes the rest of perfmon 6, then covers HUBP/HUBPREQ/HUBPRET/cursor/perfmon register fields for HUBP instances 0 and 1. It then starts the same generated register layout for HUBP instance 2 and stops in the middle of `HUBPREQ2_HUBPREQ_MEM_PWR_CTRL`; `REQ_PDE_MEM_PWR_*` masks and the following memory-power status fields continue in the next chunk.

There are no functions, structs, branches, loops, local includes, allocations, locks, or direct runtime side effects in this chunk. The exported surface is macro metadata. Runtime behavior appears when DCN 3.1 resource, HUBP, IRQ, and DMUB code binds these macros into register tables and later uses `REG_SET`, `REG_UPDATE`, `REG_GET`, and related helpers to program or read hardware.

Although the repository path is under a `ceph-client` mirror, this source is AMDGPU display-driver hardware metadata. It does not implement distributed filesystem behavior.

## Register Blocks Covered

The chunk begins with the end of `DC_PERFMON6`, including perfmon count-off mask bits, count-off interrupt type/clock/start-stop selection, counter-value interrupt status and acknowledgement bits, high counter-value readback, and low/high perfmon readback registers.

For `HUBP0`, `HUBP1`, and the beginning of `HUBP2`, the generated `dce_dc_dcbubp*_dispdec_hubp_dispdec` blocks define fields for:

- Surface format, rotation, horizontal mirror, alpha plane enable, address configuration, tiling configuration, primary/secondary viewport start and dimension fields, and chroma-plane viewport equivalents.
- Request sizing for luma and chroma planes: swath height, PTE row height, chunk size, minimum chunk size, metadata chunk size, DPTE group size, and VM group size where present.
- HUBP control state: blank enable/in-blank status, no outstanding requests, soft reset, VTG selection, vready/vsync relation, stop-data behavior during VM activity, unbounded request mode, segment allocation error status, TTU mode/disable, timeout fields, underflow status, and underflow clear.
- Clock-control and measurement-window fields for HUBP, DCFCLK, and DPPCLK timing measurement.

For `HUBPREQ0`, `HUBPREQ1`, and partial `HUBPREQ2`, the range defines request-path fields for:

- Surface pitch, chroma pitch, VMID selection, primary/secondary luma and chroma surface addresses, metadata addresses, in-use address readbacks, and earliest-in-use address readbacks.
- Surface control bits for TMZ and DCC enable/independent-block state across primary, secondary, luma, chroma, and metadata surfaces.
- Flip controls, stereo-sync flip behavior, pending/update-lock status, triple buffering, global swap lock enable, and surface flip interrupt mask/type/status/clear fields.
- Request expansion mode, TTU QoS watermarks, global TTU controls, per-surface and cursor TTU controls, VM aperture and L1 TLB controls, blank offset, destination timing, prefetch timing, vblank/flip/nominal delivery parameters, per-line delivery parameters, cursor request settings, reference-to-pixel clock ratio, DRQ delta limits, and request-path memory power controls/status.

For `HUBPRET0` and `HUBPRET1`, the generated `hubpret` blocks cover detile buffer and post-request processing: plane-1 DET buffer base address, pack-3-to-2 element disable, component crossbar source selection for alpha/Y-G/Cb-B/Cr-R, memory-power controls and status for DMROB and PIXCDC memories, read-line control windows, read-line values/status, and pipe vblank/read-line interrupt mask/type/clear/status fields.

For `CURSOR0_0` and `CURSOR0_1`, the chunk covers cursor and DMDATA fields: cursor enable/mode/request mode, 2x magnification, pitch, lines-per-chunk, address high/low, size, position, hot spot, stereo control, destination X offset, cursor memory power status/control, DMDATA address, control, QoS, status, and software data/update fields.

`DC_PERFMON7` and `DC_PERFMON8` repeat the standard DC performance monitor field layout for HUBP instances 0 and 1. The visible fields include perf counter control, secondary counter control, state/readback fields, perfmon control, perfmon secondary control, interrupt/ack status for counter values, and low/high readback registers.

## Important APIs, Types, And Macros

The important interface is the generated macro naming contract:

- `<register>__<field>__SHIFT` gives the field bit offset in a 32-bit register.
- `<register>__<field>_MASK` gives the field mask.
- Comments such as `//HUBP0_DCSURF_SURFACE_CONFIG` and `// addressBlock: ...` delimit generated register groups but are not compiled APIs.
- Instance prefixes in this chunk include `HUBP0`, `HUBPREQ0`, `HUBPRET0`, `CURSOR0_0`, `DC_PERFMON7`, the matching instance-1 prefixes, and partial instance-2 `HUBP2`/`HUBPREQ2`.

The main DCN 3.1 include path is `display/dc/resource/dcn31/dcn31_resource.c`, which includes `dcn/dcn_3_1_2_offset.h` and this `dcn/dcn_3_1_2_sh_mask.h`. It builds per-HUBP register tables with `HUBP_REG_LIST_DCN30(id)` and initializes shared shift/mask tables using `HUBP_MASK_SH_LIST_DCN31(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN31(_MASK)`. `dcn31_hubp_create()` then constructs HUBP objects through `hubp31_construct()`.

`display/dc/hubp/dcn31/dcn31_hubp.h` maps canonical driver field names to the instance-0 generated macros through `HUBP_SF(...)`. The runtime code can then use generic field names such as `DCSURF_SURFACE_CONFIG.SURFACE_PIXEL_FORMAT`, `DCHUBP_CNTL.HUBP_UNDERFLOW_CLEAR`, `DCSURF_SURFACE_CONTROL.PRIMARY_SURFACE_DCC_EN`, `HUBPRET_CONTROL.CROSSBAR_SRC_Y_G`, `CURSOR_CONTROL.CURSOR_REQ_MODE`, and `DMDATA_CNTL.DMDATA_UPDATED` while resource construction supplies per-instance offsets.

The runtime implementation lives mostly in the DCN10/DCN20/DCN30/DCN31 HUBP code. `dcn31_hubp.c` adds DCN31-specific operations such as unbounded requesting, cursor request mode, soft reset, extended blank programming, and segment allocation error readback. Broader inherited paths program surface config, flips, VM apertures, DCC, viewport, cursor attributes/position, DMDATA, underflow handling, clock control, and register-state readback through these generated masks.

`display/dc/irq/dcn31/irq_service_dcn31.c` includes the same generated header for interrupt register mapping, including HUBPREQ page-flip-related fields. `display/dmub/src/dmub_dcn31.c` also includes the DCN 3.1.2 offset and mask headers so DMUB-facing code can share the same register field definitions.

## Functional Field Groups

Surface and viewport fields describe how a HUBP fetches primary and secondary planes. Pixel format, rotation, mirror, alpha enable, tiling mode, address pipe/interleave configuration, luma/chroma viewport starts and dimensions, and pitch fields must match the framebuffer layout and scaler input expectations.

Address and metadata fields expose the base addresses for luma/chroma primary and secondary surfaces plus metadata planes. The matching in-use and earliest-in-use readback fields let the driver reason about which addresses hardware has consumed during flips and surface updates.

Request-size, TTU, prefetch, vblank, flip, nominal, and per-line delivery fields are the low-level bandwidth scheduling surface. The display mode library computes delivery timing and request sizes; HUBP programming writes those values through fields such as `SWATH_HEIGHT`, `CHUNK_SIZE`, `DPTE_GROUP_SIZE`, `REFCYC_PER_REQ_DELIVERY`, `DST_Y_PREFETCH`, `REFCYC_PER_PTE_GROUP_*`, and `REFCYC_PER_META_CHUNK_*`.

VM and memory-protection fields include VMID selection, VM system aperture bounds, L1 TLB enable/access-mode controls, TMZ bits on surface and metadata paths, and DMDATA VM fault/underflow/late status in the DCN31 mask list. These fields connect scanout fetches to GPU virtual memory, protected memory, and fault reporting.

Flip and update fields handle double-buffered surface changes. `SURFACE_FLIP_PENDING`, `SURFACE_UPDATE_LOCK`, `HUBPREQ_MASTER_UPDATE_LOCK_STATUS`, `SURFACE_TRIPLE_BUFFER_ENABLE`, `SURFACE_GSL_ENABLE`, and flip interrupt fields tell the driver when a pending address/config update has been latched or when it should hold updates for synchronization.

HUBP control fields expose enable/reset/error state. Blanking, in-blank status, no-outstanding-request status, soft reset, VTG selection, unbounded request mode, timeout, underflow, segment allocation error, and TTU controls are used during modeset, blanking, recovery, diagnostics, and bandwidth-sensitive operation.

HUBPRET fields configure data unpacking and component routing after request processing. DET buffer base selection, pack-3-to-2 disable, and component crossbar selections must match plane format and downstream pixel processing assumptions.

Cursor and DMDATA fields provide the per-pipe cursor plane and metadata path. Cursor address, size, mode, request mode, pitch, magnification, position, hotspot, stereo, memory power, and destination offset fields are paired with DMDATA address/control/QoS/status/software update fields for metadata delivery.

Perfmon fields expose hardware diagnostic counters. Counter enable, clear, event selection, threshold, interrupt status/ack, read selection, and low/high counter readback fields are stateful observability surfaces rather than display-mode configuration.

## Control Flow And State Behavior

This header has no direct control flow. Runtime sequencing comes from resource construction and register helper calls:

1. DCN31 resource code includes the DCN 3.1.2 offset and shift/mask headers.
2. Register-list macros paste each instance number into generated names such as `HUBP1_DCHUBP_CNTL`, `HUBPREQ1_DCSURF_SURFACE_CONTROL`, or `CURSOR0_1_CURSOR_CONTROL`.
3. `hubp31_construct()` stores per-instance register offsets plus shared shift/mask tables in each HUBP object.
4. HUBP, IRQ, and DMUB code later use those tables to read, write, poll, clear, or update hardware registers.

Hardware state represented by these fields persists in DCN registers until the driver, DMUB, power-management logic, reset logic, or hardware status events change it. Configuration state includes surface format, tiling, addresses, pitches, viewport, request sizing, TTU/delivery timing, VM aperture, flip policy, cursor attributes, DMDATA attributes, memory-power force/disable bits, and perfmon configuration. Live status includes flip pending, update-lock status, in-use addresses, earliest-in-use addresses, no-outstanding-request, underflow/timeout/segment-error flags, interrupt status, memory-power state, read-line state, DMDATA done/fault/late indicators, and perfmon counter values.

Several groups are ordering-sensitive. Surface address and metadata writes are double-buffered around flip/update controls. TTU and prefetch values must align with timing and watermark calculations before scanout depends on them. Cursor and DMDATA updates require coherent address/control/QoS/status sequencing. Memory-power force or disable fields should not be changed while the corresponding request, cursor, metadata, or HUBPRET memory is actively needed.

## Dependencies And Integration Points

This file must stay synchronized with `dcn_3_1_2_offset.h`. The offset header gives the MMIO addresses for the same register names, while this header gives the field layout. A mismatch can either fail compilation in token-pasted register lists or silently program the wrong bits if both names still exist but no longer describe the same hardware field.

The direct include sites visible in this tree are:

- `display/dc/resource/dcn31/dcn31_resource.c`
- `display/dc/irq/dcn31/irq_service_dcn31.c`
- `display/dmub/src/dmub_dcn31.c`

The primary HUBP integration point is `display/dc/hubp/dcn31/dcn31_hubp.h`, whose `HUBP_MASK_SH_LIST_DCN31` consumes many fields from this chunk. The associated runtime code in `dcn31_hubp.c` and inherited DCN10/DCN20/DCN30 HUBP implementations programs surfaces, DCC, VM, TTU, blanking, flip, cursor, and DMDATA state through these masks.

IRQ integration uses HUBPREQ flip interrupt fields and related masks so page-flip and timing interrupt handling can map source IDs to concrete register bits. DMUB integration shares the same generated definitions for firmware-command register programming and state capture.

The register families are repeated per HUBP instance. Resource construction relies on instance-0 shift/mask definitions as the canonical field layout and combines them with instance-specific offsets. The generated fields for instances 1 and 2 in this chunk therefore serve both as direct metadata and as consistency evidence that the repeated hardware blocks have matching layouts.

## Risks And Edge Cases

Generated-header drift is the central risk. A wrong shift or mask can compile cleanly while corrupting scanout format, address, pitch, tiling, viewport, DCC/TMZ, request sizing, TTU timing, cursor, DMDATA, memory-power, interrupt, or perfmon behavior.

The chunk boundaries are artificial. The first lines are only the tail of `DC_PERFMON6_PERFMON_CNTL`, and the final line stops inside `HUBPREQ2_HUBPREQ_MEM_PWR_CTRL`. Adjacent chunks are required before making complete file-level claims about perfmon 6 or HUBP instance 2.

Bandwidth and timing fields are high impact. Incorrect swath/chunk/group sizes or delivery timings may only fail under high resolution, high refresh rate, DSC, multi-plane, chroma, or bandwidth-pressure scenarios, where symptoms show up as underflow, corruption, missed flips, or unstable power/performance behavior.

Address, VM, TMZ, and metadata fields are security- and stability-sensitive. Incorrect VMID, aperture, surface address, metadata address, or TMZ/DCC mask handling can fetch from the wrong memory, mishandle protected content, trigger VM faults, or produce display corruption that is hard to attribute to a single register field.

Flip and update fields are synchronization-sensitive. Code that mishandles update locks, pending bits, triple buffering, GSL enablement, or interrupt clear/status semantics can lose page flips, report vblank completion too early, or leave a plane stuck on an old surface.

Memory-power fields can create intermittent failures around blanking, suspend/resume, clock gating, and modeset. Forcing or disabling DPTE/MPTE/meta/PDE/cursor/HUBPRET memories at the wrong time can make otherwise valid register programming fail only during power-state transitions.

Perfmon fields are diagnostic state. Wrong event selection, clear/enable ordering, read selection, threshold programming, or interrupt acknowledgement can make profiling data misleading without visibly breaking display output.

## Test Signals

Build-time coverage should catch missing or renamed generated macros in `dcn31_resource.c`, `dcn31_hubp.h`, `irq_service_dcn31.c`, and `dmub_dcn31.c`. High-signal compile failures include missing `HUBP0_*`, `HUBPREQ0_*`, `HUBPRET0_*`, `CURSOR0_0_*`, or `DC_PERFMON*` field names referenced through the register-list macros.

Mechanical validation should compare this chunk against the authoritative DCN 3.1.2 register database and verify that repeated instance families remain structurally consistent across HUBP0, HUBP1, and HUBP2 where covered. The requested range has a nearly one-to-one shift/mask pairing, with imbalance explained by the partial start and partial end.

Runtime display validation should exercise modesets across enough active pipes to use HUBP instances 0, 1, and 2. Useful signals include correct plane format, rotation, mirroring, alpha handling, viewport/crop, pitch, tiling, DCC, TMZ, and chroma-plane behavior.

Bandwidth validation should cover high-resolution and multi-plane modes that stress DML-calculated swath, chunk, group-size, prefetch, vblank, flip, nominal, and per-line delivery parameters. Watch for HUBP underflow, timeout, segment allocation errors, stuck no-outstanding-request state, visual corruption, and watermark-related regressions.

Flip validation should cover immediate flips, vblank-synchronized flips, triple buffering, global swap lock, update lock/unlock, page-flip interrupts, and in-use/earliest-in-use readbacks. Correct behavior is pending bits clearing at the intended update point and no lost or early-completed flips.

Cursor and DMDATA tests should cover cursor enable/disable, mode, size, position, hotspot, 2x magnification, stereo, destination offset, cursor memory power, metadata update/repeat/size, QoS, and DMDATA completion/fault signals.

Power-management and resume tests should exercise blanking, soft reset, clock gating, memory-power controls/status, suspend/resume, hotplug modesets, and repeated stream enable/disable cycles. Perfmon tests should validate clear/enable/readback sequencing for `DC_PERFMON6`, `DC_PERFMON7`, and `DC_PERFMON8` where available.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DC_PERFMON6_PERFMON_CNTL`. The next chunk completes `HUBPREQ2_HUBPREQ_MEM_PWR_CTRL`, covers `HUBPREQ2_HUBPREQ_MEM_PWR_STATUS`, and continues the remaining HUBP instance-2 generated fields. The later merge/reconciliation lane should combine these adjacent chunk documents before presenting complete per-file coverage for `dcn_3_1_2_sh_mask.h`.

### subset-b-001807: lines 12400-14927

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 12400-14927

## Purpose

This chunk is a generated AMD DCN 3.1.2 register field map. It defines C preprocessor constants for bit shifts and masks used by the AMDGPU display driver when programming display pipe fetch, cursor, performance monitor, format conversion, scaler, and color-management hardware. The definitions in this slice do not implement executable logic; they are the ABI between higher-level DC display code and MMIO register layouts for this ASIC generation.

The chunk starts in the tail of the pipe-2 HUBPREQ register block and then covers:

- Pipe-2 HUBPRET read/interrupt/power fields.
- Pipe-2 cursor and display metadata fields.
- Pipe-2 DC performance monitor fields.
- Pipe-3 HUBP/HUBPREQ/HUBPRET/cursor/performance monitor fields.
- DPP0 CNVC format converter and cursor conversion fields.
- DPP0 DSCL scaler fields.
- The beginning of DPP0 CM gamma correction and blend-gamma LUT fields.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or callable APIs in this chunk. The important exported surface is the naming convention of macros:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for the same field.
- `HUBP3_*`, `HUBPREQ3_*`, `HUBPRET3_*`, and `CURSOR0_3_*` identify pipe-3 DC hub pipe fetch, request, return, and cursor registers.
- `HUBPREQ2_*`, `HUBPRET2_*`, and `CURSOR0_2_*` identify the corresponding pipe-2 blocks where this chunk starts.
- `DC_PERFMON9_*` and `DC_PERFMON10_*` expose display performance counter fields for the pipe-2 and pipe-3 perfmon address blocks.
- `CNVC_CFG0_*` and `CNVC_CUR0_*` expose DPP0 format-conversion and cursor-conversion fields.
- `DSCL0_*` exposes DPP0 scaler, line-buffer, output rectangle, and scaler memory-power fields.
- `CM0_CM_GAMCOR_*` and `CM0_CM_BLNDGAM_*` expose color-management gamma correction and blend-gamma controls/LUTs.

These macros are consumed indirectly by generated register-list and field-list macros in display code. For example, DPP definitions use `TF_SF(...)` field entries for `CM0_CM_GAMCOR_CONTROL`, `CNVC_CFG0_PRE_DEGAM`, `DSCL0_SCL_MODE`, and related fields, while HUBP and cursor code uses the pipe-indexed HUBP/HUBPREQ/HUBPRET/CURSOR field names through `REG_SET`, `REG_UPDATE`, `REG_GET`, and similar AMD display register helpers.

## Register Families In This Chunk

### Pipe-2 HUBPREQ/HUBPRET/CURSOR Tail

The chunk begins with the remaining pipe-2 HUBPREQ fields:

- `HUBPREQ2_HUBPREQ_MEM_PWR_STATUS` reports memory-power state for DPTE, MPTE, META, and PDE request buffers.
- `HUBPREQ2_VBLANK_PARAMETERS_5/6` and `HUBPREQ2_FLIP_PARAMETERS_3..6` hold reference-cycle timing for VM and page-table/meta traffic during vblank and flip.

The pipe-2 HUBPRET block then defines:

- `HUBPRET2_HUBPRET_CONTROL` fields for DET buffer plane base, 3-to-2 packing disable, and channel crossbar source selection.
- `HUBPRET2_HUBPRET_MEM_PWR_CTRL/STATUS` fields for DMROB and PIXCDC memory power force/disable/low-power/status.
- `HUBPRET2_HUBPRET_READ_LINE*` and `HUBPRET2_HUBPRET_INTERRUPT` fields for read-line windows, vblank/read-line interrupt mask/type/clear/status, and current/snapshot read-line status.

The pipe-2 cursor block defines:

- Cursor enable, request mode, 2x magnification, mode, TMZ protection, pitch, rotation/mirroring bypass, chunking, and perfmon latency measurement.
- Cursor surface address high/low, size, position, hotspot, stereo offsets, destination offset, cursor memory power status/control, and DMDATA address/control/QoS/status/software-data fields.

### Pipe-2 Performance Monitor

`DC_PERFMON9_*` defines selectable performance-counter controls, low/high values, test/debug controls, counter limits, state control, run/stop selection, interrupt status/ack fields, and 48-bit-ish value composition through low and high/misc registers. These fields let diagnostic code measure display events tied to the pipe-2 HUBP perfmon block.

### Pipe-3 HUBP

`HUBP3_*` starts a full pipe-3 fetch-pipe definition:

- Surface format, rotation, mirroring, alpha plane enable.
- Address/tiling configuration including pipe interleave, compressed fragments, swizzle mode, dimension type, meta-linear, and pipe alignment.
- Primary and secondary luma/chroma viewport start/dimension registers.
- Request sizing for luma and chroma: swath height, linear PTE row height, chunk/min-chunk, meta chunk/min-meta chunk, DPTE group, and VM group.
- Control/status fields for blanking, no-outstanding-request status, soft reset, VTG select, vready timing, stop-data-during-VM behavior, unbounded request mode, segment allocation error, TTU configuration, timeout/underflow status and clear.
- Clock gating and clock-on status for DISPCLK, DPPCLK, and DCFCLK domains.
- VM page size and HUBPREQ debug registers.
- DCFCLK and DPPCLK measurement-window controls for perfmon start/stop events and period selection.

### Pipe-3 HUBPREQ

`HUBPREQ3_*` covers the request side of pipe-3 memory fetch:

- Surface pitch and meta pitch for luma/chroma.
- VMID selection.
- Primary/secondary luma/chroma surface addresses and metadata surface addresses, split into low and high 32-bit register halves.
- Surface control for TMZ, DCC enable, DCC independent-block mode, and metadata TMZ flags.
- Flip control for update locking, flip type, pending status, stereo sync, pending delay, and master update lock status.
- TTU controls for surface 0/1 and cursor 0/1 request delivery timing, fixed QoS level, and QoS ramp disable.
- DCN VM aperture low/high and L1 TLB controls.
- Display logic timing and prefetch fields: blank offsets, `REFCYC_PER_HTOTAL`, after-scaler coordinates, VRATIO prefetch, vblank/flip/nominal PTE/meta timing, line-delivery timing, cursor chunk adjustment, reference-to-pixel frequency ratio, and DRQ limit.
- HUBPREQ memory power control/status for DPTE, MPTE, META, and PDE request memories.

### Pipe-3 HUBPRET, Cursor, And Perfmon

The pipe-3 HUBPRET block mirrors pipe 2, with DET buffer, crossbar, memory power, read-line, vblank/read-line interrupt, and status fields.

`CURSOR0_3_*` mirrors the pipe-2 cursor layout: cursor control, address, size, position, hotspot, stereo control, destination offset, cursor memory power, and DMDATA transport/QoS/status/software data fields.

`DC_PERFMON10_*` mirrors the pipe-2 perfmon definitions for pipe 3.

### DPP0 CNVC And Cursor Conversion

`CNVC_CFG0_*` defines DPP0 format conversion and pre-color processing:

- Surface pixel format and alpha-plane enable.
- Format control for expansion mode, 16-bit conversion, alpha enable, bypass and MSB alignment, positive clamping, update pending, and RGB crossbar mapping.
- Floating-point conversion bias/scale for R/G/B channels.
- Color keyer enable/mode and low/high threshold registers for alpha, red, green, and blue.
- 2-bit alpha LUT entries.
- Pre-dealpha and pre-realpha enable/alpha-blend enable.
- Pre-CSC mode and current mode.
- Pre-CSC matrix coefficients for A and B register banks, packed two 16-bit coefficients per register.
- Pre-degamma mode and LUT select.

`CNVC_CUR0_*` defines converted cursor control and cursor color state for DPP0: enable, expansion, pixel inversion, ROM enable, mode, pixel-alpha modulation, update pending, two 24-bit cursor colors, and floating-point cursor scale/bias.

### DPP0 DSCL

`DSCL0_*` defines DPP0 scaler and line-buffer programming:

- Coefficient RAM tap select/data with tap-pair index, phase, filter type, even/odd coefficient values, and enable bits.
- Scaler mode, coefficient RAM bank select/current/readback, chroma coefficient mode, and alpha coefficient mode.
- Luma/chroma horizontal and vertical tap counts.
- Boundary mode and 2-tap hardcoded coefficient/sharpening controls.
- Manual replicate factors.
- Horizontal/vertical luma and chroma scale ratios plus initial phase integer/fraction values, including bottom-field variants.
- Black color, scaler update pending, autocal mode/pipe identity, overscan, OTG blanking, recout start/size, MPC size, and line-buffer data format.
- Line-buffer memory configuration, partition counts, vertical counters, and scaler/LB memory power force/disable/status fields.
- OBUF memory-power controls appear near the end of the DSCL section.

### DPP0 Color Management

The CM section begins with gamma correction:

- `CM0_CM_GAMCOR_CONTROL`, `CM0_CM_GAMCOR_LUT_INDEX`, `CM0_CM_GAMCOR_LUT_DATA`, and `CM0_CM_GAMCOR_LUT_CONTROL` select gamma-correction mode/bank, LUT address/data, write color mask, read color selection, debug read, host selection, and config mode.
- `CM0_CM_GAMCOR_RAMA_*` and `CM0_CM_GAMCOR_RAMB_*` define double-buffered RAM A/B piecewise-linear region setup for B/G/R: start point, start segment, start slope, start base, end base, end value, end slope, per-channel offset, and packed region definitions.
- Region registers are emitted as pairs, `REGION_0_1` through `REGION_32_33`, with LUT offset and segment-count fields for two regions per register.

The chunk then enters blend gamma:

- `CM0_CM_BLNDGAM_CONTROL`, `CM0_CM_BLNDGAM_LUT_INDEX`, `CM0_CM_BLNDGAM_LUT_DATA`, and `CM0_CM_BLNDGAM_LUT_CONTROL` expose mode/bank, LUT address/data, write color mask, read color select, host select, and config mode.
- It begins the `CM0_CM_BLNDGAM_RAMA_*` region programming block and ends at `CM0_CM_BLNDGAM_RAMA_REGION_18_19`, so the remaining blend-gamma region fields continue in the next chunk.

## Control Flow

This header has no runtime control flow. The effective control flow is in consumers:

1. DC resource construction picks register addresses from matching `dcn_3_1_2_offset.h` entries and field masks/shifts from this header.
2. Display pipe programming computes field values from mode timing, surface layout, cursor state, scaling parameters, color pipeline state, and memory/QoS requirements.
3. Register helper macros combine these `_SHIFT` and `_MASK` constants to read, write, or update packed fields.
4. Hardware state changes through MMIO writes and later exposes status bits through the corresponding status macros.

For double-buffered color LUTs and scaler coefficient RAM, the driver writes index/control/data fields and selects the active bank. Current-mode/current-select and update-pending fields are the observable completion handshakes.

## State And Persistence Behavior

The state described by these macros is hardware register state, not software-owned persistent storage. It persists in the display engine until changed by another driver write, reset, power-gating transition, suspend/resume reprogramming, or hardware status update.

Important state categories:

- Surface state: addresses, metadata addresses, pitch, tiling, viewport, DCC, TMZ, VMID, and flip/update-lock state.
- Timing/QoS state: TTU delivery, prefetch, vblank/flip/nominal PTE/meta timing, line-delivery, DRQ limit, and reference-to-pixel-frequency conversion.
- Cursor state: image address, size, position, hotspot, mode, DMDATA, and memory-power state.
- Diagnostic state: perfmon counter values, limits, run/stop selection, and interrupt ack/status bits.
- Color/scaler state: scaler coefficients/ratios, CNVC/pre-CSC/pre-degamma settings, gamma/blend-gamma LUT content, active RAM bank, and update-pending/current fields.
- Power state: HUBPREQ/HUBPRET/cursor/DSCL memory force/disable/status fields and clock-gating controls.

Status, pending, done, underflow, timeout, and interrupt fields can be hardware-mutated. Clear/ack fields are write-side controls and must be handled as write-one style side effects according to the register spec.

## Dependencies

This chunk depends on the AMDGPU display register programming framework:

- Matching address macros in `dcn_3_1_2_offset.h`; masks and shifts are only useful when paired with the correct MMIO address.
- Register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WRITE`, and generated `*_SF`/`*_SRI` list macros used throughout `drivers/gpu/drm/amd/display`.
- DPP register/field list definitions in files such as `display/dc/dpp/dcn30/dcn30_dpp.h`, which reference many `CM0`, `CNVC_CFG0`, `CNVC_CUR0`, and `DSCL0` fields from this chunk.
- HUBP, IRQ, DMUB, and HW sequencing code that consumes pipe-indexed HUBP/HUBPREQ/HUBPRET/CURSOR and perfmon fields.
- Hardware-generated register specifications for DCN 3.1.2; the source is not hand-authored business logic.

## Integration Points

- HUBP/HUBPREQ/HUBPRET fields integrate with plane address programming, page-table/DCC metadata fetch, flip scheduling, VM/TLB setup, underflow handling, clock/power gating, and display diagnostics.
- Cursor fields integrate with DRM cursor plane updates, protected content/TMZ, cursor DMDATA transport, cursor memory power management, and cursor color conversion.
- Perfmon fields integrate with display debug/performance tooling and counter-based interrupt/status handling.
- CNVC fields integrate with input pixel format conversion, pre-CSC, pre-degamma, alpha handling, color keying, and DMUB-assisted cursor state capture.
- DSCL fields integrate with scaling setup, scaler coefficient downloads, line-buffer partitioning, overscan/recout/MPC sizing, and scaler memory power.
- CM fields integrate with color management APIs that program gamma correction, blend gamma, shaper/gamut paths, and LUT bank switching.

## Risks And Edge Cases

- Mask/shift drift from the ASIC specification is high impact: a one-bit error can silently program the wrong hardware field, corrupt display output, break flips, or disable memory blocks.
- Pipe-indexed duplication is easy to misuse. A pipe-3 field name must be paired with pipe-3 addresses; mixing pipe 2/3 address and mask sets can program the wrong display pipe.
- Low/high address halves require correct ordering and synchronization with update locks. Partial address updates can point the display engine at invalid memory.
- Protected content/TMZ bits appear on surfaces, metadata, cursors, and DMDATA. Incorrect settings can break protected playback or violate memory-access expectations.
- Clear/ack/status fields share packed registers with mask/type bits in interrupt and perfmon controls. Read-modify-write helpers must avoid acknowledging interrupts or clearing error states unintentionally.
- Double-buffered LUT and coefficient RAM fields require correct bank selection and update sequencing. Writing the inactive bank without switching, or switching before upload completion, produces wrong color/scaler output.
- Hardware-mutated fields such as `*_CURRENT`, `*_UPDATE_PENDING`, `*_DONE`, `*_UNDERFLOW`, timeout, and memory-power status cannot be treated as ordinary cached software state.
- This chunk ends mid-family in the blend-gamma RAMA region list; any analysis or generated tables for `CM0_CM_BLNDGAM_RAMA_*` must include the next chunk before concluding the full register family.

## Test Signals

Useful validation signals for changes touching this header or its consumers:

- Compile coverage for AMDGPU display with DCN 3.1.2 enabled; generated field names must still satisfy all `TF_SF`, `SRI`, and register-helper references.
- Boot/runtime smoke on DCN 3.1.2 hardware or emulator: modeset, page flip, plane enable/disable, cursor movement, cursor format changes, suspend/resume, and hotplug.
- Display correctness under scaling: identity, upscaling, downscaling, chroma formats, interlaced/bottom-field initialization if supported, overscan, and MPC sizing.
- Color pipeline checks: pre-degamma, pre-CSC, gamma correction, blend gamma, LUT bank switching, and current/update-pending handshakes.
- Memory/QoS stress: DCC surfaces, metadata fetch, VM/TLB enabled surfaces, vblank and flip prefetch timing, underflow/timeout status, and recovery clear paths.
- Protected-content tests where TMZ cursor/surface/metadata/DMDATA bits are expected.
- Perfmon tests that program counter selection/limits, read low/high values, and verify interrupt status/ack behavior without disturbing unrelated fields.

### subset-b-001808: lines 14928-17438

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 14928-17438

## Purpose

This chunk is generated AMD DCN 3.1.2 register field metadata. It contains no executable C logic; it publishes C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for display-pipe registers. Runtime code combines these constants with matching register offsets from `dcn_3_1_2_offset.h` through helper macros such as `FD_SHIFT`, `FD_MASK`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`.

The requested range is a large mid-file slice of `dcn_3_1_2_sh_mask.h`. It starts inside the `CM0_CM_BLNDGAM_RAMA_REGION_18_19` definition set, covers the rest of CM0 blend-gamma RAM A/B and CM0 shaper/3D LUT/test-debug fields, then moves through DPP0 top-level CRC/control fields, DC perfmon instance 11, DPP1 conversion/cursor/scaler fields, and most of DPP1 color-management fields through `CM1_CM_MEM_PWR_STATUS`. The final requested line is only the `//CM1_CM_DEALPHA` comment; the actual `CM1_CM_DEALPHA` field definitions begin in the following chunk.

Although this tree path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata, not Ceph or distributed-filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this range. Its interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset of a field inside a 32-bit MMIO register value.
- `<REGISTER>__<FIELD>_MASK`: the field mask, already shifted into register position.

This chunk contains 2,113 `#define` lines: 1,056 shift macros and 1,057 mask macros. The one-count difference is from the artificial line boundary: line 14928 includes only the `NUM_SEGMENTS__SHIFT` for `CM0_CM_BLNDGAM_RAMA_REGION_18_19`, while the corresponding first field shift at line 14927 is outside this chunk.

Major register families covered:

- `CM0_CM_BLNDGAM_*`: tail of CM0 blend-gamma RAM A region descriptors, complete RAM B start/end/base/slope/offset/region descriptors, LUT index/data/control, HDR multiplier, memory power control/status, dealpha, coefficient format, and test debug fields.
- `CM0_CM_SHAPER_*`: shaper control, per-channel offsets/scales, LUT index/data/write-enable, RAM A/B start/end and 34-region segment descriptors, and second memory-power control/status.
- `CM0_CM_3DLUT_*`: 3D LUT mode, index, data, 30-bit data path, read/write control, output normalization, and per-channel output offsets.
- `DPP_TOP0_*`: DPP0 control, soft reset, CRC readback/control, CRC component selection, shadow/readback controls, and host read control.
- `DC_PERFMON11_*`: perfcounter control/state, perfmon control, current-value capture, high/low counter values, windowing, event select, clear, enable, and mode fields.
- `CNVC_CFG1_*`: DPP1 surface pixel format, format control, fixed-point conversion bias/scale, color keyer, alpha 2-bit LUT, pre-dealpha, pre-CSC mode/matrix coefficients, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR1_*`: DPP1 cursor0 enable/mode/2x magnification/pitch/format/position fields, cursor colors, and FP scale/bias.
- `DSCL1_*`: DPP1 scaler coefficient RAM tap select/data, scaler mode, tap control, DSCL control and 2-tap parameters, manual replicate, horizontal/vertical/chroma scale ratios and filter initial phases, overscan, output timing blanking, recout/MPC size, line-buffer format and memory controls, DSCL memory power, output-buffer control and memory power.
- `CM1_CM_*`: DPP1 color-management control, post-CSC and gamut-remap matrices, bias formats/values, gamma-correction RAM A/B descriptors, blend-gamma RAM A/B descriptors, LUT access fields, HDR multiplier, and memory power control/status.

## Control Flow

The header itself has no runtime control flow. The effective runtime path is generated macro expansion:

1. DCN 3.1 resource, IRQ, and DMUB code include `dcn_3_1_2_offset.h` and this mask header.
2. Register-list macros build per-block register tables from offset macros, while mask/shift-list macros build companion field tables from this file.
3. DPP, HW sequencer, DMUB, and IRQ code call register helpers such as `REG_SET_*`, `REG_UPDATE_*`, `REG_GET_*`, and `REG_WAIT`; those helpers use this chunk's masks and shifts to isolate or update individual fields without hand-coded bit arithmetic.
4. Hardware sequencing is implemented by consumers, not by this header. Consumers decide when to power up DSCL/CM memories, load LUTs, program scalers and color matrices, read CRC/perf counters, or clear/reset blocks.

The fields in this chunk participate in modeset and plane programming flows: DPP format conversion and cursor setup occur before scanout, scaler ratios/taps and line-buffer state are programmed during plane scaling setup, color-management LUTs and matrices are programmed during color pipeline updates, and CRC/perfmon fields are used by diagnostics or debug paths.

## State And Persistence Behavior

This file stores no software state and persists nothing. It describes MMIO-backed hardware state in DCN display blocks:

- Color-management state: gamma/blend-gamma/shaper/3D LUT banks, region descriptors, per-channel start/end/base/slope values, matrix coefficients, bias values, dealpha/re-alpha controls, HDR multiplier, and coefficient formats.
- Scaler and line-buffer state: DSCL mode, tap counts, 2-tap parameters, filter coefficients, initial phases, scale ratios, recout/MPC dimensions, line-buffer format, memory partitioning, and output-buffer controls.
- Conversion/cursor state: source format, pre-CSC and fixed-point conversion controls, color key values, alpha LUT entries, cursor dimensions/format/position/colors, and FP scale/bias.
- Diagnostic state: DPP CRC selection/readback, soft-reset/control fields, DC perfmon event selection, counter control, high/low counter snapshots, current-value captures, and debug index/data registers.
- Power state: CM, shaper, DSCL LUT, line-buffer, and output-buffer memory power force/disable/status fields.

Persistence is hardware-defined. Programming registers generally retain values until a modeset, pipe reprogramming, power gating, suspend/resume, or ASIC reset. LUT index/data registers are stateful access ports rather than ordinary memory arrays: write ordering, bank selection, write-enable masks, and index resets matter. Status, CRC, perfmon, reset, and memory-power fields may be read-only, sticky, self-clearing, or sequencing-sensitive; this generated header only encodes bit positions, not access semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.2 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h` for the corresponding register offsets and base-index values.
- AMD DC register helper macros in `reg_helper.h`, `dmub_reg.h`, and DPP/HWSS resource headers that paste register and field tokens into `FD_MASK`, `FD_SHIFT`, `SR`, `SRI`, and related expansions.

Direct include sites for this exact generated header in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`

Important consumer areas include:

- DPP transform/scaler/color-management code, especially shared DCN DPP paths that use register tables for `CNVC_CFG`, `CNVC_CUR`, `DSCL`, `DPP_TOP`, and `CM` blocks.
- DCN31 resource construction, where `BASE(reg..._BASE_IDX) + reg...` builds register addresses and mask/shift lists populate typed field tables.
- HW sequencer diagnostic paths that use `DPP_TOP0_DPP_CRC_*` fields for DPP CRC configuration and readback.
- DMUB DCN31 support, which includes this header so firmware-service register structures can use generated masks and shifts consistently with host driver code.

## Risks And Edge Cases

- Generated-field drift is the central risk. A wrong shift or mask compiles cleanly but updates the wrong bits in a live MMIO register.
- Shift/mask pairs must stay consistent. For example, a correct `REG_UPDATE` depends on the mask covering exactly the field width at the shift position; a mismatch can corrupt adjacent fields in color, scaler, cursor, power, or perfmon registers.
- Repeated RAM-region definitions are copy-sensitive. Gamma, blend-gamma, and shaper RAM A/B region macros repeat the same offset/segment pattern across regions 0 through 33 and across CM0/CM1; a single generated typo may only appear with particular color-transfer curves or LUT bank choices.
- LUT programming uses index/data side effects. Incorrect masks for LUT index, write enable, RAM select, or read/write control can silently load the wrong bank, channel, or entry.
- Memory-power fields are sequencing-sensitive. Bad masks for DSCL/CM/shaper memory force, disable, or state fields can cause writes to be ignored, power transitions to hang, or low-power optimizations to corrupt display state.
- DPP1 and DPP0 are both represented in this chunk. The DPP0 material is mostly top-level control/CRC/perfmon, while DPP1 includes CNVC/DSCL/CM pipeline programming; instance-token mistakes may only fail on multi-pipe or secondary-plane configurations.
- Chunk boundaries are artificial. The first field set starts mid-register, and the last `CM1_CM_DEALPHA` comment has no field definitions in this work item. Adjacent chunks are required before making complete file-level claims.

## Test Signals

Useful validation is mostly generated-header consistency plus display hardware behavior:

- Build AMDGPU/DC with DCN31 support enabled; missing or renamed shift/mask macros should fail in resource, IRQ, DMUB, DPP, or HWSS register-table construction.
- Mechanically verify that every full register field in the chunk has both a `__SHIFT` and `_MASK` macro, allowing for the known boundary exceptions at lines 14928 and 17438.
- Diff this range against AMD's authoritative DCN 3.1.2 register database and the companion `dcn_3_1_2_offset.h`.
- Exercise DPP color paths: degamma/gamma/blend-gamma/shaper/3D LUT loading, HDR multiplier, gamut remap, post-CSC, bias, pre-CSC, dealpha/re-alpha, and color-key behavior.
- Exercise scaler paths on DPP1: RGB and YCbCr formats, 4:2:0 luma/chroma scaling, identity scaling, non-integer scaling, tap-count changes, coefficient RAM programming, overscan, recout sizing, and line-buffer partitioning.
- Validate cursor paths on DPP1: cursor enable/disable, color modes, position, 2x magnification, pitch, size, and FP scale/bias.
- Validate diagnostics: DPP CRC capture/readback, perfmon counter enable/clear/window/event select, and debug index/data paths.
- Test suspend/resume, display hotplug, modeset, plane enable/disable, and memory low-power transitions while watching for blank screens, underflow, color corruption, cursor artifacts, CRC mismatches, perfmon counter anomalies, stuck power-state waits, and kernel register-helper warnings.

## Cross-Chunk Notes

Earlier chunks own the beginning of `CM0_CM_BLNDGAM_RAMA_REGION_18_19`, including the first LUT-offset shift at line 14927. Later chunks own the actual `CM1_CM_DEALPHA` definitions and continue the remaining CM1 color-management/shaper/3D-LUT namespace. The final per-file research document should merge adjacent chunks before making complete claims about all DCN 3.1.2 DPP instances, all CM blocks, or the complete generated mask namespace.

### subset-b-001809: lines 17439-19949

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 17439-19949

## Scope

This chunk is a generated DCN 3.1.2 register-field mask slice from `dcn_3_1_2_sh_mask.h`. It contains preprocessor constants only: `_SHIFT` values for field bit positions, `_MASK` values for 32-bit register masks, and comment markers that name registers and hardware address blocks. There are no C functions, structs, enums, branches, loops, local variables, or in-memory data structures in this range.

The range contains 2,114 generated `#define` lines, split almost evenly between field shifts and field masks. It starts in the tail of DPP1 color-management (`CM1`) fields, then covers DPP1 top/perfmon fields, and then moves through the DPP2 converter, cursor, scaler, and color-management register surface. The chunk ends partway through the `CM2_CM_SHAPER_RAMB_REGION_10_11` definition, so the following chunk must complete the remaining DPP2 CM shaper RAMB region fields.

## Purpose And Hardware Surface

The purpose of this header range is to provide the bit-layout ABI between AMDGPU Display Core code and DCN 3.1.2 display hardware. The companion `dcn_3_1_2_offset.h` header supplies register addresses; this mask header supplies the field positions and masks consumed by register helper macros to encode values, decode MMIO readbacks, and perform read/modify/write updates without hard-coding numeric bit positions in functional code.

Major hardware areas represented here:

- Tail of `CM1` color-management fields for dealpha, coefficient format, shaper control, shaper LUT programming, shaper RAM A/B regions, 3D LUT programming, CM memory power status/control, and test/debug index/data.
- `DPP_TOP1` display pipe processor top controls for DPP enablement, expansion mode, gamut remap selection, realpha/dealpha controls, DPP reset, CRC capture/readback, CRC window programming, and host-read gating.
- `DC_PERFMON12`, a DPP performance monitor block with counter selection, increment mode, run/stop state, counter report selection, clock enable, counter-value interrupt status/ack bits, and low/high counter readback fields.
- `CNVC_CFG2`, the DPP2 input conversion/configuration block, including source pixel format, format-control mode bits, floating-point bias/scale, color keying, alpha LUTs, pre-dealpha/re-alpha, pre-degamma, pre-CSC matrices, and coefficient format.
- `CNVC_CUR2`, the DPP2 cursor block, including cursor enable, mode, pitch, line-per-chunk, 2x magnify, expansion mode, color0/color1, and floating-point scale/bias controls.
- `DSCL2`, the DPP2 scaler and line-buffer block, including coefficient RAM access, scaler mode/taps, 2-tap and manual replication controls, horizontal/vertical scale ratios and initial phases, recout/MPC/OTG geometry, line-buffer format/memory controls, DSCL and OBUF memory power controls/status, and autocal/update bits.
- Beginning and main body of `CM2`, the DPP2 color-management block, including post-CSC, gamut remap, bias, gamma-correction LUTs and RAM A/B PWL regions, blend-gamma LUTs and RAM A/B PWL regions, HDR multiplier, memory power controls/status, dealpha, coefficient format, shaper LUTs, shaper RAM A, and partial shaper RAM B regions.

## Important Definitions

The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit.
- `<REGISTER>__<FIELD>_MASK` gives the field's raw bitmask within the register.
- `// addressBlock: ...` comments identify the hardware aperture for the following register group.
- `//<REGISTER>` comments group the generated shift/mask pairs for one register.

Important field families in this chunk:

- Color-management mode fields include `CM_CONTROL`, `CM_POST_CSC_CONTROL`, `CM_GAMUT_REMAP_CONTROL`, `CM_GAMCOR_CONTROL`, `CM_BLNDGAM_CONTROL`, `CM_DEALPHA`, `CM_COEF_FORMAT`, and `CM_SHAPER_CONTROL`. They select enable modes, current-mode readback fields, RAM A/B selection, PWL disable controls, and coefficient numeric formats.
- CSC and gamut remap matrices are packed into paired coefficient registers such as `CM2_CM_POST_CSC_C11_C12`, `CM2_CM_POST_CSC_C33_C34`, `CM2_CM_GAMUT_REMAP_C11_C12`, and their `B_` variants. Each carries two coefficient fields, usually with low and high 16-bit masks.
- Gamma, blend-gamma, and shaper LUT access uses indexed data windows: `*_LUT_INDEX`, `*_LUT_DATA`, `*_LUT_CONTROL`, and `*_LUT_WRITE_EN_MASK` fields. These fields are the register-level doorbell for loading piecewise-linear transfer functions into hardware RAM.
- RAM A/B PWL regions use repeated start, end, base, slope, offset, and region-pair registers. Region-pair registers such as `CM2_CM_GAMCOR_RAMA_REGION_0_1` and `CM2_CM_BLNDGAM_RAMB_REGION_32_33` pack a LUT offset and segment count for two adjacent regions, while start/end registers set channel-specific bounds for red, green, and blue.
- 3D LUT fields in the tail of `CM1` include `CM1_CM_3DLUT_MODE`, `CM1_CM_3DLUT_INDEX`, `CM1_CM_3DLUT_DATA`, `CM1_CM_3DLUT_DATA_30BIT`, `CM1_CM_3DLUT_READ_WRITE_CONTROL`, output normalization, and per-channel output offsets. These fields drive the DPP color pipeline's 3D lookup stage.
- DPP top fields include enable/configuration bits (`DPP_CLOCK_ENABLE`, `DPP_PIPE_CLOCK_ENABLE`, expansion mode), CRC controls and readback (`DPP_CRC_*`), and soft reset/status. These are used for pipe bring-up, reset sequencing, and validation.
- Perfmon fields include counter event selection, readback selection, increment mode, counter state, run-enable selection, report count, clock enable, counter-value interrupt status/ack for counters 0-7, and low/high counter-value registers.
- CNVC fields define input conversion behavior: surface pixel format, alpha enable/source/override, 10-bit and 12-bit component formatting, truncation/rounding modes, clamp controls, fixed/floating conversion bias/scale, pre-degamma, pre-CSC matrix values, and keyer channels.
- Cursor fields define whether cursor0 is enabled, how cursor memory is interpreted, pitch/line chunking, magnification, expansion, and palette/color values.
- DSCL fields define coefficient RAM bank/tap access, scaler operating mode, horizontal/vertical tap count, chroma/luma scale ratios and initial phases, autocalculation controls, overscan, recout and MPC geometry, line-buffer format/memory behavior, and DSCL/OBUF power state.
- Memory-power fields split force/disable controls from status readbacks: CM shaper/HDR 3D LUT controls in `CM*_CM_MEM_PWR_CTRL2`, CM gamma/blend controls in `CM2_CM_MEM_PWR_CTRL`, DSCL scaler and line-buffer controls in `DSCL2_DSCL_MEM_PWR_CTRL`, and status fields that report actual memory power state.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when Display Core code combines these constants with register addresses from the matching offset header and register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, or generated `SF`/`SRI` tables.

A typical usage pattern is:

1. Select the DCN 3.1.2 register address for the target DPP instance from `dcn_3_1_2_offset.h` or an instance table.
2. Use this chunk's `_SHIFT` and `_MASK` macros to pack a field value into a 32-bit register word or extract a field from an MMIO readback.
3. Perform an MMIO write, read, or read/modify/write through the AMDGPU display register abstraction.
4. Let the hardware retain, consume, update, or clear the register-backed state according to the block's semantics.

The state represented here is hardware state, not software-owned persistent state:

- Color pipeline configuration, CSC coefficients, gamut matrices, shaper/gamma/blend transfer curves, 3D LUT values, format controls, cursor format, scaler geometry, and line-buffer mode persist in display hardware registers or RAMs until reprogrammed, reset, or power-gated.
- Current-mode fields, perfmon counter state, CRC values, memory-power status, line-buffer counters, soft-reset done/status, and host-read status are volatile hardware readbacks.
- LUT index/data windows and RAM A/B region registers are programming interfaces for hardware RAMs. Their contents are durable only while the relevant block and memory remain powered and are not reset or reloaded.
- ACK, reset, update, and clear-style fields are side-effecting write paths. They should not be treated like ordinary durable configuration bits.
- Memory-power force/disable fields affect whether dependent LUT, scaler, line-buffer, or output-buffer state can be reliably accessed. Callers must sequence power and clock controls around register programming.

The masks do not encode ordering or synchronization. Correct driver code must still enforce hardware sequencing: hold appropriate update locks when changing live pipe state, program LUT RAM through the expected index/data/write-enable order, avoid reading CRC or perfmon counters before capture/report state is valid, wait for reset/power status where required, and avoid updating scaler or color pipeline registers at scan positions that would create visible corruption.

## Dependencies And Integration Points

This chunk integrates with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h`, which supplies the matching `reg...` addresses and base indices for the register names defined here.
- Display Core register helpers and generated shift/mask tables that use `FD_SHIFT`, `FD_MASK`, `SF`, `SRI`, `SRI_ARR`, `REG_GET`, `REG_SET`, and `REG_UPDATE` style macros.
- `dcn31` resource construction, which includes `dcn_3_1_2_offset.h` and `dcn_3_1_2_sh_mask.h` for DCN 3.1 register programming. Resource creation wires DPP instances, scalers, color blocks, OPPs, timing generators, AUX/I2C blocks, and IRQ services into the DC resource pool.
- DPP and MPC color code that programs degamma, regamma, shaper LUTs, 3D LUTs, gamut remap matrices, HDR multiplier, blend gamma, and post-CSC using the CM/CNVC register sets represented here.
- Plane programming paths that configure DPP input format, alpha behavior, color keying, cursor format, scaler taps, scaling ratios, recout geometry, and line-buffer format for each active plane.
- CRC and diagnostics paths that use `DPP_TOP1_DPP_CRC_CTRL`, `DPP_TOP1_DPP_CRC_VAL_R_G`, and `DPP_TOP1_DPP_CRC_VAL_B_A` to validate DPP output.
- Performance-monitoring code that configures `DC_PERFMON12` counters and samples low/high counter values or counter-value interrupt status for DPP2-related events.
- Clock, reset, and power-management paths that touch DPP top soft reset, DSCL memory power, OBUF memory power, line-buffer memory controls, and CM LUT memory power fields during pipe enable/disable, suspend/resume, and idle transitions.

The integration contract is name and numeric consistency. A missing macro name generally causes a compile-time failure in a generated table or register helper use. A wrong numeric mask or shift can compile successfully while programming the wrong hardware bits.

## Risks And Maintenance Notes

- Numeric drift from the ASIC register specification is the primary risk. A stale mask or shift can corrupt display pipe programming, color conversion, scaler state, LUT programming, CRC behavior, perfmon events, or power transitions.
- The range is heavily instance-prefixed. Confusing `CM1` with `CM2`, `CNVC_CFG2` with other CNVC instances, `DSCL2` with another scaler, or `DPP_TOP1` with a different top block can target the wrong pipe or a mismatched register address.
- The chunk straddles instance boundaries. It starts with DPP1 CM tail fields and then moves to DPP2 blocks; consumers should not assume every definition in the slice belongs to the same DPP instance.
- The end of the chunk is incomplete for `CM2_CM_SHAPER_RAMB_REGION_*`. Any per-file or per-block summary must merge with the following chunk before claiming full CM2 shaper RAMB coverage.
- LUT and PWL programming is ordering-sensitive. Writing data without the correct index, RAM selection, write-enable mask, or region bounds can create broken transfer curves, color artifacts, or inconsistent RAM A/B state.
- Current-mode/readback fields are not control fields. Treating `*_MODE_CURRENT` or memory-power status bits as writable control fields can produce ineffective writes or hide sequencing bugs.
- CSC, gamut, and bias fields are raw fixed-point representations. The header does not validate coefficient range, sign interpretation, matrix order, or channel packing.
- DSCL scaler ratio, phase, tap, and autocal fields interact with viewport size, recout size, chroma sampling, and line-buffer allocation. Incorrect programming can cause underflow, cropping, corruption, or incorrect chroma alignment.
- Memory power controls can make later LUT, scaler, line-buffer, or output-buffer register accesses unreliable if blocks are forced off or disabled while still in use.
- Perfmon and CRC fields have read/clear/capture semantics. Generic read/modify/write code must avoid accidentally acknowledging events or sampling partially updated values.

## Test Signals

Useful validation signals for this chunk are compile-time checks, generated-header consistency checks, and hardware/display exercise:

- Build AMDGPU Display Core with DCN 3.1 support and verify all referenced generated register-field names resolve against `dcn_3_1_2_sh_mask.h`.
- Run generated-header validation that every field has matching `_SHIFT` and `_MASK` definitions, masks are 32-bit bounded, bitfields do not overlap unexpectedly within each register, and register prefixes line up with the companion offset header.
- Exercise modesetting on pipes that use DPP1 and DPP2, including plane enable/disable, pipe reset, DPP clock enable, host-read control, and suspend/resume.
- Validate DPP2 plane input formats across RGB/YUV, 8/10/12-bit formats, alpha modes, pre-dealpha/re-alpha, pre-degamma, pre-CSC, color keying, and cursor enable/magnify modes.
- Program scaler paths using DSCL2 with scaling up/down, luma/chroma ratios, tap changes, coefficient RAM updates, recout/MPC geometry changes, overscan, autocal, and line-buffer format changes.
- Program color-management paths using CM2 post-CSC, gamut remap, gamma-correction RAM A/B, blend-gamma RAM A/B, shaper RAM A/B, HDR multiplier, and 3D/shaper-related memory power controls.
- Use CRC diagnostics through `DPP_TOP1_DPP_CRC_CTRL` and read `DPP_CRC_VAL_R_G`/`DPP_CRC_VAL_B_A` to confirm capture windows, enable bits, and reset/continuous behavior.
- Configure `DC_PERFMON12`, sample counter low/high values, trigger counter-value interrupts, and verify status/ack bits clear without losing counter state.
- Test memory-power sequencing for DSCL, line buffer, OBUF, CM shaper, HDR 3D LUT, gamma, and blend-gamma memory around blank/unblank, idle optimization, runtime PM, and full suspend/resume.

## Chunk-Specific Summary

Lines 17439-19949 define a dense generated register-field surface for DCN 3.1.2 DPP color, conversion, scaler, cursor, CRC, perfmon, and memory-power blocks. The most important responsibilities in this slice are DPP2 plane input conversion, DSCL2 scaler programming, DPP1/DPP2 color-management LUT and matrix programming, hardware RAM region layout for shaper/gamma/blend transfer curves, and status/control fields for diagnostics and power management. Correctness depends on exact mask/shift values, instance-correct register use, proper LUT and power sequencing, and successful hardware behavior under modeset, color-management, scaling, cursor, CRC, perfmon, and suspend/resume workloads.

### subset-b-001810: lines 19950-22457

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 19950-22457

## Scope And Purpose

This chunk is a generated AMD DCN 3.1.2 register shift/mask header slice. It contains only preprocessor constants for memory-mapped display-controller register fields: `__SHIFT` macros give bit positions, `_MASK` macros give raw 32-bit field masks, and comments delimit register groups and hardware `addressBlock` sections. There are no functions, structs, enums, loops, branches, allocations, locks, or in-memory state in this range.

The purpose of the range is to define the field layout ABI used by AMDGPU Display Core code when programming DCN 3.1.2 DPP-related hardware. The matching `dcn_3_1_2_offset.h` header provides register addresses; this header provides the bit fields used by register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and related macros after resource construction binds the generated addresses, shifts, and masks into DPP objects.

The slice has partial logical boundaries. It starts in the middle of DPP2 color-management shaper RAM B region definitions, at `CM2_CM_SHAPER_RAMB_REGION_10_11`; the preceding DPP2 shaper setup and earlier RAM B regions are in the previous chunk. It ends inside DPP3 perfmon definitions, after most `DC_PERFMON14_PERFCOUNTER_STATE` masks; the remaining `DC_PERFMON14` perfmon registers continue in a later chunk.

This specific chunk contains 2,117 `#define` lines across 368 generated register groups. The main hardware surface is the tail of DPP2 CM shaper/3DLUT, all DPP2 top and perfmon13 fields, most DPP3 CNVC/DSCL/CM/DPP top fields, and the beginning of DPP3 perfmon14.

## Register Blocks Covered

The initial DPP2 color-management tail covers:

- `CM2_CM_SHAPER_RAMB_REGION_10_11` through `CM2_CM_SHAPER_RAMB_REGION_32_33`, completing later RAM B shaper piecewise-linear region descriptors with LUT offsets and segment counts.
- `CM2_CM_MEM_PWR_CTRL2` and `CM2_CM_MEM_PWR_STATUS2` for shaper and HDR 3D LUT memory force/disable/state fields.
- `CM2_CM_3DLUT_MODE`, `CM2_CM_3DLUT_INDEX`, `CM2_CM_3DLUT_DATA`, `CM2_CM_3DLUT_DATA_30BIT`, `CM2_CM_3DLUT_READ_WRITE_CONTROL`, output normalization, per-channel output offset/scale, and CM test debug index/data fields.

The `dce_dc_dpp2_dispdec_dpp_top_dispdec` block covers `DPP_TOP2` control/status and diagnostics:

- `DPP_TOP2_DPP_CONTROL` for DPP clock enable, multiple DPPCLK/DISPCLK gate-disable controls, and test clock selection.
- `DPP_TOP2_DPP_SOFT_RESET` for CNVC, DSCL, CM, and OBUF soft reset bits.
- `DPP_TOP2_DPP_CRC_VAL_R_G`, `DPP_TOP2_DPP_CRC_VAL_B_A`, and `DPP_TOP2_DPP_CRC_CTRL` for DPP CRC readback and one-shot/continuous CRC selection.
- `DPP_TOP2_HOST_READ_CONTROL` for host-read rate limiting.

The `dce_dc_dpp2_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` block covers a full `DC_PERFMON13` surface for DPP2. It defines counter event selection, counted-value type, hardware stop/count-off controls, counter states for eight counters, perfmon run/enable/clear controls, threshold/interrupt state and acknowledge fields, and low/high counter readbacks.

The DPP3 converter configuration block, `dce_dc_dpp3_dispdec_cnvc_cfg_dispdec`, covers:

- Surface pixel format and alpha-plane enable.
- `FORMAT_CONTROL` fields for CNVC bypass, alpha enable, expansion, truncation, clipping, 16-bit conversion, MSB alignment, positive clamp, and RGB crossbar selection.
- Floating-point conversion bias/scale for R/G/B.
- Color keyer control and low/high thresholds for alpha, red, green, and blue.
- Two-bit alpha LUT entries.
- Pre-dealpha, pre-degamma, pre-realpha, pre-CSC mode, coefficient format, and A/B pre-CSC coefficient matrices.

The DPP3 cursor converter block, `dce_dc_dpp3_dispdec_cnvc_cur_dispdec`, covers cursor0 mode, expansion, enable, pixel-inversion, alpha modulation, ROM enable, two cursor colors, and cursor FP scale/bias.

The DPP3 scaler block, `dce_dc_dpp3_dispdec_dscl_dispdec`, covers:

- Scaler coefficient RAM tap select/data windows.
- Scaler mode and tap controls, including luma/chroma taps, chroma coefficient mode, coefficient RAM selection, 4:2:0 processing, and alpha-luma mode.
- DSCL 2-tap sharpness/hardcoded coefficient controls.
- Manual replicate, horizontal/vertical luma and chroma scale ratios, and initial filter phases.
- Black color, update/autocal, overscan, OTG blanking windows, recout start/size, MPC size, and line-buffer data/memory controls.
- DSCL LUT memory power controls/status and OBUF control/memory power controls.

The DPP3 color-management block, `dce_dc_dpp3_dispdec_cm_dispdec`, is the largest part of the chunk. It covers:

- CM bypass, post-CSC A/B mode and coefficient matrices, gamut-remap A/B mode and coefficient matrices, fixed bias fields, dealpha, coefficient format, and HDR multiplier.
- GAMCOR control, indexed LUT access, LUT write/read controls, RAM A/B start/base/slope/end/offset, and region descriptors for regions 0 through 33.
- BLNDGAM control, indexed LUT access, LUT controls, RAM A/B start/base/slope/end/offset, and region descriptors for regions 0 through 33.
- Shaper control, offset/scale fields, indexed LUT access, write enable/select, RAM A/B start/end controls, and region descriptors for regions 0 through 33.
- Memory-power controls/status for GAMCOR, BLNDGAM, shaper, and HDR 3D LUT memories.
- 3D LUT mode, size, current mode, index/data paths, 30-bit data path, read/write control, output normalization, per-channel output offset/scale, and test debug index/data.

The `dce_dc_dpp3_dispdec_dpp_top_dispdec` block mirrors the DPP2 top fields for instance 3: clock/gating controls, soft resets, CRC values/control, and host-read rate control.

The final block begins `dce_dc_dpp3_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` for `DC_PERFMON14`. This chunk includes `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, and most of `PERFCOUNTER_STATE`. Later `DC_PERFMON14` perfmon control, threshold/interrupt, and counter readback definitions are outside this assigned range.

## Important APIs, Types, And Macros

The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives a field's low bit within the 32-bit register.
- `<REGISTER>__<FIELD>_MASK` gives the field mask before shifting or after register readback masking, depending on the helper macro.
- `// addressBlock: ...` comments identify the generated hardware register aperture.
- `//<REGISTER>` comments group the fields belonging to a single register.

Important instance prefixes in this chunk are `CM2`, `DPP_TOP2`, `DC_PERFMON13`, `CNVC_CFG3`, `CNVC_CUR3`, `DSCL3`, `CM3`, `DPP_TOP3`, and `DC_PERFMON14`. The prefix is part of the generated symbol and encodes the hardware instance. A wrong prefix can compile if a similarly named field exists for another instance, but it targets the wrong register instance when bound through register-list macros.

The primary consumer path for these macros is `display/dc/resource/dcn31/dcn31_resource.c`. That file includes `dcn/dcn_3_1_2_offset.h` and `dcn/dcn_3_1_2_sh_mask.h`, builds `dpp_regs[]` with `DPP_REG_LIST_DCN30(id)`, and initializes `tf_shift`/`tf_mask` with `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)`. `dcn31_dpp_create()` then passes the selected per-instance addresses plus the shared shift/mask tables into `dpp3_construct()`.

The DPP register-list and field-list definitions live in `display/dc/dpp/dcn30/dcn30_dpp.h`. DCN31 reuses this DCN30 DPP hardware object shape. `DPP_REG_LIST_DCN30_COMMON(id)` names the CNVC, cursor, DSCL, CM, and DPP top registers for each instance. `DPP_REG_LIST_SH_MASK_DCN30_COMMON()` and `DPP_REG_LIST_SH_MASK_DCN30_UPDATED()` map canonical field names in `struct dcn3_dpp_shift` and `struct dcn3_dpp_mask` to generated instance-0 macro names; resource construction pairs those common shifts/masks with instance-specific addresses for DPP0 through DPP3.

Runtime code that consumes the resulting DPP object includes the DCN10/DCN20/DCN30 DPP scaler and color-management implementations. Examples include CNVC format programming, cursor programming, DPP clock enable/disable, DSCL tap/ratio/recout setup, line-buffer memory setup, DSCL memory-power sequencing, CSC/gamut-remap programming, GAMCOR/BLNDGAM/shaper PWL LUT programming through index/data windows, and CM memory-power controls.

## Functional Field Groups

CNVC format fields define how source pixels enter the DPP. Pixel format, alpha-plane enable, alpha expansion, format expansion/truncation, component clipping, positive clamp, 16-bit conversion, MSB alignment, and RGB crossbar fields are the low-level representation of plane format choices made by higher-level DRM/AMDGPU display code. The floating-point bias/scale registers and pre-degamma/dealpha/realpha controls further adapt incoming plane data before scaling and color processing.

Pre-CSC and post-CSC fields expose banked color-space conversion matrices. Each coefficient register packs two coefficients, and both A and B banks are present for pre-CSC and post-CSC paths. Mode and current-mode fields let driver code select or observe which matrix bank is active. Correct bank selection matters when changing color matrices on a live pipe.

DSCL fields program scaling geometry and filter behavior. The chunk includes both luma and chroma scale ratios, initial phases, tap counts, coefficient RAM access, 2-tap sharpness controls, 4:2:0 mode selection, recout geometry, MPC size, overscan, OTG blank windows, and line-buffer format/memory parameters. These fields translate plane scaling, viewport, chroma-siting, and line-buffer decisions into hardware state.

The CM GAMCOR, BLNDGAM, and shaper LUT blocks are piecewise-linear LUT engines. They use a repeated pattern: control/current-mode fields, an index register, a data register, a LUT control or write-enable register, per-channel start/end/base/slope/offset registers, and region descriptors that pack two regions per register. Region descriptors use 9-bit LUT offsets and segment-count fields for regions 0 through 33. The DPP2 portion completes the later shaper RAM B region descriptors; the DPP3 portion includes full GAMCOR, BLNDGAM, and shaper RAM A/B definitions.

The 3D LUT fields define a stateful indexed RAM interface. `CM_3DLUT_MODE` selects mode and size and exposes current mode, `CM_3DLUT_INDEX` selects the entry, `CM_3DLUT_DATA` packs two 16-bit data values, `CM_3DLUT_DATA_30BIT` exposes a 30-bit access path, and `CM_3DLUT_READ_WRITE_CONTROL` selects write enable mask, RAM bank, 30-bit enable, and read selection. Output normalization and per-channel offset/scale fields shape the 3D LUT output.

Memory-power fields gate or report internal DPP memories. `CM_MEM_PWR_CTRL`, `CM_MEM_PWR_STATUS`, `CM_MEM_PWR_CTRL2`, and `CM_MEM_PWR_STATUS2` cover GAMCOR, BLNDGAM, shaper, and HDR 3D LUT memory force/disable/state. DSCL and OBUF memory-power fields cover scaler LUT and output-buffer memories. These fields are not just diagnostics; setting force/disable bits can make dependent LUT or scaler access invalid until memory state is restored.

DPP top fields are instance-level control and diagnostic fields. Clock-enable and gate-disable fields decide whether the DPP subblock is active or gated. Soft-reset fields reset CNVC, DSCL, CM, and OBUF subblocks. CRC fields configure one-shot or continuous DPP CRC capture and read back R/G/B/A signatures. Host-read rate control throttles host-side reads from the DPP block.

Perfmon fields define hardware profiling controls. `DC_PERFMON13` is complete in this chunk and `DC_PERFMON14` starts at the end. Counter controls select events, counted-value type, increment mode, hardware stop behavior, run enable mode, interrupt enable, active state, and counter selection. State and cvalue fields expose counter status and threshold/interrupt conditions, while low/high registers expose the sampled count value.

## Control Flow And State Behavior

This header has no executable control flow. Runtime behavior appears when DCN31 resource setup binds generated offsets and masks into DPP objects, and later DPP code uses those objects to access MMIO registers. A normal path is:

1. `dcn31_resource.c` includes `dcn_3_1_2_offset.h` and this shift/mask header.
2. `dpp_regs[inst]` selects the instance-specific register addresses, for example DPP2 or DPP3.
3. `tf_shift` and `tf_mask` provide canonical field positions and masks through the DCN30 DPP field-list macros.
4. DPP code calls register helpers to set or read fields; the helper combines the chosen address with the relevant shift/mask.
5. Hardware persists, latches, consumes, or updates the register-backed state according to the block's semantics.

Most fields in this range represent hardware state rather than software state. Format, scaler, CSC, gamut, gamma, shaper, 3D LUT, CRC, and memory-power controls persist in hardware registers until reprogrammed, reset, power-gated, or overwritten by firmware/hardware mechanisms. Status fields such as current mode, memory-power state, CRC values, perfmon active state, and counter state are volatile hardware readbacks.

Several register groups are explicitly stateful. LUT and 3D LUT programming uses index/data windows, write masks, RAM bank selectors, and current-mode readbacks. A valid mask with a stale index or wrong bank can write correct-looking data to the wrong LUT bank. CRC and perfmon fields are interval-sensitive; clear/ack, enable, one-shot/continuous, event selection, threshold, and readout ordering determine what a readback means.

Soft reset, ACK/clear, and memory-power fields have side effects. They should not be treated as ordinary durable configuration bits. Writing a soft-reset field can reset subblock state, writing clear/ack fields can drop latched diagnostic events, and forcing memory power down can make subsequent LUT or coefficient writes unreliable.

## Dependencies And Integration Points

This chunk must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h`. Offset macros and shift/mask macros are generated as a pair; address drift or field-layout drift can compile but program wrong bits.

The main include sites in this tree are:

- `display/dc/resource/dcn31/dcn31_resource.c`, which constructs DPP0 through DPP3 objects and binds the DCN 3.1.2 generated masks and shifts.
- `display/dc/irq/dcn31/irq_service_dcn31.c`, which includes the same generated header set for DCN31 interrupt-service register definitions.
- `display/dmub/src/dmub_dcn31.c`, which includes the generated header set for DMUB/DCN31 register access.

The DPP-specific consumer definitions are in `display/dc/dpp/dcn30/dcn30_dpp.h` and the inherited DPP implementations under `display/dc/dpp/dcn10`, `display/dc/dpp/dcn20`, and `display/dc/dpp/dcn30`. The fields in this chunk support:

- Plane format and converter programming through CNVC/CNVC_CUR fields.
- Scaling and line-buffer setup through DSCL fields.
- Color-management programming through CM CSC, gamut, GAMCOR, BLNDGAM, shaper, and 3D LUT fields.
- Power-management sequencing for CM, DSCL, and OBUF memories.
- DPP clocking, soft reset, CRC diagnostics, and host-read throttling.
- Perfmon diagnostics for DPP2 and DPP3.

Higher-level display integration comes from DRM plane state, atomic modeset/resource validation, color-management properties, scaling ratio calculations, cursor state, power management, CRC/debugfs workflows, and hardware performance diagnostics. This generated header is the low-level endpoint those paths use to encode the requested hardware state.

## Risks And Maintenance Notes

Generated numeric drift is the primary risk. A wrong shift or mask can corrupt adjacent fields in MMIO registers, which may show up as bad color output, failed scaling, cursor artifacts, incorrect CRCs, broken 3D LUT programming, unreliable perfmon data, or power-management failures rather than an immediate crash.

Instance-prefix mistakes are high risk because this chunk contains repeated DPP2 and DPP3 surfaces. Using `CM2` versus `CM3`, `DPP_TOP2` versus `DPP_TOP3`, or `DC_PERFMON13` versus `DC_PERFMON14` incorrectly can target a different pipe's hardware. Shared DPP code relies on resource construction to pair common field tables with the correct instance addresses.

The range is split across logical blocks. The DPP2 shaper RAM B definitions are only the tail, and `DC_PERFMON14` is incomplete. Merge/reconciliation should combine neighboring chunk documents before presenting a complete per-file register map for DPP2 shaper or DPP3 perfmon.

LUT programming is ordering-sensitive. GAMCOR, BLNDGAM, shaper, and 3D LUT paths use bank selectors, current-mode readbacks, index/data windows, color write masks, and region descriptors. Updating a visible bank before all data and regions are programmed can cause transient or persistent color corruption.

Scaler and CNVC format fields are tightly coupled to plane state. Wrong tap counts, chroma modes, scale ratios, initial phases, line-buffer memory configuration, or format crossbar settings can produce artifacts only on specific pixel formats, scaling ratios, rotation/chroma cases, or cursor/alpha combinations.

Memory-power controls can invalidate dependent programming. Forcing shaper, HDR 3D LUT, GAMCOR, BLNDGAM, DSCL LUT, or OBUF memories into low-power states while the block is active can cause lost LUT contents, failed register waits, or display corruption around blanking, suspend/resume, hotplug, or plane reconfiguration.

CRC and perfmon fields are diagnostics with stateful clear/enable/read ordering. Generic read/modify/write code must preserve unrelated bits and avoid accidentally acknowledging or masking events. Tests that do not reset counters, clear pending one-shot state, or select the intended source can report misleading data even if the masks are correct.

Soft-reset and clock-gating fields affect whole DPP subblocks. Resetting CNVC, DSCL, CM, or OBUF while an active pipe depends on them can drop programmed state. Disabling clocks or forcing gate behavior can make subsequent register access unreliable unless sequencing matches hardware requirements.

## Test Signals

Build-time validation should catch missing or renamed generated macros in `dcn31_resource.c` and `dcn30_dpp.h`, especially through `DPP_REG_LIST_DCN30(id)`, `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)`, and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)`.

Generated-header consistency checks should verify that every field has the expected `_SHIFT` and `_MASK`, masks fit in 32 bits, fields do not overlap unexpectedly within a register, and repeated DPP2/DPP3 register groups match the ASIC specification.

Modeset and plane tests should exercise DPP2 and DPP3 with varied pixel formats, alpha-plane state, format expansion/truncation, color keying, cursor formats, pre-dealpha/realpha, and pre-degamma paths. Useful symptoms are correct color channels, alpha behavior, cursor appearance, and no unexpected converter bypass.

Scaler tests should cover upscaling, downscaling, bypass, 4:2:0 luma/chroma handling, chroma coefficient mode, tap-count changes, coefficient RAM programming, overscan, recout size/start, MPC size, and line-buffer memory configuration.

Color-management tests should program post-CSC, gamut remap, GAMCOR, BLNDGAM, shaper, HDR multiplier, and 3D LUT paths on DPP3 and the DPP2 shaper/3D LUT tail where applicable. High-signal checks include color-ramp output, LUT bank switching, current-mode readback, region descriptor correctness, and no visible transient during atomic updates.

Power-management tests should exercise suspend/resume, runtime power transitions, display blank/unblank, stream reconfiguration, and plane disable/enable around CM, DSCL, shaper, HDR 3D LUT, GAMCOR, BLNDGAM, and OBUF memory-power fields. Expected signals are successful register waits, restored LUT contents where required, and no corruption after resume.

DPP CRC tests should enable one-shot and continuous CRC on DPP2 and DPP3, vary CRC source/pixel/cursor/420/stereo/interlace selection where supported, read R/G/B/A values, and verify pending bits and masks behave as expected.

Perfmon tests should configure `DC_PERFMON13` for DPP2 and the available `DC_PERFMON14` counter-control/state fields for DPP3, select known events, start/stop counters, read low/high values, trigger threshold interrupts where available, and verify clear/ack behavior without losing unrelated counter state.

## Chunk-Specific Summary

Lines 19950-22457 are generated DCN 3.1.2 register metadata for DPP color, scaler, converter, top-level control, CRC, memory-power, 3D LUT, and perfmon programming. The chunk completes the DPP2 shaper/3D LUT tail, fully covers DPP2 top and perfmon13, covers most DPP3 CNVC/CNVC_CUR/DSCL/CM/DPP_TOP fields, and starts DPP3 perfmon14. Correctness depends on exact generated mask/shift values, correct instance binding through DCN31 resource construction, careful LUT/index/bank sequencing, and hardware validation across modeset, scaling, color management, CRC, perfmon, reset, and power-management workflows.

### subset-b-001811: lines 22458-24978

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 22458-24978

## Scope

This chunk is a generated DCN 3.1.2 register-field shift/mask slice from `dcn_3_1_2_sh_mask.h`. It contains preprocessor constants only: `_SHIFT` values for field low-bit positions, `_MASK` values for raw 32-bit register masks, and generated comments that group fields by register and address block. There are no C functions, structs, enums, branches, loops, local variables, allocation paths, or in-memory data structures in this range.

The chunk starts in the tail of `DC_PERFMON14_PERFCOUNTER_STATE`, completes the remaining `DC_PERFMON14` perfmon control/readback registers, covers `MPCC0` through `MPCC3`, covers shared MPC configuration/status/CRC/vupdate-lock registers, covers `DC_PERFMON15`, then defines the MPCC output-gamma and gamut-remap register fields for complete `MPCC_OGAM0`, `MPCC_OGAM1`, `MPCC_OGAM2`, and the beginning of `MPCC_OGAM3`.

## Purpose And Hardware Surface

The purpose of this range is to provide the bit-layout ABI between AMDGPU Display Core code and DCN 3.1.2 MPC/MPCC hardware. Companion generated offset headers provide register addresses; this header provides the field masks and shifts used by register helper macros to encode values, decode readbacks, and update MMIO registers without hard-coded bit arithmetic in functional driver code.

Major hardware areas represented here:

- `DC_PERFMON14` tail fields for MPC/MPCC perfmon state, report/count-off controls, clock/run start/stop selection, counter-value interrupt status/ack for counters 0-7, high/low counter readback, and read selection.
- `MPCC0` through `MPCC3` compositor slice controls: top/bottom input selection, OPP target selection, blend/alpha/gain mode, stereo/multi-plane control, update-lock source/status, top/bottom gain, background color components, output-gamma memory power control, and idle/busy/disabled status.
- Shared `MPC` configuration registers for clock control, soft reset of MPCC and MPC subblocks, CRC control/selection/results, perfmon event enable, bypass background color, host read rate, DPP/OPP/MPCC/DWB pending status, per-pipe vupdate lock sets, and DWB0 mux selection/status.
- `DC_PERFMON15` full perfmon block with counter event selection, counted value type, hardware stop/count-off selectors, per-counter states, perfmon state, interrupt controls, clock enable, and low/high readback.
- `MPCC_OGAM0`, `MPCC_OGAM1`, and `MPCC_OGAM2` complete output-gamma blocks: OGAM mode/select/current-state controls, LUT index/data/control, RAM A and RAM B piecewise-linear region definitions for RGB channels, offsets, region LUT offsets/segment counts, gamut-remap coefficient format/mode, and 3x4-style gamut-remap coefficient pairs for A and B coefficient banks.
- `MPCC_OGAM3` beginning: OGAM control, LUT access, RAM A start/end/offset fields, and RAM A region pairs through the chunk boundary at `MPCC_OGAM3_MPCC_OGAM_RAMA_REGION_16_17`.

## Important Definitions

The exported interface is the generated macro naming pattern:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit position where the field starts.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask within the 32-bit register.
- `// addressBlock: ...` comments identify the register aperture for following definitions.
- `//<REGISTER>` comments group the field definitions for each register.

Important field families in this chunk:

- Perfmon fields use `PERFCOUNTER_EVENT_SEL`, `PERFCOUNTER_CVALUE_SEL`, `PERFCOUNTER_INC_MODE`, `PERFCOUNTER_HW_CNTL_SEL`, `PERFCOUNTER_RUNEN_MODE`, `PERFCOUNTER_CNTOFF_*`, `PERFCOUNTER_RESTART_EN`, `PERFCOUNTER_INT_EN`, `PERFCOUNTER_ACTIVE`, and selector fields to configure event counting and readback multiplexing.
- Perfmon status/readback fields include per-counter 2-bit state fields, counter-state select bits, `PERFMON_STATE`, `PERFMON_RPT_COUNT`, counter-value interrupt status/ack bits for counters 0-7, high 16-bit readback, low 32-bit readback, and read selection.
- MPCC compositor fields use 4-bit selectors for top/bottom input and OPP ID, mode fields for blend and alpha behavior, 8-bit global alpha/gain fields, 19-bit gain fields, 12-bit background color components, and status bits for idle/busy/disabled.
- MPCC stereo/multi-plane fields include stereo/multi-plane enable, mode, frame/field alternation, forced next-frame/top polarity, and current frame polarity readback.
- MPCC update-lock fields select which lock source controls each compositor slice and expose locked-status bits. These interact with atomic display updates and vupdate locking.
- MPCC memory-power fields cover output-gamma memory power force, disable, low-power mode, and current power state for each MPCC instance.
- MPC soft-reset fields independently reset `MPCC0-3`, scalar/filter-like `MPC_SFR0-3` and `MPC_SFT0-3` subblocks, plus a global MPC soft reset.
- MPC CRC fields select enable/continuous/one-shot behavior, stereo/interlace mode, CRC source, update lock, DPP/OPP/DWB source selectors, mask bits, and result readbacks for AR, GB, and C channels.
- MPC pending-status fields expose surface/config/cursor update pending bits for DPP0-3, config update pending bits for OPP0-3 and MPCC0-3, and DWB0 pending state.
- Vupdate-lock set registers provide single-bit lock controls for address/config/cursor combinations, address/config-only combinations, address-only, config-only, and cursor-only domains for pipe sets 0-3.
- OGAM LUT fields provide a 9-bit LUT index, 18-bit LUT data, write color mask, read color selection, read debug, host selection, and configuration mode.
- OGAM piecewise-linear fields are replicated for RAM A and RAM B, RGB channels, and region pairs. Start/end/base/slope values are mostly 16-bit or 18-bit payloads, offsets are 19-bit, region LUT offsets are 9-bit, and region segment counts are 3-bit fields packed two regions per register.
- Gamut-remap fields provide coefficient format/mode/current mode and paired 16-bit coefficient fields for rows/columns `C11` through `C34` in A and B banks.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when AMDGPU Display Core code combines these constants with matching register addresses and helper macros such as generated `REG_GET`, `REG_SET`, `REG_UPDATE`, or table-driven register accessors.

A typical runtime use is:

1. Select a DCN 3.1.2 register address from a companion offset/register header.
2. Use this chunk's `_SHIFT` and `_MASK` macros to pack a field value, unpack a readback, or generate a read/modify/write mask.
3. Perform MMIO access through the display register abstraction.
4. Let hardware retain, consume, report, or clear the associated state.

The persistent state represented here is hardware state, not software-owned data:

- MPCC selection, blending, background color, gain, OPP routing, output-gamma mode, LUT contents, PWL RAM region programming, and gamut-remap coefficients persist in display hardware until reprogrammed, reset, or power-gated.
- MPC clock, soft reset, memory-power, mux, vupdate-lock, and CRC controls are configuration state that affects live display pipeline behavior.
- Perfmon state, counter values, pending-status bits, lock-status bits, MPCC idle/busy/disabled bits, OGAM current-mode/current-select fields, CRC results, and memory-power states are volatile hardware readbacks.
- Interrupt status/ack fields in perfmon blocks are latched hardware event state. ACK fields are side-effecting write paths, not ordinary persistent configuration.
- LUT index/data/control registers are an indexed hardware access window. Correct behavior depends on setting index, color mask/read select, host/config mode, and data in the expected sequence.

Correct sequencing is imposed by hardware and the functional driver code, not by these macros. Driver paths must still hold appropriate update locks, avoid changing active compositor/gamma state at unsafe times, respect clock/reset/power ordering, program LUT/region data before enabling a mode that consumes it, and acknowledge perfmon interrupts without losing pending events.

## Dependencies And Integration Points

This chunk integrates with:

- The matching DCN 3.1.2 register offset/address headers for the same `dcn_3_1_2` ASIC register namespace.
- AMDGPU Display Core register tables and access helpers that map register names to instance-specific offsets and pair them with these shift/mask names.
- MPC/MPCC resource code that builds compositor trees, maps DPP inputs to MPCC top/bottom slots, routes MPCC output to OPP instances, controls blend/alpha/gain behavior, and checks MPCC busy/idle state.
- Atomic modeset and plane update paths that use MPCC update locks, MPC pending-status readbacks, and vupdate-lock set registers to coordinate surface/config/cursor updates.
- Color-management paths that program MPCC output gamma LUTs, PWL RAM A/B region descriptors, per-channel offsets, and gamut-remap matrices.
- CRC/debug code that enables MPC CRC capture, selects DPP/OPP/DWB sources, reads AR/GB/C result registers, and masks/locks CRC updates.
- Perfmon/debug tooling that configures `DC_PERFMON14` and `DC_PERFMON15`, selects events, controls start/stop/count-off behavior, reads low/high counter values, and services counter interrupts.
- Clock/reset/power-management paths that toggle MPC clock gating, soft reset, and MPCC OGAM memory power state.
- Display writeback paths using `MPC_DWB0_MUX` and pending status for DWB0 integration.

Because this is a generated preprocessor interface, name consistency is as important as numeric correctness. Missing or renamed macros fail at compile time where referenced; stale shifts or masks can compile cleanly and cause MMIO writes to the wrong bits.

## Risks And Maintenance Notes

- The main correctness risk is drift from the ASIC register specification. A wrong shift or mask can misprogram compositor routing, blending, color transforms, CRC, perfmon, reset, or power state.
- The range is heavily repetitive across MPCC0-3 and MPCC_OGAM0-3. Prefix mistakes can target the wrong compositor slice or gamma block while leaving code structurally valid.
- The chunk starts mid-`DC_PERFMON14_PERFCOUNTER_STATE` and ends mid-`MPCC_OGAM3` RAM A region definitions. Adjacent chunks are needed for complete per-register/per-block coverage.
- ACK and clear-like perfmon bits are side-effecting. Generic read/modify/write code must avoid accidentally acknowledging pending counter interrupts.
- MPCC update locks and MPC vupdate locks are sequencing-sensitive. Misuse can create partially applied plane, cursor, or configuration updates and visible display glitches.
- OGAM LUT and region programming is indexed and banked. Incorrect index progression, RAM A/B selection, color channel selection, or current-vs-target mode handling can produce wrong gamma curves.
- Gamut-remap coefficient fields are packed as 16-bit halves. A shift/mask error or signed/unsigned interpretation mismatch can distort color conversion without causing a build failure.
- Memory-power and soft-reset fields can make subsequent register accesses unreliable if toggled while dependent blocks are active.
- Pending-status fields are diagnostic/readback signals, not locks by themselves. Driver code must still enforce the update ordering around them.
- Full-width and wide payload fields, such as perfmon low values, PWL values, offsets, and CRC masks/results, provide no C type-level range checking. Callers must validate field width and hardware-defined fixed-point formats.

## Test Signals

Useful validation signals for this chunk are mostly compile-time generated-header checks plus hardware/display behavior tests:

- Build AMDGPU with DCN 3.1.2 support and ensure all referenced generated macro names resolve.
- Run generated-header consistency checks that each field has matching `_SHIFT` and `_MASK` definitions, masks fit in 32 bits, and field masks do not overlap unexpectedly within a register.
- Exercise plane composition across MPCC0-3, including top/bottom input routing, OPP routing, blend modes, global alpha/gain, background color, and MPCC idle/busy/disabled readback.
- Run atomic plane, cursor, and config update tests that observe `MPC_DPP_PENDING_STATUS`, `MPC_PENDING_STATUS_MISC`, MPCC update-lock status, and vupdate-lock set behavior.
- Program output gamma on MPCC_OGAM0-2 and the covered MPCC_OGAM3 RAM A portion, verifying LUT index/data access, RAM A/B region programming, offsets, segment counts, and current mode/select readbacks.
- Exercise gamut-remap enable/disable and coefficient-bank programming for MPCC_OGAM0-2, checking color accuracy or CRC output before and after matrix updates.
- Use display CRC diagnostics to configure MPC CRC source selection, update locking, one-shot/continuous modes, and read AR/GB/C result registers.
- Configure `DC_PERFMON14` and `DC_PERFMON15`, select events, start and stop counters, read high/low values, trigger counter interrupts, and verify status/ack bits clear without corrupting counter state.
- Test clock/reset/power transitions around suspend/resume, modeset, blank/unblank, and runtime power management, with attention to MPC soft reset and MPCC OGAM memory power fields.
- Validate DWB0 mux selection/status and DWB pending-state behavior when display writeback is enabled.

## Chunk-Specific Summary

Lines 22458-24978 define a dense generated DCN 3.1.2 MPC/MPCC register-field surface rather than executable code. The most important responsibilities in this slice are compositor routing/blending for MPCC0-3, MPC reset/CRC/pending/vupdate-lock controls, two perfmon register blocks, output-gamma LUT/PWL programming, and gamut-remap coefficient programming. Correctness depends on exact generated mask/shift values, instance-correct prefixes, and successful hardware behavior under modeset, atomic update, color-management, CRC, perfmon, reset, power-management, and display-writeback workloads.

### subset-b-001812: lines 24979-27504

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 24979-27504

## Purpose

This chunk is generated AMD DCN 3.1.2 register field metadata. It contains no executable C logic; it publishes `#define` constants for bit shifts and masks used to pack and unpack fields inside DCN display-controller MMIO registers.

The range covers the tail of the `MPCC_OGAM3` output-gamma/gamut-remap field map, the `MPC_OUT*` output color-space-conversion and denorm fields, the `MPC_RMU*` shaper and 3D LUT field map, full ABM0 and ABM1 backlight/ambient-backlight-management field maps, and the beginning of ABM2. The requested slice contains 2,106 `#define` lines. A prefix count over the first token shows 310 `MPCC*` definitions, 1,116 `MPC*` definitions, 252 `ABM0*` definitions, 252 `ABM1*` definitions, and 176 `ABM2*` definitions.

Although the source tree path is under a local `ceph-client` mirror, this file is AMDGPU display driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation sites, or locks in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: the field bitmask in the raw 32-bit MMIO register value.

Major field groups visible in this slice:

- `MPCC_OGAM3_MPCC_OGAM_RAMA_REGION_16_17` through `MPCC_OGAM3_MPCC_OGAM_RAMA_REGION_32_33`: output-gamma RAM A region descriptors. Each pair of regions has `LUT_OFFSET` and `NUM_SEGMENTS` fields packed at shifts `0x0`, `0xc`, `0x10`, and `0x1c`, with `0x000001FF`, `0x00007000`, `0x01FF0000`, and `0x70000000` masks.
- `MPCC_OGAM3_MPCC_OGAM_RAMB_*`: output-gamma RAM B start, start-slope, start-base, end, offset, and region descriptors for B/G/R channels. Start and base values are 18-bit style fields, offsets use 19-bit masks, and region pairs follow the same two-regions-per-register packing as RAM A.
- `MPCC_OGAM3_MPCC_GAMUT_REMAP_*` and `MPCC_OGAM3_MPC_GAMUT_REMAP_*`: gamut-remap format, mode/current-mode, and 3x4 coefficient fields for coefficient banks A and B.
- `MPC_OUT0_MUX` through `MPC_OUT3_MUX`: output mux flow/rate-control fields for four MPC outputs, including current mux status.
- `MPC_OUT0_DENORM_*` through `MPC_OUT3_DENORM_*`: output denormalization mode and clamp min/max fields for R/Cr, G/Y, and B/Cb channels.
- `MPC_OUT_CSC_COEF_FORMAT` plus `MPC_OUT0_CSC_*` through `MPC_OUT3_CSC_*`: output color-space-conversion mode/current-mode and 3x4 matrix coefficient fields for four output pipes and two coefficient banks.
- `MPC_RMU_CONTROL` and `MPC_RMU_MEM_PWR_CTRL`: RMU mux selection/current status plus memory power force/disable/low-power/state fields for RMU0 and RMU1 shaper and 3D LUT memories.
- `MPC_RMU0_SHAPER_*` and `MPC_RMU1_SHAPER_*`: shaper LUT mode/current mode, offsets, scales, LUT index/data/write mask/config status, and RAM A/RAM B piecewise-region metadata.
- `MPC_RMU0_3DLUT_*` and `MPC_RMU1_3DLUT_*`: 3D LUT mode/size/current mode, LUT index/data, 30-bit data path, read/write control, RAM select, config status, output normalization factor, and output offsets.
- `ABM0_*` and `ABM1_*`: backlight PWM levels, minimum/final duty cycle, ABM control, sample-rate and grouped-update lock fields, ABM enable/bypass, input CSC coefficient selection, ACE slope/offset/threshold fields, missed-frame and clear bits, high-gain/luma-stat read progress, histogram control, luma statistics, sample rates, histogram shift flags/indexes, histogram result registers, and master lock.
- `ABM2_*`: the same ABM field family starts for ABM instance 2, from PWM level/control fields through `ABM2_DC_ABM1_HG_SAMPLE_RATE` shifts. The chunk ends before that register's mask definitions.

## Control Flow

This header chunk has no runtime control flow. It is compile-time metadata that gets folded into driver register tables and helper calls:

1. DCN 3.1 resource, IRQ, and DMUB code include `dcn_3_1_2_sh_mask.h` with the matching `dcn_3_1_2_offset.h`.
2. Register-list macros in display blocks use token-pasting helpers such as `SF(reg, field, mask_sh)` or `FN(reg, field)` to reference names like `MPC_OUT0_CSC_MODE__MPC_OCSC_MODE__SHIFT` and `MPC_OUT0_CSC_MODE__MPC_OCSC_MODE_MASK`.
3. Initialization code stores these constants in generated `shift` and `mask` tables, usually as `uint8_t` shifts and `uint32_t` masks.
4. Runtime code uses register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and DMUB equivalents to manipulate the hardware fields.

The macros do not encode sequencing. The actual ordering is in the consumers: modeset, pipe construction, color management, output CSC/denorm programming, RMU shaper and 3D LUT programming, ABM/backlight programming, double-buffer updates, lock/unlock sequences, and power-gating transitions.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on disk. It describes MMIO-backed hardware state:

- MPCC output gamma and gamut remap state: piecewise-linear LUT region starts, slopes, bases, offsets, segment counts, coefficient format, mode/current-mode, and remap matrix coefficients.
- MPC output state: mux routing, flow/rate control, denormalization clamp mode and limits, output CSC mode/current-mode, and output CSC coefficient banks.
- RMU color state: shaper LUTs, shaper region tables, 3D LUT index/data/control, output normalization/offsets, mux routing, and memory power state.
- ABM state: PWM duty and level registers, ambient/user/current/target levels, automatic update controls, frame-sampled update rates, grouped register locks, ACE thresholds/slopes/offsets, read-progress/missed-frame status, luma statistics, histogram configuration/results, and master locks.

Persistence is hardware-defined. Configuration fields usually remain until rewritten, pipe-disabled, power-gated, suspended, or reset. Current-mode/status, update-pending, missed-frame, read-progress, histogram result, luma statistic, and clear fields may be read-only, sticky, double-buffered, self-clearing, write-one-to-clear, or frame-latched depending on the block. This generated mask header does not distinguish those behaviors; the consuming driver code and hardware programming guide provide the operational semantics.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.2 generated register offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h`

Direct include sites for `dcn_3_1_2_sh_mask.h` in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`

Important local integration patterns:

- `dcn31_resource.c` includes `yellow_carp_offset.h`, `dcn_3_1_2_offset.h`, and `dcn_3_1_2_sh_mask.h`, then uses macros such as `SR`, `SRI`, and field-list expansions to build DCN 3.1 hardware register tables.
- `dmub_dcn31.c` includes the same DCN 3.1.2 offset and mask headers and builds `dmub_srv_dcn31_regs` by expanding `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)`.
- `dmub_reg.h` defines `FN(reg_name, field)` as a lookup of `(REGS)->shift.reg_name__field` and `(REGS)->mask.reg_name__field`, then passes those pairs to `dmub_reg_set`, `dmub_reg_update`, and `dmub_reg_get`.
- MPC field-list macros in `display/dc/mpc/dcn30/dcn30_mpc.h` reference many fields in this chunk, including `MPC_OUT0_CSC_MODE`, `MPC_RMU0_3DLUT_*`, `MPC_RMU0_SHAPER_*`, `MPC_RMU_MEM_PWR_CTRL`, and `MPCC_OGAM0_*` equivalents. The `MPCC_OGAM3` instance fields in this chunk are part of the same generated per-instance namespace used when register tables are expanded across MPCC instances.
- OPP/ABM code paths use ABM-style field definitions through OPP and panel/backlight control support, especially for PWM duty-cycle programming, ABM enable/bypass, luma/histogram status, and double-buffered lock/update behavior.

## Risks And Edge Cases

- Shift/mask drift is the central risk. These constants are untyped preprocessor values, so a wrong mask or shift can compile cleanly while corrupting a different field in the same MMIO register.
- Copy-pattern errors are plausible. This chunk contains repeated instance families (`MPC_OUT0` to `MPC_OUT3`, `MPC_RMU0` and `MPC_RMU1`, `ABM0` to `ABM2`) and repeated region pairs (`0_1` through `32_33`). A one-instance typo may only affect a specific pipe, output, color block, or panel backlight path.
- The requested bounds are artificial. The first line starts inside `MPCC_OGAM3_MPCC_OGAM_RAMA_REGION_16_17`; earlier lines in the prior chunk define the comment marker and the RAMA regions before 16. The last line stops after `ABM2_DC_ABM1_HG_SAMPLE_RATE` shift definitions and before the corresponding masks.
- Some fields are double-buffered or frame-latched. Lock, update-pending, update-at-frame-start, readback DB, current-mode, missed-frame, and clear fields can cause subtle frame timing bugs if field metadata is correct but consumer sequencing is wrong.
- Color-management registers can fail visually rather than loudly. Incorrect OGAM/RMU/CSC/denorm fields can produce wrong color, clipped highlights, bad HDR/SDR transforms, or pipe-specific artifacts without obvious build-time failures.
- 3D LUT and shaper fields interact with RMU memory power state. Programming LUT data while memory is gated, in the wrong RAM selection, or with the wrong 30-bit/control bits can silently drop updates or produce stale color output.
- ABM/backlight fields are user-visible and panel-sensitive. Wrong duty-cycle, minimum-duty, auto-update, sample-rate, master-lock, or luma-stat fields can cause brightness jumps, flicker, stuck backlight levels, or failed ambient-backlight management.
- Status and clear bits can be side-effect sensitive. Misusing `*_MISSED_FRAME_CLEAR`, read-progress, update-pending, or lock bits can mask a real missed update or create polling loops that never complete.

## Test Signals

Useful validation signals combine generated-header consistency with hardware behavior:

- Build AMDGPU/DC with DCN 3.1 support enabled. Missing or renamed macros should fail in DCN31 resource, IRQ, DMUB, MPC, OPP, and ABM register-table construction.
- Mechanically verify that each complete register field in this chunk has both `__SHIFT` and `_MASK` definitions, while explicitly allowing the chunk-boundary exceptions at the first and last register groups.
- Compare this generated range against AMD's authoritative DCN 3.1.2 register database and adjacent DCN 3.x generated headers where compatible fields are expected to align.
- Exercise color-management paths: output CSC enable/bypass, matrix programming for outputs 0 through 3, denorm clamp modes, gamut remap coefficient programming, OGAM LUT updates, RMU shaper LUT programming, RMU 3D LUT programming, and memory power transitions.
- Test multiple-pipe and multi-monitor scenarios so `MPC_OUT*`, `MPCC_OGAM3`, and RMU instance fields are not only validated through output 0.
- Validate ABM and backlight behavior on supported panels: user brightness, ambient-light driven changes, minimum/final duty cycle, automatic ABM updates, sample-rate counters, frame-start update locking, suspend/resume, and rapid brightness changes.
- Poll and inspect luma/histogram status paths: read-progress bits, missed-frame flags and clears, luma min/max/filter stats, pixel counts, histogram bin results, and sample-rate reset behavior.
- Watch kernel logs and display diagnostics for register wait timeouts, update-pending bits that do not clear, color corruption, unexpected brightness changes, flicker, panel blanking, suspend/resume regressions, and DMUB register-access failures.

## Cross-Chunk Notes

Previous chunks are needed for the start of the `MPCC_OGAM3` OGAM block, including earlier RAM A regions and the beginning of `MPCC_OGAM3_MPCC_OGAM_RAMA_REGION_16_17`. Later chunks are needed for the rest of `ABM2_DC_ABM1_HG_SAMPLE_RATE` and the remaining ABM2 field map. The final per-file research document should merge this chunk with adjacent chunks before making complete claims about all DCN 3.1.2 field definitions, all MPCC OGAM instances, or the full ABM2 register namespace.

### subset-b-001813: lines 27505-30069

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 27505-30069

## Purpose

This chunk is generated AMD Display Core Next 3.1.2 register field metadata. It contains C preprocessor constants for memory-mapped display hardware register fields: `REGISTER__FIELD__SHIFT` gives the bit offset and `REGISTER__FIELD_MASK` gives the packed 32-bit mask. It has no executable C control flow, no structs, no functions, no storage, and no direct side effects.

The selected range starts at the tail of the `ABM2` adaptive-backlight block, covers a complete `ABM3` block, then spans OPP display-output blocks for instances 0 through 3, DSCRM forwarding controls, OPP top/perfmon fields, ODM input controls for instances 0 through 3, and the first large part of OTG0 timing-generator fields. It stops on the marker for `OTG0_OTG_TRIG_MANUAL_CONTROL`; that register's field definitions continue in the next chunk. Adjacent chunks are therefore required for the complete file-level report.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display-controller hardware metadata, not distributed-filesystem code.

## Important APIs, Types, And Macro Families

The public API is the generated macro namespace. Consumers normally do not hand-code every symbol; they use token-pasting helpers such as `SF`, `SRI`, `OPP_SF`, and `ABM_SF` inside register-list and mask-list macros. The matching `dcn_3_1_2_offset.h` supplies MMIO addresses, while this file supplies the field layouts used by `REG_SET`, `REG_UPDATE`, `REG_GET`, and raw register-read paths.

Major macro families in this chunk:

- `ABM2_*` tail: line 27505 finishes `ABM2_DC_ABM1_HG_SAMPLE_RATE`, then defines low-side sample-rate controls, histogram bin shift/index words, histogram result registers 1 through 24, and the ABM backlight master lock.
- `ABM3_*`: PWM ambient/user/target/current/final/minimum duty-cycle registers, ABM enable and auto-update controls, sample-rate controls, group update lock, ABM enable/bypass, IPCSC coefficient selection, ACE offset/slope/threshold fields, histogram/luma statistics, min/max pixel thresholds and counts, high-gain and low-side sample rates, histogram bin shift/index registers, histogram results, and master lock.
- `DPG0` through `DPG3`: display pattern-generator control, ramp control, dimensions, RGB/YCbCr colors, offset segment, and status fields for four OPP pipes.
- `FMT0` through `FMT3`: output formatter clamp component limits, dynamic expansion, pixel encoding/subsampling, dithering/truncation, random seeds, clamp control, side-by-side stereo control, 4:2:0 memory control, and 4:2:2 controls.
- `OPPBUF0` through `OPPBUF3` and `OPP_PIPE0` through `OPP_PIPE3`: OPP buffer active width, pixel repetition, segmentation, overlap/padded pixels, 3D dummy data/VACT-space parameters, memory power control, and OPP pipe clock control.
- `OPP_PIPE_CRC0` through `OPP_PIPE_CRC3`: CRC enable/mode/source/window/mask fields and CRC result registers for each OPP pipe.
- `DSCRM0` through `DSCRM2`: DSC forward configuration fields that connect DSC forwarding through the OPP side.
- `OPP_TOP_*` and `OPP_ABM_CONTROL`: top-level OPP clock control and ABM mux/connection control.
- `DC_PERFMON16_*`: display perfmon counter controls, event selection, state, current-value threshold/interrupt handling, and low/high readback words associated with the OPP address block.
- `ODM0` through `ODM3`: OPTC input global control, data-source/segment selection, data format and DSC mode, bytes-per-pixel, width and segment width, input clock control, memory selection, and spare register fields.
- `OTG0_*`: horizontal/vertical timing totals, blanking and sync, variable-vtotal controls, trigger controls, flow/stereo/interlace controls, status counters, snapshot and interrupt controls, update locks, vertical interrupt positions, CRC controls/results/windows, static-screen detection, 3D structure, genlock/swaplock controls, clock/reset status, global sync events, master update lock, GSL windows, vupdate keepout, and global control fields.

## Control Flow And Data Flow

This header has no runtime control flow. Runtime behavior is created by AMD Display Core code that binds these constants into per-block register tables and later performs MMIO reads/writes:

1. The DCN 3.1/3.1.2 display stack includes the matching offset and shift/mask headers.
2. Resource code builds static register tables. For example, `dcn31_resource.c` creates ABM register arrays with `ABM_DCN302_REG_LIST(id)`, OPP register arrays with `OPP_REG_LIST_DCN30(id)`, and OPTC register arrays with `OPTC_COMMON_REG_LIST_DCN3_1(id)`.
3. Mask/shift tables are initialized from field-list macros such as `ABM_MASK_SH_LIST_DCN30`, `OPP_MASK_SH_LIST_DCN20`, and `OPTC_COMMON_MASK_SH_LIST_DCN3_1`, which paste field names into the generated symbols in this file.
4. Hardware block constructors receive the tables. Examples include `dmub_abm_create()` for ABM/backlight and OPTC/OPP constructors for timing-generator and output-pixel-processor state.
5. Modeset, color, backlight, CRC, timing, ODM combine/split, diagnostics, and interrupt paths call `REG_UPDATE`, `REG_SET`, `REG_GET`, or `REG_READ`. Those helpers use the shift/mask values to alter or decode individual fields while preserving unrelated bits.

The chunk itself does not encode ordering. Callers must still sequence writes around clocks, resets, vblank/vupdate windows, double-buffer pending bits, update locks, genlock/swaplock state, power gating, and hardware interrupt clear/ack behavior.

## State And Persistence Behavior

The macros do not hold software state or persist data on disk. They describe state inside GPU display hardware registers. Configuration fields generally remain until overwritten, reset, power-gated, or restored by suspend/resume and modeset paths; status fields may be read-only, sticky, self-clearing, write-one-to-clear, or latch-on-read depending on the hardware register.

Important hardware state represented here includes:

- Adaptive brightness and backlight state: ABM PWM levels, user/ambient/target/current values, auto-calculated duty cycle, ACE curve segments, histogram/luma statistics, sample-rate frame counters, register locks, and master locks.
- Output formatting state: per-pipe clamp limits, pixel encoding, dynamic expansion, bit-depth truncation, spatial/temporal dithering, random seeds, stereo packing, and 420/422 handling.
- OPP buffer and pipe state: active output width, segmentation/overlap, pixel repetition, 3D dummy data and spacing, memory power controls, OPP pipe clock enable, and CRC capture state.
- Pattern and diagnostic state: DPG ramp/color/dimension generators, OPP pipe CRC windows/results, OTG CRC windows/results, perfmon counter selects/states/thresholds/readbacks, and snapshot status.
- ODM/OPTC input state: segment source selection, number of input segments, DSC data format and bytes-per-pixel, segment/slice widths, input clock enables, memory selection, underflow status, and double-buffer pending state.
- OTG timing-generator state: programmed timing totals and syncs, variable-vtotal controls, trigger sources/windows, flow-control delay, stereo/interlace mode/status, vertical interrupts, static-screen detection, global sync events, update locks, genlock/swaplock controls, vupdate keepout, and master/global update controls.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.1.2 register database and must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h`. A mask/shift symbol is meaningful only when paired with the corresponding register offset and base-index constants.

Observed integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`, which directly includes `dcn_3_1_2_offset.h` and `dcn_3_1_2_sh_mask.h` so DMUB service register helpers can expand `FD_MASK` and `FD_SHIFT` values for DCN31-family hardware.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which builds ABM, OPP, and OPTC register/mask/shift tables used by DCN31 resources. The chunk supplies many of the field names used by those table macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_abm.h` and the DMUB ABM paths, which map ABM fields such as sample-rate, current/target/user level, IPCSC selection, ACE, histogram progress, and PWM update control into backlight/adaptive-brightness operations.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn10/dcn10_opp.h`, `dcn20_opp.h`, and corresponding OPP implementations, which use FMT, OPPBUF, OPP pipe, and CRC fields when programming bit-depth reduction, clamping/pixel encoding, dithering, buffer segmentation, 3D parameters, memory power, and CRC readback.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn31/dcn31_optc.h` and `dcn31_optc.c`, which consume ODM and OTG fields for timing programming, ODM segment routing, DSC formatting at the timing generator input, CRC, vertical interrupts, update locks, genlock/swaplock, and state readback.
- User-facing and validation paths in DRM/AMDGPU that depend indirectly on these fields for modesets, panel brightness/ABM controls, CRC debugfs output, vblank/vertical interrupts, underflow handling, and display diagnostics.

## Risks And Edge Cases

- Numeric drift is the primary risk. A wrong mask or shift can compile successfully while programming the wrong hardware bits, corrupting visible color, timing, brightness, CRC diagnostics, or pipe routing.
- The range is artificially bounded. It starts mid-`ABM2` and ends immediately before the fields for `OTG0_OTG_TRIG_MANUAL_CONTROL`; adjacent chunks are required for complete ABM2 and OTG0 coverage.
- Repeated instance blocks are copy-sensitive. `DPG/FMT/OPPBUF/OPP_PIPE/OPP_PIPE_CRC` and `ODM` instances 0 through 3 share layouts but distinct prefixes; an instance-prefix error can silently bind one pipe's software table to another pipe's field names.
- ABM fields mix configuration, readback, locks, and hardware-collected histogram/luma data. Treating readback/status fields like ordinary writable configuration, or ignoring lock/update-pending fields, can produce stale brightness state or bad adaptive-brightness behavior.
- Formatter and OPP buffer fields are user-visible. Mistakes in clamp, encoding, truncation, dithering, 420/422, segmentation, overlap, or 3D fields can show up as color shifts, banding, stereo errors, corruption, or blank output rather than a clean kernel failure.
- ODM and OTG fields are timing-critical. Incorrect data-source selection, segment count, DSC bytes-per-pixel/slice width, vtotal limits, sync positions, update locks, GSL, vupdate keepout, or clock/reset bits can cause underflow, missed vblank/update events, broken multi-pipe combine, VRR issues, or display blanking.
- Status and interrupt fields have hardware-defined side effects that this generated file does not express. Consumers must know which bits are read-only, sticky, write-one-to-clear, self-clearing, double-buffered, or safe only during vblank/vupdate.

## Test Signals

Useful validation signals are mostly integration and hardware behavior rather than unit tests for this header alone:

- Kernel build coverage for DCN 3.1/3.1.2 paths, especially token-pasted field-list macros that fail compilation if a referenced generated symbol is missing or renamed.
- Modeset and hotplug smoke tests across all four timing/OPP instances, including ODM combine/split configurations where segment routing and DSC formatting fields are exercised.
- DRM CRC/debugfs tests that enable OPP and OTG CRC capture and confirm stable, expected readbacks from the result fields.
- Backlight and ABM tests on eDP panels, including user brightness changes, ABM level changes, ambient/user/current/target level programming, pause/save/restore, and histogram readback through DMUB ABM commands.
- VRR/vblank/vertical-interrupt tests that exercise OTG vtotal, vertical interrupt positions, global sync status, update locks, and vupdate keepout behavior.
- Display diagnostics/perfmon tests that configure `DC_PERFMON16` counters, observe threshold/interrupt status, and read low/high counter values without disturbing normal display output.

### subset-b-001814: lines 30070-32536

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 30070-32536

## Scope

This chunk is a generated AMD Display Core Next 3.1.2 register-field mask slice. It contains C preprocessor constants only: `_SHIFT` macros for field bit positions, `_MASK` macros for the corresponding 32-bit register bitmasks, and comment markers that group those fields by register and address block. There are no functions, structs, enums, local variables, branches, loops, allocations, or direct MMIO accesses in this line range.

The range starts in the tail of the `OTG0` timing-generator register definitions, covers the complete `dce_dc_optc_otg1_dispdec` and `dce_dc_optc_otg2_dispdec` register-field surfaces, and then covers most of the `dce_dc_optc_otg3_dispdec` block through `OTG3_OTG_DRR_TIMING_INT_STATUS`. The requested line boundary stops at `OTG3_OTG_DRR_TIMING_INT_STATUS__OTG_DRR_V_TOTAL_REACH_OCCURRED_INT_MSK_MASK`; the final `OTG_DRR_V_TOTAL_REACH_OCCURRED_INT_TYPE_MASK` for that register appears on the next source line and is outside this chunk.

## Purpose And Hardware Surface

The purpose of this header section is to provide the bit layout ABI used by AMDGPU Display Core code when programming DCN 3.1.2 output timing generators. Companion generated headers provide register offsets; this mask header provides the field positions and masks that register helper macros use to encode, decode, and update individual hardware fields without scattering numeric bit positions through functional driver code.

Hardware areas represented in this chunk:

- `OTG0` tail definitions for manual flow control, dynamic refresh rate timing interrupt status, DRR vtotal reach/change/trigger/control fields, M/N constant DTO phase and modulo, request control, DSC start position, pipe update status, and spare register fields.
- Full `OTG1` and `OTG2` OPTC/OTG register sets for scanout timing, blanking, sync generation, trigger A/B control, forced count updates, flow control, stereo and interlace state, live status counters, snapshot capture, vertical interrupts, CRC capture, static screen detection, 3D structure control, global swap lock, master update locking, vstartup/vupdate/vready signaling, DRR, DSC start position, request control, pipe update status, and spare fields.
- The start-to-near-end of the `OTG3` register set through global update controls and the `OTG3_OTG_DRR_TIMING_INT_STATUS` fields included by the requested line range.

This is display-pipe register metadata. Its correctness affects modeset timing, vblank/vsync interrupt delivery, atomic update sequencing, variable refresh behavior, display CRC diagnostics, stereo/interlace output, Display Stream Compression positioning, global synchronization, and low-level pipe status reporting.

## Important Definitions

The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit index.
- `<REGISTER>__<FIELD>_MASK` gives the field's raw mask within the 32-bit register.
- `// addressBlock: dce_dc_optc_otgN_dispdec` comments delimit per-OTG register blocks.
- `//OTGN_REGISTER_NAME` comments group the following field macros by hardware register.

Important field families in this chunk:

- Timing geometry: `OTG_H_TOTAL`, `OTG_H_BLANK_START_END`, `OTG_H_SYNC_A`, `OTG_V_TOTAL`, `OTG_V_TOTAL_MIN/MAX/MID`, `OTG_V_BLANK_START_END`, and `OTG_V_SYNC_A` define horizontal and vertical totals, blanking windows, sync ranges, polarity, and timing division controls. Most coordinate-like fields use 15-bit masks such as `0x00007FFFL` and `0x7FFF0000L`.
- DRR and vtotal control: `OTG_V_TOTAL_CONTROL`, `OTG_V_TOTAL_INT_STATUS`, `OTG_DRR_TIMING_INT_STATUS`, `OTG_DRR_V_TOTAL_REACH_RANGE`, `OTG_DRR_V_TOTAL_CHANGE`, `OTG_DRR_TRIGGER_WINDOW`, and `OTG_DRR_CONTROL` expose min/max/mid vtotal selection, event masks/acks, timing-update events, vtotal reach events, trigger windows, and last-used vtotal readback for variable refresh and frame pacing.
- Trigger and flow control: `OTG_TRIGA_CNTL`, `OTG_TRIGB_CNTL`, manual trigger registers, `OTG_FORCE_COUNT_NOW_CNTL`, `OTG_FLOW_CONTROL`, `OTG_TRIG_MANUAL_CONTROL`, and `OTG_MANUAL_FLOW_CONTROL` define trigger source selection, pipe selection, polarity, edge detection, frequency selection, delays, clear bits, and manual/global update flow controls.
- Scanout status and counters: `OTG_STATUS`, `OTG_STATUS_POSITION`, `OTG_NOM_VERT_POSITION`, `OTG_STATUS_FRAME_COUNT`, `OTG_STATUS_VF_COUNT`, `OTG_STATUS_HV_COUNT`, `OTG_COUNT_CONTROL`, and `OTG_COUNT_RESET` provide current timing-generator state, frame/field counters, h/v count readback, and counter reset/update controls.
- Stereo, interlace, and 3D output: `OTG_STEREO_FORCE_NEXT_EYE`, `OTG_CONTROL`, `OTG_INTERLACE_CONTROL`, `OTG_INTERLACE_STATUS`, `OTG_STEREO_STATUS`, `OTG_STEREO_CONTROL`, and `OTG_3D_STRUCTURE_CONTROL` expose current/next field, eye selection, stereo polarity, forced eye transitions, frame count reset/update state, interlace enable, and DP stereo/field output controls.
- Snapshot and interrupt controls: `OTG_SNAPSHOT_STATUS`, `OTG_SNAPSHOT_CONTROL`, `OTG_SNAPSHOT_POSITION`, `OTG_SNAPSHOT_FRAME`, `OTG_INTERRUPT_CONTROL`, and `OTG_VERTICAL_INTERRUPT{0,1,2}_{POSITION,CONTROL}` define snapshot request/clear/status fields and programmable vertical interrupt positions, sources, polarity, enables, clears, and status bits.
- Atomic update synchronization: `OTG_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_MASTER_EN`, `OTG_MASTER_UPDATE_MODE`, `OTG_MASTER_UPDATE_LOCK`, `OTG_GSL_CONTROL`, `OTG_GSL_WINDOW_X/Y`, `OTG_VUPDATE_KEEPOUT`, and `OTG_GLOBAL_CONTROL0..4` define update locks, double-buffer enable/update-instantly behavior, master enable, master update lock status, global swap lock windows, vupdate keepout offsets, and global update lock selection.
- CRC and diagnostics: `OTG_CRC_CNTL`, `OTG_CRC_CNTL2`, `OTG_CRC0/1_WINDOW*`, `OTG_CRC0..3_DATA_*`, and CRC signature masks define capture enable, continuous/one-shot mode, stereo/interlace handling, capture windows, data readback, and mask controls for display CRC validation.
- Miscellaneous pipe fields: pixel readback, blank color not present in this chunk but nearby in the file, static screen frame counting, `OTG_CLOCK_CONTROL`, vstartup/vupdate/vready parameters, global sync status, DTO phase/modulo, request mode for horizontal duplicate handling, DSC start position, pipe update pending status, and full-width spare registers.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior is created when AMDGPU Display Core code combines these constants with matching register offsets and register access helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and table-driven field descriptors.

A typical runtime pattern is:

1. Driver code selects an OTG instance and matching register offset from generated DCN 3.1.2 register tables.
2. The code uses this chunk's `_SHIFT` and `_MASK` macros to pack or unpack a field value.
3. The display register abstraction performs an MMIO read, write, or read/modify/write.
4. Hardware stores configuration fields, exposes volatile status fields, or consumes side-effecting clear/ack/reset bits.

The state represented here is hardware register state rather than C heap or stack state:

- Timing configuration, sync polarity, update lock, DRR, CRC, stereo/interlace, GSL, vstartup/vupdate/vready, DTO, DSC start position, and request-control fields persist in hardware registers until reprogrammed, reset, or power-gated.
- Status, scan position, frame count, field count, stereo state, global sync status, pipe update pending, clock-on, busy, CRC data, and DRR last-used vtotal fields are volatile readbacks produced by display hardware.
- ACK, clear, reset, manual trigger, force-count, snapshot, and event-clear fields are side-effecting write paths. They should be treated as commands to a hardware state machine, not durable configuration storage.
- Double-buffered and master-update fields have sequencing constraints. The mask constants do not enforce that sequencing; callers must coordinate update locks and vupdate/vready timing to avoid partial pipe updates.

## Dependencies And Integration Points

This chunk depends on generated-name consistency across the DCN 3.1.2 register header family. It is normally consumed together with matching offset and register-list headers for `dcn_3_1_2`, ASIC-specific display resource tables, and the AMDGPU Display Core register helper layer.

Primary integration points include:

- OPTC/OTG timing code that programs scanout totals, blanking, sync, trigger behavior, count resets, and master enable state.
- Atomic modeset and plane-update paths that use update locks, double-buffer controls, master update locks, global update lock selection, vupdate keepout windows, and pipe update pending status.
- Vblank, vsync, vertical interrupt, vstartup, vupdate, vready, and DRR interrupt handlers that use status, clear/ack, mask, and type fields.
- VRR/DRR logic that manipulates vtotal min/max/mid, DRR trigger windows, vtotal reach ranges, vtotal change limits, and average frame settings.
- Display CRC and validation paths that configure CRC windows/selectors, trigger one-shot or continuous capture, and read CRC data registers.
- Stereo, interlace, and 3D display support that consumes field-number, eye-selection, forced next eye, stereo sync, and frame count fields.
- DSC and request scheduling paths that use `OTG_DSC_START_POSITION` and `OTG_REQUEST_CONTROL` fields.
- Power and clock sequencing paths that use `OTG_CLOCK_CONTROL` enable, gate-disable, soft-reset, clock-on, and busy fields before accessing dependent timing-generator state.

Because these are macros, invalid names usually fail at compile time only where referenced. Incorrect numeric values can compile cleanly and then misprogram MMIO registers at runtime.

## Risks And Maintenance Notes

- Numeric drift from the ASIC register specification is the main risk. A wrong mask or shift can write the wrong bit, corrupting timing, interrupts, update locking, DRR, CRC capture, or clock/reset behavior.
- The OTG1, OTG2, and OTG3 blocks are highly repetitive. Instance-prefix mistakes can route a modeset, interrupt clear, update lock, or CRC operation to the wrong display pipe.
- The requested chunk boundary cuts through the `OTG3_OTG_DRR_TIMING_INT_STATUS` macro group. Any reconciliation or review should account for the missing final `OTG_DRR_V_TOTAL_REACH_OCCURRED_INT_TYPE_MASK` on the next source line.
- Clear/ack/reset/manual-trigger fields have side effects. Generic read/modify/write helpers must avoid accidentally writing event clear bits while only intending to update masks or type fields.
- Update-lock, double-buffer, vupdate keepout, and GSL fields are timing-sensitive. Misuse can produce partially applied timing changes, stale pipe update state, missed vupdate events, or visible display glitches.
- DRR/vtotal fields influence frame pacing. Incorrect min/max/mid/range/window programming can create unstable VRR behavior, unexpected frame durations, or missed vtotal reach interrupts.
- Full-width fields such as DTO phase/modulo and spare registers provide no type or range checking. Callers must validate values against hardware semantics before packing them through the macros.
- Clock enable, gate-disable, soft-reset, clock-on, and busy fields interact with power management. Accessing the OTG while the block is gated, resetting, or busy can make status readbacks unreliable.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware/display behavior:

- Build AMDGPU/DCN 3.1.2 code and ensure referenced macro names from this range resolve.
- Run generated-header checks that each in-scope register field has the expected `_SHIFT`/`_MASK` pair, masks are 32-bit, and field masks do not overlap unexpectedly within a register.
- Compare the generated values against the authoritative DCN 3.1.2 register specification, especially repeated OTG1/OTG2/OTG3 blocks and the chunk boundary around `OTG3_OTG_DRR_TIMING_INT_STATUS`.
- Exercise modesets on pipes using OTG1 and OTG2, and on OTG3 for the fields included here, validating horizontal/vertical timing, sync polarity, master enable, clock state, and scan position readback.
- Test atomic updates with update locks, double-buffer controls, global update locks, GSL windows, vupdate keepout, and pipe update pending status.
- Exercise vblank/vsync/vertical interrupt paths and confirm status, mask, type, clear, and ack bits behave as expected.
- Run VRR/DRR tests that validate vtotal min/max/mid programming, DRR timing update interrupts, vtotal reach events, trigger windows, and last-used vtotal readback.
- Use display CRC tests to configure windows, enable one-shot and continuous capture, read CRC0-CRC3 data, and verify pending/status bits clear correctly.
- Test stereo/interlace modes where supported, checking field/eye status, forced next eye behavior, frame count reset/update, and 3D structure controls.
- Validate suspend/resume or runtime power transitions that toggle OTG clock, gate, reset, busy, vstartup, vupdate, and vready related fields.

## Chunk-Specific Summary

Lines 30070-32536 define a dense DCN 3.1.2 OTG mask/shift surface, not executable logic. The chunk's most important responsibilities are per-pipe timing programming for OTG1 and OTG2, the tail of OTG0 DRR/update/status metadata, and most of OTG3 up to the DRR timing interrupt status group. Correctness depends on exact generated bit positions and masks, instance-correct macro use, careful handling of side-effecting clear/ack/reset fields, and hardware tests that cover modeset timing, atomic update sequencing, interrupts, DRR/VRR, CRC, stereo/interlace, DSC start position, and OTG clock/reset behavior.

### subset-b-001815: lines 32537-34973

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 32537-34973

## Scope And Purpose

This chunk is part of the generated AMD DCN 3.1.2 register shift/mask header. It exports preprocessor constants that describe bit positions (`__SHIFT`) and masks (`_MASK`) for memory-mapped display controller registers. The companion offset header supplies register addresses; this file supplies the field layout consumed by the AMD display register helper macros.

The requested range starts in the tail of the OTG3 timing-generator block, immediately after the `OTG3_OTG_DRR_TIMING_INT_STATUS` definitions, and continues through dynamic refresh-rate, constant DTO, DSC start-position, pipe-update, and spare-register fields. It then covers OPTC misc selection and memory-power fields, `DC_PERFMON17`, HPD instances 0 through 4, the full DP0 and DIG0 DIO register groups, and the beginning of DP1 through `DP1_DP_SEC_CNTL2`. The range ends mid-DP1; later DP1 secondary-packet, metadata, ALPM, GSP, and following DIO blocks continue in the next chunk.

There are no functions, structs, branches, loops, or direct runtime side effects in this chunk. The public surface is generated macro metadata. Runtime behavior is created when DCN resource constructors bind these masks and shifts into timing-generator, HPD/GPIO, link-encoder, stream-encoder, interrupt-service, and hardware-sequencer objects, after which display code uses `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and related helpers to program hardware.

## Register Blocks Covered

The OTG3 tail covers dynamic refresh-rate programming and status: vertical-total reach ranges, vertical-total change limits, trigger-window X ranges, average-frame and last-used vertical-total readback, M-constant DTO phase/modulo, horizontal-duplicate request mode, DSC start X/line position, pipe update pending/status bits, and a spare register.

The OPTC misc block covers DWB source selection for three writeback paths, global swap-lock ready/timing-sync source selection, OPTC clock-gating/test-clock controls, ODM memory power force/disable bits for memories 0 through 7, unassigned and vblank ODM memory power modes, ODM memory power status readback, and an OPTC misc spare register. `DC_PERFMON17` follows with the standard display performance-counter and perfmon field set: counter event/value selection, increment and hardware-control modes, run/interrupt/restart controls, counter state lanes 0 through 7, perfmon state/report count/interrupt controls, clock and run-enable start/stop selection, counter-value interrupt status/ack bits, and high/low counter readback selectors.

HPD0 through HPD4 are repeated hotplug-detect blocks. Each instance defines interrupt status and sense fields, interrupt and RX interrupt ack/enable/polarity fields, HPD enable and timer fields, fast-training connection delay/enables, and connect/disconnect debounce filter delays.

DP0 is a complete DisplayPort transmitter register field group. It includes link control, pixel format, MSA colorimetry/misc/timing, DP configuration and lane count, video stream enable/status/deferred-disable, FIFO steering, video M/N timing generation, link framing and enhanced frame mode, HBR2 eye pattern, VBID and video interrupt controls, DPHY controls for training patterns, symbols, 8b/10b, PRBS, scrambling, CRC, MST CRC, fast training, BS/SR swap, and HBR2 pattern control. It also includes secondary-data packet controls for stream, audio, ACP/ISRC/MPG/GSP packets, secondary-packet framing, DP audio N/M and readbacks, timestamp mode, MSE rate and stream-allocation-table programming/status, MSA timing parameter registers, MSO controls, DSC control and bytes-per-pixel, metadata transmission, ALPM, GSP8 through GSP11 controls, and GSP enable double-buffer status.

DIG0 is the corresponding digital encoder and HDMI/TMDS block. It covers frontend and backend control, output CRC control/result, clock/test/random pattern fields, FIFO status and recalibration fields, HDMI metadata, general HDMI control/status, HDMI audio and ACR packet controls and readbacks, VBI/infoframe/generic packet controls 0 through 10, general-control packet fields, AFMT audio clock control, TMDS mode/control characters, stereo-sync selection, sync-character patterns, TMDS control bits, DC balancer controls, DIG version, and forced disable.

DP1 begins a second DisplayPort transmitter instance with the same generated shape as DP0, but this chunk only reaches `DP1_DP_SEC_CNTL2`. The covered DP1 fields include link/video/pixel/MSA setup, DPHY training/CRC/fast-training controls, secondary packet enables and framing, DP audio N/M and readbacks, timestamp mode, MSE rate/SAT programming and status, MSA timing parameters, MSO controls, DSC control, and GSP1 through GSP7 send/pending/deadline/any-line controls plus the GSP11 PPS bit in `DP1_DP_SEC_CNTL2`.

## Important APIs, Types, And Macros

The important interface is the generated naming contract:

- `<register>__<field>__SHIFT` gives the field bit offset inside a 32-bit register.
- `<register>__<field>_MASK` gives the mask for that field.
- `// addressBlock: ...` and `//REGISTER_NAME` comments delimit generated register groups but are not compiled APIs.
- Instance prefixes in this chunk include `OTG3`, `HPD0` through `HPD4`, `DP0`, `DIG0`, and `DP1`; shared or unindexed OPTC names include `DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`, `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS`.

The OPTC fields integrate with timing-generator register tables such as `dcn10_optc.h`, `dcn30_optc.h`, and `dcn314_optc.h`. These headers map `GSL_SOURCE_SELECT` and `DWB_SOURCE_SELECT` fields into `dcn_optc_shift`/`dcn_optc_mask` structures, and runtime functions update GSL ready-source selection and DWB source muxing through the register helper layer. The ODM memory-power fields are also pulled into DCN31-family hardware-sequencer register lists in `display/dc/resource/dcn31/dcn31_resource.c`.

The HPD fields integrate with `display/dc/gpio/hpd_regs.h`, DCN GPIO hardware factories, and IRQ services such as `irq_service_dcn314.c`, `irq_service_dcn315.c`, and related DCN-family files. IRQ tables bind `HPD*_DC_HPD_INT_STATUS` as HPD and HPD RX interrupt status registers; link and GPIO paths use HPD control, sense, debounce, and enable fields to detect and filter hotplug events.

The DP and DIG fields are consumed by link-encoder and stream-encoder register lists. `display/dc/dio/dcn10/dcn10_link_encoder.h` maps DP link, DPHY, MSE SAT, secondary-packet, stream-enable, and HPD fields into `dcn10_link_enc_registers` and mask/shift structures. `display/dc/dce/dce_stream_encoder.h` and `display/dc/dio/dcn30/dcn30_dio_stream_encoder.h` map DP pixel format, MSA timing/colorimetry, MSE rate, secondary-packet, audio, DSC, metadata, HDMI, AFMT, TMDS, and DIG FIFO fields into stream-encoder objects.

`display/dmub/src/dmub_dcn31.c` includes `dcn_3_1_2_sh_mask.h` directly for DMUB-side DCN31-family register definitions. DCN 3.1/3.1.2 resource code includes the generated offset and shift/mask headers, builds static register, shift, and mask tables, and passes those tables to constructors for timing generators, link encoders, stream encoders, HPD objects, DIO, and hardware sequencing.

## Functional Field Groups

The OTG and OPTC fields describe timing-generator and output-pipe coordination state. DRR fields bound vertical-total changes and trigger timing for variable refresh behavior. `OTG_DSC_START_POSITION` coordinates compressed-stream start timing. Pipe-update status exposes pending flip, DC register update, cursor update, and vupdate keepout status. GSL source fields select which pipe readiness signals participate in global-swap-lock synchronization. DWB source selection routes OPTC output to writeback instances.

The ODM memory-power fields provide explicit power controls and readback for multiple ODM memories. `ODM_MEM*_PWR_FORCE` and `ODM_MEM*_PWR_DIS` are per-memory controls; `ODM_MEM_UNASSIGNED_PWR_MODE` and `ODM_MEM_VBLANK_PWR_MODE` set policy for unassigned or vblank periods; `ODM_MEM*_PWR_STATE` exposes current state. These fields are used by DCN hardware sequencing around init, mode changes, blanking, and power management.

HPD fields provide the low-level connector presence and interrupt surface. Status exposes raw and delayed sense, HPD interrupt status, RX interrupt status, and filter timer values. Control fields acknowledge interrupts, set polarity, enable HPD and RX interrupts, configure connection/RX timers, and enable fast-training handoff behavior after connect. Toggle filter controls debounce connect and disconnect transitions.

The DP link and DPHY fields program physical/link-layer behavior: lane count, link-training-complete, training pattern, bypass/test selection, PRBS, scrambler behavior, symbol pattern registers, 8b/10b controls, CRC source/result, MST CRC slot windows, HBR2 eye/pattern controls, fast-training timing/state, and BS/SR swap sequencing. These fields sit under link training, compliance testing, CRC diagnostics, and MST setup.

The DP stream and MSA fields program stream presentation: pixel encoding, component depth, dynamic and YCbCr range, MSA misc/colorimetry, VBID, timing totals/start/sync/active dimensions, video M/N generation, stream enable/status/deferred-disable, FIFO reset, and video interrupt controls. Incorrect values here affect sink timing interpretation, color format, stream enable sequencing, and audio/video packet alignment.

The DP secondary-data, audio, MST, MSO, DSC, metadata, ALPM, and GSP fields provide packetized sideband behavior. Secondary controls enable audio/sample, timestamp, ACP, ISRC, MPG, generic stream packets, and GSP slots; `DP_SEC_CNTL2` through later registers control per-GSP send, pending, deadline-missed, any-line, and line-number behavior. MSE rate and SAT fields configure MST payload bandwidth and slot allocation. MSO controls split SST links. DSC fields select DSC mode, slice width, and bytes-per-pixel. Metadata and ALPM fields support modern link features such as HDR/metadata packets and panel low-power modes.

The DIG0 HDMI/TMDS fields provide the HDMI and legacy digital-encoder surface. They control HDMI packet-generation version, deep color, scrambling, keepout, null/general/control/infoframe/VBI packet scheduling, audio packet and ACR timing, AFMT audio clock, TMDS control characters and DC balancing, output CRC/test patterns, FIFO calibration/status, and frontend/backend enable/source selection.

## Control Flow And State Behavior

This header has no direct control flow. Its macros become runtime behavior only after expansion into register tables and register helper calls. Resource initialization pairs addresses from the matching DCN 3.1.2 offset header with shifts/masks from this file. Later, hardware blocks use those tables to read and update memory-mapped registers.

The described hardware state persists in display-controller registers until driver writes, firmware activity, reset, power transitions, or hardware events change it. Configuration state includes DRR windows, DWB/GSL muxes, memory-power modes, HPD timers/enables, DP lane/pixel/MSA/link settings, secondary packet enables, MSE/MST allocation, DSC/MSO setup, HDMI packet controls, TMDS controls, and DIG source/enable fields. Status and telemetry include pipe-update pending bits, ODM memory power state, perfmon counters and interrupts, HPD sense/interrupt state, DP stream status, DPHY CRC results, fast-training status, MSE update pending/SAT status, DIG FIFO status, and HDMI/CRC readbacks.

Several covered groups are explicitly ordered or timing-sensitive. DRR and pipe update fields interact with vertical timing and keepout windows. GSL source selection must match the pipes participating in synchronized updates. ODM memory power should not be forced off while the corresponding output path is active. HPD interrupt ack, polarity, filter, and enable programming must preserve latched status and avoid spurious connect/disconnect detection. DP training, stream enable, MSA timing, secondary packet transmission, MST SAT updates, and DSC enable must follow the link and stream sequencing expected by the sink.

MST and packet state is double-buffered or pending in several places. MSE rate and SAT updates expose pending/keepout state and require waits or polling before subsequent payload changes. `DP_SEC_*_SEND_PENDING` and deadline-missed fields indicate packet scheduling state; tests and runtime code must distinguish a scheduled packet from a completed packet. HDMI generic/infoframe controls similarly have update and line-selection semantics that can affect when a changed packet becomes visible on the wire.

## Dependencies And Integration Points

This file must stay synchronized with `dcn_3_1_2_offset.h`. The offset header supplies `reg...` address symbols for the same register names, while this header supplies field layout. A mismatch can break compilation in generated register-list initializers or silently program the wrong bits if names still compile but the hardware specification has drifted.

The OPTC and HWSEQ consumers include `display/dc/optc/dcn10/dcn10_optc.h`, `display/dc/optc/dcn30/dcn30_optc.h`, `display/dc/optc/dcn314/dcn314_optc.h`, and DCN31-family resource/hardware-sequencer setup. Runtime functions in OPTC and HWSEQ code use the GSL, DWB source, and ODM memory-power masks during synchronized update setup, writeback routing, and display memory power policy programming.

The HPD consumers include GPIO hardware factories, `display/dc/gpio/hpd_regs.h`, IRQ services, and link-encoder HPD helper paths. HPD status and control masks are central to connector detection, HPD RX interrupt processing, debounce timing, and AUX/HPD association.

The DP link-layer consumers include `display/dc/dio/dcn10/dcn10_link_encoder.h` and `display/dc/dce/dce_link_encoder.c`. Those paths program DP DPHY training, scrambler, PRBS, link framing, stream enable, MST SAT allocation, fast training, and HPD-related link state using the DP0 base field names from this generated header and per-instance register addresses.

The stream-encoder consumers include `display/dc/dce/dce_stream_encoder.h`, `display/dc/dce/dce_stream_encoder.c`, `display/dc/dio/dcn30/dcn30_dio_stream_encoder.h`, and `display/dc/dio/dcn30/dcn30_dio_stream_encoder.c`. These paths program DP pixel format, MSA, M/N generation, secondary packet controls, HDMI infoframes, audio and ACR, AFMT, DIG FIFO, DSC packet state, metadata, and TMDS behavior.

The perfmon fields are generated diagnostic metadata. They may be used by register dumps, debug tooling, firmware-assisted diagnostics, or future instrumentation through the standard display register helper layer; correctness still matters because a wrong counter control or readback mask can mislead performance and interrupt analysis.

## Risks And Edge Cases

Generated-header drift is the main risk. An incorrect shift or mask can corrupt unrelated fields in the same 32-bit register, causing display timing instability, bad color format, failed link training, lost HPD events, broken audio/infoframes, MST payload allocation failures, DSC/MSO misprogramming, writeback source routing errors, or misleading diagnostic counters.

The chunk boundaries split logical hardware blocks. The OTG3 interrupt status register is partially in the previous chunk, and DP1 continues in the next chunk. Merge/reconciliation must not treat this chunk alone as complete coverage for OTG3 or DP1.

HPD status/control registers mix latched event bits, sense readback, ack bits, polarity, enables, and timers. Full-register writes or stale masks can accidentally acknowledge events, invert polarity handling, disable RX interrupts, or shorten debounce windows enough to create hotplug flapping.

DP link training and compliance fields are sensitive to ordering and sink capabilities. Training pattern selection, scrambler state, lane count, PRBS/test patterns, fast-training timers, and link-training-complete state must align with AUX/DPCD negotiation. Bad masks can pass normal modes but fail CTS, MST, fast-training, or HBR2 diagnostic cases.

MST/MSE programming has pending and keepout semantics. Updating SAT slots or MSE rate without respecting `DP_MSE_RATE_UPDATE_PENDING`, `DP_MSE_SAT_UPDATE`, and `DP_MSE_16_MTP_KEEPOUT` can create transient payload mismatches, bandwidth drops, or stream corruption.

Secondary packet and HDMI packet controls are stateful and line-timed. Wrong send, continuous, line-reference, any-line, or deadline fields can drop HDR/AVI/audio/GSP/ISRC packets, send them on the wrong line, or report missed deadlines. Some failures appear only as sink-side feature loss rather than a driver error.

DIG FIFO, CRC, and perfmon fields are diagnostic but still stateful. Tests must clear or acknowledge status before measuring, choose the intended read selector/source, and avoid interpreting stale CRC/perfmon/FIFO extrema as current behavior.

ODM and DIO memory-power controls can cause mode-change or suspend/resume-only failures. Forcing memories off while scanout, writeback, or output-merger paths are active can produce intermittent blanking, underflow-like symptoms, or bad wake behavior.

## Test Signals

Build-time coverage should catch missing or renamed macros in DCN31/312 include paths, OPTC/HWSEQ tables, HPD register lists, link-encoder masks, and stream-encoder masks. High-signal failures include missing `OTG3_*`, `DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `ODM_MEM_PWR_CTRL3`, `HPD0_*`, `DP0_*`, `DIG0_*`, or `DP1_*` field names referenced by register-list macros.

Runtime HPD validation should exercise connect/disconnect and HPD RX interrupts across HPD0 through HPD4, including debounce timing, interrupt ack, polarity, delayed sense, and fast-training delay controls. Expected signals are stable connector detection, no interrupt storms, correct HPD RX handling, and accurate delayed sense readback.

DP link validation should cover SST and MST modes on DP0 and DP1 where routed, link training at multiple rates/lane counts, DPHY CRC, PRBS/compliance patterns, HBR2 pattern control, fast training, scrambler behavior, and stream enable/deferred-disable sequencing. Useful signals include successful modesets, no unexpected stream-status drops, correct CRC/test-pattern behavior, and passing CTS-style link tests.

MST and sideband packet validation should cover MSE rate programming, SAT slot allocation/status, SAT update pending/keepout waits, secondary packet enables, GSP send/pending/deadline status, HDR/metadata packets, ISRC/MPG, and DSC PPS/GSP11 behavior. Register dumps should show coherent MSA timing, MSE allocation, and packet scheduling state.

HDMI/DIG validation should cover HDMI deep color and scrambling, AVI/audio infoframes, generic packets, ACR N/CTS programming and readback, audio packet generation, TMDS controls, output CRC/test patterns, and DIG FIFO status. Expected signals are stable HDMI output, correct sink-reported packet/audio state, no FIFO error flags after clear, and matching CRC results for known frames.

Power-management validation should exercise blanking, mode changes, suspend/resume, writeback source changes, and ODM memory-power modes. Signals include correct ODM memory-power status, no blanking or corruption during vblank power policy changes, and no regressions in synchronized update/GSL paths.

### subset-b-001816: lines 34974-37370

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 34974-37370

## Scope

This chunk is a generated DCN 3.1.2 register-field mask slice from `dcn_3_1_2_sh_mask.h`. It contains preprocessor constants only: `_SHIFT` macros for field bit positions, `_MASK` macros for raw 32-bit register masks, and comment markers that name hardware registers and address blocks. There are no C functions, structs, enums, executable branches, loops, or in-memory state objects in this range.

The slice starts in the tail of `DP1_DP_SEC_CNTL2`, covers the rest of the DP1 secondary-packet and late DisplayPort controls, then covers the full `dce_dc_dio_dig1_dispdec` DIG1 encoder/HDMI/TMDS field surface, the full `dce_dc_dio_dp2_dispdec` DP2 DisplayPort field surface, the full `dce_dc_dio_dig2_dispdec` DIG2 encoder/HDMI/TMDS field surface, and the beginning of `dce_dc_dio_dp3_dispdec` through the first `DP3_DP_DPHY_SYM0` symbol fields.

## Purpose And Hardware Surface

The purpose of this header range is to provide the bit layout ABI between AMDGPU Display Core code and DCN 3.1.2 display hardware. Companion offset headers identify MMIO register addresses; this mask header identifies each field's low bit and mask so display code can pack values, decode readbacks, and perform read/modify/write updates without embedding magic bit numbers in functional code.

Major hardware areas represented here:

- DP1 late secondary-packet controls: GSP1-GSP11 send/status fields, line-number fields, double-buffer disable/status fields, MSA/VBID override fields, secondary metadata transmission, DSC byte-per-pixel, ALPM PHY sleep/standby control, and GSP8-GSP11 per-packet controls.
- `DIG1` digital encoder fields: front-end mode and source selection, output CRC, clock/test/random patterns, FIFO status, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic-packet controls, HDMI deep-color/general-control bits, audio formatter enable, backend enable/control, TMDS control, sync/control-character programming, DC balancer, and DIG version/force-disable.
- DP2 link and stream fields: link status, pixel format, MSA colorimetry, lane configuration, video stream enable/status, steer FIFO overflow, MSA misc, DPHY controls, video M/N timing, link framing, training patterns, 8b/10b and PRBS/scrambler controls, CRC controls/results, fast training, secondary packet control, audio M/N/timestamp, MST/MSE rate and slot allocation controls, MSA timing parameters, MSO, DSC, metadata, ALPM, and GSP8-GSP11 controls.
- `DIG2` duplicates the DIG1 encoder/HDMI/TMDS surface for the next digital encoder instance, with identical field families under the `DIG2_` prefix.
- DP3 begins at the end of this range with link, pixel format, MSA, stream, FIFO, DPHY internal/timing/M/N/framing/interrupt, FEC/scrambler/training, and the first DPHY symbol pattern fields.

## Important Definitions

The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field's unshifted mask within the 32-bit register.
- `// addressBlock: ...` comments identify the display hardware aperture for following definitions.
- `//<REGISTER>` comments group field definitions by MMIO register.

Important field families in this chunk:

- Secondary data packet controls for DP1 and DP2 include GSP send requests, pending bits, active bits, deadline-missed bits, any-line mode, send-in-idle mode, line-reference selection, target line numbers, MSO lane enables, and double-buffer disable/status bits. These fields are used for DisplayPort secondary data packets such as infoframes, metadata, PPS/DSC-related packets, and generic stream packets.
- `DP*_DP_DB_CNTL` fields expose double-buffer pending/taken/clear/lock/disable state plus vupdate-specific pending/taken/clear bits. These are synchronization controls for programming packet/timing-related registers at safe update boundaries.
- MSA/VBID fields cover pixel encoding/component depth/combine, colorimetry misc bytes, MSA timing parameters, VBID override bits, stereo sync override, VBID field polarity, and MSA insertion location. These are part of the DisplayPort main stream attribute and video blanking ID programming path.
- DSC and MSO fields include DSC mode, slice width, bytes per pixel, MSO per-lane secondary packet enables, and metadata packet enable/line controls. These fields integrate compressed streams and multi-stream/multi-segment output paths with secondary data transmission.
- DP link/DPHY fields cover link-training-complete/status, lane count, stream enable/defer/status, steer/TU overflow interrupts and ACKs, FEC enable/ready/active state, scrambler selection/disable/advance/BS count/K-code, bypass/skew controls, training-pattern selection, symbol pattern registers, 8b/10b reset/disparity controls, PRBS enable/select/seed, CRC enable/selector/mask/result, MST CRC controls/status, and fast-training controls/status.
- DP MST/MSE fields include rate calculation controls, stream-rate updates, stream allocation table words, SAT update triggers/status, link timing, misc controls, and per-slot/status masks. These support DisplayPort multi-stream transport allocation and link scheduling.
- DIG front-end and backend fields select pixel source, enable the DIG front end/backend, select mode, report FIFO underflow/overflow, and expose DIG type/version/force-disable. The field names distinguish source/mode controls from status bits such as FIFO error state.
- HDMI packet fields cover metadata packet output, HDMI enable, keepout modes, null/audio/ACR/VBI/infoframe/generic packet send controls, line references, pending/status/readback bits, general control packet fields, audio sample rate/layout/channel count, and ACR CTS/N programming/readback for 32 kHz, 44.1 kHz, and 48 kHz families.
- TMDS fields cover clock pattern/test pattern data, random pattern seed, data and control character patterns, per-control-bit selection, feedback and stereo sync controls, DC balancer state, sync DC-balance characters, per-control-lane generator selection/delay/invert/modulation/feedback/pattern-enable fields, and a TMDS 2-bit counter enable.
- Interrupt-like fields in this range use a familiar status/ack/mask pattern: stream-disable interrupts, steer/TU overflow flags and ACKs, secondary packet pending/active/deadline bits, FIFO status, HDMI packet pending/sent state, and CRC result-valid state.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when AMDGPU Display Core code combines these constants with register addresses and register helper macros. A typical usage pattern is:

1. Select the DCN 3.1.2 register address from a companion offset/header table.
2. Use this chunk's `_SHIFT` and `_MASK` macros to pack, update, or extract a field.
3. Perform an MMIO write, read, or read/modify/write through AMD display register helpers.
4. Let display hardware retain, consume, update, or clear the register-backed state according to the register semantics.

The state represented here is hardware state rather than driver-owned memory:

- Persistent configuration fields include DP link format, lane count, pixel encoding/depth, MSA/VBID values, DSC/MSO metadata settings, secondary packet enable/line scheduling, DIG source/mode/backend enables, HDMI packet/audio/ACR controls, TMDS patterns, DPHY scrambler/FEC/training configuration, and MST/MSE scheduling parameters.
- Volatile status/readback fields include link-training-complete, stream status, FIFO overflow/underflow, packet pending/sent/active/deadline state, DPHY FEC active status, CRC result valid/results, fast-training status, M/N readbacks, ACR CTS/N readbacks, SAT update status, and GSP enable double-buffer status.
- ACK, clear, reset, send, update, and trigger fields are side-effecting write paths. Examples include GSP send bits, `DP_DB_TAKEN_CLR`, vupdate taken clear, stream-disable ACK, steer/TU overflow ACKs, CRC enable/result capture controls, 8b/10b reset, MSE rate/SAT update requests, and HDMI packet send controls.
- Double-buffered fields are timing-sensitive. The `DP*_DP_DB_CNTL` and `DP*_DP_GSP_EN_DB_STATUS` definitions indicate that some GSP enable changes and packet controls can be staged and taken at update boundaries instead of immediately.
- Shared transport state must be sequenced with the active display pipe. DP link training, FEC, scrambler, MST/MSE slot allocation, secondary packet scheduling, DSC PPS/metadata, and ALPM PHY sleep/standby controls interact with live stream state and cannot be safely treated as independent booleans.

The masks do not encode ordering constraints. Correct callers still need to hold the appropriate display locks, use update locks or double-buffering where required, poll/observe pending and active status bits, avoid clearing latched interrupts before service, and respect link-training, stream-disable, power, and vblank/vupdate sequencing.

## Dependencies And Integration Points

This chunk integrates with:

- Companion DCN 3.1.2 register offset/address headers for the same ASIC register namespace, especially generated `dcn_3_1_2_offset.h` style tables.
- AMDGPU Display Core register helper macros and generated register tables that consume `<register>__<field>__SHIFT` and `<register>__<field>_MASK` constants for `REG_GET`, `REG_SET`, `REG_UPDATE`, and similar operations.
- DisplayPort stream setup code that programs link status expectations, lane count, pixel encoding/component depth, MSA/VBID, video M/N, link framing, stream enable/defer, DPHY training, FEC, scrambler, PRBS/test patterns, CRC, and fast training.
- DisplayPort secondary-packet code for GSP packet enables, line scheduling, metadata packets, DSC PPS/bytes-per-pixel fields, MSO per-lane packet enables, and packet send/pending/deadline status.
- MST/MSE scheduling code that updates rate controls, stream allocation table words, SAT update triggers, link timing, and MSE status fields for multi-stream transport.
- DIG encoder setup code that selects front-end source/mode, backend enables, FIFO handling, output CRC, HDMI/TMDS mode selection, test patterns, and force-disable/version checks.
- HDMI output code that manages metadata, audio, ACR, VBI, AVI/vendor/generic infoframes, general control packets, deep color, packet keepout behavior, and packet send/readback status.
- Audio formatter code that coordinates HDMI audio packet controls, AFMT enable, channel/sample metadata, and ACR N/CTS values/readbacks.
- Diagnostics and validation tooling that reads DP/DPHY CRC results, DIG output CRC, FIFO status, link/training status, packet status, TMDS patterns, and MST/MSE allocation status.
- Power-management and link idle paths using DP ALPM PHY sleep/standby send/pending/immediate/line-number fields and `DP_LINK_TRAINING_SWITCH_BETWEEN_VIDEO`.

Because these are generated preprocessor macros, name mismatches are usually compile-time failures only where a macro is referenced. Numeric mask or shift drift can compile cleanly and then misprogram MMIO fields at runtime.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.2 register specification is the main risk. An incorrect mask or shift can silently write the wrong bits in display hardware registers, affecting link training, stream enable, packet scheduling, HDMI audio/infoframes, MST allocation, or PHY state.
- This range is highly repetitive across DP1/DP2/DP3 and DIG1/DIG2 instances. Prefix mistakes can target the wrong link or encoder instance while still compiling if the mistaken macro exists.
- The chunk starts and ends in the middle of logical hardware coverage: it begins after the first `DP1_DP_SEC_CNTL2` shift fields and ends partway through DP3 DPHY symbol definitions. The merge/reconciliation lane must combine adjacent chunks for a complete per-file view.
- Side-effecting bits are easy to misuse in generic read/modify/write helpers. Clear/ACK/reset/send/update bits should be programmed with awareness of hardware semantics so pending interrupts, packet sends, MSE updates, CRC captures, and reset sequences are not lost or repeated unintentionally.
- Double-buffer and update-boundary fields require sequencing. Misusing GSP enable DB disable/status, `DP_DB_LOCK`, pending/taken/clear bits, or vupdate taken fields can cause partially applied secondary-packet changes or visible packet/timing glitches.
- DP secondary packet and metadata fields interact with DSC, MSO, MST, and HDMI/DIG packet paths. Incorrect line numbers, any-line mode, line-reference selection, or send-in-idle behavior can create missed deadlines or malformed metadata on the wire.
- Link PHY controls are stateful and hardware-sensitive. FEC, scrambler, bypass, training pattern, 8b/10b, PRBS, CRC, fast-training, and ALPM fields can disrupt active links if toggled outside the expected training or idle windows.
- MST/MSE rate and SAT update fields can affect bandwidth allocation for multiple streams. Bad values or missed update-status checks can cause link oversubscription, stream starvation, or incomplete slot updates.
- HDMI ACR/audio/infoframe fields must match the mode and audio format. Incorrect CTS/N, sample-rate, layout, deep-color, or packet-control fields can produce audio dropouts or invalid HDMI metadata despite a lit display.
- Wide fields such as M/N, ACR CTS/N, timestamp, symbol patterns, SAT words, CRC results, packet line numbers, and metadata payload-related controls have no type checking here. Callers must validate ranges and units before packing values.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generated-header consistency, and hardware/display smoke tests:

- Build AMDGPU with DCN 3.1.2 support and ensure all referenced generated macro names resolve.
- Run generated-header consistency checks that each field has the expected `_SHIFT`/`_MASK` pair, masks fit in 32 bits, and fields do not overlap unexpectedly within each register.
- Exercise DisplayPort modeset paths using DP1, DP2, and DP3-adjacent hardware coverage, including lane count, pixel format, MSA/VBID, stream enable/defer, video M/N, link framing, and stream-disable interrupt handling.
- Run link-training and PHY diagnostics that cover DPHY training patterns, FEC enable/ready/active status, scrambler controls, PRBS, 8b/10b reset/disparity, CRC enable/result-valid/readback, and fast-training status.
- Validate DP secondary packet behavior for GSP1-GSP11, metadata packets, DSC PPS/bytes-per-pixel, MSO enables, any-line/line-number scheduling, send-in-idle, pending/active/deadline status, and double-buffer taken/clear behavior.
- Exercise DSC/MSO/MST cases, checking MSE rate update, SAT programming/update/status, link timing, MSA timing parameter fields, and stream allocation behavior under multiple stream configurations.
- Exercise HDMI output on DIG1 and DIG2, including HDMI enable, deep color/general control, metadata/infoframe/generic packet send controls, VBI/null/audio packets, ACR CTS/N programming, and packet status/readbacks.
- Run audio validation through DIG1/DIG2 HDMI paths, checking AFMT enable, audio sample rate/layout/channel count, ACR values, and absence of audio dropouts across mode changes.
- Use display diagnostics to verify DIG output CRC and DP DPHY CRC results, FIFO underflow/overflow status, TMDS test/control patterns, and random pattern seed behavior.
- Test suspend/resume, display blank/unblank, link idle, and ALPM paths to ensure PHY sleep/standby send/pending/immediate/line-number fields do not strand links or interfere with link training between video periods.

## Chunk-Specific Summary

Lines 34974-37370 define a dense DCN 3.1.2 register-field surface rather than executable code. The most important responsibilities in this slice are DP1 late secondary-packet scheduling, complete DIG1 and DIG2 encoder/HDMI/TMDS field maps, complete DP2 link/PHY/secondary-packet/MST/MSO/DSC field maps, and the opening DP3 link/PHY field map. Correctness depends on exact generated masks and shifts, instance-correct macro use, and hardware behavior under modeset, DP link training, secondary packet delivery, DSC/MSO/MST, HDMI audio/infoframes, CRC/test-pattern diagnostics, ALPM, and interrupt/status handling.

### subset-b-001817: lines 37371-39761

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 37371-39761

## Scope

This chunk covers 2,391 lines from the generated DCN 3.1.2 display register shift/mask header. It contains preprocessor constants and generated register-group comments only; there are no C functions, structs, enums, storage definitions, branches, loops, or local algorithms in this range.

The range starts in the middle of `DP3_DP_DPHY_SYM0`, after the `DPHY_SYM1` mask and before the remaining `DPHY_SYM2`/`DPHY_SYM3` masks. It then covers the tail of the DisplayPort 3 link/secondary-data-packet surface, the full `dce_dc_dio_dig3_dispdec` digital encoder and HDMI/TMDS surface, the full `dce_dc_dio_dp4_dispdec` DisplayPort 4 surface, and the beginning of `dce_dc_dio_dig4_dispdec`. It ends inside `DIG4_HDMI_GENERIC_PACKET_CONTROL5`, after generic packet 8 immediate-send pending mask; masks for generic packets 9 through 14 continue in the next chunk.

The chunk contains 2,174 `#define` entries: 1,092 `__SHIFT` definitions and 1,090 `_MASK` definitions. The uneven count is expected for this slice because it begins and ends inside register groups. Generated comments identify register blocks for the DP3 tail, `DIG3`, full `DP4`, and early `DIG4`.

## Purpose

This header slice gives DCN 3.1.2 AMD display code symbolic bit offsets and bit masks for DisplayPort and digital encoder register fields. Runtime code pairs these constants with the matching offset header and AMD display register helpers to construct MMIO read/modify/write operations without embedding literal bit arithmetic at call sites.

For `DP3`, the chunk covers the lower-level DisplayPort PHY and stream-control tail: DPHY training symbols, 8b/10b state, PRBS and scrambler controls, CRC controls and results, MST CRC phase status, fast-training controls/status, secondary-data-packet enablement and framing, audio N/M values and readbacks, packet coding and channel-count override, multi-stream encoder rate and slot-allocation table controls/status, MSA timing parameters, MSO controls, DSC enablement, double-buffer controls, VBID misc, SDP metadata transmission, DSC bytes-per-pixel, ALPM controls, and GSP8 through GSP11 controls/status.

For `DIG3`, the chunk maps the digital encoder instance that can drive HDMI/TMDS style output paths. It includes front-end source selection and start state, output CRC generation, clock/test/random patterns, FIFO status, HDMI metadata and control/status fields, audio and ACR packet controls, VBI and infoframe scheduling, generic HDMI packet send/continue/line/update-lock/immediate-send controls, DB control, audio clock regeneration values for 32/44.1/48 kHz families, AFMT controls, back-end enablement, TMDS control characters, sync patterns, DC balancer controls, TMDS generated-control bits, version, and force-disable controls.

For `DP4`, the chunk covers a complete DisplayPort transmitter instance. It maps link status/training state, pixel format and colorimetry, DP configuration and video stream control, FIFO steering, MSA misc/timing/VBID fields, DPHY internal controls, video timing and M/N values, link framing, HBR2 eye pattern and test controls, video interrupts, DPHY training/scrambler/CRC/fast-training controls, secondary-data-packet and audio timing controls, MST/MSE rate and slot-allocation controls/status, MSO controls, DSC controls, packet double-buffering, metadata transmission, DSC byte-per-pixel fields, ALPM controls, and GSP8 through GSP11 packet controls/status.

For `DIG4`, the chunk begins the next digital encoder instance and maps its front-end/output-CRC/test-pattern/FIFO fields plus the early HDMI packet-control surface through the first half of `HDMI_GENERIC_PACKET_CONTROL5`.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated preprocessor naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field's 32-bit mask.
- Comments such as `// addressBlock: dce_dc_dio_dp4_dispdec`, `//DP4_DP_LINK_CNTL`, and `//DIG3_HDMI_CONTROL` group constants by generated hardware block and register.

Important `DP3` register families in this range include:

- `DP3_DP_DPHY_*`: symbol pattern words, 8b/10b reset/disparity fields, PRBS enable/select/seed fields, scrambler disable/advance/BS count/K-code fields, CRC enable/control/result fields, MST CRC phase-lock/error/ack fields, and fast-training capability/start/timing/status fields.
- `DP3_DP_SEC_*`: secondary-data-packet stream/ASP/ATP/AIP/ACM/GSP/MPG enables, GSP0 scheduling and pending/deadline status, SDP framing positions and widths, audio mute/collision status, audio N/M and readback fields, timestamp mode, packet coding type, packet priority, SDP version, and audio channel-count override.
- `DP3_DP_MSE_*`: MST multi-stream encoder rate numerator/denominator fields, rate-update pending state, SAT source/slot-count fields, SAT update controls, link-frame/link-line timing, blank-code/timestamp/zero-encoder controls, and SAT status readbacks.
- `DP3_DP_MSA_*`, `DP3_DP_MSO_*`, and `DP3_DP_DSC_*`: main stream attribute timings, MSO segment/link-count/enable controls, and DSC mode/bytes-per-pixel fields.
- `DP3_DP_ALPM_CNTL` and `DP3_DP_GSP8_CNTL` through `DP3_DP_GSP11_CNTL`: ALPM pattern/symbol/error-status fields and extended generic SDP line, send, pending, and update controls.

Important `DIG3` register families include:

- `DIG3_DIG_FE_CNTL`, `DIG3_DIG_BE_CNTL`, and `DIG3_DIG_BE_EN_CNTL`: source selection, stereo sync, start, bypass, input-pixel selection, Dolby Vision enable/missed status, symbol-clock state, TMDS pixel/color encoding, back-end mode, and enable state.
- `DIG3_DIG_OUTPUT_CRC_*`, `DIG3_DIG_CLOCK_PATTERN`, `DIG3_DIG_TEST_PATTERN`, `DIG3_DIG_RANDOM_PATTERN_SEED`, and `DIG3_DIG_FIFO_STATUS`: diagnostic output CRC, clock/test-pattern generation, random-pattern seed, and FIFO overflow/underflow/depth/sync status fields.
- `DIG3_HDMI_*`: metadata packet controls, HDMI enable/deep-color/packing/reorder/scrambler/control-period controls, HDMI status, audio packet enable/continue fields, ACR packet source/send/continue/select controls, VBI null/general-control/ISRC send controls, audio and MPEG infoframe send/line controls, generic packet controls 0 through 14, immediate-send pending bits, generic packet line controls, DB control, ACR N/CTS programming/status for 32 kHz, 44.1 kHz, and 48 kHz bases, and HDMI general-control fields.
- `DIG3_AFMT_CNTL` and `DIG3_TMDS_*`: AFMT audio/HDMI state and forced audio-clock controls plus TMDS modulation, control-character, sync-character, stereo-sync, control-bit, DC-balancer, and generated-control fields.

Important `DP4` register families include:

- `DP4_DP_LINK_CNTL`, `DP4_DP_PIXEL_FORMAT`, `DP4_DP_MSA_COLORIMETRY`, `DP4_DP_CONFIG`, `DP4_DP_VID_STREAM_CNTL`, `DP4_DP_STEER_FIFO`, and `DP4_DP_MSA_MISC`: link-training completion/status, embedded-panel mode, component depth, pixel encoding, dynamic range, colorimetry, stereo/alternate-scrambler/DP clock settings, stream enable/mode/start/stop, FIFO steering, and MSA misc values.
- `DP4_DP_DPHY_INTERNAL_CTRL`, `DP4_DP_DPHY_CNTL`, `DP4_DP_DPHY_TRAINING_PATTERN_SEL`, `DP4_DP_DPHY_SYM*`, `DP4_DP_DPHY_8B10B_CNTL`, `DP4_DP_DPHY_PRBS_CNTL`, `DP4_DP_DPHY_SCRAM_CNTL`, `DP4_DP_DPHY_CRC_*`, and `DP4_DP_DPHY_FAST_TRAINING*`: PHY ownership, link clock controls, bypass/skew settings, training symbols, scrambler/PRBS/CRC diagnostics, MST CRC phase status, and fast-training state.
- `DP4_DP_VID_TIMING`, `DP4_DP_VID_N`, `DP4_DP_VID_M`, `DP4_DP_LINK_FRAMING_CNTL`, `DP4_DP_HBR2_EYE_PATTERN`, `DP4_DP_VID_MSA_VBID`, and `DP4_DP_VID_INTERRUPT_CNTL`: stream timing, M/N generation, link framing, HBR2 eye-pattern testing, VBID, and video interrupt status/mask/ack controls.
- `DP4_DP_SEC_*`, `DP4_DP_MSE_*`, `DP4_DP_MSA_TIMING_PARAM*`, `DP4_DP_MSO_*`, `DP4_DP_DSC_*`, `DP4_DP_DB_CNTL`, `DP4_DP_MSA_VBID_MISC`, `DP4_DP_SEC_METADATA_TRANSMISSION`, `DP4_DP_ALPM_CNTL`, and `DP4_DP_GSP*`: packetization, audio timing, MST/MSE, MSA timing, multi-stream output, DSC, double-buffering, metadata, ALPM, and generic SDP fields for the fourth DP transmitter.

Important `DIG4` register families in this partial range mirror the early `DIG3` surface: `DIG4_DIG_FE_CNTL`, output CRC, test-pattern, FIFO, HDMI metadata/control/status, audio/ACR/VBI/infoframe packet controls, and generic packet controls through the first half of `DIG4_HDMI_GENERIC_PACKET_CONTROL5`.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time symbol resolution:

1. DCN 3.1.2 display code includes `dcn_3_1_2_sh_mask.h` together with the matching DCN 3.1.2 offset header.
2. AMD display register helper macros concatenate register and field tokens to resolve `__SHIFT` and `_MASK` constants.
3. Runtime MMIO paths use the resolved constants to insert, update, or extract hardware register fields.

The declaration order follows the generated hardware register order. The range starts inside `DP3_DP_DPHY_SYM0`, continues through the rest of the DP3 display transmitter fields covered by this generated address block, enters `dce_dc_dio_dig3_dispdec`, then `dce_dc_dio_dp4_dispdec`, then starts `dce_dc_dio_dig4_dispdec`. Within complete register groups, shift macros normally precede mask macros for the same fields.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes bit layout for state stored in DCN 3.1.2 display hardware:

- DisplayPort link and DPHY fields describe programmed training, scrambling, PRBS, CRC, 8b/10b, link-framing, timing, and diagnostic state.
- DisplayPort video, MSA, M/N, VBID, MSO, DSC, and ALPM fields describe stream format, stream timing, transport framing, compression, and low-power link behavior.
- Secondary-data-packet, audio N/M, generic SDP, and HDMI generic packet fields describe packet enablement, scheduling, immediate-send requests, pending status, line references, metadata transmission, and audio clock generation.
- HDMI/TMDS fields describe encoder mode, deep color, audio/infoframe/VBI packet scheduling, ACR values, TMDS control characters, sync patterns, and DC-balance behavior.
- CRC, FIFO, interrupt, status, pending, collision, phase-error, and readback fields describe hardware-observed state that can change asynchronously with link training, hotplug, stream enablement, packet transmission, and diagnostic operations.

Persistence is hardware-defined. Writable fields may remain programmed until driver reconfiguration, stream disable, display block reset, suspend/resume restore, or ASIC reset. Status and pending fields may be volatile, sticky, masked, or acknowledge-driven depending on the underlying register semantics; this generated shift/mask header does not encode access permissions, reset values, side effects, or write-one-to-clear rules.

## Dependencies And Integration Points

This chunk depends on generated DCN 3.1.2 register files staying synchronized:

- `dcn_3_1_2_offset.h` supplies the matching register offsets and base indices. Examples near this chunk include `regDP3_DP_DPHY_SYM0` at `0x2419`, `regDIG3_DIG_FE_CNTL` at `0x238b`, `regDP4_DP_LINK_CNTL` at `0x2508`, and `regDIG4_HDMI_GENERIC_PACKET_CONTROL5` at `0x249c`, all with base index `2`.
- AMD display register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT` rely on the exact generated suffix convention used here.
- DisplayPort link training, MST allocation, DSC, ALPM, audio packetization, HDMI packet scheduling, TMDS programming, diagnostics, interrupt handling, and power-management paths integrate with these constants when programming or reading the DCN display engines.
- The generated register database remains the source of truth for legal values, access modes, reset values, and sequencing constraints. This file only captures numeric bit positions and masks.

The main integration contract is preprocessor naming. Missing or renamed fields typically fail at compile time when helper macros expand, while wrong numeric masks or shifts can compile cleanly and produce incorrect MMIO reads or writes.

## Risks And Edge Cases

- The chunk starts and ends mid-register group. `DP3_DP_DPHY_SYM0` must be completed from the previous chunk, and `DIG4_HDMI_GENERIC_PACKET_CONTROL5` must be completed from the next chunk before whole-register conclusions are made.
- The `DP3` and `DP4` blocks are highly repetitive. A generated prefix, endpoint number, or field-width mismatch can be hard to notice because most lines differ only by transmitter instance.
- `DIG3` and early `DIG4` HDMI/TMDS fields are similarly repetitive. Confusing encoder instances can program the wrong output path while leaving the intended path unchanged.
- Full-width or high-bit masks such as `0xFFFFFFFFL`, `0xFF000000L`, `0xC0000000L`, and `0x80000000L` require unsigned-safe handling in consumers. Signed temporary values can corrupt comparisons or shifts.
- Control and status fields use the same macro style. The header cannot prevent callers from writing read-only status fields, missing required acknowledges, or treating pending/status bits as ordinary configuration.
- Packet send and immediate-send fields are side-effect prone. Incorrect writes can schedule HDMI generic packets, SDPs, infoframes, ISRC packets, or audio packets at the wrong time or on the wrong line.
- MST/MSE slot-allocation and rate fields are compact and instance-specific. Wrong masks can corrupt adjacent source/slot fields or create invalid bandwidth allocation.
- Link training, PRBS, scrambler, CRC, fast-training, and HBR2 pattern controls are diagnostic or sequencing-sensitive. Programming them outside the expected link-training flow can disrupt active streams.
- DSC, MSO, ALPM, and metadata fields interact with stream capabilities and sink/link state. A bitfield definition may be numerically correct but still unsafe to use without the proper higher-level capability checks.
- Cross-generation reuse is risky. DCN 3.1.2 layouts are close to neighboring DCN generations, but code must include the offset and shift/mask headers that match the target ASIC.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Build AMDGPU DCN 3.1.2 display code that includes this header to catch missing macro names in register-helper expansions.
- Preprocess representative users of `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE` for DP3, DP4, DIG3, and DIG4 fields to confirm the expected constants resolve.
- Compare this file with `dcn_3_1_2_offset.h` and the generated register database to ensure register offsets and field masks remain paired for each transmitter and digital encoder instance.
- Exercise DP link training and retraining on DCN 3.1.2 hardware, watching link status, DPHY training, scrambler, fast-training, CRC, and video interrupt fields for plausible transitions.
- Test MST configurations that use MSE rate and SAT programming, including multi-stream slot updates and SAT status readback.
- Exercise DSC, MSO, ALPM, and SDP metadata paths with capable sinks, checking that DP4 fields produce correct stream bring-up and that DB/status bits settle as expected.
- Validate HDMI/DIG3 output modes including deep color, audio, ACR, infoframes, VBI packets, generic packets, TMDS encoding, output CRC, and FIFO status.
- Validate DIG4 paths covered by this partial chunk in the same way, but defer full generic-packet-control conclusions until the next chunk completes `DIG4_HDMI_GENERIC_PACKET_CONTROL5`.
- Run suspend/resume, display reset, hotplug, and mode-set tests to ensure programmed DP, HDMI, packet, audio, and diagnostic state is restored or re-read correctly.

## Open Cross-Chunk Questions

- The merge lane should combine this with the previous chunk to complete the beginning of `DP3_DP_DPHY_SYM0`.
- The merge lane should combine this with the next chunk to complete `DIG4_HDMI_GENERIC_PACKET_CONTROL5` and the rest of the DIG4 HDMI/TMDS block.
- Whole-file analysis should verify all DP and DIG instance counts for DCN 3.1.2 and compare the repeated instance layouts against the authoritative generated register source.

### subset-b-001818: lines 39762-42177

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 39762-42177

## Chunk Scope

This chunk is a generated AMD DCN 3.1.2 ASIC register shift/mask header segment. It contains preprocessor constants only: `#define` pairs ending in `__SHIFT` and `_MASK` for bitfield extraction and register writes. There are no C functions, structs, enums, or executable control paths in the range. The behavioral content is the hardware contract encoded by the bit positions, masks, repeated display-engine instances, and address-block comments.

The chunk covers 2,162 macro definitions across these register families:

- `DIG4_*`: HDMI, TMDS, digital backend, and AFMT clock/control fields for digital link instance 4.
- `AFMT0_*` through `AFMT4_*`: repeated audio formatter packet, infoframe, CRC, test-ramp, status, source-select, and memory-power bitfields for five DIG/AFMT display pipes.
- `DME0_*` through `DME4_*`: repeated display metadata engine control and memory-power bitfields.
- `VPG0_*` through `VPG4_*`: repeated video packet generator generic-packet RAM access, frame/immediate update, status, memory-power, ISRC, and MPEG infoframe bitfields.
- `DP_AUX0_*`: DisplayPort AUX channel control, software/light-sleep status, data FIFO access, DPHY timing/status, and GTC synchronization bitfields.

## Purpose

The header supplies the mask and shift constants consumed by AMDGPU Display Core register-access macros. Driver code can compose read-modify-write operations by naming fields such as `DIG4_HDMI_DB_CONTROL__HDMI_DB_PENDING_MASK` and `DIG4_HDMI_DB_CONTROL__HDMI_DB_PENDING__SHIFT` instead of hard-coding numeric bit positions. This matters because the surrounding display driver programs hardware blocks directly and needs the generated register schema to match the DCN 3.1.2 register specification exactly.

Within this chunk, the constants describe HDMI/AFMT/audio packet programming for one digital output (`DIG4`) plus replicated AFMT, DME, and VPG blocks for display pipes 0 through 4. The final section describes DP AUX instance 0, including arbitration, interrupt, transfer status, PHY timing, and GTC sync control/status.

## Important Macro Groups

### DIG4 HDMI, TMDS, and Backend Fields

The chunk begins mid-register with `DIG4_HDMI_GENERIC_PACKET_CONTROL5` immediate-send and pending masks for generic packets 9 through 14. It then defines:

- `DIG4_HDMI_GC`: AVMUTE, continuous AVMUTE, default phase, packing phase, and packing override fields.
- `DIG4_HDMI_GENERIC_PACKET_CONTROL1` through `CONTROL4`, `CONTROL7` through `CONTROL10`: generic packet line scheduling fields for packet slots 0 through 14, plus per-slot double-buffer pending flags in `CONTROL10`.
- `DIG4_HDMI_DB_CONTROL`: HDMI and vupdate double-buffer pending/taken/clear/lock/disable fields.
- `DIG4_HDMI_ACR_*` and `DIG4_HDMI_ACR_STATUS_*`: audio clock regeneration CTS/N fields for 32, 44.1, and 48 kHz base rates and current status.
- `DIG4_AFMT_CNTL`: audio formatter clock enable/on status.
- `DIG4_DIG_BE_CNTL` and `DIG4_DIG_BE_EN_CNTL`: digital backend dual-link, swap, red/blue switch, front-end source select, link mode, HPD select, enable, and symbol clock status.
- TMDS fields: sync phase, control-character enables, feedback selection/delay, stereo sync select, sync character patterns, control bits, DC-balancer behavior, control generator parameters for CTL0/1 and CTL2/3, digital version, and forced disable.

These definitions are integration points for HDMI bring-up, audio infoframe scheduling, link enable/disable sequencing, and TMDS compliance/test programming.

### AFMT0-AFMT4 Audio Formatter Fields

Each AFMT instance has the same visible field layout. The repeated per-instance blocks include:

- `AFMT*_AFMT_VBI_PACKET_CONTROL`: HDMI audio packets per line and max-send control.
- `AFMT*_AFMT_AUDIO_PACKET_CONTROL2`: layout override/select, channel enable bitmap, DP audio stream ID, HBR override, and IEC 60958 OSF override.
- `AFMT*_AFMT_AUDIO_INFO0` and `AUDIO_INFO1`: HDMI audio infoframe checksum, channel count, coding type, checksum offset, extension coding type, channel allocation, level shift, downmix inhibit, and LFE playback-level fields.
- `AFMT*_AFMT_60958_0`, `_1`, and `_2`: channel-status fields including category code, source number, left/right channel numbers, sampling frequency, clock accuracy, word length, original sampling frequency, validity bits, and channel numbers for channels 2 through 7.
- `AFMT*_AFMT_AUDIO_CRC_CONTROL` and `AUDIO_CRC_RESULT`: audio CRC enable/continuous/source/channel/count, done status, and result data.
- `AFMT*_AFMT_RAMP_CONTROL0` through `RAMP_CONTROL3`: audio test ramp max/min/inc/dec counts, sign, and test-channel disable bitmap.
- `AFMT*_AFMT_STATUS`: audio enable, HBR enable, FIFO overflow, and AZ audio-enable change indication.
- `AFMT*_AFMT_AUDIO_PACKET_CONTROL`: sample-send, double-buffer enable, FIFO reset on disable, audio test mode, overflow ack, channel swap, 60958 channel-status update, and AZ change ack.
- `AFMT*_AFMT_INFOFRAME_CONTROL0`, `AUDIO_SRC_CONTROL`, and `MEM_PWR`: audio info source/update, source selection, and formatter memory power gating fields.

The `AFMT*_AFMT_INTERRUPT_STATUS` comments have no field defines in this chunk, which likely means that either the register has no named fields in this generated revision or its fields are defined outside the selected line range.

### DME0-DME4 Metadata Engine Fields

Each DME block defines:

- `DME*_DME_CONTROL`: metadata HUBP requestor ID, engine enable, stream type, double-buffer pending/taken/clear/disable, transmission missed, and missed-clear fields.
- `DME*_DME_MEMORY_CONTROL`: DME memory power force, disable, state, and default low-power state.

These fields support per-pipe metadata transmission. The double-buffer and missed-transmission flags are stateful hardware handshake bits and are likely read or cleared by display metadata programming paths.

### VPG0-VPG4 Video Packet Generator Fields

Each VPG block defines:

- `VPG*_VPG_GENERIC_PACKET_ACCESS_CTRL` and `GENERIC_PACKET_DATA`: indexed access to generic packet bytes, four bytes per data register access.
- `VPG*_VPG_GSP_FRAME_UPDATE_CTRL`: frame-update request and pending fields for generic packet slots 0 through 14.
- `VPG*_VPG_GSP_IMMEDIATE_UPDATE_CTRL`: immediate-update request and pending fields for generic packet slots 0 through 14.
- `VPG*_VPG_GENERIC_STATUS`: lock status, conflict occurrence, and conflict clear.
- `VPG*_VPG_MEM_PWR`: generic-stream-packet memory light-sleep disable, light-sleep force, and power-state reporting.
- `VPG*_VPG_ISRC1_2_ACCESS_CTRL` and `ISRC1_2_DATA`: indexed ISRC packet byte access.
- `VPG*_VPG_MPEG_INFO0` and `MPEG_INFO1`: MPEG infoframe checksum, payload bytes, frame flags, and update trigger.

The VPG fields are the packet RAM and packet-update counterpart to the HDMI generic packet controls in the DIG block. Driver sequencing must coordinate packet data writes, frame/immediate update triggers, and pending/status polling.

### DP_AUX0 Fields

The DP AUX block contains:

- `DP_AUX0_AUX_CONTROL`: AUX enable/reset/reset-done, light-sleep read/update disable, HPD-disconnect ignore, mode-detect enable, HPD select, impedance calibration request enable, test mode, deglitch enable, and spare bits.
- `DP_AUX0_AUX_SW_CONTROL`: software transaction go, light-sleep read trigger, start delay, and write-byte count.
- `DP_AUX0_AUX_ARB_CONTROL`: AUX register arbitration priority, register read/write control status, no-queued SW/LS go controls, and ownership request/done bits for software and DMCU. Some request and pending request names intentionally alias the same bit/mask.
- `DP_AUX0_AUX_INTERRUPT_CONTROL`: interrupt, ack, and mask fields for software-done, light-sleep-done, GTC sync lock done, and GTC sync error.
- `DP_AUX0_AUX_SW_STATUS` and `AUX_LS_STATUS`: done/request flags, receive timeout state, timeout, overflow, HPD disconnect, partial byte, non-AUX mode, min-count violation, invalid stop/start/sync, receive detect errors, reply byte count, AUX arbitration status, CP IRQ, light-sleep update, and update ack.
- `DP_AUX0_AUX_SW_DATA` and `AUX_LS_DATA`: indexed byte access to AUX software and light-sleep data buffers, including software read/write and autoincrement-disable fields.
- `DP_AUX0_AUX_DPHY_*`: TX reference/rate/divider, TX precharge and output-enable timing, RX window/filter/threshold/timeout controls, and TX/RX status including state and half-symbol period measurements.
- `DP_AUX0_AUX_GTC_SYNC_*`: GTC sync enable, impedance calibration, lock acquisition/maintenance timing, block request, interval reset window, retry counts, potential/definite error thresholds, lock acquisition timeout, retry for lock maintenance, and controller status fields through lock acquisition timeout state at the end of the chunk.

This is a high-risk control surface because AUX is used for DisplayPort DPCD/I2C-over-AUX communication and link management. Bitfield drift here can break monitor detection, link training, HDCP/CP IRQ handling, or AUX timeout/error recovery.

## APIs, Types, and Functions

There are no declared APIs, types, or functions. The exported interface is the macro namespace itself. Each register field normally appears as:

- `<REGISTER>__<FIELD>__SHIFT`: the right shift to normalize the bitfield value.
- `<REGISTER>__<FIELD>_MASK`: the raw register mask used to preserve or update the field.

Consumers are expected to use the macros with DC register helpers such as generated register lists, `REG_SET`, `REG_UPDATE`, `REG_GET`, or equivalent AMDGPU/DC bitfield utilities defined elsewhere. This chunk does not include the register offsets; it only supplies masks/shifts for already named register symbols.

## Control Flow and State Behavior

The header itself has no runtime control flow. The implied control flow comes from hardware handshakes:

- Generic HDMI/VPG packet update paths write packet payload/index data, trigger frame or immediate update bits, then observe corresponding pending/status bits.
- HDMI/metadata double-buffer paths use pending/taken/clear/disable fields to synchronize register updates with frame/vupdate boundaries.
- AFMT audio programming writes infoframe/channel-status/sample-send fields, may trigger 60958 updates, and must acknowledge FIFO overflow or AZ audio-enable changes via ack bits.
- DME metadata transmission uses engine enable, stream type, double-buffer state, and missed-transmission clear fields.
- DP AUX software transactions acquire AUX register ownership as needed, write buffer/index/byte count fields, set go, poll or handle done/error status, then acknowledge interrupts and release ownership.
- AUX GTC sync programming configures acquisition and maintenance windows, then reads controller status for lock complete, lock lost, or timeout.

State is entirely hardware-resident. The macros identify persistent and transient register fields, including power-state fields (`*_MEM_PWR_STATE`, `AUX_RESET_DONE`), pending/taken handshakes, interrupt ack/mask fields, and error clear/ack bits. Incorrect masks can cause stale pending bits, missed clear writes, or unintended modification of adjacent hardware state.

## Dependencies and Integration Points

This generated header depends on the DCN 3.1.2 ASIC register database and on the surrounding AMDGPU display driver conventions for bitfield naming. Integration points include:

- DCN register definition headers that provide register offsets for the same symbols.
- Display Core link encoder and stream encoder code that configures DIG/HDMI/TMDS fields.
- Audio formatter code that writes AFMT infoframe, channel-status, HBR, sample-send, source-select, and CRC/test fields.
- VPG packet-generation code for generic packets, ISRC packets, and MPEG infoframes.
- Metadata engine code that enables DME and coordinates HUBP requestor IDs and double-buffered metadata updates.
- DP AUX/I2C-over-AUX code, link training, HPD handling, CP IRQ handling, and DMCU/software AUX arbitration paths.
- Power-management code that observes or programs AFMT, DME, VPG, and AUX memory/light-sleep controls.

Because the file is an include under `drivers/gpu/drm/amd/include/asic_reg/dcn`, it is generally not edited by hand. Manual changes risk divergence from other generated register headers such as offset, default, or SOC-specific variants.

## Risks and Edge Cases

- This chunk starts in the middle of `DIG4_HDMI_GENERIC_PACKET_CONTROL5`; earlier shift definitions and packet 0-8 fields are outside this range. Merge reconciliation should combine adjacent chunks before making whole-file conclusions.
- Repeated AFMT/DME/VPG blocks must remain instance-consistent. A copy-generation error in one instance can silently affect only one display pipe.
- Several control surfaces use write-one-to-clear or ack-style semantics (`*_TAKEN_CLR`, `*_MISSED_CLR`, `*_ACK`, conflict clear). Incorrect masks can clear the wrong status or fail to clear an interrupt.
- Double-buffer and pending bits are timing-sensitive. Misprogramming HDMI generic packet, VPG frame/immediate update, DME metadata, or AFMT sample-send update fields can produce stale packets, dropped metadata, or visible/audio glitches.
- DP AUX arbitration fields include aliases where request and pending request share a shift/mask. Consumers must understand whether they are writing a request or reading pending state even though the bit position is identical.
- DP AUX DPHY timing fields are protocol-sensitive. Wrong masks or shifts can manifest as intermittent AUX timeouts, invalid starts/stops, partial bytes, or failed monitor detection rather than compile failures.
- Power-state fields are often read-only or hardware-controlled; treating them as writable in consumers would be a driver bug even though this header only exposes masks.
- The `SPARE_0` and `SPARE_1` fields in `DP_AUX0_AUX_CONTROL` should not be repurposed without hardware documentation.

## Test and Validation Signals

Useful validation for this chunk is mostly integration and hardware-oriented:

- Build coverage: compile AMDGPU/DC code with DCN 3.1.2 enabled to ensure all macro names match consumer references.
- Header consistency: compare generated mask/shift pairs against the authoritative DCN 3.1.2 register database and related offset/default headers.
- HDMI validation: exercise DIG4 HDMI output with audio, generic infoframes, AVMUTE, TMDS control symbols, and mode changes while checking for packet/update pending completion.
- Audio validation: test AFMT instances 0-4 for LPCM channel layouts, HBR modes, 60958 channel-status updates, FIFO overflow handling, audio CRC/test ramp, and hotplug audio-enable changes.
- Metadata/VPG validation: verify metadata and generic packet delivery across display pipes 0-4, including frame-update and immediate-update paths and conflict status handling.
- DP AUX validation: run monitor detection, DPCD reads/writes, I2C-over-AUX EDID reads, HPD disconnect handling, CP IRQ handling, software/DMCU arbitration, timeout/error paths, and GTC sync lock/loss behavior on AUX0.
- Power validation: suspend/resume, display idle, and hotplug scenarios should not leave AFMT/DME/VPG/AUX memory-power state or light-sleep fields in bad states.

## Open Questions for Merge Lane

- The chunk ends inside `DP_AUX0_AUX_GTC_SYNC_CONTROLLER_STATUS`; subsequent status masks and any following AUX blocks must be checked in the next chunk.
- Whole-file synthesis should verify how many DIG/AFMT/DME/VPG/AUX instances DCN 3.1.2 exposes and whether instances beyond 4 or AUX channels beyond 0 are defined in adjacent chunks.
- The merge lane should cross-check whether `AFMT*_AFMT_INTERRUPT_STATUS` intentionally has no bitfield definitions or whether the fields reside outside this chunk.

### subset-b-001819: lines 42178-44529

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 42178-44529

## Scope

This chunk is part of the generated DCN 3.1.2 ASIC register field header. It defines C preprocessor `__SHIFT` and `_MASK` constants for a contiguous set of Display Core register blocks:

- The tail of `DP_AUX0` GTC sync status and AUX PHY wake fields.
- Full `DP_AUX1` through `DP_AUX4` DisplayPort AUX channel field maps.
- The display DDC I2C controller block.
- DIO miscellaneous scratch, power, clock, reset, interrupt, and link-control fields.
- `DC_PERFMON18` performance monitor fields.
- The start of the DCIO/UNIPHY block, through `UNIPHYB_CHANNEL_XBAR_CNTL`.

The file is data, not executable logic. Its purpose is to let AMDGPU display code refer to hardware bitfields symbolically through the register access macros used throughout `drivers/gpu/drm/amd/display`.

## Purpose And Structure

Each hardware register field has two generated constants:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for the field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.

The source is arranged by hardware address block comments. In this chunk those comments identify `dce_dc_dio_dp_aux1_dispdec`, `dce_dc_dio_dp_aux2_dispdec`, `dce_dc_dio_dp_aux3_dispdec`, `dce_dc_dio_dp_aux4_dispdec`, `dce_dc_dio_dout_i2c_dispdec`, `dce_dc_dio_dio_misc_dispdec`, `dce_dc_dio_dio_dcperfmon_dc_perfmon_dispdec`, and `dce_dc_dcio_dcio_dispdec`. Address definitions live separately in `dcn_3_1_2_offset.h`, for example the matching AUX register offsets at `regDP_AUX1_AUX_CONTROL` through `regDP_AUX4_AUX_PHY_WAKE_CNTL`, `regDC_I2C_*`, `regDC_PERFMON18_*`, and `regUNIPHYA_*`.

## Important Register Families

The `DP_AUX1` through `DP_AUX4` sections repeat the same field layout for four AUX engines:

- `AUX_CONTROL` enables and resets an AUX channel, gates low-speed reads, selects HPD routing, controls impedance calibration, test mode, and deglitching.
- `AUX_SW_CONTROL` starts software AUX transactions and encodes software write byte count and start delay.
- `AUX_ARB_CONTROL` arbitrates ownership of the AUX registers between software and DMCU paths using request, pending, done, and queued-operation bits.
- `AUX_INTERRUPT_CONTROL` exposes SW done, LS done, GTC lock done, and GTC error interrupt status, ack, and mask bits.
- `AUX_SW_STATUS` and `AUX_LS_STATUS` expose transaction done/request state, receive timeout, overflow, HPD disconnect, invalid framing/sync/start/stop, receive detection failures, reply byte count, link-service CP IRQ, and update-ack bits.
- `AUX_SW_DATA` and `AUX_LS_DATA` map the indexed byte data windows used to read and write AUX payloads.
- `AUX_DPHY_TX_REF_CONTROL`, `AUX_DPHY_TX_CONTROL`, `AUX_DPHY_RX_CONTROL0`, and `AUX_DPHY_RX_CONTROL1` define AUX PHY timing, reference divider/rate, precharge, receive window, phase detect, threshold, and timeout fields.
- `AUX_DPHY_TX_STATUS` and `AUX_DPHY_RX_STATUS` expose PHY state and measured half-symbol periods.
- `AUX_GTC_SYNC_CONTROL`, `AUX_GTC_SYNC_ERROR_CONTROL`, `AUX_GTC_SYNC_CONTROLLER_STATUS`, and `AUX_GTC_SYNC_STATUS` define DisplayPort global timecode synchronization enable, retry, threshold, lock, error, ack, and AUX-reply status fields.
- `AUX_PHY_WAKE_CNTL` exposes wake request, pending, priority, and acknowledge bits.

The `DC_I2C_*` block defines the display DDC I2C hardware controller:

- `DC_I2C_CONTROL` starts transfers, performs soft/send/status resets, selects the target DDC engine, and encodes transaction count.
- `DC_I2C_ARBITRATION` mirrors the AUX ownership pattern for software and DMCU users and adds abort controls for hardware and software transfers.
- `DC_I2C_INTERRUPT_CONTROL` exposes SW done and per-DDC hardware done interrupt, ack, and mask bits for DDC1-DDC6 and DDCVGA.
- `DC_I2C_SW_STATUS` and `DC_I2C_DDC*_HW_STATUS` report active, done, aborted, timeout, interrupted, stopped-on-NACK, stopped-on-timeout, stopped-on-overflow, and index state.
- `DC_I2C_DDC*_SPEED` and `DC_I2C_DDC*_SETUP` configure threshold, prescale, enable, EDID-detect, setup delay, and receive-hold timing per DDC engine.
- `DC_I2C_TRANSACTION0` through `DC_I2C_TRANSACTION3` describe transaction stop/start/rw/count/address fields; `DC_I2C_DATA` is the indexed data FIFO/window.
- `DC_I2C_EDID_DETECT_CTRL` and `DC_I2C_READ_REQUEST_INTERRUPT` support EDID detection and read-request interrupt masking/status/ack handling.

The DIO miscellaneous block contains scratch registers `DIO_SCRATCH0` through `DIO_SCRATCH7`, display IO memory power status/control, DIO clock controls, power-management force bits, digital soft resets, HDMI RX status timer control, generic interrupt message/clear fields, and per-link enable controls for links A-F. These fields are mostly low-level display hardware control and diagnostic surfaces.

`DC_PERFMON18` defines an eight-counter performance monitor instance. Its fields select events, counted value type, off/interrupt thresholds, hardware stop sources, count-off selection, state selectors for counters 0-7, perfmon run state, report count, clock enable, run-enable start/stop selections, interrupt status/ack bits per counter, and high/low current/readback values.

The DCIO/UNIPHY start defines generic clock/debug output selectors (`DC_GENERICA`, `DC_GENERICB`, `DCIO_CLOCK_CNTL`, `DC_REF_CLK_CNTL`) and physical link wiring controls (`UNIPHYA_LINK_CNTL`, `UNIPHYA_CHANNEL_XBAR_CNTL`, `UNIPHYB_LINK_CNTL`, `UNIPHYB_CHANNEL_XBAR_CNTL`). UNIPHY link fields control per-lane inversion, power sequence selection, and channel crossbar source selection.

## Important APIs, Types, And Consumers

There are no functions or C types in this chunk. The important API surface is the naming contract consumed by display register helper macros:

- `AUX_SF(...)` in `display/dc/dce/dce_aux.h` expects `AUX_SW_STATUS`, `AUX_SW_REPLY_BYTE_COUNT`, `AUX_SW_DONE`, and related mask/shift symbols. `display/dc/dce/dce_aux.c` reads these fields to wait for AUX completion and classify HPD disconnect, timeout, invalid stop, no-detect, and invalid-receive errors.
- `I2C_SF(...)` and `SR(...)` in `display/dc/dce/dce_i2c_hw.h` expect `DC_I2C_CONTROL`, `DC_I2C_SW_STATUS`, and related fields. `display/dc/dce/dce_i2c_hw.c` uses the status-reset, done, aborted, timeout, stopped-on-NACK, and status fields to drive DDC transactions.
- Link encoder field tables in `display/dc/dio/dcn10/dcn10_link_encoder.h`, `display/dc/dio/dcn20/dcn20_link_encoder.h`, and `display/dc/dcn21/dcn21_link_encoder.h` consume `UNIPHYA_CHANNEL_XBAR_CNTL` and channel source masks/shifts for lane routing. Later blocks in this header define the equivalent UNIPHY instances.
- `display/dc/resource/dcn31/dcn31_resource.c`, `display/dc/irq/dcn31/irq_service_dcn31.c`, and `display/dmub/src/dmub_dcn31.c` include `dcn_3_1_2_sh_mask.h`, binding these field definitions to DCN 3.1.2 resource construction, interrupt setup, and DMUB register access.

The chunk depends on matching `reg*` address constants from `dcn_3_1_2_offset.h` and on register access macros such as `REG_GET`, `REG_READ`, `REG_UPDATE`, and `REG_WAIT` supplied by the AMD display register framework. A mismatch between offset and mask headers would compile but read or write wrong hardware bits.

## Control Flow And State Behavior

This header has no runtime control flow. Runtime behavior emerges when display code uses these masks in read-modify-write and polling sequences:

- AUX software transactions write payload bytes through `AUX_SW_DATA`, program `AUX_SW_CONTROL`, assert `AUX_SW_GO`, then poll or interrupt on `AUX_SW_STATUS.AUX_SW_DONE`. The reply byte count and error bits determine transaction result and retry behavior.
- AUX low-speed and GTC sync paths use parallel status and interrupt fields. Ack bits in `AUX_INTERRUPT_CONTROL` and `AUX_GTC_SYNC_CONTROLLER_STATUS` clear latched hardware events.
- I2C DDC transactions program one or more `DC_I2C_TRANSACTION*` descriptors plus `DC_I2C_DATA`, select a DDC engine and count in `DC_I2C_CONTROL`, assert `DC_I2C_GO`, then poll `DC_I2C_SW_STATUS` or per-DDC hardware status. Status reset bits clear persistent software status between transactions.
- DIO clock, power, reset, and link-control fields persist in MMIO hardware state until changed by the driver, firmware, reset, or power transition. Scratch registers are explicit persistence/diagnostic storage in the display IO block.
- Perfmon fields select events and run/stop conditions, then hardware accumulates counter state until stopped, reset, or reprogrammed. Interrupt status/ack fields are sticky event surfaces.

## Dependencies And Integration Points

The values in this chunk must match the DCN 3.1.2 register specification and the sibling offset header. They are integrated through generated register lists and field lists rather than direct hand-written constants. The driver code generally does not include per-channel `DP_AUX1_...` names directly; it builds per-instance register structures with macros such as `SRI`, `SRI_ARR`, and `AUX_SF`, then uses common AUX/I2C/link encoder logic against those structures.

The AUX and I2C fields are visible at the DRM/KMS level through monitor detection, EDID reads, DisplayPort link training, DPCD access, MST sideband operations, HDCP/CP IRQ service, and HPD handling. UNIPHY fields affect physical lane mapping and inversion, so they integrate with BIOS link encoder descriptors and board-specific connector routing.

## Risks

- Generated mask or shift errors are high impact: they can silently drive the wrong bit in MMIO, causing display detection failures, failed AUX/I2C transactions, interrupt storms, bad lane routing, or link training failure.
- AUX status fields mix transient status, error classification, reply counts, and ack bits. Using a mask from a different AUX instance or ASIC revision can make timeout/HPD-disconnect handling unreliable.
- I2C arbitration and reset fields are shared between software and DMCU/firmware paths. Incorrect ownership or abort bits can leave the DDC engine busy or corrupt EDID reads.
- Link inversion and crossbar fields are board-routing sensitive. A wrong channel source or inversion bit can produce no display or unstable high-speed links even when higher-level mode programming is correct.
- Perfmon and scratch fields are diagnostic/control surfaces; they are less likely to affect normal display bring-up, but stale sticky status or wrong ack masks can hide performance counter interrupts.
- Because this is a generated header, manual edits are likely to be overwritten or diverge from hardware source data. Changes should come from the register generation source, not local hand patches.

## Test Signals

Good validation signals for this chunk are mostly integration and hardware-facing:

- Kernel build coverage for DCN 3.1.2 paths, including `dcn31_resource`, IRQ service, DMUB, AUX, I2C, and link encoder compilation.
- EDID read success on all physical DDC/AUX-routed connectors, including repeated hotplug cycles and suspend/resume.
- DisplayPort DPCD and AUX transactions with normal replies, timeouts, HPD disconnect, and NACK/error cases, checking that `AUX_SW_STATUS` error classification matches expected behavior.
- I2C DDC transactions across DDC1-DDC5/DDC6/VGA where present, confirming done, timeout, NACK, and abort statuses are decoded correctly and status reset clears the next transaction.
- DisplayPort link training on connectors using UNIPHY A/B lane routing, including lane reversal or inversion cases indicated by board BIOS.
- Interrupt tests for AUX/I2C done and GTC sync error/lock events, verifying ack and mask fields clear only the intended status bits.
- Optional debug/performance validation that `DC_PERFMON18` counters can be configured, run, stopped, read, and acknowledged without spurious interrupts.

### subset-b-001820: lines 44530-47039

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 44530-47039

## Scope

This chunk covers a generated DCN 3.1.2 shift/mask header slice for AMD display hardware registers. It contains only C preprocessor constants and generated grouping comments; there are no local functions, structs, enums, storage objects, or executable statements.

The slice starts in the tail of `UNIPHYB_CHANNEL_XBAR_CNTL`, covers DCIO link/GPIO controls, UNIPHY reserved macro-control fields, panel power sequencer instances 0 and 1, DSC compressor instance 0, DSC interface/top controls, and ends partway through `DC_PERFMON19_PERFCOUNTER_CNTL2`. Because both ends are partial register families, the final per-file reconciliation should merge this chunk with neighboring chunks before making whole-file claims.

## Purpose

This header is part of the generated hardware ABI used by AMDGPU Display Core for DCN 3.1.2 ASICs. Each macro gives either a field bit offset (`__SHIFT`) or bit mask (`_MASK`) for a named MMIO register field. Driver code normally reaches these constants through register table builders and helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `SF`, `SRI`, `SRIR`, GPIO field lists, panel-control field lists, DSC field lists, and perfmon tables.

At a hardware level, this chunk describes:

- UNIPHY link lane inversion, power-sequencer selection, and channel crossbar routing for UNIPHY B through E.
- DCIO-level write-command delay, pin strap, intercept, genlock/swaplock pad, frame-start selection, and soft-reset fields.
- Display GPIO pin programming for generic pins, DDC/I2C/AUX pads, HPD pins, genlock pins, power-sequence pins, TX/RX enables, pullups, pad strength, AUX control, and AUX/I2C pad power-good status.
- Reserved UNIPHY macro-control register fields for UNIPHY instances 1 through 4.
- PWRSEQ0 and PWRSEQ1 panel GPIO, panel digital/backlight power sequencing, delay/reference divider, PWM, grouped register lock, and spare fields.
- DSCC0 Display Stream Compression compressor configuration, picture parameter set programming, interrupt/status bits, memory power control, quality/error metrics, buffer fullness readbacks, and debug bus selection.
- DSCCIF0 input-interface format/underflow/update-pending fields and DSC_TOP0 clock/debug controls.
- The beginning of DC perfmon instance 19 counter control fields.

The main value is symbolic correctness. Consumers can request fields such as `DC_GPIO_DDC1_MASK__AUX_PAD1_MODE_MASK`, `PWRSEQ0_BL_PWM_CNTL__BL_PWM_EN_MASK`, or `DSCC0_DSCC_PPS_CONFIG16__RANGE_BPG_OFFSET2_MASK` without embedding fragile numeric bit layouts in runtime code.

## Important APIs, Types, And Constants

There are no callable APIs or local types. The exported interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: numeric bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: mask for the same field.
- Register comments such as `//DSCC0_DSCC_PPS_CONFIG1` and address-block comments such as `// addressBlock: dce_dc_pwrseq0_dispdec_pwrseq_dispdec` preserve generated register grouping.

Important macro families in this chunk are:

- `UNIPHYC_LINK_CNTL`, `UNIPHYD_LINK_CNTL`, `UNIPHYE_LINK_CNTL`, and corresponding `*_CHANNEL_XBAR_CNTL` families: per-channel invert bits, link-to-power-sequencer selection, and 2-bit channel source selectors. The first six lines complete the preceding `UNIPHYB_CHANNEL_XBAR_CNTL` family.
- `DCIO_WRCMD_DELAY`, `DC_PINSTRAPS`, `INTERCEPT_STATE`, `DCIO_BL_PWM_FRAME_START_DISP_SEL`, `DCIO_GSL_GENLK_PAD_CNTL`, `DCIO_GSL_SWAPLOCK_PAD_CNTL`, and `DCIO_SOFT_RESET`: top-level DCIO timing, strap, power/intercept state, genlock/swaplock routing, and reset masks for UNIPHY/DSYNC/PWRSEQ blocks.
- `DC_GPIO_GENERIC_*`, `DC_GPIO_DDC1_*` through `DC_GPIO_DDC5_*`, `DC_GPIO_DDCVGA_*`, `DC_GPIO_GENLK_*`, and `DC_GPIO_HPD_*`: GPIO mask, output enable, output value, and input/readback fields. DDC masks also include AUX pad mode, AUX polarity, hardware pull-down enable allowance, and clock/data drive strength. HPD masks include per-pin mask/pull-down/receive fields, RX select fields, and HPD pad strength.
- `DC_GPIO_PWRSEQ0_EN`, `DC_GPIO_PWRSEQ1_EN`, `DC_GPIO_TX12_EN`, `DC_GPIO_RXEN`, `DC_GPIO_PULLUPEN`, `PHY_AUX_CNTL`, `DC_GPIO_AUX_CTRL_0` through `DC_GPIO_AUX_CTRL_5`, and `AUXI2C_PAD_ALL_PWR_OK`: pad enables, RX enable/power-down behavior, pullup controls, AUX pad receiver selection, AUX I/O enable, I2C-mode controls, pad polarity, pull-down selection, detect selection, and power-good status.
- `DCIO_UNIPHY<n>_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57` for UNIPHY instances 1-4: reserved full-width or subfield masks, mostly one data field per register, used to preserve the generated register map even where public driver code may not name individual semantics.
- `PWRSEQ0_*` and `PWRSEQ1_*`: per-instance panel power sequencer fields for GPIO enable/control/mask/readback, panel `BLON`/`DIGON`/`SYNCEN` control and polarity, target-state request and readback, delay programming, PWM reference dividers, PWM period and active count, PWM fractional/override enable, grouped register lock/update-pending bits, and spare fields.
- `DSCC0_DSCC_CONFIG0`, `DSCC0_DSCC_CONFIG1`, `DSCC0_DSCC_STATUS`, and `DSCC0_DSCC_INTERRUPT_CONTROL_STATUS`: DSC slice/topology controls, rate-control buffer model size, double-buffer update-pending bit, and interrupt enable/status/clear fields for rate-control buffer model, output buffer overflow/underflow, and end-of-frame-not-reached conditions.
- `DSCC0_DSCC_PPS_CONFIG0` through `DSCC0_DSCC_PPS_CONFIG22`: DSC picture parameter set fields including DSC version, PPS identifier, line buffer depth, bits per component/pixel, VBR/simple/native modes, RGB conversion, block prediction, chunk size, picture/slice dimensions, initial delays, scale intervals, BPG offsets, initial/final offsets, flatness QP limits, RC model size, RC edge factor, quant increment limits, target offsets, RC buffer thresholds, and range min/max QP plus BPG offsets 0-14.
- `DSCC0_DSCC_MEM_POWER_CONTROL`, error/readback, fullness, and debug fields: DSC memory low-power control/state, squared-error lower/upper words per component, max absolute error, rate-buffer and rate-control-buffer max fullness levels, and debug bus rotate selectors.
- `DSCCIF0_DSCCIF_CONFIG0/1`: input-interface underflow recovery/interrupt/status, input pixel format, bits per component, double-buffer update pending, and picture size fields.
- `DSC_TOP0_DSC_TOP_CONTROL` and `DSC_TOP0_DSC_DEBUG_CONTROL`: DSC clock enable, display/DSC clock gate disable bits, debug enable, and test clock mux selection. `DSC_TOP0_DSC_DEBUG_CONTROL` appears twice with identical field definitions in this slice.
- `DC_PERFMON19_PERFCOUNTER_CNTL` and the start of `DC_PERFMON19_PERFCOUNTER_CNTL2`: event selection, counted-value source selection, increment mode, hardware control, run-enable mode, counter-off start disable, restart, interrupt enable, active status, counter selector, counted value type, hardware stop selections, and counter-off selector fields.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time macro expansion:

1. DCN 3.1.2-specific resource, IRQ, DMUB, GPIO, panel, DSC, or diagnostic code includes this header with the matching offset header.
2. Register table macros concatenate register and field names into `*_MASK` and `*__SHIFT` constants.
3. Runtime helpers use those generated table entries to compose MMIO writes, read/modify/write selected fields, poll status bits, decode readback fields, and acknowledge hardware events.
4. Actual sequencing lives in other display code. This header supplies the bit layout required by those sequences, including AUX/DDC pin setup, HPD/GPIO translation, panel/backlight sequencing, DSC PPS programming, DSC clock gating, update-pending polling, and perf counter setup.

The order in the file is generated and hardware-block oriented. Most register comments are followed by all `__SHIFT` definitions and then all matching `_MASK` definitions. Repeated instances are ordered numerically, such as DDC1-DDC5, UNIPHY1-UNIPHY4 reserved registers, PWRSEQ0/PWRSEQ1, and DSC PPS registers 0-22.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes hardware state held in DCN display registers:

- DCIO and UNIPHY state covers lane inversion, crossbar source selection, soft reset, strap readback, write-command delay, genlock/swaplock pad routing, intercept state, and PWM frame-start display selection.
- GPIO state covers pin masks, pull-down/pullup enables, output enables, output values, receive/readback bits, drive strength, AUX/DDC mode selection, polarity, RX enable, detect selection, and AUX/I2C pad power-good readback.
- PWRSEQ state covers panel target/current state, backlight and digital power outputs, sequencing delays, PWM period/duty/fractional controls, reference dividers, grouped register lock/update-pending status, and spare state.
- DSCC/DSCCIF/DSC_TOP state covers DSC clocking, compressor topology and PPS parameters, underflow recovery/status, double-buffered update pending, interrupt enables/status/clear bits, DSC memory power state, quality metrics, buffer fullness levels, debug selection, and input picture format/dimensions.
- DC perfmon19 state covers event selection, counting mode, interrupt enable/status-related control, counter active status, and hardware stop/counter-off routing for the selected counter.

Persistence is hardware-defined. Programmed fields generally remain until changed by another MMIO write, panel/display block reset, power transition, or full ASIC reset. Status and readback fields can change asynchronously with HPD/AUX activity, I2C/DDC transactions, panel sequencing, backlight updates, DSC frame processing, DSC interrupt events, memory power management, or perf counter activity. This header does not encode read-only, write-one-to-clear, volatile, lock, or delay semantics; callers must follow the block-specific programming model.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.1.2 register model staying synchronized across companion files and consumers:

- `dcn_3_1_2_offset.h` supplies the register offsets paired with these shift/mask definitions.
- DCN 3.1 include sites in this tree include this header from `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, `drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c`, and `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`.
- GPIO register helpers use these names through `dc/gpio/ddc_regs.h`, `dc/gpio/hpd_regs.h`, `dc/gpio/hw_ddc.c`, and generation-specific `hw_translate_*` files to map logical DDC, HPD, generic, and PWRSEQ pins to MMIO offsets, masks, and shifts.
- Panel/backlight control paths use PWRSEQ and BL_PWM fields through DCE/DCN panel control headers and implementations, including stored backlight register save/restore, PWM period/duty programming, PWM group locking, and panel power-state polling.
- DSC code consumes DSCC/DSCCIF/DSC_TOP field names through DSC field-list macros and register helpers. Later-generation DSC headers show the same naming contract for programming PPS registers, enabling DSC clocks, reading update-pending state, configuring interrupts, and collecting error/fullness diagnostics.
- IRQ and hotplug flows depend on HPD and HPDRX mapping code in the display IRQ services; this chunk's GPIO HPD masks are adjacent infrastructure for the physical pin state, while HPD interrupt registers live elsewhere in the full header.
- DMUB and resource initialization can use the same register tables to restore or coordinate DCN 3.1.2 display state across firmware-assisted paths.
- SOC enum headers define values for some fields described here, such as `DCIO_UNIPHY_CHANNEL_XBAR_SOURCE` and PWRSEQ target/override enums, while this chunk supplies the bit placement.

The direct interface is a preprocessor name contract. Missing or renamed macros normally fail at build time when an `SF`/`REG_*` table expands. Incorrect numeric masks are more dangerous because the build can succeed while runtime MMIO writes target the wrong bits.

## Risks And Edge Cases

- The chunk begins inside `UNIPHYB_CHANNEL_XBAR_CNTL` and ends inside `DC_PERFMON19_PERFCOUNTER_CNTL2`; merge/reconciliation must include adjacent chunks for complete register-family coverage.
- GPIO and AUX/DDC masks are tightly tied to board routing and connector discovery. Wrong DDC clock/data, AUX pad mode, RX select, polarity, pull-down, or power-good masks can break EDID reads, AUX transactions, link training, or HPD behavior.
- HPD and generic GPIO fields are repetitive and review-unfriendly. A one-pin mask drift can affect only one connector, making failures appear board-specific.
- PWRSEQ fields have visible user impact. Incorrect panel `DIGON`, `BLON`, target-state, delay, reference-divider, PWM period, or PWM duty masks can cause black panels, flicker, bad brightness levels, or resume failures.
- Grouped PWM register lock/update-pending fields are sequencing-sensitive. Updating duty-cycle fields without the correct lock/unlock and pending polling can leave stale backlight values or create frame-boundary glitches.
- DCIO soft-reset bits are high-impact. A wrong reset mask could reset the wrong UNIPHY/DSYNC/PWRSEQ block or fail to reset a block that needs recovery.
- DSCC PPS fields mirror DSC protocol parameters. Mask drift in bits-per-pixel, chunk size, slice dimensions, BPG offsets, QP ranges, or RC thresholds can produce compressed stream corruption that may only show on DSC-enabled displays and modes.
- DSCC interrupt/status/clear bits mix enable, status, and clear semantics in one generated namespace. The shift/mask header cannot prevent callers from treating clear bits as ordinary state bits.
- DSC clock-gating and DSCC memory-power fields can interact with low-power behavior. Wrong masks can leave DSC inaccessible, waste power, or cause hangs if registers are touched while the required clock/power state is absent.
- Full-width readback masks such as squared-error words and high-bit masks such as perfmon selectors, interrupt acknowledgements, and DSC PPS fields require unsigned 32-bit handling in callers.
- `DSC_TOP0_DSC_DEBUG_CONTROL` is duplicated in this chunk with identical definitions. That is probably generator output, but whole-file validation should confirm it is intentional and not masking a missing adjacent register.
- Reserved UNIPHY macro-control registers are intentionally opaque. They preserve register-map coverage but give no semantic safety; any consumer must rely on hardware documentation or generator provenance.
- Similar field names exist across DCN generations, but this file is specific to DCN 3.1.2. Copying masks from DCN 3.0.x, 3.1.x variants, or later ASICs is unsafe without register-database confirmation.

## Test Signals

Useful validation is mostly build-time, register-table, and hardware-integration oriented:

- Build AMDGPU Display Core with DCN 3.1 support so `dcn31_resource.c`, `irq_service_dcn31.c`, and `dmub_dcn31.c` compile against `dcn_3_1_2_offset.h` plus this shift/mask header.
- Preprocess or compile GPIO, DDC, HPD, panel-control, DSC, and perfmon users that expand `SF_DDC`, `HPD_REG_LIST`, `DCN301_PANEL_CNTL_SF`-style lists, `DSC_SF`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT` against these macro names.
- Compare this header slice against the matching offset header and upstream register-generation source to ensure every listed register field has a matching register offset and expected bit width.
- Exercise DDC/AUX paths on DCN 3.1.2 hardware: EDID read, DP AUX transactions, AUX/I2C mode switching, HPD-low AUX error paths, connector hotplug/unplug, and multi-connector boards that cover DDC1-DDC5 and DDCVGA if present.
- Validate GPIO translation for generic, HPD, DDC, genlock, and PWRSEQ pins by checking logical pin mappings against board schematics or BIOS connector tables.
- Exercise panel power and backlight behavior: boot panel enable, suspend/resume restore, backlight duty updates, PWM period/reference-divider setup, group-lock update-pending polling, and PWRSEQ0/PWRSEQ1 selection.
- Run DSC-enabled display modes that cover RGB, 4:2:2/4:2:0/native modes where supported, multiple slice widths/heights, different bits-per-pixel/component settings, and mode changes that force PPS reprogramming.
- Check DSC error/fullness/status telemetry after stress modes and link-rate changes, including interrupt enable/status/clear behavior for buffer overflow/underflow and end-of-frame-not-reached conditions.
- Verify DSC clock enable/disable and memory power transitions across blanking, modesets, low-power entry/exit, and reset paths.
- Run perfmon smoke tests for DC perfmon19 counter event selection, counter activation, interrupt enable path, hardware stop controls, and counter-off selection once the adjacent chunk supplies the remaining perfmon fields.

## Open Cross-Chunk Questions

- The preceding chunk should provide the beginning of `UNIPHYB_CHANNEL_XBAR_CNTL`; this chunk only includes channel 2/3 shifts and all four masks.
- The next chunk should complete `DC_PERFMON19_PERFCOUNTER_CNTL2` and likely the rest of the DC perfmon19 register family.
- Whole-file reconciliation should decide whether the duplicated `DSC_TOP0_DSC_DEBUG_CONTROL` block is expected generator output or a sign that a neighboring DSC top register is missing from the source register database.
- Final synthesis should identify the generator/register-database provenance if available, because manual edits to this file are high risk and hard to validate by inspection alone.

### subset-b-001821: lines 47040-49469

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 47040-49469

## Scope

This chunk covers 2,430 lines from the generated DCN 3.1.2 shift/mask header. It contains only preprocessor constants and generated address-block comments; there are no C functions, structs, enums, storage definitions, loops, branches, or local algorithms in this range.

The range starts at the final two mask definitions for `DC_PERFMON19_PERFCOUNTER_CNTL2`, then covers complete register-field definitions for the rest of perfmon instance 19, DSC compressor instances 1 and 2, HPO top/stream-mapper fields, perfmon instances 20 through 22, HPO HDMI stream encoder 0 audio/packet blocks, HPO DP stream encoder 0, APG0, DME5/DME6, VPG5/VPG6, and the beginning of DP symbol encoder 0 sideband-packet controls. It ends inside `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL13`, after the first eight `__SHIFT` fields; the masks and remaining fields for that register continue in the next chunk.

The chunk contains 2,146 `#define` entries. Most definitions come in `__SHIFT` and `_MASK` pairs. The only boundary exceptions are the two tail masks for `DC_PERFMON19_PERFCOUNTER_CNTL2` at the beginning and the partial `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL13` shift list at the end.

## Purpose

This header slice gives DCN 3.1.2 AMD display code the bit positions and masks used to program Display Core Next hardware registers. Runtime code combines these constants with the matching offset header and AMD display register helpers to read, write, update, and decode MMIO fields without open-coded bit arithmetic.

The covered hardware domains are:

- Display Stream Compression, via `DSCC1_*`, `DSCCIF1_*`, `DSC_TOP1_*`, `DSCC2_*`, `DSCCIF2_*`, and `DSC_TOP2_*` fields.
- DC performance monitors 19 through 22, including counter selection, counter state, run/stop gating, counted-value reads, and interrupt status/ack fields.
- HPO top-level clock/reset controls and DP stream mapper target selection.
- HPO HDMI stream encoder 0 packet/audio blocks, including AFMT5, DME5, and VPG5.
- HPO DP stream encoder 0 blocks, including DP stream encoder clock/input/audio selection, APG0 audio-packet generation, DME6 metadata engine fields, VPG6 packet payload state, and DP symbol encoder 0 video/MSA/GSP sideband fields.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated preprocessor naming contract:

- `<REGISTER>__<FIELD>__SHIFT` defines the bit offset of a field.
- `<REGISTER>__<FIELD>_MASK` defines the corresponding field mask.
- Address-block comments, such as `// addressBlock: dce_dc_dsc1_dispdec_dscc_dispdec`, identify the generated hardware block that owns subsequent register groups.
- Register helper macros elsewhere concatenate register and field tokens to resolve these definitions through field-list macros such as `DSC_REG_LIST_SH_MASK_DCN20`, `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST`, and `DCN31_APG_MASK_SH_LIST`.

Important DSC register families in this chunk include:

- `DSCC{1,2}_DSCC_CONFIG0/1`, which describe slice layout, alternate ICH encoding enablement, vertical slice count, and rate-control buffer model size.
- `DSCC{1,2}_DSCC_STATUS`, exposing double-buffer update-pending state.
- `DSCC{1,2}_DSCC_INTERRUPT_CONTROL_STATUS`, mapping rate-buffer overflow/underflow status bits and per-condition interrupt-enable bits for four buffers plus rate-control model overflow bits.
- `DSCC{1,2}_DSCC_PPS_CONFIG0` through `PPS_CONFIG22`, mapping Display Stream Compression PPS fields: DSC version, PPS identifier, line buffer depth, bits per component/pixel, VBR, 4:2:2/4:2:0/native modes, chunk size, picture size, slice size, initial transmit/decode delay, scaling values, BPG offsets, initial/final offsets, flatness QP, RC model size, RC edge factor, quantization increment limits, target offsets, RC buffer thresholds, and range min/max QP and BPG offsets.
- `DSCC{1,2}_DSCC_MEM_POWER_CONTROL`, mapping memory low-power force/disable/default state and separate RAM power-state indicators.
- `DSCC{1,2}_DSCC_*_SQUARED_ERROR_*`, `MAX_ABS_ERROR*`, and rate-buffer fullness registers, exposing DSC debug/quality/error metrics and fullness counters.
- `DSCCIF{1,2}_DSCCIF_CONFIG0/1`, mapping source-select, bits per component, pixel format, back-pressure delay, and YCbCr 4:2:2 simple/stuffing/depth behavior.
- `DSC_TOP{1,2}_DSC_TOP_CONTROL` and `DSC_DEBUG_CONTROL`, mapping DSC clock enable, clock-gating disables, memory shut-down control, debug enable, and test-clock mux selection.

Important perfmon register families include:

- `DC_PERFMON{19,20,21,22}_PERFCOUNTER_CNTL` and `CNTL2`, configuring eight counters through event selection, counted-value type, hardware stop selectors, count-off selector, and secondary selector fields.
- `DC_PERFMON{19,20,21,22}_PERFCOUNTER_STATE`, mapping each counter's two-bit state and per-counter state selector.
- `DC_PERFMON{19,20,21,22}_PERFMON_CNTL` and `CNTL2`, defining perfmon run state, report count, count-off interrupt enable/status/ack, count-off interrupt type, clock enable, and run-enable start/stop selectors.
- `DC_PERFMON{19,20,21,22}_PERFMON_CVALUE_INT_MISC`, `CVALUE_LOW`, `HI`, and `LOW`, exposing counter interrupt status/ack bits and low/high counted-value readback fields.

Important HPO and stream encoder families include:

- `HPO_TOP_CLOCK_CONTROL`, which has a dense set of 15 clock-enable and 15 clock-on fields for DTO, stream encoder, DP link encoder, DPG, PHY, stream encoder clock, HDMI stream encoder, audio, DMU, DIO, DISPCLK, DPREFCLK, SYMCLK, and ALINK clocks.
- `HPO_TOP_HW_CONTROL`, mapping global HPO enable.
- `DP_STREAM_MAPPER_CONTROL0` through `CONTROL3`, mapping DP stream link target fields.
- `DP_STREAM_ENC0_DP_STREAM_ENC_*`, mapping stream encoder clock enable, pixel/audio input mux selection, clock-ramp FIFO reset/enable/status/level, and spare bits.
- `DP_SYM32_ENC0_DP_SYM32_ENC_CONTROL`, `VID_FIFO_CONTROL`, `VID_MSA_DOUBLE_BUFFER_CONTROL`, `VID_PIXEL_FORMAT_DOUBLE_BUFFER_CONTROL`, `VID_PIXEL_FORMAT`, `VID_MSA0` through `VID_MSA8`, and `HBLANK_CONTROL`, mapping symbol encoder reset/enable status, pixel-to-symbol FIFO state, MSA and pixel-format double buffering, pixel encoding/depth, MSA lane payload words, and minimum hblank symbol width.
- `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL0` through the partial `CONTROL13`, mapping generic secondary data packet transmission modes: video/idle continuous transmission, one-shot triggers, trigger position, double buffering, payload size, SOF reference, deadline missed/pending states, double-buffer pending state, and transmission line number.

Important HDMI/DP packet and audio families include:

- `AFMT5_AFMT_*`, mapping HDMI audio and infoframe behavior: VBI packet control, audio packet layout/send behavior, audio info bytes, IEC 60958 channel-status words, audio CRC control/result, ramp control, AFMT status, audio source selection, infoframe control, interrupt status, and memory power.
- `DME5_DME_*` and `DME6_DME_*`, mapping data/metadata engine enable, update, generic packet, multi-frame, line-number, double-buffer, pending, immediate update, and memory power control fields.
- `VPG5_VPG_*` and `VPG6_VPG_*`, mapping generic packet access/data, GSP frame-update and immediate-update controls for multiple packets, generic status, memory power, ISRC access/data, and MPEG infoframe payload fields.
- `APG0_APG_*`, mapping DP audio packet generator reset/status, enable, stream ID, debug audio channel generation, packet control, audio CRC, status, memory power, and spare bits.

## Control Flow

This chunk has no runtime control flow. Its effective control flow is compile-time token resolution:

1. DCN 3.1.2 display code includes `dcn_3_1_2_sh_mask.h` with the matching DCN 3.1.2 offset header.
2. Resource constructors and hardware-block headers define per-block register, shift, and mask tables by expanding macros such as `DSC_SF`, `SE_SF`, and `SRI_ARR`.
3. Runtime MMIO helpers such as `REG_GET`, `REG_SET`, `REG_SET_N`, and `REG_UPDATE` use the resulting register address, shift, and mask tables to isolate or update hardware fields.

The source order mirrors generated hardware address-block order. Within most register comments, all `__SHIFT` macros for the register are emitted first and all `_MASK` macros follow. The chunk boundaries split two generated groups, so whole-file analysis must reconcile the missing beginning of `DC_PERFMON19_PERFCOUNTER_CNTL2` and the missing tail of `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL13`.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes the bit layout of state held by DCN 3.1.2 display hardware:

- DSC PPS, slice, rate-control, DSCCIF, and top-control fields persist in the DSC hardware until reprogrammed, reset, power-gated, or restored across suspend/resume.
- DSC status, interrupt, error, fullness, and memory power-state fields can change asynchronously as compression runs, buffers fill or drain, interrupts occur, or memory power management changes state.
- Perfmon control fields configure hardware counters, while counter state, interrupt status, and counted-value fields reflect live hardware measurement state. Interrupt ack fields are write-sensitive and should be handled according to the hardware programming guide, not inferred from this header alone.
- HPO clock and hardware-enable fields control hardware availability. Clock-on/status fields report live clock state and may lag requested enable bits.
- AFMT, APG, DME, VPG, DP stream encoder, and DP symbol encoder fields persist programmed packet, audio, metadata, stream, MSA, and double-buffer state until reprogramming or reset. Pending/status/deadline fields are live hardware observations.

This file does not specify reset values, legal enumerations, read/write permissions, sticky semantics, write-one-to-clear behavior, or sequencing requirements. Those behaviors come from the ASIC register specification and the driver code that consumes these macros.

## Dependencies And Integration Points

This chunk depends on generated DCN 3.1.2 register files remaining synchronized:

- The matching `dcn_3_1_2_offset.h` supplies register offsets and base indices for the same register names.
- AMD display register helper macros depend on the exact suffix convention used here: `__SHIFT` for bit positions and `_MASK` for masks.
- DSC integration occurs through `drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.*` and resource files that expand `DSC_REG_LIST_DCN20` and `DSC_REG_LIST_SH_MASK_DCN20` for DSC instances.
- HPO DP stream encoder integration occurs through `drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h`, whose DCN3.1 mask/shift list references fields from `DP_STREAM_MAPPER_CONTROL0`, `DP_STREAM_ENC0_*`, and `DP_SYM32_ENC0_*`.
- APG integration occurs through `drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h`, which references `APG0_APG_CONTROL`, `APG0_APG_CONTROL2`, `APG0_APG_DBG_GEN_CONTROL`, and `APG0_APG_MEM_PWR` fields from this range.
- DMUB and IRQ code include this generated header directly for DCN 3.1.2 display management and interrupt handling.

The main contract is compile-time naming plus numeric correctness. Missing or renamed fields usually produce build failures in generated field-list expansions; wrong masks or shifts can build successfully and cause bad MMIO writes or incorrect status decoding.

## Risks And Edge Cases

- The chunk starts mid-register at `DC_PERFMON19_PERFCOUNTER_CNTL2`; only two masks are present here. The previous chunk must be merged to describe the whole register.
- The chunk ends mid-register at `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL13`; only the first eight shift definitions are present here. The next chunk must supply the remaining shifts and masks.
- DSC1 and DSC2 register blocks are nearly identical. Prefix mistakes can route PPS or control writes to the wrong DSC instance and may only appear when multiple compressed streams are active.
- DSC PPS fields are tightly packed and protocol-sensitive. Mask/shift mistakes in bits-per-pixel, slice size, RC model, thresholds, or range QP/BPG fields can produce blanking, link training failures, visible corruption, or underrun/overflow interrupts.
- Interrupt-control registers pack status and enable fields into the same word. Consumers must not infer clear or acknowledge behavior from the mask name alone.
- Perfmon fields mix selectors, live state, counted values, interrupt status, and ack bits. Using the wrong counter instance or selector can silently invalidate performance telemetry.
- HPO clock-enable fields and clock-on fields are adjacent and repetitive. Confusing request bits with status bits can make reset or enable sequencing unreliable.
- DP symbol encoder GSP controls repeat the same field layout across many packet slots. A single wrong packet index can transmit the right sideband payload at the wrong cadence or scanline.
- Several fields use full-width masks such as `0xFFFFFFFFL`; consumers should avoid signed intermediate assumptions and should use the driver helper types consistently.
- Cross-generation reuse is risky. DCN 3.1, 3.1.2, 3.2, and later HPO/DSC blocks share names and layouts in many places but are not guaranteed to be numerically identical.

## Test Signals

Useful validation signals are mostly build-time, static-comparison, and hardware-integration oriented:

- Build AMDGPU display code for DCN 3.1.2 configurations to catch unresolved field names in `DSC_REG_LIST_SH_MASK_DCN20`, `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST`, `DCN31_APG_MASK_SH_LIST`, IRQ, and DMUB include paths.
- Compare this header against the matching `dcn_3_1_2_offset.h` and the authoritative register database to verify that every register in this range has matching offsets and that every mask matches the documented bit range.
- Exercise DSC enable/disable and compressed DisplayPort modes across one and two DSC instances; verify PPS programming, slice dimensions, bits-per-pixel, DSCCIF input format, top clock enable, double-buffer update pending, and absence of rate-buffer overflow/underflow interrupts.
- Run display suspend/resume, hotplug, and modeset tests with DSC enabled to confirm DSC, DSCCIF, and DSC_TOP state is restored or reprogrammed correctly.
- Exercise HPO DP link bring-up and stream mapping, checking stream target selection, stream encoder clock/input mux state, FIFO reset/enable/done transitions, symbol encoder reset/enable/done transitions, MSA programming, pixel-format double buffering, and hblank symbol width.
- Test DP sideband packet scheduling for GSP packet slots covered here, including continuous transmission, one-shot transmission, SOF reference, transmission line number, double-buffer pending, and missed-deadline status.
- Exercise HDMI and DP audio packet paths, checking AFMT/APG enablement, stream ID selection, audio info fields, IEC 60958 status fields, audio CRC results, memory power controls, and mute/packet enable behavior.
- Validate DME/VPG generic packet and infoframe paths by changing metadata and observing double-buffer pending/status transitions plus correct ISRC/MPEG/generic payload transmission.
- Use perfmon instances 19 through 22 to count a known display event, then verify counter state transitions, low/high counted value readback, interrupt status, and ack behavior.

## Open Cross-Chunk Questions

- The merge lane should combine this with the previous chunk to reconstruct the full `DC_PERFMON19_PERFCOUNTER_CNTL2` field list.
- The merge lane should combine this with the next chunk to finish `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL13`.
- Whole-file analysis should verify whether DCN 3.1.2 resource code intentionally exposes all packet slots and DSC instances covered by this generated header, or whether some definitions are generated but unused on specific ASIC variants.

### subset-b-001822: lines 49470-51864

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 49470-51864

## Scope

This chunk covers a generated DCN 3.1.2 register shift/mask header slice for high-performance DisplayPort output (HPO DP) stream encoder hardware. It contains only preprocessor constants and generated register grouping comments; there are no functions, structs, enums, global storage objects, or executable statements in this slice.

The range is 2,395 lines with 2,139 `#define` entries: 1,072 `__SHIFT` definitions and 1,067 `_MASK` definitions. The count is intentionally uneven because the chunk starts in the middle of `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL13` and ends in the middle of `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL8`. It includes 15 complete address-block comments for HPO stream/APG/DME/VPG/SYM32 encoder instances 1 through 3, plus the tail of the previous SYM32 encoder 0 block.

## Purpose

The purpose of this header region is to provide symbolic bit positions and masks for DCN 3.1.2 HPO DP stream encoding, audio packet generation, DisplayPort stream metadata packet generation, and 32-symbol encoder state. AMDGPU display code includes this file together with the matching DCN 3.1.2 offset header so register helper macros can pack, update, and extract MMIO fields without embedding raw bit offsets.

This is a hardware-interface contract rather than algorithmic code. Its important behavior is the exact macro namespace and numeric bit layout expected by DCN31 register tables and register-access helpers.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for the same field.
- Address-block comments, such as `dce_dc_hpo_dp_stream_enc1_dispdec`, group register fields by hardware block.
- Register comments, such as `//DP_SYM32_ENC1_DP_SYM32_ENC_SDP_GSP_CONTROL0`, group the shift/mask pairs for a logical register.

The chunk covers these block families:

- Tail of `DP_SYM32_ENC0`: remaining GSP control 13 fields, full GSP control 14 fields, SDP stream/audio/metadata controls, MSA/VBID/video stream controls, panel replay control, CRC controls/results/status, memory power control, and spare.
- `DP_STREAM_ENC1`, `DP_STREAM_ENC2`, and `DP_STREAM_ENC3`: clock control, pixel/audio input mux control, clock-ramp adjuster FIFO controls, and spare fields.
- `APG1`, `APG2`, and `APG3`: audio packet generator reset/enable, stream ID selection, packet control, audio CRC control/result/status, memory power, and spare fields.
- `DME7`, `DME8`, and `DME9`: data mux engine control, metadata HSI/stereo flags, source select, reset/enable status, reset select, and memory power fields.
- `VPG7`, `VPG8`, and `VPG9`: generic packet indexed data access, GSP frame/immediate update bits for generic packets 0-14, generic conflict status/clear, memory power, ISRC access/data, and MPEG info packet words.
- `DP_SYM32_ENC1` and `DP_SYM32_ENC2`: complete symbol encoder blocks covering reset/enable, pixel-to-symbol FIFO, MSA and pixel-format double buffering, pixel format, MSA data registers, HBLANK minimum symbol width, GSP controls 0-14, SDP stream/audio/metadata controls, MSA/VBID/video stream controls, panel replay, CRC, memory power, and spare fields.
- Beginning of `DP_SYM32_ENC3`: complete control, FIFO, MSA/pixel-format, video MSA data, HBLANK, and GSP controls 0-7, followed by only the shift fields for GSP control 8 at the chunk boundary.

Important repeated field families include:

- Clock and mux controls: stream encoder clock enable/status across `DISPCLK`, `SOCCLK`, `DPSTREAMCLK`, and `SYMCLK32`, plus pixel/audio stream source select fields.
- FIFO and reset controls: FIFO enable/reset/read-start-level/read-clock-source/reset-done/video-active/error fields, plus symbol-encoder and pixel-to-symbol FIFO reset/done/enable fields.
- Video formatting controls: pixel encoding type, uncompressed pixel encoding, component depth, dynamic range, YCbCr coefficient selection, MSA lane data, MSA double buffering, pixel-format double buffering, and HBLANK minimum symbol width.
- Generic secondary-data packet controls: GSP continuous video/idle transmission, one-shot trigger, one-shot position, double buffering, payload size, start-of-frame reference, deadline-missed/pending status, double-buffer pending status, and transmission line number.
- SDP/audio/metadata controls: SDP stream enable, GSP priority, CRC16 enable, audio sample/time/info/change/ISRC packet enablement, audio mute/status, audio sample concatenation limits, metadata packet enable, double buffering, SOF reference, pending status, and line number.
- Video status and validation fields: video stream enable/deferred disable/status, VBID compressed stream flag timing, panel replay tunneling optimization, video CRC enable/continuous mode/results/valid bit.
- Packet generators: VPG generic packet byte lanes, GSP frame and immediate update bits, ISRC continuation/index/data, MPEG info packet fields, and VPG conflict status.
- Power fields: memory low-power default, force, disable, and state for SYM32/VPG/APG/DME-related blocks.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time token resolution:

1. DCN31 code includes `dcn_3_1_2_offset.h` and `dcn_3_1_2_sh_mask.h`.
2. Resource construction macros build per-instance register tables, for example `hpo_dp_stream_encoder_reg_list(1)` resolves `DP_STREAM_ENC1`, `DP_SYM32_ENC1`, APG, and VPG register offsets.
3. Shift/mask table initializers such as `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST(__SHIFT)` and `_MASK` use the generated field macros from this header.
4. Runtime register helpers such as `REG_UPDATE`, `REG_GET`, `REG_SET`, `FD_MASK`, and `FD_SHIFT` apply the resolved constants to MMIO reads/writes.

The declaration order mirrors hardware instance order. The chunk finishes encoder 0, then lists stream/APG/DME/VPG/SYM32 blocks for HPO stream encoder 1, repeats the same pattern for encoder 2, and starts the same pattern for encoder 3.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes bit locations for state that lives in DCN 3.1.2 display hardware registers.

Writable fields can program HPO DP clock enablement, mux source selection, FIFO/reset sequencing, pixel format, MSA transmission timing, generic SDP/GSP transmission timing, audio packet behavior, metadata packet delivery, video stream enablement, panel replay optimization, CRC capture, and memory power policy. Read-only or hardware-updated fields can report reset completion, FIFO/video activity/error state, pending or deadline-missed packet transmission, audio mute status, CRC results/validity, VPG generic-packet conflicts, and memory power state.

Persistence is hardware-defined. Programmed control fields generally persist until driver reprogramming, display block reset, suspend/resume restore, or ASIC reset. Status fields may change with stream enable/disable, packet transmission, hotplug modes, clock/power transitions, or CRC capture state. This generated header does not encode access type, reset values, write-one-to-clear semantics, or ordering requirements.

## Dependencies And Integration Points

The matching offset contract is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h`. The same 15 HPO DP address blocks for stream encoder instances 1-3 appear there with `reg...` offsets and `_BASE_IDX` values. The offset and shift/mask headers must be generated from the same register database; otherwise register table construction can compile with missing symbols or, worse, program the wrong field bits.

Important source-tree integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` builds four HPO DP stream encoder register tables, initializes `hpo_dp_se_shift` and `hpo_dp_se_mask`, and reports `num_hpo_dp_stream_encoder = 4`.
- The same resource code maps HPO stream instances to VPG/APG blocks: `VPG[6] -> HPO_DP[0]`, `VPG[7] -> HPO_DP[1]`, `VPG[8] -> HPO_DP[2]`, `VPG[9] -> HPO_DP[3]`; `APG[0-3] -> HPO_DP[0-3]`. This chunk covers the generated VPG7-9 and APG1-3 field definitions for instances 1-3.
- `drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h` defines the DCN31 HPO stream encoder register and field lists that consume the generated `DP_STREAM_ENC*` and `DP_SYM32_ENC*` shift/mask symbols.
- `drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h` consumes APG field symbols through `DCN31_APG_MASK_SH_LIST`; `dcn31_apg.c` uses those fields for reset, enable, audio stream ID, debug channel enablement, and memory power programming.
- `drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h` consumes VPG field symbols through `DCN31_VPG_MASK_SH_LIST`; the generated VPG7-9 macros in this chunk support HPO instances 1-3 even though field tables are written against instance-0 names and paired with per-instance register offsets.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c` and `drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c` directly include `dcn_3_1_2_sh_mask.h` along with the matching offset header for DMUB and IRQ register infrastructure.

The DME7-9 macros in this chunk are part of the generated HPO stream encoder register map, but direct consumers are less visible in the nearby DCN31 code than APG/VPG/SYM32. Whole-file or cross-file analysis should reconcile whether DME programming is unused, abstracted through other generated tables, or reserved for firmware/hardware flows.

## Risks And Edge Cases

- The chunk boundaries split register definitions. The start lacks the earlier `DP_SYM32_ENC0...GSP_CONTROL13` shift and some mask fields, while the end has only `DP_SYM32_ENC3...GSP_CONTROL8` shift fields and no corresponding masks. The merge lane must combine adjacent chunks before making whole-file completeness claims.
- The blocks are highly repetitive across instances 1-3. A generator drift or copy error that changes only one instance can be hard to spot in review because most lines differ only by instance number.
- The runtime HPO stream encoder field tables use instance-0 field names for common shift/mask values while pairing them with per-instance register offsets. That pattern assumes equivalent field layout across instances; per-instance divergence would require different shift/mask tables.
- Several fields are status or pending bits next to writable control bits, such as reset done, FIFO error, packet transmission pending, double-buffer pending, CRC valid, and memory power state. This header does not prevent accidental writes to status bits.
- Packet timing fields such as `GSP_TRANSMISSION_LINE_NUMBER`, `METADATA_PACKET_TRANSMISSION_LINE_NUMBER`, `VBID_6_COMPRESSEDSTREAM_FLAG_LINE_NUMBER`, and `MSA_TRANSMISSION_LINE_NUMBER` can affect precisely when data is emitted relative to a frame. Wrong shifts or masks may produce intermittent display, audio, metadata, or compliance failures.
- Full-width masks such as VPG generic packet data, ISRC data, MPEG info fields, MSA lane registers, and spare registers use `0xFFFFFFFFL`; consumers should use unsigned 32-bit register values and avoid signed-width assumptions.
- Packed byte and lane fields invite off-by-one errors. VPG generic packet data packs bytes 0-3 into one word, and SYM32 MSA fields carry lane data across full 32-bit registers.
- Memory power controls are present in SYM32, VPG, APG, and DME families. Incorrect force/disable/default state programming can cause reads or writes to appear flaky if the block is clocked or powered down.
- Cross-generation reuse is risky. DCN 3.1.2 names resemble nearby DCN 3.1/3.2 generated headers, but offsets and field layouts must be paired with the exact ASIC generation.

## Test Signals

Useful validation signals are mostly build-time, generated-header consistency, and hardware integration checks:

- Build AMDGPU display code for a DCN31/DCN 3.1.2 configuration to catch missing generated macros in `SRI`, `SE_SF`, `FD_MASK`, `FD_SHIFT`, `REG_GET`, and `REG_UPDATE` expansions.
- Preprocess `dcn31_resource.c`, `dcn31_hpo_dp_stream_encoder.c`, `dcn31_apg.c`, and `dcn31_vpg.c` to confirm the intended per-instance register offsets combine with the common shift/mask field tables.
- Compare this slice against `dcn_3_1_2_offset.h` and verify every register named here has a matching `reg...` offset and base index, especially across `DP_STREAM_ENC1-3`, `APG1-3`, `DME7-9`, `VPG7-9`, and `DP_SYM32_ENC1-3`.
- Validate generated field values against the authoritative AMD register database for DCN 3.1.2, with special attention to high-bit status fields, full-width masks, packet line-number fields, memory-power fields, and repeated GSP control blocks.
- Exercise HPO DP stream creation and destruction on hardware, verifying that all four HPO stream encoder instances can be allocated, mapped to the expected APG/VPG blocks, enabled, disabled, and reset.
- Run DisplayPort 128b/132b or HPO-capable link tests with video stream enable/disable, pixel format changes, MSA programming, metadata packet transmission, panel replay modes, and CRC capture.
- Exercise audio paths through APG programming, checking reset completion, stream ID programming, audio packet generation, mute behavior, audio CRC result/status, and suspend/resume restore.
- Stress generic packet updates through VPG frame-update and immediate-update paths, including conflict status/clear behavior and ISRC/MPEG packet programming.
- Test power-management transitions while repeatedly enabling/disabling streams to catch stale memory-power force/disable settings or missing reinitialization after reset.

## Open Cross-Chunk Questions

- The previous chunk is needed to present `DP_SYM32_ENC0` GSP control 13 as a complete register group.
- The next chunk is needed to complete `DP_SYM32_ENC3` GSP control 8 and the rest of SYM32 encoder 3.
- Whole-file analysis should reconcile DME7-9 generated fields with the actual DCN31 runtime programming path, since APG/VPG/SYM32 consumers are explicit but DME usage is not obvious from the local HPO stream encoder construction path.
- Whole-file analysis should verify that the instance-0 shift/mask table assumption used by DCN31 HPO code remains valid for all generated instances covered here.

### subset-b-001823: lines 51865-54474

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 51865-54474

## Scope

This chunk covers lines 51865-54474 of the generated DCN 3.1.2 shift/mask header. It contains only preprocessor constants and generated register grouping comments: 2070 `#define` entries, made up of 1034 `__SHIFT` constants and 1036 `_MASK` constants, plus 35 `addressBlock` group comments. There are no functions, structs, enums, storage objects, or executable statements in this range.

The range starts in the middle of `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL8`, after several shift definitions that belong to the previous chunk, and ends in the middle of the `AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` / following pin-capability area that continues in the next chunk. Complete register families in the body cover HPO DisplayPort stream encoder 3 sideband/audio/video fields, HPO DP link encoder instances 0 and 1, HPO DP DPHY SYM32 instances 0 and 1, display HVM control, legacy VGA indexed register masks, Azalia F2 codec endpoint/input/root blocks, audio descriptor and sink-info indexed blocks, Azalia CRC result blocks, and Azalia F0 stream latency blocks 0-15.

## Purpose

The purpose of this region is to expose symbolic bit positions and masks for DCN 3.1.2 display, DisplayPort, VGA compatibility, and display-audio hardware registers. AMDGPU display code combines these macros with the matching DCN 3.1.2 offset header and register helper macros to pack writes, update individual fields, and decode status values without hard-coding raw bit layouts.

This is a generated hardware contract rather than algorithmic code. Its behavioral importance is the exact macro name and numeric bit layout. Runtime behavior is produced by consumers that use these constants for MMIO or indexed-register access.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within a 32-bit register.
- `// addressBlock: ...` comments identify indexed or decoded register blocks.
- `//<REGISTER>` comments group the field macros for one logical register.

Major constant groups in this chunk include:

- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL8` through `GSP_CONTROL14`, with GSP sideband packet controls such as video/idle continuous transmission enable, one-shot trigger, one-shot position, double-buffer enable/pending, payload size, SOF reference, transmission pending/deadline status, and transmission line number.
- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_CONTROL`, `SDP_AUDIO_CONTROL0/1`, and `SDP_METADATA_PACKET_CONTROL`, covering sideband stream enable, CRC16 enable, audio packet enables for ASP/ATP/AIP/ACM/ISRC, audio mute/status, ATP version, audio packet concatenation limits, metadata packet enable, metadata double buffering, SOF reference, and line-number scheduling.
- `DP_SYM32_ENC3_DP_SYM32_ENC_VID_*` registers for main-stream attributes, VBID compressed-stream flag scheduling, stream enable/defer/status, panel replay tunneling optimization, video CRC control/results/status, memory power control, and spare bits.
- `DP_LINK_ENC0` and `DP_LINK_ENC1` clock-control/spare fields for link-encoder clock enable/force-on behavior.
- `DP_DPHY_SYM320` and `DP_DPHY_SYM321` DPHY SYM32 registers for reset/enable/status, output mode, lane count, scheduler status, SAT update and VC rate control, per-VC SAT configuration/status, training-pattern selection, PRBS seeds, square-pulse/custom test pattern data, error status, symbol override, and CRC configuration/status/count.
- `DCHVM_*` display HVM controls for enablement, VMID/PASID, clock control, memory interface settings, RIOMMU control, and RIOMMU status.
- Legacy VGA indexed masks for sequencer (`SEQ00`-`SEQ04`), CRT controller (`CRT00`-`CRT18`, `CRT1E`, `CRT1F`, `CRT22`), graphics controller (`GRA00`-`GRA08`), and attribute controller (`ATTR00`-`ATTR14`) fields.
- `AZALIA_F2_CODEC_*` endpoint, input-endpoint, and root-function registers for converter format, channel/stream ID, digital converter flags, stream/rate capability bitmaps, pin widget controls, unsolicited responses, pin sense, default configuration words, speaker/channel allocation, audio descriptors, multichannel enablement, HBR, lipsync, LPIB snapshots, coding type, format-change flags, wireless display identification, remote keepalive, subsystem IDs, power state, reset, and codec function parameters.
- `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13` and `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17`, plus manufacturer/product IDs, sink description length, and port IDs used by the Azalia sink-info/descriptor indexed blocks.
- Azalia input/output CRC result blocks: `AZALIA_INPUT_CRC0/1_CHANNEL0-7` and `AZALIA_CRC0/1_CHANNEL0-7`.
- `AZF0STREAM0` through `AZF0STREAM15` stream latency and FIFO metrics: minimum FIFO size, maximum FIFO size, max latency support, latency-counter reset, worst-case latency count, cumulative latency count, and cumulative request count.
- The beginning of `AZF0ENDPOINT0` F0 endpoint converter/pin macros for audio widget capabilities, converter format, stream/channel routing, digital converter flags, stream formats, supported size/rates, stripe control, ramp rate, GTC embedding, GTC counter deltas, and the start of pin audio-widget capability fields.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time token expansion:

1. DCN 3.1.2 display code includes the matching offset and shift/mask headers.
2. Register helper macros concatenate register and field names to resolve these `__SHIFT` and `_MASK` constants.
3. Runtime display, DP, VGA, or audio code performs MMIO or indexed-register reads/writes using the resolved numeric layout.

The declaration order mirrors hardware organization. The chunk finishes part of DP stream encoder 3, then moves through HPO DP link/DPHY blocks, display VM, VGA indexed registers, Azalia F2 endpoint/root/descriptor/sink/CRC/input blocks, 16 F0 stream blocks, and finally starts the F0 endpoint 0 block.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes bit locations for hardware state in DCN 3.1.2 registers.

Writable fields in the described registers can program DP sideband packet timing, audio packet generation, metadata scheduling, video stream enablement, panel replay optimization, CRC capture, DPHY reset/enable/rate/test-pattern/CRC behavior, HVM/RIOMMU control, VGA compatibility state, Azalia converter formats, stream IDs, channel allocation, multichannel routing, digital converter flags, codec power/reset state, LPIB snapshot control, and latency-counter reset.

Hardware-updated or capability fields can expose DP stream/CRC status, DPHY scheduler/update/error/CRC status, RIOMMU status, VGA indexed register state, Azalia widget and pin capabilities, supported stream formats and sample rates, pin sense, hot-plug/audio status, input status, infoframe data, sink descriptors, CRC results, FIFO limits, and cumulative/worst-case latency counters. Access type, reset values, read-clear/write-one-to-clear behavior, and required programming order are not encoded here; consumers must follow the hardware spec and surrounding display/audio driver logic.

Programmed values persist according to hardware power/reset domains. They may survive until rewritten, display block reset, audio function reset, suspend/resume reinitialization, GPU reset, or ASIC reset. Counter and status fields are live hardware observations and can change without any C-visible state transition in this header.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.2 register offset header for addresses and indexed-register selectors. The shift/mask header alone only identifies bit positions; it does not identify where a register lives.

Primary integration points are AMD display register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT`, which rely on the generated suffix convention. A missing or renamed macro usually fails at compile time, while a wrong numeric mask or shift can compile successfully and surface only as broken hardware programming or misread status.

Related generated enum definitions exist outside this file for several fields, especially `DP_DPHY_SYM32_*` modes/status values and `AZALIA_F2_CODEC_*` converter format/digital-converter values. Those enums provide semantic values; this header provides the bit placement used to write or read those values.

Hardware-module integration spans multiple display subsystems:

- HPO DP stream/link/DPHY code consumes the `DP_SYM32_ENC3`, `DP_LINK_ENC*`, and `DP_DPHY_SYM32*` fields during link bring-up, stream enable/disable, training/test-pattern control, MST/SAT scheduling, CRC capture, and diagnostics.
- Display VM setup consumes the `DCHVM_*` masks for memory and RIOMMU control/status.
- VGA compatibility paths consume `SEQ*`, `CRT*`, `GRA*`, and `ATTR*` masks when legacy indexed VGA state must be programmed or preserved.
- Display audio/Azalia code consumes the F2 codec, descriptor, sink-info, CRC, stream, and F0 endpoint macros for HDMI/DisplayPort audio capabilities, stream configuration, status reporting, and latency/CRC diagnostics.

The offset header and this shift/mask header must be generated from the same register database. Cross-generation mixing with DCN 3.1, 3.0.x, or later ASIC headers is risky because names are similar but field layouts can diverge.

## Risks And Edge Cases

- The chunk starts mid-register. `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL8` has earlier shift fields in the previous chunk; this chunk begins at `GSP_TRIGGER_TRANSMISSION_DEADLINE_MISSED__SHIFT` and contains all masks for that register.
- The chunk ends mid-block. The `AZF0ENDPOINT0` F0 endpoint pin capability/register sequence continues in the next chunk, so this note should not be treated as a complete endpoint-0 analysis.
- Two HPO DPHY instances, `DP_DPHY_SYM320` and `DP_DPHY_SYM321`, repeat many field layouts. Generator drift or manual edits can be hard to spot because most lines differ only by instance number.
- Full-width masks such as CRC counts, custom test-pattern data, sink-description words, LPIB values, GTC deltas, latency counters, and stream-format bitmaps use `0xFFFFFFFFL`; consumers should avoid signed-width assumptions.
- Many fields are packed into high bits, including line-number fields at `0xFFFF0000L`, CRC/status bits, DPHY control bits, and VGA/Azalia configuration fields. Off-by-one shifts can corrupt unrelated control or status state.
- Capability, status, control, and reset fields use the same macro style. This header does not prevent writes to read-only/status fields or incorrect clear semantics.
- Azalia unsolicited-response, format-change, hot-plug, keepalive, LPIB snapshot, and latency-counter reset fields can affect event generation and diagnostics; incorrect programming may produce misleading audio hotplug or stream-position behavior.
- Legacy VGA indexed registers are included next to modern DCN/HPO/Azalia blocks. Consumers must use the correct indexed access path for the address block rather than assuming normal flat MMIO semantics.
- DPHY training pattern, symbol override, and CRC controls are diagnostic/link-training sensitive. Wrong masks can disrupt link training or make CRC diagnostics invalid while still compiling cleanly.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Build AMDGPU display code for a DCN 3.1.2-enabled configuration to catch missing symbols in register helper expansion.
- Preprocess representative users of `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT` to confirm token concatenation resolves to the expected `DP_SYM32_ENC3`, `DP_LINK_ENC*`, `DP_DPHY_SYM32*`, `DCHVM`, VGA, and Azalia macros.
- Compare this slice against the matching DCN 3.1.2 offset header and AMD register database so every register comment has matching offsets and every field has the intended mask/shift pair.
- Exercise HPO DisplayPort link bring-up, link training, MST/SAT scheduling, stream enable/disable, sideband packet transmission, metadata/audio packet generation, panel replay, and CRC capture on DCN 3.1.2 hardware.
- Exercise HDMI/DisplayPort audio with format changes, multichannel and HBR modes, sink descriptor reads, hotplug, suspend/resume, LPIB snapshots, latency counters, and audio CRC paths.
- Verify VGA fallback/compatibility paths if the ASIC exposes those legacy indexed registers in the tested configuration.
- Pay special attention to boundary fields split across chunks: `GSP_CONTROL8` at the beginning and `AZF0ENDPOINT0` pin capability/pin control fields at the end.

## Open Cross-Chunk Questions

- The merge lane should combine this chunk with subset `subset-b-001822` to describe `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL8` as a complete register.
- The merge lane should combine this chunk with subset `subset-b-001824` to describe the complete `AZF0ENDPOINT0` F0 endpoint block.
- Whole-file analysis should reconcile generated DCN 3.1.2 register exposure with actual resource counts and product configurations, especially the number of HPO DP, Azalia endpoint, and stream instances that are live on a given ASIC.

### subset-b-001824: lines 54475-56841

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 54475-56841

## Purpose

This chunk is generated AMD DCN 3.1.2 register field metadata. It contains no executable C logic; it publishes C preprocessor constants for field shifts and bit masks used to read, write, and update MMIO-backed Azalia/HD-audio endpoint registers on DCN 3.1.2 hardware.

The requested range is a mid-file slice of `dcn_3_1_2_sh_mask.h`. It covers 2,367 lines with 2,051 `#define` entries: 1,026 `__SHIFT` macros and 1,025 `_MASK` macros. The range starts in the middle of `AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, continues through the rest of endpoint 0 pin/status fields, covers complete endpoint 1 through endpoint 3 Azalia converter and pin field blocks, and ends partway through endpoint 4 at `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE`.

Although the path is under a local `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locking primitives in this range. The public interface is the generated macro namespace:

- `AZF0ENDPOINT<n>_<register>__<field>__SHIFT`: bit position for a named field.
- `AZF0ENDPOINT<n>_<register>__<field>_MASK`: bit mask for the same field.

These macros are intended to be consumed with the matching DCN 3.1.2 offset header and helper macros such as `FD_SHIFT`, `FD_MASK`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and DMUB register-table construction. The shift and mask constants are not useful by themselves unless the caller also addresses the correct endpoint register through `dcn_3_1_2_offset.h`.

Major field families in this slice:

- Endpoint 0 pin fields: tail of audio-widget capabilities, pin capabilities, unsolicited response control, pin sense, widget output enable, channel/speaker allocation, audio descriptor 0 through 13, multichannel enable maps, lipsync/HBR response, sink information, hot-plug controls, default configuration, channel-status overrides, association/status/LPIB fields, coding and format-change status, wireless-display identification, remote keepalive, and audio enable/disable/format interrupt status.
- Endpoints 1 through 3 complete blocks: converter audio-widget capabilities, converter stream format, channel/stream ID, digital converter control, supported formats and rates, stripe/ramp/GTC controls, GTC counter deltas, then the same pin-control, sink-info, multichannel, channel-status override, LPIB, coding, format-change, wireless-display, keepalive, and audio interrupt/status families as endpoint 0.
- Endpoint 4 partial block: converter and pin capability/control fields from audio-widget capabilities through audio descriptor 13 and the beginning of `MULTICHANNEL_ENABLE`.

Representative fields include audio channel count, amplifier presence, converter type, stream/channel IDs, digital converter enable/V/VCFG/DIGEN bits, supported stream formats and sample rates, GTC embedding and timing deltas, impedance sense, output enable, HDMI/DP connection flags, speaker/channel allocation, ELD-like sink manufacturer/product/port-description fields, hot-plug capability/enables, unsolicited-response tag/enable/force controls, multichannel pair enable/mute/channel-ID fields for 0/1 through 6/7 channels, IEC 60958 channel-status override bytes, LPIB snapshot/timer fields, coding type, format-change flags, keepalive enable/status, and per-audio-event interrupt masks/acks/status bits.

## Control Flow

This header has no runtime control flow. Runtime code supplies the sequencing:

1. DCN 3.1.2 display and DMUB code includes `dcn_3_1_2_offset.h` and `dcn_3_1_2_sh_mask.h`.
2. Register lists and helper macros paste register and field names into generated tokens such as `AZF0ENDPOINT2_AZALIA_F0_CODEC_PIN_CONTROL_CHANNEL_SPEAKER__CHANNEL_ALLOCATION_MASK`.
3. `FD_MASK` and `FD_SHIFT`-style macros place those constants into field tables or use them directly in register access helpers.
4. Driver or firmware-service code programs the addressed Azalia endpoint registers during audio-capability exposure, HDMI/DP audio setup, stream-format updates, hotplug/unsolicited-response handling, and status/interrupt processing.

The macros do not encode ordering requirements. Consumers must still sequence audio endpoint enablement, display-link setup, ELD/sink updates, converter stream assignment, channel-status programming, hotplug notification, interrupt clear/ack, and suspend/resume restoration correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing. It describes fields within hardware registers. The represented hardware state includes:

- Converter state for stream format, stream/channel identity, supported formats/rates, digital converter bits, striping, ramp control, GTC embedding, and GTC timing-delta reporting.
- Pin state for widget capability reporting, pin capability reporting, output enable, pin sense, HDMI/DP connection indication, speaker/channel allocation, supported audio descriptors, multichannel routing and mute controls, and lipsync/HBR response.
- Sink metadata state for manufacturer/product IDs, description length/content fragments, and DP/HDMI port identifiers.
- Notification and status state for unsolicited responses, forced responses, hotplug presence/capability/enables, digital-output status, LPIB snapshot/timer values, coding type, format-change bits, wireless-display identification, remote keepalive, and audio enable/disable/format-change interrupts.

Persistence is hardware-defined. Configuration-like fields normally retain values until modeset, endpoint reprogramming, display/audio reset, power gating, suspend/resume, or ASIC reset. Status, interrupt, hotplug, LPIB, format-change, keepalive, and force/ack fields may be read-only, sticky, self-clearing, write-one-to-clear, or sequencing-sensitive. The generated mask header only provides bit layout; it does not declare access type or side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.2 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h` for the corresponding register offsets and base-index selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/yellow_carp/yellow_carp_offset.h` and DCN base-address definitions for Yellow Carp/DCN 3.1 register addressing.
- Field helper macros such as `FD_MASK` and `FD_SHIFT` in the AMD display/DMUB register access layer.

The direct include site found in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`, which builds `dmub_srv_dcn31_regs` by combining DCN 3.1 offset constants with DCN 3.1.2 field masks and shifts. Broader integration is through AMDGPU display audio and DMUB service code that uses generated register tables and field macros for HDMI/DisplayPort audio endpoint programming.

This range is closely coupled to the adjacent offset and mask chunks. The line range begins after the start of endpoint 0 and ends before endpoint 4 is complete, so final file-level analysis must merge neighboring chunks before making complete claims about all Azalia endpoints.

## Risks And Edge Cases

- Shift/mask drift is the central risk. These are untyped constants, so a wrong mask or bit position can compile cleanly while corrupting unrelated hardware fields.
- Endpoint repetition is copy-sensitive. Endpoint 1 through endpoint 3 are complete and structurally similar, while endpoint 0 and endpoint 4 are partial in this chunk; a merge or generator error can affect only a specific display/audio endpoint.
- Some fields are side-effect-sensitive. Interrupt status/ack/mask bits, format-change flags, unsolicited-response force bits, hotplug controls, LPIB snapshot controls, and keepalive state may not tolerate blind read-modify-write patterns.
- Audio capability fields are externally visible through HDMI/DP audio behavior. Incorrect descriptor, supported-rate, channel allocation, or HBR fields can produce missing formats, wrong channel maps, audio dropouts, or broken receiver compatibility.
- Sink information and port ID fields must line up with link and ELD/EDID handling. Stale or incorrectly masked values can confuse audio device enumeration after hotplug, MST changes, or resume.
- Multichannel routing fields pack enable, mute, and channel IDs into repeated bit groups. Misprogramming one group can leave stereo working while 5.1/7.1 or HBR audio fails.
- This header does not identify access permissions. Callers must know which fields are read-only, write-only, W1C, sticky, or self-clearing from the hardware specification and surrounding driver logic.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC and DMUB code paths that include `dcn_3_1_2_sh_mask.h`; missing or renamed macros should fail during register-table and field-table construction.
- Mechanically verify that every complete register field in lines 54475-56841 has a consistent `__SHIFT`/`_MASK` pair, accounting for the artificial chunk boundaries at endpoint 0 and endpoint 4.
- Diff this range against AMD's authoritative DCN 3.1.2 register database and neighboring generated DCN headers where endpoint field layouts are expected to match.
- Exercise HDMI and DisplayPort audio on hardware that uses DCN 3.1.2/Yellow Carp paths: hotplug, modeset, suspend/resume, audio enable/disable, stream-format changes, stereo, multichannel, and HBR formats.
- Validate audio descriptors and channel allocation with receivers that report different ELD/EDID capabilities, including 2-channel-only sinks, 5.1/7.1 sinks, high sample-rate modes, and DP versus HDMI connections.
- Check unsolicited response and hotplug behavior through audio-device enumeration after monitor unplug/replug, MST topology changes, and resume.
- Watch kernel logs and user-visible audio diagnostics for missing HDMI/DP audio devices, format-change storms, stuck interrupts, channel-map errors, LPIB/timestamp anomalies, audio dropouts, or failures limited to one connector/endpoint.

## Cross-Chunk Notes

Previous chunks own the beginning of endpoint 0, including earlier converter and audio-widget capability fields. Later chunks continue endpoint 4 after `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` and should cover the rest of endpoint 4 plus any later endpoints. The final per-file research document should reconcile these boundaries before summarizing the complete `dcn_3_1_2_sh_mask.h` Azalia endpoint field map.

### subset-b-001825: lines 56842-59188

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 56842-59188

## Scope

This chunk covers a generated region of the DCN 3.1.2 shift/mask header. It contains only C preprocessor constants and generated grouping comments; there are no functions, structs, enums, storage objects, or executable statements in this slice.

The line range starts in the tail of `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE`, continues through the rest of output endpoint 4, covers complete output endpoint 5, output endpoint 6, and output endpoint 7 blocks, and then enters input endpoint 0 and the beginning of input endpoint 1. The range contains 2,040 `#define` entries: 1,018 `__SHIFT` definitions and 1,022 `_MASK` definitions. The mask count is higher because the range begins with six endpoint-4 multichannel masks whose shifts are in the previous chunk and ends after two input-endpoint-1 default-configuration shifts whose masks are in the next chunk.

The main hardware area represented here is Azalia function 0 display audio for DCN 3.1.2: HDMI/DisplayPort-style output pins/converters and the first two input endpoint register groups. The generated comments identify indexed register address blocks such as `azf0endpoint5_endpointind`, `azf0endpoint6_endpointind`, `azf0endpoint7_endpointind`, `azf0inputendpoint0_inputendpointind`, and `azf0inputendpoint1_inputendpointind`.

## Purpose

The purpose of this header region is to provide symbolic bit positions and masks for DCN 3.1.2 Azalia audio endpoint registers. AMDGPU display code can pair these field constants with the matching DCN 3.1.2 offset header and register-helper macros, avoiding hard-coded bit positions in code that programs or reads audio hardware state.

The output endpoint blocks describe converter format selection, stream/channel routing, digital converter flags, supported format and rate capability fields, pin capabilities, speaker/channel descriptors, sink identification, lip-sync and HBR state, hot-plug audio status, LPIB snapshots, channel-status overrides, remote keepalive, and audio enable/disable/format-change interrupt status. The input endpoint blocks describe a similar input-converter and input-pin contract, with input activity, infoframe status, and input-specific pin sense fields.

This file is a hardware contract rather than an algorithm. Its important behavior is the exact macro spelling and numeric bit layout consumed by ASIC-specific DCN 3.1 register tables and register-access helpers.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated preprocessor convention:

- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` gives a bit offset for output endpoint `n`.
- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>_MASK` gives the corresponding output endpoint field mask.
- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` and `_MASK` do the same for input endpoint `n`.
- Grouping comments name the hardware register, and `// addressBlock: ...` comments mark transitions between indexed endpoint blocks.

The partial endpoint 4 tail includes masks for multichannel slots `45` and `67`, then complete pin-side groups for:

- `RESPONSE_LIPSYNC`, with 8-bit video and audio lip-sync fields.
- `RESPONSE_HBR`, with HBR capable and enable bits.
- `SINK_INFO0` through `SINK_INFO8`, covering manufacturer/product IDs, sink-description length, two 32-bit port-ID words, and 18 bytes of sink description.
- `HOT_PLUG_CONTROL`, with clock-gating disable, clock-on state, and high-bit `AUDIO_ENABLED`.
- `UNSOLICITED_RESPONSE_FORCE`, with a 26-bit payload and force bit.
- `RESPONSE_CONFIGURATION_DEFAULT`, with sequence, association, misc, color, connection type, default device, location, and port-connectivity fields.
- `MULTICHANNEL_ENABLE2`, `MULTICHANNEL_MODE`, `CODEC_CS_OVERRIDE_0` through `_8`, association info, digital-output status, LPIB snapshot/LPIB/timer snapshot, coding type, format-change fields, wireless display identification, remote keepalive, and audio enable/disable/format-change interrupt status.

Output endpoints 5, 6, and 7 repeat the complete endpoint pattern. Important register families include:

- Converter parameters: `CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `PARAMETER_STREAM_FORMATS`, and `PARAMETER_SUPPORTED_SIZE_RATES`.
- Converter controls: `CONTROL_CONVERTER_FORMAT`, `CONTROL_CHANNEL_STREAM_ID`, `CONTROL_DIGITAL_CONVERTER`, `STRIPE_CONTROL`, `CONTROL_RAMP_RATE`, `CONTROL_GTC_EMBEDDING`, and GTC counter delta/min/max.
- Pin parameters and controls: `CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `CODEC_PIN_PARAMETER_CAPABILITIES`, unsolicited response, pin sense, widget control, channel speaker, audio descriptors 0-13, multichannel enable registers, lip-sync, HBR, sink info, hot-plug control, forced unsolicited response, default configuration, channel-status overrides, association info, digital output status, LPIB controls, coding type, format changed, wireless display identification, and remote keepalive.
- Per-endpoint audio status/interrupt registers: `AUDIO_ENABLE_STATUS`, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS`.

Input endpoint 0 is complete in this chunk. Its register families include:

- Input converter capability, format, channel/stream ID, digital converter flags, supported stream formats, and supported size/rate bitmaps.
- Input pin widget and pin capability fields, including impedance sense, trigger-required, jack detect, headphone drive, output/input capability, HDMI, VREF, EAPD, and DisplayPort capability bits.
- Input pin controls for unsolicited response, input pin sense, widget input enable, multichannel slots 0-7, HBR, channel allocation, hot-plug audio state, forced unsolicited response, default configuration, LPIB snapshot/LPIB/timer snapshot, input activity/status control, and infoframe fields.

Input endpoint 1 starts with the same input-converter and input-pin pattern and reaches the beginning of `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`; the rest of that register and later input-endpoint-1 registers are outside this line range.

Common field families in the chunk include:

- Audio format fields: number of channels, bits per sample, sample base divisor/multiple/rate, and stream type.
- Routing fields: 4-bit channel IDs and 4-bit stream IDs.
- Digital converter flags: `DIGEN`, validity, validity configuration, preemphasis, copy, non-audio, professional, level, category code, and keepalive.
- Capability bitmaps: full-width stream formats plus rate and bit-depth capabilities.
- Multichannel packed slots: enable, mute, and 4-bit channel IDs, either as `01/23/45/67` output pairs or individual input slots split across two registers.
- Event/status fields: unsolicited response tag/enable/force, HBR capability/enable, hot-plug clock state, audio enabled, audio enabled/disabled/format-changed interrupt masks/acks, LPIB snapshots, input activity, and infoframe validity.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time token resolution:

1. DCN 3.1 display code includes `dcn_3_1_2_offset.h` and `dcn_3_1_2_sh_mask.h`.
2. Register tables and helpers concatenate register and field tokens to find matching `__SHIFT` and `_MASK` macros.
3. Runtime MMIO or indexed-register helper code uses those constants to pack write values, preserve neighboring fields during updates, or extract status fields from hardware reads.

The declaration order reflects hardware organization. The slice first finishes output endpoint 4, then walks output endpoints 5, 6, and 7 in order, then starts input endpoints 0 and 1. Within each register group, shift definitions normally precede mask definitions; the exceptions are caused by this chunk starting and ending mid-register group.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes where state lives in DCN 3.1.2 Azalia endpoint hardware registers.

Writable converter and pin-control fields can represent programmed audio format, stream/channel association, digital converter behavior, speaker/channel routing, multichannel enablement and mute state, HBR enablement, hot-plug audio enablement, channel-status overrides, forced unsolicited responses, GTC embedding, LPIB snapshot locking, and interrupt mask/ack state. Read-only or hardware-updated fields can represent capability declarations, sink identity, pin sense, lip-sync values, LPIB/timer snapshots, audio enable state, format-change status, input activity, and infoframe validity/data.

Persistence is hardware-defined. Programmed control fields may remain until reprogramming, display/audio block reset, suspend/resume restore, or ASIC reset. Capability and status fields may change with connector hot-plug, link training, audio stream changes, input activity, sink EDID/ELD-derived state, or DCN power management. The header does not encode access type, reset value, volatile behavior, clear-on-read, or write-one-to-clear semantics; consumers must rely on the hardware specification and established AMD display register helpers.

## Dependencies And Integration Points

This chunk depends on the matching generated DCN 3.1.2 register offset file:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h` supplies MMIO and indexed-register offsets such as the `ixAZF0ENDPOINT<n>_...` and `ixAZF0INPUTENDPOINT<n>_...` names corresponding to the fields in this shift/mask header.
- The offset header and shift/mask header must come from the same register database. A field macro without a matching register offset, or a register offset with stale field masks, breaks the register-helper contract.

Observed direct include users in the DCN 3.1 tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`, which includes `yellow_carp_offset.h`, `dcn_3_1_2_offset.h`, and this shift/mask header, then builds DMUB register shift and mask tables with `FD_MASK` and `FD_SHIFT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c`, which includes the same register headers for DCN31 interrupt-service setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which includes the same register headers while constructing DCN31 resources. That file declares seven audio register table entries, `audio_regs(0)` through `audio_regs(6)`, while the resource capability block sets `num_audio = 5`; generated endpoints and instantiated audio resources are related but not identical concepts.

The broader AMD display register framework is the main integration point. Helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT` rely on exact macro suffixes. Missing or renamed symbols generally fail at compile time; incorrect numeric masks or shifts can compile cleanly and only surface as wrong hardware programming or status interpretation.

## Risks And Edge Cases

- The range starts mid-register: endpoint 4 multichannel `45` and `67` shift definitions are in the previous chunk, while only their masks appear here.
- The range ends mid-register: input endpoint 1 default-configuration `SEQUENCE` and `DEFAULT_ASSOCIATION` shifts appear here, but the remaining fields and masks are in the next chunk.
- The output endpoint blocks are highly repetitive. Endpoint-specific generator drift can be hard to notice because most lines differ only by `AZF0ENDPOINT5`, `AZF0ENDPOINT6`, or `AZF0ENDPOINT7`.
- Several high-bit fields use bit 31, including `AUDIO_ENABLED`, `PRESENCE_DETECT`, and audio interrupt status/ack fields. Wrong signedness or width assumptions can corrupt status interpretation.
- Full-width fields such as stream format bitmaps, LPIB, timer snapshots, port IDs, GTC counter deltas, and wireless display identification use `0xFFFFFFFFL`; consumers should use unsigned 32-bit register values.
- Capability, control, status, and interrupt registers all use the same macro style. This header does not prevent writing read-only capability/status fields or mishandling write-one-to-clear or mask/ack behavior.
- `UNSOLICITED_RESPONSE_FORCE` can synthesize event payloads. Incorrect writes could create misleading hot-plug, pin-response, input-activity, or format-change notifications.
- Multichannel registers pack several enable, mute, and channel-ID fields into one word. A wrong mask or wrong endpoint prefix can alter neighboring channel state while still compiling.
- Cross-generation reuse is risky. Many DCN and DCE headers contain near-identical Azalia field names, but DCN 3.1.2 code must keep the `dcn_3_1_2_offset.h` and `dcn_3_1_2_sh_mask.h` pair aligned.
- Generated endpoint count can exceed the product's exposed audio count. Resource configuration, connector topology, BIOS straps, and SKU limits determine which generated endpoints are actually active.

## Test Signals

Useful validation is mostly build-time and hardware-integration oriented:

- Build AMDGPU display code for a DCN31/DCN 3.1.2-enabled configuration to catch missing macro names in register-helper expansions.
- Preprocess representative users of `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to ensure token concatenation resolves to the intended `AZF0ENDPOINT4` through `AZF0ENDPOINT7` and `AZF0INPUTENDPOINT0`/`1` macros.
- Compare this slice against `dcn_3_1_2_offset.h` to verify that every endpoint indexed register named in this chunk has matching register offsets.
- Compare generated masks and shifts against the authoritative AMD register database for DCN 3.1.2, especially high-bit status fields, full-width fields, GTC/LPIB fields, sink-info bytes, and packed multichannel slots.
- Exercise HDMI/DisplayPort audio bring-up on DCN31 hardware and verify converter format programming, stream/channel ID routing, digital converter flags, speaker allocation/audio descriptors, sink info, HBR state, lip-sync responses, and hot-plug audio enabled state.
- Test hotplug, audio enable/disable, audio format changes, suspend/resume, and display reset paths while checking that driver state is reprogrammed or re-read consistently for converter state, channel-status overrides, multichannel routing, LPIB snapshots, input status, and unsolicited response controls.
- Validate interrupt behavior around `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS`, including mask and ack fields.
- For input endpoints, validate input activity, channel layout, infoframe valid/data, and input pin sense transitions if the platform exposes these paths.

## Open Cross-Chunk Questions

- The merge lane should combine this with neighboring chunks to present endpoint 4 and input endpoint 1 as complete logical blocks, because both are split at this chunk boundary.
- Whole-file analysis should reconcile generated endpoint blocks with DCN31 resource limits such as `audio_regs[]` entries and `num_audio = 5`.
- Whole-file analysis should compare this DCN 3.1.2 Azalia layout with nearby generated headers such as DCN 3.1.5/3.1.6 and DCE 12.0 to distinguish intentional register-database reuse from accidental drift.

### subset-b-001826: lines 59189-60782

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 59189-60782

## Scope

This chunk is the final 1,594-line slice of the generated AMD DCN 3.1.2 register shift/mask header. It contains only preprocessor constants and generated grouping comments; there are no functions, structs, enums, storage objects, or executable statements in this range.

The range starts in the middle of `AZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`, continues through the tail of input endpoint 1, then covers complete generated `azf0inputendpoint2_inputendpointind` through `azf0inputendpoint7_inputendpointind` blocks. It ends with the header guard `#endif`. The slice contains 1,430 `#define` entries: 714 `__SHIFT` definitions and 716 `_MASK` definitions. The mask count is larger because the first two shift fields for endpoint 1's default-configuration register are in the previous chunk, while their masks remain in this chunk.

This file sits under a local `ceph-client` source mirror, but the content is AMDGPU Display Core hardware metadata, not Ceph filesystem logic.

## Purpose

The purpose of this header region is to give DCN 3.1.2 display-audio code symbolic bit positions and masks for Azalia/HD-audio function 0 input endpoint registers. Runtime code combines these constants with the matching DCN 3.1.2 offset/index header and AMD display register helpers to pack fields for writes or extract fields from register reads without hard-coded bit arithmetic.

The covered register fields describe HDMI/DisplayPort-style audio input converter and input pin state. They model converter widget capabilities, stream format selection, channel and stream IDs, digital converter flags, stream-format and size/rate capability bitmaps, input pin capabilities, unsolicited responses, pin sense, widget input enablement, multichannel routing, HBR capability/enablement, channel allocation, hot-plug audio state, forced unsolicited-response payloads, HDA pin default configuration, LPIB snapshots, input activity/status, and decoded audio infoframe summary data.

The behavioral contract here is the exact generated macro namespace and numeric bit layout. Changing a macro value is equivalent to changing the hardware register ABI for DCN 3.1.2.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated preprocessor convention:

- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` gives the bit offset for an input endpoint field.
- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>_MASK` gives the field mask for the same field.
- Generated comments such as `// addressBlock: azf0inputendpoint2_inputendpointind` group fields by indexed input-endpoint block.
- Generated comments such as `//AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME` group fields by logical indexed register.

The endpoint 1 tail includes the latter part of `RESPONSE_CONFIGURATION_DEFAULT`, then `LPIB_SNAPSHOT_CONTROL`, `LPIB`, `LPIB_TIMER_SNAPSHOT`, `INPUT_STATUS_CONTROL`, and `INFOFRAME`.

Input endpoints 2 through 7 each repeat a complete 23-register input endpoint layout:

- `AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`
- `AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`
- `AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`
- `AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`
- `AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS`
- `AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES`
- `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`
- `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_CAPABILITIES`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_INPUT_PIN_SENSE`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_WIDGET_CONTROL`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE2`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_CHANNEL_ALLOCATION`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE_FORCE`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB_TIMER_SNAPSHOT`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME`

Important field families:

- Converter capability fields: channel capability, amplifier presence, amplifier override, format override, stripe, processing widget, unsolicited response capability, connection list, digital, power control, LR swap, widget delay, and widget type.
- Converter format fields: number of channels, bits per sample, sample base divisor, sample base multiple, sample base rate, and stream type.
- Routing fields: 4-bit channel ID and 4-bit stream ID.
- Digital converter fields: `DIGEN`, validity, validity configuration, preemphasis, copy, non-audio, professional, level, category code, and keepalive.
- Capability bitmaps: full-width stream formats plus audio rate and bit-depth capability fields.
- Pin capability fields: impedance sense, trigger-required, jack detection, headphone drive, output/input capability, balanced I/O, HDMI, VREF control, EAPD, and DisplayPort.
- Event and status fields: unsolicited response tag/enable, forced unsolicited response payload/force bit, pin sense presence detect, input activity, channel layout, and infoframe validity.
- Multichannel fields: two packed registers cover slots 0-7, with each slot exposing enable, mute, and 4-bit channel ID fields.
- HBR, channel, and hot-plug fields: HBR capability/enable, 8-bit channel allocation, clock-gating disable, clock-on state, and high-bit `AUDIO_ENABLED`.
- Default pin configuration fields: sequence, default association, misc, color, connection type, default device, location, and port connectivity.
- LPIB fields: snapshot lock, cyclic-buffer wrap count, full-width LPIB, and full-width LPIB timer snapshot.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time symbol resolution:

1. DCN 3.1.2 consumers include `dcn_3_1_2_offset.h` and `dcn_3_1_2_sh_mask.h`.
2. Register helper macros concatenate register and field tokens to find matching `__SHIFT` and `_MASK` definitions.
3. Runtime code uses those constants when reading or writing the Azalia input endpoint indexed-register data value.

The declaration order mirrors hardware organization. The chunk finishes endpoint 1, then proceeds through input endpoints 2, 3, 4, 5, 6, and 7 in ascending endpoint order. Within each register group, generated shift definitions appear before mask definitions for the same fields.

Azalia endpoint access is indirect: software selects an endpoint indexed register and then reads or writes a data register. This header describes the bit layout of the data values, not the sequencing policy for the index/data transactions.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes hardware state in DCN 3.1.2 Azalia input endpoint registers.

Writable control fields can represent audio input format, stream/channel binding, digital converter behavior, input widget enablement, multichannel routing, HBR enablement, channel allocation, hot-plug audio state, unsolicited-response setup, forced event generation, and LPIB snapshot locking. Capability and status fields can represent advertised widget/pin capabilities, supported stream formats and rates, pin presence, input activity, infoframe contents, LPIB snapshots, timer snapshots, and clock/audio enabled state.

Persistence is hardware-defined. Programmed fields generally remain until rewritten, reset by the display/audio block, restored during suspend/resume, or cleared by a broader ASIC reset. Capability and live status fields may change with sink topology, hot-plug state, audio activity, or display/audio power state. The shift/mask header does not encode access type, volatility, reset values, read-only behavior, clear-on-read behavior, or write-one-to-clear semantics.

## Dependencies And Integration Points

This chunk depends on the matching generated DCN 3.1.2 offset header:

- `dcn_3_1_2_offset.h` defines direct MMIO index/data windows for `regAZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` through `regAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_ENDPOINT_DATA`, with base index `2`.
- The same offset header defines the indexed `ixAZF0INPUTENDPOINT<n>_...` selectors for the logical registers described here. For each endpoint, converter controls occupy indexed offsets `0x0001` through `0x0006`, input pin controls include `0x0020` through `0x0024`, multichannel/HBR controls occupy `0x0036` through `0x0038`, channel/hotplug/default controls occupy `0x0053` through `0x0056`, and LPIB/status/infoframe controls occupy `0x0064` through `0x0068`.
- `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, `drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c`, and `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c` include `dcn_3_1_2_offset.h` and `dcn_3_1_2_sh_mask.h`. Those files are the DCN 3.1 generation integration points for generated register symbols.
- `dcn31_resource.c` reports `num_audio = 5`, so the generated register database exposes more input endpoint instances than every resource configuration necessarily instantiates as live audio resources.
- Shared display audio code such as `drivers/gpu/drm/amd/display/dc/dce/dce_audio.c` implements Azalia endpoint index/data programming for display audio. The input endpoint constants in this chunk must remain compatible with that broader indirect-register model even when the most visible resource table entries use output endpoint macros.

The main integration contract is token naming. Helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, `FD_SHIFT`, `SF`, and `SRI` rely on exact macro suffixes. A missing or renamed symbol usually fails at compile time; an incorrect numeric mask or shift can compile and then misprogram hardware.

## Risks And Edge Cases

- The chunk starts mid-register. Endpoint 1's `RESPONSE_CONFIGURATION_DEFAULT` register comment plus `SEQUENCE__SHIFT` and `DEFAULT_ASSOCIATION__SHIFT` are in the previous chunk, while this slice contains the remaining shifts and all masks for that register.
- This is the final chunk of `dcn_3_1_2_sh_mask.h` and ends with `#endif`. The merge lane should not treat the guard close as a hardware register definition.
- The input endpoint blocks are highly repetitive. Generator or hand-edit drift affecting only one endpoint can be hard to spot because most lines differ only by endpoint number.
- Several fields sit at bit 31: `PRESENCE_DETECT`, `AUDIO_ENABLED`, and `INFOFRAME_VALID`. Wrong signedness or wrong high-bit masks can produce status interpretation failures.
- Full-width masks use `0xFFFFFFFFL` for fields such as stream formats, LPIB, and LPIB timer snapshots. Consumers should use appropriate unsigned 32-bit register types and avoid sign-extension assumptions.
- Capability, status, and control fields use the same macro style. The header does not prevent a caller from writing capability/status registers or from missing special read/clear semantics if the hardware assigns them.
- `UNSOLICITED_RESPONSE_FORCE` can synthesize a response payload. Bad writes can create misleading audio, hot-plug, input-activity, or pin-response events.
- Multichannel enable registers pack four channel slots per word. An incorrect mask, endpoint prefix, or read-modify-write sequence can alter neighboring enable, mute, or channel-ID fields.
- Generated endpoint count and active audio resource count are not identical. DCN 3.1.2 exposes endpoint 0-7 register windows, while DCN 3.1 resource capabilities in this tree report five audio resources.
- Cross-generation reuse is risky. DCN 3.1.2 field names resemble DCN 3.0.x and other DCN headers, but offset and shift/mask headers must be paired by the same ASIC generation.

## Test Signals

Useful validation is mostly build-time and hardware-integration oriented:

- Build AMDGPU display code for a DCN 3.1/DCN 3.1.2-enabled configuration to catch unresolved generated macro names.
- Preprocess representative users of `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, `FD_SHIFT`, `SF`, and `SRI` to ensure token concatenation resolves to the expected `AZF0INPUTENDPOINT*` macros.
- Compare this slice against `dcn_3_1_2_offset.h` to verify every input endpoint indexed register selector has matching field shift/mask definitions.
- Compare the generated field values against the authoritative AMD register database for DCN 3.1.2, especially high-bit fields, full-width fields, and packed multichannel fields.
- Exercise HDMI/DisplayPort audio bring-up on DCN 3.1-family hardware and verify converter format, stream/channel IDs, digital converter state, channel allocation, HBR state, hot-plug audio enablement, and input status/infoframe reporting.
- Test hot-plug, audio enable/disable, audio format changes, suspend/resume, and display reset paths while checking that endpoint state is reprogrammed or re-read consistently.
- Validate endpoint-instance symmetry for endpoints 2 through 7 while preserving the endpoint-specific prefixes and matching index/data windows.

## Open Cross-Chunk Questions

- The merge lane should combine this with the previous chunk before describing endpoint 1 as complete, because this chunk begins after the start of endpoint 1's default-configuration register.
- Whole-file research should reconcile generated input endpoint coverage with DCN 3.1.2 resource limits and any product-specific audio endpoint disablement.
- Whole-file research should compare the final DCN 3.1.2 Azalia input endpoint layout with adjacent DCN 3.1 and DCN 3.0.x generated headers to distinguish intended register-database continuity from accidental divergence.
