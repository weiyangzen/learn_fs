# sources/distributed-fs/lizardfs/src/common/hashfn.h

Purpose: provides fast non-cryptographic hash helpers, checksum composition, byte-array hashing, and tuple hashing.

Important APIs/types/functions: `hash32`, `hash32mult`, `hash6432`, `hash64`; template `hash<T>` with primitive specializations; `hashCombineRaw`, variadic `hashCombine`; `ByteArray` and its specialization; `addToChecksum`, `removeFromChecksum`; `AlmostGenericTupleHash`.

Control flow: primitive hashes use Thomas Wang-style avalanche mixes. `hashCombine` recursively hashes values into a seed. `ByteArray` iterates bytes and combines each byte hash. Tuple hashing expands indexes via `make_index_sequence`.

State and persistence: no state; checksum helpers mutate caller-provided integers.

Dependencies and integration: depends on `integer_sequence.h`, tuples, and integer types. Used where deterministic internal hash/checksum values are needed, not for security.

Risks: not cryptographic. The generic `hash<T>` is declared but undefined to force unsupported-type link errors, which can be less clear than compile-time static assertions. `addToChecksum`/`removeFromChecksum` are XOR symmetric and order-insensitive, suitable only for specific checksum semantics.

Test signals: `hashfn_unittest.cc` checks string byte hashing distinctions, combine order sensitivity, primitive uniqueness over a million ints, and variadic combine equivalence.
