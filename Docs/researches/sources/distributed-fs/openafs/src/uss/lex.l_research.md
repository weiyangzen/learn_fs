
# sources/distributed-fs/openafs/src/uss/lex.l

`lex.l` is the lexer for `uss` bulk/template files. It recognizes line-leading single-letter commands, comments, whitespace, quoted strings, unquoted strings, end-of-line tokens, invalid commands, and performs variable substitution before returning `STRING_TKN`.

Important patterns are comments `#[^\n]*`, command starts `D/F/L/S/E/X/V/G/A/Y` followed by whitespace, unquoted strings beginning with `[.A-Z0-9a-z/$]`, quoted strings without embedded newlines, and invalid line-leading command characters. The global `line` counter increments on blank lines and newline tokens. `yywrap` returns 1 for single-input completion.

The key function is `Replace`. It strips opening quotes, scans for `$` variables, expands positional `$1`..`$9`, rejects `$0`, checks against `uss_VarMax`, expands named variables like `$USER`, `$UID`, `$SERVER`, `$PART`, `$MTPT`, `$NAME`, `$AUTO`, and `$PWEXPIRES`, and warns while copying through unknown variables. `$AUTO` calls `uss_procs_PickADir`, then uses global `uss_Auto`.

State and side effects are parser globals and substitution globals from `uss_common.h`/`uss_procs.h`. The lexer itself does not persist data, but substitutions drive later provisioning side effects. Dependencies include yacc-generated `y.tab.h`, uss common globals, and `uss_procs_PrintErr`.

Risks include unchecked `strcpy` into yacc semantic buffers during substitution, quoted-string pattern accepting newline as a terminator, unknown variable handling advancing one character at a time, command recognition only at line start, and direct `exit` on invalid positional variables. Test signals include all command tokens, comments/blank lines, quoted and unquoted strings, every supported variable, `$AUTO` selection, unknown variable warnings, invalid commands, and line-number accuracy.
