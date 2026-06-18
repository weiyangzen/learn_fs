# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_rand.h

Purpose: user-space helper for generating semi-random 64-bit values with edge-case bit patterns for BPF tests.

Important APIs and functions: `bpf_rand_mask()`, generated `bpf_rand_u8/u16/.../u64(shift)`, `bpf_semi_rand_init()`, and `bpf_semi_rand_get()`.

Control flow: initialization seeds `rand()` with current time. `bpf_semi_rand_get()` picks among 39 cases combining fixed masks, random low/high fields, shifts, all-zero/all-one, and sign-bit-heavy values.

State and persistence: uses libc global PRNG state seeded by `srand`.

Dependencies and integration points: includes stdint/stdlib/time; used by tests wanting varied immediate/register values.

Risks: not deterministic unless caller controls seed separately; uses weak libc `rand()` quality; some shift arguments are random modulo 64 and should remain within range.

Test signals: fuzz-like tests should see a mix of boundary and random values; reproducibility may require overriding seed behavior.
