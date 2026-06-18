# subset-b-004671 Research

Grouped research for `subset-b-004671`. Each section preserves the source path in its title and is intended to be split into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/xilinx_axienet_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/xilinx_axienet_main.c

Purpose: Implements the Xilinx AXI Ethernet platform netdev driver for AXI Ethernet MAC cores. It owns platform probe/remove/shutdown/PM, MAC register programming, phylink/PCS integration, multicast and MAC address programming, checksum feature exposure, ethtool operations, NAPI, interrupt handling, AXI DMA descriptor rings, optional dmaengine-backed TX/RX, hardware statistics, interrupt coalescing, and DMA error recovery.

Important APIs/types/functions: The driver centers on `struct axienet_local` from `xilinx_axienet.h`, with state for MAC registers, DMA registers/channels, descriptor rings, SKB rings, phylink, MDIO, PCS PHY, stats, DIM, locks, IRQs, and feature bits. Major lifecycle functions are `axienet_probe()`, `axienet_open()`, `axienet_stop()`, `axienet_remove()`, `axienet_shutdown()`, `axienet_suspend()`, and `axienet_resume()`. Legacy DMA data path functions include `axienet_dma_bd_init()`, `axienet_dma_start()`, `axienet_dma_stop()`, `axienet_start_xmit()`, `axienet_tx_poll()`, `axienet_rx_poll()`, `axienet_tx_irq()`, and `axienet_rx_irq()`. Dmaengine mode uses `axienet_init_dmaengine()`, `axienet_rx_submit_desc()`, `axienet_start_xmit_dmaengine()`, `axienet_dma_tx_cb()`, and `axienet_dma_rx_cb()`. MAC control helpers include `axienet_setoptions()`, `axienet_set_mac_address()`, `axienet_set_multicast_list()`, `axienet_device_reset()`, and `axienet_dma_err_handler()`. Ettool and phylink integration is through `axienet_ethtool_ops`, `axienet_netdev_ops`, `axienet_netdev_dmaengine_ops`, `axienet_phylink_ops`, and `axienet_pcs_ops`.

Control flow: Probe allocates the netdev, enables clocks, maps MAC registers, reads DT synthesis properties (`xlnx,txcsum`, `xlnx,rxcsum`, `xlnx,rxmem`, `xlnx,phy-type` or `phy-mode`, `xlnx,switch-x-sgmii`), selects legacy DMA or dmaengine mode based on the `dmas` property, maps DMA registers and IRQs or resets the dmaengine channel, detects 64-bit DMA descriptor support, initializes NAPI and coalescing defaults, registers MDIO, resolves PCS devices for SGMII/1000BaseX, creates phylink, and registers the netdev. Open locks MDIO around a reset because the DMA reset also resets the MAC/MDIO block, connects and starts phylink, starts periodic statistics refresh, and then initializes either dmaengine rings/channels or legacy DMA IRQs/NAPI. In legacy transmit, `ndo_start_xmit` maps the head and fragments into AXI DMA BDs, writes the tail descriptor pointer, and queue-stops when descriptor space is low; TX NAPI unmaps completed BDs and wakes the queue. Legacy RX NAPI consumes completed BDs, unmaps buffers, applies checksum status from app words, hands packets to GRO, refills buffers, and advances the DMA tail pointer. IRQ handlers clear DMA status, disable completion interrupts while NAPI owns the queue, and schedule reset work on DMA errors. Stop reverses the flow: disable work and NAPI, stop phylink, disable MAC TX/RX, stop or terminate DMA, free IRQs/channels/rings, reset queue accounting, and disable MAC interrupts.

State and persistence behavior: Runtime state persists for the platform device lifetime in `axienet_local`. Legacy DMA descriptors are coherent rings with producer/consumer indexes (`tx_bd_ci`, `tx_bd_tail`, `rx_bd_ci`) and per-BD SKB pointers; dmaengine mode keeps separate circular SKB descriptor arrays and head/tail counters. Hardware state includes MAC option registers, unicast/multicast filters, frame-size settings, flow-control registers, DMA control/status/tail registers, MDIO registers, PCS mode, and hardware counters. Statistics are accumulated across 32-bit hardware counter wraps and resets using `hw_stat_base`, `hw_last_counter`, `stats_work`, a mutex, and a seqcount; reset marks counters temporarily unreliable with `reset_in_progress`. Coalescing state is shadowed in `rx_dma_cr`/`tx_dma_cr` under spinlocks and applied immediately only when the DMA channel is running. No disk persistence is involved.

Dependencies and integration points: Depends on Linux platform device, OF bindings, clocks, phylink/phylib, optional OF MDIO, DMA mapping, AXI DMA MMIO, dmaengine and Xilinx VDMA reset APIs, NAPI/GRO, ethtool, u64 stats, net DIM, and optional netpoll. It is selected by Xilinx Ethernet Kconfig outside this subset and shares MDIO helper declarations with `xilinx_axienet_mdio.c`. Device-tree bindings referenced by earlier research include `xlnx,axi-ethernet-*`, `axistream-connected`, optional `dmas`, `pcs-handle`, `phy-handle`, and MAC/PHY properties.

Risks and test signals: Probe and open unwind paths span clocks, phylink, MDIO, PCS references, DMA channels, NAPI, IRQs, and coherent rings, so failure-injection coverage matters. Legacy DMA error reset is asynchronous work that must not race stop/remove; tests should exercise DMA error IRQs, reset during traffic, and close while reset work is pending. Descriptor wrap and queue-stop/wake barriers are critical for fragmented SKBs and high TX load. RX refill failure leaves a completed slot without an SKB until a later refill, so memory pressure tests should verify no packet replay or tail advancement bug. Dmaengine mode uses fixed ring constants and callbacks rather than NAPI; test channel request failure, metadata absence, terminate/unmap behavior, and TX queue wake accounting. Other useful signals are SGMII/1000BaseX PCS switching, phylink attach failures, MDIO reset locking, 32-bit versus detected 64-bit DMA, checksum offload modes, jumbo MTU bounds against `xlnx,rxmem`, ethtool ring/coalesce validation, hardware stats with resets/wraps, suspend/resume, missing optional Ethernet core IRQ, and `CONFIG_NET_POLL_CONTROLLER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/xilinx_axienet_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/xilinx_axienet_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/xilinx_axienet_mdio.c

Purpose: Provides the MDIO bus implementation embedded in the Xilinx AXI Ethernet MAC. It calculates the MDC divisor, enables/disables the MDIO clock around transactions, implements C22 read/write operations, registers the OF MDIO bus, and tears it down for the main AXI Ethernet driver.

Important APIs/types/functions: Public entry points are `axienet_mdio_setup(struct axienet_local *lp)` and `axienet_mdio_teardown(struct axienet_local *lp)`. Internal helpers are `axienet_mdio_wait_until_ready()`, `axienet_mdio_mdc_enable()`, `axienet_mdio_mdc_disable()`, `axienet_mdio_read()`, `axienet_mdio_write()`, and `axienet_mdio_enable()`. It uses `struct mii_bus`, the AXI Ethernet register helpers and MDIO bit definitions from `xilinx_axienet.h`, and `lp->axi_clk`, `lp->mii_clk_div`, `lp->mii_bus`, `lp->regs_start`, `lp->regs`, and `lp->dev`.

Control flow: Setup allocates an `mii_bus`, assigns the driver callbacks, derives a stable bus id from the MAC resource start address, locates an optional `mdio` child node, enables the MDIO block, registers children with `of_mdiobus_register()`, disables MDC after successful registration, and stores the bus in `lp->mii_bus`. Read and write operations enable MDC, wait for the controller ready bit, program PHY address/register/opcode fields into `XAE_MDIO_MCR_OFFSET`, poll for completion, read or write the data register, and then disable MDC. `axienet_mdio_enable()` obtains the AXI host clock from the enabled AXI clock when available or legacy CPU `clock-frequency` fallback, reads an optional MDIO `clock-frequency`, calculates a divider that does not exceed the requested MDIO rate, rejects values outside the hardware divisor field, enables MDIO, and waits for readiness. Teardown unregisters and frees the bus.

State and persistence behavior: The only persistent runtime state is the allocated `mii_bus` pointer and the calculated `mii_clk_div` in `axienet_local`. Hardware state is transient: the MDIO enable bit is asserted during setup and transactions, then disabled to leave MDC idle. Registered PHY child devices persist until teardown via the MDIO core. There is no durable persistence.

Dependencies and integration points: Integrates with the main AXI Ethernet driver, OF MDIO registration, Linux phylib, clock framework, jiffies/poll helpers, and the MAC's MMIO register accessors. It must coordinate with `xilinx_axienet_main.c` resets; the main driver locks the MII bus around MAC/DMA resets because reset also resets this MDIO block.

Risks and test signals: Divider calculation can underflow or divide by zero if a malformed `clock-frequency` is supplied; validation should include missing, default, low, high, and overflow MDIO rates. Read/write paths must always disable MDC on timeout; timeout injection should verify no stuck enable bit. Setup failure after `lp->mii_bus` assignment should leave no stale pointer. Teardown assumes `lp->mii_bus` is valid, so remove paths should only call after successful setup or guard accordingly. Test signals include PHY discovery from an `mdio` child, no-child direct registration, phylink attach through this bus, reset while PHY traffic is active, and `of_mdiobus_register()` failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/xilinx_axienet_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/xilinx_emaclite.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/xilinx_emaclite.c

Purpose: Implements the Xilinx Ethernet MAC Lite platform netdev driver. This is a small PIO-based Ethernet driver with optional ping-pong TX/RX buffers, optional in-core MDIO registration, phylib link reporting, basic ethtool hooks, interrupt-driven RX/TX, deferred single-SKB transmit when the hardware buffer is busy, and OF platform probe/remove.

Important APIs/types/functions: Driver state is `struct net_local`, storing netdev, base MMIO, ping-pong flags, next TX/RX buffer offsets, reset lock, deferred SKB, PHY node/device, MII bus, and last link state. Register access uses endian-dependent `xemaclite_readl`/`xemaclite_writel`. Core helpers include `xemaclite_enable_interrupts()`, `xemaclite_disable_interrupts()`, `xemaclite_aligned_write()`, `xemaclite_aligned_read()`, `xemaclite_send_data()`, `xemaclite_recv_data()`, `xemaclite_update_address()`, and `xemaclite_tx_timeout()`. Data path and lifecycle functions are `xemaclite_send()`, `xemaclite_interrupt()`, `xemaclite_tx_handler()`, `xemaclite_rx_handler()`, `xemaclite_open()`, `xemaclite_close()`, `xemaclite_of_probe()`, and `xemaclite_of_remove()`. MDIO support is implemented by `xemaclite_mdio_wait()`, `xemaclite_mdio_read()`, `xemaclite_mdio_write()`, and `xemaclite_mdio_setup()`.

Control flow: Probe allocates an etherdev, maps registers, gets the IRQ and optional clock, reads/generates the MAC address, clears TX status registers, programs the MAC address using a transmit buffer, records ping-pong buffer properties from DT, finds an optional `phy-handle`, optionally registers an MDIO bus if this device owns the PHY's parent MDIO resource, installs netdev/ethtool ops, disables multicast support in netdev flags, and registers the netdev. Open disables interrupts, connects the PHY if present, limits PHY speed to 100 Mbps, starts PHY state, reprograms the MAC address, requests the IRQ, enables interrupts, and starts the queue. Transmit tries to copy the SKB payload into the current TX buffer and start hardware; if both ping-pong buffers are busy it stops the queue and stores one deferred SKB for the TX interrupt handler. The interrupt handler checks RX done bits on both buffers, receives one frame at a time into a new SKB, checks TX completion active markers on both buffers, and tries to flush any deferred TX SKB. Close stops the queue, disables interrupts, frees IRQ, and disconnects PHY. Remove unregisters the optional MDIO bus, unregisters netdev, and drops the PHY node reference.

State and persistence behavior: Persistent runtime state is in `net_local`: current ping-pong offsets, deferred SKB ownership, PHY attachment, and MDIO bus lifetime. Packet data is copied directly to/from device buffer memory; no DMA rings exist. Hardware state includes TX/RX buffer status bits, global interrupt enable, MDIO control/address/data registers, MAC address programming through a TX buffer, and ping-pong buffer selection. The driver keeps netdev software statistics in `dev->stats`; no hardware statistics are accumulated. There is no disk persistence.

Dependencies and integration points: Integrates with OF platform matching for `xlnx,*ethernetlite*` compatibles, the clock framework, phylib, OF MDIO/PHY helpers, netdev core, ethtool link settings delegated to phylib, optional netpoll, and the device-tree binding `xlnx,emaclite`. It uses PIO rather than DMA, so CPU endian and alignment behavior are explicit in the aligned read/write helpers.

Risks and test signals: The driver only stores one deferred SKB, so TX queue stop/wake behavior must prevent overwriting it under stress. `xemaclite_disable_interrupts()` writes the global interrupt mask value rather than clearing it before clearing per-buffer bits, so hardware semantics should be verified on real cores. RX length is inferred from Ethernet/IP/ARP headers and may use max frame length for unknown types; tests should include non-IP/ARP frames, short/truncated frames, VLAN-like types, and FCS handling. MDIO setup deliberately avoids duplicate bus registration when the PHY's MDIO parent belongs to another EmacLite instance; test multi-instance DT topologies and probe ordering. Other signals include ping-pong enabled/disabled TX/RX, PHY absent operation, IRQ allocation failure, open/close cycles with deferred SKB, TX timeout reset path, big-endian build/runtime behavior, `phy-handle` reference cleanup, and netpoll.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/xilinx_emaclite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xircom/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xircom/Kconfig

Purpose: Defines the Xircom Ethernet vendor configuration menu and the build option for the 16-bit PCMCIA Xircom Ethernet driver.

Important APIs/types/functions: `NET_VENDOR_XIRCOM` is a bool vendor gate that defaults to yes but depends on `PCMCIA`. `PCMCIA_XIRC2PS` is the tristate option for Xircom 16-bit PCMCIA Ethernet/Fast Ethernet cards and depends on `PCMCIA && HAS_IOPORT`. Its module name is documented as `xirc2ps_cs`.

Control flow: Kconfig first exposes the vendor bucket only when PCMCIA is available. If enabled, it exposes the concrete driver option. Selecting `PCMCIA_XIRC2PS=y` builds the driver in, `m` builds a module, and `n` omits it.

State and persistence behavior: No runtime state. The file persists build-time policy only: whether the PCMCIA Xircom source is compiled and whether I/O port APIs are allowed.

Dependencies and integration points: Integrates with the parent Ethernet Kconfig tree, the PCMCIA subsystem, architecture `HAS_IOPORT`, and the sibling Makefile entry that maps `CONFIG_PCMCIA_XIRC2PS` to `xirc2ps_cs.o`.

Risks and test signals: Build coverage should verify all three tristate values, especially architectures without `HAS_IOPORT` where the option must be hidden. Menu visibility should be tested with `PCMCIA=n` and `PCMCIA=y`. Runtime testing belongs to `xirc2ps_cs.c`, but Kconfig tests should confirm module naming and dependency pruning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xircom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xircom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xircom/Makefile

Purpose: Connects the Xircom vendor directory to the 16-bit PCMCIA Xircom Ethernet driver object.

Important APIs/types/functions: `obj-$(CONFIG_PCMCIA_XIRC2PS) += xirc2ps_cs.o` is the only build rule.

Control flow: Kbuild includes `xirc2ps_cs.o` as built-in or module according to the value of `CONFIG_PCMCIA_XIRC2PS`; if the symbol is disabled, the directory contributes no object.

State and persistence behavior: No runtime state. The file is a build-routing artifact.

Dependencies and integration points: Depends on `PCMCIA_XIRC2PS` from the sibling Kconfig and on `xirc2ps_cs.c` exporting the PCMCIA driver module.

Risks and test signals: Build tests should verify `CONFIG_PCMCIA_XIRC2PS=m` produces `xirc2ps_cs.ko`, built-in links cleanly, and disabled config does not compile the legacy I/O-port driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xircom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xircom/xirc2ps_cs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xircom/xirc2ps_cs.c

Purpose: Implements the legacy Xircom CreditCard/RealPort 16-bit PCMCIA Ethernet driver. It handles PCMCIA card identification and I/O-window configuration, netdev registration, programmed-I/O transmit/receive, interrupt service, media selection, multicast filter programming, bit-banged MII for Mohawk/newer variants, timeout reset work, suspend/resume, and module/boot parameters.

Important APIs/types/functions: The key private type is `struct local_info`, which stores the netdev and PCMCIA device, card type flags (`mohawk`, `dingo`, `modem`, `new_mii`), mapped Dingo CCR memory, media probe state, silicon revision, last TX pointer, manufacturer string, and timeout work. PCMCIA entry points are `xirc2ps_probe()`, `xirc2ps_config()`, `xirc2ps_release()`, `xirc2ps_detach()`, `xirc2ps_suspend()`, and `xirc2ps_resume()`, registered through `xirc2ps_cs_driver` and `xirc2ps_ids`. Netdev operations include `do_open()`, `do_stop()`, `do_start_xmit()`, `xirc_tx_timeout()`, `do_config()`, `do_ioctl()`, `set_multicast_list()`, and address validation/set helpers. Hardware setup and media helpers include `set_card_type()`, `has_ce2_string()`, `hardreset()`, `do_reset()`, `init_mii()`, `do_powerdown()`, `set_addresses()`, and the `mii_*` bit-banging routines.

Control flow: Probe allocates an etherdev, initializes netdev ops, timeout work, and then calls configuration. Configuration validates the manufacturer, determines the card subtype from CIS tuples, obtains the MAC address from standard CIS data or fallback tuples, requests suitable I/O windows differently for Ethernet-only, modem-combo, and Dingo cards, requests an IRQ, enables the PCMCIA function, optionally maps Dingo attribute memory and writes Ethernet CCRs manually, applies `if_port` selection policy, optionally performs an early reset for Dingo, and registers the netdev. Open checks card presence, increments the PCMCIA open count, starts the netdev queue, and performs a full reset. Reset powers the card down/up, toggles soft reset, waits for hardware power-up, detects silicon revision, configures media/MII, interrupt masks, receive memory split, MAC address table, multicast state, LEDs, receiver online state, and interrupt enable. TX reserves on-card space, writes length and payload through I/O ports, triggers transmit for Mohawk variants, updates bytes, and restarts the queue. The ISR disables Mohawk interrupts, saves the page register, reads/clears interrupt and MAC status, drains full RX packets up to an adaptive byte budget, updates RX/TX stats and error counters, restarts TX after excessive collisions, optionally loops for `lockup_hack`, restores the page, and reenables interrupts. Stop disables interrupts, masks MAC interrupts, powers down, and decrements the PCMCIA open count. Suspend powers down if open; resume resets and reattaches if open.

State and persistence behavior: Runtime state is split across `local_info`, netdev fields (`base_addr`, `irq`, `if_port`, stats), PCMCIA resources/config flags, and hardware page registers. Module parameters (`if_port`, `full_duplex`, `do_sound`, `lockup_hack`) persist for the module lifetime and influence reset/configuration. `maxrx_bytes` is a global adaptive ISR budget that changes according to observed interrupt duration. Dingo cards keep a remapped CCR pointer until release. Hardware state includes page-selected MAC registers, local memory split, multicast address slots, MII PHY registers, media/LED control, and PCMCIA configuration registers. There is no disk persistence.

Dependencies and integration points: Depends on the PCMCIA core and CIS tuple helpers, legacy I/O port access, netdev core, ethtool driver info, MII ioctl ABI for Mohawk cards, module parameters and boot-time `__setup`, and manufacturer/product IDs for Xircom, Accton, Compaq, Intel, and Toshiba branded cards. The Kconfig dependency on `HAS_IOPORT` is essential because the data path is `inb/outb/insw/outsw`.

Risks and test signals: This driver has many hardware-specific timing sleeps and page-register side effects; regression testing needs real PCMCIA hardware or detailed emulation. The TX path stops the queue before checking available space and returns `NETDEV_TX_BUSY` with the SKB still owned by the stack; queue restart depends on later TX interrupts and can hang if interrupts are lost. The ISR is long and adaptive but still processes PIO RX in hard IRQ context; stress tests should monitor latency and `maxrx_bytes` adjustment. Card detection and MAC extraction have several CIS fallbacks that can fail differently across rebranded cards. Dingo CCR mapping uses an offset pointer and manual PCMCIA register writes, so error unwinds and release mapping should be validated. Other signals include hot unplug during interrupt/open, suspend/resume while open, modem-combo resource assignment, forced media (`if_port=1/2/4`), MII ioctl reads/writes, full-duplex parameter, multicast filter sizes over/under 9 addresses, TX timeout work cancellation during detach, and old CE unsupported-card rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xircom/xirc2ps_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/Kconfig

Purpose: Defines the Intel XScale IXP Ethernet vendor menu, the IXP4xx Ethernet MAC driver option, and the optional IXP46x PTP clock support used for hardware timestamping.

Important APIs/types/functions: `NET_VENDOR_XSCALE` is a bool vendor gate depending on `NET_VENDOR_INTEL` and the ARM IXP4xx NPE/QMGR platform pieces. `IXP4XX_ETH` is the tristate Ethernet driver option; it depends on ARM IXP4xx, NPE, QMGR, and OF, and selects `PHYLIB`, `OF_MDIO`, and `NET_PTP_CLASSIFY`. `PTP_1588_CLOCK_IXP46X` is a bool depending on `IXP4XX_ETH` and compatible `PTP_1588_CLOCK` configuration, defaulting to yes.

Control flow: Kconfig exposes XScale IXP drivers only on the correct ARM/IXP4xx platform. Enabling `IXP4XX_ETH` compiles the Ethernet driver and its selected PHY/MDIO/PTP-classify dependencies. Enabling the PTP bool adds the IXP46x PTP clock object through the Makefile.

State and persistence behavior: No runtime state. It encodes build-time availability and ensures timestamp classification support is present for `ixp4xx_eth.c`.

Dependencies and integration points: Integrates the XScale Ethernet directory with the Intel vendor menu, IXP4xx platform NPE and queue manager subsystems, OF platform descriptions, phylib/OF MDIO, and the PTP core.

Risks and test signals: Build matrix should cover `IXP4XX_ETH=y/m/n`, `PTP_1588_CLOCK_IXP46X=y/n`, and PTP core combinations including `PTP_1588_CLOCK=y` or matching module linkage. The PTP option is bool despite help text mentioning a module, so build output should be checked against Makefile behavior. Dependency tests should verify the driver is hidden when NPE/QMGR/OF or `NET_VENDOR_INTEL` is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/Makefile

Purpose: Defines build order for the Intel XScale IXP Ethernet driver objects.

Important APIs/types/functions: If `CONFIG_PTP_1588_CLOCK_IXP46X` is set, `ptp_ixp46x.o` is added before `ixp4xx_eth.o`; `ixp4xx_eth.o` is built according to `CONFIG_IXP4XX_ETH`.

Control flow: Kbuild conditionally links the PTP clock object first to avoid deferred probing, then links the Ethernet driver. When `IXP4XX_ETH=m`, these objects participate in module build according to Kconfig linkage.

State and persistence behavior: No runtime state. The main persistence is build ordering, which affects whether the Ethernet probe can find the PTP clock provider without deferral.

Dependencies and integration points: Consumes symbols from the sibling Kconfig and coordinates the exported `ixp46x_ptp_find()` provider with the Ethernet consumer in `ixp4xx_eth.c`.

Risks and test signals: Build and boot tests should verify the stated link order prevents avoidable probe deferral when PTP is enabled. Also verify PTP-disabled builds compile `ixp4xx_eth.c` against the inline `ixp46x_ptp_find()` stub in `ixp46x_ts.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/ixp46x_ts.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/ixp46x_ts.h

Purpose: Defines the IXP46x time-sync register layout, bit masks, timestamp scaling constants, and the conditional API used by the Ethernet driver to discover the PTP hardware clock.

Important APIs/types/functions: `struct ixp46x_channel_ctl` maps per-channel timestamp control/event and TX/RX snapshot/source UUID registers. `struct ixp46x_ts_regs` maps global time-sync control, event, addend, accumulator, raw/system time, target time, auxiliary snapshots, and three timestamp channels. Constants include `DEFAULT_ADDEND`, `TICKS_NS_SHIFT`, global control/event masks (`TSCR_*`, `TSER_*`, `TTIPEND`), channel control masks (`MASTER_MODE`, `TIMESTAMP_ALL`), and snapshot event masks (`TX_SNAPSHOT_LOCKED`, `RX_SNAPSHOT_LOCKED`). `ixp46x_ptp_find()` is declared when `CONFIG_PTP_1588_CLOCK_IXP46X` is enabled and otherwise provided as an inline `-ENODEV` stub that clears the output registers/index.

Control flow: Consumers include this header and call `ixp46x_ptp_find()` to obtain the memory-mapped timestamp registers and PHC index. If PTP support is disabled, the stub makes timestamp support cleanly unavailable while keeping Ethernet builds working.

State and persistence behavior: No state is allocated by the header. It defines the ABI for persistent hardware register state used by `ptp_ixp46x.c` and `ixp4xx_eth.c`.

Dependencies and integration points: Integrates the IXP46x PTP clock provider with the IXP4xx Ethernet driver. It relies on Linux fixed-width integer types and error codes supplied by including C files and on Kconfig selecting or omitting `CONFIG_PTP_1588_CLOCK_IXP46X`.

Risks and test signals: Register layout changes are hardware ABI changes and would break both PHC operations and packet timestamping. `TICKS_NS_SHIFT` defines conversion between hardware ticks and nanoseconds; timestamp tests should verify read/write/adjust behavior against wall-clock expectations. PTP-disabled builds should confirm the stub returns `-ENODEV`, `regs=NULL`, and `phc_index=-1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/ixp46x_ts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/ixp4xx_eth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/ixp4xx_eth.c

Purpose: Implements the Intel IXP4xx built-in Ethernet platform driver using IXP NPE firmware and the queue manager. It owns OF platform parsing, shared MDIO bus registration, NPE firmware setup, queue allocation, DMA descriptor/buffer pools, NAPI RX, TX done handling, phylib, multicast filtering, MTU programming through NPE messages, ethtool info, and optional IXP46x PTP packet timestamping.

Important APIs/types/functions: Core types are `struct eth_plat_info` for DT-derived queue/NPE/MAC/MDIO data, `struct eth_regs` for MAC MMIO registers, `struct port` for per-netdev state, `struct msg` for NPE firmware commands, and `struct desc` for NPE packet descriptors. Important globals are `mdio_lock`, `mdio_regs`, `mdio_bus`, `mdio_bus_np`, `ports_open`, `npe_port_tab[]`, and shared `dma_pool`. Key functions include `ixp4xx_eth_probe()`, `ixp4xx_eth_remove()`, `ixp4xx_of_get_platdata()`, `eth_open()`, `eth_close()`, `eth_xmit()`, `eth_poll()`, `eth_rx_irq()`, `eth_txdone_irq()`, `request_queues()`, `release_queues()`, `init_queues()`, `destroy_queues()`, `ixp4xx_mdio_register()`, `ixp4xx_mdio_read/write()`, `ixp4xx_adjust_link()`, `eth_set_mcast_list()`, `ixp4xx_eth_change_mtu()`, `ixp4xx_hwtstamp_get/set()`, `ixp_rx_timestamp()`, and `ixp_tx_timestamp()`.

Control flow: Probe parses the NPE phandle, RX and TX-ready queue phandles, optional child MDIO node, and MAC address; allocates an etherdev; maps MAC registers; registers the shared MDIO bus from the port that owns it or defers until one exists; sets netdev ops, DMA masks, MTU bounds, NAPI, and ethtool ops; requests the NPE instance; resets the MAC core; connects the PHY; and registers the netdev. Open loads NPE firmware if needed, reads firmware version, sends NPE messages to route RX queues and set MAC/firewall/MTU, requests queue-manager queues, allocates coherent descriptor memory and RX buffers, starts PHY, programs MAC registers, populates TX-ready and RX-free queues, enables MAC RX/TX, enables NAPI and queue interrupts, starts the netdev queue, sets global TX-done IRQ on the first open port, increments `ports_open`, and schedules NAPI. RX IRQ disables the RX queue interrupt and schedules NAPI; NAPI drains RX descriptors from the queue manager, allocates/replaces buffers, performs endian copy/sync as needed, applies optional RX PTP timestamp, submits SKBs, and returns descriptors to RX-free queue. TX maps/copies the outgoing frame, obtains a TX-ready descriptor, submits it to the NPE TX queue, queue-stops if no TX-ready descriptors remain, and optionally polls the PTP TX snapshot. A global TX-done IRQ drains completions for all ports, unmaps/frees buffers, returns descriptors to per-port TX-ready queues, and wakes queues. Close disables RX IRQ/NAPI and TX queue, drains RX/TX hardware queues using loopback packet injection if needed, stops PHY, disables shared TX-done IRQ on last port, destroys DMA/buffer pools, and releases queues.

State and persistence behavior: Per-port state persists in `struct port`: registers, NPE handle, NAPI, descriptor table, DMA address, RX/TX buffer arrays, firmware version, link speed/duplex, timestamp enable flags, PTP register pointer, and PHC index. Shared state persists in globals for the single MDIO bus, port table, open-port count, TX-done queue, and DMA pool. Hardware state includes MAC registers, NPE firmware routing/configuration, queue manager entries, descriptor memory owned by NPE, MDIO command/status registers, and IXP46x timestamp registers. Netdev stats are accumulated in `dev->stats`. No disk persistence exists.

Dependencies and integration points: Depends on ARM IXP4xx NPE and QMGR platform APIs, OF platform and phandle parsing, OF MDIO/phylib, DMA mapping and DMA pools, NAPI, PTP classification and timestamping APIs, IXP46x PTP provider from `ptp_ixp46x.c`, and the device-tree binding `intel,ixp4xx-ethernet`. Endianness is significant: big-endian builds use SKBs directly while little-endian paths copy/swap packet data into CPU buffers.

Risks and test signals: Shared globals make multi-port ordering delicate: the MDIO bus is removed unconditionally in remove, the TX-done queue and DMA pool depend on `ports_open`, and `npe_port_tab` is used in IRQ context. Tests should cover multiple ports opening/closing/removing in different orders. Queue draining on close relies on loopback and bounded polling; test under RX/TX load and NPE stalls. DMA descriptor ownership and endian-specific copy paths are high-risk and need RX/TX traffic tests on supported endianness. TX timestamping busy-polls up to 100 microseconds and only supports PTP v1 IPv4 matching; test enabled/disabled PHC, unsupported filters, TX snapshot timeout, RX snapshot mismatch, and PTP provider probe deferral. Other signals include missing MDIO-owning port causing `-EPROBE_DEFER`, NPE firmware load failure, queue-manager allocation failure, MTU changes while up/down, multicast/promiscuous modes, PHY polling, hot remove after open, and DMA mapping failures during queue init/TX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/ixp4xx_eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/ptp_ixp46x.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/ptp_ixp46x.c

Purpose: Implements the IXP46x PTP hardware clock provider backed by the on-chip time-sync timer. It registers a PHC, supports time read/write/adjust operations, handles auxiliary external timestamp IRQs, initializes addend/target/event registers, and exports `ixp46x_ptp_find()` for the Ethernet driver to obtain timestamp registers and PHC index.

Important APIs/types/functions: `struct ixp_clock` stores the mapped `ixp46x_ts_regs`, `ptp_clock`, `ptp_clock_info`, external timestamp enable flags, and master/slave IRQs. Hardware helpers are `ixp_systime_read()` and `ixp_systime_write()`. PTP callbacks are `ptp_ixp_adjfine()`, `ptp_ixp_adjtime()`, `ptp_ixp_gettime()`, `ptp_ixp_settime()`, and `ptp_ixp_enable()`, collected in `ptp_ixp_caps`. Platform lifecycle is `ptp_ixp_probe()` plus devm cleanup through `ptp_ixp_unregister_action()`. `isr()` handles external timestamp and target-time events. `ixp46x_ptp_find()` is exported GPL for `ixp4xx_eth.c`.

Control flow: Probe maps the timer registers, obtains master and slave IRQs, copies static clock capabilities into the global clock instance, registers the PHC, installs a devm action to unregister it, initializes the addend and target/event registers, and requests both IRQs. Time operations take the global register spinlock for read/modify/write of the split 64-bit system-time registers. Frequency adjustment writes a scaled addend. External timestamp enable toggles per-index flags only; the ISR reads the global event register, acknowledges slave/master snapshot bits and the always-set target bit, reads auxiliary snapshot registers when enabled, converts hardware ticks to nanoseconds by shifting with `TICKS_NS_SHIFT`, and emits `PTP_CLOCK_EXTTS` events. `ixp46x_ptp_find()` rejects non-IXP46x CPUs, returns the global register pointer and PHC index, and returns `-EPROBE_DEFER` if called before PHC registration is complete.

State and persistence behavior: A single global `ixp_clock` instance persists for the platform driver lifetime. Hardware time, addend, target, and event bits persist in the mapped timer block. External timestamp enable flags persist in memory but are not separately programmed into mask registers. Cleanup unregisters the PHC and clears the global `ptp_clock` pointer; devm handles IRQ and mapping lifetime. There is no disk persistence.

Dependencies and integration points: Depends on the Linux PTP clock core, platform devices, IRQ APIs, raw MMIO access, IXP4xx CPU detection, and register definitions from `ixp46x_ts.h`. It is intentionally linked before `ixp4xx_eth.o` so Ethernet timestamp configuration can call `ixp46x_ptp_find()` without unnecessary deferral.

Risks and test signals: `ixp46x_ptp_find()` computes `ptp_clock_index(ixp_clock.ptp_clock)` before checking for a NULL clock pointer, so callers racing early provider initialization deserve scrutiny. The global singleton prevents multiple timer instances. Split 64-bit time reads/writes rely on locking but no hardware latch, so monotonicity should be tested around low-word rollover. External timestamp flags are not protected by the same spinlock as the ISR. Test PHC registration failure, IRQ request failure, get/set/adjfine/adjtime, external timestamp enable for both indexes, interrupt ack behavior for always-set `TTIPEND`, non-IXP46x behavior, and Ethernet driver probe ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/ptp_ixp46x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/Kconfig

Purpose: Defines the top-level FDDI network driver menu and the individual DEC and SysKonnect FDDI adapter build options.

Important APIs/types/functions: `FDDI` is a tristate umbrella depending on `PCI || EISA || TC`. Under it, `DEFZA` supports DEC FDDIcontroller 700/700-C TURBOchannel cards and depends on `FDDI && TC`; `DEFXX` supports Digital DEFTA/DEFEA/DEFPA adapters and depends on `FDDI && (PCI || EISA || TC)`; `SKFP` supports SysKonnect FDDI PCI adapters, depends on `FDDI && PCI`, and selects `BITREVERSE`.

Control flow: Enabling `FDDI` exposes the concrete adapter choices. Each child tristate controls whether its driver is built-in, built as a module, or omitted. `SKFP` also forces bit-reversal helpers through Kconfig selection.

State and persistence behavior: No runtime state. The file only encodes build-time availability for legacy FDDI drivers.

Dependencies and integration points: Integrates with PCI, EISA, and TURBOchannel bus support and the sibling Makefile mapping to `defxx.o`, `defza.o`, and `skfp/`. Documentation points users to the SysKonnect FDDI driver guide.

Risks and test signals: Build matrix should cover bus-specific visibility: no FDDI menu without PCI/EISA/TC, `DEFZA` only with TC, `DEFXX` with any supported bus, and `SKFP` only with PCI plus `BITREVERSE` selected. Module names should match help text (`defza`, `defxx`, `skfp`).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/Makefile

Purpose: Routes enabled FDDI driver Kconfig symbols to their Kbuild objects/subdirectories.

Important APIs/types/functions: `obj-$(CONFIG_DEFXX) += defxx.o`, `obj-$(CONFIG_DEFZA) += defza.o`, and `obj-$(CONFIG_SKFP) += skfp/` are the build rules.

Control flow: Kbuild compiles the Digital DEFXX object, DEC DEFZA object, and/or descends into the SysKonnect `skfp` directory according to the selected child Kconfig symbols.

State and persistence behavior: No runtime state. It is a build-routing file.

Dependencies and integration points: Depends on symbols from `drivers/net/fddi/Kconfig` and on the corresponding source files/subdirectory existing elsewhere in the tree.

Risks and test signals: Build tests should cover each driver as built-in and module where supported, plus all disabled. `CONFIG_SKFP=m` should descend into `skfp/` and produce the expected module rather than a flat object in this directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/Makefile -->
