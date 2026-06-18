# Research: subset-b-004439

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_qp_ctxt.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_qp_ctxt.h

## Purpose
Defines the firmware-visible queue-pair context records for the original Huawei HiNIC driver. The file is a hardware contract header: it describes how SQ and RQ context blocks are packed before being sent through the command-queue path to initialize, clean, or reconfigure queue resources.

## Important APIs, Types, And Constants
The main exported types are `struct hinic_qp_ctxt_header`, `struct hinic_sq_ctxt`, `struct hinic_rq_ctxt`, `struct hinic_clean_queue_ctxt`, `struct hinic_sq_ctxt_block`, and `struct hinic_rq_ctxt_block`. `enum hinic_qp_ctxt_type` selects SQ or RQ contexts. Bitfield helpers such as `HINIC_SQ_CTXT_CEQ_ATTR_SET`, `HINIC_RQ_CTXT_PI_SET`, and `HINIC_*_WQ_BLOCK_SET` encode queue IDs, completion-event enable bits, producer/consumer indexes, page PFNs, and WQ block PFNs. `HINIC_SQ_CTXT_SIZE`, `HINIC_RQ_CTXT_SIZE`, and `HINIC_Q_CTXT_MAX` bound how many queue contexts fit in a `HINIC_CMDQ_BUF_SIZE` command buffer.

## Control Flow And State
This header has no executable flow; callers populate the structures and send them to firmware. The state represented is persistent device queue context: queue type, queue count, queue address offset, CI/PI positions, wrap bits, completion-event settings, WQ page addresses, prefetch cache hints, and physical WQ block addresses. PFNs are derived from DMA addresses with `HINIC_WQ_PAGE_PFN()` and `HINIC_WQ_BLOCK_PFN()`.

## Dependencies And Integration Points
It depends on `linux/types.h` and `hinic_hw_cmdq.h` for command-buffer sizing. It is coupled to queue allocation in `hinic_hw_wq.c` and queue-pair programming in `hinic_hw_qp.c`; those layers must supply DMA addresses and indices in the layout expected here. The big-endian/little-endian conversion policy is enforced by callers that marshal these records for firmware.

## Risks And Test Signals
The central risk is silent firmware misconfiguration from a wrong shift, mask, PFN granularity, or structure size. Tests/signals should include queue bring-up on SQ/RQ counts near `HINIC_Q_CTXT_MAX`, traffic after interface reopen, reset or queue-clean flows, and hardware error logs for invalid command buffers. Sparse or build checks help catch type regressions, but only device or emulator testing validates the packed ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_qp_ctxt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_wq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_wq.c

## Purpose
Implements the original HiNIC work-queue allocator and WQE access layer. It owns DMA page allocation for normal SQ/RQ work queues and command queues, tracks blocks inside shared WQ-set pages, and provides producer/consumer helpers that hide ring wraparound and multi-page WQE layout.

## Important APIs And Functions
Public allocation APIs are `hinic_wqs_alloc()`, `hinic_wqs_free()`, `hinic_wq_allocate()`, `hinic_wq_free()`, `hinic_wqs_cmdq_alloc()`, and `hinic_wqs_cmdq_free()`. WQE access APIs are `hinic_get_wqe()`, `hinic_return_wqe()`, `hinic_put_wqe()`, `hinic_read_wqe()`, `hinic_read_wqe_direct()`, and `hinic_write_wqe()`. Internal helpers allocate coherent pages (`queue_alloc_page()`, `alloc_wq_pages()`), manage the free block ring (`wqs_next_block()`, `wqs_return_block()`), and copy wrapped WQEs through shadow buffers (`copy_wqe_to_shadow()`, `copy_wqe_from_shadow()`).

## Control Flow And State
`hinic_wqs_alloc()` aligns the requested queue count to four blocks per page, allocates DMA pages plus VM shadow arrays, initializes the free-block ring, and exposes blocks to `hinic_wq_allocate()`. Each `hinic_wq` stores DMA block address, shadow page addresses, queue depth, WQEBB size, page sizing shifts, and atomics for `prod_idx`, `cons_idx`, and free-space `delta`. `hinic_get_wqe()` reserves WQEBBs by subtracting `delta`, advances `prod_idx`, and returns either a direct WQE pointer or a per-page `shadow_wqe` when the WQE crosses a page/ring boundary. `hinic_write_wqe()` copies such shadow WQEs back to DMA memory. Consumers use `hinic_read_wqe()` and release space with `hinic_put_wqe()`.

## Dependencies And Integration Points
The file depends on PCI coherent DMA, vmalloc, atomics, semaphores, `hinic_hw_if`, `hinic_hw_wqe`, and command-queue constants. `hinic_hw_qp.c`, Rx, Tx, and command-queue code rely on its ring accounting and DMA address tables. Hardware consumes the big-endian page-address table written here.

## Risks And Test Signals
High-risk areas are off-by-one ring wrap logic, power-of-two assumptions, mismatched WQE size accounting, and shadow-copy handling when a WQE straddles page boundaries. Stress tests should exercise full rings, fragmented Tx WQEs, jumbo Rx, command queues, repeated interface up/down, DMA allocation failures, and concurrency between Tx submission and completion. KASAN/KCSAN and DMA debug are useful signals for stale shadow pointers, leaks, or invalid unmaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_wq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_wq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_wq.h

## Purpose
Declares the original HiNIC work-queue data structures and public APIs used by command queues, SQ/RQ queue-pair setup, Tx, and Rx. It is the driver-internal interface for allocating queue memory and producing or consuming hardware WQEs.

## Important APIs And Types
`struct hinic_wq` describes a single hardware work queue: backing block location inside a WQ set, WQEBB and page sizing, DMA block address, page-address arrays, shadow WQE storage, ring atomics, and index mask. `struct hinic_wqs` owns a pool of WQ blocks over one or more coherent pages, with page-address arrays and a semaphore-protected free-block ring. `struct hinic_cmdq_pages` is the command-queue-specific page container. Public functions cover WQS lifecycle, individual WQ lifecycle, command-queue WQS allocation, WQE reservation/return/read/write, and direct reads by consumer index.

## Control Flow And State
The header does not implement behavior, but it exposes the state machine used by `hinic_hw_wq.c`: `prod_idx` reserves WQEBBs for new WQEs, `cons_idx` releases completed WQEs, `delta` tracks available WQEBBs, and `mask` implements power-of-two ring wrapping. `shadow_wqe` and `shadow_idx` persist temporary copies of WQEs that cannot be represented as a single contiguous DMA-memory span.

## Dependencies And Integration Points
It includes Linux types, semaphores, atomics, `hinic_hw_if.h`, and `hinic_hw_wqe.h`. Higher layers use `struct hinic_hw_wqe` unions from `hinic_hw_wqe.h` while queue-pair code maps `hinic_wq` addresses into firmware queue contexts. Rx and Tx code consume this API through `hinic_hw_qp` wrappers.

## Risks And Test Signals
The exposed fields are tightly coupled to queue implementation; callers that manipulate atomics or address arrays directly can break ring invariants. API tests should check allocation failure unwinding, power-of-two validation, WQE wraparound, and queue depths at boundary values. Integration signals are successful interface open/close, no DMA-debug complaints, and stable Tx/Rx under ring pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_wq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_wqe.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_wqe.h

## Purpose
Defines hardware WQE, CQE, command-queue, SQ, and RQ wire formats for the original HiNIC driver. It is an ABI header shared by queue allocation, Tx/Rx datapaths, and firmware command submission.

## Important APIs, Types, And Constants
The file provides bitfield setters/getters for command queue control/header words, SQ control and task offload words, RQ CQE status/length/offload fields, RSS type bits, VLAN extraction, and packet/LRO decoding. Key sizes are `HINIC_SQ_WQE_MAX_SIZE`, `HINIC_RQ_WQE_SIZE`, `HINIC_MAX_SQ_BUFDESCS`, and `HINIC_SQ_WQE_SIZE(nr_sges)`. Important structs include `hinic_cmdq_wqe_scmd`, `hinic_cmdq_wqe_lcmd`, `hinic_sq_wqe`, `hinic_rq_cqe`, `hinic_rq_wqe`, and the top-level `union` in `struct hinic_hw_wqe`.

## Control Flow And State
There is no executable flow; state is encoded in WQE/CQE fields consumed by hardware and the datapath. Tx fills SQ control/task/buffer descriptors for checksum, TSO, tunnel, VLAN, and scatter-gather DMA. Rx reads RQ CQE status bits for RXDONE, checksum errors, LRO packet count, VLAN tag, packet type, and SGE length. Command-queue code uses the command WQE structs for short and long commands and either direct or SGE completion response.

## Dependencies And Integration Points
The header depends on `hinic_common.h` for SGE layout and endian helpers. It is directly used by `hinic_tx.c`, `hinic_rx.c`, `hinic_hw_wq.c`, `hinic_hw_cmdq.c`, and queue-pair helpers. Its definitions must match firmware and hardware documentation exactly.

## Risks And Test Signals
Risk concentrates in bitfield definitions, endian conversions, and size/alignment of hardware structs. Incorrect masks can manifest as broken offloads, corrupt DMA descriptors, false checksum errors, missing completions, or command timeouts. Test signals include checksum/TSO/tunnel/VLAN/LRO traffic, RSS configuration, command-queue direct and SGE responses, and hardware counter or dmesg errors under mixed offload workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_wqe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_main.c

## Purpose
Provides the original HiNIC PCI netdevice driver entry point. It handles module parameters, PCI probe/remove/shutdown, netdevice allocation and registration, feature initialization, open/close sequencing, Rx/Tx queue lifecycle, RSS setup, link events, VLAN/MAC netdev operations, stats, and SR-IOV netdev operation wiring.

## Important APIs And Functions
Driver lifecycle is implemented by `hinic_probe()`, `nic_dev_init()`, `hinic_remove()`, `hinic_shutdown()`, `hinic_module_init()`, and `hinic_module_exit()`. Runtime netdev operations include `hinic_open()`, `hinic_close()`, `hinic_change_mtu()`, `hinic_set_mac_addr()`, VLAN add/remove callbacks, `hinic_set_rx_mode()`, `hinic_tx_timeout()`, `hinic_get_stats64()`, `hinic_fix_features()`, and `hinic_set_features()`. Queue helpers are `create_txqs()`, `create_rxqs()`, `free_txqs()`, `free_rxqs()`, plus RSS helpers such as `hinic_enable_rss()` and `hinic_rss_init()`.

## Control Flow And State
Probe enables PCI, reserves BARs, sets DMA mask, initializes `hinic_hwdev`, allocates a multiqueue `net_device`, fetches/sets MAC and MTU, registers management event callbacks, applies offload features, initializes interrupt coalescing/debugfs, and registers the netdev. `hinic_open()` brings hardware up, creates Tx then Rx queues, enables RSS, configures queue counts, enables port/function state, samples link state, notifies VFs, sets `HINIC_INTF_UP`, and wakes queues if link is up. `hinic_close()` disables Tx NAPI first, clears interface/link state under `mgmt_lock`, disables port/function state, tears down RSS and queues, and calls hardware ifdown. Persistent driver state lives in `struct hinic_dev`: flags, queue arrays, VLAN bitmap, RSS template, coalescing arrays, workqueue, and SR-IOV info.

## Dependencies And Integration Points
It integrates `hinic_hw_dev`, `hinic_port`, `hinic_tx`, `hinic_rx`, `hinic_debugfs`, `hinic_devlink`, and `hinic_sriov`. The netdev ops differ for PF versus VF; PF exposes VF configuration callbacks. Firmware management callbacks update carrier state and cable/module flags.

## Risks And Test Signals
Risk lies in resource unwinding across many probe/open failure labels, races between link events and close/remove, delayed rx-mode work, RSS template cleanup, and SR-IOV removal coordination. Test signals include probe/remove loops, open/close loops, feature toggles, VLAN/MAC sync, link flap, Tx timeout diagnostics, SR-IOV enable/disable, and fault injection for queue, IRQ, workqueue, and firmware-command failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_port.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_port.c

## Purpose
Implements the original HiNIC port and NIC-configuration command layer. Most functions are thin wrappers that build firmware command structures, send them through management mailbox or command queue paths, validate `status` and response length, and expose configuration/state to main, ethtool, DCB, RSS, SR-IOV, and diagnostics code.

## Important APIs And Functions
MAC/VLAN/MTU/link APIs include `hinic_port_add_mac()`, `hinic_port_del_mac()`, `hinic_port_get_mac()`, `hinic_port_set_mtu()`, `hinic_port_add_vlan()`, `hinic_port_del_vlan()`, `hinic_port_set_rx_mode()`, `hinic_port_link_state()`, `hinic_port_set_state()`, and `hinic_port_set_func_state()`. Offload and queue APIs include `hinic_port_set_tso()`, `hinic_set_rx_csum_offload()`, `hinic_set_rx_vlan_offload()`, `hinic_set_vlan_fliter()`, `hinic_set_max_qnum()`, and `hinic_set_rx_lro_state()`. RSS APIs configure template, indirection, context type, hash engine, and RSS enable. Statistics, link settings, pause/PFC, loopback, LED, management version, and SFP EEPROM/type helpers round out the file.

## Control Flow And State
The common flow is: populate command with `HINIC_HWIF_FUNC_IDX()` or port ID, call `hinic_port_msg_cmd()` or `hinic_cmdq_direct_resp()`, check kernel error, output size, and firmware status, then copy results or return a normalized errno. RSS indirection and context writes allocate a command-queue buffer and program hardware in chunks. Pause/PFC updates also mutate `hwdev->func_to_io.nic_cfg` under `cfg_mutex`; SFP and stats paths copy firmware data into caller buffers.

## Dependencies And Integration Points
This file depends on `hinic_hw_if`, `hinic_hw_dev`, `hinic_port.h`, and `hinic_dev.h`. It is called by `hinic_main.c`, ethtool support, DCB support, SR-IOV, and loopback/LED diagnostics. It bridges the Linux netdev feature model to firmware commands in `HINIC_PORT_CMD_*` and `HINIC_UCODE_CMD_*`.

## Risks And Test Signals
Risks include response-size validation mismatches, unsupported firmware commands, inconsistent PF/VF behavior, endian conversion of RSS tables, and typo-prone command structs. Signals include successful feature toggles, RSS hash/indir round trips, ethtool stats, pause/PFC configuration, SFP EEPROM reads, LED/loopback diagnostics, and dmesg checks for firmware status handling on older firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_port.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_port.h

## Purpose
Declares the original HiNIC port-management ABI structures, enums, constants, and public helper prototypes. It is the interface between the netdevice/ethtool/DCB/SR-IOV layers and firmware management commands for MAC, VLAN, link, offload, RSS, stats, pause, loopback, LED, and SFP operations.

## Important APIs And Types
The header defines command payload structs such as `hinic_port_mac_cmd`, `hinic_port_mtu_cmd`, `hinic_port_vlan_cmd`, `hinic_port_link_cmd`, `hinic_port_cap`, `hinic_tso_config`, `hinic_checksum_offload`, `hinic_lro_config`, RSS structures, stats structures, `hinic_pause_config`, `hinic_set_pfc`, loopback/LED/SFP commands, and firmware update payloads. Enums cover Rx mode bits, port/link/function state, speed, link modes, port type, autoneg, duplex, TSO state, LED mode/type, and link-setting valid bits.

## Control Flow And State
No code executes here; it defines persistent command state and exposes functions implemented in `hinic_port.c` and `hinic_main.c`. The structures generally begin with firmware `status/version/rsvd` fields followed by function ID or port-specific configuration. RSS constants define the 40-byte hash key and 256-entry indirection table sizes. Large stats structs mirror firmware counter blocks.

## Dependencies And Integration Points
It includes Linux ethtool/etherdevice/bitops headers and `hinic_dev.h`. `hinic_main.c`, `hinic_port.c`, `hinic_sriov.c`, and ethtool code include it to share command layouts. Because these layouts cross the firmware boundary, compatibility depends on exact field order and size.

## Risks And Test Signals
Main risks are ABI drift, duplicated constants (`STD_SFP_INFO_MAX_SIZE` appears twice), spelling mistakes that propagate into public helpers such as `hinic_set_vlan_fliter()`, and unsupported commands on older firmware. Test signals are compile coverage, ethtool link/settings/stats/RSS tests, VLAN/MAC operations, offload feature toggles, and firmware-version compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_rx.c

## Purpose
Implements the original HiNIC Rx datapath: allocating and replenishing receive buffers, handling Rx MSI-X interrupts with NAPI, processing CQEs, checksum/VLAN/LRO metadata, building jumbo packets, updating per-queue stats, and cleaning Rx resources.

## Important APIs And Functions
Externally visible functions are `hinic_rxq_get_stats()`, `hinic_init_rxq()`, and `hinic_clean_rxq()`. Core internals include `rx_alloc_skb()`, `rx_alloc_pkts()`, `free_all_rx_skbs()`, `rx_recv_jumbo_pkt()`, `rxq_recv()`, `rx_poll()`, `rx_irq()`, `rx_request_irq()`, and `rx_free_irq()`. `rx_csum()` decodes checksum status and `hinic_copy_lp_data()` supports loopback test capture.

## Control Flow And State
Initialization sets netdev/RQ pointers, buffer size, stats sync, IRQ name, preposts receive WQEs with DMA-mapped SKBs, then configures NAPI, interrupt coalescing, IRQ, and affinity. On interrupt, the handler disables MSI-X for PFs, records interrupt count, and schedules NAPI. `rxq_recv()` reads completed RQ WQEs until budget or LRO replenish threshold, orders DMA reads, unmaps the buffer, applies checksum state, grows the skb or chains jumbo fragments, releases consumed WQEs, handles VLAN tag insertion, feeds loopback capture, records queue and protocol, and submits to GRO. It then replenishes buffers when the free count exceeds a threshold and updates stats under `u64_stats_sync`.

## Dependencies And Integration Points
It depends on `hinic_hw_qp` wrappers, `hinic_hw_wqe` CQE helpers, netdev/NAPI/SKB/DMA APIs, and `hinic_dev` runtime settings such as Rx weight and coalescing. It is created and destroyed by `hinic_main.c`.

## Risks And Test Signals
Risks include DMA ordering mistakes, skb leak/unmap imbalance, jumbo fragment list errors, LRO byte accounting, checksum false positives, and IRQ/NAPI disable races during close. Test signals include Rx traffic with checksum offload on/off, VLAN receive offload, jumbo frames, LRO traffic, low-memory Rx replenish failures, IRQ affinity/coalescing behavior, loopback test packets, and clean interface teardown under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_rx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_rx.h

## Purpose
Declares the original HiNIC logical Rx queue structure, Rx statistics, checksum constants, and public queue lifecycle/stat APIs used by the main driver and ethtool/stat paths.

## Important APIs And Types
`struct hinic_rxq_stats` tracks packets, bytes, generic errors, checksum errors, other errors, allocation failures, and a `u64_stats_sync` seqlock for lockless 64-bit stats reads. `struct hinic_rxq` binds a Linux `net_device` to a hardware `hinic_rq`, stats, IRQ name, buffer sizing, Rx buffer shift, and NAPI instance. Public functions are `hinic_rxq_get_stats()`, `hinic_init_rxq()`, and `hinic_clean_rxq()`. Constants describe hardware checksum-offload masks and special error bits.

## Control Flow And State
The header exposes the state that `hinic_rx.c` manages. Queue lifetime begins with `hinic_init_rxq()`, which initializes stats, preposts buffers, and requests IRQ/NAPI. Runtime state is split between hardware RQ saved SKBs/CQEs and `struct hinic_rxq` metadata. `hinic_clean_rxq()` disables IRQ/NAPI and frees outstanding SKBs.

## Dependencies And Integration Points
It includes Linux netdevice, interrupt, and stats synchronization headers plus `hinic_hw_qp.h`. `hinic_main.c` allocates an array of these objects per netdev; `hinic_rx.c` owns their behavior; stats aggregation reads them through `hinic_rxq_get_stats()`.

## Risks And Test Signals
Risks are mostly structural: adding stats without updating aggregation or cleaning, changing buffer fields without matching Rx code, or using stats without `u64_stats_sync`. Signals include clean compilation, correct stats under 32-bit and 64-bit builds, Rx queue creation/teardown, and ethtool/netdev stats matching packet traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_sriov.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_sriov.c

## Purpose
Implements original HiNIC SR-IOV support for PF and VF roles. It manages VF lifecycle, PF-side VF policy state, mailbox command validation/dispatch, VF registration, forced link state, VF MAC/VLAN/trust/spoof-check/rate settings, and PCI SR-IOV enable/disable.

## Important APIs And Functions
Netdev VF operations are `hinic_ndo_set_vf_mac()`, `hinic_ndo_set_vf_vlan()`, `hinic_ndo_get_vf_config()`, `hinic_ndo_set_vf_trust()`, `hinic_ndo_set_vf_bw()`, `hinic_ndo_set_vf_spoofchk()`, and `hinic_ndo_set_vf_link_state()`. Lifecycle APIs are `hinic_vf_func_init()`, `hinic_vf_func_free()`, `hinic_pci_sriov_configure()`, and `hinic_pci_sriov_disable()`. Mailbox paths use `nic_pf_mbox_handler()`, `cfg_mbx_pf_proc_vf_msg()`, and command-specific handlers for VF register/unregister, MTU, MAC, and link state.

## Control Flow And State
PF init registers mailbox callbacks, allocates `vf_infos`, and applies the module parameter `set_vf_link_state`. VF init registers with the PF over mailbox. Enabling SR-IOV sets the `HINIC_SRIOV_ENABLE` bit, initializes VF WQ page size, calls `pci_enable_sriov()`, records `sriov_enabled` and `num_vfs`, then clears the state bit. Disabling handles assigned-VF refusal, disables PCI SR-IOV, clears hardware settings and VF state, and resets page sizes. `struct vf_data_storage` persists PF-selected MAC, VLAN/QoS, bandwidth, link force, spoof-check, trust, and registration state. PF mailbox dispatch validates commands and function IDs before either handling locally or forwarding to management firmware.

## Dependencies And Integration Points
It integrates PCI SR-IOV APIs, HiNIC mailbox, management command wrappers in `hinic_port.c`, hardware device capability data, and `hinic_main.c` netdev ops. Link events call `hinic_notify_all_vfs_link_changed()` from the main link handler.

## Risks And Test Signals
Risks include OS-VF versus hardware-VF off-by-one conversions, missing bounds checks, inconsistent indexing in trust/spoof state, stale PF policy after VF reload, mailbox validation gaps, and SR-IOV removal races. Tests should cover enabling/disabling varying VF counts, assigned-VF unload refusal, VF register/unregister, PF-set MAC/VLAN/rate/spoof/trust/link policies, VF driver reload, link flap propagation, and older firmware unsupported-command paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_sriov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_sriov.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_sriov.h

## Purpose
Declares original HiNIC SR-IOV state, VF policy records, mailbox payload structures, VF ID conversion macros, and public SR-IOV/netdev operation hooks.

## Important APIs And Types
`OS_VF_ID_TO_HW()` and `HW_VF_ID_TO_OS()` encode the hardware convention that VF IDs start at 1 while Linux-visible VF indexes start at 0. `enum hinic_sriov_state` defines bit positions for enable, disable, and function removal. `struct hinic_sriov_info` tracks the PF PCI device, hardware device, enable state, VF count, and state bits. `struct vf_data_storage` persists per-VF MAC, VLAN/QoS, bandwidth, forced link, spoof-check, trust, and registration fields. Command payloads include `hinic_register_vf`, `hinic_port_mac_update`, and `hinic_vf_vlan_config`.

## Control Flow And State
This header has no executable control flow, but it defines the state consumed by `hinic_sriov.c`. Public prototypes connect netdev VF ops, link notifications, PCI SR-IOV configuration, and VF function init/free into the rest of the driver.

## Dependencies And Integration Points
It includes `hinic_hw_dev.h` for hardware-device structures and is included by `hinic_main.c` and `hinic_sriov.c`. It also relies on Linux netdevice VF structures through function prototypes.

## Risks And Test Signals
The main risk is incorrect VF ID translation or state-bit interpretation, which can apply PF policy to the wrong VF. Structure layout changes affect mailbox ABI. Test signals include VF policy round trips through `ip link`, VF reload with PF-set MAC/VLAN, link forced/auto behavior, and SR-IOV enable/disable races during PF removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_sriov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_tx.c

## Purpose
Implements the original HiNIC Tx datapath: SKB DMA mapping, SQ WQE construction, checksum/TSO/tunnel/VLAN offload programming, doorbell writes, Tx completion cleanup through NAPI, queue wake logic, stats, and Tx queue lifecycle.

## Important APIs And Functions
Externally visible APIs are `hinic_txq_get_stats()`, `hinic_lb_xmit_frame()`, `hinic_xmit_frame()`, `hinic_init_txq()`, and `hinic_clean_txq()`. Internal helpers include `tx_map_skb()`, `tx_unmap_skb()`, `offload_tso()`, `offload_csum()`, `hinic_tx_offload()`, `free_all_tx_skbs()`, `free_tx_poll()`, `tx_irq()`, and IRQ setup/teardown functions.

## Control Flow And State
Transmit maps skb head and frags into SGEs, reserves an SQ WQE, prepares descriptors, programs offloads, writes the WQE with saved skb metadata, and rings the SQ doorbell unless xmit_more batching delays it. If the ring is full, it stops the subqueue, retries to close the race with completion on another CPU, and returns `NETDEV_TX_BUSY` if still full. Completion NAPI reads hardware CI, compares it with software CI and WQE size, unmaps/free SKBs, advances the SQ consumer, updates stats, and wakes a stopped subqueue when enough WQEBBs are free. Initialization allocates SGE scratch arrays, programs the hardware CI address, sets interrupt coalescing, and requests IRQ.

## Dependencies And Integration Points
It depends on `hinic_hw_qp` SQ helpers, `hinic_hw_wqe` offload bitfields, Linux SKB/DMA/NAPI APIs, `hinic_port` feature configuration, and `hinic_main.c` queue lifecycle. It shares interrupt coalescing settings through `hinic_dev`.

## Risks And Test Signals
Risks include DMA unmap imbalance on partial mapping/offload errors, queue stop/wake races, WQE size miscalculation for fragmented SKBs, offload header parsing bugs for IPv6 extensions and tunnels, and minimum-packet padding behavior. Test signals include TCP/UDP/SCTP checksum, TSO/TSO6, UDP tunnel offloads, VLAN insertion, high-fragment SKBs, ring saturation, Tx timeout diagnostics, loopback xmit, and close under active Tx load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_tx.h

## Purpose
Declares the original HiNIC logical Tx queue structure, Tx statistics, and public Tx datapath/lifecycle APIs used by the netdevice layer.

## Important APIs And Types
`struct hinic_txq_stats` tracks packets, bytes, busy events, wake events, dropped packets, oversized-fragment packet count, and a `u64_stats_sync` guard. `struct hinic_txq` binds a netdevice to a hardware `hinic_sq`, owns stats, maximum SGE count, scratch SGE arrays for mapping and freeing, IRQ name, and NAPI instance. Public functions are `hinic_txq_get_stats()`, `hinic_lb_xmit_frame()`, `hinic_xmit_frame()`, `hinic_init_txq()`, and `hinic_clean_txq()`.

## Control Flow And State
The header exposes state that `hinic_tx.c` manages. Runtime Tx submission uses `sges` as scratch descriptors before writing an SQ WQE, while completion cleanup uses `free_sges` to reconstruct and unmap DMA mappings from completed WQEs. The NAPI instance is used for Tx completion polling rather than Rx packet delivery.

## Dependencies And Integration Points
It includes Linux netdevice, SKB, stats sync, `hinic_common.h`, and `hinic_hw_qp.h`. `hinic_main.c` allocates and initializes one `hinic_txq` per hardware SQ, aggregates stats, and wires `hinic_xmit_frame()` into netdev ops.

## Risks And Test Signals
Risks include mismatched `max_sges` relative to hardware `HINIC_MAX_SQ_BUFDESCS`, stats changes not mirrored in aggregation, and misuse of scratch SGE arrays across concurrent queue contexts. Signals include multi-queue Tx traffic, high-fragment SKBs, stats validation, Tx NAPI enable/disable ordering, and loopback transmit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/Kconfig

## Purpose
Adds the kernel configuration symbol for Huawei third-generation HiNIC adapters. It controls whether the `hinic3` driver is built and documents the supported architecture and module name.

## Important Settings
`config HINIC3` is a tristate option named "Huawei 3rd generation network adapters (HINIC3) support". It depends on little-endian CPUs, `X86 || ARM64 || COMPILE_TEST`, `PCI_MSI`, and `64BIT`. It selects `AUXILIARY_BUS`, `DIMLIB`, and `PAGE_POOL`, signaling that the driver integrates with auxiliary-device infrastructure, dynamic interrupt moderation, and page-pool-backed Rx buffering elsewhere in the hinic3 tree.

## Control Flow And State
Kconfig has no runtime flow, but it gates all object compilation in the hinic3 Makefile. The explicit `!CPU_BIG_ENDIAN` dependency is important because hardware and management structures in this driver are little endian and currently not converted comprehensively.

## Dependencies And Integration Points
The symbol is consumed by the local `Makefile` through `obj-$(CONFIG_HINIC3) += hinic3.o`. Kernel builders and distro configs use this file to expose the driver as built-in, module, or disabled.

## Risks And Test Signals
Risks are mostly build-configuration drift: missing dependencies cause link or runtime failures, while overly strict dependencies reduce test coverage. Test signals include `allmodconfig`, `COMPILE_TEST` on non-target architectures allowed by dependencies, module build/loading, and ensuring selected subsystems are still required by the actual source set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/Makefile

## Purpose
Defines how the third-generation HiNIC driver is built by kbuild. It collects the hinic3 source files into a single `hinic3.o` module or built-in object under `CONFIG_HINIC3`.

## Important Build Entries
`obj-$(CONFIG_HINIC3) += hinic3.o` registers the driver object. `hinic3-objs` lists command queue, common helpers, EQs, ethtool, filtering, hardware config/communication/device/interface, IRQ, low-level device, main, mailbox, management, netdev ops, NIC config and I/O, queue common, RSS, Rx, Tx, and WQ objects. The researched files in this work item include `hinic3_cmdq.o` and `hinic3_common.o`; many referenced symbols are supplied by the other listed objects.

## Control Flow And State
The Makefile has no runtime state, but object ordering is kbuild input for linking one composite driver. Missing entries would appear as unresolved symbols; stale entries would break compilation if files are renamed or removed.

## Dependencies And Integration Points
It is controlled by `hinic3/Kconfig`. It integrates all hinic3 subsystem objects into the kernel networking driver tree under Huawei Ethernet drivers.

## Risks And Test Signals
Risks include accidentally omitting new objects, retaining deleted ones, or failing to update the list when features move between files. Test signals are `make M=drivers/net/ethernet/huawei/hinic3`, full kernel builds with `CONFIG_HINIC3=m` and `=y`, and modpost checks for unresolved or unused exported symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_cmdq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_cmdq.c

## Purpose
Implements the hinic3 synchronous command-queue engine. It allocates DMA command buffers, creates command-queue WQs, programs firmware command-queue contexts, submits long-command WQEs through doorbells, handles CEQ completions, waits for synchronous responses, handles timeout/force-stop cases, and frees or reinitializes command queues.

## Important APIs And Functions
Public APIs are `hinic3_cmdqs_init()`, `hinic3_cmdqs_free()`, `hinic3_alloc_cmd_buf()`, `hinic3_free_cmd_buf()`, `hinic3_cmd_buf_pair_init()`, `hinic3_cmd_buf_pair_uninit()`, `hinic3_cmdq_direct_resp()`, `hinic3_cmdq_detail_resp()`, `hinic3_cmdq_ceq_handler()`, `hinic3_cmdq_flush_sync_cmd()`, `hinic3_reinit_cmdq_ctxts()`, and `hinic3_cmdq_idle()`. Key internals include `cmdq_sync_cmd_exec()`, `wait_cmdq_sync_cmd_completion()`, `cmdq_wqe_fill()`, `cmdq_prepare_wqe_ctrl()`, `cmdq_set_db()`, `cmdq_init_queue_ctxt()`, and `create_cmdq_wq()`.

## Control Flow And State
Initialization allocates `struct hinic3_cmdqs`, creates a DMA pool for 2048-byte command buffers, creates WQs of depth 4096 with 64-byte WQEBBs, allocates a doorbell address, allocates per-WQE `cmd_infos`, and sends command-queue contexts to management firmware. Submission validates buffer size, waits for `HINIC3_CMDQ_ENABLE`, reserves a WQE under `cmdq_lock`, increments input/output buffer refcounts, fills command metadata, writes the WQE header last, rings the doorbell, and waits up to 5000 ms for completion. CEQ handling walks used WQEs, checks busy bits, copies errcode/direct response, completes waiters, clears refcounted buffers, and advances CI. Timeout code distinguishes real timeout, fake timeout after late completion, and force-stop during flush.

## Dependencies And Integration Points
It depends on hinic3 WQ helpers, EQ completion dispatch, hardware device/interface helpers, management mailbox context commands, DMA pools, completions, spinlocks, and bitfield helpers. Other hinic3 modules use direct/detail response APIs for firmware commands.

## Risks And Test Signals
Risks include completion races, refcount leaks, doorbell index mistakes, WQE header ordering, endian conversion, timeout cleanup while firmware still owns buffers, and 0-level versus 1-level CLA handling. Tests should cover command success, SGE response, timeout injection, reset/reinit, device removal with in-flight commands, CEQ storms, DMA pool exhaustion, and lockdep/KASAN around flush paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_cmdq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_cmdq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_cmdq.h

## Purpose
Declares hinic3 command-queue wire formats, queue state, command-buffer wrappers, and public command-queue APIs. It is the shared interface between hinic3 firmware-command callers and the command-queue implementation.

## Important APIs And Types
Hardware WQE structs include `cmdq_header`, `cmdq_wqe_scmd`, `cmdq_wqe_lcmd`, `cmdq_completion`, and top-level `cmdq_wqe`, asserted to be exactly 64 bytes. `struct hinic3_cmd_buf` wraps a DMA pool buffer, DMA address, little-endian size, and refcount. `struct hinic3_cmdq_cmd_info` stores per-WQE in-flight command metadata: command type, completion, errcode, completion code, direct response pointer, message ID, and input/output buffers. `struct hinic3_cmdq` owns a WQ, type, wrap bit, lock, command-info array, and hwdev pointer. `struct hinic3_cmdqs` owns all command queues, the DMA pool, doorbell base, optional WQ block, enable/disable state, and command-queue count.

## Control Flow And State
The header defines the state machine implemented in `hinic3_cmdq.c`: commands transition through direct/detail response types, timeout/fake-timeout/force-stop types, and finally idle/none. The `wrapped` bit and WQ indices determine hardware ownership. `cmd_buf` refcounts protect DMA buffers across submission and asynchronous completion/flush cleanup.

## Dependencies And Integration Points
It includes `linux/dmapool.h`, `hinic3_hw_intf.h`, and `hinic3_wq.h`. Callers throughout hinic3 use `hinic3_cmdq_direct_resp()` and `hinic3_cmdq_detail_resp()` to talk to firmware; EQ code calls `hinic3_cmdq_ceq_handler()`.

## Risks And Test Signals
Risks include ABI-size changes to `cmdq_wqe`, incorrect enum use in completion handling, and lifetime bugs if command buffers are freed without refcount discipline. Signals include static assertion coverage, command-queue initialization/free, successful direct and SGE responses, timeout/flush tests, and reset reinitialization while commands are outstanding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_cmdq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_common.c

## Purpose
Provides small shared hinic3 utility implementations: aligned coherent DMA allocation, matching free, polling with timeout through a callback, and command-buffer dword byte swapping.

## Important APIs And Functions
`hinic3_dma_zalloc_coherent_align()` allocates coherent DMA memory with a requested alignment, retrying with `size + align` if the first allocation is not aligned and recording both original and aligned addresses. `hinic3_dma_free_coherent_align()` releases the original allocation recorded in `struct hinic3_dma_addr_align`. `hinic3_wait_for_timeout()` wraps `read_poll_timeout()` around a caller-provided `wait_cpl_handler`. `hinic3_cmdq_buf_swab32()` calls `swab32_array()` for command-queue buffers.

## Control Flow And State
The aligned allocation path first attempts exact-size allocation, checks `ALIGN(paddr, align)`, and if necessary frees and reallocates a larger buffer so the aligned virtual address can be derived by offsetting from the original virtual address. The polling helper treats `HINIC3_WAIT_PROCESS_WAITING` as continue, returns `-EIO` for `HINIC3_WAIT_PROCESS_ERR`, and otherwise returns the polling timeout result. The byte-swap helper mutates a buffer in place.

## Dependencies And Integration Points
It depends on Linux DMA mapping, delay/iopoll helpers, and `hinic3_common.h`. It is a support library for modules that need aligned DMA blocks, polling waits, or command-queue buffer endian transformation.

## Risks And Test Signals
Risks include invalid `align` assumptions, pointer arithmetic on `void *` relying on compiler extension, freeing only through the recorded original allocation, and byte-swapping buffers whose length is not a multiple of 32 bits. Test signals include DMA-debug clean runs, allocations with already-aligned and misaligned DMA addresses, timeout and error polling paths, and command buffers verified before/after swap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_common.h

## Purpose
Declares shared hinic3 utility types and helpers for aligned DMA memory, scatter-gather element programming, polling completion state, and command-buffer byte swapping.

## Important APIs And Types
`HINIC3_MIN_PAGE_SIZE` defines the 4 KiB minimum page size used by command queues and WQ logic. `struct hinic3_dma_addr_align` records original and aligned virtual/physical addresses plus allocation size. `enum hinic3_wait_return` defines polling callback outcomes: complete, waiting, or error. `struct hinic3_sge` is a little-endian SGE with high address, low address, length, and reserved dword. `hinic3_set_sge()` fills an SGE from a DMA address and little-endian length. Public prototypes cover aligned DMA allocation/free, timeout polling, and `hinic3_cmdq_buf_swab32()`.

## Control Flow And State
The inline `hinic3_set_sge()` is the only executable code here; it writes upper/lower DMA address halves with `cpu_to_le32()`, stores the provided length, and clears the reserved field. Other declarations describe utility state consumed by `hinic3_common.c` and command/queue modules.

## Dependencies And Integration Points
It includes `linux/device.h` for DMA types and device pointers. `hinic3_cmdq.h` embeds `struct hinic3_sge` in command WQEs, and many hinic3 command builders can use `hinic3_set_sge()` for firmware-visible descriptors.

## Risks And Test Signals
Risks include passing a CPU-endian length to `hinic3_set_sge()` despite its `__le32` parameter, changing SGE layout in a way that breaks firmware ABI, or using aligned DMA records without matching free. Signals include sparse endian warnings, static layout checks in command structures, successful command-queue detail responses, and DMA-debug clean teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_common.h -->
