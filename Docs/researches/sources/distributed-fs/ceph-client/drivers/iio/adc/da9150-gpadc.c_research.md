# sources/distributed-fs/ceph-client/drivers/iio/adc/da9150-gpadc.c

## Purpose
This Dialog DA9150 GPADC driver exposes GPIO, USB/battery/system voltage, bus current, battery temperature, and junction temperature measurements through IIO. It is a platform child of the DA9150 MFD and provides default IIO maps consumed by the DA9150 charger driver.

## Important APIs, Types, And Functions
`struct da9150_gpadc` stores the parent DA9150 device, local device pointer, mutex, and completion. `da9150_gpadc_irq()` completes conversions. `da9150_gpadc_read_adc()` selects a hardware mux channel, waits briefly for completion, reads result/status bytes, and assembles a 10-bit result. `da9150_gpadc_read_processed()`, `da9150_gpadc_read_scale()`, and `da9150_gpadc_read_offset()` implement channel conversions. `da9150_gpadc_read_raw()` is the IIO callback.

## Control Flow
Probe gets the parent `struct da9150`, initializes mutex/completion, requests named IRQ `GPADC`, registers IIO maps for charger channels, fills direct-mode IIO metadata, and registers the device. Reads validate channel number, then either perform processed/raw conversion or return scale/offset. `da9150_gpadc_read_adc()` locks, writes `DA9150_GPADC_MAN` with enable and mux selection, clears stale completion with `try_wait_for_completion()`, waits up to 5 ms, bulk-reads result registers, unlocks, checks the RUN bit for timeout, then combines LSB/MSB fields.

## State And Persistence
State is per-device and volatile. Completion objects can retain stale signals, explicitly consumed before each conversion. No remove callback is needed because all resources are devm-managed. Hardware conversion configuration is written per read.

## Dependencies And Integration Points
The driver depends on DA9150 MFD core/register helpers, platform named IRQ `GPADC`, IIO core, IIO machine maps, and charger consumers using map names `CHAN_IBUS`, `CHAN_VBUS`, `CHAN_TJUNC`, and `CHAN_VBAT`.

## Risks And Test Signals
Risks include ignoring the return value of `wait_for_completion_timeout()` and relying on the RUN bit for timeout detection, very short 5 ms wait budget, channel pairs with underscore hardware IDs, and mixed semantics where RAW and PROCESSED both call the processed helper for many channels. Test signals include timeout logging with RUN bit set, correct conversion formulas for GPIO/IBUS/VBUS/VSYS, scale/offset only for VBAT and junction temperature channels, and default charger map registration.
