# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm-regbits-44xx.h

## Purpose
Defines OMAP44xx PRM bit masks and shifts for reset sources, voltage controller/processor, IO wake clock control, context loss, memory/logic states, and global wake enable.

## APIs, Flow, And State
Macro-only definitions include reset source shifts (`GLOBAL_COLD`, `GLOBAL_WARM_SW`, `MPU_WDT`, `C2C`), VC command/voltage fields, VP transaction done masks for MPU/IVA/CORE, `OMAP4430_GLOBAL_WUEN_MASK`, `OMAP4430_WUCLK_*`, power-state and memory-state masks, and context-loss masks.

## Dependencies And Integration
Consumed by `prm44xx.c`, `prminst44xx.c`, and OMAP4+ voltage/powerdomain code. The reset-source map and IO-chain routines directly depend on these constants.

## Risks And Test Signals
Voltage and wake bits affect hardware-level power sequencing; wrong masks can hang suspend/resume or misreport reset causes. Test signals are OMAP4 PRCM IRQs, IO wake chain reconfiguration, VP transaction completion, and reset behavior.
