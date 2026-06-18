# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_denormal.c

## Purpose
Regression test for POWER8 FPU denormal handling during conversion and process exit.

## Important APIs, Types, and Functions
Defines `test_denormal_fpu()` and `main()`. The test crafts a 32-bit denormal float bit pattern, converts it to double, and checks the expected renormalized 64-bit representation.

## Control Flow
Main runs the single test through `test_harness()`.

## State and Persistence
Only local FP variables are used; no persistent state.

## Dependencies and Integration Points
Depends on FPU behavior, libc `memcpy`, and PowerPC harness utilities.

## Risks and Test Signals
Risk is CPU/model-specific FP denormal behavior; failure indicates wrong result or potential kernel FP save/restore issues described by the file comment.
