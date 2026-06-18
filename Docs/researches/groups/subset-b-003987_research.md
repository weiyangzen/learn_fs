# subset-b-003987 Research

Grouped research for Qualcomm interconnect driver source files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sc7280.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sc7280.c

## Purpose
Implements the Qualcomm SC7280 Network-on-Chip interconnect provider tables for the Linux interconnect framework. The file describes the SoC's RPMh-managed NoC topology: aggregating NoCs, clock virtual paths, CNOC2/CNOC3, display/config NoC, GEM NoC, LPASS, memory controller virtual path, multimedia NoC, NSP/CDSP NoC, and system NoC. It is declarative driver data rather than active algorithmic code; the common RPMh interconnect core consumes these descriptors to register ICC nodes and issue BCM bandwidth votes.

## Important APIs, Types, And Data
The primary type is `struct qcom_icc_node`, with node name, channel count, bus width, optional QoS box metadata, and link edges through `link_nodes`. Master and slave identifiers come from `dt-bindings/interconnect/qcom,sc7280.h`, and node arrays are indexed by those binding constants so device-tree consumers can request paths by stable IDs.

The file defines many `struct qcom_icc_bcm` instances such as `bcm_acv`, `bcm_cn0`, `bcm_cn1`, `bcm_mc0`, `bcm_mm0`, `bcm_qup0`, and `bcm_sn0`. These group nodes into Bus Clock Manager vote buckets. Some groups are marked `keepalive` to maintain essential fabric or memory paths, `bcm_acv` uses `enable_mask = BIT(3)`, and QUP clock groups use `vote_scale = 1`.

Provider descriptors are `struct qcom_icc_desc` objects for `sc7280_aggre1_noc`, `sc7280_aggre2_noc`, `sc7280_clk_virt`, `sc7280_cnoc2`, `sc7280_cnoc3`, `sc7280_dc_noc`, `sc7280_gem_noc`, `sc7280_lpass_ag_noc`, `sc7280_mc_virt`, `sc7280_mmss_noc`, `sc7280_nsp_noc`, and `sc7280_system_noc`. Most physical NoCs include `regmap_config` data with 32-bit registers, 4-byte stride, `fast_io`, and a NoC-specific `max_register`; the aggregating NoCs set `qos_requires_clocks = true`.

## Control Flow
At module load, the platform driver `qnoc-sc7280` is registered with `module_platform_driver`. Device-tree compatible strings in `qnoc_of_match` select one descriptor per NoC node, for example `qcom,sc7280-aggre1-noc` or `qcom,sc7280-system-noc`. Probe and remove are delegated entirely to `qcom_icc_rpmh_probe` and `qcom_icc_rpmh_remove`.

Runtime bandwidth control flows through the common interconnect framework: a client requests bandwidth between binding IDs, the core resolves those IDs to `qcom_icc_node` objects in the matching descriptor, walks the `link_nodes` graph, aggregates bandwidth over the relevant path, and the RPMh provider converts that aggregate into BCM votes. QoS-capable nodes such as QSPI, QUP, SDCC, UFS, USB, PCIe, and QDSS masters carry QoS box offsets and priorities that the common code may program through the descriptor's regmap.

## State And Persistence
All topology, BCM, and QoS data is static kernel data. Persistent hardware state is limited to register programming and RPMh/BCM votes made by the common provider after probe; this source does not maintain private mutable state or allocate per-client structures directly. `icc_sync_state` is supplied as the driver sync-state callback so the framework can coordinate initial constraints after consumers have probed.

## Dependencies And Integration Points
This file depends on the Linux device, module, platform-device, interconnect, and interconnect-provider APIs; Qualcomm-specific helpers in `bcm-voter.h` and `icc-rpmh.h`; and the SC7280 device-tree binding header. It integrates with SC7280 DTS nodes through compatible strings and with peripheral drivers through interconnect specifiers referencing the binding IDs. Hardware integration points include RPMh BCM voting, QoS register programming, and NoC clocks needed for QoS programming on aggregation NoCs.

## Risks
The main correctness risk is binding or topology drift: a wrong array index, missing link, or incorrect compatible-to-descriptor mapping can make interconnect paths fail or vote on the wrong fabric. BCM grouping and keepalive flags are performance- and power-sensitive; under-voting can cause stalls or data corruption under load, while over-voting wastes power. QoS offsets and `max_register` bounds must match hardware manuals because bad offsets can program unrelated registers. The file has empty BCM arrays for some config-only fabrics, so maintainers must distinguish intentionally unvoted configuration paths from omissions.

## Test Signals
Build coverage should include this driver with `CONFIG_INTERCONNECT_QCOM_SC7280` and device-tree binding checks for the compatible strings and ID references. Runtime smoke tests are successful probe of all SC7280 NoC providers, absence of `-EPROBE_DEFER` or invalid path errors from interconnect consumers, and visible interconnect nodes in debugfs when enabled. Functional signals include storage, USB, PCIe, display, camera/video, GPU, audio/LPASS, CDSP, and memory bandwidth behavior under load with no RPMh vote errors or QoS register faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sc7280.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sc8180x.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sc8180x.c

## Purpose
Defines the Qualcomm SC8180X interconnect topology for RPMh-controlled NoC fabrics. It covers aggregation NoCs, camera virtual NoC, compute/NPU NoC, config NoC, display/config NoC, GEM NoC, memory-controller virtual path, multimedia NoC, system NoC, and a QUP virtual clock fabric. The source is a data provider for the common Qualcomm RPMh interconnect driver.

## Important APIs, Types, And Data
The central data model is a set of static `struct qcom_icc_node` definitions whose names use master/slave prefixes such as `mas_qhm_*`, `mas_xm_*`, and `slv_qhs_*`. These nodes define channel counts, bus widths, and path edges through `link_nodes`, and are exposed through arrays indexed by IDs from `dt-bindings/interconnect/qcom,sc8180x.h`.

`struct qcom_icc_bcm` groups represent RPMh BCM voting targets. Notable BCMs include memory buckets `bcm_acv` and `bcm_mc0`, shared LLCC/GEM buckets `bcm_sh0`, `bcm_sh2`, and `bcm_sh3`, multimedia buckets `bcm_mm0` through `bcm_mm2`, compute buckets `bcm_co0` and `bcm_co2`, configuration bucket `bcm_cn0`, QUP bucket `bcm_qup0`, and system NoC buckets `bcm_sn0` through `bcm_sn15`. Several buckets are marked `keepalive`, including memory, compute, application, and selected system/config paths.

The exported provider descriptors are `sc8180x_aggre1_noc`, `sc8180x_aggre2_noc`, `sc8180x_camnoc_virt`, `sc8180x_compute_noc`, `sc8180x_config_noc`, `sc8180x_dc_noc`, `sc8180x_gem_noc`, `sc8180x_mc_virt`, `sc8180x_mmss_noc`, `sc8180x_system_noc`, and `sc8180x_qup_virt`. Unlike SC7280, these descriptors do not carry local regmap configuration in this file, leaving programming details to the common RPMh provider and descriptor defaults.

## Control Flow
The platform driver named `qnoc-sc8180x` is registered with `module_platform_driver`. During probe, `qcom_icc_rpmh_probe` matches the device-tree compatible string to one descriptor in `qnoc_of_match`, registers the nodes for that fabric with the interconnect framework, and prepares BCM voting. Removal is handled by `qcom_icc_rpmh_remove`.

At runtime, client bandwidth requests are resolved from DT binding IDs into descriptor node arrays. The interconnect framework traverses the static graph, aggregates votes on nodes and BCM groups, then the RPMh common layer sends appropriate BCM votes. The QUP virtual fabric maps QUP core masters and slaves into a separate descriptor so serial-engine clock-style votes can be represented through ICC requests.

## State And Persistence
The file has no dynamic state of its own. Static node arrays and BCM arrays persist for the module lifetime. Hardware-visible state is created by common probe registration and by subsequent RPMh votes in response to interconnect framework requests. `icc_sync_state` coordinates late synchronization once consumers have had a chance to vote, reducing the risk of dropping boot-time constraints too early.

## Dependencies And Integration Points
It depends on Linux platform driver, module, device-tree match, and interconnect provider infrastructure; Qualcomm `bcm-voter.h` and `icc-rpmh.h`; and SC8180X binding IDs. Integration is through DTS compatibles such as `qcom,sc8180x-aggre1-noc`, `qcom,sc8180x-compute-noc`, and `qcom,sc8180x-qup-virt`. Consumers include UFS, USB, PCIe, EMAC, SDCC, QUP, camera, display, video, NPU/CDSP, GPU, memory, and debug/trace blocks.

## Risks
The most important risks are inaccurate static topology and BCM grouping. A misplaced node in `config_noc_nodes` or `system_noc_nodes` may let clients probe but route votes through the wrong fabric. Keepalive choices affect both stability and idle power. SC8180X has broad config and system fabrics with many endpoints, so binding index mistakes are easy to miss at compile time if array entries remain syntactically valid. Absence of local regmap constraints means changes rely heavily on common RPMh behavior and DT correctness.

## Test Signals
Compile-test with the SC8180X interconnect driver enabled and run DT binding validation for all compatible strings. Runtime signals include successful registration of all NoC providers, interconnect consumer probe success for storage/network/PCIe/display/camera/video/GPU/NPU clients, no RPMh BCM vote failures, and bandwidth-sensitive workloads maintaining performance without excessive always-on power. Debugfs interconnect topology, when available, should show expected nodes and paths for each descriptor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sc8180x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sc8280xp.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sc8280xp.c

## Purpose
Provides the Qualcomm SC8280XP interconnect topology for the Linux interconnect framework and the Qualcomm RPMh BCM voter. This SoC has a large laptop-class fabric, and the file maps aggregation, USB aggregation, config, display/config, GEM, LPASS, memory-controller virtual, multimedia, dual NSP/CDSP, and system NoC domains into descriptors consumed by the common RPMh provider.

## Important APIs, Types, And Data
Each endpoint and fabric bridge is represented by `struct qcom_icc_node`. Nodes define `channels`, `buswidth`, and `link_nodes`, and arrays are indexed by constants from `dt-bindings/interconnect/qcom,sc8280xp.h`. The source includes PCIe-heavy, USB4, multi-display, dual compute, dual NSP, and LPASS-specific nodes in addition to standard storage, QUP, IPA, GPU, camera, video, LLCC, memory, and debug endpoints.

`struct qcom_icc_bcm` instances are the RPMh vote groups. Important groups include `bcm_acv` and `bcm_mc0` for memory, `bcm_cn0` through `bcm_cn3` for config and PCIe/config-side targets, `bcm_mm0` and `bcm_mm1` for multimedia high-frequency and system-friendly traffic, `bcm_nsa*` and `bcm_nsb*` for the two NSP/CDSP fabrics, `bcm_pci0` for PCIe-to-GEM aggregation, QUP groups `bcm_qup0` through `bcm_qup2`, shared GEM groups `bcm_sh0` and `bcm_sh2`, and system groups `bcm_sn0` through `bcm_sn10`.

Provider descriptors include `sc8280xp_aggre1_noc`, `sc8280xp_aggre2_noc`, `sc8280xp_clk_virt`, `sc8280xp_config_noc`, `sc8280xp_dc_noc`, `sc8280xp_gem_noc`, `sc8280xp_lpass_ag_noc`, `sc8280xp_mc_virt`, `sc8280xp_mmss_noc`, `sc8280xp_nspa_noc`, `sc8280xp_nspb_noc`, and `sc8280xp_system_noc_main`. The SC8280XP source uses descriptor node and BCM arrays without local regmap configs, matching the RPMh table style used by newer Qualcomm interconnect drivers.

## Control Flow
The driver registers as `qnoc-sc8280xp`, but unlike most similar files it uses an explicit `core_initcall(qnoc_driver_init)` and `module_exit(qnoc_driver_exit)` instead of `module_platform_driver`. This causes early platform-driver registration, which is important for laptop-class boot ordering where many consumers may need interconnect providers early.

Probe, remove, and bandwidth-vote handling are delegated to `qcom_icc_rpmh_probe` and `qcom_icc_rpmh_remove`. Device-tree compatible strings in `qnoc_of_match` select the descriptor for each NoC provider. Runtime path resolution and vote aggregation are performed by the generic interconnect framework and the Qualcomm RPMh helper code using the static node graph and BCM arrays.

## State And Persistence
The source owns no private mutable state. Its static topology persists for the driver lifetime; the dynamic provider state, aggregate bandwidth, and RPMh votes are managed by the common ICC/RPMh code. `icc_sync_state` is installed as the driver sync-state callback so initial votes are not synchronized away before all consumers have registered.

## Dependencies And Integration Points
Dependencies are the Linux platform-driver and interconnect-provider APIs, device-tree matching, `bcm-voter.h`, `icc-rpmh.h`, and the SC8280XP binding header. Integration points are DTS compatible strings such as `qcom,sc8280xp-aggre1-noc`, `qcom,sc8280xp-nspa-noc`, `qcom,sc8280xp-nspb-noc`, and `qcom,sc8280xp-system-noc`. Key consumers include PCIe controllers, USB3/USB4, UFS, SDCC, EMAC, QUP, IPA, LPASS, camera/display/video, GPU, CDSP/NSP blocks, GIC, LLCC, and external memory.

## Risks
SC8280XP has broad topology coverage, so the main risk is incorrect graph modeling: PCIe, USB aggregation, dual NSP, or LPASS paths can silently under-vote if linked to the wrong system or GEM node. The early `core_initcall` registration changes boot-order behavior; converting it casually to `module_platform_driver` could introduce probe-order regressions. Keepalive BCMs and memory/GEM votes are power critical. Binding ID mistakes can produce consumer failures or, worse, successful probes with inadequate bandwidth.

## Test Signals
Static validation includes build coverage and DT binding checks for all SC8280XP interconnect compatibles. Runtime smoke tests should confirm early provider registration, no consumer probe deferrals caused by missing interconnects, and no RPMh BCM vote errors. Functional stress should cover PCIe, USB4/USB3, storage, display, camera/video, GPU, LPASS/audio, CDSP/NSP workloads, and suspend/resume to catch both under-voting and keepalive/power regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sc8280xp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdm660.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdm660.c

## Purpose
Implements the Qualcomm SDM630/SDM636/SDM660 NoC QoS interconnect driver data for the older RPM-based interconnect framework. It describes A2NOC, BIMC, CNOC, GNOC, MNOC, and SNOC fabrics, including RPM master/slave IDs, QoS programming metadata, bus clock descriptors, interface clocks, and regmap bounds. Compared with the RPMh drivers in this group, this file uses `icc-rpm.h` and the legacy `qnoc_probe`/`qnoc_remove` path.

## Important APIs, Types, And Data
The file defines a local enum of SDM660 master and slave IDs, then maps Linux binding IDs from `dt-bindings/interconnect/qcom,sdm660.h` onto static `struct qcom_icc_node` objects. Nodes include fields not present in the newer RPMh-only tables: `.id`, `.mas_rpm_id`, `.slv_rpm_id`, `.qos.ap_owned`, `.qos.qos_mode`, `.qos.areq_prio`, `.qos.prio_level`, and `.qos.qos_port`. Links are represented by `const u16` ID arrays rather than direct node pointers.

Clock integration is explicit. `mm_intf_clocks` contains `iface`, while `a2noc_intf_clocks` lists `ipa`, `ufs_axi`, `aggre2_ufs_axi`, `aggre2_usb3_axi`, and `cfg_noc_usb2_axi`. Descriptors reference bus clock descriptors such as `aggre2_clk`, `bimc_clk`, `bus_2_clk`, `mmaxi_0_clk`, and `bus_1_clk`, which are provided by the common RPM interconnect support.

The provider descriptors are `sdm660_a2noc`, `sdm660_bimc`, `sdm660_cnoc`, `sdm660_gnoc`, `sdm660_mnoc`, and `sdm660_snoc`. Each has a `type` such as `QCOM_ICC_NOC` or `QCOM_ICC_BIMC`, a node array, and a `regmap_cfg`; BIMC and MNOC set `ab_coeff = 153`.

## Control Flow
The platform driver `qnoc-sdm660` is registered with `module_platform_driver`. Device-tree compatible strings in `sdm660_noc_of_match` select a descriptor for each fabric. Probe goes through `qnoc_probe`, which is the legacy RPM interconnect provider setup path; remove goes through `qnoc_remove`.

Runtime bandwidth requests use the interconnect framework to traverse node links by numeric IDs. The Qualcomm RPM provider aggregates average and peak bandwidth, manages bus and interface clocks, programs NoC/BIMC QoS registers through the regmap configuration where applicable, and sends RPM votes using the node RPM IDs. QoS modes distinguish fixed, bypass, and invalid/no QoS programming for different masters and slaves.

## State And Persistence
Static node tables, link arrays, clock lists, and descriptors are compile-time data. Dynamic provider state, clock handles, regmaps, QoS programming, and RPM vote state are owned by common `icc-rpm` code after probe. Hardware state persists as RPM votes, enabled clocks during operations, and NoC/BIMC QoS register values. This source does not implement a sync-state callback.

## Dependencies And Integration Points
Dependencies include device, interconnect-provider, I/O, regmap, slab, module, platform-device, and device-tree APIs; the legacy Qualcomm `icc-rpm.h`; and SDM660 DT bindings. Integration with DTS occurs through `qcom,sdm660-a2noc`, `qcom,sdm660-bimc`, `qcom,sdm660-cnoc`, `qcom,sdm660-gnoc`, `qcom,sdm660-mnoc`, and `qcom,sdm660-snoc`. Consumer integration spans IPA, SDCC, BLSP/QUP, UFS, USB, crypto, GPU, camera, display, video, QDSS, apps CPU, memory/BIMC, PIMEM/IMEM, WLAN, LPASS, and CDSP.

## Risks
Legacy RPM IDs and QoS port numbers are high-risk constants: incorrect `mas_rpm_id`, `slv_rpm_id`, or `qos_port` values can vote the wrong RPM resource or program the wrong hardware port. Clock lists must match DTS and hardware requirements or QoS programming and bus access can fail. `ab_coeff` affects bandwidth scaling for BIMC and MNOC, so changing it can distort votes. Because links are numeric IDs, a mismatched enum or binding index can produce path errors that are harder to inspect than direct pointers.

## Test Signals
Build with the SDM660 interconnect driver and run device-tree binding checks against SDM630/636/660 board files. Runtime signals include successful probe for all six NoC providers, clock acquisition for bus and interface clocks, valid regmap access within declared `max_register` ranges, and no RPM vote failures. Functional stress should cover storage, USB, display/camera/video, GPU, CPU-memory, IPA/networking, and suspend/resume. Debugfs ICC path inspection can confirm that numeric links resolve to expected fabrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdm660.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdm670.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdm670.c

## Purpose
Defines Qualcomm SDM670 RPMh interconnect topology data. It covers aggregation NoCs, config NoC, display/config NoC, Gladiator/GNOC, memory NoC, multimedia NoC, and system NoC. SDM670 sits between the older SDM660 RPM style and later SC-series RPMh style; this file uses RPMh BCM voting while modeling fabrics that still resemble the SDM660-era split between aggregation, memory, multimedia, and system domains.

## Important APIs, Types, And Data
The file defines static `struct qcom_icc_node` objects with names such as `qhm_a1noc_cfg`, `xm_ufs_mem`, `qnm_memnoc`, `qxm_gpu`, `qxm_camnoc_*`, `qhs_*` config slaves, `qns_*` NoC slaves, and `ebi`. Nodes carry channel count, bus width, and `link_nodes`; arrays are indexed by binding IDs from `dt-bindings/interconnect/qcom,sdm670-rpmh.h`.

`struct qcom_icc_bcm` objects group nodes into RPMh BCM votes. Important groups include memory `bcm_acv`, `bcm_mc0`, and shared `bcm_sh*`; multimedia `bcm_mm0` through `bcm_mm3`; crypto `bcm_ce0`; config `bcm_cn0`; QUP `bcm_qup0`; and system `bcm_sn*` buckets. Many groups explicitly set `keepalive = false`; essential memory/config groups such as `bcm_mc0`, `bcm_sh0`, `bcm_mm0`, `bcm_mm1`, `bcm_cn0`, and `bcm_sn0` keep selected paths alive.

Provider descriptors are `sdm670_aggre1_noc`, `sdm670_aggre2_noc`, `sdm670_config_noc`, `sdm670_dc_noc`, `sdm670_gladiator_noc`, `sdm670_mem_noc`, `sdm670_mmss_noc`, and `sdm670_system_noc`. The memory NoC descriptor notably includes both LLCC-to-EBI and other memory/system masters in one node array, while the system NoC descriptor also includes camera uncompressed virtual paths.

## Control Flow
The `qnoc-sdm670` platform driver is registered through `module_platform_driver`. Device-tree compatible strings in `qnoc_of_match` map each provider node to its descriptor. Probe and remove are delegated to `qcom_icc_rpmh_probe` and `qcom_icc_rpmh_remove`; `icc_sync_state` is used for provider synchronization after consumers register.

Bandwidth requests from peripheral drivers resolve binding IDs into the relevant descriptor's node array. The interconnect framework traverses `link_nodes`, aggregates requested bandwidth, and the Qualcomm RPMh provider turns the resulting aggregate into BCM votes. Because QUP masters from both aggregation NoCs are grouped in `bcm_qup0`, QUP-related bandwidth can affect both A1NOC and A2NOC voting.

## State And Persistence
The source itself only provides static data. Common RPMh interconnect code owns provider allocation, aggregate bandwidth state, and RPMh vote transactions after probe. Hardware-visible persistent state consists of active BCM votes and any related NoC state maintained by RPMh firmware. There are no file-local mutable globals beyond static descriptors and tables.

## Dependencies And Integration Points
Dependencies are Linux interconnect provider and platform-driver infrastructure, device-tree matching, Qualcomm `bcm-voter.h` and `icc-rpmh.h`, and the SDM670 RPMh binding header. DTS integration is through compatibles such as `qcom,sdm670-aggre1-noc`, `qcom,sdm670-mem-noc`, `qcom,sdm670-mmss-noc`, and `qcom,sdm670-system-noc`. Consumers include BLSP/QUP, TSIF, eMMC/SDCC/UFS, USB3, crypto, IPA, camera, display, video, GPU, CPU/memory, GNOC, GIC, PIMEM/IMEM, and debug trace.

## Risks
The main risks are static topology and BCM membership errors. SDM670's memory and system descriptors mix many high-impact paths; wrong placement can create under-voting that only appears under multimedia or memory pressure. The explicit keepalive settings must match hardware expectations, or idle and resume behavior can regress. The system NoC descriptor contains camera uncompressed nodes, so camera paths depend on system-NoC votes as well as multimedia votes. Binding header changes must stay synchronized with array indices.

## Test Signals
Compile-test with SDM670 interconnect support and validate DTS compatible strings and interconnect specifiers. Runtime smoke tests should show all eight providers probing, consumers acquiring interconnect paths, and no RPMh vote failures. Workload tests should exercise UFS/eMMC/SDCC, USB3, IPA/network, camera/display/video, GPU, and CPU-memory traffic, plus idle and suspend/resume to catch keepalive and vote teardown issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdm670.c -->
