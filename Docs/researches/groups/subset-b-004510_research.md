# subset-b-004510 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/npc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/npc.c

## Purpose
Implements CN20K-specific NPC support for the Marvell RVU Admin Function driver. The file programs parser/KPM and MCAM key-extraction profiles, manages CN20K's split MCAM subbank allocator for X2/X4/DYN key widths, translates virtual MCAM indexes used by defragmentable allocations, services CN20K NPC mailbox handlers, installs and frees default steering rules, and initializes/deinitializes the global CN20K NPC private state.

## Important APIs, Types, and Functions
External entry points include `npc_cn20k_init`, `npc_cn20k_deinit`, `npc_cn20k_parser_profile_init`, `npc_cn20k_load_mkex_profile`, `npc_cn20k_apply_custom_kpu`, `npc_cn20k_ref_idx_alloc`, `npc_cn20k_idx_free`, `npc_cn20k_config_mcam_entry`, `npc_cn20k_enable_mcam_entry`, `npc_cn20k_read_mcam_entry`, `npc_cn20k_copy_mcam_entry`, `npc_cn20k_clear_mcam_entry`, `npc_mcam_idx_2_key_type`, `npc_cn20k_defrag`, `npc_cn20k_dft_rules_alloc`, `npc_cn20k_dft_rules_free`, `npc_cn20k_dft_rules_idx_get`, `npc_cn20k_subbank_calc_free`, `npc_cn20k_idx2vidx`, and `npc_cn20k_vidx2idx`. Mailbox-facing handlers include CN20K MCAM write/read/alloc-and-write, base steering rule read, free count, KEX config, default rule index, profile info, number-of-keywords, and defrag handlers.

The file's central state is the static `npc_priv` of type `struct npc_priv_t`. It owns the subbank array, subbank free/used xarrays, PF/function maps, default-rule maps, MCAM-index to virtual-index maps, the defrag show list, and initialization metadata read from hardware constants. The built-in `npc_mkex_extr_default` profile describes default RX/TX key extraction, including RX channel, L2/L3 broadcast, ltype/flags nibbles, DMAC, VLAN, IPv4/IPv6, TOS, TCP, and UDP fields.

## Control Flow
Initialization starts in `npc_cn20k_init`, which calls `npc_priv_init` to locate the NPC block, read MCAM bank/subbank shape from hardware, initialize xarrays and subbanks, build a pcifunc index map from RVU PF/VF configuration CSRs, and create a midpoint-biased subbank search order. It then programs all MCAM sections as X2 and marks initialization done. Parser setup disables KPM entries and KPUs, loads the KPU profile, programs second-pass KPM mapping, writes PKIND actions, writes KPM CAM/action entries, enables valid entries, and enables corresponding KPUs.

MKEX profile loading chooses either the built-in profile, a custom KPU-provided profile, or a matching profile from the firmware database image. It writes interface KEX CFG, extractor LID registers, extractor/ltype registers, and hash extraction config. MCAM entry programming disables the target entry, clears stale CAM/action/stat fields, emits CAM0/CAM1 values for X2 or X4 bank layouts, writes action/action2/vtag action and hardware priority, then conditionally re-enables the entry. Read/copy paths reverse or duplicate that register layout.

Allocation flows through `npc_cn20k_ref_idx_alloc`. Reference-less allocations prefer already-used compatible subbanks, then free subbanks, then restricted first/last subbanks. Reference-based allocations iterate between reference and limit boundaries in priority direction and fall back to multi-subbank scans when a single subbank cannot satisfy the request. Successful allocations update PF ownership maps; eligible virtual non-contiguous allocations also allocate a stable VIDX and return it to callers. Freeing translates VIDX to physical index, clears subbank bitmaps, moves empty subbanks back to the free pool, deletes PF maps, and removes VIDX maps.

Defrag locks the MCAM and every subbank, builds per-subbank nodes, identifies subbanks containing only virtual allocations, repeatedly moves VIDX-backed entries from sparse subbanks into subbanks with more free space, copies MCAM hardware state and hit stats, updates software maps and `mcam_rules`, and records old/new/virtual mappings in `defrag_lh`.

## State and Persistence Behavior
Persistent hardware state is written to NPC CSRs: KPM CAM/action tables, PKIND actions, KEX extractors, MCAM CAM/action/stat/config registers, MCAM section key type registers, and KPM enable masks. Driver-owned persistent runtime state is in global xarrays and subbank bitmaps for the life of the AF driver. Virtual indexes are intentionally stable API objects while their physical MCAM index can change during defrag. Default rule mappings persist per `pcifunc` until `npc_cn20k_dft_rules_free` erases the xarray entries and hardware rules.

## Dependencies and Integration Points
Depends on Linux xarray, bitmap, mutex, list, field/bit helpers, and RVU register I/O. It integrates with `rvu.h`, `rvu_npc.h`, `rvu_npc_fs.h`, `rvu_npc_hash.h`, `npc_profile.h`, `mbox.h`, `cn20k/npc.h`, and `cn20k/reg.h`. It calls common NPC allocation and verification helpers, NIX interface discovery, PF/VF mapping helpers, firmware-profile mapping helpers, and mailbox request/response types from `mbox.h`.

## Risks
This file is high risk because hardware CSR layout, MCAM key width, and allocator metadata must stay synchronized. Defrag is especially delicate: comments explicitly say rollback is not attempted after internal algorithm errors. `npc_defrag_move_vdx_to_free` does not preserve counters and rewrites `entry2cntr_map` to the new index, which is intentional but observable. Xarray map updates include manual rollback paths that can leave inconsistent state if rollback itself fails. Duplicate `CN20K_SET_EXTR_LT` definitions in the header are harmless but a maintenance smell. Default-rule allocation has known TODOs around PF rule ordering when VF setup happens first.

## Test Signals
Useful validation includes CN20K probe/init/deinit, custom and default KPU/MKEX profile loading, invalid profile signature/version/size handling, RX/TX KEX dump through mailbox, X2 and X4 MCAM write/read/copy/clear/enable, virtual and physical allocation/free, contiguous and non-contiguous allocation with higher/lower/any priority, allocation near restricted first/last subbanks, VIDX stability through defrag, defrag show-list contents, default PF/VF/LBK rule allocation/free, mailbox rejection on invalid interfaces or non-CN20K devices, MCAM hit-stat preservation across defrag, and stress tests with concurrent mailbox operations under `mcam->lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/npc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/npc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/npc.h

## Purpose
Declares the CN20K NPC private interface, constants, parser key extraction macros, subbank metadata, custom KPU/MKEX profile formats, and public functions implemented by `cn20k/npc.c`. It is the local contract for CN20K-specific MCAM allocation, KEX programming, default steering rules, and defragmentation.

## Important APIs, Types, and Functions
Important constants include `MKEX_CN20K_SIGN`, `MAX_NUM_BANKS`, `MAX_NUM_SUB_BANKS`, `MAX_SUBBANK_DEPTH`, `MKEX_END_SIGN`, parse nibble masks, `NPC_CN20K_PARSE_NIBBLE_INTF_RX`, `NPC_CN20K_PARSE_NIBBLE_INTF_TX`, and `NPC_MAX_EXTRACTOR`. CSR helper macros read and write KEX/extractor state through `rvu_read64`/`rvu_write64`. Types include `enum npc_subbank_flag`, `enum npc_dft_rule_id`, `struct npc_subbank`, `struct npc_defrag_show_node`, `struct npc_priv_t`, `struct npc_kpm_action0`, `struct npc_mcam_kex_extr`, and `struct npc_cn20k_kpu_profile_fwdata`.

The exported prototypes cover initialization, parser profile programming, custom KPU application, MCAM allocation/free, MCAM entry manipulation, default rule management, VIDX translation, defrag, and CGX/LBK eligibility checks.

## Control Flow
The header has no standalone runtime flow. It shapes the control flow in `npc.c` by defining the state machine flags for subbanks, the default-rule IDs used for PF/VF/LBK rule installation, packed firmware profile layouts consumed by KPU/MKEX loading, and the function prototypes used by generic RVU/NPC code and mailbox handlers.

## State and Persistence Behavior
`struct npc_priv_t` describes long-lived driver state mirrored from hardware: bank depth, subbank depth, key width, subbank array, PF/function maps, virtual index maps, and the defrag list. `struct npc_mcam_kex_extr` and `struct npc_cn20k_kpu_profile_fwdata` describe persistent firmware/profile data loaded from memory images; their signatures, versions, packed layout, and fixed array dimensions are ABI-sensitive.

## Dependencies and Integration Points
Depends on definitions from the generic RVU/NPC stack for `struct rvu`, `struct npc_kpu_profile_adapter`, `struct npc_lt_def_cfg`, `struct cn20k_mcam_entry`, interface IDs, KEX dimensions, and register I/O helpers. It integrates directly with `cn20k/reg.h` for CN20K CSR offsets and with `mbox.h` for MCAM key type constants and CN20K entry formats.

## Risks
The header encodes hardware and firmware ABI. Changing bitfield order in `npc_kpm_action0`, packed profile structs, parse nibble masks, or maximum extractor/subbank depths can silently break parser programming. `CN20K_SET_EXTR_LT` is defined twice with the same body, which can hide future divergence. Several macros assume caller-local `rvu` and `BLKADDR_NPC` names, making include context important.

## Test Signals
Compile coverage with CN20K NPC enabled, profile signature/version validation, KEX config dump matching programmed extractor arrays, static or runtime checks for packed profile sizes, subbank allocation at maximum depth, default rule ID map round trips, VIDX translation before and after init, and endian/bitfield sanity for `npc_kpm_action0` are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/npc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/reg.h

## Purpose
Defines CN20K-specific RVU mailbox and NPC register offsets used by AF, PF, VF, and NPC programming paths. It adapts mailbox trigger/interrupt addressing and NPC parser/MCAM CSR addressing for the CN20K register map.

## Important APIs, Types, and Functions
This is a macro-only register header. It defines RVUM discovery CSRs, AF/PF/VF mailbox address/config/trigger/interrupt registers, BAR2 selection registers, NIX interrupt helper offsets, CN20K mailbox interrupt bits, NPC extractor/KPM/KPU programming offsets, MCAM section config, CN20K extended MCAM CAM word/action/config/stat offsets, and miss-action offsets.

Key macro families are `RVU_MBOX_AF_*`, `RVU_MBOX_PF_*`, `RVU_MBOX_VF_*`, `NPC_AF_INTFX_EXTRACTORX_CFG`, `NPC_AF_INTFX_EXTRACTORX_LTX_CFG`, `NPC_AF_KPMX_ENTRYX_*`, `NPC_AF_MCAM_SECTIONX_CFG_EXT`, `NPC_AF_CN20K_MCAMEX_BANKX_*_EXT`, and `NPC_AF_CN20K_MCAMEX_BANKX_STAT_EXT`.

## Control Flow
The header has no runtime control flow. Its offsets steer control flow in `mbox.c`, which selects trigger registers based on mailbox direction and device type, and in `npc.c`, which writes parser, MCAM, action, priority, and statistic registers using these address calculations.

## State and Persistence Behavior
Each macro names persistent hardware state. Mailbox register offsets control shared-memory doorbells and interrupt enable/status bits. NPC macros address persistent parser and MCAM tables until reset or driver reprogramming. The extended MCAM macros include bank and CAM selector fields, so incorrect arithmetic would write a different hardware entry while still compiling.

## Dependencies and Integration Points
Includes `../rvu.h` and `../rvu_reg.h`, and is included by CN20K mailbox/NPC code. It integrates with `rvu_read64`, `rvu_write64`, and MMIO `readq`/`writeq` callers. The mailbox trigger offsets are paired with direction setup in `mbox.c`; the MCAM offsets are paired with `cn20k/npc.c` X2/X4 bank layout code.

## Risks
Register headers are blast-radius sensitive. There is a duplicate `RVU_MBOX_AF_VFAF_INT_ENA_W1C` macro and likely typographical naming in `RVU_MBOX_AF_VFAF1_IN_ENA_*`; if consumers expect a different name, they may fail to compile or use older aliases. Statement-expression macros are GNU C specific but acceptable in kernel code. Bit shifts lack explicit parentheses around parameters in some formulas, so callers must pass side-effect-free values.

## Test Signals
Probe and mailbox interrupt tests on CN20K, AF/PF/VF down and up mailbox traffic, NPC parser profile programming, MCAM write/read/copy/stat operations, default rule install, FLR interrupt handling, and register dump comparison against CN20K hardware documentation are useful validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/struct.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/struct.h

## Purpose
Defines CN20K-specific hardware context layouts for NIX SQ/CQ/RQ and NPA aura/pool contexts, plus CN20K RVU mailbox interrupt vector enumerations. These structures are used in mailbox AQ enqueue requests/responses and must match the hardware context format exactly.

## Important APIs, Types, and Functions
Important declarations are `NIX_MAX_CTX_SIZE`, `enum rvu_mbox_pf_int_vec_e`, `enum rvu_af_cn20k_int_vec_e`, `struct nix_cn20k_sq_ctx_s`, `struct nix_cn20k_cq_ctx_s`, `struct nix_cn20k_rq_ctx_s`, `struct npa_cn20k_aura_s`, and `struct npa_cn20k_pool_s`. The contexts contain bitfields for queue enablement, CQ/RQ/SQ indices, scheduler mappings, aura/pool IDs, interrupt controls, buffering, caching/stashing, flow control, LSO, statistics, drops, and reserved hardware words. `static_assert` checks enforce 128-byte context size.

## Control Flow
There is no executable control flow. AQ handlers and mailbox clients choose the CN20K request/response variants from `mbox.h`, then fill these context structures and masks before the AF writes or reads hardware contexts.

## State and Persistence Behavior
Every context struct is a hardware-persistent record. SQ/RQ/CQ fields determine queue operation, interrupt routing, buffering, scheduler association, flow control, and counters. NPA aura/pool fields determine buffer pool ownership, limits, flow control, thresholds, and error interrupt behavior. Reserved fields preserve layout compatibility and must remain sized to keep the 128-byte contract.

## Dependencies and Integration Points
Included by `mbox.h`, which embeds these structs in `nix_cn20k_aq_enq_req`, `nix_cn20k_aq_enq_rsp`, `npa_cn20k_aq_enq_req`, and `npa_cn20k_aq_enq_rsp`. It depends on Linux fixed-width integer types and the compiler's bitfield layout assumptions used throughout the RVU driver. It complements generic `rvu_struct.h` and CN10K context variants.

## Risks
The largest risk is ABI drift: reordering bitfields, changing widths, or fixing apparent typos without hardware confirmation can corrupt queue or pool contexts. One `static_assert` after the CQ struct checks `sizeof(struct nix_cn20k_sq_ctx_s)` again rather than the CQ type, which reduces compile-time coverage for the CQ layout. Mixed `u64` and `uint64_t` bitfields are harmless in practice but inconsistent.

## Test Signals
Build-time `static_assert` coverage, CN20K NIX/NPA LF allocation, AQ read/write/init of RQ/SQ/CQ/aura/pool contexts, queue start/stop traffic, LSO, flow-control/backpressure behavior, interrupt routing, stats counters, and hardware context dump comparisons are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/struct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/common.h

## Purpose
Provides shared RVU AF constants and small helper types for queue memory allocation, admin queues, NPA aura sizing, NIX scheduler/link/action identifiers, packet size limits, channel numbering, RSS defaults, and NDC transaction constants.

## Important APIs, Types, and Functions
Queue sizing macros include `Q_SIZE_*`, `Q_COUNT`, `Q_SIZE`, `AQ_SIZE`, and `AQ_PTR_MASK`. `struct qmem` records DMA-backed queue memory, while `qmem_alloc` and `qmem_free` allocate/free physically contiguous, 128-byte-aligned queue buffers. `struct admin_queue` groups instruction/result qmem and a lock. Other key declarations include `enum npa_aura_sz`, `NPA_AURA_COUNT`, `struct npa_aq_aura_res`, `struct npa_aq_pool_res`, `enum nix_scheduler`, scheduler quantum defaults, link type constants, hardware FRS limits, NIX RX/TX action opcodes, NIX interface/channel/link macros, LSO format indexes, RSS group/table constants, and NDC index/cache type enums.

## Control Flow
The header has limited inline control flow in `qmem_alloc` and `qmem_free`. Allocation validates queue size, allocates the metadata with devres, allocates contiguous DMA memory with alignment slop, adjusts both CPU and IOVA pointers to a 128-byte boundary, and records the offset for later free. Free reverses the alignment adjustment before calling `dma_free_attrs` and releases the devres metadata.

## State and Persistence Behavior
`qmem` allocations persist for the lifetime of admin or hardware queues and expose stable DMA IOVA addresses to device blocks. The queue-size, action, channel, link, RSS, and FRS constants are cross-module ABI and policy state: they determine ring depths, scheduler hierarchy, MCAM actions, physical link/channel numbering, RSS context limits, and packet length constraints.

## Dependencies and Integration Points
Includes `rvu_struct.h` for hardware result/context structures. It is included by `mbox.h` and many AF implementation files for NPA, NIX, NPC, scheduler, and mailbox configuration. It depends on Linux device-managed allocation, DMA APIs, `ilog2`, alignment helpers, and fixed-width integer types.

## Risks
`qmem_alloc` mutates `qmem->base` after DMA allocation, so every free path must subtract `qmem->align`; callers must not cache the original CPU pointer separately. `aligned_addr` is an `int` even though it stores an aligned DMA address expression, which is suspicious on wide DMA addresses. Queue-size macros assume power-of-four growth from 16 entries. Channel/link constants must stay synchronized with hardware and firmware conventions.

## Test Signals
Admin queue allocation/free under probe/remove and failure injection, DMA API debug, alignment checks for CPU and IOVA addresses, NPA/NIX AQ operations, queue-size boundary tests, RSS group allocation, LSO format programming, link/channel mapping for CGX/LBK/SDP/CPT paths, and max/min frame-size configuration tests are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/lmac_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/lmac_common.h

## Purpose
Defines common per-LMAC and per-MAC state shared by CGX and RPM MAC drivers. It abstracts differences in register offsets, interrupt sources, lane layout, stats counts, pause/PTP/FEC/reset operations, and LMAC discovery behind `struct mac_ops`.

## Important APIs, Types, and Functions
`struct lmac` stores command completion wait state, command serialization lock, firmware response, link information, MAC filter bitmap, RX/TX flow-control bitmaps, event callback state, parent `cgx`, multicast filter count, LMAC ID/type, pending-command flag, and name. `struct mac_ops` is the operation table for CGX/RPM-specific behavior: number/type of LMACs, FIFO length, internal loopback, RX/TX stats, pause frame controls, PTP config, RX/TX enable, PFC, reset, FEC stats, stats reset, X2P reset, and RX enable. `struct cgx` stores PCI/MMIO identity, LMAC mapping, command workqueue, global list linkage, feature bits, ops pointer, enabled-LMAC bitmap, and CSR serialization lock. Declared helpers are `cgx_write`, `cgx_read`, `lmac_pdata`, `cgx_fwi_cmd_send`, `cgx_fwi_cmd_generic`, `is_lmac_valid`, and `rpm_get_mac_ops`.

## Control Flow
This header has no executable flow. Runtime MAC code uses the structs to serialize firmware commands through `cmd_lock`/`wq_cmd_cmplt`, dispatch link events through `event_cb`, and call device-specific methods through `mac_ops`.

## State and Persistence Behavior
LMAC state persists per physical port while the MAC driver is loaded. It caches link information, firmware command response state, filter and flow-control resource bitmaps, callback registration, and per-LMAC identity. `cgx` state persists per MAC block and owns MMIO base, workqueue, operation table, feature flags, and the map from LMAC ID to live `struct lmac`.

## Dependencies and Integration Points
Includes `rvu.h` and `cgx.h`, and is consumed by CGX/RPM implementation and AF mailbox handlers that configure link, MAC filters, flow control, PTP, PFC, FEC, and stats. It integrates physical MAC state with RVU PF/VF resource maps and mailbox structures from `mbox.h`.

## Risks
The header is an abstraction boundary between similar but not identical MAC blocks. A missing or incorrect `mac_ops` callback can produce runtime NULL calls or silently unsupported features. Command and event callback locking must match implementation code to avoid lost firmware responses or callbacks after unregister. Fixed `MAX_LMAC_COUNT` and bitmap assumptions must match hardware generations.

## Test Signals
CGX and RPM probe, all LMAC discovery paths, firmware command timeout/completion, link event register/unregister, start/stop RX/TX, MAC filter add/delete/update/reset, pause/PFC/PTP/FEC operations, stats read/reset, internal loopback, X2P reset, hot-unplug/remove with pending events, and invalid LMAC ID rejection are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/lmac_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mbox.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mbox.c

## Purpose
Implements shared mailbox helper routines for RVU AF/PF/VF communication. It initializes mailbox regions, selects direction-specific TX/RX windows and doorbell registers, allocates request/response slots, sends down/up messages, waits for responses, validates replies, creates invalid-message responses, detects pending messages, and maps message IDs to names.

## Important APIs, Types, and Functions
Public functions include `__otx2_mbox_reset`, `otx2_mbox_reset`, `otx2_mbox_destroy`, `otx2_mbox_init`, `otx2_mbox_regions_init`, `otx2_mbox_msg_send`, `otx2_mbox_msg_send_up`, `otx2_mbox_wait_for_rsp`, `otx2_mbox_busy_poll_for_rsp`, `otx2_mbox_wait_for_zero`, `otx2_mbox_alloc_msg_rsp`, `otx2_mbox_get_rsp`, `otx2_mbox_check_rsp_msgs`, `otx2_reply_invalid_msg`, `otx2_mbox_nonempty`, and `otx2_mbox_id2name`. Internal setup is split between CN20K-specific `cn20k_mbox_setup` and generic `otx2_mbox_setup`. `msgs_offset` aligns the first message after `struct mbox_hdr`.

## Control Flow
Setup first chooses TX/RX offsets based on direction: requester directions use the peer's RX window as TX, while responder/up directions use the corresponding up windows. It then chooses the trigger CSR and shift based on AF/PF/VF direction and device generation. Initialization assigns either one contiguous mailbox base per device or per-peer region addresses, initializes locks, and resets headers.

Message allocation takes the per-device spinlock, aligns request and expected response sizes, checks space in TX/RX regions, increments `num_msgs`, zeros the message and header area, initializes `ver`, advances `msg_size`/`rsp_size`, and stores `next_msgoff`. Sending optionally copies from a bounce buffer into hardware memory, writes the mailbox header only if the peer has not already signaled, resets local construction counters, uses `smp_wmb`, clears peer RX `num_msgs`, traces, and rings the direction-specific doorbell with `MBOX_DOWN_MSG` or `MBOX_UP_MSG`.

Response waiting polls until `num_msgs == msgs_acked`, either sleeping up to `MBOX_RSP_TIMEOUT` or busy-polling for one second. Response retrieval and validation walk request and response message chains in parallel, matching IDs and returning response errors. Invalid-message replies allocate a `msg_rsp` with response signature and `MBOX_MSG_INVALID`.

## State and Persistence Behavior
Mailbox state is split between shared hardware memory (`mbox_hdr`, message payloads, peer-visible `num_msgs`) and host-only `struct otx2_mbox_dev` counters (`msg_size`, `rsp_size`, `num_msgs`, `msgs_acked`). Doorbell CSR state is read-modify-written on send. Reset zeros both TX and RX headers and local counters for a peer device.

## Dependencies and Integration Points
Depends on Linux PCI, interrupt/module headers, spinlocks, time/jiffies, MMIO `readq`/`writeq`, memory barriers, and tracing. It includes generic RVU registers, CN20K register definitions, CN20K API detection, mailbox ABI declarations, RVU tracepoints, and `rvu.h`. It is used by AF, PF, VF, CGX, NIX, NPA, NPC, CPT, MCS, SDP, and representor control paths.

## Risks
Ordering is critical: payload and header must become visible before the doorbell. The code relies on spinlocks for local construction but peer synchronization is through shared headers and interrupt registers. If `msgs_acked` is not updated by interrupt handlers, waits time out. `otx2_mbox_msg_send_data` skips rewriting a nonzero `tx_hdr->sig`, so stale signatures must be managed correctly by reset/peer processing. Region setup with sparse `pf_bmap` leaves unselected `mdev` entries uninitialized.

## Test Signals
AF/PF, PF/AF, PF/VF, VF/PF, and up-message traffic on pre-CN20K and CN20K devices, multi-message batches, mailbox full allocation failures, bounce-buffer copy path, response timeout tracepoint, busy-poll path, invalid response ID detection, nonzero response `rc`, invalid-message reply, reset during probe/remove/FLR, sparse region initialization, and doorbell wait-for-zero behavior are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mbox.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mbox.h

## Purpose
Defines the RVU mailbox ABI shared by AF, PF, VF, and device block drivers. It includes mailbox memory layout, direction IDs, message headers, helper prototypes, message ID registry, error-code ranges, and request/response payloads for generic RVU resource management, CGX/RPM, NPA, NIX, NPC, PTP, SDP, CPT, MCS, representor events, and CN20K-specific AQ/MCAM operations.

## Important APIs, Types, and Functions
Core layout definitions are `MBOX_SIZE`, down/up TX/RX offsets and sizes, `MBOX_RSP_TIMEOUT`, `MBOX_MSG_ALIGN`, direction constants, `struct otx2_mbox_dev`, `struct otx2_mbox`, `struct mbox_hdr`, and `struct mbox_msghdr`. Helper prototypes mirror `mbox.c`. `MBOX_MESSAGES`, `MBOX_UP_CGX_MESSAGES`, `MBOX_UP_CPT_MESSAGES`, `MBOX_UP_MCS_MESSAGES`, and `MBOX_UP_REP_MESSAGES` define the message registry and generate `MBOX_MSG_*` enum values.

Important payload families include generic resource attach/detach/free/MSI-X/hardware-capability messages; CGX/RPM link, stats, MAC filter, FEC, pause/PFC, feature, and firmware-data messages; NPA LF/AQ/CN20K AQ messages; NIX LF/AQ/CN10K/CN20K AQ, scheduler, vtag, RSS, RX mode/config, FRS, LSO, backpressure, multicast, inline IPsec, hardware info, bandwidth profile, and stats messages; NPC MCAM allocation/counter/flow/KEX/hash/default-rule/CN20K MCAM messages; PTP operations; CPT LF/register/inline/stats/fault messages; SDP channel messages; MCS MACsec resource/policy/stats/interrupt messages; and representor events.

## Control Flow
The header has no runtime control flow, but its macro registry controls handler dispatch and ID/name generation. Message handlers use the request/response structs selected by each `M(...)` row. `otx2_mbox_alloc_msg` is a small inline wrapper around `otx2_mbox_alloc_msg_rsp` for messages without an expected response-size reservation.

## State and Persistence Behavior
Mailbox structs are serialized into shared memory and are therefore ABI-persistent across driver components and firmware/peer functions. `pcifunc`, message ID, signature, version, next offset, and return code fields define the framing contract. Many payloads contain hardware context snapshots, resource IDs, table indexes, stats, link state, and action encodings that persist in AF-managed hardware until later mailbox commands modify them. CN20K payloads embed CN20K context structs from `cn20k/struct.h` and `cn20k_mcam_entry` with eight keywords and `action2`.

## Dependencies and Integration Points
Includes Linux Ethernet, size, and ethtool headers, plus `rvu_struct.h`, `common.h`, and `cn20k/struct.h`. It is included across AF/PF/VF driver code and acts as the common protocol between mailbox transport (`mbox.c`) and block-specific handlers. It integrates with physical MAC code, NIX/NPA admin queues, NPC flow steering, CPT crypto/IPsec, SDP, MCS MACsec, PTP, eswitch/representor support, and CN20K-specific context programming.

## Risks
This file is highly ABI-sensitive. Changing message IDs, struct sizes, field order, bit definitions, or error-code values can break communication between AF, PF, VF, firmware, and user-visible tooling while still compiling. Several structs intentionally reserve space for future expansion; removing or repurposing reserved fields can break compatibility. The macro registry is central: missing an ID in `otx2_mbox_id2name`-covered lists or mismatching handler names causes dispatch and diagnostics issues. Large fixed arrays in response structs affect mailbox space limits.

## Test Signals
Compile coverage for all generated `MBOX_MSG_*` values, request/response size checks against mailbox region limits, AF/PF/VF resource attach/detach, NPA/NIX/CN20K AQ read/write/init, CGX/RPM link and MAC operations, NPC flow install/delete and CN20K MCAM virtual allocations, PTP ops, CPT inline/stats/register ops, SDP channel queries, MCS resource and stats operations, representor event up/down messages, invalid message IDs, version/signature validation, and cross-version compatibility tests are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mbox.h -->
