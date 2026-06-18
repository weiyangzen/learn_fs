<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/iostat.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/iostat.c

## Purpose

`iostat.c` provides weak default implementations for perf iostat hooks on platforms that do not supply architecture-specific support.

## Important APIs, Types, and Functions

It defines global `enum iostat_mode_t iostat_mode = IOSTAT_NONE` and weak functions `iostat_prepare()`, `iostat_parse()`, `iostat_list()`, `iostat_release()`, `iostat_print_header_prefix()`, `iostat_print_metric()`, `iostat_prefix()`, and `iostat_print_counters()`.

## Control Flow

Unsupported builds return `-1` from prepare/parse and otherwise no-op. `iostat_parse()` prints a clear unsupported-platform error.

## State and Persistence Behavior

Only `iostat_mode` is mutable global state. No runtime allocations or persistent data are managed by this fallback file.

## Dependencies and Integration Points

It integrates with perf stat iostat command-line and output paths. Architecture/platform files can override the weak symbols with real implementations.

## Risks and Edge Cases

Weak-symbol behavior depends on linker support and build configuration. Callers must handle `-1` from prepare/parse and should not assume print hooks did anything on unsupported platforms.

## Test Signals

Build tests should verify unsupported platforms link and print the unsupported message. Supported-platform builds should verify strong symbols override these weak defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/iostat.c -->
