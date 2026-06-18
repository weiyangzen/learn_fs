# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-sparc.c

## Purpose
Provides SPARC instruction classification for perf annotate. It recognizes SPARC call, jump, return, move, integer branch, register branch, and floating-point branch mnemonics.

## Important APIs, Types, and Functions
`arch__new_sparc()` allocates the descriptor, names it `sparc`, sets `objdump.comment_char` to `#`, and installs `sparc__associate_instruction_ops()`.
`is_branch_cond()`, `is_branch_reg_cond()`, and `is_branch_float_cond()` validate condition-code suffixes for integer, register, and floating-point branch families.
`sparc__associate_instruction_ops()` maps `call`, `jmp`, and `jmpl` to calls, `ret`, `retl`, and `return` to returns, `mov` to moves, and validated branch forms to jumps.

## Control Flow
Classification handles exact call/return/move names first. For other names, it strips optional `cw`/`cx` prefixes before testing `b*` and `fb*` branch families. Valid condition suffixes are required before associating `jump_ops`, reducing accidental matches.

## State and Persistence
Only the process-local architecture descriptor and instruction-operation cache are modified. No per-instruction state is allocated in this file.

## Dependencies and Integration Points
Uses `../../util/disasm.h` and generic operation instances. The resulting `ins_ops` drive common annotate arrows, jump-source counts, and call/return markers.

## Risks
Condition recognition is hand-coded and must track assembler naming. Treating `jmp`/`jmpl` as calls can be display-oriented but may not always model indirect branch semantics. Prefix stripping changes the name pointer before caching, so cached aliases may use the stripped name rather than original spelling.

## Test Signals
Annotate SPARC functions containing integer conditional branches, register branches (`brz`, `brlz` forms), floating branches (`fb*`), `call`, `jmpl`, `retl`, and `mov`.
