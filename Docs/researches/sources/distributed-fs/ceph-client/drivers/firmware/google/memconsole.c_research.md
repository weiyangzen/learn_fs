# sources/distributed-fs/ceph-client/drivers/firmware/google/memconsole.c

Purpose: Provides the architecture-independent sysfs wrapper for firmware memory console logs.

Important APIs/types/functions: `memconsole_setup()` stores a backend read callback in the binary attribute private field. `memconsole_sysfs_init()` creates `/sys/firmware/log`. `memconsole_exit()` removes it. The binary attribute `memconsole_bin_attr` is read-only.

Control flow: Platform-specific discovery code calls `memconsole_setup()` before `memconsole_sysfs_init()`. Sysfs reads dispatch through `memconsole_read()` to the registered backend callback, returning `-EIO` if no callback has been installed.

State and persistence behavior: Static binary attribute state holds one callback pointer. The code does not store log contents; backends read firmware memory.

Dependencies and integration points: Used by coreboot and x86 legacy memconsole drivers. Depends on `firmware_kobj`, sysfs binary attributes, and module exports.

Risks and test signals: Only one global log file/callback exists, so simultaneous backend registration would conflict. Test signals include backend setup before sysfs creation, read behavior without a callback warning, removal cleanup, and module reference/linkage for both providers.
