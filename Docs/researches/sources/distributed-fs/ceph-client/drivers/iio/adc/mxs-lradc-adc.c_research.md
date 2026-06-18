# sources/distributed-fs/ceph-client/drivers/iio/adc/mxs-lradc-adc.c

Purpose: this is the general-purpose ADC child driver for Freescale/NXP MXS LRADC MFD hardware on i.MX23 and i.MX28. It supports direct raw reads, die-temperature calculation, configurable input range through divide-by-two, IRQ-driven completion, and triggered buffered sampling through LRADC delay channel 0.

Important APIs, types, and functions: `struct mxs_lradc_adc` carries the parent LRADC descriptor, MMIO base, completion, spinlock, trigger, scale table, and per-channel divider bitmap. `mxs_lradc_adc_read_single()` claims direct mode, maps the requested physical channel into virtual channel 0, configures divide-by-two, starts conversion, waits up to one second for IRQ completion, and reads `LRADC_CH(0)`. `mxs_lradc_adc_read_temp()` subtracts channel 8 from channel 9. Buffer setup functions map active scan channels to LRADC slots and delay triggers. `mxs_lradc_adc_validate_scan_mask()` rejects touchscreen/touchbutton-reserved channels and too many mapped channels.

Control flow: probe maps the child memory resource, resets the block, requests all named IRQs, initializes an IIO trigger and triggered buffer, computes scale availability for both divider states, initializes delay channel 0 and temperature sensing, then registers IIO. IRQ handling either completes direct reads or polls the trigger for buffered mode.

State and persistence: runtime state includes selected divide-by-two bits, active buffered channel mapping, delay channel programming, and completion state. Remove unregisters IIO, stops delay channel 0, cleans up the buffer, and unregisters the trigger.

Dependencies and integration points: it integrates with `linux/mfd/mxs-lradc.h`, parent LRADC SoC metadata, OF IRQ mapping, STMP reset helpers, IIO triggered buffers, and sysfs scale-available attributes.

Risks: direct and buffered modes are mutually exclusive via `iio_device_claim_direct()`. IRQ mapping uses parent OF IRQ indexes and named platform IRQs, so DT mistakes fail probe. Buffered mode assumes LRADC virtual channel ordering matches active scan order. Reserved touchscreen/touchbutton channel checks are essential to avoid stealing channels from sibling functions.

Test signals: direct reads on all valid voltage channels, temperature raw/scale/offset, scale write and readback for divider states, buffer enable/disable with multiple scan masks, rejection of reserved channels, timeout when IRQ never completes, and remove cleanup of trigger/buffer/hardware delay state.
