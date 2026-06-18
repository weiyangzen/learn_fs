# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/hyp-constants.c

## Purpose

This file emits compile-time constants for hyp assembly by including `asm-offsets.h` under the hyp build.

## Important APIs, Types, And Functions

It defines `KBUILD_MODNAME` as `"kvm_hyp"` and includes `../kernel/asm-offsets.c`. There are no callable functions.

## Control Flow

Only build-time constant generation occurs.

## State And Persistence Behavior

The output is generated assembler constants consumed by hyp assembly. There is no runtime state.

## Dependencies And Integration Points

It integrates arm64 KVM hyp assembly with kernel structure offsets such as vCPU context and CPU register layout.

## Risks And Test Signals

Risks are stale or missing offsets causing assembly context save/restore corruption. Test signals are successful offset generation and build failures when structure references are invalid.
