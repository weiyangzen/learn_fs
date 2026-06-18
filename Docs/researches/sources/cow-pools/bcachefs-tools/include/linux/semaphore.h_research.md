# File Research: sources/cow-pools/bcachefs-tools/include/linux/semaphore.h

Declares a Linux semaphore shape with raw spinlock, count, and wait list plus initializer macros. It exposes `down`, interruptible/killable/trylock/timeout variants, and `up`, implemented in `linux/semaphore.c`.

The file intentionally warns callers not to access fields directly, preserving the kernel API boundary.
