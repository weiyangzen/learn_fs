# sources/distributed-fs/ceph-client/lib/notifier-error-inject.h

## Purpose
Declares the small internal interface used by notifier error-injection modules.

## APIs, Control Flow, and State
Defines `struct notifier_err_inject_action` with notifier value, configured errno, and action name; `NOTIFIER_ERR_INJECT_ACTION(action)` for name/value initializer pairs; and `struct notifier_err_inject`, which embeds a `notifier_block` followed by a flexible action table terminated by a zero sentinel. It declares the top-level debugfs dentry and `notifier_err_inject_init()`. There is no executable control flow in the header; state is supplied by including modules through static action arrays.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/atomic.h`, `linux/debugfs.h`, and `linux/notifier.h`. Risks include forgetting the sentinel, using a notifier value that does not match the target chain, and exposing mutable debugfs errno fields without caller-side synchronization. Test signals are compile coverage for action table initializers and module tests that verify each named action directory maps to the intended notifier event.
