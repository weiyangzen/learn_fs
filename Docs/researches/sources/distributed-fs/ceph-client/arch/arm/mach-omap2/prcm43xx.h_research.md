# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm43xx.h

## Purpose
Provides AM43xx PRCM partition, PRM instance, CM instance, clockdomain offset, interrupt register, IO power-control, and selected clock-control register offsets.

## APIs, Flow, And State
This header exposes macros only. Key constants include `AM43XX_PRM_PARTITION`, `AM43XX_CM_PARTITION`, `AM43XX_PRM_*_INST`, `AM43XX_PRM_IRQSTATUS_MPU_OFFSET`, `AM43XX_PRM_IRQENABLE_MPU_OFFSET`, `AM43XX_PRM_IO_PMCTRL_OFFSET`, `AM43XX_CM_*_INST`, clockdomain offsets such as `AM43XX_CM_PER_EMIF_CDOFFS`, and `AM43XX_CM_PER_EMIF_CLKCTRL_OFFSET`. No runtime state is stored here.

## Dependencies And Integration
Consumed by `prm44xx.c`, `sleep43xx.S`, PRM/CM register accessors, and AM43xx-specific initialization that reuses the OMAP4-style PRM code with AM43xx offsets. It integrates with device-tree compatible `ti,am4-prcm`.

## Risks And Test Signals
The AM43xx reuse of OMAP4-style code makes offset accuracy critical; a wrong IRQ or IO PMCTRL offset breaks chained PRCM IRQs and wakeups. Test signals include AM43xx boot, PRM IRQ setup with a single IRQ register, EMIF clock control during suspend, and RTC+DDR wake behavior.
