<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/net/bpf_jit.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/net/bpf_jit.c

### Purpose
`bpf_jit.c` is the LoongArch eBPF JIT backend. It translates BPF instructions into LoongArch machine code, handles BPF text patching and invalidation, emits BPF trampoline code, supports kfuncs/arenas/fsession/subprog tailcalls, and frees JIT images.

### Important APIs, Types, And Functions
Major public functions are `bpf_jit_supports_kfunc_call()`, `bpf_jit_supports_far_kfunc_call()`, `ex_handler_bpf()`, `bpf_arch_text_copy()`, `bpf_arch_text_poke()`, `bpf_arch_text_invalidate()`, `arch_alloc_bpf_trampoline()`, `arch_free_bpf_trampoline()`, `arch_protect_bpf_trampoline()`, `arch_prepare_bpf_trampoline()`, `arch_bpf_trampoline_size()`, `bpf_int_jit_compile()`, `bpf_jit_free()`, and support booleans for speculation bypass, arenas, fsession, and subprog tailcalls. Core internals are `build_prologue()`, `build_body()`, `build_insn()`, `build_epilogue()`, `emit_bpf_tail_call()`, atomic emitters, exception handler creation, text patch helpers, and trampoline invocation helpers.

### Control Flow
`bpf_int_jit_compile()` exits if JIT was not requested, then performs a sizing pass with `ctx.image == NULL`, allocates RW/RO packed BPF binary memory plus extable space, emits real instructions, validates no `INSN_BREAK` holes remain and extable counts match, finalizes ROX text, flushes I-cache, fills line info, and handles subprogram extra passes through `prog->aux->jit_data`. `build_insn()` translates arithmetic, moves, endian swaps, branches, calls, tail calls, loads/stores, atomics, probe-memory modes, arena-relative access, and exits. Trampoline preparation computes a stack frame for saved args, return values, metadata, cookies, run context, tail-call context, and stack args; it emits fentry/fmod_ret/fexit/original-call flow and patches reserved conditional branches after targets are known.

### State, Persistence, And Dependencies
Persistent runtime state includes generated executable BPF images, optional extable entries in `prog->aux->extable`, `prog->jited`, `prog->jited_len`, `prog->bpf_func`, trampoline images, and temporary `jit_data` across subprogram passes. Dependencies include generic BPF verifier/JIT APIs, BTF kfunc models, BPF trampoline/session-cookie infrastructure, LoongArch instruction encoders from `asm/inst.h`, text patching via `larch_insn_text_copy()`, cache flushing, `text_mutex`, CPU hotplug read locks, and exception handling in `mm/extable.c`.

### Integration Points
The Makefile gates this file under `CONFIG_BPF_JIT`. Probe-memory extable entries are dispatched by `fixup_exception()`. BPF program pack allocation and kallsyms integrate with generic BPF. Text poking supports fentry/fexit, calls, and BPF program entry patching. Atomic instructions depend on LoongArch CPU features such as `cpu_has_lam_bh`.

### Risks
JIT correctness is security-critical. Branch offsets are limited to signed 26-bit or 16-bit tail-call branches and return `-E2BIG`/`-EINVAL` when too far. Register mapping and ABI extension must match BPF and LoongArch calling conventions. Probe-memory extable offsets use RO/RW image address translation and range checks. Text patching must compare old instructions exactly to avoid racing wrong code. Atomic byte/halfword operations require hardware support. Trampoline frame layout is complex and flag-dependent.

### Test Signals
Run `test_bpf`, BPF selftests, verifier/JIT differential tests, tail-call and bpf2bpf tests, kfunc/trampoline/fentry/fexit/fmod_ret/fsession tests, arena/probe-memory tests, atomic instruction tests on CPUs with and without LAM_BH, text-poke stress, and JIT hardening/constant blinding tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/net/bpf_jit.c -->
