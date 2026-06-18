# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utdecode.c

Purpose: `utdecode.c` maps ACPICA numeric IDs, descriptor types, object types, region spaces, event IDs, mutex IDs, reference classes, notify values, and parser argument types to readable strings, and publishes namespace type property metadata.

Important APIs/types/functions: Key data includes `acpi_gbl_ns_properties`, `acpi_gbl_region_types`, type-name arrays, descriptor-name arrays, mutex names, notify-name arrays, and argument-type arrays. Functions include `acpi_ut_get_region_name()`, `acpi_ut_get_event_name()`, `acpi_ut_get_type_name()`, `acpi_ut_get_object_type_name()`, `acpi_ut_get_node_name()`, `acpi_ut_get_descriptor_name()`, `acpi_ut_get_reference_name()`, `acpi_ut_get_mutex_name()`, `acpi_ut_get_notify_name()`, `acpi_ut_get_argument_type_name()`, and `acpi_ut_valid_object_type()`.

Control flow: Most functions bounds-check indexes and return stable fallback strings for invalid IDs. `acpi_ut_get_object_type_name()` validates descriptor type before dereferencing object type. `acpi_ut_get_node_name()` recognizes NULL/root, verifies namespace-node descriptor type, repairs corrupted names, and returns a four-character nameseg. Notify decoding follows ACPI ranges: generic, reserved, per-object-specific, device-specific, and hardware-specific.

State and persistence behavior: The file mostly exposes read-only static/global lookup tables. `acpi_ut_get_node_name()` can repair a namespace node name in place if corruption is detected.

Dependencies and integration points: It is used throughout diagnostics, namespace handling, address-range warnings, mutex debug, notify dispatch logging, parser debugging, and object validation. It depends on namespace node structures and name repair helpers.

Risks and test signals: Risks include table/enum drift when ACPI adds values, in-place node name repair hiding corruption, invalid descriptor dereferences if callers pass arbitrary memory, and debug-only functions missing in non-debug builds. Tests should validate boundary values for every decoder, corrupted namespace names, user-defined region IDs, notify decoding by object type, and `acpi_ut_valid_object_type()` for local max.
