# sources/distributed-fs/ceph-client/drivers/misc/cb710/Kconfig

Purpose: declares build-time configuration for the ENE CB710/CB720 flash memory card reader core and optional debug support.

Important APIs, types, and functions: `CONFIG_CB710_CORE` is a tristate depending on PCI and builds the `cb710` module/core. `CONFIG_CB710_DEBUG` is a developer-oriented bool depending on the core and enables verbose debug output through `-DDEBUG`. `CONFIG_CB710_DEBUG_ASSUMPTIONS` is a hidden bool defaulting to yes when the core is enabled and gates internal assumption checks in the code.

Control flow: Kconfig choices determine whether `core.o` and `sgbuf2.o` are built and whether `debug.o` plus additional debug assertions are included. Users must separately enable child flash-card format drivers such as MMC/SD or MemoryStick.

State and persistence: no runtime state is stored here; it controls compilation and module availability.

Dependencies and integration points: integrated with the Linux Kconfig system under `drivers/misc`. The core's PCI dependency matches `core.c`; debug settings match `debug.c` and debug assumption blocks in `core.c`.

Risks: enabling debug can create a lot of dmesg output. The hidden default-on assumption checks can turn logical mistakes into BUGs on unusual platform-device lifetimes when debugging assumptions are compiled in.

Test signals: expected build matrix includes `CB710_CORE=m/y/n`, debug on/off, and child media driver combinations. Kconfig dependency checks should prevent non-PCI builds.
