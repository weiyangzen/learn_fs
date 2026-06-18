# Group Research: group_1631_plan9_sources_os_plan9_plan9_sys_src_cmd_vac_file_c_sources_os_plan_757976ab6659

Scope checked against `Docs/research_subset_a.md`. Every listed source file was read completely in manifest order.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/file.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/file.c

Purpose: core Vac filesystem implementation layered on Venti files. It implements `VacFs`, `VacFile`, directory metadata handling, traversal, mutation, archive root creation/opening, flushing, syncing, and block-score comparison.

Key structures and model:
- `VacFile` is private here and wraps one Venti file for ordinary data, or two Venti files for directories: `source` for directory entries and `msource` for Vac metadata entries.
- Metadata such as `dir`, `ref`, `removed`, and `dirty` is synchronized by the parent lock. The file comments define an upward locking order: hold child then acquire parent, not the reverse.
- Files are reference-counted and linked in the parent `down` list, so repeated walks share in-memory `VacFile` objects.
- Root opening handles both normal Vac roots and older Fossil-style extra indirection.

Major behavior:
- Reference lifecycle is handled by `filealloc`, `filefree`, `vacfileincref`, and `vacfiledecref`; decrement flushes source/msource and dirty metadata before unlinking from parent.
- Path lookup uses `vacfilewalk`, `dirlookup`, and `fileopensource`, with special handling for `.`, `..`, removed children, snapshots, and Venti entry generation checks.
- Directory enumeration uses `VacDirEnum` through `vdeopen`, `vderead`, `vdeunread`, and `vdeclose`; it flushes dirty in-memory children before direct metablock scanning.
- Metadata block mutation is handled by `filemetaalloc`, `filemetaflush`, and `filemetaremove`; these manage sorted `MetaBlock` entries and can move entries across metablocks when resized.
- File mutation includes `vacfilecreate`, `vacfilesetsize`, `vacfilewrite`, `vacfilesetentries`, `vacfilesetdir`, `vacfilesetqidspace`, and `vacfileremove`.
- Filesystem open/create/sync uses `vacfsopen`, `vacfsopenscore`, `vacfscreate`, and `vacfssync`, with Venti root blocks carrying type `vac`, current root score, block size, and previous score.

Integration points:
- Depends on Venti cache/file APIs such as `vtfileopenroot`, `vtfilecreate`, `vtfileblock`, `vtfileflush`, `vtfilesetentry`, `vtread`, `vtwrite`, and `vtrootpack`.
- Depends on metadata packing helpers in `pack.c` and public API declarations in `vac.h`/`fns.h`.
- Used by `vac.c`, `unvac.c`, and `vacfs.c` for archive creation, extraction, and 9P serving.

Risks and invariants:
- Lock ordering is critical; violating the upward parent-lock rule can deadlock.
- `filemetaflush` contains an unusual unconditional `vdunpack(&f->dir, &me)` immediately after `vdpack`; because `vdunpack` allocates new strings into an existing `VacDir`, this is a maintenance risk and should be reviewed before changing metadata code.
- `vacfilewrite` flushes before the written offset, which is central to Vac’s write-once/cache behavior.
- Venti generation and active-entry checks prevent stale directory references from being treated as valid files.
- `vacfssync` mutates `fs->score` with the newly written root score; callers rely on this when printing `vac:%V`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/fns.h

Purpose: internal function declarations shared across Vac implementation files.

Contents:
- Declares metablock operations: `mbunpack`, `mbinsert`, `mbdelete`, `mbpack`, `mballoc`, `mbinit`, `mbsearch`, and `mbresize`.
- Declares metaentry comparison/unpacking: `meunpack`, `mecmp`, `mecmpnew`.
- Defines metadata directory versions: `VacDirVersion = 8`, `FossilDirVersion = 9`.
- Declares Vac directory packing helpers: `vdsize`, `vdunpack`, `vdpack`.
- Exposes internal root/qid functions `_vacfileroot`, `_vacfsnextqid`, and `vacfsjumpqid`.
- Declares glob/exclusion helpers used by `vac.c` and tested by `testinc.c`.

Integration points:
- Included by `file.c`, `pack.c`, `glob.c`, `vac.c`, and `testinc.c`.
- Keeps internal helpers out of public `vac.h` while still sharing them within the Vac command implementation.

Risks:
- Version constants are format-level contracts; changing them affects on-disk Vac metadata compatibility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/glob.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/glob.c

Purpose: include/exclude pattern engine for the `vac` archiver.

Key behavior:
- `glob2regexp` converts a Vac glob syntax into a Plan 9 regular expression.
- Supported patterns include `*`, `...`, `?`, bracket classes, and `~` negation inside bracket classes.
- Beginning-of-path-element handling prevents leading `.` matches for `*`/`?` unless explicitly requested.
- `loadexcludefile` reads lines beginning with `include ` or `exclude `, skips blank/comment lines, compiles patterns, and stores ordered rules.
- `excludepattern` appends a command-line exclusion rule.
- `includefile` returns the first matching rule’s include flag, defaulting to included.

Integration points:
- Used by `vac.c` to skip files during archive creation.
- Tested interactively by `testinc.c`.

Risks:
- Pattern storage is global and append-only.
- `glob2regexp` allocates `20 * strlen(glob)` bytes, which is generous but assumes the expansion bound remains true.
- Character-class parsing walks until `]`; malformed classes reach syntax handling through failed compilation or slash checks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/glob.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/pack.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/pack.c

Purpose: binary packing and unpacking of Vac metadata blocks, metadata entries, and `VacDir` records.

Key structures and helpers:
- `MetaChunk` tracks free/used regions inside a metablock during allocation and compaction.
- Big-endian integer macros encode/decode 8-, 16-, 32-, 48-, and 64-bit fields.
- `stringunpack` and `stringpack` encode strings as 16-bit length plus bytes.

Metablock behavior:
- `mbunpack` validates magic, size, index counts, and handles `MetaMagic+1` via `unbotch`.
- `mbpack` writes metablock headers.
- `meunpack` validates index offsets and embedded directory entry magic.
- `mecmp` and `mecmpnew` compare entry names for binary search; `mbsearch` chooses comparison based on `unbotch`.
- `mballoc` finds holes, appends, or compacts with `metachunks`/`mbcompact`.
- `mbinsert`, `mbdelete`, and `mbresize` maintain sorted index entries and free-space accounting.

VacDir behavior:
- `vdsize` computes packed length for version 8 or 9 records.
- `vdpack` serializes fixed fields, strings, and optional Plan 9/qidspace/generation sections.
- `vdunpack` supports versions 7 through 9, including older replacement-score fields and optional metadata sections.
- `vdcleanup` and `vdcopy` manage the heap-owned strings in `VacDir`.

Integration points:
- `file.c` relies on this code for all directory lookup, enumeration, creation, rename, remove, and root initialization.
- Format constants are declared in `vac.h` and versions in `fns.h`.

Risks:
- This is format-critical code with manual pointer arithmetic and 16-bit offsets; malformed metadata can corrupt assumptions if validation is weakened.
- `metachunks` has dense consistency logic around offsets/free space; changes require careful fixture coverage.
- `vdunpack` allocates strings and must always be paired with `vdcleanup` by callers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/pack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/stdinc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/stdinc.h

Purpose: common include umbrella for Vac command sources.

Contents:
- Includes Plan 9 base headers: `<u.h>`, `<libc.h>`, `<bio.h>`, `<ctype.h>`, and `<thread.h>`.
- Includes Venti, security/hash, and regexp APIs: `<venti.h>`, `<libsec.h>`, and `<regexp.h>`.

Integration points:
- Used by most `cmd/vac` sources to keep include lists consistent.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/stdinc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/testinc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/testinc.c

Purpose: small command-line harness for the Vac include/exclude pattern engine.

Behavior:
- Accepts one include/exclude rules file.
- Calls `loadexcludefile`.
- Reads paths from standard input using `Brdline`.
- Prints `0` or `1` from `includefile(path)` followed by the path.

Integration points:
- Exercises `glob.c` rule loading and matching without running a full archive.
- Uses the same internal headers as `vac.c`.

Risks:
- Input line handling assumes newline-terminated records and overwrites the trailing newline.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/testinc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/unvac.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/unvac.c

Purpose: restore, list, or compare files from a Vac archive.

Command behavior:
- Options include table/list mode, verbose output, stdout extraction, diff/update mode, setting mtimes, Venti host selection, and statistics.
- Opens a Venti connection, opens the Vac archive read-only, gets the root, and recursively calls `unvac`.

Core functions:
- `wantfile` filters requested paths while allowing traversal through ancestors and descendants of requested names.
- `unvac` handles directory recursion, directory creation, file extraction, table output, and special-mode warnings.
- Diff mode opens an existing local file, compares block SHA1 via `sha1matches`, and writes only changed blocks.
- `writen` ensures full writes.
- `mtimefmt` formats mtimes for table output.

Integration points:
- Uses `vacfsopen`, `vacfsgetroot`, `vdeopen`/`vderead`, `vacfilewalk`, `vacfileread`, `vacfiledsize`, and `sha1matches`.
- Uses Plan 9 `Dir`, `dirmodefmt`, `dirwstat`, `create`, and `dirstat`.

Risks:
- Unsupported archived types such as device, symlink, named pipe, and exclusive file are warned and skipped.
- Diff mode removes a partially written output file on write errors.
- Path filtering is string-prefix based and depends on normalized archive names.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/unvac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/vac.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/vac.c

Purpose: main Vac archive creation command.

Command behavior:
- Supports archive mode (`-a`), output file (`-f`), diff archive (`-d`), merge mode, quick diff, stdin input, exclusions, block size selection, Venti host selection, verbose output, and stats.
- Creates a new Vac filesystem or opens an existing archive filesystem for dated snapshots.
- Emits the final `vac:<score>` line after `vacfssync`.

Core flow:
- `threadmain` parses options, connects to Venti, sets up output root, processes stdin and command-line files, records qidspace, syncs, prints root score, and cleans temporary output on failure.
- `recentarchive` finds the newest `yyyy/mmdd[.n]` archive directory for diffing.
- `plan9tovacdir` maps Plan 9 `Dir` metadata into `VacDir`.
- `vac` recursively archives files/directories, applies include/exclude filters, creates Vac nodes, copies metadata, and writes data.
- With a diff archive, unchanged blocks are skipped by comparing SHA1 block scores; quick diff can skip whole files based on metadata.
- `vacmerge` and `vacmergefile` merge existing `.vac` roots while offsetting qid ranges to avoid collisions.
- `vacstdin` archives standard input under a supplied name.
- `unittoull` parses size suffixes.

Integration points:
- Relies heavily on `file.c` APIs and `glob.c`.
- Uses Venti connection setup and packet stats.
- Archive mode depends on the dated tree layout and root previous-score linkage.

Risks:
- The code intentionally relies on content-addressed block reuse for diffing and merging; incorrect block size assumptions can reduce reuse.
- `vacmerge` expects qidspace metadata or falls back to max-qid discovery; qid range maintenance is a key invariant.
- `removevacfile` only removes `vacfile`, so archive-file creation cleanup is limited to non-archive `-f` output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/vac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/vac.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/vac.h

Purpose: public Vac API and format constants shared by Vac tools.

Key contents:
- Forward declarations for `VacFs`, `VacDir`, `VacFile`, and `VacDirEnum`.
- Mode bit definitions for Unix/Plan 9 permissions plus append, exclusive, link, directory, DOS flags, snapshot, device, and named pipe.
- Metadata constants: `MetaMagic`, header/index sizes, `DirMagic`, and optional directory section tags.
- `VacDir` format containing file entry locations, generation numbers, size, qid, owner strings, timestamps, mode, Plan 9 qid info, and qidspace annotations.
- `VacFs` public structure with name, score, root, Venti connection, mode, block size, qid counter, and cache.
- Public functions for opening/creating/syncing Vac filesystems, walking/creating/removing/reading/writing files, reading/changing metadata, directory enumeration, score matching, and entry access.

Integration points:
- Consumed by `vac.c`, `unvac.c`, `vacfs.c`, `file.c`, `pack.c`, and helper tests.
- The incomplete pragmas hide `VacFile` and `VacDirEnum` internals from users.

Risks:
- `VacFs` is not fully opaque and callers such as `vac.c` directly access `fs->score` and `fs->bsize`.
- Mode constants are archive-format-visible and should not be renumbered.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/vac.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/vacfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/vacfs.c

Purpose: serve a Vac archive as a 9P filesystem.

Command behavior:
- Supports debug tracing, cache size, stdio mode, Venti host, service registration, mountpoint, no-permission mode, and Venti verbosity.
- Opens the Vac archive read-only and serves 9P requests over stdio, `/srv`, or a mounted pipe.

Core structures and dispatch:
- `Fid` tracks 9P fid state: busy/open flags, user, qid, associated `VacFile`, and active directory enumerator.
- `initfcalls` maps 9P request types to handler functions.
- `io` reads 9P messages, dispatches by `rhdr.type`, builds replies, and writes responses.

Handlers:
- `rversion`, `rauth`, and `rattach` implement session setup without authentication.
- `rwalk` clones/walks fids through Vac directories using `vacfilewalk`.
- `ropen` enforces permission checks and read-only constraints.
- `rread` reads file data or directory records through `vacdirread`.
- `rstat` converts `VacDir` to 9P `Dir` with `vacstat`.
- `rwrite` and `rwstat` always return read-only.
- `rcreate` and `rremove` contain vestigial mutation paths, but the filesystem is opened read-only in `threadmain`.

Integration points:
- Uses `vac.h` APIs, Plan 9 `fcall.h`, and 9P conversion functions.
- `vacstat` maps Vac mode bits to Plan 9 qid/type/mode bits and applies qidspace offsets.

Risks:
- `rremove` appears to invert `vacfileremove` success handling: it records an error when `vacfileremove` returns `0`. This path is effectively unreachable for the read-only mount but is risky if write support is revived.
- `rcreate` checks `fs->mode & ModeSnapshot`, but `fs->mode` is a Venti open mode, not Vac mode bits; actual read-only protection comes later from `vacfilecreate`.
- Permission checks compare user to `uid` or `gid` strings only; there is no group database lookup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/vacfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/cgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/cgen.c

Purpose: expression, boolean, lvalue, and structure code generation for the Plan 9 MIPS C compiler backend.

Core functions:
- `cgen` emits code for scalar expressions, assignments, arithmetic, calls, casts, conditionals, increments, bitfields, and loads/stores.
- `reglcgen` and `lcgen` compute lvalue addresses.
- `bcgen` and `boolgen` emit branch/value boolean code with short-circuiting.
- `sugen` emits structure/union copies, structure literals, function-returned structs, and temporary handling.
- `layout` copies small groups of longwords and supports unrolled loop copies for larger structures.

Integration points:
- Uses register allocation and instruction emission from `txt.c`.
- Uses bitfield helpers and multiply-constant optimization from `swt.c`/`mul.c`.
- Depends on complexity/addressability from `sgen.c`.

Risks:
- Correctness relies on `complex`/`addable` metadata and function-call complexity (`FNX`) to avoid clobbering operands.
- Struct copy logic creates non-interruptible temporaries (`nodrat`) and requires stack/rathole sizing to be accurate.
- Many branches depend on type classes (`typefd`, `typesuv`, `typeu`); extending types requires coordinated changes across backend files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/cgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/enam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/enam.c

Purpose: instruction mnemonic table for the MIPS backend.

Contents:
- Defines `char *anames[]`, mapping opcode enum values to assembly mnemonic strings.
- Includes all base MIPS instructions used by the backend plus Plan 9 pseudo-ops such as `DATA`, `GLOBL`, `HISTORY`, `TEXT`, `NAME`, and `SIGNAME`.
- Includes later 64-bit and conversion opcodes such as `MOVV`, `DIVV`, `TRUNCDW`, and related entries.

Integration points:
- `list.c` uses this table through `Aconv`.
- The array order must match the `enum as` in `v.out.h`.

Risks:
- Any insertion or reordering in `v.out.h` must be mirrored here exactly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/enam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/gc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/gc.h

Purpose: shared backend header for the Plan 9 MIPS C compiler.

Key contents:
- Includes common C compiler definitions from `../cc/cc.h` and MIPS object definitions from `v.out.h`.
- Defines target sizes for MIPS: 1-byte chars, 4-byte ints/longs/pointers/floats, 8-byte vlongs/doubles.
- Defines backend structures: `Adr`, `Prog`, `Case`, `C1`, `Multab`, `Hintab`, `Var`, `Reg`, and `Rgn`.
- Declares global codegen/register-allocation state.
- Defines liveness and region-cost macros.
- Declares functions implemented by `sgen.c`, `cgen.c`, `txt.c`, `swt.c`, `list.c`, `reg.c`, and `peep.c`.
- Registers custom format verbs for instructions, addresses, bits, and symbols.

Integration points:
- Included by every `cmd/vc` C file in this group.
- Serves as the backend ABI among parser/common compiler code and target-specific emission code.

Risks:
- Many globals are shared mutable compiler state; backend routines assume single-threaded compilation.
- Register-region limits such as `NRGN` and `NVAR` constrain optimization on large functions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/gc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/list.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/list.c

Purpose: debug/listing formatters for backend instructions, addresses, symbols, strings, and bitsets.

Key functions:
- `listinit` installs format verbs.
- `Bconv` formats variable bitsets using `var[]`.
- `Pconv` formats `Prog` instructions with special cases for `DATA` and `TEXT`.
- `Aconv` maps opcode integers through `anames`.
- `Dconv` formats `Adr` operands by addressing type.
- `Sconv` quotes fixed-size string constants.
- `Nconv` formats named address components such as extern, static, auto, and param.

Integration points:
- Used by debug flags throughout `cgen.c`, `reg.c`, `peep.c`, and `txt.c`.
- Depends on `anames[]` from `enam.c`.

Risks:
- Fixed-size buffers (`STRINGSZ`) are used with length checks in some but not all formatting paths.
- Debug output correctness depends on address enum consistency.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/mul.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/mul.c

Purpose: generate shift/add/subtract sequences for multiplication by integer constants.

Core behavior:
- `mulcon0` returns a cached `Multab` sequence for an absolute constant.
- It first checks a cache, then a sorted exception `hintab`, then searches for short sequences, then tries recursion plus trailing shifts.
- Encoded sequences use letters for shifts and `+`/`-` operations with operand selectors.
- `docode`, `gen1`, `gen2`, and `gen3` search and validate sequence encodings.
- `hintab` stores constants where the search algorithm fails or benefits from precomputed sequences.

Integration points:
- `swt.c` uses `mulcon0` via `mulcon` to optimize `OMUL`/`OLMUL` by constants.
- `gc.h` declares `Multab`/`Hintab`.

Risks:
- Dense recursive search and compact sequence encoding are difficult to audit.
- Constants outside successful search/hint paths fall back to hardware multiply.
- Hint table ordering is required for binary search.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/mul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/peep.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/peep.c

Purpose: peephole and copy-propagation optimizer for backend instruction streams.

Core behavior:
- `peep` completes the `Reg` structure for instructions between existing CFG nodes, repeatedly removes redundant register moves, tries substitution propagation, and removes redundant sign/zero-extension moves.
- `excise` converts an instruction to `ANOP`.
- `uniqp`/`uniqs` detect unique predecessor/successor paths.
- `subprop` rewrites register substitutions backward to enable move elimination.
- `copyprop` and `copy1` propagate copies forward through the CFG.
- `copyu` classifies instruction use/set behavior for a target operand.
- `copyas`, `copyau`, `copyau1`, `copysub`, and `copysub1` handle direct and indirect operand substitution.

Integration points:
- Invoked by `regopt` after register painting unless disabled by debug flags.
- Uses instruction semantics from `v.out.h`.

Risks:
- `copyu` defaults unknown opcodes to read-alter-write, which is conservative but can limit optimization.
- New opcodes must be added to use/set classification or they will block propagation.
- Correctness depends on CFG uniqueness checks and call-clobber handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/peep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/reg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/reg.c

Purpose: global register allocator and liveness optimizer for the MIPS backend.

Core flow in `regopt`:
- Builds `Reg` nodes for non-data instructions and assigns pseudo-PCs.
- Computes use/set variable bitsets with `mkvar`.
- Resolves branch targets into CFG predecessor/successor links.
- Detects loops with reverse postorder and approximate dominators.
- Propagates references/calls backward (`prop`) and register-variable synchrony forward (`synch`) to fixed point.
- Finds live regions, computes costs with `paint1`, sorts by value, picks registers with `paint2`/`allreg`, and rewrites code with `paint3`.
- Runs `peep`, recomputes PCs, fixes branch offsets, strips NOPs, and recycles `Reg` nodes.

Other functions:
- `addmove` inserts memory/register loads or stores.
- `mkvar` maps operands to optimizable variable slots and classifies externs, params, constants, and address-taken variables.
- `loopit`, `postorder`, `rpolca`, `doms`, `loophead`, and `loopmark` build loop weighting.
- `RtoB`, `BtoR`, `FtoB`, and `BtoF` map allocatable machine registers to bit masks.

Integration points:
- Driven by common compiler code after code generation.
- Calls `peep.c` and mutates `Prog` streams from `txt.c`.

Risks:
- Optimization is bounded by fixed arrays (`NVAR`, `NRGN`, bitset size).
- Alias handling is conservative through `addrs`, but missed address-taking classification would be unsafe.
- Register bit mapping excludes reserved MIPS registers and only allocates even floating registers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/reg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/sgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/sgen.c

Purpose: backend expression simplification and addressability/complexity analysis.

Key functions:
- `noretval` emits pseudo-use NOPs for integer and floating return registers.
- `xcom` computes node `addable` and `complex` values for code generation.
- It recognizes constants, names, registers, indirect registers, address-of, indirection, additions, calls, and arithmetic rewrites.
- Rewrites multiplication/division/modulo by powers of two into shifts/ands where valid.
- Canonicalizes immediate-friendly operations so constants move to the right side.
- Marks calls as high complexity (`FNX`).

Integration points:
- `cgen.c` relies on `complex` and `addable` to order evaluation safely.
- Uses common compiler helpers such as `vlog`, `simplifyshift`, `com64`, and type tables.

Risks:
- Incorrect complexity can cause register clobbering around function calls.
- Shift/division rewrites must preserve signedness; this file distinguishes logical operations for unsigned cases.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/sgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/swt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/swt.c

Purpose: switch emission, bitfield operations, string/data output, constant-multiply use, object serialization, and layout/alignment helpers.

Key behavior:
- `swit1`/`swit2` emit switch comparisons; small switches are linear and larger ones use recursive binary splitting.
- `bitload` and `bitstore` extract/insert bitfields with shifts and masks.
- `outstring` accumulates string data into `ADATA` chunks of `NSNAME`.
- `mulcon` turns multiplication by selected constants into shift/add/sub sequences from `mul.c`.
- `gextern` emits initialized global data, with special handling for 64-bit constants.
- `outcode`, `zwrite`, `zname`, and `zaddr` serialize the backend instruction stream into Plan 9 object format.
- `outhist` emits source history, with Windows path handling.
- `align` and `maxround` implement MIPS ABI layout rules for structs, parameters, and autos.

Integration points:
- `txt.c` emits `Prog` records consumed by `outcode`.
- `cgen.c` calls bitfield and multiply helpers.
- Object format enums and address types come from `v.out.h`.

Risks:
- Symbol cache size `NSYM` affects object output symbol interning.
- Alignment behavior is ABI-defining and uses endian-specific parameter adjustment for `thechar == 'v'`.
- `mulcon` assumes integer constant conversion through `convvtox` preserves value before optimizing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/swt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/txt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/txt.c

Purpose: low-level MIPS instruction emission, register allocation helpers, moves/conversions, branching, pseudo-ops, and type width/cast tables.

Core initialization:
- `ginit` sets target identity (`thechar = 'v'`, `thestring = "mips"`), initializes globals, special nodes, rathole/return nodes, 64-bit support, and reserved registers.
- `gclean` validates register state, flushes pending string data, emits globals, emits `AEND`, and calls `outcode`.

Register/address helpers:
- `nextpc` allocates `Prog` records.
- `gargs`/`garg1` handle call argument evaluation, including function-call temporaries and first-argument register passing.
- `regalloc`, `regfree`, `regialloc`, `regsalloc`, `regaalloc1`, and `regaalloc` manage temporary registers and stack argument locations.
- `naddr` lowers compiler `Node` operands to backend `Adr` operands.

Instruction emission:
- `gmove` implements loads, stores, scalar conversions, float/integer conversions, constants, and special floating constants.
- `gins` emits a raw instruction.
- `gopcode` maps compiler operations to MIPS opcodes, including multiply/divide LO/HI handling and compare/branch generation.
- `gbranch`, `patch`, and `gpseudo` emit branches and pseudo-ops.
- `sconst`, `sval`, and `exreg` support immediate/register-variable decisions.
- `ewidth` and `ncast` define target type widths and no-cast compatibility masks.

Risks:
- Float-to-int conversion manipulates FCR31 and emits NOPs; this is highly target-specific and fragile.
- Register allocation uses global `reg[]` counts and must be balanced exactly.
- `regfree` checks `i >= sizeof(reg)`, which compares an index to bytes, not element count; the oversized bound is unlikely to fail safely for bad indices.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/txt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/v.out.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/v.out.h

Purpose: MIPS object/instruction definitions for the Plan 9 `vc` backend.

Contents:
- Defines symbol-name length, symbol cache size, and register count.
- Defines text flags and named machine registers such as zero, return, stack, static base, link, and floating constants.
- Declares `enum as` instruction/pseudo-op numbers.
- Defines address type/name constants such as `D_BRANCH`, `D_OREG`, `D_EXTERN`, `D_AUTO`, `D_CONST`, `D_FREG`, `D_LO`, and `D_HI`.
- Defines archive symbol marker `SYMDEF`.
- Defines `Ieee`, Plan 9’s simulated IEEE double representation.

Integration points:
- Included by `gc.h`, used by every backend file.
- `enam.c` must match `enum as` order.
- Object writing in `swt.c` serializes these opcode and address type values.

Risks:
- This is an object format contract; numeric changes affect assembler/linker compatibility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vc/v.out.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/copy.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/copy.c

Purpose: recursively copy reachable Venti blocks from one server to another.

Command behavior:
- Usage: source host, destination host, and starting score, with options for fast destination check, ignore errors, visited memoization, rewrite broken pointers, explicit type, and verbosity.
- Determines the starting block type by probing unless `-t` is supplied.

Core behavior:
- `walk` skips zero scores, optionally skips already visited scores, optionally skips blocks already on destination, reads from source, recursively walks child references by type, writes to destination, and verifies score stability unless rewriting.
- Handles `VtRootType` by walking previous root and root score.
- Handles `VtDirType` by unpacking active `VtEntry` records and walking their scores.
- Handles pointer blocks by walking VtScore-sized score arrays with `type-1`.
- `ScoreTree` AVL memoization avoids revisiting score/type pairs.

Integration points:
- Uses Venti client APIs, `vtrootunpack`, `vtentryunpack`, `vtwrite`, `vtsync`, SHA1, AVL, and bin allocator.

Risks:
- In rewrite mode, unreadable child scores are replaced with zero scores, mutating copied metadata.
- Without `-m`, cycles or repeated shared blocks are handled only by content tree shape and zero checks, not memoization.
- Fast mode trusts destination `vtread` success as proof a block can be skipped.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/copy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/devnull.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/devnull.c

Purpose: minimal Venti server that accepts writes and syncs but stores nothing.

Behavior:
- Listens on an address, defaulting to `tcp!*!venti`.
- Responds to ping, goodbye, write, and sync.
- Read requests return `no such block`.
- Write requests return the SHA1 score of submitted data without persistence.
- Optional verbose mode logs Venti fcalls.

Integration points:
- Uses Venti server APIs `vtlisten`, `vtgetreq`, and `vtrespond`.
- Useful as a sink/test endpoint for Venti clients.

Risks:
- It can appear to accept writes successfully while guaranteeing future reads fail; only appropriate for tests or benchmarking sinks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/devnull.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/mkroot.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/mkroot.c

Purpose: create and write a Venti root block manually.

Behavior:
- Accepts name, type, data score, block size, and previous root score.
- Packs a `VtRoot` and writes it as `VtRootType`.
- Prints the resulting root score.

Integration points:
- Uses Venti client connection and `vtrootpack`.
- Can create Vac-like or other Venti roots when supplied valid fields.

Risks:
- Minimal validation beyond score parsing and numeric blocksize conversion.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/mkroot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/randtest.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/randtest.c

Purpose: randomized Venti read/write throughput and integrity tester.

Behavior:
- Generates deterministic pseudo-random block contents from a seed and template.
- Can write, read, or both; default is both.
- Supports block size, total bytes, max blocks, random byte percentage, permuted order, host, concurrency, and disabling SHA1 double-check.
- `wr` computes expected SHA1 and writes a data block.
- `rd` recomputes expected score and verifies readback bytes.
- `run` emits blocks in sequential or permuted order, optionally dispatching to worker channels.
- Includes a Mitchell/Reeds-style pseudo-random generator (`xxxsrand`, `xxxlrand`).

Integration points:
- Uses Venti client APIs and Plan 9 thread channels.
- Useful for performance and integrity testing of Venti servers.

Risks:
- Concurrent mode starts both read and write workers; caller must choose operation flags appropriately.
- The first word of each generated block is overwritten with the block order value, so templates are not pure random bytes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/randtest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/read.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/read.c

Purpose: read a single Venti block and write raw bytes to stdout.

Behavior:
- Parses a score and optional type/host.
- If type is omitted, probes all Venti types until a read succeeds and prints the discovered invocation to stderr.
- Reads up to `VtMaxLumpSize`, hangs up, and writes the block data to stdout.

Integration points:
- Simple diagnostic/client utility around `vtread`.

Risks:
- Type probing can find the first readable interpretation, which may not be the caller’s intended semantic type.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/read.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/readlist.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/readlist.c

Purpose: batch Venti block read checker for score/type lists.

Behavior:
- Reads from stdin or named files.
- Each line must contain a hex score and numeric type.
- `parsescore` manually decodes 40 hex characters into a 20-byte score.
- `run` reads each listed block and prints progress every 1000 reads; raw output is intentionally commented out.

Integration points:
- Uses `Bio` for input and Venti `vtread`.

Risks:
- Exits fatally on first syntax/read error.
- Does not close Venti connection explicitly before thread exit.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/readlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/ro.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/ro.c

Purpose: read-only Venti proxy server.

Behavior:
- Listens as a Venti server and forwards read requests to an upstream Venti server.
- Ping, goodbye, and sync succeed locally.
- Write requests fail with `read-only server`.
- Read requests are handled in separate threads by `readthread`.

Integration points:
- Uses both Venti client and server APIs.
- Wraps read data with `packetforeign` so the response packet owns the allocated buffer.

Risks:
- One thread per read can be high overhead under heavy load.
- Upstream errors are passed as Venti error responses.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/ro.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/root.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/root.c

Purpose: inspect Venti root blocks.

Behavior:
- Accepts one or more root scores.
- Reads each as `VtRootType`, validates size equals `VtRootSize`, unpacks `VtRoot`, and prints score, quoted name/type, data score, block size, and previous score.
- Continues after per-score parse/read/unpack failures.

Integration points:
- Uses `quotefmtinstall`, Venti score formatting, `vtread`, and `vtrootunpack`.

Risks:
- Hard-coded diagnostic text says wrong size `!= 300`, matching historical `VtRootSize`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/root.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/arena.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/arena.c

Purpose: core Venti arena storage management.

Key responsibilities:
- Initialize existing arenas (`initarena`) from header/trailer and create new arenas (`newarena`).
- Read/write clump data and clump info directory entries.
- Allocate and append new clumps through `writeaclump`.
- Maintain arena memory/disk stats, sealing state, and checksums.
- Load clump-info-group (`cig`) summaries for index readahead and address grouping.

Major behavior:
- Arenas reserve one block for header and one for trailer; usable clump storage is `size - 2*blocksize`.
- `readarena`/`writearena` perform block-aligned partition I/O with bounds checks against clump storage and directory size.
- `writeaclump` seals the arena when a new clump plus directory metadata no longer fits, writes packed clump bytes, updates stats, writes clump info, and writes the trailer.
- `setatailstate` reconciles arena tail state through the main index map.
- `sealarena` queues background checksum work; `sumarena` computes a checksum across the arena with the trailer checksum field zeroed.
- `wbarena` writes the trailer; `wbarenahead` writes the header.
- `loadarena` validates trailer and compares header consistency.
- `loadcig`, `arenatog`, and `asumload` map arena offsets to clump groups and load index entries.

Integration points:
- Depends on server `dat.h`/`fns.h`, partition I/O, dirty block cache, clump pack/unpack, stats, index globals, and background `vtproc`.
- Used by broader Venti server read/write/index code.

Risks:
- Arena locking is central; writes hold `arena->lock`, while background checksum also updates arena state.
- `writearena` and `writeaclump` set `ok = 0` before `putdblock`; any async write failure is not captured here.
- `loadcig` may scan tens of megabytes of table-of-contents data on first access.
- Sealed arenas should be immutable except repairs; code relies on this invariant for checksumming and indexing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/arena.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/arenas.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/arenas.c

Purpose: manage arena partitions, arena maps, and name lookup.

Key behavior:
- Maintains a 512-bucket hash table from arena name to `Arena`.
- `addarena`, `findarena`, and `delarena` manage global lookup.
- `initarenapart` reads an arena partition header, validates block/table layout, reads the arena map, initializes each arena, checks map/name consistency, and registers arenas.
- `newarenapart` creates a new arena partition layout and writes the header.
- `wbarenapart` writes the partition header and arena map.
- `freearenapart` frees maps/arena arrays and optionally unregisters/frees arenas.
- `okamap` verifies sorted non-overlapping arena ranges within partition bounds.
- `maparenas` resolves map names to arena pointers.
- `readarenamap`, `wbarenamap`, `parseamap`, and `outputamap` implement the textual arena map format.

Integration points:
- Calls `initarena`/`freearena` from `arena.c`.
- Uses `Part`, `IFile`, zblocks, format helpers, and name validation helpers.

Risks:
- `Emergency` is a compile-time constant `0`; emergency partial-load paths are present but disabled.
- Map parsing exits early on malformed rows and must free allocated maps on failures.
- Duplicate arena names across partitions are rejected through global lookup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/arenas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/bloom.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/bloom.c

Purpose: Bloom filter for tracking scores present or absent in Venti arenas.

Key behavior:
- `bloominit` initializes size, default hash count, header parsing, bitmask, and data pointer.
- `readbloom` reads/parses the on-disk header and adjusts partition block size upward for large filter I/O.
- `resetbloom` allocates an empty in-memory filter.
- `loadbloom` reads the whole filter and counts set bits for stats.
- `writebloom` writes header plus filter data back to the partition.
- `gethashes` derives double-hash sequence values from SHA1 score bytes and reserves the header bit range.
- `_markbloomfilter` and `_inbloomfilter` perform bit setting/testing.
- Public `inbloomfilter` and `markbloomfilter` wrap access with locks and stats.
- `startbloomproc` launches a background writer thread.

Integration points:
- Uses pack/unpack helpers for Bloom headers, partition I/O, stats, locks, and Venti process/channel primitives.

Risks:
- `gethashes` casts score bytes to `u32int*`, so it assumes acceptable unaligned access for the target environment.
- `ignorebloom` bypasses filtering by making all lookups positive.
- Stats naming in `inbloomfilter` is non-obvious: a positive Bloom result increments `StatBloomMiss`, while a negative result increments `StatBloomHit`, likely reflecting avoided disk lookup semantics rather than membership semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/bloom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/buildbuck.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/buildbuck.c

Purpose: build index buckets from a sorted stream of packed index entries.

Key structures and behavior:
- `IEStream` tracks a partition-backed stream of packed `IEntry` records: read offset, remaining entries, buffer, current position, and end position.
- `initiestream` allocates the stream and buffer.
- `freeiestream` frees stream resources.
- `peekientry` keeps at least one packed `IEntry` available by compacting unread bytes and reading more from the partition.
- `iebuck` computes the bucket number from score hash bits and index divisor.
- `buildbucket` fills an `IBucket` with consecutive stream entries belonging to one bucket, merges duplicate score/type entries by preferring the larger address, checks max bucket data size, and advances the stream.

Integration points:
- Used by Venti index-building code.
- Depends on packed `IEntry` layout having score first, plus `hashbits`, `ientrycmp`, `unpackientry`, and `IBucket`.

Risks:
- Duplicate handling mutates the in-buffer entry when preferring the older larger address path; this is compact but subtle.
- Bucket overflow returns `TWID32` and sets an error.
- Correct bucket grouping assumes input entries are sorted consistently with bucket/hash order.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/venti/srv/buildbuck.c -->