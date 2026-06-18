# sources/distributed-fs/ceph-client/lib/find_bit_benchmark.c

## Purpose
Defines a loadable/init benchmark module for measuring performance of C `find_*_bit` operations over dense random and sparse random bitmaps. It is a performance smoke test, not a correctness suite.

## Important APIs, Types, and Functions
The module uses static initdata bitmaps `bitmap` and `bitmap2` of `BITMAP_LEN` bits and test helpers `test_find_first_bit()`, `test_find_first_and_bit()`, `test_find_next_bit()`, `test_find_next_zero_bit()`, `test_find_last_bit()`, `test_find_nth_bit()`, and `test_find_next_and_bit()`. `find_bit_test()` is registered with `module_init()`.

## Control Flow
On module init, the benchmark fills two bitmaps with random bytes, times several traversal patterns with `ktime_get()`, and prints nanosecond totals plus iteration counts. It then zeros both bitmaps, sets a sparse random subset of bits, repeats the timing tests, and returns `-EINVAL` intentionally so the benchmark can be inserted repeatedly without removing the module.

## State and Persistence
State is limited to static initdata bitmaps during initialization. No long-lived module state is kept because init returns failure by design.

## Dependencies and Integration Points
Depends on bitmap/bitops APIs, kernel random helpers, printk, module initialization, and timing APIs. It benchmarks the implementation selected by the build, including architecture overrides or generic fallbacks.

## Risks
The benchmark mutates copied bitmaps in first-bit tests and can take noticeable CPU time. It prints with `pr_err()` for visibility, which can look like a failure even though the final `-EINVAL` is intentional. Random input means timings vary run to run. It is not a correctness oracle; comments explicitly rely on boot coverage for broad correctness.

## Test Signals
Successful execution prints all benchmark lines for random and sparse phases, with plausible iteration counts. Compare timings across kernel changes or architectures. Confirm that returning `-EINVAL` does not leave the module loaded.
