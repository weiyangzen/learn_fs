# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 34933-37347

## Scope

This chunk covers lines 34933-37347 of `dcn_2_0_0_sh_mask.h`, a generated AMD DCN 2.0 register shift/mask header. The slice contains 2,165 preprocessor definitions: 1,083 `__SHIFT` constants and 1,082 `__MASK` constants. It starts in the OPTC/OTG5 timing-generator block, crosses several display-controller address blocks, and ends in the beginning of DP AUX0 interrupt-control definitions.

The file does not define C functions or runtime data structures. Its "API" is the collection of macro names that other AMDGPU DC/DCN code uses to pack, unpack, read, write, and poll memory-mapped display hardware registers.

## Purpose

The macros map named hardware bitfields to stable bit positions and masks for DCN 2.0 display registers. Driver code can then use register helper macros, generated register tables, or direct `REG_SET`, `REG_UPDATE`, `REG_GET`, and equivalent accessors without hard-coding numeric bit layouts at call sites.

This chunk is especially tied to:

- OTG5 output timing generator state, synchronization, dynamic refresh, CRC, stereo/3D, global sync lock, update lock, and pipe-update status.
- OPTC miscellaneous controls for DWB source selection, GSL source selection, OPTC clocking, and ODM memory power.
- DC performance monitor instances 19 and 20.
- DIO I2C/DDC controller setup, transaction, status, and interrupt fields.
- DIO scratch, memory power, clock gate, soft reset, PSP/generic interrupt, and power-management fields.
- HPD0 through HPD5 hot-plug-detect status, interrupt, control, fast-training, and toggle-filter fields.
- The opening DP AUX0 control, software-control, arbitration, and interrupt-control fields.

## Important Macro Groups

### OTG5 timing and synchronization

The OTG5 section defines fields for core display timing:

- Horizontal and vertical timing: `OTG5_OTG_H_SYNC_A_CNTL`, `OTG5_OTG_H_TIMING_CNTL`, `OTG5_OTG_V_TOTAL`, `OTG5_OTG_V_TOTAL_MIN`, `OTG5_OTG_V_TOTAL_MAX`, `OTG5_OTG_V_TOTAL_MID`, `OTG5_OTG_V_BLANK_START_END`, `OTG5_OTG_V_SYNC_A`, and `OTG5_OTG_V_SYNC_A_CNTL`.
- Dynamic refresh / DRR support: `OTG5_OTG_V_TOTAL_CONTROL`, `OTG5_OTG_V_TOTAL_INT_STATUS`, `OTG5_OTG_DRR_CONTROL`, and range-timing update interrupt status.
- Trigger and force-count paths: `OTG5_OTG_TRIGA_CNTL`, `OTG5_OTG_TRIGB_CNTL`, their manual trigger registers, `OTG5_OTG_FORCE_COUNT_NOW_CNTL`, `OTG5_OTG_TRIG_MANUAL_CONTROL`, and `OTG5_OTG_MANUAL_FLOW_CONTROL`.
- Main OTG enable and blanking controls: `OTG5_OTG_CONTROL`, `OTG5_OTG_MASTER_EN`, `OTG5_OTG_BLANK_CONTROL`, `OTG5_OTG_PIPE_ABORT_CONTROL`, `OTG5_OTG_CLOCK_CONTROL`, and blank/black color registers.
- Readback and status: `OTG5_OTG_STATUS`, `OTG5_OTG_STATUS_POSITION`, frame/VF/HV count registers, pixel readback registers, interlace status, snapshot status/control/position/frame, and pipe update status.
- Interrupt scheduling: `OTG5_OTG_INTERRUPT_CONTROL`, vertical interrupt 0/1/2 position/control, `OTG5_OTG_GLOBAL_SYNC_STATUS`, and range timing interrupt status.
- Update-lock and double-buffering: `OTG5_OTG_UPDATE_LOCK`, `OTG5_OTG_DOUBLE_BUFFER_CONTROL`, `OTG5_OTG_MASTER_UPDATE_LOCK`, `OTG5_OTG_GLOBAL_CONTROL0` through `OTG5_OTG_GLOBAL_CONTROL3`, and `OTG5_OTG_VUPDATE_KEEPOUT`.
- Stereo, 3D, and global sync lock: `OTG5_OTG_STEREO_FORCE_NEXT_EYE`, `OTG5_OTG_STEREO_STATUS`, `OTG5_OTG_STEREO_CONTROL`, `OTG5_OTG_3D_STRUCTURE_CONTROL`, `OTG5_OTG_GSL_CONTROL`, `OTG5_OTG_GSL_VSYNC_GAP`, and GSL window X/Y registers.
- CRC and static-screen detection: `OTG5_OTG_CRC_CNTL`, `OTG5_OTG_CRC_CNTL2`, CRC window/data registers 0-3, CRC signature masks, and `OTG5_OTG_STATIC_SCREEN_CONTROL`.

The OTG5 block is a repeated timing-generator instance. The `5` suffix identifies the hardware instance; other chunks in the same header likely define equivalent OTG0-OTG4 and later OTG blocks.

### OPTC miscellaneous and ODM power

The `dce_dc_optc_optc_misc_dispdec` address block starts at line 35752. It defines:

- `DWB_SOURCE_SELECT` fields for selecting which OPTC feeds DWB0-DWB2.
- `GSL_SOURCE_SELECT` fields for GSL ready-source and timing-sync selection.
- `OPTC_CLOCK_CONTROL` fields for display clock gating and test-clock selection.
- `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL2`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS` fields for up to 12 ODM memory slices plus unassigned/vblank power modes.
- `OPTC_MISC_SPARE_REGISTER` as a full-width spare field.

These macros are integration points for display writeback, multi-pipe synchronization, and ODM memory power policy.

### DC perfmon instances 19 and 20

Two nearly identical DC performance monitor blocks appear:

- `DC_PERFMON19_*` under the OPTC perfmon address block.
- `DC_PERFMON20_*` under the DIO perfmon address block.

Each instance exposes performance counter select/mask controls, counter state selectors, run/stop control, report count, count-off interrupt enable/status/ack, 32-bit value readback split into low/high fields, and per-counter interrupt status/ack bits. Consumers can program counter sources, gate counting windows, read accumulated values, and service count-off interrupts.

### DIO I2C/DDC controller

The `dce_dc_dio_dout_i2c_dispdec` address block defines the display I2C/DDC controller interface:

- `DC_I2C_CONTROL` for software go, send-reset, sw status reset, transaction count, DDC selection, and shutdown.
- `DC_I2C_ARBITRATION` for software, DMCU, and hardware-request arbitration status/requests/done bits.
- `DC_I2C_INTERRUPT_CONTROL` for done, NACK, arbitration-done/lost, DDC1-6 HW-done, and DDCVGA HW-done interrupt/ack/mask/type fields.
- `DC_I2C_SW_STATUS` for DC I2C used-by-sw, software stop, NACK, timeout, abort, done, and byte-count status.
- Per-DDC hardware status registers for DDC1 through DDC6, each with used-by-HW, EDID detect, done, NACK, timeout, and abort fields.
- Per-DDC speed/setup registers for DDC1 through DDC6, including threshold, filter-during-stall, start/stop timing control, prescale, data/clock drive controls, reset length, EDID detect mode/enable, intra-byte delay, intra-transaction delay, and time limit.
- Four transaction descriptor registers `DC_I2C_TRANSACTION0` through `DC_I2C_TRANSACTION3`, each carrying read/write, stop-on-NACK, start, stop, and byte count fields.
- `DC_I2C_DATA` for indexed data access and `DC_I2C_EDID_DETECT_CTRL` for EDID detect timing/retry/reset behavior.
- `DC_I2C_READ_REQUEST_INTERRUPT` for DDC1-6 and DDCVGA read-request occurred/int/ack/mask fields plus global ack-enable and interrupt type.

This area is central to EDID reads, DDC transactions, display detection, and firmware/software arbitration over the I2C engine.

### DIO miscellaneous, clocks, reset, power, and interrupts

The `dce_dc_dio_dio_misc_dispdec` block defines:

- Eight full-width DIO scratch registers.
- `DCE_VCE_CONTROL` audio-stream select.
- `DIO_MEM_PWR_STATUS`, `DIO_MEM_PWR_STATUS1`, `DIO_MEM_PWR_CTRL`, `DIO_MEM_PWR_CTRL2`, and `DIO_MEM_PWR_CTRL3` for I2C, DP A-G, HDMI0-6, AFMT0-5, DPHY, and AUX memory/light-sleep force/disable/state fields.
- `DIO_CLK_CNTL`, `DIO_CLK_CNTL2`, and `DIO_CLK_CNTL3` for display/ref clock gating across DIO, DAC, DIG A-G, DP stream encoder, DP link encoder, PHY symclk, DP alt, AUX, and audio format blocks.
- `DIO_POWER_MANAGEMENT_CNTL` for global power-management enable.
- `DIG_SOFT_RESET` for DIG frontend, DP stream encoder, DP link encoder, AUX, FEC, PHY symclk, and related soft-reset bits across links.
- `DIO_HDMI_RXSTATUS_TIMER_CONTROL` for HDMI RX status timer interval and enable.
- PSP and generic DIO interrupt status/clear/message fields.

These fields are lower-level than the DC core timing fields; mistakes here can affect clock availability, PHY/link reset sequencing, AUX/I2C availability, and audio/link sideband behavior.

### HPD0-HPD5 hot plug detect

The chunk contains six repeated HPD blocks, `HPD0` through `HPD5`. Each block defines:

- `DC_HPD_INT_STATUS` fields for interrupt status, sense, acknowledge, polarity, and mask.
- `DC_HPD_INT_CONTROL` fields for interrupt acknowledge, polarity, mask, detection timer, and interrupt-detected flags.
- `DC_HPD_CONTROL` fields for enable, connection timer, and RX interrupt timer.
- `DC_HPD_FAST_TRAIN_CNTL` fields for min/max wait count, legacy fast train enable, and fast-train complete status.
- `DC_HPD_TOGGLE_FILT_CNTL` fields for toggle-filter timer control.

These macros support connector hotplug detection, DP fast-training coordination, and debounce/toggle filtering across multiple physical outputs.

### DP AUX0 opening block

The final address block begins `dce_dc_dio_dp_aux0_dispdec`. This chunk includes:

- `DP_AUX0_AUX_CONTROL` for AUX enable/reset/reset-done, low-speed read, update-disable, ignore-HPD-disconnect, mode detect, HPD selection, impedance calibration request, test mode, deglitch enable, and spare bits.
- `DP_AUX0_AUX_SW_CONTROL` for software AUX go, low-speed read trigger, start delay, and software write-byte count.
- `DP_AUX0_AUX_ARB_CONTROL` for AUX arbitration priority/status, queued-go controls, software/DMCU register-use request and done bits. Some names intentionally alias the same bit positions, such as `AUX_SW_USE_AUX_REG_REQ` and `AUX_SW_PENDING_USE_AUX_REG_REQ`.
- `DP_AUX0_AUX_INTERRUPT_CONTROL` for software done, low-speed done, GTC sync lock done, and GTC sync error interrupt/ack/mask fields. The chunk ends while this register's masks are still being listed, so later DP AUX0 fields continue in the next chunk.

## Control Flow and Runtime Behavior

There is no executable control flow in this header. Runtime behavior emerges when DCN code includes this file and uses the macros with register accessor helpers:

1. A driver path selects a register address from the paired generated address header or a DCN register table.
2. The caller supplies field values by name.
3. Register helper macros combine `__SHIFT` and `__MASK` values to clear, insert, or extract the appropriate bits.
4. The resulting memory-mapped register read/write changes hardware state or observes status.

The same pattern applies to interrupt service paths and polling loops: status fields are extracted with masks/shifts, then clear/ack fields are written using the matching `*_ACK`, `*_CLEAR`, or event-clear masks.

The most important ordering constraints are not encoded here. They are imposed by hardware programming sequences in the consuming driver code, for example enabling clocks before touching dependent blocks, taking update locks before programming timing, clearing interrupts after observing status, and arbitrating AUX/I2C ownership before software transactions.

## State and Persistence Behavior

These macros describe persistent hardware register state, not software-owned persistence. Relevant state classes in this chunk include:

- Configuration state: timing totals, blank/sync positions, DDC speed/setup, HPD timers, clock gating, power modes, update-lock locations, CRC windows, perfmon counter sources, and AUX control options.
- Live status state: current OTG/blank/master enable status, frame/count positions, interlace/stereo state, update pending/taken bits, I2C/AUX done/error flags, HPD sense/status, memory power states, clock-on/busy state, and perfmon current values.
- Interrupt/event latch state: vertical interrupts, V_TOTAL/min events, global-sync events, range-timing update, I2C done/NACK/arbitration/read-request events, HPD events, PSP/generic DIO interrupts, and AUX done/GTC events.
- Clear/ack write state: many registers have paired `*_ACK`, `*_CLEAR`, or event-clear fields that are normally write-one-to-clear or write-controlled by hardware semantics.

The persistence boundary is the display hardware register file. Values may reset on GPU reset, block soft reset, power-gate transitions, suspend/resume, or display engine reinitialization. The header itself stores no state and cannot validate whether a field is safe to write at a given time.

## Dependencies and Integration Points

This header depends on the generated DCN 2.0 register naming scheme being consistent with:

- The paired address/offset header for DCN 2.0 registers.
- AMDGPU DC register accessor infrastructure that expects `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macro names.
- ASIC-specific register tables that bind generic DC resource code to concrete DCN 2.0 register instances.
- Hardware documentation or generator inputs that define bit positions, widths, reset behavior, and access semantics.

Integration surfaces visible from this chunk include:

- Timing-generator and OPTC code that programs OTG5 for mode set, vblank/vupdate, DRR, CRC capture, stereo/3D, master update lock, and global sync lock.
- Display writeback and ODM code that uses DWB source selection and ODM memory power fields.
- Power-management code that gates display clocks, controls memory light sleep, manages HDMI/DP/DIO power states, and sequences soft resets.
- Connector management code that uses HPD and DDC/I2C fields for EDID detection, hotplug interrupts, and DP link training readiness.
- DP AUX code that arbitrates AUX register access among software and DMCU paths and services AUX done/error interrupts.
- Performance/debug paths that program DC perfmon instances 19/20 and read counters.

## Risks and Edge Cases

- Generated macro drift is high risk. A single wrong shift or mask silently writes the wrong hardware bits, which can break modesets, clocks, hotplug, AUX/I2C transactions, or interrupt handling.
- Repeated-instance blocks invite copy/paste or generator-index mistakes. OTG5, HPD0-HPD5, DDC1-DDC6, and perfmon19/20 are structurally repetitive but instance-specific.
- Some fields intentionally alias the same bit, especially in AUX arbitration pending/request names. Consumers must understand read-versus-write semantics rather than assuming distinct storage.
- Interrupt fields often include status, ack/clear, mask, and type bits in one register. Incorrect helper use can clear pending events, leave interrupts masked, or acknowledge the wrong event.
- Clear/ack naming is inconsistent across blocks (`ACK`, `CLEAR`, `EVENT_CLEAR`, `*_INT_CLEAR`, `*_TAKEN_CLEAR`). Tests and reviews should verify hardware semantics in the consuming paths, not just macro spelling.
- Clock, reset, and memory-power fields can race with register access if callers do not first ensure the target block is powered and ungated.
- DDC/I2C and DP AUX arbitration fields coordinate software, hardware, and firmware/DMCU users. Incorrect ownership handling can deadlock transactions or corrupt EDID/AUX exchanges.
- Dynamic timing fields such as V_TOTAL min/max/mid, GSL, vupdate keepout, and master update locks are sensitive to vertical timing windows. Incorrect sequencing can cause flicker, underflow, missed vblank events, or synchronization loss.
- The chunk ends mid-DP-AUX0 address block. Any whole-file analysis must merge this with the following chunk before treating DP AUX0 coverage as complete.

## Test and Validation Signals

Useful validation for this chunk is mostly indirect because the header has no standalone executable behavior:

- Build coverage: compile AMDGPU/DCN code paths that include `dcn_2_0_0_sh_mask.h` and instantiate DCN 2.0 register tables.
- Macro consistency checks: generated tests or scripts can verify every `__SHIFT` has a corresponding `_MASK`, mask width matches shift/field width, and repeated instances have consistent layouts where expected.
- Modeset and vblank tests: exercise OTG5 timing, vblank/vupdate interrupt, DRR, update-lock, and CRC paths on DCN 2.0 hardware or emulation.
- Connector tests: hotplug/unplug cycles across HPD0-HPD5, EDID reads over DDC1-DDC6, DDC read-request interrupts, and DP AUX transactions.
- Power-management tests: suspend/resume, display off/on, clock-gating, light-sleep, memory power, and DIG/AUX soft-reset sequences.
- Perf/debug tests: configure perfmon19 and perfmon20 counters, read low/high values, and verify count-off interrupts and acknowledgements.
- Register trace comparison: compare MMIO writes generated by driver operations against known-good traces or hardware-programming guides for DCN 2.0.
- Static review signal: because this is generated hardware metadata, any hand edit in this chunk should be treated as suspicious unless backed by updated generator input or vendor register documentation.

## Open Questions for Merge Lane

- Confirm the previous chunk supplies the start of `OTG5_OTG_H_SYNC_A_CNTL`, since this chunk begins with that register's field definitions before the next comment marker.
- Merge with the next chunk for the remainder of DP AUX0 and subsequent AUX/register blocks before producing the final per-file document.
- Cross-check whether perfmon instance numbering 19/20 aligns with address block placement in the paired DCN 2.0 offset header.
