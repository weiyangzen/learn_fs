# subset-b-004378 Research

Grouped research for the listed Broadcom bnxt driver files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_sriov.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_sriov.c

## Purpose
Implements SR-IOV control for the bnxt Ethernet driver. On PFs it validates netdev VF operations, allocates VF bookkeeping and firmware mailbox buffers, reserves firmware resources for enabled VFs, creates VF representors in switchdev mode, disables and frees VFs, and mediates forwarded VF HWRM requests. On VFs it tracks PF-assigned MAC policy and asks the PF to approve local MAC changes.

## Important APIs, Types, And Functions
The externally visible netdev/PCI entry points are `bnxt_sriov_configure()`, `bnxt_cfg_hw_sriov()`, `__bnxt_sriov_disable()`, `bnxt_get_vf_config()`, `bnxt_set_vf_mac()`, `bnxt_set_vf_vlan()`, `bnxt_set_vf_bw()`, `bnxt_set_vf_link_state()`, `bnxt_set_vf_spoofchk()`, `bnxt_set_vf_trust()`, `bnxt_hwrm_exec_fwd_req()`, `bnxt_update_vf_mac()`, and `bnxt_approve_mac()`. The core state carrier is `bp->pf.vf[]`, an array of `struct bnxt_vf_info` entries containing firmware FIDs, PF-assigned MACs, VF-reported MACs, VLAN/BW/link/trust/spoof flags, and per-VF DMA HWRM request buffers.

Firmware command helpers include `bnxt_hwrm_func_vf_resc_cfg()` for new resource-manager VF reservation, `bnxt_hwrm_func_cfg()` for older fixed allocation, `bnxt_hwrm_func_buf_rgtr()` for registering VF request buffer pages, `bnxt_hwrm_func_vf_resource_free()` for teardown, `bnxt_hwrm_roce_sriov_cfg()` for RoCE VF limits, and forwarded-response helpers `bnxt_hwrm_fwd_resp()`, `bnxt_hwrm_fwd_err_resp()`, and `bnxt_hwrm_exec_fwd_resp()`.

## Control Flow
PF SR-IOV enable starts at `bnxt_sriov_configure()`. It rejects requests while the netdev is down, firmware reset is active, or VFs are assigned, then disables existing VFs before enabling a new count. `bnxt_sriov_enable()` calculates the largest feasible VF count from RX/TX/CP/stat/RSS/VNIC resources, allocates `bp->pf.vf`, DMA request pages, and the VF event bitmap, configures firmware resources, calls `pci_enable_sriov()`, and creates VF representors if `bp->eswitch_mode` is switchdev.

Disable flows through `bnxt_sriov_disable()` or `__bnxt_sriov_disable()`. Representors are destroyed first under `devl_lock()`. If VFs are assigned, the PF cannot call `pci_disable_sriov()` and instead forwards a PF driver unload async event to all VFs; otherwise it disables PCI SR-IOV and frees VF firmware resources. The wrapper then restores PF firmware resources under RTNL and netdev instance locks.

Forwarded VF requests are processed by `bnxt_hwrm_exec_fwd_req()`, which scans `bp->pf.vf_event_bmap`, clears pending bits, decodes the encapsulated HWRM request in the VF DMA buffer, and either executes it, rejects it, or synthesizes a PF-controlled response. MAC-related requests are constrained by PF-assigned MAC and trusted-VF state. Link query responses can be rewritten when the PF forced VF link up/down.

## State And Persistence Behavior
All state is in driver memory and firmware configuration, not on disk. The PF mirrors admin configuration in `bp->pf.vf[]` so it can report VF settings and replay selected parameters during reset (`__bnxt_set_vf_params()`). Hardware resource accounting mutates `bp->hw_resc` after VF reservation, and teardown re-queries/restores capabilities. VF request buffers are coherent DMA pages registered with firmware; `vf_event_bmap` is a bitmap of pending forwarded requests. VF-side `bp->vf.mac_addr` records the PF-assigned administrative MAC and is used to decide whether local MAC changes require PF approval.

## Dependencies And Integration Points
The file depends heavily on bnxt HWRM request infrastructure (`hwrm_req_init()`, `hwrm_req_send()`, held responses, and short `FUNC_CFG` requests), PCI SR-IOV APIs, rtnl/netdev locking, firmware capability flags, ethtool speed conversion, RoCE/ULP capability macros, and VF representor helpers from `bnxt_vfr.c`. It integrates with ndo VF callbacks, PCI `.sriov_configure`, firmware async events, firmware reset/resource restore paths, and switchdev representor creation.

## Risks
Resource calculations are sensitive to firmware generation, aggregation rings, NQ/MSI-X accounting, pre-reserved VNICs, and reservation strategy. Partial enable failures require ordered unwinding of PCI SR-IOV, firmware resources, and local memory. Forwarded request validation is security-sensitive because untrusted VFs can attempt MAC or link-related operations. The PF mirrors admin state before/after firmware operations in a few places, so failed HWRM commands or reset replay bugs can desynchronize Linux-visible state from firmware.

## Test Signals
Useful signals include enabling and disabling varying VF counts, reducing requested VF count when resources are constrained, changing VF MAC/VLAN/rate/link/spoof/trust through iproute2, observing VF MAC approval from an untrusted and trusted VF, hot reset with SR-IOV enabled, assigned-VF disable behavior, switchdev enable with representor creation, RoCE SR-IOV resource provisioning, and firmware error-injection around each HWRM allocation/free path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_sriov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_sriov.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_sriov.h

## Purpose
Declares the bnxt SR-IOV interface used by the rest of the driver and defines small constants/macros needed to safely forward or reject encapsulated VF HWRM commands.

## Important APIs, Types, And Functions
The header exports VF ndo helpers (`bnxt_get_vf_config()`, `bnxt_set_vf_mac()`, `bnxt_set_vf_vlan()`, `bnxt_set_vf_bw()`, `bnxt_set_vf_link_state()`, `bnxt_set_vf_spoofchk()`, `bnxt_set_vf_trust()`), lifecycle functions (`bnxt_sriov_configure()`, `bnxt_cfg_hw_sriov()`, `__bnxt_sriov_disable()`), mailbox helpers (`bnxt_hwrm_exec_fwd_req()`), and VF-side MAC helpers (`bnxt_update_vf_mac()`, `bnxt_approve_mac()`). `BNXT_FWD_RESP_SIZE_ERR()`, `BNXT_EXEC_FWD_RESP_SIZE_ERR()`, and `BNXT_REJ_FWD_RESP_SIZE_ERR()` guard encapsulated message copies against HWRM request layout limits. VF resource constants define minimum/maximum RSS and L2 contexts.

## Control Flow
This file has no runtime control flow, but it shapes build-time linkage. Non-SR-IOV fallbacks are implemented in `bnxt_sriov.c`, while callers include this header unconditionally and rely on the C file to provide either real or stubbed implementations.

## State And Persistence Behavior
The header itself stores no state. Its prototypes operate on `struct bnxt`, `struct bnxt_vf_info`, `struct net_device`, and `struct pci_dev` objects owned by the broader driver. The size-check macros influence transient mailbox-copy behavior and prevent overrunning fixed HWRM input structures.

## Dependencies And Integration Points
It depends on HWRM structure definitions for `offsetof()` and field layout, VLAN/link/VF netdev structures, and bnxt private types. It is the API seam between core bnxt files, SR-IOV lifecycle code, representor code, and VF MAC approval paths.

## Risks
The safety macros rely on exact HWRM structure layouts and must be updated if firmware ABI structs change. Header declarations must stay synchronized with SR-IOV-disabled stubs or non-SR-IOV builds will fail.

## Test Signals
Signals are mostly compile-time: build with and without `CONFIG_BNXT_SRIOV`, plus static analysis for mailbox copy bounds. Runtime coverage comes from the `.c` file's VF lifecycle and forwarded-command tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_sriov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_tc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_tc.c

## Purpose
Implements flower classifier hardware offload for bnxt. It parses TC flower matches/actions into bnxt flow objects, validates hardware-supported patterns, allocates/free firmware CFA flows, shares L2 and tunnel handles across compatible flows, supports VXLAN indirect offload, and periodically collects hardware flow statistics.

## Important APIs, Types, And Functions
The public driver hooks are `bnxt_tc_setup_flower()`, `bnxt_init_tc()`, `bnxt_shutdown_tc()`, and `bnxt_tc_flow_stats_work()`. Parsing is split across `bnxt_tc_parse_flow()`, `bnxt_tc_parse_actions()`, and action helpers for redirect, VLAN, tunnel encap/decap, pedit L2 rewrite, and NAT/NAPT. Firmware allocation is handled by `bnxt_hwrm_cfa_flow_alloc()` and `bnxt_hwrm_cfa_flow_free()`, with tunnel-specific helpers for decap filters and encap records. Sharing is managed through rhashtables for flows, L2 keys, decap L2 keys, decap tunnels, and encap tunnels.

## Control Flow
`bnxt_tc_setup_flower()` dispatches replace, destroy, and stats commands. On replace, `bnxt_tc_add_flow()` allocates a `bnxt_tc_flow_node`, parses the flow rule, assigns source FID and direction, validates offloadability, deletes any prior flow with the same cookie, acquires the TC lock, obtains a reference L2 flow handle, resolves or allocates a tunnel handle if required, allocates the firmware CFA flow, initializes stats state, and inserts the node into the flow table. Error unwinding releases handles in reverse order.

On destroy, `bnxt_tc_del_flow()` looks up the cookie and `__bnxt_tc_del_flow()` frees the firmware flow, releases tunnel and L2 references under the TC lock, removes the node from the flow table, and frees it with RCU. On stats, `bnxt_tc_get_flow_stats()` returns deltas accumulated by the periodic worker. The worker walks the flow rhashtable in batches, sends `HWRM_CFA_FLOW_STATS`, handles hardware counter wraparound, and updates `lastused`.

Indirect VXLAN offload registers `bnxt_tc_setup_indr_cb()` in `bnxt_init_tc()`. Binding allocates a callback-private object per tunnel netdev and routes flower callbacks back into `bnxt_tc_setup_flower()` using the PF FID.

## State And Persistence Behavior
`bp->tc_info` owns all TC offload state for the lifetime of feature enablement. Persistent in-memory objects include the flow rhashtable keyed by TC cookie, shared L2 nodes keyed by the first 16 bytes of `bnxt_tc_l2_key`, shared decap/encap tunnel nodes keyed by `struct ip_tunnel_key`, per-flow firmware handles, accumulated stats, and an indirect-block callback list. Firmware state persists until explicit free commands or driver shutdown. There is no disk persistence.

## Dependencies And Integration Points
The file integrates with Linux TC flower, `flow_rule` dissectors, `flow_action`, rhashtable, RCU freeing, neighbor/route lookup for VXLAN tunnel header resolution, VXLAN indirect devices, and bnxt HWRM CFA commands. It depends on VF representor helpers to identify representor devices and convert them to VF FIDs, and on `netdev_port_same_parent_id()` to keep redirects inside the same switch.

## Risks
Offload correctness depends on strict match/action validation. Partial MAC/VLAN wildcards, non-TCP/UDP port matches, missing ethertype masks, IPv6 tunnel keys, and unsupported pedit combinations must be rejected. Shared L2/tunnel reference management is subtle; failure paths must not leak firmware handles or leave list entries attached. Route/neighbor resolution for encap can become stale after neighbor, VLAN, or route changes. Counter wrap handling assumes firmware-programmed widths of 36 bytes bits and 28 packet bits. Concurrency spans TC callbacks, stats walks, RCU frees, and driver shutdown.

## Test Signals
Key tests are flower add/delete/replace by cookie, unsupported-pattern rejection, PF-to-VF and VF-rep-to-PF redirects, drop, VLAN push/pop, L2 rewrite, IPv4/IPv6 NAT/NAPT, VXLAN encap/decap with indirect block bind/unbind, shared L2/tunnel reference reuse, stats deltas and wraparound, firmware allocation failure unwinding, shutdown with active flows, and switchdev flows sourced from VF representors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_tc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_tc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_tc.h

## Purpose
Defines the in-memory model for bnxt TC flower offload and exposes feature entry points with real implementations under `CONFIG_BNXT_FLOWER_OFFLOAD` and stubs otherwise.

## Important APIs, Types, And Functions
`struct bnxt_tc_l2_key`, `bnxt_tc_l3_key`, and `bnxt_tc_l4_key` represent parsed match keys and masks. `struct bnxt_tc_actions` stores parsed forwarding, drop, VLAN, tunnel, L2 rewrite, and NAT actions. `struct bnxt_tc_flow` combines source FID, keys/masks, tunnel keys, actions, accumulated stats, prior stats, last-used time, and a stats spinlock. `struct bnxt_tc_tunnel_node`, `bnxt_tc_l2_node`, and `bnxt_tc_flow_node` are the rhashtable/list nodes used for sharing firmware handles and tracking TC cookies. Exported functions are `bnxt_tc_setup_flower()`, `bnxt_init_tc()`, `bnxt_shutdown_tc()`, `bnxt_tc_flow_stats_work()`, and `bnxt_tc_flower_enabled()`.

## Control Flow
The header is declarative. Compile-time control flow selects real prototypes and structures only when flower offload is enabled. Without the config, static inline stubs report unsupported setup and no-op init/shutdown/stats behavior, allowing other bnxt code to call TC helpers without preprocessor clutter.

## State And Persistence Behavior
The structures defined here are the persistent in-memory state for offloaded flows. Firmware handles are stored in flow and tunnel nodes; flow stats are maintained as cumulative software counters plus previous snapshots for TC delta reporting. RCU heads on nodes define deferred free semantics.

## Dependencies And Integration Points
The header depends on netdev, rhashtable, list, RCU, spinlock, `struct ip_tunnel_key`, and TC flower offload types. It is consumed by `bnxt_tc.c` and by representor code that forwards VF-rep TC rules into the PF offload engine.

## Risks
Hash key lengths are important: `BNXT_TC_L2_KEY_LEN` hashes only the first 16 bytes of the L2 key, so structure layout changes can affect sharing semantics. Action and flow flag bits must remain synchronized with parser and HWRM allocation code. Stub behavior must match callers' expectations in non-offload builds.

## Test Signals
Build with `CONFIG_BNXT_FLOWER_OFFLOAD=y` and disabled. Runtime signals come from add/delete/stats paths in `bnxt_tc.c`; structural risk is best covered by compile tests and flow cases that share L2/tunnel keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_tc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_ulp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_ulp.c

## Purpose
Manages bnxt upper-layer protocol auxiliary devices, primarily RDMA/RoCE and fwctl. It allocates auxiliary-device identities, publishes `bnxt_en_dev` objects, handles ULP registration and firmware messaging, reserves MSI-X/stat resources, routes async events, and coordinates ULP stop/start around netdev and firmware-reset transitions.

## Important APIs, Types, And Functions
Exports include `bnxt_register_dev()`, `bnxt_unregister_dev()`, `bnxt_send_msg()`, `bnxt_register_async_events()`, resource getters/setters for ULP MSI-X and stat contexts, stop/start/IRQ helpers, and auxiliary lifecycle functions `bnxt_aux_devices_init()`, `bnxt_aux_devices_add()`, `bnxt_aux_devices_del()`, `bnxt_aux_devices_uninit()`, `bnxt_auxdev_id_alloc()`, and `bnxt_auxdev_id_free()`. Internal `struct bnxt_aux_device` names supported aux devices, while `bp->edev[]`, `bp->aux_priv[]`, and `bp->auxdev_state[]` track active objects.

## Control Flow
Initialization allocates a global IDA id, creates initialized-but-not-added auxiliary devices for supported slots, allocates `bnxt_en_dev` and `bnxt_ulp`, copies bnxt device capabilities into the exported object, and records an INIT state. Add transitions INIT devices to ADD through `auxiliary_device_add()`. Delete removes active auxiliary devices and returns them to INIT. Uninit releases initialized devices; final memory cleanup occurs in the auxiliary device release callback.

ULP drivers call `bnxt_register_dev()` with operation callbacks and a handle. The driver validates IRQ/resource availability, installs ops under RCU, optionally reconfigures the default VNIC for dual VNIC mode if the netdev is open, records requested MSI-X count, and fills vector metadata. Unregister clears async registration, removes ops with RCU synchronization, and resets event fields. Stop/start loops over active aux devices, sets `BNXT_EN_FLAG_ULP_STOPPED`, and calls auxiliary driver suspend/resume where appropriate.

## State And Persistence Behavior
State is in memory: auxiliary device state slots, exported device descriptors, ULP callback pointers, requested MSI-X count, stat context reservations, async event bitmaps, max event id, stopped flags, and cached bnxt state. `bnxt_register_async_events()` uses a write memory barrier before publishing the max event id; `bnxt_ulp_async_events()` uses a read barrier before testing the bitmap. Firmware registration through `bnxt_hwrm_func_drv_rgtr()` persists async event subscriptions in device firmware until cleared.

## Dependencies And Integration Points
This file integrates with the Linux auxiliary bus, IDA allocation, netdev instance locking, RCU callback publication, HWRM command transport, firmware async event registration, bnxt VNIC configuration, IRQ/MSI-X table layout, RoCE capability flags, and auxiliary drivers that implement suspend/resume and ULP ops.

## Risks
The lifecycle crosses several ownership systems: auxiliary bus release semantics, bnxt private arrays, RCU ops pointers, and netdev locks. Misordered cleanup can leak aux devices or leave stale `bp->edev[]` pointers. MSI-X vectors must match current IRQ tables after reset. Async bitmap publication uses memory ordering that must remain paired. `bnxt_send_msg()` copies firmware responses into caller buffers and depends on response length clamping.

## Test Signals
Useful coverage includes loading/unloading RDMA and fwctl auxiliary drivers, registering/unregistering while the netdev is open and closed, firmware reset with ULP stop/start and IRQ restart, async event delivery only for subscribed event ids, MSI-X reservation pressure, auxiliary add failure unwind, and builds without RoCE capability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_ulp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_vfr.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_vfr.c

## Purpose
Implements VF representor netdevices for bnxt switchdev SR-IOV mode and devlink eswitch mode transitions. It allocates firmware VF-representor CFA handles, creates one Linux netdev per VF, maps RX CFA codes back to representors, transmits representor packets through the PF lower device using metadata dst, and forwards representor TC flower setup into the PF TC offload engine.

## Important APIs, Types, And Functions
External functions include `bnxt_vf_reps_create()`, `bnxt_vf_reps_destroy()`, `bnxt_vf_reps_open()`, `bnxt_vf_reps_close()`, `bnxt_vf_reps_alloc()`, `bnxt_vf_reps_free()`, `bnxt_get_vf_rep()`, `bnxt_vf_rep_rx()`, `bnxt_dev_is_vf_rep()`, `bnxt_dl_eswitch_mode_get()`, and `bnxt_dl_eswitch_mode_set()`. Firmware helpers `hwrm_cfa_vfr_alloc()` and `hwrm_cfa_vfr_free()` allocate/free per-VF representor handles. `bnxt_vf_rep_netdev_ops` defines open, close, xmit, stats, TC setup, parent id, and physical port naming behavior.

## Control Flow
Switchdev creation starts in `bnxt_vf_reps_create()`. It verifies DSN validity, allocates `bp->vf_reps`, allocates a `MAX_CFA_CODE` map initialized to invalid VF indexes, then allocates an etherdev per VF. Each representor gets firmware CFA handles, a metadata destination that muxes TX packets through the PF, inherited PF features, deterministic generated MAC address, max MTU queried from the VF function, and registration with the networking stack. Only after all representors are initialized is `bp->cfa_code_map` published for RX-path lookup.

Representor TX drops any existing dst, attaches the metadata dst containing `tx_cfa_action` and PF lower dev, and calls `dev_queue_xmit()`. RX lookup uses `bnxt_get_vf_rep()` to map hardware CFA code to a representor dev and `bnxt_vf_rep_rx()` updates stats before injecting the skb with `netif_receive_skb()`. Destroy first closes the PF if needed to quiesce RX/TX, unpublishes `cfa_code_map`, reopens the PF with temporary legacy eswitch mode if it was closed, then unregisters/free netdevs outside the netdev lock.

## State And Persistence Behavior
Representor state is in `bp->vf_reps[]`, each `struct bnxt_vf_rep`, `bp->cfa_code_map`, metadata dst objects, firmware CFA VFR allocations, and per-representor software RX/TX counters. `bnxt_vf_reps_free()` releases firmware handles while keeping netdevs registered during firmware hot reset; `bnxt_vf_reps_alloc()` reacquires handles and repopulates the CFA-code map. No state is persisted to disk.

## Dependencies And Integration Points
The file integrates with SR-IOV state from `bp->pf.vf[]`, devlink eswitch mode, metadata hardware port mux dsts, netdev registration and stats APIs, ethtool drvinfo, TC block callbacks, bnxt TC flower offload, and bnxt devlink helpers. It relies on switchdev mode being serialized with netdev instance locking as noted in comments.

## Risks
Publishing and unpublishing `bp->cfa_code_map` must be synchronized with RX activity; destroy deliberately quiesces the PF first. Error unwind spans firmware VFR handles, metadata dst references, netdev registration, and allocated maps. `sprintf(req->vfr_name, "vfr%d", vf_idx)` depends on firmware field sizing. Representor feature inheritance from PF can expose feature combinations that rely on PF rings. TC setup depends on correct VF FID lookup from `bp->pf.vf[vf_idx]`.

## Test Signals
Test switchdev/legacy devlink transitions with zero and nonzero VFs, representor registration naming and phys port names, PF close/open with representors, representor TX/RX stats, CFA-code RX mapping, firmware hot reset free/alloc, TC flower rules on representors, partial create failure unwind, and eswitch switchdev rejection on unsupported firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_vfr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_vfr.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_vfr.h

## Purpose
Declares the VF representor API used by SR-IOV, TC offload, RX demux, and devlink eswitch code. It also provides no-op stubs when SR-IOV support is disabled.

## Important APIs, Types, And Functions
The header defines `MAX_CFA_CODE` and declares representor lifecycle (`bnxt_vf_reps_create()`, `bnxt_vf_reps_destroy()`, `bnxt_vf_reps_open()`, `bnxt_vf_reps_close()`, `bnxt_vf_reps_alloc()`, `bnxt_vf_reps_free()`), RX/TX integration (`bnxt_vf_rep_rx()`, `bnxt_get_vf_rep()`), device identification (`bnxt_dev_is_vf_rep()`), VF FID lookup (`bnxt_vf_rep_get_fid()`), and devlink eswitch mode functions. The inline FID helper maps a representor netdev back to `bp->pf.vf[vf_idx].fw_fid`.

## Control Flow
There is no runtime control flow in the header. Compile-time control flow selects real declarations under `CONFIG_BNXT_SRIOV`; otherwise, inline stubs make representor creation/destruction harmless and representor lookups return false or `NULL`.

## State And Persistence Behavior
The header stores no state. Its API operates on `bp->vf_reps`, `bp->cfa_code_map`, `bp->pf.vf[]`, and representor private data allocated by `bnxt_vfr.c`.

## Dependencies And Integration Points
It bridges `bnxt_sriov.c`, `bnxt_tc.c`, RX completion code, and devlink code. Consumers can identify VF representors without depending on the implementation file's netdev ops symbol.

## Risks
The inline FID helper assumes the netdev is a valid bnxt VF representor and that `vf_idx` indexes an initialized VF entry. Callers must use it only after representor validation. Stub behavior in non-SR-IOV builds must preserve caller expectations.

## Test Signals
Compile with and without `CONFIG_BNXT_SRIOV`. Runtime signals are switchdev representor create/destroy and TC redirect tests that call `bnxt_vf_rep_get_fid()` through `bnxt_flow_get_dst_fid()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_vfr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_xdp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_xdp.c

## Purpose
Implements XDP support for bnxt RX and TX rings. It attaches/detaches XDP programs, runs programs on received packets, supports `XDP_PASS`, `XDP_DROP`, `XDP_ABORTED`, `XDP_TX`, and `XDP_REDIRECT`, builds XDP TX descriptors including fragments, handles XDP TX completions and page recycling, exposes ndo XDP xmit, builds skb fragment metadata after XDP pass, and implements XDP RX hash kfunc support.

## Important APIs, Types, And Functions
The public functions are `bnxt_xdp()`, `bnxt_rx_xdp()`, `bnxt_xdp_xmit()`, `bnxt_tx_int_xdp()`, `bnxt_xmit_bd()`, `bnxt_xdp_attached()`, `bnxt_xdp_buff_init()`, `bnxt_xdp_buff_frags_free()`, `bnxt_xdp_build_skb()`, and `bnxt_xdp_rx_hash()`. `bnxt_xdp_locking_key` is a static branch used to enable XDP TX locking when needed. `bnxt_xmit_bd()` is the shared descriptor builder for XDP_TX and XDP_REDIRECT paths.

## Control Flow
Program setup enters through `bnxt_xdp()` and `bnxt_xdp_set()`. Setup validates MTU versus fragment support, disallows XDP with HDS, requires combined RX/TX channels, checks ring resources, closes the NIC if running, swaps `bp->xdp_prog`, updates skb/page mode and redirect target features, recomputes XDP TX ring counts and ring parameters, and reopens the NIC if needed.

RX processing calls `bnxt_xdp_buff_init()` to sync DMA and prepare an `xdp_buff`, then `bnxt_rx_xdp()` runs the BPF program. PASS returns false so the normal stack path continues. TX checks descriptor availability, syncs DMA for device, queues a TX BD referencing the RX page, marks events for TX completion, and reuses the RX buffer. REDIRECT allocates a replacement RX buffer before `xdp_do_redirect()` and marks redirect events. DROP/ABORTED recycle fragments and reuse RX data. ndo `bnxt_xdp_xmit()` maps external XDP frames, queues redirect descriptors on a CPU-selected XDP TX ring, and optionally flushes the doorbell.

TX completions in `bnxt_tx_int_xdp()` distinguish redirected frames from XDP_TX recycled RX pages. Redirect completions unmap DMA and return the frame; XDP_TX completions recycle fragment pages and ring the RX doorbell when needed.

## State And Persistence Behavior
XDP state is in `bp->xdp_prog`, per-RX-ring `rxr->xdp_prog`, `bp->tx_nr_rings_xdp`, adjusted total TX/CP ring counts, page-pool state, TX software descriptors with `action`, `rx_prod`, `xdpf`, page and DMA metadata, and netdev XDP redirect-target feature flags. No persistent disk state exists. Program references are owned through BPF refcounts and the old program is released after `xchg()`.

## Dependencies And Integration Points
The file integrates with Linux XDP/BPF APIs, page pool recycling, PCI DMA mapping/syncing, bnxt ring macros and doorbells, netdev instance locking, NIC open/close flows, RSS completion formats, and tracepoints for XDP exceptions. It depends on ring sizing helpers from core bnxt code and assumes XDP runs in page mode.

## Risks
DMA ownership and page recycling are the highest-risk areas: XDP_TX reuses RX pages, REDIRECT needs replacement allocation before handoff, and fragmented XDP requires recycling all frags on drop/error. Ring-full behavior must avoid advancing RX producer too early. Program attach must preserve NIC state across close/reopen and reject unsupported MTU/HDS/channel layouts. `bnxt_xdp_xmit()` can run concurrently and only locks when the static key says it is needed.

## Test Signals
Run XDP programs for PASS, DROP, ABORTED, TX, and REDIRECT; include multi-buffer/frags, jumbo MTU with and without frag-capable programs, ring exhaustion, redirect to another device, external ndo xmit, attach/detach while the NIC is up, attach rejection with HDS or split channels, TX completion recycling, DMA mapping failures, and `bpf_xdp_metadata_rx_hash` behavior for L2, IPv4/IPv6, TCP/UDP/ICMP, and v3 completion formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_xdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_xdp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_xdp.h

## Purpose
Declares bnxt XDP entry points and the small wrapper context used for XDP RX hash metadata extraction.

## Important APIs, Types, And Functions
`struct bnxt_xdp_buff` embeds `struct xdp_buff` and carries RX completion pointers plus completion type so `bnxt_xdp_rx_hash()` can derive RSS hash metadata. The header declares XDP TX descriptor construction, TX completion, RX execution, program setup, ndo xmit, attach checks, buffer initialization, fragment cleanup, skb fragment finalization, and RX hash metadata functions. It also declares `bnxt_xdp_locking_key`.

## Control Flow
The header has no runtime control flow. It provides declarations consumed by core RX/TX and netdev setup code so XDP-specific behavior can be called from the main datapath.

## State And Persistence Behavior
The header defines transient per-packet context (`bnxt_xdp_buff`) and references external static-branch state. Persistent XDP program and ring state are owned by `struct bnxt` and ring structures in the implementation.

## Dependencies And Integration Points
It integrates XDP support with bnxt RX completion code, TX ring cleanup, netdev BPF setup, page-pool-backed RX buffers, and BPF metadata helpers. It depends on bnxt ring types and Linux XDP types.

## Risks
`struct bnxt_xdp_buff` must remain layout-compatible with casting from `const struct xdp_md *` in `bnxt_xdp_rx_hash()`, with the embedded `xdp_buff` first. Prototype changes must stay synchronized with call sites in the RX/TX datapath.

## Test Signals
Compile coverage plus runtime XDP attach, RX action, TX completion, and metadata hash tests from `bnxt_xdp.c` cover this header's contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_xdp.h -->
