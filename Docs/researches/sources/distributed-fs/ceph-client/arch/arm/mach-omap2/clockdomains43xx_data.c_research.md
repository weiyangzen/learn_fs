# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clockdomains43xx_data.c

Purpose: Defines AM43xx clockdomains using the OMAP4-style CM partition/instance layout with AM43xx-specific domain offsets.

Important APIs/types/functions: Defines domains for CEFUSE, MPU, L4LS, tamper, RTC, PRUSS, OCPWP, TSC, LCDC, DSS, L3 AON, EMIF, L4 WKUP AON, L3, L4 WKUP, CPSW, GFX, and L3S. Provides `clockdomains_am43xx[]` and `am43xx_clockdomains_init()`.

Control flow: Initialization registers `am43xx_clkdm_operations`, registers the AM43xx array, and completes generic initialization. The backend for AM43xx is implemented in `cminst44xx.c`, but with a reduced operation table compared with full OMAP4.

State and persistence: Static descriptors include `prcm_partition`, `cm_inst`, and `clkdm_offs`. AM43xx off-mode can lose clockdomain context; the generic layer installs a CPU PM notifier for AM43xx and uses backend context hooks when available.

Dependencies: Uses AM43xx CM/PRCM headers and OMAP4-style clockdomain infrastructure. Requires matching AM43xx powerdomain names for core, wakeup, graphics, RTC, and peripheral blocks.

Integration points: Bridges AM43xx data to the partitioned CM instance backend, enabling OMAP4-style CLKSTCTRL control on AM43xx.

Risks: Since `am43xx_clkdm_operations` lacks dependency and context callbacks in this snapshot, behavior differs from full OMAP4 and generic context calls may no-op or fail if invoked through absent hooks. Incorrect partition IDs are hazardous because the backend uses BUG_ON for invalid partitions.

Test signals: AM43xx boot should register all domains and complete init without partition faults. RTC-DDR suspend/resume and peripheral enable-disable cycles are key signals.
