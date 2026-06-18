# sources/distributed-fs/beegfs/client_module/source/common/toolkit/vector/UInt8Vec.h

## Purpose
Defines an indexed append-only vector for `uint8_t` values while keeping list-compatible storage semantics.

## Important APIs and control flow
`init` allocates an initial four-byte array. `append` appends the byte to the underlying `UInt8List`, grows the array by doubling when needed, and writes the value at the last index. `at`, `length`, `clear`, and `uninit` provide access and cleanup.

## State, dependencies, integration
State is a `UInt8List`, byte array, and array capacity. Serialization code reuses UInt8 list wire format for vectors.

## Risks and test signals
Unchecked allocation and stale array contents after clear are the main risks. Tests should cover byte min/max, growth, clear/reuse, and deserialization into a vector.
