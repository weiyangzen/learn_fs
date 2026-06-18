# sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/Makefile

Purpose: builds the C-SKY VDSO shared object, symbol assembly, and embedded kernel object.

Important APIs/types/functions: build rules: `include $(srctree)/lib/vdso/Makefile.include`; `vdso-syms += rt_sigreturn`; `obj-vdso = $(patsubst %, %.o, $(vdso-syms)) note.o`; `ifneq ($(c-gettimeofday-y),)`; `CFLAGS_vgettimeofday.o += -include $(c-gettimeofday-y)`; `endif`; `ccflags-y := -fno-stack-protector -DBUILD_VDSO32`; `targets := $(obj-vdso) vdso.so vdso.so.dbg vdso.lds vdso-dummy.o`

Control flow: Kbuild evaluates these object lists and conditionals at build time; runtime flow comes from the selected objects.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on Linux Kbuild/Kconfig evaluation and the configuration symbols or objects named by the rules.

Risks: Configuration drift can silently omit required objects or expose unsupported option combinations in cross-builds.

Test signals: C-SKY cross-build; defconfig, allyesconfig, and allmodconfig build checks.
