# Group Research: group_36_9front_sources_os_plan9_9front_sys_src_cmd_7l_bits_c_sources_os_plan9_0a42361b6f40

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/bits.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7l/bits.c

ARM64 logical-immediate lookup support for the `7l` linker/assembler backend.

This file is dominated by the static `bitmasks[]` table, containing encodable ARM64 logical-immediate patterns with their decoded fields:
- `s`: run size/width metadata used by logical-immediate encoding.
- `e`: element size.
- `r`: rotation.
- `v`: the actual 64-bit mask value.

The only function is `findmask(uvlong v)`, which binary-searches `bitmasks[]` and returns the matching `Mask*` or `nil`. It is used by instruction encoding paths to decide whether a constant can be emitted as an ARM64 bitmask immediate.

Important details:
- The table is sorted by `v`, which is required by `findmask`.
- Supports both 32-bit-replicated and full 64-bit encodable logical-immediate forms.
- This is linker backend infrastructure, not filesystem logic.

Filesystem relevance: indirect. It is part of the Plan 9/9front ARM64 toolchain sources included in the OS source tree.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/bits.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/compat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7l/compat.c

Tiny compatibility wrapper for the ARM64 linker.

Contents:
- Includes local linker declarations from `l.h`.
- Includes shared compiler compatibility code from `../cc/compat`.

There is no local logic. Its purpose is to pull the common Plan 9 compiler/linker compatibility implementation into the `7l` build.

Filesystem relevance: none directly; build support only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/dyn.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7l/dyn.c

Dynamic module relocation/import table support for the ARM64 linker.

Key elements:
- `Reloc` stores relocation count/capacity plus parallel arrays of relocation modes and word addresses.
- `grow` expands relocation arrays in chunks of 64 entries.
- `dynreloc` records one relocation, classifying it as absolute/relative and defined/undefined, converting byte addresses to word addresses, and keeping entries sorted.
- `sput` emits a NUL-terminated string through the linker output buffer.
- `asmdyn` emits the dynamic import table and relocation stream, then patches the table size at the start.

Important details:
- Relocation addresses must be word-aligned.
- Undefined symbols become import-relative relocation entries.
- Relocation deltas are encoded compactly using 1, 2, or 4 bytes depending on distance from the previous relocation.
- Debug `v` prints import/export counts.

Filesystem relevance: indirect. This supports dynamically loadable Plan 9 modules, not filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/dyn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/l.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7l/l.h

Central header for the 9front ARM64 linker `7l`.

Major definitions:
- `Adr`: instruction operand/address form, including offsets, strings, IEEE constants, symbols, registers, names, and operand class.
- `Prog`: linker instruction node with `from`, optional `from3`, `to`, branch target, PC, line, marks, opcode, and cached optab index.
- `Sym`: linker symbol table entry with type, version, value, signature, file index, frame/become metadata, and linkage.
- `Autom`: automatic/local symbol metadata attached to text symbols.
- `Optab`: instruction pattern entry used by the encoder, with opcode, operand classes, encoding case type, emitted size, parameter, and literal flags.
- `Mask`: ARM64 logical-immediate mask descriptor used by `bits.c`.

Important enums and globals:
- Symbol classes: `STEXT`, `SDATA`, `SBSS`, `SXREF`, `SLEAF`, `SFILE`, `SSTRING`, `SUNDEF`, `SIMPORT`, `SEXPORT`.
- Operand classes: register, stack pointer, shifts, constants, branches, auto/external offsets, pre/post-indexed operands, vector registers, and fallback classes.
- Mark flags: `FOLL`, `LABEL`, `LEAF`, `FLOAT`, `BRANCH`, `LOAD`, `SYNC`, `NOSCHED`.
- ARM64-specific constants: `STACKALIGN = 16`, `PCSZ = 8`, relocation bit splits `Roffset`/`Rindex`.
- Linker globals for output layout, buffers, symbol hash table, text/data instruction lists, dynamic import/export state, and literal-pool state.

Declared functions cover the whole linker pipeline:
- Object/archive loading: `objfile`, `ldobj`, `lookup`, `loadlib`.
- Control flow/layout: `patch`, `follow`, `span`, `noops`.
- Data and dynamic linking: `dodata`, `dynreloc`, `asmdyn`, `import`, `export`.
- Output: `asmb`, `asmout`, `asmsym`, buffered integer writers.
- Formatting and diagnostics: `listinit`, `%A/%D/%P/%S/%N/%R` formatters, `diag`.

Filesystem relevance: indirect. It defines the linker’s shared state and ABI contracts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/l.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7l/list.c

Debug/listing formatter support for ARM64 linker instructions and operands.

Key functions:
- `listinit` installs Plan 9 format verbs for opcodes, operands, programs, strings, names, and classes.
- `Pconv` formats one `Prog`, including special display for `ADATA`, `AINIT`, and `ADYNT`.
- `Aconv` maps opcode numbers to `anames[]`.
- `Dconv` formats `Adr` operands: constants, registers, stack pointer, shifts, extended registers, register-offset addressing, branches, floating constants, string constants, and special registers.
- `Nconv` formats named offsets for extern/static/auto/param operands.
- `Rconv` maps operand class IDs to `cnames[]`.
- `Sconv` escapes fixed-size Plan 9 string constants.
- `prasm` prints one instruction.
- `diag` prints an error prefixed by current function name and aborts after too many errors.

Important details:
- Uses `curp` and `curtext` for context-sensitive branch and diagnostic formatting.
- Knows ARM64 condition-code names and selected special registers (`FPSR`, `FPCR`, `NZCV`).
- Diagnostic reporting is global and increments `nerrors`.

Filesystem relevance: none directly; developer/debug infrastructure for the linker.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/mod.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7l/mod.c

Import/export symbol-table support for dynamically loadable modules.

Key functions:
- `readundefs` reads whitespace-separated symbol names from a file and marks them as import/export references.
- `undefsym` assigns an import index to an unresolved external symbol and converts it to `SUNDEF`.
- `zerosig` clears a symbol signature.
- `import` walks the symbol hash table and converts matching signed external references into imports.
- `ckoff` validates relocation offsets against the relocation address bit budget.
- `newdata` creates synthetic `ADATA` records.
- `export` builds the `_exporttab` data object and associated `.string` storage for exported symbols.

Important details:
- Exported symbols are collected from signed, defined symbols and sorted by name.
- Each export table entry contains signature, address, and name pointer.
- The table ends with three zero words.
- `export` synthesizes data records rather than writing bytes directly, so normal data layout/output handles the result.

Filesystem relevance: indirect. This supports Plan 9 module linking, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/mod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/noop.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7l/noop.c

Late instruction cleanup and function prologue/epilogue expansion for ARM64.

Key functions:
- `noops` performs several final rewrites over the instruction list.
- `nocache` clears cached instruction-class/optab data after an instruction is rewritten.

Main `noops` responsibilities:
- Finds leaf subroutines by clearing `LEAF` on calls.
- Tracks frame size and `BECOME` argument-space requirements.
- Removes `ANOP` instructions and retargets branches around them.
- Defines `ALEFbecome` with the maximum become size.
- Increases caller frame sizes when a function may call a `BECOME` target.
- Aligns stack frames to `STACKALIGN`.
- Expands `ATEXT` into stack adjustment and link-register save sequences.
- Expands `ARETURN` into restore, stack adjustment, and `ARET`.
- Expands special `RETURN $n` forms into branch/become sequences.

Important details:
- Leaf functions with no frame can avoid save/restore.
- Large stack frames are split between pre/post-indexed link-register operations and explicit `ADD`/`SUB`.
- Rewritten instructions must have caches cleared because operand classes and optab selections are no longer valid.

Filesystem relevance: indirect toolchain code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/noop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/obj.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7l/obj.c

Main ARM64 linker driver, object/archive reader, symbol table manager, profiling inserter, and floating/endian helper code.

Key entry points:
- `main` parses linker options, chooses output/header layout, initializes linker state, loads object files and libraries, optionally builds import/export tables, then runs `patch`, profiling, `dodata`, `follow`, `noops`, `span`, and `asmb`.
- `usage` and `errorexit` handle command-line and error exits.
- `objfile` loads either a raw object or Plan 9 archive, resolving archive members from the archive symbol table.
- `ldobj` decodes Plan 9 object records into `Prog` nodes, handles symbol/name records, history records, data records, text records, branch offsets, duplicate text handling, and floating literal synthesis.

Object/symbol helpers:
- `isobjfile` distinguishes object/archive input from import/export symbol-list files.
- `zaddr` decodes serialized operand records into `Adr`.
- `lookup` hashes and interns symbols by name/version.
- `prg` allocates and initializes a `Prog`.
- `nopout` rewrites an instruction to `ANOP`.
- `readsome` refills the object input buffer while preserving unconsumed bytes.
- `addlib`, `addhist`, `histtoauto`, and `collapsefrog` maintain history/autolib metadata from `AHISTORY`.

Pipeline and rewrite details:
- Negative immediate `ADD`/`SUB` variants are canonicalized to the opposite operation.
- Non-encodable float constants for `AFMOVS`/`AFMOVD` are moved into synthetic data literals.
- `AGLOBL`, `ADATA`, `ADYNT`, and `AINIT` are diverted into data lists.
- `ATEXT` establishes text symbols, PC values, frame sizes, and text-chain links.
- Branch operands are adjusted by the current object base PC.
- Archive loading loops while unresolved `SXREF` symbols can pull in more members.

Profiling helpers:
- `doprof1` creates `__mcount` data and inserts counter increments at function entry.
- `doprof2` inserts calls to `_profin`/`_profout` or `_tracein`/`_traceout`.

Other helpers:
- `nuxiinit`/`find1` initialize byte-order conversion tables.
- `ieeedtof` converts Plan 9 double representation to single precision.
- `ieeedtod` converts Plan 9 IEEE representation to host `double`.

Filesystem relevance: indirect. This is OS toolchain infrastructure for producing ARM64 Plan 9 binaries.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/obj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/optab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7l/optab.c

Instruction selection table for the ARM64 linker encoder.

This file defines `Optab optab[]`, mapping assembly opcodes and operand classes to encoder case numbers, emitted sizes, parameters, and literal/relocation flags.

Covered instruction families:
- `ATEXT` pseudo-instructions.
- Arithmetic and logical instructions with register, shifted-register, extended-register, add-immediate, bitmask-immediate, and large-constant forms.
- Moves, including constant materialization through `MOVK`/`MOVN`/`MOVZ`-style cases.
- Branches, calls, returns, ADR/ADRP, conditional branches, compare/test-and-branch.
- Bitfield/extract/sign-extension/count instructions.
- System instructions, barriers, hints, `ERET`.
- Loads/stores for byte/halfword/word/doubleword, signed/unsigned forms, stack/extern/register offsets, scaled/unscaled offsets, pre/post-indexed modes, register-offset modes, and register pairs.
- Floating-point moves, arithmetic, conversions, compares, conditional compares/selects.
- Atomic load/store exclusive/acquire/release forms.
- Vector/crypto-like entries such as AES/SHA forms.
- Data pseudo-ops `AWORD`, `ADWORD`, `ACASE`, `ABCASE`.

Important fields:
- `a1`, `a2`, `a3` are operand classes matched against `from`, `reg/from3`, and `to`.
- `type` is the encoder case consumed by `asmout`.
- `size` is the instruction expansion size in bytes.
- `param` supplies registers such as `REGSB`/`REGSP` or other encoder parameters.
- Flags such as `LFROM`, `LTO`, and `LPOOL` mark literal/large-constant handling needs.

Filesystem relevance: indirect toolchain backend table.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/optab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/pass.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7l/pass.c

General linker passes for parsing constants, laying out data, following/reordering control flow, and patching branches.

Key functions:
- `atolwhex` parses signed decimal, octal, and hex integers.
- `rnd` rounds values up to an alignment.
- `dodata` validates data initializers, assigns data/BSS addresses, aligns objects, defines linker symbols like `bdata`, `edata`, `end`, and `etext`.
- `brchain` follows chains of unconditional branches.
- `follow` creates a new instruction order using `xfol`.
- `xfol` lays out reachable code, inverts simple branches when useful, copies short already-followed sequences when needed, and inserts explicit branches to already-emitted code.
- `patch` resolves call/branch/return targets from symbols or PCs and connects `cond` pointers.
- `mkfwd` builds skip-forward links to speed PC-to-`Prog` lookup.
- `brloop` collapses branch chains while detecting loops.
- `undef` reports remaining unresolved external references.

Important details:
- `dodata` puts small data objects first to improve addressing via `REGSB`.
- Data and BSS sizes are rounded to 8-byte boundaries.
- Undefined call targets can become dynamic imports via `SUNDEF`; non-call undefined branches are diagnosed.
- Branch target lookup uses `forwd` acceleration links created by `mkfwd`.
- `xfol` is inherited Plan 9 linker control-flow layout logic and mutates branch directions/links.

Filesystem relevance: indirect. It is binary layout and control-flow infrastructure, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/pass.c -->