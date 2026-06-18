# Group Research: group_176_9front_sources_os_plan9_9front_sys_src_cmd_spin_pangen1_h_e49deb27e64c

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen1.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen1.h

## Scope And Read Status

Read completely: 8,700 lines, 238,474 bytes.

This file is in the 9front source tree under `sys/src/cmd/spin`, but it is not Plan 9 kernel, VFS, or filesystem implementation code. It is a large C string-template header used by Spin to generate the `pan.c` verifier. Its contents are mostly string literals in `Code2a[]` and `Code2d[]` that are emitted into generated verifier C code.

## Primary Role

`pangen1.h` supplies the generated verifier runtime for Spin models:

- verifier startup and `run()` tail behavior
- DFS and BFS state-space exploration
- trail file creation/replay
- assertion and end-state reporting
- partial-order reduction
- weak fairness and liveness cycle checks
- bitstate hashing, full-state hashing, hash compaction, and graph encoding
- process/channel state-vector save, restore, deletion, and reconstruction
- optional multicore/shared-memory search coordination
- optional disk-backed BFS/stack spill support

The file is a generator payload, not normal compiled application code by itself. The arrays terminate with `0` and are consumed by Spin’s code-generation path.

## Major Generated Sections

`Code2a[]` begins with the end of generated `run()` and covers early runtime support:

- Initializes global state, state tables, hash tables, bitstate arrays, DFS/BFS stacks, never claims, active processes, event traces, and optional C-code model initialization.
- Provides simple pthread-like model helpers: `spin_malloc`, `spin_free`, `spin_join`, mutex helpers, and condition-variable helpers.
- Defines critical-section wrappers for multicore runs and `cpu_printf`.
- Defines `Printf` behavior for verification/replay mode.
- Implements stack-frame access through `getframe`, including optional stack compression/spill mode (`SC`) using `open`, `lseek`, and `read`.
- Implements `pan_exit`, trail transmogrification, source lookup, trail replay discovery, and trail replay execution.
- Implements bitstate storage variants `bstore_mod` and `bstore_reg`.
- Implements trail creation via `make_trail`.
- Implements BFS support, including queueing, state snapshot storage, optional disk-backed BFS temporary files, and BFS trail emission.

`Code2d[]` continues with the main verifier runtime:

- Timer setup/reporting, crash detection timing, and search startup.
- `do_the_search`, `do_transit`, optional `do_reverse`, event-trace matching, `enabled`, priority helpers, snapshots, and stack-to-disk spill/reload for `SC`.
- Claim selection and process-order permutation helpers.
- Main DFS routine `new_state`, including pseudo-recursive descent/backtracking, depth limits, rendezvous handling, atomic/d_step handling, partial-order preselection, fairness rules, bounded context switching, randomized ordering, acceptance/non-progress cycle handling, and trail support.
- Search summary and memory statistics in `wrap_stats`/`wrapup`.
- `main` option parsing for generated `pan` options.
- Allocators `Malloc` and `emalloc`.
- Error handling with `dfs_uerror`/`dfs_Uerror`.
- Unreached-state reporting.
- Trail writing with `puttrail` and multicore full-trail reconstruction.
- State-vector save/restore, process/channel restore/delete, queue empty/end-state checks.
- Compression, stack membership, hash initialization, state storage, and optional closed hashing with locality (`USE_TDH`).
- Ends by including generated `TRANSITIONS`.

## Filesystem And Storage Relevance

This file does not implement a filesystem, VFS, block layer, or Plan 9 storage interface. Its filesystem interaction is limited to verifier artifacts:

- Trail discovery and replay: `findtrail()` opens trail files using candidate names derived from `TrailFile`, suffixes, and multicore `cpuN_trail` variants.
- Trail creation: `make_trail()` creates files with `open(..., O_CREAT|O_WRONLY|O_TRUNC[, O_EXCL], TMODE)` and writes verifier step records.
- Trail output: `puttrail()`, `putter()`, `nuerror()`, and related helpers write transition triplets and metadata markers.
- Stack spill mode (`SC`): `stack2disk()`, `disk2stack()`, and `getframe()` use a `stackfile` for trail-frame spill/reload through `creat`, `open`, `write`, `read`, and `lseek`.
- BFS disk mode: under `BFS_DISK`, BFS states can be written to and read from temporary files named like `pan_bfs_%d.tmp`.
- State-vector dump mode (`SVDUMP`): writes `.svd` data for stored states.
- Checkpoint naming appears through `R_XPT`/`W_XPT` in graph-encoding mode, but the checkpoint implementation is external (`r_xpoint`, `w_xpoint`).

These are ordinary host-file uses by a model checker, not filesystem subsystem behavior.

## Key Data And State Concepts

Important generated runtime objects referenced throughout:

- `now`: current global state vector.
- `trail`/`trpt`: DFS/BFS trail stack and current trail frame.
- `Trans`: transition descriptors generated from the Promela model.
- `H_el`: hash-table state element.
- `Svtack` and `_Stack`: saved state/process/channel restoration stacks.
- `Mask`: bytes excluded from compressed state matching.
- `H_tab`, `S_Tab`, `SS`: full-state hash table, stack hash table, and bitstate array.
- `processes[]`/`channels[]`: TRIX tree-index compression bodies when enabled.
- `BFS_State`, `SV_Hold`, `EV_Hold`: BFS queue and saved state/mask holders.
- `A_Root`, `A_depth`, `_a_t`, `_cnt`: liveness/fairness cycle checking state.

## Search Behavior

The generated verifier supports multiple compile-time modes:

- DFS default search with `new_state`.
- BFS mode via `bfs`.
- Parallel BFS through `BFS_PAR`.
- Multicore DFS through `NCORE>1`.
- Bitstate search through `BITSTATE`.
- Full-stack and counter-stack matching through `FULLSTACK`/`CNTRSTACK`.
- Hash compaction through `HC`.
- Collapse compression through `COLLAPSE`.
- Graph encoding through `MA`.
- Tree index compression through `TRIX`.
- Partial-order reduction unless `NOREDUCE`.
- Safety-only builds through `SAFETY`.
- Acceptance/non-progress cycle detection through `-a`, `-l`, `NP`, and fairness flags.

The DFS engine uses an explicit trail stack and labels/gotos for pseudo-recursion. It stores each state in a selected storage backend, detects old/on-stack states, applies provisos for partial-order reduction and liveness, and backtracks by reversing transitions.

## Hashing And Compression

The file emits several hashing paths:

- Paul Hsieh “super fast hash” variant for 32-bit hashing (`d_sfh`).
- Jenkins-style 32-bit/64-bit mixing (`d_hash`).
- Optional 64-bit MurmurHash3 (`m_hash`) when `MURMUR && WS==8`.
- Random hash polynomial generation (`hashgen`).
- Seeded alternate hash functions for closed hashing (`o_hash32`, `o_hash64`).

Compression modes include:

- Default masked-byte compression using `Mask`.
- Hash-compaction mode where state vectors are represented by hash fragments.
- Collapse compression that interns globals, processes, and queues into ordinal templates.
- Compact stack representation for bitstate stack matching.

## Error, Trail, And Reporting Flow

Errors are reported through `uerror`/`Uerror` function pointers set to DFS or BFS implementations. For DFS:

- `dfs_uerror` prints the error with depth.
- It writes a trail when configured or when reaching the requested error count.
- It supports iterative shortest-path reduction for safety checks.
- It handles multicore termination signaling and wrapping up.

Trail files contain line records like `depth:proc:transition_id`, plus negative metadata records for claim type, merged statements, transition/process order randomization, and cycle start.

`wrapup()` prints configuration, state counts, transition counts, hash conflicts, memory usage, unreached states, optional peg counts, variable ranges, and mode-specific diagnostics.

## Process And Channel State Handling

The generated runtime models Promela processes and channels inside a flat state vector or TRIX bodies:

- `Pptr`/`Qptr` return safe process/channel pointers or dummy pointers for missing entries.
- `sv_save`/`sv_restor` save and restore entire state vectors.
- `p_restor`/`q_restor` restore deleted processes/channels from `_Stack`.
- `delproc`/`delq` remove process/channel bodies, update offsets/masks/vector size, and optionally save data for reversal.
- `qs_empty` and `endstate` check termination validity.

This is model-state manipulation, not OS process or kernel channel management.

## Notable Risks Or Quirks

- The file is highly compile-time-conditional; behavior depends on many macros and generated includes (`FORWARD_MOVES`, `BACKWARD_MOVES`, `TRANSITIONS`).
- It uses fixed-size buffers in several artifact paths (`fnm[512]`, `snap[64]`, trail naming buffers), typical of this Spin codebase.
- Some generated paths intentionally use `goto` and pseudo-recursion for performance and compact verifier generation.
- Disk-backed BFS and stack-spill paths assume sequential temporary-file behavior and abort on read/write/lseek mismatch.
- A few sections are compatibility scaffolding for invalid/unsupported macro combinations, emitting placeholder functions or compile-time errors.

## Research Classification

For filesystem research, classify this file as:

- Component: Spin generated verifier runtime template.
- Filesystem relevance: incidental host-file I/O for verifier trails, temp state spill files, state dumps, and checkpoints.
- Not a filesystem implementation.
- Not part of Plan 9 kernel storage/VFS behavior.
- Useful only if studying verification tooling bundled in 9front or host-file usage patterns in command-line tools.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen1.h -->