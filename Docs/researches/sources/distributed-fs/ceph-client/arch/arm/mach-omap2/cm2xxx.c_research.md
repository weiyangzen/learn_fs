# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2xxx.c

Purpose: Implements OMAP2xxx-specific CM low-level operations and clockdomain backend behavior.

Important APIs/types/functions: Internal helpers include `_write_clktrctrl()`, `omap2xxx_cm_is_clkdm_in_hwsup()`, `omap2xxx_cm_clkdm_enable_hwsup()`, `omap2xxx_cm_clkdm_disable_hwsup()`, `_omap2xxx_set_dpll_autoidle()`, `omap2xxx_cm_split_idlest_reg()`, and `omap2xxx_cm_wait_module_ready()`. Public functions include DPLL autoidle setters, `omap2xxx_cm_fclks_active()`, `omap2xxx_cm_mpu_retention_allowed()`, core clock queries, divider programming, and `omap2xxx_cm_init()`. Exports `struct clkdm_ops omap2_clkdm_operations`.

Control flow: The backend maps generic clockdomain calls to OMAP2 module register accesses through `omap2_cm_read_mod_reg()` and `omap2_cm_write_mod_reg()`. Clock enable/disable checks hwsup state and forces wake/sleep where supported. `omap2xxx_cm_init()` registers `omap2xxx_cm_ll_data` with the common CM layer.

State and persistence: Software state is minimal; it writes CM registers directly. DPLL/APLL autoidle and divider settings persist in hardware registers. Common CM stores the registered operation table pointer.

Dependencies: Includes PRM2xxx, CM common headers, OMAP24xx bit definitions, and clockdomain APIs. It reuses wake dependency helpers declared elsewhere for OMAP2.

Integration points: Used by OMAP2420/2430 clockdomain data and the common CM dispatchers for module readiness and legacy IDLEST register splitting.

Risks: The DPLL setter names appear counterintuitive: `omap2xxx_cm_set_dpll_disable_autoidle()` writes low-power stop and `omap2xxx_cm_set_dpll_auto_low_power_stop()` writes disable, so callers must match historical semantics. Module readiness uses OMAP2 polarity where enabled means the IDLEST bit is set.

Test signals: OMAP2 boot should initialize CM, poll IDLEST successfully, and control DPLL autoidle. MPU retention allowed logic should respond to active MMC/UART/McSPI/DSS clocks.
