<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sctp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sctp.h

Purpose: defines the Linux SCTP sockets API extension: socket option numbers, ancillary data structures, notification events, association/address/query structs, PR-SCTP, authentication, stream reset/reconfiguration, UDP encapsulation, and scheduler controls.

Important APIs, types, and functions: `sctp_assoc_t` identifies associations. Socket options include public SCTP options, internal bindx/connectx/peeloff helpers, PR-SCTP, stream reset, event subscription, ASCONF/AUTH/ECN exposure, UDP encapsulation, and PLPMTUD probe interval. Ancillary structs include `sctp_initmsg`, `sctp_sndrcvinfo`, `sctp_sndinfo`, `sctp_rcvinfo`, `sctp_nxtinfo`, `sctp_prinfo`, and `sctp_authinfo`. Notification structs include association, peer address, remote error, send failed, shutdown, adaptation, partial delivery, auth key, sender dry, stream reset, association reset, and stream change events, unified by `union sctp_notification`. Query/control structs cover RTO, association params, primary addresses, peer address params/info, authentication chunks/keys, SACK info, status, addresses, association stats, PR status/defaults, `sctp_info`, stream add/reset, event toggle, UDP encapsulation, scheduler type, and probe interval.

Control flow: applications configure an SCTP socket with setsockopt, send messages with SCTP cmsgs, receive data or `MSG_NOTIFICATION` events through recvmsg, query association and peer address state, and use internal socket options through lksctp helper library calls for bindx/connectx/peeloff/address enumeration.

State and persistence behavior: SCTP endpoint, association, stream, peer address, authentication key, scheduler, and statistics state lives in kernel SCTP sockets and associations. Many variable-length arrays are snapshot outputs. The header defines packed/aligned layouts for sockaddr_storage-containing structs to preserve ABI across architectures.

Dependencies and integration points: depends on Linux types and socket storage. It integrates with the SCTP protocol stack, libc/lksctp-tools, sendmsg/recvmsg cmsg handling, socket options, netlink-independent diagnostics, and applications using one-to-one or one-to-many SCTP sockets.

Risks and edge cases: ABI is large and historically compatible aliases/spellings must remain. Flexible arrays require length checks. Packed sockaddr_storage structs can expose alignment bugs. Notification subscription has legacy and per-event forms. PR policy bits share `sinfo_flags`, and internal options must not be confused with standardized options.

Test signals: lksctp functional tests for connectx/bindx/peeloff, cmsg send/receive, every notification type, auth key lifecycle, PR-SCTP TTL/RTX/PRIO, stream reset/add, UDP encapsulation, PLPMTUD probe interval, stats snapshots, packed struct size on 32/64-bit, and malformed option length rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sctp.h -->
