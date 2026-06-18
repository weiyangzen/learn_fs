# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func_ctx_args.c

Research item: `subset-b-006814` ordinal `37`. Source size: 3618 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func_ctx_args.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `?kprobe`, `?raw_tp`, `?perf_event`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_core_read`, `bpf_misc`, `bpf_user_pt_regs_t`, `bpf_get_stack`, `bpf_target_s390`, `bpf_raw_tracepoint_args`, `bpf_perf_event_data`
- Declared maps: None visible in this compact source.
- Key local types: `struct type`, `struct bpf_user_pt_regs_t`, `struct hack`, `struct types`, `struct pt_regs`, `struct bpf_raw_tracepoint_args`, `struct bpf_perf_event_data`, `struct my_struct`
- Main functions/subprograms: `kprobe_typedef_ctx_subprog`, `kprobe_typedef_ctx`, `kprobe_struct_ctx_subprog`, `kprobe_resolved_ctx`, `kprobe_workaround_ctx_subprog`, `kprobe_workaround_ctx`, `raw_tp_ctx_subprog`, `raw_tp_ctx`, `raw_tp_writable_ctx_subprog`, `raw_tp_writable_ctx`, `perf_event_ctx_subprog`, `perf_event_ctx`, `subprog_ctx_tag`, `subprog_multi_ctx_tags`, `arg_tag_ctx_raw_tp`, `arg_tag_ctx_perf`, and 1 more.

## Control Flow
Entry programs are attached through `?kprobe`, `?raw_tp`, `?perf_event`. Control is organized around `kprobe_typedef_ctx_subprog`, `kprobe_typedef_ctx`, `kprobe_struct_ctx_subprog`, `kprobe_resolved_ctx`, `kprobe_workaround_ctx_subprog`, `kprobe_workaround_ctx`, `raw_tp_ctx_subprog`, `raw_tp_ctx`, `raw_tp_writable_ctx_subprog`, `raw_tp_writable_ctx`, `perf_event_ctx_subprog`, `perf_event_ctx`, and 5 more.. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`, `bpf/bpf_core_read.h`.
Local test dependencies: `vmlinux.h`, `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func_ctx_args.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `#include <bpf/bpf_core_read.h>` | `#include "bpf_misc.h"` | `char _license[] SEC("license") = "GPL";` | `__weak int kprobe_typedef_ctx_subprog(bpf_user_pt_regs_t *ctx)` | `return bpf_get_stack(ctx, &stack, sizeof(stack), 0);` | `SEC("?kprobe")` | `__success` | `* typedef user_pt_regs bpf_user_pt_regs_t;` | and 15 more marker lines
