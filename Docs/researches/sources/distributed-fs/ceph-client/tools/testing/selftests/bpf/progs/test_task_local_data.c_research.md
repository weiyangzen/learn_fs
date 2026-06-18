<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_task_local_data.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_task_local_data.c

## Purpose

Checks task local storage helper wrappers from `task_local_data.bpf.h` in a syscall program. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 65 source lines. BPF sections: `syscall`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_get_current_task_btf`, `bpf_helpers`. Important C functions and entry points include `task_main`. Notable globals or configuration/result fields include `int test_value0`; `int test_value1`; `int task_main(void *ctx)`.

## Control Flow

`task_main` gets the current task, creates or reads task-local values keyed by structures, and updates result globals.

## State And Persistence Behavior

`test_value0` and `test_value1` are user-visible results; task local storage persists on the task while it exists. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Task lifetime, storage creation flags, and BTF task pointer typing are the main verifier/runtime concerns. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run the syscall program and verify expected local-storage values are observed. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_task_local_data.c -->
