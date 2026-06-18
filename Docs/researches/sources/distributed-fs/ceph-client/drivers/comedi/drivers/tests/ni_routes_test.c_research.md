# sources/distributed-fs/ceph-client/drivers/comedi/drivers/tests/ni_routes_test.c

## Purpose
This file is a loadable kernel-module unit test suite for the COMEDI National Instruments routing helpers implemented by `ni_routes.c` and described by `ni_routes.h`/`ni_stc.h`. It verifies that board-specific route tables are selected, sorted, counted, searched, and translated into register values correctly, including indirect routes through mux-like intermediate destinations such as `NI_RGOUT0` and `NI_RTSI_BRD(n)`.

## Important APIs, Types, And Functions
The test builds fake board state with `struct ni_board_struct board`, `struct ni_private private`, a synthetic `struct ni_device_routes DR`, and a synthetic route-value matrix `RV[NI_NUM_NAMES][NI_NUM_NAMES]`. Helper macros `O()`, `B()`, `V()`, and `RVI()` convert between NI symbolic names, table offsets, and encoded valid register values. `route_set_dests_in_order()` and `route_set_sources_in_order()` assert sorted table invariants.

The individual tests cover `ni_assign_device_routes()`, `ni_sort_device_routes()`, `ni_find_route_set()`, `ni_route_set_has_source()`, `ni_route_to_register()`, `ni_lookup_route_register()`, `route_is_valid()`, `ni_is_cmd_dest()`, `channel_is_pfi()`, `channel_is_rtsi()`, `ni_count_valid_routes()`, `ni_get_valid_routes()`, `ni_find_route_source()`, `route_register_is_valid()`, `ni_check_trigger_arg[_roffs]()`, and `ni_get_reg_value[_roffs]()`. Module entry `ni_routes_unittest()` passes these functions to `exec_unittests()`.

## Control Flow
The suite initializes one of three test board contexts (`pci-6070e`, `pci-6220`, or `pci-fake`) before each logical test. Real board tests assert that E-series and M-series table selection finds expected route sets and register encodings. The fake board tests sort the synthetic route set once, then exercise route lookup, validity, direct register lookup, indirect route resolution, trigger argument validation, and valid-route enumeration. Test failure reporting is non-fatal: every `unittest()` call updates global counters and logs through the kernel logging API, so all tests run even after earlier failures.

## State And Persistence
The file mutates static fake board globals only inside module lifetime. `init_private()` clears `private`; `init_pci_*()` assigns board names and routing table pointers. `ni_sort_device_routes(&DR)` permanently orders the static synthetic route list for later tests in the same module load. No state persists after module unload except kernel log output.

## Dependencies And Integration Points
The test depends on COMEDI NI internals, not only public APIs: it includes `../ni_stc.h` and `../ni_routes.h` and directly instantiates `struct ni_private`. It integrates with the local minimal test framework in `unittest.h` and with Linux module init/exit macros. It is normally built only as part of the COMEDI driver tests.

## Risks And Edge Cases
The tests intentionally rely on hard-coded table sizes and route counts, so legitimate route-table updates can require test updates. Fake routes use names offset from `NI_NAMES_BASE`; an enum layout change could invalidate assumptions. The indirect-route cases are important because direct lookup intentionally rejects muxed paths while `ni_route_to_register()` resolves them. The suite does not test concurrent access, memory allocation failures, or all real boards.

## Test Signals
Strong signals are the expected route-set count for `pci-6070e`, different route-value matrices for `pci-6070e` and `pci-6220`, sortedness of route sets and sources, valid route count `57` for the fake device, invalid return codes such as `-EINVAL`, and correct register values for direct and indirect trigger paths.
