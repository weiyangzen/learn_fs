# sources/distributed-fs/ceph-client/lib/pm-notifier-error-inject.c

## Purpose
Adds debugfs-configurable error injection for power-management notifier events.

## APIs, Control Flow, and State
Defines a `priority` module parameter, an action table for hibernation prepare, suspend prepare, and restore prepare, and module init/exit. Init creates `debugfs/notifier-error-inject/pm/actions/.../error`, registers the notifier with `register_pm_notifier()`, and removes debugfs state on failure. Exit unregisters and removes the directory. Runtime state is the notifier block plus per-action errno fields.

## Dependencies, Integration, Risks, and Tests
Depends on PM notifier APIs, suspend constants, module parameters, debugfs, and the shared notifier error-injection helper. Risks include causing suspend/hibernate abort paths that are rarely exercised, priority-dependent behavior, and debugfs availability. Test signals include suspend and hibernation preparation tests with injected errno values, registration failure cleanup, and module unload cleanup.
