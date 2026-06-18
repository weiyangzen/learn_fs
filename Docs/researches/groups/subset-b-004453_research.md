# subset-b-004453 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_main.c

## Purpose
`fm10k_main.c` is the central datapath and queueing implementation for the Intel FM10K Ethernet switch host interface driver. It registers the module-wide workqueue and PCI driver, implements NAPI polling, Rx buffer recycling, Tx descriptor construction, checksum/TSO/tunnel offload preparation, interrupt moderation, and queue-vector allocation. It is the bridge between Linux networking packet objects (`sk_buff`, NAPI, netdev queues) and FM10K descriptor rings.

## Important APIs, types, and functions
The module lifecycle is handled by `fm10k_init_module()` and `fm10k_exit_module()`, which allocate/destroy `fm10k_workqueue`, initialize debug support, and register/unregister the PCI driver through `fm10k_register_pci_driver()` and `fm10k_unregister_pci_driver()`.

The Rx path is built around `fm10k_alloc_rx_buffers()`, `fm10k_fetch_rx_buffer()`, `fm10k_add_rx_frag()`, `fm10k_process_skb_fields()`, `fm10k_cleanup_headers()`, and `fm10k_clean_rx_irq()`. These functions manage page-backed buffers, DMA sync/unmap operations, descriptor status bits, checksum/hash metadata, VLAN tag reconstruction, GLORT/macvlan selection, GRO delivery, and per-ring statistics.

The Tx path uses `fm10k_xmit_frame_ring()`, `fm10k_tso()`, `fm10k_tx_csum()`, `fm10k_tx_encap_offload()`, `fm10k_tx_map()`, `fm10k_maybe_stop_tx()`, and `fm10k_clean_tx_irq()`. These functions validate offload eligibility, populate the first descriptor with header/MSS state, map skb head and fragments to DMA descriptors, handle BQL, stop/wake netdev subqueues, reclaim completed descriptors, and detect repeated Tx hangs.

Queueing and interrupt support is implemented by `fm10k_poll()`, `fm10k_update_itr()`, `fm10k_qv_enable()`, `fm10k_set_num_queues()`, `fm10k_alloc_q_vector()`, `fm10k_alloc_q_vectors()`, `fm10k_init_msix_capability()`, `fm10k_assign_rings()`, `fm10k_init_reta()`, `fm10k_init_queueing_scheme()`, and `fm10k_clear_queueing_scheme()`. The key local structures are `struct fm10k_ring`, `struct fm10k_q_vector`, `struct fm10k_ring_container`, `struct fm10k_rx_buffer`, and `struct fm10k_tx_buffer`, all declared in shared driver headers.

## Control flow
On module load, the file creates a per-CPU workqueue, initializes debugfs support, and registers the PCI driver. Runtime packet flow enters through netdev code in `fm10k_netdev.c`, then reaches `fm10k_xmit_frame_ring()` for Tx and `fm10k_poll()` for NAPI Rx/Tx cleanup.

Rx control flow starts when an interrupt schedules NAPI. `fm10k_poll()` first reclaims Tx completions for all Tx rings in the q_vector, then splits the NAPI budget across Rx rings. `fm10k_clean_rx_irq()` replenishes descriptors in batches, checks descriptor writeback status, synchronizes DMA data for CPU access, constructs or extends an skb, handles multi-buffer frames until EOP, drops malformed/error descriptors, fills hash/checksum/VLAN/GLORT metadata, and submits the skb via `napi_gro_receive()`. Incomplete frames remain in `rx_ring->skb` for the next poll.

Tx control flow starts with descriptor counting and queue-space checks. `fm10k_xmit_frame_ring()` records the first Tx buffer, applies TSO if possible, otherwise applies checksum offload or software checksum fallback, and delegates DMA mapping to `fm10k_tx_map()`. `fm10k_tx_map()` writes one or more descriptors, adds RS/INT flags at writeback FIFO boundaries, marks the last descriptor, updates BQL, publishes `next_to_watch` after a write barrier, advances `next_to_use`, and rings the hardware tail when needed. `fm10k_clean_tx_irq()` later observes the EOP descriptor DONE bit, consumes the skb, unmaps all DMA segments, updates statistics, wakes queues when enough descriptors are free, and schedules reset on confirmed hangs.

Queue setup first derives RSS/QoS queue counts, requests MSI-X vectors, allocates q_vectors with embedded ring arrays, maps logical rings to hardware register indexes, and initializes the RETA table. Teardown reverses q_vector and MSI-X allocation.

## State and persistence behavior
The file maintains volatile driver state only; there is no on-disk persistence. Ring progress is tracked by `next_to_use`, `next_to_clean`, `next_to_alloc`, `next_to_watch`, and hardware tail/head registers. Rx page lifetime is tracked in `rx_buffer->page`, `dma`, and `page_offset`; reusable pages are refcounted and synchronized back for DMA. Tx state is tracked through `tx_buffer` DMA lengths, skb pointers, GSO segment counts, and BQL counters.

Persistent across resets only in the driver instance are configuration fields stored on `struct fm10k_intfc`, including queue feature limits, ITR defaults, RETA/RSS key values, and statistics accumulators. Hardware-visible state is pushed through MMIO descriptor registers and queue tail writes; these must be reconstructed after reset by PCI/netdev code.

## Dependencies and integration points
This file depends on Linux networking (`sk_buff`, NAPI, GRO, VLAN, checksum, TSO/GSO, RSS hash APIs), DMA mapping APIs, MSI-X setup through PCI helpers, memory barriers, page recycling helpers, and driver-local macros from `fm10k.h`. It calls into `fm10k_netdev.c` for resource cleanup helpers, into `fm10k_pci.c` for register reads and PCI driver registration, and into debug helpers (`fm10k_dbg_*`). It relies on hardware register and descriptor definitions shared across the fm10k driver.

Integration with macvlan/L2 acceleration occurs on Rx by mapping descriptor DGLORT values to accelerated macvlan devices via RCU-protected `ring->l2_accel`. Tunnel offload integration recognizes VXLAN and NVGRE encapsulation for PF devices and enforces the FM10K tunnel header length limit.

## Risks and edge cases
The most sensitive areas are DMA ordering and ring index consistency. `wmb()`, `dma_rmb()`, `smp_rmb()`, and `smp_mb()` are required to avoid publishing descriptors or consuming writebacks out of order. Rx page reuse must not recycle non-reusable, remote, pfmemalloc, or externally referenced pages. Tx DMA error handling walks backward through partially mapped descriptors; mistakes there would leak DMA mappings or free the wrong skb.

Offload eligibility is narrow: tunnel TSO/checksum only supports specific VXLAN/NVGRE inner protocols and header sizes, and unsupported tunnel TSO disables `NETIF_F_GSO_UDP_TUNNEL`. Queue stopping/waking depends on descriptor accounting and can cause stalls if the threshold logic diverges from hardware progress. Tx hang detection deliberately requires two checks to avoid false positives, but reset scheduling still depends on service work progress.

## Test signals
Useful validation signals include successful module load/unload, PCI probe creating q_vectors and MSI-X entries, `ip link set up/down` without resource leaks, NAPI packet receive with GRO delivery, Tx under fragmented and GSO skb workloads, VLAN tag insertion/stripping behavior, VXLAN/NVGRE offload fallback, queue wake after descriptor pressure, and reset on forced Tx hang. Runtime counters to watch include `alloc_failed`, checksum good/error counts, Rx descriptor error buckets, `restart_queue`, `tx_busy`, per-ring packet/byte counters, and dev logs for DMA map failures or Tx unit hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_mbx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_mbx.c

## Purpose
`fm10k_mbx.c` implements the FM10K mailbox transport used for PF/VF and PF/switch-manager communication. It provides circular FIFO management, mailbox-memory copy helpers, CRC verification, PF/VF connection state handling, switch-manager version negotiation, TLV handler registration, and the exported initialization routines that populate `struct fm10k_mbx_info` operations.

## Important APIs, types, and functions
FIFO primitives include `fm10k_fifo_init()`, `fm10k_fifo_used()`, `fm10k_fifo_unused()`, `fm10k_fifo_head_len()`, `fm10k_fifo_enqueue()`, `fm10k_fifo_head_drop()`, and `fm10k_fifo_drop_all()`. These operate on `struct fm10k_mbx_fifo` and assume power-of-two buffer sizes for mask-based wraparound.

PF/VF mailbox helpers include index arithmetic (`fm10k_mbx_index_len()`, `fm10k_mbx_tail_add/sub()`, `fm10k_mbx_head_add/sub()`), mailbox-memory transfer (`fm10k_mbx_write_copy()`, `fm10k_mbx_read_copy()`, `fm10k_mbx_pull_head()`, `fm10k_mbx_push_tail()`), CRC helpers (`fm10k_crc_16b()`, `fm10k_fifo_crc()`, `fm10k_mbx_update_local_crc()`, `fm10k_mbx_verify_remote_crc()`), and state handlers (`fm10k_mbx_process_connect()`, `fm10k_mbx_process_data()`, `fm10k_mbx_process_disconnect()`, `fm10k_mbx_process_error()`, `fm10k_mbx_process()`).

Switch-manager mailbox support is implemented by `fm10k_sm_mbx_connect()`, `fm10k_sm_mbx_disconnect()`, `fm10k_sm_mbx_validate_fifo_hdr()`, `fm10k_sm_mbx_receive()`, `fm10k_sm_mbx_transmit()`, `fm10k_sm_mbx_process_reset()`, `fm10k_sm_mbx_process_version_1()`, and `fm10k_sm_mbx_process()`. Public initialization is through `fm10k_pfvf_mbx_init()` and `fm10k_sm_mbx_init()`.

## Control flow
Both mailbox variants expose operations through `mbx->ops`. Callers initialize the mailbox, register TLV handlers, connect it, enqueue Tx messages, and periodically process interrupts or polling events.

For PF/VF mailboxes, `connect()` transitions from CLOSED to CONNECT, seeds timeout and CRC state, writes a fake remote disconnect header, enables mailbox interrupts, and publishes a CONNECT header. `process()` reads the remote header, validates type/head/tail/reserved/size fields, dispatches to the type-specific handler, optionally builds an ERROR header, then writes the local header and interrupt bits. DATA processing copies newly advertised remote DWORDs into the Rx FIFO, checks message sizes, verifies CRC over data and header, parses complete TLV messages with `fm10k_tlv_msg_parse()`, advances acknowledgements, pulls Tx FIFO data into mailbox memory, and emits a DATA reply. DISCONNECT and ERROR paths reset work, drain or drop pending FIFO contents, and move toward CONNECT or CLOSED depending on state.

For PF/switch-manager mailboxes, the header layout carries local tail, version, remote head, and error fields rather than PF/VF message type/CRC fields. `connect()` starts version negotiation; version 0 is reset, version 1 is active. `process()` validates FIFO offsets and version, handles remote error flags, processes reset or version-1 data, aligns receive head to message boundaries, transmits only whole TLV messages, and sends connect/data headers reflecting local state.

## State and persistence behavior
All mailbox state is in `struct fm10k_mbx_info`: operation table, handler table, Tx/Rx FIFOs, timeout/delay, MMIO register offsets, current header/lock bits, max message size, mailbox memory length, local tail and remote head indexes, in-flight lengths (`tail_len`, `head_len`), pushed/pulled partial-message counts, local/remote CRC or SM version values, current state, last test result, and detailed counters. It is runtime state only and is reinitialized on reset or reconnect.

The Tx FIFO persists queued TLV messages until acknowledged by the remote head; completed messages are dropped from the FIFO and counted. Oversized messages can be dropped when the remote announces a smaller maximum size. The Rx FIFO keeps pushed partial data until a complete TLV message is available, then parsing drops it. Error/reset paths deliberately discard in-progress work to resynchronize both endpoints.

## Dependencies and integration points
The implementation depends on register accessors `fm10k_read_reg()`/`fm10k_write_reg()`, TLV parsing and handler metadata from `fm10k_tlv.h`, hardware type information from `fm10k_type.h`, mailbox register definitions from `fm10k_mbx.h`, and microsecond delays for bounded drain/connect loops. It is used by PCI interrupt handling, MAC/VLAN request submission, VF management, and host-state monitoring code.

`fm10k_pfvf_mbx_init()` selects VF or PF mailbox registers based on `hw->mac.type` and VF id, while `fm10k_sm_mbx_init()` binds to the PF global switch-manager mailbox. Handler registration validates ascending message IDs, ascending attribute IDs, non-null callbacks, result-array bounds, and terminators before assigning `mbx->msg_data`.

## Risks and edge cases
Mailbox correctness depends on strict head/tail arithmetic, avoidance of reserved index values, and alignment to complete TLV message boundaries. A bad remote header can otherwise make the local side read stale mailbox memory or overrun FIFO capacity. CRC handling in the PF/VF path is a major corruption guard; mismatches force error response and reconnect. The switch-manager path lacks the same CRC field and relies on header validation and version/error negotiation.

Timeout behavior is intentionally conservative but can silently drop queued Tx data when reconnecting or shrinking `max_size`. `fm10k_mbx_enqueue_tx()` returns `0` even after FIFO enqueue failure after recording `tx_busy` and clearing timeout, so callers must rely on mailbox state/counters rather than the return value alone for every delivery failure. Handler-table validation is important because the TLV parser assumes sorted metadata and bounded result indexes.

## Test signals
Test signals include successful PF/VF mailbox connect/open/disconnect cycles, SM version-1 negotiation, TLV test-message handling, expected reset on malformed head/tail/reserved/size/CRC cases, no FIFO overflow when the remote stops acknowledging, and recovery after remote ERROR or RESET headers. Counters such as `tx_busy`, `tx_dropped`, `tx_messages`, `rx_messages`, `rx_parse_err`, `tx_mbmem_pulled`, and `rx_mbmem_pushed` should move predictably during stress tests. Fault injection should verify that oversized messages, bad handler tables, and full FIFOs do not corrupt mailbox state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_mbx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_mbx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_mbx.h

## Purpose
`fm10k_mbx.h` defines the mailbox ABI used by the fm10k driver. It describes PF/VF mailbox registers, VF mailbox registers, switch-manager FIFO layout, header field encodings, mailbox states, error codes, buffer sizing, operation callbacks, FIFO state, and the exported initialization prototypes.

## Important APIs, types, and functions
The file defines register macros such as `FM10K_MBMEM()`, `FM10K_MBMEM_VF()`, `FM10K_MBMEM_SM()`, `FM10K_MBMEM_PF()`, `FM10K_MBX()`, `FM10K_MBICR()`, `FM10K_GMBX`, `FM10K_VFMBX`, and `FM10K_VFMBMEM()`. It also defines mailbox interrupt/control bits including `FM10K_MBX_REQ`, `FM10K_MBX_ACK`, request/ack interrupt bits, interrupt enable/disable bits, and global request/ack interrupt bits.

The key type definitions are `enum fm10k_mbx_state`, `enum fm10k_msg_type`, `struct fm10k_mbx_ops`, `struct fm10k_mbx_fifo`, and `struct fm10k_mbx_info`. `struct fm10k_mbx_ops` is the driver-facing operation table for connect, disconnect, readiness checks, enqueue, process, and handler registration. `struct fm10k_mbx_info` is the complete runtime state container used by `fm10k_mbx.c`.

Header field helpers `FM10K_MSG_HDR_FIELD_SET()` and `FM10K_MSG_HDR_FIELD_GET()` encode and decode PF/VF and SM mailbox header fields. Exported initialization prototypes are `fm10k_pfvf_mbx_init()` and `fm10k_sm_mbx_init()`.

## Control flow
This header does not execute code, but it defines the control contract followed by `fm10k_mbx.c`. The PF/VF state machine is documented as CLOSED -> CONNECT -> OPEN -> DISCONNECT -> CLOSED, with transitions caused by local `connect()`/`disconnect()` calls and remote CONNECT, DATA, DISCONNECT, or ERROR headers. The header format carries type, tail, head, reserved bits, and either CRC, connect size, or error number.

The switch-manager contract defines a pair of hardware FIFOs with a header containing local tail, version, remote head, and error. Version 0 represents reset/negotiation, and `FM10K_SM_MBX_VERSION` represents the supported active protocol.

## State and persistence behavior
The header codifies volatile runtime state rather than durable state. `struct fm10k_mbx_info` stores FIFO buffers, indexes, state, CRC/version fields, timeout configuration, last test result, message counters, and a fixed in-struct buffer sized by `FM10K_MBX_BUFFER_SIZE`. This state is recreated during mailbox initialization and reset flows.

Mailbox buffer sizing constants define capacity and message limits: Tx FIFO is 512 DWORDs, Rx FIFO is 128 DWORDs, and maximum message size is constrained by both. VF mailbox memory size and MTU are smaller (`FM10K_VFMBMEM_LEN`, `FM10K_VFMBX_MSG_MTU`) and influence connect-size validation.

## Dependencies and integration points
The header includes `fm10k_type.h` and `fm10k_tlv.h`, so it is tied to hardware type declarations and TLV message handling. It is included by common hardware code and mailbox implementation code, and its operation table is consumed by PCI, netdev, IOV, and MAC/VLAN paths through `hw->mbx.ops`.

The error-code range is intentionally outside common Linux errno values, using visible `0xFE**` encodings when embedded in mailbox messages. This makes local software errors and remote mailbox protocol errors share a compact transport representation.

## Risks and edge cases
Changing any shift, size, register, or buffer constant would affect the hardware ABI. The code relies on FIFO sizes being powers of two for mask arithmetic, and on invalid PF/VF mailbox index values 0 and all-ones being reserved. The documented state machine matters because the implementation intentionally ignores or resets on some messages depending on state.

The SM FIFO length is derived from the XOR distance between PF and SM mailbox memory regions; mistakes in these constants could make the SM path overwrite or read from the wrong hardware mailbox area. Error-code collisions with Linux errno values are avoided by convention, so new errors should stay inside the documented mailbox range.

## Test signals
Useful validation includes compile-time coverage of all users after header changes, mailbox connect/data/disconnect cycles for both PF/VF and SM paths, tests of `FIELD_SET`/`FIELD_GET` round trips for all defined fields, and protocol fault tests for reserved indexes, reserved bits, invalid sizes, unsupported SM versions, and expected error-code propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_mbx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_netdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_netdev.c

## Purpose
`fm10k_netdev.c` implements Linux `net_device` integration for the fm10k driver. It allocates and frees descriptor resources, opens and closes the interface, prepares outbound skbs for the ring transmit path, handles netdev VLAN/MAC/multicast/promiscuous changes, restores and resets Rx filter state, exposes statistics and traffic-class setup, manages macvlan L2 forwarding offload, checks offload features, and allocates/configures the netdev instance.

## Important APIs, types, and functions
Resource management is provided by `fm10k_setup_tx_resources()`, `fm10k_setup_rx_resources()`, `fm10k_free_tx_resources()`, `fm10k_free_rx_resources()`, `fm10k_clean_all_tx_rings()`, `fm10k_clean_all_rx_rings()`, and `fm10k_unmap_and_free_tx_resource()`.

Netdev lifecycle and transmit entry points are `fm10k_open()`, `fm10k_close()`, `fm10k_xmit_frame()`, and `fm10k_tx_timeout()`. Filter and address management use `fm10k_queue_vlan_request()`, `fm10k_queue_mac_request()`, `fm10k_clear_macvlan_queue()`, `fm10k_update_vid()`, `fm10k_set_mac()`, `fm10k_set_rx_mode()`, `fm10k_restore_rx_state()`, and `fm10k_reset_rx_state()`.

Other important APIs include `fm10k_get_stats64()`, `fm10k_setup_tc()`, `__fm10k_setup_tc()`, `fm10k_dfwd_add_station()`, `fm10k_dfwd_del_station()`, `fm10k_features_check()`, `fm10k_alloc_netdev()`, and the `fm10k_netdev_ops` table. The file also defines `fm10k_udp_tunnels` and `fm10k_udp_tunnel_sync()` for VXLAN/Geneve port tracking.

## Control flow
Opening the interface allocates all Tx/Rx descriptor rings, requests queue-vector IRQs, computes GLORT range assignment, publishes actual Tx/Rx queue counts to the stack, and calls `fm10k_up()` in the PCI layer to program hardware and start traffic. Closing calls `fm10k_down()`, frees queue-vector IRQs, and releases Tx/Rx resources.

Transmit begins in `fm10k_xmit_frame()`. It handles inline 802.1Q headers by converting them to hardware-accelerated VLAN tags, pads very small packets to the hardware minimum, normalizes an out-of-range queue mapping, and delegates descriptor construction to `fm10k_xmit_frame_ring()` in `fm10k_main.c`.

VLAN/MAC state changes are queued rather than synchronously blasted to hardware. `fm10k_queue_vlan_request()` and `fm10k_queue_mac_request()` allocate `struct fm10k_macvlan_request` entries under `macvlan_lock` and schedule `macvlan_task` in `fm10k_pci.c`. `fm10k_update_vid()` updates the active VLAN bitmap, adjusts per-Rx-ring default VLAN suppression, and, when running, queues VLAN and MAC updates for the base interface plus L2-accelerated macvlan stations. `fm10k_set_rx_mode()` converts netdev flags into FM10K xcast mode, queues all-VLAN changes for promiscuous transitions, updates hardware xcast mode when the host mailbox is ready, and syncs unicast/multicast lists.

Rx state restoration after reset reenables the logical port, requeues VLAN/MAC filters for active VLANs and L2 accel stations, restores xcast mode and tunnel configuration, and synchronizes address lists. Resetting Rx state waits for pending MAC/VLAN work to finish, clears queued requests, disables the logical port, and clears netdev address-sync flags.

## State and persistence behavior
This file maintains runtime state in `struct fm10k_intfc`: active VLAN bitmap, GLORT base/count, default/current VID state, xcast mode, L2 acceleration table, queued MAC/VLAN requests, VXLAN/Geneve port values, ring counts, and feature flags. Descriptor memory is allocated with `dma_alloc_coherent()` and software ring metadata with `vzalloc()`, then freed on close, reset, or error unwind.

MAC/VLAN requests persist in memory until the delayed `macvlan_task` submits them through mailbox operations or `fm10k_clear_macvlan_queue()` cancels them. L2 forwarding offload state is RCU-protected because Rx rings dereference it during packet delivery. Statistics returned to the stack are accumulated from per-ring counters with `u64_stats_fetch_begin/retry` so 32-bit readers see consistent values.

## Dependencies and integration points
The file depends on Linux netdev, VLAN, UDP tunnel, DMA coherent allocation, vmalloc, macvlan, multicast/unicast address sync, mqprio traffic-class, and stats APIs. It integrates with `fm10k_main.c` for descriptor datapath functions, with `fm10k_pci.c` for hardware up/down, IRQs, mailbox IRQs, and macvlan task execution, with hardware ops through `hw->mac.ops`, with IOV ndo handlers for VF configuration, and with ethtool setup.

Tunnel integration supports one VXLAN and one Geneve UDP port in `udp_tunnel_nic_info`; PF-only tunnel registers are restored after reset. L2 forwarding acceleration integrates with macvlan destination-filter capability and DGLORT mapping.

## Risks and edge cases
Resource unwind paths must free partially allocated rings in reverse order and avoid double-freeing descriptor memory. `fm10k_xmit_frame()` mutates skbs to convert inline VLAN headers; failure paths must drop safely after `skb_share_check()`, `pskb_may_pull()`, or `skb_cow_head()`. VLAN override mode restricts VLAN additions and suppresses some removal requests.

MAC/VLAN queue processing is asynchronous, so reset/down paths must stop or drain the delayed work before clearing state. `fm10k_clear_macvlan_queue()` has subtle filtering behavior: MAC requests are GLORT-specific, while VLAN requests are removed only when the `vlans` parameter allows it. L2 acceleration grows the table under RCU; incorrect assignment could leave Rx rings pointing to freed state. Traffic-class setup closes and reopens the device and can detach the netdev on failure.

## Test signals
Validation should cover open/close error unwinds, ring allocation failures, transmit with inline VLAN tags, tiny packet padding, Tx timeout false-positive backoff vs real reset, VLAN add/remove with default VLAN and override cases, promiscuous/allmulti transitions, MAC address changes while up and down, address-list sync/unsync, reset-time Rx state replay, tunnel port add/delete restore, mqprio setup for PF vs VF, and macvlan L2 offload add/remove under traffic. Useful runtime signals include active VLAN bitmap changes, queued MAC/VLAN list length, xcast mode, GLORT mappings, stats64 totals, and mailbox readiness gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_pci.c

## Purpose
`fm10k_pci.c` implements PCI driver binding and the hardware lifecycle for fm10k devices. It contains PCI IDs, MMIO/config-space accessors, service and MAC/VLAN work scheduling, reset and detach recovery, watchdog/statistics subtasks, hardware Tx/Rx ring programming, MSI-X interrupt request/free logic, mailbox IRQ handlers and TLV handlers, interface up/down sequencing, software initialization, PCI probe/remove, power management, PCI error recovery, SR-IOV hooks, and PCI driver registration.

## Important APIs, types, and functions
PCI binding is defined by `fm10k_pci_tbl`, `fm10k_driver`, `fm10k_register_pci_driver()`, and `fm10k_unregister_pci_driver()`. Register access uses `fm10k_read_pci_cfg_word()` and `fm10k_read_reg()`, both of which handle surprise removal indicators.

Work and reset orchestration is handled by `fm10k_service_event_schedule()`, `fm10k_service_task()`, `fm10k_macvlan_schedule()`, `fm10k_macvlan_task()`, `fm10k_prepare_for_reset()`, `fm10k_handle_reset()`, `fm10k_detach_subtask()`, `fm10k_reset_subtask()`, and watchdog helpers for host state, stats, Tx flushing, and hang checks.

Hardware programming uses `fm10k_configure_tx_ring()`, `fm10k_enable_tx_ring()`, `fm10k_configure_tx()`, `fm10k_configure_rx_ring()`, `fm10k_update_rx_drop_en()`, `fm10k_configure_dglort()`, `fm10k_configure_rx()`, `fm10k_up()`, and `fm10k_down()`. Interrupt and mailbox handling use `fm10k_mbx_request_irq()`, `fm10k_mbx_free_irq()`, `fm10k_qv_request_irq()`, `fm10k_qv_free_irq()`, `fm10k_msix_clean_rings()`, `fm10k_msix_mbx_vf()`, and `fm10k_msix_mbx_pf()`.

Probe/remove and platform integration are provided by `fm10k_sw_init()`, `fm10k_probe()`, `fm10k_remove()`, `fm10k_suspend()`, `fm10k_resume()`, `fm10k_io_error_detected()`, `fm10k_io_slot_reset()`, `fm10k_io_resume()`, `fm10k_io_reset_prepare()`, and `fm10k_io_reset_done()`.

## Control flow
Probe validates PCI error state, enables memory access, sets a 48-bit or 32-bit coherent DMA mask, claims BARs, enables bus mastering, allocates a netdev, maps BAR0, initializes hardware/software state, initializes queueing and mailbox IRQs, confirms hardware readiness, registers the netdev, starts the service timer/work, logs link status/MAC, configures SR-IOV, and schedules initial service work. Error unwinds release mailbox IRQs, queueing, debugfs, mappings, netdev, BARs, and the PCI device in reverse order.

Service work is the long-running control loop. The timer schedules `fm10k_service_task()`, which checks surprise detach/recovery, processes upstream and downstream mailboxes, handles requested resets, updates link carrier based on host readiness, updates stats once per second, flushes Tx by reset if link is down with pending DMA, and periodically arms Tx hang detection plus interrupt strobes.

Reset preparation stops MAC/VLAN work, takes rtnl, suspends SR-IOV, closes the netdev if running, frees mailbox IRQs and queueing scheme, records a reset delay, and releases rtnl. Reset handling restores bus mastering, resets and initializes hardware, rebuilds queueing, requests mailbox IRQs, checks hardware, updates VF MAC/VLAN feature state, reopens the netdev if it was running, resumes SR-IOV, resumes MAC/VLAN work, and clears `__FM10K_RESETTING`.

`fm10k_up()` starts hardware DMA, programs Tx/Rx descriptor rings, programs interrupt moderation, enables NAPI, restores Rx filters, starts netdev queues, and kicks the service timer. `fm10k_down()` stops carrier/queues, resets Rx filters, disables NAPI, captures stats, waits out concurrent stats updates, attempts graceful Tx DMA drain, stops hardware, and cleans all rings.

Mailbox IRQ flow differs for PF and VF. VF mailbox IRQs process the upstream mailbox, mark host-state refresh, schedule service work, and reenable the VF ITR. PF mailbox IRQs read/ack EICR, report hardware faults, reset drop-on-empty queues after max-hold-time events, process the switch-manager mailbox and VF events under mailbox lock, handle switch ready/not-ready transitions, schedule service work, and reenable mailbox ITR.

## State and persistence behavior
PCI state lives in `struct fm10k_intfc` and `struct fm10k_hw`: mapped MMIO addresses, PCI device pointer, netdev pointer, service timer/work, delayed MAC/VLAN work, interface flags/state bits, host readiness, link-down debounce time, reset timestamps, hardware statistics, queue/ring arrays, MSI-X entries, mailbox state, RSS/RETA state, and SR-IOV data. The state is runtime-only and reconstructed on reset, resume, error recovery, and probe.

The service scheduler uses bit flags (`__FM10K_SERVICE_DISABLE`, `__FM10K_SERVICE_SCHED`, `__FM10K_SERVICE_REQUEST`) to avoid lost work while coalescing requests. The MAC/VLAN scheduler uses analogous bits to throttle mailbox submissions. Surprise removal is represented by clearing `hw->hw_addr` and detaching the netdev; recovery restores it from `uc_addr` and runs the reset path.

Hardware persistent effects are MMIO register writes for descriptor base/len/head/tail, interrupt mapping/masking, DGLORT/RSS/RETA, mailbox interrupt causes, and logical port/VF state through hardware ops. These are replayed after reset rather than stored on disk.

## Dependencies and integration points
The file depends on the Linux PCI, MSI-X, interrupt, PM, PCI error recovery, DMA, timer/workqueue, rtnl, netdev carrier/queue, NAPI, and SR-IOV frameworks. It integrates with `fm10k_main.c` for queueing scheme and datapath cleanup, `fm10k_netdev.c` for open/close/filter state, `fm10k_mbx.c` for mailbox ops, IOV support for VF lifecycle and mailbox events, DCB support for priority mapping, debugfs hooks, and hardware-specific MAC/IOV operation tables from `fm10k_info`.

The PCI driver registration is invoked by module init in `fm10k_main.c`. `fm10k_mbx_request_irq()` binds mailbox TLV handlers for VF or PF mode, so mailbox message handling is coupled to PCI role.

## Risks and edge cases
Reset and remove paths have high concurrency risk: service work, MAC/VLAN delayed work, netdev open/close, mailbox IRQs, SR-IOV, and PM/error recovery all interact. The code uses state bits, rtnl, work cancellation, mailbox spinlocks, and detach checks to serialize key paths. A missed bit clear can suppress future service or MAC/VLAN processing.

Surprise PCIe removal is handled by detecting all-ones MMIO reads, clearing `hw_addr`, detaching the netdev, and later probing `uc_addr` for recovery; any register access path that bypasses `fm10k_read_reg()` could violate that model. Tx DMA drain can time out, leading to warning and forced stop. PF fault handling resets VF resources and reconnects VF mailboxes, but malicious or repeatedly faulty VFs may require administrator intervention.

Mailbox IRQ setup must register sorted TLV handlers before connecting. `fm10k_mbx_free_irq()` disconnects mailbox before masking/freeing IRQ, so callers must avoid holding locks that the disconnect process may need. Traffic-class or reset failures can leave the netdev detached and require user-visible recovery.

## Test signals
Validation should include PCI probe/remove, module unload, open/close, reset request via Tx timeout, mailbox IRQ activity for PF and VF, SR-IOV enable/disable and VF FLR, suspend/resume, PCI AER slot reset, manual function reset, surprise-removal simulation, host ready/not-ready link transitions, DGLORT/RSS programming after reset, max-hold-time/drop-on-empty recovery, and service/MACVLAN rescheduling under mailbox pressure. Logs to watch include PCIe link lost/restored, reset failures, Tx DMA drain warnings, mailbox request IRQ failures, logical port map failures, fault reports, and invalid MAC/VLAN reset triggers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_pci.c -->
