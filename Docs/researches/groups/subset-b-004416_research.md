# subset-b-004416 Research

Grouped research for the subset B item covering Faraday FTMAC100, Myson/Fealnx, Freescale DPAA, and DPAA2 Ethernet support files. Each section is bounded by the required source-path markers for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/ftmac100.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/ftmac100.c

## Purpose
This file implements the Faraday FTMAC100 10/100 Ethernet platform driver. It binds to the `andestech,atmac100` compatible string, allocates a standard `net_device`, maps the controller MMIO region, registers NAPI and ethtool hooks, and drives the hardware through RX/TX DMA descriptor rings declared in `ftmac100.h`.

## Important APIs, Types, and Functions
The central private state is `struct ftmac100`, which stores MMIO base, IRQ, DMA-coherent descriptor memory, RX/TX ring cursors, a TX spinlock, `net_device`, `device`, NAPI object, and `mii_if_info`. Probe/remove are handled by `ftmac100_probe()` and `ftmac100_remove()`. Netdev entry points are `ftmac100_open()`, `ftmac100_stop()`, `ftmac100_hard_start_xmit()`, `ftmac100_change_mtu()`, `ftmac100_set_rx_mode()`, and `ftmac100_do_ioctl()`. Hardware setup is centralized in `ftmac100_reset()`, `ftmac100_start_hw()`, and `ftmac100_stop_hw()`. MDIO access is provided through `ftmac100_mdio_read()` and `ftmac100_mdio_write()`, feeding generic MII ethtool/ioctl helpers.

## Control Flow
Probe obtains memory and IRQ resources, allocates `alloc_etherdev()`, populates netdev ops and ethtool ops, resolves a platform MAC address or later randomizes one, maps registers, initializes MII metadata, and registers the netdev. Open allocates the coherent descriptor block plus RX pages, requests the IRQ, resets ring cursors, starts hardware, enables NAPI, starts the TX queue, and unmasks interrupts. The IRQ handler disables all interrupts and schedules NAPI. `ftmac100_poll()` reads ISR, drains RX packets up to budget, completes TX descriptors, accounts status bits, handles MII link changes, and re-enables interrupts once the poll cycle completes. Stop masks interrupts, stops queueing, disables NAPI, shuts down MACCR, frees IRQ, unmaps/free buffers.

## State and Persistence
State is in memory only: descriptor rings, RX page pointers, TX skb backpointers, ring indices, MII status, netdev counters, and MACCR programming. No persistent storage is touched. RX descriptor `rxdes3` stores a `struct page *`, and TX descriptor `txdes3` stores an `sk_buff *`; this is convenient but assumes pointer width fits in `unsigned int`, which is a portability risk on 64-bit systems. Descriptor ownership is exchanged with DMA through OWN bits and explicit DMA map/unmap calls.

## Dependencies and Integration Points
The driver depends on platform device resources, OF matching, Linux netdev, NAPI, ethtool, MII helpers, DMA mapping, `platform_get_ethdev_address()`, and raw MMIO accessors. It integrates with multicast filtering through hash table registers, with PHY management through `generic_mii_ioctl()` and `mii_ethtool_*()`, and with normal Ethernet stack receive/transmit paths through `netif_receive_skb()` and `ndo_start_xmit`.

## Risks
The implementation supports only single-segment TX and RX; oversized TX packets are dropped and multi-segment RX packets are dropped. `ftmac100_rx_packet()` allocates a small skb shell then attaches a page; failed page replacement after consuming the old page is not checked, so sustained allocation failures can deplete RX descriptors. The pointer-in-32-bit descriptor scratch fields are risky on 64-bit builds. `ftmac100_change_mtu()` writes MACCR even when the device may be down, so tests should cover closed-device MTU changes. Interrupt handling always returns `IRQ_HANDLED` after masking interrupts.

## Test Signals
Useful validation includes probe/remove on a DT-backed platform, open/close cycles, ping/iperf traffic, jumbo-MTU boundary tests up to `MAX_PKT_SIZE - VLAN_ETH_HLEN`, multicast/allmulti/promiscuous mode changes, MDIO ethtool operations, TX timeout/error injection, low-memory RX allocation behavior, and NAPI budget behavior under RX load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/ftmac100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/ftmac100.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/ftmac100.h

## Purpose
This header defines the FTMAC100 hardware contract used by `ftmac100.c`: register offsets, interrupt/status/control bits, MDIO command fields, and aligned RX/TX DMA descriptor layouts.

## Important APIs, Types, and Functions
The key exported local types are `struct ftmac100_txdes` and `struct ftmac100_rxdes`, each aligned to 16 bytes and made of four words. The first two words hold status/control flags, the third holds a hardware buffer address, and the fourth is explicitly unused by hardware and used by the C driver as private scratch. Macro groups describe `FTMAC100_OFFSET_*` registers, `FTMAC100_INT_*` ISR/IMR bits, interrupt coalescing/timer fields, DMA burst control, `FTMAC100_MACCR_*`, MDIO fields, and descriptor flags such as `FTMAC100_TXDES0_TXDMA_OWN`, `FTMAC100_TXDES1_EDOTR`, `FTMAC100_RXDES0_RXDMA_OWN`, `FTMAC100_RXDES0_FRS`, and `FTMAC100_RXDES1_EDORR`.

## Control Flow
The header has no executable control flow, but it defines the protocol for the source file. Rings are terminated by `EDOTR` or `EDORR`; DMA ownership is represented by the high bit of descriptor word 0; RX frame boundaries use FRS/LRS; TX frame boundaries use FTS/LTS; and MDIO access is issued through PHYCR/PHYWDATA bitfields.

## State and Persistence
The only state represented here is volatile hardware state in MMIO registers and DMA descriptors. There is no persistent state. The descriptor `txdes3` and `rxdes3` fields are typed as `unsigned int` even though the driver stores kernel pointers there; this is a structural portability concern.

## Dependencies and Integration Points
The file is private to the Faraday driver. It depends on kernel fixed-width endian types such as `__le32` being available through including C files. Its definitions integrate the platform driver with the Ethernet MAC, DMA engine, and MII management block.

## Risks
Bit definitions must match the hardware manual exactly; mistakes cause silent DMA corruption, interrupt loss, or packet filtering errors. The 11-bit buffer-size masks enforce the driver's `0x7ff` size limits. Pointer scratch fields are unsafe if built for an ABI where `sizeof(void *) > sizeof(unsigned int)`.

## Test Signals
Compile coverage catches missing definitions. Runtime validation should focus on descriptor ring wrap, interrupt mask behavior, MDIO read/write, multicast hash programming, and RX/TX ownership transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/ftmac100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fealnx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fealnx.c

## Purpose
This file implements the Myson MTD-8xx/Fealnx PCI Ethernet driver. It is an older-style PCI netdev driver using fixed-size DMA descriptor rings, bit-banged MII management, interrupt-driven RX/TX completion, timers for link maintenance and reset recovery, and ethtool/MII interfaces.

## Important APIs, Types, and Functions
Private state lives in `struct netdev_private`, including RX/TX rings and DMA addresses, a spinlock, media and reset timers, cached CR/BCR/IMR register values, ring cursors and counts, PHY identity, MII info, and the mapped register base. `fealnx_init_one()` and `fealnx_remove_one()` implement PCI probe/remove. Netdev operations are `netdev_open()`, `netdev_close()`, `start_tx()`, `get_stats()`, `set_rx_mode()`, `mii_ioctl()`, and `fealnx_tx_timeout()`. PHY access uses `m80x_send_cmd_to_phy()`, `mdio_read()`, and `mdio_write()`. RX/TX maintenance is split across `init_ring()`, `allocate_rx_buffers()`, `netdev_rx()`, `reset_rx_descriptors()`, `reset_tx_descriptors()`, and `intr_handler()`.

## Control Flow
Probe enables the PCI device, requests BAR regions, maps IO or memory space depending on architecture, allocates netdev and coherent RX/TX descriptor rings, reads the hardware MAC address, resets the chip, discovers MII PHYs or built-in PHY type, applies module options, installs netdev/ethtool ops, and registers the netdev. Open resets hardware, requests a shared IRQ, writes the MAC address, initializes rings, programs ring bases and bus/config registers, detects link state/type, starts the net queue, enables interrupts, and starts media/reset timers. `start_tx()` maps skb data into the current TX descriptor, sets control bits, marks ownership to hardware, advances the ring, and triggers TX polling demand. `intr_handler()` masks interrupts, acknowledges ISR bits, handles RX, RBU recovery, TX completion/error accounting, tally counters, and overload-triggered delayed reset, then unmasks interrupts. Close stops queueing, disables interrupts, stops RX/TX, deletes timers, frees IRQ, and unmaps/frees outstanding skbs.

## State and Persistence
All state is volatile driver and device state. Module parameters (`debug`, `max_interrupt_work`, `rx_copybreak`, `multicast_filter_limit`, `options`, `full_duplex`) shape runtime behavior but are not persisted by the driver. Descriptor rings contain both hardware addresses and logical next pointers. Statistics are kept in `dev->stats` and per-driver counters. Link state is cached in `linkok`, `line_speed`, `duplexmode`, and CR bits.

## Dependencies and Integration Points
The driver integrates with PCI core, netdev, DMA mapping, ethtool, MII helpers, timers, and legacy IO/MMIO accessors. Device IDs cover vendor `0x1516` devices `0x0800`, `0x0803`, and `0x0891`. PHY-specific link detection handles Myson, Seeq, Ahdoc, Marvell, Myson981, LevelOne, and unknown PHYs.

## Risks
The driver predates many modern netdev patterns: no NAPI, tiny TX/RX rings, global debug/module configuration, manual timer reset recovery, and broad interrupt-side work under one spinlock. DMA mapping failures in several RX/TX paths are not consistently checked. The inactive `two_buffer` branch references `ep`, suggesting stale code. `dpaa2_dbg_ch_show`-style division is not relevant here, but this file has its own risk in `netdev_rx()` long-packet recovery and low-memory RX refill. Multicast filtering intentionally accepts all multicast after a threshold. PCI error handling and suspend/resume are absent.

## Test Signals
Important tests include PCI probe/remove, repeated ifup/ifdown, shared IRQ behavior, MII ethtool get/set/nway reset, multicast/promiscuous toggles, RX copybreak paths, TX timeout recovery, RX buffer unavailable interrupts, counter overflow accounting, link transitions across supported PHY types, and stress with small rings to exercise queue stop/wake logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fealnx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/Kconfig

## Purpose
This Kconfig file is the top-level menu for Freescale/NXP Ethernet drivers. It gates the vendor menu behind `NET_VENDOR_FREESCALE`, declares classic FEC/MPC52xx/PQ/XGMAC/UCC/Gianfar symbols, and sources submenus for fs_enet, FMan, DPAA, DPAA2, and ENETC.

## Important APIs, Types, and Functions
The significant configuration symbols are `NET_VENDOR_FREESCALE`, `FEC`, `FEC_MPC52xx`, `FEC_MPC52xx_MDIO`, `FSL_PQ_MDIO`, `FSL_XGMAC_MDIO`, `UCC_GETH`, `UGETH_TX_ON_DEMAND`, and `GIANFAR`. Symbols select dependencies such as `PHYLIB`, `PHYLINK`, `FIXED_PHY`, `PAGE_POOL`, `CRC32`, `OF_MDIO`, and Freescale platform blocks.

## Control Flow
Kconfig control flow is menu-based. `NET_VENDOR_FREESCALE` depends on a broad set of Freescale-related SoC/architecture symbols or `COMPILE_TEST`; when enabled, it exposes individual driver options and includes subdirectory Kconfig files. Downstream symbols then determine which objects the Makefiles build.

## State and Persistence
State is persisted only in kernel configuration (`.config`). No runtime state exists.

## Dependencies and Integration Points
This file integrates with the kernel networking driver Kconfig hierarchy and with `drivers/net/ethernet/freescale/Makefile`. It also establishes dependency contracts for PHY, phylink, MDIO, page pool, FMan, and DPAA subdrivers.

## Risks
Incorrect dependency expressions can expose drivers on unsupported architectures or hide valid compile-test coverage. The menu's broad default `y` makes subdriver dependencies especially important. DPAA and DPAA2 functionality depends on sourced files, so missing source statements would silently remove platform support.

## Test Signals
Useful signals are `olddefconfig` and `allyesconfig`/`allmodconfig` coverage across ARM, PPC, Layerscape, S32, and `COMPILE_TEST`, plus checking that selected symbols produce the expected object lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/Makefile

## Purpose
This Makefile maps Freescale Ethernet Kconfig symbols to built objects and subdirectories.

## Important APIs, Types, and Functions
It builds composite objects for `fec` (`fec_main.o fec_ptp.o`), `gianfar_driver` (`gianfar.o gianfar_ethtool.o`), and `ucc_geth_driver` (`ucc_geth.o ucc_geth_ethtool.o`). It conditionally descends into `fs_enet/`, `fman/`, and `dpaa/`, and always descends into `dpaa2/` and `enetc/` so their internal Makefiles can decide based on their own symbols.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_*)` variables and composite `*-objs` lists. `CONFIG_FEC_MPC52xx_MDIO=y` adds `fec_mpc52xx_phy.o` to the MPC52xx build. DPAA1 is gated here by `CONFIG_FSL_DPAA_ETH`; DPAA2 and ENETC are always visited.

## State and Persistence
There is no runtime state. Build state is produced in the kernel output tree.

## Dependencies and Integration Points
This file integrates Kconfig symbols from `freescale/Kconfig` with Kbuild. It depends on subdirectory Makefiles for DPAA2, ENETC, FMan, and fs_enet.

## Risks
Unconditional `obj-y += dpaa2/ enetc/` is intentional for subdirectory symbol resolution but can surprise readers expecting top-level gating. Composite object names must match module expectations. Mismatched Kconfig/Makefile symbols would cause silent missing drivers.

## Test Signals
Run `make drivers/net/ethernet/freescale/` under representative configs and verify expected modules/objects are emitted for FEC, Gianfar, UCC, FMan, DPAA, DPAA2, and ENETC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/Kconfig

## Purpose
This file declares the DPAA1 Ethernet driver configuration symbol.

## Important APIs, Types, and Functions
`FSL_DPAA_ETH` is a tristate menuconfig named "DPAA Ethernet". It depends on `FSL_DPAA` and `FSL_FMAN`, and selects `PHYLINK` and `PCS_LYNX`.

## Control Flow
When enabled, Kbuild enters `freescale/dpaa/Makefile` through the parent Makefile and builds the `fsl_dpa` composite module or built-in object. The help text documents that it supports Freescale QorIQ DPAA chips and requires Buffer Manager, Queue Manager, and Frame Manager support.

## State and Persistence
The only state is the kernel configuration choice.

## Dependencies and Integration Points
The symbol integrates DPAA Ethernet with the FMan MAC/port stack, QMan/BMan platform support, phylink, and Lynx PCS support.

## Risks
Missing dependency coverage can lead to build failures because `dpaa_eth.c` calls many FMan, QMan, BMan, phylink, and PCS APIs. Selecting PHYLINK/PCS here helps prevent incomplete configs.

## Test Signals
Config tests should check built-in and module builds with `FSL_DPAA`, `FSL_FMAN`, phylink, and Lynx PCS enabled; disabled dependencies should hide the option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/Makefile

## Purpose
This Makefile builds the DPAA1 Ethernet driver and exposes FMan headers to its sources.

## Important APIs, Types, and Functions
It sets `FMAN = $(srctree)/drivers/net/ethernet/freescale/fman`, adds `-I$(FMAN)` to `ccflags-y`, builds `fsl_dpa.o` when `CONFIG_FSL_DPAA_ETH` is set, and composes it from `dpaa_eth.o`, `dpaa_ethtool.o`, and `dpaa_eth_sysfs.o`. `CFLAGS_dpaa_eth.o := -I$(src)` supports local trace header inclusion.

## Control Flow
Kbuild evaluates the `obj-$(CONFIG_FSL_DPAA_ETH)` line, then links the listed objects into the composite driver. The local include path is required because `dpaa_eth.c` creates tracepoints using `dpaa_eth_trace.h`.

## State and Persistence
There is no runtime state; build artifacts are the only output.

## Dependencies and Integration Points
The file connects DPAA source files with FMan headers and the tracing framework's include expectations.

## Risks
Incorrect include paths break FMan type resolution or trace event generation. Adding new DPAA source files requires extending `fsl_dpa-objs`.

## Test Signals
Build `CONFIG_FSL_DPAA_ETH=m` and `=y`, confirm `fsl_dpa` contains all three objects, and verify tracepoint compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_eth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_eth.c

## Purpose
This is the main Freescale DPAA1 Ethernet driver. It wires netdev operations to FMan MAC/ports, QMan frame queues and congestion groups, BMan buffer pools, phylink, ethtool/sysfs sidecars, hardware timestamping, checksum offload, traffic classes, NAPI-over-QMan portals, and XDP.

## Important APIs, Types, and Functions
Important private constructs include `struct fm_port_fqs`, global `dpaa_bp_array`, `DPAA_BP_RAW_SIZE`, RX/TX headroom calculations, queue type constants, and module parameters `debug` and `tx_timeout`. Probe/remove are `dpaa_eth_probe()` and `dpaa_remove()`. Netdev ops are `dpaa_open()`, `dpaa_eth_stop()`, `dpaa_start_xmit()`, `dpaa_get_stats64()`, `dpaa_set_mac_address()`, `dpaa_set_rx_mode()`, `dpaa_setup_tc()`, `dpaa_change_mtu()`, `dpaa_xdp()`, `dpaa_xdp_xmit()`, and hardware timestamp get/set. Queue and pool management uses `dpaa_bp_alloc_pool()`, `dpaa_bp_seed()`, `dpaa_eth_refill_bpools()`, `dpaa_alloc_all_fqs()`, `dpaa_fq_setup()`, `dpaa_fq_init()`, `dpaa_fq_free()`, and congestion helpers `dpaa_eth_cgr_init()` and `dpaa_ingress_cgr_init()`.

## Control Flow
Module load reads FMan maximum frame/headroom values and registers a platform driver. Probe waits for BMan/QMan/portal readiness, allocates a multiqueue netdev, obtains the platform MAC device, configures DMA masks on FMan RX/TX port devices, creates a BMan pool and QMan FQs, allocates a QMan pool channel, configures egress and ingress congestion groups, initializes FQs and FMan ports, allocates per-CPU private data, adds NAPI objects, registers the netdev, and creates sysfs files. Open enables per-CPU NAPI, connects phylink, enables FMan ports and MAC, starts phylink, and starts all queues. Stop reverses the live datapath by stopping queues, stopping phylink, disabling MAC/ports, disconnecting PHY, and disabling NAPI.

## Packet Flow
TX pads short packets, ensures writable headroom, optionally linearizes unsupported SG depth, applies erratum A050385 alignment workarounds, builds either a contiguous or SG QMan frame descriptor, optionally requests hardware timestamping, and enqueues to a per-queue egress FQ with a confirmation FQ id in `fd.cmd`. TX confirmations and error queues call `dpaa_cleanup_tx_fd()` to unmap DMA, return XDP frames or consume/free skbs, and record timestamp data. RX callbacks refill buffer pools, reject error FDs, unmap incoming buffers, optionally run XDP for contiguous frames, build skbs from contiguous or SG FDs, attach checksum/hash/timestamp metadata, and inject into the stack with `netif_receive_skb()`.

## State and Persistence
Runtime state spans BMan pools, per-CPU buffer counts, QMan FQs, congestion groups, per-CPU stats, NAPI portal state, phylink state, MAC flags, XDP program pointer, timestamp flags, and FMan buffer-layout headroom. No persistent storage is used. The global `dpaa_bp_array` maps BPIDs to pool objects with refcounts so pools can be reused and drained safely.

## Dependencies and Integration Points
The driver depends on `soc/fsl/qman.h`, `soc/fsl/bman.h`, FMan port/MAC APIs, phylink, BPF/XDP, DMA mapping, PTP timestamping via FMan port headroom, kernel tracepoints, and the sidecar files `dpaa_ethtool.c`, `dpaa_eth_sysfs.c`, and `dpaa_eth_trace.h`.

## Risks
The driver is sensitive to DMA ownership and buffer accounting: missed decrements or failed remaps can leak pages or starve BMan pools. `dpaa_cleanup_tx_fd()` and SG conversion paths must match every mapping exactly. XDP supports only contiguous RX frames and rejects SG under XDP. Erratum A050385 rewrites or copies buffers and can affect metadata/headroom semantics. Congestion-group thresholds are speed dependent and must be updated on link changes. Probe failure unwinding crosses many subsystems and is a high-risk path. `dpaa_start_xmit()` reports `NETDEV_TX_OK` after freeing dropped skbs, so drop visibility depends on stats.

## Test Signals
Strong signals include module load/unload, probe deferral when QMan/BMan portals are missing, ifup/ifdown loops, phylink link changes, MTU and XDP MTU validation, single and multiqueue TX, SG and non-SG TX/RX, TX timestamping, RX timestamp/hash/checksum offload, XDP PASS/DROP/TX/REDIRECT, QMan congestion transitions, BMan pool low-memory refill behavior, PCD RX queue distribution, TC mqprio setup, and error FD/ERN handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_eth.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_eth.h

## Purpose
This private header defines DPAA1 Ethernet driver state shared by the main, ethtool, sysfs, and trace files.

## Important APIs, Types, and Functions
The header defines `DPAA_TC_NUM`, `enum dpaa_fq_type`, `struct dpaa_fq`, `struct dpaa_fq_cbs`, `struct dpaa_bp`, `struct dpaa_rx_errors`, `struct dpaa_ern_cnt`, `struct dpaa_napi_portal`, `struct dpaa_percpu_priv`, `struct dpaa_buffer_layout`, `struct dpaa_eth_swbp`, and `struct dpaa_priv`. It declares `dpaa_ethtool_ops`, `dpaa_eth_sysfs_init()`, and `dpaa_eth_sysfs_remove()`. Helpers `dpaa_num_txqs_per_tc()` and `dpaa_max_num_txqs()` bind TX queue scaling to `num_possible_cpus()` and four traffic classes.

## Control Flow
The header has no executable control flow, but it defines the layout used throughout the driver. FQ entries wrap QMan FQs and optional XDP RX queue metadata. Buffer pools track per-CPU counts, raw/usable size, BPID, BMan pool, seed/free callbacks, and refcounting. `dpaa_priv` is the root object behind `netdev_priv()` and connects the netdev to MAC, DMA devices, FQ arrays, congestion groups, buffer layouts, timestamp flags, and XDP program.

## State and Persistence
All represented state is runtime-only. Per-CPU stats and buffer counts are volatile. `xdp_prog` is a live BPF program pointer managed by the main driver. No file or firmware persistence is represented.

## Dependencies and Integration Points
It depends on netdev, refcount, XDP, QMan, BMan, FMan, MAC definitions, and local trace declarations. It is the key integration contract for `dpaa_eth.c`, `dpaa_ethtool.c`, `dpaa_eth_sysfs.c`, and tracing.

## Risks
Because many files share this structure layout, changes can have broad ABI-like impact inside the module. Queue-count helpers based on possible CPUs can allocate more queues than online CPUs and must stay aligned with netdev queue setup. `dpaa_eth_swbp` size must remain within `DPAA_TX_PRIV_DATA_SIZE`.

## Test Signals
Compile all DPAA objects after any structure change, then validate per-CPU stats, sysfs FQ/BPID reporting, ethtool stats, XDP RX queue registration, and traffic class queue counts on systems with different CPU online/possible masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_eth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_eth_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_eth_sysfs.c

## Purpose
This sidecar creates read-only sysfs attributes for DPAA1 netdevs, exposing MAC device address range, frame queue IDs, and buffer pool IDs.

## Important APIs, Types, and Functions
`dpaa_eth_show_addr()` prints `mac_dev->res->start` or `none`. `dpaa_eth_show_fqids()` iterates `priv->dpaa_fq_list`, groups contiguous FQID ranges of the same queue type, and labels RX default/error/PCD, TX, TX confirmation, and TX error queues. `dpaa_eth_show_bpids()` prints the primary BPID. `dpaa_eth_sysfs_init()` creates `device_addr`, `fqids`, and `bpids`; `dpaa_eth_sysfs_remove()` removes them.

## Control Flow
Probe calls `dpaa_eth_sysfs_init()` after registering the netdev. If any attribute creation fails, the function removes earlier files and returns without aborting probe. Remove calls `dpaa_eth_sysfs_remove()` to delete all known attributes.

## State and Persistence
The file exposes live driver state but does not own persistent state. Attribute contents reflect the current `dpaa_priv`, FQ list, and buffer pool.

## Dependencies and Integration Points
It depends on `to_net_dev()`, `netdev_priv()`, `struct dpaa_priv`, list traversal, and Linux device attributes. It integrates with the main driver's probe/remove lifecycle.

## Risks
The show methods use `sprintf()`/manual byte counts and assume output fits in a page. Very large FQ lists can approach sysfs page limits. The FQ grouping compares string pointer identity (`str == prevstr`), which is safe here because labels are string literals assigned in the switch. `dpaa_eth_sysfs_remove()` removes all attributes regardless of whether creation partially failed, which is acceptable for device attributes.

## Test Signals
Check `/sys/class/net/<if>/device_addr`, `fqids`, and `bpids` after probe; validate output on interfaces with many TX queues and PCD queues; exercise partial creation failure via fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_eth_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_eth_trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_eth_trace.h

## Purpose
This trace header declares DPAA1 Ethernet tracepoints for QMan frame descriptors on TX, RX, and TX confirmation paths.

## Important APIs, Types, and Functions
The trace system is `dpaa_eth`. `DECLARE_EVENT_CLASS(dpaa_eth_fd)` captures FQID, frame descriptor address, format, offset, length, status, and netdev name. `DEFINE_EVENT()` instantiates `dpaa_tx_fd`, `dpaa_rx_fd`, and `dpaa_tx_conf_fd`. `fd_format_list` renders contiguous and SG frame descriptor formats.

## Control Flow
There is no normal control flow. `dpaa_eth.c` defines `CREATE_TRACE_POINTS` before including this header, causing tracepoint definitions to be emitted once. Other source files can include it for declarations.

## State and Persistence
Tracepoints record transient event data into the kernel tracing infrastructure when enabled. They do not persist state themselves.

## Dependencies and Integration Points
The header depends on Linux tracepoint macros, skbuff/netdev headers, QMan FD helpers from `dpaa_eth.h`, and `TRACE_INCLUDE_PATH .` plus `TRACE_INCLUDE_FILE dpaa_eth_trace` so generated trace code can find the local header.

## Risks
Trace field extraction must avoid side effects and must stay compatible with QMan FD layout. Include recursion and `TRACE_HEADER_MULTI_READ` guards must remain correct. Renaming the file or changing Makefile include flags can break trace generation.

## Test Signals
Build with tracing enabled, verify events appear under tracing/events/dpaa_eth, and enable `dpaa_tx_fd`, `dpaa_rx_fd`, and `dpaa_tx_conf_fd` during traffic to confirm sane FQID/address/format output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_eth_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_ethtool.c

## Purpose
This file implements DPAA1 ethtool operations for link settings, pause, message level, detailed statistics, RX hash controls, timestamp capabilities, QMan interrupt coalescing, and standard MAC/RMON/pause stats delegation.

## Important APIs, Types, and Functions
The exported object is `dpaa_ethtool_ops`. Link operations delegate to phylink (`dpaa_get_link_ksettings()`, `dpaa_set_link_ksettings()`, `dpaa_nway_reset()`, pause get/set). Stats are described by `dpaa_stats_percpu` and `dpaa_stats_global`, filled by `dpaa_get_ethtool_stats()`, and named by `dpaa_get_strings()`. RX hash controls are `dpaa_get_rxfh_fields()` and `dpaa_set_rxfh_fields()`. Timestamp info is `dpaa_get_ts_info()`. Coalescing is handled by `dpaa_get_coalesce()` and `dpaa_set_coalesce()`.

## Control Flow
Ettool calls enter through the ops table. Stats iterate online CPUs, copy per-CPU counters plus per-CPU BMan pool counts, aggregate RX error and ERN counters, query congestion status, and reset congestion time/count after reporting. RXFH enables or disables FMan keygen hashing based on supported IP/L4 field masks. Coalescing reads or writes QMan portal interrupt period/threshold on affine online CPUs, reverting prior portals if a later update fails.

## State and Persistence
This file reads and mutates live driver state: `msg_enable`, `keygen_in_use`, per-CPU stats, buffer pool counts, congestion counters, and QMan portal coalescing settings. Changes are runtime-only.

## Dependencies and Integration Points
It integrates with phylink, FMan MAC statistic callbacks, QMan portal APIs, OF/PTP lookup for PHC index, and DPAA private structures. It also uses ethtool's modern stats, RXFH, timestamp, and coalesce interfaces.

## Risks
Stats sizing depends on `num_online_cpus()` at get-count/get-strings/get-stats time; CPU hotplug between calls can confuse userspace buffer expectations. `dpaa_get_ethtool_stats()` resets congestion counters as a read side effect. `dpaa_get_coalesce()` reports the current CPU's portal values, while setting attempts all affine online portals. PTP lookup depends on the FMan node's `ptimer-handle`.

## Test Signals
Run `ethtool -S`, `-k`, `-c`, `-C`, `-n`/RXFH field operations, pause operations, link setting changes, and `ethtool -T`. Include CPU hotplug/coalescing failure injection and traffic that exercises ERN and congestion counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/Kconfig

## Purpose
This Kconfig file declares DPAA2 Ethernet, optional DPAA2 DCB support, DPAA2 PTP clock support, and DPAA2 switch support.

## Important APIs, Types, and Functions
`FSL_DPAA2_ETH` depends on `FSL_MC_BUS` and `FSL_MC_DPIO`, and selects `PHYLINK`, `PCS_LYNX`, `FSL_XGMAC_MDIO`, and `NET_DEVLINK`. `FSL_DPAA2_ETH_DCB` depends on `DCB` and is available only under DPAA2 Ethernet. `FSL_DPAA2_PTP_CLOCK` depends on DPAA2 Ethernet plus `PTP_1588_CLOCK_QORIQ`. `FSL_DPAA2_SWITCH` depends on bridge/switchdev plus MC/DPIO and selects phylink/PCS/MDIO support.

## Control Flow
When symbols are enabled, `dpaa2/Makefile` selects the corresponding composite objects. DCB support conditionally adds `dpaa2-eth-dcb.o`; debugfs is controlled separately by `CONFIG_DEBUG_FS`.

## State and Persistence
The only state is kernel configuration.

## Dependencies and Integration Points
This file connects DPAA2 Ethernet to the Freescale Management Complex bus, DPIO portals, phylink, Lynx PCS, XGMAC MDIO, devlink, PTP, DCB, and switchdev.

## Risks
Missing `NET_DEVLINK` would break devlink support in `dpaa2-eth-devlink.c`; missing MC/DPIO would expose a driver with no device/control-plane substrate. Optional DCB must stay gated because `dpaa2-eth-dcb.c` depends on DCB netlink types.

## Test Signals
Config build DPAA2 Ethernet with and without DCB, PTP, switch, and debugfs; verify symbols are hidden when MC/DPIO dependencies are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/Makefile

## Purpose
This Makefile composes DPAA2 Ethernet, MAC, PTP, and switch drivers.

## Important APIs, Types, and Functions
`fsl-dpaa2-eth` is built from `dpaa2-eth.o`, `dpaa2-ethtool.o`, `dpni.o`, `dpaa2-eth-devlink.o`, and `dpaa2-xsk.o`, with conditional additions for DCB and debugfs. `fsl-dpaa2-ptp` uses `dpaa2-ptp.o dprtc.o`. `fsl-dpaa2-switch` uses switch core, ethtool, DPSW, and flower files. `fsl-dpaa2-mac` includes `dpaa2-mac.o dpmac.o`. `CFLAGS_dpaa2-eth.o := -I$(src)` supports trace header generation.

## Control Flow
Kbuild selects composite objects based on `CONFIG_FSL_DPAA2_ETH`, `CONFIG_FSL_DPAA2_PTP_CLOCK`, `CONFIG_FSL_DPAA2_SWITCH`, `CONFIG_FSL_DPAA2_ETH_DCB`, and `CONFIG_DEBUG_FS`.

## State and Persistence
There is no runtime state in the Makefile.

## Dependencies and Integration Points
The file integrates the main DPAA2 Ethernet driver with MC command files (`dpni`, `dpmac`, `dprtc`, `dpsw`), optional debugfs/DCB sidecars, AF_XDP support, PTP, and switchdev support.

## Risks
Conditional object syntax must match Kbuild expectations; missing optional object entries would compile but silently omit features. Trace include flags must stay aligned with `dpaa2-eth-trace.h`.

## Test Signals
Build each symbol combination as module and built-in, especially DCB on/off and debugfs on/off, and confirm the expected objects are linked into each composite module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-dcb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-dcb.c

## Purpose
This optional DPAA2 Ethernet sidecar implements DCB netlink operations for IEEE Priority Flow Control.

## Important APIs, Types, and Functions
The exported object is `dpaa2_eth_dcbnl_ops`. `dpaa2_eth_dcbnl_ieee_getpfc()` reports stored PFC state when PFC pause is enabled. `dpaa2_eth_dcbnl_ieee_setpfc()` validates unsupported fields, updates DPNI link options, configures congestion notifications by priority via `dpaa2_eth_set_pfc_cn()`, stores `priv->pfc`, updates `priv->pfc_enabled`, and adjusts RX taildrop. `dpaa2_eth_dcbnl_getdcbx()`, `setdcbx()`, and `getcap()` expose DCBX mode and capabilities.

## Control Flow
Userspace DCB changes enter through rtnetlink DCBNL ops. Setting PFC first rejects MBC/delay, skips no-op masks, warns if pause support is not enabled, toggles `DPNI_LINK_OPT_PFC_PAUSE` through `dpni_set_link_cfg()`, configures per-TC congestion thresholds, and updates driver state.

## State and Persistence
Runtime state is in `priv->pfc`, `priv->pfc_enabled`, `priv->dcbx_mode`, and Management Complex DPNI link/congestion configuration. No persistent storage is used.

## Dependencies and Integration Points
The file depends on `dpaa2-eth.h`, DCB netlink types, DPNI commands, link-state helpers, traffic-class count helpers, congestion threshold macros, and RX taildrop configuration from the main driver.

## Risks
`getcap()` reports `1 << (tc_count - 1)` for PFC TCs, which must match DCB expectations for advertised capability. PFC configuration may be accepted while pause is disabled, producing a warning but no immediate effect. Partial failure after link config but before local state update can leave hardware and software state divergent.

## Test Signals
Use `dcb pfc show/set`, test unsupported MBC/delay rejection, toggle pause and PFC combinations, verify DPNI congestion thresholds per TC, and test failure injection for `dpni_set_link_cfg()` and `dpni_set_congestion_notification()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-dcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-debugfs.c

## Purpose
This optional debugfs sidecar exposes DPAA2 Ethernet internal counters for per-CPU stats, frame queues, channels, and buffer pools under a `dpaa2-eth` debugfs root.

## Important APIs, Types, and Functions
Show functions are `dpaa2_dbg_cpu_show()`, `dpaa2_dbg_fqs_show()`, `dpaa2_dbg_ch_show()`, and `dpaa2_dbg_bp_show()`, each wrapped by `DEFINE_SHOW_ATTRIBUTE`. Lifecycle functions are `dpaa2_eth_dbg_init()`, `dpaa2_eth_dbg_exit()`, `dpaa2_dbg_add()`, and `dpaa2_dbg_remove()`.

## Control Flow
Module init creates the root directory. Per-interface probe calls `dpaa2_dbg_add()`, which creates a `dpni.<id>` directory and files `cpu_stats`, `fq_stats`, `ch_stats`, and `bp_stats`. Reads format current state through seq_file. Remove recursively deletes the per-interface directory, and module exit removes the root.

## State and Persistence
Debugfs state consists of dentries only. File contents are live views of `dpaa2_eth_priv` counters, FQ state, channel state, and buffer pool state. Nothing is persisted.

## Dependencies and Integration Points
The file depends on `debugfs`, `seq_file`, DPAA2 private structures, DPIO query helpers (`dpaa2_io_query_fq_count()` and `dpaa2_io_query_bp_count()`), and `fsl_mc_device` object IDs.

## Risks
`dpaa2_dbg_ch_show()` divides frames by CDAN count without a zero guard, so a channel with zero CDANs can fault during debugfs read. Debugfs creation errors are not checked in `dpaa2_dbg_add()`. Names are limited to 10 bytes, which fits `dpni.%d` for typical IDs but truncation is possible for large object IDs.

## Test Signals
Mount debugfs and read all files before and after traffic, with idle channels, multiple CPUs, multiple buffer pools, and interfaces removed while files are open. Specifically validate zero-CDAN behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-debugfs.h

## Purpose
This header provides the DPAA2 Ethernet debugfs interface contract and no-op stubs when debugfs is disabled.

## Important APIs, Types, and Functions
It defines `struct dpaa2_debugfs` containing a per-interface `struct dentry *dir`. Under `CONFIG_DEBUG_FS`, it declares init/exit and per-interface add/remove functions. Otherwise, it defines inline empty stubs for the same functions.

## Control Flow
The header lets the main driver call debugfs lifecycle hooks unconditionally. Compile-time configuration chooses real implementations or no-ops.

## State and Persistence
State is limited to a dentry pointer stored in the main private structure. There is no persistence.

## Dependencies and Integration Points
It depends on `linux/dcache.h` and forward-declares `struct dpaa2_eth_priv`. It is included by the debugfs implementation and the main DPAA2 driver.

## Risks
The stubbed API hides debugfs absence cleanly, but callers must not assume `priv->dbg.dir` is valid when debugfs is disabled. Any additions to the implementation API must be mirrored in both branches.

## Test Signals
Compile with `CONFIG_DEBUG_FS=y` and `n`, then exercise module init/probe/remove paths in both configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-devlink.c

## Purpose
This file implements DPAA2 Ethernet devlink support: driver info, physical devlink port registration, and parser-error drop traps.

## Important APIs, Types, and Functions
`dpaa2_eth_devlink_ops` provides `info_get`, `trap_init`, independent trap action rejection, and trap group action setting. `dpaa2_eth_dl_alloc/free/register/unregister()` manage the devlink instance. `dpaa2_eth_dl_port_add/del()` manage the physical devlink port. `dpaa2_eth_dl_traps_register/unregister()` install generic parser-error traps. `dpaa2_eth_dl_get_trap()` maps frame annotation parser error bits to registered trap items.

## Control Flow
Probe allocates a devlink, registers trap groups and traps, adds a physical port, and later registers devlink. Trap initialization stores trap contexts in `priv->trap_data`. Error frame processing in the main driver can call `dpaa2_eth_dl_get_trap()` to identify the devlink trap item from FAF bits. Trap group action changes configure DPNI error behavior: drop means discard parser-error frames, trap means send them to the error queue with annotations.

## State and Persistence
Runtime state includes `priv->devlink`, `priv->devlink_port`, `priv->trap_data`, dynamically allocated trap item arrays, and DPNI error behavior programmed in the Management Complex. There is no persistence.

## Dependencies and Integration Points
The file depends on devlink, DPNI MC commands, DPAA2 parser annotation structures, generic devlink trap IDs, and main-driver fields such as DPNI version and MC token.

## Risks
Trap mapping relies on hard-coded FAF bit positions and endian conversions; wrong positions misclassify drops. Only group action changes are supported, not independent trap actions. Failure unwinding must unregister groups/traps and free allocations in exact reverse order. The label `trap_groups_unregiser` is misspelled but harmless.

## Test Signals
Use `devlink dev info`, `devlink trap show`, `devlink trap set group parser_error_drops action trap/drop`, inject parser errors for each supported protocol bit, and run allocation/failure-injection tests through trap registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-trace.h

## Purpose
This trace header declares DPAA2 Ethernet tracepoints for frame descriptors and raw buffer pool seeding events, including AF_XDP-specific paths.

## Important APIs, Types, and Functions
Trace system is `dpaa2_eth`. Event class `dpaa2_eth_fd` captures FD address, length, offset, and netdev name; events include `dpaa2_tx_fd`, `dpaa2_tx_xsk_fd`, `dpaa2_rx_fd`, `dpaa2_rx_xsk_fd`, and `dpaa2_tx_conf_fd`. Event class `dpaa2_eth_buf` captures virtual address, size, DMA address, DMA map size, BPID, and netdev name; events include `dpaa2_eth_buf_seed` and `dpaa2_xsk_buf_seed`.

## Control Flow
No normal control flow exists. The main DPAA2 source defines `CREATE_TRACE_POINTS` once, and the tracing framework expands this header into tracepoint definitions. Other files include it for declarations.

## State and Persistence
Tracepoints emit transient records only when enabled by ftrace/perf infrastructure. They own no persistent state.

## Dependencies and Integration Points
The header depends on Linux tracepoint macros, netdev/skbuff headers, DPAA2 FD accessor functions, and `TRACE_INCLUDE_PATH .`/`TRACE_INCLUDE_FILE dpaa2-eth-trace`. It integrates with main DPAA2 TX/RX, TX confirmation, buffer seeding, and AF_XDP code paths.

## Risks
Trace definitions must match the available `struct dpaa2_fd` accessors and local include path. Printing DMA address by pointer to `__entry->dma_addr` must stay compatible with `%pad`. Header guard and `TRACE_HEADER_MULTI_READ` handling are important for trace generation.

## Test Signals
Build with tracing enabled, inspect tracing/events/dpaa2_eth, enable each FD and buffer event during normal and AF_XDP traffic, and verify address/length/offset/BPID fields are plausible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-trace.h -->
