# sources/distributed-fs/ceph-client/drivers/power/supply/cros_usbpd-charger.c

Purpose: exposes ChromeOS EC USB-PD and optional dedicated charger ports as power supplies. It reports online/status/current/voltage/USB type/model/manufacturer and provides global writable external input current/voltage limits.

Important APIs/types/functions: `struct charger_data` owns EC handles, port counts, registered supplies, and notifier. `struct port_data` caches per-port power info and discovery strings. `cros_usbpd_charger_ec_command()` wraps EC transport; `cros_usbpd_charger_get_power_info()` maps EC roles/types to `POWER_SUPPLY_*`; `cros_usbpd_charger_set_ext_power_limit()` sends `EC_CMD_EXTERNAL_POWER_LIMIT`.

Control flow: probe queries USB-PD port count and total charge-port count, validates that at most one dedicated charger follows the USB-PD ports, registers per-port descriptors as USB or mains supplies, and registers for USB-PD EC notifications. Dynamic property reads refresh power info with a 500 ms cache except when MKBP event support makes cached online state authoritative. External power changes and EC notifications refresh every registered port. Resume emits changed notifications and expires port caches.

State and persistence: port state is an in-memory cache. `input_current_limit` and `input_voltage_limit` are module-global cached limits shared across all ports; they are initialized to `EC_POWER_LIMIT_NONE` and updated only after successful EC writes.

Dependencies and integration: depends on ChromeOS EC USB-PD commands, `cros_usbpd_notify`, the power-supply USB type bitmap, and EC discovery/power-info response formats. Dedicated charger ports intentionally expose a smaller property set.

Risks and test signals: this source snapshot includes duplicated local declarations in `cros_usbpd_charger_power_changed()`. Because input limits are global, multi-instance behavior should be reviewed. Test unsupported command fallbacks, dedicated-port count validation, EC failure handling, USB type mapping, limit clearing with negative values, uevent generation on type/status changes, and resume cache invalidation.
