# sources/distributed-fs/ceph-client/drivers/char/agp/efficeon-agp.c

## Purpose
This file implements AGPGART support for Transmeta Efficeon TM8000 integrated northbridges. It uses Intel-like AGP control registers plus an Efficeon-specific two-level GATT programmed through the `EFFICEON_ATTPAGE` register.

## Important APIs, Types, and Functions
Key functions are `efficeon_fetch_size()`, `efficeon_configure()`, `efficeon_cleanup()`, `efficeon_tlbflush()`, `efficeon_create_gatt_table()`, `efficeon_free_gatt_table()`, `efficeon_insert_memory()`, `efficeon_remove_memory()`, `agp_efficeon_probe()`, `agp_efficeon_remove()`, and `agp_efficeon_resume()`. The bridge callbacks are collected in `efficeon_driver`; L1 page pointers live in `efficeon_private.l1_table`.

## Control Flow
Probe matches Transmeta host bridges, verifies AGP capability and exact Efficeon device ID, allocates a bridge, enables the PCI device, assigns BAR0 if BIOS left it unset, reads AGP status, and registers the bridge. GATT creation allocates zeroed second-level pages for the aperture size, flushes them with `clflush`, records them in a 64-entry L1 array, and writes physical page address plus PAT/present/index bits to `EFFICEON_ATTPAGE`. Insert/remove writes PTEs directly into the second-level pages, flushes modified cache lines, and toggles AGP TLB control.

## State and Persistence Behavior
Runtime state is the L1 table of allocated pages, generic bridge data, and Efficeon/Intel-compatible PCI config registers. Cleanup clears L1 hardware entries, frees pages, disables NBXCFG aperture bits, and restores previous aperture size.

## Dependencies and Integration Points
It depends on PCI, generic AGP backend, Intel AGP register definitions from `intel-agp.h`, x86 `cpuid_ebx()` and `clflush`, and Transmeta PCI IDs.

## Risks
The driver assumes a valid CLFLUSH line size from CPUID; a zero or unexpected value would break flush loops. Insert skips missing L1 pages rather than failing, which could hide inconsistent GATT setup. The comments note module unload/S3 concerns. BIOS resource repair through `pci_assign_resource()` is necessary to avoid crashes but can fail. Static `agp_initialised` prevents duplicate registration but is not synchronized.

## Test Signals
Test Efficeon hardware probe with and without BIOS BAR assignment, aperture sizes 32-256 MB, GATT allocation/free, bind/unbind with cache-line flush validation, suspend/resume reconfiguration, and repeated module load/unload behavior.
