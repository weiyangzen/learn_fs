# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1298.c

Purpose: SPI IIO ADC driver for the TI ADS1298 family, including ADS129x/ADS129xR identification, direct single-channel reads, and software-buffered sampling driven by DRDY interrupts.

Important APIs/types/functions: `struct ads1298_private` holds SPI, regmap, regulators, optional clock, trigger/buffer state, DMA-safe buffers, completion, and a DRDY/SPI busy counter. `ads1298_probe()` powers supplies, resets the chip, initializes regmap and IIO buffering, requests the DRDY IRQ, and registers the IIO device. `ads1298_read_raw()`, `ads1298_write_raw()`, `ads1298_update_scan_mode()`, `ads1298_buffer_postenable()`, `ads1298_buffer_predisable()`, and `ads1298_interrupt()` form the core IIO flow. `ads1298_reg_read()` and `ads1298_reg_write()` back a maple-cached regmap.

Control flow: probe asserts reset, enables `vref` if external, enables `avdd`, configures SDATAC, reads ID to choose name/channel count, enables test/reference config, prepares the `RDATA` SPI message, then registers a kfifo buffer. Direct reads claim direct mode, power the requested channel, enable single-shot mode, issue START, wait on completion from DRDY/SPI completion, then decode signed 24-bit data. Buffered mode powers channels according to the scan mask, starts continuous conversions, and uses DRDY to schedule asynchronous SPI reads.

State and persistence: hardware configuration lives in chip registers and regmap cache; runtime sample state is in `rx_buffer`, `bounce_buffer`, completion, and `rdata_xfer_busy`. No disk persistence. Regulator enables and buffer state are undone through devm actions and buffer predisable.

Dependencies and integration: depends on SPI, regmap, GPIO reset, regulators, optional clock, IIO kfifo buffer, and IRQ. DT compatible is `ti,ads1298`; SPI id is `ads1298`.

Risks: `rdata_xfer_busy > 2` means samples were lost during SPI overrun; direct reads rely on a 50 ms DRDY timeout; register access is forced to slow SPI timing; IRQ is mandatory. Test signals include probe/init failures, `CMD_START` errors, direct read timeout, sample-rate/scale sysfs values, debugfs register access, and buffered scans under high DRDY rates.
