<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/fpu/test_fpu.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/fpu/test_fpu.c

## Purpose
This helper verifies that kernel FPU use by the `test_fpu` module does not corrupt user-mode floating point control state.

## Important APIs, Types, And Functions
`main()` opens `/sys/kernel/debug/selftest_helpers/test_fpu`, reads from it under default rounding, after `fesetround(FE_DOWNWARD)`, and after `feenableexcept(FE_ALL_EXCEPT)`. It checks `fegetround()` and `fegetexcept()`.

## Control Flow
Open failure prints `[SKIP]` and returns success. Each read triggers kernel module floating point work. The helper returns distinct failure codes if default access fails, downward rounding access fails, rounding mode is clobbered, unmasked exception access fails, or exception mask is clobbered.

## State And Persistence
It changes only the calling process FPU rounding mode and exception mask and reads a debugfs file. The expected persistent condition is that user FPU state remains unchanged across kernel entry/exit.

## Dependencies And Integration Points
It depends on libm/fenv, debugfs, and the `test_fpu` kernel module.

## Risks
The unmasked exception phase can expose severe kernel FPU bugs and potentially crash a broken kernel, as noted in the source. Open failure returns 0 with `[SKIP]`, so wrapper-level skip accounting may be weak.

## Test Signals
Pass output is `[OK]\ttest_fpu`; failures identify the precise state corruption or access phase.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/fpu/test_fpu.c -->
