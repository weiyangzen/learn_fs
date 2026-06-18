# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu.h

## Purpose
Small helper for generating varied floating-point test data.

## Important APIs, Types, and Functions
Defines `randomise_darray(double *darray, int num)`, which fills an array with random positive/negative integers squared or reciprocal values.

## Control Flow
The function loops over requested elements and writes deterministic-from-`random()` double values.

## State and Persistence
Mutates caller-provided arrays only.

## Dependencies and Integration Points
Included by FPU syscall/preempt/signal tests to seed expected register contents.

## Risks and Test Signals
Risk is division by zero if `random()` returns zero on a reciprocal path; in practice randomization is used for stress data, and failures would show as register comparison mismatch or FP exception behavior.
