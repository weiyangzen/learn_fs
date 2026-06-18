# sources/distributed-fs/ceph-client/arch/xtensa/platforms/Makefile

Purpose: Selects Xtensa platform subdirectories for the build.

Important APIs, types, and functions: `obj-$(CONFIG_XTENSA_PLATFORM_XT2000)`, `obj-$(CONFIG_XTENSA_PLATFORM_ISS)`, and `obj-$(CONFIG_XTENSA_PLATFORM_XTFPGA)`.

Control flow: Kbuild descends into exactly the platform directories enabled by configuration, making their setup and device code available to `platform_setup()`/platform headers.

State and persistence: No runtime state; controls platform object inclusion.

Dependencies and integration: Architecture platform Kconfig, platform-specific `Makefile`s, and generic Xtensa setup hooks.

Risks: Multiple enabled platforms may create duplicate platform symbols if not intended; missing platform selection leaves required hooks unresolved.

Test signals: Build each platform defconfig and verify the expected subdirectory objects are linked.
