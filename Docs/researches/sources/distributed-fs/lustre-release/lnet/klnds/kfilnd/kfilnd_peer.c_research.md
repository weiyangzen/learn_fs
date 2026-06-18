<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_peer.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_peer.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_peer.c_research.md`.

Purpose: manages the per-device peer cache that maps LNet NIDs to kfabric addresses, negotiates hello/session metadata, tracks peer health, and removes stale/down peers.

Important APIs/types/functions: rhashtable params keyed by `kp_nid`; lifecycle `kfilnd_peer_init()`, `kfilnd_peer_destroy()`, `kfilnd_peer_get()`, `kfilnd_peer_put()`; address helpers `kfilnd_peer_get_kfi_addr()` and `kfilnd_peer_target_rx_base()`; health helpers `kfilnd_peer_alive()`, `kfilnd_peer_tn_failed()`, and internal stale/down/delete/purge routines; protocol `kfilnd_peer_process_hello()`.

Control flow: lookup takes an RCU ref if a non-removing peer exists; otherwise it allocates a peer, formats node/service from NID address/net number, inserts a KFI address with `kfi_av_insertsvc()`, initializes state/session key/refcounts, inserts into rhashtable, and marks alive. Transaction failures mark peers stale or down based on errno and optionally delete them to protect RKEY reuse. Hello processing records remote RX base/session key and negotiates version, moving NEW to WAIT_RSP for requests and UPTODATE for responses, then notifies LNet that the peer is up.

State and persistence behavior: peer entries persist in the device rhashtable under RCU/refcounting. Each peer stores KFI address, local/remote session keys, hello state, peer state, last-alive time, remove flag, and RX base. Deletion removes from hash, drops allocation ref, notifies LNet down, removes KFI AV address, and frees via RCU.

Dependencies and integration: depends on Linux rhashtable/RCU/refcount, KFI AV insertion/removal, LNet NID conversion and notification, device session-key generation, endpoint CPT mapping, and transaction failure logic.

Risks: RKEY safety depends on deleting peers before releasing transaction keys in certain failure paths. New-peer hello throttling can replay or drop traffic. `KP_PURGE_LIMIT` ties cache lifetime to timeout. Service/node formatting assumes NID4 address/net layout. RX count support is TODO and currently uses one RX context base.

Test signals: concurrent peer lookup/insert/delete races, hello request/response negotiation, transaction failures with `-EHOSTUNREACH`, `-ENOTCONN`, timeout, and delete true/false, stale peer purge after timeout, KFI AV insertion failures, and LNet up/down notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_peer.c -->
