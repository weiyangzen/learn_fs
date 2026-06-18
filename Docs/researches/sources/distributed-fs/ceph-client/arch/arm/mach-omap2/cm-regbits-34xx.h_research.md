# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-34xx.h

Purpose: Defines OMAP3430/AM35xx CM register masks, shifts, and CLKSTCTRL mode encodings.

Important APIs/types/functions: Includes IVA2, MPU, CORE, GFX/SGX, DSS, CAM, PER, EMU, NEON, USBHOST status and CLKTRCTRL fields, plus `OMAP34XX_CLKSTCTRL_DISABLE_AUTO`, `OMAP34XX_CLKSTCTRL_FORCE_SLEEP`, `OMAP34XX_CLKSTCTRL_FORCE_WAKEUP`, and `OMAP34XX_CLKSTCTRL_ENABLE_AUTO`.

Control flow: No executable flow. `cm3xxx.c`, `cm33xx.c`, and `cminst44xx.c` use the mode constants to write CLKSTCTRL fields; OMAP3 data uses the masks for clockdomain descriptors.

State and persistence: No software state. Defines CM hardware field layout and mode values.

Dependencies: Standalone guarded header used by OMAP3 and by newer backends where CLKSTCTRL encodings are shared.

Integration points: Supports OMAP3 autodeps, sleepdeps, force sleep/wakeup, hardware supervision, and context save/restore.

Risks: This header mixes OMAP3430 and AM35xx fields and ES-specific macros. Incorrect selection can break SGX/GFX or USBHOST handling across silicon revisions.

Test signals: OMAP3430 ES1/ES2+, AM35x, AM33xx, and OMAP4-style builds should compile and use expected CLKSTCTRL encodings. Runtime CM timeout absence validates status/mode fields.
