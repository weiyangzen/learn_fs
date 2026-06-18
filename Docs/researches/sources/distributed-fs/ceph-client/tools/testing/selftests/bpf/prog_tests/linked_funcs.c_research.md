
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_funcs.c

## Purpose

`linked_funcs.c` validates linked BPF functions and weak function behavior across two manually autoloaded raw tracepoint handlers.

## Important APIs, Types, and Functions

It uses `linked_funcs.skel.h`, enables autoload for `handler1` and `handler2`, sets rodata `my_tid`, BSS `syscall_id`, loads/attaches the skeleton, triggers `SYS_getpgid`, and checks BSS outputs.

## Control Flow and Data Flow

The handlers are optional sections by default, so the harness enables them before load. After attach, the syscall trigger causes both handlers to execute linked functions. The test asserts computed output values, captured syscall context, and weak function results.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is rodata filter TID, BSS syscall id, and output fields. Dependencies include raw tracepoint attach, syscall availability, and linked subprogram/weak symbol support. Integration is BPF static linking across functions and optional program autoload. Risks are missing trigger due to TID/syscall filtering or changes in paired BPF computations. Test signals are `output_val1 == 4000`, `output_ctx1 == SYS_getpgid`, `output_weak1 == 42`, `output_val2 == 6000`, `output_ctx2 == SYS_getpgid`, and `output_weak2 == 0`.
