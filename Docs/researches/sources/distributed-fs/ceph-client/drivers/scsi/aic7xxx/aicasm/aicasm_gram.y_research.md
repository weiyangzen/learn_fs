# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_gram.y

Purpose: primary Bison grammar and semantic engine for AIC7xxx sequencer assembly language. It parses register definitions, constants, macros, SRAM/SCB layouts, labels, conditionals, critical sections, and sequencer instructions, then constructs typed symbols and encoded instruction objects.

Important APIs and functions: grammar tokens cover directives (`include`, `prefix`, `patch_arg_list`, `version`), register fields/masks/enums, macros, memory regions, labels, conditionals, and opcodes. Semantic helpers include `process_field()`, `initialize_symbol()`, `add_macro_arg()`, `add_macro_body()`, `process_register()`, `format_1_instr()`, `format_2_instr()`, `format_3_instr()`, `test_readable_symbol()`, `test_writable_symbol()`, `type_check()`, `make_expression()`, `add_conditional()`, `add_version()`, `is_download_const()`, and `is_location_address()`.

Control flow: parser actions build symbols as declarations are parsed, maintain current register/SRAM/SCB context, track source/destination register modes, increment `instruction_ptr` as instructions are emitted, and push/pop scopes for conditional firmware patches. ALU, move, shift, branch, test, compare, and pseudo-instructions are normalized into instruction formats. Forward branch labels are recorded for later backpatching by `aicasm.c`.

State and persistence: grammar-owned globals include current symbol/context pointers, special register references (`A`, mode pointer, allones/allzeros/none/sindex), instruction pointer, SRAM/SCB offsets, downloaded constant count, critical-section flag, enum counters, prefix, patch argument list, version text, and filename. It persists only through objects appended to main-program queues and generated output later.

Dependencies and integration: depends on the lexer for tokens, symbol table APIs, instruction bitfield definitions, queue macros, and `stop()` for fatal errors. Its symbol metadata feeds register dump and generated firmware patch tables.

Risks: expression values are largely 8-bit masked in instruction contexts; incorrect type masks can reject valid firmware or permit invalid register bits. Mode tracking is updated only for recognized mode-pointer operations. Scope/patch semantics are sensitive to nested if/else structure. Several diagnostics exit immediately, so parser recovery is minimal.

Test signals: parse known `aic7xxx.seq`/`.reg` inputs, compare generated instruction bytes, validate field/mask type checking, test undefined/redefined symbols, register mode restrictions, forward/backward branches, downloaded constants, nested conditionals, macro definitions, and critical-section balance errors.
