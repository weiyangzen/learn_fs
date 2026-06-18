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