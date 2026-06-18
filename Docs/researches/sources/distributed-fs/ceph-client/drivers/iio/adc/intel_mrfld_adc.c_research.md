# sources/distributed-fs/ceph-client/drivers/iio/adc/intel_mrfld_adc.c

## Purpose
`intel_mrfld_adc.c` is the IIO ADC driver for the Intel Merrifield Basin Cove PMIC. It exposes voltage, resistance, current, and temperature channels and maps them to battery and thermal PMIC consumers.

## Important APIs, types, and functions
- `struct mrfld_adc` stores the PMIC regmap, completion, and mutex.
- `mrfld_adc_requests` maps IIO channel index to PMIC ADC request bits.
- `mrfld_adc_single_conv()` clears pending ADC IRQ state, waits for GPADC not busy, writes request plus IRQ enable, waits for threaded IRQ completion, bulk-reads the result, then re-masks IRQs.
- `mrfld_adc_thread_isr()` completes conversions.
- `mrfld_adc_read_raw()` serializes raw conversions through `lock`.
- Probe registers default IIO maps for `bcove-battery` and `bcove-temp`.

## Control flow
Probe gets the parent PMIC regmap, allocates IIO state, initializes completion and mutex, requests a shared threaded IRQ, installs channel table and direct mode, registers IIO maps, and registers the device. Every raw read runs one PMIC conversion request and waits up to one second.

## State and persistence
The driver has only volatile completion and lock state. Hardware state includes PMIC IRQ masks, GPADC request bits, and result registers. It clears and restores interrupt mask bits around each conversion; no user configuration persists.

## Dependencies and integration points
It depends on Intel Basin Cove MFD register definitions, regmap, platform IRQ, IIO maps, completions, and IIO direct-mode ABI.

## Risks
- The request table and channel table must remain in exact index alignment.
- IRQ mask restoration uses broad `0xff` update values, which assumes existing PMIC mask semantics.
- On timeout or read failure the cleanup still re-masks interrupts, but conversion hardware may remain in an unknown state until PMIC clears busy.

## Test signals
Verify all nine channel request mappings, busy polling timeout, IRQ completion, big-endian result decoding, IIO maps, and concurrent reads through the mutex.
