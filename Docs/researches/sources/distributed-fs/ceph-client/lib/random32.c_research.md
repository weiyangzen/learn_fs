## sources/distributed-fs/ceph-client/lib/random32.c

Purpose: implements the kernel pseudo-random `prandom` Tausworthe generator for non-cryptographic uses, plus optional self-tests under `CONFIG_RANDOM32_SELFTEST`.

Important APIs/functions: `prandom_u32_state()` advances a caller-provided `struct rnd_state` using four LFSR/Tausworthe components and returns their XOR. `prandom_bytes_state()` fills byte buffers from repeated 32-bit outputs. `prandom_seed_full_state()` seeds per-CPU states from `get_random_bytes()` and warms each state. Self-test helpers include `prandom_state_selftest_seed()` and `prandom_state_selftest()`.

Control flow: state transitions use the `TAUSWORTHE` macro with fixed masks/shifts and seed constraints documented in comments. Byte generation writes full unaligned 32-bit words, then any remaining bytes from a final value. Full-state seeding iterates possible CPUs, derives four constrained seeds with `__seed()`, and calls `prandom_warmup()` ten times.

State and persistence: state lives in caller-supplied `struct rnd_state` or per-CPU storage passed to seeding. The file itself keeps only static test vectors when self-test is enabled.

Dependencies/integration: exports `prandom_u32_state`, `prandom_bytes_state`, and `prandom_seed_full_state`. Depends on random seeding, percpu iteration, jiffies/scheduler infrastructure for tests, and unaligned stores.

Risks/test signals: not cryptographic; callers needing entropy must use `get_random_*`. Bad seeding can violate generator constraints. Built-in self-tests compare boundary and GSL-derived vectors and report pass/fail at init.
