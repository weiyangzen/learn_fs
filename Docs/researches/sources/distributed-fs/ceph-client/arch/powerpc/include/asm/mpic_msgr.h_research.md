# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpic_msgr.h

Purpose: declares MPIC message-register allocation/control APIs and inline register accessors.

Important APIs/types/functions: `struct mpic_msgr` stores base register pointer, message-enable register pointer, IRQ, in-use flag, lock, and register number. APIs include `mpic_msgr_get`, `mpic_msgr_put`, `mpic_msgr_enable`, `mpic_msgr_disable`, `mpic_msgr_write`, `mpic_msgr_read`, `mpic_msgr_clear`, `mpic_msgr_set_destination`, and `mpic_msgr_get_irq`.

Control flow: clients acquire a message register, set destination CPU, enable it, write a 32-bit message to trigger an interrupt, read/clear it in the handler, then disable and release it.

State and persistence: message-register allocation state is tracked by `in_use` and protected by `lock` in implementation. Hardware message, enable, destination, and IRQ state persists in MPIC registers.

Dependencies and integration points: depends on spinlocks, SMP hard CPU IDs, big-endian MMIO accessors, and MPIC interrupt routing.

Risks: destination uses hardware CPU numbering derived from Linux CPU IDs; wrong mapping misroutes messages. Reading clears interrupts, so handlers must preserve message values before acknowledging.

Test signals: allocate all valid message registers, verify busy/error paths, send messages between CPUs, confirm IRQ clearing on read, and test hotplug destination remapping.
