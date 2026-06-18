# Chunk Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/configlexer.c lines 6093-7274

## Scope

This chunk covers the tail of the generated Unbound configuration lexer action table and most of the generated flex scanner runtime for `configlexer.c`. It is within `sources/os/bsd/openbsd-src`, which is included by `Docs/research_subset_a.md`.

The source is generated from `util/configlexer.lex` and includes custom actions for single-quoted string values, `include:` and `include-toplevel:` directives, generic string arguments, unknown-token diagnostics, EOF handling across nested include files, and the standard flex buffer/scanner management routines.

## APIs and Entry Points

- `yylex()` action cases in this range return parser tokens including `STRING_ARG` and `VAR_FORCE_TOPLEVEL`.
- Single-quoted value actions enter `singlequotedstr`, accumulate text with `yymore()`, terminate by replacing the closing quote with `'\0'`, duplicate the value into `yylval.str`, and return `STRING_ARG`.
- Include directive actions call `config_start_include_glob(yytext, 0)` for ordinary includes and `config_start_include_glob(yytext, 1)` for top-level includes.
- EOF handling for `INITIAL` and `val` either terminates scanning or unwinds one include file via `config_end_include()`.
- Generated flex APIs in this chunk include `yyrestart()`, `yy_switch_to_buffer()`, `yy_create_buffer()`, `yy_delete_buffer()`, `yy_flush_buffer()`, `yypush_buffer_state()`, `yypop_buffer_state()`, `yy_scan_buffer()`, `yy_scan_string()`, `yy_scan_bytes()`, accessor setters/getters, `yylex_destroy()`, `yyalloc()`, `yyrealloc()`, and `yyfree()`.

## Control Flow

Single-quoted string parsing starts when the lexer sees the opening quote and switches to `singlequotedstr`. Interior text is appended with `yymore()`. A newline before the closing quote reports `newline inside quoted string, no end '`, increments `cfg_parser->line`, and returns to `INITIAL`. EOF reports `EOF inside quoted string`, decrements the pending argument count, and returns to `INITIAL` or `val` depending on whether more values remain. A closing quote finalizes and returns a `STRING_ARG`.

For `include:`, the lexer saves the current start state in `inc_prev`, enters `include`, skips whitespace, tracks newlines, and accepts either an unquoted include name or a double-quoted include name. When a name is complete it starts the include glob, restores `inc_prev`, and continues scanning from the included file if opening succeeded. Errors inside the directive restore `inc_prev`.

For `include-toplevel:`, the same path is used with a `toplevel` flag of `1`. After an include file is started, the lexer immediately returns `VAR_FORCE_TOPLEVEL` so the parser can force grammar state at top level. When EOF is reached inside a top-level include, EOF unwinding also returns `VAR_FORCE_TOPLEVEL` after restoring the previous include frame.

After user actions, the generated scanner loop handles end-of-buffer transitions. It distinguishes a real NUL byte, an input refill, a last pending token before EOF, and actual EOF. Actual EOF invokes the state-specific EOF action through `YY_STATE_EOF(YY_START)`.

The flex buffer runtime moves unmatched text to the beginning of the buffer, grows owned buffers when needed, reads additional bytes through `YY_INPUT`, appends two end-of-buffer sentinels, and resumes the DFA. Buffer switch/push/pop operations save and restore `yy_c_buf_p`, `yy_n_chars`, `yyin`, and `yy_hold_char`.

## State and Data Flow

- `num_args` counts how many values remain for the current config directive. This chunk decrements it when string arguments complete or when quoted-string EOF is encountered.
- `yylval.str` receives heap-duplicated string values from quoted and unquoted value rules.
- `cfg_parser->line` is manually incremented on recognized newlines and newline-in-string errors.
- `inc_prev` stores the start condition to restore after include directive parsing.
- `inc_toplevel` marks whether the active include should force a top-level parser token on entry/return.
- `config_include_stack` controls nested include unwinding at EOF.
- `yy_buffer_stack`, `yy_buffer_stack_top`, and `yy_buffer_stack_max` hold generated flex buffer state.
- `YY_CURRENT_BUFFER` owns the active input source; include handling swaps this buffer to scan included files.
- `yyin`, `yyout`, `yytext`, `yyleng`, `yy_start`, `yy_c_buf_p`, `yy_n_chars`, and `yy_hold_char` are the non-reentrant scanner globals manipulated by generated flex helpers.

## Dependencies

This chunk depends on local parser definitions from `configparser.h`, including `STRING_ARG` and `VAR_FORCE_TOPLEVEL`, and the `yyerror` rename in `configyyrename.h` that maps lexer error reporting to `ub_c_error`.

It depends on earlier custom lexer support in the same generated file: `YDVAR`, `struct inc_state`, `config_include_stack`, `inc_prev`, `num_args`, `inc_toplevel`, `config_start_include_glob()`, `config_end_include()`, and `init_cfg_parse()`.

It depends on `cfg_parser` fields from the config parser context, especially `filename`, `line`, and `chroot`, and on `ub_c_error_msg()` for unknown keyword, stray character, and `ECHO` syntax diagnostics.

Standard C/POSIX dependencies include `FILE`, `fclose()`, `fprintf()`, `stderr`, `stdin`, `stdout`, `malloc()`, `realloc()`, `free()`, `strdup()`, `strlen()`, `memset()`, `isatty()`, `fileno()`, `errno`, and `exit()`.

## Risks and Edge Cases

- Unquoted string arguments call `strdup(yytext)` and return `STRING_ARG` without checking allocation failure in this visible rule.
- Quoted string allocation failures call `yyerror("out of memory")` but still return `STRING_ARG`; downstream parser code must tolerate a possible null `yylval.str`.
- Newline inside quoted strings resets to `INITIAL` rather than preserving a partially consumed multi-argument `val` state.
- EOF inside a quoted string decrements `num_args`, which can alter directive argument accounting even though the value was malformed.
- Include glob expansion and include opening happen in earlier helpers; from this chunk's perspective include failures are diagnostic side effects and scanning resumes in the previous lexer state.
- `include-toplevel` returns `VAR_FORCE_TOPLEVEL` even after starting an include; parser logic must be prepared for a control token that is not a normal config variable.
- The generated scanner is non-reentrant and relies on global mutable state, so concurrent parses would interfere unless externally serialized.
- Flex buffer growth uses dynamic allocation and fatal exits on allocation failure in generated helpers, unlike some custom actions that report parser errors and continue.
- `yy_scan_buffer()` requires the caller-supplied buffer to end with two `YY_END_OF_BUFFER_CHAR` bytes; otherwise it returns null.
- `yylex_destroy()` deletes current buffers while looping through stack state; correctness depends on generated buffer-stack invariants.

## Cross-Chunk References

- Earlier chunks define the large keyword-to-token action table and the `YDVAR(nargs, var)` macro that sets `num_args` and enters `val`.
- Earlier lines define quoted double-string behavior that mirrors this chunk's single-quoted handling.
- Earlier custom include helpers implement the stack frames that this chunk unwinds at EOF.
- Parser files outside this generated lexer define how `STRING_ARG`, `VAR_FORCE_TOPLEVEL`, and the many `VAR_*` tokens are consumed.
- The final per-file report should merge this chunk with the previous chunk research instead of treating these generated runtime routines as the whole file.