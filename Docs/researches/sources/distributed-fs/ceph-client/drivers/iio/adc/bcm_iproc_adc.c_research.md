# sources/distributed-fs/ceph-client/drivers/iio/adc/bcm_iproc_adc.c

## Purpose
This driver exposes the Broadcom iProc static ADC as an eight-channel direct-mode IIO voltage device. The ADC shares register space and an interrupt line with touchscreen IP, so the driver uses syscon/regmap and shared IRQ filtering. Reads are snapshot conversions per channel with completion signaled by per-channel watermark interrupts.

## Important APIs, Types, And Functions
`struct iproc_adc_priv` holds the syscon regmap, ADC clock, mutex, IRQ number, selected channel/value, and completion. `iproc_adc_enable()` powers LDO/ADC/bandgap, enables the controller, and clears channel interrupt masks/status. `iproc_adc_do_read()` performs the snapshot conversion sequence. `iproc_adc_interrupt_thread()` filters shared interrupts and wakes the threaded handler only for ADC channel bits; `iproc_adc_interrupt_handler()` reads FIFO status/data and completes pending reads. `iproc_adc_read_raw()` exposes raw and fixed scale.

## Control Flow
Probe allocates the IIO device, initializes mutex/completion, looks up the `adc-syscon` regmap, gets the `tsc_clk`, gets the shared IRQ, disables AUXIN scan, requests a threaded shared IRQ, enables the clock, powers/configures the ADC, fills the IIO metadata, and registers the device. A raw read locks the mutex, records the channel, clears pending ADC/AUX status, configures the selected channel for snapshot mode with one round and watermark one, enables the per-channel watermark interrupt and top-level interrupt mask, retries the top-level mask write if hardware does not latch it, then waits up to two seconds for completion. On success it returns the low 16 bits of channel data; on failure it disables and clears interrupt state and dumps registers.

## State And Persistence
State is volatile: current channel/value and completion are used for a single in-flight read, protected by the mutex. Hardware power/controller state is enabled at probe and disabled at remove. No runtime PM is implemented, so the ADC clock remains prepared while bound.

## Dependencies And Integration Points
The driver depends on platform/OF compatible `brcm,iproc-static-adc`, syscon regmap via `adc-syscon`, the `tsc_clk` clock, shared IRQs, completions, IIO core, and regmap bit helpers. It provides eight `IIO_VOLTAGE` channels named `adc0` through `adc7` with scale `1800 / 2^10`.

## Risks And Test Signals
Risks include shared IRQ misclassification, stale channel data if completion arrives after timeout, interrupt mask write unreliability, no runtime clock gating, and a suspicious macro typo in `IPROC_ADC_CHANNEL_FULL_INTR_MASK` referencing `IPROC_ADC_IPROC_ADC_CHANNEL_FULL_INTR` though it is unused. Test signals include successful syscon lookup, read timeout cleanup, register dump on failure, IRQ filter returning `IRQ_NONE` for touchscreen-only events, raw reads on all eight channels, and scale reporting as fractional-log2.
