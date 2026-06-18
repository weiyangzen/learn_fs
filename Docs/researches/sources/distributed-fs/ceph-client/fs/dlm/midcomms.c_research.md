# sources/distributed-fs/ceph-client/fs/dlm/midcomms.c

## Purpose
`midcomms.c` adds DLM-level reliability and protocol-version handling above lowcomms. For DLM 3.2 peers it wraps messages in `DLM_OPTS`, assigns sequence numbers, tracks unacknowledged messages, retransmits after transport errors, drops duplicate receives, and performs a DLM FIN/ACK shutdown state machine.

## Important APIs, Types, And Functions
Key types are `struct midcomms_node` and `struct dlm_mhandle`. Important exports include `dlm_midcomms_addr()`, `dlm_midcomms_get_mhandle()`, `dlm_midcomms_commit_mhandle()`, `dlm_validate_incoming_buffer()`, `dlm_process_incoming_buffer()`, `dlm_midcomms_unack_msg_resend()`, lifecycle wrappers, member add/remove functions, `dlm_midcomms_close()`, `dlm_midcomms_shutdown()`, debug accessors, and `dlm_midcomms_rawmsg_send()`.

## Control Flow
Address registration calls lowcomms address setup, creates a `midcomms_node`, initializes sequence counters and send queues, and creates debugfs communication state. On send, `dlm_midcomms_get_mhandle()` checks node version. Version 3.1 sends a raw lowcomms message. Version 3.2 may send a threshold ACK first, allocates a wrapped lowcomms message, inserts the handle into the send queue via callback, fills an options header, and assigns a sequence. Commit finalizes `o_nextcmd`, traces, and commits the lowcomms message.

Receive validation first uses lowcomms-visible `dlm_validate_incoming_buffer()` to determine complete frame lengths. `dlm_process_incoming_buffer()` dispatches by `h_version`. Version 3.1 directly accepts RCOM/MSG after minimal length checks. Version 3.2 accepts early RCOM status/name messages for version detection without the reliability wrapper, handles `DLM_OPTS` by checking outer and inner lengths, and passes sequenced inner packets to `dlm_midcomms_receive_buffer()`. ACKs release all send-queue handles with sequence lower than the acknowledged sequence.

Shutdown uses reduced TCP-like states: `CLOSED`, `ESTABLISHED`, `FIN_WAIT1`, `FIN_WAIT2`, `CLOSE_WAIT`, `LAST_ACK`, and `CLOSING`. Member add/remove updates per-node `users`; zero users or received FIN drives active or passive FIN exchange. Forced close sets `DLM_NODE_FLAG_CLOSE`, wakes waiters, closes lowcomms, removes debugfs and the node from the hash, flushes send queues, and RCU-frees the node.

## State And Persistence
Per-node state includes detected protocol version, send and receive sequence counters, unacknowledged send queue, delivered-message ACK counters, shutdown flags/state, users count, waitqueue, and debugfs pointer. It is in-memory and tied to node membership/address lifetime. Unacknowledged 3.2 messages persist in memory until ACKed, resent, flushed, or node close.

## Dependencies And Integration Points
Midcomms depends on lowcomms message allocation/resend, config constants, DLM wire structures, lock receive dispatch `dlm_receive_buffer()`, debugfs communication files, tracepoints, memory cache wrappers, and errno conversion helpers indirectly through DLM packet handling.

## Risks
Sequence arithmetic and send-queue deletion are concurrency-sensitive; ACK receive can release message handles quickly after commit. Version detection relies on early RCOM name/status messages for backward compatibility. The comments call out known gaps: unaligned message lengths, incomplete tail-size validation, and future fencing needs for bad sequence behavior or shutdown timeouts.

## Test Signals
Exercise mixed 3.1/3.2 protocol peers, duplicate and out-of-order message receives, socket reconnect retransmission, ACK threshold behavior, active/passive shutdown state transitions, forced node fencing close, and debug raw-message injection. KASAN/KCSAN are useful around ACK/commit races and node removal.
