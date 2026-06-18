# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_lpc.c

Purpose: LPC transport driver for ChromeOS EC on x86/ACPI/DMI systems, including Microchip MEC variants and Framework Laptop quirks.

Important APIs, types, and functions: `struct lpc_driver_data` describes DMI/ACPI quirks. `struct cros_ec_lpc` stores memory-map base, optional ACPI fixed-memory mapping, and read/write callbacks. Transport functions include raw port IO, MEC-aware wrappers, direct MMIO wrappers, `cros_ec_pkt_xfer_lpc()` for v3, `cros_ec_cmd_xfer_lpc()` for v2, and `cros_ec_lpc_readmem()` for userspace readmem. `cros_ec_lpc_acpi_notify()` handles EC panic, MKBP, and wake notifications.

Control flow: module init checks ACPI devices (`GOOG0004`, `FRMWC004`) or DMI match, registers the platform driver, and creates a synthetic platform device for DMI-only systems. Probe applies quirk data, optionally remaps memory base, attaches a different ACPI companion, acquires an AML mutex for MEC, reads ACPI fixed-memory resources for direct MMIO, otherwise reserves IO regions and initializes MEC EMI. It probes EC ID first through MEC then fallback non-MEC IO, reserves remaining regions, allocates/registers the core EC device, optionally sets IRQ, and installs ACPI notify handler. Command transfers write request buffers/registers, trigger host command, poll busy status up to one second, validate result/checksum, and return response length.

State and persistence: static `cros_ec_lpc_acpi_device_found` controls synthetic-device cleanup. Driver quirk data is static. Per-device LPC state holds IO/MMIO access functions. Firmware shared memory is readable through `cmd_readmem`. ACPI notify can trigger system shutdown on EC panic.

Dependencies and integration points: ACPI, DMI, IO port access, optional fixed-memory resources, MEC helper file, core Chrome EC, platform devices, PM hooks, reboot/hw-protection path, and Framework/Chromebook DMI tables.

Risks and edge cases: IO region reservation differs for MEC vs non-MEC and can fail on partially exposed hardware. EC ID probing is the critical hardware-detection gate. ACPI panic notify triggers emergency log, notifier fanout, uevent, and orderly shutdown. Polling busy status uses a one-second timeout. `cros_ec_lpc_readmem()` rejects `offset >= EC_MEMMAP_SIZE - bytes`, which has edge behavior for zero-length string reads. Forced synchronous probe avoids ACPI child races.

Test signals: DMI-only and ACPI-backed probe paths, Framework quirk variants, MEC and non-MEC EC ID detection, v2/v3 host commands, readmem through chardev, ACPI MKBP and panic notifications, wake notification, suspend prepare/late/resume early/complete sequencing, and module unload cleanup.
