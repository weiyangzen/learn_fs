# Group Research: group_39_9front_sources_os_plan9_9front_sys_src_cmd_9c_swt_c_sources_os_plan9__150781b1f3b4

Scope: `Docs/research_subset_a.md`, covering the 9front source tree under `sources/os/plan9/9front`.

This group covers three related areas: the Power64 `9c` compiler backend helpers, the Power64 `9l` linker/assembler pipeline, and the `9nfs` RPC/NFS-to-9P bridge utilities.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/swt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9c/swt.c

This file contains backend support routines for the Plan 9 C compiler targeting Power64. It handles switch-code lowering, bitfield load/store generation, static data emission, constant-multiply strength reduction, object-file symbol/address serialization, source-history emission, and target-specific alignment.

Key routines:
- `swit1` and `swit2` generate switch dispatch code. Small switch sets become linear equality tests; larger sets become binary-search compare/branch trees.
- `bitload` and `bitstore` extract and update C bitfields using shifts, masks, and temporary registers.
- `outstring`, `sextern`, and `gextern` emit string/static initializer data through `ADATA` pseudo-instructions.
- `mulcon` uses `Multab` recipes from `mulcon0` to replace multiplication by constants with shifts/adds/subtracts where possible.
- `outcode`, `zwrite`, `zname`, and `zaddr` serialize compiler `Prog` instructions into the Plan 9 object format consumed by `9l`.
- `outhist` emits `AHISTORY` records for source path/line tracking, including Windows path normalization.
- `align` and `maxround` define target ABI alignment for structs, arguments, automatics, and big-endian parameter adjustment.

Important interactions:
- Depends heavily on global codegen state from `gc.h`: `firstp`, `lastp`, `p`, `pc`, `types`, `debug`, `symstring`, and string buffers.
- Emits object records compatible with `9l/obj.c` decoding.
- Uses Power64-specific object address classes such as `D_CONST`, `D_DCONST`, `D_SCONST`, `D_BRANCH`, and `D_EXTERN`.

Research notes:
- Switch lowering explicitly works around immediates outside signed 16-bit range by subtracting into a temporary before compare.
- 64-bit constants are split in `gextern` according to target endian behavior detected through `align(..., Aarg1)`.
- This file is part of the compiler-to-linker contract: mistakes here affect linker parsing and final relocation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/swt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/txt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9c/txt.c

This file is the main Power64 text/instruction emission layer for `9c`. It initializes backend state, manages registers and calling convention temporaries, maps compiler IR operations to Power64 assembly opcodes, and defines type widths/cast compatibility.

Key routines:
- `ginit` initializes target identity (`thechar='9'`, `thestring="power64"`), register reservations, standard constant/register nodes, pseudo symbols, and 64-bit helper state.
- `gclean` checks leaked registers, flushes pending string data, emits `AGLOBL` declarations, appends `AEND`, and calls `outcode`.
- `nextpc`, `gins`, `gopcode`, `gbranch`, `patch`, and `gpseudo` build the `Prog` stream.
- `gargs` and `garg1` evaluate and place call arguments, including struct-by-pointer and first-register-argument handling.
- `regalloc`, `regfree`, `regsalloc`, `regaalloc`, and `regaalloc1` implement simple backend register and stack argument allocation.
- `naddr` and `raddr` translate compiler `Node` values into assembler `Adr` operands.
- `gmove` emits type-aware moves and conversions, including integer/float conversions, memory loads/stores, immediate zero handling, and common floating constants.
- `sval`, `sconst`, `uconst`, and `exreg` classify immediate/register possibilities.
- `ewidth` and `ncast` define target type sizes and legal cast categories.

Important interactions:
- Produces Power64 `Prog` records consumed by `swt.c` object serialization and later by `9l`.
- Relies on reserved registers such as `REGZERO`, `REGTMP`, `REGSP`, `REGRET`, `FREGRET`, `FREGCVI`, and floating constants.
- Uses `typechlpv`, `typefd`, `typeu`, and `typesu` tables from the shared compiler frontend.

Research notes:
- Integer-to-float conversion is implemented with the classic `0x43300000` double-bias trick and includes unsigned adjustment for `TULONG`.
- Floating constants like 0, 0.5, 1, and 2 use pre-reserved floating registers.
- The backend treats `TVLONG`, `TUVLONG`, and `TIND` as 64-bit integer-like values via the `isv` macro.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9c/txt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/asm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9l/asm.c

This file writes the final linked output image. It emits text, data, symbol tables, line tables, optional dynamic relocation data, and binary headers for several Power64 output formats.

Key routines:
- `entryvalue` resolves the entry point from `INITENTRY`, accepting either numeric addresses or symbols.
- `asmb` is the top-level assembler writer. It writes text instructions through `asmout`, data blocks through `datblk`, symbols through `asmsym`, line tables through `asmlc`, optional dynamic data through `asmdyn`, and finally the output header.
- Header output supports boot/q.out/Plan 9/raw/ELF variants selected by `HEADTYPE`.
- `strnput`, `cput`, `wput`, `lput`, `llput`, and `cflush` implement buffered big-endian output.
- `asmsym` and `putsymb` emit Plan 9 symbol table entries for text, data, bss, file history, frames, autos, and parameters.
- `asmlc` encodes line-number deltas compactly.
- `datblk` materializes initialized data blocks from `ADATA`, `AINIT`, and `ADYNT` records, handling constants, strings, floats, endian maps, symbol-relative values, and dynamic relocations.

Important interactions:
- Calls `oplook` and `asmout` for instruction encoding.
- Consumes layout decisions made by `span` and `dodata`.
- Uses endian index arrays initialized by `nuxiinit` in `obj.c`.
- Calls `dynreloc` when data initializers reference symbols in dynamically loadable module mode.

Research notes:
- ELF output is 64-bit, big-endian PowerPC64.
- In DLM mode, data placement and relocation output are adjusted, and `HEADTYPE` is forced elsewhere to Plan 9 format.
- `datblk` detects overlapping initializers except for `AINIT`/`ADYNT`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/asm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/asmout.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9l/asmout.c

This file is the Power64 machine-code encoder for `9l`. It converts an already matched `Prog` plus `Optab` entry into one to five 32-bit instruction words or raw data words.

Key routines and structures:
- Opcode-construction macros such as `OPVCC`, `AOP_RRR`, `AOP_IRR`, `LOP_RRR`, `OP_BR`, `OP_BC`, and `OP_RLW` encode PowerPC instruction fields.
- `getmask`, `maskgen`, `getmask64`, and `maskgen64` validate and convert 32/64-bit masks for rotate-and-mask instructions.
- `asmout` handles `Optab.type` cases, including pseudo-ops, register moves, arithmetic/logical operations, memory loads/stores, branches, large constants, 64-bit constants, special registers, floating point, traps, compares, indexed forms, cache/TLB operations, and dynamic relocation forms.
- `oprrr`, `opirr`, `opload`, `oploadx`, `opstore`, and `opstorex` map assembler opcodes to PowerPC primary/extended opcodes.

Important interactions:
- Called from `asm.c:asmb` after instruction sizes and operand classes are fixed.
- Uses `regoff`/`vregoff` from `span.c` to obtain classified offsets.
- Calls `dynreloc` for DLM relocation records where required.
- Relies on `Optab.type` values defined by `optab.c`.

Research notes:
- Large constants are synthesized through `ADDIS`/`ORI`, temporary register use, and 64-bit rotate/insert forms.
- Conditional and unconditional branches validate alignment and displacement range.
- Several macro instructions, such as remainder, expand to multi-instruction sequences using `REGTMP`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/asmout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/cnam.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9l/cnam.c

This file defines `cnames`, the printable names for linker operand classes.

Key content:
- Maps `C_*` class enum values from `l.h` to strings such as `REG`, `FREG`, `SCON`, `LCON`, `SBRA`, `LAUTO`, `SEXT`, `LR`, `CTR`, `ADDR`, and `NCLASS`.

Important interactions:
- Used by `list.c:Rconv` for diagnostics and assembly listing output.
- Must stay aligned with the operand class enum in `l.h`.

Research notes:
- This is a pure diagnostic/listing support table; it has no code-generation logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/cnam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/compat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9l/compat.c

This file only includes shared linker compatibility headers.

Key content:
- Includes `l.h`.
- Includes `../cc/compat`.

Important interactions:
- Serves as a small compatibility bridge for non-native or hosted builds.

Research notes:
- No functions or state are defined in this file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/cputime.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9l/cputime.c

This file provides hosted compatibility helpers for timing and file creation/seek behavior.

Key routines:
- `cputime` sums process CPU time from `times` and returns seconds as a double.
- `seek` wraps `lseek`.
- `create` wraps Unix `creat`, accepting only mode argument `m == 1`.

Important interactions:
- Used by verbose linker timing logs in files such as `obj.c`, `asm.c`, `pass.c`, and `span.c`.
- Provides Plan 9-like function names in a hosted environment.

Research notes:
- This is support glue, not target-specific linker logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/cputime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/l.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9l/l.h

This is the central header for the Power64 linker. It defines linker data structures, symbol classes, operand classes, global state, and function prototypes.

Key structures:
- `Adr`: assembler operand with offset/string/IEEE union, symbol, auto record, type, register, name, and class.
- `Prog`: instruction node with `from`, `from3`, `to`, branch/flow links, pc, mark flags, optab index, opcode, and register.
- `Sym`: linker symbol with type, version, value, signature, file, frame, and become metadata.
- `Autom`: auto/parameter/file-history metadata.
- `Optab`: operand pattern and encoder dispatch record.

Key enums and constants:
- Mark flags: `LABEL`, `LEAF`, `FLOAT`, `BRANCH`, `LOAD`, `FCMP`, `SYNC`, `FOLL`, `NOSCHED`.
- Symbol types: `STEXT`, `SDATA`, `SBSS`, `SXREF`, `SLEAF`, `SCONST`, `SUNDEF`, `SIMPORT`, `SEXPORT`.
- Operand classes: `C_REG`, `C_FREG`, `C_ZCON`, `C_SCON`, `C_LCON`, `C_VCON`, `C_SBRA`, `C_LBRA`, `C_SAUTO`, `C_LEXT`, `C_ADDR`, etc.
- Relocation bit partition constants `Roffset` and `Rindex`.

Important interactions:
- Shared by all `9l` implementation files.
- Includes target opcode/address definitions from `../9c/9.out.h`.
- Declares global state such as `firstp`, `textp`, `datap`, `hash`, `HEADTYPE`, `INITTEXT`, `INITDAT`, `datsize`, `textsize`, `debug`, `oprange`, and dynamic import/export state.

Research notes:
- This header defines the linker’s internal ABI and must remain consistent with object records emitted by `9c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/l.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9l/list.c

This file implements formatting and diagnostics for linker instructions, operands, opcodes, strings, and classes.

Key routines:
- `listinit` installs custom formatters `%A`, `%D`, `%P`, `%S`, `%N`, and `%R`.
- `prasm` prints a single `Prog`.
- `Pconv` formats full instructions, including indexed forms and `NOSCHED` markers.
- `Aconv` converts opcode numbers to assembler names.
- `Dconv` formats raw operand address modes.
- `Nconv` formats symbol-relative operands such as `SB`, `SP`, and `FP`.
- `Rconv` formats operand class names through `cnames`.
- `Sconv` escapes string constants.
- `diag` reports errors scoped to the current text symbol and aborts after too many errors.

Important interactions:
- Used throughout linker diagnostics, debug listings, and illegal-combination reporting.
- Depends on `anames`, `cnames`, `curp`, `curtext`, and `INITTEXT`.

Research notes:
- `Dconv` handles Power64 special registers (`XER`, `LR`, `CTR`), FPSCR/MSR, branches, floating constants, and string constants.
- `diag` increments global `nerrors`, which drives `errorexit` cleanup behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/noop.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9l/noop.c

This file performs late instruction-stream cleanup and prologue/epilogue expansion before scheduling and spanning.

Key routines:
- `noops` marks leaf routines, detects branches/sync/floating operations, strips `ANOP`, computes frame and `BECOME` sizes, expands `TEXT` prologues, expands `RETURN`, handles `BECOME` pseudo-returns, and optionally schedules instruction blocks.
- `addnop` inserts a Power64 no-op encoded as `OR R0,R0`.

Important interactions:
- Runs after `follow` and before `span`.
- Uses symbol fields `frame`, `become`, and type `SLEAF`.
- Calls `sched` when instruction scheduling is enabled via `debug['Q']`.
- Inserts LR save/restore through `REGTMP`, `REGSP`, and special register `D_LR`.

Research notes:
- Leaf functions with no frame suppress stack adjustment and LR save/restore.
- Non-leaf prologues save LR through `REGTMP` and may use `MOVDU` for compact SP adjustment.
- `BECOME` support adjusts frame sizes across calls and rewrites returns into tail branches.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/noop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/obj.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9l/obj.c

This file is the main `9l` driver and object/archive reader. It parses command-line options, loads object files and libraries, decodes Plan 9 object records, manages symbols, inserts profiling code, and initializes endian conversion state.

Key routines:
- `main` configures output format, entry/text/data placement, dynamic module/export options, default entry symbol, object loading, library autoloading, passes, and final assembly.
- `isobjfile`, `objfile`, and `loadlib` distinguish object files from archives and autoload needed archive members based on unresolved `SXREF` symbols.
- `ldobj` decodes object records emitted by `9c`: `ANAME`, `ASIGNAME`, `AHISTORY`, `AEND`, `AGLOBL`, `ADATA`, `ADYNT`, `AINIT`, `ATEXT`, and ordinary instructions.
- `zaddr` decodes serialized `Adr` operands and records autos/params.
- `addlib`, `addhist`, `histtoauto`, and `collapsefrog` maintain source history and autolib paths.
- `lookup` manages versioned symbol hash entries.
- `doprof1` and `doprof2` insert profiling instrumentation.
- `nuxiinit`, `find1`, `ieeedtof`, and `ieeedtod` set byte-order maps and float conversion helpers.
- `undefsym`, `zerosig`, and `readundefs` support dynamic imports/exports.

Important interactions:
- Drives the full pass sequence: `patch`, optional profiling, `dodata`, `follow`, `noops`, `span`, `asmb`, and `undef`.
- Receives object format emitted by `9c/swt.c`.
- Populates `textp`, `datap`, symbol table, autolib list, and global linker settings.

Research notes:
- Supports q.out, Plan 9 64-bit, boot, raw, ELF, and bootable ELF output modes.
- Floating constants are pooled into data symbols during object loading.
- Dynamic loadable module mode changes export/import handling and later output layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/obj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/optab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9l/optab.c

This file defines the static operand-pattern table used by the linker to select instruction encodings.

Key content:
- `optab[]` maps assembler opcode plus operand classes to:
  - `type`: encoder case consumed by `asmout`.
  - `size`: emitted byte length.
  - `param`: default base register or helper parameter.
- Covers text pseudo-ops, register moves, arithmetic, logical operations, shifts/rotates, floating-point operations, loads/stores, branches, constants, special registers, compares, traps, cache/TLB operations, raw words, and dynamic relocation forms.

Important interactions:
- `span.c:buildop` sorts this table and expands opcode-range aliases.
- `span.c:oplook` matches instructions against this table.
- `asmout.c:asmout` interprets the selected `type`.

Research notes:
- The table is the declarative bridge between abstract assembler operands and concrete Power64 encoding recipes.
- Several instructions intentionally share patterns through aliasing in `buildop`, rather than duplicating all variants here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/optab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/pass.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9l/pass.c

This file implements major linker transformation passes after object loading: data layout, undefined-symbol checking, branch target resolution, code-follow ordering, numeric parsing, rounding, and import/export table construction.

Key routines:
- `dodata` validates data initializers, lays out small data, regular data, BSS, literal pools, and defines linker symbols such as `setSB`, `bdata`, `edata`, `end`, and `etext`.
- `undef` reports unresolved external references.
- `relinv` returns inverse conditional branch opcodes.
- `follow` and `xfol` reorder reachable code to improve fallthroughs and duplicate small branch islands where useful.
- `patch` resolves branch symbols to `Prog.cond` pointers and handles undefined dynamic imports via `UP`.
- `mkfwd` builds skip-forward pointers to speed branch target lookup.
- `brloop` collapses chains of unconditional branches.
- `atolwhex` parses decimal, octal, hex, and signed numeric options.
- `rnd` rounds values to alignment.
- `import`, `ckoff`, `newdata`, and `export` build dynamic import/export metadata and exported symbol tables.

Important interactions:
- Runs before `noops`, `span`, and `asmb`.
- Consumes symbols and data records from `obj.c`.
- Produces data layout consumed by `asm.c:datblk`.
- Dynamic import/export records feed `span.c:dynreloc` and `asmdyn`.

Research notes:
- Literal-pool insertion targets large `AMOVW` constants or symbol addresses that are not compactly encodable.
- `follow` rewrites control flow using `FOLL` marks and branch inversion for layout.
- Export table construction serializes signature, address, and name pointer triples into data records.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/pass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/sched.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9l/sched.c

This file implements an optional local instruction scheduler for Power64 instruction blocks.

Key structures:
- `Dep` records integer registers, floating registers, condition-code effects, and condition-register effects.
- `Sch` wraps a `Prog` with dependency sets, memory offset/size, and compound-instruction metadata.

Key routines:
- `sched` builds scheduling metadata for a block, attempts to fill load-use and floating-compare delay slots with safe earlier instructions, then writes the reordered instructions back.
- `regused` computes per-instruction set/use dependencies from opcode and operand classes.
- `depend` determines whether two instructions can be interchanged without changing semantics.
- `offoverlap` detects overlapping stack/SB memory ranges.
- `conflict` detects adjacent load-result use stalls.
- `compound` treats multiword optab encodings and writes to `REGSB` as scheduling barriers.
- `dumpbits` prints dependency masks for debug output.

Important interactions:
- Called from `noop.c:noops` only when `debug['Q']` is enabled.
- Uses `oplook`, `aclass`, and `regoff` to classify operands.
- Honors marks such as `LOAD`, `BRANCH`, `FCMP`, `SYNC`, and `NOSCHED`.

Research notes:
- Memory dependencies distinguish generic memory, stack-pointer-relative memory, and static-base-relative memory.
- Special registers and FPSCR/MSR operations conservatively clobber broad dependency sets.
- The scheduler is local and bounded by `NSCHED`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/sched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/span.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9l/span.c

This file computes final text addresses, classifies operands, selects optab entries, builds opcode lookup ranges, expands too-distant short branches, and serializes dynamic relocation metadata.

Key routines:
- `span` assigns `pc` values, handles explicit `TEXT` origins, detects large procedures, expands out-of-range conditional branches by inserting branch-around sequences, rounds text size, sets `etext`, and computes `INITDAT`.
- `xdefine` defines linker-generated symbols if not already defined.
- `vregoff` and `regoff` classify operands and return computed offsets.
- `isint32` and `isuint32` test constant ranges.
- `aclass` maps `Adr` operands to `C_*` classes and computes `instoffset` for extern/static/auto/param/constant/branch forms.
- `oplook` matches an instruction against sorted optab ranges and caches the selected optab index.
- `cmp` defines class-subsumption rules used by optab matching.
- `ocmp` sorts optab entries.
- `buildop` constructs `xcmp` compatibility tables, sorts `optab`, creates `oprange`, and aliases many opcode variants to shared pattern ranges.
- `dynreloc` records sorted dynamic relocation entries.
- `asmdyn` writes import and relocation tables after the main image.

Important interactions:
- Uses `optab.c` patterns and `asmout.c` encoder cases.
- Called after `noops`; its resulting `pc`, `textsize`, and `INITDAT` are consumed by `asm.c`.
- In DLM mode, `aclass` classifies symbol references as relocatable addresses and `dynreloc` records them.

Research notes:
- Short conditional branch expansion is iterative because inserting branches changes later PCs.
- Operand classes encode both addressing mode and offset range, making optab matching compact.
- Dynamic relocation records are delta-compressed when written by `asmdyn`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9l/span.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/9auth.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/9auth.c

This standalone utility interacts with a mounted 9nfs authentication file for a user.

Key behavior:
- Parses options `-D`, `-d`, and `-r root`.
- Constructs an auth file path as `<root>/#<username>`.
- With `-d`, creates/truncates the file and exits.
- Otherwise opens the file read/write, reads a network challenge, prompts for a response, rewinds, and writes the response.

Important interactions:
- Uses Unix/POSIX headers rather than Plan 9 headers, suggesting hosted utility behavior.
- Works with authentication pseudo-files exposed by the NFS/9P bridge.

Research notes:
- Default root is `/n/emelie`.
- Challenge and response buffers are `NETCHLEN` bytes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/9auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/9p.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/9p.c

This file implements synchronous 9P message exchange and fid caching for `9nfs`.

Key routines:
- `xmesg` sends a 9P request from `Session.f`, waits for the matching tag, validates reply type, handles `Rerror`, and logs debug traces.
- `newfid` allocates or recycles fids from a session-local LRU/free list.
- `setfid` moves a fid to the front of the active list and sets `Session.f.fid`.
- `putfid` returns a fid to the free list and clears owner back-pointers.
- `clunkfid` sends `Tclunk` for a fid and releases it.
- `fidtimer` auto-clunks stale owned fids.

Important interactions:
- Used by NFS request translation in `nfs.c`, `nfsserver.c`, `nfsmount.c`, and `authhostowner.c`.
- `Fid.owner` is a pointer-to-pointer so cached `Xfid` fields can be nulled when fids are reclaimed.
- Uses `messagesize`, `Maxfdata`, `staletime`, and global `nfstime`.

Research notes:
- Tag mismatch replies are skipped until the expected tag arrives.
- Fid recycling may clunk the least-recently-used owned fid when no free fid remains.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/9p.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/all.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/all.h

This is the umbrella include header for `9nfs`.

Key content:
- Includes Plan 9 system/library headers: `u.h`, `libc.h`, `ip.h`, `bio.h`, `auth.h`, `authsrv.h`, `fcall.h`, and `regexp.h`.
- Includes local headers: `dat.h`, `fns.h`, `rpc.h`, and `nfs.h`.
- Installs vararg format checks for `chat`, `clog`, `panic`, and `%I`.

Important interactions:
- Included by most `9nfs` C files.
- Centralizes subsystem type and function visibility.

Research notes:
- This header establishes that `9nfs` combines RPC, NFS, 9P, auth, and UID-map functionality.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/all.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/auth.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/auth.c

This file contains disabled/stubbed NFS authentication pseudo-file hooks.

Key routines:
- `xfauth` returns nil.
- `xfauthread` logs and returns zero bytes.
- `xfauthwrite` logs and returns zero.
- `xfauthremove` logs and returns failure.

Important interactions:
- Called from NFS lookup/create/read/write/setattr paths when handling root-level `#user` authentication pseudo-files.
- Current behavior effectively disables this older authentication mechanism.

Research notes:
- The file comment states NFS authentication support is now disabled.
- Real host-owner authentication is handled separately in `authhostowner.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/authhostowner.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/authhostowner.c

This file authenticates a `Session` to a 9P server using factotum-backed auth proxying.

Key routines:
- `gstring` and `gcarray` parse counted strings/byte arrays from buffers, though they are local helpers not used by the main path here.
- `dorpc` wraps `auth_rpc`, handling `ARneedkey`/`ARbadkey` by invoking an optional key callback.
- `doread` and `dowrite` perform 9P reads/writes on an auth fid.
- `authproto` proxies an auth conversation between factotum RPC and a 9P auth fid until `auth_getinfo` succeeds or an error occurs.
- `authhostowner` obtains an auth fid with `Tauth`, opens `/mnt/factotum/rpc`, runs `p9any` as client, then tries `Tattach` with the auth fid.

Important interactions:
- Uses `xmesg`, `newfid`, `putfid`, and 9P request fields in `Session.f`.
- Uses Plan 9 auth APIs: `auth_allocrpc`, `auth_rpc`, `auth_getkey`, `auth_getinfo`, and cleanup helpers.
- Called during service initialization in `nfsmount.c:srvinit`.

Research notes:
- If `Tauth` fails, it treats authentication as unneeded and returns success.
- Always cleans/clunks auth and attach fids on exit paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/authhostowner.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/chat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/chat.c

This file provides debug logging, syslog logging, panic handling, and a `/srv` control endpoint for runtime chat/debug verbosity.

Key routines:
- `chatsrv` creates a `/srv` file exposing a pipe; writes to it adjust `chatty`, `rpcdebug`, and `conftime`.
- `killchat` removes the service file and kills the helper process at exit.
- `chat` prints debug messages to fd 2 when `chatty` is enabled.
- `clog` logs to stderr or Plan 9 syslog depending on verbosity.
- `panic` logs a fatal error and exits.

Important interactions:
- Shared by all `9nfs` server programs.
- Updates global `rpcdebug` used by RPC serialization/debug code.
- `conftime` forces config reload timing when chat control receives commands starting with `c`.

Research notes:
- `chatsrv` forks with `RFPROC|RFMEM`, sharing memory with the parent for debug-control variables.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/chat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/dat.h

This header defines the shared data model for `9nfs`.

Key structures:
- RPC-related: `Auth`, `Authunix`, `Accept`, `Reject`, `Rpccall`, and `Rpccache`.
- NFS/data conversion: `Fhandle`, `Sattr`, `String`.
- UID mapping: `Unixid`, `Unixmap`, `Unixidmap`, and `Unixscmap`.
- Namespace/session: `Xfile`, `Xfid`, `Fid`, `Session`, and `Chalstuff`.
- Program dispatch: `Progmap` and `Procmap`.

Important fields:
- `Rpccall` includes UDP-header-derived host/port fields and RPC call/reply unions.
- `Xfile` caches a 9P qid tree and maps it to NFS file handles.
- `Xfid` binds a user to an `Xfile` with cached user/root and open fids.
- `Session` holds the underlying 9P connection, message buffer, fid pool, root, service name, and auth flags.

Important interactions:
- Used by NFS server, mount server, PC-NFS server, RPC parser/serializer, auth, and UID-map code.
- Defines constants such as `FHSIZE`, `Maxfdata`, and `Maxstatdata`.

Research notes:
- The design is a stateful bridge from stateless NFS file handles to cached 9P sessions/fids.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/fns.h

This header declares shared `9nfs` functions.

Key groups:
- Auth and mapping: `auth2unix`, `authhostowner`, `readunixidmaps`, `pair2idmap`, `id2name`, `name2id`.
- RPC: `rpcM2S`, `rpcS2M`, `rpcprint`, `server`, `error`, `garbage`.
- 9P/fids: `xmesg`, `newfid`, `setfid`, `putfid`, `clunkfid`, `fidtimer`.
- Namespace bridge: `xfroot`, `xfile`, `xfid`, `setuser`, `xfstat`, `xfopen`, `xfwalkcr`, `xp2fhandle`, `xpclear`.
- NFS conversion: `convM2sattr`, `dir2fattr`.
- Logging and utilities: `chat`, `clog`, `panic`, `strstore`, `strparse`, `listalloc`.

Important interactions:
- Included via `all.h`.
- Documents the subsystem boundary across multiple implementation files not all present in this group.

Research notes:
- The prototypes show that this group is a slice of a larger `9nfs` program, with RPC and mapping implementations elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/listalloc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/listalloc.c

This file implements a simple fixed-size free-list allocator.

Key routine:
- `listalloc(n, size)` rounds `size` up to pointer alignment, allocates `n * size` bytes, and chains the elements by storing a next pointer at the start of each item.

Important interactions:
- Declared in `fns.h`; intended for subsystems needing bulk allocation of list nodes.

Research notes:
- The caller receives the base pointer, with each element internally linked.
- No free routine is provided here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/listalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/mport.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/mport.c

This standalone utility queries a remote NFS mount service through the portmapper.

Key behavior:
- Dials UDP port 111 on a host, enables header mode, and parses remote IP/port from the network directory.
- Sends a portmapper `GETPORT` request for mount program `100005`, version 1, UDP.
- Sends mount `NULL` and `EXPORT` RPCs to the returned mount port.
- Prints exported directories and access groups.
- Optionally emits AUTH_UNIX credentials through `putauth` when `-m mach` is supplied.

Key routines:
- `main` drives portmapper and mount RPC sequence.
- `putauth` builds an AUTH_UNIX credential blob.
- `rpccall` serializes, sends, reads, parses, validates, and returns result length.

Important interactions:
- Uses shared RPC packing/parsing macros and `rpcS2M`/`rpcM2S`.
- Debug output is controlled by `rpcdebug`.

Research notes:
- This is a diagnostic/client tool, not part of the main NFS server loop.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/mport.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/nametest.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/nametest.c

This utility tests Unix ID-map parsing and name/id lookup behavior.

Key behavior:
- With no arguments, reads Unix IDs from stdin using selected style (`-9` or `-u`) and prints them.
- With a config file, loads maps, selects a default or requested client, and accepts interactive commands from stdin.
- Commands switch user/group maps, reload maps, lookup id-to-name and name-to-id, print current server/client, and dump IDs.

Key routines:
- `main` parses options and command loop.
- `mapinit` reads mapping files and selects a `Unixidmap` using `pair2idmap`.

Important interactions:
- Uses mapping functions declared in `fns.h`.
- Uses `chatty` and `rpcdebug` globals for debugging compatibility.

Research notes:
- Default test client is hard-coded as `nslocum.research.bell-labs.com`; default server in lookup is `bootes`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/nametest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/nfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/nfs.c

This file contains core NFS-to-9P object translation helpers.

Key routines:
- `rpc2xfid` converts an NFS file handle plus AUTH_UNIX credentials into an `Xfid`, validating file-handle tags, resolving `Xfile`, mapping client UID to a Plan 9 user, and optionally statting the target.
- `setuser` recursively walks/creates per-user fids from parent `Xfile` state.
- `xfstat` stats a 9P-backed `Xfid`, or fabricates stat data for authentication pseudo-files.
- `xfwstat` writes stat changes through 9P `Twstat`.
- `xfopen` opens an `Xfid`, creating a duplicate/open fid as needed and tracking mode.
- `xfclose` and `xfclear` close and release cached fids.
- `xfwalkcr` performs 9P walk or create and updates `Xfile`/`Xfid` caches.
- `xpclear` recursively clears cached namespace state.
- `xp2fhandle` encodes an `Xfile` into a 32-byte NFS file handle.
- `dir2fattr` converts Plan 9 `Dir` metadata into NFS v2 file attributes.
- `convM2sattr` parses NFS setattr data.

Important interactions:
- Used heavily by `nfsserver.c`.
- Bridges `Rpccall`, `Authunix`, `Unixidmap`, `Session`, `Xfile`, `Xfid`, and 9P `Fcall` state.
- Uses `starttime` and `Session*` pointer values in non-root file handles.

Research notes:
- Root handles contain a service name; non-root handles contain a starttime tag, session pointer, qid path, and qid type.
- UID translation is mandatory for normal requests through `pair2idmap` and `id2name`.
- Directory attributes use a synthetic length of 1024 and NFS mode bits are derived from Plan 9 mode bits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/nfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/nfs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/nfs.h

This header defines NFS v2 constants used by the bridge.

Key content:
- NFS status codes such as `NFS_OK`, `NFSERR_PERM`, `NFSERR_NOENT`, `NFSERR_STALE`, and `NFSERR_WFLUSH`.
- NFS file types: `NFNON`, `NFREG`, `NFDIR`, `NFBLK`, `NFCHR`, and `NFLNK`.
- NFS mode constants `S_IFMT`, `S_IFDIR`, and `S_IFREG`.
- `NOATTR` sentinel for unset setattr fields.

Important interactions:
- Used by `nfs.c`, `nfsmount.c`, and `nfsserver.c`.
- Constants match RFC 1094-era NFS v2 expectations.

Research notes:
- This header is protocol-definition only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/nfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/nfsmount.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/nfsmount.c

This file implements the NFS mount protocol service and initializes backing 9P sessions.

Key routines:
- `mntinit` parses mount/server options, initializes one or more 9P services, reads UID maps, sets `starttime`, and configures stale-fid timeout.
- `srvinit` opens/dials/uses a 9P connection, negotiates `Tversion`, authenticates, attaches as `none`, creates root `Xfile`/`Xfid` state, and links the session into the service list.
- `mnttimer` invokes per-session fid expiration.
- Mount RPC handlers: `mntnull`, `mntmnt`, `mntdump`, `mntumnt`, `mntumntall`, and `mntexport`.
- `xfroot` resolves a mount root name or service alias to a session root.

Important interactions:
- `nfsserver.c` registers this as program `100005`, version 1.
- Uses `authhostowner`, `xmesg`, `newfid`, `xfile`, `xfid`, `xp2fhandle`, and UID-map functions.
- Maintains global `head`/`tail` session list.

Research notes:
- `noauth` is forced on with `noauth=1; /* ZZZ */`, disabling some auth behavior regardless of option parsing.
- Default service is `tcp!fs` if none is configured.
- Export replies expose `/` and optionally the AUTH_UNIX machine name.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/nfsmount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/nfsserver.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/nfsserver.c

This file is the main NFS v2 server implementation over the shared RPC server framework.

Key content:
- Defines the NFS procedure table for program `100003`, version 2.
- Defines a combined `progmap` registering both mount program `100005` and NFS program `100003`.
- `main` starts the RPC server on port 2049.
- `nfsinit` installs periodic alarm logic for fid expiration and UID-map reloads.
- `doalarm` updates `nfstime`, runs mount timers, and reloads config periodically.

Implemented NFS handlers:
- `nfsgetattr`, `nfssetattr`, `nfslookup`, `nfsread`, `nfswrite`, `nfscreate`, `nfsremove`, `nfsrename`, `nfsmkdir`, `nfsrmdir`, `nfsreaddir`, and `nfsstatfs`.
- Stub/error handlers for `nfsreadlink`, `nfslink`, and `nfssymlink`.
- `nfsnull`, `nfsroot`, and `nfswritecache` provide simple protocol responses.

Important interactions:
- Uses `rpc2xfid` and the `Xfile`/`Xfid` bridge from `nfs.c`.
- Translates errors into NFS status codes using `error`.
- Reads/writes through 9P `Tread`, `Twrite`, `Twalk`, `Topen`, `Tcreate`, `Tremove`, and `Twstat` via helper routines.
- Directory reads convert Plan 9 packed `Dir` records into NFS directory entries.

Research notes:
- Write and read counts are bounded by message size/8192-byte buffers.
- Rename only supports same-directory renames because source and target handles must match.
- `statfs` returns synthetic large free-space values rather than querying backing storage.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/nfsserver.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/pcnfsd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/pcnfsd.c

This file implements a minimal PC-NFS daemon RPC service.

Key content:
- Registers program `150001`, versions 1 and 2, on port 1111.
- Version 2 procedures: null, info, and auth.
- Version 1 procedure: null and auth.

Key routines:
- `main` starts the shared RPC server.
- `pcinit` parses config, initializes facility status table, and reads UID maps.
- `pcinfo` returns version string, comment, and facility list.
- `scramble` decodes PC-NFS obfuscated strings using XOR `0x5b`.
- `pc1auth` and `pcauth` parse credentials, decode username/password fields, map the user through `pair2idmap("pcnfsd", host)`, and return uid/gid metadata.
- `pcnull` handles no-op requests.

Important interactions:
- Uses shared `server`, `argopt`, `readunixidmaps`, `pair2idmap`, `name2id`, `chat`, and RPC packing macros.
- Shares UID mapping infrastructure with the NFS bridge.

Research notes:
- Password contents are decoded and logged for debugging but not actually verified here.
- Unknown users fall back to uid/gid 1.
- Version 2 auth replies include a static home path `merrimack:/` and comment `Trust me.`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/pcnfsd.c -->