# File Research: sources/block-storage/kvdo/vdo/thread-registry.c

This file implements a generic current-task registry using a spinlock-protected RCU list. It avoids logging while holding locks, because logging itself may use registry functions.

`uds_register_thread()` initializes a caller-owned `registered_thread`, removes any stale entry for `current`, appends the new entry with RCU list operations, and synchronizes before reinitializing a replaced entry. `uds_unregister_thread()` removes the current thread's entry and synchronizes before list reinitialization. `uds_lookup_thread()` uses an RCU read-side section to find the pointer associated with `current`.

The registry stores arbitrary `const void *` pointers, enabling multiple contextual registries such as device id or allocation tracking.
