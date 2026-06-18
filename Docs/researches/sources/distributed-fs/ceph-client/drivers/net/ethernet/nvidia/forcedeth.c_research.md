# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/nvidia/forcedeth.c

## Purpose

`forcedeth.c` is the reverse-engineered Linux Ethernet driver for NVIDIA nForce/nForce2/nForce3/CK804/MCP family PCI Ethernet controllers. It is a full netdev driver handling PCI probe/remove, DMA ring allocation, PHY discovery and vendor workarounds, TX/RX packet processing, NAPI, interrupt moderation, MSI/MSI-X setup, ethtool operations, wake-on-LAN, power management, and a large PCI ID table mapping hardware revisions to feature flags.

Within the Ceph client source tree, this driver is infrastructure below the distributed filesystem layer. Its correctness affects network connectivity, latency, checksum/VLAN offload, jumbo frames, power transitions, and error recovery for hosts whose Ceph traffic uses nForce Ethernet hardware.

## Important APIs, Types, and Functions

- Register and feature definitions: `NvReg*` offsets, `NVREG_*` bitfields, `DEV_*` feature flags, descriptor flags, PHY constants, interrupt masks, ring limits, and timeout constants describe the reverse-engineered hardware contract.
- Descriptor types: `struct ring_desc` for original 32-bit descriptors, `struct ring_desc_ex` for extended descriptors, and `union ring_type` for version-dependent ring pointers.
- `struct fe_priv`: central private state, including locks, NAPI, PCI device, MMIO base, descriptor version, ring memory, skb maps, IRQ masks, link/PHY state, timers, MSI/MSI-X state, pause flags, stats, power-save registers, management-unit state, and workaround flags.
- TX/RX context: `struct nv_skb_map` tracks skb ownership, DMA address/length, mapping type, and delayed ownership flipping for limited-TX hardware.
- Stats: `struct nv_ethtool_stats`, `struct nv_txrx_stats`, per-CPU software stats with `u64_stats_sync`, and hardware stat accumulation under `hwstats_lock`.
- PCI lifecycle: `nv_probe`, `nv_remove`, `nv_suspend`, `nv_resume`, `nv_shutdown`, and `forcedeth_pci_driver`.
- Netdev operations: `nv_open`, `nv_close`, `nv_start_xmit`, `nv_start_xmit_optimized`, `nv_tx_timeout`, `nv_change_mtu`, `nv_set_mac_address`, `nv_set_multicast`, `nv_fix_features`, `nv_set_features`, and `nv_get_stats64`.
- Ring/DMA lifecycle: `setup_hw_rings`, `free_rings`, `nv_init_rx`, `nv_init_tx`, `nv_init_ring`, `nv_alloc_rx`, `nv_alloc_rx_optimized`, `nv_drain_tx`, `nv_drain_rx`, `nv_drain_rxtx`, and DMA unmap helpers.
- RX/TX completion: `nv_tx_done`, `nv_tx_done_optimized`, `nv_rx_process`, `nv_rx_process_optimized`, `nv_getlen`, `rx_missing_handler`, and `nv_tx_flip_ownership`.
- Interrupts/NAPI/timers: `nv_nic_irq`, `nv_nic_irq_optimized`, split MSI-X handlers, `nv_napi_poll`, `nv_do_nic_poll`, `nv_do_rx_refill`, `nv_do_stats_poll`, `nv_request_irq`, and `nv_free_irq`.
- PHY/link handling: `mii_rw`, `phy_reset`, `phy_init`, Realtek/Cicada/Vitesse/Marvell init helpers, `nv_update_linkspeed`, `nv_force_linkspeed`, `nv_linkchange`, and `nv_link_irq`.
- ethtool: `ops` includes driver info, WOL, register dump, nway reset, ring params, pause params, stats strings/data, self-test, timestamp info, and link ksettings.
- Management unit and power helpers: `nv_mgmt_acquire_sema`, `nv_mgmt_release_sema`, `nv_mgmt_get_version`, `nv_txrx_gate`, `nv_mac_reset`, `nv_restore_mac_addr`, and `nv_restore_phy`.

## Control Flow

Probe starts with `nv_probe`. It allocates `net_device` and `fe_priv`, initializes locks, per-CPU stats, timers, enables the PCI device, requests regions, chooses the register-window size from feature flags, finds a memory BAR, and copies `driver_data` from the PCI ID table. It selects descriptor version 1, 2, or 3 from feature flags and requested high-DMA capability, sets MTU limits and netdev hardware features for checksum, SG, TSO, VLAN, high DMA, and loopback, maps MMIO, allocates a combined coherent RX/TX ring and skb context arrays, registers NAPI and ethtool operations, reads/restores/corrects the MAC address ordering, disables WOL, powers up low-power-capable devices, configures interrupt mode and workarounds, scans MII addresses for a valid PHY, optionally coordinates with the management unit semaphore, initializes the PHY unless firmware already did so, registers the netdev, and logs discovered features.

Open (`nv_open`) powers up the PHY, ungates TX/RX clocks, resets MAC/TXRX state, clears filters and control registers, initializes ring software state and RX buffers, programs hardware ring base/size/offload registers, configures link speed defaults, backoff seed behavior, polling interval, MII masks, wake flags, and adapter control, clears pending interrupts, requests the selected IRQ mode, enables hardware interrupts, initializes multicast filtering, forces one link-speed update, starts RX/TX engines, starts the queue, enables NAPI, sets carrier according to link state, arms OOM refill and stats timers as needed, and applies loopback if the feature was enabled while down.

TX has two variants. `nv_start_xmit` handles descriptor versions 1/2, while `nv_start_xmit_optimized` handles descriptor version 3. Both calculate required descriptor entries by splitting skb head/fragments into chunks of at most `NV_TX2_TSO_MAX_SIZE`, stop the queue if the ring lacks space, map the skb head and fragments, populate descriptor DMA addresses and flag/length words, mark the last descriptor, store the skb on the final context, add TSO or checksum offload flags when applicable, timestamp and account the skb, advance `put_tx`, and kick hardware unless batching via `netdev_xmit_more`. The optimized path also handles VLAN tag insertion and the `tx_limit` workaround by withholding the VALID bit until enough prior packets complete.

TX completion happens in `nv_tx_done` or `nv_tx_done_optimized` under `np->lock`. Each scans descriptors until it reaches the producer pointer, a hardware-owned descriptor, or the work limit. It unmaps DMA, checks last-packet and error flags, updates software TX stats, applies collision/backoff reseeding on certain retry errors, frees completed skbs, calls `netdev_completed_queue`, wakes a stopped queue if progress was made, and in optimized limited-TX mode flips ownership to release delayed descriptors.

RX allocation preposts skb buffers with DMA mappings through `nv_alloc_rx` or `nv_alloc_rx_optimized`. RX processing scans completed descriptors, unmaps DMA, validates descriptor status, corrects certain length-mismatch or framing cases, drops hard-error packets, sets checksum-unnecessary for IP/TCP or IP/UDP checksum statuses, decodes VLAN tags in the optimized path when VLAN RX acceleration is enabled, hands valid packets to GRO, updates software RX stats, advances descriptor/context cursors, and later refills descriptors. Allocation failure schedules the OOM refill timer, which reschedules NAPI.

Interrupt handling depends on mode. Non-MSI-X or single-vector MSI-X paths acknowledge status, store `np->events`, apply an MSI workaround, mask interrupts, and schedule NAPI. NAPI performs TX completion, RX processing/refill, dynamic interrupt-mode changes, link handling, link timer polling, recoverable-error scheduling, and interrupt re-enable. Throughput MSI-X mode can request separate RX, TX, and OTHER handlers that process limited work directly and fall back to `nic_poll` when they exceed `max_interrupt_work` or see recoverable errors. `nv_do_nic_poll` safely disables/synchronizes an IRQ, performs recovery reset/reinit when needed, re-enables masks, and invokes the appropriate handler.

Link setup is mostly custom MII logic rather than phylib. `mii_rw` serializes PHY register access through MAC MII registers. `phy_init` handles Marvell, Realtek, Cicada, and Vitesse quirks, configures advertisement, gigabit advertisement for RGMII, resets or restarts autonegotiation, and optionally powers down the PHY. `nv_update_linkspeed` double-reads BMSR, resolves autonegotiated or forced speed/duplex, updates MAC slot time, PHY interface bits, TX deferral, TX watermarks, MAC link speed, and pause-frame negotiation; it restarts TX/RX when necessary and drives carrier transitions through `nv_linkchange`.

Close (`nv_close`) marks shutdown, disables NAPI, synchronizes interrupts, deletes timers, stops queue and engines, disables hardware interrupts, frees IRQs/MSI, drains rings, and either keeps RX/WOL path active or powers down PHY and gates clocks according to WOL and `phy_power_down`. Remove unregisters the netdev, restores original MAC ordering for future probes/kexec, restores Realtek PHY crossover state, releases the management semaphore, frees rings, unmaps MMIO, releases PCI regions, disables the PCI device, frees per-CPU stats, and frees the netdev.

## State and Persistence Behavior

The driver keeps extensive volatile runtime state in `struct fe_priv`: ring cursors, descriptor memory, skb maps, interrupt masks, timers, link state, PHY identity, offload feature bits, pause flags, MSI flags, and software stats. Descriptor memory is coherent DMA memory allocated at probe or ring resize and reused across opens until resized or removed. RX skbs are continually posted and recycled; TX skb ownership transfers to hardware via descriptor VALID bits and returns on completion.

Some state intentionally persists across lifecycle boundaries. `orig_mac` stores the hardware MAC words as originally found so the driver can restore reversed ordering on remove, shutdown, or kexec-sensitive paths. `saved_config_space` stores MMIO register contents over suspend/resume. `wolenabled` controls device wakeup and shutdown D3 wake behavior. Module parameters persist for the module lifetime and alter interrupt mode, DMA width, PHY crossover behavior, PHY power-down, and TX-timeout debugging. The management semaphore state persists until release and protects PHY initialization when firmware management is active.

Stats are split: per-CPU software counters track packet/byte/drop paths, while hardware counters are periodically accumulated under `hwstats_lock` to avoid wraparound and exported through ethtool and rtnl stats. Hardware feature state such as VLAN strip/insert and RX checksum is mirrored in `txrxctl_bits` and rewritten during feature changes, open, MTU changes, recovery, and ring resize.

## Dependencies and Integration Points

- PCI core: ID table matching, BAR/resource handling, `pci_enable_device`, DMA mask setup, MSI/MSI-X, power-state and wake handling, and shutdown callbacks.
- netdev stack: NAPI, qdisc accounting, queue stop/wake, GRO, feature negotiation, VLAN acceleration, link carrier, watchdog timeout, rtnl stats, and netpoll.
- Linux DMA API: coherent rings, streaming skb maps/unmaps, high-DMA feature negotiation.
- MII/ethtool APIs: direct MII register definitions, ethtool link ksettings conversion, ring/pause/stats/self-test operations, WOL, register dump, and timestamp info.
- Timers and locking: `timer_list` for OOM refill, NIC polling/recovery, and stats polling; spinlocks for hardware and stats paths; netdev and address locks around reconfiguration.
- Module parameters: `max_interrupt_work`, `optimization_mode`, `poll_interval`, `msi`, `msix`, `dma_64bit`, `phy_cross`, `phy_power_down`, and `debug_tx_timeout`.

## Risks and Edge Cases

- The driver is reverse engineered and contains many hardware-specific magic values, making regressions likely if register sequencing changes without hardware coverage.
- MSI-X capability is effectively disabled by `#if 0` despite code support, indicating known issues around IRQ mask behavior and NAPI.
- TX timeout recovery is complex: it stops TX, drains/cleans descriptors, restores hardware position, and restarts; incorrect `tx_change_owner` or descriptor cursor state can drop or duplicate completions.
- RX allocation failure depends on timer-driven NAPI rescheduling; sustained memory pressure can leave RX descriptors unavailable and increase drops.
- Multiple live reconfiguration paths, including MTU change, ring resize, pause changes, feature toggles, and link ksettings, stop engines and manipulate rings under several locks. Lock ordering and long polling delays are explicit concerns.
- `nv_loopback_test` maps the TX test skb with `DMA_FROM_DEVICE` even though it is placed in a TX descriptor, which is suspicious and worth checking against DMA API expectations.
- Some suspend/resume loops iterate `i <= register_size / sizeof(u32)`, which may read/write one u32 beyond the nominal register-size count.
- Custom MII handling lacks phylib integration, so modern PHY features, EEE, advanced link modes, and standardized state machines are absent.
- Power-down behavior can persist across reboot according to the module parameter documentation, so enabling `phy_power_down` carries operational risk on older systems.
- Feature flags in the PCI ID table are dense and easy to misapply; wrong flags can select descriptor format, DMA mask, stats version, pause-frame version, or workaround behavior incorrectly.

## Test Signals

- Build tests with `CONFIG_FORCEDETH=y` and `m`, plus PM, netpoll, VLAN, MSI, and 64-bit DMA configurations.
- PCI probe tests on representative hardware for descriptor v1, v2, and v3 families, with and without high-DMA mask success.
- Packet tests: small packets, fragmented skbs, checksum offload, TSO, VLAN TX/RX, jumbo MTU where supported, queue stop/wake, watchdog timeout, and GRO receive.
- Interrupt tests: legacy INTx, MSI, dynamic/throughput/CPU optimization modes, forced timer IRQ, max-work fallback to `nic_poll`, and recoverable-error reset.
- PHY/link tests across Realtek 8201/8211, Marvell E3016, Cicada, and Vitesse hardware if available; validate autonegotiation, forced 10/100 modes, link down/up, pause negotiation, and loopback.
- ethtool tests: stats strings/counts for each stats version, register dump size, ring resize, pause params, WOL enable/disable, offline self-tests, and link ksettings.
- Power-management tests: suspend/resume with interface up/down, WOL shutdown, kexec MAC restoration, and module unload/reload.
- Fault injection: DMA mapping failure, ring allocation failure, IRQ request failure, invalid MAC address, missing PHY, and low-memory RX refill behavior.
