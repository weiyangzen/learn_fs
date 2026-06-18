# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/psoc_mme_pll_regs.h

Purpose: defines the PSOC MME PLL register map for the matrix-math engine clock domain. It has the same 41-register PLL prototype as the eMMC and PCI PLL maps, with base addresses from `0xC71100` to `0xC71440`.

Important APIs/types/functions: macro-only `mmPSOC_MME_PLL_*` constants for `NR`, `NF`, `OD`, `NB`, `CFG`, lock/loss controls, reset/data-change controls, four divider factor lanes, divider commands, divider selects/enables, busy flags, clock gater/relaxation registers, reference counter thresholds, not-stable status, and frequency calculation enable.

Control flow: low-level clock initialization programs PLL factors, requests data changes or reset, waits on lock/busy indicators, and gates or ungates derived clocks before enabling dependent MME hardware.

State and persistence: PLL factor and divider settings are persistent clock-domain hardware state. Bad state can remain until reset and affect all MME transactions.

Dependencies and integration: included through `goya_regs.h`. It belongs to the generated PSOC PLL family and can be used by firmware or driver clock setup before MME enablement.

Risks: MME stability depends on correct PLL setup. Programming values out of order or ignoring busy/lock can create transient clock glitches. Copying values from another PLL block without verifying the intended frequency is unsafe.

Test signals: MME initialization, workload execution, frequency measurement, PLL lock monitoring, reset/resume, and clock-gating tests are the main validation paths.
