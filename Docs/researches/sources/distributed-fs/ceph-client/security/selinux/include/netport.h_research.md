## sources/distributed-fs/ceph-client/security/selinux/include/netport.h

### Purpose
`netport.h` declares the SELinux network-port SID cache API. It maps protocol and port number to a policy SID for socket name-bind/name-connect checks.

### Important APIs, types, and functions
The interface has `sel_netport_flush()` and `sel_netport_sid(u8 protocol, u16 pnum, u32 *sid)`.

### Control flow
`hooks.c` calls `sel_netport_sid()` when binding privileged/out-of-ephemeral-range ports or connecting TCP/SCTP sockets, then checks `SOCKET__NAME_BIND` or `*_SOCKET__NAME_CONNECT` permissions.

### State and persistence
The header has no state. The implementation maintains a bounded in-memory cache derived from policy portcon rules.

### Dependencies and integration points
It includes Linux types and is used by socket bind/connect paths plus AVC reset flushing.

### Risks
Protocol/port mismatches can allow or deny the wrong service label. Ephemeral port range logic lives in callers, so tests must cover both cache and caller thresholds.

### Test signals
Test TCP/UDP/SCTP port label lookups, privileged and non-ephemeral bind checks, name_connect denials, policy reload flushing, and unknown protocol behavior.
