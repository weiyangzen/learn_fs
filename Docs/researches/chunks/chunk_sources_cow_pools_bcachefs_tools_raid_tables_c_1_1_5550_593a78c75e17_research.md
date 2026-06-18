# Chunk Research: sources/cow-pools/bcachefs-tools/raid/tables.c lines 1-5550

## Scope

This report covers only `sources/cow-pools/bcachefs-tools/raid/tables.c` lines 1-5550 in learn_fs subset A. The chunk is the opening portion of a generated/static RAID finite-field table translation unit. It does not contain functions or branches; its behavioral role is to provide immutable lookup data consumed by the RAID parity and recovery code in the same `raid/` directory.

## APIs And Exported Data

- `raid_gfmul[256][256]` begins at line 17 as `const uint8_t __aligned(256) raid_gfmul[256][256]`.
- The declaration is paired with `extern const uint8_t raid_gfmul[256][256] __aligned(256);` in `raid/internal.h`, where it is also aliased as `gfmul`.
- Lines 1-5550 include the copyright/license header, `#include "internal.h"`, the `raid_gfmul` declaration, 162 complete rows of the multiplication table, and part of row `0xa2`.
- Rows completed in this chunk are the coefficient rows `0x00` through `0xa1`.
- Row `0xa2` starts at line 5527 and is incomplete at this chunk boundary; line 5550 reaches entries 176-183 of that row. The row and the `raid_gfmul` initializer continue in the next chunk.

Later declarations visible from symbol scans, but outside this chunk, include `raid_gfexp`, `raid_gfinv`, `raid_gfvandermonde`, `raid_gfcauchy`, `raid_gfcauchypshufb`, and `raid_gfmulpshufb`.

## Control Flow

There is no executable control flow in this chunk. The only runtime effect is static initialization by the C compiler/linker:

- `internal.h` is included so `uint8_t` and `__aligned(256)` are available.
- `raid_gfmul` is emitted as a 256-byte-aligned constant object.
- Consumers perform table lookups such as `gfmul[a][b]` rather than calculating Galois-field products at runtime.

The effective control flow lives in consumers, not in this file:

- `raid/gf.h` wraps table access through helpers such as `gf_mul()`, `gf_inv()`, `gf_exp()`, and `gf_gen()`.
- `raid/int.c` uses `gfmul[d0][gfgen[p][d]]` in the scalar parity generators for 3-6 parity blocks.
- `raid/check.c` and `raid/module.c` use `gfmul` for verification/reference parity generation.
- `raid/raid.c` selects the active generator table through `raid_gfgen`, choosing Vandermonde or Cauchy tables outside this chunk.

## State And Data Semantics

`raid_gfmul` is immutable global state. It is the full GF(2^8) multiplication matrix used by RAID parity math:

- First row is all zero, matching multiplication by zero.
- Second row is identity, matching multiplication by one.
- Subsequent rows contain precomputed products for each left-hand byte coefficient and right-hand byte value.
- The reduction pattern visible in rows such as `0x02` shows arithmetic over an 8-bit finite field rather than normal integer multiplication.

Because it is a dense `[256][256]` table, the complete object is 65,536 bytes before alignment/padding. This chunk contains about 41.5 KiB of the initializer data plus the surrounding declaration.

## Dependencies

Direct dependency:

- `raid/internal.h` supplies `uint8_t` through `<stdint.h>` and defines `__aligned(a)` as `__attribute__((aligned(a)))` when not already defined.

Important downstream users:

- `raid/gf.h` exposes inline finite-field lookup helpers over these tables.
- `raid/int.c` depends on `gfmul` for scalar RAID parity generation and recovery paths.
- `raid/check.c` and `raid/module.c` use `gfmul` for checking and reference generation.
- `raid/raid.c` chooses generator matrices used alongside `gfmul`.

Configuration dependency:

- Alignment is compiler-attribute based. The rest of `internal.h` contains architecture feature selection, but this chunk itself is architecture-neutral. Architecture-specific shuffle tables are declared later under `CONFIG_X86`, outside this chunk.

## Risks And Correctness Notes

- Table correctness is critical. A single wrong byte in `raid_gfmul` can silently corrupt generated parity or make recovery reconstruct bad data.
- The source is not self-verifying. Correctness depends on external generation, review, or `raid_selftest()` coverage elsewhere.
- Because line 5550 cuts through the `raid_gfmul` initializer, this chunk alone cannot validate the object’s closing braces, full row count, or subsequent table declarations.
- The 256-byte alignment is part of the ABI/performance contract expected by vectorized code and table consumers. Changing it can affect optimized RAID paths.
- The large static table trades binary size and cache footprint for fast deterministic lookup.

## Cross-Chunk References

- Next chunk must continue row `0xa2` from line 5551 and eventually complete `raid_gfmul[256][256]`.
- The `raid_gfmul` initializer ends before line 8725, where `raid_gfexp[256]` begins.
- Later chunks must cover the remaining finite-field tables and `CONFIG_X86` shuffle tables, especially `raid_gfcauchypshufb` and `raid_gfmulpshufb`, because optimized paths depend on those separate constants.