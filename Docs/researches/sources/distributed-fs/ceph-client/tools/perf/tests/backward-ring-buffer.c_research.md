# sources/distributed-fs/ceph-client/tools/perf/tests/backward-ring-buffer.c

Purpose: `backward-ring-buffer.c` verifies perf overwrite/backward ring-buffer reading for a tracepoint event.

Important APIs and state: `testcase` triggers `NR_ITERS` `prctl(PR_SET_NAME)` calls. `count_samples` reads `evlist->overwrite_mmap` and counts only `PERF_RECORD_SAMPLE` and `PERF_RECORD_COMM`. `do_test` mmap/enables/disables/reads a configured evlist. The suite is `"Read backward ring buffer"`.

Control flow: the test targets the current PID/TID, parses `syscalls:sys_enter_prctl/overwrite/`, configures mmap recording, opens the evlist, runs once with default mmap pages and checks exact sample and comm counts, then reopens and runs with one mmap page to exercise constrained backward-buffer behavior.

State and persistence: state is kernel perf event descriptors and mmaps owned by the evlist. They are opened, unmapped, closed, and deleted during the test. No files are written.

Dependencies, integration, risks, and tests: it depends on syscall tracepoints, sufficient permissions, and overwrite mmap support. It skips when tracepoint parsing fails, commonly without root or tracing access. Risks include exact count sensitivity to lost records or environment changes. Test signals are `NR_ITERS` sample records and `NR_ITERS` comm records in the first run and successful processing in the one-page run.
