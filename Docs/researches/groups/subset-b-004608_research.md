# subset-b-004608 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_vf.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_vf.c

### Purpose
`qed_vf.c` implements the VF side of the QED SR-IOV VF/PF control channel. It allocates coherent mailbox and bulletin-board memory, negotiates resources with the PF, starts and stops queues and vports, sends filter/coalescing/tunnel updates, and translates PF bulletin-board updates into link, MAC, and tunnel-port changes visible to the upper QEDE network driver.

### Important APIs, Types, And Functions
The core mailbox helpers are `qed_vf_pf_prep()`, `qed_send_msg2pf()`, `qed_vf_pf_req_end()`, and `qed_vf_pf_add_qid()`. Lifecycle entry points include `qed_vf_hw_prepare()`, `qed_vf_pf_acquire()`, `_qed_vf_pf_release()`, `qed_vf_pf_release()`, and `qed_vf_pf_reset()`. Datapath provisioning functions are `qed_vf_pf_rxq_start()`, `qed_vf_pf_rxq_stop()`, `qed_vf_pf_txq_start()`, `qed_vf_pf_txq_stop()`, `qed_vf_pf_vport_start()`, `qed_vf_pf_vport_stop()`, and `qed_vf_pf_vport_update()`. Other exported VF operations cover multicast and unicast filtering, interrupt cleanup, per-queue coalescing, tunnel parameter update, status block registration, resource getters, MAC checks, firmware-version getters, and bulletin polling via `qed_iov_vf_task()`.

### Control Flow
VF/PF requests follow a strict prepare-send-end sequence. `qed_vf_pf_prep()` takes `vf_iov_info->mutex`, clears request and response unions, writes the first TLV, and stores the physical response address. Callers append optional TLVs and a `CHANNEL_TLV_LIST_END`, then `qed_send_msg2pf()` writes the request DMA address into the VF USDM zone, executes a write barrier, triggers the PF, and polls the PF-written status byte first with short `udelay()` loops and then with `msleep()` retries. `qed_vf_pf_req_end()` logs the request and PF status before unlocking the mailbox mutex.

`qed_vf_hw_prepare()` reads VF opaque and concrete FIDs, allocates `struct qed_vf_iov`, request/reply DMA mailboxes, and a coherent bulletin board, selects register-bar versus doorbell-bar behavior, and sends `ACQUIRE`. Acquisition asks for maximum VF queues, status blocks, filters, and CIDs, advertises firmware and fastpath HSI versions, retries transient channel timeouts, reduces resource requests when the PF returns `NO_RESOURCE`, and handles old PFs by enabling `VFPF_ACQUIRE_CAP_PRE_FP_HSI`. On success it copies the PF response into `acquire_resp`, updates device type/chip information, records bulletin size, derives CMT/100G configuration, and may retry without mapped doorbells when a legacy PF cannot report the doorbell BAR split.

Queue and vport setup builds typed TLVs and waits for PF success. RX queue start may compute and initialize producer addresses locally for pre-FP-HSI PFs, otherwise it uses the PF returned offset. TX queue start similarly chooses a PF-returned doorbell offset for modern PFs or a legacy CID-derived doorbell address. Vport update constructs a list of extended TLVs only for requested changes: activation, TX switching, VLAN stripping, multicast bins, accept-mode flags, RSS table/key/caps, accept-any-VLAN, and SGE/TPA parameters where compiled in by struct availability. Tunnel updates send requested VXLAN/Geneve/GRE mode, class, and UDP-port changes, then fold the PF's response back into `cdev->tunnel`.

Bulletin handling is polling based. `qed_iov_vf_task()` reschedules itself every second unless stopped, calls `qed_vf_read_bulletin()`, validates a version change with CRC32 over the bulletin excluding its `crc` field, updates `bulletin_shadow`, and then `qed_handle_bulletin_change()` invokes protocol callbacks for forced/suggested MAC and UDP tunnel ports and triggers `qed_link_update()`.

### State, Persistence, And Dependencies
All VF state is in `p_hwfn->vf_iov_info`. Persistent-in-memory fields include DMA addresses for `vf2pf_request`, `pf2vf_reply`, and `bulletin`, a shadow copy of the latest valid bulletin, the saved PF acquisition response, pre-FP-HSI and doorbell-bar compatibility booleans, and per-status-block pointers used during vport start. The only hardware-persistent effects are PF-owned queue/vport/filter/coalescing/link settings requested through the mailbox. Dependencies include `qed.h`, `qed_sriov.h`, `qed_vf.h`, QED TLV list helpers, PXP VF BAR register definitions, DMA coherent memory APIs, memory barriers, firmware HSI constants, CRC32, Ethernet address helpers, and protocol callbacks from the upper Ethernet driver.

### Integration Points
This file is the VF backend behind QED Ethernet operations consumed by QEDE. QEDE open/close and queue allocation paths indirectly call the queue/vport functions; ethtool coalescing calls reach `qed_vf_pf_get_coalesce()` and `qed_vf_pf_set_coalesce()` for VFs; filter and MAC changes call `qed_vf_pf_filter_ucast()`, `qed_vf_pf_filter_mcast()`, `qed_vf_check_mac()`, and `qed_vf_pf_bulletin_update_mac()`. The delayed IOV workqueue integrates PF bulletin updates with QEDE callbacks `force_mac` and `ports_update`.

### Risks
The mailbox lock depends on every caller pairing `qed_vf_pf_prep()` with `qed_vf_pf_req_end()` on every exit path; missing an end call would deadlock future VF/PF messages. DMA buffer lifetimes must outlive PF accesses and are freed only during final release. Channel timeout handling is intentionally conservative but can leave PF-side operations ambiguous. Compatibility paths for old PFs, 100G CMT, and physical doorbell BARs are subtle and can break queue producer/doorbell address computation. `qed_vf_read_bulletin()` tolerates racing PF writes by returning `-EAGAIN` on CRC mismatch; callers currently ignore that error and poll again. `qed_vf_check_mac()` returns false whenever a forced MAC exists, even when the requested MAC equals the forced MAC, so callers must interpret it as "VF may not independently set MAC" rather than "address mismatch."

### Test Signals
Useful signals include VF probe against modern and legacy PFs, acquisition retry after simulated `-EBUSY`, resource reduction after `PFVF_STATUS_NO_RESOURCE`, queue start/stop with and without `PFVF_ACQUIRE_CAP_QUEUE_QIDS`, 100G dual-hwfn doorbell BAR fallback, vport update TLV combinations, coalescing reads and writes on RX/TX handles, forced MAC bulletin behavior, CRC-corrupt bulletin retry, tunnel-port update propagation, and release/reset while interrupts and delayed bulletin work are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_vf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_vf.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_vf.h

### Purpose
`qed_vf.h` defines the VF/PF mailbox ABI used by the QED VF driver and declares the VF helper API implemented in `qed_vf.c`. It contains the TLV wire structures for acquisition, queue/vport management, filters, RSS, tunnel updates, coalescing, bulletin MAC updates, PF responses, and the PF-to-VF bulletin board.

### Important APIs, Types, And Functions
Important wire types include `struct channel_tlv`, `struct vfpf_first_tlv`, `struct pfvf_tlv`, `struct vfpf_acquire_tlv`, `struct pfvf_acquire_resp_tlv`, queue TLVs such as `vfpf_start_rxq_tlv`, `vfpf_start_txq_tlv`, stop/update queue TLVs, vport update TLVs, `vfpf_ucast_filter_tlv`, `vfpf_update_tunn_param_tlv`, `pfvf_update_tunn_param_tlv`, coalescing TLVs, and `vfpf_bulletin_update_mac_tlv`. The unions `union vfpf_tlvs` and `union pfvf_tlvs` reserve the fixed 1024-byte mailbox size. `struct qed_bulletin_content` is the PF-published shared status structure, and `struct qed_vf_iov` is the per-hwfn VF runtime container.

### Control Flow
The header describes the control vocabulary consumed by `qed_vf.c`. Every request begins with `vfpf_first_tlv`, which carries a physical reply address, then optional typed TLVs, and ends with `CHANNEL_TLV_LIST_END`. PF responses embed `pfvf_tlv` headers with `PFVF_STATUS_*` status codes. Acquisition negotiates VF capabilities, requested resources, bulletin address/size, PF capabilities, device identity, queue/status-block IDs, stats locations, and fastpath HSI compatibility. Later TLVs use relative queue IDs and optionally `CHANNEL_TLV_QID` when the PF negotiated queue-QID support.

### State, Persistence, And Dependencies
`struct qed_vf_iov` stores mailbox pointers and DMA addresses, a mutex and TLV offset cursor, the coherent bulletin board and shadow, saved acquisition response, legacy-HSI compatibility state, registered status-block pointers, and doorbell-bar mode. `struct qed_bulletin_content` persists PF-provided link parameters, link state, link capabilities, forced/suggested MAC, forced VLAN/default untagged flags, tunnel UDP ports, and a CRC/version pair for race detection. The header depends on QED L2/MCP types, Ethernet constants, QED queue CIDs, link parameter structures, and SR-IOV build configuration.

### Integration Points
When `CONFIG_QED_SRIOV` is enabled this header exposes the VF operations used by the rest of QED and QEDE: hardware prepare/release/reset, queue and vport commands, filtering, interrupt cleanup, coalescing, link/resource getters, bulletin polling, tunnel update preparation, and MAC bulletin requests. When SR-IOV is disabled, inline stubs return `-EINVAL`, `false`, `0`, or no-op behavior so callers can compile without VF support.

### Risks
The TLV structures are a hardware/firmware ABI, so layout, sizes, alignment, and enum values must remain compatible with PF firmware and older drivers. `CHANNEL_TLV_VPORT_UPDATE_MAX` assumes vport update TLV enum values stay sequential. `TLV_BUFFER_SIZE` constrains future extension space. Several fields are documented as deprecated but still required for backward compatibility. The fallback stubs can hide accidental VF calls in non-SRIOV builds until runtime paths observe `-EINVAL`.

### Test Signals
Validation should include compile-time structure size/layout checks where available, acquisition with old and new PF capability combinations, mailbox TLV list parsing, vport update enum iteration, SR-IOV enabled and disabled builds, bulletin CRC/version parsing, and queue-QID negotiation coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_vf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/Makefile

### Purpose
This Makefile wires the QEDE Ethernet driver into the kernel build. It declares the `qede.o` module/object for `CONFIG_QEDE` and selects the component objects that implement main device logic, fastpath, filtering, ethtool, PTP, optional DCB, and optional RDMA integration.

### Important APIs, Types, And Functions
The build variables are `obj-$(CONFIG_QEDE) := qede.o`, the base `qede-y` object list, `qede-$(CONFIG_DCB) += qede_dcbnl.o`, and `qede-$(CONFIG_QED_RDMA) += qede_rdma.o`.

### Control Flow
Kbuild includes `qede.o` only when `CONFIG_QEDE` is enabled. The base driver always links `qede_main.o`, `qede_fp.o`, `qede_filter.o`, `qede_ethtool.o`, and `qede_ptp.o`. DCB netlink callbacks are linked only under `CONFIG_DCB`, and RDMA hooks are linked only under `CONFIG_QED_RDMA`.

### State, Persistence, And Dependencies
There is no runtime state. The file persists build-time dependency decisions. It depends on Linux Kbuild conventions and on config symbols supplied by the kernel configuration.

### Integration Points
This is the compilation boundary for QEDE. It determines whether functions declared in `qede.h`, such as `qede_set_dcbnl_ops()` and RDMA event helpers, are backed by linked objects or compiled out via conditional code elsewhere.

### Risks
Missing an object in `qede-y` causes link failures or absent runtime functionality. Optional object guards must match the `#ifdef`/`IS_ENABLED()` guards in source files. Since `qede_dcbnl.o` depends on `edev->ops->dcb`, enabling DCB at build time still requires hardware/core-driver DCB support at runtime.

### Test Signals
Build coverage should include `CONFIG_QEDE=y/m`, `CONFIG_DCB` enabled and disabled, and `CONFIG_QED_RDMA` enabled and disabled. Link tests should verify no unresolved DCB/RDMA symbols appear for each matrix entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede.h

### Purpose
`qede.h` is the central private header for the QEDE network driver. It defines device state, statistics, queue structures, fastpath layout, VLAN/RSS/XDP/RDMA/PTP fields, feature flags, constants, and cross-file function prototypes used by the QEDE main, fastpath, filter, ethtool, DCB, PTP, and RDMA modules.

### Important APIs, Types, And Functions
Key structures are `struct qede_dev`, `struct qede_fastpath`, `struct qede_rx_queue`, `struct qede_tx_queue`, `struct qede_stats`, `struct qede_vlan`, `struct qede_rdma_dev`, `struct qede_coalesce`, and `struct qede_reload_args`. Important macros derive queue counts and queue indexes, including `QEDE_RSS_COUNT()`, `QEDE_TSS_COUNT()`, `QEDE_RX_QUEUE_IDX()`, `QEDE_TXQ_*` mapping helpers, `QEDE_QUEUE_CNT()`, and chip checks `QEDE_IS_BB()`/`QEDE_IS_AH()`. It declares externally implemented operations such as datapath transmit/poll, XDP, VLAN/filter configuration, RSS filling, ethtool setup, reload, MTU change, coalescing, aRFS, flower filters, and DCB hook installation.

### Control Flow
The header does not execute logic directly, but it defines the state transitions and call contracts shared by implementation files. `enum QEDE_STATE` distinguishes closed, open, and recovery states protected by `qede_lock`. `qede_reload_args` carries small mutation callbacks into reload flows so ethtool, MTU, feature, and XDP changes can update state at the correct point. Queue mapping macros convert between netdev TX queue IDs, fastpath IDs, traffic classes, and XDP queue IDs.

### State, Persistence, And Dependencies
`struct qede_dev` is the persistent per-netdev state: QED core device and ops pointers, netdev/pci/devlink objects, debug settings, flags, device info, fastpath arrays, requested and active queue counts, interrupt info, lock-protected state, RX buffer sizing, stats, RSS indirection/key/caps initialization bits, VLAN list and accept-any-VLAN state, delayed slowpath and periodic work, tunnel ports, aRFS state, WoL, RDMA, XDP program pointer, error/recovery flags, dump command state, and stats coalescing controls. Queue state persists DMA rings, producer/consumer indexes, handles passed to QED, NAPI status blocks, XDP metadata, and per-queue counters. Dependencies include Linux networking, workqueue, interrupt, BPF/XDP, TC flower, QED public interfaces, QED chain/HSi definitions, and optional CPU rmap/DCB/RDMA support.

### Integration Points
Every QEDE implementation file includes this header. The QED core driver provides hardware operations through `struct qed_eth_ops` and common ops; Linux netdev, ethtool, DCBNL, XDP, TC flower, VLAN, RFS, and PTP subsystems call into functions declared here. VF-specific behavior is visible through `QEDE_FLAGS_IS_VF` and `IS_VF()`, which ethtool and filter paths use to restrict PF-only stats or operations.

### Risks
The header concentrates ownership of many shared fields, so changes to queue counts, RSS initialization, feature flags, or reload callbacks can affect multiple subsystems. Queue index macros assume consistent `fp_num_rx`, `fp_num_tx`, `num_queues`, and `dev_info.num_tc` values. Statistics arrays in `qede_ethtool.c` use offsets into structs defined here, so struct field removal/renaming must update those arrays. Locking comments matter: `state` is protected by `qede_lock`, stats by `stats_lock`, and aRFS has its own spinlock. XDP and GRO_HW interactions depend on `xdp_prog` and MTU constraints being kept coherent.

### Test Signals
Build all optional configurations, run netdev open/close/reload paths, change queue/channel counts, enable XDP and GRO_HW, add/remove VLANs, exercise RSS indirection updates, collect ethtool stats, run per-queue coalescing, validate TX queue mapping under multiple traffic classes, and test VF versus PF behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_dcbnl.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_dcbnl.c

### Purpose
`qede_dcbnl.c` adapts Linux DCBNL rtnetlink operations to the QED core DCB operation table. It lets userspace query and configure DCB, PFC, ETS, CEE, IEEE application priorities, peer information, and DCBX state through the netdev's `dcbnl_ops`.

### Important APIs, Types, And Functions
Most functions are thin wrappers named `qede_dcbnl_*`. They get `struct qede_dev *edev = netdev_priv(netdev)` and delegate to `edev->ops->dcb` methods, passing `edev->cdev` and the DCBNL arguments. The static `qede_dcbnl_ops` table maps Linux callbacks such as `ieee_getpfc`, `ieee_setpfc`, `ieee_getets`, `ieee_setets`, `getstate`, `setstate`, `getpgtccfgtx`, `setpgtccfgtx`, `getapp`, `setapp`, peer CEE/IEEE queries, feature config, and DCBX config. `qede_set_dcbnl_ops()` installs the table on the netdev.

### Control Flow
There is almost no local policy. A DCBNL request enters through the kernel's rtnetlink DCB layer, the selected callback unwraps `qede_dev`, then calls the QED DCB op. The exception is `qede_dcbnl_ieee_setapp()`, which first calls `dcb_ieee_setapp(netdev, app)` to update the kernel DCB application table; only if that succeeds does it call the hardware/core `ieee_setapp` method.

### State, Persistence, And Dependencies
This file keeps no private state. Persistent changes live in the kernel DCB app table and in firmware/core-driver DCB state managed by QED. It depends on `CONFIG_DCB` build selection, `<net/dcbnl.h>`, rtnetlink serialization expectations, and a populated `edev->ops->dcb` table.

### Integration Points
`qede_set_dcbnl_ops()` is called by QEDE setup code when DCB support is available. The wrappers bridge Linux netdev DCBNL APIs to QED common hardware management. DCB configuration also interacts with traffic classes used by TX queue layout and with PFC/link behavior reported elsewhere through ethtool.

### Risks
The wrappers assume `edev->ops`, `edev->ops->dcb`, and every function pointer in the table are valid; there are no local NULL checks. If core DCB support is absent despite `CONFIG_DCB`, callbacks can crash. Error handling is delegated, so inconsistent return conventions in QED DCB ops would be visible directly to userspace. `ieee_setapp()` has a two-stage update, so failure after the kernel table update would need scrutiny for rollback behavior outside this file.

### Test Signals
Test with DCB enabled hardware/core ops, `dcbtool`/`lldptool` or netlink DCB commands for CEE and IEEE paths, PFC/ETS get and set, app priority add/delete, peer table reads, DCBX mode changes, and negative tests where unsupported DCB operations return clean errors rather than dereferencing missing ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_dcbnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_ethtool.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_ethtool.c

### Purpose
`qede_ethtool.c` implements QEDE's ethtool surface for PFs and VFs. It reports statistics, strings, driver/firmware information, link settings, rings, channels, RSS, coalescing, private flags, module EEPROM data, PTP timestamp info, self-tests, dumps, EEE, FEC, WoL, debug message levels, and tunables, and it selects a reduced VF ethtool operation table.

### Important APIs, Types, And Functions
The file defines stat descriptor arrays for RX queues, TX queues, and device stats, private flag names, self-test names, and forced-speed maps initialized by `qede_forced_speed_maps_init()`. Main callbacks include `qede_get_strings()`, `qede_get_ethtool_stats()`, `qede_get_sset_count()`, private flag get/set, link ksettings get/set, `qede_get_drvinfo()`, WoL get/set, message level get/set, `qede_nway_reset()`, `qede_get_link()`, flash, coalescing get/set including per-queue variants, ringparam get/set, pause get/set, register dump, MTU change, channel get/set, RSS hash fields and indirection/key get/set, RX NFC get/set delegation to filter code, self-test helpers, tunables, EEE, FEC, module EEPROM, dump operations, and `qede_set_ethtool_ops()`.

### Control Flow
Statistics collection first refreshes on-demand stats via `qede_fill_by_demand_stats()`, locks `qede_lock` around fastpath array traversal, emits per-RX, per-XDP-TX, per-regular-TX counters, then locks `stats_lock` for device stats. PF-only and chip-specific stats are filtered by `qede_is_irrelevant_stat()`. Link setting changes validate `can_link_change()`, map autoneg or forced speed to QED link params, and call `set_link()`. Ring and channel changes update requested counts or buffer counts and call `qede_reload()`, with channel changes also resetting RSS indirection when the RX queue count changes.

Coalescing reads representative RX and TX queue handles when open, while global and per-queue setters validate `QED_COALESCE_MAX`, call QED set-coalesce ops, and cache values in `coal_entry`. RSS callbacks expose TOP hash, indirection, key, and per-flow hash fields; setters reject unsupported hash functions, disallow RSS configuration on multi-hwfn 100G devices, update cached RSS state, and if the interface is open allocate a vport update and call `vport_update()`. Self-test offline loopback disables NAPI/interrupts, sets internal PHY loopback, crafts an Ethernet frame, manually posts a TX BD, polls for TX completion, polls RX CQEs for the same packet, restores normal link mode, and restarts NAPI/interrupts. Dump operations are stateful: `set_dump` stores a command and arguments in `edev->dump_info`, and `get_dump_data` executes the selected NVM or GRC dump then resets the state.

### State, Persistence, And Dependencies
Persistent driver state touched here includes debug levels, `wol_enabled`, queue/ring requested counts, RSS indirection/key/caps and initialization flags, stats coalescing usecs/ticks, netdev MTU/features, `coal_entry`, private recover-on-error flag, and dump command state. Hardware/firmware state is changed through QED common ops for link, pause, WoL, LED, NVM flash, module EEPROM, EEE, FEC, coalescing, debug level, and self-tests. Dependencies include Linux ethtool APIs, phylink link-mode helpers, PCI names, vmalloc, PTP helper `qede_ptp_get_ts_info()`, QED link and debug ops, QED chain/BD helpers for loopback self-test, and filter functions for RX NFC.

### Integration Points
`qede_set_ethtool_ops()` installs either full PF ops or reduced VF ops. The VF table omits PF-only capabilities such as link changes, pause, WoL, EEPROM/module, EEE/FEC, self-tests, physical ID, flash, and dumps, but keeps stats, RSS, rings, channels, coalescing, tunables, and RX NFC. Ettool RX NFC delegates to `qede_add_cls_rule()`, `qede_delete_flow_filter()`, `qede_get_cls_rule_entry()`, and `qede_get_cls_rule_all()` in `qede_filter.c`. MTU and channel changes integrate with reload logic and RDMA MTU notifications when enabled.

### Risks
Many callbacks assume `edev->ops->common` sub-ops are valid; PF/VF table separation reduces but does not eliminate bad capability combinations. Offset-based stats require the arrays to stay synchronized with structures in `qede.h`. Several setters change cached state before open-state hardware reconfiguration; failed `vport_update()` can leave desired cached RSS settings that apply on next reload. Loopback self-test manipulates rings directly and must restore link/NAPI even on errors. Dump command state is multi-call and global to the device, so concurrent ethtool dump users could interfere if not serialized by ethtool/netdev locking. Channel divisibility by `num_hwfns` is critical for CMT devices.

### Test Signals
Run `ethtool -S`, `-i`, `-k`, `-c`, `-C`, `-g`, `-G`, `-l`, `-L`, `-x`, `-X`, `-n`, `-N`, `--show-eee`, `--set-eee`, `--show-fec`, `--set-fec`, module EEPROM reads, private flags, message-level changes, and PF/VF operation comparisons. Exercise open and closed interfaces, multi-queue and multi-TC configurations, XDP-enabled stats, 100G CMT RSS rejection, coalescing error injection, self-test pass/fail paths, and dump command argument validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_filter.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_filter.c

### Purpose
`qede_filter.c` implements QEDE receive filtering and steering policy. It handles accelerated RFS filters, ethtool ntuple/classification rules, TC flower filters, VLAN filter quota management, promiscuous/all-multicast RX mode programming, multicast/unicast MAC filters, RSS parameter preparation, UDP tunnel port synchronization, XDP program reload, and VF bulletin callbacks for forced MAC and tunnel ports.

### Important APIs, Types, And Functions
Important local types are `struct qede_arfs_tuple`, `struct qede_arfs_fltr_node`, and `struct qede_arfs`. aRFS lifecycle functions include `qede_alloc_arfs()`, `qede_free_arfs()`, `qede_rx_flow_steer()`, `qede_configure_arfs_fltr()`, `qede_arfs_filter_op()`, `qede_process_arfs_filters()`, and `qede_poll_for_freeing_arfs_filters()`. VLAN/RX mode functions include `qede_vlan_rx_add_vid()`, `qede_vlan_rx_kill_vid()`, `qede_configure_vlan_filters()`, `qede_vlan_mark_nonconfigured()`, `qede_set_rx_mode()`, and `qede_config_rx_mode()`. Other exported functions include `qede_force_mac()`, `qede_udp_ports_update()`, `qede_fill_rss_params()`, `qede_set_mac_addr()`, `qede_fix_features()`, `qede_set_features()`, `qede_set_udp_tunnels()`, `qede_xdp()`, flow rule get/add/delete helpers, `qede_add_tc_flower_fltr()`, and `qede_get_arfs_filter_count()`.

### Control Flow
aRFS allocation creates a hash table, bitmap, and optional CPU rmap. `qede_rx_flow_steer()` rejects encapsulated or non-TCP/UDP IPv4/IPv6 packets, hashes into a bucket, searches for an existing tuple, updates or reprograms queue steering if found, or allocates a new filter node with a copied packet header, DMA maps it, enables the searcher for the filter mode if this is the first filter, and sends an asynchronous QED ntuple config. Firmware completion calls `qede_arfs_filter_op()`, which marks filters valid, clears `used`, and handles queue moves as delete-then-add sequences. Periodic processing removes invalid/expired filters, waits for flow expiry via RFS when enabled, and disables the searcher when the last filter is dequeued.

VLAN add stores every VID in `edev->vlan_list`. If the interface is open and there are hardware VLAN credits, it programs a unicast VLAN filter; otherwise it increments `non_configured_vlans` and enables accept-any-VLAN mode. VLAN removal deletes configured hardware filters, updates counters, and calls `qede_configure_vlan_filters()` to promote previously unconfigured VLANs or disable accept-any-VLAN when possible. RX mode changes are deferred by setting `QEDE_SP_RX_MODE`; `qede_config_rx_mode()` replaces secondary unicast filters, chooses regular or promiscuous accept flags, adds unicast filters while within MAC filter quota, configures multicast filters or multicast-promisc for allmulti/large lists, adjusts accept-any-VLAN, and calls QED RX-mode configuration.

Ntuple and TC flower parsing convert ethtool or flow-rule matches into `qede_arfs_tuple`. Supported keys are IPv4/IPv6 addresses, basic IP protocol, and exact TCP/UDP ports; unsupported masks, VLAN classification, MAC extensions, user data, and unsupported protocols are rejected. The selected tuple profile is one of 5-tuple, L4 port, source IP, or destination IP, and all installed filters must share the same searcher mode. Add paths build a minimal synthetic L2/L3/L4 header, enqueue and DMA-map it, configure firmware, and poll for completion. Delete paths configure removal, poll, and dequeue on success.

RSS preparation ensures a valid indirection table, random key, and default capabilities, then maps indirection entries to RX queue handles for vport update. UDP tunnel sync reads the kernel UDP tunnel NIC table and calls QED tunnel configuration, caching the successfully programmed VXLAN/Geneve port. XDP setup swaps the BPF program inside a reload callback, and feature fixing disables hardware GRO when XDP, large MTU, or software GRO constraints require it.

### State, Persistence, And Dependencies
Persistent state includes `edev->arfs` hash buckets, filter bitmap/count/mode, filter nodes with DMA mappings and firmware status, VLAN list and configured/non-configured counts, `accept_any_vlan`, cached tunnel destination ports, RSS arrays and initialization bits, `xdp_prog`, netdev features, and netdev MAC address. Hardware state is programmed through QED filter, vport, tunnel, ntuple, and aRFS searcher ops. Dependencies include Linux netdevice address lists, VLAN callbacks, UDP tunnel NIC API, RFS acceleration, DMA mapping, flow dissector and TC flower APIs, ethtool RX flow-rule conversion, BPF/XDP reference handling, and QED filter configuration modes.

### Integration Points
Netdev VLAN callbacks call VLAN add/kill. Netdev `ndo_set_rx_mode` schedules RX mode work. Ettool RX NFC calls classification add/delete/get functions. TC flower offload calls `qede_add_tc_flower_fltr()`. The QED firmware completion path calls `qede_arfs_filter_op()`. VF bulletin handling from `qed_vf.c` calls `qede_force_mac()` and `qede_udp_ports_update()`. Ettool RSS and vport open paths use `qede_fill_rss_params()`. Feature changes and XDP setup integrate with `qede_reload()`.

### Risks
aRFS filter lifecycle is asynchronous and lock-sensitive: nodes carry DMA mappings, `used` state, validity bits, firmware return codes, and can be freed by timeout/cleanup paths. The searcher supports only one filter mode while filters are installed, so mixed ntuple profiles fail. `qede_get_cls_rule_all()` and related get paths use bucket 0, while RFS dynamic filters hash across buckets; fixed ethtool/flower filters are inserted into bucket 0, so callers must not expect dynamic RFS entries in rule dumps. VLAN quota fallback deliberately enables accept-any-VLAN, expanding receive scope when filters exceed hardware credits. `qede_config_accept_any_vlan()` returns `0` even when `vport_update()` fails after logging, which can mask errors in callers. MAC change removes the old filter before setting and adding the new one; add failure can leave netdev MAC changed without the matching hardware filter. XDP reload relies on reference ownership noted in comments.

### Test Signals
Exercise VLAN add/remove above and below hardware filter credits, promisc/allmulti transitions, multicast lists over 64 entries, MAC changes on open and closed PF/VF devices, forced MAC bulletin updates, RSS initialization and invalid indirection reset, UDP tunnel table sync for VXLAN and Geneve, XDP attach/detach with GRO_HW feature changes, aRFS dynamic steering and expiry, ntuple add/delete/get for IPv4/IPv6 TCP/UDP exact matches, invalid masks and unsupported keys, TC flower drop/queue actions including VF queue action handling, firmware failure callbacks, and filter cleanup during close/recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_filter.c -->
