# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm3xxx.c

Purpose: Implements OMAP3 CM operations, OMAP3 clockdomain backend behavior, sleep dependency handling, and CM context save/restore for low-power states.

Important APIs/types/functions: Includes CLKTRCTRL helpers, `omap3xxx_cm_wait_module_ready()`, `omap3xxx_cm_split_idlest_reg()`, sleepdep add/delete/read/clear operations, force sleep/wakeup and hwsup operations, `omap3_clkdm_operations`, `struct omap3_cm_regs`, `omap3_cm_save_context()`, `omap3_cm_restore_context()`, `omap3_cm_save_scratchpad_contents()`, and `omap3xxx_cm_init()`.

Control flow: OMAP3 CM dispatchers poll IDLEST with OMAP3 polarity, split legacy IDLEST register addresses, and control CLKSTCTRL fields. Clock enable/disable handles missing idle reporting, temporarily disables hwsup while changing autodeps, and uses force wake/sleep when in software-supervised mode.

State and persistence: OMAP3 CM context is saved into static `cm_context`, which covers clock selects, enables, autoidle, CLKSTCTRL, sleepdeps, and CLKOUT control. Scratchpad save writes a DPLL/clock subset for ROM-assisted resume. Runtime clockdomain state remains in generic `struct clockdomain`.

Dependencies: Uses OMAP2/3 PRM/CM headers, OMAP34xx regbits, generic clockdomain APIs, and `omap2_clk_legacy_provider_init()`.

Integration points: Backend for `clockdomains3xxx_data.c`, common CM dispatch, OMAP3 PM suspend/resume, and clock provider initialization.

Risks: Context list is broad and order-sensitive; omitted registers can break resume. Erratum i671 requires special PER DPLL autoidle handling. Autodep manipulation while in hwsup is delicate.

Test signals: OMAP3 suspend/resume, retention/off-mode resume, SGX/DSS/CAM/PER/USBHOST enable-disable, and DPLL scratchpad restore should be validated.
