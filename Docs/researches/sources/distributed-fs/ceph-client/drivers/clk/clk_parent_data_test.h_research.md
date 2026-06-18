# sources/distributed-fs/ceph-client/drivers/clk/clk_parent_data_test.h

## Purpose

`clk_parent_data_test.h` centralizes string constants used by clock parent-data KUnit tests and their DT overlays. It keeps the expected legacy names, firmware names, and generated parent names consistent between C test logic and overlay data.

## Important APIs, Types, And Functions

The file defines four macros: `CLK_PARENT_DATA_1MHZ_NAME`, `CLK_PARENT_DATA_PARENT1`, `CLK_PARENT_DATA_PARENT2`, and `CLK_PARENT_DATA_50MHZ_NAME`. There are no functions or types.

## Control Flow

There is no runtime control flow. The constants are substituted at compile time into test cases that build `struct clk_parent_data` values.

## State And Persistence Behavior

The header has no state and no persistence behavior. It only provides compile-time string literals.

## Dependencies And Integration Points

`clk_test.c` includes this header for the `clk_register_clk_parent_data_of_*`, `clk_register_clk_parent_data_device_*`, and direct-`hw` parent-data parameter tables. The values must align with the KUnit DT overlay data referenced through `kunit_clk_parent_data_test`.

## Risks And Edge Cases

Because this header is the shared contract between test code and overlay contents, changing a string without updating the overlay will produce parent lookup failures rather than compile errors. The include guard prevents duplicate macro definitions.

## Test Signals

The parent-data suites in `clk_test.c` verify these constants by expecting parent lookup through OF index, firmware name, global name, and direct hardware pointer to resolve to the intended clocks.
