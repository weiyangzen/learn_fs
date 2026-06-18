# subset-b-001153 grouped research

Research covers 21 Qualcomm clock/reset controller source files under `sources/distributed-fs/ceph-client/drivers/clk/qcom/`. Each section is delimited for reconciliation into source-tree-aligned per-file outputs.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/nsscc-qca8k.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/nsscc-qca8k.c

## Purpose
This driver exposes the QCA8084/QCA8K NSS clock controller over an MDIO-attached device. It registers a large set of switch-core, APB/AHB, TLMM, MDIO, SERDES, GEPHY, and MAC0-MAC5 RX/TX clocks plus reset lines through the Qualcomm common clock framework. Unlike normal memory-mapped qcom clock controllers, its register access is implemented through Clause 22 MDIO transactions.

## Important APIs, types, and functions
- `nss_cc_qca8k_clocks[]` maps dt-binding clock IDs to `struct clk_regmap` instances: RCGs (`clk_rcg2`), dividers (`clk_regmap_div`), muxes (`clk_regmap_mux`), and branches (`clk_branch`).
- `nss_cc_qca8k_resets[]` maps reset IDs to register/bit or bitmask entries consumed by `qcom_reset_ops` through `qcom_cc_really_probe()`.
- `convert_reg_to_mii_addr()` splits an NSSCC register address into MDIO register, PHY address, and page fields using the QCA8K masks/prefix constants.
- `qca8k_regmap_read()`, `qca8k_regmap_write()`, and `qca8k_regmap_update_bits()` are the custom regmap bus callbacks. They add `QCA8K_CLK_REG_BASE`, select the MDIO page, and perform 32-bit access as two 16-bit MDIO accesses while holding `bus->mdio_lock`.
- `nss_cc_qca8k_clock_enable_and_reset()` enables the reference clock and optionally toggles the `"reset"` GPIO after a 100 ms high pulse.
- `nss_cc_qca8k_probe()` initializes the custom regmap with `devm_regmap_init()` and calls `qcom_cc_really_probe()`.

## Control flow
The MDIO core matches `"qcom,qca8084-nsscc"` and invokes `nss_cc_qca8k_probe()`. Probe first enables the unnamed input clock and releases optional reset GPIO, then creates a regmap whose read/write/update callbacks translate qcom CC register operations into MDIO page select plus lower/upper 16-bit transactions. The common qcom CC registration then publishes clocks and resets to consumers. Runtime clock operations go through standard CCF branch/RCG/divider/mux ops, but all register traffic is serialized by the MDIO bus lock.

## State and persistence behavior
Persistent hardware state is the NSSCC register block behind MDIO: clock source selectors, dividers, branch enables, reset bits, and page-selected MDIO access. The driver keeps no dynamic software state beyond static descriptors and devres-managed clock/regmap/GPIO handles. Reset operations persist in hardware until deasserted. `disable_locking = true` delegates serialization to explicit `mdio_lock` critical sections rather than regmap's internal lock.

## Dependencies and integration points
The file integrates with the MDIO driver model (`mdio_module_driver`), CCF, qcom common CC helpers, qcom reset support, device-tree clock/reset bindings, optional GPIO reset, and the parent MDIO bus. Consumers reference the clocks/resets by `qcom,qca8k-nsscc` binding IDs. Parent sources include UNIPHY/SERDES and fixed external clocks represented through `clk_parent_data`.

## Risks
MDIO access is fragile because every 32-bit operation depends on correct page selection and two 16-bit transfers; a failed write logs but `qca8k_mii_write()` itself returns void, so write failures can be partially hidden after page selection succeeds. The custom update-bits path performs read/modify/write under the MDIO lock, which is correct for bus serialization but cannot prevent hardware-side concurrent changes. Register address masks and dt-binding array indices must remain synchronized with hardware documentation. The reset GPIO pulse depends on the reference clock being enabled first.

## Test signals
Probe success should show all NSSCC clocks and reset controls registered for a matching MDIO node. Useful validation includes boot logs without MDIO read/write/page errors, `clk_summary` visibility for MAC/SERDES/AHB clocks, successful clock rate changes for RCG/divider-controlled MAC paths, reset-controller assertions for GEPHY/global/XPCS lines, and network bring-up across all switch ports. Fault tests should cover missing reference clock, absent optional reset GPIO, and MDIO transaction failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/nsscc-qca8k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/nwgcc-nord.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/nwgcc-nord.c

## Purpose
This platform driver registers the NORD NWGCC clock controller. It primarily supplies NoC-facing GPU, video, camera, display, EVA, DPRX, general-purpose, and measurement clocks, plus a small set of block resets.

## Important APIs, types, and functions
- Static PLL descriptors `nw_gcc_gpll0` and `nw_gcc_gpll0_out_even` provide GPLL0 and its even post-divider.
- `parent_map`/`clk_parent_data` tables define XO/GPLL parent choices for RCGs and branch-derived source clocks.
- `nw_gcc_gp1_clk_src` and `nw_gcc_gp2_clk_src` are programmable RCGs with common GP frequency tables.
- Numerous `clk_branch` descriptors expose vote/branch gates for camera, display, GPU, video, EVA, HSCNOC, and SMMU/TCU paths.
- `nw_gcc_nord_clocks[]`, `nw_gcc_nord_resets[]`, `nw_gcc_nord_critical_cbcrs[]`, and `nw_gcc_nord_desc` form the qcom CC registration payload.
- `nw_gcc_nord_probe()` calls `qcom_cc_probe()`.

## Control flow
The platform bus matches `"qcom,nord-nwgcc"` and calls probe. `qcom_cc_probe()` maps the MMIO resource using `nw_gcc_nord_regmap_config`, registers the clock table and reset map, and applies `qcom_cc_driver_data` so critical CBCRs stay enabled. After registration, consumers enable/disable branches or reprogram GP RCGs through normal CCF calls.

## State and persistence behavior
The driver has static descriptor state only. Persistent state lives in NWGCC registers: branch enable bits, halt status, GP RCG command/config registers, GPLL postdivider state, and reset registers. Critical CBCRs are intentionally kept enabled across normal consumer churn.

## Dependencies and integration points
It depends on qcom common CC helpers, alpha PLL, branch, RCG, divider, mux, reset support, and `dt-bindings/clock/qcom,nord-nwgcc.h`. Integration is device-tree based and provides infrastructure clocks to GPU/NoC/display/video/camera consumers rather than a user-facing subsystem.

## Risks
Most branch clocks use fixed register offsets and binding-index array positions; an off-by-one in the binding or descriptor array would expose the wrong hardware clock. Critical CBCR choices can mask missing consumers or keep hardware powered. Reset map offsets must match the NWGCC register map because qcom reset ops perform direct bit updates.

## Test signals
Boot should bind `nwgcc-nord` without regmap errors and show the exported clock names in `clk_summary`. GPU/display/video/camera traffic should be able to vote their AXI/HF/SF paths. Reset-controller lookups for the NWGCC reset IDs should assert/deassert the intended blocks. Suspend/resume and unused-clock disabling should preserve critical CBCR state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/nwgcc-nord.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/q6sstop-qcs404.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/q6sstop-qcs404.c

## Purpose
This driver registers QCS404 Q6SSTOP/LCC clocks and one reset used around the Hexagon/Q6 subsystem, and also registers a TCSR clock region in the same probe path.

## Important APIs, types, and functions
- `clk_branch` descriptors expose AHB fabric, Q6SS AHBS/AHBM/AXIM, TCM slave, sleep, and TCSR LCC CSR branch clocks.
- `q6sstop_qcs404_clocks[]` and `q6sstop_qcs404_resets[]` describe the main Q6SSTOP clock/reset block.
- `tcsr_qcs404_clocks[]` and `tcsr_qcs404_desc` describe the secondary TCSR region.
- `q6sstopcc_qcs404_probe()` enables runtime PM, acquires an interface clock through `pm_clk_add()`, resumes the device, and probes MMIO resource index 1 for TCSR then index 0 for Q6SSTOP.
- `q6sstopcc_pm_ops` uses `pm_clk_suspend`/`pm_clk_resume`.

## Control flow
After matching `"qcom,qcs404-q6sstopcc"`, probe sets up runtime PM and an unnamed PM clock. It resumes the device so register access is safe, names the shared regmap config `"q6sstop_tcsr"` and registers the TCSR clock at resource index 1, then renames it `"q6sstop_cc"` and registers the main controller at index 0. On failure it releases the runtime PM reference synchronously.

## State and persistence behavior
Hardware registers hold branch gate states and the `Q6SSTOP_BCR_RESET` bit. Software state is limited to static descriptors and runtime-PM/devres bookkeeping. The mutable `q6sstop_regmap_config.name` is reused between the two qcom CC probe calls.

## Dependencies and integration points
The file depends on qcom common CC/reset helpers, CCF branch ops, regmap, platform resources, runtime PM, and PM clock support. It integrates with device tree through `qcom,q6sstopcc-qcs404` clock binding IDs and the platform node's two MMIO resources.

## Risks
Probe assumes resource index 1 is TCSR and index 0 is Q6SSTOP; a device-tree resource order mismatch will register the wrong register block. The shared mutable regmap config name is simple but must not be used concurrently. Runtime PM failures leave the controller unregistered, and missing interface clock acquisition fails probe.

## Test signals
Validation should include successful probe with two mapped regions, `clk_summary` entries for Q6SS and TCSR clocks, working runtime suspend/resume, and reset-controller operation for `Q6SSTOP_BCR_RESET`. Boot logs should not contain `"failed to acquire iface clock"` or qcom CC probe errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/q6sstop-qcs404.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/reset.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/reset.c

## Purpose
This file implements the shared Qualcomm clock-controller reset operations used by many qcom CC drivers. It translates reset-controller assertions into regmap bit updates based on per-controller `qcom_reset_map` tables.

## Important APIs, types, and functions
- `qcom_reset_ops` exports `.reset`, `.assert`, and `.deassert` operations.
- `qcom_reset()` asserts a reset line, sleeps for the map's `udelay` or 1 microsecond by default, then deasserts it.
- `qcom_reset_set_assert()` selects either `map->bitmask` or `BIT(map->bit)`, writes the asserted/deasserted value with `regmap_update_bits()`, and performs a read-back to flush the write.
- `qcom_reset_assert()` and `qcom_reset_deassert()` are thin wrappers.

## Control flow
A qcom CC driver registers a reset controller whose `reset_map` points at file-local reset descriptors. Reset framework calls arrive through `qcom_reset_ops`; the implementation derives the containing `qcom_reset_controller`, indexes the map by reset ID, updates the target register, reads back for write completion, and returns success.

## State and persistence behavior
Reset state is entirely hardware-backed in the regmap target. The operation does not cache state or track ownership. A pulse reset persists only for the configured sleep interval between assert and deassert; assert/deassert calls leave the hardware bit in the requested final state.

## Dependencies and integration points
The file depends on Linux reset-controller APIs, regmap, bitops, `fsleep()`, and `reset.h` types. It is exported GPL-only for qcom clock-controller modules and is integrated by `qcom_cc_really_probe()`/descriptor code that provides reset maps.

## Risks
The code ignores return values from `regmap_update_bits()` and `regmap_read()`, so bus/register write errors are not propagated. The map index must be valid and supplied by the reset framework; invalid IDs would read beyond the reset map. Default 1 us pulses may be insufficient for hardware that needs a longer delay unless `udelay` is specified.

## Test signals
Useful tests include reset-controller assert/deassert/reset calls for single-bit and bitmask resets, register read-back confirming final bit state, and fault injection for regmap errors to show current non-propagation behavior. Hardware bring-up should verify blocks exit reset after the expected pulse width.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/reset.h -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/reset.h

## Purpose
This header declares the shared reset descriptor and controller types used by Qualcomm clock-controller drivers, plus the exported `qcom_reset_ops` operations implemented in `reset.c`.

## Important APIs, types, and functions
- `struct qcom_reset_map` describes one reset line: register offset, bit index, optional pulse delay in microseconds, and optional multi-bit `bitmask`.
- `struct qcom_reset_controller` bundles a reset map, target `struct regmap`, and embedded `struct reset_controller_dev`.
- `to_qcom_reset_controller()` converts a reset-controller device pointer back to the qcom container.
- `extern const struct reset_control_ops qcom_reset_ops` is the operation table shared by qcom CC drivers.

## Control flow
Clock-controller drivers define static arrays of `qcom_reset_map` and pass them through qcom CC descriptors. The common probe path creates a `qcom_reset_controller`, sets up the embedded reset framework device, and routes reset framework callbacks to `qcom_reset_ops`.

## State and persistence behavior
The header defines no runtime state by itself. It shapes how reset state is represented: static reset maps plus a regmap pointer to persistent hardware reset registers.

## Dependencies and integration points
It includes Linux reset-controller declarations and forward-declares `struct regmap`. It is included by qcom CC drivers with reset support and by `reset.c`.

## Risks
The macro includes a trailing semicolon in its definition, which matches current usage but can surprise unusual expression contexts. `qcom_reset_map` can represent either a bit or bitmask; authors must avoid setting inconsistent fields. Map order must match dt-binding reset IDs.

## Test signals
Compile coverage from qcom CC drivers is the primary signal. Runtime tests should indirectly validate that maps declared with this type register reset controls and that both bit and bitmask entries operate through `qcom_reset_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/segcc-nord.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/segcc-nord.c

## Purpose
This driver registers the NORD SEGCC controller, covering south/east general clocks for dual Ethernet MACs and QUPv3 serial engine wrappers. It provides PLLs, RCGs, branches, DFS-capable serial clocks, GDSCs, and reset lines.

## Important APIs, types, and functions
- `se_gcc_gpll0`, `se_gcc_gpll2`, `se_gcc_gpll4`, `se_gcc_gpll5`, and `se_gcc_gpll0_out_even` define GPLL sources and a postdivider.
- Parent maps/data describe XO, sleep, GPLL, EMAC/SGMII/RGMII/XGXS, and QUP parent choices.
- Frequency tables configure EMAC EEE/PTP/RGMII/PHY AUX, GP clocks, and QUPv3 S0-S6 serial sources.
- `clk_branch` descriptors expose EMAC AXI/PHY/PTP/RGMII/RPCS/XGXS and QUP wrapper AHB/core/serial clocks.
- `se_gcc_emac0_gdsc` and `se_gcc_emac1_gdsc` power-gate the two Ethernet MAC domains with polling and retention flags.
- `se_gcc_nord_dfs_clocks[]` registers DFS support for all QUPv3 wrap0/wrap1 S0-S6 RCGs.
- `se_gcc_nord_desc` wires clocks, resets, GDSCs, and driver data into `qcom_cc_probe()`.

## Control flow
The platform driver matches `"qcom,nord-segcc"` and invokes `se_gcc_nord_probe()`. The qcom common clock probe maps the MMIO range, registers clocks by binding ID, registers EMAC GDSCs and reset controls, and enables DFS metadata for QUP RCGs. After probe, serial and Ethernet consumers control clock rates and branch enables through CCF and genpd/reset APIs.

## State and persistence behavior
SEGCC hardware registers persist PLL, RCG, divider, branch, reset, DFS, and GDSC power state. The driver stores only static descriptors. GDSCs use `PWRSTS_OFF_ON`, `POLL_CFG_GDSCR`, and `RETAIN_FF_ENABLE`, so power-domain transitions are hardware-visible and retain selected flip-flop state.

## Dependencies and integration points
The file depends on qcom CCF helpers for alpha PLLs, PLLs, branches, RCGs, dividers, GDSCs, DFS, resets, regmap, and `dt-bindings/clock/qcom,nord-segcc.h`. It integrates with Ethernet MAC drivers, QUPv3 serial controllers, and reset/power-domain consumers through device-tree clock, reset, and power-domain references.

## Risks
This descriptor-heavy file has high binding-index and register-offset risk. QUP DFS lists must stay aligned with RCG definitions; missing an RCG would prevent dynamic frequency scaling. Ethernet clock parent/frequency tables must match PHY mode expectations or link timing may fail. GDSC wait values and retention flags are hardware-sensitive.

## Test signals
Boot should register SEGCC and show all EMAC/QUP/GP clocks in `clk_summary`. Ethernet link tests should cover both MACs and PTP/RGMII/SGMII paths. Serial tests should exercise QUP instances and rate changes across supported frequencies. Power-domain tests should toggle EMAC GDSCs, and reset tests should assert/deassert EMAC and QUP wrapper resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/segcc-nord.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-eliza.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-eliza.c

## Purpose
This TCSR clock-controller driver exposes one-bit reference-clock enables for Eliza HDMI, PCIe, UFS, USB2, and USB3 PHY-related consumers.

## Important APIs, types, and functions
- Six `clk_branch` descriptors gate `tcsr_hdmi_clkref_en`, PCIe 0/1, UFS, USB2, and USB3 reference clocks.
- Each branch uses `BRANCH_HALT_DELAY`, `BIT(0)`, `clk_branch2_ops`, and mostly parent `DT_BI_TCXO_PAD`.
- `tcsr_cc_eliza_clocks[]` maps dt-binding IDs to branch clocks.
- `tcsr_cc_eliza_desc` and `tcsr_cc_eliza_probe()` register the controller with `qcom_cc_probe()`.

## Control flow
The driver registers at `subsys_initcall`, matches `"qcom,eliza-tcsr"`, maps the MMIO region using `tcsr_cc_eliza_regmap_config`, and registers branch clocks. Consumers then enable a branch to set bit 0 at that branch's TCSR offset.

## State and persistence behavior
State is the hardware latch at offsets 0x0 through 0x1c. There is no software cache or runtime PM. Branch enable state persists in TCSR registers until changed by the clock framework or reset.

## Dependencies and integration points
It depends on qcom common CC helpers, CCF branch ops, regmap, platform driver support, and `dt-bindings/clock/qcom,eliza-tcsr.h`. It integrates with PHY/controller drivers needing stable TCXO-derived reference clocks.

## Risks
All clocks are simple bit-0 gates, so the main risk is incorrect offset or binding ID. `BRANCH_HALT_DELAY` avoids strict halt polling; this is appropriate for reference gates but gives less direct hardware confirmation.

## Test signals
Probe should occur early and expose all six clock names. USB/PCIe/UFS/HDMI bring-up should succeed when their clkrefs are requested. Register tracing should show bit 0 toggles at the documented offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-eliza.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-glymur.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-glymur.c

## Purpose
This driver exposes Glymur TCSR reference-clock gates for eDP, multiple PCIe lanes/controllers, USB2/USB3, and USB4.

## Important APIs, types, and functions
- Thirteen `clk_branch` descriptors gate eDP, PCIe 1-4, USB2 1-4, USB3 0-1, and USB4 1-2 clkrefs.
- All gates use `BRANCH_HALT_DELAY`, `BIT(0)`, `clk_branch2_ops`, and `DT_BI_TCXO_PAD` as the parent.
- `tcsr_cc_glymur_clocks[]` maps binding IDs, and `tcsr_cc_glymur_desc` supplies regmap/clock metadata to qcom CC.
- `tcsr_cc_glymur_probe()` is a thin `qcom_cc_probe()` wrapper.

## Control flow
Registered via `subsys_initcall`, the platform driver matches `"qcom,glymur-tcsr"`, maps the TCSR register block with max register 0x94, and exposes the branch clocks. Consumers request reference clocks and the branch ops set/clear bit 0 at each offset.

## State and persistence behavior
The only persistent state is the enable bit in each TCSR register. The driver has no dynamic memory state after probe beyond framework registrations.

## Dependencies and integration points
It uses qcom common CC, CCF branch ops, regmap, device-tree binding `qcom,glymur-tcsr`, and TCXO parent indexing. It integrates with PCIe, USB, USB4, and display PHY nodes.

## Risks
The file includes several qcom clock headers not needed for the simple gates, but behavior is unaffected. Hardware risk centers on offset correctness and consumer binding references. Delayed halt checking may hide a stuck gate.

## Test signals
Expected signals are early successful probe, `clk_summary` entries for all clkrefs, PCIe/USB/eDP PHY initialization succeeding, and register-level confirmation that bit 0 toggles at offsets 0x44-0x88 as consumers enable clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-glymur.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-kaanapali.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-kaanapali.c

## Purpose
This Kaanapali TCSR driver provides reference-clock gates for PCIe 0, UFS, USB2, and USB3.

## Important APIs, types, and functions
- Four `clk_branch` descriptors target offsets 0x15044, 0x1504c, 0x15054, and 0x1505c.
- USB/UFS clocks declare `DT_BI_TCXO_PAD` parent data; the PCIe branch has no explicit parent data despite the enum.
- `tcsr_cc_kaanapali_clocks[]`, `tcsr_cc_kaanapali_regmap_config`, and `tcsr_cc_kaanapali_desc` provide qcom CC metadata.
- `tcsr_cc_kaanapali_probe()` calls `qcom_cc_probe()`.

## Control flow
The subsys-init platform driver binds `"qcom,kaanapali-tcsr"`, maps the register block up to 0x3d000, and registers four branch clocks. Consumer enable requests set bit 0 at each configured offset.

## State and persistence behavior
State is persistent only in TCSR reference-clock enable registers. There is no runtime PM, cached state, or custom recovery path.

## Dependencies and integration points
The file integrates with qcom common CC, CCF branch ops, regmap, platform bus, and clock binding IDs from `dt-bindings/clock/qcom,sm8750-tcsr.h`. It provides clkrefs to PCIe, UFS, and USB PHY/controller nodes.

## Risks
It reuses the SM8750 TCSR binding include while matching Kaanapali, so binding compatibility must be intentional and kept aligned. The PCIe branch's missing parent data may be fine for a gate-only clock but differs from the other clkrefs. Large max register coverage means wrong offsets could still map without an immediate range failure.

## Test signals
Probe should expose four clock IDs. PCIe/UFS/USB PHY init on Kaanapali hardware should request and enable the clocks. Register readback should confirm bit 0 at the four high offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-kaanapali.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-nord.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-nord.c

## Purpose
This NORD TCSRCC driver exposes reference-clock gates for DisplayPort RX/TX lanes, PCIe, UFS, USB2/USB3 ports, and UX SGMII references.

## Important APIs, types, and functions
- Fifteen `clk_branch` descriptors use `BRANCH_HALT_DELAY`, bit 0, and `clk_branch2_ops`.
- Parent data uses `DT_BI_TCXO_PAD` for TCXO-derived clkrefs.
- `tcsr_cc_nord_clocks[]` maps NORD TCSR binding IDs to branches.
- `tcsr_cc_nord_desc` and `tcsr_cc_nord_probe()` register the clocks through `qcom_cc_probe()`.

## Control flow
At subsys init, the platform driver binds `"qcom,nord-tcsrcc"`, maps the TCSR block up to 0xf008, and registers branch gates. Peripheral drivers enable the relevant clkref, causing the branch ops to update bit 0 at DP/PCIe/UFS/USB/SGMII offsets.

## State and persistence behavior
The driver maintains no private runtime state. Hardware TCSR bits store reference-clock enable state and persist until consumer operations or reset alter them.

## Dependencies and integration points
It depends on qcom common CC, branch/regmap helpers, platform device matching, and `dt-bindings/clock/qcom,nord-tcsrcc.h`. It integrates with display, PCIe, UFS, USB, and network/SGMII consumers.

## Risks
The broad set of clkrefs makes binding index accuracy important. DP lane offsets are separated by 0x1000 regions; wrong offsets could break only a subset of display lanes. Because halt checks are delay-based, stuck or absent clkref feedback is not directly detected.

## Test signals
DisplayPort multi-lane, PCIe, UFS, USB2/USB3, and SGMII initialization should succeed with requested clock references. `clk_summary` should list all TCSRCC NORD gates, and register readback should show bit 0 changes at offsets such as 0xa008-0xf008 and USB/UFS offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-nord.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-sm8550.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-sm8550.c

## Purpose
This driver registers SM8550-family TCSR reference-clock gates, with a reduced descriptor for SAR2130P and a fuller descriptor for SM8550.

## Important APIs, types, and functions
- Six branch descriptors cover PCIe 0/1, UFS, UFS pad, USB2, and USB3 reference clocks.
- `tcsr_cc_sar2130p_clocks[]` omits UFS entries; `tcsr_cc_sm8550_clocks[]` includes all six.
- `of_device_id` entries attach `.data` pointers to either `tcsr_cc_sar2130p_desc` or `tcsr_cc_sm8550_desc`.
- `tcsr_cc_sm8550_probe()` maps the matched descriptor with `qcom_cc_map()` but then calls `qcom_cc_really_probe()` with `tcsr_cc_sm8550_desc`.

## Control flow
The subsys-init driver matches `"qcom,sar2130p-tcsr"` or `"qcom,sm8550-tcsr"`. Probe obtains match data for mapping, checks for mapping errors, and registers clocks. Consumers enable branch gates through CCF.

## State and persistence behavior
TCSR registers at 0x15100-0x15118 store the clock-reference enable state. No private mutable state is maintained.

## Dependencies and integration points
It uses qcom common CC, CCF branch ops, regmap, `of_device_get_match_data()`, and `dt-bindings/clock/qcom,sm8550-tcsr.h`. It integrates with PCIe, UFS, and USB PHY/controller device-tree nodes.

## Risks
The probe maps with match-specific data but always registers `tcsr_cc_sm8550_desc`; that appears inconsistent with the SAR2130P reduced descriptor and could expose clocks not meant for SAR2130P. Several branches use `BRANCH_HALT_SKIP`, so enable operations do not verify halt status. Binding arrays must match compatible-specific hardware.

## Test signals
On SM8550, all six clkrefs should register and enable. On SAR2130P, validation should specifically check whether UFS clocks appear unexpectedly and whether consumers bind correctly. Register readback and `clk_summary` should confirm branch states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-sm8550.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-sm8650.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-sm8650.c

## Purpose
This TCSRCC driver exposes SM8650 reference-clock gates for PCIe, UFS, UFS pad, USB2, and USB3, with special handling for Milos.

## Important APIs, types, and functions
- Six `clk_branch` descriptors use offsets in the 0x31100 range and `BRANCH_HALT_DELAY`.
- `tcsr_cc_sm8650_clocks[]` maps binding IDs to PCIe/UFS/USB clkrefs.
- `tcsr_cc_sm8650_probe()` checks `of_device_is_compatible(..., "qcom,milos-tcsr")`; for Milos it moves `tcsr_ufs_clkref_en` to offset 0x31118 and nulls USB2/USB3 clock entries.
- `qcom_cc_probe()` registers the resulting descriptor.

## Control flow
The platform driver binds either `"qcom,milos-tcsr"` or `"qcom,sm8650-tcsr"`. Probe mutates static descriptors for the Milos variant before common qcom CC registration. Clock consumers then enable branch gates by binding ID.

## State and persistence behavior
Hardware state is the bit-0 gate at each TCSR offset. The Milos compatibility path mutates static global descriptors and the clock array for the life of the module; because a single instance is expected, this is acceptable but not per-device isolated.

## Dependencies and integration points
The file integrates with qcom common CC, CCF, regmap, platform matching, `of_device_is_compatible()`, and `dt-bindings/clock/qcom,sm8650-tcsr.h`. Consumers are PCIe/UFS/USB PHY/controller drivers.

## Risks
Static mutation for Milos would be unsafe if both Milos and SM8650 instances could coexist. Nulling clock entries relies on qcom CC code accepting sparse arrays. Variant offset changes need hardware validation, especially because UFS moves to the same offset as the normal USB2 gate.

## Test signals
On SM8650, all six clocks should appear and toggle the 0x31100-0x31118 offsets. On Milos, USB2/USB3 clocks should be absent/unavailable and UFS should toggle 0x31118. Probe and peripheral bring-up logs should show no sparse-clock registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-sm8650.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-sm8750.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-sm8750.c

## Purpose
This driver registers SM8750 TCSR reference-clock gates for PCIe 0, UFS, USB2, and USB3.

## Important APIs, types, and functions
- Four `clk_branch` descriptors at offsets 0x0, 0x1000, 0x2000, and 0x3000.
- UFS/USB branches declare `DT_BI_TCXO_PAD` parent data; PCIe is a gate-only branch without explicit parent.
- `tcsr_cc_sm8750_clocks[]` maps binding IDs from `qcom,sm8750-tcsr.h`.
- `tcsr_cc_sm8750_probe()` calls `qcom_cc_probe()`.

## Control flow
The platform driver registers at subsys init and matches `"qcom,sm8750-tcsr"`. Probe maps the small TCSR region and registers branch clocks. Consumer enable requests set bit 0 at the corresponding region offset.

## State and persistence behavior
Only hardware TCSR enable bits store state. There is no runtime PM or software cache.

## Dependencies and integration points
It depends on qcom common CC, branch/regmap helpers, platform device matching, and the SM8750 TCSR dt-binding. It integrates with PCIe, UFS, and USB subsystems through clock phandles.

## Risks
The PCIe branch lacks explicit parent data while others point to TCXO. The simple four-offset layout is easy to audit, but any binding mismatch directly affects peripheral reference clocks. `BRANCH_HALT_DELAY` does not prove the hardware gate changed state.

## Test signals
Probe should expose four clocks. PCIe/UFS/USB PHY bring-up should request the expected clkrefs. Register readback should confirm bit 0 toggling at 0x0, 0x1000, 0x2000, and 0x3000.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-sm8750.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-x1e80100.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-x1e80100.c

## Purpose
This driver exposes X1E80100 TCSR reference-clock gates for eDP, multiple PCIe groups, USB3 multiport, USB2, UFS PHY, and USB4.

## Important APIs, types, and functions
- Twelve `clk_branch` descriptors target offsets 0x15100 through 0x15130.
- Branch names include PCIe 2-lane groups, PCIe 8-lane/4-lane, USB3 MP0/MP1, USB4 1/2, USB2 1/2, UFS PHY, and eDP.
- `tcsr_cc_x1e80100_clocks[]` maps binding IDs to branches.
- `tcsr_cc_x1e80100_probe()` wraps `qcom_cc_probe()`.

## Control flow
The subsys-init platform driver binds `"qcom,x1e80100-tcsr"`, maps the TCSR register range up to 0x2f000, and registers clkref branches. Peripheral consumers enable the needed reference clock through normal CCF APIs.

## State and persistence behavior
State is hardware-resident in bit 0 of each TCSR register. The driver has no per-device mutable data beyond common framework registration.

## Dependencies and integration points
It depends on qcom common CC, CCF branch ops, regmap, platform driver matching, and `dt-bindings/clock/qcom,x1e80100-tcsr.h`. It integrates with laptop/SoC display, PCIe, USB, USB4, and UFS PHY/controller nodes.

## Risks
The many high-speed I/O reference clocks make offset and binding accuracy important. A wrong clkref can selectively break only one physical port. Halt-delay checks are weak for debugging missing external reference behavior.

## Test signals
Expected signals include successful early probe, `clk_summary` entries for all twelve branches, functional PCIe/USB4/USB3/UFS/eDP bring-up, and register tracing showing bit 0 at each 0x151xx offset toggles with consumer usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-x1e80100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/turingcc-qcs404.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/turingcc-qcs404.c

## Purpose
This driver registers the QCS404 Turing clock controller, exposing always-on/wrapper/Q6SS AHB and AXI branch clocks around the Turing/QDSP subsystem.

## Important APIs, types, and functions
- Five `clk_branch` descriptors define wrapper AON, Q6SS AHBM, Q6 AXIM, Q6SS AHBS AON, and wrapper QoS AHBS AON clocks.
- AON branches use `clk_branch2_aon_ops`; regular branch uses `clk_branch2_ops`.
- `turingcc_clocks[]` maps binding IDs from `qcom,turingcc-qcs404.h`.
- `turingcc_probe()` enables runtime PM, creates/acquires a PM clock, resumes the device, calls `qcom_cc_probe()`, then releases the runtime PM reference.
- `turingcc_pm_ops` delegates runtime suspend/resume to PM clock helpers.

## Control flow
The platform driver matches `"qcom,qcs404-turingcc"`. Probe prepares runtime PM and the interface clock, resumes the hardware for MMIO access, registers the qcom CC descriptor, then idles the runtime PM reference. CCF consumers later toggle branches as needed.

## State and persistence behavior
Clock enable and halt state persists in Turing CC registers. Runtime PM controls the interface clock used for register access. No private software state is stored beyond devres/runtime-PM state.

## Dependencies and integration points
It depends on qcom common CC, branch ops, platform resources, runtime PM, PM clocks, regmap, and `dt-bindings/clock/qcom,turingcc-qcs404.h`. It integrates with Q6/Turing subsystem consumers that need bus and wrapper clocks.

## Risks
Missing interface clock or runtime PM resume failure prevents registration. AON branch semantics must match hardware; using non-AON ops on always-on paths could gate critical access. There are no reset maps, so reset control must come from elsewhere.

## Test signals
Probe should log no interface-clock errors and register five clocks. Runtime suspend/resume should preserve register access. Q6/Turing boot or firmware loading should exercise the AHBS/AHBM/AXIM paths. `clk_summary` should show AON branches with expected prepare/enable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/turingcc-qcs404.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-glymur.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-glymur.c

## Purpose
This driver registers Glymur VIDEOCC clocks, reset lines, and GDSCs for MVS0/MVS0C/MVS1 video hardware domains.

## Important APIs, types, and functions
- `video_cc_pll0` is a Taycan EKO T alpha PLL configured for 720 MHz.
- RCGs provide AHB, MVS0, sleep, and XO sources; dividers derive MVS0/MVS0C/MVS1 clocks.
- Branches expose MVS core, freerun, and shift clocks.
- `video_cc_mvs0_gdsc`, `video_cc_mvs0c_gdsc`, and `video_cc_mvs1_gdsc` define power domains.
- `video_cc_glymur_resets[]` maps interface/MVS block resets and freerun clock resets.
- `clk_glymur_regs_configure()` sets bit 0 at 0x9f24 before/while registering via driver data.
- `video_cc_glymur_desc` sets `.use_rpm = true` and includes PLLs, critical CBCRs, resets, and GDSCs.

## Control flow
The platform driver matches `"qcom,glymur-videocc"` and calls `qcom_cc_probe()`. Common qcom code maps the register block, configures alpha PLLs, keeps critical AHB/sleep/XO CBCRs enabled, runs the register configure hook, registers clocks, resets, and power domains, and honors RPM integration.

## State and persistence behavior
VIDEOCC registers hold PLL configuration, RCG selections, dividers, branch enables, reset bits, and GDSC states. The driver is descriptor-only after probe. Critical clocks are intentionally kept enabled.

## Dependencies and integration points
It depends on qcom alpha PLL, branch, RCG, divider, mux, GDSC, reset, regmap, and `dt-bindings/clock/qcom,glymur-videocc.h`. It integrates with video codec drivers through clocks, resets, and genpd domains.

## Risks
PLL frequency tables and divider topology must match video performance points. The 0x9f24 register tweak is hardware-specific and could regress if moved or omitted. GDSC ordering and reset IDs must match bindings. Critical CBCRs can keep hardware active and affect power measurements.

## Test signals
Video encode/decode should power domains on/off and switch clock rates successfully. `clk_summary` should show PLL0 and MVS clocks. Reset tests should hit interface/MVS reset lines. Power tests should confirm GDSC transitions and critical clocks remaining enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-glymur.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-kaanapali.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-kaanapali.c

## Purpose
This driver registers Kaanapali VIDEOCC, including four video PLLs, MVS0/MVS0A/MVS0B/MVS0C/VPP clocks, GDSCs, and resets.

## Important APIs, types, and functions
- `video_cc_pll0` through `video_cc_pll3` are Taycan EKO T PLLs configured for 360/480 MHz-class sources.
- RCGs generate AHB and MVS0/MVS0A/MVS0B/MVS0C rates; branches expose core, freerun, shift, and VPP clocks.
- `clk_mem_branch video_cc_mvs0_freerun_clk` indicates a memory-retention style branch for one freerun path.
- Five GDSCs cover MVS0A, MVS0, VPP1, VPP0, and MVS0C.
- `clk_kaanapali_regs_configure()` enables clk_on sync and sets `ACCU_CFG_MASK` on several GDSC CFG3 registers.
- Driver data lists all four PLLs and critical AHB/sleep/TS_XO/XO CBCRs.

## Control flow
On `"qcom,kaanapali-videocc"` match, `qcom_cc_probe()` maps the register block, configures PLLs, applies the hardware register configure callback, marks critical CBCRs, and registers clocks, resets, and GDSCs. Consumers then use CCF and genpd to drive video engines and VPP paths.

## State and persistence behavior
Hardware retains PLL programming, RCG settings, branch gates, reset bits, and GDSC power state. The configure hook writes persistent GDSC timing/sync bits. The driver keeps only static descriptors.

## Dependencies and integration points
It integrates with qcom CCF primitives, GDSC power domains, reset framework, regmap, and Kaanapali video dt-bindings. Consumers are video codec and VPP/display-adjacent blocks that request named clocks and power domains.

## Risks
This is a dense descriptor file with high risk in PLL config values, GDSC CFG3 offsets, and binding array order. The hardware recommendations in `clk_kaanapali_regs_configure()` are mandatory-looking; missing them may cause reset or power sequencing failures. Critical clocks affect idle power.

## Test signals
Video workloads should exercise all MVS/VPP domains. Rate tests should select entries from each MVS RCG table. Power-domain tests should verify GDSC on/off sequencing after the ACCU config writes. Reset lines and always-on critical clocks should be visible through debugfs and functional tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-kaanapali.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-milos.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-milos.c

## Purpose
This Milos VIDEOCC driver registers a compact video clock controller with one PLL, MVS0/MVS0C clocks, two GDSCs, and reset controls.

## Important APIs, types, and functions
- `video_cc_pll0` is a Lucid OLE alpha PLL configured around 604.8 MHz.
- Parent maps include XO and sleep sources with always-on parent variants.
- RCGs provide AHB, MVS0, sleep, and XO sources; dividers derive MVS0 and MVS0C divided paths.
- Branches expose MVS0/MVS0C core and shift clocks.
- `video_cc_milos_gdscs[]`, `video_cc_milos_resets[]`, `video_cc_milos_plls[]`, and critical CBCRs are collected in driver data/descriptor.
- `video_cc_milos_probe()` delegates to `qcom_cc_probe()`.

## Control flow
The platform driver matches `"qcom,milos-videocc"`. Common qcom probe maps registers, configures the listed PLL, keeps critical AHB/sleep/XO CBCRs enabled, and registers clocks, resets, and GDSCs. Video consumers then enable domains and clocks.

## State and persistence behavior
PLL, RCG, divider, branch, reset, and GDSC state lives in hardware registers. `.use_rpm = true` requests RPM-aware handling in the qcom CC layer. Software state remains static.

## Dependencies and integration points
It depends on qcom alpha PLL, branch, RCG, divider, GDSC, reset, regmap, platform matching, and `dt-bindings/clock/qcom,milos-videocc.h`. It serves video codec drivers and power-domain consumers.

## Risks
The Milos-specific PLL frequency and parent data must align with firmware/OPP expectations. Sparse or wrong reset mapping would break video block recovery. Critical clocks and RPM integration need power testing to avoid idle regressions.

## Test signals
Successful boot should register PLL0, MVS0/MVS0C clocks, and two GDSCs. Video encode/decode should power-cycle domains, change rates, and survive reset assertions. `clk_summary` should show critical CBCRs enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-milos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-qcs615.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-qcs615.c

## Purpose
This driver registers QCS615 VIDEOCC for Venus/vcodec hardware, including one video PLL, sleep/Venus RCGs, branch clocks, resets, and two GDSCs.

## Important APIs, types, and functions
- `video_pll0` is an alpha PLL configured for a 600 MHz VCO setting.
- RCGs generate sleep and Venus clock sources.
- Branches expose sleep, vcodec0 AXI/core, Venus AHB, Venus CTL AXI/core.
- `vcodec0_gdsc` and `venus_gdsc` provide power domains.
- `video_cc_qcs615_resets[]` maps interface, vcodec0, and Venus resets.
- Driver data lists PLL0 and critical XO CBCR 0xab8.

## Control flow
The platform driver matches `"qcom,qcs615-videocc"` and calls `qcom_cc_probe()`. Common code maps registers, configures PLL0, keeps the critical XO clock enabled, and registers clocks, resets, and GDSCs for video consumers.

## State and persistence behavior
State is hardware-backed in VIDEOCC registers. The driver does not maintain dynamic state. GDSC power state persists in hardware and is managed by genpd via qcom GDSC callbacks.

## Dependencies and integration points
It uses qcom alpha PLL, PLL, branch, RCG, divider/mux headers, common CC, GDSC, reset, regmap, and `dt-bindings/clock/qcom,qcs615-videocc.h`. It integrates with Venus/vcodec drivers.

## Risks
PLL config and frequency tables must match supported video rates. Critical XO enable is required for stable access but affects power. Reset offsets are small and close together; binding/order mistakes can affect recovery operations.

## Test signals
Test Venus decode/encode, vcodec domain power toggles, clock-rate selection for Venus, reset assertion/deassertion, and debugfs visibility of PLL0 plus branch clocks. Probe should produce no qcom CC registration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-qcs615.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sa8775p.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sa8775p.c

## Purpose
This driver registers SA8775P/QCS8300 VIDEOCC clocks, resets, and GDSCs for MVS0/MVS0C/MVS1/MVS1C video domains, with explicit runtime-PM and PLL setup in probe.

## Important APIs, types, and functions
- `video_pll0` and `video_pll1` are Lucid EVO alpha PLLs.
- RCGs cover AHB, MVS0, MVS1, sleep, XO, and a status/monitor divider path.
- Branches expose MVS0/MVS0C/MVS1/MVS1C clocks, PLL lock monitor, and SM observation clocks.
- Four GDSCs and seven reset map entries cover MVS domains and interface reset.
- `video_cc_sa8775p_probe()` enables runtime PM, maps registers, configures both PLLs, applies a QCS8300-specific MVS0C divider override, forces critical AHB/sleep/XO branches on, registers qcom CC, and drops the PM reference.

## Control flow
The platform driver matches `"qcom,sa8775p-videocc"` or `"qcom,qcs8300-videocc"`. Unlike many newer video drivers that rely entirely on driver data, probe manually performs power management, regmap mapping, PLL configuration, optional variant tweak, critical branch enables, and `qcom_cc_really_probe()`.

## State and persistence behavior
Runtime PM controls register-access power during probe. Hardware registers retain PLL configuration, variant divider override, branch enables, reset bits, and GDSC state. Critical branches are forced on by direct `qcom_branch_set_clk_en()` writes.

## Dependencies and integration points
It depends on qcom alpha PLL/PLL/branch/RCG/divider/mux/common/GDSC/reset helpers, regmap, runtime PM, platform matching, and SA8775P video dt-bindings. Video drivers consume its clocks, resets, and power domains; QCS8300 uses the compatible-specific divider behavior.

## Risks
Manual probe sequencing increases risk: each error path must release runtime PM correctly. The QCS8300 divider write is variant-specific and could misclock MVS0C if the compatible is wrong. Critical branch forcing affects power and masks missing consumers. No `qcom_cc_driver_data` lists PLLs, so PLL setup depends on probe code.

## Test signals
Run video workloads on both SA8775P and QCS8300. Confirm PLL0/PLL1 lock, MVS0/MVS1 rates, GDSC transitions, and reset behavior. On QCS8300, verify MVS0C divider register equals div-3 override. Runtime PM trace should show balanced get/put on success and map errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sa8775p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sc7180.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sc7180.c

## Purpose
This SC7180 VIDEOCC driver registers a small Venus/vcodec clock controller with one Fabia PLL, Venus/vcodec branch clocks, and two GDSCs.

## Important APIs, types, and functions
- `video_pll0` is a Fabia alpha PLL whose configuration is built locally in probe.
- `video_cc_venus_clk_src` is the main Venus RCG with rates from 100 MHz to 434 MHz.
- Branches expose vcodec0 AXI/core and Venus AHB/CTL AXI/CTL core clocks.
- `venus_gdsc` and `vcodec0_gdsc` expose power domains.
- `video_cc_sc7180_probe()` maps registers, fills `alpha_pll_config`, configures PLL0 with `clk_fabia_pll_configure()`, forces `VIDEO_CC_XO_CLK` on via `regmap_update_bits(0x984)`, and calls `qcom_cc_really_probe()`.

## Control flow
The platform driver matches `"qcom,sc7180-videocc"`. Probe manually maps the register block, programs PLL0, enables the XO branch, and registers clocks and GDSCs. Consumers then use CCF/genpd to run Venus and vcodec hardware.

## State and persistence behavior
VIDEOCC hardware registers store PLL programming, RCG source/rate, branch enables, and GDSC power state. The probe-local PLL config is not retained after programming. No reset map is registered by this driver.

## Dependencies and integration points
It depends on qcom alpha PLL, branch, RCG, common CC, GDSC, regmap, platform bus, and `dt-bindings/clock/qcom,videocc-sc7180.h`. It integrates with SC7180 Venus/vcodec drivers.

## Risks
Manual PLL config in probe must match hardware; there is no named static config table. The forced XO bit at 0x984 is critical and easy to miss in refactors. Lack of reset controls means consumers cannot recover video blocks through this driver.

## Test signals
Boot should register SC7180 VIDEOCC and show PLL0 plus Venus/vcodec clocks. Video decode/encode should exercise Venus RCG rates and GDSC transitions. Register readback should confirm XO bit 0 at 0x984 remains enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sc7180.c -->
