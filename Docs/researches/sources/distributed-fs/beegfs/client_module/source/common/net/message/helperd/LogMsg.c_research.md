# sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/LogMsg.c

## Research
`LogMsg.c` implements helper-daemon log-entry message payload handling. The payload wire order is log level, thread ID, thread name string, context string, and log message string. Serialization writes all fields; deserialization reads them in order and fails on the first malformed field.

Control flow is sequential and field-oriented. State includes integer fields plus non-owned string pointers/lengths; deserialized strings are receive-buffer slices. Dependencies include `LogMsg.h`, `Node.h`, `ListTk`, `NodeStoreEx`, and socket/app headers, although the active functions use mainly serialization. Integration points are legacy/helperd log forwarding paths where kernel/client logs are transported to a helper process. Risks are fixed string lifetime, large log truncation before this message type, no local validation of log level range, and stale includes. Test signals are helper log request/response behavior, round-trip preservation of thread/context/message fields, and malformed string rejection.
