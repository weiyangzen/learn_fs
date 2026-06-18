# sources/distributed-fs/ceph-client/drivers/iio/adc/stmpe-adc.c

Purpose: IIO direct-mode ADC and temperature driver for the STMPE811 MFD. It exposes enabled voltage channels plus one processed temperature channel, using STMPE MFD register helpers and conversion-completion interrupts.

Important APIs/types/functions: `struct stmpe_adc` stores the parent `stmpe`, mutex, channel table, completion, active channel, and latest value. Main functions are `stmpe_read_voltage()`, `stmpe_read_temp()`, `stmpe_read_raw()`, `stmpe_adc_isr()`, channel descriptor helpers, `stmpe_adc_init_hw()`, probe, and resume.

Control flow: probe requests ADC and optional temperature IRQs, builds the channel table from `st,norequest-mask`, initializes the ADC block and common STMPE811 ADC state, enables ADC interrupts for requested channels, clears stale status, and registers the IIO device. Voltage reads select one channel in `ADC_CAPT` and wait for its interrupt. Temperature reads write `TEMP_CTRL` to start one conversion and wait for the temperature IRQ path. The ISR verifies the relevant channel status, reads the big-endian data register, clears ADC status when needed, stores the value, and completes the waiter.

State and persistence: runtime state is the active channel, completion, and latest raw value. Hardware state persists in STMPE ADC block enable, ADC control registers initialized by the MFD helper, ADC interrupt enable/status, and temperature threshold/control registers. Resume reinitializes hardware but does not rebuild channels.

Dependencies and integration: depends on `linux/mfd/stmpe.h`, platform IRQ names `STMPE_ADC` and `STMPE_TEMP_SENS`, OF property parsing, IIO direct-mode read callbacks, and STMPE parent-provided block enable/reg access functions.

Risks: direct reads require interrupts; timeouts clear ADC status only for voltage channels. `norequest-mask` controls which ADC inputs are exposed and interrupt-enabled, so bad firmware can hide channels. Temperature conversion uses threshold interrupt behavior by programming zero threshold. The `clk` field is unused.

Test signals: probe with and without temp IRQ, `st,norequest-mask` channel exclusion, voltage raw reads for each enabled channel, temperature processed conversion, ADC timeout handling, irrelevant IRQ returning `IRQ_NONE`, 10-bit versus 12-bit scale, and resume reinitialization.
