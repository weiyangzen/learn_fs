# sources/distributed-fs/ceph-client/drivers/clk/qcom/apss-ipq5424.c

## Purpose
`apss-ipq5424.c` registers the IPQ5424 APSS clock controller. It provides APSS and L3 PLLs, RCG sources, critical core branch clocks, and an interconnect hardware clock relation between CPU and L3.

## Important APIs, Types, And Functions
Key objects include `ipq5424_apss_pll`, `apss_silver_clk_src`, `apss_silver_core_clk`, `ipq5424_l3_pll`, `l3_clk_src`, `l3_core_clk`, `apss_ipq5424_clks`, `icc_ipq5424_cpu_l3`, `apss_ipq5424_desc`, and `apss_ipq5424_probe()`. It uses `clk_alpha_pll_huayra_ops`, `clk_rcg2_ops`, `clk_branch2_ops`, `qcom_cc_probe()`, and `icc_sync_state()`.

## Control Flow, State, And Persistence
The static descriptor defines register layout, two configured Huayra 2290 PLLs, APSS silver and L3 RCG frequency tables, critical branches, interconnect hardware clock data, and driver data listing PLLs for common initialization. Probe delegates all mapping, registration, reset/GDSC-style setup, and provider publication to `qcom_cc_probe()`. State is MMIO-backed clock configuration and generic clock/interconnect provider registration.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include qcom common clock helpers, alpha PLL/RCG/branch implementations, DT binding IDs, two parent clocks by DT index, interconnect provider support, and GCC/firmware supplying reference clocks. Risks include a likely `ipa5424` naming typo in local arrays, incorrect interconnect node IDs, critical branches masking unused-clock cleanup issues, and PLL/frequency table mismatches affecting CPU or L3 stability. Test signals include IPQ5424 boot, APSS CPU frequency selection at 816 MHz to 1.8 GHz, L3 frequencies at 816 MHz to 1.272 GHz, interconnect sync-state behavior, and `clk_summary` showing critical APSS/L3 core clocks enabled.
