# sources/distributed-fs/ceph-client/include/linux/soc/pxa/smemc.h

Purpose: This header defines PXA static memory controller interfaces and register constants.

Important APIs/types/functions: It declares `pxa_smemc_set_pcmcia_timing`, `pxa_smemc_set_pcmcia_socket`, `pxa2xx_smemc_get_sdram_rows`, `pxa3xx_smemc_get_memclkdiv`, and `pxa_smemc_get_mdrefr`. It also conditionally declares `pxa25x_get_clk_frequency_khz` and `pxa27x_get_clk_frequency_khz`, with zero-return stubs when the respective family is disabled.

Control flow: PCMCIA/board code programs socket and timing values; memory and clock code query SDRAM rows, memory clock divisor, MDREFR MMIO, or legacy core frequency values.

State and persistence: SMEMC and MDREFR registers hold bus timing, PCMCIA socket, refresh, and memory clock state until reset or reprogramming.

Dependencies and integration: Integrates with PXA platform initialization, flash/PCMCIA/external memory drivers, and low-level suspend/resume code.

Risks and test signals: Incorrect timings can corrupt external memory transactions. Test early boot memory access, flash reads/writes, suspend/resume restore, and variant-specific timing values.
