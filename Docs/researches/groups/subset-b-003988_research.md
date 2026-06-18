# subset-b-003988 research

Grouped research for Qualcomm interconnect driver sources. Each section is delimited for reconciliation into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdm845.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdm845.c

Purpose: defines the Qualcomm SDM845 Network-on-Chip interconnect topology for the Linux interconnect framework. It is an RPMh/BCM-voter driver: most of the file is declarative data describing masters, slaves, bus widths, channels, topology links, BCM groups, and per-NoC provider descriptors. The platform driver binds device-tree compatibles such as `qcom,sdm845-aggre1-noc`, `qcom,sdm845-mem-noc`, and `qcom,sdm845-system-noc` to those descriptors.

Important APIs/types/functions: the central types are `struct qcom_icc_node`, `struct qcom_icc_bcm`, `struct qcom_icc_desc`, `struct of_device_id`, and `struct platform_driver`. There are about 130 node definitions, 28 BCM definitions, and 8 descriptors. `qcom_icc_node` entries encode node name, channel count, bus width, and `link_nodes`; `qcom_icc_bcm` entries group one or more nodes under RPMh BCM names such as `MC0`, `SH*`, `MM*`, `CN0`, `QUP0`, and `SN*`; `qcom_icc_desc` arrays publish the node and BCM sets per provider. The only executable integration in this file is `module_platform_driver(qnoc_driver)`, whose `.probe` is `qcom_icc_rpmh_probe`, `.remove` is `qcom_icc_rpmh_remove`, and `.driver.sync_state` is `icc_sync_state`.

Control flow: device-tree matching selects a descriptor from `qnoc_of_match`. The shared RPMh probe allocates/registers an interconnect provider from the descriptor, creates framework nodes from the indexed node arrays, resolves static links through the `link_nodes` pointers, and wires bandwidth votes through the BCM voter layer. Runtime bandwidth requests are handled outside this file by the common Qualcomm interconnect code using this topology data. Removal unwinds the provider through the common RPMh remove path.

State and persistence behavior: all topology state is static read-only driver data after initialization. No persistent state is written by this file. Runtime interconnect votes live in the common provider, interconnect core, and RPMh/BCM voter state created by `qcom_icc_rpmh_probe`. Several BCMs are marked `keepalive = true` for always-on paths such as memory-controller/shared paths, so boot and sync-state behavior depends on retaining minimum votes for those BCMs.

Dependencies and integration points: includes `dt-bindings/interconnect/qcom,sdm845.h` for stable master/slave IDs, `bcm-voter.h` for BCM voting, and `icc-rpmh.h` for the common RPMh interconnect implementation. It integrates with platform bus probing, OF matching, the Linux interconnect provider API, RPMh firmware resources, and device-tree consumers using SDM845 interconnect phandles.

Risks: the main risk is data correctness rather than algorithmic failure. A wrong array index, missing link, bad bus width/channel count, or incorrect BCM membership can under-vote or over-vote paths, causing memory, display, camera, storage, PCIe, USB, or debug bandwidth failures. Empty BCM arrays on DC/gladiator descriptors are intentional-looking but should be validated against hardware docs because they rely on nodes without local BCM groups. Since all links are pointer-based, forward declarations must remain consistent with definitions. Compatible strings and dt-binding IDs must stay synchronized with DTS and binding headers.

Test signals: build coverage should compile this file with `CONFIG_INTERCONNECT_QCOM_SDM845` and catch missing symbols or dt-binding drift. Runtime signals include successful provider registration for all eight compatibles, absence of probe deferrals caused by missing RPMh resources, `debugfs` interconnect topology visibility, and working bandwidth scaling under display/camera/video/storage/PCIe/USB stress. Device-tree schema checks should cover compatible names and expected provider cells.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdm845.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdx55.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdx55.c

Purpose: describes the Qualcomm SDX55 modem-platform interconnect topology for RPMh-managed NoCs. It exposes three providers: `qcom,sdx55-mc-virt`, `qcom,sdx55-mem-noc`, and `qcom,sdx55-system-noc`. The file is mostly static topology data for memory-controller, memory NoC, and system NoC paths used by modem, IPA, PCIe, USB, storage, Ethernet, QDSS, and configuration targets.

Important APIs/types/functions: uses `struct qcom_icc_node` for about 58 nodes, `struct qcom_icc_bcm` for about 20 BCMs, and three `struct qcom_icc_desc` descriptors. Nodes specify names, channels, bus widths, and pointer links. BCMs include keepalive memory/shared paths (`MC0`, `SH0`, `SN0`) plus peripheral/system BCM groups (`PN*`, `SN*`, `CE0`). The platform driver is named `qnoc-sdx55`, uses `qcom_icc_rpmh_probe`/`qcom_icc_rpmh_remove`, exports `MODULE_DEVICE_TABLE(of, qnoc_of_match)`, and uses `icc_sync_state`.

Control flow: the platform bus matches one of the three SDX55 compatibles, passes the selected descriptor to the common RPMh probe, and the common code registers the provider and node graph with the interconnect core. Bandwidth requests from consumers then traverse the graph and vote on the BCM groups declared here. `module_platform_driver` supplies normal module init/exit handling.

State and persistence behavior: the file has no mutable local runtime state and no persistence. Static node and BCM arrays are the authoritative topology. Runtime state is created in common RPMh interconnect code and in RPMh firmware votes. Keepalive BCMs keep memory paths available even before or after consumer votes converge.

Dependencies and integration points: includes `dt-bindings/interconnect/qcom,sdx55.h`, `bcm-voter.h`, and `icc-rpmh.h`. It integrates with SDX55 device trees, the Linux interconnect framework, RPMh BCM voting, and subsystem drivers that request paths for PCIe, IPA, USB3, SDCC, QPIC, BLSP, QDSS, EMAC, and memory access.

Risks: topology errors can be hard to diagnose because this driver contains no active policy beyond data. SDX55 has broad system NoC fan-out from nodes like `qhm_qdss_bam`, `qnm_aggre_noc`, and `qnm_ipa`; missing a target can break apparently unrelated debug or modem data paths. The `bcm_sn7` definition contains repeated `xm_emac` membership, which may be deliberate hardware modeling or a copy/paste-sensitive area to validate. Binding ID mismatches against `qcom,sdx55.h` or DTS consumers will cause wrong node lookup.

Test signals: compile with the SDX55 interconnect driver enabled, check OF modalias generation, and boot an SDX55 board or DT with all three providers registered. Runtime tests should exercise IPA, PCIe, USB3, SDCC, QDSS trace, and memory bandwidth requests while watching RPMh vote/debugfs state. Schema validation should confirm the three compatible strings and consumer phandle IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdx55.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdx65.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdx65.c

Purpose: provides static RPMh interconnect topology for Qualcomm SDX65. It is very close in shape to SDX55 but updates widths, node sets, BCM grouping, and dt-binding names for SDX65 hardware. The providers are `qcom,sdx65-mc-virt`, `qcom,sdx65-mem-noc`, and `qcom,sdx65-system-noc`.

Important APIs/types/functions: defines about 55 `qcom_icc_node` objects, 20 `qcom_icc_bcm` groups, and three `qcom_icc_desc` descriptors. Important nodes include memory paths (`llcc_mc`, `ebi`, `qns_llcc`), system NoC aggregators (`qnm_aggre_noc`, `qnm_snoc_gc`), and peripheral/config targets for IPA, PCIe, QDSS, SDCC, USB3, BLSP, QPIC, AOSS, DDRSS, and MSS. The driver uses the common `qcom_icc_rpmh_probe` and `qcom_icc_rpmh_remove` functions with `icc_sync_state`.

Control flow: OF match data selects a descriptor, the common RPMh probe consumes that descriptor, and interconnect consumers request paths by dt-binding IDs. The node graph links masters to intermediate slaves and final targets; BCM arrays determine which RPMh resources receive aggregated votes. Module load and unload are handled by `module_platform_driver`.

State and persistence behavior: local data is static; no file-local locks, allocations, or persistence exist. Runtime bandwidth aggregation and BCM vote state are maintained by the shared Qualcomm RPMh interconnect layer. Keepalive BCMs (`MC0`, `PN0`, `SH0`, `SN0`) preserve essential memory/system paths.

Dependencies and integration points: includes `dt-bindings/interconnect/qcom,sdx65.h`, `bcm-voter.h`, and `icc-rpmh.h`. The file depends on device-tree providers matching its three compatible strings and on subsystem consumers using the same master/slave IDs. It integrates with RPMh firmware and the interconnect core rather than touching hardware registers directly.

Risks: most bugs would be incorrect hardware modeling. SDX65 changes relative to SDX55 include narrower/wider bus widths in several memory/system links and a large `PN0` BCM that keeps many config/system nodes alive; errors there can affect idle power or boot stability. Missing links in high-fanout nodes such as `qnm_aggre_noc`, `qnm_ipa`, or `qnm_memnoc` can strand consumers. Because there is no procedural validation, array indices must match the dt-binding enum exactly.

Test signals: compile coverage catches symbol and binding drift. Runtime validation should confirm all three providers probe, interconnect debugfs shows expected nodes and links, and bandwidth votes change under IPA, PCIe, USB3, SDCC, QDSS, and memory stress. Device-tree schema checks should verify compatible strings and provider references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdx65.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdx75.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdx75.c

Purpose: defines Qualcomm SDX75 interconnect providers for a newer RPMh modem platform. It models six providers: clock virtual, DC NoC, GEM NoC, memory-controller virtual, PCIe aggregation NoC, and system NoC. Compared with SDX55/SDX65, the topology adds GEM NoC, multiple PCIe controllers, Ethernet blocks, MVMSS, and a QUP core clock path.

Important APIs/types/functions: uses about 85 `qcom_icc_node` objects, 10 `qcom_icc_bcm` groups, and six `qcom_icc_desc` descriptors. It includes `icc-common.h` in addition to `bcm-voter.h` and `icc-rpmh.h`, reflecting shared descriptor/node helpers. Important BCMs include `CN0` for a large keepalive config/system group, `MC0`, `QUP0`, `SH0`, `SH1`, and `SN*` groups for system, GEM, PCIe, and memory paths. The driver registers as `qnoc-sdx75` using `qcom_icc_rpmh_probe`, `qcom_icc_rpmh_remove`, and `icc_sync_state`.

Control flow: during core init, `qnoc_driver_init` registers the platform driver via `core_initcall`, making these providers available early. OF matching selects descriptors for `qcom,sdx75-clk-virt`, `qcom,sdx75-dc-noc`, `qcom,sdx75-gem-noc`, `qcom,sdx75-mc-virt`, `qcom,sdx75-pcie-anoc`, and `qcom,sdx75-system-noc`. The common RPMh probe registers nodes and BCM voters. Consumer bandwidth requests later flow through this static graph to RPMh BCM votes.

State and persistence behavior: the file has no local mutable state. The static descriptors are retained for the module lifetime. Keepalive BCMs preserve critical config, memory, and QUP-clock paths. Runtime vote state is external to this file in the interconnect provider and RPMh layers.

Dependencies and integration points: depends on `dt-bindings/interconnect/qcom,sdx75.h`, platform bus OF matching, RPMh BCM voter support, and interconnect consumers for PCIe, Ethernet, IPA, USB, QDSS, SDCC, QUP, GEM/memory, and modem/multimedia subsystems. `core_initcall` is an integration choice: this driver must be ready before later consumers need interconnect paths.

Risks: the large `CN0` keepalive group and multi-PCIe topology are high-risk data areas because incorrect membership can produce either excess always-on votes or missing config access. Descriptor coverage must match DTS provider nodes exactly; a missing provider breaks all consumers for that NoC. Since the DC NoC descriptor has nodes but no BCM list, its behavior relies on common code handling descriptors without BCMs. Multiple PCIe endpoint nodes (`xs_pcie_0/1/2`) and PCIe config paths create room for swapped IDs.

Test signals: build with SDX75 enabled and boot with all six compatible providers. Confirm early registration order does not race consumers, and inspect interconnect debugfs for PCIe/GEM/system paths. Exercise PCIe0/1/2, Ethernet, IPA, USB3, SDCC, QDSS, and QUP activity while checking RPMh votes and absence of probe deferrals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sdx75.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm6115.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm6115.c

Purpose: implements the Qualcomm SM6115 interconnect topology using the older RPM/regmap Qualcomm interconnect path rather than the RPMh BCM-voter path used by most other files in this group. It describes BIMC, CNOC, SNOC, QUP clock virtual, multimedia non-real-time virtual, and multimedia real-time virtual providers.

Important APIs/types/functions: includes `icc-rpm.h` and `linux/regmap.h`, not `bcm-voter.h`. It defines about 89 `qcom_icc_node` objects, six `qcom_icc_desc` descriptors, three `regmap_config` blocks, clock-name arrays (`snoc_intf_clocks`, `cnoc_intf_clocks`), and an internal enum for SM6115 node IDs. Nodes carry RPM-specific fields such as `.id`, `.mas_rpm_id`, `.slv_rpm_id`, `.links`, and optional `.qos` settings. Descriptors set fields such as `.type = QCOM_ICC_BIMC` or `QCOM_ICC_QNOC`, `.regmap_cfg`, `.bus_clk_desc`, `.intf_clocks`, `.keep_alive`, `.qos_offset`, and `.ab_coeff`. The platform driver uses `qnoc_probe` and `qnoc_remove`.

Control flow: `core_initcall(qnoc_driver_init)` registers `qnoc-sm6115` early. OF match data maps `qcom,sm6115-bimc`, `qcom,sm6115-clk-virt`, `qcom,sm6115-cnoc`, `qcom,sm6115-mmrt-virt`, `qcom,sm6115-mmnrt-virt`, and `qcom,sm6115-snoc` to descriptors. The common RPM interconnect probe maps registers with regmap, prepares listed interface/bus clocks, creates provider nodes from ID/link arrays, programs QoS where specified, and sends bandwidth requests through the RPM path.

State and persistence behavior: static topology, QoS, clock, and regmap configuration is immutable. Runtime state lives in the common RPM interconnect provider, regmap-backed hardware programming, clock framework, and RPM vote aggregation. The descriptors use `.keep_alive = true` for these providers, so paths may retain minimum votes/clocks to keep fabric access safe.

Dependencies and integration points: depends on `dt-bindings/interconnect/qcom,sm6115.h`, `icc-rpm.h`, platform OF matching, regmap, bus clock descriptors from the shared Qualcomm interconnect code, and named clocks in device tree. It integrates with BIMC/QNOC hardware registers directly through common code and with consumers for GPU, camera, display, video, IPA, USB3, SDCC, QDSS, QUP, PIMEM/OCIMEM, and CPU/memory paths.

Risks: SM6115 has more procedural coupling than RPMh-only files. Incorrect `regmap_config.max_register`, `.qos_offset`, `.ab_coeff`, QoS mode/port, RPM master/slave ID, or clock list can break bandwidth programming or cause probe failures. Link arrays use numeric enum IDs rather than pointer links, so enum order and dt-binding values must remain synchronized. Missing clocks, especially `ipa` in `snoc_intf_clocks`, can surface as probe deferral or runtime access failures.

Test signals: compile with the SM6115 interconnect driver and boot with all six providers. Check probe logs for clock/regmap failures, validate debugfs node graphs, and run memory, display, camera/video, USB, SDCC, IPA, and GPU workloads. Device-tree schema checks should validate compatible strings, clocks, reg ranges, and interconnect consumer IDs. Runtime power tests should watch that keepalive and QoS settings do not create unexpected idle drain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm6115.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm6350.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm6350.c

Purpose: defines RPMh interconnect topology for Qualcomm SM6350. It models a broad application-processor SoC fabric with aggregation NoCs, clock virtual nodes, compute/NPU paths, config/DC/GEM/MMSS/system NoCs, and a separate NPU NoC descriptor.

Important APIs/types/functions: uses about 127 `qcom_icc_node` objects, 25 `qcom_icc_bcm` groups, 10 `qcom_icc_desc` descriptors, 28 `qcom_icc_qosbox` definitions, and seven `regmap_config` blocks. Unlike simpler RPMh files, several descriptors provide `.config` regmap data and some set `.qos_requires_clocks = true`, so common RPMh code can program QoS boxes with clock requirements. Provider descriptors cover `aggre1_noc`, `aggre2_noc`, `clk_virt`, `compute_noc`, `config_noc`, `dc_noc`, `gem_noc`, `mmss_noc`, `npu_noc`, and `system_noc`. The driver uses `qcom_icc_rpmh_probe`/`remove` and `icc_sync_state`.

Control flow: OF matching maps ten `qcom,sm6350-*` compatibles to descriptors. The common RPMh probe registers the selected node graph, configures BCM voters, and, for descriptors with regmap config and QoS boxes, has enough metadata to program NoC QoS settings. Interconnect consumers request bandwidth through dt-binding IDs; requests aggregate to BCM votes and QoS/register behavior in the common layer.

State and persistence behavior: the file itself is static data. Runtime state is in the interconnect core, RPMh BCM voter, and optional QoS/regmap programming owned by shared code. Keepalive flags on BCMs preserve essential memory/control paths. QoS box definitions are persistent hardware policy inputs but are not mutated locally after registration.

Dependencies and integration points: depends on `dt-bindings/interconnect/qcom,sm6350.h`, `bcm-voter.h`, `icc-rpmh.h`, the platform bus, RPMh resources, and NoC QoS register access. It integrates with storage, USB, IPA, camera, display, video, GPU, NPU/CDSP, QDSS, QUP, GEM/memory, and config consumers.

Risks: this file has both topology and QoS metadata, increasing the risk of subtle performance/power bugs. Incorrect QoS port offsets or priorities can harm latency-sensitive masters even if bandwidth voting works. `qos_requires_clocks` means clock availability/order matters for aggre NoC QoS programming. Descriptor/provider mismatch can break entire subsystems such as NPU or MMSS. Empty BCM-free descriptors like `npu_noc` depend on common code accepting node-only providers.

Test signals: compile with SM6350 support, run DT schema validation for all ten compatibles, and boot hardware with every provider registered. Runtime validation should exercise NPU/CDSP, camera/video/display, GPU, USB, UFS/eMMC, SDCC, IPA, QUP, and QDSS while checking interconnect debugfs, RPMh votes, QoS programming logs, and suspend/resume stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm6350.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm7150.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm7150.c

Purpose: provides the Qualcomm SM7150 RPMh interconnect topology. It covers application, multimedia, compute, memory, and system fabrics through ten providers: aggre1, aggre2, camnoc virtual, compute, config, DC, GEM, memory-controller virtual, MMSS, and system NoC.

Important APIs/types/functions: defines about 127 nodes, 24 BCMs, and 10 descriptors using `qcom_icc_node`, `qcom_icc_bcm`, and `qcom_icc_desc`. It includes `dt-bindings/interconnect/qcom,sm7150-rpmh.h`, `bcm-voter.h`, and `icc-rpmh.h`. Major BCM groups include config (`CN0`), QUP (`QUP0`), multimedia (`MM*`), shared/memory (`SH*`, `MC0`, `ACV`), compute (`CO*`), and system (`SN*`). The driver is registered with explicit `core_initcall`/`module_exit`, uses `qcom_icc_rpmh_probe` and `qcom_icc_rpmh_remove`, and sets `icc_sync_state`.

Control flow: early platform-driver registration allows consumers to find providers during boot. Device-tree compatible matching selects the descriptor, the common RPMh layer registers the graph and BCMs, and bandwidth requests from interconnect consumers are resolved through static pointer links and BCM memberships. The file contains no custom request handling.

State and persistence behavior: local state is immutable topology data. Runtime interconnect state and RPMh votes are external. BCM keepalive settings preserve selected critical memory/control paths. Since this file has no regmap/QoS-box metadata, QoS behavior is represented indirectly by BCM and node topology rather than local register programming.

Dependencies and integration points: integrates with SM7150 DTS provider nodes and consumers, the Linux interconnect framework, RPMh BCM voting, and subsystems such as UFS/eMMC/SDCC, PCIe, USB, IPA, camera, display, video, NPU/CDSP, GPU, QUP, QDSS, and memory/GEM fabric.

Risks: SM7150’s topology is dense and strongly order-dependent through dt-binding enum indices. Swapped `A1NOC`/`A2NOC`, GEM, MMSS, or CAMNOC virtual links can manifest as subsystem-specific bandwidth failures. The camnoc virtual descriptor models uncompressed camera paths through BCM `MM1`; wrong membership can harm camera throughput or power. Early registration via `core_initcall` should be retained if consumers depend on it before normal module init.

Test signals: build coverage, DT schema validation for all ten compatibles, boot logs showing provider registration, and interconnect debugfs graph inspection. Runtime tests should include camera capture, display/video playback, NPU/CDSP workloads, GPU, storage, USB, PCIe, IPA, QUP, QDSS, suspend/resume, and RPMh vote observation under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm7150.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8150.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8150.c

Purpose: defines the Qualcomm SM8150 RPMh interconnect topology. It is a high-end SoC fabric driver covering aggregation NoCs, camera virtual paths, compute/NPU, config/DC/GEM/memory/MMSS/system NoCs, and a memory-controller virtual provider.

Important APIs/types/functions: uses about 138 nodes, 28 BCMs, and 10 `qcom_icc_desc` descriptors. It includes `dt-bindings/interconnect/qcom,sm8150.h`, `bcm-voter.h`, and `icc-rpmh.h`. Descriptors map the compatibles `qcom,sm8150-aggre1-noc`, `aggre2-noc`, `camnoc-virt`, `compute-noc`, `config-noc`, `dc-noc`, `gem-noc`, `mc-virt`, `mmss-noc`, and `system-noc`. The driver uses `module_platform_driver(qnoc_driver)`, `qcom_icc_rpmh_probe`, and `qcom_icc_rpmh_remove`; unlike several peers, the displayed driver struct does not set `.sync_state`.

Control flow: module/platform-driver registration installs `qnoc-sm8150`. OF match data provides the descriptor for each provider node. The common RPMh probe registers nodes and BCMs with the interconnect core. Consumers request master/slave paths using binding IDs, and common code aggregates those requests into RPMh BCM votes according to the static graph and BCM membership.

State and persistence behavior: no local mutable or persistent state exists. Static topology remains for the driver lifetime. Runtime bandwidth votes and provider state are held by common interconnect/RPMh code. Keepalive BCMs preserve selected critical paths, especially memory/shared fabric and config-related resources.

Dependencies and integration points: depends on SM8150 dt-bindings, platform OF matching, Linux interconnect provider APIs, RPMh BCM voter support, and DTS consumers. It integrates with application CPU/GPU/memory paths, PCIe, USB, UFS, SDCC, EMAC, IPA, camera, display, video, NPU/CDSP, QUP/QSPI, QDSS, and config/peripheral targets.

Risks: the large topology has many subsystem-specific failure modes if a node index, link, BCM, or compatible string is wrong. SM8150 includes dual PCIe, EMAC, camera uncompressed paths, compute/NPU, ECC, and multiple QUP blocks, so copy/paste errors can be localized and hard to spot. The absence of `.sync_state = icc_sync_state` compared with nearby RPMh drivers is a notable integration difference to validate against the expected kernel version and boot behavior. Incorrect BCM keepalive settings can affect power or boot stability.

Test signals: compile with SM8150 interconnect support, validate DTS compatibles and dt-binding IDs, boot hardware with all ten providers, and inspect interconnect debugfs. Runtime signals include successful storage, PCIe, USB, EMAC, IPA, camera/display/video, NPU/CDSP, GPU, QDSS, and suspend/resume tests while observing RPMh votes and checking for bandwidth-related timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8150.c -->
