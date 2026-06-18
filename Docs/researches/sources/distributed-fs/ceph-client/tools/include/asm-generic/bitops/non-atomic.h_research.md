# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/non-atomic.h

## Purpose

This header implements non-atomic bitmap mutation and test helpers for tools code.

## APIs, State, and Dependencies

Functions include `___set_bit`, `___clear_bit`, `___change_bit`, `___test_and_set_bit`, `___test_and_clear_bit`, `___test_and_change_bit`, and `_test_bit`. They compute `BIT_MASK` and `BIT_WORD`, cast the address to an unsigned long pointer, and update caller-owned memory directly. The header depends on `<linux/bits.h>` and has no own state.

## Risks and Test Signals

The functions are explicitly non-atomic and may be reordered, so racing callers need external locking. Volatile in the signature does not make compound operations atomic. Tests should cover bit positions across word boundaries, return values from test-and-modify helpers, and use through `<linux/bitops.h>` wrappers.
