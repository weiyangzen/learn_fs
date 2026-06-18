# sources/distributed-fs/ceph-client/lib/test_bitops.c

## Purpose
Provides a small module selftest for basic bit operations and order helpers. It exercises set/clear/find behavior on a global bitmap and validates `get_count_order()` and `get_count_order_long()` for selected boundary values.

## APIs, Control Flow, and State
The module declares enum bit positions, a global `DECLARE_BITMAP(g_bitmap, BITOPS_LENGTH)`, 32-bit order test vectors, and 64-bit vectors under `CONFIG_64BIT`. `test_bitops_startup()` sets several bits, checks order helper results, clears those bits, verifies `find_first_bit()` returns the sentinel end position, runs `test_fns()`, and logs completion. `test_fns()` allocates 10,000 random words, repeatedly calls `fns(word, n)` for every `n < BITS_PER_LONG`, stores the volatile result to prevent optimization, and logs elapsed time. Exit is a no-op.

Persistent state is only the module-global test bitmap while the module is loaded; allocated random buffers are freed automatically via cleanup attribute.

## Dependencies, Integration, Risks, and Tests
Depends on bitops, random bytes, ktime, slab allocation, module init/exit, and cleanup attributes. Integration is with kernel lib selftests and CI module loading. Risks include warning-only failures instead of a formal aggregate result, limited coverage of order-helper inputs, performance timing variability, and dependence on architecture word size for 64-bit vectors. Test signals are module logs: order mismatch warnings, unexpected set-bit errors, and the `fns` timing line.
