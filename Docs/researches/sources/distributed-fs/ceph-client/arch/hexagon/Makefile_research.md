# sources/distributed-fs/ceph-client/arch/hexagon/Makefile

Purpose: architecture Kbuild compiler/linker flags and object selection.

Important APIs/types/functions: build rules: `KBUILD_DEFCONFIG = comet_defconfig`; `KBUILD_CFLAGS += -G0`; `LDFLAGS_vmlinux += -G0`; `KBUILD_CFLAGS += -fno-short-enums`; `KBUILD_CFLAGS += -mlong-calls`; `KBUILD_CFLAGS_MODULE += -mlong-calls`; `cflags-y += $(call cc-option,-mv${CONFIG_HEXAGON_ARCH_VERSION})`; `aflags-y += $(call cc-option,-mv${CONFIG_HEXAGON_ARCH_VERSION})`

Control flow: Kbuild evaluates these object lists and conditionals at build time; runtime flow comes from the selected objects.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on Linux Kbuild/Kconfig evaluation and the configuration symbols or objects named by the rules.

Risks: Configuration drift can silently omit required objects or expose unsupported option combinations in cross-builds.

Test signals: Hexagon cross-build; defconfig, allyesconfig, and allmodconfig build checks.
