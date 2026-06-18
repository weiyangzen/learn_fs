<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pm.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pm.h

Purpose: internal PXA PM function-table interface and low-level suspend symbol declarations.

Important types/APIs: `struct pxa_cpu_pm_fns` contains save/restore/valid/enter/prepare/finish callbacks and `save_count`. Declares `pxa_cpu_pm_fns`, low-level assembly helpers `pxa25x_finish_suspend()`, `pxa27x_finish_suspend()`, `pxa3xx_finish_suspend()`, generic PM functions, and standby code address symbols.

Control flow and integration: SoC files fill the table; `pm.c` consumes it. Assembly suspend code and SRAM-copied standby code are linked through these declarations.

State and persistence: no state except exported pointer declaration.

Dependencies: includes `linux/suspend.h`.

Risks and test signals: callback contract must match `save_count` and allocated buffer size. Test suspend entry for each SoC family and link coverage for assembly symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pm.h -->
