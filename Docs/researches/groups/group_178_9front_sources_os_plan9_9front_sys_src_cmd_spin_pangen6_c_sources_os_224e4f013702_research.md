# Group Research: group_178_9front_sources_os_plan9_9front_sys_src_cmd_spin_pangen6_c_sources_os_224e4f013702

Scope: `Docs/research_subset_a.md`, specifically the `sources/os/plan9/9front` tree. I read all seven listed Spin source files completely. The requested internal group report path did not exist before this run.

These files are under 9front's imported Spin model checker source. They are not filesystem implementation code, but they are part of the Plan 9/9front OS source tree in subset A. The group covers property-driven source slicing, generated verifier runtime templates for multicore DFS and parallel BFS, synchronous product construction for multiple never claims, a small PC-only preprocessor, PostScript message-sequence-chart generation, and Promela source reproduction/pretty-printing.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen6.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen6.c

## Purpose

`pangen6.c` implements Spin's AST/FSM based static slicing analysis. It tracks def/use information over Promela statements, discovers channel aliases, marks data- and control-relevant transitions for a given property, reports redundant statements and variables, and suggests simplifications such as predicate abstraction, source/sink process merging, or avoiding buffer processes.

## Key Points

- Builds per-proctype `AST` records over `FSM_state` / `FSM_trans`.
- Tracks `USE`, `DEF`, `DEREF_DEF`, and `DEREF_USE` for expressions, assignments, sends, receives, polls, predicates, `run`, assertions, and printing.
- Performs conservative channel alias analysis through `run` parameters, assignments, initialized locals, and channel names passed through channels.
- Models hidden assignments for formal parameter passing and initialized variables as synthetic `FSM_trans` records.
- Propagates slice relevance through data dependencies, run-target relevance, assertions, claims, remote references, and control dependencies.
- Uses dominator analysis to identify clean proper subgraphs that need not contribute control-dependence criteria.
- Reports redundant statements and variables, and emits suggestions for predicate abstraction or process simplification.

## Important Functions

- `AST_slice()` orchestrates def/use, hidden assignments, alias analysis, relevance iteration, reporting, and suggestions.
- `def_use()` and `AST_track()` walk syntax trees to classify variable references.
- `AST_relevant()`, `def_relevant()`, and `AST_indirect()` propagate relevance from criteria to defining statements and their used variables.
- `AST_alias_analysis()` collects send-derived channel references, formal parameter aliases, assignment/receive aliases, then closes aliases transitively.
- `AST_ctrl()` marks blockable/control-relevant transitions that can influence relevant code.
- `AST_dominant()` computes forward/reverse dominators, records entry/exit pairs, and marks clean subgraphs.
- `AST_dump()`, `AST_dump_rel()`, and `AST_suggestions()` produce human-facing analysis output.

## Dependencies and Risks

The file depends on Spin globals and helpers from `spin.h`, parser tokens from `y.tab.h`, and shared FSM/AST utilities. It mutates FSM transition metadata, uses `fsm_tbl` as a state-number index, and temporarily swaps predecessor/successor lists during reverse-dominance analysis. Channel aliasing is intentionally conservative, so results can over-approximate relevance.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen6.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen6.h

## Purpose

`pangen6.h` is a generated-code template, not a normal C header. It defines string arrays that Spin emits into generated verifier code for multicore verification.

## Key Points

- `Code2e[]` emits platform-specific atomic `tas()` and `cas()` support for multicore/parallel builds.
- `Code2c[]` emits the large `NCORE > 1` multicore verifier runtime fragment.
- Supports POSIX shared memory and Windows file mappings/process creation.
- Defines shared work queue frames (`SM_frame`), result frames (`SM_results`), shared allocation pools (`sh_Allocater`), and many queue/lock/stat globals.
- Implements state handoff, shared hash/bitstate allocation, per-core/local queues, optional global queues, optional disk overflow, termination detection, crash detection, and partial trail-root persistence.
- Handles compile-time modes such as `SEP_STATE`, `SEP_HEAP`, `BITSTATE`, `FULL_TRAIL`, `USE_DISK`, `NGQ`, `MEMLIM`, and platform variants.

## Important Emitted Functions

- `record_info()` / `retrieve_info()` copy and merge worker statistics and reachability data.
- `init_shm()`, `prep_shmid_S()`, `prep_state_mem()`, `init_HT()`, and `cleanup_shm()` manage shared-memory setup/teardown.
- `Get_Full_Frame()`, `Get_Free_Frame()`, `GlobalQ_HasRoom()`, and `Read_Queue()` implement queue protocol and termination-query circulation.
- `mem_put()`, `unpack_state()`, `mem_hand_off()`, and `mem_put_acc()` serialize, restore, and distribute verifier states.
- `write_root()` and `set_root()` save/restore root state frames for trail reconstruction.
- `mem_file()` and `mem_drain()` support disk-backed overflow under `USE_DISK`.
- `sudden_stop()` and `someone_crashed()` handle abnormal termination and crash detection.

## Dependencies and Risks

This file is C source embedded as quoted strings, so escaping and ordering are part of its interface. Correctness depends on generated `pan.c` context: state-vector globals, `new_state()`, `wrapup()`, transition metadata, shared lock macros, and compile-time feature macros. Frame readiness is signaled through `m_vsize`, which writers set last and readers clear after use.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen6.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen7.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen7.c

## Purpose

`pangen7.c` builds a synchronous product automaton when a Promela model has multiple never claims. It constructs tuple states, combines component claim transitions, prunes dead product states, manages accepting/end labels, and prints a generated `never Product` automaton.

## Key Points

- Uses `matrix[n][from][to]` to record each claim's transition elements.
- Represents product states as integer tuples in `OneState.combo`.
- Uses queues `sq`, `sd`, `render`, and `holding` to intern, process, explore, and print product states.
- Rewrites terminal `@` states into true self-loops and creates synthetic accept labels where needed.
- Rewrites `else` in claim options into explicit conditions based on negating other options.
- Rejects unsupported constructs in never-claim products, including `unless`, `atomic`, and `d_step`.
- Prints one unfolded copy per claim so accepting behavior is tracked across multiple claims.

## Important Functions

- `sync_product()` allocates matrices/reachability arrays, reads claims, and starts product generation.
- `get_seq()`, `get_sub()`, `set_el()`, and `t_record()` parse claim sequences into transition matrices.
- `gen_product()` interns and expands product states, prunes dead successors, explores reachable self-loops, prunes unreachable accept labels, and prints the product.
- `all_successors()` recursively enumerates cross-products of component claim transitions.
- `create_transition()` rejects component combinations blocked by explicit false conditions.
- `render_state()`, `state_body()`, and `complete_transition()` print Promela product-state bodies.
- `check_special()`, `mk_accepting()`, `claim_has_accept()`, and `prune_accept()` manage accept/end labels.

## Dependencies and Risks

The file mutates parsed `Element` and `Lextok` structures in place, including `else` conversion and terminal self-loop insertion. It prints directly to stdout. The algorithm assumes claim control-flow states have valid `seqno` values within the computed maximum `nst`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen7.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen7.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen7.h

## Purpose

`pangen7.h` is a generated-code template. Its `pan_par[]` string array emits `pan.p`, the parallel BFS verifier runtime used by generated Spin verifiers compiled with `BFS_PAR`.

## Key Points

- Defines shared BFS structures: `BFS_Slot`, `BFS_data`, and `BFS_shared`.
- Implements shared-memory parallel breadth-first search using System V shared memory and `fork`.
- Supports generation-based queues (`BFS_GEN`), fixed-size queues (`BFS_QSZ`), FIFO mode, disk-backed queues (`BFS_DISK`), staggered sending, and local per-core shared heaps.
- Rejects incompatible modes such as `MA`, `BCS`, `BFS_FIFO` with disk, and `BFS_QSZ` with FIFO/disk.
- Handles state packing/unpacking, duplicate detection, Q-proviso metadata, rendezvous retry/failure, atomic moves, timeouts, event traces, and verification claim scheduling.
- Provides BFS-specific trail reconstruction and error handling.

## Important Emitted Functions

- `bfs_main()`, `bfs_setup_mem()`, `bfs_setup()`, and `bfs_run()` initialize and run the parallel BFS search.
- `bfs_next()` scans incoming queues and handles idle state.
- `bfs_push_state()` routes successors to destination cores.
- `bfs_pack_state()` and `bfs_unpack_state()` serialize/restore states and trail metadata.
- `bfs_explore_state()` generates all successors of a queued state.
- `bfs_store_state()` performs duplicate detection and queues new states.
- `sh_pre_malloc()` and `sh_malloc()` allocate shared/per-core memory.
- `e_critical()` and `x_critical()` implement shared locks with optional owner validation and crash override.
- `bfs_update()`, `bfs_statistics()`, and reachability helpers merge per-core results.
- `bfs_disk_*()` functions manage optional `.spin` disk queues.
- `bfs_uerror()`, `bfs_Uerror()`, and trail writer helpers record BFS error trails.

## Dependencies and Risks

The emitted runtime assumes the generated verifier context provides state structures, transition tables, hash/storage functions, trail globals, and `tas()`. It relies on shared-memory discipline and many compile-time modes. If memory runs out, some paths punt states or shut down, so completeness depends on the selected configuration and available shared memory.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen7.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pc_zpp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pc_zpp.c

## Purpose

`pc_zpp.c` is a small built-in preprocessor used only when `PC` is defined. It reduces reliance on an external C preprocessor in the PC version of Spin. The public entry point is `try_zpp(fnm, onm)`.

## Key Points

- Supports object-like `#define`, `#undefine`, `#ifdef`, `#ifndef`, simple `#if`, `#else`, `#endif`, and `#include`.
- Does not support function-like macros.
- Simple `#if` accepts literal `0`, literal `1`, or a defined macro expanding to `0` or `1`.
- Maintains conditional state with `if_truth[]` and `printing[]`.
- Performs token-bounded textual macro expansion with `apply()`.
- Handles block comments, strings, chars, and escapes with a small lexical state machine.
- Emits `#line` directives to preserve source-location mapping.

## Important Functions

- `do_define()` records a macro, invalidating older definitions of the same name.
- `apply()` performs recursive replacement using two alternating buffers.
- `do_ifdef()`, `do_ifndef()`, `do_if()`, `do_else()`, and `do_endif()` implement conditional output.
- `do_include()` recursively preprocesses included files.
- `in_comment()` blanks block comments while preserving line structure.
- `zpp_do()` reads, joins continuation lines, handles directives, and writes expanded output.
- `process()` dispatches preprocessor directives.

## Dependencies and Risks

This is intentionally incomplete and returns failure for unsupported constructs so callers can fall back to a real preprocessor. It is globally stateful, capped by `MAXNEST`, `MAXDEF`, and fixed buffers, and uses the nonstandard directive spelling `undefine`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pc_zpp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/ps_msc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/ps_msc.c

## Purpose

`ps_msc.c` generates PostScript message sequence charts from Spin simulation or trail runs. It supports Spin's MSC output path by recording process columns, labels, depth mappings, and rendezvous arrows, then writing a multipage `.ps` file.

## Key Points

- `PsPre[]` contains the PostScript prolog and text drawing helpers.
- Layout uses fixed page dimensions, margins, process-column spacing, vertical step spacing, and optional scaling.
- Arrays `I`, `D`, `R`, `M`, `T`, and `L` track initial process labels, depth mappings, x positions, arrows, and event labels.
- `putprelude()` opens the `.ps` output, emits headers, counts trail steps when needed, allocates arrays, and starts page one.
- `putpostlude()` writes remaining pages/trailer, reports the filename, and exits.
- `spitbox()` draws colored event boxes based on label content or `~B`/`~G`/`~R` prefixes.
- `putpages()` handles scaling, pagination, cross-page arrows, event rendering, and label cleanup.
- `dotag()` routes `MSC:` tags to PostScript mode or ordinary textual output depending on column mode.

## Important Functions

- `putlegend()`, `startpage()`, `psline()`, `colbox()`, `putgrid()`, and `stepnumber()` emit low-level PostScript.
- `putarrow()` maps trail-depth message matches into local rendered arrow targets.
- `putbox()` records event process columns.
- `pstext()` records initial process labels or per-depth labels.
- `dotag()` is the integration point called by Spin's tag output path.

## Dependencies and Risks

The generated PostScript strings are built directly from labels, with no obvious escaping in this file. `putpostlude()` terminates the process. The code uses fixed layout assumptions and internal arrays sized by `TotSteps`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/ps_msc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/reprosrc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/reprosrc.c

## Purpose

`reprosrc.c` provides two source-output utilities for Spin: AST-based reproduction of parsed Promela process bodies and lexer-token pretty-printing. Output goes to stdout.

## Key Points

- `repro_src()` prints processes from the ready list `rdy`.
- `repro_proc()` emits deterministic proctype marker `D`, the proctype name, optional `provided`, and body braces.
- `repro_seq()` walks `Sequence` elements, prints labels, `unless`, `do`/`if`, options, nested blocks, ordinary statements, and embedded C forms.
- `repro_sub()` prints `d_step`, `atomic`, and non-atomic blocks.
- `pretty_print()` tokenizes with `lex()` and prints normalized Promela text using indentation and spacing rules.
- `blip()` maps raw characters and parser token constants to printable Promela syntax, using `yylval` for symbol names and constants.
- `purge()` flushes buffered text with indentation and resets declaration/C-code flags.

## Important Behaviors

- AST reproduction reconstructs from Spin's internal normalized representation, not original whitespace.
- Some internal placeholder nodes such as `.`, `@`, and `BREAK` are skipped in AST reproduction.
- Embedded C output delegates to `plunk_inline()` and `plunk_expr()`.
- Preprocessor tokens are printed at indentation zero in pretty-print mode.
- The proctype reproduction here prints `proctype name()` and does not reconstruct original formal parameter lists.

## Dependencies and Risks

The file depends on parser tokens, lexer globals, `rdy`, `has_lab()`, `comment()`, `plunk_inline()`, `plunk_expr()`, and `lex()`. Pretty-print buffering uses fixed-size local buffers, so unusually long token streams on one logical line could be risky.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/reprosrc.c -->