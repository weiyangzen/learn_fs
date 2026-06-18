# sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_pstore.c

Purpose: instantiates a `ramoops` platform device for ChromeOS persistent crash logging, using either ACPI-provided memory or a traditional x86 Chromebook VGA memory range.

Important APIs, types, and functions: `chromeos_ramoops_data` defines default pstore sizes and address `0xf00000`/`0x100000`. `ecc_size` module parameter optionally enables ECC. `chromeos_probe_acpi()` reads a memory resource from ACPI `GOOG9999`. `chromeos_pstore_init()` chooses ACPI or DMI path and registers `chromeos_ramoops`.

Control flow: init applies ECC size if positive, probes ACPI first, then falls back to DMI checks for known Chromebook/coreboot signatures. If either path matches, it registers the static `ramoops` platform device. Exit unregisters it. ACPI probing uses `platform_driver_probe()` only at init time.

State and persistence: persistent data resides in the reserved RAM range consumed by ramoops across reboots. Kernel state is static platform data and device registration. ACPI can override default address/size.

Dependencies and integration points: depends on DMI, ACPI when enabled, pstore/ramoops platform data, and the ramoops driver. DMI table matches Google coreboot Chromebooks plus early Samsung/Acer/Cr-48 devices.

Risks and edge cases: the hardcoded VGA range is x86-Chromebook-specific and unsafe on unmatched systems, so DMI gating is important. ACPI resource absence returns `-ENOMEM`, which prevents ACPI path. ECC parameter is read-only after load. The static ramoops device means only one instance.

Test signals: verify ramoops device registration on ACPI GOOG9999 and DMI-only systems, crash log persistence across reboot, ECC sizing behavior, and non-ChromeOS systems returning `-ENODEV`.
