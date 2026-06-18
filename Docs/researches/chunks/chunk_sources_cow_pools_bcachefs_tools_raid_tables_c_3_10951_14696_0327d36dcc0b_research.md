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