# sources/distributed-fs/ceph-client/lib/cmpxchg-emu.c

## Purpose

`sources/distributed-fs/ceph-client/lib/cmpxchg-emu.c` emulates one-byte `cmpxchg()` for architectures that can atomically compare/exchange 32-bit words but not 8-bit bytes.

## Important APIs, Types, and Functions

The exported function is `cmpxchg_emu_u8(volatile u8 *p, uintptr_t old, uintptr_t new)`. The helper union `u8_32` overlays four bytes and one 32-bit word.

## Control Flow

The function aligns the target byte pointer down to a 32-bit word, computes the byte index, reads the word with `READ_ONCE`, and loops. Each iteration checks whether the target byte equals `old`; if not, it returns the observed byte. Otherwise it modifies only that byte in a copied word, instruments an atomic read/write of one byte, and calls 32-bit `cmpxchg()` under `data_race()`. The loop retries until the full word compare/exchange succeeds.

## State and Persistence Behavior

There is no local persistent state. The function atomically mutates the containing 32-bit memory word and returns the old byte value according to cmpxchg semantics.

## Dependencies and Integration Points

Dependencies include atomic cmpxchg support, `READ_ONCE`, KCSAN instrumentation, and generic cmpxchg emulation headers. It integrates with generic atomics on architectures without byte cmpxchg.

## Risks and Edge Cases

The containing 32-bit word must be safely accessible and properly aligned for 32-bit atomics; bytes near page or object boundaries can still touch neighboring bytes in the same word. Concurrent writers to other bytes in the word can cause retries. Endianness is handled by the union byte indexing in native memory order but must match intended byte address semantics.

## Test Signals

Signals include successful byte exchange, mismatch return without store, concurrent updates to adjacent bytes, all four byte offsets, KCSAN/instrumentation sanity, and fault/alignment expectations on the target architecture.

## Read Coverage

Source read size: 45 lines, 1086 bytes.
