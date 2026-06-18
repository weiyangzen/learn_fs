# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/slice_test.c

Purpose: `slice_test.c` validates the rseq time-slice extension using the kselftest harness. It requests short slice extensions while a noise thread creates intermittent CPU pressure, then reports whether requests succeed, yield, schedule out, race, or abort.

Important APIs, types, and functions: it defines `struct noise_params`, a `slice_ext` fixture, three fixture variants, `elapsed()`, `noise_thread()`, fixture setup/teardown, and `TEST_F(slice_ext, slice_test)`. It uses `rseq_get_abi()`, `__rseq_register_current_thread()`, `RSEQ_READ_ONCE()`, `RSEQ_WRITE_ONCE()`, `prctl(PR_RSEQ_SLICE_EXTENSION, ...)`, and `syscall(__NR_rseq_slice_yield)`.

Control flow: setup registers rseq in nolibc mode, enables the slice extension with `prctl`, pins the test to one nonzero allowed CPU, and starts a noise thread. The test loop runs for the variant duration, writes `slice_ctrl.request`, busy-waits for the target slice span, clears pending requests, handles granted slices by either yielding or forcing an abort path, and counts outcomes. Teardown stops and joins the noise thread.

State and persistence: state lives in the fixture, the noise thread's `run` flag, and the current thread's `rseq_abi.slice_ctrl`. The kernel may set and clear `slice_ctrl.granted`; userspace writes `request`.

Dependencies and integration points: depends on kselftest harness macros, pthreads, scheduler affinity, `prctl` slice extension constants, the rseq syscall stack, and optional fallback syscall numbers/constants for newer kernel interfaces.

Risks and test signals: this is timing-sensitive and can skip when rseq or the extension is unsupported. It assumes at least one allowed CPU greater than zero for pinning. Test signals are successful harness completion and printed counters for total, success, yielded, aborted, scheduled, and raced events.
