# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_main.c

## Purpose

`lio_main.c` is the primary LiquidIO PF network driver module. It registers the PCI driver, probes and initializes Octeon adapters, loads or coordinates firmware, creates Linux netdevs, owns netdev operations, implements TX, link and feature handling, manages SR-IOV PF policy, devlink switchdev mode, PTP timestamping, watchdog behavior, and full teardown. It is compiled into `liquidio.o` with the Octeon console and VF representor support.

## Important APIs, Types, and Functions

- Module parameters: `ddr_timeout`, `debug`, `fw_type`, and `console_bitmask` configure boot wait, netif logging, firmware source/type, and debug console forwarding.
- `struct handshake` and global `handshake[]` / `first_stage` coordinate asynchronous PCI probe, firmware startup, and module init completion across multiple Octeon devices.
- PCI/module entry points: `liquidio_init()`, `liquidio_exit()`, `liquidio_probe()`, `liquidio_remove()`, `liquidio_init_pci()`, and `liquidio_deinit_pci()`.
- PCI AER callbacks: `liquidio_pcie_error_detected()`, `liquidio_pcie_mmio_enabled()`, `liquidio_pcie_slot_reset()`, and `liquidio_pcie_resume()`.
- Device lifecycle helpers: `octeon_device_init()`, `octeon_chip_specific_setup()`, `octeon_pci_os_setup()`, `octeon_destroy_resources()`, `load_firmware()`, and `nic_starter()`.
- Netdev operations: `liquidio_open()`, `liquidio_stop()`, `liquidio_xmit()`, `liquidio_get_stats64()`, `liquidio_set_mac()`, `liquidio_set_mcast_list()`, `liquidio_tx_timeout()`, VLAN add/delete, feature fix/set, hardware timestamp get/set, and VF control callbacks.
- RX/link support: `lio_nic_info()`, `update_link_status()`, `setup_link_status_change_wq()`, and delayed MTU correction.
- TX support: `free_netbuf()`, `free_netsgbuf()`, `free_netsgbuf_with_resp()`, `send_nic_timestamp_pkt()`, `handle_timestamp()`, and `check_txq_status()`.
- PTP support: `liquidio_ptp_adjfine()`, `liquidio_ptp_adjtime()`, `liquidio_ptp_gettime()`, `liquidio_ptp_settime()`, `oct_ptp_open()`, and `liquidio_ptp_init()`.
- SR-IOV/devlink support: `liquidio_enable_sriov()`, `octeon_enable_sriov()`, `lio_pci_sriov_disable()`, VF MAC/VLAN/spoof/trust/link-state/stats callbacks, `liquidio_eswitch_mode_get()`, `liquidio_eswitch_mode_set()`, and VF representor creation/destruction.
- Watchdog support: `liquidio_watchdog()` monitors CN23XX crash/stuck-core scratch status, disables VF links, and manages module references associated with loaded VFs.

## Control Flow

Module load begins in `liquidio_init()`, which initializes the Octeon device list, registers the PCI driver, waits for first probe, then waits for each probed device to complete `init` and `started` handshakes. `liquidio_probe()` allocates an `octeon_device`, records PCI data, initializes per-device handshakes, calls `octeon_device_init()`, starts the CN23XX PF watchdog for the first PF of an adapter, and sets default pause state.

`octeon_device_init()` is the hardware/firmware bring-up state machine. It enables PCI and DMA, maps chip-specific BAR/register support, registers the device, determines whether firmware is preloaded or must be loaded, initializes dispatch and response infrastructure, creates IQ/DROQ structures, sets up PF mailbox and I/O vectors, installs interrupts, credits and enables queues, optionally waits for DDR/bootloader and downloads firmware, completes the init handshake, and transitions to `OCT_DEV_HOST_OK`. The delayed `nic_starter()` polls until firmware reports `OCT_DEV_CORE_OK`, transitions to `OCT_DEV_RUNNING`, and initializes the NIC module if `oct->app_mode == CVM_DRV_NIC_APP`.

`liquidio_init_nic_module()` determines the configured number of NIC ports, initializes `oct->props`, calls `setup_nic_devices()`, optionally initializes VF representor support, and initializes PTP hardware. `setup_nic_devices()` registers firmware dispatch/free callbacks, sends `OPCODE_NIC_IF_CFG` per interface, validates firmware version and queue masks, allocates a multi-queue netdev, fills `struct lio`, programs queue counts and capabilities, assigns random VF MACs, sets up I/O queues and gather lists, installs ethtool ops, enables default firmware features, creates link/time/RX-OOM workqueues, registers the netdev, enables checksum commands, and caches speed/FEC boot state.

Netdev open enables NAPI, opens PTP if supported, sets `LIO_IFSTATE_RUNNING`, starts TX queue polling when needed, starts all TX queues, marks the interface open for link updates, sends firmware RX enable, and schedules periodic stats fetch. Netdev stop clears running state, disables carrier/TX, sends firmware RX disable, tears down TX polling and stats work, unregisters PTP, waits for RX drain, disables NAPI, restores tasklet processing, and records link-down state.

Transmit starts in `liquidio_xmit()`. The function chooses an IQ from SKB queue mapping, rejects packets when the interface is down or link is down, prepares `skb->cb` free metadata, checks IQ fullness, builds either a single-buffer DMA command or a gather-list DMA command, sets checksum/tunnel/timestamp/GSO/VLAN metadata, sends a timestamped or normal NIC data packet, stops the subqueue on `IQ_SEND_STOP`, updates stats, and relies on the request-type free callbacks to unmap DMA and free SKBs after completion. Failure paths unmap the current single DMA pointer when present, ring the IQ doorbell, update drops, and free the SKB.

Teardown runs through `liquidio_remove()`, `liquidio_stop_nic_module()`, `liquidio_destroy_nic_device()`, and `octeon_destroy_resources()`. The cleanup state machine falls through by `oct->status`, disabling queues and interrupts, draining requests, freeing IRQs/MSI-X, freeing mailbox/vector/sc/list/queue resources, disabling SR-IOV, unregistering the Octeon device, performing FLR or soft reset, unmapping BARs, disabling PCI, and killing tasklets.

## State and Persistence Behavior

Driver state is mostly in-memory and hardware/firmware-backed. `oct->status` is the core lifecycle cursor, with values such as `OCT_DEV_BEGIN_STATE`, `OCT_DEV_PCI_ENABLE_DONE`, `OCT_DEV_DROQ_INIT_DONE`, `OCT_DEV_INTR_SET_DONE`, `OCT_DEV_IO_QUEUES_DONE`, `OCT_DEV_HOST_OK`, `OCT_DEV_CORE_OK`, `OCT_DEV_RUNNING`, and `OCT_DEV_IN_RESET`. The teardown path depends on this cursor to decide what resources were initialized.

Per-netdev state lives in `struct lio`: interface index, `linfo`, queue IDs, queue sizes, netdev pointer, Octeon pointer, feature capabilities, logging level, workqueue contexts, PTP clock state, timestamp adjustment, link-change count, and ifstate bits. Per-device state lives in `struct octeon_device`: PCI device, chip ID, firmware/app mode, firmware version, queue masks, properties, SR-IOV state, devlink, pause settings, speed/FEC settings, watchdog state, and function-table callbacks.

Firmware/hardware-backed state includes loaded firmware, app mode, interface queue allocation, MAC/VLAN/spoof/trust/link-state policy for VFs, RX forwarding state, link status, MTU, checksum/LRO/VLAN filter/tunnel settings, PTP clock registers, interrupt thresholds, and CSR state. There is no filesystem persistence except firmware files requested from the kernel firmware loader.

Handshake state persists only during module initialization. The first successful `octeon_device_init()` completion marks `init_ok`; `nic_starter()` marks `started_ok` only after firmware reaches NIC app mode and netdev setup succeeds. Failure paths complete pending handshakes during resource destruction to avoid module-init deadlock.

## Dependencies and Integration Points

The file integrates the Linux PCI driver model, firmware loader, netdev API, ethtool assignment, NAPI/tasklets, DMA mapping, PTP clock API, hardware timestamp API, UDP tunnel offload API, devlink eswitch API, SR-IOV PCI APIs, module refcount APIs, and PCI AER callbacks. It depends heavily on LiquidIO internal modules for Octeon queue management, response management, console access, firmware download, chip-specific setup for CN66XX/CN68XX/CN23XX PFs, and VF representors.

It calls core exports from `lio_core.c` for queue setup, interrupt setup, feature commands, MTU changes, stats polling, RX drain wait, gather-list management, RX OOM workqueues, speed, and FEC. It calls `liquidio_set_ethtool_ops()` from `lio_ethtool.c` during netdev creation. Firmware dispatch callbacks connect incoming `OPCODE_NIC_INFO`, `OPCODE_NIC_CORE_DRV_ACTIVE`, and `OPCODE_NIC_VF_DRV_NOTICE` messages back into driver state.

## Risks and Edge Cases

- The resource lifecycle is status-driven and order-sensitive. Missing a status update or returning after partial initialization can leak resources or make `octeon_destroy_resources()` skip required cleanup.
- `liquidio_xmit()` has complex DMA and gather-list ownership. Some SG failure paths return `NETDEV_TX_BUSY` after taking a gather entry or mapping part of a packet; changes should audit whether all DMA mappings and gather entries are restored.
- Queue reset from ethtool can race with netdev open/stop/TX/link/stat work if reset-state checks are incomplete.
- Firmware version checks and firmware state coordination happen across multiple functions/PFs. Preloaded firmware, auto firmware, and multi-function adapters need careful testing.
- `load_firmware()` calls `release_firmware(fw)` after `request_firmware()` failure even though the firmware pointer may not be valid under normal kernel API expectations.
- Watchdog logic assumes `get_other_octeon_device()` may return an adapter peer; paths under `CONFIG_MODULE_UNLOAD` read `other_oct->sriov_info` without an obvious null guard after `disable_all_vf_links(other_oct)`.
- `octeon_recv_vf_drv_notice()` trusts VF numbers parsed from firmware messages and uses them as bit indices/array indices without visible bounds validation.
- Many PF/VF administrative changes update local `oct->sriov_info` state after firmware command success, but several commands have no callback and limited rollback. Firmware failure or timeout can desynchronize local policy.
- PTP timestamp adjustment is local (`lio->ptp_adjust`) and is applied to RX/TX timestamps; hardware clock setting and adjustment need consistent locking and wraparound expectations.
- Module initialization waits up to 30 seconds for firmware started handshakes; failed async setup can cause long probe/module-load delays.

## Test Signals

- Probe/remove the driver on CN6XXX and CN23XX PF hardware, including firmware preloaded and host-loaded firmware paths.
- Exercise module load with multiple PFs on the same adapter and verify `handshake[]`, adapter firmware state, and watchdog startup/teardown.
- Run sustained TX/RX with checksum offload, GSO/TSO, SG SKBs, VLAN tags, VxLAN encapsulation, and hardware TX timestamping.
- Force IQ full conditions and TX timeouts to verify subqueue stop/wake, BQL accounting through core helpers, and queue polling behavior.
- Bring interfaces up/down repeatedly while polling `ethtool -S` and changing link state from firmware to verify workqueue cancellation and no use-after-free.
- Test SR-IOV enable/disable, assigned-VF rejection, VF MAC/VLAN/spoof/trust/link-state operations, VF driver loaded/removed notices, and switchdev representor mode.
- Validate PTP with `phc2sys`/`testptp`, RX timestamp filters, TX timestamp requests, and netdev open/stop cycles.
- Inject firmware command failures/timeouts and PCI AER fatal/nonfatal events to verify cleanup, handshake completion, and absence of leaked IRQs, tasklets, workqueues, and DMA mappings.
