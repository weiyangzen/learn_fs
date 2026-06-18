# sources/distributed-fs/ceph-client/net/sctp/inqueue.c

## Purpose
`inqueue.c` implements the SCTP receive inqueue abstraction. It accepts packet-level `struct sctp_chunk` objects produced by `sctp_rcv()` and exposes chunk-level iteration to the SCTP state-machine top-half handler. The important job is splitting bundled SCTP packets and SCTP GSO frag-list packets into individual chunks while preserving enough skb/control-block context for later processing.

## Important APIs, Types, And Functions
The external API is small: `sctp_inq_init()`, `sctp_inq_free()`, `sctp_inq_push()`, `sctp_inq_peek()`, `sctp_inq_pop()`, and `sctp_inq_set_th_handler()`. State is in `struct sctp_inq`: `in_chunk_list` for queued packet chunks, `in_progress` for the packet currently being walked, and `immediate` for the handler callback. Important per-chunk flags maintained here are `singleton`, `end_of_packet`, `pdiscard`, `data_accepted`, `auth`, `has_asconf`, `chunk_hdr`, `chunk_end`, and `head_skb`.

## Control Flow
`sctp_inq_push()` drops chunks whose receiver was already marked dead, appends live chunks to `in_chunk_list`, updates association input packet stats, and directly invokes the configured work callback. Despite the `work_struct` shape, this path is synchronous at a known lock-safe point.

`sctp_inq_pop()` first completes any prior `in_progress` packet. If the previous chunk ended a packet, hit a parse-discard condition, or was a singleton, it advances through GSO `frag_list`/`next` skb chains or frees the packet chunk. If more chunks remain in the same skb, it advances `skb->data` to the prior padded `chunk_end`. When pulling a new packet, it handles SCTP GSO cover-letter skbs, saves RPS hash to the association socket, copies input control block data from a GSO head skb to fragment skbs, then initializes per-chunk parse flags.

For every popped chunk it sets `chunk_hdr`, computes padded `chunk_end`, pulls the chunk header, invalidates `subh`, and classifies the chunk as bundled, end-of-packet, or malformed. Malformed chunk lengths are not immediately freed here; `pdiscard` lets the state machine account and discard consistently.

## State And Persistence
The inqueue is volatile per endpoint/association receive state. It owns queued packet chunks until they are popped or freed. `sctp_inq_chunk_free()` restores `chunk->skb` to `head_skb` before freeing so GSO-owned resources are released from the correct head.

## Dependencies And Integration Points
This file depends on skbuff layout helpers, SCTP chunk allocation/freeing, `sctp_list_dequeue()`, SCTP state-machine callback wiring, and per-association stats. It is called from `input.c` receive/backlog paths and consumed by the state machine configured through `sctp_inq_set_th_handler()`.

## Risks
The high-risk logic is skb pointer movement across bundled chunks and GSO fragment lists. Incorrect `chunk_end` or `skb_pull()` arithmetic can desynchronize parsing, while freeing the wrong skb in GSO mode can leak or double-free. The direct callback model assumes caller lock context is correct; changing it to scheduled work would affect locking and object lifetime.

## Test Signals
Test with single-chunk packets, multi-chunk bundles, malformed short chunk lengths, padded chunk boundaries, SCTP GSO skbs with frag lists, cover-letter GSO skbs, dead receiver drops, queue free with active `in_progress`, and state-machine handler invocation ordering.
