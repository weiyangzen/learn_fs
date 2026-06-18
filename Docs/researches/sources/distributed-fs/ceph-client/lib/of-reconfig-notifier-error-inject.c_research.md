# sources/distributed-fs/ceph-client/lib/of-reconfig-notifier-error-inject.c

## Purpose
Adds error injection for Open Firmware/device-tree reconfiguration notifier events.

## APIs, Control Flow, and State
Defines a module parameter `priority`, a static `notifier_err_inject` action table for attach node, detach node, add property, remove property, and update property events, and module init/exit routines. Init creates `debugfs/notifier-error-inject/OF-reconfig/actions/.../error`, registers the notifier with `of_reconfig_notifier_register()`, and removes debugfs state on registration failure. Exit unregisters and removes the directory. Runtime state is the debugfs-controlled errno per action and the registered notifier block.

## Dependencies, Integration, Risks, and Tests
Depends on OF reconfig notifier APIs, module parameters, debugfs, and the common notifier error-injection helper. Risks include injecting errors into paths that rarely expect notifier failure, incorrect priority changing ordering-sensitive behavior, and stale debugfs entries if registration/unregistration is mishandled. Test signals include OF overlay/reconfig tests with each action errno set, registration failure cleanup checks, and module unload while debugfs files were open.
