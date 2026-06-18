# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-powerpc.c

## Purpose
Implements PowerPC-specific annotate support. It classifies branch/call/return mnemonics, detects load/store and arithmetic instructions from raw instruction bits, configures operand metadata for type tracking, and provides a libdw-enabled register type-state updater for register moves.

## Important APIs, Types, and Functions
`arch__new_powerpc()` creates the architecture descriptor, sets `show_asm_raw = true`, installs `powerpc__associate_instruction_ops()`, and, with libdw, installs `update_insn_state_powerpc()`.
`powerpc__associate_instruction_ops()` maps `b*` mnemonics to jump/call/return operations, excluding non-branch prefixes such as `bcd`, `brinc`, and `bper`.
`check_ppc_insn()` inspects `dl->raw.raw_insn` to choose `load_store_ops` or `arithmetic_ops` for instructions that need operand location metadata.
`load_store__parse()` marks the source operand as a memory reference and sets `multi_regs` for X-form opcode 31 instructions.
`arithmetic__parse()` marks arithmetic source operands with multiple registers except for specific one-source extended forms.
`update_insn_state_powerpc()` propagates DWARF type-state across register moves, including special handling for `mr` encoded as OR X-form.

## Control Flow
Text mnemonics first classify branch-like instructions. Raw instruction classification then uses primary opcode and opcode-extension tables: opcodes 32 to 63 are memory instructions, opcode 31 is searched in sorted tables for memory or arithmetic X-form instructions, and selected two-operand arithmetic opcodes are recognized separately. With libdw type profiling, `annotate-data.c` calls the architecture updater as it walks basic blocks, allowing PowerPC register copies to keep data type attribution alive.

## State and Persistence
Static opcode tables provide read-only classification state. Per-line parsing writes `mem_ref` and `multi_regs` fields into `ins_operands`. Type-state updates mutate the transient `struct type_state` used during data-type lookup. `annotate_opts.show_asm_raw` is globally enabled for PowerPC because raw bits are required by the parser.

## Dependencies and Integration Points
Depends on `annotate-data.h`, `debug.h`, and `disasm.h`; `check_ppc_insn()` is consumed by common disassembly logic when raw PowerPC instructions need operation selection. `annotate_get_insn_location()` later uses `get_powerpc_regs()` with these metadata flags to fill operand locations.

## Risks
The opcode-extension tables must remain sorted for `bsearch()`. A missing or unsorted entry silently loses load/store or arithmetic type tracking. The `arithmetic__parse()` check compares the primary opcode variable against extension constants, which is fragile and depends on intended instruction encodings. Branch classification based on suffixes may misclassify uncommon branch aliases.

## Test Signals
Run annotate and data-type annotation on PowerPC binaries with X-form loads/stores, arithmetic register moves, `mr`, branch-and-link calls, `blr` returns, and conditional branches. Build with and without `HAVE_LIBDW_SUPPORT` to verify both classification-only and type-state paths.
