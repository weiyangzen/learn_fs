# sources/distributed-fs/ceph-client/drivers/char/agp/generic.c

## Purpose

`generic.c` is the shared AGPGART backend implementation used by chipset-specific AGP bridge drivers. It owns generic `struct agp_memory` allocation/freeing, GATT creation and teardown, bind/unbind operations, AGP mode negotiation, device command programming, cache flushing, and generic AGP 3.x register setup. The file is not Ceph-specific despite the source tree prefix; it is Linux kernel graphics aperture infrastructure.

## Important APIs, Types, And Functions

- Global state: `agp_gatt_table` exposes the active GATT kernel table pointer, and `agp_memory_reserved` reduces advertised aperture capacity for reserved regions.
- Key and memory lifecycle: `agp_free_key()`, `agp_create_memory()`, `agp_allocate_memory()`, `agp_free_memory()`, `agp_generic_alloc_user()`, `agp_alloc_page_array()`, and `agp_free_page_array()` allocate keyed `struct agp_memory` objects and backing page arrays.
- Binding APIs: `agp_bind_memory()` and `agp_unbind_memory()` call the current bridge driver's `insert_memory` and `remove_memory`, update `is_bound`/`pg_start`, and maintain `bridge->mapped_list`.
- GATT helpers: `agp_generic_create_gatt_table()`, `agp_generic_free_gatt_table()`, `agp_generic_insert_memory()`, and `agp_generic_remove_memory()` implement a single-level GATT filled with scratch-page entries.
- Page helpers: `agp_generic_alloc_page()`, `agp_generic_alloc_pages()`, `agp_generic_destroy_page()`, and `agp_generic_destroy_pages()` manage DMA32 zeroed pages, AGP mapping attributes, refcounts, and `current_memory_agp`.
- Mode negotiation: `agp_collect_device_status()`, `agp_generic_enable()`, `agp_device_command()`, `get_agp_version()`, `agp_v2_parse_one()`, and `agp_v3_parse_one()` sanitize requested modes against bridge and VGA capabilities.
- AGP 3.x defaults: `agp3_generic_fetch_size()`, `agp3_generic_configure()`, `agp3_generic_tlbflush()`, `agp3_generic_cleanup()`, and exported `agp3_generic_sizes`.
- Utility hooks: `global_cache_flush()`, `agp_generic_mask_memory()`, `agp_generic_type_to_mask_type()`, and `agp_generic_find_bridge()`.

## Control Flow

Chipset modules allocate and register an `agp_bridge_data` whose `agp_bridge_driver` points back to these helpers. During bridge add, the backend fetches aperture size, allocates scratch/GATT resources, configures chipset registers, and later clients allocate memory via `agp_allocate_memory()`. Binding checks bounds and occupancy, flushes CPU caches if needed, writes masked page addresses into GATT slots, posts the final read, then calls the bridge TLB flush hook. Unbinding restores scratch-page entries and flushes again.

AGP enable flows through `agp_generic_enable()`: it reads bridge AGP status, finds an AGP VGA device, intersects requested mode with bridge/card capabilities, applies bridge errata flags, sets `AGPSTAT_AGP_ENABLE`, optionally invokes `agp_3_5_enable()` for AGP 3.5 isochronous setup, and writes commands to all AGP-capable PCI devices.

## State And Persistence Behavior

Persistent runtime state lives in `agp_bridge`, `agp_bridges`, each `agp_bridge_data`, `agp_memory` objects, the allocated GATT pages, page cache attributes, PCI config registers, and per-memory flags such as `is_flushed` and `is_bound`. The file updates `atomic_t current_memory_agp` as pages are allocated/freed and uses `mapped_lock` to track bound regions. Hardware-visible persistence is the GATT contents and AGP command/config state until cleanup, suspend reconfiguration, or module removal.

## Dependencies And Integration Points

This file depends on `agp.h`, `<linux/agp_backend.h>`, PCI config accessors, DMA/page APIs, `set_memory_uc/wb` on x86, and architecture AGP cache helpers. All chipset files in this work item call into it through `struct agp_bridge_driver` callbacks. User-visible AGP ioctls and DRM paths ultimately rely on these exported symbols for memory allocation, mode setup, and bind/unbind behavior.

## Risks And Edge Cases

Single-level generic GATT routines reject `LVL2_APER_SIZE`, so two-level chipsets must provide their own implementation. Many bounds checks explicitly guard integer overflow, but consumers still depend on correct `current_size` metadata. GATT entries are noted as unable to encode addresses over 4 GB in some paths. Global `agp_bridge` usage means this code is effectively written around a singleton bridge model even though bridge structs are passed through several APIs. Cache attribute transitions and scratch-page DMA visibility are high-risk areas, especially on non-x86 paths and during partial allocation failures.

## Test Signals

Build with representative AGP drivers enabled, boot/probe on supported hardware or emulation, and exercise allocation, bind, unbind, and free through AGP users. Useful signals include correct aperture reporting via `agp_copy_info()`, no `-EBUSY` on empty GATT ranges, successful TLB flushes, restored scratch entries after unbind, correct `current_memory_agp` accounting after error paths, and AGP mode logs matching bridge/card capabilities. Static analysis should focus on overflow, lock coverage around `mapped_list`, cache attribute restoration, and failure cleanup in GATT allocation.
