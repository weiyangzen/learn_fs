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
