# sources/distributed-fs/ceph-client/include/linux/cmpxchg-emu.h

Purpose: This header declares an emulated byte-sized compare-exchange helper for architectures that lack direct 1-byte or 2-byte cmpxchg operations and implement them through wider atomics.

Important APIs/types/functions: The exported API is `uintptr_t cmpxchg_emu_u8(volatile u8 *p, uintptr_t old, uintptr_t new)`.

Control flow: Architecture or generic atomic code calls the helper when it needs cmpxchg semantics for an 8-bit target. The implementation performs the emulation, typically using a 32-bit cmpxchg around the containing word.

State and persistence behavior: No state is stored in the header. State mutation is the atomic update of the byte pointed to by `p`, returning the observed old value in cmpxchg style.

Dependencies and integration points: It relies on integer and `u8` types from including contexts and integrates with architecture atomic implementations and generic cmpxchg fallback code.

Risks: Emulation must preserve atomicity for the target byte without corrupting neighboring bytes. Alignment, endian layout, and volatile access rules are critical. Return type width must match generic cmpxchg expectations.

Test signals: Atomic cmpxchg selftests on architectures using the fallback, KCSAN stress, unaligned/neighbor-byte tests where allowed, and build coverage for small-width atomics validate behavior.
