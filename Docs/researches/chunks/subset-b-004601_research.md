# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_hsi.h lines 7575-10880

## Chunk Scope

This chunk is the tail of the QED hardware/software interface header. It is not
executable driver logic; it defines the host-visible ABI layouts shared by the
Linux QED driver and the QLogic/Marvell firmware for RDMA storage offloads and
related TCP-based protocols. The range starts in the final fields of an E4
Xstorm RoCE aggregation context, continues through RoCE request/response
aggregation contexts, then defines iWARP connection contexts, iWARP ramrod and
event payloads, FCoE connection contexts and ramrod/event identifiers, and the
first iSCSI connection context definitions before the header guard closes.

The definitions are source-tree critical because `qed_cxt.c` uses the context
types in the global connection-context union, `qed_sp.h` embeds the ramrod
payload types in the slow-path command union, and protocol modules such as
`qed_iwarp.c`, `qed_roce.c`, `qed_ll2.c`, and `qed_fcoe.c` fill or interpret
these structures when posting commands to firmware.

## Purpose and Responsibilities

- Publish exact little-endian memory layouts for firmware-owned connection
  contexts in Mstorm, Tstorm, Ustorm, Xstorm, Ystorm, and Pstorm.
- Provide bit-mask and shift constants for compact `u8`/`__le16` flag fields,
  including condition flags, enable bits, rule gates, queue-manager membership,
  flush/error state, producer/consumer threshold tracking, and protocol feature
  toggles.
- Define the `roce_flavor` selector used by RoCE packet handling for plain
  RoCE and routable RoCE over IPv4/IPv6.
- Define iWARP control-plane payloads for TCP offload, MPA offload, create QP,
  modify/query/destroy/abort command identifiers, async/sync EQE opcodes, and
  firmware return codes.
- Define FCoE static and aggregation contexts for each storm engine, including
  Ethernet/VLAN encapsulation state, queue PBL addresses, FC IDs, timers,
  protection-information bits, cached WQEs, and ramrod wrapper/event enums.
- Define iSCSI connection context fragments at the end of the header, including
  combined TCP/iSCSI storm contexts and aggregation contexts for Xstorm,
  Tstorm, Ustorm, Mstorm, and Ystorm.

## Important APIs, Types, and Constants

- RoCE aggregation contexts:
  `mstorm_roce_conn_ag_ctx`, `mstorm_roce_req_conn_ag_ctx`,
  `mstorm_roce_resp_conn_ag_ctx`, `tstorm_roce_req_conn_ag_ctx`,
  `tstorm_roce_resp_conn_ag_ctx`, `ustorm_roce_req_conn_ag_ctx`,
  `ustorm_roce_resp_conn_ag_ctx`, `xstorm_roce_req_conn_ag_ctx`,
  `xstorm_roce_resp_conn_ag_ctx`, `ystorm_roce_conn_ag_ctx`,
  `ystorm_roce_req_conn_ag_ctx`, and `ystorm_roce_resp_conn_ag_ctx`.
  These structures expose per-QP firmware scheduler state: `state`,
  `physical_q0`, `conn_dpi`, send/request queue consumers and producers,
  retransmit PSNs, ACK/IRQ tracking, DIF counters and error offsets, ORQ
  fences, responder RXMIT data, and flush/error condition flags.
- `enum roce_flavor`: identifies `PLAIN_ROCE`, `RROCE_IPV4`, and
  `RROCE_IPV6`. Nearby driver code maps public RoCE mode to this enum and LL2
  transmit code maps LL2 packet flavor to core BD fields.
- iWARP connection storage:
  `ystorm_iwarp_conn_st_ctx`, `pstorm_iwarp_conn_st_ctx`,
  `xstorm_iwarp_conn_st_ctx`, `tstorm_iwarp_conn_st_ctx`,
  `mstorm_iwarp_conn_st_ctx`, `ustorm_iwarp_conn_st_ctx`,
  `xstorm_iwarp_conn_ag_ctx`, `tstorm_iwarp_conn_ag_ctx`,
  `mstorm_iwarp_conn_ag_ctx`, `ustorm_iwarp_conn_ag_ctx`, and
  `ystorm_iwarp_conn_ag_ctx`. `struct iwarp_conn_context` assembles these into
  the complete connection context allocated through the CDU/ILT context path.
- iWARP ramrod payloads:
  `iwarp_create_qp_ramrod_data` contains QP creation flags for FMR/reserved
  LKey, signaled completions, RDMA read/write, atomics, SRQ, and low-latency
  queue enablement plus PD, SQ/RQ page counts, CQ CIDs, DPI, physical queues,
  QP handle, and SRQ ID.
  `iwarp_tcp_offload_ramrod_data` combines `tcp_offload_params_opt2` with
  `iwarp_offload_params` for TCP connection offload.
  `iwarp_mpa_offload_ramrod_data` carries MPA private-data buffers, TCP CID,
  negotiation mode, active/passive side, RTR preferences, async output buffers,
  shared queue address, receive window, and stats counter.
  `iwarp_modify_qp_ramrod_data`, `iwarp_query_qp_ramrod_data`, and
  `iwarp_query_qp_output_params` define state transition and query ABI.
- iWARP event and status enums:
  `iwarp_eqe_async_opcode` reports connect complete, MPA reply/request,
  handshake complete, cleaned CID, exception, QP error, CQ overflow, and SRQ
  limit/empty events. `iwarp_eqe_sync_opcode` and `iwarp_ramrod_cmd_id` use the
  same command numbering for TCP offload, MPA offload, create/query/modify/
  destroy QP, and abort TCP offload. `iwarp_fw_return_code` enumerates TCP,
  MPA, QP error, and exception causes reported by firmware.
- MPA helpers:
  `mpa_rq_params`, `mpa_ulp_buffer`, `mpa_outgoing_params`,
  `mpa_negotiation_mode`, and `mpa_rtr_type` define Basic/Enhanced MPA private
  data and RTR negotiation fields. `unaligned_opaque_data` describes LL2 data
  used when initial MPA bytes arrive unaligned in TCP payloads.
- FCoE contexts:
  `ystorm_fcoe_conn_st_ctx`, `pstorm_fcoe_conn_st_ctx`,
  `xstorm_fcoe_conn_st_ctx`, `ustorm_fcoe_conn_st_ctx`,
  `tstorm_fcoe_conn_st_ctx`, `mstorm_fcoe_conn_st_ctx`, and their aggregation
  contexts form `struct fcoe_conn_context`. These include FC payload sizes,
  MTU/MSS, source/destination FC IDs, Ethernet MAC/VLAN fields, SQ/XFERQ/RESPQ
  PBLs and indices, cached `fcoe_wqe` entries, queue producers/consumers,
  BDQ/CQ/CMDQ relative offsets, timers, and protection metadata.
- FCoE ramrod/event wrappers:
  `fcoe_conn_offload_ramrod_params`, `fcoe_conn_terminate_ramrod_params`,
  `fcoe_init_ramrod_params`, and `fcoe_stat_ramrod_params` wrap earlier FCoE
  payload definitions. `enum fcoe_event_type` and `enum fcoe_ramrod_cmd_id`
  enumerate init, destroy, stat, offload connection, terminate connection, and
  error flows.
- iSCSI context tail:
  `ystorm_iscsi_conn_st_ctx`, `pstorm_iscsi_tcp_conn_st_ctx`,
  `xstorm_iscsi_tcp_conn_st_ctx`, `xstorm_iscsi_conn_ag_ctx`,
  `tstorm_iscsi_conn_ag_ctx`, `ustorm_iscsi_conn_ag_ctx`,
  `tstorm_iscsi_conn_st_ctx`, `mstorm_iscsi_conn_ag_ctx`,
  `mstorm_iscsi_tcp_conn_st_ctx`, `ustorm_iscsi_conn_st_ctx`,
  `iscsi_conn_context`, `iscsi_init_ramrod_params`, and
  `ystorm_iscsi_conn_ag_ctx`. These complete the header with TCP/iSCSI
  offload state and iSCSI init parameters.

## Control Flow and Firmware Protocol Flow

This header chunk has no functions, branches, or loops, but it encodes control
flow as firmware state-machine fields:

- Queue-manager residency bits such as `EXIST_IN_QM0` through `EXIST_IN_QM3`
  tell firmware scheduler logic whether the connection currently has work in a
  physical queue.
- `state` bytes in Xstorm/Tstorm/Mstorm contexts are firmware connection-state
  slots. Driver code normally initializes or transitions them indirectly by
  posting ramrods instead of writing state-machine code in the host.
- Two-bit condition fields (`*_CF*`, `*_FLUSH_*`, `*_RX_ERROR_*`,
  `*_TIMER_STOP_ALL_*`, `*_SLOW_PATH`, and similar) pair with one-bit enable
  fields (`*_CF*_EN`, `*_RULE*EN`) to let firmware evaluate events, timers,
  queue thresholds, and protocol-specific decision rules.
- RoCE request contexts coordinate send queue advancement, retransmit and PSN
  state, DIF error accounting, ORQ fences, invalidation fences, max-ORD
  gating, eDPM enablement, and migration flags. Responder contexts coordinate
  RQ/IRQ producer-consumer state, force ACK/retransmit work, RX/TX error
  signals, and syndrome reporting.
- iWARP TCP offload proceeds through a slow-path command using
  `iwarp_tcp_offload_ramrod_data`; later MPA negotiation uses
  `iwarp_mpa_offload_ramrod_data`; then QP creation and modifications use the
  QP ramrod payloads. The async EQE opcodes and firmware return codes in this
  chunk are the completion/error side of that protocol flow.
- FCoE offload uses `fcoe_init_ramrod_params` for function setup, per-connection
  `fcoe_conn_offload_ramrod_params` and `fcoe_conn_context` for offloaded FC
  exchanges, and terminate/stat ramrods for cleanup and accounting. The Xstorm
  FCoE aggregation context contains SQ/XFERQ/RESPQ decision enables, which are
  firmware-side control points for deciding which FC queue can progress.
- iSCSI offload state at the end mirrors the same pattern: a combined TCP/iSCSI
  static context plus storm aggregation contexts with flush, cleanup, queue
  decision, and slow-path bits.

## State and Persistence Behavior

The state represented here is persistent hardware/firmware connection context
state, not ordinary kernel heap-only state. QED allocates connection contexts
through the context manager (`qed_cxt.c`) and stores them in CDU/ILT-backed
memory visible to firmware. The `union conn_context` in `qed_cxt.c` includes
`roce_conn_context`, `iwarp_conn_context`, `fcoe_conn_context`, and
`iscsi_conn_context`; therefore the size and alignment of these structs directly
affect context allocation, ILT sizing, and firmware indexing.

Fields use fixed-width kernel types and little-endian annotations such as
`__le16`, `__le32`, and `struct regpair`. Host code must convert CPU values
with `cpu_to_le16()`, `cpu_to_le32()`, `DMA_REGPAIR_LE()`, `DMA_LO_LE()`, and
`DMA_HI_LE()` before posting ramrods or programming DMA addresses. The layouts
also contain explicit padding (`reserved`, `*_padding`, `e5_reserved`,
`a0_reserved`) to preserve firmware ABI offsets across chip generations and
firmware revisions.

Many producer/consumer fields are long-lived connection progress markers:
RoCE `sq_cons`, `sq_prod`, `rq_cons`, `rq_prod`, `irq_cons`, `irq_prod`,
`snd_una_psn`, `snd_nxt_psn`, and ORQ counters; iWARP `sq_tx_cons`,
`irq_cons`, `hq_cons`, `orq_cons`, and shared queue page addresses; FCoE
`sq_cons`, `sq_prod`, `xferq_prod`, `xferq_cons`, `respq_prod`, `respq_cons`,
PBL current/next page addresses, and cached WQEs; iSCSI SQ/R2TQ/HQ producer
and consumer values. These values persist for the life of an offloaded
connection and are consumed by firmware across interrupts, timers, retransmit
events, and slow-path commands.

## Dependencies and Integration Points

- `qed_hsi.h` depends on earlier declarations in the same header, including
  `regpair`, `timers_context`, `rdma_init_func_ramrod_data`,
  `tcp_init_params`, `tcp_offload_params_opt2`, `rdma_srq_id`,
  `fcoe_wqe`, `fcoe_conn_offload_ramrod_data`,
  `fcoe_conn_terminate_ramrod_data`, `fcoe_init_func_ramrod_data`,
  `fcoe_stat_ramrod_data`, `pb_context`, and `iscsi_spe_func_init`.
- `qed_cxt.c` consumes `iwarp_conn_context`, `fcoe_conn_context`, and
  `iscsi_conn_context` in `union conn_context`, so any layout change affects
  CDU context sizing and the ILT memory model.
- `qed_sp.h` embeds `iwarp_create_qp_ramrod_data`,
  `iwarp_tcp_offload_ramrod_data`, and `iwarp_mpa_offload_ramrod_data` in the
  slow-path ramrod union; `qed_iwarp.c` fills those payloads with DMA buffer
  addresses, endpoint handles, physical queues, TCP 4-tuple data, MPA mode,
  RTR preferences, and QP capability bits before calling `qed_spq_post()`.
- `qed_iwarp.c` also interprets the MPA async output and uses the MPA enums in
  this chunk to negotiate Basic versus Enhanced MPA, ORD/IRD, and RTR type
  behavior.
- `qed_fcoe.c` posts FCoE init/offload/terminate/stat ramrods and obtains
  `fcoe_conn_context` information through the context manager while validating
  PF FCoE parameters such as CQ counts, MTU, PBL pages, timers, and physical
  queues.
- `qed_roce.c` maps higher-level RoCE mode to `enum roce_flavor`, while
  `qed_ll2.c` uses RoCE flavor information when constructing transmit BD data
  for LL2 RoCE packets.
- Firmware is the most important integration point. The comments name these
  structures as "passed by driver to FW" or "storm context" layouts. The host
  driver and firmware must agree on every offset, width, endian conversion, and
  reserved bit convention.

## Risks and Edge Cases

- ABI drift is the dominant risk. Reordering a field, changing a type width,
  removing padding, or altering a mask/shift constant can silently corrupt
  firmware context interpretation even if the C code still compiles.
- Reserved bits are not free. Many fields carry `A0_RESERVED`, `E5_RESERVED`,
  or generic `RESERVED` names. Driver code should preserve zeros unless a
  matching firmware contract explicitly assigns meaning to the bit.
- Endian mistakes are easy because the structs mix `u8` flags with `__le16`,
  `__le32`, and `regpair` values. A missing `cpu_to_le*()` conversion in code
  that fills these ramrods may work on little-endian hosts and fail on
  big-endian configurations.
- The condition-flag and enable-bit pairs are dense. Using a mask from the
  request side on a responder context, or from RoCE on iWARP/FCoE/iSCSI, can
  enable an unrelated firmware rule because the fields intentionally reuse
  compact bit positions.
- Context sizing is cross-protocol. Because `union conn_context` takes the
  maximum of these layouts, growth in FCoE/iWARP/iSCSI contexts can affect ILT
  allocation and memory pressure for all connection types.
- Several `enum` values start at nonzero offsets, especially iWARP synchronous
  opcodes and ramrod command IDs starting at 13. Code must use symbolic enums
  rather than assuming dense zero-based command numbering.
- Fields such as shared queue page addresses, PBL addresses, async EQE output
  buffers, and ULP private-data buffers are DMA contracts. The host must keep
  those buffers mapped, aligned, and alive until firmware completion or cleanup
  guarantees they are no longer referenced.
- Protocol boundaries are adjacent in one header. The chunk moves from RoCE to
  iWARP to FCoE to iSCSI, so broad search-and-replace edits or generated mask
  updates can accidentally modify similarly named fields in the wrong protocol.

## Test Signals and Validation Hooks

- Compile-time coverage should include all protocol objects that include
  `qed_hsi.h`: at minimum QED core context management, RDMA/iWARP, RoCE LL2,
  FCoE, and iSCSI-enabled builds. Header-only ABI changes should be treated as
  requiring broad driver rebuilds, not protocol-local rebuilds.
- Static layout checks are valuable when available: compare `sizeof()` and
  `offsetof()` for `iwarp_conn_context`, `fcoe_conn_context`,
  `iscsi_conn_context`, and important ramrod structs against firmware HSI
  expectations.
- Runtime iWARP signals include successful TCP offload, MPA offload,
  create-QP/modify-QP/query-QP flows, correct async EQE decoding for connect,
  MPA, CID-cleaned, exception, CQ overflow, and SRQ limit/empty events, and
  correct mapping of firmware return codes to upper RDMA CM errors.
- Runtime RoCE signals include correct RoCE flavor selection, successful QP
  send/receive traffic, retransmit/force-ACK behavior, error flush completion,
  and no corruption of PSN, ORQ, IRQ, SQ, or RQ producer-consumer state.
- Runtime FCoE signals include init/offload/terminate/stat ramrod completion,
  correct VLAN/MAC/FC ID programming, queue producer-consumer progress for SQ,
  XFERQ, RESPQ, CQ, CMDQ, and BDQ resources, protection-info behavior, and
  cleanup after timers or error paths.
- Runtime iSCSI signals include successful context allocation for TCP/iSCSI
  connections, cleanup/flush completion, queue decision rule progress, checksum
  error accounting, and stable SQ/R2TQ/HQ producer-consumer tracking.
- Diagnostic output in protocol modules is a useful smoke signal: iWARP debug
  prints expose fields filled from `iwarp_tcp_offload_ramrod_data`, while FCoE
  start paths validate PF parameters before posting ramrods. Any mismatch
  between debug values and expected host configuration points to a ramrod
  population or endian/layout issue.
