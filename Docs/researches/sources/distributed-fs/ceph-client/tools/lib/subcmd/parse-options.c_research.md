# sources/distributed-fs/ceph-client/tools/lib/subcmd/parse-options.c

Purpose: Implements libsubcmd command-line option parsing, usage rendering, internal help/list options, option negation/abbreviation, exclusive options, callbacks, and typed value storage.

Important APIs/types/functions: Public APIs include `parse_options()`, `parse_options_subcommand()`, `usage_with_options()`, `usage_with_options_msg()`, `parse_options_usage()`, `parse_opt_verbosity_cb()`, `set_option_flag()`, and `set_option_nobuild()`. Internal helpers include `get_arg()`, `get_value()`, `parse_short_opt()`, `parse_long_opt()`, `parse_options_step()`, `parse_options_end()`, `print_option_help()`, and `usage_with_options_internal()`.

Control flow: Parsing initializes a context, scans argv, handles short clusters and long options, processes special options such as `--help`, `--help-all`, `--list-opts`, and `--list-cmds`, stores parsed values according to option type, preserves or stops at non-options depending on flags, and compacts remaining args back into argv. Usage output sorts option groups and may page output.

State and persistence: Global `error_buf` holds formatted error text until usage output frees it. Parsed option values are written directly through pointers in `struct option`. `ctx->out` aliases argv for in-place compaction.

Dependencies/integration: Uses `parse-options.h`, `subcmd-util.h`, `subcmd-config.h`, `pager.h`, Linux type/string/compiler helpers, libc conversion functions, and GNU `strcasestr`/`vasprintf`.

Risks: Many error paths call `exit(129/130)`, so library users must expect process termination. Long-option abbreviation and negation are complex and can surprise users or introduce ambiguity. `parse_options_subcommand()` allocates a generated usage string and stores it in `usagestr[0]` without freeing in normal return. Numeric parsing uses `strtol/strtoul/strtoull` without explicit range/errno checks. The `die()` message for impossible option types is intentionally abrupt.

Test signals: Cover all option types, optional args, last-arg default, no-negation, hidden/disabled/nobuild, exclusive conflict, abbreviated long options, `--no-*`, short option clusters, keep-unknown, stop-at-non-option, usage formatting, and list modes.
