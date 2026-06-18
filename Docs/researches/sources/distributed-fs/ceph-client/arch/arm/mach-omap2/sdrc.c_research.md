# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sdrc.c

## Purpose
Implements common OMAP2/3 SMS/SDRC initialization and SMS context save/restore for SDRAM controller support.

## APIs, Flow, And State
Global state includes `omap2_sdrc_base`, `omap2_sms_base`, static SDRC init parameter pointers for CS0/CS1, and `sms_context.sms_sysconfig`. `omap2_set_globals_sdrc(sdrc, sms)` stores base addresses. `omap2_sdrc_init(sdrc_cs0, sdrc_cs1)` programs SMS and SDRC smart-idle modes, records timing parameter tables, writes SDRC power policy with external clock disable and page policy set, avoids `PWDENA` due to OMAP34xx erratum 1.150, and saves SMS context. `omap2_sms_restore_context()` restores `SMS_SYSCONFIG` after off mode.

## Dependencies And Integration
Depends on `sdrc.h` inline MMIO accessors, common clock setup, and board/platform timing data. Integrates with low-level suspend assembly and SRAM SDRC reprogramming code.

## Risks And Test Signals
SDRAM controller programming is memory-corruption sensitive; comments explicitly avoid a known erratum. Test signals are stable memory under idle/off-mode, SMS context restoration, and boot on platforms with one or two chip selects.
