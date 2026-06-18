# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains33xx_data.c

Purpose: Defines AM33xx clockdomain descriptors and registers them with the AM33xx CM backend.

Important APIs/types/functions: Defines domains for L4LS, L3S, L4FW, L3, L4HS, OCPWP, PRUSS, CPSW, LCDC, 24MHz clock, WKUP, L3 AON, L4 WKUP AON, MPU, RTC, GFX L3, GFX L4LS, and CEFUSE. Provides `clockdomains_am33xx[]` and `am33xx_clockdomains_init()`.

Control flow: `am33xx_clockdomains_init()` registers `am33xx_clkdm_operations`, registers all AM33xx clockdomains, and completes initialization. There are no explicit dependency arrays; domains primarily use CM instance and clockdomain offset pairs with software-supervised capability flags.

State and persistence: Descriptors include `cm_inst` and `clkdm_offs` offsets into AM33xx CM. Runtime `context` is saved/restored by `cm33xx.c` for CLKTRCTRL state.

Dependencies: Includes `cm33xx.h`, `cm-regbits-33xx.h`, `prcm-common.h`, and `clockdomain.h`. Requires powerdomain names such as `per_pwrdm`, `wkup_pwrdm`, `mpu_pwrdm`, `rtc_pwrdm`, `gfx_pwrdm`, and `cefuse_pwrdm`.

Integration points: Used on AM33xx/AM335x systems by platform init. Its offsets feed AM33xx CM operations for force sleep/wakeup, hardware supervision, and module readiness.

Risks: A wrong `clkdm_offs` can make the backend write the wrong CLKSTCTRL register. Standby behavior has special handling in `cm33xx.c`, so domains requiring `CLKDM_STANDBY_FORCE_WAKEUP` must be flagged correctly.

Test signals: AM33xx boot should register all powerdomain mappings. Runtime checks include PRUSS/CPSW/LCDC enable-disable, standby wake, and PM tests that verify L4LS is not incorrectly forced asleep during standby.
