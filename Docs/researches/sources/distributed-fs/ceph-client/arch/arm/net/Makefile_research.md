# sources/distributed-fs/ceph-client/arch/arm/net/Makefile

## Purpose
Builds ARM-specific networking support objects. In this subset it controls inclusion of the 32-bit ARM BPF JIT.

## Important APIs, Types, And Functions
The sole rule is `obj-$(CONFIG_BPF_JIT) += bpf_jit_32.o`.

## Control Flow
Kbuild includes `bpf_jit_32.o` only when `CONFIG_BPF_JIT` is enabled. If disabled, networking falls back to interpreter or generic non-JIT paths.

## State, Dependencies, And Integration
No runtime state. Depends on Kbuild and `CONFIG_BPF_JIT`. Integrates with `arch/arm/net/bpf_jit_32.c` and the kernel BPF core.

## Risks And Test Signals
Risks are simple build gating mistakes. Test signals are ARM builds with `CONFIG_BPF_JIT=y/m/n` and BPF selftests confirming the arch JIT is present only when configured.
