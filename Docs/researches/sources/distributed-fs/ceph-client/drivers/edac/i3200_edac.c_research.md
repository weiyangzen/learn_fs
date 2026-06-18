# sources/distributed-fs/ceph-client/drivers/edac/i3200_edac.c

## Purpose
This PCI EDAC driver supports Intel 3200/3210 memory hub controllers. It maps a 64-bit MCHBAR, discovers channel count and rank boundaries, registers DDR2 DIMM topology, polls ECC error logs, and reports CE/UE events.

## Important APIs and Functions
`how_many_channels()` reads CAPID0 to detect single/dual channel mode. `eccerrlog_syndrome()` and `eccerrlog_row()` decode ECC error log fields. `i3200_get_and_clear_error_info()` captures status and channel ECC logs while guarding against CE/UE overwrite races. `i3200_map_mchbar()`, `i3200_get_drbs()`, `i3200_is_stacked()`, and `drb_to_nr_pages()` implement topology discovery. `i3200_probe1()` and remove/init functions handle lifecycle.

## Control Flow
Module init initializes op state and registers the PCI driver, with a manual fallback probe if needed. Probe enables PCI, maps MCHBAR, reads DRBs, determines channel count, allocates EDAC layers of DIMM and channel, records the MCHBAR window in private state, detects stacked memory layout, fills DIMM sizes, clears stale errors, and registers EDAC. Polling captures ERRSTS and channel ECC logs, clears ERRSTS, reports an overwrite UE if status changed, then emits CE/UE reports for each channel log.

## State and Persistence
Per-controller private state is `struct i3200_priv` with the mapped MCHBAR window. Static state includes global `nr_channels`, `mci_pdev`, and `i3200_registered`. Hardware error logs are cleared on each poll.

## Dependencies and Integration
The driver uses PCI config space, `readq()` for ECC logs, `ioremap`/`iounmap`, EDAC memory-controller APIs, and Intel PCI IDs. It does not create a generic EDAC PCI parity controller unlike i3000/i5000/i5400.

## Risks
`nr_channels` is global, so the code assumes only one active controller instance. Error log capture is non-atomic and uses the same overwrite mitigation pattern as i3000. Stacked-memory page calculation is register-layout sensitive.

## Test Signals
Validation should check MCHBAR mapping including high address rejection, CAPID channel mode, DIMM page counts from DRBs, CE/UE reports from ECCERRLOG bits, status clearing, and unload unmapping plus `pci_disable_device()`.
