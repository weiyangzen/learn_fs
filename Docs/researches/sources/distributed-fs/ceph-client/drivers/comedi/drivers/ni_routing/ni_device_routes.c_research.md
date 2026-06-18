# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes.c

## Purpose

`ni_device_routes.c` is the generated board-route registry. It builds the null-terminated `ni_device_routes_list[]` array that `ni_routes.c` scans by board name when `ni_assign_device_routes()` selects valid routes for an attached NI board.

## Important APIs, Types, and Functions

The file defines one exported data object, `struct ni_device_routes *const ni_device_routes_list[]`. Its entries point at generated per-board `struct ni_device_routes` objects such as `ni_pci_6070e_device_routes`, `ni_pci_6220_device_routes`, `ni_pci_6259_device_routes`, and `ni_pci_6534_device_routes`, with a final `NULL` sentinel.

There are no functions. The important API contract is data shape: the list must contain each route object that should be discoverable by exact board-name string matching in `ni_find_valid_routes()`.

## Control Flow, State, and Persistence

Control flow is data-driven. During NI routing module initialization, `ni_sort_all_device_routes()` iterates this list and calls `ni_sort_device_routes()` for every entry, which fills `n_route_sets`, fills each route set's `n_src`, and sorts arrays in place. During device attach, `ni_find_valid_routes()` iterates the same list until it finds a matching `.device` string or reaches `NULL`.

The file has no persistent storage. Its only runtime state effect is that pointed-to generated route arrays become sorted and counted after module initialization.

## Dependencies and Integration Points

It includes `ni_device_routes.h` for the list declaration and `ni_device_routes/all.h` for per-board extern declarations. It is built into the Comedi NI routing support via the drivers Makefile along with each generated board table. Its primary consumer is `ni_routes.c`; generator tooling under `ni_routing/tools` also includes this file when converting generated C tables back to Python/CSV data.

## Risks and Test Signals

The critical risk is registry incompleteness: a generated board object can compile and have an extern in `all.h` but still be undiscoverable if it is omitted from `ni_device_routes_list[]`. In this snapshot, `all.h` declares `ni_pxie_6535_device_routes` and `ni_pxie_6738_device_routes`, and the Makefile builds those objects, but this registry list does not include them. That should be treated as an integration signal to verify whether those boards intentionally use alternate board names or are accidentally absent from lookup.

Test signals are `ni_assign_device_routes()` success for every intended board string, unit-test coverage that the list resolves representative E-series/M-series/660x boards, and generated-table consistency checks comparing `all.h`, `ni_device_routes.c`, the Makefile object list, and actual `ni_device_routes/*.c` files.
