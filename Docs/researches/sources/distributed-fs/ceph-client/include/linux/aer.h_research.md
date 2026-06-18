<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/aer.h -->
# sources/distributed-fs/ceph-client/include/linux/aer.h

## Purpose
`aer.h` declares PCIe Advanced Error Reporting data structures and helper APIs used to log, clear, and recover PCIe AER/DPC errors.

## Important APIs, types, and functions
Severity constants include nonfatal, fatal, correctable, and DPC fatal. TLP log constants size standard header and prefix logs. `struct pcie_tlp_log` stores logged DWORDs, header length, and flit-mode flag. `struct aer_capability_regs` snapshots AER capability registers and source IDs. Enabled APIs include `pci_aer_clear_nonfatal_status()`, `pcie_aer_is_native()`, and `pci_aer_unmask_internal_errors()`, with disabled stubs. Always-declared APIs include `pci_print_aer()`, `cper_severity_to_aer()`, and `aer_recover_queue()`.

## Control flow
PCIe error paths snapshot capability registers, print them, map firmware CPER severity if needed, clear/unmask status, and queue recovery work by domain/bus/devfn/severity.

## State and persistence behavior
Register snapshots are transient; hardware AER status persists until cleared. Recovery queue state is maintained by PCIe AER core.

## Dependencies and integration points
It integrates PCI core, firmware CPER reporting, DPC, AER native-control negotiation, and recovery work queues.

## Risks and test signals
Risks include wrong TLP log length, native-control mismatches with firmware, failing to clear errors, and recovery queued for wrong BDF. Test signals include AER injection, firmware-first CPER paths, DPC events, native/non-native control tests, and disabled `CONFIG_PCIEAER` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/aer.h -->
