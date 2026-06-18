# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 32384-34755

## Scope

This chunk is part of the generated AMD DCN 2.1.0 ASIC register mask/shift header. It covers lines 32384-34755 and exports bit-position and bit-mask constants for the tail of OTG5 timing, OPTC misc and performance monitor registers, DIO I2C, DIG soft reset and clock/power/interrupt registers, HPD0-HPD4, DIO performance monitor 18, and DP AUX0-AUX3. The slice contains 2,178 `#define` entries: 1,091 `__SHIFT` constants and 1,087 `_MASK` constants. It has no C functions, structs, enums, or executable code; its API is the generated macro namespace consumed by AMDGPU display register helper tables.

The chunk starts mid-register with the remaining `OTG5_OTG_RANGE_TIMING_INT_STATUS` masks and ends mid-register at `DP_AUX3_AUX_SW_STATUS`, so whole-file reconciliation must merge it with adjacent chunks for complete register-family coverage.

## Purpose

The purpose of this chunk is to bind symbolic DCN 2.1.0 display register fields to exact hardware bit layouts. Driver code uses these constants through register-field tables and generic access helpers instead of open-coded masks and shifts.

Major hardware domains represented here are:

- OTG5 timing state: dynamic refresh-rate tracking, DSC start position, request mode, range-timing interrupt status, pipe update pending/taken/clear bits, and vupdate keepout status.
- OPTC misc state: display-writeback source selection, global swap-lock ready/timing source selection, OPTC clock gating/test clock controls, ODM memory power controls for memories 0-11, vblank/unassigned memory power modes, and memory power status.
- DC performance monitors 17 and 18: event selection, counter modes, run-enable selectors, counter state, counter interrupt status/ack, high/low value readback, and counter-off interrupt controls.
- DIO I2C engine: software transaction control, arbitration between software and DMCU, interrupt status/ack/mask bits, DDC1-DDC5 hardware status, per-DDC speed/setup, four transaction descriptors, data FIFO/index access, EDID detect, and read-request interrupts for DDC1-DDC6/DDCVGA.
- DIO global controls: DIG front-end/back-end soft resets for DIGA-DIGG, AFMT/DME memory power status, clock gate controls for AFMT and TMDS symbol clocks, HDMI RX status timer interrupt configuration, PSP interrupt message/status, and generic interrupt message/status.
- HPD0-HPD4: hotplug sense and delayed-sense status, RX interrupt status, HPD interrupt ack/polarity/enable, connection/RX timers, fast-train delays/enables, and connect/disconnect toggle filter delays.
- DP AUX0-AUX3: AUX enable/reset, HPD selection, arbitration with software/DMCU, software transaction trigger and status, interrupt ack/masks, native and link-service data/status, DPHY TX/RX timing/status, GTC sync control/error/status for AUX0-AUX2, and AUX PHY wake controls.

## Important API Surface

The exported surface follows the generated convention:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Important macro families in this chunk include:

- `OTG5_OTG_PIPE_UPDATE_STATUS__OTG_FLIP_PENDING`, `OTG5_OTG_PIPE_UPDATE_STATUS__OTG_DC_REG_UPDATE_TAKEN`, and `OTG5_OTG_PIPE_UPDATE_STATUS__OTG_CURSOR_UPDATE_TAKEN_CLEAR` for pipe update sequencing.
- `DWB_SOURCE_SELECT__OPTC_DWB*_SOURCE_SELECT`, `GSL_SOURCE_SELECT__GSL*_READY_SOURCE_SEL`, and `OPTC_CLOCK_CONTROL__OPTC_DISPCLK_R_*` for routing and clock state in the OPTC misc block.
- `ODM_MEM_PWR_CTRL*` and `ODM_MEM_PWR_STATUS__ODM_MEM*_PWR_STATE` for controlling and observing ODM memory power state.
- `DC_PERFMON17_*` and `DC_PERFMON18_*` for display performance counter selection, run gating, interrupt acknowledgement, and value readback.
- `DC_I2C_CONTROL`, `DC_I2C_ARBITRATION`, `DC_I2C_INTERRUPT_CONTROL`, `DC_I2C_SW_STATUS`, `DC_I2C_DDC*_SPEED`, `DC_I2C_DDC*_SETUP`, `DC_I2C_TRANSACTION*`, and `DC_I2C_DATA` for DDC/EDID software I2C transactions.
- `DC_I2C_READ_REQUEST_INTERRUPT__DC_I2C_DDC*_READ_REQUEST_*` for hardware read-request interrupt reporting, acknowledgement, masking, and interrupt type.
- `DIG_SOFT_RESET`, `DIO_CLK_CNTL2`, `DIO_CLK_CNTL3`, `DIO_HDMI_RXSTATUS_TIMER_CONTROL`, `DIO_PSP_INTERRUPT_*`, and `DIO_GENERIC_INTERRUPT_*` for global DIO reset, clock/power, and interrupt-message handling.
- `HPD[0-4]_DC_HPD_*` for hotplug detect sense, interrupt control, connection timer programming, fast-train timing, and toggle filtering.
- `DP_AUX[0-3]_AUX_CONTROL`, `AUX_SW_CONTROL`, `AUX_ARB_CONTROL`, `AUX_INTERRUPT_CONTROL`, and `AUX_SW_STATUS` for AUX channel ownership, software transaction launch, status polling, and interrupt acknowledgement.
- `DP_AUX[0-2]_AUX_LS_STATUS`, `AUX_SW_DATA`, `AUX_LS_DATA`, `AUX_DPHY_*`, `AUX_GTC_SYNC_*`, and `AUX_PHY_WAKE_CNTL` for link-service events, AUX data windows, DPHY timing, GTC sync lock/error reporting, and PHY wake handshakes.

These constants are normally consumed through AMD display register access helpers such as `REG_GET`, `REG_UPDATE`, `REG_SET`, symbol-pasting field-list macros, and block-specific table initializers. For DCN 2.1, `drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, `drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c`, `drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`, `drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, and `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c` include the matching `dcn_2_1_0_offset.h` and `dcn_2_1_0_sh_mask.h` headers.

## Control Flow

There is no local control flow in this header chunk. Runtime behavior is in display driver code that binds these generated constants to register tables and then performs ordered MMIO reads/writes:

- DCN 2.1 resource construction builds link encoder AUX and HPD register arrays with macros such as `DCN2_AUX_REG_LIST(id)` and `HPD_REG_LIST(id)`. Those arrays pair offset-header addresses with the shifts and masks defined here.
- AUX transaction paths in DCE/DCN link encoder and AUX code request ownership through `AUX_ARB_CONTROL`, program software data and transaction byte counts, trigger `AUX_SW_GO`, then poll `AUX_SW_STATUS` or acknowledge `AUX_INTERRUPT_CONTROL`.
- I2C/DDC paths request I2C register ownership through `DC_I2C_ARBITRATION`, configure per-DDC speed/setup and transaction descriptors, write/read `DC_I2C_DATA`, trigger `DC_I2C_GO`, and interpret `DC_I2C_SW_STATUS` error bits such as timeout, aborted, buffer overflow, and NACK.
- HPD handling code reads `DC_HPD_INT_STATUS`/`DC_HPD_SENSE`, programs HPD timers and filters, and acknowledges/enables hotplug and RX interrupts through `DC_HPD_INT_CONTROL`.
- IRQ service code for DCN 2.1 includes this header so generated masks/shifts can back interrupt source setup and status/ack handling.
- Link encoder bring-up and low-level DIO code use DPHY timing, AUX reset, HPD select, and wake bits to prepare AUX channels for DisplayPort link training and sideband transactions.
- Clock, reset, and power-management paths use `DIG_SOFT_RESET`, `DIO_CLK_CNTL*`, `DIO_MEM_PWR_STATUS1`, `ODM_MEM_PWR_CTRL*`, and `ODM_MEM_PWR_STATUS` fields around modeset, encoder reset, and power-gating sequences.
- Performance-monitor control code can select events, start/stop counters, acknowledge counter interrupts, and read low/high counter values through the `DC_PERFMON17_*` and `DC_PERFMON18_*` fields.

Ordering is an implicit hardware contract. For example, ownership request/status fields must be sequenced before writes to shared I2C/AUX registers, sticky interrupt/status bits must be acknowledged without clobbering adjacent enable/mask fields, and reset/wake bits must be paired with polling of done/ack status where hardware requires it.

## State and Persistence

The file stores no software state. Its macros describe memory-mapped hardware state that persists in GPU display blocks while those blocks are powered:

- OTG5 pipe update bits expose live and sticky flip/register/cursor update state, including clear bits that alter hardware status.
- OPTC routing, GSL source selection, clock controls, and ODM memory power fields persist as active display pipe configuration.
- Performance monitor registers hold selected events, run/stop mode, counter state, interrupt state, and counter values until disabled, reset, overwritten, or power-cycled.
- I2C/DDC registers hold transaction descriptors, selected DDC line, speed/setup timing, data index/window state, EDID detect settings, and software/hardware status bits.
- HPD registers hold debounce/timer/filter configuration and live hotplug/RX interrupt state for each HPD instance.
- AUX registers hold reset/enable/HPD selection, transaction byte count and data window state, arbitration ownership, link-service update state, DPHY timing calibration, GTC sync thresholds/state, and PHY wake handshakes.
- DIO reset, clock gate, memory power, PSP, and generic interrupt registers affect shared display I/O state across encoders.

Wrong constants can leave hardware in a bad programmed state until a modeset, block reset, suspend/resume, GPU reset, or full driver reinitialization restores known-good register contents.

## Dependencies and Integration Points

This chunk depends on the matching `dcn_2_1_0_offset.h` register addresses and on AMD display helper macros that paste register and field names into `__SHIFT` and `_MASK` identifiers. The masks are only correct for DCN 2.1.0 hardware; same-named fields in DCN 2.0, DCN 3.x, DCN 4.x, and DCE headers can differ.

Key integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, where DCN 2.1 resource tables include this header and construct AUX/HPD register arrays for five link instances.
- `drivers/gpu/drm/amd/display/dc/dce/dce_aux.h` and `dce_aux.c`, where AUX field-list structures and ownership/polling helpers consume `DP_AUX0_*` style masks/shifts through symbol-pasting macros.
- `drivers/gpu/drm/amd/display/dc/dce/dce_i2c_hw.h` and `dce_i2c_hw.c`, where I2C field-list structures and software transaction helpers consume `DC_I2C_*` masks/shifts for arbitration, setup, transaction, data, and status handling.
- `drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_link_encoder.c` and related DCN link encoder code, where AUX DPHY timing and AUX control fields are programmed during encoder initialization and DisplayPort AUX setup.
- `drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c` and `hw_translate_dcn21.c`, where HPD/DDC GPIO abstractions bind DCN 2.1 register metadata to generic GPIO services.
- `drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, which includes the generated DCN 2.1 offset and mask headers for interrupt source integration.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, which includes this header for DMUB-facing DCN 2.1 register access.

## Risks

- A wrong shift or mask silently targets the wrong hardware bit. Highest-risk fields here are ownership/arbitration bits, transaction launch bits, reset bits, interrupt acknowledgements, and packed timing fields.
- The I2C and AUX engines have shared ownership with DMCU/firmware paths. Incorrect `*_USE_*_REQ`, `*_DONE_USING_*`, or `*_REG_RW_CNTL_STATUS` fields can deadlock register access or race firmware ownership.
- Status, mask, ack, and enable bits are often packed into the same register. A bad read-modify-write mask can drop hotplug, AUX, I2C, PSP, generic, or performance counter interrupts, or repeatedly retrigger stale sticky status.
- HPD0-HPD4 and DP_AUX0-DP_AUX3 are near-duplicate register families. Instance drift can affect only one connector, making regressions appear as board-, port-, or monitor-specific failures.
- DDC speed/setup and AUX DPHY timing fields are narrow and hardware-sensitive. Bit mistakes can cause EDID read failures, AUX timeouts, link training failures, or intermittent DisplayPort sideband errors rather than immediate compile failures.
- `DP_AUX3` is truncated in this chunk after the first `AUX_SW_STATUS` shifts, while AUX0-AUX2 have complete LS/DPHY/GTC/wake coverage in this slice. Final reporting must avoid treating this chunk alone as the complete AUX3 definition.
- Performance monitor fields expose diagnostic counters, so most mask errors are unlikely to break normal display bring-up but can invalidate profiling, interrupt-on-threshold behavior, or debug telemetry.
- Generated headers are not usually unit-tested directly. Many errors surface only when a specific DCN generation, connector instance, interrupt path, low-power path, or hardware transaction is exercised.

## Test Signals

Useful validation signals for changes to this chunk are:

- AMDGPU display build coverage for DCN 2.1 paths, including `dcn21_resource.c`, `irq_service_dcn21.c`, GPIO translation/factory code, DCE I2C, DCE AUX, link encoder code, and DMUB DCN21 code.
- Static comparison against the vendor register database and the adjacent `dcn_2_1_0_offset.h`, verifying that each field's shift and mask match the correct register address and that repeated HPD/AUX/DDC instance families stay intentionally consistent.
- Display hotplug testing across HPD0-HPD4, including connect/disconnect debounce, delayed sense, RX interrupt generation, interrupt acknowledgement, and fast-train timing where supported.
- EDID/DDC tests across all wired DDC instances, covering normal reads, NACK handling, timeout handling, abort paths, read-request interrupts, and DDC speed/setup programming.
- DisplayPort AUX tests across AUX0-AUX3, including software AUX reads/writes, link-service update status, HPD disconnect during AUX, timeout/overflow/error reporting, AUX reset, and AUX PHY wake.
- Modeset and DisplayPort link-training tests that exercise AUX DPHY timing and HPD/AUX routing, especially on multi-connector systems.
- Suspend/resume, runtime power-management, and low-power display tests that observe DIG/AFMT/DME/ODM memory power status and verify DIO clocks/resets recover correctly.
- Performance monitor smoke tests or debugfs/tooling checks that can configure counters, observe active/run state, read low/high counter values, and clear counter interrupts.

## Chunk Notes

This chunk is generated register metadata, not functional logic. The main research value is identifying the hardware contracts covered by the constants: OTG5 update/timing status, OPTC routing and memory power, DIO I2C/HPD/AUX transaction machinery, DIO reset/clock/interrupt controls, and DC performance monitoring. The final merged report should connect this slice with adjacent chunks to provide complete coverage of `dcn_2_1_0_sh_mask.h`, especially for the partial `OTG5_OTG_RANGE_TIMING_INT_STATUS` start and partial `DP_AUX3_AUX_SW_STATUS` end.
