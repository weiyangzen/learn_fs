# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/enum-attributes.c

Purpose: handles HP BIOS enumeration attributes, exposing each enumerated BIOS setting as a sysfs directory with current value, possible values, display name, language code, and type.

Important APIs/types/functions: `hp_alloc_enumeration_data()`, `hp_populate_enumeration_package_data()`, `hp_populate_enumeration_buffer_data()`, and `hp_exit_enumeration_attributes()` are called by the core. `validate_enumeration_input()` accepts only values present in `possible_values`; `update_enumeration_value()` refreshes cached state after successful firmware writes. `expected_enum_types` validates ACPI package layout.

Control flow: allocation sizes the typed array from WMI instance count. Package parsing walks ordered ACPI elements, converts hex strings, validates expected types, handles optional prerequisite and possible-value lists, clamps counts, and fills `enumeration_data`. Buffer parsing reads the current value, common data, current value again, count, and value strings from the firmware buffer. Populate functions update permissions, derive friendly names, and create the attribute group.

State and persistence: cached current value and possible-value lists live in `bioscfg_drv.enumeration_data`; writes persist only through `hp_set_attribute()` from the shared store macro.

Dependencies and integration: depends on common parsing helpers, sysfs macros, firmware WMI enumeration GUID, and hp-bioscfg core enumeration.

Risks: package parsing has element-index adjustments for omitted zero-length lists, making off-by-one regressions likely. The possible-values package branch only copies when `size < MAX_VALUES_SIZE`, so exactly max-sized lists deserve review. Test signals include invalid value writes, readonly enforcement, package/buffer parsing with zero and oversized lists, and cleanup removing sysfs groups before freeing arrays.
