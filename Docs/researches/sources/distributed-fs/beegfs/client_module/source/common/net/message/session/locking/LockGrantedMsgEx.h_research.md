# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/LockGrantedMsgEx.h

## Research
`LockGrantedMsgEx.h` declares the incoming lock-granted notification. It embeds `NetMessage` and stores receive-buffer-backed lock ack ID, ack ID, and `NumNodeID granterNodeID`. Inline getters expose all fields, and init sets `NETMSGTYPE_LockGranted`.

Control flow is init/access plus deserialization/processing in the `.c` file. State is non-owning for strings and fixed-size for the granter ID. Dependencies are `NetMessage.h`. Integration points are distributed lock wait queues, acknowledgment store, and ack manager. Risks are string lifetime, empty ack IDs, and no outgoing serialization support. Test signals are matching lockAckID values waking the correct waiter and granter acknowledgements being queued.
