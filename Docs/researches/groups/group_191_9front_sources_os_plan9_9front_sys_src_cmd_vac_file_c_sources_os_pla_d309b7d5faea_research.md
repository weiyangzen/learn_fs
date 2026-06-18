# Group Research: group_191_9front_sources_os_plan9_9front_sys_src_cmd_vac_file_c_sources_os_pla_d309b7d5faea

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/file.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vac/file.c

Purpose: Implements the Vac filesystem object layer, mapping `VacFs`/`VacFile` operations onto Venti `VtFile` trees and Vac metadata blocks.

Key behavior:
- Defines the private `VacFile` with parent/child links, refcounts, cached `VacDir`, data `source`, directory metadata `msource`, read/write locks, dirty/removal state, and qid offset handling.
- Uses an upward metadata lock order: a file may lock its parent to synchronize directory metadata, avoiding parent-to-child lock acquisition.
- Opens roots through `_vacfileroot`, including a Fossil compatibility redirect for roots with an extra level of indirection.
- Provides path walking, child caching, `.`, `..`, refcounting, and lazy opening of child data/meta Venti files from directory entries.
- Implements reads, block-score lookup, entry extraction, size queries, and directory enumeration via `VacDirEnum`.
- Manages directory metadata as a stream of sorted `MetaBlock`s: lookup, allocation, flush, remove, resize, and relocation on long rename.
- Supports mutation for create, write, truncate, set entries, set directory metadata, set qid space, remove, recursive flush, and sync.
- Opens existing Vac roots from `vac:` scores or score files, creates fresh Vac filesystems, writes new Venti root blocks, and preserves previous root score in `VtRoot.prev`.
- Includes helper `sha1matches` for block reuse and `vacfiledsize` for archive diff/extract code.

Dependencies:
- Uses `stdinc.h`, `vac.h`, `dat.h`, `fns.h`, `error.h`, Venti cache/file/block APIs, metadata pack/unpack helpers from `pack.c`, and Vac error strings.

Notable details:
- Directories are two Venti files: traditional directory entry stream plus metadata stream. Plain files are one Venti file.
- `vacfilegetid` returns qid plus accumulated qid offset so merged archives can avoid qid collisions.
- `vacfssync` flushes the whole tree, builds a three-entry root directory, writes a Venti root block, and updates `fs->score`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vac/fns.h

Purpose: Declares shared Vac helper interfaces and constants used by the Vac commands and object layer.

Key behavior:
- Declares metadata block functions (`mbunpack`, `mbinsert`, `mbdelete`, `mbpack`, `mballoc`, `mbinit`, `mbsearch`, `mbresize`).
- Declares metadata entry and directory serialization helpers (`meunpack`, `mecmp`, `mecmpnew`, `vdsize`, `vdunpack`, `vdpack`, `vdcleanup`, `vdcopy`).
- Declares internal root construction and qid management helpers (`_vacfileroot`, `_vacfsnextqid`, `vacfsjumpqid`).
- Declares include/exclude pattern helpers (`glob2regexp`, `loadexcludefile`, `includefile`, `excludepattern`).
- Defines `VacDirVersion = 8` and `FossilDirVersion = 9`.

Dependencies:
- Expects types from `vac.h`, `dat.h`, Venti, and regexp headers included by users.

Notable details:
- The version constants show this tree writes Vac directory metadata version 8 while retaining Fossil version 9 support in the packer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/glob.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vac/glob.c

Purpose: Converts Vac include/exclude glob syntax to regular expressions and evaluates path filters.

Key behavior:
- `glob2regexp` converts `*`, `...`, `?`, character classes, and negated character classes into anchored Plan 9 regexp syntax.
- Treats `*` and `?` specially at the beginning of path elements so dot files are not matched by default.
- `loadexcludefile` reads `include PATTERN` and `exclude PATTERN` lines, ignoring blank lines and comments.
- `excludepattern` appends a command-line exclude rule.
- `includefile` returns the first matching pattern’s include flag, defaulting to include.

Dependencies:
- Uses `Biobuf`, `regexp`, `isspace`, Venti allocation helpers, and `sysfatal` for invalid pattern files.

Notable details:
- Pattern order matters: the first regexp match decides inclusion.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/glob.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/pack.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vac/pack.c

Purpose: Owns the on-disk/in-Venti metadata block, metadata entry, and `VacDir` binary formats.

Key behavior:
- Provides big-endian integer get/put macros for 8/16/32/48/64-bit fields.
- Packs and unpacks counted strings used in directory entries.
- `mbunpack`/`mbpack` validate and emit `MetaBlock` headers, including `MetaMagic+1` compatibility through `unbotch`.
- `meunpack`, `mecmp`, and `mecmpnew` validate entries and compare names for binary search.
- `mbdelete`, `mbinsert`, `mballoc`, `mbcompact`, and `mbresize` maintain index slots and variable-sized entry payloads.
- `vdsize`, `vdpack`, and `vdunpack` serialize `VacDir` fields, version-specific generation fields, Plan 9 metadata, qid-space annotations, and legacy version 7 replacement-score skipping.
- `vdcleanup` and `vdcopy` manage `VacDir` string ownership.
- `mbsearch` performs binary search inside one metadata block and returns either a found entry or an insertion index.

Dependencies:
- Uses `vac.h` constants (`MetaMagic`, `DirMagic`, option tags), `dat.h` structs, Venti allocation helpers, and Vac error strings.

Notable details:
- Metadata offsets and sizes are 16-bit, so metadata blocks must stay below that practical limit.
- Version 9 stores `gen`, `mentry`, and `mgen` in the fixed part; version 8 uses optional generation metadata.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/pack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/stdinc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vac/stdinc.h

Purpose: Common include header for the Vac command sources.

Key behavior:
- Includes Plan 9 system, libc, buffered I/O, ctype, threading, Venti, libsec, and regexp headers.

Dependencies:
- Provides the standard type and API surface expected by Vac implementation files.

Notable details:
- No logic is defined here; it standardizes compilation context.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/stdinc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/testinc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vac/testinc.c

Purpose: Small command-line tester for Vac include/exclude pattern files.

Key behavior:
- Requires one include-file argument.
- Loads patterns with `loadexcludefile`.
- Reads newline-delimited paths from standard input and prints `0` or `1` from `includefile` next to each path.

Dependencies:
- Uses the Vac glob/filter helpers and `Biobuf`.

Notable details:
- This is diagnostic tooling for exclusion behavior, not archive processing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/testinc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/unvac.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vac/unvac.c

Purpose: Extracts, lists, or incrementally updates files from a Vac archive.

Key behavior:
- Opens a Vac archive read-only from a Venti server and recursively walks from the root.
- Supports stdout extraction (`-c`), diff/update mode (`-d`), table/list mode (`-t`), mtime restoration (`-T`), stats (`-s`), host selection, and verbosity.
- Filters extraction by requested path prefixes and tracks missing requested files.
- Skips unsupported stored types such as devices, links, named pipes, and exclusive lock files.
- Creates directories and files with stored permissions unless listing or writing to stdout.
- In diff mode, opens an existing file read/write, compares existing blocks with stored block scores via `sha1matches`, and writes only changed data.
- Optionally restores modification time after extraction.

Dependencies:
- Uses `vacfsopen`, `vacfsgetroot`, `vdeopen`/`vderead`, `vacfilewalk`, `vacfileread`, `vacfiledsize`, `sha1matches`, and Plan 9 `Dir`/`dirmodefmt`.

Notable details:
- `wantfile` includes both ancestors and descendants of requested paths so traversal reaches selected leaves.
- Diff extraction truncates via `dirfwstat` when a partial final read shortens an existing file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/unvac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/vac.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vac/vac.c

Purpose: Main Vac archive creation command.

Key behavior:
- Parses options for archive mode (`-a`), block size, diff source (`-d`), exclude patterns/files, output file, stdin file name, merge mode, quick diff, temp-file skipping, stats, Venti host, and verbosity.
- Creates a new `VacFs` or opens an archive file read/write and creates dated `yyyy/mmdd[.n]` archive directories.
- Walks input paths, expanding root-like path arguments into directory contents.
- Converts Plan 9 `Dir` metadata into `VacDir`, including permissions, append/exclusive bits, qid path/version, owner/group/muid, times, and size.
- Archives directories recursively and files block-by-block.
- Uses previous archive/diff source entries by copying Venti entries first, then rewriting only blocks whose SHA1 does not match current input.
- Quick diff can skip reading unchanged files based on mtime, size, and Plan 9 qid version metadata.
- Merges `.vac` files by copying root children and shifting qid spaces to avoid overlap.
- Records maximum qid in root qid-space metadata before syncing.

Dependencies:
- Uses Vac filesystem APIs from `file.c`, pattern filtering from `glob.c`, Venti connection APIs, Plan 9 directory APIs, and `sha1matches`.

Notable details:
- `-a` is mutually exclusive with explicit output and diff files because archive mode maintains the file as a rotating archive root.
- `vacmerge` uses qid-space metadata when available and falls back to scanned maximum qid.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/vac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/vac.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vac/vac.h

Purpose: Public Vac data model and API declarations.

Key behavior:
- Declares opaque `VacFile` and `VacDirEnum`, plus public `VacFs` and `VacDir`.
- Defines Vac mode bits for Unix/Plan 9 permissions, append, exclusive, link, directory, MS-DOS flags, snapshot, device, and named pipe.
- Defines metadata format constants and optional directory-entry tags.
- `VacDir` stores file name, Venti entry references, size, qid, uid/gid/mid, times, mode, Plan 9 qid metadata, and qid-space annotations.
- `VacFs` stores root score, root file, Venti connection, cache, block size, mode, and qid counter.
- Declares filesystem, file, directory enumeration, metadata, filter, and helper APIs used by `vac`, `unvac`, and `vacfs`.

Dependencies:
- Relies on Venti types such as `VtConn`, `VtCache`, `VtEntry`, `VtScoreSize`, and `Reprog`.

Notable details:
- `ModeDir` duplicates directory-entry state so Vac metadata can carry directory identity independently.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/vac.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/vacfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vac/vacfs.c

Purpose: Exposes a Vac archive as a 9P filesystem.

Key behavior:
- Starts as a mounted filesystem, `/srv` service, or stdio 9P server.
- Opens the requested Vac archive read-only and serves 9P requests from a Venti-backed `VacFs`.
- Maintains a linked list of `Fid` records with user, qid, open state, `VacFile`, and directory enumerator.
- Handles 9P version, attach, walk, open, read, clunk, remove, stat, and read-only errors for write/wstat.
- Converts `VacDir` to Plan 9 `Dir` records with qid offsets, qid-space metadata, append/exclusive/directory flags, sizes, owners, and times.
- Implements directory reads with `VacDirEnum`, preserving unread entries when a stat record will not fit.
- Enforces owner/group/other permission checks unless `-p` disables checks.

Dependencies:
- Uses `fcall.h`, Plan 9 mount/service APIs, Venti formats, and Vac file/directory APIs.

Notable details:
- Although some create/remove handlers exist, the archive is opened with `VtOREAD`; write-side operations return read-only errors in normal use.
- Supports both `9P2000` and `9P2000.u` stat conversion through local compatibility macros.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/vacfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/cgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vc/cgen.c

Purpose: MIPS expression, boolean, lvalue, call, bitfield, and structure code generation for the Plan 9 C compiler backend.

Key behavior:
- `cgen` recursively lowers C expression trees into backend `Prog` instructions, handling assignments, arithmetic, calls, indirection, address generation, casts, conditionals, comma expressions, and pre/post increments.
- Handles hard evaluation order cases by saving complex function-call results into temporaries.
- Uses immediate forms for suitable constant arithmetic/logical operations.
- `genasop` handles compound assignments with careful lvalue address preservation.
- `reglcgen` and `lcgen` compute lvalue addresses, including constant-offset folding for indirect additions.
- `bcgen` and `boolgen` generate branches or boolean values for logical, comparison, constant, conditional, and short-circuit expressions.
- `sugen` copies or initializes structs/unions, rewrites side-effecting destinations, handles struct-return calls, and emits word-copy loops for larger objects.
- `layout` emits small unrolled word-copy sequences used by `sugen`.

Dependencies:
- Uses `gc.h` backend types, register allocators and instruction emitters from `txt.c`, bitfield helpers from `swt.c`, multiply optimization from `swt.c`/`mul.c`, and common compiler tree helpers.

Notable details:
- Structure copies are word-based and choose a small unroll factor before loop emission.
- Floating and integer boolean materialization paths differ: floating comparisons branch via FP compare instructions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/cgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/gc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vc/gc.h

Purpose: Shared header for the `vc` MIPS compiler backend.

Key behavior:
- Includes the generic C compiler header and MIPS object-format definitions.
- Defines target type sizes for 32-bit MIPS and backend constants.
- Declares core backend structures: `Adr`, `Prog`, `Case`, `C1`, `Multab`, `Hintab`, `Var`, `Reg`, and `Rgn`.
- Declares global compiler/backend state, including program lists, case lists, register tracking, variable bitsets, dataflow graph nodes, and optimization regions.
- Defines dataflow macros for loads, stores, bit membership, and cost constants.
- Prototypes codegen, register allocation, peephole, switch, bitfield, output, formatting, and optimizer functions.

Dependencies:
- Depends on generic `../cc/cc.h` and MIPS-specific `v.out.h`.

Notable details:
- `Reg` stores both control-flow edges and backward/forward liveness/synchrony bitsets for global register optimization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/gc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vc/list.c

Purpose: Formatting support for debugging/listing MIPS backend instructions, operands, bitsets, and symbols.

Key behavior:
- `listinit` installs custom formatters for opcodes, programs, strings, names, bitsets, and addresses.
- `Bconv` prints variable bitsets as variable names or constants.
- `Pconv` prints `Prog` instructions, with special formats for `ADATA` and `ATEXT`.
- `Aconv` maps opcode numbers through `anames`.
- `Dconv` renders address forms such as constants, memory references, registers, branch targets, string constants, and floating constants.
- `Sconv` quotes fixed-width symbol/string bytes.
- `Nconv` prints symbol addressing relative to `SB`, `SP`, or `FP`.

Dependencies:
- Uses backend globals from `gc.h`, `var[]`, `pc`, and Plan 9 `Fmt`.

Notable details:
- This file defines `EXTERN` before including `gc.h`, making it the owner of many global definitions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/mul.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vc/mul.c

Purpose: Builds shift/add/sub instruction sequences for multiplication by integer constants.

Key behavior:
- `mulcon0` looks up or computes a compact code sequence for multiplying by a positive constant.
- Maintains a small cache in `multab`.
- Uses a sorted exception `hintab` for constants the search cannot find efficiently.
- Searches sequences up to bounded lengths using `gen1`, `gen2`, and `gen3`.
- `docode` verifies/generated encoded sequences by simulating register values.
- Supports recursive decomposition by factoring powers of two.

Dependencies:
- Uses `Multab` and `Hintab` from `gc.h`; consumed by `mulcon` in `swt.c`.

Notable details:
- The code sequence language encodes shifts as letters and arithmetic as `+`/`-` with operand-selector digits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/mul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/peep.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vc/peep.c

Purpose: Peephole and copy-propagation optimization for generated MIPS `Prog` streams.

Key behavior:
- Completes the `Reg` flow graph for instructions inserted between register optimizer nodes.
- Repeatedly removes redundant register-to-register moves through `copyprop` and `subprop`.
- Converts zero constants to `R0` when profitable and attempts propagation again.
- Removes redundant sign/zero-extension sequences like `MOVB x,R; MOVB R,R`.
- `copy1` walks control flow to substitute source registers while respecting merge points, sets, calls, and read-alter-write hazards.
- `copyu`, `copyau`, `copyas`, and substitution helpers classify and rewrite register uses in instruction operands.

Dependencies:
- Uses `gc.h`, `Reg` graph links, address classes from `v.out.h`, and `excise` by replacing instructions with `ANOP`.

Notable details:
- Calls and returns conservatively block propagation for calling-convention registers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/peep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/reg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vc/reg.c

Purpose: Global register optimizer and dataflow engine for the MIPS backend.

Key behavior:
- Builds a `Reg` node graph over real instructions, excluding metadata pseudo-ops.
- Computes use/set bitsets for tracked variables and builds branch successor/predecessor links.
- Marks loops using reverse postorder and approximate dominators.
- Propagates reference/call liveness backward and register/variable synchrony forward to fixed point.
- Warns on used-not-set and set-not-used variables; excises unused sets.
- Finds profitable live regions with `paint1`, determines conflicting registers with `paint2`, chooses available integer/FP registers, and rewrites code with `paint3`.
- Inserts loads/stores around allocated live regions via `addmove`.
- Recomputes program counters, fixes branch targets, removes nops, and runs peephole optimization.
- Maps allocatable MIPS integer and floating registers to bit masks.

Dependencies:
- Uses backend bitset helpers, `Var` table, `Prog` address classes, `peep`, and target register constants from `v.out.h`.

Notable details:
- Integer register allocation covers R3-R23; FP allocation covers even F4-F22.
- Extern/static/param/address-taken variables are treated conservatively in dataflow.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/reg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/sgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vc/sgen.c

Purpose: Target-specific tree simplification and addressability analysis.

Key behavior:
- `noretval` emits pseudo-uses of integer and/or FP return registers.
- `xcom` computes each node’s `addable` and `complex` values for MIPS code generation.
- Recognizes addressable constants, names, registers, indirect registers, address-of, indirection, and constant-offset additions.
- Rewrites multiplication/division/modulo by powers of two into shifts or masks.
- Swaps immediate-friendly binary operands so constants sit on the right.
- Marks function calls as high complexity (`FNX`) and invokes 64-bit comparison support through `com64`.

Dependencies:
- Uses generic compiler tree helpers from `cc.h`, backend target constants, `simplifyshift`, `vlog`, and `com64`.

Notable details:
- The `addable` scale is target-specific and drives direct addressing versus register-temporary generation in `cgen.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/sgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/swt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vc/swt.c

Purpose: Switch lowering, bitfield helpers, string/static data emission, object output encoding, and alignment for the MIPS backend.

Key behavior:
- `swit1`/`swit2` lower switches as linear comparisons for small case counts and recursive binary-search comparisons for larger sets.
- `bitload` and `bitstore` load, mask, shift, merge, and store C bitfields.
- `outstring`, `sextern`, and `gextern` emit string and global/static data as `ADATA`.
- `mulcon` consumes constant multiply sequences from `mul.c` and emits shift/add/sub instructions.
- `outcode` writes history records, symbol table name records, and encoded `Prog` instructions.
- `zname`, `zaddr`, and `zwrite` implement the compact object-file instruction encoding.
- `outhist` emits source file history records, with Windows path handling.
- `align` and `maxround` define MIPS ABI alignment for structs, arguments, and autos.

Dependencies:
- Uses `gc.h`, `v.out.h` address classes/opcodes, `Biobuf`, `ieeedtod`, and generic compiler type/symbol/history state.

Notable details:
- Argument alignment applies a big-endian adjustment for narrow parameters when `thechar == 'v'`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/swt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/txt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vc/txt.c

Purpose: MIPS backend initialization, register allocation helpers, address lowering, instruction selection, and target type tables.

Key behavior:
- `ginit` initializes target identity, register state, pseudo nodes, return/safe temporaries, and 64-bit support.
- `gclean` checks leaked registers, emits pending strings/globals, appends `AEND`, and writes object code.
- Provides program allocation (`nextpc`), argument passing (`gargs`, `garg1`), constant/register node constructors, and register allocation/free helpers.
- Converts compiler `Node`s into backend `Adr`s with `naddr`/`raddr`.
- `gmove` selects load, store, register move, integer/FP conversion, unsigned integer to FP fixup, and special FP constants.
- `gopcode` maps generic compiler operations to MIPS opcodes, including multiply/divide LO/HI handling and integer/FP branch generation.
- Provides branch, patch, pseudo-op, small-constant, stack/register-variable, and target type-width/cast tables.

Dependencies:
- Uses all backend structures from `gc.h`, object constants from `v.out.h`, and generic compiler globals.

Notable details:
- Floating-to-integer conversion temporarily changes FP control register rounding unless `fproundflg` allows a simpler path.
- Special double constants are synthesized from dedicated FP constants/registers where possible.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/txt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/v.out.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vc/v.out.h

Purpose: MIPS object-code constants for the Plan 9 `vc` compiler and related tools.

Key behavior:
- Defines symbol/register counts and text flags.
- Defines MIPS integer and floating register assignments used by the backend ABI.
- Enumerates MIPS opcodes, including core arithmetic/branch/load/store, FP operations, MIPS64-like extensions, dynamic/init pseudo-ops, switch pseudo-ops, and object markers.
- Defines address type/name constants such as branch, memory, extern/static/auto/param, constants, registers, FP registers, file names, and vlong constants.
- Defines `SYMDEF` and the simulated IEEE double layout used for object encoding.

Dependencies:
- Included by `gc.h` and object emitters.

Notable details:
- Register names encode Plan 9 backend conventions: stack is R29, static base is R30, link is R31, and R0 is the zero register.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vc/v.out.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vcrop.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vcrop.c

Purpose: Interactive Plan 9 image cropper.

Key behavior:
- Reads an image from stdin or a named file and displays it in a draw window.
- Left-drag pans the image; middle-click invokes rectangle crop; right-click opens a menu with crop, undo, save, and exit.
- `crop` clamps the selected rectangle to image bounds, creates a new image, stores the previous image for one-level undo, and resets position.
- `save` prompts for an output filename and writes the current image.
- Handles window resize and Delete-key exit.

Dependencies:
- Uses Plan 9 draw, mouse, keyboard, thread, image read/write, and `getrect`/`enter`.

Notable details:
- Ignores tiny crop rectangles below a 5-pixel threshold in both dimensions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vcrop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vdiff.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vdiff.c

Purpose: Graphical diff/patch viewer for Plan 9.

Key behavior:
- Parses unified/git-style diff input from files or stdin into patches, file blocks, and typed lines.
- Renders collapsible file blocks with different colors for file headers, hunk separators, additions, deletions, normal lines, and trailing whitespace.
- Supports dark mode (`-b`) and path-component stripping for plumbed edit targets (`-p nstrip`).
- Provides scrollbar, mouse wheel/buttons, keyboard navigation, horizontal panning, expand/collapse menu, and patch-selection menu.
- Right-clicking a diff line plumbs `file:line` to the editor.
- Handles multi-patch input separated by the `⑨` marker and names patches from diff hashes when available.

Dependencies:
- Uses Plan 9 draw, mouse, keyboard, plumb, buffered I/O, and thread APIs.

Notable details:
- Tabs are rendered visibly and trailing spaces are highlighted.
- Long lines are clipped with an ellipsis based on current horizontal pan.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vdiff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/copy.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/copy.c

Purpose: Recursively copies a Venti block graph from one Venti server to another.

Key behavior:
- Parses source host, destination host, and a starting score; optionally detects type or uses `-t`.
- Walks root, directory, pointer, and data blocks; root blocks recurse into previous roots and root scores.
- For directory blocks, unpacks active `VtEntry`s and walks their scores by entry type.
- For pointer blocks, walks non-zero child scores with type decremented.
- Writes each block to the destination and verifies score stability unless rewrite mode is enabled.
- Supports fast skipping when the destination already has a block, ignore-errors mode, rewrite-missing mode, visited-score memoization, and verbosity.

Dependencies:
- Uses Venti read/write/root/entry APIs, SHA1, AVL trees, and bin allocation.

Notable details:
- `-r` rewrites unreadable child scores to zero and repacks parents, changing the graph and reporting pointer changes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/copy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/devnull.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/devnull.c

Purpose: Minimal Venti server that accepts writes and discards data.

Key behavior:
- Listens on an address, defaulting to `tcp!*!venti`.
- Responds to ping, goodbye, write, and sync.
- For writes, returns the packet SHA1 score without storing data.
- For reads, returns a `no such block` error.
- Optional verbose request/response logging.

Dependencies:
- Uses Venti server request APIs, threading, packet SHA1, and Venti formatters.

Notable details:
- Useful for testing write clients without persistent storage.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/devnull.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/mkroot.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/mkroot.c

Purpose: Creates and writes a Venti root block from command-line fields.

Key behavior:
- Accepts root name, type, data score, block size, and previous root score.
- Packs a `VtRoot`, writes it as `VtRootType`, syncs the server, and prints the resulting root score.
- Supports optional Venti host selection.

Dependencies:
- Uses Venti connection, score parsing, root packing, write, and sync APIs.

Notable details:
- This is a low-level root-construction utility independent of Vac-specific metadata.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/mkroot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/randtest.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/randtest.c

Purpose: Venti read/write throughput and integrity test using deterministic pseudo-random data.

Key behavior:
- Generates blocks from a template seeded by a custom PRNG, with each block tagged by its order index.
- Writes blocks to Venti and optionally double-checks returned scores against locally computed SHA1.
- Reads blocks back by recomputing their scores and verifies byte-for-byte data.
- Supports configurable block size, total bytes, max blocks, seed, randomness percentage, permutation, read/write selection, concurrency, host, and disabling double SHA1 checks.
- Reports MB/s for write and read phases.

Dependencies:
- Uses Venti read/write APIs, SHA1, Plan 9 threads/channels, and a Mitchell-Reeds style PRNG.

Notable details:
- Multi-thread mode starts both read and write worker pools and feeds block buffers over channels.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/randtest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/read.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/read.c

Purpose: Reads one Venti block by score and writes its raw bytes to stdout.

Key behavior:
- Parses a score and optional host/type.
- If no type is specified, probes all Venti block types until a read succeeds and prints a reproducible command to stderr.
- Writes the retrieved block payload to stdout.

Dependencies:
- Uses Venti score parsing, connection, read, and formatting APIs.

Notable details:
- Allocates a full `VtMaxLumpSize` buffer to support any block type.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/read.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/readlist.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/readlist.c

Purpose: Batch Venti block reader for lists of score/type pairs.

Key behavior:
- Reads one or more files, or stdin, containing two fields per line: hex score and type.
- Parses exactly 40 hex score characters into a 20-byte score.
- Reads each listed block from the Venti server.
- Prints progress every 1000 reads; payload writing is present but commented out.

Dependencies:
- Uses Venti read APIs and Plan 9 `Biobuf`.

Notable details:
- This is mainly a cache/server stress or validation utility, not a data extraction tool in its current form.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/readlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/ro.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/ro.c

Purpose: Read-only Venti proxy server.

Key behavior:
- Listens for Venti requests on one address and connects to an upstream Venti server.
- Passes through ping, goodbye, and sync responses.
- Services read requests in separate threads by reading from upstream and returning packet-backed data.
- Rejects writes with a read-only error.
- Supports verbose logging and separate listen/upstream addresses.

Dependencies:
- Uses Venti server/client APIs, packet foreign buffers, and Plan 9 threading.

Notable details:
- Each read allocates a buffer sized to the requested count and transfers ownership to the response packet.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/ro.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/root.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/root.c

Purpose: Prints decoded Venti root blocks.

Key behavior:
- Connects to a Venti server and processes one or more root scores.
- Reads each score as `VtRootType`, validates root block size, unpacks `VtRoot`, and prints score, quoted name/type, root data score, block size, and previous root score.
- Continues after parse/read/unpack failures for individual arguments.

Dependencies:
- Uses Venti root unpacking, score parsing, connection APIs, and quote formatting.

Notable details:
- Hard-checks the read size against `VtRootSize`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/root.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/arena.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/arena.c

Purpose: Implements Venti server arena lifecycle, clump data I/O, clump-directory access, arena sealing, checksumming, and clump-info group indexing.

Key behavior:
- `initarenasum` starts a background checksum worker for sealed arenas.
- `initarena` loads an arena from disk header/trailer, validates stats, and schedules sealing if needed.
- `newarena` creates a fresh arena with a valid header/trailer, randomized clump magic for newer versions, and an initial zero block.
- Reads and writes clump directory entries through `readclumpinfo`, `readclumpinfos`, and `writeclumpinfo`; directory blocks are stored in reverse order at the end of the arena.
- `readarena` and `writearena` perform bounded block-cache I/O inside the clump data region.
- `writeaclump` appends a packed clump, updates memory stats, compressed counts, clump info, clump-info group starts, timestamps, and arena trailer.
- `setatailstate` advances disk tail state across arenas in index order and seals arenas whose state becomes sealed.
- `backsumarena`, `sumproc`, and `sumarena` asynchronously compute and write SHA1 checksums for sealed arenas.
- `wbarena` and `wbarenahead` write trailer and header blocks.
- `loadarena` reads trailer/header metadata and logs inconsistencies between them.
- `okarena` validates basic size and count relationships.
- `loadcig`, `arenatog`, and `asumload` build and use clump-info-group offset tables for index-entry readahead.

Dependencies:
- Uses Venti server `dat.h`/`fns.h`, partition I/O, disk cache blocks, clump pack/unpack helpers, arena pack/unpack helpers, stats, tracing, scheduler hooks, SHA1, and global `mainindex`.

Notable details:
- Arena usable data excludes one header block before and one trailer block after the arena body.
- `writeaclump` seals the arena when the next clump plus directory growth would exceed arena size.
- Sealed arena checksums treat the checksum field itself as zero during SHA1 calculation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/venti/srv/arena.c -->