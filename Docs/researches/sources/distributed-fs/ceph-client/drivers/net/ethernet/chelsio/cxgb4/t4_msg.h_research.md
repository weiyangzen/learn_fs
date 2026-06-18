# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_msg.h

## Purpose

`t4_msg.h` defines the Chelsio Protocol Layer (CPL), work request, RSS, ULP, tunnel LSO, TLS/security, iSCSI, RDMA, L2T, SMT, and firmware wrapper message formats consumed and produced by the `cxgb4` driver. It is a hardware/firmware ABI header: structures map to big-endian descriptor payloads and macros pack or extract bitfields for commands placed on SGE queues or received from hardware/firmware.

## Important APIs, Types, and Constants

- CPL opcode enum covers connection management (`CPL_PASS_OPEN_REQ`, `CPL_ACT_OPEN_REQ`, `CPL_PASS_ACCEPT_REQ`, establish/close/abort/release), data path (`CPL_TX_DATA`, `CPL_RX_DATA`, `CPL_TX_PKT`, `CPL_RX_PKT`), offloads (`CPL_ISCSI_*`, `CPL_RDMA_*`, `CPL_TX_TLS_*`, `CPL_TLS_DATA`, `CPL_RX_TLS_CMP`), firmware wrappers (`CPL_FW4_MSG`, `CPL_FW6_MSG`, payload/ack forms), table operations (`CPL_L2T_WRITE_REQ`, `CPL_SMT_WRITE_REQ`, `CPL_SRQ_TABLE_REQ`), and tunnel/LSO commands (`CPL_TX_TNL_LSO`, `CPL_TX_PKT_LSO`, `CPL_TX_PKT_XT`).
- `enum CPL_error` defines firmware/hardware status values such as TCAM miss/full, bad length/route/SYN, connection reset/existing/timed-out, ARP miss, retransmit/persist/keepalive advice, abort failure, and iWARP/embedded reply indicators.
- Mode enums define connection policy, ULP modes (`NONE`, `ISCSI`, `RDMA`, `TCPDDP`, `FCOE`, `TLS`), CRC flags, abort reset behavior, TX checksum types, congestion algorithms, firmware wrapper types, ULP TX opcodes, ULP TX scatter/gather subcommands, and tunnel LSO types.
- `union opcode_tid` and helpers `CPL_OPCODE_*`, `TID_G`, `MK_OPCODE_TID`, `OPCODE_TID`, `GET_TID`, `TID_TID_*`, and `TID_QID_*` encode/decode the common opcode/TID word.
- `struct rss_header` carries RX opcode, channel/filter/hash metadata, queue id, and hash value with endian-dependent bitfield layout.
- `struct work_request_hdr` plus `WR_HDR` are embedded in outbound work requests. `WR_OP_V()` and related option-field macros pack WR operation and connection options.
- Connection-management structures include passive-open requests/replies, IPv6 variants, accept requests/replies including T5 reply form, active-open T4/T5/T6 IPv4/IPv6 requests, open replies, establish notifications, TCB get/set requests/replies, close server/connection requests/replies, abort request/reply RSS and WR forms, peer close, and TID release.
- TX/RX packet structures include `cpl_tx_pkt_core`, `cpl_tx_pkt`, `cpl_tx_pkt_lso_core`, `cpl_tx_pkt_lso`, `cpl_tx_data`, `cpl_rx_data`, `cpl_rx_data_ack`, and `cpl_rx_pkt`. Macros pack checksum, VLAN, timestamp, LSO, header length, tunnel, and RX error vector fields.
- iSCSI/DDP structures include `cpl_iscsi_hdr`, `cpl_rx_data_ddp`, `cpl_iscsi_data`, `cpl_rx_iscsi_cmp`, and `cpl_tx_data_iso`.
- L2/SMT structures include `cpl_l2t_write_req/rpl`, `cpl_smt_write_req/rpl`, and `cpl_t6_smt_write_req`.
- Firmware wrappers include `cpl_fw4_pld`, `cpl_fw6_pld`, `cpl_fw4_msg`, `cpl_fw4_ack`, `cpl_fw6_msg`, and `cpl_fw6_msg_ofld_connection_wr_rpl`.
- ULP and memory I/O structures include `ulptx_sge_pair`, `ulptx_sgl`, `ulptx_idata`, `ulp_txpkt`, `ulp_mem_io`, and `ulptx_sc_memrd`.
- Tunnel and security structures include `cpl_tx_tnl_lso`, `cpl_tx_sec_pdu`, `cpl_tx_tls_sfo`, `cpl_tls_data`, and `cpl_rx_tls_cmp`.
- Other receive/control messages include trace packets, RDMA terminate, SGE egress update, RX physical DSGL, RX MPS packet, and SRQ table request/reply.

## Control Flow and State Behavior

The header has no functions or executable branches. It shapes driver control flow by letting call sites construct outbound CPL work requests and dispatch inbound completions by opcode. Typical flows are:

- Passive listen setup sends a passive-open request, receives accept requests, replies with accept parameters, and later receives establish/close/abort messages.
- Active open sends an active-open request with generation-specific T4/T5/T6 layout and handles open-reply or establish messages.
- TCB operations send get/set messages using `TCB_WORD`, cookie, mask, and value fields and correlate replies by cookie/status.
- TX packet paths build `cpl_tx_pkt`, `cpl_tx_pkt_lso`, `cpl_tx_tnl_lso`, or `cpl_tx_data` structures before pushing descriptors to SGE queues.
- RX paths decode `rss_header`, `cpl_rx_pkt`, `cpl_rx_data`, TLS/iSCSI completion messages, and hardware error/status fields.
- Firmware events are wrapped in CPL FW4/FW6 messages and then dispatched by nested firmware type.

The state represented here is transport/offload state held by firmware and ASIC tables: TIDs, STIDs/ATIDs, TCB words, L2 table entries, SMT entries, SRQ state, TLS key/context state, RSS queue routing, and sequence/window values. The header owns none of that state; it only defines the serialized representation and bitfield accessors.

## Dependencies and Integration Points

- Includes `<linux/types.h>` for fixed-width, `__be*`, and `__u*` kernel types.
- Macros such as `GET_TID()` depend on `be32_to_cpu()` being visible in including translation units.
- Endian-dependent bitfields depend on Linux `__LITTLE_ENDIAN_BITFIELD` conventions.
- Integrates directly with SGE TX/RX queue code, offload connection manager code, TOE/iSCSI/RDMA/TLS paths, L2 table and source MAC table management, firmware mailbox/event handling, and RSS receive dispatch.
- Uses TCB word definitions from `t4_tcb.h` at call sites, register constants from `t4_regs.h`, and modal values from `t4_values.h`.
- T4/T5/T6 compatibility is represented by parallel structure variants and generation-specific field macros, so adapter-version selection must happen at the call sites.

## Risks and Edge Cases

- This is wire-format ABI. Structure padding, field order, endian conversion, or bit shifts cannot change without breaking hardware/firmware communication.
- Several fields are generation-specific: T5/T6 active-open request layout, T6 header-length fields, T5/T6 TX/RX header encodings, T6 SMT write form, and T6 TX force bit. Using the wrong form for an adapter can produce failed opens, malformed packets, or firmware errors.
- Bitfield layout in `rss_header`, `tcp_options`, `cpl_rx_data`, and trace messages is controlled by endian preprocessor macros; unsupported endian configurations need careful build validation.
- Many macros only shift values and do not mask on write. Callers must pass bounded field values or risk overwriting neighboring bits.
- Some macro names are repeated or aliased, for example `ULPTX_CMD_S`, `ULP_TX_SC_MORE_*`, and `RXF_SYN_*`. Reuse reflects hardware manuals but increases collision/confusion risk.
- The `ULP_TXPKT_DATAMODIFY_G()` macro references `ULP_TXPKT_DATAMODIFY__M` with a double underscore, which appears inconsistent with the defined `ULP_TXPKT_DATAMODIFY_M`; this should be build-covered if the getter is used.
- Flexible array `struct ulptx_sgl::sge[]` requires correct allocation/descriptor length calculation by callers.
- Security/TLS and tunnel LSO fields have many interdependent offsets/lengths. Incorrect payload lengths or header offsets can create malformed packets or crypto offload failures.

## Test Signals

- Compile `cxgb4` with all enabled offload paths to catch structure, macro, and endian dependency regressions.
- Active/passive TCP offload connection tests should cover open, establish, close, abort, TID release, TCB get/set, and error replies.
- RX/TX traffic tests should cover plain packets, checksum offload, VLAN, timestamping, LSO, tunnel LSO, and compressed RX error fields.
- iSCSI, RDMA, and TLS offload tests validate the specialized CPL structures and length/offset packing.
- Firmware command/event tests validate FW4/FW6 wrapper decoding and `cpl_fw4_ack` flag handling.
- Sparse/compiler warnings and structure-size assertions, if present in surrounding code, are valuable because this file is mostly layout definitions.
