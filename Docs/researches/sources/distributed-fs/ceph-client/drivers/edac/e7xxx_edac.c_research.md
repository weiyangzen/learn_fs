# sources/distributed-fs/ceph-client/drivers/edac/e7xxx_edac.c

## Purpose
This file implements PCI EDAC support for older Intel E7500, E7501, E7505, and E7205 memory controllers. It decodes DRAM first/next correctable and uncorrectable ECC log registers and exposes memory-controller reporting through the EDAC MC core.

## Important APIs, Types, And Functions
`struct e7xxx_pvt` stores the error-reporting bridge device and memory remap boundaries. `struct e7xxx_error_info` snapshots DRAM first/next error bits, CE log address/syndrome, and UE log address. Device metadata is stored in `e7xxx_devs[]`.

Primary functions are `e7xxx_probe1()`, `e7xxx_init_one()`, `e7xxx_remove_one()`, `e7xxx_init_csrows()`, `e7xxx_get_error_info()`, `e7xxx_process_error_info()`, `e7xxx_check()`, `process_ce()`, `process_ue()`, `process_ce_no_info()`, `process_ue_no_info()`, `e7xxx_find_channel()`, and `ctl_page_to_phys()`.

## Control Flow
Module init calls `opstate_init()` and registers a PCI driver. Probe reads DRC channel/granularity/configuration, allocates a chip-select/channel EDAC topology, finds the error-reporting function with `pci_get_device()`, fills metadata and page-remap callback, initializes csrows from DRB/DRA/DRC, reads TOLM/remap base/remap limit, clears stale error info, registers with EDAC, and creates a generic PCI EDAC controller.

During polling, `e7xxx_check()` snapshots DRAM first/next error registers. If CE or UE bits are set, the driver reads the associated log address and syndrome registers, clears the first/next bits with `pci_write_bits8()`, and reports CE/UE events. If both first and next entries contain the same class, only one address is available and the second report is emitted as no-info overflow.

## State And Persistence
PCI configuration registers hold latched error state and are cleared by polling. Private state caches bridge device and remap limits for `ctl_page_to_phys()`. EDAC stores row/channel/DIMM metadata and counters for the lifetime of the registered controller. A single global `e7xxx_pci` tracks the generic PCI control object.

## Dependencies And Integration Points
The driver depends on PCI config access, supported Intel PCI IDs, EDAC MC APIs, EDAC PCI generic control, and the module parameter `edac_op_state`. It integrates with EDAC polling or NMI mode as initialized by `opstate_init()`.

## Risks
The driver assumes at most one instance and hardcodes MC index 0. Address conversion has FIXME comments and uses legacy register-specific shifts. Channel detection from syndrome is heuristic. If first and next logs overflow, detailed location is unavailable for later events. The error-reporting PCI function must exist and be accessible.

## Test Signals
Tests should validate all PCI IDs, channel/granularity handling, csrow sizing, remap callback behavior, CE/UE log decoding, no-info overflow reporting, stale error clearing before registration, and generic PCI EDAC creation/release.
