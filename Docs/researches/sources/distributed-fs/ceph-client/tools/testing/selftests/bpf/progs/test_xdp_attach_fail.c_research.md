<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_attach_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_attach_fail.c

## Purpose

Tracepoint test for XDP link attach failure diagnostics. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 54 source lines. BPF sections: `.maps`, `tp/xdp/bpf_xdp_link_attach_failed`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_PERF_EVENT_ARRAY`. Important helper/kfunc surface: `bpf_helpers`, `bpf_perf_event_output`, `bpf_probe_read_kernel_str`, `bpf_xdp_link_attach_failed`. Important C functions and entry points include `tp__xdp__bpf_xdp_link_attach_failed`. Notable globals or configuration/result fields include `int tp__xdp__bpf_xdp_link_attach_failed(struct xdp_attach_error_ctx *ctx)`.

## Control Flow

The tracepoint handler reads the kernel error message string from attach-failure context and emits it through a perf event array.

## State And Persistence Behavior

`xdp_errmsg_pb` carries error records to user space. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Tracepoint context layout and bounded string copy length must match the kernel event. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Intentionally fail XDP attach and verify received error text. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_attach_fail.c -->
