# sources/distributed-fs/ceph-client/scripts/kconfig/preprocess.c

## Purpose
`preprocess.c` implements Kconfig's make-like variable and function expansion layer. It expands `$()` references in tokens and assignment values, supports simple/recursive/append variables, user-defined functions, selected built-in functions, and tracks referenced environment variables so generated config dependencies can notice environment changes.

## Important APIs, Types, and Functions
Internal types are `struct env`, `struct function`, and `struct variable`. Exported functions are `env_write_dep()`, `variable_add()`, `variable_all_del()`, `expand_dollar()`, and `expand_one_token()`.

Built-ins in `function_table` are `error-if`, `filename`, `info`, `lineno`, `shell`, and `warning-if`. Expansion internals include `env_expand()`, `function_expand()`, `variable_lookup()`, `variable_expand()`, `eval_clause()`, `expand_dollar_with_args()`, `__expand_string()`, and `expand_string_with_args()`.

## Control Flow
The parser adds variables through `variable_add()` for `=`, `:=`, and `+=`. Simple variables are expanded at assignment time; recursive variables store the raw text and expand when referenced. `__expand_string()` scans for `$`, delegates `$(`...`)` clauses to `expand_dollar_with_args()`, and appends expanded text. `eval_clause()` splits comma-separated function arguments while respecting nested parentheses, expands the callee name and arguments, then resolves in order: user variable/function, built-in function, environment variable, empty string.

## State and Persistence
Variables live in `variable_list` until `variable_all_del()` is called by `conf_parse()`. Referenced environment variables live in `env_list` until `env_write_dep()` writes dependency snippets to `autoconf_cmd` and deletes them. Recursive expansion is protected by `exp_count` and a hard depth limit.

## Dependencies and Integration Points
The file depends on `list.h`, `xalloc.h`, `array_size.h`, scanner globals `cur_filename` and `yylineno`, and shared string type `struct gstr`. It is called by the lexer/parser to expand Kconfig input and to produce dependency metadata for `include/config/auto.conf.cmd`.

## Risks and Edge Cases
`do_shell()` reads at most 4096 bytes from command output and ignores further output, so long shell outputs are truncated. It executes arbitrary shell commands from Kconfig files, which is expected but security-sensitive when parsing untrusted trees. The file contains a duplicate `v = variable_lookup(name);`, harmless but suspicious. Comma splitting supports nesting but not escape syntax beyond Kconfig's variable tricks. Undefined variables collapse to empty strings.

## Test Signals
Tests in `tests/preprocess/builtin_func`, `circular_expansion`, `escape`, and `variable` directly exercise built-ins, recursive detection, quoting/escaping, simple versus recursive variables, appends, left-hand-side expansion, and user-defined function arguments.
