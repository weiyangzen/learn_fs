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
