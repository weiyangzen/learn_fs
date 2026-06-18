# sources/distributed-fs/ceph-client/lib/memory-notifier-error-inject.c

Purpose: Debug/test module that injects failures into memory hotplug notifier actions.

Important APIs/types/functions: Defines module parameter `priority`, `memory_notifier_err_inject`, `err_inject_init()`, and `err_inject_exit()`.

Control flow: Module init creates a debugfs notifier error-injection directory for memory actions, registers the memory notifier, and cleans debugfs on registration failure. Exit unregisters and removes debugfs recursively.

State and persistence: Maintains a debugfs dentry and notifier registration while module is loaded.

Dependencies/integration: Depends on memory hotplug notifiers, `notifier-error-inject.h`, debugfs infrastructure, and module parameters.

Risks: Intended to force failures; should only be enabled in debug/testing environments. Cleanup must match registration to avoid stale notifiers.

Test signals: Behavior is observed through debugfs knobs and memory hotplug operation return paths.
