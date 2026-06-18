# File Research: sources/block-storage/kvdo/vdo/thread-registry.h

This header defines `struct thread_registry` as an RCU list plus spinlock, and `struct registered_thread` as a caller-owned list node containing an associated pointer and task pointer.

It declares initialization, current-thread registration, current-thread unregistration, and lookup. Callers must keep `registered_thread` storage valid while registered.
