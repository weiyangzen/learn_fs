# sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/builtin_func/Kconfig

## Purpose
This fixture tests Kconfig preprocessor built-in functions.

## Important APIs, Types, and Functions
It invokes `$(info,...)`, `$(warning-if,...)`, `$(error-if,...)`, `$(shell,...)`, `$(filename)`, and `$(lineno)`, and defines a shorthand `warning = $(warning-if,y,$(1))`.

## Control Flow
Parsing expands each built-in; info prints to stdout, warning prints to stderr with file/line, false `error-if` is a no-op, shell output is transformed by trimming trailing newlines and replacing internal newlines with spaces.

## State and Persistence
No config symbols are defined; output streams are the observable state.

## Dependencies and Integration Points
Targets `preprocess.c` built-ins and parser line/file tracking.

## Risks and Edge Cases
The shell command behavior depends on host `echo`/`printf` but uses simple POSIX-like commands.

## Test Signals
The paired test checks stdout and regex-matched stderr.
