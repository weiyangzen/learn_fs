<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/help-unknown-cmd.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/help-unknown-cmd.c

## Purpose
`help-unknown-cmd.c` implements perf's unknown-command suggestion and optional autocorrect behavior. It loads known built-in/external command names, computes Levenshtein distances against the user input, prints suggestions, and can return a single assumed command.

## Important APIs, types, and functions
The public function is `help_unknown_cmd(const char *cmd, struct cmdnames *main_cmds)`. Internal helpers are `perf_unknown_cmd_config` for `help.autocorrect`, `levenshtein_compare` for sorting by edit distance then name, and `add_cmd_list` for merging discovered external command names into the main command list.

## Control flow
`help_unknown_cmd` reads perf config, calls `load_command_list("perf-", ...)`, merges command arrays, sorts and deduplicates with subcmd helpers, then reuses `cmdname->len` to store edit distance. The best-distance prefix becomes the suggestion set. If `help.autocorrect` is set and exactly one best match exists, it warns, optionally sleeps via `poll`, and returns the assumed command name. Otherwise it prints an error and any close suggestions with distance below 6.

## State and persistence
State is transient except the static `autocorrect` config variable. Ownership is subtle: on autocorrect, `main_cmds->names[0]` is set to `NULL` before cleanup so the returned string remains valid for the caller; `other_cmds` is cleaned and merged storage is left in `main_cmds`.

## Dependencies and integration points
The file uses perf config parsing, command discovery/cleanup from subcmd help, `alloc_nr`, `zfree`, Levenshtein scoring, and the builtin command registry.

## Risks
`cmdname->len` is repurposed from name length to edit distance, so later code must not assume it still contains a string length after this function. Allocation failure falls back to the generic error path. Autocorrect sleeps in tenths of a second and can unexpectedly execute a command if config enables it.

## Test signals
Tests should cover no suggestions, single autocorrect match, multiple equal-distance suggestions, external command merging, duplicate removal, allocation failure simulation, and `help.autocorrect` values of zero, positive, and negative.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/help-unknown-cmd.c -->
