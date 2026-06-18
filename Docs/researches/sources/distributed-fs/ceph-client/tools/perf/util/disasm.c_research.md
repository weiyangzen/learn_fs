# sources/distributed-fs/ceph-client/tools/perf/util/disasm.c

## Purpose
This file turns binary code for a perf `struct symbol` into annotation lines. It selects architecture metadata, parses disassembler output, classifies instructions into semantic operation families, maps branch/call targets back to perf symbols, and coordinates objdump, LLVM, Capstone, raw PowerPC, BPF, compressed module, and kcore paths.

## Important APIs, Types, And Functions
Exported APIs include `arch__find()`, `arch__associate_ins_ops()`, `ins__find()`, `ins__is_call()`, `ins__is_jump()`, `ins__is_fused()`, `disasm_line__new()`, `disasm_line__free()`, `disasm_line__scnprintf()`, `expand_tabs()`, `symbol__strerror_disassemble()`, and `symbol__disassemble()`. Important operation tables are `call_ops`, `jump_ops`, `mov_ops`, `dec_ops`, `lock_ops`, `nop_ops`, and `ret_ops`. Internal control centers are `symbol__parse_objdump_line()`, `symbol__disassemble_objdump()`, `symbol__disassemble_raw()`, `dso__disassemble_filename()`, and instruction parsers such as `call__parse()`, `jump__parse()`, `mov__parse()`, and `lock__parse()`.

## Control Flow
`symbol__disassemble()` resolves the best file path for the DSO, optionally extracts kcore or decompresses kernel modules, then tries disassembly strategies in configured order. Source annotation requests prefer objdump because LLVM/Capstone paths do not support source emission here. Objdump output is read line by line, tabs are expanded, source `file:line` markers update line state, and address-prefixed lines become `struct disasm_line` entries with offsets relative to the target symbol. Each instruction name is looked up in the architecture instruction table, parsed into operands, and later rendered in normalized form.

## State, Dependencies, And Integration
Static state includes the compiled `file_lineno` regex and a lazily grown/sorted array of architecture descriptors. Each disassembly line owns duplicated line text, file-location text, instruction name, operand strings, and per-event annotation data. Integration points are broad: `dso` file resolution/cache APIs, `map` address translation, `maps__find_ams()` symbol lookup, `annotation_line__add()`, `thread` maps, `symbol` metadata, kcore extraction, BPF disassembly, libbfd, LLVM, Capstone, objdump child processes, and perf annotation options.

## Risks And Test Signals
Risks include fragile objdump text parsing, command-line quoting issues around filenames/options, architecture-specific suffix/opcode matching mistakes, wrong objdump-to-memory address translation, races with DSO metadata changes, missing BPF/kcore capabilities, and partial disassembly leaving stale lines. Tests should exercise call/jump/mov parsing, PowerPC raw parsing, source line preservation, kcore nop deletion, compressed module cleanup, failure messages from `symbol__strerror_disassemble()`, backend fallback ordering, tab expansion, and branch/call target resolution across maps.
