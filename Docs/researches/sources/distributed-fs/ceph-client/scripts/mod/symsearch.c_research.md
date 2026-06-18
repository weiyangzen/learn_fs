<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/symsearch.c -->
# sources/distributed-fs/ceph-client/scripts/mod/symsearch.c

## Purpose

`symsearch.c` builds sorted per-section symbol lookup tables so `modpost` can find nearest symbols for relocation/section-mismatch diagnostics.

## Important APIs, Types, and Functions

Internal types are `struct syminfo` and `struct symsearch`. `syminfo_compare()`, `symbol_count()`, `symsearch_populate()`, and `symsearch_fixup()` build the tables. Public functions are `symsearch_init()`, `symsearch_finish()`, and `symsearch_find_nearest()`.

## Control Flow

Initialization counts valid named symbols, allocates table storage, records symbol pointers with section indexes and values, sorts them, and fixes duplicate/ordering details for nearest lookup. Lookup searches for the closest symbol in the requested section, optionally allowing negative distances and enforcing a minimum distance bound. Finish frees the allocated state.

## State and Persistence Behavior

The lookup table is attached to `struct elf_info` for the lifetime of one parsed object and freed in `parse_elf_finish()`. No files are written.

## Dependencies and Integration Points

It depends on `modpost.h`, target ELF symbol tables, valid-name filtering, and qsort/bsearch-style ordering. It is used by section mismatch reporting in `modpost.c`.

## Risks and Edge Cases

Nearest-symbol diagnostics can be misleading for stripped, compiler-generated, duplicate-address, or section-boundary symbols. Large objects consume memory proportional to symbol count. Incorrect section-index normalization breaks lookups.

## Test Signals

Test relocations near named symbols, duplicate addresses, missing names, mapping symbols, section boundaries, negative-distance behavior, and large symbol tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/symsearch.c -->
