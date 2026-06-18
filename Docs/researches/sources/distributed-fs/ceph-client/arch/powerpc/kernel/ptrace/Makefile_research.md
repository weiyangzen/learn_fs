# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/Makefile

## Purpose
This Makefile composes the PowerPC ptrace implementation from core, compatibility, feature-specific regset, and debug-breakpoint source files.

## Important APIs, Types, And Functions
It sets `CFLAGS_ptrace-view.o += -DUTS_MACHINE='"$(UTS_MACHINE)"'` so `ptrace-view.c` can name the native user regset view. It always builds `ptrace.o`, `ptrace-view.o`, and `ptrace-fpu.o`; conditionally builds `ptrace32.o`, `ptrace-vsx.o`, `ptrace-altivec.o`, `ptrace-spe.o`, `ptrace-tm.o`, and `ptrace-adv.o`; and builds `ptrace-novsx.o` or `ptrace-noadv.o` as fallback implementations when the matching feature is absent.

## Control Flow
Kernel Kbuild evaluates `obj-y`, `obj-$(CONFIG_*)`, and `ifneq` clauses to select the correct object set for the target configuration.

## State And Persistence
There is no runtime state. The persistent effect is the build graph and the compile-time definition of `UTS_MACHINE` for native regset metadata.

## Dependencies And Integration Points
The Makefile gates C definitions declared in `ptrace-decl.h`; exactly one FPR regset provider (`ptrace-vsx.c` or `ptrace-novsx.c`) and exactly one advanced-debug provider (`ptrace-adv.c` or `ptrace-noadv.c`) should be linked.

## Risks
Incorrect conditionals can produce duplicate symbols or missing symbols for declarations shared by `ptrace-decl.h`. Configuration combinations such as VSX without Altivec or PPC32 with VSX are constrained elsewhere and need build coverage.

## Test Signals
Build matrices should cover native PPC32, PPC64 with compat, VSX and non-VSX, Altivec, SPE, transactional memory, advanced debug registers, and generic hardware breakpoint configurations.
