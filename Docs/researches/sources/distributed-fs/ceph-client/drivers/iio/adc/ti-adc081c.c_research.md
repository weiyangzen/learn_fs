# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc081c.c

Purpose: I2C IIO driver for TI ADC081C/ADC101C/ADC121C single-channel ADCs. It supports direct reads and triggered buffering, with model-specific bit resolution and regulator-derived voltage scale.

Important APIs/types/functions: `struct adc081c` stores the I2C client, vref regulator, resolution bits, and an aligned scan buffer. `adc081c_read_raw()` handles raw and scale reads, `adc081c_trigger_handler()` pushes buffered samples, and `adc081c_probe()` validates SMBus word support, enables vref, sets channel metadata, and registers the triggered buffer.

Control flow: direct raw read performs `i2c_smbus_read_word_swapped()` from conversion register 0, masks 12 result bits, and right-shifts according to the model. Scale reads use `regulator_get_voltage()` and return mV divided by `2^bits`. The trigger handler reads the same conversion register and pushes the sample with a timestamp.

State and persistence: persistent state is minimal: model bit width, enabled vref regulator, I2C client, and scan storage. The ADC itself continuously provides conversion results from one register; no driver-side configuration is maintained.

Dependencies and integration: depends on SMBus word-data functionality, IIO direct/buffer/triggered-buffer APIs, regulator `vref`, OF/I2C/ACPI match tables, and `devm_add_action_or_reset()` for regulator disable.

Risks: triggered-buffer samples store the raw 12-bit register value without applying the direct-read right shift, relying on scan_type shift to describe layout. Probe fails without SMBus word support or vref. No locking is needed because there is no mutable bus command state, but direct and buffered reads can still contend on the adapter.

Test signals: all three model IDs, ACPI `ADC081C`, raw value shifts for 8/10/12-bit devices, vref scale, triggered buffer timestamped samples, missing regulator, SMBus functionality rejection, and regulator cleanup on probe failure.
