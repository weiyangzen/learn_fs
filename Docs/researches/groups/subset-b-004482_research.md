# subset-b-004482 Research Report

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/rss.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/rss.c

## Purpose
This file implements the ICE PF-side virtchnl RSS handlers for SR-IOV VFs. It translates VF-provided `virtchnl_rss_cfg`, RSS key, LUT, hash-function, and hash-capability requests into ICE VSI and flow profile programming. It supports both classic key/LUT/hfunc operations and advanced RSS profile add/delete, including protocol-header parsing, raw packet pattern parsing, symmetric hashing, GTPU rule ordering, and per-VF context tracking.

## Important APIs, Types, And Functions
The exported handlers are `ice_vc_handle_rss_cfg()`, `ice_vc_config_rss_key()`, `ice_vc_config_rss_lut()`, `ice_vc_config_rss_hfunc()`, `ice_vc_get_rss_hashcfg()`, and `ice_vc_set_rss_hashcfg()`. Internal mapping tables `ice_vc_hdr_list` and `ice_vc_hash_field_list` convert `VIRTCHNL_PROTO_HDR_*` and field selectors to `ICE_FLOW_SEG_HDR_*` and `ICE_FLOW_FIELD_IDX_*` masks. `ice_vc_validate_pattern()` checks whether the PF package enables the derived packet type. `ice_vc_parse_rss_cfg()` builds `struct ice_rss_hash_cfg`. `ice_add_rss_cfg_wrap()` and `ice_rem_rss_cfg_wrap()` program or remove flow RSS profiles while keeping VF hash context state coherent.

## Control Flow
`ice_vc_handle_rss_cfg()` validates PF RSS support, advanced RSS capability negotiation, VF active state, algorithm range, and VSI existence. `VIRTCHNL_RSS_ALG_R_ASYMMETRIC` only updates the VSI hash mode to XOR or Toeplitz. Other algorithms update VSI hash mode to symmetric or standard Toeplitz and then choose either raw-pattern handling when `proto_hdrs.count == 0` and `tunnel_level == 0`, or protocol-header parsing for normal profiles. Raw profiles are parsed through the ICE parser, then installed with `ice_flow_set_parser_prof()` and tracked by packet-type group. Normal profiles are parsed, validated, added through `ice_add_rss_cfg_wrap()`, or removed through `ice_rem_rss_cfg_wrap()`.

## State And Persistence
The file updates persistent in-memory VF state in `vf->hash_ctx`, `vf->rss_prof_info`, and `vf->rss_hashcfg`. VSI RSS hash mode is persisted in `vsi->info.q_opt_rss` after `ice_update_vsi()` succeeds. GTPU contexts are cached separately for IPv4 and IPv6 to preserve TCAM ordering across later adds and deletes. Raw RSS profile state is cached per packet-type group. This state is runtime driver state, rebuilt through virtchnl requests after VF/PF reset rather than stored on disk.

## Dependencies And Integration Points
The code depends on virtchnl ABI definitions, ICE flow director/RSS profile helpers, parser profile helpers, VSI update admin queue calls, and VF state from `ice_vf_lib_private.h`. It is integrated by `virtchnl.c` through `ice_virtchnl_ops` entries for RSS opcodes. Error responses are converted to virtchnl status and returned with `ice_vc_send_msg_to_vf()`.

## Risks
The highest-risk behavior is rule ordering for overlapping GTPU extension-header, uplink, and downlink RSS profiles. Incorrect moveout, remove, or moveback logic can shadow more-specific profiles or leave stale hardware rules. Raw profile parsing depends on VF-provided packet bytes and masks, so length bounds and allocation failures matter. `ice_vc_parse_rss_cfg()` mutates protocol header field selectors for fragment cases, so callers must not expect the message buffer to remain logically unchanged.

## Test Signals
Useful tests include VF virtchnl add/delete RSS profiles for IPv4, IPv6, TCP, UDP, SCTP, ESP/NAT-T ESP, PFCP, L2TP, GRE, and GTPU EH/UP/DWN combinations; symmetric versus asymmetric algorithm changes; raw profile add/remove with valid and invalid packet lengths; RSS key length and LUT size validation; reset/replay behavior for `vf->hash_ctx`; and negative tests for inactive VFs, missing RSS PF flag, unsupported ptypes, invalid protocol counts, and package-disabled packet types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/rss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/rss.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/rss.h

## Purpose
This header exposes the ICE VF RSS virtchnl handlers implemented in `rss.c` to the rest of the ICE virtualization code. It is intentionally narrow: it forward-declares `struct ice_vf`, includes Linux scalar types, and publishes only the functions needed by the virtchnl dispatcher.

## Important APIs, Types, And Functions
The public API consists of `ice_vc_handle_rss_cfg()`, `ice_vc_config_rss_key()`, `ice_vc_config_rss_lut()`, `ice_vc_config_rss_hfunc()`, `ice_vc_get_rss_hashcfg()`, and `ice_vc_set_rss_hashcfg()`. The `bool add` parameter on `ice_vc_handle_rss_cfg()` lets the dispatcher reuse one handler for `VIRTCHNL_OP_ADD_RSS_CFG` and `VIRTCHNL_OP_DEL_RSS_CFG`. The remaining handlers map one-to-one to legacy RSS virtchnl operations.

## Control Flow
The header has no executable control flow. Its role in control flow is indirect: `virtchnl.c` includes it, assigns these functions into `struct ice_virtchnl_ops`, and calls them from `ice_vc_process_vf_msg()` after virtchnl message validation and opcode allowlist checks.

## State And Persistence
No state is defined in this header. All state changes occur through the opaque `struct ice_vf *` passed to the functions, including per-VF RSS contexts, capabilities, and VSI-backed hardware configuration.

## Dependencies And Integration Points
The header depends on `<linux/types.h>` for `u8` and `bool`, and on ICE VF definitions only through a forward declaration. This keeps compile-time coupling low while allowing `virtchnl.c` to integrate RSS support without importing `rss.c` internals.

## Risks
Because this is a dispatcher-facing interface, prototype drift between `rss.h`, `rss.c`, and `struct ice_virtchnl_ops` would break builds or misroute callbacks. The simple `u8 *msg` signature also means type safety is enforced inside implementations and by virtchnl validation, not by the header.

## Test Signals
Build coverage with `CONFIG_PCI_IOV` enabled is the primary signal. Runtime signals come from each RSS virtchnl opcode reaching the correct handler and producing a response through `ice_vc_send_msg_to_vf()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/rss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/virtchnl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/virtchnl.c

## Purpose
This file is the ICE PF-side virtchnl control plane for SR-IOV VFs. It receives mailbox requests, validates ABI messages, checks VF state and opcode allowlists, dispatches to operation handlers, and sends responses or asynchronous events back to VFs. The covered feature surface includes version/resource negotiation, link and reset notifications, MAC filters, promiscuous mode, VLAN v1/v2 filtering and offloads, RSS delegation, flexible RXDID query, QoS, PTP capability/time, and switchdev representor-specific behavior.

## Important APIs, Types, And Functions
Public functions include `ice_vc_notify_vf_link_state()`, `ice_vc_notify_link_state()`, `ice_vc_notify_reset()`, `ice_vc_send_msg_to_vf()`, `ice_vc_isvalid_vsi_id()`, `ice_vf_ena_vlan_promisc()`, `ice_is_vlan_promisc_allowed()`, `ice_virtchnl_set_dflt_ops()`, `ice_virtchnl_set_repr_ops()`, and `ice_vc_process_vf_msg()`. Static handlers implement each opcode. Two `struct ice_virtchnl_ops` instances, `ice_virtchnl_dflt_ops` and `ice_virtchnl_repr_ops`, provide mode-specific behavior while keeping the dispatcher table stable.

## Control Flow
Mailbox processing starts in `ice_vc_process_vf_msg()`. It extracts opcode, VF id, message pointer, and length from the AQ event, obtains the VF, locks `vf->cfg_lock`, rejects malicious or disabled VFs, validates message shape with `virtchnl_vc_validate_vf_msg()`, checks `ice_vc_is_opcode_allowed()`, then switches by opcode and invokes the selected operation table. `VIRTCHNL_OP_GET_VF_RESOURCES` negotiates `vf->driver_caps`, sets `ICE_VF_STATE_ACTIVE`, initializes VLAN stripping, and sends link state. Other paths validate active state and `ICE_VF_VSI_ID` before touching VSI resources.

## State And Persistence
The file mutates VF runtime state including `vf->vf_ver`, `vf->driver_caps`, `vf->vf_states`, `vf->num_mac`, `vf->dev_lan_addr`, `vf->hw_lan_addr`, `vf->legacy_last_added_umac`, VLAN capability cache `vf->vlan_v2_caps`, VLAN strip flags, promiscuous state bits, PTP capability bits, and mailbox maliciousness state. MAC hardware address behavior is intentionally persistent across VF reboot in `hw_lan_addr`, while `dev_lan_addr` can be cleared and repopulated. Hardware filter, VLAN, RSS, scheduler, interrupt, and PTP state is applied through ICE subsystem helpers.

## Dependencies And Integration Points
The dispatcher integrates with the admin queue mailbox, virtchnl ABI, VF library, queues, RSS, Flow Director, VLAN ops, filter programming, DCB/QoS, flex pipe RXDID, PTP, and switchdev representor mode. It sends all VF responses through `ice_aq_send_msg_to_vf()` via `ice_vc_send_msg_to_vf()`. Queue and FDIR handlers are declared outside this file and connected through `ice_virtchnl_ops`.

## Risks
This is a large security boundary: untrusted VFs can submit mailbox messages. Risks include missed capability checks, allowing untrusted MAC/LLDP/promiscuous/VLAN actions, stale allowlist state after capability negotiation, inconsistent SVM/DVM VLAN handling, failure to restore VLAN filtering after deletes, and races around VF removal if `cfg_lock` or reference handling is bypassed. The representor ops intentionally do not program firmware MAC filters, so default and switchdev behavior must stay aligned where required.

## Test Signals
High-value tests exercise full VF init ordering, invalid message validation, disabled and malicious VF paths, link/reset event broadcasts, admin-set MAC restrictions, legacy MAC add-before-delete ordering, untrusted LLDP rejection, trusted and untrusted MAC/VLAN limits, SVM and DVM VLAN v1/v2 capability matrices, VLAN stripping/insertion toggles with CRC strip disabled, RSS opcode dispatch, QoS capability responses, PTP caps/time responses, representor MAC/promisc behavior, and default unsupported-opcode responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/virtchnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/virtchnl.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/virtchnl.h

## Purpose
This header defines the ICE VF virtchnl operation interface, constants, and exported helpers used when PCI SR-IOV support is enabled. It centralizes the callback table that `virtchnl.c` fills and other virtualization modules call.

## Important APIs, Types, And Functions
Important constants include `ICE_MAX_VLAN_PER_VF`, `ICE_MAX_MACADDR_PER_VF`, `ICE_FLEX_DESC_RXDID_MAX_NUM`, and the intentionally static VF-visible `ICE_VF_VSI_ID`. `struct ice_virtchnl_ops` is the key type: it contains function pointers for version/resource negotiation, reset, MAC, queue, interrupt, RSS, stats, promiscuous mode, VLAN v1/v2, FDIR, QoS, queue bandwidth/quanta, and PTP handlers. The header declares dispatcher helpers such as `ice_vc_process_vf_msg()` and response/event helpers such as `ice_vc_send_msg_to_vf()`.

## Control Flow
The header itself has no executable flow, but its operation table defines the dynamic dispatch path used in `ice_vc_process_vf_msg()`. `ice_virtchnl_set_dflt_ops()` and `ice_virtchnl_set_repr_ops()` switch a VF between normal PF-controlled behavior and representor/switchdev behavior by changing the table pointer.

## State And Persistence
No storage is allocated here. The state implications are in the function signatures: nearly every operation receives `struct ice_vf *`, and several helpers receive `struct ice_vsi *` or `struct ice_vlan *` to mutate VF/VSI state and hardware filters.

## Dependencies And Integration Points
The header includes Linux types, bit operations, Ethernet constants, the kernel AVF virtchnl ABI, and `ice_vf_lib.h`. It provides stub inline functions returning no-op or `-EOPNOTSUPP` when `CONFIG_PCI_IOV` is disabled, allowing non-SRIOV builds to compile without the virtchnl implementation.

## Risks
The operation table must stay synchronized with both default and representor implementations. Adding a callback to only one table can create null pointer dispatch or mode-specific feature loss. The static `ICE_VF_VSI_ID` avoids leaking PF topology but requires all VF requests to use this synthetic id.

## Test Signals
Build both `CONFIG_PCI_IOV=y` and disabled configurations. Runtime tests should verify that all opcode callbacks are populated in both operation tables, unsupported no-IOV stubs return stable errors, and VF-visible VSI id validation accepts only `ICE_VF_VSI_ID`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/virtchnl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/Kconfig

## Purpose
This Kconfig file exposes the Intel Infrastructure Data Path Function driver to kernel configuration. It controls whether the `idpf` module is built and whether optional legacy single queue datapath support is compiled.

## Important APIs, Types, And Functions
`config IDPF` is a tristate option named "Intel(R) Infrastructure Data Path Function Support". It depends on `PCI_MSI` and `PTP_1588_CLOCK_OPTIONAL`, and selects `DIMLIB` and `LIBETH_XDP`. `config IDPF_SINGLEQ` is a boolean nested under `if IDPF`; it enables legacy single Rx/Tx queues without completion/fill queues.

## Control Flow
Kconfig has declarative build-time control flow. If `IDPF` is disabled, the driver object is not built. If it is `m`, the driver builds as the `idpf` module. If `IDPF_SINGLEQ` is enabled, the Makefile includes `idpf_singleq_txrx.o`, and runtime helpers such as `idpf_is_queue_model_split()` allow either single or split queue models.

## State And Persistence
The file persists user or distribution build choices in the kernel `.config`. It does not create runtime state, but the selected options change the compiled code paths and hotpath checks available in the driver.

## Dependencies And Integration Points
`PCI_MSI` is required for interrupt support. `PTP_1588_CLOCK_OPTIONAL` permits optional PTP integration. `DIMLIB` supports dynamic interrupt moderation and `LIBETH_XDP` supports the XDP/libeth integration used by the driver. `IDPF_SINGLEQ` integrates with the Makefile and conditional code under `CONFIG_IDPF_SINGLEQ`.

## Risks
The help text for `IDPF_SINGLEQ` notes increased driver size and runtime hotpath checks. A misspelled help word "runtme" is cosmetic. Incorrect dependency selection would surface as build failures in objects that assume MSI, PTP optional APIs, DIM, or XDP helpers.

## Test Signals
Build matrix coverage should include `IDPF=n`, `IDPF=m`, `IDPF=y`, and `IDPF_SINGLEQ=y/n`. With single queue disabled, split queue paths should remain functional and no unresolved references to `idpf_singleq_txrx.o` should exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/Makefile

## Purpose
This Makefile defines the object composition for the `idpf` driver module or built-in object. It maps Kconfig selections to the compilation units that implement control queues, device setup, ethtool, IDC, core library, PCI entry points, Tx/Rx datapath, virtchnl, PTP, XDP, and AF_XDP.

## Important APIs, Types, And Functions
The key build target is `obj-$(CONFIG_IDPF) += idpf.o`. The base `idpf-y` list includes `idpf_controlq.o`, `idpf_controlq_setup.o`, `idpf_dev.o`, `idpf_ethtool.o`, `idpf_idc.o`, `idpf_lib.o`, `idpf_main.o`, `idpf_txrx.o`, `idpf_virtchnl.o`, and `idpf_vf_dev.o`. Conditional entries add `idpf_singleq_txrx.o` for `CONFIG_IDPF_SINGLEQ` and PTP objects for `CONFIG_PTP_1588_CLOCK`. `xdp.o` and `xsk.o` are always included when IDPF is built.

## Control Flow
The Makefile controls link-time composition. Core mailbox/control queue code is always present for the driver. Single queue and PTP functionality are compiled only when their configuration symbols are enabled. XDP and XSK support are unconditional within the driver build, relying on Kconfig-selected dependencies.

## State And Persistence
No runtime state is defined. Build state is encoded in the object list generated by Kbuild, which determines which functions are available at runtime and which conditional branches can link.

## Dependencies And Integration Points
This file integrates the `idpf` directory with kernel Kbuild. It relies on Kconfig for `CONFIG_IDPF`, `CONFIG_IDPF_SINGLEQ`, and `CONFIG_PTP_1588_CLOCK`. The object ordering keeps control queue setup and device ops in the same final module as virtchnl and datapath consumers.

## Risks
Forgetting to add a new source object here would produce unresolved symbols or silently omit a feature. Conditional PTP object inclusion must match `idpf.h` declarations and runtime capability paths. Since `xdp.o` and `xsk.o` are unconditional under IDPF, their dependencies must remain selected or otherwise always available.

## Test Signals
Build tests with IDPF as module and built-in are the main signal. Additional build coverage should toggle `CONFIG_IDPF_SINGLEQ` and `CONFIG_PTP_1588_CLOCK` to ensure conditional object lists satisfy all references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf.h

## Purpose
This is the central private header for the IDPF driver. It defines adapter, vport, queue/vector resource, user configuration, capability, reset, register operation, statistics, RSS, and auxiliary RDMA integration structures. It also declares the driver-internal task, interrupt, reset, IDC, ethtool, and flow steering entry points used across IDPF compilation units.

## Important APIs, Types, And Functions
Core types include `struct idpf_adapter`, `struct idpf_vport`, `struct idpf_q_vec_rsrc`, `struct idpf_dev_ops`, `struct idpf_reg_ops`, `struct idpf_vport_config`, `struct idpf_vport_user_config_data`, `struct idpf_rss_data`, `struct idpf_vector_lifo`, and `struct idpf_queue_id_reg_info`. Key enums define initialization state, hard reset flags, vport reset causes, vport flags, user flags, and capability field offsets. Inline helpers include `idpf_is_queue_model_split()`, `idpf_xdp_enabled()`, `idpf_is_rdma_cap_ena()`, capability-check macros, reserved vector/vport accessors, register address translators, reset detection helpers, and netdev-to-private converters.

## Control Flow
The header shapes most IDPF control flow. `enum idpf_state` drives bring-up from version check to capabilities to software init. Hard reset flags distinguish load, function reset, reset in progress, removal, mailbox interrupt mode, and virtchnl core init. The register operation table lets PF and VF device files install hardware-specific mailbox, interrupt, reset, and PTP register functions. `idpf_for_each_vport()` provides a standard adapter vport iteration idiom.

## State And Persistence
`struct idpf_adapter` is the primary long-lived PCI device state: it stores virtchnl version, mailbox/error counters, reset state, hardware struct, MSI-X state, RDMA vectors, vport arrays, workqueues, negotiated capabilities, transaction manager, device ops, queue/vector locks, and PTP state. `struct idpf_vport` stores netdev-facing state, queue resources, XDP program, link state, stats, timestamps, and default MAC. `struct idpf_vport_user_config_data` persists user-requested RSS, coalescing, queue counts, descriptor counts, XDP, MAC filters, and flow steering across resets.

## Dependencies And Integration Points
The header pulls in PCI, netdevice, GRO, ethtool netlink, SCTP, virtchnl2, Tx/Rx, control queue, and Intel IDC RDMA headers. It integrates the control queue hardware struct via `idpf_controlq.h`, datapath definitions via `idpf_txrx.h`, and device-specific register setup via `idpf_dev.c` and `idpf_vf_dev.c`.

## Risks
This header has high blast radius: structure layout or semantic changes affect many compilation units and possibly auxiliary RDMA consumers. Register address helpers assume offsets from the control plane are valid and intentionally `BUG()` on impossible LAN-region misses. Capability field offsets use `offsetof()` into `virtchnl2_get_capabilities`, so ABI structure drift must be handled carefully. State flags require consistent bit operations across workqueues and reset paths.

## Test Signals
Build coverage is essential. Runtime signals include successful init state transitions, reset detection before and after mailbox setup, PF and VF register address mapping, user configuration restoration after soft/hard resets, XDP enable/disable behavior, RDMA capability gating, vport iteration across sparse arrays, and lockdep coverage for vport, vector, queue, and virtchnl buffer locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_controlq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_controlq.c

## Purpose
This file implements IDPF generic control queue lifecycle and ring operations. It creates mailbox send/receive queues, initializes descriptor rings and hardware registers, sends control messages, cleans completed send descriptors, receives mailbox messages, reposts receive buffers, and tears queues down.

## Important APIs, Types, And Functions
Public APIs are `idpf_ctlq_add()`, `idpf_ctlq_remove()`, `idpf_ctlq_init()`, `idpf_ctlq_deinit()`, `idpf_ctlq_send()`, `idpf_ctlq_clean_sq()`, `idpf_ctlq_post_rx_buffs()`, and `idpf_ctlq_recv()`. Internal helpers `idpf_ctlq_setup_regs()`, `idpf_ctlq_init_regs()`, `idpf_ctlq_init_rxq_bufs()`, and `idpf_ctlq_shutdown()` handle register copies, initial tail/head/base programming, receive descriptor buffer posting, and resource release.

## Control Flow
Initialization starts with `idpf_ctlq_init()`, which initializes `hw->cq_list_head` and calls `idpf_ctlq_add()` for each create-info entry. `idpf_ctlq_add()` allocates `struct idpf_ctlq_info`, sets ring indices, allocates ring resources, initializes RX descriptors or TX message pointer storage, copies register offsets, programs hardware, initializes the spinlock, and links the queue. Send flow checks descriptor availability under `cq_lock`, fills descriptors from `struct idpf_ctlq_msg`, stores original message pointers in `bi.tx_msg`, issues `dma_wmb()`, and writes tail. Receive and clean flows check the DD bit, issue `dma_rmb()`, copy status and payload context back to callers, clear descriptors, and advance ring indices.

## State And Persistence
Queue state lives in `struct idpf_ctlq_info`: `next_to_use`, `next_to_clean`, `next_to_post`, descriptor DMA memory, RX buffer or TX message pointer arrays, ring size, buffer size, and register offsets. `hw->cq_list_head` tracks all created queues. This is runtime hardware-driver state and is deallocated by `idpf_ctlq_deinit()` or `idpf_ctlq_remove()`.

## Dependencies And Integration Points
The implementation depends on `idpf_controlq.h` descriptor layout, DMA allocation helpers from `idpf_controlq_setup.c`, mailbox register accessors such as `idpf_mbx_wr32()`, and upper virtchnl code in `idpf_virtchnl.c` that sends, receives, cleans, and reposts buffers. It currently accepts mailbox TX and RX queue types; unsupported queue types return `-EBADR`.

## Risks
Ring index correctness and memory ordering are critical. Missing `dma_wmb()` before tail writes or `dma_rmb()` after DD checks can expose stale descriptors. `idpf_ctlq_send()` stores caller-owned message pointers until clean, so callers must keep them valid. RX posting logic can move existing buffers between descriptors; bugs can leak DMA buffers or starve the ring. Error handling must unwind partially initialized queues without freeing upper-layer TX buffers it does not own.

## Test Signals
Tests should cover queue init with TX/RX pairs, unsupported queue type failure and unwind, send with full and partially full rings, clean with DD unset/set and descriptor errors, receive direct and indirect messages, `-ENOMSG` on empty RX, repost with provided buffers and with ring-resident buffers, wraparound for all indices, and deinit after partial initialization failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_controlq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_controlq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_controlq.h

## Purpose
This private control queue header defines descriptor layout, descriptor flag bits, hardware/MMIO state, default constants, and internal allocation APIs for IDPF control queues. It bridges the public control queue API and the device-specific hardware structure used by the driver.

## Important APIs, Types, And Functions
Key macros are `IDPF_CTLQ_MAX_BUF_LEN`, `IDPF_CTLQ_DESC()`, `IDPF_CTLQ_DESC_UNUSED()`, and `IDPF_CTRL_SQ_CMD_TIMEOUT`. `struct idpf_ctlq_desc` is the hardware descriptor with flags, opcode, length, return value, virtchnl opcode/status, and direct or indirect parameters. Flag macros define DD, completion, error, function type, read, virtchnl, buffer, and host id fields. `struct idpf_hw` stores mailbox and reset MMIO mappings, LAN regions, adapter back pointer, ASQ/ARQ pointers, PCI identity, stopped flag, and the control queue list. Internal APIs declare `idpf_ctlq_alloc_ring_res()` and `idpf_ctlq_dealloc_ring_res()`.

## Control Flow
The descriptor and flag definitions are consumed by `idpf_controlq.c` to fill send descriptors, parse completed descriptors, initialize RX descriptors, and compute unused ring slots. The hardware struct is filled during PCI/device setup and passed into queue init and send/receive paths.

## State And Persistence
`struct idpf_hw` is long-lived adapter hardware state. It persists MMIO mapping information, control queue pointers, PCI ids, and adapter stopped state for the lifetime of the PCI device. Descriptor contents are DMA-visible transient state shared with hardware.

## Dependencies And Integration Points
The header includes `idpf_controlq_api.h` and Linux slab helpers. It depends on `idpf_dma_mem`, list heads, and MMIO resource types. It is included by `idpf.h`, `idpf_controlq.c`, and `idpf_controlq_setup.c`, making it the common contract for queue resource management.

## Risks
Descriptor layout must match hardware exactly; field size, endianness, or flag mistakes break mailbox communication. `IDPF_CTLQ_DESC_UNUSED()` leaves one ring slot empty to distinguish full from empty; changing it can corrupt ring accounting. Host id is a multi-bit field, not a simple flag, and must be masked correctly.

## Test Signals
Build-time structure and endian usage checks are important. Runtime signals include successful mailbox initialization, correct descriptor wraparound, accurate unused count, valid host id routing, and clean handling of DD/ERR/BUF/RD flag combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_controlq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_controlq_api.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_controlq_api.h

## Purpose
This header is the public-ish internal API for IDPF control queue management. It defines queue types, queue register descriptions, generic control queue message format, queue creation parameters, live queue state, mailbox opcodes, and callable queue lifecycle/send/receive functions.

## Important APIs, Types, And Functions
`enum idpf_ctlq_type` defines mailbox, config, event, and RDMA queue categories. `struct idpf_ctlq_reg` stores head, tail, length, base address, and masks. `struct idpf_ctlq_msg` is the software message abstraction with source type, host id, opcode, payload length, function/status union, mailbox cookie, and direct or indirect context. `struct idpf_ctlq_create_info` describes a queue to create. `struct idpf_ctlq_info` stores live ring indices, DMA descriptor memory, RX/TX backing arrays, and registers. Public functions include `idpf_ctlq_init()`, `idpf_ctlq_add()`, `idpf_ctlq_remove()`, `idpf_ctlq_send()`, `idpf_ctlq_recv()`, `idpf_ctlq_clean_sq()`, `idpf_ctlq_post_rx_buffs()`, and `idpf_ctlq_deinit()`.

## Control Flow
Upper layers create queues from `idpf_ctlq_create_info`, send `idpf_ctlq_msg` arrays on TX queues, clean send completions to recover status and caller-owned messages, receive messages from RX queues, and repost consumed DMA buffers. The API separates direct 16-byte descriptors from indirect payload-backed messages.

## State And Persistence
Live control queue state is represented by `struct idpf_ctlq_info`. The API stores ring state, lock state, DMA memory, buffer arrays, queue type/id, and register offsets for the lifetime of a created queue. Message payload DMA buffers are owned by callers on TX and returned to callers on RX until reposted.

## Dependencies And Integration Points
The header includes `idpf_mem.h` for DMA memory definitions and forward-declares `struct idpf_hw`. It is consumed by the queue implementation, hardware header, and virtchnl mailbox layer. Mailbox opcodes `idpf_mbq_opc_send_msg_to_cp` and `idpf_mbq_opc_send_msg_to_peer_drv` connect this queue abstraction to the control plane.

## Risks
Ownership rules are easy to misuse: send will hold message pointers until clean, while receive transfers indirect payload buffers to the caller until repost. `data_len` determines direct versus indirect handling, so inconsistent payload metadata can lead to invalid DMA addresses or copied context. Queue type support in implementation is narrower than the enum, so callers must not assume every enum value can be created.

## Test Signals
API tests should verify create-info register propagation, direct and indirect send/receive, status propagation through clean, caller buffer ownership, host id masking, source VM/VF/PF decoding, and expected failures for unsupported queue creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_controlq_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_controlq_setup.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_controlq_setup.c

## Purpose
This file owns DMA memory allocation and deallocation for IDPF control queue descriptor rings and receive buffers. It is separated from queue operation logic so lifecycle code can request or release resources through `idpf_ctlq_alloc_ring_res()` and `idpf_ctlq_dealloc_ring_res()`.

## Important APIs, Types, And Functions
Public functions are `idpf_ctlq_alloc_ring_res()` and `idpf_ctlq_dealloc_ring_res()`. Internal helpers allocate and free descriptor rings (`idpf_ctlq_alloc_desc_ring()`, `idpf_ctlq_free_desc_ring()`) and buffer arrays (`idpf_ctlq_alloc_bufs()`, `idpf_ctlq_free_bufs()`). The code uses `idpf_alloc_dma_mem()` and `idpf_free_dma_mem()` for DMA-visible memory and `kzalloc_objs()` for pointer/header arrays.

## Control Flow
Allocation first creates the descriptor ring sized as `ring_size * sizeof(struct idpf_ctlq_desc)`. It then allocates queue buffers. TX queues do not allocate DMA payload buffers here. RX queues allocate an array of `struct idpf_dma_mem *` and allocate mapped buffers for all but the last ring slot, matching the one-empty-slot ring convention. On failure, allocation unwinds previously allocated RX buffers and descriptor memory. Deallocation frees RX DMA buffers if present, frees the RX or TX backing array, then frees the descriptor ring.

## State And Persistence
Allocated state is stored in `cq->desc_ring` and `cq->bi.rx_buff` or `cq->bi.tx_msg`. RX buffers remain associated with descriptors until receive transfers them to upper layers or repost returns them. TX payload buffers are explicitly not owned by this file.

## Dependencies And Integration Points
This file depends on `idpf_controlq.h` for queue state and descriptor sizing. It is called from `idpf_ctlq_add()` during queue creation and `idpf_ctlq_shutdown()` during queue removal. The DMA helpers are platform/driver allocation wrappers.

## Risks
The ownership distinction between RX buffers and TX buffers is important. Freeing TX DMA payloads here would double-free upper-layer memory, while failing to free RX buffers leaks DMA memory. The "all but last" RX allocation must stay consistent with ring-full accounting. `idpf_ctlq_dealloc_ring_res()` assumes buffers were initialized enough for the selected queue type; callers must avoid deallocating uninitialized queue structs.

## Test Signals
Fault-injection tests should cover descriptor allocation failure, RX pointer array allocation failure, RX buffer header failure, DMA buffer failure after partial allocation, TX queue allocation with no RX buffers, and deallocation after partially and fully initialized queues. DMA leak detection and KASAN/KFENCE are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_controlq_setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_dev.c

## Purpose
This file provides PF-device-specific operations for IDPF. It initializes mailbox control queue register offsets, mailbox and data interrupt register addresses, reset registers, reset triggering, PTP command masks, IDC registration, and the `idpf_dev_ops` table for PF devices.

## Important APIs, Types, And Functions
The exported entry point is `idpf_dev_ops_init()`. Internal operations installed into `adapter->dev_ops.reg_ops` are `idpf_ctlq_reg_init()`, `idpf_intr_reg_init()`, `idpf_mb_intr_reg_init()`, `idpf_reset_reg_init()`, `idpf_trigger_reset()`, and `idpf_ptp_reg_init()`. `idpf_idc_register()` installs the PF IDC auxiliary core device callback. Constants include `IDPF_PF_ITR_IDX_SPACING`.

## Control Flow
`idpf_dev_ops_init()` calls `idpf_reg_ops_init()`, sets `adapter->dev_ops.idc_init`, and records static BAR resource ranges for mailbox and reset/status regions. Later, mailbox setup calls `ctlq_reg_init()` to translate PF firmware ATQ/ARQ registers into offsets relative to the mapped mailbox region. Interrupt setup maps mailbox and traffic dynamic control/ITR registers from capability-provided register chunks. Reset setup maps PF reset status, and reset trigger sets `PFGEN_CTRL_PFSWR`.

## State And Persistence
The file populates `adapter->dev_ops`, `adapter->dev_ops.static_reg_info`, `adapter->mb_vector.intr_reg`, per-queue-vector `intr_reg` fields, `rsrc->noirq_dyn_ctl`, `rsrc->noirq_dyn_ctl_ena`, `adapter->reset_reg`, and PTP command masks. This state persists for the lifetime of the adapter and is recalculated during device initialization or reset-related setup.

## Dependencies And Integration Points
It depends on `idpf_lan_pf_regs.h` for PF register constants, `idpf_virtchnl.h` for interrupt vector register discovery, and `idpf_ptp.h` for PTP state. It integrates with `idpf_main.c`, which selects PF or VF device ops based on PCI device id, and with control queue and interrupt setup paths that call the operation table.

## Risks
Register address translation is hardware-specific and sensitive to static region starts. Incorrect offsets can program the wrong BAR location. `idpf_intr_reg_init()` allocates register metadata for all reserved vectors and indexes by queue vector ids minus the mailbox vector; invalid vector indexes can produce bad register mappings. The NOIRQ vector setup reads `i` after the loop, relying on `i == num_vecs`.

## Test Signals
PF probe tests should verify static resource ranges, mailbox ATQ/ARQ register programming, mailbox interrupt enable behavior, data vector ITR addresses, NOIRQ dyn_ctl setup, reset trigger writes, reset status reads, PTP mask initialization, IDC registration, and error handling when available interrupt register chunks are fewer than requested vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_devids.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_devids.h

## Purpose
This header defines the PCI device ids recognized by the IDPF driver for PF and VF functions. It is a small shared include used by PCI probe/id-table code and device-type selection logic.

## Important APIs, Types, And Functions
The two definitions are `IDPF_DEV_ID_PF` with value `0x1452` and `IDPF_DEV_ID_VF` with value `0x145C`. There are no functions or structures.

## Control Flow
The ids influence probe-time control flow in `idpf_main.c`: matching PCI ids select the driver, and device id checks choose PF-specific `idpf_dev_ops_init()` or VF-specific `idpf_vf_dev_ops_init()`.

## State And Persistence
No runtime state is stored. The constants are compiled into the module PCI id table and device dispatch logic.

## Dependencies And Integration Points
The header is guarded by `_IDPF_DEVIDS_H_` and is included by IDPF PCI code. It integrates with Linux PCI matching through `PCI_VDEVICE(INTEL, ...)` entries elsewhere.

## Risks
An incorrect id prevents the driver from binding to supported hardware or can bind it to the wrong function type. PF/VF id confusion would select the wrong register operation table and break mailbox/reset setup.

## Test Signals
Probe tests should confirm both PF and VF PCI ids match the driver and route to the expected device ops. Static analysis can verify no duplicate or stale ids conflict with adjacent Intel drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_devids.h -->
