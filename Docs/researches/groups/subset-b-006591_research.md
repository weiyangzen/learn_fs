# subset-b-006591 grouped research

This grouped report covers the exact source files assigned to `subset-b-006591`. Each file section is delimited for reconciliation into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_parser.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_parser.py

Purpose: Implements the Python kernel-doc source parser. It scans C source/header files for `/** ... */` kernel-doc blocks, parses DOC blocks, functions, typedefs, structs/unions, enums, variables, inline prototype documentation, tracepoints, syscalls, and `EXPORT_SYMBOL*` lines, then returns export symbols plus `KdocItem` entries for later formatting.

Important APIs/types/functions: Module regex constants define the grammar (`doc_start`, `doc_sect`, `doc_begin_func`, `export_symbol`, `type_param`). `KernelEntry` stores one in-progress documentation unit, including sections, parameter descriptions/types, declaration line numbers, warnings, prototype text, and anonymous struct tracking. `KernelDoc` owns the parser state machine, with `parse_kdoc()` as the primary API and `parse_export()` as export-only API. Core helpers include `create_parameter_list()`, `push_parameter()`, `dump_function()`, `dump_typedef()`, `dump_struct()`, `dump_enum()`, `dump_var()`, `process_proto_function()`, `process_proto_type()`, `syscall_munge()`, and `tracepoint_munge()`.

Control flow: `parse_kdoc()` opens the file, expands tabs, handles prototype continuation lines, optionally stores source text, records exported symbols while in normal state, and dispatches each line through `state_actions`. The state machine moves from `NORMAL` to `NAME`, then through `DECLARATION`, `BODY`, `SPECIAL_SECTION`, `DOCBLOCK`, or `PROTO` depending on the comment shape. Once a comment ends, prototype lines are accumulated until a function body/semicolon/macro definition is seen; declaration-specific dump routines validate identifiers, build parameter/member lists, check sections, and append a `KdocItem`.

State and persistence: Parser state is in-memory only. `KernelDoc.entries` accumulates parsed output for the current file; `export_table` is returned as a set. `KernelEntry` buffers warnings until an item is emitted so output filters can decide which warnings matter. `python_warning` is a module global that ensures the Python-version warning is emitted only once per process. No files are written by this module.

Dependencies/integration: Depends on `kdoc.c_lex.CTokenizer` and `tokenizer_set_log`, `kdoc.kdoc_re.KernRe`, `kdoc.kdoc_item.KdocItem`, and an external `config` object with logging and warning flags (`wreturn`, `wshort_desc`, `verbose`, `warning`). Transformation behavior is delegated to the injected `xforms` object, usually `CTransforms` from `xforms_lists.py`. Downstream output modules consume `KdocItem`.

Risks: The parser uses many regular-expression approximations for C, so unusual declarations, macro-heavy prototypes, nested braces, and anonymous members can be misparsed. `emit_unused_warnings()` tests `self.entry not in self.entries`, but entries contain `KdocItem`, not `KernelEntry`, so it can emit warnings from the active entry after parse failure and depends on reset timing. `dump_declaration()` calls `self.emit_message()` for an unknown declaration type, but the method is named `emit_msg()`, creating a latent error path. `process_special()` indexes `cont[i]` while trimming leading whitespace and can fail if the continuation is shorter than the previous indent. Identifier mismatch checks prevent stale documentation from being emitted but can silently drop an entry after warning.

Test signals: Exercise parser unit tests with function pointers, syscalls, tracepoints, macro functions, anonymous structs/unions, typedef functions, `DOC:` blocks, duplicate/excess sections, missing return docs, continuation macros, and `EXPORT_SYMBOL_NS`. Regression tests should compare produced `KdocItem` fields, warnings, and line numbers rather than just rendered text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_parser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_re.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_re.py

Purpose: Provides `KernRe`, a small wrapper around Python `re` that centralizes regex compilation, optional caching, match-result storage, concatenation, and common regex operations for the kernel-doc Python code.

Important APIs/types/functions: `re_cache` is the module-level pattern cache. `KernRe.__init__()` compiles or reuses a pattern. `__add__()` concatenates two `KernRe` patterns and ORs their flags. `match()`, `search()`, `finditer()`, `findall()`, `split()`, and `sub()` delegate to the compiled regex while `match()`/`search()` store `last_match`. `group()` and `groups()` read the last match.

Control flow: Construction calls `_add_regex()`, which first looks up the raw pattern string in `re_cache`, then compiles with flags if missing and stores it only when `cache=True`. Calls to `match()` or `search()` mutate `last_match`, after which callers can request groups without keeping the match object.

State and persistence: Regex cache and last match are in-memory only. The cache key is only the pattern string, not the flags, so the first cached compilation for a pattern determines the flags used by later cached construction of the same string.

Dependencies/integration: Wraps Python `re` and is used heavily by `kdoc_parser.py`, `xforms_lists.py`, and related tokenizer/parser code to make regex definitions composable and cacheable.

Risks: Cache keys ignore flags, which can produce wrong behavior if the same string is compiled with different flags and caching enabled. `group()`/`groups()` assume a successful prior match and will raise on `None`. `__add__()` assumes `other` is a `KernRe` with `cache` and `regex` attributes.

Test signals: Add tests for cache reuse, same-pattern-different-flags behavior, concatenation flags, `last_match` replacement, and failed `group()` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_re.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_yaml_file.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_yaml_file.py

Purpose: Serializes kernel-doc parser/output results into YAML test files for unit/regression tests, supporting expected `man`, `rst`, and optional raw `KdocItem` representations.

Important APIs/types/functions: `KDocTestFile.__init__()` prepares the target YAML file, validates output directory existence, imports `yaml`, and creates selected `ManFormat`/`RestFormat` renderers from `yaml_content`. `set_filter()` forwards output filters to renderers. `get_kdoc_item()` converts an object to a dict and normalizes declaration, parameter, and section start lines relative to a requested start line. `output_symbols()` converts parsed symbols into named test entries. `write()` emits YAML with block-style multiline strings.

Control flow: The caller constructs the object with config and YAML options, sets filters, calls `output_symbols()` per source file, then `write()`. For each symbol, a unique lowercase test name is derived from the symbol or file name; selected output formats are rendered via `output_symbols(fname, [arg])`, and expected data is appended to `self.tests`.

State and persistence: `self.tests` accumulates YAML test cases; `self.test_names` prevents duplicate case names. `write()` persists `{"tests": self.tests}` to `self.test_file`.

Dependencies/integration: Depends on PyYAML, `kdoc.kdoc_output.ManFormat`, and `RestFormat`. It expects symbol objects to expose `name`, `declaration_start_line`, `get("source")`, and `vars()`-compatible fields.

Risks: `__init__()` calls `sys.exit()` but does not import `sys`, so missing PyYAML or missing output directory triggers `NameError` rather than the intended exit. `get_kdoc_item()` mutates the object dictionary returned by `vars(arg)`, including nested line-number maps. `start_line` is initialized in `output_symbols()` but not advanced per symbol, so relative line normalization is fixed at 1. Reusing `expected_dict` inside the loop requires careful reset to avoid bleeding fields between symbols.

Test signals: Cover missing PyYAML/output directory behavior, duplicate symbol names, `KdocItem` line normalization, source removal from `other_stuff`, and YAML block style for multiline rendered output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_yaml_file.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/latex_fonts.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/latex_fonts.py

Purpose: Detects variable-format Noto CJK fonts visible to XeTeX that can break Linux documentation PDF builds, and returns a diagnostic message with mitigation guidance.

Important APIs/types/functions: `LatexFontChecker.__init__()` configures an environment with `XDG_CONFIG_HOME` pointing at a denylist directory and compiles a CJK font regex. `description()` returns the module docstring. `get_noto_cjk_vf_fonts()` runs `fc-list : file family variable` and extracts paths for variable Noto Sans/Sans Mono/Serif CJK fonts. `check()` formats a warning block or returns `None`.

Control flow: `check()` calls `get_noto_cjk_vf_fonts()`, indents the returned font paths, and if non-empty builds a bordered message explaining that XeTeX must hide the variable fonts or skip CJK pages. `get_noto_cjk_vf_fonts()` filters `fc-list` output to `variable=True` lines matching the CJK regex.

State and persistence: No persistence. The only state is a copy of the process environment used for the subprocess, plus the compiled regex.

Dependencies/integration: Requires the external `fc-list` command from fontconfig and imports `os`, `re`, `subprocess`, `textwrap`, and `sys`. It is intended for the PDF documentation error path, likely through a wrapper such as `tools/docs/check-variable-fonts.py`.

Risks: Missing `fc-list` raises `FileNotFoundError`, which is not caught. The regex and `fc-list` output parsing are distribution-sensitive. The `rel_file` variable in `check()` is computed but unused. `sys.exit()` is used on subprocess errors, which is appropriate for a CLI helper but awkward for library-style use.

Test signals: Mock `subprocess.run()` for empty output, variable CJK fonts, non-CJK variable fonts, and command failure. Integration tests should verify the denylist environment changes the `fc-list` view as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/latex_fonts.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/parse_data_structs.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/parse_data_structs.py

Purpose: Parses C/uAPI headers and produces ReStructuredText with Sphinx cross-references for defines, ioctl macros, enum values, typedefs, enums, and structs, optionally applying exception rules.

Important APIs/types/functions: `ParseDataStructs` owns `symbols`, `namespace`, `ignore`, `replace`, and accumulated source text. `read_exceptions()` parses `ignore`, `replace`, and `namespace` rules. `parse_file()` reads the input, strips comments/continuations, stores symbol references through `store_type()`, and applies exceptions. `gen_output()` escapes source text and substitutes references. `gen_toc()` builds a categorized TOC. `write_output()` writes the final rst file.

Control flow: `parse_file()` stores each original line indented in `self.data`, folds backslash continuations and multi-line comments, then detects ioctl defines, generic defines, typedefs, enum starts/member values, and struct starts. `apply_exceptions()` removes ignored symbols and rewrites replacements to explicit Sphinx references. `gen_output()` escapes special ReST characters before replacing escaped symbol occurrences using delimiter-aware regexes.

State and persistence: All parse state is in memory until `write_output()` writes the ReST output. `self.symbols` maps each type category to `symbol -> (replacement, line)`. `self.data` contains the indented source body. Exception rules persist only on the parser instance.

Dependencies/integration: Uses only Python stdlib (`os`, `re`, `sys`) and emits Sphinx C-domain/ref markup consumed by kernel documentation builds. The exception file syntax is part of its integration contract with media/uAPI docs.

Risks: `apply_exceptions()` references `name` in error/warning messages but `name` is local to `read_exceptions()`, causing a `NameError` on invalid type or missing replacement target. C parsing is regex-based and will miss complex typedefs, declarations split in unexpected ways, or macros hiding types. `line.endswith(r"\\")` checks for two backslashes, which may not match intended single continuation handling. Replacement after global escaping can still create false positives/negatives around unusual delimiters.

Test signals: Use header fixtures with ioctl macros, guarded comments, multiline macros, enums with explicit assignments, typedefs, anonymous and named structs, namespaces, ignore/replace rules, invalid exception lines, and TOC generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/parse_data_structs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/python_version.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/python_version.py

Purpose: Checks whether the running Python meets a minimum version, discovers newer `python3.x` binaries on `PATH`, optionally prints alternatives, and can re-exec the current script under a newer interpreter.

Important APIs/types/functions: `PythonVersion.parse_version()` and `ver_str()` convert version strings/tuples. `cmd_print()` shell-quotes command lines with wrapping. `get_python_version()` executes `<cmd> --version`. `find_python()` scans PATH for `python3.[0-9]` and `python3.[0-9][0-9]`. `check_python()` is the main policy API.

Control flow: `check_python()` returns immediately when `sys.version_info[:3]` satisfies `min_version`. Otherwise it discovers candidates, optionally prints commands, optionally exits, or calls `os.execv()` with the newest candidate and the current script path plus original arguments.

State and persistence: Stateless except for subprocess execution and possible process replacement. No files are written.

Dependencies/integration: Uses stdlib `os`, `re`, `subprocess`, `shlex`, `sys`, `glob`, and `textwrap.indent`. Intended for scripts that need newer Python during documentation builds or tooling execution.

Risks: `get_python_version()` only parses `stdout`, but some Python versions historically printed version to `stderr`; those would be treated as `(0,0,0)`. PATH scanning can include duplicate symlinked interpreters. `os.execv()` failure exits the current script. `find_python()` compares tuples directly, so unusual version tuple lengths can affect ordering.

Test signals: Mock subprocess and PATH scanning for versions below/above minimum, stdout vs stderr version output, `bail_out` with `success_on_error`, alternatives printing, and failed `execv()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/python_version.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/xforms_lists.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/xforms_lists.py

Purpose: Defines parser transformations that normalize kernel C declarations before kernel-doc parsing, removing attributes and rewriting common declaration macros into C-like declarations.

Important APIs/types/functions: `CTransforms` contains `struct_xforms`, `function_xforms`, `var_xforms`, and `xforms`. `apply(xforms_type, source)` runs the appropriate transformation sequence over a string or `CTokenizer`.

Control flow: The transform lists are ordered. `CMatch` substitutions run token-aware rewrites for common kernel macros/attributes; `KernRe` entries force conversion to string and apply plain regex replacements. `apply()` returns the transformed source string or the original source for unknown transform classes.

State and persistence: Class-level transformation tables are static. No per-instance persistent state beyond the instance itself.

Dependencies/integration: Depends on `kdoc.kdoc_re.KernRe` and `kdoc.c_lex.CMatch`/`CTokenizer`. It is injected into `KernelDoc` and used by `dump_struct()`, `dump_function()`, and `dump_var()`.

Risks: Ordering is semantically important; placing string regex transforms too early loses tokenizer advantages. Macro rewrites are necessarily incomplete and must track kernel declaration patterns. `CMatch` capture numbering must match replacement strings; changes in tokenizer behavior can break many parser cases. Attribute removal can hide meaningful type information if a new macro is not just annotation.

Test signals: Fixture declarations should cover cacheline/alignment attributes, bitmap/kfifo/hashtable/flex-array macros, struct_group variants, syscall/function annotations, `LIST_HEAD`, comments, and `_noprof` name normalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/xforms_lists.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/unittest_helper.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/unittest_helper.py

Purpose: Provides a custom Python unittest runner with concise colored summaries, verbosity control, failfast, regex method filtering via `-k`, environment injection, and optional detailed normal unittest output.

Important APIs/types/functions: `Summary` extends `unittest.TestResult` and records hierarchical module/class/method status. `flatten_suite()` converts nested suites into a flat list. `TestUnits.parse_args()` builds the CLI. `TestUnits.run()` loads/discovers/filter/runs tests. `run_unittest(fname)` is the simple entry point for test modules.

Control flow: `TestUnits.run()` parses args if needed, validates caller file or suite, computes verbosity, patches `os.environ`, discovers tests from the caller file unless a suite is provided, flattens and optionally filters by regex, chooses `Summary` for low verbosity or default unittest output for verbose mode, runs the suite, prints the custom summary, and exits with inverted success status.

State and persistence: Runtime-only state. Environment changes are applied through `patch.dict()` and stopped via `atexit`. `Summary.test_results` and `max_name_length` are per-run.

Dependencies/integration: Uses stdlib `argparse`, `atexit`, `os`, `re`, `unittest`, `sys`, and `unittest.mock.patch`. Intended for kernel Python unit test files under `tools/unittests`.

Risks: `Summary._record_test()` assumes `startTest()` already initialized module/class buckets; unusual `TestResult` calls could break that. For `verbose >= 2`, monkey-patching `unittest.TextTestRunner(verbosity=verbose).run` on a temporary instance has no effect on the runner later created, so that branch likely does not do what it appears to intend. `sys.exit()` in the runner limits embedding in larger test harnesses. Filtering by method name only may surprise users expecting class/module matching.

Test signals: Run sample passing/failing/error/skipped tests under quiet, default, verbose, failfast, invalid `-k`, custom suite, and custom environment. Verify exit codes and printed summaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/unittest_helper.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/rbtree.c -->
# sources/distributed-fs/ceph-client/tools/lib/rbtree.c

Purpose: User-space tools copy of Linux red-black tree implementation, including insertion, deletion/rebalancing, replacement, ordered traversal, and postorder traversal for `struct rb_root`/`struct rb_node`.

Important APIs/types/functions: Public functions include `rb_insert_color()`, `rb_erase()`, `__rb_insert_augmented()`, `__rb_erase_color()`, `rb_first()`, `rb_last()`, `rb_next()`, `rb_prev()`, `rb_replace_node()`, `rb_first_postorder()`, and `rb_next_postorder()`. Internal helpers include `rb_set_black()`, `rb_red_parent()`, `__rb_rotate_set_parents()`, `__rb_insert()`, and `____rb_erase_color()`.

Control flow: Insert fixes red-red violations using standard red-black cases: root recolor, uncle recolor, parent rotation, and grandparent rotation, mirrored for left/right. Delete delegates structural removal to `__rb_erase_augmented()` and then rebalances black-height violations through sibling cases. Traversal walks left/right extrema or climbs parent pointers. Replacement copies victim metadata and rewires children/root.

State and persistence: Mutates caller-owned tree nodes in memory. Parent and color are packed in `__rb_parent_color`; child pointers are updated with `WRITE_ONCE()` to support lockless lookup constraints described in comments. No allocation or persistence occurs.

Dependencies/integration: Includes `<linux/rbtree_augmented.h>` and `<linux/export.h>`. Augmented users supply rotate callbacks; non-augmented paths use dummy callbacks expected to optimize away.

Risks: Correctness depends on callers linking nodes in sorted order before insertion and providing external locking for updates. Lockless lookups are only guaranteed to terminate and return valid found nodes; they can miss nodes during mutation. Parent-pointer loops are not protected for lockless users. Misusing `rb_replace_node()` with a node already in a tree corrupts structure.

Test signals: Validate tree invariants after randomized insert/delete, in-order traversal, reverse traversal, postorder traversal, replacement, augmented callback invocation, empty tree behavior, and concurrent-reader assumptions under sanitizer or stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/rbtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/slab.c -->
# sources/distributed-fs/ceph-client/tools/lib/slab.c

Purpose: Provides small user-space implementations of kernel allocation helpers `kmalloc()`, `kfree()`, and `kmalloc_array()` for tools code.

Important APIs/types/functions: Globals `kmalloc_nr_allocated` and `kmalloc_verbose` track allocation count and optional debug printing. `kmalloc(size, gfp)` uses `malloc()`. `kmalloc_array(n, size, gfp)` uses `calloc()`. `kfree(p)` releases with `free()`.

Control flow: Allocation returns `NULL` unless `gfp` includes `__GFP_DIRECT_RECLAIM`. Successful allocation increments `kmalloc_nr_allocated`; `kfree()` decrements for non-NULL pointers. `__GFP_ZERO` triggers explicit zeroing after allocation, although `calloc()` already zeroes arrays.

State and persistence: Allocation count is process-global and updated with userspace RCU atomics (`uatomic_inc/dec`). Allocated memory belongs to callers and must be freed with `kfree()`.

Dependencies/integration: Includes `<urcu/uatomic.h>`, `<linux/slab.h>`, `<linux/gfp.h>`, libc `malloc/calloc/free`, and `stdio/string` for verbose output and zeroing.

Risks: `kmalloc()` calls `memset(ret, 0, size)` without checking `ret`, so `__GFP_ZERO` plus allocation failure dereferences `NULL`. `kmalloc_array()` does not guard integer overflow in `n * size` before the redundant `memset()`. Allocation count increments even if `malloc()`/`calloc()` returns `NULL`. Only `__GFP_DIRECT_RECLAIM` allocation mode is accepted.

Test signals: Test allocation/free count under success and failure injection, `__GFP_ZERO`, missing reclaim flag, null free, `kmalloc_array()` overflow-sized inputs, and verbose output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/slab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/str_error_r.c -->
# sources/distributed-fs/ceph-client/tools/lib/str_error_r.c

Purpose: Provides `str_error_r()`, a portable wrapper with GNU-like return semantics that always returns the caller-provided buffer while using XSI `strerror_r()`.

Important APIs/types/functions: `char *str_error_r(int errnum, char *buf, size_t buflen)` calls `strerror_r()`, formats an internal-error message into `buf` if it fails, and returns `buf`.

Control flow: Undefines `_GNU_SOURCE` before including string headers to force XSI behavior. On success, the platform fills `buf`; on nonzero return, `snprintf()` writes a diagnostic.

State and persistence: Stateless; caller owns the buffer.

Dependencies/integration: Includes libc `string.h`, `stdio.h`, and `<linux/string.h>`. Used by tools code expecting GNU `strerror_r()`-style string return while remaining compatible with musl and other libc implementations.

Risks: If the build environment still exposes GNU semantics despite `_GNU_SOURCE` handling, the return type expectations can conflict. Very small buffers truncate diagnostics. Passing a null buffer or zero length is caller error.

Test signals: Build and run on glibc and musl, test known/unknown errno values, tiny buffer sizes, and callers that immediately print the returned pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/str_error_r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/string.c -->
# sources/distributed-fs/ceph-client/tools/lib/string.c

Purpose: Supplies user-space copies or fallbacks for kernel string/memory helpers needed by tools code.

Important APIs/types/functions: `memdup()` duplicates a memory region. `strtobool()` parses common boolean strings. Weak `strlcpy()` provides BSD-compatible bounded copy if libc lacks it. `skip_spaces()`, `strim()`, `remove_spaces()`, and `strreplace()` manipulate strings in place. `memchr_inv()` finds the first byte not equal to a value, using `check_bytes8()` and 64-bit scanning.

Control flow: Most functions are linear scans over strings/buffers. `memchr_inv()` checks short buffers byte-by-byte, aligns to 8 bytes, scans 64-bit words for any mismatch, then checks the suffix.

State and persistence: Stateless except mutations to caller-provided strings and allocated buffer from `memdup()`.

Dependencies/integration: Includes libc `stdlib/string/errno` and Linux headers for `bool`, `u8/u64`, ctype, and weak symbol attributes. Intended to satisfy shared tools library dependencies.

Risks: `memchr_inv()` casts possibly unaligned memory to `u64 *` after manual alignment, which assumes alignment calculations and architecture behavior are correct. `remove_spaces()` removes only ASCII space, not all whitespace. `strtobool()` inspects `s[1]` for `o/O`, so one-character `"o"` safely reads NUL but returns invalid. `strim()` mutates input and should not receive string literals.

Test signals: Exercise boolean strings, zero-size copy, weak override behavior, whitespace trimming, all-space strings, `memchr_inv()` on aligned/unaligned buffers, short buffers, and not-found cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/Makefile -->
# sources/distributed-fs/ceph-client/tools/lib/subcmd/Makefile

Purpose: Builds and installs `libsubcmd.a`, the common subcommand/option/pager/process helper library used by Linux tools.

Important APIs/types/functions: Targets include `all`, `$(SUBCMD_IN)`, `$(LIBFILE)`, `install_lib`, `install_headers`, `install`, `clean`, and `FORCE`. Variables configure `srctree`, compiler tools, `CFLAGS`, `OUTPUT`, `LIBFILE`, header install list, `prefix`, and `libdir`.

Control flow: The Makefile derives `srctree` when unset, includes kernel tools build helpers, builds `libsubcmd-in.o` via recursive `$(MAKE) $(build)=libsubcmd`, archives it into `libsubcmd.a`, and installs library/header files under `DESTDIR`/`prefix`.

State and persistence: Produces object files and `$(OUTPUT)libsubcmd.a`; install targets copy artifacts into the configured destination. `clean` removes archive and object/cmd/dependency files.

Dependencies/integration: Includes `../../scripts/Makefile.include`, `../../scripts/utilities.mak`, and `$(srctree)/tools/build/Makefile.include`. Requires kernel tools headers under `tools/include`.

Risks: `find ... | xargs $(RM)` can invoke `rm` with no arguments depending on xargs behavior; usually harmless with `rm -f`. Header install list must stay synchronized with exported API. `WERROR` defaults to enabled unless explicitly `0`, which can break builds on newer compilers.

Test signals: Build with default and custom `OUTPUT`, `DEBUG`, `WERROR=0`, `LP64`, `DESTDIR`, and cross-compile variables; verify archive contents and installed headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/exec-cmd.c -->
# sources/distributed-fs/ceph-client/tools/lib/subcmd/exec-cmd.c

Purpose: Manages subcommand executable path configuration and provides wrappers to execute external subcommands through a configured main executable name.

Important APIs/types/functions: `exec_cmd_init()` initializes `subcmd_config` and `PREFIX`. `system_path()`, `extract_argv0_path()`, `set_argv_exec_path()`, `get_argv_exec_path()`, and `setup_path()` resolve and export executable search paths. `execv_cmd()` and `execl_cmd()` execute the configured command with added argv[0].

Control flow: Initialization stores config and environment. Path resolution prefers explicit `argv_exec_path`, then the configured environment variable, then `prefix/exec_path`. `setup_path()` prepends the exec path and the path of `argv0` to `PATH`. Execution builds a new argv where element 0 is `subcmd_config.exec_name`, then calls `execvp()`.

State and persistence: Static `argv_exec_path` and `argv0_path` persist for the process; environment variables `PREFIX`, `PATH`, and configured exec-path env are mutated.

Dependencies/integration: Depends on `subcmd-config.h`, `subcmd-util.h`, `linux/string.h` for `strlcpy`, and POSIX `getcwd`, `stat`, `execvp`, `setenv`. Used by subcmd tools to locate built-in and external command helpers.

Risks: `prepare_exec_cmd()` does not check `malloc()` failure. `extract_argv0_path()` uses `strndup(argv0, slash - argv0)`, yielding an empty string for `/cmd` paths and storing static allocated memory never freed. `execl_cmd()` caps arguments at `MAX_ARGS` and returns an error if exceeded. Environment mutation affects all later child processes.

Test signals: Verify relative/absolute exec paths, `PWD` symlink preservation, PATH prepending, environment override precedence, `execl_cmd()` overflow, and failed `execvp()` return path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/exec-cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/exec-cmd.h -->
# sources/distributed-fs/ceph-client/tools/lib/subcmd/exec-cmd.h

Purpose: Declares the public path setup and subcommand execution API implemented by `exec-cmd.c`.

Important APIs/types/functions: Exports `exec_cmd_init()`, `set_argv_exec_path()`, `extract_argv0_path()`, `setup_path()`, `execv_cmd()`, `execl_cmd()`, `get_argv_exec_path()`, and `system_path()`.

Control flow: Header-only declarations; callers initialize config, optionally extract argv0 path and override exec path, update `PATH`, then execute subcommands.

State and persistence: Documents ownership for `get_argv_exec_path()` and `system_path()` as malloc-returning APIs that callers must free. Other state lives in the implementation.

Dependencies/integration: Included by tools using libsubcmd. Guarded by `__SUBCMD_EXEC_CMD_H`.

Risks: Callers must respect NULL-terminated argv for `execv_cmd()` and free returned strings. The header does not enforce initialization before use.

Test signals: Compile tests should include the header from C and C++-like strict contexts where applicable; API tests should validate ownership and initialization ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/exec-cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/help.c -->
# sources/distributed-fs/ceph-client/tools/lib/subcmd/help.c

Purpose: Discovers executable subcommands in configured directories and prints column-formatted command lists for help output.

Important APIs/types/functions: `add_cmdname()`, `clean_cmdnames()`, `cmdname_compare()`, `uniq()`, `exclude_cmds()`, `load_command_list()`, `list_commands()`, and `is_in_cmdlist()`. Internal helpers determine terminal dimensions, executable status, filename extensions, and directory scanning.

Control flow: `load_command_list()` scans the preferred exec path into `main_cmds`, scans each PATH entry into `other_cmds`, sorts/deduplicates both lists, and excludes main commands from other commands. `list_commands()` computes the longest command name and prints separate sections for preferred and other commands using terminal-width-aware columns.

State and persistence: `struct cmdnames` arrays are caller-owned and dynamically grown; `clean_cmdnames()` frees entries and resets counters. No persistent files.

Dependencies/integration: Uses `exec-cmd.c` for `get_argv_exec_path()`, `subcmd-util.h` allocation helpers, Linux `strstarts`, POSIX directory/stat APIs, and terminal dimension APIs.

Risks: `list_commands_in_dir()` appends each directory entry to `buf` without resetting it to the directory prefix, so repeated entries can build an invalid path unless `astrcat()` behavior is externally countered; this is a notable path-construction risk. `is_executable()` only checks user execute bit (`S_IXUSR`), not group/other or access rights. `exclude_cmds()` assumes sorted input. Memory allocation failure in `add_cmdname()` silently skips that command.

Test signals: Use temporary directories with executable/non-executable files, `.exe` suffixes, duplicate commands, PATH exclusions, terminal width variations, and empty command sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/help.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/help.h -->
# sources/distributed-fs/ceph-client/tools/lib/subcmd/help.h

Purpose: Defines command-name storage structures and help/listing API declarations for libsubcmd.

Important APIs/types/functions: `struct cmdnames` contains allocation/count plus an array of flexible-array `struct cmdname` entries. `mput_char()` prints repeated characters. Declares command-list lifecycle, sorting, filtering, membership, loading, and listing functions.

Control flow: Header declarations support callers creating zero-initialized `cmdnames`, populating via `load_command_list()` or `add_cmdname()`, sorting/filtering, printing, and cleaning.

State and persistence: Structures store heap pointers managed by `help.c`; no persistence.

Dependencies/integration: Includes `sys/types.h` and `stdio.h`, and is installed as a libsubcmd public header.

Risks: Callers must initialize `struct cmdnames` to zero and later call `clean_cmdnames()`. `mput_char()` is inline and writes directly to stdout.

Test signals: Compile API usage with static initializers and dynamic lists; verify ABI expectations for flexible array allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/help.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/pager.c -->
# sources/distributed-fs/ceph-client/tools/lib/subcmd/pager.c

Purpose: Starts and manages a pager process for command help/output, redirecting stdout/stderr through the pager and handling cleanup on exit/signals.

Important APIs/types/functions: `pager_init()`, `force_pager()`, `setup_pager()`, `pager_in_use()`, and `pager_get_columns()`. Internal state includes `spawned_pager`, `pager_columns`, `forced_pager`, `pager_argv`, and `pager_process`.

Control flow: `setup_pager()` chooses a pager from forced value, configured env, `PAGER`, `/usr/bin/pager`, `/usr/bin/less`, or `cat`; skips paging for non-tty output unless forced; starts a child with `start_command()`, redirects stdout and tty stderr to the pipe, installs common signal handlers, and registers `atexit()`. `wait_for_pager()` closes output FDs and waits for the child.

State and persistence: Process-global pager state and environment `LESS` set in the child preexec callback. Parent FDs are mutated by `dup2()`.

Dependencies/integration: Uses `run-command.c` for child process handling, `sigchain.c` for signal chaining, `subcmd-config.h` for pager env name, and POSIX select/ioctl/signal APIs.

Risks: Once stdout/stderr are redirected, later code must tolerate closed descriptors during pager shutdown. `pager_preexec()` blocks in `select()` until input is available. Signal handling assumes `wait_for_pager()` is safe enough in that context. Pager choice uses shell `sh -c`, so pager strings come from environment and are shell-interpreted by design.

Test signals: Run with tty/non-tty output, forced pager, `PAGER=cat`, missing pager binaries, signal interruption, and COLUMNS/window-size behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/pager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/pager.h -->
# sources/distributed-fs/ceph-client/tools/lib/subcmd/pager.h

Purpose: Public header for libsubcmd pager setup and query APIs.

Important APIs/types/functions: Declares `pager_init()`, `setup_pager()`, `pager_in_use()`, `pager_get_columns()`, and `force_pager()`.

Control flow: Callers initialize the pager environment variable name, optionally force a pager, call `setup_pager()` before output, and query status/columns as needed.

State and persistence: State is implementation-private in `pager.c`.

Dependencies/integration: Guarded by `__SUBCMD_PAGER_H`; installed with libsubcmd headers.

Risks: API does not expose shutdown; cleanup is atexit/signal based. Call ordering matters because `pager_init()` sets the environment variable key used later.

Test signals: Compile against header and verify behavior through `pager.c` integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/pager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/parse-options.c -->
# sources/distributed-fs/ceph-client/tools/lib/subcmd/parse-options.c

Purpose: Implements libsubcmd command-line option parsing, usage rendering, internal help/list options, option negation/abbreviation, exclusive options, callbacks, and typed value storage.

Important APIs/types/functions: Public APIs include `parse_options()`, `parse_options_subcommand()`, `usage_with_options()`, `usage_with_options_msg()`, `parse_options_usage()`, `parse_opt_verbosity_cb()`, `set_option_flag()`, and `set_option_nobuild()`. Internal helpers include `get_arg()`, `get_value()`, `parse_short_opt()`, `parse_long_opt()`, `parse_options_step()`, `parse_options_end()`, `print_option_help()`, and `usage_with_options_internal()`.

Control flow: Parsing initializes a context, scans argv, handles short clusters and long options, processes special options such as `--help`, `--help-all`, `--list-opts`, and `--list-cmds`, stores parsed values according to option type, preserves or stops at non-options depending on flags, and compacts remaining args back into argv. Usage output sorts option groups and may page output.

State and persistence: Global `error_buf` holds formatted error text until usage output frees it. Parsed option values are written directly through pointers in `struct option`. `ctx->out` aliases argv for in-place compaction.

Dependencies/integration: Uses `parse-options.h`, `subcmd-util.h`, `subcmd-config.h`, `pager.h`, Linux type/string/compiler helpers, libc conversion functions, and GNU `strcasestr`/`vasprintf`.

Risks: Many error paths call `exit(129/130)`, so library users must expect process termination. Long-option abbreviation and negation are complex and can surprise users or introduce ambiguity. `parse_options_subcommand()` allocates a generated usage string and stores it in `usagestr[0]` without freeing in normal return. Numeric parsing uses `strtol/strtoul/strtoull` without explicit range/errno checks. The `die()` message for impossible option types is intentionally abrupt.

Test signals: Cover all option types, optional args, last-arg default, no-negation, hidden/disabled/nobuild, exclusive conflict, abbreviated long options, `--no-*`, short option clusters, keep-unknown, stop-at-non-option, usage formatting, and list modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/parse-options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/parse-options.h -->
# sources/distributed-fs/ceph-client/tools/lib/subcmd/parse-options.h

Purpose: Defines libsubcmd option-parser data structures, flags, constructor macros, return codes, and public parser/usage APIs.

Important APIs/types/functions: `enum parse_opt_type`, `enum parse_opt_flags`, `enum parse_opt_option_flags`, `struct option`, `parse_opt_cb`, and `struct parse_opt_ctx_t` define the parser contract. Macros such as `OPT_BOOLEAN`, `OPT_STRING`, `OPT_INTEGER`, `OPT_U64`, `OPT_CALLBACK`, `OPT_GROUP`, and `OPT_END` build option arrays with type checking via `check_vtype`.

Control flow: Header-only setup; callers declare an option array terminated by `OPT_END()` or `OPT_PARENT()`, then pass it to `parse_options()`/`parse_options_subcommand()`.

State and persistence: Parser writes to caller-provided storage pointed to by `struct option.value` and optional `set`. No persistent state in the header.

Dependencies/integration: Includes `<linux/kernel.h>`, `<stdbool.h>`, `<stdint.h>`, and depends on compiler support for GNU `typeof`/`__builtin_types_compatible_p`.

Risks: The macro `OPT_CALLBACK_DEFAULT_NOOPT` initializes `.arg`, but `struct option` has `.argh`; if used, this is a compile-time bug. Type-checking macros are GCC/Clang-specific. Callers must ensure help strings are non-NULL except for end markers and that option arrays are terminated.

Test signals: Compile representative option arrays using every macro, especially callback/default variants, under GCC and Clang with warnings as errors. Runtime tests belong with `parse-options.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/parse-options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/run-command.c -->
# sources/distributed-fs/ceph-client/tools/lib/subcmd/run-command.c

Purpose: Provides child process execution helpers with optional stdin/stdout/stderr pipes, environment/working-directory setup, exec-subcmd support, and blocking/nonblocking finish checks.

Important APIs/types/functions: Public APIs are `start_command()`, `check_if_command_finished()`, `finish_command()`, `run_command()`, and `run_command_v_opt()`. Internal helpers include `close_pair()`, `dup_devnull()`, `wait_or_whine()`, and `prepare_run_command_v_opt()`.

Control flow: `start_command()` allocates requested pipes, forks, sets up child stdio, changes directory, applies environment entries or unsets variables, runs optional preexec/no-exec callback, then calls `execv_cmd()` or `execvp()`. The parent closes opposite pipe ends and returns. `finish_command()` waits and normalizes exit status to 0 or negative error/code. Linux `check_if_command_finished()` reads `/proc/<pid>/status` to avoid reaping early.

State and persistence: Mutates `struct child_process` fields (`pid`, FDs, `finished`, `finish_result`). Child process state is external to the library. No files are persisted.

Dependencies/integration: Uses POSIX fork/pipe/dup2/exec/wait, `/proc` on Linux, `str_error_r()`, `exec-cmd.c`, and `subcmd-util.h`.

Risks: Pipe/file descriptor ownership is subtle; passed FDs are closed even on some error paths as documented. `dup_devnull()` does not check `open()` failure. Environment handling mutates the child process before exec. Nonblocking finish on Linux relies on `/proc`, so behavior differs across platforms. Exit code 127 is mapped to exec failure, which may conflate real child exit 127.

Test signals: Test FD redirection combinations, no-stdin/stdout/stderr, stdout-to-stderr, working-directory failure, environment set/unset, preexec/no-exec callbacks, exec failure, signal exit, nonblocking status, and repeated `finish_command()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/run-command.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/run-command.h -->
# sources/distributed-fs/ceph-client/tools/lib/subcmd/run-command.h

Purpose: Declares child process execution data structures, error codes, option flags, and APIs for libsubcmd.

Important APIs/types/functions: Error enum values start at `ERR_RUN_COMMAND_FORK`; `IS_RUN_COMMAND_ERR()` identifies normalized library errors. `struct child_process` describes argv, pid, FDs, dir, env, finish status, behavior bitfields, preexec callback, and no-exec callback. Declares run/start/finish/check APIs plus `RUN_COMMAND_*` flags.

Control flow: Callers zero-initialize `struct child_process`, fill fields, call `start_command()` then manage returned FDs and `finish_command()`, or use `run_command()`/`run_command_v_opt()` for synchronous execution.

State and persistence: State is caller-owned in `struct child_process`; implementation updates fields.

Dependencies/integration: Includes `<unistd.h>` for `pid_t` and POSIX types. Used by pager and other tools.

Risks: FD semantics require careful caller cleanup after `start_command()`. Bitfields encode booleans but do not validate incompatible combinations. Header comments are the primary ownership contract.

Test signals: Compile and exercise all documented FD modes through `run-command.c` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/run-command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/sigchain.c -->
# sources/distributed-fs/ceph-client/tools/lib/subcmd/sigchain.c

Purpose: Maintains a small stack of previous signal handlers so libsubcmd can push common handlers and later restore/chain them.

Important APIs/types/functions: `sigchain_pop()` restores the previous handler for one signal. `sigchain_push_common()` pushes a handler for `SIGINT`, `SIGHUP`, `SIGTERM`, `SIGQUIT`, and `SIGPIPE`. Internal `sigchain_push()` stores previous handlers in a dynamically grown array per signal.

Control flow: Push validates signal range, grows the per-signal stack, installs the new handler with `signal()`, stores the old handler, and increments count. Pop restores the most recent saved handler and decrements.

State and persistence: Static `signals[SIGCHAIN_MAX_SIGNALS]` stores handler stacks for the process lifetime. No persistence.

Dependencies/integration: Uses `signal.h` and `subcmd-util.h` allocation/die helpers. Pager uses it to wait for the pager then re-raise signals.

Risks: Limited to signal numbers 1-31. Uses `signal()` rather than `sigaction()`, so semantics are platform-dependent. Failed `signal()` after `ALLOC_GROW()` leaves allocated capacity. Not thread-safe.

Test signals: Push/pop multiple handlers per signal, invalid signal handling, common signal coverage, and signal delivery integration with pager.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/sigchain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/sigchain.h -->
# sources/distributed-fs/ceph-client/tools/lib/subcmd/sigchain.h

Purpose: Public declarations for libsubcmd signal handler chaining.

Important APIs/types/functions: Defines `typedef void (*sigchain_fun)(int)` and declares `sigchain_pop()` and `sigchain_push_common()`.

Control flow: Callers push one handler across common termination signals and pop individual handlers when re-raising or restoring.

State and persistence: Implementation stores signal stacks statically.

Dependencies/integration: Used by pager cleanup and any libsubcmd user needing stacked signal handlers.

Risks: The header exposes no push for arbitrary signals; only common push plus single-signal pop. Callers must not assume thread safety.

Test signals: Compile and behavioral tests in `sigchain.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/sigchain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/subcmd-config.c -->
# sources/distributed-fs/ceph-client/tools/lib/subcmd/subcmd-config.c

Purpose: Defines the global `subcmd_config` object shared by libsubcmd modules.

Important APIs/types/functions: `struct subcmd_config subcmd_config` is initialized with sentinel string `SUBCMD_HAS_NOT_BEEN_INITIALIZED` for exec name, prefix, exec path, exec path environment, and pager environment.

Control flow: No functions. Initialization occurs at load time; `exec_cmd_init()` and `pager_init()` later populate fields.

State and persistence: Process-global mutable configuration.

Dependencies/integration: Includes `subcmd-config.h`; used by exec, pager, parse-options, and help modules.

Risks: Consumers can use sentinel values if initialization is skipped, potentially creating invalid environment lookups or paths. No locking for concurrent mutation.

Test signals: Verify default values, initialization through exec/pager APIs, and behavior when uninitialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/subcmd-config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/subcmd-config.h -->
# sources/distributed-fs/ceph-client/tools/lib/subcmd/subcmd-config.h

Purpose: Defines the shared libsubcmd configuration structure and extern declaration.

Important APIs/types/functions: `struct subcmd_config` contains `exec_name`, `prefix`, `exec_path`, `exec_path_env`, and `pager_env`. `extern struct subcmd_config subcmd_config` exposes the global instance.

Control flow: Header-only configuration contract.

State and persistence: Describes process-global mutable strings owned by callers or static literals.

Dependencies/integration: Included by libsubcmd implementation files and tools that need direct config access.

Risks: Direct global access makes initialization ordering and thread safety caller responsibilities. The include guard uses `__PERF_SUBCMD_CONFIG_H`, reflecting perf heritage.

Test signals: Compile users and initialization tests through `subcmd-config.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/subcmd-config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/subcmd-util.h -->
# sources/distributed-fs/ceph-client/tools/lib/subcmd/subcmd-util.h

Purpose: Provides small allocation, reporting, fatal-error, and string-append helpers for libsubcmd.

Important APIs/types/functions: `report()` formats prefixed messages. `die()` prints fatal errors and exits 128. `zfree(ptr)` frees a pointer and sets it to NULL. `alloc_nr()` and `ALLOC_GROW()` implement dynamic array growth. `xrealloc()` wraps `realloc()` with fatal OOM. `astrcatf()` and `astrcat()` append formatted/plain text to heap strings.

Control flow: Allocation helpers grow buffers as needed and terminate on unrecoverable allocation/formatting failures. String append helpers allocate a new combined string with `asprintf()`, free the old string, and store the new pointer.

State and persistence: Mutates caller pointers and exits the process on fatal paths. No persistent files.

Dependencies/integration: Includes stdarg/stdlib/stdio and Linux compiler attributes. Used across libsubcmd.

Risks: `zfree(ptr)` evaluates `ptr` as pointer-to-pointer and is macro-based; misuse can double-free or assign through invalid pointers. `ALLOC_GROW()` warns not to pass side-effect expressions. Helpers rely on GNU `asprintf()`. Fatal exit behavior may not suit embedded library consumers.

Test signals: Exercise growth boundaries, append from NULL/non-NULL, OOM/failure injection where practical, and macro misuse coverage via compile tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/subcmd/subcmd-util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/symbol/Makefile -->
# sources/distributed-fs/ceph-client/tools/lib/symbol/Makefile

Purpose: Builds and installs `libsymbol.a`, containing symbol parsing helpers such as kallsyms support.

Important APIs/types/functions: Targets include `all`, `$(SYMBOL_IN)`, `$(LIBFILE)`, `install_lib`, `install_headers`, `install`, and `clean`. Variables configure compiler/archive tools, `CFLAGS`, `OUTPUT`, `LIBFILE`, header install path, `prefix`, and `libdir`.

Control flow: Determines `srctree`, includes tools make helpers, builds `libsymbol-in.o` recursively via `$(build)=libsymbol`, archives `libsymbol.a`, installs archive and `kallsyms.h`.

State and persistence: Produces `$(OUTPUT)libsymbol.a` and intermediate objects; install copies archive/header to configured destination. `clean` removes outputs and object metadata.

Dependencies/integration: Includes tools build and scripts makefiles; requires `tools/lib`, `tools/include`, and generated fixdep support.

Risks: `CFLAGS += -D_FORTIFY_SOURCE` omits an explicit level, which may behave differently than common `-D_FORTIFY_SOURCE=2`. `WERROR` can break on compiler warning churn. Header install list must stay aligned with public API.

Test signals: Build/install under default/custom `OUTPUT`, `DEBUG=0`, `WERROR=0`, LP64/non-LP64, and DESTDIR packaging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/symbol/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/symbol/kallsyms.c -->
# sources/distributed-fs/ceph-client/tools/lib/symbol/kallsyms.c

Purpose: Parses Linux kallsyms-style symbol files and maps kallsyms symbol type letters to ELF type/function classification.

Important APIs/types/functions: `kallsyms2elf_type()` maps text/weak text to `STT_FUNC`, otherwise `STT_OBJECT`. `kallsyms__is_function()` identifies `T`/`W` symbols. `kallsyms__parse()` reads symbols and calls a user callback. Internal `read_to_eol()` skips malformed lines.

Control flow: `kallsyms__parse()` opens the file, initializes buffered `io`, reads a hex address, type char, separating spaces, then up to `KSYM_NAME_LEN` chars of name until newline. Each parsed symbol is passed to `process_symbol(arg, name, type, start)` and parsing stops on callback error.

State and persistence: Stateless except for file descriptor and local buffers. Callback owns persistence of parsed data.

Dependencies/integration: Uses `symbol/kallsyms.h`, `api/io.h`, ELF constants, file open/close APIs, and Linux types/ctype from the header.

Risks: Symbol names longer than `KSYM_NAME_LEN` are truncated and remaining line content is not explicitly discarded before the next loop, which can misparse overlong lines. Open failure returns `-1` without errno detail. Callback errors stop parsing immediately.

Test signals: Fixtures with valid symbols, malformed lines, lowercase/uppercase types, weak symbols, overlong names, callback stop behavior, and missing file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/symbol/kallsyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/symbol/kallsyms.h -->
# sources/distributed-fs/ceph-client/tools/lib/symbol/kallsyms.h

Purpose: Public kallsyms parsing/classification API for tools symbol code.

Important APIs/types/functions: Defines default `KSYM_NAME_LEN` as 512. Inline `kallsyms2elf_binding()` maps `W` to `STB_WEAK`, uppercase types to `STB_GLOBAL`, and lowercase to `STB_LOCAL`. Declares `kallsyms2elf_type()`, `kallsyms__is_function()`, and `kallsyms__parse()`.

Control flow: Header provides binding classification inline and callback-driven parser declaration.

State and persistence: No state; parser callback decides storage.

Dependencies/integration: Includes `<elf.h>`, Linux ctype, and Linux types. Installed as `include/symbol/kallsyms.h`.

Risks: Binding/type mapping is intentionally coarse and may not reflect all kallsyms type letters. Callback signature must remain ABI-compatible for consumers.

Test signals: Compile and classify representative kallsyms type letters; parser behavior tested through `kallsyms.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/symbol/kallsyms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/thermal/Makefile -->
# sources/distributed-fs/ceph-client/tools/lib/thermal/Makefile

Purpose: Builds, links, installs, and cleans the `libthermal` static and shared libraries plus pkg-config metadata and headers.

Important APIs/types/functions: Version variables define `0.0.1`. Targets include `libs`, `all`, `clean`, `install_lib`, `install_headers`, `install_pkgconfig`, `install_doc`, and `install`. Artifacts include `libthermal.a`, `libthermal.so.$(VERSION)`, symlinks, and `libthermal.pc`.

Control flow: Resolves `srctree`, computes libdir, gets libnl CFLAGS from `pkg-config` or fallback path, creates a symlink to the thermal UAPI header, builds `libthermal-in.o`, archives static lib, links shared lib with a version script, generates pkg-config file from a template, and installs artifacts.

State and persistence: Produces static/shared libraries, symlinks, pkg-config file, and a tools UAPI symlink. Install copies artifacts into DESTDIR/prefix. Clean removes build products and the symlink.

Dependencies/integration: Depends on kernel tools build system, libnl-3.0 headers/libraries, `include/uapi/linux/thermal.h`, and `libthermal.map`/pc template files. Includes many kernel tools include directories.

Risks: Variables `CFGLAS` appear to be misspelled and likely intended as linker flags, so the `-L.`/`-lthermal` additions may be unused. `-Werror` is forced, making builds sensitive to external libnl/compiler warnings. Header symlink target assumes source-tree layout. Shared link command relies on external linker defaults for libnl linkage.

Test signals: Build static/shared libs with and without pkg-config libnl cflags, custom `OUTPUT`, DESTDIR install, clean, and packaging validation of `.pc` and symlinks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/thermal/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/thermal/commands.c -->
# sources/distributed-fs/ceph-client/tools/lib/thermal/commands.c

Purpose: Implements synchronous generic-netlink thermal command requests for listing zones/cooling devices and reading trips, temperatures, governors, and thresholds, plus threshold mutation commands.

Important APIs/types/functions: Static parsers include `parse_tz_get()`, `parse_cdev_get()`, `parse_tz_get_trip()`, `parse_tz_get_temp()`, `parse_tz_get_gov()`, and `parse_threshold_get()`. Public APIs include `thermal_cmd_get_tz()`, `thermal_cmd_get_cdev()`, `thermal_cmd_get_trip()`, `thermal_cmd_get_governor()`, `thermal_cmd_get_temp()`, threshold get/add/delete/flush, `thermal_cmd_init()`, and `thermal_cmd_exit()`.

Control flow: `thermal_cmd_init()` connects a netlink socket, registers local command metadata, resolves the thermal family, and verifies `nlctrl`. Command APIs build a netlink message in `thermal_genl_auto()`, optionally encode zone/threshold attributes, send it via `nl_send_msg()`, and parse replies in `handle_netlink()` based on command id. Dump replies allocate sentinel-terminated arrays.

State and persistence: Mutates `struct thermal_handler` command socket/callback fields and fills caller-visible `thermal_zone`, `thermal_cdev`, `thermal_trip`, and `thermal_threshold` arrays. Arrays use sentinel `id = -1` or `temperature = INT_MAX` and must be freed by callers.

Dependencies/integration: Depends on libnl generic netlink, Linux thermal generic-netlink UAPI constants, public `thermal.h`, and private `thermal_nl.h` helpers.

Risks: `realloc()` failure overwrites the only pointer, leaking prior entries and returning error. Parsers assume attributes arrive in an order where ID/temp precedes other fields; malformed kernel messages could index `size - 1` before allocation. `thermal_cmd_init()` does not disconnect/unregister resources on later failure paths. Threshold add/delete/flush use the same parser callback metadata although those commands may not return payloads.

Test signals: Mock netlink replies for zones, cdevs, trips, temp, governor, thresholds, malformed/missing attributes, allocation failure, family resolution failure, and threshold command encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/thermal/commands.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/thermal/events.c -->
# sources/distributed-fs/ceph-client/tools/lib/thermal/events.c

Purpose: Subscribes to thermal generic-netlink event multicast group, dispatches thermal events to user-provided callbacks, and exposes the event socket fd.

Important APIs/types/functions: Public APIs are `thermal_events_init()`, `thermal_events_exit()`, `thermal_events_handle()`, and `thermal_events_fd()`. Internal `thermal_events_ops_init()` populates the `enabled_ops` command table from callback presence. `handle_thermal_event()` parses a netlink event and calls the matching callback.

Control flow: Init records which callbacks are non-NULL, connects a netlink socket, and subscribes to `THERMAL_GENL_EVENT_GROUP_NAME`. Handle installs a valid-message callback and calls `nl_recvmsgs()`. The message handler parses attributes, skips disabled event types, and switches on `genlhdr->cmd` to invoke the corresponding user callback with extracted attributes.

State and persistence: Static `enabled_ops` is process-global, not per-handler. `struct thermal_handler` stores event socket/callback. Event handling is runtime-only.

Dependencies/integration: Depends on libnl, Linux thermal event constants, public `thermal_events_ops`, and private netlink helpers.

Risks: `enabled_ops` being global means multiple handlers with different ops can interfere. `handle_thermal_event()` assumes enabled callbacks are non-NULL and required attrs exist; malformed messages can dereference NULL attrs. `THERMAL_GENL_ATTR_GOV_NAME` is used for governor events while policy elsewhere uses `THERMAL_GENL_ATTR_TZ_GOV_NAME`, which may indicate an attribute-name mismatch depending on UAPI definitions. Exit returns error before disconnecting if unsubscribe fails.

Test signals: Simulate every event type, disabled callbacks, missing attrs, multiple handlers, subscription failure, fd retrieval, and unsubscribe/disconnect behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/thermal/events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/thermal/include/thermal.h -->
# sources/distributed-fs/ceph-client/tools/lib/thermal/include/thermal.h

Purpose: Public C API for `libthermal`, defining operations callbacks, thermal data structures, iteration helpers, discovery/init/exit, and netlink command/event/sampling functions.

Important APIs/types/functions: Defines callback groups `thermal_sampling_ops`, `thermal_events_ops`, and `thermal_ops`; data structures `thermal_trip`, `thermal_threshold`, `thermal_zone`, and `thermal_cdev`; `thermal_error_t`; callback typedefs for iterators; public functions annotated with `LIBTHERMAL_API`.

Control flow: Consumers provide `thermal_ops` to `thermal_init()`, discover zones with command APIs or `thermal_zone_discover()`, iterate sentinel-terminated arrays with `for_each_*`, handle events/sampling through fds and handle functions, and clean up with `thermal_exit()`.

State and persistence: Data arrays are heap-allocated by command code and sentinel-terminated. `struct thermal_handler` is opaque to public users. No persistence beyond process memory.

Dependencies/integration: Includes Linux thermal UAPI and sys types. Provides C linkage guards for C++ consumers and default visibility attributes for shared library exports.

Risks: The `extern "C"` closing block appears after the `#endif /* __LIBTHERMAL_H */`, so in C++ the closing brace is outside the include guard; repeated includes could be problematic. Ownership/freeing rules for discovered arrays are not documented in the header. Callback pointers may be NULL, but some handlers assume enabled callbacks exist.

Test signals: Compile from C and C++, ABI visibility checks, iterator behavior with NULL and sentinel arrays, and lifecycle tests using `thermal_init()`/`thermal_exit()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/thermal/include/thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/thermal/sampling.c -->
# sources/distributed-fs/ceph-client/tools/lib/thermal/sampling.c

Purpose: Subscribes to thermal sampling netlink group and dispatches temperature sample messages to the user `tz_temp` callback.

Important APIs/types/functions: Public APIs are `thermal_sampling_init()`, `thermal_sampling_exit()`, `thermal_sampling_handle()`, and `thermal_sampling_fd()`. Internal `handle_thermal_sample()` decodes sampling messages.

Control flow: Init connects a netlink socket and subscribes to `THERMAL_GENL_SAMPLING_GROUP_NAME`. Handle sets a valid callback and receives messages. The handler switches on `genlhdr->cmd`; for `THERMAL_GENL_SAMPLING_TEMP`, it extracts thermal zone id and temperature and invokes `th->ops->sampling.tz_temp()`.

State and persistence: Mutates sampling socket/callback fields on `struct thermal_handler`. Runtime-only event processing.

Dependencies/integration: Depends on public `thermal.h`, private `thermal_nl.h`, libnl, and Linux thermal sampling UAPI constants.

Risks: No NULL check for `th->ops` or `th->ops->sampling.tz_temp`; enabling sampling without callback can crash. Missing message attributes can crash. Exit returns before disconnect if unsubscribe fails. Init does not clean up the socket if subscription fails.

Test signals: Simulate sample event, unknown command, NULL handler, NULL callback, missing attrs, subscription failure, and fd retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/thermal/sampling.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/thermal/thermal.c -->
# sources/distributed-fs/ceph-client/tools/lib/thermal/thermal.c

Purpose: Provides high-level libthermal helpers for iterating thermal arrays, finding thermal zones, discovering full zone details, and managing handler lifecycle.

Important APIs/types/functions: Iterators: `for_each_thermal_threshold()`, `for_each_thermal_cdev()`, `for_each_thermal_trip()`, `for_each_thermal_zone()`. Finders: `thermal_zone_find_by_name()` and `thermal_zone_find_by_id()`. Lifecycle/discovery: `thermal_zone_discover()`, `thermal_init()`, and `thermal_exit()`.

Control flow: Iterators walk sentinel-terminated arrays and OR callback return values. Zone discovery first fetches zones, then for each zone fetches trips, thresholds, and governor. `thermal_init()` allocates a handler, stores ops, then initializes events, sampling, and command channels in order. `thermal_exit()` calls all three exit functions then frees the handler.

State and persistence: Uses heap-allocated `struct thermal_handler` and data arrays from command calls. No automatic freeing for discovered zone arrays/trips/thresholds is provided here.

Dependencies/integration: Calls command/event/sampling APIs declared in `thermal.h` and uses private `thermal_nl.h` for handler layout.

Risks: `thermal_init()` leaks partially initialized netlink resources if a later init step fails. `thermal_exit()` assumes `th` is non-NULL and all channels were initialized. `thermal_zone_discover()` leaks `tz` if per-zone detail fetch fails. Iterators OR all callback returns, so they do not short-circuit on failure.

Test signals: Iterator sentinel behavior, finder success/failure, discovery success and partial failure, init failure at each stage with leak checks, and exit with normal/partial handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/thermal/thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/thermal/thermal_nl.c -->
# sources/distributed-fs/ceph-client/tools/lib/thermal/thermal_nl.c

Purpose: Implements low-level libnl helpers for connecting to generic netlink, sending messages synchronously, resolving thermal multicast group IDs, and subscribing/unsubscribing.

Important APIs/types/functions: Public-private APIs include `nl_send_msg()`, `nl_thermal_connect()`, `nl_thermal_disconnect()`, `nl_subscribe_thermal()`, and `nl_unsubscribe_thermal()`. Internal callbacks handle sequence checks, netlink errors, finish, ack, and family multicast group parsing.

Control flow: `nl_thermal_connect()` allocates callbacks and socket, connects generic netlink, and installs error/finish/ack/seq callbacks. `nl_send_msg()` sends a message, installs the caller rx handler, then loops receiving until `done` or `err`. Multicast resolution sends `CTRL_CMD_GETFAMILY` for the thermal family, parses nested multicast groups, and returns the requested group id. Subscribe/unsubscribe add/drop socket membership.

State and persistence: Uses thread-local `err` and `done` flags shared by callbacks in the current thread. Socket/callback objects are allocated and returned to callers. No file persistence.

Dependencies/integration: Depends on libnl core/genl/ctrl APIs and thermal UAPI names from `thermal.h`/`thermal_nl.h`.

Risks: `nl_thermal_connect()` returns `THERMAL_ERROR` without freeing socket/callback if callback setup fails. `nl_send_msg()` can spin indefinitely if callbacks never set `done` or `err`. Thread-local flags help per-thread concurrency but one thread using multiple sockets concurrently still shares flags. `nl_get_multicast_id()` does not check `genlmsg_put()`/`nla_put_string()` failures before send.

Test signals: Mock libnl for connect failures at each step, callback setup failure, send error, ack/finish/error callbacks, group resolution success/missing group, subscribe/unsubscribe failure, and concurrent sends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/thermal/thermal_nl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/thermal/thermal_nl.h -->
# sources/distributed-fs/ceph-client/tools/lib/thermal/thermal_nl.h

Purpose: Private libthermal header exposing handler internals and low-level netlink helper prototypes to implementation files.

Important APIs/types/functions: `struct thermal_handler` stores status fields, `thermal_ops *`, a message pointer, three netlink sockets, and three callback objects. `struct thermal_handler_param` packages a handler plus user argument for callbacks. Declares subscribe/unsubscribe/connect/disconnect/send helpers.

Control flow: Implementation files include this header to access handler internals and pass handler-param bundles into libnl callbacks.

State and persistence: Defines process memory layout for the opaque public handler. Sockets and callbacks are owned by init/exit routines.

Dependencies/integration: Includes libnl headers for netlink/genl/mngt/ctrl and is paired with public `thermal.h`.

Risks: Because internals are shared across implementation files, lifecycle invariants are distributed. Fields `done`, `error`, and `msg` are present but not meaningfully used by the current low-level implementation. No ownership annotations for sockets/callbacks.

Test signals: Compile all thermal implementation files against this header; lifecycle behavior tested through thermal init/exit and netlink helper tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/thermal/thermal_nl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/vsprintf.c -->
# sources/distributed-fs/ceph-client/tools/lib/vsprintf.c

Purpose: Provides userspace implementations of kernel-style `vscnprintf()`, `scnprintf()`, and `scnprintf_pad()` helpers.

Important APIs/types/functions: `vscnprintf(buf, size, fmt, args)` wraps `vsnprintf()` and returns the number actually written capped at `size - 1`. `scnprintf()` is variadic equivalent. `scnprintf_pad()` writes formatted text and pads the remaining buffer with spaces before NUL termination.

Control flow: Each function formats with `vsnprintf()`/`vscnprintf()`, compares the result against signed `size`, and returns a capped count. Padding loops from formatted length to `size`, fills spaces, then writes NUL.

State and persistence: Stateless except mutation of caller-provided buffers.

Dependencies/integration: Includes `<linux/kernel.h>`, `<sys/types.h>`, and `stdio.h` for `vsnprintf`; used by tools expecting kernel formatting semantics.

Risks: For `size == 0`, `ssize` is 0 and return expression can produce `-1`, matching kernel-ish semantics but risky for callers expecting nonnegative `int`. `scnprintf_pad()` writes `buf[i] = 0` after loop where `i == size`, which writes one byte past the supplied size if `i < size` branch runs to completion. Formatting errors from `vsnprintf()` are not specially handled.

Test signals: Test truncation, exact fit, zero size, formatting error if mockable, and `scnprintf_pad()` with small buffers under ASan to catch the apparent off-by-one write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/vsprintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/zalloc.c -->
# sources/distributed-fs/ceph-client/tools/lib/zalloc.c

Purpose: Provides zero-allocation and freeing helpers for tools code.

Important APIs/types/functions: `zalloc(size)` returns `calloc(1, size)`. `__zfree(void **ptr)` frees `*ptr` and sets it to NULL.

Control flow: Straight wrappers around libc allocation/free.

State and persistence: Mutates caller pointer in `__zfree()`. Allocated memory is caller-owned.

Dependencies/integration: Includes `<linux/zalloc.h>` for declarations and libc `stdlib.h`.

Risks: `__zfree()` does not check `ptr` before dereference; callers must pass a valid pointer-to-pointer. `zalloc()` returns NULL on allocation failure without diagnostics.

Test signals: Allocate zeroed memory, free normal pointer, free NULL pointee, and invalid pointer-to-pointer avoidance through API usage tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/zalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/linux-kernel.cfg -->
# sources/distributed-fs/ceph-client/tools/memory-model/linux-kernel.cfg

Purpose: Herd/LKMM configuration file selecting the Linux-kernel memory model, macro definitions, Bell/Cat model files, variant, graph layout, event visibility, and edge rendering attributes.

Important APIs/types/functions: Configuration keys include `macros linux-kernel.def`, `bell linux-kernel.bell`, `model linux-kernel.cat`, `variant lkmmv2`, graph/display settings, and colored `edgeattr` entries for relations such as `hb`, `co`, `mb`, `wmb`, and `rmb`.

Control flow: Consumed by herd7/litmus tooling rather than executed. Tools read the file to configure model evaluation and generated graph output.

State and persistence: Static configuration. No runtime state.

Dependencies/integration: Integrates with `tools/memory-model` scripts and herdtools7. Referenced model/macro files must exist relative to the memory-model directory.

Risks: Changes alter formal verification semantics and visualization. Missing referenced files or unsupported keys break herd runs. Display settings can affect graph readability but not model result.

Test signals: Run representative LKMM litmus tests with `herd7 -conf linux-kernel.cfg` through existing scripts and compare expected `Result:` annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/linux-kernel.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/checkalllitmus.sh -->
# sources/distributed-fs/ceph-client/tools/memory-model/scripts/checkalllitmus.sh

Purpose: Runs LKMM checking over all top-level `.litmus` files in `litmus-tests` and reports whether results match embedded expected `Result:` comments.

Important APIs/types/functions: Shell script sourcing `scripts/parseargs.sh`; uses `LKMM_DESTDIR`, `LKMM_HW_MAP_FILE`, `scripts/simpletest.sh`, and `scripts/checklitmus.sh`.

Control flow: Validates `litmus-tests` is accessible, mirrors directories into destination when needed, iterates `litmus-tests/*.litmus`, skips non-simple tests for hardware translation mode, runs each through `checklitmus.sh`, accumulates failure status, and prints success or verification mismatch summary to stderr.

State and persistence: Writes `.out` files through downstream scripts into `LKMM_DESTDIR`. Creates destination directories when not using `.`.

Dependencies/integration: Requires LKMM environment from `parseargs.sh`, litmus-tests directory, herd/runlitmus/judgelitmus tooling, and optional hardware mapping support.

Risks: Only checks top-level `litmus-tests/*.litmus`, not recursive subdirectories. Unquoted `$litmusdir`/`$i` are acceptable for expected paths but fragile with spaces. Directory mirroring via generated shell commands assumes trusted path names.

Test signals: Run with default, custom `--destdir`, `--hw`, missing/inaccessible litmus-tests, passing fixtures, and intentionally mismatched `Result:` comments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/checkalllitmus.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/checkghlitmus.sh -->
# sources/distributed-fs/ceph-client/tools/memory-model/scripts/checkghlitmus.sh

Purpose: Fetches or reuses Paul McKenney's external `litmus` repository, selects C-language litmus tests with expected results and acceptable process counts, runs missing tests, and judges results.

Important APIs/types/functions: Sources `scripts/parseargs.sh` and `scripts/hwfnseg.sh`; uses temp directory `$T`, `git clone`, `mselect7 -arch C`, `scripts/runlitmushist.sh`, and `scripts/judgelitmus.sh`.

Control flow: Creates a temp workdir with cleanup trap, clones `https://github.com/paulmckrcu/litmus` if absent, mirrors directories into destination, computes already-run tests, computes eligible C tests with `Result:` comments and process-count filter, takes the symmetric difference to find needed tests, runs needed tests, judges all eligible short tests, prints run errors and `!!!` judge lines.

State and persistence: Creates/updates local `litmus` clone. Writes historical `.out` files under `LKMM_DESTDIR`. Uses temp files under `/tmp`.

Dependencies/integration: Requires network/git for first clone, herdtools `mselect7`, LKMM parseargs variables, historical run scripts, grep/sort/xargs utilities.

Risks: Network dependency makes first run non-hermetic. Uses `git checkout origin/master` without pinning a commit, so test corpus changes over time. File/path processing is newline/space fragile. `uniq -u` over combined sorted lists computes symmetric difference, so unusual duplicate cases can affect selection.

Test signals: Run with existing clone, no clone/network available, custom process limit, custom destdir, hardware suffix, and injected mismatches/errors in judge output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/checkghlitmus.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/checklitmus.sh -->
# sources/distributed-fs/ceph-client/tools/memory-model/scripts/checklitmus.sh

Purpose: Runs and judges one specified LKMM litmus test by invoking `runlitmus.sh` followed by `judgelitmus.sh`.

Important APIs/types/functions: Positional argument `$1` is the litmus file path. Calls `scripts/runlitmus.sh $1` and `scripts/judgelitmus.sh $1`.

Control flow: Sequential shell execution; because there is no `set -e`, the script's exit status is that of `judgelitmus.sh`, not necessarily `runlitmus.sh` if the run command fails but judge still runs.

State and persistence: Downstream scripts write `.out` files and judge output according to LKMM environment variables.

Dependencies/integration: Must be run from `tools/memory-model` with environment prepared by caller/parseargs. Depends on runlitmus and judgelitmus scripts.

Risks: `$1` is unquoted, so paths with spaces break. Run failure is not explicitly checked before judging. Only accepts one positional file despite shell passing possible extras to neither command.

Test signals: Run with valid test, missing test, runlitmus failure, judgelitmus mismatch, and file path quoting edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/checklitmus.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/checklitmushist.sh -->
# sources/distributed-fs/ceph-client/tools/memory-model/scripts/checklitmushist.sh

Purpose: Reruns previously executed C-language litmus tests matching current criteria into a temporary results directory, then compares new outputs with historical outputs.

Important APIs/types/functions: Sources `scripts/parseargs.sh`; uses temp `$T`, `scripts/runlitmushist.sh`, and `scripts/cmplitmushist.sh`. Relies on `LKMM_DESTDIR` and `LKMM_PROCS`.

Control flow: Requires local `litmus` repo, creates temp mirrored results tree, builds a list of historical `.litmus.out` files under destination and filters out tests with too many processes, temporarily redirects `LKMM_DESTDIR` to temp results for rerun, copies new outputs back beside old outputs as `.new`, and invokes comparison script with destination-prefixed paths.

State and persistence: Creates temp results and writes `.new` output files next to historical outputs in `LKMM_DESTDIR`. Cleans temp directory on exit.

Dependencies/integration: Requires initialized litmus history via `initlitmushist.sh`, LKMM run/compare scripts, standard shell utilities, and accessible destination history.

Risks: Generated `cp` commands via `sed | sh` assume trusted path names. Existing `.new` files may be overwritten. If rerun fails, comparison may still proceed depending on downstream behavior. Path resolution via awk handles absolute vs relative destdir but remains shell-string based.

Test signals: Run after initialized history, missing litmus repo, custom destdir, process filters, intentional changed outputs, missing historical outputs, and existing `.new` files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/checklitmushist.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/checktheselitmus.sh -->
# sources/distributed-fs/ceph-client/tools/memory-model/scripts/checktheselitmus.sh

Purpose: Checks a caller-provided list of litmus tests after parsing LKMM command-line options, reporting aggregate verification success or mismatch.

Important APIs/types/functions: Sources `scripts/parseargs.sh`; loops over remaining `"$@"`; calls `scripts/checklitmus.sh` for each file; accumulates `ret`.

Control flow: `parseargs.sh` consumes options before `--`; the script then checks each provided path, sets `ret=1` for any failure, prints mismatch or success summary to stderr, and exits with aggregate status.

State and persistence: Downstream scripts write outputs under `LKMM_DESTDIR`. The script itself keeps only aggregate status.

Dependencies/integration: Designed for paths relative to `tools/memory-model` unless `--destdir /` or another prepared destination is used. Depends on `checklitmus.sh` and LKMM environment.

Risks: The call `scripts/checklitmus.sh $i` is unquoted despite iterating `"$@"`, so paths with spaces break. With no file arguments it reports success after doing nothing. It does not short-circuit on failure.

Test signals: Run multiple passing tests, one failing test, no tests, absolute paths with destdir, and paths requiring quoting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/memory-model/scripts/checktheselitmus.sh -->
