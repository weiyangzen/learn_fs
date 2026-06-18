# File Research: sources/cow-pools/bcachefs-tools/raid/tables.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-5550, source bytes 262115, report `Docs/researches/chunks/chunk_sources_cow_pools_bcachefs_tools_raid_tables_c_1_1_5550_593a78c75e17_research.md`
- chunk 2: lines 5551-10950, source bytes 262044, report `Docs/researches/chunks/chunk_sources_cow_pools_bcachefs_tools_raid_tables_c_2_5551_10950_5457c1428a40_research.md`
- chunk 3: lines 10951-14696, source bytes 184636, report `Docs/researches/chunks/chunk_sources_cow_pools_bcachefs_tools_raid_tables_c_3_10951_14696_0327d36dcc0b_research.md`

## Chunk Research

### Chunk 1: lines 1-5550

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

### Chunk 2: lines 5551-10950

# Chunk Research: sources/cow-pools/bcachefs-tools/raid/tables.c lines 5551-10950

## Scope

This chunk is part of subset A (`Docs/research_subset_a.md`) under `sources/cow-pools/bcachefs-tools`. I read the requested range completely (`5400` lines, `262044` bytes) and used adjacent context only to identify array declarations and callers. The file is a generated/static RAID Galois-field table source, not ordinary control-flow-heavy C.

## APIs And Exported Data

The chunk contributes exported, 256-byte-aligned `const uint8_t` table symbols declared in `raid/internal.h`:

- `raid_gfmul[256][256]`: tail of the GF(2^8) multiplication table. The table begins before this chunk at line 17 and closes at line 8723. Line 5551 is inside row index 162 of 256, so rows 162-255 are visible here.
- `raid_gfexp[256]`: complete in this chunk, lines 8725-8759. Exponent/power table for `2^a`.
- `raid_gfinv[256]`: complete in this chunk, lines 8761-8796. Element zero is documented as non-significant.
- `raid_gfvandermonde[3][256]`: complete in this chunk, lines 8806-8910. Valid for up to 3 parity disks with 251 data disks.
- `raid_gfcauchy[6][256]`: complete in this chunk, lines 8923-9129. Valid for up to 6 parity disks with 251 data disks.
- `raid_gfcauchypshufb[251][4][2][16]`: begins under `#ifdef CONFIG_X86`, lines 9131-10950, and continues into the next chunk. The visible prefix covers disk entries 0 through 100 of 251.

## Control Flow

There is no runtime function body in this chunk except the preprocessor gate for x86 PSHUFB data. Runtime behavior is indirect:

- `gf.h` inline helpers read `gfmul`, `gfinv`, `gfexp`, and active `gfgen`.
- `raid.c::raid_mode()` selects `raid_gfgen = gfvandermonde` for `RAID_MODE_VANDERMONDE`, otherwise `raid_gfgen = gfcauchy`.
- Scalar paths in `int.c`, `check.c`, and `module.c` consume `gfmul` and `gfgen`.
- SIMD paths in `x86.c` consume `gfgenpshufb` with `movdqa`/`vbroadcasti128` and `pshufb`/`vpshufb`.

## State And Invariants

All objects are immutable static data. There is no heap state, locking, mutation, or initialization side effect in this chunk.

Key invariants:

- Tables use `__aligned(256)`, which matters for SIMD loads and table layout assumptions.
- GF arithmetic is byte-sized: 256 possible field values.
- `RAID_PARITY_MAX == 6` and `RAID_DATA_MAX == 251`, matching `raid_gfcauchy[6][256]` and `raid_gfcauchypshufb[251][4][2][16]`.
- Vandermonde is a 3-row generator matrix; Cauchy is a 6-row generator matrix.
- `raid_gfcauchypshufb` encodes `[DISK][PARITY - 2][low/high-nibble-table][16]`.

## Dependencies And Risks

Compile-time dependencies are `internal.h`, `uint8_t`, `__aligned`, and `CONFIG_X86`. Runtime use depends on `raid_init()`/`raid_mode()` setting `raid_gfgen` before `A(p,d)` lookups.

Risks:

- Manual edits are high risk because one byte error silently corrupts parity or recovery.
- This chunk starts inside `raid_gfmul` and ends inside `raid_gfcauchypshufb`; adjacent chunk reports are required for whole-symbol review.
- `raid_gfcauchypshufb` is conditionally compiled for x86 while declared unconditionally in `internal.h`; non-x86 code must not reference it.
- `raid_gfinv[0]` is dummy data; correctness relies on callers avoiding inverse-of-zero.
- Changing parity/data limits or matrix semantics requires regenerating and revalidating all dependent tables.

## Cross-Chunk References

- Previous chunk: contains `raid_gfmul` declaration and rows 0-161.
- This chunk: completes `raid_gfmul`; fully defines `raid_gfexp`, `raid_gfinv`, `raid_gfvandermonde`, and `raid_gfcauchy`; starts `raid_gfcauchypshufb`.
- Next chunk: continues and closes `raid_gfcauchypshufb`, then later defines `raid_gfmulpshufb`.
- Consumer files: `raid/internal.h`, `raid/gf.h`, `raid/raid.c`, `raid/int.c`, `raid/check.c`, `raid/module.c`, and `raid/x86.c`.

### Chunk 3: lines 10951-14696

# Chunk Research: sources/cow-pools/bcachefs-tools/raid/tables.c lines 10951-14696

## Scope

This report covers only `sources/cow-pools/bcachefs-tools/raid/tables.c` lines 10951-14696 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context only to identify the enclosing declarations, preprocessor boundaries, and consumers. The chunk is generated/static RAID finite-field lookup data, not executable C logic.

## APIs And Exported Data

This chunk contributes x86-only, 256-byte-aligned `const uint8_t` table objects declared in `raid/internal.h`:

- `raid_gfcauchypshufb[251][4][2][16]`: the chunk starts inside this initializer at line 10951 and carries it through its closing brace at line 13658. Adjacent context identifies the declaration at line 9138 under `#ifdef CONFIG_X86`.
- `raid_gfmulpshufb[256][2][16]`: complete in this chunk, declared at line 13668 and closed at line 14694, also under `#ifdef CONFIG_X86`.

`internal.h` aliases these symbols for local RAID code as `gfgenpshufb` and `gfmulpshufb`.

## Control Flow

There are no functions, branches, loops, heap operations, or runtime initialization side effects in this chunk. The only control-like construct is preprocessor gating around both x86-only tables.

Runtime behavior is indirect through consumers in `raid/x86.c`: Cauchy parity generation uses `gfgenpshufb` with `pshufb`/`vpshufb`; recovery paths use `gfmulpshufb` for arbitrary GF multipliers from inverted recovery matrices.

## State And Dependencies

All data is immutable global state emitted by the compiler/linker. Each PSHUFB leaf table has 16 bytes, one result per nibble value; low/high nibble products are shuffled separately and XORed.

Direct dependencies are `internal.h`, `uint8_t`, `__aligned(256)`, and `CONFIG_X86`. Downstream dependencies include `raid/internal.h`, `raid/x86.c`, and the Cauchy matrix design described in `raid/raid.c`.

## Risks And Cross-Chunk References

A one-byte error in either table can silently corrupt parity or recovery. The shapes must stay synchronized with `RAID_DATA_MAX == 251`, `RAID_PARITY_MAX == 6`, `raid_gfcauchy`, and scalar `raid_gfmul` semantics.

Previous chunk begins `raid_gfcauchypshufb`; this chunk completes it and fully defines `raid_gfmulpshufb`. There is no next chunk for this file after line 14696.
