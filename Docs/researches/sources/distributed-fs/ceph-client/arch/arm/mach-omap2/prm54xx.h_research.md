# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm54xx.h

## Purpose
Defines OMAP54xx PRM base address, PRM instance offsets, clockdomain offsets, and selected device PRM voltage setup offsets.

## APIs, Flow, And State
The `OMAP54XX_PRM_REGADDR(inst, reg)` macro maps OMAP5 PRM MMIO. Instance offsets include OCP socket, CKGEN, MPU, DSP, ABE, COREAON, CORE, IVA, CAM, DSS, GPU, L3INIT, CUSTEFUSE, WKUPAON, EMU, and DEVICE. Device PRM voltage setup offsets cover CORE/MPU/MM retention sleep. No executable flow or state.

## Dependencies And Integration
Includes shared OMAP4/5 PRM prototypes and `prm.h`. Used by common `omap44xx_prm_init()` through OMAP5 init data with `OMAP54XX_PRM_DEVICE_INST`.

## Risks And Test Signals
OMAP5 uses the OMAP4-style common PRM implementation but different instance layout and base address. Test signals are OMAP5 PRM init, voltage retention setup, powerdomain register access, and wake/reset behavior.
