# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_global_subprogs.c

## Purpose

`verifier_global_subprogs.c` tests global BPF subprogram verification across many program types. It checks when global functions are assumed valid from their prototype, when they are revalidated at call sites, and how ctx, memory, dynptr, tail-call, and unsupported-helper contracts cross global-call boundaries.

## Important APIs, Types, and Functions

The file includes BTF, tracing, `xdp_metadata.h`, kfunc declarations, and `err.h`. It defines a `syscall_prog_array` map for tail calls and struct_ops data for `test_1`. Helpers include `bpf_get_prandom_u32`, `bpf_tail_call`, `bpf_get_stack`, `bpf_dynptr_from_xdp`, `bpf_dynptr_data`, `bpf_dynptr_slice`, and `bpf_for`. Sections span raw_tp, syscall, tracepoint, tp_btf, kprobe, perf_event, iter, lsm, struct_ops, xdp, and tc.

## Control Flow

Some tests call simple global functions that are safe for any matching prototype, while others call global functions that do invalid map-value pointer math, use unsupported helpers, or dereference ctx after modification. The ctx-tag section passes program-specific contexts through subprogram prototypes and checks fixed-offset versus variable-offset behavior. Dynptr and XDP paths verify that global subprograms preserve helper contracts for packet-derived dynptr data.

## State and Persistence Behavior

Persistent state is limited to the prog-array map and struct_ops object. Verifier state includes global function validation summaries, argument type tags, ctx pointer offsets, dynptr initialization, map-value pointer ranges, and tail-call reachability.

## Dependencies and Integration Points

The file integrates with verifier global function analysis, BTF function prototype tags, many program-type context validators, tail calls, struct_ops loading, XDP dynptr helpers, and iterator/LSM support.

## Risks and Test Signals

Risks are assuming unsafe global functions are valid, over-revalidating safe globals, or losing program-type-specific ctx constraints at global-call boundaries. Test signals are verifier logs such as global function assumed valid, validating named functions, unsafe map pointer math, invalid memory access, modified ctx dereference, variable ctx access, and successful multi-program-type loads.
