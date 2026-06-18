# sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx-conf-reg.h

## Purpose

`cx231xx-conf-reg.h` defines the Polaris/cx231xx control-register addresses, endpoint enable masks, power-mode bits, AV mode enum values, AFE/Colibri register addresses, and DIF register addresses/field masks used by the cx231xx hardware-control code. It is a pure register map header with no executable logic.

## Important APIs, Types, And Definitions

- Top-level system-control registers: `BOARD_CFG_STAT`, `TS_MODE_REG`, `TS1_CFG_REG`, `TS1_LENGTH_REG`, `TS2_CFG_REG`, `TS2_LENGTH_REG`, `EP_MODE_SET`, CIR power/config registers, `GBULK_BIT_EN`, and `PWR_CTL_EN`.
- Endpoint masks: `ENABLE_EP1` through `ENABLE_EP6` map endpoint enable bits used by `cx231xx_start_stream()` and `cx231xx_stop_stream()`.
- Power bits: `PWR_MODE_MASK`, `PWR_AV_EN`, `PWR_ISO_EN`, `PWR_AV_MODE`, `PWR_TUNER_EN`, `PWR_DEMOD_EN`, `I2C_DEMOD_EN`, and `PWR_RESETOUT_EN` define `PWR_CTL_EN` manipulation.
- `enum AV_MODE` defines `POLARIS_AVMODE_DEFAULT`, `POLARIS_AVMODE_DIGITAL`, `POLARIS_AVMODE_ANALOGT_TV`, and `POLARIS_AVMODE_ENXTERNAL_AV`.
- AFE/Colibri input-mode constants: `SINGLE_ENDED`, `LOW_IF`, `EU_IF`, and `US_IF`.
- AFE super-block and ADC channel registers cover tuning, PLL, reference, powerdown, quantizer calibration, channel status, clamp power, DAC controls, DC servo/dynamic element matching, modulator reset, input selection, preclamp, resistor/termination, and test-bus control for three ADC channels.
- DIF register base `DIRECT_IF_REVB_BASE` and register offsets define PLL frequency/control, AGC references and current values, video AGC, audio/video override, AV separation, compensation filters, miscellaneous control, source phase/gain, bandpass filter coefficients, report variance, soft reset, and PLL frequency error.
- DIF field masks such as `FLD_DIF_DIF_BYPASS`, `FLD_DIF_SPEC_INV`, `FLD_DIF_AUD_SRC_SEL`, `FLD_DIF_PLL_FREQ`, AGC fields, BPF coefficient masks, and reset masks support read-modify-write operations in `cx231xx-avcore.c`.

## Control Flow

There is no control flow in this header. It is included by the main cx231xx header and consumed by implementation files. Runtime behavior emerges when `cx231xx-avcore.c` uses these constants to set power modes, endpoint enables, AFE input and power state, DIF standards, and stream transfer modes.

## State And Persistence

The header defines symbolic constants only. It does not allocate memory, store state, or perform persistence. Its definitions describe hardware state that persists in device registers after writes by the driver.

## Dependencies And Integration Points

The header is guarded by `_POLARIS_REG_H_` and is used by cx231xx driver code that performs USB vendor control reads/writes, I2C register writes, GPIO/stream setup, and DIF programming. The strongest consumer is `cx231xx-avcore.c`, but endpoint and power macros also affect audio, MPEG, VBI, video, DVB, and board setup paths through shared helper functions.

## Risks And Edge Cases

- Register and field masks are hardware contracts. A wrong value silently misroutes endpoints, powers down blocks, or corrupts tuner IF/video processing.
- `POLARIS_AVMODE_ENXTERNAL_AV` contains a spelling error that is part of the source ABI; renaming it would require coordinated source updates.
- Field masks encode positions but not shifts for most fields, so callers must use helpers like `cx231xx_set_field()` correctly.
- Endianness is not expressed here; users must preserve the little-endian byte ordering expected by USB control-register writes.
- Because many DIF register constants are profile-programmed with opaque magic values, tests need hardware signal validation rather than simple compile-time checks.

## Test Signals

Compile coverage should ensure every consumer still builds after header changes. Runtime signals include correct endpoint bit toggling in `EP_MODE_SET`, correct power sequencing through `PWR_CTL_EN`, working analog/digital/external-AV mode switches, successful AFE input selection for composite/S-video/tuner, standard-specific DIF lock and video/audio quality, and no regressions in tuner I2C port switching. Static review should verify new register definitions against hardware documentation and maintain one-to-one use of masks with helper functions.
