# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/Makefile

## Purpose
Defines the built-in object list for x86 kernel FPU support.

## Important APIs, Types, And Functions
The `obj-y` rule builds `init.o`, `bugs.o`, `core.o`, `regset.o`, `signal.o`, and `xstate.o` into the kernel FPU subsystem.

## Control Flow
There is no runtime control flow. Kbuild compiles and links the listed objects whenever this directory is included in the architecture build.

## State, Persistence, And Dependencies
The file contributes build-time state only. Runtime dependencies are expressed by the object files it includes; notably `xstate.o` is required even though it is outside this work item.

## Integration Points
Connects FPU initialization, bug checks, core context management, ptrace/core-dump regsets, signal frames, and xstate handling into the architecture kernel.

## Risks
Removing or reordering objects can cause missing symbols or initialization dependencies. Adding FPU files requires updating this list or related conditional Kbuild rules.

## Test Signals
Architecture builds should link all FPU symbols, and boot should execute FPU initialization without unresolved references.
