# subset-b-004647 Research

Grouped research for Ethernet driver sources under `sources/distributed-fs/ceph-client/drivers/net/ethernet`. Each section is delimited for deterministic reconciliation into per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/socionext/sni_ave.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/socionext/sni_ave.c

## Purpose
`sni_ave.c` is the full Linux netdev driver for the Socionext UniPhier AVE Ethernet MAC. It owns MAC reset/configuration, embedded descriptor memory, MDIO bus operations, NAPI RX/TX processing, PHY link adjustment, packet filtering, ethtool pause/WOL controls, suspend/resume, and SoC-specific pin-mode programming for multiple UniPhier variants. It is not an STMMAC glue layer; it implements a standalone `platform_driver` named `ave`.

## Important APIs, Types, And Functions
- Register and bit definitions cover AVE general, interrupt, MAC, descriptor-control, packet-filter, 32-bit and 64-bit descriptor memory, RMII bridge, and UniPhier syscon pinmode registers.
- `struct ave_private` is the driver state: MMIO base, IRQ, clocks/resets, PHY mode/device, MDIO bus, syscon regmap, WOL options, NAPI handles, RX/TX descriptor rings, pause settings, and `ave_soc_data`.
- `struct ave_desc_info` tracks each ring's descriptor-memory base, descriptor count, producer/consumer indices, and skb sidecar array. `struct ave_desc` stores skb and DMA mapping metadata.
- `ave_desc_read*()`, `ave_desc_write*()`, and `ave_desc_write_addr()` abstract 32-bit versus 64-bit hardware descriptor formats.
- `ave_mdiobus_read()` and `ave_mdiobus_write()` implement MDIO transactions with `readl_poll_timeout()` on `AVE_MDIOSR_STS`.
- `ave_open()`, `ave_stop()`, `ave_start_xmit()`, `ave_rx_receive()`, `ave_tx_complete()`, `ave_irq_handler()`, and NAPI poll functions form the datapath.
- `ave_pfsel_*()` and `ave_set_rx_mode()` implement unicast, broadcast, multicast, allmulti, and promiscuous filtering using AVE packet-filter entries.
- `ave_init()` and `ave_uninit()` are `ndo_init`/`ndo_uninit`; they enable clocks/resets, program syscon pinmode, reset hardware, register MDIO, attach the PHY, configure WOL defaults, and detach on cleanup.
- `ave_probe()` parses DT resources, allocates `net_device`, sets feature flags (`NETIF_F_IP_CSUM`, `NETIF_F_RXCSUM`), selects descriptor format and DMA mask, registers NAPI and the netdev, and logs hardware ID/version.
- `ave_suspend()` and `ave_resume()` preserve PHY WOL state and re-open the device when it was running.
- SoC match data (`ave_pro4_data`, `ave_pxs2_data`, `ave_ld11_data`, `ave_ld20_data`, `ave_pxs3_data`, `ave_nx1_data`) selects 32/64-bit descriptors, clocks/resets, and pinmode validation functions.

## Control Flow
Probe obtains `phy-mode`, IRQ, MMIO, optional MAC address, clocks/resets, syscon phandle, and MDIO bus, then registers the netdev. `ndo_init` enables the hardware clock/reset domain, writes pinmux bits through the syscon regmap, globally resets the MAC/PHY, registers the child `mdio` bus, and connects the PHY with `ave_phy_adjust_link()` as the callback. `ndo_open` requests the shared IRQ, allocates RX/TX sidecar arrays, initializes descriptor memory, pre-maps RX buffers, starts descriptors, initializes packet filters and MAC address registers, configures RX/TX MAC controls, enables interval IRQs, enables NAPI, starts PHY autonegotiation, and starts the queue.

TX maps the skb data into the current TX descriptor, pads short frames, sets `OWN`, first/last, length, checksum-disable, and interrupt bits, then advances `tx.proc_idx`. Completion is interrupt-driven through `AVE_GI_TX`; the TX NAPI poll calls `ave_tx_complete()`, which walks descriptors from `done_idx`, stops at hardware-owned entries, unmaps DMA, consumes skbs, updates u64 stats, and wakes the queue when buffers were freed.

RX uses pre-filled descriptors with mapped skb buffers. The RX interval interrupt schedules NAPI, which calls `ave_rx_receive()`. That path checks hardware ownership and status, unmaps the buffer, builds an skb, marks checksum as unnecessary when hardware reports a valid checksum, submits via `netif_receive_skb()`, advances indices, and refills freed RX descriptors. RX FIFO overflow calls `ave_rxfifo_reset()`, temporarily disables RX, suspends descriptors, drains packets, resets FIFO, clears status, and resumes RX.

Link changes update RGMII or RMII speed registers, duplex, and pause flow-control bits. Packet filter setup disables or enables exact-match filters for unicast/broadcast/multicast and can fall back to multicast prefix filters for IPv4/IPv6 all-multicast behavior.

## State And Persistence
Persistent state is in `ave_private`, descriptor sidecar arrays allocated during open, and hardware registers. RX/TX counters are software-maintained using `u64_stats_sync`; errors, drops, FIFO errors, and collisions are updated in IRQ/NAPI paths. `wolopts` is saved across suspend and restored during resume. MAC address persists in `ndev->dev_addr` and is rewritten to hardware on open or address change. No on-disk state exists.

## Dependencies And Integration Points
The driver integrates with platform DT (`compatible`, `phy-mode`, `mdio` child, `socionext,syscon-phy-mode`), phylib, of_mdio, syscon/regmap, clk/reset frameworks, DMA mapping, NAPI, ethtool, and PM sleep hooks. SoC-specific pinmode functions validate the requested PHY interface and syscon argument. It exposes a conventional Ethernet `net_device` and registers an MDIO bus named `uniphier-mdio`.

## Risks
- Descriptor ownership semantics differ for RX and TX and must remain correct; bad transitions can leak buffers or hand incomplete descriptors to hardware.
- `ave_start_xmit()` supports only the linear skb buffer, so scatter-gather is not enabled; enabling SG without implementation would be unsafe.
- RX descriptor preparation relies on 2-byte headroom and alignment assumptions.
- Error paths in `ave_open()` after partial RX descriptor preparation do not free already allocated descriptor sidecars in the shown failure path before IRQ cleanup; allocation failures during RX setup should be carefully tested.
- Syscon pinmode programming is SoC-specific and invalid DT arguments return probe/init errors.
- Suspend/resume assumes PHY state is available and `ave_global_reset()` can run before reopening the interface.

## Test Signals
Useful checks include DT probe for all compatible strings, MDIO child registration and PHY attach, `ip link set up/down`, RX/TX traffic including checksum offload, multicast/allmulti/promisc transitions, MTU maximum enforcement, link speed and duplex changes across RMII/RGMII, ethtool pause/WOL operations, suspend/resume with and without WOL, and induced RX FIFO overflow or TX completion stress. Kernel warning signals include descriptor stop/suspend timeouts, MDIO poll timeouts, invalid pinmode errors, and netdev stats consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/socionext/sni_ave.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/spacemit/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/spacemit/Kconfig

## Purpose
This Kconfig file introduces the SpacemiT Ethernet vendor menu and the K1 EMAC driver option.

## Important APIs, Types, And Functions
- `NET_VENDOR_SPACEMIT` is a vendor gate, default `y`, visible on `ARCH_SPACEMIT` or `COMPILE_TEST`.
- `SPACEMIT_K1_EMAC` is a tristate for the SpacemiT K1 Ethernet MAC driver, defaulting to module on `ARCH_SPACEMIT`.
- The driver depends on `MFD_SYSCON` and `OF`, and selects `PHYLIB`.

## Control Flow
When `NET_VENDOR_SPACEMIT` is enabled, the nested `SPACEMIT_K1_EMAC` option becomes available. Selecting it causes the Makefile in the same directory to build `k1_emac.o`.

## State And Persistence
The file affects kernel configuration only. It persists no runtime state.

## Dependencies And Integration Points
It integrates the K1 EMAC into the kernel networking Kconfig hierarchy and ensures required OF/syscon/PHY library dependencies are present before compilation.

## Risks
Dependency coverage is narrow: the driver also uses clocks, reset, runtime PM, timers, DMA mapping, NAPI, and ethtool APIs that are normally available in this build context but are not explicit Kconfig dependencies here. `COMPILE_TEST` helps expose missing include/config dependencies.

## Test Signals
Expected signals are successful `oldconfig/menuconfig` visibility, `CONFIG_SPACEMIT_K1_EMAC=m/y` producing `k1_emac.o`, and compile-test builds outside SpacemiT architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/spacemit/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/spacemit/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/spacemit/Makefile

## Purpose
The Makefile wires the SpacemiT K1 EMAC implementation into kbuild.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_SPACEMIT_K1_EMAC) += k1_emac.o` builds the driver when the Kconfig symbol is enabled.

## Control Flow
kbuild evaluates the `CONFIG_SPACEMIT_K1_EMAC` tristate and either links `k1_emac.o` into the kernel or builds it as a module.

## State And Persistence
Build-only file; no runtime state.

## Dependencies And Integration Points
Depends on the parent networking Makefile including the `spacemit/` directory and on the Kconfig symbol declared in `spacemit/Kconfig`.

## Risks
The Makefile has a single object and no composite module list, so additional source files would require explicit edits.

## Test Signals
`make M=drivers/net/ethernet/spacemit` or a full kernel build should emit `k1_emac.o` when `CONFIG_SPACEMIT_K1_EMAC` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/spacemit/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/spacemit/k1_emac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/spacemit/k1_emac.c

## Purpose
`k1_emac.c` is a standalone SpacemiT K1 Ethernet MAC driver. It implements a platform `net_device` driver with coherent DMA descriptor rings, MDIO bus registration, PHY connection, NAPI RX/TX cleanup, multicast filtering, runtime PM aware open/stop, hardware statistics extension, ethtool reporting, and system sleep callbacks.

## Important APIs, Types, And Functions
- `struct emac_priv` is the central private state: MMIO base, buffer size, TX/RX rings, netdev/platform device, NAPI, clocks, APMU syscon regmap and offset, IRQ, PHY interface, hardware stats and offsets, TX coalescing state, timers, delay-line settings, and `stats_lock`.
- `struct emac_desc_ring` describes a coherent descriptor ring, DMA address, descriptor count, head/tail indices, and RX/TX buffer sidecar arrays.
- `struct emac_tx_desc_buffer` and `struct emac_rx_desc_buffer` track skb ownership and DMA mappings.
- `emac_init_hw()` programs MAC filtering, thresholds, frame sizes, RX IRQ mitigation, DMA reset, 64-bit DMA mode, strict bursts, and burst length.
- `emac_alloc_*_resources()` and `emac_free_*_resources()` allocate/free coherent descriptor rings and sidecar arrays.
- `emac_tx_mem_map()` maps the skb head plus fragments into descriptors, using two buffers per descriptor and deferring ownership of the first descriptor until all descriptors are initialized.
- `emac_rx_clean_desc()` receives completed descriptors, validates frame status, strips FCS, feeds `napi_gro_receive()`, and refills RX buffers.
- `emac_interrupt_handler()` acknowledges DMA interrupts, disables RX/TX transfer-done interrupts, and schedules NAPI.
- `emac_mii_read()` and `emac_mii_write()` implement MDIO via MAC MDIO registers with poll timeouts.
- `emac_stats_update()` periodically reads 32-bit hardware statistic counters, detects wraparound, and adds saved offsets from previous down/up cycles.
- `emac_open()`/`emac_stop()` allocate/free resources and call `emac_up()`/`emac_down()`.
- `emac_probe()` configures OF resources, clocks, reset, fixed-link registration, MDIO bus, netdev ops, ethtool ops, and NAPI.

## Control Flow
Probe allocates an Ethernet netdev, enables scatter-gather features, parses MMIO, syscon, IRQ, MAC address, internal delay properties, clocks and reset, registers any fixed-link, initializes software defaults and timers, registers the MDIO bus, registers the netdev, and adds NAPI. `emac_config_dt()` converts `tx-internal-delay-ps` and `rx-internal-delay-ps` into delay-line units and validates them against the 8-bit delay code range.

Open allocates TX and RX coherent rings, then `emac_up()` runtime-resumes the device, parses/connects the PHY, programs APMU interface mode and delay line, initializes MAC/DMA hardware, writes the MAC address, configures TX/RX DMA base addresses, preallocates RX skb buffers, starts the PHY, requests the shared IRQ, enables DMA interrupts, enables NAPI, starts the queue, and schedules the stats timer.

TX checks available descriptors against the skb fragment count, stops the queue if space is low, maps the skb into descriptors, sets first/last/interruption flags, writes all descriptors before setting ownership on the first, kicks `DMA_TRANSMIT_POLL_DEMAND`, and stops the queue proactively when the remaining ring space approaches `MAX_SKB_FRAGS + 2`. TX cleanup runs inside the shared NAPI poll and unmaps both descriptor buffers before freeing the skb.

RX uses `emac_alloc_rx_desc_buffers()` to keep descriptors populated with DMA-mapped skbs. `emac_rx_clean_desc()` walks from the RX tail until it hits a DMA-owned descriptor or budget is exhausted, validates descriptor status bits, subtracts FCS, submits frames to GRO, clears sidecar ownership, advances tail, and refills empty descriptors.

Hardware statistics are read on demand through netdev/ethtool getters and periodically by `stats_timer`. `emac_down()` updates counters before reset and copies current totals into offset unions so later hardware counter resets do not make stats jump backwards.

## State And Persistence
Runtime state lives in `emac_priv`, coherent descriptor rings, skb sidecar arrays, timers, work item, and hardware registers. Hardware stats are accumulated in 64-bit software unions with offset copies to survive interface down/up resets. TX drops use per-CPU netdev dstats. Delay-line and interface-mode state is loaded from DT and programmed into the APMU syscon. No disk state is persisted.

## Dependencies And Integration Points
The driver integrates with OF (`spacemit,k1-emac`, `phy-handle`, fixed-link, `spacemit,apmu`, delay properties), syscon/regmap, phylib/of_mdio, runtime PM, clock/reset frameworks, DMA mapping, NAPI, ethtool netlink stats families, and netdev core. It uses definitions from `k1_emac.h` for register and descriptor layout.

## Risks
- TX mapping failure in `emac_tx_mem_map()` frees descriptors only from `old_head` to current `head`; failures while filling buffer 2 of a descriptor need careful leak testing.
- Hardware descriptor base registers are written as 32-bit values while DMA mode is set to 64-bit; this assumes reachable low address allocation or hardware-specific interpretation.
- Stats reads can time out if a PHY stops the reference clock; the driver returns without rescheduling in some cases, so link-down/up transitions are important.
- `emac_down()` disconnects PHY before disabling IRQ/NAPI; ordering should be validated under concurrent interrupts.
- MTU changes are refused while running, so userspace must down the interface before changing frame size.
- Internal delay conversion is rounded; marginal board timing depends on DT values and the fixed 15.6 ps step assumption.

## Test Signals
Exercise probe with valid/random MAC, fixed-link and external PHY, RMII/RGMII modes, delay property bounds, open/stop cycles, SG TX with many fragments, ring-full queue stop/wake, RX error descriptors, multicast/allmulti/promisc hashing, `ethtool -S`, RMON/MAC/pause stats, register dumps, TX timeout recovery, suspend/resume, runtime PM, and link speed changes. Watch for DMA mapping errors, MDIO poll timeouts, stats timeout messages, IRQ storms, and queue stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/spacemit/k1_emac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/spacemit/k1_emac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/spacemit/k1_emac.h

## Purpose
`k1_emac.h` defines the SpacemiT K1 EMAC hardware contract used by `k1_emac.c`: APMU syscon bits, DMA and MAC register offsets, register bitfields, DMA descriptor layouts, and hardware statistic counter unions.

## Important APIs, Types, And Functions
- APMU definitions cover interface selection, reference/function clocks, RMII/RGMII clock choices, PHY IRQ, AXI single-ID mode, and RX/TX delay-line fields.
- DMA register offsets include configuration/control/status/interrupts, poll-demand, base addresses, current pointers, missed frame, and IRQ mitigation.
- MAC register offsets include global/transmit/receive controls, frame/jabber size, address filters, multicast hash tables, flow control, MDIO, stats counters, FIFO thresholds, and MAC interrupts.
- Descriptor bitfields describe RX and TX ownership, first/last descriptors, buffer sizes, ring end, timestamp flags, error/status bits, and interrupt-on-completion.
- `struct emac_desc` is a four-word descriptor with `desc0`, `desc1`, and two buffer addresses.
- `union emac_hw_tx_stats` and `union emac_hw_rx_stats` map ordered 64-bit software counters to hardware counter indices. The array view is intentionally tied to struct member order.

## Control Flow
This header has no executable control flow. Its definitions are consumed by `k1_emac.c` to compose and decode hardware register values with `FIELD_PREP()` and `FIELD_GET()`.

## State And Persistence
The header defines in-memory layouts and symbolic constants. Statistic unions become persistent runtime state when embedded in `struct emac_priv`.

## Dependencies And Integration Points
It depends on Linux bitfield/bitops macros available through included headers and kernel context. It is tightly coupled to the K1 EMAC hardware programming model and the driver assumptions about descriptor size and stats ordering.

## Risks
- The stats unions rely on struct order matching hardware counter numbering; reordering members changes behavior.
- Delay-line field widths and units must match silicon documentation.
- Descriptor address fields are 32-bit in `struct emac_desc` even though the driver enables 64-bit DMA mode, so hardware constraints must be understood before broad platform reuse.
- Typos in macro names such as `MREGBIT_BIG_LITLE_ENDIAN` and `MREGBIT_ACOOUNT_VLAN` are harmless but may complicate future maintenance.

## Test Signals
Compile-time coverage should catch missing macros and type mismatches. Runtime signals are correct register programming, descriptor ownership transitions, ethtool stats counter alignment, and successful traffic at all supported PHY modes/speeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/spacemit/k1_emac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/Kconfig

## Purpose
This file adds the STMicroelectronics/Synopsys Ethernet vendor menu and includes the STMMAC Kconfig subtree.

## Important APIs, Types, And Functions
- `NET_VENDOR_STMICRO` is a vendor-level bool, default `y`, requiring `HAS_IOMEM`.
- If enabled, it sources `drivers/net/ethernet/stmicro/stmmac/Kconfig`.

## Control Flow
Kernel configuration enters this vendor menu, then delegates all specific STMMAC options to the nested Kconfig.

## State And Persistence
Configuration-only; no runtime state.

## Dependencies And Integration Points
Connects the STMMAC driver family to the global Ethernet driver configuration hierarchy.

## Risks
Disabling `NET_VENDOR_STMICRO` hides all STMMAC options, including many non-ST SoC glue drivers that use Synopsys IP.

## Test Signals
Menu visibility and successful selection of nested `STMMAC_ETH` and platform/PCI variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/Makefile

## Purpose
This Makefile descends into the STMMAC subdirectory when the main STMMAC Ethernet symbol is enabled.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_STMMAC_ETH) += stmmac/` selects the subdirectory.

## Control Flow
kbuild includes `drivers/net/ethernet/stmicro/stmmac/Makefile` when `CONFIG_STMMAC_ETH` is enabled.

## State And Persistence
Build-only; no runtime state.

## Dependencies And Integration Points
Depends on `STMMAC_ETH` from the nested Kconfig.

## Risks
No direct risk beyond build omission if the parent symbol is not enabled.

## Test Signals
Full kernel builds should traverse the `stmmac/` directory whenever STMMAC is built-in or modular.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/Kconfig

## Purpose
This Kconfig file defines the STMMAC core driver, optional selftests, platform-bus glue drivers, PCI helpers, and many SoC/vendor-specific DWMAC variants.

## Important APIs, Types, And Functions
- `STMMAC_ETH` is the main tristate for Synopsys Ethernet IP based controllers. It depends on I/O memory, DMA, optional PTP clock support, and ethtool netlink, and selects core subsystems including MII, PCS_XPCS, PAGE_POOL, PHYLINK, CRC32, reset controller, and devlink.
- `STMMAC_SELFTESTS` enables ethtool selftests when INET is present.
- `STMMAC_PLATFORM` enables platform-bus support and selects `MFD_SYSCON`.
- Platform glue options include DWC QoS, generic, Anarion, EIC7700, Ingenic, i.MX8, Intel platform, and many other SoC integrations.
- PCI-related options include `STMMAC_LIBPCI`, `DWMAC_INTEL`, `DWMAC_LOONGSON`, `DWMAC_MOTORCOMM`, and generic `STMMAC_PCI`.

## Control Flow
Selecting `STMMAC_ETH` enables the nested menus. Platform drivers are visible only under `STMMAC_PLATFORM`, while PCI choices are under the main STMMAC block. Each symbol maps to objects in `stmmac/Makefile`.

## State And Persistence
Configuration only; no runtime state.

## Dependencies And Integration Points
The file coordinates STMMAC with PHYLINK, XPCS, page pool, PTP, reset, syscon, MDIO mux/regmap, and architecture-specific symbols. It gates the build for all STMMAC core and glue sources in this work item.

## Risks
- Operator precedence in expressions such as `depends on OF && HAS_DMA && ARCH_ESWIN || COMPILE_TEST` should be read as allowing compile-test even without the earlier terms; this is common but can surprise maintainers.
- Selecting `STMMAC_PLATFORM` defaults to `y`, which may pull many platform options into config menus.
- Missing dependencies in individual glue options can surface as compile-test failures rather than menu constraints.

## Test Signals
Run `allmodconfig`/`allyesconfig`/architecture configs and verify the intended objects are selected. Confirm `DWMAC_EIC7700`, `DWMAC_IMX8`, `DWMAC_INTEL_PLAT`, and `DWMAC_INTEL` each map to their corresponding object files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/Makefile

## Purpose
The STMMAC Makefile builds the shared STMMAC core object and conditionally builds platform and PCI glue drivers.

## Important APIs, Types, And Functions
- `stmmac.o` is composed from core datapath, ethtool, MDIO, ring/chain modes, DWMAC 100/1000/4/5/XGMAC cores, descriptors, PTP, traffic control, XDP, EST, FPE, VLAN, PCS, and optional selftests.
- `stmmac-platform.o` is composed from `stmmac_platform.o`.
- Conditional `obj-$(CONFIG_DWMAC_*)` entries build specific platform glue modules.
- `STMMAC_LIBPCI`, `STMMAC_PCI`, and PCI DWMAC variants are mapped to their objects.

## Control Flow
kbuild first composes the shared core when `CONFIG_STMMAC_ETH` is set, then emits enabled platform/PCI glue modules based on individual Kconfig symbols. The comment notes that the generic platform driver must be ordered last.

## State And Persistence
Build-only; no runtime state.

## Dependencies And Integration Points
This file is the build integration point for the STMMAC core and all glue drivers in this subset: `chain_mode.c`, descriptor headers via core objects, DWC QoS, Anarion, EIC7700, generic, i.MX, Ingenic, Intel platform, and Intel PCI.

## Risks
Object ordering matters for generic platform matching; moving `DWMAC_GENERIC` earlier may cause overly broad compatible strings to bind before specific drivers. Adding a new glue driver requires matching Kconfig and Makefile changes.

## Test Signals
`make M=drivers/net/ethernet/stmicro/stmmac` with selected configs should compile the expected object set, and module aliases should be provided by each glue driver's OF/PCI tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/chain_mode.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/chain_mode.c

## Purpose
`chain_mode.c` implements STMMAC descriptor management for chained DMA mode, where each descriptor points to the next descriptor through `des3` instead of using only ring-end bits.

## Important APIs, Types, And Functions
- `jumbo_frm()` maps a large linear skb across multiple chained TX descriptors, using 8 KiB chunks for enhanced descriptors and 2 KiB chunks for normal descriptors.
- `is_jumbo_frm()` reports whether a frame exceeds the single-descriptor buffer limit for the active descriptor format.
- `init_dma_chain()` initializes `des3` next pointers for basic or extended descriptor arrays, wrapping the last descriptor back to the first.
- `refill_desc3()` repairs RX `des3` after timestamping hardware may overwrite it on non-extended descriptors.
- `clean_desc3()` repairs TX `des3` after TX timestamping may overwrite it on the last segment.
- `chain_mode_ops` exports these callbacks to the STMMAC core as `struct stmmac_mode_ops`.

## Control Flow
During ring initialization the core calls `.init` to populate next-descriptor addresses. During TX, `.is_jumbo_frm` decides whether a jumbo linear frame must be split, and `.jumbo_frm` maps each chunk into consecutive descriptors before returning the last descriptor index. During RX refill and TX cleanup, timestamp-aware hooks restore chain pointers when hardware used the same field for timestamps.

## State And Persistence
The persistent state is hardware-visible descriptor memory. Software state is the TX/RX queue indices and DMA sidecar entries in STMMAC queues. No separate state is allocated here.

## Dependencies And Integration Points
This file depends on STMMAC queue structures, descriptor ops, DMA mapping, timestamp enable flags, descriptor sizes, and `STMMAC_NEXT_ENTRY()`. It is selected in the core `stmmac-objs` list and used when the platform is configured for chained mode.

## Risks
- Error handling in `jumbo_frm()` returns `-1` on DMA mapping failures after earlier mappings, so callers must clean partial mappings correctly.
- Address calculations cast DMA addresses to 32-bit descriptor fields, limiting applicability on hardware requiring high DMA bits in chained pointers.
- `clean_desc3()` computes a replacement pointer using queue state and timestamp flags; mistakes can corrupt the chain and stall DMA.
- Chained mode interacts subtly with IEEE 1588 timestamp overwrite behavior.

## Test Signals
Use jumbo MTU traffic in chain mode for normal and enhanced descriptors, enable RX/TX hardware timestamping, stress wraparound at the last descriptor, inject DMA mapping failures where possible, and watch for "inconsistent Rx chain" or TX timeout symptoms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/chain_mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/common.h

## Purpose
`common.h` is a central STMMAC header defining core versions, descriptor sizing, statistics structures, feature flags, hardware capability fields, common register bits, flow-control constants, queue/status enums, DMA features, MAC device abstraction, and prototypes shared across STMMAC core files.

## Important APIs, Types, And Functions
- Core version macros identify DWMAC, XGMAC, and XLGMAC revisions.
- Descriptor sizing macros define supported RX/TX descriptor count ranges and defaults.
- `struct stmmac_extra_stats`, `struct stmmac_safety_stats`, queue stats, NAPI stats, and per-CPU stats shape ethtool and runtime accounting.
- `struct dma_features` records decoded hardware feature registers, including checksum, PTP, EEE, queues/channels, RSS, VLAN, TSN, safety, DMA width, and active PHY interface.
- Enums describe packet routing, RX frame status, TX frame status, DMA IRQ status/direction, IRQ request error categories, and FPE events.
- `struct mac_link`, `struct mii_regs`, and `struct mac_device_info` define the hardware abstraction linking MAC, DMA, descriptor, PTP, TC, MMC, EST, VLAN, PCS, MII, link, and filter capabilities.
- Function prototypes expose setup and MAC address helpers used by core implementations.

## Control Flow
This header has no executable control flow except `dwmac_is_xmac()`. It provides constants and type definitions that drive decisions in STMMAC setup, IRQ handling, ethtool stats, queue allocation, feature gating, and platform glue.

## State And Persistence
Types defined here become persistent runtime state in `struct stmmac_priv`, platform data, and hardware abstraction objects. Stats structures persist for the lifetime of the netdev and are exposed through ethtool/netdev APIs.

## Dependencies And Integration Points
It includes Linux netdevice, PHY, XPCS, module, VLAN when enabled, and internal `descs.h`, `hwif.h`, and `mmc.h`. It is consumed by most STMMAC core and glue files, making it a cross-module contract.

## Risks
- Changes to stats structures affect ethtool string ordering and userspace expectations.
- Queue and descriptor size constants must remain powers of two because `STMMAC_NEXT_ENTRY()` uses bit masking.
- `struct dma_features` mirrors hardware feature decoding; incorrect field semantics can enable unsupported offloads.
- Feature flags and enum values are shared across many files, so apparently local edits can have broad effects.

## Test Signals
Build all STMMAC variants, run ethtool stats/selftests where enabled, verify queue count bounds, exercise PTP/EEE/VLAN/TSN feature paths on capable hardware, and check that descriptor sizes are rejected or rounded appropriately by platform configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/descs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/descs.h

## Purpose
`descs.h` defines legacy DWMAC100/1000 normal, enhanced, and extended DMA descriptor bitfields and structures used by STMMAC descriptor operations.

## Important APIs, Types, And Functions
- RX normal descriptor bits cover checksum, CRC, dribble, MII, watchdog, frame type, collision, first/last, VLAN, overflow, length, filter failures, error summary, frame length, and ownership.
- RX enhanced/extended bits add alternate buffer sizing, chained/ring markers, PTP message metadata, timestamp drop, AV/VLAN/L3/L4 filter metadata.
- TX normal/enhanced bits cover collisions, carrier, payload/header errors, timestamp status, checksum insertion, padding/CRC controls, first/last segment, interrupt, chained/ring markers, and ownership.
- `struct dma_desc` is the four-word basic descriptor.
- `struct dma_extended_desc` adds extended status and timestamp words after the basic descriptor.
- `struct dma_edesc` supports enhanced descriptor layout for TBS with extra words before the basic descriptor.
- `dma_desc_to_edesc()` converts a basic descriptor pointer to the enclosing enhanced descriptor.
- `TX_CIC_FULL` encodes full checksum insertion.

## Control Flow
No control flow; descriptor ops and mode ops use these constants to interpret and prepare descriptors.

## State And Persistence
The structures define DMA-coherent memory shared with hardware. Values persist while rings are active and are updated by both CPU and DMA engine.

## Dependencies And Integration Points
Included by `common.h` and descriptor implementation files. The bit definitions are coupled to STMMAC normal/enhanced descriptor ops, timestamping, checksum offload, VLAN, and filtering.

## Risks
- Bitfield mistakes directly corrupt DMA ownership or status handling.
- Layout differences among normal, enhanced, extended, and TBS descriptors require callers to use the correct operations table.
- Endianness conversion must be handled by users of these fields; raw constants are CPU-side definitions.

## Test Signals
Traffic tests with checksum offload, VLAN, PTP timestamping, jumbo frames, ring and chain modes, and descriptor error injection validate these definitions. Compile coverage should include normal, enhanced, extended, and TBS descriptor users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/descs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/descs_com.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/descs_com.h

## Purpose
`descs_com.h` provides inline helpers for preparing normal and enhanced descriptors in ring and chained modes.

## Important APIs, Types, And Functions
- Ring-mode RX helpers set second-buffer size and end-ring bits for enhanced or normal descriptors.
- Ring-mode TX helpers set/clear end-ring bits and encode TX length across buffer 1 and buffer 2 masks.
- Chain-mode RX/TX helpers mark descriptors as second-address-chained.
- Chain-mode length helpers encode TX buffer length into the appropriate normal/enhanced mask.

## Control Flow
The inline helpers are called by descriptor operation implementations when initializing/refilling descriptors or preparing TX descriptors. Ring helpers branch on end-of-ring and buffer size; chain helpers set fixed chained bits.

## State And Persistence
They mutate hardware-visible descriptor fields in DMA memory. No additional state is stored.

## Dependencies And Integration Points
These helpers depend on `struct dma_desc`, descriptor bit definitions from `descs.h`, buffer size constants, `FIELD_PREP()`, and little-endian conversion. They are shared by ring and chain descriptor implementations.

## Risks
- The enhanced TX ring helper intentionally caps buffer 1 at 4 KiB despite a larger hardware mask; callers must understand split behavior.
- Incorrect `end` or buffer-size inputs can break ring wrap or overflow descriptor length fields.
- Because helpers OR fields into descriptors, callers must zero or mask descriptors before reuse.

## Test Signals
Ring wrap tests, chain mode traffic, jumbo frames, enhanced and normal descriptor modes, and static inspection for proper descriptor zeroing before helper use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/descs_com.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-anarion.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-anarion.c

## Purpose
This is the Adaptrum Anarion STMMAC glue layer. It handles a small control block used to reset the GMAC and select the RGMII interface before handing off to the shared STMMAC platform driver.

## Important APIs, Types, And Functions
- `struct anarion_gmac` stores the control-block MMIO base and encoded PHY interface selection.
- `anarion_gmac_init()` asserts reset, updates `GMAC_SW_CONFIG_REG` interface bits, and releases reset.
- `anarion_gmac_exit()` asserts reset on shutdown.
- `anarion_config_dt()` maps resource 1 for reset/config control, allocates private data, validates RGMII mode, and stores the interface selection.
- `anarion_dwmac_probe()` obtains STMMAC resources, parses DT platform data, installs init/exit callbacks and `bsp_priv`, then calls `devm_stmmac_pltfr_probe()`.

## Control Flow
Probe follows the common STMMAC glue sequence: get resources, parse DT into `plat_stmmacenet_data`, parse board-specific control region, attach callbacks, and invoke the core platform probe. During core bring-up, `init` toggles reset and interface selection. During core shutdown, `exit` reasserts reset.

## State And Persistence
State is limited to devm-managed `anarion_gmac` and the hardware reset/config registers. No software state persists beyond device lifetime.

## Dependencies And Integration Points
Depends on OF, platform resources, `stmmac_platform.h`, and RGMII PHY mode. Compatible string is `adaptrum,anarion-gmac`.

## Risks
Only RGMII is accepted; DTs using other modes fail probe. The control block is expected as platform resource index 1, so resource ordering matters. Reset is simple and lacks delay/polling, relying on hardware tolerance.

## Test Signals
Probe with valid/invalid `phy-mode`, verify resource 1 mapping, observe reset register transitions, and run basic STMMAC link/traffic tests on Anarion hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-anarion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-dwc-qos-eth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-dwc-qos-eth.c

## Purpose
This glue driver supports Synopsys DWC Ethernet QoS v4.10 style bindings and related Tegra/Tesla variants. It prepares STMMAC platform data, AXI tuning, clocks, resets, Tegra PHY reset GPIO handling, Tegra pad calibration on speed changes, and variant remove hooks.

## Important APIs, Types, And Functions
- `dwc_eth_dwmac_config_dt()` allocates or fills `plat_dat->axi`, parses `snps,en-lpi`, read/write outstanding request limits, and burst map, then forces GMAC4, AAL, TSO, and PMT support.
- `dwc_qos_probe()` picks `phy_ref_clk` as platform clock.
- `struct tegra_eqos` stores device, register base, EQOS reset control, and PHY reset GPIO.
- `tegra_eqos_fix_speed()` calibrates Tegra pads for 100/1000 Mbps while holding the STMMAC MDIO lock; it disables calibration for 10 Mbps.
- `tegra_eqos_probe()` handles Tegra-specific TX clock, PHY reset GPIO pulse, MDIO reset suppression, EQOS reset assert/deassert, MAC speed callback, TX clock-rate callback, and flags for SPH disable, TX LPI clock behavior, and PHY WOL.
- `dwc_eth_dwmac_probe()` manually fills resources, enables all clocks, runs variant probe, applies common config, and calls `stmmac_dvr_probe()`.
- `dwc_eth_dwmac_remove()` calls `stmmac_dvr_remove()` and variant remove.

## Control Flow
The driver does not use `stmmac_get_platform_resources()` because it handles unnamed IRQ/MMIO directly. Probe gets IRQ and MMIO, parses DT, bulk-enables clocks, selects the STMMAC clock by variant name, runs optional variant setup, fills common QoS config, then probes the STMMAC core. Tegra speed changes call the calibration routine through `plat_dat->fix_mac_speed`.

## State And Persistence
Variant state is devm-managed and stored in `plat_dat->bsp_priv`. Hardware state includes EQOS reset, PHY reset GPIO value, auto-calibration registers, AXI config, and STMMAC platform flags. No disk state exists.

## Dependencies And Integration Points
Uses OF match strings `snps,dwc-qos-ethernet-4.10`, `nvidia,tegra186-eqos`, and `tesla,fsd-ethqos`; integrates with clock bulk APIs, reset controls, GPIO descriptors, STMMAC core, MDIO locking, and GMAC4 register definitions.

## Risks
- Tegra calibration polling has very short timeouts; marginal hardware can fail speed changes.
- The driver decrements explicit outstanding request properties, preserving legacy binding behavior but requiring valid nonzero DT values.
- Bulk clock enablement is devm-managed but variant remove must still undo non-devm reset/GPIO state.
- Manual resource setup may miss named IRQ behavior expected by other STMMAC platform helpers.

## Test Signals
Probe all compatible variants, validate clock names, Tegra PHY reset timing, 10/100/1000 speed changes with calibration logs, suspend/resume through `stmmac_pltfr_pm_ops`, WOL behavior, AXI register programming, and normal STMMAC traffic including TSO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-dwc-qos-eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-eic7700.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-eic7700.c

## Purpose
This is the Eswin EIC7700 DWMAC QoS glue driver. It programs Eswin HSP syscon registers for interface selection, low-power AXI behavior, and TX/RX delay, configures clocks, and delegates the Ethernet core to STMMAC.

## Important APIs, Types, And Functions
- `struct eic7700_qos_priv` stores the STMMAC platform data for clock callbacks.
- `eic7700_clks_config()` prepares/enables or disables the bulk clock list.
- `eic7700_dwmac_init()`/`exit()` wrap clock enable/disable for STMMAC platform callbacks.
- `eic7700_dwmac_suspend()`/`resume()` delegate to runtime PM force suspend/resume.
- `eic7700_dwmac_probe()` reads required delay properties, looks up the HSP syscon regmap, reads offsets from the same phandle property, writes interface and delay registers, obtains optional clocks, installs callbacks, and probes STMMAC.

## Control Flow
Probe gets resources and standard STMMAC DT config, requires `rx-internal-delay-ps` and `tx-internal-delay-ps`, converts each to 0.1 ns units capped at `0x7f`, programs HSP control offsets, creates a three-clock bulk list (`tx`, `axi`, `cfg`), attaches `clks_config`, init/exit/suspend/resume callbacks, and calls `devm_stmmac_pltfr_probe()`.

## State And Persistence
State is devm-managed `eic7700_qos_priv`, STMMAC platform data, and syscon hardware registers. Runtime clock state follows STMMAC init/exit and PM callbacks.

## Dependencies And Integration Points
Depends on OF, syscon/regmap, runtime PM, clocks, STMMAC platform helpers, and compatible `eswin,eic7700-qos-eth`.

## Risks
- Delay properties are mandatory; missing either fails probe.
- The `eswin,hsp-sp-csr` phandle is used both as a regmap reference and as a container for three offset cells; DT binding must match exactly.
- Clock callbacks rely on `plat_dat->clks` and `num_clks` being stable.
- Register writes are not read back or masked for all fields, so integration depends on correct offsets and reset state.

## Test Signals
Probe with valid/missing delay properties, verify syscon writes, test all clocks optional/present, open/close PM cycles, suspend/resume, link speed changes, and STMMAC traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-eic7700.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-generic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-generic.c

## Purpose
The generic DWMAC platform driver binds common Synopsys DWMAC-compatible devices that need no SoC-specific glue beyond standard STMMAC platform data.

## Important APIs, Types, And Functions
- `dwmac_generic_probe()` gets STMMAC resources, parses DT platform data when an OF node exists, or consumes legacy platform data otherwise.
- For non-OF platform data it sets default multicast filter bins to `HASH_TABLE_SIZE` and unicast entries to 1.
- The OF match table includes many generic Synopsys and SPEAr compatible strings.

## Control Flow
Probe obtains resources, chooses OF or platform-data configuration, then calls `devm_stmmac_pltfr_probe()`.

## State And Persistence
No private state beyond STMMAC platform data.

## Dependencies And Integration Points
Uses STMMAC platform helpers and the broad compatible table. The Makefile orders this object after specific platform drivers because generic compatibles could otherwise bind too broadly.

## Risks
Generic matching can hide missing SoC glue if a DT uses only a generic compatible. Non-OF platform data must provide all required fields except the small defaults this file fills.

## Test Signals
Probe generic compatible DTs, legacy platform-data use, multicast filter behavior, and module alias ordering relative to specific glue drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-imx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-imx.c

## Purpose
This file is the NXP i.MX8/i.MX9 DWMAC EQOS glue layer. It configures SoC interface-mode syscon registers, TX and memory clocks, RMII reference-clock selection, speed-specific TX clock handling, i.MX93 reset quirks, and STMMAC platform flags.

## Important APIs, Types, And Functions
- `struct imx_dwmac_ops` holds variant flags, DMA address width, whether RGMII TX clock is auto-adjusted, and callbacks for reset, interface mode, and speed fixups.
- `struct imx_priv_data` stores device, TX/memory clocks, syscon regmap/offset, RMII reference-clock source, MMIO base, ops, and platform data.
- `imx8mp_set_intf_mode()`, `imx8dxl_set_intf_mode()`, and `imx93_set_intf_mode()` program interface selection differently by SoC.
- `imx_dwmac_clks_config()` enables/disables memory and TX clocks.
- `imx_set_phy_intf_sel()` validates STMMAC PHY interface selector values before calling variant mode setup.
- `imx_dwmac_fix_speed()` and `imx93_dwmac_fix_speed()` handle speed-dependent TX clock and i.MX93 fixed-link RGMII reprogramming.
- `imx_dwmac_mx93_reset()` performs DMA software reset and writes RMII speed reset bits for RMII mode.
- `imx_dwmac_parse_dt()` parses clocks, `snps,rmii_refclk_ext`, and `intf_mode` syscon phandle where required.
- `imx_dwmac_probe()` installs platform callbacks, enables clocks, sets queue TBS defaults, and calls `stmmac_pltfr_probe()`.

## Control Flow
Probe gets resources and standard DT STMMAC config, allocates private state, selects variant ops by compatible, parses clocks/syscon, copies variant flags, enables TBS on TX queues except queue 0, sets host DMA width, installs `set_phy_intf_sel`, clock config, `bsp_priv`, speed/clock callbacks, and optional reset quirk, then enables clocks and probes STMMAC. On probe failure it disables clocks.

## State And Persistence
State persists in `imx_priv_data`, STMMAC platform data, enabled clocks, syscon interface registers, and MMIO MAC control registers for i.MX93 speed/reset workarounds.

## Dependencies And Integration Points
Uses OF compatibles `nxp,imx8mp-dwmac-eqos`, `nxp,imx8dxl-dwmac-eqos`, and `nxp,imx93-dwmac-eqos`; depends on syscon/regmap, clocks, STMMAC platform core, PHY interface encodings, and platform PM ops.

## Risks
- `imx8dxl_set_intf_mode()` is a stub, so SCU-dependent configuration must happen elsewhere.
- i.MX93 fixed-link speed workaround temporarily disables interface bits and rewrites MAC control; incorrect ordering can disrupt traffic.
- Clock enablement is done before `stmmac_pltfr_probe()` and disabled only on immediate probe failure; later lifecycle relies on STMMAC callbacks.
- Queue TBS defaults are forced for all nonzero TX queues and may surprise DT queue configurations.

## Test Signals
Probe each compatible, validate `intf_mode` phandle handling, RMII external/internal reference clock cases, TX rate changes for 10/100/1000 RGMII, i.MX93 fixed-link mode changes and reset, suspend/resume, and STMMAC traffic with queue features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-imx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-ingenic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-ingenic.c

## Purpose
This is the Ingenic SoC DWMAC glue layer. It programs a MAC PHY control syscon register for different Ingenic SoC families and optional RGMII TX/RX delays, then delegates datapath operation to STMMAC.

## Important APIs, Types, And Functions
- `enum ingenic_mac_version` identifies JZ4775, X1000, X1600, X1830, and X2000 variants.
- `struct ingenic_soc_info` stores version, register mask, variant `set_mode` callback, and valid PHY interface selector bitmap.
- `struct ingenic_mac` stores variant info, STMMAC platform data, device, syscon regmap, and delay values.
- Variant mode functions (`jz4775_mac_set_mode()`, `x1000_mac_set_mode()`, `x1600_mac_set_mode()`, `x1830_mac_set_mode()`, `x2000_mac_set_mode()`) compose syscon register values.
- `ingenic_set_phy_intf_sel()` validates STMMAC selector encoding against the variant bitmap and calls the variant mode function.
- `ingenic_mac_probe()` parses STMMAC resources/DT, gets `mode-reg` syscon, parses optional `tx-clk-delay-ps` and `rx-clk-delay-ps`, installs `bsp_priv` and selector callback, and probes STMMAC.

## Control Flow
At probe, the driver builds standard STMMAC platform data, allocates private state, gets match data, looks up the MAC PHY control regmap, validates optional delay properties, stores platform data and callbacks, and calls `devm_stmmac_pltfr_probe()`. During STMMAC setup, `set_phy_intf_sel` programs the syscon according to the selected interface.

## State And Persistence
State is the devm-managed `ingenic_mac` and syscon register contents. Delay values are stored in internal units after multiplying parsed picosecond values by 1000 for the X2000 formula.

## Dependencies And Integration Points
Depends on OF, syscon/regmap, STMMAC platform helpers, and variant compatibles `ingenic,jz4775-mac`, `ingenic,x1000-mac`, `ingenic,x1600-mac`, `ingenic,x1830-mac`, and `ingenic,x2000-mac`.

## Risks
- Delay property names use `tx-clk-delay-ps`/`rx-clk-delay-ps`, not the common `*-internal-delay-ps`; DT binding must match.
- X2000 delay conversion uses `(delay + 9750) / 19500 - 1` after multiplying input by 1000, which is easy to misread and should be validated against hardware units.
- Valid interface selector bitmaps differ by SoC; invalid `phy-mode` fails setup.
- The syscon offset is fixed at 0 in `regmap_update_bits()`, so `mode-reg` must expose the intended register at offset zero.

## Test Signals
Probe all compatibles, validate GMII/RGMII/RMII acceptance per SoC, test invalid and boundary delay values, inspect syscon register programming, and run STMMAC traffic with link changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-ingenic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-intel-plat.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-intel-plat.c

## Purpose
This is the Intel platform-bus DWMAC glue driver, currently matching Intel Keem Bay. It configures TX and PTP reference clock rates and hands control to the STMMAC core.

## Important APIs, Types, And Functions
- `struct intel_dwmac_data` stores desired PTP reference clock rate, TX clock rate, and whether TX clock management is required.
- `struct intel_dwmac` stores device, TX clock, and match data.
- `intel_eth_plat_probe()` gets STMMAC resources/DT config, allocates private state, enables and rates `tx_clk`, rates `clk_ptp_ref`, installs TX clock callbacks, and calls `stmmac_dvr_probe()`.
- `intel_eth_plat_remove()` removes STMMAC and disables the TX clock.
- `kmb_data` sets 200 MHz PTP ref and 125 MHz TX clock.

## Control Flow
Probe follows STMMAC platform setup, then applies Intel clock policy before invoking the core driver. On failure after enabling TX clock, it disables the clock. Remove unwinds core and clock state.

## State And Persistence
State is the devm-managed `intel_dwmac` and enabled clock rates. No extra runtime datapath state is managed here.

## Dependencies And Integration Points
Uses compatible `intel,keembay-dwmac`, clock framework, STMMAC platform helpers, and GMAC4 clock-rate callback `stmmac_set_clk_tx_rate`.

## Risks
- Assumes `plat_dat->clk_ptp_ref` is valid when clock-rate adjustment is requested.
- Clock rate mismatches are corrected at probe, which may fail if clocks are fixed or shared.
- Uses `stmmac_dvr_probe()` directly rather than `devm_stmmac_pltfr_probe()`, so remove must be correct.

## Test Signals
Probe Keem Bay DTs, verify `tx_clk` and PTP ref rates, traffic at multiple speeds, remove/unbind clock disable, and suspend/resume through STMMAC platform PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-intel-plat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-intel.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-intel.c

## Purpose
`dwmac-intel.c` is the Intel PCI DWMAC glue driver for Quark, Elkhart Lake, Tiger Lake, Alder Lake, Raptor Lake, and PSE variants. It creates STMMAC platform data for PCI devices, handles SerDes power sequencing over an Intel MDIO ad-hoc address, configures PTP clock frequency and cross timestamping, programs PMC/FIA/ModPHY registers for TSN lanes, maps DMI board data to PHY addresses for Quark, configures MSI/MSI-X vectors, and invokes the shared STMMAC PCI/core probe.

## Important APIs, Types, And Functions
- `struct intel_priv_data` stores MDIO ad-hoc address, cross timestamp adjustment, PSE flag, TSN lane register list, and ModPHY register tables for 1G/2.5G.
- `struct stmmac_pci_info` wraps per-device setup callbacks referenced from the PCI ID table.
- `stmmac_pci_find_phy_addr()` maps PCI function numbers to PHY addresses through DMI tables for Quark/Galileo/IOT2000.
- `serdes_status_poll()`, `intel_serdes_powerup()`, and `intel_serdes_powerdown()` sequence SerDes PLL, reset, power state, rate, PCLK, and PSE RX clock gate bits over MDIO.
- `tgl_get_interfaces()` reads SerDes link mode and exposes SGMII or 2500BASE-X to phylink.
- `intel_mgbe_ptp_clk_freq_config()` programs GMAC GPIO bits to choose 200 MHz PTP clock mapping for PSE and PCH variants.
- `intel_crosststamp()` triggers internal auxiliary timestamp snapshots, reads PTP and ART values, and reports cross timestamps using `CSID_X86_ART`.
- `intel_tsn_lane_is_available()`, `intel_set_reg_access()`, and `intel_mac_finish()` interact with Intel PMC IPC to verify TSN lane availability and program 1G/2.5G ModPHY registers before SerDes re-power.
- `intel_mgbe_common_data()` fills queue counts, DMA/AXI settings, TSO/SPH flags, FIFO sizes, PTP, PCS/XPCS, VLAN fail queue, cross timestamping, and MSI vector offsets.
- Per-platform setup functions (`ehl_*`, `tgl_*`, `adls_*`, `adln_*`, `quark_default_data()`) specialize bus IDs, PHY interface, clock rates, queue counts, SerDes callbacks, safety features, host DMA width, and ModPHY tables.
- `stmmac_config_multi_msi()` and `stmmac_config_single_msi()` allocate PCI IRQ vectors and fill STMMAC resource IRQ fields.
- `intel_eth_pci_probe()` allocates platform data, enables PCI, maps BAR0, runs per-ID setup, configures MSI, and calls `stmmac_dvr_probe()`.

## Control Flow
PCI probe allocates Intel/private/STMMAC platform structures, enables the PCI device, maps BAR0, initializes default invalid MSI vector indices, runs the setup callback from the PCI ID table, builds `stmmac_resources`, tries multi-MSI then single IRQ fallback, and probes STMMAC. Remove calls `stmmac_dvr_remove()` and unregisters the fixed-rate STMMAC clock created by common data.

For mGbE variants, setup fills queue/traffic scheduling defaults, DMA burst/AXI settings, fixed-rate STMMAC clock, PTP controls, PCS selection for SGMII/1000BASE-X, MDIO masks to skip ad-hoc and XPCS addresses, cross timestamping support, VLAN fail queue, and MSI vector layout. SerDes power-up occurs through STMMAC callbacks, selecting 1G or 2.5G rate and polling for PLL/reset/power-state transitions. `mac_finish` can program PMC ModPHY tables and repower SerDes for requested interface.

Quark setup is simpler: it fills common GMAC defaults, determines PHY address by DMI/function mapping or fallback, sets RMII, and configures DMA burst settings.

## State And Persistence
State persists in `intel_priv_data`, STMMAC platform data, fixed-rate clock registration, PCI device power state, SerDes MDIO registers, PMC-programmed ModPHY registers, and GMAC GPIO/PTP control registers. Cross timestamp state temporarily sets STMMAC internal snapshot flags and uses aux timestamp locks/FIFO state.

## Dependencies And Integration Points
Depends on PCI, DMI, Intel PMC IPC, x86 ART CPUID support, STMMAC core/PTP helpers, XPCS/phylink PCS, MDIO bus operations, clock provider APIs, and PCI MSI/MSI-X. The PCI ID table maps many Intel device IDs to setup structures.

## Risks
- `intel_tsn_lane_is_available()` loops `j <= max_tsn_lane_regs`, which appears to read one element past the array length when `max_tsn_lane_regs` is set to `ARRAY_SIZE(...)`; this deserves review.
- SerDes status polling uses only ten short retries, so slow hardware transitions may fail power sequencing.
- Cross timestamping conflicts with external snapshot mode and relies on interrupt/FIFO behavior; failure paths must clear internal snapshot flags.
- Multi-MSI vector offsets are platform-data dependent; invalid queue counts or vector bases can map wrong IRQs.
- Fixed-rate clock registration must be unwound on all probe/remove failure paths to avoid leaks.
- PMC IPC register programming is platform-specific and can fail when firmware denies access or TSN lanes are unavailable.

## Test Signals
Test PCI probe/remove on each ID class, DMI PHY mapping for Galileo/IOT2000, multi-MSI and single-MSI fallback, SGMII/2500BASE-X SerDes power cycles, link mode switching through `mac_finish`, PTP clock frequency selection, cross timestamp reads, suspend/resume PCI D-state transitions, WOL where enabled, queue traffic across RX/TX queues, and safety/error interrupt paths. Static analysis should inspect the TSN lane loop bound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-intel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-intel.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-intel.h

## Purpose
`dwmac-intel.h` centralizes Intel DWMAC PCI glue constants for SerDes MDIO registers, power/rate fields, MDIO addresses, cross timestamping, PTP clock selection, and PMC ModPHY register programming values.

## Important APIs, Types, And Functions
- SerDes register indices: `SERDES_GCR`, `SERDES_GSR0`, and `SERDES_GCR0`.
- SerDes bitfields cover PLL clock request/ack, PHY RX clock, reset, power state, link mode, PCIe rate, and PCLK rate.
- `INTEL_MGBE_ADHOC_ADDR` and `INTEL_MGBE_XPCS_ADDR` identify non-PHY MDIO addresses used by Intel glue and XPCS.
- Cross timestamp constants include ART CPUID leaf and EHL PSE ART base frequency.
- PTP clock frequency masks define PSE and PCH GMAC GPIO encodings for 19.2, 200, and 256 MHz cases.
- ModPHY register indices and 1G/2.5G values are consumed by PMC IPC programming in `dwmac-intel.c`.

## Control Flow
No executable flow; definitions are consumed by the Intel PCI glue driver during SerDes power sequencing, interface detection, PTP clock setup, cross timestamp adjustment, and PMC ModPHY programming.

## State And Persistence
Constants define hardware register values that persist when written by `dwmac-intel.c`.

## Dependencies And Integration Points
The header assumes GMAC GPIO bit definitions from included STMMAC/DWMAC headers are visible to consumers. It is private to Intel DWMAC glue.

## Risks
- Typo `SERSED_LINK_MODE_1G` is unused or easy to misuse.
- ModPHY magic values are hardware/firmware-specific and should not be changed without Intel platform validation.
- MDIO addresses are masked out from normal PHY scanning in the driver; changing them affects discovery.

## Test Signals
Successful Intel PCI driver compile, correct SerDes power transitions, SGMII/2.5G mode detection, PTP frequency selection, and PMC ModPHY programming for 1G and 2.5G cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-intel.h -->
