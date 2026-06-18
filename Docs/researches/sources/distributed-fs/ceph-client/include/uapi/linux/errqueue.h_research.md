## sources/distributed-fs/ceph-client/include/uapi/linux/errqueue.h

Purpose: This header defines ancillary data structures for socket error queues, including extended errors, RFC 4884 data, zero-copy and txtime status, and timestamping control messages.

Important APIs and types: `struct sock_ee_data_rfc4884` carries extension length and flags. `struct sock_extended_err` carries errno, origin, type, code, info, and data or RFC4884 metadata. Origins include local, ICMP, ICMPv6, TX status/timestamping, zero-copy, and txtime. `SO_EE_OFFENDER()` locates the following offender sockaddr. `struct scm_timestamping` and `struct scm_timestamping64` expose three timestamps for socket timestamping, with kernel/userspace timespec layout handling. The timestamp type enum distinguishes send, scheduler, ACK, and completion timestamps.

Control flow and state: Network stack code queues extended errors or timestamp completions on a socket error queue. Userspace receives them with `recvmsg(MSG_ERRQUEUE)` and parses cmsgs into these structures. The values describe asynchronous status for earlier sends or network errors.

Persistence and dependencies: State is per-socket queued ancillary data. The header depends on `<linux/types.h>` and `<linux/time_types.h>`.

Integration points: It integrates with IP_RECVERR/IPV6_RECVERR, SO_TIMESTAMPING, MSG_ZEROCOPY, SO_TXTIME, ICMP diagnostics, and hardware/software timestamping.

Risks and test signals: Risks include old versus 64-bit timespec mismatch, assuming offender address is always present, treating timestamp origin incorrectly, missing zero-copy copied fallback, and RFC4884 extension validation. Tests should send packets that trigger ICMP errors, TX timestamps, zerocopy completions, and txtime failures; parse both timestamping structs; validate offender sockaddr alignment; and check origin/code-specific interpretation.
