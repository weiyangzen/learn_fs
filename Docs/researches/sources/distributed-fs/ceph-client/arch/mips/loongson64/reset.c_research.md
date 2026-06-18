<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/reset.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/reset.c

Purpose: Registers firmware restart/poweroff handlers and Loongson64 kexec/crash-shutdown preparation.

Important APIs/types/functions: `firmware_restart()`, `firmware_poweroff()`, `loongson_kexec_prepare()`, `loongson_kexec_shutdown()`, `loongson_crash_shutdown()`, and `mips_reboot_setup()`.

Control flow: Init registers firmware sys-off handlers when firmware addresses exist. With kexec, it allocates argument/environment buffers, parses a `kexec` command-line segment into firmware-style argv, pins the control code page, brings offline CPUs online before kexec shutdown, and copies argv/envp to firmware argument addresses.

State and persistence: Stores kexec/kdump argc and argv buffers, copies firmware envp, writes global MIPS kexec function pointers and firmware argument globals.

Dependencies and integration: Consumes `loongson_sysconf.restart_addr/poweroff_addr`, `fw_arg1/fw_arg2`, MIPS kexec hooks, and optional SMP `secondary_kexec_args`.

Risks: Fixed physical control/argv addresses must be safe. Kexec command-line parsing is bounded but assumes segment buffer contains a string beginning with `kexec`. Firmware function pointers are trusted.

Test signals: `reboot` and `poweroff` should call firmware sys-off handlers; kexec should pass argv/envp to the next kernel and bring secondary CPUs to the reboot buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/reset.c -->
