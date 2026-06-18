# sources/distributed-fs/coda/coda-src/venus/SpookyV2.h

## Purpose
This header declares and mostly defines the SpookyHash V2 class, including public one-shot hash APIs and inline mixing primitives.

## Important APIs, Types, and Functions
`Hash128`, `Hash64`, and `Hash32` are public one-shot hash functions. `Init`, `Update`, and `Final` provide incremental hashing. Inline helpers include `Rot64`, `Mix`, `EndPartial`, `End`, `ShortMix`, and `ShortEnd`. Private constants define twelve 64-bit state lanes, 96-byte blocks, a 192-byte short-buffer threshold, and the `0xdeadbeefdeadbeef` seed constant.

## Control Flow
Most mixing logic is inline in the header for performance. Public static wrappers seed and call `Hash128`, while streaming callers initialize state, feed fragments, and finalize without mutating the state further.

## State and Persistence Behavior
Instances store transient buffered input, hash state, total length, and remainder length. No persistent state is declared, but hash stability matters wherever output is stored or used as a wire identity.

## Dependencies and Integration Points
It provides portable integer typedefs for MSVC and standard `<stdint.h>` builds. `9pfs.cc` depends on `Hash64`.

## Risks and Test Signals
Risks are duplicate type definitions, architecture-dependent output on big endian systems, and the absence of include guards. Tests should compile on target compilers and validate deterministic vectors for 32-, 64-, and 128-bit outputs.
