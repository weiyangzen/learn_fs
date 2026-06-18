# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-arm64.c

## Purpose

`annotate-arm64.c` creates the ARM64 architecture descriptor for perf annotation and adds ARM64-specific instruction parsing, especially move-immediate target parsing.

## Important APIs, Types, and Functions

`struct arch_arm64` embeds `struct arch` and compiled regexes. `arm64_mov__parse` parses `mov` operands and records immediate values as jump targets when present. `arm64_mov_ops` installs that parser. `arm64__associate_instruction_ops` recognizes calls, jumps, and mov instructions. Public `arch__new_arm64` initializes the descriptor and regexes.

## Control Flow and State

Creation allocates state, sets architecture metadata and callback, compiles regexes for call/jump matching, and returns the generic arch pointer. During annotation, instruction names are matched lazily and associated with ops for later parsing/rendering.

## Dependencies and Integration Points

It depends on regex, generic annotate/disasm instruction operations, and ARM64 objdump syntax. It feeds annotation's branch/call classification and immediate target display.

## Risks and Test Signals

Risks include operand parser assumptions, missing aliases, regex drift with objdump output, and partial initialization cleanup. Tests should cover ARM64 `bl`, `b.*`, `cbz/cbnz/tbz/tbnz`, `ret`, `mov` immediate forms, and non-branch instructions.
