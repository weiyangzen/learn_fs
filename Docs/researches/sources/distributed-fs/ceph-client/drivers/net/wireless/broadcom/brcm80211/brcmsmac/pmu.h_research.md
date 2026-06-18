# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/pmu.h

Purpose: Declares the brcmsmac PMU helper interface.

Important APIs: `si_pmu_fast_pwrup_delay(struct si_pub *sih)` returns a chip-specific or maximum PMU transition delay in microseconds. `si_pmu_measure_alpclk(struct si_pub *sih)` measures or reports ALP clock frequency in kHz when supported.

Control flow and state: The header has no state; it defines the PMU helper contract for callers holding an SI public handle.

Dependencies and integration: Includes `types.h` for `struct si_pub` and fixed-width types. It is consumed by chip/AI bring-up and clock management paths. Risks are mainly contract-level: callers must tolerate 0 from ALP measurement and use the delay as a bounded wait value rather than a precise hardware latency. Test signals include compile coverage and hardware initialization paths using both helpers on supported and unsupported chip IDs.
