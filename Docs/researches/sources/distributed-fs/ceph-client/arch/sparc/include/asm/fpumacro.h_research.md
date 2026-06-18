<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/fpumacro.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/fpumacro.h

## Purpose
This header provides SPARC FPU/VIS state-management macros for assembly routines.

## Important APIs, Types, and Functions
It defines macros such as VIS entry/exit or FPU register transfer helpers used by crypto and low-level floating-point assembly.

## Control Flow
Assembly routines expand these macros to enable/use VIS/FPU state safely and preserve required calling conventions.

## State and Persistence Behavior
The macros affect transient FPU/VIS register state and FPRS flags.

## Dependencies and Integration Points
It integrates with SPARC64 crypto assembly, floating-point trap handling, and kernel FPU state rules.

## Risks
Incorrect FPU state management can corrupt user FPU registers or leak kernel crypto state.

## Test Signals
Run crypto selftests, FPU user workload during kernel crypto activity, and preemption/interrupt stress if applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/fpumacro.h -->
