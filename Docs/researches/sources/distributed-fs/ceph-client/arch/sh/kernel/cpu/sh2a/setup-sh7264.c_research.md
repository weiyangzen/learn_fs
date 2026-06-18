# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7264.c

## Purpose
`setup-sh7264.c` provides SH7264 interrupt routing and on-chip platform-device registration. It exposes eight SCIF ports, CMT, MTU2, RTC, and the on-chip R8A66597 USB host to generic Linux drivers.

## Important APIs, Types, And Functions
The file defines a large INTC map with grouped PINT and per-port SCIF interrupt groups, `DECLARE_INTC_DESC(intc_desc, "sh7264", ...)`, eight `plat_sci_port` objects using `SCIx_SH2_SCIF_FIFODATA_REGTYPE`, CMT/MTU/RTC resources, `r8a66597_platdata`, and `usb_port_power()`. Public setup hooks are `sh7264_devices_setup()`, `plat_irq_setup()`, and `plat_early_device_setup()`.

## Control Flow
Normal device registration happens through `arch_initcall(sh7264_devices_setup)`. `plat_irq_setup()` registers the INTC descriptor. Early boot registers SCIF0-7, CMT, and MTU2 only; RTC and USB host wait for normal platform init. `usb_port_power()` is handed to the USB host platform data and writes UACS25 when the HCD toggles port power.

## State And Persistence
State is static platform-resource description plus hardware configuration in INTC priority/mask registers and a USB control register. No persistent storage is used. The USB host advertises `dma_mask = NULL`, explicitly indicating no DMA use.

## Dependencies And Integration Points
The code integrates with `sh-sci`, `sh-cmt-16`, `sh-mtu2`, `sh-rtc`, and `r8a66597_hcd`. It relies on `linux/sh_intc` macros through the platform headers and raw I/O for USB power control.

## Risks
The dense interrupt table has high off-by-one risk, especially SCIF BRI/ERI/RXI/TXI ordering. The hard-coded USB power write is board/SoC specific and can break host bring-up if the address or bit differs. Early devices omit USB/RTC, so console and timer must not depend on them.

## Test Signals
Boot should show eight SCI ports and CMT/MTU timers registered, RTC appearing after platform init, and R8A66597 HCD probing on IRQ 170. Interrupt counters for grouped SCIF events and USB low-trigger IRQs are the main runtime evidence.
