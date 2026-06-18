# subset-b-004421 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/ntmp_private.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/ntmp_private.h

### Purpose
`ntmp_private.h` defines private command-buffer data formats for the ENETC NETC Table Management Protocol (NTMP). It is a packing contract between ENETC driver code and NETC command BD rings: callers fill request headers and request data buffers for table add/update/query/delete operations, and parse response headers/data returned by hardware.

### Important APIs, Types, And Functions
The central type is `union netc_cbd`, which overlays the command buffer descriptor request header and response header. Request fields include DMA address, encoded request/response lengths via `NTMP_LEN()`, command bits (`NTMP_CMD_ADD`, `NTMP_CMD_UPDATE`, `NTMP_CMD_QUERY`, `NTMP_CMD_DELETE`, and query-update `NTMP_CMD_QU`), access methods (`NTMP_AM_ENTRY_ID`, `NTMP_AM_EXACT_KEY`, `NTMP_AM_SEARCH`, `NTMP_AM_TERNARY_KEY`), table id, header version, CCI/RR bits, and NPF. Response fields include matched count and encoded NTMP error/RR bits. The header also defines common request data (`struct ntmp_cmn_req_data`), query response common data (`struct ntmp_cmn_resp_query`), entry-id requests (`struct ntmp_req_by_eid`), MAC address filter table add/query buffers (`struct maft_req_add`, `struct maft_resp_query`), and RSS table update buffers (`struct rsst_req_update` with flexible `groups[]`).

### Control Flow
There is no executable control flow in the header. Runtime flow is implied: NTMP users allocate or map request/response buffers, fill `union netc_cbd.req_hdr`, select an access method and command, submit the descriptor to a NETC CBD ring, and later inspect `union netc_cbd.resp_hdr` plus table-specific response data. `FIELD_PREP()` and masks from `linux/bitfield.h` centralize bitfield packing so command producers do not hand-code shifts.

### State, Persistence, And Dependencies
The file owns no runtime state. State lives in hardware tables modified by NTMP commands and in DMA buffers described by the CBD. The on-wire/in-memory structures are little-endian and depend on `<linux/fsl/ntmp.h>` for table-specific key/config element structures such as `maft_keye_data`, `maft_cfge_data`, and RSS data semantics.

### Integration Points
This header integrates ENETC NETC command-ring code with NXP's public NTMP table definitions. Expected users are ENETC `ntmp.c`, CBDR helpers, and table-management routines for MAC filters and RSS indirection. The constants `NETC_CBDR_BD_NUM`, `NETC_CBDRCIR_INDEX`, `NETC_CBDRCIR_SBE`, and `NETC_CBDR_CLEAN_WORK` also couple command descriptors to ring management logic.

### Risks
The risk profile is ABI/layout driven. Any structure padding, endianness mismatch, wrong length encoding, or table-version/query-action packing error will cause hardware command rejection or silent table corruption. `struct rsst_req_update` has a flexible array, so callers must size DMA buffers carefully. Command bit combinations are open-coded flags, making invalid combinations possible unless call sites validate them.

### Test Signals
Useful signals are compile-time layout checks where available, NTMP add/query/delete round trips for MAC filter table entries, RSS update verification, command rejection/error code parsing, CBDR wraparound with `NETC_CBDR_BD_NUM`, and endian-sensitive tests on little-endian descriptor fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/ntmp_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec.h

### Purpose
`fec.h` is the shared private header for the main NXP/Freescale Fast Ethernet Controller driver (`fec_main.c`) and its PTP companion (`fec_ptp.c`). It defines register offsets for multiple FEC register layouts, descriptor formats, interrupt/status bits, queue sizing, SoC quirk flags, per-queue state, the main private device state, and the PTP function contract.

### Important APIs, Types, And Functions
The file defines two register offset sets: the common FEC/ENET layout and the `CONFIG_M5272` ColdFire layout. It abstracts descriptor endianness with `fec16_to_cpu`, `fec32_to_cpu`, `cpu_to_fec16`, and `cpu_to_fec32`, because ARM/ARM64 FEC blocks use little-endian descriptors while other platforms use big-endian ordering. `struct bufdesc` is the basic RX/TX descriptor, and `struct bufdesc_ex` adds enhanced fields for checksum, VLAN, AVB queue, and timestamp support.

Important state types are `struct bufdesc_prop`, `struct fec_enet_priv_tx_q`, `struct fec_enet_priv_rx_q`, `union fec_rx_buffer`, `struct fec_tx_buffer`, `enum fec_txbuf_type`, `struct fec_stop_mode_gpr`, and `struct fec_enet_private`. `fec_enet_private` owns MMIO base, clocks, queue arrays, platform and PHY/MDIO data, IRQs, quirk flags, NAPI, work items, PTP clock/timecounter fields, interrupt coalescing settings, stop-mode state, XDP program pointer, AF_XDP pools via queues, and flexible ethtool stats storage. The exported internal PTP declarations are `fec_ptp_init()`, `fec_ptp_stop()`, `fec_ptp_start_cyclecounter()`, `fec_ptp_save_state()`, `fec_ptp_restore_state()`, `fec_ptp_set()`, and `fec_ptp_get()`.

### Control Flow
The header has no runtime control flow but strongly shapes it. `fec_main.c` uses descriptor and ring metadata to allocate queues, start hardware, transmit SKBs/TSO/XDP frames, receive into page pools or XSK buffers, and clean descriptors. PTP flow is enabled when `FEC_QUIRK_HAS_BUFDESC_EX` and a PTP clock are available, with enhanced descriptors carrying timestamps. Quirk bits gate large areas of driver behavior: ENET-MAC mode, frame byte swapping, gasket setup, gigabit support, enhanced descriptors, checksum/VLAN offloads, AVB multi-queue support, hardware erratum workarounds, RACC, coalescing, EEE, wakeup, MDIO Clause 45, and jumbo frames.

### State, Persistence, And Dependencies
Runtime state is entirely in kernel memory and hardware registers. It is not persisted across reboot, but the driver may save and restore PTP time state across MAC reset using `ptp_saved_state`. Dependencies include Linux BPF/XDP, page pool, PTP clock/timecounter, phylib, PM QoS, i.MX SCU firmware, and dt-bindings for i.MX resources.

### Integration Points
The header is the compile-time integration point between the main netdev implementation and PTP implementation. It also maps hardware details into Linux networking subsystems: netdev features, XDP memory models, page pools, MDIO/PHY, runtime PM, and ethtool stats.

### Risks
Descriptor layout and endian selection are high risk because they affect DMA ownership. Several constants are power-of-two or alignment-sensitive (`TX_RING_SIZE`, `TX_RING_MOD_MASK`, XDP headroom, descriptor size log2). Quirk combinations must match actual SoC integration; a wrong quirk can enable unsupported registers or omit required errata handling. `struct fec_enet_private` is a shared contract, so field changes can break PTP, PM, XDP, and queue logic together.

### Test Signals
Build coverage should include ARM/ARM64, ColdFire/M5272, COMPILE_TEST, PTP-enabled and PTP-disabled variants. Runtime signals include descriptor wrap handling, multi-queue AVB routing, checksum/VLAN offloads, XDP/AF_XDP paths, PTP timestamp availability, suspend/resume with WOL, and jumbo MTU configuration on quirked hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec_main.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec_main.c

### Purpose
`fec_main.c` implements the platform net_device driver for NXP/Freescale FEC/ENET MACs across ColdFire and i.MX-family SoCs. It handles probing, clock/regulator/runtime-PM setup, MDIO/PHY integration, descriptor rings, NAPI RX/TX polling, normal SKB transmit, software TSO descriptorization, checksum/VLAN offloads, PTP timestamp hooks, interrupt coalescing, Energy Efficient Ethernet, Wake-on-LAN, XDP, AF_XDP zero-copy, ethtool, suspend/resume, and SoC erratum workarounds.

### Important APIs, Types, And Functions
The driver registers `fec_driver` as a platform driver named `fec` with OF matches for `fsl,imx25-fec`, `imx27`, `imx28`, `imx6q`, `mvf600`, `imx6sx`, `imx6ul`, `imx8mq`, `imx8qm`, and `s32v234`. Each match maps to a `struct fec_devinfo` quirk set. Netdev operations are in `fec_netdev_ops`: `fec_enet_open()`, `fec_enet_close()`, `fec_enet_start_xmit()`, queue selection, multicast filtering, MAC address changes, MTU changes, feature toggles, BPF/XDP setup, XDP transmit, AF_XDP wakeup, and hwtstamp get/set. Ettool operations are in `fec_enet_ethtool_ops`.

Key lifecycle functions are `fec_probe()`, `fec_drv_remove()`, `fec_enet_init()`, `fec_enet_deinit()`, `fec_restart()`, `fec_stop()`, `fec_suspend()`, `fec_resume()`, `fec_runtime_suspend()`, and `fec_runtime_resume()`. TX functions include descriptor helpers, `fec_enet_txq_submit_skb()`, `fec_enet_txq_submit_tso()`, `fec_enet_start_xmit()`, and `fec_enet_tx_queue()`. RX functions include `fec_enet_rx_queue()`, `fec_enet_rx_queue_xdp()`, `fec_enet_rx_queue_xsk()`, and `fec_build_skb()`. MDIO/PHY functions include `fec_enet_mii_init()`, Clause 22/45 read/write helpers, `fec_enet_mii_probe()`, and `fec_enet_adjust_link()`.

### Control Flow
Probe allocates a multi-queue Ethernet device, chooses quirks from OF or platform id data, maps MMIO, parses WOL, stop-mode, PHY/fixed-link, PHY mode, RGMII delays, clocks, optional regulator, runtime PM, resets the PHY, initializes PTP if enhanced descriptors are usable, allocates descriptor rings and queues, requests IRQs, creates/registers the MDIO bus, sets carrier down, configures MTU/buffer sizing, and registers the netdev.

Open resumes runtime PM, selects pinctrl default state, enables clocks, allocates RX/TX buffers, calls `fec_restart()` to program hardware and rings, connects to the PHY, enables NAPI, starts phylib, and starts TX queues. Link changes call `fec_enet_adjust_link()`, which restarts the MAC on speed/duplex changes or stops it on link down. Interrupts only collect/clear non-MDIO events and schedule NAPI. NAPI loops over RX and TX work until the budget is reached or no events remain, then reenables interrupts.

Transmit maps SKB heads/fragments or TSO-generated header/data descriptors, uses bounce buffers for alignment or frame-swap variants, marks descriptors ready with memory barriers, stores cleanup state in `tx_buf[]`, and triggers TDAR with erratum-aware logic. TX cleanup unmaps DMA, completes SKBs or XDP frames, extracts TX hardware timestamps from enhanced descriptors, updates stats, wakes stopped queues, handles AF_XDP completions, and keeps transmit active for ERR006358. RX consumes descriptors, checks status bits, updates/replaces page-pool or XSK buffers before handing packets up, handles VLAN/checksum/timestamps from enhanced descriptors, and dispatches through normal GRO, XDP_PASS/DROP/TX/REDIRECT, or AF_XDP zero-copy flows.

### State, Persistence, And Dependencies
Persistent state is limited to hardware registers while the device is powered and software fields in `struct fec_enet_private`. The driver maintains descriptor rings in DMA memory, page pools, XSK pools, PTP timecounter state, ethtool statistic snapshots, runtime PM status, WOL flags, PHY link state, and PM QoS requests. It depends on platform devices/OF, clk/regulator/pinctrl APIs, phylib and fixed PHY, MDIO, NAPI/netdev core, DMA mapping, page_pool, BPF/XDP/AF_XDP, PTP via `fec_ptp.c`, i.MX cpuidle/SCU stop-mode integration, and ethtool selftests.

### Integration Points
The file is the main integration layer between FEC hardware and Linux networking. It exposes netdev and ethtool operations, registers an MDIO bus for PHY devices, calls PTP helpers for PHC and timestamp configuration, uses devm IRQ/resource management for platform resources, participates in runtime and system sleep PM, and advertises XDP features when hardware does not require software frame swapping.

### Risks
High-risk areas are DMA descriptor ownership, memory barriers, ring wrap and dirty/cur pointer math, mixed SKB/XDP/XSK cleanup types, and restart paths that free or reuse descriptors while NAPI/TX may be active. PM paths are subtle because MDIO operations resume runtime PM, WOL may keep ENET partially enabled, and clocks/regulators affect PHY link state. SoC quirks are critical; wrong quirk data can break timestamping, MDIO, reset, endian/frame swapping, coalescing, or multi-queue registers. The file also has complex failure unwinds in probe/open and comments noting cleanup limitations in `fec_enet_init()`.

### Test Signals
Signals include successful probe/register on each compatible, MDIO Clause 22/45 scans, PHY link up/down and speed/duplex changes, suspend/resume and runtime PM MDIO access, WOL magic packet wake, TX timeout recovery, normal RX/TX under stress, TSO and SG transmit, checksum/VLAN offloads, ethtool stats/register dumps/coalescing/EEE/pause/WOL, PTP hwtstamp get/set, XDP basic/redirect/TX, AF_XDP zero-copy RX/TX/wakeup, multi-queue VLAN priority selection, jumbo MTU on i.MX8QM, and fault injection for DMA map/page allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec_mpc52xx.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec_mpc52xx.c

### Purpose
`fec_mpc52xx.c` implements a separate Ethernet driver for the MPC5200/MPC52xx Fast Ethernet Controller. Unlike the modern `fec_main.c` driver, it uses the MPC52xx BestComm DMA engine and a big-endian register block described by `fec_mpc52xx.h`.

### Important APIs, Types, And Functions
The private state `struct mpc52xx_fec_priv` stores the net_device, duplex/speed/link state, control/RX/TX IRQs, MMIO register pointer, BestComm RX/TX tasks, a spinlock, message level, MDIO speed, optional PHY node, and seven-wire mode flag. Netdev operations are `mpc52xx_fec_open()`, `mpc52xx_fec_close()`, `mpc52xx_fec_start_xmit()`, `mpc52xx_fec_set_multicast_list()`, `mpc52xx_fec_set_mac_address()`, `mpc52xx_fec_tx_timeout()`, and `mpc52xx_fec_get_stats()`. Driver lifecycle functions are `mpc52xx_fec_probe()`, `mpc52xx_fec_remove()`, suspend/resume hooks, and module init/exit registering this driver plus the optional MDIO platform driver.

### Control Flow
Probe allocates an Ethernet device, maps the FEC control registers, initializes BestComm RX/TX tasks using FIFO register addresses, obtains control and BestComm task IRQs, reads a MAC address from DT or hardware registers, falls back to a random address if invalid, parses current speed/duplex and `phy-handle`, handles `fsl,7-wire-mode`, initializes hardware, resets stats, and registers the netdev. Open optionally connects to the PHY, requests three IRQs, resets BestComm tasks, allocates RX SKBs into the BestComm RX queue, enables DMA tasks, starts the FEC, and starts the netdev queue.

Transmit prepares a BestComm TX buffer descriptor, DMA maps the SKB data, submits it, timestamps in software, and stops the queue if the BestComm queue is full. The TX IRQ retrieves completed buffers, unmaps DMA, consumes SKBs, and wakes the queue. The RX IRQ loops completed RX buffers, drops errored frames, allocates a replacement SKB before handing up the completed one, unmaps DMA, strips the CRC, sets protocol, defers RX timestamp handling if needed, and calls `netif_rx()`. Control IRQ clears non-MII events and soft-resets the MAC on FIFO errors.

### State, Persistence, And Dependencies
State is volatile: MMIO registers, BestComm task rings, queued SKBs, PHY link state, and net_device stats. The driver depends on OF address/IRQ helpers, phylib/of_mdio, BestComm FEC task helpers, big-endian MMIO accessors, CRC32 multicast hashing, and the companion MDIO driver symbol when `CONFIG_FEC_MPC52xx_MDIO` is enabled.

### Integration Points
The module registers an OF platform driver for `fsl,mpc5200b-fec`, `fsl,mpc5200-fec`, and `mpc5200-fec`. It integrates with phylib through `of_phy_connect()`, with ethtool for message level/link settings, and with the BestComm subsystem for DMA queueing.

### Risks
The RX path allocates replacement SKBs under the RX interrupt path and drops packets on allocation failure. Reset paths run under spinlock and rebuild DMA queues, so BestComm queue state must stay consistent. There is no NAPI; heavy interrupt load can be expensive. Hardware register writes are endian-sensitive. Probe/open unwind paths involve several resources (mem region, ioremap, two BestComm tasks, three IRQs, PHY references), making error handling important.

### Test Signals
Test signals include OF probe on MPC5200-compatible nodes, MAC address fallback, open/close with and without PHY node, RX/TX traffic under stress, TX queue full/wakeup behavior, FIFO error reset recovery, multicast/promiscuous filters, stats counter reads/resets, suspend/resume while running, and optional MDIO-driver registration ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec_mpc52xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec_mpc52xx.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec_mpc52xx.h

### Purpose
`fec_mpc52xx.h` describes the MPC5200 FEC hardware register block and bit definitions used by the MPC52xx Ethernet and MDIO drivers. It is a low-level register contract, not a public API.

### Important APIs, Types, And Functions
The main type is `struct mpc52xx_fec`, a full memory-map layout from `fec_id` through MAC, FIFO, DMA/status, and RMON/IEEE MIB counters. The header defines queue and buffer constants (`FEC_RX_BUFFER_SIZE`, `FEC_RX_NUM_BD`, `FEC_TX_NUM_BD`), reset/watchdog timings, MIB disable bit, interrupt event/mask bits, receive/transmit control bits, Ethernet control bits, MII management frame fields, FIFO status/control bits, reset control bits, transmit FSM CRC bits, and pause opcode constants. It also declares `extern struct platform_driver mpc52xx_fec_mdio_driver`.

### Control Flow
No executable flow is present. `fec_mpc52xx.c` uses the structure and constants to reset/configure the MAC, enable interrupts, program FIFO thresholds, update link mode, set MAC address and multicast filters, read statistics, and control RX/TX. `fec_mpc52xx_phy.c` uses the MII frame constants and `mii_speed` register to implement MDIO transfers.

### State, Persistence, And Dependencies
The structure maps hardware state directly through big-endian MMIO. The only dependency is `<linux/phy.h>` for the MDIO platform driver declaration context. Runtime persistence is hardware-defined; register state is reinitialized by probe/start/resume/reset paths.

### Integration Points
This header is shared only inside the MPC52xx FEC driver pair. The exported MDIO driver declaration lets `fec_mpc52xx.c` register the MDIO bus driver before the MAC driver when built together.

### Risks
Register offsets must match the MPC5200 reference manual; any field displacement corrupts all MMIO access. The structure contains reserved arrays to preserve offsets, so edits are risky. MII bit shifts/masks are used by both MAC and MDIO logic; incorrect values cause PHY access timeouts or wrong register access.

### Test Signals
Build tests should cover `CONFIG_FEC_MPC52xx` and optional `CONFIG_FEC_MPC52xx_MDIO`. Runtime signals include successful reset, MDIO read/write, FIFO setup, interrupt acknowledgement, MAC address programming, RMON/IEEE stat reads, and link duplex transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec_mpc52xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec_mpc52xx_phy.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec_mpc52xx_phy.c

### Purpose
`fec_mpc52xx_phy.c` implements the MDIO bus driver for the MPC5200 FEC MII management interface. It exposes FEC MII read/write operations as a Linux `mii_bus` so PHY devices described under OF can be registered and used by the MPC52xx FEC MAC driver.

### Important APIs, Types, And Functions
`struct mpc52xx_fec_mdio_priv` stores the mapped FEC register block. `mpc52xx_fec_mdio_transfer()` is the core helper: it packs PHY address, register address, and read/write frame bits into `mii_data`, clears the MII event, waits for completion, and returns read data or timeout. `mpc52xx_fec_mdio_read()` and `mpc52xx_fec_mdio_write()` are `mii_bus` callbacks. `mpc52xx_fec_mdio_probe()` allocates the bus/private state, maps registers, sets the bus id, programs `mii_speed`, and calls `of_mdiobus_register()`. Remove unregisters the bus, unmaps registers, and frees state. `mpc52xx_fec_mdio_driver` is exported for registration by `fec_mpc52xx.c`.

### Control Flow
On probe, the driver translates the OF resource, ioremaps it, initializes `bus->read`/`write`, computes MDIO speed from `mpc5xxx_get_bus_frequency()`, registers child PHYs from OF, and stores the bus in device drvdata. Each MDIO operation writes a management frame to the FEC, then polls `FEC_IEVENT_MII` up to three sleep intervals; read operations return the low 16 data bits from `mii_data`.

### State, Persistence, And Dependencies
State is a mapped register pointer plus an allocated `mii_bus`. It depends on OF address/MDIO registration, platform devices, phylib, `asm/mpc52xx.h` bus-frequency helpers, and the MPC52xx FEC register definitions. No state is persisted beyond the registered MDIO bus and hardware registers.

### Integration Points
The MAC driver registers this platform driver before the FEC MAC driver when MDIO support is enabled, ensuring PHY devices exist before MAC open/connect paths need them. Compatible strings include `fsl,mpc5200b-mdio`, `fsl,mpc5200-mdio`, and legacy `mpc5200b-fec-phy`.

### Risks
Timeout behavior is coarse (`msleep(1)` with three tries) and depends on hardware event delivery. The driver uses the FEC register block resource directly, so resource overlap with the MAC node must match platform description. Incorrect MII speed calculation can make all PHY operations unreliable. Error unwinds must free both `priv` and `mii_bus`; current probe funnels most failures through `out_free`.

### Test Signals
Useful tests are OF MDIO node registration, Clause 22 PHY reads/writes, timeout behavior with no responding PHY, module load/unload with the MAC driver, and verifying PHY discovery before FEC open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec_mpc52xx_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec_ptp.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec_ptp.c

### Purpose
`fec_ptp.c` provides IEEE 1588/PTP hardware clock support for FEC/ENET variants with enhanced buffer descriptors and a PTP clock. It registers a PHC, manages the FEC 31-bit nanosecond counter, supports frequency/time adjustment, PPS and periodic output, hardware timestamp configuration, and save/restore around MAC resets.

### Important APIs, Types, And Functions
The exported internal functions are `fec_ptp_init()`, `fec_ptp_stop()`, `fec_ptp_start_cyclecounter()`, `fec_ptp_save_state()`, `fec_ptp_restore_state()`, `fec_ptp_set()`, and `fec_ptp_get()`. The local PTP clock callbacks are `fec_ptp_adjfine()`, `fec_ptp_adjtime()`, `fec_ptp_gettime()`, `fec_ptp_settime()`, and `fec_ptp_enable()`. PPS/perout helpers include `fec_ptp_enable_pps()`, `fec_ptp_pps_perout()`, `fec_ptp_pps_perout_handler()`, `fec_ptp_pps_disable()`, `fec_pps_interrupt()`, and the periodic `fec_time_keep()` work item.

### Control Flow
Initialization fills `ptp_clock_info`, selects `fsl,pps-channel` or channel 0, derives cycle speed and increment from `clk_ptp`, initializes the spinlock/cyclecounter/timecounter, schedules keepalive work, sets up the perout hrtimer, optionally requests a `pps` IRQ or fallback IRQ index, and registers the PHC. `fec_ptp_start_cyclecounter()` programs `FEC_ATIME_INC`, `FEC_ATIME_EVT_PERIOD`, and `FEC_ATIME_CTRL`, then initializes a 31-bit `cyclecounter` and `timecounter`.

PTP get/set/adjust operations serialize with `ptp_clk_mutex` and/or `tmreg_lock`. `fec_ptp_adjfine()` computes correction increment/period values and programs `FEC_ATIME_INC`/`FEC_ATIME_CORR`; `adjtime()` adjusts the software timecounter; `settime()` writes `FEC_ATIME` and reinitializes the counter base. PPS enable programs compare channel mode, first/next compare counters, pin period mode, and interrupt bits. Periodic output validates period/start time, rejects overlap with PPS, and uses an hrtimer if the requested start is beyond the 31-bit hardware compare range. The PPS interrupt reloads the next compare value and emits `PTP_CLOCK_PPS` events.

### State, Persistence, And Dependencies
State is held in `struct fec_enet_private`: PHC pointer/caps, cyclecounter/timecounter, `tmreg_lock`, PTP clock state mutex, timestamp enable flags, PPS/perout channel and timing fields, delayed keepalive work, perout hrtimer, and `ptp_saved_state`. State is not persisted to storage, but `fec_ptp_save_state()` records PHC/system time and correction registers before MAC reset, and `fec_ptp_restore_state()` reconstructs PHC time and PPS state afterward. Dependencies include the Linux PTP clock API, timecounter/cyclecounter helpers, hrtimer, delayed work, MMIO, OF, platform IRQs, and the FEC private header.

### Integration Points
`fec_main.c` calls PTP init during probe when enhanced descriptors are available, starts/restores the cyclecounter on MAC restart, saves state before reset/stop, exposes hwtstamp get/set via netdev ops, and uses descriptor timestamps for RX/TX SKBs. Ettool timestamp info reports the PHC index when registered.

### Risks
The hardware counter is only 31 bits, so keepalive reads every second are required to avoid timecounter ambiguity. PPS and PEROUT are mutually exclusive on the selected channel; failure to enforce this would corrupt output timing. Clock gating is guarded by `ptp_clk_mutex`, but callers must respect clock state. The code handles a capture erratum with a delay, so missing the quirk can produce stale timestamps. There is a visible duplicated assignment of `reload_period = div_u64(period_ns, 2);`, harmless but suspicious.

### Test Signals
Test with `phc2sys`/`ptp4l`, `ethtool -T`, `SIOCSHWTSTAMP` TX/RX modes, TX/RX timestamp delivery, `phc_ctl` get/set/adjfine/adjtime, PPS enable/disable, PEROUT start periods up to 4 seconds, start times beyond the 31-bit compare range, MAC reset/link restart preserving PHC time, suspend/resume, PTP clock gating failure paths, and PPS IRQ delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/Kconfig

### Purpose
`fman/Kconfig` defines build-time configuration for Freescale/NXP DPAA Frame Manager support and one DPAA FMan erratum workaround. It controls whether the FMan core, ports, and MAC support can be built.

### Important APIs, Types, And Functions
The user-visible symbol is `FSL_FMAN`, a tristate "FMan support" option depending on `FSL_SOC || ARCH_LAYERSCAPE || COMPILE_TEST`. It selects `GENERIC_ALLOCATOR`, `PHYLINK`, `PCS_LYNX`, and `CRC32`. The hidden bool `DPAA_ERRATUM_A050385` depends on `ARM64 && FSL_DPAA` and defaults to yes.

### Control Flow
There is no runtime control flow. Kconfig selection flow makes FMan objects eligible for compilation when SoC/platform or compile-test prerequisites are met, and automatically pulls required allocator, PHY link, Lynx PCS, and CRC dependencies. The erratum symbol enables software workaround code elsewhere for an FMan DMA transaction splitting issue.

### State, Persistence, And Dependencies
The file stores configuration state in the kernel `.config`. `FSL_FMAN` affects object inclusion via the sibling Makefile. `DPAA_ERRATUM_A050385` persists as a config symbol consumed by DPAA/FMan code paths.

### Integration Points
This Kconfig file integrates the `drivers/net/ethernet/freescale/fman` directory with the broader Freescale DPAA stack. `FSL_FMAN` is required by the Makefile objects `fsl_dpaa_fman.o`, `fsl_dpaa_fman_port.o`, and `fsl_dpaa_mac.o`, and by higher-level DPAA Ethernet components that depend on Frame Manager services.

### Risks
Missing selected dependencies would break link or runtime PHY integration. The erratum help text documents strict alignment constraints; disabling or misapplying the workaround under heavy traffic can stall packet processing through an internal FMan resource leak. Because `COMPILE_TEST` is allowed, code must build without real platform hardware.

### Test Signals
Configuration tests should cover `FSL_FMAN=m`, `FSL_FMAN=y`, and `COMPILE_TEST` builds. ARM64 DPAA builds should verify `DPAA_ERRATUM_A050385=y` and exercise traffic patterns with 4K-crossing DMA, unaligned DMA, and scatter-gather fragments not multiple of 16 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/Makefile

### Purpose
`fman/Makefile` defines how the Freescale/NXP DPAA Frame Manager directory is compiled. It groups source files into three logical kernel objects: FMan core, FMan port, and FMan MAC support.

### Important APIs, Types, And Functions
The Makefile adds the FMan directory to `subdir-ccflags-y` include search paths, then builds `fsl_dpaa_fman.o`, `fsl_dpaa_fman_port.o`, and `fsl_dpaa_mac.o` when `CONFIG_FSL_FMAN` is enabled. Object composition is `fman_muram.o fman.o fman_sp.o fman_keygen.o` for the core, `fman_port.o` for ports, and `mac.o fman_dtsec.o fman_memac.o fman_tgec.o` for MAC support.

### Control Flow
Build flow is controlled by Kbuild. Enabling `CONFIG_FSL_FMAN` causes all three composite objects to be compiled and linked into the kernel or module according to the tristate setting. The include flag ensures local headers such as `fman.h`, `fman_port.h`, and MAC-specific headers are found consistently.

### State, Persistence, And Dependencies
No runtime state exists. Build state is captured by Kbuild variables and `CONFIG_FSL_FMAN`. The object lists depend on the FMan source files in the same directory and on Kconfig-selected dependencies such as PHYLINK, PCS_LYNX, GENERIC_ALLOCATOR, and CRC32.

### Integration Points
This file is the build integration point between FMan source modules and the kernel networking tree. The composite objects separate reusable FMan core services, port management, and MAC implementations for dTSEC, mEMAC, and TGEC.

### Risks
Object grouping is part of symbol availability. Removing a source from the wrong composite object could produce unresolved symbols or feature loss in DPAA Ethernet drivers. The broad local include path can hide missing explicit include relationships, so header refactors should be build-tested carefully.

### Test Signals
Run build tests with `CONFIG_FSL_FMAN=y` and `m`, plus `COMPILE_TEST`. Confirm the three composite objects are produced, module dependencies resolve, and DPAA Ethernet users link against the expected FMan symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/Makefile -->
