# sources/distributed-fs/ceph-client/drivers/watchdog/iTCO_wdt.c

## Purpose
`iTCO_wdt.c` is the Intel TCO watchdog driver for many ICH/PCH generations. It handles version-specific timeout encodings, NO_REBOOT control, optional SMI watchdog clearing disablement, running-at-probe handoff, and suspend-to-idle handling.

## Important APIs, types, and functions
`struct iTCO_wdt_private` stores watchdog device, TCO version, I/O resources, optional GCS/PMC mapping, PCI parent, suspend state, and a function pointer for NO_REBOOT updates. Core operations are `iTCO_wdt_start`, `iTCO_wdt_stop`, `iTCO_wdt_ping`, `iTCO_wdt_set_timeout`, and `iTCO_wdt_get_timeleft`. NO_REBOOT strategies include PCI config, memory-mapped GCS/PMC, TCO1_CNT, and Intel PMC GCR updates.

## Control Flow
Probe consumes `itco_wdt_platform_data`, validates I/O resources, selects NO_REBOOT update method, maps GCS/PMC when needed, clears NO_REBOOT to prove reset is possible, optionally disables SMI watchdog clearing, reserves TCO I/O, clears status bits, initializes the watchdog, detects whether hardware is already running, sets timeout, and registers. Start clears NO_REBOOT, reloads, and clears the halt bit. Stop sets halt and then sets NO_REBOOT.

## State and Persistence
Hardware TCO state may be running before probe. NO_REBOOT policy is persisted in chipset registers until changed. The driver caches whether it stopped the watchdog during suspend so it can restart on resume.

## Dependencies and Integration Points
It depends on platform data from Intel LPC/PMC infrastructure, I/O port resources, optional MMIO/PMC register APIs, ACPI sleep-state detection, watchdog core, and platform PM noirq callbacks.

## Risks and Test Signals
Risks include generation-specific NO_REBOOT bit errors, timeout tick conversion, SMI clearing resource absence, status clearing differences, and suspend-to-idle stop/restart. Tests should cover versions 1-6, PMC-backed NO_REBOOT, invalid heartbeat fallback, running-at-probe, timeleft math, SMI resource missing, and S0ix suspend.
