# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_common.h

Purpose: central compatibility layer for BPF arena address-space annotations, casts, page kfunc declarations, and user-space stubs.

Important APIs and types: defines `__arena`, `__arena_global`, `__arg_arena`, `cast_kern`, `cast_user`, `arena_container_of`, `arena_base(map)`, and weak kfunc declarations for `bpf_arena_alloc_pages`, `bpf_arena_reserve_pages`, and `bpf_arena_free_pages`.

Control flow: compile-time branches distinguish BPF and user-space builds. BPF builds use LLVM address-space attributes when available, otherwise emit `bpf_addr_space_cast`; user-space builds erase annotations and provide inert arena allocation stubs.

State and persistence: declares weak `arena` for user-space compatibility; real arena state is in BPF maps/kfunc-managed pages.

Dependencies and integration points: depends on `bpf_experimental.h` for casts in asm fallback, BPF feature macro `__BPF_FEATURE_ADDR_SPACE_CAST`, and kernel arena support.

Risks: behavior changes with compiler feature availability; older kernels may lack page-size assumptions or kfuncs; incorrect casts can lead to verifier rejection.

Test signals: successful compilation for both BPF and user-space consumers, and arena selftests that exercise address-space casts and page kfuncs.
