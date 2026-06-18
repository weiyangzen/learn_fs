<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_usdt_multispec.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_usdt_multispec.c

## Purpose

Tests attaching one USDT program to a multi-spec probe definition. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 30 source lines. BPF sections: `usdt//proc/self/exe:test:usdt_100`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_get_current_pid_tgid`, `bpf_helpers`. Important C functions and entry points include `BPF_USDT`. Notable globals or configuration/result fields include `int usdt_100_called`; `int usdt_100_sum`; `int BPF_USDT(usdt_100, int x)`.

## Control Flow

The program filters current pid and records that the `usdt_100` probe fired.

## State And Persistence Behavior

A small set of globals records pid and hit state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Libbpf must resolve multiple USDT specs for one logical probe without duplicate or missing attachments. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run the executable probe and assert exactly the expected hits. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_usdt_multispec.c -->
