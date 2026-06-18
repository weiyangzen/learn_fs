# sources/distributed-fs/ceph-client/virt/lib/Makefile

## Purpose
This Makefile ties the `IRQ_BYPASS_MANAGER` Kconfig symbol to the `irqbypass.o` object.

## Important APIs, Types, And Functions
The only build rule is `obj-$(CONFIG_IRQ_BYPASS_MANAGER) += irqbypass.o`, which follows kernel kbuild conventions for built-in, module, or absent objects.

## Control Flow And State
There is no runtime control flow. Build state follows the tristate expansion of `CONFIG_IRQ_BYPASS_MANAGER`.

## Dependencies And Integration Points
It integrates `virt/lib/irqbypass.c` into the kernel build when selected by higher-level virtualization or interrupt acceleration features.

## Risks And Test Signals
The risk is build coverage: a mismatch between Kconfig and Makefile would omit the manager or build it unexpectedly. Test signals are successful kbuilds for `CONFIG_IRQ_BYPASS_MANAGER=n/y/m` and symbol availability for producer/consumer users.
