# sources/distributed-fs/ceph-client/net/nfc/llcp.h

Purpose: Defines internal LLCP state, constants, local-device structures, socket structures, TLV/PDU constants, and cross-file function prototypes for the Linux NFC LLCP implementation.

Important APIs and types: Key types are `enum llcp_state`, `struct nfc_llcp_local`, `struct nfc_llcp_sock`, `struct nfc_llcp_sdp_tlv`, `struct llcp_sock_list`, and `struct nfc_llcp_ui_cb`. Constants define defaults and limits for LTO/RW/MIU, SAP ranges, LLCP versions, PDU types, TLV types, well-known SAPs, and DM reason codes.

Control flow: The header separates the implementation into socket management, TLV handling, command/PDU building, and core receive/transmit paths by declaring functions implemented in `llcp_core.c`, `llcp_commands.c`, and `llcp_sock.c`.

State and persistence: `struct nfc_llcp_local` persists per-NFC-device LLCP state: refcount, timers/work, tx/rx state, local and remote general bytes, remote link params, SAP bitmaps/counters, pending SDP requests, and socket lists. `struct nfc_llcp_sock` persists per-socket SAPs, service name, flow-control parameters, sequence numbers, queues, accept queue, and parent link.

Dependencies and integration points: Uses Linux networking sockets/skbs and NFC core types. Its prototypes are consumed by NFC device registration, DEP link callbacks, socket protocol registration, and generic netlink SDP result reporting.

Risks: Several fields are protected by different locks (`sdp_lock`, socket-list rwlocks, skb queue locks, socket locks), so users must respect locking boundaries. SAP range math and bitmap offsets are central to correctness and susceptible to off-by-one errors.

Test signals: Compile and runtime tests should cover structure initialization defaults, SAP range boundaries, TLV constants, sequence field extraction, and socket list locking assumptions.
