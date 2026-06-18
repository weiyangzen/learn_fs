# sources/distributed-fs/ceph-client/arch/s390/kernel/bpf.c

## Purpose
Exposes an s390 BPF kfunc that lets BPF programs obtain the current CPU's lowcore pointer.

## Important APIs, Types, And Functions
`bpf_get_lowcore()` is declared with `__bpf_kfunc` and returns `struct lowcore *` by calling `get_lowcore()`. The definitions are wrapped in `__bpf_kfunc_start_defs()` and `__bpf_kfunc_end_defs()`.

## Control Flow
When a verifier-approved BPF program calls this kfunc, the BPF runtime invokes the helper and receives the lowcore address for the executing CPU.

## State And Persistence
No state is stored here. The returned pointer exposes live per-CPU lowcore state, so verifier and BTF typing are the safety boundary.

## Dependencies And Integration Points
Depends on BTF kfunc registration infrastructure and the s390 lowcore API. It integrates BPF observability with architecture-specific CPU state.

## Risks And Edge Cases
The main risk is exposing sensitive or unstable lowcore fields to BPF programs. Correct BTF typing, verifier restrictions, and privilege policy are critical. CPU migration semantics should be considered by BPF callers.

## Test Signals
Signals include BPF selftests that load a program using `bpf_get_lowcore`, verifier rejection for unsafe field access, BTF availability checks, and runtime validation on SMP systems.
