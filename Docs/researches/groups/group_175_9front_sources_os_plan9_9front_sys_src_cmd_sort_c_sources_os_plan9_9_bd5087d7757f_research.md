# Group Research: group_175_9front_sources_os_plan9_9front_sys_src_cmd_sort_c_sources_os_plan9_9_bd5087d7757f

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sort.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sort.c

`sort.c` implements the Plan 9/9front `sort` command. It parses classic and POSIX-style sort options, reads input lines through `Biobuf`, constructs byte-comparable sort keys, sorts in memory when possible, spills sorted runs to temporary files when needed, and k-way merges those temporary files to the final output.

Core flow starts in `main()`: `doargs()` builds global/per-field sort specifications, input files are processed by `dofile()`, and output is handled by either `printout()` or `tempout()` plus `mergeout()`. `newline()` preserves newline-terminated records, adding a newline to unterminated final records, and immediately calls `buildkey()` so sorting compares precomputed keys rather than source lines.

Field/key handling is the main logic. `skip()` locates field and character offsets, honoring whitespace fields or a user-specified tab rune. `dokey_()`, `dokey_r()`, `dokey_dfi()`, `dokey_m()`, and `dokey_gn()` encode plain, reverse, directory/fold/ignore, month, and numeric/floating-point comparisons. Numeric encoding normalizes sign, decimal point, exponent, significant digits, and reverse ordering into a lexicographic key. `makemapd()` and `makemapm()` build byte maps for case folding, directory order, ASCII filtering, whitespace ignoring, reverse sorting, month parsing, and selected Latin rune folding.

Sorting uses `sort4()`, which chooses radix sort (`rsort4()`) above a small threshold and insertion/bubble cleanup (`bsort4()`) below it. Keys are sorted through pointer indirection, and `Merge` deliberately begins with a `Key *` so merge entries can be sorted with the same sorter shape as line pointers. `-u` suppresses duplicate keys during final output or merge, and `-c` checks sorted input order without producing output.

Important risks and constraints: temporary file names are predictable `sort.<pid>.<n>` names under `/tmp` or `-T`; the comment notes `00/ff` key terminators can conflict with source bytes; `kcmp()` compares only the shorter key length and relies on embedded terminator conventions; memory limits are fixed through `-l` line count and dynamic line/key allocation; and `doargs()` mutates `argv` to hide processed options.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sort.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spell/code.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spell/code.h

`code.h` defines the affix/class bitmask vocabulary shared by the spelling dictionary encoder (`pcode.c`) and spelling recognizer (`sprog.c`). The constants describe which derivational or inflectional transformations are valid for a base dictionary word.

The bits cover suffix classes such as `ED`, `ADJ`, `NOUN`, `ACTOR`, `ION`, `N_AFFIX`, `V_AFFIX`, `V_IRREG`, `MAN`, `ADV`, and `_Y`; special handling flags such as `DONT_TOUCH`, `STOP`, `NOPREF`, `MONO`, and `IN`; and convenience combinations such as `COMP`, `VERB`, and `ALL`.

This header is pure data contract. Changes here must stay synchronized with `pcode.c` string-to-bit encoding, `sprog.c` suffix/prefix logic, and any existing encoded dictionary files, because the binary dictionary stores these bit meanings by value.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spell/code.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spell/pcode.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spell/pcode.c

`pcode.c` converts annotated spelling word lists into the compact binary dictionary format consumed by `sprog.c`. Input lines are `word<TAB>affixcode[,affixcode...]`; output is a big-endian encoded affix table followed by sorted, prefix-compressed dictionary entries.

`main()` reads one or more input files, stores words in fixed global arrays, sorts `Dict` records by word with `qsort()`, then calls `pdict()`. `readinput()` copies each word into the global `space` buffer and converts the comma-separated code string with `typecode()`.

`typecode()` maps textual affix names (`n`, `ed`, `comp`, `nopref`, `ion`, `va`, `ms`, etc.) to the `code.h` bitmasks through small alphabet-indexed tables. Unique bit combinations are interned in `encodes[]`; dictionary entries store an index into that table rather than the full bitmask.

`pdict()` writes `ncodes`, all encoded bitmasks, and then each sorted word as a two-byte header plus suffix bytes. The header uses bit 15 as an entry marker, bits 14..11 as the number of prefix bytes shared with the previous word, and bits 10..0 as the affix-code index. All multi-byte integers are written big-endian by `sput()` and `lput()`.

Important constraints: `words`, `space`, and `encodes` are fixed-size globals with hard exits on overflow; duplicate words are reported but still encoded; unknown affix codes return code index zero after printing an error; and the binary format must remain consistent with `sprog.c`'s `readdict()` decoder.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spell/pcode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spell/sprog.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spell/sprog.c

`sprog.c` is the runtime spelling checker and affix analyzer. It reads the compact dictionary produced by `pcode.c`, then checks words from standard input by direct dictionary lookup plus recursive prefix and suffix stripping rules.

The file is table-driven. Large `Suftab` tables encode reversed suffix patterns, transformation routines, messages, required affix flags, and allowed follow-on classes. `Ptab` tables define allowed prefixes. The transformation functions (`strip`, `cstrip`, `s`, `es`, `an`, `ize`, `y_to_e`, `i_to_y`, `ily`, `bility`, `subst`, `tion`, `CCe`, `VCe`) mutate candidate word endings, check phonetic/vowel constraints, and recursively call `trypref()` or `trysuff()`.

`main()` parses spell options, loads `/sys/lib/amspell` or `/sys/lib/brspell`, then processes each input line. It handles optional acme-style `file:addr:word` prefixes, preserves or lowers case depending on the original word, skips numeric ordinals, and prints either misspellings, correction markers, or verbose derivation traces. `-b` Britishises `z` suffix rules through `ise()`/`ztos()`, `-c`/`-C` produce compact correctness codes, `-v` records derivations, `-x` traces dictionary lookups, and `-f` selects the dictionary file.

Dictionary lookup is optimized around the binary format. `readdict()` reads the big-endian affix table, expands prefix-compressed dictionary bytes into `space`, and builds `spacep[]`, an index by the first two 7-bit characters. `dict()` uses that two-character bucket and a binary search over compressed entries; found entries return the decoded affix bitmask.

Important behavior: prefix stripping refuses `NOPREF` words and validates `in-`/`im-`/`ir-`/`un-` semantics through `inun()`. Derivation recording uses fixed `deriv[]` and `affix[]` buffers. The dictionary buffer sizes are fixed and must match the encoder’s expected limits. Many routines temporarily mutate `word[]`, so recursive paths rely on careful restoration of changed characters.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spell/sprog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/dstep.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/dstep.c

`dstep.c` generates verifier C code for Promela `d_step` sequences in Spin. It turns deterministic step blocks into straight-line/generated-label code, while preserving executability checks, state reachability marking, and correct exits back to surrounding control flow.

`putcode()` is the external entry point. It emits guard checks for the first statement or selection, marks reached states, handles `TstOnly` enabledness calls, saves state with `sv_save()`, then delegates to `putCode()` for the sequence body. `CollectGuards()` recursively emits disjunctions for `if`/`do` options, sends, receives, conditions, and `else`.

The file tracks generated label sources and destinations with `Tojump[]`, `Jumpto[]`, and `Special[]`. `Sourced()`, `Dested()`, `FirstTime()`, and `Mopup()` prevent duplicate labels, report gotos that leave a `d_step`, preserve global exit labels, and emit a break destination label when required.

`filterbad()` rejects constructs that cannot safely live inside `d_step`: process termination, nested `d_step`/`atomic`, `run` operators, and remote references. `putCode()` handles nested non-atomic fragments, break/goto translation, guard options, generated `Uerror()` calls for blocking selections, and transitions to the next element.

Important coupling: depends on Spin’s `Element`, `Sequence`, `SeqList`, code-emission functions such as `putstmnt()`, label resolution through `get_lab()`/`huntele()`, process IDs, claim detection, and global verifier output files. Capacity is capped by `MAXDSTEP`; oversized or confusing control structures abort generation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/dstep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/flow.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/flow.c

`flow.c` builds and normalizes Spin’s internal control-flow graph from parsed Promela syntax. It creates `Sequence` and `Element` objects, wires `if`, `do`, `unless`, blocks, labels, breaks, gotos, atomic regions, `d_step` regions, `for`, and `select` constructs.

Sequence construction uses `open_seq()`, `add_seq()`, `add_el()`, and `close_seq()`. `new_el()` assigns per-process and global sequence numbers, while `if_seq()` and `unless_seq()` expand compound constructs into graph nodes with sub-sequences and synthetic target elements. `loose_ends()` later repairs sub-sequence exits so nested blocks flow to the correct next element.

Label handling is central. `set_lab()` records labels with context, block scope, and inline ID. `get_lab()`, `find_lab()`, and `fix_dest()` resolve ordinary and remote label references, including special handling when a label points at a goto. The code rejects labels placed inside ambiguous compound guards and detects jumps into or out of `d_step` with `cross_dsteps()` and `Rjumpslocal()`.

Atomic handling marks ranges with `ATOM`, `L_ATOM`, or `D_ATOM` through `make_atomic()` and `walk_atomic()`, warning or rewriting nested atomic/d_step constructs as needed. `attach_escape()` and `escape_el()` propagate `unless` escape sequences to the states where they can interrupt execution.

The later helpers lower Promela iteration forms. `for_setup()`, `for_index()`, `for_body()`, and `sel_index()` synthesize assignments, loop guards, receives/sends for channel iteration, break destinations, and loop bodies. Validation catches bad index variables, mismatched channel/struct iteration, and reversed constant ranges.

Important risks: much behavior relies on global parser/build state (`cur_s`, `labtab`, `context`, `Fname`, `lineno`, `DstepStart`). Misplaced labels and jumps are fatal because later verifier generation assumes a normalized graph. The file also prunes redundant unlabeled skips, which affects reachability presentation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/flow.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/guided.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/guided.c

`guided.c` replays verifier trail files against Spin’s interpreted model graph. It is used for guided simulations/error-trail replay, including optional xspin/two-column/MSC-style output.

`match_trail()` locates a trail file by explicit `-k` name or by trying `.trail`/`.tra` variants of the model filename, warns if the model is newer, enables timeout handling, calls `hookup()` to resolve compound statement starts, then reads trail records as `depth:process:state`. Special negative depth records start claims, mark merged-statement mode, or print cycle-start markers.

For each trail step it finds the matching `Element` by global `Seqno`, maps the verifier process number onto the active `RunList`, updates `X->pc`, executes or tests transitions with `eval_sub()`, handles merged transitions, and prints process/statement/value output according to verbosity. `D_STEP` replay walks internal substeps until it reaches the enclosing next state.

`find_min()` and `find_max()` compute valid statement-number ranges for a process sequence, including nested compound sequences, to diagnose stale or mismatched trails. `lost_trail()` dumps remaining trail records when replay cannot match a step. `pc_value()` implements the Promela `pc_value()` helper over the active run list.

Important caveats: embedded C code is explicitly not executed during this kind of replay, so variable values can be inaccurate; stale trails are detected only by file modification time; and replay depends on generated statement numbers matching the current parsed model.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/guided.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/main.c

`main.c` is Spin’s command-line front end and lifecycle coordinator. It parses options, invokes the C preprocessor, parses Promela, handles LTL/never-claim injection, chooses simulation vs verifier-generation modes, optionally compiles/runs `pan`, and cleans up temporary/generated files.

Major paths include plain parsing/simulation, `-a` verifier generation, `-run`/`-search` generate-compile-run flow, `-replay` trail replay, `-t` guided trail interpretation, `-f`/`-F` LTL translation, `-N` external never claim inclusion, `-pp` pretty-printing, `-M` MSC/Tcl output, and xspin/internal modes. `preprocess()` builds the preprocessor command from `PreProc` and accumulated `-D`/`-U`/`-E` arguments and writes `pan.pre`.

`alldone()` owns cleanup and the post-parse automation path. In buzzed verifier modes it may replay with Spin itself, reuse or compile `pan.c`, add compile-time macros and runtime flags, run swarm/biterate iterative searches, randomize hash/search parameters, and remove generated `pan.*` files afterward. `final_fiddle()`, `add_runtime()`, and `add_comptime()` translate high-level search options into `pan` compile/runtime options.

`main()` also initializes predefined symbols, seeds Spin’s RNG, parses the model with `yyparse()`, optionally parses generated LTL claims, fixes loose graph ends, performs channel access analysis, disables incompatible statement merging when needed, runs source analysis optimizations, schedules/interprets the model, and exits through `alldone()`.

Supporting functions include `non_fatal()`/`fatal()` diagnostics, zeroing allocator `emalloc()`, access tracking through `setaccess()` and `trapwonly()`, AST node construction in `nn()`, remote label/variable expression builders `rem_lab()`/`rem_var()`, and `explain()` for token names used in diagnostics.

Important risks: command strings are assembled into fixed buffers and executed through `system()`; option parsing mutates global mode flags with broad downstream effects; temporary files have fixed names such as `pan.pre` and `_spin_nvr.tmp`; and many syntax checks depend on global parser state (`context`, `claimproc`, `lineno`, `Fname`).
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/mesg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/mesg.c

`mesg.c` implements Spin’s simulation-time channel and message behavior. It creates queue instances, handles asynchronous and rendezvous send/receive operations, performs message-field type checks, prints send/receive traces, dumps queue contents, and validates channel-use restrictions.

`qmake()` creates `Queue` objects from channel declarations, assigning queue IDs, slot counts, field counts, field widths, backing storage, and step-number tracking. `qsend()` dispatches to asynchronous `a_snd()` or synchronous/rendezvous `s_snd()`. `qrecv()` handles normal queues via `a_rcv()` and has special nonblocking terminal input support for `STDIN`.

Asynchronous send appends or sorted-inserts messages (`sa_snd()`), casts fields to declared widths, records the producing depth, and respects `m_loss` for sends to full queues. Asynchronous receive tests constants and `eval()` constraints, supports random receive/poll variants, writes received values into target variables only on full receives, shifts queue contents after consuming, and emits arrows for MSC output. Rendezvous send stages a single-slot message, calls `complete_rendez()`, and coordinates sender/receiver trace output.

Output helpers `sr_talk()`, `docolumns()`, `difcolumns()`, `sr_buf()`, and `sr_mesg()` format ordinary traces, columnated output, xspin text, mtype names, and MSC/Tcl event labels. `qhide()`/`qishidden()` suppress selected queue output. `doq()` dumps visible queue state for globals/locals output.

Validation helpers catch unsafe channel operations and expression patterns. `nochan_manip()` rejects invalid channel assignments and records channel access. `no_internals()` prevents assignment to internal predefined variables. `scan_tree()` and `no_nested_array_refs()` detect array self-indexing patterns that can break generated verifier backing code.

Important risks: queue count is capped by `MAXQ`; queue IDs are one-based externally and zero-based internally; formatted printing uses a shared `Buf`; rendezvous state uses static remembered receiver pointers; and simulation behavior must match verifier code generated elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/mesg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/msc_tcl.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/msc_tcl.c

`msc_tcl.c` generates Tcl/Tk message sequence chart output for Spin simulations or trail replays. It records process lanes, step labels, message arrows, and initial process boxes, writes a `.tcl` canvas script, then launches it with `wish`.

`putprelude()` opens `<model>.tcl`, optionally counts trail-file lines to size arrays, and allocates depth-to-chart maps (`D`, `R`), lane positions (`M`), arrow targets (`T`), labels (`L`), and initial process labels (`I`). `pstext()` records either an initial process label at depth zero or a chart event at the current simulation depth.

Rendering is deferred until `putpostlude()`. `putpages()` emits the Tcl window, canvas, scrollbars, grid lines, boxes, labels, and message arrows. `psline()` draws grid or message lines, using distinct colors for rendezvous and asynchronous messages. `spitbox()` chooses box colors from event content and escapes text for Tcl. `putarrow()` connects send/receive depths by mapping simulation depth to chart depth.

`dotag()` is the integration point used by ordinary trace printing: in MSC mode it records chart text by process/lane, otherwise it prints indented trace text. `putpostlude()` writes the final page, closes the Tcl file, prints the random seed, removes `pan.pre`, and executes `wish -f <model>.tcl &`.

Important constraints: process lanes are limited to 256, default max steps starts at `2*4096` but is adjusted from trail length, dimensions are heuristic, strings are only lightly escaped, and the file launch uses `system()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/msc_tcl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen1.c

`pangen1.c` is a large part of Spin’s `pan` verifier generator. It emits C header/source fragments for state-vector layout, process structures, queue structures, process creation, queue operations, global/local initialization, claim setup, reachability tables, state labels, variable dumping, and selected helper routines.

`genheader()` writes core verifier definitions: word size, sync/async counts, core count defaults, process-name/type arrays, process structure typedefs via `put_ptype()`, special never-claim wrapper structures for multiple claims, imported template fragments, the `State` structure, TRIX state support, and hidden-variable declarations. It depends heavily on template arrays from `pangen1.h`, `pangen3.h`, and `pangen6.h`.

`genaddproc()` emits the generated `addproc()` switch, process initialization cases through `put_pinit()`, predefined `np_` initialization, optional multiple-claim initialization, and `provided()` gating when proctypes use `provided` clauses. `put_pinit()` sets `_t`, `_p`, priority, reached-state bits, parameters, locals, embedded-code local initialization, and claim metadata.

Variable generation is split across `doglobal()`, `dolocal()`, `do_var()`, `do_init()`, and `typ2c()`. These functions order variables by type, generate struct fields, initialize scalars/arrays/channels, log ranges, warn about reducible types, reject local variables in never claims, and account for bitfield packing through `nBits`/`LstSet`. `walk_struct()` is declared for structured variable traversal and used when structs need initialization/logging.

Queue generation is handled by `genaddqueue()`. It emits queue type typedefs, `NQS`, field storage widths, queue-size helpers, TRIX sizing helpers, random receive-poll helper `Q_has()`, generated `qsend()`, queue-full/synchronous checks, generated receive field extraction and message removal, q-size switch code, prototypes, and the `Addproc` macro.

Other generator support includes `end_labs()` for stop/progress/accept/visible state tables, `c_chandump()`/`c_var()`/`c_wrapper()` for runtime variable and queue printing, `huntstart()`/`huntele()` for resolving executable elements through skips/gotos/unless, `qlen_type()` for compact queue-length fields, and small template emitters `ntimes()`/`ncases()`.

Important risks and coupling: this file assumes normalized `Element`/`Sequence` graphs from `flow.c`, queue metadata from `mesg.c`, process metadata from parser/analyzer state, and many global counters (`nrRdy`, `nqs`, `mst`, `Mpars`, `Npars`, `nclaims`). Generated C correctness depends on exact type widths, array bounds, state numbering, and template fragment compatibility.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spin/pangen1.c -->