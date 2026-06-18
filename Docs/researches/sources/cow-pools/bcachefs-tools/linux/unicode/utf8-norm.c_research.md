# File Research: sources/cow-pools/bcachefs-tools/linux/unicode/utf8-norm.c

## Purpose
Core UTF-8 validation, normalization, casefold decomposition, and canonical combining class ordering engine.

## Key Responsibilities
- Validates UTF-8 sequences through a compact trie.
- Looks up Unicode data leaves for selected normalization tables.
- Computes normalized length with `utf8nlen()`.
- Initializes cursors with `utf8ncursor()`.
- Emits normalized bytes incrementally with `utf8byte()`.
- Handles Hangul syllable decomposition algorithmically.

## Important Structures
- `utf8trie_t`: compact binary trie used to validate and classify UTF-8 sequences.
- `utf8leaf_t`: embedded leaf containing Unicode generation, canonical combining class, and optional decomposition string.
- `utf8cursor`: streaming state machine for normalized output.

## Algorithm Notes
- Rejects invalid UTF-8, continuation-byte starts, overlong/non-table sequences, and unsupported code points.
- Code points newer than the selected table max age are treated as undecomposed with CCC 0.
- Decomposition can redirect cursor input to an embedded decomposition string.
- Combining marks are emitted in canonical combining class order by repeated scans between stoppers.
- Hangul decomposition uses Unicode Section 3.12 constants and synthesizes a temporary leaf.

## Dependencies
Uses `utf8n.h` and generated Unicode tables.
