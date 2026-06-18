# sources/distributed-fs/ceph-client/arch/mips/lib/bitops.c

Purpose: provides fallback atomic bit operations for MIPS configurations without faster inline LL/SC implementations.

Important APIs/functions: exports `__mips_set_bit`, `__mips_clear_bit`, `__mips_change_bit`, `__mips_test_and_set_bit_lock`, `__mips_test_and_clear_bit`, and `__mips_test_and_change_bit`; also defines `__mips_xor_is_negative_byte`.

Control flow: each operation computes the target word and bit mask, disables local IRQs, updates memory, optionally captures old bit state, then restores IRQs.

State and persistence: mutates caller-provided memory only; no global state.

Dependencies and integration: used by generic bitops macros when no faster MIPS path is available; exports support modules and core code.

Risks: IRQ masking gives local atomicity but not cross-CPU atomicity unless these routines are only selected for appropriate uniprocessor/no-LLSC contexts. Volatile memory operations are intentionally simple.

Test signals: bitops selftests, lock bit behavior, SMP configuration review, and module symbol resolution.
