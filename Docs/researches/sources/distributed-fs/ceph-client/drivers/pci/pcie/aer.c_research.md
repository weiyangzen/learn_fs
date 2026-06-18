<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/aer.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/aer.c

## Purpose
`aer.c` implements the PCIe Advanced Error Reporting root port/RCEC service driver and most AER device support. It initializes AER capability state, manages ECRC policy, exposes AER sysfs counters and ratelimits, handles root-port interrupts, identifies devices that logged errors, prints and traces error details, invokes driver callbacks for correctable errors, and dispatches nonfatal/fatal recovery through `pcie_do_recovery()`.

## Important APIs, Types, and Functions
Important internal types are `struct aer_err_source`, `struct aer_rpc`, and `struct aer_info`. Externally relevant functions include `pci_no_aer()`, `pci_aer_available()`, `pcie_aer_is_native()`, `pci_aer_clear_nonfatal_status()`, `pci_aer_clear_fatal_status()`, `pci_aer_raw_clear_status()`, `pci_aer_clear_status()`, `pci_save_aer_state()`, `pci_restore_aer_state()`, `pci_aer_init()`, `pci_aer_exit()`, `pci_print_aer()`, `pci_aer_unmask_internal_errors()`, `aer_get_device_error_info()`, `aer_print_error()`, `aer_recover_queue()` under APEI, and `pcie_aer_init()`.

## Control Flow and State
Device initialization finds `PCI_EXT_CAP_ID_ERR`, allocates `dev->aer_info`, initializes ratelimits, registers a saved extended-cap buffer, clears status, enables device error reporting if native AER is available, and applies ECRC policy. The service probe is limited to Root Ports and RCECs; it allocates `aer_rpc`, requests a threaded IRQ, enables CXL RCH internal errors if needed, clears stale root/downstream status, disables system-error forwarding, and enables root AER interrupts.

The hard IRQ reads root status/source, clears root status, queues an `aer_err_source` in a kfifo, and wakes the threaded handler. The threaded handler processes correctable first, then uncorrectable; `find_source_device()` walks the subordinate bus or RCEC association, `aer_get_device_error_info()` reads status/mask/FEP/TLP log, `aer_print_error()` updates counters, tracepoints, and logs, and `handle_error_source()` invokes CXL RCH handling plus recovery. APEI GHES can queue firmware-reported AER records through a separate kfifo/work item.

## Dependencies and Integration Points
AER depends on PCIe port services, MSI availability, host bridge native AER ownership or `pcie_ports=native`, RAS trace/event infrastructure, optional ACPI APEI/GHES, optional ECRC, optional CXL RAS, and generic PCI error handlers. It collaborates with `err.c` for recovery, `dpc.c` for DPC-sourced AER details, `aer_cxl_rch.c` for CXL internal errors, `aer_inject.c` for synthetic testing, and `portdrv.c` for service device creation and IRQ assignment.

## Risks and Test Signals
Risks include losing errors when the root FIFO overflows, mishandling firmware-owned AER, stale status during probe/resume, incorrect source identification when Requester ID is absent or multiple errors are present, and unsafe reset behavior for RCiEP/RCEC paths. Strong tests include AER injection of correctable/nonfatal/fatal errors, CXL RCH internal-error paths, APEI GHES recovery records, suspend/resume save-restore, sysfs counter and ratelimit behavior, MSI-disabled boot paths, and recovery callback voting through `err.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/aer.c -->
