# sources/distributed-fs/ceph-client/arch/sh/kernel/sh_bios.c

Purpose: exposes C helpers and optional early console support for trapping into the standard LinuxSH BIOS/GDB vector.

Important APIs and control flow: `sh_bios_call()` loads function and arguments into SH registers and executes `trapa #0x3f` if `gdb_vbr_vector` is known. Helpers wrap console write, GDB detach, Ethernet node address, and shutdown BIOS calls. `sh_bios_vbr_init()` reads the old VBR and records the BIOS trap vector at `vbr + 0x100`; `sh_bios_vbr_reload()` restores VBR from that vector, used around kexec/restore paths. With early printk, a `bios` console writes through BIOS calls and `earlyprintk=bios[,keep]` registers it.

State, dependencies, and risks: state is global `gdb_vbr_vector` and optional `early_console`. Dependencies include debug trap table entry 0x3f, BIOS calling convention, VBR register access, console core, and kexec VBR reload. Risks include trapping when firmware is absent, bogus BIOS cflags, VBR restoration conflicts, and early console lifetime. Test signals are `earlyprintk=bios`, BIOS node address users, KGDB detach through BIOS, and kexec with BIOS VBR.
