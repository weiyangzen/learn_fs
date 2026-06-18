# subset-b-003986 research

This grouped report covers five Qualcomm RPMh interconnect topology drivers. Each section preserves the source path as its title and is wrapped with the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/qcs8300.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/qcs8300.c

## Purpose
`qcs8300.c` describes the Qualcomm QCS8300 network-on-chip interconnect topology for the Linux interconnect framework. It is a platform driver that exposes QCS8300 NoC fabrics to device-tree consumers so bandwidth requests can be translated into Qualcomm RPMh BCM votes and, for QoS-capable nodes, register programming through regmap-backed fabric blocks.

## Important APIs, Types, And Functions
The file is almost entirely static topology data built from `struct qcom_icc_node`, `struct qcom_icc_bcm`, `struct qcom_icc_desc`, `struct qcom_icc_qosbox`, `struct regmap_config`, and `struct of_device_id`. Node definitions carry names, channel counts, bus widths, optional QoS box metadata, and `link_nodes` edges. BCM definitions such as `bcm_acv`, `bcm_ce0`, `bcm_cn*`, `bcm_mm*`, `bcm_nsa*`, `bcm_qup*`, `bcm_sh*`, and `bcm_sn*` group nodes into voteable bandwidth clock managers. Descriptor objects expose the fabric slices: `qcs8300_aggre1_noc`, `qcs8300_aggre2_noc`, `qcs8300_clk_virt`, `qcs8300_config_noc`, `qcs8300_dc_noc`, `qcs8300_gem_noc`, `qcs8300_gpdsp_anoc`, `qcs8300_lpass_ag_noc`, `qcs8300_mc_virt`, `qcs8300_mmss_noc`, `qcs8300_nspa_noc`, `qcs8300_pcie_anoc`, and `qcs8300_system_noc`.

The only local functions are `qnoc_driver_init` and `qnoc_driver_exit`, which register and unregister the `platform_driver`. Probe and remove are delegated to `qcom_icc_rpmh_probe` and `qcom_icc_rpmh_remove`; provider synchronization is delegated to `icc_sync_state`.

## Control Flow
At `core_initcall`, the platform driver registers as `qnoc-qcs8300`. Device-tree nodes matching `qcom,qcs8300-*` compatibles select one `qcom_icc_desc` through `qnoc_of_match`. The shared RPMh probe consumes that descriptor, registers all indexed interconnect nodes, initializes BCM voter data, maps QoS register windows when a descriptor has `.config`, and publishes an ICC provider. Runtime ICC consumers then request paths by dt-binding IDs. The interconnect core resolves the path through the static `link_nodes` graph, and Qualcomm RPMh code aggregates average/peak bandwidth into BCM votes and QoS programming.

## State And Persistence
Persistent state is not stored by this file. The source defines immutable SoC topology and initial BCM policy. Runtime state, including provider registration, aggregated bandwidth requests, RPMh votes, regmap handles, and sync state, is owned by the shared Qualcomm ICC/RPMh framework. Important static policy includes `keepalive` on selected BCMs, `enable_mask = BIT(3)` for `ACV`, `vote_scale = 1` for QUP BCMs, and `.qos_requires_clocks = true` for aggre1, aggre2, and gem NoC descriptors.

## Dependencies And Integration Points
It depends on Linux device, module, OF platform, and interconnect provider APIs; `dt-bindings/interconnect/qcom,qcs8300-rpmh.h`; and local Qualcomm helpers `bcm-voter.h` and `icc-rpmh.h`. Integration points are QCS8300 device-tree NoC nodes, interconnect consumers in peripheral drivers, RPMh firmware resources named by BCM strings, and fabric QoS register layouts defined by the per-fabric `regmap_config` `max_register` values.

## Risks
The highest-risk areas are binding-ID array indexes, static graph links, QoS port offsets, and BCM grouping. A wrong index silently binds a consumer path to the wrong node. A missing link can make a valid device-tree interconnect path unresolved. Incorrect QoS offsets or `max_register` limits can program the wrong fabric register or fail regmap validation. Keepalive and vote-scale changes affect idle power and minimum clocks. The QCS8300 file is close to SA8775P but not identical; copying nodes between them risks enabling unsupported second instances or omitting QCS8300-specific service/config nodes.

## Test Signals
Useful signals are kernel build coverage for this driver and its dt-binding header, `dtbs_check` for all `qcom,qcs8300-*` compatibles, boot logs showing each NoC provider registering, debugfs ICC topology/path inspection, and runtime bandwidth requests from UFS, USB, PCIe, display, camera, GPU, LPASS, CDSP, and QUP consumers. On hardware, RPMh vote traces and peripheral throughput or suspend/resume tests are the best evidence that BCM grouping, QoS clocks, and keepalive settings are correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/qcs8300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/qdu1000.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/qdu1000.c

## Purpose
`qdu1000.c` is the Qualcomm QDU1000 RPMh interconnect provider. It models a smaller set of NoC fabrics than the automotive/mobile-oriented files in this group, exposing clock-virtual, GEM NoC, memory-controller virtual, and system NoC paths for modem, eCPRI, PCIe, QUP, storage, USB, QDSS, and Ethernet-related traffic.

## Important APIs, Types, And Functions
The topology uses `struct qcom_icc_node` for masters/slaves, `struct qcom_icc_bcm` for RPMh bandwidth clock managers, `struct qcom_icc_desc` for fabric descriptors, and `struct of_device_id` for compatible-to-descriptor mapping. It includes `icc-common.h` as well as `bcm-voter.h` and `icc-rpmh.h`.

Important descriptors are `qdu1000_clk_virt`, `qdu1000_gem_noc`, `qdu1000_mc_virt`, and `qdu1000_system_noc`. BCMs include `ACV`, `CE0`, `CN0`, `MC0`, `QUP0`, `SH0`, `SH1`, and `SN0`/`SN1`/`SN2`/`SN7`. `qnoc_probe` wraps `qcom_icc_rpmh_probe` only to log `"failed to register ICC provider"` on registration failure.

## Control Flow
The driver registers at `core_initcall` time. Matching `qcom,qdu1000-clk-virt`, `qcom,qdu1000-gem-noc`, `qcom,qdu1000-mc-virt`, or `qcom,qdu1000-system-noc` selects the appropriate descriptor. `qnoc_probe` calls the shared RPMh probe, which registers the provider and nodes for that fabric. Interconnect consumers then request paths by the QDU1000 dt-binding IDs, with the shared framework resolving node links and aggregating requests into the BCM arrays attached to each descriptor.

## State And Persistence
All topology state is static C data. Runtime provider state and RPMh votes live in the shared ICC/RPMh layer. This file has no per-fabric `regmap_config` and no local QoS boxes, so it is primarily vote-topology data rather than direct QoS register programming. `ACV` uses `enable_mask = BIT(3)`, and the other BCMs encode group membership without explicit keepalive or vote-scale fields in this file.

## Dependencies And Integration Points
The driver depends on Linux platform-driver and interconnect-provider APIs, `dt-bindings/interconnect/qcom,qdu1000-rpmh.h`, and the Qualcomm BCM/RPMh helpers. It integrates with QDU1000 device-tree NoC nodes, RPMh resources named by the BCMs, and device drivers for PCIe, QUP, storage, USB, QPIC/QSPI, QDSS, eCPRI, Ethernet subsystem, and modem paths. `MODULE_DEVICE_TABLE(of, qnoc_of_match)` makes the compatibles available for module autoload metadata.

## Risks
Because QDU1000 uses only four descriptors, the biggest risk is overloading `system_noc_nodes`: it contains many peripheral/configuration targets and bridges that other SoCs split into aggre/config fabrics. Incorrect dt-binding indexes or missing bridge links can route consumers to the wrong slave or make a path unresolvable. The lack of local QoS/regmap data means correctness depends heavily on the shared RPMh voting model and BCM membership. The `qnoc_probe` wrapper changes only logging; it must keep returning the exact shared-probe result.

## Test Signals
Build and dt-binding coverage should catch enum/name drift. Boot logs should show registration for all four QDU1000 providers without the local probe error. ICC debugfs should show GEM, MC, system, and QUP core paths. Runtime tests should exercise PCIe, USB, SDCC, QUP, QPIC/QSPI, eCPRI, modem, Ethernet, and QDSS consumers while watching RPMh votes and throughput. Suspend/resume and idle-power checks help confirm that the simplified BCM policy does not leave required rails under-voted or over-voted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/qdu1000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sa8775p.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sa8775p.c

## Purpose
`sa8775p.c` provides the Qualcomm SA8775P RPMh interconnect topology. It is a large SoC data driver for automotive-class fabrics, covering aggregate NoCs, config NoC, display-controller NoC, GEM NoC, GP-DSP NoC, LPASS NoC, memory-controller virtual paths, multimedia NoC, dual NSP/CDSP NoCs, PCIe NoC, and system NoC.

## Important APIs, Types, And Functions
The file is built from `struct qcom_icc_node`, `struct qcom_icc_qosbox`, `struct qcom_icc_bcm`, `struct qcom_icc_desc`, `struct regmap_config`, and OF/platform-driver structures. Its descriptors are `sa8775p_aggre1_noc`, `sa8775p_aggre2_noc`, `sa8775p_clk_virt`, `sa8775p_config_noc`, `sa8775p_dc_noc`, `sa8775p_gem_noc`, `sa8775p_gpdsp_anoc`, `sa8775p_lpass_ag_noc`, `sa8775p_mc_virt`, `sa8775p_mmss_noc`, `sa8775p_nspa_noc`, `sa8775p_nspb_noc`, `sa8775p_pcie_anoc`, and `sa8775p_system_noc`.

BCMs include ACV, crypto, config NoC groups, GP-DSP groups, memory controller, multimedia groups, NSA/NSB CDSP groups, PCIe, QUP, shared memory, and system NoC groups. Many master nodes include inline QoS boxes with port offsets and priority/urgent forwarding policy. The local init/exit functions register a platform driver whose probe and remove are shared `qcom_icc_rpmh_probe` and `qcom_icc_rpmh_remove`.

## Control Flow
At core init, `qnoc-sa8775p` registers. Each `qcom,sa8775p-*` compatible selects a fabric descriptor from `qnoc_of_match`. During probe the shared RPMh code registers indexed nodes, prepares regmap-backed QoS windows from descriptor `.config`, and binds BCM vote groups to the provider. ICC consumers request master-to-slave paths using IDs from `qcom,sa8775p-rpmh.h`; path traversal follows `link_nodes`, then bandwidth aggregation updates the relevant BCMs.

## State And Persistence
This file has no persisted data. Static state captures SoC topology, register limits, QoS policy, and initial BCM behavior. Runtime state is in the interconnect core and Qualcomm RPMh provider. `ACV` uses an enable mask of `0x8`; selected BCMs have `keepalive = true`; QUP BCMs use `vote_scale = 1`; aggre1 and aggre2 descriptors require QoS clocks. The file models extra SA8775P capacity compared with QCS8300, including second EMAC/USB/display/compute/video/GP-DSP and NSPB resources.

## Dependencies And Integration Points
It depends on Linux platform, OF, module, interconnect provider APIs, `dt-bindings/interconnect/qcom,sa8775p-rpmh.h`, and local `bcm-voter.h` and `icc-rpmh.h`. Integration points are SA8775P DTS NoC nodes, interconnect consumers in high-throughput peripherals, RPMh BCM resources, and QoS register blocks described by per-fabric `regmap_config` maximum registers.

## Risks
This is a high-blast-radius static data file. Risks include off-by-one dt-binding indexes, accidental omission of second-instance nodes, mismatched `link_nodes`, wrong QoS port offsets, and BCM groups that aggregate unrelated traffic. The empty `dc_noc_bcms` array is intentional-looking but easy to misread when changing descriptor code. SA8775P and QCS8300 share patterns but differ in node counts and fabric coverage; backporting or forward-porting between them needs careful comparison against hardware documentation and binding headers. Keepalive changes can affect both boot stability and idle power.

## Test Signals
Compile tests should include this driver and the SA8775P binding header. `dtbs_check` should validate all SA8775P NoC compatibles and consumer interconnect references. Boot should show registration of every fabric descriptor. Runtime validation should cover PCIe, UFS card/memory, USB instances, EMAC instances, display pipelines, camera, video, GPU, CDSP/NSP A and B, GP-DSP, LPASS, QUP, and QDSS. ICC debugfs, RPMh vote tracing, throughput benchmarks, suspend/resume, and display/camera/video concurrency are strong signals for topology and QoS correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sa8775p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sar2130p.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sar2130p.c

## Purpose
`sar2130p.c` is the RPMh interconnect topology driver for Qualcomm SAR2130P. It exposes clock virtual, config, GEM, LPASS, memory-controller virtual, multimedia, NSP, PCIe, and system NoC providers. Compared with QCS8300/SA8775P, it uses a shared local `icc_regmap_config` and named reusable QoS box objects for many masters.

## Important APIs, Types, And Functions
The file uses the standard Qualcomm ICC data types: `struct qcom_icc_node`, `struct qcom_icc_qosbox`, `struct qcom_icc_bcm`, `struct qcom_icc_desc`, `struct regmap_config`, and `struct of_device_id`. It includes `icc-common.h` and has additional Linux includes for `io.h`, `of_device.h`, and `sort.h`, although the file itself is still static topology data.

Descriptors are `sar2130p_clk_virt`, `sar2130p_config_noc`, `sar2130p_gem_noc`, `sar2130p_lpass_ag_noc`, `sar2130p_mc_virt`, `sar2130p_mmss_noc`, `sar2130p_nsp_noc`, `sar2130p_pcie_anoc`, and `sar2130p_system_noc`. BCMs include ACV, CE0, CN0, CO0, MC0, MM0/MM1, QUP0/QUP1, SH0/SH1, SN0/SN1/SN3/SN4/SN7. Local init and exit register/unregister a platform driver using shared RPMh probe/remove and `icc_sync_state`.

## Control Flow
The driver registers during core init. Device-tree compatibles select a descriptor, and the shared RPMh probe registers that provider. Consumer bandwidth requests flow through the interconnect core, which resolves SAR2130P node links and aggregates votes into BCMs. QoS-capable masters reference named `qcom_icc_qosbox` objects, giving the shared code port offsets and priority/urgent-forwarding policy for fabric programming through the common `icc_regmap_config`.

## State And Persistence
All state in this file is static topology and policy. Runtime provider objects, bandwidth aggregation, RPMh transactions, and regmap mappings are owned externally. Static policy includes `enable_mask = BIT(3)` for ACV and several `BIT(0)` enable masks, keepalive on selected memory/shared/system BCMs, and `vote_scale = 1` for QUP BCMs. No persistent storage is written.

## Dependencies And Integration Points
Dependencies are Linux device/platform/OF/module/interconnect APIs, `dt-bindings/interconnect/qcom,sar2130p-rpmh.h`, `bcm-voter.h`, `icc-common.h`, and `icc-rpmh.h`. Integration points are SAR2130P DTS NoC providers, interconnect consumers for GPU, camera, display, video, PCIe, USB, SDCC, crypto, QUP, QSPI, LPASS, WLAN Q6, NSP/CDSP, QDSS, and RPMh BCM resources.

## Risks
The shared `icc_regmap_config` reduces repeated register-limit data but increases the chance that a fabric with a different register extent would be under- or over-described. Named QoS boxes improve reuse but require every referenced port offset to match the node's real fabric port. The system NoC descriptor combines many masters, including QDSS, QSPI, QUP, crypto, PIMEM, SDCC, USB, and bridge nodes, so binding-index drift can have broad effects. Extra includes should be kept justified; if future cleanup removes helper usage, unused include warnings may surface under stricter builds.

## Test Signals
Build coverage should compile the SAR2130P driver and binding header. `dtbs_check` should validate each `qcom,sar2130p-*` provider and consumer path. Boot logs should show all nine providers registering and synchronizing. Runtime tests should exercise GPU/display/camera/video concurrency, PCIe, USB, SDCC, QUP/QSPI, LPASS, WLAN Q6, NSP, and QDSS while inspecting ICC debugfs paths and RPMh votes. Suspend/resume and idle tests are important because several BCMs are marked keepalive or have explicit enable masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sar2130p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sc7180.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sc7180.c

## Purpose
`sc7180.c` is the Qualcomm SC7180 interconnect topology driver. It exposes multiple RPMh-backed NoC providers for an older Snapdragon platform, including aggregate NoCs, camera virtual NoC, compute/NPU NoC, config NoC, display-controller NoC, GEM NoC, memory-controller virtual paths, multimedia NoC, QUP virtual paths, and system NoC.

## Important APIs, Types, And Functions
The file uses `struct qcom_icc_node`, `struct qcom_icc_bcm`, `struct qcom_icc_desc`, and OF platform-driver data. Unlike the newer QCS8300/SA8775P files, this file does not define explicit `regmap_config` or `qcom_icc_qosbox` entries; it is predominantly graph and BCM vote topology. Descriptors are `sc7180_aggre1_noc`, `sc7180_aggre2_noc`, `sc7180_camnoc_virt`, `sc7180_compute_noc`, `sc7180_config_noc`, `sc7180_dc_noc`, `sc7180_gem_noc`, `sc7180_mc_virt`, `sc7180_mmss_noc`, `sc7180_npu_noc`, `sc7180_qup_virt`, and `sc7180_system_noc`.

BCMs include ACV, MC0, shared memory groups, multimedia groups, crypto/config/system groups, QUP, compute/NPU groups, and multiple SN groups. Many BCM definitions explicitly set `keepalive` true or false, making the intended power behavior more visible than in some newer files. Driver registration uses `module_platform_driver(qnoc_driver)` rather than manual core init/exit functions.

## Control Flow
When the module or built-in driver registers, OF matching maps `qcom,sc7180-*` compatibles to descriptors. `qcom_icc_rpmh_probe` registers nodes and BCMs with the interconnect core. Consumers use `dt-bindings/interconnect/qcom,sc7180.h` IDs to request bandwidth. The interconnect core follows node links through the relevant fabric descriptors and the Qualcomm RPMh layer sends aggregated BCM votes.

## State And Persistence
There is no persistent data. Static state defines the SC7180 topology, BCM membership, and keepalive policy. Runtime state is external in the ICC provider and RPMh voter. Because no local QoS boxes or regmap configs are present, this driver's behavior is mainly path resolution plus BCM vote aggregation. `ACV` uses `enable_mask = BIT(3)`, and several BCMs deliberately spell out `keepalive = false` where other platforms omit the field.

## Dependencies And Integration Points
Dependencies are Linux device, platform, module, OF match, and interconnect provider APIs; `dt-bindings/interconnect/qcom,sc7180.h`; and local `bcm-voter.h` and `icc-rpmh.h`. Integration points include SC7180 device-tree NoC nodes, interconnect consumers for storage, UFS/eMMC/SDCC, USB, QUP/QSPI, camera, display, Venus, GPU, NPU, IPA, QDSS, PIMEM/IMEM, and RPMh BCM resources.

## Risks
SC7180 has both `compute_noc` and `npu_noc` descriptors plus camera virtual paths, so consumer IDs can be easy to misplace when editing binding arrays. The lack of explicit QoS programming in this file means throughput and latency depend on BCM grouping and shared framework defaults. Explicit false keepalive settings are meaningful documentation; removing them may not change C initialization but can obscure power-intent review. Since this driver uses `module_platform_driver`, changes to init ordering should be considered differently from the core-initcall based newer drivers.

## Test Signals
Build and module metadata checks should cover the SC7180 binding header and OF match table. `dtbs_check` should validate all `qcom,sc7180-*` providers. Boot or module-load logs should show each provider registering and `icc_sync_state` running. Runtime validation should cover camera/display/video, NPU/compute, GPU, UFS/eMMC/SDCC, USB, QUP/QSPI, IPA, QDSS, and memory throughput. ICC debugfs topology, RPMh vote traces, suspend/resume, and idle-power measurements are the best regression signals for BCM membership and keepalive policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sc7180.c -->
