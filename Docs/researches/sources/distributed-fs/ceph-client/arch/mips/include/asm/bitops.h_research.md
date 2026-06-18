<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bitops.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/bitops.h

**Purpose:** Implements MIPS atomic and non-atomic bit operations plus bit-scan helpers.

**Important APIs/types/functions:** Atomic APIs include `set_bit`, `clear_bit`, `change_bit`, `test_and_set_bit{,_lock}`, `test_and_clear_bit`, `test_and_change_bit`, and `xor_unlock_is_negative_byte`. Bit scan helpers include `__fls`, `__ffs`, `fls`, and `ffs`.

**Control flow:** Atomic operations use LL/SC loops with sync and R10000/Loongson workarounds when available; otherwise they call slower IRQ-disabled out-of-line functions. MIPSr2 constant-bit cases use `ins/ext` optimizations.

**State, dependencies, integration:** Depends on CPU feature macros, barriers, endian/generic bitops, and out-of-line helpers in bitops implementation files.

**Risks and test signals:** Lock semantics depend on before/after barriers, and bit numbering must match generic expectations. Test atomic bit lock/unlock on SMP, no-LLSC fallback, MIPSr2 constant optimizations, and 32/64-bit scan results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bitops.h -->
