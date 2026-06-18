# sources/distributed-fs/ceph-client/drivers/macintosh/therm_adt746x.c

Purpose: controls ADT7460/ADT7467 thermal chips in iBook G4 and aluminum PowerBook G4 systems. It reads sensors, sets thermal limits, manages fan speed manually or automatically, and exposes legacy temperature attributes.

Important APIs and functions: `struct thermostat` stores I2C client, cached temperatures/limits, fan state, chip type, kthread, and legacy platform device. `read_reg()`/`write_reg()` implement byte I2C register access. `write_fan_speed()` and `write_both_fan_speed()` program manual or automatic fan modes. `monitor_task()` periodically reads sensors and calls `update_fans_speed()`. `thermostat_create_files()` creates old ABI sysfs attributes on a generated platform device. Probe/remove are I2C driver callbacks.

Control flow: module init optionally loads `i2c-powermac` and registers an I2C driver. Probe requires OF sensor parameter version 1, reads locations, determines chip type, reads config, sets default fan speed if unset, initializes ADT7460 if needed, lowers chip limits while storing originals, records PWM invert bits, starts fans or automatic mode, launches `kfand`, and creates sysfs files. Remove deletes files, stops the thread, restores original limits, returns fans to automatic mode, and frees state.

State and persistence: module parameters `limit_adjust`, `fan_speed`, and `verbose`; global sensor location strings; per-device thermostat state. Settings persist while module is loaded.

Dependencies and integration: depends on I2C, OF sensor properties, platform device creation for old ABI paths, freezer-aware kthread handling, and Apple thermal device-tree conventions.

Risks: global `fan_speed` and locations are shared across devices. I2C helper return values are not always checked by callers. Thermal policy is empirical and hardware-specific. Sysfs store paths use `simple_strtol()` and update global limits/fan speed without a thermostat-wide lock.

Test signals: probe on ADT7460 and ADT7467 nodes, sysfs attribute presence and values, fan speed transitions around limits with hysteresis, suspend/freezer behavior, removal restoring limits/automatic fans, module parameter effects, and I2C error handling.
