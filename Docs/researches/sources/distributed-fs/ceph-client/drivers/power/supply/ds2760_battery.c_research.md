# sources/distributed-fs/ceph-client/drivers/power/supply/ds2760_battery.c

Purpose: implements a 1-Wire DS2760 battery monitor/fuel-gauge driver. It exposes raw 1-Wire SRAM through a bin attribute and registers a battery power supply with voltage, current, charge, temperature, capacity, time-to-empty, and writable charge calibration properties.

Important APIs/types/functions: `struct ds2760_device_info` caches raw SRAM, converted readings, capacity estimates, charge status, power supply descriptor, monitor workqueue, and PM notifier. `w1_ds2760_io()` serializes 1-Wire read/write with the bus mutex. `ds2760_battery_read_status()` refreshes cached values and computes capacity. `ds2760_battery_update_status()` derives charging/full/discharging state.

Control flow: `w1_ds2760_add_slave()` allocates state, applies module parameters and OF overrides, writes PMOD/rated-capacity/current-accumulator values when requested, registers the battery, starts an ordered monitor workqueue, and registers a PM notifier. Reads use `cache_time` to avoid frequent full SRAM access, then convert raw register fields and interpolate active-full/empty capacity over temperature. External power changes reschedule a near-term monitor update.

State and persistence: cached readings live in memory. PMOD, rated capacity, active-full, and current-accumulator writes can be copied/recalled through DS2760 EEPROM blocks, so calibration changes persist in the pack. PM events force status unknown and refresh after resume.

Dependencies and integration: depends on the 1-Wire subsystem, W1 family registration, OF properties, module parameters, power-supply external supply detection, PM notifier chain, and bin sysfs attributes.

Risks and test signals: write paths directly program battery EEPROM and need careful validation. Error handling treats short 1-Wire reads as status read failure but some write helpers cannot know actual bytes written. Test cache expiration, full first read vs partial later reads, EEPROM writes, PMOD/device-tree overrides, external power status transitions, full-counter behavior, suspend/resume notifier behavior, and bin attribute bounds.
