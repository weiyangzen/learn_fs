# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/uaccess_flush.c

Purpose: measures whether the `powerpc/uaccess_flush` mitigation produces expected L1D misses around kernel user-access paths.

Important APIs/types/functions: `uaccess_flush_test()` uses debugfs reads/writes, perf event helpers, `syscall_loop_uaccess()`, and `set_dscr()`.

Control flow: the test skips unless root and Power7+ PMU support are available, reads original RFI/entry/uaccess flush settings, disables RFI and entry flushing, measures L1D misses for repeated `uname()` calls with the original uaccess setting, toggles uaccess flushing and repeats, then restores all three knobs.

State and persistence behavior: debugfs mitigation files and DSCR are temporary mutable state. Normal cleanup restores them; early hard failures may not.

Dependencies and integration points: depends on debugfs powerpc security knobs, perf counters, and common flush utilities.

Risks and test signals: the error message for missing uaccess debugfs says entry_flush, which can mislead diagnosis. PASS/FAIL messages provide miss totals and thresholds.
