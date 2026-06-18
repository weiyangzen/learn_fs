# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/shmobile/Makefile

Purpose: declares build objects for the Linux/SuperH SH-Mobile backend directory.

Important APIs, types, and functions: this is Kbuild metadata, not C code. `obj-$(CONFIG_PM) += pm.o sleep.o` includes power-management and sleep support when PM is enabled. `obj-$(CONFIG_CPU_IDLE) += cpuidle.o` includes CPU idle support when configured.

Control flow: during kernel build, Kbuild evaluates the configuration symbols and compiles/link these backend objects into the SH-Mobile CPU support area.

State and persistence: no runtime state. Build outputs persist as object files and linked kernel code depending on configuration.

Dependencies and integration points: integrates SH-Mobile PM, sleep, and cpuidle source files with the architecture build. Setup files such as SH7724 depend on SH-Mobile sleep notifier infrastructure when PM code is enabled.

Risks: missing `CONFIG_PM` omits sleep notifier support required by SoC-specific suspend paths. Missing `CONFIG_CPU_IDLE` excludes idle driver support. The Makefile intentionally has no per-SoC selection logic, so source files must guard their own dependencies.

Test signals: configuration/build tests should verify `pm.o` and `sleep.o` appear with PM and `cpuidle.o` appears with CPU idle; SH-Mobile suspend and cpuidle runtime tests validate the selected objects.
