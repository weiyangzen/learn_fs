# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/smemc.c

Purpose: PXA3xx static memory controller syscore save/restore and a helper to decode memory clock divider.

Important APIs/types/functions: `pxa3xx_smemc_suspend()`, `pxa3xx_smemc_resume()`, `smemc_init()`, and exported `pxa3xx_smemc_get_memclkdiv()`. Static saved state includes `msc[]`, `sxcnfg`, `memclkcfg`, and `csadrcfg[]`.

Control flow: `subsys_initcall` registers syscore ops only on PXA3xx. Suspend snapshots selected SMEMC timing/address registers. Resume restores them in a fixed order. The divider helper reads `MEMCLKCFG`, masks the low two bits, and returns a table value.

State and persistence: volatile kernel globals hold register images across suspend. Hardware SMEMC state is restored after resume; no disk persistence.

Dependencies and integration points: depends on `cpu_is_pxa3xx()`, syscore infrastructure, raw MMIO helpers, and register addresses from `smemc.h`. Suspend assembly and memory-mapped peripheral users rely on these timings staying coherent.

Risks: saved register coverage is minimal and PXA3xx-specific. Incorrect resume order or missing registers can break external memory devices.

Test signals: PXA3xx suspend/resume with devices on static memory chip selects, clock divider readback, and boot logs confirming syscore registration only on supported CPUs.
