# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_nix.c

## Purpose

`rvu_nix.c` is the RVU Admin Function implementation for Marvell OcteonTX2/CN10K/CN20K NIX blocks, which are the packet I/O engines behind PF/VF Ethernet interfaces. It owns NIX block bring-up, LF allocation/free, admin-queue context programming, RX/TX scheduler resources, multicast replication, VLAN tag definition resources, RSS flow-key algorithms, link frame-size/credit configuration, PTP TX enablement, inline IPsec NIX-side plumbing, ingress policer bandwidth-profile resources, and FLR/teardown cleanup.

The file is not a persistence layer; its durable state is hardware state in NIX/NDC/NPC/CGX/CPT registers and DMA-backed context memory. Software mirrors of ownership and enabled resources live in `struct rvu_pfvf` and `struct nix_hw` so mailbox handlers can validate future operations and teardown only resources owned by the requester.

## Important APIs, Types, And Functions

- NIX discovery helpers: `rvu_get_next_nix_blkaddr`, `is_nixlf_attached`, `rvu_get_nixlf_count`, `nix_get_nixlf`, `nix_get_struct_ptrs`, and `get_nix_hw` translate PF/VF `pcifunc` values into NIX block/LF and per-block `struct nix_hw` state.
- Admin queue path: `nix_aq_init`, `nix_aq_enqueue_wait`, `rvu_nix_blk_aq_enq_inst`, `rvu_nix_aq_enq_inst`, `rvu_mbox_handler_nix_aq_enq`, and `rvu_mbox_handler_nix_cn10k_aq_enq` serialize NIX AQ operations for RQ, SQ, CQ, RSS, MCE, and CN10K bandwidth profile contexts. `nix_aq_context_read` is a reusable read helper.
- LF lifecycle: `rvu_mbox_handler_nix_lf_alloc`, `rvu_mbox_handler_nix_lf_free`, `rvu_nix_lf_teardown`, `nix_ctx_free`, `nix_lf_hwctx_disable`, and optional `nix_lf_hwctx_lockdown` allocate/free qmem contexts, reset LFs, disable active contexts, and release associated NIX resources.
- Interface/link setup: `nix_interface_init`, `nix_interface_deinit`, `nix_link_config`, `rvu_mbox_handler_nix_set_hw_frs`, `rvu_mbox_handler_nix_set_rx_cfg`, `rvu_mbox_handler_nix_lf_start_rx`, and `rvu_mbox_handler_nix_lf_stop_rx` connect an LF to CGX, LBK, SDP, or representor paths and coordinate NPC rules and CGX I/O.
- TX scheduler handling: `nix_setup_txschq`, `rvu_mbox_handler_nix_txsch_alloc`, `rvu_mbox_handler_nix_txsch_free`, `rvu_mbox_handler_nix_txschq_cfg`, `nix_smq_flush`, `nix_txschq_free`, `nix_txschq_free_one`, `is_valid_txschq`, and related reset helpers manage SMQ/TL4/TL3/TL2/TL1 resources and register writes.
- Backpressure and BPIDs: `nix_setup_bpids`, `rvu_nix_get_bpid`, `nix_bp_enable`, `nix_bp_disable`, `rvu_mbox_handler_nix_bp_enable`, `rvu_mbox_handler_nix_bp_disable`, CPT variants, and `rvu_nix_flr_free_bpids` map channels to BPIDs and handle LBK/SDP/free-pool ownership.
- VLAN and LSO: `nix_setup_txvlan`, `rvu_mbox_handler_nix_vtag_cfg`, `nix_tx_vtag_alloc/free`, `nix_rx_vtag_cfg`, `nix_setup_lso`, and `rvu_mbox_handler_nix_lso_format_cfg` reserve transmit vtag definitions, program RX tag extraction/strip behavior, and allocate static or custom segmentation formats.
- Multicast/mirror: `nix_setup_mcast`, `nix_setup_mce_tables`, `nix_update_mce_rule`, `nix_update_mce_list`, multicast group create/destroy/update handlers, `rvu_nix_mcast_flr_free_entries`, and `rvu_nix_mcast_update_mcam_entry` coordinate MCE qmem entries with NPC MCAM actions.
- RSS flow keys: `set_flowkey_fields`, `reserve_flowkey_alg_idx`, `nix_rx_flowkey_alg_cfg`, and `rvu_mbox_handler_nix_rss_flowkey_cfg` translate requested flow-key bitmasks into NIX flow-key algorithm fields and attach the selected algorithm to NPC flow rules.
- Initialization/free: `rvu_nix_init`, `rvu_nix_block_init`, `rvu_nix_freemem`, and `rvu_nix_block_freemem` allocate per-block software state, initialize block-level registers/resources, and free AQ/resource bitmaps/qmem.
- CN10K ingress policers: `nix_setup_ipolicers`, `nix_verify_bandprof`, `rvu_mbox_handler_nix_bandprof_alloc/free/get_hwinfo`, `rvu_nix_setup_ratelimit_aggr`, and `nix_clear_ratelimit_aggr` allocate and validate bandwidth profile contexts and aggregate leaf profiles through mid-layer profiles.

Important local structures include `struct mce` for multicast replication list entries, `struct nix_hw` for per-NIX block resources, `struct nix_mcast`, `struct nix_mcast_grp_elem`, `struct nix_txsch`, `struct nix_txvlan`, `struct nix_bp`, and `struct nix_ipolicer`; their definitions live in the companion RVU headers.

## Control Flow

Block initialization starts in `rvu_nix_init`, allocates `hw->nix`, iterates all NIX block addresses, and calls `rvu_nix_block_init`. Per block, the driver applies hardware errata settings, sets channel/link backpressure level, disables SQ sticky modes, calibrates X2P against CGX/LBK, detects DWRR MTU capabilities, initializes the admin queue, configures CN10K/CN20K extras, allocates TX scheduler bitmaps, initializes ingress policers, reserves default mark formats, sets up multicast tables and TX vtag resources, reserves BPID structures, configures static LSO formats, programs NPC layer definitions into NIX protocol checker registers, reserves default RSS flow-key algorithms, allocates link credit state, sets link credits/min-max FRS, and enables channel backpressure.

LF allocation enters through `rvu_mbox_handler_nix_lf_alloc`. It validates queue counts, optional NPA/SSO PF_FUNC mapping, RSS size/group constraints, and resets the LF. It allocates qmem and bitmaps for RQ, SQ, CQ, RSS, CQ interrupt, and queue interrupt contexts, writes their base/config registers, sets VLAN TPIDs and LMTST enable, writes `NIX_AF_LFX_CFG` with NPA/SSO and XQE settings, sets RX and TX parse config, then initializes the interface unless the function is a representor. Interface setup selects CGX/LBK/SDP behavior, assigns RX/TX channel bases/counts, configures pkind/promisc defaults for LBK/SDP, installs unicast and broadcast NPC rules, and records initial frame-size bounds.

Admin queue requests flow through mailbox handlers into `rvu_nix_aq_enq_inst`. The function chooses the NIX block for the requester, validates context type/index and ownership, validates SQ `smq` references through `is_valid_txschq`, serializes on `aq->lock`, writes context/mask data at result-memory offsets, rings `NIX_AF_AQ_DOOR`, polls completion, copies read contexts to the response, and updates RQ/SQ/CQ enabled bitmaps. On CQ writes it performs a read-back workaround for an erratum where CQ AQ modifications can be lost under heavy traffic and retries up to five times.

TX scheduler allocation/free is coordinated under `rvu->rsrc_lock`. Allocation validates availability, link ownership, aggregation-level sharing rules, fixed-mapping constraints, and contiguous requests; it resets schedule/link/shaper state for assigned queues and records `TXSCH_MAP(pcifunc, flags)`. Configuration validates register offset, hierarchy parent ownership, shaping support, and BP permissions before writing registers. Freeing disables link config and XOFF, flushes SMQs, resets schedule/shaper state, frees bitmaps, clears maps, and runs NDC TX sync.

RX start and stop are mailbox-visible state transitions. Start reactivates multicast entries for the PF/VF, enables default NPC entries and custom MCAM flows, marks `NIXLF_INITIALIZED`, updates switch rules/representor state, and starts CGX I/O. Stop disables MCAM entries, deactivates multicast entries, clears `NIXLF_INITIALIZED`, stops CGX I/O, updates switch rules, re-enables TX, and notifies representors where applicable. Full teardown is stronger: it disables/frees MCAM entries, deinitializes interface rules, performs double RX sync, frees TX scheduler resources, disables SQ/RQ/CQ hardware contexts by walking enabled bitmaps, resets parse/PTP/flow-control state, frees qmem, frees all bandwidth profiles, and flushes CPT context if inline IPsec SA base is still programmed.

Multicast group control creates software group objects, allocates contiguous MCE ranges on update, programs ingress MCE contexts through AQ or egress MCE registers, updates NPC MCAM action indexes, temporarily disables MCAM entries while editing, and restores or rolls back on failures. FLR cleanup deletes groups created by the reset function and removes entries for the reset function from other groups.

## State And Persistence Behavior

Primary software state is in `struct rvu_pfvf`: NIX LF attachment flag, RQ/SQ/CQ/RSS/qint/cint qmem pointers, queue enabled bitmaps, MAC/default MAC, rx/tx channel base/count, frame-size bounds, LBK id, flags such as `NIXLF_INITIALIZED`, PTP timestamp state, and VF trust/admin MAC flags. `nix_ctx_free` is the single local qmem/bitmap release helper for LF context state.

Per-block state is in `struct nix_hw`: TX scheduler resource bitmaps and `pfvf_map`, multicast qmem/bitmaps/groups, TX vtag bitmap and entry owner map, BPID allocation maps/refcounts, LSO and mark-format usage, flow-key algorithms, ingress policer profile maps/refcounts, link credits, and block address. These resources are initialized once per implemented NIX block and released by `rvu_nix_freemem`.

Persistent hardware-visible state is stored in NIX AF/LF registers, NPC MCAM entries, CGX/RPM/LBK/SDP link state, NPA/SSO/CPT PF_FUNC relationships, NDC cached contexts, and DMA memory allocated through `qmem_alloc`. The driver uses locks (`aq->lock`, `rvu->rsrc_lock`, multicast locks, vtag lock) to keep software mirrors aligned with hardware programming.

The file contains multiple cleanup paths keyed to FLR or LF free. Some resources are freed from explicit mailbox free paths, while teardown also handles implicit failure/reset cleanup. `rvu_block_bcast_xon` is an erratum-style helper that forces a broadcast XON by rewriting channel configuration on CN10K and older hardware.

## Dependencies And Integration Points

This file depends on RVU core helpers (`rvu_read64`, `rvu_write64`, `rvu_poll_reg`, `rvu_lf_reset`, `rvu_get_blkaddr`, `rvu_get_lf`, `rvu_get_pfvf`, resource bitmap helpers, `qmem_alloc/free`, `rvu_aq_alloc/free`), hardware register/structure headers (`rvu_struct.h`, `rvu_reg.h`, `rvu.h`), and NPC definitions (`npc.h`, `rvu_npc_hash.h`). It integrates heavily with NPC MCAM programming for unicast, broadcast, allmulti, promisc, flow steering, RSS flow-key algorithms, switch rules, and parse modes.

External networking and hardware dependencies include CGX/RPM/LMAC operations (`cgx.h`, `lmac_common.h`) for pkind, MAC I/O start/stop, TX enable, PTP, FIFO length, priority flow control, and pause frames; MCS integration for link credit adjustment; CPT for inline IPsec context flush and queue selection; NPA and SSO mappings through PF_FUNC validation; NDC erratum recovery through `rvu_ndc_fix_locked_cacheline` and NDC sync; and CN10K/CN20K companion code such as `rvu_nix_block_cn10k_init`.

Mailbox handlers form the main integration surface with PF/VF drivers. They validate ownership before exposing low-level hardware register/configuration operations, so tests must exercise the mailbox contract rather than only internal helpers.

## Risks And Edge Cases

- AQ submission uses a single result buffer and busy-poll timeout, so missing completions return `-EBUSY`; callers map some such failures to mailbox error codes but not all errors have fine-grained diagnostics.
- AQ context errors trigger NDC locked-cacheline cleanup across several NIX NDC blocks. This is broad hardware recovery and can hide the original AQ compcode.
- The RQ/SQ/CQ enabled bitmap update logic after AQ WRITE uses mask-derived enable state. The SQ and CQ branches reference `req->rq.ena` while applying SQ/CQ masks, which is a risk signal because teardown depends on these bitmaps to disable active contexts.
- TX scheduler code mixes per-function ownership with shared aggregation levels. Incorrect `nix_tx_aggr_lvl`, fixed mapping, or link derivation can deny legal configurations or allow shared TL state to be overwritten.
- `nix_smq_flush` temporarily manipulates CGX TX, RX backpressure, TL2 XOFF, rates, and link enable bits. Failures here can leave link scheduling disturbed if a restore path is missed.
- Multicast group updates require contiguous MCE allocation and have rollback paths that reallocate previous ranges. Low MCE availability or allocation failure can leave MCAM entries disabled until restoration succeeds.
- Ingress policer aggregation intentionally drops and reacquires `rvu->rsrc_lock` inside `nix_clear_ratelimit_aggr` for AQ reads. This avoids sleeping/long AQ work under the lock but creates an observation window where profile state can change.
- Many flows are hardware-family conditional (`is_rvu_otx2`, `is_cn20k`, CN10K bandwidth profiles, DWRR MTU modes, NDC support). Regression risk is high when changing common paths without testing all supported families.
- Several handlers return success for unsupported or skipped operations, especially for unsupported VF promisc/allmulti or absent CPT/IPsec blocks. Callers must not infer that hardware was changed just because the mailbox completed.

## Test Signals

- NIX init should be validated on each supported silicon family with logs for X2P calibration, AQ allocation, RSS flow-key setup, multicast resource allocation, policer capability detection, and link credit programming.
- LF allocation/free tests should cover CGX PFs, trusted/untrusted VFs, PF0 LBK VFs, SDP PF/VFs, representor functions, RSS disabled/enabled, invalid NPA/SSO PF_FUNCs, invalid RSS size/group values, and memory-allocation failure injection.
- AQ tests should cover RQ/SQ/CQ/RSS READ/INIT/WRITE/LOCK/UNLOCK, invalid queue indexes, invalid SMQ ownership, CQ write retry behavior, bitmap updates, and NDC locked-cacheline recovery paths.
- TX scheduler tests should allocate/free contiguous and non-contiguous queues at every level, verify parent hierarchy validation, shape enable/disable transitions, SMQ flush behavior with busy links, fixed-mapping hardware, and aggregation-level sharing between PF and VF.
- Multicast tests should create/destroy/update ingress and egress groups, handle group-owner deletion, member deletion on FLR, non-contiguous MCE allocation failure, MCAM action update, RX start/stop reactivation, and default broadcast/allmulti/promisc lists.
- VLAN/LSO/RSS tests should cover vtag allocation ownership/free, RX type 7 rejection, duplicate LSO format detection, LSO table exhaustion, default and custom RSS flow-key reuse, unsupported key combinations, and NPC action update.
- Link/MAC/RX-mode tests should verify admin-set VF MAC protection, trusted VF MAC update to default, frame-size aggregation across PF/VFs, min length bounds, promisc/allmulti handling with and without NIX multicast support, PTP TX enable on unsupported MACs, and inline IPsec enable/read/disable.
- Policer tests should cover profile allocation limits, owner validation, high-layer linkage validation, aggregate ratelimit mid-profile allocation/refcount/free, and `nix_bandprof_get_hwinfo` timeunit/count reporting.
