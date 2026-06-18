# sources/distributed-fs/ceph-client/virt/lib/Kconfig

## Purpose
This Kconfig fragment declares the `IRQ_BYPASS_MANAGER` symbol used to build the IRQ bypass manager utility under `virt/lib`.

## Important APIs, Types, And Functions
The single symbol is `config IRQ_BYPASS_MANAGER` with type `tristate`. It has no prompt here, so other subsystems select or depend on it rather than presenting it directly to users.

## Control Flow And State
Kconfig state controls whether `irqbypass.o` is not built, built in, or built as a module. No runtime state is defined in this file.

## Dependencies And Integration Points
The matching Makefile uses `obj-$(CONFIG_IRQ_BYPASS_MANAGER) += irqbypass.o`. KVM, VFIO, or architecture interrupt acceleration code can select this symbol when posted-interrupt or forwarded-interrupt bypass support is needed.

## Risks And Test Signals
Risks are configuration-level: missing selects produce unresolved symbols for irq bypass users, while unnecessary selects add an unused module. Build matrix tests should cover disabled, built-in, and module states plus any KVM/VFIO configs that register irq bypass producers or consumers.
