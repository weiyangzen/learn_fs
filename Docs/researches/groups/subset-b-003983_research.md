# subset-b-003983 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/bulk.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/bulk.c

Purpose: consumer-side bulk helpers for the Linux interconnect framework. The file lets drivers acquire, release, enable, disable, and vote bandwidth for multiple named paths through one table of `struct icc_bulk_data`.

Important APIs/types/functions: `of_icc_bulk_get()`, `icc_bulk_put()`, `icc_bulk_set_bw()`, `icc_bulk_enable()`, `icc_bulk_disable()`, and `devm_of_icc_bulk_get()` are exported. `struct icc_bulk_devres` records the caller-provided path table and count for devres cleanup.

Control flow: acquisition walks the path table and calls `of_icc_get()` for each name. On the first failure it clears the failed slot and unwinds already acquired paths with `icc_bulk_put()`. Bandwidth and enable operations iterate forward and stop on the first error; enable unwinds already-enabled paths by disabling the prefix.

State and persistence: no independent persistent state is owned here. The caller's `paths[i].path` fields are populated and later nulled by `icc_bulk_put()`. Devm state persists until device teardown and then releases all paths.

Dependencies/integration: depends on the core interconnect consumer API, OF path naming, devres, and exported symbols for driver modules.

Risks and test signals: test partial acquisition failure, `-EPROBE_DEFER` logging suppression, NULL path handling when a device has no interconnects, enable rollback, and devm cleanup ordering. A `icc_bulk_set_bw()` failure does not roll back prior bandwidth votes, so consumers need tests for partial vote application.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/bulk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/core.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/core.c

Purpose: central Linux interconnect framework implementation. It registers providers, stores topology nodes in an IDR and provider lists, resolves device-tree or name-based paths, aggregates consumer bandwidth requests, applies provider constraints, exposes debugfs summaries/graphs, and handles boot-time sync-state floors.

Important APIs/types/functions: exports include `of_icc_xlate_onecell()`, `of_icc_get_from_provider()`, `of_icc_get_by_index()`, `of_icc_get()`, `icc_get()`, `icc_set_tag()`, `icc_get_name()`, `icc_set_bw()`, `icc_enable()`, `icc_disable()`, `icc_put()`, node create/destroy/link/add/remove helpers, provider init/register/deregister, `icc_std_aggregate()`, and `icc_sync_state()`.

Control flow: providers create nodes and links, register an xlate callback, and consumers obtain an `icc_path` by OF phandle pairs or by source/destination name. `path_find()` performs breadth-first traversal using temporary `is_traversed` and `reverse` fields, then `path_init()` attaches one `icc_req` per node to each node's request hlist. `icc_set_bw()` updates all requests in a path, reaggregates every affected node through provider callbacks, calls provider `set()` along adjacent path hops, and rolls back old values if applying constraints fails.

State and persistence: global state is `icc_idr`, `icc_providers`, `providers_count`, `synced_state`, and debugfs dentries. Per-path request state persists until `icc_put()` removes hlist entries, drops provider user counts, and frees the path name. Initial hardware bandwidth is preserved as `init_avg/init_peak` until all counted providers call `icc_sync_state()`.

Dependencies/integration: integrates with OF phandle parsing, device model sync-state, debugfs/seq_file, tracepoints, provider callbacks, and `internal.h` path/request layouts.

Risks and test signals: exercise lock ordering between `icc_lock` and `icc_bw_lock`, path traversal cleanup after missing links, rollback when a provider `set()` fails, dynamic ID lifetime, provider deregistration with active users, initial bandwidth floors before and after sync-state, and debugfs reads during provider add/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/debugfs-client.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/debugfs-client.c

Purpose: optional debugfs-only test client for manually creating interconnect votes by source and destination node names. It is intentionally disabled at compile time unless the source is edited to define `INTERCONNECT_ALLOW_WRITE_DEBUGFS`.

Important APIs/types/functions: when enabled, `icc_debugfs_client_init()` creates `test_client` files under the interconnect debugfs directory. `icc_get_set()` looks up or reuses a path, `icc_commit_set()` applies the stored tag and bandwidth, and `struct debugfs_path` caches previously requested path handles.

Control flow: users write `src_node` and `dst_node`, then write `get` to create or select an `icc_path`, then write `avg_bw`, `peak_bw`, and `tag`, and finally write `commit` to call `icc_set_tag()` and `icc_set_bw()`. A synthetic platform device supplies the consumer device for `icc_get()`.

State and persistence: static globals hold the platform device, current path, strings, bandwidth values, tag, and cached path list. Cached paths are not released by this file during normal operation, which is acceptable only for ad hoc debug sessions.

Dependencies/integration: depends on debugfs, platform devices, RCU string dereference used by `debugfs_create_str()`, and the internal name-based `icc_get()` function.

Risks and test signals: this can alter live interconnect votes from debugfs, hence the source-level opt-in. If enabled, test duplicate path reuse, invalid names, allocation failure after string duplication, concurrency under `debugfs_lock`, module/device teardown leaks, and commit before get. The disabled stub should compile and return success without debugfs side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/debugfs-client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/icc-clk.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/icc-clk.c

Purpose: generic adapter that exposes ordinary clocks as interconnect providers. It lets consumers vote peak bandwidth on a simple master-to-slave pair and translates that vote into clock enable/disable and rate changes.

Important APIs/types/functions: `struct icc_clk_node` tracks a clock and enabled state, `struct icc_clk_provider` embeds `struct icc_provider`, and exported APIs are `icc_clk_register()`, `devm_icc_clk_register()`, and `icc_clk_unregister()`. Provider callbacks are `icc_clk_set()` and `icc_clk_get_bw()`.

Control flow: registration allocates a onecell table with two nodes per clock, creates a master node with clock data, links it to a slave node, adds both to the provider, and registers the provider. `icc_clk_set()` disables the clock when peak bandwidth is zero, otherwise prepares/enables it and calls `clk_set_rate()` with `icc_units_to_bps(src->peak_bw)`.

State and persistence: state is devm-allocated with the registering device. Each clock node records whether this wrapper enabled the clock. Unregister deregisters the provider, removes nodes, and disables any still-enabled clocks.

Dependencies/integration: depends on common clock framework, `linux/interconnect-clk.h` data, core interconnect node APIs, and onecell OF translation.

Risks and test signals: test zero-rate disable, first enable failure, `clk_set_rate()` failure after enable, unregister with active paths, duplicate IDs, and NULL clocks. `icc_clk_get_bw()` only fills `peak`, so callers expecting `avg` initialization should be checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/icc-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/icc-kunit.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/icc-kunit.c

Purpose: KUnit coverage for core interconnect topology construction, request aggregation, bandwidth voting, tags, enable/disable, and bulk helper behavior using a small synthetic provider.

Important APIs/types/functions: `struct test_node_data` describes a CPU/GPU to BUS to DDR topology. `struct icc_test_priv` owns the provider, platform device, and node pointers. Tests are `icc_test_topology_integrity()`, `icc_test_set_bw()`, `icc_test_aggregation()`, and `icc_test_bulk_ops()`.

Control flow: suite init allocates a platform device, registers a provider with no-op `set`, standard aggregation, and zero initial bandwidth, creates nodes and links from `test_topology`, then calls `icc_sync_state()`. Helpers manually create mock `icc_path` objects and attach their requests to node hlist state so `icc_set_bw()` can aggregate without OF path lookup.

State and persistence: all test objects are KUnit-managed except nodes registered in the real interconnect core. Suite exit removes nodes and deregisters the provider. Mock paths are explicitly detached from request lists before freeing.

Dependencies/integration: depends on KUnit, KUnit platform device helpers, interconnect core internals, and `bulk.c` exported helpers.

Risks and test signals: useful signals include aggregate sum/max behavior on shared BUS, disabled paths voting zero, tag propagation to all path requests, and bulk enable/disable semantics. The manual path construction bypasses provider user counts and path search, so separate tests are still needed for `icc_get()`, OF parsing, rollback, and provider lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/icc-kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/imx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/interconnect/imx/Kconfig

Purpose: Kconfig menu for NXP i.MX interconnect support. It defines the generic i.MX helper driver and per-SoC platform topology drivers for i.MX8MM, i.MX8MN, i.MX8MQ, and i.MX8MP.

Important APIs/types/functions: symbols are `INTERCONNECT_IMX`, `INTERCONNECT_IMX8MM`, `INTERCONNECT_IMX8MN`, `INTERCONNECT_IMX8MQ`, and `INTERCONNECT_IMX8MP`. The generic symbol is tristate and depends on `ARCH_MXC || COMPILE_TEST`; the SoC symbols depend on `INTERCONNECT_IMX`.

Control flow: there is no runtime flow, but build selection controls whether `imx.o` and specific SoC module objects are compiled. The SoC drivers call the helper exported by `imx.c`.

State and persistence: Kconfig state persists in kernel configuration and determines module or built-in linkage.

Dependencies/integration: integrates with the parent `drivers/interconnect` Kconfig and the Makefile in this directory.

Risks and test signals: test allmodconfig, allyesconfig, and COMPILE_TEST builds for dependency coverage. Since the per-SoC entries have no help text, config UI clarity depends on symbol names alone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/imx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/imx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/interconnect/imx/Makefile

Purpose: build mapping for the i.MX interconnect helper and SoC topology modules.

Important APIs/types/functions: object groups are `imx-interconnect-objs := imx.o`, `imx8mm-interconnect-objs := imx8mm.o`, `imx8mq-interconnect-objs := imx8mq.o`, `imx8mn-interconnect-objs := imx8mn.o`, and `imx8mp-interconnect-objs := imx8mp.o`.

Control flow: each `obj-$(CONFIG_...)` line ties the Kconfig symbol to the corresponding composite object. The generic helper can build independently, while SoC modules depend on it through Kconfig.

State and persistence: no runtime state; it affects build artifacts and module names.

Dependencies/integration: consumes the symbols defined in `imx/Kconfig` and exports modules used by platform-driver matching.

Risks and test signals: verify all five Kconfig symbols produce the expected module names, especially when built as modules. Formatting uses tabs/spaces inconsistently but is functionally harmless.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/imx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx.c

Purpose: shared i.MX interconnect provider implementation. It converts SoC topology descriptions into interconnect nodes, optionally programs NoC priority registers, and maps bandwidth votes to `dev_pm_qos` minimum-frequency requests on the NoC or DDR controller devices.

Important APIs/types/functions: exported lifecycle functions are `imx_icc_register()` and `imx_icc_unregister()`. Private functions include `imx_icc_node_set()`, `imx_icc_set()`, `imx_icc_node_init_qos()`, `imx_icc_node_add()`, `imx_icc_register_nodes()`, and cleanup helpers. `struct imx_icc_node` stores descriptor, NoC setting, QoS device/request, and provider backpointer.

Control flow: a SoC driver passes node descriptors and optional NoC settings. Registration allocates onecell data indexed by node ID, initializes provider callbacks, maps the NoC register base when settings are present, creates nodes, initializes optional PM QoS requests, creates links, and registers the provider. On votes, `imx_icc_set()` applies source and destination nodes; each node can program fixed NoC priority/mode registers and update a frequency QoS request derived from `(avg + peak) * bw_mul / bw_div`.

State and persistence: per-node data is devm-allocated, but active PM QoS requests and core nodes are explicitly removed. `noc_base` persists in `struct imx_icc_provider`. Votes persist as interconnect node aggregate state and PM QoS constraints until changed or removed.

Dependencies/integration: depends on OF phandles such as `fsl,ddrc`, platform devices, MMIO access, PM QoS, and the generic interconnect core.

Risks and test signals: test deferred probe for missing QoS devices, disabled phandle targets, NoC mapping failure, duplicate node IDs, `S32_MAX` frequency overflow, unsupported NoC modes, and cleanup after partial registration. The missing `get_device()` before `put_device(node_data->qos_dev)` is worth lifetime review for non-parent QoS devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx.h -->
# sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx.h

Purpose: shared type, register, and topology macro contract for the i.MX interconnect drivers.

Important APIs/types/functions: defines NoC priority/mode register offsets, priority masks, mode constants, `IMX_ICC_MAX_LINKS`, `struct imx_icc_provider`, `struct imx_icc_node_adj_desc`, `struct imx_icc_node_desc`, and `struct imx_icc_noc_setting`. Macros `DEFINE_BUS_INTERCONNECT()`, `DEFINE_BUS_MASTER()`, and `DEFINE_BUS_SLAVE()` build SoC node tables. Prototypes expose `imx_icc_register()` and `imx_icc_unregister()`.

Control flow: declarative SoC files use the macros to describe masters, slaves, interconnect nodes, optional adjustment descriptors, and links. `imx.c` consumes those structures at probe.

State and persistence: no runtime state is allocated here, but struct layouts define persistent provider, node descriptor, adjustment, and NoC setting data used by all i.MX drivers.

Dependencies/integration: includes kernel argument-counting, bit, type, and interconnect provider headers.

Risks and test signals: test that macro argument counts never exceed `IMX_ICC_MAX_LINKS`, NoC register constants match hardware manuals, and all SoC node IDs are suitable for onecell array indexing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx8mm.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx8mm.c

Purpose: i.MX8MM topology driver. It describes a simplified bus graph for NOC, DRAM, OCRAM, A53, VPU, GPU, display/MIPI, HSIO, audio, Ethernet, SDMA, NAND, and USDHC paths.

Important APIs/types/functions: `imx8mm_dram_adj` and `imx8mm_noc_adj` define bandwidth-to-frequency scaling with divisor 16. The `nodes[]` table uses i.MX8MM binding IDs and `DEFINE_BUS_*` macros. `imx8mm_icc_probe()` calls `imx_icc_register()` without NoC register settings.

Control flow: the platform driver named `imx8mm-interconnect` registers on probe and delegates remove to `imx_icc_unregister()`. Runtime bandwidth votes are handled by the shared helper through PM QoS for adjustable NOC/DRAM nodes.

State and persistence: topology descriptors are static. Runtime state is allocated by `imx.c`; this file contributes node names, IDs, links, and adjustment coefficients.

Dependencies/integration: depends on `dt-bindings/interconnect/imx8mm.h`, the generic i.MX helper, and platform device registration.

Risks and test signals: validate all binding IDs fit the onecell data size, paths from every master to DRAM/OCRAM traverse as intended, and `fsl,ddrc` phandle behavior for DRAM scaling. This model intentionally merges/skips several PL301 NICs, so performance tests should compare representative multimedia, storage, and network loads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx8mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx8mn.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx8mn.c

Purpose: i.MX8MN topology driver for the generic i.MX interconnect helper. It models NOC, DRAM, OCRAM, A53, GPU, MIPI/display/camera/ISI, USB, audio, Ethernet, SDMA, NAND, USDHC, and main PL301 paths.

Important APIs/types/functions: adjustment descriptors use divisor 4 for DRAM and main NOC scaling. The `nodes[]` array is the source of node IDs, names, and links. `imx8mn_icc_probe()` passes this table to `imx_icc_register()`.

Control flow: platform-driver probe registers all nodes and links; removal uses shared unregister. No NoC priority settings are passed, so votes translate to standard aggregation and optional PM QoS updates only.

State and persistence: static node descriptors persist for module lifetime; provider, node, path, and PM QoS state live in `imx.c`.

Dependencies/integration: depends on `dt-bindings/interconnect/imx8mn.h`, module platform driver glue, and `icc_sync_state()` indirectly through the framework though this driver does not set a sync callback.

Risks and test signals: test camera/display and USB paths, scaling coefficients, missing DDRC phandle handling, and all IDs in `nodes[]` mapping into onecell data. The simplified topology should be validated against board-level bandwidth-sensitive workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx8mn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx8mp.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx8mp.c

Purpose: i.MX8MP topology and NoC priority-setting driver. It covers NOC, DRAM/OCRAM, A53, supermix/GIC/ML, audio/DSP/SDMA/EDMA, GPU, HDMI, HSIO, media, video, and PL301 main paths.

Important APIs/types/functions: `imx8mp_noc_adj` uses divisor 16. `noc_setting_nodes[]` provides register offsets, fixed priority levels, and optional external control flags for many masters; several interconnect nodes are marked `IMX_NOC_MODE_UNCONFIGURED`. `nodes[]` describes the graph and `imx8mp_icc_probe()` passes both nodes and settings to `imx_icc_register()`.

Control flow: registration maps the parent NoC MMIO resource because settings are present. On nonzero peak votes, `imx_icc_node_set()` writes fixed priority, mode, and external control values for configured nodes before applying optional PM QoS.

State and persistence: register settings are static descriptors; actual programmed priority/mode persists in hardware until changed or reset. Runtime state is owned by the shared i.MX provider.

Dependencies/integration: depends on `dt-bindings/interconnect/fsl,imx8mp.h`, MMIO mapping, and the common i.MX helper.

Risks and test signals: test MMIO mapping, every configured register offset, peak-zero behavior where priority programming is skipped, unsupported mode handling, and media/HDMI priority under high display/camera load. Array indexing by binding IDs means sparse or out-of-range IDs are high-risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx8mp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx8mq.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx8mq.c

Purpose: i.MX8MQ topology driver. It models NOC, DRAM/OCRAM, A53, VPU, GPU, DCSS, USB, display/CSI/LCDIF, audio, Ethernet, SDMA, NAND, USDHC, PCIe, and PL301 main paths.

Important APIs/types/functions: DRAM and NOC adjustment descriptors use divisor 4. The `nodes[]` table uses i.MX8MQ binding IDs. The platform driver sets `.sync_state = icc_sync_state`, unlike most neighboring i.MX topology files.

Control flow: `imx8mq_icc_probe()` registers the node table without NoC settings. During runtime, shared callbacks aggregate votes and update PM QoS where adjustment descriptors are present. Device sync-state eventually clears initial bandwidth floors in the core.

State and persistence: static topology remains for module lifetime; runtime provider/node/PM QoS state is maintained by `imx.c` and the core.

Dependencies/integration: depends on `dt-bindings/interconnect/imx8mq.h`, platform device matching, and generic i.MX helper exports.

Risks and test signals: test sync-state interaction, all master-to-memory paths, PCIe and display path correctness, DDRC phandle probe ordering, and behavior when the simplified PL301 topology hides hardware detail needed by a workload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/imx/imx8mq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/internal.h -->
# sources/distributed-fs/ceph-client/drivers/interconnect/internal.h

Purpose: private interconnect framework header shared by core and debug/test code. It defines the internal representation of per-consumer requests and resolved paths.

Important APIs/types/functions: `struct icc_req` records a request hlist node, target `icc_node`, consumer device, enabled flag, tag, average bandwidth, and peak bandwidth. `struct icc_path` stores a path name, hop count, and flexible array of requests. It also declares internal `icc_get()` and `icc_debugfs_client_init()`.

Control flow: `core.c` allocates `struct icc_path` with one request per hop and attaches each request to the corresponding node's `req_list`; aggregation later walks those lists. Debugfs client and KUnit use the internal name-based API or structures.

State and persistence: these structures are the persistent per-path state between `icc_get()` and `icc_put()`. The request hlist entries are live global aggregation inputs while attached.

Dependencies/integration: relies on definitions from interconnect provider headers included by users before or alongside this header.

Risks and test signals: changing layout affects the core, tests, and debugfs client. Test counted flexible-array allocation, hlist attach/detach, tag propagation, disabled request aggregation, and cleanup after failed path creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/Kconfig

Purpose: Kconfig menu for MediaTek interconnect support, especially DVFSRC-backed External Memory Interface bandwidth voting.

Important APIs/types/functions: symbols are `INTERCONNECT_MTK`, `INTERCONNECT_MTK_DVFSRC_EMI`, `INTERCONNECT_MTK_MT8183`, `INTERCONNECT_MTK_MT8195`, and `INTERCONNECT_MTK_MT8196`. The base symbol depends on `ARCH_MEDIATEK || COMPILE_TEST`; the EMI helper depends on `INTERCONNECT_MTK && MTK_DVFSRC`; SoC symbols depend on the EMI helper.

Control flow: build configuration decides whether the common EMI provider and per-SoC topology platform drivers are available. SoC modules call `mtk_emi_icc_probe()` and `mtk_emi_icc_remove()`.

State and persistence: Kconfig selections persist in `.config` and determine compile/link behavior.

Dependencies/integration: integrates with MediaTek DVFSRC support and the directory Makefile.

Risks and test signals: verify dependency behavior when `MTK_DVFSRC` is modular or absent, and test each SoC symbol independently against the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/Makefile -->
# sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/Makefile

Purpose: object mapping for MediaTek interconnect modules.

Important APIs/types/functions: `icc-emi.o` is built for `CONFIG_INTERCONNECT_MTK_DVFSRC_EMI`; `mt8183.o` and `mt8195.o` are tied to their SoC symbols.

Control flow: make conditionals translate Kconfig selections into compiled objects.

State and persistence: no runtime state; affects kernel build outputs.

Dependencies/integration: consumes symbols from `mediatek/Kconfig`.

Risks and test signals: the file maps `mt8196.o` to `CONFIG_INTERCONNECT_MTK_MT8195` instead of `CONFIG_INTERCONNECT_MTK_MT8196`. That looks like a build-selection bug: MT8196 may not build when only its own symbol is enabled, and enabling MT8195 may compile an extra unrelated driver. Test with `CONFIG_INTERCONNECT_MTK_MT8196=m` and `CONFIG_INTERCONNECT_MTK_MT8195=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/icc-emi.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/icc-emi.c

Purpose: common MediaTek EMI interconnect provider. It registers SoC-described nodes and translates bandwidth aggregates into DVFSRC requests for normal peak/average memory bandwidth or high-real-time bandwidth.

Important APIs/types/functions: exports `mtk_emi_icc_probe()` and `mtk_emi_icc_remove()`. Provider callbacks are `mtk_emi_icc_aggregate()` and `mtk_emi_icc_set()`. `mtk_emi_icc_aggregate()` stores running sum average and max peak in the destination node data.

Control flow: probe obtains the matched `struct mtk_icc_desc`, allocates an interconnect provider and onecell table, creates each non-NULL SoC node, adds links, registers the provider, and stores it as driver data. On set, endpoint type 1 sends `MTK_DVFSRC_CMD_PEAK_BW` then `MTK_DVFSRC_CMD_BW`; endpoint type 2 sends `MTK_DVFSRC_CMD_HRT_BW`; endpoint 0 is an internal hop.

State and persistence: SoC node objects are static but their `sum_avg` and `max_peak` fields are mutable aggregate state. Provider nodes persist until remove deregisters and removes nodes.

Dependencies/integration: depends on MediaTek DVFSRC, OF match data, onecell xlate, and interconnect core.

Risks and test signals: test overflow saturation in aggregation, DVFSRC error propagation, unknown endpoint handling, missing node holes in onecell arrays, link creation return values, and removal with active paths. The code does not check `icc_link_create()` failures in the loop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/icc-emi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/icc-emi.h -->
# sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/icc-emi.h

Purpose: shared MediaTek EMI interconnect data contract.

Important APIs/types/functions: `struct mtk_icc_node` defines node name, endpoint type, ID, aggregate state (`sum_avg`, `max_peak`), and a flexible array of link IDs. `struct mtk_icc_desc` points to a node pointer array and node count. Prototypes expose common probe/remove helpers.

Control flow: per-SoC files instantiate static `mtk_icc_node` objects and a descriptor. `icc-emi.c` consumes those descriptors at platform probe.

State and persistence: aggregate bandwidth fields live inside the static node structures, so they persist for the module lifetime and are reset by aggregation passes rather than by allocation.

Dependencies/integration: requires platform-device declarations through including C files and interconnect core types indirectly.

Risks and test signals: test flexible array initializers for each node, endpoint semantics, and reuse of static mutable aggregate fields across remove/reprobe cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/icc-emi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/mt8183.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/mt8183.c

Purpose: MT8183 EMI topology driver. It describes DDR EMI plus CPU, GPU, multimedia, VPU, display, video decode/encode, camera, image, and MDP masters.

Important APIs/types/functions: static `mtk_icc_node` objects encode endpoint type, binding ID, and links. `mt8183_emi_icc_nodes[]` maps binding IDs to node pointers, and `mt8183_emi_icc` is passed as OF match data for compatible `mediatek,mt8183-emi`.

Control flow: platform-driver probe/remove are the common `mtk_emi_icc_probe()` and `mtk_emi_icc_remove()`. Runtime votes traverse master nodes through MMSYS or directly to `SLAVE_DDR_EMI`, where endpoint type 1 sends DVFSRC bandwidth commands.

State and persistence: topology is static; aggregate fields in node structs mutate as votes change.

Dependencies/integration: depends on `dt-bindings/interconnect/mediatek,mt8183.h`, DVFSRC EMI helper, and framework sync-state callback.

Risks and test signals: validate all multimedia paths aggregate at `mmsys`, direct CPU/GPU paths reach DDR EMI, binding array indexes are complete, and sync-state clears initial constraints. Test real display/video/camera bandwidth votes against DVFSRC requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/mt8183.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/mt8195.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/mt8195.c

Purpose: MT8195 EMI topology driver. It extends the basic DDR EMI graph with VPU, MDLA, UFS, PCIe, USB, Wi-Fi, Bluetooth, NETSYS, debug, and a separate high-real-time DDR EMI path for multimedia HRT clients.

Important APIs/types/functions: `mt8195_emi_icc_nodes[]` maps many binding IDs to static `mtk_icc_node` objects. Endpoint type 1 is normal DDR EMI; endpoint type 2 is `hrt-ddr-emi` for HRT bandwidth. The OF compatible is `mediatek,mt8195-emi`.

Control flow: common EMI probe registers nodes and links. Normal masters route to `SLAVE_DDR_EMI` directly or through subsystem nodes, while HRT multimedia/debug nodes route to `SLAVE_HRT_DDR_EMI` and therefore generate `MTK_DVFSRC_CMD_HRT_BW`.

State and persistence: static topology and mutable aggregate fields persist for module lifetime.

Dependencies/integration: depends on MT8195 interconnect binding IDs, DVFSRC helper, and `icc_sync_state`.

Risks and test signals: test normal and HRT votes independently, sparse node array handling, multimedia aggregation through HRT MMSYS, and all peripheral direct-to-DDR paths. Cross-check that the Makefile builds this file without unintentionally masking MT8196 coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/mt8195.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/mt8196.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/mt8196.c

Purpose: MT8196 EMI topology driver. It models DDR EMI, multiple MCU ports, GPU, multimedia, VPU, MDLA, storage, PCIe, USB, wireless/network/debug masters, plus HRT DDR paths including ADSP.

Important APIs/types/functions: static `mtk_icc_node` entries map MT8196 binding IDs into `mt8196_emi_icc_nodes[]`; `mt8196_emi_icc` is matched by compatible `mediatek,mt8196-emi`. Endpoint type 1 handles normal DDR bandwidth and endpoint type 2 handles HRT bandwidth.

Control flow: common probe/remove register the provider. Votes from masters route through subsystem nodes such as MMSYS, VPUSYS, MDLASYS, or HRT MMSYS to one of the DDR endpoints, where the shared EMI set callback sends DVFSRC requests.

State and persistence: topology descriptors are static; per-node aggregate values are mutable and persist until reset by aggregation or module unload.

Dependencies/integration: depends on `dt-bindings/interconnect/mediatek,mt8196.h`, the common EMI helper, DVFSRC, and sync-state.

Risks and test signals: test all five MCU ports, HRT ADSP, PCIe binding differences from MT8195, and sparse array holes. The adjacent Makefile currently appears to gate `mt8196.o` on the MT8195 config symbol, so MT8196 build coverage is a key test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/mt8196.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/Kconfig

Purpose: Kconfig menu for Qualcomm interconnect providers, covering legacy SMD RPM NoC drivers, RPMh NoC drivers, BCM voter support, OSM L3, and many SoC-specific topology modules.

Important APIs/types/functions: key shared symbols are `INTERCONNECT_QCOM`, `INTERCONNECT_QCOM_BCM_VOTER`, `INTERCONNECT_QCOM_RPMH_POSSIBLE`, `INTERCONNECT_QCOM_RPMH`, and `INTERCONNECT_QCOM_SMD_RPM`. The listed SoC symbols select the appropriate RPMh or SMD RPM helper and, for RPMh, BCM voter support.

Control flow: this file determines which topology C files and helper modules are built. `INTERCONNECT_QCOM_RPMH_POSSIBLE` constrains compile-test/built-in combinations to avoid link failures when RPMh or command DB are modular.

State and persistence: kernel configuration state controls built-in/module availability and compatible matching at runtime.

Dependencies/integration: integrates with QCOM RPMh, command DB, SMD RPM, OF, and architecture dependencies.

Risks and test signals: test build matrices for RPMh built-in versus module combinations, COMPILE_TEST, and each SoC symbol. There are minor help-text typos, but the main risk is dependency drift causing unresolved symbols or missing BCM voter selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/Makefile

Purpose: Qualcomm interconnect build map. It defines composite object names for common helpers, BCM voter, RPMh topologies, SMD RPM topologies, OSM L3, and the SMD RPM helper bundle.

Important APIs/types/functions: `interconnect_qcom-y := icc-common.o`; `icc-bcm-voter-objs := bcm-voter.o`; `icc-smd-rpm-objs := smd-rpm.o icc-rpm.o icc-rpm-clocks.o`; many `qnoc-*-objs` map SoC topology files. `obj-$(CONFIG_...)` lines attach Kconfig symbols to those objects.

Control flow: make conditionals compile the helper and topology modules selected by Kconfig. RPMh topologies link against `icc-rpmh.o`; legacy SMD RPM topologies link against `icc-rpm.o` and clock resources.

State and persistence: no runtime state, but module composition affects symbol visibility and probe availability.

Dependencies/integration: consumes the large Qualcomm Kconfig symbol set and exports modules named by platform drivers.

Risks and test signals: test that new Kconfig entries have matching object definitions and `obj-*` lines. Note `icc-rpmh-obj` is singular and not a standard composite-object variable name; since `obj-$(CONFIG_INTERCONNECT_QCOM_RPMH) += icc-rpmh.o` can still build `icc-rpmh.o` directly, verify this is intentional and not a typo for `icc-rpmh-objs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/bcm-voter.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/bcm-voter.c

Purpose: RPMh Bus Clock Manager voter support for Qualcomm interconnect providers. It aggregates BCM votes from provider nodes, converts them into TCS commands, and writes active/wake/sleep RPMh batches.

Important APIs/types/functions: `struct bcm_voter` tracks the RPMh device, DT node, lock, commit list, wake/sleep list, and bucket wait mask. Exports are `of_bcm_voter_get()`, `qcom_icc_bcm_voter_add()`, and `qcom_icc_bcm_voter_commit()`. Helpers include `bcm_aggregate_mask()`, `bcm_aggregate()`, `tcs_cmd_gen()`, and `tcs_list_gen()`.

Control flow: providers get a voter by matching a `qcom,bcm-voters` phandle to probed `qcom,bcm-voter` devices. Dirty BCMs are queued on commit and wake/sleep lists. Commit aggregates each BCM, sorts by VCD, writes ACTIVE_ONLY commands, then optionally writes WAKE_ONLY and SLEEP commands for BCMs whose wake and sleep votes differ.

State and persistence: global `bcm_voters` persists probed voters. Per-voter lists persist across commits; `ws_list` intentionally keeps BCMs until wake and sleep requirements converge. BCM vote arrays and command DB-derived aux data live in provider BCM structures.

Dependencies/integration: depends on RPMh, TCS command format, command DB data from `icc-rpmh`, DT phandles, and list sorting.

Risks and test signals: test batching around VCD boundaries and `MAX_RPMH_PAYLOAD`, vote saturation to `BCM_TCS_CMD_VOTE_MASK`, keepalive and enable-mask BCMs, wake/sleep deltas, `qcom,tcs-wait`, missing voter probe deferral, and concurrent commits. Probe has no remove path, so device unbind assumptions should be reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/bcm-voter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/bcm-voter.h -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/bcm-voter.h

Purpose: public local header for Qualcomm RPMh BCM voter helpers.

Important APIs/types/functions: forward-facing prototypes are `of_bcm_voter_get()`, `qcom_icc_bcm_voter_add()`, and `qcom_icc_bcm_voter_commit()`. It includes command DB, RPMh, TCS, and `icc-rpmh.h` definitions so callers can pass `struct qcom_icc_bcm`.

Control flow: RPMh topology/provider code includes this header to acquire a voter, queue BCMs after aggregation, and flush votes to hardware.

State and persistence: no state is declared here, but the API manipulates persistent voter lists and BCM vote arrays owned by `bcm-voter.c` and RPMh providers.

Dependencies/integration: couples RPMh interconnect providers to Qualcomm SoC RPMh infrastructure.

Risks and test signals: compile-test include ordering, symbol export availability for modules, and ABI drift with `struct qcom_icc_bcm` in `icc-rpmh.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/bcm-voter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/eliza.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/eliza.c

Purpose: RPMh topology driver for Qualcomm Eliza NoC fabrics. It declares nodes, links, BCM groups, provider descriptors, and compatible strings for Eliza fabric blocks such as aggre NoCs, CNOC, GEM_NOC, LPASS, memory controller virtual fabric, MMSS, NSP, PCIe, and system NoC.

Important APIs/types/functions: the file is mostly static `struct qcom_icc_node`, `struct qcom_icc_bcm`, node arrays, BCM arrays, and `struct qcom_icc_desc` descriptors. `qnoc_of_match[]` maps `qcom,eliza-*` compatibles to descriptors. The platform driver uses `qcom_icc_rpmh_probe()` and `qcom_icc_rpmh_remove()`.

Control flow: core init registers the platform driver early. On matching a fabric DT node, the RPMh helper consumes the descriptor, initializes BCMs, creates interconnect nodes/links, sets up optional QoS register access, and registers the provider. Consumer votes later flow through RPMh aggregate/set callbacks and BCM voter commits.

State and persistence: topology and BCM descriptors are static. Runtime aggregate vote arrays inside nodes/BCMs persist while the provider is bound. Keepalive and enable-mask BCMs preserve minimum or on/off votes.

Dependencies/integration: depends on `dt-bindings/interconnect/qcom,eliza-rpmh.h`, `icc-rpmh.h`, BCM voter support, command DB, RPMh, and device sync-state.

Risks and test signals: test every compatible descriptor, BCM command DB lookup, QoS-required clock handling on aggre/PCIe fabrics, large fanout links such as config nodes, and wake/sleep vote behavior. Since the file is declarative, binding ID mismatches, NULL holes, wrong bus widths/channels, or BCM membership errors are the main failure modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/eliza.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/glymur.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/glymur.c

Purpose: RPMh topology driver for Qualcomm Glymur and Mahua NoC fabrics. It describes a large multi-fabric topology including aggre NoCs, CNOC, HSCNOC, LPASS, MC virtual, MMSS, NSINOC, NSP, OOBM, east/west PCIe fabrics, and system NoC.

Important APIs/types/functions: static `qcom_icc_node` and `qcom_icc_bcm` objects define topology and BCM voting groups. Many descriptors include `regmap_config` for QoS registers and some set `.qos_requires_clocks`. `glymur_qnoc_probe()` adjusts shared static topology fields for Mahua-compatible variants before delegating to `qcom_icc_rpmh_probe()`.

Control flow: the platform driver is registered at core init. Probe optionally patches channels, bus widths, or node array entries for Mahua variants, then the RPMh helper registers nodes/BCMs/provider state. Runtime votes aggregate per bucket and commit through BCM voter RPMh batches.

State and persistence: topology data is static and mutable for Mahua adjustments. That mutation persists after the first matching probe, which is important if multiple compatible variants could coexist. Runtime votes live in node and BCM aggregate arrays until provider removal or reaggregation.

Dependencies/integration: depends on `dt-bindings/interconnect/qcom,glymur-rpmh.h`, `linux/property.h` device compatibility checks, RPMh provider helpers, BCM voter, command DB, and sync-state.

Risks and test signals: test Glymur and every Mahua override path, especially NULLing PCIe 3A/WLAN nodes and changing channel/buswidth fields. Because static data is patched in place, test reprobe and multiple fabric instances. Also validate regmap ranges, QoS clock requirements, BCM membership, keepalive/enable-mask votes, and all compatible-to-descriptor mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/glymur.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-common.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-common.c

Purpose: small Qualcomm common helper for extended OF translation. It lets Qualcomm interconnect bindings carry an optional tag argument in addition to the onecell node index.

Important APIs/types/functions: `qcom_icc_xlate_extended()` is exported. It calls `of_icc_xlate_onecell()`, allocates `struct icc_node_data`, stores the translated node, and copies `spec->args[1]` into `ndata->tag` when two arguments are present.

Control flow: providers assign this function to `provider->xlate_extended`. The core calls it from `of_icc_get_from_provider()`, then applies the tag to the created path only when source and destination tags match.

State and persistence: each call allocates transient `icc_node_data` freed by the core after path creation. No module-global state exists.

Dependencies/integration: depends on OF phandle args, onecell translation, dynamic allocation, and Qualcomm providers that support tagged buckets.

Risks and test signals: test one-argument and two-argument phandles, too many arguments warning, allocation failure, invalid onecell index, and tag mismatch behavior in the core path builder.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-common.h -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-common.h

Purpose: local Qualcomm common header exposing extended interconnect OF translation.

Important APIs/types/functions: declares `qcom_icc_xlate_extended()` and includes `linux/interconnect-provider.h` for `struct icc_node_data` and `struct of_phandle_args` context.

Control flow: SMD RPM and RPMh Qualcomm provider implementations include this header and assign the function to their provider before registration.

State and persistence: no state is owned.

Dependencies/integration: keeps Qualcomm provider files decoupled from the implementation in `icc-common.c`.

Risks and test signals: compile-test all Qualcomm provider objects for prototype drift and exported symbol availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-rpm-clocks.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-rpm-clocks.c

Purpose: shared SMD RPM bus clock resource descriptors for legacy Qualcomm interconnect drivers.

Important APIs/types/functions: exports `struct rpm_clk_resource` constants for aggregate clocks, BIMC/memory clocks, bus clocks, MMAXI, QUP, and branch variants. Each descriptor stores RPM resource type, clock ID, and optional branch flag.

Control flow: topology descriptors in legacy RPM drivers reference these constants. `icc-rpm.c` later passes them to `qcom_icc_rpm_set_bus_rate()` when aggregate or node-specific rates change.

State and persistence: descriptors are const static module data and hold no runtime state.

Dependencies/integration: depends on Qualcomm SMD RPM resource IDs from `linux/soc/qcom/smd-rpm.h` and the struct definition in `icc-rpm.h`.

Risks and test signals: test exported symbols under module builds, correct resource type/ID pairs for each SoC topology, and branch-clock semantics where RPM expects boolean enable-style rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-rpm-clocks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-rpm.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-rpm.c

Purpose: common legacy Qualcomm SMD RPM interconnect provider. It registers topology nodes, programs AP-owned QoS registers, aggregates tagged active/sleep bandwidth, sends RPM master/slave bandwidth votes, and scales RPM-owned or CCF-owned bus clocks.

Important APIs/types/functions: exported lifecycle functions are `qnoc_probe()` and `qnoc_remove()`. Key helpers include QoS writers for QNOC/BIMC/NoC, `qcom_icc_rpm_set()`, `qcom_icc_pre_bw_aggregate()`, `qcom_icc_bw_aggregate()`, `qcom_icc_calc_rate()`, `qcom_icc_bus_aggregate()`, and provider callback `qcom_icc_set()`.

Control flow: probe waits for SMD RPM, reads matched `qcom_icc_desc`, allocates provider state and onecell data, maps optional QoS regmap, enables bus/interface clocks for safe register access, creates nodes and links, applies AP-owned QoS once, disables interface clocks, registers the provider, and populates child NoC devices. At vote time, aggregate state is converted to active/sleep RPM votes and bus clock rates, with cached bus rates avoiding duplicate RPM sends.

State and persistence: `struct qcom_icc_provider` stores regmap, bus clock descriptors, cached bus rates, interface clocks, keepalive, and ignore-ENXIO policy. Each `qcom_icc_node` stores mutable per-state `sum_avg`, `max_peak`, and node bus clock caches.

Dependencies/integration: depends on SMD RPM helper functions, regmap/MMIO, CCF clocks, OF child population, extended Qualcomm xlate tags, and interconnect core callbacks.

Risks and test signals: test RPM unavailability deferral, AP-owned QoS programming with clocks enabled, rollback on node creation/QoS failure, child population failure cleanup, active/sleep tag aggregation, keepalive minimum rate, bus clock cache correctness, `ignore_enxio` handling, and missing link-create errors. The assignment to a devm-allocated `bus_clk_desc` is redundant before overwriting with the const descriptor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-rpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-rpm.h -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-rpm.h

Purpose: shared data contract for legacy Qualcomm SMD RPM interconnect drivers.

Important APIs/types/functions: defines RPM bus master/slave request IDs, `enum qcom_icc_type`, `struct rpm_clk_resource`, `struct qcom_icc_provider`, `struct qcom_icc_qos`, `struct qcom_icc_node`, and `struct qcom_icc_desc`. It declares exported clock resources, `qnoc_probe()`, `qnoc_remove()`, and low-level RPM send helpers.

Control flow: SoC topology files instantiate `qcom_icc_node` arrays and `qcom_icc_desc` descriptors. `icc-rpm.c` uses the descriptor to build providers, program QoS, aggregate requests, and send RPM/clock votes.

State and persistence: provider and node structs define all persistent runtime fields for legacy RPM operation, including cached per-state bus clock rates and aggregate bandwidth arrays.

Dependencies/integration: includes SMD RPM, dt-bindings for RPM ICC tags/states, clocks, interconnect provider APIs, and platform devices.

Risks and test signals: compile-test all legacy Qualcomm topologies for struct initializer drift, validate coefficient defaults, buswidth/channels nonzero for rate math, RPM ID values, and tag bit compatibility with `QCOM_SMD_RPM_STATE_NUM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/icc-rpm.h -->
