# sources/distributed-fs/ceph-client/drivers/platform/x86/asus-armoury.h

## Purpose
`asus-armoury.h` is the companion header for `asus-armoury.c`. It defines the firmware-attributes sysfs macro framework, declares generic integer WMI show/store helpers, defines ROG power-limit data structures, and contains the large DMI table that maps ASUS board names to AC/DC tunable limits.

## Important APIs, Types, and Macros
The header declares `armoury_attr_uint_store()` and `armoury_attr_uint_show()` for macro-generated sysfs handlers. Low-level macros such as `__ASUS_ATTR_RO`, `__ASUS_ATTR_RO_AS`, `__ASUS_ATTR_RW`, `__WMI_STORE_INT`, and `ASUS_WMI_SHOW_INT` build `struct kobj_attribute` definitions. Group macros including `ASUS_ATTR_GROUP_BOOL_RO`, `ASUS_ATTR_GROUP_BOOL_RW`, `ASUS_ATTR_GROUP_ENUM_INT_RO`, `ASUS_ATTR_GROUP_BOOL`, `ASUS_ATTR_GROUP_ENUM`, `ASUS_ATTR_GROUP_INT_VALUE_ONLY_RO`, and `ASUS_ATTR_GROUP_ROG_TUNABLE` generate firmware-attributes-compatible directories with `current_value`, `possible_values`, `display_name`, `type`, and, for tunables, `default_value`, `min_value`, `max_value`, and `scalar_increment`.

`struct power_limits` stores min/default/max values for CPU package limits, APU/platform limits, Nvidia dynamic boost, Nvidia thermal target, and Nvidia TGP. `struct power_data` pairs AC and DC `power_limits` and records whether a model requires fan-curve handling. `power_limits[]` is a static DMI match table keyed primarily by `DMI_BOARD_NAME`.

## Control Flow
This header does not execute code independently; its macros expand into static functions, attributes, and attribute groups in `asus-armoury.c`. ROG tunable macros call `get_current_tunables()` at show/store time so AC/DC limits follow power-source state. The DMI table is consumed by `init_rog_tunables()`, which calls `dmi_first_match(power_limits)`, reads the selected `struct power_data`, allocates AC/DC tunable stores, and seeds defaults from `_def` values or `_max` when no default is specified.

## State and Persistence
The header defines static const model data rather than mutable state. The DMI table is compiled into the module and persists for the lifetime of the loaded code. The generated attributes store mutable current values in `struct rog_tunables` allocated by the C file; firmware persistence depends on ASUS WMI behavior.

## Dependencies and Integration Points
The macros assume `enum_type_show()`, `int_type_show()`, `get_current_tunables()`, and the generic armoury integer helpers exist in the including C file. They depend on sysfs/kobject types, DMI matching, and ASUS WMI device IDs supplied by included platform headers. The DMI table is the model policy boundary for safe power tuning; it prevents exposing tunables when no model-specific limits exist.

## Risks and Test Signals
Macro-generated sysfs code is compact but easy to break with naming mismatches because each macro synthesizes function and symbol names. ROG tunable stores reject equal min/max values as unsupported and rely on `u8` limits, so model values must fit that range. The DMI table is large and model-specific; incorrect board names, missing DC data, or missing max values directly affect attribute visibility. Tests should compile-check every generated attribute group, validate that group names match the firmware-attributes ABI, verify model-specific DMI matches for representative FA/GA/GU/GV/GX/RC boards, confirm default fallback to max, and check that absent limits suppress the corresponding power tunable.
