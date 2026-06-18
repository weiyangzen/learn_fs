# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_htab.c

## Purpose

BPF arena hash table exercise using helpers from `bpf_arena_htab.h`. It allocates an arena hash table, updates many elements, touches arena and non-arena arrays, and exposes the table pointer to userspace. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`BPF_MAP_TYPE_ARENA`, `bpf_alloc()`, `htab_init()`, `htab_update_elem()`, `cast_kern()`, `cast_user()`, arena globals, and `SEC("syscall") arena_htab_llvm`.

## Control Flow

When address-space casts are supported, the program allocates a hash table in arena memory, initializes it, loops up to 100000 updates while writing `arr1`, then does replacement updates for 1000 entries while touching `arr2`, casts the table pointer to user address space, and stores it in `htab_for_user`. Unsupported builds set `skip`.

## State and Persistence Behavior

Arena map pages hold the hash table and `arr1`; normal BSS holds `arr2`, `zero`, `skip`, and exported user pointer. State persists until map/skeleton teardown.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here. It depends on `bpf_arena_htab.h` and arena address-space cast support.

## Risks and Edge Cases

Long bounded loops stress verifier loop handling and arena pointer casts. Userspace pointer exposure must use the correct cast direction.

## Test Signals

Expected signals are `skip=false` on supported targets, successful syscall program run, populated arena hash table, and usable `htab_for_user` pointer for harness validation.
