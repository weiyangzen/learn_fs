# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/pmu.c

Purpose: Provides brcmsmac PMU helper logic for power-up delay selection and ALP clock measurement through the chipcommon PMU registers.

Important APIs: `si_pmu_fast_pwrup_delay()` returns the maximum transition delay by default and a chip-specific 3700 us value for BCM43224, BCM43225, and BCM4313. `si_pmu_measure_alpclk()` requires PMU revision 10 or newer, checks `PST_EXTLPOAVAIL`, enables `pmu_xtalfreq` measurement, waits at least four ILP clocks, reads the latched ALP tick counter, disables measurement, and returns rounded ALP frequency in kHz.

Control flow and state: The delay function is a switch on `ai_get_chip_id()`. The measurement path temporarily mutates the `pmu_xtalfreq` register and otherwise derives a value from MMIO; no software state is retained. A saved `core` pointer is read from `sii->icbus->drv_cc.core`.

Dependencies and integration: Uses Linux delay/MMIO headers, BCMA chip IDs, `chipcommon.h` offsets, `brcmu_utils.h`, `pub.h`, `aiutils.h`, `pmu.h`, and `soc.h`. It depends on `container_of(sih, struct si_info, pub)` matching `aiutils` layout. Risks include returning 0 for unsupported PMU revisions or absent external LPO, MMIO access when chipcommon is not available, and measurement rounding masking marginal clock values. Test signals include chip-ID-specific delay checks, PMU rev gating, external-LPO present/absent cases, and suspend/resume clock stability.
