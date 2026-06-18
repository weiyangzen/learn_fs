# sources/distributed-fs/ceph-client/kernel/irq/debugfs.c

## Purpose
`debugfs.c` exposes IRQ descriptor, irqdata, chip, affinity, and domain state through debugfs when `GENERIC_IRQ_DEBUGFS` is enabled. It also supports writing `trigger` to an IRQ file to inject an interrupt for debugging.

## Important APIs, types, and functions
Public helpers are `irq_debug_show_bits()`, `irq_debugfs_copy_devname()`, and `irq_add_debugfs_entry()`. Core functions are `irq_debug_show()`, `irq_debug_open()`, `irq_debug_write()`, and `irq_debugfs_init()`. Static descriptor tables map chip flags, irqdata states, descriptor settings, and internal states to names.

## Control flow
Initialization creates `/sys/kernel/debug/irq`, initializes domain debugfs, creates `irqs/`, then adds one file per active IRQ. `irq_debug_show()` locks the descriptor, prints handler, device, status, internal state, depth, wake depth, irqdata state, NUMA node, affinity masks, chip hierarchy, and domain-specific debug output. `irq_debug_write()` copies a small command and invokes `irq_inject_interrupt()` for the `trigger` command.

## State and persistence
Debugfs files persist while descriptors exist and the debugfs tree is mounted. `irq_debugfs_copy_devname()` duplicates a device name into `desc->dev_name`, later freed by `irq_remove_debugfs_entry()`. There is no durable persistence.

## Dependencies and integration points
This file integrates with debugfs, irqdomain debugfs, descriptor allocation/free in `irqdesc.c`, injection support selected by Kconfig, SMP affinity masks, hierarchy domains, and chip/domain debug callbacks. It reads live IRQ core state under descriptor lock.

## Risks and test signals
Risks include leaking duplicated device names if descriptors are not removed cleanly, command parsing accepting prefixes by `strncmp()` length, debug output racing with domain removal beyond descriptor lock coverage, and exposing internals in production debugfs. Test signals include debugfs files for early and dynamically allocated IRQs, `trigger` injection, affinity/effective/pending mask output, hierarchy parent output, and descriptor free cleanup.
