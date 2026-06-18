# sources/distributed-fs/ceph-client/drivers/watchdog/hpwdt.c

## Purpose
`hpwdt.c` is the HPE iLO2+ hardware watchdog driver for supported ProLiant/iLO PCI devices. It supports watchdog core operation, optional NMI pretimeout decoding, crash-kernel timeout policy, suspend/resume, and hardware-running handoff.

## Important APIs, types, and functions
Global MMIO pointers identify NMI status, timer reload, and timer control registers. Watchdog ops are `hpwdt_start`, `hpwdt_stop_core`, `hpwdt_ping`, `hpwdt_settimeout`, `hpwdt_gettimeleft`, and optionally `hpwdt_set_pretimeout`. PCI lifecycle is handled by `hpwdt_init_one` and `hpwdt_exit`. NMI support uses `hpwdt_pretimeout`, `hpwdt_my_nmi`, and register/unregister NMI handlers.

## Control Flow
Probe validates subsystem vendor, rejects blacklisted auxiliary devices, enables PCI, maps BAR1, detects running hardware, registers NMI decoding when configured, applies nowayout/timeout/pretimeout/kdump settings, and registers the watchdog. Start writes reload ticks and control bits including pretimeout enable. Ping rewrites reload ticks. NMI pretimeout may stop or extend the timer, pack the NMI reason into a panic message, and call `nmi_panic`.

## State and Persistence
The driver uses global singleton state for one active PCI device. Hardware timer state may be active before probe and is adopted through `WDOG_HW_RUNNING`. `kdumptimeout` changes behavior in crash kernels.

## Dependencies and Integration Points
It depends on PCI IDs, BAR mapping, watchdog core, optional x86 NMI handlers, crash dump detection, suspend/resume PM ops, and HPE iLO hardware semantics.

## Risks and Test Signals
Risks include global state with multiple devices, NMI ownership conflicts, pretimeout/timeout interactions, kdump behavior, blacklist coverage, and MMIO lifetime. Tests should cover supported/blacklisted PCI IDs, running-at-probe, NMI registration failures, pretimeout toggling, kdump kernel path, suspend/resume, and max tick conversion.
