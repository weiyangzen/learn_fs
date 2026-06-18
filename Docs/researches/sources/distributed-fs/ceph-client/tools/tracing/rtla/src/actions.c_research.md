# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/actions.c

## Purpose
`actions.c` implements RTLA's threshold/end action list. Actions can save trace output, send a signal, run a shell command, or request measurement continuation after a threshold stop.

## Important APIs, Types, and Functions
Public functions are `actions_init()`, `actions_destroy()`, `actions_add_trace_output()`, `actions_add_signal()`, `actions_add_shell()`, `actions_add_continue()`, `actions_parse()`, and `actions_perform()`. Internal `actions_new()` grows the action array with `reallocarray_fatal()`. `extract_arg()` parses comma-delimited action tokens like `file=...`, `num=...`, `pid=...`, or `command=...`.

## Control Flow
Tool parsers initialize action sets and call `actions_parse()` for `--on-threshold` or `--on-end`. The parser copies the trigger string, tokenizes by comma, determines action type, validates required arguments, and appends a normalized action. Runtime calls `actions_perform()`, which walks the list in order. Trace actions call `save_trace_to_file()`, signal actions call `kill()` using parent PID when `pid=parent`, shell actions call `system()`, and continue actions set `continue_flag` and stop further action processing.

## State and Persistence
`struct actions` owns a heap array and duplicated strings. Trace actions persist trace snapshots to files; shell actions can have arbitrary side effects; signal actions affect external processes; continue actions mutate `continue_flag`.

## Dependencies and Integration Points
The implementation depends on `trace.h` for trace saving and `utils.h` fatal/string helpers. It is integrated by `common.c` threshold/end handling and by mode parsers that provide default trace filenames.

## Risks and Edge Cases
Action parsing uses `strtok()` and therefore supports only simple comma-separated syntax; shell commands containing commas are not supported. `system()` executes through the shell and carries command-injection risk if users pass untrusted strings. `actions_init()` does not explicitly clear `present[]`, so callers must allocate zeroed parent params, as current parsers do with `calloc_fatal()`. `ACTION_CONTINUE` returns immediately and suppresses later actions.

## Test Signals
Unit tests should cover valid/invalid parse strings for each action, dynamic growth, parent PID signal handling, continue ordering, trace-output instance requirements, and cleanup freeing duplicated strings.
