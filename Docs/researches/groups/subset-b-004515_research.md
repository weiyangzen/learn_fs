# subset-b-004515 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_nix.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_nix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_npa.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_npa.c

## Purpose

`rvu_npa.c` implements the RVU Admin Function side of the NPA block, the OcteonTX2/CN10K packet buffer allocator used by NIX and other RVU engines. It handles NPA admin queue initialization/submission, NPALF allocation/free, aura and pool hardware context memory, queue interrupt context memory, context enabled bitmaps, optional NDC context lockdown, and a hardware erratum recovery helper for locked NDC cachelines.

The file has no filesystem persistence. It persists operational state in hardware registers, NPA AQ context memory, NDC cache state, and software mirrors hanging off `struct rvu_pfvf`.

## Important APIs, Types, And Functions

- `npa_aq_init` initializes NPA AQ endianness, NDC caching policy, CN10K batch DMA cache-line count, allocates the AQ instruction/result rings through `rvu_aq_alloc`, and writes `NPA_AF_AQ_CFG`/`NPA_AF_AQ_BASE`.
- `npa_aq_enqueue_wait` writes one `struct npa_aq_inst_s` to the current AQ head, clears shared result memory, rings the AQ doorbell, polls completion, and invokes `rvu_ndc_fix_locked_cacheline` on context fault/lock/poison completion codes.
- `rvu_npa_aq_enq_inst` is the main AQ operation implementation for aura and pool contexts. It validates LF and context bounds, serializes on `aq->lock`, handles WRITE/INIT/READ/LOCK/UNLOCK/NOP, translates aura pool indexes to pool context IOVA on INIT, updates aura/pool enabled bitmaps, and copies READ results into the mailbox response.
- `rvu_mbox_handler_npa_aq_enq` exposes AQ operations to mailbox callers and optionally locks newly initialized contexts when `CONFIG_NDC_DIS_DYNAMIC_CACHING` is enabled.
- `npa_lf_hwctx_disable` and `rvu_mbox_handler_npa_hwctx_disable` walk enabled aura or pool bitmaps and clear enable bits through AQ WRITE operations.
- `npa_ctx_free` releases per-PF/VF aura, pool, aura bitmap, pool bitmap, and NPA qint qmem state.
- `rvu_mbox_handler_npa_lf_alloc` resets the NPALF, allocates aura/pool/qint qmem, configures LF context bases/caching/way masks, and returns stack-page and qint/cache-line hardware information.
- `rvu_mbox_handler_npa_lf_free` resets the NPALF and frees per-LF context memory.
- `rvu_npa_init` and `rvu_npa_freemem` initialize/free the global NPA AQ for the first NPA block.
- `rvu_npa_lf_teardown` disables all active pools and auras then frees the PF/VF context memory for FLR or higher-level teardown.
- `rvu_ndc_fix_locked_cacheline` clears an NDC erratum condition where metadata lines can become locked while invalid.

Important context types are `struct npa_aq_inst_s`, `struct npa_aq_res_s`, `struct npa_aq_enq_req/rsp`, `struct npa_aura_s`, `struct npa_pool_s`, `struct npa_lf_alloc_req/rsp`, and the per-function `struct rvu_pfvf` fields `aura_ctx`, `pool_ctx`, `npa_qints_ctx`, `aura_bmap`, `pool_bmap`, and `npalf`.

## Control Flow

Global init is minimal: `rvu_npa_init` locates the NPA block for PF_FUNC 0 and calls `npa_aq_init`; if no NPA block exists it returns success. AQ init programs endianness, configures NPA NDC bypass bits, adjusts CN10K batch control when applicable, allocates AQ memory with enough result space for a response plus context and mask payloads, and writes AQ base/config registers.

NPALF allocation enters through `rvu_mbox_handler_npa_lf_alloc`. It validates aura size and pool count, masks cache way partition bits, validates that the PF/VF has an attached NPALF, resets the LF, reads hardware context-size fields from `NPA_AF_CONST1`, allocates qmem for aura contexts, pool contexts, and qint contexts, allocates bitmaps used to remember enabled aura/pool contexts, programs LF aura size/caching/way mask and qint caching/base registers, and returns stack page pointer/byte fields plus qint/cache-line capabilities.

AQ operations enter through `rvu_npa_aq_enq_inst`. The function validates the requested aura id against the aura context qsize, verifies LF attachment, finds the hardware NPALF, prepares an AQ instruction, then uses the shared AQ result memory under `aq->lock`. WRITE copies the requested aura/pool context and write mask; INIT copies a new aura/pool context and rewrites aura `pool_addr` from a pool index to the DMA address of that pool context; READ/LOCK/UNLOCK/NOP require no context payload. After `npa_aq_enqueue_wait` succeeds, the function updates aura or pool enabled bitmaps based on INIT or masked WRITE enable changes and copies readback context into the response.

Free and teardown paths reset or disable before releasing memory. Explicit LF free validates the LF, resets it with `rvu_lf_reset`, and calls `npa_ctx_free`. Teardown first clears all enabled pool contexts, then all enabled aura contexts, using the bitmaps as a sparse active set, and finally frees context memory. The disable path keeps going after per-context AQ failures, logging each failed context and returning the last error.

The NDC erratum helper disables CAM read interval enable, polls busy bits to idle, then walks all NDC banks/lines and clears lock bit 60 when valid bit 63 is clear. It is skipped on CN20K where NDC is not applicable.

## State And Persistence Behavior

Per-function NPA state lives in `struct rvu_pfvf`: `npalf` attachment, qmem pointers for aura/pool/qint contexts, and enabled bitmaps for auras and pools. The bitmaps are not hardware truth; they are software mirrors maintained only by successful INIT/WRITE AQ operations and used for efficient disable during teardown.

Hardware-visible state includes LF context base registers, aura size/caching/way-mask configuration, qint base/config registers, AQ instruction/result memory, NPA aura and pool contexts, batch control, NDC caching mode, and NDC metadata lock bits. `qmem_alloc` provides DMA-addressable context memory and `qmem_free` releases it.

`npa_ctx_free` nulls all freed pointers after releasing them, which makes repeated cleanup paths safer. `rvu_npa_freemem` only frees the block-level AQ memory; per-LF context memory is owned by PF/VF lifecycle paths.

## Dependencies And Integration Points

The file depends on RVU core services from `rvu.h`: block lookup, LF lookup, PF/VF lookup, register access, polling, LF reset, AQ allocation/free, and qmem allocation/free. It uses NPA hardware definitions from `rvu_struct.h` and `rvu_reg.h`, and Linux primitives for spinlocks, memory barriers, delay/poll loops, and allocation.

Mailbox handlers are the main caller-facing API: PF/VF drivers allocate NPALFs, configure aura/pool contexts, disable contexts, and free NPALFs through mailbox requests. NIX LF allocation validates NPA PF_FUNC mappings in `rvu_nix.c`, so NPA state is a dependency of NIX packet I/O. NDC recovery is shared with NIX: `rvu_ndc_fix_locked_cacheline` is defined here but called from both NPA and NIX AQ error paths.

Hardware-family integration matters: CN20K skips NDC cleanup; CN10K and newer NPA batch control reports cache-line count; `CONFIG_NDC_DIS_DYNAMIC_CACHING` changes both NDC configuration and post-INIT context locking behavior.

## Risks And Edge Cases

- `rvu_npa_aq_enq_inst` validates `req->aura_id` against aura qsize before branching on context type. Pool operations therefore also depend on the aura id range unless pool-specific qsize checks later catch INIT pool address use. This is likely intentional because the field is reused as context index, but it is a boundary worth testing when pool count and aura count differ.
- Pool bitmap allocation uses `NPA_AURA_COUNT(req->aura_sz)` entries rather than `req->nr_pools`. If pool count can exceed aura count, pool bitmap updates/teardown may miss or overrun logical ownership; if hardware/API guarantees otherwise, that contract should be documented by tests.
- AQ result memory is shared per block and protected by a spinlock. Any future path that sleeps while holding `aq->lock` or bypasses the lock would corrupt AQ result handling.
- AQ timeout returns `-EBUSY` after roughly 1000 micro-delay iterations; callers generally convert this to broad mailbox errors, so diagnosis depends on logs and hardware compcodes.
- INIT of aura contexts rewrites `req->aura.pool_addr` in place from a pool index to a DMA address. Reusing the same request object after a failed or repeated call could surprise callers.
- Context disable depends on software bitmaps. If bitmaps drift from hardware state, teardown will leave enabled hardware contexts behind.
- `rvu_ndc_fix_locked_cacheline` scans every bank/line after stopping CAM reads. Incorrect bank/line field interpretation or failure to re-enable a disabled interval elsewhere could affect NDC behavior beyond the failed AQ.
- Several cleanup paths ignore absent NPA blocks or already-null state. That is useful for teardown idempotence but can hide missing init in tests unless assertions inspect returned capabilities/state.

## Test Signals

- Init/free tests should validate AQ allocation, AQ register programming, endianness bit behavior, CN10K batch cache-line programming/reporting, CN20K NDC skip, and no-NPA-block early success.
- LF allocation tests should cover invalid aura size, zero pools, way-mask truncation, missing NPALF attachment, LF reset failure, qmem allocation failure at each allocation stage, aura/pool/qint base register programming, returned stack page fields, qints, and CN10K cache-line count.
- AQ tests should cover aura and pool INIT/WRITE/READ/LOCK/UNLOCK/NOP, invalid op, invalid aura id, invalid aura pool index, masked enable transitions, bitmap set/clear behavior, readback copying, AQ timeout, non-good compcodes, and NDC erratum recovery.
- Teardown tests should create sparse enabled aura/pool bitmaps, verify only enabled contexts get disable writes, confirm errors are logged and propagated while remaining contexts are attempted, and ensure qmem pointers/bitmaps are nulled after free.
- Integration tests should allocate NPA before NIX, verify NIX rejects invalid NPA PF_FUNC mappings, run NPA teardown under FLR while NIX queues are disabled, and validate no stale aura/pool contexts remain in hardware after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_npa.c -->
