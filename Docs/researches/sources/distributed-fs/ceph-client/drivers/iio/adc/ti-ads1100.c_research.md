# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1100.c

Purpose: I2C IIO driver for the single-channel ADS1100/ADS1000 ADC. It provides raw reads, gain-derived scale, sample-frequency control where supported, vdd regulator management, and runtime PM autosuspend.

Important APIs/types/functions: `struct ads1100_data` stores I2C client, vdd regulator, mutex, available scale table, cached config byte, and a flag for data-rate support. Important functions are `ads1100_set_config_bits()`, `ads1100_get_adc_result()`, scale/data-rate setters, availability/read/write callbacks, setup, cleanup actions, probe, and runtime PM callbacks.

Control flow: probe enables vdd, writes continuous 8 SPS setup, reads back conversion/config bytes to cache config and detect ADS1100 data-rate support, registers cleanup to return to single-shot and disable regulator, computes available scales from vdd, enables runtime PM, and registers IIO. Raw read claims direct mode, runtime-resumes, receives the 16-bit conversion, autosuspends, left-aligns the value according to resolution implied by data rate, and sign-extends. Scale writes convert requested fractional scale into PGA gain bits; sample-frequency writes update DR bits only if the chip supports them.

State and persistence: persistent state is cached config, gain/data-rate bits, vdd regulator state, scale table, and data-rate capability. Hardware state persists in the one-byte config register and continuous versus single-shot mode. Runtime suspend powers down conversion and disables vdd; resume re-enables vdd and writes continuous mode.

Dependencies and integration: depends on I2C master send/recv, regulator `vdd`, runtime PM, IIO direct callbacks and available-list ABI, firmware match IDs, and cleanup guard mutex style.

Risks: ADS1000-like devices may not support data-rate changes and are detected by readback behavior. Scale-setting arithmetic assumes vdd between 2.7 V and 5 V and scale below 1. Runtime power cycling relies on cached config being rewritten when continuous mode changes. `ads1100_set_config_bits()` treats successful `i2c_master_send()` byte counts as success without checking exact count.

Test signals: ADS1100 and ADS1000 probing, data-rate capability detection, raw reads at each data rate, scale available list from vdd, gain writes, runtime suspend/resume regulator transitions, single-shot cleanup on detach, and I2C error handling.
