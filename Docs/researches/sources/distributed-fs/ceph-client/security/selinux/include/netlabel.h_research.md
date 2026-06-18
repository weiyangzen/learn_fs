## sources/distributed-fs/ceph-client/security/selinux/include/netlabel.h

### Purpose
`netlabel.h` declares SELinux's interface to the NetLabel subsystem and provides no-op fallbacks when NetLabel is disabled. NetLabel carries packet security labels such as CIPSO/CALIPSO across network traffic.

### Important APIs, types, and functions
With `CONFIG_NETLABEL`, the header declares cache invalidation, error reporting, socket security lifecycle helpers, skb SID get/set helpers, SCTP and inet connection setup helpers, socket post-create/connect/setopt helpers, and receive checks. Without NetLabel, inline stubs return neutral values: no label type, null SID, or success.

### Control flow
Socket and netfilter hooks call these helpers while creating sockets, receiving packets, connecting sockets, cloning connections, setting packet labels, and reporting label-related errors. The fallback path lets the rest of SELinux networking compile and execute without NetLabel.

### State and persistence
The header stores no state. Real state is in `sk_security_struct` NetLabel fields and the NetLabel subsystem's own caches/configuration.

### Dependencies and integration points
It includes socket, skb, request_sock, SCTP, AVC, and object-security types. It is tightly integrated with `hooks.c` network receive, connect, SCTP, MPTCP, and netfilter labeling paths.

### Risks
Stub behavior must preserve SELinux semantics when NetLabel is absent. Real builds must avoid stale `nlbl_secattr` data on clone/free/reset and must coordinate NetLabel with XFRM/secmark peer label resolution.

### Test signals
Build with and without `CONFIG_NETLABEL`; test CIPSO/CALIPSO labeling, socket connect and receive checks, SCTP association labeling, packet error handling, and policy/cache invalidation.
