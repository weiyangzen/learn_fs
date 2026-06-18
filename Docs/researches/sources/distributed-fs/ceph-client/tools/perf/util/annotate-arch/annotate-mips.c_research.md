# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-mips.c

## Purpose
Provides MIPS instruction classification for perf annotate. It maps branch-and-link forms to calls, `jr*` forms to returns, and remaining jump/branch mnemonics to generic jumps.

## Important APIs, Types, and Functions
`arch__new_mips()` allocates the `mips` architecture descriptor, sets `objdump.comment_char` to `#`, and installs `mips__associate_ins_ops()`.
`mips__associate_ins_ops()` classifies mnemonics with prefix checks for call-like branch-and-link instructions (`bal`, `bgezal`, `bltzal`, `jal`, `jialc`, and related likely forms), return-like `jr`, and generic `j*`/`b*` jumps.

## Control Flow
The common disassembly parser asks the architecture to classify a mnemonic. MIPS-specific prefix tests run in call-before-jump order so branch-and-link instructions are not downgraded to plain jumps. Matched operations are cached via `arch__associate_ins_ops()`.

## State and Persistence
State is limited to the allocated `struct arch` and instruction-operation associations. The file does not allocate per-instruction operand data or retain external resources.

## Dependencies and Integration Points
Depends on `../disasm.h` for `arch`, `ins_ops`, and generic operation instances. Its output affects annotate jump/call/return markers and any control-flow features that depend on `ins__is_call()`, `ins__is_jump()`, or `ins__is_ret()`.

## Risks
Prefix matching can over-classify synthetic or future mnemonics that share prefixes. Conversely, unlisted aliases can be missed. `jr` is treated as return even though some register jumps may represent indirect branches rather than function returns.

## Test Signals
Use MIPS disassembly with branch-and-link, plain branch, jump, and register-return forms; verify calls and returns render differently and that branch arrows still point to local targets through generic parsers.
