# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Coverage.inc

## Purpose

`Coverage.inc` implements a signal-callable coverage flush hook for MGM/OFS builds. In coverage builds it dumps gcov data for the main binary and asks loaded plugins to dump their own coverage; in non-coverage builds it logs that coverage support is absent.

## Important APIs, Types, and Functions

- `xrdmgmofs_coverage(int sig)` is the exported coverage handler.
- Under `COVERAGE_BUILD`, it calls `__gcov_dump()`.
- It obtains loaded dynamic libraries from `eos::common::PluginManager::GetInstance().GetDynamicLibMap()`.
- For each dynamic library, it looks up `plugin_coverage` and calls it when present.

## Control Flow

The handler logs that coverage data is being printed, flushes gcov data for the main process, iterates the plugin manager's dynamic library map, and invokes optional plugin coverage functions. Without `COVERAGE_BUILD`, it only logs a notice.

## State and Persistence Behavior

The function writes coverage data through gcov runtime side effects and plugin-provided hooks. It does not mutate namespace state. Plugin coverage functions may write their own coverage files.

## Dependencies and Integration Points

Dependencies include gcov runtime symbols, EOS logging, `PluginManager`, and dynamic-library symbol lookup. It integrates with signal handlers or manual hooks used by coverage test runs.

## Risks and Edge Cases

- Running complex C++ code in a signal handler can be unsafe if actually called from asynchronous signal context.
- Plugin coverage functions are optional and unchecked beyond null testing; plugin failures are not handled.
- `__gcov_dump()` availability depends on compiler/runtime and `COVERAGE_BUILD`.

## Test Signals

Coverage builds should verify gcov files update for the MGM and plugins, missing plugin symbols are skipped, and non-coverage builds log the expected message without link errors.
