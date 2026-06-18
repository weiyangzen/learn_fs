# sources/distributed-fs/ceph-client/lib/crypto/powerpc/ghashp8-ppc.pl

## Purpose
Generates POWER8 GHASH assembly from CRYPTOGAMS perlasm. The generated code provides vector polynomial multiplication helpers for GCM/GHASH.

## Important APIs, Types, and Functions
Emits `.gcm_init_p8`, `.gcm_gmult_p8`, and `.gcm_ghash_p8`. The script configures word size and stack instructions from `$flavour`, locates `ppc-xlate.pl`, and uses vector registers for accumulator, input, hash table entries, reduction constants, and endian masks.

## Control Flow
The script validates the target flavour, opens a pipe to the PowerPC translator, emits assembly text, and removes or comments endian-conditional markers. Generated `gcm_init_p8` loads H, endian-adjusts on LE, twists H into the form expected by the reduction algorithm, and stores a four-entry table. `gcm_gmult_p8` loads Xi and table entries, uses `vpmsumd` to compute carryless products, reduces in two phases, endian-adjusts, and stores Xi. `gcm_ghash_p8` loops over 16-byte input blocks, xors each into Xi, multiplies/reduces, and writes the final accumulator.

## State and Persistence
The generator writes assembly and has no runtime state. Generated routines modify caller-provided table or accumulator buffers and preserve VRSAVE. No global runtime state is used.

## Dependencies and Integration Points
Depends on `ppc-xlate.pl`, PowerISA 2.07 vector instructions, and the C declarations in `gf128hash.h`. The C wrapper is responsible for enabling VSX and converting between GHASH and POLYVAL representations.

## Risks
The `le?`/`be?` marker rewriting makes endian behavior easy to break. GHASH reduction constants and table layout must match the C fallback in `gf128hash.h`. Any translator path change can alter emitted ABI details.

## Test Signals
Regenerate output and compare to checked-in generated assembly when applicable. GHASH known-answer tests and C-fallback table equivalence tests should catch most arithmetic and endian regressions.
