# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_route_values/all.h

## Purpose
This generated header declares the family route-value tables that are aggregated by `ni_route_values.c` and referenced by generated per-family C files.

## Important APIs, Types, And Data
It declares `extern const struct family_route_values ni_660x_route_values`, `ni_eseries_route_values`, and `ni_mseries_route_values`. It includes `../ni_route_values.h`, so all declarations share the same table type and marker macro definitions.

## Control Flow
There is no control flow. It is an extern declaration bridge between generated objects and the central array initializer.

## State And Persistence
The header owns no state. It exposes immutable static objects defined in sibling `.c` files and compiled into the NI routing object set.

## Dependencies And Integration Points
`ni_route_values.c` includes this file to build `ni_all_route_values[]`. Each generated family `.c` file includes it as well, ensuring declarations match definitions. `convert_csv_to_c.py::RouteValues` writes this file as `c/ni_route_values/all.h`.

## Risks
Missing declarations can break compilation when `ni_route_values.c` references a new family. Extra declarations without matching definitions can also fail link-time builds if used by the registry. Manual edits are likely to be overwritten by the generator.

## Test Signals
Build coverage is the main signal. A generator round trip should verify that every `csv/route_values/*.csv` sheet emits exactly one extern declaration and one registry entry.
