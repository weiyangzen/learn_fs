# sources/distributed-fs/ceph-client/drivers/memstick/Kconfig

Purpose: This Kconfig file defines the top-level MemoryStick subsystem configuration menu and includes the core and host-driver Kconfig files when MemoryStick support is enabled.

Important APIs/types/functions: `menuconfig MEMSTICK` is a tristate option for Sony MemoryStick card support. `config MEMSTICK_DEBUG` enables debug logging by later Makefile flags. `source "drivers/memstick/core/Kconfig"` and `source "drivers/memstick/host/Kconfig"` include subordinate options.

Control flow: Kconfig dependency flow is simple: if `MEMSTICK` is disabled, neither core nor host options are visible. If enabled, developers can also enable debug and select specific core/host drivers.

State and persistence: Configuration state is stored in the kernel `.config`, not in this file at runtime. The options control which objects are built and whether `DEBUG` is defined.

Dependencies and integration: Integrates with the kernel Kconfig system and the corresponding `drivers/memstick/Makefile`. It is the entry point for MemoryStick block drivers and host controller options.

Risks and test signals: Risks are mostly build-configuration regressions, such as exposing drivers without the core or failing to propagate debug. Test signals include `olddefconfig`/menuconfig visibility, builds with `MEMSTICK=y`, `MEMSTICK=m`, and disabled, plus debug builds showing `-DDEBUG` in affected subdirs.
