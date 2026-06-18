# sources/distributed-fs/ceph-client/include/acpi/acuuid.h

Purpose: Centralizes ACPI UUID/GUID string constants for controllers, devices, interfaces, TPM functions, NVDIMM/NFIT range/device types, processor properties, and miscellaneous device properties.

Important APIs, types, and functions: Exports only macros such as `UUID_GPIO_CONTROLLER`, `UUID_PCI_HOST_BRIDGE`, `UUID_CONTROL_METHOD_BATTERY`, `UUID_NFIT_DIMM`, `UUID_PERSISTENT_MEMORY`, `UUID_CACHE_PROPERTIES`, `UUID_DEVICE_PROPERTIES`, `UUID_DEVICE_GRAPHS`, and `UUID_USB4_CAPABILITIES`.

Control flow: No control flow. Consumers compare or publish UUID strings in `_DSD`, NFIT, device property, TPM, battery, USB4, graph, and platform-capability paths.

State and persistence: Values are immutable ABI identifiers mirrored from ACPI/device specifications. Firmware may persist these UUIDs in tables or namespace packages; the header stores no runtime state.

Dependencies and integration points: Deliberately standalone. It integrates with ACPICA table decoding, Linux ACPI property parsing, NVDIMM/NFIT code, TPM physical-presence/memory-clear flows, and device graph/property helpers.

Risks and test signals: Risks are typo-induced ABI mismatches and case/format-sensitive comparisons in consumers. Test by validating known UUID strings against spec fixtures and by probing firmware/device property paths that depend on each identifier.
