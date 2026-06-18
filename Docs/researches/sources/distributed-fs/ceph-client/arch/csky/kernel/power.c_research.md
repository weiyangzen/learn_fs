# sources/distributed-fs/ceph-client/arch/csky/kernel/power.c

Purpose: architecture reboot and power-off hooks.

Important APIs/types/functions: functions: `machine_power_off`, `machine_halt`, `machine_restart`; exports: `pm_power_off`

Control flow: Runtime flow is organized around `machine_power_off`, `machine_halt`, `machine_restart`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/reboot.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.
