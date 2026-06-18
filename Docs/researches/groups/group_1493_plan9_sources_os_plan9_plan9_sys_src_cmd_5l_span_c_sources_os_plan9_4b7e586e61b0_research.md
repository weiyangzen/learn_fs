# Group Research: group_1493_plan9_sources_os_plan9_plan9_sys_src_cmd_5l_span_c_sources_os_plan9_4b7e586e61b0

Scope verified against `Docs/research_subset_a.md`: this group is inside `sources/os/plan9/plan9`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/span.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/span.c

This is the ARM linker span/layout and instruction selection support for `5l`. It assigns program counters, sizes instructions through `oplook`, handles `ATEXT` boundaries, updates text symbol values, rounds final text size, and sets `etext`.

A central responsibility is ARM literal pool management. `addpool`, `checkpool`, and `flushpool` collect constants needed by instructions, deduplicate pool entries, and insert branches around literal pools before 12-bit PC-relative literal loads go out of range. The implementation flushes on explicit pool points, unconditional PC writes, pool overflow, or end of program.

The file also classifies operands via `aclass`, including register, shifted-register, auto/param, extern/static, constants, branch targets, floating constants, and offset forms. This drives `oplook`, which matches instructions against `optab` using compatibility tables built by `buildop`.

It includes dynamic relocation support for dynamically loadable modules: `dynreloc` records sorted relocation addresses and `asmdyn` emits import and relocation tables.

Filesystem relevance is indirect but important: this is part of the Plan 9 toolchain used to build OS binaries. Its data/text layout, symbol resolution, relocation, and dynamic module support influence how filesystem and kernel code becomes executable images.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/span.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6a/a.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6a/a.h

This header defines the shared state and types for the amd64 assembler `6a`. It includes Plan 9 base headers, Bio I/O, and the amd64 object/instruction definitions from `../6c/6.out.h`.

Important types include `Sym` for assembler symbols, `Gen` and `Gen2` for encoded operands, `Io` for input streams, and `Hist` for source history records. `Gen` carries the operand type, symbol, offset, register index, scale, string constant, and floating constant data that later become Plan 9 object records.

The header declares assembler globals for debug flags, hash tables, include paths, input buffers, output file state, two-pass assembly state, source line tracking, and current PC. It also declares the assembler pipeline functions: lexical input, macro handling, include handling, parser entry, symbol setup, object output, history output, and platform wrappers.

Its filesystem-facing importance is mostly build-pipeline related: the assembler reads source files, include files, and emits `.6` object files. It also abstracts path handling and file creation across Plan 9, Unix, and Windows host environments.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6a/a.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6a/a.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6a/a.y

This yacc grammar defines amd64 Plan 9 assembly syntax for `6a`. It parses labels, symbol assignments, instructions, constants, expressions, registers, immediates, memory operands, branch targets, and special pseudo-instruction forms.

Instruction parsing is grouped by lexer token classes such as `LTYPE0` through `LTYPE4`, `LTYPED`, `LTYPET`, `LTYPEC`, `LTYPES`, `LTYPEM`, and media/SSE-specific forms. Each rule builds a `Gen2` pair and calls `outcode`, except assignments and labels, which update assembler symbols.

The grammar covers Plan 9 assembler addressing forms including `name+offset(SB)`, `name<>(SB)` for statics, stack/parameter references through `SP` and `FP`, PC-relative branch expressions, indirect calls/jumps, indexed addressing with scale checks, and constants including integer, floating, and 8-byte string constants.

Expression grammar supports arithmetic, shifts, bitwise operations, unary complement, and parenthesized expressions. The grammar enforces some amd64-specific constraints, such as index scale values and special handling for double-precision shift/move forms using segment or long registers.

Filesystem relevance is indirect: this grammar is the input language used to assemble runtime, syscall, kernel, and filesystem-adjacent Plan 9 assembly into object files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6a/a.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6a/lex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6a/lex.c

This file is the amd64 assembler driver, symbol/opcode initializer, object encoder, and lexer support glue. `main` parses options, supports parallel assembly on non-Windows hosts using `NPROC`, and delegates each file to `assemble`.

`assemble` derives the output `.6` file name, configures include paths, opens the object output, and runs the assembler in two passes. Pass 1 resolves labels and symbols; pass 2 emits history and instruction records.

The large `itab` table maps register names, special pseudo-registers (`SP`, `SB`, `FP`, `PC`), integer/floating/media registers, segment/control/debug/task registers, opcodes, pseudo-ops (`TEXT`, `DATA`, `GLOBL`, `END`, `MODE`), condition aliases, x87, MMX, and SSE instructions into parser token classes and opcode enum values.

`cinit` initializes symbols and null operands. `zname`, `zaddr`, and `outcode` emit Plan 9 object records, including compact address encodings, symbol table slots, 64-bit offsets, floating constants, string constants, and source history.

The file includes shared C compiler lexer/macro/compat bodies, so assembler preprocessing and macro behavior align with the broader Plan 9 compiler suite.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6a/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/6.out.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/6.out.h

This header defines the amd64 Plan 9 object instruction namespace and operand encoding constants shared by `6a`, `6c`, and `6l`.

The `enum as` instruction list covers classic x86, amd64 extensions, floating-point x87 operations, conditional moves, 64-bit operations, MMX/SSE/media operations, Plan 9 pseudo-ops (`ANAME`, `AHISTORY`, `ADATA`, `ATEXT`, `AGLOBL`, `AEND`, `AMODE`), dynamic/import/export pseudo-ops, and return variants.

The operand enum defines register numbering for byte, word/quad, high-byte, x87, MMX, XMM, segment, descriptor, control, debug, and task registers. It also defines pseudo-address types such as branch, extern, static, auto, param, const, float const, string const, address, file, and indirect forms.

The `T_*` bits describe compact object-address encoding fields: type, index/scale, offset, float constant, symbol reference, string constant, and 64-bit offset extension. Register role macros specify return registers, stack pointer, temporary register, external register allocation bounds, and floating register bounds.

This file is the contract for amd64 Plan 9 object files. Filesystem relevance is via the OS build chain: object records produced for filesystem/kernel code must use these stable opcode and address encodings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/6.out.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/cgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/cgen.c

This is the core amd64 expression code generator for `6c`. `cgen` lowers C expression trees into Plan 9 amd64 instructions, handling assignments, arithmetic, shifts, multiply/divide/modulo, address generation, function calls, indirection, comparisons, logical expressions, casts, conditionals, comma expressions, struct/union expressions, and pre/post increment or decrement.

It pays close attention to evaluation order and register pressure. If both sides of an expression can call functions, it spills one side into temporaries before continuing. It uses fixed amd64 registers where required, especially `CX` for variable shifts and `AX`/`DX` for multiply/divide.

The file delegates optimized constant arithmetic to `mulgen`, `sdivgen`, `udivgen`, `sdiv2`, and `smod2`. It has special handling for bitfields through `bitload` and `bitstore`, boolean generation through `boolgen`, and structure copying/return through `sugen`.

`lcgen` and `reglcgen` generate l-values and addresses. Helpers classify immediate constants, hard constants, useful cast folding, 64-bit high/low halves, and suspicious 32-bit masks used against 64-bit values.

Filesystem relevance is build-pipeline level: this backend emits the machine code for Plan 9 amd64 C code, including kernel and filesystem components.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/cgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/div.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/div.c

This file implements optimized division and modulo by invariant integer constants for amd64 code generation. It is based on Granlund and Montgomery’s multiplication-based division method.

`multiplier`, `sdiv`, and `udiv` compute magic multipliers, shifts, and adjustment flags for signed and unsigned 32-bit division. `sdivgen` and `udivgen` emit instruction sequences using multiply, shifts, adjustment adds, and sign correction instead of hardware divide when the divisor is constant.

`sdiv2` and `smod2` handle signed division and modulo by powers of two, preserving C signed-division semantics through sign extension and biasing before arithmetic shifts. `sext` produces sign-extension helpers, using `CDQ` when possible.

This is performance-sensitive compiler infrastructure. It matters to filesystem code indirectly because hot paths compiled with `6c`, including block and metadata arithmetic, benefit from constant division lowering without requiring source-level changes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/div.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/enam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/enam.c

This generated-style table maps amd64 opcode enum values to printable instruction names. `anames[]` must remain synchronized with the `enum as` order in `6.out.h`.

The list includes base x86 instructions, pseudo-ops, x87 operations, system instructions, conditional moves, 64-bit amd64 operations, media/SSE operations, 3DNow-like entries, return variants, `SWAPGS`, `MODE`, and `LAST`.

The table is consumed by listing/debug formatting code in the compiler and linker. It underpins `%A` formatting, diagnostic output, debug dumps, and assembly listings.

Filesystem relevance is diagnostic rather than runtime: when building Plan 9 kernel or filesystem code, this table makes compiler/linker output readable and allows instruction-level debugging of generated object streams.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/enam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/gc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/gc.h

This is the amd64 backend header for `6c`. It includes generic C compiler definitions and amd64 object definitions, then declares target sizes, backend data structures, globals, macros, and function prototypes.

Core structures include `Adr` for machine operands, `Prog` for emitted instructions, `Case`/`C1` for switch lowering, `Var` for register allocation candidates, `Reg` for control-flow/liveness nodes, `Rgn` for register allocation regions, and `Renv` for register environment state.

The header defines target sizes: 8-byte pointers, 4-byte long/int, 8-byte vlong/double, and amd64-specific return/register roles. It declares global compiler backend state such as instruction lists, string data buffers, register arrays, live-variable bitsets, region arrays, and external register offsets.

It also prototypes the full backend: statement generation, expression generation, object output, switch lowering, register allocation, peephole optimization, 64-bit support hooks, division/multiplication lowering, and formatted listing.

Filesystem relevance is as target ABI/build infrastructure. It controls how Plan 9 amd64 C code, including filesystem and kernel code, is represented before assembly/linking.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/gc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/list.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/list.c

This file implements formatted printing for amd64 compiler backend objects. `listinit` installs format handlers for opcodes, operands, programs, registers, symbols, and bitsets.

`Pconv` renders `Prog` instructions, with special cases for `DATA` and `TEXT` pseudo-ops. `Aconv` maps opcode enum values through `anames`. `Dconv` formats amd64 operands including indirect addressing, branches, extern/static/auto/param symbols, constants, floating constants, string constants, and address constants. `Rconv` maps register numbers to printable register names. `Sconv` escapes 8-byte string constants. `Bconv` renders live-variable bitsets by symbol/offset.

This is not code generation itself, but it is essential for compiler diagnostics, debug modes, and register allocator tracing.

Filesystem relevance is build observability: when filesystem-related C code miscompiles or triggers backend diagnostics, these formatters make emitted instructions and operands understandable.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/machcap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/machcap.c

`machcap` reports whether the amd64 backend can handle a given compiler tree operation directly. It returns true for many integer and pointer arithmetic operations, casts, conditionals, logical operators, assignments, compound assignments, shifts, increment/decrement, comparisons, and supported multiply forms.

It treats small integer and vlong multiply as supported and permits common unary/binary operations on character, short, long, pointer, and vlong categories. Unsupported operations return false, allowing generic compiler code to avoid target-specific lowering paths.

Filesystem relevance is indirect: this is a target capability gate in the compiler. It affects which expressions from OS/filesystem code can be lowered directly by the amd64 backend versus requiring generic transformations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/machcap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/mul.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/mul.c

This file optimizes multiplication by integer constants. It searches for short sequences of shifts, adds, subtracts, and scaled-address calculations that replace a general multiply instruction.

`mulparam` analyzes a multiplier and chooses an algorithm from predefined forms. `mulgen1` uses cached multiplier parameters and emits selected instruction sequences. `genmuladd` builds amd64 indexed-address expressions to compute `base + index*scale` through `LEA`-style address generation. `shiftit` chooses an add for shift-by-one or a shift instruction otherwise.

If no compact sequence is found, `mulgen` falls back to normal multiply generation. Helpers such as `lowbit`, `m0`, `m1`, and `m2` support constant decomposition.

Filesystem relevance is performance-oriented: compiled filesystem and kernel code often contains offset, block, and structure-size arithmetic, and this backend can lower some constant multiplies into cheaper address arithmetic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/mul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/peep.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/peep.c

This file performs amd64 peephole optimizations over the register-flow graph built by `reg.c`. It first ensures the `Reg` graph has a node for every executable instruction, then repeatedly applies local copy and instruction simplifications.

Main optimizations include copy propagation for register-to-register moves, substitution propagation to expose removable moves, collapse of repeated sign/zero extension moves, and conversion of add/sub by one into inc/dec when flags are not needed. `needc` prevents transformations that would break carry-dependent instructions.

The copy analysis classifies instruction use of operands with `copyu`: read-only, set-only, read-alter-write, use-and-set, or untouched. It handles special amd64 constraints for `AX`/`DX` division, `CX` shifts/repeats, string instructions, calls, returns, and branch targets.

`excise` turns eliminated instructions into `NOP`, later removed by register optimization cleanup.

Filesystem relevance is compiled-code quality. Kernel/filesystem routines can be sensitive to instruction count, and these simple backend optimizations reduce redundant moves without changing source code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/peep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/reg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/reg.c

This is the amd64 compiler register allocator and global data-flow optimizer. It builds a control-flow graph from emitted `Prog` instructions, identifies variable references, computes branches, detects loops, propagates liveness, selects register-allocation regions, paints variables into registers, inserts loads/stores, runs peephole optimization, recalculates PCs, fixes branches, and removes NOPs.

`mkvar` maps addressable autos, params, statics, and externs into bitset variables, while marking address-taken or punning cases as unsafe. `prop` propagates references and call-live sets backward. `synch` computes register/memory divergence forward. `loopit` uses reverse postorder and approximate dominators to weight loops.

`paint1` scores profitable regions, `paint2` determines unavailable registers, `allreg` chooses integer or XMM registers, and `paint3` rewrites operand addresses to selected registers. `addmove` inserts memory/register synchronization moves.

The allocator reserves architectural registers such as stack, return, argument, and external registers, and handles special instruction register uses.

Filesystem relevance is high at the build level: this determines register quality for all amd64 Plan 9 C code, including filesystem code paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/reg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/sgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/sgen.c

This file performs statement/tree complexity analysis and addressability rewriting for the amd64 backend.

`xcom` computes each node’s `complex` and `addable` classifications. It recognizes constants, names, registers, address-of, indirection, pointer addition, indexed addressing, shifts usable as scale factors, multiplication/division/modulo by powers of two, compound assignments, function calls, casts, comparisons, and commutable operations.

The addressability model encodes Plan 9 addressing forms: globals/statics, autos/params, constants, dereferenced constants, address constants, stack addresses, and amd64 base+index*scale addressing. `indx` extracts base, index, and scale for generated `OINDEX` nodes.

`noretval` marks no-return-value cases with NOPs targeting integer and floating return registers. `commute` and `indexshift` help canonicalize trees for cheaper code generation.

Filesystem relevance is target lowering quality. This file decides when filesystem/kernel expressions can become direct amd64 memory operands or addressing modes rather than extra instructions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/sgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/swt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/swt.c

This file handles switch lowering, bitfield access, string/data emission helpers, and final object output support.

`swit1` emits a binary-search comparison tree for switch cases, using direct linear compares for small case counts. `bitload` and `bitstore` load, mask, shift, merge, and store C bitfields while preserving signedness and unsigned extraction behavior.

`outstring` buffers string literals into `ADATA` records of `NSNAME` chunks. `gextern` emits global/static initialization data, converting address-like operands into `D_ADDR` records where needed.

`outcode`, `zname`, `zaddr`, and `outhist` write the compiler’s in-memory `Prog` list into Plan 9 object format, including source history, symbol table entries, compact address fields, 64-bit offsets, floating constants, and string constants.

The file also defines target alignment behavior for structs, arguments, and autos. Filesystem relevance is object generation and ABI layout: C structures and globals in OS/filesystem code rely on these size/alignment and object-emission rules.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/swt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/sys.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/sys.c

This small file provides syscall stubs used by the amd64 C compiler support environment. It defines `_sysargs`, declares `_callsys`, and wraps selected Plan 9 syscalls: `getpid`, `pread`, `pwrite`, `close`, `open`, `create`, `_exits`, `dup`, `errstr`, `brk_`, and `sbrk`.

Each wrapper fills `_sysargs` with a syscall number and arguments, then calls `_callsys`. `sbrk` uses a private negative selector rather than a normal syscall number, matching the surrounding toolchain support conventions.

Filesystem relevance is direct for hosted compiler/tool execution: `open`, `create`, `pread`, `pwrite`, and `close` are the filesystem I/O primitives the compiler runtime uses to read sources and emit objects.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/sys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/txt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/txt.c

This is the amd64 compiler backend’s instruction emission and ABI helper file. `ginit` initializes target state, reserved registers, special nodes, string/rathole symbols, return nodes, and type capability arrays. `gclean` validates register release, flushes string data, emits globals, appends `AEND`, and writes object output.

It implements argument placement (`gargs`, `garg1`, `regaalloc`, `regaalloc1`), temporary stack allocation (`regsalloc`), register allocation/free helpers, return-register selection, address conversion (`naddr`), instruction creation (`gins`), pseudo-op creation, branch generation, and branch patching.

`gmove` is a major conversion/move engine. It handles loads, stores, integer extension/truncation, pointer/vlong moves, float/integer conversions, unsigned-to-float corner cases, float-to-float moves, zero floating constants, and same-register no-ops.

`gopcode` maps compiler tree operations to amd64 opcodes, including integer, pointer, floating, shift, comparison, call, multiply, divide, and modulo forms.

The file also defines target type widths, legal cast masks, external register allocation, small constant checks, and structure/argument alignment policy.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6c/txt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6l/asm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6l/asm.c

This file writes final amd64 linked output. `asmb` emits text, data, symbols, line tables, dynamic relocation data, and the executable header. It supports Plan 9 format (`HEADTYPE 2`) and ELF32/ELF64 (`HEADTYPE 5/6`) output.

The text pass walks `firstp`, verifies phase consistency between expected and assigned PCs, calls `asmins` for instruction encoding, flushes the output buffer, and optionally prints assembly bytes under debug. It handles dynamic-load-module relocation state while emitting text.

`datblk` builds zero-filled data blocks and overlays `ADATA` initializers, detecting overlapping initialization. It supports floating constants, string constants, integer constants, and address constants. Address constants against symbols are adjusted by symbol values and `INITDAT`; dynamic modules record relocations via `dynreloc`.

The header pass writes Plan 9 magic, text/data/bss/symbol sizes, entry value, stack pointer table size, line table size, and 64-bit entry address, or delegates to ELF writers.

Filesystem relevance is executable image construction: linked filesystem/kernel binaries depend on correct text/data layout, symbol emission, relocation, and file-format headers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6l/asm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6l/compat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6l/compat.c

This file supplies simple allocation and compatibility helpers for the amd64 linker. It implements a hunk-based `malloc`, `calloc`, no-op `free`, and unsupported `realloc`. Allocation rounds to 8-byte alignment and pulls memory from linker hunks via `gethunk`.

`mysbrk` delegates to `sbrk`, and `setmalloctag` is a no-op compatibility stub. `fileexists` checks whether `stat` succeeds, deliberately treating an oversized stat result as still proving file existence.

Filesystem relevance is practical: `fileexists` is used by library path resolution, and the allocation wrappers support the linker’s object/archive ingestion without relying on a conventional allocator.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6l/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6l/l.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6l/l.h

This is the central header for the amd64 linker `6l`. It imports Plan 9 headers, amd64 object constants, and ELF definitions, then declares linker data structures, constants, globals, and function prototypes.

Key structures are `Adr` for linker operands, `Prog` for linked instructions, `Auto` for automatic/history metadata, `Sym` for linker symbols, `Optab` for instruction encoding patterns, and `Movtab` for move encodings. Symbol types include text, data, bss, cross-reference, file, constant, undefined import, import, and export.

The header defines instruction encoding classes (`Y*`, `Z*`), prefix constants, REX bit flags, relocation bit packing, I/O buffers, global layout values (`HEADR`, `INITTEXT`, `INITDAT`, `INITRND`), symbol/hash tables, text/data lists, history state, dynamic module/import/export state, endian byte-order arrays, and output buffers.

Its prototypes cover object loading, archive/library handling, symbol lookup, patch/follow/layout passes, data output, ELF/Plan 9 assembly, dynamic relocation, profiling insertion, diagnostics, and formatting.

Filesystem relevance is build-system infrastructure: this is the linker contract for turning Plan 9 object files into bootable/runnable OS binaries.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6l/l.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6l/list.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6l/list.c

This file implements formatted diagnostics and instruction listing for the amd64 linker. It installs formatters for registers, opcodes, operands, string constants, and `Prog` records.

`Pconv` prints instructions with line numbers and special formatting for `TEXT`, `DATA`, `INIT`, and `DYNT`. `Dconv` formats operands, including branch targets resolved through `pcond`, extern/static/auto/param symbols, constants, floating constants, string constants, and address constants. `Rconv` maps register numbers to names. `Sconv` escapes string constants.

`diag` reports linker errors in the context of the current text symbol and exits after too many errors. This makes object/link failures tied to the function being processed rather than only the raw object file.

Filesystem relevance is diagnostic: it helps debug failed OS/filesystem builds by rendering linker instructions, operands, and symbol contexts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6l/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6l/obj.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6l/obj.c

This is the main amd64 linker driver and object/archive reader. `main` parses linker options, configures output format and segment addresses, initializes opcode coverage and register encoding tables, creates the output file, loads object files, resolves libraries, handles export/import or dynamic module modes, patches/follows code, lays out data and stack offsets, optionally inserts profiling, spans instructions, and emits the final binary.

`objfile` handles regular object files and Plan 9 archives. For archives, it reads `__.SYMDEF`, searches members needed by unresolved `SXREF` symbols, and loads only required objects, repeating until no more references resolve. `loadlib`, `addlibpath`, and `findlib` manage explicit and autolib search paths.

`ldobj` parses `.6` object streams: `ANAME`/`ASIGNAME` symbol records, source history, `TEXT`, `DATA`, `GLOBL`, `DYNT`, `INIT`, `MODE`, `AEND`, branch offsets, duplicate text, float constants converted into data literals, and auto/param metadata. It maintains symbol versions for statics and source history path compression.

The file also implements hunk allocation, instruction allocation/copy/append helpers, profiling insertion, byte-order initialization, IEEE conversions, undefined-import marking, and import/export list reading.

Filesystem relevance is strong: this is the code that reads object and archive files from the filesystem and emits final Plan 9/ELF binaries for OS components.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6l/obj.c -->