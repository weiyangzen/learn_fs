# sources/distributed-fs/ceph-client/drivers/iio/common/ms_sensors/ms_sensors_i2c.h

Purpose: shared private header for Measurement Specialties I2C helper users. It defines common device-state structs and function prototypes exported by `ms_sensors_i2c.c`.

Important APIs, types, and functions: `struct ms_ht_dev` stores client, mutex, and resolution index for humidity/temperature devices. `struct ms_tp_hw_data` describes PROM length and maximum resolution index for temperature/pressure devices. `struct ms_tp_dev` stores client, mutex, hardware data, PROM coefficient array, and resolution index. Prototypes cover reset, PROM word reads, ADC conversion, serial read, resolution/heater/battery helpers, HT readings, PROM reading, and compensated temperature/pressure readings.

Control flow: concrete drivers initialize one of these structs, often during probe, call reset/read PROM or serial helpers, and use read helpers from IIO callbacks under the helper-managed locks.

State and persistence: the structs are caller-owned runtime state. PROM coefficients are cached in RAM after validation; sensor config bits persist in the device.

Dependencies and integration: includes I2C and mutex headers. It is internal to kernel drivers, not UAPI, and pairs with namespace exports from the C file.

Risks and test signals: the declared `ms_sensors_show_serial()` lacks a definition in the paired source file, so dependency analysis should verify no unresolved user. Tests should compile all include users, verify struct field initialization before helper calls, and ensure PROM array length matches `MS_SENSORS_TP_PROM_WORDS_NB`.
