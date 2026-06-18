# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm44xx.h

## Purpose
Declares OMAP44xx PRM base address, PRM instance offsets, clockdomain offsets, common OMAP4 power/reset register offsets, IRQ register offsets, device PRM voltage/IO/VP/VC offsets, and address macros.

## APIs, Flow, And State
`OMAP44XX_PRM_REGADDR(inst, reg)` maps OMAP4 PRM addresses. Instance macros cover OCP socket, CKGEN, MPU, TESLA, ABE, ALWAYS_ON, CORE, IVAHD, CAM, DSS, GFX, L3INIT, L4PER, CEFUSE, WKUP, EMU, and DEVICE. Register constants include `OMAP4_PM_PWSTCTRL`, `OMAP4_PM_PWSTST`, IRQSTATUS/IRQENABLE, MPU context, reset control, IO PMCTRL, voltage setup, VP configs/status, VC SMPS/command/bypass/channel/I2C config.

## Dependencies And Integration
Includes shared OMAP4/5 PRM prototypes and `prm.h`. Used by `prm44xx.c`, `prminst44xx.c`, voltage code, powerdomain data, and generated clockdomain tables.

## Risks And Test Signals
Because many offsets are reused by generic `omap44xx_prm_init()`, offset mistakes affect several independent features. Test signals are OMAP4 PRM IRQ, voltage controller setup, powerdomain read/write, and hardreset operation.
