# Group Research: group_171_9front_sources_os_plan9_9front_sys_src_cmd_ql_asm_c_sources_os_plan9_46304f28b300

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`.

This group covers the Plan 9/9front PowerPC linker backend `ql`, plus several user-space commands: QR-code generation, in-memory 9P filesystem service, ratification policy filesystem, syscall tracing, and `rc` bytecode compilation.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/asm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ql/asm.c

This file emits final `ql` linker output. It writes text, data, symbols, line tables, dynamic relocation metadata, and executable headers for several PowerPC targets.

Key responsibilities:
- `entryvalue()` resolves the configured entry point, accepting numeric addresses or symbols.
- `asmb()` is the main output routine: emits text instructions via `asmout`, writes data blocks via `datblk`, optionally emits symbols and line tables, and then back-patches the file header.
- Header support includes boot format, Be PEF, Plan 9 format, raw output, AIX XCOFF, Blue Gene ELF, and Virtex 4 ELF boot images.
- `asmsym()` and `putsymb()` serialize Plan 9 symbol records for text, data, bss, files, autos, params, and frames.
- `asmlc()` emits compressed line-number deltas.
- `datblk()` materializes initialized data, performs endian conversion, handles float constants, string constants, symbol constants, duplicate initialization checks, and DLM relocations.

Important dependencies:
- Instruction encoding is delegated to `asmout.c`.
- Symbol/type state comes from `obj.c`, `pass.c`, and `span.c`.
- Dynamic relocation records are produced through `dynreloc()` in `span.c`.

Implementation notes:
- Output is buffered through `cput`, `wput`, `lput`, and `cflush`.
- All multi-byte output is big-endian, matching the PowerPC target.
- `datblk()` is sparse over linker data directives and writes zero-filled gaps.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/asm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/asmout.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ql/asmout.c

This file maps linker pseudo-instructions and selected `Optab` instruction forms into PowerPC machine words.

Key responsibilities:
- Defines PowerPC opcode construction macros such as `OPVCC`, `AOP_RRR`, `AOP_IRR`, branch encoders, and rotate-mask encoders.
- `asmout()` is the central encoder. It switches on `Optab.type` and emits one to five 32-bit words for each instruction form.
- Handles register-register arithmetic, immediate arithmetic, loads/stores, indexed memory operations, branches, condition-register moves, SPR/MSR/FPSCR moves, traps, rotate-mask instructions, cache/TLB operations, and floating-point instructions.
- Expands macro forms such as signed byte loads, large constants, large-address loads/stores, branch-to-register via LR, and remainder via divide/multiply/subtract.
- Supports DLM relocation emission through `reloc()` and `dynreloc()` calls for split and absolute relocations.

Opcode tables:
- `oprrr()` maps register-register and many special/floating opcodes.
- `opirr()` maps immediate and branch opcodes.
- `opload()`, `oploadx()`, `opstore()`, and `opstorex()` map load/store variants.

Implementation notes:
- `getmask()` and `maskgen()` convert bit masks into PowerPC rotate-mask fields.
- `aflag` mode returns a synthesized first instruction word for scheduler/analysis use without emitting output.
- It diagnoses illegal R0 literal operations when `r0iszero` semantics are active.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/asmout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/cnam.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ql/cnam.c

This file provides the textual names for `ql` operand classes.

Contents:
- Defines `char *cnames[]`, indexed by the `C_*` operand classification enum in `l.h`.
- Names include register classes, constants, branch ranges, auto/external addressing forms, special registers, wildcard classes, and `NCLASS`.

Usage:
- `list.c` uses `cnames` through `%R` formatting in `Rconv()`.
- `span.c` diagnostics use these names when reporting illegal instruction operand combinations.

Implementation notes:
- This is a small debug/diagnostic support table.
- It must remain in enum order with the `C_*` definitions in `l.h`; mismatches would make diagnostics misleading.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/cnam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/compat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ql/compat.c

This file is a compatibility shim.

Contents:
- Includes `l.h`.
- Includes `../cc/compat`, pulling in shared C compiler/linker compatibility code by textual inclusion.

Usage:
- Keeps `ql` aligned with the shared Plan 9 compiler toolchain support code without duplicating it locally.

Implementation notes:
- The file has no local functions or data.
- Its behavior is entirely determined by the included compatibility source.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/l.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ql/l.h

This is the central private header for the PowerPC linker `ql`.

Key definitions:
- Core structures: `Adr`, `Prog`, `Sym`, `Auto`, and `Optab`.
- Operand classes `C_*`, symbol types `S*`, program mark flags, relocation bit layout constants, and global linker limits.
- Global linker state: buffers, header parameters, symbol hash table, instruction chains, data chains, debug flags, sizes, current text/function context, import/export state, and dynamic-linking state.
- Declarations for all linker passes and helpers across `asm.c`, `asmout.c`, `obj.c`, `pass.c`, `span.c`, `sched.c`, and `list.c`.

Important conventions:
- `P` and `S` are null sentinels for `Prog*` and `Sym*`.
- `Adr` overlays offsets, string constants, and IEEE constants.
- `Prog` includes `from`, `from3`, `to`, branch links, scheduling marks, opcode cache, line number, and register fields.
- `Optab` rows describe assembler operand classes, encoding type, output size, and default base register.

Implementation notes:
- The header makes heavy use of Plan 9 `EXTERN` style global declarations.
- It installs custom format checking pragmas for instruction, address, symbol, and class printers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/l.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ql/list.c

This file implements debug and diagnostic formatting for `ql` linker instructions and operands.

Key responsibilities:
- `listinit()` installs formatters for `%A`, `%D`, `%P`, `%S`, `%N`, and `%R`.
- `Pconv()` prints a `Prog`, including special formatting for data directives, indexed addressing, third operands, and NOSCHED markers.
- `Aconv()` converts opcode numbers to assembler names.
- `Dconv()` prints typed addresses: constants, offsets, branches, registers, SPR/DCR/FPSCR/MSR/SREG, floating constants, and string constants.
- `Nconv()` prints symbol-relative names for extern, static, auto, and param addressing.
- `Sconv()` escapes fixed-size string constants.
- `Rconv()` maps operand classes through `cnames`.
- `diag()` reports current-text-prefixed errors and aborts through `errorexit()` after too many errors.

Usage:
- Used throughout the linker for debugging flags and fatal diagnostics.
- `asm.c`, `asmout.c`, `span.c`, `pass.c`, and `obj.c` rely on `%P`, `%D`, `%A`, and `%R` diagnostics.

Implementation notes:
- `curp` and `curtext` are updated during formatting, which diagnostics depend on.
- Branch display adjusts target PCs relative to text/header layout for readability.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/noop.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ql/noop.c

This file performs late pseudo-instruction cleanup, function prologue/epilogue generation, leaf detection, and optional scheduling boundaries.

Key responsibilities:
- `noops()` scans the instruction stream to:
  - detect leaf functions,
  - compute frame and become sizes,
  - strip `ANOP`,
  - mark labels, branches, sync instructions, floating instructions, and scheduling barriers,
  - expand `ARETURN`,
  - expand Plan 9 `BECOME` pseudo-returns,
  - insert stack adjustment and link-register save/restore code.
- Updates symbol metadata for function frame and become requirements.
- Defines `ALEFbecome` with the maximum become frame requirement.
- Invokes `sched()` over eligible basic blocks when `debug['Q']` enables scheduling.
- `addnop()` inserts a PowerPC no-op as `NOR R0,R0`.

Important behavior:
- Leaf functions with no stack frame suppress save/restore code and become `SLEAF`.
- Non-leaf prologues save LR through `REGTMP` and use `MOVWU` when the stack adjustment is small.
- Returns are rewritten into LR restore, stack restore, and branch-to-LR sequences.

Implementation notes:
- Many low-level or ordering-sensitive instructions are marked `SYNC` and excluded from unsafe scheduling movement.
- Branch targets skip over stripped NOPs and are marked as labels.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/noop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/obj.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ql/obj.c

This file is the main program and object/archive loader for the `ql` PowerPC linker.

Key responsibilities:
- `main()` parses linker options, initializes output format defaults, opens the output file, loads object files, resolves libraries, performs all linker passes, and emits the final binary.
- Supports output selection for boot, Be PEF, Plan 9, raw, XCOFF, and ELF variants.
- Handles `-x` export-table and `-u` dynamically loadable module modes.
- `objfile()` loads either plain object files or Plan 9 archives with symbol headers.
- `ldobj()` parses Plan 9 object records, builds `Prog` chains, resolves `ANAME`/`ASIGNAME`, handles history/autolib metadata, `TEXT`, `GLOBL`, `DATA`, `DYNT`, and `INIT`.
- Floating constants in `FMOVS`/`FMOVD` are interned as generated data symbols.
- `loadlib()` repeatedly loads autolibs until external references stop being resolved.
- `doprof1()` and `doprof2()` inject profiling/tracing code.
- `lookup()` manages the linker symbol hash table.

Important support:
- `zaddr()` decodes serialized object addresses and records auto/param symbols.
- `addlib()`, `addhist()`, `histtoauto()`, and `collapsefrog()` process object history and autolib paths.
- `nuxiinit()`, `ieeedtof()`, and `ieeedtod()` handle target endian layout and IEEE conversions.
- `readundefs()` reads explicit import/export symbol lists.

Implementation notes:
- Duplicate `TEXT` with `DUPOK` is skipped by turning instructions into NOPs.
- Undefined dynamic imports become `SUNDEF` with relocation index encoding.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/obj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/optab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ql/optab.c

This file defines the instruction selection table for `ql`.

Contents:
- `Optab optab[]` maps assembler opcodes plus operand classes to:
  - encoding type used by `asmout()`,
  - instruction size in bytes,
  - default base register parameter.
- Covers text pseudo-ops, moves, arithmetic, logical operations, loads/stores, branches, condition branches, floating-point operations, SPR/MSR/FPSCR/CR moves, trap/cache/TLB operations, string load/store, and embedded/FP2 PowerPC opcodes.
- The final sentinel is `{ AXXX, ... }`.

Usage:
- `span.c` sorts and indexes this table in `buildop()`.
- `oplook()` uses `oprange` plus operand class compatibility to select the matching row.
- `asmout.c` interprets the selected row’s `type` and `size`.

Implementation notes:
- Many opcode families are represented once here and then aliased in `buildop()`.
- The table is highly coupled to `aclass()` classifications and `asmout()` type cases.
- Incorrect sizes here would corrupt PC layout, branch reach checks, and output emission.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/optab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/pass.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ql/pass.c

This file implements major non-emission linker passes: data layout, undefined-symbol checking, branch following, patching, utility parsing, and import/export table creation.

Key responsibilities:
- `dodata()` validates data initializers, assigns small data, large data, and bss offsets, creates literal pool entries for large constants, computes `datsize`/`bsssize`, and defines linker symbols such as `setSB`, `bdata`, `edata`, `end`, and `etext`.
- `undef()` diagnoses unresolved external references.
- `follow()` and `xfol()` reorder instruction flow to improve fall-through layout and duplicate short code runs when useful.
- `patch()` resolves branch operands to `Prog.cond`, handles unresolved dynamic branches, and collapses branch chains through `brloop()`.
- `mkfwd()` builds sparse forward links to speed PC-to-instruction lookup.
- `atolwhex()` and `rnd()` are utility parsers/rounders used by option and layout code.
- `import()` marks import symbols as undefined dynamic symbols.
- `export()` builds the `_exporttab` and `.string` data records for exported symbols and type signatures.

Implementation notes:
- Data layout favors small symbols near `REGSB` for efficient 16-bit addressing.
- Literal generation is conservative and avoids `setSB`.
- Export entries contain signature, address, and string pointer triples, terminated by zero records.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/pass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/sched.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ql/sched.c

This file implements a small local instruction scheduler for PowerPC delay/stall avoidance.

Key responsibilities:
- `sched()` operates over basic blocks of up to `NSCHED` instructions when scheduling is enabled by `debug['Q']`.
- Builds side records containing each instruction, register/memory/control dependencies, memory offset/size, load markers, branch markers, and compound-instruction markers.
- Moves independent earlier instructions after loads or floating compares to avoid load-use and compare-branch stalls.
- Writes the reordered instructions back into the original `Prog` chain.

Dependency analysis:
- `regused()` computes integer register, floating register, condition/control register, and memory set/use masks.
- Tracks special resources such as LR, CTR, XER, CR fields, ICC/FCC, SB-relative memory, SP-relative memory, and generic memory.
- `depend()` prevents reordering across true, anti, output, control, and overlapping memory dependencies.
- `conflict()` detects immediate load-result use.
- `offoverlap()` refines SB/SP memory alias checks by offset and size.
- `compound()` treats multiword encodings and writes to `REGSB` as nontrivial scheduling units.

Implementation notes:
- Many special-register and FPSCR operations conservatively clobber broad state.
- Debug flag `X` prints set/use dependency masks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/sched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/span.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ql/span.c

This file computes final instruction addresses, classifies operands, selects optab rows, handles long conditional branches, and emits dynamic relocation tables.

Key responsibilities:
- `span()` assigns PCs starting at `INITTEXT`, handles `TEXT` origin overrides, updates text symbol values, expands out-of-range conditional branches into longer branch sequences, aligns text, sets `textsize`, and derives `INITDAT` from `INITRND`.
- `aclass()` classifies `Adr` operands into `C_*` classes and computes `instoffset`.
- `regoff()` returns the offset computed by `aclass()`.
- `oplook()` selects and caches the matching `Optab` entry for a `Prog`.
- `cmp()` defines class compatibility rules used by `buildop()`.
- `buildop()` sorts `optab`, builds opcode ranges, and aliases opcode families to shared table ranges.
- `dynreloc()` records dynamic relocations in sorted address order.
- `asmdyn()` serializes import names/signatures and compressed relocation records.

Important behavior:
- In dynamic-linking mode, external/static operands become `C_ADDR` or large constants and relocation records are attached later during encoding/data emission.
- Conditional branches that exceed signed 16-bit reach are rewritten with inverted/extra branches and inserted no-ops.
- `buildop()` is tightly coupled to `optab.c` and must run before instruction lookup.

Implementation notes:
- The file intentionally defines `r0iszero` as `1` locally for operand classification decisions.
- Relocation records encode absolute/relative, defined/undefined, split, and sign-extension modes through compact mode values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ql/span.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qr.c

This file implements a standalone QR-code encoder that reads input from stdin and writes a Plan 9 image-like bitmap stream.

Key responsibilities:
- Supports QR numeric, alphanumeric, and byte modes.
- Supports error correction levels L, M, Q, and H.
- Selects a QR version automatically or uses `-v`.
- Encodes payload bits, pads codewords, computes Reed-Solomon error correction, interleaves blocks, builds base QR patterns, fills data modules, evaluates masks, writes format/version bits, and finalizes module values.
- `main()` reads up to 8192 bytes, calls `qrcode()`, and writes a `k8` image header followed by raw module bytes.

Important functions:
- `qrinit()` initializes polynomial and block-capacity tables from embedded data.
- `formsel()` chooses version/level capacity.
- `encode()` serializes the chosen QR payload mode.
- `ecc()` computes Reed-Solomon parity over GF(256).
- `codewords()` interleaves data and ECC codewords according to QR block layout.
- `basepat()`, `fill()`, `mask()`, `evaluate()`, `format()`, and `version()` construct and score the QR matrix.

Implementation notes:
- Static tables include GF exponent/log tables, alignment positions, generator polynomials, and all version/level block layouts.
- Alphanumeric mode accepts both uppercase and lowercase letters by mapping them to the same table values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ramfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ramfs.c

This file implements `ramfs`, a user-space in-memory 9P filesystem using lib9p.

Key responsibilities:
- Stores file contents sparsely in 64 KiB chunks under an indirect `Ram` array.
- Uses a custom Plan 9 `Pool` backed by `sbrk`, with relocation repair through `rammoved()`.
- `fsread()` reads file data, returning zeros for holes.
- `fswrite()` expands indirect/data chunks as needed, honors append mode, zero-fills gaps, and enforces `MAXFSIZE`.
- `truncfile()` shrinks or frees backing chunks.
- `fswstat()` implements rename, chmod-like mode changes, group changes, length changes, and timestamp updates with Plan 9-style permission checks.
- `fscreate()`, `fsopen()`, `fsdestroyfid()`, and `fsdestroyfile()` implement create/open/remove-on-close/free behavior.
- `fsstart()` can mark the process memory private and unswappable when `-p` is used.
- `main()` configures mount/server modes and posts the service through stdio, `/srv`, or a mountpoint.

Options:
- `-i` serves on stdin/stdout.
- `-s`/`-S` post service names.
- `-m` chooses mountpoint.
- `-p` protects memory.
- `-u` removes the default pool size cap.
- `-a`, `-b`, `-c` adjust mount flags.

Implementation notes:
- Exclusive files use a 300-second lock check based on refs and atime.
- ORCLOSE removes files on fid destruction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ramfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ratfs/ctlfiles.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ratfs/ctlfiles.c

This file parses ratfs configuration and control files into the in-memory policy tree.

Key responsibilities:
- `getconf()` reads the smtpd config file and processes `ournets` entries into permanent trusted-network pseudo-files.
- `reload()` reads the blocked/control file and populates allow, delay, block, dial, and deny address/account directories.
- `getline()` canonicalizes input lines into lower-case, NUL-separated tokens, removing comments, commas, whitespace runs, and simple escapes.
- `findkey()` maps text keywords to action codes.
- `cidrparse()` parses IP/mask or IP#mask names into canonical network and mask values.
- `subslash()` converts `/` to `#` for file-name-safe CIDR strings.
- `acctinsert()` inserts account rules under `account`, rejecting broad dangerous patterns like `*` and `*!*`.
- `ipinsert()` inserts IP/CIDR rules under `ip`.
- `ipsort()` sorts IP entries and assigns base QID ranges for generated pseudo-files.

Implementation notes:
- Permanent trusted entries are purged/reloaded while temporary trusted entries are retained and renumbered.
- Address entries are stored as `Address` arrays on `IPaddr`/`Acctaddr` nodes.
- IP matching depends on sorted arrays and binary search in `misc.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ratfs/ctlfiles.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ratfs/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ratfs/main.c

This file is the entry point and tree initializer for `ratfs`, a 9P filesystem exposing mail ratification/blocking policy.

Key responsibilities:
- Defines default paths:
  - service file `/srv/ratify`,
  - mountpoint `/mail/ratify`,
  - control file `/mail/lib/blocked`,
  - config file `/mail/lib/smtpd.conf.ext`.
- Defines the prototype filesystem tree: root, allow/delay/block/dial/deny directories, trusted directory, ctl file, and generated `ip`/`account` subdirectories.
- `main()` parses options, initializes formatters, builds the root tree, loads config/control files, posts a service pipe, forks the protocol server, and mounts it.
- `setroot()` materializes the static tree and initializes the reusable dummy node for generated address pseudo-files.
- `post()` publishes the service in `/srv/ratify`, replacing stale entries and exiting if another server is already mountable.
- `fatal()` prints an error and exits.
- `newnode()` allocates and links `Node` records.
- Debug helpers print nodes, fids, and full trees.

Options:
- `-c` alternate config file.
- `-f` alternate control file.
- `-m` alternate mountpoint.
- `-d` debug to stderr.

Implementation notes:
- Most nodes are owned by atomized `"upas"` strings.
- The server child seals stdin/stdout to `/dev/null` and runs `io()` from `proto.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ratfs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ratfs/misc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ratfs/misc.c

This file contains ratfs path walking, directory read helpers, address matching, trusted-entry cleanup, and string interning.

Key responsibilities:
- `walk()` dispatches path traversal based on node type.
- `dirwalk()` finds static child directories.
- `trwalk()` matches trusted CIDR pseudo-files by masking the requested IP.
- `ipwalk()` parses an IP path element, binary-searches sorted address rules, and returns the shared `dummy` node.
- `acctwalk()` parses source-routed account paths and matches them against account patterns.
- `ipsearch()` performs masked binary search over sorted IP/CIDR entries.
- `dread()` serializes real child nodes for directory reads.
- `hread()` serializes generated address/account pseudo-file directory entries.
- `finddir()` locates top-level directories by type.
- `cleantrusted()` removes expired temporary trusted files after a two-hour timeout.
- `accountmatch()`, `usermatch()`, and `dommatch()` implement domain/user wildcard semantics.
- `atom()` interns strings through a custom permanent string table.

Implementation notes:
- Generated address pseudo-files reuse global `dummy`, mutating its name and QID as needed.
- Account patterns support domain, subdomain, user, and trailing-user-prefix matches.
- The string table intentionally never frees interned strings to support pointer identity comparisons.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ratfs/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ratfs/proto.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ratfs/proto.c

This file implements the ratfs 9P protocol loop and request handlers.

Key responsibilities:
- `io()` reads 9P messages from `srvfd`, decodes them, dispatches through `fcalls[]`, and writes replies.
- `reply()` converts successful replies or `Rerror` responses back to the client.
- `newfid()` allocates/reuses fid records.
- Implements handlers for version, flush, auth, attach, clone/walk, open, create, read, write, clunk, remove, stat, and wstat.

Protocol behavior:
- Authentication is not required.
- `rattach()` reloads config/control files when mtimes change and cleans expired trusted entries.
- `rwalk()` supports clone-walk semantics and partial walk responses.
- `ropen()` allows only write access to `ctl`; all other files/directories are read-only.
- `rcreate()` only creates temporary trusted CIDR files in writable trusted directories.
- `rread()` only returns directory contents; non-directories read as EOF.
- `rwrite()` accepts `ctl` commands: `reload`, `debug [file]`, and `nodebug`.
- `rremove()` only removes temporary trusted files owned by the calling user.
- `rwstat()` is intentionally unimplemented.

Implementation notes:
- Permission checks rely on atomized uid/gid pointer equality.
- `rbuf` is sized with one spare byte so `rwrite()` can NUL-terminate command text.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ratfs/proto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ratfs/ratfs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ratfs/ratfs.h

This is the shared header for ratfs.

Key definitions:
- QID constants for root, action directories, trusted files, generated address files, ctl, and dummy nodes.
- Node type constants: static directories, address directories, IP/account address holders, trusted directory/files, ctl file, and dummy node.
- Core structures:
  - `Fid` for active 9P fids,
  - `Cidraddr` for IP/mask pairs,
  - `Address` for account or CIDR entries,
  - `Node` for filesystem tree nodes,
  - `Keyword` for command/action parsing.
- Global state: `root`, `dummy`, `srvfd`, protocol buffer, debug fd, file paths, reload timestamps, and `trustedqid`.

Declared APIs:
- Tree and protocol functions: `io`, `newnode`, `walk`, `dread`, `hread`.
- Config/control functions: `getconf`, `reload`, `cidrparse`, `findkey`, `subslash`.
- Utilities: `atom`, `fatal`, debug printers, `cleantrusted`, `finddir`.

Implementation notes:
- `Node` uses a union for children, address arrays, or CIDR data depending on type.
- Several semantics depend on atomized strings for cheap equality.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ratfs/ratfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ratrace.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ratrace.c

This file implements `ratrace`, a small threaded syscall tracer for Plan 9 processes.

Key responsibilities:
- Attaches to an existing pid or starts a command with `-c`.
- Opens `/proc/<pid>/ctl` and `/proc/<pid>/syscall`.
- Stops the process, enables syscall tracing with `startsyscall`, reads syscall lines, prints them to stderr, and resumes tracing.
- Detects `Rfork` syscalls with `RFPROC` and starts reader threads for newly forked child processes.
- Uses Plan 9 threads and channels:
  - `out` for syscall messages,
  - `quit` for reader termination,
  - `forkc` for child-process accounting.
- `writer()` multiplexes channels, tracks active readers, formats pid transitions, and frees messages.

Implementation notes:
- The child command path uses `hang` on its own proc ctl before `exec`, allowing the tracer to attach before execution proceeds.
- Reader failure sends the `%r` error through `quit`.
- The syscall fork detection is intentionally conservative, checking the syscall text and parsed flags.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ratrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/Makefile -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/Makefile

This Makefile builds the Unix-hosted `rc` shell target.

Key contents:
- Target binary: `rc`.
- Object files include parser/runtime modules such as `code.o`, `exec.o`, `glob.o`, `lex.o`, `pcmd.o`, `pfnc.o`, `simple.o`, `tree.o`, `var.o`, `unix.o`, and generated parser object `syn.o`.
- Header dependencies include `rc.h`, `y.tab.h`, `io.h`, `exec.h`, `fns.h`, and `getflags.h`.
- Grammar source: `syn.y`, built with `YFLAGS=-d`.
- `PREFIX` defaults to `/usr/local`.
- `install` copies `rc` to `$(PREFIX)/bin/` and `rcmain.unix` to `$(PREFIX)/lib/rcmain`.
- `unix.o` is compiled with `-DPREFIX="$(PREFIX)"`.
- `clean` removes objects, binary, and generated parser files.

Implementation notes:
- This is a conventional portable makefile rather than a Plan 9 `mkfile`.
- `y.tab.h` depends on generated `syn.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/code.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/code.c

This file compiles `rc` parse trees into the shell’s internal bytecode representation.

Key responsibilities:
- Maintains `codebuf`, `codep`, `ncode`, and source line tracking.
- `compile()` initializes bytecode, stores reference count and source file name, compiles a tree, and appends `Xreturn`.
- `morecode()` grows the bytecode buffer.
- `stuffdot()` patches forward jump addresses.
- `noglobs()` removes glob markers where a literal string or pattern is expected.
- `outcode()` recursively emits bytecode for all major shell syntax nodes: variables, quoting, substitution, background jobs, sequencing, concatenation, command substitution, conditionals, functions, loops, words, redirections, assignments, pipes, subshells, switches, matches, and simple commands.
- `codeswitch()` emits the switch/case bytecode layout with jump patching and final `Xpopm`.
- `iscase()` recognizes literal `case` commands in switch bodies.
- `codecopy()` and `codefree()` implement reference-counted bytecode lifetime, freeing owned strings according to opcode layout.

Implementation notes:
- `outcode()` emits `Xsrcline` records when source line changes.
- Background jobs synthesize `/dev/null` read redirection and optionally emit a Plan 9 `rfork s` builtin call.
- Some tree strings transfer ownership into bytecode by setting `t->str = 0`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/code.c -->