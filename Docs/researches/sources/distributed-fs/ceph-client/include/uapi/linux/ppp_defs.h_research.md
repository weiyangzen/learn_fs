<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ppp_defs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ppp_defs.h

Purpose: defines core PPP frame layout constants, protocol numbers, FCS helpers, packet statistics structs, idle-time structs, and network protocol mode enum values shared by PPP kernel and userspace.

Important APIs and types: constants include `PPP_HDRLEN`, `PPP_FCSLEN`, `PPP_MRU`, address/control bytes, protocol IDs such as `PPP_IP`, `PPP_IPV6`, `PPP_LCP`, `PPP_CCP`, and escape/control values. `struct pppstat`, `struct vjstat`, `struct ppp_stats`, `struct ppp_comp_stats`, and idle-time structs expose counters. `enum NPmode` controls pass/drop/error/queue behavior for protocols.

Control flow: PPP framing uses these constants to parse and emit frames, select protocol handlers, update stats, and negotiate modes. Userspace reads stats through ioctls and uses protocol constants in configuration.

State and persistence: PPP counters, VJ/compression stats, and idle timestamps are runtime link state. The header defines the serialized ABI, not storage.

Dependencies and integration points: depends on Linux types and integrates with PPP generic, pppd, compression modules, Van Jacobson TCP compression, and network protocol demultiplexing.

Risks and test signals: risks include protocol constant mismatch, FCS/stat struct compatibility, 32/64-bit time handling, and compression stats overflow. Test frame encode/decode, IPv4/IPv6 and control protocol demux, stats ioctls, idle counters, and pppd compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ppp_defs.h -->
