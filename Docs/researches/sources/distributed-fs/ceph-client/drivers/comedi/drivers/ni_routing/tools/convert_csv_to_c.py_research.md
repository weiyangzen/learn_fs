# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/tools/convert_csv_to_c.py

## Purpose
This Python generator converts semicolon-delimited CSV routing sheets into generated C route-value and device-route source trees under `c/`.

## Important APIs, Types, And Functions
`c_to_o()` formats Makefile object paths. `routedict_to_structinit_single()` converts a route-value CSV sheet into a `struct family_route_values` initializer and enforces register strings matching `V(...)`, `I(...)`, or `U(...)`. `routedict_to_routelist_single()` converts a device-route CSV sheet into a sentinel-terminated `struct ni_route_set` array. `DeviceRoutes` and `RouteValues` subclass `CSVCollection`, define generated file templates, emit per-item `.c` files, `all.h`, central list files, and `.mk` fragments. The CLI accepts `--route_values` and `--device_routes`.

## Control Flow
CSV data is loaded into `source -> destination -> cell` dictionaries. For C output the script reverses that to destination-major order, sorts signals by numeric Comedi constant using `eval(..., comedi_h.__dict__, Locals)`, and writes generated files. With both CLI flags, it runs `RouteValues().save()` and `DeviceRoutes().save()`.

## State And Persistence
It creates and overwrites files below `c/`, including `ni_route_values.c`, `ni_route_values/*.c`, `ni_route_values/all.h`, `route-values.mk`, `ni_device_routes.c`, `ni_device_routes/*.c`, `ni_device_routes/all.h`, and `device-route.mk`. It does not edit checked-in sources directly.

## Dependencies And Integration Points
It depends on generated `comedi_h.py`, `CSVCollection`, and CSV folders `csv/route_values` and `csv/device_routes`. Its output is intended to be compared with or copied into `drivers/comedi/drivers/ni_routing` and to update Makefile object lists.

## Risks
The script uses `eval()` on CSV field names and source names, so malformed CSV can execute names in the `comedi_h` namespace or fail generation. It can overwrite generated output without atomic writes. Template comments contain stale wording such as route-value files saying "NI 660x hardware" for all families, which can propagate misleading documentation. Manual notes in checked-in annotated files may be lost if generated output replaces them wholesale.

## Test Signals
Run with `--route_values --device_routes` after generating `comedi_h.py`, then compile the resulting C. Tests should include invalid register marker strings, unknown signal names, sorting stability, and exact null sentinel emission for both route-set arrays and central pointer lists.
