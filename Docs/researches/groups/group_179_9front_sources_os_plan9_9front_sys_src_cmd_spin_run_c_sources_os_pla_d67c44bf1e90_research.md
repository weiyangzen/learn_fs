# Group Research: group_179_9front_sources_os_plan9_9front_sys_src_cmd_spin_run_c_sources_os_pla_d67c44bf1e90

Scope checked against `Docs/research_subset_a.md`: all files are within `sources/os/plan9/9front`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/run.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/run.c

`run.c` implements Spin's random-simulation execution engine for PROMELA parse tree nodes and control-flow elements. It depends on `spin.h` data structures, parser token IDs from `y.tab.h`, scheduler globals from `sched.c`, queue/message helpers, label/control-flow helpers, and printing/commenting helpers.

Key responsibilities:
- Provides deterministic pseudo-random generation through `Srand` and `Rand`, used for nondeterministic scheduling and option selection.
- Executes one `Element` or compound subtree with `eval_sub`, handling `goto`, `unless`, `if`, `do`, `atomic`, `d_step`, non-atomic blocks, escape sequences, rendezvous restrictions, interactive choice prompting, and trail replay constraints.
- Evaluates expression and statement `Lextok` nodes with `eval`, covering arithmetic, boolean operators, queue probes, sends/receives, `run`, `enabled`, priority operations, `pc_value`, `np_`, assertions, prints, C fragments, assignments, and remote references.
- Implements assignment typing through `assign`, using `Sym_typ`, `typ_ck`, `setval`, and structure tracking checks.
- Implements executable-state checks through `Enabled1` and `Enabled0`, conservatively treating side-effecting statements as enabled while probing channel operations without committing effects.
- Implements process priority introspection and mutation with `pc_highest`, `get_priority`, and `set_priority`.
- Implements `printm` and `interprint`, building formatted output in global `Buf` and routing through `dotag`.

Important interactions:
- `eval_sub` updates `LastStep`, consults `Rvous`, and delegates actual expression/statement effects to `eval`.
- `Enabled0` is used both by interactive simulation and scheduler selection to decide whether a process or option can proceed.
- Rendezvous sends call into queue logic and scheduler completion via the queue layer; `eval_sync` restricts the complementary side to synchronous receives.
- `pc_enabled` temporarily switches global `X` to another process, so callers must treat `X` as global mutable interpreter state.

Notable details:
- `TstOnly` suppresses side effects for trial execution.
- `E_Check` and `Escape_Check` prevent recursive enabled/escape probes from producing interactive prompts or visible side effects.
- Assertions call `wrapup(1)` unless running from an accepted trail mode.
- There is a duplicated `if (like_java)` line in the escape handling path; it is behaviorally redundant but worth preserving if doing mechanical source comparisons.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/run.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/sched.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/sched.c

`sched.c` owns Spin's simulation process tables, scheduling loop, process creation, never-claim startup, rendezvous completion, and runtime local-variable storage. It is central to the interpreter mode and code-generation handoff.

Key responsibilities:
- Defines global runtime state: `run`, `X`, `LastX`, `rdy`, `LastStep`, `nproc`, `nstop`, `depth`, `Tval`, `Rvous`, `Priority_Sum`, `Have_claim`, and `Skip_claim`.
- Registers proctypes/claims/traces with `ready`, and instantiates runtime processes with `runnable`.
- Starts processes from `run` expressions with `enable`, validates parameter counts, binds actuals to formals, and initializes local variables.
- Starts a selected never claim with `start_claim`, reorders it to pid 0, and adjusts process pids.
- Implements final reporting in `wrapup`, including globals, locals, process states, and MSC/postlude output.
- Implements scheduling in `sched`, including code-generation mode, product generation, trail replay, random simulation, interactive selection, timeout handling, process termination, atomic-chain preservation, and blocked-process detection.
- Completes synchronous rendezvous operations with `complete_rendez`.
- Implements local runtime symbol lookup and mutation through `findloc`, `getlocal`, `setlocal`, `in_bound`, `addsymbol`, `setlocals`, and `setparams`.
- Implements remote label and variable references with `remotelab` and `remotevar`.

Important interactions:
- `sched` repeatedly chooses a process with `pickproc`, executes through `eval_sub`, and writes the resulting element back to the process `pc`.
- `pickproc` uses priorities, `provided` guards, `Enabled0`, and optional interactive menus to choose a runnable process.
- `complete_rendez` temporarily sets `Rvous`, suppresses interactivity, and scans other processes for a matching synchronous receive.
- `remotevar` temporarily switches `X` to evaluate another process' local variable.

Notable details:
- `silent_moves` collapses labels/gotos/compound wrappers before interactive presentation and after atomic/rendezvous steps.
- Priority behavior has compatibility branching for `old_priority_rules`.
- `enabled()` is rejected for models with synchronous channels.
- The file has a few duplicated statements/returns in the local tree (`Have_claim = 1`, `if (X->pc && X->pc->n)`, a duplicated `return cast_val` line); they appear redundant rather than intentional new behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/sched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/spin.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/spin.h

`spin.h` is the shared structural and API contract for the Spin translator, simulator, and verifier generator. It defines the main AST, symbol, process, queue, flow, and FSM data structures used throughout `cmd/spin`.

Key definitions:
- Core enums: `btypes` for process/claim/trace categories, status-bit constants for `Element`, symbol hash size, channel x[rs] flags, code-fragment type IDs, and PROMELA type constants.
- `Lextok`: parse-tree node with token type, value, source location, symbol reference, sequence references, child links, inline id, and mtype marker.
- `Symbol`: unified symbol table entry with type, array/width metadata, initializers/runtime values, struct metadata, channel access metadata, scope/context/owner fields, and linked-list pointers.
- `Element`, `Sequence`, and `SeqList`: normalized control-flow representation built from parser output and consumed by interpreter/code generator.
- `RunList` and `ProcList`: runtime process instances and proctype definitions.
- `Queue`, `Label`, `Lbreak`, `Ordered`, `FSM_state`, `FSM_trans`, and `FSM_use`: queues, labels, break stacks, ordered symbol traversal, and pangen5 data-flow analysis.
- Declares a large cross-module function surface for parser helpers, symbol/type helpers, flow construction, code generation, queue operations, scheduler/runtime, diagnostics, LTL handling, and C-code support.

Important interactions:
- `YYSTYPE` is `Lextok *`, coupling this header directly to the yacc grammar.
- Many C files share mutable globals declared elsewhere rather than encapsulated module state.
- Scope support relies on `Symbol.context`, `Symbol.owner`, and `Symbol.bscp`.

Notable details:
- `TMP_FILE1` and `TMP_FILE2` are fixed temporary filenames used by LTL conversion/deferred parsing.
- Type constants double as bit-width values for integer-like PROMELA types.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/spin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/spin.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/spin.y

`spin.y` is the yacc grammar for PROMELA plus embedded LTL syntax. It builds `Lextok` AST nodes, creates proctype/claim/trace definitions, registers declarations and typedefs, expands inline/C fragments, and records semantic feature flags used by the simulator and verifier generator.

Key responsibilities:
- Defines tokens and precedence for PROMELA statements, expressions, channels, priorities, inline code, claims, traces, and LTL operators.
- Parses top-level units: proctypes, `init`, never claims, inline LTL formulas, trace/event assertions, declarations, typedefs, C fragments, and inline definitions.
- Builds proctype bodies and starts active processes via `ready`, `runnable`, and `announce`.
- Parses declarations for primitive types, mtypes, arrays, channels, and user-defined structs, calling `setptype`, `setutype`, `setmtype`, and structure expansion helpers.
- Parses statements: assignments, sends/receives, random receives, sorted sends, assertions, prints, inline calls, returns, `if/do`, `for`, `select`, `atomic`, `d_step`, non-atomic blocks, labels, gotos, breaks, `unless`, and channel probes.
- Parses expressions: arithmetic, bitwise, comparisons, boolean operators, ternary-like arrow form, `run`, `len`, `enabled`, priority access, queue poll, constants, timeout, `np_`, `pc_value`, remote label/variable references, and LTL expressions.
- Converts embedded LTL ASTs to string formulas in `ltl_to_string`, using `recursive` to print formula syntax, then passes them to the existing LTL translation pipeline.
- Provides `yyerror` wrapper and disabled `sanity_check`.

Important interactions:
- `context`, `owner`, `Expand_Ok`, `initialization_ok`, `has_*` feature flags, and `NamesNotAdded` are modified throughout grammar actions.
- Struct references are expanded with `mk_explicit` when formals or message parameters require flattening.
- Channel-use tracking is attached during send/receive/run parsing.
- Inline call argument text collection is coordinated with `spinlex.c` through `IArgs`.

Notable details:
- `ltl_to_string` writes to `TMP_FILE1`, reads back the formula, unlinks the file, and stores the formula as a symbol name.
- A duplicate `expr IMPLIES expr` production is present in the file. It appears to be a duplicated grammar line in the imported source.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/spin.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/spinlex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/spinlex.c

`spinlex.c` is the lexer, inline expander, C-fragment collector, deferred LTL handler, and generated-C support module for Spin's front end. It feeds `spin.y` through `yylex`.

Key responsibilities:
- Tokenizes PROMELA source, including identifiers, strings, `$...$` LTL strings, character constants, numbers, comments, operators, optional semicolon insertion, preprocessor line directives, and scope tracking.
- Maps keywords and built-ins to yacc tokens through `Names`, and maps LTL words/operators through `LTL_syms`.
- Maintains source location globals `lineno`, `Fname`, `CurScope`, `scope_seq`, and `scope_level`.
- Implements inline definition capture with `prep_inline`, registration with `def_inline`, lookup with `find_inline`, expansion with `pickup_inline`, and nested inline stream reading through `getinline`/`uninline`.
- Preserves literal argument text for inline calls in `IArg_cont`, enabling textual substitution during expansion.
- Supports return-from-inline by translating `return expr` into assignment to the captured return target.
- Handles C fragments and declarations, including `c_code`, `c_decl`, `c_expr`, `c_state`, and `c_track`.
- Generates supporting verifier C code for embedded C state tracking: `gencodetable`, `c_add_sv`, `c_add_stack`, `c_add_def`, `c_add_globinit`, `c_add_locinit`, `plunk_c_decls`, `plunk_c_fcts`, and `plunk_expr`.
- Performs side-effect checks for `c_expr` used in logical contexts.
- Defers `ltl { ... }` formulas to a temporary file so they are parsed after the rest of the spec.
- Expands `select` statements into equivalent `if`/`do` source pushed back into the lexer stream.

Important interactions:
- `check_name` consults symbol/type/proctype/inline registries and performs inline formal-parameter substitution.
- `yylex` repairs common semicolon mistakes and keeps `owner` from leaking across statement boundaries.
- C-code support feeds later pangen modules by emitting state-vector declarations, hidden declarations, update/revert functions, and code lookup tables.

Notable details:
- Uses fixed-size buffers for inline text, parameter text, pushed-back select expansions, and generated C snippets.
- Deferred LTL uses `TMP_FILE2`.
- Scope names are encoded as underscore-prefixed numeric scope paths, later used by symbol lookup and disambiguation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/spinlex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/structs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/structs.c

`structs.c` implements PROMELA user-defined type and struct handling. It manages typedef registration, struct field expansion, runtime struct values, nested field lookup, code-generation traversal, and proctype-name registration.

Key responsibilities:
- Registers typedefs with `setuname`, lists them as C structs with `putunames`, and resolves names with `isutype`/`getuname`.
- Applies user-defined struct types to declared variables in `setutype`, preserving visibility flags and formal-parameter metadata.
- Initializes nested runtime struct values with `ini_struct`, copying template nodes with `cpnn` and assigning fresh channel IDs to copied channel fields.
- Resolves nested field references through `do_same`.
- Reads and writes nested struct fields with `Rval_struct` and `Lval_struct`.
- Counts flattened field slots with `Cnt_flds`, returns terminal field type with `Sym_typ`, and fills type-width arrays with `Width_set`.
- Builds printable/generated names for nested fields through `full_name` and `struct_name`.
- Validates field references with `validref`.
- Traverses struct fields for channel cases, generic variable generation, C code generation, and runtime dumping with `walk2_struct`, `walk_struct`, `c_struct`, and `dump_struct`.
- Expands implicit structure references into comma-linked explicit field references with `expand`, `mk_explicit`, and `retrieve`.
- Maintains known proctype names through `setpname`/`isproctype`.

Important interactions:
- Parser actions call `setutype`, `expand`, and `mk_explicit` for declarations, message parameters, receive arguments, and formal parameters.
- Runtime value access from `sched.c`/`vars.c` delegates to `Rval_struct` and `Lval_struct`.
- Code-generation modules call traversal functions to emit state-vector and C representations.

Notable details:
- Struct arrays are supported, but arrays of structures in parameter lists are explicitly rejected.
- `owner` is global parser state used to distinguish struct-field symbols during declaration and lookup.
- There is a duplicated `if (m->ntyp == ',')` and duplicated loop header in `retrieve`; both appear redundant.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/structs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/sym.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/sym.c

`sym.c` implements Spin's main symbol table, scoped name lookup, type tagging, mtype handling, channel-use tracking, and diagnostics for unused variables/channel access.

Key responsibilities:
- Defines global parser symbol state: `context`, ordered symbol list `all_names`, channel ID counter `Nid`, mtype list `Mtype`, and collected `run` statements.
- Provides `hash` and `lookup`, including legacy and newer scope-rule handling through `context`, `owner`, `CurScope`, and `bscp`.
- Applies scope-prefix disambiguation with `disambiguate`.
- Tracks variable-width hints through `trackvar` and `checkrun`.
- Tracks `run` statements and channel parameters through `trackrun`, `trackchanuse`, and `setaccess` calls.
- Assigns primitive types and declaration metadata with `setptype`, including unsigned width checks, visibility flags, channel IDs, and formal-parameter markers.
- Applies `xr`/`xs` channel assertions through `setxus`, `setallxu`, and `setonexu`.
- Registers and resolves mtype values with `setmtype` and `ismtype`.
- Converts type IDs to text with `sputtype`, prints symbols with `symvar`, and dumps all symbols with `symdump`.
- Reports channel access patterns and unused variables with `chanaccess`.

Important interactions:
- `lookup` is called by both lexing and parsing for every identifier-like token.
- `setptype`, `setmtype`, and `setxus` are grammar action targets from `spin.y`.
- `symdump` is used when `dumptab` is requested in `sched`.
- Channel access reports use `Access` lists attached to `Symbol`.

Notable details:
- `hidden` is a bitfield carrying visibility, inferred width, use, formal parameter, and mtype flags.
- Newer scoping accepts a lookup if a stored block scope is a prefix of the current scope, which approximates nested lexical visibility.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/sym.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/tl.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/tl.h

`tl.h` is the shared header for Spin's LTL-to-never-claim translator. It defines the LTL symbol table, formula AST, graph-state representation, token IDs, and function contracts for parsing, rewriting, caching, graph expansion, and Büchi printing.

Key definitions:
- `Symbol`: LTL symbol-table entry with name and hash-chain link.
- `Node`: LTL formula tree/list node with token type, symbol, left/right children, and list link.
- `Graph`: tableau graph node with name sets, formula sets (`New`, `Old`, `Other`, `Next`), red/green acceptance-color arrays, reachability, and next link.
- `Mapping`: maps symbolic names to graph nodes during translation.
- Token enum for LTL operators and leaves: `ALWAYS`, `AND`, `EQUIV`, `EVENTUALLY`, `FALSE`, `IMPLIES`, `NOT`, `OR`, `PREDICATE`, `TRUE`, `U_OPER`, `V_OPER`, optional `NEXT`, and `CEXPR`.
- Convenience macros: `True`, `False`, `Not`, `rewrite`, debug macros, and `Assert`.

Important interactions:
- `tl_parse.c`, `tl_lex.c`, `tl_cache.c`, `tl_rewrt.c`, `tl_trans.c`, `tl_buchi.c`, `tl_main.c`, and `tl_mem.c` all share this contract.
- It imports `emalloc` and `hash` from the broader Spin codebase, tying the TL translator to the main Spin runtime.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/tl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/tl_buchi.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/tl_buchi.c

`tl_buchi.c` converts the intermediate LTL translation graph into a minimized PROMELA `never` claim. It owns the printable Büchi-state/transition representation and post-translation cleanup.

Key responsibilities:
- Defines `State` and `Transition` lists separate from the tableau `Graph`.
- Initializes module state with `ini_buchi`.
- Adds graph transitions with `addtrans`, pruning and rewriting transition conditions before storing them.
- Prunes non-condition formula nodes with `Prune`.
- Retargets transitions and marks redundant states with `retarget`.
- Computes reachability with `Dfs` and tracks whether `accept_all` is reached.
- Optionally removes contradictory simple conditions with `unclutter`/`clutter`.
- Merges transitions to the same target by OR-combining conditions with `mergetrans`.
- Merges equivalent states through `all_trans_match` and `mergestates`.
- Applies the optional `BUCKY` optimization for special paired-state reductions.
- Prints states and transitions in never-claim syntax through `rev_trans`, `printstate`, and `fsm_print`.

Important interactions:
- Receives transitions from `tl_trans.c` via `addtrans`.
- Uses formula equality/rewrite helpers from `tl_cache.c` and `tl_rewrt.c`.
- Uses `dump_cond` from `tl_trans.c` to print PROMELA conditions.
- `fsm_print` emits to global `tl_out`.

Notable details:
- `accept_all` transitions are printed as atomic assertions designed to flag counterexample acceptance.
- `Max_Red == 0` affects generation of `T0` labels for accepting states.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/tl_buchi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/tl_cache.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/tl_cache.c

`tl_cache.c` implements formula-node allocation helpers, deep copy/release operations, formula equality checks, and a canonicalization cache for the LTL translator.

Key responsibilities:
- Initializes cache counters and list with `ini_cache`.
- Looks up prior canonicalization results with `in_cache` and stores new ones with `cached`.
- Reports cache stats with `cache_stats`.
- Allocates, shallow-copies, deep-copies, and releases `Node` trees with `tl_nn`, `getnode`, `dupnode`, and `releasenode`.
- Implements structural and associative/commutative equality through `sameform`, `sametrees`, `all_lfts`, `one_lft`, and `isequal`.
- Implements exact-shape match with `ismatch`.
- Searches formula trees for matching terms under `AND`/`OR` with `any_term`, `any_and`, `any_lor`, and `anywhere`.

Important interactions:
- `tl_rewrt.c` calls `cached`, `in_cache`, `isequal`, and `anywhere` during formula rewrite/canonicalization.
- `tl_buchi.c` uses `isequal` to detect identical transition conditions.
- Node memory comes from `tl_mem.c` and is returned through `tfree`.

Notable details:
- `isequal(NULL, TRUE)` treats missing conditions as true in some contexts.
- Canonicalization cache stores both the original and canonical tree, marking `same` when canonicalization did not change structure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/tl_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/tl_lex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/tl_lex.c

`tl_lex.c` is the lexer and symbol table for standalone LTL formulas passed to the TL translator.

Key responsibilities:
- Tokenizes formula text from `tl_Getchar`, skipping spaces and returning `;` on end of input.
- Recognizes lowercase words for `true`, `false`, `always`, `eventually`, `until`, optional `next`, `c_expr`, `not`, or predicate names.
- Recognizes symbolic operators: `/\`, `\/`, `&&`, `||`, `[]`, `<>`, `<->`, `->`, `!`, `U`, `V`, and optional `X`.
- Treats parenthesized or braced non-temporal content as a single `PREDICATE`, using lookahead in `is_predicate` and extraction in `read_upto_closing`.
- Maintains a TL-specific symbol table through `tl_lookup`; clones symbols with `getsym`.

Important interactions:
- `tl_parse.c` consumes `tl_yylex`.
- Predicate recognition deliberately avoids swallowing nested temporal syntax.
- Uses main Spin `yytext` buffer and `isalnum_` helper from `spinlex.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/tl_lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/tl_main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/tl_main.c

`tl_main.c` is the entry point and diagnostic shell for the LTL-to-Büchi translator embedded in Spin.

Key responsibilities:
- Defines TL global flags and counters: `newstates`, `tl_errs`, `tl_verbose`, `tl_terse`, `tl_clutter`, `state_cnt`, `All_Mem`, and `claim_name`.
- Stores the input formula in `uform` and provides character stream helpers `tl_Getchar`, `tl_peek`, and `tl_UnGetchar`.
- Checks parenthesis balance with `tl_balanced`, ignoring character/string literal parentheses.
- Initializes all TL subsystems in `tl_main`: Büchi state, cache, rewrite, and transition graph modules.
- Parses command-like arguments: `-f formula`, `-v`, `-n`, `-c claim_name`, and `-d`.
- Calls `tl_parse` to translate the formula.
- Prints formulas and nodes with `put_uform`, `dump`, and `tl_explain`.
- Emits fatal/syntax diagnostics with source-position caret display through `Fatal`, `tl_yyerror`, and `tl_non_fatal`.

Important interactions:
- `tl_out` is shared with `tl_buchi.c` for generated never-claim output.
- `tl_clutter` is selected based on xspin/trail mode to keep replay-generation compatible with verifier output.
- Memory/cache stats are printed only in verbose mode.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/tl_main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/tl_mem.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/tl_mem.c

`tl_mem.c` provides a small pooled allocator for the TL translator.

Key responsibilities:
- Allocates zeroed memory through `tl_emalloc`.
- Buckets small allocations by `union M` units in freelists, with gradually growing pool requests capped by `NOTOOBIG`.
- Allocates large blocks directly through the main `emalloc`.
- Tracks total allocated memory in `All_Mem`.
- Returns blocks to the freelist with `tfree`, validating an `A_USER` tag to catch double-free/free-corruption.
- Reports allocation statistics with `a_stats`.

Important interactions:
- Used by all TL node, graph, state, transition, and symbol allocations.
- Large allocations are intentionally not returned to the system; the free path logs them and leaves the actual `free(m)` commented out.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/tl_mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/tl_parse.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/tl_parse.c

`tl_parse.c` is the recursive-descent parser and algebraic simplifier for TL formulas.

Key responsibilities:
- Parses factors: parentheses, negation, `[]`, `<>`, optional `X`, `c_expr`, predicates, true, and false.
- Parses binary operators by precedence with `tl_level`: temporal `U`/`V`, then boolean `OR`/`AND`/`IMPLIES`/`EQUIV`.
- Performs early simplifications in `tl_factor` and `bin_simpler`, including idempotence, constants, nested eventually/always, implication elimination, equivalence expansion, and several LTL absorption/distribution identities.
- Pushes negations down with `push_negation`.
- Calls `rewrite` to canonicalize simplified subtrees.
- Entrypoint `tl_parse` parses a formula, validates trailing input, and calls `trans`.

Important interactions:
- Consumes tokens from `tl_lex.c`.
- Builds nodes with `tl_nn`, compares with `isequal`, and invokes rewrite/cache logic.
- Hands the final formula tree to `tl_trans.c`.

Notable details:
- Optimization blocks are guarded by `NO_OPT`.
- Optional `NXT` support adds `NEXT` simplifications when compiled in.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/tl_parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/tl_rewrt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/tl_rewrt.c

`tl_rewrt.c` canonicalizes TL formula trees and normalizes negation.

Key responsibilities:
- Resets canonicalization state with `ini_rewrt`.
- Converts left-nested `AND`/`OR` trees into right-linked chains with `right_linked`.
- Recursively canonicalizes subtrees and stores/reuses canonical forms through cache with `canonical`.
- Pushes negation inward with `push_negation`, applying De Morgan rules, duality between `U` and `V`, double-negation elimination, and constant negation.
- Builds sorted canonical operand chains with `addcan`, using `DoDump` string forms for ordering and duplicate detection.
- Marks and removes redundant operands in `Canonical`.
- Simplifies boolean chains: removes `true` from conjunction, removes `false` from disjunction, collapses conjunctions containing `false`, disjunctions containing `true`, duplicate terms, and absorption cases.

Important interactions:
- `rewrite(n)` in `tl.h` composes `right_linked` and `canonical`.
- `tl_parse.c`, `tl_trans.c`, and `tl_buchi.c` rely on this normalization before equality/comparison.
- Uses `anywhere` and `isequal` from `tl_cache.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/tl_rewrt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/tl_trans.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/tl_trans.c

`tl_trans.c` implements the tableau-style translation from normalized LTL formula trees to an intermediate graph, then drives Büchi automaton generation.

Key responsibilities:
- Initializes graph translation state with `ini_trans`.
- Maintains graph-node sets, DFS stack, mapping table, red/green acceptance color counters, and generated state names.
- Builds acceptance/liveness obligations with `liveness`, `mk_grn`, and `mk_red`.
- Prints graph diagnostics with `dump_graph`, `sdump`, and `DoDump`.
- Emits PROMELA transition conditions with `dump_cond`, respecting `V_OPER`, `AND`, predicates, C expressions, optional `NEXT`, and condition elision.
- Computes Choueka-style red acceptance cycling with `choueka` and state-name prefixes with `set_prefix`.
- Converts graph nodes to FSM transitions with `fsm_trans` and finalizes via `mkbuchi`.
- Manages incoming/outgoing symbol sets with `dupSlist`, `catSlist`, and `Addout`.
- Normalizes graph formula sets with `flatten`, `Duplicate`, and `not_new`.
- Expands tableau graph nodes in `expand_g`, processing `AND`, `OR`, `U`, `V`, optional `NEXT`, predicates, and constants.
- Applies special two-case simplifications in `twocases`.
- Main `trans` rewrites/fixes the initial formula, expands the graph, computes liveness colors, builds the Büchi form, and prints it.

Important interactions:
- Receives formula tree from `tl_parse.c`.
- Calls `addtrans`/`fsm_print` in `tl_buchi.c`.
- Uses canonicalization/equality helpers from `tl_cache.c` and `tl_rewrt.c`.
- Uses `tl_out` for generated condition text.

Notable details:
- `Max_Red`, `Red_cnt`, and green/red color arrays implement acceptance-set tracking.
- `dump_cond` returns whether it printed no concrete condition, allowing callers to emit `1`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/tl_trans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/vars.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/vars.c

`vars.c` implements runtime access, initialization, assignment, casting, and reporting for PROMELA variables during simulation.

Key responsibilities:
- Provides `getval` and `setval`, dispatching to local or global storage depending on `Symbol.context`.
- Rejects assignments to reserved predefined variables such as `_p`, `_pid`, `_nr_qs`, and `_nr_pr`, with compatibility behavior for old priority rules.
- Removes self-referential initializers with `rm_selfrefs`.
- Initializes variable storage lazily in `checkvar`, allocating arrays and evaluating initializers.
- Reads and writes global variables with `getglobal` and `setglobal`, delegating struct fields to `Rval_struct`/`Lval_struct`.
- Casts values according to PROMELA type widths in `cast_val`, including bit, byte, short, and unsigned-width masking.
- Dumps claim state with `dumpclaims`.
- Dumps visible/tracked globals with `dumpglobals`, including queues, structs, MSC output, and column-output mode.
- Dumps local variables for a process with `dumplocal`, including queues, structs, tracked locals, and MSC output.

Important interactions:
- `run.c` uses `getval`, `setval`, and `cast_val` through expression evaluation.
- `sched.c` calls `checkvar`, `getlocal`, and `setlocal`.
- Structure access is delegated to `structs.c`; queues are delegated to message/queue helpers.
- Visibility and tracking are controlled by symbol `hidden` flags and global verbosity flags.

Notable details:
- `setat` depth is used to suppress or include recently changed variables in trace-style output.
- `limited_vis` and `no_arrays` affect dump filtering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/vars.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/version.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/version.h

`version.h` defines the Spin version string used by the tool.

Content:
- `#define SpinVersion "Spin Version 6.4.7 -- 19 August 2017"`

Important interactions:
- Included by Spin front-end code that reports version information.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/version.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/split.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/split.c

`split.c` is the Plan 9 `split` command implementation. It splits input into output files either by fixed line count or by regular-expression matches.

Key responsibilities:
- Parses options: `-n`/`-l` line count, `-e` regex, `-f` output stem, `-s` suffix, `-x` skip matched separator lines, and `-i` case-insensitive matching.
- Reads from a named file or stdin using `Biobuf`.
- In line-count mode, opens a new output every `n` lines and copies trailing non-newline bytes to the last file.
- In regex mode, compiles the expression, starts output with `matchfile`, and creates a new output whenever the regex matches.
- Uses capture group 1 as the output file name when present, appending `suffix`; otherwise uses incrementing suffixes.
- Generates output names from `stem` plus two-letter suffix `aa` through `zz` in `nextfile`.
- Handles output creation and buffer switching in `openf`.
- Implements case folding for ASCII letters in `fold`.

Important interactions:
- Uses Plan 9 `regexp.h` `Reprog` and `Resub`.
- Uses Plan 9 `ARGBEGIN`, `Bopen`, `Binit`, `Brdline`, `Bwrite`, `Bterm`, `create`, and `%r` error formatting.

Notable details:
- Output suffix space is capped at `zz`; further files are not created and a warning is printed once.
- `openf` error text says `grep: can't create`, likely inherited typo.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/split.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spred/cmd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spred/cmd.c

`spred/cmd.c` implements textual commands for the `spred` sprite editor command window.

Key responsibilities:
- `dopal`: opens or creates a palette file/window.
- `dosize`: resizes the active palette or sprite, parsing `N` for palettes and `W*H` for sprites.
- `doset`: sets the selected palette color from a numeric RGB value.
- `dozoom`: changes active window zoom and redraws.
- `dospr`: opens or creates a sprite, reads its file if present, creates a sprite window, and loads referenced palette.
- `dowrite`: writes the active palette/sprite, optionally to a specified file.
- `doquit`: calls `quit` and exits all threads when no unsaved-change confirmation remains.
- `docmd`: tokenizes a command line, dispatches through the `cmds` table, checks arity, and prints `?` on errors.

Important interactions:
- Uses global `mc`, active file/window globals from `dat.h`, and file/window helpers from `fns.h`.
- Palette and sprite file formats are implemented in `pal.c` and `spr.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spred/cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spred/cmdw.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spred/cmdw.c

`spred/cmdw.c` implements the editable command/output window for `spred`.

Key responsibilities:
- Defines `cmdtab`, the `Wintab` implementation for command windows.
- Draws the command window frame and scrollbar with `cmddraw` and `scrollbar`.
- Scrolls by lines with `cmdscroll`.
- Handles mouse selection and right-button scrollbar behavior with `cmdclick` and `cmdrmb`.
- Inserts and deletes rune ranges with `cmdinsert` and `cmddel`.
- Maintains frame selection with `setsel`.
- Executes the current command line from `opoint` through `cmdline` and `docmd`.
- Handles keyboard input in `cmdkey`, including view/up/left/right, deletion, newline command execution, and text insertion.
- Implements cut/snarf/paste using `/dev/snarf` with `tosnarf`, `fromsnarf`, and `cmdmenu`.
- Appends formatted command output with `cmdprint`.

Important interactions:
- Uses Plan 9 `Frame` APIs for text display/editing.
- `cmdprint` writes into global `cmdw`.
- The command menu uses middle mouse button, while right-button handling is partly delegated to the generic app menu.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spred/cmdw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spred/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spred/dat.h

`spred/dat.h` defines shared data structures, constants, and globals for the `spred` sprite editor.

Key definitions:
- UI constants: border size, minimum window size, selection border size, scrollbar sizes, and rune allocation block size.
- Color-index extension: `DISB` and `NCOLS`.
- Window/file types: `CMD`, `PAL`, `SPR`, `NTYPES`.
- `Wintab`: per-window behavior table with init/die/click/menu/rmb/key/draw/zerox hooks and color slots.
- `Win`: window geometry, image, global/file window links, type, frame state, command-window rune buffer, zoom/scroll data, attached file, and sprite rectangle cache.
- `Ident`: device identity tuple from file metadata.
- `File`: common base struct with type, refcount, file-list links, name, dirty flag, identity, and per-file window list sentinel.
- `Pal`: palette file with colors, 1x1 color images, and selected index.
- `Spr`: sprite file with palette pointer, dimensions, pixel-index data, and palette filename.

Important globals:
- `wlist`, `flist`, `actw`, `actf`, `cmdw`, `scr`, `invcol`, and `quitok`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spred/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spred/fil.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spred/fil.c

`spred/fil.c` implements shared file-list, identity, title, dirty-state, and write helpers for palettes and sprites.

Key responsibilities:
- `tline`: reads logical file-format lines, strips comments outside quoted regions, tokenizes fields, and skips blank/comment-only lines.
- `getident`: captures file identity from `dirfstat`; `putident` is a no-op placeholder.
- `identcmp`: compares file identities by type, dev, and qid path.
- `filcmp`: orders files by type then name.
- `filinit`: initializes a `File`, assigns its name, creates empty window-list sentinel links, and inserts into sorted global `flist`.
- `putfil`: dispatches type-specific cleanup, removes from file list, and frees common storage.
- `filtitlelen`/`filtitle`: produce menu titles showing dirty flag, window count marker, active-file marker, and filename.
- `winwrite`: dispatches active window write to palette or sprite writer.
- `filredraw`: redraws all windows attached to a file.
- `change`: marks a file dirty and clears `quitok`.

Important interactions:
- Used by `pal.c`, `spr.c`, `spred.c`, and window-management code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spred/fil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spred/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spred/fns.h

`spred/fns.h` declares the cross-file function interface for the `spred` sprite editor.

Covered modules:
- File/common helpers: `change`, `filinit`, `filredraw`, `filtitle`, `filtitlelen`, `putfil`, `winwrite`, identity helpers, and `tline`.
- Command helpers: `cmdprint`, `docmd`.
- Window helpers: `emalloc`, `initwin`, `newwin`, `newwinsel`, `resize`, `setfocus`, mouse/window actions, and selection helpers.
- Palette helpers: `newpal`, `findpal`, `readpal`, `writepal`, `putpal`, `paldraw`, `palset`, `palsize`.
- Sprite helpers: `newspr`, `readspr`, `writespr`, `putspr`, `sprsize`.
- Application quit helper: `quit`.

Important interactions:
- This header is the glue between the listed files and adjacent `win.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spred/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spred/pal.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spred/pal.c

`spred/pal.c` implements palette file objects, palette file I/O, palette lookup/reuse, palette drawing, selection, resizing, and color mutation.

Key responsibilities:
- Creates and destroys palettes with `newpal` and `putpal`.
- Reads palette format with `readpal`: first line `pal N`, followed by `N` RGB values, each converted to a 1x1 `Image`.
- Writes palette format with `writepal`, clears dirty state, and reports byte count.
- Finds or loads palettes with `findpal`, using file identity to reuse already-open files.
- Redraws a palette and any sprites using it through `palredraw`.
- Resizes palettes with `palsize`, allocating new color/image entries as needed.
- Draws swatch grids in `paldraw`, including selected-cell border.
- Updates selected color with `palset`, refreshing its backing image and marking dirty.
- Defines palette window behavior through `paltab`, including default zoom, click selection, and zerox state copy.

Important interactions:
- Sprites hold `Pal *` references and use palette images while drawing.
- `findpal` is called by sprite opening and commands to associate sprite palette files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spred/pal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spred/spr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spred/spr.c

`spred/spr.c` implements sprite file objects, sprite file I/O, drawing, painting, scrolling, resizing, palette attachment, and key shortcuts.

Key responsibilities:
- Creates and destroys sprites with `newspr` and `putspr`, including palette reference cleanup.
- Reads sprite format with `readspr`: `sprite W H palettefile`, followed by `H` rows of `W` palette indices.
- Writes sprite format with `writespr`, clears dirty state, resets quit confirmation, and reports byte count.
- Initializes default sprite zoom with `sprinit`.
- Computes the drawn sprite rectangle centered in the window via `sprrect`.
- Draws scrollbars when the zoomed sprite exceeds the viewport with `scrollbars`.
- Draws sprites with `sprdraw`, using palette images for valid indices and `invcol` for invalid/missing palette values.
- Handles scrollbar clicks with `sprbars`.
- Paints with selected palette color while mouse button 1 is held in `sprclick`.
- Resizes sprite data with `sprsize`, preserving overlapping pixels.
- Attaches a palette from another selected palette window via `sprmenu`.
- Copies zoom/scroll state for zerox windows with `sprzerox`.
- Selects palette colors from keyboard shortcuts with `sprkey`.
- Defines sprite window behavior in `sprtab`.

Important interactions:
- Depends on palette refcounts and `filredraw` to update linked palette/sprite views.
- Uses `palfile` currently as a simple duplicate of palette name; no path relativization is implemented.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spred/spr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spred/spred.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spred/spred.c

`spred.c` is the main entry point and event loop for the Plan 9 sprite editor.

Key responsibilities:
- Defines global input controllers `mc` and `kc`, plus `quitok`.
- Implements dirty-file quit confirmation in `quit`: first quit with dirty files prints `?` and sets `quitok`; next quit exits.
- Generates right-button menu labels with `menugen`, including actions and open-file entries decorated by `filtitle`.
- Handles the global right-button menu in `rmb`: zerox, close, resize, write, quit, focusing command window, opening file windows, or cycling focus among existing windows.
- Runs the main event loop in `loop`, multiplexing mouse, keyboard, and resize events with `alt`.
- Dispatches left-clicks to window focus/click handling, middle-clicks to active window menu, right-clicks to `rmb`, keyboard runes to active window key handlers, and resize events to `resize`.
- Initializes draw, window system, mouse, keyboard, quote formatting, and enters the loop in `threadmain`.
- Defines `crosscursor`, likely used by window selection/resize logic in adjacent `win.c`.

Important interactions:
- Relies on `initwin`, `winclick`, `resize`, `winzerox`, `winclose`, `winresize`, `newwinsel`, `setfocus`, and active window globals from the window subsystem.
- Command, palette, and sprite behavior is delegated through each window's `Wintab`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spred/spred.c -->