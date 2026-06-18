# sources/distributed-fs/ceph-client/drivers/char/agp/amd-k7-agp.c

## Purpose
This file implements AGPGART support for AMD K7-era Irongate/761/760MP host bridges using a two-level GATT and MMIO control registers.

## Important APIs, Types, and Functions
Important internals include `struct amd_page_map`, `amd_create_page_map()`, `amd_create_gatt_pages()`, `amd_create_gatt_table()`, `amd_irongate_fetch_size()`, `amd_irongate_configure()`, `amd_irongate_cleanup()`, `amd_irongate_tlbflush()`, `amd_insert_memory()`, and `amd_remove_memory()`. PCI lifecycle functions are `agp_amdk7_probe()`, `agp_amdk7_remove()`, and resume `agp_amdk7_resume()`.

## Control Flow
Probe matches AMD host-bridge IDs, verifies AGP capability, allocates a bridge, attaches `amd_irongate_driver`, applies known errata flags for AMD 751/761 revisions and NVIDIA graphics combinations, reads AGP mode, stores PCI driver data, and registers with the backend. GATT creation allocates an uncached page directory and per-4MB GATT pages, fills them with scratch-page mappings, and points directory entries at GATT pages. Configure ioremaps MMIO, writes GATT base, sync/indexing registers, enables GART translation, programs aperture size, and flushes TLB.

## State and Persistence Behavior
Driver state includes `amd_irongate_private.registers`, `gatt_pages`, and `num_tables`, plus generic bridge state. It changes page cacheability with `set_memory_uc()`/`set_memory_wb()`, writes MMIO GART registers, and restores aperture size/disables GART on cleanup.

## Dependencies and Integration Points
It depends on PCI host bridge IDs, generic AGP backend helpers, x86 memory attribute helpers, MMIO mapping, and AGP mode errata flags consumed by generic enable logic.

## Risks
Two-level GATT indexing macros depend on aperture bus address consistency. Page-table pages are made uncached and must be restored on free. Error unwind in GATT page allocation must free partially allocated tables. Probe errata uses global `agp_bridge` soon after bridge allocation, relying on singleton behavior. Resume only reruns configure and assumes GATT structures remain intact.

## Test Signals
Test supported AMD 751/761/760MP hardware, aperture size fetch, GATT allocation/free under memory pressure, bind/unbind occupancy checks, TLB flushes, errata mode limiting, suspend/resume, and module unload after AGP memory use.
