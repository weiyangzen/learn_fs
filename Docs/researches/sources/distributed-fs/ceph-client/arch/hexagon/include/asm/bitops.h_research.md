# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/bitops.h

Purpose: Hexagon bit operations and generic bitops integration.

Important APIs/types/functions: functions: `test_and_clear_bit`, `test_and_set_bit`, `test_and_change_bit`, `clear_bit`, `set_bit`, `change_bit`, `arch___clear_bit`, `arch___set_bit`, `arch___change_bit`, `arch___test_and_clear_bit`, `arch___test_and_set_bit`, `arch___test_and_change_bit`, `arch_test_bit`, `arch_test_bit_acquire`, `ffz`, `fls`, `ffs`, `__ffs`; macros: `_ASM_BITOPS_H`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `linux/compiler.h`, `asm/byteorder.h`, `asm/atomic.h`, `asm/barrier.h`, `asm-generic/bitops/lock.h`, `asm-generic/bitops/non-instrumented-non-atomic.h`, `asm-generic/bitops/fls64.h`, `asm-generic/bitops/sched.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.
