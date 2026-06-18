# sources/distributed-fs/ceph-client/scripts/kconfig/lexer.l

## Purpose

`lexer.l` is the flex scanner for Kconfig syntax. It tokenizes keywords, operators, words, quoted strings, assignments, help text, variable expansion, and source-file inclusion while maintaining parser-facing file and line state.

## Important APIs, Types, and Functions

Generated scanner entry is wrapped by `yylex()`, which calls `yylex1()` and normalizes statement newlines. Public helpers are `zconf_starthelp()`, `zconf_fopen()`, `zconf_initscan()`, and `zconf_nextfile()`. Internal helpers include `new_string()`, `append_string()`, `alloc_string()`, `expand_token()`, `append_expanded_string()`, `zconf_endhelp()`, and `zconf_endfile()`. `struct buffer` stores include-stack state.

## Control Flow

The scanner uses start states `INITIAL`, `ASSIGN_VAL`, `HELP`, and `STRING`. Top-level rules ignore comments/whitespace, emit tokens for Kconfig keywords and operators, expand `$` tokens, and warn on unsupported characters. `STRING` removes escape backslashes and expands `$...`. `HELP` preserves indentation relative to the first help line. `yylex()` suppresses repeated end-of-line tokens, records `cur_lineno` at statement start, and enters `ASSIGN_VAL` after top-level variable assignment operators. EOF either pops an included file buffer or terminates scanning.

## State and Persistence Behavior

The lexer owns current source filename/line globals, previous-token tracking, temporary string buffers, help indentation state, and the include stack. It does not persist files, but it opens Kconfig and sourced files using current directory or `$srctree`.

## Dependencies and Integration Points

It includes `lkc.h`, `preprocess.h`, and `parser.tab.h`. It feeds the bison parser, uses preprocessing helpers for variable expansion, and uses `file_lookup()` for stable filename records.

## Risks and Edge Cases

Missing source files and recursive inclusion call `exit(1)`, so callers cannot recover. `zconf_nextfile()` compares include names against stored filenames, which makes path normalization important. Multi-line strings are warned and truncated back to parser flow. Help indentation is stateful and sensitive to tabs. Unsupported characters are warnings rather than fatal errors.

## Test Signals

Parser tests should cover variables, quoted strings, escaped newlines, help indentation, no-newline-at-EOF warnings, missing include errors, recursive include errors, `$srctree` lookup, and preprocessing expansion failures.
