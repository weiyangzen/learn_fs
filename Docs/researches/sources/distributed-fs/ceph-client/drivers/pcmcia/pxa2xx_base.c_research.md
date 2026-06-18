# sources/distributed-fs/ceph-client/drivers/pcmcia/pxa2xx_base.c

Purpose: Implements the common PXA2xx PCMCIA socket controller platform driver. It translates PCMCIA timing requests into PXA static-memory-controller timing values and registers sockets through the shared SoC PCMCIA layer.

Important APIs and functions: Exports `pxa2xx_configure_sockets()`, `pxa2xx_drv_pcmcia_add_one()`, and `pxa2xx_drv_pcmcia_ops()`. Internal timing helpers compute setup, assertion, and hold fields (`pxa2xx_mcxx_setup()`, `pxa2xx_mcxx_asst()`, `pxa2xx_mcxx_hold()`) and write them through `pxa_smemc_set_pcmcia_timing()`. `pxa2xx_drv_pcmcia_probe()` and remove/resume callbacks implement the platform driver.

Control flow: Probe reads platform `struct pcmcia_low_level`, rejects unsupported multi-slot PXA320 setups, obtains the memory-controller clock, installs PXA timing callbacks into low-level ops, allocates a flexible `skt_dev_info`, initializes each `soc_pcmcia_socket`, and calls `pxa2xx_drv_pcmcia_add_one()`. After socket registration it invokes `pxa2xx_configure_sockets()`. CPU-frequency transitions pre-update timing when frequency rises and post-update timing when it falls.

State and persistence: Per-socket resources are physical PXA PCMCIA partitions for I/O, memory, and attribute space. Timing values persist in SMEMC registers until frequency changes, resume, or later map operations.

Dependencies and integration points: Uses PXA SoC helpers (`cpu_is_pxa320()`, `pxa_smemc_set_pcmcia_socket()`, `pxa_smemc_set_pcmcia_timing()`), common SoC PCMCIA (`soc_common.h`), Linux platform/clock/cpufreq APIs, and board-specific low-level ops passed through platform data.

Risks: Timing math is integer-rounded and depends on clock rate in 10 kHz units; low clock or extreme access values can underflow helper return values. Platform data is mandatory. Resource ranges are hard-coded PXA physical layout, so this driver is tightly architecture-specific.

Test signals: Platform device probe, socket registration, card insertion on each supported slot, I/O/attribute/common-memory access, CPU-frequency transitions with stable card traffic, PXA320 one-slot rejection, and resume reconfiguration.
