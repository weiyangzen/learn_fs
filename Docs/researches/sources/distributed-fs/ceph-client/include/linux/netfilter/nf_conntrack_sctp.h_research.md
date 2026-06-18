# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_sctp.h

Purpose: Defines SCTP-specific conntrack state storage for SCTP association verification tags.

Important APIs, types, and functions: Exports `struct ip_ct_sctp` and includes the UAPI SCTP conntrack state definitions. Detected source surface: 17 lines; includes `uapi/linux/netfilter/nf_conntrack_sctp.h`; macros `_NF_CONNTRACK_SCTP_H`; structs `ip_ct_sctp`; enums `sctp_conntrack`; typedefs none; function-like declarations/helpers none.

Control flow: The SCTP conntrack implementation uses this header to store original/reply verification tags and the protocol state while packets advance association state.

State and persistence behavior: State is per conntrack entry and persists for the lifetime of the association in the conntrack table.

Dependencies and integration points: Integrates with `uapi/linux/netfilter/nf_conntrack_sctp.h`, conntrack protocol dispatch, and SCTP packet parsing code.

Risks and test signals: Risks are accepting packets with wrong verification tags or mishandling multihoming paths. Test INIT/COOKIE paths, shutdown, abort, and tag mismatch cases.
