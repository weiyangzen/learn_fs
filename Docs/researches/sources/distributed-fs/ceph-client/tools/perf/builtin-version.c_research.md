# sources/distributed-fs/ceph-client/tools/perf/builtin-version.c

### Purpose
This file implements `perf version`. It prints the perf version string and, when requested by `--build-options` or `-v`, prints the status of build-time optional features.

### Important APIs, Types, And Functions
`struct version` stores the `build_options` flag. `version_options` defines `--build-options` using the subcmd parse-options API. `library_status()` iterates the global `supported_features[]` array declared in `builtin.h` and prints each feature through `feature_status__printf()`. `cmd_version()` is the builtin entry point called from `perf.c`.

### Control Flow
`cmd_version()` parses options with `PARSE_OPT_STOP_AT_NON_OPTION`, prints `perf version %s` using `perf_version_string`, then conditionally calls `library_status()` if the option was set or global `verbose` is positive.

### State And Persistence
State is limited to one static `version` instance and global `verbose`. The command does not write persistent data.

### Dependencies And Integration Points
It depends on `util/header.h` for `perf_version_string`, `util/debug.h` for `verbose`, `color.h`/feature status formatting, generated `tools/config.h`, and `builtin.h` for supported feature metadata.

### Risks
Output correctness depends on `supported_features[]` staying in sync with build configuration. The static `version` object is not reset between hypothetical in-process invocations, though perf normally exits per command.

### Test Signals
Run `perf version`, `perf version --build-options`, and `perf -vv` and verify version output plus expected feature rows for enabled/disabled libraries.
