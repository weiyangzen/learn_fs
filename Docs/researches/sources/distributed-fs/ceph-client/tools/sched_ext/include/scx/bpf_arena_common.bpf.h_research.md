# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/bpf_arena_common.bpf.h

Purpose: BPF-side compatibility header for BPF arena address-space pointers, arena allocation kfuncs, and portable loop break helpers.

Important APIs/macros: defines `PAGE_SIZE` from `__PAGE_SIZE`, `__arena`, `__arena_global`, `cast_kern()`, and `cast_user()` depending on compiler support for `__BPF_FEATURE_ADDR_SPACE_CAST`. When unavailable, `bpf_addr_space_cast()` emits raw BPF address-space-cast instructions through inline assembly. Declares weak arena kfuncs `bpf_arena_alloc_pages()`, `bpf_arena_free_pages()`, and `bpf_arena_reserve_pages()`. Defines `can_loop`, `cond_break`, and `cond_break_label` using `may_goto` or raw instruction encoding, plus `bpf_preempt_disable()`, `bpf_preempt_enable()`, and `bpf_arena_mapping_nr_pages()`.

Control flow: compile-time feature tests select either native LLVM address-space casts or inline assembly fallback. Loop helpers expand into verifier-aware control-flow constructs that can break portable BPF loops.

State and persistence: no persistent state. It controls pointer address-space annotations and generated BPF instructions at compile time.

Dependencies and integration: included by BPF code through `common.bpf.h` paths when arena functionality is needed. It depends on BPF kfunc availability in the running kernel and compiler feature macros.

Risks: raw instruction emission is architecture and verifier sensitive. Weak kfuncs may be unavailable at load/runtime, so users must gate behavior. `PAGE_SIZE` fallback assumes `__PAGE_SIZE` exists in generated BTF context.

Test signals: compile BPF programs with old and new LLVM, with and without `__BPF_FEATURE_ADDR_SPACE_CAST`, and load on kernels with and without arena kfuncs. Verifier acceptance of loops using `cond_break` is a key signal.
