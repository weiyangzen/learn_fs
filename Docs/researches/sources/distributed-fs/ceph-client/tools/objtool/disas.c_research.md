# sources/distributed-fs/ceph-client/tools/objtool/disas.c

Purpose: BFD-backed disassembly and diagnostic formatting for objtool warnings, tracing, explicit `--disas`, and alternative visualization.

Important APIs/types/functions: `disas_context_create()` initializes libopcodes/BFD state through `arch_disas_info_init()`. `disas_insn()` disassembles one instruction. `disas_print_insn()` and `disas_print_info()` format output. `disas_alt_type_name()`, `disas_alt_name()`, and `disas_alt()` format alternatives. `disas_warned_funcs()` and `disas_funcs()` drive function-level output.

Control flow: creates a context with custom memory and address printers, resolves printed addresses through instruction destinations, relocations, symbols, and alternative remapping, then prints either normal instruction streams or compact/wide alternative tables. Alternative printers collect default and replacement instruction strings, trim trailing NOPs, and align output.

State and persistence behavior: owns transient `struct disas_context` and allocated alternative strings. It writes only to stdout/stderr and does not mutate ELF files.

Dependencies and integration points: depends on BFD/dis-asm compatibility, architecture-specific disassembly setup, objtool instruction graph state, relocation lookup, special alternative data, and global `opts`.

Risks: hard limits `DISAS_ALT_MAX` and `DISAS_ALT_INSN_MAX` can truncate unusual alternative sets. Symbol resolution is heuristic around `_THIS_IP_`, section symbols, and alternative-applied addresses. Missing BFD support disables disassembly-related diagnostics.

Test signals: verify disassembly for warned functions, wildcard/function-pattern `--disas`, compact and `--wide` alternatives, exception/jump-table alternatives, RIP-relative relocations, and big/little-endian architecture setup.
