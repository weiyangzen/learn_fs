# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-44xx.h

Purpose: Defines OMAP44xx CM register bit shifts and masks, especially static dependency bits and common CLKCTRL/CLKSTCTRL fields.

Important APIs/types/functions: Provides `OMAP4430_*_STATDEP_SHIFT` values for ABE, Ducati, IVAHD, MEMIF, L3/L4 domains, DSS, GFX, L3INIT, TESLA, and wakeup domains, plus `OMAP4430_IDLEST_MASK`, `OMAP4430_CLKTRCTRL_MASK`, and `OMAP4430_MODULEMODE_MASK`.

Control flow: No executable logic. Clockdomain data uses STATDEP shifts as `dep_bit` values, while the OMAP4 CM backend uses local equivalent masks for IDLEST, CLKTRCTRL, and MODULEMODE.

State and persistence: No software state. Encodes OMAP44xx CM hardware bit positions.

Dependencies: Standalone guarded generated header. Included by OMAP44xx clockdomain data and related CM code.

Integration points: Enables OMAP4 static dependency register programming through `OMAP4_CM_STATICDEP`.

Risks: Static dependency shifts are central to wake/sleep behavior; mismatched values can either prevent low-power entry or fail to wake dependent domains. Generated-file comments imply edits should stay coordinated with hardware database generation.

Test signals: OMAP4 boot dependency resolution, accelerator/peripheral wake tests, and suspend/resume validate the shifts.
