# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001897`: lines 1-2508, `Docs/researches/chunks/subset-b-001897_research.md`
- `subset-b-001898`: lines 2509-4798, `Docs/researches/chunks/subset-b-001898_research.md`
- `subset-b-001899`: lines 4799-7213, `Docs/researches/chunks/subset-b-001899_research.md`
- `subset-b-001900`: lines 7214-9828, `Docs/researches/chunks/subset-b-001900_research.md`
- `subset-b-001901`: lines 9829-12382, `Docs/researches/chunks/subset-b-001901_research.md`
- `subset-b-001902`: lines 12383-14898, `Docs/researches/chunks/subset-b-001902_research.md`
- `subset-b-001903`: lines 14899-17419, `Docs/researches/chunks/subset-b-001903_research.md`
- `subset-b-001904`: lines 17420-19930, `Docs/researches/chunks/subset-b-001904_research.md`
- `subset-b-001905`: lines 19931-22447, `Docs/researches/chunks/subset-b-001905_research.md`
- `subset-b-001906`: lines 22448-24952, `Docs/researches/chunks/subset-b-001906_research.md`
- `subset-b-001907`: lines 24953-27463, `Docs/researches/chunks/subset-b-001907_research.md`
- `subset-b-001908`: lines 27464-30059, `Docs/researches/chunks/subset-b-001908_research.md`
- `subset-b-001909`: lines 30060-32529, `Docs/researches/chunks/subset-b-001909_research.md`
- `subset-b-001910`: lines 32530-34962, `Docs/researches/chunks/subset-b-001910_research.md`
- `subset-b-001911`: lines 34963-37371, `Docs/researches/chunks/subset-b-001911_research.md`
- `subset-b-001912`: lines 37372-39766, `Docs/researches/chunks/subset-b-001912_research.md`
- `subset-b-001913`: lines 39767-42179, `Docs/researches/chunks/subset-b-001913_research.md`
- `subset-b-001914`: lines 42180-44523, `Docs/researches/chunks/subset-b-001914_research.md`
- `subset-b-001915`: lines 44524-46938, `Docs/researches/chunks/subset-b-001915_research.md`
- `subset-b-001916`: lines 46939-49518, `Docs/researches/chunks/subset-b-001916_research.md`
- `subset-b-001917`: lines 49519-51930, `Docs/researches/chunks/subset-b-001917_research.md`
- `subset-b-001918`: lines 51931-54346, `Docs/researches/chunks/subset-b-001918_research.md`
- `subset-b-001919`: lines 54347-56952, `Docs/researches/chunks/subset-b-001919_research.md`
- `subset-b-001920`: lines 56953-59328, `Docs/researches/chunks/subset-b-001920_research.md`
- `subset-b-001921`: lines 59329-61649, `Docs/researches/chunks/subset-b-001921_research.md`
- `subset-b-001922`: lines 61650-62727, `Docs/researches/chunks/subset-b-001922_research.md`

## Chunk Research

### subset-b-001897: lines 1-2508

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 1-2508

## Scope

This chunk is the opening portion of AMDGPU DCN 3.1.6 generated register metadata. It contains copyright/license text, the header guard, and C preprocessor constants for register-field shifts and masks. It is not executable code and defines no functions, structs, enums, or runtime storage.

The exact range spans line 1 through line 2508 of `dcn_3_1_6_sh_mask.h`. It starts at the file prologue and enters these hardware address blocks:

- HDA/Azalia controller, endpoint, input endpoint, root, and output stream descriptor blocks.
- Legacy VGA register windows in `dce_dc_mmhubbub_vga_dispdec`.
- DCCG display clock generator DFS and clock-control blocks.
- Two DCCG DC perfmon blocks.
- The beginning of the DMCU block, ending mid-register inside `DMCU_INTERRUPT_STATUS`.

The chunk has 2,101 `#define` lines. Each meaningful definition follows the generated AMD register convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field bit mask.

## Purpose

The purpose of this chunk is to publish DCN 3.1.6 bitfield layout for low-level display, audio, clocking, diagnostics, and microcontroller registers. The companion address header names register addresses; this shift/mask header tells AMDGPU display code how to pack and unpack individual fields for memory-mapped register access.

Major covered areas:

- `AZCONTROLLER0` and partial `AZCONTROLLER1`: HDA controller capability, version, global control/status, wake/status, stream interrupt masks/status, wall-clock, CORB/RIRB base address and pointer fields, immediate command/response registers, and DMA position buffer fields.
- `AZENDPOINT*`, `AZINPUTENDPOINT*`, and `AZROOT*`: immediate command data/index register fields for HDA codec endpoint/root interactions.
- `AZSTREAM0_1` through `AZSTREAM7_1`: replicated HDA output stream descriptor controls, cyclic buffer state, last valid index, FIFO size, sample format, buffer descriptor list base addresses, and link-position aliases.
- Legacy VGA fields: `VGA_MEM_*_PAGE_ADDR`, `CRTC8_*`, `GENFC_*`, `GENS*`, `ATTR*`, `GENMO_*`, `SEQ8_*`, `DAC_*`, and `GRPH8_*`.
- DCCG clocking: `DENTIST_DISPCLK_CNTL`, PHY PLL pixel clock resync controls, DP/DTB/DPP/DSC/HDMI/audio DTO phase and modulo registers, clock source selectors, gate-disable controls, CGTT delay controls, soft reset, force-disable fields, pixel-rate controls for OTG0-OTG3, and vsync counter/latch controls.
- Perfmon: `DC_PERFMON0_*` and `DC_PERFMON1_*` counter selection, state, run/stop, interrupt, compare-value, and high/low counter fields.
- DMCU: reset/enable/status, firmware start/end/checksum fields, ERAM/IRAM host access, event trigger, internal interrupt status, static-screen interrupt controls, and the opening fields of DMCU interrupt status.

## Important Definitions

This header's API surface is macro-only. Driver code consumes the constants through AMD display register helpers such as generated `REG_GET`, `REG_SET`, and `REG_UPDATE` style macros rather than by linking symbols from this file.

Important groups in this chunk:

- HDA controller fields: `AZCONTROLLER0_GLOBAL_CAPABILITIES`, `AZCONTROLLER0_GLOBAL_CONTROL`, `AZCONTROLLER0_INTERRUPT_CONTROL`, `AZCONTROLLER0_INTERRUPT_STATUS`, `AZCONTROLLER0_STREAM_SYNCHRONIZATION`, CORB/RIRB registers, immediate command status, and DMA position buffer address fields define audio controller capabilities, reset/flush/unsolicited-response control, stream interrupt enable/status bits, command/response DMA ring programming, and position-buffer DMA.
- HDA stream descriptor fields: each `AZSTREAM*_1_OUTPUT_STREAM_DESCRIPTOR_*` group provides stream reset/run, interrupt enables, FIFO/descriptor error flags, FIFO readiness, stream number, cyclic buffer length, last-valid index, FIFO size, sample format, BDL base address, and link-position fields. The eight stream blocks use the same field layout.
- VGA compatibility fields: the VGA page, CRTC, sequencer, graphics, attribute, DAC, feature-control, miscellaneous-output, and status fields expose legacy display register state through the DCN register map.
- DCCG clock programming fields: `DENTIST_DISPCLK_CNTL`, `DISPCLK_FREQ_CHANGE_CNTL`, `DP_DTO*_PHASE`, `DP_DTO*_MODULO`, `DTBCLK_DTO*_PHASE`, `DTBCLK_DTO*_MODULO`, `DPPCLK*_DTO_PARAM`, `DSCCLK*_DTO_PARAM`, `HDMISTREAMCLK0_DTO_PARAM`, and audio DTO registers describe fractional clock generation and ramping.
- DCCG gate/source fields: `DCCG_GATE_DISABLE_CNTL`, `DCCG_GATE_DISABLE_CNTL2`, `DCCG_GATE_DISABLE_CNTL3`, `DCCG_GATE_DISABLE_CNTL4`, `DPSTREAMCLK_CNTL`, `SYMCLK32_*`, `HDMISTREAMCLK_CNTL`, `HDMICHARCLK0_CLOCK_CNTL`, and `PHY*SYMCLK_CLOCK_CNTL` describe source selection, enable/force-enable, and clock gating for display, DP, HDMI, PHY, DPP, DSC, DMCUB, AOM, and related clocks.
- OTG pixel-rate fields: `OTG0_PIXEL_RATE_CNTL` through `OTG3_PIXEL_RATE_CNTL` and `OTG*_PHYPLL_PIXEL_RATE_CNTL` encode DTO enable/status, add/drop pixel controls, half-rate output, FIFO error reporting, error counts, DTO division, and PHY PLL pixel-rate source selection.
- Vsync/time-base fields: `MILLISECOND_TIME_BASE_DIV`, `MICROSECOND_TIME_BASE_DIV`, `DCCG_VSYNC_CNT_CTRL`, `DCCG_VSYNC_CNT_INT_CTRL`, and `DCCG_VSYNC_OTG*_LATCH_VALUE` define timebase divisors, clock source selection, vsync counter control, per-OTG latch enable/trigger selection, interrupt status/clear/mask fields, and latched values.
- Perfmon fields: each `DC_PERFMON{0,1}` block defines event selection, counter value source, count mode, hardware stop/start controls, run enable, interrupt controls, active state, counted value type, counter state selectors, report count, count-off interrupt status/ack, compare-value interrupt status/clear/mask, and 64-bit high/low readback registers.
- DMCU fields: `DMCU_CTRL`, `DMCU_STATUS`, firmware address/checksum registers, ERAM/IRAM access control/data registers, `DMCU_EVENT_TRIGGER`, `DMCU_UC_INTERNAL_INT_STATUS`, `DMCU_SS_INTERRUPT_CNTL_STATUS`, and the visible portion of `DMCU_INTERRUPT_STATUS` describe host control of the display microcontroller, firmware memory windows, software/internal interrupts, static-screen interrupts, and power-domain event interrupts.

Generated field names ending in `_MASK_MASK`, such as `DCCG_VSYNC_CNT_INT_CTRL__DCCG_VSYNC_CNT_OTG0_LATCH_MASK_MASK` and `DC_PERFMON0_PERFCOUNTER_CNTL__PERFCOUNTER_OFF_MASK_MASK`, are intentional: the hardware field itself is named `*_MASK`, and the generator appends `_MASK` for the bit mask constant.

## Control Flow and State

There is no C control flow in this header. Runtime behavior is created by code that includes this file and applies the constants to register reads and writes. Typical usage is:

1. DC/AMDGPU code selects the DCN 3.1.6 register address for a hardware block.
2. It uses the matching `__SHIFT` and `_MASK` constants to insert or extract a field.
3. The write updates memory-mapped hardware state, or the read observes current hardware state.
4. Later reads check status, interrupt, pending, done, or error fields to complete the protocol.

The stateful hardware protocols represented in this chunk include:

- HDA command/response rings: CORB and RIRB base addresses, read/write pointers, size, DMA enable, reset, memory-error, response interrupt, and overrun fields persist in audio-controller hardware after programming.
- HDA output DMA streams: stream reset/run, BDL pointer, cyclic buffer length, last-valid index, format, FIFO readiness, and error flags control and report audio DMA stream execution.
- Clock programming and handshakes: DENTIST, DTO, pixel-rate, and frequency-ramp fields configure generated clocks; fields such as `*_CHGTOG`, `*_DONETOG`, `*_CHG_DONE`, `*_ENABLE_STATUS`, `DISPCLK_FREQ_RAMP_DONE`, and FIFO error counters report asynchronous clock transitions.
- Clock gating and reset state: DCCG gate-disable, soft-reset, force-disable, CGTT delay, and source-select fields persist as display-clock control state and directly affect whether downstream display/audio/PHY paths can run.
- Perfmon counters: perfmon run/stop, event selection, counter state, interrupt enable/status/ack, and high/low counter registers form a hardware measurement state machine.
- DMCU host control: reset/enable/wait/stop status, firmware address/checksum setup, ERAM/IRAM access windows, software events, internal interrupt status, and static-screen/DMCU interrupt clear bits represent host-visible microcontroller state.

## Dependencies and Integration Points

This file depends on the generated AMD ASIC register naming contract. It is useful only with the corresponding DCN 3.1.6 address header and the AMDGPU display register access layer.

Primary integration points:

- AMD DC register helpers that expect field shift/mask macros paired with register addresses.
- HDA/HDMI audio setup paths that initialize Azalia controller, codec immediate commands, stream descriptors, CORB/RIRB rings, and audio DTOs.
- Display clock generator code that programs DISPCLK, DPPCLK, DPREFCLK, DTBCLK, DSCCLK, PHY pixel clocks, HDMI stream clocks, and gate-disable or reset controls.
- Link/pipe timing code that uses OTG pixel-rate, DP DTO, DTB DTO, and vsync counter/latch fields.
- Diagnostics and performance tooling that configures DCCG perfmon counters and reads counter high/low values or compare interrupts.
- DMCU/DMCUB-related power, firmware, static-screen, and interrupt handling paths that touch the legacy DMCU register block.

The header itself has no persistence. Persistence is in hardware registers after MMIO writes and in the compiler output after macros are expanded into constants.

## Risks and Edge Cases

- Generated-header drift is high impact. A wrong mask or shift silently targets the wrong hardware bits and can break audio DMA, clock generation, display timing, diagnostics, DMCU control, or interrupt handling.
- Several fields share a bit position for status and clear semantics, for example DCCG vsync latch interrupt status/clear, DMCU static-screen occurred/clear, and DMCU interrupt occurred/clear fields. The header names the bits but does not encode write-one-to-clear or read-only/write-only semantics; caller sequencing must come from the register spec and driver conventions.
- Chunk boundaries are not semantic boundaries. This chunk starts cleanly at the file prologue but ends inside `DMCU_INTERRUPT_STATUS`: lines after 2508 contain the remaining masks and subsequent DMCU fields. The merge lane must combine adjacent chunks before making whole-register claims about `DMCU_INTERRUPT_STATUS`.
- `AZCONTROLLER0` is complete for the common controller fields in this range, while `AZCONTROLLER1` begins later and only includes the CORB/RIRB/immediate-command/DMA-position subset in this chunk. Absence of an `AZCONTROLLER1` field here should not be interpreted as absence from the full file or hardware.
- Repeated stream and clock blocks are easy to update inconsistently by hand. The source is generated; manual edits to one `AZSTREAM*_1`, `OTG*_PIXEL_RATE_CNTL`, `DC_PERFMON*`, or PHY clock family risk breaking replicated hardware instances.
- Many fields are full-width `0xFFFFFFFFL` counters, data windows, or address fragments; consumers must use the correct register width and must avoid signed arithmetic surprises when composing values in C.
- Address-alignment and unimplemented-bit fields in CORB/RIRB, BDL, and DMA position base addresses indicate reserved low bits. Callers must respect alignment requirements instead of assuming arbitrary byte addresses are accepted.

## Test Signals

There are no unit-testable functions in this chunk. Useful validation signals are compile-time, structural, and hardware-integration focused:

- Build coverage: AMDGPU/DC code that includes `dcn_3_1_6_sh_mask.h` should compile without undefined field macros for DCN 3.1.6 paths.
- Generated consistency checks: each mask should align with its shift and expected field width; replicated families such as `AZSTREAM0_1` through `AZSTREAM7_1`, `OTG0` through `OTG3`, PHY PLL resync controls, and `DC_PERFMON0`/`DC_PERFMON1` should retain matching layouts where hardware instances are replicated.
- Audio validation: HDMI/DP audio bring-up should exercise CORB/RIRB command response, immediate codec commands, stream descriptor DMA, BDL programming, position-buffer reporting, interrupts, and FIFO/descriptor error fields.
- Clock/timing validation: display mode set, clock switching, deep-color modes, DSC/DPP clock DTO programming, DP/DTB DTO programming, and pixel-rate changes should complete without FIFO errors and should observe expected `*_DONE`, `*_STATUS`, latch, and error-count behavior.
- Perfmon validation: configuring both DCCG perfmon blocks should produce monotonic high/low counter values, correct active state, and expected compare-value interrupt status/ack behavior.
- DMCU validation: firmware-memory access, reset/enable status, software/internal interrupt delivery, static-screen interrupt clear, and visible power-domain interrupt bits should behave as expected on hardware that still uses this DMCU block.

## Chunk Notes for Merge Lane

- The range covers 2,508 source lines and 2,101 `#define` lines.
- Address-block starts in this chunk are at lines 29, 281, 290, 299, 308, 321, 428, 517, 526, 535, 544, 606, 668, 730, 792, 854, 916, 978, 1040, 1064, 2043, 2181, and 2319.
- The largest definition families in this chunk are DCCG clock/control fields, DMCU fields, `AZCONTROLLER0`, the eight `AZSTREAM*_1` descriptors, the two `DC_PERFMON*` blocks, and OTG pixel-rate controls.
- This chunk has no local includes, typedefs, structs, enums, functions, or writable software state.

### subset-b-001898: lines 2509-4798

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 2509-4798

## Scope

This chunk is a generated DCN 3.1.6 register-field shift/mask slice. It contains only preprocessor constants and register/address-block comments: `_SHIFT` macros encode field bit positions and `_MASK` macros encode raw register bitmasks. There are no C functions, structs, enums, loops, branches, allocations, or direct MMIO accesses in this range.

The range starts in the middle of `DMCU_INTERRUPT_STATUS`, after earlier ABM/MCP/static-screen fields, and continues through legacy DMCU interrupt routing, DMCU command mailboxes, DMCU perfmon and DPRX interrupt routing, RBBMIF timeout/security fields, DC perfmon instance 2 fields, GPU timer readback fields, and the display interrupt status chain through the first field of `DISP_INTERRUPT_STATUS_CONTINUE18`. Neighboring chunks are needed for the complete file-level view of both the leading `DMCU_INTERRUPT_STATUS` register and the trailing continuation-18 register.

## Purpose And Hardware Surface

This header supplies the bit-layout ABI used by AMDGPU Display Core and DMUB support code for DCN 3.1.6 display hardware. Companion generated headers provide register offsets; this file provides masks and shifts consumed by register-helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WRITE`, and generated table builders.

Major hardware areas represented here:

- DMCU interrupt status and routing: ABM ready/update events, static-screen events, OTG range/timing update events, DCPG power-up/power-down events, vblank events, DMCU generic/internal/SCP/MCP events, DCIO DPCS TX events, host enable masks, uC enable masks, and XIRQ/IRQ selection masks.
- DMCU command and scratch registers: `DC_DMCU_SCRATCH`, ABM interrupt counters, firmware checksum byte-position sampling, uC clock-gating controls, master/slave command/data byte lanes, and mailbox interrupt/in-progress controls.
- DMCU perfmon interrupts: occurred/clear, route-to-uC, and XIRQ/IRQ-select fields for DMU, DIO, DCCG, HPO, HUBP0-7, HUBBUB, DPP0-7, writeback, DCCG perfmon2, MMHUBBUB, MPC, OPP, OPTC, HDA, and DSC0-5 counter events.
- DPRX interrupt routing: stream decode events for SD0P0/SD1P0, DPRX DPHY threshold/error/lock/alignment/deskw failure events, AUX/I2C/CPU/message-timeout events, plus enable and XIRQ/IRQ-select routing for those same receiver-side events.
- DMU RBBMIF security and timeout diagnostics: DMCUB RBBMIF security level/trust/source fields, timeout delay/hold configuration, timeout client decode status, timeout address/op/read-write/ack/mask fields, per-client timeout-disable bits for clients 0-38, and invalid-access status.
- DC perfmon instance 2: performance counter event/value selection, increment/run/restart/interrupt controls, counted-value and hardware-stop selectors, per-counter state readback, perfmon run state, counter-off interrupt control/status/ack/type, clock enable, high/low value readback, and current-value interrupt status/ack fields.
- IHC display interrupt status chain: top-level display interrupt aggregation for OPTC underflow, OTG snapshot/force/trigger/vsync/vtotal/vertical/DRR events, DIG fast-training and stream-disable events, HPD and HPDRX, AUX SW/LS/GTC events, I2C completion, RBBMIF timeout, DMCU and ABM signals, MCIF/DWB/WBSCL events, perfmon events, DCCG latches, MPCC stalls, VGA CRT, HUBBUB VM/timeout/compbuf events, DCPG domain events, HUBP vblank/vline/timeout/flip/flip-away events, and the continuation-bit linkage across status registers.

## Important Definitions

The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field least-significant bit.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bitmask in the register value.
- `// addressBlock: ...` comments group registers by hardware address block.
- `//<REGISTER>` comments group fields belonging to each register.

Important macro families in this chunk:

- `DMCU_INTERRUPT_STATUS`, `DMCU_INTERRUPT_STATUS_1`, `DMCU_INTERRUPT_STATUS_CONTINUE`, and `DMCU_INTERRUPT_STATUS_2` expose latched DMCU-side events and matching clear bits. Many occurred and clear fields intentionally share the same bit position and mask, making write-one-clear handling dependent on the caller's register helper sequence.
- `DMCU_INTERRUPT_TO_HOST_EN_MASK`, `DMCU_INTERRUPT_TO_UC_EN_MASK*`, and `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL*` define which DMCU-side events are exposed to the host, routed to the microcontroller, or selected as XIRQ/IRQ inputs. The continued variants extend routing for DCPG domains, DCIO DPCS TX errors, and DCIO DPCS TXA-TXG events.
- `DMCU_INT_CNT`, `DMCU_INT_CNT_CONTINUE`, `DMCU_INT_CNT_CONT2`, and `DMCU_INT_CNT_CONT3` provide packed 8-bit interrupt counters for ABM0-3 high-gain ready, local-store ready, and backlight-update events.
- `MASTER_COMM_*` and `SLAVE_COMM_*` define four byte lanes per command/data register plus interrupt and message-in-progress bits. Shared DCE ABM/DMCU helpers use similarly named fields to send legacy microcontroller commands such as ABM, backlight, PSR, PHY sync, and EDID-related commands.
- `DMCU_PERFMON_INTERRUPT_STATUS1..5`, `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK1..5`, and `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1..5` repeat the same occurred/clear, enable, and IRQ-select pattern across display performance monitor blocks.
- `DMCU_DPRX_INTERRUPT_STATUS1`, `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1`, and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1` cover DisplayPort receiver-side stream decode, physical layer, AUX, I2C, CPU, and message timeout interrupts for port 0.
- `DMCUB_RBBMIF_SEC_CNTL` is in the foreground-security address block and defines security level, trust level, and source ID fields for DMCUB RBBMIF traffic.
- `RBBMIF_*` registers cover timeout programming and diagnostics. `RBBMIF_TIMEOUT_DIS` and `_DIS_2` provide one bit per timeout client, while `RBBMIF_STATUS_FLAG` exposes state, read-timeout, FIFO empty/full, invalid-access flag, invalid-access type, and invalid-access address.
- `DC_PERFMON2_*` fields implement the second DC perfmon register set, including counter selection, run/stop policy, interrupt policy, state readback, current-value interrupt status/ack, and high/low result readout.
- `DC_GPU_TIMER_*` fields select and read GPU timer values aligned with D1-D6 vupdate, vstartup, and nominal-vsync timing positions.
- `DISP_INTERRUPT_STATUS` through `DISP_INTERRUPT_STATUS_CONTINUE17` define a linked interrupt summary chain. Bit 31 in each register indicates the next continuation register has pending status. Line 4798 begins `DISP_INTERRUPT_STATUS_CONTINUE18` with `AZ_PERFMON_COUNTER0_INTERRUPT__SHIFT`; the remaining fields are outside this chunk.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when DCN 3.1.6-specific tables combine these constants with matching offsets from `dcn_3_1_6_offset.h`, then shared display code performs MMIO reads/writes through register helpers.

Typical runtime flow:

1. DCN316 resource, DMUB, interrupt, ABM, DMCU, perfmon, or hardware-sequencing code selects a register offset from a generated register table.
2. Register helpers use this header's masks and shifts to pack fields, decode status bits, perform read/modify/write updates, or write clear/ack bits.
3. The hardware side latches interrupt state, routes events to host/uC/IRQ paths, advances mailbox handshakes, updates counters, reports timeout diagnostics, or returns timer/perfmon values.

The state represented here is hardware register state, not persistent driver-owned memory:

- Persistent configuration includes interrupt routing masks, XIRQ/IRQ selection bits, timeout delay/hold controls, per-client RBBMIF timeout-disable policy, DMCUB RBBMIF security/trust/source attributes, DMCU clock-gating controls, mailbox command/data bytes, perfmon event/run/interrupt selection, and GPU timer read selectors.
- Volatile readback includes interrupt occurred bits, ABM interrupt counters, mailbox in-progress state, RBBMIF timeout clients, timeout address/op/read-write status, RBBMIF FIFO/invalid-access state, perfmon counter state and values, current-value interrupt status, GPU timer reads, and display interrupt summary-chain bits.
- Side-effecting fields include clear, ack, and interrupt-mask bits in DMCU status, DPRX status, perfmon status, RBBMIF timeout status, and DC perfmon current-value interrupt registers. Because many clear/ack fields share bit positions with status fields, broad writes or stale read/modify/write values can clear diagnostics unintentionally.

## Dependencies And Integration Points

This chunk depends on generated-name consistency across the DCN 3.1.6 register-header family. It is paired with `dcn_3_1_6_offset.h` and consumed by DCN316 display code through macro-expanded register and mask tables.

Primary integration points include:

- `display/dmub/src/dmub_dcn316.c` includes this header and `dcn_3_1_6_offset.h` to build `dmub_srv_dcn316_regs`. The table stores DCN31-family DMUB register offsets plus field masks/shifts for the shared DMUB service layer.
- `display/dmub/src/dmub_dcn31.c` uses the resulting field tables for DMUB reset, boot, secure-region programming, inbox/outbox pointer management, GPINT acking, firmware status scratch reads, debug collection, and interrupt enable/ack handling.
- `display/dc/resource/dcn316/dcn316_resource.c` includes this header to populate DCN316 resource tables. The hardware sequencer register list includes `RBBMIF_TIMEOUT_DIS` and `RBBMIF_TIMEOUT_DIS_2`, and the mask/shift lists feed shared DCN31 hardware sequencing and power-management logic.
- Shared DCE/DMCU/ABM helpers (`display/dc/dce/dce_dmcu.*`, `dce_abm.*`) use `MASTER_COMM_CMD_REG`, `MASTER_COMM_DATA_REG*`, and `DMCU_INTERRUPT_TO_UC_EN_MASK` style fields to send DMCU commands and route DMCU events. On DCN316, DMUB is the primary firmware path, but generated DMCU definitions remain part of the register ABI and shared code surface.
- Interrupt services and display-core IRQ mapping depend on the IHC summary-chain fields for HPD/HPDRX, vblank/vline/vupdate-related OTG events, page-flip/HUBP events, AUX completion/GTC events, DMCU/ABM events, RBBMIF timeout, and perfmon interrupts. The continuation bit at bit 31 is part of the hardware's interrupt traversal contract.
- Perfmon, diagnostics, and debug tooling can use DMCU perfmon interrupt fields, DC perfmon2 fields, RBBMIF timeout status, and GPU timer registers to observe display pipeline health, counter thresholds, timeout causes, and timestamp alignment.

Because this file is only macro definitions, a missing macro usually fails at compile time where referenced. Incorrect numeric masks or shifts generally compile successfully but can misroute interrupts, lose clear/ack operations, corrupt security/timeout policy, or decode volatile diagnostics incorrectly at runtime.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.6 hardware register specification is the main risk. Wrong shifts/masks in this range affect interrupt delivery, interrupt clearing, mailbox byte packing, perfmon programming, timeout diagnosis, GPU timer selection, and DMUB/RBBMIF security policy.
- The chunk begins and ends inside logical register families. Merge/reconciliation should combine it with adjacent chunks before making final statements about full `DMCU_INTERRUPT_STATUS` and `DISP_INTERRUPT_STATUS_CONTINUE18` coverage.
- The DMCU interrupt routing blocks are highly repetitive across status, enable, and XIRQ/IRQ-select registers. Copy-generation mistakes can leave a field name valid but mapped to the wrong event, causing only specific power-domain, vblank, static-screen, ABM, or DCIO paths to fail.
- Occurred/clear and status/ack fields commonly share the same bit. Callers must treat them as side-effecting write-one-clear/write-one-ack fields, not ordinary persistent configuration bits.
- The display interrupt status chain relies on bit 31 continuation fields. If any continuation mask or shift is wrong, interrupt service code can stop scanning too early or chase the wrong summary state, leading to lost HPD, AUX, vblank, flip, underflow, timeout, or perfmon events.
- RBBMIF timeout-disable masks span 39 clients across two registers. Off-by-one client mapping can hide real timeouts or leave noisy clients enabled, which affects display hang diagnosis and recovery.
- Mailbox byte-lane fields are packed. Incorrect byte shifts in `MASTER_COMM_*` or `SLAVE_COMM_*` can transform a valid command into a different firmware command or corrupt command parameters.
- DC perfmon2 fields mix configuration, run state, current-value interrupt status, acks, high/low values, and read selectors. Broad updates risk changing counter source or clearing threshold events while reading values.
- Some macro families describe legacy DMCU-facing paths even on DMUB-era hardware. Consumers must confirm which firmware path owns a register before adding new runtime uses.

## Test Signals

Useful validation combines generated-header checks, build coverage, and hardware/runtime interrupt tests:

- Build AMDGPU Display Core with DCN316 enabled and ensure all `dcn_3_1_6_sh_mask.h` names referenced by `dmub_dcn316.c`, `dcn316_resource.c`, shared DMUB, DMCU/ABM, hardware sequencing, and IRQ code resolve.
- Run generated-header consistency checks that every in-scope field has matching `_SHIFT` and `_MASK` definitions where expected, masks fit in 32 bits, fields do not overlap unexpectedly inside each register, and repeated register families keep event ordering aligned.
- Compare this range against the authoritative DCN 3.1.6 register specification, especially DMCU interrupt route/clear fields, DPRX events, RBBMIF timeout client numbering, DC perfmon2 fields, and `DISP_INTERRUPT_STATUS_CONTINUE*` continuation bits.
- Exercise HPD/HPDRX, AUX software done, AUX link-service done, AUX GTC lock/error, DC I2C software done, vblank/vline/vupdate/DRR, page-flip/flip-away, underflow, WBSCL overflow, MPCC stall, HUBBUB VM fault/timeout, and DCPG power-domain interrupt paths on DCN316 hardware.
- Validate DMCU/ABM-related events where applicable: ABM ready/update interrupts, ABM counters, static-screen events, and mailbox command/data byte packing.
- Inject or observe RBBMIF timeout and invalid-access scenarios, confirming timeout address/op/read-write/ack/mask fields and per-client timeout-disable bits decode correctly.
- Test DMUB reset/boot/GPINT/debug paths on DCN316, since this generated header supplies the field masks and shifts used by the DMUB register table.
- Validate perfmon programming by selecting events, enabling counter/current-value interrupts, reading high/low values, acknowledging threshold events, and confirming the display interrupt status chain reports corresponding perfmon interrupts.
- Test suspend/resume and runtime power transitions with active displays, checking that DCPG power-up/power-down, RBBMIF timeout policy, DMUB/DMCU routing, and display interrupt traversal recover consistently.

## Chunk-Specific Summary

Lines 2509-4798 define a DCN 3.1.6 generated mask/shift slice for DMCU interrupt status/routing, DMCU mailbox and ABM counter fields, DMCU perfmon and DPRX interrupt routing, DMCUB/RBBMIF security and timeout diagnostics, DC perfmon2 controls/readback, GPU timer readback, and the IHC display interrupt status chain through the start of continuation 18. Correctness depends on exact bit positions, careful handling of clear/ack side effects, instance/event ordering across repeated macro families, and runtime validation of interrupt delivery, timeout diagnostics, DMUB table usage, perfmon behavior, and power-transition recovery.

### subset-b-001899: lines 4799-7213

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 4799-7213

## Scope

This chunk is part of the generated AMD DCN 3.1.6 shift/mask header. It exports C preprocessor constants that describe bit positions and masks for DCN display-controller registers. The source range is macro-only: it has no functions, structs, typedefs, branches, loops, or software-owned storage.

The range starts in the middle of `DISP_INTERRUPT_STATUS_CONTINUE18`, so the first field's shift definition is outside this chunk while the later shift and mask constants are present. It ends in the middle of `DWB_OGAM_RAMA_END_CNTL2_R`, where the final `DWB_OGAM_RAMA_EXP_REGION_END_SLOPE_R_MASK` constant is outside the requested lines. The merge lane should combine adjacent chunks before making complete-register claims for those two boundary registers.

## Purpose

The purpose of this range is to expose DCN 3.1.6 hardware bitfield layout to AMDGPU display code. The companion `dcn_3_1_6_offset.h` header names MMIO registers; this header names fields inside those registers. Runtime code combines both through register helper macros such as `REG_GET`, `REG_UPDATE`, `FD_MASK`, `FD_SHIFT`, and DC/DMUB register-list constructors.

The covered definitions fall into four broad groups:

- Display interrupt status continuation registers and interrupt destination routing registers for DC, DMU/DMCUB, DCPG, MMHUBBUB, DCHUB, DPP perfmon, MPC, OPP, OPTC, OTG, DIG/DIO/DCIO, HPD, audio, AUX, DSC, and HPO sources.
- DMU miscellaneous and display power-gating registers, including clock gating, memory-power control, SMU interrupt controls, Z-state/SOC-access controls, per-domain power-gating config/status, DCPG interrupt status/control, and IP request enable.
- DMCUB registers for region mapping, code-window mapping, interrupt enable/ack/status/type, external interrupt reporting, security/fault handling, inbox/outbox queues, timers, scratch registers, GPINT data, memory power, processor ID, and soft reset.
- Display Writeback (`DWB`) top and color-pipeline registers for enable/clocking, memory power, frame capture, window/source sizing, CRC, output formatting, overflow/backpressure/debug state, HDR multiplier, gamut remap matrices, OGAM mode/LUT controls, and the first OGAM RAM A endpoint controls.

## Important Definitions

The public surface is the generated shift/mask naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask.

The interrupt-status continuation group covers `DISP_INTERRUPT_STATUS_CONTINUE18` through `DISP_INTERRUPT_STATUS_CONTINUE25`. Important fields include AZ audio endpoint format/enabled/disabled interrupts, DIG fast-training and video-stream-disable interrupts, OTG CPU static-screen/vupdate/GSL-vsync-gap/vstartup/vready events for six OTGs, I2C DDC hardware-done and read-request events, DCPG domain power up/down events, DSC underflow/core-error/perfmon events, DMCUB timer/inbox/outbox/GPINT/fault events, ABM ready/update events, DPIA, whitelist-invalid-access, HPO perfmon, and MMHUBBUB warmup. Continuation bits at bit 31 link each status register to the next continuation register.

The interrupt-destination group maps the same classes of hardware events to destinations. It includes `DCCG_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST2`, `DCPG_INTERRUPT_DEST`, `DCPG_INTERRUPT_DEST2`, `MMHUBBUB_INTERRUPT_DEST`, `WB_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST`, `DCHUB_PERFCOUNTER_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST2`, `DPP_PERFCOUNTER_INTERRUPT_DEST`, `MPC_INTERRUPT_DEST`, `OPP_INTERRUPT_DEST`, `OPTC_INTERRUPT_DEST`, `OTG0_INTERRUPT_DEST` through `OTG5_INTERRUPT_DEST`, `DIG_INTERRUPT_DEST`, `I2C_DDC_HPD_INTERRUPT_DEST`, `DIO_INTERRUPT_DEST`, `DCIO_INTERRUPT_DEST`, `HPD_INTERRUPT_DEST`, `AZ_INTERRUPT_DEST`, `AUX_INTERRUPT_DEST`, `DSC_INTERRUPT_DEST`, and `HPO_INTERRUPT_DEST`.

The GPU timer start-position registers, `DC_GPU_TIMER_START_POSITION_VREADY`, `DC_GPU_TIMER_START_POSITION_FLIP`, `DC_GPU_TIMER_START_POSITION_V_UPDATE_NO_LOCK`, and `DC_GPU_TIMER_START_POSITION_FLIP_AWAY`, define per-display-pipe timing selectors. Most pipe fields are 3-bit values spaced every four bits; the flip and flip-away variants cover D1-D8 while vready and vupdate-no-lock cover D1-D6 in this chunk.

The DMU/DCPG group covers `CC_DC_PIPE_DIS`, `DMU_CLK_CNTL`, `DMU_MEM_PWR_CNTL`, `DMCU_SMU_INTERRUPT_CNTL`, `SMU_INTERRUPT_CONTROL`, `ZSC_CNTL`, `ZSC_CNTL2`, `DMU_MISC_ALLOW_DS_FORCE`, `ZSC_STATUS`, domain power-gate config/status registers for domains 0-3 and 16-18, `DCPG_INTERRUPT_STATUS`, `DCPG_INTERRUPT_STATUS_2`, `DCPG_INTERRUPT_CONTROL_1`, `DCPG_INTERRUPT_CONTROL_3`, and `DC_IP_REQUEST_CNTL`.

The DMCUB group is dense and operationally important. Region registers define 64-bit-style offsets via low and high pieces, top addresses, and enable bits for regions 0, 1, 2, 4, 5, 6, and 7 plus code windows `REGION3_CW0` through `REGION3_CW7`. Interrupt registers expose enable, ack, status, and type fields for timers, inbox/outbox ready/done, GPINT0-GPINT6, GPINT_IH, and undefined-address faults. Queue registers expose base, size, write pointer, and read pointer for inboxes and outboxes 0 and 1. Control/fault registers include security level, unit ID, secure reset, fault interrupt disable, auto-reset and secure-reset status, instruction-fetch/data-write fault clear bits, full-width fault addresses, timer trigger/current, scratch0-scratch15, GPINT data in/out, light-sleep wake interrupt enable, memory-power control, processor ID, and soft reset.

The DWB top group covers `DWB_ENABLE_CLK_CTRL`, `DWB_MEM_PWR_CTRL`, `FC_MODE_CTRL`, `FC_FLOW_CTRL`, `FC_WINDOW_START`, `FC_WINDOW_SIZE`, `FC_SOURCE_SIZE`, `DWB_UPDATE_CTRL`, `DWB_CRC_*`, `DWB_OUT_CTRL`, `DWB_MMHUBBUB_BACKPRESSURE_*`, `DWB_HOST_READ_CONTROL`, `DWB_OVERFLOW_*`, `DWB_SOFT_RESET`, and `DWB_DEBUG_CTRL`. These fields control capture enable/rate/cropping/stereo/new-content state, capture dimensions, update locking, CRC selection and readback, output denorm/min/max/format, host read throttling, overflow interrupt status/ack/mask/type, and debug selection.

The DWB color-pipeline group starts `dce_dc_wb0_dispdec_dwbcp_dispdec`. It includes `DWB_HDR_MULT_COEF`, gamut-remap mode/current mode, coefficient format, two complete remap coefficient banks `A` and `B` with 3x4-style C11-C34 packed pairs, `DWB_OGAM_CONTROL`, `DWB_OGAM_LUT_INDEX`, `DWB_OGAM_LUT_DATA`, `DWB_OGAM_LUT_CONTROL`, and OGAM RAM A start/base/slope/end controls for B, G, and R channels through the partial `DWB_OGAM_RAMA_END_CNTL2_R` register.

## Control Flow And State

This header has no direct control flow. At runtime, DCN 3.1.6 code includes this file and expands field constants into register metadata tables. For example, `display/dmub/src/dmub_dcn316.c` includes `dcn_3_1_6_offset.h` and this header, then fills `dmub_srv_dcn316_regs` with register offsets plus `FD_MASK`/`FD_SHIFT` field values. `display/dc/resource/dcn316/dcn316_resource.c` includes the same generated pair while constructing DC resource objects and DWB/MMHUBBUB support. IRQ service code in nearby DCN generations uses `DMCUB_INTERRUPT_ENABLE` and `DMCUB_INTERRUPT_ACK` fields to build outbox interrupt descriptors, matching fields defined here.

Runtime flow is table-driven:

1. Resource or service code selects a register address from the offset header.
2. It selects a field from this shift/mask header.
3. Register helpers combine address, mask, and shift to read, write, or update the MMIO field.
4. Hardware keeps the programmed value or reports live status until reset, power gating, firmware activity, or a later write changes it.

Most state represented here is persistent hardware register state. DMCUB region mappings, inbox/outbox base and pointer registers, interrupt enables/types, clock/memory power controls, DWB capture configuration, color matrices, LUT controls, output format, and GPU timer selectors persist as MMIO-programmed state. Status fields are live hardware or firmware state, such as interrupt status bits, power-gate FSM state, ZSC access/fence status, DMCUB fault addresses, external interrupt count/ID/context, DWB update pending, CRC values, overflow flags/counters, and current color-mode readbacks.

Several protocols are ordering-sensitive. Interrupt status and ack fields must be masked, acknowledged, and routed consistently. DCPG power state must coordinate force-on/gate requests with PGFSM status and power up/down interrupt clear bits. DMCUB region and mailbox registers must be valid before firmware use; pointer updates need producer/consumer discipline. DWB capture should coordinate enable, window/source size, update lock/pending, memory power, and overflow handling. DWB color programming must use the intended matrix bank, OGAM host selection, LUT index/data ordering, and current-mode status.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register contract. It is meaningful only with:

- `dcn_3_1_6_offset.h`, which supplies the matching register offsets and base indices.
- DC and DMUB register helper layers that expand `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_UPDATE`, `IRQ_REG_ENTRY`, and related macros.
- DCN 3.1.6 resource construction in `display/dc/resource/dcn316/dcn316_resource.c`.
- DMUB service construction in `display/dmub/src/dmub_dcn316.c`.
- DWB support from the DC DWB register-list family, including `display/dc/dwb/dcn30/dcn30_dwb.c` and `dcn30_dwb.h`, which use fields such as `DWB_ENABLE`, update controls, CRC, output format, and overflow status through per-generation register tables.
- IRQ service tables and interrupt source ID mappings that rely on the status, destination, enable, ack, and type field layout for DMCUB outbox events, OTG timing events, HPD/AUX/I2C, DCPG, DSC, audio, and perfmon sources.

Integration is compile-time but behavior is hardware-facing. A bad constant can compile cleanly if the symbol name exists, then program the wrong bit in an MMIO register. The risk surface is larger than ordinary local C code because these definitions are shared by display modeset, firmware mailbox, interrupt, power-management, writeback, color, and diagnostics paths.

## Risks And Edge Cases

Generated-header drift is the main risk. If any shift or mask differs from the silicon register specification or from the companion offset header, the driver can silently manipulate the wrong field. Likely failures include missing or storming interrupts, stuck DMUB mailbox communication, firmware fault handling failures, display power-gating hangs, broken DWB capture, incorrect writeback color, stale CRC or perfmon data, and subtle suspend/resume or idle-state failures.

Chunk boundaries are not semantic. The first register and final register are incomplete in this chunk. The merge lane should not infer that `DISP_INTERRUPT_STATUS_CONTINUE18` lacks the counter0 shift or that `DWB_OGAM_RAMA_END_CNTL2_R` lacks its slope mask.

Replicated fields are easy to mis-index. OTG0-OTG5, DMCUB GPINT0-GPINT6, DCPG domains 0-3 and 16-18, AUX/HPD/DDC instances, DSC0-DSC5, and DWB channel registers rely on predictable bit ordering. Off-by-one instance mapping can route an interrupt or configure a capture/color channel for the wrong hardware block.

Some field names intentionally produce doubled suffixes such as `*_MASK_MASK` for fields whose hardware name already contains `MASK`. Those should be treated as generated names, not cleanup candidates.

Interrupt and status fields do not encode access semantics. Names such as `*_ACK`, `*_CLEAR`, `*_MASK`, `*_STATUS`, `*_INT_TYPE`, and `*_CURRENT` imply write-one-to-clear, mask, level/pulse, or readback behavior, but this header only supplies bits. Callers must still follow the sequencing expected by hardware and by the IRQ helper tables.

DMCUB address and mailbox fields are full-width or wide physical/firmware-facing values. Region offsets use low/high pieces and top-address enable bits, so truncation, wrong alignment, or enabling before programming both halves can expose invalid firmware memory windows.

DWB capture/color fields are stateful and banked. Matrix coefficients, OGAM LUT data, start/end/base/slope controls, current-mode readbacks, update locks, and memory-power state can make errors appear as intermittent capture glitches or color inaccuracies rather than immediate build or modeset failures.

## Test Signals

There are no unit-testable functions in this chunk. Useful validation is structural and integration-focused:

- Build coverage: DCN 3.1.6 display and DMUB objects that include `dcn_3_1_6_sh_mask.h` should compile with no missing field macros in resource, DMUB, DWB, and IRQ table construction.
- Generated consistency checks: every field's mask should align with its shift and expected width; replicated register families should keep identical layouts where the hardware block is replicated.
- Interrupt validation: HPD/AUX/I2C, OTG vupdate/vstartup/vready, DMCUB outbox/GPINT, DCPG power events, DSC error/perfmon, and audio endpoint interrupts should route, mask, ack, and clear correctly without spurious repeats.
- DMUB validation: firmware boot, region setup, inbox/outbox command traffic, GPINT signaling, scratch register use, timer interrupts, fault reporting, secure reset, and soft reset should work across suspend/resume and power transitions.
- Power-management validation: DMCU/DMCUB/DMU memory-power fields, DCPG domain force/gate/status, ZSC allow/access/fence status, and DC IP request enable should behave across idle, display-off, and resume scenarios.
- DWB validation: frame capture enable/rate/crop/source-size paths should produce expected writeback output; update pending should drain; CRC values should change with content; overflow and backpressure counters should remain clear under valid bandwidth.
- Color validation: DWB HDR multiplier, gamut remap bank A/B, OGAM LUT programming, and OGAM RAM endpoint controls should produce expected pixel-capture or CRC signatures for known color test patterns.

## Chunk Notes For Merge Lane

- The chunk covers lines 4799-7213 of `dcn_3_1_6_sh_mask.h`.
- It contains generated `#define` constants only; no local includes, functions, data objects, enums, or structs are introduced in the range.
- Address blocks fully or partly covered are `dce_dc_dmu_dmu_misc_dispdec`, `dce_dc_dmu_dc_pg_dispdec`, `dce_dc_dmu_dmcub_dispdec`, `dce_dc_wb0_dispdec_dwb_top_dispdec`, and `dce_dc_wb0_dispdec_dwbcp_dispdec`, preceded by interrupt continuation and interrupt destination registers that belong to the surrounding generated interrupt namespace.
- Boundary registers are partial: `DISP_INTERRUPT_STATUS_CONTINUE18` begins before the chunk, and `DWB_OGAM_RAMA_END_CNTL2_R` continues after it.

### subset-b-001900: lines 7214-9828

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 7214-9828

## Scope

This chunk is a generated AMD DCN 3.1.6 register shift/mask header segment. It contains preprocessor constants only: each hardware field is represented by a `...__SHIFT` macro and a matching `..._MASK` macro. The range covers 2,615 source lines and starts in the middle of the DWB output-gamma RAMA field family, then continues through DWB OGAM RAMB, DC perfmon blocks, VGA/MMHUBBUB writeback, Azalia HDA audio, DCHUBBUB arbitration/clock/debug/timeout controls, SDPIF configuration, and the beginning of DCN VM physical-window fields.

Although this tree is under `ceph-client`, this source is AMDGPU display hardware metadata. It does not implement Ceph filesystem behavior.

## Purpose

The purpose of this chunk is to publish bit positions and masks for DCN 3.1.6 display MMIO registers. Driver code includes this file with `dcn_3_1_6_offset.h`, builds per-ASIC register tables from the generated names, and later uses AMD display register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_READ`, and `REG_WRITE` to pack and unpack fields without embedding literal bit layouts.

The constants are data-like, but correctness is high impact. A wrong shift or mask can still compile and then program an incorrect hardware field for writeback color, capture buffers, memory arbitration, VM apertures, audio control, or debug/status handling.

## Important APIs, Types, And Macros

There are no callable functions, structs, enums, variables, includes, locks, or allocation paths in this source range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or updating the field.
- `// addressBlock: ...` comments: generated grouping metadata for the owning hardware block.

Major register families in this chunk:

- `DWB_OGAM_RAMA_*` and `DWB_OGAM_RAMB_*`: output-gamma RAM bank A/B fields for writeback. The chunk starts with the final RAMA end-control mask from the previous logical block, then includes RAMA channel offsets, RAMA region pairs 0-33, all RAMB start/base/slope/end/offset fields for B/G/R channels, and RAMB region pairs 0-33. Region-pair registers encode LUT offsets and segment counts for piecewise-linear output-gamma curves.
- `DC_PERFMON3_*`, `DC_PERFMON4_*`, and `DC_PERFMON5_*`: display performance monitor counter control, secondary control, state, perfmon control, current-value interrupt/misc selection, and low/high counter readback fields around writeback, MMHUBBUB, and HDA blocks.
- VGA and VGAIF blocks: `VGA_RENDER_CONTROL`, sequencer reset, mode control, surface pitch/base addresses, HDP/cache controls, per-pipe `D1VGA_CONTROL` through `D6VGA_CONTROL`, security, status, interrupt, source select, and MCIF phase outstanding counters.
- `MCIF_WB_*`: memory client interface writeback fields for buffer-manager software control/status, luma/chroma pitch and addresses, buffer status and resolution for four buffers, arbitration, SCLK/NB pstate watermarks, clock gating, self refresh, VMID, minimum time-to-urgent, and luma/chroma buffer sizes.
- `MMHUBBUB_*` and `WBIF0_*`: writeback memory-hub warmup controls, warmup address/region, minimum time-to-urgent, global MMHUBBUB control, SMU watermark control, miscellaneous WBIF control, outstanding counters, source split, memory power status/control, clock gating, soft reset, DMU interface error status, client unit ID, and warmup VMID.
- `AZALIA_*`, `AZALIA_F0_*`, `AZF0STREAM*`, `AZF0ENDPOINT*`, and `AZF0INPUTENDPOINT*`: HDA/HDMI/DP audio controller fields, codec root parameters and controls, CRC control/readback, memory power state, stream index/data windows for 16 streams, and codec endpoint index/data windows for output and input endpoints.
- `DCHUBBUB_ARB_*`: hubbub arbitration and watermark fields for outstanding DF requests, saturation/QoS forcing, DRAM state control, watermarks A-D for urgency, memory trip latency, self-refresh enter/exit including Z8 variants, DRAM clock-change permission, fractional urgent bandwidth for nominal and flip traffic, host-VM controls, watermark-change control, and timeout enable.
- DCHUBBUB system fields: global timer, surface check addresses, `VTG0_CONTROL` through `VTG3_CONTROL`, soft reset, clock control, `DCFCLK_CNTL`, latency/performance measurement controls, vline snapshot, overflow/status clearing, timeout detection and interrupt status, `FMON_CTRL`, and test debug index/data.
- `DCHUBBUB_SDPIF_*`, `VM_REQUEST_PHYSICAL`, `DCHUBBUB_FORCE_IO_STATUS_*`, and `DCN_VM_*`: SDPIF port/credit/status/error/force-snoop fields, physical PDE/PTE request controls, force-IO status address/pipe/type capture fields, and the start of framebuffer/AGP aperture fields through `DCN_VM_AGP_BASE`.

## Control Flow And Runtime Behavior

The header has no runtime control flow. Runtime behavior is supplied by generated-table consumers:

1. DCN 3.1.6 resource and DMUB code includes `dcn_3_1_6_offset.h` and this header.
2. Register-list macros paste symbolic register and field names into table initializers. Offsets come from the offset header; shifts and masks come from this file.
3. DCN resource construction stores those constants in typed register/mask/shift tables such as hubbub, hubp, timing generator, clock, and writeback-related tables.
4. Runtime code uses those tables to perform read-modify-write programming and status reads against MMIO registers.

Concrete integration in this tree includes `display/dc/resource/dcn316/dcn316_resource.c`, which includes this generated header and builds `hubbub_reg`, `hubbub_shift`, and `hubbub_mask` using `HUBBUB_REG_LIST_DCN31(0)` and `HUBBUB_MASK_SH_LIST_DCN31(__SHIFT/_MASK)`. Those lists consume fields from this chunk such as `DCHUBBUB_ARB_FRAC_URG_BW_*`, `DCHUBBUB_ARB_REFCYC_PER_TRIP_TO_MEMORY_*`, Z8 self-refresh watermarks, `DCHUBBUB_CLOCK_CNTL`, `DCHUBBUB_SDPIF_CFG0`, and the `DCN_VM_FB_LOCATION_*` / `DCN_VM_AGP_*` aperture fields.

DMUB integration is direct as well. `display/dmub/src/dmub_dcn316.c` includes `dcn_3_1_6_offset.h` and this header, then initializes `dmub_srv_dcn316_regs` with `DMUB_DCN31_REGS()` and `DMUB_DCN31_FIELDS()`. The DMUB DCN31 field list consumes `DCN_VM_FB_LOCATION_BASE__FB_BASE` and `DCN_VM_FB_OFFSET__FB_OFFSET` from this chunk so firmware-facing code can read framebuffer placement with the correct DCN316 bit layout.

Writeback and memory-client behavior is shared with older DCN helpers. The `MCIF_WB_*` fields match the table style in `display/dc/mmhubbub/dcn20/dcn20_mmhubbub.h` and are programmed by `dcn20_mmhubbub.c` for writeback buffer addresses, high address halves, pitch, size, arbitration, watermarks, pstate behavior, and buffer-manager interrupts. DWB color-management code uses the DWB OGAM RAMA/RAMB fields to program output-gamma LUT curves and bank selection around writeback capture.

DCHUBBUB arbitration fields are consumed by hubbub code such as the DCN30/DCN31/DCN32 families. Watermark programming writes the urgency, self-refresh, DRAM clock-change, and fractional bandwidth registers. SDPIF control code updates `DCHUBBUB_SDPIF_CFG0.SDPIF_PORT_CONTROL` to hand SDPIF port control between DC and another agent as required by the platform path.

The Azalia, VGA, perfmon, timeout, force-IO, and debug blocks are mostly accessed by generic display/audio/debug paths rather than by functions in this header. This file only describes the bit packing; it does not define when to clear status, arm interrupts, select debug indices, or read counters.

## State And Persistence Behavior

The macros hold no software state and persist nothing. They describe stateful hardware registers whose values remain in the display engine until later register writes, mode-set reprogramming, suspend/resume restore, power gating, soft reset, or ASIC reset changes them.

State represented by this chunk includes:

- DWB output-gamma RAM bank configuration, including B/G/R channel start/end/base/slope/offset values and per-region LUT segment layout for RAMA/RAMB.
- Perfmon counter source selection, enable/freeze/clear controls, current counter values, interrupt selection, overflow/status fields, and high/low readback.
- VGA mode, source selection, render/security/cache/HDP behavior, per-pipe enablement, and VGA interrupt/status state.
- MCIF writeback buffer-manager state: active addresses, buffer pitches, luma/chroma sizes, buffer status, buffer resolution, VMID, fences/locks, interrupt enables/acks, and watermark/pstate controls.
- MMHUBBUB and WBIF state for warmup, memory power, clock gating, soft reset, source split, SMU watermarks, outstanding counters, and DMU interface error status.
- HDA/Azalia controller and codec state, including audio DTO programming, DMA control, payload capabilities, CRC counters/results, power state, stream index/data windows, and endpoint index/data windows.
- DCHUBBUB arbitration and memory-service state for watermarks A-D, Z8 self-refresh watermarks, DRAM clock-change permissions, fractional urgent bandwidth, host-VM behavior, global timing, VTG links, latency measurement, ROB overflow, timeout detection, force-monitor controls, and SDPIF port/credit/error status.
- DCN VM aperture state for framebuffer base/top/offset and AGP bottom/top/base fields visible at the end of the chunk.

Some fields are not plain configuration bits. Status and clear fields such as MCIF buffer status, VGA interrupt/status, MMHUBBUB memory power status, Azalia CRC/power status, DCHUBBUB overflow/timeout/SDPIF error state, and force-IO sticky status may be read-only, latched, self-clearing, write-one-to-clear, or sequencing-sensitive. The generated header does not encode access type.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`, which supplies the matching register offsets.
- `display/dc/resource/dcn316/dcn316_resource.c`, which includes this header and builds DCN316 resource tables from generated register and field macros.
- `display/dmub/src/dmub_dcn316.c` and `display/dmub/src/dmub_dcn31.h`, which expose selected DCN316 register offsets, masks, and shifts to DMUB service code.
- `display/dc/hubbub/dcn31/dcn31_hubbub.h`, `dcn30_hubbub.h`, and related hubbub implementation files, which consume DCHUBBUB watermark, SDPIF, VM aperture, clock, and fault-related field names through `HUBBUB_SF(...)` lists.
- `display/dc/mmhubbub/dcn20/dcn20_mmhubbub.h` and `dcn20_mmhubbub.c`, whose writeback memory-interface register tables and runtime programming paths use the `MCIF_WB_*` field layout represented in this chunk.
- DWB writeback and color-management helpers, which rely on the DWB OGAM field names for output-gamma LUT/RAM programming.
- Audio/HDA code paths and diagnostics that use the Azalia register fields through the generated AMD register-access namespace.

The macro names themselves are the compile-time API. Missing or renamed macros are usually caught by table initializers. Wrong numeric constants are harder: they can preserve a clean build while producing display corruption, failed writeback, bad audio behavior, missed interrupts, or unstable power-state transitions.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts with the tail of a RAMA end-control field whose register began in the previous chunk, and it stops after `DCN_VM_AGP_BASE__AGP_BASE__SHIFT`; the matching mask and later VM fields continue in the next chunk.
- Generated-header drift is the main risk. A single incorrect mask width or shift can misprogram DWB gamma regions, MCIF writeback addresses, watermarks, VM apertures, audio DMA controls, or status clear bits.
- DWB OGAM programming is banked and channel-specific. RAMA/RAMB and B/G/R fields are structurally similar; swapped masks or region-pair errors can create color errors that only appear on writeback/capture paths using that LUT bank.
- MCIF writeback buffer address fields are high impact. Bad low/high address or pitch masks can direct writeback to the wrong memory, corrupt captured frames, trip VM faults, or break chroma/luma layout.
- Watermark and arbitration fields are timing-sensitive. Incorrect `DCHUBBUB_ARB_*` masks can cause underflow, stutter-entry failures, bad DRAM clock-change decisions, or bandwidth issues only under high-resolution, multi-display, low-clock, or page-flip stress.
- Status/clear/interrupt fields need correct access ordering. VGA, MCIF_WB, Azalia, perfmon, DCHUBBUB timeout, SDPIF, force-IO, and overflow bits may require read-before-clear or write-one-to-clear behavior that this header does not document.
- SDPIF credit and port-control fields affect request routing between display and system fabric. Wrong masks can leave requests blocked, credit errors uncleared, or snooping/host-VM attributes misapplied.
- Memory-power and clock-gating fields interact with sequencing. Forcing resets or gating clocks around active writeback, audio, or hubbub traffic can create transient failures even when masks are correct.
- The Azalia stream and endpoint index/data windows are repeated 16 and 8 times respectively. Instance-specific generation mistakes can affect only one audio stream or connector path and can be missed by basic display-only testing.

## Test Signals

Useful validation combines generated-header consistency checks, build coverage, and hardware behavior:

- Build AMDGPU/DC with DCN316 enabled. Missing or renamed symbols should fail in `dcn316_resource.c`, `dmub_dcn316.c`, hubbub table construction, DMUB table construction, writeback/MMHUBBUB users, or audio/debug users.
- Mechanically verify that every `__SHIFT` field visible in lines 7214-9828 has the expected companion `_MASK` field when the generated schema defines one, and that masks align with their shifts.
- Diff this DCN 3.1.6 slice against adjacent generated headers for compatible ASICs such as DCN 3.1.5, DCN 3.1.4, or DCN 3.2 where layout parity is expected.
- Exercise display writeback with multiple output formats, luma/chroma planes, four-buffer cycling, high address bits, VMID selection, buffer fences/locks, overflow interrupts, and suspend/resume.
- Validate DWB color-management writeback with OGAM bypass, RAMA/RAMB bank selection, B/G/R channel LUT writes, and region-pair programming across all 0-33 regions.
- Run bandwidth-stress display modes that exercise hubbub watermarks: high refresh, multiple displays, DCC, flips, memory-clock changes, self-refresh/Z8 transitions, and low-power entry/exit.
- Check DMUB boot and framebuffer-window setup on DCN316, especially reads of `DCN_VM_FB_LOCATION_BASE` and `DCN_VM_FB_OFFSET`.
- Exercise SDPIF control and monitor `SDPIF_REQ_CREDIT_ERROR`, response status, force-snoop behavior, and force-IO sticky status where diagnostics expose them.
- Validate HDA/DP/HDMI audio playback across multiple streams/connectors, including power transitions and CRC/debug paths if available.
- Read perfmon3/4/5 counters with known event selections and verify counter enable, clear, freeze, low/high readback, overflow, and interrupt status behavior.
- Monitor kernel logs and hardware status for MCIF writeback overrun, DCHUBBUB ROB overflow, timeout interrupts, VM faults, audio underflow, display underflow, or resume-only regressions.

## Cross-Chunk Notes

The previous chunk owns the earlier DWB top/color-management fields and the beginning of `DWB_OGAM_RAMA_END_CNTL2_R`. This chunk completes most of the RAMA/RAMB output-gamma region layout but begins from a partial logical register. The next chunk must be consulted for the `DCN_VM_AGP_BASE__AGP_BASE_MASK` companion field and subsequent DCN VM/security/fault blocks. The final per-file report should merge adjacent chunks before making complete claims about DWB OGAM, DCN VM, or the full DCN316 shift/mask namespace.

### subset-b-001901: lines 9829-12382

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 9829-12382

## Purpose

This chunk is generated AMD DCN 3.1.6 register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit shifts and bit masks used to encode or decode fields inside DCN display-controller MMIO registers. Consumers pair these `__SHIFT` and `_MASK` macros with the matching register offsets from `dcn_3_1_6_offset.h` and the AMD display register helper macros.

The requested range contains 2,554 source lines and 2,084 `#define` entries. It starts in the DCHUBBUB/VM section at the local-HBM aperture and SDPIF security fields, covers DCHUBBUB return-path, VM request, and perfmon field definitions, then covers HUBP/HUBPREQ/HUBPRET/CURSOR field definitions for display pipes 0 and 1. Although this repository path is under a `ceph-client` source mirror, this file is AMDGPU display-driver ASIC register metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or exported symbols in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

Major field families in this chunk:

- DCHUBBUB/VM aperture and security fields: `DCN_VM_LOCAL_HBM_ADDRESS_*`, `DCN_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL`, `DCHUBBUB_SDPIF_PIPE_SEC_LVL`, `DCHUBBUB_SDPIF_PIPE_DMDATA_SEC_LVL`, and SDPIF memory power status/control.
- DCHUBBUB return path: DCC video-format enable, DCC constant tables `DCHUBBUB_RET_PATH_DCC_CFG0_0` through `DCHUBBUB_RET_PATH_DCC_CFG7_1`, return-path memory power control/status, DCHUBBUB CRC enable/source/pipe/surface selection, CRC result fields, DCC statistics, compressed-buffer sizing, DET buffer sizing for DET0 through DET3, memory-power mode/status, and reserved compbuf space.
- DCHUBBUB VM request interface: repeated `DCN_VM_CONTEXT0` through `DCN_VM_CONTEXT15` page-table depth/block-size fields, base/start/end page-table address fields, default-address fields, and VM fault control/status/address fields.
- `DC_PERFMON6` and `DC_PERFMON7`: perfcounter select/clear/status, perfmon enable/state, current-value capture, high/low counter values, and integer/misc capture fields.
- HUBP0/HUBP1 core pipe fields: surface format/rotation/tiling/swizzle/DCC metadata controls, viewport start and dimension fields for luma and chroma planes, request-size controls, HUBP clock control, VM page config, debug fields, and DCFCLK/DPPCLK measurement-window controls.
- HUBPREQ0/HUBPREQ1 memory request fields: luma/chroma pitch, VMID settings, primary/secondary and meta-surface 64-bit addresses, surface control, flip control and flip interrupts, current and earliest in-use addresses, expansion mode, TTU/QoS watermarks and deadlines, DMDATA VM control, system aperture limits, MX L1 TLB control, blank/destination/prefetch/vblank/flip/nominal timing parameters, per-line delivery, cursor request timing, ref-to-pixel frequency ratio, destination Y delta request limits, and HUBPREQ memory power state.
- HUBPRET0/HUBPRET1 return fields: DET plane base, pack/crossbar controls, DMROB/PIXCDC memory power state, read-line interval/window configuration, vblank and read-line interrupts, current/snapshot line values, and read-line status bits.
- CURSOR0_0 and partial CURSOR0_1 fields: cursor enable/request/magnify/mode/TMZ/pitch/lines-per-chunk/perfmon controls, cursor surface address, size, position, hot spot, stereo offsets, destination offset, cursor ROB memory power state, DMDATA address/control/QoS/status/software fields for pipe 0, and the beginning of the same pipe-1 cursor/DMDATA family through `CURSOR0_1_DMDATA_QOS_CNTL`.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMD display code:

1. DCN 3.1.6 resource and DMUB code include `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h`.
2. Resource code builds per-block register tables and shift/mask tables for hubbub, HUBP, cursor, perfmon, DMUB, and related DCN components.
3. Driver helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_READ`, `REG_WRITE`, and polling/wait helpers use the generated masks and shifts to change individual fields without hand-coded bit math at every call site.
4. Hardware sequencing code performs modeset, plane update, flip, cursor update, VM setup, power-gating, QoS, timing, and diagnostic operations by writing these fields in the order required by DCN hardware.

The macros themselves do not encode ordering constraints. For example, flip-control fields do not express when a surface update lock must be acquired, CRC fields do not express when results are valid, and memory-power fields do not express when a block is safe to gate. Those semantics live in the consuming DCN code and hardware programming guides.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk. It describes MMIO-backed GPU display state. The represented hardware state includes:

- Aperture, VM context, page-table, default-address, and fault-reporting state for display memory requests.
- Surface, metadata, pitch, viewport, tiling, DCC, and flip state for HUBP/HUBPREQ pipes 0 and 1.
- Timing-derived request state such as prefetch, vblank, flip, nominal, per-line delivery, QoS, TTU deadlines, and destination geometry.
- Return-path buffers and compression state, including DCC constants/statistics, DET/compbuf allocation, crossbar mapping, and read-line/vblank status.
- Cursor image address, size, position, hot spot, stereo, metadata, memory-power, QoS, and software DMDATA update state.
- Diagnostic and observability state for CRC, perfmon counters, debug registers, and fault status.
- Power-management state for SDPIF, return path, compbuf, DET, HUBPREQ, HUBPRET, and cursor memory blocks.

Persistence is hardware-defined. Configuration fields generally remain until modeset/reprogramming, suspend/resume restoration, power gating, or ASIC reset. Status, interrupt, counter, `*_CURRENT`, `*_DONE`, clear, sticky, fault, and power-status fields may be read-only, self-clearing, write-one-to-clear, or otherwise side-effect-sensitive; this header names and locates fields but does not classify access permissions.

## Dependencies And Integration Points

This generated chunk must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`, which supplies the register offsets for the same DCN 3.1.6 register names.
- AMD display register helper infrastructure that combines offsets with field masks/shifts for `REG_SET`, `REG_UPDATE`, `REG_GET`, and related helpers.
- DCN 3.1/3.1.6 block implementations for hubbub, HUBP, cursor, perfmon, resource construction, and DMUB register access.

Direct include sites in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`

Those include sites use token-pasted register names and block-specific shift/mask structs, so generated symbol spelling is part of the local ABI between this header and the DCN code. This chunk also aligns structurally with neighboring generated DCN headers for later ASIC revisions; many families such as `HUBPREQ0_DCSURF_FLIP_CONTROL__*`, `DCN_VM_CONTEXT0_CNTL__*`, `DCHUBBUB_CRC_CTRL__*`, and `CURSOR0_0_CURSOR_CONTROL__*` appear across other DCN versions with compatible naming.

## Risks And Edge Cases

- Bitfield drift is the central risk. These constants are untyped preprocessor values, so an incorrect shift or mask can compile cleanly while changing the wrong field in a live MMIO register.
- Repeated pipe families are copy-sensitive. HUBP/HUBPREQ/HUBPRET/CURSOR pipe 0 and pipe 1 definitions are structurally similar but instance-specific; a single bad field can affect only one display pipe, plane, cursor, or multi-display topology.
- VM and aperture fields are high risk because wrong page-table, aperture, default-address, or VMID fields can produce display faults, black screens, stale scanout, incorrect memory isolation, or hard-to-debug GPU VM errors.
- Surface address, meta-address, pitch, tiling, DCC, and flip fields are sequencing-sensitive. Incorrect field definitions can manifest only during page flips, stereo flips, DCC-enabled surfaces, rotated/swizzled formats, chroma planes, or specific plane formats.
- Timing/QoS/prefetch fields affect underflow margins. Bad masks in TTU, vblank, flip, nominal, or per-line delivery parameters can cause intermittent underflow, stutter, or failures that depend on clock state and display mode.
- Power-control fields can be hazardous. Incorrect force/disable/low-power-state masks may leave SRAMs powered when they should gate, or gate memory while display requests are active.
- Status, interrupt, fault, and clear fields may have side effects. Treating clear bits or sticky status as ordinary configuration fields can lose interrupt/fault evidence or wedge status handling.
- The requested chunk boundaries are artificial. It starts after earlier VM/framebuffer/AGP definitions and ends partway through the `CURSOR0_1` DMDATA field family, so adjacent chunks are required for complete file-level conclusions.

## Test Signals

Useful validation combines generated-header consistency with DCN hardware behavior:

- Build AMDGPU/DC with DCN 3.1.6 support enabled; missing or renamed macros should fail in `dcn316_resource.c`, `dmub_dcn316.c`, or the shared DCN block constructors that consume shift/mask tables.
- Mechanically verify that every visible field has a paired shift and mask macro where expected, and that masks match the declared bit positions and widths.
- Diff this chunk against AMD's authoritative DCN 3.1.6 register database and nearby generated headers where field compatibility is expected.
- Exercise modesets and plane updates across pipes 0 and 1 with luma/chroma surfaces, DCC-enabled surfaces, rotation/swizzle/tiled layouts, stereo-flip paths, immediate and delayed flips, cursor movement, cursor format changes, and cursor DMDATA updates.
- Stress VM paths with page-table programming, system-aperture limits, VM fault reporting, multiple VMIDs, TMZ-protected cursor or DMDATA surfaces, and suspend/resume.
- Validate timing and bandwidth behavior at high resolutions/refresh rates: watch for underflow, missed flips, wrong vblank timing, QoS deadline problems, or prefetch failures.
- Check diagnostics: CRC capture values, DCC statistic completion, perfmon counter enable/read/clear behavior, read-line/vblank interrupts, surface-flip interrupts, and VM fault status/address reporting.
- Test power-management transitions for HUBBUB, HUBPREQ/HUBPRET, DET/compbuf, SDPIF, and cursor memory blocks during idle, active display, display-off, clock gating, and resume.

## Cross-Chunk Notes

Earlier chunks in `dcn_3_1_6_sh_mask.h` contain the preceding DCHUBBUB force-IO, framebuffer, and AGP VM fields that lead into this range. Later chunks continue the `CURSOR0_1` DMDATA fields and the remaining DCN 3.1.6 shift/mask namespace. The final per-file research document should merge adjacent chunks before making complete claims about all pipes, all cursor instances, or the full DCN 3.1.6 register-field map.

### subset-b-001902: lines 12383-14898

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 12383-14898

## Purpose

This chunk is generated AMDGPU DCN 3.1.6 register shift/mask metadata. It contains no executable code; it exports C preprocessor constants that describe bit offsets (`__SHIFT`) and bit masks (`_MASK`) for display-controller MMIO register fields. Driver code pairs these definitions with `dcn_3_1_6_offset.h` so common register helpers can read, write, and update individual hardware fields for this ASIC generation.

The requested range starts in the tail of the `CURSOR0_1_DMDATA_*` group, then covers the rest of perfmon 8, complete HUBP/HUBPREQ/HUBPRET/cursor/perfmon register-field groups for HUBP instances 2 and 3, and the start of DPP0 converter, cursor, scaler, and color-management fields. It ends inside `CM0_CM_POST_CSC_C11_C12`, so adjacent chunks are required for complete DPP0 color-management coverage. The slice contains 2,113 `#define` lines, split evenly into 1,057 shift macros and 1,056 mask macros, plus 373 generated comments/register headings.

Although the source lives under a local `ceph-client` tree, this file is AMD display hardware metadata. It does not implement distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, typedefs, enums, variables, includes, locks, allocation paths, or direct MMIO accesses in this chunk. The exported interface is entirely macro based:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK`: mask used to isolate, clear, or insert the field.
- `// addressBlock: ...` comments: generated grouping metadata identifying the display sub-block that owns the following register definitions.

Major register families in this range:

- Tail of `CURSOR0_1_DMDATA_STATUS`, `DMDATA_SW_CNTL`, and `DMDATA_SW_DATA`: display metadata completion, underflow, clear, software update/repeat/size, and payload fields for cursor/sideband metadata on instance 1.
- `DC_PERFMON8`, `DC_PERFMON9`, and `DC_PERFMON10`: perf counter source selection, counted-value type, increment mode, run-enable mode, hardware stop/counter-off selectors, active/state bits, interrupt enables/status/acks, high/low values, and perfmon global control.
- `HUBP2` and `HUBP3`: surface format, address/tiling configuration, primary/secondary viewport coordinates, request-size configuration for luma/chroma/meta planes, HUBP control/status, blanking, reset, timeout, underflow, clock-control, VMPG, debug, and DCFCLK/DPPCLK measurement windows.
- `HUBPREQ2` and `HUBPREQ3`: surface pitch, VMID, primary/secondary luma and chroma surface addresses, metadata addresses, DCC/TMZ surface control, flip control/interrupts, in-use and earliest-in-use address latches, expansion mode, TTU/QoS, VM aperture/TLB controls, blank/destination/prefetch/vblank/flip/nominal timing parameters, per-line delivery, cursor request settings, and HUBPREQ memory power controls/status.
- `HUBPRET2` and `HUBPRET3`: HUBPRET control, memory power control/status, read-line control/value/status, and interrupt status/ack/mask fields.
- `CURSOR0_2` and `CURSOR0_3`: cursor enable/mode/pitch/lines-per-chunk, address high/low, size, position, hot spot, stereo offsets, destination offset, cursor memory power, DMDATA address/control/QoS/status, and software DMDATA fields.
- `CNVC_CFG0` and `CNVC_CUR0`: DPP0 pixel format, format expansion/alpha/output FP controls, FP bias/scale, color-keyer channels, 2-bit alpha LUT, pre-dealpha/pre-realpha, pre-CSC mode and matrix coefficients, converter coefficient format, pre-degamma, and cursor0 color/control/FP scale-bias fields.
- `DSCL0`: DPP0 scaler coefficient RAM select/data, scaler mode/taps, DSCL control/autocal/update, manual replicate factors, luma/chroma horizontal and vertical ratios and initial phases, black color, extended overscan, OTG blanking, recout/MPC size, line-buffer data and memory controls/status, DSCL memory power, output-buffer control, and OBUF memory power.
- Start of `CM0`: color-management bypass/update-pending and post-CSC mode/current fields, followed by the first post-CSC coefficient pair (`C11`/`C12`) where the range stops.

## Control Flow

This header has no runtime branches or sequencing. Runtime control flow is provided by AMD display code that includes the generated header:

1. DCN 3.1.6 resource and DMUB code include `dcn_3_1_6_offset.h` for register addresses and this `dcn_3_1_6_sh_mask.h` file for field layout.
2. Register-list macros paste symbolic register and field names into generated constants. Offsets come from the offset header; masks and shifts come from this file.
3. Helpers such as `FD_MASK`, `FD_SHIFT`, `TF_SF`, `IPP_SF`, HUBP/HUBBUB field macros, DMUB field macros, and `REG_READ`/`REG_WRITE`/`REG_UPDATE` style accessors materialize typed register tables or perform field updates.
4. Higher-level display flows program planes, cursors, page flips, memory request timing, virtual-memory controls, scaler ratios, converter/color controls, and perf counters through those tables.

The macros do not encode ordering constraints. Consumers must still sequence plane address updates, update locks, flip interrupt clears, cursor/DMDATA updates, DCC/TMZ setup, VM aperture/TLB programming, scaler coefficient RAM writes, line-buffer partitioning, memory-power transitions, clock gating, and perf counter clear/freeze/ack operations according to hardware rules.

## State And Persistence Behavior

The chunk stores no software state and persists nothing in files or kernel memory. It describes MMIO-backed hardware state. The represented state includes:

- Plane-fetch state in HUBP/HUBPREQ for instances 2 and 3: surface format/layout, tiling, viewport windows, pitch, luma/chroma addresses, metadata addresses, DCC and TMZ protection, active/in-use address latches, flip pending/interrupt state, blanking, destination geometry, and request granularity.
- Display memory scheduling and QoS state: TTU controls, QoS watermarks, global TTU settings, prefetch/vblank/flip/nominal timing registers, per-line delivery estimates, cursor request adjustments, and reference-clock-to-pixel-clock ratios.
- Virtual-memory state: VMID selection, system aperture low/high limits, L1 TLB controls, DMDATA VM controls, and VMPG page-size configuration.
- Cursor and DMDATA state: cursor image address/size/position/hotspot/stereo, cursor memory power, metadata address/control/status/QoS, and software-supplied metadata payloads.
- Perfmon state: counter event selection, counter state, counted values, interrupt status/ack, high/low readback values, run-enable modes, and perfmon global control.
- DPP0 processing state: pixel conversion, color keying, alpha/dealpha/re-alpha, pre-CSC matrix, pre-degamma, cursor colors, scaler taps/ratios/initial phases/coefficient RAM, line-buffer partitioning, scaler/OBUF memory power, recout/MPC geometry, overscan, and the beginning of post-CSC color-management state.

Persistence and side effects are hardware-defined. Configuration fields usually remain programmed until modeset, plane update, power gating, suspend/resume, or ASIC reset. Status, pending, underflow, timeout, interrupt, ack, clear, memory-power state, in-use, and earliest-in-use fields may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This generated header only exposes bit positions and masks; it does not state access type.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.6 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`, which supplies matching MMIO offsets.
- DCN 3.1.6 base-address definitions in the resource and DMUB translation units.
- Common AMD display register helper macros that derive field masks and shifts from generated names.

Observed include/integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes the DCN 3.1.6 offset/mask headers and constructs the DCN 3.1.6 resource pool using shared DCN31 HUBP, DPP, scaler, cursor, IRQ, and related building blocks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`, which includes the same generated headers and builds `dmub_srv_dcn316_regs` with `FD_MASK` and `FD_SHIFT` over `DMUB_DCN31_FIELDS()`.
- Shared DPP/IPP/HUBP code such as `dcn10_dpp.h`, `dcn10_ipp.h`, `dcn10_dpp.c`, and DCN31 HUBP/resource code, which consume families like `CNVC_CFG0`, `CNVC_CUR0`, `DSCL0`, `CURSOR0_*`, `HUBP*`, and `HUBPREQ*` through generation-specific register tables.
- IRQ and atomic/page-flip paths that rely on HUBPREQ flip interrupt and pending/status fields.
- Display mode validation and watermark programming, which compute timing and delivery values that are ultimately written to TTU, prefetch, vblank, nominal, and per-line delivery registers represented here.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong mask or shift is still a valid C constant and can silently program the wrong MMIO bits.
- The chunk boundary is artificial. It starts after the `CURSOR0_1_DMDATA_QOS_CNTL` group has already begun and ends mid-register at `CM0_CM_POST_CSC_C11_C12`; adjacent chunks are required for complete file-level claims.
- Instance repetition is copy-sensitive. `HUBP2`/`HUBP3`, `HUBPREQ2`/`HUBPREQ3`, `HUBPRET2`/`HUBPRET3`, `CURSOR0_2`/`CURSOR0_3`, and `DC_PERFMON9`/`10` are structurally similar but not interchangeable.
- Surface address, pitch, metadata, DCC, and TMZ fields are high impact. Incorrect fields can cause corrupted planes, chroma corruption, blank output, protected-memory faults, metadata/DCC corruption, or display VM faults.
- Flip and update fields are handshake-sensitive. Bad pending, lock, clear, enable, or interrupt masks can cause missed page flips, stuck IRQs, frame pacing failures, or races during atomic commits.
- TTU, prefetch, vblank, nominal, and per-line delivery fields are bandwidth/timing-sensitive. Errors may only appear under high resolution, high refresh, multi-display, DCC, scaling, cursor, overlay, or low-memory-clock workloads.
- Scaler and line-buffer fields are mode-sensitive. Wrong tap, ratio, init, coefficient RAM, line-buffer partition, recout, MPC size, or overscan masks can distort images, misalign chroma, underflow, or fail only for specific scaling ratios and formats.
- Memory power, clock, reset, underflow, timeout, interrupt ack, and status fields may have side effects. Writes while blocks are gated, reset, scanning, or pending update can be ignored or disruptive.
- Field names containing repeated words such as `*_MASK_MASK` in perf/status families are generated from hardware field names and should not be manually simplified without updating all consumers.

## Test Signals

Useful validation combines generated-header checks with display behavior:

- Build AMDGPU/DC with DCN 3.1.6 enabled. Missing or renamed macros should fail in `dcn316_resource.c`, `dmub_dcn316.c`, and shared DCN31/HUBP/DPP/IPP users.
- Mechanically verify that each visible `__SHIFT` macro in lines 12383-14898 has the expected companion `_MASK` macro for the same register field where the generated schema defines one.
- Diff this slice against AMD's authoritative DCN 3.1.6 register database and against nearby generated generations where hardware compatibility is expected.
- Exercise enough active planes to use HUBP/HUBPREQ instances 2 and 3: primary plus overlays, chroma formats, DCC-enabled buffers, protected buffers, cursor planes, rapid page flips, multi-display, and suspend/resume.
- Run modes that stress timing and scaler paths: high resolution, high refresh, fractional scaling, 4:2:0/chroma planes, nonzero overscan, cursor movement, bandwidth-limited memory clocks, and multi-plane composition.
- Check page-flip and IRQ behavior with DRM page-flip tests, looking for missed flips, stuck pending bits, interrupt storms, or stale in-use addresses.
- Monitor kernel logs and hardware debug output for HUBP/HUBPREQ underflow, timeout, VM fault, DCC corruption, cursor artifacts, scaler artifacts, memory-power wait failures, and resume-only failures.
- Validate perfmon programming by enabling display performance counters and confirming event selection, clear/freeze/run, interrupt status/ack, and high/low counter readbacks behave plausibly.

## Cross-Chunk Notes

The previous chunk owns the beginning of the `CURSOR0_1_DMDATA_*` area. This chunk completes instance 1 DMDATA status/software data, covers complete instance 2 and 3 HUBP/HUBPREQ/HUBPRET/cursor/perfmon field groups, and starts DPP0 converter/scaler/color-management coverage. The next chunk must continue `CM0_CM_POST_CSC_C11_C12` and the rest of the DPP0 color-management register set before the merge lane writes a complete per-file report for `dcn_3_1_6_sh_mask.h`.

### subset-b-001903: lines 14899-17419

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 14899-17419

## Scope

This chunk is part of the generated AMDGPU DCN 3.1.6 register shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, includes, or executable control flow. The covered range has 2,521 source lines, 2,111 `#define` lines, and 398 register/group comments.

The chunk starts mid-register in the DPP0 color-management block: line 14899 contains the mask definitions for `CM0_CM_POST_CSC_C11_C12`, while the corresponding shift definitions are in the previous chunk. It ends mid-color-management table at `CM1_CM_GAMCOR_RAMA_REGION_22_23`, before that register's field definitions are complete. The merge lane must combine adjacent chunks before making whole-file or whole-register claims.

## Purpose

The purpose of this range is to publish bitfield ABI for DCN 3.1.6 display pipe programming. Each macro pairs a hardware register and field with either its bit offset or its bit mask:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a register field.
- `<REGISTER>__<FIELD>_MASK`: mask for the same field.

Driver register helpers use these constants with the matching DCN 3.1.6 address header to pack, update, and extract fields in memory-mapped display registers. The covered hardware areas are:

- DPP0 color-management tail: post-CSC, gamut remap, color bias, gamma correction, blend gamma, HDR multiplier, color memory power state, shaper LUTs, 3D LUT controls, and CM debug index/data.
- DPP0 top-level and perfmon blocks: DPP enable/clock/soft reset, DPP CRC, host read control, and display performance counter control/status/value registers.
- DPP1 converter/scaler blocks: surface format conversion, pre-CSC, cursor colors, scaler coefficients and ratios, line-buffer and output-buffer memory power controls.
- DPP1 color-management start: CM1 control, post-CSC, gamut remap, bias, gamma-correction LUT controls, and the first portion of gamma RAM A region descriptors.

## Important Definitions

The public surface is macro-only. The most important groups in this chunk are:

- `CM0_CM_POST_CSC_*` and `CM1_CM_POST_CSC_*`: 16-bit coefficient and bias fields for post color-space conversion matrices. Control fields include requested and current post-CSC mode.
- `CM0_CM_GAMUT_REMAP_*` and `CM1_CM_GAMUT_REMAP_*`: gamut-remap matrix coefficients and mode/current-mode fields, again represented as paired 16-bit matrix entries.
- `CM*_CM_BIAS_CR_R` and `CM*_CM_BIAS_Y_G_CB_B`: channel bias fields for color-management math.
- `CM0_CM_GAMCOR_*`, `CM0_CM_BLNDGAM_*`, and `CM1_CM_GAMCOR_*`: gamma and blend-gamma control, LUT index/data/control, and RAM A/B piecewise-linear region descriptors. These include LUT index fields, 18-bit LUT data fields, per-channel start/end/base/slope/offset fields, and packed region descriptors containing LUT offsets and segment counts.
- `CM0_CM_SHAPER_*`: shaper scale, offset, LUT index/data/write enable, and RAM A/B region descriptor fields used before 3D LUT processing.
- `CM0_CM_3DLUT_*`: 3D LUT mode, index, data, 30-bit data path, read/write control, output normalization, and per-channel output offsets.
- `CM0_CM_MEM_PWR_CTRL`, `CM0_CM_MEM_PWR_STATUS`, `CM0_CM_MEM_PWR_CTRL2`, and `CM0_CM_MEM_PWR_STATUS2`: power-force, power-disable, power-mode, and power-state fields for color-management RAMs.
- `DPP_TOP0_DPP_*`: top-level DPP enable/clock gating/reset controls, CRC value/control fields, and host read control.
- `DC_PERFMON11_*`: performance counter control, state, perfmon enable, condition select, threshold, value, and high/low counter fields.
- `CNVC_CFG1_*`: DPP1 converter configuration for surface pixel format, clamp/expansion/alpha settings, floating-point bias/scale, color keyer thresholds, alpha LUT, pre-dealpha/pre-realpha, pre-CSC mode/matrix, and coefficient format.
- `CNVC_CUR1_CURSOR0_*`: cursor enable, mode, expansion, premultiplied alpha, color0/color1, and cursor floating-point scale/bias fields.
- `DSCL1_*`: DPP1 scaler coefficient RAM access, scale mode, tap counts, manual replicate, horizontal/vertical luma/chroma ratios and initial phases, black color, update/autocal, overscan, timing windows, recout/MPC sizes, line-buffer format/memory control/status, OBUF control, and OBUF memory power control.

## Control Flow and State

This header has no runtime branches or calls. Runtime behavior comes from code that includes the generated address and shift/mask headers, selects a DPP instance, and calls AMD display register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, or field-table builders such as `TF_SF(...)`.

Typical use is:

1. The DPP, color, scaler, cursor, or perfmon code selects a generated register address for DCN 3.1.6.
2. A helper shifts a field value by `<REGISTER>__<FIELD>__SHIFT` and applies `<REGISTER>__<FIELD>_MASK`.
3. The helper writes the memory-mapped register, or reads it and extracts a field through the same constants.
4. Hardware latches the programmed value or exposes status/readback fields for later polling.

The chunk describes several persistent hardware states:

- Color pipeline state persists in post-CSC, gamut-remap, bias, gamma, blend-gamma, shaper, and 3D LUT registers until the driver reprograms them or the block is reset.
- LUT RAM programming is indexed and stateful. `*_LUT_INDEX`, `*_LUT_DATA`, `*_LUT_CONTROL`, `*_RAMA_*`, and `*_RAMB_*` fields define a host-programmed table and piecewise-linear segmentation for multiple channels and banks.
- Double-buffer/current-mode style state appears in fields such as `*_MODE_CURRENT`, `*_SELECT_CURRENT`, `CM_UPDATE_PENDING`, `DSCL_UPDATE_PENDING`, `DSCL_UPDATE_TAKEN`, and related scaler update bits.
- Memory power controls persist in DPP color, scaler line-buffer, and output-buffer memory power registers, with paired status fields exposing hardware state.
- Perfmon counters and DPP CRC/debug fields are readback-oriented state: software configures selection/enables, then reads captured values or status.

## Dependencies and Integration Points

This header depends on the generated AMD ASIC register naming contract. It is useful only with the matching DCN 3.1.6 register-address header and the AMD display register helper layer.

Important integration points:

- `drivers/gpu/drm/amd/display/dc/dpp/` headers define field lists with `TF_SF(...)` using the same register/field names. Those lists map generated `__SHIFT` and `_MASK` constants into typed DPP register structures for common color, scaler, and memory power code.
- DPP color management code consumes the CM, GAMCOR, BLNDGAM, SHAPER, and 3D LUT fields when programming color transforms, gamma curves, HDR multipliers, and LUT banks.
- DPP scaler code consumes `DSCL1_*` fields when configuring scaling ratios, taps, coefficient RAM, line-buffer format, viewport/recout sizing, and memory power behavior.
- Converter and cursor code consume `CNVC_CFG1_*` and `CNVC_CUR1_*` fields for pixel format, color keying, alpha handling, pre-CSC, cursor mode, and cursor colors.
- Diagnostics and validation paths consume DPP CRC, host read, test/debug, and `DC_PERFMON11_*` fields.

The `CM0`, `DPP_TOP0`, and `DC_PERFMON11` prefixes identify DPP0-side blocks, while `CNVC_CFG1`, `CNVC_CUR1`, `DSCL1`, and `CM1` identify corresponding DPP1-side converter, cursor, scaler, and color-management blocks. Shared suffixes allow common code to work across pipe instances while preserving per-instance register names.

## Risks and Edge Cases

- These constants are hardware ABI. A wrong shift or mask can silently write the wrong bits, producing incorrect color transforms, broken gamma/LUT programming, scaler artifacts, cursor corruption, failed memory power transitions, or misleading perfmon/CRC readings.
- The chunk boundaries are not semantic boundaries. `CM0_CM_POST_CSC_C11_C12` is missing its shift definitions here, and `CM1_CM_GAMCOR_RAMA_REGION_22_23` is incomplete at the end of the range.
- Many matrix and LUT fields are packed as two 16-bit halves, 18-bit LUT data values, 19-bit offsets, or 9-bit LUT offsets with 3-bit segment counts. Raw callers must rely on helper masking or validate values before packing to avoid truncation.
- Generated names with repeated suffixes, such as fields ending in `*_MASK_MASK`, are intentional when the hardware field itself is named `*_MASK`; reviewers should not simplify those identifiers locally.
- Current/pending/taken/status fields describe hardware handshakes but do not encode access semantics. Correct sequencing, polling, and write-one-to-clear behavior must come from driver code and hardware documentation.
- DPP0 and DPP1 blocks are similar but not fully represented in this single chunk. Absence of a matching `CM1` blend-gamma, shaper, or 3D LUT section here should be treated as a chunking artifact, not evidence that the full source lacks it.

## Test Signals

There are no unit-testable functions in this chunk. Useful validation is compile-time, generated-structure, and hardware integration focused:

- AMDGPU/DC builds that include `dcn_3_1_6_sh_mask.h` should compile with no undefined register-field macros for DCN 3.1.6 DPP color, converter, cursor, scaler, perfmon, or top-level code.
- Generated consistency checks should verify that every field has a matching shift/mask pair, masks align with shifts and expected widths, and replicated CM0/CM1 or DPP0/DPP1 fields match where hardware blocks are replicated.
- Display validation should exercise SDR/HDR color pipelines, post-CSC, gamut remap, gamma correction, blend gamma, shaper LUT, and 3D LUT programming on affected DCN 3.1.6 hardware.
- Scaler tests should cover luma/chroma scaling ratios, tap programming, coefficient RAM writes, overscan/recout sizing, line-buffer formats, and OBUF/line-buffer memory power transitions.
- Cursor and converter tests should cover surface pixel formats, alpha/keying paths, pre-CSC, cursor color/mode programming, and cursor scale/bias.
- Diagnostics should observe DPP CRC values, perfmon counter state/value updates, CM debug index/data reads, and status transitions for `*_PENDING`, `*_TAKEN`, memory power state, and LUT/control current-mode fields.

## Chunk Notes for Merge Lane

- Prefix distribution in this range: `CM0` has 1,310 `#define` lines, `CM1` has 265, `CNVC` has 154, `DSCL1` has 200, `DC` perfmon has 126, and `DPP` top-level has 56.
- Address-block comments in this chunk are `dce_dc_dpp0_dispdec_dpp_top_dispdec`, `dce_dc_dpp0_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`, `dce_dc_dpp1_dispdec_cnvc_cfg_dispdec`, `dce_dc_dpp1_dispdec_cnvc_cur_dispdec`, `dce_dc_dpp1_dispdec_dscl_dispdec`, and `dce_dc_dpp1_dispdec_cm_dispdec`.
- The final per-file research document should be produced later by the reconciliation lane after all chunks for `dcn_3_1_6_sh_mask.h` are available.

### subset-b-001904: lines 17420-19930

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 17420-19930

## Purpose

This chunk is generated AMD DCN 3.1.6 register field metadata. It contains no executable C logic; it exports preprocessor constants that describe hardware register bit positions (`__SHIFT`) and masks (`_MASK`) for the display pipe processor (DPP), color management, scaler, perfmon, and related DPP instance blocks. Runtime code pairs these constants with addresses from `dcn_3_1_6_offset.h` and then uses the AMD display register helpers to program MMIO fields.

The requested range covers 2,511 source lines with 2,113 `#define` entries and 386 generated register/address-block comments. It starts in the middle of `CM1_CM_GAMCOR_RAMA_REGION_18_19`, covers the rest of the DPP1 color-management/gamma-correction tail, DPP1 top/perfmon metadata, DPP2 converter/cursor/scaler/color-management metadata, and ends inside `CM2_CM_BLNDGAM_LUT_CONTROL`. Adjacent chunks are required for the beginning of DPP1 gamma correction and the rest of DPP2 blend-gamma RAM metadata.

Although this file lives under a local `ceph-client` source mirror, the content is AMDGPU display hardware metadata, not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, branches, or direct register reads/writes in this range. The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or updating that field.
- Address-block comments such as `// addressBlock: dce_dc_dpp2_dispdec_cm_dispdec`: generated grouping metadata that identifies the hardware block owning the following register fields.

Major register families in this chunk:

- `CM1_CM_GAMCOR_RAMA/RAMB_*`: tail of DPP1 gamma-correction programmable transfer-function RAM A/B fields. These define region start/end, start slope, start base, offsets, and 34 exponential region descriptors for blue/green/red channels.
- `CM1_CM_BLNDGAM_*`: DPP1 blend/output gamma control, LUT index/data/control fields, RAM A/B PWL region setup, offsets, and region descriptors.
- `CM1_CM_HDR_MULT_COEF`, `CM1_CM_DEALPHA`, `CM1_CM_COEF_FORMAT`, `CM1_CM_BIAS_*`, `CM1_CM_SHAPER_*`, and `CM1_CM_3DLUT_*`: DPP1 HDR multiplier, dealpha, coefficient format, shaper LUT, 3D LUT, output normalization/offset, memory-power, and debug fields.
- `DPP_TOP1_*`: DPP1 top-level clock enable/gating, soft reset, DPP CRC values/control, and host-read rate control fields.
- `DC_PERFMON12_*`: DPP1 display perfmon counter selection, counter state, run/clear/freeze/interrupt controls, current/high/low counter values, and interrupt/status fields.
- `CNVC_CFG2_*` and `CNVC_CUR2_*`: DPP2 converter surface pixel format, numeric format, alpha/keyer, pre-dealpha, pre-CSC matrices, pre-degamma, pre-realpha, cursor format/colors, and cursor FP scale/bias fields.
- `DSCL2_*`: DPP2 scaler coefficient RAM, scaler mode/taps/ratios/init values, recout/MPC/blanking geometry, line-buffer format and partitioning, memory power, output-buffer control, and status fields.
- `CM2_CM_*`: DPP2 color-management control, post-CSC and gamut-remap matrices, bias, gamma-correction control/LUT/RAM A/B, memory power, dealpha, coefficient format, shaper LUT, 3D LUT, debug, and the beginning of blend-gamma control/LUT fields.

Representative field patterns include 16-bit paired matrix coefficients, 13- or 14-bit geometry fields, 18-bit PWL base/slope/start values, 9-bit LUT offsets, 3-bit segment counts, 27-bit scaler ratios, per-channel color RAM selectors, current/active mode readback fields, memory-power force/disable/state fields, and write/ack/status bits for perfmon and LUT programming.

## Control Flow

This header chunk has no runtime control flow. Runtime sequencing is supplied by AMD display code:

1. DCN316 resource code includes `dcn_3_1_6_offset.h` and this `dcn_3_1_6_sh_mask.h`.
2. `dcn316_resource.c` builds `dpp_regs[]` with `DPP_REG_LIST_DCN30(id)` for DPP instances 0 through 3, and builds `tf_shift`/`tf_mask` with `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)`.
3. `dcn31_dpp_create()` passes the per-instance register addresses and shared shift/mask tables into `dpp3_construct()`.
4. DPP implementation code in the DCN10/DCN20/DCN30 family then calls register helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and multi-field variants to program scaler setup, color matrices, gamma/shaper/3D LUTs, blend gamma, memory power, clock/reset control, cursor format, and diagnostic readback.

The macros do not encode ordering rules. Consumers must still sequence update locks, scaler programming, color pipeline updates, LUT host selection, RAM A/B double buffering, memory-power transitions, clock gating, reset, perfmon clear/enable/readback, and CRC operations correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing in files or memory. It describes MMIO-backed display hardware state. The represented state includes:

- DPP1 and DPP2 color pipeline state: bypass/update bits, post-CSC and gamut-remap matrices, bias, HDR multiplier, dealpha, coefficient format, gamma-correction modes, blend-gamma modes, shaper state, 3D LUT mode/index/data/format, and output normalization/offset.
- PWL/LUT state for gamma correction, blend gamma, and shaper RAMs: active/select/current modes, LUT indexes/data, color write masks, host selection, region starts, slopes, bases, offsets, and exponential region descriptors.
- DPP top state: clock enable/gating controls, soft reset bits, CRC source/mode/control, CRC values, and host-read rate control.
- DPP1 perfmon state: counter event selection, counted value type, counter run/stop selectors, active/state bits, report count, current values, high/low values, interrupt enable/status/ack, and counter interrupt status/ack.
- DPP2 converter/cursor/scaler state: pixel format, expansion/alpha/keyer settings, pre-CSC/pre-degamma/pre-realpha, cursor control/color/scale/bias, scaler mode/taps/ratios/init values, overscan/blanking/recout/MPC geometry, line-buffer partitioning, output-buffer mode, and scaler/output-buffer memory power.

Persistence is hardware-defined. Configuration fields usually retain values until a modeset, plane update, power gating, suspend/resume, or ASIC reset. Status/current/pending/ack/readback fields may be live, sticky, self-clearing, read-only, or write-one-to-clear depending on the register. This generated header only supplies bit layout; it does not express access type, side effects, double-buffering rules, or reset defaults.

## Dependencies And Integration Points

This chunk must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`, which supplies matching MMIO register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes the generated DCN 3.1.6 headers and expands DPP register, shift, and mask lists.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h`, where `DPP_REG_LIST_DCN30` and `DPP_REG_LIST_SH_MASK_DCN30` map generic DPP fields onto generated register names.
- DPP implementation files in the DCN10/DCN20/DCN30 family, which use the resulting tables through register helpers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`, which also includes the DCN 3.1.6 generated headers for firmware-service register tables.

Important consumers and integration points:

- DPP construction creates up to four DPP instances on DCN 3.1.6. This chunk specifically covers instance-1 tail fields and instance-2 DPP/CNVC/DSCL/CM fields, so array instance mapping is critical.
- Color-management code uses `CM_GAMCOR`, `CM_BLNDGAM`, `CM_SHAPER`, `CM_3DLUT`, matrix, bias, dealpha, and HDR multiplier fields to implement DRM/AMDGPU color operations, HDR transfer functions, 3D LUT features, and plane/output gamma behavior.
- Scaler code uses `DSCL2_*` fields for manual scaler setup, line-buffer allocation, coefficient RAM programming, recout geometry, chroma/luma scaling, and memory-power handling.
- Cursor/converter paths use `CNVC_CFG2_*` and `CNVC_CUR2_*` fields for format conversion, alpha/keying, cursor format, cursor colors, and fixed-point cursor scale/bias.
- Diagnostics use `DPP_TOP1_DPP_CRC_*` and `DC_PERFMON12_*` for CRC and display perfmon validation.
- Resource capability setup in `dcn316_resource.c` advertises DPP color capabilities such as gamma correction, post CSC, hardware 3D LUT, output gamma RAM, and related color-management behavior that ultimately depends on these field definitions being correct.

## Risks And Edge Cases

- Generated-header drift is the central risk. These macros are untyped constants, so an incorrect shift or mask can compile cleanly while programming the wrong MMIO bits.
- The chunk boundary is artificial. Line 17420 is only the tail of a `CM1_CM_GAMCOR_RAMA` region register, and line 19930 stops inside `CM2_CM_BLNDGAM_LUT_CONTROL`; adjacent chunks are needed for complete DPP1 gamma and DPP2 blend-gamma coverage.
- Repeated DPP instance prefixes are copy-sensitive. `CM1`/`DPP_TOP1`/`DC_PERFMON12` and `CNVC_CFG2`/`DSCL2`/`CM2` describe different hardware instances; a valid-looking mask with the wrong prefix can drive the wrong pipe.
- Color pipeline fields are visually high impact. Wrong masks for CSC/gamut matrices, bias, coefficient format, degamma/gamma/blend/shaper/3D LUT, or HDR multiplier can cause color shifts, banding, broken HDR, bad alpha handling, or incorrect protected color-management state without crashing the kernel.
- PWL region fields are dense and repetitive. Off-by-one region descriptors, bad segment counts, wrong LUT offsets, or swapped channel fields can produce subtle transfer-function errors that only show under specific gamma/HDR/LUT configurations.
- LUT programming is double-buffered and selection-sensitive. Incorrect host-select, RAM A/B select, mode-current, write-color-mask, index, or data masks can update the inactive RAM, the wrong channel, or a partially visible LUT.
- Scaler and line-buffer fields are timing-sensitive. Bad tap counts, ratios, init fractions, recout size, line-buffer partitions, blanking geometry, or memory-power fields can create underflow, corrupted scaling, blank planes, or mode-specific failures.
- Clock, reset, memory-power, CRC, and perfmon fields may have side effects. Writes while a block is gated, reset, scanning out, or in a pending update can be ignored or disruptive. Status/ack fields may require exact clear/read order.
- Some current/status fields reflect hardware state rather than requested state. Tests that only write requested fields without checking current fields may miss failed updates or stale hardware state.

## Test Signals

Useful validation combines generated-header consistency checks with display behavior:

- Build AMDGPU/DC with DCN316 support. Missing or renamed macros should fail in `dcn316_resource.c`, `dcn30_dpp.h`, DCN30 DPP implementation files, and DMUB DCN316 code.
- Mechanically verify that every visible `__SHIFT` macro in lines 17420-19930 has the expected companion `_MASK` macro for the same field where the generated schema defines one.
- Diff this slice against AMD's authoritative DCN 3.1.6 register database and nearby generated DCN headers where hardware compatibility is expected.
- Exercise systems with enough active pipes to use DPP instances 1 and 2, including primary planes, overlays, scaling, cursor, SDR/HDR transitions, color-management updates, suspend/resume, and rapid atomic commits.
- Validate color paths with post-CSC, gamut remap, bias, HDR multiplier, gamma correction, blend gamma, shaper LUT, and 3D LUT programming. Signals include correct visual output, expected register dumps, no stale update-pending/current-mode state, and no channel swaps.
- Test LUT RAM A/B switching by updating gamma/blend/shaper LUTs while scanning out, then confirming that host selection, active selection, current mode, and per-channel data behave as expected.
- Run scaler stress modes: upscaling, downscaling, chroma formats, interleaved/alpha paths, large recout sizes, overscan, multiple displays, bandwidth-limited memory clocks, and memory low-power transitions. Watch for underflow, blanking, corruption, or bad line-buffer partitioning.
- Validate DPP CRC and `DC_PERFMON12` flows by clearing, selecting, enabling, freezing, reading, and acknowledging counters/status in the documented order; stale or impossible counter values are strong signals of field mismatch.
- Monitor kernel logs and display traces for DPP reset/gating problems, CM update-pending stalls, scaler memory-power state mismatches, LUT write failures, cursor/color-key artifacts, HDR/color regressions, and resume-only failures.

## Cross-Chunk Notes

The previous chunk owns the beginning of the DPP1 gamma-correction RAM A region tables, including the start of `CM1_CM_GAMCOR_RAMA_REGION_18_19`. The next chunk continues `CM2_CM_BLNDGAM_LUT_CONTROL` and should cover DPP2 blend-gamma RAM A/B region setup after the two fields visible at the end of this range. The final per-file report should merge adjacent chunks before making complete statements about all DPP instances, all gamma/blend/shaper RAMs, or the full DCN 3.1.6 shift/mask namespace.

### subset-b-001905: lines 19931-22447

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 19931-22447

## Scope

This chunk is a generated AMD DCN 3.1.6 register field header segment. It contains only C preprocessor constants: `__SHIFT` and `_MASK` values for packed hardware register fields. There are no functions, structs, storage definitions, or executable control-flow blocks in the chunk. Runtime behavior comes from consumers that include this header with the matching `dcn_3_1_6_offset.h` register-address header and feed the constants into AMD display register helper macros.

The source path must remain tied to `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h`; this is a partial chunk report for lines 19931-22447 only.

## Purpose

The chunk maps bit layouts for several display-pipe hardware blocks:

- Tail of DPP2 color-management blender gamma (`CM2_CM_BLNDGAM_*`) LUT, region, shaper, memory-power, 3D LUT, and debug fields.
- DPP2 top-level, host-read, CRC, and soft-reset fields (`DPP_TOP2_*`).
- DC perfmon block 13 fields (`DC_PERFMON13_*`) for counter control, counter state, value selection, manual/clear control, and high/low counter reads.
- DPP3 CNVC configuration and cursor fields (`CNVC_CFG3_*`, `CNVC_CUR3_*`) for pixel format, fixed-point conversion bias/scale, color keying, alpha LUT, pre-dealpha/pre-realpha, pre-CSC coefficients, and cursor color/control.
- DPP3 scaler/display scaler fields (`DSCL3_*`) for coefficient RAM, scaler modes, taps, ratios, recout/MPC sizes, line buffer state, memory power, and output buffer configuration.
- Start of DPP3 color-management fields (`CM3_CM_*`), including control, post-CSC, gamut remap, bias, gamma-correction LUTs, gamma-correction PWL region programming, blender-gamma control/LUTs, and the start of blender-gamma RAM B region programming.

The constants let shared DCN display code access hardware registers by symbolic field name instead of embedding numeric bit positions throughout the driver.

## Important APIs, Types, and Macro Contracts

This chunk does not define APIs in the function-call sense. Its public contract is the macro naming scheme:

- `REGISTER__FIELD__SHIFT` gives the right-shift amount for extracting or placing a field.
- `REGISTER__FIELD_MASK` gives the unshifted register mask for the same field.
- Register comments such as `//CM3_CM_BLNDGAM_RAMA_REGION_0_1` group the following field constants by hardware register.
- Prefixes encode instance/block identity. For example, `CM2_` is color management under DPP instance 2, `CM3_` is the DPP instance 3 color-management block, `DSCL3_` is scaler instance 3, and `DC_PERFMON13_` is perfmon instance 13.

The integration layer is visible in nearby consumers:

- `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` includes `dcn/dcn_3_1_6_offset.h` and this file, then initializes DPP shift and mask tables with `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)`.
- `drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.h` defines field-list macros and shift/mask table member lists for color-management fields such as `CM_BLNDGAM_RAMA_EXP_REGION*_LUT_OFFSET`, `CM_BLNDGAM_RAMB_EXP_REGION*_NUM_SEGMENTS`, `CM_3DLUT_*`, `CM_SHAPER_*`, and memory-power fields.
- `drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.c` uses register helpers such as `REG_GET` against fields like `CM_BLNDGAM_CONFIG_STATUS`, relying on the generated shift/mask tables populated from this header.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c` also includes this header for DCN316 DMUB-side register bit definitions.

## Register Groups in This Chunk

### CM2 Blender Gamma and Shaper Tail

Lines 19931-20376 complete the `CM2_CM_BLNDGAM_*` region that began before the chunk. The first visible entries finish `CM2_CM_BLNDGAM_LUT_CONTROL`, including write color mask, read color select, debug read, host select, and config mode fields. The section then defines:

- `CM2_CM_BLNDGAM_RAMA_*` start, slope, base, end, offset, and 34 region descriptors.
- `CM2_CM_BLNDGAM_RAMB_*` with the same double-buffered PWL region layout.
- Per-channel start/end fields for B, G, and R, generally with 18-bit or 19-bit value masks and segment selectors at shift `0x14`.
- Region-pair registers `REGION_0_1` through `REGION_32_33`, each packing two LUT offsets and two segment-count fields into one 32-bit register.

Lines 20377-20873 continue with CM2 color blocks: HDR multiplier coefficient, memory-power control/status, dealpha, coefficient format, shaper control/LUT/index/data, shaper RAM A/B region programming, second memory-power controls, 3D LUT mode/index/data/read-write control/out normalization/offsets, and test debug index/data.

These fields support the display color pipeline around programmable transfer functions: shaper LUT, blender gamma LUT, and 3D LUT. The hardware-visible state is register-resident, not persisted by this header.

### DPP2 Top and Perfmon

Lines 20874-20939 switch to `dce_dc_dpp2_dispdec_dpp_top_dispdec`. The defined fields cover DPP control, soft reset, CRC values/control, and host read control. These are top-level display-pipe control and diagnostics fields for instance 2.

Lines 20940-21076 switch to `dce_dc_dpp2_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`. The `DC_PERFMON13_*` fields describe performance-counter setup: enable/reset/start modes, event selectors, perfmon state bits, selected counter value fields, and high/low counter registers. Runtime code can configure these counters to observe display hardware behavior.

### DPP3 CNVC, Cursor, and Scaler

Lines 21077-21243 define `CNVC_CFG3_*` fields. The converter configuration includes surface pixel format, format expansion and alpha enable bits, fixed-point conversion biases/scales, color-key control and per-channel key values, a 2-bit alpha LUT, pre-dealpha, pre-CSC mode and coefficient matrices, coefficient format, pre-degamma, and pre-realpha.

Lines 21244-21271 define `CNVC_CUR3_*` cursor fields: cursor enable/mode/2x magnify/control bits, cursor color entries, and cursor fixed-point scale/bias fields.

Lines 21272-21508 define `DSCL3_*` fields. They cover scaler coefficient RAM tap select/data, scaler mode, tap control, DSCL control, two-tap control, manual replicate, horizontal/vertical scale ratios and initial phases for luma/chroma, black color, update/autocal, extended overscan, OTG blanking, recout and MPC sizing, line-buffer data/memory control, vertical counter, scaler memory-power control/status, output buffer control, and output-buffer memory-power control.

These fields are central to display-pipe programming. A wrong shift or mask can change scaling, cursor rendering, color conversion, memory power, or diagnostics on a specific DPP instance.

### DPP3 Color Management

Lines 21509-22447 define the start and middle of `dce_dc_dpp3_dispdec_cm_dispdec`:

- `CM3_CM_CONTROL`, post-CSC control and coefficient matrix fields.
- Gamut remap control and coefficient matrix fields.
- Bias registers for chroma/red and luma/green/chroma-blue channels.
- `CM3_CM_GAMCOR_*` mode, LUT index/data/control, RAM A/B start/slope/base/end/offset, and 34 region descriptors.
- `CM3_CM_BLNDGAM_CONTROL`, LUT index/data/control, RAM A region programming through region `32_33`, and start of RAM B programming through `CM3_CM_BLNDGAM_RAMB_REGION_2_3`.

The gamma-correction and blender-gamma sections use highly repetitive double-buffered RAM A/RAM B layouts. Start registers carry a base value and a start segment, slope/base/end registers define the piecewise-linear curve endpoints, offset registers apply per-channel offsets, and region-pair registers assign LUT offsets plus segment counts for regions 0-33.

## Control Flow

There is no local control flow. The effective runtime flow is indirect:

1. DCN316 resource code includes this header and the matching offset header.
2. Field-list macros expand the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants into `tf_shift` and `tf_mask` tables for a DPP instance.
3. Register helper macros such as `REG_GET`, `REG_SET`, or equivalent AMD DC helpers use the register address, mask, and shift to read-modify-write 32-bit hardware registers.
4. Higher-level display code programs color transforms, scalers, cursors, power gates, diagnostics, and performance counters through those helpers.

The generated constants therefore influence control flow elsewhere only by determining which bits the helpers read or modify.

## State and Persistence

The header itself has no memory state and no persistent storage. It defines compile-time constants. The state affected by those constants lives in:

- Memory-mapped DCN display registers.
- Hardware LUT RAMs or indexed register windows reached through LUT index/data/control fields.
- Runtime C structs such as DPP shift/mask tables initialized from the macros.

Hardware register writes persist only as long as the display hardware, power state, and driver programming sequence preserve them. Power gating, reset, mode-set, or suspend/resume can clear or reprogram the underlying hardware state.

## Dependencies and Integration Points

Primary dependencies are generated alongside this file:

- `dcn_3_1_6_offset.h` for register addresses and base indices.
- `reg_helper.h` and AMD display `REG_*` helper macros for actual MMIO access.
- DPP/DCN field-list declarations such as `DPP_REG_LIST_SH_MASK_DCN30` and DPP shift/mask structs.
- DCN316 resource construction in `dcn316_resource.c`, which binds these generated values to the DC runtime for the ASIC family.
- DMUB DCN316 support, which includes this header where firmware-facing display microcontroller code needs the same bitfield definitions.

The source is a vendor-generated ASIC register description. Consistency with hardware documentation and companion generated headers is more important than local readability.

## Risks

- Generated header drift: if a mask/shift changes without the matching offset header, DPP field-list macros, or hardware generation, register helpers may silently program wrong bits.
- Instance mismatch: `CM2_`, `CM3_`, `DSCL3_`, and `DC_PERFMON13_` prefixes must match the intended display-pipe instance. Reusing the wrong instance constants can target the wrong register layout or table slot.
- Packed-field mistakes are high impact. Many region registers pack two LUT offsets and two segment counts into one 32-bit register. A single incorrect mask can corrupt the neighboring region.
- Power-management fields such as `*_MEM_PWR_CTRL` and `*_MEM_PWR_STATUS` are sensitive to sequencing. Incorrect masks can leave LUT/scaler memories forced on, disabled, or in an unexpected power state.
- The chunk boundary cuts through logical groups. It starts in the middle of `CM2_CM_BLNDGAM_LUT_CONTROL` and ends before the full `CM3_CM_BLNDGAM_RAMB_*` group is complete, so whole-file reconciliation must merge adjacent chunks before final conclusions about coverage.

## Test Signals

Useful validation signals for changes touching this chunk are mostly integration and hardware-facing:

- Compile coverage for AMDGPU DCN316 paths, proving field-list macros still find all expected shift/mask names.
- Static checks that every `*_SHIFT` used by DPP/DCN shift structs has the corresponding `_MASK`, and vice versa.
- Diff checks against AMD-generated upstream register headers for DCN 3.1.6.
- Runtime display smoke tests on DCN316 hardware: mode set, cursor enable/move, scaling, color-management/gamma changes, HDR/3D LUT paths, suspend/resume, and memory-power transitions.
- Debugfs or driver diagnostics that read DPP CRCs, perfmon counters, LUT state, and memory-power status can reveal bad masks that compile cleanly.

## Chunk Notes for Merge Lane

This is not a standalone per-file report. Merge/reconciliation should combine it with the surrounding chunks for `dcn_3_1_6_sh_mask.h`, especially the prior chunk that contains the beginning of the CM2 color-management block and the following chunk that completes `CM3_CM_BLNDGAM_RAMB_*` and later DCN316 register groups.

### subset-b-001906: lines 22448-24952

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 22448-24952

## Scope

This chunk is part of the generated AMDGPU DCN 3.1.6 register shift/mask header. It contains C preprocessor constants only; there are no executable functions, structs, enums, or runtime branches in the covered lines. The chunk begins in the middle of the `CM3_CM_BLNDGAM_RAMB_REGION_2_3` mask definitions, then covers the tail of DPP3 color-management registers, DPP3 top-level and performance-monitor registers, MPC/MPCC compositor registers, and the beginning of MPCC output-gamma instance 1. It ends mid-register at `MPCC_OGAM1_MPCC_OGAM_RAMB_REGION_32_33__MPCC_OGAM_RAMB_EXP_REGION32_LUT_OFFSET_MASK`.

The public interface is the generated macro pair pattern:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: mask for the same field.

These values are hardware ABI for the DCN 3.1.6 display engine. Driver code uses them with generated register address headers and DC register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, and `SF(...)`-built mask/shift tables.

## Purpose

The chunk exposes bitfield layouts for several display pipeline areas:

- `CM3` color-management controls for DPP pipe 3, including blend-gamma RAM B region descriptors, HDR multiplier, memory power control/status, dealpha, coefficient formats, shaper LUT programming, shaper RAM A/B region descriptors, 3D LUT access, 3D LUT output normalization/offset, and test debug access.
- `DPP_TOP3` top-level DPP pipe 3 controls, including DPP clock enable/gating, soft reset for CNVC/DSCL/CM/OBUF sub-blocks, DPP CRC result/control fields, and host read rate control.
- `DC_PERFMON14` for the DPP3 performance-monitor address block, covering performance counter event selection, count/run/interrupt controls, counter state multiplexing, high/low count value readback, and interrupt status/ack fields.
- `MPCC0` through `MPCC3` compositor slice controls, including top/bottom source selection, OPP routing, alpha/blending/overlap controls, stereo/side-by-side controls, update-lock selection, gains, background color, memory power control, and MPCC busy/idle/status bits.
- Global `MPC` controls, including clock control, soft reset, CRC source/result selection, perfmon event selection, bypass background colors, host read control, DPP pending status, vupdate lock set programming, and DWB0 mux selection.
- `DC_PERFMON15` for the MPC performance-monitor block, with the same counter/control/readback pattern as `DC_PERFMON14`.
- `MPCC_OGAM0` and partial `MPCC_OGAM1` output-gamma and gamut-remap controls, including LUT index/data/control, RAM A/B piecewise-linear region start/end/slope/base/offset fields, 34 exponential region descriptors, output gamut-remap mode/format, and A/B coefficient matrices for `MPCC_OGAM0`.

## Important APIs, Types, and Definitions

There are no C APIs or types defined in this chunk. The important definitions are the register-field constants grouped by prefix.

`CM3_CM_*` definitions describe DPP3 color blocks:

- `CM3_CM_BLNDGAM_RAMB_REGION_4_5` through `CM3_CM_BLNDGAM_RAMB_REGION_32_33` encode paired blend-gamma RAM B region descriptors. Each pair has LUT offset fields and number-of-segments fields for two adjacent regions.
- `CM3_CM_HDR_MULT_COEF`, `CM3_CM_COEF_FORMAT`, and `CM3_CM_DEALPHA` expose HDR multiplier, coefficient fixed-point format selection, and dealpha enable/alpha blend behavior.
- `CM3_CM_MEM_PWR_CTRL`, `CM3_CM_MEM_PWR_STATUS`, `CM3_CM_MEM_PWR_CTRL2`, and `CM3_CM_MEM_PWR_STATUS2` expose power force/disable/state controls for gamma correction, blend-gamma, shaper, and 3D LUT memories.
- `CM3_CM_SHAPER_*` exposes shaper mode, RGB offsets/scales, host LUT index/data/write color masks, and RAM A/B start/end/region layout.
- `CM3_CM_3DLUT_*` exposes 3D LUT mode, index/data access, 30-bit data access, read/write control flags, output normalization factor, and RGB output offsets.

`DPP_TOP3_*` definitions describe the top-level state of DPP pipe 3:

- `DPP_TOP3_DPP_CONTROL` controls clock enable and fine-grained clock gating disables.
- `DPP_TOP3_DPP_SOFT_RESET` controls reset bits for DPP sub-blocks.
- `DPP_TOP3_DPP_CRC_VAL_R_G`, `DPP_TOP3_DPP_CRC_VAL_B_A`, and `DPP_TOP3_DPP_CRC_CTRL` select and read CRC diagnostics.
- `DPP_TOP3_HOST_READ_CONTROL` controls host read pacing.

`DC_PERFMON14_*` and `DC_PERFMON15_*` definitions describe display performance-monitor programming:

- `*_PERFCOUNTER_CNTL` selects events, cvalue inputs, increment modes, run-enable modes, restart, interrupt enable, active status, and counter selector fields.
- `*_PERFCOUNTER_CNTL2` selects counted value type and hardware stop/count-off selectors.
- `*_PERFCOUNTER_STATE` exposes eight packed counter state/select pairs.
- `*_PERFMON_CNTL`, `*_PERFMON_CNTL2`, `*_PERFMON_CVALUE_INT_MISC`, `*_PERFMON_CVALUE_LOW`, `*_PERFMON_HI`, and `*_PERFMON_LOW` expose monitor run state, report count, count-off interrupt controls, interrupt status/ack bits, and 64-bit-style readback split across high/low fields.

`MPCC0_*` through `MPCC3_*` definitions describe four multi-plane compositor components:

- `MPCC*_MPCC_TOP_SEL`, `MPCC*_MPCC_BOT_SEL`, and `MPCC*_MPCC_OPP_ID` select compositor inputs and output processor routing.
- `MPCC*_MPCC_CONTROL` defines alpha blending, mode/current mode, pre/post-multiply controls, overlap-only mode, and stereo controls.
- `MPCC*_MPCC_SM_CONTROL` defines slice/segment metadata for side-by-side operation.
- `MPCC*_MPCC_UPDATE_LOCK_SEL` selects which update-lock source gates updates.
- `MPCC*_MPCC_TOP_GAIN`, `MPCC*_MPCC_BOT_GAIN_INSIDE`, `MPCC*_MPCC_BOT_GAIN_OUTSIDE`, and `MPCC*_MPCC_BG_*` define blend gains and background color values.
- `MPCC*_MPCC_MEM_PWR_CTRL` and `MPCC*_MPCC_STATUS` expose MPCC memory power forcing/disabling/state plus busy and idle flags.

`MPC_*`, `ADR_*_VUPDATE_LOCK_SET*`, `CFG_*_VUPDATE_LOCK_SET*`, and `CUR_*_VUPDATE_LOCK_SET*` definitions describe global compositor behavior:

- `MPC_CLOCK_CONTROL` and `MPC_SOFT_RESET` gate or reset MPC sub-blocks.
- `MPC_CRC_CTRL`, `MPC_CRC_SEL_CONTROL`, and `MPC_CRC_RESULT_*` configure and read MPC CRC output.
- `MPC_DPP_PENDING_STATUS` and `MPC_PENDING_STATUS_MISC` expose pending DPP, OPP, MPCC, update-lock, and idle status bits.
- `ADR_CFG_CUR_VUPDATE_LOCK_SET*`, `ADR_CFG_VUPDATE_LOCK_SET*`, `ADR_VUPDATE_LOCK_SET*`, `CFG_VUPDATE_LOCK_SET*`, and `CUR_VUPDATE_LOCK_SET*` define per-lock-set address/config/current vupdate lock associations.
- `MPC_DWB0_MUX` chooses the DWB0 source.

`MPCC_OGAM0_*` and `MPCC_OGAM1_*` definitions describe per-MPCC output gamma:

- `MPCC_OGAM*_MPCC_OGAM_CONTROL` selects OGAM mode, LUT selection, PWL disable state, and current mode/select readback.
- `MPCC_OGAM*_MPCC_OGAM_LUT_INDEX`, `LUT_DATA`, and `LUT_CONTROL` expose host-indexed LUT programming and readback controls.
- `MPCC_OGAM*_MPCC_OGAM_RAMA_*` and `RAMB_*` define piecewise-linear RAM A/B start, start segment, start slope, start base, end base, end value, end slope, RGB offset, and paired region descriptors.
- `MPCC_OGAM0_MPCC_GAMUT_REMAP_*` and `MPCC_OGAM0_MPC_GAMUT_REMAP_C**_*` define gamut remap mode/current mode, coefficient format, and two coefficient banks. The equivalent `MPCC_OGAM1` gamut-remap coefficients begin after this chunk.

## Control Flow

There is no control flow in the header itself. Runtime flow is created by code that includes this header:

1. The driver selects a DCN 3.1.6 register address from the matching address header or a generated register table.
2. It chooses the field constants from this header through macros such as `FN(reg, field)` or `SF(reg, field, mask_sh)`.
3. `REG_GET`, `REG_UPDATE`, `REG_SET`, or related helpers shift and mask values using the generated constants.
4. The helper reads or writes the memory-mapped register, and hardware updates or reports state asynchronously.

The covered fields support several hardware protocols:

- LUT programming: shaper, 3D LUT, blend-gamma, and OGAM RAM fields are written by selecting an index/control mode, writing data, and programming region descriptors for RAM A/B.
- Double-buffer/current-state observation: fields with `*_CURRENT`, `*_PENDING`, and vupdate-lock names distinguish requested state from state taken by hardware at an update boundary.
- Power management: memory power force/disable/status fields in `CM3` and `MPCC*` allow software or firmware to force blocks on/off and then observe power state.
- Diagnostics: CRC and perfmon fields configure counters or CRC sources, start/stop counting, acknowledge interrupts, and read result fields.
- Compositor routing: MPCC and MPC fields persistently define source routing, blending, update locking, and output mapping until reprogrammed.

## State and Persistence

The macros are compile-time constants and hold no state. State persistence is entirely in hardware registers after memory-mapped writes. Important persistent or observable state includes:

- Programmed DPP3 color pipeline state: HDR multiplier, coefficient formats, shaper/3D LUT mode, RAM region descriptors, LUT contents, and memory power settings.
- Programmed MPCC compositor state: top/bottom input selections, OPP routing, blending controls, gains, background colors, update-lock selection, and memory power controls.
- Programmed MPC global state: clock/reset settings, CRC source selection, DPP/OPP/MPCC pending state, update-lock set mappings, and DWB0 mux source.
- Perfmon state: active counters, selected events, run-enable sources, count-off thresholds, interrupt status/ack bits, and high/low readback values.
- OGAM state: mode/select/current mode, PWL disable, LUT index/data/control, RAM A/B region descriptors, offsets, and gamut-remap matrices.

Fields named `*_STATUS`, `*_CURRENT`, `*_ACTIVE`, `*_BUSY`, `*_IDLE`, `*_STATE`, `*_PENDING`, `*_INT_STATUS`, and `*_ACK` should be treated as hardware handshake or readback fields rather than ordinary storage.

## Dependencies and Integration Points

This header depends on the generated AMD ASIC register contract:

- The matching DCN 3.1.6 register address header supplies the register offsets with the same register names.
- AMD display code includes `dcn/dcn_3_1_6_sh_mask.h`; for example the DMUB DCN 3.1.6 source includes it so firmware-facing register helpers can use the DCN 3.1.6 field layout.
- DC register-helper layers use the field constants through `REG_*` helper macros and generated `mask_sh` tables.
- MPC code for nearby DCN generations demonstrates the direct integration pattern with `SF(MPCC_OGAM0_..., field, mask_sh)` entries for OGAM LUT, RAM, and gamut-remap fields. The same generated field names in this chunk are intended for that style of per-generation register table.
- Display color, plane/compositor, diagnostics, performance-monitor, and DMUB paths are the primary consumers because this chunk covers DPP3 color management, DPP top, MPCC/MPC, OGAM, CRC, and perfmon fields.

The replicated instance prefixes are significant. `CM3` and `DPP_TOP3` identify DPP pipe 3, `MPCC0` through `MPCC3` identify compositor components, `DC_PERFMON14` and `DC_PERFMON15` identify separate perfmon address blocks, and `MPCC_OGAM0`/`MPCC_OGAM1` identify per-MPCC output gamma blocks.

## Risks and Edge Cases

- Generated-header drift is the main risk. Any incorrect shift or mask can silently write the wrong bits in display hardware, causing color corruption, bad blending, failed updates, broken CRC/perfmon diagnostics, missed interrupts, or display pipeline hangs.
- The chunk boundaries are not semantic boundaries. It starts after the first two masks for `CM3_CM_BLNDGAM_RAMB_REGION_2_3` and ends before the remaining masks for `MPCC_OGAM1_MPCC_OGAM_RAMB_REGION_32_33`. The later merge lane must combine neighboring chunks before making whole-register claims for those boundary registers.
- Names such as `*_MASK_MASK` are generated intentionally when the field itself is named `*_MASK`; they should not be manually simplified because users expect the generated `REGISTER__FIELD_MASK` contract.
- The header does not encode access semantics. Fields named `*_ACK`, `*_CLR`, `*_STATUS`, `*_CURRENT`, `*_ACTIVE`, and `*_PENDING` may have write-one-to-clear, read-only, latched, or update-boundary behavior that must be enforced by caller code and hardware documentation.
- Many LUT and region descriptors pack two region definitions into one register with small fields, for example 9-bit LUT offsets and 3-bit segment counts. Raw writes with out-of-range values can truncate or spill unless the register helper masks and caller validation are correct.
- Power-control bits can affect memories backing color or compositor blocks. Incorrect sequencing around memory power force/disable and LUT programming can lead to stale or invalid readback even if the bitfield constants are syntactically correct.
- MPCC update-lock fields and current-mode fields indicate hardware synchronization. Assuming writes take effect immediately can race vupdate or update-lock gating.
- `MPCC_OGAM0` is complete through gamut-remap bank B in this chunk, while `MPCC_OGAM1` is only complete through most RAM B region descriptors. Absence of `MPCC_OGAM1` gamut-remap definitions in this chunk does not imply absence from the source file.

## Test Signals

This chunk has no directly unit-testable function behavior. Useful validation signals are structural and integration-oriented:

- Compile AMDGPU display code for DCN 3.1.6 with this header included; undefined macro errors catch missing or renamed generated fields.
- Compare generated `__SHIFT`/`_MASK` pairs against the authoritative ASIC register database for DCN 3.1.6.
- Run static checks that every field used in DCN 3.1.6 `mask_sh` tables has both a shift and mask definition.
- Validate mask/shift consistency mechanically: masks should align with their shifts, paired low/high fields should not overlap, and full-register fields such as low counter values should use `0xFFFFFFFFL`.
- Exercise display modes that program DPP3 color management, shaper/3D LUT, MPCC blending, OGAM, and gamut remap, then verify visual output or CRC stability.
- Exercise perfmon and CRC debug paths: counters should start/stop, interrupt status/ack bits should behave, and high/low result fields should produce plausible values.
- Exercise update-lock and vupdate paths by changing MPCC/MPC state during active scanout and confirming no stuck `*_PENDING`, `*_BUSY`, or update-lock status remains.
- Exercise power-management transitions around CM and MPCC memories, checking that status fields match programmed force/disable values and that LUT programming survives required power states.

### subset-b-001907: lines 24953-27463

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 24953-27463

## Purpose

This chunk is a generated DCN 3.1.6 AMD display ASIC register shift/mask slice. It contains preprocessor constants only: 2,097 `#define` entries, split into 1,048 `__SHIFT` macros and 1,049 `_MASK` macros. The constants describe bit positions and register-value masks for MPC/MPCC color pipeline blocks and the beginning of the ABM0 backlight/PWM block. They are paired with `dcn_3_1_6_offset.h` register-address macros and consumed by DCN 3.1.6 display resource construction and register helper code.

Although this repository path is under `sources/distributed-fs/ceph-client`, the file is AMDGPU display-driver hardware metadata, not Ceph filesystem logic. There are no functions, structs, enums, heap objects, locks, syscalls, or executable control-flow statements in this chunk.

The range has artificial boundaries. It starts after the first field of `MPCC_OGAM1_MPCC_OGAM_RAMB_REGION_32_33`; adjacent previous lines define that register's `REGION32_LUT_OFFSET__SHIFT`. It ends at the comment for `ABM0_BL1_PWM_BL_UPDATE_SAMPLE_RATE`, before that register's fields are emitted.

## Covered Hardware Blocks

- Tail of `MPCC_OGAM1`: final RAMB region 32/33 fields plus output-gamma gamut-remap coefficient format, remap mode/current-mode, and A/B matrix coefficient fields.
- Complete `dce_dc_mpc_mpcc_ogam2_dispdec`: `MPCC_OGAM2` output-gamma control, LUT index/data/control, RAM A and RAM B PWL curve descriptors, and gamut-remap matrix banks.
- Complete `dce_dc_mpc_mpcc_ogam3_dispdec`: the same `MPCC_OGAM3` output-gamma, PWL RAM A/B, and gamut-remap field surface.
- `dce_dc_mpc_mpc_ocsc_dispdec`: MPC output mux, denormalization, output color-space conversion (OCSC) coefficient banks for outputs 0-3, and OCSC test/debug access.
- `dce_dc_mpc_mpc_rmu_dispdec`: RMU mux/memory-power control, RMU0 and RMU1 shaper LUT/PWL fields, and RMU0/RMU1 3D LUT fields. RMU0 starts at global control and RMU1 is complete through 3DLUT output offsets.
- Start of `dce_dc_opp_abm0_dispdec`: ABM0 BL1 PWM ambient/user/target/current levels, final/minimum duty-cycle fields, and ABM PWM policy control.

## Important APIs, Types, and Macros

The naming contract is generated and token-paste driven:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask after shifting into register-value position.
- Some names intentionally include repeated `MASK` tokens, such as `MPC_RMU1_SHAPER_LUT_WRITE_EN_MASK__MPC_RMU_SHAPER_LUT_WRITE_EN_MASK_MASK`, because the hardware field itself is named `*_MASK`.

Important field families in this chunk include:

- `MPCC_OGAM<n>_MPCC_OGAM_CONTROL`: active OGAM mode, RAM select, PWL disable, and current mode/select readback.
- `MPCC_OGAM<n>_MPCC_OGAM_LUT_INDEX`, `LUT_DATA`, and `LUT_CONTROL`: host programming cursor, 18-bit LUT data, per-color write mask, read color selection, debug-read enable, host RAM selection, and config mode.
- `MPCC_OGAM<n>_MPCC_OGAM_RAMA_*` and `RAMB_*`: two hardware RAM-bank descriptions for output-gamma PWL curves. Region registers pack two regions per register with `LUT_OFFSET` fields at bits 0/16 and `NUM_SEGMENTS` fields at bits 12/28.
- `MPCC_OGAM<n>_MPCC_GAMUT_REMAP_*` and `MPC_GAMUT_REMAP_Cxx_Cyy_[AB]`: gamut-remap coefficient format, active/current bank/mode, and packed 16-bit coefficient pairs for A/B matrix banks.
- `MPC_OUT<n>_MUX`, `DENORM_*`, and `CSC_*`: output routing/rate-control, denormalization clamp controls, output CSC mode/current mode, and A/B coefficient matrices.
- `MPC_RMU_CONTROL` and `MPC_RMU_MEM_PWR_CTRL`: RMU mux selection/status and force/disable/state fields for RMU0/RMU1 shaper and 3DLUT memories.
- `MPC_RMU<n>_SHAPER_*`: shaper LUT mode/current mode, RGB offset/scale, LUT index/data/write enables, RAM A/B PWL start/end/region descriptors.
- `MPC_RMU<n>_3DLUT_*`: 3DLUT mode/size/current mode, index, 16-bit paired data path, 30-bit data path, RAM select/write/read controls, output normalization factor, and RGB output offset/scale.
- `ABM0_BL1_PWM_*`: 17-bit ambient, user, target, current, final-duty, and minimum-duty values plus enable and auto-update policy bits.

The direct integration points are visible in this tree. `display/dc/resource/dcn316/dcn316_resource.c` includes `dcn_3_1_6_sh_mask.h`, then builds `mpc_regs`, `mpc_shift`, and `mpc_mask` with `MPC_REG_LIST_DCN3_0`, `MPC_RMU_GLOBAL_REG_LIST_DCN3AG`, `MPC_RMU_REG_LIST_DCN3AG(0/1)`, and `MPC_COMMON_MASK_SH_LIST_DCN30`. It also builds ABM register/shift/mask tables with `ABM_DCN302_REG_LIST` and `ABM_MASK_SH_LIST_DCN30`. `display/dmub/src/dmub_dcn316.c` includes the same generated header for DMUB register-table constants. `display/dc/mpc/dcn30/dcn30_mpc.h` provides the MPC list and mask/shift macros that consume the `MPCC_OGAM`, `MPC_OUT`, and `MPC_RMU` field names; `display/dc/dce/dce_abm.h` consumes the ABM0 BL1 PWM field names through `ABM_SF(...)`.

## Control Flow and State

This header has no local runtime control flow. Its constants are compiled into register descriptor structures. Runtime display code later passes those descriptors to helper macros such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, and `REG_WAIT`, which perform MMIO reads, bit masking, shifts, writes, and polling.

The state represented by the chunk is hardware state:

- Output gamma state: active/bypass mode, selected RAM bank, PWL disable state, current-mode/current-bank readback, LUT cursor position, LUT payload contents, and PWL curve region geometry for `MPCC_OGAM1` tail plus full `MPCC_OGAM2` and `MPCC_OGAM3`.
- Gamut-remap state: coefficient format, active/current remap mode, and two coefficient banks. The A/B matrix registers allow software to stage one bank while another is active, depending on hardware sequencing.
- MPC output state: mux routing/source selection for outputs 0-3, rate/flow control, denormalization mode and clamp limits, and output CSC coefficient banks with current-mode readback.
- RMU state: mux selection/status, memory-power force/disable/status bits, shaper LUT mode/current state, 1D shaper LUT contents, shaper PWL RAM A/B regions, 3DLUT mode/size/current state, 3DLUT RAM selection, 16-bit or 30-bit data path selection, output normalization, and output offset/scale.
- ABM/PWM state: ambient-light, user, target, current ABM level, final/minimum duty cycle, and hardware auto-update policy bits for BL1 PWM.

Persistence is hardware-local. LUT RAM contents, matrix coefficients, mux selections, and PWM levels persist in the display engine until overwritten, reset, or lost through power/reset sequencing. Indexed registers such as LUT and 3DLUT index/data pairs form stateful write streams, so write order and cursor reset are part of the hardware programming contract even though they are not encoded by this header.

## Dependencies and Integration Points

This chunk depends on exact DCN 3.1.6 register database generation. It must remain aligned with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`, which supplies the matching register offsets and base-index values.
- `display/dc/resource/dcn316/dcn316_resource.c`, which instantiates DCN 3.1.6 resource objects and populates the MPC and ABM register tables from generated offset/shift/mask macros.
- `display/dc/mpc/dcn30/dcn30_mpc.h` and `dcn30_mpc.c`, where common DCN3 MPC code expects the field names and widths used for MPCC OGAM, MPC OCSC, and RMU programming.
- `display/dc/dce/dce_abm.h` and ABM implementation code, which use the ABM0 field names as common mask/shift templates for ABM instances.
- `display/dmub/src/dmub_dcn316.c`, which includes this header for DCN 3.1.6 DMUB register descriptors.
- Register helper infrastructure in `reg_helper.h`, where masks and shifts are interpreted as bitfield metadata for MMIO helper calls.

The repeated instance prefixes are part of the ABI between generated headers and handwritten display code. Resource construction uses instance-aware offset macros for `MPCC_OGAM2`, `MPCC_OGAM3`, `MPC_OUT0`-`MPC_OUT3`, and `MPC_RMU0`/`MPC_RMU1`, while common mask/shift lists often use instance-0 names as templates for shared field layouts.

## Risks and Edge Cases

- A wrong mask or shift can compile cleanly while programming the wrong bits. Visible failures include color corruption, wrong gamma curves, broken gamut remap, blank or misrouted outputs, incorrect CSC/clamp behavior, failed 3DLUT programming, or incorrect panel backlight behavior.
- The chunk boundaries split logical registers. `MPCC_OGAM1_MPCC_OGAM_RAMB_REGION_32_33` is incomplete at the top boundary, and `ABM0_BL1_PWM_BL_UPDATE_SAMPLE_RATE` begins only as a comment at the bottom boundary. The merge lane must reconcile adjacent chunks before making whole-file completeness claims.
- Banked LUT programming is order-sensitive. Software must select the inactive RAM bank, reset the index, write all expected entries with the correct color write mask, and switch modes only after data and region descriptors are valid.
- Status/current fields use the same macro shape as writable fields. Code that treats all fields as ordinary read-write bits can corrupt control registers or misread synchronization state.
- Memory-power state matters for RMU shaper and 3DLUT memories. Writes while memories are disabled or still transitioning can be dropped or read back inconsistently; runtime code uses waits and status reads around those paths.
- Repeated instance blocks are copy/regeneration-sensitive. A prefix mix-up between `MPCC_OGAM2` and `MPCC_OGAM3`, `MPC_OUT2` and `MPC_OUT3`, or RMU0 and RMU1 can affect only one pipe/path, making bugs display-topology dependent.
- Packed coefficient fields and limited-width value fields can silently truncate data if callers pass values outside expected fixed-point ranges. Examples include 16-bit coefficient halves, 18-bit LUT/PWL values, 17-bit PWM levels, and 9-bit LUT indices.

## Test and Validation Signals

- Build coverage for DCN 3.1.6 display code should catch missing or misspelled field macros in `dcn316_resource.c`, `dmub_dcn316.c`, `dcn30_mpc.h`, and `dce_abm.h`.
- Generated-header checks should verify that complete in-range registers have paired `__SHIFT` and `_MASK` definitions, while allowing the two documented boundary exceptions.
- Register-table sanity checks should compare `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h` for the repeated `MPCC_OGAM2/3`, `MPC_OUT0-3`, `MPC_RMU0/1`, and ABM0 field families.
- Hardware or emulator validation should exercise mode set, multi-pipe composition, output mux routing, CSC/denorm programming, gamma LUT updates, gamut-remap updates, RMU shaper programming, RMU 3DLUT programming, suspend/resume, and memory-power transitions.
- Useful runtime readbacks include `MPCC_OGAM_MODE_CURRENT`, `MPCC_OGAM_SELECT_CURRENT`, `MPCC_GAMUT_REMAP_MODE_CURRENT`, `MPC_OCSC_MODE_CURRENT`, `MPC_RMU*_MUX_STATUS`, `MPC_RMU*_SHAPER_MEM_PWR_STATE`, `MPC_RMU*_3DLUT_MEM_PWR_STATE`, `MPC_RMU_3DLUT_MODE_CURRENT`, and ABM current/final PWM level registers.

## Chunk Boundary Notes

The previous chunk is required for the beginning of `MPCC_OGAM1_MPCC_OGAM_RAMB_REGION_32_33`, including the missing `REGION32_LUT_OFFSET__SHIFT` line. The next chunk is required for `ABM0_BL1_PWM_BL_UPDATE_SAMPLE_RATE` and the remaining ABM0 register family. This document should be merged with neighboring chunk notes before producing a final per-file report for `dcn_3_1_6_sh_mask.h`.

### subset-b-001908: lines 27464-30059

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 27464-30059

## Scope

This chunk is part of the generated DCN 3.1.6 register shift/mask header used by the AMD display driver. It covers hardware bitfield definitions for output-pixel-processing and output-data-merge related display blocks:

- The tail of `dce_dc_opp_abm0_dispdec`, then complete ABM replicas for `ABM1`, `ABM2`, and `ABM3`.
- Four repeated OPP pipe slices, each with display pattern generator (`DPGx`), formatter (`FMTx`), OPP buffer (`OPPBUFx`), OPP pipe control, and OPP pipe CRC registers.
- DSC remap/forwarding blocks `DSCRM0` through `DSCRM2`.
- OPP top-level clock and ABM selection registers.
- OPP performance monitor register masks for `DC_PERFMON16`.
- ODM input blocks for `ODM0`, `ODM1`, `ODM2`, and the beginning of `ODM3`.

The file contains no functions or runtime code. Its purpose is to expose C preprocessor constants named `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` so register access helpers in the AMD DC code can compose, write, read, and decode DCN 3.1.6 MMIO register fields without hard-coded bit arithmetic at call sites.

## Important API Surface

The exported API is a generated macro namespace. Each register field appears as a pair of constants:

- `...__SHIFT` gives the low bit index for the field.
- `..._MASK` gives the already-positioned mask for the field.

The important register families in this chunk are:

- `ABM[0-3]_BL1_PWM_*` and `ABM[0-3]_DC_ABM1_*`: adaptive backlight management, PWM brightness levels, ambient/user/target/current/final duty-cycle fields, ambient contrast enhancement (`ACE`) curve fields, histogram (`HG`) and luma statistics (`LS`) fields, sample-rate controls, read-progress/missed-frame flags, and master-lock bits.
- `DPG[0-3]_*`: display pattern generator enable, mode, dynamic range, bit depth, active dimensions, ramp controls, RGB/YCbCr pattern colors, segment offsets, and double-buffer-pending status.
- `FMT[0-3]_*`: formatter clamp ranges, dynamic expansion, pixel encoding, subsampling, dither/truncation controls, random dither seeds, clamp enable/color format, 4:2:0 memory low-power controls, and 4:2:2 edge handling.
- `OPPBUF[0-3]_*`: OPP buffer active width, segmentation, overlap, pixel repetition, double-buffer pending, 3D dummy-data/vertical-active spacing, and segment padded pixels.
- `OPP_PIPE[0-3]_OPP_PIPE_CONTROL`: per-pipe clock enable/on status and digital bypass control.
- `OPP_PIPE_CRC[0-3]_*`: per-pipe CRC enable/configuration, one-shot pending state, CRC mask, and result fields for A/R/G/B/C components.
- `DSCRM[0-2]_DSCRM_DSC_FORWARD_CONFIG`: DSC forwarding enable, OPP-pipe source selection, double-buffer pending, and enable status.
- `OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL`: OPP clock gating/test clock selection, ABM clock-on status for ABM0-3, and backlight PWM source selection.
- `DC_PERFMON16_*`: performance counter event selection, count modes, hardware start/stop/off controls, active state, interrupt enable/status/ack fields, counter state slots 0-7, current-value high/low reads, and read selector.
- `ODM[0-3]_OPTC_*`: ODM input soft reset, underflow interrupt/status/clear fields, double-buffer pending, input/output segment counts, segment source selectors, DSC data format, DSC bytes per pixel, segment/DSC slice widths, input clock control, memory selection/status, and spare register fields. The chunk ends after `ODM3_OPTC_DATA_SOURCE_SELECT`, so the remaining ODM3 fields are in the next chunk.

## Control Flow and State Behavior

There is no direct control flow in this header, but the bitfields model several hardware sequencing patterns that driver code must observe:

- ABM writes are synchronized with lock and double-buffer fields. The `ABM1_HGLS_REG_LOCK`, `ABM1_ACE_LOCK`, `ABM1_BL_MASTER_LOCK`, `*_REG_UPDATE_PENDING`, `*_UPDATE_AT_FRAME_START`, `*_FRAME_START_DISP_SEL`, `*_READBACK_DB_REG_VALUE_EN`, and `*_IGNORE_MASTER_LOCK_EN` fields indicate that parts of ABM state are latched at frame boundaries and may have readback-vs-shadow behavior.
- ABM statistics are frame-derived hardware state. `LS_SUM_OF_LUMA`, `LS_MIN_MAX_LUMA`, filtered min/max, pixel counts, min/max value counts, and `HG_RESULT_1` through `HG_RESULT_24` are hardware-produced measurements. Sample-rate controls can enable counting, reset frame counters, and set frame-count periods.
- `ACE_CNTL_MISC` and `HGLS_REG_READ_PROGRESS` expose missed-frame and clear bits. Code using these fields needs write-one-style clear behavior awareness from the register spec and should not treat status and clear bits as ordinary persistent configuration.
- DPG, FMT, OPPBUF, DSCRM, and ODM fields include double-buffer-pending bits. These are hardware state signals used to confirm whether a programmed update has latched, especially around timing-sensitive mode changes.
- OPP pipe CRC has both continuous and one-shot modes. The `ONE_SHOT_PENDING` field and result registers imply a sequence of enable/configure, wait for completion/pending clear, then read result fields.
- Performance monitor fields encode a small state machine. `PERFMON_STATE`, per-counter `PERFCOUNTER_CNTx_STATE`, active bits, interrupt status/ack bits, run-enable selectors, and current-value reads define runtime sampling behavior, not static configuration.
- ODM input-global fields carry underflow status/current-status/interrupt/clear fields and input soft reset. These are critical display-pipeline health and recovery controls.

## Dependencies and Integration Points

This header is paired with the DCN 3.1.6 offset header, usually `dcn_3_1_6_offset.h`, whose register-address macros share the same register names. Runtime access typically flows through AMD DC register helpers and register lists that combine an offset macro with the corresponding field shift/mask macros from this file.

Downstream integration points include:

- Display Core resource and hardware-sequencer code that initializes OPP/FMT/DPG/ODM blocks during mode set, pipe bring-up, stream enable, DSC routing, and pipe split/ODM combine.
- ABM/backlight code that configures adaptive brightness, luma/histogram collection, sample cadence, and PWM output source selection.
- CRC debug/test paths that program OPP pipe CRC and read component results for validation.
- Performance/debug paths that program `DC_PERFMON16` to count selected display events and acknowledge generated counter interrupts.
- DMUB/DCN 3.1.6 setup tables that include this generated ASIC header to access the right field layout for this hardware revision.

The macro naming and bit positions are an ABI-like contract between generated register headers and the rest of the kernel display driver. Adjacent chunks define previous and later address blocks in the same register namespace; the final per-file research should merge them as one generated hardware register map.

## Risks and Edge Cases

- Field-name repetition across instances is intentional. ABM, DPG, FMT, OPPBUF, OPP pipe, CRC, and ODM instances differ mainly by numeric prefix. A copy/paste or generator error in one instance can silently program the wrong field for only one pipe.
- Some fields are status or acknowledge/clear controls, not normal read-write configuration. Examples include ABM missed-frame clear bits, perfmon interrupt acks, ODM underflow clear, and many `*_PENDING` or `*_STATUS` fields. Generic read-modify-write code can accidentally clear or preserve hardware state incorrectly if it does not know field semantics.
- The `MASK` constants are already shifted. Callers must not shift them again when using common `REG_SET`, `REG_GET`, or field-preparation helpers.
- Several registers pack signed or scaled values into 10-, 11-, 12-, 14-, 16-, 24-, or full 32-bit fields. Bounds errors in callers can truncate brightness levels, ACE slopes/offsets, active dimensions, DSC slice widths, CRC masks, or performance event selectors.
- Lock/update-at-frame-start fields mean mode-set and backlight changes can be asynchronous. Tests that read immediately after a write may observe old shadow state unless they select readback behavior or wait for update-pending bits.
- The chunk boundary cuts `ODM3` in the middle of its register group. Any generated documentation or analysis must reconcile with `subset-b-001909` before treating ODM3 coverage as complete.
- These constants are ASIC-specific. Reusing them for a different DCN revision can produce valid C that writes invalid hardware bit positions.

## Test Signals

Useful validation signals for code paths using this chunk include:

- Build coverage for DCN 3.1.6 display code, ensuring every referenced register field macro resolves with the matching offset macro.
- Mode-set tests across four OPP pipes that exercise FMT pixel encoding/subsampling, DPG patterns, OPPBUF segmentation, and ODM segment/source programming without underflow.
- Backlight/ABM tests that verify PWM level changes, ABM enable/bypass, sample-rate updates, histogram/luma statistic reads, and missed-frame clear behavior.
- DSC/ODM tests that enable DSCRM forwarding and ODM DSC data format/bytes-per-pixel/slice-width fields, then confirm double-buffer pending clears and no ODM underflow status remains set.
- CRC tests that configure each `OPP_PIPE_CRC[0-3]` path in one-shot and continuous modes and compare stable result registers for known DPG output.
- Perfmon tests that select a display event, enable counting/interrupts, observe `PERFCOUNTER_ACTIVE`/state fields, read high/low/current values, and acknowledge interrupt status without leaving counters armed.

### subset-b-001909: lines 30060-32529

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 30060-32529

## Scope

This chunk is a generated DCN 3.1.6 register-field shift/mask slice. It contains C preprocessor constants only: every exported symbol is a `_SHIFT` or `_MASK` macro for a hardware register field, plus comments that identify register names and address-block boundaries. There are no C functions, structs, enums, allocations, loops, branches, or direct MMIO operations in this range.

The range starts at the tail of the `ODM3_OPTC_*` output data formatter fields, then covers the `dce_dc_optc_otg0_dispdec`, `dce_dc_optc_otg1_dispdec`, and `dce_dc_optc_otg2_dispdec` address blocks. The `OTG0`, `OTG1`, and `OTG2` blocks are highly repetitive and describe timing-generator fields for display timing, dynamic refresh, global synchronization, CRC capture, stereo/interlace state, interrupts, update locking, clocking, and status readback. The chunk ends at the `OTG2_OTG_SPARE_REGISTER` marker, before its field definitions appear in the next chunk.

## Purpose And Hardware Surface

This header provides the bit-layout ABI used by AMDGPU Display Core when programming DCN 3.1.6 output timing generators and the tail of an ODM/OPTC formatter block. Companion generated offset headers provide register addresses; this file supplies the masks and shifts that register-helper macros use to pack values into MMIO writes and decode MMIO reads.

Major hardware areas represented here:

- `ODM3_OPTC_*`: final fields for ODM/OPTC segment source selection, data format and DSC mode, DSC bytes-per-pixel, segment and DSC slice widths, input clock gating/enabling/status, memory selection/status, and spare input bits.
- `OTG0`, `OTG1`, and `OTG2` base timing: horizontal total, horizontal blanking, horizontal sync A, horizontal timing divider controls, vertical total/min/max/mid values, vertical blanking, vertical sync A, and vertical-total control fields for dynamic timing changes.
- Trigger and flow controls: trigger A/B source, pipe, polarity, edge detection, frequency, delay, manual trigger, force-count-now, manual flow control, and flow-control input status.
- Timing state readback: active/blank/sync/update status, current horizontal/vertical counters, nominal vertical counter, frame/VF/HV counters, pixel data readback, interlace state, stereo state, field selection, and snapshot registers.
- Interrupt and event fields: vertical-total event status, nominal-vsync status, vertical interrupt 0/1/2 position and control registers, trigger/force-count/snapshot/vsync/GSL interrupt masks and types, and global sync event state.
- CRC and validation registers: CRC control, DSC/data-format CRC mode, two programmable CRC windows, four CRC data result groups, and CRC signature masks.
- Update and synchronization controls: OTG update lock, double-buffer pending flags, master enable, static-screen detection, 3D structure control, global swap-lock (GSL) control and windows, master update lock, vupdate keepout, global update controls, and pipe update pending status.
- Dynamic refresh and clocking: DRR timing interrupt/status, DRR v-total reach range, v-total change limit, DRR trigger window, DRR average-frame/last-used-vtotal readback, m-constant DTO phase/modulo, clock enable/gate/reset/status, vstartup/vupdate/vready parameters, and DSC start position.

## Important Definitions

The generated interface follows the standard AMD display register naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit mask for the field.
- `// addressBlock: ...` comments mark hardware instance blocks.
- `//<REGISTER>` comments group all following field macros for that register.

Important macro families in this chunk:

- `ODM3_OPTC_DATA_FORMAT_CONTROL`, `ODM3_OPTC_BYTES_PER_PIXEL`, and `ODM3_OPTC_WIDTH_CONTROL` define DSC/output-format packing fields such as `OPTC_DATA_FORMAT`, `OPTC_DSC_MODE`, `OPTC_DSC_BYTES_PER_PIXEL`, `OPTC_SEGMENT_WIDTH`, and `OPTC_DSC_SLICE_WIDTH`.
- `ODM3_OPTC_INPUT_CLOCK_CONTROL` and `ODM3_OPTC_MEMORY_CONFIG` expose input clock gate/enable/on status and OPTC memory selection/status for the ODM3 instance.
- `OTGx_OTG_H_*` and `OTGx_OTG_V_*` macros define the timing model: totals, blanking start/end, sync start/end, sync polarity/mode, timing divider mode, and DRR-oriented min/max/mid v-total controls.
- `OTGx_OTG_V_TOTAL_CONTROL`, `OTGx_OTG_DRR_*`, and `OTGx_OTG_M_CONST_DTO*` define variable-refresh and dynamic-refresh behavior: v-total source selection, min/max/mid replacement, forced lock events, event-active period, v-total reach interrupts, trigger windows, change limits, averaging, and DTO phase/modulo.
- `OTGx_OTG_TRIGA_*`, `OTGx_OTG_TRIGB_*`, `OTGx_OTG_FORCE_COUNT_NOW_CNTL`, `OTGx_OTG_TRIG_MANUAL_CONTROL`, and `OTGx_OTG_MANUAL_FLOW_CONTROL` define external/manual trigger, count-forcing, and flow-control bit positions.
- `OTGx_OTG_STATUS*`, `OTGx_OTG_COUNT_*`, `OTGx_OTG_PIXEL_DATA_READBACK*`, `OTGx_OTG_INTERLACE_*`, and `OTGx_OTG_STEREO_*` provide volatile readback fields for scanout state, counters, frame count, pixel sample data, interlace field state, stereo eye selection, and 3D structure status.
- `OTGx_OTG_VERTICAL_INTERRUPT*`, `OTGx_OTG_INTERRUPT_CONTROL`, `OTGx_OTG_V_TOTAL_INT_STATUS`, `OTGx_OTG_VSYNC_NOM_INT_STATUS`, and `OTGx_OTG_GLOBAL_SYNC_STATUS` define interrupt enable/status/clear/type fields for vstartup, vupdate, vready, vertical interrupts, nominal vsync, triggers, snapshots, force-count-now, and GSL-vsync-gap events.
- `OTGx_OTG_CRC_*` macros define CRC enable/mode/source/window fields and the readback data for CRC0 through CRC3. These fields are used for display validation and diagnostics rather than normal scanout programming.
- `OTGx_OTG_UPDATE_LOCK`, `OTGx_OTG_DOUBLE_BUFFER_CONTROL`, `OTGx_OTG_MASTER_UPDATE_LOCK`, `OTGx_OTG_VUPDATE_KEEPOUT`, and `OTGx_OTG_GLOBAL_CONTROL*` define double-buffer update locks, pending flags, global update lock selection, master update lock dead-band/keepout windows, DIG update positions, and field/eye update selection.
- `OTGx_OTG_CLOCK_CONTROL`, `OTGx_OTG_MASTER_EN`, `OTGx_OTG_CONTROL`, and `OTGx_OTG_PIPE_UPDATE_STATUS` expose OTG enable/gating/reset/busy state and pending flip, DC register, cursor, and vupdate-keepout state.

Here `x` is `0`, `1`, or `2`. The three OTG instances generally carry the same field layout, so instance-prefix correctness is part of the API contract.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when Display Core code combines these macros with generated register offsets and register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`.

Typical runtime flow:

1. Resource construction or an OPTC instance table selects an `OTG0`, `OTG1`, or `OTG2` register offset for the active pipe.
2. Shared OPTC code uses this header's field shifts and masks to program timing, enable the timing generator, lock double-buffered updates, configure vstartup/vupdate/vready windows, or decode status.
3. IRQ service code uses global-sync, vertical interrupt, vtotal, and vsync status masks to enable, clear, and classify display timing interrupts.
4. Debug, validation, or state-dump code reads CRC, counter, pipe-update, DRR, stereo/interlace, pixel-readback, and snapshot fields to report hardware state.

The state described by these macros is hardware register state, not persistent driver-owned memory:

- Persistent configuration includes programmed timing totals and blank/sync intervals, sync polarity, DRR min/max/mid and trigger parameters, global update lock settings, GSL windows, vupdate keepout windows, stereo/interlace mode, static-screen detection, CRC windows, interrupt masks/types, and clock/master-enable controls.
- Volatile readback includes current blank/active/sync/update state, counters, frame count, vupdate/vready/vstartup event status, update pending flags, lock status, clock-on/busy state, CRC result data, pixel readback, interlace/stereo current state, snapshot position/frame, and DRR last-used vtotal.
- Side-effecting fields include clear/ack bits for vtotal events, vertical interrupts, nominal vsync, global sync events, trigger occurrence, force-count-now, GSL-vsync-gap, snapshot clear/manual trigger, update lock toggles, count reset, manual trigger/flow-control controls, and soft reset bits.

## Dependencies And Integration Points

This chunk depends on generated-name consistency across the DCN 3.1.6 register header family. It is normally consumed together with the matching `dcn_3_1_6_offset.h` register address definitions and Display Core's register helper layer.

Important integration points include:

- OPTC timing-generator code under `drivers/gpu/drm/amd/display/dc/optc/`, especially DCN 3.x register tables such as `dcn31_optc.h`, `dcn314_optc.h`, and related implementation files. These tables use `SF(...)` and `SRI(...)` style macros to map `OTG0_*` mask/shift constants into per-instance `optc` register structures.
- IRQ service code under `drivers/gpu/drm/amd/display/dc/irq/`, where `OTG_GLOBAL_SYNC_STATUS`, `VSTARTUP_*`, `VUPDATE_*`, and `VUPDATE_NO_LOCK_*` fields are used to enable and clear timing interrupts.
- Resource code that instantiates timing generators and binds OTG register offsets/masks to display pipes. Instance alignment matters because this chunk exposes separate `OTG0`, `OTG1`, and `OTG2` names for equivalent hardware layouts.
- Display mode programming paths that set totals, blanking, sync, DSC/ODM formatting, DRR/vtotal behavior, vstartup/vupdate/vready timing, global update locks, and master enable state during modeset, fast update, and variable-refresh transitions.
- Diagnostic and validation paths that read OTG CRCs, counters, snapshots, pipe-update status, pixel readback, static-screen state, and interlace/stereo status. State capture code in DCN 3.1 reads registers such as `OTG_DRR_CONTROL`, `OTG_GLOBAL_SYNC_STATUS`, and `OTG_PIPE_UPDATE_STATUS`.
- DisplayPort/DSC and ODM paths, where the tail `ODM3_OPTC_*` fields describe segment source selection, data format, DSC byte rate, slice width, clocking, and memory selection feeding an output timing path.

Because this file only defines macros, missing symbols usually fail at compile time. Incorrect numeric masks or shifts can compile cleanly and only appear as runtime MMIO misprogramming.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.6 register specification is the primary risk. A wrong mask or shift can corrupt timing generator programming, interrupt handling, double-buffer updates, DRR behavior, CRC readout, or clock/reset control.
- The three OTG blocks are repetitive. Copy-generation mistakes can produce macros that are valid C symbols but point an `OTG1` or `OTG2` field at the wrong bit layout.
- Several fields are write-one-to-clear, trigger, ack, lock, or reset controls. Incorrect masks can clear latched diagnostics, retrigger manual actions, leave update locks asserted, or reset a timing generator unexpectedly.
- Timing fields are hardware-contract values. Incorrect horizontal/vertical totals, blanking, sync, vstartup, vupdate, or vready fields can cause modeset failures, flicker, missed flips, frame timing drift, or black screens.
- DRR and variable-refresh fields are sensitive to frame timing. Errors in vtotal min/max/mid, trigger windows, reach ranges, and change limits may only reproduce with FreeSync/VRR, low-refresh panels, or under compositor frame pacing.
- Global update lock, GSL, and vupdate keepout fields coordinate multiple pipes. Mistakes can cause unsynchronized pipe updates, stuck pending bits, or missed global-lock events in multi-display or ODM/MPO scenarios.
- CRC and pixel-readback fields are often used as test signals. Bad masks may hide real display corruption or produce false validation failures.
- The chunk starts inside the `ODM3_OPTC_DATA_SOURCE_SELECT` family and ends before the `OTG2_OTG_SPARE_REGISTER` fields, so final file-level reconciliation must merge neighboring chunks to describe those families completely.

## Test Signals

Useful validation combines generated-header checks, build coverage, and display hardware behavior:

- Build AMDGPU Display Core with DCN 3.1.6 support enabled and ensure all `OTG0`, `OTG1`, `OTG2`, and `ODM3_OPTC` field names referenced by OPTC, IRQ, resource, and diagnostic code resolve.
- Run generated-register consistency checks that every in-scope field has both `_SHIFT` and `_MASK`, masks fit in 32 bits, packed fields do not overlap unexpectedly, and repeated `OTG0`/`OTG1`/`OTG2` layouts match where the hardware spec says they should.
- Compare this range against the authoritative DCN 3.1.6 register specification, focusing on timing totals, interrupt clear bits, double-buffer pending flags, global update lock fields, DRR fields, and side-effecting trigger/reset bits.
- Exercise modesets on pipes backed by OTG0, OTG1, and OTG2, including common progressive modes, interlaced modes if supported, DSC modes, ODM/segment-width configurations, and stereo/3D paths if available.
- Test VRR/DRR paths by changing vtotal min/max/mid, trigger windows, reach-range interrupts, and average-frame settings while watching for missed flips, unstable refresh, or incorrect `OTG_V_TOTAL_LAST_USED_BY_DRR` readback.
- Validate vstartup, vupdate, vready, vtotal, vertical interrupt, nominal vsync, and no-lock interrupt handling through IRQ enable/clear/status paths.
- Verify update-lock and global-lock behavior with atomic commits, cursor updates, page flips, multi-plane updates, and multi-display synchronized updates; monitor `OTG_PIPE_UPDATE_STATUS` and double-buffer pending bits.
- Use CRC capture tests with both CRC windows and multiple source/data-format modes, confirming CRC0-CRC3 data readbacks and one-shot/continuous pending semantics.
- Run suspend/resume, runtime power, and display hotplug/modeset cycles to confirm clock gate, clock-on, busy, master-enable, memory-selection, and update-lock state recovers.
- Capture state dumps before and after modeset/flip/VRR events and confirm counters, snapshots, static-screen status, stereo/interlace state, global sync status, and pipe update pending fields decode correctly.

## Chunk-Specific Summary

Lines 30060-32529 define DCN 3.1.6 bit shifts and masks for the end of the `ODM3_OPTC` data-format/clock/memory block and most of the `OTG0`, `OTG1`, and `OTG2` output timing generator blocks. The content is generated register ABI, not executable logic. Correctness depends on exact mask/shift values, instance-correct macro use, careful treatment of side-effecting clear/trigger/reset bits, and hardware validation across modeset, IRQ, DRR/VRR, update-lock, CRC, multi-pipe sync, and suspend/resume paths.

### subset-b-001910: lines 32530-34962

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 32530-34962

## Scope

This chunk is generated AMD DCN 3.1.6 register field metadata. It contains C preprocessor constants only: paired `__SHIFT` and `_MASK` macros for fields in display timing, OPTC, DC perfmon, HPD, DisplayPort, and DIG/HDMI registers, plus generated register/address-block comments. There are no functions, structs, enums, branches, loops, allocations, includes, or software-owned data structures in this range.

The reviewed span contains 2,433 lines, with 1,093 shift definitions and 1,080 mask definitions. The count mismatch is caused by chunk boundaries: the range begins with the final `OTG2_OTG_SPARE_REGISTER` shift/mask pair from the previous OTG instance, then covers complete OTG3/OPTC/HPD/DP0 blocks, and ends inside `DIG0_HDMI_GENERIC_PACKET_CONTROL5` before the corresponding mask definitions for that register. Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU Display Core hardware metadata rather than distributed filesystem code.

## Purpose And Hardware Surface

The purpose of this header slice is to define bit positions and masks for DCN 3.1.6 display engine registers. The companion `dcn_3_1_6_offset.h` header supplies register addresses and base indices; this `*_sh_mask.h` header supplies the field layouts used by AMDGPU Display Core and DMUB register helpers to pack writes and decode readbacks.

The hardware surface covered in this chunk includes:

- The tail of `OTG2_OTG_SPARE_REGISTER`, then the full `dce_dc_optc_otg3_dispdec` block for timing generator instance 3.
- OPTC miscellaneous controls in `dce_dc_optc_optc_misc_dispdec`, including DWB/GSL source selection, OPTC clock controls, ODM memory power controls/status, and a spare register.
- DC perfmon counter 17 control, state, compare, high, and low value registers.
- Hot-plug-detect blocks `HPD0` through `HPD4`, each with interrupt status/control, HPD control, fast training, and toggle filter timing fields.
- The `DP0` DisplayPort encoder block, including link control, pixel format, MSA, stream control, DPHY/training/CRC, secondary data packets, MST/MSE allocation, DSC, panel replay/ALPM-like controls, GSP controls, and double-buffer status.
- The beginning of the `DIG0` digital encoder block, covering front-end control, output CRC/test-pattern/random-pattern/FIFO status, HDMI metadata/control/status/audio/ACR/VBI/infoframe controls, generic packet enable controls, generic packet 8-14 controls, and the start of immediate generic packet send control.

## Important Definitions

The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives a field's low-bit position.
- `<REGISTER>__<FIELD>_MASK` gives the corresponding register mask.
- `//<REGISTER>` comments group fields by generated register name.
- `// addressBlock: ...` comments mark the hardware aperture from which the following register names were generated.

Important OTG3 definitions include:

- Timing programming fields such as `OTG3_OTG_H_TOTAL`, horizontal/vertical blanking, sync start/end/polarity, vertical total min/max/mid, and dynamic refresh rate controls.
- Trigger, flow, and synchronization fields in `OTG3_OTG_TRIGA_CNTL`, `OTG3_OTG_TRIGB_CNTL`, `OTG3_OTG_FORCE_COUNT_NOW_CNTL`, `OTG3_OTG_GSL_*`, `OTG3_OTG_GLOBAL_CONTROL*`, and `OTG3_OTG_TRIG_MANUAL_CONTROL`.
- Run-state and update controls such as `OTG3_OTG_CONTROL`, `OTG3_OTG_MASTER_EN`, `OTG3_OTG_UPDATE_LOCK`, `OTG3_OTG_DOUBLE_BUFFER_CONTROL`, `OTG3_OTG_MASTER_UPDATE_MODE`, `OTG3_OTG_MASTER_UPDATE_LOCK`, and `OTG3_OTG_PIPE_UPDATE_STATUS`.
- Readback/status fields for scan position, frame counts, interlace/stereo state, snapshots, global sync, CRC data, and static screen detection.
- Display timing helper fields for vertical interrupt positions, VSTARTUP/VUPDATE/VREADY, vupdate keepout, DSC start position, constant DTO phase/modulo, and DRR event/status windows.

Important OPTC/perfmon/HPD definitions include:

- `DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`, `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS`, which support display writeback routing, global sync routing, clock gating, and ODM memory power management.
- `DC_PERFMON17_*` fields for selecting counters, clearing/starting/freezing the perfmon, defining comparison values, and reading high/low counter state.
- `HPD<n>_DC_HPD_INT_STATUS`, `HPD<n>_DC_HPD_INT_CONTROL`, `HPD<n>_DC_HPD_CONTROL`, `HPD<n>_DC_HPD_FAST_TRAIN_CNTL`, and `HPD<n>_DC_HPD_TOGGLE_FILT_CNTL` for connector detect state, RX interrupt state, delayed sense, interrupt acknowledge/mask/polarity, connection/disconnection filter windows, and fast-training signaling for HPD instances 0-4.

Important DP0 and DIG0 definitions include:

- DisplayPort stream/link fields in `DP0_DP_LINK_CNTL`, `DP0_DP_PIXEL_FORMAT`, `DP0_DP_CONFIG`, `DP0_DP_VID_STREAM_CNTL`, `DP0_DP_VID_TIMING`, `DP0_DP_VID_N`, `DP0_DP_VID_M`, and `DP0_DP_LINK_FRAMING_CNTL`.
- DPHY and training controls such as `DP0_DP_DPHY_CNTL`, `DP0_DP_DPHY_TRAINING_PATTERN_SEL`, symbol/error/scrambler controls, PRBS, CRC enable/control/result, MST CRC status, fast training, HBR2 eye pattern, and bit-swap controls.
- Secondary packet/audio/MST controls in `DP0_DP_SEC_CNTL*`, `DP0_DP_SEC_FRAMING*`, `DP0_DP_SEC_AUD_*`, `DP0_DP_SEC_TIMESTAMP`, `DP0_DP_SEC_PACKET_CNTL`, `DP0_DP_MSE_*`, `DP0_DP_MSA_*`, `DP0_DP_MSO_CNTL*`, `DP0_DP_DSC_*`, `DP0_DP_SEC_METADATA_TRANSMISSION`, `DP0_DP_ALPM_CNTL`, and `DP0_DP_GSP*`.
- DIG/HDMI fields for source selection, output CRC, clock/test/random patterns, FIFO status, HDMI packet generation, deep color/scrambling/keepout, audio packets, ACR source/priority, VBI packet sending, audio/MPEG infoframe controls, generic packet continuous/send/update-lock bits, and immediate generic packet send/pending bits.

## Control Flow

This header has no executable control flow. Runtime sequencing is supplied by AMDGPU Display Core code that includes `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h`, builds register/field tables with token-pasting macros, and then uses register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `FD_MASK`, and `FD_SHIFT`.

A typical use path is:

1. DCN316 resource construction or DMUB setup selects a hardware block instance, for example OTG3, HPD2, DP0, or DIG0.
2. The offset header provides the MMIO register address/base index.
3. This header provides the bit shift and mask for the target field.
4. A register helper reads, updates, or writes the packed field while preserving unrelated bits.
5. Display hardware latches the programmed value, reports status, or clears an interrupt according to the register's hardware semantics.

The macros do not encode operation ordering. Callers remain responsible for sequencing around blanking windows, update locks, stream enable/disable, link training, HPD interrupt acknowledgement, DRR/vtotal changes, DSC enablement, audio/infoframe packet updates, and write-one-to-clear status bits.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes stateful MMIO fields inside the GPU display block.

Configuration-like hardware state includes programmed timing totals, sync/blanking windows, trigger routing, flow control, master enable, interlace/stereo control, global sync lock/update behavior, ODM memory power settings, DP stream/link/DPHY/secondary-packet configuration, DSC and MST allocation settings, DIG source selection, HDMI packet controls, and generic packet send modes. Status/readback state includes current scan position, frame counts, CRC outputs, static-screen detection, global sync status, pipe update pending bits, perfmon counter values, HPD sense/RX interrupt status, DPHY CRC/training status, MST slot status, FIFO status, HDMI status, and generic packet pending bits.

The persistence boundary is hardware lifetime: values remain in registers until changed by the driver, reset by hardware, lost during GPU reset/power gating, or overwritten by firmware or another display path. The header itself does not retain runtime state.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.1.6 register-address header, especially `dcn_3_1_6_offset.h`, because masks/shifts are useful only when paired with the matching register offsets. The exact header is included by DCN316 Display Core resource code and DMUB support: `display/dc/resource/dcn316/dcn316_resource.c` and `display/dmub/src/dmub_dcn316.c` include both the offset and shift/mask headers.

Integration points include:

- `dmub_dcn316.c`, which builds `dmub_srv_dcn316_regs` using `FD_MASK` and `FD_SHIFT` over DCN31 field lists.
- DCN316 resource construction, which uses the generated constants through block-specific register tables for timing generators, hub/display pipes, stream encoders, HPD handlers, and related Display Core objects.
- DCE/DCN helper headers such as stream encoder register-field lists, where fields like `DIG0_HDMI_GENERIC_PACKET_CONTROL0`, `DP0_DP_PIXEL_FORMAT`, `DP0_DP_SEC_CNTL`, and `DIG0_HDMI_CONTROL` are consumed through common mask/shift table macros.
- Interrupt service and HPD paths, which depend on the HPD status/control masks matching hardware so sense, RX IRQ, ack, mask, and polarity fields are interpreted correctly.
- Link encoder, stream encoder, timing generator, DSC, MST, audio/infoframe, CRC, and diagnostics paths that use these macros for MMIO programming and readback.

## Risks And Review Notes

- Because this is generated hardware metadata, an incorrect bit position or mask compiles cleanly but can silently program the wrong field. The likely symptoms are display timing failures, HPD interrupt storms or missed detects, DP link-training failures, bad MST/DSC/secondary packet behavior, invalid HDMI audio/infoframes, or broken CRC diagnostics.
- The chunk boundary is not register-aligned. Consumers of this research should not infer that `OTG2_OTG_SPARE_REGISTER` or `DIG0_HDMI_GENERIC_PACKET_CONTROL5` are incomplete in the source file; they are incomplete only in this work-item slice.
- Repeated HPD blocks and repeated DP/DIG packet fields are vulnerable to copy/generation drift. A single instance mismatch can affect only one connector or stream encoder, making failures appear board- or port-specific.
- Some status fields are not ordinary read/write state. Interrupt status/ack/clear fields, pending bits, CRC readbacks, training status, and dynamic refresh timing event bits have side effects or timing constraints defined by hardware and driver code, not by these macros.
- DCN316 uses common DCN31-era helper lists where field availability must match the generated header. Removing or renaming a macro here can break table initialization at compile time; changing a value can pass compile and fail only on hardware.

## Test Signals

Useful validation signals are mostly integration and hardware-display tests rather than unit tests for this header:

- Build coverage for AMDGPU Display Core and DMUB DCN316 paths, especially translation units that include `dcn_3_1_6_sh_mask.h` and instantiate field tables with `FD_MASK`/`FD_SHIFT`.
- Multi-connector hotplug tests across HPD0-HPD4, checking plug/unplug detection, delayed sense, RX IRQ handling, interrupt masking/acknowledgement, and debounce/filter behavior.
- DP link bring-up and retraining on DP0, including different pixel encodings/depths, HBR rates, training patterns, DPHY CRC checks, scrambling, fast training, MST slot allocation, DSC enablement, and secondary data packet transmission.
- OTG3 display-mode tests covering timing programming, vertical interrupts, update locks, DRR/vtotal changes, stereo/interlace modes if supported, CRC capture, and scan-position/frame-counter readback.
- HDMI/DIG0 tests for source selection, deep color, scrambling, audio packet generation, ACR, VBI packets, infoframes, generic packets, AVMUTE/general-control behavior, and immediate-send pending status.
- Runtime diagnostics such as `dmesg` display-core errors, HPD interrupt logs, DP AUX/link-training failures, CRC mismatch reports, blanking/flicker during mode sets, and audio/infoframe analyzer results.

### subset-b-001911: lines 34963-37371

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 34963-37371

## Scope

This chunk is generated AMDGPU DCN 3.1.6 register shift/mask metadata. It contains C preprocessor constants only: no functions, structs, enums, variables, includes, locks, allocation paths, or executable control flow. The covered range has 2,409 source lines, 2,168 `#define` lines, 235 register/address-block comments, and 233 visible register groups.

The chunk starts inside `DIG0_HDMI_GENERIC_PACKET_CONTROL5`: the first visible lines are the tail of HDMI generic-packet immediate-send shift definitions and the complete mask list for generic packets 0 through 14. It ends inside `DP2_DP_SEC_CNTL7`, after the `DP_SEC_GSP1_SEND_ACTIVE` mask and before the remaining `DP_SEC_CNTL7` masks. Adjacent chunks are needed before making whole-register or whole-file claims.

Although this file lives under a local `ceph-client` mirror, the content is AMD display-controller hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this range is to expose bit positions and masks for DCN 3.1.6 display output blocks. Consumers combine these constants with matching register offsets from `dcn_3_1_6_offset.h` and AMD display register helpers to program memory-mapped display registers.

The macro convention is:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or updating that field.
- `// addressBlock: ...` comments: generated grouping metadata for the following replicated register block.

The covered hardware areas are:

- Tail of `DIG0` HDMI generic-packet control and the rest of `DIG0` HDMI/TMDS/backend control.
- Full `DP1` DisplayPort link, video, PHY, secondary-data, audio, MSE/MSO, DSC, and GSP metadata controls.
- Full `DIG1` frontend, HDMI, TMDS, backend, CRC/test-pattern, FIFO/status, and force-disable controls.
- Start through middle of `DP2` DisplayPort controls, ending in secondary-packet active/idle status for GSP streams.

## Important Definitions

There are no callable APIs in this chunk. The public surface is the generated macro namespace.

Important `DIG0` and `DIG1` groups:

- `DIG*_HDMI_GENERIC_PACKET_CONTROL*`: enable, line-number, immediate-send, pending, double-buffer-pending, and generic packet scheduling fields for HDMI generic packets 0 through 14. The `DIG0` section starts at the tail of control register 5; the `DIG1` section includes metadata packet control, generic-packet control 0/1/2/3/4/5/6/7/8/9/10, and double-buffer control.
- `DIG*_HDMI_GC`: HDMI general-control packet fields including AVMUTE, continuous AVMUTE, default phase, packing phase, and packing override.
- `DIG*_HDMI_ACR_*` and `DIG*_HDMI_ACR_STATUS_*`: audio clock regeneration CTS/N fields for 32 kHz, 44.1 kHz, 48 kHz, plus status readback values.
- `DIG*_AFMT_CNTL`: audio formatting clock enable/status fields.
- `DIG*_DIG_BE_CNTL` and `DIG*_DIG_BE_EN_CNTL`: digital backend enable, symbol clock status, dual-link, swap, red/blue switch, frontend source select, mode, and HPD select fields.
- `DIG*_TMDS_*`: TMDS sync phase, control-character output enables, feedback, stereo-sync selection, sync-character patterns, control bits, DC balancer control, DC-balance character, and generated control-character fields.
- `DIG*_DIG_FE_CNTL`, `DIG*_DIG_OUTPUT_CRC_*`, `DIG*_DIG_CLOCK_PATTERN`, `DIG*_DIG_TEST_PATTERN`, `DIG*_DIG_RANDOM_PATTERN_SEED`, and `DIG*_DIG_FIFO_STATUS`: frontend enable/source/test/debug path, output CRC, clock/test/random pattern generation, and FIFO status for the `DIG1` frontend side.
- `DIG*_DIG_VERSION` and `DIG*_FORCE_DIG_DISABLE`: block version and force-disable bits.

Important `DP1` and `DP2` groups:

- `DP*_DP_LINK_CNTL`, `DP*_DP_PIXEL_FORMAT`, `DP*_DP_MSA_COLORIMETRY`, `DP*_DP_CONFIG`, and `DP*_DP_VID_STREAM_CNTL`: core DisplayPort link enable/configuration, pixel encoding, main-stream attributes, enhanced framing, training/start/stop controls, video stream enable, and stream status fields.
- `DP*_DP_MSA_MISC` and `DP*_DP_MSA_TIMING_PARAM1` through `PARAM4`: packed MSA color/depth/misc and timing fields for horizontal/vertical total, start, sync width, polarity, and active width/height.
- `DP*_DP_VID_N`, `DP*_DP_VID_M`, `DP*_DP_VID_MSA_VBID`, and `DP*_DP_VID_INTERRUPT_CNTL`: video timing generator M/N values, VBID/MSA fields, and interrupt control/status around stream timing.
- `DP*_DP_DPHY_*`: DisplayPort PHY control, training pattern selection, per-symbol training controls, 8b/10b control, PRBS, scrambling, CRC enable/control/result, MST CRC status, fast-training control/status, byte/serializer swap, and HBR2 pattern controls.
- `DP*_DP_SEC_*`: secondary-data packet control, framing, audio N/M and readback, timestamps, packet control, generic secondary packet send/pending/deadline/any-line controls, line-number controls, double-buffer disable/status, active/idle status, and GSP metadata controls.
- `DP*_DP_MSE_*`: multi-stream transport scheduling fields, including rate control/update, SAT slots/status, link timing, and miscellaneous control.
- `DP*_DP_MSO_CNTL`, `DP*_DP_MSO_CNTL1`, and `DP*_DP_DSC_CNTL`: multi-stream operation enable masks for secondary packets and Display Stream Compression mode/slice-width fields.
- `DP*_DP_DSC_BYTES_PER_PIXEL`, `DP*_DP_ALPM_CNTL`, and `DP*_DP_GSP8_CNTL` through `GSP11_CNTL`: later DP metadata controls present in `DP1`; the `DP2` range has not reached all of these by the chunk end.

## Control Flow

This header has no runtime branches or calls. Runtime sequencing is provided by AMDGPU display code:

1. DCN316 resource and DMUB code include `dcn_3_1_6_offset.h` and this `dcn_3_1_6_sh_mask.h` file.
2. `dcn316_resource.c` defines DCN base segments, then expands register-list and field-list macros for display output resources.
3. `dmub_dcn316.c` expands DMUB register and field lists into `dmub_srv_dcn316_regs`, using `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` to copy generated constants into firmware-facing register tables.
4. Runtime stream-encoder, link-encoder, audio, HDMI, and DisplayPort code uses register helper paths such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WRITE`, `REG_READ`, and polling helpers to program fields described by this chunk.

The macros only encode bit layout. They do not encode ordering requirements for link training, HDMI packet programming, double-buffer commits, audio clock regeneration, stream enable/disable, MST scheduling, DSC setup, interrupt clearing, or status polling.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk. It describes MMIO-backed GPU display state:

- HDMI generic-packet and metadata state: packet enables, packet line targets, immediate-send requests, pending status, double-buffer pending state, AVMUTE/general-control behavior, metadata packet control, infoframe controls, VBI/audio/ACR packet control, and HDMI status.
- HDMI audio state: ACR N/CTS values for common sample-rate families, readback/status values, AFMT audio clock enable/on state, and audio packet controls.
- TMDS and digital backend state: sync/control-character generation, DC balancing, dual-link/backend enable, frontend source selection, output mode, HPD selection, symbol clock status, FIFO status, test patterns, output CRC, and force-disable state.
- DisplayPort link and video state: link control, pixel format, stream enable/status, M/N timing, MSA/VBID fields, enhanced framing, training patterns, DPHY symbols, scrambling, PRBS, CRC, and fast-training state.
- DisplayPort secondary-data state: audio packets, timestamps, secondary-packet framing, GSP sends, packet pending/deadline status, per-packet line numbers, double-buffer disable/status, active/idle status, and metadata packet controls.
- MST/MSO/DSC state: MSE rate/SAT/link timing, MSO secondary stream packet enables, DSC mode/slice width, and bytes-per-pixel fields.

Persistence is hardware-defined. Configuration fields usually remain until modeset reprogramming, link retraining, stream disable, power gating, suspend/resume restore, or ASIC reset. Status, pending, deadline-missed, taken, clear, active, idle, CRC, interrupt, and readback fields may be read-only, sticky, self-clearing, or write-one-to-clear depending on the hardware register. This generated header does not express access type or side effects.

## Dependencies And Integration Points

This chunk depends on the AMD-generated DCN 3.1.6 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`, which supplies matching MMIO offsets and base-index macros.
- DCN316 base segment definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`.
- DCN316 DMUB register table construction in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`.
- Common AMD display register helper macros that derive fields through generated names, including `FD_MASK`, `FD_SHIFT`, and `REG_*` helper families.

Important consumer areas:

- DCN316 resource construction uses this namespace while creating stream encoder, audio, DIO, and related display output resources.
- HDMI stream-encoder paths consume `DIG*_HDMI_*`, `DIG*_AFMT_*`, and `DIG*_TMDS_*` fields for infoframes, generic packets, audio setup, AVMUTE, TMDS formatting, and backend enable/disable.
- DisplayPort stream/link paths consume `DP*_DP_LINK_*`, `DP*_DP_DPHY_*`, `DP*_DP_MSA_*`, `DP*_DP_VID_*`, and `DP*_DP_CONFIG` fields for link training, stream timing, colorimetry, video enable, scrambling, PRBS, and CRC.
- MST/MSO/DSC code consumes `DP*_DP_MSE_*`, `DP*_DP_MSO_*`, `DP*_DP_SEC_*`, and `DP*_DP_DSC_*` fields for multi-stream scheduling, secondary-data packet transmission, DSC PPS/metadata, and line-targeted packet sends.
- DMUB firmware-facing support uses selected generated masks/shifts in `dmub_srv_dcn316_regs`, so field names shared with `DMUB_DCN31_FIELDS()` must remain stable.

## Risks And Edge Cases

- Field drift is the central risk. These are untyped constants; a wrong shift or mask can compile cleanly while programming the wrong MMIO bits.
- Chunk boundaries are not semantic. `DIG0_HDMI_GENERIC_PACKET_CONTROL5` is incomplete at the start, and `DP2_DP_SEC_CNTL7` is incomplete at the end. Adjacent chunks must be merged for complete register-pair validation.
- Repeated output instances are copy-sensitive. `DIG0`/`DIG1` and `DP1`/`DP2` blocks are similar but not interchangeable; instance-prefixed fields must match the selected encoder/link instance.
- HDMI packet controls include pending and double-buffered state. Misprogramming immediate-send, line-number, pending, or DB fields can drop infoframes/metadata, send stale packets, or leave packet state stuck.
- HDMI ACR and audio fields affect sink audio lock. Incorrect N/CTS masks or packet controls can produce silent audio, clock drift, or sample-rate-specific failures.
- TMDS/backend controls are mode-sensitive. Wrong control-character, packing, DC-balance, frontend source, backend enable, mode, or HPD fields can cause blank output, link errors, or bad HDMI/DVI behavior.
- DisplayPort DPHY and training fields are link-critical. Incorrect training-pattern, symbol, scrambling, PRBS, CRC, fast-training, or HBR2 pattern masks can cause training failure or intermittent high-rate link instability.
- MSA/VBID/timing fields are packed and sink-visible. Bad masks can produce incorrect active size, sync polarity, colorimetry, dynamic range, stream attributes, or VBID state.
- Secondary-packet and GSP send fields are timing-sensitive. Wrong send, pending, deadline, any-line, line-number, active/idle, or DB-disable fields can lose HDR/static metadata, DSC PPS, audio timestamps, or other sideband packets.
- MST/MSO and DSC fields are tightly coupled to stream allocation and compression setup. Bad masks can corrupt slot allocation, secondary stream enables, DSC mode, slice width, or bytes-per-pixel programming.
- Status/clear/interrupt fields may have side effects that are not represented here. Driver code must rely on hardware documentation and existing helpers for write-one-to-clear, readback, and polling semantics.

## Test Signals

Useful validation is mostly compile-time, generated-header consistency, and hardware integration:

- Build AMDGPU/DC with DCN316 enabled. Undefined or renamed field macros should fail in `dcn316_resource.c`, `dmub_dcn316.c`, and shared HDMI/DP/DIO/stream-encoder users.
- Mechanically verify that each visible `__SHIFT` field in this range has the expected companion `_MASK` field where the generated schema defines one, while allowing the known leading and trailing boundary exceptions.
- Compare this slice against AMD's authoritative DCN 3.1.6 register database and adjacent DCN 3.1.x headers where block layouts are expected to match.
- Exercise HDMI modes that use generic packets, infoframes, metadata packets, AVMUTE, ACR audio, TMDS control-character generation, DVI/HDMI mode switching, and audio sample rates 32 kHz, 44.1 kHz, and 48 kHz.
- Exercise DisplayPort SST and MST links across link rates and lane counts, including training/retraining, scrambling, PRBS/CRC diagnostics, MSA timing/colorimetry, VBID, hotplug, suspend/resume, and stream enable/disable.
- Validate DSC and metadata paths with HDR/static metadata, DSC PPS packets, GSP packets, MSO/MST secondary packet enables, and line-targeted sends. Watch for deadline-missed, stuck-pending, active/idle, or double-buffer status anomalies.
- Run DRM page-flip and modeset tests across outputs backed by `DIG0`/`DIG1` and `DP1`/`DP2`, checking for blank screens, link training failures, metadata loss, audio dropouts, CRC/test-pattern mismatches, and resume-only regressions.

## Cross-Chunk Notes

- Prefix distribution in this range: 34 visible `DIG0` register groups, 52 `DIG1` groups, 78 `DP1` groups, 68 `DP2` groups, and three address-block comments.
- `DIG0` starts mid-HDMI generic-packet control; earlier `DIG0` HDMI metadata/control/status fields are in the previous chunk.
- `DP2` continues after this chunk with the rest of `DP2_DP_SEC_CNTL7` and later DP2 DB/MSA metadata/GSP status fields.
- The final per-file research document should be produced later by the reconciliation lane after all chunks for `dcn_3_1_6_sh_mask.h` are available.

### subset-b-001912: lines 37372-39766

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 37372-39766

## Purpose

This chunk is part of AMDGPU's generated DCN 3.1.6 register field mask header. It defines preprocessor constants for hardware register bit positions and masks; it does not contain executable C logic. The constants pair with `dcn_3_1_6_offset.h` address definitions so display code can construct register tables and access fields through AMDGPU register helpers such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_UPDATE`, and related macros.

The assigned range contains 2,171 `#define` entries: 1,080 `__SHIFT` values and 1,099 `_MASK` values. The range starts inside the tail of `DP2_DP_SEC_CNTL7`, where only remaining GSP active/idle masks are visible, and ends inside `DP4_DP_DPHY_SYM2`, after the symbol shift fields but before the matching masks appear in the next chunk.

## Covered Hardware Blocks

- `DP2` tail registers: secondary packet status/control for GSP1-GSP7, DP double-buffer controls, MSA/VBID override fields, secondary metadata transmission, DSC bytes-per-pixel, ALPM PHY sleep/standby, GSP8-GSP11 packet controls, and GSP enable double-buffer status.
- `DIG2` display encoder block: front-end control, output CRC, clock/test/random patterns, FIFO status, HDMI metadata/audio/ACR/VBI/infoframe/generic packet controls, HDMI double-buffer status, HDMI audio clock regeneration values and status, AFMT selection, backend enable/control, TMDS controls, generated control bits, version, and force-disable.
- `DP3` DisplayPort stream encoder block: link status, pixel format, lane config, stream enable/disable interrupts, steer/TU FIFO status, video M/N timing, link framing, DPHY training/pattern/CRC/FEC/scrambler fields, DP secondary data/audio packet controls, MST/MSE slot allocation tables and status, MSA timing parameters, MSO controls, DSC control, metadata transmission, ALPM, GSP8-GSP11 controls, and GSP enable double-buffer status.
- `DIG3` display encoder block: the same broad DIG/HDMI/TMDS register surface as `DIG2`, for the next hardware instance.
- `DP4` beginning registers: link status, pixel format, lane config, stream control, FIFO overflow/status, MSA misc fields, DPHY internal controls, video M/N timing, link framing, HBR2 eye pattern, MSA/VBID placement, stream-disable interrupt fields, DPHY control/training fields, and the first DPHY symbol fields.

## Important APIs, Types, and Macros

The header exports only macros. Each field is represented by the generated naming scheme:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask already shifted into register value space.

Important local consumers for this DCN 3.1.6 header include:

- `display/dmub/src/dmub_dcn316.c`, which includes `dcn_3_1_6_offset.h` and this file, then fills `dmub_srv_dcn316_regs` using `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)`.
- `display/dc/resource/dcn316/dcn316_resource.c`, which includes this file and uses `SRI`, `SRII`, `SE_DCN3_REG_LIST`, `VPG_DCN31_REG_LIST`, `AFMT_DCN31_REG_LIST`, `APG_DCN31_REG_LIST`, and other list macros to build DCN 3.1.6 resource-register tables.
- Stream encoder definitions in `display/dc/dio/dcn30/dcn30_dio_stream_encoder.h`, where `SE_DCN3_REG_LIST` and `SE_COMMON_MASK_SH_LIST_DCN30` bind DIO stream encoder code to the `DIG*`, `DP*`, HDMI, TMDS, and secondary-packet fields represented here.
- VPG/AFMT definitions in `display/dc/dcn31/dcn31_vpg.h` and `display/dc/dcn31/dcn31_afmt.h`; while this chunk is mostly DIO/DIG/DP rather than VPG/AFMT payload storage, the same generated-mask mechanism is used by the DCN 3.1.6 resource file for adjacent packet-generation and audio-format blocks.

There are no functions, structs, enums, memory allocations, locks, syscalls, or direct error paths in this slice. The "API" surface is the compile-time set of register field identifiers.

## Control Flow and State

Runtime control flow is indirect. During compilation, resource and DMUB code expands these macros into arrays or structures of register offsets, masks, and shifts. At runtime, AMD display code uses those tables to read, modify, poll, or clear hardware register fields.

The state represented by this chunk is hardware state:

- DP stream state includes link-training completion/status, embedded-panel mode, lane count, pixel encoding/depth, stream enable/status, deferred stream disable, vblank/vupdate double-buffer state, MSA/VBID overrides, MSA timing, video M/N generator fields, DSC bytes-per-pixel, MSO selection, MST/MSE slot allocation tables, and secondary packet enable/send state.
- HDMI/DIG state includes encoder source selection, stereosync, display color depth, TMDS encoding, Dolby Vision metadata status, output CRC, test/random patterns, FIFO underflow/overflow/status, HDMI keepout, deep-color enable, generic packet send/continuous/immediate-send state, packet line numbers, ACR source/select values, and HDMI double-buffer pending/taken flags.
- DPHY state includes training pattern selection, HBR2 eye pattern enable, FEC enable/readiness/active status, scrambler selection, bypass/skew-bypass, custom symbol values, PRBS/scrambler control, CRC enable/control/result, fast-training lane/ack state, and bit/symbol swap controls.
- Interrupt and clear/ack state appears in stream-disable interrupts, steer/TU FIFO overflow ack, HDMI audio-enable change ack, secondary packet missed/overflow bits, metadata transmission missed clear bits, and generic-packet deadline status.
- Power-management and low-power timing state appears in ALPM PHY sleep/standby send/pending/immediate controls and line-number fields.

Hardware fields persist in MMIO/register state until changed by the driver, reset by display hardware sequencing, or affected by power-gating/reset. Pending/taken/status fields are synchronized with hardware update points such as vupdate, packet send timing, stream enable/disable sequencing, or link-training events.

## Dependencies and Integration Points

This file must remain exactly aligned with DCN 3.1.6 hardware layout and with the companion `dcn_3_1_6_offset.h` register address header. A correct field name is not sufficient: its bit position and mask must also match the ASIC register definition for the relevant DIO/DIG/DP instance.

The repeated instance prefixes are integration-critical. `DIG2` and `DIG3` represent separate display encoder instances. `DP2`, `DP3`, and `DP4` represent separate DisplayPort stream/link-facing blocks. The resource layer selects concrete instances through offset-list macros, while common object code often uses shared mask/shift structures whose field names are generated from a representative instance.

Downstream integration paths include DC resource-pool construction for DCN 3.1.6, DMUB service register access, DIO stream encoder programming, HDMI audio and packet programming, DP link training, DP MST/MSO/DSC programming, vblank/vupdate double-buffer update paths, hotplug/IRQ handling, and display suspend/resume or power-management sequences.

## Risks and Edge Cases

- A wrong shift or mask can compile cleanly while programming the wrong hardware bits. Likely symptoms include blank displays, failed DP link training, broken HDMI/DP infoframes, missing HDR/metadata packets, bad audio clock regeneration, corrupted TMDS control patterns, MST slot-allocation errors, DSC setup failures, or spurious display interrupts.
- This chunk has split register definitions at both boundaries. `DP2_DP_SEC_CNTL7` began in the prior chunk, and `DP4_DP_DPHY_SYM2` continues in the next chunk. The merge lane should treat these as boundary artifacts rather than complete-register omissions in the whole-file report.
- Status and clear fields are mixed with control fields in the same generated namespace. Fields ending in `ACK`, `CLR`, or clear-like names may have write-one-to-clear hardware semantics; generic read-modify-write paths must avoid accidentally asserting them.
- Pending/taken/deadline fields depend on display timing. Polling code needs bounded waits and must account for disabled streams, missed vblank/vupdate windows, and power-gated or reset blocks.
- Line-number and slot-allocation fields have fixed masks. Out-of-range values may be truncated before write, producing subtle packet timing failures that surface only as deadline-missed or packet-missed status.
- Instance-copy mistakes are easy in generated headers. A stale `DIG2`/`DIG3` or `DP3`/`DP4` field can still look structurally valid but bind a resource table to the wrong hardware instance.

## Test and Validation Signals

- Kernel build coverage for DCN 3.1.6 display and DMUB code should catch missing macro names in `dmub_dcn316.c`, `dcn316_resource.c`, stream encoder headers, and related register-table initialization.
- Compile-time expansion of `FD_MASK`, `FD_SHIFT`, `SRI`, `SRII`, `SE_DCN3_REG_LIST`, `SE_COMMON_MASK_SH_LIST_DCN30`, `VPG_DCN31_REG_LIST`, and `AFMT_DCN31_REG_LIST` is the first validation that this header remains name-compatible with the driver.
- Display smoke tests should include DP and HDMI mode sets, stream enable/disable, vblank/vupdate programming, suspend/resume, hotplug, and link retraining across the affected encoder instances.
- Feature tests should cover DP link training, FEC, MST/MSE slot allocation, MSO, DSC, ALPM transitions, HDMI audio, ACR values, generic packets, infoframes, HDR/metadata packets, output CRC/test pattern paths, and TMDS modes.
- Useful runtime diagnostics are link-training status, stream-disable interrupt/ack state, FIFO overflow bits, DP secondary packet missed/deadline status, GSP enable pending bits, HDMI generic packet pending/deadline fields, ACR status, DPHY CRC results, and ALPM sleep/standby pending bits.

### subset-b-001913: lines 39767-42179

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 39767-42179

## Purpose

This chunk is generated AMD DCN 3.1.6 register field metadata. It contains no executable C logic; it publishes preprocessor constants that describe hardware MMIO bit positions (`__SHIFT`) and bit masks (`_MASK`). AMD display code includes this header with the matching `dcn_3_1_6_offset.h` so per-ASIC register tables can combine register offsets with field encodings and then use common register helpers to read, set, update, or poll individual fields.

The requested range covers the tail of the `DP4_DP_DPHY_SYM2` group, then a large portion of the fourth DisplayPort/DIG stream encoder instance, the DIG4 HDMI/TMDS front-end and back-end registers, AFMT0 through AFMT4 audio formatter fields, DME0/DME1 metadata-engine fields, VPG0 generic secondary-packet fields, and the beginning of VPG1 generic secondary-packet fields. Although this path is under a local `ceph-client` mirror, the file is AMDGPU display hardware metadata and has no Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation paths, locks, includes, or direct register operations in this chunk. Its exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position of a field in a hardware register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or updating that field.
- `// addressBlock: ...` comments: generated grouping metadata for the following register family.

Major register families in this slice:

- `DP4_DP_DPHY_*`: DisplayPort physical/link-layer controls for 8b/10b reset/disparity, PRBS generation, scrambler behavior, CRC enable/control/result, MST CRC slot/status, fast training, byte-swap/scrambler-reset swap, and HBR2 pattern control.
- `DP4_DP_SEC_*`, `DP4_DP_GSP*`, and `DP4_DP_SEC_METADATA_TRANSMISSION`: DP secondary-data packet control for audio, ASP/ATP/AIP/ACM, generic secondary packets GSP0-GSP11, MPEG/ISRC style packet enables, PPS/metadata packet enable and line timing, collision/audio mute status, stream enable, and send/pending/deadline bits.
- `DP4_DP_MSE_*`, `DP4_DP_MSO_*`, `DP4_DP_MSA_*`, and `DP4_DP_MSA_VBID_MISC`: MST stream allocation-table fields, link timing, MSO lane/segment controls, main-stream-attribute timing fields, VBID misc bits, and update/status latches.
- `DP4_DP_DSC_*`, `DP4_DP_ALPM_CNTL`, and `DP4_DP_DB_CNTL`: DSC mode/bytes-per-pixel fields, ALPM enable/force/wake/status controls, and double-buffer control/status.
- `DIG4_DIG_*`, `DIG4_HDMI_*`, and `DIG4_TMDS_*`: DIG4 front-end source, start, pixel/TMDS encoding, stereo sync, FIFO status, CRC/test/random pattern controls, HDMI metadata/audio/ACR/VBI/infoframe/generic packet controls, HDMI deep-color/scrambling/status controls, data-bypass controls, and TMDS control/data-balance/sync-character fields.
- `AFMT0_AFMT_*` through `AFMT4_AFMT_*`: audio formatter packet control, audio source/channel enable, HDMI/DP audio info fields, IEC 60958 channel-status fields, CRC/ramp/status registers, and memory power controls for five AFMT instances.
- `DME0_DME_*` and `DME1_DME_*`: metadata engine requestor ID, engine enable, stream type, double-buffer pending/taken/clear/disable, missed-transmission status/clear, and memory power/default-low-power fields.
- `VPG0_VPG_*` and beginning of `VPG1_VPG_*`: video packet generator generic packet data-index/data-byte fields, frame/immediate update bits and pending bits for generic slots 0-14, conflict status/clear, memory power, ISRC access/data, MPEG info, and the start of VPG1 frame-update controls.

Representative fields that are directly useful to consumers include `DP_SEC_STREAM_ENABLE`, `DP_SEC_GSP*_ENABLE`, `DP_SEC_GSP*_SEND`, `DP_SEC_GSP*_LINE_NUM`, `DP_SEC_GSP11_PPS`, `DP_SEC_METADATA_PACKET_ENABLE`, `DP_MSA_HTOTAL`, `DP_MSA_VTOTAL`, `DP_MSA_HSTART`, `DP_MSA_VSTART`, `DP_MSA_HSYNCWIDTH`, `DP_MSA_VSYNCWIDTH`, `DP_DSC_MODE`, `DP_DSC_BYTES_PER_PIXEL`, `DIG_SOURCE_SELECT`, `DIG_START`, `DIG_FIFO_LEVEL_ERROR`, `HDMI_GENERIC*_SEND`, `HDMI_GENERIC*_CONT`, `HDMI_GENERIC*_LINE`, `HDMI_ACR_*`, `AFMT_AUDIO_SRC_SELECT`, `AFMT_AUDIO_CHANNEL_ENABLE`, `AFMT_60958_CS_UPDATE`, `AFMT_AUDIO_SAMPLE_SEND`, `AFMT_MEM_PWR_*`, `VPG_GENERIC_DATA_INDEX`, `VPG_GENERIC_DATA_BYTE*`, `VPG_GENERIC*_FRAME_UPDATE`, `VPG_GENERIC*_IMMEDIATE_UPDATE`, and `VPG_GENERIC_CONFLICT_*`.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that consumes the generated constants:

1. DCN316 resource setup includes `dcn_3_1_6_offset.h` and this `dcn_3_1_6_sh_mask.h`.
2. `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` expands register-list macros such as `SE_DCN3_REG_LIST(id)`, `VPG_DCN31_REG_LIST(id)`, and `AFMT_DCN31_REG_LIST(id)` into per-instance address tables, using offsets from the offset header.
3. The same file expands shift/mask lists into typed tables: `se_shift`/`se_mask`, `vpg_shift`/`vpg_mask`, and `afmt_shift`/`afmt_mask`. Those values come from macros in this generated header.
4. `dcn316_stream_encoder_create()` maps a stream engine to its stream encoder, VPG, and AFMT instances, then passes the register, shift, and mask tables into `dcn30_dio_stream_encoder_construct()`.
5. Runtime methods in the DIO stream encoder, VPG, and AFMT modules use `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_WRITE`, `REG_GET`, and `REG_WAIT` helpers. Those helpers rely on the field shifts and masks from this chunk to program hardware.

Important runtime sequences represented by these fields include:

- HDMI infoframe updates: the stream encoder writes generic packet payload through the VPG, then sets `HDMI_GENERIC*_CONT`, `HDMI_GENERIC*_SEND`, and `HDMI_GENERIC*_LINE` fields for the selected packet slot.
- DP DSC PPS transmission: the stream encoder enables PPS handling with `DP_SEC_GSP11_PPS`, loads PPS chunks into VPG generic slots, sets `DP_SEC_GSP11_LINE_NUM`, and coordinates VBID/PPS line timing.
- DP and HDMI audio setup: AFMT programs audio source, channel enable, 60958 channel-status fields, audio sample send, and memory power; DP secondary-data fields handle audio packet and timestamp paths.
- VPG generic packet writes: `vpg3_update_generic_info_packet()` waits for `VPG_GENERIC_CONFLICT_OCCURED` to clear, clears conflict status, sets `VPG_GENERIC_DATA_INDEX`, writes packet header/body bytes through `VPG_GENERIC_PACKET_DATA`, and triggers either frame update or immediate update bits for slots 0-14.

The macros themselves do not encode required ordering, access type, locking, or side effects. Consumers must preserve the hardware-specific sequencing around stream enable/disable, packet double-buffering, update locks, symbol clocks, AFMT/VPG memory power, DSC PPS timing, and interrupt/status clears.

## State And Persistence Behavior

This chunk stores no software state and persists nothing in memory or on disk. It describes MMIO-backed GPU display state:

- DP4 link-layer state: PRBS, scrambler, CRC, MST CRC, fast training, HBR2 pattern, MSE/MST allocation, MSO, MSA timing, VBID misc, DSC, ALPM, and double-buffer controls.
- DP4 secondary-packet state: stream enable, packet enable bits, packet send and pending bits, line reference/line number selection, audio N/M values and readbacks, PPS/metadata controls, collision status, and audio mute status.
- DIG4 HDMI/TMDS state: HDMI packet generation, generic packet line/send/continuous controls, ACR CTS/N values, deep color, scrambling, keepout, VBI packets, TMDS symbol/control/data-balance settings, DIG FIFO status, CRC/test pattern state, and DIG enable/disable status.
- AFMT0-4 audio formatter state: audio source routing, active channel mask, audio/infoframe update bits, IEC 60958 channel status, ramp/CRC/status, audio sample transmission, and AFMT memory power force/disable/status fields.
- DME0-1 metadata state: engine enable, stream type, HUBP requestor ID, double-buffer status/clear bits, missed transmission status/clear bits, and metadata-engine memory power policy/status.
- VPG0 and partial VPG1 packet-generator state: generic packet payload index/data windows, frame/immediate update triggers, update-pending bits, conflict status/clear, VPG memory power, ISRC data, and MPEG info fields.

Persistence is hardware-defined. Configuration fields generally remain in the display block until a modeset, stream disable, power-gating transition, suspend/resume, or ASIC reset changes them. Status, pending, readback, conflict, clear, ack, missed, CRC-result, memory-power-state, and training-status fields may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. The generated header provides masks and shifts only; it does not document access semantics.

## Dependencies And Integration Points

This chunk must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`, which supplies the matching register offsets and base-index macros.
- DCN316 base-address definitions and register-table construction in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`.
- Common register-helper macros in AMD display code, especially the `SE_SF`, `SRI`, `REG_*`, `FN`, and per-block shift/mask table patterns.

Direct DCN316 include and construction points found in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` includes this header and builds `stream_enc_regs`, `vpg_regs`, `afmt_regs`, `se_shift`, `se_mask`, `vpg_shift`, `vpg_mask`, `afmt_shift`, and `afmt_mask`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c` includes the same generated DCN316 register headers for DMUB-facing register metadata, though this particular chunk is primarily DIO/VPG/AFMT stream metadata.

Important shared consumers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.h` defines `SE_DCN3_REG_LIST(id)` and `SE_COMMON_MASK_SH_LIST_DCN30(...)`, which reference many fields in this chunk for HDMI packet control, DP secondary packets, MSA timing, DSC, stream enable, AFMT clock, DIG source/start, FIFO status, and metadata packets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.c` uses those tables to update HDMI info packets, stop generic packets, program DP DSC/PPS packets, and control stream packet behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_vpg.c` use the VPG0 masks/shifts from this chunk as the canonical field layout for all VPG instances.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_afmt.h`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_afmt.c`, and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_afmt.c` use the AFMT0 masks/shifts from this chunk as the canonical field layout for AFMT instances.

## Risks And Edge Cases

- Field drift is the main risk. These macros are untyped constants, so an incorrect mask or shift can compile cleanly while programming the wrong hardware bits.
- The chunk boundaries are artificial. The first requested line starts at the tail of `DP4_DP_DPHY_SYM2`, and the last requested line stops inside `VPG1_VPG_GSP_FRAME_UPDATE_CTRL`; adjacent chunks are required for complete file-level claims.
- Instance symmetry is assumed by consumer code. DCN316 uses instance-0 field names in shift/mask tables and applies them to multiple stream/VPG/AFMT instances. If a later instance has a different layout, the shared-table pattern would silently misprogram that instance.
- DP secondary-packet bits are sequencing-sensitive. Wrong GSP enable, send, pending, line number, PPS, or stream-enable fields can cause missing HDR/DSC/audio/metadata packets, PPS line conflicts, or sink compatibility failures.
- VPG generic-packet access is conflict-sensitive. Bad `VPG_GENERIC_CONFLICT_*`, data-index, data-byte, frame-update, or immediate-update masks can corrupt infoframes or race hardware reads of packet memory.
- HDMI generic-packet controls are slot-specific. Incorrect `HDMI_GENERIC*_SEND`, `CONT`, or `LINE` masks can disable mandatory packets, transmit stale packets every frame, or send packets on invalid lines.
- AFMT fields affect audio routing and memory power. Incorrect audio source, channel-enable, 60958, sample-send, or memory-power masks can cause silent audio, wrong channel mapping, audio dropouts after power transitions, or read-modify-write of status bits.
- DSC/MSA/MST timing fields are mode-sensitive. Incorrect MSA timing, MSO, MSE allocation, DSC mode, bytes-per-pixel, or PPS packet fields may only fail on high-refresh, MST, DSC, deep-color, or multi-stream configurations.
- Status, ack, clear, pending, readback, and power-state fields may have side effects or read-only semantics not represented here. Generic read-modify-write on such fields can be unsafe unless the consumer knows the register contract.
- Generated-register changes can create broad compile or behavior failures because stream encoder, VPG, AFMT, DMUB, and resource construction code all depend on exact macro names.

## Test Signals

Useful validation combines generated-header consistency checks and hardware-facing display tests:

- Build AMDGPU/DC with DCN316 support enabled. Missing or renamed fields should fail in `dcn316_resource.c`, `dcn30_dio_stream_encoder`, `dcn31_vpg`, `dcn31_afmt`, and DMUB DCN316 code.
- Mechanically verify that visible `__SHIFT` entries in lines 39767-42179 have matching `_MASK` entries for fields that the register schema defines as writable/readable bitfields.
- Diff this slice against AMD's authoritative DCN 3.1.6 register database and adjacent generated DCN 3.1.x headers where the hardware block is expected to be layout-compatible.
- Exercise HDMI modes that use generic packets: AVI, vendor, gamut, SPD, HDR static metadata, HF-VSIF, VRR/VTEM, deep color, scrambling above 340 MHz, and packet stop/restart paths.
- Exercise DP modes with secondary packets: audio, HDR metadata, DSC PPS, MST, MSO, ALPM, high refresh, and modes that require correct MSA/VBID timing.
- Run DSC display tests and check for PPS packet delivery, valid decompression, no corruption, and correct transition when DSC is enabled/disabled.
- Test VPG generic packet update paths with both immediate and frame-update modes, including repeated updates and conflict-polling behavior.
- Validate AFMT audio behavior across HDMI and DP: channel mapping, audio infoframes, 60958 channel status, mute/unmute, sample send, suspend/resume, and AFMT memory power transitions.
- Watch kernel logs and display diagnostics for DIG FIFO level errors, DP secondary-packet collision/deadline-missed flags, VPG conflict flags, audio mute/status mismatches, DSC failures, MST allocation problems, and resume-only failures.

## Cross-Chunk Notes

The previous chunk owns the beginning of the DP4 DPHY symbol group and earlier DP4 stream fields. Later chunks continue VPG1 after `VPG1_VPG_GSP_FRAME_UPDATE_CTRL` and cover the remaining VPG/DME/AFMT/DIG/DP instances and other generated DCN 3.1.6 register families. The final per-file report should merge adjacent chunks before making complete statements about all DCN316 stream encoders, all packet-generator instances, or the full `dcn_3_1_6_sh_mask.h` hardware map.

### subset-b-001914: lines 42180-44523

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 42180-44523

## Purpose

This chunk is generated AMD DCN 3.1.6 field shift/mask metadata. It contains no executable driver logic; it publishes C preprocessor constants that tell common AMD display register helpers where each hardware bitfield lives inside an MMIO register.

The requested range covers 2,181 `#define` lines: 1,084 `__SHIFT` constants and 1,097 `_MASK` constants. The range starts in the middle of `VPG1_VPG_GSP_FRAME_UPDATE_CTRL`, then covers the rest of the DIG1 VPG status/power/infoframe tail, complete DME/VPG blocks for DIG2 through DIG4, complete DP AUX blocks for AUX0 through AUX3, and the first half of DP AUX4 through `DP_AUX4_AUX_DPHY_RX_CONTROL0__AUX_RX_TRANSITION_FILTER_EN_MASK`. The range ends mid-register; later chunk research must complete the remaining DP AUX4 DPHY RX fields and any following AUX4 registers.

Although this repository path is under a local `ceph-client` mirror, this source is AMDGPU display hardware metadata, not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocations, or runtime APIs in this chunk. Its interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position used by `REG_GET`, `REG_SET`, `REG_UPDATE`, and related helpers.
- `<REGISTER>__<FIELD>_MASK`: bit mask used with the shift constant to isolate or program a field.
- `// addressBlock: ...` comments: generated grouping markers for hardware register blocks.

Major register families in this chunk:

- `VPG1_VPG_*` tail: completes generic packet frame/immediate update masks for packet slots 0-14, generic lock/conflict status, VPG GSP memory power, ISRC indexed data access, and MPEG infoframe bytes/update.
- `DME2_DME_*`, `DME3_DME_*`, and `DME4_DME_*`: Display Metadata Engine control and memory power fields. These include metadata HUBP requestor selection, engine enable, stream type, double-buffer pending/taken/disable/clear bits, missed-transmission status/clear bits, and DME memory power force/disable/state/default low-power fields.
- `VPG2_VPG_*`, `VPG3_VPG_*`, and `VPG4_VPG_*`: Video Packet Generator field layouts for generic packet memory access, packet payload bytes, per-slot frame update and immediate update requests/pending bits for slots 0-14, generic access conflict/clear state, GSP memory power, ISRC bytes, and MPEG infoframe payload/update fields.
- `DP_AUX0_AUX_*` through `DP_AUX3_AUX_*`: complete DisplayPort AUX engine field layouts for control, software transaction control, arbitration, interrupts, software and link-service status, software/link-service data windows, DPHY TX/RX timing controls and status, GTC synchronization control/error/status, and PHY wake control.
- `DP_AUX4_AUX_*`: partial fifth AUX engine field layouts, complete through software/link-service data windows and TX timing controls, ending partway through RX control 0.

The VPG instances share the same field geometry: generic packet access index uses bits 7:0; packet data bytes occupy 8-bit lanes at 0, 8, 16, and 24; generic packet update request bits occupy slots 0-14; update-pending bits occupy slots 16-30; memory power uses light-sleep disable at bit 0, force at bit 4, and state at bit 8.

The AUX instances also share a repeated layout. `AUX_CONTROL` exposes enable/reset/reset-done, link-service read enable/update disable, HPD disconnect handling, mode detect, HPD select, impedance calibration request enable, test mode, deglitch, and spare bits. `AUX_ARB_CONTROL` arbitrates SW and DMCU ownership. `AUX_SW_CONTROL` starts software transactions and programs start delay/write-byte count. `AUX_SW_DATA` is an indexed/autoincrementing data window. `AUX_SW_STATUS` and `AUX_LS_STATUS` report completion, request state, timeout/overflow/HPD disconnect, invalid symbol/stop/start conditions, reply byte count, arbitration state, CP IRQ, update, and update ack.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by consuming AMD display code:

1. DCN316 resource construction includes `dcn_3_1_6_offset.h` and this `dcn_3_1_6_sh_mask.h`.
2. Register-list macros in AMD display objects paste instance names into these generated constants.
3. Shift/mask tables are initialized once as static data, for example `vpg_shift`, `vpg_mask`, `aux_shift`, and `aux_mask` in `display/dc/resource/dcn316/dcn316_resource.c`.
4. Runtime helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and `REG_WAIT` use the selected register address plus the shift/mask entry to access the actual hardware field.

Concrete consumer paths verified in this tree:

- `display/dc/resource/dcn316/dcn316_resource.c` includes this header, builds `vpg_regs[]` for VPG0-VPG9 with `VPG_DCN31_REG_LIST(id)`, initializes `vpg_shift`/`vpg_mask` with `DCN31_VPG_MASK_SH_LIST`, builds AUX register arrays for AUX0-AUX4, and initializes `aux_shift`/`aux_mask` with `DCN_AUX_MASK_SH_LIST`.
- `display/dc/dcn30/dcn30_vpg.c` writes generic info packets by polling `VPG_GENERIC_STATUS.VPG_GENERIC_CONFLICT_OCCURED`, clearing `VPG_GENERIC_CONFLICT_CLR`, selecting `VPG_GENERIC_DATA_INDEX`, writing header/body bytes through `VPG_GENERIC_PACKET_DATA`, and then triggering either a per-packet immediate update or frame update.
- `display/dc/dcn31/dcn31_vpg.c` uses the VPG memory-power fields to force/allow light sleep and read `VPG_GSP_MEM_PWR_STATE`.
- `display/dc/dce/dce_aux.c` acquires AUX ownership via `AUX_ARB_CONTROL`, enables/resets the AUX block via `AUX_CONTROL`, programs AUX request bytes through `AUX_SW_CONTROL` and `AUX_SW_DATA`, triggers `AUX_SW_GO`, waits on `AUX_SW_STATUS.AUX_SW_DONE`, and parses reply length/status with `AUX_SW_REPLY_BYTE_COUNT`.
- `display/dc/dio/dcn32/dcn32_dio_stream_encoder.h` includes DME metadata fields in the stream encoder mask/shift list, so DME control bits are part of DCN stream encoder metadata programming.

## State And Persistence Behavior

This chunk stores no software state. It describes MMIO-backed display hardware state:

- VPG registers hold generic SDP/info packet staging memory, per-packet update request state, update-pending status, conflict/lock status, ISRC and MPEG infoframe payloads, and VPG GSP memory power controls.
- DME registers hold metadata-engine routing and enable state, double-buffer lifecycle bits, missed-transmission status, and DME memory low-power policy/state.
- AUX registers hold DisplayPort sideband transaction engine state, AUX ownership arbitration between software and DMCU/firmware, interrupt status/ack/mask bits, SW and link-service request/reply buffers, physical-layer TX/RX timing configuration, GTC synchronization state/error counters, and PHY wake behavior.

Persistence is hardware-defined. Configuration fields usually persist until driver reprogramming, display power-gating, suspend/resume, GPU reset, or ASIC reset. Status, pending, ack, clear, interrupt, and data-window fields can be read-only, sticky, self-clearing, write-one-to-clear, or side-effecting depending on the hardware register; this generated header does not encode access type or ordering semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- The companion offset header `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`, because these field layouts are only meaningful when paired with the matching register offsets and base indices.
- Common AMD display register helper macros from `display/dc/inc/reg_helper.h` and object-specific list macros such as `DCN31_VPG_MASK_SH_LIST`, `DCN_AUX_MASK_SH_LIST`, and stream encoder `SE_SF` lists.
- DCN316 resource construction in `display/dc/resource/dcn316/dcn316_resource.c`, which binds these generated constants into per-object tables used by VPG, AUX, link encoder, and stream encoder instances.
- VPG implementation files under `display/dc/dcn30/` and `display/dc/dcn31/`, which perform packet staging, update triggering, and VPG memory power handling.
- AUX implementation files under `display/dc/dce/` and link encoder code under `display/dc/dio/`, which use the AUX control/arbitration/status/data fields for DP AUX and I2C-over-AUX transactions.
- Stream encoder metadata paths, especially DCN32-style metadata fields in `display/dc/dio/dcn32/dcn32_dio_stream_encoder.h`, where DME control bits are listed for dynamic metadata/secondary-data-packet programming.

The in-tree DCN316 resource table instantiates five AUX engines (`AUX0` through `AUX4`) and at least VPG instances 0-9. This chunk therefore covers live DCN316 instances, not merely unused generated definitions.

## Risks And Edge Cases

- Field drift is the central risk. A wrong mask or shift compiles cleanly but causes `REG_UPDATE` and `REG_GET` to touch the wrong bits in a live MMIO register.
- The chunk boundaries are artificial. The first visible lines are the tail of `VPG1_VPG_GSP_FRAME_UPDATE_CTRL`, so full VPG1 ownership is split with the previous chunk. The last visible lines stop mid-`DP_AUX4_AUX_DPHY_RX_CONTROL0`, so full AUX4 ownership is split with the next chunk.
- VPG packet update bits are indexed by packet slot 0-14. A shifted or mismatched field can update the wrong generic packet, leave a pending bit uncleared, or cause stale HDR/AVI/vendor/ISRC/MPEG metadata to be transmitted.
- VPG conflict and memory-power fields are sequencing-sensitive. Bad conflict clearing or light-sleep control can race with hardware reads of GSP memory and cause packet corruption or intermittent update failures.
- DME metadata fields affect dynamic metadata routing and double-buffer lifecycle. Incorrect HUBP requestor, stream type, pending/taken clear, or missed-transmission clear fields can silently drop or misroute metadata packets.
- AUX arbitration fields protect shared ownership between software and firmware. Bad `AUX_SW_USE_AUX_REG_REQ`, `AUX_SW_DONE_USING_AUX_REG`, DMCU request, or status bits can deadlock access, steal an engine from firmware, or make software believe the engine is available when it is not.
- AUX status and reply count fields feed error handling in `dce_aux.c`. Wrong timeout, overflow, HPD disconnect, invalid symbol, or reply-byte-count masks can convert real link errors into bogus successful replies, truncate DPCD/EDID data, or cause retry storms.
- AUX data-window fields are side-effecting and indexed. Wrong `AUX_SW_INDEX`, `AUX_SW_DATA_RW`, `AUX_SW_AUTOINCREMENT_DISABLE`, or data-byte masks can corrupt outgoing DP AUX headers/payloads or read the wrong reply bytes.
- AUX DPHY timing and GTC sync fields are link-quality sensitive. Incorrect TX precharge, RX detection/window/timeout, or GTC sync masks may only fail on marginal cables, adapters, resume paths, or compliance tests.
- Instance repetition hides copy/paste hazards. AUX0-AUX4 and VPG2-VPG4 should generally share layouts; a single instance-specific deviation may only affect one connector or one stream encoder.

## Test Signals

Useful validation combines generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU display support with DCN316 enabled. Missing or renamed macros should fail in `dcn316_resource.c`, VPG mask/shift lists, AUX mask/shift lists, or stream encoder metadata lists.
- Mechanically verify every complete field in this range has exactly one `__SHIFT` and one `_MASK` macro, allowing for the known partial boundaries at the start and end of the chunk.
- Diff VPG2/VPG3/VPG4 and AUX0/AUX1/AUX2/AUX3 repeated layouts against each other and against AMD's authoritative DCN 3.1.6 register database. Treat unexpected per-instance differences as high risk.
- Exercise generic info packet programming on DCN316: modesets, HDR metadata, vendor-specific packets, ISRC/MPEG packets if exposed, immediate update and frame update paths, and multi-stream cases using different VPG instances.
- Monitor for VPG conflict timeouts, persistent update-pending bits, stale metadata on the wire, display metadata CRC/compliance failures, and failures after display power-gating or suspend/resume.
- Exercise DME metadata paths with dynamic metadata enabled where supported, including stream changes, HUBP/requestor changes, and double-buffer update timing.
- Exercise DP AUX and I2C-over-AUX: DPCD reads/writes, EDID reads, link training, HPD plug/unplug, HPD-low transaction aborts, MST sideband if available, eDP panel bring-up, and suspend/resume.
- Watch kernel logs and display diagnostics for AUX acquisition failures, AUX timeout/overflow/invalid-reply retries, EDID/DPCD read failures, link training instability, HPD storms, and one-connector-only failures that point to an AUX instance layout issue.
- Run DP compliance or analyzer-based tests for AUX waveform/timing and GTC sync when changing any AUX DPHY or sync field definitions.

## Cross-Chunk Notes

This chunk must be reconciled with `subset-b-001913` for the beginning of VPG1 and with `subset-b-001915` for the remainder of DP AUX4. The final per-file report should avoid treating this chunk as a complete description of either `VPG1_VPG_GSP_FRAME_UPDATE_CTRL` or `DP_AUX4_AUX_DPHY_RX_CONTROL0`; both are split by chunk boundaries.

### subset-b-001915: lines 44524-46938

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 44524-46938

## Scope

This chunk is generated AMD DCN 3.1.6 display register field metadata. It contains C preprocessor constants only: paired `__SHIFT` and `_MASK` macros for fields in DisplayPort AUX, display I2C/DDC, DIO/DCIO, GPIO, DC perfmon, and UNIPHY register blocks. There are no functions, structs, enums, executable branches, loops, allocations, includes, or software-owned data structures in this range.

The reviewed span contains 2,152 `#define` entries: 1,074 shift definitions and 1,078 mask definitions. The mismatch is from chunk boundaries. The range begins with the mask tail for `DP_AUX4_AUX_DPHY_RX_CONTROL0`, whose shift definitions are in the previous chunk, and it ends at `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED37__UNIPHY_MACRO_CNTL_RESERVED__SHIFT`, before the matching mask in the next chunk.

Although this repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU Display Core hardware metadata rather than Ceph or distributed filesystem logic.

## Purpose And Hardware Surface

The purpose of this header slice is to describe bit layouts for DCN 3.1.6 display I/O registers. The companion `dcn_3_1_6_offset.h` header supplies register offsets and base-index selectors; this file supplies the field masks and shifts consumed by AMD Display Core register helpers.

The hardware surface covered here is broad but centered on display connector I/O:

- The tail of the `DP_AUX4` register family, including AUX DPHY receive timing, transmit/receive status, Global Time Counter sync control/status/error fields, and AUX PHY wake request handshaking.
- The `dce_dc_dio_dout_i2c_dispdec` block, including display I2C controller control, arbitration, interrupts, software status, DDC hardware status, per-DDC speed/setup registers, transaction descriptors, data FIFO/index access, EDID-detect control, and read-request interrupts.
- The `dce_dc_dio_dio_misc_dispdec` block, including scratch registers, DIO memory power status/control, DIO clock gating, DIG soft reset, DIO power management, HDMI RX status timer control, PSP/generic interrupt status/clear, and per-link DIO controls for links A through F.
- The `dce_dc_dio_dio_dcperfmon_dc_perfmon_dispdec` block for `DC_PERFMON18`, covering counter selection/control, state, perfmon control, current-value interrupt/misc state, and high/low counter readbacks.
- The `dce_dc_dcio_dcio_dispdec` block, including generic DC registers, DCIO/ref clock controls, UNIPHY A-G link invert and channel crossbar fields, write-command delay, pinstrap readback, intercept state, backlight PWM frame-start source selection, genlock/swaplock pad controls, and DCIO soft reset.
- The `dce_dc_dcio_dcio_chip_dispdec` block, including generic GPIO, DDC/AUX pads, VGA DDC, genlock/swaplock pads, HPD pads, panel power-sequencer GPIO controls, pad strength, AUX PHY control, GPIO RX/pullup/drive behavior, AUX analog tuning, and AUX/I2C pad power-good status.
- The start of UNIPHY macro-control reserved apertures for UNIPHY0 and UNIPHY1, where each exposed reserved register is represented as a full 32-bit field.

## Important Definitions

The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low-bit position for a field in a 32-bit register value.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the same register.
- `//<REGISTER>` comments group fields by generated register name.
- `// addressBlock: ...` comments mark the hardware address block whose register names follow.

Important register families in this range:

- `DP_AUX4_AUX_DPHY_RX_CONTROL1`, `DP_AUX4_AUX_DPHY_TX_STATUS`, and `DP_AUX4_AUX_DPHY_RX_STATUS` describe AUX physical-layer receive timeout/precharge timing and low-level TX/RX state readbacks, including half-symbol-period and sync-valid count fields.
- `DP_AUX4_AUX_GTC_SYNC_CONTROL`, `DP_AUX4_AUX_GTC_SYNC_ERROR_CONTROL`, `DP_AUX4_AUX_GTC_SYNC_CONTROLLER_STATUS`, and `DP_AUX4_AUX_GTC_SYNC_STATUS` describe DisplayPort AUX GTC synchronization enablement, calibration, lock acquisition/maintenance timing, error thresholds, lock/error status, reply byte counts, NACK/timeouts, invalid AUX symbol conditions, and acknowledge fields for critical/potential/definite error events.
- `DP_AUX4_AUX_PHY_WAKE_CNTL` exposes wake request, pending, priority, and acknowledge bits for AUX PHY wake sequencing.
- `DC_I2C_CONTROL` starts software-driven display I2C transactions with `DC_I2C_GO`, reset/status-reset controls, DDC channel selection, transaction count, and debug reference selection.
- `DC_I2C_ARBITRATION` coordinates software, hardware, and DMCU ownership of the shared I2C registers with priority, request/done bits, queued-go behavior, and hardware/software abort controls.
- `DC_I2C_INTERRUPT_CONTROL` packs software-done interrupt/status/mask/ack bits and hardware-done interrupt/status/mask/ack fields for DDC1 through DDC6 plus DDCVGA.
- `DC_I2C_SW_STATUS` reports software controller completion, abort, timeout, interrupt, buffer overflow, NACK per transaction, and software request state.
- `DC_I2C_DDC<n>_HW_STATUS` for DDC1-DDC5 reports hardware transfer state, done/request/urgent flags, EDID-detect result, valid-try count, and EDID-detect state.
- `DC_I2C_DDC<n>_SPEED` and `DC_I2C_DDC<n>_SETUP` for DDC1-DDC5 define I2C threshold, filtering, start/stop timing, prescale, drive controls, send-reset length, EDID detect enable/mode, DDC enable, clock drive, intra-byte/transaction delay, and time-limit fields.
- `DC_I2C_TRANSACTION0` through `DC_I2C_TRANSACTION3` define the up-to-four segment transaction descriptor model: read/write direction, stop-on-NACK, start/stop, and transfer byte count.
- `DC_I2C_DATA` defines data byte, read/write selector, data index, and index-write fields used to access the I2C data buffer.
- `DC_I2C_EDID_DETECT_CTRL` and `DC_I2C_READ_REQUEST_INTERRUPT` define automatic EDID detect timing/retry/reset behavior and read-request interrupt/ack/mask state for DDC1-DDC6 and DDCVGA.
- `DIO_SCRATCH0` through `DIO_SCRATCH7` are full-width scratch registers.
- `DIO_MEM_PWR_STATUS`, `DIO_MEM_PWR_CTRL`, and `DIO_MEM_PWR_CTRL2` expose light-sleep status, disable, and force fields for I2C and DP link memories A-G.
- `DIO_CLK_CNTL`, `DIO_CLK_CNTL2`, and `DIO_CLK_CNTL3` expose display/ref/soc/symbol/TMDS clock gating controls for DIO, DIG, AFMT, and per-link symbol clocks.
- `DIG_SOFT_RESET`, `DIO_POWER_MANAGEMENT_CNTL`, and `DCIO_SOFT_RESET` define reset and power-management controls for digital front-end/back-end blocks, UNIPHY A-G, DSYNC A-G, and panel power sequencers.
- `DIO_PSP_INTERRUPT_STATUS`, `DIO_PSP_INTERRUPT_CLEAR`, `DIO_GENERIC_INTERRUPT_MESSAGE`, and `DIO_GENERIC_INTERRUPT_CLEAR` describe DIO interrupt handoff/status for PSP and generic interrupt paths.
- `DIO_LINKA_CNTL` through `DIO_LINKF_CNTL` carry per-link enable and PHY selection fields.
- `DC_PERFMON18_*` defines a generated perfmon instance, including counter enable/reset/clear/start/stop/update-mode/mode/window, event/source selection, counter state snapshots, perfmon enable/window/mode, interrupt status/ack/mask, high/low readback, and current-value comparisons.
- `UNIPHYA_LINK_CNTL` through `UNIPHYG_LINK_CNTL` and matching `UNIPHY*_CHANNEL_XBAR_CNTL` define per-lane polarity inversion and channel crossbar source selection for UNIPHY links A-G.
- `DC_PINSTRAPS`, `INTERCEPT_STATE`, `DCIO_BL_PWM_FRAME_START_DISP_SEL`, `DCIO_GSL_GENLK_PAD_CNTL`, and `DCIO_GSL_SWAPLOCK_PAD_CNTL` expose boot strap state, power/DPCS intercept readbacks, backlight PWM frame-start source selection, and genlock/swaplock GSL flip-ready/mask controls.
- `DC_GPIO_GENERIC_*` provides mask/pull/receive, output value, output enable, and readback fields for generic GPIO A-G.
- `DC_GPIO_DDC1_*` through `DC_GPIO_DDC5_*` and `DC_GPIO_DDCVGA_*` provide DDC clock/data mask, pull-down, receive, AUX pad mode, AUX polarity, hardware pull-down allow, pad-strength, output value, output enable, and readback fields.
- `DC_GPIO_GENLK_*` and `DC_GPIO_HPD_*` provide mask/pull/receive/output-enable/readback controls for genlock clock, genlock vsync, swaplock A/B, and HPD1-HPD6. HPD enable also includes Schmitt-trigger, slew, select, and spare pad fields.
- `DC_GPIO_PWRSEQ0_EN`, `DC_GPIO_PWRSEQ1_EN`, `DC_GPIO_PAD_STRENGTH_1`, `DC_GPIO_PAD_STRENGTH_2`, `PHY_AUX_CNTL`, and `DC_GPIO_TX12_EN` cover panel power/backlight GPIO routing, pad drive strength, AUX PHY enable/control, and 1.2 V transmit enable style controls for generic GPIO pins.
- `DC_GPIO_AUX_CTRL_0` through `DC_GPIO_AUX_CTRL_5`, `DC_GPIO_RXEN`, and `DC_GPIO_PULLUPEN` define AUX/DDC/HPD analog tuning, spike rejection, comparator selection, bias/resistance controls, differential pair swap, hysteresis, VOD tune, I2C pad mode, 1.2 V power enables, RX enables, and pull-up enables.
- `AUXI2C_PAD_ALL_PWR_OK` reports power-good status for AUX/I2C PHYs 1-6.
- `DCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57` and `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0` through the shift half of `RESERVED37` expose full 32-bit reserved macro-control register fields. These are generated placeholders for PHY macro control aperture entries whose internal bit layout is not named in this header.

## Control Flow

This header has no executable control flow. Runtime sequencing is supplied by AMDGPU Display Core and DMUB code that includes `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h`, constructs register tables through token-pasting macros, and calls register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `FD_MASK`, and `FD_SHIFT`.

A typical use path is:

1. DCN316 resource, AUX, I2C, GPIO, link encoder, or DMUB code selects a register by generated name.
2. The offset header maps that register name to an MMIO offset and base segment.
3. This shift/mask header maps a field name to the low bit and mask used for packing or extracting values.
4. Register-helper macros preserve unrelated fields, update selected fields, poll hardware state, or acknowledge interrupt/status bits.
5. The hardware block performs the actual AUX/I2C transfer, DIO/DCIO reset or gating operation, GPIO pad transition, perfmon capture, or PHY macro behavior.

The macros do not encode protocol ordering. Callers must still implement AUX retry/timeout policy, I2C transaction setup and FIFO order, DDC arbitration handoff, interrupt clear ordering, clock/power gating preconditions, reset sequencing, HPD debounce/polarity policy, and PHY analog programming constraints.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes GPU MMIO register state in DCN 3.1.6 display I/O blocks.

Configuration-like hardware fields include AUX/GTC sync enable and thresholds, AUX PHY wake request/priority, I2C controller setup, DDC speed and setup parameters, I2C transaction descriptors, EDID detect policy, interrupt masks, DIO memory light-sleep controls, DIO/DCIO clock gating, soft reset bits, UNIPHY lane invert and crossbar selection, genlock/swaplock pad routing, GPIO output enables and output values, DDC/AUX pad modes, HPD pad electrical controls, panel power-sequencer GPIO routing, AUX analog tuning, and reserved UNIPHY macro-control words.

Readback/status fields include AUX TX/RX state, GTC sync lock/error/status, AUX PHY wake pending/ack, I2C software and hardware status, NACK/timeout/abort flags, EDID-detect status, DIO memory power state, pinstrap and intercept state, PSP/generic interrupt state, perfmon counter state and values, GPIO readback values, HPD/DDC/AUX receive state, AUX/I2C power-good status, and full-width scratch or reserved readback registers.

Several fields are side-effect prone by name: `*_ACK`, `*_CLEAR`, `*_GO`, reset fields, abort fields, soft reset fields, interrupt mask/ack fields, read-request acknowledgements, I2C data index-write, perfmon clear/reset/start/stop, and PHY wake request bits. The generated masks do not distinguish read-only, sticky, self-clearing, write-one-to-clear, or destructive control fields; functional code and hardware documentation must supply those semantics.

## Dependencies And Integration Points

This chunk must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`. The offset header defines register addresses and base indexes; this shift/mask header defines bit layouts. A missing generated macro usually fails compilation, while a wrong numeric mask or shift can compile and silently program or decode the wrong hardware bits.

Direct include sites found in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`, which includes the DCN316 offset and shift/mask headers to populate `dmub_srv_dcn316_regs` with register offsets, masks, and shifts for DMUB-facing register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes the same generated headers before constructing DCN316 resource objects and register tables used by DCE/DCN helper modules.

Functional consumers are mostly indirect through display hardware object macros and shared helper layers:

- `dce/dce_aux.h` and related AUX implementations consume DP AUX register layouts for AUX transactions, wake handling, and timing/status polling.
- `dce/dce_i2c.h` and I2C/DDC code consume `DC_I2C_*` and `DC_GPIO_DDC*` fields for EDID/DDC transfers, arbitration, error handling, and DDC pad setup.
- `dio/dcn10/dcn10_dio.h`, link encoder/resource code, and DCN316 resource construction bind DIO/DCIO, UNIPHY, HPD, GPIO, and reset fields into per-link display output objects.
- DMUB service code consumes a generated subset through `DMUB_DCN31_REGS()` and `DMUB_DCN31_FIELDS()`, where `FD_MASK` and `FD_SHIFT` resolve to definitions in this file.
- Perfmon/debug paths can use `DC_PERFMON18_*` fields for event selection, counting windows, interrupt status, and counter readback.

The register names are hardware-instance specific. `DP_AUX4` fields target the fifth generated AUX instance, DDC1-DDC5/DDC6/DDCVGA fields target different I2C/DDC channels, UNIPHY A-G fields target specific physical link macros, and HPD1-HPD6 fields target connector hotplug pads. Token-pasting code can resolve successfully even when the wrong instance prefix is selected, so instance binding is a key integration risk.

## Risks And Maintenance Notes

- The primary risk is generated-header drift from the DCN 3.1.6 register database. A wrong bit position can silently break AUX, DDC/EDID, HPD, GPIO, link PHY, reset, power, or perfmon behavior.
- The chunk starts mid-register. `DP_AUX4_AUX_DPHY_RX_CONTROL0` has only mask definitions here; its shift definitions are in the previous chunk. The final per-file report should merge adjacent chunks before presenting that register as complete.
- The chunk ends mid-register. `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED37` has only the shift definition here; its mask definition continues in the next chunk.
- I2C/DDC fields are dense and protocol-sensitive. Incorrect transaction count, byte count, start/stop, data index, or stop-on-NACK masks can corrupt EDID reads, sideband DDC transactions, or firmware/driver arbitration.
- DDC arbitration fields coordinate software, hardware, and DMCU access. Incorrect request/done/abort masks can deadlock the I2C register aperture or make concurrent ownership unsafe.
- Interrupt groups pack status, ack, and mask fields together. Treating an ack or clear bit like persistent state can drop events, while failing to preserve mask bits can disable DDC, read-request, PSP, generic, or perfmon interrupts unexpectedly.
- AUX/GTC sync status and control fields include timing, lock, retry, and error threshold bits. Bad values can make DisplayPort AUX GTC synchronization unreliable or hard to diagnose.
- Clock gating, memory light-sleep, reset, and PHY wake fields can affect live display links. Programming them without sequencing around link disable, power state, or DMUB ownership can cause display blanking, AUX failures, or resume problems.
- GPIO and pad-control registers mix logical GPIO state with electrical characteristics such as pull enables, receiver enables, slew, comparator, bias, resistance, polarity, and pad strength. Mask drift can create board-specific failures that only show up on certain connector routings.
- HPD and DDC/AUX fields are instance repeated but not uniform in every detail. DDCVGA lacks some DDCn fields, HPD groups include per-pair spare/tuning bits, and DDC1-DDC5 hardware status appears here while interrupt/read-request groups also include DDC6 and DDCVGA.
- Reserved UNIPHY macro-control registers are full-width placeholders. They may be intentionally opaque, fuse/firmware controlled, or subject to separate PHY documentation; broad writes to these fields are especially risky without authoritative programming guidance.

## Test Signals

Useful validation for changes touching this chunk includes:

- Compile AMDGPU Display Core with DCN316 enabled. This catches missing, renamed, or malformed macros referenced through DCN316 resource and DMUB register tables.
- Regenerate or mechanically compare `dcn_3_1_6_sh_mask.h` and `dcn_3_1_6_offset.h` against the authoritative DCN 3.1.6 register database, with special attention to the boundary registers `DP_AUX4_AUX_DPHY_RX_CONTROL0` and `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED37`.
- Preprocess representative DCN316 `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT` call sites to ensure token concatenation resolves to the intended register instance and field macros.
- Validate DDC/EDID reads on DCN316 hardware across ports routed to DDC1-DDC5 and any DDC6/DDCVGA path represented by interrupt/read-request fields: hotplug, modeset, EDID retry, NACK handling, timeout handling, and suspend/resume.
- Validate DisplayPort AUX behavior on the AUX4 instance: native AUX reads/writes, link training sideband access, AUX timeout/error reporting, wake behavior, and GTC sync status where supported.
- Validate HPD behavior on all connector pads represented here: plug/unplug, IRQ generation, debounce/polarity handling, runtime suspend/resume, and wake from low-power states.
- Validate GPIO/DDC/AUX pad programming with register dumps before and after modeset, HPD, EDID read, and suspend/resume. Writes should affect only intended masked bits and preserve neighboring electrical-control fields.
- Validate link bring-up on UNIPHY A-G routes affected by lane invert and channel crossbar fields, including multi-lane DisplayPort, HDMI/TMDS paths, and any board-specific lane swizzle.
- Validate reset and clock/power gating transitions around display enable/disable, runtime power management, and display resume, checking that DIO/DCIO/DIG reset bits and light-sleep controls are sequenced without live-link corruption.
- Validate perfmon use by selecting known events, starting/stopping counters, checking high/low readback stability, and verifying interrupt ack/mask behavior for `DC_PERFMON18`.

## Cross-Chunk Notes

Previous chunks own earlier `DP_AUX4` definitions, including the shift half of `DP_AUX4_AUX_DPHY_RX_CONTROL0`. Later chunks continue UNIPHY1 reserved macro-control definitions after `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED37`. The final per-file research document should merge adjacent chunk reports before making complete claims about the full DCN 3.1.6 AUX, DCIO, GPIO, or UNIPHY register namespace.

### subset-b-001916: lines 46939-49518

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 46939-49518

## Purpose

This chunk is generated AMD DCN 3.1.6 register field metadata. It contains no executable C logic; it publishes `#define` constants for bit shifts and masks used to pack, update, and read display-controller MMIO register fields. Consumers include it with `dcn_3_1_6_offset.h` so register-table macros can pair a physical register offset with field-level layout.

The assigned range starts at the tail of `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED37`, covers the remaining UNIPHY macro-reserved register masks for UNIPHY1 and complete reserved maps for UNIPHY2 through UNIPHY6, covers panel power/backlight sequencing fields for `PWRSEQ0` and `PWRSEQ1`, covers DSC compressor instance 0 and 1 fields including DSCC, DSCCIF, DSC_TOP, and local perfmon blocks, and ends inside `DSCC2_DSCC_PPS_CONFIG18`.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, includes, variables, allocation sites, or locks in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a field within a 32-bit register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field.
- Repeated instance prefixes such as `PWRSEQ0_`, `PWRSEQ1_`, `DSCC0_`, `DSCC1_`, and `DSCC2_` expose per-instance copies of the same hardware layouts.

Major macro families in this slice:

- `DCIO_UNIPHY*_UNIPHY_MACRO_CNTL_RESERVED*`: full-width `UNIPHY_MACRO_CNTL_RESERVED` fields with shift `0` and mask `0xFFFFFFFFL` for UNIPHY lanes/blocks 1 through 6. These are opaque/reserved register fields rather than semantically named driver controls.
- `PWRSEQ0_*` and `PWRSEQ1_*`: GPIO power-sequence enable/control/mask/readback, panel power sequencing controls and state, programmable delays, reference dividers, backlight PWM duty/period controls, group-lock/update-pending fields, and spare bits.
- `DSCC0_*` and `DSCC1_*`: complete Display Stream Compression compressor-client layouts for config, status, interrupt/status, PPS configuration registers 0 through 22, memory power, squared/max error counters, rate-buffer fullness counters, rate-control-buffer fullness counters, and debug-bus rotation.
- `DSCCIF0_*` and `DSCCIF1_*`: DSC client interface fields for input underflow recovery/status/interrupts, input pixel format, bits per component, double-buffer update status, acknowledge fields, picture width, and picture height.
- `DSC_TOP0_*` and `DSC_TOP1_*`: top-level DSC clock gating/enables and debug controls.
- `DC_PERFMON19_*` and `DC_PERFMON20_*`: DSC-local performance monitor counter select, enable/clear, mode, state, current value, threshold, and overflow fields.
- `DSCC2_*`: beginning of DSC compressor instance 2, from config/status/interrupt fields through PPS fields for picture geometry, slice geometry, rate-control model parameters, RC thresholds, and range entries through QP range 6.

## Control Flow

This header has no runtime control flow. Runtime sequencing is provided by AMD display code:

1. DCN316 resource and DMUB files include `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h`.
2. Register-list macros such as `SR`, `SRI`, `SRIR`, and field-list macros such as `DSC_SF` paste register and field tokens into names from this file.
3. Resource constructors populate register-offset tables and field shift/mask tables for blocks such as panel control and DSC.
4. Operational code later calls helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and wait/poll wrappers. Those helpers use the shifts and masks in this chunk to preserve unrelated fields while programming panel power, backlight PWM, DSC PPS data, DSC status/interrupt handling, and perfmon counters.

The macros do not encode sequencing requirements. Panel control still has to order power rails, DIGON/BLON, delays, PWM updates, and register locks. DSC code still has to program PPS registers, interface format, memory power, clocks, and double-buffer updates in the order required by the hardware.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU state:

- UNIPHY reserved registers are opaque 32-bit hardware state. Because the fields are named reserved, driver code should avoid relying on undocumented bit meanings unless directed by hardware programming tables.
- `PWRSEQ*` registers represent panel power/backlight state: GPIO output enables, mask/data values, target and readback states, delay counters, PWM duty/period/ref-divider values, group lock state, and update-pending state.
- `DSCC*` registers represent DSC compressor state: slice layout, ICH behavior, rate-control buffer model size, sticky overflow/underflow status, interrupt enables, PPS payload fields, memory low-power/force/disable/state fields, debug selectors, and error/fullness counters.
- `DSCCIF*` registers represent DSC input-interface state and double-buffer update handshake state.
- `DSC_TOP*` registers represent DSC clock/debug gating.
- `DC_PERFMON19/20` registers represent programmable performance counter state and threshold/overflow state for the DSC-related perfmon blocks.

Persistence is hardware-defined. Configuration fields normally retain values until modeset reprogramming, power gating, suspend/resume, or ASIC reset. Status, interrupt, update-pending, acknowledgement, clear, and counter fields may be sticky, self-clearing, write-one-to-clear, read-only, or timing-sensitive. This generated mask file does not identify access type; consuming code and hardware documentation must supply those semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.6 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`, which gives the companion `reg...` offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes this header and builds DCN316 register/field tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`, which includes the same generated DCN316 headers for DMUB-side register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h` and `dcn20_dsc.c`, whose `DSC_REG_LIST_DCN20` and `DSC_REG_LIST_SH_MASK_DCN20` macros consume `DSCC0_*`, `DSCCIF0_*`, and `DSC_TOP0_*` field names and apply them to DSC instances.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn301/dcn301_panel_cntl.h` and `dcn301_panel_cntl.c`, which consume panel/backlight masks for `PANEL_PWRSEQ*`, `BL_PWM*`, and register lock/update-pending fields.

The primary integration pattern is token-pasting, so macro spelling is part of the ABI between generated headers and driver tables. A renamed field, missing mask, or changed shift can break compilation or, worse, compile while corrupting hardware programming if a stale value still matches a token expected by shared helper code.

## Risks And Edge Cases

- Generated masks are untyped constants. A wrong shift or mask can compile cleanly and cause only runtime display failures on specific hardware paths.
- The UNIPHY reserved blocks are especially risky for manual edits because every register is exposed as a full-width opaque field. Accidental writes through these masks could alter undocumented PHY behavior.
- `PWRSEQ0` and `PWRSEQ1` are stateful and timing-sensitive. Bad masks can break embedded panel power-up/down, backlight PWM duty or period, GPIO output selection, register locking, or idle/suspend resume.
- DSC PPS fields must match the DSC encoder model and the DRM DSC configuration. Incorrect masks for bit depth, bits-per-pixel, slice size, RC thresholds, range QP/BPG offsets, or native 4:2:0/4:2:2 flags can produce link bandwidth failures or visible corruption while modesets otherwise appear successful.
- Interrupt/status masks for DSCC buffer overflow/underflow and rate-control-model overflow are sticky/error-path fields; bad clear or enable masks can hide DSC faults or create interrupt storms.
- Perfmon fields are diagnostic but still side-effect-sensitive. Wrong clear, enable, counter-selection, or threshold masks can invalidate performance/debug data.
- Chunk boundaries are artificial. The range begins after part of `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED37` and ends before the rest of `DSCC2`, so final file-level conclusions require adjacent chunks.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN316 support enabled; token-pasting consumers in `dcn316_resource.c`, DMUB DCN316 code, panel control, and DSC code should catch missing or renamed macros.
- Mechanically compare every `__SHIFT` macro in this line range with its matching `_MASK` macro and verify masks align with their shifts and expected field widths.
- Diff this chunk against AMD's authoritative DCN 3.1.6 register database and nearby generated headers such as `dcn_3_1_4_sh_mask.h`, `dcn_3_2_0_sh_mask.h`, or `dcn_3_5_0_sh_mask.h` where hardware compatibility is expected.
- Exercise embedded-panel power paths: boot display bring-up, backlight enable/disable, brightness changes, PWM fractional mode, panel off/on cycles, suspend/resume, and idle optimizations that depend on `PWRSEQ0`.
- Exercise DSC-capable modes on pipes using DSC instances 0, 1, and 2: high-bandwidth modes, slice-count changes, bits-per-component changes, native 4:2:0/4:2:2 cases, MST or high-rate DP where DSC is required, and repeated modesets.
- Monitor kernel logs and display diagnostics for backlight failures, panel stuck-off/stuck-on behavior, DSC underflow/overflow interrupts, rate-buffer fullness anomalies, visual corruption, link-training fallback, and resume regressions.

## Cross-Chunk Notes

Adjacent chunks are required for a complete file report. Earlier chunks contain the beginning of the UNIPHY1 reserved field block and other preceding DCN316 mask families. Later chunks continue `DSCC2_DSCC_PPS_CONFIG18` and the remaining DSC/perfmon/register-mask namespace. The merge lane should preserve that this chunk is only a middle slice of `dcn_3_1_6_sh_mask.h`.

### subset-b-001917: lines 49519-51930

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 49519-51930

## Scope

This chunk is generated AMD DCN 3.1.6 display register field metadata. It contains C preprocessor constants only: paired `__SHIFT` and `_MASK` macros for fields inside Display Stream Compression, HPO, HDMI/DP audio, metadata, video packet generator, DisplayPort stream encoder, and DisplayPort symbol encoder registers. There are no functions, structs, enums, branches, loops, allocations, includes, or software-owned state in this range.

The reviewed span contains 2,145 `#define` entries: 1,076 shift definitions and 1,069 mask definitions. The mismatch is from chunk boundaries. The range starts with the final two masks for `DSCC2_DSCC_PPS_CONFIG18`, whose shifts and earlier masks are above line 49519, and it ends inside `DP_SYM32_ENC1_DP_SYM32_ENC_SDP_GSP_CONTROL12`, before the rest of that register's masks and following GSP controls.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU Display Core hardware metadata rather than distributed filesystem code.

## Purpose And Hardware Surface

The purpose of this header slice is to describe bit layouts for DCN 3.1.6 display hardware registers. The companion `dcn_3_1_6_offset.h` header supplies register addresses or index selectors; this file supplies the masks and shifts used by AMD display register helpers to pack field writes and decode readbacks.

The hardware surface covered here includes:

- Tail fields for DSC compressor instance 2 (`DSCC2`) and its DSC client interface/top/performance monitor blocks.
- HPO top clock/control and HPO DP stream mapper registers.
- HPO HDMI stream encoder 0 audio formatter (`AFMT5`), data/metadata engine (`DME5`), and video packet generator (`VPG5`) registers.
- HPO DP stream encoder 0 and 1 register families, including audio packet generator (`APG0`, `APG1`), DME (`DME6`, `DME7`), VPG (`VPG6`, `VPG7`), and DP stream encoder clock/input/audio/FIFO controls.
- DP 32-symbol encoder instance 0 (`DP_SYM32_ENC0`) video, MSA, SDP/GSP, audio SDP, metadata packet, CRC, panel replay, and memory-power fields.
- The beginning of DP 32-symbol encoder instance 1 (`DP_SYM32_ENC1`), through the first part of `SDP_GSP_CONTROL12`.

These definitions allow higher-level DCN316 resource, stream encoder, audio, metadata, and diagnostics code to bind one register-list template to concrete generated field names for each hardware instance.

## Important Definitions

The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low-bit position for a field in a 16-bit or 32-bit hardware register value.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in that register value.
- `//<REGISTER>` comments group field macros by generated register name.
- `// addressBlock: ...` comments mark the hardware address block that owns following register groups.

Important register families in this range:

- `DSCC2_DSCC_PPS_CONFIG19` through `PPS_CONFIG22` continue the DSC Picture Parameter Set range table for QP ranges 7-14, with min-QP, max-QP, and BPG-offset fields packed in repeated bit groups. The first two lines also complete masks for QP range 6 in `PPS_CONFIG18`.
- `DSCC2_DSCC_MEM_POWER_CONTROL` controls low-power/default/force/disable/state fields for DSC memory and native 4:2:2 memory. `DSCC2_DSCC_*_SQUARED_ERROR_*`, `MAX_ABS_ERROR*`, rate-buffer fullness, rate-control-buffer fullness, and debug-bus rotate registers expose DSC quality/error, buffer, and debug readbacks.
- `DSCCIF2_DSCCIF_CONFIG0` and `CONFIG1` describe DSC client-interface input underflow recovery/interrupt/status, input pixel format, bits per component, double-buffer update-pending, and picture width/height fields.
- `DSC_TOP2_DSC_TOP_CONTROL` and `DSC_DEBUG_CONTROL` expose DSC clock enable, clock-gate disable, debug enable, and test clock mux selection.
- `DC_PERFMON21_*` and `DC_PERFMON22_*` define performance counter event selection, counted-value type, state readback, control/start/stop/clear behavior, current-value interrupt conditions, and high/low counter values for the DSC2 and HPO performance monitor blocks.
- `HPO_TOP_CLOCK_CONTROL` defines per-clock enable, gate-disable, and ready/state fields for HPO DP, HPO HDMI, link symbol, ref, and DP stream clocks. `HPO_TOP_HW_CONTROL` exposes HPO topology/hardware enable state.
- `DP_STREAM_MAPPER_CONTROL0` through `CONTROL3` map logical stream slots to HPO stream encoders.
- `AFMT5_*` covers HDMI audio formatter behavior: VBI/audio packet control, channel enables, DP audio stream ID, HBR overrides, HDMI audio infoframe fields, IEC 60958 channel-status words, audio CRC generation/readback, audio test ramp counters, status bits, FIFO-overflow/audio-enable-change acknowledgements, infoframe source/update, audio source select, and memory-power state.
- `DME5_DME_CONTROL`, `DME6_DME_CONTROL`, and `DME7_DME_CONTROL` expose metadata requestor ID, metadata engine enable, stream type, double-buffer pending/taken/clear/disable, and missed-transmission clear/status fields. Their `DME_MEMORY_CONTROL` registers define DMEM power gating and DME-specific memory power controls.
- `VPG5_*`, `VPG6_*`, and `VPG7_*` describe generic packet access/data, frame-update and immediate-update controls for generic stream packets 0-14, generic packet status, memory power, ISRC packet access/data, and MPEG information registers.
- `DP_STREAM_ENC0_*` and `DP_STREAM_ENC1_*` define stream-encoder clock enables, clock-gate disables, input mux selection, audio mux selection, clock-ramp FIFO threshold/level/clear behavior, FIFO underflow/overflow status and interrupt controls, and spare bits.
- `APG0_*` and `APG1_*` define DP audio packet generator enable, compressed audio mode, double-buffering, packet transmission control, audio CRC test/readback, status, memory-power, and spare fields.
- `DP_SYM32_ENC0_*` defines the first DP symbol encoder instance: encoder enable, HPO stream source select, link/channel selection, video FIFO enable/underflow/status, video MSA double-buffer controls, pixel format, MSA words 0-8, HBLANK minimum symbol width, SDP/GSP transmission controls 0-14, audio SDP, metadata packet control, MSA/VBID/stream/panel-replay control, CRC generation/result/status, memory power, and spare fields.
- `DP_SYM32_ENC1_*` starts the second DP symbol encoder instance with the same control, video FIFO, MSA, pixel format, and GSP transmission-control pattern, but this chunk ends before the full instance-1 register family is present.

## Control Flow

This header has no executable control flow. Runtime sequencing is supplied by AMDGPU Display Core code that includes `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h`, builds register and field tables with generated macros, and then calls register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, or related token-pasting helpers.

A typical use path is:

1. DCN316 resource construction selects a hardware object, such as an HPO DP stream encoder, DP symbol encoder, audio packet generator, VPG, DME, DSC block, or performance monitor.
2. The companion offset header supplies the register address for the selected instance.
3. This shift/mask header supplies the field position and mask.
4. Register helpers pack writes, preserve neighboring fields, decode status, or acknowledge events.
5. Hardware latches configuration, reports status, transmits packets, counts events, gates memory/clocks, or clears sticky status according to the register's hardware semantics.

The macros do not encode ordering. Callers must still sequence DSC setup, HPO clock enable, stream mapping, stream encoder programming, audio packet generator setup, metadata/VPG double-buffer updates, DP symbol encoder enable, CRC tests, interrupt acknowledgements, and memory-power transitions in functional driver code.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes MMIO hardware state in the GPU display engine.

Configuration-like fields include DSC QP ranges, DSC memory power controls, DSC input pixel format and dimensions, DSC/HPO/DP clock enables and gate disables, stream-to-encoder mappings, AFMT audio packet/infoframe/channel-status/ramp/source controls, APG audio packet controls, DME metadata engine controls, VPG generic packet controls, DP stream encoder input/audio muxing, symbol encoder source/link selection, pixel format, MSA/VBID/stream/panel-replay controls, SDP/GSP scheduling, and memory-power controls.

Readback/status fields include DSC squared/max error and buffer fullness counters, underflow and double-buffer pending state, performance counter active/current/high/low/count state, HPO clock ready/state bits, AFMT audio FIFO overflow and audio enable/HBR status, APG CRC/status fields, DME double-buffer taken/pending and missed-transmission state, VPG generic packet/ISRC/MPEG status data, DP stream encoder FIFO levels and underflow/overflow status, DP symbol encoder FIFO underflow/status, CRC results/status, GSP transmission pending/deadline missed/double-buffer pending, and memory-power state.

Several names imply write side effects: interrupt acknowledgements, clear bits, double-buffer update/taken clear bits, FIFO status clears, CRC enable/continuous controls, audio FIFO overflow acknowledge, audio-enable-change acknowledge, metadata missed-transmission clear, and memory-power force/disable controls. The generated mask/shift macros do not label read-only, write-one-to-clear, sticky, self-clearing, or power-managed fields; that behavior must be enforced by the driver code and the hardware specification.

## Dependencies And Integration Points

This chunk must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`. The offset header defines the register addresses; this header defines the bit layouts. A missing macro name generally fails compilation, while an incorrect numeric shift or mask can compile and silently program or decode the wrong hardware bits.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`, which binds DCN316 register metadata for the DMUB service.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes the DCN316 offset and shift/mask headers while constructing display resources, DIO links, and stream encoders.

Functional consumers are mostly indirect through generated register tables. DCN316 resource construction and display objects use these macros to configure DSC, HPO output paths, DP/HDMI stream encoders, audio packet generators, metadata packet paths, video packet generators, performance counters, clock gating, CRC diagnostics, and memory-power controls. The macros in this range are instance-specific; for example `AFMT5`, `DME5`, `VPG5`, `DME6`, `VPG6`, `DP_SYM32_ENC0`, and `DP_SYM32_ENC1` names target different hardware blocks even when their field layouts are repetitive.

## Risks And Maintenance Notes

- The primary risk is generated-header drift from the DCN 3.1.6 register database. Wrong numeric masks or shifts can corrupt DSC PPS programming, clock gating, HPO routing, stream encoder setup, packet scheduling, audio infoframes, metadata transmission, CRC diagnostics, or power-management state without producing a compile error.
- The span starts mid-register. Only the final masks for `DSCC2_DSCC_PPS_CONFIG18` are present here; adjacent chunks own the shifts and earlier masks for QP range 5 and part of range 6.
- The span ends mid-register family. `DP_SYM32_ENC1_DP_SYM32_ENC_SDP_GSP_CONTROL12` is incomplete in this chunk, and later chunks own the remaining masks and following instance-1 SDP/audio/metadata/video/CRC/memory-power fields.
- Many families are repeated by instance. A generator error in one instance may compile because the same field exists for another instance, but runtime failures would appear only on displays or connectors routed through that specific HPO, APG, VPG, DME, or DP symbol encoder instance.
- Dense packet-control fields combine enable, one-shot trigger, double-buffer enable, payload size, start-of-frame reference, line number, pending, and missed-deadline bits. Read-modify-write mistakes can cause missing, duplicated, late, or continuously transmitted secondary data packets.
- Audio fields are protocol-visible. Bad AFMT/APG masks can produce incorrect IEC 60958 channel status, HDMI audio infoframes, HBR state, channel allocation, channel enables, CRC diagnostics, or FIFO acknowledgement behavior.
- Memory and clock power fields can affect display bring-up and suspend/resume. Incorrect force/disable/state masks may leave blocks clock gated, fail to save power, or race with hardware low-power transitions.
- Status/ack/clear fields are easy to misuse because generated macros do not capture side effects. Treating an acknowledge or clear bit as persistent state can drop events; failing to preserve neighboring bits can change unrelated interrupt, FIFO, or double-buffer behavior.

## Test Signals

Useful validation for changes touching this chunk includes:

- Compile AMDGPU Display Core with DCN316 enabled. This catches missing or malformed generated macro names referenced by DCN316 resource, DMUB, stream encoder, DSC, audio, metadata, and diagnostics code.
- Regenerate or mechanically compare `dcn_3_1_6_sh_mask.h` against the authoritative DCN 3.1.6 register database, especially for chunk-boundary registers `DSCC2_DSCC_PPS_CONFIG18` and `DP_SYM32_ENC1_DP_SYM32_ENC_SDP_GSP_CONTROL12`.
- Check that complete register groups in this slice have paired `__SHIFT` and `_MASK` definitions, while allowing the known boundary exceptions at the beginning and end.
- Preprocess representative `REG_GET`, `REG_SET`, `REG_UPDATE`, register-table, and field-table macros to confirm token concatenation resolves to the intended instance-specific symbols such as `AFMT5`, `APG0`, `APG1`, `VPG6`, `DME7`, `DP_STREAM_ENC1`, or `DP_SYM32_ENC0`.
- Runtime DCN316 display tests covering HDMI/DP modeset, HPO stream mapping, DSC-enabled modes, DP stream encoder enable/disable, MST or multi-stream scenarios where available, suspend/resume, and display hotplug.
- Runtime audio tests over HDMI/DP covering PCM playback, channel mapping, multichannel layouts, sample-rate changes, HBR/encoded audio where supported, audio enable/disable, FIFO overflow acknowledgement, and APG/AFMT CRC readback.
- Metadata and packet tests for VPG/DME/DP symbol encoder paths: HDR or other SDP metadata updates, generic packet one-shot and continuous transmission, double-buffer pending/taken transitions, missed-transmission/deadline status, ISRC/MPEG packet fields, and line-number scheduling.
- Register-dump validation before and after programming. Writes should affect only intended masked fields and preserve neighboring bits in dense registers such as GSP controls, AFMT audio packet controls, APG controls, DME controls, VPG frame/immediate update controls, performance monitor controls, memory-power controls, and stream encoder FIFO/status controls.

## Cross-Chunk Notes

Previous chunks own the beginning of DSC instance 2 and the full setup for `DSCC2_DSCC_PPS_CONFIG18` before the final masks visible here. Later chunks continue `DP_SYM32_ENC1` after the partial `SDP_GSP_CONTROL12` definition. The final per-file report should merge adjacent chunk reports before making complete claims about all DCN 3.1.6 DSC or DP symbol encoder instance coverage.

### subset-b-001918: lines 51931-54346

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 51931-54346

## Scope

This chunk is a generated AMDGPU DCN 3.1.6 register shift/mask header slice. It contains only C preprocessor constants: no functions, structs, enums, storage definitions, or executable control flow. The macros describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for HPO DisplayPort stream encoders, audio packet generators, metadata/video packet generators, Symbol32 encoders, DPHY Symbol32 blocks, link encoder spares, and the beginning of DCHVM host-VM controls.

The slice starts in the tail of `DP_SYM32_ENC1` SDP generic stream packet controls and then defines complete repeated register groups for stream encoders 2 and 3. It ends at `DCHVM_CLK_CTRL`, where only the first clock-gating and request-clock fields are present in this chunk.

## Purpose

The header gives the display driver symbolic bitfield names for MMIO register programming. Driver code can compose or decode register values without hard-coded literals by combining these masks and shifts with AMD register access helpers. The chunk covers several hardware responsibilities:

- `DP_STREAM_ENC2` and `DP_STREAM_ENC3`: clock enables, stream/audio input mux selection, and clock-ramp-adjuster FIFO status/control.
- `APG2` and `APG3`: DisplayPort audio packet generator reset, enable, debug audio generation, packet source selection, audio CRC, active/overflow status, memory power, and spare fields.
- `DME8` and `DME9`: metadata engine source selection, enable, stream type, double-buffer pending/taken state, clear bits, missed-transmission state, and memory power.
- `VPG8` and `VPG9`: generic packet byte access, generic packet frame/immediate update requests for slots 0-14 and their pending bits, generic conflict status/clear, memory power, ISRC packet data, and MPEG info packet fields.
- `DP_SYM32_ENC1/2/3`: Symbol32 video stream encoding, MSA payload registers, pixel format, HBLANK symbol width, 15 generic secondary data packet controls, audio SDP controls, metadata packet scheduling, VBID/MSA timing, stream enable/status, panel replay tunneling, video CRC, memory power, and spare registers.
- `DP_LINK_ENC0` and `DP_LINK_ENC1`: clock-control/spare field definitions for link encoder instances, though the visible clock-control fields in this chunk are minimal.
- `DP_DPHY_SYM320` and `DP_DPHY_SYM321`: physical Symbol32 link control/status, stream allocation table update, virtual-channel rate controls, SAT VC and SAT VC status fields, test-pattern configuration and seeds, error status, symbol override, and CRC configuration/status/count.
- `DCHVM`: initial host virtual memory request and display/HVM clock gating fields at the chunk boundary.

## Important Macro Groups

The naming pattern is consistent:

- Register field shift: `<REGISTER>__<FIELD>__SHIFT`
- Register field mask: `<REGISTER>__<FIELD>_MASK`

There are no helper APIs in this file, but these macro names become the API surface consumed by driver register programming macros elsewhere in the AMD DC stack.

### Symbol32 stream encoders

`DP_SYM32_ENC1` tail fields cover `SDP_GSP_CONTROL12` through `SDP_GSP_CONTROL14`, followed by common stream fields. `DP_SYM32_ENC2` and `DP_SYM32_ENC3` are fully represented in this chunk.

Key controls include:

- core enable/reset/status: `DP_SYM32_ENC{2,3}_DP_SYM32_ENC_CONTROL__DP_SYM32_ENC_ENABLE`, `...RESET`, `...RESET_DONE`;
- pixel-to-symbol FIFO setup: `VID_FIFO_CONTROL__PIXEL_TO_SYMBOL_FIFO_ENABLE`, `...RESET_DONE`, `...OVERFLOW_STATUS`;
- double-buffering: `VID_MSA_DOUBLE_BUFFER_CONTROL`, `VID_PIXEL_FORMAT_DOUBLE_BUFFER_CONTROL`, generic SDP `GSP_DOUBLE_BUFFER_ENABLE`, `GSP_DOUBLE_BUFFER_PENDING`, metadata packet double-buffer fields;
- pixel format: `VID_PIXEL_FORMAT__PIXEL_ENCODING_TYPE`, `UNCOMPRESSED_PIXEL_ENCODING`, and `UNCOMPRESSED_COMPONENT_DEPTH`;
- MSA payload words: `VID_MSA0` through `VID_MSA8`, each exposing a full 32-bit `MSA_DATA` field;
- secondary data packet enable/scheduling: `SDP_CONTROL`, `SDP_GSP_CONTROL0` through `SDP_GSP_CONTROL14`, `SDP_AUDIO_CONTROL0/1`, and `SDP_METADATA_PACKET_CONTROL`;
- stream timing/status: `VID_MSA_CONTROL`, `VID_VBID_CONTROL`, `VID_STREAM_CONTROL`, `VID_PANEL_REPLAY_CONTROL`;
- diagnostics: `VID_CRC_CONTROL`, `VID_CRC_RESULT0/1`, `VID_CRC_STATUS`;
- memory/spare: `MEM_POWER_CONTROL` and `SPARE`.

Each GSP control register repeats the same field layout: continuous transmission during video/idle, one-shot trigger and trigger position, double buffering, payload size, SOF reference, deadline missed, trigger pending, double-buffer pending, and a high 16-bit transmission line number.

### HPO DP stream encoder wrappers

`DP_STREAM_ENC2` and `DP_STREAM_ENC3` define clocks and muxes around the Symbol32 encoder path. Their clock-control fields identify whether the stream encoder clock is enabled and sourced/observed on `DISPCLK`, `SOCCLK`, `DPSTREAMCLK`, and `SYMCLK32`. The input mux fields select the pixel stream source and audio stream source. FIFO status/control registers expose enable/reset, read-start level, read clock source, reset-done, video-stream-active, FIFO error, forced recalculation, overwrite/min/max/calculated FIFO levels, and calibration status.

### Audio packet generators

`APG2` and `APG3` are repeated APG register blocks. They expose reset/reset-done, enable, DP audio stream ID, channel-count override, debug generator enable/reset, debug channel enables, packet source selection, audio CRC enable/continuous/channel/count, CRC result/done/clear, audio/HBR status, audio FIFO overflow status/clear, output-active status, memory power controls, and spare fields.

### Metadata and video packet generators

`DME8` and `DME9` hold metadata engine state: HUBP requestor ID, engine enable, stream type, double-buffer pending/taken state, clear/disable bits, transmission-missed status/clear, and DME memory power fields.

`VPG8` and `VPG9` define byte-indexed generic packet data access, 15 generic packet frame update request bits plus 15 pending bits, 15 generic packet immediate update request bits plus 15 pending bits, lock/conflict status and conflict clear, GSP memory light-sleep controls, ISRC data access, and MPEG info packet checksum/byte/format/update fields.

### DPHY Symbol32 blocks

`DP_DPHY_SYM320` and `DP_DPHY_SYM321` are repeated physical/link Symbol32 register blocks. They include:

- control/status: `SYM32_ENABLE`, `SYM32_RESET`, `SYM32_RESET_DONE`, `SYM32_READY`, `PHY_SYMCLK_FE_ON`, `PHY_SYMCLK_FE_OFF`;
- stream allocation/rate: `SAT_UPDATE`, four `VC_RATE_CNTL` registers, four `SAT_VC` configs, and four `SAT_VC_STATUS` views;
- test patterns: lane/select and PRBS selection in `TP_CONFIG`, per-lane PRBS seeds, square pulse width, and `TP_CUSTOM0` through `TP_CUSTOM10`;
- error reporting: total slot count, rate, duplicate VC stream source, missing ACT, unexpected mode transition, illegal stream symbol, rate counter saturation, counter overflow, and cipher errors;
- stream symbol override: four stream override enable/type/symbol slots packed across the register;
- CRC diagnostics: `CRC_CONFIG0`, `CRC_CONFIG1`, `CRC_STATUS`, and `CRC_COUNT`.

## Control Flow

There is no local control flow. The effective hardware programming sequence is external and inferred from the fields:

1. Enable clocks and choose stream/audio sources through `DP_STREAM_ENC*_CLOCK_CONTROL`, `INPUT_MUX_CONTROL`, and `AUDIO_CONTROL`.
2. Reset and enable APG/DME/VPG/Symbol32/DPHY blocks using their reset, reset-done, and enable fields.
3. Program stream metadata: MSA words, pixel format, VBID/MSA scheduling, generic SDP payload control, metadata packet timing, APG audio packets, and VPG generic/ISRC/MPEG packet bytes.
4. Use double-buffer enable/pending or frame/immediate update request/pending bits to commit packet and format updates at a frame boundary or immediately.
5. Monitor status, overflow, missed-transmission, CRC, FIFO, DPHY readiness, and DPHY error bits.
6. Apply memory power settings once blocks are idle or during low-power transitions.

Any actual ordering, polling, locking, and delay behavior must come from AMD DC source files that consume these macros, not from this header.

## State And Persistence

The macros themselves have no runtime state. They describe persistent hardware state stored in display engine registers. Notable state categories exposed by this chunk are:

- latched/clearable status: APG FIFO overflow, APG CRC done, DME metadata double-buffer taken, DME transmission missed, VPG generic conflict, DPHY error status, CRC done, FIFO errors;
- pending state: generic SDP trigger pending, generic SDP double-buffer pending, metadata packet double-buffer pending, VPG frame/immediate update pending, MSA/pixel-format double-buffer pending;
- enable/configuration state: stream encoder clocks, audio/video/metadata packet enables, stream enable, DPHY/Symbol32 enable, virtual-channel allocation, test patterns, memory power mode;
- diagnostic counters/results: video CRC result words, APG audio CRC, DPHY CRC value/count, FIFO calculated levels.

Because these are MMIO bit definitions, writes can have side effects such as clears, resets, hardware commits, and power-state changes. The `_CLR`, `_RESET`, `_UPDATE`, and one-shot trigger fields should be treated as side-effectful by consumers.

## Dependencies And Integration Points

This header depends only on the C preprocessor. Its integration points are generated AMD register address headers and AMD DC register helper macros that expect matching register and field names. The likely consumers are Display Core modules handling HPO DisplayPort stream/link encoders, audio packet generation, metadata packet handling, DisplayPort MST/SST allocation, Panel Replay, CRC diagnostics, and power management.

The register groups are tightly coupled by instance numbering:

- stream encoder 2 uses `APG2`, `DME8`, `VPG8`, and `DP_SYM32_ENC2`;
- stream encoder 3 uses `APG3`, `DME9`, `VPG9`, and `DP_SYM32_ENC3`;
- DPHY Symbol32 blocks `DP_DPHY_SYM320` and `DP_DPHY_SYM321` pair with link encoder instances 0 and 1;
- the `DP_SYM32_ENC1` tail is a continuation from the previous chunk and should be merged with earlier chunk research for the full encoder-1 view.

The masks use `L`-suffixed constants and are suitable for 32-bit register fields. Consumers should avoid assuming signed arithmetic semantics and should use the existing AMD register update/read helpers.

## Risks

- Generated header drift is the main risk: a wrong shift/mask silently programs the wrong hardware bits.
- Repeated blocks are highly similar but instance-specific. Copying an `ENC2`/`VPG8` macro into `ENC3`/`VPG9` code, or mixing DPHY 0/1 macros, can route state to the wrong hardware instance.
- Side-effect bits such as clear, reset, update, one-shot send, and force recalculation fields should not be written through broad read-modify-write sequences unless the caller masks them deliberately.
- Pending/status fields share register layouts with control bits in several groups. Polling code must distinguish writable controls from hardware-owned state.
- Line-number and payload fields are multi-bit packed fields; callers must shift values before masking or use helper macros that do this consistently.
- The chunk boundary splits `DP_SYM32_ENC1` and `DCHVM`, so whole-file research must reconcile adjacent chunks before making file-wide completeness claims.

## Test Signals

Useful validation signals for code using this chunk include:

- compile coverage for all generated macro names referenced by DCN 3.1.6 display code;
- register read/write traces showing correct instance selection for stream encoders 2/3, APG2/3, DME8/9, VPG8/9, DPHY0/1, and link encoder 0/1;
- DisplayPort bring-up tests that verify clock enable, FIFO reset-done, Symbol32 reset-done, DPHY ready, and stream status transitions;
- audio playback and HBR audio tests that check APG enable/status, FIFO overflow, audio mute, ASP/ATP/AIP/ACM/ISRC packet enables, and APG CRC;
- generic SDP, metadata, ISRC, MPEG infoframe, Panel Replay, and one-shot packet tests that watch pending bits clear and expected packets appear on the link;
- CRC diagnostics that compare video CRC, APG audio CRC, and DPHY CRC status/count values against expected test patterns;
- error-injection or compliance tests for DPHY slot count, rate, duplicate VC source, missing ACT, illegal symbol, overflow, cipher, and unexpected mode transition bits;
- low-power tests that exercise APG, DME, VPG, Symbol32 encoder, and DCHVM clock/memory power fields without losing stream state.

## Cross-Chunk Notes

This chunk is partial-file research for `dcn_3_1_6_sh_mask.h`. It should be merged with neighboring chunks to recover full address-block continuity. The previous chunk is needed for the beginning of `DP_SYM32_ENC1` and earlier HPO stream/link blocks. The next chunk is needed for the rest of `DCHVM_CLK_CTRL` and any subsequent DCHVM fields.

### subset-b-001919: lines 54347-56952

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 54347-56952

## Chunk Scope

This chunk is a generated AMD DCN 3.1.6 ASIC register shift/mask header segment. It contains preprocessor constants only: `#define` pairs for hardware bitfield offsets (`__SHIFT`) and masks (`_MASK`), plus generated comments that preserve register and address-block grouping. There are no C functions, structs, enums, global variables, or executable branches in the selected lines.

The range contains 2,606 source lines with 2,058 macro definitions: 1,062 shift constants and 996 mask constants. It spans 32 address blocks and 452 register comments. The chunk starts in the tail of the DCHVM host-VM register block and ends partway through endpoint 1 Azalia pin-control fields, so the final per-file report should merge this with neighboring chunks before making whole-file claims.

## Purpose

The purpose of this header region is to provide symbolic bit layouts for DCN 3.1.6 display, VGA compatibility, performance-monitor, and display-audio hardware registers. AMDGPU display code does not normally hand-code these bit values. Instead, register table builders and helpers such as `FD_MASK`, `FD_SHIFT`, `SF`, `SRI`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT` use these generated symbols to create register-access tables and compose MMIO read/modify/write operations.

At a hardware level, this chunk covers:

- DCHVM host-VM initialization, display/DCF clock-gating controls, GPUVM retention power request controls, RIOMMU prefetch request/status, and active/done status fields.
- DC perfmon debug counter fields for eight clock-domain counters, event selectors, start/stop events, and per-clock counter-off bits.
- Legacy VGA sequencer, CRTC, graphics-controller, and attribute-controller indexed fields.
- Display Azalia F2 codec output and input converter/pin/root-function fields.
- Audio descriptor, sink-info, CRC result, and stream latency/debug fields for the display audio controller.
- Azalia F0 endpoint 0 and the beginning of endpoint 1 converter and pin fields, including stream format, channel/stream IDs, digital converter control, GTC embedding, pin capabilities, channel/speaker allocation, sink info, interrupt status, and multichannel enable fields.

## Important Macro Groups

### DCHVM Host-VM And RIOMMU Fields

The chunk begins after `DCHVM_CLK_CTRL` was introduced by the previous chunk. Visible fields include display clock and DCF clock root/gate disable bits, request/response clock-request modes, GPUVM retention power request disable/force/status fields, RIOMMU prefetch request and power status, and RIOMMU active/prefetch-done status.

These constants line up with hubbub code patterns in nearby DCN generations that initialize the host-VM block by setting `HOSTVM_INIT_REQ`, reading `RIOMMU_ACTIVE`, setting `HOSTVM_POWERSTATUS`, issuing `HOSTVM_PREFETCH_REQ`, waiting for `HOSTVM_PREFETCH_DONE`, and controlling DCHVM clock-gating and memory retention. The macros in this chunk are therefore stateful hardware-control fields even though the header itself is static.

### Perfmon Debug Fields

The `dc_perfmon_dc_perfmondebugind` block defines `PERFMON_DEBUG_ID` and `PERFMON_DEBUG01` through `PERFMON_DEBUG12`. The layout exposes low and high counter words for clock counters 0 through 7, event selector fields in the high-word registers, event start/stop bits in `PERFMON_DEBUG09`, and per-clock plus global counter-off bits in `PERFMON_DEBUG12`.

The defined fields are diagnostic infrastructure. Consumers can select a debug counter/event, start or stop collection, read low/high values, and turn individual counters off. Bugs here would usually show as broken performance/debug telemetry rather than ordinary modeset failures.

### VGA Compatibility Indexed Blocks

Four legacy VGA indexed address blocks are covered:

- `vga_vgaseqind`: `SEQ00` through `SEQ04` reset, dot clock, shift, plane map enable, font-bank, memory size, odd/even, and chain fields.
- `vga_vgacrtind`: `CRT00` through `CRT18`, plus `CRT1E`, `CRT1F`, and `CRT22`, covering horizontal/vertical total, display end, blanking, sync start/end, cursor location/shape, display start, offset, underline, CRTC mode, line compare, and graphics controller index.
- `vga_vgagrphind`: `GRA00` through `GRA08` set/reset, enable set/reset, color compare, rotate, read/write mode, odd/even, chain, memory map select, color don't-care, and bit mask fields.
- `vga_vgaattrind`: `ATTR00` through `ATTR14` palette entries, graphics/text mode controls, monochrome/logical graphics, blink, pixel panning, color select, overscan, plane enable, and pixel shift/count fields.

These fields preserve VGA register compatibility in the generated DCN register map. They are not modern display pipe programming knobs, but wrong masks can affect firmware/BIOS compatibility paths, VGA console handoff, or low-level diagnostic access.

### Azalia F2 Output Codec Fields

The `azendpoint_f2codecind` block defines display-audio codec fields with an `AZALIA_F2_CODEC_*` namespace. The converter side includes format fields (`NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, sample base divisor/multiple/rate, and stream type), channel/stream ID, digital converter channel status bits (`DIGEN`, validity/config, pre/copy/non-audio/professional/level, category code), stripe control, ramp rate, GTC embedding, audio widget capabilities, supported rates/sizes, and stream formats.

The pin side includes connection-list entry, widget output enable, unsolicited-response tag/enable, pin sense, configuration defaults, speaker/channel allocation, downmix information, ACP data, audio descriptors, multichannel enables, lipsync, HBR, sink-info index/data, codec channel-status override registers, digital output status, LPIB snapshot/counter fields, coding type, format-change status/response, wireless display identification, remote keepalive, widget capabilities, pin capabilities, and connection-list length.

These constants back endpoint discovery and programming for HDMI/DP audio. For example, resource construction comments in display core mention using `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`-style registers to find valid audio pins; the F2 register family carries analogous pin default/capability information for the F2 codec namespace.

### Audio Descriptor, Sink Info, And CRC Blocks

The `azendpoint_descriptorind` block defines `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, each carrying maximum channels, supported frequencies, descriptor byte 2, and for descriptor 0 a stereo-specific supported-frequency byte. The `azendpoint_sinkinfoind` block exposes manufacturer ID, product ID, sink description length, port ID words, and sink description string words 0 through 17.

The chunk also defines input and output CRC result windows: `AZALIA_INPUT_CRC0_CHANNEL0` through `CHANNEL7`, `AZALIA_INPUT_CRC1_CHANNEL0` through `CHANNEL7`, `AZALIA_CRC0_CHANNEL0` through `CHANNEL7`, and `AZALIA_CRC1_CHANNEL0` through `CHANNEL7`. Each is a full-width CRC result field. These fields are likely used for audio validation, debug, or hardware self-test rather than normal audio enable sequencing.

### Azalia F2 Input Codec And Root Function Fields

The `azinputendpoint_f2codecind` block mirrors many output-codec patterns for input audio. It defines input converter format, channel/stream ID, digital converter status/control, audio widget capabilities, supported rates/sizes, stream formats, input pin widget/unsolicited/pin-sense/configuration fields, channel allocation, multichannel enable fields for channels 0 through 7, HBR, LPIB snapshot and timer fields, input status control, infoframe checksum/version/length/bytes, channel status low/high, input pin widget capabilities, and input pin capabilities.

The `azroot_f2codecind` block defines root/function-level metadata and controls: vendor/device ID, revision ID, subordinate node count, power state set/reset/actual/status, subsystem ID response fields, converter synchronization, reset, group type, supported size/rate and stream-format parameters, and supported power states including D0/D1/D2/D3, clock-stop, and EPSS support.

### Azalia Stream Instances 0-15

The `azf0stream*_streamind` blocks repeat the same stream-debug layout for stream instances 0 through 15. Each instance defines FIFO size control, latency counter reset, worst-case latency count, cumulative latency count, cumulative request count, and stream debug status. The FIFO control fields include FIFO allocation, FIFO size, and enable; stream debug exposes the active stream ID.

This repetition is an important integration point for display audio stream accounting. Runtime code can configure or inspect a stream instance by using generated array/register-list macros against `AZF0STREAM<n>` names while sharing one implementation body.

### Azalia F0 Endpoint 0

The `azf0endpoint0_endpointind` block is the largest complete block in this chunk. It defines endpoint 0 converter pin debug, converter widget capabilities, converter format and channel/stream ID, digital converter control, stream formats, supported size/rate fields, stripe control, ramp rate, GTC embedding, GTC offset debug, and GTC counter delta/min/max readbacks.

The pin side includes widget capabilities, pin capabilities, unsolicited response, pin sense, widget output enable, channel/speaker allocation, ACP data, audio descriptors 0 through 13, two multichannel-enable register groups, lipsync, HBR, sink-info registers, hot-plug control, forced unsolicited response, default pin configuration, multichannel mode, IEC 60958 channel-status override registers 0 through 8, association information, digital output status, LPIB snapshot/data/timer fields, coding type, format-change status and response, wireless display ID, remote keepalive, audio enable status, and audio enabled/disabled/format-changed interrupt status fields.

Endpoint 0 is likely the primary display-audio endpoint used by DCN 3.1.6 audio paths. The broader display code uses `AUD_COMMON_REG_LIST(id)` and DCN resource tables to create per-audio-instance `AZF0ENDPOINT` index/data registers; the detailed endpoint fields in this chunk are the data payload layout behind those indexed accesses.

### Beginning Of Azalia F0 Endpoint 1

The final address block starts `azf0endpoint1_endpointind` and covers endpoint 1 through `AZF0ENDPOINT1_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA__ACP_TYPE_DEPENDENT_BYTE0__SHIFT`. The visible endpoint 1 layout mirrors endpoint 0 for converter pin debug, converter widget capabilities, converter format, channel/stream ID, digital converter channel-status bits, stream formats, size/rate capabilities, stripe/ramp/GTC controls, pin widget capabilities, pin capabilities, unsolicited response, pin sense, widget output enable, channel/speaker allocation, and the first ACP data fields.

Because the chunk ends mid-register family, endpoint 1 audio descriptor and later pin-control/status fields must be read from the following chunk before synthesizing a whole-file report.

## Important APIs, Types, And Functions

This range exports no callable APIs or C types. Its interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a field.
- `<REGISTER>__<FIELD>_MASK` gives the mask for the same field.
- Register comments such as `//AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_CHANNEL_SPEAKER` and address-block comments such as `// addressBlock: azf0stream0_streamind` preserve generated grouping and instance identity.

The practical consumers are generated register-list tables and display register helpers. Concrete integration examples visible elsewhere in the tree include `dmub_dcn316.c`, which includes `dcn_3_1_6_offset.h` and this `dcn_3_1_6_sh_mask.h` to populate the DCN 3.1.6 DMUB register table with `FD_MASK` and `FD_SHIFT`, and `dcn316_resource.c`, which builds audio shift/mask tables for `AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX` and endpoint data registers. The DCE audio common header maps `AZF0ENDPOINT` index/data registers into `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask`.

## Control Flow

There is no runtime control flow in the chunk. Its effective flow is compile-time and table-driven:

1. DCN 3.1.6-specific source files include the matching offset and shift/mask headers.
2. Register table macros concatenate register and field names into generated symbols such as `DCHVM_RIOMMU_STAT0__HOSTVM_PREFETCH_DONE_MASK` or `AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_CHANNEL_SPEAKER__DOWN_MIX_INHIBIT__SHIFT`.
3. Runtime display code uses the populated register, mask, and shift tables with helpers like `REG_UPDATE`, `REG_GET`, `REG_WAIT`, indexed register access, and DMUB service register operations.
4. Sequencing lives outside this header: hubbub code drives DCHVM init/prefetch and power transitions; display audio code discovers endpoints, configures codecs, enables/disables Azalia audio, programs stream formats, reads sink capabilities, and handles status/interrupt fields.

The generated order is hardware-block order, not execution order. Most registers list all shift macros first and then the matching mask macros, and repeated instances are ordered numerically (`AZF0STREAM0` through `AZF0STREAM15`, then `AZF0ENDPOINT0`, then `AZF0ENDPOINT1`).

## State And Persistence Behavior

The header stores no software state and performs no persistence. The state represented by the macros is hardware state:

- DCHVM fields persist in MMIO registers across the relevant power domain lifetime and control initialization, power status, retention, clock gating, RIOMMU activity, and prefetch completion.
- Perfmon debug counters accumulate hardware counts until reset/disabled or reconfigured; high/low counter fields and counter-off bits are stateful diagnostics.
- VGA indexed registers represent legacy display state such as CRTC timing, cursor, display start, VGA memory access mode, palette/attribute mode, and plane selection.
- Azalia codec, stream, descriptor, sink-info, LPIB, GTC, CRC, and interrupt-status fields reflect display-audio endpoint state, stream assignments, negotiated sink capabilities, timing snapshots, and hardware event flags.

Several fields have clear write-one/ack or handshake semantics implied by their names, such as DCHVM `HOSTVM_PREFETCH_REQ`/`HOSTVM_PREFETCH_DONE`, audio enabled/disabled/format-changed interrupt flags and masks, format-change acknowledgement/response fields, LPIB snapshot lock, hot-plug control, and unsolicited response force. Incorrect bit positions in these fields can cause hangs, missed interrupts, or stale capability reads even though the header itself has no mutable storage.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.1.6 offset header for register addresses and base-index selection. It is useful only when included with code that supplies register accessors and field-table macros.

Important integration points include:

- `display/dmub/src/dmub_dcn316.c`: includes this header and the matching offset header to build the DCN 3.1.6 DMUB register, mask, and shift tables.
- HubBub/DCHVM code in nearby DCN generations: uses `DCHVM_CTRL0`, `DCHVM_MEM_CTRL`, `DCHVM_CLK_CTRL`, `DCHVM_RIOMMU_CTRL0`, and `DCHVM_RIOMMU_STAT0` fields for host-VM initialization and RIOMMU prefetch sequencing.
- `display/dc/dce/dce_audio.h`: defines common Azalia audio register/mask/shift structures and register-list macros around `AZF0ENDPOINT` index/data access.
- `display/dc/resource/dcn316/dcn316_resource.c`: populates DCN 3.1.6 display-audio shift/mask tables using the generated endpoint index/data field names.
- `display/dc/core/dc_resource.c`: constructs audio resources, probes endpoint validity, and comments on using Azalia pin configuration default registers to discover available display audio pins.
- Audio, AFMT/APG, stream encoder, and HPO DP paths: consume audio endpoint and stream state indirectly when configuring HDMI/DP audio, channel allocation, mute/control packets, audio stream IDs, and sink capability propagation.

The file also cross-relates to generated enum headers such as `soc24_enum.h`, which provide named values for some audio fields. The shift/mask header supplies layout; enum headers supply semantic values.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A single stale mask or shift can silently corrupt MMIO programming and affect display audio, power management, diagnostics, or legacy VGA compatibility.
- This chunk starts and ends mid-context. DCHVM `CTRL0`/`CTRL1` and the opening of `DCHVM_CLK_CTRL` are in the previous chunk, while the rest of endpoint 1 is in the next chunk. Whole-file conclusions must reconcile adjacent chunks.
- Repeated audio instances invite copy/paste or generator bugs. `AZF0STREAM0` through `AZF0STREAM15` and endpoint 0/1 mirrored fields should remain structurally consistent except where the hardware spec intentionally differs.
- Interrupt/status fields whose names include `FLAG`, `MASK`, `TYPE`, `ACK`, or `RESPONSE` are sensitive to polarity and write semantics. The header cannot express access type; call sites must still follow hardware programming guidance.
- VGA compatibility fields are easy to dismiss as legacy, but incorrect definitions can break early console, VGA handoff, emulator paths, or firmware assumptions.
- Full-width masks such as CRC result, sink-description, LPIB, GTC delta, and descriptor data fields must remain `0xFFFFFFFFL`; narrowing them would truncate diagnostic or capability payloads.
- Audio descriptor/channel allocation fields cross software boundaries: EDID-derived audio information, ALSA/HD-audio behavior, and display link programming all depend on consistent interpretation of channel count, sample rate, bit depth, downmix, HBR, and speaker allocation fields.

## Test Signals

Useful validation signals for changes touching this range include:

- Build coverage for DCN 3.1.6 display code so all generated macro references used by `dmub_dcn316.c`, `dcn316_resource.c`, DCHVM tables, and DCE audio tables compile.
- Register-table sanity checks that compare generated offsets, masks, and shifts against the authoritative ASIC XML/spec output for DCN 3.1.6.
- Display audio smoke tests over HDMI and DisplayPort: endpoint discovery, audio device enumeration, PCM playback at common sample rates and bit depths, multichannel channel allocation, HBR/non-PCM paths, mute/disable/re-enable, and hotplug while audio is active.
- Audio capability checks against EDID: descriptor count, supported frequencies, maximum channel count, speaker allocation, sink description/manufacturer/product/port ID, and pin default configuration.
- DCHVM/host-VM tests on systems using GPUVM retention and RIOMMU prefetch: successful display bring-up, no timeout waiting for `HOSTVM_PREFETCH_DONE`, stable power-gating transitions, and no display memory fault regressions.
- Perfmon/debug validation: counters start/stop, per-clock counter-off bits behave as expected, selected event fields produce nonzero counts under known workloads, and high/low counter reads compose correctly.
- VGA fallback checks: firmware console handoff, simple framebuffer/VGA text compatibility where applicable, and no regressions in low-resolution boot or recovery modes.
- Interrupt/status testing for endpoint 0 audio enabled, disabled, and format-changed events, including mask/type decoding and acknowledgement behavior.

### subset-b-001920: lines 56953-59328

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 56953-59328

## Scope

This chunk is generated AMD DCN 3.1.6 register field metadata. It contains C preprocessor constants only: paired `__SHIFT` and `_MASK` macros for Azalia/HDA display-audio codec endpoint indexed registers. There are no functions, structs, enums, branches, loops, allocations, includes, or software-owned variables in this range.

The reviewed span contains 2,046 `#define` entries: 1,041 shift definitions and 1,005 mask definitions. The mismatch is from chunk boundaries. The range begins after the first endpoint-1 `ACP_DATA` masks and starts at `ACP_TYPE_DEPENDENT_BYTE1__SHIFT`, then continues through endpoint-1 descriptor and pin-control status fields. It covers complete output endpoint blocks 2, 3, and 4. It then covers the beginning and most of output endpoint 5 through the first mask in `AZF0ENDPOINT5_AZALIA_F0_CODEC_PIN_CONTROL_SINK_INFO4`; the remaining sink-info masks and later endpoint-5 fields are in the next chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU Display Core hardware metadata, not distributed filesystem code.

## Purpose

The header supplies DCN 3.1.6 bit layouts for Azalia F0 display-audio codec endpoint registers. The companion `dcn_3_1_6_offset.h` header supplies the matching indexed register numbers and endpoint index/data apertures, for example `regAZF0ENDPOINT2_AZALIA_F0_CODEC_ENDPOINT_INDEX`, `regAZF0ENDPOINT2_AZALIA_F0_CODEC_ENDPOINT_DATA`, and `ixAZF0ENDPOINT2_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0`. This shift/mask file supplies the field positions used by AMD display register helpers to pack writes and decode readbacks.

The hardware surface in this chunk is the repeated output endpoint namespace for HDMI/DisplayPort audio. These endpoint registers represent HDA/Azalia converter and pin widgets attached to display outputs. Runtime display-audio code can program stream format, stream/channel IDs, digital audio status, supported formats, sink ELD data, HBR support, multichannel routing, unsolicited responses, LPIB snapshots, and audio status interrupts without hard-coding numeric bit positions.

## Important Definitions

The exported API is the generated macro naming convention:

- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` gives the field low bit.
- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>_MASK` gives the raw 32-bit field mask.
- `//AZF0ENDPOINT...` comments group field macros by indexed Azalia register.
- `// addressBlock: azf0endpoint<n>_endpointind` marks the repeated endpoint register block.

Endpoint 1 coverage starts mid-pin-control block and includes:

- `CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`: per-audio-format descriptor fields. Descriptor 0 has max channels, supported frequencies, descriptor byte 2, and stereo supported frequencies; descriptors 1-13 have max channels, supported frequencies, and descriptor byte 2.
- `CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`: enable, mute, and channel-ID fields for channel pairs or single-channel mappings across channels 0-7.
- `RESPONSE_LIPSYNC`, `RESPONSE_HBR`, and `SINK_INFO0` through `SINK_INFO8`: audio/video latency, HBR capability/enable, manufacturer/product ID, port ID, and sink description/latency bytes.
- `HOT_PLUG_CONTROL`, `UNSOLICITED_RESPONSE_FORCE`, `RESPONSE_CONFIGURATION_DEFAULT`, `MULTICHANNEL_MODE`, channel-status override registers `CODEC_CS_OVERRIDE_0` through `_8`, `ASSOCIATION_INFO`, `DIGITAL_OUTPUT_STATUS`, `LPIB` snapshot/readback, coding type, format-changed, wireless-display identification, remote keepalive, audio-enable status, and audio enabled/disabled/format-changed interrupt status fields.

Endpoints 2, 3, and 4 are complete repeated output endpoint blocks. Each includes:

- `CODEC_CONVERTER_PIN_DEBUG`: a generated debug field.
- `CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: converter widget properties including channel capability, input/output amplifier presence, amplifier/format override support, stripe support, processing-widget support, unsolicited-response capability, connection-list, digital, power-control, left/right swap, delay, and widget type.
- `CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT`: number of channels, bits per sample, sample base divisor, sample base multiple, base rate, and stream type.
- `CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID`: converter channel ID and stream ID.
- `CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER`: digital audio enable and IEC 60958-style status/control bits such as validity, VCFG, pre-emphasis, copyright, non-audio, professional mode, level, category code, and keepalive.
- `CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` and `PARAMETER_SUPPORTED_SIZE_RATES`: supported stream formats, audio rate capabilities, and audio bit capabilities.
- `CODEC_CONVERTER_STRIPE_CONTROL`, `CONTROL_RAMP_RATE`, `CONTROL_GTC_EMBEDDING`, `CONTROL_GTC_OFFSET_DEBUG`, and `GTC_COUNTER_DELTA*`: converter striping, ramp, presentation-time/GTC embedding, offset debug, and min/current/max GTC delta readback fields.
- `CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `CODEC_PIN_PARAMETER_CAPABILITIES`: pin widget capability fields such as impedance sense, trigger requirement, jack detection, headphone drive, output/input capability, balanced pins, HDMI, DP, VREF, and EAPD.
- `CODEC_PIN_CONTROL_UNSOLICITED_RESPONSE`, `RESPONSE_PIN_SENSE`, `WIDGET_CONTROL`, `CHANNEL_SPEAKER`, `ACP_DATA`, `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, multichannel controls, lipsync, HBR, sink info, hotplug, default configuration, channel-status override, LPIB, format-change, remote keepalive, audio enable status, and audio interrupt status fields.

Endpoint 5 coverage starts at its address block and continues through `CODEC_PIN_CONTROL_SINK_INFO4`. It has the same converter and pin-control structure as endpoints 2-4 up to the partial sink-info boundary.

## APIs, Types, And Functions

There are no C functions or types declared by this chunk. The important interface is the macro namespace itself. Callers normally consume these symbols through AMD Display Core register helper macros and generated field tables rather than using the numeric values directly.

Related semantic enum names live outside this chunk, for example in `include/soc24_enum.h`, which defines values for fields such as `AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_MODE_MULTICHANNEL_MODE`, `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_HBR_HBR_CAPABLE`, and several audio-widget or pin-capability booleans. Older DCE audio programming code uses the same descriptor field shape when it maps EDID SAD entries to `AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0` fields and writes endpoint registers via audio endpoint helpers.

## Control Flow

This header has no executable control flow. Runtime sequencing is supplied by AMDGPU/DC code that includes `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h`, builds register/field tables, then uses MMIO or indexed-register helpers to read, update, or acknowledge fields.

The implied control flow for consumers is:

1. Select the output audio endpoint for a display pipe or connector.
2. Use the companion offset header to address the endpoint index/data aperture and the specific `ixAZF0ENDPOINT<n>_*` register.
3. Use these shift/mask macros to compose a read-modify-write, status read, or interrupt acknowledge operation.
4. Let hardware latch converter format, stream ID, sink data, channel mapping, hotplug/audio enable, or interrupt state according to the Azalia/HDA register protocol.

The macros do not encode HDA verb ordering, stream disable/enable sequencing, ELD update timing, hotplug timing, write-one-to-clear behavior, or read-only versus writable status. Functional code and hardware documentation must supply those rules.

## State And Persistence Behavior

This chunk persists no software state. It describes hardware state held in DCN 3.1.6 display-audio endpoint registers.

Configuration-like fields include converter format, channel/stream ID, digital converter control, supported format/rate advertisement, stripe and GTC embedding control, pin output enable, speaker and channel allocation, ACP packet data, audio descriptors, multichannel enable/mute/channel mapping, HBR enable, hotplug audio enable, unsolicited-response enable/tag, default pin configuration, channel-status override bytes, wireless display identification, and remote keepalive.

Readback/status fields include converter and pin capabilities, stream format support, pin sense/impedance, sink information/ELD bytes, lipsync latency, HBR capability, digital output status, LPIB and timer snapshots, format-changed status, audio enabled state, and audio enabled/disabled/format-changed interrupt state.

Several fields are side-effecting or sticky in typical hardware use: interrupt acknowledge bits, interrupt masks and polarities, forced unsolicited-response trigger, LPIB snapshot lock, GTC delta clear, audio hotplug enable, audio keepalive, and format-change/audio-enable status. The generated masks do not mark those semantics; they only identify the bit positions.

## Dependencies And Integration Points

This chunk must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`. The offset header defines the endpoint index/data apertures and indexed register IDs, while this file defines bit layouts. A missing macro name usually fails compilation; a wrong numeric mask or shift can compile and silently program or decode the wrong hardware bits.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`, which includes the DCN316 offset and shift/mask headers for DMUB register metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes the same generated headers while constructing DCN316 display resources.

Functional integration is mostly indirect through Display Core audio, stream encoder, resource, IRQ, and DMUB register tables. HDMI/DP audio paths use these endpoint fields to populate monitor audio capabilities from EDID/ELD/SAD data, select stream IDs and formats, enable or disable audio on hotplug, route multichannel audio, enable HBR or encoded audio, service audio format-change and audio enable/disable interrupts, and expose link-position or timing readbacks such as LPIB/GTC information.

## Risks And Edge Cases

- This is generated hardware metadata. Manual edits risk divergence from the authoritative DCN 3.1.6 register database and from sibling offset/default/enum headers.
- The chunk begins and ends inside register groups. Endpoint 1 `ACP_DATA` starts before this range, and endpoint 5 `SINK_INFO4` continues after line 59328. Whole-file conclusions must merge adjacent chunks.
- Endpoint blocks are highly repetitive. A generator or copy error in only one endpoint can compile but fail only on connectors routed through that endpoint.
- Output endpoint names are instance-specific. Accidentally using `AZF0ENDPOINT3_*` masks for endpoint 4, or using generic/non-DCN masks from an older ASIC generation, can target valid-looking but wrong hardware fields.
- Dense channel-mapping registers pack enable, mute, and channel ID fields into adjacent nibbles and bytes. Wrong shifts can cause muted, swapped, or missing channels.
- Descriptor and sink-info fields are protocol-facing. Bad masks can advertise the wrong sample rates, channel count, speaker allocation, HBR capability, HDMI/DP connection type, sink identity, or latency to higher-level audio logic.
- Interrupt fields combine status, mask, ack, and polarity concepts. Treating acknowledge bits like persistent state can clear events unexpectedly; failing to preserve mask or polarity bits can break audio hotplug or format-change notification.
- Some capability and status fields are likely read-only or hardware-owned. The presence of a mask does not imply a caller should write the field.

## Test Signals

Useful validation signals for this chunk are mostly build, generation, and hardware integration checks:

- Compile AMDGPU Display Core with DCN316 enabled, including DMUB and DCN316 resource paths, to catch missing or malformed macro names.
- Regenerate or mechanically compare `dcn_3_1_6_sh_mask.h` against the authoritative DCN 3.1.6 register database and verify consistency with `dcn_3_1_6_offset.h`.
- Check paired `__SHIFT` and `_MASK` definitions for complete endpoint 2-4 register groups, while allowing known boundary exceptions at endpoint 1 start and endpoint 5 end.
- Preprocess representative DC register field-table macros to confirm token pasting resolves to the intended `AZF0ENDPOINT<n>` symbols for DCN316.
- Run HDMI/DisplayPort audio validation on DCN316 hardware for endpoints routed through output endpoints 1-5: hotplug, modeset, audio enable/disable, PCM playback, sample-rate changes, multichannel playback, channel allocation, encoded/HBR audio where supported, and suspend/resume.
- Validate ELD/SAD-derived sink data by comparing programmed audio descriptors, speaker allocation, latency, manufacturer/product IDs, port IDs, HBR capability, and sink-description bytes against known-good EDID/ELD data.
- Exercise audio enabled, audio disabled, format-changed, and unsolicited-response interrupt paths and verify status, mask, polarity, and ack bits behave as expected.
- Use register dumps around audio setup to confirm read-modify-write operations affect only intended masked bits in dense registers such as multichannel enable, channel-status override, hotplug control, and interrupt status/control.

## Cross-Chunk Notes

The previous chunk owns the beginning of endpoint 1, including the rest of `CODEC_PIN_CONTROL_ACP_DATA`. The next chunk owns the rest of endpoint 5 after `SINK_INFO4`, including later sink-info, hotplug, channel-status override, LPIB, remote keepalive, and audio interrupt fields if the generated layout continues like endpoints 2-4. The final per-file research document should reconcile these boundaries before presenting complete endpoint coverage for DCN 3.1.6.

### subset-b-001921: lines 59329-61649

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 59329-61649

## Scope

This chunk is a generated AMD DCN 3.1.6 register shift/mask header slice for Azalia/HDA audio endpoint and input-endpoint indirect registers. It contains no executable code, functions, structs, or runtime allocation logic. Its public surface is a large set of preprocessor constants named as:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

The slice starts inside `AZF0ENDPOINT5_AZALIA_F0_CODEC_PIN_CONTROL_SINK_INFO4`, completes the tail of output endpoint 5, covers complete output endpoint 6 and output endpoint 7 Azalia register families, then covers input endpoint 0, input endpoint 1, input endpoint 2, and most of input endpoint 3. The next chunk begins at `azf0inputendpoint4_inputendpointind`.

## Purpose

The header maps hardware register bit layouts into C preprocessor constants used by DCN 3.1.6 display/audio code. Consumers pair these field masks and shifts with matching offset/index definitions from `dcn_3_1_6_offset.h` and the display driver's register helper macros. The intended use is field extraction and field construction for memory-mapped or indirect Azalia codec endpoint registers.

The endpoint blocks describe HDMI/DisplayPort audio codec state exposed through GPU display hardware:

- Output endpoints `AZF0ENDPOINT5`, `AZF0ENDPOINT6`, and `AZF0ENDPOINT7` model digital audio converter/pin widgets, sink metadata, ELD-like descriptor fields, stream/channel routing, IEC 60958 channel-status overrides, hot-plug/audio enable state, and interrupt/status bits.
- Input endpoints `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT3` model input converter and input pin widgets, including stream format, channel/stream ID, input pin sense, multichannel enables, HBR support, input activity, LPIB snapshots, and audio infoframe fields.

## Important Definitions

The main macro families in this chunk are:

- `AZF0ENDPOINT5_AZALIA_F0_CODEC_PIN_CONTROL_*`: tail of endpoint 5 pin-control metadata and status. The chunk includes sink description bytes 4-17, hot-plug control, forced unsolicited response payload, default pin configuration, multichannel enable mode, IEC 60958 channel-status override registers 0-8, association info, output-active status, LPIB snapshot registers, coding type, format-change status, wireless display ID, remote keepalive, and audio enable/disable/format interrupt status.
- `AZF0ENDPOINT6_AZALIA_F0_CODEC_CONVERTER_*` and `AZF0ENDPOINT7_AZALIA_F0_CODEC_CONVERTER_*`: output converter fields for audio widget capabilities, converter format, channel/stream ID, digital converter flags, supported stream formats/rates, stripe control, ramp rate, GTC presentation-time embedding, and GTC delta diagnostics.
- `AZF0ENDPOINT6_AZALIA_F0_CODEC_PIN_*` and `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_*`: output pin fields for widget capabilities, pin capabilities, unsolicited response, pin sense, output widget enable, channel/speaker allocation, ACP packet data, audio descriptors 0-13, multichannel controls, lipsync, HBR, sink information, hot-plug control, configuration default, channel-status overrides, output status, LPIB, coding type, format change, wireless display, remote keepalive, and audio enable/disable/format interrupt state.
- `AZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_*` through `AZF0INPUTENDPOINT3_AZALIA_F0_CODEC_INPUT_*`: input converter and input pin fields for input debug, widget capabilities, converter format, channel/stream ID, digital converter flags, supported formats/rates, input pin capabilities, unsolicited response, input pin sense with presence detect, input widget enable, multichannel controls 0-7, HBR, channel allocation, hot-plug/audio-enabled state, forced unsolicited response, default config, LPIB snapshots, input activity/status-control, and audio infoframe fields.

Repeated field patterns are important because most endpoints share identical bit positions:

- Audio widget capability bits use low single-bit flags (`INPUT_AMPLIFIER_PRESENT`, `OUTPUT_AMPLIFIER_PRESENT`, `FORMAT_OVERRIDE`, `DIGITAL`, `POWER_CONTROL`, `LR_SWAP`) plus delay and type fields in the upper halfword.
- Converter format uses `NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, sample base divisor/multiple/rate, and stream type packed in the low 16 bits.
- Digital converter control uses IEC 60958-style flags: `DIGEN`, validity, `VCFG`, pre-emphasis, copyright, non-audio, professional, level, category code, and keepalive.
- Pin speaker/channel allocation uses speaker allocation, channel allocation, HDMI/DP connection bits, extra connection info, LFE playback level, level shift, and down-mix inhibit.
- Multichannel controls pack enable, mute, and channel ID fields into repeated 8-bit lanes.
- Status/interrupt registers expose flag, mask, and type bits for audio enabled, disabled, and format changed events.

## Control Flow

There is no local control flow in this header chunk. Runtime behavior is indirect:

1. DCN 3.1.6 display code includes `dcn_3_1_6_offset.h` and this `dcn_3_1_6_sh_mask.h`.
2. Register helper macros such as `FD_MASK`, `FD_SHIFT`, `SF`, `HWS_SF`, and related resource-table initializers expand these constants into per-block register/mask/shift tables.
3. Higher-level audio, DIO, AFMT, APG, VPG, and DMUB paths use those tables to read, mask, shift, and write hardware fields.

`dcn316_resource.c` includes this header and uses Azalia endpoint index/data fields in audio register lists. `dmub_dcn316.c` also includes the same offset and mask headers to populate DMUB service register tables through mask/shift expansion.

## State And Persistence

The macros themselves are compile-time constants and persist only in the built kernel object code as immediate values or initializer data. They do not store software state.

The hardware fields they describe are stateful device registers. Relevant state categories in this slice include:

- Link/sink capability state: sink manufacturer/product IDs, sink description bytes, audio descriptors, speaker/channel allocation, HBR capability, DP/HDMI connection indicators, supported rates/formats, and widget capabilities.
- Stream programming state: converter format, stream ID, channel ID, digital converter flags, multichannel enable/mute/channel routing, channel-status overrides, coding type, and keepalive.
- Event/status state: hot-plug audio enable, output active, input activity, presence detect, format changed, forced unsolicited responses, and enable/disable/format interrupt flags/masks/types.
- Timing/debug state: LPIB snapshots, cyclic buffer wrap count, LPIB timer snapshot, GTC embedding controls, and GTC counter delta/min/max diagnostics.

Persistence across suspend/resume, hotplug, modeset, or audio stream teardown depends on the surrounding AMDGPU display/audio code reprogramming the corresponding hardware registers. This header only defines bit positions; it does not preserve or restore register contents.

## Dependencies

This chunk depends on generated register naming consistency across AMD's ASIC register headers:

- Matching register offsets and indirect indices in `dcn_3_1_6_offset.h`.
- Register helper macros in AMD display code that expect the `REG__FIELD__SHIFT` and `REG__FIELD_MASK` naming scheme.
- DCN 3.1.6 resource and DMUB code that include these generated headers.
- The Azalia/HDA hardware programming model, where endpoint index/data registers select codec node registers and fields are packed into 32-bit register values.

The source tree also contains analogous definitions for other DCN/DCE generations. Those parallel headers are useful for diff-based validation, but this chunk is authoritative for DCN 3.1.6.

## Integration Points

Key integration points are:

- `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`: includes this header and uses its masks/shifts in DCN 3.1.6 resource construction and hardware sequencer field tables. Audio-related register lists reference Azalia endpoint index/data registers and global Azalia clock/audio DTO fields.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`: includes this header to build DMUB service mask/shift tables through `FD_MASK` and `FD_SHIFT`.
- DCE/DCN audio support such as `dce_audio`, AFMT, APG, VPG, DIO stream encoders, and HPO stream paths: these components consume the generated field tables rather than directly depending on individual macros from this chunk in most cases.
- Hardware validation and generated-header maintenance: ASIC register database updates must keep `_SHIFT`, `_MASK`, offset, and indexed address-block definitions synchronized.

## Risks

- Generated-header drift: a wrong mask or shift compiles cleanly but can program the wrong hardware bits, leading to broken HDMI/DP audio, bad channel routing, missing HBR, incorrect ELD/sink data, or missed unsolicited responses.
- Boundary risk: this chunk begins mid-register for endpoint 5 and ends before input endpoint 4. Merge/reconciliation must combine adjacent chunks to avoid treating endpoint 5 or input endpoint 3/4 coverage as complete per-file analysis.
- Repetition risk: endpoint 6 and endpoint 7 are near-identical. Copy-generation mistakes can leave one endpoint with mismatched field names, missing masks, or a stale bit position while neighboring endpoints look correct.
- Interrupt/status risk: flag/mask/type fields for audio enabled/disabled/format changed use compact bit positions. Incorrect masks can invert interrupt enable behavior or hide format-change notifications.
- Indexed-register risk: Azalia endpoint blocks are accessed through endpoint index/data registers. A correct field mask is still unsafe if paired with the wrong `ix...` indirect index or endpoint instance.
- Capability reporting risk: sink info, audio descriptors, HBR capability, speaker allocation, and input infoframe fields may be surfaced up-stack. Bad field extraction can cause userspace-visible audio capability errors even when the link itself is otherwise functional.

## Test Signals

Useful validation signals for changes touching this header or its generator include:

- Build coverage for AMDGPU DCN 3.1.6 display code with warnings enabled, confirming all generated macro names referenced by resource/DMUB tables still resolve.
- Diff checks against the paired `dcn_3_1_6_offset.h` to ensure every `AZF0ENDPOINT6`, `AZF0ENDPOINT7`, and `AZF0INPUTENDPOINT0-3` register field has a matching register/index definition where applicable.
- Cross-generation diffing against nearby DCN headers for repeated Azalia endpoint layouts, while accounting for ASIC-specific differences.
- HDMI/DP audio smoke tests on DCN 3.1.6 hardware: hotplug audio detection, audio enable/disable transitions, PCM playback, multichannel routing, HBR/encoded playback if supported, suspend/resume with audio, and format changes during active playback.
- Register readback tests for representative fields: converter format packing, channel/stream ID, multichannel enables, audio descriptors, sink info bytes, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, `AUDIO_FORMAT_CHANGED_INT_STATUS`, input activity/status-control, and LPIB snapshots.
- DMUB initialization tests verifying mask/shift tables derived from `FD_MASK`/`FD_SHIFT` match expected DCN 3.1.6 register metadata.

### subset-b-001922: lines 61650-62727

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 61650-62727

## Purpose

This chunk is the end of the generated AMD DCN 3.1.6 shift/mask header. It contains no executable C logic; it publishes preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for Azalia F0 codec input endpoint registers. Consumers pair these constants with the matching DCN 3.1.6 offset header and AMD display register helpers to compose, update, or decode MMIO register fields.

The range starts mid-register in `AZF0INPUTENDPOINT3`, covering the remaining configuration-default masks plus the endpoint-3 LPIB, activity/status, and infoframe fields. It then defines complete repeated blocks for `AZF0INPUTENDPOINT4` through `AZF0INPUTENDPOINT7`, and ends the file with the final include-guard `#endif`. The chunk defines 962 preprocessor constants: 480 shift constants and 482 mask constants.

Although this source tree is rooted under `ceph-client`, this file is AMDGPU display hardware metadata, not distributed-filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, locks, allocation paths, includes, or direct register accesses in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the low bit index of a hardware field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for isolating or updating that field.
- `// addressBlock: azf0inputendpointN_inputendpointind`: generated grouping comments for indexed Azalia input endpoint instances.

The covered register groups are:

- `AZF0INPUTENDPOINT3_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`: the tail masks for `MISC`, `COLOR`, `CONNECTION_TYPE`, `DEFAULT_DEVICE`, `LOCATION`, and `PORT_CONNECTIVITY`.
- `AZF0INPUTENDPOINT3` runtime input-pin controls: `LPIB_SNAPSHOT_CONTROL`, `LPIB`, `LPIB_TIMER_SNAPSHOT`, `INPUT_STATUS_CONTROL`, and `INFOFRAME`.
- `AZF0INPUTENDPOINT4` through `AZF0INPUTENDPOINT7`: complete input endpoint blocks, each with converter debug, converter audio-widget capabilities, converter format, channel/stream ID, digital-converter control, supported stream formats/rates, pin widget capabilities, pin capabilities, unsolicited response control, input-pin sense, widget input enable, multichannel controls, HBR, channel allocation, hot-plug/audio control, forced unsolicited response, default configuration, LPIB snapshot/value/timer, input status, and infoframe fields.

Representative fields include:

- Audio capability fields: channel capability, amplifier presence, format override, stripe, processing widget, unsolicited response capability, connection list, digital, power control, LR swap, delay, and widget type.
- Converter programming fields: number of channels, bits per sample, sample base divisor/multiple/rate, stream type, channel ID, stream ID, digital enable, validity/configuration flags, pre-emphasis, copyright, non-audio, professional mode, category code, and keepalive.
- Pin capability and control fields: impedance sense, trigger required, jack detection, input/output capability, HDMI/DP flags, VREF, EAPD, input enable, HBR capability/enable, channel allocation, clock gating disable, clock-on state, and audio enabled.
- Multichannel routing fields: `MULTICHANNEL0` through `MULTICHANNEL7` enable, mute, and channel-ID fields split across `MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`.
- Event/status fields: unsolicited response tag/enable/force payload, input activity, channel layout, input-activity unsolicited-response enable, channel-layout/channel-status infoframe-change unsolicited-response enable, and infoframe channel count/allocation/byte 5/valid.
- Audio-position snapshot fields: LPIB snapshot lock, cyclic buffer wrap count, full-width LPIB value, and full-width LPIB timer snapshot.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h`, then uses token-pasting helper macros such as field/mask/shift table builders to bind symbolic register fields to per-ASIC register tables.

For the Azalia input endpoint fields represented here, the expected runtime sequence is outside the header:

1. DCN 3.1.6 display/audio code selects an Azalia endpoint register or indexed endpoint aperture.
2. The matching offset macro provides the register address or index/data aperture.
3. The shift/mask macro from this header isolates or updates a specific field.
4. Higher-level audio code sequences stream format, pin state, hotplug/audio enablement, infoframe programming, multichannel/HBR setup, LPIB snapshot reads, and unsolicited-response handling.

The generated constants do not encode ordering, access type, volatility, or side effects. Callers must still obey the hardware sequence for active display audio streams, hotplug changes, power-gating transitions, suspend/resume, reset, and snapshot locking.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to memory, disk, or firmware. It describes MMIO-backed GPU state in DCN 3.1.6 Azalia input endpoint hardware.

The represented hardware state includes:

- Static or advertised capabilities for input converter and pin widgets.
- Active converter state such as sample format, stream/channel ID, digital converter flags, and supported rate/size masks.
- Pin state for input enablement, HDMI/DP capability, jack/presence/impedance sense, HBR, multichannel routing, channel allocation, clock gating, audio enabled, and default configuration metadata.
- Event and status state for unsolicited responses, input activity, channel layout, infoframe changes, and infoframe validity.
- Position/timer observations through LPIB snapshot lock, cyclic-buffer wrap count, LPIB, and LPIB timer snapshot fields.

Persistence is hardware-defined. Programmed configuration usually lasts until stream reconfiguration, modeset, power gating, suspend/resume, or ASIC reset. Sense/status/unsolicited-response/LPIB fields may be read-only, sticky, latched, timing-sensitive, self-clearing, or write-one-to-clear depending on the register definition outside this generated mask file.

## Dependencies And Integration Points

This chunk must remain synchronized with the rest of the DCN 3.1.6 generated register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h` supplies the matching register offsets and base-index macros.
- DCN base segment definitions in DCN316 display code turn generated offsets into MMIO addresses.
- AMD display register helpers use token-pasted register and field names to retrieve masks and shifts.

Observed include sites for `dcn_3_1_6_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`, which builds the DCN316 DMUB register mask/shift tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which builds DCN316 resource objects and register tables, including DIO/audio-related structures.

Relevant runtime integration is with the shared AMD display audio path under `display/dc/dce/dce_audio.c` and `display/dc/dce/dce_audio.h`. That code programs Azalia codec endpoint index/data registers, hot-plug audio control, HBR, speaker/channel information, sink information, supported formats/rates, and default configuration. This chunk's `AZF0INPUTENDPOINT*` names describe the generated input-endpoint field geometry for endpoint instances 3 through 7; the standard audio code may reach related hardware through generic indexed endpoint access rather than spelling these generated macro names directly.

## Risks And Edge Cases

- Field drift is the main risk. These macros are untyped constants, so an incorrect bit position or mask can compile cleanly while programming or decoding the wrong hardware bits.
- The chunk starts in the middle of `AZF0INPUTENDPOINT3`. Adjacent chunk `subset-b-001921` is required for complete endpoint-3 analysis.
- The complete endpoint blocks for 4 through 7 are repetitive and instance-specific. A copy-generation error in one endpoint can affect only one physical/logical audio path, making failures connector- or routing-dependent.
- Audio format fields are user-visible. Bad masks for sample size/rate, stream type, channel count, stream ID, or channel ID can cause silence, distorted audio, wrong channel mapping, or failures limited to multichannel/HBR modes.
- Digital converter flags affect validity, non-audio/professional/copyright metadata, category code, and keepalive behavior. Misprogramming can break sink interpretation or audio continuity during blanking/idle periods.
- Hotplug, unsolicited response, input activity, and infoframe-change fields are event-sensitive. Incorrect masks can cause missed notifications, spurious events, stuck status, or resume-only audio failures.
- LPIB snapshot fields are timing-sensitive. Misinterpreting lock, wrap count, LPIB, or timer snapshot fields can produce wrong audio position accounting or races while a stream is active.
- The final `#endif` is in this range. Accidental edits at the tail can break the entire generated header's include guard and fail all DCN316 users.

## Test Signals

Useful validation should combine generated-header checks with display/audio behavior:

- Build AMDGPU display code with DCN316 enabled. Include or token-paste mismatches should surface in `dmub_dcn316.c`, `dcn316_resource.c`, or shared register-table helpers.
- Mechanically verify that every field in endpoint blocks 4 through 7 has the expected `__SHIFT`/`_MASK` pair where the generated schema requires both, and that full-register fields such as LPIB use `0xFFFFFFFFL` masks.
- Diff the endpoint 4 through 7 layouts against neighboring generated DCN headers or AMD's authoritative register database where compatibility is expected.
- Exercise HDMI/DP audio on DCN316 hardware across stereo, multichannel PCM, multiple sample rates and bit depths, HBR-capable formats, stream start/stop, plug/unplug, blanking, modeset, suspend, and resume.
- Watch for no-sound-on-one-endpoint bugs, channel swaps, incorrect channel allocation, hotplug notification storms, missed audio endpoint changes, stuck activity/status bits, invalid infoframe state, LPIB position anomalies, and audio regressions after resume.

## Cross-Chunk Notes

This is chunk 26 of 26 for `dcn_3_1_6_sh_mask.h`. Earlier chunks cover the beginning of the generated header and the earlier Azalia endpoint blocks. The final per-file report should merge this tail with `subset-b-001921` before making complete claims about `AZF0INPUTENDPOINT3`, and with all earlier chunks before summarizing the whole DCN 3.1.6 shift/mask namespace.
