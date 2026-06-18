<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/edr.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/edr.c

## Purpose
`edr.c` implements ACPI Error Disconnect Recover support, a hybrid firmware/OS DPC model. Firmware notifies the OS of a disconnect recover event, the OS locates the DPC port, logs and recovers the containment event, then reports success or failure to firmware via `_OST`.

## Important APIs, Types, and Functions
Key helpers are `acpi_enable_dpc()`, `acpi_dpc_port_get()`, `acpi_send_edr_status()`, and `edr_handle_event()`. The externally used functions are `pci_acpi_add_edr_notifier()` and `pci_acpi_remove_edr_notifier()`, declared through PCI ACPI headers and called by PCI ACPI setup/teardown.

## Control Flow and State
Notifier installation checks for an ACPI companion, installs a system notify handler, and optionally evaluates the PCI firmware `_DSM` function to enable DPC. When `ACPI_NOTIFY_DISCONNECT_RECOVER` arrives, `edr_handle_event()` locates the actual DPC port using `_DSM` function 0x0D or defaults to the notified device, verifies DPC capability and trigger status, calls `dpc_process_error()`, clears raw AER status, and runs `pcie_do_recovery()` with `dpc_reset_link()`. It sends `_OST` with success `0x80` or failure `0x81` encoded with the affected BDF.

## Dependencies and Integration Points
EDR depends on `CONFIG_ACPI`, `CONFIG_PCIE_DPC`, PCI firmware DSM GUID support, DPC helpers, AER raw status clearing, and generic PCI error recovery. It is attached from `drivers/pci/pci-acpi.c` for suitable devices and removed when ACPI PCI state is torn down.

## Risks and Test Signals
Risks include firmware returning malformed `_DSM` objects, locating the wrong DPC port, missing trigger status due to races with native DPC, and incorrect `_OST` status causing firmware/OS disagreement. Tests should simulate EDR notifications, absent optional DSMs, failed locate DSM, ports without DPC, recovery success/failure, and notifier removal on device teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/edr.c -->
