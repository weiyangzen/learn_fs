# sources/distributed-fs/ceph-client/drivers/memstick/Makefile

Purpose: This Makefile controls top-level MemoryStick subsystem compilation. It applies debug compiler flags and descends into core and host directories when `CONFIG_MEMSTICK` is enabled.

Important APIs/types/functions: `subdir-ccflags-$(CONFIG_MEMSTICK_DEBUG) := -DDEBUG` enables debug builds for subdirectories. `obj-$(CONFIG_MEMSTICK) += core/` and `obj-$(CONFIG_MEMSTICK) += host/` include the subsystem implementation and host drivers.

Control flow: Kbuild evaluates config symbols and includes both subdirectories for built-in or modular MemoryStick builds. If `MEMSTICK_DEBUG` is set, all compiled files below receive `-DDEBUG`.

State and persistence: There is no runtime state. Build output depends on `.config` and Kbuild's object traversal.

Dependencies and integration: Depends on top-level kernel Kbuild and Kconfig symbols from `drivers/memstick/Kconfig`. It integrates with `drivers/memstick/core/Makefile` and host Makefiles.

Risks and test signals: Risks include failing to build host drivers when the core is enabled, or debug flags not propagating. Test signals are `make drivers/memstick/` with `MEMSTICK=y/m`, disabled builds excluding the directory, and debug builds compiling with dynamic debug/dev_dbg support.
