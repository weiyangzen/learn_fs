# sources/distributed-fs/ceph-client/arch/arm/include/asm/bitops.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/bitops.h` provides ARM bit manipulation
primitives, including atomic bitops, non-atomic local bitops, find/ffz helpers, and little-endian
operation aliases. It is part of the ARM kernel-architecture compatibility layer imported in the
Ceph client source tree, so its direct consumers are kernel architecture, MM, interrupt, driver, and
board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `ATOMIC_BITOP`, `set_bit`, `clear_bit`, `change_bit`, `test_and_set_bit`,
`test_and_clear_bit`, `test_and_change_bit`, `find_first_zero_bit`, `find_next_zero_bit`,
`find_first_bit`, `find_next_bit`, `find_first_zero_bit_le`, `find_next_zero_bit_le`,
`find_next_bit_le`; functions/prototypes: `BIT_MASK`, `BIT_WORD`, `raw_local_irq_save`,
`raw_local_irq_restore`, `_set_bit`, `_clear_bit`, `_change_bit`, `_test_and_set_bit`,
`_test_and_clear_bit`, `_test_and_change_bit`, `_find_first_zero_bit_le`, `_find_first_bit_le`,
`_find_next_bit_le`, `_find_first_zero_bit_be`, `_find_first_bit_be`, `_find_next_bit_be`,
`_find_next_zero_bit_le`. The file is 278 lines / 7732 bytes, and the exported surface is primarily
an include-time contract for other kernel files.

### Control Flow
Ordering-sensitive helpers place barriers around the architectural operation so SMP, DMA, exception
return, or device-observable side effects occur in the required sequence. IRQ/FIQ helpers are
normally used from early boot, interrupt entry, or low-level driver paths where callers must already
understand local interrupt state.

### State, Persistence, And Dependencies
External state or implementation hooks include `_set_bit`, `_clear_bit`, `_change_bit`,
`_test_and_set_bit`, `_test_and_clear_bit`, `_test_and_change_bit`. There is no userspace filesystem
persistence in this file; persistence is either kernel memory, CPU register state, hardware register
state, or generated ABI values. Direct includes are `linux/compiler.h`, `linux/irqflags.h`,
`asm/barrier.h`, `asm-generic/bitops/non-atomic.h`, `asm-generic/bitops/__fls.h`, `asm-
generic/bitops/__ffs.h`, `asm-generic/bitops/fls.h`, `asm-generic/bitops/ffs.h`, `asm-
generic/bitops/builtin-__fls.h`, `asm-generic/bitops/builtin-__ffs.h`, and 9 more. It integrates
with generic Linux ARM architecture code through include-time contracts rather than a standalone
translation unit. Barrier correctness depends on ARM memory-model semantics and the generic Linux
ordering APIs. Interrupt-related declarations integrate with generic irqchip, exception entry, and
per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `bitops.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
missing or misplaced barriers can create SMP, DMA, or device-ordering races that are hard to
reproduce; callers must preserve interrupt-state assumptions and avoid using low-level helpers from
preemptible or wrong-context paths.

### Test Signals
run SMP, lockdep, memory-ordering, and DMA stress tests; exercise boot, interrupt entry/exit, and
irqchip paths; ensure all include users still build with sparse/objtool-style diagnostics where
available.
