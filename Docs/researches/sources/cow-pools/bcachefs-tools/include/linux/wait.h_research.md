# File Research: sources/cow-pools/bcachefs-tools/include/linux/wait.h

Declares wait queue structures, wake/prepare/finish functions, wait-event macros, bit wait helpers, and default wake callbacks. Wait queues use spinlocks and list heads; implementation is in `linux/wait.c`.

The macros map kernel wait loops onto the userspace scheduler shim and futex-backed `schedule()`.
