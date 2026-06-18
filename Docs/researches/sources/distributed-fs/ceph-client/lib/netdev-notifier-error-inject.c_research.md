# sources/distributed-fs/ceph-client/lib/netdev-notifier-error-inject.c

Purpose: Debug/test module that injects failures into selected netdevice notifier events.

Important APIs/types/functions: Defines module parameter `priority`, `netdev_notifier_err_inject`, `netdev_err_inject_init()`, and `netdev_err_inject_exit()`.

Control flow: Module init creates a `netdev` error-injection debugfs directory, registers a netdevice notifier, and removes debugfs if registration fails. Exit unregisters the notifier and removes debugfs.

State and persistence: Holds notifier registration and debugfs directory for module lifetime.

Dependencies/integration: Depends on netdevice notifier chain, common notifier error-injection helper, debugfs, and module infrastructure.

Risks: Intended to disrupt network device operations for testing; event list includes register, MTU/name changes, pre-up/type/upper changes, and post-init.

Test signals: Testers control injected responses through debugfs and observe netdevice operation failures.
