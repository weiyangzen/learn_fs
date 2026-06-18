# sources/distributed-fs/ceph-client/scripts/dtc/srcpos.c

Purpose: Implements dtc source-file stack management, include search paths, dependency-file emission, parser source location tracking, and formatted source-position diagnostics. It is the runtime backing for the `srcpos.h` parser location type.

Important APIs/functions: `srcfile_relative_open()` opens stdin or searches current source directory plus added include paths. `srcfile_push()` and `srcfile_pop()` maintain nested include state with `MAX_SRCFILE_DEPTH`. `srcfile_add_search_path()` appends include directories. `srcpos_update()` advances line/column counters for lexer text. `srcpos_copy()`, `srcpos_extend()`, and `srcpos_free()` manage location chains. `srcpos_string()`, `srcpos_string_first()`, `srcpos_string_last()`, `srcpos_error()`, and `srcpos_verror()` format diagnostics and annotations. `srcpos_set_line()` supports preprocessor line directives.

Control flow: parsing starts with `srcfile_push()`, which opens the file, records dirname, initializes line/column, links the previous file state, and seeds the initial path for shorter annotations. The lexer calls `srcpos_update()` for consumed text. Includes push another `srcfile_state`; popping restores the previous file. Diagnostics walk `srcpos` chains and shorten filenames relative to the initial source where possible.

State/persistence: Uses process-global `depfile`, `current_srcfile`, include search list, include depth, initial source path, and `initial_cpp`. `srcfile_pop()` intentionally leaks `srcfile_state` structures because parser location records may still reference them. Dependency output appends escaped paths to `depfile`.

Dependencies/integration: Depends on dtc allocation/error helpers from `util.h`, parser globals from generated lexer/parser, libc file I/O, and DTC global annotation settings through callers. It supplies `YYLTYPE` state consumed by the parser and annotation output in `treesource.c`.

Risks: Global mutable state is not reentrant. Closing stdin in `srcfile_pop()` can surprise embedding contexts when input is `-`. `shorten_to_initial_path()` assumes `initial_path` has been set before comment formatting. Location lifetime relies on intentional leaks. Include recursion is bounded but include path nodes are also never freed.

Test signals: Exercise nested includes, dependency-file output with paths containing spaces, stdin input, preprocessor line changes, multi-line tokens, annotation levels, and include-depth failure.
