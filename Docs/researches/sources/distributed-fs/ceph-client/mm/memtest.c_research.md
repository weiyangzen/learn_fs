<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/memtest.c -->
# sources/distributed-fs/ceph-client/mm/memtest.c

## Purpose

`memtest.c` implements the early boot `memtest=` physical memory test. It writes a sequence of 64-bit patterns over free memblock ranges, verifies the pattern, reserves any bad physical ranges so the rest of the kernel will not allocate them, and reports the reserved bad-memory total through proc meminfo. The complete 139-line file was read.

## Important APIs, Types, and Functions

The file keeps `early_memtest_done`, `early_memtest_bad_size`, and the `patterns[]` table, whose first entry is zero so the final pass can leave memory zeroed. Important functions are `parse_memtest()`, registered by `early_param("memtest", ...)`, `early_memtest()`, `do_one_pass()`, `memtest()`, `reserve_bad_mem()`, and `memtest_report_meminfo()`.

## Control Flow

Boot parameter parsing sets `memtest_pattern` to the user-supplied count or to the number of built-in patterns when `memtest` is passed without an argument. `early_memtest(start, end)` returns immediately when disabled. Otherwise it iterates backward for the requested number of tests, maps each pass to `patterns[i % ARRAY_SIZE(patterns)]`, and calls `do_one_pass()`. `do_one_pass()` walks free memblock ranges, clamps them to the requested physical bounds, logs the range and pattern, and calls `memtest()`. `memtest()` aligns the start address to an eight-byte pattern boundary, writes the pattern with `WRITE_ONCE()`, reads it back with `READ_ONCE()`, coalesces adjacent bad words into physical ranges, and calls `reserve_bad_mem()` for each bad span.

## State and Persistence Behavior

Bad regions are persisted by `memblock_reserve()`, making them unavailable for later boot allocation. `early_memtest_bad_size` accumulates the reserved byte total, and `early_memtest_done` controls whether `memtest_report_meminfo()` emits `EarlyMemtestBad`. A reported value of zero after a completed test means the test ran successfully without detected bad memory.

## Dependencies and Integration Points

The implementation depends on early memblock free-range iteration, direct physical-to-virtual mapping via `__va()`, boot parameter parsing, kernel logging, and procfs meminfo emission through `seq_file`. It must run early enough that tested free ranges are safe to overwrite and before normal allocators consume bad regions.

## Risks and Edge Cases

The test is destructive by design and must only touch free memblock ranges. Start alignment can skip leading unaligned bytes. `VM_WARN_ON_ONCE()` guards against impossible underflow when the aligned start exceeds the range. The loop in `early_memtest()` uses unsigned decrement from `memtest_pattern - 1` to zero, so disabled state must be filtered before entering it. Very small bad totals report as 1 kB to avoid hiding nonzero failures after shifting to KiB.

## Test Signals

Useful signals include boot tests with `memtest=0`, `memtest=1`, and bare `memtest`, log verification for tested ranges and patterns, injected memory corruption in an early test environment, checks that bad spans are reserved in memblock and reflected in `EarlyMemtestBad`, and confirmation that no proc output appears when the early test did not run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/memtest.c -->
