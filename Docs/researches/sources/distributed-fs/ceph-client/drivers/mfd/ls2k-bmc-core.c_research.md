# sources/distributed-fs/ceph-client/drivers/mfd/ls2k-bmc-core.c

Purpose: this is the Loongson-2K BMC PCI MFD core. It exposes framebuffer and IPMI child devices from BMC BAR resources and contains reset-recovery logic for the LS2K BMC/LS7A PCIe link.

Important APIs, types, and functions: `ls2k_bmc_cells[]` registers one `simple-framebuffer` and five `ls2k-ipmi-si` children. `struct ls2k_bmc_ddata` stores saved BMC and bridge PCI config values plus reset work. `ls2k_bmc_save_pci_data()` captures bridge/BMC config registers. `ls2k_bmc_recover_pci_data()` runs under `stop_machine()` to clear bridge BARs, wait for reset, restore config, retrain PCIe, wait for firmware/DDR, and restore BMC BAR/IRQ state. `ls2k_bmc_init()` wires PCIe and GPIO reset interrupts. `ls2k_bmc_parse_mode()` reads a mode string from BAR0 and fills `simplefb_platform_data`.

Control flow: probe enables the PCI device, allocates driver data, initializes interrupt/reset recovery, parses display mode from BAR0, removes conflicting firmware framebuffers, then registers children relative to BAR0. Reset interrupts are rate-limited by `LS2K_BMC_INT_INTERVAL` and schedule work; the work uses `stop_machine()` to avoid CPU access during PCIe loss.

State and persistence: the driver persists saved PCI config state in memory for reset recovery. It programs Loongson GPIO registers via ioremap to enable the reset interrupt. Framebuffer mode comes from a BAR memory string and child resources are offsets within the BMC BAR.

Dependencies and integration points: PCI, ACPI GSI registration, aperture conflict removal, simplefb platform data, platform devices, workqueues, stop_machine, virtual terminal console refresh, and LS2K IPMI child drivers.

Risks: reset recovery is hardware-specific and uses long delays including a 10-second wait under a reset work path. `ls2k_bmc_recover_pci_data()` is declared `int` but returns `false` in some paths, effectively `0`, which may hide failures from `stop_machine()`. Mode parsing trusts BAR content formatting. Tests should include BAR0 mode parsing, aperture removal errors, PCI config save/restore, interrupt throttling, GPIO/GSI setup, and reset recovery failure paths.
