# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arena_htab.c

Purpose: tests hash table data structures allocated in BPF arena memory, for both compiler-generated and hand-written assembly variants.

Important APIs/types/functions: generated skeletons `arena_htab.skel.h` and `arena_htab_asm.skel.h` expose BPF programs. Shared validation `test_arena_htab_common` checks `struct htab` from `bpf_arena_htab.h`, verifies buckets exist, and calls `htab_lookup_elem` on keys 0, 4, 8, and 12 expecting key-value equality.

Control flow: LLVM path opens/loads skeleton, faults in arena page zero via `bpf_map__initial_value`, runs `arena_htab_llvm`, handles compiler support skip, then validates the user-visible arena hash table pointer. ASM path opens/loads, runs `arena_htab_asm`, and validates the same structure.

State and persistence behavior: arena pages contain the hash table buckets and nodes created by BPF. Userspace reads arena pointers and traverses bucket lists after the BPF program returns. State disappears with skeleton destruction.

Dependencies and integration points: depends on arena map support, generated skeletons, `bpf_arena_htab.h`, mmap-visible arena initial value access, and `test_progs.h`.

Risks: direct userspace traversal of arena pointers assumes pointer relocation and arena mapping are correct. LLVM variant can skip on missing `arena_cast` support, reducing coverage on older toolchains.

Test signals: successful BPF test run, non-null buckets, and matching lookup values. Two subtests isolate LLVM and ASM paths.
