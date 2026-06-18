# subset-b-004650 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxgmac2.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxgmac2.h

Purpose: Defines the DesignWare XGMAC2 register map, bit fields, descriptor fields, and exported operation tables used by the stmmac XGMAC/XLGMAC implementation. It is the hardware contract consumed mainly by `dwxgmac2_core.c`, `dwxgmac2_dma.c`, `dwxgmac2_descs.c`, `mmc_core.c`, `stmmac_fpe.c`, and `hwif.c`.

Important APIs and data: The header exports register offsets for MAC configuration, queue routing, RSS, timestamp/PPS, MTL scheduling, DMA channels, safety interrupts, L3/L4 filters, and XGMAC descriptor layouts. It declares `dwxgmac210_ops`, `dwxlgmac2_ops`, `dwxgmac210_dma_ops`, and `dwxgmac210_desc_ops`.

Control flow and state: No executable code lives here, but the macros define how runtime code persists hardware state through MMIO: link speed bits in `XGMAC_TX_CONFIG`, RX/TX enable bits, MTL queue maps, DMA ring addresses/tails/lengths, RSS key/table access windows, safety status latches, and descriptor ownership bits.

Dependencies and integration: Depends on `common.h` for shared DMA/MTL constants and kernel bit helpers. It integrates XGMAC2-specific code with generic `stmmac_ops`, `stmmac_dma_ops`, and `stmmac_desc_ops` callback dispatch in `hwif.h`.

Risks and test signals: Register masks are data-path critical. Regressions show up as broken link speed programming, DMA channel setup, RSS table writes, FPE/EST/PTP behavior, or descriptor ownership handoff. Test XGMAC and XLGMAC variants, all advertised speeds, RX/TX queue counts above four, RSS enable/disable, timestamp/PPS, and safety interrupt decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxgmac2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxgmac2_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxgmac2_core.c

Purpose: Implements MAC-side callbacks for Synopsys XGMAC2 and XLGMAC cores. It programs MAC enablement, link capabilities, MTL queue routing/scheduling, filtering, RSS, EEE/LPI, Wake-on-LAN, safety features, flexible RX parser, PPS, L3/L4 filters, ARP offload, and setup of `mac_device_info`.

Important APIs and flow: `dwxgmac210_ops` and `dwxlgmac2_ops` are the exported `stmmac_ops` tables. Setup functions initialize `mac->pcsr`, link speed masks, MDIO register layout, multicast/unicast filter capacity, VLAN count, and XGMAC/XLGMAC advertised speeds. Runtime callbacks include `core_init`, `irq_modify`, `set_mac`, `rx_ipc`, queue priority/routing functions, `rss_configure`, `config_l3_filter`, `config_l4_filter`, `flex_pps_config`, and `rxp_config`.

Control flow and state: Most operations are read-modify-write MMIO updates. Interrupt enable changes are serialized by `hw->irq_ctrl_lock`. RSS writes use the indirect address/data register and poll the busy bit. RX parser reprogramming temporarily disables RX and the parser, orders entries by priority, handles fragment entries, writes the all-pass entry last, then restores RX state. Safety IRQ handlers read, clear, log, and accumulate error counters in `stmmac_safety_stats`.

Dependencies and integration: Uses `stmmac.h` private state, `stmmac_fpe.h` for preemption class mapping, `stmmac_ptp.h`, VLAN helpers, XGMAC/XLGMAC register definitions, netdev multicast/unicast lists, CRC/hash helpers, and `readl_poll_timeout`.

Risks and test signals: High-risk paths are indirect filter/RSS polling timeouts, priority mapping conflicts, RX parser reconfiguration while traffic is active, safety counter offsets, and PPS period conversion. Test queue routing, multicast hash and perfect filter overflow, RSS key/table programming, L3/L4 filter enable/disable including IPv6 SA/DA exclusivity, EEE forced mode rejection of timer mode, FPE class mapping, and XGMAC versus XLGMAC speed setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxgmac2_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxgmac2_descs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxgmac2_descs.c

Purpose: Provides the XGMAC2 descriptor callback table used by the generic stmmac TX/RX paths. It understands XGMAC normal descriptors plus extended descriptor fields for TBS, VLAN insertion, RSS hash reporting, split-header metadata, timestamps, and context descriptors.

Important APIs and flow: Exported `dwxgmac210_desc_ops` implements descriptor initialization, ownership handoff, TX/RX status, TX/TSO preparation, interrupt-on-completion, MSS context descriptors, address programming, VLAN context descriptors, source-address insertion, RSS hash extraction, RX header length extraction, secondary buffer address programming, and TBS launch time fields.

Control flow and state: Descriptor state persists in little-endian DMA descriptors shared with hardware. TX preparation fills buffer lengths, first/last flags, checksum insertion, TSO fields, and sets OWN last after a `dma_wmb()` on first descriptors to avoid hardware seeing a partial frame. RX status checks OWN, context descriptors, last descriptor, and error summary. RX timestamps are valid only when a context descriptor follows and timestamp bits are sane.

Dependencies and integration: Depends on XGMAC descriptor masks from `dwxgmac2.h`, generic status enums from `common.h`, and is selected for XGMAC/XLGMAC by `hwif.c`. Callers reach it through `stmmac_desc_ops` wrappers in `hwif.h`.

Risks and test signals: Ownership ordering, endian conversion, and context descriptor reuse are critical. Test TX cleanup and DMA ownership races, multi-fragment and TSO packets, VLAN outer/inner insertion, RSS hash type reporting for TCP/UDP IPv4/IPv6, RX timestamp context descriptor validation, TBS descriptors, and error/discard behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxgmac2_descs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxgmac2_dma.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxgmac2_dma.c

Purpose: Implements the XGMAC2 DMA callback table for reset, AXI/system-bus configuration, channel initialization, MTL FIFO thresholds, interrupt handling, feature discovery, ring pointer setup, TSO, SPH, and TBS.

Important APIs and flow: `dwxgmac210_dma_ops` exports all DMA callbacks. Initialization programs system bus mode, PBL settings, channel descriptor base addresses, default DMA interrupt masks, RX/TX queue modes, FIFO sizes, flow-control thresholds, and static queue-to-TC maps. Interrupt handling reads channel status and enable masks, maps abnormal/normal bits to stmmac action flags, updates per-CPU IRQ counters, and clears enabled pending bits.

Control flow and state: DMA state is stored in hardware registers and `priv->dma_cap`. `get_hw_feature()` decodes MAC feature registers into capabilities for checksum offload, EEE, timestamping, RSS, TSO, SPH, queue/channel counts, FIFO sizes, EST, FPE, safety, address width, and parser resources. Start/stop TX also toggles MAC TX enable; start RX enables MAC RX, while stop RX only stops the DMA channel.

Dependencies and integration: Uses `stmmac_dma_cfg`, platform AXI data, `stmmac_pcpu_stats`, and XGMAC register definitions. It is selected by `hwif.c` for XGMAC and XLGMAC entries and invoked through `hwif.h` wrappers by open, reinit, interrupt, ethtool, and queue-control paths.

Risks and test signals: Feature decoding drives many upper-layer decisions, so bit shifts and generation-specific rules need coverage. Test reset timeout, 32/40/48-bit addressing, channel counts, RX/TX interrupt masking by direction, FIFO threshold modes, RIWT watchdog, TSO/SPH/TBS enablement, queue AVB/DCB behavior, and fatal bus error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxgmac2_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxlgmac2.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxlgmac2.h

Purpose: Defines the small XLGMAC-specific extension to the XGMAC2 register contract: high-speed link speed encodings and the XLGMAC RX queue enable register offset.

Important APIs and data: Macros cover `XLGMAC_CONFIG_SS` speed fields for 1G, 2.5G, 10G, 25G, 40G, 50G, and 100G plus `XLGMAC_RXQ_ENABLE_CTRL0`. These are used by `dwxgmac2_core.c` in `dwxlgmac2_setup()` and `dwxlgmac2_rx_queue_enable()`.

Control flow and state: No runtime code exists here. Runtime state affected by these macros is the link speed selection in the MAC configuration register and per-RX-queue enable mode.

Dependencies and integration: The header assumes kernel bit helpers are already available through including sources. It integrates with the shared XGMAC2 code path instead of defining a separate driver.

Risks and test signals: Wrong speed encodings would make phylink speed changes fail only on XLGMAC devices. Test XLGMAC setup, all high-speed modes, queue enablement for AVB and DCB, and fallback rejection when the device ID does not match `DWXLGMAC_ID`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxlgmac2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/enh_desc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/enh_desc.c

Purpose: Implements enhanced/alternate descriptor operations for older GMAC cores. These descriptors support richer TX/RX error reporting, checksum-offload status, PTP extended status, timestamp extraction, and ring/chain layout helpers.

Important APIs and flow: Exported `enh_desc_ops` provides status, init, release, prepare, ownership, IOC, frame length, extended RX status, timestamp, display, address, and clear callbacks. TX status decodes last-segment errors and may flush the TX FIFO. RX status validates ownership and last descriptor, updates detailed error counters, and maps checksum-offload status to stack-visible frame results.

Control flow and state: Descriptor fields are little-endian shared DMA state. Initialization marks RX descriptors owned and sets buffer sizes for chain or ring mode. Release preserves ring end markers. TX preparation writes length, first/last flags, checksum mode, and uses `dma_wmb()` before giving the first descriptor to hardware. Extended status updates PTP message, IP checksum, AV, VLAN priority, and L3/L4 match counters.

Dependencies and integration: Depends on `common.h` status enums and `descs_com.h` ring/chain bit helpers. `hwif.c` chooses it for GMAC devices using enhanced descriptors, with extended descriptors enabled only on sufficiently new Synopsys IDs.

Risks and test signals: Error accounting and descriptor marker preservation are easy to regress. Test enhanced ring and chain modes, checksum status variants, timestamp with and without extended descriptors, FIFO flush on underflow/frame-flush, VLAN status, and TX/RX descriptor reuse after cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/enh_desc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/hwif.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/hwif.c

Purpose: Selects and initializes the hardware-interface callback tables for every supported stmmac core family. It maps core type, Synopsys version, and XGMAC device ID to descriptor, DMA, MAC, PTP, TC, MMC, EST, VLAN, mode, FPE register offsets, and setup functions.

Important APIs and flow: `stmmac_hwif_init()` reads the version register, saves `priv->synopsys_id`, allocates `mac_device_info`, honors platform `mac_setup` overrides, finds the best `stmmac_hwif_entry`, fills missing callback pointers, sets `ptpaddr`, `mmcaddr`, `estaddr`, copies PTP clock ops, runs setup, and stores quirk callbacks. `stmmac_reset()` dispatches either platform reset or DMA reset. Internal quirk helpers choose normal/enhanced descriptors and ring/chain mode for older cores.

Control flow and state: The static `stmmac_hw[]` table is ordered so newer versions override older entries by reverse search. State persists in `priv->hw`, `priv->synopsys_id`, FPE register config, and subsystem MMIO base pointers. Platform overrides can partially prefill the MAC structure before generic fallback fills gaps.

Dependencies and integration: Includes all relevant stmmac operation providers: DWMAC100/1000/4/5, XGMAC2, VLAN, PTP, EST, FPE, descriptors, DMA, MMC, and TC. It is the main bridge between probe-time platform data and runtime callback dispatch in `hwif.h`.

Risks and test signals: Table ordering and version matching decide the whole driver personality. Test each core type, custom `mac_setup`, zero version register, XGMAC device ID mismatch, GMAC 3.50 extended descriptor threshold, ring/chain mode selection, FPE offset assignment, and failure paths for missing table entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/hwif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/hwif.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/hwif.h

Purpose: Declares the callback interfaces and wrapper macros that isolate the common stmmac driver from hardware-family-specific implementations.

Important APIs and types: Defines `stmmac_desc_ops`, `stmmac_dma_ops`, `stmmac_ops`, `stmmac_hwtimestamp`, `stmmac_mode_ops`, `stmmac_tc_ops`, `stmmac_mmc_ops`, `stmmac_est_ops`, `stmmac_vlan_ops`, and `stmmac_regs_off`. It also declares exported operation tables for descriptor, PTP, ring/chain, MAC, DMA, TC, MMC, and EST implementations plus `stmmac_reset()` and `stmmac_hwif_init()`.

Control flow and state: The `stmmac_do_callback` and `stmmac_do_void_callback` macros centralize null-checking and return `-EINVAL` when a callback is absent. All runtime hardware operations are dispatched through these wrappers from `priv->hw`, so the selected vtables become persistent driver state after probe.

Dependencies and integration: Pulls in netdevice, Linux stmmac platform definitions, packet classifier types, and many forward declarations to avoid large include coupling. It is included by implementation files and common driver code.

Risks and test signals: Macro signatures hide type checking and can silently return `-EINVAL` for missing callbacks. Build coverage should exercise all callback users, and runtime tests should verify optional operations degrade correctly: absent TC, absent EST, absent VLAN, absent PTP, and missing safety/FPE hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/hwif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/mmc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/mmc.h

Purpose: Defines MMC control bits, per-core MMC base offsets, and the persistent `stmmac_counters` structure used for hardware MAC Management Counter statistics.

Important APIs and data: `stmmac_counters` contains TX/RX frame, octet, size-bin, error, pause, VLAN, LPI, IPv4/IPv6, protocol, stream-gate, and FPE/MM counters. The header exports `dwmac_mmc_ops` and `dwxgmac_mmc_ops`.

Control flow and state: Counter fields are software accumulation state. `mmc_core.c` reads hardware counters, many of which reset on read, and adds them into this structure. The control bits select reset, freeze, preset, rollover, and reset-on-read behavior.

Dependencies and integration: Used by ethtool stats, FPE MAC Merge stats, MMC callbacks in `hwif.h`, and hardware selection in `hwif.c`. Base offsets are combined with `priv->ioaddr` to create `priv->mmcaddr`.

Risks and test signals: Field order and names are externally visible through ethtool stats. Test RMON-enabled and disabled devices, reset-on-read accumulation, XGMAC 64-bit counter saturation, FPE counter updates, and string/count alignment in ethtool.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/mmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/mmc_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/mmc_core.c

Purpose: Implements MMC statistics callbacks for GMAC-style and XGMAC-style counter blocks. It masks counter interrupts, controls counter behavior, and accumulates hardware counters into `struct stmmac_counters`.

Important APIs and flow: Exported `dwmac_mmc_ops` and `dwxgmac_mmc_ops` implement `ctrl`, `intr_all_mask`, and `read`. `dwmac_mmc_read()` reads 32-bit GMAC counters directly. `dwxgmac_mmc_read()` uses `dwxgmac_read_mmc_reg()` for 64-bit register pairs, saturating software fields to `~0U` if the hardware value exceeds 32 bits.

Control flow and state: Hardware counters are read from `priv->mmcaddr`; software state is monotonically accumulated in `priv->mmc` because the hardware is normally configured to reset counters after reads. XGMAC masking differs from GMAC: RX/TX interrupt masks are written as zero while FPE and IPC masks use all ones.

Dependencies and integration: Depends on `hwif.h` and `mmc.h`. Et htool calls `stmmac_mmc_read()` when RMON is supported and exposes the fields; MAC Merge stats also read FPE-specific counters.

Risks and test signals: Counter offset mistakes cause misleading user diagnostics. The XGMAC RX CRC register is read twice into the same field, which is worth regression awareness because reset-on-read hardware could double-clear or miscount depending on semantics. Test GMAC and XGMAC counter readback, reset-on-read accumulation, FPE counters, IPC counters, LPI counters, and interrupt mask behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/mmc_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/norm_desc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/norm_desc.c

Purpose: Implements normal descriptor operations for older non-enhanced GMAC descriptor formats.

Important APIs and flow: Exported `ndesc_ops` supplies descriptor status, initialization, release, TX preparation, ownership handoff, interrupt-on-completion, frame length, timestamp, display, address, and clear callbacks. TX status reports DMA ownership, non-last-segment status, and error summary counters. RX status reports ownership, last descriptor, error summary counters, dribbling, length, MII, CRC, overflow, and checksum errors.

Control flow and state: The code manipulates little-endian DMA descriptors shared with hardware. RX initialization sets OWN, buffer size, ring/chain markers, and optional interrupt disable. TX cleanup preserves ring end markers before clearing reusable fields. TX preparation updates first/last flags, checksum insertion, length fields using ring/chain helpers, and optionally sets OWN.

Dependencies and integration: Depends on `common.h` and `descs_com.h`. `hwif.c` selects this table for GMAC devices without enhanced descriptors; generic TX/RX paths invoke it through `hwif.h` wrappers.

Risks and test signals: Normal descriptors have less metadata, so common code must not assume enhanced-only callbacks. Test old MAC100/GMAC paths, ring and chain modes, checksum offload type-1 length adjustment, corrupted timestamp sentinel handling, VLAN status under `STMMAC_VLAN_TAG_USED`, and descriptor release marker preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/norm_desc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/ring_mode.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/ring_mode.c

Purpose: Implements ring-mode descriptor helpers for jumbo-frame TX and DES3 buffer management.

Important APIs and flow: Exported `ring_mode_ops` provides jumbo detection, jumbo TX mapping, 16 KiB RX buffer selection, DES3 initialization/refill, and DES3 cleanup. `jumbo_frm()` maps the linear skb head into one or two DMA descriptors, sets DES2/DES3 addresses for split buffers, prepares descriptors through the selected descriptor ops, and advances `cur_tx`.

Control flow and state: State is in `stmmac_tx_queue` and `stmmac_rx_queue` ring indices, descriptor memory, and `tx_skbuff_dma` metadata. Jumbo descriptors mark `is_jumbo` so cleanup knows when DES3 was used as an extra buffer pointer. RX DES3 is filled only for 16 KiB buffers.

Dependencies and integration: Depends on `stmmac.h`, DMA mapping APIs, buffer size constants, and descriptor callbacks. `hwif.c` selects ring mode for most non-chain configurations.

Risks and test signals: DMA mapping errors after partially mapping a jumbo frame can leave earlier mappings needing cleanup by callers. Test MTUs around 4 KiB, 8 KiB, and above 8 KiB, nonlinear skbs, extended versus normal descriptors, TX timestamp interaction with DES3 cleanup, and RX 16 KiB buffer refill.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/ring_mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac.h

Purpose: Defines central private data structures, resource declarations, queue state, feature state, and cross-file prototypes for the stmmac driver.

Important APIs and types: Key structures include `stmmac_resources`, TX/RX queue and buffer types, XDP wrappers, FPE config, TC/RFS/filter entries, RSS config, DMA queue arrays, EST schedule state, MSI interrupt names, and `stmmac_priv`. It declares probe/remove/suspend/resume, MDIO, PCS, PTP, XDP, ethtool, queue reinit, queue enable/disable, AF_XDP wakeup, and TAS basetime helpers.

Control flow and state: `stmmac_priv` is the persistent driver instance tying together MMIO bases, netdev/device, selected hardware callbacks, platform data, phylink, DMA rings, NAPI channels, statistics, EST/FPE/PTP/MMC state, EEE/WOL, descriptor mode, VLAN bitmap, TC/RFS flow tables, RSS table, XDP program, workqueue state, and devlink.

Dependencies and integration: Includes Linux networking, phylink, PCI, PTP, reset, page pool, XDP, BPF, and driver `common.h`. It is included by nearly every file in this subset.

Risks and test signals: Layout changes affect hot-path cache behavior and many subsystems. Test probe/remove, suspend/resume, queue reconfiguration, XDP/AF_XDP, PTP registration, EST/FPE, ethtool stats, MSI naming, VLAN restore, and selftest build configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_est.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_est.c

Purpose: Implements Enhanced Scheduled Traffic (802.3 Qbv) hardware programming and interrupt decoding for GMAC5/XGMAC EST blocks.

Important APIs and flow: Exported `dwmac510_est_ops` provides `configure` and `irq_status`. `est_configure()` validates PTP rate, writes base time, cycle time, gate-list length, time extension, and each gate control list entry through the indirect GCL access registers, configures PTOV differently for XGMAC and GMAC5, enables/disables EST, and controls EST interrupts.

Control flow and state: EST configuration persists in hardware registers under `priv->estaddr`; desired software schedule state is supplied in `struct stmmac_est`. `est_write()` polls the `EST_SRWO` bit after each indirect write. Interrupt status handling reads error bits, clears latches, updates `stmmac_extra_stats`, tracks per-TXQ head-of-line blocking reasons, and emits rate-limited diagnostics.

Dependencies and integration: Depends on `stmmac.h`, `stmmac_est.h`, PTP rate supplied by common TC/TAPRIO setup, and callback dispatch through `hwif.h`. `hwif.c` assigns this ops table to GMAC4+/XGMAC entries with EST offsets.

Risks and test signals: Indirect write timeout, bad PTP rate, and gate-list sizing can break schedules. Test enable and disable, GMAC5 versus XGMAC PTOV fields, full GCL programming, base-time rollover, all EST interrupts, per-queue HLB accounting, and taprio reconfiguration under `est_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_est.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_est.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_est.h

Purpose: Defines EST register offsets, bit fields, indirect GCL register indexes, and exports the `dwmac510_est_ops` callback table.

Important APIs and data: Provides GMAC and XGMAC EST base offsets, control/status/interrupt bits, PTOV masks and multipliers, error registers, frame-size capture masks, indirect GCL control/data registers, and indexes for BTR, CTR, TER, and LLR.

Control flow and state: No executable state exists here. These macros govern how `stmmac_est.c` writes schedule state into hardware and decodes interrupt state into statistics.

Dependencies and integration: Consumed by `hwif.c` for EST base offsets and by `stmmac_est.c` for all EST programming. It relies on kernel bit macros being available through including files.

Risks and test signals: Mask differences between GMAC5 and XGMAC are central to correct scheduling diagnostics. Test EST programming on both core types, status clear behavior, `EST_SZ_CAP_HBFQ_MASK()` for queue counts, and interrupt enable bit alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_est.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_ethtool.c

Purpose: Implements ethtool operations for stmmac: driver info, link settings, register dumps, ring sizes, coalescing, queue counts, RSS, Wake-on-LAN, EEE, timestamp capabilities, selftests, statistics, and MAC Merge/FPE controls.

Important APIs and flow: `stmmac_set_ethtool_ops()` installs `stmmac_ethtool_ops`. Stats paths build string/count/data arrays from safety counters, MMC counters, software extra stats, aggregate queue stats, and per-queue stats. Ring/channel setters validate bounds and power-of-two sizes before calling reinit helpers. RSS get/set copies `priv->rss` and invokes hardware RSS configuration. Coalescing translates RX RIWT between microseconds and watchdog units and updates per-queue TX timers/frame thresholds.

Control flow and state: User requests mutate `priv->msg_enable`, ring sizes through reinit, coalescing arrays, RX watchdog registers, RSS key/table, queue counts, FPE additional fragment size, and ethtool MMSV state. Register dumps call selected MAC/DMA dump callbacks, then reshape older DMA register regions into ethtool's expected layout.

Dependencies and integration: Depends on phylink ethtool helpers, PTP clock registration, FPE helpers, MMC read callbacks, DMA/MAC debug callbacks, selftest hooks, per-CPU stats sync, and the selected hardware vtables.

Risks and test signals: Stats string/count/data ordering must stay identical. Test `ethtool -S`, `-d`, `-g/-G`, `-c/-C` including per-queue, `-l/-L`, RSS key/indir updates, timestamp info with and without PHC, WOL/EEE forwarding through phylink, MAC Merge get/set/stats, and invalid ring/coalesce inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_fpe.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_fpe.c

Purpose: Implements Frame Preemption / MAC Merge (802.3 Qbu/802.3br) support for GMAC5 and XGMAC3-style hardware.

Important APIs and flow: Public helpers report support, initialize ethtool MMSV, handle FPE interrupts, get/set additional fragment size, and map preemption classes for GMAC5 and XGMAC3. `stmmac_mmsv_ops` integrates with ethtool's MAC Merge state machine by configuring TX FPE, enabling PMAC interrupts, and sending verify/response mPackets.

Control flow and state: FPE state persists in MAC and MTL FPE registers plus `priv->fpe_cfg.fpe_csr` cache and `ethtool_mmsv`. IRQ status reads the clear-on-read MAC FPE status register only in `stmmac_fpe_irq_status()`, translates verify/response events, and passes them to ethtool MMSV. Preemption class mapping writes queue bitmaps into MTL registers and, for XGMAC, reprograms TC-to-queue fields.

Dependencies and integration: Depends on `stmmac_priv`, selected `stmmac_fpe_reg` offsets from `hwif.c`, ethtool MMSV helpers, MAC interrupt locking, queue/TC mappings, and GMAC/XGMAC register definitions. Et htool calls this file for `get_mm`, `set_mm`, and MM stats.

Risks and test signals: Clear-on-read interrupt status and TC-to-queue mapping are delicate. Test FPE supported/unsupported combinations, PMAC interrupt enable/disable races, verify/response state transitions, additional fragment size, GMAC5 one-to-many TC validation under SP and weighted schedulers, XGMAC no-TC default restoration, and MM statistics from MMC counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_fpe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_fpe.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_fpe.h

Purpose: Declares stmmac FPE/MAC Merge support APIs and exported register layout instances.

Important APIs and data: Declares support detection, initialization, IRQ handling, additional-fragment-size accessors, GMAC5/XGMAC3 preemption class mapping callbacks, and `dwmac5_fpe_reg`/`dwxgmac3_fpe_reg`.

Control flow and state: The header has no state, but its APIs operate on `priv->fpe_cfg`, ethtool MMSV state, MAC FPE status/control, MTL FPE control, and MAC interrupt enable registers.

Dependencies and integration: Includes Linux types and netdevice definitions and forward-declares `stmmac_priv`. `dwxgmac2_core.c`, `hwif.c`, `stmmac_ethtool.c`, and `stmmac_fpe.c` rely on this contract.

Risks and test signals: Optional FPE support depends on both hardware capability and a valid preemption mapping callback. Build and runtime tests should cover GMAC5, XGMAC3, and unsupported cores, plus ethtool MAC Merge operations when the callbacks are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_fpe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_hwtstamp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_hwtstamp.c

Purpose: Implements hardware timestamp and PTP timecounter register operations shared by GMAC and XGMAC stmmac cores.

Important APIs and flow: Exported `stmmac_ptp` and `dwmac1000_ptp` provide `stmmac_hwtimestamp` callbacks for timestamp configuration, sub-second increment, system time init/adjust/read, addend update, auxiliary PTP time read, timestamp interrupt handling, and latency correction. GMAC1000 uses legacy `dwmac1000_get_ptptime` and interrupt helpers for part of the table.

Control flow and state: PTP commands write update registers, set command bits in `PTP_TCR`, and poll until hardware clears them. `config_sub_second_increment()` chooses fine/coarse and digital/binary rollover scaling. `timestamp_interrupt()` handles internal snapshot wakeups or external timestamp events, reading auxiliary snapshot time under `ptp_lock` and emitting `ptp_clock_event()`. Latency correction writes ingress and egress correction registers based on hardware latency registers and timestamp format.

Dependencies and integration: Depends on PTP register definitions, platform snapshot flags, wait queues, `ptp_clock_kernel`, and selected PTP ops from `hwif.c`. Et htool timestamp info and PTP clock code consume these callbacks.

Risks and test signals: Polling timeouts and rollover-format conversions affect PHC correctness. Test fine/coarse adjustment, digital and binary rollover, init/addend/adjust timeout paths, get_systime stable seconds read, external timestamp events, internal snapshot wakeup, latency correction on i.MX-style hardware, and legacy GMAC1000 behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_hwtstamp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_libpci.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_libpci.c

Purpose: Provides reusable PCI power-management helpers for stmmac platform glue drivers.

Important APIs and flow: `stmmac_pci_plat_suspend()` saves PCI state, disables the device, and enables wake from D3. `stmmac_pci_plat_resume()` restores PCI state, powers the device to D0, enables it, and restores bus mastering. Both are exported GPL symbols.

Control flow and state: Persistent state is PCI config/device state managed by the PCI core. The `bsp_priv` argument is accepted for platform-helper compatibility but unused.

Dependencies and integration: Depends on Linux device and PCI APIs plus `stmmac_libpci.h`. PCI-based stmmac drivers can use these helpers in PM callbacks before or after common stmmac suspend/resume logic.

Risks and test signals: Ordering with common netdev suspend/resume matters: device disable before DMA quiesce would be unsafe if called in the wrong layer. Test suspend/resume on PCI devices, wake from D3, `pci_enable_device()` failure recovery, bus mastering restored after resume, and interaction with runtime PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_libpci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_libpci.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_libpci.h

Purpose: Declares the stmmac PCI platform suspend/resume helper functions.

Important APIs and data: Exposes `stmmac_pci_plat_suspend(struct device *dev, void *bsp_priv)` and `stmmac_pci_plat_resume(struct device *dev, void *bsp_priv)`.

Control flow and state: No state is defined here. The declarations allow PCI glue drivers to share PM helper behavior implemented in `stmmac_libpci.c`.

Dependencies and integration: Uses `struct device` declarations from included translation units; included by the PCI helper implementation and expected PCI glue users.

Risks and test signals: Header/API drift would break out-of-file PCI glue builds. Test module builds with PCI stmmac users and ensure suspend/resume callback signatures match platform glue expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_libpci.h -->
