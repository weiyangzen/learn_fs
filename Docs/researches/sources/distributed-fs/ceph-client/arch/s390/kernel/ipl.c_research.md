# sources/distributed-fs/ceph-client/arch/s390/kernel/ipl.c

Purpose: central Initial Program Load, re-IPL, dump, shutdown, secure-boot, and kexec report support for Linux on s390. It exposes current boot information, lets users configure reboot/dump targets, and issues DIAG 308 firmware calls during shutdown.

Important APIs and state: global preserved boot data includes `ipl_block`, `ipl_block_valid`, `ipl_secure_flag`, certificate list addresses, and component list data. Public integration points include `diag308()`, `ipl_info`, `setup_ipl()`, `s390_reset_system()`, `arch_get_secureboot()`, `set_os_info_reipl_block()`, and, under kexec-file, `ipl_report_*()` helpers. Mutable state tracks reipl/dump capabilities, selected `reipl_type`/`dump_type`, allocated IPL parameter blocks for CCW/FCP/NVMe/ECKD/NSS, clear flags, shutdown triggers, and optional z/VM commands.

Control flow: early setup derives `ipl_info` from the preserved parameter block and registers the panic notifier. Init creates firmware sysfs ksets: `ipl`, `reipl`, `dump`, `vmcmd`, and `shutdown_actions`. Sysfs store methods validate and mutate parameter blocks, loadparm, VM parm, SCP data, boot program selectors, and selected shutdown actions. Shutdown entry points stop CPUs and invoke trigger actions, which either issue `DIAG308_SET` plus load subcodes, request dump loops, run VM CP commands, or stop in disabled wait.

State and persistence: configured reipl blocks are copied into OS info for crash/kdump handoff; dump-reipl also writes lowcore `ipib` and checksum. Kexec-file report construction serializes the IPL block, component entries, and certificates for secure IPL reporting.

Dependencies and integration: tightly coupled to firmware kobjects, SCLP IPL info, DIAG 308, lowcore, OS info, kexec, panic/reboot hooks, z/VM CP commands, EBCDIC conversion, and secure boot.

Risks and test signals: high-risk areas are sysfs input bounds, EBCDIC/ASCII conversion, firmware capability mismatches, stale OS-info reipl blocks, and shutdown paths that intentionally do not return. Test via sysfs attribute read/write, VM vs LPAR boot modes, dump/reipl dry runs where available, secure boot reporting, kexec-file load with certificates, and panic/restart/halt trigger selection.
