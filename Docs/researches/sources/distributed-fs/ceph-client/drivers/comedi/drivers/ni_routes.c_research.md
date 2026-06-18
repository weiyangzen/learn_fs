# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routes.c

## Purpose
`ni_routes.c` is a helper module for National Instruments Comedi signal routing. It assigns per-device route tables, sorts route metadata for efficient search, validates source-to-destination pairs, converts valid routes to hardware register values, enumerates valid routes for userspace, and reverse-maps register values back to NI global signal names.

## Important APIs, Types, And Functions
The module operates on `struct ni_route_tables`, `struct ni_device_routes`, and `struct ni_route_set` from `ni_routes.h`. Route values come from generated/static routing headers `ni_routing/ni_route_values.h` and `ni_routing/ni_device_routes.h`. `RVi()` indexes the flattened destination-by-source register-value matrix; `B()` converts NI global names to table indexes, and `V()`/`UNMARK()` mark/unmark valid register values.

Exported APIs include `ni_assign_device_routes()`, `ni_count_valid_routes()`, `ni_get_valid_routes()`, `ni_is_cmd_dest()`, `ni_sort_device_routes()`, `ni_find_route_set()`, `ni_route_set_has_source()`, `ni_lookup_route_register()`, `ni_route_to_register()`, and `ni_find_route_source()`. Internal helpers locate route-value tables by device family and valid-route tables by board name or alternate board name, sort destination/source arrays, and implement bsearch comparators.

## Control Flow
At module init, `ni_sort_all_device_routes()` walks every entry in `ni_device_routes_list` and calls `ni_sort_device_routes()`. Sorting counts route sets until a zero destination sentinel, sorts route sets by destination, counts each source list until a zero sentinel, and sorts sources. Runtime users call `ni_assign_device_routes()` during device attach to bind a board to its family register-value table and valid-route set. Query paths then use binary search for destination route sets and sources.

`ni_route_to_register()` first verifies that a destination exists for the device and that the requested source is listed as valid. It then looks up the direct register value. If the destination is an RTSI channel and no direct route exists, it tries indirect routing through `NI_RGOUT0` or `NI_RTSI_BRD(0..3)` and returns special register encodings when a shared mux is needed. `ni_get_valid_routes()` enumerates all direct and valid indirect RTSI routes into source/destination pairs for Comedi `INSN_DEVICE_CONFIG_GET_ROUTES`.

## State And Persistence Behavior
The module mutates route metadata in memory by sorting `ni_device_routes_list` at module init and setting `n_route_sets`/`n_src` counts. It does not allocate persistent storage, write files, or persist user choices. Assigned route tables are stored by caller-owned `struct ni_route_tables`.

## Dependencies And Integration Points
The code depends on kernel `sort()`, `bsearch()`, `slab`, Comedi global route names/macros, and the generated NI routing headers. It exports symbols used by NI MIO and NI-TIO integration code to validate Comedi trigger arguments, global route connect/disconnect operations, and route enumeration.

## Risks
The route arrays rely on sentinel values and module-init sorting. If a caller used route tables before module init sorting, binary searches would be invalid; normal module initialization avoids that. Invalid or incomplete generated route data can make valid hardware routes unavailable or expose wrong register values. The indirect RTSI encoding is compact and caller-sensitive: consumers must understand `BIT(6)` as a shared mux requirement and not a direct register value.

## Test Signals
Tests should cover table assignment by family/board/alternate board name, route count/enumeration consistency, direct and indirect RTSI route conversion, invalid source/destination bounds, reverse lookup by register value, sorting idempotence, bsearch behavior after sorting, and integration with MIO global connect/disconnect and command-trigger validation.
