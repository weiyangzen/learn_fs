# Research: subset-b-003989

Grouped research report for Qualcomm interconnect drivers in `sources/distributed-fs/ceph-client/drivers/interconnect/qcom/`. Each section is bounded for reconciliation into its source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8250.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8250.c

## Purpose

`sm8250.c` is the Qualcomm RPMh interconnect provider description for Snapdragon SM8250. It declares the NoC topology, bandwidth clock manager groups, and device-tree compatible bindings that let the generic Qualcomm RPMh interconnect core expose SM8250 buses to Linux interconnect consumers. The file is almost entirely declarative: executable behavior is delegated to the shared `icc-rpmh` and BCM voter code.

## Important APIs, Types, and Data

The file uses `struct qcom_icc_node` from `icc-rpmh.h` to model masters, slaves, service nodes, and NoC bridge nodes. Important fields are `name`, `channels`, `buswidth`, `num_links`, and `link_nodes`; these drive path traversal and bandwidth scaling in the common interconnect framework. SM8250 covers many domains: aggregate NoCs, QUP virtual clock nodes, compute/NPU NoCs, config NoC, display controller NoC, GEM NoC, memory-controller virtual fabric, MMSS NoC, and system NoC.

`struct qcom_icc_bcm` instances group nodes into RPMh Bus Clock Manager votes. The file defines BCMs such as `ACV`, `MC0`, `SH0`, `MM0`, `CE0`, `CN0`, `SN*`, `QUP*`, and NPU/multimedia groups. Flags like `keepalive`, `enable_mask`, and `vote_scale` affect how the common voter commits RPMh requests. Each `static const struct qcom_icc_desc` combines node arrays and BCM arrays for a single device-tree provider instance.

## Control Flow

Kernel matching starts at `qnoc_of_match`, whose compatible strings include `qcom,sm8250-aggre1-noc`, `aggre2-noc`, `compute-noc`, `config-noc`, `dc-noc`, `gem-noc`, `mc-virt`, `mmss-noc`, `npu-noc`, `qup-virt`, and `system-noc`. `module_platform_driver(qnoc_driver)` registers a platform driver named `qnoc-sm8250`. Probe and remove are shared: `qcom_icc_rpmh_probe` consumes the matched `qcom_icc_desc`, registers provider nodes and links, initializes BCM metadata from command-db, and connects to the BCM voter. Runtime interconnect requests flow through the framework into the common aggregate/set callbacks, which update per-node `sum_avg` and `max_peak`, mark BCMs dirty, and commit RPMh votes.

## State and Persistence

Persistent driver state is static topology data plus runtime aggregation fields embedded in each `qcom_icc_node` and `qcom_icc_bcm`. The source file itself does not allocate long-lived state; provider, voter, regmap, and node registration state are managed by `qcom_icc_rpmh_probe`. State persists for the lifetime of each matched platform device and is removed by `qcom_icc_rpmh_remove`. `icc_sync_state` is used as the driver sync-state hook, so bandwidth votes are expected to settle after device links have synchronized.

## Dependencies and Integration Points

This file depends on Linux interconnect core headers, `dt-bindings/interconnect/qcom,sm8250.h`, `bcm-voter.h`, and `icc-rpmh.h`. Device tree must instantiate the matching NoC nodes with the same compatible strings and binding IDs used as array indexes. Other kernel drivers integrate by requesting interconnect paths with SM8250 binding IDs; the correctness of those paths depends on this file's `link_nodes` topology and BCM membership.

## Risks

The main risk is data skew. A wrong binding index, missing link, incorrect `buswidth`, or mis-grouped BCM can silently produce under-votes, over-votes, failed path lookup, or performance and power regressions. SM8250 includes older domains not present in later chips, including `dc_noc`, `npu_noc`, a modem PCIe path, UFS card, TSIF, and split TLMM nodes, so copy-forward edits from newer SoCs are risky. Empty BCM lists for some domains are intentional only if the common provider can operate without direct BCM voting for that descriptor.

## Test Signals

Useful signals are successful probe for every compatible in the SM8250 device tree, valid `/sys/kernel/debug/interconnect/` nodes and links, no `-EPROBE_DEFER` or command-db lookup failures, and functional bandwidth scaling for display, camera, video, GPU, UFS, USB, PCIe, QUP, NPU, and LLCC/DDR paths. Device-tree binding checks should confirm every referenced master/slave ID maps to exactly one node in the expected descriptor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8350.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8350.c

## Purpose

`sm8350.c` describes the Qualcomm RPMh interconnect topology for Snapdragon SM8350. It exposes SM8350 NoC providers to the Linux interconnect framework by mapping device-tree compatible strings to SoC-specific `qcom_icc_desc` tables. Like most RPMh NoC drivers, it contains little local code and a large amount of static fabric data.

## Important APIs, Types, and Data

The primary data type is `struct qcom_icc_node`, used for masters such as QSPI, QUP, SDCC, UFS, USB, crypto, IPA, PCIe, QDSS, GPU, camera, video, display, NSP, and system/GEM/MEM NoC bridges. `link_nodes` expresses the graph used for interconnect path discovery. `struct qcom_icc_bcm` groups nodes into RPMh-voted resources such as `ACV`, `CE0`, `CN0`, `CN1`, `CN2`, `CO0`, `CO3`, `MC0`, `MM0`, `MM1`, `MM4`, `MM5`, `SH*`, and `SN*`.

Descriptor tables cover `aggre1_noc`, `aggre2_noc`, `config_noc`, `dc_noc`, `gem_noc`, `lpass_ag_noc`, `mc_virt`, `mmss_noc`, `compute_noc`, and `system_noc`. Compared with SM8250, SM8350 adds LPASS aggregate NoC support and an NSP/compute descriptor shape, while dropping the explicit SM8250 NPU NoC descriptor.

## Control Flow

The `qnoc_of_match` table maps SM8350 compatible strings to descriptor data. `module_platform_driver(qnoc_driver)` registers the `qnoc-sm8350` platform driver. Probe dispatches to `qcom_icc_rpmh_probe`; that helper reads the matched descriptor, registers an interconnect provider, creates interconnect nodes for every non-null indexed entry, wires graph links, initializes BCMs, and prepares the RPMh voter. Subsequent `icc_set_bw` calls from device drivers are aggregated by common RPMh callbacks and committed as BCM votes.

## State and Persistence

Static node and BCM objects own the topology declarations. Runtime state is stored in per-node aggregate arrays and per-BCM vote/dirty fields defined by `icc-rpmh.h`; the common provider owns any allocation and teardown. No file-local persistence, firmware cache, or workqueue is implemented here. Driver state exists only while each platform device is bound.

## Dependencies and Integration Points

The file depends on `dt-bindings/interconnect/qcom,sm8350.h`, Linux interconnect provider APIs, and Qualcomm RPMh support from `icc-rpmh` and `bcm-voter`. It integrates with device tree through compatible strings such as `qcom,sm8350-gem-noc`, `qcom,sm8350-mmss-noc`, and `qcom,sm8350-system-noc`. Runtime consumers are display, camera, video, storage, USB, PCIe, crypto, IPA, audio/LPASS, compute/NSP, and memory drivers using SM8350 binding IDs.

## Risks

The file is sensitive to topology and binding drift. Incorrect links between aggregate NoCs, GEM NoC, system NoC, LLCC, or EBI can break path resolution or route bandwidth through the wrong BCM. BCM group membership is power-critical: `keepalive` and `enable_mask` resources such as CN/MC/SH/SN groups must stay aligned with RPMh command-db expectations. LPASS and compute/NSP descriptors are distinct from SM8250, so backporting needs device-tree and binding synchronization.

## Test Signals

Expected signals include clean module/platform probe, no command-db errors, interconnect debugfs paths for all SM8350 providers, and successful bandwidth votes for memory, multimedia, LPASS, PCIe, QUP, UFS, USB, SDCC, and crypto paths. Binding tests should catch missing array indexes; runtime validation should include suspend/resume because `keepalive` BCMs and sync-state behavior affect low-power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8350.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8450.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8450.c

## Purpose

`sm8450.c` is the RPMh interconnect topology driver for Qualcomm SM8450. It publishes the SoC's NoC fabrics as interconnect providers and supplies the common Qualcomm RPMh code with node graphs, BCM vote groups, and OF compatible mappings.

## Important APIs, Types, and Data

The file defines many `qcom_icc_node` objects for aggregate NoCs, QUP virtual clocks, config NoC, GEM NoC, LPASS aggregate NoC, MC virtual memory path, MMSS NoC, NSP NoC, PCIe aggregate NoC, and system NoC. Node fields define the debug name, channel count, bus width, and graph links. Notable SM8450 additions relative to SM8350 include split QDSS ETR nodes, sensor/SP masters, LPASS DSP node, PCIe ANOC, display-specific duplicate memory path nodes (`*_disp`), and updated video/camera node names.

BCM definitions cover core memory, multimedia, compute, system, crypto, QUP, and display-specific vote groups. The `clk_virt` descriptor uses QUP BCMs and core master/slave nodes so serial-engine clock paths can be represented as interconnect providers.

## Control Flow

The driver has a standard platform driver but registers through an explicit `qnoc_driver_init` marked `core_initcall`, with `qnoc_driver_exit` for module removal. This earlier init timing helps make interconnect providers available before dependent core devices need them. Probe still delegates to `qcom_icc_rpmh_probe`, and remove delegates to `qcom_icc_rpmh_remove`. The OF table maps compatibles for `aggre1-noc`, `aggre2-noc`, `clk-virt`, `config-noc`, `gem-noc`, `lpass-ag-noc`, `mc-virt`, `mmss-noc`, `nsp-noc`, `pcie-anoc`, and `system-noc`.

## State and Persistence

All topology state is static. Runtime aggregate bandwidth and BCM vote state are stored in the common `qcom_icc_node` and `qcom_icc_bcm` fields after registration. There is no custom file-local persistence, locking, or asynchronous control flow. The sync-state callback is `icc_sync_state`, ensuring interconnect provider state participates in the device core's sync-state phase.

## Dependencies and Integration Points

The driver depends on `dt-bindings/interconnect/qcom,sm8450.h`, `icc-rpmh.h`, and `bcm-voter.h`. It integrates with RPMh command-db through BCM names and with device tree through compatible strings. Consumers include high-bandwidth multimedia blocks, GPU, PCIe, UFS/USB/SDCC, QUP, crypto/IPA, LPASS, NSP/compute, and system memory clients.

## Risks

The main risk is mismatch among bindings, node-array indexes, and device-tree references. Display-specific nodes and duplicated memory path descriptors raise the chance of accidentally voting the wrong path. The `core_initcall` timing means probe failures can show up early in boot and may block consumers sooner than module-init drivers. Incorrect QUP `vote_scale` or `keepalive` settings can break serial buses during low-power states.

## Test Signals

Tests should verify early boot probe ordering, successful registration for every SM8450 compatible, and interconnect path availability before display, storage, PCIe, and serial-engine clients probe. Runtime evidence should include bandwidth vote changes under camera/video/display load, successful suspend/resume, and no RPMh/command-db warnings for BCM names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8450.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8550.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8550.c

## Purpose

`sm8550.c` describes Snapdragon SM8550 interconnect fabrics for the Qualcomm RPMh interconnect core. It maps SM8550 device-tree NoC providers to node and BCM tables so clients can request bandwidth across aggregate, config, GEM, LPASS, memory, multimedia, NSP, PCIe, and system fabrics.

## Important APIs, Types, and Data

The file uses the RPMh `qcom_icc_node`, `qcom_icc_bcm`, and `qcom_icc_desc` types. SM8550 introduces a more split provider model than SM8450: separate `cnoc_main`, `lpass_lpiaon_noc`, and `lpass_lpicx_noc` descriptors appear alongside `config_noc`, `lpass_ag_noc`, `nsp_noc`, and `pcie_anoc`. Nodes include QUP core virtual nodes, storage/USB/QDSS/crypto/IPA masters, a config super-master `qsm_cfg`, GEM NoC bridges, LPASS/LPI nodes, MMSS camera/display/video masters, and memory endpoints.

BCM groups include `ACV`, `CE0`, `CN0`, `CN1`, `CO0`, `LP0`, `MC0`, `MM0`, `MM1`, `QUP*`, `SH*`, and `SN*`. `keepalive`, `enable_mask`, and `vote_scale` data are interpreted by shared RPMh code, not by this file.

## Control Flow

SM8550 uses explicit `core_initcall(qnoc_driver_init)` registration and `module_exit(qnoc_driver_exit)`. The platform driver named `qnoc-sm8550` uses `qcom_icc_rpmh_probe`, `qcom_icc_rpmh_remove`, and `icc_sync_state`. The OF match table wires compatibles for `aggre1-noc`, `aggre2-noc`, `clk-virt`, `config-noc`, `cnoc-main`, `gem-noc`, `lpass-ag-noc`, `lpass-lpiaon-noc`, `lpass-lpicx-noc`, `mc-virt`, `mmss-noc`, `nsp-noc`, `pcie-anoc`, and `system-noc`.

## State and Persistence

The static data models hardware topology. Runtime state is limited to common per-provider allocations and mutable aggregate/vote fields inside shared structs. There are no custom timers, firmware transactions, or file-local caches. Because registration happens at core init, this data can become available to early consumers during boot.

## Dependencies and Integration Points

Dependencies include `dt-bindings/interconnect/qcom,sm8550.h`, Linux interconnect provider APIs, RPMh command-db and BCM voter support through `icc-rpmh.h` and `bcm-voter.h`. Integration points are the SM8550 DTS NoC nodes and any drivers using SM8550 master/slave IDs. The split LPASS/LPI and CNOC main descriptors must match firmware and DTS layout exactly.

## Risks

Risk clusters around split-domain correctness. Moving a node between `config_noc` and `cnoc_main`, or between LPASS aggregate/LPI CX/LPI AON descriptors, can make paths unresolvable or produce missing BCM votes. Multimedia and PCIe paths have high bandwidth sensitivity; wrong bus widths or BCM grouping can cause performance throttling that is hard to attribute. License metadata is `GPL`, while several nearby older files use `GPL v2`; this matters only for module metadata consistency.

## Test Signals

Boot should show all SM8550 NoC platform devices probing with no command-db lookup errors. Debugfs should expose paths through the split CNOC and LPASS providers. Exercise camera, display, video, PCIe, UFS, USB, QUP, IPA, crypto, LPASS, and NSP clients while watching interconnect summaries and RPMh vote traces. Suspend/resume tests are important for keepalive BCMs and LPI paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8550.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8650.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8650.c

## Purpose

`sm8650.c` is the Qualcomm RPMh interconnect topology driver for Snapdragon SM8650. It supplies common RPMh interconnect code with SM8650-specific node graphs, BCM vote groups, QoS register metadata, and OF compatible-to-descriptor mappings.

## Important APIs, Types, and Data

The file uses `qcom_icc_node`, `qcom_icc_bcm`, `qcom_icc_desc`, and newer `qcom_icc_qosbox` data. A local `icc_regmap_config` configures 32-bit, stride-4, fast regmap access for QoS-capable descriptors. Many master nodes carry `.qosbox` pointers with port offsets and priority/urgent-forwarding policy; descriptor entries with `.config = &icc_regmap_config` allow the shared RPMh code to program QoS registers where needed.

SM8650 topology includes aggregate NoCs, `clk_virt`, `config_noc`, `cnoc_main`, `gem_noc`, LPASS aggregate/LPI AON/LPI CX NoCs, `mc_virt`, `mmss_noc`, `nsp_noc`, `pcie_anoc`, and `system_noc`. Newer nodes include combined `qxm_qup02`, `alm_ubwc_p_tcu`, `qnm_ubwc_p`, `qnm_apss_noc`, expanded CPR/I3C/PCIe RSCC config slaves, and UBWC-related BCM coverage.

## Control Flow

The driver registers at `core_initcall` using a platform driver named `qnoc-sm8650`. OF compatibles map each SM8650 NoC provider to its `qcom_icc_desc`. During probe, `qcom_icc_rpmh_probe` reads descriptor data, maps registers for descriptors with `config`, creates interconnect nodes and links, initializes BCMs, and connects to the BCM voter. Runtime bandwidth changes are handled by shared aggregate and set callbacks, which combine client votes into RPMh BCM commits.

## State and Persistence

Static topology, BCM, QoS, and descriptor data live in this file. Runtime state is stored in common mutable fields: per-node aggregate arrays, per-BCM vote arrays, dirty flags, command-db auxiliary data, regmap/provider objects, and voter state. There is no SM8650-specific persistence beyond the platform device lifetime. QoS programming depends on regmap access established during probe.

## Dependencies and Integration Points

The file depends on `dt-bindings/interconnect/qcom,sm8650.h`, Linux interconnect core APIs, `icc-rpmh.h`, `bcm-voter.h`, regmap, RPMh command-db, and the device tree's MMIO resources for QoS-capable NoCs. Integration points include all SM8650 consumers using binding IDs, plus firmware command-db resources named by BCM strings such as `CN0`, `MM1`, `SH1`, and `SN*`.

## Risks

This file has higher risk than older declarative-only variants because QoS boxes add register offsets and policy bits. Wrong `port_offsets`, `prio`, `urg_fwd`, or descriptor `.config` settings can cause subtle priority or latency regressions. Missing `.config` on a QoS-bearing descriptor can skip QoS programming; adding it to a provider without resources can break probe. Combined QUP and UBWC-related nodes require careful binding alignment. Empty BCM arrays for selected descriptors should be treated deliberately, not as omissions, because they change whether a provider emits RPMh votes.

## Test Signals

Validation should include boot-time probe for every SM8650 compatible, successful regmap/resource mapping for QoS descriptors, absence of RPMh command-db errors, and debugfs visibility for all provider graphs. Runtime tests should cover QUP, UFS, USB, SDCC, PCIe, display, camera, video, GPU, LPASS, NSP, IPA, crypto, and memory bandwidth. QoS-sensitive validation should look for latency/performance changes under concurrent multimedia and storage traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8650.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8750.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8750.c

## Purpose

`sm8750.c` provides the RPMh interconnect topology for Qualcomm SM8750. It is a newer-generation NoC description file that maps SM8750 device-tree providers to static node graphs and BCM vote groups consumed by the shared Qualcomm interconnect RPMh implementation.

## Important APIs, Types, and Data

The file defines `qcom_icc_node` objects for aggregate NoCs, QUP virtual clocks, config/CNOC main providers, GEM NoC, LPASS aggregate and LPI providers, MC virtual memory, MMSS, NSP, PCIe ANOC, and system NoC. Compared with SM8650, it has no local QoS regmap/qosbox data in this file, uses a single `xm_pcie3`/`xs_pcie` naming shape, adds SoC control processor nodes such as `qxm_soccp` and `qhs_soccp`, adds EVA/video-specific nodes (`qhs_eva_cfg`, `qnm_video_eva`, `qnm_video_mvp`), and includes UBWC path nodes through `qnm_ubwc_p` and `chs_ubwc_p`.

BCM groups include memory, multimedia, crypto, CNOC, LPASS, QUP, shared/GEM, system, PCIe, and UBWC-related resources. Descriptors cover `aggre1_noc`, `aggre2_noc`, `clk_virt`, `config_noc`, `cnoc_main`, `gem_noc`, `lpass_ag_noc`, `lpass_lpiaon_noc`, `lpass_lpicx_noc`, `mc_virt`, `mmss_noc`, `nsp_noc`, `pcie_anoc`, and `system_noc`.

## Control Flow

The platform driver `qnoc-sm8750` is registered through `core_initcall(qnoc_driver_init)`, with module exit unregistering it. Probe and remove use `qcom_icc_rpmh_probe` and `qcom_icc_rpmh_remove`; the driver also sets `.sync_state = icc_sync_state`. The OF match table maps each `qcom,sm8750-*` compatible to the descriptor for that NoC domain. Once registered, normal interconnect consumer requests aggregate through common RPMh callbacks into BCM votes.

## State and Persistence

The file's only durable contents are static topology and BCM definitions. Runtime mutable state is owned by common code: provider allocations, interconnect node registration, per-node aggregate bandwidth, BCM vote state, and command-db-derived BCM metadata. There is no file-local persistent storage, delayed work, or direct RPMh transaction code.

## Dependencies and Integration Points

Dependencies include `dt-bindings/interconnect/qcom,sm8750.h`, Linux interconnect provider infrastructure, and Qualcomm RPMh/BCM support via `icc-rpmh.h` and `bcm-voter.h`. Integration depends on device tree using matching compatible strings and binding IDs. Runtime consumers include storage, USB, PCIe, display, camera, video/EVA, GPU, QUP, crypto, IPA, LPASS, NSP, SoC control processor, and memory/LLCC clients.

## Risks

SM8750 is likely to receive churn as bindings and DTS mature. Naming and topology changes from SM8650, especially PCIe consolidation, SoC control processor nodes, EVA/video changes, and UBWC BCM membership, are high-risk areas. Missing or misplaced BCMs can under-vote shared memory or multimedia fabrics. Because this file lacks explicit QoS boxes while SM8650 has them, reviewers should confirm whether SM8750 QoS is intentionally handled elsewhere or not required for these descriptors.

## Test Signals

Expected tests are clean early provider registration, successful probe for all `qcom,sm8750-*` NoC compatibles, populated interconnect debugfs graphs, and no command-db/BCM-voter errors. Functional validation should exercise PCIe, UFS, USB, SDCC, QUP, display, camera, EVA/video, GPU, LPASS, NSP, crypto/IPA, and memory traffic, including suspend/resume to verify keepalive BCM handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/sm8750.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/smd-rpm.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/smd-rpm.c

## Purpose

`smd-rpm.c` is a small communication wrapper that lets legacy Qualcomm interconnect drivers send bandwidth and bus-clock votes to the Resource Power Manager over SMD. It is separate from the RPMh path used by the SM8250 and newer files above; this wrapper supports older RPM/SMD-based interconnect providers.

## Important APIs, Types, and Functions

The file defines a single global `static struct qcom_smd_rpm *icc_smd_rpm` and exports three GPL symbols. `qcom_icc_rpm_smd_available()` returns whether the RPM handle has been discovered. `qcom_icc_rpm_smd_send(int ctx, int rsc_type, int id, u32 val)` builds an `icc_rpm_smd_req` with key `RPM_KEY_BW`, a 32-bit payload size, and the requested value, then calls `qcom_rpm_smd_write()`. `qcom_icc_rpm_set_bus_rate(const struct rpm_clk_resource *clk, int ctx, u32 rate)` builds a `clk_smd_rpm_req` using `QCOM_RPM_SMD_KEY_RATE`; branch clocks are normalized to boolean on/off before writing.

## Control Flow

The platform driver is named `icc_smd_rpm` and is registered with `module_platform_driver`. Probe obtains the parent RPM handle with `dev_get_drvdata(pdev->dev.parent)` and stores it in the global. If the handle is missing, probe logs an error and returns `-ENODEV`. Remove clears the global pointer. Exported send functions are then called by RPM interconnect code when aggregating bus bandwidth or clock-rate changes.

## State and Persistence

State is intentionally minimal and global. The RPM handle persists in `icc_smd_rpm` only while the wrapper platform device is bound. There is no reference counting, locking, queueing, or cached vote state in this file; callers are expected to use it only after availability is true and while the device remains registered. Request structs are stack-local and serialized immediately through `qcom_rpm_smd_write`.

## Dependencies and Integration Points

The wrapper depends on `linux/soc/qcom/smd-rpm.h`, `icc-rpm.h`, platform-device infrastructure, and the parent Qualcomm SMD RPM device. It integrates with older Qualcomm interconnect providers that call the exported symbols to send RPM bus master/slave requests or bus clock rate requests. The request format must match RPM firmware expectations: little-endian key, byte count, and value.

## Risks

The global pointer has no internal locking, so correctness depends on normal platform-device lifetime and module dependencies preventing calls after remove. Calling `qcom_icc_rpm_smd_send` before successful probe would pass a null RPM handle to `qcom_rpm_smd_write`. Branch clock coercion is intentional but easy to misuse if a non-branch clock is described incorrectly. Endianness and key constants are firmware ABI details and should not be changed casually.

## Test Signals

Probe should succeed only when the parent SMD RPM driver has provided drvdata. Legacy interconnect clients should see successful RPM writes for bandwidth and bus-rate updates, with no `unable to retrieve handle to RPM` log. Useful tests include booting an RPM/SMD platform, exercising interconnect bandwidth requests, toggling branch-clock resources, and verifying no calls occur before `qcom_icc_rpm_smd_available()` returns true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/smd-rpm.c -->
