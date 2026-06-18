# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_route_values.c

## Purpose
This generated registry file gathers all NI route-value family tables into one null-terminated array for the generic NI routing code. It does not contain per-route encodings itself; it imports the generated family tables and exposes a discoverable list.

## Important APIs, Types, And Data
The exported data is `const struct family_route_values *const ni_all_route_values[]`. In this tree it contains `&ni_660x_route_values`, `&ni_eseries_route_values`, `&ni_mseries_route_values`, followed by `NULL`. The element type is declared in `ni_route_values.h` and represents a family name plus a two-dimensional destination/source register-value matrix.

## Control Flow
There is no executable control flow. `ni_routes.c::ni_find_route_values()` iterates this array until `NULL`, compares `.family` strings with the requested device family, and returns a flattened pointer to `register_values[0][0]`.

## State And Persistence
The file contributes immutable static kernel data. Persistence is limited to the compiled object. Runtime drivers store a pointer into the selected table in `struct ni_route_tables`, but this file owns no mutable state.

## Dependencies And Integration Points
It includes `ni_route_values.h` for the struct and `ni_route_values/all.h` for extern declarations. It is referenced by the Comedi drivers Makefile through `ni_routing/ni_route_values.o` and consumed by `ni_routes.c`. Tools in `ni_routing/tools` regenerate this file from CSV route-value sheets.

## Risks
If a family table is missing from this list, devices in that family can have valid device-route tables but still fail `ni_assign_device_routes()` with `-ENODATA`. Ordering is not semantically important, but duplicate `.family` strings would make later entries unreachable. The terminating `NULL` is mandatory for lookup safety.

## Test Signals
`drivers/comedi/drivers/tests/ni_routes_test.c` already checks assignment for e-series and m-series families. Regression tests should also assert every generated family table in `ni_route_values/all.h` appears exactly once in `ni_all_route_values[]`.
