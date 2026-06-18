# sources/distributed-fs/ceph-client/drivers/clk/clk-fixed-rate_test.h


### Purpose
`clk-fixed-rate_test.h` provides shared constants for the fixed-rate KUnit overlay tests.

### Important APIs, Types, And Functions
It defines `TEST_FIXED_FREQUENCY` as `50000000` and `TEST_FIXED_ACCURACY` as `300`. There are no functions or data structures.

### Control Flow, State, And Persistence
The header has no runtime control flow or persistent state. Its values are compiled into the KUnit test and must match the test device-tree overlay referenced by `clk-fixed-rate_test.c`.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on inclusion by `clk-fixed-rate_test.c` and the overlay generated for `kunit_clk_fixed_rate_test`. Risks are simple drift between constants and overlay data or accidental include-guard mismatch. Test signals are the OF fixed-rate KUnit assertions that compare `clk_get_rate()` and `clk_get_accuracy()` to these constants.
