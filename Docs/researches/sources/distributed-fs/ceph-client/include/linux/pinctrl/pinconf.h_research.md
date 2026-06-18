# sources/distributed-fs/ceph-client/include/linux/pinctrl/pinconf.h

Purpose: declares the driver callback contract for pin configuration-capable pinctrl controllers. It is the generic-to-driver boundary for reading and applying electrical pin settings on individual pins or groups.

Important APIs and types: `struct pinconf_ops` contains optional `is_generic` under `CONFIG_GENERIC_PINCONF`, pin-level `pin_config_get()` and `pin_config_set()`, group-level `pin_config_group_get()` and `pin_config_group_set()`, and debugfs hooks `pin_config_dbg_show()`, `pin_config_group_dbg_show()`, and `pin_config_config_dbg_show()`.

Control flow: pinctrl core resolves a requested state into config values and calls the relevant pin or group setter with an array of packed `unsigned long` configs. Query/debug paths call the getter or debug hooks. The documented error convention distinguishes unsupported settings (`-ENOTSUPP`) from settings that exist but are currently disabled (`-EINVAL`).

State and persistence: this header stores no state. Runtime state lives in the pin controller driver and hardware registers; config callbacks mutate hardware as part of pinctrl state selection and may be replayed by PM resume flows.

Dependencies and integration points: depends on `pinctrl_dev` and `seq_file` forward declarations and integrates with `pinctrl_desc.confops`, generic pinconf packing, pinctrl state selection, and debugfs reporting.

Risks and test signals: risks include callbacks accepting unsupported configs silently, failing to apply all configs atomically enough for hardware requirements, inconsistent pin vs group behavior, and stale debug display. Test by applying known DT states, reading back configs, exercising unsupported/disabled parameters, group setters, and debugfs output across generic and custom pinconf drivers.
