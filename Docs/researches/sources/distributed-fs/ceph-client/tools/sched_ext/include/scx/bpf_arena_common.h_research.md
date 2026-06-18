# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/bpf_arena_common.h

Purpose: user-space counterpart for BPF arena code, allowing shared headers to compile outside BPF while treating arena annotations and casts as no-ops.

Important APIs/macros: defines `arena_container_of()`, includes `<sys/user.h>` to get `PAGE_SIZE`, defines empty `__arena`, `__arg_arena`, `cast_kern()`, and `cast_user()`, provides weak `arena[1]`, fallback `offsetof`, and a stub `bpf_arena_alloc_pages()` returning `NULL`.

Control flow: none beyond the inline stub allocation function.

State and persistence: the weak `arena` symbol is a compile/link placeholder. No runtime persistent state.

Dependencies and integration: included by user-space `common.h`. It lets code that names arena-qualified pointers or helpers compile in loaders and tests without pulling in BPF-only declarations.

Risks: user-space arena allocation always returns `NULL`; shared code must not assume it can allocate real arena memory outside BPF. Empty annotations may hide type/address-space issues that only appear in BPF builds.

Test signals: compile user-space sched_ext loaders and any shared arena-using code; ensure no accidental user-space runtime path depends on successful `bpf_arena_alloc_pages()`.
