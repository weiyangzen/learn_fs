# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/8xx_immap.h

Purpose: defines the memory-mapped internal register layout for MPC8xx processors, including SIU, PCMCIA, memory controller, timers, clock/reset, video/LCD, I2C, SDMA, CPM interrupt controller, I/O ports, CPM timers, SCC/SMC/SPI/parallel interfaces, FEC, dual-port RAM, and parameter RAM.

Important APIs/types/functions: major types are `sysconf8xx_t`, `pcmconf8xx_t`, `memctl8xx_t`, `sit8xx_t`, `car8xx_t`, `sitk8xx_t`, `cark8xx_t`, `vid823_t`, `lcd823_t`, `i2c8xx_t`, `sdma8xx_t`, `cpic8xx_t`, `iop8xx_t`, `cpmtimer8xx_t`, `scc_t`, `smc_t`, `fec_t`, `cpm8xx_t`, and top-level `immap_t`. Register bit macros cover memory-controller BR/OR fields, timer status/control bits, keep-alive power keying, and FEC/LCD aliases. `mpc8xx_immr` is the exported mapped base pointer.

Control flow: this header is declarative. Board and driver code map the IMMR area, cast it to `immap_t`, then access the nested register blocks directly or through the `cp_fec`, `cp_fec1`, `cp_fec2`, and `lcd_cmap` aliases.

State and persistence: all state is live MPC8xx hardware state. Register writes configure chip selects, wait states, timers, resets, interrupt masks, serial channels, Ethernet descriptors, DMA, and dual-port RAM; values persist until reset or reprogramming.

Dependencies and integration points: available only for `__KERNEL__`. It depends on kernel integer typedefs and `__iomem`. It integrates with old 8xx board support, CPM serial/Ethernet/I2C code, early platform setup, and low-level memory-controller initialization.

Risks: structure padding and reserved byte counts must exactly match the processor manual; casual refactors can shift every hardware register. Some blocks are model-specific, and the FEC/LCD address union means simultaneous assumptions are unsafe. Direct volatile MMIO users must handle endian, ordering, and posted writes externally.

Test signals: validate with `BUILD_BUG_ON` offsets where available, boot MPC8xx targets, exercise timer, FEC, CPM serial, I2C, and PCMCIA paths, and compare register dumps against the hardware manual after board initialization.
