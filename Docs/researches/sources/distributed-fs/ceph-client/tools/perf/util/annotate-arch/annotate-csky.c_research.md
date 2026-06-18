# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-csky.c

## Purpose
Provides the C-SKY architecture adapter for perf annotate disassembly. It creates an `arch` descriptor named `csky`, sets objdump parsing conventions, and maps C-SKY branch, call, and return mnemonics to generic annotation instruction operations.

## Important APIs, Types, and Functions
`arch__new_csky()` allocates and initializes the architecture descriptor using `zalloc()`, copies the ELF machine/e_flags id, sets `objdump.comment_char` to `/`, and installs `csky__associate_ins_ops()`.
`csky__associate_ins_ops()` classifies mnemonics into `jump_ops`, `call_ops`, or `ret_ops`, then caches the association through `arch__associate_ins_ops()`.

## Control Flow
Perf annotation asks the architecture to associate an instruction name when a disassembly line is parsed. The function compares the mnemonic against fixed C-SKY branch forms (`bt`, `bf`, `bez`, `br`, `jmpi`, `jmp`, and related conditional forms), call forms (`bsr`, `jsri`, `jsr`), and return form (`rts`). Matching names are registered and reused by the common disassembly renderer.

## State and Persistence
State is limited to the allocated `struct arch` and the common instruction-operation cache populated by `arch__associate_ins_ops()`. There is no persistent file or cross-run state.

## Dependencies and Integration Points
Depends on `../disasm.h` for `struct arch`, `struct ins_ops`, and generic operation instances. Integrated by the perf architecture registry through `arch__new_csky()`, then consumed by generic annotate code for jump arrows, call markers, and return markers.

## Risks
The classifier uses exact string comparisons, so new assembler aliases or suffix forms are ignored until added. A missed branch/call primarily affects annotation presentation and jump-target accounting rather than sample accounting. The comment character is architecture-specific and must match objdump output.

## Test Signals
Useful tests include annotating C-SKY binaries containing each listed branch/call/return form, checking rendered call/return/jump arrows, and confirming comments beginning with `/` are parsed correctly.
