# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/bitops.h

Purpose: implements PowerPC atomic bit operations and bit-number conversion helpers while importing generic non-atomic, little-endian, hweight, and filesystem bitmap helpers.

Important APIs/types/functions: defines `PPC_BIT*` masks, `set_bits`, `clear_bits`, `change_bits`, `arch_set_bit`, `arch_clear_bit`, `arch_clear_bit_unlock`, `arch_change_bit`, `arch_test_and_set_bit`, lock and clear/change variants, `arch_xor_unlock_is_negative_byte`, `arch___clear_bit_unlock`, `fls`, `fls64`, and hweight declarations for PPC64.

Control flow: modifying operations use `PPC_LLARX/PPC_STLCX` retry loops. Clear paths optimize constant masks on PPC32 with `rlwinm` when possible. Test-and-set/clear/change return the old masked bit state.

State and persistence: state is caller-provided bitmaps or words. The header stores nothing.

Dependencies and integration points: requires inclusion through `<linux/bitops.h>`, plus asm compatibility, sync, barrier, and generic bitops headers. Used by scheduler, filesystems, locks, memory management, and drivers.

Risks: PowerPC big-endian word bit numbering differs from byte-oriented little-endian bitmap expectations. Barrier variants must match lock/unlock semantics. Constant-mask optimization must preserve semantics for wrapping masks and PPC32 instruction constraints.

Test signals: generic bitops self-tests, ext2/ext4 bitmap tests on big-endian PowerPC, lock bit stress, KCSAN concurrency tests, and compile checks for PPC32 and PPC64.
