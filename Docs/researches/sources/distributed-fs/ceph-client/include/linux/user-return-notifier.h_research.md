# sources/distributed-fs/ceph-client/include/linux/user-return-notifier.h

## Purpose
This header defines a per-task notifier mechanism fired just before returning to user mode when `CONFIG_USER_RETURN_NOTIFIER` is enabled.

## Important APIs, types, and functions
Key type is `user_return_notifier` with an `on_user_return` callback and hlist link. APIs are `user_return_notifier_register()`, `user_return_notifier_unregister()`, `propagate_user_return_notify()`, `fire_user_return_notifiers()`, and `clear_user_return_notifier()`. Disabled builds provide empty stubs.

## Control flow, state, and persistence
Users register callbacks that set task thread flags. On context switch, `propagate_user_return_notify()` moves `TIF_USER_RETURN_NOTIFY` from previous to next task when needed; return-to-user code calls `fire_user_return_notifiers()`. State is task-local flags and notifier lists, not persistent.

## Dependencies and integration points
It depends on scheduler task flags and hlist support. It integrates with low-level context-switch and return-to-user paths.

## Risks and test signals
Risks include callback lifetime errors, missing flag propagation, and callbacks running in sensitive return-to-user context. Tests should register/unregister notifiers, switch tasks, clear flags, and verify disabled stubs compile away.
