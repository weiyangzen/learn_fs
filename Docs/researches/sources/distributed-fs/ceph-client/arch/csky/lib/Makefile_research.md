# sources/distributed-fs/ceph-client/arch/csky/lib/Makefile

Purpose: selects C-SKY library objects for usercopy, delay, error injection, and fallback string routines.

Important APIs/types/functions: build rules: `lib-y := usercopy.o delay.o`; `obj-$(CONFIG_FUNCTION_ERROR_INJECTION) += error-inject.o`; `ifneq ($(CONFIG_HAVE_EFFICIENT_UNALIGNED_STRING_OPS), y)`; `lib-y += string.o`; `endif`

Control flow: Kbuild evaluates these object lists and conditionals at build time; runtime flow comes from the selected objects.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on Linux Kbuild/Kconfig evaluation and the configuration symbols or objects named by the rules.

Risks: Configuration drift can silently omit required objects or expose unsupported option combinations in cross-builds.

Test signals: C-SKY cross-build; defconfig, allyesconfig, and allmodconfig build checks.
