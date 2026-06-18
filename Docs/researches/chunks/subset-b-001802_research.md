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
