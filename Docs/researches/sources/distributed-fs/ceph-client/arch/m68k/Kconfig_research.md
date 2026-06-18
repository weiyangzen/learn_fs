# sources/distributed-fs/ceph-client/arch/m68k/Kconfig

Purpose: root configuration model for the Linux m68k architecture.

The top-level `config M68K` selects architecture capabilities such as flat binaries, DMA/cache behavior, syscall/modversion support, atomic helpers, old signal ABI options, and `ZONE_DMA`. Additional symbols define big-endian CPU behavior, ilog2/hweight support, default low-resolution time, `HZ`, page-table levels, MMU variants, and kexec/bootinfo support. It sources CPU, machine, bus, and device Kconfig files.

Control flow is configuration-time. `MMU`, `MMU_MOTOROLA`, `MMU_COLDFIRE`, and `MMU_SUN3` partition memory-management support; the `!MMU` branch exposes power management options. `HZ` defaults to 100 except for `CLEOPATRA`.

State/persistence: no runtime state directly, but selected symbols shape compiler flags, object inclusion, ABI assumptions, and machine hook availability throughout the architecture.

Dependencies include other `arch/m68k/Kconfig.*` files and generic kernel Kconfig symbols. Integration is broad: `Kbuild`, `Makefile`, board subdirectories, and headers all consume these symbols.

Risks and test signals: incorrect `select` statements can enable unsupported generic features or hide required dependencies. Test with `allyesconfig`, `allnoconfig` plus target machines, `randconfig`, and compile checks for MMU/non-MMU and ColdFire/classic splits.
