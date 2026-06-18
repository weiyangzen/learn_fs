# sources/distributed-fs/ceph-client/fs/proc/Kconfig

Purpose: Defines Kconfig switches controlling procfs and optional `/proc` features.

Important APIs and types: User-visible symbols include `PROC_FS`, `PROC_KCORE`, `PROC_VMCORE`, `PROC_VMCORE_DEVICE_DUMP`, `NEED_PROC_VMCORE_DEVICE_RAM`, `PROC_VMCORE_DEVICE_RAM`, `PROC_SYSCTL`, `PROC_PAGE_MONITOR`, `PROC_CHILDREN`, `PROC_PID_ARCH_STATUS`, and `PROC_CPU_RESCTRL`. These symbols gate compilation in the proc Makefile and many `#ifdef` paths in proc sources.

Control flow: Kconfig has no runtime flow. During configuration, `PROC_FS` defaults to enabled; dependent options select or depend on crash dump, MMU, sysctl, page-monitoring, boot/crash, and architecture support. Help text documents user-visible files such as `/proc/kcore`, `/proc/vmcore`, `/proc/sys`, page monitoring files, and `/proc/<pid>/task/<tid>/children`.

State and persistence: Configuration choices are persisted in the kernel `.config` and compiled into the kernel image. They determine which proc entries can exist at runtime, but this file does not manage runtime state itself.

Dependencies and integration points: Drives `fs/proc/Makefile` object selection and conditional code in proc files such as `base.c`, `array.c`, `page.c`, `proc_sysctl.c`, `kcore.c`, and `vmcore.c`. It also selects `SYSCTL` and `VMCORE_INFO` where necessary.

Risks: Disabling `PROC_FS` or `PROC_SYSCTL` can break userspace assumptions. Enabling crash/core interfaces exposes sensitive kernel memory/dump data and must rely on their runtime permission checks. `PROC_CHILDREN` is off by default because it provides a specialized interface with consistency caveats.

Test signals: Build matrix with procfs enabled/disabled, MMU and crash-dump combinations, sysctl enabled/disabled, page-monitoring enabled/disabled, and boot tests verifying expected proc entries appear or are absent.
