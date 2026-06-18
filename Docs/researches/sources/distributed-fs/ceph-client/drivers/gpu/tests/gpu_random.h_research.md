# sources/distributed-fs/ceph-client/drivers/gpu/tests/gpu_random.h

Purpose: declarations and convenience macros for GPU test pseudo-random helpers.

Important APIs and macros: `GPU_RND_STATE_INITIALIZER(seed__)` creates and seeds a `struct rnd_state`; `GPU_RND_STATE(name__, seed__)` declares a seeded state variable. Function declarations cover `gpu_random_order`, `gpu_random_reorder`, and `gpu_prandom_u32_max_state`.

Control flow: macro expansion seeds local PRNG state before test code calls helper functions.

State and persistence: state is caller-owned `struct rnd_state`; there is no global state.

Dependencies and integration: includes `linux/prandom.h` and pairs with `gpu_random.c`. Used by GPU KUnit tests requiring reproducible randomized orders.

Risks: macros create block-expression values and are kernel/GNU C specific. Callers must preserve and log seeds when debugging randomized failures.

Test signals: indirect through KUnit tests that use `GPU_RND_STATE`.
