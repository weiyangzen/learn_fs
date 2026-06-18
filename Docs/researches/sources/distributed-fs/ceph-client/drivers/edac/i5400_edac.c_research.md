# sources/distributed-fs/ceph-client/drivers/edac/i5400_edac.c

## Purpose
This PCI EDAC driver supports Intel 5400 "Seaburg" FB-DIMM memory controllers. It is derived from i5000 but adapts register layouts, error masks, topology, and EDAC reporting for the i5400 two-branch/two-channel lockstep architecture.

## Important APIs and Functions
`enum error_mask` and `error_name[]` define i5400 fatal/nonfatal error classes. `to_nf_mask()` and `from_nf_ferr()` translate between EMASK and FERR nonfatal bit layouts. `struct i5400_pvt` stores PCI devices, map registers, MTR/AMB-present state, and DIMM sizes. `i5400_get_error_info()` reads and clears fatal/nonfatal registers. `i5400_proccess_non_recoverable_info()` handles fatal, unrecoverable, and recoverable nonfatal events; `i5400_process_nonfatal_error_info()` handles CE and misc categories. Topology uses `i5400_get_devices()`, `i5400_get_mc_regs()`, `calculate_dimm_size()`, and `i5400_init_dimms()`.

## Control Flow
Probe accepts device 16 function 0, allocates branch/channel/slot EDAC layers, obtains the branchmap/error and FBD branch devices, reads topology registers, computes DIMM size matrix, fills EDAC DIMM metadata with FB-DDR2 and SDDC/Chipkill-like modes, enables error masks if memory exists, registers the controller, clears stale errors, and creates a generic PCI parity controller. Polling reads hardware error state, processes fatal first, then nonfatal CE/UE/recoverable/misc errors.

## State and Persistence
Runtime state is the EDAC private `i5400_pvt`, global `i5400_pci`, PCI device references, and modified FBD error mask registers. Error status is cleared by writing back observed bits. No on-disk persistence exists.

## Dependencies and Integration
The driver depends on Intel 5400 PCI IDs, PCI config access, EDAC memory-controller APIs, EDAC PCI generic parity support, and common kernel helpers such as `find_first_bit()` and string choice helpers.

## Risks
The function name `i5400_proccess_non_recoverable_info` has a spelling error but is internally consistent. Error-name lookup assumes a valid bit within `error_name[]`; unsupported/reserved bits may produce sparse-array nulls if masks change. Like i5000, error reporting is enabled without restoring original masks on remove. Multi-function PCI enumeration must match firmware exposure.

## Test Signals
Signals include correct branch/channel/slot DIMM topology, FB-DDR2 EDAC modes including single-DIMM SECDED downgrade, CE/UE/fatal/recoverable reports with decoded bank/rank/buffer/RAS/CAS, mask enablement, generic PCI parity controller creation, and balanced PCI references on remove/failure.
