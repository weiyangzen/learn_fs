# sources/distributed-fs/ceph-client/drivers/clk/qcom/ecpricc-qdu1000.c

## Purpose

`ecpricc-qdu1000.c` is a Qualcomm clock-controller driver for the QDU1000 ECPRI clock controller, matched by the devicetree compatible `qcom,qdu1000-ecpricc`. It exposes the clocks and resets needed by the eCPRI, ORAN, 100G Ethernet/front-haul, MACsec, MSS EMAC, NoC, and Ethernet PHY lane blocks on that SoC. The file is almost entirely static clock metadata: PLL definitions, root clock generators, read-only dividers, branches, memory branches, reset offsets, and the `qcom_cc_desc` used by the common Qualcomm clock-controller registration path.

## Important APIs, Types, And Data

The driver uses the common clock framework and Qualcomm clock helpers: `struct clk_alpha_pll`, `struct alpha_pll_config`, `struct clk_rcg2`, `struct clk_regmap_div`, `struct clk_branch`, `struct clk_mem_branch`, `struct qcom_reset_map`, `struct regmap_config`, and `struct qcom_cc_desc`.

Two Lucid EVO fixed alpha PLLs are defined locally: `ecpri_cc_pll0`, configured to 700 MHz from `ecpri_cc_pll0_config`, and `ecpri_cc_pll1`, configured to 806 MHz from `ecpri_cc_pll1_config`. The PLLs share `lucid_evo_vco`, use `clk_alpha_pll_fixed_lucid_evo_ops`, and are configured during probe with `clk_lucid_evo_pll_configure()`. External parents arrive through devicetree indexes for `bi_tcxo` and GCC-to-ECPRI GPLL outputs. Internal parents are wired by direct `.hw` references to the two ECPRI PLLs.

Parent maps `ecpri_cc_parent_map_0`, `_1`, and `_2` describe hardware mux values for the RCGs. Frequency tables cover fixed, hardware-supported rates for eCPRI, DMA, fast, ORAN, 100G HM FF, MACsec, MAC reference, and MSS EMAC sources. The main exported arrays are `ecpri_cc_qdu1000_clocks[]`, `ecpri_cc_qdu1000_resets[]`, and `ecpri_cc_qdu1000_desc`.

## Control Flow

`module_platform_driver(ecpri_cc_qdu1000_driver)` registers the platform driver. The OF match table binds `qcom,qdu1000-ecpricc` to `ecpri_cc_qdu1000_probe()`. Probe maps controller MMIO through `qcom_cc_map()`, programs PLL0 and PLL1 with their static alpha PLL configurations, and calls `qcom_cc_really_probe()` to register all clocks and resets with the CCF/reset framework. After registration, consumers interact through standard clock and reset APIs, with operations dispatched to `clk_rcg2_shared_ops`, `clk_regmap_div_ro_ops`, `clk_branch2_ops`, and `clk_branch2_mem_ops`.

## State And Persistence

The driver has no file-backed or heap-persistent state. Persistent state is hardware state in the clock-controller registers: PLL configuration registers, RCG command/config registers, branch enable/halt bits, memory-retention enable/ack bits, and reset bits. Static C data describes offsets, masks, parents, and allowed rates. On each probe, PLL0 and PLL1 are explicitly programmed, while most other clocks are registered around their existing hardware state and then changed on demand by CCF consumers.

The `clk_mem_branch` entries are important stateful integrations: HM FF, MACsec, MAC reference, and OCK SRAM clocks include both branch gate state and memory enable/ack state. A consumer enable must set the memory enable mask and observe the ack mask, not just toggle the CBCR branch bit.

## Dependencies And Integration Points

This file depends on the Qualcomm clock driver helpers in the same directory: `clk-alpha-pll.h`, `clk-branch.h`, `clk-rcg.h`, `clk-regmap-divider.h`, `clk-regmap-mux.h`, `common.h`, and `reset.h`. It also depends on the binding header `dt-bindings/clock/qcom,qdu1000-ecpricc.h`; the ordering and size of `ecpri_cc_qdu1000_clocks[]` must remain aligned with that header.

Integration with the rest of the SoC is via devicetree parent indexes. Parent IDs such as `DT_GCC_ECPRI_CC_GPLL0_OUT_MAIN`, `DT_GCC_ECPRI_CC_GPLL5_OUT_EVEN`, and similar GCC exported clocks must be supplied by the platform clock topology. The controller also exports reset controls for ECPRI SS, Ethernet C2C/FH wrappers, modem, and NoC blocks. Consumers include Ethernet/eCPRI datapath drivers, MACsec, ORAN/MSS components, NoC consumers, and PHY lane logic.

## Risks And Test Signals

The main risk is binding drift: every entry in `ecpri_cc_qdu1000_clocks[]` and `ecpri_cc_qdu1000_resets[]` is position-indexed by public dt-binding constants. Register offsets and masks are hardware contract values; a single wrong offset can enable the wrong block or make halt polling time out. Rate tables are intentionally narrow, so missing rates cause normal CCF `set_rate` requests to fail or round unexpectedly. Several PHY lane RX/TX clocks have no explicit parent, modeling externally driven or hardware-rooted signals.

Useful test signals are kernel probe logs for `qcom,qdu1000-ecpricc`, absence of `qcom_cc_map()` or `qcom_cc_really_probe()` errors, and successful clock lookup by consumers using the binding IDs. Dynamic tests should exercise representative eCPRI, DMA, fast, ORAN, MACsec, HM FF, MSS EMAC, PHY lane, and reset consumers. Debugfs clock summaries can verify parent selection, rates, prepare/enable counts, and branch halt state.
