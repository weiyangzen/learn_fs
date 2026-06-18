<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_urandom_usdt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_urandom_usdt.c

## Purpose

USDT auto-attach test for executable and shared-library probes with and without semaphores. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 70 source lines. BPF sections: `usdt/./urandom_read:urand:read_without_sema`, `usdt/./urandom_read:urand:read_with_sema`, `usdt/./liburandom_read.so:urandlib:read_without_sema`, `usdt/./liburandom_read.so:urandlib:read_with_sema`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_get_current_pid_tgid`, `bpf_helpers`. Important C functions and entry points include `BPF_USDT`, `BPF_USDT`, `BPF_USDT`, `BPF_USDT`. Notable globals or configuration/result fields include `int urand_pid`; `int urand_read_without_sema_call_cnt`; `int urand_read_without_sema_buf_sz_sum`; `int BPF_USDT(urand_read_without_sema, int iter_num, int iter_cnt, int buf_sz)`; `int urand_read_with_sema_call_cnt`; `int urand_read_with_sema_buf_sz_sum`; `int BPF_USDT(urand_read_with_sema, int iter_num, int iter_cnt, int buf_sz)`; `int urandlib_read_without_sema_call_cnt`.

## Control Flow

Four USDT programs attach to `urand` and `urandlib` providers and read current pid to filter hits.

## State And Persistence Behavior

Hit counters/globals are set by the probe programs. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

USDT semaphore activation and shared-object path resolution are the key integration points. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run the urandom test binary/library and verify all configured USDT probes fire. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_urandom_usdt.c -->
