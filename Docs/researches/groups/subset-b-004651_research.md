# Research: subset-b-004651

Work item `subset-b-004651` covers the STMMAC Ethernet driver main datapath/lifecycle file and its MDIO bus implementation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_main.c

## Purpose

`stmmac_main.c` is the core Linux network driver implementation for Synopsys/STMMAC Ethernet MACs used by the Ceph client source snapshot. It owns the `net_device` lifecycle, DMA descriptor rings, TX/RX datapaths, NAPI scheduling, IRQ dispatch, PTP hardware timestamping, phylink integration, VLAN filtering/offload, XDP/AF_XDP support, traffic-control offloads, suspend/resume, debugfs surfaces, and driver probe/remove entry points that platform glue calls through exported helpers.

The file is the integration center for the STMMAC driver family. Hardware-specific register operations are largely delegated through `hwif.h` callbacks and helpers in sibling files, while this file sequences those operations with Linux networking, runtime PM, phylink, page_pool, DMA mapping, devlink, debugfs, and XDP APIs.

## Important APIs, Types, and Entry Points

- Exported platform/helper APIs:
  - `stmmac_set_clk_tx_rate()` sets a MAC TX clock rate for 10/100/1000 Mbps interfaces and is exported for platform glue.
  - `stmmac_axi_blen_to_mask()` converts AXI burst-length arrays into `DMA_AXI_BLEN_MASK` register fields and validates power-of-two ranges.
  - `stmmac_get_phy_intf_sel()` maps selected `phy_interface_t` modes to STMMAC PHY interface selector constants.
  - `stmmac_plat_dat_alloc()` allocates and initializes default `plat_stmmacenet_data` values.
  - `stmmac_dvr_probe()`, `stmmac_dvr_remove()`, `stmmac_suspend()`, `stmmac_resume()`, and `stmmac_simple_pm_ops` are the primary platform-facing lifecycle APIs.
  - `stmmac_disable_rx_queue()`, `stmmac_enable_rx_queue()`, `stmmac_disable_tx_queue()`, `stmmac_enable_tx_queue()`, `stmmac_xdp_release()`, `stmmac_xdp_open()`, and `stmmac_xsk_wakeup()` are used by XDP/AF_XDP queue reconfiguration and wakeup paths.

- Netdevice operations:
  - `stmmac_open()` and `stmmac_release()` implement `ndo_open` and `ndo_stop`.
  - `stmmac_xmit()` and `stmmac_tso_xmit()` implement normal TX and hardware TSO/USO TX.
  - `stmmac_features_check()`, `stmmac_fix_features()`, and `stmmac_set_features()` gate checksum, TSO, RXCSUM, VLAN, RSS, and split-header behavior.
  - `stmmac_change_mtu()` restarts the device around a newly allocated DMA configuration when running.
  - `stmmac_ioctl()` forwards MII ioctls to phylink.
  - `stmmac_setup_tc()` routes TC offload requests for U32/flower/mqprio/CBS/TAPRIO/ETF.
  - `stmmac_set_mac_address()`, `stmmac_set_rx_mode()`, VLAN add/kill, `stmmac_get_stats64()`, `stmmac_bpf()`, `stmmac_xdp_xmit()`, and `stmmac_xsk_wakeup()` expose standard network stack hooks.

- Phylink and PCS integration:
  - `stmmac_phylink_setup()` builds the phylink configuration, supported interfaces, LPI/EEE capabilities, WoL support, and PCS-derived interface support.
  - `stmmac_mac_get_caps()`, `stmmac_mac_select_pcs()`, `stmmac_mac_link_up()`, `stmmac_mac_link_down()`, `stmmac_mac_enable_tx_lpi()`, `stmmac_mac_disable_tx_lpi()`, and `stmmac_mac_wol_set()` implement `phylink_mac_ops`.
  - `stmmac_init_phy()` attaches a PHY through phylink using firmware nodes, explicit MDIO addresses, or xPCS autonegotiation constraints.
  - `stmmac_check_pcs_mode()` configures reverse SGMII mode when the DMA capability register exposes PCS support.

- DMA ring and queue state:
  - `struct stmmac_dma_conf` carries per-run RX/TX ring sizes, buffer size, and queue arrays.
  - RX state lives in `struct stmmac_rx_queue`: descriptor arrays, page_pool, RX buffers, XDP RXQ info, AF_XDP pool, `cur_rx`/`dirty_rx`, saved multi-descriptor packet state, and coalescing counters.
  - TX state lives in `struct stmmac_tx_queue`: descriptor arrays, DMA mapping metadata, SKB/XDP frame slots, AF_XDP pool, `cur_tx`/`dirty_tx`, MSS/TBS flags, hrtimer, coalescing counters, and queue index.
  - Helpers such as `stmmac_get_rx_desc()`, `stmmac_get_tx_desc()`, `stmmac_set_queue_rx_tail_ptr()`, `stmmac_set_queue_tx_tail_ptr()`, `stmmac_clear_*_descriptors()`, and `stmmac_reset_*_queue()` centralize descriptor-format differences.

- Timestamping/PTP:
  - `stmmac_hwtstamp_set()` and `stmmac_hwtstamp_get()` implement netdevice hardware timestamp configuration.
  - `stmmac_init_timestamping()`, `stmmac_setup_ptp()`, `stmmac_release_ptp()`, `stmmac_update_subsecond_increment()`, and `stmmac_init_tstamp_counter()` program the timestamp counter and register/unregister the PTP clock.
  - `stmmac_get_tx_hwtstamp()`, `stmmac_get_rx_hwtstamp()`, and `stmmac_xdp_rx_timestamp()` deliver timestamps to SKB or XDP metadata consumers.
  - Devlink parameter `phc_coarse_adj` toggles coarse timestamp updates through `stmmac_dl_ts_coarse_set/get()`.

- Interrupt and NAPI:
  - Single-IRQ mode uses `stmmac_interrupt()`.
  - Multi-MSI mode uses `stmmac_mac_interrupt()`, `stmmac_safety_interrupt()`, `stmmac_msi_intr_tx()`, and `stmmac_msi_intr_rx()`.
  - `stmmac_dma_interrupt()` and `stmmac_napi_check()` read DMA status, mask per-direction IRQs, and schedule RX/TX/rxtx NAPI instances.
  - `stmmac_napi_poll_rx()`, `stmmac_napi_poll_tx()`, and `stmmac_napi_poll_rxtx()` drain RX, clean TX, handle AF_XDP zero-copy queues, and re-enable DMA IRQs on completion.

- XDP/AF_XDP:
  - `stmmac_xdp_run_prog()` and `__stmmac_xdp_run_prog()` interpret XDP verdicts.
  - `stmmac_xdp_xmit_xdpf()` sends XDP frames from both RX-side XDP_TX and ndo XDP transmit.
  - `stmmac_rx_zc()`, `stmmac_rx_refill_zc()`, `stmmac_xdp_xmit_zc()`, `stmmac_dispatch_skb_zc()`, and AF_XDP wakeup handling implement XSK zero-copy datapaths.
  - XSK TX metadata hooks request/fill TX timestamps and launch-time/TBS metadata.

## Control Flow

Probe begins at `stmmac_dvr_probe()`, which optionally invokes platform `init()` and then calls `__stmmac_dvr_probe()`. The internal probe validates DMA configuration, allocates a multi-queue Ethernet device, initializes private statistics and workqueue state, applies module/cmdline overrides, handles reset controls, initializes the hardware interface with `stmmac_hw_init()`, configures netdevice operations/features, initializes RSS defaults and MTU limits, adds NAPI contexts, initializes FPE and PCS mode state, enables runtime PM, registers MDIO and PCS, creates phylink, registers devlink if timestamping is usable, registers the netdevice, and creates debugfs files when configured. Error labels unwind in reverse order for devlink, phylink, PCS, MDIO, NAPI, workqueue, and AF_XDP bitmap resources.

Open starts in `stmmac_open()`. It initializes the EEE LPI timer default, allocates a fresh DMA configuration with `stmmac_setup_dma_desc()`, resumes runtime PM, attaches the PHY through phylink, powers legacy SerDes when required, and calls `__stmmac_open()`. The internal open copies TBS state from the previous queue configuration, installs the DMA config into `priv->dma_conf`, resets queue cursors, performs `stmmac_hw_setup()`, starts PTP, initializes TX/RX coalescing timers and thresholds, starts phylink, restores VLAN filters, requests IRQs, enables NAPI queues, starts netdev TX queues, and enables DMA IRQs.

Hardware setup is sequenced by `stmmac_hw_setup()`: it pre-initializes PCS if needed, blocks RX clock stop during reset-sensitive work, resets and initializes DMA through `stmmac_init_dma_engine()`, writes the MAC address, initializes the core, programs MTL queues, safety features, RX checksum offload, MAC enable, DMA operation modes, MMC counters, RX watchdogs, ring lengths, TSO, split-header, VLAN insertion, TBS, real queue counts, DMA start, and hardware VLAN mode. `stmmac_init_dma_engine()` performs pre-reset interface selection, resets DMA, programs DMA/AXI/common channel state, disables DMA IRQs, and writes descriptor base/tail pointers for all RX/TX channels.

Close starts in `stmmac_release()`. It may slow PHY speed for wake-capable devices, then `__stmmac_release()` stops phylink, disables NAPI queues, cancels TX hrtimers, disables netdev TX, frees IRQs, stops all DMA, frees descriptors and buffers, releases PTP, and stops FPE. The outer close powers down SerDes, disconnects the PHY, and releases runtime PM.

Normal TX enters `stmmac_xmit()`. It exits software LPI if necessary, diverts supported GSO frames to `stmmac_tso_xmit()`, applies EST max-SDU checks, checks ring availability, optionally emits a hardware VLAN insertion context descriptor, maps SKB head and fragments, prepares descriptors while leaving the first descriptor ownership until the complete chain is ready, sets TBS launch time if enabled, chooses interrupt-on-completion based on timestamp/coalescing thresholds, advances `cur_tx`, stops the netdev queue when the ring falls below fragment headroom, updates queue stats, grants ownership of the first descriptor, updates netdev TX accounting, kicks DMA, flushes the tail pointer, and arms TX cleanup timer. TSO follows a similar shape but writes an MSS context descriptor when MSS changes and splits payloads across descriptors via `stmmac_tso_allocator()`.

TX completion runs in `stmmac_tx_clean()`. It locks the netdev TX queue, walks from `dirty_tx` to `cur_tx` until DMA-owned descriptors or budget/ring limits stop it, reads status with DMA barriers, handles timestamp completion, completes XSK metadata, unmaps DMA buffers, returns XDP frames, completes XSK descriptors, consumes SKBs, releases descriptors, updates `dirty_tx`, updates BQL with `netdev_tx_completed_queue()`, wakes stopped queues when space returns, possibly drives AF_XDP TX, restarts EEE software LPI, marks pending packets for timer rearm, and updates stats/errors.

RX NAPI enters either `stmmac_rx()` for page_pool/SKB RX or `stmmac_rx_zc()` for AF_XDP zero-copy queues. The normal RX path walks descriptors until budget, DMA ownership, or ring exhaustion. It handles saved multi-descriptor packet state, descriptor status/errors, split-header buffer length calculation, FCS stripping, DMA sync, XDP program execution, SKB construction or fragment append, timestamp/VLAN/hash/checksum setup, GRO delivery, refill of descriptors through page_pool, XDP TX/redirect finalization, and stats updates. The zero-copy path uses XSK buffers, enforces one XSK buffer per RX frame, runs XDP directly on XSK buffers, copies PASS traffic into an SKB for stack delivery, returns or redirects buffers based on verdict, updates need-wakeup state, and batches RX refill.

Interrupt flow differs by mode. In single IRQ mode `stmmac_interrupt()` first ignores interrupts while `STMMAC_DOWN` is set, handles safety errors if no separate safety IRQ exists, processes common MAC interrupts, then processes DMA interrupts. In multi-MSI mode common MAC, safety, TX, and RX interrupts are split. `stmmac_napi_check()` reads DMA status for a channel/direction, masks DMA IRQs under the channel spinlock, schedules the appropriate NAPI instance, and returns status so hard TX errors can trigger threshold bumping or channel reset.

Suspend detaches the netdev if running, disables queues/timers, stops EEE software timer, stops DMA, powers down SerDes, either programs PMT WoL or disables MAC and selects sleep pinctrl, suspends phylink under RTNL, stops FPE, and finally invokes platform suspend. Resume invokes platform resume first, exits PMT/pinctrl sleep state, resets MDIO if needed, powers SerDes, prepares phylink resume, resets queue parameters, frees pending TX buffers, clears descriptors, reruns hardware setup, timestamping and coalescing, restores RX mode and VLAN filters, enables queues/IRQs, resumes phylink, and reattaches the netdev.

## State and Persistence Behavior

The main persistent driver state is `struct stmmac_priv`, stored as netdev private data and as device drvdata. It owns platform data, hardware callback state, DMA capability snapshots, `priv->dma_conf`, phylink/PCS/MDIO handles, runtime PM relationship, timestamping configuration, RSS state, XDP program/pool bitmap, workqueue state bits, IRQ numbers, debugfs/devlink handles, and software statistics.

Queue state is volatile across open/close and some reconfiguration operations. `stmmac_setup_dma_desc()` allocates a temporary DMA configuration for open/MTU change, and `__stmmac_open()` copies it into `priv->dma_conf`. Descriptor rings and page pools are allocated with coherent DMA/page_pool APIs and are freed on close, MTU restart, XDP reconfiguration, or remove. Ring cursors are reset by `stmmac_reset_queues_param()`.

Feature state persists in several places:
- Timestamp settings persist in `priv->tstamp_config`, `priv->hwts_tx_en`, `priv->hwts_rx_en`, `priv->systime_flags`, `priv->default_addend`, and `priv->sub_second_inc`. Resume and devlink coarse-mode changes reprogram hardware from these values.
- VLAN filter state persists in `priv->active_vlans` and `priv->num_double_vlans`, then `stmmac_vlan_restore()` reapplies it after open/resume.
- RSS persists in `priv->rss.key`, `priv->rss.table`, and `priv->rss.enable`.
- EEE/LPI state persists in `eee_timer`, `priv->tx_lpi_timer`, `priv->eee_enabled`, `priv->eee_active`, `priv->eee_sw_timer_en`, `priv->tx_path_in_lpi_mode`, and `priv->tx_lpi_clk_stop`.
- WoL state persists in `priv->wolopts` and device wakeup capability.
- XDP state persists in `priv->xdp_prog` and AF_XDP queue bitmap/pool association managed through external helpers.

The driver uses bit state in `priv->state` for `STMMAC_DOWN`, `STMMAC_SERVICE_SCHED`, `STMMAC_RESET_REQUESTED`, and `STMMAC_RESETING`. Fatal errors and TX timeouts schedule a service work item that closes and reopens the device under RTNL.

## Dependencies and Integration Points

Internal STMMAC dependencies include `stmmac.h`, `hwif.h`, `stmmac_ptp.h`, `stmmac_fpe.h`, `stmmac_pcs.h`, `stmmac_xdp.h`, `dwmac1000.h`, and `dwxgmac2.h`. The file assumes hardware-specific helpers provide register access, descriptor formatting, DMA setup, timestamp register access, queue setup, VLAN filter programming, RSS programming, traffic-control offloads, EST/FPE status, safety feature handling, and PCS integration.

Linux subsystem integration is broad:
- Network core through `net_device_ops`, BQL, NAPI, GRO, ethtool, VLAN, multicast filtering, netdev queues, stats64, and feature negotiation.
- DMA API and page_pool for descriptor and packet buffer ownership.
- phylink/phylib/PCS for link mode, PHY attachment, autonegotiation, LPI/EEE, WoL, and RX clock stop coordination.
- Runtime PM and wake IRQ APIs for register access and suspend/resume.
- PTP and timestamping APIs for PHC registration and SKB/XDP timestamp metadata.
- XDP, BPF, and AF_XDP APIs for in-driver XDP processing and zero-copy sockets.
- TC offload APIs for flower, U32, mqprio, CBS, TAPRIO, and ETF.
- devlink for runtime PHC coarse-adjust parameter exposure.
- debugfs and netdevice notifier for descriptor/capability inspection.
- reset, pinctrl, clock, and platform callback hooks for SoC-specific glue.

## Risks and Edge Cases

- Descriptor ownership ordering is safety-critical. TX paths deliberately write all descriptor fields before setting OWN on the first descriptor and use `wmb()`/`dma_wmb()` before updating tail pointers or context descriptors. Reordering can cause DMA to read partially initialized descriptors.
- RX saved state for multi-descriptor frames (`rx_q->state_saved`) is subtle. Error and length carry-over must stay consistent across NAPI budget exits, XDP verdicts, split-header payloads, and FCS stripping.
- AF_XDP zero-copy mode uses different NAPI (`rxtx_napi`) and buffer lifecycle rules. Queue enable/disable must synchronize with XDP buffers, and `stmmac_disable_all_queues()` uses `synchronize_rcu()` when XSK pools exist.
- Hardware feature combinations can conflict: TSO cannot coexist with TBS on a channel; TSO is gated by PBL and header/MSS constraints; hardware VLAN insertion is disabled for hardware GSO; XDP rejects jumbo MTUs; split-header depends on RX checksum; EEE can trigger interrupt storms on flagged platforms.
- Runtime PM and RX clock stop ordering is fragile. Several functions block phylink RX clock stop around register accesses, while comments note that `stmmac_set_rx_mode()` and VLAN updates may need RXC but can be called in contexts where blocking cannot be done.
- Error unwinding in open/probe/MTU change must keep DMA resources, phylink/PHY attachment, runtime PM, timers, PTP, IRQs, and SerDes state balanced.
- Multi-MSI IRQ allocation has many partial-failure paths; `stmmac_free_irq()` depends on the correct `request_irq_err` stage and index.
- Queue count and ring parameter reinit call close/open around NAPI deletion/addition. Callers must expect link disruption and the code must avoid freeing user-owned state such as platform data.
- `stmmac_vlan_update()` falls back to limited perfect matching when VLAN hash filtering is unavailable, so more than two active VLANs can fail.
- Devlink coarse timestamp changes call `stmmac_update_subsecond_increment()` directly and assume timestamp registers are accessible and timestamping has been initialized.

## Test Signals and Validation Ideas

- Probe/remove: verify successful registration and clean remove across platform variants, with runtime PM enabled/disabled, MDIO present/absent, fixed-link, xPCS, devlink timestamp support, and debugfs enabled.
- Open/close: exercise repeated `ip link set up/down`, SerDes modes, multi-MSI and shared IRQ modes, PTP-capable and non-PTP hardware, and failure injection for descriptor allocation, IRQ allocation, PHY attach, and DMA reset.
- TX datapath: test normal SKB, SG, jumbo, checksum offload fallback, VLAN insertion, TSO/USO, TBS launch time, timestamped TX, queue stop/wake, BQL accounting, and TX timeout reset.
- RX datapath: test checksum offload, VLAN stripping, RSS hash, split-header, multi-descriptor packets, GRO delivery, timestamped RX, RX refill under memory pressure, and descriptor errors.
- XDP/AF_XDP: run XDP_PASS/DROP/TX/REDIRECT, ndo_xdp_xmit, AF_XDP zero-copy RX/TX, need-wakeup behavior, pool setup/teardown while interface is running, and MTU rejection with XDP enabled.
- Link/PHY: verify phylink modes, xPCS selection, EEE LPI enable/disable, RX clock stop behavior, MAC speed clock changes, pause flow control, WoL, and reverse SGMII.
- PM: suspend/resume with and without WoL, runtime PM during MDIO/MAC address/VLAN operations, and resume reprogramming of timestamping, VLANs, RX mode, queues, and IRQs.
- TC/offloads: validate mqprio, CBS, TAPRIO/EST, ETF/TBS, flower/U32 offloads, FPE/MMSV handling, and max-SDU drops.
- Debug/observability: inspect debugfs ring/capability output, `ethtool -S`, stats64 counters, devlink `phc_coarse_adj`, and PTP timestamp monotonicity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_mdio.c

## Purpose

`stmmac_mdio.c` implements the STMMAC MII/MDIO bus layer. It provides Clause 22 and Clause 45 register access for GMAC, GMAC4, and XGMAC hardware variants, chooses the MDIO CSR/MDC clock divider, registers and unregisters the Linux `mii_bus`, resets PHYs through optional GPIO or dummy bus cycles, discovers or binds PHY devices, and initializes or destroys PCS/xPCS instances used by the main driver.

The file is the bridge between the STMMAC MAC register interface and Linux phylib/phylink. It hides hardware-specific MDIO register formats while exposing standard `mii_bus` callbacks to phylib.

## Important APIs, Types, and Functions

- Register bit definitions:
  - Generic GMII/MII access uses `MII_ADDR_GBUSY`, `MII_ADDR_GWRITE`, and `MII_DATA_GD_MASK`.
  - GMAC4 uses command bits `MII_GMAC4_WRITE`, `MII_GMAC4_READ`, register address shift `MII_GMAC4_REG_ADDR_SHIFT`, and Clause 45 enable `MII_GMAC4_C45E`.
  - XGMAC uses `MII_XGMAC_BUSY`, `MII_XGMAC_SADDR`, `MII_XGMAC_WRITE`, `MII_XGMAC_READ`, C22 port bitmap `XGMAC_MDIO_C22P`, and PA/DA shifts.

- Core helpers:
  - `stmmac_mdio_wait()` polls a register until a busy mask clears and returns `-EBUSY` on timeout.
  - `stmmac_mdio_format_addr()` builds the generic MII address register using hardware-provided address/register masks, the precomputed CSR clock bits, and the busy bit.
  - `stmmac_mdio_access()` wraps generic read/write transactions with runtime PM, busy polling, data/address writes, final busy wait, and optional data readback.
  - `stmmac_mdio_read()` and `stmmac_mdio_write()` are thin generic wrappers.

- XGMAC-specific access:
  - `stmmac_xgmac2_c22_format()` marks a PHY address as Clause 22 in `XGMAC_MDIO_C22P`, handles pre-2.20 address limitations, and formats the address field.
  - `stmmac_xgmac2_c45_format()` clears the C22 port bit for Clause 45 and builds PA/DA/register address fields.
  - `stmmac_xgmac2_mdio_read()` and `stmmac_xgmac2_mdio_write()` perform XGMAC data-register based transactions with runtime PM and busy polling.
  - `stmmac_xgmac2_mdio_read_c22/read_c45/write_c22/write_c45()` are `mii_bus` callbacks.

- Generic GMAC/GMAC4 access:
  - `stmmac_mdio_read_c22()` chooses the GMAC4 read command or legacy zero command.
  - `stmmac_mdio_read_c45()` encodes the Clause 45 device address and shifted register address for GMAC4.
  - `stmmac_mdio_write_c22()` chooses `MII_GMAC4_WRITE` or legacy `MII_ADDR_GWRITE`.
  - `stmmac_mdio_write_c45()` encodes GMAC4 Clause 45 writes.

- Bus lifecycle and PCS:
  - `stmmac_mdio_reset()` optionally toggles a firmware-described reset GPIO with configurable delays and performs a legacy dummy MDIO read workaround for STE101P-style PHY reset completion.
  - `stmmac_pcs_setup()` creates PCS state through platform `pcs_init`, firmware `pcs-handle`, or a PCS MDIO address selected from `pcs_mask`; it also configures xPCS EEE multiplier when an xPCS object is created.
  - `stmmac_pcs_clean()` calls platform PCS exit and destroys any `dw_xpcs` object.
  - `stmmac_clk_csr_set()` maps the STMMAC CSR clock rate to an MDC divider field for standard, sun8i, or XGMAC mappings.
  - `stmmac_mdio_bus_config()` stores the selected and mask-truncated divider bits in `priv->gmii_address_bus_config`.
  - `stmmac_mdio_register()` allocates and registers `struct mii_bus`, installs variant-specific callbacks, applies IRQ/phy/pcs masks, handles OF registration, performs XGMAC dummy reads, skips scanning for fixed links, discovers PHYs when no explicit node is present, and records `priv->mii`.
  - `stmmac_mdio_unregister()` unregisters and frees the bus.
  - `stmmac_mdio_lock()` and `stmmac_mdio_unlock()` export optional external serialization on the bus `mdio_lock`.

## Control Flow

During probe, `stmmac_mdio_register()` is called after runtime PM and hardware initialization are active. If platform MDIO bus data is absent, it returns success without creating a bus. Otherwise it computes `priv->gmii_address_bus_config`, allocates a `mii_bus`, copies platform IRQ mappings, names and IDs the bus, installs callback functions based on `priv->plat->core_type`, sets reset callback when requested, sets the PHY mask to include both normal PHY and PCS masks, and calls `of_mdiobus_register()`.

If OF registration returns `-ENODEV`, the bus is treated as disabled and registration exits without error after freeing the bus. Other registration errors are fatal. For XGMAC, the driver performs a dummy Clause 45 read after registration. Fixed links skip PHY scanning. If a PHY node or MDIO node is explicitly supplied, scanning is also skipped. Otherwise the first PHY is located, validated against XGMAC pre-2.20 maximum C22 address limits when applicable, optional probed IRQ is assigned, `plat->phy_addr` is filled if still autodetect, and `phy_attached_info()` logs the result.

Generic MDIO read/write transactions flow through the Linux mii bus callbacks into `stmmac_mdio_access()`. That function resumes runtime PM, waits for the address register busy bit to clear, writes data and formatted address/command, waits again for completion, reads the data register for reads, and releases runtime PM. XGMAC transactions are similar but use the XGMAC MDIO data register busy bit and split address/data registers differently.

PCS setup runs after MDIO registration. Platform-specific `pcs_init()` takes priority. If firmware supplies `pcs-handle`, the code creates an xPCS object from that fwnode. Otherwise `mdio_bus_data->pcs_mask` can select an MDIO address for `xpcs_create_mdiodev()`. The created xPCS is stored in `priv->hw->xpcs`, making it available to main-file phylink setup and MAC PCS selection. Cleanup reverses platform PCS and xPCS ownership.

## State and Persistence Behavior

The MDIO bus pointer persists in `priv->mii` from successful registration until `stmmac_mdio_unregister()`. `new_bus->priv` points back to the netdevice, so callbacks retrieve `struct stmmac_priv` with `netdev_priv(bus->priv)`. The bus owns callback pointers, IRQ mapping, PHY masks, parent device, and ID string.

`priv->gmii_address_bus_config` stores the selected CSR/MDC clock divider bits and is reused by every transaction. This value is derived from either platform `clk_csr` or current `stmmac_clk` rate and hardware register mask layout.

PCS state persists in `priv->hw->xpcs` when xPCS creation succeeds. It is destroyed by `stmmac_pcs_clean()` and set back to `NULL`. Platform PCS hooks may also maintain state outside this file through `plat->pcs_init` and `plat->pcs_exit`.

Runtime PM is acquired for each MDIO transaction, so MDIO state is transiently powered only around register access. Reset GPIO descriptors are devm-managed and not stored by this file after `stmmac_mdio_reset()` completes.

## Dependencies and Integration Points

This file depends on `stmmac.h` for `struct stmmac_priv`, platform data, MDIO bus data, register offsets, and core type constants; and on `dwxgmac2.h` for XGMAC MDIO registers and core version checks.

Kernel subsystem dependencies include:
- `mii_bus`, phylib, `phy_device`, `phy_find_first()`, and `phy_attached_info()`.
- OF/fwnode MDIO helpers, including `of_mdiobus_register()`, `fwnode_get_phy_node()` usage from the main file, and firmware `pcs-handle` lookup here.
- Runtime PM for safe register access while clocks may be gated.
- GPIO consumer API for optional PHY reset signaling.
- Clock API for deriving MDC divider from `plat->stmmac_clk`.
- xPCS helpers `xpcs_create_fwnode()`, `xpcs_create_mdiodev()`, `xpcs_destroy()`, and `xpcs_config_eee_mult_fact()`.

The main file integrates this implementation by calling MDIO register/unregister during probe/remove, MDIO reset during resume when no WoL PMT path is active, PCS setup before phylink setup, PCS cleanup during error/remove, and MDIO bus access indirectly through phylink/phylib.

## Risks and Edge Cases

- Busy polling timeouts return `-EBUSY` after 10 ms. Hardware that never clears busy bits will make PHY access fail but should not hang the kernel.
- XGMAC cores older than 2.20 support Clause 22 addresses only up to 3. The code rejects callback access above that range, warns if firmware configured a larger PHY address, and limits autodiscovery validation.
- `stmmac_xgmac2_c22_format()` modifies the `XGMAC_MDIO_C22P` bitmap before every C22 transaction. Concurrent MDIO access must remain serialized by the mii bus lock or exported lock helpers.
- `stmmac_mdio_bus_config()` masks out-of-range clock divider values after warning. A bad platform `clk_csr` can still select an unintended truncated divider.
- When `of_mdiobus_register()` returns `-ENODEV`, the function treats the MDIO bus as disabled and succeeds. Callers must tolerate `priv->mii == NULL`.
- If no fixed link, no explicit PHY node, and no scan result is found, probe fails with `-ENODEV`; this is correct for PHY-backed designs but unsuitable for firmware that forgot to describe fixed-link/PHY wiring.
- `stmmac_mdio_reset()` uses optional GPIO reset delays in microseconds rounded up to milliseconds, so sub-millisecond requested delays are stretched.
- PCS creation has multiple ownership modes. Platform `pcs_init` can populate hardware state without returning an xPCS object, while fwnode/MDIO creation stores `priv->hw->xpcs`; cleanup must match the setup path.
- Clause 45 generic GMAC4 access encodes `phyreg` into the data register for address phase style behavior. Any register-format mismatch in hardware callbacks would break C45 transactions.

## Test Signals and Validation Ideas

- Register probe with MDIO disabled, no MDIO bus data, fixed-link, explicit PHY node, explicit MDIO node, autodetected PHY, and missing PHY.
- Exercise C22 read/write on GMAC, GMAC4, XGMAC pre-2.20, and XGMAC 2.20+ cores, including invalid pre-2.20 PHY addresses.
- Exercise C45 read/write on GMAC4 and XGMAC, including the XGMAC dummy read path after bus registration.
- Validate MDC divider selection with platform fixed `clk_csr`, auto-derived standard clock rates, sun8i mapping, XGMAC mapping, and out-of-mask values that should warn and truncate.
- Verify runtime PM balance during successful reads/writes and timeout/error paths.
- Test reset GPIO sequencing with absent GPIO, present GPIO, reset delays, and legacy dummy-read behavior.
- Validate PCS setup from platform hooks, firmware `pcs-handle`, MDIO `pcs_mask`, and absent PCS, followed by cleanup and remove error unwinds.
- Confirm `stmmac_mdio_lock()`/`unlock()` are no-ops without a bus and serialize correctly with a registered bus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_mdio.c -->
