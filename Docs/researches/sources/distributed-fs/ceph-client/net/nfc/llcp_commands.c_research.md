# sources/distributed-fs/ceph-client/net/nfc/llcp_commands.c

Purpose: Builds and parses LLCP TLVs and constructs outbound LLCP PDUs for link management, connection setup, service discovery, connected I-frame data, unnumbered UI data, disconnect, DM, SYMM, CC, and RR.

Important APIs and functions: TLV APIs include `nfc_llcp_build_tlv`, `nfc_llcp_build_sdres_tlv`, `nfc_llcp_build_sdreq_tlv`, `nfc_llcp_free_sdp_tlv`, `nfc_llcp_free_sdp_tlv_list`, `nfc_llcp_parse_gb_tlv`, and `nfc_llcp_parse_connection_tlv`. PDU APIs include `nfc_llcp_send_disconnect`, `nfc_llcp_send_symm`, `nfc_llcp_send_connect`, `nfc_llcp_send_cc`, `nfc_llcp_send_snl_sdres`, `nfc_llcp_send_snl_sdreq`, `nfc_llcp_send_dm`, `nfc_llcp_send_i_frame`, `nfc_llcp_send_ui_frame`, and `nfc_llcp_send_rr`.

Control flow: Outbound connected setup builds MIUX/RW/service-name TLVs, allocates a PDU with `llcp_allocate_pdu`, and queues it on `local->tx_queue`. I-frame send copies the user message, fragments by remote MIU, queues per-socket PDUs, and calls `nfc_llcp_queue_i_frames` under the socket lock. UI frames bypass connected flow control and enqueue directly to the local tx queue after checking that the local object is still listed.

State and persistence: The file mutates remote parameters on `nfc_llcp_local` and `nfc_llcp_sock`, manages pending SDP request lists and timers, enqueues skbs onto local and socket tx queues, and stores UI source/destination SAPs in skb control data for recvmsg.

Dependencies and integration points: Depends on `llcp_core.c` for local lookup, raw socket mirroring, and I-frame scheduling; depends on `llcp_sock.c` for socket fields and user msg handling; uses `nfc_data_exchange` to send SYMM immediately.

Risks: TLV parsing does not fully validate that `offset + length + 2` stays within the array before each dereference. `nfc_llcp_build_sdreq_tlv` assumes `uri_len > 0` when checking the last byte. Fragmentation allocates a full temporary user buffer before splitting, which may be costly for large sends. Queue pressure checks depend on `remote_rw` being sane.

Test signals: Fuzz TLV arrays, test all fixed and variable TLV lengths, validate CONNECT/CC TLV composition, exercise I/UI fragmentation at MIU boundaries, force skb allocation failures, verify SDP timeout list handling, and ensure DM/RR queue ordering.
