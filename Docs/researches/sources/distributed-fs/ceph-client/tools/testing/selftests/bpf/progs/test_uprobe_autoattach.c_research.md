<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_uprobe_autoattach.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_uprobe_autoattach.c

## Purpose

Covers libbpf uprobe auto-attach section syntax for current executable and libc symbols. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 117 source lines. BPF sections: `uprobe`, `uprobe//proc/self/exe:autoattach_trigger_func`, `uretprobe//proc/self/exe:autoattach_trigger_func`, `uprobe/libc.so.6:fopen`, `uretprobe/libc.so.6:fopen`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_core_read`, `bpf_get_current_pid_tgid`, `bpf_helpers`, `bpf_misc`, `bpf_tracing`. Important C functions and entry points include `handle_uprobe_noautoattach`, `BPF_UPROBE`, `BPF_URETPROBE`, `BPF_UPROBE`, `BPF_URETPROBE`. Notable globals or configuration/result fields include `int uprobe_byname_parm1 = 0`; `int uprobe_byname_ran = 0`; `int uretprobe_byname_rc = 0`; `int uretprobe_byname_ret = 0`; `int uretprobe_byname_ran = 0`; `int uprobe_byname2_ran = 0`; `int uretprobe_byname2_ran = 0`; `int test_pid`.

## Control Flow

Autoattach programs target `/proc/self/exe:autoattach_trigger_func` and `libc.so.6:fopen`; handlers filter by pid and store arguments/results.

## State And Persistence Behavior

Globals capture pid, argument values, return values, and hit counters. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Path resolution, PIE/ASLR, libc symbol lookup, and return-probe pairing can fail independently. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Trigger the local function and `fopen`, then assert corresponding entry/return globals. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_uprobe_autoattach.c -->
