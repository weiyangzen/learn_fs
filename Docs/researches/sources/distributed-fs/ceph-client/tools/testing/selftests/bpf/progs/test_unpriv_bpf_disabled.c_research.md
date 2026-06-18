<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_unpriv_bpf_disabled.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_unpriv_bpf_disabled.c

## Purpose

Tests behavior when unprivileged BPF is disabled across common map types and output helpers. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 83 source lines. BPF sections: `.maps`, `.maps`, `.maps`, `.maps`, `.maps`, `.maps`, `.maps`, `perf_event`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`, `BPF_MAP_TYPE_HASH`, `BPF_MAP_TYPE_PERCPU_ARRAY`, `BPF_MAP_TYPE_PERCPU_HASH`, `BPF_MAP_TYPE_PERF_EVENT_ARRAY`, `BPF_MAP_TYPE_PROG_ARRAY`, `BPF_MAP_TYPE_RINGBUF`. Important helper/kfunc surface: `bpf_get_current_pid_tgid`, `bpf_helpers`, `bpf_misc`, `bpf_perf_event_output`, `bpf_ringbuf_output`, `bpf_tracing`. Important C functions and entry points include `sys_nanosleep_enter`, `handle_perf_event`. Notable globals or configuration/result fields include `__u32 perfbuf_val = 0`; `__u32 ringbuf_val = 0`; `int test_pid`; `int sys_nanosleep_enter(void *ctx)`; `int handle_perf_event(void *ctx)`.

## Control Flow

A perf-event program touches array, percpu, hash, ringbuf, perfbuf, and prog-array maps and emits through output helpers.

## State And Persistence Behavior

Several maps persist trivial values and output buffers. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Privilege gating must reject or allow operations consistently without exposing restricted helpers to unprivileged loaders. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run under configured `unprivileged_bpf_disabled` settings and compare expected load/operation failures. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_unpriv_bpf_disabled.c -->
