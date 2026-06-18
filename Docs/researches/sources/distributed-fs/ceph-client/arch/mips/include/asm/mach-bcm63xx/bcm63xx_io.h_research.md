# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_io.h

**Purpose:** Defines BCM63xx physical IO windows and raw register access macros for current-CPU register sets.

**Important APIs/types/functions:** Exports PCMCIA common/attribute/IO, PCI memory/IO, CardBus, and PCIe memory physical windows; `BCM_REGS_VA(x)`; raw volatile `bcm_readb/w/l/q()` and `bcm_writeb/w/l/q()` macros; generic `bcm_rset_read*()`/`bcm_rset_write*()` helpers; and convenience helpers for performance, timer, watchdog, GPIO, UART0, MPI, PCMCIA, PCIe, SDRAM, MEMC, DDR, and MISC register sets.

**Control flow:** Drivers ask `bcm63xx_regset_address()` for the active SoC base and then perform volatile MMIO through these helpers. Board/PCI/PCMCIA setup uses the physical window constants for resource creation.

**State and persistence behavior:** No software state. All writes mutate hardware registers directly through uncached/architecture-mapped addresses. The helpers impose no barriers beyond volatile access semantics.

**Dependencies and integration points:** Depends on `bcm63xx_cpu.h`. Integrated by most BCM63xx platform code, including timer, watchdog, GPIO, UART, PCI/PCMCIA, memory controller, and reset/performance blocks.

**Risks:** Direct pointer dereference macros bypass `readl()/writel()` ordering and sparse checks. Passing an unsupported register set can access `0xdeadbeef`. Physical window sizes must remain power-of-two where noted.

**Test signals:** Boot each SoC, verify no invalid MMIO faults, test timer/watchdog/GPIO/UART/PCIe helpers, inspect resource windows, and run sparse/build warnings around `__iomem` usage.
