# sources/distributed-fs/ceph-client/tools/perf/tests/kallsyms-split.c

## Purpose
Regression test ensuring a bad module symbol interleaved in `/proc/kallsyms` does not incorrectly split the main kernel kallsyms map.

## Important APIs, Types, and Functions
- Static fake proc files provide `version`, `modules`, and `kallsyms` content. The kallsyms stream includes main kernel symbols, a module, and a module `u bad_symbol` at an address inside the kernel range.
- `create_proc_dir()` builds `/tmp/perf-test.XXXXXX/proc` and writes the fake proc files.
- `remove_proc_dir()` removes those files/directories and is installed as a signal handler.
- `test__kallsyms_split()` initializes a `struct machine` rooted at the fake directory, creates kernel maps, forces kallsyms loading by setting `symbol_conf` flags, loads the kernel map, and validates map count and symbol ownership.

## Control Flow
The test creates the fake proc root, registers cleanup handlers, initializes the machine with that root, creates kernel maps, sets `ignore_vmlinux`, `ignore_vmlinux_buildid`, and `allow_aliases`, then loads the kernel map from fake kallsyms. It expects exactly two maps (main kernel plus module) and verifies `main_symbol3` resolves to `machine__kernel_map(&m)`, not a split or module map.

## State and Persistence
Creates temporary files under `/tmp` and removes them on normal exit or selected signals. Mutates global `symbol_conf` flags and a stack-local `struct machine`. No artifact should remain after cleanup.

## Dependencies and Integration Points
Exercises machine kernel map creation, DSO/map/symbol loading, fake root support, kallsyms parsing, module range handling, and test registration via `DEFINE_SUITE("split kallsyms", kallsyms_split)`.

## Risks and Edge Cases
- Signal-handler cleanup calls filesystem functions that are not strictly async-signal-safe, but this is test cleanup code.
- The temporary root uses a static template modified by `mkdtemp()`, so repeated invocations in the same process rely on cleanup resetting only `root_dir`, not the template string.
- Global `symbol_conf` mutations may affect later tests unless the broader suite resets them.

## Test Signals
Passing shows the fake mixed kallsyms/module input yields two maps and keeps `main_symbol3` in the main kernel map. Failure messages distinguish setup, load, map-count, and symbol-map mismatches.
