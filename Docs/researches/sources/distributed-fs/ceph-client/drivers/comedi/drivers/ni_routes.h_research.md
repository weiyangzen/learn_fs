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
