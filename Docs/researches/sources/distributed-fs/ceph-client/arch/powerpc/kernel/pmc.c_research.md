# sources/distributed-fs/ceph-client/arch/powerpc/kernel/pmc.c

Purpose: this file arbitrates ownership of PowerPC performance monitor counter interrupt handling and supplies low-level enable/disable helpers for PMC hardware. It is a small shared layer used by perf/perfmon-style users that need exclusive access to PMU interrupt delivery.

Important APIs and state: `perf_irq` is the active PMU interrupt handler and defaults to `dummy_perf()`. `reserve_pmc_hardware()` installs a caller-provided handler if no owner is active, records `pmc_owner_caller`, and returns `-EBUSY` on contention. `release_pmc_hardware()` clears ownership and restores the dummy handler. On Book3S 64-bit, `power4_enable_pmcs()` performs the POWER4 HID0 sequence required to enable counters.

Control flow: callers reserve the hardware before programming counters. If no handler is supplied, the dummy handler remains active. Interrupts arriving while dummy is installed clear/disable the PMU interrupt-enable condition using the CPU-family-specific register path: FSL embedded PMR, IBM MMCR0 with PMAO handling, or generic MMCR0 PMXE clearing. Release resets ownership under the same raw spinlock.

State and persistence: ownership is process-independent kernel state protected by `pmc_owner_lock`. The only persistent state in this file is the active handler pointer and debugging caller address. Hardware state changes are immediate SPR/PMR writes and are not persisted beyond CPU PMU registers.

Dependencies and integration points: depends on `cur_cpu_spec->pmc_type`, PMU SPR/PMR definitions, low-level interrupt paths that call `perf_irq`, and external PMU/perf code that reserves and releases the hardware.

Risks: incorrect reserve/release pairing leaves PMU hardware unavailable. `release_pmc_hardware()` warns but still clears even if there is no owner. The dummy handler must correctly disable interrupts for all configured CPU families; otherwise stray PMU interrupts can loop. The owner address is only diagnostic and not a full owner identity.

Test signals: concurrent reserve attempts should return `-EBUSY` for the second caller. Releasing should restore dummy handling. PMU overflow interrupts with no owner should be disabled without interrupt storms. POWER4 systems need validation of the exact HID0 enable sequence.
