# sources/distributed-fs/ceph-client/include/asm-generic/access_ok.h

Purpose: Provides the generic user-pointer range validation used by architectures that do not need custom `access_ok()` behavior.

Important APIs, types, and functions: Defines fallback `TASK_SIZE_MAX`, inline `__access_ok(const void __user *ptr, unsigned long size)`, and macro `access_ok(addr, size)`.

Control flow: The check returns true for alternate user address spaces or no-MMU builds. Otherwise it validates `size <= TASK_SIZE_MAX` and `addr <= TASK_SIZE_MAX - size`, catching overflow with a single range comparison.

State and persistence: No state. It validates transient user-space access ranges.

Dependencies and integration points: Depends on `TASK_SIZE`, `CONFIG_MMU`, `CONFIG_ALTERNATE_USER_ADDRESS_SPACE`, `likely()`, and `__user` annotations. Integrates with `uaccess` copy/get/put paths.

Risks and test signals: Risks include architectures with variable compat `TASK_SIZE` not overriding `TASK_SIZE_MAX`, overflow mistakes, and false positives on special address-space architectures. Test boundary addresses, zero/large sizes, compat tasks, no-MMU builds, and hardened usercopy paths.
