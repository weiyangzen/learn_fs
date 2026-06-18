# sources/distributed-fs/orangefs/src/common/dotconf/dotconf.c

Purpose: Implements the bundled dot.conf configuration parser used by OrangeFS. It opens config files, reads logical lines, parses typed command arguments, applies defaults, dispatches callbacks, and supports internal `Include`/`IncludePath` directives with wildcard expansion.

Important APIs/functions: `PINT_dotconf_create()` allocates a `configfile_t`, opens the input, registers built-in and caller options, and selects case-sensitive or case-insensitive comparison. `PINT_dotconf_command_loop()` and `_until_error()` read lines and call `PINT_dotconf_handle_command()`. `PINT_dotconf_set_command()` populates `command_t` for `ARG_TOGGLE`, `ARG_INT`, `ARG_STR`, `ARG_LIST`, `ARG_NAME`, `ARG_RAW`, and `ARG_NONE`. `PINT_dotconf_read_arg()` handles quotes, backslash escaping, inline comments, and environment substitution. Include handling is split across `dotconf_cb_include()`, `dotconf_cb_includepath()`, wildcard discovery, `PINT_dotconf_handle_star()`, and `PINT_dotconf_handle_question_mark()`.

Control flow: The parser loops over physical lines via `fgets()`, joins backslash-continued lines, skips blank/comment lines, extracts the first token into a static option-name buffer, searches registered option tables, optionally applies an `ARG_NAME` fallback, invokes context checking, then invokes the option callback. Include callbacks recursively create a child parser, copy later option tables and callbacks, parse included files, and clean up.

State/persistence: `configfile_t` stores stream, filename, line number, flags, include path, registered option-table pointers, and callback pointers. The parser has a file-static `name` buffer for the current option. It does not persist settings itself; caller callbacks own configuration state.

Dependencies/integration: Uses POSIX/Win32 filesystem APIs for access and directory scanning, `pvfs2-internal.h`, and the public declarations in `dotconf.h`. `module.mk.in` adds it to library and server sources.

Risks: Fixed-size buffers dominate (`CFG_BUFSIZE`, `CFG_MAX_VALUE`, `CFG_MAX_FILENAME`, `CFG_VALUES`). Recursive includes have no explicit cycle/depth guard. Some realloc calls assign/check incorrectly in wildcard handlers. `PINT_dotconf_substitute_env()` can advance output pointers by full environment value length even when `strncat()` truncates. The static `name` buffer makes parsing state process-global and not reentrant. `id`/line reporting paths often warn and continue, so callers need strict error handlers if malformed config should fail.

Test signals: Cover quote/escape parsing, inline comment flags, `${VAR:-default}` substitution, here-docs, defaults, unknown options, context rejection, nested includes, wildcard includes on POSIX and Windows, and include-path environment override.
