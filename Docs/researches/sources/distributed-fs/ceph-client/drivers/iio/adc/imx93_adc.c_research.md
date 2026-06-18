# sources/distributed-fs/ceph-client/drivers/iio/adc/imx93_adc.c

## Purpose
`imx93_adc.c` supports the NXP i.MX93 ADC as a direct-mode IIO voltage device with eight channels. It performs probe-time ADC calibration, then uses normal one-shot conversions completed by the third platform IRQ.

## Important APIs, types, and functions
- `struct imx93_adc` holds MMIO, IPG clock, IRQ, vref regulator, mutex, and completion.
- `imx93_adc_power_down()` and `imx93_adc_power_up()` manage ADC power state and poll status.
- `imx93_adc_calibration()` configures calibration mode, starts calibration, waits up to 2 seconds, and logs calibration failure.
- `imx93_adc_read_channel_conversion()` configures normal channel mask, interrupt masks, one-shot mode, starts conversion, waits, and reads `PCDRn`.
- `imx93_adc_isr()` acknowledges EOC/ECH interrupts and reports unexpected bits.
- Runtime PM callbacks power down/up and manage clock/regulator.

## Control flow
Probe maps MMIO, gets IRQ index 2, obtains clock and regulator, enables them, requests IRQ, runs calibration, configures AD clock, registers IIO, and enables runtime autosuspend. A raw read resumes the device, locks, starts a one-shot normal conversion for the requested channel, waits for completion, reads the 12-bit result, unlocks, and autosuspends.

## State and persistence
The driver stores no user settings. Hardware state includes calibration results, AD clock selection, interrupt masks, channel mask, and power state. Runtime suspend powers the ADC down; runtime resume powers it up without rerunning calibration.

## Dependencies and integration points
It integrates with platform/OF `nxp,imx93-adc`, common clock, regulators, IRQs, Linux completions, runtime PM, and direct-mode IIO.

## Risks
- The code uses IRQ index 2 specifically; bindings must provide that conversion IRQ.
- Calibration timeout message says "2 min" although the timeout argument is 2 seconds.
- `pm_runtime_get_sync()` results are not checked before MMIO access.
- Unexpected interrupt bits return `IRQ_NONE` after clearing them, which can affect shared IRQ diagnostics.

## Test signals
Test calibration success/failure paths, channel conversions on all eight channels, EOC/ECH interrupt ack, runtime PM autosuspend/resume, regulator-derived scale, and removal while runtime PM is active.
