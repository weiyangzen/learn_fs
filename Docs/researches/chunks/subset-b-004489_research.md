# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_main.c lines 9557-10314

## Chunk Scope

This chunk covers the tail of the Intel `igb` PCI Ethernet driver's main source file. It begins inside `igb_deliver_wake_packet()` and then defines suspend/resume, runtime PM, shutdown, SR-IOV configuration, PCI AER recovery, VF administrative netdev operations, VMDq/SR-IOV receive-address programming, DMA coalescing setup, I2C byte accessors, queue reinitialization, NFC filter replay helpers, PM operations, and the final `struct pci_driver` registration record.

The immediately preceding context is `__igb_shutdown()`, which tears the device down for suspend/runtime suspend/shutdown: it detaches the netdev, closes a running interface, suspends PTP, clears interrupt resources, programs wake filters, controls PHY power, releases firmware ownership, and disables the PCI function. This chunk supplies the matching resume and registration-side callbacks that make that shutdown path reachable.

## Purpose and Responsibilities

- Deliver a captured wake packet from the controller wake-up packet memory into the network stack after resume.
- Restore a suspended or runtime-suspended NIC to D0, re-enable PCI memory access, rebuild interrupts/queues, reset hardware, reclaim firmware ownership, reopen a running netdev, and reattach the device.
- Provide runtime PM policy: schedule suspend after a link-loss idle interval but return `-EBUSY` so runtime PM only acts when explicitly scheduled.
- Handle final system shutdown and power-off wake state programming.
- Expose PCI SR-IOV sysfs configuration through `igb_enable_sriov()` and `igb_disable_sriov()`.
- Implement PCI error recovery callbacks for AER: detach and stop traffic, request slot reset, reinitialize MMIO state, and resume traffic.
- Back the PF netdev VF controls for setting VF MACs, VF max TX rates, spoof checking, trust state, and reading VF configuration.
- Program receive address registers from the driver's MAC table, including VF queue/pool steering bits and source-address filtering flags.
- Configure VMDq replication, loopback, and anti-spoofing for SR-IOV-capable devices.
- Configure DMA coalescing and related PCIe low-power transition controls on supported MAC generations.
- Provide shared-code I2C byte read/write hooks over the driver's bit-banged I2C adapter with SW/FW synchronization.
- Reinitialize queue and interrupt resources after channel-count changes.
- Remove and restore network flow classification filters around device down/up.
- Bind all of the above into Linux PM, PCI error, shutdown, SR-IOV, and PCI driver registration structures.

## Important APIs, Types, and Functions

- `igb_deliver_wake_packet(struct net_device *netdev)`: reads `E1000_WUPL` and `E1000_WUPM_REG()` memory, builds an aligned `sk_buff`, assigns protocol with `eth_type_trans()`, and submits it with `netif_rx()`.
- `igb_suspend()`, `igb_resume()`, `igb_runtime_suspend()`, `igb_runtime_resume()`, and `igb_runtime_idle()`: PM callbacks assembled into `_DEFINE_DEV_PM_OPS(igb_pm_ops, ...)`.
- `__igb_resume(struct device *dev, bool rpm)`: shared resume implementation for system and runtime PM. The `rpm` flag controls RTNL handling because runtime PM callers are expected to be in a context that does not use the same outer lock path.
- `igb_shutdown(struct pci_dev *pdev)`: final PCI shutdown callback. It calls `__igb_shutdown()` and, on `SYSTEM_POWER_OFF`, arms wake-from-D3 and enters `PCI_D3hot`.
- `igb_pci_sriov_configure(struct pci_dev *dev, int num_vfs)`: PCI core SR-IOV configure hook, compiled around `CONFIG_PCI_IOV`.
- `igb_io_error_detected()`, `igb_io_slot_reset()`, and `igb_io_resume()`: `struct pci_error_handlers` implementation referenced by `igb_err_handler`.
- `igb_rar_set_index(struct igb_adapter *adapter, u32 index)`: synchronizes one software `adapter->mac_table[]` entry into `E1000_RAL()`/`E1000_RAH()` hardware receive address registers.
- `igb_set_vf_mac()` and `igb_ndo_set_vf_mac()`: update VF MAC state in `adapter->vf_data[]`, the software MAC table, and the hardware RAR entry reserved from the top of the RAR table.
- `igb_link_mbps()`, `igb_set_vf_rate_limit()`, `igb_check_vf_rate_limit()`, and `igb_ndo_set_vf_bw()`: translate link speed to Mbps and program per-VF max TX rate limits through `E1000_RTTDQSEL`, `E1000_RTTBCNRM`, and `E1000_RTTBCNRC`.
- `igb_ndo_set_vf_spoofchk()`, `igb_ndo_set_vf_trust()`, and `igb_ndo_get_vf_config()`: netdev SR-IOV administrative callbacks stored in `igb_netdev_ops`.
- `igb_vmm_control(struct igb_adapter *adapter)`: configures VMDq/SR-IOV replication behavior, loopback, and anti-spoofing based on MAC type and VF allocation count.
- `igb_init_dmac(struct igb_adapter *adapter, u32 pba)`: initializes DMA coalescing register thresholds and PCIe low-power decision behavior after reset.
- `igb_read_i2c_byte()` and `igb_write_i2c_byte()`: shared-code hooks that use `adapter->i2c_client` and SMBus byte transfers while holding `E1000_SWFW_PHY0_SM` software/firmware synchronization.
- `igb_reinit_queues(struct igb_adapter *adapter)`: exported within the driver via `igb.h` and used by ethtool channel reconfiguration.
- `igb_nfc_filter_exit()` and `igb_nfc_filter_restore()`: erase and replay NFC filters from `adapter->nfc_filter_list` and `adapter->cls_flower_list`.
- `igb_driver`: the final `struct pci_driver` tying together PCI ID matching, probe/remove, PM ops, shutdown, SR-IOV configure, and PCI error handling.

Key data structures are `struct igb_adapter`, `struct e1000_hw`, `struct vf_data_storage`, `struct igb_mac_addr`, `struct igb_nfc_filter`, `struct ifla_vf_info`, `struct net_device`, and `struct pci_dev`. The relevant persistent fields include `adapter->state`, `adapter->flags`, `adapter->wol`, `adapter->en_mng_pt`, `adapter->io_addr`, `adapter->vfs_allocated_count`, `adapter->vf_data[]`, `adapter->vf_rate_link_speed`, `adapter->link_speed`, `adapter->mac_table[]`, `adapter->i2c_client`, `adapter->nfc_filter_list`, `adapter->cls_flower_list`, and `adapter->nfc_lock`.

## Control Flow and State Machines

### Wake Packet Delivery

After `__igb_resume()` resets hardware and reclaims driver ownership, it reads `E1000_WUS`. If `WAKE_PKT_WUS` is set, it calls `igb_deliver_wake_packet()`. The helper reads the hardware wake packet length from `E1000_WUPL`, rejects zero or larger-than-buffer lengths because WUPM stores only the first `E1000_WUPM_BYTES`, allocates an skb sized to the WUPM buffer, advances the skb length by the real packet length, rounds the MMIO copy length up to a 32-bit boundary, copies from wake packet memory, derives the protocol, and injects the packet through `netif_rx()`. This makes a wake-triggering packet visible to the host networking stack after resume when the device captured a complete packet.

### System and Runtime Resume

`__igb_resume()` is the central resume state machine. It moves the PCI function to `PCI_D0`, restores PCI config state, verifies presence, enables memory BAR decoding, sets bus mastership, disables PCI wake from D3 states, allocates interrupt/queue resources with `igb_init_interrupt_scheme(adapter, true)`, and calls `igb_reset(adapter)`. It then calls `igb_get_hw_control()` so firmware knows the OS driver owns the hardware again.

Wake status is handled before reopening the interface: a wake packet is delivered if present, and then `E1000_WUS` is cleared with all ones. For normal system resume, the function takes RTNL before checking `netif_running()` and calling `__igb_open(netdev, true)`. For runtime resume, it skips this explicit RTNL lock because runtime PM call paths already differ from full system PM locking expectations. If reopen succeeds, `netif_device_attach()` marks the netdev usable again.

Important failure exits are early and leave the device detached or not reopened: missing PCI device returns `-ENODEV`; failed `pci_enable_device_mem()` returns that error; failed interrupt-scheme allocation returns `-ENOMEM`. The interrupt allocation failure path occurs after the PCI device has been enabled, so caller-side PM/error recovery cleanup must account for partial resume.

### Runtime PM and Shutdown

`igb_runtime_idle()` checks link state with `igb_has_link()`. If no link is present, it schedules runtime suspend five seconds later using `pm_schedule_suspend(dev, MSEC_PER_SEC * 5)`, but always returns `-EBUSY`. That pattern keeps the PM core from immediately suspending during idle notification while still allowing the delayed suspend request to run.

`igb_runtime_suspend()` reuses `__igb_shutdown()` with `runtime=true`, which narrows wake filtering to link-change wake (`E1000_WUFC_LNKC`) instead of the full user-configured WoL mask. `igb_suspend()` and `igb_shutdown()` use the non-runtime path. During final power-off, `igb_shutdown()` also calls `pci_wake_from_d3(pdev, wake)` and sets `PCI_D3hot` if the system is powering off.

### PCI Error Recovery

`igb_io_error_detected()` is the first PCI AER callback. A `pci_channel_io_normal` event is treated as a recoverable non-fatal report without device teardown. For frozen or reset-needed channels, the netdev is detached, permanent failure returns `PCI_ERS_RESULT_DISCONNECT`, and otherwise RTNL protects `igb_down(adapter)` for a running interface before the PCI function is disabled and `PCI_ERS_RESULT_NEED_RESET` requests slot reset.

`igb_io_slot_reset()` re-enables memory BAR access, restores PCI state, disables D3 wake, reassigns `hw->hw_addr = adapter->io_addr` because PCI reset may invalidate the hardware address pointer used by register accessors, resets hardware, clears wake status, and reports `PCI_ERS_RESULT_RECOVERED`. If `pci_enable_device_mem()` fails, recovery reports disconnect.

`igb_io_resume()` is the second half of recovery. Under RTNL, it checks whether the netdev is running. If the adapter is not marked `__IGB_DOWN`, recovery is from a non-fatal error and no queue restart is needed. Otherwise it calls `igb_up(adapter)` to configure hardware, enable NAPI/interrupts, start queues, notify VFs of PF reset completion, and reschedule the watchdog. On success it attaches the netdev and calls `igb_get_hw_control()`.

### SR-IOV and VF Administration

`igb_pci_sriov_configure()` handles PCI sysfs VF count changes. With `CONFIG_PCI_IOV`, a request for zero VFs disables SR-IOV with `igb_disable_sriov(dev, true)`, while a positive count tries `igb_enable_sriov(dev, num_vfs, true)` and returns either the requested VF count or the error. Without PCI IOV support it returns zero.

The VF netdev callbacks rely on `adapter->vfs_allocated_count` bounds checks and `adapter->vf_data[]` persistence. `igb_ndo_set_vf_mac()` accepts either a zero MAC to clear `IGB_VF_FLAG_PF_SET_MAC` or a valid unicast MAC to set that flag and log that the VF driver must reload. It also warns when the PF is down. In both accepted cases it calls `igb_set_vf_mac()`, which stores the address in VF state, mirrors it to the RAR entry at `hw->mac.rar_entry_count - (vf + 1)`, associates the entry with the VF queue, marks it in use, and writes the hardware RAR registers.

`igb_ndo_set_vf_bw()` supports max TX rate limiting only on `e1000_82576` and rejects nonzero min rates. It requires the VF index to be valid, link to be up, and `max_tx_rate` to be between zero and the current link speed in Mbps. Successful calls set `adapter->vf_rate_link_speed`, store `vf_data[vf].tx_rate`, and program the hardware rate factor. `igb_check_vf_rate_limit()` is called when link comes up in the watchdog path; if the actual link speed changed from the speed used when limits were set, it clears all VF TX rate state and disables hardware limits.

`igb_ndo_set_vf_spoofchk()` writes MAC/VLAN spoofing bits in `E1000_DTXSWC` for 82576 or `E1000_TXSWC` for other supported devices, then persists `vf_data[vf].spoofchk_enabled`. `igb_ndo_set_vf_trust()` updates only the software trusted flag and logs the change; enforcement is consumed by other VF mailbox paths that check `vf_data[vf].trusted`. `igb_ndo_get_vf_config()` reports MAC, TX rate, PF VLAN/QoS, spoof-check, and trust state through `struct ifla_vf_info`.

### Receive Address Register Programming

`igb_rar_set_index()` converts the six-byte MAC address in `adapter->mac_table[index].addr` into little-endian register values, then conditionally adds hardware-valid, source-address, queue-steering, and pool bits based on the entry state. The RAR pool encoding differs by MAC type: `e1000_82575` and `e1000_i210` use multiplication by `E1000_RAH_POOL_1`, while other devices shift `E1000_RAH_POOL_1` by the queue index. The helper writes `E1000_RAL(index)` and `E1000_RAH(index)` with flushes between writes.

This helper is the low-level bridge between software MAC-table intent and hardware unicast filtering. Other parts of the file call similar MAC-table code for the PF default MAC, unicast list sync, MAC steering filters, and VF reset/configuration.

### VMDq, DMA Coalescing, I2C, and Filters

`igb_vmm_control()` is called during RX multi-queue control setup before `E1000_MRQC` is written. Unsupported or non-replicating MACs return early. For 82576 it marks VLAN tags as added by the MAC in `E1000_DTXCTL`; for 82576 and 82580 it enables replicated VLAN stripping in `E1000_RPLOLR`; i350 falls through to the common VMDq controls. With allocated VFs, it enables PF loopback, replication, and anti-spoofing for the VF count. Without VFs, it disables loopback and replication.

`igb_init_dmac()` is invoked from `igb_reset()` after hardware initialization. On MACs newer than 82580 and when `IGB_FLAG_DMAC` is enabled, it programs DMA coalescing thresholds using the packet buffer allocation (`pba`), `adapter->max_frame_size`, and fixed timing/flush constants. It also configures PCIe low-power transition decisions via `E1000_PCIEMISC_LX_DECISION` for i210-or-newer devices or when DMAC is enabled. For 82580 it explicitly clears LX decision and disables `E1000_DMACR`.

`igb_read_i2c_byte()` and `igb_write_i2c_byte()` are global symbols used by the Intel shared-code hardware operation tables. They require `adapter->i2c_client`, acquire the SW/FW PHY semaphore (`E1000_SWFW_PHY0_SM`) through `hw->mac.ops.acquire_swfw_sync()`, issue SMBus byte read/write operations, release the semaphore, and translate Linux I2C failures to `E1000_ERR_I2C` or semaphore failures to `E1000_ERR_SWFW_SYNC`. The `dev_addr` parameter is present for the shared-code API but not used because the Linux `i2c_client` already encodes the target device address.

`igb_reinit_queues()` closes a running netdev, resets interrupt capability, allocates a new interrupt scheme, and reopens the device if it was running. It is used by ethtool channel configuration after `adapter->rss_queues` changes. `igb_nfc_filter_exit()` erases programmed filters from both the ethtool NFC list and the tc flower list under `adapter->nfc_lock`; `igb_nfc_filter_restore()` replays only `nfc_filter_list` under the same lock during `igb_configure()`. Flower filter replay is not done here, which implies cls_flower rules either have a separate restore path or are intentionally removed from hardware on down.

## State and Persistence Behavior

- Hardware wake state lives in `E1000_WUS`, `E1000_WUPL`, WUPM memory, `E1000_WUC`, and `E1000_WUFC`; software wake policy comes from `adapter->wol`, runtime mode, and `adapter->en_mng_pt`.
- Device PM state spans PCI power state/config space, PCI wake flags, driver-owned MMIO register state, interrupt scheme allocations, queue resources, and `netif_device_detach()`/`netif_device_attach()` visibility to the network stack.
- `adapter->state` includes `__IGB_DOWN`, which determines whether PCI error resume must call `igb_up()` and whether VF MAC warnings should tell the operator to bring the PF up.
- VF administrative state persists in `adapter->vf_data[]`: MAC address, PF-set-MAC flag, max TX rate, PF VLAN/QoS, spoof-check enable, and trust. Rate limiting also stores the link speed used for the programmed hardware factors in `adapter->vf_rate_link_speed`.
- `adapter->mac_table[]` is the source of truth for receive address register entries. This chunk writes one entry to hardware but does not allocate or free the table; allocation happens during software init and reset paths clear/rebuild hardware from it.
- NFC filter software lists persist across down/up. The hardware side is erased on `igb_down()` and replayed from `nfc_filter_list` during `igb_configure()`.
- I2C state is persisted in `adapter->i2c_adap`, `adapter->i2c_algo`, and `adapter->i2c_client`, initialized at probe for i350-class hardware and removed during driver remove.
- The final `igb_driver` structure is static module state and is registered/unregistered by the file's module init/exit functions earlier in the file.

## Dependencies and Integration Points

- Linux PCI core: `struct pci_driver`, `pci_set_power_state()`, `pci_restore_state()`, `pci_enable_device_mem()`, `pci_set_master()`, `pci_enable_wake()`, `pci_wake_from_d3()`, `pci_disable_device()`, SR-IOV configure callbacks, and AER `struct pci_error_handlers`.
- Linux PM core: `_DEFINE_DEV_PM_OPS`, system suspend/resume, runtime suspend/resume/idle, `pm_schedule_suspend()`, and wakeup capability configured during probe.
- Linux netdev core: `netif_device_detach()/attach()`, `netif_running()`, `__igb_open()`, `igb_close()/igb_open()`, `igb_up()/igb_down()`, `netif_rx()`, `sk_buff` allocation, `eth_type_trans()`, RTNL locking, and `net_device_ops` VF callbacks.
- Intel shared hardware layer: `struct e1000_hw`, `hw->mac.type`, `hw->mac.rar_entry_count`, `hw->mac.ops.acquire_swfw_sync()`, `hw->mac.ops.release_swfw_sync()`, register access macros `rd32()`, `wr32()`, `wrfl()`, and many `E1000_*` register/bit definitions.
- SR-IOV/VMDq support: `igb_enable_sriov()`, `igb_disable_sriov()`, `adapter->vf_data`, VF mailbox/reset paths, VMDq loopback/replication/anti-spoof helpers, and netlink VF administration.
- Ettool and channel configuration: `igb_reinit_queues()` is declared in `igb.h` and called from `igb_ethtool.c` when the combined channel count changes.
- Flow classification: `igb_add_filter()` and `igb_erase_filter()` live in the ethtool/filter support code and are invoked here for down/up hardware synchronization.
- I2C subsystem: `i2c_smbus_read_byte_data()`, `i2c_smbus_write_byte_data()`, and the i350 bit-banged I2C bus initialized earlier in this file.
- PTP and firmware ownership: resume and error recovery call `igb_get_hw_control()`, while the preceding shutdown path calls `igb_ptp_suspend()` and `igb_release_hw_control()`.

## Risks and Edge Cases

- `igb_deliver_wake_packet()` rounds the copy length up to a 32-bit boundary after setting the skb length to the unrounded packet length. This is intentional for MMIO alignment, but it writes up to three bytes beyond `skb->len` inside the allocated WUPM-sized data area. Any future buffer-size change must preserve that headroom.
- Resume error handling after `igb_init_interrupt_scheme()` failure returns without disabling the PCI function or clearing partial allocations in this function. Correctness depends on caller recovery paths and the interrupt scheme helper's own cleanup behavior.
- `__igb_resume()` uses `u32 err` even though it stores negative Linux errno values such as `-ENOMEM`; returning it as `int` works by conversion but is stylistically risky and can obscure signedness bugs.
- Runtime resume skips RTNL while system resume takes it. Any future changes to `__igb_open()` or attach sequencing need to preserve the locking assumptions for both PM paths.
- `igb_ndo_set_vf_mac()` validates only `vf >= adapter->vfs_allocated_count`, not negative `vf`. Netdev callers normally supply validated VF indices, but the local check alone would not reject negative indexes before indexing `adapter->vf_data[vf]`.
- VF rate limiting divides by `tx_rate` only when nonzero and bounds `max_tx_rate` against current link speed. It also depends on `igb_link_mbps()` returning nonzero; unsupported or stale speeds make otherwise valid requests fail.
- Per-VF rate programming is 82576-only. Link speed changes disable all VF TX rates, so tests should expect user-configured max rates to be lost after speed transition.
- `igb_ndo_set_vf_spoofchk()` chooses `E1000_TXSWC` for every non-82576 MAC once VFs exist. The hardware support matrix must match the earlier SR-IOV enable paths so unsupported MACs cannot reach this register programming.
- `igb_ndo_set_vf_trust()` persists a software flag but does not program hardware directly in this chunk. Enforcement depends on mailbox and filter paths respecting the trusted flag consistently.
- `igb_nfc_filter_exit()` erases both ethtool NFC and cls_flower lists, while `igb_nfc_filter_restore()` re-adds only ethtool NFC filters. This asymmetry deserves review with the tc flower offload path to ensure flower filters are not silently absent after down/up.
- PCI AER recovery manually restores `hw->hw_addr` from `adapter->io_addr`; any future MMIO remap or BAR handling change must keep these pointers coherent before `rd32()`/`wr32()` are used.
- `igb_init_dmac()` computes thresholds from `pba`, `IGB_MIN_TXPBSIZE`, `IGB_TX_BUF_4096`, and `adapter->max_frame_size`. Jumbo MTU or unusual PBA settings should be validated so threshold arithmetic does not underflow or program nonsensical coalescing values.
- I2C read/write ignore `dev_addr`; if the shared code ever expects dynamic target addresses, this wrapper would need to select or instantiate the correct `i2c_client`.

## Test Signals and Validation Ideas

- Suspend/resume: put the interface up, suspend/resume the system, and verify PCI D0 restoration, interrupt allocation, `igb_reset()`, queue reopen, carrier recovery, and absence of leaked/doubled interrupts.
- Wake-on-LAN: enable different WoL modes, suspend, wake by magic/multicast/link where supported, and verify `E1000_WUS` clears and captured wake packets are injected only when `E1000_WUPL` is within `E1000_WUPM_BYTES`.
- Runtime PM: drop link, confirm delayed runtime suspend is scheduled, then restore link and verify runtime resume reopens/reattaches without RTNL warnings or deadlocks.
- Shutdown/poweroff: power off with WoL enabled and disabled and verify D3 wake behavior and PHY power state match `wake = wufc || adapter->en_mng_pt`.
- PCI AER: inject normal, frozen, and permanent-failure channel states. Expected signals are detach/down/disable on frozen errors, slot reset re-enabling MMIO and clearing `E1000_WUS`, and `igb_up()` plus `netif_device_attach()` on resume.
- SR-IOV sysfs: create and remove VFs through PCI sysfs with `CONFIG_PCI_IOV`, verify return counts/errors, and exercise the zero-VF disable path.
- VF MACs: set a valid VF MAC, clear it with all zeros, try invalid addresses, test while PF is down, and confirm RAR entries and `IGB_VF_FLAG_PF_SET_MAC` behavior.
- VF rates: on 82576 with link up, set max TX rates of zero, a valid sub-link rate, and values above link speed; then change link speed and confirm rates are disabled and `vf_data[].tx_rate` clears.
- VF spoof/trust/config: toggle spoof checking and trust through `ip link`, then verify register bits, `ifla_vf_info` output, and behavior of VF MAC/VLAN changes.
- VMDq/SR-IOV receive behavior: test 82576, 82580, and i350-class hardware or emulation for VLAN replication, PF loopback, anti-spoofing, and VF receive path after reset.
- DMA coalescing: test supported MACs with DMAC enabled/disabled, i210-or-newer LX decision behavior, 82580 disable path, jumbo MTUs, and power-latency impact.
- I2C: on i350 hardware with an external I2C target, verify byte reads/writes, semaphore failure handling, missing-client failure, and concurrent PHY/shared-code access.
- Queue reinit: change ethtool channel count while the interface is up and down, ensuring queues/interrupts are rebuilt and traffic resumes; fault-inject interrupt allocation failures.
- NFC filters: add ethtool ntuple and tc flower filters, bring the interface down/up or reset it, and verify which filters are erased, restored, or require replay through a separate path.
