# subset-b-009325 research

Grouped research report for selected strace documentation, maintenance generators, and early decoder sources. Each section title preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/doc/strace.1.in -->
# sources/test-tools/strace/doc/strace.1.in

Purpose: canonical roff source for the `strace(1)` manual page. It documents the command synopsis, event trace format, option grammar, filtering, output controls, statistics, tampering, diagnostics, ABI/personality support, caveats, history, and reporting channels. Autoconf substitutions such as `@VERSION@`, `@STRACE_MANPAGE_DATE@`, `@ENABLE_STACKTRACE_FALSE@`, and `@ENABLE_SECONTEXT_FALSE@` make parts of the manual conditional on build features.

Important APIs/types/functions: this file is not executable code, but it defines user-visible contracts for CLI options including `-e` qualifiers, `--trace`, `--trace-fds`, `--status`, `--decode-fds`, `--decode-pids`, `--inject`, `--fault`, `--seccomp-bpf`, `--syscall-limit`, timestamp options, summary columns, stack traces, SELinux contexts, and tip output. It also defines local roff macros `CW`, `CE`, `OM`, and `OR` for code blocks and option formatting.

Control flow: the document progresses from synopsis and conceptual trace examples into option families: startup, tracing, filtering, output format, statistics, tampering, and miscellaneous behavior. Later sections describe exit status behavior, setuid installation, multiple personalities, notes, bugs, history, reporting, and related tools. Conditional roff lines include or omit feature-specific text during configure-time rendering.

State and persistence behavior: documents how `strace` observes live tracee state at syscall entry/exit, dereferences pointers only when safe and relevant, tracks unfinished/resumed calls, can alter tracee behavior with injection/poking/delays, can write one log or per-PID logs, and can leave or kill tracees depending on detach/exit settings.

Dependencies and integration points: integrates with the build system via substitution tokens and with implementation files that parse options, maintain qualifier sets, decode syscalls, collect summaries, implement seccomp filtering, and support mpers ABI decoding. It also references external Linux APIs such as `ptrace(2)`, `seccomp(2)`, signals, namespaces, SELinux, and process credentials.

Risks: because this is the public contract, drift from actual option parsing or decoder behavior is high impact. Conditional feature guards must remain aligned with configure variables. Examples and lists such as syscall classes, summary columns, color keys, and injection syntax are regression-prone when implementation evolves.

Test signals: generated manpage checks, `strace -h`, `strace -V`, CLI option tests, documentation spelling/style checks, and behavior tests for filters, output formatting, seccomp, injection, and mpers should confirm that documented syntax and defaults match the binary.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/doc/strace.1.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/m4/gen_bpf_attr_m4.awk -->
# sources/test-tools/strace/m4/gen_bpf_attr_m4.awk

Purpose: gawk extractor that reads `src/bpf_attr.h` and emits member references for an Autoconf `AC_CHECK_MEMBERS` probe of `union bpf_attr` fields.

Important APIs/types/functions: uses awk regex matching, `match()` capture arrays, state variable `in_struct`, `struct_name`, optional `subtype_name`, and a generated `prefix` that is either `union bpf_attr`, `struct <name>`, or a subtype-qualified path.

Control flow: when a line starts a generated `struct *_struct` block, it records the structure and optional comment subtype, then enters struct mode. In struct mode it matches simple field declarations and prints a tab-indented `prefix.field,` entry. On the closing brace it leaves struct mode.

State and persistence behavior: has only streaming awk state and writes to stdout. It assumes the input header follows the project generator's predictable struct declaration style.

Dependencies and integration points: invoked by `gen_bpf_attr_m4.sh`; output is sorted and wrapped into `m4/bpf_attr.m4`, which is consumed by configure to detect available Linux BPF attribute members.

Risks: regex parsing is intentionally narrow and may miss bitfields, arrays with unusual declarations, nested constructs, or formatting changes. Incorrect member paths can break configure probes or silently omit capability checks.

Test signals: rerunning `m4/gen_bpf_attr_m4.sh` after BPF header changes, Autoconf `AC_CHECK_MEMBERS` success, and generated `bpf_attr.m4` diffs are the main validation signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/m4/gen_bpf_attr_m4.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/m4/gen_bpf_attr_m4.sh -->
# sources/test-tools/strace/m4/gen_bpf_attr_m4.sh

Purpose: shell wrapper that regenerates `m4/bpf_attr.m4` from `src/bpf_attr.h` using the adjacent awk extractor.

Important APIs/types/functions: uses POSIX shell with `-efu`, sets `input=src/bpf_attr.h`, redirects stdout to `m4/bpf_attr.m4`, emits an `AC_DEFUN([st_BPF_ATTR], ...)` body, invokes `gawk -f gen_bpf_attr_m4.awk`, sorts unique member references, and includes `#include <linux/bpf.h>` for the configure probe.

Control flow: writes a fixed m4 header, streams generated members from awk through `sort -u`, then writes a fallback `union bpf_attr.dummy` member and closes the macro.

State and persistence behavior: overwrites the generated m4 file atomically only in the sense of shell redirection at start; an interrupted run could leave a partial file. No temporary file or cleanup is used.

Dependencies and integration points: depends on `gawk`, `src/bpf_attr.h`, and the Autoconf macro consumer. It bridges strace's internal BPF attribute model with configure-time Linux header feature detection.

Risks: direct redirection can truncate output on failure. The script assumes it is run from the repository root and that `${0%/*}` resolves to the `m4` directory.

Test signals: generated `bpf_attr.m4` should contain a normalized `AC_CHECK_MEMBERS` list and configure should detect expected `union bpf_attr` members against current kernel headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/m4/gen_bpf_attr_m4.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/enum2xlat.sh -->
# sources/test-tools/strace/maint/enum2xlat.sh

Purpose: generates strace xlat `.in` tables from C enum definitions in a source header, either listing enum names or writing table content.

Important APIs/types/functions: shell functions `print_help`, `print_usage`, and `gen`; options `-d DIR`, `--list`, `--stdout`; sed extraction of `enum NAME { ... };`; filtering of `_MAX` members; optional `#value_indexed` directive when enum values are implicit.

Control flow: parse options, validate mode/arguments, verify the input file is readable, default enum list from `sed` if no enum names are supplied, then either print enum names, print generated content to stdout, or write each table to `src/xlat/<enum>.in`.

State and persistence behavior: writes generated xlat files under the selected directory unless `--stdout` is used. It does not use temporary files, so interrupted writes can leave partial `.in` files.

Dependencies and integration points: consumed by xlat maintenance and by `update-xlat.sh`, which reconstructs commands from generated headers. The generated files feed `src/xlat/Makemodule.am` and decoder constant tables.

Risks: enum parsing is line-oriented and uppercase-name oriented; comments, explicit complex values, multiline names, or lowercase constants can be skipped. `eval` users downstream rely on the generated header line remaining stable.

Test signals: `--list` should enumerate expected enums; `--stdout` diffs should match checked-in xlat tables; xlat generation and decoder builds should continue to compile.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/enum2xlat.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/errnoent.sh -->
# sources/test-tools/strace/maint/errnoent.sh

Purpose: converts preprocessor errno definitions into indexed C initializer entries for strace errno tables.

Important APIs/types/functions: one awk program reads `#define E... <number>` lines, stores `errno[number] = name`, tracks `max`, and prints array slots as `[ n ] = "ENAME",`.

Control flow: all input files are processed by awk; matching definitions update the map and maximum numeric value. The END block emits all present entries from 0 through `max`.

State and persistence behavior: no persistent writes; output is stdout. Duplicate errno numbers are overwritten by later input definitions.

Dependencies and integration points: used for architecture-specific errno table generation from kernel or libc headers; output integrates with strace's architecture errno lookup headers.

Risks: only simple numeric `#define` values are accepted; aliases, expressions, negative values, or macro indirection are ignored. Input order affects duplicates.

Test signals: generated errno tables should include expected numeric names, build successfully, and match runtime errno decoding tests for target architectures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/errnoent.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/find-new-xlat-constants.sh -->
# sources/test-tools/strace/maint/find-new-xlat-constants.sh

Purpose: compares Linux kernel header constants across a commit range and reports constants newly added upstream that are not represented in existing strace xlat tables.

Important APIs/types/functions: shell functions `extract_xlat_constants`, `extract_prefix_directive`, `extract_pattern_directive`, `calculate_prefix`, `extract_all_header_constants`, prefix/pattern filters, and `process_line`. It uses Git object access, `sed`, `awk`, `grep`, `comm`, `sort`, and temporary files.

Control flow: validates `-d LINUX_REPO` and a two-dot commit range, verifies both commits, creates temp files, reads a tab-separated table from stdin (`xlat_file`, `line_type`, `header_file`), skips missing files/headers, extracts constants already in xlat, derives a matching prefix or uses `#Prefix`/`#Pattern`, extracts matching constants from both commits, then prints rows where constants exist in the newer commit but not the older commit or xlat.

State and persistence behavior: changes directory briefly for Git validation, then processes through temp files removed by traps. It emits report rows to stdout and does not modify xlat files.

Dependencies and integration points: pairs with `list-xlat-linux-headers.sh -t -c` to build the input table. It integrates kernel-header update review with strace xlat maintenance.

Risks: prefix inference can be too broad or too narrow; regex extraction of enum and define names can include false positives or miss lower/macro-expression constants. Only two-dot ranges are accepted. `comm` correctness depends on sorted inputs.

Test signals: running against known Linux tag ranges should identify expected new constants without noisy unrelated rows; shellcheck-like validation and temp cleanup on interrupts are useful operational checks.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/find-new-xlat-constants.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/gen-contributors-list.sh -->
# sources/test-tools/strace/maint/gen-contributors-list.sh

Purpose: produces a unique contributor list for a commit range, optionally including email addresses and optionally merging additional contributors from stdin.

Important APIs/types/functions: `get_commit_id`, `git describe`, `git log`, sed regexes for trailer-like author lines, `git check-mailmap`, sorting, and options `-e/--include-email`, `-/--stdin`, `LAST_COMMIT`, `FIRST_COMMIT`, and `--initial`.

Control flow: parse options, resolve the upper commit and lower bound tag/commit/root, choose output regex based on email inclusion, collect matching names from `git log` and optional stdin, normalize through mailmap, sort unique, and strip or retain email addresses.

State and persistence behavior: no writes; relies on repository history and `.mailmap` state. Output ordering is locale-controlled through `LC_COLLATE=C`.

Dependencies and integration points: called by `gen-tag-message.sh` for release notes and can be used manually for credits. It depends on commit message formatting conventions.

Risks: regex only recognizes specific indented contributor line forms and may miss nonstandard trailers. `--help` exits with status 1, which is unusual for help paths.

Test signals: generated release contributor blocks should match expected mailmap-canonical names for a release range; stdin mode should add normalized extra contributors.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/gen-contributors-list.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/gen-release-github.sh -->
# sources/test-tools/strace/maint/gen-release-github.sh

Purpose: formats a release announcement body for GitHub releases.

Important APIs/types/functions: invokes `gen-tag-message.sh`, escapes literal asterisks with sed, and appends a Downloads warning telling readers to ignore GitHub-generated source links.

Control flow: stream tag message through sed, then append a fixed Markdown downloads section.

State and persistence behavior: no persistent state; output is stdout.

Dependencies and integration points: used in release publication flow after `gen-tag-message.sh`. Integrates with GitHub release notes UI conventions.

Risks: Markdown escaping is broad and can alter intended emphasis. The generated download section contains placeholder text rather than artifact-specific checksums or URLs.

Test signals: rendered GitHub release text should preserve NEWS formatting, contributor bullets, and the downloads warning without broken Markdown.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/gen-release-github.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/gen-release-gitlab.sh -->
# sources/test-tools/strace/maint/gen-release-gitlab.sh

Purpose: formats release text for GitLab, including upload links for local `strace-*.tar.xz*` artifacts.

Important APIs/types/functions: shell glob expansion, `set +f`/`set -f`, fixed Markdown output, and `gen-tag-message.sh` piped through sed asterisk escaping.

Control flow: print a Downloads header, iterate matching tarball files and emit placeholder `/uploads/...` links, print the GitLab source-link warning, then append the escaped tag message.

State and persistence behavior: reads current directory artifact names and writes stdout only.

Dependencies and integration points: used after distribution artifact generation, likely with manual replacement of upload placeholders in GitLab release drafting.

Risks: if no glob matches, POSIX shells can leave the literal pattern as a file candidate. Upload path placeholder `"..."` requires human or CI replacement. Markdown escaping can affect intended formatting.

Test signals: in a release directory, output should list each tarball/signature and render cleanly in GitLab Markdown.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/gen-release-gitlab.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/gen-release-notes.sh -->
# sources/test-tools/strace/maint/gen-release-notes.sh

Purpose: emits release notes as HTML-preformatted text.

Important APIs/types/functions: prints `<pre>`, invokes adjacent `gen-tag-message.sh`, prints `</pre>`.

Control flow: a simple three-step wrapper with strict shell mode.

State and persistence behavior: no persistent state; stdout is the artifact.

Dependencies and integration points: integrates with release channels that expect preformatted HTML rather than Markdown.

Risks: no escaping is performed, so unexpected HTML-significant characters from NEWS or contributor names could affect rendering. It depends wholly on `gen-tag-message.sh` correctness.

Test signals: generated text should contain the current release NEWS excerpt and contributor block enclosed in a single preformatted element.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/gen-release-notes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/gen-tag-message.sh -->
# sources/test-tools/strace/maint/gen-tag-message.sh

Purpose: constructs an annotated tag or release message from the top section of `NEWS` plus a contributor list.

Important APIs/types/functions: `get_commit_id`, `mktemp`, trap-based cleanup, `git show "$id:NEWS"`, sed extraction of the release marker, UTC date formatting, dynamic underline generation, and `gen-contributors-list.sh`.

Control flow: resolve commit argument or HEAD, copy that commit's NEWS to a temp file, extract the release version from the first `Noteworthy changes` marker, print a dated title and underline, print NEWS content until the next release marker, then append a fixed contributor intro and bulletized contributor names.

State and persistence behavior: uses a temporary NEWS copy removed on exit; no repository writes. Output embeds current UTC date, so it is intentionally time-dependent.

Dependencies and integration points: called by GitHub/GitLab/release-note wrappers and release tagging workflows. Depends on NEWS section format and git history.

Risks: malformed NEWS markers produce an empty version or wrong section. Date-sensitive output can make reproducible comparisons fail. Contributor generation inherits mailmap/trailer regex limitations.

Test signals: for a tagged release commit, the message should contain exactly the intended NEWS section, current release version, generated date, and contributors since previous `v*` tag.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/gen-tag-message.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/gen/Makefile -->
# sources/test-tools/strace/maint/gen/Makefile

Purpose: standalone makefile for building the strace decoder-definition generator and producing generated decoder C sources from `.def` files.

Important APIs/types/functions: variables `CPPFLAGS`, `TARGET=gen`, object list, dependency files, `GEN_IN=hdio.def`, generated output path `../../src/gen/gen_%.c`, and rules for `flex`, `bison -d`, dependency generation, and cleanup.

Control flow: default target builds `gen` and generated output files. `lex.yy.c` is produced from `lex.l`; `parse.tab.c/h` from `parse.y`; object files link into `gen`; each `defs/%.def` is compiled by running `./gen input output`.

State and persistence behavior: writes build products, generated parser/lexer C, `.d` files, the `gen` executable, and generated decoder files under `src/gen`.

Dependencies and integration points: depends on a C compiler, Flex, Bison, local generator sources, and definition files. The generated C integrates into `src/Makefile.am` through `gen/gen_hdio.c` and `gen/generated.h`.

Risks: dependency inclusion requires `parse.tab.h` ordering. No install target or atomic output for generated C. The makefile is separate from the main Automake flow and can drift.

Test signals: `make` in `maint/gen` should build `gen` and regenerate `src/gen/gen_hdio.c`; `make clean` should remove generated build artifacts.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/gen/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/gen/ast.c -->
# sources/test-tools/strace/maint/gen/ast.c

Purpose: allocation, interning, comparison, and freeing helpers for the generator DSL AST.

Important APIs/types/functions: `create_ast_node`, list/node constructors, `known_type`, `known_type_option`, `compare_type_option_list`, `ast_type_matching`, `create_or_get_type`, type-option constructors, and `free_ast_tree`.

Control flow: parser actions call constructors as grammar reductions occur. `create_or_get_type` checks the interned list before resolving a type through `resolve_type`; type options for numbers and nested types are also interned when possible. Matching supports template options for decoder selection. Freeing recursively releases AST nodes and selected owned strings/lists.

State and persistence behavior: process-local global intern tables `known_types` and `known_type_options` persist for the generator run. AST nodes store source locations using `cur_filename` and Bison locations. No file writes happen here.

Dependencies and integration points: used by `parse.y`, `lex.l`, `symbols.c`, `preprocess.c`, and `codegen.c`. Depends on `xmalloc` helpers and Bison `YYLTYPE`.

Risks: lifetime ownership is mixed: interned types and options are not comprehensively freed, acceptable for a short generator but relevant for tools/reuse. `free_ast_tree` does not deeply free all type structures. Template matching intentionally treats template IDs as wildcards only in matching mode.

Test signals: parser tests with duplicate declarations, nested types, template decoders, and malformed type options should produce expected ASTs or errors without crashes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/gen/ast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/gen/ast.h -->
# sources/test-tools/strace/maint/gen/ast.h

Purpose: public AST type model for the decoder-definition generator.

Important APIs/types/functions: defines `ast_number`, `ast_node_type`, structs for syscalls, arguments, structs, flags, locations, type options, and `ast_type`. Standard type categories include `TYPE_BASIC`, `TYPE_CONST`, `TYPE_PTR`, `TYPE_REF`, `TYPE_XORFLAGS`, and `TYPE_ORFLAGS`; pointer direction helpers `IS_IN_PTR`, `IS_OUT_PTR`, and `IS_INOUT_PTR` support code generation.

Control flow: the header encodes the tree/list shape consumed by parser reductions, preprocessing, and code generation. AST nodes use a tagged union to represent statements such as syscalls, defines, includes, conditionals, flags, structs, and custom decoders.

State and persistence behavior: only type declarations and function prototypes; no storage except through users of these types.

Dependencies and integration points: included by almost every `maint/gen` C file. Its type contracts drive symbol resolution, variant grouping, decoder matching, and output generation.

Risks: changes are high blast radius across Bison actions and codegen. Flexible ownership of char pointers and nested type options is not obvious from the declarations, increasing leak/double-free risk for future modifications.

Test signals: full generator compile plus successful parse/codegen of existing `.def` files validates structural compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/gen/ast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/gen/codegen.c -->
# sources/test-tools/strace/maint/gen/codegen.c

Purpose: converts the preprocessed generator AST into C decoder functions that use strace's syscall-printing APIs.

Important APIs/types/functions: type mapping arrays, decoder list, output helpers, `type_to_ctype`, `type_variable_declaration`, `get_sys_func_return_flags`, `resolve_type_option_to_value`, pointer/value printers, `generate_templated_printer`, `generate_printer`, `generate_return_flags`, `generate_decoder`, `output_defines`, `output_variant_syscall_group`, `output_syscall_groups`, and `generate_code`.

Control flow: `generate_code` opens the output file, writes headers/includes, stores decoder templates, emits preprocessor statements, and recursively emits syscall groups. For each syscall it chooses an entry/exit printing strategy based on out-pointer count, prints arguments using explicit or inferred decoders, handles variants by dispatching on `const` arguments, and returns appropriate `RVAL_*` flags.

State and persistence behavior: writes generated C output. Runtime state during generated decoder execution can use `set_tcb_priv_data` for inout pointer snapshots. Codegen itself stores decoder templates in a static pointer and emits warnings to stderr.

Dependencies and integration points: depends on `processed_ast` from `preprocess.c`, symbols from `ast.c`, strace C helper APIs such as `tprints_arg_name`, `umove_or_printaddr`, `printflags64`, `printxval64`, `RVAL_DECODED`, and generated DSL definitions.

Risks: more than one out pointer is currently emitted as `#error TODO`, so DSL inputs must avoid that shape. `store_single_value` copies `tmp_var` using `memcpy(tmp_buffer, tmp_var, sizeof(tmp_var))`, which is subtle for arrays/pointers. Template substitution has fixed stack/substitution arrays and warnings for unresolved refs rather than hard failures.

Test signals: generated C should compile without `#error` for all checked-in definitions, and decoder output tests should verify variant dispatch, pointer directions, flag printers, and return-value formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/gen/codegen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/gen/deflang.h -->
# sources/test-tools/strace/maint/gen/deflang.h

Purpose: shared declarations for the generator's lexer, parser, preprocessor, and code generator.

Important APIs/types/functions: declares external `yyin`, `last_line_location`, `cur_filename`, `lexer_init_newfile`, formatted `yyerror`, and `generate_code`. Includes `preprocess.h` and `xmalloc.h`.

Control flow: not executable itself; it provides the cross-module contract used by generated Bison/Flex code and handwritten generator C.

State and persistence behavior: exposes lexer/parser globals for current file and error-position tracking.

Dependencies and integration points: central include for `lex.l`, `parse.y`, `ast.c`, `symbols.c`, `preprocess.c`, and `codegen.c`.

Risks: global variables make the generator single-threaded and require careful reset between imported files or repeated parses.

Test signals: successful Flex/Bison compilation and useful syntax-error locations validate this header's declarations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/gen/deflang.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/gen/lex.l -->
# sources/test-tools/strace/maint/gen/lex.l

Purpose: Flex lexer for the strace decoder-definition language.

Important APIs/types/functions: token rules for punctuation, decimal/hex/binary/character numbers, template identifiers like `$1`, identifiers including `@ret`, `%{...%}` decoder source blocks, `define`, `#ifdef`, `#ifndef`, `include`, `#endif`, comments, and `#import`. It uses import stack state, `cur_filename`, `cur_location`, `last_line_location`, and `update_yylloc`.

Control flow: normal lexing returns Bison tokens while tracking source coordinates. On `#import "file"` it saves lexer state, opens the imported file, pushes a buffer, and resumes from that file. EOF emits a synthetic newline once, then pops import state or terminates.

State and persistence behavior: maintains global current filename/location and a bounded import stack of 10 levels. It opens imported files but relies on buffer cleanup rather than explicit close in the visible code path.

Dependencies and integration points: consumed by Bison parser in `parse.y`; uses `xstrdup`, `yyerror`, and Bison semantic values.

Risks: import paths are used directly and nesting beyond 10 aborts. Identifier and decoder-source regexes encode DSL syntax tightly. Location tracking must remain synchronized with manual input consumption in import handling.

Test signals: parse definitions with imports, comments, template identifiers, binary/hex literals, `@ret`, and decoder blocks; error messages should point to the correct file/line/column.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/gen/lex.l -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/gen/parse.y -->
# sources/test-tools/strace/maint/gen/parse.y

Purpose: Bison grammar and main program for the decoder-definition generator.

Important APIs/types/functions: grammar productions for compound statements, syscalls, typed arguments, return types, type option lists/ranges/templates, defines, includes, conditionals, structs, flags, and decoder source blocks. Helper `error_prev_decl`, formatted `yyerror`, and `main` are defined here.

Control flow: `main` validates input/output arguments, initializes the lexer, runs `yyparse`, preprocesses the root AST, calls `generate_code`, and frees the AST. Grammar actions construct AST nodes and insert named syscalls/structs/flags into the symbol table, rejecting duplicate declarations.

State and persistence behavior: uses static `root`, Bison error count/location state, lexer globals, and symbol table state. Writes only through `generate_code`.

Dependencies and integration points: tied to `lex.l` token stream, `ast.c` constructors, `symbols.c` duplicate detection, `preprocess.c`, and `codegen.c`.

Risks: error recovery can continue through malformed lines but may leave partial AST state. Some grammar productions accept attributes but ignore them (`syscall_attribute`, `struct_attr`), so future syntax assumptions need care.

Test signals: invalid duplicate declarations should produce previous-location errors; malformed type options should print source context; existing `.def` files should parse and generate compilable C.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/gen/parse.y -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/gen/preprocess.c -->
# sources/test-tools/strace/maint/gen/preprocess.c

Purpose: transforms the raw AST into a `processed_ast` organized for code generation: preprocessor statements, custom decoders, and grouped syscall variants with condition metadata.

Important APIs/types/functions: `condition_stack`, `create_statement_condition`, `strip_whitespace`, `processing_state`, `preprocess_rec`, `find_matching`, `syscall_comparator`, `group_syscall_variants`, and `preprocess`.

Control flow: recursively walks AST nodes, pushing condition strings for `#ifdef`/`#ifndef`, collecting defines/includes with current conditions, adding decoder templates, converting syscall AST nodes into flat `struct syscall` entries, then sorting by syscall name and grouping `$`-delimited variants into parent/child trees.

State and persistence behavior: allocates processed structures and condition snapshots; no file output. Maximum preprocessor nesting is 16 and maximum syscall count is 4096.

Dependencies and integration points: consumes `ast.h` nodes from the parser and produces `preprocess.h` structures for `codegen.c`.

Risks: the `invert` flag for `#ifndef` is not reflected when storing conditions; the original condition text is emitted as parsed, so correctness depends on lexer token value. Fixed maximum counts can assert or overflow if definition files grow unexpectedly.

Test signals: variant syscall names such as `prctl$...` should group under base syscalls; nested conditionals should wrap generated output in matching preprocessor blocks.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/gen/preprocess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/gen/preprocess.h -->
# sources/test-tools/strace/maint/gen/preprocess.h

Purpose: declares the intermediate representation passed from AST preprocessing to code generation.

Important APIs/types/functions: `statement_condition`, `preprocessor_statement`, `preprocessor_statement_list`, `struct_def`, `syscall_argument`, `decoder`, `decoder_list`, `syscall`, `syscall_group`, `processed_ast`, and `preprocess`.

Control flow: not executable; defines how conditional wrappers, syscall definitions, decoder templates, and variant trees are represented.

State and persistence behavior: structures use flexible arrays for condition values and syscall arguments, with allocation performed by `preprocess.c`.

Dependencies and integration points: included by `deflang.h` and `codegen.c`; all generated decoder behavior depends on this IR's fields.

Risks: ownership and lifetime are implicit. `struct_def` is present but marked TODO, so struct statements are not fully represented beyond symbol/type lookup.

Test signals: compile-time compatibility plus generated decoder output for conditional and variant definitions validates the IR.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/gen/preprocess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/gen/symbols.c -->
# sources/test-tools/strace/maint/gen/symbols.c

Purpose: symbol table and type resolver for the generator DSL.

Important APIs/types/functions: linked-list `symbol_entry`, global `symbol_table`, `symbol_get`, `symbol_add`, and `resolve_type`. `resolve_type` recognizes special types `const`, `ptr`, `ref`, `xor_flags`, and `or_flags`, validates option counts/kinds, and fills `struct ast_type`.

Control flow: parser actions add named declarations to catch duplicates. Type construction calls `resolve_type`, which starts every type as `TYPE_BASIC`, then rewrites the union fields for special names after validating options.

State and persistence behavior: symbol table is process-global for one generator run. Types are returned through caller-provided storage and may reference option/type nodes interned elsewhere.

Dependencies and integration points: called by `ast.c` and `parse.y`; `codegen.c` relies on resolved type tags to choose printers and dispatch behavior.

Risks: some error strings mention the wrong type name (`len`/`ptr`) in messages. Template identifiers are rejected as ordinary options here, while template-aware matching is handled elsewhere. No cleanup of symbol table entries is visible.

Test signals: invalid `ptr` direction, wrong option counts, duplicate symbols, and flag/ref types should produce deterministic parser errors.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/gen/symbols.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/gen/symbols.h -->
# sources/test-tools/strace/maint/gen/symbols.h

Purpose: public interface for generator symbol registration and type resolution.

Important APIs/types/functions: prototypes `resolve_type`, `symbol_add`, and `symbol_get`; includes `ast.h`.

Control flow: not executable; consumers call these functions during parsing and AST type interning.

State and persistence behavior: documents return contracts but not the underlying global symbol table.

Dependencies and integration points: included by `parse.y`, `ast.c`, `preprocess.c`, and `codegen.c`.

Risks: sparse documentation leaves ownership and thread-safety implicit. Header guard closing comment has a compact `//SYMBOLS_H` style but no functional issue.

Test signals: generator builds and duplicate/type-error parser tests exercise this interface.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/gen/symbols.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/gen/xmalloc.c -->
# sources/test-tools/strace/maint/gen/xmalloc.c

Purpose: fail-fast allocation helpers for the standalone generator.

Important APIs/types/functions: `die_out_of_memory`, `free_by_pointer`, `xmalloc`, `xcalloc`, `xstrdup`, and `xasprintf`.

Control flow: each allocation wrapper calls the libc allocator, exits with an error message on failure, and returns allocated memory otherwise. `xasprintf` wraps `vasprintf`.

State and persistence behavior: no persistent state except heap allocations returned to callers. `free_by_pointer` supports GCC cleanup attributes by freeing and nulling a pointer variable.

Dependencies and integration points: included across maint/gen to avoid repetitive allocation checks and support `CLEANUP_FREE`.

Risks: exits on allocation failure rather than propagating errors. `xasprintf` calls `va_end` only after successful `vasprintf`; if `vasprintf` fails and exits, cleanup is skipped but process termination makes it immaterial.

Test signals: normal generator build/run validates use sites; fault-injected allocation tests would confirm fail-fast behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/gen/xmalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/gen/xmalloc.h -->
# sources/test-tools/strace/maint/gen/xmalloc.h

Purpose: declarations and GCC attribute macros for the generator allocation helpers.

Important APIs/types/functions: `ATTRIBUTE_FORMAT`, `ATTRIBUTE_MALLOC`, `ATTRIBUTE_ALLOC_SIZE`, `ATTRIBUTE_CLEANUP`, `CLEANUP_FREE`, and prototypes for allocation/string helpers.

Control flow: not executable; annotations improve compiler diagnostics and cleanup ergonomics.

State and persistence behavior: no state.

Dependencies and integration points: used by all handwritten generator modules and by `deflang.h`.

Risks: depends on GNU C attributes, matching `CPPFLAGS=-std=gnu99`. Porting to non-GNU compilers would require compatibility shims.

Test signals: compiler format warnings for `xasprintf` callers and successful `CLEANUP_FREE` usage in codegen validate the declarations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/gen/xmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/gen_xlat_defs.sh -->
# sources/test-tools/strace/maint/gen_xlat_defs.sh

Purpose: regenerates xlat `.in` definitions from Linux UAPI headers while preserving comments/directives and representing architecture-specific value differences with preprocessor guards.

Important APIs/types/functions: Bash option parser for `-f`, `-p`, `-d`, `-c`, and `-a`; sed/grep extraction of common and arch-specific `#define`s; embedded awk `mystrtonum` for octal/hex/decimal conversion; emitted `#if/#elif/#else/#endif` blocks.

Control flow: validate all required options, print a generated-by header, read existing xlat content from stdin, pass through comments/empty directives, and for each constant search common headers for a default value and arch headers for overrides. The awk stage groups differing values by architecture macros and emits guarded xlat entries.

State and persistence behavior: reads stdin and kernel source tree; writes stdout only. It logs warnings for missing or resolved definitions to stderr.

Dependencies and integration points: feeds xlat maintenance for constants whose numeric values vary by architecture. Its generated header is parsed by `list-xlat-linux-headers.sh` and `update-xlat` workflows.

Risks: shell globbing over kernel header patterns and regex extraction can be fragile. The script is Bash-specific despite a `/bin/bash` shebang. Architecture macro normalization is hard-coded for arm64/aarch64 and x86.

Test signals: regenerated xlat files should preserve existing comments, include correct default and arch-guarded values, and compile through xlat generation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/gen_xlat_defs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/ioctls_gen.sh -->
# sources/test-tools/strace/maint/ioctls_gen.sh

Purpose: orchestrates ioctl table generation from Linux include directories, producing `ioctls_inc.h` and optionally `ioctls_arch.h`.

Important APIs/types/functions: include path canonicalization, temporary `ioctls_hex.h`/`ioctls_sym.h`, helper invocations `ioctls_hex.sh` and `ioctls_sym.sh`, KVM splitting into arch output, Android staging inclusion, sorting, and trap cleanup.

Control flow: validate one or two include directories, generate known hex ioctl entries from selected headers, generate symbolic ioctl entries using compile/DWARF pipeline, split KVM constants to arch output, append Android staging ioctls if present, sort unique into `ioctls_inc.h`, then repeat arch-specific generation when an arch include directory is supplied.

State and persistence behavior: writes generated headers in the current directory and temporary helper headers that are removed by cleanup. Logs counts to stderr.

Dependencies and integration points: core maintainer tool for updating strace's ioctl lookup tables. Depends on Linux UAPI tree layout and the symbolic/hex helper scripts.

Risks: writes output in current directory, so invocation location matters. Helper failures can produce partial headers. KVM reassignment relies on `linux/kvm.h` string matching.

Test signals: generated counts should be plausible, headers should sort/deduplicate, and resulting strace build/tests should decode known ioctl constants.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/ioctls_gen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/ioctls_hex.sh -->
# sources/test-tools/strace/maint/ioctls_hex.sh

Purpose: extracts ioctl constants defined directly as hexadecimal command numbers from selected header files.

Important APIs/types/functions: accepts include directory, type regex, and header paths; constructs a define regex; greps both plain and `uapi/` paths; sed formats entries as `{ "header", "NAME", 0, VALUE, 0 },`.

Control flow: validate arguments, `cd` into include directory, search each requested file for matching `#define` lines, normalize `uapi/` prefixes, format entries, and sort unique.

State and persistence behavior: no writes; stdout is generated table content.

Dependencies and integration points: called repeatedly by `ioctls_gen.sh` for known ioctl families that are easier to detect by command-number high byte.

Risks: only direct hex literals matching `0xTYPE..` are captured; symbolic `_IO*` definitions are intentionally handled elsewhere. Regex type argument can be broad and may include false positives.

Test signals: grep counts in `ioctls_gen.sh` and generated entries for hdreg, fb, loop, cdrom, termios, sockios, wireless, and related headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/ioctls_hex.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/ioctls_sym.awk -->
# sources/test-tools/strace/maint/ioctls_sym.awk

Purpose: parses normalized DWARF debug information for synthetic ioctl variables and emits ioctl table entries.

Important APIs/types/functions: `dirmap`, `array_get`, `dir2str`, DWARF line handlers for DIE ids, names, types, bounds/counts, and tags, plus END logic that reconstructs `_IOC` direction/type/number/size fields.

Control flow: as `readelf` output is streamed in, the awk script records DIE parent relationships and attributes. At END it finds variables named `ioc_<NAME>`, follows their type/member data for fields `d`, `n`, and `s`, groups ioctl names by encoded value, filters redundant aliases/time32/time64 variants, and prints `{ "HEADER", "NAME", DIR, NR, SIZE },`.

State and persistence behavior: in-memory associative arrays only. Exits nonzero on missing expected DWARF attributes or unknown direction values.

Dependencies and integration points: invoked by `ioctls_sym.sh` after compiling generated C that encodes ioctl macros as array sizes. It is the final symbolic extraction stage.

Risks: tightly coupled to `readelf --debug-dump=info` formatting and the synthetic struct layout produced by `ioctls_sym.sh`. Alias filtering can suppress names that are substrings of others.

Test signals: known symbolic ioctl headers should produce stable entries; failures should identify the header and missing attribute.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/ioctls_sym.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/ioctls_sym.sh -->
# sources/test-tools/strace/maint/ioctls_sym.sh

Purpose: discovers ioctl macros defined through `_IO`, `_IOR`, `_IOW`, `_IOWR`, and related symbolic forms by preprocessing and compiling candidate Linux headers, then extracting encoded values from DWARF.

Important APIs/types/functions: candidate header discovery via `find`/`grep`, temp include overrides for `asm/ioctl.h`, `process_file`, generated `printents.c`, many header-specific workaround cases, `CPP`, `CC`, `READELF`, `fixes.h`, `defs.h`, and `ioctls_sym.awk`.

Control flow: find headers containing ioctl-like macro patterns, set up a temporary include tree redefining `_IOC` to encode fields as array sizes, then process each header in a subshell. For each file, generate compatibility includes/workarounds, possibly rewrite or filter header content, preprocess with `-dD`, extract locally defined ioctl names, create declarations `struct {NAME;} ioc_NAME;`, compile with DWARF, dump debug info, normalize it, run awk, and output entries.

State and persistence behavior: uses a temp directory removed on exit. Emits ioctl entries to stdout and progress/failure messages to stderr. Environment variables can override compiler/preprocessor/readelf and flags.

Dependencies and integration points: called by `ioctls_gen.sh`; depends heavily on Linux UAPI header layout and compiler/debug-info behavior. Supports prefixing header names for Android staging.

Risks: large maintenance surface of fragile per-header workarounds. Build failures for one header are counted but do not abort the whole run. Host architecture affects KVM and other filtering. DWARF format/compiler changes can break extraction.

Test signals: processing a Linux header tree should finish with low/no failed files and produce stable sorted ioctl entries that compile into strace's ioctl lookup tables.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/ioctls_sym.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/ioctls_zfs.sh -->
# sources/test-tools/strace/maint/ioctls_zfs.sh

Purpose: scrapes OpenZFS ioctl definitions into strace ioctl table format.

Important APIs/types/functions: reads OpenZFS `META` version, constructs temporary C source/executable, helper `obtain`, includes `include/sys/fs/zfs.h` and `lib/libspl/include/sys/kstat.h`, compiles with `cc`, and executes generated code to print encoded constants.

Control flow: change to supplied OpenZFS clone, create temp source/executable, generate a C program that prints ioctl entries for selected ZFS/KSTAT constants, compile it with OpenZFS include paths, print a generated header plus hard-coded `BLKZNAME`, then run the executable.

State and persistence behavior: temporary files are removed by traps. No repository writes; stdout is intended to be captured into a generated header.

Dependencies and integration points: maintainer-only helper for updating `ioctls_zfs.h`, separate from Linux UAPI extraction because OpenZFS maintains its ABI outside Linux headers.

Risks: executes compiled code from the target OpenZFS headers, so it should be run only on trusted source trees. Assumes include layout and `META` version format.

Test signals: output should include the OpenZFS version and expected `ZFS_IOC_*`/`KSTAT_IOC_*` entries; compilation failure indicates include/API drift.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/ioctls_zfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/list-xlat-linux-headers.sh -->
# sources/test-tools/strace/maint/list-xlat-linux-headers.sh

Purpose: derives Linux header paths referenced by generated strace xlat files and can output a table suitable for changed-header/new-constant analysis.

Important APIs/types/functions: option parser for `-d LINUX_SRC`, `-t`, and `-c COMMIT_RANGE`; functions `expand_pattern`, `find_common_headers`, `find_arch_headers`, `process_gen_xlat_defs_line`, `process_enum2xlat_line`, `process_from_line`, and commit-range filtering using `git diff`, `cut`, `sort`, `join`.

Control flow: validate Linux source tree and optional commit range, scan each xlat file for `#Generated by maint/gen_xlat_defs.sh`, `#Generated by maint/enum2xlat.sh`, or `#From` lines, resolve referenced common/arch/header paths relative to Linux source, output either headers or `xlat_file<TAB>line_type<TAB>header_file`, then optionally filter table rows to headers changed in a two-dot commit range.

State and persistence behavior: uses temp files only in commit-filter mode and removes them with traps. No xlat modifications.

Dependencies and integration points: feeds `find-new-xlat-constants.sh`; also helps maintainers understand which Linux headers drive xlat tables.

Risks: generated-by line parsing depends on exact quoting in xlat headers. `enum2xlat` paths are expected under `bundled/linux/`. Glob expansion occurs in shell and can be sensitive to current directory after `cd "$LINUX_SRC"`.

Test signals: table mode should include stable rows for known generated xlat files; `-c` should reduce rows to changed headers for a known Linux range.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/list-xlat-linux-headers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/make-dist -->
# sources/test-tools/strace/maint/make-dist

Purpose: release helper that creates a clean distribution checkout, runs bootstrap/configure/distcheck, performs release checks, and exports source artifacts.

Important APIs/types/functions: resolves commit id, computes parallel make jobs from `getconf`, clones the local `.git` with `git clone -n -s`, runs `git checkout`, `build-aux/git-set-file-times`, `bootstrap`, `configure --enable-maintainer-mode`, `make distcheck`, optional `make news-check`, `make-dsc`, and copies `strace.spec` and tarballs.

Control flow: create a temp dist directory named with the shell PID, install cleanup trap, clone and checkout requested commit, prepare autotools tree, run distribution checks, skip news check if commit is not exactly tagged `v*`, generate Debian source control text, copy spec and tar artifacts up one level.

State and persistence behavior: creates and deletes the dist checkout; leaves `strace.dsc`, `strace.spec`, and tarballs in the original working directory. Uses `set -x` for traceability.

Dependencies and integration points: release engineering flow; depends on Git, Autotools, make, maintainer-mode dependencies, and `make-dsc`.

Risks: cleanup trap uses unquoted variables in places and removes the temp dir on exit; failures before artifact copy leave no dist tree for inspection. Shared clone assumes local `.git` is complete.

Test signals: successful `make distcheck`, optional `news-check`, generated tarballs, Debian `.dsc`, and spec file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/make-dist -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/make-dsc -->
# sources/test-tools/strace/maint/make-dsc

Purpose: emits a Debian `.dsc` source control file for given tarball artifacts using metadata from `debian/control` and `debian/changelog`.

Important APIs/types/functions: stdin redirected from `/dev/null`, `sed` extraction of package fields, package-list construction for `strace`, `strace64`, and `strace-udeb`, and checksum sections using `sha1sum`, `sha256sum`, `md5sum`, and `stat -c %s`.

Control flow: print fixed `Format: 1.0`, derive source/binary/architecture/version/maintainer/homepage/standards/build-depends fields, print package list with arch values, then iterate input files for SHA1, SHA256, and MD5 file entries while transforming tarball names to Debian `.orig` naming.

State and persistence behavior: stdout only; reads Debian packaging files and artifact files.

Dependencies and integration points: called by `make-dist` to produce `strace.dsc` for release artifacts.

Risks: assumes exact Debian control paragraph formatting and package names. Filename transformation is simple and may not cover unusual artifact names.

Test signals: generated `.dsc` should parse with Debian tooling and contain correct checksums/sizes for all supplied tarballs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/make-dsc -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/signalent.sh -->
# sources/test-tools/strace/maint/signalent.sh

Purpose: converts signal `#define SIG... <number>` lines into indexed signal-name table entries.

Important APIs/types/functions: pipeline of `cat`, `sed`, numeric sort/uniq, and awk formatting with placeholder names for gaps.

Control flow: strip comments, extract signal names and numbers, sort by number, skip duplicates, emit `"SIG_<n>"` placeholders for missing numeric slots up to each found signal, then emit the named signal entry aligned with tabs. It ignores signals above 256.

State and persistence behavior: stdout only.

Dependencies and integration points: used to generate architecture signal tables for strace's signal decoding.

Risks: only simple numeric defines are recognized; aliases and macro expressions are skipped. The awk assignment `n` appears duplicated but harmless.

Test signals: generated signal tables should include expected arch signal names and placeholders, and signal decoding tests should resolve common signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/signalent.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/syscallent.sh -->
# sources/test-tools/strace/maint/syscallent.sh

Purpose: builds syscall table initializer rows from `SYS_*` or `__NR_*` numeric definitions.

Important APIs/types/functions: sed patterns for direct numeric defines and `__NR_Linux + offset`, numeric sort/uniq, and awk output using `printargs` placeholders for gaps and `sys_<name>` decoder functions for known calls.

Control flow: read headers from arguments/stdin, extract syscall names/numbers, sort, emit placeholder rows until each syscall number is reached, emit the syscall row, then append 100 trailing placeholder entries after the last known syscall.

State and persistence behavior: stdout only.

Dependencies and integration points: historical architecture syscall table generation; output shape matches strace `sysent` initializer format.

Risks: parser only sees simple numeric forms and may not correctly handle aliases or complex macro arithmetic. The trailing 100 placeholders are a convention that can drift from modern table needs.

Test signals: generated syscall tables should compile and resolve known syscall numbers for the target architecture.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/syscallent.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/update-xlat.sh -->
# sources/test-tools/strace/maint/update-xlat.sh

Purpose: updates generated xlat files by re-running the command embedded in their first-line generated-by marker.

Important APIs/types/functions: help/usage parser, regex components for `maint/<script>.sh`, `"enum <name>"`, and `bundled/...h`, sed command extraction, and `eval $cmd > "$file"`.

Control flow: validate file arguments, for each file extract a recognized first-line generated-by command, skip files without a match, then execute the reconstructed command and overwrite the file.

State and persistence behavior: overwrites xlat files in place without temporary files. No backup or diff stage.

Dependencies and integration points: intended for xlat files generated by `enum2xlat.sh` and similar markers; integrates bundled Linux header updates with regenerated xlat content.

Risks: `eval` on file-derived content is powerful and assumes repository-trusted xlat headers. Direct overwrite can leave partial files on failure. Regex is narrow and misses other generation forms.

Test signals: running on generated xlat files should produce no diff when inputs are unchanged and expected diffs after bundled header updates.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/update-xlat.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/update_copyright_years.awk -->
# sources/test-tools/strace/maint/update_copyright_years.awk

Purpose: awk helper that inserts a new copyright notice after an existing copyright block.

Important APIs/types/functions: external variables `COMMENT_MARKER`, `COMMENT_MARKER_RE`, `COPYRIGHT_MARKER`, and `COPYRIGHT_NOTICE`; state machine states 0 through 3; regexes for initial copyright lines and continuations.

Control flow: detect the beginning of a copyright notice, stay in the notice/continuation block while matching lines continue, transition after the block, print the new notice once, then print all input lines. END exits with `3 - state`, allowing caller to distinguish whether insertion happened.

State and persistence behavior: streaming only; writes transformed file to stdout.

Dependencies and integration points: called by `update_copyright_years.sh` when a file lacks an existing notice for the target owner.

Risks: continuation detection is comment-prefix sensitive and may insert in the wrong place for unusual copyright layouts. Exit-code protocol is non-obvious.

Test signals: files with C, roff, and shell comment styles should get a single inserted notice after existing copyright blocks.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/update_copyright_years.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/maint/update_copyright_years.sh -->
# sources/test-tools/strace/maint/update_copyright_years.sh

Purpose: updates copyright year spans for git-tracked files based on commit history and optionally stages/commits the changes.

Important APIs/types/functions: environment defaults `COPYRIGHT_NOTICE`, `COPYRIGHT_MARKER`, `COPYRIGHT_PREFIX`, `VERBOSE`, `CALL_GIT_ADD`, `CALL_GIT_COMMIT`; functions `log`, `debug`, `print_help`, `get_comment_prefix`, and `process_file`; options `-v`, `-q`, `-a`, `-c`, `-j`, `-h`; parallel background job control.

Control flow: parse options, enumerate `git ls-files` excluding imported paths, process files in parallel up to `MAX_JOBS`. For each file, detect comment prefix, find current copyright years, derive first/last commit years with `git log`, skip up-to-date files, update existing notice or call the awk helper to add a notice, optionally `git add`, then optionally commit after all jobs finish.

State and persistence behavior: edits files in place, creates/removes temporary `.out` files, can stage and commit. Uses Git history as the source of truth for year spans.

Dependencies and integration points: maintenance script for repository headers; integrates with `update_copyright_years.awk` and Git.

Risks: concurrent background edits are safe per file but output ordering is nondeterministic. Existing notice regex may miss nonstandard forms. `COPYTIGHT_PREFIX` is misspelled in help, while variable is `COPYRIGHT_PREFIX`.

Test signals: dry runs on selected files should update only stale notices; `git diff` should show expected year-span changes and no touched ignored imported files.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/maint/update_copyright_years.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/Makefile.am -->
# sources/test-tools/strace/src/Makefile.am

Purpose: main Automake build description for the strace binary, static library, generated headers, ioctl tables, and mpers compatibility libraries.

Important APIs/types/functions: defines `bin_PROGRAMS=strace`, `libstrace.a`, include flags for build/source architecture directories and bundled headers, `libstrace_a_SOURCES`, optional stacktrace/SELinux source additions, `EXTRA_DIST`, `BUILT_SOURCES`, `CLEANFILES`, ioctl generation rules, `sys_func.h`, `sen.h`, and mpers printer/type/function generation rules.

Control flow: Automake builds `libstrace.a` from decoder/runtime sources, links `strace`, builds helper programs, generates syscall function prototypes by scanning `SYS_FUNC`, generates syscall entry names, builds ioctl sorter helpers from architecture ioctl includes, and preprocesses mpers sources to create native/m32/mx32 printer declarations/definitions and compatibility libraries when enabled.

State and persistence behavior: produces numerous generated headers and build artifacts in the build directory; distribution state is captured through the extensive `EXTRA_DIST` list of architecture-specific files and scripts.

Dependencies and integration points: central integration point for configure substitutions (`@arch@`, `@karch@`, feature flags, compiler flags), xlat `Makemodule.am`, `scno.am`, `mpers.am`, generated `maint/gen` outputs, and optional libraries libdw/libunwind/libiberty/libselinux.

Risks: high drift risk because source lists, generated headers, and `EXTRA_DIST` must be complete and ordered. Host/build/target distinction for ioctl and mpers rules is subtle. Generated files like `sys_func.h` must exist before preprocessing sources that include them.

Test signals: `autoreconf/bootstrap`, `configure`, `make`, `make distcheck`, feature-enabled builds, mpers builds, and cleanup/distclean targets are the primary validation gates.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/access.c -->
# sources/test-tools/strace/src/access.c

Purpose: syscall decoders for `access`, `faccessat`, and `faccessat2`.

Important APIs/types/functions: `decode_access`, `decode_faccessat`, `SYS_FUNC(access)`, `SYS_FUNC(faccessat)`, `SYS_FUNC(faccessat2)`, `printpath`, `print_dirfd`, `printflags`, and xlat tables `access_modes` and `faccessat_flags`.

Control flow: `access` decodes pathname and mode starting at argument 0. `faccessat` first prints `dirfd`, then reuses `decode_access` at offset 1. `faccessat2` extends `faccessat` decoding by printing argument 3 as flags.

State and persistence behavior: read-only decoder; no persistent state. It dereferences path arguments from the tracee using strace path-printing helpers.

Dependencies and integration points: included in `libstrace.a`; syscall table entries map access-family syscalls to these `SYS_FUNC`s. Xlat tables provide symbolic access and `AT_*` flag names.

Risks: `faccessat` and `faccessat2` differ only by flags; adding new access-like syscalls should preserve offset assumptions. Path decoding can fail if tracee memory is inaccessible.

Test signals: strace tests for `access`, `faccessat`, and `faccessat2` should show path, `R_OK/W_OK/X_OK/F_OK`, dirfd, and flags formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/affinity.c -->
# sources/test-tools/strace/src/affinity.c

Purpose: decodes CPU affinity masks for `sched_setaffinity` and `sched_getaffinity`.

Important APIs/types/functions: `get_cpuset_size`, `print_affinitylist`, `SYS_FUNC(sched_setaffinity)`, `SYS_FUNC(sched_getaffinity)`, `sched_getaffinity`, `next_set_bit`, `umoven_or_printaddr`, `tprint_bitset_*`, and `printpid`.

Control flow: `get_cpuset_size` lazily probes a kernel-accepted affinity mask size by calling `sched_getaffinity` with NULL until errors shift from `EINVAL`. `print_affinitylist` validates verbosity/error/address/length, copies the mask, prints set CPU indexes, and adds an ellipsis marker when user length exceeds copied size. `sched_getaffinity` prints pid/size on entry and the returned mask on exit using `tcp->u_rval` as length.

State and persistence behavior: static cached `cpuset_size` persists within the strace process. Per-call allocations are freed after printing.

Dependencies and integration points: uses Linux scheduler API behavior, generic bitset helpers, syscall enter/exit state, and current personality word size.

Risks: the probing relies on undocumented kernel behavior. Very large `len` values are bounded by probed max for copying but still affect ellipsis output. Allocation failure falls back to raw address.

Test signals: affinity syscall tests should verify empty sets, populated masks, oversized masks with more-data marker, failed `sched_getaffinity`, and nonverbose/raw address paths.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/affinity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/aio.c -->
# sources/test-tools/strace/src/aio.c

Purpose: decoders for Linux native AIO syscalls: `io_setup`, `io_destroy`, `io_submit`, `io_cancel`, `io_getevents`, and `io_pgetevents` time variants.

Important APIs/types/functions: `tprint_lio_opcode`, `print_common_flags`, `iocb_is_valid`, `print_iocb_header`, `print_iocb`, `print_iocbp`, `print_io_event`, `print_io_getevents`, xlat `aio_cmds`, optional `aio_iocb_flags`, `rwf_flags`, `pollflags`, and time/sigset printers.

Control flow: setup/destroy print context identifiers and output pointers. `io_submit` prints an array of iocb pointers and each pointed-to iocb with opcode-specific body handling for common buffer ops, vector ops, poll, or no-extra-data commands. `io_cancel` prints the iocb header on entry and result event on exit. `io_getevents` prints scalar inputs on entry and event array plus timeout/sigset on exit, temporarily clearing syscall error so entry-read timeout/sig args are decoded even on failure.

State and persistence behavior: no persistent decoder state. It reads tracee memory for iocb pointers, iocb structures, event arrays, iovecs, strings, timespecs, and sigsets.

Dependencies and integration points: relies on `<linux/aio_abi.h>` field availability configure checks, generic array printers, mpers-neutral kernel integer truncation, and architecture time32/time64 feature macros.

Risks: opcode checks use numeric values in a few spots (`aio_lio_opcode == 1`, vector opcode `8`) alongside constants, which can be brittle. Invalid user pointers or mismatched structure sizes fall back to addresses. Conditional fields must match configured kernel headers.

Test signals: AIO decoder tests should cover read/write/vector/poll iocbs, `IOCB_FLAG_RESFD`, `IOCB_FLAG_IOPRIO`, cancellation result, event arrays, time32/time64 paths, and failed calls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/aio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/alarm.c -->
# sources/test-tools/strace/src/alarm.c

Purpose: simple decoder for the `alarm` syscall.

Important APIs/types/functions: `SYS_FUNC(alarm)`, `tprints_arg_name`, and `PRINT_VAL_U`.

Control flow: prints the single `seconds` argument as an unsigned integer and returns `RVAL_DECODED`.

State and persistence behavior: none.

Dependencies and integration points: linked into `libstrace.a` and referenced by syscall tables for architectures exposing `alarm`.

Risks: minimal; value truncation to `unsigned int` mirrors the syscall argument semantics expected by the decoder.

Test signals: tracing `alarm(2)` should print `seconds=<value>` and decoded return value.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/alarm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/alpha.c -->
# sources/test-tools/strace/src/alpha.c

Purpose: Alpha-architecture-specific syscall decoders for dual-return-value identity syscalls and OSF statfs variants.

Important APIs/types/functions: guarded by `#ifdef ALPHA`; `decode_getxxid`, `SYS_FUNC(getxpid)`, `SYS_FUNC(getxuid)`, `SYS_FUNC(getxgid)`, `SYS_FUNC(osf_statfs)`, `SYS_FUNC(osf_fstatfs)`, `getrval2`, `tcp->auxstr`, and `xsprintf`.

Control flow: `decode_getxxid` runs only on syscall exit, retrieves the second return value, formats it as aux string with labels `ppid`, `euid`, or `egid`, and returns `RVAL_STR`. OSF statfs decoders print pathname/fd, buffer address, and size.

State and persistence behavior: uses a static buffer for aux output, overwritten on each call. No durable state.

Dependencies and integration points: compiled only for Alpha builds; depends on architecture support for `getrval2` and strace return-value formatting.

Risks: static aux buffer is shared within the tracer process but used synchronously for output. Non-Alpha builds compile none of this code, so coverage depends on architecture CI or cross builds.

Test signals: Alpha-specific syscall tests should verify second return value annotations and OSF statfs argument formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/alpha.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/arch_defs.h -->
# sources/test-tools/strace/src/arch_defs.h

Purpose: central fallback header for architecture-specific build-time capability macros.

Important APIs/types/functions: includes generated `arch_defs_.h` and defines defaults for `HAVE_ARCH_GETRVAL2`, old syscall families, UID16 support, personality counts/names/designators, dedicated error registers, compat capability, syscall-tampering needs, word sizes, time32/time64 availability, and timespec32 availability.

Control flow: preprocessor-only fallback chain: if an architecture file does not define a macro, this header supplies a conservative default derived from `SUPPORTED_PERSONALITIES`, `SIZEOF_LONG`, `SIZEOF_KERNEL_LONG_T`, or `__WORDSIZE`.

State and persistence behavior: no runtime state; affects conditional compilation throughout strace.

Dependencies and integration points: included by core definitions and decoders to select architecture behavior. Generated `arch_defs_.h` is supplied per build/architecture.

Risks: incorrect defaults can silently include/exclude syscall decoders or ABI handling. Personality macros must match arrays and syscall table counts elsewhere.

Test signals: cross-architecture builds, `strace -V` mpers/personality output, and time32/time64 syscall tests validate these fallbacks.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/arch_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/basic_filters.c -->
# sources/test-tools/strace/src/basic_filters.c

Purpose: implements parsing of basic syscall and numeric qualification filters used by `-e trace=...` and similar options.

Important APIs/types/functions: `personality_designators`, `qualify_syscall_separate_personality`, `qualify_syscall_number`, `qualify_syscall_regex`, `qualify_syscall_class`, `scno_by_name`, `qualify_syscall_name`, `qualify_syscall_pers`, `qualify_syscall`, `qualify_syscall_tokens`, and generic `qualify_tokens`.

Control flow: filter strings are cleared/inverted according to leading `!`, handle `none`/`all`, split comma-separated tokens, and resolve each token as number, regex, class, or syscall name across all personalities or a suffix-specific personality such as `@64`. Numeric syscalls are shuffled/validated per personality before adding to number sets.

State and persistence behavior: mutates caller-provided `number_set` arrays. It reads global syscall tables `sysent_vec`/`nsyscall_vec` and architecture personality metadata.

Dependencies and integration points: supports CLI filtering documented in `strace.1.in`; uses regex library, number-set helpers, syscall table vectors, xlat lookup, and error handling.

Risks: invalid filters terminate with help/error messages. Regex matching traverses all syscall names and can be costly but bounded by syscall table sizes. Personality suffix parsing treats unknown suffixes as fatal.

Test signals: option parsing tests for names, numbers, regexes, classes, negation, `none`, `all`, `?` suppression, and `@` personality suffixes should exercise this file.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/basic_filters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/bind.c -->
# sources/test-tools/strace/src/bind.c

Purpose: decoder for the socket `bind` syscall.

Important APIs/types/functions: `SYS_FUNC(bind)`, `printfd`, `decode_sockaddr`, and `PRINT_VAL_D`.

Control flow: prints socket fd, decodes the sockaddr pointer using the provided `addrlen`, then prints `addrlen` as a signed integer and returns `RVAL_DECODED`.

State and persistence behavior: no persistent state; reads tracee memory for sockaddr decoding.

Dependencies and integration points: integrates with generic socket address decoders and syscall table entries for networking syscalls.

Risks: invalid or short `addrlen` affects `decode_sockaddr` output. Address family-specific decoding depends on other modules.

Test signals: bind tests for IPv4, IPv6, Unix-domain, netlink, invalid pointers, and short lengths should verify formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/bind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/bjm.c -->
# sources/test-tools/strace/src/bjm.c

Purpose: decoders for module-management syscalls: `delete_module`, `init_module`, and `finit_module`.

Important APIs/types/functions: `SYS_FUNC(delete_module)`, `SYS_FUNC(init_module)`, `SYS_FUNC(finit_module)`, `printstr`, `printaddr`, `printfd`, `printflags`, and xlat tables `delete_module_flags` and `module_init_flags`.

Control flow: `delete_module` prints module name and flags. `init_module` prints raw module image address, length, and parameter string. `finit_module` prints fd, parameter string, and module init flags.

State and persistence behavior: no persistent state. Reads string arguments from tracee memory; module image bytes are intentionally not dumped.

Dependencies and integration points: uses kernel fcntl/header constants and xlat-generated flag tables. Syscall table entries map module syscalls here.

Risks: parameter strings can be inaccessible or truncated by global string limits. Flag tables must track kernel module option additions.

Test signals: module syscall decoder tests should verify flag names, fd formatting, string handling, and raw module image address output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/bjm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/block.c -->
# sources/test-tools/strace/src/block.c

Purpose: multipers-aware ioctl decoder for block-device ioctl commands.

Important APIs/types/functions: `MPERS_PRINTER_DECL(int, block_ioctl, ...)`, type aliases for `struct_blk_user_trace_setup`, `struct_blkpg_ioctl_arg`, `struct_blkpg_partition`, `print_blkpg_req`, `umove_or_printaddr`, numeric printers, pair printers, xlat `blkpg_ops`, and many `BLK*` ioctl constants.

Control flow: switch on ioctl `code`. Some commands treat `arg` as an immediate value, some decode output values only on exit, some decode input integers or integer pairs immediately, `BLKPG` reads nested partition data and prints a struct, and `BLKTRACESETUP` prints most fields on entry then appends the kernel-filled name on successful exit. Unknown commands return plain `RVAL_DECODED` for fallback handling; recognized commands return `RVAL_IOCTL_DECODED`.

State and persistence behavior: no persistent state. Reads tracee memory for ioctl argument structures and output values. Entry/exit handling for `BLKTRACESETUP` relies on strace syscall phase state.

Dependencies and integration points: part of the ioctl decoder dispatch; uses mpers type generation so structure layout matches tracee ABI, and build rules in `Makefile.am` generate printer tables for native/m32/mx32 variants.

Risks: ioctl constants and struct layouts are kernel-version and ABI sensitive. Entry-only and exit-only commands must match kernel direction semantics or output can be misleading. Nested `blkpg->data` pointer decoding can fail independently from the outer struct.

Test signals: ioctl tests for block devices should cover immediate values, integer outputs, `BLKGETSIZE64`, discard pairs, `BLKPG`, `BLKTRACESETUP` success/failure, and unknown block ioctls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/block.c -->
