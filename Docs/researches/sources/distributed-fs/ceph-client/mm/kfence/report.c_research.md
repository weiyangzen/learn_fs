# sources/distributed-fs/ceph-client/mm/kfence/report.c

## Purpose

`report.c` is KFENCE's diagnostics and fault-policy implementation. It formats memory-safety reports, prints stack and object metadata, handles the `kfence.fault` boot policy, taints or panics the kernel when configured, and exposes object information to printk slab diagnostics.

## Important APIs, Types, and Functions

Important state is `kfence_fault`, set by `early_kfence_fault()` from `kfence.fault=report|oops|panic`. Core functions are `seq_con_printf()`, `get_stack_skipnr()`, `kfence_print_stack()`, `kfence_print_object()`, `print_diff_canary()`, `kfence_report_error()`, `kfence_handle_fault()`, and optional `__kfence_obj_info()`.

## Control Flow

KFENCE core calls `kfence_report_error()` with the bad address, access type, registers if available, metadata when known, and error type. The function saves or reconstructs a stack trace, disables lockdep around printk, prints a type-specific header for OOB, UAF, corruption, invalid access, or invalid free, prints the current stack, prints object allocation/free details under the metadata lock, emits footer information and tracepoint, taints the kernel, and returns the configured fault action. `kfence_handle_fault()` then ignores, BUGs, or panics according to that action. `kfence_print_object()` also serves debugfs by writing to a `seq_file`.

## State and Persistence Behavior

The report file owns only the boot-time `kfence_fault` policy. It reads persistent metadata and stack tracks from `struct kfence_metadata`. Reports call `trace_error_report_end(ERROR_DETECTOR_KFENCE, address)` and add `TAINT_BAD_PAGE`.

## Dependencies and Integration Points

It integrates with KFENCE core fault/free paths, debugfs object listing, printk and seq_file output, stacktrace helpers, lockdep, panic handling, trace events, slab object info (`struct kmem_obj_info`), and optional arch symbol prefixes.

## Risks and Edge Cases

Reporting can occur in printk-unfriendly contexts, so the code knowingly accepts printk risk while suppressing lockdep noise. Stack trimming depends on symbol-prefix heuristics and can be affected by compiler optimization. Canary bytes are redacted unless pointer hashing is disabled to avoid leaking memory.

## Test Signals

Signals include KUnit report matching for all error types, `kfence.fault=oops|panic` boot behavior, debugfs object output, slab object diagnostic integration through `__kfence_obj_info()`, tracepoint emission, and canary corruption output with and without `no_hash_pointers`.
