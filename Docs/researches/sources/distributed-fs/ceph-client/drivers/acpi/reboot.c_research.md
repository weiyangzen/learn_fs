## sources/distributed-fs/ceph-client/drivers/acpi/reboot.c

### Purpose
`reboot.c` performs ACPI reset-register based reboot when the FADT declares a valid reset register and reset value.

### Important APIs, Types, And Functions
The main API is `acpi_reboot()`. The helper `acpi_pci_reboot()` writes PCI configuration space reset registers when `CONFIG_PCI` is enabled; otherwise it is a no-op. Generic address writes are delegated to `acpi_reset()`.

### Control Flow
`acpi_reboot()` checks `acpi_gbl_FADT.flags` for `ACPI_FADT_RESET_REGISTER`, then verifies the reset register bit width is 8 and bit offset is 0. If the address space is PCI config space it calls `acpi_pci_reboot()`, otherwise it calls `acpi_reset()`. The PCI path locates the root bus, finds the target device/function derived from the reset-register address, writes the reset value to the derived config offset, and waits ten milliseconds.

### State, Persistence, And Dependencies
The file has no persistent state. It depends on FADT global data, ACPICA reset support, PCI bus/device helpers when configured, and delay primitives.

### Integration Points
Architecture reboot paths can call `acpi_reboot()` as a firmware-defined reset mechanism. It bridges ACPI FADT reset metadata to either generic ACPI address-space writes or PCI config writes.

### Risks
Strict width/offset validation rejects non-byte reset registers. PCI reset depends on address encoding, root bus 0 availability, and device lookup. If PCI is disabled, PCI-space reset registers are ignored. Firmware-provided reset registers may be wrong or ineffective.

### Test Signals
Check FADT without reset flag, invalid width/offset, system-memory/system-I/O reset through `acpi_reset()`, PCI reset with present and missing device, PCI-disabled builds, and reboot fallback behavior when reset does not occur.
