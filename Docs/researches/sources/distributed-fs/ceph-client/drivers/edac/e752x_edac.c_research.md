# sources/distributed-fs/ceph-client/drivers/edac/e752x_edac.c

## Purpose
This file implements PCI EDAC support for Intel e7520, e7525, e7320, and i3100 memory controllers. It decodes DRAM ECC errors and optional non-memory chipset errors from PCI configuration space, supports hardware scrub-rate configuration, and creates a generic EDAC PCI controller for broader PCI error reporting.

## Important APIs, Types, And Functions
`struct e752x_pvt` stores PCI devices for controller and error functions, memory remap registers, symmetric mapping state, row map data, map type, and device metadata. `struct e752x_error_info` snapshots global, hub/NSI, system-bus, memory-buffer, and DRAM first/next error registers plus logged addresses and syndromes.

Important functions include `e752x_probe1()`, `e752x_init_one()`, `e752x_remove_one()`, `e752x_get_devs()`, `e752x_init_csrows()`, `e752x_init_mem_map_table()`, `e752x_get_error_info()`, `e752x_process_error_info()`, `e752x_check()`, `do_process_ce()`, `do_process_ue()`, `set_sdram_scrub_rate()`, and `get_sdram_scrub_rate()`.

## Control Flow
Module init calls `opstate_init()` and registers a PCI driver. Probe enables the PCI device, checks whether error function 0:1 is hidden and optionally unhides it if `force_function_unhide` is set, determines channel mode, allocates a chip-select/channel EDAC topology, locates controller and error PCI devices, fills controller metadata and scrub callbacks, determines row mapping, initializes csrows from DRB/DRA/DRC/DDRCSR registers, loads TOLM/remap registers, registers the MC, enables error reporting masks/SMI settings, clears stale errors, and creates a generic PCI EDAC controller.

Polling `e752x_check()` snapshots and clears first/next global and subdomain registers in `e752x_get_error_info()`, then decodes them in `e752x_process_error_info()`. DRAM CE/UE reports include page, offset, syndrome, row, and channel when possible. Non-memory domains log warning text when `report_non_memory_errors` allows it, while DRAM always participates in reporting.

## State And Persistence
PCI config registers hold latched first/next error state and are cleared after readout. Private state caches PCI devices, remap boundaries, and row remap tables. Module parameters control hidden function access, EDAC op state, system-bus parity policy, and non-memory error logging. EDAC counters and DIMM metadata persist while the controller is registered.

## Dependencies And Integration Points
The driver depends on PCI IDs/config-space access, x86 CPU model text for sysbus parity auto-detection, EDAC MC APIs, EDAC PCI generic control APIs, and module parameters. It integrates with `/sys/devices/system/edac/mc` and EDAC PCI reporting.

## Risks
Unhiding device 0 function 1 can conflict with BIOS expectations, and the driver warns accordingly. Hardware address mapping includes several FIXME notes and special symmetric/remap handling, so row/channel attribution is risky on unusual configurations. Non-memory logging is controlled separately from EDAC memory reporting. The code assumes at most one controller instance by using MC index 0 and a single global `e752x_pci`.

## Test Signals
Signals include PCI probe for each supported ID, hidden function refusal/forced unhide behavior, csrow population from DRB boundaries, SECDED versus S4ECD4ED mode selection, scrub-rate set/get mapping for e752x and i3100 tables, stale error clearing, and CE/UE sysfs counter changes after induced PCI error bits.
