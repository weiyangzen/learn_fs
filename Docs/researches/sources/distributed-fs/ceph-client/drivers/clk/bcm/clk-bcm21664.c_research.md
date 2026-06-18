<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm21664.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm21664.c

Purpose: This file declares Kona-style CCU clock data for the Broadcom BCM21664 mobile SoC. It maps DT-compatible CCU nodes to clock tables for root, always-on, master, and slave clock control units.

Important APIs, types, and functions: The file is almost entirely descriptor data using `peri_clk_data`, `ccu_data`, and macros from `clk-kona.h`, including `KONA_CCU_COMMON`, `KONA_CLK`, `HW_SW_GATE`, `HYST`, `CLOCKS`, `SELECTOR`, `DIVIDER`, `FRAC_DIVIDER`, `TRIGGER`, `CCU_LVM_EN`, and `CCU_POLICY_CTL`. Setup callbacks are `kona_dt_root_ccu_setup()`, `kona_dt_aon_ccu_setup()`, `kona_dt_master_ccu_setup()`, and `kona_dt_slave_ccu_setup()`, all calling `kona_dt_ccu_setup()`.

Control flow: At boot, each `CLK_OF_DECLARE()` compatible invokes the corresponding setup function. The common Kona setup code consumes the static `ccu_data`, maps registers, creates clocks for the indexed `kona_clks` array, and registers the onecell provider.

State and persistence behavior: This file has no custom mutable runtime state. Runtime clock state is managed by the Kona common driver through hardware gate, selector, divider, trigger, hysteresis, and policy-control registers. Some sleep-clock entries are marked with "Verify" comments, indicating known uncertainty in parent definitions.

Dependencies and integration points: It depends on `clk-kona.h`, BCM21664 DT clock binding indices, and DT compatible strings from those bindings. It provides clocks for SDIO, UART, BSC/I2C, hub timer, and fractional root clock consumers.

Risks and test signals: Risks are descriptor accuracy: wrong offsets, trigger bits, parent names, or clock IDs can silently produce bad peripheral clocks. Test signals include successful BCM21664 boot, SDIO/UART/I2C operation, hub timer function, and `clk_summary` showing expected Kona CCU clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm21664.c -->
