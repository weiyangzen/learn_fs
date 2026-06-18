# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_therm.c

## Purpose
Thermal family driver for DS18S20, DS1822, DS18B20/GX20MH01, DS1825/MAX31850, and DS28EA00 devices. It exposes legacy W1 sysfs readings, configuration controls, optional bulk conversion, and hwmon temperature input.

## Important APIs, Types, and Functions
`struct w1_therm_family_converter` binds family-specific conversion, timing, resolution, write, and bulk-read capabilities. `struct w1_therm_family_data` stores ROM scratchpad cache, refcount, power mode, resolution, conversion state, conversion-time override, feature flags, and converter pointer. Core helpers include `convert_t()`, `read_scratchpad()`, `write_scratchpad()`, `copy_scratchpad()`, `recall_eeprom()`, `read_powermode()`, `trigger_bulk_read()`, and DS18x-specific conversion/resolution functions.

## Control Flow
Add allocates family data, finds converter, creates a master-level `therm_bulk_read` attribute once for bulk-capable devices, detects power mode and resolution, and initializes state. Normal reads either trigger conversion and read scratchpad or consume a pending bulk conversion. Strong pullup is used for parasite-powered conversion/copy when enabled. Sysfs controls manage resolution, alarm bytes, EEPROM save/restore, conversion-time override or measurement, and feature bits. DS28EA00 sequence reading performs chain-state commands across the bus.

## State and Persistence
Runtime per-slave state tracks power mode, resolution, conversion state, feature flags, and cached last scratchpad bytes. EEPROM save/restore and alarm/resolution writes affect device nonvolatile or scratchpad state. `bulk_read_device_counter` is global module state controlling the master-level bulk attribute.

## Dependencies and Integration Points
Depends on W1 reset/select/read/write, strong pullup, hwmon when reachable, sysfs device attributes, master/slave list traversal, and module family registration for five IDs.

## Risks and Test Signals
The driver has complex locking and refcounting because conversions sleep while devices can be removed. `reset_select_slave()` deliberately avoids `SKIP_ROM` to prevent collisions during early discovery. Feature interactions matter: polling completion is disabled with strong pullup parasite mode. Test sysfs compatibility (`w1_slave`, `temperature`, `ext_power`), hwmon reads, resolution changes, EEPROM commands, bulk-read states -1/0/1, parasite-powered devices, interrupted sleeps, DS28EA00 sequence reads, and module unload waiting for refcounts.
