# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/misc.c

## Purpose
`misc.c` is the shared support library for POWER PMU sampling and event-code tests. It centralizes platform/PVR gating, raw event-code field masks, perf mmap sample parsing, interrupt-register extraction, threshold-compare conversion, and generic compat PMU detection.

## Important APIs, Types, and Functions
Important exported helpers are `check_pvr_for_sampling_tests()`, `platform_check_for_tests()`, `perf_get_platform_reg_mask()`, `check_extended_regs_support()`, `event_sample_buf_mmap()`, `__event_read_samples()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, `get_thresh_cmp_val()`, `check_for_generic_compat_pmu()`, and `check_for_compat_mode()`. Global state includes `pvr`, `platform_extended_mask`, and the `ev_mask_*`/`ev_shift_*` field tables consumed by `EV_CODE_EXTRACT`.

## Control Flow and State
Platform setup reads `SPRN_PVR`, checks HWCAP2 bits for EBB and architecture level, probes `PERF_SAMPLE_REGS_INTR`, then initializes event-code field layouts differently for POWER9 versus POWER10/POWER11. Sampling helpers mmap the perf ring buffer, read `data_head`/`data_tail` with a memory barrier, count or return samples, skip branch-stack records when present, and map register names to indexes in the interrupt register array. Threshold comparison conversion clamps POWER10 thresholds and encodes mantissa/exponent values to match MMCRA programming. State is process-global and must be initialized before tests use `EV_CODE_EXTRACT` or `get_reg_value`.

## Dependencies and Integration Points
The library depends on `event.h`, perf UAPI sample formats, auxv platform strings, `/sys/bus/event_source/devices/cpu/caps/pmu_name`, Power ISA HWCAP2 flags, and kselftest utility helpers. It is linked by both `event_code_tests` and `sampling_tests`.

## Risks and Test Signals
Risks are stale field masks for new CPUs, off-by-one register-mask checks, perf ring-buffer parsing assumptions, and false generic-PMU detection if sysfs or auxv changes. Strong signals are clean skips on unsupported systems, successful sample collection, correct register-field extraction across POWER9/10/11, and no mmap parser overrun when branch-stack records precede register payloads.
