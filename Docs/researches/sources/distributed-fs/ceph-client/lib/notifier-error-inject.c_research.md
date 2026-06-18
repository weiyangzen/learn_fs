# sources/distributed-fs/ceph-client/lib/notifier-error-inject.c

## Purpose
Implements shared debugfs-backed error injection for kernel notifier chains. It lets specialized modules expose notifier action names and configurable negative errno values.

## APIs, Control Flow, and State
Exports `notifier_err_inject_dir` and `notifier_err_inject_init()`. The initializer wires `err_inject->nb.notifier_call`, sets notifier priority, creates a debugfs directory with an `actions` subdirectory, and creates an `error` file per action. Writes are clamped to `[-MAX_ERRNO, 0]`. The notifier callback scans the null-terminated action array, matches `val`, logs non-zero injection, and returns `notifier_from_errno(err)`. Module init creates the top-level `notifier-error-inject` directory; exit removes it recursively. State is the action array's mutable `error` fields and debugfs dentries.

## Dependencies, Integration, Risks, and Tests
Depends on debugfs, notifier blocks, module lifetime, and the local header. It is reused by PM and OF reconfiguration error-injection modules. Risks include missing debugfs cleanup on registration failure in users, no locking around action `error` fields, action values not listed in the table returning success, and injection only being available when debugfs is mounted and enabled. Test signals include debugfs read/write of each action, clamping behavior, notifier return conversion, and unregister cleanup under module unload.
