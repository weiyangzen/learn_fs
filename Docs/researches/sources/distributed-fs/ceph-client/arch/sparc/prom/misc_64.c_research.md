# sources/distributed-fs/ceph-client/arch/sparc/prom/misc_64.c

Purpose: provides SPARC64 miscellaneous IEEE-1275 PROM services for reboot/power, firmware command entry, MMU/memory methods, power management, CPU control, and diagnostic memory lookup.

Important APIs/functions: includes `prom_reboot()`, `prom_feval()`, `prom_cmdline()`, `prom_halt()`, `prom_halt_power_off()`, `prom_get_idprom()`, `prom_itlb_load()`, `prom_dtlb_load()`, `prom_map()`, `prom_unmap()`, `prom_retain()`, `prom_getunumber()`, sleep/wakeup calls, and SMP CPU start/stop/idle/resume helpers. Internal helpers cache MMU and memory ihandles.

Control flow: each service builds a P1275 argument array and calls `p1275_cmd_direct()`. LDOM builds may delegate reboot or poweroff to LDOM hypervisor paths. `prom_cmdline()` captures other CPUs and disables interrupts around PROM entry.

State and persistence: caches ihandles for MMU and memory package methods. Firmware calls can retain memory across soft reset or change platform power/CPU state.

Dependencies and integration points: integrates with restart/poweroff, early MMU mapping, CPU bring-up, sun4v soft state, LDOM services, ECC unumber reporting, and suspend/power-management code.

Risks: P1275 argument counts and return slots must match firmware methods. PROM entry under SMP requires capture/release. Firmware errors are often weakly typed and can leave cached handles invalid.

Test signals: reboot/poweroff on bare metal and LDOM, PROM enter/continue with SMP, TLB load/map/unmap calls during boot, retained memory allocation, CPU start/stop paths, and unumber lookup after memory errors.
