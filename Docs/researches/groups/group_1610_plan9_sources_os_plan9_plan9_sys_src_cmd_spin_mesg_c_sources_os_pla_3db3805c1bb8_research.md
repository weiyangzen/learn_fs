# Group Research: group_1610_plan9_sources_os_plan9_plan9_sys_src_cmd_spin_mesg_c_sources_os_pla_3db3805c1bb8

Scope: `Docs/research_subset_a.md` only.  
Files researched completely:
- `sources/os/plan9/plan9/sys/src/cmd/spin/mesg.c`
- `sources/os/plan9/plan9/sys/src/cmd/spin/pangen1.c`
- `sources/os/plan9/plan9/sys/src/cmd/spin/pangen1.h`

These files are part of Plan 9’s bundled Spin model checker sources, not Plan 9 kernel/filesystem implementation code. They matter to the subset as source-tree content under `sources/os/plan9/plan9`.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/mesg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/mesg.c

## Purpose

`mesg.c` implements Spin’s runtime/simulation handling for Promela channels and messages. It manages channel queue allocation, asynchronous and rendezvous sends/receives, queue inspection, message trace output, and semantic checks that prevent invalid channel manipulation in Promela expressions.

## Main Responsibilities

- Creates queue instances for `chan` initializers through `qmake`.
- Maintains global queue registries:
  - `qtab`: linked list of all queues.
  - `ltab[MAXQ]`: direct queue lookup by one-based queue id.
  - `nqs`: number of allocated queue types/instances.
- Implements channel predicates:
  - `qfull`
  - `qlen`
  - `q_is_sync`
- Executes send/receive operations:
  - `qsend`
  - `qrecv`
  - `a_snd` for buffered channels.
  - `s_snd` for rendezvous channels.
  - `a_rcv` for receive/poll/test behavior.
  - `sa_snd` for sorted send insertion.
- Emits trace/debug output for Spin, XSpin, and columnated traces.
- Dumps queue contents for simulation display.
- Checks invalid channel assignments and risky array self-indexing.

## Important Data Flow

`qmake(Symbol *s)` is the creation path. If a symbol initializer is a `CHAN`, it allocates a `Queue`, assigns a one-based `qid`, records slot count and field count, allocates `contents`, `fld_width`, and `stepnr`, then stores the queue in both `qtab` and `ltab`.

`qsend(Lextok *n)` evaluates the channel expression, maps it to `ltab[whichq]`, and chooses buffered or rendezvous send based on `nslots`.

`qrecv(Lextok *n, int full)` evaluates the channel expression and calls `a_rcv`. It special-cases `STDIN` as pseudo-channel id zero when the channel evaluates to uninitialized id `-1`.

Buffered receive first checks executability by matching constants and `eval(...)` receive arguments. For non-FIFO random receive forms, it can scan later queue slots. If `full` is true and the operation is not a poll, it assigns received values and shifts the queue down.

Rendezvous send temporarily stores message fields in the zero-slot queue, calls `complete_rendez()`, and only commits the synchronized send if a matching receive exists.

## Key Functions

- `cnt_mpars`: counts message fields, expanding compound field declarations through `Cnt_flds`.
- `qmake`: allocates and initializes queue metadata and storage.
- `qfull`, `qlen`, `q_is_sync`: queue predicates used by Promela expressions.
- `qsend`: public send dispatcher.
- `qrecv`: public receive dispatcher plus `STDIN` support.
- `sa_snd`: sorted insertion point and slot shift for sorted sends.
- `typ_ck`: optional type-clash warning for channel-related fields.
- `a_snd`: buffered send implementation.
- `a_rcv`: buffered receive, poll, and executability test implementation.
- `s_snd`: rendezvous send implementation.
- `channm`: builds printable channel names, including struct/array references.
- `docolumns`, `difcolumns`, `sr_talk`, `sr_buf`, `sr_mesg`: trace formatting.
- `doq`: prints queue contents for a channel symbol.
- `qhide`, `qishidden`: suppress trace output for selected channels.
- `nochan_manip`: rejects invalid use/assignment of channel names and tracks accesses.
- `newbasename`, `delbasename`, `checkindex`, `scan_tree`, `no_nested_array_refs`: detect array self-index patterns such as `a[a[1]]`.
- `no_internals`: blocks assignments to internal system variables `_nr_pr` and `_p`.

## Dependencies

The file depends heavily on Spin’s AST and symbol infrastructure from `spin.h` and `y.tab.h`, including `Lextok`, `Symbol`, `Queue`, `RunList`, `eval`, `setval`, `cast_val`, `Sym_typ`, `Width_set`, `getuname`, `complete_rendez`, `pstext`, `whoruns`, `fatal`, and `non_fatal`.

Global flags such as `verbose`, `TstOnly`, `s_trail`, `analyze`, `columns`, `depth`, `xspin`, `m_loss`, and `jumpsteps` alter both semantics and reporting.

## Notable Behavior

- Queue ids are one-based externally and zero-based in `ltab`.
- Zero-slot channels are still allocated with one storage slot internally so rendezvous values can be staged.
- `m_loss` controls behavior when a buffered send targets a full queue.
- `TstOnly` makes send/receive paths act as executability tests without mutating queue state.
- `n->val` selects variants such as sorted send, FIFO/random receive, and poll behavior.
- `columns == 2` produces MSC-style differential column traces through `pstext` and `putarrow`.
- The predefined variable `_` is treated specially in rendezvous trace output as a write-only placeholder.

## Risks and Maintenance Notes

This is old C with fixed-size local buffers and repeated `strcat`/`sprintf` use. Most inputs are Promela identifiers or generated/internal strings, but the code assumes those upstream constraints hold.

`sr_mesg` uses `fprintf(fd, Buf)` instead of `fprintf(fd, "%s", Buf)`. In normal Spin usage `Buf` is built from numbers or mtype identifiers, but the pattern is still fragile.

The channel semantics are tightly coupled to global interpreter state. Any change to `TstOnly`, rendezvous bookkeeping, or receive variants needs regression coverage across buffered channels, zero-slot rendezvous channels, sorted send, poll, and trail replay output.

## Filesystem Relevance

No filesystem implementation logic is present. Filesystem interaction is limited to stdout/stderr style reporting; this file is relevant only because it is part of the Plan 9 source tree.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/mesg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen1.c

## Purpose

`pangen1.c` is part of Spin’s verifier generator. It writes generated verifier C code, mainly into `pan.c`, `pan.h`, and related generated files through global output streams `tc`, `th`, and `tt`.

It combines model metadata, process lists, queues, labels, variable declarations, and large string-template fragments from `pangen1.h`, `pangen3.h`, and `pangen6.h`.

## Main Responsibilities

- Generates verifier headers and state-vector layout.
- Emits process type structs and queue structs.
- Emits process and channel initialization code.
- Emits claim, progress, accept, stop, visible, and reached-state tables.
- Emits helpers for global/local variable printing.
- Emits queue runtime functions for generated verifier code.
- Emits support for sorted/random receive, rendezvous, TRIX compression, BFS/DFS modes, multi-claim models, and provided clauses.

## Output Streams

- `th`: generated header-like verifier declarations and structs.
- `tc`: generated verifier implementation body.
- `tt`: generated transition/provided support, especially `provided(...)`.

The file’s behavior is mostly `fprintf` and `ntimes` template expansion over those streams.

## Key Generation Paths

`genheader()` writes foundational verifier definitions:
- Word size and channel counts.
- `NCORE` defaults.
- User-defined names.
- Process names and process type categories.
- `P<n>` process structs.
- Multi-claim wrapper process if needed.
- State-vector `State`.
- TRIX-specific state storage structures.
- Hidden variables and predefined write-only `_`.

`genaddproc()` writes:
- TRIX channel re-marking helper.
- `addproc(...)`.
- Optional `provided(...)`.
- Multi-claim initialization.
- `np_` predefined process.
- Per-proctype initialization cases.

`genother()` writes:
- State-table code fragments.
- Label-derived arrays for stop/progress/accept states.
- Reachability reporting setup.
- `iniglobals(...)`.
- Main verifier body templates such as DFS/BFS support.

`genaddqueue()` writes:
- Queue type definitions `Q<n>`.
- Queue metadata arrays `q_flds` and `q_max`.
- `addqueue`.
- `qsend`, `qrecv`, `q_len`, `q_full`, and queue size helpers.
- Optional `Q_has` for random receive polling.

## Important Functions

- `reverse_names`, `reverse_types`: emit process metadata in reverse list order.
- `blog`: computes enough bit width for generated bitfields.
- `genheader`: top-level state-vector and proctype header generation.
- `genaddproc`: add-process generation and process initialization dispatch.
- `genother`: state tables, reachability, globals, and main verifier body generation.
- `gensvmap`: emits state-vector map template.
- `end_labs`: maps labels to `stopstate`, `progstate`, `accpstate`, and `visstate`.
- `ntimes`: expands template arrays, substituting an index into repeated `%d` placeholders.
- `checktype`: warns that integer-like declarations could be narrowed to `bit` or `byte`.
- `dolocal`, `doglobal`: enumerate model variables in declaration/type order for initialization, logging, or struct emission.
- `c_chandump`, `c_var`, `c_splurge`, `c_wrapper`: generate runtime variable/channel dump helpers.
- `dohidden`: emits hidden globals and predefined `_`.
- `do_var`, `do_init`: generate initialization/logging code for scalar, array, struct, and channel variables.
- `put_ptype`: emits process struct declarations and `Air<n>` size macros.
- `tc_predef_np`: emits the built-in `np_` process metadata.
- `multi_init`: emits multi-never-claim selection initialization.
- `put_pinit`: emits initialization case for a proctype.
- `huntstart`, `huntele`: find executable control-flow entry states through gotos, unless blocks, and atomic/d_step structure.
- `typ2c`: maps Promela types to generated C fields.
- `qlen_type`: picks compact queue length storage type.
- `genaddqueue`: emits generated queue runtime code.

## Data and Model Coupling

The file depends on global parser/generator state:
- Process list: `rdy`, `nrRdy`, `Pid`.
- Queue list: `qtab`, `ltab`, `nqs`.
- Labels: `labtab`.
- Symbols: `all_names`, `Fname`, `lineno`.
- Claims and traces: `nclaims`, `claimnr`, `eventmapnr`.
- Feature flags: `separate`, `old_scope_rules`, `has_sorted`, `has_random`, `has_provided`, `has_io`, `has_state`.

Generated code depends on many symbols emitted elsewhere, including transition tables, state vector helpers, queue pointer helpers, C code fragments, and templates from other `pangen*.h` files.

## Notable Behavior

- `separate` controls whether normal processes and claims are generated together or split.
- Multi-claim support replaces concrete claims in the state vector with an aggregate claim process storing active claim type/state/index and per-claim current states.
- Claims are not allowed to define locals; `dolocal` reports this as an error for `N_CLAIM`.
- Channel initialization calls `qmake`, then emits either a queue id or `addqueue(...)` depending on whether a dynamic channel must be created in generated verifier state.
- Queue field widths are compacted based on Promela field types; unsupported channel field specs are fatal.
- State labels inside `atomic`/`d_step` blocks produce warnings because they may be invisible.
- `provided` clauses are emitted as a generated switch over proctype/state.

## Risks and Maintenance Notes

This file is a code generator built around `fprintf` templates and global mutable state. Small changes can affect generated C in many compile modes.

The generated verifier has many mutually interacting options: BFS, TRIX, multi-core, bitstate, compression, hash compaction, fairness, bounded context switching, claims, randomization, and rendezvous. Changes to emitted structs or queue layouts must stay synchronized with generated runtime functions and template assumptions in `pangen1.h`.

Because it emits C identifiers and string fragments from model symbols, correctness depends on parser-side sanitization and name mangling.

## Filesystem Relevance

No filesystem algorithm is implemented. The generated verifier can emit and read trail files, stack spill files, and temporary BFS disk files through template code, but this file itself is generator logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen1.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen1.h

## Purpose

`pangen1.h` is not a conventional declaration header. It contains large static arrays of C string literals used by `pangen1.c` to generate Spin’s verifier source. The main arrays are:

- `Code2a[]`: startup/runtime support, trail replay, BFS support, bitstate setup, and related verifier scaffolding.
- `Code2d[]`: timers, main search routines, DFS/BFS dispatch, hashing, error handling, trail writing, compression, state storage, option parsing, and memory management.

The generated output becomes part of `pan.c` and related verifier code.

## Major Generated Components

### `Code2a[]`

`Code2a` emits the tail of generated `run()` and several runtime helpers:

- State table printing and dot-output exit path.
- BFS/TRIX allocation before global initialization.
- `iniglobals(...)` and initial never-claim/process startup.
- Partial-order reduction stutter-invariance warning.
- Bitstate hash-array initialization and repeated hash runs.
- Stack/state-vector allocation.
- `Printf` and `cpu_printf` wrappers.
- Disk-backed stack frame retrieval under `SC`.
- `pan_exit`.
- C-code trail text transmogrification for embedded `{c_code...}` references.
- Source/trail replay helpers:
  - `wrap_trail`
  - `findtrail`
  - `getrail`
- Trail file creation through `make_trail`.
- Bitstate storage variants:
  - `bstore_mod`
  - `bstore_reg`
- TRIX restore/repopulate support.
- BFS data structures and logic:
  - `SV_Hold`
  - `EV_Hold`
  - `BFS_Trail`
  - `getsv`
  - `getsv_mask`
  - `push_bfs`
  - `pop_bfs`
  - `store_state`
  - `bfs`
  - `putter`
  - `nuerror`

### `Code2d[]`

`Code2d` emits most of the generated verifier runtime:

- Timing and snapshot functions:
  - `start_timer`
  - `stop_timer`
  - `snap_time`
  - `snapshot`
- Multi-core crash detection:
  - `crash_reset`
  - `crash_test`
  - optional alert reporting.
- Search entry point:
  - `do_the_search`
- Generated transition dispatch:
  - `do_transit`
  - `do_reverse`
  - includes generated `FORWARD_MOVES` and `REVERSE_MOVES`.
- Event trace handling:
  - `require`
- Predicate support:
  - `enabled`
- Main DFS engine:
  - `new_state`
- Assertions and bounds:
  - `spin_assert`
  - `Boundcheck`
- Statistics and shutdown:
  - `wrap_stats`
  - `wrapup`
  - `stopped`
- Hashing:
  - optional SuperFastHash.
  - Jenkins 32-bit or 64-bit hash.
  - `d_hash`
  - `s_hash`
  - mask setup.
- Main program option parsing:
  - `main`
  - `usage`
- Memory allocation:
  - `Malloc`
  - `emalloc`
- Fatal and recoverable error handling:
  - `Uerror`
  - `uerror`
- Trail writing:
  - `puttrail`
  - multi-core reverse trail support.
- State-vector save/restore:
  - `sv_save`
  - `sv_restor`
  - `p_restor`
  - `q_restor`
- Dynamic process/channel removal:
  - `delproc`
  - `delq`
- End-state and cycle checks:
  - `qs_empty`
  - `endstate`
  - `checkcycles`
- Stack matching:
  - `onstack_init`
  - `grab_state`
  - `onstack_put`
  - `onstack_now`
  - `onstack_zap`
- Hashtable initialization:
  - `hinit`
- Compression/state storage:
  - collapse compression via `ordinal` and `compress`
  - default compression
  - hash compact support
  - MA graph encoding via `gstore`
  - TRIX `sv_populate`
  - main `hstore`
- Final inclusion of generated transition tables through `#include TRANSITIONS`.

## Search Semantics Encoded

The generated DFS/BFS logic supports many Spin verification modes:

- Safety checking.
- Acceptance cycle detection.
- Non-progress cycle detection.
- Weak fairness.
- Partial-order reduction.
- Rendezvous behavior.
- Atomic and `d_step` sequencing.
- Timeout/stuttering behavior.
- Never claims and multi-claim selection.
- Event trace and negated trace checking.
- Bounded context switching.
- Randomized process or transition ordering.
- Bitstate/supertrace approximation.
- Full-stack and counter-stack matching.
- Hash compaction and collapse compression.
- Multi-core state handoff.
- TRIX tree index compression.
- Breadth-first search with optional disk spill.

## Compile-Time Coupling

This template is governed by dense preprocessor combinations, including:

`BFS`, `TRIX`, `BITSTATE`, `FULLSTACK`, `CNTRSTACK`, `SAFETY`, `VERI`, `NOREDUCE`, `NOFAIR`, `NP`, `NCORE`, `SEP_STATE`, `HAS_CODE`, `HAS_UNLESS`, `HAS_PROVIDED`, `EVENT_TRACE`, `COLLAPSE`, `HC`, `MA`, `BCS`, `REACH`, `SVDUMP`, `MEMLIM`, `SC`, `RANDSTOR`, `P_RAND`, and `T_RAND`.

Many incompatible combinations are rejected in generated `main` with `#error`, runtime warnings, or option validation.

## Filesystem and Storage Behavior

Although this is not filesystem implementation code, generated verifier code performs several file operations:

- Trail creation and replay:
  - `.trail`, `cpuN_trail`, and custom suffix trail files.
  - Read-only trail mode with `-T`.
  - Exclusive trail creation with `-x`.
- Stack spill under `SC`:
  - `stack2disk`
  - `disk2stack`
  - configurable stack file.
- BFS disk spill:
  - temporary `pan_bfs_<n>.tmp` files.
- State-vector dump:
  - `<PanSource>.svd`.
- MA checkpoint hooks:
  - `R_XPT`
  - `W_XPT`.

These are verifier artifact operations, not Plan 9 filesystem behavior.

## Risks and Maintenance Notes

This file is highly sensitive generated-code infrastructure. The search algorithm is encoded as strings, so normal C compiler checking applies only after generation. Template syntax, escaping, and `%` formatting must remain exactly aligned with `pangen1.c`’s `fprintf` and `ntimes` usage.

The generated code uses fixed-size buffers, raw `sprintf`/`strcpy`/`strcat`, and many global variables. Most inputs are controlled by Spin’s own generated names and command-line options, but the style is legacy and fragile.

`new_state` is intentionally macro-heavy and difficult to read. The file itself recommends preprocessing generated `pan.c` for a chosen mode before studying or modifying the search routine.

Any change here should be verified by generating and compiling `pan.c` across representative modes: plain DFS, `-DSAFETY`, `-DBITSTATE`, `-DBFS`, `-DNOREDUCE`, `-DNP`, `-DTRIX`, multi-claim verification, and models with rendezvous channels.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen1.h -->