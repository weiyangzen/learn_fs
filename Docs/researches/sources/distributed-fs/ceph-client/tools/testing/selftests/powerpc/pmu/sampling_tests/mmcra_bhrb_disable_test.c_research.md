# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_bhrb_disable_test.c

## Purpose
`mmcra_bhrb_disable_test.c` checks MMCRA BHRB disable state when branch stack sampling is configured.

## Important APIs, Types, and Functions
The central routine is `mmcra_bhrb_disable_test, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `EventCode`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.
