<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm281xx.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm281xx.c

Purpose: This file declares Kona-style clock-control-unit data for Broadcom BCM281xx SoCs. It covers root, always-on, hub, master, and slave CCUs and their peripheral clocks.

Important APIs, types, and functions: It uses `peri_clk_data`, `ccu_data`, and `clk-kona.h` macros such as `KONA_CCU_COMMON`, `KONA_CLK`, `HW_SW_GATE`, `CLOCKS`, `SELECTOR`, `DIVIDER`, `FRAC_DIVIDER`, `FIXED_DIVIDER`, and `TRIGGER`. Setup callbacks `kona_dt_root_ccu_setup()`, `kona_dt_aon_ccu_setup()`, `kona_dt_hub_ccu_setup()`, `kona_dt_master_ccu_setup()`, and `kona_dt_slave_ccu_setup()` pass static descriptors to `kona_dt_ccu_setup()`.

Control flow: `CLK_OF_DECLARE()` binds BCM281xx CCU DT-compatible strings to the setup callbacks. The common Kona code interprets each descriptor, registers clocks at the binding-defined indices, and exposes the clock provider.

State and persistence behavior: No custom state is allocated here. Hardware state is controlled through the described gate, selector, divider, trigger, and fractional-divider registers. Critical persistence is table data matching the SoC's register layout.

Dependencies and integration points: It depends on BCM281xx binding IDs, Kona common clock support, and DT parent clock names like `ref_crystal`, `var_52m`, `ref_96m`, `var_156m`, and `bbl_32k`. It feeds SDIO, USB/HSIC, UART, SSP, BSC, PWM, PMU BSC, timer, and thermal-monitor clocks.

Risks and test signals: Risks are off-by-one binding indices, wrong shared register offsets, parent-name drift, and inaccurate fixed/pre-divider definitions. Test signals include peripheral probe success, usable SDIO/USB/UART/I2C/PWM clocks, and matching rates in `clk_summary` for divider-driven clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm281xx.c -->
