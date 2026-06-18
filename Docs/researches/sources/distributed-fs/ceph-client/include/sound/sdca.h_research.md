# sources/distributed-fs/ceph-client/include/sound/sdca.h

Source read summary: 87 lines, MIPI SDCA function-discovery core declarations.

Purpose: defines SDCA device/function descriptors, device-wide SDCA data, quirks, and ACPI/SoundWire discovery/register helpers for SoundWire SDCA devices.

Important APIs, types, and functions: `SDCA_MAX_FUNCTION_COUNT` caps functions. `struct sdca_function_desc` stores firmware node, SDCA function device, name, type, and ACPI address. `struct sdca_device_data` stores interface revision, number of functions, descriptor array, and optional SWFT ACPI table. Quirks include RT712 VB and skipping function type patching. Enabled APIs look up functions, SWFT, interface revision, quirk matches, and register/unregister SDCA function devices; disabled stubs are no-ops/false/success.

Control flow: SoundWire slave probe discovers SDCA metadata from ACPI firmware, patches quirks, registers function child devices, and unregisters them on removal.

State and persistence behavior: discovered function data is per-slave runtime state derived from firmware tables/properties. Firmware data persists externally; kernel objects are device-lifetime.

Dependencies and integration points: depends on ACPI, firmware nodes, SoundWire slave devices, and optional `CONFIG_SND_SOC_SDCA`. It is the base for SDCA ASoC and FDL helpers.

Risks and edge cases: invalid function counts, firmware-node lifetime, SWFT parsing errors, and config stubs can hide missing SDCA support.

Test signals: ACPI SDCA function discovery, SWFT/interface revision parsing, quirk matching, child device registration/unregistration, max function bounds, and disabled-config builds.
