# sources/distributed-fs/openafs/src/export/symtab.c

This file implements symbol lookup over the EXPORT extension's translated symbol table. `sym_lookup` searches by name when provided or by nearest address otherwise. Name lookup first tries the name exactly, then with `.` and `_` prefixes. Address lookup returns the symbol with the greatest value not exceeding the requested address.

Important helpers are `search`, `symsrch`, and `sym_flex`. `symsrch` prefers exact matches but accepts prefix matches. `sym_flex` copies a symbol into static storage and normalizes its name pointer into a static buffer, hiding 32-bit short-name versus string-table storage differences.

State is global `toc_syms`/`toc_nsyms` from `export.c` and static return buffers in `sym_flex`; it is not reentrant. Dependencies are string functions and `sym.h`. Integration is `import_kfunc`, `import_kvar`, and any debug/address resolution inside the AIX export module. Risks include prefix-match ambiguity, static buffer overwrite on nested/concurrent calls, truncation to 47/8 characters, and address search using `unsigned`. Test signals are lookup tests for exact, dotted, underscored, short-name, string-table, and address-nearest cases.
