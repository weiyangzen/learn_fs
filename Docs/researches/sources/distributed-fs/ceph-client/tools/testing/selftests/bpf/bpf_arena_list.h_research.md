# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_list.h

Purpose: provides intrusive singly-headed, doubly-linked arena list primitives for BPF arena data structures.

Important APIs and types: `struct arena_list_node`, `struct arena_list_head`, `arena_list_node_t`, `arena_list_head_t`, `list_entry`, `list_entry_safe`, `list_for_each_entry`, `list_add_head()`, `list_del()`, and `__list_del()`.

Control flow: `list_add_head()` casts between user/kernel arena address spaces, updates node `next`, previous first node `pprev`, head `first`, and new node `pprev` using `WRITE_ONCE`. `list_del()` unlinks and poisons pointers. The iterator caches next before allowing deletion and uses `can_loop` to satisfy bounded-loop/verifier requirements.

State and persistence: list topology lives entirely in arena pointers. User-space fallback stubs make compilation possible but do not implement real iterator behavior.

Dependencies and integration points: depends on `bpf_arena_common.h`, `cond_break/can_loop` from experimental helpers for BPF builds, and arena address-space casts.

Risks: no concurrency protection; corrupted `pprev` can corrupt arbitrary arena memory; poison values are fixed low addresses; iteration semantics differ in user-space stub mode.

Test signals: list tests should cover add, delete, delete-while-iterating, empty lists, and verifier acceptance of bounded traversal.
