# sources/distributed-fs/ceph-client/kernel/bpf/cpumask.c

## Purpose
`cpumask.c` exposes refcounted cpumask objects and cpumask operations to BPF programs as kfuncs. It lets tracing, struct_ops, and syscall BPF programs create mutable masks, acquire and release references, query and mutate bits, combine masks, select CPUs, count bits, and populate a cpumask from BPF memory.

## Important APIs, types, and functions
The core type is `struct bpf_cpumask`, which embeds `cpumask_t` as its first field and a `refcount_t`. Allocation uses the global `bpf_cpumask_ma` BPF memory allocator. Lifetime kfuncs are `bpf_cpumask_create()`, `bpf_cpumask_acquire()`, `bpf_cpumask_release()`, and `bpf_cpumask_release_dtor()`. Operation kfuncs include first/first_zero/first_and, set/clear/test/test_and_set/test_and_clear, setall/clear, and/or/xor/copy, equal/intersects/subset/empty/full, any_distribute/any_and_distribute, weight, and `bpf_cpumask_populate()`. Registration is done by `cpumask_kfunc_init()`.

## Control flow
`bpf_cpumask_create()` allocates from the BPF memory cache, zeroes the object, verifies first-field layout for casting to `struct cpumask`, and starts refcount at one. `acquire()` increments the refcount and returns the same trusted pointer. `release()` decrements and frees through the BPF allocator's RCU-safe free path on the final reference; the destructor calls the same release function for kptr map ownership. Bit operations validate CPU indices against `nr_cpu_ids` where they target a single CPU, then delegate to kernel cpumask helpers. Registration initializes the allocator, registers the kfunc set for tracing, struct_ops, and syscall program types, and registers the destructor BTF mapping.

## State and persistence
Each `bpf_cpumask` persists while references exist, including references held as BPF kptrs in maps. Final release is RCU-safe through `bpf_mem_cache_free_rcu()`. The kfunc registration and allocator persist for the life of the kernel/module. Mask contents are mutable runtime state only and are not stored outside BPF-managed objects unless a program copies them elsewhere.

## Dependencies and integration points
The file depends on kernel cpumask APIs, BPF kfunc and BTF ID registration, BPF memory allocator, refcounting, CFI annotations for the destructor, verifier acquire/release semantics (`KF_ACQUIRE`, `KF_RELEASE`, `KF_RET_NULL`, `KF_RCU`), and kptr destructor infrastructure. The first-field layout enables passing a `struct bpf_cpumask *` to helpers expecting `struct cpumask *`.

## Risks and test signals
Risks include refcount leaks or double releases through kptr movement, verifier trust mistakes for mutable vs const mask pointers, CPU bounds differences between `nr_cpu_ids`, `nr_cpumask_bits`, and possible CPUs, alignment and size checks in `bpf_cpumask_populate()`, allocator initialization failures stopping kfunc registration, and race expectations when multiple BPF contexts mutate the same mask. Test signals include acquire/release lifetime tests with map kptrs, invalid CPU operations, all boolean cpumask operations, distribution helpers on empty and non-empty masks, populate with too-small or unaligned memory, registration for the three program types, destructor invocation on map cleanup, and RCU use-after-free tests.
