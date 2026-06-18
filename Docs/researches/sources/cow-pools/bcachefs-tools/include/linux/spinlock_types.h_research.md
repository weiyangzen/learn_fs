# File Research: sources/cow-pools/bcachefs-tools/include/linux/spinlock_types.h

Defines `raw_spinlock_t` as a `pthread_mutex_t` wrapper and aliases `spinlock_t` to it. It provides init, lock, unlock, trylock, irq/irqsave/bh/nested macro aliases, and static initializer macros.

This is mutual exclusion only; interrupt disabling and bottom-half semantics are no-ops in userspace.
