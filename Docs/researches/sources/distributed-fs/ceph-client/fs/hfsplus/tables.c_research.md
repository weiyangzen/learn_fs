# sources/distributed-fs/ceph-client/fs/hfsplus/tables.c

## Purpose
`tables.c` contains the static Unicode mapping data used by HFS+ filename comparison, conversion, hashing, composition, and decomposition. The tables encode Apple's HFS+ case-folding behavior and normalization mappings, letting `unicode.c` implement HFS+ name semantics without dynamic Unicode database lookups.

## Important APIs, types, and functions
The exported data arrays are `hfsplus_case_fold_table[]`, `hfsplus_decompose_table[]`, and `hfsplus_compose_table[]`. There are no functions. `hfsplus_fs.h` declares the arrays for use by `unicode.c`.

`hfsplus_case_fold_table` starts with a 256-entry high-byte index and points to 256-entry subtables for blocks that have case mappings or ignorable characters; a zero high-byte entry means identity mapping for that block, and folded value zero means the character is ignorable. `hfsplus_decompose_table` is a trie-like table for non-Hangul decomposition. `hfsplus_compose_table` is a reverse lookup tree for composing decomposed sequences back to precomposed Unicode where HFS+ expects it.

## Control flow
There is no executable control flow in this file. Runtime lookup is driven by `unicode.c`: `case_fold()` indexes the case-fold table by high and low byte; `hfsplus_decompose_nonhangul()` walks the decomposition table by nibbles; and `hfsplus_compose_lookup()` binary-searches subranges in the compose table.

## State and persistence behavior
The arrays are immutable kernel data. They influence persistent namespace behavior because catalog key ordering, dentry hashing, and on-disk filename normalization depend on their exact values. Changing them can make existing names unreachable or alter collision behavior on casefolded HFSX volumes.

## Dependencies and integration points
The file depends only on `hfsplus_fs.h` for declarations and type availability. It is tightly coupled to the lookup algorithms in `unicode.c` and indirectly to catalog key comparison/building, dentry operations, and KUnit tests in `unicode_test.c`.

## Risks and test signals
Risks include table corruption, accidental regeneration from a different Unicode/HFS+ version, mismatch between compose/decompose lookup assumptions and table layout, ignorable-character handling changes, and large static data increasing review difficulty. Test signals include casefold vectors, decomposition/composition vectors including Hangul and multi-codepoint sequences, HFSX case-insensitive lookup on real disk images, dentry hash/compare consistency, and KUnit coverage for Unicode conversion paths. Static checks can also verify array bounds implied by offsets.
