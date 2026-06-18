# sources/distributed-fs/ceph-client/drivers/iio/adc/sun4i-gpadc-iio.c

Purpose: IIO GPADC and thermal-sensor driver for older Allwinner A10/A13/A31 MFD devices and DT-only sun8i-a33 THS. It exposes voltage ADC channels and optionally a temperature channel/thermal zone, using runtime PM autosuspend to keep the thermal sampling cadence valid.

Important APIs/types/functions: `struct gpadc_data` contains SoC-specific temperature calibration and channel-select fields. `struct sun4i_gpadc_iio` stores regmap, completions, IRQ ids, ignore flags, calibration data, mutex, thermal zone, and MFD/DT mode flags. Main functions are `sun4i_prepare_for_irq()`, `sun4i_gpadc_read()`, `sun4i_gpadc_read_raw()`, FIFO/temp IRQ handlers, runtime PM callbacks, thermal `get_temp`, MFD/DT probe helpers, and remove.

Control flow: probe allocates IIO, selects DT-only or MFD setup, initializes regmap and channel tables, requests MFD virtual IRQs with `IRQF_NO_AUTOEN`, enables runtime PM autosuspend, optionally registers a thermal zone, and registers IIO. Voltage reads runtime-resume the parent, flush FIFO, switch to ADC/touchscreen mode and channel, enable the FIFO IRQ, wait for completion, copy `adc_data`, then disable IRQ and autosuspend. Temperature reads either read `TEMP_DATA` directly in no-IRQ DT mode or wait on the periodic temp IRQ. Runtime resume programs ADC clock/acquisition/filter and starts periodic temperature sampling; suspend disables ADC and temp sensor.

State and persistence: software state includes last sampled ADC/temp values, completion, interrupt numbers, ignore flags for request-time races, SoC calibration constants, and thermal registration state. Hardware state persists in CTRL0/CTRL1/CTRL3/TPR mode, channel-select, FIFO trigger/flush, temp period, and MFD interrupt routing.

Dependencies and integration: depends on `linux/mfd/sun4i-gpadc.h`, regmap, regmap IRQ controller, runtime PM, IIO maps for hwmon, thermal-of, platform IDs for MFD children, and OF compatible `allwinner,sun8i-a33-ths`.

Risks: mode switching requires fixed 10 ms and 100 ms delays; conversion latency can be high when thermal support is enabled. MFD children may lack their own OF node, so thermal registration intentionally uses the parent device. IRQs are enabled only around reads and races are handled by atomic ignore flags. Error paths after runtime PM setup must unregister IIO maps.

Test signals: MFD and DT-only probe paths, voltage raw reads on four channels, temp raw/scale/offset reads, thermal zone callbacks, IRQ-disabled polling/no-IRQ temp path, runtime autosuspend/resume timing, FIFO flush, channel switch settling delays, and cleanup of IIO maps on remove.
