<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/radix-tree.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/radix-tree.h

## Purpose

`linux/radix-tree.h` adapts the kernel radix-tree header for userspace tests and instruments RCU-delayed frees.

## Important APIs, Types, and Functions

It includes the kernel radix-tree header, declares `kmalloc_verbose` and `test_verbose`, defines `trace_call_rcu()` to optionally print delayed frees before calling `call_rcu`, defines `printv()`, and remaps `call_rcu(x, y)` to `trace_call_rcu(x, y)`.

## Control Flow and State

Wrapper flow is limited to RCU callback tracing and verbosity-controlled printing. Actual radix-tree behavior comes from generated `radix-tree.c` and shared allocation stubs.

## Dependencies and Integration Points

It depends on Userspace RCU, kernel radix-tree headers, `linux.c` slab stubs, and `shared.mk` generation of `radix-tree.c`.

## Risks and Test Signals

Risks include callback macro recursion, verbosity side effects, or divergence from kernel RCU timing. Passing radix-tree/xarray tests and optional verbose output validate the shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/radix-tree.h -->
