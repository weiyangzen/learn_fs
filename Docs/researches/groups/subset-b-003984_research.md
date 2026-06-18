# subset-b-003984 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-rpmh.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-rpmh.c

Purpose: shared Qualcomm RPMh interconnect provider implementation. It turns SoC-specific `qcom_icc_desc` topology tables into Linux interconnect providers, aggregates ICC bandwidth requests into per-BCM bucket state, commits RPMh BCM votes, initializes BCM metadata from command DB, and optionally programs static NoC QoS registers.

Important APIs/types/functions: exported entry points are `qcom_icc_pre_aggregate()`, `qcom_icc_aggregate()`, `qcom_icc_set()`, `qcom_icc_bcm_init()`, `qcom_icc_rpmh_probe()`, and `qcom_icc_rpmh_remove()`. Internal helpers include `qcom_icc_set_qos()` and `qcom_icc_rpmh_configure_qos()`. The code operates on `struct qcom_icc_provider`, `struct qcom_icc_node`, `struct qcom_icc_bcm`, `struct icc_provider`, `struct icc_node`, and command-DB `struct bcm_db` data.

Control flow: probe gets the matched descriptor, allocates the provider and `icc_onecell_data`, installs ICC callbacks, obtains the BCM voter, initializes every BCM through command DB, creates or reuses each qnode's `icc_node`, names it, adds it to the provider, links it to target nodes, and stores it in onecell data. If the descriptor carries a regmap config, probe obtains a parent regmap or maps local MMIO, optionally gets QoS clocks, programs all `qosbox` entries, then registers the provider and populates child devices. Bandwidth updates call pre-aggregate to clear per-node bucket sums and queue BCMs, aggregate to update tagged buckets, and set to commit the voter.

State and persistence: state is runtime-only and per provider. Static SoC qnodes retain their `icc_node` pointer across probe. Per-node `sum_avg` and `max_peak` arrays are reset before each aggregate pass. BCMs cache command-DB addresses, aux data, list heads, scaling, linked nodes, dirty state, and wake/sleep list membership for the BCM voter.

Dependencies/integration: integrates Linux ICC core, OF platform matching/population, regmap/MMIO, bulk clocks, Qualcomm command DB, `bcm-voter`, and `icc-common` extended xlate support. SoC-specific RPMh topology files supply descriptors consumed here.

Risks and test signals: `qcom_icc_rpmh_probe()` ignores `qcom_icc_bcm_init()` return values, so missing command-DB entries can leave later vote behavior dependent on partially initialized BCMs. QoS programming is best-effort for most failures, except clock probe defer. Test probe/unwind with missing command DB, invalid aux data, parent versus local regmap, missing clocks with and without `qos_requires_clocks`, child NoC population failure, repeated aggregate/set cycles, multi-bucket tags, `init_avg/init_peak`, and remove ordering after provider registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-rpmh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-rpmh.h -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-rpmh.h

Purpose: shared data-model and API header for Qualcomm RPMh interconnect providers. It defines provider, node, BCM, QoS, fabric, and descriptor structures used by RPMh NoC topology files and declares the common probe, remove, aggregation, set, and BCM initialization functions implemented in `icc-rpmh.c`.

Important APIs/types/functions: `to_qcom_provider()` converts an ICC provider to `struct qcom_icc_provider`. `struct qcom_icc_provider` stores the generic provider, device, BCM array, BCM voter, node array, optional QoS regmap, and QoS clocks. `struct bcm_db` mirrors command-DB auxiliary BCM data. `struct qcom_icc_qosbox` describes static QoS register programming. `struct qcom_icc_node` stores name, dynamic `icc_node`, bandwidth buckets, BCM backpointers, bus geometry, QoS pointer, and flexible link-node array. `struct qcom_icc_bcm` stores RPMh vote state and command-DB metadata. `struct qcom_icc_desc` is the per-compatible descriptor consumed by probe.

Control flow: SoC files instantiate static qnodes and BCMs with this schema, arrange them in descriptor arrays, and bind descriptors to OF compatible strings. `qcom_icc_rpmh_probe()` then uses these fields to create ICC nodes, link graph edges, initialize BCMs, configure QoS, and register providers. Runtime ICC callbacks mutate only the bucket arrays and BCM vote state declared here.

State and persistence: the structures are mostly static topology plus per-probe runtime pointers and counters. `MAX_BCM_PER_NODE` bounds how many BCMs can be attached by `qcom_icc_bcm_init()`. `MAX_PORTS`, `MAX_LINKS`, `MAX_BCMS`, and `MAX_VCD` document sizing assumptions used by the implementation and topology tables.

Dependencies/integration: includes Qualcomm interconnect DT bindings and regmap declarations, while relying on types from ICC core, device, clock, list, and BCM voter headers included by users. It is the contract between chip-specific RPMh files and the shared RPMh backend.

Risks and test signals: topology files must keep `num_links`, flexible `link_nodes`, BCM `num_nodes`, and descriptor array indexes consistent with binding IDs. Overflow of `bcms[MAX_BCM_PER_NODE]` is not guarded in the initializer. Compile all RPMh topology files after signature changes, and test malformed or high-fanout topology additions with static analysis or targeted assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-rpmh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/kaanapali.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/kaanapali.c

Purpose: SoC topology driver for Qualcomm Kaanapali RPMh NoC fabrics. It declares the interconnect nodes, BCM groups, fabric descriptors, regmap ranges, OF compatible table, and platform-driver glue required for the shared RPMh interconnect backend.

Important APIs/types/functions: the file is primarily static data: many `struct qcom_icc_node` objects for CNOC, GEM_NOC, LPASS, memory, multimedia, NSP, PCIe, and system NoC endpoints; `struct qcom_icc_bcm` objects such as `bcm_acv`, `bcm_ce0`, `bcm_cn0`, `bcm_mc0`, `bcm_mm0/mm1`, `bcm_qup*`, `bcm_sh*`, `bcm_sn*`, and `bcm_co0`; descriptor arrays for `kaanapali_aggre_noc`, `clk_virt`, `cnoc_cfg`, `cnoc_main`, `gem_noc`, LPASS fabrics, `mc_virt`, `mmss_noc`, `nsp_noc`, `pcie_anoc`, and `system_noc`; and `qnoc_driver` using `qcom_icc_rpmh_probe()`/`qcom_icc_rpmh_remove()`.

Control flow: module initialization registers the platform driver at `core_initcall`. OF compatible matching selects the right `qcom_icc_desc`, after which the shared RPMh probe creates ICC nodes, links the graph, initializes BCMs, optionally maps regmaps, programs QoS data, and registers the provider. Runtime bandwidth changes are handled entirely by the shared RPMh ICC callbacks and BCM voter.

State and persistence: static qnode and BCM objects persist for the module lifetime. Per-provider runtime state lives in `icc-rpmh.c`; this file contributes immutable topology, bus widths, channel counts, link relationships, BCM membership, vote scaling/keepalive flags, and QoS register offsets.

Dependencies/integration: depends on `dt-bindings/interconnect/qcom,kaanapali-rpmh.h` for binding IDs, the RPMh shared header, BCM voter, ICC core, OF platform, regmap, and module infrastructure. Compatible strings cover Kaanapali aggre, clock virtual, CNOC, GEM, LPASS, memory, multimedia, NSP, PCIe, and system fabrics.

Risks and test signals: most failures would be topology mismatches rather than algorithmic bugs. `aggre_noc` and `pcie_anoc` set `qos_requires_clocks`, so missing clocks prevent QoS programming. Validate every compatible probes, node indexes match the binding header, links resolve to initialized nodes, BCM command-DB names exist, QoS port offsets fit the regmap max register, child providers synchronize through `icc_sync_state`, and module unload unregisters after `core_initcall` registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/kaanapali.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/milos.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/milos.c

Purpose: SoC topology driver for Qualcomm Milos RPMh interconnect fabrics. It provides static node graph, QoS boxes, BCM mappings, fabric descriptors, OF match data, and platform-driver registration for the shared RPMh interconnect implementation.

Important APIs/types/functions: the data set includes forward-declared and initialized `struct qcom_icc_node` records for QUP, UFS, USB3, QDSS, crypto, IPA, SDCC, CNOC, GEM_NOC, GPU, LPASS, modem, multimedia, compute, PCIe, SNOC, memory, and service nodes. Many masters include `struct qcom_icc_qosbox` entries with per-port offsets and priority settings. Descriptors cover `milos_aggre1_noc`, `aggre2_noc`, `clk_virt`, `cnoc_cfg`, `cnoc_main`, `gem_noc`, `lpass_ag_noc`, `mc_virt`, `mmss_noc`, `nsp_noc`, `pcie_anoc`, and `system_noc`.

Control flow: `core_initcall(qnoc_driver_init)` registers `qnoc-milos`. Device-tree matching selects the descriptor for one Milos fabric, and `qcom_icc_rpmh_probe()` creates nodes, initializes BCMs, programs QoS through each descriptor's regmap, registers the provider, and populates child devices. The file itself has no runtime callbacks beyond platform-driver registration and unregister.

State and persistence: static topology nodes retain their dynamic `icc_node` pointers after probe. QoS boxes are static, usually one port each, and their values are written during probe if the corresponding descriptor has a config. BCMs hold runtime vote arrays after shared initialization; descriptors without BCM arrays act as graph-only or pass-through providers.

Dependencies/integration: integrates with `dt-bindings/interconnect/qcom,milos-rpmh.h`, `icc-rpmh.h`, `icc-common.h`, `bcm-voter`, ICC core, OF platform, regmap, and Linux module infrastructure. It uses `icc_sync_state` so consumers can be synchronized with provider readiness.

Risks and test signals: Milos has many QoS-equipped nodes, so offset drift versus hardware documentation is a primary risk. Test each compatible string, probe with and without parent regmap, QoS register writes for all qnodes with `qosbox`, BCM command-DB lookup for all BCM names, path votes across multi-hop links, PCIe dual-root paths, multimedia high-frequency and system-frequency paths, and cleanup after partial probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/milos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8909.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8909.c

Purpose: legacy RPM-based NoC topology driver for Qualcomm MSM8909. It describes BIMC, PCNOC, and SNOC interconnect graphs, RPM master/slave IDs, QoS settings, regmap geometry, clock descriptors, and OF match data for the shared `icc-rpm` backend.

Important APIs/types/functions: the file defines an internal enum of QNOC node IDs, many `struct qcom_icc_node` records for application, graphics, SNOC-BIMC bridges, TCU, audio, SPDM, QPIC, BLSP, USB HS, crypto, SDCC, QDSS, multimedia, PCNOC/SNOC internal nodes, memory, and peripheral slaves. Descriptors are `msm8909_bimc`, `msm8909_pcnoc`, and `msm8909_snoc`; they set `type`, node arrays, `bus_clk_desc`, `regmap_cfg`, `qos_offset`, and in BIMC `ab_coeff = 154`.

Control flow: `module_platform_driver(msm8909_noc_driver)` registers a platform driver using `qnoc_probe()` and `qnoc_remove()` from `icc-rpm`. OF compatible strings select one descriptor. The shared backend maps the register block, enables the bus clock described by `bimc_clk`, `bus_0_clk`, or `bus_1_clk`, registers ICC nodes, configures QoS from node fields, and sends RPM votes for paths with RPM IDs.

State and persistence: topology is static and module-lifetime. Runtime state is held by the common RPM provider. Nodes carry persistent metadata such as `mas_rpm_id`, `slv_rpm_id`, `buswidth`, link arrays, and `qos` fields. Some nodes set `ab_coeff = 167` locally, while descriptors apply aggregate scaling for BIMC.

Dependencies/integration: depends on `dt-bindings/interconnect/qcom,msm8909.h`, `icc-rpm.h`, regmap, platform-device matching, ICC core, and RPM clock/vote definitions in the common Qualcomm interconnect code.

Risks and test signals: risks are binding/index mismatches, stale downstream-derived RPM IDs, and QoS mode or port errors. Test all three compatibles, RPM vote emission for masters/slaves with valid IDs, AP-owned QoS paths, bypass/fixed/invalid QoS modes, BIMC `ab_coeff`, QDSS and multimedia paths through SNOC, PCNOC peripheral paths, and probe failure when clocks or regmap resources are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8909.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8916.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8916.c

Purpose: RPM-based interconnect topology driver for Qualcomm MSM8916. It declares the BIMC, PCNOC, and SNOC fabrics, their ICC node graph, QoS policy, bus clock descriptors, register layouts, and platform-driver match table.

Important APIs/types/functions: the file is static topology data plus driver glue. It defines MSM8916-specific internal node IDs; `qcom_icc_node` objects for BIMC/SNOC bridges, APSS, LPASS, BLSP, DEHR, graphics, JPEG, MDP, crypto, SDCC, QDSS, SPDM, TCU, USB, VFE, video, PCNOC internals, SNOC multimedia internals, and peripheral slaves; and descriptors `msm8916_snoc`, `msm8916_bimc`, and `msm8916_pcnoc`. The platform driver delegates to `qnoc_probe()` and `qnoc_remove()`.

Control flow: when a `qcom,msm8916-{bimc,pcnoc,snoc}` device probes, the common RPM backend consumes the descriptor, creates ICC nodes according to the descriptor's indexed node array, installs links from each node's `links` array, configures QoS at `qos_offset`, registers the provider, and later translates consumer bandwidth requests into RPM and NoC clock/QoS programming.

State and persistence: all node definitions are static. Runtime path state, aggregate bandwidth, and RPM voting state live in `icc-rpm`. Many nodes have `mas_rpm_id` and `slv_rpm_id` set to `-1`, so they participate as graph/intermediate nodes rather than direct RPM resources. QoS fields persist as AP-owned fixed, bypass, or invalid modes for setup-time programming.

Dependencies/integration: integrates with `dt-bindings/interconnect/qcom,msm8916.h`, `icc-rpm.h`, Linux ICC core, regmap, platform driver matching, and bus clock descriptors such as `bimc_clk`, `bus_0_clk`, and `bus_1_clk`.

Risks and test signals: MSM8916 lacks `icc_sync_state` in the driver struct unlike some newer topology files, which may be intentional but should be considered when comparing provider readiness behavior. Test every compatible, all array indexes against the DT binding, APSS/GPU to EBI paths, SNOC multimedia paths, peripheral PCNOC paths, invalid QoS nodes that should not be programmed as normal masters, and module unload/reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8916.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8937.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8937.c

Purpose: RPM-based Qualcomm MSM8937 NoC topology driver. It describes BIMC, PCNOC, SNOC, and SNOC multimedia fabrics, including node graph, RPM IDs, QoS policies, regmap ranges, bus clock descriptors, keepalive behavior, and OF match bindings.

Important APIs/types/functions: static data includes QNOC enum IDs and `qcom_icc_node` records for APSS, graphics, three SNOC-BIMC masters, TCU, SPDM, BLSP, USB HS and XI USB HS, crypto, SDCC, QDSS, BIMC-SNOC, JPEG, MDP, video, VFE0/VFE1, CPP, PCNOC internals, SNOC internals, memory, WCSS, LPASS, CATS/OCMEM, and peripheral slaves. Descriptors are `msm8937_bimc`, `msm8937_pcnoc`, `msm8937_snoc`, and `msm8937_snoc_mm`.

Control flow: platform probe is delegated to `qnoc_probe()`. The matched descriptor tells the common RPM backend which nodes to register, which bus clock to use, which regmap range and QoS offset to program, and whether special descriptor flags apply. `msm8937_pcnoc` requests `keep_alive = true`; BIMC and SNOC-MM set `ab_coeff = 154`.

State and persistence: this file holds static topology state. Runtime bandwidth aggregation and RPM transactions are common-code state. Node records persist RPM master/slave IDs, bus widths, links, and QoS mode/port data. SNOC-MM splits multimedia masters from the main SNOC descriptor while reusing the SNOC regmap configuration.

Dependencies/integration: depends on `dt-bindings/interconnect/qcom,msm8937.h`, `icc-rpm.h`, ICC core, regmap, platform matching, and shared Qualcomm RPM clocks/vote helpers. It uses `icc_sync_state` in the platform driver.

Risks and test signals: split SNOC and SNOC-MM descriptors must agree on shared register geometry without duplicate or conflicting node ownership. `keep_alive` on PCNOC should be validated against suspend/resume behavior. Test all four compatibles, paths through each SNOC-BIMC bridge, multimedia bandwidth to memory, WCSS/LPASS peripheral paths, USB HS variants, command IDs for RPM resources, QoS programming offsets, and provider sync-state interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8937.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8939.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8939.c

Purpose: RPM-based Qualcomm MSM8939 interconnect topology driver. It models BIMC, PCNOC, SNOC, and SNOC multimedia fabrics and binds them to the common `icc-rpm` provider through descriptors and OF compatible strings.

Important APIs/types/functions: key declarations are the MSM8939 enum ID list, static `qcom_icc_node` definitions for BIMC/SNOC bridge endpoints, APSS, LPASS, BLSP, DEHR, GPU, JPEG, dual MDP, CPP, crypto, SDCC, QDSS, SNOC config, SPDM, TCU, dual USB HS, VFE, video, PCNOC internals, SNOC internals, EBI, CATS/OCMEM, and peripheral slaves. Descriptors are `msm8939_snoc`, `msm8939_snoc_mm`, `msm8939_bimc`, and `msm8939_pcnoc`.

Control flow: `module_platform_driver()` registers `qnoc-msm8939`. Device-tree compatible matching selects a descriptor, then `qnoc_probe()` registers the relevant fabric with ICC core, maps registers using the descriptor regmap config, programs QoS from node metadata, and uses bus clock descriptors and RPM IDs for vote propagation.

State and persistence: static nodes persist for the module lifetime. Common RPM code owns runtime aggregate and vote state. MSM8939 differs from MSM8916 by wider BIMC bus widths, extra MDP/CPP/USB/SNOC-BIMC resources, and a separate SNOC-MM descriptor for multimedia masters and MM internal nodes.

Dependencies/integration: integrates with `dt-bindings/interconnect/qcom,msm8939.h`, `icc-rpm.h`, regmap, Linux ICC, platform driver matching, module metadata, and shared bus clock descriptors. The driver uses `icc_sync_state`.

Risks and test signals: the file was derived by reference to MSM8916, so copy-forward errors in IDs, bus widths, and QoS ports are the main risk. Test all four compatibles, APSS/GPU to EBI, dual MDP and CPP paths through SNOC-MM, USB HS1/HS2 peripheral paths, QDSS BAM/ETR graph reachability, SNOC-BIMC bridge choices, and matching between descriptor array indexes and the public binding IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8939.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8953.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8953.c

Purpose: RPM-based Qualcomm MSM8953 NoC topology driver. It supplies BIMC, PCNOC, SNOC, and SNOC-MM interconnect descriptions, including node graph, QoS settings, clock/interface-clock requirements, register ranges, and OF match data for the common Qualcomm RPM interconnect backend.

Important APIs/types/functions: the file defines MSM8953-specific node IDs; static `qcom_icc_node` objects for APSS, GPU, SNOC-BIMC bridges, TCU, EBI, SPDM, BLSP, USB3, crypto, SDCC, PCNOC/SNOC internals, QDSS, IPA, WCSS, LPASS, multimedia masters, CATS/OCMEM, and peripheral slaves; descriptors `msm8953_bimc`, `msm8953_pcnoc`, `msm8953_snoc`, and `msm8953_snoc_mm`; and an OF table for `qcom,msm8953-{bimc,pcnoc,snoc,snoc-mm}`.

Control flow: the platform driver delegates probe/remove to `qnoc_probe()` and `qnoc_remove()`. The common backend consumes descriptor data to register nodes, link them, manage bus clocks, map NoC registers, program QoS, and translate ICC bandwidth votes into RPM messages. PCNOC additionally names an interface clock, `pcnoc_usb3_axi`, so the USB3 path has extra clock integration.

State and persistence: topology objects are static. Runtime state is held by `icc-rpm`. MSM8953 uses `ab_coeff = 153` on BIMC and SNOC-MM descriptors, sets many QoS modes directly in node records, and uses a separate SNOC-MM fabric for multimedia-to-memory paths while sharing SNOC register configuration.

Dependencies/integration: depends on `dt-bindings/interconnect/qcom,msm8953.h`, `icc-rpm.h`, regmap, clock support, platform matching, ICC core, and Linux module infrastructure.

Risks and test signals: `msm8953_bimc` lacks a trailing comma after `regmap_cfg`, which is valid C but easy to disturb in later edits. The interface clock list means USB3-related probe and runtime paths need clock coverage beyond the bus clock. Test all four compatibles, `pcnoc_usb3_axi` availability and failure handling, APSS/GPU/multimedia/IPA paths, SNOC-MM `ab_coeff`, QoS port `-1` invalid cases, descriptor indexes versus binding IDs, and remove/reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8953.c -->
