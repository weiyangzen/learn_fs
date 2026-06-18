<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/count_instructions.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/count_instructions.c

Purpose: Counts a known instruction loop with perf events and verifies PMU instruction counters are close to expected values.

Important APIs and types: Defines `setup_event`, `do_count_loop`, `determine_overhead`, `test_body`, `count_instructions`, and `main()`. Calls external `thirty_two_instruction_loop` from `loop.S`.

Control flow: `test_body()` configures events, measures overhead, runs loops for requested instruction counts, reads perf counters, and checks deltas against expected instruction totals with tolerances.

State and persistence: State lives in local `struct event` objects and perf fds; no persistence.

Dependencies and integration points: Depends on `event.h`, `lib.h`, `utils.h`, perf_event_open support, and 64-bit assembly loop code.

Risks: Counter skid, privilege filters, and PMU availability can affect accuracy. The test assumes the assembly loop contains a stable instruction count.

Test signals: Pass means instruction PMU events count deterministic userspace loops within expected bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/count_instructions.c -->
