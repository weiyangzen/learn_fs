# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/int-attributes.c

Purpose: handles integer-valued BIOS settings for hp-bioscfg, exposing current value, lower/upper bounds, scalar increment, display metadata, and type through sysfs.

Important APIs/types/functions: `hp_alloc_integer_data()`, `hp_populate_integer_package_data()`, `hp_populate_integer_buffer_data()`, and `hp_exit_integer_attributes()` provide lifecycle hooks. `validate_integer_input()` parses decimal input and enforces readonly plus bounds. `update_integer_value()` refreshes cached integer state. `expected_integer_types` defines package layout validation.

Control flow: package parsing converts string and integer ACPI elements in order, supports optional prerequisites, converts the firmware current-value string with `kstrtoint()`, and stores bounds/increment. Buffer parsing reads a UTF-16 value string into temporary memory, converts it, then reads common data and numeric bounds. Populate functions attach the sysfs group and permission mode after parsing.

State and persistence: each instance stores current value and limits in `bioscfg_drv.integer_data`. Firmware persistence is delegated to the shared `ATTRIBUTE_PROPERTY_STORE` path and `hp_set_attribute()`.

Dependencies and integration: uses common buffer/string conversion helpers from `bioscfg.c`, macro accessors from `bioscfg.h`, and the integer WMI GUID.

Risks: `scalar_increment` is exported but not enforced in `validate_integer_input()`, so firmware may reject values the driver accepts. Temporary destination sizing in buffer parsing is tied to remaining UTF-16 buffer size. Test signals should cover lower/upper bound failures, readonly writes, non-numeric input, package type mismatches, malformed buffers, and cleanup after partial enumeration.
