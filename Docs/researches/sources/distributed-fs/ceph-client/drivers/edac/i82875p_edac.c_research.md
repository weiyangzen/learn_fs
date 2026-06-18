# sources/distributed-fs/ceph-client/drivers/edac/i82875p_edac.c Research

## Purpose
`i82875p_edac.c` supports Intel 82875P/E7210-style DDR memory hubs. It exposes the hidden overflow device needed for DRB/DRA/MMIO access, maps its BAR, derives single/dual-channel EDAC rows, polls host-bridge ECC status, and reports corrected or uncorrected DRAM errors.

## Important APIs, Types, and Functions
`struct i82875p_pvt` stores the overflow PCI device and mapped overflow MMIO window. `i82875p_setup_overfl_dev()` finds or unhides device 6 function 0, enables it, requests regions when possible, and maps BAR0. `i82875p_get_error_info()` snapshots `ERRSTS`, `EAP`, channel status (`DES`), syndrome, and a second `ERRSTS` read, handling the same CE-overwritten-by-UE race pattern as other legacy Intel drivers. `i82875p_process_error_info()` maps page address to csrow and reports UE or CE, including channel when dual-channel mode is active.

`dual_channel_active()` decodes DRC channel mode. `i82875p_init_csrows()` reads DRB registers from the overflow window, converts cumulative 64 MiB boundaries to page ranges, divides pages across active channels, and fills DIMM metadata with DDR type, SECDED/no-EDAC mode, 4 KiB grain, and unknown device width. `i82875p_probe1()` owns allocation, overflow setup, EDAC registration, stale error clearing, and generic PCI EDAC creation.

## Control Flow
Module init initializes opstate, registers the PCI driver, and uses a fallback host-bridge scan if the probe did not run. Probe enables the device, sets up the overflow MMIO path, reads DRC, allocates a chip-select/channel EDAC topology, initializes rows, clears stale counters, registers the MC, and creates generic PCI control. Polling calls `i82875p_check()`. Removal releases generic PCI control, unregisters the MC, unmaps the overflow window, disables/puts the overflow device, and frees EDAC state.

## State and Persistence
Persistent runtime state is limited to PCI device references, the overflow MMIO mapping, EDAC MC metadata, and the global `mci_pdev`/`i82875p_pci` pointers. Error status is cleared after reads. No disk state exists.

## Dependencies and Integration Points
The driver depends on PCI config and resource APIs, low-level `ioremap`/MMIO access, EDAC MC APIs, generic PCI EDAC, and Intel 82875 PCI IDs. It integrates with EDAC polling through `mci->edac_check`.

## Risks and Edge Cases
Device 6 can be hidden by BIOS and the driver writes a magic config bit to expose it. Region ownership is conditional under `CORRECT_BIOS`, so resource cleanup behavior differs by build. The error-address-to-row path does not validate row before reporting. Register snapshots are racy. The code assumes a single controller and uses fallback registration that can interact awkwardly with normal PCI probing.

## Test Signals
Test by loading on 82875P/E7210 hardware, confirming device 6 exposure and MMIO map, checking row sizes against DRB registers, validating dual-channel channel attribution from `DES`, injecting/observing CE and UE status bits, and unloading with the overflow BAR unmapped and PCI references released.
