# sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-power.c

Purpose: IP30 restart hook using HEART cold reset.

Important APIs and control flow: `ip30_reboot_setup()` installs `_machine_restart` at subsys init. `ip30_machine_restart()` sets `HM_COLD_RST` in the HEART mode register and never returns.

State, persistence, and integration: state is machine restart hook registration and a write to HEART mode. Dependencies include valid `heart_regs` from setup. Risks include no halt/poweroff implementation here and reset failure if HEART registers are inaccessible. Test signals are reboot triggering HEART cold reset and no return from restart.
