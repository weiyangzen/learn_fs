# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-clps711x.c

Purpose: implements the CLPS711X cpuidle driver with a single HALT state backed by an MMIO write.

Important APIs and functions: probe maps the first platform resource into global `clps711x_halt` and registers `clps711x_idle_driver`. `clps711x_cpuidle_halt()` writes `0xaa` to the mapped HALT register and returns the selected index.

Control flow and state: the only runtime state is the global MMIO pointer managed by devm. The driver has one state with exit latency 1 and no separate WFI fallback state.

Dependencies and integration points: depends on a platform device named `clps711x-cpuidle`, MMIO resource mapping, and cpuidle core registration via `builtin_platform_driver_probe`.

Risks and test signals: risks include global MMIO pointer for a single device, no explicit target residency, no unregister path, and the assumption that a write to the HALT register is sufficient and safe in cpuidle context. Test signals include successful resource mapping, HALT register write on idle entry, wakeup from interrupts, and registration of exactly one state.
