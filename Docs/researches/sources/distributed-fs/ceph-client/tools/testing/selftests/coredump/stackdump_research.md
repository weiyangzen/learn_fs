# sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/stackdump

## Purpose

`stackdump` is a shell helper used as a pipe-style `core_pattern` program. It records stack pointer values from every thread of a crashing process into a file.

## Important APIs, Types, and Functions

It accepts crashing process id and output path arguments, uses `mktemp`, iterates `/proc/$pid/task/*`, extracts each task id with `basename`, reads `/proc/$tid/stat`, and appends field 29 via `awk`.

## Control Flow

The script creates a temporary file, appends one stack pointer value per task, then atomically moves the temporary file to the requested output file.

## State and Persistence Behavior

It persists the final stack-value list at the supplied output path and leaves no intended temporary file after `mv`. It reads transient `/proc` task state while the kernel is invoking the pipe helper for a crashing process.

## Dependencies and Integration Points

It depends on procfs task directories, `/proc/<tid>/stat` field layout, POSIX shell tools, and `stackdump_test.c` setting `core_pattern` to invoke it with `%P`.

## Risks and Edge Cases

Task directories can disappear if process teardown races the script, and `/proc/<tid>/stat` parsing by whitespace is fragile if kernel stat layout changes. The script assumes field 29 is the stack pointer.

## Test Signals

The paired test expects the output file to exist, contain one nonzero stack pointer per thread plus the main task, and have exactly `1 + NUM_THREAD_SPAWN` lines.
