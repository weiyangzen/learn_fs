# sources/distributed-fs/ceph-client/arch/hexagon/Kconfig

Purpose: architecture configuration symbols, feature selections, and build-time options.

Important APIs/types/functions: build rules: `comment "Linux Kernel Configuration for Hexagon"`; `config HEXAGON`; `def_bool y`; `select ARCH_32BIT_OFF_T`; `select ARCH_HAS_SYNC_DMA_FOR_DEVICE`; `select ARCH_NO_PREEMPT`; `select ARCH_WANT_FRAME_POINTERS`; `select DMA_GLOBAL_POOL`

Control flow: Configuration is declarative: symbols select generic kernel facilities, architecture features, and build options before compilation.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on Linux Kbuild/Kconfig evaluation and the configuration symbols or objects named by the rules.

Risks: Configuration drift can silently omit required objects or expose unsupported option combinations in cross-builds.

Test signals: Hexagon cross-build; defconfig, allyesconfig, and allmodconfig build checks.
