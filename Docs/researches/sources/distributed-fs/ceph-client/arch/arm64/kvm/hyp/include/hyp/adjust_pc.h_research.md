# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/adjust_pc.h

## Purpose

This header provides inline helpers for advancing guest or host PCs after emulated instructions.

## Important APIs, Types, And Functions

Functions are `kvm_skip_instr()`, `__kvm_skip_instr()`, and `kvm_skip_host_instr()`.

## Control Flow

`kvm_skip_instr()` dispatches to AArch32 skip logic or advances AArch64 PC by 4 and clears BTYPE, then clears single-step state. `__kvm_skip_instr()` synchronizes live EL2 ELR/SPSR into vCPU state, skips, and writes adjusted values back. `kvm_skip_host_instr()` advances host ELR by 4.

## State And Persistence Behavior

It mutates guest PC, CPSR/PSTATE, EL2 ELR/SPSR, BTYPE, and single-step bits.

## Dependencies And Integration Points

It is included by hyp exception, switch, and nested code. AArch32 support comes from `kvm_skip_instr32()`.

## Risks And Test Signals

Risks are incorrect instruction length, stale live sysreg state during hyp emulation, and leaving single-step/BTYPE active. Test signals include emulated sysregs, VGIC MMIO fast paths, AArch32 Thumb traps, and host instruction skip after nVHE host traps.
