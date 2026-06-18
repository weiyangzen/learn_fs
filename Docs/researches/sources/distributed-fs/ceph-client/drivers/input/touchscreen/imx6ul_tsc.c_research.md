# sources/distributed-fs/ceph-client/drivers/input/touchscreen/imx6ul_tsc.c

## Purpose
`imx6ul_tsc.c` is a platform driver for the Freescale/NXP i.MX6UL resistive touchscreen controller and its coupled ADC. It configures ADC calibration/hardware trigger mode, TSC measurement timing, pen-detect GPIO checks, and reports single-touch ABS_X/ABS_Y events.

## Important APIs, types, and functions
- `struct imx6ul_tsc` stores device/input, TSC and ADC MMIO bases, TSC/ADC clocks, XNUR pen-detect GPIO, timing/filter properties, and an ADC calibration completion.
- `imx6ul_adc_init()` configures 12-bit ADC mode, clock source/divider, optional averaging, calibration interrupt, starts calibration, waits for completion, checks failure, and switches ADC to hardware trigger.
- `imx6ul_tsc_channel_config()` programs ADC channels around a documented TSC channel workaround.
- `imx6ul_tsc_set()` writes TSC measurement delay, deglitch, precharge, interrupt enables, and starts sense detection.
- `imx6ul_tsc_disable()` disables TSC and ADC conversion.
- `tsc_wait_detect_mode()` polls the TSC state machine before reading pen-detect GPIO.
- `tsc_irq_fn()` clears TSC status, restarts sense detection, extracts X/Y measurement, decides touch/release using detect mode and XNUR GPIO, and reports input.
- `adc_irq_fn()` completes ADC calibration when conversion complete is signaled.
- `imx6ul_tsc_probe()` maps resources, gets clocks/GPIO/IRQs, reads DT timing properties, configures input, and registers the platform device.

## Control flow
Probe allocates state/input, gets XNUR GPIO, maps TSC and ADC resources, gets clocks, requests TSC and ADC IRQs, reads `measure-delay-time`, `pre-charge-time`, `touchscreen-average-samples`, and `debounce-delay-us`, computes deglitch selection, registers input, and stores drvdata. Input open enables clocks and initializes ADC/TSC; close disables both. The TSC IRQ handles measurements and touch/release reporting. The ADC IRQ is only used to complete calibration during startup.

## State and persistence
State is runtime-only and mostly derived from DT. Hardware registers are reinitialized on input open and resume when the input device is enabled. No calibration persistence is stored by the driver beyond each ADC init cycle.

## Dependencies and integration points
The driver integrates with platform resources, MMIO, clocks, GPIO descriptors, OF properties, threaded TSC IRQ, hard ADC IRQ, completions, input open/close, and PM helpers.

## Risks
- ADC calibration depends on IRQ completion; IRQ ordering or missing ADC interrupt causes open to timeout.
- Debounce conversion depends on TSC clock rate and coarse threshold buckets; board DT values need validation.
- `tsc_wait_detect_mode()` may time out and then treats the contact as active, which can delay release reporting.
- Hardware workaround channel programming is SoC-specific and easy to break when refactoring.
- The driver supports only one host-style resistive touch, not multitouch or pressure reporting.

## Test signals
- Probe with valid and invalid `touchscreen-average-samples`, missing resources, missing clocks, and absent XNUR GPIO.
- Open/close tests should verify clock enable rollback, ADC calibration timeout/failure, and TSC/ADC disable.
- Hardware tests should validate X/Y extraction, release detection, debounce settings, precharge/measure timing, and suspend/resume while input is open.
