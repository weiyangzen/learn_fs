# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/rfi_flush.c

Purpose: measures whether the `powerpc/rfi_flush` mitigation causes the expected L1D miss pattern on return-from-interrupt/syscall paths.

Important APIs/types/functions: `rfi_flush_test()` uses debugfs integer helpers, perf cache counters, `syscall_loop()`, and `set_dscr()`.

Control flow: after root and PMU skips, the test reads original RFI flush and optional entry flush state, disables entry flush if present, opens an L1D miss counter, disables prefetching through DSCR, runs a repeated syscall/cacheline loop, checks misses against threshold, toggles RFI flush, repeats, then restores original knobs.

State and persistence behavior: temporarily mutates debugfs and DSCR state. It closes the perf fd and restores knobs only on the normal path.

Dependencies and integration points: requires real debugfs mitigation controls, Power7+ PMU events, and `flush_utils.c`.

Risks and test signals: perf noise and scheduler contention may cause false failures. PASS/FAIL output reports total misses and threshold direction for each RFI setting.
