# sources/distributed-fs/ceph-client/kernel/bpf/bloom_filter.c

Purpose: implements keyless BPF Bloom filter maps using push/peek operations and a power-of-two bitset.

Important APIs/types/functions: `struct bpf_bloom_filter` stores the embedded map, bitset mask, hash seed, hash count, and flexible bitset. `hash` uses `jhash`/`jhash2`. Map ops are `bloom_map_alloc_check`, `bloom_map_alloc`, `bloom_map_push_elem`, `bloom_map_peek_elem`, `bloom_map_free`, `bloom_map_check_btf`, and `bloom_map_mem_usage`.

Control flow: creation rejects keys, zero values, unsupported flags, and invalid `map_extra`; `map_extra` low four bits choose hash count, defaulting to five. It sizes the bitset from expected entries and hash count, approximating optimal Bloom filter sizing, rounds to a power of two, and optionally randomizes the seed. Push sets all hash bits for a value. Peek returns success only if all corresponding bits are set. Pop, delete, get-next-key, ordinary lookup, and ordinary update are unsupported.

State and persistence: bitset state persists for map lifetime and only grows more set bits; there is no deletion. Seed persists per map unless `BPF_F_ZERO_SEED` is requested.

Dependencies and integration: integrates with BPF map core, BTF map typing, `jhash`, random seed generation, bitmap bit operations, and BPF queue/stack-like push/peek map callbacks.

Risks: false positives are expected by design; false negatives indicate bugs. Large `max_entries` and hash-count calculations must avoid overflow. Concurrent `set_bit`/`test_bit` use is lockless, so tests should consider atomic bitops semantics. Keyless BTF validation must reject non-void keys.

Test signals: BPF map selftests for Bloom filter creation flags, zero seed determinism, push/peek behavior, expected false-positive envelope, unsupported operations, and BTF key validation.
