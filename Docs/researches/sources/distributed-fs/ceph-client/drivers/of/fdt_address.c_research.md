# sources/distributed-fs/ceph-client/drivers/of/fdt_address.c

## Purpose
`fdt_address.c` translates addresses directly from the flattened boot FDT before a live devicetree exists. It is a minimal early-boot counterpart to normal OF address translation.

## Important APIs, types, and functions
The central type is `struct of_bus`, containing `count_cells`, `map`, and `translate` callbacks. The default bus implementation includes `fdt_bus_default_count_cells()`, `fdt_bus_default_map()`, and `fdt_bus_default_translate()`. `fdt_translate_one()` applies one `ranges` level, `fdt_translate_address()` walks parent buses, and `of_flat_dt_translate_address()` is the exported init API.

## Control flow and state
Translation starts from a node's `reg` property, reads parent `#address-cells` and `#size-cells`, copies the child address into a bounded local array, then walks up through parent offsets. Each level requires valid parent cell counts and a usable `ranges` property. Empty `ranges` means identity mapping. Non-empty `ranges` are searched for the child address, then rewritten into parent bus address cells with offset applied. Reaching the root returns the accumulated address.

## Dependencies and integration
The file depends on `initial_boot_params`, libfdt accessors, numeric helpers from OF core, and constants/macros in `of_private.h`. Early reserved-memory and boot scanners can use this when live address translation is unavailable.

## Risks and test signals
The implementation only supports the default bus translator in this file. Translation fails on missing `reg`, invalid cell counts, absent or nonmatching `ranges`, and `#size-cells == 0`. Risks are malformed FDT data and overflow-limited address cell arrays. Boot-time address/resource logs and later live-tree address KUnit tests are relevant signals.
