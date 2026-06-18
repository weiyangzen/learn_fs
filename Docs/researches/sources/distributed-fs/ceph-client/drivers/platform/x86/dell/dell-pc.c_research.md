# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-pc.c

Purpose: Dell system thermal-profile driver mapping SMBIOS thermal modes to the generic `platform_profile` API.

Important APIs/types/functions: `thermal_get_mode()`, `thermal_get_supported_modes()`, `thermal_get_acc_mode()`, `thermal_set_mode()`, platform-profile callbacks, and faux-device registration.

Control flow/state/persistence: Init DMI-checks Dell vendors and creates a faux device. Probe verifies SMBIOS class support, reads supported thermal mode bits, and registers platform-profile ops. Setting a profile preserves active acoustic controller bits. Firmware holds selected mode; driver caches supported modes.

Dependencies/integration: DMI, Dell SMBIOS, faux device core, and `ACPI_PLATFORM_PROFILE`.

Risks/test signals: Bitfield extraction and AAC preservation are key. Test unsupported SMBIOS class, supported profile choices, get/set for balanced/performance/quiet/cool, and coexistence with other platform-profile providers.
