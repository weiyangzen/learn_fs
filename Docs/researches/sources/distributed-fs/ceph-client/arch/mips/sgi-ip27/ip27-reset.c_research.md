# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-reset.c

Purpose: reboot, halt, and poweroff hooks for SGI IP27 systems.

Important APIs and control flow: `ip27_reboot_setup()` assigns `_machine_restart`, `_machine_halt`, and `pm_power_off`. Restart logs the initiating CPU, stops SMP, and resets the local HUB port. Halt stops SMP, writes `PROMOP_RESTART` to each online node's PROMOP register, then resets the local HUB port. Poweroff is a stub infinite loop.

State, persistence, and integration: state is global machine hook registration and HUB/PROMOP register side effects. Dependencies include SMP stop support, online nodes, and SN HUB reset registers. Risks include no implemented poweroff, alternative reboot path disabled under `#if 0`, and reset relying on local port reset propagation. Test signals are reboot/halt behavior and expected "Reboot started" log.
