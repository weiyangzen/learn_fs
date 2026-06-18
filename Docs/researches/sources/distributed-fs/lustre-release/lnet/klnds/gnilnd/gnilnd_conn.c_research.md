# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_conn.c

## Purpose

`gnilnd_conn.c` implements the connection-establishment side of the GNI LNet driver: SMSG mailbox block allocation/registration, connection request datagram packing/unpacking, datagram posting/cancel/probing, active and wildcard connection completion, NAK handling, dgram worker threads, and cleanup of datagrams during network shutdown or stack reset.

It complements `gnilnd_cb.c`: the callback file queues TXs and runs the data path once a `kgn_conn_t` is established; this file creates the underlying GNI endpoint/mailbox pairing that makes SMSG traffic possible.

## Important APIs, Types, And Functions

- SMSG mailbox setup: `kgnilnd_setup_smsg_attr()`, `kgnilnd_map_fmablk()`, `kgnilnd_alloc_fmablk()`, `kgnilnd_unmap_fmablk()`, `kgnilnd_free_fmablk_locked()`, `kgnilnd_find_free_mbox()`, `kgnilnd_setup_mbox()`, and `kgnilnd_release_mbox()`.
- Physical mailbox support: `kgnilnd_count_phys_mbox()`, `kgnilnd_allocate_phys_fmablk()`, `kgnilnd_map_phys_fmablk()`, `kgnilnd_unmap_fma_blocks()`, and `kgnilnd_free_phys_fmablk()`.
- Datagram lookup and lifetime: `kgnilnd_nid2dgramlist()`, `kgnilnd_find_dgram_locked()`, `kgnilnd_find_and_cancel_dgram()`, `kgnilnd_alloc_dgram()`, `kgnilnd_free_dgram()`, `kgnilnd_cleanup_dgram()`, and `kgnilnd_release_dgram()`.
- Connection request protocol: `kgnilnd_pack_connreq()`, `kgnilnd_unpack_connreq()`, `kgnilnd_process_connreq()`, `kgnilnd_send_nak()`, and `kgnilnd_process_nak()`.
- Datagram posting and cancellation: `kgnilnd_post_dgram()`, `kgnilnd_process_dgram()`, `kgnilnd_cancel_dgram_locked()`, `kgnilnd_probe_for_dgram()`, `kgnilnd_setup_wildcard_dgram()`, `kgnilnd_cancel_net_dgrams()`, `kgnilnd_cancel_wc_dgrams()`, `kgnilnd_cancel_dgrams()`, and `kgnilnd_wait_for_canceled_dgrams()`.
- Connection worker paths: `kgnilnd_start_connect()`, `kgnilnd_finish_connect()`, `kgnilnd_probe_and_process_dgram()`, `kgnilnd_reaper_dgram_check()`, `kgnilnd_dgram_waitq()`, `kgnilnd_start_outbound_dgrams()`, `kgnilnd_repost_wc_dgrams()`, and `kgnilnd_dgram_mover()`.

Key state types are `kgn_fma_memblock_t`, `kgn_mbox_info_t`, `kgn_dgram_t`, `kgn_connreq_t`, `kgn_conn_t`, `kgn_peer_t`, `kgn_device_t`, and GNI `gni_smsg_attr_t`.

## Control Flow

Connection setup starts when a peer has queued TXs but no established connection. The reaper in `gnilnd_cb.c` marks the peer as connecting and places it on `gnd_connd_peers`; `kgnilnd_dgram_mover()` calls `kgnilnd_start_outbound_dgrams()`, which removes peers from that list and calls `kgnilnd_start_connect()`.

`kgnilnd_start_connect()` validates that the peer is still active, transitions `gnp_connecting` through `CONNECT` to `POSTING`, and calls `kgnilnd_post_dgram()` for an active `GNILND_CONNREQ_REQ`. Posting creates a temporary connection, binds the endpoint for active connects, sets up an SMSG mailbox for request datagrams, packs source/destination NIDs, stamps, timeout, host ID, CQ ID, and SMSG attributes into `kgn_connreq_t`, then posts the datagram with a GNI ID equal to the dgram pointer.

Wildcard receive datagrams are posted by `kgnilnd_setup_wildcard_dgram()` and reposted by `kgnilnd_release_dgram()`/`kgnilnd_repost_wc_dgrams()`. They listen with `LNET_NID_ANY`, use net 0 for the local NID field, and become inbound connection requests once GNI matches them.

`kgnilnd_dgram_waitq()` waits in a blocking GNI probe path and wakes `kgnilnd_dgram_mover()`. The mover uses `kgnilnd_probe_and_process_dgram()`, which calls `kgnilnd_probe_for_dgram()` to remove a ready dgram from the hash list, test post state, and classify it as complete, pending, timeout, or terminated. Complete request datagrams go through `kgnilnd_process_connreq()`.

`kgnilnd_unpack_connreq()` validates magic, handles byte-swapping, normalizes the source NID for active matches, verifies wildcard destination network, checks protocol version, stamps, timeout, and request type, and for request packets calls `kgnilnd_set_conn_params()` to wire remote SMSG parameters into the endpoint. `kgnilnd_finish_connect()` then creates or finds the peer, rejects duplicates/stale attempts, closes older stale connections, initializes timestamps, marks the connection established, inserts it into peer and CQID hash lists, sends an initial NOOP, moves queued peer TXs to the new connection, notifies LNet, and clears reconnect backoff.

NAK datagrams use the same GNI datagram mechanism but carry an errno. `kgnilnd_process_nak()` either closes stale connections that match the NAK stamps or cancels an in-flight active dgram and adjusts reconnect state.

Mailbox allocation control starts with `kgnilnd_setup_mbox()`, which searches existing FMA blocks via `kgnilnd_find_free_mbox()` and allocates a new virtual FMA block if none are available. FMA blocks are registered with GNI and tracked with bitmaps, available/held counts, debug metadata, version counters, and device MDD/byte counters. Release can free immediately, hold for purgatory, or release a previously held mailbox; once all mailboxes in a virtual block are available it deregisters and frees the block.

## State And Persistence Behavior

No disk persistence is present. State is live kernel state in devices, peers, dgrams, conns, and FMA blocks.

FMA block state transitions include physical or virtual allocation, mapped/live, idle/unmapped, and freed. Physical blocks are preallocated and preserved across normal connection churn; virtual blocks are allocated on demand and freed when all mailboxes are available and no purgatory holds remain. `gnd_fmablk_vers` lets waiters detect that the block list changed while they were sleeping.

Mailbox state is represented by a bit array and counters: total, available, held, next available, maximum timeout, and per-mailbox debug timestamps/counters. `kgnilnd_release_mbox()` requires the endpoint to be destroyed before clearing a mailbox bit, because KGNI may still inspect SMSG blocks until EP teardown.

Dgram state transitions include `USED`, `POSTED`, `PROCESSING`, `CANCELED`, and `DONE`. Dgrams remain on NID hash lists while posted or canceled, and canceled wildcard datagrams may require a full GNI state-machine cycle before safe release. `gnd_canceled_dgrams` tracks outstanding cancellation completions.

Peer connection attempt state uses `GNILND_PEER_IDLE`, `CONNECT`, `POSTING`, `POSTED`, `NEEDS_DEATH`, and `KILL`. These states are protected by `kgn_peer_conn_lock` for peer visibility and `gnd_connd_lock` for the outbound worker queue.

## Dependencies And Integration Points

The file integrates with GNI endpoint/datagram/SMSG/memory APIs, local peer and connection helpers (`kgnilnd_create_conn()`, `kgnilnd_create_peer_safe()`, `kgnilnd_add_peer_locked()`, `kgnilnd_conn_isdup_locked()`, `kgnilnd_close_stale_conns_locked()`, `kgnilnd_set_conn_params()`), LNet NID/notification APIs, hardware NID-to-NIC translation from `gnilnd_hss_ops.h`, and module parameters from `gnilnd_modparams.c`.

## Risks And Edge Cases

- Connection setup races are central. Active and wildcard dgrams can complete while peers are being deleted, NAKed, or reconnected.
- `kgnilnd_release_mbox()` intentionally delays reuse through purgatory. Prematurely clearing `gnm_bit_array` or freeing an FMA block while KGNI can still inspect an endpoint/mailbox risks stale hardware access.
- Datagram cancellation is asynchronous. Some canceled wildcard dgrams are immediately gone, while others return pending and need a later terminated event.
- `kgnilnd_cancel_dgrams()` iterates only to `peer_hash_size - 1`; verify this boundary against hash allocation and wildcard bucket conventions.
- `kgnilnd_map_fmablk()` has a static registration-failure timeout shared across devices/blocks.
- `kgnilnd_unpack_connreq()` must return only `-EBADF` before source NID normalization when it cannot safely NAK.
- Physical FMA blocks are special during stack reset; treating physical and virtual blocks identically can leak or double-deregister MDDs.

## Test Signals

- Mailbox tests should allocate/release virtual and physical FMA blocks, hold and release purgatory mailboxes, exhaust mailbox blocks, and verify MDD/byte/fmablk counters return to expected values.
- Connection-race tests should force simultaneous active connects, active connect versus wildcard receive, duplicate connection request completion, peer deletion during `POSTING`, NAK arriving while connecting, and TX queue migration after establishment.
- Datagram tests should cover successful active request, successful wildcard request, NAK posting, timeout, terminated, canceled wildcard immediate `NO_MATCH`, canceled wildcard `POST_PENDING`, and shutdown wait for `gnd_canceled_dgrams`.
- Protocol validation should inject bad magic, byte-swapped requests, wrong source/destination NID, unsupported version/type, zero stamps, too-small timeout, unknown network, and malformed SMSG attributes.
