# sources/cloud-native/moby/contrib/syscall-test/exit32.s

## Purpose
Provides a minimal 32-bit assembly program that exits via a raw syscall.

## APIs, Types, And Functions
The assembly defines the entry sequence for a 32-bit Linux exit syscall. It has no C-level functions.

## Control Flow, State, And Integration
Execution enters the assembly entry point, loads syscall registers, invokes the kernel, and exits. It persists no state and is used only for architecture/syscall behavior checks.

## Risks And Test Signals
Risks include architecture incompatibility, assembler/toolchain availability, and host kernels without 32-bit syscall support. Integration is with seccomp and compatibility testing.
