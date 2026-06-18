<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_uprobe.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_uprobe.c

## Purpose

Tests uprobe/uretprobe section parsing, symbol version suffixes, and manual uprobe attach paths. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 99 source lines. BPF sections: `uprobe/./liburandom_read.so:urandlib_api_sameoffset`, `uprobe/./liburandom_read.so:urandlib_api_sameoffset@LIBURANDOM_READ_1.0.0`, `uretprobe/./liburandom_read.so:urandlib_api_sameoffset@@LIBURANDOM_READ_2.0.0`, `uprobe`, `uprobe`, `uprobe`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_get_current_pid_tgid`, `bpf_helpers`, `bpf_tracing`. Important C functions and entry points include `BPF_UPROBE`, `BPF_UPROBE`, `BPF_URETPROBE`, `BPF_UPROBE`, `BPF_UPROBE`, `BPF_UPROBE`. Notable globals or configuration/result fields include `int test1_result = 0`; `int test2_result = 0`; `int test3_result = 0`; `int test4_result = 0`; `int BPF_UPROBE(test1)`; `int BPF_UPROBE(test2)`; `int BPF_URETPROBE(test3, int ret)`; `int BPF_UPROBE(test4)`.

## Control Flow

Programs attach to versioned and unversioned symbols in `liburandom_read.so` plus generic `uprobe` sections and update pid/result globals.

## State And Persistence Behavior

Global counters/results identify which probes fired for the current pid. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

ELF symbol version syntax with `@` and `@@` must be parsed correctly by libbpf auto-attach. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Call the library symbols and verify the expected uprobe and uretprobe programs fired. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_uprobe.c -->
