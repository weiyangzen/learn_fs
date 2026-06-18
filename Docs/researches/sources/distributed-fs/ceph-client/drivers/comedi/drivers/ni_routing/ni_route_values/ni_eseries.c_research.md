# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_route_values/ni_eseries.c

## Purpose
This family table maps NI E-series signal routes to DAQ-STC register encodings. It is used by E-series MIO boards to convert validated route pairs into route-programming values.

## Important APIs, Types, And Data
The exported object is `const struct family_route_values ni_eseries_route_values` with `.family = "ni_eseries"`. The table covers PFI outputs, trigger-line/RTSI routing, RTSI board muxes, counter source/gate/out, AI sample/start/reference/convert/pause routes, AO sample/start/pause routes, master timebase, and `NI_RGOUT0`. The inspected source contains 480 destination rows by marker-line count: 290 `I(...)` entries and 151 `U(...)` entries. It also records E-series-specific notes, including that `TRIGGER_LINE(6)` is generally not connected to `RTSI(6)`.

## Control Flow
There is no local control flow. Generic routing code checks this table after selecting it by family string. Non-zero entries become available register encodings; `UNMARK()` yields the value passed to lower-level register programming helpers.

## State And Persistence
All state is immutable source and compiled data. Comments preserve maintenance knowledge about conflicting DAQ-STC/MHDDK information, such as the `NI_AI_StartTrigger -> NI_AO_StartTrigger` value disagreement.

## Dependencies And Integration Points
The file depends on `ni_route_values.h`, NI signal constants, and route-output constants such as `NI_PFI_OUTPUT_*` and `NI_RTSI_OUTPUT_RTSI_OSC`. It is aggregated through `ni_all_route_values[]` and consumed by `ni_mio_common.c` when E-series boards assign routing tables.

## Risks
Several `U()` entries are known but not implemented, and `I()` entries are not marked fully tested. The E-series RTSI note means a route may look syntactically similar to other trigger lines while differing electrically. Conflicting hardware documentation comments should be treated as active risk when changing AO start or timebase routes.

## Test Signals
Existing `ni_routes_test` checks e-series assignment for `pci-6070e`. Additional tests should validate a PFI output route, an indirect RTSI route, `NI_RGOUT0`, and the documented `TRIGGER_LINE(6)` distinction. Regeneration should preserve comments that are not derivable from CSV alone.
