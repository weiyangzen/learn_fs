# sources/distributed-fs/ceph-client/net/sctp/chunk.c

Purpose: implements `sctp_datamsg`, the outbound user-message container split into DATA chunks. It handles fragmentation sizing, auth overhead, partial reliability abandonment, failure notification, and refcounted chunk grouping.

Important APIs/types/functions: datamsg lifecycle is managed by `sctp_datamsg_init/new/hold/put/destroy/free()`. `sctp_datamsg_assign()` links chunks to messages. `sctp_datamsg_from_user()` fragments an `iov_iter` into stream-specific DATA chunks, applies PR-SCTP TTL, auth key selection, SACK and Cookie-ECHO bundling headroom, and first/middle/last flags. `sctp_chunk_abandoned()` evaluates TTL and retransmission policies and updates counters. `sctp_chunk_fail()` records send failure on the message.

Control flow: sendmsg creates a datamsg, computes `max_data` from `asoc->frag_point` with fallback, subtracts AUTH/SACK/Cookie-ECHO overhead when needed, loops through the user iterator creating DATA fragments, copies user bytes, restores skb layout, assigns auth key pointer, and links fragments. Error paths free created chunks and the datamsg. Destruction emits send-failed events if requested and releases chunks.

State and persistence: volatile datamsg refcount, fragment list, failure/error fields, delay/abandon flags, and expiration jiffies. Chunks hold datamsg references. PR-SCTP abandoned counters update association and stream state.

Dependencies/integration: stream scheduler/interleaving callbacks, chunk creation and user-copy helpers, AUTH policy/key lookup, association PMTU/frag point, SACK timer/outqueue state, PR-SCTP flags, ULP event generation, and send subscriptions.

Risks: fragment sizing is sensitive to auth overhead and bundling reserves; zero or too-small frag points can cause fallback or failures. Cleanup must release each created chunk exactly once. PR-SCTP abandonment differs before/after TSN assignment and by policy. Explicit auth key selection can reject unknown keys.

Test signals: single and multi-fragment sends, flag placement, SACK-immediate/EOF, pending SACK and pre-cookie reserves, DATA AUTH overhead and explicit key use, zero frag-point fallback, copy/allocation cleanup, TTL/RTX abandonment counters, send-failed events, and datamsg refcount release.
