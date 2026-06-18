# sources/compression/lz4/lib/xxhash.h

## Purpose
`xxhash.h` is the public declaration and optional inline implementation gateway for xxHash 0.6.5. It documents the algorithm, exposes one-shot and streaming APIs, and provides static-linking-only state definitions.

## Important APIs, Types, And Functions
The header defines `XXH_errorcode`, `XXH32_hash_t`, `XXH64_hash_t`, `XXH32_canonical_t`, `XXH64_canonical_t`, opaque `XXH32_state_t` and `XXH64_state_t`, version macros, and all `XXH32*`/`XXH64*` public functions. `XXH_INLINE_ALL` and `XXH_PRIVATE_API` convert definitions to static inline mode by including `xxhash.c`.

## Control Flow
There is no runtime control flow, but preprocessor flow is important. `XXH_NAMESPACE` rewrites public names, `XXH_NO_LONG_LONG` removes 64-bit APIs, and `XXH_STATIC_LINKING_ONLY` reveals state structs for stack allocation or embedding.

## State, Persistence, And Dependencies
The static section defines the exact state fields used by the implementation, including accumulators, temporary buffers, and reserved fields that should never be accessed. The header depends only on `stddef.h` for the normal public surface and `stdint.h` when static definitions use fixed-width types.

## Integration Points
This header is included by `xxhash.c`, fuzz helpers, and benchmark code. It is also safe for consumers that want namespaced or private inline copies to avoid public symbol conflicts.

## Risks
The static state layout is explicitly not stable API. Including with `XXH_INLINE_ALL` pulls the implementation into each translation unit, which is useful for speed but can cause duplicate-code bloat. Namespace macros require all users in a linkage unit to agree on symbol naming.

## Test Signals
Compile coverage should include normal dynamic declarations, namespaced declarations, `XXH_INLINE_ALL`, `XXH_NO_LONG_LONG`, C++ inclusion, canonical type sizes, and static state allocation.
