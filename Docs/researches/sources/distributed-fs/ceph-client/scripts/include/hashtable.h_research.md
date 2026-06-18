# sources/distributed-fs/ceph-client/scripts/include/hashtable.h

## Purpose
Provides a compact kernel-style hash table API for host utilities.

## APIs, Control Flow, and State
The header defines table declaration/definition macros, `HASH_SIZE`, bucket selection by `key % HASH_SIZE(table)`, initialization, add/delete helpers, and iteration macros for all buckets or a specific bucket with safe-removal variants. It builds on `struct hlist_head` and `struct hlist_node`.

## Dependencies and Integration
It includes `array_size.h` and `list.h`. `genksyms.c` uses it for the symbol table, but it is generic enough for other host tools.

## Risks and Test Signals
Risks include modulo-based distribution depending entirely on caller hash quality, macro assumptions that `table` is a true array, and C99 loop variable declarations. Test signals are host-tool compilation, add/find/delete behavior, and safe iteration while removing entries.
