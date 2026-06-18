# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/flowring.h

Purpose: Declares flowring structures and APIs for msgbuf TX flow management.

Important APIs/types/functions: Defines hash size, invalid flow ID, hash entries, ring status enum, ring object with SKB queue, TDLS entry, top-level flowring object, and all lifecycle/queue/peer APIs.

Control flow: Msgbuf/protocol code owns a `struct brcmf_flowring` and calls these APIs as packets and firmware flowring messages progress.

State and persistence behavior: Runtime in-memory tables, SKB queues, and TDLS list only.

Dependencies and integration points: Uses Ethernet address length, SKB queues, `BRCMF_MAX_IFS`, and `enum proto_addr_mode`.

Risks: Hash size must remain power-of-two. Ring status transitions are convention-based, not enforced by type.

Test signals: Compile msgbuf users; heavy TX flow lifecycle; power-of-two hash assumption.
