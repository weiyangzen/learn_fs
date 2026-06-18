# sources/distributed-fs/ceph-client/drivers/edac/octeon_edac-pci.c

## Purpose
Implements polling EDAC PCI error reporting for Cavium Octeon PCI controllers. It reads the PCI status/config CSR, maps parity and abort/system-error bits to EDAC PCI events, and clears handled bits.

## Important APIs, Types, And Functions
- `octeon_pci_poll` reads `CVMX_NPI_PCI_CFG01`, reports detected parity errors with `edac_pci_handle_pe`, reports non-parity system/abort/parity-master conditions with `edac_pci_handle_npe`, and writes set bits back to clear them.
- `octeon_pci_probe` allocates and registers `edac_pci_ctl_info`.
- `octeon_pci_remove` unregisters and frees EDAC PCI state.

## Control Flow
The platform probe allocates a zero-private EDAC PCI control object, attaches device names and `octeon_pci_poll`, and adds it to the EDAC core. Polling reads `CFG01`, tests each error bit independently, reports the matching EDAC event, sets that status bit to one, and writes the register back after each handled condition.

## State And Persistence
No private driver state is stored beyond the EDAC PCI control object. Hardware error bits persist in `CVMX_NPI_PCI_CFG01` until cleared by the poll function.

## Dependencies And Integration Points
Depends on Octeon NPI/PCI CSR helpers and EDAC PCI APIs. The platform driver name is `octeon_pci_edac`, and operation is polling-only.

## Risks And Edge Cases
Writing the register after each bit can race with newly arriving bits depending on hardware write-one-to-clear semantics. Probe initializes `res` to zero and returns it on `edac_pci_add_device` failure, which can report success after a failed add unless the EDAC core failure path is interpreted elsewhere. There is no interrupt support.

## Test Signals
Exercise DPE, SSE, RMA, RTA, STA, and MDPE bits; verify correct CE/non-parity EDAC counters and clear behavior; test add-device failure return handling; and ensure remove deletes the EDAC PCI device.
