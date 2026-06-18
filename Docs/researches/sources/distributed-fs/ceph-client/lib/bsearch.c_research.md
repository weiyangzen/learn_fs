# sources/distributed-fs/ceph-client/lib/bsearch.c

## Purpose

`sources/distributed-fs/ceph-client/lib/bsearch.c` is the non-inline exported wrapper for the generic kernel binary search helper. It provides a stable symbol for modules or code that cannot use only the inline implementation.

## Important APIs, Types, and Functions

The only runtime function is `bsearch(const void *key, const void *base, size_t num, size_t size, cmp_func_t cmp)`, exported with `EXPORT_SYMBOL` and marked `NOKPROBE_SYMBOL`. It delegates directly to `__inline_bsearch()` from `<linux/bsearch.h>`.

## Control Flow

The wrapper performs no local validation or looping. It receives the search key, base pointer, element count, element size, and comparator, then returns the result of `__inline_bsearch()`. The comparator controls ordering and equality.

## State and Persistence Behavior

There is no owned state. The function reads caller-owned array memory and returns a pointer into that array or `NULL`.

## Dependencies and Integration Points

Dependencies are `linux/bsearch.h`, `linux/export.h`, and `linux/kprobes.h`. Kernel subsystems and modules use this symbol when they need a generic binary search over sorted arrays without duplicating search logic.

## Risks and Edge Cases

Correctness depends entirely on the caller providing sorted input, a stable comparator, a nonzero element size, and a valid memory range. The wrapper cannot detect comparator contract violations or overflow in caller-provided layout.

## Test Signals

Signals are generic bsearch tests over empty arrays, one-element arrays, missing keys, first/last matches, key type different from element type, and module link coverage for the exported symbol. Kprobe blacklisting should keep tracing from instrumenting the wrapper.

## Read Coverage

Source read size: 36 lines, 1247 bytes.
