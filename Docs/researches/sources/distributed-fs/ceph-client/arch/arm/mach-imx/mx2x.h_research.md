# sources/distributed-fs/ceph-client/arch/arm/mach-imx/mx2x.h

Purpose: Common i.MX21/i.MX27 register, interrupt, and DMA request map for legacy platform code.

Important APIs/types/functions: Defines AIPI peripheral base addresses, AVIC and SAHB regions, fixed legacy IRQ numbers based on `NR_IRQS_LEGACY`, and fixed DMA request ids for UART, SSI, CSPI, SDHC, CSI, and external requests.

Control flow: No executable control flow. The header provides compile-time constants used by board files, platform data, and low-level drivers.

State and persistence: No runtime state. It persists SoC ABI assumptions about interrupt numbering and DMA request routing in source form.

Dependencies and integration points: Depends on `<asm/irq.h>` for `NR_IRQS_LEGACY`; integrates with AVIC interrupt setup, old non-DT platform devices, and DMA/client driver platform data.

Risks: The values are hard-coded SoC contract. Mismatched interrupt or DMA ids produce silent device malfunction, often as missing interrupts or broken DMA. Constants are not discoverable from DT, so legacy board users rely on them exactly.

Test signals: Build old i.MX2 configurations and exercise UART, SDHC, SSI, CSPI, DMA, and AVIC interrupt delivery on i.MX21/i.MX27 boards.
