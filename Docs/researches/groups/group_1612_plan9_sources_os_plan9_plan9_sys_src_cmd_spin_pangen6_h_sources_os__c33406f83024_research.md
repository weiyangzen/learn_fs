# Group Research: group_1612_plan9_sources_os_plan9_plan9_sys_src_cmd_spin

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/plan9` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen6.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen6.h

This file is not ordinary compiled C for Spin itself; it is a generated-code template, `static char *Code2c[]`, emitted into generated `pan` verifiers when `NCORE>1`. It contains the multi-core verifier support layer for Spin 5.x-era pan code.

The template defines shared-memory queue frames (`SM_frame`), result aggregation records (`SM_results`), and shared allocation pools (`sh_Allocater`). It supports both Unix/System V shared memory and Windows file mappings. The frame layout serializes a verifier state vector, mask bits, process and channel offsets/skips, C tracked-state stack data under `C_States`, and optional `FULL_TRAIL` stack-tree links.

Major generated subsystems:
- Multi-core configuration constants: `NCORE`, `VMAX`, `PMAX`, `QMAX`, queue sizes, crash/termination timing, and disk spill limits.
- Shared memory setup: `init_shm`, `prep_shmid_S`, `prep_state_mem`, `init_HT`, `init_SS`, and platform-specific cleanup.
- Interprocess locking: `tas`, `e_critical`, `x_critical`, `iam_alive`, and crash detection via shared `is_alive`.
- State handoff: `mem_put`, `mem_put_acc`, `mem_hand_off`, `Get_Free_Frame`, `Get_Full_Frame`, `GlobalQ_HasRoom`.
- Queue reading and termination detection: `Read_Queue` circulates `QUERY`, `QUERY_F`, and `QUIT` control frames and folds per-core stats with `record_info`/`retrieve_info`.
- Error trail support: `cur_Root`, `write_root`, `set_root`, and optional `Stack_Tree` history for `FULL_TRAIL`.
- Optional disk overflow path under `USE_DISK`: `mem_file`, `mem_drain`, and disk stats/cleanup.

Notable constraints and coupling:
- Multi-core mode explicitly rejects `BFS`, `SC`, and some `MA` combinations.
- State handoff is blocked in certain atomic/rendezvous/claim-move situations to preserve verifier semantics.
- `m_vsize` is used as the publication flag and is written last when filling a frame.
- The code assumes fixed upper bounds for serialized process/channel metadata; exceeding them requires recompilation with larger `VMAX`, `PMAX`, or `QMAX`.

Risk notes:
- This template uses manual shared memory layout and pointer arithmetic with word-alignment fixes; portability and 32/64-bit behavior depend on the generated compile environment.
- It uses busy waits and timeout heuristics for crash and termination detection.
- Some counters are intentionally read outside locks for performance, relying on benign races.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen6.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen7.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen7.c

This file builds the synchronous product of multiple never claims. It is used when the model contains more than one claim and Spin needs a single product never claim named `Product`.

Core data structures:
- `OneState`: one product-state vector, `combo`, plus successor list.
- `SQueue`: queue/list wrapper for product states.
- `Succ_List`: links immediate successor product states.
- `State_Stack`: recursion stack for rendering and loop detection.
- `Guard`: accumulated transition guard list while collapsing intermediate states.

The product construction starts in `sync_product()`. It allocates per-claim state matrices, tracks initial states (`Ist`), accept-state counts (`Nacc`), reachable states, self-loop states, and an `Element ****matrix` indexed by claim/from/to. It then scans all never-claim sequences with `get_seq()` and records transitions with `t_record()`.

Important behavior:
- `get_seq()` rejects `unless`, `atomic`, and `d_step` constructs inside product claims where they cannot be handled.
- `set_el()` converts terminal `@` nodes into true self-loops and marks them accepting through `mk_accepting()`.
- `IF`/`DO` suboptions are converted into explicit matrix transitions; `else` guards are rewritten into negated disjunctions of earlier guards.
- `gen_product()` enumerates the Cartesian successor relation across all claims, prunes dead-end transitions, explores reachable product states, prunes unreachable synthetic accept labels, then prints one unfolded copy per claim.
- `check_special()` emits `accept` and `end` labels and handles pseudo-acceptance for claims without accept labels unless strict mode is enabled.
- `state_body()` recursively skips structural/non-atomic states and emits guarded Promela transitions through `complete_transition()`.

Output shape:
- On first unfolding it prints `never Product {`.
- Each unfolding section is labeled with `/* ============= U%d ============= */`.
- Product states are named `P_<state0>_<state1>..._U<unfolding>`.

Risk notes:
- `retrieve_state()` appears to assign `sd = nq` when removing the head instead of `sd = nq->nxt`; this is old source and may depend on surrounding assumptions, but it is a suspicious removal pattern.
- The algorithm uses global mutable state heavily (`sq`, `sd`, `render`, `holding`, `dsts`, `unfolding`, `not_printing`), so it is tightly coupled to single-threaded code generation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pangen7.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pc_zpp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pc_zpp.c

This is a small built-in preprocessor used only under `#ifdef PC`, intended to reduce dependence on an external C preprocessor in the PC version of Spin.

Supported preprocessor features:
- Object-like `#define` without arguments.
- `#undefine`.
- `#ifdef`, `#ifndef`, simple `#if 0`/`#if 1` or matching defined-symbol values.
- `#else`, `#endif`.
- `#include` with quoted or angle-bracket filenames.
- `#line` and numeric line directives.
- `#error` and `#warning`.

Major functions:
- `try_zpp(fnm, onm)` opens the output and runs `zpp_do`.
- `zpp_do()` reads the input file, handles line continuations, strips comments, applies directives, emits `#line` markers, and writes macro-expanded lines.
- `process()` dispatches directive names to handler functions.
- `do_define()` stores simple macro mappings in a fixed `MAXDEF` table.
- `apply()` repeatedly expands known macros using two static output buffers.
- `in_comment()` implements a small lexer state machine that tracks strings, character quotes, and C comments.
- `strip_cpp_comments()` removes `//` comments, with a simple escaped-slash check.

Limits and fallback behavior:
- `MAXNEST` is 32 conditional levels.
- `MAXDEF` is 128 defines.
- `MAXLINE` is 2048 and macro expansion uses 8192-byte buffers.
- Function-like macros are not supported; encountering one returns failure so Spin can fall back to an external `cpp`.
- Complex `#if` expressions are unsupported unless reducible to `0` or `1`.

Risk notes:
- `apply()` has a questionable boundary test around `in2+j == '\0'`; `in2+j` is a pointer, so this condition does not test the character value. The intended check is likely `*(in2+j) == '\0'`.
- Include handling recursively calls `zpp_do` but does not manage include search paths.
- Macro expansion is intentionally lightweight and not a full C preprocessor.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/pc_zpp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/ps_msc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/ps_msc.c

This file generates PostScript message sequence chart output for Spin simulation runs, supporting Spin’s `-M` style MSC output.

Main state:
- `PsPre[]` is a PostScript prolog defining text rendering, ISO encoding, and color adjustment.
- Page geometry constants define page width/height, margins, process-line spacing, step spacing, and process tag height.
- Arrays `I`, `D`, `R`, `M`, `T`, and `L` map simulation depth to rendered rows, labels, process columns, and message arrows.
- `ProcLine` tracks which process lifelines have already been drawn on a page.
- `pspno`, `ldepth`, `maxx`, `TotSteps`, and `Scaler` track pagination, scaling, and chart extent.

Major functions:
- `putprelude()` creates `<model>.ps`, writes headers/prolog, optionally counts trail length, allocates chart arrays, and starts the first page.
- `startpage()` writes page headers, legend, process headers, clipping region, and coordinate transform.
- `putlegend()` prints Spin version, model file name, MSC label, and page number.
- `spitbox()` draws colored event boxes, with color selected by message marker or by send/receive symbols.
- `putarrow()` records matching send/receive relationships by depth index.
- `putpages()` performs final pagination, draws step numbers, boxes, lifelines, and red arrows, handling arrows crossing page boundaries.
- `pstext()` records process labels/events during simulation.
- `dotag()` either routes MSC-tagged text into PostScript mode or prints normal simulation text.

Integration:
- `sched.c` uses `pstext()` when `columns == 2`.
- `run.c` printing functions eventually call `dotag()`.
- Trail replay affects `TotSteps` by counting lines from the trail file.

Risk notes:
- Fixed-size strings and manual `sprintf` are used for output names and labels.
- Long labels can affect box width but there is no deep escaping for arbitrary PostScript-special characters beyond normal formatted insertion.
- The module exits the process in `putpostlude()` after finalizing the PostScript file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/ps_msc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/reprosrc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/reprosrc.c

This file reconstructs a readable Promela source representation from Spin’s internal parsed process list and sequence graph.

Main behavior:
- `repro_src()` starts from global `rdy` and calls `repro_proc()`.
- `repro_proc()` recursively walks to the end of the process list first, then prints each proctype in original-like order. It preserves deterministic proctype marker `D`, `provided` clauses, and the body.
- `repro_seq()` walks a `Sequence` from `frst` to `last`, printing labels, statements, branches, loops, and unless constructs.
- `repro_sub()` prints nested `d_step`, `atomic`, or non-atomic blocks.

Construct handling:
- Labels are recovered through `has_lab(e, 0)`.
- `UNLESS` is rendered as a normal block followed by an `unless` block.
- `DO` and `IF` nodes print `do`/`if`, each option with `::`, then `od`/`fi`.
- `ATOMIC`, `D_STEP`, and `NON_ATOMIC` nodes recurse into their nested sequence.
- Terminal/internal nodes `.`, `@`, and `BREAK` are suppressed.
- `C_CODE` and `C_EXPR` are printed through `plunk_inline()` and `plunk_expr()` respectively.
- Other statements use `comment(stdout, e->n, 0)` and append a semicolon.

State:
- Uses a single static `indent` counter and `doindent()` to print three spaces per indentation level.

Purpose in the larger Spin code:
- This is a pretty-printer/reproducer for the parsed AST/sequence representation, useful for diagnostics or source normalization.
- It depends on parser-created `Element`, `Sequence`, `SeqList`, label, and inline code structures defined and declared through `spin.h`.

Limitations:
- It is a reconstruction, not a token-preserving formatter.
- Comments, exact whitespace, and some syntactic sugar are not preserved.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/reprosrc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/run.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/run.c

This file implements the random/interactive simulator’s expression and statement execution engine. It evaluates Promela AST nodes and advances `Element` program counters.

Main execution functions:
- `eval_sub(Element *e)` evaluates one executable element or compound construct and returns the next `Element` to execute.
- `eval(Lextok *now)` evaluates expression/statement AST nodes and performs side effects for sends, receives, assignments, prints, `run`, assertions, and C fragments.
- `Enabled0(Element *e)` and `Enabled1(Lextok *n)` test whether a statement or compound branch is executable.
- `pc_enabled()` implements `enabled(pid)` by temporarily switching `X` to another running process.
- `complete_rendez()` is in `sched.c`, while this file’s `eval_sync()` restricts rendezvous partner matching to synchronous receives.

Important semantics:
- `eval_sub()` handles `GOTO`, `UNLESS`, `IF`, `DO`, `ATOMIC`, `D_STEP`, `NON_ATOMIC`, stop states, and normal statements.
- Branch choice is random unless interactive mode is active or `indstep` forces deterministic selection.
- Escape sequences are tested around normal statements unless replaying a trail; Java-like reverse escape priority is supported via `rev_escape()`.
- `D_STEP` and `ATOMIC` blocks splice their internal sequence into the outer continuation by setting the nested last element’s `nxt`.
- Rendezvous mode (`Rvous`) suppresses non-receive operations and changes behavior of gotos/else.
- `eval()` sets `lineno` and `Fname` before handling a node, keeping diagnostics tied to source location.

Side-effecting node support:
- `ASGN` goes through `assign()`, performs type checking, and delegates to `setval`.
- `ASSERT` reports failed assertions and may call `wrapup(1)`.
- `PRINT` and `PRINTM` go through `interprint()` and `printm()`, feeding `dotag()` for normal or MSC output.
- `C_CODE` and `C_EXPR` are uninterpreted in analysis mode and printed/evaluated through inline C plunking in simulation mode.

Risk notes:
- Arithmetic evaluation does not guard division/modulo by zero in this file.
- `interprint()` appends into fixed buffers and only checks length after formatting.
- Many functions temporarily mutate global flags such as `TstOnly`, `verbose`, `E_Check`, and `Escape_Check`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/run.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/sched.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/sched.c

This file owns Spin’s simulation scheduler, process/run lists, local variable runtime state, process creation, claim startup, rendezvous completion, and final reporting.

Global runtime state:
- `rdy` is the parsed process/proctype list.
- `run` is the active process list.
- `X` is the currently selected running process.
- `LastX`, `LastStep`, `nproc`, `nstop`, `Tval`, `Rvous`, `depth`, `nrRdy`, `Have_claim`, and `Skip_claim` control simulation state.
- `Priority_Sum` supports weighted random process selection.

Process lifecycle:
- `ready()` registers a parsed proctype/claim/init/trace in `rdy`.
- `runnable()` instantiates a `ProcList` into a `RunList`, assigns pid/priority, initializes program counter, and marks end states.
- `enable()` implements Promela `run`, checking `MAXP`, creating a runtime process, setting parameters, and initializing locals.
- `start_claim()` starts a selected never claim, moves it to pid 0, and shifts other pids.
- `wrapup()` prints final process/global/local state and process counts.

Scheduling:
- `pickproc()` chooses the next process by priority-weighted randomness or interactive user selection.
- `sched()` is the top-level driver. It handles table dump mode, product generation, verifier source generation, guided trail replay, then runs the random/interactive simulation loop.
- It evaluates provided clauses, calls `eval_sub()`, prints trace output, preserves atomic and d_step execution where required, detects blocked systems, enables timeout, and removes terminated processes.
- `silent_moves()` skips gotos, unless wrappers, atomic wrappers, and `.` pseudo-steps.

Rendezvous:
- `complete_rendez()` temporarily sets `Rvous`, searches another process for a matching synchronous receive, executes it, updates that process PC, and restores interactive state.

Local state:
- `addsymbol()`, `setlocals()`, `setparams()`, and `oneparam()` create per-process symbol tables.
- `findloc()`, `getlocal()`, and `setlocal()` resolve and mutate locals, including struct fields through `Rval_struct`/`Lval_struct`.

Remote references:
- `f_pid()`, `remotelab()`, and `remotevar()` resolve remote labels, `_p`, and remote variables, accounting for never-claim pid shifting.

Risk notes:
- Interactive mode stores choices in 256-sized arrays and skips pids above 255.
- Scheduler behavior depends heavily on global state and temporary context switches.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/sched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/spin.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/spin.h

This is the central shared header for the Spin front end, simulator, and pan-code generator sources in this directory.

Core type definitions:
- `Lextok`: AST node with token type, value, source location, inline id, symbol, sequence/list links, and left/right children.
- `Symbol`: symbol-table entry with name, unique id, type, visibility/hidden flags, array and bit-width metadata, runtime values, struct metadata, channel access metadata, initializer, owner/context, and next link.
- `Queue`: runtime channel instance with queue id, length, slot/field counts, field widths, contents, and send-step metadata.
- `Element`: executable control-flow node with AST pointer, global/local sequence numbers, merge metadata, status bits, sub/escape sequences, and linked-list edges.
- `Sequence` and `SeqList`: statement sequence and lists of alternatives.
- `Label`: label binding to symbol, context, element, inline id, visibility, and next link.
- `RunList` and `ProcList`: active runtime process instance and parsed proctype/claim/init/trace definition.
- FSM/dataflow types used by pangen slicing logic: `FSM_state`, `FSM_trans`, and `FSM_use`.

Important enums and constants:
- Process/body categories: `NONE`, `N_CLAIM`, `I_PROC`, `A_PROC`, `P_PROC`, `E_TRACE`, `N_TRACE`.
- Element status flags: `DONE`, `ATOM`, `L_ATOM`, `I_GLOB`, `DONE2`, `D_ATOM`, `ENDSTATE`, `CHECK2`, `CHECK3`.
- Symbol/channel/type constants: `XR`, `XS`, `XX`, `CODE_FRAG`, `CODE_DECL`, `PREDEF`, `UNSIGNED`, `BIT`, `BYTE`, `SHORT`, `INT`, `CHAN`, `STRUCT`.
- Size constants: `Nhash`, `SOMETHINGBIG`, `RATHERSMALL`, `MAXSCOPESZ`.

The header also defines `YYSTYPE` as `Lextok *`, null sentinels `ZN`, `ZS`, `ZE`, portability write mode `MFLAGS`, and a broad set of prototypes spanning parsing, scheduling, evaluation, channel operations, code generation, struct handling, C-code embedding, labels, assertions, trail replay, and diagnostics.

Architectural role:
- This header exposes most subsystem boundaries through C prototypes rather than opaque interfaces.
- It makes `Lextok`, `Symbol`, and `Element` the shared currency across parser, scheduler, simulator, product builder, and verifier generator.

Risk notes:
- The shared structures are large and mutable, with many fields reused by different phases.
- Several fields encode phase-specific meaning, so invariants are distributed across many `.c` files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/spin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/spin.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/spin.y

This is the Yacc grammar for Promela plus embedded LTL syntax. It constructs `Lextok`, `Sequence`, and process definitions used by the rest of Spin.

Parser globals:
- `Mpars`: max message parameters.
- `nclaims`: number of never claims.
- `ltl_mode`: lexer/parser mode for LTL formulas.
- `Expand_Ok`, `realread`, `IArgs`, `NamesNotAdded`, `in_for`: parsing context flags.
- `claimproc` and `eventmap`: selected/current claim and trace names.
- Internal flags track embedded struct references, event-map parsing, and initialized declarations.

Top-level grammar:
- `program` is a sequence of units.
- Units include proctypes, init, never claims, LTL formulae, event traces, declarations, typedefs, C code fragments, inline definitions, semicolons, and errors.
- `proc` registers active or passive proctypes through `ready()` and may instantiate active ones through `runnable()`.
- `init` registers and starts the init process.
- `claim` increments `nclaims` and registers a never claim.
- `events` registers trace or notrace bodies.

Statement support:
- Declarations with visibility modifiers: `hidden`, `show`, `local`.
- Channel initializers update synchronous/asynchronous channel counts and message-field maximums.
- Send/receive forms include normal, sorted, random, poll, and random-poll variants.
- Control constructs include `if`, `do`, `for`, `select`, `break`, `goto`, labels, `unless`, `atomic`, `d_step`, and plain non-atomic blocks.
- Inline invocations are expanded by `pickup_inline()`.
- C fragments and C expressions are captured as pseudo-inlines.
- Assignments and increments/decrements perform tracking and reject channel arithmetic.

Expression support:
- Arithmetic, bitwise, comparison, boolean, shifts, conditional expression, `run`, `len`, `enabled`, channel probes, remote label/variable refs, `timeout`, `np_`, `pc_value`, and LTL operators.
- LTL includes `U`, release, weak-until expansion, implies, equivalence, next, always, and eventually.

Post-grammar helpers:
- `recursive()` renders a parsed LTL AST back to a textual formula.
- `ltl_to_string()` writes the formula through a temporary file and stores it as a string symbol for later translation.
- `yyerror()` delegates to `non_fatal()`.

Risk notes:
- The grammar deliberately uses many semantic actions, so parsing has side effects on symbol tables, process lists, code fragments, and analysis flags.
- LTL conversion writes `_S_p_I_n_.tmp`, then unlinks it; concurrent invocations in the same directory would collide.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/spin.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/spinlex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/spinlex.c

This file implements Spin’s lexer, inline expansion machinery, embedded C-code capture, C-state tracking support, and token name tables.

Lexer/global state:
- `lineno`, `Fname`, `yytext`, `yyin`, `yyout`.
- Scope tracking via `scope_seq`, `scope_level`, and `CurScope`.
- Inline expansion stacks with `MAXINL`, `MAXPAR`, and `MAXLEN`.
- `IType` records inline/C-code definitions with body text, formal parameters, call/definition source locations, preconditions, and unique inline ids.
- `C_Added` records `c_state` and `c_track` declarations.

Lexing:
- `lex()` skips whitespace/comments, handles preprocessor line directives, strings, `$...$` LTL strings, character constants, numbers, names, LTL operator spellings, comments, multi-character operators, and scope entry/exit.
- `check_name()` maps keywords and LTL symbols, converts mtype names to constants, recognizes `_last`, handles inline actual-parameter substitution, and returns `UNAME`, `PNAME`, `INAME`, or `NAME`.
- `yylex()` wraps `lex()` to repair common semicolon mistakes around `}` and `else`, and records inline actual parameter text while parsing inline calls.

Keyword tables:
- `Names[]` maps Promela keywords and type names to parser tokens and type values.
- `LTL_syms[]` maps textual LTL operators when `ltl_mode` is active.

Inline and C embedding:
- `prep_inline()` captures inline or C-code body text, handles optional preconditions for `c_code`, records source line directives, and stores definitions through `def_inline()`.
- `pickup_inline()` pushes an inline body on the inlining stack and validates actual/formal parameter counts.
- `getinline()` and `uninline()` feed inline body text into the lexer as if it were source input.
- `plunk_expr()`, `plunk_inline()`, `plunk_c_decls()`, and `plunk_c_fcts()` emit captured C fragments into generated verifier code.
- `no_side_effects()` does textual checks to reject obvious side effects in `c_expr`.

C state tracking:
- `c_state()` and `c_track()` record externally managed C objects.
- `c_preview()`, `c_add_sv()`, `c_add_stack()`, `c_add_def()`, `c_add_globinit()`, `c_add_locinit()`, and `c_add_loc()` generate state-vector fields and update/revert/stack helper functions for generated pan code.

Risk notes:
- Inline parameter substitution is textual and includes explicit checks for cyclic replacement and struct-field substitution hazards.
- Many buffers are fixed-size (`yytext[2048]`, inline body buffers, parameter text buffers).
- C-expression side-effect detection is heuristic and cannot catch all effects through function calls.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/spinlex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/structs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/structs.c

This file implements Promela user-defined structure type handling, proctype-name tracking for lexer disambiguation, struct field expansion, runtime struct value access, and generated-code helpers for structs.

Type registries:
- `Unames` stores typedef/user type definitions.
- `Pnames` stores known proctype names so the lexer can return `PNAME`.
- Global `owner` tracks the typedef or struct-owner context during parsing.

User type functions:
- `setuname()` registers a new typedef body under `owner`.
- `putunames()` emits C `struct` definitions for all user-defined types.
- `isutype()` and `getuname()` query typedef names.
- `setutype()` applies a user type to declared variables, setting `STRUCT`, template list, defining type name, visibility bits, formal parameter flags, and array sanity checks.

Runtime access:
- `ini_struct()` lazily initializes a struct symbol’s `Sval` array by deep-copying the typedef template and initializing nested fields.
- `do_same()` locates the requested subfield for a struct reference and performs index checking.
- `Rval_struct()` recursively reads nested struct fields and casts values.
- `Lval_struct()` recursively writes nested struct fields and updates `setat`.
- `Sym_typ()` resolves the leaf type for explicit struct field references.

Expansion and naming:
- `Cnt_flds()` counts flattened non-struct fields.
- `Width_set()` fills message field-width arrays for struct-valued message parameters.
- `mk_explicit()` expands implicit struct references into comma lists of explicit field references.
- `expand()` applies that expansion to declaration/reference lists when allowed.
- `retrieve()` reconstructs an explicit field reference for a flattened index.
- `full_name()` and `struct_name()` print or build dotted field names.

Generated-code and diagnostics:
- `walk2_struct()` visits nested structs to handle channel cases.
- `walk_struct()` and `c_struct()` emit generated variable/state-vector handling for nested fields.
- `dump_struct()` prints runtime struct contents, using `doq()` for channels and `sr_mesg()` for scalar values.
- `validref()` checks that a referenced field exists in a structure.
- `setpname()` and `isproctype()` maintain proctype name recognition.

Risk notes:
- Struct templates are copied by manually duplicating `Lextok` and `Symbol` objects in `cpnn()`.
- Error handling is mostly fatal/non-fatal parser diagnostics, not recoverable API results.
- Some generated name buffers are fixed-size and assume reasonable nesting/name lengths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/structs.c -->