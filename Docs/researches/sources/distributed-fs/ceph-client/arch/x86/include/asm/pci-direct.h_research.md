# sources/distributed-fs/ceph-client/arch/x86/include/asm/pci-direct.h

Purpose: declares early direct PCI configuration-space accessors used before the generic PCI subsystem is initialized.

Important APIs, types, and functions: exports `read_pci_config()`, `read_pci_config_byte()`, `read_pci_config_16()`, `write_pci_config()`, `write_pci_config_byte()`, `write_pci_config_16()`, and `early_pci_allowed()`. All accessors take bus, slot, function, offset, and for writes a value.

Control flow: no implementation is in this header. Early boot code calls these functions to query or modify PCI config space before `struct pci_bus` and normal `pci_ops` are available. `early_pci_allowed()` gates whether such direct access is permitted in the current environment.

State and persistence: reads and writes target hardware PCI configuration registers. State persists in device configuration until reset or later reconfiguration.

Dependencies and integration points: implemented by x86 PCI direct access code and used by early quirks, chipset discovery, and boot-time PCI setup.

Risks: early direct config cycles bypass normal resource ownership, locking, and firmware mediation. Wrong bus/device/function or offsets can alter device decode, interrupts, or bridge windows before kernel PCI enumeration.

Test signals: early quirk logs, PCI enumeration after direct access, `early_pci_allowed()` behavior under firmware/virtualization restrictions, and boot tests on systems needing config type 1/type 2 access.
