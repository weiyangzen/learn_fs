# sources/distributed-fs/ceph-client/scripts/genksyms/genksyms.c

## Purpose
Implements the `genksyms` host program, which parses preprocessed C declarations and emits `#SYMVER name crc` lines for exported symbols. The CRC encodes ABI-relevant type information for module versioning.

## APIs, Control Flow, and State
Public functions shared with the lexer/parser are `find_symbol()`, `add_symbol()`, `export_symbol()`, `free_node()`, `free_list()`, `copy_node()`, `copy_list_range()`, and `error_with_pos()`. Global state includes `cur_line`, `cur_filename`, `in_source_file`, CLI flags, a 4096-bucket symbol hashtable, and traversal lists for expansion and dump output. `main()` parses flags (`--debug`, `--dump`, `--reference`, `--dump-types`, `--preserve`, warnings), reads an optional reference type dump, invokes `yyparse()`, optionally writes expanded type dumps, and exits nonzero on accumulated errors.

`__add_symbol()` handles namespace mapping, redefinition detection, reference override preservation, enum constant value synthesis, and declaration status tracking. `expand_and_crc_sym()` recursively expands typedef, enum, struct, and union references into a CRC stream while detecting cycles through `expansion_trail`. `export_symbol()` finds the normal symbol, expands it, reports reference changes, and prints the final CRC.

## Dependencies and Integration
It depends on generated lexer/parser code, `genksyms.h`, local hashtable/list helpers, and kbuild piping preprocessed sources containing rewritten export markers.

## Risks and Test Signals
Risks include segfaults on malformed reference files, stack use from `alloca()` for large type lists, C-parser incompleteness, namespace collision behavior, and ABI churn if formatting changes. Test signals are stable `#SYMVER` values, `--dump-types` round trips, warning behavior under `--preserve`, and module build tests with changed exported prototypes.
