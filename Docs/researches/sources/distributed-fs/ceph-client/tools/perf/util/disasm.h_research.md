# sources/distributed-fs/ceph-client/tools/perf/util/disasm.h

## Purpose
This header declares perf's disassembly and instruction-classification contract for annotation code and architecture-specific backends. It defines the architecture descriptor, instruction descriptor, parsed operand layout, operation callbacks, and the arguments passed into disassembly-line construction.

## Important APIs And Types
`struct arch` carries ELF identity, objdump syntax characters, instruction tables, optional instruction-fusion and DWARF state hooks, and architecture-specific dynamic association. `struct ins` binds a mnemonic to `struct ins_ops`. `struct ins_operands` stores raw operands, source/target details, lock-prefixed nested instructions, and jump comment metadata. `struct annotate_args` supplies the architecture, map/symbol, annotation options, current offset, source line, and file location. Exported APIs include architecture constructors, `arch__find()`, instruction predicates, `ins__find()`, `disasm_line__new/free/scnprintf()`, `symbol__disassemble()`, and render helpers for call/jump/mov/raw instructions.

## Control Flow And Integration
Architecture-specific code constructs `struct arch` instances and can associate unknown instruction names on demand. Generic disassembly code consumes these definitions to parse lines, normalize operands, update annotation state, and render output for perf annotate/report views. Optional `HAVE_LIBDW_SUPPORT` adds data-location/type-state updates tied to DWARF DIEs.

## State And Persistence
The header's structures describe ownership boundaries: operation parsers may allocate operand strings and must pair them with `free` callbacks when custom cleanup is required. `struct arch` instruction arrays may be static initially and later copied/grown dynamically by `arch__associate_ins_ops()`.

## Risks And Test Signals
The main risks are ABI drift between generic disassembly and arch-specific constructors, missing cleanup for operands added by new parsers, and incorrect objdump syntax characters for a target architecture. Build tests should cover all enabled architecture constructors and optional libdw paths; behavior tests should verify instruction lookup, suffix stripping, call/jump predicates, and cleanup of nested lock operands.
