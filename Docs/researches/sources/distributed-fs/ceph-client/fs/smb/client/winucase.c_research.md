# sources/distributed-fs/ceph-client/fs/smb/client/winucase.c

Read coverage: full file.

## Purpose
`winucase.c` implements Windows-compatible UTF-16 uppercase mapping for CIFS/SMB name comparison and case-insensitive hashing. The static data was generated from Microsoft Windows 8 uppercase mapping data and converted into C tables.

## Important APIs, types, and functions
The exported function is `wchar_t cifs_toupper(wchar_t in)`. It indexes a two-level table: the high byte selects an optional 256-entry page table from `toplevel`, and the low byte indexes a mapped uppercase character in that page. A zero table entry means no mapping, so the input character is returned unchanged.

The important data structures are the page tables `t2_00`, `t2_01`, `t2_02`, `t2_03`, `t2_04`, `t2_05`, `t2_1d`, `t2_1e`, `t2_1f`, `t2_21`, `t2_24`, `t2_2c`, `t2_2d`, `t2_a6`, `t2_a7`, and `t2_ff`, plus `toplevel[256]`.

## Control flow
`cifs_toupper` extracts `(in & 0xff00) >> 8`, looks up a second-level table, returns the input if no page table exists, then looks up the low byte. If the mapped value is nonzero it returns that uppercase value; otherwise it returns the original input.

## State and persistence behavior
All mapping state is immutable static const data. The function has no allocation, locking, reference counting, or external side effects. Its behavioral persistence is compatibility with Windows casefolding expectations for directory lookup, dcache names, and protocol comparisons.

## Dependencies and integration points
The file depends on `linux/nls.h` for `wchar_t`. It is consumed by CIFS Unicode conversion/comparison code and must match the server-side case-insensitive behavior closely enough for SMB shares that preserve case but search case-insensitively.

## Risks and test signals
The table is intentionally versioned to Windows 8 mappings, so newer Unicode casing changes may not be represented. The design supports BMP `wchar_t` values through two-byte indexing; behavior for any wider code unit is effectively based on low 16 bits. Regeneration risk is high because a misplaced table entry causes subtle lookup mismatches. Test signals include case-insensitive lookup tests for ASCII, Latin-1, Greek, Cyrillic, fullwidth Latin, and unmapped characters, plus comparing results with Windows/SMB server expectations.
