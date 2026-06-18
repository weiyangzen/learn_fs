# sources/distributed-fs/ceph-client/drivers/hwmon/ibmaem.c

## Purpose

`ibmaem.c` is a legacy hwmon driver for IBM System x Active Energy Manager firmware. It discovers AEM firmware instances through IPMI SMI watcher callbacks and exposes each instance as a platform-backed hwmon device with energy, computed average power, temperature, and power-cap attributes. AEM1 exposes one energy/power meter; AEM2 exposes two energy meters, two computed power meters, two exhaust temperatures, and several power-cap registers.

## Important APIs, Types, and Functions

`struct aem_ipmi_data` owns the IPMI user, target address, completion, transmit message, receive buffer pointer, and BMC device. `struct aem_data` is the per-AEM-instance state: hwmon/platform devices, mutex, refresh validity, firmware version/module handle, IPMI state, cached energy/power-period/temp/power-cap values, dynamic sysfs attributes, and the update callback. Packed request/response structures model AEM find-firmware, find-instance, and read-register commands. `aem_init_ipmi_data()`, `aem_send_message()`, and `aem_msg_handler()` are the IPMI transport layer. `aem_read_sensor()` is the central typed register read helper. `aem_init_aem1_inst()` and `aem_init_aem2_inst()` allocate devices and attributes; `aem_register_bmc()` probes both protocol generations for each BMC. Sysfs show/store functions implement `name`, `version`, `energy*_input`, `power*_average`, `power*_average_interval`, temperatures, and power-cap values.

## Control Flow

Module init registers a platform driver shell and an IPMI SMI watcher. When a BMC appears, a temporary IPMI user probes for AEM1 instance count and AEM2 instance records. Each discovered instance gets a platform device, private IPMI user, hwmon registration, response buffer, and dynamic sensor files. Sensor reads flow from sysfs into `data->update()` or direct energy reads, then into synchronous IPMI requests completed by `aem_msg_handler()`. Power average is computed by reading energy, sleeping for the configured interval, reading energy again, and dividing the delta by elapsed nanoseconds. BMC removal and module exit walk `driver_data.aem_devices` and unregister sysfs, hwmon, IPMI, platform, IDA, and memory state.

## State and Persistence Behavior

All persistent runtime state is in memory per AEM instance. The driver caches sensor values for `REFRESH_INTERVAL`, but energy reads used for power calculation bypass most aggregate caching. `power_period[]` is user-writable sysfs state only and defaults to 1000 ms with a 200 ms minimum. There is no durable storage; firmware state is read-only from this driver except for the query protocol itself.

## Dependencies and Integration Points

The driver integrates IPMI (`ipmi_create_user`, `ipmi_smi_watcher_register`, `ipmi_request_settime`), platform devices, classic hwmon sysfs registration, IDA instance allocation, completions, mutexes, jiffies, and endian conversion helpers. It also declares IBM DMI aliases for autoloading on known System x/Blade platforms.

## Risks and Edge Cases

`aem_read_sensor()` calls `aem_send_message()` but does not check its return before waiting, so address/request failures can degrade into timeout behavior. The IPMI completion is reused without an explicit `reinit_completion()` before every transaction, relying on serialized use and prior completion state. `update_aem1_sensors()` and `update_aem2_sensors()` never set `last_updated` or `valid`, so the intended refresh cache appears ineffective and every sysfs update can hit IPMI. Power average sysfs reads sleep while holding `data->lock`, serializing other sensor access for the interval. Error returns from individual sensor reads in update paths are ignored, which can leave stale values. Dynamic sysfs creation and cleanup are manual, making partial registration failures a risk surface.

## Test Signals

Useful tests include BMC add/remove with zero, AEM1, AEM2, and mixed instances; IPMI timeout, completion-code, bad IANA, and short-response paths; sysfs file cleanup after partial create failure; energy scaling to microjoules; power averaging with interrupted sleep; power interval validation; AEM2 power-cap and temperature scaling; and concurrent sysfs reads during BMC removal.
