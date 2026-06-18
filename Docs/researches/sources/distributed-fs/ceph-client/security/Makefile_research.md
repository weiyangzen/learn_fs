# sources/distributed-fs/ceph-client/security/Makefile

Purpose: `security/Makefile` maps security-related Kconfig selections to compiled objects and subdirectories.

Important APIs, types, and functions: it always builds `commoncap.o`, conditionally builds `keys/`, `lsm_syscalls.o`, `min_addr.o`, `security.o`, `lsm_notifier.o`, `lsm_init.o`, `inode.o`, individual LSM subdirectories (`selinux/`, `smack/`, `tomoyo/`, `apparmor/`, `yama/`, `loadpin/`, `safesetid/`, `lockdown/`, `bpf/`, `landlock/`, `ipe/`), `lsm_audit.o`, `device_cgroup.o`, and `integrity/`.

Control flow: Kbuild evaluates `obj-y` and `obj-$(CONFIG_*)` assignments to decide which objects and directories are linked into the kernel.

State and persistence: no runtime state in the Makefile, but it controls kernel object composition.

Dependencies and integration points: directly corresponds to `security/Kconfig` options and subsystem directories. `commoncap.o` is always included as the default capability implementation.

Risks: missing an object here can make a Kconfig option silently incomplete at link/runtime. Spacing inconsistency is cosmetic, but config variable names must exactly match Kconfig definitions.

Test signals: build matrices for each LSM/security config, link checks for selected objects, and boot/runtime smoke tests for enabled security modules.
