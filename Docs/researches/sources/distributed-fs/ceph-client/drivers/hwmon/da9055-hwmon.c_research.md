## sources/distributed-fs/ceph-client/drivers/hwmon/da9055-hwmon.c

### Purpose

`da9055-hwmon.c` is the hwmon child driver for the Dialog DA9055 PMIC. It exposes the PMIC ADC channels as Linux hwmon voltage inputs and a temperature input: VSYS, ADCIN1-3, and chip junction temperature. Voltage channels use the DA9055 continuous ADC registers, while junction temperature uses a manual ADC conversion and the PMIC trim offset.

### Important APIs, types, and functions

The central state is `struct da9055_hwmon`, which holds the parent `struct da9055`, a `hwmon_lock` for normal sysfs reads, an `irq_lock` around manual conversion, and a `completion` signaled by the ADC IRQ. `chan_mux[]` maps hwmon channel indices to DA9055 ADC mux values, and `input_names[]` provides labels. Important functions are `da9055_adc_manual_read()`, `da9055_auxadc_irq()`, `volt_reg_to_mv()`, `da9055_auto_ch_show()`, `da9055_tjunc_show()`, and `da9055_hwmon_probe()`.

### Control flow

Probe allocates state, initializes locks/completion, fetches parent MFD driver data, obtains the named `"HWMON"` IRQ, registers `da9055_auxadc_irq()`, and registers a static hwmon attribute group. Voltage reads enable one continuous ADC channel, sleep about 10 ms, read the result register, disable the channel, and convert raw values to millivolts. Junction temperature reads program a manual conversion, wait up to 500 ms for IRQ completion, read result high/low bytes, read `DA9055_REG_T_OFFSET`, and apply the trim-aware linear formula.

### State and persistence behavior

The driver keeps no measurement cache. Continuous ADC bits are enabled only during a voltage read and disabled on normal and error exits. Manual conversion state is serialized by `irq_lock`; normal sysfs voltage reads are serialized by `hwmon_lock`. Device resources are devm-managed.

### Dependencies and integration points

It depends on DA9055 MFD register helpers, platform-device IRQ resources, completions, mutexes, and hwmon sysfs registration. It integrates as the `"da9055-hwmon"` platform child and exports `in*_input`, `in*_label`, `temp1_input`, and `temp1_label`.

### Risks

The manual ADC path depends on completion/IRQ ordering; a stale completion would make a conversion appear complete early. Voltage reads must not leave auto mode enabled after errors. Temperature conversion uses signed integer arithmetic and should be reviewed for overflow/rounding if formulas change.

### Test signals

Validate probe with a DA9055 MFD, all expected hwmon files, repeated voltage reads with auto mode disabled afterward, manual temperature reads with IRQ delivery, timeout behavior when the ADC IRQ is absent, and register-error injection.
