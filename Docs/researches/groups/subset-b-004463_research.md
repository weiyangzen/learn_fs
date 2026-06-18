# Research: subset-b-004463

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_ethtool.c

## Purpose
`iavf_ethtool.c` exposes the Intel Adaptive Virtual Function driver's userspace control surface through `struct ethtool_ops`. It translates ethtool requests into updates to `struct iavf_adapter`, queue rings, RSS configuration, Flow Director filters, and virtchnl admin-queue work scheduled by `iavf_main.c` and implemented by `iavf_virtchnl.c`.

## Important APIs, Types, And Functions
The local `struct iavf_stats` plus `IAVF_STAT`, `IAVF_QUEUE_STAT`, and `VF_STAT` define the ethtool statistic layout. `iavf_add_one_ethtool_stat`, `__iavf_add_ethtool_stats`, `iavf_add_queue_stats`, and `__iavf_add_stat_strings` copy adapter and ring counters into ethtool buffers while preserving queue counter consistency with `u64_stats_fetch_begin/retry`.

Core ethtool callbacks include `iavf_get_link_ksettings`, `iavf_get_sset_count`, `iavf_get_ethtool_stats`, `iavf_get_strings`, `iavf_get_msglevel`, `iavf_set_msglevel`, `iavf_get_drvinfo`, `iavf_get_ringparam`, `iavf_set_ringparam`, coalesce getters/setters, RX classification getters/setters, channel count getters/setters, and RSS key/LUT getters/setters. `iavf_set_ethtool_ops` installs the static `iavf_ethtool_ops` table on the netdev.

Flow Director support is the largest user-facing area. `iavf_ethtool_flow_to_fltr` and `iavf_fltr_to_ethtool_flow` map ethtool flow constants to `enum iavf_fdir_flow_type`. `iavf_parse_rx_flow_user_data` decodes two 32-bit user-defined flex words from `h_ext/m_ext.data`, enforcing full masks and a maximum offset of 504 bytes. `iavf_add_fdir_fltr_info` converts an `ethtool_rx_flow_spec` into `struct iavf_fdir_fltr`, validates full-or-empty masks via `iavf_validate_fdir_fltr_masks`, rejects duplicates, parses flex words, and builds a virtchnl add message with `iavf_fill_fdir_add_msg`. `iavf_add_fdir_ethtool` and `iavf_del_fdir_ethtool` are wired to `ETHTOOL_SRXCLSRLINS` and `ETHTOOL_SRXCLSRLDEL`.

Advanced RSS is handled by `iavf_adv_rss_parse_hdrs`, `iavf_adv_rss_parse_hash_flds`, `iavf_set_rxfh_fields`, and `iavf_get_rxfh_fields`, which translate ethtool RSS field requests into `iavf_adv_rss` records and `virtchnl_rss_cfg` messages. Standard RSS uses `iavf_get_rxfh`, `iavf_set_rxfh`, `iavf_get_rxfh_key_size`, and `iavf_get_rxfh_indir_size`.

## Control Flow
Most callbacks read or mutate adapter state under the netdev lock supplied by the core networking stack. Configuration callbacks usually validate request shape first, update cached adapter fields, then either call a synchronous helper or set an AQ flag. Examples: ring count changes set `adapter->tx_desc_count` and `rx_desc_count` and invoke `iavf_reset_step` if the interface is running; channel changes set `num_req_queues`, `IAVF_FLAG_REINIT_ITR_NEEDED`, and `IAVF_FLAG_RESET_NEEDED`; RSS field changes add/update an `iavf_adv_rss` list item and schedule `IAVF_FLAG_AQ_ADD_ADV_RSS_CFG`.

FDIR add flow is: ethtool command -> allocate `iavf_fdir_fltr` -> parse action/ring, flow-specific key/mask fields, optional flex words -> validate masks and duplicate status -> fill virtchnl protocol/action message -> insert into adapter FDIR list through `iavf_fdir_add_fltr`. Deletion maps a rule location to `iavf_fdir_del_fltr`, which marks the entry for PF deletion or frees inactive entries.

## State And Persistence Behavior
This file does not persist configuration outside memory. It updates adapter-owned state that survives normal down/up cycles and is replayed by reset/open paths: RSS key and LUT buffers, `adapter->hfunc`, ring descriptor counts, FDIR list entries, advanced RSS list entries, queue coalesce settings, and requested queue counts. Hardware state is asynchronous: many callbacks schedule virtchnl work and return before PF confirmation.

## Dependencies And Integration Points
It depends on Linux ethtool/netdev APIs, RCU and stats sync primitives, TC/RSS constants, `iavf.h`, `iavf_fdir.h`, `iavf_adv_rss.h`, and virtchnl definitions. It integrates with `iavf_main.c` for reset, RSS programming, queue state, and AQ scheduling; with `iavf_fdir.c` for FDIR validation/message building/list management; and with `iavf_adv_rss.c` and `iavf_virtchnl.c` for PF-visible advanced RSS programming.

## Risks
The main risks are asynchronous state races and mismatches between cached state and PF-confirmed state. FDIR and advanced RSS callbacks can return success after enqueueing work, so failures may surface later through virtchnl completions. Mask validation is intentionally strict; partial masks or unsupported flex offsets return errors. `iavf_set_rxfh` writes RSS LUT entries from user-provided indirection values without local queue-range validation in this function, so correctness depends on ethtool/core validation and PF/AQ handling. Reset-triggering operations run under netdev locking and can sleep.

## Test Signals
Useful signals include `ethtool -S` counter shape and per-queue zeroing beyond active queues, ring resize followed by reset and descriptor count preservation, coalesce get/set including per-queue adaptive ITR behavior, `ethtool -N/-n` FDIR add/list/delete paths for IPv4/IPv6/TCP/UDP/SCTP/AH/ESP/L2/user flows, duplicate and partial-mask rejection, `ethtool -X/-x` RSS key/LUT updates, advanced RSS field add/get errors, and channel changes with ADQ disabled/enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_fdir.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_fdir.c

## Purpose
`iavf_fdir.c` implements Flow Director filter validation, virtchnl add-message construction, diagnostics, duplicate detection, and adapter list management. It is shared by ethtool ntuple rules and TC u32 raw FDIR offload paths.

## Important APIs, Types, And Functions
Public functions are `iavf_validate_fdir_fltr_masks`, `iavf_fill_fdir_add_msg`, `iavf_print_fdir_fltr`, `iavf_fdir_is_dup_fltr`, `iavf_find_fdir_fltr`, `iavf_fdir_add_fltr`, and `iavf_fdir_del_fltr`. They operate on `struct iavf_fdir_fltr` from `iavf_fdir.h`.

Message construction is decomposed by protocol: `iavf_fill_fdir_eth_hdr`, IPv4/IPv6 helpers, TCP/UDP/SCTP helpers, AH/ESP helpers, `iavf_fill_fdir_l4_hdr` for L2TPv3-over-IP session ID, and UDP payload helpers for GTP-U, NAT-T-ESP, and PFCP. Constants for well-known UDP ports and flex offsets encode the subset of payload fields supported by the PF parser, such as GTP-U TEID/QFI, PFCP S field, and NAT-T ESP SPI.

## Control Flow
Validation first enforces full-or-empty masks for Ethernet type, IPv4/IPv6 addresses, TOS/traffic class, protocol, ports, SPI, and first L4 bytes. `iavf_fill_fdir_add_msg` then always emits an Ethernet protocol header and switches by `flow_type` to append IP and L4 headers. Each helper sets `VIRTCHNL_SET_PROTO_HDR_TYPE`, fills protocol header buffers from filter data, and marks selected fields with `VIRTCHNL_ADD_PROTO_HDR_FIELD_BIT`.

For UDP flex payloads, the code computes the offset relative to the UDP payload by subtracting Ethernet + IP + UDP header length. It accepts only a small set of exact offsets, rejects flex offsets before the payload, and rejects unsupported payload formats. For GTP-U, QFI selection requires seeing a PSC extension header marker before QFI extraction. For NAT-T-ESP, SPI 0 is rejected because that represents the IKE header format rather than ESP.

List management uses `adapter->fdir_fltr_lock`. `iavf_fdir_add_fltr` checks `iavf_fdir_max_reached`, inserts ethtool filters sorted by `loc` while raw TC u32 filters are not location-sorted, increments active accounting, marks the filter `ADD_REQUEST` when link is up or `INACTIVE` when down, and schedules `IAVF_FLAG_AQ_ADD_FDIR_FILTER` for live links. `iavf_fdir_del_fltr` finds by rule location or TC u32 handle, marks active filters `DEL_REQUEST`, frees inactive filters immediately, and reports busy for filters already in a transient state.

## State And Persistence Behavior
Filter state is entirely in memory on `adapter->fdir_list_head`, with active counters maintained by `iavf_inc_fdir_active_fltr` and `iavf_dec_fdir_active_fltr`. Hardware persistence is mediated through PF virtchnl messages stored in each filter's `vc_add_msg`. Filters may remain in inactive or pending states across link down/up and reset; `iavf_main.c` clears, disables, restores, or deletes them based on driver lifecycle.

## Dependencies And Integration Points
The file depends on `iavf.h`, Linux network header structs, endian helpers, `linux/bitfield.h`, virtchnl protocol header macros, and adapter locks/list heads from the main driver. It is called from `iavf_ethtool.c` for ethtool ntuple and from `iavf_main.c` TC u32 paths. Actual PF messaging is performed later by `iavf_virtchnl.c` when AQ flags are processed.

## Risks
The strict mask policy means many ethtool masks are rejected; this is intentional but easy to regress. Protocol header count increments must stay within virtchnl array capacity. Flex parsing is offset-sensitive and combines network-order fields with host-order `flex_words`, so endianness and alignment are important. `iavf_fdir_is_dup_fltr` skips raw filters and compares only flow, Ethernet, IP, and ext data, so action/queue differences do not make an ethtool rule unique. Deletion can return `-EINVAL` only when active filters exist but the requested filter does not, which affects empty-list semantics.

## Test Signals
Exercise full and partial masks for every supported flow type, UDP payload flex cases for GTP-U/PFCP/NAT-T-ESP, duplicate ethtool filters with different queues, raw TC u32 add/delete by handle, add while link is down then open, delete while add/delete is pending, max-filter exhaustion, and PF completion paths that transition from request/pending to active or freed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_fdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_fdir.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_fdir.h

## Purpose
`iavf_fdir.h` defines the Flow Director data model and public helper interface used by ethtool ntuple and TC u32 offload code. It is the contract between userspace rule parsing, local bookkeeping, and virtchnl PF programming.

## Important APIs, Types, And Functions
`enum iavf_fdir_fltr_state_t` describes the filter lifecycle: add request/pending, delete request/pending, disable request/pending, inactive, and active. Comments clarify that delete removes a VF-side object after PF success, while disable keeps the object and moves it inactive.

`enum iavf_fdir_flow_type` enumerates supported L2, IPv4, and IPv6 FDIR families: TCP, UDP, SCTP, AH, ESP, other IP, and non-IP L2. `IAVF_FLEX_WORD_NUM` is fixed at two because ethtool exposes two `m_ext.data` words.

Data structs split rule content into `iavf_fdir_eth`, `iavf_fdir_ip`, `iavf_fdir_extra`, and flex words. `struct iavf_fdir_fltr` is the central record: list linkage, state, flow type, data/mask pairs, virtchnl action, IP version, flex words, ethtool `flow_id`/`loc`/queue, TC u32 handle, and the prebuilt `virtchnl_fdir_add` message.

`iavf_is_raw_fdir` identifies TC u32 raw filters by checking whether the prebuilt virtchnl protocol header count is zero. Prototypes expose validation, add-message filling, printing, duplicate lookup, list add/delete, and lookup.

## Control Flow
The header itself has no runtime control flow except `iavf_is_raw_fdir`. Its state enum drives control in `iavf_fdir.c`, `iavf_ethtool.c`, `iavf_main.c`, and virtchnl completion handling. A normal ethtool rule is created with parsed key/mask fields, validated, converted to `vc_add_msg`, then inserted with an initial request or inactive state. A raw TC u32 rule is inserted with raw `vc_add_msg.rule_cfg.proto_hdrs.raw` bytes and is found/deleted by `cls_u32_handle`.

## State And Persistence Behavior
`struct iavf_fdir_fltr` is persistent only for the lifetime of the adapter instance. Its `state` field captures whether PF hardware has been requested, is pending, is active, or must be disabled/deleted. The embedded `vc_add_msg` allows the driver to replay or add the same rule after link changes and resets without reparsing the original user command.

## Dependencies And Integration Points
This header forward-declares `struct iavf_adapter` and requires virtchnl types through `iavf.h` include chains. It is consumed by FDIR implementation, ethtool RXNFC support, TC u32 offload, reset/down/open handling, and virtchnl completion code that advances filter states after PF responses.

## Risks
Any change to `struct iavf_fdir_fltr` affects multiple asynchronous paths and must preserve lock discipline around `adapter->fdir_fltr_lock`. The raw-filter heuristic depends on protocol header count being zero for TC u32 raw rules; if a raw rule ever uses counted protocol headers this classification breaks. Adding new flow types requires updates in ethtool mappings, message construction, print formatting, validation, and PF capability checks.

## Test Signals
Compile coverage should catch missing enum switch cases only where warnings are enabled, so runtime tests should add/list/delete ethtool and raw u32 rules, cycle link down/up, reset the VF, disable `NETIF_F_NTUPLE`, and verify state transitions and active counters remain consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_fdir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_main.c

## Purpose
`iavf_main.c` is the core PCI/netdev driver for Intel Adaptive Virtual Functions. It owns module registration, PCI probe/remove, adapter allocation, netdev operations, queue and interrupt setup, RSS initialization, VLAN/MAC/filter bookkeeping, admin queue scheduling, reset recovery, TC offloads, feature negotiation, suspend/resume, and integration with PTP and virtchnl support.

## Important APIs, Types, And Functions
The module exposes `iavf_init_module`/`iavf_exit_module` around a static `pci_driver`, and the netdev behavior is defined by `iavf_netdev_ops`. Public helpers used by other iavf files include `iavf_status_to_errno`, `virtchnl_status_to_errno`, `iavf_allocate_dma_mem_d`, `iavf_free_dma_mem`, `iavf_allocate_virt_mem`, `iavf_free_virt_mem`, `iavf_schedule_reset`, `iavf_schedule_aq_request`, `iavf_irq_enable`, `iavf_get_num_vlans_added`, `iavf_add_filter`, `iavf_promiscuous_mode_changed`, `iavf_down`, `iavf_set_queue_vlan_tag_loc`, `iavf_config_rss`, `iavf_schedule_finish_config`, `iavf_parse_vf_resource_msg`, `iavf_reset_step`, `iavf_free_all_tx_resources`, `iavf_free_all_rx_resources`, and `iavf_process_config`.

Key internal functions cover interrupt mapping/request/free, Tx/Rx ring allocation/configuration, VLAN and MAC filter list state, RSS key/LUT programming, q-vector/NAPI setup, staged initialization, watchdog processing, admin queue draining, reset replay, TC mqprio/flower/u32 offload, feature fix/set, queue shaper netlink ops, PCI lifecycle, and PM.

## Control Flow
Probe enables the PCI device, configures DMA, maps BAR0, allocates the netdev and adapter, initializes locks/lists/work items/wait queues/PTP state, then schedules the watchdog. Initialization proceeds asynchronously through `iavf_watchdog_step`: `__IAVF_STARTUP` initializes AdminQ and sends API version; `__IAVF_INIT_VERSION_CHECK` validates PF API and requests VF resources; `__IAVF_INIT_GET_RESOURCES` parses VF resource data; `__IAVF_INIT_EXTENDED_CAPS` exchanges VLAN V2/RXDID/PTP capabilities; `__IAVF_INIT_CONFIG_ADAPTER` configures netdev features, interrupts, queues, RSS, VLAN offload, QoS/PTP, and reaches `__IAVF_DOWN`.

Open allocates Tx/Rx descriptors, requests traffic IRQs, installs the primary MAC filter, restores inactive/disabled FDIR filters, configures rings and queues, enables NAPI, schedules queue enable, and unmasks interrupts. Close marks VSI down, preserves only safe AQ work, calls `iavf_down`, waits briefly for PF confirmation that resources are released, and restores deferred AQ bits. Reset disables interrupts, optionally requests PF reset, waits for reset detection and completion, rebuilds AdminQ/RSS/interrupts as needed, replays MAC/cloud/filter state, restores rings and queues if previously running, and either returns to running or down.

The watchdog and adminq tasks form the async control loop. `iavf_schedule_aq_request` ORs bits into `adapter->aq_required` and wakes the watchdog. `iavf_process_aq_command` sends one pending virtchnl or firmware command per pass in a fixed priority order. `iavf_adminq_task` drains ARQ events and calls `iavf_virtchnl_completion`, then logs and clears AQ error bits.

## State And Persistence Behavior
Adapter state is held in `adapter->state`, `last_state`, `flags`, `aq_required`, `current_op`, lists, queues, rings, RSS buffers, VLAN caps, QoS caps, PTP state, wait queues, and workqueue items. State is in-memory and rebuilt after PCI probe. Across netdev down/up and VF reset, the driver attempts to preserve user-visible configuration: MAC/VLAN filters, FDIR filters, cloud filters, advanced RSS, queue counts, RSS key/LUT, VLAN offload toggles, shaper values, and PTP configuration where supported.

List-backed state is protected by spinlocks: MAC/VLAN, cloud filters, FDIR filters, advanced RSS, and promiscuous flags. Netdev operations that mutate core state assert or take the netdev lock; some paths also use RTNL when changing registered queue counts. Wait queues synchronize `ndo_stop` and MAC-address changes with virtchnl completions.

## Dependencies And Integration Points
This file depends on PCI, netdevice, NAPI, MSI-X, DMA, ethtool, TC, flow dissector, net shaper, PTP, libie/libeth, virtchnl, and iavf shared AdminQ code. It integrates with `iavf_txrx.c` for transmit/receive rings, `iavf_virtchnl.c` for PF messages and completions, `iavf_ethtool.c` for ethtool ops installation, `iavf_fdir.c`/`.h` for FDIR state, `iavf_adv_rss.c` for advanced RSS, `iavf_ptp.c` for timestamping, and shared headers for hardware registers and status codes.

## Risks
The major risks are ordering and concurrency around async PF communication. AQ bit priority can starve lower-priority work if a command remains pending. Close/reset/remove paths must avoid freeing DMA resources before PF confirms queues are disabled. Reset can run while netdev operations are in flight, so lock ordering between RTNL, netdev lock, workqueue cancellation, and spinlocks is critical. Feature negotiation must tolerate PFs that omit optional capabilities or return invalid MTU/RXDID/VLAN data. TC and FDIR offloads accept only strict masks and limited actions, so user-visible errors must remain accurate. Several paths replay cached state after reset; leaks or stale flags can duplicate filters or leave PF state inconsistent.

## Test Signals
High-value tests include PCI probe/remove error unwinds, staged init retries and PF communication failure recovery, open/close with PF response delay, VF reset while running and while down, ring/channel/MTU changes that force reset, RSS AQ/register/PF modes, VLAN V1/V2 filtering and strip/insert toggles, MAC replacement wait outcomes, ntuple enable/disable and FDIR cleanup, TC mqprio ADQ add/delete, TC flower/u32 offloads, queue shaper set/delete and reset replay, suspend/resume, PTP capability negotiation, and AQ overflow/error register handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_osdep.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_osdep.h

## Purpose
`iavf_osdep.h` is the Linux OS abstraction header for shared iavf code. It provides type/header dependencies, MMIO access macros, memory wrapper structs, an allocation macro, and a debug macro expected by shared AdminQ and hardware helper code.

## Important APIs, Types, And Functions
The header includes Linux networking, PCI, TCP, VLAN, Ethernet, type, and non-atomic 64-bit I/O support. `wr32`, `rd32`, `wr64`, and `rd64` perform MMIO access relative to `struct iavf_hw::hw_addr`. `iavf_flush` reads `IAVF_VFGEN_RSTAT` to force posted MMIO writes to complete.

`struct iavf_dma_mem` records a coherent DMA allocation as virtual address, physical/DMA address, and size. `struct iavf_virt_mem` records a normal zeroed allocation as virtual address and size. `iavf_allocate_dma_mem` maps the shared-code signature to the Linux implementation `iavf_allocate_dma_mem_d`. `iavf_debug` gates `pr_info` output on `hw->debug_mask` and prefixes messages with PCI bus/device/function.

## Control Flow
This header has no standalone control loop. Its macros are invoked by shared AdminQ and main-driver code during hardware register access, queue setup, RSS programming, AdminQ setup/shutdown, and diagnostics. The memory structs are filled and freed by implementations in `iavf_main.c`.

## State And Persistence Behavior
No persistent state is stored by this header. It defines the shape of memory tracking objects and the register access model used to mutate hardware state. The debug macro reads `debug_mask` from the hardware struct; the memory wrappers carry allocation metadata until freed.

## Dependencies And Integration Points
It depends on `IAVF_VFGEN_RSTAT` being visible from register headers through include order. It integrates with `iavf_prototype.h` and AdminQ/shared code by presenting the OS-dependent names expected by Intel shared driver sources. The actual allocation/free functions live in `iavf_main.c`.

## Risks
MMIO macros assume `hw_addr` is valid and mapped; use after remove/unmap would be fatal. The 64-bit I/O include selects low-first non-atomic helpers for 32-bit kernels, so ordering assumptions must match hardware expectations. `iavf_allocate_dma_mem` ignores one shared-code parameter by design; changing shared signatures could silently break the macro. `iavf_debug` logs with `pr_info`, so broad debug masks can produce high log volume.

## Test Signals
Compile coverage across 32-bit and 64-bit configurations, AdminQ DMA allocation/free tests, reset/probe/remove register access under fault injection, and debug-mask toggling through ethtool message levels are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_osdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_prototype.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_prototype.h

## Purpose
`iavf_prototype.h` declares shared-code entry points that are needed before full hardware operations tables are initialized. It is the compile-time bridge from Linux-specific driver code to common AdminQ, RSS, hardware config parsing, and PF virtchnl send helpers.

## Important APIs, Types, And Functions
AdminQ lifecycle and command APIs include `iavf_init_adminq`, `iavf_shutdown_adminq`, `iavf_clean_arq_element`, `iavf_asq_send_command`, and `iavf_asq_done`. Debug and liveness helpers are `iavf_debug_aq`, `iavf_check_asq_alive`, `iavf_aq_queue_shutdown`, and `iavf_stat_str`.

RSS AdminQ helpers are `iavf_aq_set_rss_lut` and `iavf_aq_set_rss_key`. VF configuration and PF messaging helpers are `iavf_vf_parse_hw_config` and `iavf_aq_send_msg_to_pf`. The declarations use `struct iavf_hw`, `struct iavf_arq_event_info`, `struct libie_aq_desc`, `struct iavf_asq_cmd_details`, `struct iavf_aqc_get_set_rss_key_data`, and virtchnl resource/op/status types.

## Control Flow
The header itself has no runtime behavior. In `iavf_main.c`, initialization calls `iavf_init_adminq`, sends API/config messages to PF, polls `iavf_asq_done`, drains events with `iavf_clean_arq_element`, and shuts AdminQ down on reset/remove/failure. RSS configuration paths call the RSS AQ helpers when the negotiated mode requires firmware AdminQ programming.

## State And Persistence Behavior
The declared functions operate on `struct iavf_hw`, especially AdminQ rings, status, debug mask, and backpointer state. They do not define persistence here, but callers rely on them to initialize, tear down, and restore AdminQ/RSS state across reset and probe/remove.

## Dependencies And Integration Points
This header includes `iavf_type.h`, `iavf_alloc.h`, and `<linux/avf/virtchnl.h>`. It is included by `iavf_main.c` and shared AdminQ implementation files. It connects OS-dependent allocation/register helpers from `iavf_osdep.h` with common hardware code and Linux driver lifecycle.

## Risks
Prototype drift between this header and implementation files will break builds or, worse, ABI assumptions inside shared-code call sites. Many functions return `enum iavf_status`, so callers must consistently translate to Linux errno with `iavf_status_to_errno` when crossing kernel API boundaries. AdminQ command APIs take raw buffers and sizes; incorrect lifetime or size handling can corrupt PF/VF communication.

## Test Signals
Build coverage of all shared-code objects, AdminQ init/shutdown fault injection, PF message send/timeout paths, RSS AQ set key/LUT behavior, debug AQ tracing, and reset loops that repeatedly tear down and rebuild AdminQ are the practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_prototype.h -->
