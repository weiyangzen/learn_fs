# subset-b-001200 NI Comedi route-table research

This grouped report covers the requested National Instruments Comedi routing API declarations and generated per-board route tables. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routes.h -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routes.h

## Purpose

`ni_routes.h` is the public helper interface for NI signal-routing support in the Comedi drivers. It defines the in-memory representation of valid device routes, binds those valid-route tables to per-family register-value tables, and exposes lookup/validation helpers used by NI MIO, NI 660x, and related drivers when users configure triggers, clocks, counters, PFI pins, and RTSI trigger lines.

## Important APIs, types, and functions

The core data types are `struct ni_route_set`, `struct ni_device_routes`, and `struct ni_route_tables`. `ni_route_set` groups all legal sources for one destination. `ni_device_routes` names a board and owns the route-set array for that board. `ni_route_tables` combines board-specific `valid_routes` with family-specific `route_values`.

The main external functions are `ni_assign_device_routes()`, `ni_find_route_set()`, `ni_route_set_has_source()`, `ni_route_to_register()`, `ni_lookup_route_register()`, `ni_is_cmd_dest()`, `ni_count_valid_routes()`, `ni_get_valid_routes()`, `ni_sort_device_routes()`, and `ni_find_route_source()`. Inline helpers include `route_is_valid()`, `route_register_is_valid()`, `ni_get_reg_value_roffs()`, `ni_get_reg_value()`, `ni_check_trigger_arg_roffs()`, and `ni_check_trigger_arg()`. Channel classifiers `channel_is_pfi()`, `channel_is_rtsi()`, and `channel_is_ctr()` encode NI naming ranges from `<linux/comedi.h>`.

## Control Flow, State, and Persistence

The header declares the route assignment and lookup flow implemented in `ni_routes.c`: a board driver calls `ni_assign_device_routes()` with a family string and board name, then stores the resulting `ni_route_tables` in device-private state. Later command/config paths call route validation or register-value helpers before programming hardware. `ni_sort_device_routes()` is part of module initialization and mutates generated route arrays in memory by counting terminator-delimited entries and sorting destinations/sources so the search helpers can use binary search.

State is not persisted to disk. Runtime state is the selected `ni_route_tables` pointer pair plus sorted generated arrays resident in the module image. The direct-register compatibility path in `ni_get_reg_value_roffs()` treats values below `NI_NAMES_BASE` as legacy register selectors, optionally shifted by `direct_reg_offset`, and only accepts them if `ni_find_route_source()` can map them back to a valid route destination.

## Dependencies and Integration Points

The header depends on Linux integer/error/bit helpers and `<linux/comedi.h>` for global NI signal names such as `NI_PFI()`, `TRIGGER_LINE()`, `NI_AI_SampleClock`, and counter names. It integrates with generated tables under `ni_routing/ni_device_routes*` and `ni_routing/ni_route_values*`. Callers include `ni_mio_common.c`, `ni_660x.c`, and the `drivers/comedi/drivers/tests/ni_routes_test.c` unit tests.

The RTSI integration is explicit: `ni_route_to_register()` may return an indirect register value for routes that traverse `NI_RGOUT0` or may return `BIT(6)` to mark a route requiring the RTSI board mux. `ni_rtsi_route_requires_mux()` lets downstream code identify that special return value before programming the RTSI subdevice.

## Risks and Test Signals

The main risks are contract drift between generated valid-route arrays and generated register-value matrices, invalid direct-register compatibility offsets, and misuse of helper return ranges. `ni_route_to_register()` returns `-1` on invalid device routes, while `ni_lookup_route_register()` and `ni_find_route_source()` return `-EINVAL`; callers must preserve those expectations. The sort/search helpers require every generated list to be terminated with `.dest = 0` and every source list to end with `0`.

Useful tests are the existing `ni_routes_test.c` coverage for assignment, route-set lookup, route-to-register conversion, register-to-source lookup, valid-route enumeration, and trigger-argument validation. Hardware-facing smoke tests should exercise AI/AO sample-clock and start-trigger routing, counter gates/sources, PFI export, and RTSI indirect routing on E-series, M-series, and 660x devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/all.h -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/all.h

## Purpose

`ni_device_routes/all.h` is the generated extern catalog for all generated per-board NI valid-route tables. It centralizes declarations so `ni_device_routes.c` can build the global lookup list without each board file needing a bespoke header.

## Important APIs, Types, and Functions

The file declares `extern struct ni_device_routes` symbols for E-series, M-series, 653x, 6602, 6713/6723/6733, PXI, and PXIe route tables. Examples include `ni_pxi_6030e_device_routes`, `ni_pci_6070e_device_routes`, `ni_pci_6220_device_routes`, `ni_pci_6259_device_routes`, `ni_pci_6534_device_routes`, `ni_pxie_6535_device_routes`, and `ni_pxie_6738_device_routes`.

It defines no functions. The declarations rely on `../ni_device_routes.h`, which in turn includes the core route type definitions from `ni_routes.h`.

## Control Flow, State, and Persistence

The header has no runtime control flow or storage. It is generated metadata used at compile time to tie per-board C translation units to the central route-list translation unit.

## Dependencies and Integration Points

`ni_device_routes.c` includes this file to reference board symbols. Each generated board `.c` file also includes `all.h`, which gives the compiler visibility into sibling table symbols if generator output ever needs them. The generator in `ni_routing/tools/convert_csv_to_c.py` is the likely source of this extern list and should be used to maintain it.

## Risks and Test Signals

The main integration risk is mismatch between this extern catalog, `ni_device_routes.c`, and the Makefile. In this snapshot the catalog declares `ni_pxie_6535_device_routes` and `ni_pxie_6738_device_routes`; the Makefile builds those objects; but the central `ni_device_routes_list[]` omits them. A consistency test should assert that every generated table intended for assignment appears in the central registry or is documented as reachable by an alternate board name.

Build success catches missing object definitions for externs only when they are actually referenced. Runtime assignment tests are still required to catch externs that compile but are not in the lookup list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/all.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6070e.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6070e.c

## Purpose

`pci-6070e.c` is the generated valid-route table for the NI PCI-6070E E-series board. It constrains which abstract NI signals may be routed to PFI pins, RTSI trigger lines, counter terminals, AI/AO timing terminals, and the master timebase before the generic route-value matrix is used to compute hardware register selectors.

## Important APIs, Types, and Functions

The file defines `struct ni_device_routes ni_pci_6070e_device_routes` with `.device = "pci-6070e"` and a compound-literal `.routes` array of `struct ni_route_set`. It includes 37 real destinations plus the terminating `.dest = 0` element. Source lists are `int[]` compound literals ending in `0`.

Route coverage includes `NI_PFI(0)` through `NI_PFI(9)`, `TRIGGER_LINE(0)` through `TRIGGER_LINE(7)`, counter sources/gates/outs for counters 0 and 1, AI sample/start/reference/convert/pause/hold-complete terminals, AO sample/start/pause terminals, and `NI_MasterTimebase`. The table references E-series signals such as `NI_20MHzTimebase`, `NI_100kHzTimebase`, `NI_AI_HoldCompleteEvent`, and `NI_AnalogComparisonEvent`.

## Control Flow, State, and Persistence

The file has no executable control flow. At module initialization, `ni_sort_device_routes()` counts and sorts this route table in place. At attach time, `ni_find_valid_routes()` selects it when the board name is `pci-6070e`; later `ni_route_to_register()` first verifies that a requested source appears in this table's destination source list before looking up the E-series route value.

Runtime state is the sorted/counted generated array. There is no persistent state beyond the compiled table.

## Dependencies and Integration Points

It depends on `../ni_device_routes.h` for route structures and `all.h` for generated extern declarations. It integrates with the E-series `ni_route_values` family selected by `ni_assign_device_routes("ni_eseries", "pci-6070e", ...)`. `ni_routes_test.c` explicitly uses the PCI-6070E assignment path as a representative E-series test.

## Risks and Test Signals

Because this is generated static data, the key risks are stale CSV/tool output, missing terminators, route-value mismatches, and accidentally broadening routes that hardware cannot realize. The low PFI count and E-series-only timing signals distinguish it from M-series tables; copying M-series routes here would be suspicious.

Test signals include successful `ni_assign_device_routes()` for `pci-6070e`, valid route-to-register conversion for AI/AO triggers and counter terminals, valid enumeration through `INSN_DEVICE_CONFIG_GET_ROUTES`, and hardware tests exporting/importing PFI and RTSI signals without invalid register selectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6070e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6220.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6220.c

## Purpose

`pci-6220.c` is the generated valid-route table for the NI PCI-6220 M-series board. It describes routing for a 16-PFI, AI/counter/DIO-capable board without analog-output timing destinations.

## Important APIs, Types, and Functions

The file defines `struct ni_device_routes ni_pci_6220_device_routes` with `.device = "pci-6220"`. It has 47 real route-set destinations plus a `.dest = 0` terminator and approximately 1,972 listed source entries before runtime sorting/counting.

Destinations cover `NI_PFI(0)` through `NI_PFI(15)`, all eight `TRIGGER_LINE()` RTSI lines, counter source/gate/aux/A/B/Z/arm-start terminals for counters 0 and 1, AI sample/start/reference/convert/pause timing terminals, and `NI_DI_SampleClock`/`NI_DO_SampleClock`. Source lists include M-series timing names such as `NI_80MHzTimebase`, `NI_10MHzRefClock`, `NI_FrequencyOutput`, and `NI_ChangeDetectionEvent`.

## Control Flow, State, and Persistence

This file is pure generated data. The generic NI routing module sorts the destination and source arrays during initialization, then the board attach path selects the table by exact device string. Route validation uses the table as a first-stage device capability filter before consulting M-series register values.

No state is persisted. The only mutation is the module-init in-place sort and count of generated compound-literal arrays.

## Dependencies and Integration Points

It includes the generated route headers and integrates with the `ni_mseries` route-value table. PCI-6220 is also used in `ni_routes_test.c` to verify assignment to a different route-value table than PCI-6070E. It is listed in `ni_device_routes_list[]`, so normal board-name lookup can find it.

## Risks and Test Signals

The main functional risk is confusing the PCI-6220 with AO-capable 6221/6229 variants. This table intentionally lacks `NI_AO_SampleClock`, `NI_AO_StartTrigger`, `NI_AO_PauseTrigger`, and `NI_AO_SampleClockTimebase` destinations; adding those would expose invalid AO command routes. Test by comparing route enumeration against expected no-AO hardware capability, running unit route assignment/conversion tests, and exercising AI, DI/DO sample clocks, counter source/gate/aux routes, and RTSI/PFI routing on real hardware or table-driven tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6220.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6221.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6221.c

## Purpose

`pci-6221.c` is the generated valid-route table for the NI PCI-6221 M-series board. It extends the PCI-6220-style AI/counter/DIO routing surface with analog-output timing routes.

## Important APIs, Types, and Functions

The file defines `struct ni_device_routes ni_pci_6221_device_routes` with `.device = "pci-6221"`. It contains 51 real destinations plus the terminator and approximately 2,230 source entries. It is structurally identical to `pci-6229.c` except for the C symbol, `.device` string, and comment path.

Destinations include the full `NI_PFI(0..15)` range, `TRIGGER_LINE(0..7)`, two-counter source/gate/aux/A/B/Z/arm-start terminals, AI timing terminals, AO sample/start/pause/sample-clock-timebase terminals, and DI/DO sample clocks. Source lists include `NI_AO_SampleClock` and `NI_AO_StartTrigger` where a non-AO board would not.

## Control Flow, State, and Persistence

The table is sorted and counted by `ni_sort_device_routes()` at module initialization. Lookup is by exact `pci-6221` device string through `ni_device_routes_list[]`. Later route checks use this table to reject invalid source/destination pairs before `ni_route_to_register()` consults M-series register values and handles possible RTSI indirect muxing.

Runtime state is limited to in-memory sorted generated arrays; no route state is persisted.

## Dependencies and Integration Points

It depends on the shared route headers and the M-series route-value matrix. It is listed in `ni_device_routes.c`, so `ni_mio_common.c` can bind it when board metadata reports `pci-6221`. It integrates with command argument validation for AI/AO/DI/DO clocks and triggers through `ni_get_reg_value()` and `ni_check_trigger_arg()`.

## Risks and Test Signals

The main risk is copy-family drift: PCI-6221 and PCI-6229 are currently identical tables, while PCI-6251/6259 add analog-comparison routing. Changes should be generated from the routing CSV/tools rather than patched by hand. Test signals are successful board assignment, route enumeration that includes AO timing destinations, route-to-register tests for AO sample/start/pause paths, and no exposure of 625x-only `NI_AnalogComparisonEvent` routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6221.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6229.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6229.c

## Purpose

`pci-6229.c` is the generated valid-route table for the NI PCI-6229 M-series board. It provides the same routing surface as the PCI-6221 table for PFI, RTSI, AI, AO, counter, DI, and DO timing signals.

## Important APIs, Types, and Functions

The file defines `struct ni_device_routes ni_pci_6229_device_routes` with `.device = "pci-6229"`. It has 51 real destinations plus a terminator and approximately 2,230 listed source entries. A diff against `pci-6221.c` shows only file-comment, symbol-name, and device-string differences.

Destination groups are `NI_PFI(0..15)`, `TRIGGER_LINE(0..7)`, two-counter source/gate/aux/A/B/Z/arm-start terminals, AI sample/start/reference/convert/pause timing terminals, AO sample/start/pause/sample-clock-timebase terminals, and DI/DO sample clocks.

## Control Flow, State, and Persistence

There is no file-local executable flow. The generic NI routing module mutates the table once during initialization to compute counts and sort arrays. Board attach selects the table by `pci-6229`, then runtime route validation and register-value lookup proceed through the generic helpers in `ni_routes.c`.

The generated table does not persist state. Any active route programming lives in hardware registers managed by the consuming driver, not in this file.

## Dependencies and Integration Points

It depends on `../ni_device_routes.h`, `all.h`, the M-series route-value table, and inclusion in `ni_device_routes_list[]`. It integrates with `ni_mio_common.c` command/config paths for AI/AO/DIO/counter routing and with user-visible route enumeration via `ni_get_valid_routes()`.

## Risks and Test Signals

The main risks are unintended divergence from `pci-6221.c` and mistaken import of 625x-only analog-comparison sources. Generated-route consistency checks should flag unexpected differences. Test signals include `ni_assign_device_routes("ni_mseries", "pci-6229", ...)`, AO/AI/counter route-to-register validation, and route enumeration matching the 6221-equivalent capability model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6229.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6251.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6251.c

## Purpose

`pci-6251.c` is the generated valid-route table for the NI PCI-6251 M-series board. It is an AO-capable M-series table like PCI-6221/6229, with additional analog-comparison-event routing available on the 625x class.

## Important APIs, Types, and Functions

The file defines `struct ni_device_routes ni_pci_6251_device_routes` with `.device = "pci-6251"`. It has 51 real route-set destinations plus a terminator and approximately 2,280 source entries. It is identical to `pci-6259.c` except for symbol/device/file naming.

The route surface includes `NI_PFI(0..15)`, `TRIGGER_LINE(0..7)`, counter source/gate/aux/A/B/Z/arm-start terminals for two counters, AI timing terminals, AO timing terminals, and DI/DO sample clocks. Compared with PCI-6221/6229, many source lists also include `NI_AnalogComparisonEvent`.

## Control Flow, State, and Persistence

The generated route table is counted and sorted once at module initialization. Device attach selects it through the central `ni_device_routes_list[]`, and all later flow is handled by `ni_route_to_register()`, `ni_get_reg_value()`, and related helpers. Indirect RTSI behavior is still resolved by generic route-value lookup, not by special code in this table.

No state is persisted. The only mutation is in-memory sorting/count initialization.

## Dependencies and Integration Points

It depends on generated route headers and the M-series route-value matrix. It is consumed by NI MIO board setup for `pci-6251` and by user-facing device-config route enumeration. Its table must remain consistent with generated route-value entries for analog comparison, AO timing, DI/DO timing, counters, and PFI/RTSI cross-routing.

## Risks and Test Signals

The primary risks are losing `NI_AnalogComparisonEvent` on destinations where 625x hardware supports it, or accidentally spreading that source to lower 622x tables. Test signals include assignment success for `pci-6251`, table comparison against `pci-6259.c`, route-to-register coverage for analog-comparison routes, AO timing route checks, and hardware validation of AI trigger/pause paths using analog comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6251.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6254.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6254.c

## Purpose

`pci-6254.c` is the generated valid-route table for the NI PCI-6254 M-series board. It follows the no-AO-destination shape of PCI-6220 while adding 625x analog-comparison-event routing.

## Important APIs, Types, and Functions

The file defines `struct ni_device_routes ni_pci_6254_device_routes` with `.device = "pci-6254"`. It contains 47 real destinations plus a terminator and approximately 2,018 source entries. Its destination set matches PCI-6220: 16 PFI pins, 8 RTSI trigger lines, two-counter terminals, AI timing terminals, and DI/DO sample clocks, without AO timing destinations.

Compared with PCI-6220, many source lists include `NI_AnalogComparisonEvent`, making it the 625x counterpart to a no-AO table.

## Control Flow, State, and Persistence

This is static generated data. `ni_sort_device_routes()` initializes counts and sort order; `ni_find_valid_routes()` selects it by `pci-6254`; `ni_route_to_register()` validates source membership and consults M-series register values for the actual selector. No persistent state is held in the table.

## Dependencies and Integration Points

The file depends on `../ni_device_routes.h` and `all.h`, is included in `ni_device_routes_list[]`, and uses the M-series route-value matrix. It integrates with AI/counter/DIO command validation while intentionally omitting AO command destinations.

## Risks and Test Signals

The main risk is capability confusion in either direction: adding AO destinations would expose unsupported routes, while removing `NI_AnalogComparisonEvent` would under-report 625x routing. Test by comparing against PCI-6220 for analog-comparison deltas, comparing against PCI-6251/6259 for intentionally absent AO destinations, checking `ni_assign_device_routes()` success, and validating AI/counter/DIO routes with analog-comparison sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6254.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6259.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6259.c

## Purpose

`pci-6259.c` is the generated valid-route table for the NI PCI-6259 M-series board. It represents the AO-capable 625x routing surface, including analog-comparison-event sources.

## Important APIs, Types, and Functions

The file defines `struct ni_device_routes ni_pci_6259_device_routes` with `.device = "pci-6259"`. It has 51 real destinations plus a terminator and approximately 2,280 source entries. It is identical to `pci-6251.c` apart from naming.

Routes cover `NI_PFI(0..15)`, `TRIGGER_LINE(0..7)`, two-counter source/gate/aux/A/B/Z/arm-start terminals, AI timing terminals, AO sample/start/pause/sample-clock-timebase terminals, DI/DO sample clocks, M-series timebases, `NI_FrequencyOutput`, `NI_ChangeDetectionEvent`, and `NI_AnalogComparisonEvent`.

## Control Flow, State, and Persistence

The table is counted and sorted by generic module initialization, then selected by exact board-name lookup. Runtime consumers never execute code in this file; they pass requested source/destination pairs to `ni_route_to_register()` and related helpers, which use this data as the board-validity filter before computing register selectors.

No persistent state exists in this file. Hardware route programming is performed elsewhere after validation.

## Dependencies and Integration Points

It depends on generated route headers and the M-series route-value table. It is registered in `ni_device_routes.c`, used by NI MIO attach for PCI-6259 boards, and exposed indirectly through Comedi route enumeration and trigger argument validation.

## Risks and Test Signals

Risk centers on generated-data drift from `pci-6251.c`, lost analog-comparison coverage, or accidental mismatch with M-series route-value entries. Tests should include assignment by `pci-6259`, equality checks against `pci-6251.c` aside from naming, route-to-register validation for analog comparison and AO timing, and hardware exercise of AI/AO/counter/DIO routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6259.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6534.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6534.c

## Purpose

`pci-6534.c` is the generated valid-route table for the NI PCI-6534 digital I/O board. Its route surface is much smaller than the MIO boards: it mainly permits PFI-to-RTSI and RTSI-to-PFI routing plus a master timebase route.

## Important APIs, Types, and Functions

The file defines `struct ni_device_routes ni_pci_6534_device_routes` with `.device = "pci-6534"`. It contains 17 real destinations plus the terminator and approximately 298 listed source entries.

Destinations cover `NI_PFI(0)` through `NI_PFI(7)`, `TRIGGER_LINE(0)` through `TRIGGER_LINE(7)`, and `NI_MasterTimebase`. PFI destinations accept RTSI trigger lines; RTSI destinations accept PFIs and peer RTSI lines; `TRIGGER_LINE(7)` can source `NI_20MHzTimebase`; `NI_MasterTimebase` can source `TRIGGER_LINE(7)` or `NI_20MHzTimebase`.

## Control Flow, State, and Persistence

The file is static generated data. During route module initialization, its destination/source arrays are counted and sorted. Board setup finds it through `ni_device_routes_list[]`, and route validation uses it before family route-value lookup. It does not store active route state or persist anything.

## Dependencies and Integration Points

It includes `../ni_device_routes.h` and `all.h`. It is listed in the central device-route registry and built with the NI route support. Its likely integration points are digital I/O timing and RTSI/PFI signal export/import for PCI-6534 rather than the AI/AO/counter-rich MIO command paths.

## Risks and Test Signals

The main risk is over-generalizing from M-series tables. This file intentionally lacks AI, AO, DI/DO sample-clock, frequency-output, change-detection, and counter terminal destinations. Test signals include successful assignment for `pci-6534`, valid route enumeration limited to PFI/RTSI/timebase paths, route-to-register coverage for PFI/RTSI cross-routing, and hardware validation that timebase and RTSI lines behave without exposing unsupported MIO routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6534.c -->
