# Research Report: subset-b-004389

This grouped report covers the LiquidIO core, ethtool, and main network-driver files listed for `subset-b-004389`. Each source section preserves the original source path and is wrapped in reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_core.c

## Purpose

`lio_core.c` contains shared LiquidIO NIC core support used by the main PF/VF netdev drivers. It is responsible for gather-list allocation, firmware control command completion logging, RX packet delivery into the Linux network stack, NAPI and interrupt scheduling, runtime I/O queue creation, MTU changes, periodic firmware statistics retrieval, and firmware-backed speed/FEC operations. It is built into `liquidio-core.o` with `lio_ethtool.o`, while `lio_main.c` consumes its exported functions.

## Important APIs, Types, and Functions

- `lio_setup_glists()` / `lio_delete_glists()` allocate and release per-IQ `struct octnic_gather` pools backed by coherent DMA memory. These lists are later consumed by `liquidio_xmit()` in `lio_main.c` for SG transmit packets.
- `liquidio_set_feature()` sends asynchronous `struct octnic_ctrl_pkt` feature commands to firmware and uses `liquidio_link_ctrl_cmd_completion()` as the common completion callback.
- `liquidio_link_ctrl_cmd_completion()` interprets firmware command completions for MAC changes, LED identification, LRO, verbose logging, VLAN filtering, tunnel checksum, VxLAN port, flow-control, and queue-count changes.
- `octeon_pf_changed_vf_macaddr()` handles PF-driven VF MAC updates, updates `netdev->dev_addr`, updates `lio->linfo.hw_addr`, and emits `NETDEV_CHANGEADDR`.
- `setup_rx_oom_poll_fn()`, `cleanup_rx_oom_poll_fn()`, `octeon_schedule_rxq_oom_work()`, and `octnet_poll_check_rxq_oom_status()` implement delayed refill retry for DROQs that failed RX buffer allocation.
- `liquidio_setup_io_queues()` creates DROQs and IQs for a netdev, registers `liquidio_push_packet()` as the receive callback, attaches NAPI through `liquidio_napi_poll()`, assigns CPU affinity hints, and sets XPS for MSI-X vectors.
- `liquidio_push_packet()` builds received SKBs from LiquidIO DROQ buffers, handles paged RX buffers, strips firmware RX headers, applies hash/timestamp/checksum/VLAN metadata, and submits packets via `napi_gro_receive()`.
- `liquidio_napi_poll()`, `liquidio_msix_intr_handler()`, and `liquidio_legacy_intr_handler()` coordinate RX and TX-completion processing in NAPI, MSI-X, MSI, and legacy interrupt modes.
- `octeon_setup_interrupt()` allocates MSI-X or MSI/legacy IRQ resources, names IRQs, requests handlers, and records affinity hints.
- `liquidio_change_mtu()` sends a synchronous firmware soft command before committing `netdev->mtu` and `lio->mtu`.
- `lio_wait_for_clean_oq()` polls all active output queues until pending RX packets drain.
- `lio_fetch_stats()` and `octnet_nic_stats_callback()` periodically fetch firmware port stats into `oct_dev->link_stats`; PF mode also polls VF spoof counters via `lio_fetch_vf_stats()`.
- `liquidio_get_speed()`, `liquidio_set_speed()`, `liquidio_get_fec()`, and `liquidio_set_fec()` send SEAPI/UBoot-control soft commands for 25G-capable CN23XX PFs.

## Control Flow

Queue setup starts in `liquidio_setup_io_queues()`: for each RX PCI queue from `lio->linfo.rxpciq`, it creates a DROQ, attaches a NAPI struct, assigns a target CPU, and registers packet dispatch ops. For each TX PCI queue from `lio->linfo.txpciq`, it creates an instruction queue and optionally applies XPS using the MSI-X vector affinity mask. CN23XX PF/VF queue zero is treated specially because firmware control messages may arrive while the netdev is down, so queue-zero poll mode can be disabled.

RX interrupt handling branches by interrupt mode. MSI-X vectors call `liquidio_msix_intr_handler()`, which asks the chip-specific handler for interrupt status and schedules NAPI or a tasklet through `liquidio_schedule_msix_droq_pkt_handler()`. Non-MSI-X modes call `liquidio_legacy_intr_handler()`, which disables interrupts, processes interrupt registers, schedules affected DROQs, and re-enables interrupts unless the device is in reset. NAPI polls call `octeon_droq_process_poll_pkts()` for RX and `octeon_flush_iq()` for TX completions, then wake stopped TX subqueues if their IQ has capacity.

RX packet flow enters `liquidio_push_packet()` after DROQ dispatch. The function rejects packets if the interface is not `LIO_IFSTATE_RUNNING`; otherwise it reconstructs linear and paged SKB data, processes optional PTP timestamp and RSS hash fields from the firmware data header, pulls the Octeon header, sets protocol and checksum state, marks encapsulated packets, attaches VLAN tags, and hands the packet to GRO. DROQ RX byte and packet counters are updated after header removal.

Firmware command flows are mostly synchronous soft commands for operations needing an immediate result and asynchronous control packets for feature changes. `liquidio_change_mtu()`, stats fetch, speed, and FEC use `octeon_alloc_soft_command()`, `octeon_prepare_soft_command()`, `octeon_send_soft_command()`, and `wait_for_sc_completion_timeout()`. Feature, VLAN, VxLAN, and logging changes use `octnet_send_nic_ctrl_pkt()` and report via `liquidio_link_ctrl_cmd_completion()`.

## State and Persistence Behavior

This file maintains runtime, in-memory driver state only. Gather-list state lives in `lio->glist`, `lio->glist_lock`, `lio->glists_virt_base`, `lio->glists_dma_base`, and `lio->glist_entry_size`; all of it is freed on netdev teardown or queue reset. RX OOM retry state is held in per-queue `cavium_wq` workqueues under `lio->rxq_status_wq`. NAPI, DROQ, IQ, and IRQ state are stored in `struct octeon_device`, `struct octeon_droq`, `struct octeon_instr_queue`, `struct octeon_ioq_vector`, and `oct->io_qmask`.

Persistent hardware or firmware-backed state includes MTU, speed, FEC, feature toggles, VLAN filters, tunnel checksum settings, VxLAN ports, flow control, and firmware debug verbosity. The local driver mirrors some of that state in `netdev->mtu`, `lio->mtu`, `oct->speed_setting`, `oct->no_speed_setting`, `oct->props[ifidx].fec`, `oct_dev->link_stats`, `oct_dev->rx_pause`, and `oct_dev->tx_pause`.

Soft-command lifetime is explicit and subtle: callers set `sc->caller_is_done` after completion is consumed, but failure and timeout paths sometimes return before setting it. Any changes to soft-command flows need to preserve the response-manager ownership contract.

## Dependencies and Integration Points

The file depends on kernel networking (`net_device`, NAPI, GRO, VLAN acceleration, BQL, queue wake/stop APIs), PCI/MSI-X interrupt APIs, workqueues, DMA mapping helpers supplied by LiquidIO, and the LiquidIO internal Octeon abstractions in `octeon_droq.h`, `octeon_iq.h`, `response_manager.h`, `octeon_device.h`, `octeon_nic.h`, `octeon_main.h`, and `octeon_network.h`.

It exports the core functions used by `lio_main.c` and `lio_ethtool.c`: gather-list management, feature control, queue setup, interrupt setup, MTU change, RX drain wait, stats polling, and speed/FEC getters and setters. It also integrates with chip-specific register programming through function pointers in `oct->fn_list` and chip macros for CN23XX PF/VF and CN6XXX families.

## Risks and Edge Cases

- Queue reset and teardown paths depend on exact ordering: NAPI deletion, DROQ/IQ deletion, IRQ cleanup, glist freeing, firmware notification, and re-enablement must remain synchronized.
- Some workqueue setup functions return immediately on allocation failure without cleaning earlier per-queue workqueues allocated in the same loop; callers should ensure failure cleanup paths destroy partially initialized queues.
- `lio_setup_glists()` allocates DMA backing and many `struct octnic_gather` objects per IQ; queue-size changes can expose memory pressure and NUMA fallback behavior.
- `liquidio_push_packet()` trusts firmware RX header fields to locate timestamp/hash metadata and pull the header. Bounds assumptions are inherited from DROQ packet construction and should be treated as a high-value fuzz/test target.
- `octeon_setup_interrupt()` has different cleanup paths for PF MSI-X, VF MSI-X, MSI, and legacy interrupts; error paths must not free unrequested auxiliary IRQs or leave affinity hints behind.
- Speed and FEC functions are PF-only and firmware-version/subsystem dependent. They cache local state after firmware replies, so failed or partial firmware updates can leave local and hardware state diverged.
- Stats fetch and MTU/speed/FEC command paths can return on wait timeout before marking `caller_is_done`, depending on helper semantics; response-manager leak or use-after-free behavior should be checked when modifying these areas.

## Test Signals

- Bring a LiquidIO PF interface up/down repeatedly under traffic and verify NAPI enable/disable, IRQ enablement, and TX queue wakeups with no WARNs or leaked IRQs.
- Exercise RX with small packets, paged buffers, VLAN tags, RSS hash, encapsulated VxLAN packets, and RX checksum on/off to validate `liquidio_push_packet()`.
- Force RX buffer allocation failure and verify delayed OOM refill retries stop after interface down and resume while running.
- Change MTU through `ip link set mtu` and verify firmware rejection does not update `netdev->mtu`.
- Toggle LRO, VLAN filter, tunnel checksum, VxLAN UDP ports, firmware verbosity, speed, and FEC through netdev/ethtool paths and confirm firmware command completion plus local state.
- Test MSI-X PF, MSI-X VF, MSI fallback, and legacy IRQ modes, including module unload and probe-failure cleanup.
- Monitor `ethtool -S` and netdev stats while traffic runs to confirm periodic firmware stats update and no stale queue stats after queue reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_ethtool.c

## Purpose

`lio_ethtool.c` provides the ethtool control and observability surface for LiquidIO PF and VF netdevs. It translates ethtool requests into local driver state reads, chip CSR reads/writes, firmware soft commands, and netdev/queue reconfiguration. It also selects separate PF and VF `struct ethtool_ops` tables through `liquidio_set_ethtool_ops()`.

## Important APIs, Types, and Functions

- `lio_get_link_ksettings()` reports port type, link modes, speed, duplex, FEC advertising, and 10G/25G support using `lio->linfo`, `oct->subsystem_id`, `oct->speed_setting`, and firmware-backed speed/FEC getters.
- `lio_set_link_ksettings()` supports 10G/25G speed changes only on supported CN23XX 25G PFs and delegates to `liquidio_set_speed()`.
- `lio_get_drvinfo()` and `lio_get_vf_drvinfo()` expose driver name, firmware version, and PCI bus name.
- `lio_ethtool_get_channels()` and `lio_ethtool_set_channels()` report and change combined RX/TX queue count, with CN23XX PF/VF-specific maximum discovery.
- `lio_reset_queues()` is the central queue teardown/rebuild helper used by channel count and ring descriptor count changes.
- `lio_ethtool_get_ringparam()` and `lio_ethtool_set_ringparam()` expose and reconfigure RX/TX descriptor counts for CN23XX PF/VF.
- `lio_set_phys_id()`, `octnet_gpio_access()`, `octnet_id_active()`, and `octnet_mdio45_access()` implement LED identification using GPIO, MDIO clause 45, or firmware commands depending on chip.
- `lio_get_pauseparam()` and `lio_set_pauseparam()` expose flow-control state and send `OCTNET_CMD_SET_FLOW_CTL` for CN23XX PF.
- `lio_get_ethtool_stats()` and `lio_vf_get_ethtool_stats()` assemble PF/VF stats from netdev stats, firmware link stats, IQ stats, and DROQ stats.
- `lio_get_strings()`, `lio_vf_get_strings()`, `lio_get_sset_count()`, and `lio_vf_get_sset_count()` keep ethtool string tables aligned with stats output.
- `octnet_get_intrmod_cfg()`, `octnet_set_intrmod_cfg()`, `lio_get_intr_coalesce()`, and `lio_set_intr_coalesce()` expose interrupt moderation, including adaptive firmware parameters and direct CSR updates.
- `lio_get_regs_len()` and `lio_get_regs()` provide register dumps for CN23XX PF, CN23XX VF, and CN6XXX variants.
- `lio_get_fecparam()` and `lio_set_fecparam()` expose FEC settings for supported 25G CN23XX cards through core FEC helpers.
- `lio_get_priv_flags()` and `lio_set_priv_flags()` expose driver private flags stored in `oct->priv_flags`; the visible private flag string table is currently empty.

## Control Flow

Normal ethtool reads are direct: link settings read `lio->linfo` and occasionally refresh speed/FEC from firmware; stats read netdev/IQ/DROQ/link-stat counters; register dumps read CSRs into the provided buffer. Writes are split between simple firmware control commands and disruptive queue reconfiguration.

Channel-count changes enter `lio_ethtool_set_channels()`. The function enforces firmware version `>= 1.6.1`, accepts only `combined_count`, validates chip-specific maximums, marks the interface `LIO_IFSTATE_RESETTING`, stops the netdev if it is running, calls `lio_reset_queues()`, reopens if needed, and clears reset state. Ring descriptor changes follow a similar flow in `lio_ethtool_set_ringparam()`, except they first update the configured descriptor counts and roll those values back if `lio_reset_queues()` fails.

`lio_reset_queues()` drains pending requests, turns queues off in firmware/hardware, disables all I/O queues, deletes NAPI entries, optionally tears down RX OOM workqueues and gather lists, deletes all active DROQs and IQs, updates SR-IOV ring allocation when queue count changes, re-runs chip register setup, recreates instruction/output queue structures, recreates PF mailbox and IRQs when needed, re-enables I/O queues, informs firmware about queue counts, calls `liquidio_setup_io_queues()`, and recreates gather lists plus RX OOM polling.

Coalesce changes first configure firmware adaptive interrupt moderation through `oct_cfg_adaptive_intr()`. If adaptive mode is disabled, the function programs RX interrupt time/count thresholds and TX interrupt count thresholds directly into CN6XXX or CN23XX PF/VF CSRs and mirrors values into `oct->rx_coalesce_usecs`, `oct->rx_max_coalesced_frames`, and `oct->tx_max_coalesced_frames`.

## State and Persistence Behavior

The file reads and writes several layers of state:

- Netdev-visible state: link settings, ring/channel parameters, stats, pause parameters, FEC, timestamp info, and register dumps.
- Local driver state: `lio->msg_enable`, `lio->ifstate`, `oct->num_iqs`, `oct->num_oqs`, `oct->priv_flags`, coalesce caches, pause flags, FEC/speed caches, and queue masks.
- Firmware state: speed, FEC, queue count, interrupt moderation policy, LED activity, MDIO values, flow control, and queue/ring configuration.
- Hardware state: MSI-X IRQ allocation, IQ/DROQ registers, interrupt thresholds, and CSR register dump contents.

No durable filesystem state is written. Persistence is in the adapter firmware, chip registers, and Linux in-memory driver structures. Some settings, especially FEC and speed, may require reload or reboot semantics described only through log messages, so callers should not assume immediate link renegotiation from local state alone.

## Dependencies and Integration Points

The file integrates Linux ethtool APIs, netdev queue APIs, NAPI list manipulation, PCI MSI-X APIs, chip-specific CN23XX/CN6XXX CSR macros, and LiquidIO firmware command helpers. It calls exported functions from `lio_core.c` for queue setup, gather-list management, RX OOM workqueue setup, interrupts, feature logging, speed/FEC, and RX drain waits. It also relies on chip-specific helpers such as `cn23xx_sriov_config()`, `octeon_allocate_ioq_vector()`, `octeon_setup_interrupt()`, `cn23xx_pf_get_oq_ticks()`, and `cn23xx_vf_get_oq_ticks()`.

`liquidio_set_ethtool_ops()` is called during netdev setup in `lio_main.c`, assigning the VF ops table for CN23XX VFs and the PF/full ops table otherwise. Several PF-only capabilities are hidden or rejected for VFs through the ops table or runtime checks.

## Risks and Edge Cases

- `lio_reset_queues()` performs broad teardown and rebuild under ethtool calls. Failure in the middle can leave NAPI, IRQs, mailbox state, config values, or queue objects partially changed; only ring descriptor counts have explicit config rollback.
- `lio_ethtool_set_channels()` sets `LIO_IFSTATE_RESETTING` and may return early on reset failure without clearing it or reopening a previously stopped netdev.
- Stats string counts must exactly match stats data order. Any change to `oct_stats_strings`, `oct_vf_stats_strings`, `oct_iq_stats_strings`, or `oct_droq_stats_strings` requires coordinated updates to the data fill loops and sset counts.
- Register dumps append many formatted strings into fixed-size ethtool buffers using `sprintf`. The advertised lengths are constants, so additions to dump content need explicit size validation to avoid overrun.
- Firmware version checks use string comparison for versions such as `"1.6.1"` and `"1.7.1"`, which can misorder multi-digit version components.
- LED identification paths differ sharply by chip and firmware version. MDIO restore failures can leave CN68XX LED registers in identification mode.
- Coalesce configuration mixes firmware adaptive moderation with direct CSR writes. Partial failure can leave firmware and cached local values inconsistent.
- PF/VF queue indexing differs between direct queue numbers and PF SRN-adjusted queue numbers; off-by-base mistakes can affect other functions or VFs.

## Test Signals

- Run `ethtool`, `ethtool -i`, `ethtool -k`, `ethtool -c`, `ethtool -g`, `ethtool -l`, `ethtool -S`, `ethtool -d`, `ethtool --show-fec`, and `ethtool --identify` on PF and VF devices.
- Change combined channels while traffic is active and while the netdev is down, then verify queue count, IRQ count, NAPI count, XPS affinity, and firmware queue count.
- Change ring sizes to minimum, maximum, and clamped values; verify rollback on reset failure and no stale descriptor counts.
- Validate stats string/data alignment by checking `ethtool -S` output length and counter plausibility before and after queue-count changes.
- Toggle adaptive and fixed interrupt coalescing and verify CSR values plus firmware moderation state.
- Test PF-only paths on VF devices and unsupported CN6XXX/CN23XX variants to confirm `-EOPNOTSUPP` or `-EINVAL` behavior.
- Run register dump paths under KASAN or hardened builds because fixed dump lengths and nested loops are sensitive to buffer growth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_main.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_main.c -->
