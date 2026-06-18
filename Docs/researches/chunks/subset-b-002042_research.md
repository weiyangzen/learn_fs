# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h - subset-b-002042

## Scope

- Chunk id: `subset-b-002042`
- Source lines: 37347-39686
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`
- Observed content: 2,340 source lines with 2,184 `#define` entries, 1,092 `__SHIFT` macros, 1,127 `_MASK` macros, and 109 register block comments.

This chunk is generated AMD DCN 3.2.1 register field metadata. It does not define executable C, functions, structs, enums, or persistent software objects. Its public interface is the preprocessor namespace of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants used by AMDGPU/DCN register helpers.

## Purpose

The chunk publishes bit layouts for a contiguous Display I/O area covering DisplayPort AUX channels, display DDC I2C registers, and DIO misc power/clock/reset/link controls:

- `DP_AUX0_*` through `DP_AUX4_*` define AUX channel control, software transaction, arbitration, interrupt, status, data FIFO/index, DPHY TX/RX timing/status, GTC sync, sync error, sync controller/status, and PHY wake fields for five DP AUX engines.
- `DC_I2C_*` defines shared DDC hardware I2C control, arbitration, interrupt, software status, per-DDC hardware status, speed/setup, transaction slots, data, EDID detect, and read-request interrupt fields.
- `DIO_SCRATCH0` through `DIO_SCRATCH7` provide full 32-bit scratch data field masks for DIO firmware/driver scratch use.
- `DIO_DP_ALPM_WAKEUP_INTERRUPT_STATUS`, `DIO_MEM_PWR_STATUS`, `DIO_MEM_PWR_CTRL`, and `DIO_MEM_PWR_CTRL2` describe wake interrupt state and light-sleep memory power state/control for I2C and DP link memories.
- `DIO_CLK_CNTL`, `DIO_POWER_MANAGEMENT_CNTL`, `DIG_SOFT_RESET`, `DIO_CLK_CNTL2`, and `DIO_CLK_CNTL3` describe DIO clock gating, power reset, front-end/back-end DIG soft resets, AFMT symbol clock gates, and TMDS symbol clock gates.
- The chunk ends after the first field of `DIO_HDMI_RXSTATUS_TIMER_CONTROL`, so its remaining timer fields continue in the next chunk.

The macros are paired by convention: `REGISTER__FIELD__SHIFT` is the least-significant bit position and `REGISTER__FIELD_MASK` is the already-shifted mask. Consumers combine these with register offsets from `dcn_3_2_1_offset.h`.

## Important APIs, Types, and Macros

There are no normal C APIs or types here. Important exported macro groups are:

- AUX engine programming:
  - `DP_AUXn_AUX_CONTROL` fields include enable, reset, reset-done, link-service read enable, update disable, HPD-disconnect ignore, mode detect, HPD select, impedance calibration request enable, test mode, and deglitch enable.
  - `DP_AUXn_AUX_SW_CONTROL`, `AUX_SW_DATA`, and `AUX_SW_STATUS` fields drive software AUX transactions through `AUX_SW_GO`, start delay, write byte count, indexed data, autoincrement disable, done/request bits, timeout/overflow/HPD-disconnect/protocol error bits, reply byte count, and arbitration status.
  - `DP_AUXn_AUX_ARB_CONTROL` fields arbitrate register ownership among software, link service, and DMCU/firmware users through priority, register ownership status, queued-go disables, pending request aliases, and done-using bits.
  - `DP_AUXn_AUX_INTERRUPT_CONTROL` exposes software done, link-service done, GTC sync lock done, and GTC sync error interrupt/status/ack/mask bits.
  - `DP_AUXn_AUX_LS_STATUS` and `DP_AUXn_AUX_LS_DATA` mirror status/data fields for link-service AUX reads, including CP IRQ, updated, and updated-ack bits.
- AUX physical layer and timing:
  - `DP_AUXn_AUX_DPHY_TX_REF_CONTROL`, `AUX_DPHY_TX_CONTROL`, `AUX_DPHY_RX_CONTROL0`, and `AUX_DPHY_RX_CONTROL1` define TX reference/rate/divider, precharge, output-enable timing, receive windows, threshold behavior, phase detect length, timeout length/multiplier, and precharge skip fields.
  - `DP_AUXn_AUX_DPHY_TX_STATUS` and `AUX_DPHY_RX_STATUS` report TX current-sense calibration and RX mode-detection state.
  - `DP_AUXn_AUX_GTC_SYNC_*` fields configure and observe DP AUX global-time-code synchronization: lock enable, RX global timestamp counters, phase offsets, error timeout/threshold/counter, controller state, continuous update, locked/lost/error status, and status clear.
  - `DP_AUXn_AUX_PHY_WAKE_CNTL` exposes AUX wake enable/status/clear/mask and the AUX connect request status.
- DDC I2C:
  - `DC_I2C_CONTROL`, `DC_I2C_ARBITRATION`, `DC_I2C_INTERRUPT_CONTROL`, and `DC_I2C_SW_STATUS` describe GO/reset/status reset, send reset, software status, transaction count, DDC select, soft reset, register ownership, queuing policy, interrupt acks/masks, timeout, NACK, stop, and overflow state.
  - `DC_I2C_DDC1_HW_STATUS` through `DC_I2C_DDC5_HW_STATUS` describe hardware request, done, status, byte count, setup failure, arbitration loss, timeout, reset, EDID detection, and request type for each DDC engine.
  - `DC_I2C_DDC1_SPEED` through `DC_I2C_DDC5_SETUP` define prescale, threshold, start/stop timing, time limits, enable, data drive enable, setup fail trigger, and send-reset length.
  - `DC_I2C_TRANSACTION0` through `DC_I2C_TRANSACTION3` define stop-on-NACK, start/stop generation, RW, count, and STOP bits for up to four transaction descriptors; `DC_I2C_DATA` supplies RW, byte, index, and autoincrement disable fields.
  - `DC_I2C_EDID_DETECT_CTRL` and `DC_I2C_READ_REQUEST_INTERRUPT` expose EDID detect mode/enable and read-request interrupt ack/mask bits.
- DIO misc:
  - `DIO_MEM_PWR_*` tracks and controls I2C and DPA-DPG memory light sleep, including force/disable controls.
  - `DIO_CLK_CNTL*` controls DISPCLK/REFCLK/SOCCLK/SYMCLK gates for DIGA-DIGG, AFMT, and TMDS paths.
  - `DIG_SOFT_RESET` has paired front-end/back-end soft reset fields for DIGA-DIGG.
  - `DIO_POWER_MANAGEMENT_CNTL` exposes PM reset and all-busy-off state.

## Control Flow

This header has no runtime control flow. Runtime control is implemented by display components that include the matching offset and shift/mask headers, populate register/field tables, and call DC register helper macros such as `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and `REG_UPDATE_N`.

External flows implied by this chunk include:

1. AUX transactions: a caller acquires AUX register ownership via `AUX_ARB_CONTROL`, programs `AUX_SW_DATA` and `AUX_SW_CONTROL` byte count/start delay, asserts `AUX_SW_GO`, polls or interrupts on `AUX_SW_DONE`, reads reply byte count/data/status, acknowledges `AUX_SW_DONE_ACK`, and releases ownership with `AUX_SW_DONE_USING_AUX_REG`.
2. AUX link-service reads and CP IRQ handling: link-service status/data and updated/ack bits allow hardware-assisted AUX monitoring separate from direct software transactions.
3. AUX DPHY setup: link encoder initialization uses RX start/receive windows, threshold, transition filter, precharge skip, timeout length, TX precharge, and mode-detect delay fields before normal hotplug/link traffic.
4. I2C/DDC operations: hardware I2C setup deasserts soft reset, optionally wakes I2C memory from light sleep, acquires I2C arbitration, programs speed/setup/transactions/data, handles interrupts/status, releases the engine, and may force I2C memory back into light sleep.
5. Link encoder muxing and reset: DCN link encoder code writes `DIO_LINKx_CNTL` fields in adjacent chunks for HPO HDMI/DP routing; this chunk provides the DIO clock, reset, and power fields that bound that programming.
6. Power and clock gating: display initialization, suspend/resume, and low-power paths use DIO memory power status/control, clock gate disables, and DIG soft-reset masks to coordinate access to DIO sub-blocks.

## State and Persistence Behavior

The macros are stateless compile-time constants. They describe MMIO register fields whose state lives in display hardware:

- Persistent configuration until reset or reprogramming: AUX enable, HPD select, mode detect, deglitch, DPHY timing, GTC sync configuration, I2C speed/setup limits, DDC select, DIO light-sleep disable/force fields, clock gate disable fields, DIG soft reset bits, and PM reset fields.
- Transient command or handshake fields: `AUX_SW_GO`, link-service read trigger, interrupt ACK bits, GTC status clear, AUX wake clear, I2C GO, send reset, status reset, transaction START/STOP, EDID detect controls, read-request interrupt ACK, and done-using arbitration bits.
- Status/observation fields: AUX done/request/error/reply-count/arbitration, DPHY TX/RX status, GTC controller/sync/error status, AUX wake/connect request, I2C hardware/software status, I2C timeout/NACK/overflow/stop, DDC EDID detection, DIO memory power states, ALPM wake interrupt state, PM all-busy-off, and HDMI RX status timer state.
- Scratch registers are modeled as full 32-bit fields and may preserve opaque firmware/driver state until overwritten or reset by the relevant hardware domain.

## Dependencies

This chunk depends on the generated AMDGPU/DCN register infrastructure:

- Matching register offsets and base indices in `drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`.
- DC register access helpers and field-table macros that expect the `REG__FIELD__SHIFT` and `REG__FIELD_MASK` naming convention.
- AUX consumers in `display/dc/dce/dce_aux.h` and related AUX engine code, which map `DP_AUX0_*` fields into `struct dce110_aux_registers` and AUX mask/shift tables.
- DDC I2C consumers in `display/dc/dce/dce_i2c_hw.c` and `dce_i2c_hw.h`, which use `DIO_MEM_PWR_CTRL`, `DIO_MEM_PWR_STATUS`, and `DC_I2C_*` fields for hardware I2C transactions.
- Link encoder/resource consumers such as `display/dc/dio/dcn31/dcn31_dio_link_encoder.*`, `dcn35_dio_link_encoder.*`, and DCN resource files, which use AUX DPHY fields, DIO clock fields, memory power fields, and DIG/DIO register tables.

The path is inside a Ceph client source corpus, but the content is Linux AMDGPU display driver register metadata and is not Ceph-specific.

## Integration Points

Important integration points are:

- DisplayPort AUX transport for DPCD reads/writes, link training support traffic, HDCP/CP IRQ handling, hotplug-related AUX wake, and AUX-to-GTC synchronization.
- Display DDC hardware I2C for EDID reads, HDMI/DP sink management, HDCP polling, and DDC arbitration with firmware/hardware users.
- Link encoder initialization, where AUX DPHY timing and DIO clock/reset state must be correct before a transmitter can communicate reliably.
- Display power management, where low-power memory controls and clock gate disables interact with register availability and suspend/resume behavior.
- Firmware/DMUB/DMCU coordination, especially around AUX/I2C arbitration and shared ownership fields.
- Hardware diagnostics and bring-up tooling, where scratch registers, protocol error status bits, GTC sync status, DPHY status, and DIO clock/reset bits are useful readback signals.

## Risks and Edge Cases

- Generated mask/shift drift would silently corrupt MMIO field access. AUX/I2C ownership, status ack, clock gate, reset, and power fields are especially sensitive because wrong bits can hang register access or break hotplug/DDC.
- The chunk repeats nearly identical register layouts for AUX0-AUX4 and DDC1-DDC5. Copy/paste or generated-index mistakes can compile while programming the wrong engine.
- Ownership fields have aliases such as pending request and use request sharing the same bit. Callers must use the correct semantic name for readability and must still follow the hardware handshake.
- ACK, clear, GO, reset, and done-using fields may have pulse or write-one semantics. Generic read-modify-write behavior can lose events if callers do not respect the hardware protocol.
- Multi-bit fields such as HPD select, start delay, write byte count, reply byte count, RX timeout, timestamp counters, I2C prescale/time limits, byte counts, and test clock select require proper masking and range validation.
- I2C memory light sleep must be coordinated with register access. `dce_i2c_hw.c` explicitly wakes memory and waits on `I2C_MEM_PWR_STATE` before setup, then can force light sleep on release.
- AUX and I2C arbitration crosses software and firmware/hardware users. Failing to release ownership can starve DMUB/DMCU or hardware pollers; releasing while a transaction is active can corrupt bus traffic.
- Clock gate and soft-reset fields affect shared DIO/DIG blocks across multiple links. Per-link changes can have cross-link impact when clocks or reset domains are shared.
- The chunk boundary starts after the `DP_AUX0_AUX_CONTROL` shift definitions and ends before the full `DIO_HDMI_RXSTATUS_TIMER_CONTROL` block is present. The final merged report needs adjacent chunks for complete field coverage.

## Test Signals

Useful validation signals for code using this chunk:

- Build coverage for DCN 3.2.1 consumers that include `dcn_3_2_1_offset.h` and this shift/mask header, catching missing or renamed generated macros.
- Generated consistency checks that every field has aligned shift/mask pairs, masks match shifts, and repeated AUX/DDC instances have equivalent field layouts where expected.
- Unit-style field insert/extract tests for multi-bit fields: AUX HPD select, AUX write/reply byte counts, AUX RX timeout length/multiplier, GTC timestamps/offsets, I2C prescale/time limits, I2C transaction count, DDC byte count, DIO test clock select, and DIG reset bits.
- Hardware smoke tests for DP AUX DPCD reads/writes, EDID reads over DDC1-DDC5, hotplug with AUX wake, link training, HDCP polling, and suspend/resume with I2C memory low power enabled.
- Register trace checks that AUX/I2C arbitration is acquired and released, ACK/clear bits are written only after the corresponding status event, and light-sleep force is paired with a successful power-state wait.
- Display mode-set and link recovery tests across multiple transmitters to catch clock gate, soft reset, or repeated-instance indexing errors.

## Chunk Boundary Notes

The first visible line is the final `SPARE_1_MASK` entry for `DP_AUX0_AUX_CONTROL`; that register's shift entries and earlier masks are in the previous chunk. The last visible line is `DIO_HDMI_RXSTATUS_TIMER_CONTROL__DIO_HDMI_RXSTATUS_TIMER_ENABLE__SHIFT`; the rest of that register's fields continue after line 39686. The merge/reconciliation lane should combine this report with adjacent chunks before producing the final per-file research document for `dcn_3_2_1_sh_mask.h`.
