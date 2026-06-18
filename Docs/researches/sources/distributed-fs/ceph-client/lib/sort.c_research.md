# sources/distributed-fs/ceph-client/lib/sort.c

## Purpose
Implements the kernel generic in-place sort helpers. The algorithm is a non-recursive heapsort chosen for bounded O(n log n) worst-case behavior and low stack usage, with optimized swap paths for aligned element sizes.

## APIs, Control Flow, and State
Exports `sort_r()`, `sort_r_nonatomic()`, `sort()`, and `sort_nonatomic()`. `sort_r*()` accepts comparator and swap functions with a private pointer; `sort*()` wraps legacy comparators and swaps through `struct wrapper`. `__sort_r()` chooses a swap implementation when the caller does not provide one: 64-bit word swaps, 32-bit word swaps, or byte swaps based on element size and base alignment. The main loop first builds a heap using byte offsets, then repeatedly extracts the largest elements using a bottom-up sift that reduces comparator calls. The `_nonatomic` variants call `cond_resched()` inside the loop.

No persistent state is stored. The caller-provided array is mutated in place.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/sort.h`, type definitions, export support, and scheduler rescheduling for nonatomic variants. Integration points are any kernel subsystem sorting arrays without allocating temporary memory. Risks include invalid comparators that violate antisymmetry or transitivity, custom swap functions that do not preserve auxiliary state, zero element size, integer overflow in `num * size`, and using the atomic variant for very large arrays in sleepable contexts. Test signals include lib/sort selftests, randomized ordering tests, adversarial comparator tests, custom swap coverage, alignment-sensitive tests, and latency checks with `sort_r_nonatomic()`.
