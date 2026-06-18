# sources/distributed-fs/ceph-client/include/linux/prandom.h

Purpose: declares the fast pseudo-random state API for deterministic or per-CPU non-cryptographic random generation.

Important APIs and types: `struct rnd_state` stores four 32-bit state words. APIs include `prandom_u32_state()`, `prandom_bytes_state()`, `prandom_seed_full_state()`, `prandom_init_once()` for one-time per-CPU seeding, `__seed()` minimum-value adjustment, and `prandom_seed_state()` which expands a 64-bit seed into the four state words.

Control flow: users allocate state, seed it explicitly or once per CPU, then request u32 values or byte buffers. The seed helper derives a 32-bit value from the 64-bit seed and ensures each state component is above its minimum threshold.

State and persistence: mutable PRNG state is caller-owned or per-CPU and advances as values are generated. It is not cryptographic persistent entropy and should not be used for secrets.

Dependencies and integration points: depends on types, once helpers, percpu storage, and random seeding. Used by networking/tests/subsystems needing fast pseudo-randomness.

Risks and test signals: risks include cryptographic misuse, unseeded/reused deterministic state, per-CPU init races if not using `prandom_init_once()`, and assumptions about sequence stability. Test deterministic sequences after seeding, byte generation length, per-CPU one-time seeding, and static analysis for security-sensitive use.
