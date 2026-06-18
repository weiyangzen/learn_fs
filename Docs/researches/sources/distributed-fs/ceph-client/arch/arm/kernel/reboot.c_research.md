# sources/distributed-fs/ceph-client/arch/arm/kernel/reboot.c

Purpose: provides ARM restart, halt, power-off, and low-level soft restart sequencing.

Important APIs/types/functions: `arm_pm_restart`, `pm_power_off`, `machine_restart`, `machine_halt`, `machine_power_off`, `soft_restart`, and restart-mode handling. The file coordinates cache/TLB shutdown and optional HYP soft restart path.

Control flow: machine restart stops secondary CPUs, shuts down devices, then calls configured restart hook or falls back to `soft_restart`. Soft restart prepares an identity-mapped execution path, disables MMU/cache state through processor hooks, and branches to the physical/idmapped restart address.

State and persistence: global function pointers and reboot mode carry platform policy. Restart is terminal, so persistent state mostly concerns logs and hardware side effects.

Dependencies and integration: machine descriptors may install restart hooks; kexec calls `soft_restart`; HYP stub may be used for restart; cache/TLB/proc hooks must match CPU type.

Risks: restart with active secondary CPUs or stale caches can hang; missing platform restart hook may only soft reset CPU state, not board power. Test signals include reboot/halt/poweroff, kexec transition, watchdog fallback, and SMP stop logs.
