# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/hashfn.h

## Purpose
Declares non-cryptographic hash functions used by GlusterFS for data distribution, lookup tables, or message/string hashing.

## APIs, Types, and Functions
`SuperFastHash(const char *data, int32_t len)` computes a 32-bit hash for a byte string. `gf_dm_hashfn(const char *msg, int len)` computes another 32-bit hash used by GlusterFS distribution/mapping code.

## Control Flow, State, and Persistence
Both APIs are pure hash computations with no persistent state. Their output can affect persistent placement or lookup behavior if used for layout decisions.

## Dependencies and Integration
Depends on integer and size types. Integrated with hash tables and distributed layout code that needs stable, fast hashes.

## Risks and Test Signals
Risks include hash instability if algorithms change, collision behavior under adversarial names, signed-length misuse, and non-cryptographic use in security-sensitive paths. Test signals include known-vector tests, distribution/collision benchmarks, DHT placement compatibility tests, and checks for negative/zero length handling.
