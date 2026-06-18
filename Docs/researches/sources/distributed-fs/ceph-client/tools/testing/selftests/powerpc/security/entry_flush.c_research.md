# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/entry_flush.c

Purpose: measures whether the `powerpc/entry_flush` mitigation produces the expected L1D cache-miss behavior on syscall entry.

Important APIs/types/functions: `entry_flush_test()` uses `read_debugfs_int()`, `write_debugfs_int()`, `perf_event_open_counter()`, `perf_event_enable/reset/disable()`, `syscall_loop()`, and `set_dscr()`.

Control flow: the test skips unless root and Power7-or-newer PMU support exist. It records original `rfi_flush` and `entry_flush`, disables RFI flushing, runs repeated syscall/cacheline loops under perf, checks miss thresholds with the original entry setting, toggles entry_flush, repeats, then restores both debugfs controls.

State and persistence behavior: mutates debugfs mitigation knobs and DSCR prefetch behavior. Intended restoration happens on normal control flow, but early failures after writes can leave mitigation state changed.

Dependencies and integration points: requires debugfs powerpc controls, perf hardware cache events, `flush_utils.c`, and `utils.c`.

Risks and test signals: PMU contention can distort counts. PASS/FAIL messages include miss totals and comparison thresholds; non-root or unavailable knobs result in skip.
