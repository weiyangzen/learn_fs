# subset-b-004229 research: sources/distributed-fs/ceph-client/drivers/memory/tegra

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra124.c -->
## sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra124.c

### Purpose
This file is the Tegra124/Tegra132 memory-controller SoC description consumed by the common Tegra MC driver. It enumerates memory clients, SMMU software groups, grouped DRM SMMU policy, reset controls, interrupt masks, and interconnect aggregation behavior. There is no standalone platform driver here; the exported `tegra124_mc_soc` and `tegra132_mc_soc` structures are selected by the common MC match table when the corresponding SoC config is enabled.

### Important APIs, Types, And Functions
The core data objects are `tegra124_mc_clients`, `tegra124_swgroups`, `tegra124_groups`, `tegra124_mc_resets`, `tegra124_smmu_soc`, `tegra132_smmu_soc`, `tegra124_mc_intmasks`, `tegra132_mc_intmasks`, `tegra124_mc_soc`, and `tegra132_mc_soc`. Client entries map numeric memory-client IDs to names, SMMU enable bits, latency-allowance register fields, and SWGROUP IDs. Reset entries are created with `TEGRA124_MC_RESET()` and use common reset ops. ICC hooks are `tegra124_mc_of_icc_xlate_extended()`, `tegra124_mc_icc_aggreate()`, and `tegra124_mc_icc_set()`.

### Control Flow
At probe time the common MC driver reads the selected `struct tegra_mc_soc`, creates memory-client ICC nodes, configures interrupt masks, and exposes resets using this file's static tables. ICC translation looks up the requested client ID among provider nodes. If the client exists but its ICC node has not been created yet, translation returns `-EPROBE_DEFER`; unknown IDs are logged and rejected with `-EINVAL`. Display, display-B, PTC, and VI clients are tagged isochronous by default. Aggregation sums average bandwidth and uses the maximum peak bandwidth, scaling isochronous peak requests by 400 percent. The `set` hook is a stub that returns success with a TODO for PTSA programming.

### State And Persistence
The file itself maintains no runtime state. State is stored by the common MC/SMMU/ICC layers using these constant descriptors: hardware registers hold SMMU enables, latency allowances, interrupt masks, and reset state; ICC node data allocated by `kzalloc_obj()` is transient per translation. Configuration is rebuilt on driver probe and resume by common code, not persisted in this file.

### Dependencies And Integration Points
It depends on `mc.h`, `dt-bindings/memory/tegra124-mc.h`, the common Tegra MC register definitions (`tegra20_mc_regs`, `tegra30_mc_ops`, `tegra30_mc_irq_handlers`), common reset operations, the Tegra SMMU integration, and the Linux interconnect framework. The `CONFIG_ARCH_TEGRA_124_SOC` and `CONFIG_ARCH_TEGRA_132_SOC` blocks export separate SoC descriptors sharing the same client/reset/SMMU tables. Device tree interconnect specifiers must use memory-client IDs that match `tegra124_mc_clients`.

### Risks
The table is correctness-critical: wrong IDs, SMMU bits, reset bits, or latency-allowance shifts can break DMA isolation, reset sequencing, display/video throughput, or error attribution. The 400 percent ISO scaling is conservative but may over-reserve bandwidth. The `tegra124_mc_icc_set()` stub means bandwidth requests do not program PTSA knobs despite successful ICC votes, so performance behavior depends on boot defaults and other MC/EMC drivers. Array indexing in xlate uses `mc->soc->clients[idx]` after matching `node->id == idx`; this assumes client IDs are dense enough to index the clients array, which should be watched when adding sparse IDs.

### Test Signals
Useful validation signals are successful MC probe on Tegra124/Tegra132, SMMU client registration, reset-controller consumers toggling each reset, interrupt decode logs for DECERR/security/page faults, and ICC paths resolving for display/VI/PTC as ISO. Device-tree ABI tests should cover valid and invalid interconnect client IDs. Hardware smoke tests should exercise display, VIC, XUSB, SDMMC, SATA, GPU, and VDE DMA with SMMU enabled and verify no unexpected MC faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra124.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra186-emc.c -->
## sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra186-emc.c

### Purpose
This file implements the Tegra186-family External Memory Controller platform driver used on Tegra186, Tegra194, Tegra234, and Tegra264 compatibles. It acquires BPMP and EMC clocks, optionally queries BPMP for EMC DVFS latency pairs, exposes debugfs rate controls, and registers an EMC-side interconnect provider that bridges MC bandwidth requests to the external memory node.

### Important APIs, Types, And Functions
`struct tegra186_emc` stores the BPMP handle, device, EMC and DBB clocks, DVFS table, debugfs limits, and ICC provider. `tegra186_emc_get_emc_dvfs_latency()` sends `MRQ_EMC_DVFS_LATENCY` through BPMP, converts firmware frequencies from kHz to Hz, computes min/max rates, sets the clock rate range, and creates debugfs files. `tegra186_emc_interconnect_init()` creates `TEGRA_ICC_EMC` and `TEGRA_ICC_EMEM` nodes, links EMC to EMEM, and registers the provider. Probe/remove are `tegra186_emc_probe()` and `tegra186_emc_remove()`.

### Control Flow
Probe allocates `tegra186_emc`, gets BPMP, gets the `emc` clock, optionally enables the `dbb` clock, stores driver data, and queries DVFS latency if BPMP advertises that MRQ. If the parent MC exists and has ICC ops, probe checks `MRQ_BWMGR_INT`; when supported, it marks `mc->bwmgr_mrq_supported`, stores the BPMP pointer in `mc->bpmp`, and uses a barrier before registering the EMC ICC provider. ICC registration happens even without BWMGR support so client paths exist, but later MC set hooks can fail cleanly. Remove deletes debugfs, clears `mc->bpmp`, and releases BPMP.

### State And Persistence
Persistent runtime state is held in `struct tegra186_emc` and in the parent `struct tegra_mc`: debugfs min/max reflect the last successfully applied limits, `dvfs` stores firmware-provided rates until device removal, `mc->bpmp` is borrowed from the EMC node for MC bandwidth requests, and `mc->bwmgr_mrq_supported` captures firmware capability. No state is saved across reboot; suspend behavior is delegated to clocks/firmware and there are no explicit PM callbacks here.

### Dependencies And Integration Points
The driver integrates with BPMP (`tegra_bpmp_get()`, `tegra_bpmp_transfer()`, `tegra_bpmp_mrq_is_supported()`), the Linux clock API, debugfs, of-platform child population under the parent MC, and the interconnect framework. It expects the parent device's driver data to be a `struct tegra_mc`. Its ICC aggregate callback is taken from `mc->soc->icc_ops`, while EMC `set` intentionally does nothing because BPMP bandwidth programming is performed by the MC provider for newer chips.

### Risks
The BPMP pointer sharing into `mc->bpmp` is a lifecycle-sensitive integration point; remove clears it, but concurrent ICC users depend on normal device lifetime ordering. Debugfs rate setters only accept exact DVFS rates, so firmware table changes directly affect user-visible control. If `MRQ_EMC_DVFS_LATENCY` returns zero pairs, min/max initialization would produce unusable rate limits. `tegra186_emc_interconnect_init()` removes nodes on failure but remove does not explicitly unregister the ICC provider, relying on provider/device lifetime conventions. Missing or wrong parent MC data can disable ICC setup or cause null assumptions in remove.

### Test Signals
Probe logs should show successful BPMP and clock acquisition, debugfs `/sys/kernel/debug/emc/available_rates` should list firmware rates, and min/max writes should reject invalid values and apply valid ones through `clk_set_min_rate()`/`clk_set_max_rate()`. ICC tests should verify EMC/EMEM nodes register even when `MRQ_BWMGR_INT` is unsupported, and MC bandwidth requests fail or pass according to firmware capability. Device removal or bind failure paths should be checked for BPMP release and debugfs cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra186-emc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra186.c -->
## sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra186.c

### Purpose
This file supplies Tegra186 memory-controller operations and the Tegra186 SoC descriptor. It handles MC register-region mapping for broadcast/channel access, populates child devices such as EMC, programs memory-client stream ID overrides for IOMMU integration, restores overrides on resume, and describes Tegra186 memory clients, interrupts, channels, and address geometry.

### Important APIs, Types, And Functions
`tegra186_mc_ops` provides `.probe`, `.remove`, `.resume`, and `.probe_device`. `tegra186_mc_probe()` maps the broadcast channel and per-channel register windows, with Tegra264-compatible handling for DTs where the SID region is absent and the first resource is already broadcast. `tegra186_mc_client_sid_override()` writes per-client SID override/security registers when firmware permits. `tegra186_mc_probe_device()` reads a device's IOMMU stream ID and interconnect phandles to program matching MC client SIDs. `tegra186_mc_resume()` reapplies default SIDs. `tegra186_mc_soc` exports the client table and MC capabilities.

### Control Flow
Common MC probe invokes `tegra186_mc_probe()`. The function identifies whether a named `sid` resource exists; if so it maps the named `broadcast` region, otherwise it reuses `mc->regs` as broadcast for newer layouts. It allocates and maps `ch0` through `ch3`, then calls `of_platform_populate()` so child EMC devices can bind. During device attachment, `probe_device` obtains the device stream ID via `tegra_dev_iommu_get_stream_id()` and scans `interconnects` entries. For entries targeting the MC node, it finds the matching client ID and writes the SID override. Resume loops over all clients and restores descriptor SIDs.

### State And Persistence
Runtime state includes mapped broadcast and channel register pointers in `struct tegra_mc`, per-client SID override register contents, populated child platform devices, and firmware lock bits in MC security registers. SID overrides are hardware state and must be restored after resume. The file does not allocate persistent private state beyond arrays managed by devm.

### Dependencies And Integration Points
It depends on `soc/tegra/mc.h`, `mc.h`, `dt-bindings/memory/tegra186-mc.h`, of-platform population, IOMMU APIs, and the common MC IRQ/error handling tables. The client table maps `TEGRA186_MEMORY_CLIENT_*` IDs to `TEGRA186_SID_*` values and SID override/security offsets. The SoC descriptor uses `tegra20_mc_regs` and `tegra30_mc_irq_handlers`, 40-bit addressing, four channels, `ch_intmask = 0x0000000f`, and global channel shift zero.

### Risks
SID programming depends on secure firmware policy. If the security register has write access disabled and no override enabled, Linux silently leaves the firmware configuration in place. The `WARN_ON()` in the path that tries to set `MC_SID_STREAMID_SECURITY_OVERRIDE` appears to warn on the condition it is about to fix, which can be noisy if reached. Device tree resource naming is critical: missing channel windows fail probe, while missing broadcast only degrades with a warning. Incorrect interconnect client IDs can leave devices with stale stream IDs and cause IOMMU faults or isolation gaps.

### Test Signals
Boot tests should verify MC probe maps all four channel windows and populates EMC children. IOMMU-enabled tests should confirm client devices with interconnects receive the expected SID override and continue DMA after suspend/resume. Negative tests include firmware-locked SID registers, absent broadcast resource, invalid interconnect client IDs, and channel MC faults decoded through common interrupt handling. `dmesg` should show no unexpected SID override warnings during normal boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra186.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra194.c -->
## sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra194.c

### Purpose
This file is the Tegra194 MC SoC data table. It enumerates Tegra194 memory clients, assigns stream IDs and SID override/security register offsets, defines MC interrupt masks, and exports `tegra194_mc_soc` for the common MC driver. It reuses the Tegra186 MC operations for probe, child population, SID override, and resume.

### Important APIs, Types, And Functions
The principal objects are `tegra194_mc_clients`, `tegra194_mc_intmasks`, and `tegra194_mc_soc`. There are no local functions. The client table covers legacy engines plus Tegra194-specific MIU, NVDLA, PVA, RCE, NVENC1, PCIe, NVDEC1, ISP/VI falcon, and additional read paths. Each client entry records a memory-client ID, a printable name, a `TEGRA194_SID_*` stream ID, and SID override/security offsets.

### Control Flow
At runtime the common MC driver selects `tegra194_mc_soc`, then uses `tegra186_mc_ops`. The inherited probe maps broadcast/channel windows and populates child devices. Device attachment and resume use the table entries here to program SID overrides. Interrupt decode is handled by the common Tegra30-style handlers with the Tegra194 mask, including route-sanity, generalized carveout, MTS, secure, VPR, security-violation, and EMEM decode errors.

### State And Persistence
This file contains only constant descriptors. Hardware state derived from it includes SID override register values, interrupt mask settings, channel register mapping behavior, and high-address error reporting. No file-local state persists; the common MC driver and hardware registers hold all runtime state. Resume behavior is inherited from Tegra186 and reprograms SIDs from this table.

### Dependencies And Integration Points
It depends on `dt-bindings/memory/tegra194-mc.h`, `soc/tegra/mc.h`, and `mc.h`. The SoC descriptor advertises 40-bit addressing, 16 MC channels, high address register support, `client_id_mask = 0xff`, `ch_intmask = 0x00000f00`, `global_intstatus_channel_shift = 8`, common `tegra_mc_icc_ops`, `tegra20_mc_regs`, and `tegra30_mc_irq_handlers`. Device tree interconnect IDs and IOMMU stream IDs must align with this table.

### Risks
The data table is large and manually maintained, so duplicate or incorrect SID offsets are the main risk. Some entries share offsets that may reflect hardware aliasing but should be reviewed carefully during updates. A wrong SID can route DMA through the wrong IOMMU context; a wrong client ID can make ICC, error logging, and SID override target the wrong engine. Because functionality is inherited from Tegra186, changes in `tegra186.c` affect Tegra194 behavior as well.

### Test Signals
Validation should include booting Tegra194 with IOMMU enabled, checking that PCIe, display, VIC, NVDEC/NVENC, NVDLA, PVA, XUSB, EQOS, SDMMC, and BPMP clients DMA without stream-ID faults, and verifying MC error reports identify the expected client names. Suspend/resume should preserve SID overrides. Device tree binding tests should ensure all interconnect client IDs used by peripherals exist in `tegra194_mc_clients`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra194.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra20-emc.c -->
## sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra20-emc.c

### Purpose
This file implements the Tegra20 External Memory Controller driver. It initializes EMC hardware, loads memory timing tables from device tree, coordinates EMC clock changes with timing-register programming, exposes debugfs rate controls, registers an EMC ICC provider, implements devfreq scaling through OPPs, reads LPDDR2 mode registers for memory identity, and reports refresh-overflow interrupts.

### Important APIs, Types, And Functions
`struct tegra_emc` is the main state container: device, MC pointer, ICC provider, clock notifier, EMC clock, MMIO base, timing table, debugfs limits, rate requests, devfreq governor data, LPDDR2 identity, and MRR error flag. Key functions include `emc_setup_hw()`, `tegra20_emc_find_node_by_ram_code()`, `tegra20_emc_load_timings_from_dt()`, `emc_prepare_timing_change()`, `emc_complete_timing_change()`, `tegra20_emc_clk_change_notify()`, `emc_request_rate()`, `emc_icc_set()`, `tegra20_emc_devfreq_target()`, `tegra20_emc_devfreq_get_dev_status()`, and `tegra20_emc_probe()`.

### Control Flow
Probe maps registers, verifies bootloader-selected DRAM auto-suspend mode, enables EMC/CAR clock-change handshake, configures interrupts/debug defaults, detects DRAM width/type/devices, and reads LPDDR2 JEDEC mode registers where applicable. It selects a timing-table node by RAM code or LPDDR2 identity, loads child timing entries, converts bus kHz to EMC Hz, and sorts them. It requests the IRQ, registers a Tegra clock round-rate callback and clock notifier, initializes OPPs, sets up debugfs, ICC, and devfreq, then pins the module loaded. Rate changes enter through devfreq, debugfs, or ICC; all converge on `emc_request_rate()` under `rate_lock`, which combines min/max constraints and calls `dev_pm_opp_set_rate()`. Clock notifier PRE writes timing shadow registers; POST waits for CAR handshake; ABORT restores old timing and forces update.

### State And Persistence
The driver persists timing data in devm memory, current min/max requests in `requested_rate[]`, debugfs limits, measured DRAM identity, and counters/timers managed by devfreq. Hardware state includes EMC timing registers, power/statistics counters, interrupt masks/status, MRR state, and clock rate. Timing tables are not persisted by the driver; they come from device tree each boot. `mrr_error` suppresses RAM-code timing selection if mode-register reads fail.

### Dependencies And Integration Points
It integrates with the Tegra clock driver via `tegra20_clk_set_emc_round_callback()` and clock notifiers, the OPP framework for voltage-aware rate changes, devfreq simple_ondemand, the interconnect framework, the common Tegra MC provider via `devm_tegra_memory_controller_get()`, JEDEC LPDDR2 helpers, and device tree timing nodes compatible with `nvidia,tegra20-emc-table`. ICC receives EMEM bandwidth votes and converts peak/average bytes per second to an EMC clock floor using detected DRAM bus width.

### Risks
Clock/timing ordering is sensitive: incorrect timing tables or notifier failures can destabilize memory. Timing lookup picks the first table with rate greater than or equal to the target, so table sorting and full rate coverage are essential. `emc_request_rate()` applies OPP rate to the aggregate minimum, not directly to the requested rate, so conflicting debug/devfreq/ICC min/max values can return `-ERANGE`. MRR timeouts mark `mrr_error` and skip memory-timing selection. Devfreq statistics depend on counter semantics and a low threshold. Probe ignores return values from ICC/devfreq init, so failures may be non-fatal but reduce functionality.

### Test Signals
Hardware validation should include boot with valid and missing timing tables, RAM-code matching, LPDDR2 identity matching, debugfs available/min/max rates, devfreq transitions, ICC bandwidth votes, suspend-like clock changes with abort paths, and refresh-overflow IRQ logging. OPP tests should confirm voltage changes precede higher EMC rates. Stress tests should run display/video/storage DMA while changing rates and should monitor MC/EMC error logs for decode, refresh, or timing failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra20-emc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra20.c -->
## sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra20.c

### Purpose
This file provides the Tegra20 MC SoC descriptor plus Tegra20-specific reset, interconnect aggregation, interrupt handling, and debugfs statistics collection. It is used by the common MC platform driver to expose memory clients, reset controls, ICC nodes, error interrupts, and a `stats` debugfs seqfile.

### Important APIs, Types, And Functions
Important data includes `tegra20_mc_clients`, `tegra20_mc_resets`, `tegra20_mc_reset_ops`, `tegra20_mc_icc_ops`, `tegra20_mc_irq_handlers`, `tegra20_mc_intmasks`, and `tegra20_mc_soc`. Reset functions are `tegra20_mc_hotreset_assert()`, `tegra20_mc_hotreset_deassert()`, `tegra20_mc_block_dma()`, `tegra20_mc_dma_idling()`, `tegra20_mc_unblock_dma()`, and `tegra20_mc_reset_status()`. ICC functions are `tegra20_mc_of_icc_xlate_extended()`, `tegra20_mc_icc_aggreate()`, and `tegra20_mc_icc_set()`. Statistics functions build two hardware gatherers at a time and render per-client percentages in `tegra20_mc_stats_show()`.

### Control Flow
Common MC probe consumes `tegra20_mc_soc` and calls `tegra20_mc_probe()`, which adds the debugfs `stats` seqfile. Reset operations block DMA, poll idle status, assert/deassert hotreset, and unblock DMA by manipulating per-reset control/status/reset registers under `mc->lock`. ICC xlate finds the requested client node, tags display and VI clients as ISO, and aggregation scales ISO peak bandwidth by 300 percent before passing requests up the ICC graph. Interrupt handling masks `MC_INTSTATUS` by the SoC interrupt mask, decodes EMEM decode errors, invalid GART pages, and security violations, logs client/direction/address details, and clears handled bits.

### State And Persistence
Most state is hardware-resident: reset bits, DMA block bits, interrupt status, and MC statistics counters. `tegra20_mc_stat_lock` serializes debugfs statistics gathering globally. The stats path allocates a temporary per-client array per read and samples counters for `MC_STAT_SAMPLE_TIME_USEC`. ICC node data is allocated per translation. No file-local persistent device state exists beyond constant descriptors and the global mutex.

### Dependencies And Integration Points
The file depends on Tegra20 memory DT bindings, common `mc.h`, debugfs seqfile support, the interconnect framework, and common MC names/error strings from `mc.c`. The SoC descriptor advertises 32-bit addressing, `client_id_mask = 0x3f`, Tegra20 register layout, Tegra20 reset ops, and Tegra20 interrupt handlers. The EMC driver consumes the MC ICC aggregation behavior when creating EMC-side ICC routes.

### Risks
The stats collector assumes paired clients and writes directly to shared MC gather registers, so concurrent readers are serialized but other firmware/kernel users of those counters could interfere. Interrupt handling indexes `mc->soc->clients[id]` from hardware-reported IDs; bad IDs could overrun if hardware reports outside `client_id_mask` assumptions. Reset ops must match hardware polarity exactly or DMA may remain blocked or reset may be inverted. ICC `set` is intentionally a no-op, leaving arbitration defaults unchanged.

### Test Signals
Tests should cover reset consumers for AVPC/DC/DCB/EPP/2D/HC/ISP/MPCORE/MPE/3D/PPCS/VDE/VI, debugfs `stats` output under active memory traffic, MC error interrupt injection or fault generation for GART/security/EMEM decode, ICC path creation for display and VI as ISO, and suspend/resume behavior through the common MC layer. A useful regression signal is stable DMA after repeated reset assert/deassert cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210-emc-cc-r21021.c -->
## sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210-emc-cc-r21021.c

### Purpose
This file implements the Tegra210 EMC clock-change sequence revision r21021. It is not a platform driver; it exports `tegra210_emc_r21021`, a `struct tegra210_emc_sequence` with callbacks for DVFS clock changes and periodic clock-tree compensation. The code programs EMC, MC, DRAM mode, calibration, DLL, ZQ, pad, and CCFIFO operations in a strict hardware-defined order.

### Important APIs, Types, And Functions
The exported object is `tegra210_emc_r21021`. The main callback is `tegra210_emc_r21021_set_clock()`. Periodic training uses `tegra210_emc_r21021_periodic_compensation()`, `periodic_compensation_handler()`, `tegra210_emc_get_clktree_delay()`, and `tegra210_emc_compare_update_delay()`. The PTFV macros maintain fixed-point moving averages for DQS oscillator-derived clock-tree delays. The sequence relies on helper APIs from `tegra210-emc-core.c` and `tegra210-emc.h`, including `emc_writel()`, `emc_channel_writel()`, `ccfifo_writel()`, `tegra210_emc_timing_update()`, `tegra210_emc_dll_prelock()`, `tegra210_emc_do_clock_change()`, and power ramp helpers.

### Control Flow
For periodic compensation, the code disables power optimizations, disables DLL, waits for channels to leave powerdown/self-refresh, samples DQSOSC MRR18/MRR19, updates moving averages, optionally writes compensated trim registers, restores EMC config, updates timing, and re-enables DLL. For a DVFS clock change, `set_clock()` computes source/destination periods and DRAM type, disables DLL/autocal/power features, optionally performs clock-tree compensation, prelocks or disables the DLL, prepares autocal, handles LPDDR4/LPDDR3/DDR3 special cases, writes burst/per-channel/vref/trim/MC latency registers, enters self-refresh through CCFIFO, ramps pads down, triggers the clock change, ramps pads up, exits self-refresh, issues MRWs/ZQ/refresh/QRST operations, restores ZCAL/EMC config/FDPD/autocal, and leaves `emc->last` update to the core caller.

### State And Persistence
The sequence mutates `emc->last`, `emc->next`, timing-table fields such as `ptfv_list` and current clock-tree values, a static `fsp_for_next_freq` toggle for LPDDR4 FSP selection, and many EMC/MC hardware registers. Moving averages and compensated clktree values persist in the selected timing structures while the driver is loaded. Hardware mode-register, DLL, pad, ZQ, self-refresh, autocal, and latency-allowance state changes persist until the next rate change or suspend/resume reprogramming.

### Dependencies And Integration Points
It depends on Tegra210 EMC register definitions and timing-table layout in `tegra210-emc.h`, MC register definitions in `tegra210-mc.h`, common core helpers from `tegra210-emc-core.c`, and the Tegra210 clock provider. The core selects this sequence when a reserved-memory timing table has revision `0x7`. The algorithm is tightly coupled to table indices such as `EMC_CFG_INDEX`, `EMC_ZCAL_INTERVAL_INDEX`, `EMC_MRW*`, trim arrays, burst MC arrays, and per-channel register offset tables.

### Risks
This is a high-risk hardware transaction: ordering, delays, and table fields are all critical to DRAM stability. Several loops wait for hardware conditions without timeout in DLL prelock-related helper paths outside this file's direct control. Static `fsp_for_next_freq` is global to the sequence, so multiple controllers would share it, though Tegra210 normally has one EMC instance. Unsupported or malformed timing tables can lead to wrong MRWs, pad ramps, ZQ timing, or trimmer compensation. Removed training sections mean correctness depends on pre-trained table values and periodic compensation.

### Test Signals
Tests must be hardware based: sweep every EMC OPP up and down under memory stress, exercise LPDDR4 and non-LPDDR4 paths where available, verify periodic training timer changes trim values only when margins are exceeded, and monitor for MC/EMC faults, data corruption, DLL lock warnings, and clock-change completion warnings. Thermal refresh transitions and suspend/resume should be tested in combination with DVFS because they select nominal/derated tables and invoke this sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210-emc-cc-r21021.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210-emc-core.c -->
## sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210-emc-core.c

### Purpose
This file is the Tegra210 EMC platform driver core. It maps EMC/MC/channel registers, attaches reserved-memory timing tables, selects a compatible clock-change sequence, registers with the Tegra210 EMC clock provider, exposes debugfs controls, manages thermal refresh derating, runs periodic training timers, implements suspend/resume, and provides helper functions used by the r21021 sequence.

### Important APIs, Types, And Functions
Key local data includes `tegra210_emc_sequences[]` and `tegra210_emc_table_register_offsets`, the offset map that translates timing-table arrays into register addresses. Driver entry points are `tegra210_emc_probe()`, `tegra210_emc_remove()`, `tegra210_emc_suspend()`, and `tegra210_emc_resume()`. Clock-provider integration is through `tegra210_emc_set_rate()`. Thermal/refresh control uses `tegra210_emc_set_refresh()`, `tegra210_emc_poll_refresh()`, and cooling-device ops. Exported helpers include `tegra210_emc_mrr_read()`, `tegra210_emc_do_clock_change()`, `tegra210_emc_find_timing()`, `tegra210_emc_wait_for_update()`, `tegra210_emc_timing_update()`, `tegra210_emc_compensate()`, DLL helpers, power ramp helpers, and `tegra210_emc_adjust_timing()`.

### Control Flow
Probe allocates state, gets the EMC clock and MC handle, maps base plus two channel windows, detects DRAM devices/type/channels, attaches nominal and optional derated reserved-memory EMC tables, validates monotonic rates/voltages, selects the current timing by the live EMC clock, picks the r21021 sequence by revision, builds Tegra clock configs from timing entries, attaches the EMC clock provider, initializes timers/debugfs, and registers a thermal cooling device. Rate changes from the clock framework validate the target timing and training status, enforce a minimum delay between changes, lock the EMC, call the selected sequence, update `clkchange_time` and `last`, then unlock. Refresh polling reads LPDDR MR4 temperature or a debug override and switches nominal, 2x, 4x, or throttle refresh.

### State And Persistence
`struct tegra210_emc` stores mapped registers, timing tables (`nominal`, `derated`, active `timings`, `last`, `next`), provider configs, refresh state, thermal/debugfs values, timers, spinlock, clock-change timing, and suspend resume rate. Reserved-memory tables are `memremap()`ed by `tegra210-emc-table.c` and retained until device release. Hardware state includes EMC timing registers, MC arbitration registers, DLL state, MRW/ZQ/autocal/pad state, and refresh configuration. Suspend stores `resume_rate`, forces 204 MHz, detaches the provider, then resume reattaches and restores the rate.

### Dependencies And Integration Points
The core depends on the Tegra210 clock API (`tegra210_clk_emc_attach()`, `tegra210_clk_emc_update_setting()`, DLL helpers), reserved-memory table ops, the common Tegra MC handle, thermal cooling framework, debugfs, timers, LPDDR mode-register semantics, and the r21021 sequence file. Timing table structure and register offset arrays must match firmware/BCT generated tables exactly. The thermal framework can enable refresh polling through the registered cooling device named `emc`.

### Risks
The driver trusts reserved-memory timing table layout and only performs limited validation; corrupt or mismatched tables can destabilize memory. Many helper waits busy-loop with microsecond delays, and some DLL loops do not have explicit timeout. Rate changes above 204 MHz require `timing->trained`, so missing training markers reject higher OPPs. Refresh switching can replace the active timing table with derated entries while preserving the current index, so nominal/derated table counts and ordering must match. Debugfs temperature override can force refresh modes and should not be exposed in production test assumptions.

### Test Signals
Important signals include successful reserved-memory attach for nominal/derated tables, current-rate matching at probe, sequence revision selection, clock OPP transitions through `tegra210_clk_emc_attach()`, debugfs rate/temperature behavior, thermal cooling state toggling refresh polling, MR4-driven refresh mode changes, suspend/resume returning to the pre-suspend rate, and memory stress during repeated rate changes. Warnings for timing update, clock-change completion, missing table entries, unsupported sequence, or cooling registration should be treated as regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210-emc-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210-emc-table.c -->
## sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210-emc-table.c

### Purpose
This file registers reserved-memory operations for Tegra210 EMC timing tables. It maps firmware-provided timing-table memory into the EMC driver's address space, classifies the first table as nominal and the second matching table as derated, stores table counts, and unmaps the table on release.

### Important APIs, Types, And Functions
The main callbacks are `tegra210_emc_table_init()`, `tegra210_emc_table_device_init()`, and `tegra210_emc_table_device_release()`, grouped in `tegra210_emc_table_ops`. `RESERVEDMEM_OF_DECLARE()` binds these ops to reserved-memory nodes compatible with `nvidia,tegra210-emc-table`. `TEGRA_EMC_MAX_FREQS` limits scanning to 16 timing entries. The code consumes `struct tegra210_emc_timing` and writes into `struct tegra210_emc` fields `nominal`, `derated`, and `num_timings`.

### Control Flow
When the EMC core calls `of_reserved_mem_device_init_by_name()` for `nominal` or `derated`, the reserved-memory framework invokes `device_init`. The callback `memremap()`s the region write-back, counts entries until a zero revision or 16 entries, warns and ignores excess tables after nominal and derated are already assigned, requires derated entry count to match nominal count, and stores the mapped pointer in `rmem->priv`. Release checks that the pointer corresponds to either active table and calls `memunmap()`. Node init only logs base and size.

### State And Persistence
The persistent state is the mapping pointer stored in both `struct tegra210_emc` and `rmem->priv`. `emc->num_timings` is set from the nominal table and reused to validate derated tables. The timing contents are not copied; the core uses the mapped reserved-memory region directly. State persists for the device lifetime and is released by `of_reserved_mem_device_release()` from the EMC core.

### Dependencies And Integration Points
It depends on the reserved-memory framework, `memremap()`/`memunmap()`, the Tegra210 EMC timing struct definition, and the core driver's call order. It assumes only two named tables are meaningful: nominal first, derated second. The core later validates monotonic rates/voltages, selects timing entries, and builds clock configs from these mapped arrays.

### Risks
The table scanner trusts the reserved-memory size and scans up to 16 `struct tegra210_emc_timing` entries without deriving the bound from `rmem->size`; if firmware reserves too small a region, this can read beyond the mapping. If the nominal table has zero valid entries, core validation/current-rate matching will fail later. Excess tables are only warned and left mapped until release. Because data is used in place, corruption of reserved memory or ABI mismatch with `struct tegra210_emc_timing` can directly destabilize EMC programming.

### Test Signals
Tests should cover nominal-only and nominal-plus-derated reserved-memory nodes, derated count mismatch returning `-EINVAL`, excess table warnings, clean unmap on driver remove/failure, and core probe failure when no current-rate timing exists. Firmware/DT validation should ensure reserved-memory size is at least `num_entries * sizeof(struct tegra210_emc_timing)` and table revisions terminate with zero within 16 entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210-emc-table.c -->
