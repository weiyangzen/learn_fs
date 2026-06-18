# Research: subset-b-003985 Qualcomm interconnect sources

Work item: `subset-b-003985`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8974.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8974.c

## Purpose

`msm8974.c` describes the Qualcomm MSM8974 interconnect topology for the Linux interconnect framework. It is a data-heavy platform driver for the legacy RPM-based NoC stack. The file maps device-tree compatibles for the MSM8974 bus fabrics to `struct qcom_icc_desc` descriptors consumed by the shared `icc-rpm` implementation.

The modeled fabrics are BIMC, CNOC, MMSS NoC, OCMEM NoC, PNOC, and SNOC. The opening block comment documents the high-level topology: multimedia, configuration, system, peripheral, on-chip memory, and memory-controller regions. Most of the file is static `qcom_icc_node` declarations for masters, slaves, and fabric bridge nodes, with explicit links expressing graph traversal between interconnect endpoints.

## Important APIs, Types, And Data

The source depends on `dt-bindings/interconnect/qcom,msm8974.h` for public interconnect IDs and on the local `icc-rpm.h` helper API for `struct qcom_icc_node`, `struct qcom_icc_desc`, RPM clock descriptors such as `bimc_clk`, `bus_0_clk`, `bus_1_clk`, `bus_2_clk`, `gpu_mem_2_clk`, and generic `qnoc_probe()` / `qnoc_remove()`.

The file has a private enum whose values are arranged in contiguous fabric-local blocks, but node array indices use the DT binding aliases such as `BIMC_MAS_AMPSS_M0`, `CNOC_SLV_CLK_CTL`, `MNOC_MAS_GRAPHICS_3D`, `OCMEM_SLV_OCMEM`, `PNOC_MAS_SDCC_1`, and `SNOC_MAS_LPASS_AHB`. This keeps the static arrays aligned with binding IDs expected by `of_icc_xlate_onecell` through the common RPM driver.

`msm8974_get_bw()` is a custom `get_bw` callback that writes zero average and peak bandwidth. Every descriptor installs it. This makes the provider avoid deriving initial bandwidth from hardware state; runtime votes are controlled by interconnect clients through the shared aggregation path.

The main descriptor groups are:

- `msm8974_bimc`: APSS/MSS, BIMC-to-MNOC, BIMC-to-SNOC, EBI, and APSS L2 nodes; uses `bimc_clk`, `ignore_enxio`, and `get_bw`.
- `msm8974_cnoc`: RPM, DEHR, QDSS DAP, SPDM, TIC, clock/TCSR/TLMM/security/config slaves, CNOC-to-SNOC and CNOC-to-MM/ONOC/PNOC bridge nodes; uses `bus_2_clk`.
- `msm8974_mnoc`: graphics, JPEG, MDP, video, VFE, MNOC-to-CNOC/BIMC, and MMSS configuration slaves; no explicit bus clock descriptor in the descriptor snippet and relies on common handling plus zero `get_bw`.
- `msm8974_onoc`: OCMEM and OCMEM virtual NoC paths, JPEG/MDP/video/VFE OCMEM masters, and ONOC service node; uses `gpu_mem_2_clk`.
- `msm8974_pnoc`: peripheral masters and slaves for SDCC, BLSP, BAM DMA, USB, TSIF, PDM, PRNG, and PNOC-to-SNOC; uses `bus_0_clk`, `keep_alive = true`.
- `msm8974_snoc`: LPASS/QDSS/SNOC config/BIMC/CNOC/PNOC/OCMEM bridges plus crypto, MSS, WCSS, USB3, OCIMEM, and QDSS STM; uses `bus_1_clk`.

Each `qcom_icc_node` provides a debug name, a stable interconnect ID, bus width, RPM master/slave IDs, and optional links. Links point to downstream node IDs and are the contract that lets the framework build paths across fabric bridges.

## Control Flow

At module load, `module_platform_driver(msm8974_noc_driver)` registers a platform driver named `qnoc-msm8974`. Device tree nodes whose compatibles match `qcom,msm8974-bimc`, `qcom,msm8974-cnoc`, `qcom,msm8974-mmssnoc`, `qcom,msm8974-ocmemnoc`, `qcom,msm8974-pnoc`, or `qcom,msm8974-snoc` bind to the driver. The match table passes the selected `qcom_icc_desc` through `.data`.

Probe, remove, and path programming are delegated to `qnoc_probe`, `qnoc_remove`, and the provider callbacks supplied by `icc-rpm`. During probe the shared code consumes the descriptor, creates Linux `icc_node` objects for each non-null entry, applies bus clock and RPM metadata, registers the interconnect provider, and exposes onecell translation to clients. Runtime control flow is then client-driven: consumers call the interconnect framework, the common RPM code walks linked nodes, aggregates bandwidth, and sends RPM votes for nodes with valid master/slave RPM IDs.

`icc_sync_state` is installed as the driver sync-state callback so late provider synchronization is coordinated with consumers after device probe ordering settles.

## State And Persistence

This file has no persistent on-disk state and does not allocate state directly. The only state it defines is static topology metadata. Hardware and RPM voting state is external: bus clock enablement, keep-alive behavior, and RPM bandwidth votes are handled by the shared `icc-rpm` provider after probe. The zeroing `get_bw` callback means no attempt is made here to persist or restore hardware bandwidth from previous firmware/kernel state.

## Dependencies And Integration Points

The primary integration points are device tree compatible strings, DT interconnect IDs, the common `drivers/interconnect/qcom/icc-rpm.*` implementation, the Linux interconnect core, platform-device binding, and clock/RPM resources named by the shared clock descriptors. Client drivers use the DT binding IDs to request paths through these providers; correctness depends on the node arrays, links, and RPM IDs matching downstream/vendor bus data and board DT.

The provider also integrates with debugfs and interconnect summaries through node names. Because several fabrics bridge into others, the link graph is the key integration surface between otherwise separate DT NoC nodes.

## Risks And Edge Cases

The driver is almost entirely declarative, so the main risks are table accuracy errors: wrong `mas_rpm_id`/`slv_rpm_id`, wrong bus width, missing bridge link, or mismatched array index can silently misroute or under-vote bandwidth. `ignore_enxio = true` on all descriptors tolerates missing RPM paths but can also hide platform-resource issues. `keep_alive` only appears on PNOC, so regressions in idle-sensitive peripheral paths are possible if that flag is changed.

Because `msm8974_get_bw()` always returns zero, tests that expect initial nonzero hardware bandwidth will not observe it through the framework. This is intentional for the existing code path but is a risk if future code assumes provider `get_bw` reflects bootloader state.

## Test Signals

Useful validation signals are successful boot-time binding for all six compatible strings, no `-EPROBE_DEFER` or clock/RPM errors from `qnoc-msm8974`, populated `/sys/kernel/debug/interconnect/` nodes with expected names, and functional bandwidth requests from display, camera, storage, USB, GPU, and modem-related clients. Static review should check every DT binding ID has a matching non-null array slot where expected and every bridge node links to a valid downstream ID.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8974.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8976.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8976.c

## Purpose

`msm8976.c` provides the Qualcomm MSM8976 NoC topology to the interconnect framework. It is another legacy RPM/QoS provider file, based on downstream `msm8976-bus.dtsi` data, and it binds multiple MSM8976 fabric device-tree nodes to shared `icc-rpm` probe/remove logic.

The modeled fabrics are BIMC, PCNOC, SNOC, and SNOC-MM. Compared with `msm8974.c`, this file has richer QoS/regmap metadata: each real NoC descriptor declares a `type`, register layout, QoS offset, clock descriptor, and in some cases AB coefficient or keep-alive behavior.

## Important APIs, Types, And Data

The file includes `dt-bindings/interconnect/qcom,msm8976.h` and `icc-rpm.h`. The private enum lists internal node IDs beginning at 1, while `qcom_icc_node` array indices use binding names like `MAS_APPS_PROC`, `MAS_SMMNOC_BIMC`, `MAS_SNOC_BIMC`, `SLV_EBI`, `MAS_USB_HS2`, `PCNOC_INT_0`, `QDSS_INT`, `SNOC_INT_2`, and `MAS_VFE_1`.

The important descriptors are:

- `msm8976_bimc`: `QCOM_ICC_BIMC` fabric with APPS, SMMNOC, SNOC, TCU, EBI, and BIMC-SNOC nodes. It uses `bimc_clk`, a 32-bit regmap with max register `0x62000`, `qos_offset = 0x8000`, and `ab_coeff = 154`.
- `msm8976_pcnoc`: `QCOM_ICC_NOC` fabric for USB, BLSP, crypto, SDCC, LPASS AHB, SPDM, DEHR, PCNOC internal nodes, and many peripheral/config slaves. It uses `bus_0_clk`, `qos_offset = 0x7000`, `keep_alive = true`, and a `0x14000` regmap limit.
- `msm8976_snoc`: `QCOM_ICC_NOC` system fabric for QDSS, BIMC/SNOC/PCNOC bridge nodes, LPASS, IPA, IMEM, CATS, and related service paths. It uses `bus_1_clk`, `qos_offset = 0x7000`, and a `0x1A000` regmap limit.
- `msm8976_snoc_mm`: multimedia/system fabric slice for JPEG, GPU/OXILI, MDP0/1, Venus, VFE0/1, CPP, MM internal node, and SMMNOC-BIMC slave. It uses `bus_2_clk`, reuses the SNOC regmap config, has `qos_offset = 0x7000`, and `ab_coeff = 154`.

Individual `qcom_icc_node` entries carry node names, IDs, bus widths, QoS settings such as `NOC_QOS_MODE_FIXED` or `NOC_QOS_MODE_INVALID`, AP ownership flags, QoS ports, priorities, and RPM master/slave IDs. Link arrays define edges from masters/bridges to slaves and cross-fabric nodes.

## Control Flow

`module_platform_driver(msm8976_noc_driver)` registers a platform driver named `qnoc-msm8976`. The OF match table maps `qcom,msm8976-bimc`, `qcom,msm8976-pcnoc`, `qcom,msm8976-snoc`, and `qcom,msm8976-snoc-mm` to the corresponding descriptor. The driver delegates probe and remove to `qnoc_probe` and `qnoc_remove`.

On probe, the shared RPM provider code uses the descriptor to map QoS registers, register interconnect nodes, enable or prepare bus clocks as required, and expose the provider to interconnect clients. At runtime, client bandwidth requests are aggregated by the common code and translated into RPM and NoC QoS programming according to node metadata and fabric type.

`icc_sync_state` is set on the platform driver, so the provider participates in sync-state after deferred consumer probing finishes.

## State And Persistence

There is no local mutable state beyond static descriptors. Runtime state lives in the shared provider allocation created by `qnoc_probe`, in regmap-backed NoC QoS registers, in bus-clock state, and in RPM votes. The file itself does not persist votes or restore state. `keep_alive` on PCNOC asks the shared provider to hold that bus active enough to avoid losing access to critical peripheral/config paths.

## Dependencies And Integration Points

This file integrates with DT bindings for MSM8976 interconnect IDs, device-tree compatible strings, platform devices, Linux regmap, the interconnect core, and `icc-rpm`. Correct operation also depends on named clocks and RPM resources expected by the shared descriptors. Display, camera, storage, USB, crypto, GPU, LPASS, IPA, and debug/trace clients consume these paths via DT.

The descriptor `type` field is important because `icc-rpm` programs BIMC, NOC, and QoS registers differently. `ab_coeff` influences average-bandwidth conversion, so it is part of the performance contract, not just metadata.

## Risks And Edge Cases

The highest risk is mismatched topology data from downstream bus definitions. Off-by-one array slots, stale binding IDs, incorrect QoS port numbers, or wrong RPM IDs can produce valid-looking providers that make ineffective votes. Reusing `msm8976_snoc_regmap_config` for SNOC-MM is deliberate but couples MM QoS programming to SNOC register bounds and stride assumptions. `keep_alive` is only on PCNOC; if another fabric has hidden always-on requirements, this data file will not express them.

Because all real behavior is in the common driver, regressions may appear only when a client requests a path through a particular master/slave combination. Static build success is not enough to prove the graph is complete.

## Test Signals

Validation should include boot logs showing `qnoc-msm8976` binds each compatible without regmap, clock, or RPM errors; debugfs interconnect paths show expected BIMC/PCNOC/SNOC/SNOC-MM nodes; and bandwidth clients for SDCC, USB, display/camera/video, GPU, IPA, and LPASS can set paths without `-EINVAL` or missing-provider errors. Static tests should compare the array slots with `qcom,msm8976.h` and verify link targets exist in the represented fabrics.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8976.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8996.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8996.c

## Purpose

`msm8996.c` models the Qualcomm MSM8996 Network-on-Chip topology and QoS metadata for the Linux interconnect framework. It binds eight fabric compatibles to the shared legacy RPM interconnect implementation: A0NOC, A1NOC, A2NOC, BIMC, CNOC, MNOC, PNOC, and SNOC.

This file is the implementation partner for the local `msm8996.h` private ID header and the public `dt-bindings/interconnect/qcom,msm8996.h`. It is data-heavy but includes module registration through a `core_initcall`, which makes MSM8996 NoC providers available early in boot.

## Important APIs, Types, And Data

The file includes Linux device, interconnect-provider, IO, module, platform, and regmap headers, the public MSM8996 DT binding, `icc-rpm.h`, and the local `msm8996.h` internal ID map.

Key static data includes:

- Interface clock name arrays: `mm_intf_clocks` (`iface`), `a0noc_intf_clocks` (`aggre0_snoc_axi`, `aggre0_cnoc_ahb`, `aggre0_noc_mpu_cfg`), and `a2noc_intf_clocks` (`aggre2_ufs_axi`, `ufs_axi`).
- Many link arrays, such as common links from A0/A1/A2 masters into SNOC, BIMC-to-SNOC bridge links, CNOC-to-MNOC config links, MNOC-to-BIMC links, SNOC-to-CNOC/PNOC/VMEM links, and QDSS links.
- `qcom_icc_node` definitions with bus widths, RPM IDs, QoS mode, AP ownership, priority fields, and QoS ports. Notable nodes include PCIe masters, UFS, IPA, USB3, APSS, GPU, MMSS masters, QDSS, BIMC/SNOC/AxNOC bridges, memory/config slaves, and service nodes.
- 32-bit `regmap_config` objects for each fabric with fabric-specific `max_register` values.

The main descriptors are:

- `msm8996_a0noc`: `QCOM_ICC_NOC`, three PCIe masters, A0 interface clocks, `max_register = 0x6000`.
- `msm8996_a1noc`: `QCOM_ICC_NOC`, CNOC/crypto/PNOC A1 masters, `aggre1_branch_clk`, `max_register = 0x5000`.
- `msm8996_a2noc`: `QCOM_ICC_NOC`, USB3/IPA/UFS masters, `aggre2_branch_clk`, A2 interface clocks, `max_register = 0x7000`.
- `msm8996_bimc`: `QCOM_ICC_BIMC`, APSS/GPU/MNOC/SNOC masters and EBI/HMSS/BIMC-SNOC slaves, `bimc_clk`, `ab_coeff = 154`, `max_register = 0x5a000`.
- `msm8996_cnoc`: `QCOM_ICC_NOC`, SNOC-to-CNOC/QDSS DAP masters and many config slaves, `bus_2_clk`, `max_register = 0x1000`.
- `msm8996_mnoc`: `QCOM_ICC_NOC`, multimedia masters and MM config/throttle/SMMU slaves, `mmaxi_0_clk`, `iface` clock, `ab_coeff = 154`, `max_register = 0x1c000`.
- `msm8996_pnoc`: `QCOM_ICC_NOC`, SNOC-to-PNOC and SDCC/USB/BLSP/TSIF/PDM nodes, `bus_0_clk`, `max_register = 0x3000`.
- `msm8996_snoc`: `QCOM_ICC_NOC`, HMSS/QDSS/SNOC config/BIMC/AxNOC bridges and SNOC slaves, `bus_1_clk`, `max_register = 0x20000`.

## Control Flow

The OF table `qnoc_of_match` maps eight `qcom,msm8996-*` compatible strings to descriptors. The platform driver named `qnoc-msm8996` uses `qnoc_probe` and `qnoc_remove`, with `icc_sync_state` for interconnect sync-state.

Unlike several sibling files, registration is explicit: `qnoc_driver_init()` calls `platform_driver_register(&qnoc_driver)` under `core_initcall`, and `qnoc_driver_exit()` unregisters it at module exit. This early init ordering matters for consumers that may probe before normal module-platform-driver init would run.

After a DT node matches, `qnoc_probe` creates the provider, maps registers from the resource, handles clocks, creates graph nodes from the descriptor, and registers the provider with the interconnect core. Runtime requests flow from interconnect consumers into the common RPM aggregator and QoS programmer, using this file's graph to resolve full paths.

## State And Persistence

There is no local dynamic state. Persistent platform state is represented by static descriptors; runtime state is allocated and owned by `icc-rpm`. Hardware-facing state includes NoC QoS registers, clock enable/reference state, and RPM master/slave votes. Because nodes include AP-owned QoS metadata, the shared provider may program local QoS registers in addition to sending RPM votes.

## Dependencies And Integration Points

Dependencies include `icc-rpm`, public and private MSM8996 interconnect IDs, regmap, platform resources, interconnect core, device-tree compatibles, and named clocks. The local `msm8996.h` defines the driver-internal numeric IDs used as array indices; the public binding is the external ABI used by device tree and client drivers.

Integration points cover PCIe, UFS, IPA, USB, APSS/HMSS, GPU, display, camera, video, QDSS, LPASS, storage, and peripheral buses. The A0/A1/A2 split makes bridge links especially important: many client paths begin in an aggregate NoC and terminate through SNOC/BIMC/CNOC/MNOC.

## Risks And Edge Cases

This file has a large surface for table drift: private IDs, public binding IDs, array indices, links, RPM IDs, QoS ports, and register ranges all have to agree. Because the private header is separate, changes to `msm8996.h` can break array indexing without changing this file's compile status if names still resolve differently. Early `core_initcall` registration can expose failures earlier in boot; missing clocks/resources may affect consumers that rely on early interconnect availability.

Interface clocks on A0/A2/MNOC are extra integration risk: a provider may bind but fail to carry traffic if required interface clocks are not described in DT or are misnamed. `ab_coeff` is present only on BIMC and MNOC; performance regressions can occur if multimedia or memory votes are converted with the wrong coefficient.

## Test Signals

Test by booting an MSM8996 DT with all eight NoC nodes and checking that `qnoc-msm8996` providers register during core init without missing-clock/regmap/RPM errors. Debugfs should show all expected nodes and links. Functional signals include PCIe/UFS/USB/IPA activity, display and camera/video bandwidth votes, GPU memory performance, and QDSS tracing paths. Static review should compare `msm8996.h`, `qcom,msm8996.h`, descriptor arrays, and link targets as a set.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8996.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8996.h -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8996.h

## Purpose

`msm8996.h` is a private driver header for `drivers/interconnect/qcom/msm8996.c`. It defines the internal numeric IDs used by the MSM8996 NoC data tables. These IDs are not the public device-tree binding header; they are local array-index and link-target constants for the MSM8996 provider implementation.

## Important APIs, Types, And Data

The header has only preprocessor definitions. It is protected by `__DRIVERS_INTERCONNECT_QCOM_MSM8996_H__` and contains a flat sequence of `#define` constants for MSM8996 masters and slaves.

The master range starts with PCIe/AxNOC and high-performance masters:

- `MSM8996_MASTER_PCIE_0` through `MSM8996_MASTER_PCIE_2`
- `MSM8996_MASTER_CNOC_A1NOC`, `MSM8996_MASTER_CRYPTO_CORE0`, `MSM8996_MASTER_PNOC_A1NOC`
- `MSM8996_MASTER_USB3`, `MSM8996_MASTER_IPA`, `MSM8996_MASTER_UFS`
- APSS/GPU/BIMC/SNOC/CNOC/QDSS and multimedia masters through `MSM8996_MASTER_QDSS_ETR`

The slave range continues at `MSM8996_SLAVE_A0NOC_SNOC` and covers SNOC/BIMC bridge slaves, EBI, HMSS L3, CNOC config slaves, PCIe/UFS/AxNOC config slaves, MMSS config/throttle/SMMU slaves, PNOC peripheral slaves, SNOC endpoint slaves, and service nodes. The final IDs include PCIe and service SNOC endpoints.

## Control Flow

There is no executable control flow. The file is included by `msm8996.c`, where the constants become `.id` values for `qcom_icc_node` entries, array indices through shorter binding aliases, and link targets in `u16` link arrays. The interconnect graph is therefore indirectly controlled by this header's numeric stability.

## State And Persistence

The header has no runtime state and no persistence. Its constants are compile-time ABI inside the MSM8996 driver module. If the numeric values change, every compiled node ID and link target changes.

## Dependencies And Integration Points

The direct integration point is `msm8996.c`. Indirectly, it integrates with the Linux interconnect core because `icc_node` IDs and link target IDs must match registered nodes. It also needs to stay conceptually aligned with `include/dt-bindings/interconnect/qcom,msm8996.h`, although it is private and can contain implementation-specific or differently named IDs.

## Risks And Edge Cases

This is a fragile mapping file. Duplicate values, gaps not reflected by descriptor arrays, renumbering, or a mismatch between master/slave definitions and `msm8996.c` link arrays can create broken paths at runtime while still compiling. Because the definitions are simple macros, the compiler cannot validate semantic grouping or graph completeness.

If future code includes this header outside `msm8996.c`, the private constants could become an accidental API. Keeping it local to the driver avoids exposing unstable implementation IDs.

## Test Signals

The main test signal is successful compilation of `msm8996.c`, but real validation requires runtime provider registration and path resolution. Static checks should ensure every ID referenced by `msm8996.c` exists here, every link target corresponds to a registered node, and the private IDs remain aligned with any generated or hand-maintained node arrays.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/msm8996.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/osm-l3.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/osm-l3.c

## Purpose

`osm-l3.c` is a Qualcomm L3 interconnect provider for OSM and EPSS CPU/L3 clock-performance hardware. Unlike the NoC topology files in this group, it implements provider logic directly. It exposes a simple two-node interconnect path from an apps master to an L3 slave and translates requested peak bandwidth into a hardware performance-state index selected from a frequency LUT.

The driver supports OSM-style L3 blocks and EPSS variants, including a distinction between EPSS `PERF_STATE` and `L3_VOTE` register targets.

## Important APIs, Types, And Data

The file includes bitfield, clock, interconnect-provider, IO, OF, and platform headers plus `dt-bindings/interconnect/qcom,osm-l3.h`.

Important constants:

- `LUT_MAX_ENTRIES = 40`
- `LUT_SRC` and `LUT_L_VAL` extract frequency-source and L-value fields from LUT entries.
- `CLK_HW_DIV = 2`
- OSM registers: `REG_ENABLE`, `OSM_REG_FREQ_LUT`, `OSM_REG_PERF_STATE`, `OSM_LUT_ROW_SIZE`
- EPSS registers: `EPSS_REG_L3_VOTE`, `EPSS_REG_FREQ_LUT`, `EPSS_REG_PERF_STATE`, `EPSS_LUT_ROW_SIZE`

Important types:

- `struct qcom_osm_l3_icc_provider`: runtime provider state with mapped base, max LUT state, performance-state register offset, LUT frequency table, and embedded `icc_provider`.
- `struct qcom_osm_l3_node`: static node metadata containing debug name and bus width.
- `struct qcom_osm_l3_desc`: match-data descriptor containing node table, LUT row size, frequency-LUT offset, and performance-state register offset.

`DEFINE_QNODE` builds the static master/slave node metadata. The driver defines OSM nodes with bus width 16 and EPSS nodes with bus width 32. Descriptors are `osm_l3`, `epss_l3_perf_state`, and `epss_l3_l3_vote`.

## Control Flow

`qcom_osm_l3_probe()` starts by reading the `xo` clock rate and the `alternate` clock rate. The hardware rate used for LUT entries sourced from the alternate path is `alternate / 2`. It allocates provider state, ioremaps the first platform resource, and checks `REG_ENABLE`; if hardware is not enabled, probe fails with `-ENODEV`.

Probe then reads match data, stores the target performance-state register, and scans up to 40 LUT rows. For each row it extracts source and L value. If `src` is set, frequency is `xo_rate * lval`; otherwise it uses the divided alternate-clock rate. Two consecutive equal frequencies terminate the table. The resulting frequency table and `max_state` drive later votes.

After reading the LUT, probe allocates onecell provider data, initializes an `icc_provider` with `qcom_osm_l3_set`, `icc_std_aggregate`, and `of_icc_xlate_onecell`, creates dynamic `icc_node` objects for every descriptor node, assigns node metadata via `node->data`, links master to slave with `icc_link_nodes`, registers the provider, and stores driver data.

`qcom_osm_l3_set()` converts destination peak bandwidth from interconnect units to bytes/second with `icc_units_to_bps()`, divides by source node bus width, finds the first LUT entry that is at least the requested rate, and writes that index to the configured performance-state register with `writel_relaxed()`.

`qcom_osm_l3_remove()` deregisters the provider and removes nodes.

## State And Persistence

Runtime state is per-platform-device and stored in `qcom_osm_l3_icc_provider`. The LUT is read from hardware at probe and retained in memory. The current hardware vote is not mirrored in a separate field; it is the last index written to the performance-state or L3-vote register. There is no persistence across reboot or driver unload.

The driver relies on the hardware already being enabled. It does not enable the OSM/EPSS block itself beyond using clocks to read rates, so firmware/bootloader or another driver must provide the initial enabled state.

## Dependencies And Integration Points

The driver integrates directly with the Linux interconnect framework, OF onecell translation, platform resources, MMIO, and named clocks `xo` and `alternate`. Supported compatibles include `qcom,epss-l3`, `qcom,osm-l3`, `qcom,sa8775p-epss-l3`, `qcom,sc7180-osm-l3`, `qcom,sc7280-epss-l3`, `qcom,sdm845-osm-l3`, `qcom,sm8150-osm-l3`, `qcom,sc8180x-osm-l3`, and `qcom,sm8250-epss-l3`.

Interconnect consumers request the L3 path using IDs from `qcom,osm-l3.h`. CPUfreq/devfreq-related clients are typical consumers because the provider converts bandwidth demand into an L3 performance state.

## Risks And Edge Cases

The LUT scan assumes duplicate consecutive frequencies mean end-of-table; malformed hardware tables could stop early or expose no valid state. If `max_state` ends up 0 or 1, the search loop in `qcom_osm_l3_set()` has little room to select states. `qcom_osm_l3_set()` uses `dst->peak_bw`; aggregate behavior must ensure the destination peak reflects all clients.

The source-node bus width is critical because requested bandwidth is divided by it before LUT comparison. A wrong width for OSM versus EPSS would select consistently wrong performance states. The probe also hard-fails if `REG_ENABLE` is not set, so platforms where the block is disabled until a later power-domain transition will not bind.

The code creates links using `MASTER_OSM_L3_APPS` and `SLAVE_OSM_L3` indices even for EPSS descriptors whose arrays use `MASTER_EPSS_L3_APPS` and `SLAVE_EPSS_L3_SHARED`. This works only if the binding values are intentionally aligned; if DT binding IDs diverge, the link code would need descriptor-specific indices.

## Test Signals

Runtime signals include successful probe with both clocks present, `REG_ENABLE` set, debug logs showing sensible LUT frequencies, and interconnect debugfs showing a two-node provider. Functional validation should request increasing peak bandwidths and confirm the written performance-state index increases and saturates at the last LUT entry. Remove/unbind should deregister the provider without leaked nodes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/osm-l3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/qcm2290.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/qcm2290.c

## Purpose

`qcm2290.c` describes Qualcomm QCM2290 NoC topology for the Linux interconnect framework using the legacy RPM provider. It models BIMC, CNOC, SNOC, a QUP virtual fabric, and multimedia real-time and non-real-time virtual fabrics. The source is table-driven and delegates lifecycle and vote handling to `icc-rpm`.

## Important APIs, Types, And Data

The file includes `dt-bindings/interconnect/qcom,qcm2290.h`, Linux interconnect provider, IO, regmap, platform, and module headers, and `icc-rpm.h`. It defines a private enum of QCM2290 master/slave identifiers and many `qcom_icc_node` objects with bus widths, RPM IDs, QoS fields, and links.

Notable descriptors:

- `qcm2290_bimc`: `QCOM_ICC_BIMC`, APSS, SNOC-BIMC RT/NRT/general, TCU, GFX3D, EBI, and BIMC-SNOC nodes. It uses `bimc_clk`, `keep_alive = true`, `qos_offset = 0x8000`, `ab_coeff = 153`, and a `0x80000` regmap.
- `qcm2290_cnoc`: `QCOM_ICC_NOC`, SNOC-CNOC/QDSS DAP masters and numerous config/peripheral slaves including camera/display/GPU/IPA/LPASS/QPIC/QUP/SDCC/USB/Venus/service nodes. It uses `bus_1_clk`, `keep_alive = true`, and a `0x8200` regmap.
- `qcm2290_snoc`: `QCOM_ICC_QNOC`, crypto/SNOC config/TIC/ANOC/BIMC/PIMEM/QDSS/QUP/IPA/SDCC/QPIC/USB masters and system slaves. It uses `bus_2_clk`, `keep_alive = true`, `qos_offset = 0x15000`, and a `0x60200` regmap.
- `qcm2290_qup_virt`: virtual QUP core path with `qup_clk` and keep-alive behavior.
- `qcm2290_mmnrt_virt`: non-real-time multimedia path for CAMNOC SF, video, and SNOC-BIMC NRT, using `mmaxi_0_clk`, SNOC regmap/QoS offset, `keep_alive`, and `ab_coeff = 142`.
- `qcm2290_mmrt_virt`: real-time multimedia path for CAMNOC HF, MDP0, and SNOC-BIMC RT, using `mmaxi_1_clk`, SNOC regmap/QoS offset, `keep_alive`, and `ab_coeff = 139`.

Many nodes explicitly set `qos.ap_owned = true` and a QoS mode. Links connect peripheral and multimedia masters to SNOC/BIMC/CNOC slaves and virtual endpoints.

## Control Flow

The OF match table maps `qcom,qcm2290-bimc`, `qcom,qcm2290-cnoc`, `qcom,qcm2290-snoc`, `qcom,qcm2290-qup-virt`, `qcom,qcm2290-mmrt-virt`, and `qcom,qcm2290-mmnrt-virt` to descriptors. `module_platform_driver(qcm2290_noc_driver)` registers a platform driver named `qnoc-qcm2290`, using `qnoc_probe` and `qnoc_remove` with `icc_sync_state`.

Probe and runtime behavior are common RPM-provider behavior: map registers if configured, prepare bus clocks, create nodes, register onecell interconnect providers, aggregate requests, program NoC QoS where AP-owned, and send RPM votes for valid master/slave IDs.

## State And Persistence

The file contains static topology only. Runtime state is allocated by `qnoc_probe` and persists for the platform device lifetime. Hardware state consists of NoC QoS register programming, RPM votes, and bus-clock state. The numerous `keep_alive` flags indicate that these fabrics or virtual paths should remain active enough for critical access, but the actual state management is in the shared driver.

## Dependencies And Integration Points

Integration depends on QCM2290 DT interconnect bindings, matching DT fabric nodes, RPM resources, named clocks (`bimc`, bus clocks, QUP, multimedia AXI clocks via shared descriptors), regmap resources, and the interconnect core. Consumers include CPU/APSS, GPU, display, camera, video, USB3, SDCC, QPIC, QUP, IPA, crypto, QDSS, and LPASS users.

The virtual MMRT/MMNRT split is a performance integration point: clients should request the correct real-time or non-real-time path so the different AB coefficients and clock domains are used.

## Risks And Edge Cases

The main risks are data accuracy and virtual-fabric modeling. QCM2290 uses `QCOM_ICC_QNOC` for SNOC and virtual fabrics; an incorrect type or QoS offset can program the wrong register block. The RT/NRT AB coefficients differ, so path misclassification can affect latency-sensitive display/camera traffic. `keep_alive` everywhere reduces risk of inaccessible fabric but can cost idle power if used too broadly.

Because virtual descriptors may reuse SNOC regmap configuration, resource layout assumptions must match DT. Missing or incorrect links from virtual masters to SNOC/BIMC slaves can make client requests resolve incorrectly or fail.

## Test Signals

Useful signals include successful binding of all six compatibles, no missing RPM/clock/regmap resources, populated interconnect debugfs nodes for real and virtual fabrics, and functional bandwidth votes from display/camera/video, QUP, SDCC, USB, IPA, and GPU. Static validation should compare every array slot with `qcom,qcm2290.h` and verify virtual RT/NRT paths terminate at the intended SNOC-BIMC nodes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/qcm2290.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/qcs404.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/qcs404.c

## Purpose

`qcs404.c` is the Qualcomm QCS404 NoC topology provider for the Linux interconnect framework. It is a legacy RPM/QoS data file that describes BIMC, PCNOC, and SNOC fabrics and delegates implementation to the shared `icc-rpm` provider.

## Important APIs, Types, And Data

The source includes `dt-bindings/interconnect/qcom,qcs404.h`, Linux interconnect provider, platform, regmap, module headers, and `icc-rpm.h`. A private enum lists QCS404 master/slave identifiers, while static `qcom_icc_node` declarations describe endpoints and bridge nodes.

The descriptor groups are:

- `qcs404_bimc`: `QCOM_ICC_BIMC`, APSS, graphics, MDP, SNOC-BIMC, TCU, EBI, and BIMC-SNOC. It uses `bimc_clk`, `qos_offset = 0x8000`, `ab_coeff = 153`, and a `0x80000` regmap.
- `qcs404_pcnoc`: `QCOM_ICC_NOC`, SPDM, BLSP, USB HS, crypto, SDCC, SNOC-PCNOC, QPIC, PCNOC internal nodes, and many peripheral/config slaves. It uses `bus_0_clk`, `qos_offset = 0x7000`, `keep_alive = true`, and a `0x15080` regmap.
- `qcs404_snoc`: `QCOM_ICC_NOC`, QDSS, BIMC/SNOC/PCNOC bridges, EMAC, PCIe, USB3, SNOC internal nodes, KPSS/WCSS/IMEM/QDSS/CATS/LPASS slaves. It uses `bus_1_clk`, `qos_offset = 0x11000`, and a `0x23080` regmap.

Nodes contain bus width, RPM master/slave IDs, AP-owned QoS flags, QoS modes, ports, and link arrays. QCS404 includes fixed-priority QoS for several masters and invalid QoS mode for endpoints that should not be directly programmed.

## Control Flow

The OF match table recognizes `qcom,qcs404-bimc`, `qcom,qcs404-pcnoc`, and `qcom,qcs404-snoc`. `module_platform_driver(qcs404_noc_driver)` registers `qnoc-qcs404`, whose probe and remove callbacks are `qnoc_probe` and `qnoc_remove`.

During probe, the shared driver consumes the descriptor, maps registers, creates interconnect nodes, registers links, handles clocks/RPM metadata, and publishes the provider. Unlike several newer files, this driver struct does not set `.sync_state = icc_sync_state`, so sync-state coordination is absent here.

Runtime bandwidth requests from clients flow through the interconnect core into the shared RPM/QoS code. The static links in this file determine how requests traverse PCNOC/SNOC/BIMC bridge nodes.

## State And Persistence

There is no local mutable state. State is static topology plus shared-provider runtime allocations, regmap writes, clock state, and RPM votes. PCNOC `keep_alive` asks the shared code to preserve access to peripheral paths.

## Dependencies And Integration Points

This file integrates with QCS404 DT bindings, device-tree compatible strings, `icc-rpm`, regmap, the interconnect framework, RPM resources, and bus clock resources. Consumers include APSS, GPU/MDP, storage, USB, BLSP, PCIe, EMAC, QPIC, crypto, QDSS, WCSS, and LPASS paths.

## Risks And Edge Cases

As with other declarative NoC files, incorrect IDs, links, QoS ports, or register offsets are the main risks. The absence of a sync-state callback may be intentional for this platform, but it is a difference from adjacent drivers and can affect ordering-sensitive consumers if assumptions change. The PCNOC keep-alive choice must preserve peripheral access without unnecessarily keeping other fabrics active.

The register max values have non-round endings (`0x15080`, `0x23080`), so accidental copy/paste from related SoCs could truncate valid QoS registers or allow out-of-range programming.

## Test Signals

Validation should show all three providers binding, debugfs paths resolving between peripheral/SNOC/BIMC nodes, and real clients such as SDCC, USB, EMAC, PCIe, GPU/MDP, and QDSS successfully voting bandwidth. Static checks should compare array indices with `qcom,qcs404.h` and ensure every link target exists.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/qcs404.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/qcs615.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/qcs615.c

## Purpose

`qcs615.c` describes the Qualcomm QCS615 RPMh interconnect topology. Unlike the legacy RPM files in this group, it uses the RPMh interconnect stack with BCM voters. It binds eight QCS615 NoC compatibles to `qcom_icc_rpmh_probe()` / `qcom_icc_rpmh_remove()` and supplies the nodes, BCM groupings, and regmap configs needed to vote bandwidth through RPMh.

The modeled fabrics are Aggre1 NoC, CAMNOC virtual, Config NoC, DC NoC, GEM NoC, MC virtual, MMSS NoC, and System NoC.

## Important APIs, Types, And Data

The file includes Linux interconnect headers, module and OF platform headers, `dt-bindings/interconnect/qcom,qcs615-rpmh.h`, and the local RPMh helpers `bcm-voter.h` and `icc-rpmh.h`.

The data model uses:

- `struct qcom_icc_node`: RPMh node metadata. Nodes include `.name`, `.id`, `.channels`, `.buswidth`, `.num_links`, and `.links`. Static forward declarations let nodes link to each other before definition.
- `struct qcom_icc_bcm`: bandwidth clock manager groups. BCMs such as `bcm_acv`, `bcm_ce0`, `bcm_cn0`, `bcm_cn1`, `bcm_mc0`, `bcm_mm0`..`bcm_mm3`, `bcm_qup0`, `bcm_sh*`, and `bcm_sn*` group one or more nodes and may set flags such as `.keepalive`, `.vote_scale`, or `.enable_mask`.
- `struct qcom_icc_desc`: per-fabric descriptor with optional `.config` regmap config, node arrays, BCM arrays, and counts.

The descriptor groups are:

- `qcs615_aggre1_noc`: aggregate NoC slice for QUP/QSPI/crypto/IPA/PCIe/UFS/USB/QDSS and bridges into SNOC/CAMNOC; includes BCMs for QUP, crypto, config, and SNOC-related paths.
- `qcs615_camnoc_virt`: virtual camera NoC for uncompressed CAMNOC HF/SF paths and CAMNOC uncomp slave; grouped with MM BCMs.
- `qcs615_config_noc`: large configuration fabric for clocks, TCSR/TLMM, camera/display/GPU/IPA/SDCC/UFS/USB/Venus/QDSS/service/config endpoints.
- `qcs615_dc_noc`: display/cache interconnect region including DC NoC to GEM NoC, LLCC, MDSP MPU config, GEM/SNOC bridges, system PCIe, and service GEMNOC.
- `qcs615_gem_noc`: compute/memory backbone around APPS, TCU, GEMNOC config, GPU, MNOC, SNOC GC/SF, LLCC, and related BCMs.
- `qcs615_mc_virt`: memory-controller virtual path from LLCC to EBI with memory BCMs.
- `qcs615_mmss_noc`: multimedia NoC for CAMNOC HF/SF, MDP, rotator, Venus, MNOC-to-memory endpoints, and service MNOC.
- `qcs615_system_noc`: system NoC for SNOC config, Aggre1/GEM/LPASS/PCIe/PIMEM/GIC masters and APSS/CNOC/GEM/SNOC/memory/IMEM/PIMEM/PCIe/QDSS/TCU slaves.

## Control Flow

The OF match table maps `qcom,qcs615-aggre1-noc`, `qcom,qcs615-camnoc-virt`, `qcom,qcs615-config-noc`, `qcom,qcs615-dc-noc`, `qcom,qcs615-gem-noc`, `qcom,qcs615-mc-virt`, `qcom,qcs615-mmss-noc`, and `qcom,qcs615-system-noc` to descriptors.

The platform driver `qnoc-qcs615` uses `qcom_icc_rpmh_probe` and `qcom_icc_rpmh_remove`, with `icc_sync_state`. Registration is via explicit `core_initcall(qnoc_driver_init)` and `module_exit(qnoc_driver_exit)`, so providers are registered early.

During probe, the shared RPMh code creates interconnect nodes, attaches BCMs to the RPMh BCM voter, maps regmap resources where provided, and registers the provider. Runtime control flow is client-driven: bandwidth requests are aggregated per path, converted into BCM votes, and sent through RPMh rather than legacy RPM.

## State And Persistence

This file declares static topology and BCM membership. Runtime state is owned by the RPMh interconnect core, including provider allocations, BCM voter state, RPMh votes, and any mapped register state for fabrics with `.config`. The file itself does not persist values and does not implement local callbacks.

`keepalive` and BCM grouping are the important state-shaping declarations. They determine which BCMs remain voted and how bandwidth from multiple nodes is combined before RPMh transmission.

## Dependencies And Integration Points

Dependencies include RPMh interconnect support, BCM voter support, QCS615 RPMh DT binding IDs, device-tree compatible nodes, interconnect core, OF platform matching, and register resources for fabrics with regmap configs.

Integration points span QUP/QSPI, crypto, IPA, PCIe, QDSS, SDCC, UFS, USB, camera, display, GPU, Venus, rotator, LLCC, EBI, LPASS, PIMEM, GIC, TCU, APSS, and configuration fabrics. Because RPMh votes are grouped by BCM, the BCM arrays are as important as the node graph for real performance.

## Risks And Edge Cases

The highest risk is BCM membership or node-link accuracy. A path may resolve through the interconnect graph but vote the wrong BCM, under-vote a shared clock manager, or keep an unnecessary BCM active. QCS615 has many similar SNOC/GEM/MNOC endpoint names, so copy/paste errors are plausible and hard to detect through build tests.

Descriptors without `.config` are virtual and depend entirely on shared RPMh handling; descriptors with regmap configs must have correct register bounds. Early `core_initcall` registration can expose resource-order problems during boot. Because this file uses RPMh, using legacy RPM test expectations would miss the key vote path.

## Test Signals

Validation should include successful early binding for all eight compatibles, no RPMh/BCM-voter errors, and interconnect debugfs showing the expected nodes. Functional tests should exercise storage, USB, display, camera, video, GPU, PCIe, IPA, and QUP clients while observing RPMh BCM votes or bandwidth counters. Static review should validate each node ID against `qcom,qcs615-rpmh.h`, every link target, and every BCM's node membership.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/qcs615.c -->
