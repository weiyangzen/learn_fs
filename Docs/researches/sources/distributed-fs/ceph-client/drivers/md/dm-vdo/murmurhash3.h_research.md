# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/murmurhash3.h

## Purpose
`murmurhash3.h` declares the MurmurHash3 128-bit hashing function used by VDO/UDS code.

## Important APIs, Types, and Functions
It exposes `murmurhash3_128(const void *key, int len, u32 seed, void *out)`.

## Control Flow
No logic is defined here; callers pass key bytes, length, seed, and output storage to the implementation.

## State and Persistence Behavior
No state is declared. Hash output is deterministic and transient.

## Dependencies and Integration Points
The header includes Linux compiler and type definitions. It can be included by any module needing this non-cryptographic hash.

## Risks and Edge Cases
The output buffer size contract is implicit; callers must provide enough space for the 128-bit result. The hash is not security-sensitive.

## Test Signals
Compile coverage and known-vector tests for callers validate the declaration.
