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
