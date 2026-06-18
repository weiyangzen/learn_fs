# sources/distributed-fs/ceph-client/arch/csky/kernel/probes/Makefile

Purpose: selects C-SKY kprobes, kprobes-on-ftrace, uprobes, decoder, simulator, and trampoline objects.

Important APIs/types/functions: build rules: `obj-$(CONFIG_KPROBES) += kprobes.o decode-insn.o simulate-insn.o`; `obj-$(CONFIG_KPROBES) += kprobes_trampoline.o`; `obj-$(CONFIG_KPROBES_ON_FTRACE) += ftrace.o`; `obj-$(CONFIG_UPROBES) += uprobes.o decode-insn.o simulate-insn.o`; `CFLAGS_REMOVE_simulate-insn.o = $(CC_FLAGS_FTRACE)`

Control flow: Kbuild evaluates these object lists and conditionals at build time; runtime flow comes from the selected objects.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on Linux Kbuild/Kconfig evaluation and the configuration symbols or objects named by the rules.

Risks: Configuration drift can silently omit required objects or expose unsupported option combinations in cross-builds.

Test signals: C-SKY cross-build; defconfig, allyesconfig, and allmodconfig build checks.
