# sources/distributed-fs/ceph-client/drivers/firmware/google/memconsole.h

Purpose: Declares the shared memconsole interface used by platform-specific firmware log providers.

Important APIs/types/functions: Declares `memconsole_setup()`, `memconsole_sysfs_init()`, and `memconsole_exit()`.

Control flow: No executable flow. Backends call setup with a read callback, initialize sysfs, and remove sysfs on teardown.

State and persistence behavior: No local state. The interface manages a global sysfs file in `memconsole.c`; providers own the memory being read.

Dependencies and integration points: Depends only on Linux basic types. Included by `memconsole-coreboot.c`, `memconsole-x86-legacy.c`, and `memconsole.c`.

Risks and test signals: The comments mention unmapping but the actual common code only removes sysfs; backend drivers must manage their own mappings. Compile coverage of all providers is the primary test signal.
