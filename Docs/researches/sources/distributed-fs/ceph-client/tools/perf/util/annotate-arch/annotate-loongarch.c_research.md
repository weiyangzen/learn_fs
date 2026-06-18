# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-loongarch.c

## Purpose
Implements LoongArch-specific instruction classification and operand parsing for perf annotate. It improves generic jump and call rendering by resolving target addresses, symbol names, local offsets, and outside-function status from LoongArch objdump syntax.

## Important APIs, Types, and Functions
`arch__new_loongarch()` creates the `loongarch` descriptor and installs `loongarch__associate_ins_ops()`.
`loongarch_call__parse()` parses call operands containing `#addr <name>`, stores target address/name, maps objdump address to runtime memory address, and resolves a target symbol through thread maps.
`loongarch_jump__parse()` parses branch targets either after `#` or directly from the operand, records raw comment/function markers, computes whether the target is outside the current symbol, fills local offset availability, and resolves a symbol when possible.
`loongarch_call_ops` and `loongarch_jump_ops` bind those parsers to generic `call__scnprintf()` and `jump__scnprintf()`.

## Control Flow
During disassembly, `bl` is associated with LoongArch call parsing, `jirl` is treated as a return, and unconditional/conditional branch families (`b`, `beq*`, `bne*`, `blt*`, `bge*`, `bltu*`, `bgeu*`) use LoongArch jump parsing. Target resolution follows map conversion (`map__objdump_2mem()`), map lookup (`maps__find_ams()`), and verification by converting back to objdump address.

## State and Persistence
The code mutates `ins_operands` for each disassembly line by filling `ops->target`, `ops->jump`, and allocated target names. It temporarily gets map references and releases them with `addr_map_symbol__exit()`. No persistent state is stored beyond the per-line annotation structures and architecture operation cache.

## Dependencies and Integration Points
Depends on perf map/thread/symbol infrastructure (`map.h`, `maps.h`, `symbol.h`, `thread.h`) and common disassembly helpers. Feeds `annotate.c` jump validation, arrow rendering, and local target indexing by setting `target.offset`, `target.offset_avail`, and `target.outside`.

## Risks
Parsing assumes GNU objdump-style comments and symbol delimiters. `name = strchr(endptr, '<'); name++;` relies on the call operand containing `<`; malformed input before this point can risk invalid pointer use. Incorrect map conversion or symbol verification would show wrong target symbols or suppress local jump arrows.

## Test Signals
Annotate LoongArch samples with internal branches, external branches, calls with symbol names, and `jirl` returns. Include branch operands with comments and function annotations to verify `#` parsing and skip-function-character behavior.
