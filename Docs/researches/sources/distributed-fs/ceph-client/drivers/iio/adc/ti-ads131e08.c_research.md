# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads131e08.c

Purpose: SPI IIO driver for TI ADS131E04/E06/E08 simultaneous-sampling delta-sigma ADCs with direct reads, triggered buffers, per-channel DT configuration, data-rate control, PGA gain, mux, and reference setup.

Important APIs/types/functions: `struct ads131e08_state` stores chip info, SPI, trigger, clock, optional external `vref`, per-channel config, data rate, timing delays, completion, and DMA-safe transfer buffers. `ads131e08_alloc_channels()` parses child nodes with `reg`, `ti,gain`, and `ti,mux`. `ads131e08_initial_config()` resets, exits continuous mode, programs data rate/reference/channel registers, powers unused channels down, and performs offset calibration. `ads131e08_read_raw()`, `ads131e08_write_raw()`, `ads131e08_trigger_handler()`, and `ads131e08_interrupt()` expose IIO behavior.

Control flow: probe obtains match data, allocates channels from firmware children, requests a falling-edge DRDY IRQ, registers an own IIO trigger, configures a triggered buffer, enables optional external vref and required `adc-clk`, derives SPI decode/reset delays from the clock, then applies initial configuration. Direct reads claim direct mode, issue START, wait up to the settling window for completion, read an RDATA frame, stop conversion, and sign-extend the selected channel. Buffered reads either consume own-trigger DRDY data or poll manually for external triggers.

State and persistence: `data_rate`, `readback_len`, `vref_mv`, and `channel_config` mirror hardware register state. Calibration is requested at init but not persisted by the driver. Runtime results reside in `rx_buf` and `tmp_buf`; no nonvolatile state is written.

Dependencies and integration: SPI, regulator, clock, IIO trigger/triggered buffer, firmware child nodes, and IRQ. Compatible strings cover `ti,ads131e04`, `ti,ads131e06`, and `ti,ads131e08`.

Risks: missing IRQ or missing channel children prevents probe; invalid firmware gain/mux/vref values reject the device; 32/64 kSPS use 16-bit data packed into a fixed 24-bit scan format with special sign-extension logic. Test signals include sampling-frequency availability, scale with internal/external vref, buffered scan packing at all rates, debugfs register access, and offset-calibration timing.
