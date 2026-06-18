# sources/distributed-fs/ceph-client/kernel/trace/trace_probe_tmpl.h

## Purpose

`trace_probe_tmpl.h` is the reusable inline runtime for executing parsed probe fetch programs. Callers define source-specific front-end fetch logic and include this template for common store, dynamic sizing, bitfield, and array behavior. The complete 275-line file was read.

## Important APIs, Types, and Functions

Important helpers are `fetch_store_raw()`, `fetch_apply_bitfield()`, `fetch_store_symstrlen()`, `fetch_store_symstring()`, `process_common_fetch_insn()`, `process_fetch_insn_bottom()`, `__get_data_size()`, and `store_trace_args()`.

## Control Flow

`process_fetch_insn_bottom()` walks optional dereferences, stores raw values, memory, user memory, kernel strings, user strings, or symbol strings, applies an optional bitfield transform, and loops for arrays. `dest == NULL` computes dynamic string storage. `store_trace_args()` primes dynamic `__data_loc` fields and advances the dynamic data pointer as strings are stored.

## State and Persistence Behavior

No global state is owned. The template mutates caller-provided trace record payload and transient dynamic data placement.

## Dependencies and Integration Points

It integrates with kprobe, uprobe, fprobe, and eprobe fetch front ends. It depends on kallsyms, current task state, trace probe metadata, and caller-provided nofault memory access functions.

## Risks and Edge Cases

Risks include advancing past `FETCH_OP_END`, array loops over strings, stale data locations after faults, wrong bitfield base sizes, sizing/storage mismatch, and unchecked nofault read errors for raw memory stores.

## Test Signals

Test scalar loads, nested dereferences, user dereferences, string arrays, non-string arrays, bitfields, symbol strings, `$comm`, immediate strings, dynamic data bounds, and malformed instruction streams.
