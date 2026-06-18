# sources/distributed-fs/lizardfs/src/common/hashfn_unittest.cc

Purpose: tests hash helpers and combination semantics.

Important APIs/types/functions: tests `hash(ByteArray)`, `hash<T>` primitive specializations, `hashCombineRaw`, and variadic `hashCombine`.

Control flow: string test checks different byte arrays produce different hashes. Combine test checks different seeds and argument orders produce different results. Primitive test creates one million integer hashes and checks uniqueness, then compares hashes across primitive types. Variadic test compares repeated one-by-one combine with one variadic call.

State and persistence: test-only vectors and seeds.

Dependencies and integration: includes `hashfn.h`, `gtest`, and `algorithm`.

Risks: uniqueness over a finite range is a useful smoke test but not a formal distribution test. The second million-hash loop duplicates `int` input rather than truly using 32-bit variable diversity.

Test signals: good regression coverage for deterministic hashing and combine behavior.
