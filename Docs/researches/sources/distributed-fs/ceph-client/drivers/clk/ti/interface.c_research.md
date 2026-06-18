# sources/distributed-fs/ceph-client/drivers/clk/ti/interface.c

Purpose: OMAP interface clock registration. It wraps interface clocks in `clk_hw_omap` and selects the proper idle/wait ops for generic, no-wait, OMAP3 special, AM35xx, and OMAP2430 variants.

Important APIs/types/functions: `_register_interface()`, `_of_ti_interface_clk_setup()`, and `CLK_OF_DECLARE()` handlers for `ti,omap3-interface-clock`, `ti,omap3-no-wait-interface-clock`, `ti,omap3-hsotgusb-interface-clock`, `ti,omap3-dss-interface-clock`, `ti,omap3-ssi-interface-clock`, `ti,am35xx-interface-clock`, and `ti,omap2430-interface-clock`.

Control flow: setup parses the register bit, requires one parent, names the clock, registers it with `ti_interface_clk_ops`, and publishes an OF provider. Runtime operations use default enable/disable/is_enabled with clockdomain initialization, while chosen `clk_hw_omap_ops` determine idle allowance and IDLEST wait behavior.

State and persistence: each interface clock stores enable register and bit plus optional ops. Hardware CM enable/idle bits persist.

Dependencies/integration: uses `ti_clk_get_reg_addr()`, `of_ti_clk_register_omap_hw()`, default OMAP clock ops, and special ops from `clkt_iclk.c` and SoC-specific files.

Risks: wrong compatible string changes wait behavior and can cause boot hangs or skipped readiness waits. Parent is mandatory and missing parent aborts registration.

Test signals: DT registration for each compatible variant, module enable waits, no-wait behavior for clocks without reliable IDLEST, and SoC-specific interface clocks under suspend/resume.
