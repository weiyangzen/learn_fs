# sources/distributed-fs/ceph-client/net/nfc/llcp_core.c

Purpose: Implements the LLCP link core: per-device local registration, SAP allocation, general-bytes negotiation, SYMM-driven tx/rx scheduling, PDU receive dispatch, connected-socket state transitions, SDP handling, raw socket mirroring, and MAC up/down integration.

Important APIs and functions: Public functions include `nfc_llcp_sock_link`, `nfc_llcp_sock_unlink`, `nfc_llcp_socket_remote_param_init`, `nfc_llcp_find_local`, `nfc_llcp_local_put`, `nfc_llcp_get_sdp_ssap`, `nfc_llcp_get_local_ssap`, `nfc_llcp_put_ssap`, `nfc_llcp_general_bytes`, `nfc_llcp_set_remote_gb`, `nfc_llcp_send_to_raw_sock`, `nfc_llcp_queue_i_frames`, `nfc_llcp_recv`, `nfc_llcp_data_received`, `nfc_llcp_mac_is_down`, `nfc_llcp_mac_is_up`, `nfc_llcp_register_device`, and `nfc_llcp_unregister_device`.

Control flow: The NFC core registers a local object per device. MAC up starts initiator tx work or target link timer. TX work sends one queued PDU or a SYMM keepalive, mirrors to raw sockets, calls `nfc_data_exchange`, and refreshes link timeout. RX completion stores `rx_pending`, cancels the link timer, runs `rx_work`, mirrors to raw sockets, dispatches by PDU type, schedules tx work, and frees the skb.

State and persistence: `llcp_devices` globally tracks local objects under a spinlock. Each local is kref-managed and also holds an `nfc_dev` reference. Persistent per-link state includes local/remote GB, remote MIU/LTO/WKS/OPT, SAP bitmaps/counters, pending SDP requests, socket lists, target index, RF/communication modes, timers, work items, and tx/rx queues.

Dependencies and integration points: Integrates with NFC DEP link callbacks, generic netlink SDP result delivery, raw NFC sockets, LLCP socket implementation, and PDU builders in `llcp_commands.c`.

Risks: `nfc_llcp_general_bytes` calls `nfc_llcp_local_put(local)` and then returns `local->gb`, which is risky if the local ref can drop to zero before the caller copies the bytes. Many receive paths assume PDU length is sufficient before indexing header/sequence/reason bytes. Socket release while tx work scans local queues is protected partly by skb queue locks but needs careful concurrency testing.

Test signals: Cover local refcounting and device unregister, SAP allocation/free for WKS/SDP/local ranges, remote GB parsing failures, SYMM timeout link down, PDU dispatch for all known PDU types, AGF nested PDU parsing, connect/CC/DM/DISC transitions, SDP request/response and timeout paths, raw socket mirroring, and MAC up/down lifecycle.
