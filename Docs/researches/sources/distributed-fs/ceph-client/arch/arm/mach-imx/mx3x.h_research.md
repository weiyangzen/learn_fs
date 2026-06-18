# sources/distributed-fs/ceph-client/arch/arm/mach-imx/mx3x.h

Purpose: Common i.MX31/i.MX35 memory map, peripheral base, chip-select, interrupt, and product signature definitions.

Important APIs/types/functions: Defines MX3x AIPS/SPBA/AIPS2 peripheral bases, L2CC, ROMP/AVIC, SDRAM and chip-select windows, X_MEMC sub-blocks, legacy interrupt numbers, and `MX3x_PROD_SIGNATURE`.

Control flow: No runtime flow; it supplies constants to early platform, board, and driver glue.

State and persistence: No mutable state. The header preserves the static virtual/physical layout assumptions for MX3x-era code.

Dependencies and integration points: Depends on `<asm/irq.h>` and integrates with i.MX31/i.MX35 machine descriptors, AVIC irq code, WEIM/NAND/SDRAM setup, and non-DT platform data.

Risks: Interrupt numbering and register windows are fragile hardware ABI. A mistake usually appears as stuck boot, broken serial/timer, or devices firing wrong IRQs. The map mixes virtual-address documentation with physical constants, so consumers must use the right conversion path.

Test signals: Build i.MX31/i.MX35 configurations and smoke boot with timer, UART, GPIO, SDMA, IPU, and watchdog paths.
