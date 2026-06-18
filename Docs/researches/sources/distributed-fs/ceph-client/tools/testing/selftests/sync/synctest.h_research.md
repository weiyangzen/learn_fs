# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/synctest.h

## Purpose
Defines the shared test harness surface for the sync selftests: assertion and run macros plus prototypes for every test function compiled into the runner.

## Important APIs, Types, And Functions
`ASSERT(cond, msg)` prints a kselftest error message and returns `1` from the current test on failure. `RUN_TEST(x)` passes a function and its name to `run_test()`. The header declares allocation, fence, merge, wait, parallelism, consumer, and random-merge stress test functions.

## Control Flow
The macros shape control flow in all test implementations. Failed assertions return immediately from the test function, which becomes the child process exit status consumed by `sync_test.c`.

## State And Persistence
No state is held here. It centralizes the convention that test success is return `0` and failure is return `1`.

## Dependencies And Integration Points
Includes `../kselftest.h` for output and integrates all sync `.c` test files with the single runner. It relies on `run_test()` being visible in `sync_test.c` before macro expansion.

## Risks
`ASSERT` returns from the enclosing function, so using it in helper functions only signals failure if callers propagate the return value. It cannot run cleanup automatically, making fd cleanup after failed mid-test assertions dependent on process isolation.

## Test Signals
Compilation and clear kselftest `[ERROR]` messages from failed assertions are the primary signals. The full prototype list also protects against missing test objects at link time.
