# sources/distributed-fs/ceph-client/drivers/pinctrl/pinconf.c

Purpose: Provides the core pin configuration glue between pinctrl maps/settings and controller driver `pinconf_ops`. It validates maps, converts map names to numeric pin or group selectors, applies settings, exposes direct pin config setting, and creates debugfs views for per-pin and per-group configuration.

Important APIs and functions: `pinconf_check_ops()` validates that a controller can set either pin or group configs. `pinconf_validate_map()` checks map integrity. `pin_config_get_for_pin()` and `pin_config_group_get()` are the core read paths used by generic debug dumping. `pinconf_map_to_setting()`, `pinconf_apply_setting()`, and `pinconf_set_config()` form the set/apply path. Debugfs helpers include `pinconf_show_map()`, `pinconf_show_setting()`, `pinconf_init_device_debugfs()`, `pinconf_pins_show()`, and `pinconf_groups_show()`.

Control flow: Registration validation rejects config-capable controllers that cannot set configs. When a map is converted, `PIN_MAP_TYPE_CONFIGS_PIN` resolves a pin name with `pin_get_from_name()`, while `PIN_MAP_TYPE_CONFIGS_GROUP` resolves a group selector with `pinctrl_get_group_selector()`. Applying the setting dispatches to `pin_config_set()` or `pin_config_group_set()` and logs failures with the numeric selector. Group reads acquire the target pinctrl device by dev name, lock `pctldev->mutex`, resolve the group selector, call the driver's group getter, and unlock.

State and persistence: The file does not own hardware state. It stores selector/config pointers in `struct pinctrl_setting` and relies on map lifetimes owned by the pinctrl core. Hardware persistence is entirely driver-defined after `pinconf_apply_setting()` invokes callbacks.

Dependencies and integration points: Depends on `core.h` lookup helpers, pin descriptors, pinctrl map/settings types, debugfs/seq_file, and optional generic pinconf debug dumping from `pinconf-generic.c`. It is central to all drivers that provide `struct pinconf_ops`.

Risks: `pinconf_map_to_setting()` copies config pointers rather than duplicating arrays, so map lifetime must outlive settings. `pinconf_apply_setting()` requires exact callback presence for the chosen setting type, so a map type mismatch becomes runtime `-EINVAL`. Debugfs paths assume descriptors and group callbacks are stable under `pctldev->mutex`; driver-specific callbacks must avoid unsafe sleeping or lock inversions.

Test signals: Useful tests include invalid map registration, pin-name and group-name lookup failures, pin and group config application, direct `pinconf_set_config()`, debugfs `pinconf-pins`/`pinconf-groups` rendering, and drivers that implement only pin or only group callbacks.
