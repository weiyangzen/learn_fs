# sources/distributed-fs/ceph-client/drivers/hwmon/gl518sm.c

## Purpose
`gl518sm.c` supports the Genesys Logic GL518SM hardware monitor over SMBus/I2C. It exposes voltage limits and inputs, fan tachometers and divisors, temperature limits, alarms, and beep controls through legacy sysfs attribute groups.

## Important APIs, Types, and Functions
`struct gl518_data` holds the I2C client, chip revision, attribute groups, update mutex, cache validity timestamp, register mirrors for voltages/fans/temp/alarms/beeps, and an `alarm_mask`. `gl518_read_value()` and `gl518_write_value()` hide the chip's mixed byte/word register format and swapped word convention. `gl518_update_device()` is the cache refresh routine. Macro-generated `show()` and `set()` handlers implement most sysfs files; hand-written handlers cover fan RPM/divisor behavior and per-bit alarms/beeps. `gl518_detect()`, `gl518_init_client()`, and `gl518_probe()` implement I2C autodetection, chip startup, and hwmon registration.

## Control Flow
The I2C core scans addresses `0x2c` and `0x2d`, requiring SMBus byte and word operations. Detection checks chip ID, config reset bit, and revision (`0x00` or `0x80`). Probe allocates state, records revision as `gl518sm_r00` or `gl518sm_r80`, initializes the chip, chooses base attributes plus extra voltage-input attributes for revision `0x80`, and registers with `devm_hwmon_device_register_with_groups()`. Reads call `gl518_update_device()`, which refreshes the cache at most every 1.5 seconds. Stores convert user values to register encodings, update the cached field, and write hardware under `update_lock`.

## State and Persistence
The driver caches register values in RAM; hardware threshold, fan divisor, fan auto, beep, and mask writes persist in the chip until changed or reset. Revision `0x00` cannot read some voltage inputs, so those sysfs input attributes are intentionally omitted. Fan minimum writes also mutate `alarm_mask` so disabled fan alarms stop contributing to alarm/beep reporting.

## Dependencies and Integration Points
It uses the I2C hwmon class scanning path (`I2C_CLASS_HWMON`), `hwmon-sysfs` sensor attributes, standard mutex/jiffies cache patterns, and the hwmon core group registration API. User space sees conventional lm-sensors style attributes rather than modern `hwmon_chip_info`.

## Risks
Read and write helpers do not uniformly handle negative SMBus errors in cache population, so bus faults can be reflected as bogus cached byte values. Several read-modify-write paths can overwrite concurrent hardware changes outside this driver. The chip's old revision limitations mean missing input attributes are expected and should not be treated as probe failure. Fan divisor changes do not rescale minimum registers automatically.

## Test Signals
Test by SMBus detection on valid and invalid addresses, sysfs mode/attribute presence by revision, voltage/temp/fan conversions at clamp edges, fan minimum zero masking alarm bits, invalid fan divisors returning `-EINVAL`, and cache refresh cadence around the 1.5 second window.
