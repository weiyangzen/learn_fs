<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl115_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl115_i2c.c

## Purpose
`mpl115_i2c.c` is the I2C bus wrapper for the MPL115A2 pressure/temperature sensor. It supplies SMBus register access callbacks to the shared MPL115 core.

## Important APIs, types, and functions
`mpl115_i2c_read()` uses `i2c_smbus_read_word_swapped()` for 16-bit register reads. `mpl115_i2c_write()` uses `i2c_smbus_write_byte_data()` to issue conversion commands. `mpl115_i2c_probe()` checks `I2C_FUNC_SMBUS_WORD_DATA`, fetches the I2C ID name, and calls `mpl115_probe()`.

## Control flow
The I2C driver binds to `mpl115`, verifies adapter functionality, and delegates device initialization to the common core. Runtime reads and writes are callback-driven through the ops table.

## State and persistence behavior
No wrapper-local state is kept. All calibration, PM, and IIO state lives in the common `mpl115_data` object.

## Dependencies and integration points
It integrates Linux I2C/SMBus with the `IIO_MPL115` core and attaches `mpl115_dev_pm_ops` to the driver. The expected 7-bit address is documented as `0x60`.

## Risks
The functionality check covers word data but not byte-data writes explicitly; most SMBus-capable adapters provide both but adapter edge cases should be tested. Endianness relies on the swapped SMBus helper matching the sensor register layout.

## Test signals
Probe with adapters missing word-data support, verify coefficient reads and conversion commands on MPL115A2 hardware, and run runtime PM tests through the common shutdown GPIO path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl115_i2c.c -->
