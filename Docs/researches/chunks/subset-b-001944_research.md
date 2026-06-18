# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 37352-39690

## Scope

This chunk is part of the generated DCN 3.2.0 ASIC register shift/mask header. It contains C preprocessor constants for display I/O register bitfields rather than executable functions. The covered range starts in the `DP_AUX0_AUX_CONTROL` field list, defines the complete repeated DisplayPort AUX register-field families for AUX0 through AUX4, then defines DOUT I2C/DDC register fields and the beginning of the DIO miscellaneous control block.

## Purpose

The macros provide the bit positions (`__SHIFT`) and bit masks (`_MASK`) that AMDGPU DCN display code uses when programming display hardware through memory-mapped registers. The primary hardware areas represented here are:

- DisplayPort AUX channel instances `DP_AUX0` through `DP_AUX4`, under address blocks such as `dcn_dc_dio_dp_aux1_dispdec`.
- DOUT I2C/DDC controller fields in `dcn_dc_dio_dout_i2c_dispdec`.
- DIO miscellaneous fields in `dcn_dc_dio_dio_misc_dispdec`, including scratch registers, DisplayPort ALPM wake status, DIO memory light sleep controls, clock gating controls, and DIG soft resets.

These definitions are an ABI layer between generated register descriptions and hand-written driver logic. They let call sites construct register values without hard-coding raw hexadecimal field locations in the driver source.

## Important Macro Families

### DisplayPort AUX0-AUX4

Each AUX instance uses the same register-field pattern with only the instance number changed. This chunk includes full field sets for `DP_AUX1` through `DP_AUX4` and the tail of `DP_AUX0` beginning at line 37352.

Important AUX control fields include:

- `DP_AUXn_AUX_CONTROL__AUX_EN`, `AUX_RESET`, and `AUX_RESET_DONE` for enabling and resetting the AUX engine.
- `AUX_LS_READ_EN`, `AUX_LS_UPDATE_DISABLE`, and `AUX_IGNORE_HPD_DISCON` for link-service behavior and HPD disconnect handling.
- `AUX_MODE_DET_EN`, `AUX_HPD_SEL`, `AUX_IMPCAL_REQ_EN`, `AUX_TEST_MODE`, and `AUX_DEGLITCH_EN` for mode detection, HPD routing, impedance calibration, test behavior, and input filtering.
- `SPARE_0` and `SPARE_1` masks occupying the top bits of `AUX_CONTROL`.

The software transaction path is represented by:

- `AUX_SW_CONTROL`: `AUX_SW_GO`, `AUX_LS_READ_TRIG`, `AUX_SW_START_DELAY`, and `AUX_SW_WR_BYTES`.
- `AUX_SW_STATUS`: completion/request flags plus receive error signals such as timeout, overflow, HPD disconnect, partial byte, non-AUX mode, min-count violation, invalid stop/start/sync, no-detect, invalid high/low receive, reply byte count, and arbitration status.
- `AUX_SW_DATA`: byte payload, data read/write direction, index, and autoincrement disable.

The link-service path mirrors the software status/data model through:

- `AUX_LS_STATUS`: link-service completion/request, receive error diagnostics, reply byte count, CP IRQ, updated flag, and update acknowledgement.
- `AUX_LS_DATA`: link-service byte payload and index.

The arbitration model is exposed through:

- `AUX_ARB_CONTROL`: priority, register read/write control status, no-queued software/link-service flags, software register-use request/done, and DMCU register-use request/done.
- Some request/pending names intentionally alias the same bit position and mask, such as `AUX_SW_USE_AUX_REG_REQ` and `AUX_SW_PENDING_USE_AUX_REG_REQ`. Consumers must treat these aliases according to the hardware programming guide.

Physical-layer timing/status fields include:

- `AUX_DPHY_TX_REF_CONTROL`: transmit reference selection, rate, and divider.
- `AUX_DPHY_TX_CONTROL`: precharge length/multiplier, output-enable assert timing, precharge symbols, and mode-detection check delay.
- `AUX_DPHY_RX_CONTROL0` and `AUX_DPHY_RX_CONTROL1`: receive start/receive windows, half-symbol and phase-detection lengths, transition filtering, threshold allowances, detection threshold, precharge skip, timeout length, and timeout multiplier.
- `AUX_DPHY_TX_STATUS` and `AUX_DPHY_RX_STATUS`: active/state flags and measured half-symbol periods/counts.

GTC synchronization support is represented by:

- `AUX_GTC_SYNC_CONTROL`: enable, impedance calibration, calibration interval, lock-acquisition and maintenance periods, block request, interval reset window, offset calculation attempts, and lock acquisition attempts.
- `AUX_GTC_SYNC_ERROR_CONTROL`: potential and definite error thresholds, lock-acquisition timeout length, and retry count for lock maintenance.
- `AUX_GTC_SYNC_CONTROLLER_STATUS`: lock acquisition complete/lost, timeout occurred/state, phase adjust time violation, critical error, max potential/definite error reached, acknowledgement fields, and controller state.
- `AUX_GTC_SYNC_STATUS`: transaction completion/request plus the same receive error categories as other AUX transactions, with GTC-specific `NACKED` and `MASTER_REQ_BY_RX` fields.

Low-power wake coordination is exposed by:

- `AUX_PHY_WAKE_CNTL`: `DP_AUX_PHY_WAKE_GO`, pending, priority, and acknowledgement bits for each AUX instance.

### DOUT I2C/DDC

The `DC_I2C_*` macros describe a shared display I2C/DDC controller used for software I2C transactions, hardware DDC activity, EDID detection, and read-request interrupts.

Core controller fields:

- `DC_I2C_CONTROL`: `GO`, soft reset, send reset, software status reset, DDC select, transaction count, and debug reference select.
- `DC_I2C_ARBITRATION`: software priority, register read/write control status, no-queued software go, abort hardware/software transfer, software register-use request/done, and DMCU register-use request/done.
- `DC_I2C_INTERRUPT_CONTROL`: software done interrupt/ack/mask and hardware done interrupt/ack/mask triplets for DDC1 through DDC6 plus DDCVGA.
- `DC_I2C_SW_STATUS`: software status, done, aborted, timeout, interrupted, buffer overflow, stopped-on-NACK, per-transaction NACK0-NACK3, and request.

Hardware DDC status is repeated for `DC_I2C_DDC1_HW_STATUS` through `DC_I2C_DDC5_HW_STATUS` in this chunk. Each instance has hardware status, done, request, urgent, EDID detect status, number of valid tries, and EDID detect state fields. The interrupt register includes DDC6 and DDCVGA fields even though this chunk only shows DDC1-DDC5 hardware status blocks.

Per-DDC timing/setup fields are repeated for DDC1-DDC5:

- `DC_I2C_DDCn_SPEED`: threshold, disable-filter-during-stall, start/stop timing control, and prescale.
- `DC_I2C_DDCn_SETUP`: data drive enable/select, send-reset length, EDID detect enable/mode, controller enable, clock drive enable, intra-byte delay, intra-transaction delay, and time limit.

Transaction/data fields:

- `DC_I2C_TRANSACTION0` through `DC_I2C_TRANSACTION3`: read/write direction, stop-on-NACK, start, stop, and transfer byte count.
- `DC_I2C_DATA`: payload byte, data read/write direction, 10-bit index, and index write control.
- `DC_I2C_EDID_DETECT_CTRL`: EDID detect wait time, number of tries until valid, and send-reset behavior.
- `DC_I2C_READ_REQUEST_INTERRUPT`: per-DDC read-request occurred/int/ack/mask fields for DDC1-DDC6 and DDCVGA, plus global read-request ack enable and interrupt type.

### DIO Miscellaneous

The miscellaneous DIO section starts at line 39491 and contains:

- `DIO_SCRATCH0` through `DIO_SCRATCH7`: full-width 32-bit scratch register masks. These may be used as general hardware-visible driver/firmware scratch storage depending on platform convention.
- `DIO_DP_ALPM_WAKEUP_INTERRUPT_STATUS`: per-DIG `DIGA` through `DIGG` DisplayPort ALPM wakeup status bits.
- `DIO_MEM_PWR_STATUS`: memory power state bits for I2C and DP link blocks `DPA` through `DPG`.
- `DIO_MEM_PWR_CTRL` and `DIO_MEM_PWR_CTRL2`: force/disable light sleep controls for I2C and DP link blocks.
- `DIO_CLK_CNTL`: display/reference clock gate disable bits for DIO and per-DIG display clock gating.
- `DIO_POWER_MANAGEMENT_CNTL`: power-management reset assertion and all-busy-off indication/control.
- `DIG_SOFT_RESET`: front-end and back-end soft reset bits for DIGA through DIGG.
- `DIO_CLK_CNTL2`: DIO test clock select, SOCCLK AFMT gate disables, SYMCLK AFMT gate disables, and SYMCLK reference gate disables for A through G.
- Start of `DIO_CLK_CNTL3`: TMDS-related SYMCLK gate-disable shifts for A through G. The masks for this register continue beyond the chunk boundary.

## Control Flow and Runtime Behavior

This chunk has no direct control flow, functions, branches, or runtime allocation. Runtime behavior emerges when driver code includes this header and uses the macros with register-access helpers such as field-update, read-modify-write, poll, and interrupt acknowledgement paths elsewhere in the AMD display stack.

The implicit hardware control flows represented by these fields are:

- AUX transaction setup: write payload/index and transaction parameters, set `AUX_SW_GO`, then poll/interrupt on done/status/error fields.
- AUX register arbitration: request ownership of AUX registers for software or DMCU use, observe pending/status bits, then write the corresponding done bit after the critical section.
- AUX reset/enable: assert reset/enable fields and observe reset-done or status fields.
- AUX GTC sync: configure lock periods/error thresholds, enable sync, then inspect controller and transaction status/ack fields.
- I2C transaction setup: select DDC, configure up to four transaction descriptors and data buffer indices, set transaction count and `DC_I2C_GO`, then inspect software status, interrupt, NACK, and timeout fields.
- Hardware DDC/EDID detection: configure per-DDC speed/setup and EDID detect control, then use hardware status and interrupts to detect completion or EDID validity.
- DIO power/clock/reset management: set light sleep, clock gate disable, and soft reset bits around display link bring-up, power transitions, suspend/resume, or diagnostics.

## State and Persistence

The macros themselves are stateless compile-time constants. The state they address is hardware register state in the display engine:

- Transaction state is volatile and hardware-owned, including AUX/I2C request, done, timeout, NACK, overflow, and receive-error status bits.
- Interrupt state often uses paired `INT`, `ACK`, and `MASK` fields. Incorrect acknowledgement ordering can leave stale interrupts asserted or mask future events.
- Scratch registers are explicitly persistent hardware-visible 32-bit storage until reset or overwritten; their persistence semantics depend on the display block reset/power domain.
- Power, clock gate, light sleep, and reset bits persist in hardware register state and can affect later operations until changed or reset.
- Several fields are status/ack pairs or aliased request/pending definitions; consumers must not assume all fields are simple read/write storage.

## Dependencies and Integration Points

This header depends on the surrounding AMDGPU DCN register definition ecosystem:

- It pairs with same-ASIC address headers, commonly named with `_offset` or register-list variants, that define register addresses for the fields in this mask file.
- It is consumed by DCN display code under AMDGPU, especially Display Core (DC) link/AUX/DDC/I2C, HPD, EDID, clock, reset, and power-management paths.
- The `DP_AUXn` and `DC_I2C_*` definitions integrate with DisplayPort link training, DisplayPort AUX DPCD access, monitor EDID reads, DDC transactions, HPD behavior, and low-power display features.
- The DMCU ownership fields indicate coordination with display microcontroller firmware or related hardware agents that may also access AUX/I2C register files.
- The `DIGA` through `DIGG`, `DPA` through `DPG`, and `AFMT` naming ties this chunk to per-link display front-end/back-end and audio formatter blocks.

Because these definitions are generated hardware ABI constants, their correctness must match the ASIC register specification exactly. Higher-level code generally assumes the shift and mask values are authoritative.

## Risks and Edge Cases

- A wrong shift/mask silently corrupts unrelated register bits, which can break link training, AUX/DDC communication, EDID reads, interrupt handling, or power management.
- Repeated instance blocks invite copy/paste or generation mistakes. AUX0-AUX4 must remain structurally identical except for instance numbering and address binding in companion headers.
- The chunk begins in the middle of `DP_AUX0_AUX_CONTROL` and ends in the middle of `DIO_CLK_CNTL3`, so whole-file review must merge adjacent chunks to avoid missing the start/end of those register definitions.
- Aliased fields such as AUX register-use request and pending bits can be misread by generic tooling as duplicate definitions; for hardware access, the alias is meaningful and should not be automatically deduplicated without spec review.
- Interrupt fields with names ending in `_MASK_MASK` are generated names for a field named `*_MASK`; consumers and reviewers should distinguish the register interrupt-mask bit from the C macro suffix `_MASK`.
- I2C interrupt control references DDC6 and DDCVGA while visible speed/setup/status groups in this chunk cover DDC1-DDC5. The companion lines outside this chunk may contain the remaining register groups.
- Power and clock gate disable bits are safety-sensitive: programming them at the wrong time can cause register access timeouts or hung display links.
- Soft reset bits for front-end/back-end DIG blocks are broad controls; incorrect masks can reset the wrong display pipeline.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- Build coverage for AMDGPU/DCN 3.2.0 display code with this header included and warnings enabled.
- Static comparison of generated `__SHIFT` and `_MASK` values against the vendor register database for DCN 3.2.0.
- Consistency checks across `DP_AUX0` through `DP_AUX4`: each repeated register family should have the same field names, shifts, and masks after replacing the instance number.
- Register read/write tests or hardware smoke tests for DisplayPort AUX DPCD reads, link training, HPD disconnect behavior, and AUX timeout/error handling.
- EDID read tests over DDC/I2C for multiple connectors, including NACK, timeout, and read-request interrupt cases.
- Suspend/resume and display hotplug tests that exercise DIO memory light sleep, ALPM wake status, clock gating, and DIG soft reset paths.
- Interrupt tests that verify `INT`, `ACK`, and `MASK` fields clear and mask only their intended DDC/AUX events.

## Unresolved Cross-Chunk References

- The start of `DP_AUX0_AUX_CONTROL` is before this chunk at lines 37346-37351.
- `DIO_CLK_CNTL3` continues after line 39690, so this chunk only observes its shift definitions and some early mask lines from the adjacent context.
- Consumers of these macros, companion register address definitions, and any generated metadata comments are outside this chunk and must be reconciled in the final per-file research document.
