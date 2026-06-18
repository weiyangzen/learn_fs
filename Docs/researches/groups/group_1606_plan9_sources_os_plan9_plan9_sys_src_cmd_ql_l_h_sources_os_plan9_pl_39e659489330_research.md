# Group Research: group_1606_plan9_sources_os_plan9_plan9_sys_src_cmd_ql_l_h_sources_os_plan9_pl_39e659489330

Scope: `Docs/research_subset_a.md`; all listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/l.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/l.h

PowerPC linker shared header for `ql`.

Defines the linker’s central IR and global state:
- `Adr`: assembler operand with value union, symbol, auto metadata, register/name/type/class fields.
- `Prog`: instruction node with `from`, `from3`, `to`, branch `cond`, list links, pc, mark flags, opcode, and register.
- `Sym`: linker symbol record with type/version/value/signature metadata.
- `Autom`: auto/history metadata attached to `TEXT`.
- `Optab`: instruction selection table entry.

Important enums cover:
- instruction mark bits such as `LABEL`, `LEAF`, `BRANCH`, `LOAD`, `SYNC`, `NOSCHED`;
- linker symbol classes such as `STEXT`, `SDATA`, `SBSS`, `SXREF`, `SIMPORT`, `SEXPORT`;
- operand classes such as `C_REG`, `C_SCON`, `C_LEXT`, `C_SBRA`, `C_ADDR`.

The file also declares all major global linker state: output/header layout, current text/prog pointers, symbol hash table, data/text sizes, object/library tracking, dynamic import/export counters, byte-order maps, and output buffers. It is the coupling point for the `ql` linker pipeline: object loading, branch patching, data layout, scheduling, instruction spanning, assembly output, profiling injection, and dynamic relocation.

Risk/notes:
- The design is intentionally global-state-heavy; ordering of passes matters.
- Operand class caching (`Adr.class`) is central to `oplook()` performance and correctness.
- `Roffset`/`Rindex` encode dynamic relocation limits and are checked later.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/l.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/list.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/list.c

Diagnostic and pretty-print support for the `ql` linker IR.

Main responsibilities:
- `listinit()` installs Plan 9 `Fmt` conversions for opcodes, operands, programs, symbols, and register classes.
- `prasm()` prints one `Prog`.
- `Pconv()` formats an instruction, including `ADATA`/`AINIT`/`ADYNT`, indexed addressing, `from3`, scheduling marks, and register operands.
- `Aconv()` maps opcode numbers through `anames`.
- `Dconv()` formats operand types including constants, memory references, integer/floating/control registers, SPR/DCR/FPSCR/MSR/SREG, branches, float constants, and string constants.
- `Nconv()` formats symbol-relative names for extern/static/auto/param addressing.
- `Rconv()` formats operand classes through `cnames`.
- `Sconv()` escapes fixed-width string constants.
- `diag()` reports errors against the current text symbol and exits after too many errors.

This file is not transformation logic, but it is essential for debugging all linker passes and for fatal diagnostics emitted by object loading, branch resolution, span, and instruction selection.

Risk/notes:
- `Dconv()` depends on `curp` to resolve branch target formatting.
- `diag()` increments global `nerrors`; later `errorexit()` removes partial output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/noop.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/noop.c

Instruction cleanup, frame/prologue/epilogue generation, leaf detection, and optional scheduling entry point.

Main flow in `noops()`:
- Scans the instruction list to identify leaf functions, frame sizes, branch labels, floating-point operations, synchronization-sensitive instructions, and call/become requirements.
- Removes `ANOP` nodes by relinking them out while preserving marks.
- Tracks maximum `BECOME` stack requirement and defines `ALEFbecome`.
- Adjusts calling function frame sizes when calls may need extra become space.
- Expands `ATEXT` into function prologue code:
  - computes `autosize`;
  - suppresses save/restore for true leaf functions;
  - emits stack adjustment and link-register save using `REGTMP`.
- Expands `ARETURN` into actual return sequences:
  - direct branch to LR for frameless leaf functions;
  - stack restoration for leaf functions with frames;
  - LR restore plus stack adjustment for non-leaf functions;
  - special handling for `BECOME`.
- If debug flag `Q` is enabled, schedules basic blocks by invoking `sched()` around labels, branches, syncs, and `NOSCHED` runs.

`addnop()` inserts a PowerPC no-op as `NOR R0,R0`.

Risk/notes:
- Correctness depends on conservative marks for instructions touching special registers and memory synchronization.
- `NOSCHED` regions are preserved during scheduling.
- Leaf/non-leaf decisions affect ABI-visible stack and LR handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/noop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/obj.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/obj.c

Main driver and object/archive loader for the PowerPC Plan 9 linker.

Major responsibilities:
- Defines linker identity: `thechar='q'`, `thestring="power"`, default output `q.out`.
- Parses options for output, entry, text/data addresses, header type, library paths, exports, imports, dynamic modules, and debug flags.
- Sets executable header defaults for boot, Be boot, Plan 9, raw, XCOFF, and ELF variants.
- Initializes global linker state, opcode tables, byte-order maps, symbol state, object list, and output file.
- Orchestrates the full pass pipeline:
  `objfile/loadlib -> import/export -> patch -> profiling -> dodata -> follow -> noops -> span -> asmb -> undef`.

Object loading:
- `objfile()` loads regular object files or Plan 9 archives.
- Archive loading reads the symbol table and repeatedly pulls archive members for unresolved `SXREF` symbols.
- `ldobj()` decodes object records, symbol/name records, history records, data records, text records, floating constants, globals, dynamic tables, and branch/data operands.
- `zaddr()` decodes serialized operands and records auto/param metadata.
- `addlib()` resolves autolib history paths, expanding `$O` and `$M`, deduplicating libraries.

Symbol/memory management:
- `lookup()` hashes symbols by name and version.
- `prg()` allocates initialized `Prog` nodes from hunks.
- `gethunk()` grows linker arena memory.
- `nuxiinit()` computes byte-order maps.

Instrumentation/dynamic support:
- `doprof1()` inserts counter data and increment sequences.
- `doprof2()` inserts calls to `_profin/_profout` or tracing hooks.
- `undefsym()`, `zerosig()`, and `readundefs()` support import/export lists and dynamic modules.

Risk/notes:
- `ldobj()` is the format-critical path; malformed object records can desynchronize parsing.
- Static symbols use object-version scoping.
- Duplicate `TEXT` can be skipped under `DUPOK`, otherwise diagnosed.
- Dynamic-loadable module mode changes layout assumptions (`HEADTYPE`, `INITTEXT`, `INITDAT`, `INITRND`, entry).
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/obj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/optab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/optab.c

PowerPC instruction selection table for the linker backend.

Defines `Optab optab[]`, mapping:
- assembler opcode (`as`);
- operand classes for `from`, register, `from3`, and `to`;
- encoding type number;
- emitted instruction size;
- optional parameter register.

The table covers:
- `TEXT` pseudo-ops;
- integer moves, arithmetic, logical operations, multiply/divide/remainder;
- shifts and rotate/mask forms;
- floating-point arithmetic and moves;
- memory loads/stores for SB/SP/zero-register/long-address forms;
- branches and branch-to-LR/CTR forms;
- special registers, FPSCR, CR, MSR, SREG, SPR;
- cache/TLB/sync operations;
- FP2 and embedded PowerPC variants.

`buildop()` in `span.c` sorts this table and creates alias opcode ranges, so many related mnemonics share a base table entry.

Risk/notes:
- The numeric encoding `type` values are consumed by `asmout()` outside this group.
- Size values drive `span()` PC assignment and branch relaxation.
- Missing/incorrect operand classes surface as `illegal combination` diagnostics from `oplook()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/optab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/pass.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/pass.c

Mid-level linker passes for data layout, branch patching, control-flow following, and dynamic export/import table generation.

Key functions:
- `dodata()` validates data initializers, assigns small data first, lays out data and BSS, builds literal data entries for large constants/address constants, and defines `setSB`, `bdata`, `edata`, `end`, and `etext`.
- `undef()` diagnoses unresolved external references.
- `relinv()` maps conditional branches to inverse conditions.
- `patch()` resolves branch and call symbol operands to `Prog.cond` targets, handles undefined calls through `UP`, then collapses branch chains with `brloop()`.
- `mkfwd()` creates sparse forward links to accelerate PC target lookup.
- `follow()`/`xfol()` reorder code by following branches, copying short instruction runs when useful, and inserting synthetic branches when needed.
- `atolwhex()` parses decimal, octal, and hex numeric arguments.
- `rnd()` rounds addresses.
- `import()` turns unresolved signature-bearing symbols into import entries.
- `export()` builds `_exporttab` and `.string` data containing sorted exported symbol signatures, addresses, and names.

Risk/notes:
- `dodata()` mutates symbol types between `SDATA`, `SDATA1`, and `SBSS`; this layout is consumed by `span()` and assembly output.
- `xfol()` duplicates already-followed code in limited cases to improve fall-through layout.
- Export table construction emits synthetic `ADATA` records into `datap`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/pass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/sched.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/sched.c

Optional local instruction scheduler for PowerPC delay/stall reduction.

Core model:
- `Sch` wraps one `Prog` with dependency sets, memory offset/size, and compound flags.
- `Dep` tracks integer regs, floating regs, condition/control bits, and memory categories.
- `regused()` classifies each instruction’s read/write effects based on opcode and operand classes.
- `depend()` determines whether two instructions can be interchanged safely.
- `conflict()` detects immediate load/use or compare/branch hazards.
- `offoverlap()` refines SP/SB memory dependencies using offset/size ranges.
- `compound()` treats multiword instruction expansions and writes to `REGSB` as unschedulable compounds.
- `sched()` builds a fixed-size scheduling window, moves safe earlier instructions between load/use or fcmp/branch pairs, and writes the reordered `Prog` data back.

It is only active under debug flag `Q`, invoked from `noops()` over bounded basic blocks.

Risk/notes:
- Memory disambiguation is conservative except for SP/SB offset ranges.
- Special registers and broad operations set all dependency classes to prevent unsafe movement.
- Scheduler relies on `aclass()` and `oplook()` from `span.c`, so instruction selection must be initialized first.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/sched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/span.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/span.c

PC assignment, operand classification, opcode lookup, branch relaxation, and dynamic relocation emission.

Key functions:
- `span()` assigns PCs from `INITTEXT`, uses `oplook()` sizes, handles `TEXT` origin overrides, detects very large procedures, inserts long-branch workaround sequences when short branches exceed range, aligns text, sets `etext`, `textsize`, and `INITDAT`.
- `xdefine()` defines unresolved symbols if still undefined.
- `aclass()` maps `Adr` operands to linker operand classes and computes `instoffset`.
- `regoff()` returns the offset computed by `aclass()`.
- `oplook()` caches operand classes on `Prog` operands, scans the opcode range for compatible `Optab`, and diagnoses illegal combinations.
- `cmp()` defines class compatibility, allowing narrower classes to satisfy broader table entries.
- `ocmp()` and `buildop()` sort `optab`, build `oprange`, and alias many related opcodes to shared encoding ranges.
- `dynreloc()` records sorted dynamic relocation entries, distinguishing absolute/relative, defined/undefined, split, and sign-extended modes.
- `asmdyn()` emits import names/signatures and compressed relocation deltas.

Risk/notes:
- `#define r0iszero 1` makes zero-register behavior fixed within this file.
- `aclass()` is where dynamic-module addressing diverges from normal static linking.
- Branch relaxation mutates the instruction stream after an initial span pass.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/span.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ramfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ramfs.c

Standalone in-memory 9P file server.

Data model:
- Fixed `ram[Nram]` array stores file/directory nodes.
- Linked `Fid` table maps 9P fids to `Ram` nodes.
- Root directory is initialized as `.` owned by the current user.
- File data is held in heap buffers, optionally capped by `Maxsize`.

Server behavior:
- `main()` supports stdio mode, service posting, mount point selection, private/noswap mode, debug logging, and unlimited-memory mode.
- `io()` reads 9P messages with `read9pmsg()`, dispatches through `fcalls`, and writes replies.
- Implements 9P operations: version, auth, flush, attach, walk, open, create, read, write, clunk, remove, stat, wstat.
- Directory reads serialize child `Dir` records with `convD2M()`.
- File reads return slices of stored data; writes grow buffers, zero gaps, update qid versions and mtimes.
- `rwstat()` supports rename, mode/group changes, and truncation/extension with simplified Plan 9 ownership/group rules.
- `perm()` checks owner/group/other bits based on the attached user.

Risk/notes:
- This is explicitly a toy-style filesystem; group membership assumes each user leads their own group.
- Fids and nodes are managed manually; user strings leak intentionally/minimally.
- Fixed node table can exhaust at 4096 busy entries.
- Remove-on-clunk (`ORCLOSE`) is implemented through `rclose`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ramfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ratfs/ctlfiles.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ratfs/ctlfiles.c

Parses ratfs configuration/control files and populates synthetic address directories.

Main functions:
- `getconf()` reads `conffile`, currently processing `ournets`, and populates permanent trusted CIDR pseudo-files under `trusted`.
- `reload()` reads `ctlfile`, clears prior counts, maps actions (`allow`, `block`, `deny`, `dial`, `delay`, aliases), and inserts IP/account entries under the corresponding action directory.
- `getline()` canonicalizes each line into lowercase NUL-separated tokens, strips comments, commas, and whitespace, and handles backslash escapes.
- `findkey()` maps token strings through a `Keyword` table.
- `cidrparse()` parses IPv4 CIDR strings, accepting `/` or `#`, and derives a minimal mask if omitted.
- `subslash()` converts `/` to `#` for path-safe names.
- `acctinsert()` inserts account pseudo-file entries, rejecting broad dangerous patterns like `*`, `!`, and variants.
- `ipinsert()` inserts IP/CIDR pseudo-file entries and stores parsed address/mask.
- `ipsort()` sorts IP address arrays and assigns base qids.

Risk/notes:
- `reload()` distinguishes account rules by leading `*`; otherwise treats values as IP/CIDR.
- Address directories store dense arrays; qid assignment depends on sorted counts.
- Permanent trusted entries are rebuilt on config reload, while temporary entries are preserved/re-qid’d.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ratfs/ctlfiles.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ratfs/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ratfs/main.c

Entry point and static tree builder for `ratfs`, a synthetic filesystem exposing mail ratification/blocking policy.

Main responsibilities:
- Defines defaults: `/srv/ratify`, `/mail/ratify`, `/mail/lib/blocked`, `/mail/lib/smtpd.conf.ext`.
- Describes the prototype tree:
  `/`, `allow`, `delay`, `block`, `dial`, `deny`, `trusted`, `ctl`, plus `ip` and `account` subdirs under each address directory.
- `main()` parses flags, installs `%I` CIDR formatter, builds root, loads config/control data, posts the server pipe, forks the protocol loop, and mounts it.
- `setroot()` constructs the static `Node` hierarchy and initializes the reusable `dummy` node.
- `post()` creates/reuses `/srv/ratify`, exiting early if an existing server can be mounted.
- `newnode()` allocates and links nodes, initializes Plan 9 `Dir` metadata, qids, ownership, mode, parent/child/sibling links.
- Debug helpers print nodes, fids, and the whole tree.
- `ipconv()` formats `Cidraddr` values.

Risk/notes:
- `Node.d.type` is used as a ratfs-specific node kind, not just a Plan 9 directory type.
- Children are inserted at the head of sibling lists.
- `dummy` is reused for dynamic address match results.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ratfs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ratfs/misc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ratfs/misc.c

ratfs walking, directory serialization, trusted cleanup, address/account matching, and string interning.

Main logic:
- `walk()` dispatches path lookup by current node kind: normal directory, trusted dir, IP address dir, account dir.
- `dirwalk()` finds named child nodes.
- `trwalk()` matches an input IP against trusted CIDR nodes.
- `ipwalk()` parses an IP path component and binary-searches the sorted address table.
- `acctwalk()` parses source-routed account paths into domains plus user and matches against account patterns.
- `ipsearch()` searches CIDR entries sorted by base IP.
- `dread()` serializes real child nodes for directory reads.
- `hread()` serializes address-array pseudo-files using the shared `dummy` Dir.
- `finddir()` finds top-level directories by type.
- `cleantrusted()` removes expired temporary trusted files after `Timeout`.
- `accountmatch()`, `usermatch()`, and `dommatch()` implement account/domain pattern semantics.
- `atom()` interns strings using a small hash table and bump allocators.

Risk/notes:
- Atomized strings allow pointer comparison in permission checks elsewhere.
- `accountmatch()` temporarily edits the stored pattern string at `!` and restores it.
- `dummy` node reuse means callers must not expect persistent per-address node objects.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ratfs/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ratfs/proto.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ratfs/proto.c

9P protocol implementation for ratfs.

Main dispatch:
- `io()` reads 9P messages from `srvfd`, decodes with `convM2S()`, dispatches by message type, and logs debug traffic.
- `reply()` converts successful replies by incrementing type, or emits `Rerror`.
- `newfid()` allocates/reuses `Fid` records.

Implemented 9P operations:
- `rversion()` clamps msize to `MAXRPC`.
- `rauth()` rejects auth as unnecessary.
- `rattach()` reloads config/control files when mtimes change, cleans temporary trusted entries, and binds fid to root.
- `rwalk()` supports clone-walk and partial walk semantics.
- `ropen()` permits writable access only to `ctl`, read-only elsewhere.
- `rcreate()` allows creates only where directory permissions allow, practically the `trusted` directory, creating temporary trusted CIDR files.
- `rread()` supports directory reads for real directories and address directories; non-directories return EOF.
- `rwrite()` accepts `ctl` commands: `reload`, `debug`, `nodebug`.
- `rclunk()` releases fid state.
- `rremove()` removes only owner-owned temporary trusted files.
- `rstat()` serializes node metadata, adjusting `dummy` name for address pseudo-files.
- `rwstat()` is unimplemented.

Risk/notes:
- Permission checking is deliberately simplified because most files are read-only or ctl-only.
- `rwrite()` NUL-terminates data using the extra byte in `rbuf`.
- Temporary trusted qids wrap before colliding with address-file qids.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ratfs/proto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ratfs/ratfs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ratfs/ratfs.h

Shared definitions for the ratfs synthetic filesystem.

Defines:
- RPC size and qid ranges for fixed nodes, trusted files, and address pseudo-files.
- Node kind constants: `Directory`, `Addrdir`, `IPaddr`, `Acctaddr`, `Trusted`, `Trustedperm`, `Trustedtemp`, `Ctlfile`, `Dummynode`.
- `Fid`: active 9P fid state, current node, open flag, user, directory index.
- `Cidraddr`: IPv4 address and mask.
- `Address`: account string or CIDR address entry.
- `Node`: synthetic tree node with `Dir`, child/address/trusted union, sibling/parent links, qid base, and counts.
- `Keyword`: string-to-code mapping helper.

Declares all cross-file ratfs globals: `root`, `dummy`, `srvfd`, shared RPC buffer, debug/config paths, reload mtimes, and trusted qid counter.

Risk/notes:
- The `Node` union depends strictly on `d.type`.
- `Dir` string fields are expected to be atomized in most paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ratfs/ratfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ratrace.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ratrace.c

Threaded syscall tracer using Plan 9 `/proc`.

Main behavior:
- Can trace an existing pid or launch a command with `-c`.
- For launched commands, child calls `hang()` before `exec()` so tracing can attach before execution.
- `reader()` opens `/proc/<pid>/ctl` and `/proc/<pid>/syscall`, starts syscall tracing, reads syscall records, detects `rfork(RFPROC)` returns, and spawns readers for forked children.
- `writer()` multiplexes trace output, child fork notifications, and quit events over channels.
- `cwrite()` writes proc-control commands and signals shutdown on failure.
- `newstr()` allocates fixed trace buffers.

Risk/notes:
- Fork detection parses syscall trace text heuristically but with several checks.
- `writer()` currently increments reader count for fork events; reader spawning is performed in `reader()` itself, with an older `procrfork` line commented out.
- Trace output is written to fd 2.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ratrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/code.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/code.c

Compiler from rc parse trees to the shell’s bytecode-like `code` vector.

Main components:
- `morecode()` grows compiler output.
- `compile()` initializes code, emits tree code, reads heredocs, appends `Xreturn`, and returns success/failure.
- `outcode()` recursively emits `X*` opcodes for rc syntax: variable expansion, quoted expansion, subscripts, async, sequencing, concatenation, backquote, conditionals, loops, functions, switch, redirection, assignment, pipes, pipefd, globbing, and simple commands.
- `codeswitch()` emits the switch/case control-flow skeleton using patched jumps.
- `iscase()` recognizes `case` commands in switch bodies.
- `fnstr()` converts a tree back to command text for function definitions and no-fork fallback paths.
- `codecopy()`/`codefree()` manage reference counts and free embedded strings/function text.

Risk/notes:
- In no-fork builds, async/backquote/subshell/pipe snippets are stored as strings to run through a new rc.
- Jump patching uses `stuffdot()` with placeholder code slots.
- `if not` correctness uses `runq->iflast` static checking.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/code.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/exec.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/exec.c

Core rc interpreter, word/list stack management, variable handling, and many `X*` opcode implementations.

Startup:
- `main()` parses flags, initializes traps/keywords/environment, sets `$pid`, `$cflag`, `$rcname`, builds bootstrap code to assign `$*` and run rcmain, then enters the dispatch loop.
- `start()` pushes a new `thread` frame with code, pc, local vars, redirection inheritance, command input state, and return link.

Stack/data helpers:
- `newword()`, `pushword()`, `popword()`, `pushlist()`, `poplist()`, `freelist()`, `freewords()`, `count()`.
- `pushredir()` stores pending redirections.
- `newvar()` allocates variable records.

Opcode coverage includes:
- redirection open/close/dup: `Xappend`, `Xread`, `Xrdwr`, `Xwrite`, `Xclose`, `Xdup`, `Xpopredir`;
- status/control flow: `Xsettrue`, `Xbang`, `Xeflag`, `Xexit`, `Xfalse`, `Xtrue`, `Xif`, `Xifnot`, `Xwastrue`, `Xjump`, `Xreturn`;
- stack/list operations: `Xmark`, `Xpopm`, `Xword`, `Xconc`;
- matching: `Xmatch`, `Xcase`;
- variables: `Xassign`, `Xdol`, `Xqdol`, `Xsub`, `Xcount`, `Xlocal`, `Xunlocal`;
- functions: `Xfn`, `Xdelfn`;
- pipes/status: `Xpipewait`;
- command reading: `Xrdcmds`;
- errors/status: `Xerror`, `Xerror1`, `setstatus()`, `getstatus()`, `truestatus()`;
- heredoc cleanup and loops: `Xdelhere`, `Xfor`, `Xglob`.

Risk/notes:
- `Xexit()` runs `sigexit` once in the main shell before exiting.
- Error paths unwind non-interactive threads back to the command loop or exit.
- Word lists are often reversed internally and restored by callers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/exec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/exec.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/exec.h

Interpreter data definitions and opcode declarations for rc.

Defines:
- external declarations for all `X*` opcode functions;
- `word`: linked list of shell words;
- `list`: stack frame containing a word list;
- `redir`: deferred redirection operation (`ROPEN`, `RDUP`, `RCLOSE`);
- `thread`: execution frame containing code vector, pc, argv stack, redirections, locals, command input, status, tree nodes, wait pid, and return link;
- `builtin`: builtin command mapping.

Declares global interpreter state: `runq`, `codebuf`, traps, builtin table, `eflagok`, and `havefork`.

Risk/notes:
- `thread.ret` is the interpreter call stack.
- Redirection stack is inherited through `startredir`.
- `NSTATUS` is tied to Plan 9 `ERRMAX`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/exec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/fns.h

Cross-file function prototype hub for rc.

It declares:
- Plan 9/Unix adapter calls (`Read`, `Write`, `Seek`, `Execute`, `Waitfor`, `Opendir`, `Readdir`, `Trapinit`, `Updenv`, etc.).
- compiler/parser helpers (`compile`, `yyparse`, `yylex`, `yyerror`, `readhere`, `cleanhere`);
- interpreter helpers (`start`, `setvar`, `vlook`, `searchpath`, `globlist`, `dotrap`);
- formatting/matching/argument helpers (`match`, `mkargv`, `list2str`, `count`);
- wait-pid tracking helpers.

This file keeps old-style C compilation coherent across the rc modules.

Risk/notes:
- Several prototypes expose platform abstraction boundaries implemented in `plan9.c` and Unix-specific files outside this group.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/getflags.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/getflags.c

Small command-line flag parser used by rc.

Main logic:
- `getflags()` scans `argv`, recognizes flags according to a compact format string, stores presence-only flags as `flagset`, and moves argument-taking flag values to the end of `argv`.
- `scanflag()` validates a flag spec and returns its argument count.
- `reverse()` supports in-place argument rearrangement.
- `usage()` prints reason-specific errors and generated usage text from the same flag spec.
- `errc()` buffers error output through the platform `Write()` wrapper.

Flag spec syntax supports:
- single-letter flags;
- `:<n>` argument counts;
- bracketed usage labels like `[command]`.

Risk/notes:
- `flag` is indexed directly by character value and limited by `NFLAG`.
- Duplicate flags are rejected.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/getflags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/getflags.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/getflags.h

Tiny shared header for rc flag parsing.

Defines:
- `NFLAG 128`;
- global `flag[NFLAG]`;
- `cmdname`;
- sentinel `flagset`;
- prototype for `getflags()`.

Risk/notes:
- The `flag` table assumes ASCII-ish single-byte option characters below 128.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/getflags.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/glob.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/glob.c

Filename globbing and pattern matching for rc.

Main pieces:
- `deglob()` removes internal `GLOB` escape markers.
- `glob()` expands one pattern, falling back to literal text if no matches.
- `globdir()` recursively scans path components, opening directories only at components containing glob metacharacters.
- `globsort()` sorts matched names lexicographically.
- UTF helpers `equtf()`, `nextutf()`, `unicode()` keep matching rune-aware.
- `matchfn()` applies filename-specific dotfile rules.
- `match()` implements `*`, `?`, character classes, ranges, complements, and escaped `GLOB`.
- `globlist()` expands every word on the current argv list.

Risk/notes:
- Glob metacharacters are represented as `GLOB` followed by the actual metacharacter.
- `.` and `..` only match patterns beginning with `.`.
- Directory-only hints are passed to `Readdir()` when the remaining pattern contains `/`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/glob.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/havefork.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/havefork.c

Implementation of rc process-control opcodes for systems with fork/rfork support.

Functions:
- `Xasync()` forks an async child, redirects stdin from `/dev/null`, sets `$apid`, and skips child code in parent.
- `Xpipe()` creates a pipe, forks left side, runs right side in current interpreter thread, and records pid for `Xpipewait`.
- `Xbackq()` forks command substitution, captures stdout through a pipe, splits output by `$ifs`, and pushes words.
- `Xpipefd()` implements `<{}`/`>{}` style pipefd by forking a side command and pushing `/fd/<n>`.
- `Xsubshell()` forks a subshell and waits.
- `execforkexec()` forks a child to execute an external command.

Risk/notes:
- Children call `clearwaitpids()` so inherited wait tracking does not confuse nested shells.
- `Xbackq()` uses rune-aware reading and `$ifs` matching.
- Parent/child code paths share `runq->code` and rely on `start()` to create correct frames.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/havefork.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/haventfork.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/haventfork.c

Fallback rc process-control implementation for environments without fork.

Strategy:
- `havefork = 0`.
- `rcargv()` builds an argv that re-invokes rc with `-S`/`-Se -c <script>` plus current `$*`.
- `Xasync()`, `Xbackq()`, `Xpipe()`, and `Xsubshell()` run script snippets via `ForkExecute()` instead of in-process forked interpreter frames.
- `Xpipefd()` is unsupported and aborts.
- `execforkexec()` searches `$path` and starts commands with mapped fds via `ForkExecute()`.

Risk/notes:
- No-fork mode depends on `code.c` emitting command strings for affected constructs.
- Backquote splitting here is byte-based, unlike the rune-aware fork implementation.
- Pipefd is not portable in this mode.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/haventfork.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/here.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/here.c

Here-document creation, reading, substitution, and cleanup for rc.

Main logic:
- `heredoc()` records a pending heredoc tag and returns a temporary filename token.
- Temporary names are generated under `/tmp/here....` using pid and a serial number.
- `readhere()` reads heredoc bodies after compilation, writes them to temp files, performs substitution unless the tag was quoted, emits cleanup code via `cleanhere()`, and frees pending records.
- `psubst()` expands `$name`, `$n`, and `$$` in heredoc lines.
- `pstrs()` prints word lists with spaces.

Risk/notes:
- The file notes a known bug: lines longer than `NLINE` are split, which can affect EOF marker recognition and substitution.
- Heredoc cleanup is compiled into the command stream as `Xdelhere`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/here.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/io.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/io.c

Buffered I/O and custom formatting for rc.

Capabilities:
- `pfmt()` implements rc-specific formatting: chars, decimals, octal, pointers, quoted words, error strings, command trees, and word lists.
- `pchr()`, `fullbuf()`, `flush()` handle output buffering to fd-backed or string-backed `io`.
- `rchr()`, `emptybuf()`, `rutf()` handle buffered byte/rune input.
- `pquo()`, `pwrd()`, `pval()` print shell-safe quoted words/lists.
- `pdec()`, `poct()`, `pptr()`, `pstr()` are lightweight format primitives.
- `openfd()`, `openstr()`, `opencore()`, `rewind()`, `closeio()` construct and manage `io` objects.

Risk/notes:
- String-backed `io` grows in `Stralloc` chunks.
- `flush()` can trigger traps if writes fail while traps are pending.
- `rutf()` may push back unconsumed bytes for malformed/partial UTF.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/io.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/io.h

Shared buffered I/O definitions for rc.

Defines:
- `EOF (-1)`;
- `NBUF 512`;
- `struct io` with fd, buffer pointers, optional string pointer, and inline buffer;
- global `err`;
- prototypes for buffered input/output, string/core openers, command/function printers, and formatting primitives.

Risk/notes:
- `strp != nil` distinguishes string/core buffers from fd-backed buffers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/lex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/lex.c

Lexer for rc syntax.

Main features:
- Character classification through `wordchr()` and `idchr()`.
- One-character lookahead with `nextc()`/`advance()`.
- `getnext()` reads command input, handles line continuations, prompting, echo flags, EOF, and comments.
- `pprompt()`, `skipwhite()`, `skipnl()`, `nextis()` support parser interaction.
- Token construction uses `tok` with UTF-preserving `addutf()`.
- `yylex()` recognizes:
  - variable operators `$`, `$#`, `$"`;
  - `&&`, `||`;
  - pipes and redirections including fd forms;
  - quoted strings with doubled quote escaping;
  - implicit concatenation `^` after words;
  - subscript `(` after words;
  - glob metacharacter marking;
  - keywords via `klook()`.

Risk/notes:
- Parser context flags `lastdol` and `lastword` alter tokenization.
- Redirection token trees are allocated directly in the lexer.
- Comments are skipped regardless of quote state per the current comment in code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/pcmd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/pcmd.c

Pretty-printer from rc parse trees back to rc source.

Main functions:
- `pdeglob()` prints a word without internal `GLOB` escape bytes.
- `pcmd()` recursively formats every tree type: variables, quoted vars, async, concatenation, backquote, logical operators, blocks, loops, conditionals, switch, match, assignments, redirections, fd duplication, pipes, words, and arg lists.

Uses:
- Function body serialization in `code.c`.
- Debugging and `whatis` output through `io.c` formatting.

Risk/notes:
- Global `nl` switches command separator output between newline and semicolon for function serialization.
- Some fd duplication print order follows lexer-internal representation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/pcmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/pfnc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/pfnc.c

Debug printer for rc interpreter execution cycles.

Contents:
- Static `fname[]` maps `X*` opcode function pointers to names.
- `pfnc()` prints current pid, code vector pointer, pc, opcode name or raw pointer, and current argv stack contents.

Used when rc flag `-r` is set in the main dispatch loop.

Risk/notes:
- Function pointer matching requires the exact opcode symbols compiled into the same binary.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/pfnc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/plan9.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/plan9.c

Plan 9 platform adapter for rc.

Major responsibilities:
- Defines signal names, rcmain path, fd prefix, and builtin table.
- Builtin `rfork` implementation in `execnewpgrp()`.
- `Vinit()` imports `/env` variables into rc variables.
- `Xrdfn()` and `execfinit()` read function definitions from `/env/fn#*`.
- `Waitfor()` wraps Plan 9 wait, integrates with tracked child pids and pipeline status.
- `mkargv()`, `addenv()`, `Updenv()` convert rc variables/functions back to `/env`.
- `ForkExecute()` and `Execute()` start external programs with path search and env update.
- Directory/glob adapter: `Globsize()`, `Opendir()`, `Readdir()`, `Closedir()`.
- Trap adapter: `notifyf()`, `Trapinit()`, `Eintr()`, `Noerror()`.
- System wrappers: `Unlink`, `Read`, `Write`, `Seek`, `Executable`, `Creat`, `Dup`, `Exit`, `Isatty`, `Abort`, `Malloc`.
- Wait-pid tracking: `addwaitpid()`, `delwaitpid()`, `clearwaitpids()`, `havewaitpid()`.

Risk/notes:
- Environment synchronization is explicit and change-flag based.
- `Exit()` writes environment before exiting.
- `notifyf()` converts Plan 9 notes into rc trap counters and avoids infinite trap loops.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/plan9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/rc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/rc.h

Primary shared header for rc.

Defines:
- Plan 9 vs Unix include boundary.
- parser depth and generated parser include.
- core typedefs for trees, words, I/O, code vectors, variables, lists, redirs, threads, and builtins.
- `tree` AST node with type, redirection/pipe details, string, quote/keyword flags, children, and allocation list.
- `union code` instruction word with function pointer/int/string variants and reference-count convention.
- token buffer `tok`, prompt state, redirection token constants, variable table, heredoc records, glob marker semantics, fd conventions, rcmain/fd prefix globals, and parser state globals.

Risk/notes:
- Many globals are definitions, not just declarations, reflecting old Plan 9 C style.
- `GLOB` escape representation is shared by lexer, globber, and printers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/rc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/simple.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/simple.c

Execution of simple commands and rc builtins.

Main command path:
- `Xsimple()` glob-expands argv, resolves functions, `builtin`, builtins table, optimized final `exec`, or forks external commands.
- `doredir()` applies deferred redirections.
- `searchpath()` chooses path lookup or direct execution.
- `execexec()` replaces shell execution path with external command.
- `execfunc()` starts a function with local `$*`.

Builtins implemented:
- `cd` with `cdpath` and `/dev/wdir` update for interactive shells.
- `exit`.
- `shift`.
- `eval`.
- `.` for sourcing files with local `$0` and `$*`.
- `flag` to inspect/toggle shell flags.
- `whatis` for variables, functions, builtins, and path lookup.
- `wait`.

Helpers:
- `exitnext()` optimizes commands followed only by exit.
- `dochdir()`, `appfile()`, `octal()`, `mapfd()`, `execcmds()`.

Risk/notes:
- `execdot()` carefully transfers caller argv list into sourced command frame.
- `execwhatis()` writes through mapped stdout but notes it should ideally fork first.
- `mapfd()` computes effective fd mapping from pending redirections.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/simple.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/subr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/subr.c

Small rc utility and error helpers.

Functions:
- `emalloc()` wraps platform `Malloc()` and panics on failure.
- `efree()` wraps `free()` and reports attempts to free nil.
- `yyerror()` reports parser errors with file/line/token context, resets lexer continuation state, skips to newline/EOF, increments `nerror`, and sets status.
- `inttoascii()` converts signed integers through recursive helper `iacvt()`.
- `panic()` prints an internal error and aborts.

Risk/notes:
- `iacvt()` does not handle the most negative integer correctly, as commented.
- `yyerror()` consumes input until line end to recover parser state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/syn.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/syn.y

Yacc grammar for rc.

Defines tokens, precedence, semantic type, and grammar rules for:
- command lines and command sequencing;
- braces and parentheses;
- assignments and redirection epilogues;
- `if`, `if not`, `for`, `while`, `switch`, functions;
- simple commands, arg lists, concatenation;
- variables, quoted variables, counts, command substitution, pipefd;
- logical operators, pipes, async, subshell, match.

Actions build `tree` nodes using helpers from `tree.c`, call `heredoc()` for `<<`, and call `compile()` when a line is parsed.

Risk/notes:
- Empty `for(i in )` is represented distinctly from implicit `for(i)`.
- Switch grammar expects case commands inside the brace body and `code.c` validates that structure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/syn.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/trap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/trap.c

rc trap delivery logic.

`dotrap()`:
- Processes pending `trap[]` counters while `ntrap` is nonzero.
- For child processes, exits immediately with current status.
- Looks up function variables named by `Signame[]`.
- If a trap function exists, starts it with copied `$*` as a local and clears redirection inheritance.
- If no function exists for interrupt/quit, unwinds to the interactive command loop.
- Otherwise exits.

Risk/notes:
- Trap functions run as ordinary rc function code on the interpreter stack.
- `$*` is copied from the interrupted context.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/tree.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/tree.c

AST allocation and manipulation helpers for rc.

Main functions:
- `newtree()` allocates zeroed tree nodes and links them into the parse allocation list.
- `freenodes()` frees all parse-time nodes after command compilation.
- `tree1()`, `tree2()`, `tree3()` construct nodes and simplify null `;` nodes.
- `mung1()`, `mung2()`, `mung3()` mutate lexer-created nodes with children.
- `epimung()` attaches redirection epilogues around compound commands.
- `simplemung()` wraps simple commands, records printable command text, and hoists redirections from arg lists to the command root.
- `token()` creates word/keyword nodes.
- `freetree()` recursively frees a standalone tree.

Risk/notes:
- `simplemung()` depends on tree shape produced by grammar and lexer.
- Parse nodes are normally arena-like via `treenodes`; `freetree()` is separate for explicit ownership cases.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/tree.c -->