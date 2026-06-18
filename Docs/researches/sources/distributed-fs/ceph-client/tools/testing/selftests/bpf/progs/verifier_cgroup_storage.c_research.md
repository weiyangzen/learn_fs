# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_cgroup_storage.c

## Purpose

`verifier_cgroup_storage.c` is a BPF verifier selftest focused on `bpf_get_local_storage()` for cgroup-local and percpu-cgroup-local storage. It checks that the verifier accepts valid storage lookups and rejects wrong map types, invalid pseudo-fds, out-of-bounds map-value accesses, negative offsets, non-zero helper flags, and unprivileged pointer leaks.

## Important APIs, Types, and Functions

The file defines three maps with BTF-style map declarations: `cgroup_storage` using `BPF_MAP_TYPE_CGROUP_STORAGE`, `percpu_cgroup_storage` using `BPF_MAP_TYPE_PERCPU_CGROUP_STORAGE`, and `map_hash_8b` as a deliberately wrong `BPF_MAP_TYPE_HASH`. All programs are `SEC("cgroup/skb")` naked assembly tests. The key helper API under test is `bpf_get_local_storage`, invoked with `BPF_PSEUDO_MAP_FD` operands and flag register `r2`. The `bpf_misc.h` metadata macros declare expected verifier success, unprivileged behavior, return values, flags, and exact diagnostic fragments.

## Control Flow

The valid tests load the cgroup-storage map pseudo-fd, pass zero flags, call `bpf_get_local_storage`, then read and write a word inside the 64-byte value. Invalid variants change one verifier precondition at a time: using the hash map, using a raw immediate in place of a map pseudo-fd, accessing offset 256, accessing a negative offset, or passing non-zero flags through either an immediate or a pointer-like register. The percpu half repeats the same pattern against `percpu_cgroup_storage`.

## State and Persistence Behavior

Persistent state is limited to map definitions. Runtime local-storage state belongs to the cgroup attachment context and is not initialized in this file. The tests depend on verifier-side tracking of map type, local-storage helper flags, returned map-value bounds, pointer offsets, and unprivileged pointer-leak restrictions.

## Dependencies and Integration Points

This file depends on libbpf section handling, selftest verifier metadata, kernel cgroup/skb program loading, and the BPF helper prototype for local storage. It integrates with the verifier test harness in `tools/testing/selftests/bpf`, which compiles the naked inline assembly, loads each SEC program, and matches verifier logs against `__msg` expectations.

## Risks and Test Signals

Risks are diagnostic drift, map-type changes, and altered unprivileged policy. Strong test signals are one accepted normal cgroup-storage case, one accepted percpu case, and all invalid variants producing the expected errors: wrong map type, invalid map fd, map-value bounds violation, negative offset, non-zero flags, and unprivileged address leakage.
