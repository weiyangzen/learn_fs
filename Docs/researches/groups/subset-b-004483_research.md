# subset-b-004483 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_ethtool.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_ethtool.c

## Purpose
`idpf_ethtool.c` is the IDPF driver's ethtool integration layer. It exposes vport state to userspace for RSS, ntuple flow steering, queue/channel sizing, ring descriptor sizing, interrupt coalescing, statistics, link settings, and timestamping capabilities. It is deliberately thin on hardware programming: most user requests are validated here, cached into `idpf_vport_config->user_config`, and then pushed to firmware or hardware through virtchnl helpers or a soft reset.

## Important APIs, types, and functions
- `idpf_set_ethtool_ops()` installs `idpf_ethtool_ops` on the netdev.
- Flow steering: `idpf_get_rxnfc()`, `idpf_set_rxnfc()`, `idpf_add_flow_steer()`, `idpf_del_flow_steer()`, plus protocol builders `idpf_fsteer_fill_ipv4()`, `idpf_fsteer_fill_udp()`, and `idpf_fsteer_fill_tcp()`.
- RSS: `idpf_get_rxfh_key_size()`, `idpf_get_rxfh_indir_size()`, `idpf_get_rxfh()`, and `idpf_set_rxfh()` operate on cached `struct idpf_rss_data`.
- Queue and ring controls: `idpf_get_channels()`, `idpf_set_channels()`, `idpf_get_ringparam()`, and `idpf_set_ringparam()`.
- Statistics: `struct idpf_stats`, `IDPF_STAT`, queue/port statistic arrays, `idpf_get_strings()`, `idpf_get_sset_count()`, and `idpf_get_ethtool_stats()`.
- Coalescing: `idpf_find_rxq_vec()`, `idpf_find_txq_vec()`, `idpf_get_q_coalesce()`, `idpf_set_q_coalesce()`, `idpf_set_coalesce()`, and per-queue variants.
- Link and timestamp reporting: `idpf_get_link_ksettings()`, `idpf_get_ts_info()`, `idpf_get_ts_stats()`, and `idpf_get_timestamp_filters()`.

## Control flow
Flow steering requests enter via ethtool rxnfc. Get paths lock the vport control mutex, read `flow_steer_list` under `flow_steer_list_lock`, and return either counts, a specific saved `ethtool_rx_flow_spec`, or all rule locations. Insert validates unsupported flow extensions, sideband capabilities, rule count, queue index, and duplicate locations. It then builds a `virtchnl2_flow_rule_add_del` rule for TCP/UDP IPv4 and sends `VIRTCHNL2_OP_ADD_FLOW_RULE`; only after firmware success does it cache the ethtool spec in sorted list order. Delete sends `VIRTCHNL2_OP_DEL_FLOW_RULE` first and then removes the cached list entry.

RSS get/set reads and writes the cached RSS key and LUT in `user_config.rss_data`. `set_rxfh` accepts only Toeplitz or no-change hash function, stores new key/LUT values, and if the vport is up calls `idpf_config_rss()` so the running device observes the change. If RXHASH is disabled, `get_rxfh` reports zeroed indirection entries while preserving the cached configured LUT.

Queue count and descriptor changes are staged in `user_config` and applied through `idpf_initiate_soft_reset()`. `set_channels` rejects simultaneous dedicated RX and TX queues, validates the combined plus dedicated counts against `max_q`, updates requested TX/RX queue counts, and rolls back if the queue-change soft reset fails. `set_ringparam` enforces min descriptor counts, aligns requested counts to hardware multiples, updates RX buffer queue descriptor counts for split queues, updates header split state, and triggers a descriptor-change soft reset.

Statistics are a stable userspace ABI. The string count and ordering are based on maximum queue counts, not the currently allocated queues, to avoid size changes between ethtool string/count/data ioctl phases. Runtime stats collection locks the vport, requires `IDPF_VPORT_UP`, uses RCU to walk queues, folds per-queue software stats into port-level counters with `u64_stats_sync`, emits real queue stats where queues exist, and fills missing max-queue slots with zeros.

Coalesce get maps a queue index to the owning `idpf_q_vector` for split or single queue models and reads static or dynamic ITR state. Set paths reject static usec changes while adaptive mode is enabled, clamp to `IDPF_ITR_MAX`, round odd ITR values down to even values, update both the live q-vector and persistent `user_config->q_coalesce`, and write static ITR to hardware immediately.

Timestamp ethtool paths report PHC index and socket timestamping modes only when PTP capability and clock registration are present. `get_ts_stats` combines vport timestamp counters with per-TX-queue skipped timestamp counts while preserving `u64_stats_sync` consistency.

## State and persistence behavior
Persistent user-facing settings are cached in `adapter->vport_config[np->vport_idx]->user_config`: requested queue counts, descriptor counts, RSS key/LUT, coalescing settings, header split flag, MAC/flow steering lists, and flow steering count. These settings survive queue resource teardown and are replayed by open/reset paths in `idpf_lib.c`. Live state exists in `vport->dflt_qv_rsrc`, q-vectors, queue stats, and PTP/timestamp counters. The file uses `idpf_vport_ctrl_lock()` for vport lifetime protection and spinlocks for list state.

## Dependencies and integration points
The file depends on Linux ethtool, netdevice, PTP timestamping, RCU, `u64_stats_sync`, and virtchnl2 flow rule structures. It integrates with IDPF helpers from `idpf.h`, `idpf_virtchnl.h`, and `idpf_ptp.h`: capability checks, `idpf_config_rss()`, `idpf_add_del_fsteer_filters()`, soft reset initiation, queue model helpers, interrupt ITR writes, and timestamp capability tests. It is installed from `idpf_cfg_netdev()` in `idpf_lib.c`.

## Risks and edge cases
- Ettool stats must keep constant count and order across queue changes; changing max-count based reporting would break userspace buffers.
- Flow steering cache and firmware must stay synchronized. Firmware success with later cache failure or list races would produce misleading rule state.
- `idpf_add_flow_steer()` checks `num_fsteer_fltrs > max`; an off-by-one interpretation around full capacity should be reviewed against firmware expectations.
- Per-queue coalesce uses `q_coalesce[q_num]` for both TX and RX; q index validation depends on callers and q-vector lookup.
- Soft reset rollback differs by operation: channel changes roll back requested counts, while descriptor changes rely on reset behavior after staging.
- Timestamp reporting depends on `adapter->ptp`; missing or partially initialized PTP state must return ethtool fallbacks or `-EOPNOTSUPP`.

## Test signals
Useful signals include `ethtool -x/-X` RSS key/LUT changes with interface up and down, `ethtool -L` queue count changes and rollback on injected reset failure, `ethtool -G` descriptor alignment and TCP data split toggles, `ethtool -C` and per-queue coalesce changes including adaptive/static conflicts, `ethtool -S` count stability before and after queue changes, ntuple TCP/UDP IPv4 add/delete/list tests, PHC/timestamp capability reporting with and without PTP support, and concurrency tests around reset/remove while ethtool queries run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_idc.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_idc.c

## Purpose
`idpf_idc.c` implements the IDPF Inter-Driver Communication integration used to expose RDMA-capable IDPF devices and vports as Linux auxiliary devices. It creates and removes core and per-vport auxiliary devices, passes mapped LAN register and MSI-X resources to the RDMA auxiliary driver, emits MTU/reset events, and exports callbacks that the RDMA side uses to bring vport devices up/down or request a reset.

## Important APIs, types, and functions
- Initialization and teardown: `idpf_idc_init()`, `idpf_idc_init_aux_core_dev()`, `idpf_idc_deinit_core_aux_device()`, and `idpf_idc_deinit_vport_aux_device()`.
- Auxiliary-device plumbing: `idpf_plug_core_aux_dev()`, `idpf_plug_vport_aux_dev()`, `idpf_unplug_aux_dev()`, `idpf_core_adev_release()`, and `idpf_vport_adev_release()`.
- Vport RDMA lifecycle: `idpf_idc_init_aux_vport_dev()`, `idpf_idc_vport_dev_up()`, `idpf_idc_vport_dev_down()`, and exported `idpf_idc_vport_dev_ctrl()`.
- Event and reset integration: `idpf_idc_vdev_mtu_event()`, `idpf_idc_issue_reset_event()`, and exported `idpf_idc_request_reset()`.
- Resource handoff: `idpf_idc_init_msix_data()` and the construction of `iidc_rdma_priv_dev_info::mapped_mem_regions`.

## Control flow
`idpf_idc_init()` is called after core device initialization and returns success when RDMA is unsupported or the device ops table has no IDC initializer. When RDMA is enabled, the device-specific `idc_init` callback typically builds the core auxiliary device through `idpf_idc_init_aux_core_dev()`. That function allocates `iidc_rdma_core_dev_info` and private info, records PF/VF function type, captures BAR LAN register mappings from `adapter->hw.lan_regs`, attaches RDMA MSI-X entries if available, and registers an auxiliary device named from the PCI vendor and `.rdma.core` suffix.

When the RDMA core auxiliary driver is ready, it calls exported `idpf_idc_vport_dev_ctrl(cdev_info, true)`. The IDPF side iterates allocated vports; for each RDMA-enabled vport it either allocates `iidc_rdma_vport_dev_info` from the virtchnl create-vport flags or re-plugs an existing vport auxiliary device, then registers a `.rdma.vdev` auxiliary child. When the RDMA core goes down, `idpf_idc_vport_dev_ctrl(..., false)` removes each vport auxiliary device but retains vport info for possible replug.

MTU soft resets call `idpf_idc_vdev_mtu_event()` before and after the change. The function locks the auxiliary device, verifies a bound driver, derives the RDMA auxiliary driver container, and calls its event handler with the selected event bit. Hard reset preparation similarly calls `idpf_idc_issue_reset_event()` for the core auxiliary device. RDMA-triggered reset requests call exported `idpf_idc_request_reset()`, set `IDPF_HR_FUNC_RESET` if no reset is already active, and queue `vc_event_task`.

Teardown paths unregister auxiliary devices with `auxiliary_device_delete()` and `auxiliary_device_uninit()`, free IDs from a file-local `IDA`, and release allocated IDC core/vport structures.

## State and persistence behavior
The persistent IDC state is stored on `adapter->cdev_info` and `vport->vdev_info`. Core private data contains function type, mapped register regions, RDMA protocol, PCI device, and optional RDMA MSI-X entries. Vport info contains vport ID, netdev, parent core auxiliary device, and the current auxiliary device pointer. The file does not persist hardware configuration; it publishes existing IDPF resources to another kernel driver. Auxiliary device IDs are allocated from a global `DEFINE_IDA`.

## Dependencies and integration points
This file depends on Linux auxiliary bus, IDA allocation, PCI driver data, IDPF virtchnl create-vport data, and `iidc_rdma_*` structures from the IDC/RDMA interface. It integrates with `idpf_lib.c` reset and MTU flows, with `idpf_main.c` remove/deinit through core/vport cleanup, and with device-specific ops that initialize IDC only for RDMA-capable hardware.

## Risks and edge cases
- The auxiliary device `name` is assigned from a stack buffer in both plug helpers. If `auxiliary_device_init/add` does not copy the name synchronously, this is a lifetime hazard and should be verified against auxiliary bus semantics.
- `idpf_idc_vport_dev_up()` returns only the last error observed while iterating vports; earlier failures can be overwritten by later success.
- Event delivery locks the device and checks `adev->dev.driver`, but concurrent unplug paths still require careful ordering to avoid use-after-free.
- Resource maps expose BAR virtual addresses and MSI-X entries to another driver; stale pointers after reset/remove would be high impact.
- RDMA reset requests are coalesced by reset-in-progress checks; tests should confirm repeated requests do not lose required state.

## Test signals
Build with RDMA/auxiliary support enabled, probe RDMA-capable PF/VF devices, confirm core and vport auxiliary devices appear and disappear on RDMA driver bind/unbind, validate mapped register region counts and MSI-X counts, exercise MTU changes and observe before/after RDMA events, request resets from the RDMA side, unload while auxiliary devices are bound, and run reset/remove races under KASAN/KCSAN or lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_idc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_lan_pf_regs.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_lan_pf_regs.h

## Purpose
`idpf_lan_pf_regs.h` defines the PF-side LAN register offsets and bit masks used by the IDPF driver. It covers queue tail doorbells, PF firmware mailbox rings, PTP command synchronization, interrupt dynamic control and ITR registers, miscellaneous interrupt cause registers, PCI function RID decoding, and PF reset trigger/status/control registers.

## Important APIs, types, and functions
- RX/TX queue registers: `PF_QRX_TAIL()`, `PF_QRX_BUFFQ_TAIL()`, and `PF_QTX_COMM_DBELL()`.
- PF mailbox: `PF_FW_ARQ*` and `PF_FW_ATQ*` base address, length, head, tail, overflow, critical, and enable masks.
- PTP command bits: `PF_GLTSYN_CMD_SYNC_EXEC_CMD_M` and `PF_GLTSYN_CMD_SYNC_SHTIME_EN_M`.
- Interrupts: `PF_GLINT_DYN_CTL()`, `PF_GLINT_ITR()`, `PF_GLINT_ITR_ADDR()`, `PF_GLINT_ITR_MAX_INDEX`, and `PF_GLINT_ITR_INTERVAL_M`.
- Other interrupt and identity registers: `PF_INT_DIR_OICR_*`, `PF_INT_PBA_CLEAR`, and `PF_FUNC_RID_*`.
- Reset registers: `PFGEN_RTRIG`, `PFGEN_RSTAT`, `PFGEN_CTRL`, and related bit masks.

## Control flow
This header has no runtime control flow. Device-specific register initialization code includes these constants to populate `idpf_reg_ops` register descriptors. Later code uses the resulting MMIO pointers for mailbox setup, interrupt enable/disable, queue tail writes, reset polling, and PTP direct clock command synchronization.

## State and persistence behavior
The definitions describe hardware state in BAR0. Writes to queue tail and TX common doorbell registers advance hardware producer indices. Mailbox length/head/tail registers define the control queue state. Dynamic interrupt and ITR registers control interrupt enablement and moderation. Reset registers trigger and report PF resets. The header itself stores no software state.

## Dependencies and integration points
The header relies on Linux `BIT` and `GENMASK` style macros provided by included driver context. It is paired with PF device ops setup and used indirectly by `idpf_main.c` hardware mapping, `idpf_lib.c` mailbox/interrupt/reset flows, and `idpf_ptp.c` direct PTP command reads when PF PTP registers are initialized.

## Risks and edge cases
- Register offsets and masks are hardware ABI. Any incorrect value can corrupt unrelated register programming or break reset/interrupt/mailbox operation.
- PF and VF register spacing differs substantially; using PF macros for VF devices would misprogram BAR offsets.
- ITR spacing helper arguments must match the selected hardware generation.
- Reset masks must align with firmware readiness semantics; otherwise reset completion polling can falsely pass or time out.

## Test signals
Validation comes from PF probe, mailbox initialization and virtchnl traffic, queue bring-up with correct tail writes, MSI-X interrupt delivery and moderation changes, PTP direct clock access on capable PFs, function reset trigger/recovery, and register trace comparison against hardware specifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_lan_pf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_lan_txrx.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_lan_txrx.h

## Purpose
`idpf_lan_txrx.h` defines the LAN transmit descriptor formats, descriptor bit fields, completion descriptor fields, context descriptor formats, and default RSS hash capability masks used by IDPF TX/RX datapath code. It is a hardware contract header rather than executable logic.

## Important APIs, types, and functions
- RSS definitions: `enum idpf_rss_hash`, `IDPF_DEFAULT_RSS_HASH`, and `IDPF_DEFAULT_RSS_HASH_EXPANDED`.
- Split queue TX completion fields: `IDPF_TXD_COMPLQ_*` masks and `struct idpf_splitq_4b_tx_compl_desc` / `struct idpf_splitq_tx_compl_desc`.
- Base TX descriptor fields: `struct idpf_base_tx_desc`, `struct idpf_base_tx_ctx_desc`, `enum idpf_tx_desc_dtype_value`, `enum idpf_tx_ctx_desc_cmd_bits`, `enum idpf_tx_desc_len_fields`, and `enum idpf_tx_base_desc_cmd_bits`.
- Tunnel/TSO/checksum fields: `IDPF_TXD_CTX_QW0_TUNN_*`, `IDPF_TXD_CTX_QW1_*`, `IDPF_TXD_QW1_*`.
- Flex descriptor support: `struct idpf_flex_tx_desc`, `struct idpf_flex_tx_sched_desc`, `struct idpf_flex_tx_tso_ctx_qw`, `union idpf_flex_tx_ctx_desc`, and flex command masks.

## Control flow
This header has no functions. TX datapath code builds descriptor quadwords by combining these masks with `FIELD_PREP()` and CPU-to-little-endian conversions, then hardware consumes descriptors from DMA rings. Completion code interprets completion descriptor fields and descriptor done values defined here.

## State and persistence behavior
The structures map DMA memory shared between CPU and NIC hardware. State is encoded in descriptor rings: buffer DMA addresses, command bits, header offsets, payload sizes, L2 tags, TSO length/MSS, tunnel metadata, completion type, queue ID, generation bit, and optional timestamp fields. The definitions themselves are stateless, but any layout change changes the DMA ABI.

## Dependencies and integration points
The header depends on `linux/bits.h` and standard endian types. It is consumed by single queue TX in `idpf_singleq_txrx.c`, split queue TX/RX files elsewhere in the IDPF driver, RSS configuration code, and feature validation in `idpf_lib.c`. It also complements virtchnl2 RX descriptor definitions included through other headers.

## Risks and edge cases
- Descriptor layout must exactly match hardware. Wrong bit positions for command, dtype, TSO, tunnel, or length fields can cause packet corruption, checksum failures, hangs, or dropped completions.
- Comments note reserved dtype and completion values; using reserved encodings may work on one device and fail on another.
- The `IDPF_TX_CTX_MSS_M` definition uses `GENMASK_ULL(50, 63)`, which is visually reversed from common high/low order and should be verified against macro behavior and usage.
- RSS hash masks must align with control-plane advertised capabilities or default RSS programming may request unsupported hashes.

## Test signals
Signals include successful TX with checksum offload, TSO, UDP tunnel, GRE tunnel, VLAN tag insertion, split queue completions, TX timestamps carried in flex flow descriptors, RSS default hash programming, descriptor ring dumps compared with expected bitfields, and hardware traffic tests with offloads enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_lan_txrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_lan_vf_regs.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_lan_vf_regs.h

## Purpose
`idpf_lan_vf_regs.h` defines VF-side LAN BAR register offsets and masks. It covers VF reset status, admin transmit/receive queue mailbox registers, queue tail doorbells, interrupt dynamic control and ITR layouts for multiple VF vector scaling modes, interrupt cause registers, and VF RSS key/LUT/HENA registers.

## Important APIs, types, and functions
- Reset: `VFGEN_RSTAT` and `VFGEN_RSTAT_VFR_STATE_M`.
- VF mailbox: `VF_ATQ*` and `VF_ARQ*` length, head, tail, overflow, critical, and enable fields.
- Queue tails: `VF_QTX_TAIL()`, `VF_QTX_TAIL_EXT()`, `VF_QRX_TAIL()`, `VF_QRX_TAIL_EXT()`, and `VF_QRXB_TAIL()`.
- Interrupt control: `VF_INT_DYN_CTL0`, `VF_INT_DYN_CTLN()`, `VF_INT_DYN_CTLN_EXT()`, `VF_INT_ITR0()`, `VF_INT_ITRN()`, `VF_INT_ITRN_64()`, `VF_INT_ITRN_2K()`, and `VF_INT_ITRN_ADDR()`.
- Mailbox interrupt cause: `VF_INT_ICR0_ENA1`, `VF_INT_ICR01`, and admin queue mask bits.
- RSS registers: `VF_QF_HENA()`, `VF_QF_HKEY()`, and `VF_QF_HLUT()`.

## Control flow
This header has no runtime control flow. VF device ops use it to initialize register tables and MMIO offsets. Probe-time device-type detection in `idpf_main.c` writes to `VF_ARQBAL` to distinguish VF from PF when the PCI class entry is generic.

## State and persistence behavior
The macros describe VF-visible hardware state. Mailbox registers control admin queue DMA rings, queue tail registers notify hardware of new TX/RX descriptors, interrupt registers enable and moderate MSI-X delivery, reset status reports VF reset progress, and QF RSS registers hold VF RSS programming when direct VF access is used. The file stores no software state.

## Dependencies and integration points
The header depends on bit-mask macros and is included by `idpf_main.c` for VF detection. It is also consumed by VF register ops initialization code in the driver, mailbox setup, interrupt code, queue register initialization, and RSS configuration paths.

## Risks and edge cases
- The VF register layout has several vector-count-dependent ITR formulas. Selecting the wrong formula for a device capability can direct ITR writes to the wrong register.
- Queue tail EXT and non-EXT offsets differ; incorrect choice can break queue progress.
- VF mailbox register order is not monotonic by name, so assumptions based on PF layout are unsafe.
- Probe's write/read VF test relies on `VF_ARQBAL` being writable for VFs and not behaving the same way for PFs; hardware changes could affect detection.

## Test signals
Validation includes VF probe through both explicit VF ID and generic class ID, successful admin queue negotiation, VF reset detection, TX/RX queue progress through tail writes, mailbox interrupt delivery, interrupt moderation changes across 16/64/2k vector layouts, and direct RSS programming where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_lan_vf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_lib.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_lib.c

## Purpose
`idpf_lib.c` is the central IDPF driver lifecycle and netdevice implementation file. It manages MSI-X vectors, mailbox interrupts, vport allocation and release, netdev creation, MAC filters, open/stop paths, queue resource reset, hard reset recovery, SR-IOV configuration, periodic service/statistics work, feature changes, MTU and MAC changes, DMA memory helpers, hardware timestamp NDOs, and the `net_device_ops` table.

## Important APIs, types, and functions
- Interrupt/vector management: `idpf_intr_req()`, `idpf_intr_rel()`, `idpf_req_rel_vector_indexes()`, vector LIFO helpers, and mailbox IRQ helpers.
- Vport/netdev lifecycle: `idpf_init_task()`, `idpf_vport_alloc()`, `idpf_cfg_netdev()`, `idpf_vport_open()`, `idpf_vport_stop()`, `idpf_vport_dealloc()`, `idpf_vport_rel()`, `idpf_deinit_task()`.
- Reset flows: `idpf_service_task()`, `idpf_vc_event_task()`, `idpf_init_hard_reset()`, `idpf_check_reset_complete()`, and `idpf_initiate_soft_reset()`.
- Netdev ops: `idpf_open()`, `idpf_stop()`, `idpf_set_rx_mode()`, `idpf_set_features()`, `idpf_change_mtu()`, `idpf_set_mac()`, `idpf_get_stats64()`, hwtstamp get/set, XDP hooks, and `idpf_netdev_ops`.
- Feature/filter state: MAC filter add/delete/restore/remove helpers, flow steering cleanup, `idpf_vport_get_hsplit()`, `idpf_vport_set_hsplit()`, and promiscuous mode handling.
- Datapath validation: `idpf_chk_tso_segment()` and `idpf_features_check()` enforce hardware offload limits before TX.
- DMA helpers: `idpf_alloc_dma_mem()` and `idpf_free_dma_mem()`.
- SR-IOV/IDC/PTP hooks: `idpf_sriov_configure()`, IDC init/deinit/event calls, and PTP hwtstamp integration.

## Control flow
Initial device bring-up is asynchronous. Probe schedules `vc_event_task` with `IDPF_HR_DRV_LOAD`; the event task sets `IDPF_HR_RESET_IN_PROG` and calls `idpf_init_hard_reset()`. Hard reset initializes the default mailbox, starts mailbox processing, runs virtchnl core init, and waits until `idpf_init_task()` creates all default vports. `idpf_init_task()` allocates max queues through virtchnl, creates a vport, initializes per-vport config lists and RSS data, configures a netdev, repeats until all default vports exist, registers netdevs, clears reset/load flags, and starts periodic stats collection.

Interface open locks vport control, sets real queue counts, allocates vport interrupt resources, queue resources, queue IDs, interrupt registers, queue MMIO registers, RX buffers, XDP RXQ info, enables interrupts, configures queues through virtchnl, maps queue vectors, enables queues and vport, restores MAC filters, configures RSS, and finally marks the vport up. Stop performs the reverse: carrier off, TX disable, disable vport/queues, unmap vectors, optionally delete queues after queue-count changes, remove feature filters, deinit interrupts and XDP RXQ info, release queues/vectors, and clear `IDPF_VPORT_UP`.

Soft reset is a preallocation-based queue resource replacement flow. It clones the current vport up to the `link_up` field, adjusts the clone for queue count, descriptor count, MTU, or RSC changes, stops the live vport or deletes queues if down, requests new queues from the control plane, copies the clone back into the real vport, reallocates vector indexes if needed, updates netdev queue counts, refills default RSS LUT if queue count changed and userspace did not customize RSS, and reopens the vport if it was up. On failure it tries to add back the old queues and reopen the old vport.

Hard reset detaches netdevs, closes running interfaces while remembering `IDPF_VPORT_UP_REQUESTED`, issues IDC reset events, tears down virtchnl core and mailbox, triggers or observes firmware reset, waits for reset completion, rebuilds mailbox and virtchnl core, waits for vport init completion, reattaches/reopens previously running netdevs, and initializes IDC.

Netdev feature changes are serialized by vport control. RXHASH toggles update RSS when the interface is up. GRO_HW changes trigger an RSC soft reset. LOOPBACK sends an enable/disable virtchnl command. RX mode synchronizes unicast/multicast MAC filter lists asynchronously when called under addr-list spinlock and updates promiscuous/all-multicast flags through control-plane messages.

## State and persistence behavior
Adapter state includes workqueues, flags, mutexes, MSI-X arrays, vector LIFO, vport arrays, netdev arrays, control-plane connection manager, mailbox state, and capability-derived device ops. Vport state includes queue/vector resources, default MAC, vport ID/index, link state, timestamp config, and `dflt_qv_rsrc`. Per-vport persistent user settings are kept in `idpf_vport_config->user_config`: MAC filters, flow steering filters, RSS data, requested queue/descriptor counts, header split flag, promiscuous flags, and coalescing settings. These survive vport queue resource resets and are restored during open/reset.

Concurrency relies on `adapter->vport_ctrl_lock` for vport/netdev lifetime and configuration, `vector_lock` for MSI-X stack allocation, `queue_lock`/virtchnl synchronization elsewhere, spinlocks for MAC and flow steering lists, RTNL around netdev close/open where needed, delayed work cancellation during deinit/remove, and bit flags for remove/reset/vport-up state. DMA control queue memory is allocated with contiguous DMA attributes and page-aligned size.

## Dependencies and integration points
The file integrates with Linux PCI, netdevice, workqueue, MSI-X, NAPI, DMA, XDP/XSK, SR-IOV, PTP hwtstamp, and libeth TX validation APIs. It delegates hardware/control-plane operations to IDPF modules: virtchnl message helpers, queue allocation/configuration, interrupt register setup, RSS, TX/RX datapaths, XDP, IDC, PTP, and device-specific register ops. `idpf_main.c` owns probe/remove around these library routines.

## Risks and edge cases
- Reset ordering is high risk: workqueue cancellation, mailbox teardown, vport deallocation, IDC events, and netdev unregister must not race with callbacks.
- Soft reset copies only part of `struct idpf_vport`; adding fields before `link_up` may unintentionally become cloned state, while fields after it are intentionally preserved.
- Queue-change rollback after failed add/open is best effort; failures can leave the interface down or partially restored.
- MAC filter operations can be asynchronous from `.set_rx_mode`; firmware failures may be observed later and cached state can temporarily diverge.
- Vector LIFO accounting must remain exact across default vport reserved vectors, RDMA-reserved vectors, vport releases, and queue count changes.
- `idpf_features_check()` and TSO fragment walking encode hardware descriptor limits; off-by-one errors can surface as TX hangs or corrupted offloads.
- Remove paths free stale registered netdevs even if reset recovery failed earlier; double free/unregister ordering needs continued lockdep/KASAN coverage.

## Test signals
Signals include probe/remove/load-failure cleanup, interface open/close cycles, queue count and descriptor-count ethtool resets, MTU changes with RDMA IDC events, RXHASH/GRO_HW/LOOPBACK feature toggles, MAC address and multicast/promiscuous changes, SR-IOV enable/disable including assigned VF rejection, hard reset injection and recovery with netdev reopen, XDP/XSK attach and traffic, TX offload boundary tests, DMA allocation failure injection, MSI-X vector exhaustion/RDMA reservation cases, and concurrent ethtool/netdev/remove/reset stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_main.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_main.c

## Purpose
`idpf_main.c` is the PCI module entry point for the IDPF Linux driver. It binds Intel PF/VF PCI IDs or a generic Ethernet programming-interface class ID, determines PF versus VF behavior, allocates the adapter, maps core BAR regions, creates driver workqueues, initializes device-specific operation tables, starts the asynchronous hard-reset/driver-load path, and tears everything down on remove or shutdown.

## Important APIs, types, and functions
- Module/PCI declarations: `MODULE_DESCRIPTION`, namespace imports, `idpf_pci_tbl`, `idpf_driver`, and `module_pci_driver(idpf_driver)`.
- Device type selection: `idpf_get_device_type()` and `idpf_dev_init()`.
- PCI lifecycle: `idpf_probe()`, `idpf_remove()`, and `idpf_shutdown()`.
- Hardware BAR setup: `idpf_cfg_hw()`.
- External lifecycle hooks used here: `idpf_vc_core_deinit()`, `idpf_deinit_dflt_mbx()`, `idpf_sriov_configure()`, `idpf_init_task`, `idpf_service_task`, `idpf_mbx_task`, `idpf_statistics_task`, and `idpf_vc_event_task`.

## Control flow
On probe, the driver allocates `struct idpf_adapter`, defaults requested TX/RX queue model to split queue, enables the PCI device, requests BAR0, enables PCIe PTM if available, configures a 64-bit coherent DMA mask, sets bus master, and stores adapter in PCI driver data. It then allocates init, service, mailbox, stats, and virtchnl-event workqueues, initializes debug message level, selects PF or VF device ops, maps the mailbox and reset-status windows using device-specific static register info, initializes adapter mutexes and delayed work items, initializes reset register descriptors, sets `IDPF_HR_DRV_LOAD`, and queues `vc_event_task` to perform the real driver-load reset and virtchnl initialization.

Device-type selection uses explicit PCI device IDs when available. For the generic class entry, `idpf_get_device_type()` temporarily maps the VF mailbox ARQBAL offset, writes a test value, and treats a successful read-back as VF; otherwise it selects PF. VF initialization sets `adapter->crc_enable`, while PF initialization uses PF device ops.

Remove sets `IDPF_REMOVE_IN_PROG`, cancels virtchnl event work, disables SR-IOV VFs if active, deinitializes virtchnl core, triggers a function reset to leave hardware clean, deinitializes the default mailbox, unregisters and frees any stale netdevs, destroys all workqueues, frees each vport config and coalescing array, frees adapter arrays and connection manager, destroys mutexes, clears PCI driver data, and frees the adapter. Shutdown cancels service/event work, deinitializes virtchnl and mailbox, and puts the device into D3hot on poweroff.

## State and persistence behavior
This file owns top-level adapter allocation and destruction, PCI driver data, workqueue lifetime, BAR mapping metadata in `adapter->hw`, adapter mutex lifetime, and the initial reset/load flags. It does not itself register netdevs or allocate vports; it starts the reset/event path that delegates that work to `idpf_lib.c`. BAR mappings are device-managed (`devm_ioremap`) for mailbox and reset windows.

## Dependencies and integration points
The file depends on Linux PCI, DMA, workqueue, module, and power-management APIs. It includes device ID definitions, VF register definitions for class-based detection, virtchnl declarations, and IDPF core headers. It integrates with PF/VF device ops initializers, register ops, virtchnl core init/deinit, mailbox setup, SR-IOV, and all delayed tasks implemented in `idpf_lib.c`.

## Risks and edge cases
- Generic class PF/VF detection writes to a VF mailbox offset; correctness depends on PF hardware not echoing the test value and the mapping being safe before normal BAR setup.
- Probe performs most initialization asynchronously. Any failure after queueing `vc_event_task` must be handled by later deinit paths, not normal probe unwinding.
- Remove must handle partially initialized adapters and reset-recovery failures, including stale registered netdevs and active VFs.
- Workqueue destroy ordering must follow cancellation/deinit paths so no delayed work can run after adapter memory is freed.
- `idpf_cfg_hw()` relies on `dev_ops.static_reg_info[0]` and `[1]` being initialized correctly for PF/VF before mapping.

## Test signals
Build and module load/unload for PF and VF IDs, probe through generic class ID, DMA mask failure injection, BAR request/map failure injection, PCIe PTM supported/unsupported paths, asynchronous init failure cleanup, remove during hard reset recovery, shutdown/poweroff behavior, SR-IOV active remove, and workqueue lifetime checks with KASAN/lockdep are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_mem.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_mem.h

## Purpose
`idpf_mem.h` defines the IDPF DMA memory descriptor used for control queues and convenience macros for reading and writing mailbox MMIO registers relative to a mapped mailbox BAR region.

## Important APIs, types, and functions
- `struct idpf_dma_mem` stores CPU virtual address `va`, DMA address `pa`, and allocation `size`.
- `idpf_mbx_wr32()`, `idpf_mbx_rd32()`, `idpf_mbx_wr64()`, and `idpf_mbx_rd64()` wrap `writel/readl/writeq/readq` against `a->mbx.vaddr + reg`.

## Control flow
This header has no runtime control flow. Callers allocate/free `struct idpf_dma_mem` through helpers in `idpf_lib.c` and use the mailbox macros to access admin/control queue registers.

## State and persistence behavior
`idpf_dma_mem` records DMA allocation metadata needed to free a coherent DMA block. The mailbox macros directly mutate or observe hardware MMIO state; they do not add locking, barriers beyond the MMIO accessors, or bounds checks.

## Dependencies and integration points
The header includes `linux/io.h` and is used by mailbox/control queue code throughout the IDPF driver. The DMA allocation/free implementation is in `idpf_lib.c`, while BAR mapping is initialized from `idpf_main.c`.

## Risks and edge cases
- Callers must ensure `mbx.vaddr` is valid and `reg` is within the mapped mailbox region; the macros do no validation.
- 64-bit MMIO access requires the target register and platform to support `readq/writeq` semantics.
- `struct idpf_dma_mem` must be kept in sync with allocation attributes; freeing with a stale size or address would corrupt DMA state.

## Test signals
Mailbox initialization, virtchnl send/receive traffic, DMA allocation/free failure injection, control queue teardown under reset/remove, and MMIO tracing for expected register offsets provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_ptp.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_ptp.c

## Purpose
`idpf_ptp.c` implements Precision Time Protocol and hardware timestamping support for IDPF. It negotiates PTP feature access, registers a Linux PHC, reads and adjusts the device clock through direct MMIO or mailbox commands, maintains cached PHC time for 32-bit timestamp extension, manages TX timestamp latch allocation and release, enables RX timestamping on queues, and provides PTP clock callbacks.

## Important APIs, types, and functions
- Feature access: `idpf_ptp_get_features_access()` and internal `idpf_ptp_get_access()`.
- Clock reads: `idpf_ptp_read_src_clk_reg_direct()`, `idpf_ptp_read_src_clk_reg_mailbox()`, and `idpf_ptp_read_src_clk_reg()`.
- Cross timestamping: direct/mailbox helpers and `idpf_ptp_get_crosststamp()` when platform support exists.
- PHC operations: `idpf_ptp_gettimex64()`, `idpf_ptp_settime64()`, `idpf_ptp_adjtime()`, `idpf_ptp_adjfine()`, `idpf_ptp_do_aux_work()`, and capability setup in `idpf_ptp_set_caps()`.
- Cached timestamp extension: `idpf_ptp_update_cached_phctime()`, `idpf_ptp_tstamp_extend_32b_to_64b()`, and `idpf_ptp_extend_ts()`.
- Timestamp mode and latches: `idpf_ptp_request_ts()`, `idpf_ptp_set_timestamp_mode()`, `idpf_ptp_set_rx_tstamp()`, `idpf_tstamp_task()`, and release helpers.
- Lifecycle: `idpf_ptp_init()`, `idpf_ptp_create_clock()`, `idpf_ptp_release()`, and `idpf_ptp_get_txq_tstamp_capability()`.

## Control flow
PTP init first checks the virtchnl PTP capability, allocates `adapter->ptp`, initializes register offsets through device ops if available, obtains PTP capabilities via mailbox, derives access mode for each feature, initializes the direct clock read spinlock, registers the PHC, schedules periodic PHC-cache work if the clock can be read, programs the base increment value when adjustment is supported, and initializes clock time from realtime when settime is supported. Failure unwinds the PHC worker, clock registration, and allocated state.

Clock read dispatch depends on negotiated access. Direct access serializes with `read_dev_clk_lock`, writes shadow-time enable and execute command bits, captures optional system pre/post timestamps, and reads low/high clock registers. Mailbox access wraps `idpf_ptp_get_dev_clk_time()` or `idpf_ptp_get_cross_time()`. PHC get/set/adjust callbacks translate Linux PTP requests to these lower-level operations and update cached PHC time after set/adjust.

The periodic PTP auxiliary worker refreshes `adapter->ptp->cached_phc_time` and `cached_phc_jiffies` every 500 ms and writes the same cached time into each live RX queue. RX/TX timestamp extension uses the cached 64-bit PHC value plus the low 32 bits from hardware; if the cache is older than two seconds, `idpf_ptp_extend_ts()` increments discarded stats and returns zero.

TX timestamp requests allocate an entry from `tx_q->cached_tstamp_caps->latches_free` under spinlock, hold an skb reference, mark `SKBTX_IN_PROGRESS`, move the latch to `latches_in_use`, and return the negotiated index for the descriptor. Release paths cancel pending timestamp work, free unused latches, consume skb references for in-use latches, increment flushed stats, and free vport timestamp capability state.

Timestamp mode changes validate TX type, enable/disable PTP flags on all RX queues depending on `rx_filter`, normalize filters to NONE or ALL, and store the resulting `kernel_hwtstamp_config` on the vport.

## State and persistence behavior
Adapter PTP state lives in `struct idpf_ptp`: PHC registration, capability bits, access modes, direct register pointers, base increment/max adjustment, cached PHC time, secondary mailbox metadata, and read lock. Vport timestamp state includes `tstamp_config`, `tx_tstamp_caps`, latch lists, per-latch skb references, and `tstamp_stats`. RX queues cache PHC time for timestamp extension and carry a PTP queue flag. State is recreated on driver load/reset and released during PTP teardown.

## Dependencies and integration points
The file depends on Linux PTP clock infrastructure, timekeeping cross timestamp APIs, PCI PTM/ART checks, IDPF virtchnl PTP mailbox commands, queue structures, timestamp stats, and `idpf_ptp.h` types. It integrates with ethtool timestamp reporting in `idpf_ethtool.c`, hwtstamp NDOs in `idpf_lib.c`, TX descriptor setup in datapath files, and queue/vport release paths.

## Risks and edge cases
- Timestamp extension depends on the cached PHC time being refreshed within two seconds; worker stalls or mailbox failures cause discarded timestamps.
- Direct clock reads require correct shadow-time command masks and register pointers; partial register initialization would return invalid time.
- Large `adjtime` values use non-atomic get/adjust/set, which can race real time progression and other adjusters.
- `idpf_ptp_adjfine()` logs mailbox errors but returns 0; callers may not see failure.
- Latch list handling must preserve skb references and list membership across completion, reset, and release.
- Platform cross timestamping is conditional on ARM arch timer or x86 ART/PTM/TSC-known-frequency support; unsupported platforms must degrade cleanly.

## Test signals
Validate PHC registration, `phc2sys`/`testptp` get/set/adjfine/adjtime, direct and mailbox clock-read devices, cross timestamp availability on supported platforms, RX and TX hardware timestamp traffic, stale cache discard behavior, latch exhaustion and release, reset/unload with outstanding timestamp skbs, ethtool `--show-time-stamping`, and mailbox failure injection for PTP commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_ptp.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_ptp.h

## Purpose
`idpf_ptp.h` declares the IDPF PTP and hardware timestamping data model and public interface. It defines PTP direct-register metadata, access modes, secondary mailbox info, TX timestamp latch tracking, vport timestamp capabilities, adapter-level PHC state, device timer results, inline capability checks, and stub implementations for builds without `CONFIG_PTP_1588_CLOCK`.

## Important APIs, types, and functions
- Register and command metadata: `struct idpf_ptp_cmd` and `struct idpf_ptp_dev_clk_regs`.
- Access classification: `enum idpf_ptp_access`.
- Mailbox and timer data: `struct idpf_ptp_secondary_mbx` and `struct idpf_ptp_dev_timers`.
- TX timestamp tracking: `enum idpf_ptp_tx_tstamp_state`, `struct idpf_ptp_tx_tstamp_status`, `struct idpf_ptp_tx_tstamp`, and `struct idpf_ptp_vport_tx_tstamp_caps`.
- Adapter PTP state: `struct idpf_ptp`.
- Helpers: `idpf_ptp_info_to_adapter()`, `idpf_ptp_is_vport_tx_tstamp_ena()`, and `idpf_ptp_is_vport_rx_tstamp_ena()`.
- Public prototypes or stubs: PTP lifecycle, capability negotiation, device/cross time mailbox operations, clock set/adjust operations, vport timestamp capability fetch, TX timestamp retrieval/request, timestamp mode set, timestamp extension, and timestamp work handler.

## Control flow
This header has no standalone runtime flow. With `CONFIG_PTP_1588_CLOCK`, it exposes real functions implemented in `idpf_ptp.c` and virtchnl PTP code. Without that config, it compiles inline no-op or `-EOPNOTSUPP` stubs so the rest of the driver can call PTP hooks conditionally without littering call sites with preprocessor checks.

## State and persistence behavior
The structs define where PTP state persists during driver runtime: PHC clock info and handle, cached PHC time and jiffies, register pointers, capability bits, feature access modes, secondary mailbox identity, TX latch free/in-use lists, per-latch skb state, and per-vport timestamp capability metadata. All state is volatile driver memory negotiated or initialized at probe/reset time.

## Dependencies and integration points
The header includes `linux/ptp_clock_kernel.h` and depends on kernel skb/list/spinlock types through included driver headers. It is included by `idpf_ptp.c`, `idpf_ethtool.c`, `idpf_lib.c`, and datapath code that requests or extends timestamps. It also declares mailbox-backed PTP helpers implemented in virtchnl-related files.

## Risks and edge cases
- Stub signatures must exactly match real-function signatures; any drift can create config-dependent build failures.
- Inline capability checks are intentionally simple pointer/access checks; callers still need vport/link/control locking where required.
- The flexible-array `tx_tstamp_status[]` in `idpf_ptp_vport_tx_tstamp_caps` requires correct allocation sizing by capability negotiation code.
- Direct register pointers must be initialized before direct access modes are used.

## Test signals
Build with PTP enabled and disabled, compile all call sites under both configs, validate timestamp capability checks before and after vport timestamp capability negotiation, exercise TX latch allocation sizing, and inspect static analysis for flexible-array allocation and register-pointer initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_singleq_txrx.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_singleq_txrx.c

## Purpose
`idpf_singleq_txrx.c` implements the single-queue IDPF TX/RX datapath. It builds base TX descriptors and context descriptors, maps skb data to DMA, handles checksum/TSO/tunnel offloads, cleans completed TX descriptors, allocates/refills RX buffers, decodes base and flex RX descriptors, runs XDP/libeth receive processing, updates stats, and provides the single-queue NAPI poll handler.

## Important APIs, types, and functions
- TX offload and mapping: `idpf_tx_singleq_csum()`, `idpf_tx_singleq_build_ctx_desc()`, `idpf_tx_singleq_map()`, `idpf_tx_singleq_dma_map_error()`, and public `idpf_tx_singleq_frame()`.
- TX completion: `idpf_tx_singleq_clean()` and `idpf_tx_singleq_clean_all()`.
- RX descriptor helpers: `idpf_rx_singleq_test_staterr()`, `idpf_rx_singleq_is_non_eop()`, base/flex checksum extractors, base/flex hash handlers, and base/flex field extractors.
- RX processing and refill: `idpf_rx_singleq_buf_hw_alloc_all()`, `idpf_rx_singleq_clean()`, and `idpf_rx_singleq_clean_all()`.
- XDP/libeth integration: `idpf_rx_singleq_process_skb_fields()`, `idpf_xdp_run_pass()`, `LIBETH_XDP_ONSTACK_BUFF`, and libeth RX/TX helpers.
- NAPI entry point: `idpf_vport_singleq_napi_poll()`.

## Control flow
TX starts in `idpf_tx_singleq_frame()`. It computes descriptor demand, stops the subqueue if available descriptors fall below the needed threshold, derives IPv4/IPv6 flags from the skb protocol, runs TSO setup, runs single-queue checksum setup, emits a context descriptor when TSO or tunnel metadata is needed, records the first TX buffer, calculates packet/byte accounting, maps the skb into one or more base descriptors, sets EOP/RS on the last descriptor, updates BQL, and rings the hardware tail unless xmit-more batching defers it.

Checksum setup handles outer and inner headers for encapsulated packets. It builds tunnel context fields for UDP/GRE/IP-in-IP/IPv6 tunnels, falls back to `skb_checksum_help()` when unsupported non-TSO offload is encountered, and rejects unsupported TSO combinations. It programs MAC/IP/L4 header length offsets and base descriptor command bits for IPv4, IPv6, TCP, UDP, and SCTP.

DMA mapping maps the linear skb first, then each fragment, splitting any segment larger than the hardware maximum descriptor data size. On mapping failure it increments DMA error stats, unmaps already mapped buffers through libeth completion helpers, clears a TSO context descriptor if one was consumed, and updates the hardware tail to keep queue state coherent.

TX clean walks from `next_to_clean`, skips context descriptors, checks the watched EOP descriptor's done dtype, completes the skb and all associated fragments through libeth, advances ring cursors with wrap handling, updates queue packet/byte stats, and wakes the netdev queue when descriptor availability exceeds the wake threshold and the vport/carrier are up.

RX clean loops until packet budget is exhausted or the next descriptor lacks DD. It uses a DMA read barrier before descriptor fields, extracts packet length and ptype from either base or flex descriptor format, attaches the buffer to an on-stack libeth XDP buffer, advances the ring, handles non-EOP aggregation and RX error descriptors, runs XDP/GRO processing with checksum/hash field population, saves partial XDP state, refills cleaned buffers, updates packet/byte stats, and returns packets processed.

The NAPI poll handler handles budget-zero netpoll by cleaning TX only. Otherwise it fairly divides budget across RX queues and TX queues on the q-vector. If work remains, it enables writeback-on-ITR and returns budget; if complete, it completes NAPI and reenables interrupts or leaves writeback-on-ITR for busy-polling.

## State and persistence behavior
TX state lives in descriptor rings (`base_tx`, `base_ctx`), `tx_buf` metadata, `next_to_use`, `next_to_clean`, watched `rs_idx`, BQL accounting, queue stats, and hardware tail registers. RX state lives in descriptor rings, `rx_buf` page-pool/netmem entries, XDP saved buffer state, `next_to_clean`, `next_to_alloc`, `next_to_use`, queue stats, ptype lookup table, page pool, and tail registers. State is volatile per queue and rebuilt on vport open/reset.

## Dependencies and integration points
The file depends on Linux skb, DMA mapping, NAPI, XDP, page pool, BQL, checksum/GSO metadata, and `net/libeth/xdp.h`. It consumes descriptor definitions from `idpf_lan_txrx.h` and virtchnl2 RX descriptor definitions, queue helpers/macros from `idpf.h`, TSO/drop/hardware-tail helpers from other IDPF files, and interrupt helpers from vport interrupt code. It is selected when the negotiated queue model is single queue.

## Risks and edge cases
- Descriptor cursor arithmetic is high risk; wrap handling must keep `tx_buf`, descriptor pointers, and negative `ntc` arithmetic synchronized.
- DMA mapping error unwind must free every mapped fragment and not unmap unmapped context descriptors.
- Checksum/tunnel parsing must reject unsupported TSO cases but safely software-checksum unsupported non-TSO packets.
- RX DD detection relies on overlapping descriptor fields being zero for unused descriptors; descriptor format changes can break this assumption.
- Non-EOP RX handling and saved XDP buffer state must handle multi-buffer packets without leaks.
- Budget division across many queues can under-service queues if packet and TX completion work are imbalanced.
- Queue wake decisions depend on vport up and carrier state; incorrect state can cause stuck TX queues.

## Test signals
Run single-queue traffic with checksum offload, TSO, SCTP, IPv6 extension headers, UDP/GRE tunnels, GSO partial, VLAN traffic, xmit-more batching, DMA mapping failure injection, TX queue stop/wake stress, RX base and flex descriptor modes, XDP pass/drop/redirect if supported, multi-buffer RX, RX checksum/hash validation, netpoll budget-zero calls, interrupt moderation/NAPI completion behavior, and reset/open/close while traffic is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_singleq_txrx.c -->
