# sources/distributed-fs/ceph-client/include/crypto/gf128hash.h

Purpose: GHASH and POLYVAL finite-field hashing interface over GF(2^128).

Important APIs/types/functions: `POLYVAL_*` constants, `struct polyval_elem`, `struct ghash_key`, `struct polyval_key`, `struct ghash_ctx`, `struct polyval_ctx`, key preparation functions, init/import/export helpers, update/final functions, and one-shot `ghash`/`polyval`.

Control flow: callers prepare a key, initialize a context pointing to the key, feed arbitrary-length data, and finalize with automatic zero-padding of the last partial block. POLYVAL supports block-aligned accumulator export/import.

State and persistence: key structs store raw/precomputed hash keys with architecture-specific layouts. Contexts store key pointer, accumulator, and partial byte count. Contexts are zeroized on finalization by implementation.

Dependencies and integration points: depends on GHASH constants and string/types. Used by GCM, AES-GCM-SIV/POLYVAL-style constructions, and architecture-optimized GF hashing.

Risks: key lifetime must outlive contexts. GHASH and POLYVAL use different byte/bit conventions; mixing formats breaks authentication. Architecture-specific key layouts must match assembly implementations.

Test signals: GHASH/POLYVAL vectors, partial-block padding tests, export/import round trips, arch/generic comparison, and GCM integration tests.
