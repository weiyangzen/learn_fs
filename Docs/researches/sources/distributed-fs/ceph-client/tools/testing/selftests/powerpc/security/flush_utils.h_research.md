# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/flush_utils.h

Purpose: declares shared constants and helper prototypes for powerpc cache flush mitigation selftests.

Important APIs/types/functions: defines `CACHELINE_SIZE` as 128 and `PERF_L1D_READ_MISS_CONFIG` as the hardware L1D read-miss perf-event encoding. Declares `syscall_loop()`, `syscall_loop_uaccess()`, and `set_dscr()`.

Control flow: no executable control flow; it centralizes the perf config and workload interfaces for multiple C tests.

State and persistence behavior: no state. Callers own all buffers and perf counters.

Dependencies and integration points: requires Linux perf event constants to be visible through the including translation unit, normally via `utils.h` and kernel headers.

Risks and test signals: the fixed 128-byte cacheline assumption matches the targeted powerpc systems; using it elsewhere would skew expected miss counts.
