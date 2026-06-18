# sources/cloud-native/ostree/src/libostree/ostree-kernel-args-private.h

## Purpose
This private header exposes the internal representation helpers for `OstreeKernelArgs` to libostree implementation files and tests. It is not a stable public API; it exists to inspect and manipulate the ordered multimap backing kernel argument handling.

## Important APIs, State, and Integration
It forward declares `OstreeKernelArgsEntry` and exposes accessors for the hash table (`_ostree_kernel_arg_get_kargs_table()`), ordered array (`_ostree_kernel_arg_get_key_array()`), entry key/value getters and setters, indexed key/value lookup, entry allocation, value cleanup, and `_ostree_kernel_args_equal()`. These functions mirror the concrete structures in `ostree-kernel-args.c`: a `GHashTable` from key to entry arrays and a `GPtrArray` preserving argument order.

## Dependencies, Risks, and Tests
The header depends only on `ostree-kernel-args.h` and GLib declarations. Integration points are tests, deployment code needing equality checks, and internals that preserve ordering while replacing/deleting entries. Risk is representation leakage: callers can observe or mutate structures in ways that break ownership invariants if used outside controlled code. Test signals should include duplicate keys, NULL values, order-sensitive equality, and mutation through public APIs rather than direct private mutation.
