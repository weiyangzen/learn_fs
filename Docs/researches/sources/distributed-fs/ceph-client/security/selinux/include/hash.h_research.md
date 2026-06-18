## sources/distributed-fs/ceph-client/security/selinux/include/hash.h

### Purpose
`hash.h` supplies a small inline hash helper for SELinux access-vector style keys. It is based on MurmurHash3 mixing and returns a bucket index masked by the caller.

### Important APIs, types, and functions
The only API is `static inline u32 av_hash(u32 key1, u32 key2, u32 key3, u32 mask)`. It mixes three 32-bit keys with constants `c1`, `c2`, rotations, final avalanche steps, and returns `hash & mask`.

### Control flow
The function initializes `hash` to zero, applies the `mix` macro to each input, performs Murmur-style finalization, and masks the result. The caller is expected to pass a mask appropriate for a power-of-two-sized hash table.

### State and persistence
The function is stateless and deterministic. There is no allocation or persistence.

### Dependencies and integration points
It depends only on SELinux/kernel availability of `u32`. It is suitable for AVC or policy data structures that need stable in-kernel hashing.

### Risks
Passing a non-power-of-two-minus-one mask gives a biased but still bounded result. Because the seed is fixed at zero, this is not a hash-flooding defense for untrusted high-volume user keys.

### Test signals
Unit-style tests can verify deterministic output, bucket bounds for expected masks, and collision distribution over representative SID/class/permission triples.
