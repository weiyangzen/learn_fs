# Group Research: group_177_9front_sources_os_plan9_9front_sys_src_cmd_spin_pangen2_c_sources_os_e8b832d3fcbe

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen2.c

Central Spin verifier code generator. It emits the generated `pan` verifier files: main C, header, transition table, forward-move code, backward-move code, and BFS_PAR support.

Key behavior:
- `gensrc` orchestrates generation of `pan.c`, `pan.h`, `pan.t`, `pan.m`, `pan.b`, and `pan.p`, or split variants for separate claim generation.
- Emits compile-time feature macros for model properties: claims, event traces, hidden variables, `_last`, priorities, sorted/random channel operations, `np_`, `unless`, embedded C, BFS, fairness, and partial-order reduction constraints.
- Walks every ready process with `putproc`, emits per-proctype transition arrays, source maps, reached arrays, loop-state arrays, and end-state definitions.
- Builds transition entries through `put_seq`, `put_sub`, `put_el`, and `case_cache`, including atomic/d_step handling, unless escapes, dead-link suppression, merge-chain support, case reuse, and transition-to-source mapping.
- Generates forward move code with `putstmnt` for Promela AST nodes: arithmetic/logical expressions, `run`, send/receive/poll, guards, `else`, assignments, assertions, print operations, remote references, embedded C, process deletion, and priority operations.
- Generates matching backward/undo hooks indirectly through case metadata and `pangen4.c`.
- Implements partial-order reduction classification with `Tpe`, `valTpe`, `has_global`, `q_cond` generation, xr/xs checks, timeout/youngest-process conditional safety, and detection of unsafe global references.
- Supports statement merging and multiple backup values through `multi_oval`, `multi_needed`, `CnT`, and dead-variable reset bookkeeping.
- Provides utility routines for claim process lookup, process reversal for initialization, name emission, run-expression validation, target resolution, and atomic-chain/global scanning.

Dependencies:
- Uses Spin parser/runtime structures from `spin.h` and `y.tab.h`: `ProcList`, `RunList`, `Sequence`, `Element`, `Lextok`, `Symbol`, `Queue`, and label/state metadata.
- Includes template/string fragments from `pangen2.h`, `pangen4.h`, `pangen5.h`, and `pangen7.h`.
- Relies heavily on global generation flags and helper functions from the rest of Spin: `ready`, `disambiguate`, `genheader`, `genaddproc`, `genother`, `genaddqueue`, `gencodetable`, `putsrc`, `dumpsrc`, `comment`, `putcode`, `undostmnt`, `any_undo`, `spit_recvs`, and embedded-C plunking helpers.

Research notes:
- This file is the main behavioral bridge from Promela AST/FSM elements to executable verifier C.
- Correctness depends on synchronized forward/backward code generation and on preserving transition ids, source-state numbers, and backup-value ordering.
- Many paths are controlled by generated-code compile macros; changes need testing across normal DFS, BFS, BFS_PAR, bitstate, collapse, TRIX, separate claim, rendezvous, and reduction modes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen2.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen2.h

Template header consumed by `pangen2.c`. It defines large `static const char *` arrays that are copied into generated verifier files.

Key template groups:
- `Pre0`: generated C includes, portability typedef/macros, and basic prototypes.
- `Separate`: generated global storage for transition tables, process/channel offsets, state-vector size, trail prefix, block-on-queue status, and PEG counters.
- `Preamble`: generated verifier globals, stack/hash state, memory counters, hash constants, search flags, randomization flags, BFS/bitstate hooks, and runtime function pointers.
- `Tail`: generated transition helpers and table rewriting logic.

Key generated behavior:
- Defines `settr` and `cpytr` for creating/copying `Trans` records.
- Implements reduction classification helpers `srinc_set`, `srunc`, and `mark_safety`.
- Implements `retrans`, which rewrites transition tables by flattening choice-in-choice transitions, pulling single-step gotos, adding unless escapes, marking reduction safety, detecting mixed selections, propagating stop states, optionally dumping table/DOT output, computing loop states, and reversing transition order when requested.
- Implements `imed`, `tagtable`, `dfs_table`, and `do_dfs` for intermediate-state metadata, reachability traversal, transition-id lookup, and loop-state tagging.
- Implements `crack` and `dot_crack` for human-readable and Graphviz transition-table diagnostics.
- Under `VAR_RANGES`, records and dumps assigned byte-range values for variables.

Dependencies:
- Expects generated symbols and arrays such as `trans`, `procname`, `Btypes`, `accpstate`, `progstate`, `stopstate`, `visstate`, `mapstate`, `t_id_lkup`, `PanSource`, `NTRANS`, `DELTA`, and `HAS_UNLESS`.
- Runtime behavior is tied to macros emitted by `pangen2.c` and structure declarations emitted by `pangen3.h`.

Research notes:
- Despite its `.h` name, this is generated-code payload, not normal API declarations.
- The large hash-constant table and many compile-option branches make this a compatibility-sensitive verifier runtime template.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen3.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen3.c

Source mapping and transition-text rendering support for generated verifier tables.

Key behavior:
- Maintains ordered source-state lists with `putsrc`, `putskip`, and `unskip`.
- `dumpsrc` emits `src_lnN[]` line-number arrays and `src_fileN[]` file-range maps for each process, then emits reached/loop-state data through `dumpskip`.
- Tracks skipped states separately so generated `reachedN[]` starts with states that do not need normal reachability reporting.
- Emits claim/event-trace aliases such as `src_claim`, `src_event`, and `reached_event`.
- `comment` renders a Promela AST node into readable source text for transition labels by using the recursive `comwork` printer.
- `comwork` handles constants/mtypes, expressions, `run`, channel operations, priority operations, receive variants, polling, guards, assignments, print/assert, remote references, embedded C placeholders, control constructs, atomic/d_step markers, and labels/gotos.
- Has special LTL-mode rendering for remote references and remote label equality.

Dependencies:
- Uses `putstmnt`, `putname`, `putremote`, `check_track`, `pid_is_claim`, and `sr_mesg` from other Spin generator/runtime files.
- Writes to generator output streams `tc` and `th`.

Research notes:
- This file is diagnostic/source-correlation infrastructure, but its output is also used by generated reachability checks and table diagnostics.
- Ordered insertion of source and skip records avoids duplicate state entries and keeps generated arrays deterministic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen3.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen3.h

Large generated-runtime template for verifier data structures, process/channel allocation, queue operations, prototypes, and compile-option reporting.

Key template groups:
- `Head0`, `Header`, `Header0`, and `Head1`: define verifier types and compile-mode setup, including `Trans`, `State`, `_Stack`, `Svtack`, `H_el`, `Trail`, BFS trail/state records, TRIX pointer access, vector sizing, fairness fields, and reduction/storage flags.
- `Addp0`/`Addp1`: generated `addproc` body skeleton for process allocation, state-vector growth, offset/skip management, TRIX allocation, fairness bounds, VECTORSZ checks, and initial process field setup.
- `Addq0`/`Addq1` and `Addq11` through `Addq5`: generated queue creation, send, rendezvous checks, xr/xs channel checks, length/full tests, receive extraction, and collapse compression hooks.
- `R0`/`R00`/`R0a`/`R2`/`R3`/`R4`/`R5`/`R6`/`R7a`/`R7b`/`R8a`/`R8b`: snippets for per-process/per-queue initialization, reachability checks, collapse compression, TRIX re-marking, and BFS_PAR mask/offset preservation.
- `R12` through `R15`: queue field receive and undo templates.
- `Proto`: generated function prototypes and core hash/trail/state declarations.
- `SvMap`: generated `to_compile` reporter that reconstructs compile-time `cc -D...` flags.

Key behavior:
- Defines verifier storage layout and the Trail frame fields used by forward/backward move code.
- Provides generated queue semantics including sorted send support, rendezvous channel checks, receive removal/shifting, and event-trace hooks.
- Provides xr/xs assertion enforcement for partial-order reduction soundness.
- Provides collapse-mode process/channel compression templates and BFS_PAR copy-on-mask/offset helpers.
- Records compile configuration for reproducibility.

Dependencies:
- Filled in by generator routines in `pangen2.c`, `pangen4.c`, and related files based on process and queue tables.
- Assumes generated process structs `P*`, queue structs `Q*`, global arrays, and macros from `pan.h`.

Research notes:
- This header is one of the core generated verifier runtime templates.
- Process/channel layout, undo code, collapse compression, and BFS_PAR behavior are tightly coupled; altering one fragment requires checking all generated modes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen3.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen4.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen4.c

Backward-move and queue-undo code generator support.

Key behavior:
- `undostmnt` emits generated code to reverse Promela statements during DFS backtracking.
- Handles undo for `run` by deleting the newest process, sends by `unsend`, receives by `unrecv` plus restoration of backed-up variables, process deletion by `p_restor`, priority updates by restoring saved priority, assignments by restoring `trpt->bup.oval(s)`, and embedded C by `sv_restor`.
- Skips undo for side-effect-free controls such as goto, break, else, printm, and pure polling receives.
- `any_undo` and `any_oper` decide whether a transition needs a backward case.
- `check_proc` recursively finds nested `run` or process deletion operations that must be undone even inside expressions/assertions/prints.
- `genunio` emits `unsend` and `unrecv` implementations for every queue type, including sorted-send slot compaction, rendezvous unblocking, message shifting, and field restoration.
- `proper_enabler` validates expressions allowed in process `provided` clauses and marks `has_provided`.

Dependencies:
- Uses queue metadata from `qtab`, generated templates `R13`/`R14`/`R15` from `pangen3.h`, and statement/name emission from `pangen2.c`.
- Depends on global generation context: `Pid`, `eventmapnr`, `m_loss`, `multi_oval`, `has_sorted`, and `has_provided`.

Research notes:
- This file is critical for state-space search correctness because all destructive forward moves must be exactly reversible.
- Backup-value ordering must match `pangen2.c` forward generation, especially for random receives and merged transitions with multiple backed-up values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen4.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen4.h

Generated template for Spin’s minimized automaton (`MA`) storage backend.

Key behavior:
- Defines DFA data structures `Vertex` and `Edge`, with compact in-node edge slots plus overflow edge lists.
- Provides free-list recycling for edges and vertices.
- Implements transition/range operations: `Delta`, `cacheDelta`, `setDelta`, `numDelta`, edge insertion, edge copying, and edge/range coalescing.
- `dfa_init` builds an initial layered DFA with root, final, and non-final vertices.
- `dfa_store` inserts state-vector byte strings into the minimized automaton, performs path copying when shared nodes need splitting, finds reusable equivalent vertices, updates incoming counts, and recycles unreachable vertices.
- `dfa_member` tests membership by walking the byte string through the DFA.
- Maintains per-layer splay-tree indexes with `insert_it`, `find_it`, `delete_it`, `splay`, `mk_key`, `mk_special`, and equivalence checking through `checkit`.
- `dfa_stats` reports minimized automaton node/edge counts.

Dependencies:
- Included into generated verifier code under `#ifdef MA`.
- Uses generated/runtime symbols such as `nr_states`, `Uerror`, `emalloc`, and byte state-vector data.

Research notes:
- This is a specialized compressed state storage implementation, not normal Spin front-end logic.
- Pointer values are part of hashing/keying, so checkpoint/restart code in `pangen5.h` has to reconstruct pointer-linked graph structure carefully.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen5.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen5.c

Static FSM analysis pass used before verifier code emission.

Key behavior:
- Builds an internal FSM graph from process `Sequence`/`Element` structures with `ana_seq` and `FSM_EDGE`.
- Tracks per-transition variable reads and writes through `ana_stmnt` and `ana_var`.
- `FSM_ANA` performs dataflow analysis to find local variables that become dead after a read/write along all future paths, then attaches dead-variable reset/backup metadata to the originating element.
- `FSM_MERGER` identifies safe statement merge chains and merge starts, excluding blocking operations, alternatives, escapes, labels, remote-reference states, embedded C, priorities, atomic/d_step boundaries, global effects, and unsafe rendezvous cases.
- Uses `build_step`, `eligible`, and `canfill_in` to mark `Element.merge`, `merge_single`, `merge_start`, and `merge_in`.
- Supports optional AST export with predecessor edges and calls to `AST_store`/`AST_slice`.
- Frees/reuses FSM state, transition, and variable-use nodes through local freelists.
- `spit_recvs` emits an `Is_Recv` table and optional `no_recvs` helper for rendezvous optimization.

Dependencies:
- Consumes global process list `rdy`, all elements `Al_El`, Spin AST node types, label helpers, `has_global`, and statement comment printing.
- Produces metadata later consumed by `pangen2.c` and `pangen4.c`.

Research notes:
- This file is an optimization and analysis layer, not final code emission except for receive helper generation.
- Merge analysis is deliberately conservative; many constructs are excluded to preserve partial-order reduction and backtracking correctness.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen5.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen5.h

Generated template for minimized-automaton checkpoint write/read support under `MA` with `W_XPT` or `R_XPT`.

Key behavior:
- Defines buffered checkpoint I/O helpers `xwrite`, `xread`, and `wclose`.
- `w_xpoint` writes an `.xpt` checkpoint containing search counters, DFA depth, root/final/non-final vertices, and all layered DFA trees.
- Serializes vertices and edges by writing pointer identities as keys plus edge ranges and destination pointer values.
- `r_xpoint` reads an `.xpt` checkpoint, recreates temporary pointer-keyed trees, resolves edge destinations, reinserts vertices into the active DFA layers, and restores automaton statistics.
- `x_fixup`, `v_fix`, `v_insert`, `insert_withkey`, and `find_withkey` rebuild graph references after reading pointer identities from disk.
- `x_cpy_rev`, `x_tail`, `x_anytail`, `x_rm_stack`, and `x_remove` identify and remove stack states from the restored automaton, adjusting `nstates`.
- Provides consistency checks for checkpoint depth, buffer counts, missing vertices, duplicate inserts, and stack-state assumptions.

Dependencies:
- Requires the `MA` DFA implementation from `pangen4.h`, including `Vertex`, `Edge`, `layers`, `path`, `R`, `F`, `NF`, `dfa_store`, `dfa_member`, `insert_it`, `splay`, `new_vertex`, `new_edge`, and `recyc_vertex`.
- Uses generated/runtime globals `PanSource`, `MA`, `a_cycles`, `nstates`, `nlinks`, `truncs`, and `truncs2`.

Research notes:
- This is checkpoint/restart machinery for compressed-state searches.
- Because serialized graph references are based on original pointer identities, readback depends on a two-phase reconstruction and fixup pass rather than direct pointer reuse.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen5.h -->