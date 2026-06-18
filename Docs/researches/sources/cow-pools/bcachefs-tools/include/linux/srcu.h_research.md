# File Research: sources/cow-pools/bcachefs-tools/include/linux/srcu.h

Provides SRCU compatibility by delegating polling and callbacks to userspace RCU helpers. `struct srcu_struct` is empty, read locks return index `0`, unlock is no-op, and `call_srcu()` calls `call_rcu()`.

This collapses SRCU domains onto the global userspace RCU mechanism.
