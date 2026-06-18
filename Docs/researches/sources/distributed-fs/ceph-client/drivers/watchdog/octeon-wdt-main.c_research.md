# sources/distributed-fs/ceph-client/drivers/watchdog/octeon-wdt-main.c

## Purpose
`octeon-wdt-main.c` implements a Cavium OCTEON per-CPU watchdog. It keeps hardware watchdogs active even before userspace opens the device, supports software countdowns for long heartbeats, and coordinates NMI diagnostics before reset.

## Important APIs, types, and functions
Global state tracks hardware divisor, period/count values, heartbeat, `do_countdown`, per-CPU countdowns, enabled IRQ CPUs, and the OCTEON boot vector. Important functions are `octeon_wdt_cpu_online`, `octeon_wdt_cpu_pre_down`, `octeon_wdt_poke_irq`, `octeon_wdt_ping`, `octeon_wdt_calc_parameters`, `octeon_wdt_set_timeout`, `octeon_wdt_start`, `octeon_wdt_stop`, and `octeon_wdt_nmi_stage3`.

## Control flow
Module init allocates the boot vector, derives the watchdog tick divisor by OCTEON model, computes the largest valid period, registers a watchdog device, and installs CPU hotplug callbacks unless disabled. Each online CPU installs the NMI stage2 vector, requests/affines a watchdog IRQ, clears stale state, and enables interrupt/NMI/soft-reset mode. IRQs either poke hardware and decrement software countdown or disable the IRQ to allow NMI/reset progression. Userspace ping reloads every online CPU and re-enables IRQs if appropriate. NMI stage3 prints saved registers and CP0 state, then may trigger a soft reset on affected OCTEON3 models.

## State and persistence
State is global and per-CPU: hardware CIU watchdog registers, boot-vector entries, per-CPU countdown arrays, and IRQ-enabled masks. It persists only while the module is loaded, but hardware watchdogs remain live across CPU hotplug transitions until disabled by callbacks.

## Dependencies and integration points
It depends on MIPS/OCTEON low-level CSR APIs, CPU hotplug, irqdomain/affinity APIs, watchdog core, boot vector allocation, and `octeon-wdt-nmi.S` for the NMI register-save stage.

## Risks and test signals
Risks include per-CPU global arrays sized by `NR_CPUS`, watchdog IRQ affinity on CIU3 mappings, boot-vector lifetime during module unload, countdown math for very long or non-divisible heartbeats, and panic/reset behavior in NMI context. Test signals include single/SMP OCTEON boot, CPU hotplug online/offline, disable module parameter, heartbeat divisibility changes, userspace open/close, IRQ disable countdown expiry, and NMI register dump on forced hang.
