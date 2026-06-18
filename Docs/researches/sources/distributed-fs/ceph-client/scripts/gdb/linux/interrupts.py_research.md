# sources/distributed-fs/ceph-client/scripts/gdb/linux/interrupts.py

## Purpose
`interrupts.py` implements `lx-interruptlist`, a `/proc/interrupts`-style GDB command for inspecting IRQ descriptors, per-CPU counts, architecture interrupt counters, and clock/error interrupt statistics.

## Important APIs, Types, and Functions
`show_irq_desc()` loads IRQ descriptors from the `sparse_irqs` maple tree, filters hidden/chained/no-count descriptors, and formats chip, hardware IRQ, trigger level, descriptor name, and actions. Architecture helpers include `x86_show_interupts()`, `arm_common_show_interrupts()`, `aarch64_show_interrupts()`, and `arch_show_interrupts()`.

## Control Flow
`LxInterruptList.invoke()` calculates field width from `nr_irqs`, prints CPU headers, iterates IRQ numbers, and appends architecture-specific lines. Descriptor lookup goes through `mapletree.mtree_load()`, then count collection uses `cpus.each_online_cpu()` and `cpus.per_cpu()`.

## State and Persistence Behavior
The script mutates no kernel state. Output is a best-effort snapshot of live counters and descriptor pointers, with no locking or consistency guarantee.

## Dependencies and Integration Points
It depends on generated constants, CPU helpers, maple tree helpers, and kernel IRQ symbols such as `nr_irqs`, `sparse_irqs`, `irq_stat`, `ipi_desc`, and `tick`/machine-check counters depending on architecture.

## Risks and Test Signals
The action-chain loop is fragile around missing `struct irqaction` debug info and corrupted `next` pointers. Architecture support is explicit; unsupported targets raise an error. Test by comparing with `/proc/interrupts` on x86, arm, and arm64 kernels and by exercising sparse IRQ configurations.
