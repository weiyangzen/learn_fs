<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/reset.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/reset.c

Purpose: Implements board-specific reboot and shutdown sequences for Lemote 2F desktops, netbooks, NAS, and Lynloong machines.

Important APIs/types/functions: `reset_cpu()`, `fl2f_reboot()`, `fl2f_shutdown()`, `ml2f_reboot()`, `ml2f_shutdown()`, `yl2f89_shutdown()`, `mach_prepare_reboot()`, and `mach_prepare_shutdown()`.

Control flow: Reboot first restores full CPU speed. Fuloong/NAS/Lynloong reset via CS5536 soft reset MSR; laptops reset via EC `REG_RESET`. Shutdown varies by machine: CS5536 GPIO13 low for desktops, special EC shutdown ports for Mengloong, CPU GPIO0 low for Yeeloong.

State and persistence: Mutates chipcfg, CS5536 GPIO/MSR state, EC reset/shutdown registers, or CPU GPIO state.

Dependencies and integration: Called by common Loongson restart/poweroff hooks and uses EC constants.

Risks: Hardware-specific sequences can fail silently; comments note rtl8169 reset problems with PM enabled. GPIO bit operations assume firmware did not reassign pins.

Test signals: Each machtype should reboot or power off using its designated path; CPU frequency should be full speed before reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/reset.c -->
