# sources/distributed-fs/ceph-client/tools/perf/perf.c

### Purpose
`perf.c` is the main executable dispatcher for perf. It initializes global perf infrastructure, parses top-level options, routes internal commands to `cmd_*()` functions, and falls back to external `perf-<cmd>` helpers.

### Important APIs, Types, And Functions
`struct cmd_struct` maps command names to builtin functions and option flags. `commands[]` is the authoritative command list used for dispatch and completion. Top-level option handling is in `handle_options()`. `run_builtin()` applies pager/browser config and executes a builtin. `handle_internal_command()`, `execv_dashed_external()`, and `run_argv()` implement internal and external command lookup. `main()` initializes config, paths, libperf printing, build-id directory, signal behavior, and unknown-command help.

### Control Flow
Startup initializes debug, exec path, pager, libperf, config, and build-id directory. If invoked as `perf-foo`, it tries direct internal dispatch. If invoked as `trace`, it directly calls `cmd_trace()` when built with libtraceevent. Otherwise it strips top-level options, prints help when no command is given, sets up PATH, blocks SIGWINCH, then loops attempting internal dispatch or external `perf-<cmd>` execution. Unknown commands are passed through `help_unknown_cmd()` once.

### State And Persistence
Global state includes `use_pager`, `debug_fp`, perf config globals, build-id directory, environment variables for pager/paths, and optional debug output file. It does not create command-specific persistent state itself.

### Dependencies And Integration Points
It integrates with every builtin declared in `builtin.h`, libsubcmd, perf config, UI browser setup, parse-events, tracing path configuration, build-id cache, libperf logging, and shell completion through `--list-cmds`/`--list-opts`.

### Risks
Command tables must stay synchronized with declarations, build conditionals, man/help docs, and external scripts such as `perf-archive` and `perf-iostat`. Top-level option parsing stops before command options, so ambiguous flags must be handled carefully. External fallback relies on PATH setup and status conventions from `run_command_v_opt()`.

### Test Signals
Run top-level help/version/listing options, builtin commands, external script commands, `perf-<cmd>` symlink invocation, unknown command suggestions, pager/no-pager behavior, debug file setup, and builds with optional features disabled.
