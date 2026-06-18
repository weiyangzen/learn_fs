# sources/distributed-fs/ceph-client/drivers/char/agp/sworks-agp.c

## Purpose

`sworks-agp.c` implements ServerWorks AGPGART support using a two-level GATT. It allocates a page directory plus per-directory GATT pages, maps ServerWorks MMIO registers, configures AGP aperture and caching behavior, and provides two-level insertion/removal and TLB flush hooks.

## Important APIs, Types, And Functions

- `struct serverworks_page_map` holds a real page and write-combining/uncached remapped pointer.
- `serverworks_private` tracks the secondary ServerWorks device, MMIO registers, GATT page array, scratch directory, and config register offsets.
- GATT lifecycle: `serverworks_create_page_map()`, `serverworks_free_page_map()`, `serverworks_create_gatt_pages()`, `serverworks_free_gatt_pages()`, `serverworks_create_gatt_table()`, and `serverworks_free_gatt_table()`.
- Runtime hooks: `serverworks_fetch_size()`, `serverworks_configure()`, `serverworks_cleanup()`, `serverworks_tlbflush()`, `serverworks_insert_memory()`, `serverworks_remove_memory()`, and `serverworks_agp_enable()`.
- PCI integration: `agp_serverworks_probe()`, `agp_serverworks_remove()`, table and module init/exit.

## Control Flow

Probe accepts documented ServerWorks HE/LE-style devices, rejects CNB20HE, finds function 1, validates 64-bit aperture/MMIO upper bits are zero, sets register offsets, allocates a bridge, and registers it. GATT creation allocates a page directory, a scratch directory filled with scratch entries, points all directory entries to the scratch directory, then allocates real second-level pages and installs their addresses. Configure maps MMIO, enables GART cache behavior, writes GATT base, sets command bits, enables AGP on the secondary device, flushes, reads AGP capability/mode, disables chipset caching bits, and enables a feature bit. Insertion maps AGP page offsets through directory/page offsets to second-level tables and writes masked entries.

## State And Persistence Behavior

Persistent state includes the allocated two-level GATT pages, scratch directory, `serverworks_private.registers` MMIO mapping, selected companion PCI device, and ServerWorks config/MMIO register contents. Removal restores entries to scratch values and flushes before and after clearing. Cleanup unmaps MMIO, while bridge teardown frees GATT pages.

## Dependencies And Integration Points

The file depends on x86 `set_memory_uc/wb`, PCI resource/config APIs, generic AGP memory helpers, and global AGP bridge state. It integrates with the AGP core as an `LVL2_APER_SIZE` driver because `generic.c` cannot manage two-level tables.

## Risks And Edge Cases

Page-map creation notes missing PCI posting flush after filling entries. Two-level indexing depends on `gart_bus_addr`; incorrect aperture base produces wrong directory selection. Probe rejects 64-bit upper bits rather than handling true 64-bit addresses. TLB flush loops can stall up to three seconds each for post and directory flush. Error cleanup must free partially allocated page maps and release companion device refs.

## Test Signals

Probe supported ServerWorks hardware and validate MMIO mapping, GATT base programming, and AGP enable logs. Bind/unbind across directory boundaries to test `GET_PAGE_DIR_IDX()`/`GET_GATT_OFF()` arithmetic. Watch for TLB post/dir flush timeout logs. Static tests should inspect partial allocation cleanup and resource lifetime around `svrwrks_dev`.
