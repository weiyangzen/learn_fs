# subset-b-000642 Research

Grouped source research for subset B work item `subset-b-000642`. Each source file section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/imx-uart.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/imx-uart.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/imx-uart.h` centralizes physical UART
base address selection for many NXP/Freescale i.MX SoCs. It is part of the vendored Linux ARM code
under the Ceph client source tree and has 142 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: IMX*_UART*_BASE_ADDR constants, IMX*_UART_BASE token-pasting
helpers, IMX_DEBUG_UART_BASE(), and the CONFIG_DEBUG_* switch that defines UART_PADDR.
Important macros/constants include: `__DEBUG_IMX_UART_H`, `IMX1_UART1_BASE_ADDR`,
`IMX1_UART2_BASE_ADDR`, `IMX1_UART_BASE_ADDR(n)`, `IMX1_UART_BASE(n)`, `IMX25_UART1_BASE_ADDR`,
`IMX25_UART2_BASE_ADDR`, `IMX25_UART3_BASE_ADDR`, `IMX25_UART4_BASE_ADDR`, `IMX25_UART5_BASE_ADDR`,
`IMX25_UART_BASE_ADDR(n)`, `IMX25_UART_BASE(n)`, `IMX27_UART1_BASE_ADDR`, `IMX27_UART2_BASE_ADDR`,
`IMX27_UART3_BASE_ADDR`, `IMX27_UART4_BASE_ADDR`, `IMX27_UART_BASE_ADDR(n)`, `IMX27_UART_BASE(n)`,
... (92 total).

## Control Flow
preprocessor selection chooses a single UART physical address before any assembly debug backend
runs.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: wrong SoC or CONFIG_DEBUG_IMX_UART_PORT values route early printk to unmapped MMIO or
a different serial port. Changes should preserve register layouts, numeric constants, early-boot
calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/imx-uart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/imx.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/imx.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/imx.S` implements the i.MX DEBUG_LL UART
macro backend. It is part of the vendored Linux ARM code under the Ceph client source tree and has
49 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: addruart, senduart, waituartcts, waituarttxrdy, busyuart,
UART_VADDR, and IMX_IO_P2V.
Visible dependencies include: `asm/assembler.h`, `imx-uart.h`.
Important macros/constants include: `IMX_IO_P2V(x)`, `UART_VADDR`.

## Control Flow
addruart computes physical and virtual addresses, senduart writes TX data, and busyuart polls
transmit-complete state.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: the virtual address formula and status bits must match the selected i.MX UART
generation. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/imx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/meson.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/meson.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/meson.S` implements the Amlogic Meson AO
UART DEBUG_LL backend. It is part of the vendored Linux ARM code under the Ceph client source tree
and has 35 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: MESON_AO_UART_WFIFO, MESON_AO_UART_STATUS, TX FIFO empty/full bits,
and the standard debug macros.
Important macros/constants include: `MESON_AO_UART_WFIFO`, `MESON_AO_UART_STATUS`,
`MESON_AO_UART_TX_FIFO_EMPTY`, `MESON_AO_UART_TX_FIFO_FULL`.

## Control Flow
addruart returns CONFIG_DEBUG_UART_PHYS/VIRT, waituarttxrdy loops until the FIFO is not full, and
busyuart waits for FIFO empty.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: misconfigured CONFIG_DEBUG_UART_PHYS or FIFO bit definitions can hang early console
output. Changes should preserve register layouts, numeric constants, early-boot calling conventions,
and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/meson.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/msm.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/msm.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/msm.S` implements the Qualcomm MSM UART
DEBUG_LL backend. It is part of the vendored Linux ARM code under the Ceph client source tree and
has 48 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: addruart, senduart, waituarttxrdy, waituartcts, and busyuart around
UARTDM or legacy register layouts.
No standalone symbols are declared beyond build-system or include-level directives.

## Control Flow
waituarttxrdy conditionally polls either UARTDM status or legacy flag registers before senduart
writes the byte.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: the backend has SoC-specific register spacing and can spin forever if the selected
port does not expose the expected status. Changes should preserve register layouts, numeric
constants, early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/msm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/omap2plus.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/omap2plus.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/omap2plus.S` implements OMAP2+ and Zoom
board DEBUG_LL address selection. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 82 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: OMAP/Zoom physical and virtual mapping constants, UART_OFFSET(),
addruart, senduart, and FIFO polling macros.
Visible dependencies include: `linux/serial_reg.h`.
Important macros/constants include: `ZOOM_UART_BASE`, `ZOOM_UART_VIRT`, `OMAP_PORT_SHIFT`,
`ZOOM_PORT_SHIFT`, `UART_OFFSET(addr)`.

## Control Flow
addruart chooses between special Zoom mapping and generic OMAP mapping, then TX writes use
serial_reg offsets with the configured port shift.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: board-specific offset handling is fragile during very early boot because no driver or
device tree mapping can correct it. Changes should preserve register layouts, numeric constants,
early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/omap2plus.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/palmchip.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/palmchip.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/palmchip.S` adapts the generic 8250
DEBUG_LL backend to Palmchip UART register numbering. It is part of the vendored Linux ARM code
under the Ceph client source tree and has 12 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: UART_TX, UART_LSR, UART_MSR overrides followed by include of
debug/8250.S.
Visible dependencies include: `linux/serial_reg.h`, `debug/8250.S`.
Important macros/constants include: `UART_TX`, `UART_LSR`, `UART_MSR`.

## Control Flow
the file has no own control flow; the included 8250 macros inherit the Palmchip register indexes.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: changing these offsets breaks all inherited 8250 polling and transmit logic for
Palmchip platforms. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/palmchip.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/pl01x.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/pl01x.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/pl01x.S` implements the ARM AMBA
PL010/PL011 DEBUG_LL UART backend. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 37 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: UART01x_DR, UART01x_FR, UART01x_FR_TXFF, UART01x_FR_BUSY, addruart,
senduart, waituarttxrdy, and busyuart.
Visible dependencies include: `linux/amba/serial.h`.

## Control Flow
addruart returns CONFIG_DEBUG_UART_PHYS/VIRT, transmit waits for TX FIFO room, sends a byte, then
polls BUSY.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: PL010 versus PL011 differences are hidden by linux/amba/serial.h constants and must
stay compatible with both users. Changes should preserve register layouts, numeric constants, early-
boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/pl01x.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/renesas-scif.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/renesas-scif.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/renesas-scif.S` implements Renesas SCIF
DEBUG_LL output for multiple register layouts. It is part of the vendored Linux ARM code under the
Ceph client source tree and has 56 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: SCIF_PHYS, SCIF_VIRT, FTDR, FSR, TDFE, TEND, addruart, senduart,
waituarttxrdy, and busyuart.
Important macros/constants include: `SCIF_PHYS`, `SCIF_VIRT`, `FTDR`, `FSR`, `TDFE`, `TEND`.

## Control Flow
compile-time CONFIG_DEBUG_R7S72100_SCIF2 and CONFIG_DEBUG_RCAR_GEN2_SCIF branches select the
transmit and status offsets.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: using the wrong variant writes to the wrong register offset and can stall waiting on
non-status bits. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/renesas-scif.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/s3c24xx.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/s3c24xx.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/s3c24xx.S` selects Samsung S3C24xx
DEBUG_LL addressing and FIFO helpers. It is part of the vendored Linux ARM code under the Ceph
client source tree and has 33 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: S3C2410_UART1_OFF, addruart, fifo_full_s3c2410, fifo_level_s3c2410,
and include of debug/samsung.S.
Visible dependencies include: `linux/serial_s3c.h`, `debug/samsung.S`.
Important macros/constants include: `S3C2410_UART1_OFF`.

## Control Flow
the file provides SoC-specific address/FIFO primitives, then delegates byte transmit and busy loops
to samsung.S.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: the generic Samsung code depends on fifo_full/fifo_level macro aliases being correct
for this UART generation. Changes should preserve register layouts, numeric constants, early-boot
calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/s3c24xx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/s5pv210.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/s5pv210.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/s5pv210.S` selects Samsung S5PV210
DEBUG_LL addressing and aliases to S5PV210 FIFO helpers. It is part of the vendored Linux ARM code
under the Ceph client source tree and has 31 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: S3C_VA_UART, S5PV210_PA_UART, addruart, fifo_full, fifo_level, and
include of debug/samsung.S.
Visible dependencies include: `debug/samsung.S`.
Important macros/constants include: `S3C_ADDR_BASE`, `S3C_VA_UART`, `S5PV210_PA_UART`, `fifo_full`,
`fifo_level`.

## Control Flow
addruart computes the configured UART channel offset and the shared Samsung transmit macros use the
S5PV210 FIFO layout.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: CONFIG_DEBUG_S3C_UART must match the boot UART or early printk writes to the wrong
channel. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/s5pv210.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/sa1100.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/sa1100.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/sa1100.S` implements Intel/StrongARM
SA1100 DEBUG_LL UART output. It is part of the vendored Linux ARM code under the Ceph client source
tree and has 67 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: UTCR3, UTDR, UTSR1, UTCR3_TXE, UTSR1_TBY, UTSR1_TNF, addruart,
senduart, waituarttxrdy, and busyuart.
Important macros/constants include: `UTCR3`, `UTDR`, `UTSR1`, `UTCR3_TXE`, `UTSR1_TBY`, `UTSR1_TNF`.

## Control Flow
addruart chooses one of the configured UART base constants, enables TX where needed, and polling
waits on SA1100 status bits.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: the code mutates UTCR3 in early boot, so register constants and the selected UART must
be exact. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/sa1100.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/samsung.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/samsung.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/samsung.S` provides shared Samsung
S3C/S5P DEBUG_LL transmit and FIFO polling logic. It is part of the vendored Linux ARM code under
the Ceph client source tree and has 94 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: fifo_level_s5pv210, fifo_full_s5pv210, fifo_level_s3c2440,
fifo_full_s3c2440, senduart, busyuart, and waituarttxrdy.
Visible dependencies include: `linux/serial_s3c.h`.
Important macros/constants include: `fifo_level`, `fifo_full`.

## Control Flow
SoC wrapper files define address and FIFO helper aliases; this file writes UTXH and loops on
UFSTAT/UTRSTAT until space or completion.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: the macro alias contract with s3c24xx.S and s5pv210.S is tight and mistakes can leave
early boot spinning in FIFO waits. Changes should preserve register layouts, numeric constants,
early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/samsung.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/sti.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/sti.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/sti.S` implements STMicroelectronics STI
ASC DEBUG_LL output. It is part of the vendored Linux ARM code under the Ceph client source tree and
has 39 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: ASC_TX_BUF_OFF, ASC_CTRL_OFF, ASC_STA_OFF, ASC_STA_TX_FULL,
ASC_STA_TX_EMPTY, and the standard debug macros.
Important macros/constants include: `ASC_TX_BUF_OFF`, `ASC_CTRL_OFF`, `ASC_STA_OFF`,
`ASC_STA_TX_FULL`, `ASC_STA_TX_EMPTY`.

## Control Flow
transmit writes ASC_TX_BUF after waituarttxrdy sees space, and busyuart waits until the ASC reports
TX empty.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: the hard-coded status bit definitions are a boot-critical ABI with the STI ASC
hardware block. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/sti.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/stm32.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/stm32.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/stm32.S` implements STM32 USART DEBUG_LL
output across old and newer register layouts. It is part of the vendored Linux ARM code under the
Ceph client source tree and has 43 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: STM32_USART_SR_OFF, STM32_USART_TDR_OFF, STM32_USART_TC,
STM32_USART_TXE, addruart, senduart, waituarttxrdy, and busyuart.
Important macros/constants include: `STM32_USART_SR_OFF`, `STM32_USART_TDR_OFF`, `STM32_USART_TC`,
`STM32_USART_TXE`.

## Control Flow
conditional CONFIG_STM32F4_DEBUG_UART selects SR/TDR offsets; the macros poll TXE/TC before and
after writes.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: mixing STM32F4 offsets with later STM32 UARTs corrupts MMIO accesses during
decompressor or early printk output. Changes should preserve register layouts, numeric constants,
early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/stm32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/tegra.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/tegra.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/tegra.S` implements NVIDIA Tegra DEBUG_LL
UART selection and transmit support. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 218 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: TEGRA_UARTA-E bases, clock/reset and PMC scratch registers,
checkuart(), addruart, senduart, busyuart, and waituartcts.
Visible dependencies include: `linux/serial_reg.h`.
Important macros/constants include: `UART_SHIFT`, `TEGRA_CLK_RESET_BASE`, `TEGRA_APB_MISC_BASE`,
`TEGRA_UARTA_BASE`, `TEGRA_UARTB_BASE`, `TEGRA_UARTC_BASE`, `TEGRA_UARTD_BASE`, `TEGRA_UARTE_BASE`,
`TEGRA_PMC_BASE`, `TEGRA_CLK_RST_DEVICES_L`, `TEGRA_CLK_RST_DEVICES_H`, `TEGRA_CLK_RST_DEVICES_U`,
`TEGRA_CLK_OUT_ENB_L`, `TEGRA_CLK_OUT_ENB_H`, `TEGRA_CLK_OUT_ENB_U`, `TEGRA_PMC_SCRATCH20`,
`TEGRA_APB_MISC_GP_HIDREV`, `UART_VIRTUAL_BASE`, ... (19 total).

## Control Flow
addruart can inspect scratch registers and clock enables to infer the active UART, then 8250-style
TX/status polling emits bytes.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: the detection path reads reset, clock, and HIDREV state before normal mappings exist,
so unsupported chips or clock-gated UARTs can select no usable console. Changes should preserve
register layouts, numeric constants, early-boot calling conventions, and userspace/module ABI
boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/tegra.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/uncompress.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/uncompress.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/uncompress.h` provides a minimal debug
decompressor interface when no real DEBUG_LL backend is enabled. It is part of the vendored Linux
ARM code under the Ceph client source tree and has 8 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: extern putc when CONFIG_DEBUG_ICEDCC is set, otherwise empty
putc(), flush(), and arch_decomp_setup() stubs.
C functions detected in this file include: `putc()`, `flush()`, `arch_decomp_setup()`.

## Control Flow
the decompressor can include this header unconditionally while output either routes through ICEDCC
or compiles away.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: silent stubs mean decompressor failures have no serial signal unless another debug
backend is selected. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/uncompress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/ux500.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/ux500.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/ux500.S` selects ST-Ericsson Ux500 PL01x
UART addresses for DEBUG_LL. It is part of the vendored Linux ARM code under the Ceph client source
tree and has 39 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: U8500_UART*_PHYS_BASE, UX500_PHYS_UART(), UART_PHYS_BASE,
UART_VIRT_BASE, addruart, and include of debug/pl01x.S.
Visible dependencies include: `debug/pl01x.S`.
Important macros/constants include: `U8500_UART0_PHYS_BASE`, `U8500_UART1_PHYS_BASE`,
`U8500_UART2_PHYS_BASE`, `__UX500_PHYS_UART(n)`, `UX500_PHYS_UART(n)`, `UART_PHYS_BASE`,
`UART_VIRT_BASE`.

## Control Flow
the wrapper computes the selected UART base and delegates transmit/status handling to the shared
PL01x backend.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: CONFIG_UX500_DEBUG_UART must match the board routing or the shared PL01x macros access
the wrong UART. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/ux500.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/vexpress.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/vexpress.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/vexpress.S` selects ARM Versatile Express
DEBUG_LL PL01x addresses. It is part of the vendored Linux ARM code under the Ceph client source
tree and has 48 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: DEBUG_LL_PHYS_BASE variants, UART offsets, DEBUG_LL_UART_PHYS_CRX,
DEBUG_LL_VIRT_BASE, addruart, and include of debug/pl01x.S.
Visible dependencies include: `debug/pl01x.S`.
Important macros/constants include: `DEBUG_LL_PHYS_BASE`, `DEBUG_LL_UART_OFFSET`,
`DEBUG_LL_PHYS_BASE_RS1`, `DEBUG_LL_UART_OFFSET_RS1`, `DEBUG_LL_UART_PHYS_CRX`,
`DEBUG_LL_VIRT_BASE`.

## Control Flow
addruart guesses the memory map from physical base ranges before handing transmit behavior to PL01x
macros.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: the educated address guess is intentionally early-boot-specific and can fail on
unusual VExpress memory maps. Changes should preserve register layouts, numeric constants, early-
boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/vexpress.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/vf.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/vf.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/vf.S` implements NXP/Freescale Vybrid
DEBUG_LL UART output. It is part of the vendored Linux ARM code under the Ceph client source tree
and has 36 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: VF_UART*_BASE_ADDR, VF_UART_PHYSICAL_BASE, VF_UART_VIRTUAL_BASE,
addruart, senduart, busyuart, and waituarttxrdy.
Important macros/constants include: `VF_UART0_BASE_ADDR`, `VF_UART1_BASE_ADDR`,
`VF_UART2_BASE_ADDR`, `VF_UART3_BASE_ADDR`, `VF_UART_BASE_ADDR(n)`, `VF_UART_BASE(n)`,
`VF_UART_PHYSICAL_BASE`, `VF_UART_VIRTUAL_BASE`.

## Control Flow
the backend selects a configured UART port and writes the data register while polling its status
register for TX readiness.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: incorrect CONFIG_DEBUG_VF_UART_PORT or virtual mapping assumptions lose early console
output. Changes should preserve register layouts, numeric constants, early-boot calling conventions,
and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/vf.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/vt8500.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/vt8500.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/vt8500.S` implements VIA/WonderMedia
VT8500 DEBUG_LL UART output. It is part of the vendored Linux ARM code under the Ceph client source
tree and has 37 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: DEBUG_LL_PHYS_BASE, DEBUG_LL_VIRT_BASE, DEBUG_LL_UART_OFFSET,
addruart, senduart, busyuart, and waituarttxrdy.
Important macros/constants include: `DEBUG_LL_PHYS_BASE`, `DEBUG_LL_VIRT_BASE`,
`DEBUG_LL_UART_OFFSET`.

## Control Flow
addruart derives the UART MMIO base and transmit waits on the status register before writing bytes.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: the fixed physical/virtual bases are board-family assumptions and must match the low-
level map. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/vt8500.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/zynq.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/zynq.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/debug/zynq.S` implements Xilinx Zynq DEBUG_LL
UART output. It is part of the vendored Linux ARM code under the Ceph client source tree and has 51
source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: UART_CR/SR/FIFO offsets, TXFULL/TXEMPTY bits, UART0/1 PHYS/VIRT
bases, addruart, senduart, waituarttxrdy, and busyuart.
Important macros/constants include: `UART_CR_OFFSET`, `UART_SR_OFFSET`, `UART_FIFO_OFFSET`,
`UART_SR_TXFULL`, `UART_SR_TXEMPTY`, `UART0_PHYS`, `UART0_VIRT`, `UART1_PHYS`, `UART1_VIRT`,
`LL_UART_PADDR`, `LL_UART_VADDR`.

## Control Flow
CONFIG_DEBUG_ZYNQ_UART0 selects UART0 or UART1, then the backend polls TXFULL/TXEMPTY around FIFO
writes.

## State and Persistence Behavior
There is no durable state. The only state is CPU registers and UART MMIO state touched during early
boot or decompression. Any characters written become serial side effects, and polling loops depend
on live hardware status bits rather than scheduler-visible state.

## Dependencies and Integration Points
This file integrates with `arch/arm/kernel/debug.S` through the DEBUG_LL macro contract: `addruart`,
`senduart`, `waituartcts`, `waituarttxrdy`, and `busyuart`. The decompressor, early printk, and low-
level `printascii` code use those macros before serial drivers, clocks, or normal ioremap services
are available.

## Risks
Primary risk: selecting the wrong UART or status bit definitions causes lost output or infinite
early boot polling. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Build-test a kernel with the matching `CONFIG_DEBUG_LL` and platform `CONFIG_DEBUG_*` option, boot
with `earlyprintk`, and verify decompressor/early console output before the normal tty driver binds.
Negative signals are hangs in wait loops, no early output, or output appearing on the wrong UART.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/zynq.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/Kbuild

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/Kbuild` declares generated and generic
UAPI headers for ARM. It is part of the vendored Linux ARM code under the Ceph client source tree
and has 5 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: generated-y entries for unistd-oabi.h and unistd-eabi.h plus
generic-y kvm_para.h.
No standalone symbols are declared beyond build-system or include-level directives.

## Control Flow
Kbuild expands generated syscall headers into the exported UAPI include tree.

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: generated syscall header mismatches break userspace ABI and libc/kernel header
synchronization. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/auxvec.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/auxvec.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/auxvec.h` defines the ARM auxiliary
vector tag for the VDSO ELF header. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 8 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: AT_SYSINFO_EHDR.
Important macros/constants include: `__ASM_AUXVEC_H`, `AT_SYSINFO_EHDR`.

## Control Flow
the ELF loader exposes this constant via auxv so userspace can locate the VDSO image.

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: changing the numeric tag breaks the stable userspace auxv ABI. Changes should preserve
register layouts, numeric constants, early-boot calling conventions, and userspace/module ABI
boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/auxvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/byteorder.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/byteorder.h` selects ARM user-visible
endian helpers. It is part of the vendored Linux ARM code under the Ceph client source tree and has
26 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: __ARMEB__ branch to linux/byteorder/big_endian.h or
little_endian.h.
Visible dependencies include: `linux/byteorder/big_endian.h`, `linux/byteorder/little_endian.h`.
Important macros/constants include: `__ASM_ARM_BYTEORDER_H`.

## Control Flow
preprocessor state chooses the byteorder API during userspace or kernel header inclusion.

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: wrong endian selection corrupts all multi-byte UAPI structure interpretation. Changes
should preserve register layouts, numeric constants, early-boot calling conventions, and
userspace/module ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/fcntl.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/fcntl.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/fcntl.h` defines ARM-specific open
flag values before including the generic fcntl contract. It is part of the vendored Linux ARM code
under the Ceph client source tree and has 12 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: O_DIRECTORY, O_NOFOLLOW, O_DIRECT, O_LARGEFILE, and asm-
generic/fcntl.h.
Visible dependencies include: `asm-generic/fcntl.h`.
Important macros/constants include: `_ARM_FCNTL_H`, `O_DIRECTORY`, `O_NOFOLLOW`, `O_DIRECT`,
`O_LARGEFILE`.

## Control Flow
userspace sees these bit values as part of the open/openat ABI.

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: renumbering flags would break existing binaries and filesystem behavior. Changes
should preserve register layouts, numeric constants, early-boot calling conventions, and
userspace/module ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/fcntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/hwcap.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/hwcap.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/hwcap.h` defines ARM AT_HWCAP and
AT_HWCAP2 feature bits. It is part of the vendored Linux ARM code under the Ceph client source tree
and has 49 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: HWCAP_* CPU feature bits and HWCAP2_* crypto/speculation feature
bits.
Important macros/constants include: `_UAPI__ASMARM_HWCAP_H`, `HWCAP_SWP`, `HWCAP_HALF`,
`HWCAP_THUMB`, `HWCAP_26BIT`, `HWCAP_FAST_MULT`, `HWCAP_FPA`, `HWCAP_VFP`, `HWCAP_EDSP`,
`HWCAP_JAVA`, `HWCAP_IWMMXT`, `HWCAP_CRUNCH`, `HWCAP_THUMBEE`, `HWCAP_NEON`, `HWCAP_VFPv3`,
`HWCAP_VFPv3D16`, `HWCAP_TLS`, `HWCAP_VFPv4`, ... (37 total).

## Control Flow
kernel ELF setup fills auxv feature masks and libc/JITs dispatch on these values.

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: feature bit reuse or inaccurate exposure can crash optimized userspace code paths.
Changes should preserve register layouts, numeric constants, early-boot calling conventions, and
userspace/module ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/hwcap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/ioctls.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/ioctls.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/ioctls.h` adds ARM-specific ioctl
numbers before importing generic ioctl definitions. It is part of the vendored Linux ARM code under
the Ceph client source tree and has 9 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: FIOQSIZE and asm-generic/ioctls.h.
Visible dependencies include: `asm-generic/ioctls.h`.
Important macros/constants include: `__ASM_ARM_IOCTLS_H`, `FIOQSIZE`.

## Control Flow
terminal and file descriptor ioctl callers share these constants with the kernel.

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: ioctl number collisions or changes break userspace command decoding. Changes should
preserve register layouts, numeric constants, early-boot calling conventions, and userspace/module
ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/ioctls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/mman.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/mman.h` adds ARM mmap validation to
the generic memory mapping UAPI. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 4 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: arch_mmap_check(addr, len, flags).
Visible dependencies include: `asm-generic/mman.h`.
Important macros/constants include: `arch_mmap_check(addr, len, flags)`.

## Control Flow
MAP_FIXED mappings below FIRST_USER_ADDRESS are rejected before generic mmap processing.

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: weakening the check can allow userspace to map protected low addresses. Changes should
preserve register layouts, numeric constants, early-boot calling conventions, and userspace/module
ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/perf_regs.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/perf_regs.h` enumerates ARM register
IDs for perf sample register masks. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 24 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: enum perf_event_arm_regs from R0 through PC and PERF_REG_ARM_MAX.
Important macros/constants include: `_ASM_ARM_PERF_REGS_H`.

## Control Flow
perf_event_open users and perf tooling use these IDs to request and decode register samples.

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: changing enum order breaks perf data ABI and cross-tool decoding. Changes should
preserve register layouts, numeric constants, early-boot calling conventions, and userspace/module
ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/posix_types.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/posix_types.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/posix_types.h` defines ARM historical
kernel POSIX typedef widths before generic types. It is part of the vendored Linux ARM code under
the Ceph client source tree and has 38 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: __kernel_mode_t, __kernel_ipc_pid_t, __kernel_uid_t,
__kernel_gid_t, __kernel_old_dev_t.
Visible dependencies include: `asm-generic/posix_types.h`.
Important macros/constants include: `__ARCH_ARM_POSIX_TYPES_H`, `__kernel_mode_t`,
`__kernel_ipc_pid_t`, `__kernel_uid_t`, `__kernel_old_dev_t`.

## Control Flow
libc and userspace code include these aliases through exported kernel headers.

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: type-width changes alter structure layouts exposed by UAPI headers. Changes should
preserve register layouts, numeric constants, early-boot calling conventions, and userspace/module
ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/posix_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/ptrace.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/ptrace.h` defines ARM ptrace requests,
CPSR/PSR bits, register aliases, and user-visible pt_regs layout. It is part of the vendored Linux
ARM code under the Ceph client source tree and has 154 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: PTRACE_GET/SET* constants, mode bits, PSR masks, PT_* magic
offsets, struct pt_regs, ARM_* register macros, and ARM_VFPREGS_SIZE.
Visible dependencies include: `asm/hwcap.h`.
Important macros/constants include: `_UAPI__ASM_ARM_PTRACE_H`, `PTRACE_GETREGS`, `PTRACE_SETREGS`,
`PTRACE_GETFPREGS`, `PTRACE_SETFPREGS`, `PTRACE_GETWMMXREGS`, `PTRACE_SETWMMXREGS`,
`PTRACE_OLDSETOPTIONS`, `PTRACE_GET_THREAD_AREA`, `PTRACE_SET_SYSCALL`, `PTRACE_GETCRUNCHREGS`,
`PTRACE_SETCRUNCHREGS`, `PTRACE_GETVFPREGS`, `PTRACE_SETVFPREGS`, `PTRACE_GETHBPREGS`,
`PTRACE_SETHBPREGS`, `PTRACE_GETFDPIC`, `PTRACE_GETFDPIC_EXEC`, ... (77 total).

## Control Flow
debuggers and core dump code use these definitions to inspect or modify task register state.

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: any layout or numeric change breaks gdb, strace, crash dump readers, and old tracing
tools. Changes should preserve register layouts, numeric constants, early-boot calling conventions,
and userspace/module ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/setup.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/setup.h` defines the legacy ARM ATAG
boot parameter UAPI structures. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 188 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: COMMAND_LINE_SIZE, ATAG_* constants, struct tag_header, struct
tag_* payloads, struct tag, struct tagtable, tag_next(), tag_size(), and for_each_tag().
Visible dependencies include: `linux/types.h`.
Important macros/constants include: `_UAPI__ASMARM_SETUP_H`, `COMMAND_LINE_SIZE`, `ATAG_NONE`,
`ATAG_CORE`, `ATAG_MEM`, `ATAG_VIDEOTEXT`, `ATAG_RAMDISK`, `ATAG_INITRD`, `ATAG_INITRD2`,
`ATAG_SERIAL`, `ATAG_REVISION`, `ATAG_VIDEOLFB`, `ATAG_CMDLINE`, `ATAG_ACORN`, `ATAG_MEMCLK`,
`tag_member_present(tag,member)`, `tag_next(t)`, `tag_size(type)`, ... (19 total).

## Control Flow
boot loaders pass tag lists and kernel parsers walk them during setup_machine_tags().

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: structure changes break old boot loaders and procfs ATAG export consumers. Changes
should preserve register layouts, numeric constants, early-boot calling conventions, and
userspace/module ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/sigcontext.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/sigcontext.h` defines the signal frame
machine context saved for ARM signal delivery. It is part of the vendored Linux ARM code under the
Ceph client source tree and has 35 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: struct sigcontext with trap/error, register, CPSR, and
fault_address fields.
Important macros/constants include: `_ASMARM_SIGCONTEXT_H`.

## Control Flow
signal setup stores interrupted register state and sigreturn restores it through this stable layout.

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: inserting fields before the end would break userspace signal handlers and unwinders.
Changes should preserve register layouts, numeric constants, early-boot calling conventions, and
userspace/module ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/signal.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/signal.h` defines ARM signal numbers,
sigaction layout, altstack type, and ARM-specific flags. It is part of the vendored Linux ARM code
under the Ceph client source tree and has 100 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: NSIG, SIG* values, SIGRTMIN/MAX, SIGSWI, SA_THIRTYTWO, SA_RESTORER,
struct sigaction, and stack_t.
Visible dependencies include: `linux/types.h`, `asm-generic/signal-defs.h`.
Important macros/constants include: `_UAPI_ASMARM_SIGNAL_H`, `NSIG`, `SIGHUP`, `SIGINT`, `SIGQUIT`,
`SIGILL`, `SIGTRAP`, `SIGABRT`, `SIGIOT`, `SIGBUS`, `SIGFPE`, `SIGKILL`, `SIGUSR1`, `SIGSEGV`,
`SIGUSR2`, `SIGPIPE`, `SIGALRM`, `SIGTERM`, ... (46 total).

## Control Flow
libc and applications compile these constants into signal setup and handler dispatch.

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: signal number or struct layout changes are direct ABI breaks. Changes should preserve
register layouts, numeric constants, early-boot calling conventions, and userspace/module ABI
boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/stat.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/stat.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/stat.h` defines ARM old stat, stat,
and stat64 UAPI layouts. It is part of the vendored Linux ARM code under the Ceph client source tree
and has 88 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: struct __old_kernel_stat, STAT_HAVE_NSEC, struct stat, struct
stat64, STAT64_HAS_BROKEN_ST_INO.
Important macros/constants include: `_ASMARM_STAT_H`, `STAT_HAVE_NSEC`, `STAT64_HAS_BROKEN_ST_INO`.

## Control Flow
sys_stat family calls copy these exact layouts to userspace, including endian and padding rules.

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: padding or field width changes corrupt filesystem metadata observed by old binaries.
Changes should preserve register layouts, numeric constants, early-boot calling conventions, and
userspace/module ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/statfs.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/statfs.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/statfs.h` sets ARM statfs64 packing
before including the generic statfs ABI. It is part of the vendored Linux ARM code under the Ceph
client source tree and has 13 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: ARCH_PACK_STATFS64 and asm-generic/statfs.h.
Visible dependencies include: `asm-generic/statfs.h`.
Important macros/constants include: `_ASMARM_STATFS_H`, `ARCH_PACK_STATFS64`.

## Control Flow
dual ABI statfs64 handling relies on the packed/aligned attribute.

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: removing packing changes EABI/OABI compatibility around filesystem statistics. Changes
should preserve register layouts, numeric constants, early-boot calling conventions, and
userspace/module ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/statfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/swab.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/swab.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/swab.h` provides ARM byte-swap
optimization helpers for exported headers. It is part of the vendored Linux ARM code under the Ceph
client source tree and has 54 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: __SWAB_64_THRU_32__ and __arch_swab32().
Visible dependencies include: `linux/compiler.h`, `linux/types.h`.
Important macros/constants include: `_UAPI__ASM_ARM_SWAB_H`, `__SWAB_64_THRU_32__`, `__arch_swab32`.
C functions detected in this file include: `accesses()`.

## Control Flow
compilers can use inline ARM rotate/eor sequences for 32-bit byte swaps when appropriate.

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: inline asm constraints and Thumb handling must remain compiler-compatible. Changes
should preserve register layouts, numeric constants, early-boot calling conventions, and
userspace/module ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/types.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/types.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/types.h` aligns ARM exported integer
type builtin definitions with kernel expectations. It is part of the vendored Linux ARM code under
the Ceph client source tree and has 41 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: include of asm-generic/int-ll64.h and overrides for __INT32_TYPE__,
__UINT32_TYPE__, __UINTPTR_TYPE__.
Visible dependencies include: `asm-generic/int-ll64.h`.
Important macros/constants include: `_UAPI_ASM_TYPES_H`, `__INT32_TYPE__`, `__UINT32_TYPE__`,
`__UINTPTR_TYPE__`.

## Control Flow
freestanding users that include linux/types.h and stdint.h get consistent ARM typedefs.

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: incorrect builtin overrides produce type conflicts in NEON/freestanding builds.
Changes should preserve register layouts, numeric constants, early-boot calling conventions, and
userspace/module ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/unistd.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/unistd.h` selects ARM EABI or OABI
syscall number headers and defines ARM-private SWIs. It is part of the vendored Linux ARM code under
the Ceph client source tree and has 41 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: __NR_OABI_SYSCALL_BASE, __NR_SYSCALL_MASK, __NR_SYSCALL_BASE,
unistd-eabi.h/unistd-oabi.h includes, __NR_sync_file_range2 alias, and __ARM_NR_*.
Visible dependencies include: `asm/unistd-eabi.h`, `asm/unistd-oabi.h`.
Important macros/constants include: `_UAPI__ASM_ARM_UNISTD_H`, `__NR_OABI_SYSCALL_BASE`,
`__NR_SYSCALL_MASK`, `__NR_SYSCALL_BASE`, `__NR_sync_file_range2`, `__ARM_NR_BASE`,
`__ARM_NR_breakpoint`, `__ARM_NR_cacheflush`, `__ARM_NR_usr26`, `__ARM_NR_usr32`,
`__ARM_NR_set_tls`, `__ARM_NR_get_tls`.

## Control Flow
the syscall entry path and libc agree on the syscall base and private ARM SWI range.

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: wrong base selection breaks every syscall for the affected ABI. Changes should
preserve register layouts, numeric constants, early-boot calling conventions, and userspace/module
ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/Makefile

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/Makefile` builds the ARM kernel architecture
object list. It is part of the vendored Linux ARM code under the Ceph client source tree and has 106
source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: obj-y and obj-$(CONFIG_*) selections, tracing sanitizer removals,
generated vmlinux.lds, and head$(MMUEXT).o.
No standalone symbols are declared beyond build-system or include-level directives.

## Control Flow
Kbuild composes entry, setup, MMU, tracing, PCI, FIQ, hibernation, EFI, and debug objects according
to configuration.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: missing or over-broad object selection can make a kernel unbootable or expose
unsupported ABI paths. Changes should preserve register layouts, numeric constants, early-boot
calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/arch_timer.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/arch_timer.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/arch_timer.c` registers the ARM architected
timer as the delay loop source. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 42 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: arch_timer_read_counter_long(), arch_timer_delay_timer_register(),
arch_timer_arch_init(), and arch_delay_timer.
Visible dependencies include: `linux/init.h`, `linux/types.h`, `linux/errno.h`, `asm/delay.h`,
`asm/arch_timer.h`, `clocksource/arm_arch_timer.h`.
C functions detected in this file include: `Copyright()`, `arch_timer_delay_timer_register()`,
`arch_timer_arch_init()`.

## Control Flow
init checks the timer rate, installs read_current_timer/freq, and registers current_timer_delay.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: a zero or wrong timer rate makes udelay-style loops inaccurate or unavailable. Changes
should preserve register layouts, numeric constants, early-boot calling conventions, and
userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/arch_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/armksyms.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/armksyms.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/armksyms.c` exports ARM architecture helper
symbols for loadable modules. It is part of the vendored Linux ARM code under the Ceph client source
tree and has 177 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: EXPORT_SYMBOL entries for checksums, raw IO, string/memory helpers,
user accessors, libgcc/AEABI helpers, bitops, ftrace, phys/virt patching, and SMCCC.
Visible dependencies include: `linux/export.h`, `linux/sched.h`, `linux/string.h`, `linux/delay.h`,
`linux/in6.h`, `linux/syscalls.h`, `linux/uaccess.h`, `linux/io.h`, `linux/arm-smccc.h`,
`asm/checksum.h`, `asm/ftrace.h`.

## Control Flow
module linking resolves these symbols against the core kernel export table.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: removing exports breaks out-of-tree and in-tree modules that depend on ARM helper
routines. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/armksyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/asm-offsets.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/asm-offsets.c` generates assembler-visible
structure offsets and constants. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 174 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: DEFINE() entries for task/thread_info/pt_regs/svc_pt_regs/signal
frames/machine_desc/proc_info/cache/MPU/kexec/SMCCC constants.
Visible dependencies include: `linux/compiler.h`, `linux/sched.h`, `linux/mm.h`, `linux/dma-
mapping.h`, `asm/cacheflush.h`, `asm/kexec-internal.h`, `asm/glue-df.h`, `asm/glue-pf.h`,
`asm/mach/arch.h`, `asm/thread_info.h`, `asm/page.h`, `asm/mpu.h`, `asm/procinfo.h`,
`asm/suspend.h`, ... (19 total).
Important macros/constants include: `COMPILE_OFFSETS`.
C functions detected in this file include: `Copyright()`.

## Control Flow
the kbuild offsets pass compiles and post-processes this C file into asm-offsets.h consumed by
assembly files.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: offset drift between C structs and assembly save/restore code causes silent register,
stack, or task-state corruption. Changes should preserve register layouts, numeric constants, early-
boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/atags.h -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/atags.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/atags.h` declares internal ATAG setup helpers.
It is part of the vendored Linux ARM code under the Ceph client source tree and has 15 source lines
in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: convert_to_tag_list() and setup_machine_tags() or the no-ATAGS
fatal inline.
C functions detected in this file include: `setup_machine_tags()`.

## Control Flow
head/setup code calls setup_machine_tags when legacy boot tags are used.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: building without CONFIG_ATAGS intentionally traps legacy ATAG-only boots. Changes
should preserve register layouts, numeric constants, early-boot calling conventions, and
userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/atags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/atags_compat.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/atags_compat.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/atags_compat.c` converts deprecated ARM
param_struct boot data into ATAG lists. It is part of the vendored Linux ARM code under the Ceph
client source tree and has 214 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: struct param_struct, memtag(), build_tag_list(), and
convert_to_tag_list().
Visible dependencies include: `linux/types.h`, `linux/kernel.h`, `linux/string.h`, `linux/init.h`,
`asm/setup.h`, `asm/mach-types.h`, `asm/page.h`, `asm/mach/arch.h`, `atags.h`.
Important macros/constants include: `FLAG_READONLY`, `FLAG_RDLOAD`, `FLAG_RDPROMPT`.
C functions detected in this file include: `memtag()`, `build_tag_list()`, `convert_to_tag_list()`.

## Control Flow
old boot parameters are validated, translated into
core/ramdisk/initrd/serial/revision/memory/cmdline tags, then copied back over the source buffer.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: the converter relies on legacy fixed layout and uses early memory assumptions, so
malformed boot data can produce wrong memory or command-line state. Changes should preserve register
layouts, numeric constants, early-boot calling conventions, and userspace/module ABI boundaries
implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/atags_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/atags_parse.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/atags_parse.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/atags_parse.c` parses legacy ARM ATAG boot lists
into kernel setup state. It is part of the vendored Linux ARM code under the Ceph client source tree
and has 230 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: default_tags, parse_tag_* handlers, __tagtable registrations,
parse_tags(), squash_mem_tags(), and setup_machine_tags().
Visible dependencies include: `linux/init.h`, `linux/initrd.h`, `linux/kernel.h`, `linux/fs.h`,
`linux/root_dev.h`, `linux/screen_info.h`, `linux/memblock.h`, `uapi/linux/mount.h`, `asm/setup.h`,
`asm/system_info.h`, `asm/page.h`, `asm/mach/arch.h`, `atags.h`.
Important macros/constants include: `MEM_SIZE`.
C functions detected in this file include: `parse_tag_core()`, `parse_tag_mem32()`,
`parse_tag_videotext()`, `parse_tag_ramdisk()`, `parse_tag_serialnr()`, `parse_tag_revision()`,
`parse_tag_cmdline()`, `parse_tag()`, `parse_tags()`, `squash_mem_tags()`, `setup_machine_tags()`,
`for_each_machine_desc()`.

## Control Flow
machine_desc lookup selects a board, optional param conversion and fixups run, memory tags are
parsed unless memblock already has memory, and boot_command_line is populated.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: bad ATAG validation or command-line policy can boot with wrong memory, root device,
initrd, or machine descriptor. Changes should preserve register layouts, numeric constants, early-
boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/atags_parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/atags_proc.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/atags_proc.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/atags_proc.c` exports a saved copy of boot ATAGs
through procfs. It is part of the vendored Linux ARM code under the Ceph client source tree and has
76 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: save_atags(), atags_read(), init_atags_procfs(), BOOT_PARAMS_SIZE,
and /proc/atags creation.
Visible dependencies include: `linux/slab.h`, `linux/proc_fs.h`, `asm/setup.h`, `asm/types.h`,
`asm/page.h`.
Important macros/constants include: `BOOT_PARAMS_SIZE`.
C functions detected in this file include: `atags_read()`, `save_atags()`, `init_atags_procfs()`.

## Control Flow
early setup copies fixed-size ATAG data, later arch_initcall allocates a right-sized buffer and
exposes it read-only.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: truncated or invalid ATAG copies reduce diagnostics for legacy boot paths. Changes
should preserve register layouts, numeric constants, early-boot calling conventions, and
userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/atags_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/bios32.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/bios32.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/bios32.c` implements ARM PCI BIOS-style host
bridge setup and fixups. It is part of the vendored Linux ARM code under the Ceph client source tree
and has 596 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: pcibios_report_status(), PCI fixups, pcibios_fixup_bus(),
pcibios_swizzle(), pcibios_map_irq(), pcibios_init_hw(), pci_common_init_dev(),
pcibios_align_resource(), and pci_map_io_early().
Visible dependencies include: `linux/export.h`, `linux/kernel.h`, `linux/pci.h`, `linux/slab.h`,
`linux/string_choices.h`, `linux/init.h`, `linux/io.h`, `asm/mach-types.h`, `asm/mach/map.h`,
`asm/mach/pci.h`.
C functions detected in this file include: `pcibios_bus_report_status()`, `list_for_each_entry()`,
`pcibios_report_status()`, `pci_fixup_83c553()`, `pci_fixup_unassign()`, `layer()`,
`pci_dev_for_each_resource()`, `pci_fixup_ide_bases()`, `pci_fixup_dec21142()`,
`pci_fixup_cy82c693()`, `pdev_bad_for_parity()`, `pcibios_fixup_bus()`, `pcibios_swizzle()`,
`pcibios_map_irq()`, `pcibios_init_resource()`, `pcibios_init_hw()`, `pci_common_init_dev()`,
`pci_bus_claim_resources()`, ... (22 total).

## Control Flow
platform hw_pci callbacks set up bridges, resources are claimed or assigned, interrupts are
swizzled/mapped, and devices are added.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: resource alignment, legacy bridge fixups, and IRQ mapping are platform-sensitive and
can break PCI enumeration. Changes should preserve register layouts, numeric constants, early-boot
calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/bios32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/bugs.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/bugs.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/bugs.c` runs ARM CPU bug checks during final
architecture CPU init. It is part of the vendored Linux ARM code under the Ceph client source tree
and has 19 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: check_other_bugs() and arch_cpu_finalize_init().
Visible dependencies include: `linux/init.h`, `linux/cpu.h`, `asm/bugs.h`, `asm/proc-fns.h`.
C functions detected in this file include: `check_other_bugs()`, `arch_cpu_finalize_init()`.

## Control Flow
write-buffer bug checks and optional processor-specific cpu_check_bugs run after CPU setup.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: skipping checks may leave required CPU erratum workarounds disabled. Changes should
preserve register layouts, numeric constants, early-boot calling conventions, and userspace/module
ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/bugs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/cacheinfo.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/cacheinfo.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/cacheinfo.c` populates generic cacheinfo from
ARM cache type registers and device tree. It is part of the vendored Linux ARM code under the Ceph
client source tree and has 173 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: cache_line_size_cp15(), cache_line_size(), get_cache_type(),
detect_cache_level(), early_cache_level(), init_cache_level(), and populate_cache_leaves().
Visible dependencies include: `linux/bitfield.h`, `linux/cacheinfo.h`, `linux/of.h`,
`asm/cachetype.h`, `asm/cputype.h`, `asm/system_info.h`.
Important macros/constants include: `CLIDR_CTYPE_SHIFT(level)`, `CLIDR_CTYPE_MASK(level)`,
`CLIDR_CTYPE(clidr, level)`, `MAX_CACHE_LEVEL`, `CTR_FORMAT_MASK`, `CTR_FORMAT_ARMV6`,
`CTR_FORMAT_ARMV7`, `CTR_CWG_MASK`, `CTR_DSIZE_LEN_MASK`, `CTR_ISIZE_LEN_MASK`.
C functions detected in this file include: `Copyright()`, `cache_line_size()`, `get_cache_type()`,
`ci_leaf_init()`, `detect_cache_level()`, `early_cache_level()`, `init_cache_level()`,
`populate_cache_leaves()`.

## Control Flow
CTR/CLIDR reads derive levels/leaves, DT can extend external unified cache levels, and generic
cacheinfo leaves are filled per CPU.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: old CPU formats, missing CLIDR, or wrong DT external cache levels can mislead DMA
alignment and sysfs cache reporting. Changes should preserve register layouts, numeric constants,
early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/cacheinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/cpuidle.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/cpuidle.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/cpuidle.c` connects ARM CPU idle states to DT-
selected low-level cpuidle operations. It is part of the vendored Linux ARM code under the Ceph
client source tree and has 148 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: arm_cpuidle_simple_enter(), arm_cpuidle_suspend(),
arm_cpuidle_get_ops(), arm_cpuidle_read_ops(), and arm_cpuidle_init().
Visible dependencies include: `linux/cpuidle.h`, `linux/of.h`, `asm/cpuidle.h`.
C functions detected in this file include: `arm_cpuidle_simple_enter()`, `arm_cpuidle_suspend()`,
`arm_cpuidle_get_ops()`, `arm_cpuidle_read_ops()`, `arm_cpuidle_init()`.

## Control Flow
per-CPU enable-method strings select init/suspend callbacks from the linker table, then cpuidle
suspend calls the copied per-CPU op.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: missing or wrong enable-method values disable idle states or call incompatible
platform suspend code. Changes should preserve register layouts, numeric constants, early-boot
calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/cpuidle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/crash_dump.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/crash_dump.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/crash_dump.c` copies pages from a crashed
kernel's old memory image. It is part of the vendored Linux ARM code under the Ceph client source
tree and has 35 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: copy_oldmem_page().
Visible dependencies include: `linux/errno.h`, `linux/crash_dump.h`, `linux/uaccess.h`,
`linux/io.h`, `linux/uio.h`.
C functions detected in this file include: `Copyright()`.

## Control Flow
the crash dump reader ioremaps the requested PFN, copies bytes to an iov_iter, and unmaps it.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: ioremap failures or offset/size mistakes prevent vmcore extraction. Changes should
preserve register layouts, numeric constants, early-boot calling conventions, and userspace/module
ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/crash_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/debug.S -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/debug.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/debug.S` provides low-level ARM debug printing
helpers used before normal consoles. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 161 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: printhex8/4/2, printascii, printch, debug_ll_addr, and
addruart_current.
Visible dependencies include: `linux/linkage.h`, `asm/assembler.h`.
Assembly entry points detected in this file include: `printhex8`, `printhex4`, `printhex2`,
`printascii`, `printch`, `debug_ll_addr`.

## Control Flow
the code selects physical or virtual UART address depending on MMU state, emits CRLF-normalized
strings, or uses semihosting calls.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: these routines are unsafe for production paths and can hang if the DEBUG_LL backend
cannot access the UART. Changes should preserve register layouts, numeric constants, early-boot
calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/debug.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/devtree.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/devtree.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/devtree.c` handles ARM machine selection and CPU
map setup from flattened device tree. It is part of the vendored Linux ARM code under the Ceph
client source tree and has 238 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: arm_dt_init_cpu_maps(), arch_match_cpu_phys_id(),
arch_get_next_mach(), and setup_machine_fdt().
Visible dependencies include: `linux/init.h`, `linux/export.h`, `linux/errno.h`, `linux/types.h`,
`linux/memblock.h`, `linux/of.h`, `linux/of_fdt.h`, `linux/of_irq.h`, `linux/smp.h`,
`asm/cputype.h`, `asm/setup.h`, `asm/page.h`, `asm/prom.h`, `asm/smp_plat.h`, ... (16 total).
C functions detected in this file include: `set_smp_ops_by_method()`, `arm_dt_init_cpu_maps()`,
`for_each_of_cpu_node()`, `smp_setup_processor_id()`, `arch_match_cpu_phys_id()`,
`arch_get_next_mach()`, `setup_machine_fdt()`.

## Control Flow
DT verification, compatible matching, CPU MPIDR parsing, SMP enable-method lookup, DT fixups, and
early node scanning happen before normal platform setup.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: bad CPU reg properties or compatible lists can cap CPUs, choose wrong smp_ops, or stop
boot with an unsupported machine table dump. Changes should preserve register layouts, numeric
constants, early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/devtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/dma.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/dma.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/dma.c` implements the legacy ISA DMA API
frontend for ARM platforms. It is part of the vendored Linux ARM code under the Ceph client source
tree and has 283 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: isa_dma_add(), request_dma(), free_dma(), set_dma_sg(),
__set_dma_addr(), set_dma_count(), set_dma_mode(), enable_dma(), disable_dma(),
dma_channel_active(), set_dma_speed(), get_dma_residue(), and proc_dma_show().
Visible dependencies include: `linux/module.h`, `linux/init.h`, `linux/spinlock.h`, `linux/errno.h`,
`linux/scatterlist.h`, `linux/seq_file.h`, `linux/proc_fs.h`, `asm/dma.h`, `asm/mach/dma.h`.
C functions detected in this file include: `isa_dma_add()`, `request_dma()`, `free_dma()`,
`set_dma_sg()`, `__set_dma_addr()`, `set_dma_count()`, `set_dma_mode()`, `enable_dma()`,
`disable_dma()`, `dma_channel_active()`, `set_dma_page()`, `set_dma_speed()`, `get_dma_residue()`,
`proc_dma_show()`, `proc_dma_init()`.

## Control Flow
registered platform dma_t channels are locked, configured, enabled/disabled through d_ops, and
optionally reported in /proc/dma.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: the API has global channel state and BUG paths when callers enable or disable
unallocated DMA channels. Changes should preserve register layouts, numeric constants, early-boot
calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/early_printk.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/early_printk.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/early_printk.c` registers an early console
backed by DEBUG_LL printascii. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 47 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: early_write(), early_console_write(), early_console_dev, and
setup_early_printk().
Visible dependencies include: `linux/kernel.h`, `linux/console.h`, `linux/init.h`, `linux/string.h`.
C functions detected in this file include: `early_write()`, `early_console_write()`,
`setup_early_printk()`.

## Control Flow
the earlyprintk boot parameter installs a boot console that chunks writes through printascii.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: the console depends entirely on low-level debug address correctness and fixed 128-byte
chunking. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/early_printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/efi.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/efi.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/efi.c` maps EFI runtime memory and validates ARM
EFI entry state. It is part of the vendored Linux ARM code under the Ceph client source tree and has
130 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: set_permissions(), efi_set_mapping_permissions(),
efi_create_mapping(), efi_arch_tables, load_cpu_state_table(), and arm_efi_init().
Visible dependencies include: `linux/efi.h`, `linux/memblock.h`, `linux/screen_info.h`, `asm/efi.h`,
`asm/mach/map.h`, `asm/mmu_context.h`.
C functions detected in this file include: `Copyright()`, `efi_set_mapping_permissions()`,
`efi_create_mapping()`, `load_cpu_state_table()`, `arm_efi_init()`.

## Control Flow
EFI memory descriptors become late mappings with cache/device types and optional RO/XN permissions,
then CPU state table diagnostics run.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: section mappings may skip fine-grained permission changes, and buggy firmware state is
only warned about. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/efi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/elf.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/elf.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/elf.c` implements ARM ELF binary checks and
personality setup. It is part of the vendored Linux ARM code under the Ceph client source tree and
has 133 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: elf_check_arch(), elf_set_personality(),
arm_elf_read_implies_exec(), and elf_fdpic_arch_lay_out_mm().
Visible dependencies include: `linux/export.h`, `linux/sched.h`, `linux/personality.h`,
`linux/binfmts.h`, `linux/elf.h`, `linux/elf-fdpic.h`, `asm/system_info.h`.
C functions detected in this file include: `elf_check_arch()`, `elf_set_personality()`,
`softfloat()`, `elf_read_implies_exec()`, `elf_fdpic_arch_lay_out_mm()`.

## Control Flow
exec validates EM_ARM, entry alignment, EABI/OABI flags, VFP/hwcap compatibility, sets
personality/IWMMXT flags, and decides READ_IMPLIES_EXEC behavior.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: loosening checks can run binaries with unsupported instruction sets or unsafe
executable mapping policy. Changes should preserve register layouts, numeric constants, early-boot
calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/elf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/entry-armv.S -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/entry-armv.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/entry-armv.S` implements classic ARM exception
vectors, SVC/IRQ/abort/undefined/FIQ entry, context switching, and kuser helpers. It is part of the
vendored Linux ARM code under the Ceph client source tree and has 1127 source lines in this
checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: irq_handler, pabt_helper, dabt_helper, svc_entry, usr_entry,
__switch_to, ret_from_exception, vector_stub variants, vector_swi references, and kuser helper area.
Visible dependencies include: `linux/init.h`, `asm/assembler.h`, `asm/page.h`, `asm/glue-df.h`,
`asm/glue-pf.h`, `asm/vfpmacros.h`, `asm/thread_notify.h`, `asm/unwind.h`, `asm/unistd.h`,
`asm/tls.h`, `asm/system_info.h`, `asm/uaccess-asm.h`, `asm/kasan_def.h`, `entry-header.S`, ... (15
total).
Important macros/constants include: `RELOC_TEXT_NONE`, `SPFIX(code...)`.
Assembly entry points detected in this file include: `ret_from_exception`, `__switch_to`.

## Control Flow
exceptions save pt_regs-compatible frames, dispatch C handlers or syscall logic, restore user/kernel
state, and preserve ABI-visible helper code.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: tiny ordering changes can corrupt register frames, preemption state, syscall restart,
BHB mitigations, or user ABI helpers. Changes should preserve register layouts, numeric constants,
early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/entry-armv.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/entry-common.S -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/entry-common.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/entry-common.S` implements ARM syscall return
paths and syscall tables. It is part of the vendored Linux ARM code under the Ceph client source
tree and has 464 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: ret_fast_syscall, ret_to_user, ret_from_fork, vector_swi,
__sys_trace, syscall_table_start/end, sys_syscall, sigreturn wrappers, mmap2, and OABI wrappers.
Visible dependencies include: `asm/assembler.h`, `asm/unistd.h`, `asm/ftrace.h`, `asm/unwind.h`,
`asm/page.h`, `asm/unistd-oabi.h`, `entry-header.S`, `calls-eabi.S`, `calls-oabi.S`.
Important macros/constants include: `TRACE(x...)`, `__SYSCALL_WITH_COMPAT(nr, native, compat)`,
`__SYSCALL(nr, func)`.
Assembly entry points detected in this file include: `ret_to_user`, `ret_to_user_from_irq`,
`ret_from_fork`, `vector_bhb_loop8_swi`, `vector_bhb_bpiall_swi`, `vector_swi`, `\sym`.

## Control Flow
SVC decode selects EABI/OABI syscall numbers, handles tracing/seccomp/restarts, invokes syscall
tables, and returns through work-pending checks.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: syscall table ordering and ABI wrapper behavior are hard userspace ABI contracts.
Changes should preserve register layouts, numeric constants, early-boot calling conventions, and
userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/entry-common.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/entry-ftrace.S -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/entry-ftrace.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/entry-ftrace.S` implements ARM ftrace and
function graph assembly trampolines. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 302 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: __gnu_mcount_nc, ftrace_caller, ftrace_regs_caller,
ftrace_graph_caller, return_to_handler, ftrace_stub, and init trampolines.
Visible dependencies include: `asm/assembler.h`, `asm/ftrace.h`, `asm/unwind.h`, `entry-header.S`.
Assembly entry points detected in this file include: `__gnu_mcount_nc`, `ftrace_caller`,
`ftrace_regs_caller`, `ftrace_graph_caller`, `ftrace_graph_regs_caller`, `return_to_handler`,
`ftrace_stub`, `ftrace_stub_graph`, `\dst\(`.

## Control Flow
mcount call sites save registers, call dynamic ftrace hooks, optionally enter graph tracing, and
restore execution.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: register save layout must match ftrace.c and unwinder expectations or tracing corrupts
kernel execution. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/entry-ftrace.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/entry-header.S -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/entry-header.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/entry-header.S` provides shared ARM exception
entry/exit assembly macros. It is part of the vendored Linux ARM code under the Ceph client source
tree and has 467 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: zero_fp, alignment_trap, v7m_exception_entry,
v7m_exception_slow_exit, store/load_user_sp_lr, svc_exit, restore_user_regs, ct_user_enter/exit,
invoke_syscall, and do_overflow_check.
Visible dependencies include: `linux/init.h`, `linux/linkage.h`, `asm/assembler.h`, `asm/asm-
offsets.h`, `asm/errno.h`, `asm/thread_info.h`, `asm/uaccess-asm.h`, `asm/v7m.h`.
Important macros/constants include: `BAD_PREFETCH`, `BAD_DATA`, `BAD_ADDREXCPTN`, `BAD_IRQ`,
`BAD_UNDEFINSTR`, `S_OFF`, `ATRAP(x...)`.

## Control Flow
included entry files use these macros to build frames, switch context tracking, invoke syscalls, and
restore user mode.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: macro changes affect several entry files simultaneously and can break stack overflow
checks, uaccess state, or register restore order. Changes should preserve register layouts, numeric
constants, early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/entry-header.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/entry-v7m.S -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/entry-v7m.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/entry-v7m.S` implements ARMv7-M exception entry
and context switching. It is part of the vendored Linux ARM code under the Ceph client source tree
and has 160 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: __invalid_entry, __irq_entry, __pendsv_entry, __switch_to,
vector_table, and exc_ret.
Visible dependencies include: `asm/page.h`, `asm/glue.h`, `asm/thread_notify.h`, `asm/v7m.h`,
`entry-header.S`.
Assembly entry points detected in this file include: `__switch_to`, `vector_table`.

## Control Flow
M-profile exceptions enter through a vector table, construct frames via shared macros, dispatch
IRQ/PendSV, and switch thread state.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: V7M has different PSR/mode semantics, so classic ARM assumptions in entry code are
unsafe here. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/entry-v7m.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/fiq.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/fiq.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/fiq.c` implements ARM FIQ ownership, handler
installation, and exported control API. It is part of the vendored Linux ARM code under the Ceph
client source tree and has 166 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: fiq_handler ownership stack, set_fiq_handler(), claim_fiq(),
release_fiq(), enable_fiq(), disable_fiq(), show_fiq_list(), and init_FIQ().
Visible dependencies include: `linux/module.h`, `linux/kernel.h`, `linux/init.h`,
`linux/interrupt.h`, `linux/seq_file.h`, `asm/cacheflush.h`, `asm/cp15.h`, `asm/fiq.h`,
`asm/mach/irq.h`, `asm/irq.h`, `asm/traps.h`.
Important macros/constants include: `FIQ_OFFSET`.
C functions detected in this file include: `fiq_def_op()`, `show_fiq_list()`, `set_fiq_handler()`,
`claim_fiq()`, `release_fiq()`, `enable_fiq()`, `disable_fiq()`, `init_FIQ()`.

## Control Flow
drivers claim FIQ, install vector code and banked registers, and prior owners can
relinquish/reacquire control.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: FIQ is not shareable, vector patching requires I-cache maintenance, and incorrect
release order is diagnosed but dangerous. Changes should preserve register layouts, numeric
constants, early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/fiq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/fiqasm.S -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/fiqasm.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/fiqasm.S` implements banked FIQ register get/set
helpers. It is part of the vendored Linux ARM code under the Ceph client source tree and has 49
source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: __set_fiq_regs and __get_fiq_regs.
Visible dependencies include: `linux/linkage.h`, `asm/assembler.h`.
Assembly entry points detected in this file include: `__set_fiq_regs`, `__get_fiq_regs`.

## Control Flow
the helpers switch CPSR to FIQ mode with IRQ/FIQ masked, load or store r8-r12/sp/lr, then restore
the prior CPSR.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: interrupts in FIQ mode are fatal, so mode switching and hazard nops must remain exact.
Changes should preserve register layouts, numeric constants, early-boot calling conventions, and
userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/fiqasm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/ftrace.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/ftrace.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/ftrace.c` patches ARM ftrace call sites and
handles function graph return rewriting. It is part of the vendored Linux ARM code under the Ceph
client source tree and has 323 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: arch_ftrace_update_code(), ftrace_make_call(),
ftrace_modify_call(), ftrace_make_nop(), ftrace_update_ftrace_func(), prepare_ftrace_return(), and
graph caller enable/disable helpers.
Visible dependencies include: `linux/ftrace.h`, `linux/uaccess.h`, `linux/module.h`,
`linux/stop_machine.h`, `asm/cacheflush.h`, `asm/opcodes.h`, `asm/ftrace.h`, `asm/insn.h`,
`asm/set_memory.h`, `asm/stacktrace.h`, `asm/text-patching.h`.
Important macros/constants include: `NOP`.
C functions detected in this file include: `__ftrace_modify_code()`, `arch_ftrace_update_code()`,
`ftrace_nop_replace()`, `adjust_address()`, `ftrace_arch_code_modify_prepare()`,
`ftrace_arch_code_modify_post_process()`, `ftrace_call_replace()`, `ftrace_modify_code()`,
`ftrace_update_ftrace_func()`, `ftrace_make_call()`, `ftrace_modify_call()`, `ftrace_make_nop()`,
`prepare_ftrace_return()`, `__ftrace_modify_caller()`, `ftrace_modify_graph_caller()`,
`ftrace_enable_ftrace_graph_caller()`, `ftrace_disable_ftrace_graph_caller()`.

## Control Flow
stop_machine-driven text patching replaces mcount sequences with NOP or branch-link instructions and
graph tracing swaps return addresses.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: instruction encoding, module PLT reachability, init-text veneers, and cache/TLB
synchronization are critical. Changes should preserve register layouts, numeric constants, early-
boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/head-common.S -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/head-common.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/head-common.S` contains shared ARM early boot
code after MMU/MPU transition. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 239 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: __vet_atags, __mmap_switched, lookup_processor_type,
__lookup_processor_type, __error_lpae, __error_p, and __error.
Visible dependencies include: `asm/assembler.h`.
Important macros/constants include: `ATAG_CORE`, `ATAG_CORE_SIZE`, `ATAG_CORE_SIZE_EMPTY`,
`OF_DT_MAGIC`.
Assembly entry points detected in this file include: `lookup_processor_type`.

## Control Flow
boot validates ATAG/DTB pointers, clears BSS, copies/decompresses XIP data, stores
processor/machine/ATAG state, and jumps to start_kernel.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: early code runs before allocators and normal mappings, so address assumptions and
register contracts are strict. Changes should preserve register layouts, numeric constants, early-
boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/head-common.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/head-inflate-data.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/head-inflate-data.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/head-inflate-data.c` inflates XIP compressed
kernel data during earliest boot. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 56 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: __inflate_kernel_data().
Visible dependencies include: `linux/init.h`, `linux/zutil.h`, `head.h`,
`../../../lib/zlib_inflate/inftrees.h`, `../../../lib/zlib_inflate/inflate.h`,
`../../../lib/zlib_inflate/infutil.h`.
C functions detected in this file include: `__inflate_kernel_data()`.

## Control Flow
a stack-allocated zlib stream inflates data from __data_loc into _sdata before BSS clearing and
start_kernel.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: the code runs with a temporary stack and no allocator, so frame size and zlib
workspace assumptions are boot-critical. Changes should preserve register layouts, numeric
constants, early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/head-inflate-data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/head-nommu.S -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/head-nommu.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/head-nommu.S` implements ARM no-MMU and MPU
kernel startup. It is part of the vendored Linux ARM code under the Ceph client source tree and has
536 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: stext, secondary_startup, __after_proc_init, __setup_mpu,
__setup_pmsa_v7/v8, and secondary MPU setup helpers.
Visible dependencies include: `linux/linkage.h`, `linux/init.h`, `linux/errno.h`, `asm/assembler.h`,
`asm/ptrace.h`, `asm/asm-offsets.h`, `asm/page.h`, `asm/cp15.h`, `asm/thread_info.h`, `asm/v7m.h`,
`asm/mpu.h`, `head-common.S`.
Assembly entry points detected in this file include: `stext`, `secondary_startup`, `__setup_mpu`,
`__setup_pmsa_v7`, `__setup_pmsa_v8`, `__secondary_setup_mpu`, `__secondary_setup_pmsa_v7`,
`__secondary_setup_pmsa_v8`.

## Control Flow
startup identifies CPU type, optionally programs MPU regions, calls processor init, enables control
bits, and enters shared mmap-switched code.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: MPU region sizing and PMSA version handling determine whether RAM, vectors, XIP ROM,
and background regions are accessible and protected. Changes should preserve register layouts,
numeric constants, early-boot calling conventions, and userspace/module ABI boundaries implied by
this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/head-nommu.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/head.S -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/head.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/head.S` implements MMU-enabled ARM kernel
startup and initial page tables. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 602 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: stext, __create_page_tables, secondary_startup,
__secondary_switched, __enable_mmu, __turn_mmu_on, __fixup_smp, __do_fixup_smp_on_up, and fixup_smp.
Visible dependencies include: `linux/linkage.h`, `linux/init.h`, `linux/pgtable.h`,
`asm/assembler.h`, `asm/cp15.h`, `asm/domain.h`, `asm/ptrace.h`, `asm/asm-offsets.h`, `asm/page.h`,
`asm/thread_info.h`, `head-common.S`.
Important macros/constants include: `KERNEL_RAM_VADDR`, `PG_DIR_SIZE`, `PMD_ENTRY_ORDER`,
`XIP_START`.
Assembly entry points detected in this file include: `stext`, `secondary_startup_arm`,
`secondary_startup`, `__secondary_switched`, `__turn_mmu_on`, `fixup_smp`.

## Control Flow
primary boot validates CPU/LPAE/ATAGs, builds identity and kernel mappings, maps debug UART and boot
params, enables the MMU, then jumps to __mmap_switched; secondary CPUs use supplied page tables.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: page-table layout, physical/virtual patching, and SMP-on-UP fixups are extremely
sensitive to alignment and CPU capability bits. Changes should preserve register layouts, numeric
constants, early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/head.h -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/head.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/head.h` declares symbols shared by XIP data
inflation code and early boot assembly. It is part of the vendored Linux ARM code under the Ceph
client source tree and has 7 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: __data_loc, _edata_loc, _sdata, and __inflate_kernel_data().
No standalone symbols are declared beyond build-system or include-level directives.

## Control Flow
head-common.S and head-inflate-data.c agree on data source/destination symbols through this header.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: symbol mismatch breaks XIP data copy or decompression before the kernel is fully
initialized. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/head.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/hibernate.c -->
# sources/distributed-fs/ceph-client/arch/arm/kernel/hibernate.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/hibernate.c` implements ARM hibernation save and
resume hooks. It is part of the vendored Linux ARM code under the Ceph client source tree and has
105 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: pfn_is_nosave(), save_processor_state(), restore_processor_state(),
arch_save_image(), swsusp_arch_suspend(), arch_restore_image(), resume_stack, and
swsusp_arch_resume().
Visible dependencies include: `linux/mm.h`, `linux/suspend.h`, `asm/system_misc.h`, `asm/idmap.h`,
`asm/suspend.h`, `asm/page.h`, `asm/sections.h`, `reboot.h`.
C functions detected in this file include: `Copyright()`, `save_processor_state()`,
`restore_processor_state()`, `swsusp_save()`, `swsusp_arch_suspend()`, `arch_restore_image()`,
`swsusp_arch_resume()`.

## Control Flow
suspend copies the image through cpu_suspend, resume restores nosave pages from PBEs and calls
cpu_resume on a nosave stack.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: resume executes with delicate stack, MMU, and nosave memory constraints; wrong PFN
filtering corrupts the restored kernel. Changes should preserve register layouts, numeric constants,
early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/kernel/hibernate.c -->
