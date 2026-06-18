# subset-b-004643 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/selftest.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/selftest.c

## Purpose
Implements Siena online/offline ethtool self-tests: PHY liveness, NVRAM, IRQ generation, event queue interrupt/DMA delivery, PHY extended tests, chip register tests through the NIC type, and disruptive MAC/PHY loopback traffic.

## Important APIs, Types, And Functions
- Public entry points: `efx_siena_selftest()`, `efx_siena_loopback_rx_packet()`, `efx_siena_selftest_async_init()`, `efx_siena_selftest_async_start()`, and `efx_siena_selftest_async_cancel()`.
- Test result ABI: `struct efx_self_tests` and per-loopback counters in `struct efx_loopback_self_tests`.
- Loopback internals: packed `struct efx_loopback_payload`, transient `struct efx_loopback_state`, `efx_begin_loopback()`, `efx_end_loopback()`, `efx_test_loopback()`, and `efx_test_loopbacks()`.
- Online diagnostics: `efx_test_phy_alive()`, `efx_test_nvram()`, `efx_test_interrupts()`, `efx_test_eventq_irq()`, and `efx_test_phy()`.

## Control Flow
`efx_siena_selftest()` cancels pending async IRQ diagnostics, runs non-disruptive PHY/NVRAM/interrupt/eventq checks, and aborts on online failure. Without `ETH_TEST_FL_OFFLINE`, it finishes with PHY tests. Offline mode detaches the netdev, runs the NIC type chip test if available, forces PHY out of low power and loopback, runs PHY tests, then iterates all supported loopback modes and enabled TX queue types. Each loopback mode reconfigures the port under `mac_lock`, waits for two stable link-up samples, sends increasing packet bursts through a chosen TX queue, and validates returned packets in the RX callback.

## State And Persistence Behavior
State is runtime-only. Results are written into the caller-supplied `struct efx_self_tests`, using `1` pass, `-1` failure, and `0` unavailable. Loopback state is temporarily installed at `efx->loopback_selftest`; received packets are either dropped during flush or validated and counted with atomics. The original PHY mode and loopback mode are restored before reattaching the netdev.

## Dependencies And Integration Points
Depends on Siena MCDI PHY/NVRAM tests, farch event/IRQ test hooks, TX enqueue, RX loopback diversion, netdevice detach/attach, delayed work, ethtool flags, `mac_lock`, and the NIC type callback table (`test_chip`, `test_nvram`, `monitor`, `check_mac_fault`).

## Risks And Test Signals
Long IRQ latency can cause false interrupt failures despite the one-second timeout. Offline tests are disruptive and must restore device state after errors. Loopback validation is sensitive to stale in-flight packets, so `flush` and memory barriers are important. Test signals are per-channel eventq DMA/interrupt arrays, loopback `tx_sent`, `tx_done`, `rx_good`, `rx_bad`, PHY extended results, timeout logs, and reset scheduling after unrecoverable chip-test failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/selftest.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/selftest.h

## Purpose
Declares the Siena self-test result structures and public self-test entry points used by ethtool, RX loopback handling, and asynchronous interrupt diagnostics.

## Important APIs, Types, And Functions
- `struct efx_loopback_self_tests` records per-TXQ sent/completed counts and aggregate RX good/bad counts.
- `struct efx_self_tests` contains online test results, offline chip/PHY results, and loopback results indexed by `LOOPBACK_TEST_MAX`.
- `EFX_MAX_PHY_TESTS` bounds PHY vendor-specific test results.
- Declared APIs are `efx_siena_loopback_rx_packet()`, `efx_siena_selftest()`, `efx_siena_selftest_async_init()`, `efx_siena_selftest_async_start()`, and `efx_siena_selftest_async_cancel()`.

## Control Flow
The header exposes a simple control surface: ethtool invokes `efx_siena_selftest()`, RX code calls `efx_siena_loopback_rx_packet()` when loopback self-test state is installed, and probe/open paths initialize/start/cancel delayed async interrupt checks.

## State And Persistence Behavior
The file only declares in-memory result containers. The result convention is documented: non-counter tests use `1` for success, `-1` for failure, and `0` when not run or unsupported. No persistent state or storage format is introduced.

## Dependencies And Integration Points
Includes `net_driver.h` for `struct efx_nic`, channel/TX queue constants, and loopback mode definitions. It integrates with `ethtool_common.c`, Siena RX paths, and common driver lifecycle code that owns `efx->selftest_work`.

## Risks And Test Signals
Array dimensions must stay aligned with driver constants such as `EFX_MAX_CHANNELS`, `EFX_MAX_TXQ_PER_CHANNEL`, and `LOOPBACK_TEST_MAX`. Useful test signals are compile-time coverage of structure consumers and ethtool self-test output matching these result fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/selftest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/siena.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/siena.c

## Purpose
Provides hardware control for the SFC9000/Siena NIC family and publishes `siena_a0_nic_type`, the callback table that connects the common driver to Siena-specific probe, reset, MCDI, stats, RX/TX/event/filter, WoL, PTP, MTD, self-test, and optional SR-IOV behavior.

## Important APIs, Types, And Functions
- Exported type object: `const struct efx_nic_type siena_a0_nic_type`.
- Lifecycle: `siena_probe_nic()`, `siena_init_nic()`, `siena_remove_nic()`, `siena_dimension_resources()`.
- Reset/test: `siena_map_reset_flags()`, `siena_test_chip()`, `efx_siena_prepare_flush()`, `siena_finish_flush()`.
- RSS/statistics: `siena_rx_push_rss_config()`, `siena_rx_pull_rss_config()`, `siena_try_update_nic_stats()`, `siena_update_nic_stats()`, `siena_describe_nic_stats()`.
- Control plane: `siena_mcdi_request()`, `siena_mcdi_poll_response()`, `siena_mcdi_read_response()`, `siena_mcdi_poll_reboot()`.
- Feature hooks: `siena_mac_reconfigure()`, `siena_get_wol()`, `siena_set_wol()`, `siena_init_wol()`, `siena_ptp_set_ts_config()`.

## Control Flow
Probe allocates `struct siena_nic_data`, rejects FPGA builds, initializes MCDI, resets the NIC, initializes WoL, allocates `irq_status`, reads board/NVRAM config, probes monitoring, optionally probes SR-IOV, and defers PTP setup. NIC init handles firmware assertions, programs TX/RX hardware registers, pushes RSS config, enables event logging, routes flush events, disables user events until SR-IOV enables them, and calls farch common init. Removal tears down monitoring, buffers, resets/detaches MCDI, and frees private data.

## State And Persistence Behavior
Runtime state lives under `efx` and `struct siena_nic_data`: timer quantum, port number, WoL filter id, IRQ status buffer, DMA stats, and optional SR-IOV backing data. Statistics are read from a DMA buffer using generation start/end fields and then copied into local cumulative software counters. WoL filter state persists in firmware/NVRAM-facing management controller state and is synchronized during initialization.

## Dependencies And Integration Points
Integrates with farch register access, MCDI protocol helpers, MCDI port/common/MTD/PTP helpers, RX common, filters, IRQ/event paths, ethtool stats and resets, PCI WoL, and optional `CONFIG_SFC_SIENA_SRIOV` hooks. The `siena_a0_nic_type` table is the main integration point consumed by generic probe/netdev code.

## Risks And Test Signals
Failure paths must unwind MCDI, IRQ buffers, monitor probe, and private state in the right order. Stats reads can race DMA updates and rely on generation retry loops. MCDI shared-memory polling must treat all-ones as reset. Test signals include successful probe/reset, RSS hash/indir updates, ethtool stats consistency, WoL enable/disable behavior across suspend, MCDI reboot detection, offline chip register tests, and SR-IOV hook availability when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/siena.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/siena_sriov.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/siena_sriov.c

## Purpose
Implements Siena PF-side SR-IOV support, including firmware SR-IOV enablement, VF resource reservation, VFDI mailbox protocol handling, VF queue/filter/status management, VF reset notification, peer address publication, and netlink VF configuration callbacks.

## Important APIs, Types, And Functions
- Core VF state: `struct siena_vf`, `struct efx_memcpy_req`, `struct efx_local_addr`, and `struct efx_endpoint_page`.
- SR-IOV lifecycle: `efx_siena_sriov_probe()`, `efx_siena_sriov_init()`, `efx_siena_sriov_fini()`, `efx_siena_sriov_reset()`, `efx_siena_sriov_flr()`, `efx_init_sriov()`, `efx_fini_sriov()`.
- VFDI handling: `efx_siena_sriov_event()`, `efx_siena_sriov_vfdi()`, `efx_vfdi_init_evq()`, `efx_vfdi_init_rxq()`, `efx_vfdi_init_txq()`, `efx_vfdi_fini_all_queues()`, filter and status-page handlers.
- VF configuration: `efx_siena_sriov_set_vf_mac()`, `efx_siena_sriov_set_vf_vlan()`, `efx_siena_sriov_set_vf_spoofchk()`, `efx_siena_sriov_get_vf_config()`, `efx_siena_sriov_wanted()`.

## Control Flow
Probe asks firmware how many VFs and VIs are available, bounds by `max_vfs`, and reserves an extra MSI-X channel for VFDI events. Init enables firmware SR-IOV, allocates a DMA `vfdi_status` page, allocates per-VF state and request buffers, discovers PCI VF requester IDs, publishes PF/VF counts, enables user events, then calls `pci_enable_sriov()`. VF user events are assembled as four ordered VFDI address words; a complete request queues work, DMAs the request page from the VF, dispatches by `op`, then writes response `rc` and `op` back to guest memory.

## State And Persistence Behavior
All state is runtime PF memory and firmware configuration. Per VF, the driver tracks requester ID, VFDI sequence/address state, request buffer, buffer-table base, RX/TX filter IDs, MAC/VLAN endpoint, status-page DMA address, peer pages, EVQ0 backing pages, queue bitmasks/counts, retry masks, waitqueues, and reset work. Firmware SR-IOV enablement and PCI VF enablement are undone during fini.

## Dependencies And Integration Points
Depends on PCI SR-IOV capability registers, Siena MCDI `MC_CMD_SRIOV` and `MC_CMD_MEMCPY`, farch registers and buffer table writes, filters, queue/event register tables, netdev RTNL locking, workqueues, `vfdi.h` ABI definitions, and `siena.c` NIC type hooks. Netlink VF operations reach this file through generic SR-IOV wrappers and the NIC type table.

## Risks And Test Signals
The VFDI sequence state machine rejects malformed or overlapping requests; bugs can hang guest VF initialization. Queue count tracking is tied to flush completion events and retry masks. Status updates use generation fields and DMA ordering barriers; broken ordering can expose torn data to guests. Test signals include VF creation/removal, guest VFDI queue init/fini/filter/status operations, spoof-check changes only while TX queues are stopped, FLR/reset notification events, flush timeout/retry logs, and peer list updates after VF/PF MAC changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/siena_sriov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/siena_sriov.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/siena_sriov.h

## Purpose
Declares Siena-specific SR-IOV constants and the PF-side SR-IOV API used by the Siena NIC type and event/flush paths.

## Important APIs, Types, And Functions
- Resource constants: `EFX_VI_SCALE_MAX`, `EFX_VI_BASE`, `EFX_VF_COUNT_MAX`, `EFX_MAX_VF_EVQ_SIZE`, and `EFX_VF_BUFTBL_PER_VI`.
- Lifecycle/configuration declarations: `efx_siena_sriov_probe()`, `efx_siena_sriov_configure()`, `efx_siena_sriov_init()`, `efx_siena_sriov_fini()`, `efx_siena_sriov_wanted()`, `efx_siena_sriov_reset()`, `efx_siena_sriov_flr()`.
- VF netlink operations: `efx_siena_sriov_set_vf_mac()`, `efx_siena_sriov_set_vf_vlan()`, `efx_siena_sriov_set_vf_spoofchk()`, `efx_siena_sriov_get_vf_config()`.
- Event helpers: `efx_siena_sriov_event()`, TX/RX flush completion handlers, and descriptor-fetch error handling.

## Control Flow
The header lets `siena.c` wire SR-IOV callbacks into `siena_a0_nic_type`, while farch event code can report VF user events, queue flush completions, FLR, and descriptor-fetch errors back to the SR-IOV backend. `efx_siena_sriov_enabled()` compiles to a real `vf_init_count` check under `CONFIG_SFC_SIENA_SRIOV` and to `false` otherwise.

## State And Persistence Behavior
This file defines hardware resource layout constraints rather than owning state. The constants determine how VIs and buffer table entries are partitioned between PF and VF BAR/register access.

## Dependencies And Integration Points
Includes `net_driver.h` and relies on `struct efx_nic`, `struct efx_channel`, `efx_qword_t`, and Linux `ifla_vf_info`. Its declarations are consumed by Siena probe/init/remove, event handling, netdev VF ops, and module-level SR-IOV workqueue setup.

## Risks And Test Signals
Incorrect VI scale/base/count constants would corrupt PF/VF register ownership. Build coverage should include both `CONFIG_SFC_SIENA_SRIOV=y` and disabled cases. Runtime signals are correct VF count/resource sizing and no SR-IOV callbacks used when the feature is compiled out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/siena_sriov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/sriov.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/sriov.h

## Purpose
Provides inline netdevice SR-IOV wrapper functions for the Siena driver variant, translating Linux `ndo_set_vf_*` calls into NIC type operations when `CONFIG_SFC_SIENA_SRIOV` is enabled.

## Important APIs, Types, And Functions
- Inline wrappers: `efx_sriov_set_vf_mac()`, `efx_sriov_set_vf_vlan()`, `efx_sriov_set_vf_spoofchk()`, `efx_sriov_get_vf_config()`, and `efx_sriov_set_vf_link_state()`.
- VLAN validation enforces `VLAN_VID_MASK`, `VLAN_PRIO_MASK`, and only `ETH_P_8021Q` protocol.

## Control Flow
Each wrapper obtains `struct efx_nic *` with `netdev_priv()`, checks whether the current NIC type supplies the relevant SR-IOV operation, validates wrapper-level arguments when needed, and returns `-EOPNOTSUPP`, `-EINVAL`, or `-EPROTONOSUPPORT` before dispatch when unsupported or invalid.

## State And Persistence Behavior
The header owns no state. It gates access to per-NIC SR-IOV state owned by the underlying NIC type implementation.

## Dependencies And Integration Points
Integrated directly with Siena `net_device_ops` and the `siena_a0_nic_type` SR-IOV function pointers. It depends on VLAN and Ethernet protocol definitions from kernel networking headers through `net_driver.h`.

## Risks And Test Signals
Because wrappers are inline and compiled only under `CONFIG_SFC_SIENA_SRIOV`, disabled builds must not reference missing symbols. Test signals include netlink VF MAC/VLAN/spoof-check/config calls returning expected validation errors and dispatching to Siena-specific handlers when VFs are initialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/sriov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx.c

## Purpose
Implements Siena transmit hot-path logic for SKB and XDP frames, including TX queue selection, copy-buffer handling, queue stop/restart decisions, PTP transmit diversion, descriptor submission, and mqprio traffic-class setup.

## Important APIs, Types, And Functions
- SKB path: `efx_siena_hard_start_xmit()` and `__efx_siena_enqueue_skb()`.
- XDP path: `efx_siena_xdp_tx_buffers()`.
- Queue helpers: `efx_tx_get_copy_buffer()`, `efx_enqueue_skb_copy()`, `efx_tx_maybe_stop_queue()`, `efx_tx_send_pending()`, `efx_siena_init_tx_queue_core_txq()`.
- TC setup: `efx_siena_setup_tc()` for `TC_SETUP_QDISC_MQPRIO`.

## Control Flow
`efx_siena_hard_start_xmit()` maps the skb queue index to a TX channel and checksum/high-priority TXQ type, diverts timestamped PTP packets to the PTP path after flushing pending descriptors, and otherwise calls `__efx_siena_enqueue_skb()`. Enqueue handles GSO by software TSO fallback, copies short fragmented packets into DMA copy buffers, maps remaining SKB data to descriptors, stops the netdev queue when thresholds are crossed, marks descriptors pending, and rings the doorbell when `xmit_more` allows. XDP TX selects a per-CPU XDP TX queue, optionally locks borrowed netdev queues, maps each frame as one descriptor, and pushes on `flush`.

## State And Persistence Behavior
TX queue state is in-memory ring counters and descriptor buffers: `insert_count`, `read_count`, `xmit_pending`, `old_read_count`, per-queue stats, copy-buffer pages, and core netdev queue mapping. No persistent storage is changed.

## Dependencies And Integration Points
Depends on TX common mapping/completion helpers, NIC type `tx_limit_len`, farch doorbell push, PTP helpers, XDP frame lifecycle, DMA mapping APIs, Linux netdev queue accounting, and Siena hardware workaround definitions. It is wired into Siena `net_device_ops` as `.ndo_start_xmit` and `.ndo_setup_tc`.

## Risks And Test Signals
Queue stop logic relies on memory barriers to avoid missed wakeups. DMA mapping failure must unwind descriptors and still push earlier pending traffic when needed. XDP borrowed queues must not leave netdev queues permanently stopped. Test signals include high-load TX with `xmit_more`, small fragmented SKBs, GSO fallback, PTP timestamped packets, XDP redirect/TX under CPU count changes, mqprio with high-priority queues, and no TX watchdog stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx.h

## Purpose
Defines the Siena TX checksum-offload queue classifier used by the TX hot path to choose normal, inner-checksum, and outer-checksum TX queue types.

## Important APIs, Types, And Functions
- `efx_tx_csum_type_skb()` returns a bitmask of `EFX_TXQ_TYPE_OUTER_CSUM` and/or `EFX_TXQ_TYPE_INNER_CSUM`.
- Encapsulation handling distinguishes inner checksum offload from outer UDP tunnel checksum offload for GSO tunnel packets.

## Control Flow
The helper returns zero for SKBs without `CHECKSUM_PARTIAL`. For encapsulated packets whose checksum starts at the inner transport header, it selects inner checksum offload and adds outer checksum offload only for multi-segment UDP tunnel checksum GSO without `SKB_GSO_PARTIAL`. Non-encapsulated partial checksums use outer checksum offload.

## State And Persistence Behavior
The helper is stateless and only inspects SKB metadata. Its output affects transient TX queue selection in `efx_siena_hard_start_xmit()`.

## Dependencies And Integration Points
Depends on Linux SKB checksum/GSO helpers and EFX TXQ type constants. It is included by Siena `tx.c`.

## Risks And Test Signals
The function assumes advertised netdev features restrict packets to supported IPv4/IPv6 checksum cases. Test signals include encapsulated TCP/UDP GSO, UDP tunnel checksum offload, partial vs non-partial checksums, and correct TXQ selection without `WARN_ON_ONCE(!tx_queue)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx_common.c

## Purpose
Provides common Siena TX queue allocation, initialization, teardown, DMA unmapping, completion processing, descriptor mapping, enqueue unwind, descriptor count estimation, and software TSO fallback.

## Important APIs, Types, And Functions
- Queue lifecycle: `efx_siena_probe_tx_queue()`, `efx_siena_init_tx_queue()`, `efx_siena_fini_tx_queue()`, `efx_siena_remove_tx_queue()`.
- Completion path: `efx_siena_xmit_done()`, `efx_siena_xmit_done_check_empty()`, `efx_dequeue_buffer()`, `efx_dequeue_buffers()`.
- Mapping/unwind: `efx_siena_tx_map_chunk()`, `efx_siena_tx_map_data()`, `efx_siena_enqueue_unwind()`.
- Limits/fallback: `efx_siena_tx_max_skb_descs()` and `efx_siena_tx_tso_fallback()`.

## Control Flow
Probe rounds queue entries up to a hardware-compatible power of two, allocates software descriptor and copy-buffer arrays, then delegates hardware ring probing to the NIC type. Init resets ring counters, timestamp/XDP flags, and hardware descriptors. TX mapping maps the SKB head, optionally splits the TSO header, walks fragments, assigns unmap responsibility to final descriptors, and stores the SKB on the final buffer. Completion dequeues through a reported index, unmaps DMA, completes SKBs or XDP frames, updates queue accounting, wakes stopped queues when fill is below threshold, and records empty-read state for hardware.

## State And Persistence Behavior
Maintains runtime TX ring state only: descriptor buffers, copy-buffer pages, DMA mapping metadata, queue counters, completion stats, timestamp completion fields, and `core_txq` state. Teardown frees remaining buffers and resets netdev TX accounting.

## Dependencies And Integration Points
Depends on `net_driver.h`, common NIC TX operations (`efx_nic_probe_tx()`, `efx_nic_init_tx()`, `efx_nic_remove_tx()`), DMA APIs, PTP timestamp conversion, XDP return APIs, Linux GSO segmentation, and reset scheduling on invalid completions.

## Risks And Test Signals
DMA mapping failures after earlier fragments rely on caller unwind to unmap all inserted descriptors. Spurious completions schedule `RESET_TYPE_TX_SKIP`. Timestamp completion fields must be consumed exactly once. Test signals include TX ring probe/remove leak checks, fragmented SKB DMA unmap correctness, software TSO fallback, XDP completion returns, queue wake under high load, and reset logs for bogus completion indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx_common.h

## Purpose
Declares shared Siena TX queue lifecycle, completion, DMA mapping, descriptor-limit, and TSO fallback helpers used by the TX hot path and NIC setup code.

## Important APIs, Types, And Functions
- Lifecycle declarations: `efx_siena_probe_tx_queue()`, `efx_siena_init_tx_queue()`, `efx_siena_fini_tx_queue()`, `efx_siena_remove_tx_queue()`.
- Completion declarations: `efx_siena_xmit_done_check_empty()` and `efx_siena_xmit_done()`.
- Mapping helpers: `efx_siena_enqueue_unwind()`, `efx_siena_tx_map_chunk()`, `efx_siena_tx_map_data()`.
- Utility: `efx_tx_buffer_in_use()`, `efx_siena_tx_max_skb_descs()`, `efx_siena_tx_tso_fallback()`, and module parameter declaration `efx_siena_separate_tx_channels`.

## Control Flow
This header provides the contracts between enqueue code and completion/setup code. Enqueue maps descriptors and calls unwind on failure; event handling calls completion helpers; probe/remove call lifecycle helpers.

## State And Persistence Behavior
No state is owned here. `efx_tx_buffer_in_use()` defines the shared meaning of an active TX buffer as nonzero length or an option descriptor flag.

## Dependencies And Integration Points
Relies on `struct efx_tx_queue`, `struct efx_tx_buffer`, `struct sk_buff`, and DMA address types from surrounding driver headers. Included by `tx.c` and `tx_common.c`.

## Risks And Test Signals
The inline buffer-use predicate must remain consistent with producer and completion code. Build coverage should catch signature drift between hot path and common implementation. Runtime signals are correct unwind/completion behavior and no spurious-reset logs under normal TX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/tx_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/vfdi.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/vfdi.h

## Purpose
Defines the Virtual Function Driver Interface ABI used for Siena PF/VF communication over user events and DMA request/status pages.

## Important APIs, Types, And Functions
- Event field layout constants: `VFDI_EV_SEQ`, `VFDI_EV_TYPE`, `VFDI_EV_DATA`, request word types, status, and reset event types.
- Endpoint and status structures: `struct vfdi_endpoint` and `struct vfdi_status`.
- Request ABI: `enum vfdi_op`, response codes, and `struct vfdi_req` with operation-specific flexible-array payloads.
- Queue/filter flags: RX scatter, TX checksum-disable flags, MAC filter RSS/scatter flags.

## Control Flow
The VF sends a page-aligned request address as four ordered user events. The PF DMAs `struct vfdi_req` from that address, executes the requested operation, writes `rc` and `VFDI_OP_RESPONSE` back, and can asynchronously DMA `struct vfdi_status` then send status or reset events to EVQ0.

## State And Persistence Behavior
The file defines guest-visible memory layouts, so fields are part of an ABI rather than private state. `vfdi_status` uses `generation_start` and `generation_end` to let the VF detect torn DMA updates. Version and length fields allow compatible extension.

## Dependencies And Integration Points
Consumed by `siena_sriov.c` PF logic and the corresponding VF driver. Depends on kernel Ethernet/VLAN types through included driver headers. The ABI maps directly onto Siena hardware user-event mailbox semantics.

## Risks And Test Signals
Structure layout changes can break guest drivers. Flexible arrays require page-size bounds validation in PF code. Test signals include VF queue initialization, filter insertion, status page updates with matching generation values, peer-list extension pages, and reset event reception after PF/VF reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/vfdi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/workarounds.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/workarounds.h

## Purpose
Centralizes hardware workaround predicates and bug-number macros for Siena/Falcon-architecture and EF10-era Solarflare NICs.

## Important APIs, Types, And Functions
- Family predicates: `EFX_WORKAROUND_SIENA(efx)`, `EFX_WORKAROUND_EF10(efx)`, and unconditional `EFX_WORKAROUND_10G(efx)`.
- Bug workarounds: `EFX_WORKAROUND_7884`, `EFX_WORKAROUND_17213`, and `EFX_EF10_WORKAROUND_61265(efx)`.

## Control Flow
No functions run here. Call sites use the macros to conditionally route around hardware/firmware issues based on NIC revision or EF10 private data.

## State And Persistence Behavior
Stateless except for reading NIC revision or EF10 private workaround flags. No persistent behavior is introduced.

## Dependencies And Integration Points
Included by Siena self-test, TX, core NIC code, and other hardware-control paths. It depends on `efx_nic_rev()` and revision constants; the EF10 macro assumes `efx->nic_data` is `struct efx_ef10_nic_data`.

## Risks And Test Signals
The EF10-specific macro is unsafe if used on non-EF10 NIC data. Workaround predicates must match hardware revisions exactly. Test signals are revision-specific behavior in affected paths, especially legacy interrupt storm mitigation and moderation timer access routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/workarounds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/sriov.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/sriov.c

## Purpose
Implements generic SFC netdevice SR-IOV operation wrappers that validate Linux netlink inputs and dispatch to the active NIC type's VF management callbacks.

## Important APIs, Types, And Functions
- Exported wrappers: `efx_sriov_set_vf_mac()`, `efx_sriov_set_vf_vlan()`, `efx_sriov_set_vf_spoofchk()`, `efx_sriov_get_vf_config()`, and `efx_sriov_set_vf_link_state()`.
- VLAN wrapper validates VID, QoS, and `ETH_P_8021Q` protocol before dispatch.

## Control Flow
Each function obtains `struct efx_nic *` with `efx_netdev_priv()`, checks the corresponding function pointer in `efx->type`, and either calls it or returns `-EOPNOTSUPP`. VLAN setup returns `-EINVAL` for out-of-range VID/QoS and `-EPROTONOSUPPORT` for non-802.1Q VLAN protocol.

## State And Persistence Behavior
This file does not store state. It is a dispatch/validation layer over NIC-specific SR-IOV state.

## Dependencies And Integration Points
Included in netdev ops for non-Siena SFC drivers and depends on `nic.h` type callbacks. It parallels the Siena inline wrapper header but is a compiled object under `CONFIG_SFC_SRIOV`.

## Risks And Test Signals
The wrappers only validate common input and rely on NIC implementations for VF index/lifetime checks. Test signals include netlink VF operations returning correct errors on unsupported NICs, invalid VLAN data, unsupported VLAN protocols, and successful dispatch on NICs that populate the callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/sriov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/sriov.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/sriov.h

## Purpose
Declares generic SFC SR-IOV netdevice operation wrappers for builds with `CONFIG_SFC_SRIOV`.

## Important APIs, Types, And Functions
- Prototypes for `efx_sriov_set_vf_mac()`, `efx_sriov_set_vf_vlan()`, `efx_sriov_set_vf_spoofchk()`, `efx_sriov_get_vf_config()`, and `efx_sriov_set_vf_link_state()`.

## Control Flow
The header contributes no runtime logic; compiled users include it to wire netdev operations to `sriov.c` wrappers when SR-IOV support is enabled.

## State And Persistence Behavior
No state is owned here. It exposes operations that modify NIC-specific VF runtime configuration elsewhere.

## Dependencies And Integration Points
Includes `net_driver.h` for `struct net_device`, `struct ifla_vf_info`, integer types, and network constants. It integrates with generic SFC netdev operation tables.

## Risks And Test Signals
Disabled `CONFIG_SFC_SRIOV` builds intentionally omit prototypes, so call sites must be conditionally compiled. Build matrix coverage with SR-IOV enabled/disabled is the main test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/sriov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc.c

## Purpose
Implements EF100/SFC TC flower offload into MAE hardware: match parsing, representor/uplink/wire mport resolution, action translation, encap-match tracking, conntrack left-hand-side rules, recirculation IDs, pedit MAC tables, rule insert/delete/stats, default switching rules, fallback actions, representor RX filters, and TC state lifecycle.

## Important APIs, Types, And Functions
- Public API: `efx_tc_flower()`, `efx_tc_flower_lookup_efv()`, `efx_tc_flower_external_mport()`, `efx_tc_configure_default_rule_rep()`, `efx_tc_deconfigure_default_rule()`, `efx_tc_insert_rep_filters()`, `efx_tc_remove_rep_filters()`, `efx_init_tc()`, `efx_fini_tc()`, `efx_init_struct_tc()`, and `efx_fini_struct_tc()`.
- Match/action machinery: `efx_tc_flower_parse_match()`, `efx_tc_flower_replace()`, `efx_tc_flower_replace_foreign()`, `efx_tc_flower_destroy()`, `efx_tc_flower_stats()`, `efx_tc_flower_action_order_ok()`, `efx_tc_mangle()`, and `efx_tc_pedit_add()`.
- Resource tables: MAC pedits, encap matches, match-action rules, LHS rules, counters, conntrack, recirc IDs, encap actions, and MAE table metadata.

## Control Flow
`efx_tc_flower()` serializes operations with `efx->tc->mutex` and dispatches replace/destroy/stats. Replace validates offload support, resolves ingress device to PF/representor or foreign tunnel device, parses flower dissector keys, adds ingress mport and recirc matches, rewrites some conntrack masks, checks MAE capabilities, then translates sequential TC actions into MAE action sets and action-set lists. Delivery actions allocate hardware action sets; mirror actions clone cursor state; redirect/drop terminate the cursor. Conntrack lookup/goto rules become LHS rules, sometimes using Outer Rule encap matches for foreign tunnel traffic. Destroy removes LHS or action rules from hardware and releases all referenced software/hardware resources.

## State And Persistence Behavior
All state is runtime and rooted in `struct efx_tc_state`: capability data, block bindings, mutex, rhashtables, recirc IDA, conntrack metadata, representor mport/filter IDs, counter flush state, default rules, fallback action-set lists, and `up` flag. Rule resources are refcounted through rhashtables and freed on destroy or defensive teardown.

## Dependencies And Integration Points
Depends on Linux TC flower/flow offload APIs, indirect device registration, VXLAN/Geneve netdev identification, representor netdev ops, MAE firmware APIs, TC counters, encap actions, conntrack offload, filters, rhashtable, IDA, waitqueues, and netlink extack reporting. EF100 NIC lifecycle calls `efx_init_struct_tc()`, `efx_init_tc()`, `efx_fini_tc()`, and `efx_fini_struct_tc()`.

## Risks And Test Signals
Action ordering and unsupported masks must reject rules before partial hardware programming leaks resources. Foreign tunnel/LHS rules have overlap constraints through pseudo encap matches. Counter stats are delta-reported and lock protected. Teardown warns if rules remain. Test signals include TC flower replace/destroy/stats on PF and representors, tunnel encap/decap via VXLAN/Geneve, conntrack goto-chain rules, VLAN push/pop, pedit MAC/TTL, delayed hardware stats, rule readiness fallback, indirect tunnel binding, default PF/wire/representor switching, and leak-free teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc.h

## Purpose
Defines the TC flower offload data model for SFC MAE hardware, including match fields, action sets, encap matches, recirculation IDs, flow/LHS rules, MAE table descriptors, and the top-level `struct efx_tc_state`.

## Important APIs, Types, And Functions
- Core types: `struct efx_tc_action_set`, `struct efx_tc_match_fields`, `struct efx_tc_match`, `struct efx_tc_flow_rule`, `struct efx_tc_lhs_rule`, `struct efx_tc_state`.
- Resource types: `struct efx_tc_mac_pedit_action`, `struct efx_tc_encap_match`, `struct efx_tc_recirc_id`, `struct efx_tc_action_set_list`, `struct efx_tc_lhs_action`, and MAE table descriptor structs.
- Helpers/API declarations: `efx_tc_match_is_encap()`, `efx_ipv6_addr_all_ones()`, `efx_tc_indr_netdev_type()`, `efx_tc_flower()`, representor filter/default-rule helpers, and TC init/fini functions.

## Control Flow
The header describes the structures filled by `tc.c` during rule parsing and consumed by MAE programming helpers. Match structs carry value/mask pairs plus encap and recirc references. Action sets model MAE's fixed-order packet mutations and delivery. Top-level state groups all lookup tables and default/fallback rules used while TC offload is active.

## State And Persistence Behavior
`struct efx_tc_state` is runtime-only but long-lived for the NIC. It persists across individual TC rule operations until NIC teardown, holding rhashtables, counters, recirc ID allocation, mports, filters, default rules, fallback actions, flush state, and an `up` gate.

## Dependencies And Integration Points
Includes Linux flow offload and rhashtable APIs plus driver `net_driver.h` and TC counter definitions. It is shared by TC bindings, representor code, encap actions, conntrack, counters, MAE programming, and EF100 NIC lifecycle.

## Risks And Test Signals
Structure field semantics must stay synchronized with MAE MCDI encoders and `tc.c` parser assumptions. Refcounted table entries require matching release paths. Test signals include successful build across IPv6/no-IPv6 configs, TC rule lifecycle exercising each structure, rhashtable teardown without warnings, recirc IDA returning empty, and default/fallback rules being deconfigured before final struct teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc.h -->
