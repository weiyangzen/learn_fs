# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 2453-4724

## Purpose

This chunk is generated AMDGPU DCN 3.0 register field metadata. It contains no executable C logic; its public surface is a large set of preprocessor constants that describe bit positions and masks for display-controller MMIO registers. Each field is represented by paired macros:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position.
- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.

The path is under a local `ceph-client` source mirror, but the content is AMD display-driver hardware metadata, not Ceph or distributed-filesystem code.

The range starts in the middle of the `DMCU_INTERRUPT_STATUS` field list and ends in the middle of `DISP_INTERRUPT_STATUS_CONTINUE21`. Within that span it covers DMCU/DMU interrupt status, host/uc enable masks, XIRQ/IRQ routing selectors, scratch and communication mailbox registers, DMCU perfmon and DPRX interrupt routing, continued DMCU interrupt banks for power-domain and DCIO DPCS events, DC GPU timer read/start-position registers, and the display interrupt status chain through continue bank 21.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or runtime storage objects in this range. The important API is the generated macro namespace consumed by AMD display register helpers such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_READ`, and `REG_WRITE`, together with the matching address macros from `dcn_3_0_0_offset.h`.

Major macro families in this chunk:

- `DMCU_INTERRUPT_STATUS`, `DMCU_INTERRUPT_STATUS_1`, `DMCU_INTERRUPT_STATUS_2`, and `DMCU_INTERRUPT_STATUS_CONTINUE`: sticky/ack-style DMCU interrupt status bits. These include ABM ready/backlight update events, microcontroller internal and register-read-timeout events, external software and SCP/MCP events, static-screen and vblank events, OTG range-timing updates, DCPG IHC domain power-up/power-down events for domains 0-21, and DCIO DPCS TXA-TXG interrupt bits.
- `DMCU_INTERRUPT_TO_HOST_EN_MASK`: host-visible enable bits for ABM0-ABM5 ready/backlight events plus selected SCP, UC internal, and UC register-read-timeout events.
- `DMCU_INTERRUPT_TO_UC_EN_MASK`, `_1`, `_2`, and `_CONTINUE`: routing enables for sending selected display events to the DMCU/DMU microcontroller, including ABM, static-screen, vblank, OTG range timing, domain power, DPRX, and DCIO DPCS events.
- `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL`, `_1`, `_CONTINUE`, and `_CONT2`: selectors that choose the interrupt line/type used when enabled events are routed to the microcontroller. Their bit layout mirrors the corresponding `*_TO_UC_EN_MASK*` banks.
- `DC_DMCU_SCRATCH`, `DMCU_INT_CNT`, and `DMCU_INT_CNT_CONT2` through `CONT5`: scratch data and per-ABM event counters, with 8-bit count fields for high-gain ready, local-slope ready, and backlight-update interrupts across ABM1-ABM5.
- `DMCU_FW_CHECKSUM_SMPL_BYTE_POS` and `DMCU_UC_CLK_GATING_CNTL`: firmware checksum sample-byte selectors and microcontroller IRAM/ERAM/RBBM read clock-gating controls.
- `MASTER_COMM_DATA_REG1-3`, `MASTER_COMM_CMD_REG`, `MASTER_COMM_CNTL_REG`, `SLAVE_COMM_DATA_REG1-3`, `SLAVE_COMM_CMD_REG`, and `SLAVE_COMM_CNTL_REG`: byte-granular communication/mailbox registers between host-side code and the display microcontroller, plus interrupt and in-progress bits.
- `DMCU_PERFMON_INTERRUPT_STATUS1-5`, `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK1-5`, and `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1-5`: status, clear, enable, and routing macros for perfmon counter interrupts from DMU, DIO, DCCG, HUBP0-7, HUBBUB, DPP0-7, writeback, MMHUBBUB, MPC, OPP, OPTC, HDA, and DSC0-5.
- `DMCU_DPRX_INTERRUPT_STATUS1`, `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1`, and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1`: DisplayPort receiver stream, PHY, AUX, I2C, CPU, timeout, training, symbol, disparity, alignment, deskew, and sideband packet interrupt fields for the DPRX path.
- `DC_GPU_TIMER_START_POSITION_V_UPDATE`, `DC_GPU_TIMER_START_POSITION_VSTARTUP`, `DC_GPU_TIMER_READ`, and `DC_GPU_TIMER_READ_CNTL`: per-display GPU timer start-position selectors for vupdate/vstartup/vsync-nominal timing and a 32-bit timer readout selector.
- `DISP_INTERRUPT_STATUS` through `DISP_INTERRUPT_STATUS_CONTINUE21`: the main display interrupt status chain. It covers OPTC underflows, OTG snapshot/trigger/vsync/set-vtotal/vertical/vupdate/vstartup/vready/static-screen events, DIGA-DIGH DisplayPort fast-training and stream-disable events, HPD/HPD RX, AUX software and link-service done events, DMCU/ABM events, DMCU perfmon/DPRX/DCPG/DCIO continued banks, CRTC force-count/snapshot2, audio endpoint format/enabled/disabled events, AZ perfmon interrupts, DPCS IHC errors, I2C DDC hardware-done/read-request events, and continuation-link bits that chain one status register to the next.

The repeated suffixes and numbers are hardware-bank selectors, not software arrays. Consumers normally bind these names into register descriptor tables and let common register helper macros perform bit extraction and insertion.

## Control Flow

This header chunk has no control flow. It is declarative hardware layout data.

Runtime use follows this pattern:

1. DCN 3.0/3.0.2 code includes `dcn_3_0_0_offset.h` for addresses and this `dcn_3_0_0_sh_mask.h` file for shifts/masks.
2. Register-table initializers expand field names with macros such as `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)`.
3. Runtime code uses the resulting descriptors through `REG_GET`, `REG_UPDATE`, `REG_SET`, `REG_WRITE`, and related helpers to read, update, route, enable, clear, or acknowledge MMIO-backed display and DMCU state.
4. Interrupt code or firmware-facing paths read status banks, follow `*_CONTINUE*` chain bits, map asserted fields to IV source IDs, and clear or route events according to the relevant enable and XIRQ/IRQ selector masks.
5. DMUB/DMCU communication and diagnostics paths use the communication, scratch, counter, timer, and perfmon fields to exchange messages, profile display blocks, timestamp display events, or observe interrupt behavior.

The macros do not encode sequencing. Correct behavior depends on the caller knowing which registers are read-only status, writable control, write-one-to-clear status, sticky interrupt status, or self-clearing request bits.

## State And Persistence Behavior

The file stores no software state and persists nothing. It describes MMIO-backed GPU display hardware state.

The represented hardware state includes:

- DMCU/DMU interrupt state: occurred/clear bits for ABM, vblank, static-screen, OTG range-timing, power-domain, DPRX, DPCS, UC internal, SCP/MCP, and software events.
- Interrupt routing and masking state: host enable masks, microcontroller enable masks, and XIRQ/IRQ selector bits for the same interrupt families.
- Firmware and communication state: scratch register contents, byte-packed master/slave command and data registers, host/microcontroller interrupt bits, and message-in-progress indication.
- Diagnostics and counters: ABM event counters, perfmon counter interrupt status/clear bits, perfmon routing enables/selectors, DPRX status, and GPU timer read/start-position controls.
- Display interrupt aggregation state: chained display interrupt status banks for OPTC, OTG, DIG, HPD, AUX, I2C, audio, DPCS, DCPG, DMCU, ABM, and perfmon signals.
- Clock/power-adjacent control state: DMCU UC clock-gating read delays/enables and DCPG IHC power up/down events for many domains.

Persistence is defined by the hardware, not this header. Configuration fields such as enable masks, routing selectors, communication bytes, scratch data, and clock-gating controls normally remain until reprogrammed, reset, or lost through power gating. Event/status fields with names such as `*_OCCURRED`, `*_CLEAR`, `*_INT`, `*_STATUS`, `*_DONE`, `*_TIMEOUT`, and `*_CONTINUE` may be sticky, write-one-to-clear, read-only, edge-sensitive, or continuation indicators. Treating them as ordinary writable storage is risky without the corresponding register specification or caller-side helper contract.

## Dependencies And Integration Points

This chunk depends on the matching generated address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`

Direct include points found in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

Those files include the DCN 3.0 offset and mask headers and build `dmub_srv_common_regs` tables by expanding `DMUB_COMMON_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_COMMON_FIELDS()` through `REG_OFFSET`, `FD_MASK`, and `FD_SHIFT`. The chunk's DMCU/DMUB-adjacent communication and interrupt metadata is therefore part of the generated register contract available to DMUB service code, even when a given source file only references it through macro expansion rather than spelling every field name directly.

Related source-ID integration appears in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, which documents several `DISP_INTERRUPT_STATUS_CONTINUE20` OTG static-screen, vupdate, GSL vsync-gap, vstartup, and vready fields as display interrupt source IDs. That header is not the register mask consumer itself, but it shows the semantic mapping between status-bank bits and the interrupt vectors surfaced to AMDGPU display IRQ handling.

The main consumers are hardware register helpers and firmware/display infrastructure rather than hand-written code in this header. The generated names must stay synchronized with DCN 3.0 register addresses, ASIC IP offsets such as `sienna_cichlid_ip_offset.h` and `dimgrey_cavefish_ip_offset.h`, DMUB register tables, display IRQ source tables, and firmware protocols that depend on DMCU/DMUB mailbox and interrupt behavior.

## Risks And Edge Cases

- These macros are a hardware ABI. Wrong shifts or masks usually compile successfully but read or write the wrong bit, causing missed interrupts, stale clears, interrupt storms, broken firmware communication, incorrect timer reads, bad perfmon routing, display underflow reporting failures, or pipe-specific display event loss.
- The range begins in the middle of `DMCU_INTERRUPT_STATUS` and ends before the complete `DISP_INTERRUPT_STATUS_CONTINUE21`/later continuation chain. Whole-file conclusions require adjacent chunks.
- Many status and clear fields deliberately share the same bit position and mask. Code that treats `*_CLEAR` as an independent field from `*_OCCURRED` can clear pending events unintentionally or fail to acknowledge them.
- Enable-mask and XIRQ/IRQ selector banks mirror status banks but are not interchangeable. Copying a field from `*_TO_UC_EN_MASK*` to `*_XIRQ_IRQ_SEL*`, or from the wrong continued bank, can silently route the wrong event.
- Chained display status banks rely on continuation bits such as `DISP_INTERRUPT_STATUS_CONTINUE*`. A wrong continuation mask can hide all later status registers or make software scan nonexistent banks.
- Repeated instance patterns create drift risk. ABM1-ABM5 counters, OTG1-OTG6 timing events, DCPG domain 0-21 power events, DPCS TXA-TXG bits, audio endpoint 0-7 bits, and DDC1-DDC6 fields are easy to misalign by one bit or one bank.
- Mailbox registers are byte-packed. Full-register writes or wrong byte masks can corrupt adjacent command/data bytes and desynchronize host-to-firmware or firmware-to-host messages.
- Interrupt status registers may be side-effect-sensitive. Read/modify/write sequences on write-one-to-clear fields can clear unrelated pending interrupts if the caller writes back a stale full-register value.
- Timer selector fields are shared packed controls. Wrong masks for `DC_GPU_TIMER_READ_CNTL` or start-position fields can return misleading timestamps and break diagnostics that depend on vupdate, vstartup, or vsync-nominal timing.
- Some field names include historical or generated spelling quirks such as `OCCURED` and `REUEST`. Renaming them for spelling cleanup would break macro consumers.

## Test Signals

Useful validation is compile-time plus hardware or simulator behavior:

- Build AMDGPU display and DMUB sources that include `dcn_3_0_0_sh_mask.h`; missing or renamed macros should fail in register table expansion through `FD_MASK`/`FD_SHIFT`.
- Diff this generated chunk against AMD's DCN 3.0 register database and adjacent DCN family headers to catch bit drift in DMCU, DPRX, perfmon, timer, and display interrupt status banks.
- Exercise DCN 3.0 or DCN 3.0.2 hardware with multiple active displays so OTG1-OTG6, HPD/AUX, vblank/vupdate/vstartup/vready, static-screen, and display underflow status paths are covered.
- Validate interrupt acknowledge behavior for `*_OCCURRED`/`*_CLEAR` pairs by checking that events clear once, do not clear unrelated bits, and do not retrigger as storms after handling.
- Test DMUB/DMCU communication paths that use master/slave command and data registers, including message-in-progress handling, interrupt signaling, firmware load/boot interactions, and timeout recovery.
- Exercise ABM/backlight events across ABM instances and verify high-gain ready, local-slope ready, and backlight-update counters/status bits.
- Run perfmon diagnostics for HUBP, HUBBUB, DPP, WB, DCCG, MMHUBBUB, MPC, OPP, OPTC, HDA, and DSC counters; confirm counter interrupt status, clear, enable, and routing selector behavior.
- Exercise DisplayPort/AUX/DPRX-related events where supported: MSA receive, VBID stream status toggles, vertical interrupts, SDP receive, PHY error thresholds, training errors, AUX/I2C/CPU interrupts, and message timeouts.
- Check GPU timer reads against expected display timing at vupdate, vstartup, and vsync-nominal positions for all active pipes.
- Monitor kernel logs and display diagnostics for missed hotplug/AUX completion, page-flip or vblank timeouts, underflow reports, audio endpoint event loss, firmware mailbox stalls, DPCS errors, power-domain interrupt anomalies, and pipe-specific regressions.

## Cross-Chunk Notes

Previous chunks of `dcn_3_0_0_sh_mask.h` define the earlier DCN 3.0 register field namespace and the beginning of `DMCU_INTERRUPT_STATUS` before line 2453. Later chunks continue after `DISP_INTERRUPT_STATUS_CONTINUE21`, including the rest of the display interrupt continuation chain and additional generated DCN 3.0 register masks. The final per-file research document should merge those chunks before making complete claims about the entire header.
