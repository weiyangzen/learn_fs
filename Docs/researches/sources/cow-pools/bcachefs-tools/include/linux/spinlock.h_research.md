# File Research: sources/cow-pools/bcachefs-tools/include/linux/spinlock.h

Defines cleanup-scope guard wrappers for `spinlock_t` and raw spinlock variants. Many kernel guard variants are present inside `#if 0`; active guards cover normal spinlock, trylock, irq, irqsave-like, and raw-spinlock aliases.

Actual lock behavior comes from `spinlock_types.h`, where spinlocks are pthread mutexes.
