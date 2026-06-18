# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_symbol.c

Purpose: implements the assembler symbol table and generated register/debug header emission for the aic7xxx sequencer build tools.

Important APIs/types/functions: `symtable_open()` creates an in-memory Berkeley DB hash table. `symtable_get()` returns existing symbols or creates `UNINITIALIZED` symbols while tracking reference counts. `symbol_delete()` frees type-specific payloads. `symlist_add()`, `symlist_search()`, `symlist_free()`, and `symlist_merge()` manage symbol lists. `symtable_dump()` emits generated `#define`s, downloaded constants, exported labels, and optional debug register print helpers through `aic_print_*()` helpers.

Control flow: parsing code creates and mutates `symbol_t` records. At dump time the DB is iterated into sorted buckets for registers, masks/fields/enums, constants, downloaded constants, aliases, and exported labels. Debug print tables are emitted before masks and aliases are folded next to their parent register entries. The final output is ordered register/address definitions, field/mask definitions, constants, download constants, and label offsets.

State and persistence: runtime state is the static `DB *symtable` and heap-owned `symbol_t` payloads. Persistence is indirect: generated C/header output is written to caller-supplied `FILE *` handles, while `symtable_close()` walks and deletes all stored symbols.

Dependencies and integration: depends on `aicdb.h`/`dbopen`, `queue.h`, symbol metadata from `aicasm_symbol.h`, global `versions`, `prefix`, `stock_include_file`, and `appname` from the assembler.

Risks and test signals: the DB stores raw symbol pointers, so ownership/lifetime bugs corrupt all later generation. `symtable_get()` increments `count` on each lookup, and debug generation uses `count == 1` to suppress unused register definitions, making accidental extra lookups behaviorally visible. Tests should cover duplicate symbols, sorted field/register emission, aliases, exported labels, macro symbols, cleanup after partial parse failure, and generated debug code with and without `dfile`.
