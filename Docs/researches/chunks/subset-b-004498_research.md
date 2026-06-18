# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_main.c lines 9245-12433

Chunk ID: `subset-b-004498`

## Scope and Purpose

This chunk is the tail of the Intel `ixgbe` PCI Ethernet driver main file. It covers the driver-facing netdev transmit and control entry points, traffic-class and classifier offload plumbing, XDP setup and XDP TX, per-ring disable/enable helpers, PCI probe/remove, PCI error recovery, and module registration. Earlier chunks define many helper routines and data structures used here; this chunk wires those lower-level routines into Linux networking, PCI, devlink, SR-IOV, DCB, XDP, ethtool/Flow Director, and power/error-management interfaces.

The code is mostly orchestration: it validates Linux subsystem requests, updates `struct ixgbe_adapter` state, programs hardware via `struct ixgbe_hw` operation tables and register macros, and performs ordered teardown on errors and module/device removal.

## Important APIs, Types, and Functions

- `ixgbe_select_queue()` is compiled with FCoE support and implements FCoE/FIP queue selection. It uses subordinate-device traffic class mapping when `sb_dev` is present, otherwise uses the adapter FCoE ring feature offset and indices.
- `ixgbe_xmit_xdp_ring()`, `ixgbe_xdp_ring_update_tail()`, `ixgbe_xdp_ring_update_tail_locked()`, and `ixgbe_xdp_xmit()` implement XDP frame TX into ixgbe TX descriptors, DMA mapping, descriptor ordering, optional ring locking, and tail doorbell updates.
- `ixgbe_xmit_frame_ring()`, `__ixgbe_xmit_frame()`, and `ixgbe_xmit_frame()` are the normal skb TX path exposed as `.ndo_start_xmit`. They handle descriptor budgeting, VLAN metadata, PTP timestamp ownership, DCB priority rewriting, FCoE offload, IPsec TX offload, TSO/checksum offloads, Flow Director ATR, and final DMA descriptor mapping.
- `ixgbe_set_mac()`, `ixgbe_mdio_read()`, `ixgbe_mdio_write()`, `ixgbe_ioctl()`, `ixgbe_add_sanmac_netdev()`, and `ixgbe_del_sanmac_netdev()` provide netdev address, MDIO, MII ioctl, and SAN MAC integration.
- `ixgbe_get_stats64()` and `ixgbe_ndo_get_vf_stats()` export PF ring counters and VF stats. Ring counters are read with `u64_stats_fetch_begin/retry()` under RCU-safe ring pointer access.
- `ixgbe_setup_tc()`, `ixgbe_set_prio_tc_map()`, and `ixgbe_validate_rtr()` manage traffic classes and DCB state. Reconfiguration closes/resets the device, rebuilds interrupt/ring allocation, defragments macvlan pools, and reopens the interface if it was running.
- `ixgbe_setup_tc_cls_u32()` and helpers (`ixgbe_configure_clsu32*`, `ixgbe_delete_clsu32()`, `ixgbe_clsu32_build_input()`, `parse_tc_actions()`) translate `tc u32` classifier offload requests into Flow Director perfect filters and optional jump-table state.
- `ixgbe_setup_tc_block_cb()`, `ixgbe_setup_tc_mqprio()`, and `__ixgbe_setup_tc()` are the netdev TC setup entry points for block classifier and mqprio offload.
- `ixgbe_fix_features()` and `ixgbe_set_features()` reconcile requested netdev features with hardware state, XDP restrictions, RSC/LRO state, Flow Director modes, VLAN filter mode, and L2 forwarding offload.
- `ixgbe_fwd_add()` and `ixgbe_fwd_del()` implement accelerated macvlan/L2 forwarding station support through VMDq pools and subordinate channels.
- `ixgbe_features_check()` strips unsupported per-skb offload features when header lengths exceed context descriptor encoding limits or tunnel TSO cannot safely mangle inner IP ID fields.
- `ixgbe_xdp_setup()` and `ixgbe_xdp()` expose `.ndo_bpf` for XDP program and AF_XDP pool setup.
- `ixgbe_netdev_ops` is the central `struct net_device_ops` table tying this chunk's callbacks to the kernel networking stack.
- `ixgbe_txrx_ring_disable()` and `ixgbe_txrx_ring_enable()` quiesce and restart one RX/TX/XDP queue group, including IRQ synchronization, NAPI disable/enable, hardware descriptor-control polling, ring cleanup, and stat reset.
- `ixgbe_enumerate_functions()`, `ixgbe_wol_supported()`, `ixgbe_set_fw_version*()`, and `ixgbe_recovery_probe()` support probe-time capability reporting, WoL selection, firmware version strings, and E610 firmware recovery mode.
- `ixgbe_probe()` and `ixgbe_remove()` are the PCI lifecycle core. They allocate devlink/netdev/adapter resources, initialize hardware operation tables, set feature bits, register netdev/devlink, and unwind resources in reverse order on failure/removal.
- `ixgbe_io_error_detected()`, `ixgbe_io_slot_reset()`, and `ixgbe_io_resume()` implement PCI AER error recovery, including SR-IOV VF error detection and FLR for offending VFs when possible.
- `ixgbe_driver`, `ixgbe_init_module()`, and `ixgbe_exit_module()` register and unregister the PCI driver and global driver workqueue/debug/DCA hooks.

## Control Flow

Normal packet TX enters through `ixgbe_netdev_ops.ndo_start_xmit -> ixgbe_xmit_frame() -> __ixgbe_xmit_frame() -> ixgbe_xmit_frame_ring()`. The path pads short packets for hardware payload requirements, rejects disabled rings with `NETDEV_TX_BUSY`, reserves descriptors, sets `first` buffer metadata, chooses VLAN tagging mode, optionally claims PTP TX timestamp state, applies DCB priority handling, runs FCoE/IPsec/TSO/checksum offload setup, optionally programs ATR metadata, and finally calls `ixgbe_tx_map()`. Drop/error paths free the skb and release timestamp ownership if it was acquired.

XDP TX enters through either internal driver paths calling `ixgbe_xmit_xdp_ring()` or external `.ndo_xdp_xmit -> ixgbe_xdp_xmit()`. The ndo path verifies device state, carrier/running status, flags, configured XDP ring, and disabled TX state. It then optionally locks the ring, maps each `xdp_frame` fragment into one descriptor chain, updates `ring->next_to_use`, and flushes the tail when requested. Memory barriers protect descriptor visibility before cleanup/hardware consumption.

Traffic-class setup enters through `.ndo_setup_tc`. For `TC_SETUP_QDISC_MQPRIO`, `ixgbe_setup_tc_mqprio()` delegates to `ixgbe_setup_tc()`. For `TC_SETUP_BLOCK`, `flow_block_cb_setup_simple()` registers `ixgbe_setup_tc_block_cb()`, which accepts only chain 0 offloadable classifier requests and supports `TC_SETUP_CLSU32`. `ixgbe_setup_tc()` is disruptive: it closes or resets the device, clears interrupt allocation, toggles DCB flags and netdev TC maps, revalidates hardware priority mapping, rebuilds interrupts, reassigns macvlan pools, then reopens if needed.

The `tc u32` offload flow is split by command. Hnode add/delete manages `adapter->tables` bitmap. Knode add/replace builds a Flow Director input/mask from the currently valid parse graph, validates link-table use, parses actions as either drop or redirect-to-VF/macvlan, enforces a single global mask for all perfect filters, writes the hardware perfect filter, and records it through the ethtool Flow Director entry list. Delete removes either one hardware filter or, if the deleted handle is a jump link, all child filters and the associated jump table.

Probe is a long staged initialization pipeline: enable PCI memory device, set DMA mask, reserve BARs, allocate devlink-backed adapter and multi-queue netdev, map BAR0, install MAC/EEPROM/PHY ops from `ixgbe_info_tbl`, initialize MDIO hooks and netdev/ethtool ops, run `ixgbe_sw_init()`, handle E610 recovery mode if firmware error is detected, fetch E610 capabilities/flash data, configure feature flags, reset hardware, enable SR-IOV when compiled and requested, initialize netdev feature sets, validate EEPROM/MAC address, set timers/work, initialize rings/interrupts/stats, configure WoL/version/bus reporting, register netdev/devlink, initialize optional DCA/HWMON/debug/MII/FW logging, and return. Each labeled error block unwinds only resources allocated up to that stage.

Remove follows the reverse lifecycle: unregister devlink, destroy regions/fwlog/debug, mark removing, cancel service work, unregister MDIO, remove DCA/HWMON/SAN MAC/SR-IOV/netdev, unregister devlink port, stop IPsec, clear interrupts, release hardware control, free DCB/jump-table/mac/RSS/AF_XDP resources, unmap BARs, release PCI regions, free netdev/devlink, destroy E610 ACI mutex, and disable the PCI device once.

PCI error recovery first tries SR-IOV-specific bad-VF detection by reading root-port AER header logs and decoding requestor ID. If an offending VF is found, it logs the TLP and issues a function-level reset, increments `vferr_refcount`, and reports recovered. Otherwise it detaches the netdev, closes it if running, disables the PCI function, and requests slot reset unless the channel failure is permanent. Slot reset reenables the device and calls `ixgbe_reset()`. Resume reopens and reattaches unless it is merely consuming a deferred VF error reference.

## State and Persistence Behavior

Primary persistent runtime state is in `struct ixgbe_adapter`: feature flags (`flags`, `flags2`), state bits (`__IXGBE_DOWN`, `__IXGBE_DISABLED`, `__IXGBE_SERVICE_INITED`, `__IXGBE_REMOVING`, `__IXGBE_PTP_TX_IN_PROGRESS`), queue/ring arrays, ring feature limits/offsets, DCB config, Flow Director filter mask/list/jump tables, SR-IOV VF info, macvlan forwarding pool bitmap, XDP program pointer, devlink state, WoL setting, firmware/EEPROM version string, and optional subsystem resources.

Hardware-visible state is programmed through MMIO register writes and operation tables: descriptor rings and tails, TXDCTL/RXDCTL enable bits, interrupt masks, VMDq/bridge registers, source address pruning, Flow Director masks/perfect filters, WUS WoL status, DCA control, SR-IOV mailbox/total VFs, and hardware reset/start hooks.

Reference and lifetime state is important. PTP TX timestamping stores a held skb in `adapter->ptp_tx_skb` and marks `__IXGBE_PTP_TX_IN_PROGRESS`; the error path must cancel work, free the skb, and clear the bit. XDP setup atomically swaps `adapter->xdp_prog`, puts the old BPF program after ring update/reset, and uses RCU synchronization when removing XDP so wakeup paths stop seeing stale state. Ring stats use `u64_stats_sync`; ring arrays are read under RCU in `ixgbe_get_stats64()`. Device disable is guarded by `test_and_set_bit(__IXGBE_DISABLED)` so PCI disable happens once across probe errors, remove, and AER.

This chunk also persists user-visible configuration into kernel objects: `netdev->features`, `hw_features`, `vlan_features`, `hw_enc_features`, `mpls_features`, `xdp_features`, `min_mtu/max_mtu`, `dcbnl_ops`, `devlink_port`, `udp_tunnel_nic_info`, bridge mode, subordinate-channel assignments, and SAN MAC address entries.

## Dependencies and Integration Points

The chunk depends on Linux networking core APIs (`net_device_ops`, skb helpers, VLAN helpers, MDIO/MII ioctl, TC setup, `flow_block_cb_setup_simple`, macvlan acceleration, bridge link netlink, rtnl locks, NAPI, RCU, XDP/AF_XDP, u64 stats), PCI APIs (`pci_driver`, BAR reservation, DMA masks, AER handlers, SR-IOV, FLR, wake from D3), devlink APIs, DCB, DCA, HWMON, IPsec/XFRM offload, FCoE, PTP hardware timestamping, and ethtool Flow Director infrastructure.

Internal ixgbe dependencies include hardware operation tables from `ixgbe_info_tbl`, register macros (`IXGBE_READ_REG`, `IXGBE_WRITE_REG`, `IXGBE_TXDCTL`, `IXGBE_RXDCTL`, `IXGBE_VMD_CTL`, etc.), ring helpers (`ixgbe_configure_*_ring`, `ixgbe_clean_*_ring`, `ixgbe_maybe_stop_tx`, `ixgbe_tx_map`), reset/open/close helpers, SR-IOV helpers, devlink helpers, debug/fwlog helpers, Flow Director helpers, XSK pool/wakeup helpers, and hardware model data such as `ixgbe_ipv4_jumps`.

Compile-time gates substantially change behavior: `IXGBE_FCOE`, `CONFIG_IXGBE_IPSEC`, `CONFIG_IXGBE_DCB`, `CONFIG_NET_CLS_ACT`, `CONFIG_PCI_IOV`, `CONFIG_IXGBE_DCA`, and `CONFIG_IXGBE_HWMON` each add or remove callbacks, state transitions, features, or teardown duties.

## Risks and Edge Cases

- TX descriptor accounting must match actual fragmentation. Underestimating descriptors can corrupt ring state; overconservative budgeting can cause unnecessary `NETDEV_TX_BUSY`.
- The XDP DMA error unwind walks backward from the current descriptor index and uses `dma_unmap_page()` even though mapping used `dma_map_single()`. This matches the local code pattern only if the DMA unmap metadata abstraction intentionally tolerates it; it is a point to verify against surrounding ixgbe cleanup helpers.
- `ixgbe_configure_clsu32()` returns `0` after attempting to build a jump link even when no `nexthdr` entry matched and temporary allocations may have been freed inside the loop. The behavior may be intentional "unsupported link ignored" semantics, but it is a fragile area for offload correctness.
- `ixgbe_configure_clsu32()` uses `loc - 1` for child location maps when `uhtid != 0x800`; a `loc` of zero in child tables would underflow the bitmap index unless rejected by tc handle constraints elsewhere.
- Flow Director perfect filters require one global mask while filters exist. Users can see `-EINVAL` for valid-looking tc rules if their masks differ from the first installed rule.
- XDP is mutually exclusive with SR-IOV, DCB, RSC/LRO, and some L2 forwarding paths in this chunk. Feature toggles can force disruptive `ixgbe_setup_tc()` resets.
- L2 forwarding offload allocation has a potential leak path: `ixgbe_fwd_add()` allocates `accel`, sets pool/subordinate state, and if `ixgbe_fwd_ring_up()` fails returns `ERR_PTR(err)` without freeing `accel` or clearing the bit in this local chunk.
- Probe error unwind is order-sensitive. Any new resource added after `register_netdev()` or `devl_lock()` must be released in the right label and lock state; otherwise remove/probe failure paths diverge.
- E610 recovery probe intentionally registers devlink with limited initialization and returns success without full netdev registration. Callers and removal paths must tolerate partially initialized adapters.
- PCI AER VF detection assumes root-port AER log availability and decodes requestor ID fields differently for old devices. If detection succeeds, normal PF detach/reset is skipped and `vferr_refcount` gates resume.
- `ixgbe_disable_rxr_hw()` skips RXDCTL polling on 82598 with link down because hardware may not clear the bit; this is a hardware-specific quiesce exception that tests should cover.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage across the compile-time matrix, especially with and without `CONFIG_PCI_IOV`, `CONFIG_IXGBE_DCB`, `CONFIG_NET_CLS_ACT`, `CONFIG_IXGBE_IPSEC`, `IXGBE_FCOE`, `CONFIG_IXGBE_DCA`, and `CONFIG_IXGBE_HWMON`.
- Netdev TX smoke tests with VLAN hardware tags, software VLAN headers, DCB priority mappings, TSO/checksum offload, SCTP CRC, UDP GSO, IPsec offload, FCoE offload, and PTP TX timestamp requests.
- XDP attach/detach tests that verify rejection under SR-IOV/DCB/RSC, AF_XDP pool setup and wakeup, `.ndo_xdp_xmit` with and without `XDP_XMIT_FLUSH`, invalid flag rejection, and ring disabled/down-device returns.
- TC tests for mqprio traffic classes, `tc u32` add/replace/delete hnode/knode, unsupported non-IPv4 protocols, mismatched masks, drop actions, redirect to VF, redirect to offloaded macvlan, chain rejection, and duplicate child locations.
- Feature-toggle tests via ethtool/netlink for LRO/RSC, RXCSUM, NTUPLE, HW_TC, RXALL, VLAN RX/filtering, and HW_L2FW_DOFFLOAD, watching whether reset or rx-mode update paths are triggered.
- SR-IOV and bridge-mode tests for VEPA/VEB programming, VF stats, VF configuration during probe, and bad-VF AER recovery if hardware or fault injection permits.
- Probe/remove fault injection at allocation, BAR map, `ixgbe_sw_init`, firmware recovery, EEPROM validation, interrupt init, netdev registration, MII bus init, devlink registration, and fwlog init boundaries.
- Suspend/resume and PCI AER tests that confirm `__IXGBE_DISABLED` transitions, netdev detach/attach, close/open pairing, and no double PCI disable.
- Runtime leak checks around macvlan `ndo_dfwd_add_station` failure after `ixgbe_fwd_ring_up()` and around tc jump-table allocation failures.
