# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/order-list-attributes.c

Purpose: supports ordered-list BIOS attributes, which represent ordered sequences such as boot orders. It exposes a semicolon-separated current value, available elements, display name, language code, and type.

Important APIs/types/functions: lifecycle functions are `hp_alloc_ordered_list_data()`, `hp_populate_ordered_list_package_data()`, `hp_populate_ordered_list_buffer_data()`, and `hp_exit_ordered_list_attributes()`. `replace_char_str()` translates comma and semicolon separators. `validate_ordered_list_input()` converts user semicolons to BIOS commas and leaves semantic validation to firmware.

Control flow: package parsing validates expected ACPI types, converts current value commas to semicolons for sysfs, handles common metadata and prerequisites, clamps element count, and splits comma-separated element data. Buffer parsing reads the current value, common data, element count, and element strings. Writes use the shared store macro; validation mutates the copied input into the firmware separator format before `hp_set_attribute()`.

State and persistence: cached ordered-list data lives in `bioscfg_drv.ordered_list_data`. Runtime cache updates follow successful WMI writes; BIOS owns persistent ordering.

Dependencies and integration: integrates with hp-bioscfg common parsing, firmware WMI ordered-list GUID, and sysfs attribute-group creation.

Risks: local validation does not check membership or duplicates, so user errors depend on firmware rejection. Package `ORD_LIST_ELEMENTS` conversion is complex because data may be hex-encoded comma-separated content. Test signals include separator conversion, list count clamping, malformed packages, empty lists, readonly mode, and user writes that firmware accepts or rejects.
