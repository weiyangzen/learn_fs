# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/check_extended_reg_test.c

## Purpose
`check_extended_reg_test.c` checks whether perf supports the platform extended interrupt register mask used by the PMU sampling tests.

## Important APIs, Types, and Functions
The central routine is `check_extended_reg_test, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `the raw event selected in the file`.

## Control Flow and State
The test primarily probes support paths: it constructs an event or helper call that may be unsupported, then requires a clean skip/failure result rather than a kernel crash or malformed sample path. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.
