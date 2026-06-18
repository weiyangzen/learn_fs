# subset-b-004386 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bna_tx_rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bna_tx_rx.c

## Purpose
Implements the BNA control-plane objects for Ethernet transmit and receive data paths in the QLogic/Brocade BR-series CNA driver. This is below Linux `net_device` glue and above firmware: it owns Tx/Rx object allocation, queue-page-table setup, firmware message construction, Rx filter CAM management, RSS/RIT/VLAN programming, interrupt block coalescing state, dynamic interrupt moderation vectors, and finite-state machines for starting, stopping, failing, and cleaning up Tx/Rx paths.

## Important APIs, Types, and Functions
The file operates on the types declared in `bna_types.h`: `bna_tx_mod`, `bna_tx`, `bna_txq`, `bna_tcb`, `bna_rx_mod`, `bna_rx`, `bna_rxp`, `bna_rxq`, `bna_rcb`, `bna_cq`, `bna_ccb`, and `bna_rxf`. Public creation and lifecycle APIs include `bna_tx_res_req`, `bna_tx_create`, `bna_tx_destroy`, `bna_tx_enable`, `bna_tx_disable`, `bna_tx_cleanup_complete`, `bna_tx_mod_init`, `bna_tx_mod_start`, `bna_tx_mod_stop`, `bna_tx_mod_fail`, `bna_rx_res_req`, `bna_rx_create`, `bna_rx_destroy`, `bna_rx_enable`, `bna_rx_disable`, `bna_rx_cleanup_complete`, `bna_rx_mod_init`, `bna_rx_mod_start`, `bna_rx_mod_stop`, and `bna_rx_mod_fail`. Firmware response entry points are `bna_bfi_tx_enet_start_rsp`, `bna_bfi_tx_enet_stop_rsp`, `bna_bfi_rx_enet_start_rsp`, `bna_bfi_rx_enet_stop_rsp`, `bna_bfi_rxf_cfg_rsp`, `bna_bfi_rxf_ucast_set_rsp`, `bna_bfi_rxf_mcast_add_rsp`, and `bna_bfi_bw_update_aen`.

Rx filter APIs include `bna_rx_ucast_set`, `bna_rx_ucast_listset`, `bna_rx_mcast_add`, `bna_rx_mcast_listset`, `bna_rx_mcast_delall`, `bna_rx_vlan_add`, `bna_rx_vlan_del`, `bna_rx_vlanfilter_enable`, `bna_rx_vlan_strip_enable`, `bna_rx_vlan_strip_disable`, and `bna_rx_mode_set`. Coalescing and DIM are exposed through `bna_tx_coalescing_timeo_set`, `bna_rx_coalescing_timeo_set`, `bna_rx_dim_reconfig`, `bna_rx_dim_update`, and the default `bna_napi_dim_vector`.

## Control Flow and State
The Rx filter (`bna_rxf`) is an asynchronous firmware-request serializer. Desired changes are accumulated in pending queues and bitmasks: unicast add/delete/default set, multicast add/delete plus firmware CAM handles, promiscuous/allmulti/default mode transitions, VLAN filter block masks, VLAN strip pending state, and RSS RIT/config/status flags. `bna_rxf_cfg_apply()` sends at most one firmware message, in a fixed order, and the `RXF_E_FW_RESP` event advances to the next pending item. Soft reset preserves desired state for replay after failure; hard cleanup may emit delete/disable firmware requests.

The Rx object FSM has stopped, start-wait, start-stop-wait, rxf-start-wait, started, rxf-stop-wait, stop-wait, cleanup-wait, failed, and quiesce-wait states. Starting sends `BFI_ENET_H2I_RX_CFG_SET_REQ`, receives queue handles and doorbells, posts buffers through BNAD callbacks, starts the Rx filter, then starts interrupt blocks. Stopping reverses this by stopping RxF, stopping IBs, sending clear requests, and waiting for BNAD cleanup completion. Failure paths stall posting, call cleanup callbacks, and quiesce before restart.

The Tx FSM similarly gates `BFI_ENET_H2I_TX_CFG_SET_REQ`/clear requests, interrupt block start/stop, BNAD stall/resume/cleanup callbacks, and bandwidth/priority updates. A bandwidth update while active forces a stop-cleanup-start sequence so firmware priority mapping is reapplied.

Queue state is held in software rings plus firmware-owned DMA queue-page tables. `bna_*_res_req()` computes KVA/DMA/interrupt requirements; `bna_*_create()` consumes those descriptors and wires QPT pages, software QPTs, work queues, IB index pages, CCB/RCB/TCB callbacks, doorbell placeholders, and active/free module lists. Firmware start responses fill hardware queue IDs and MMIO doorbell addresses and reset producer/consumer indices.

## State and Persistence Behavior
No state is persistent across driver unload. Runtime persistence is in the live BNA object graph, firmware CAM/RSS/VLAN settings, DMA rings, hardware doorbells, and statistics counters. The RxF pending/active queues are the important software cache used to reconcile Linux address/VLAN/mode state with firmware. RID bitmasks in Tx/Rx modules advertise active firmware functions to stats and ethtool code.

## Dependencies and Integration Points
Depends on `bna.h`, `bfi.h`, firmware message queue helpers, BFA FSM/work-counter helpers, BNA hardware definitions, Ethernet address helpers, endian conversion, and callbacks supplied by `bnad.c`. It integrates upward through BNAD setup/teardown callbacks and downward through firmware message classes `BFI_MC_ENET`. It also integrates with `bna_enet`/`bna_ethport` for data-path start/stop notifications and with the interrupt-block helpers declared elsewhere in the BNA driver.

## Risks and Test Signals
High-risk areas are FSM event ordering, one-message-at-a-time RxF replay, CAM handle reference counts, cleanup while firmware responses are still pending, queue depth/page-count arithmetic, DMA QPT setup, doorbell address use before firmware responses, and races between failure, stop, and restart paths. `bna_rx_mode_set()` enforces single promiscuous/default RID ownership, so regressions can block multicast/promiscuous behavior. DIM changes modify IB coalescing live and need packet-rate and timer validation. Test signals include open/stop/reopen loops, forced firmware failover, RSS fanout, VLAN add/delete and strip toggles, multicast list overflow fallback, promisc/allmulti/default transitions, jumbo MTU crossing the multi-buffer boundary, Tx bandwidth AENs, and ethtool per-ring counters matching active RIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bna_tx_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bna_types.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bna_types.h

## Purpose
Defines the central BNA runtime object model for the BR-series Ethernet driver. It is the contract between low-level BNA control code, Linux-facing BNAD glue, firmware message handling, statistics, CAM managers, queue resources, and interrupt moderation.

## Important APIs, Types, and Functions
The header is type-only but critical. It defines status and resource enums (`bna_status`, `bna_cleanup_type`, `bna_cb_status`, `bna_res_type`, `bna_mem_type`, `bna_intr_type`), module resource IDs, Tx/Rx resource IDs, Tx/Rx/RxF FSM event enums, link/enet/ethport flags, RSS pending flags, packet-rate thresholds, and DIM load/bias categories.

Core structures include generic resource descriptors `bna_mem_descr`, `bna_mem_info`, `bna_intr_info`, and `bna_res_info`; firmware/hardware metadata `bna_attr`, `bna_ioceth`, `bna_enet`, and `bna_ethport`; interrupt block state `bna_ib`; Tx data path state `bna_tcb`, `bna_txq`, `bna_tx`, `bna_tx_config`, `bna_tx_event_cbfn`, and `bna_tx_mod`; Rx state `bna_rcb`, `bna_rxq`, `bna_ccb`, `bna_cq`, `bna_rx_config`, `bna_rxp`, `bna_rxf`, `bna_rx`, `bna_rx_event_cbfn`, and `bna_rx_mod`; CAM modules `bna_ucam_mod`, `bna_mcam_handle`, `bna_mcam_mod`; and aggregate state `struct bna`.

## Control Flow and State
There is no executable control flow, but the fields encode ownership and lifecycle. Control-plane objects carry FSM function pointers and callback pointers; data-path objects carry ring pointers, producer/consumer indices, interrupt vectors, doorbells, queue depth, DMA backing, and BNAD cookies. `bna_rxf` splits desired filter state into pending and active queues/bitmasks, while `bna_tx_mod` and `bna_rx_mod` own free/active queues and RID masks. `struct bna` aggregates IOC, CEE, flash, message queue, enet, ethport, stats, Tx/Rx modules, CAM modules, and BNAD backpointer.

## State and Persistence Behavior
State is volatile and driver-owned. Hardware-persistent concepts, such as firmware attributes, CAM handles, queue IDs, link status, pause, MTU, RSS tables, VLAN filters, and counters, are mirrored here only while the driver is loaded. The resource descriptors define allocation shape but not ownership lifetime by themselves; BNAD allocation/free routines fill and release them.

## Dependencies and Integration Points
Includes `cna.h`, `bna_hw_defs.h`, `bfa_cee.h`, and `bfa_msgq.h`, so it binds this Ethernet layer to common CNA/BFA firmware infrastructure and hardware register/message definitions. It is consumed by `bna_tx_rx.c`, `bnad.c`, `bnad.h`, ethtool/debugfs code, firmware callback dispatch, and the broader BNA modules for IOC/enet/stats.

## Risks and Test Signals
This file is an ABI-like internal layout. Risks are cacheline-sensitive data-path field drift, enum value changes breaking FSM dispatch or resource indexing, callback signature mismatch, resource index mismatch between request/allocation/create paths, and stats layout assumptions in ethtool. Test signals are allmodconfig builds, open/stop with all Rx path types, MSI-X and INTx operation, ethtool stats count/string alignment, and debug checks that `BNA_*_RES_T_MAX` arrays are fully populated before allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bna_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bnad.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bnad.c

## Purpose
Provides the Linux PCI/netdev implementation for the BR-series 10G Ethernet driver. It bridges kernel networking APIs, DMA mapping, interrupts, NAPI, timers, firmware loading, PCI probe/remove, netdev open/stop, Tx/Rx packet processing, VLAN/MAC/multicast configuration, MTU changes, statistics, and BNA control-plane callbacks.

## Important APIs, Types, and Functions
PCI/module entry points are `bnad_module_init`, `bnad_module_exit`, `bnad_pci_probe`, and `bnad_pci_remove`. Netdev operations are `bnad_open`, `bnad_stop`, `bnad_start_xmit`, `bnad_get_stats64`, `bnad_set_rx_mode`, `bnad_set_mac_address`, `bnad_change_mtu`, `bnad_vlan_rx_add_vid`, `bnad_vlan_rx_kill_vid`, `bnad_set_features`, and optional `bnad_netpoll`.

Data-path functions include Tx cleanup/completion helpers `bnad_tx_buff_unmap`, `bnad_txq_cleanup`, `bnad_txcmpl_process`, `bnad_tx_complete`, `bnad_txq_wi_prepare`, and Rx helpers `bnad_rxq_alloc_init`, `bnad_rxq_refill_page`, `bnad_rxq_refill_skb`, `bnad_rxq_post`, `bnad_cq_process`, `bnad_cq_setup_skb`, `bnad_cq_setup_skb_frags`, and `bnad_napi_poll_rx`. Interrupt handlers are `bnad_msix_tx`, `bnad_msix_rx`, `bnad_msix_mbox_handler`, and shared INTx `bnad_isr`. Resource/lifecycle APIs exported to other files include `bnad_setup_tx`, `bnad_destroy_tx`, `bnad_setup_rx`, `bnad_destroy_rx`, `bnad_tx_coalescing_timeo_set`, `bnad_rx_coalescing_timeo_set`, `bnad_mac_addr_set_locked`, `bnad_enable_default_bcast`, `bnad_restore_vlans`, and stats fill helpers.

## Control Flow and State
Probe first loads firmware under `bnad_fwimg_mutex`, allocates a netdev with private `struct bnad`, initializes PCI/BAR/workqueue/netdev/debugfs, asks BNA for common resources, calls `bna_init`, enables MSI-X when possible, requests the mailbox IRQ, starts IOC timers, enables IOC Ethernet, negotiates firmware queue limits, allocates BNA module resources, initializes modules, reads the permanent MAC, and registers the netdev. Remove unregisters the netdev, disables IOC, deletes timers, uninitializes BNA, frees common/module resources, IRQs, MSI-X, PCI, debugfs, BAR mapping, locks, and netdev.

`bnad_open()` creates Tx and Rx objects, configures MTU and pause, enables enet, enables broadcast/multicast defaults, restores VLANs and unicast address, and starts stats polling. `bnad_stop()` stops stats, disables enet and waits for completion, destroys Tx/Rx objects, synchronizes mailbox IRQ, and returns. Tx transmit maps skb head/frags into BNA work items, handles TSO/checksum/VLAN/CEE priority flags, stops/wakes queues around ring pressure, writes producer index, and rings the Tx doorbell. Tx completions unmap DMA, free skbs, update counters, acknowledge IBs, and wake queues.

Rx setup allocates page or skb buffers, posts ring entries, and NAPI polls completion queues. `bnad_cq_process()` validates completion entries with barriers, supports multi-buffer packets, drops MAC/FCS/length errors, builds skb frags or skb data, sets checksum state, attaches VLAN tags, sends packets to GRO or `netif_receive_skb`, clears CQ valid bits, disables/acks IRQs during polling, and refills queues. Cleanup disables NAPI, clears CQ entries, unmaps pages/skbs, and signals the BNA FSM.

## State and Persistence Behavior
Driver state lives in `struct bnad`: active VLAN bitmap, queue counts/depths, coalescing timers, resource descriptors, completions, timers, workqueue, stats, BAR mapping, MSI-X table, run/config flags, and debugfs scratch. Persistent hardware/firmware state includes flash firmware, IOC state, MAC/MTU/pause settings, filters, rings, and hardware counters. Active VLANs and netdev flags are replayed after Rx recreation. Firmware image pointer `bfi_fw` is released at module exit.

## Dependencies and Integration Points
Integrates with Linux PCI, DMA, `net_device`, NAPI/GRO, VLAN, ethtool, netpoll, timers, firmware loader, workqueues, MSI-X/INTx IRQ APIs, and BNA/BFA firmware modules. It supplies callback tables to `bna_tx_create` and `bna_rx_create`, handles BNA completions, and exposes debugfs/ethtool support via `bnad.h`.

## Risks and Test Signals
Risks are DMA unmap correctness on partial map failure, queue stop/wake races, interrupt/NAPI ordering during teardown, null dereferences when setup partially fails, timer deletion races, mailbox IRQ synchronization, firmware enable timeout handling, and MTU transitions over the Catapult2 4K multi-buffer threshold. `bnad_change_mtu()` writes `netdev->mtu` before `bnad_mtu_set()` succeeds and does not visibly roll back on failure. `bnad_pci_probe()` has a `probe_success` path after IOC enable failure that returns success without registering a netdev, which deserves regression attention. Test signals include probe/remove failure injection, open/stop stress, INTx and MSI-X modes, Tx map-failure tests, NAPI teardown under traffic, jumbo MTU toggles, VLAN feature toggles, promisc/allmulti/multicast overflow, firmware reset/recovery, and ethtool stats consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bnad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bnad.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bnad.h

## Purpose
Defines the Linux-facing BNAD private driver state, resource limits, flags, stats, Tx/Rx unmap metadata, exported helper prototypes, and small macros used by `bnad.c`, ethtool, debugfs, and firmware-image code.

## Important APIs, Types, and Functions
Important constants include queue depths and limits (`BNAD_TXQ_DEPTH`, `BNAD_RXQ_DEPTH`, `BNAD_MAX_RXP_PER_RX`, `BNAD_MAX_TXQ_PER_TX`), IRQ vector layout, timer frequencies, timeout values, MTU and queue-depth limits, refill threshold, and frame-size calculation. `struct bnad_rx_ctrl` binds one CCB to a NAPI instance and poll/interrupt counters. `struct bnad_completion` groups synchronous completions used around asynchronous BNA commands. `struct bnad_drv_stats` and `struct bnad_stats` feed ethtool and netdev stats. Resource wrappers `bnad_tx_res_info` and `bnad_rx_res_info` hold BNA resource arrays.

Data-path private structures include `bnad_tx_info`, `bnad_rx_info`, `bnad_tx_vector`, `bnad_tx_unmap`, `bnad_rx_vector`, `bnad_rx_unmap`, `bnad_rxbuf_type`, and flexible `bnad_rx_unmap_q`. The aggregate `struct bnad` holds netdev, BNA instance, queues, VLAN bitmap, coalescing settings, BAR, PCI device, MSI-X table, locks, timers, resources, completions, permanent MAC, workqueue, debugfs data, and names.

Exports include firmware `bfi_fw`, `cna_get_firmware_buf`, netdev/config helpers (`bnad_set_rx_mode`, `bnad_get_netdev_stats`, `bnad_mac_addr_set_locked`, `bnad_enable_default_bcast`, `bnad_restore_vlans`, `bnad_set_ethtool_ops`, `bnad_cb_completion`), setup/teardown helpers, coalescing helpers, stats fill helpers, and debugfs init/uninit.

## Control Flow and State
There is no standalone runtime control flow except macros. Flags split into `cfg_flags` values such as DIM/promisc/allmulti/default/MSI-X and `run_flags` bit positions such as CEE running, MTU set, mailbox IRQ disabled, netdev registered, DIM/stats timer running, and Tx priority set. `bnad_enable_rx_irq_unsafe()` is a performance-sensitive macro that reprograms coalescing and acknowledges the Rx interrupt block only if the Rx queue is marked started.

## State and Persistence Behavior
The header defines transient driver state only. It is the main in-memory persistence layer while the module is loaded: active VLANs, queue/resource allocations, timer state, stats, debugfs register read buffers, and firmware command completions are all rooted in `struct bnad`.

## Dependencies and Integration Points
Includes networking, firmware, VLAN, checksum, IPv6, workqueue, mutex, and `bna.h` definitions. It is included by all BNAD companion files and is the binding point between Linux APIs and the BNA control layer.

## Risks and Test Signals
Risks are fixed array limits not matching firmware attributes, flexible-array size calculations for unmap queues, stats string assumptions that mirror `struct bnad_drv_stats`, flag bit/value confusion between `cfg_flags` masks and `run_flags` bit positions, and exported prototypes drifting from implementation. Test signals include build coverage with netpoll and VLAN configs, Rx path counts at CPU/MSI-X limits, ethtool stats layout checks, and open/stop with debugfs enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bnad.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bnad_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bnad_debugfs.c

## Purpose
Implements optional debugfs support for the BNA driver. It creates `/sys/kernel/debug/bna/pci_dev:<pci_name>/` entries for firmware trace capture, saved firmware crash trace capture, raw register reads and writes, and aggregate driver/IOC/CEE/flash information.

## Important APIs, Types, and Functions
`struct bnad_debug_info` stores per-open debug buffers and private BNA pointers. Open/read/write handlers include `bnad_debugfs_open_fwtrc`, `bnad_debugfs_open_fwsave`, `bnad_debugfs_open_reg`, `bnad_debugfs_open_drvinfo`, `bnad_debugfs_read`, `bnad_debugfs_read_regrd`, `bnad_debugfs_write_regrd`, and `bnad_debugfs_write_regwr`. Utility functions include `bnad_get_debug_drvinfo`, `bnad_debugfs_lseek`, `bnad_debugfs_release`, `bnad_debugfs_buffer_release`, and register-bound validation `bna_reg_offset_check`. Public entry points are `bnad_debugfs_init` and `bnad_debugfs_uninit`.

## Control Flow and State
Initialization lazily creates the global `bna` root and a per-port directory named `pci_dev:<pci_name>`, then installs files `fwtrc`, `fwsave`, `regrd`, `regwr`, and `drvinfo`. Firmware trace opens allocate a fixed trace buffer and fill it through `bfa_nw_ioc_debug_fwtrc()` or `bfa_nw_ioc_debug_fwsave()` under `bna_lock`. Driver-info opens allocate `struct bnad_drvinfo`, collect IOC attributes synchronously under lock, then issue CEE and flash attribute commands and wait for completions under `conf_mutex`.

Register reads are two-step: writing `addr:len` to `regrd` validates the masked BAR0 offset and length, allocates `bnad->regdata`, reads dwords under `bna_lock`, and later `read()` drains and frees that buffer. Register writes parse `addr:val`, validate one dword, and write BAR0 under `bna_lock`.

## State and Persistence Behavior
Debug buffers are per-open except register read data, which is stored in `bnad->regdata`/`reglen` until fully read or replaced. The global root dentry and atomic port count persist across adapters. Register writes directly mutate device MMIO state and are intentionally persistent until hardware or firmware changes it.

## Dependencies and Integration Points
Depends on Linux debugfs, module ownership, BAR0 access through `bfa_ioc_bar0`, BFA IOC debug helpers, CEE and flash APIs, BNAD completions, and BNAD locks. It is enabled from `bnad_pci_probe()` through the `bna_debugfs_enable` module parameter and cleaned up from probe failure/remove paths.

## Risks and Test Signals
Risk is high for `regwr`: it exposes raw MMIO writes to privileged debugfs users and can destabilize hardware. Other risks include `bnad->regdata` being shared per adapter across concurrent readers/writers, offset/length overflow mistakes, waiting for firmware completions while the device is resetting, and debugfs root lifetime with multiple ports. Test signals include debugfs mount with multiple adapters, concurrent `regrd` readers, invalid offset/length inputs, firmware trace after firmware failure, and remove while files are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bnad_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bnad_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bnad_ethtool.c

## Purpose
Implements ethtool support for the BNA netdev: fixed 10G link settings, driver and firmware information, coalescing/DIM control, ring-depth reconfiguration, pause settings, extensive software/hardware/per-queue statistics, EEPROM/flash partition access, and firmware flashing.

## Important APIs, Types, and Functions
The exported entry point is `bnad_set_ethtool_ops`, which installs `bnad_ethtool_ops`. Link operations are `bnad_get_link_ksettings` and `bnad_set_link_ksettings`; info and WOL are `bnad_get_drvinfo` and `bnad_get_wol`; interrupt moderation is `bnad_get_coalesce`/`bnad_set_coalesce`; ring changes are `bnad_get_ringparam`/`bnad_set_ringparam`; pause is `bnad_get_pauseparam`/`bnad_set_pauseparam`. Stats are driven by `bnad_net_stats_strings`, dynamic string emitters for TxF/RxF/CQ/RxQ/TxQ, `bnad_get_strings`, `bnad_get_stats_count_locked`, `bnad_per_q_stats_fill`, `bnad_get_ethtool_stats`, and `bnad_get_sset_count`. Flash/EEPROM paths are `bnad_get_flash_partition_by_offset`, `bnad_get_eeprom_len`, `bnad_get_eeprom`, `bnad_set_eeprom`, and `bnad_flash_device`.

## Control Flow and State
Coalescing validates nonzero usec values within firmware units, toggles DIM under `conf_mutex` and `bna_lock`, starts or deletes the DIM timer, and pushes Tx/Rx coalescing timeouts into BNA objects. Ring reconfiguration validates power-of-two depths and, if the netdev is running, destroys and recreates affected Rx/Tx objects. Rx recreation replays VLANs, broadcast, MAC address, and receive mode.

Stats string/count/value generation is dynamic. Base netdev and driver stats are followed by hardware stats, active TxF/RxF stats selected from BNA RID masks, CQs, RxQs, optional second RxQs, and TxQs. Values are read under `bna_lock` after verifying the caller's expected stats count. EEPROM reads/writes map ethtool offsets to firmware flash partitions by first querying flash attributes, then issuing asynchronous flash commands and waiting for completions. Firmware flashing uses `request_firmware()` and updates the firmware image partition.

## State and Persistence Behavior
Etthool changes can persist for the lifetime of the device instance: queue depths, coalescing values, DIM enablement, pause configuration, and firmware/EEPROM writes. Statistics are live snapshots from BNAD software counters and BNA hardware stats. Firmware flashing and EEPROM writes are persistent hardware mutations.

## Dependencies and Integration Points
Depends on Linux ethtool, rtnetlink stats types, firmware loading, BNA flash/CEE/IOC APIs, BNAD setup/teardown helpers, `bna_rx_rid_mask`, `bna_tx_rid_mask`, and BNAD locking. It is installed by `bnad_netdev_init()` in `bnad.c`.

## Risks and Test Signals
High-risk operations are ring recreation under traffic, flash writes, EEPROM partition mapping, and coalescing timer races. Stats string/count/value ordering must stay perfectly aligned; `bnad_get_strings()` appears to shift the RxF RID bitmap both in the `for` increment and inside the loop body, unlike the count and value paths, so multi-RID RxF stats strings can become misaligned. `bnad_set_coalesce()` clears the DIM flag and then checks the same flag before deleting the timer, making the delete branch look unreachable; timer behavior should be tested. `bnad_flash_device()` calls `release_firmware(fw)` even when `request_firmware()` failed, leaving `fw` uninitialized. Test signals include `ethtool -S` count/string/value validation, DIM on/off under traffic, ringparam changes while up/down, pause toggles, EEPROM invalid offsets, firmware flash failure injection, and multiple active RIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bnad_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/cna.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/cna.h

## Purpose
Provides small common CNA definitions shared by the BNA Ethernet driver and lower BFA firmware infrastructure. It centralizes basic kernel includes, a state-machine fault logging macro, firmware file names, version extern, and a Fibre Channel symbolic-name limit used by adjacent common code.

## Important APIs, Types, and Functions
The key macro is `bfa_sm_fault(event)`, which logs state-machine assertion failures with source file, line, and event value. It declares `extern char bfa_version[]`, defines firmware names `CNA_FW_FILE_CT` and `CNA_FW_FILE_CT2`, and defines `FC_SYMNAME_MAX`.

## Control Flow and State
There is no runtime control flow beyond the logging macro. The firmware-name macros are consumed by firmware loading and module firmware declarations; the fault macro is used by BNA FSM default cases to report unexpected events without stopping execution.

## State and Persistence Behavior
No mutable state is defined here. Firmware filenames represent a userspace firmware ABI: the kernel firmware loader must find `ctfw-3.2.5.1.bin` or `ct2fw-3.2.5.1.bin` depending on PCI device generation.

## Dependencies and Integration Points
Includes core kernel, PCI, timer, interrupt, delay, VLAN, and Ethernet headers. It is included by `bna_types.h`, `bnad.c`, `bnad_ethtool.c`, `cna_fwimg.c`, and other BNA/BFA files. `MODULE_FIRMWARE()` in `bnad.c` uses these names.

## Risks and Test Signals
Risks are low but ABI-sensitive. Changing firmware filenames breaks device initialization; changing `bfa_sm_fault` behavior affects diagnostics for all BFA FSMs. Test signals are firmware-load success on CT/CT2 devices, module metadata containing both firmware names, and readable state-machine fault logs on invalid event injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/cna.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/cna_fwimg.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/cna_fwimg.c

## Purpose
Loads and exposes BR-series CNA firmware images for CT and CT2 ASIC generations. It is the firmware image provider used during PCI probe and by BFA callback hooks that fetch firmware chunks and sizes for IOC download.

## Important APIs, Types, and Functions
Global `const struct firmware *bfi_fw` is exported through `bnad.h` and released at module exit. Static caches hold `bfi_image_ct_cna`, `bfi_image_ct2_cna`, and their dword sizes. `cna_read_firmware()` calls `request_firmware()`, stores the firmware data pointer as `u32 *`, records the dword count, assigns `bfi_fw`, and converts each LE32 word to CPU byte order in place. `cna_get_firmware_buf()` selects CT2 firmware by exact device ID or CT firmware by ASIC helper. `bfa_cb_image_get_chunk()` and `bfa_cb_image_get_size()` return cached image pointers and sizes by `bfi_asic_gen`.

## Control Flow and State
Firmware is lazy-loaded on first request per ASIC generation. PCI probe calls `cna_get_firmware_buf()` under a global mutex in `bnad.c`, so the static caches are serialized there. Once loaded, later calls return the cached pointer. BFA download code asks for chunks by offset and total size via callbacks.

## State and Persistence Behavior
The firmware data stays resident until module exit. The code mutates the firmware buffer with `le32_to_cpus()` so cached data is host-endian after the first load. Only one global `bfi_fw` pointer is retained even though there are two possible cached firmware images; this means module exit releases only the last assigned firmware object.

## Dependencies and Integration Points
Depends on Linux firmware loading, `bnad.h` for `bfi_fw` and PCI device macros, `bfi.h` for ASIC generation enums, and `cna.h` for firmware filenames. It integrates with `bnad_pci_probe()` and BFA IOC firmware callbacks.

## Risks and Test Signals
The main risk is firmware lifetime and cache ownership. If both CT and CT2 images are loaded in one module lifetime, `bfi_fw` tracks only one `struct firmware`, so the other may not be released. The code also casts `fw->data` away from const and endian-swaps in place, which relies on firmware memory being writable. Offset handling in `bfa_cb_image_get_chunk()` trusts callers. Test signals include probing CT and CT2 adapters in one boot, unload leak checks, missing firmware error paths, firmware download checksum/version validation, and byte-order validation on big-endian systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/cna_fwimg.c -->
