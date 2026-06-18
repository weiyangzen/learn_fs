<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/layouts.c

## Purpose
Implements the NVMEM layout bus, allowing DT-described layout parsers to bind below an NVMEM provider and dynamically add cells.

## Important APIs, Types, And Functions
Exports `__nvmem_layout_driver_register()`, `nvmem_layout_driver_unregister()`, and `of_nvmem_layout_get_container()`. Internal flow uses `nvmem_layout_bus_type`, `nvmem_layout_bus_match()`, `nvmem_layout_bus_probe()`, `nvmem_layout_bus_remove()`, `nvmem_layout_create_device()`, `nvmem_layout_bus_populate()`, `nvmem_populate_layout()`, and `nvmem_destroy_layout()`.

## Control Flow
During provider registration, the core calls `nvmem_populate_layout()`. This finds the `nvmem-layout` child, skips nodes without `compatible` and fixed layouts handled elsewhere, creates a single `struct nvmem_layout` device under the provider, marks the DT node populated, and lets a layout driver bind by OF compatible. Driver probe sets `layout->add_cells` and calls `nvmem_layout_register()` in the core.

## State And Persistence
Runtime state is the layout device linked bidirectionally with `nvmem->layout`. Device release drops the DT node reference and frees the layout. DT populated flags prevent duplicate devices.

## Dependencies And Integration Points
Depends on OF, driver core buses, device links sync-state pause/resume, DMA mask setup, MSI OF configuration, and internal NVMEM core structures. Layout drivers in `drivers/nvmem/layouts/` register on this bus.

## Risks
Provider/layer lifetime must be paired: destroying a provider must unregister the layout device and clear OF populated flags. Fixed layouts are intentionally skipped here and parsed in core, so behavior is split. Missing `remove` callbacks reject layout drivers.

## Test Signals
Register providers with no layout, fixed layout, and dynamic layout nodes; bind/unbind layout modules; verify OF_POPULATED_BUS flag clearing on teardown; and test non-OF builds through stubs in `internals.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts.c -->
