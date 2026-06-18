# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/Makefile

## Purpose
Builds PowerPC math/register-state selftests for FPU, VMX, VSX, and MMA.

## Important APIs, Types, and Functions
Defines `TEST_GEN_PROGS`, includes lib.mk and flags.mk, links generated programs with `../harness.c`, adds `-O2 -g -pthread -m64 -maltivec`, and adds per-target assembly/source dependencies.

## Control Flow
The Makefile builds FPU targets with `fpu_asm.S`, VMX/VSX targets with their assembly helpers and `../utils.c`, and MMA with `mma.c`/`mma.S`.

## State and Persistence
Only build output is persisted.

## Dependencies and Integration Points
Integrates math context preservation tests into the PowerPC selftest tree.

## Risks and Test Signals
Risks are compiler support for Altivec/VSX/MMA flags and target dependency drift. Build success plus harness runs are the signals.
