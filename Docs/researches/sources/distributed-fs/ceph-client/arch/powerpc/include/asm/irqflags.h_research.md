# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/irqflags.h

Purpose: Provides the standard architecture IRQ flag include point by importing PowerPC `arch_local_save_flags()` and related helpers from `hw_irq.h`.

Important APIs, types, and functions: Includes `asm/hw_irq.h` for non-assembly code. It intentionally contains no additional logic.

Control flow: Generic code includes `irqflags.h`, then uses the arch-local IRQ save/restore/enable/disable functions defined by `hw_irq.h`.

State and persistence: No independent state.

Dependencies and integration points: Tight wrapper around `hw_irq.h` for generic Linux include conventions.

Risks: Any include-order or assembler mismatch would expose missing IRQ flag helpers. Behavior risk lives in `hw_irq.h`.

Test signals: Build generic locking/irq code, compile assembly and C users, and run IRQ save/restore nesting tests.
