# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/OpenFileMsg.h

## Research
`OpenFileMsg.h` declares outgoing open-file metadata requests. It defines feature flags for quota information, file event payload, and bypassing metadata access checks. The struct embeds `NetMessage`, stores client numeric ID, non-owned `EntryInfo`, access flags, and optional non-owned `FileEvent`. The inline initializer sets `NETMSGTYPE_OpenFile`, stores fields, and sets the event flag when event data is present.

Control flow is construction and flag setup, with serialization in the `.c` file. State is non-owning for entry/event pointers. Dependencies include `EntryInfo.h`, `FileEvent.h`, and `NetMessage.h`. Integration points are VFS open/create workflows, session tracking, quota/access policy, and file-event logging. Risks are the unused `sessionIDLen` field suggesting legacy drift, stale entry info pointers, incorrect bypass flag use, and retry semantics. Test signals are open request serialization and `OpenFileRespMsg` parsing under normal, denied, and event-logging cases.
