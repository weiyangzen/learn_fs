# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes.h

## Purpose

`ni_device_routes.h` is the private bridge header between the generated device-route registry and the generic NI route implementation. It lets `ni_routes.c` see `ni_device_routes_list[]` without including every per-board generated file directly.

## Important APIs, Types, and Functions

The only declaration is `extern struct ni_device_routes *const ni_device_routes_list[];`. The header includes `../ni_routes.h`, so consumers get the definitions for `struct ni_device_routes` and `struct ni_route_set`.

There are no functions or local types. The include guard is named `_COMEDI_DRIVERS_NI_ROUTINT_NI_DEVICE_ROUTES_H`; the spelling of `ROUTINT` is unusual but internally consistent and therefore harmless unless another header accidentally reuses the corrected spelling.

## Control Flow, State, and Persistence

This header has no control flow and no state. Its compile-time role is to publish the generated registry symbol to `ni_routes.c` and to the generated registry implementation itself.

## Dependencies and Integration Points

It depends on `ni_routes.h` and is included by `ni_routing/ni_device_routes.c`. The data it declares is consumed by `ni_routes.c` for route-table assignment and by generator tooling that includes generated C data for conversion.

## Risks and Test Signals

The main risk is declaration drift: if `ni_device_routes_list[]` changes constness, element type, or sentinel convention without updating both this header and `ni_routes.c`, board lookup or module initialization can break. Build coverage is the primary test signal, while runtime `ni_assign_device_routes()` tests confirm the declared list is populated and sentinel-terminated.
