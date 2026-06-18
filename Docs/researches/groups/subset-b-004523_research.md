# subset-b-004523 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/sky2.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/sky2.h

### Purpose
`sky2.h` is the private hardware contract for the Marvell Yukon-2 `sky2` Ethernet driver. It does not implement the driver by itself; it defines the register map, bit fields, descriptor layouts, per-port state, shared device state, and inline MMIO helpers used by the C implementation. Its scope covers PCI/PCIe configuration windows, core CSR blocks, BMU queues, RAM buffers, GMAC/GPHY/PHY control, WOL, ASF/status units, descriptor opcodes, and hardware statistics access.

### Important APIs, Types, and Constants
Important register addressing helpers include `RAM_BUFFER(port, reg)`, `SK_REG(port, reg)`, `Q_ADDR(reg, offs)`, `Y2_QADDR(q, reg)`, `RB_ADDR(offs, queue)`, `WOL_REGS(port, x)`, `WOL_PATT_RAM_BASE(port)`, and `SK_GMAC_REG(port, reg)`. These encode the chip's banked/port-relative layout and are central to avoiding hard-coded per-port offsets in the implementation.

The header defines many hardware families:
- PCIe power/clock/ASPM control through `PCI_DEV_REG*`, `PCI_CFG_REG_1`, and related `P_*` and `PCI_*` masks.
- Global CSR and interrupt state through `B0_*`, `B2_*`, `B3_*`, `Y2_IS_*`, `Y2_HWE_*`, and timer/test fields.
- Queue, BMU, prefetch, RAM buffer, status, and polling units through `Q_*`, `BMU_*`, `PREF_UNIT_*`, `RB_*`, `STAT_*`, and `POLL_*`.
- Marvell PHY and GMAC programming through `PHY_MARV_*`, `PHY_M_*`, `GM_*`, `GMR_FS_*`, `RX_GMF_*`, and `TX_GMF_*`.
- Descriptor opcodes and control flags through `OP_*`, `HW_OWNER`, `EOP`, `INS_VLAN`, checksum opcodes, receive status opcodes, and `enum status_css`.

Core runtime types are `struct sky2_tx_le`, `struct sky2_rx_le`, and `struct sky2_status_le`, all packed little-endian hardware descriptors; `struct tx_ring_info` and `struct rx_ring_info`, which preserve software ownership and DMA-unmap metadata; `enum flow_control`; `struct sky2_stats` with `u64_stats_sync`; `struct sky2_port`, which is per-netdev/per-MAC state; and `struct sky2_hw`, which represents the PCI function, shared NAPI/status ring, chip identity, timers/work, and optional MSI waitqueue.

Inline helpers expose MMIO access: `sky2_read{8,16,32}()`, `sky2_write{8,16,32}()`, `gma_read{16,32,64}()`, `gma_write16()`, `gma_set_addr()`, `get_stats{32,64}()`, and PCI config-window helpers `sky2_pci_read{16,32}()` / `sky2_pci_write{16,32}()`.

### Control Flow
The header's control flow is declarative: it describes the state transitions the implementation must perform. Reset, power, clock, interrupt, and queue enable flows are represented by paired set/clear bits such as `CS_RST_SET/CLR`, `BMU_RST_SET/CLR`, `PREF_UNIT_RST_SET/CLR`, `RB_RST_SET/CLR`, `GMF_RST_SET/CLR`, `GMC_RST_SET/CLR`, and operational bits such as `BMU_START`, `SC_STAT_OP_ON`, or `GMF_OPER_ON`.

Transmit and receive flow is centered on descriptor ownership and status opcodes. TX and RX descriptors carry address, length, control, and opcode fields; status descriptors report RX status, VLAN/checksum/hash, TX index completion, and put-index notifications. `get_stats32()` and `get_stats64()` implement read-stable loops because multiword GMAC counters cannot be read atomically.

### State and Persistence
No durable persistence exists. State is live kernel/driver state mirrored in registers and DMA rings. `struct sky2_port` keeps ring producer/consumer indexes, pending counts, last checksum/MSS state, link advertising/speed/duplex/WOL flags, flow-control state, DMA mappings, and optional debugfs handle. `struct sky2_hw` keeps shared chip identity, status ring index/DMA address, per-port netdev pointers, feature flags such as `SKY2_HW_USE_MSI`, `SKY2_HW_RAM_BUFFER`, `SKY2_HW_NEW_LE`, `SKY2_HW_RSS_BROKEN`, and the watchdog/restart state. Hardware MIB counters accumulate until read/cleared by the implementation.

### Dependencies and Integration Points
This file depends on Linux kernel networking, PCI, DMA, MMIO, NAPI, timers/workqueues, and optional debugfs types included by the implementation. It integrates with the associated `sky2.c` driver, the PCI probe path, netdev transmit/receive paths, ethtool statistics, Wake-on-LAN, PHY/GMAC register programming, and interrupt handling. Descriptor structs and opcodes are ABI-like contracts with the Yukon-2 hardware, so layout and endianness are critical.

### Risks
The highest-risk areas are register bit correctness, descriptor packing, endian handling, and DMA ownership ordering. Wrong set/clear semantics can leave queues or PHYs in reset, while a bad opcode/control combination can corrupt TX/RX rings. `get_stats32/64()` can spin longer than expected if hardware counters are unstable. Feature flags must match chip revisions; enabling RSS, VLAN, advanced power, or new descriptor formats on broken hardware variants can produce subtle data corruption or hangs.

### Test Signals
Useful signals include successful PCI probe across Yukon chip IDs/revisions, link-up/link-down and flow-control negotiation, TX/RX with checksum/VLAN/TSO/RSS variants, jumbo MTU up to `ETH_JUMBO_MTU`, ethtool/MIB counter stability, WOL suspend/resume behavior, MSI and legacy interrupt modes, and fault-injection or stress tests around BMU/status-ring errors and reset recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/sky2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/Kconfig

### Purpose
This Kconfig file exposes MediaTek Ethernet support under the kernel networking vendor menu. It gates three symbols: the vendor visibility symbol `NET_VENDOR_MEDIATEK`, the optional wireless Ethernet dispatcher support `NET_MEDIATEK_SOC_WED`, the main SoC frame-engine Ethernet driver `NET_MEDIATEK_SOC`, and the separate STAR EMAC driver `NET_MEDIATEK_STAR_EMAC`.

### Important APIs, Types, and Functions
Kconfig symbols are the API. `NET_VENDOR_MEDIATEK` is a bool selected for MediaTek, Airoha, MT7621, MT7620, or `COMPILE_TEST` builds. `NET_MEDIATEK_SOC_WED` defaults to enabled when `NET_MEDIATEK_SOC` is not disabled and depends on `ARCH_MEDIATEK || COMPILE_TEST`. `NET_MEDIATEK_SOC` is tristate and selects its required kernel subsystems: `PINCTRL`, `PHYLINK`, `DIMLIB`, `GENERIC_ALLOCATOR`, `PAGE_POOL`, `PAGE_POOL_STATS`, `PCS_MTK_LYNXI`, and `REGMAP_MMIO`. `NET_MEDIATEK_STAR_EMAC` is a separate tristate selecting `PHYLIB` and `REGMAP_MMIO`.

### Control Flow
The file has a simple menu flow: show `NET_VENDOR_MEDIATEK`, enter the vendor block only when it is enabled, then expose WED, SoC Gigabit Ethernet, and STAR EMAC options. The `NET_MEDIATEK_SOC` dependency `NET_DSA || !NET_DSA` is the common Kconfig idiom that tracks the tristate state of DSA, preventing impossible built-in/module combinations when DSA is modular.

### State and Persistence
Build configuration is persisted in the kernel `.config`. Runtime state is not managed here, but these choices determine which object files can be built and which APIs the C code may assume are available.

### Dependencies and Integration Points
This file integrates with `drivers/net/ethernet/Kconfig`, the MediaTek Makefile in the same directory, phylink/PHY infrastructure, page-pool/XDP-adjacent receive allocation support, Dynamic Interrupt Moderation, LynxI PCS, regmap-backed syscon access, and optional DSA. The WED symbol controls compilation of `mtk_wed*` files and `mtk_wed_ops.o`.

### Risks
The main risk is dependency drift. If `mtk_eth_soc.c` starts using new APIs without selecting or depending on their providers, build failures appear only on some architecture or module combinations. `NET_MEDIATEK_SOC_WED` being `def_bool NET_MEDIATEK_SOC != n` makes WED compile broadly, so WED code must stay guarded for platforms without matching device tree resources.

### Test Signals
Run representative `allyesconfig`, `allmodconfig`, `COMPILE_TEST`, MediaTek/Airoha defconfig, and DSA-as-module builds. Check that `NET_MEDIATEK_SOC=y` with `NET_DSA=m` is not allowed, that WED objects are included only when expected, and that STAR EMAC remains independently selectable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/Makefile

### Purpose
This Makefile maps the MediaTek Ethernet Kconfig symbols to kernel objects. It builds the main MediaTek SoC Ethernet driver as a composite `mtk_eth.o`, optional WED support and debugfs components, the exported WED ops object, and the standalone STAR EMAC driver.

### Important APIs, Types, and Functions
The key build variables are `obj-$(CONFIG_NET_MEDIATEK_SOC) += mtk_eth.o`, `mtk_eth-y := ...`, `mtk_eth-$(CONFIG_NET_MEDIATEK_SOC_WED) += ...`, `obj-$(CONFIG_NET_MEDIATEK_SOC_WED) += mtk_wed_ops.o`, and `obj-$(CONFIG_NET_MEDIATEK_STAR_EMAC) += mtk_star_emac.o`. `mtk_eth-y` always includes `mtk_eth_soc.o`, `mtk_eth_path.o`, `mtk_ppe.o`, `mtk_ppe_debugfs.o`, and `mtk_ppe_offload.o`. When WED is enabled, the composite also includes `mtk_wed.o`, `mtk_wed_mcu.o`, and `mtk_wed_wo.o`; `mtk_wed_debugfs.o` is added only when `CONFIG_DEBUG_FS` is defined.

### Control Flow
Build control is declarative. Kbuild creates `mtk_eth.o` as built-in or module according to `CONFIG_NET_MEDIATEK_SOC`, links unconditional core/offload objects into it, and conditionally augments it with WED implementation files. `mtk_wed_ops.o` is built as a separate object under the WED symbol, likely because it exposes operations across module boundaries.

### State and Persistence
No runtime state exists. The persistent output is the kernel build artifact graph, determined by `.config` and the object lists.

### Dependencies and Integration Points
This file integrates directly with `Kconfig` and the C files in the directory. Its most important coupling is that `mtk_eth_soc.c` references symbols provided by `mtk_eth_path.o`, PPE files, and WED headers/objects. The debugfs conditional keeps WED debug support out of non-debugfs builds.

### Risks
Ordering and symbol ownership matter. Moving a source file out of `mtk_eth-y` can create unresolved symbols in the composite driver. Making `mtk_wed_ops.o` part of `mtk_eth-y` instead of a separate object could break consumers that expect its current linkage. Debugfs-specific code must remain fully guarded by `CONFIG_DEBUG_FS`.

### Test Signals
Build with `CONFIG_NET_MEDIATEK_SOC=y/m/n`, `CONFIG_NET_MEDIATEK_SOC_WED=y/n`, `CONFIG_DEBUG_FS=y/n`, and `CONFIG_NET_MEDIATEK_STAR_EMAC=y/m`. Use `nm` or modpost output to verify that `mtk_eth.o`, WED objects, and STAR EMAC objects appear in the intended configurations without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_eth_path.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_eth_path.c

### Purpose
`mtk_eth_path.c` is a small path-fabric configuration library for the MediaTek SoC Ethernet driver. It maps a requested MAC-to-PHY path, such as GMAC1 to SGMII or GMAC2 to GEPHY/2.5G PHY, onto the SoC-specific mux bits in `ethsys`, `infra`, and NETSYS registers. It keeps pin/path switching out of the phylink MAC configuration code in `mtk_eth_soc.c`.

### Important APIs, Types, and Functions
`struct mtk_eth_muxc` describes one mux controller with a name, a required capability bit, and a `set_path()` callback. `mtk_eth_path_name()` converts path capability bits to debug strings. The static mux writers are `set_mux_gdm1_to_gmac1_esw()`, `set_mux_gmac2_gmac0_to_gephy()`, `set_mux_u3_gmac2_to_qphy()`, `set_mux_gmac2_to_2p5gphy()`, `set_mux_gmac1_gmac2_to_sgmii_rgmii()`, and `set_mux_gmac12_to_gephy_sgmii()`. The dispatch table `mtk_eth_muxc[]` ties those callbacks to `MTK_ETH_MUX_*` capability bits.

The exported path setup functions are `mtk_gmac_sgmii_path_setup()`, `mtk_gmac_2p5gphy_path_setup()`, `mtk_gmac_gephy_path_setup()`, and `mtk_gmac_rgmii_path_setup()`. These are declared in `mtk_eth_soc.h` and called by `mtk_mac_config()` when phylink changes interface mode.

### Control Flow
Each public setup function derives a path bit from `mac_id` and requested interface family, validates unsupported IDs, then calls `mtk_eth_mux_setup()`. `mtk_eth_mux_setup()` first verifies that the SoC advertises the requested path capability. If the SoC has no mux fabric (`MTK_MUX` absent), it returns success because no register programming is needed. Otherwise it iterates all mux controllers, invokes only those whose capability is present, and stops on the first callback error.

Each callback is intentionally tolerant: it updates only when the requested path is relevant to that mux and logs whether it changed anything. The register programming uses `mtk_m32()` for NETSYS MAC misc registers and `regmap_update_bits()`, `regmap_clear_bits()`, or `regmap_read()`/`regmap_update_bits()` for syscon-backed `infra` and `ethsys` maps.

### State and Persistence
The persistent hardware state is the mux register state in `eth->ethsys`, `eth->infra`, and direct NETSYS MMIO registers. The file itself stores no long-lived software state beyond the static mux table. Path validity is represented by the SoC capability bitmap in `eth->soc->caps`.

### Dependencies and Integration Points
The file depends on `mtk_eth_soc.h` for capability bits, register constants, `struct mtk_eth`, and helpers such as `MTK_HAS_CAPS()` and `mtk_is_netsys_v3_or_greater()`. It integrates with phylink via `mtk_eth_soc.c`: interface transitions call these setup functions before MAC/PCS configuration proceeds. It also depends on device tree-provided syscon regmaps; paths that touch `eth->infra` require the `MTK_INFRA` capability and successful probe setup.

### Risks
The most visible risk is incorrect capability/path mapping. A SoC data table that advertises a path without its required mux controller can silently skip necessary programming or return `-EINVAL`. Several callbacks preserve existing register bits and clear only selected masks; stale bits can remain if a transition is not explicitly handled. `set_mux_gmac1_gmac2_to_sgmii_rgmii()` compares `path` against combined capability constants (`MTK_GMAC1_RGMII`, `MTK_GMAC2_RGMII`) inside cases for path-only constants; this relies on macro values and should be watched when capability definitions change. Register-map availability is also critical for `eth->infra` and `eth->ethsys`.

### Test Signals
Exercise every supported `phy-mode` for each SoC data table: RGMII/TRGMII/MII/GMII, SGMII/1000BASE-X/2500BASE-X, internal 2.5G PHY, and GEPHY. Boot logs should not report unsupported paths for valid device trees. Register traces or hardware validation should confirm expected `ETHSYS_SYSCFG0`, `INFRA_MISC2`, `USB_PHY_SWITCH_REG`, `TOP_MISC_NETSYS_PCS_MUX`, and `MTK_MAC_MISC(_V3)` values. Link tests should include interface switching through phylink restart paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_eth_path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_eth_soc.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_eth_soc.c

### Purpose
`mtk_eth_soc.c` is the main MediaTek SoC Ethernet frame-engine driver. It implements platform probe/remove, SoC register maps, MDIO, phylink MAC operations, shared QDMA/PDMA ring management, RX/TX data paths, XDP, page-pool allocation, hardware LRO controls, PPE/offload integration, DSA special-tag handling, interrupt/NAPI service, DIM interrupt moderation, reset/hang recovery, ethtool operations, and SoC match data for MT2701/MT762x/MT798x/RT5350 families.

### Important APIs, Types, and Functions
Top-level data is described in `mtk_eth_soc.h`: `struct mtk_eth` is the shared frame-engine state, `struct mtk_mac` is per-netdev MAC state, and `struct mtk_soc_data` supplies per-SoC capabilities, register maps, descriptor sizes, clocks, offload version, PPE count, and DMA limits. This C file defines `mtk_reg_map`, `mt7628_reg_map`, `mt7986_reg_map`, and `mt7988_reg_map`; per-SoC `mtk_soc_data` instances; and the `of_mtk_match[]` device table.

The MMIO helpers are `mtk_w32()`, `mtk_r32()`, and `mtk_m32()`. MDIO support is implemented by `_mtk_mdio_{read,write}_c22()`, `_mtk_mdio_{read,write}_c45()`, the `mii_bus` wrappers, `mtk_mdio_config()`, `mtk_mdio_init()`, and `mtk_mdio_cleanup()`.

Phylink integration is through `mtk_phylink_ops`: `mtk_mac_select_pcs()`, `mtk_mac_prepare()`, `mtk_mac_config()`, `mtk_mac_finish()`, `mtk_mac_link_down()`, `mtk_mac_link_up()`, and EEE LPI methods. RT5350 uses stub `rt5350_phylink_ops` because that hardware lacks exposed MAC control registers.

The packet path centers on `mtk_start_xmit()`, `mtk_tx_map()`, `mtk_tx_set_dma_desc_v1/v2()`, `mtk_poll_tx_qdma()`, `mtk_poll_tx_pdma()`, `mtk_poll_rx()`, `mtk_napi_tx()`, and `mtk_napi_rx()`. Allocation and teardown are handled by `mtk_init_fq_dma()`, `mtk_tx_alloc()`, `mtk_rx_alloc()`, `mtk_dma_init()`, `mtk_dma_free()`, `mtk_tx_clean()`, and `mtk_rx_clean()`. XDP support uses `mtk_xdp_setup()`, `mtk_xdp_run()`, `mtk_xdp_submit_frame()`, and `mtk_xdp_xmit()`.

### Control Flow
Probe starts in `mtk_probe()`: allocate `struct mtk_eth`, map MMIO, configure DMA masks, initialize locks/work/DIM state, acquire syscon regmaps (`ethsys`, optional `infra`, optional `pctl`), enable coherency hooks, create SGMII PCS instances, set up SRAM pools, register WED hardware, acquire IRQs and clocks, initialize hardware, add child MAC netdevs, request IRQs, create MDIO, initialize PPE/offload, register netdevs, create a dummy NAPI device, and start the DMA hang monitor.

Opening a netdev runs `mtk_open()`: connect phylink, start shared DMA only for the first user via `dma_refcnt`, start PPE blocks, configure GDM forwarding/PPE selection for each MAC, update PPE MTU, enable NAPI and IRQs, then start phylink and TX queues. Stopping reverses that path in `mtk_stop()`, but shuts down DMA only when the last netdev user drops the refcount.

TX flow validates VLAN/GSO state, locks `page_lock` because multiple netdev queues share one ring, checks `MTK_RESETTING`, maps SKB head/frags into descriptors, updates QDMA/PDMA producer indexes, and stops queues when descriptor pressure is high. TX completion runs under NAPI, unmaps DMA, frees SKBs or XDP frames, updates byte/packet accounting, wakes queues when free descriptors recover, and feeds DIM samples.

RX flow chooses the normal or HWLRO ring, reads a completed descriptor, derives source MAC and PPE hash/reason, allocates a replacement buffer before handing the old buffer upward, runs XDP when page-pool backed, builds an SKB for `XDP_PASS` or non-XDP paths, sets checksum/hash/protocol metadata, handles DSA special-tag metadata for NETSYS v1, invokes PPE learning checks for selected reasons, gives packets to GRO, rewrites the descriptor with the replacement DMA address, and advances the hardware CPU index.

Reset flow is workqueue based. TX timeout and the monitor can schedule `mtk_pending_work()`, which takes RTNL, sets `MTK_RESETTING`, prepares PPE/FE/GMAC for reset, coordinates WED reset, stops running netdevs, performs warm hardware init, reopens previously running devices, restores PPE link state, clears `MTK_RESETTING`, and signals WED completion.

### State and Persistence
Runtime state is volatile and split between software structs, DMA-coherent descriptor rings, page-pool pages, syscon/MMIO registers, and hardware counters. `eth->dma_refcnt` persists shared DMA ownership across multiple netdev opens. `eth->state` tracks `MTK_HW_INIT` and `MTK_RESETTING`. `eth->prog` is the shared RCU XDP program, so enabling XDP on one netdev affects page-pool direction and shared DMA behavior. `mac->hwlro_ip[]` and `hwlro_ip_cnt` mirror ethtool-configured LRO destination IP filters into hardware registers. `mac->hw_stats` accumulates hardware counter deltas under `u64_stats_sync`. No durable storage is written.

### Dependencies and Integration Points
The driver depends on platform device probing, device tree child `mediatek,eth-mac` nodes, syscon/regmap resources, reset/clock/runtime PM frameworks, phylink and `pcs-mtk-lynxi`, MDIO, DMA mapping, page-pool, XDP/BPF, DSA, ethtool, NAPI, Net DIM, generic allocator SRAM pools, and MediaTek-specific PPE/WED modules in the same directory. Build dependencies are selected in `Kconfig`; object composition is controlled by the local Makefile.

### Risks
Shared-ring coordination is the main correctness risk: multiple netdevs, XDP frames, SKBs, QDMA linked descriptors, and PDMA compatibility descriptors all share `page_lock`, descriptor counts, and cleanup paths. Error unwinding in allocation paths can leak buffers if a later ring/page-pool allocation fails after earlier allocations. XDP is intentionally incompatible with HWLRO and limited by page-pool buffer size; MTU and feature toggles must preserve those constraints. Reset recovery races are complex because WED reset can drop RTNL and the driver reruns preliminary reset setup to compensate. SoC data mistakes in descriptor sizes, DMA limits, IRQ masks, capability bits, or register maps can cause silent ring corruption or unmapped register writes. The probe path also registers netdevice notifiers per MAC under QDMA; notifier lifecycle must stay paired with unregister/free paths.

### Test Signals
High-value tests include boot/probe on each compatible string, MDIO C22/C45 transactions, phylink mode coverage for RGMII/TRGMII/SGMII/2500BASE-X/internal/USXGMII cases, open/close sequencing with one, two, and three MACs, traffic through QDMA and PDMA SoCs, VLAN/TSO/checksum offloads, DSA special-tag paths, XDP pass/drop/redirect/tx/ndo_xmit including fragmented frames, HWLRO ethtool rule add/delete and feature toggling, MTU changes with PPE updates, WED/PPE offload init and reset, interrupt moderation changes from DIM, forced TX timeout and DMA hang monitor recovery, module remove after active traffic, and KASAN/KMEMLEAK checks for ring allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_eth_soc.c -->
