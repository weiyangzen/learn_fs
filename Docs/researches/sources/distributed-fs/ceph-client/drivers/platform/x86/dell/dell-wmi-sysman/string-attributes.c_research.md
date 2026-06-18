## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/string-attributes.c

Purpose: implements Dell BIOS string attributes for sysman firmware-attributes.

Important APIs/functions: `alloc_str_data()` allocates cached string metadata. `populate_str_data()` validates package fields, caches name/display/default/modifier plus min/max length, and creates the sysfs group. `current_value_show()` re-queries firmware for current string value. `validate_str_input()` enforces cached minimum and maximum string lengths. Generated metadata show handlers expose language code, display name, default value, modifier, min/max length, and type.

Control flow: `sysman.c` enumerates string WMI instances and creates one kobject per attribute. Static metadata reads come from `wmi_priv.str_data`; current value reads fetch WMI. Writes pass through the generic generated store function, which strips newline, validates length, and calls `set_attribute()`.

State and persistence: cached metadata persists for the module lifetime. Successful writes persist to BIOS firmware and set global pending-change state via the BIOS attributes interface. Current values are intentionally not cached.

Dependencies and integration: sysman WMI enumeration, sysfs groups, BIOS attributes setter, shared `MAX_BUFF` bounds, and UTF-16 conversion in `set_attribute()`.

Risks: validation counts bytes from `strlen()` rather than user-visible characters, while the setter later converts to UTF-16, so non-ASCII length semantics can differ. Max-length metadata extraction follows the same ACPI union casting pattern as integer attributes. Test signals include min/max boundary writes, empty strings when permitted, malformed WMI packages, long firmware-provided metadata, non-ASCII input if supported by policy, and firmware write failures due to password requirements.
