<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa2xx-regs.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa2xx-regs.h

Purpose: PXA2xx power-manager, clock, reset, and power-mode register definitions.

Important definitions: power manager registers `PMCR`, `PSSR`, `PSPR`, `PWER`, `PRER`, `PFER`, `PEDR`, `PCFR`, `PGSR*`, `RCSR`, sleep/standby/voltage registers, `PCMD*` voltage command registers, status/config bit masks, GPIO wake masks, RTC wake bit, clock registers `CCCR`, `CCSR`, `CKEN`, `OSCC`, and PWRMODE values.

Control flow and integration: SoC PM, reset, Gumstix Bluetooth clock, MFP suspend, and wake code use these macros for direct MMIO.

State and persistence: hardware power/clock/reset registers persist across runtime and some low-power transitions.

Dependencies: includes `pxa-regs.h`.

Risks and test signals: register bits often have write-one-to-clear or write-once semantics. Test suspend/resume, wake sources, reset status clearing, OSCC 32 kHz startup, and clock users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa2xx-regs.h -->
