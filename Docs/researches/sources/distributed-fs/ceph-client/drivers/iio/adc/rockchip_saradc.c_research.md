# sources/distributed-fs/ceph-client/drivers/iio/adc/rockchip_saradc.c

Rockchip SARADC IIO driver supporting several SoC variants with v1 and v2 register layouts, direct reads, triggered-buffer sampling, regulator-based scale, clock/reset management, and suspend/resume.

`struct rockchip_saradc_data` selects channel table, clock rate, and variant operations for start/read/power-down. `struct rockchip_saradc` stores MMIO, clocks, completion, VREF regulator, mutex, reset, last conversion value/channel, and regulator notifier. Core paths are `rockchip_saradc_start_v1/v2`, `rockchip_saradc_read_v1/v2`, `rockchip_saradc_conversion`, `rockchip_saradc_read_raw`, `rockchip_saradc_isr`, `rockchip_saradc_trigger_handler`, `rockchip_saradc_probe`, and PM ops.

Probe matches variant data, maps MMIO, obtains optional reset and IRQ, enables VREF and clocks, sets ADC clock rate, installs a triggered buffer, registers a regulator voltage-change notifier, initializes mutex, and registers IIO. Direct raw reads lock, start a conversion, wait up to 100 ms for ISR completion, return `last_val`, and power down on error. ISR reads and masks the result, powers down, and completes. Triggered buffer scans active channels sequentially under the same mutex and pushes timestamped samples.

Runtime state includes current VREF microvolts, last channel/value, clocks/regulator enabled state, and variant function table. VREF changes update `uv_vref` through notifier. Suspend disables clocks and regulator; resume reenables them. Dependencies include MMIO/IRQ resources, `apb_pclk` and `saradc` clocks, `vref`, optional `saradc-apb` reset, triggered buffer framework, and Rockchip DT compatibles.

Risks include scan latency scaling with active channels, resume not explicitly restoring clock rate, notifier event-data assumptions, v2 lacking an explicit power-down callback, and shared `last_val/last_chan` state. Test all compatibles, v1/v2 paths, timeout cleanup, triggered buffers, VREF notifier, suspend/resume, optional reset, max-channel guard, and clock/regulator unwinding.
