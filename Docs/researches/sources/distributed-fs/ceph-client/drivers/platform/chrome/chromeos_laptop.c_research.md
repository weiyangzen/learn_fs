# sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_laptop.c

Purpose: legacy Chromebook helper that instantiates or augments I2C/SMBus peripherals, mainly touchpads, touchscreens, and light sensors, on systems whose firmware does not fully describe them.

Important APIs, types, and functions: `struct i2c_peripheral` describes board info, alternate probe address, DMI IRQ source, adapter type, PCI device filter, software properties, and created client. `struct acpi_peripheral` describes ACPI HID devices needing software-node properties. `chromeos_laptop_check_adapter()` instantiates missing I2C devices on matching adapters. `chromeos_laptop_adjust_client()` attaches software nodes to existing ACPI-backed I2C clients. `chromeos_laptop_prepare_*()` deep-copy static DMI tables into mutable runtime state. `chromeos_laptop_i2c_notifier_call()` reacts to I2C bus add/remove events.

Control flow: module init finds a DMI match, prepares runtime peripheral arrays, registers an I2C bus notifier, then scans existing I2C adapters/clients. For non-ACPI entries it matches adapter names and optional PCI IDs, scans the primary address, optionally probes an alternate bootloader address through a dummy client, and creates the real client. For ACPI entries it checks HID presence, duplicates properties, attaches software nodes to matching clients, and re-triggers device attach if needed. Exit unregisters the notifier, unregisters created clients, removes software nodes, frees property copies and arrays.

State and persistence: `cros_laptop` is a global pointer to runtime-copied descriptors. Each descriptor caches the created or adjusted `i2c_client`. Software nodes and DMI-derived IRQ resources persist until module exit. Hardware state is not modified except through child driver probing.

Dependencies and integration points: depends on DMI, I2C bus notifiers, ACPI device matching, software nodes/property entries, PCI parent matching, DMI onboard-device IRQ data, and drivers for `cyapa`, `elan_i2c`, `atmel_mxt`, `isl29018`, `tsl2583`, and `tsl2563`.

Risks and edge cases: adapter matching uses string prefixes and can be fragile. The function name `chromes_laptop_instantiate_i2c_device` is misspelled but internal. DMI tables are broad for generic Google Atmel devices and rely on ACPI presence validation. IRQ lookup from DMI can fail and abort preparation for affected devices. The notifier must carefully detach clients on removal to avoid stale pointers.

Test signals: validate DMI matching on each listed Chromebook family, ensure the correct adapter/Pci ID receives each client, verify alternate bootloader address detection, confirm ACPI clients get software properties and reprobe, and unload/reload without leaking clients or software nodes.
