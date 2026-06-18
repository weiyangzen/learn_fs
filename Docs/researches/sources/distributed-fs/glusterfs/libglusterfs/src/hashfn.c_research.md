# sources/distributed-fs/glusterfs/libglusterfs/src/hashfn.c

## Purpose
`hashfn.c` provides two non-cryptographic 32-bit hash implementations used by core GlusterFS data structures and path/key sharding logic: Paul Hsieh's `SuperFastHash()` and Gluster's Davies-Meyer-style `gf_dm_hashfn()`. The code is deliberately small and dependency-light so it can be used from low-level containers such as `rbthash.c` without bringing in translator state.

## Important APIs, Types, And Functions
The public entry points are `uint32_t SuperFastHash(const char *data, int32_t len)` and `uint32_t gf_dm_hashfn(const char *msg, int len)`. `SuperFastHash()` consumes bytes in little-endian 16-bit chunks via `get16bits(d)` and applies tail handling for 1, 2, or 3 remaining bytes before a final avalanche. It returns `1` for `NULL` data or `len <= 1`, which avoids a zero or trivial hash result in callers.

`gf_dm_hashfn()` initializes two fixed 32-bit chaining words, treats the input as little-endian 32-bit words, processes full 16-byte quads through the internal `dm_round(DM_PARTROUNDS, ...)`, pads a final 4-word block with `__pad(len)`, then applies a stronger final `dm_round(DM_FULLROUNDS, ...)`. `__pad()` repeats the byte-length across a 32-bit word. `dm_round()` is a TEA-like mixing primitive using `DM_DELTA`.

## Control Flow
`SuperFastHash()` validates input, reduces `len` into a count of four-byte groups plus a remainder, loops over 16-bit pairs, processes the remainder with a `switch`, then avalanches the accumulated state. `gf_dm_hashfn()` casts the message to `uint32_t *`, computes full byte/word/quad counts, loops over complete quads, fills the last four-word array either from the remaining words or from pad plus remaining bytes, and returns `h0 ^ h1`.

## State And Persistence
The file keeps no process state and performs no allocation or I/O. Hash determinism depends on explicit `le16toh()` and `le32toh()` conversions, so stored keys should be stable across endian variants for aligned input. There is no persisted format in this file, but callers may persist hash-derived placement decisions.

## Dependencies And Integration Points
Dependencies are limited to `<stdint.h>`, `<stdlib.h>`, and platform endian headers. `gf_dm_hashfn()` is a suitable `rbt_hasher_t` style function for keyed tables such as red-black tree hash buckets. Other GlusterFS modules can call these functions without a `glusterfs_ctx_t` or `xlator_t`.

## Risks
Both functions are non-cryptographic and should not be used for attacker-controlled hash tables without collision considerations. `gf_dm_hashfn()` casts `char *` to `uint32_t *`; on strict-alignment platforms this may fault if callers pass unaligned buffers. `SuperFastHash()` similarly dereferences `uint16_t *`. Neither function bounds-checks negative `len` beyond `len <= 1`; callers must pass sane lengths. `SuperFastHash()` returns `1` for all 0- or 1-byte inputs, so it intentionally sacrifices uniqueness for tiny keys.

## Test Signals
Useful tests include stable known-vector hashes on little- and big-endian systems, unaligned input buffers under sanitizers or strict-alignment targets, tail lengths 0 through 3, and caller-level distribution tests over real dentry, GFID, and option keys. Collision behavior should be assessed where hash results feed bucket selection.
