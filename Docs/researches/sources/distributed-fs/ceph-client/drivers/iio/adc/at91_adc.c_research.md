# sources/distributed-fs/ceph-client/drivers/iio/adc/at91_adc.c

## Purpose
This is the older Atmel AT91 ADC driver for AT91SAM9260, AT91SAM9RL, AT91SAM9G45, AT91SAM9X5, and SAMA5D3-style ADC blocks. It exposes board-selected voltage channels through IIO direct reads and, when touchscreen support is not enabled, IIO triggered buffers and IIO triggers. On SoCs with touchscreen support it can instead register an input device and reserve ADC channels for 4-wire or 5-wire touch reporting.

## Important APIs, Types, And Functions
`struct at91_adc_caps` is the central compatibility table: it describes touchscreen availability, TSMR support, filtering/sensitivity, startup tick calculation, channel count, resolution choices, trigger descriptors, and register offsets/masks. `struct at91_adc_state` keeps clocks, channel mask, IRQ, selected channel, conversion waitqueue, trigger array, vref, resolution, touchscreen configuration, and cached touchscreen coordinates.

The main functions are `at91_adc_probe()`, `at91_adc_remove()`, `at91_adc_read_raw()`, `at91_adc_channel_init()`, `at91_adc_trigger_init()`, `at91_adc_configure_trigger()`, `at91_adc_trigger_handler()`, `at91_adc_rl_interrupt()`, `at91_adc_9x5_interrupt()`, `at91_ts_hw_init()`, `at91_ts_register()`, and suspend/resume callbacks. Startup timing is abstracted by `calc_startup_ticks_9260()` and `calc_startup_ticks_9x5()`.

## Control Flow
Probe reads device-tree properties for channel mask, sleep mode, startup time, sample-hold time, vref, optional external triggers, optional low-resolution mode, and optional touchscreen wiring/pressure threshold. It resets the ADC, disables all IRQs, requests the correct IRQ handler based on TSMR support, enables both clocks, calculates prescaler/startup/sample-hold mode register fields, builds dynamic IIO channel specs from `atmel,adc-channels-used` minus channels reserved for touch, initializes waitqueue/mutex, then either sets up IIO triggered buffers and triggers or registers/configures the input touchscreen device. Finally it registers the IIO device.

Direct raw reads serialize on `st->lock`, enable the requested channel and EOC IRQ, start conversion, wait up to one second for the IRQ path to set `done`, then disables channel/IRQ and returns the captured value or timeout. Triggered buffer setup writes the trigger value, enables all active channels, enables DRDY, and allocates a scan buffer. On DRDY, `handle_adc_eoc_trigger()` either polls the IIO trigger for buffered capture or completes a direct conversion. The poll handler reads active channel registers, pushes the timestamped scan, acknowledges DRDY via `LCDR`, and reenables the IRQ.

Touchscreen handling has two IRQ implementations. The older AT91RL path toggles pen/NOPEN IRQs, period triggers, and debouncing in `MR`, discards the first buffered measurement, and reports previous coordinates through input events. The 9x5/TSMR path enables pen/NOPEN and X/Y/pressure ready IRQs, starts periodic sampling, validates pen contact through `PENS`, calculates X/Y/pressure, and reports `ABS_X`, `ABS_Y`, `ABS_PRESSURE`, and `BTN_TOUCH`.

## State And Persistence
No persistent storage is used. State lives in `struct at91_adc_state` and in hardware registers. `channels_mask` is derived from DT and modified to reserve touch channels. Direct conversions use `done`, `last_value`, and `chnb`; buffer mode uses allocated `st->buffer`; touchscreen mode tracks sample period, pressure threshold, debounce exponent, previous coordinates, and a flag for delayed reporting. Suspend only selects pinctrl sleep state and disables `clk`; resume reenables it and restores default pinctrl, without a full hardware reinitialization.

## Dependencies And Integration Points
The driver integrates with OF platform devices matching `atmel,at91sam9260-adc`, `atmel,at91sam9rl-adc`, `atmel,at91sam9g45-adc`, `atmel,at91sam9x5-adc`, and `atmel,sama5d3-adc`. It uses IIO core, triggered buffers, IIO trigger APIs, input subsystem for touchscreen mode, clocks, pinctrl sleep/default states, IRQs, waitqueues, and DT properties. The vref is supplied as a DT millivolt property rather than a regulator.

## Risks And Test Signals
Risks include divergence between SoC register maps, DT misconfiguration of channel masks or vref, lack of regulator-based vref validation, trigger cleanup with sparse trigger arrays, direct reads racing with buffers because direct mode is not explicitly claimed, touchscreen mode disabling ADC triggered-buffer support entirely, and limited suspend/resume restoration. Test signals include probe failure for missing required DT properties, correct channel reservation for 4-wire and 5-wire touch, raw-read timeout behavior, trigger registration only when external triggers are allowed, buffer scans across active channel masks, pen/NOPEN event sequencing on both IRQ variants, and resolution/scale correctness for lowres/highres configurations.
