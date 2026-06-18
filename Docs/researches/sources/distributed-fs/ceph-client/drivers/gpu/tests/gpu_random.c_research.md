# sources/distributed-fs/ceph-client/drivers/gpu/tests/gpu_random.c

Purpose: small randomization helper library for GPU tests.

Important APIs and functions: `gpu_prandom_u32_max_state()` scales `prandom_u32_state()` into `[0, ep_ro)` using high 32 bits of a 64-bit product. `gpu_random_reorder()` shuffles an order array. `gpu_random_order()` allocates and initializes an index array before shuffling it. All three are exported symbols.

Control flow: `gpu_random_order()` allocates with `kmalloc_array`, fills `0..count-1`, calls `gpu_random_reorder()`, and returns the array. `gpu_random_reorder()` performs repeated swaps using a random index.

State and persistence: no global state. Callers own the `rnd_state` and allocated order array.

Dependencies and integration: depends on kernel random, slab, bitops, and swap helpers. Used by `gpu_buddy_test.c` randomized range-bias tests.

Risks: the shuffle is not Fisher-Yates because each iteration chooses from the whole range; that is acceptable for stress ordering but not uniform permutation generation. `count == 0` behavior depends on allocator and loop behavior at callers.

Test signals: indirect through GPU KUnit randomized tests and reproducibility via seeded `rnd_state`.
