# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-rbtn.h

Purpose: Notifier interface header for Dell airplane-mode switch events.

Important APIs/types/functions: Declares `dell_rbtn_notifier_register()` and `dell_rbtn_notifier_unregister()` with a forward `struct notifier_block`.

Control flow/state/persistence: Header-only; runtime state is owned by `dell-rbtn.c`.

Dependencies/integration: Consumed by `dell-laptop.c`; implemented by `dell-rbtn.c`.

Risks/test signals: Built-in init ordering matters because `dell-laptop` dynamically requests these symbols. Test modular and built-in builds.
