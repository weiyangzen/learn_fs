# Group Research: group_1611_plan9_sources_os_plan9_plan9_sys_src_cmd_spin_pangen2_c_sources_os__2b7a04fdd9cf

Scope verified against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/plan9/plan9`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen2.c

This is Spin’s central `pan` verifier code generator. It writes the generated verifier source files (`pan.c`, `pan.h`, `pan.t`, `pan.m`, `pan.b`, or separate-claim variants), emits transition tables, and translates Promela AST statements into executable C forward and reverse moves.

Key behavior:
- `gensrc()` opens all generated `pan*` output files, emits compile-time feature macros, includes generated template fragments, writes process transition tables, and emits runtime helpers.
- Supports normal, separate source, and separate claim generation through `separate` and `Cfile[]`.
- Generates metadata for claims, event traces, non-progress monitoring, `np_`, fairness, rendezvous, sorted/random receive, `xr`/`xs`, `provided`, `enabled`, `pc_value`, `timeout`, and embedded C code.
- `putproc()`, `put_seq()`, `put_el()`, and `put_sub()` walk process FSM sequences and emit `Trans` table entries plus forward/reverse case labels.
- `case_cache()` emits reusable forward/backward cases, handles merge chains, records backup values for undo, and avoids duplicate emitted code where possible.
- `putstmnt()` translates each Promela AST node into generated C: expressions, assignments, sends, receives, polls, run, asserts, printf, channel operations, remote references, embedded C, and process deletion.
- `putname()` resolves variable references into generated state-vector access paths, including local process structs, globals, arrays, structures, `_pid`, `_`, and hidden names.
- `genconditionals()` emits partial-order reduction conditional-safety tables based on channel reference classes.
- `has_global()` classifies statements and expressions as local/global for partial-order reduction and merge safety.
- `count_runs()` and `any_runs()` enforce restrictions on `run` placement.

Important details:
- This file is tightly coupled to global Spin compiler state from `spin.h`, parser node tags from `y.tab.h`, and template arrays from `pangen2.h`, `pangen4.h`, and `pangen5.h`.
- Forward moves are emitted to `pan.m`; backward undo moves are emitted to `pan.b`; transition metadata is emitted to `pan.t`; shared declarations go to `pan.h`.
- `multi_oval`, `CnT`, and `YZ` track multiple backup values needed to undo merged transitions or receive assignments.
- Receive generation handles normal receive, random receive, poll receive, constant/eval match fields, `_` discard fields, rendezvous blocking, GUI trail display, and fairness counter undo.
- Send generation handles lossy send, sorted send, rendezvous handshakes, `xr`/`xs` checking, and GUI trail display.
- Merge optimization can chain nonblocking safe statements while preserving labels and reverse execution.
- Partial-order reduction safety depends on channel name IDs, not concrete runtime queue IDs, because channel arrays can map to many queues.
- Event-trace processes are special-cased so their send/receive code validates observed operations rather than mutating normal process state.

Filesystem relevance:
- Indirect. This file is not filesystem implementation code, but it creates generated verifier files on disk and emits code that may write trails/checkpoints via other templates.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen2.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen2.h

This header is mostly embedded source text for generated `pan.c`. It provides the generated verifier’s C preamble, runtime global state, transition-rewriting support, transition-table diagnostics, loop-state discovery, and variable-range logging.

Key contents:
- `Pre0[]`: emitted includes, portability macros, `Offsetof`, and `Printf` prototype.
- `Preamble[]`: generated verifier runtime globals and core structs such as `H_el` and `Trail`.
- Runtime flags and counters for memory, depth, state counts, bitstate, fairness, BFS, multicore, randomized exploration, stack cycling, and trail replay.
- `Tail[]`: generated support functions for `Trans` allocation/copying, partial-order reduction classification, transition rewriting, unless expansion, graph/table output, loop-state tagging, and optional variable range logging.

Important details:
- `Trail` records backtracking state: process id, transition id, atomic/fairness flags, saved queue/process data, old transition pointer, and backup scalar or vector values.
- `H_el` is the stored-state hash table element; its fields vary by `FULLSTACK`, `BITSTATE`, `COLLAPSE`, `BCS`, `AUTO_RESIZE`, `NCORE`, and safety/reachability modes.
- The transition rewriting code (`retrans`) expands choices, pulls transitions through intermediate states, handles `unless`, marks partial-order safety, diagnoses unconditional self-loops and duplicate `else`, and can output text or dot graph transition tables.
- Reduction classification maps generator-side statement types into runtime constants such as `LOCAL`, `Q_FULL_F`, `Q_EMPT_F`, `TIMEOUT_F`, `ALPHA_F`, and `GLOBAL`.
- `crack()` and `dot_crack()` print generated transition tables for debugging and visualization.
- `dfs_table()` and `do_dfs()` identify loop states in process automata.
- `VAR_RANGES` support records assigned byte-range values and prints compact intervals.

Filesystem relevance:
- Indirect. The generated verifier uses standard C headers and can report generated compile options; the surrounding generator writes this text into generated files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen3.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen3.c

This file generates source-line maps and readable statement comments for the verifier.

Key behavior:
- Tracks mapping from generated automaton states to Promela source lines and filenames.
- `putsrc()` records source line/file data for a state.
- `putskip()` and `unskip()` track states that should be marked reached even when they are synthetic or do not require normal reachability checks.
- `dumpsrc()` emits `src_lnN[]`, `src_fileN[]`, `src_claim`, and event-source aliases into `pan.h`.
- `dumpskip()` emits `reachedN[]` and `loopstateN` declarations.
- `comment()` renders AST nodes as compact Promela-like source text for transition labels.
- `comwork()` handles expression, channel, send/receive, run, print, assert, remote reference, `atomic`, `d_step`, `unless`, `timeout`, and control-flow syntax.

Important details:
- File ranges are compressed into `S_F_MAP` entries with filename plus state interval.
- `comment()` forces terse/no-cast printing so generated transition labels are source-like rather than executable C.
- In LTL mode, remote references are rendered in user-facing forms like `proc@label`.
- Mtype constants can be printed symbolically via `symbolic()`/`sr_mesg()`.
- Source maps support claim-specific `src_claim` and event-specific `src_event` aliases.

Filesystem relevance:
- Indirect. It records source filenames and line ranges for generated verifier diagnostics, not filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen3.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen3.h

This header contains embedded generated-verifier source fragments for `pan.h` and runtime support around state-vector layout, process/channel allocation, send/receive helpers, assertions, prototypes, and compile-option reporting.

Key contents:
- `Head0[]`, `Header[]`, `Header0[]`, and `Head1[]`: generated `Trans`, stack-frame, saved-vector, and `State` declarations plus compile-mode normalization.
- `Addp0[]`/`Addp1[]`: generated `addproc()` body for allocating process slots in the state vector or TRIX structures.
- `Addq0[]`/`Addq1[]`: generated `addqueue()` body for queue allocation.
- `Addq11[]` through `Addq5[]`: generated queue send, receive, length, fullness, rendezvous, `xr`/`xs`, and collapse-compression helpers.
- `Code0[]`, `Code1[]`, `Code3[]`, `R0[]`, `R0a[]`, `R2[]`, `R3[]`, `R4[]`, `R5[]`, `R6[]`, `R8a[]`, `R8b[]`, `R12[]`: generated initialization and per-process/per-queue setup fragments.
- `R13[]`, `R14[]`, and `R15[]`: generated queue undo helpers `unsend()` and `unrecv()`.
- `Proto[]`: generated prototypes and optional global arrays for `xr`/`xs`.
- `SvMap[]`: generated `to_compile()` function that prints the compile flags used for `pan.c`.

Important details:
- State-vector offsets are kept in `proc_offset[]` and `q_offset[]` unless `TRIX` is used.
- `addproc()` aligns process frames, updates `vsize`, masks padding for compression, initializes `_pid`, and enforces `MAXPROC`/fairness limits.
- `addqueue()` similarly aligns queue frames and initializes queue type metadata.
- Queue operations validate uninitialized/deleted channels, support TRIX backup pointers, event-trace hooks, rendezvous checks, sorted send, random receive, and field count handling.
- `q_S_check()` and `q_R_check()` enforce exclusive sender/receiver claims used by partial-order reduction.
- Collapse compression emits `col_p()` and `col_q()` to pack unmasked process/queue bytes and omit unused queue slots.
- `SvMap[]` preserves compile flags such as `BITSTATE`, `BFS`, `SAFETY`, `NOREDUCE`, `NP`, `COLLAPSE`, `MA`, `TRIX`, `NCORE`, `VECTORSZ`, and memory limits.

Filesystem relevance:
- Indirect. Generated code uses low-level `write()` in optional state-vector dump paths and reports compile commands, but the content is verifier runtime support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen3.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen4.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen4.c

This file emits reverse/backtracking code for generated verifier moves and queue undo helpers.

Key behavior:
- `undostmnt()` emits C code to undo a single Promela statement after backtracking.
- Handles undo for `run`, send, receive, assignments, process deletion, embedded C, assertions/prints containing `run`, and process restoration.
- `any_undo()` tells the generator whether a statement needs a reverse case.
- `any_oper()` searches an AST for a specific operator.
- `check_proc()` finds nested `run` or process-deletion operators that require reverse handling.
- `genunio()` emits generated `unsend()`/`unrecv()` queue restoration logic by queue type.
- `proper_enabler()` validates `provided`/enabler expressions and marks `has_provided`.

Important details:
- Receive undo is the most complex path: it restores removed queue fields, restores variables from `trpt->bup.oval` or `trpt->bup.ovals`, handles random receive index `XX`, and skips pure polls without side effects.
- Send undo calls generated `unsend()` and respects lossy-send mode.
- Assignment undo restores saved lvalue values and recursively handles nested process operations on the right-hand side.
- `genunio()` emits per-queue-type field shifting/zeroing logic for sorted send and receive rollback.
- Rendezvous queues require special blocked-state restoration through `boq`, `UnBlock`, and previous move status.
- `proper_enabler()` rejects local or side-effecting constructs that are not valid process `provided` expressions.

Filesystem relevance:
- Indirect. This is verifier backtracking support; no filesystem implementation logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen4.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen4.h

This header embeds the minimized-automaton (`MA`) runtime used by generated verifiers for graph-encoded state storage.

Key contents:
- `Dfa[]`: generated C code included when `MA` is defined.
- Defines `Edge` and `Vertex` structures for a layered DFA over byte-valued state-vector symbols.
- Maintains `layers`, `path`, root/final/non-final vertices, free lists, cached words, and counters.
- Implements edge insertion/removal, vertex recycling, transition lookup, key generation, splay-tree storage, DFA initialization, membership, insertion, and statistics.

Important details:
- The DFA represents state sets compactly with shared suffix/prefix structure and minimized transitions.
- Each vertex stores two inline transition ranges plus a linked list for additional edges.
- `setDelta()` updates one byte transition while preserving and merging edge ranges/singletons.
- `dfa_store()` checks membership and inserts a new state vector by walking the previous word prefix, reusing existing vertices, splitting shared paths, and recycling unreachable vertices.
- `dfa_member()` tests whether a suffix path reaches the final vertex.
- `insert_it()`, `find_it()`, and `delete_it()` manage per-layer splay trees keyed by transition structure.
- `dfa_stats()` reports node and edge counts for the minimized automaton.
- The algorithm comments credit Anuj Puri, Gerard Holzmann, and earlier graph-encoded-set work.

Filesystem relevance:
- Indirect. This is in-memory state-storage compression for generated verifiers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen5.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen5.c

This file performs static FSM analysis before code generation. It builds per-proctype FSM graphs, computes read/write use information, detects dead local variables, finds safe transition merges, supports AST export, and emits rendezvous-receive metadata.

Key behavior:
- Builds `FSM_state`/`FSM_trans` graphs from `Sequence` and `Element` structures via `ana_seq()` and `FSM_EDGE()`.
- `ana_stmnt()` and `ana_var()` collect read/write uses of variables on each transition.
- `FSM_ANA()` performs dataflow analysis to find local variables that are dead after reads/writes and attaches them to `Element.dead` for generated zeroing/backtracking.
- `FSM_MERGER()` identifies safe nonblocking transitions that can be merged into one generated verifier step.
- `eligible()` and `canfill_in()` screen merge candidates against blocking statements, labels, escapes, remote references, globals, C code, and compound constructs.
- `ana_src()` runs analysis for every process, optionally performs dataflow and merge passes, exports AST/FSM data, and reports unreachable code when verbose.
- `spit_recvs()` emits an `Is_Recv[]` table and optional `no_recvs()` helper for synchronous rendezvous optimization.

Important details:
- FSM state objects, transition objects, and use records are recycled through freelists.
- Dead-variable analysis skips globals, channels, structs, and cases where restoring/zeroing cannot be safely represented.
- Merge analysis distinguishes full merge chains from single eligible follow-on steps and marks `merge`, `merge_start`, `merge_single`, and `merge_in` on elements.
- Blocking operations (`c`, `r`, `s`) are treated conservatively; rendezvous sends are excluded from some merge starts because they can lose atomicity.
- AST export hands retained FSMs to `pangen6.c` via `AST_store()` and then invokes `AST_slice()`.
- The receive table is only emitted for synchronous rendezvous configurations and can conservatively mark `d_step` bodies that begin with receive-like behavior.

Filesystem relevance:
- Indirect. This is compiler analysis for generated verifier quality and state-space reduction.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen5.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen5.h

This header embeds optional checkpoint read/write support for minimized automaton (`MA`) state storage.

Key contents:
- `Xpt[]`: generated code enabled by `MA` plus `W_XPT` or `R_XPT`.
- Buffered checkpoint output helpers `xwrite()` and `wclose()`.
- Serialization routines `w_vertex()`, `w_layer()`, and `w_xpoint()` for writing DFA layers to `<PanSource>.xpt`.
- Buffered input helper `xread()` plus reconstruction routines `r_layer()`, `v_fix()`, `v_insert()`, `x_fixup()`, and `r_xpoint()`.
- Stack-state removal routines `x_remove()`, `x_rm_stack()`, `x_tail()`, `x_anytail()`, and `x_cpy_rev()`.

Important details:
- The checkpoint stores statistics (`nstates`, `truncs`, `truncs2`, `nlinks`), DFA depth, root/final/non-final vertex identities, and every layer tree.
- The file format writes raw pointer values as temporary keys, then rebuilds pointer relationships through `find_withkey()` and `v_fix()`.
- `r_xpoint()` validates `dfa_depth == MA + a_cycles`.
- After loading, the code reconstructs layers, removes stored stack states, adjusts `nstates`, and reports how many stack states were removed.
- Uses fixed 4096-byte read/write buffers and low-level `creat`, `open`, `read`, `write`, and `close`.

Filesystem relevance:
- Direct but tooling-oriented: generated verifiers can persist and reload minimized-automaton checkpoints in `<model>.xpt` files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen5.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen6.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen6.c

This file implements Spin’s AST/FSM slicing analysis for `spin -A`. It uses FSMs collected by `pangen5.c` to identify property-relevant statements, redundant variables/statements, channel aliases, control dependencies, and process-level simplification suggestions.

Key behavior:
- `AST_store()` records each non-claim/non-trace proctype FSM and start state for later slicing.
- `AST_track()` is called during parsing/property handling to collect initial slice criteria from assertions, claims, remote references, and relevant expressions.
- `AST_slice()` orchestrates the full pass: def/use computation, hidden assignment modeling, channel alias analysis, prelabeling assertions, iterative data/control dependency propagation, reporting, and suggestions.
- `def_use()`, `name_def_use()`, and `AST_def_use()` compute detailed use/def/deref-use/deref-def records for transitions, including structs and array indices.
- Channel alias analysis tracks aliases created by assignment, `run` parameters, and channel passing through send/receive.
- `AST_relevant()`, `def_relevant()`, and `AST_indirect()` mark transitions relevant when they define current slice variables, then add variables used by those definitions as new criteria.
- `AST_tagruns()` marks proctypes and `run` statements relevant when a target proctype or its parameters matter.
- `AST_ctrl()` and related helpers propagate control dependencies from blockable transitions that can reach relevant work.
- `AST_dominant()` computes dominators/reverse dominators to find subgraphs that can be treated as irrelevant for control-dependency purposes.
- Reporting functions identify redundant statements, redundant variables, predicate-abstraction candidates, source/sink processes, and buffer-like proctypes.

Important details:
- Relevance uses two bits: data relevance and control/blocking relevance, with `round` recording the iteration that marked a transition.
- Hidden assignments are made explicit for formal-actual parameter passing and initialized variables through synthetic `FSM_trans` records.
- Channel aliases are conservative; receive-based aliasing assumes possible matching sends with the same arity and argument position.
- Remote references mark referenced proctypes relevant.
- Claims, trace processes, and init processes are treated as inherently relevant in several passes.
- Dominator analysis uses bitsets over FSM states, then inverts edges to compute reverse dominance and identify proper subgraphs.
- The analysis intentionally ignores array indices for some mutual-variable comparisons and treats channel/struct cases conservatively.

Filesystem relevance:
- Indirect. This is static analysis over Promela models and generated FSMs, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen6.c -->