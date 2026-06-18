# Chunk Research: sources/local-fs/btrfs-progs/kernel-lib/tables.c lines 5551-10362

## Scope

This report covers only `sources/local-fs/btrfs-progs/kernel-lib/tables.c` lines 5551-10362 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context to identify the enclosing generated declarations, header exports, generator, and RAID56 recovery consumers. The chunk is immutable RAID6 finite-field lookup data, not hand-written executable logic.

## APIs And Exported Data

This chunk contributes the tail of the file's public RAID6 table API declared in `kernel-lib/raid56.h`:

- `raid6_gfmul[256][256]`: the chunk begins inside this 256-byte-aligned scalar GF(2^8) multiplication table and carries it to its closing brace at line 8710. The declaration is in the previous chunk at lines 3-4.
- `raid6_vgfmul[256][32]`: complete in this chunk, declared at lines 8712-8713 and closed at line 10251. Each row stores nibble-oriented products for vectorized/table-assisted multiplication: products for `0..15`, then products for `(0..15) << 4`.
- `raid6_gfexp[256]`: complete in this chunk, declared at lines 10253-10254 and closed at line 10288. It is the power-of-two exponent table used for RAID6 Q coefficient math; entry 255 is the generated sentinel `0x00`.
- `raid6_gfinv[256]`: complete in this chunk, declared at lines 10290-10291 and closed at line 10325. It maps each byte to its multiplicative inverse in the RAID6 field, with zero mapped to zero.
- `raid6_gfexi[256]`: complete in this chunk, declared at lines 10327-10328 and closed at line 10362. It stores `inv(2^x ^ 1)` values precomputed from the exponent and inverse tables.

All exported objects are `const u8` and `__attribute__((aligned(256)))`, matching the declarations in `raid56.h`.

## Control Flow

There are no functions, branches, loops, allocations, I/O, or runtime initialization side effects in this chunk. Runtime control flow is indirect:

- `raid6_recov_data2()` selects rows from `raid6_gfmul` using `raid6_gfexi`, `raid6_gfinv`, and `raid6_gfexp`, then applies the selected byte maps while reconstructing two missing data stripes.
- `raid6_recov_datap()` selects a `raid6_gfmul` row via `raid6_gfinv[raid6_gfexp[dest1]]` to recover a missing data stripe when P parity is also missing.
- `raid56_recov()` dispatches to those recovery paths depending on RAID5/RAID6 profile and failed stripe indexes.

The syndrome generator in `raid56.c` computes Q parity arithmetically with byte-shift/mask operations, while this table chunk supports recovery-time multiplication and inverse lookup.

## State And Dependencies

The chunk defines read-only global state compiled into the binary. It depends on:

- `kerncompat.h` for `u8` and kernel-style compatibility definitions.
- `kernel-lib/raid56.h` for the public extern declarations consumed elsewhere.
- `kernel-lib/mktables.c` for the generation algorithm and table shapes.
- `kernel-lib/raid56.c` for runtime consumers in RAID6 data recovery.

The tables are generated from the same field arithmetic as Linux RAID6: `gfmul()` shifts by one byte and reduces with polynomial constant `0x1d`; `gfpow()` builds inverse data as `x^254`. I regenerated `tables.c` with `mktables.c`; the generated file matched the checked-in file byte-for-byte (`sha256 a228047cf271b34267309886fe00eadd4593f0a0b1500d4cb66213c2058b0f7e`).

## Risks

A single wrong byte can silently produce incorrect RAID6 reconstruction, so the main risk is table drift from the generator or accidental manual edits. The 256-byte alignment is part of the ABI/performance contract with the RAID table declarations and should remain synchronized across `tables.c` and `raid56.h`.

Recovery callers assume valid device indexes before table indexing. `raid6_recov_data2()` checks `dest1`, `dest2`, and ordering before using `dest2 - dest1`; `raid6_recov_datap()` is reached through `raid56_recov()`'s case analysis. Any future direct caller would need equivalent bounds checks because these arrays do not guard indexes themselves.

The file is generated data, so reviewing diffs by eye is weak. Safer validation is to rebuild from `mktables.c` and compare the whole output, plus run RAID56 recovery tests that cover data+data and data+P failures.

## Cross-Chunk References

The previous chunk defines the file header and the beginning of `raid6_gfmul[256][256]`; this chunk starts inside that table and closes it at line 8710. This chunk then defines every remaining table in the file through EOF at line 10362. There is no next chunk for `tables.c`.