# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm3xxx.h

## Purpose
Declares OMAP3 PRM address macros, global PRM/VC/VP/reset/clock/voltage register offsets, OMAP3-specific module offsets, and OMAP3 PRM public APIs.

## APIs, Flow, And State
`OMAP34XX_PRM_REGADDR(module, reg)` maps PRM addresses. Register constants cover revision/sysconfig/IRQ status/enable, VC SMPS address/voltage/command/bypass/config, VP1/VP2 config/status/limits/voltage/steps, reset, voltage control, clock source/setup/polarity, and clock output. OMAP3-specific offsets include wake/status/group-select registers and IVA IRQs. APIs declare VC/VP accessors, PRM init, global cold-reset clear, scratchpad save, and PM init.

## Dependencies And Integration
Includes `prcm-common.h`, `prm.h`, and `prm2xxx_3xxx.h`. Used by OMAP3 PRM, voltage, PM, and low-level suspend code.

## Risks And Test Signals
The header handles OMAP3 global registers split across GR and CCR modules; wrong module selection changes the target physical register. Test signals are OMAP3 PRM base access, voltage controller register programming, IRQ offsets, and suspend scratchpad restore.
