# sources/distributed-fs/ceph-client/arch/powerpc/net/bpf_jit_comp.c

## Purpose
This file is the common PowerPC eBPF JIT orchestration layer. It allocates and finalizes packed executable images, drives multi-pass code generation, manages line-info and exception-table fixups, supports private BPF stacks, provides trampoline generation, and patches BPF program entry text for trampoline attach/detach.

## Important APIs, Types, And Functions
Key APIs include `bpf_int_jit_compile()`, `bpf_add_extable_entry()`, `bpf_arch_text_copy()`, `bpf_arch_text_invalidate()`, `bpf_jit_free()`, `arch_alloc_bpf_trampoline()`, `arch_prepare_bpf_trampoline()`, `arch_bpf_trampoline_size()`, and `bpf_arch_text_poke()`. `struct powerpc_jit_data` stores deferred subprogram JIT state. Helper functions include `bpf_jit_build_fentry_stubs()`, `bpf_jit_emit_exit_insn()`, private-stack guard init/check, trampoline invocation helpers, and text modification helpers.

## Control Flow
`bpf_int_jit_compile()` exits unless JIT was requested, allocates per-program JIT data, optionally allocates a guarded per-CPU private stack, runs a dry body pass to compute addresses and seen features, optionally repeats for tail calls or large programs, reallocates registers, sizes prologue/epilogue, allocates packed RW/RO images plus fixup/extable space, emits two real passes, writes ABI v1 function descriptors, finalizes text, updates `fp->bpf_func`, line info, and instruction pointers, or stores partial state for subprogram finalization. `bpf_add_extable_entry()` emits fixup instructions and relative exception-table entries for probe-memory loads. Trampoline generation builds a PPC ABI stack frame, saves args/cookies/metadata, invokes fentry/fmod_ret/fexit programs, optionally calls the original function, restores state, and emits safe return paths.

## State And Persistence
Persistent state includes packed JIT image text, optional `fp->aux->jit_data`, `fp->aux->extable`, `fp->aux->priv_stack_ptr`, BPF kallsyms metadata, and static stub size offsets `bpf_jit_ool_stub`/`bpf_jit_long_branch_stub`.

## Dependencies And Integration Points
It integrates with the architecture backends declared in `bpf_jit.h`, BPF verifier metadata, packed BPF image allocator, PowerPC text patching, ftrace/trampoline APIs, exception tables, kfunc/support capability hooks, and PPC64 ABI details.

## Risks And Test Signals
Risks include pass-size instability, extable relative offset overflow, RO/RW image offset mistakes, private stack guard corruption, trampoline ABI frame errors, stale instruction-cache synchronization in text poking, and unsupported PPC32 trampoline paths. Test signals include kernel BPF selftests, probe-memory loads, subprograms, tail calls, kfuncs, trampolines/fentry/fexit/fmod_ret, attach/detach stress, private stack overflow detection, and `bpf_jit_enable > 1` dumps.
