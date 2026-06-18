# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/avx.c

## Purpose

`avx.c` is a compact xstate test driver for AVX and AVX-512 register components. It validates YMM, opmask, high ZMM, and high-16 ZMM xstate handling through the shared xstate framework.

## Important APIs, Types, and Functions

The file includes `xstate.h` and calls `test_xstate()` for `XFEATURE_YMM`, `XFEATURE_OPMASK`, `XFEATURE_ZMM_Hi256`, and `XFEATURE_Hi16_ZMM`.

## Control Flow

`main()` sequentially invokes the generic xstate test for each listed feature. The Makefile compiles this target with `-mno-avx -mno-avx512f` so compiler-generated vector instructions do not accidentally interfere with test-controlled xstate.

## State and Persistence Behavior

Only process CPU xstate is manipulated. There is no persistent state.

## Dependencies and Integration Points

It depends on the shared `xstate.c` support, CPU/kernel support for the relevant xfeatures, and x86 selftest build flags.

## Risks and Edge Cases

Unsupported features must be skipped by the shared xstate harness. Because tests run sequentially in one process, the helper must correctly reset or isolate per-feature state.

## Test Signals

Signals are the generic xstate harness results for YMM, opmask, ZMM high-256, and high-16 ZMM state.
