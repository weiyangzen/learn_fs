# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_route_values/ni_mseries.c

## Purpose
This M-series family table maps NI M-series global signal routes to route register values. It is the largest of the route-value family tables in this item and covers PFI, RTSI, counter, AI, AO, DI, DO, timebase, analog comparison, SCXI, and RGOUT paths.

## Important APIs, Types, And Data
The exported object is `const struct family_route_values ni_mseries_route_values` with `.family = "ni_mseries"`. The inspected file contains 1,503 destination marker rows by simple count, including 1,222 `I(...)` entries and 224 `U(...)` entries, with no `V(...)` entries. It uses `Gi_SRC(val, subsel)` for M-series counter source subselect encodings and includes comments about DAQ-STC2 documentation gaps, M-series manual evidence, NI-MAX-derived guesses, and MHDDK examples.

## Control Flow
The file is static data. At runtime, M-series drivers select the table through `ni_assign_device_routes()`, the generic route helpers index `register_values[dest][src]`, and register programming uses the unmarked payload. Indirect RTSI and shared mux behavior is coordinated with the state fields and macros in `ni_stc.h`.

## State And Persistence
The runtime table is immutable. Maintenance state is represented by marker macros and comments: `I()` means implemented but needing testing, while `U()` records not-implemented encodings for tooling. The kernel only persists the compiled non-zero `I()`/`V()` availability.

## Dependencies And Integration Points
It includes `../ni_route_values.h` and `all.h`. `ni_mio_common.c` uses this table for `ni_mseries` route assignment and then programs PFI, RTSI, RGOUT0, and shared mux registers using the STC/M-series macros. The route table must align with M-series board device-route tables such as PCI/PXI 62xx/625x/673x.

## Risks
This file carries high uncertainty: gate-select notes explicitly say some `CtrAux` and `CtrArmStartTrigger` values are guesses, some routes are inferred from NI-MAX, and timebase comments mention MHDDK versus hardware-document ambiguity. Because the table is broad, a single wrong family encoding can affect many boards. `Gi_SRC()` packing must remain compatible with the seven-bit route payload mask.

## Test Signals
Existing tests cover m-series assignment for `pci-6220`. Stronger signals would include route-count snapshots for representative M-series boards, hardware-backed route programming tests for PFI and RTSI, and conversion round trips that preserve `Gi_SRC()` expressions and comments. Tests should explicitly cover DI/DO sample clocks because those are M-series-specific additions.
