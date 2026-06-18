# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/Kbuild

Purpose: architecture Kbuild object aggregation and generated header selection.

Important APIs/types/functions: build rules: `syscall-y += syscall_table_32.h`; `generic-y += extable.h`; `generic-y += iomap.h`; `generic-y += kvm_para.h`; `generic-y += mcs_spinlock.h`; `generic-y += text-patching.h`

Control flow: Kbuild evaluates these object lists and conditionals at build time; runtime flow comes from the selected objects.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on Linux Kbuild/Kconfig evaluation and the configuration symbols or objects named by the rules.

Risks: Configuration drift can silently omit required objects or expose unsupported option combinations in cross-builds.

Test signals: Hexagon cross-build; defconfig, allyesconfig, and allmodconfig build checks.
