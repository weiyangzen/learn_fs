# Group Research: group_38_9front_sources_os_plan9_9front_sys_src_cmd_8l_list_c_sources_os_plan9_b3c4748e1bf9

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8l/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8l/list.c

Formatting and diagnostics support for the 386 linker `8l`.

Key contents:
- `listinit` installs Plan 9 `fmt` converters for registers, opcodes, addresses, short strings, and full `Prog` instructions.
- `Pconv` formats linker instructions, with special forms for `TEXT`, `GLOBL`, `DATA`, `INIT`, and `DYNT`.
- `Dconv` formats 386 operands: indirect registers, branches, extern/static/auto/param symbols, constants, floating constants, string constants, and address constants.
- `Rconv` maps Plan 9 386 register/address enum values to textual register names, including x87, MMX, XMM, control/debug/task registers.
- `Sconv` escapes fixed-width string constants.
- `diag` reports linker errors in the current text symbol context, counts errors, and exits after too many unless debug `A` is set.

Filesystem relevance: indirect. This is build-tool listing/error infrastructure for 9front’s 386 linker, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8l/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8l/obj.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8l/obj.c

Main driver and object/archive loader for the Plan 9 386 linker `8l`.

Key contents:
- `main` parses linker flags, selects executable header format, initializes opcode lookup/operand class coverage/register maps, reads object files, loads libraries, patches control flow, lays out data/text, optionally injects profiling, spans instructions, initializes data relocations, assembles output, and checks undefined symbols.
- Supports Plan 9, COFF-like Unix, old “garbage unix”, DOS `.COM`, fake DOS `.EXE`, and ELF header presets.
- `isobjfile` distinguishes object/archive inputs for option parsing around import/export lists.
- `loadlib` repeatedly scans autolibraries until unresolved external references stop being resolved.
- `objfile` handles plain object files and Plan 9 archive symbol tables, loading only archive members needed by unresolved symbols.
- `ldobj` decodes `.8` object records, symbol/name records, history records, text/data/global pseudo-ops, dynamic import/export records, branch offsets, and floating constants materialized into data symbols.
- `zaddr` decodes serialized object operands and collects auto/param metadata for symbol tables.
- `addlib`, `addhist`, `histtoauto`, and `collapsefrog` manage Plan 9 file-history/autolib records.
- `doprof1` and `doprof2` insert simple counter profiling or `profin/profout` calls.
- `nuxiinit`, `ieeedtof`, and `ieeedtod` support host byte order and floating constant conversion.
- `readundefs`, `import`, `export`, and helpers implement dynamically loadable module import/export metadata.

Filesystem relevance: indirect build infrastructure. It consumes and emits binary/object files and libraries but does not implement filesystem semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8l/obj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8l/optab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8l/optab.c

Operand-pattern and opcode encoding table for the 386 linker/assembler backend.

Key contents:
- Defines many `uchar` operand pattern tables mapping source/destination classes to encoding recipes, including integer, branch, stack, x87, MMX, SSE/XMM, segment/control-register, and pseudo-op forms.
- `optab[]` maps every 386 opcode enum to an operand table, required instruction prefix, and concrete opcode bytes or ModRM extension bits.
- Covers core 386 operations, condition branches/sets, string instructions, privileged/control instructions, x87 floating point, MMX/SSE packed operations, and Plan 9 pseudo-ops such as `TEXT`, `DATA`, `GLOBL`, `WORD`, `LONG`, `BYTE`, `END`.
- Ends with `opindex[ALAST+1]`, populated by `obj.c` for fast opcode lookup.

Filesystem relevance: indirect. It is architecture encoding metadata for building Plan 9 binaries.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8l/optab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8l/pass.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8l/pass.c

Middle linker passes for data layout, branch patching, control-flow ordering, stack adjustment, undefined checks, and dynamic symbol table generation.

Key functions:
- `dodata` validates data initializers, groups small data, lays out data/BSS, optionally pads with BSS to an 8 KiB boundary, and defines `bdata`, `edata`, and `end`.
- `patch` resolves calls/branches to text symbols, marks unresolved dynamic imports, builds forward links via `mkfwd`, and collapses jump chains with `brloop`.
- `follow`/`xfol` reorder text to improve fallthrough, copy short instruction sequences to avoid jumps, and invert conditional branches when profitable.
- `dostkoff` computes function frame/become sizes, adjusts call frames for `BECOME`, rewrites auto/param offsets, inserts stack adjustments, and checks push/pop balance.
- `doinit` resolves data initializers referencing symbols to final constants.
- `undef` reports unresolved symbols.
- `import`, `export`, `newdata`, `undefsym`, and `ckoff` build import/export metadata for dynamic modules.
- `atolwhex` parses decimal, octal, and hex numeric command arguments.

Filesystem relevance: indirect. It lays out executable images and symbol data, not runtime filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8l/pass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8l/span.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8l/span.c

Instruction sizing, final text address assignment, symbol/line table emission, x86 machine-code encoding, and dynamic relocation output for `8l`.

Key functions:
- `span` iteratively sizes instructions, especially variable-width branches, until text PCs stabilize; it also aligns data start with `INITRND` and defines `etext`.
- `asmsym` and `putsymb` emit Plan 9 symbol table records for text, data, BSS, file history, frames, autos, and params.
- `asmlc` emits compressed line number tables.
- `oclass`, `prefixof`, `asmidx`, `asmand`, and `vaddr` classify operands and encode ModRM/SIB/displacement/address forms.
- `doasm` uses `optab` recipes to emit actual instruction bytes, including immediate, branch, call, MMX/SSE media, x87, and pseudo data encodings.
- `ymovtab` handles special move-family encodings not expressible in the regular optab pattern table.
- Includes byte-register workaround logic that temporarily exchanges registers when 386 byte instructions cannot address chosen registers.
- `dynreloc` and `asmdyn` collect sorted dynamic relocations and emit import/export relocation metadata for dynamically loadable modules.

Filesystem relevance: indirect. It serializes final executable bytes and metadata but has no filesystem algorithms.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8l/span.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9660srv/9660srv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9660srv/9660srv.c

Core ISO9660 filesystem implementation behind the `9660srv` 9P server. It provides read-only file and directory operations for ISO9660, High Sierra, Joliet, Plan 9 ISO extensions, and Rock Ridge/SUSP.

Key functions:
- Defines `isosub`, the `Xfsub` operation vector used by the generic 9P dispatcher.
- `iattach` scans volume descriptors starting at sector 16, detects ISO9660/High Sierra/Joliet/Plan 9 variants, validates block size, records root directory state, and detects SUSP/Rock Ridge continuation/extension data.
- `iwalk`, `iwalkup`, and `opendotdot` implement directory traversal using directory records and special `.`/`..` entries.
- `iopen`, `ireaddir`, `iread`, `istat` implement read-only open, directory listing, file reads, and stat conversion. Create/write/remove/wstat reject with permission errors.
- `getdrec`, `ungetdrec`, and `newdrec` manage sequential directory-record reading and per-fid `Isofile` private state.
- `rzdir` converts raw ISO directory records into Plan 9 `Dir`, including qids, modes, uid/gid, names, timestamps, file lengths, Plan 9 extension metadata, Joliet UTF-16 names, Rock Ridge `PX` modes and `NM` names, and ISO version stripping.
- `getcontin` follows SUSP/Rock Ridge continuation areas.
- `fakemax` treats the ISO maximum 31-bit file size as an effectively vast file length.
- `l16`, `l32`, `gtime`, `rdate`, and `nstr` decode on-disc values and diagnostics.

Filesystem relevance: direct. This is a complete read-only ISO-family filesystem implementation exposed through Plan 9 9P.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9660srv/9660srv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9660srv/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9660srv/dat.h

Shared data definitions for `9660srv`.

Key contents:
- Defines sector size `2048` and maximum name size `256`.
- `Iobuf` and `Ioclust` describe cached sector buffers grouped into clusters, including device, address, busy count, LRU links, and metadata/data cache tag.
- `Xdata` tracks an underlying ISO image/device file, its qid/type/device identity, open fd, and reference count.
- `Xfsub` is the filesystem operation interface used by the 9P request layer.
- `Xfs` represents an attached filesystem instance, including backing device, operation vector, reference count, SUSP/Rock Ridge/Plan 9 flags, root qid, and private parser state.
- `Xfile` represents a fid, with flags, qid, filesystem reference, and per-fid private `Isofile` state.
- Declares common error strings, globals, options disabling Joliet/Plan 9/Rock Ridge, and error stack state.

Filesystem relevance: direct. It defines the in-memory object model for the ISO 9P filesystem server.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9660srv/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9660srv/data.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9660srv/data.c

Global data and filesystem backend registration for `9660srv`.

Key contents:
- Defines standard error strings: nonexistent file, permission denied, no filesystem specified, and authentication failure.
- Sets default service name `9660` and default backing file pointer.
- Declares external `isosub` and installs it as the only entry in `xsublist`.

Filesystem relevance: direct but small. It wires the ISO backend into the generic 9P server.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9660srv/data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9660srv/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9660srv/fns.h

Function declarations and error-stack macros for `9660srv`.

Key contents:
- Declares shared helpers for logging, allocation, error raising, buffer cache operations, backing-device lookup, server panic, filesystem refcounting, directory display, fid lookup, and `Dir` name-buffer setup.
- Defines `waserror()` and `poperror()` wrappers around the global `jmp_buf` stack.

Filesystem relevance: direct support header for the ISO 9P filesystem server.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9660srv/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9660srv/iobuf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9660srv/iobuf.c

Clustered sector buffer cache for `9660srv`.

Key behavior:
- Uses `BUFPERCLUST=64`, so each cache cluster covers 128 KiB of ISO sectors.
- Default `NCLUST=64`, configurable through global `nclust`.
- `iobuf_init` allocates all clusters, per-sector `Iobuf` descriptors, and backing data with `sbrk`, then links clusters into an LRU list.
- Reserves roughly one-eighth of clusters for metadata-tagged reads so directory data is less likely to be evicted by large sequential file reads.
- `getbuf` maps a sector number to its cluster, reads the cluster on miss, and returns the per-sector buffer.
- `putbuf` releases a buffer and moves its cluster to the LRU head.
- `purgebuf` invalidates all cached clusters for a closing backing device.
- `xread` performs contiguous cluster reads from the ISO image/device and records how many sectors were actually read.

Filesystem relevance: direct. This is the read cache used for ISO directory and file data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9660srv/iobuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9660srv/iso9660.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9660srv/iso9660.h

On-disc ISO9660/High Sierra structure definitions and per-file parser state.

Key contents:
- Defines `VOLDESC` sector 16 and descriptor type IDs.
- Provides endian-annotated byte-array typedefs for ISO fields stored little-endian, big-endian, or both.
- `Voldesc` overlays raw 2048-byte sectors with ISO9660 `CD001` boot/primary/supplementary descriptors and High Sierra `CDROM` descriptors.
- `Drec` models ISO directory records, including record length, extent address, size, timestamp, flags, volume sequence, name length/name, and High Sierra flag alias.
- `Isofile` stores parsed format, logical block size, current directory offset, last directory-record delta, Plan 9 directory read offset, and current directory record.

Filesystem relevance: direct. It defines the disk format structures consumed by the ISO server.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9660srv/iso9660.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9660srv/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9660srv/main.c

9P server front end for `9660srv`.

Key functions:
- `main` parses options, initializes buffer cache/backends, optionally posts a pipe fd in `/srv/<name>`, forks into the background, and starts the 9P I/O loop.
- Options disable Plan 9 extensions (`-9`), Joliet (`-J`), Rock Ridge (`-r`), set cache cluster count (`-c`), set default image/device (`-f`), use stdio (`-s`), and enable verbose tracing (`-v`).
- `io` reads 9P messages, decodes `Fcall`, dispatches through `fcalls[]`, catches server errors through the local jump stack, and writes replies.
- Implements request handlers for version, auth, flush, attach, walk, open, create, read, write, clunk, remove, stat, and wstat.
- `rattach` opens/refs the backing image and lets registered backends try to attach; currently only ISO.
- `doclone` and `rwalk` carefully clone/restores fid state for partial walks.
- `rread` dispatches to directory or file read based on qid type.
- Writes, creates, removes, and wstat are rejected for this read-only filesystem.
- Utility functions include `error`, `nexterror`, `ealloc`, `setnames`, `openflags`, `showdir`, `chat`, and `panic`.

Filesystem relevance: direct. It exposes the ISO backend as a Plan 9 9P file server.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9660srv/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9660srv/xfile.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9660srv/xfile.c

Backing-device and fid lifetime management for `9660srv`.

Key functions:
- `getxdata` opens the requested image/device, validates it is a plain file, deduplicates by qid/type/dev identity, and reference-counts shared backing data.
- `putxdata` decrements backing-device refs, purges cached sectors, closes the fd, and frees the name when no attachments remain.
- `refxfs` manages attached filesystem references and releases backing data/private parser state when the filesystem refcount reaches zero.
- `xfile` manages fid lookup, allocation, cleaning, clunking, hash-bucket move-to-front, and freelist reuse.
- `clean` drops filesystem refs, frees per-fid private state, clears open flags, and resets qid.

Filesystem relevance: direct. It manages 9P fid and mounted-image lifetimes for the ISO filesystem server.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9660srv/xfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9a/a.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9a/a.h

Shared header for the PowerPC64 assembler `9a`.

Key contents:
- Includes Plan 9 libc/bio headers, PowerPC64 object interface `../9c/9.out.h`, and common compiler compatibility support.
- Defines assembler limits for symbols, buffers, include stack, history, macro count, and allocation hunks.
- Defines `Sym`, `Io`, `Gen`, and `Hist` used for symbols/macros, input stack, assembled operands, and file history records.
- Declares global lexer/parser/assembler state including include paths, input buffers, symbol table, current line, pass number, output file, pc, debug flags, and `Biobuf` output.
- Declares parser, lexer, macro preprocessor, object emission, history emission, error, include, and portability wrapper functions.
- `Gen` supports symbol, offset, type, register, index register, name class, mask, float value, and 8-byte string literal operands.

Filesystem relevance: indirect. It is assembler infrastructure for building PowerPC64 Plan 9 code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9a/a.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9a/a.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9a/a.y

Yacc grammar for the PowerPC64 assembler `9a`.

Key behavior:
- Parses labels, variable assignments, `SCHED`/`NOSCHED`, and assembler instructions.
- Covers integer/byte loads and stores, floating loads/stores, FPSCR moves, condition-register moves, special-register moves, arithmetic/logical/shift operations, multiply-accumulate, branches/traps, floating operations, comparisons, rotate/mask operations, indexed load/store/move/op forms, no-ops, `WORD`/`DWORD`, `TEXT`, `GLOBL`, `DATA`, `RETURN`, and `END`.
- Builds `Gen` operands for registers, floating registers, condition registers, special registers, FPSCR fields, immediates, string/floating constants, names, static symbols, branch targets, register-indirect and indexed addressing.
- Branch grammar supports direct labels, PC-relative constants, branch-to-address, branch-to-LR/CTR-like special registers, condition fields, and BO/BI-style condition operands.
- `mask` rule turns PowerPC rotate-mask start/end pairs into a bitmask constant.
- Expression grammar handles unary signs/complement and arithmetic/bitwise operators.

Filesystem relevance: indirect assembler frontend for the PowerPC64 toolchain.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9a/a.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9a/lex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9a/lex.c

Main program, keyword table, object writer, and lexer integration for the PowerPC64 assembler `9a`.

Key contents:
- `main` configures target `thechar='9'`, `thestring="power64"`, handles `-o`, `-D`, and `-I`, and can assemble multiple files in parallel on non-Windows systems using `NPROC`.
- `assemble` derives output file names, configures include paths, creates output, runs two assembler passes, emits history on pass 2, and writes final `AEND`.
- Large `itab[]` maps assembler mnemonics, registers, special registers, condition registers, pseudo-ops, and 64-bit PowerPC instructions to parser tokens and opcode enum values.
- `cinit` initializes null operands, symbol table, keyword symbols, input state, and working directory path.
- `zname` and `zaddr` serialize symbol names and operands into Plan 9 object format, including 64-bit constants, string constants, and IEEE floating constants.
- `outcode` and `outgcode` write two-operand and three-operand instruction records, manage symbol slots, line numbers, scheduler flags, and PC advancement.
- `outhist` emits file history records as `ANAME`/`AHISTORY`.
- Pulls in shared lexer, macro processor, and compatibility bodies from `../cc`.

Filesystem relevance: indirect. It emits object files used to build 9front binaries.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9a/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/9.out.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9c/9.out.h

PowerPC64 object/instruction interface header shared by `9a`, `9c`, linker tooling, and related code.

Key contents:
- Defines symbol/name sizes, register count, profiling/duplicate flags, and PowerPC64 register roles.
- Assigns general register conventions: zero/SP/SB/return/argument registers, compiler variable range, external register range, and linker temp.
- Assigns floating register conventions, including return, variable, external, and constant registers.
- `enum as` is the opcode namespace for PowerPC/PowerPC64 instructions plus Plan 9 pseudo-ops (`TEXT`, `DATA`, `GLOBL`, `HISTORY`, `NAME`, `END`, dynamic import/export records).
- Includes 32-bit operations, optional operations, 64-bit operations, pseudo remainder/division operations, synchronization/cache/TLB instructions, and atomic indexed load/store forms.
- Defines operand/address types such as extern/static/auto/param names, branch, offset register, constants, floating/string constants, GPR/FPR/CREG/FPSCR/MSR/SPR/DCR, file history, and 64-bit constants.
- Defines SPR values for XER/LR/CTR and the archive symbol header name `__.SYMDEF`.
- Provides Plan 9 split IEEE floating representation `Ieee`.

Filesystem relevance: indirect. It is architecture ABI/object metadata for building PowerPC64 OS/userland code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/9.out.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/bits.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9c/bits.c

Bitset helpers for the PowerPC64 compiler optimizer.

Key contents:
- Active helpers include `bany`, `bnum`, `blsh`, and `Bconv`.
- `bany` tests whether any bit is set in a `Bits`.
- `bnum` returns the first set bit index and diagnoses empty input.
- `blsh` creates a one-bit `Bits`.
- `Bconv` formats bitsets as variable names or constant offsets using the optimizer’s `var[]` table.
- Older bitset union/intersection/not/equality/set helpers are present but commented out.

Filesystem relevance: indirect compiler optimizer utility code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/bits.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/cgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9c/cgen.c

Main expression, boolean, lvalue, and aggregate code generator for the PowerPC64 C compiler backend.

Key functions:
- `cgen` lowers scalar AST nodes into backend instructions, handling assignments, bitfields, arithmetic/logical/shift operations, compound assignments, address/indirection, calls, comparisons, casts, comma/conditional expressions, and pre/post increment/decrement.
- Uses PowerPC-friendly immediate paths: signed 16-bit forms for add/sub and unsigned 16-bit/high-half forms for logical/shift-like operations.
- Converts `x ^ -1` to complement and delegates constant multiply optimization to `mulcon`.
- Handles function calls with argument generation, indirect-call temporaries, and return register moves.
- `reglcgen` and `lcgen` generate lvalue addresses, folding constant offsets into indirect operands when possible.
- `boolgen` and `bcgen` lower boolean expressions and comparisons into branches or materialized `0/1`.
- `sugen` handles structures/unions/vlong aggregates, struct literals, assignment, function returns through hidden pointers, conditionals, comma expressions, and rathole temporaries.
- `layout` copies aggregate words with small unrolled sequences or counted loops.

Filesystem relevance: indirect. It is compiler backend code used to build filesystem and OS components, not filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/cgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/gc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9c/gc.h

Primary PowerPC64 backend header for `9c`.

Key contents:
- Defines target C type sizes: 32-bit `long`, 64-bit pointers/vlong/double, 8-bit char, 16-bit short, 32-bit int/float.
- Defines backend structures: `Adr`, `Prog`, `Case`, `C1`, `Multab`, `Hintab`, `Var`, `Reg`, and `Rgn`.
- `Prog` supports `from`, optional third operand `from3`, destination `to`, link, source line, opcode, and register field.
- `Reg` is the optimizer CFG/liveness node with use/set bitsets, reference/call liveness, register divergence, loop weight, CFG links, and attached instruction.
- Declares extensive global compiler/backend state for code generation, switch lowering, register optimization, string/rathole handling, and variable tables.
- Defines register optimizer constants and macros for load/store bit computations.
- Declares cross-file entry points for codegen, text emission, switch/bitfield support, listing, register optimization, peephole optimization, and 64-bit helpers.
- Installs Plan 9 `#pragma varargck` contracts for custom formatters.

Filesystem relevance: indirect backend contract for the PowerPC64 compiler.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/gc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9c/list.c

Instruction, operand, symbol-name, string, and bitset formatting for the PowerPC64 compiler backend.

Key functions:
- `listinit` installs formatters for opcodes, programs, strings, names, operands, and bitsets.
- `Pconv` formats `Prog` instructions, including special `DATA` and `TEXT` size/reg fields and explicit GPR/FPR register fields.
- `Aconv` maps opcode enum values to `anames`.
- `Dconv` formats operands including constants, offset-register operands, GPR/FPR/CREG, branches, floating constants, and string constants.
- `Sconv` escapes 8-byte string constants.
- `Nconv` formats symbolic extern/static/auto/param names and raw offsets.
- Includes its own `Bconv` implementation for optimizer bitsets using 64-bit offsets.

Filesystem relevance: indirect debugging/listing support for compiler-generated code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/machcap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9c/machcap.c

Target capability predicate for the PowerPC64 C compiler backend.

Behavior:
- Returns true for null probe calls.
- Accepts integer/pointer/vlong multiply and assignment multiply when the node type is in `typechlv`.
- Accepts add/sub/and/or/xor/shifts when the left operand is an integer-like scalar.
- Accepts casts, conditionals, comma/list/logical nodes, compound assignments, shifts, increments/decrements, and all standard comparisons.
- Rejects operations not directly supported by this backend path, such as unary negation and complement here.

Filesystem relevance: indirect compiler target capability metadata.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/machcap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/mul.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9c/mul.c

Constant-multiplication recipe search for the PowerPC64 compiler backend.

Key functions:
- `mulcon0` normalizes constants, checks a small cache, consults an exception hint table, searches shift/add/sub recipes up to a bounded length, and handles trailing power-of-two factors recursively.
- `docode` interprets recipe strings into concrete virtual-register operations and validates that the sequence produces the requested constant.
- `gen1`, `gen2`, and `gen3` recursively search the space of shifts, adds, and subtracts.
- The recipe encoding uses letters for shifts and `+`/`-` for arithmetic between two virtual registers.
- `hintab` lists constants the search misses or would not find within the desired bounds; `hintabsize` exports its length.

Filesystem relevance: indirect compiler optimization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/mul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/peep.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9c/peep.c

Peephole optimizer for PowerPC64 compiler output.

Key behavior:
- Completes the `Reg` chain for instructions inserted after global register optimization.
- Repeatedly eliminates redundant register moves through `copyprop` and `subprop`.
- Canonicalizes zero constants/register-zero uses when `R0ISZERO` permits it.
- Removes redundant extension/move chains such as `MOVB/MOVH/MOVW x,R; same R,R`.
- Folds `CMP R,$0` followed by a conditional branch into a condition-code-setting arithmetic/logical instruction when safe.
- `copyu` classifies instruction effects on a register as use, set, read-alter-write, or untouched across integer, floating, compare, branch, call, return, and text instructions.
- Helpers `copyas`, `copyau`, `copyau1`, `copysub`, and `copysub1` detect and substitute direct/indirect register references.
- `uniqp`/`uniqs` restrict transformations to unique-predecessor/successor flow where required.
- Floating condition-code folding cases are present but disabled in comments.

Filesystem relevance: indirect compiler optimizer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/peep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/reg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9c/reg.c

Global register optimizer for the PowerPC64 compiler backend.

Key phases in `regopt`:
- Builds `Reg` CFG nodes from emitted instructions while skipping data/name pseudo-ops and assigning synthetic PCs.
- Computes use/set bitsets for variables with `mkvar`, tracks externs, params, constants, address-taken/punned variables, and register usage.
- Resolves branch destinations into CFG successor/predecessor links using skip links.
- Computes loop weights via reverse postorder, approximate dominators, loop-head detection, and loop marking.
- Propagates variable references and call-live information backward with `prop`.
- Propagates register/variable divergence forward with `synch`.
- Identifies profitable allocation regions with `paint1`, computes occupied register masks with `paint2`, selects hardware registers via `allreg`, and rewrites code with `paint3`.
- Inserts load/store moves around allocated regions with `addmove`.
- Runs peephole optimization, recalculates PCs, fixes branch targets, removes NOPs, and recycles `Reg` nodes.
- `RtoB`/`BtoR` and `FtoB`/`BtoF` map allocatable GPR/FPR ranges into optimizer bit masks.

Important constraints:
- Avoids optimizing variables with unsafe punning/address identity or excess variable-table pressure.
- Distinguishes integer and floating register classes and avoids impossible GPR/FPR move patterns.

Filesystem relevance: indirect compiler optimizer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/reg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/sgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9c/sgen.c

High-level statement/codegen preparation support for the PowerPC64 C compiler backend.

Key functions:
- `noretval` emits dummy uses of integer/floating return registers when a function must not return a value of those classes.
- `xcom` computes node addressability and register complexity, classifying constants, names, registers, indirect registers, address-of, indirection, and address arithmetic.
- Rewrites multiply/divide/modulo by powers of two into shifts or masks for unsigned cases and assignment variants.
- Calls `simplifyshift` after shift-generating rewrites.
- Marks function calls as high complexity (`FNX`).
- Normalizes immediate-friendly comparisons and commutative arithmetic by moving constants to the right side.
- The file is the machine-specific expression classification layer feeding later `cgen` decisions.

Filesystem relevance: indirect compiler code-generation support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/sgen.c -->