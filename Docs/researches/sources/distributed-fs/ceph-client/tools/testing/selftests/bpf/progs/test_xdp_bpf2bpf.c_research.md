<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_bpf2bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_bpf2bpf.c

## Purpose

Tests tracing of an XDP BPF function via fentry/fexit and XDP perf output. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 66 source lines. BPF sections: `license`, `.maps`, `fentry/FUNC`, `fexit/FUNC`. Map types declared or referenced: `BPF_MAP_TYPE_PERF_EVENT_ARRAY`. Important helper/kfunc surface: `bpf_helpers`, `bpf_tracing`, `bpf_xdp_get_buff_len`, `bpf_xdp_output`. Important C functions and entry points include `BPF_PROG`, `BPF_PROG`. Notable globals or configuration/result fields include `__u64 test_result_fentry = 0`; `int BPF_PROG(trace_on_entry, struct xdp_buff *xdp)`; `__u64 test_result_fexit = 0`; `int BPF_PROG(trace_on_exit, struct xdp_buff *xdp, int ret)`.

## Control Flow

Entry and exit programs inspect `xdp_buff`, use `bpf_xdp_get_buff_len`, and can emit metadata through `perf_buf_map`.

## State And Persistence Behavior

`test_result_fentry` and `test_result_fexit` record observations. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Target function prototype must match BTF, and fexit return value handling must be correct. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run the target XDP program and assert both tracing result globals. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_bpf2bpf.c -->
