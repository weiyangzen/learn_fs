# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-agilex5.c

Purpose: Agilex5 clock manager platform driver and clock descriptor tables.

Important APIs/types/functions: parent-name arrays, `agilex5_pll_clks`, `agilex5_main_perip_c_clks`, `agilex5_main_perip_cnt_clks`, `agilex5_gate_clks`, registration loops, `agilex5_clkmgr_init()`, and `agilex5_clkmgr_probe()`.

Control flow: core initcall registers the platform driver. Probe maps MMIO, allocates `AGILEX5_NUM_CLKS` onecell storage, initializes empty slots, registers PLLs, counters, peripheral counters, and gates, then publishes the provider.

State and persistence behavior: devm-managed clock data and MMIO base; hardware register state for mux/gate/divider choices; no explicit suspend handling.

Dependencies/integration points: Agilex5 DT bindings, shared Stratix10 helper constructors, CCF, and platform/OF registration.

Risks: large literal tables define ABI-sensitive IDs and offsets; string parent names must resolve; provider return is unchecked; some clocks use divider/bypass data without a gate register.

Test signals: Agilex5 boot, `AGILEX5_NUM_CLKS` coverage, CPU/free-clock parent tests, USB31/SDMMC/NAND clock validation, and clock-provider log review.
