# sources/distributed-fs/ceph-client/drivers/power/supply/cros_charge-control.c

Purpose: extends ChromeOS ACPI battery power supplies with EC-backed charge-control properties. It translates Linux `charge_behaviour` and charge-control threshold properties to `EC_CMD_CHARGE_CONTROL` versions 1 through 3.

Important APIs/types/functions: `struct cros_chctl_priv` stores the EC device, battery hook, selected command version, selected `power_supply_ext`, mutex, current behavior, and cached thresholds. `cros_chctl_configure_ec()` builds `struct ec_params_charge_control`; `cros_chctl_psy_ext_get_prop()` and `cros_chctl_psy_ext_set_prop()` implement the extension; `cros_chctl_add_battery()` registers it on discovered batteries.

Control flow: probe rejects Framework devices exposing the custom Framework charge-limit command unless the module parameter allows coexistence, discovers supported EC command versions, selects the property set for v1/v2/v3, initializes cached behavior to auto with 0/100 thresholds, sends a known-good EC configuration, and registers an ACPI battery hook. Battery add/remove callbacks register or unregister the power-supply extension.

State and persistence: the driver intentionally does not read EC state back after probe; sysfs values are a driver cache. Changes outside this driver are invisible until a property write synchronizes cached state to the EC. Threshold and behavior state is not persisted by the driver, though EC/firmware may retain its own state.

Dependencies and integration: depends on ChromeOS EC command transport, ACPI battery hooks, the power-supply extension API, DMI matching, and the EC charge-control command ABI. Version 2 exposes only end threshold and mirrors start threshold to either zero or the end threshold.

Risks and test signals: this source snapshot includes a duplicated `ec_dev` declaration in probe, so build testing is a first gate. Behavioral tests should verify EC command payload sizes for v1/v2/v3, threshold ordering checks, negative/out-of-range rejection, Framework guard behavior, battery hotplug extension cleanup, and that writes under the mutex leave cache and EC synchronized.
