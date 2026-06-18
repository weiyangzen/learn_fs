# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/atomic.h

Purpose: Hexagon atomic operations implemented around compare-exchange loops.

Important APIs/types/functions: functions: `arch_atomic_set`, `arch_atomic_fetch_add_unless`; macros: `_ASM_ATOMIC_H`, `arch_atomic_set_release(v,`, `arch_atomic_read(v)`, `ATOMIC_OP(op)`, `ATOMIC_OP_RETURN(op)`, `ATOMIC_FETCH_OP(op)`, `ATOMIC_OPS(op)`, `arch_atomic_add_return`, `arch_atomic_sub_return`, `arch_atomic_fetch_add`, `arch_atomic_fetch_sub`, `arch_atomic_fetch_and`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `linux/types.h`, `asm/cmpxchg.h`, `asm/barrier.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.
