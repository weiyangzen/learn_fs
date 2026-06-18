# sources/distributed-fs/ceph-client/lib/crypto/arm64/poly1305-armv8.pl

## Purpose
Perl perlasm generator for the ARMv8 Poly1305 block, emit, and optional NEON block routines used by the kernel crypto library. In kernel builds it renames the generated public labels to `poly1305_block_init`, `poly1305_blocks_arm64`, and `poly1305_blocks_neon`.

## Important APIs, Types, And Functions
Generated symbols are `poly1305_init`, `poly1305_blocks`, `poly1305_emit`, and `poly1305_blocks_neon`; kernel preprocessor aliases expose the first two as arm64 crypto-lib ABI symbols. Internal generated helpers include `poly1305_mult` and `poly1305_splat` for multiplication and key-power table setup.

## Control Flow
`poly1305_init` zeros the accumulator, clamps and stores `r`, and seeds an impossible key-power marker. `poly1305_blocks` handles 16-byte multiples in scalar base-2^64 form, converts from base-2^26 when needed, accumulates message limbs plus `padbit`, multiplies by `r`, and partially reduces. `poly1305_emit` canonicalizes the accumulator, adds the nonce, and writes the tag. `poly1305_blocks_neon` falls back for short input, otherwise saves ABI registers, converts or initializes base-2^26 state, precomputes powers through `r^4`, processes multi-block vectors, and stores the base-2^26 accumulator marker.

## State, Persistence, And Dependencies
All persistent state is in the caller's `poly1305_block_state` memory: accumulator limbs, clamped key limbs, cached powers, and a radix marker. The script depends on `arm-xlate.pl` when a flavor is requested and on generated AArch64/NEON instructions at build time. No filesystem or runtime persistence exists beyond the generated assembly artifact.

## Integration Points
Included through the arm64 Poly1305 arch header and ultimately used by generic Poly1305 and ChaCha20-Poly1305 code. The kernel wrapper decides between scalar and NEON entry points with ASIMD feature and SIMD-context checks.

## Risks
Risk concentrates in ABI offsets, endian handling, radix conversion, short-input fallback, and lazy key-power caching. Any mismatch between generated labels and C prototypes breaks kernel linkage. NEON state handling must remain inside kernel SIMD critical sections supplied by the caller.

## Test Signals
Known-answer Poly1305 vectors, mixed short and long messages, final partial-block callers that vary `padbit`, big-endian assembly builds, and stress that alternates scalar and NEON paths should all produce identical tags.
