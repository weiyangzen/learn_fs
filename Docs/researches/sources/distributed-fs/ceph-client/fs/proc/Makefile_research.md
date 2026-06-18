# sources/distributed-fs/ceph-client/fs/proc/Makefile

Purpose: Lists procfs objects and conditionally includes feature-specific files according to kernel configuration.

Important APIs and types: Builds `proc.o` from `proc-y` members. Core objects include `inode.o`, `root.o`, `base.o`, `generic.o`, `array.o`, `fd.o`, and common global proc files such as `cmdline.o`, `consoles.o`, `cpuinfo.o`, `devices.o`, `interrupts.o`, `loadavg.o`, `meminfo.o`, `stat.o`, `uptime.o`, `util.o`, `version.o`, `softirqs.o`, `namespaces.o`, `self.o`, and `thread_self.o`. Conditional objects include `task_mmu.o` or `task_nommu.o`, `proc_tty.o`, `proc_sysctl.o`, `proc_net.o`, `kcore.o`, `vmcore.o`, `kmsg.o`, `page.o`, and `bootconfig.o`.

Control flow: Kbuild aggregates `proc-y` into the procfs built-in object. `CONFIG_MMU` selects the task memory implementation, while other config symbols append optional proc subsystems.

State and persistence: The Makefile does not hold runtime state. Its choices persist only as compiled object composition in a kernel build.

Dependencies and integration points: Integrates with the Kconfig symbols in `fs/proc/Kconfig` and top-level kernel build. The warning suppression for `task_mmu.o` is a targeted compiler flag adjustment.

Risks: Missing a core object can remove proc entry registration or inode operations. Wrong conditional selection between MMU/NOMMU task memory code changes `/proc/<pid>/maps` and related behavior. Optional object gates must match their source-level `#ifdef`s.

Test signals: Build procfs across MMU/NOMMU, NET, TTY, SYSCTL, PRINTK, KCORE, VMCORE, PAGE_MONITOR, and BOOT_CONFIG configurations; boot smoke tests should confirm core and optional entries.
