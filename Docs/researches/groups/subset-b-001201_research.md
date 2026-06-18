<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6602.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6602.c

Purpose: this generated Comedi NI routing table exports `ni_pci_6602_device_routes` for board name `pci-6602`. It is not an executable driver; it is board-specific validity data for the NI routing core. The table describes which named internal or external signals may be routed to each destination on the PCI-6602 counter/timer board.

Important APIs, types, and data: the file includes `../ni_device_routes.h` and `all.h`, then defines one global `struct ni_device_routes` with `.device = "pci-6602"` and an inline `struct ni_route_set[]`. Each route set has a `.dest` signal and a sentinel-terminated `.src` array of legal sources. The observed source data contains 79 destination route sets before the `{ .dest = 0 }` terminator. Destination coverage is counter-heavy: PFI destinations 2, 3, 4, 6 through 39; RTSI `TRIGGER_LINE(0..7)`; `NI_CtrSource(0..7)`, `NI_CtrGate(0..7)`, `NI_CtrAux(0..7)`, `NI_CtrArmStartTrigger(0..7)`, and `NI_MasterTimebase`.

Control flow: there is no local branching or callable function. Runtime behavior is supplied by `ni_routes.c`: `ni_sort_all_device_routes()` walks `ni_device_routes_list`, calls `ni_sort_device_routes()`, counts route sets until `.dest == 0`, counts each source list until source `0`, and sorts the arrays in place. Later, `ni_find_route_set()` binary-searches by destination, `ni_route_set_has_source()` searches sources, and `ni_route_to_register()` combines this validity table with family route-value tables.

State and persistence: the route set and source arrays live in global storage through compound literals referenced by non-const pointers. They are mutated during initialization to fill `n_route_sets` and each `n_src`, and to sort route and source arrays. After init, the data acts as persistent in-kernel lookup state for the loaded module; there is no disk persistence, allocation, locking, or teardown path in this file.

Dependencies and integration points: the symbol is declared in `ni_device_routes/all.h` and is registered in `ni_device_routes.c` through `ni_device_routes_list`. Board matching in `ni_assign_device_routes()` depends on the `.device` string matching probe-time board names or alternate board names. Register encodings are not stored here; they come from the family-specific `route_values` table selected for the device family.

Risks: the generated nature means manual edits are fragile. A missing final `{ .dest = 0 }` or source `0` sentinel would make `ni_sort_device_routes()` walk past the arrays. Incorrect signal names can pass C compilation but produce invalid route exposure if the names remain within `NI_NAMES_BASE` range. Since sources include many PFI, RTSI, counter internal-output, logic-low, and logic-high combinations, mismatches against the actual 6602 hardware or route-value matrix would surface as routes reported but not convertible to registers.

Test signals: useful checks are compile coverage, route assignment for board `pci-6602`, `ni_count_valid_routes()` returning nonzero after module init, and `ni_get_valid_routes()` containing representative routes such as timebase-to-PFI outputs, counter source/gate/aux mappings, RTSI paths, and `NI_MasterTimebase` from `TRIGGER_LINE(7)` or `NI_20MHzTimebase`. Negative tests should verify unsupported destinations such as missing low PFI pins are rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6602.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6713.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6713.c

Purpose: this generated table exports `ni_pci_6713_device_routes` for the `pci-6713` analog-output board. It defines the valid signal routing graph for the PCI variant so the common NI routing code can answer route-validity and user route-enumeration requests.

Important APIs, types, and data: the single exported object is a `struct ni_device_routes` with `.device = "pci-6713"`. It contains 26 route sets. Destination families are compact: PFI 3, 4, 5, 6, 8, and 9; RTSI `TRIGGER_LINE(0..7)`; `NI_CtrSource(0..1)`, `NI_CtrGate(0..1)`, `NI_CtrOut(0..1)`, AO destinations `NI_AO_SampleClock`, `NI_AO_StartTrigger`, `NI_AO_PauseTrigger`, `NI_AO_SampleClockTimebase`, and `NI_MasterTimebase`. The PFI rows expose fixed associations such as counter source/gate and AO sample/start signals on selected pins.

Control flow: local control flow is declarative only. At runtime, the common routing core fills the omitted `n_route_sets` and `n_src` fields by scanning the terminators, sorts the route sets, and performs binary-search lookup by destination. The actual route must be present both in this validity table and in the selected family route-value table for `ni_route_to_register()` to return a usable register value.

State and persistence: the arrays are static lifetime C objects reachable from the exported global. Initialization mutates the arrays for sorting and count caching; no other persistent state is maintained here. All route information is regenerated by loading the module from the compiled table and is not backed by external configuration.

Dependencies and integration points: this source depends on `ni_device_routes.h` for `struct ni_device_routes` and `struct ni_route_set`, plus `all.h` for cross-file declarations. `ni_device_routes.c` includes `&ni_pci_6713_device_routes` in `ni_device_routes_list`, which makes it discoverable by `ni_assign_device_routes()`. It also depends on the shared NI signal namespace from `<linux/comedi.h>`.

Risks: because the 6713 table is small and AO-focused, omissions are easy to overlook, especially for RTSI and counter interactions. A wrong `.device` string would make route assignment fail even though the object links. Missing source terminators or destination terminator would corrupt initialization scans. The data uses `0` as sentinel, so valid sources must never be encoded as zero.

Test signals: verify `pci-6713` lookup succeeds, `ni_get_valid_routes()` returns representative AO sample/start/pause routes, and unsupported AI or digital sample-clock destinations remain absent. Tests should include external PFI-to-counter source/gate routes, AO trigger routing through RTSI lines, and route-to-register conversion against the board family route-value matrix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6713.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6723.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6723.c

Purpose: this file provides the generated valid-route table for the `pci-6723` board as `ni_pci_6723_device_routes`. It lets the shared Comedi NI routing implementation distinguish what the PCI-6723 hardware can route from what the broader family register tables know how to encode.

Important APIs, types, and data: the exported `struct ni_device_routes` has `.device = "pci-6723"` and 26 route sets. Its destination coverage matches the AO/counter shape of nearby 67xx boards: PFI 3, 4, 5, 6, 8, and 9; RTSI `TRIGGER_LINE(0..7)`; `NI_CtrSource(0..1)`, `NI_CtrGate(0..1)`, `NI_CtrOut(0..1)`, AO sample/start/pause/sample-clock-timebase destinations, and `NI_MasterTimebase`. Source lists are sentinel-terminated `int[]` compound literals.

Control flow: the file has no functions. The route data is consumed after `ni_sort_device_routes()` computes counts and sorts it. Query flow is: board name selects this object, destination lookup finds a route set, source lookup checks membership, then route-value lookup validates and translates the source/destination pair. RTSI destinations may receive indirect handling in `ni_count_valid_routes()` and `ni_route_to_register()`.

State and persistence: all state is compiled-in and process-global within the kernel module. Count fields start zero because they are not explicitly initialized, then are populated during route sorting. The source arrays are also sorted in place. No hardware registers are touched by this file; it only persists valid topology metadata while the module is loaded.

Dependencies and integration points: integration is via `ni_device_routes/all.h` and the central `ni_device_routes_list` entry in `ni_device_routes.c`. Signal constants come through `ni_routes.h` and `<linux/comedi.h>`. Correct operation also needs matching family route values; this file says a route is allowed, not which register value realizes it.

Risks: the PCI-6723 table is similar to PCI-6713, so copy-generation mistakes could silently expose the wrong AO or counter capabilities. The table relies on sentinels for both dimensions and on post-generation sorting before binary search. If a route is listed here but missing from route-values, it can appear in raw source data but be filtered out by `ni_get_valid_routes()` or rejected by `ni_route_to_register()`.

Test signals: verify assignment for board name `pci-6723`, nonzero route counts after init, valid AO sample clock/start/pause routes from PFI and RTSI sources, counter source/gate routes for both counters, and rejection of destinations outside the 6723 table. Tests comparing 6713 and 6723 should explicitly confirm intentional sameness rather than assuming it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6723.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6733.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6733.c

Purpose: this generated source exports `ni_pci_6733_device_routes`, the PCI-6733 board-specific valid-route table. It focuses on AO, counter, and selected digital timing routes for the PCI bus variant.

Important APIs, types, and data: the object is a `struct ni_device_routes` with `.device = "pci-6733"` and 28 route sets. Destination groups include PFI 3, 4, 5, 6, 8, and 9; RTSI lines 0 through 7; two counter source and gate destinations; `NI_CtrOut(0..1)`; AO sample/start/pause/sample-clock-timebase; digital sample-clock destinations `NI_DI_SampleClock` and `NI_DO_SampleClock`; and `NI_MasterTimebase`. The extra digital sample clock destinations distinguish it from the smaller 6713/6723-style AO-only tables.

Control flow: this source contributes only static route data. Common initialization counts route sets until the destination terminator and sources until each source terminator, then sorts them for binary search. Runtime route validation requires source membership in this table and a nonzero register mapping in the route-value table, with special mux handling for RTSI destinations.

State and persistence: the table is compiled into the module and persists while loaded. The common sorting step mutates `n_route_sets`, `n_src`, and element order. There is no per-device instance state, dynamic allocation, persistence outside memory, or direct register programming in this file.

Dependencies and integration points: the symbol is declared in `all.h` and registered in `ni_device_routes.c`. It is selected by `ni_assign_device_routes()` when the board name or alternate board name is `pci-6733`. It relies on NI signal constants from the Comedi namespace and on family-specific route-value data for register translation.

Risks: adding DI/DO sample-clock route sets increases the chance of mismatches with family route-value tables. If `NI_DI_SampleClock` or `NI_DO_SampleClock` sources are overbroad, users may see routes that hardware cannot realize. As with all generated route files, sentinel integrity is critical, and hand edits should be replaced by updates to the generator inputs.

Test signals: test board assignment for `pci-6733`, route enumeration including AO and DI/DO sample-clock destinations, route-to-register conversion for representative PFI and RTSI sources, and negative checks for unsupported AI destinations. Compare PCI-6733 against PXI-6733 where PXI-specific signals such as `PXI_Star` should differ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pci-6733.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxi-6030e.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxi-6030e.c

Purpose: this generated file exports `ni_pxi_6030e_device_routes`, the valid-route table for the PXI-6030E E-series board. It captures analog-input, analog-output, counter, RTSI, and PXI timing route availability for common Comedi route validation.

Important APIs, types, and data: the `struct ni_device_routes` uses `.device = "pxi-6030e"` and contains 37 route sets. Destination coverage includes PFI 0 through 9, RTSI trigger lines 0 through 5 and 7, `NI_CtrSource(0..1)`, `NI_CtrGate(0..1)`, `NI_CtrOut(0..1)`, AI sample/start/reference/convert/pause/sample-clock-timebase/convert-clock-timebase/hold-complete destinations, AO sample/start/pause/sample-clock-timebase, and `NI_MasterTimebase`.

Control flow: there is no local executable logic. The common route infrastructure registers and initializes this table, then later serves user and driver route queries from it. Lookup follows sorted destination and source arrays, while valid route enumeration filters the listed pairs through route-value availability.

State and persistence: route data is static lifetime global state. The shared init code computes count fields and sorts arrays in place; after that the data is stable lookup state. The file does not maintain hardware state, persistent configuration, locks, reference counts, or memory ownership beyond the compiled compound literals.

Dependencies and integration points: the table is included in `ni_device_routes_list`, making `pxi-6030e` discoverable through `ni_assign_device_routes()`. It depends on the shared `struct ni_device_routes` contract and on family route values for E-series boards. PXI-specific integration appears through route sources/destinations such as backplane trigger lines and master timebase selection.

Risks: E-series routing has many analog timing destinations, so wrong source lists can affect command-trigger setup rather than only explicit route configuration. `TRIGGER_LINE(6)` is not a destination in the observed coverage, which should be intentional and tested. Missing or extra PXI timing routes could break synchronization between modules in a chassis.

Test signals: verify `pxi-6030e` route assignment, AI and AO command timing routes from PFI and RTSI sources, counter source/gate route validation, master timebase alternatives, and the absence of unsupported trigger-line destinations. Integration tests should exercise `INSN_DEVICE_CONFIG_GET_ROUTES` count/query behavior after sorting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxi-6030e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxi-6224.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxi-6224.c

Purpose: this file exports `ni_pxi_6224_device_routes`, the generated M-series valid-route table for a PXI-6224 device. It defines which PFI, RTSI, AI timing, DI/DO sample-clock, and counter/quadrature signals are legal route endpoints for this board.

Important APIs, types, and data: the global `struct ni_device_routes` has `.device = "pxi-6224"` and 48 route sets. Destination coverage includes PFI 0 through 15, RTSI 0 through 7, `NI_CtrSource(0..1)`, `NI_CtrGate(0..1)`, `NI_CtrAux(0..1)`, `NI_CtrA/B/Z(0..1)`, `NI_CtrArmStartTrigger(0..1)`, AI sample/start/reference/convert/pause/sample-clock-timebase/convert-clock-timebase, plus `NI_DI_SampleClock` and `NI_DO_SampleClock`. Source lists include PFI pins, RTSI lines, counter internal outputs, AI timing signals, frequency output, change detection, analog comparison, and case/logic signals where supported.

Control flow: the table is initialized by the shared sorting pass, then queried through `ni_find_route_set()`, `ni_route_set_has_source()`, `ni_route_to_register()`, `ni_count_valid_routes()`, and `ni_get_valid_routes()`. The table gates what the board exposes; route-value tables gate what can be programmed.

State and persistence: static arrays are mutable during initialization for count and sort fields, then serve as persistent module-global lookup state. No per-board runtime data, allocation, or disk persistence is introduced. Because the arrays are not const, accidental runtime mutation outside the sort path would affect all users of this board table.

Dependencies and integration points: the symbol is declared in `all.h` and included in `ni_device_routes_list`. It depends on M-series route-value data and on the common NI signal namespace. Counter A/B/Z destinations are integration points for encoder-like counter routing, while DI/DO sample clocks integrate with digital subdevice command support.

Risks: the broader M-series matrix increases risk of routes listed without matching register encodings or vice versa. Counter quadrature destinations (`NI_CtrA/B/Z`) and arm-start triggers must remain aligned with hardware counter count. PXI backplane and RTSI behavior should be checked carefully because `ni_route_to_register()` can treat RTSI destinations indirectly.

Test signals: verify route assignment for `pxi-6224`, route enumeration for all 16 PFIs and 8 RTSI lines, AI timing sources, DI/DO sample clock routes, and counter source/gate/aux/A/B/Z routes for both counters. Negative tests should cover unsupported AO destinations because this table lacks AO timing endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxi-6224.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxi-6225.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxi-6225.c

Purpose: this generated source exports `ni_pxi_6225_device_routes`, the board-specific valid-route table for PXI-6225. It extends the PXI M-series routing shape with both analog-input and analog-output timing endpoints, digital sample clocks, and two-counter routing.

Important APIs, types, and data: the table is a `struct ni_device_routes` named for `.device = "pxi-6225"` and contains 52 route sets. Destinations cover PFI 0 through 15, RTSI 0 through 7, `NI_CtrSource/Gate/Aux/A/B/Z(0..1)`, `NI_CtrArmStartTrigger(0..1)`, AI sample/start/reference/convert/pause/sample-clock-timebase/convert-clock-timebase, AO sample/start/pause/sample-clock-timebase, and `NI_DI_SampleClock`/`NI_DO_SampleClock`.

Control flow: all behavior comes from the common routing core. The route array is sentinel-scanned and sorted at module init, then used as the first validity filter for route queries. User-visible route enumeration further filters each source/destination pair through route-value lookups, so rows here must correspond to programmable mux values.

State and persistence: static global data persists for the lifetime of the module. Initialization fills count fields and sorts route and source arrays in place. The table stores topology only; it does not persist user choices or configure registers by itself.

Dependencies and integration points: `all.h` declares the symbol, `ni_device_routes.c` registers it, `ni_routes.h` defines the structs, and family route-value tables provide register encodings. This file integrates with AI, AO, digital, and counter subdevices by defining which trigger and clock sources those subdevices may legally select.

Risks: because this file has both AI and AO endpoints, cross-subdevice route mistakes can affect command scheduling. Similarity to PXI-6251 and PXIE-6251 increases copy/paste or generator-template risk. The source arrays must remain terminated by `0`, and `n_src` must not be assumed valid before the sorting init step.

Test signals: test `pxi-6225` assignment, route count/enumeration after init, representative AI and AO timing routes from PFI/RTSI/counter sources, DI/DO sample clock routes, and counter quadrature routes. Compare expected deltas against `pxi-6224`, especially the presence of AO destinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxi-6225.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxi-6251.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxi-6251.c

Purpose: this file exports `ni_pxi_6251_device_routes`, the generated routing validity table for the PXI-6251 M-series board. It defines valid analog, digital, counter, PFI, and RTSI source/destination pairs for the shared NI routing layer.

Important APIs, types, and data: the single global object has `.device = "pxi-6251"` and 52 route sets. Destination groups include PFI 0 through 15, RTSI 0 through 7, counter source/gate/aux/A/B/Z for counters 0 and 1, arm-start triggers for both counters, AI sample/start/reference/convert/pause and AI timebase routes, AO sample/start/pause/sample-clock-timebase, and DI/DO sample-clock destinations.

Control flow: common route initialization scans the table terminators, computes `n_route_sets` and `n_src`, and sorts the arrays. Runtime validation binary-searches destinations and sources before consulting route-value tables. The file’s data therefore controls board-specific allowance, while `ni_route_values` controls register encodability.

State and persistence: compiled static arrays are shared module-global state. They are intentionally mutable during init for sorting and count caching. There is no dynamic state per device instance, and no persistence beyond the loaded module image.

Dependencies and integration points: `ni_pxi_6251_device_routes` is declared in `all.h` and listed in `ni_device_routes_list`. Integration reaches Comedi command paths indirectly through route validation for AI/AO/DI/DO clocks and triggers, and reaches counter support through source/gate/aux/quadrature and arm-start destinations.

Risks: the PXI-6251 table is broad enough that a single stale generated row can expose invalid user routes or hide valid hardware routes. RTSI and PXI backplane routes need matching route-value support. Because the arrays are sorted in place, assumptions about source order in generated text should not be relied on at runtime.

Test signals: verify lookup for `pxi-6251`, route enumeration containing all expected PFI and RTSI destinations, valid AI/AO/DI/DO timing route conversion, counter route conversion for both counters, and rejection of unsupported board-specific routes. Tests should include indirect RTSI mux behavior where route values require it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxi-6251.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxi-6733.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxi-6733.c

Purpose: this generated table exports `ni_pxi_6733_device_routes` for the PXI-6733 analog-output board. It is the PXI counterpart to the PCI-6733 route table, adding PXI-specific synchronization where supported.

Important APIs, types, and data: the `struct ni_device_routes` has `.device = "pxi-6733"` and 28 route sets. Destinations include PFI 3, 4, 5, 6, 8, and 9; RTSI trigger lines 0 through 5 and 7; `NI_CtrSource(0..1)`, `NI_CtrGate(0..1)`, `NI_CtrOut(0..1)`; AO sample/start/pause/sample-clock-timebase; DI/DO sample-clock destinations; `NI_MasterTimebase`; and PXI-specific `PXI_Star`.

Control flow: the file is declarative. Common module init counts and sorts the table, then route queries use destination and source binary searches. `PXI_Star` and RTSI destinations still require matching family route-value entries for conversion to register values.

State and persistence: data lives as module-global static storage and is mutated only by the shared sort/count initialization path. There is no per-device allocation, saved configuration, or direct hardware access.

Dependencies and integration points: the symbol is declared in `all.h` and registered in `ni_device_routes.c`. It integrates with PXI chassis timing through `PXI_Star` and trigger-line routes, with AO command timing through AO destinations, and with digital/counter subdevices through sample-clock and counter routes.

Risks: the PXI variant has a slightly different trigger-line set from PCI and exposes `PXI_Star`; mixing these tables would produce hard-to-diagnose chassis synchronization failures. Generated table order is not runtime order after sorting. Sentinel loss would affect init scans.

Test signals: verify `pxi-6733` assignment, PXI star routing behavior, AO sample/start/pause route conversion, DI/DO sample clock routes, and expected absence of `TRIGGER_LINE(6)` as a destination. Compare against PCI-6733 to confirm only intended PXI-specific differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxi-6733.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxie-6251.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxie-6251.c

Purpose: this generated source exports `ni_pxie_6251_device_routes`, the PXIe-6251 board-specific valid-route table. It mirrors much of the PXI-6251 M-series topology while using the PXIe board identity for route-table assignment.

Important APIs, types, and data: the object has `.device = "pxie-6251"` and 52 route sets. Destination coverage includes PFI 0 through 15, RTSI 0 through 7, `NI_CtrSource/Gate/Aux/A/B/Z(0..1)`, `NI_CtrArmStartTrigger(0..1)`, AI sample/start/reference/convert/pause/timebase destinations, AO sample/start/pause/sample-clock-timebase destinations, and DI/DO sample clocks.

Control flow: as with the other route tables, this file defines data only. Shared initialization counts and sorts route sets and source arrays. At runtime, board route assignment selects this object by device string, route validation checks this table first, and route-value lookup then maps valid pairs to hardware register values.

State and persistence: the route data is persistent in memory for the module lifetime. Count fields and sort order are initialized once by common code. There is no external persistence and no local locking or allocation.

Dependencies and integration points: the symbol is declared in `ni_device_routes/all.h` and listed in `ni_device_routes.c`. It integrates with the Comedi NI routing API exported from `ni_routes.c`, and with analog, digital, and counter subdevice command paths that ask whether a clock or trigger source is valid.

Risks: PXIe naming must match board descriptors exactly; otherwise this otherwise valid table is unreachable. Because it is very similar to PXI-6251, tests should catch accidental divergence or missed bus-specific differences. Any route listed here but lacking a family register value will be filtered or rejected later, so table and route-values generation must stay synchronized.

Test signals: verify assignment using `pxie-6251`, route enumeration parity with expected M-series routes, AI/AO/DI/DO timing route conversion, counter quadrature and arm-start routes, and negative tests for unsupported destinations. Include a check that `ni_device_routes_list` contains this symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxie-6251.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxie-6535.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxie-6535.c

Purpose: this generated file exports `ni_pxie_6535_device_routes`, a PXIe-6535 digital I/O route validity table. It focuses on PFI, RTSI, and digital input/output timing and handshake event routes rather than analog or counter routing.

Important APIs, types, and data: the table defines `.device = "pxie-6535"` with 22 route sets. Destinations cover PFI 0 through 5, RTSI `TRIGGER_LINE(0..7)`, `NI_DI_StartTrigger`, `NI_DI_ReferenceTrigger`, `NI_DI_SampleClock`, `NI_DI_PauseTrigger`, `NI_DO_StartTrigger`, `NI_DO_SampleClock`, and `NI_DO_PauseTrigger`. PFI sources include other PFI pins, RTSI lines, DI events such as input-buffer-full and ready-for-transfer variants, DO events such as output-buffer-full/data-active/ready-for-transfer, and change-detection events.

Control flow: this source is declarative static data. If reachable through the central route list, common initialization would count and sort route sets and sources, and runtime route APIs would validate digital timing routes from this object before consulting register values.

State and persistence: the route arrays have static lifetime and are designed to be sorted and counted in place. No user-selected routes, device registers, dynamic memory, or persistent files are managed here.

Dependencies and integration points: the symbol is declared in `ni_device_routes/all.h`, but in the inspected tree `ni_device_routes.c` does not include `&ni_pxie_6535_device_routes` in `ni_device_routes_list`. That means the table may compile and be externally declared yet not be discoverable through `ni_assign_device_routes()` unless another integration path exists outside the inspected list. It depends on the common NI routing structs and digital route-value support.

Risks: the apparent missing list registration is the primary integration risk: board route assignment for `pxie-6535` can fail even with a valid table. Digital event names are specialized, so stale generator input could expose impossible handshake/event routes. If later added to the list, sentinel and sort/count assumptions still apply.

Test signals: first verify whether `pxie-6535` route assignment succeeds; in the current inspected registration list it is expected not to. If registered, tests should enumerate PFI and RTSI digital routes, validate DI/DO sample/start/pause trigger conversion, and ensure analog/counter destinations are absent. A regression check should assert that `ni_device_routes_list` and `all.h` remain consistent for this symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/pxie-6535.c -->
