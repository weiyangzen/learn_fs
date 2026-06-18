# sources/distributed-fs/ceph-client/tools/perf/builtin-check.c

Purpose: implements `perf check feature`, a small command that reports whether selected optional perf build features are compiled in and exits successfully only if all requested features are available.

Important APIs, types, and functions: `supported_features[]` is a table of `struct feature_status` entries populated by `FEATURE_STATUS` and `FEATURE_STATUS_TIP`, mapping user-visible names to compile-time macros and optional build tips. `on_off_print()` colorizes status. `feature_status__printf()` prints one feature with macro and tip. `has_support()` performs case-insensitive lookup by name or macro. `subcommand_feature()` parses a single comma-separated feature list. `cmd_check()` dispatches subcommands.

Control flow: top-level parsing recognizes the `feature` subcommand and a global `--quiet` option. The feature subcommand requires exactly one argument, duplicates it because `strtok()` mutates the string, then checks every comma-separated token. The boolean result is an AND across requested features, and the return value is inverted so missing or unknown features produce a nonzero exit status.

State and persistence: no persistent state is written. State comes from compile-time configuration macros in `tools/config.h` and the global `quiet` flag. Output goes to stdout/stderr with perf color helpers.

Dependencies and integration points: uses perf parse-options subcommand support, color output, debug error printing, and the shared `struct feature_status` type also used by perf version/build-options code.

Risks: unknown features are treated the same as disabled features in the exit status. The status string is lowercase `"on"` for enabled and uppercase `"OFF"` for disabled, and `on_off_print()` keys only on `"OFF"`. The final `free(check_usage[0])` path is unreachable after `usage_with_options()` exits, but documents parser ownership expectations. Comma parsing does not trim whitespace.

Test signals: run known enabled and disabled features, macro-name aliases, mixed comma lists, unknown feature, quiet mode, missing argument, too many arguments, and color/no-color output environments.
