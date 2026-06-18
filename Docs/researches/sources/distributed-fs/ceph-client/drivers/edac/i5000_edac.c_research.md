# sources/distributed-fs/ceph-client/drivers/edac/i5000_edac.c

## Purpose
This PCI EDAC driver supports Intel 5000P/V/X-class FB-DIMM memory controllers. It discovers the multi-function MCH and branch devices, decodes FB-DIMM topology, enables FBD error reporting, polls fatal/nonfatal error registers, and reports memory and optional miscellaneous errors through EDAC.

## Important APIs and Functions
`struct i5000_pvt` caches PCI devices, memory-map registers, MTR/AMB-present registers, and a DIMM size matrix. `i5000_get_error_info()` reads and clears first/next fatal and nonfatal FBD error registers plus recoverable/nonrecoverable address logs. `i5000_process_fatal_error_info()` and `i5000_process_nonfatal_error_info()` decode masks into EDAC fatal/UE/CE reports. Topology helpers include `i5000_get_devices()`, `i5000_get_mc_regs()`, `determine_mtr()`, `handle_channel()`, `calculate_dimm_size()`, and `i5000_init_csrows()`.

## Control Flow
Probe accepts only device 16 function 0, reads advertised channels and DIMMs per channel, allocates branch/channel/slot EDAC layers, obtains function 1/function 2 and branch 0/1 PCI devices, caches memory-technology registers, computes DIMM sizes, fills EDAC DIMM metadata, enables error reporting when memory exists, adds the controller, clears stale errors, and creates a generic PCI parity controller. Polling reads/clears hardware status, processes fatal first, then nonfatal CE/UE/misc categories.

## State and Persistence
Runtime state is the EDAC controller private `i5000_pvt`, global `i5000_pci`, and module parameter `misc_messages`. Hardware masks are changed to enable error reporting; fatal/nonfatal status registers are cleared by writing back observed bits.

## Dependencies and Integration
The driver depends on PCI config access, Intel FBD device IDs, EDAC memory-controller APIs, EDAC PCI generic parity support, and Linux memory-zone definitions for page counts.

## Risks
The register model spans several PCI functions and branch devices, so missing/broken BIOS enumeration prevents probe. Some comments note topology mapping is awkward and could be simplified. Miscellaneous nonfatal messages are suppressed unless `misc_messages` is set. Error-reporting masks are enabled without an explicit restore path.

## Test Signals
Signals include correct branch/channel/slot EDAC topology, DIMM sizes from MTR/AMB-present bits, FBD mask changes, CE/UE/fatal reports with decoded bank/rank/RAS/CAS, optional misc reports, generic PCI parity controller creation, and balanced `pci_dev_put()` on removal/failure.
