# Research: subset-b-001121

Grouped research for Qualcomm clock-controller source files under `sources/distributed-fs/ceph-client/drivers/clk/qcom/`. Each section preserves the source path for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/ecpricc-qdu1000.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/ecpricc-qdu1000.c

## Purpose

`ecpricc-qdu1000.c` is a Qualcomm clock-controller driver for the QDU1000 ECPRI clock controller, matched by the devicetree compatible `qcom,qdu1000-ecpricc`. It exposes the clocks and resets needed by the eCPRI, ORAN, 100G Ethernet/front-haul, MACsec, MSS EMAC, NoC, and Ethernet PHY lane blocks on that SoC. The file is almost entirely static clock metadata: PLL definitions, root clock generators, read-only dividers, branches, memory branches, reset offsets, and the `qcom_cc_desc` used by the common Qualcomm clock-controller registration path.

## Important APIs, Types, And Data

The driver uses the common clock framework and Qualcomm clock helpers: `struct clk_alpha_pll`, `struct alpha_pll_config`, `struct clk_rcg2`, `struct clk_regmap_div`, `struct clk_branch`, `struct clk_mem_branch`, `struct qcom_reset_map`, `struct regmap_config`, and `struct qcom_cc_desc`.

Two Lucid EVO fixed alpha PLLs are defined locally:

- `ecpri_cc_pll0`, configured to 700 MHz from `ecpri_cc_pll0_config`.
- `ecpri_cc_pll1`, configured to 806 MHz from `ecpri_cc_pll1_config`.

The PLLs share `lucid_evo_vco`, use `clk_alpha_pll_fixed_lucid_evo_ops`, and are configured during probe with `clk_lucid_evo_pll_configure()`. External parents arrive through devicetree indexes: `bi_tcxo` and several GCC-to-ECPRI GPLL outputs. Internal parents are wired by direct `.hw` references to the two ECPRI PLLs.

Parent maps `ecpri_cc_parent_map_0`, `_1`, and `_2` describe hardware mux values for the RCGs. Frequency tables cover fixed, hardware-supported rates for eCPRI, DMA, fast, ORAN, 100G HM FF, MACsec, MAC reference, and MSS EMAC sources. The main exported arrays are:

- `ecpri_cc_qdu1000_clocks[]`, indexed by `dt-bindings/clock/qcom,qdu1000-ecpricc.h`.
- `ecpri_cc_qdu1000_resets[]`, indexed by the same binding reset IDs.
- `ecpri_cc_qdu1000_desc`, which combines regmap, clocks, and resets for the common registration code.

## Control Flow

Runtime control flow is small:

1. `module_platform_driver(ecpri_cc_qdu1000_driver)` registers the platform driver.
2. The OF match table binds `qcom,qdu1000-ecpricc` to `ecpri_cc_qdu1000_probe()`.
3. Probe calls `qcom_cc_map()` to map the controller MMIO region into a regmap using `ecpri_cc_qdu1000_regmap_config`.
4. Probe programs PLL0 and PLL1 with their static alpha PLL configurations.
5. Probe calls `qcom_cc_really_probe()` to register all clocks and resets with the CCF/reset framework.

After registration, consumers interact through standard clock and reset APIs. Rate changes and enables are dispatched to the ops selected in each static clock object, such as `clk_rcg2_shared_ops`, `clk_regmap_div_ro_ops`, `clk_branch2_ops`, and `clk_branch2_mem_ops`.

## State And Persistence

The driver has no file-backed or heap-persistent state. Persistent state is hardware state in the clock-controller registers: PLL configuration registers, RCG command/config registers, branch enable/halt bits, memory-retention enable/ack bits, and reset bits. Static C data describes offsets, masks, parents, and allowed rates. On each probe, PLL0 and PLL1 are explicitly programmed, while most other clocks are registered around their existing hardware state and then changed on demand by CCF consumers.

The `clk_mem_branch` entries are important stateful integrations: HM FF, MACsec, MAC reference, and OCK SRAM clocks include both branch gate state and memory enable/ack state. A consumer enable must set the memory enable mask and observe the ack mask, not just toggle the CBCR branch bit.

## Dependencies And Integration Points

This file depends on the Qualcomm clock driver helpers in the same directory: `clk-alpha-pll.h`, `clk-branch.h`, `clk-rcg.h`, `clk-regmap-divider.h`, `clk-regmap-mux.h`, `common.h`, and `reset.h`. It also depends on the binding header `dt-bindings/clock/qcom,qdu1000-ecpricc.h`; the ordering and size of `ecpri_cc_qdu1000_clocks[]` must remain aligned with that header.

Integration with the rest of the SoC is via devicetree parent indexes. Parent IDs such as `DT_GCC_ECPRI_CC_GPLL0_OUT_MAIN`, `DT_GCC_ECPRI_CC_GPLL5_OUT_EVEN`, and similar GCC exported clocks must be supplied by the platform clock topology. The controller also exports reset controls for ECPRI SS, Ethernet C2C/FH wrappers, modem, and NoC blocks. Consumers include Ethernet/eCPRI datapath drivers, MACsec, ORAN/MSS components, NoC consumers, and PHY lane logic.

## Risks And Maintenance Notes

The main risk is binding drift: every entry in `ecpri_cc_qdu1000_clocks[]` and `ecpri_cc_qdu1000_resets[]` is position-indexed by public dt-binding constants. Reordering or omitting entries breaks devicetree consumers. Register offsets and masks are hardware contract values; a single wrong offset can enable the wrong block or make halt polling time out.

Rate tables are intentionally narrow. Missing rates cause normal CCF `set_rate` requests to fail or round unexpectedly. The many 100G front-haul/divider/memory-branch clocks have repetitive names and offsets, so copy/paste errors are a realistic maintenance risk. A notable detail is `ecpri_cc_eth_phy_1_ock_sram_clk` using `0x841C` with an uppercase hex digit; C accepts it, but consistency checks should still verify that it is the intended `0x841c` register.

Several PHY lane RX/TX clocks have no explicit parent, so they model externally driven or hardware-rooted signals. Converting them to parented clocks without matching hardware behavior would risk invalid rate propagation.

## Test Signals

Useful test signals are kernel probe logs for `qcom,qdu1000-ecpricc`, absence of `qcom_cc_map()` or `qcom_cc_really_probe()` errors, and successful clock lookup by consumers using the binding IDs. Dynamic tests should exercise representative eCPRI, DMA, fast, ORAN, MACsec, HM FF, MSS EMAC, PHY lane, and reset consumers. Debugfs clock summaries can verify parent selection, rates, prepare/enable counts, and branch halt state. Reset smoke tests should assert/deassert each BCR-backed reset and confirm dependent devices recover. Build coverage should include this file with the corresponding binding header to catch missing enum entries and array initializer mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/ecpricc-qdu1000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-apq8084.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-apq8084.c

## Purpose

`gcc-apq8084.c` is the global clock controller driver for Qualcomm APQ8084, matched by `qcom,gcc-apq8084`. It publishes APQ8084 GCC clocks, resets, and GDSC power domains for platform peripherals including BLSP QUP/UART, BAM DMA, crypto engines, PCIe, SATA, SDCC, TSIF, UFS, USB HS/HSIC/USB3, PDM, PRNG, NoC, and MMSS GPLL vote support.

The file follows the older Qualcomm GCC style: basic `struct clk_pll` PLLs with vote clocks, `clk_rcg2` roots with frequency tables, direct branch gates, voted branches, GDSCs, and a large reset map.

## Important APIs, Types, And Data

Core types are `struct clk_pll`, `struct clk_regmap`, `struct clk_rcg2`, `struct clk_branch`, `struct gdsc`, `struct qcom_reset_map`, `struct regmap_config`, and `struct qcom_cc_desc`.

Three GPLLs are modeled as `clk_pll` objects:

- `gpll0`, the main general PLL parent used by most peripheral RCGs.
- `gpll1`, used by HSIC-related clocks.
- `gpll4`, used by SDCC high-rate options.

Each PLL also has a vote clock (`gpll0_vote`, `gpll1_vote`, `gpll4_vote`) sharing the vote register at `0x1480`. Parent maps connect XO, GPLL votes, external SATA/PCIe pipe sources, and sleep clock inputs. RCG definitions provide rate tables for UFS AXI, USB3 master/mock UTMI, BLSP I2C/SPI/UART, crypto engines, GP clocks, PCIe aux/pipe, PDM, SATA, SDCC, TSIF, USB HS, and USB HSIC.

The main public registration tables are:

- `gcc_apq8084_clocks[]`, indexed by `dt-bindings/clock/qcom,gcc-apq8084.h`.
- `gcc_apq8084_gdscs[]`, exporting `usb_hs_hsic`, `pcie0`, `pcie1`, and `usb30` power domains.
- `gcc_apq8084_resets[]`, indexed by `dt-bindings/reset/qcom,gcc-apq8084.h`.
- `gcc_apq8084_desc`, passed to the Qualcomm common probe helper.

## Control Flow

The driver is registered through a manual init/exit pair rather than `module_platform_driver()`:

1. `core_initcall(gcc_apq8084_init)` registers `gcc_apq8084_driver` early.
2. The platform bus matches `qcom,gcc-apq8084`.
3. `gcc_apq8084_probe()` registers the board XO clock as `xo_board` at 19.2 MHz by calling `qcom_cc_register_board_clk(dev, "xo_board", "xo", 19200000)`.
4. Probe registers the sleep clock through `qcom_cc_register_sleep_clk()`.
5. Probe calls `qcom_cc_probe()` with `gcc_apq8084_desc`, which maps the register space, registers clocks, resets, and GDSCs, and exposes them to CCF, reset-controller, and genpd consumers.

Once registered, individual consumer operations flow through CCF ops: `clk_pll_ops`, `clk_pll_vote_ops`, `clk_rcg2_ops`, `clk_rcg2_floor_ops`, `clk_branch2_ops`, and `clk_branch_simple_ops`.

## State And Persistence

The driver itself stores no mutable software state beyond static clock descriptors. Hardware registers hold all persistent state: PLL L/M/N/config/mode/status registers, vote registers, RCG command/config registers, branch CBCR bits, halt status, reset bits, and GDSC power-domain state. The board and sleep clocks registered during probe become CCF objects used as parents by the GCC tree.

Voted branches are significant state: many AHB/AXI clocks use shared enable registers such as `0x1484` with `BRANCH_HALT_VOTED`, while the actual halt register is peripheral-specific. The MMSS GPLL0 vote uses a simple branch object to expose a vote path to the display/multimedia subsystem.

## Dependencies And Integration Points

This file depends on Qualcomm common clock infrastructure: `common.h`, `clk-regmap.h`, `clk-pll.h`, `clk-rcg.h`, `clk-branch.h`, `reset.h`, and `gdsc.h`. It also depends on APQ8084 clock and reset binding headers. Devicetree must provide `qcom,gcc-apq8084`, the `xo` input, and external parents for PCIe pipe, SATA ASIC/RX, UFS symbol clocks, and sleep clock paths where used.

The driver integrates with multiple kernel subsystems:

- CCF consumers request clock parents, rates, and gates by binding ID or name.
- Reset consumers use the reset-controller mapping for subsystem BCRs and restart lines.
- Genpd consumers attach to PCIe and USB GDSCs.
- Storage and interconnect-facing drivers depend on SDCC, UFS, SATA, and NoC clocks.
- USB, PCIe, BLSP, crypto, PDM, TSIF, and PRNG drivers use their corresponding branch and RCG clocks.

## Risks And Maintenance Notes

The largest risk is index alignment with two binding headers. `gcc_apq8084_clocks[]`, `gcc_apq8084_gdscs[]`, and `gcc_apq8084_resets[]` are sparse arrays keyed by ABI constants. Changing indexes or dropping entries would silently break consumers.

Register offsets are dense and repetitive. Several clocks in similar blocks differ only by small offsets or enable bits, which raises copy/paste risk. CE3 entries are worth checking carefully because their branch definitions use CE3 enable registers but some halt register values resemble earlier CE blocks; hardware documentation must confirm those values.

The file mixes direct gates and voted gates. Using the wrong halt policy can cause false halt timeouts or premature success. External parent names such as `pcie_pipe`, `sata_asic0_clk`, `sata_rx_clk`, UFS symbol sources, `sleep_clk`, and `xo_board` must match devicetree and board-clock registration. Rate tables are explicit; unsupported rates are expected to round or fail rather than be synthesized freely.

Because this is registered at `core_initcall`, probe ordering matters. The board clock registration in probe mitigates parent availability for older DTs, but changes to parent naming or initcall level can affect early consumers.

## Test Signals

Build coverage should compile this driver with both APQ8084 binding headers and `CONFIG_COMMON_CLK_QCOM`. Probe tests should check that `xo_board` and `sleep_clk` register successfully and that `qcom_cc_probe()` does not fail. Runtime validation should use `/sys/kernel/debug/clk/clk_summary` to inspect PLL vote enables, BLSP rates, SDCC floor-rate behavior, USB/PCIe/SATA/UFS branches, and MMSS GPLL0 vote behavior. Power-domain tests should attach/detach PCIe and USB consumers and verify GDSC state transitions. Reset tests should exercise representative BCRs for NoC, BLSP, USB, PCIe, SATA, UFS, and restart controls. Peripheral smoke tests for UART/I2C/SPI, SD card, USB, PCIe, UFS, SATA, and crypto are the best end-to-end coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-apq8084.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-eliza.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-eliza.c

## Purpose

`gcc-eliza.c` is the GCC driver for the Qualcomm Eliza platform, matched by `qcom,eliza-gcc`. It exports global clocks, resets, and GDSC power domains for PCIe, UFS, USB3, QUPv3 serial engines, SDCC, PDM, GPU, camera, display, video, and NoC/QMIP fabrics. Compared with `gcc-apq8084.c`, it uses newer Qualcomm clock-controller patterns: Lucid OLE alpha PLLs, hardware-controlled shared RCGs, PHY mux clocks, read-only dividers, critical CBCR handling, DFS RCG metadata, and driver data callbacks.

## Important APIs, Types, And Data

The main types are `struct clk_alpha_pll`, `struct clk_alpha_pll_postdiv`, `struct clk_regmap_phy_mux`, `struct clk_regmap_mux`, `struct clk_rcg2`, `struct clk_regmap_div`, `struct clk_branch`, `struct gdsc`, `struct qcom_reset_map`, `struct clk_rcg_dfs_data`, `struct qcom_cc_driver_data`, and `struct qcom_cc_desc`.

PLL and parent infrastructure includes:

- Fixed Lucid OLE PLLs `gcc_gpll0`, `gcc_gpll4`, `gcc_gpll7`, `gcc_gpll8`, and `gcc_gpll9`.
- `gcc_gpll0_out_even`, a post-divider with divide-by-2 output.
- Parent maps for TCXO, sleep clock, GPLL main/even outputs, PCIe pipe inputs, UFS symbol inputs, and USB3 PHY pipe input.

Notable clock classes:

- PCIe PHY muxes `gcc_pcie_0_pipe_clk_src` and `gcc_pcie_1_pipe_clk_src`.
- UFS symbol PHY muxes for RX0, RX1, and TX0.
- USB3 pipe mux `gcc_usb3_prim_phy_pipe_clk_src`.
- Shared RCGs for GP clocks, PCIe aux/PHY ref-change, PDM, QUPv3 serial engines, SDCC, UFS PHY, and USB3.
- Read-only dividers for PCIe pipe-div2, QUPv3 wrap1 S2, and USB mock UTMI postdiv.
- Branch gates with multiple halt policies, hardware clock-gating fields, and vote-register bits.

Public registration tables are `gcc_eliza_clocks[]`, `gcc_eliza_gdscs[]`, and `gcc_eliza_resets[]`, all indexed by `dt-bindings/clock/qcom,eliza-gcc.h`. `gcc_eliza_driver_data` declares critical CBCRs, dynamic frequency scaling RCGs, and a post-map register configuration callback.

## Control Flow

The control path is concise:

1. `subsys_initcall(gcc_eliza_init)` registers the platform driver.
2. The OF match table binds `qcom,eliza-gcc`.
3. `gcc_eliza_probe()` calls `qcom_cc_probe(pdev, &gcc_eliza_desc)`.
4. The common Qualcomm probe path maps registers, applies `gcc_eliza_driver_data`, registers all clocks/resets/GDSCs, marks critical CBCRs, wires DFS data, and invokes `clk_eliza_regs_configure()`.
5. `clk_eliza_regs_configure()` calls `qcom_branch_set_force_mem_core()` for `gcc_ufs_phy_ice_core_clk` and `gcc_ufs_phy_axi_clk`, forcing memory core behavior needed by those UFS PHY clock branches.

After probe, consumers use standard CCF, reset, and genpd APIs. Many RCGs use `clk_rcg2_shared_ops`, `clk_rcg2_shared_no_init_park_ops`, or `clk_rcg2_shared_floor_ops`, which is important for shared hardware and safe parking behavior.

## State And Persistence

Software state is static metadata only. Hardware registers persist the active clock-controller state: PLL enable bits, postdiv selection, mux selection, RCG command state, M/N/D values, branch enables, halt state, HWCG state, reset state, and GDSC state. The driver data affects initial hardware policy by marking critical CBCRs and forcing memory core on for two UFS clocks.

The GDSCs include PCIe controller/PHY domains, UFS memory/PHY domains, USB30 primary, and USB3 PHY. Several use `POLL_CFG_GDSCR`, `RETAIN_FF_ENABLE`, and some PCIe domains are `VOTABLE`, with collapse control bits in `0x5214c`. These flags determine persistence and retention behavior across power transitions.

## Dependencies And Integration Points

The driver depends on Qualcomm clock helpers from the same directory: alpha PLLs, RCGs, branches, regmap dividers/muxes/PHY muxes, GDSC, reset, and common probe code. It also depends on the Eliza dt-binding header for all public clock, reset, and GDSC IDs.

Devicetree integration supplies parent indexes for `bi_tcxo`, `sleep_clk`, PCIe pipe clocks, UFS PHY symbol clocks, and USB3 PHY pipe clock. Downstream consumers include PCIe host/PHY drivers, UFS PHY/storage, USB3 controller/PHY, QUPv3 UART/I2C/SPI/QSPI blocks, SDCC/eMMC/SD, PDM audio, GPU SMMU/GEMNOC, camera/display/video fabric, and reset consumers for those subsystems.

Critical CBCR entries protect essential camera, display, GPU, PCIe RSCC, and video AHB/XO clocks from being treated as ordinary unused gates. DFS metadata integrates QUPv3 RCGs with Qualcomm dynamic frequency switching infrastructure.

## Risks And Maintenance Notes

The public arrays are ABI-sensitive. `gcc_eliza_clocks[]`, `gcc_eliza_gdscs[]`, and `gcc_eliza_resets[]` must stay aligned with `qcom,eliza-gcc.h`. The source uses many large register offsets and shared vote registers; incorrect bits can disturb unrelated global clocks.

The QUPv3 RCGs use `clk_rcg2_shared_no_init_park_ops`, which indicates the driver should avoid unsafe initialization or parking of clocks shared with firmware or other processors. Replacing these ops with generic RCG ops could introduce boot-time or runtime glitches. The `hw_clk_ctrl = true` flags similarly reflect hardware-managed behavior and should not be removed casually.

PHY-derived pipe and symbol clocks use muxes around external PHY outputs. These paths commonly have delayed or skipped halt checks (`BRANCH_HALT_DELAY`, `BRANCH_HALT_SKIP`) because clock availability depends on PHY state. Treating them as ordinary halt-polled branches risks false timeouts during PHY sequencing.

The UFS force-memory-core configuration is a platform-specific side effect. Removing or moving `clk_eliza_regs_configure()` can cause UFS PHY ICE/AXI clock behavior changes that may only appear under storage power collapse or high-throughput workloads.

## Test Signals

Static checks should verify that the binding constants cover every array entry and that `gcc_eliza_driver_data` points to live clock objects. Probe should log successful registration for `qcom,eliza-gcc` with no regmap or registration errors. Runtime tests should inspect `clk_summary` for parent selection and rates on QUPv3, SDCC, PCIe, UFS, and USB3 clocks; confirm critical CBCRs remain enabled when required; and validate DFS transitions for QUPv3 serial clocks. GDSC tests should power-cycle PCIe, UFS, USB30, and USB3 PHY domains. End-to-end signals include working PCIe enumeration, UFS storage, USB3 link training, SDCC I/O, QUPv3 serial peripherals, and reset assertion/deassertion for the listed BCRs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-eliza.c -->
