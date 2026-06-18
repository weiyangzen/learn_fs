# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-tsc2046.c

Purpose: SPI IIO ADC driver for TI TSC2046 touchscreen controller ADC mode, exposing eight 12-bit voltage channels with direct reads, triggered buffers, per-channel settling/oversampling, and a PENIRQ-driven rate-limited trigger state machine.

Important APIs/types/functions: `struct tsc2046_adc_priv` stores SPI, trigger/hrtimer state, scan buffers, group layout, per-channel configuration, timing, vref, and locks. `tsc2046_adc_read_one()` performs direct oversampled reads. `tsc2046_adc_update_scan_mode()` builds grouped transfer layout for active channels. `tsc2046_adc_timer()`, `tsc2046_adc_irq()`, `tsc2046_adc_reenable_trigger()`, and `tsc2046_adc_set_trigger_state()` implement the reusable IRQ trigger.

Control flow: probe validates max SPI frequency, forces SPI mode 0, reads optional external vref or uses internal 2500 mV, parses child-node settling/oversampling values, performs a dummy read to discover effective speed, allocates maximum scan buffers, requests a disabled IRQ, registers an own trigger and triggered buffer, then sets it as default. Direct reads allocate temporary transfer arrays, skip settling samples, average oversamples, and power down on the last sample. Buffered scans use prebuilt grouped commands and average each group before pushing.

State and persistence: scan layout and timing are rebuilt on scan-mask changes; trigger state tracks shutdown/standby/poll phases under spinlock. Per-channel settings come from firmware and are in memory only.

Dependencies and integration: SPI, regulator helper, IIO trigger/triggered buffer, hrtimer, IRQ, firmware child nodes. Compatible is `ti,tsc2046e-adc`.

Risks: IRQ line is affected by channel switching, requiring careful disable/reenable sequencing; oversized settling/oversampling can exceed one page; `scan_interval_us - time_per_scan_us` assumes scan time does not exceed interval despite warning. Test signals include direct reads with custom settling/oversampling, IRQ trigger enable/disable, timer transitions, buffer overflow sizing, and vref fallback.
