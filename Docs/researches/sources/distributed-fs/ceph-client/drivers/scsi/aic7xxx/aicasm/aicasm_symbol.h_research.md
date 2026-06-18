# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_symbol.h

Purpose: shared type contract for the aic sequencer assembler symbol table, expression metadata, macro metadata, labels, conditionals, critical sections, and patch scopes.

Important APIs/types/functions: `symtype` distinguishes registers, aliases, SCB/SRAM locations, fields, masks, enums, constants, labels, conditionals, and macros. `struct reg_info`, `field_info`, `const_info`, `alias_info`, `label_info`, `cond_info`, and `macro_info` define symbol payloads. `expression_t`, `symbol_ref_t`, `critical_section_t`, `patch_info_t`, and `scope_t` describe parser/compiler state. Prototypes expose symbol-table and symbol-list operations plus `symtable_dump()`.

Control flow: no executable control flow lives here, but parser and code-generation files use these structures to build scopes, track referenced symbols, record generated instruction patch sites, and emit register definitions. The list head declarations fix which BSD-style queue primitive each state structure uses.

State and persistence: this header defines heap-owned structures persisted for the assembler process lifetime. Symbols point to one active union payload according to `type`; macro args own regex and replacement strings; scopes carry patch arrays and nested scope queues.

Dependencies and integration: includes local `queue.h` and requires standard regex and `FILE` declarations through including C files. It is consumed by the scanner, grammar, macro grammar, symbol implementation, and main assembler.

Risks and test signals: the union payload is not self-validating, so every `type` transition must allocate/free the matching payload. Macro arg regex lifetime and replacement text cleanup rely on scanner/parser discipline. Compile tests for the host tool plus assembler fixture inputs covering conditionals, nested scopes, critical sections, aliases, enums, and macros are the main signals.
