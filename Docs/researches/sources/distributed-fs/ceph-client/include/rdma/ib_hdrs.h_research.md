# sources/distributed-fs/ceph-client/include/rdma/ib_hdrs.h

Purpose: defines packed InfiniBand packet header layouts and inline accessors for LRH, GRH/BTH/DETH, RDMA extended headers, atomics, AETH/NAK, congestion bits, and TID RDMA extensions.

Important APIs and types: constants define BTH flags, opcode masks, NAK values, GRH fields, FECN/BECN bits, AETH credit/NAK fields, and packet masks. `struct ib_reth`, `struct ib_atomic_eth`, `union ib_ehdrs`, `struct ib_other_headers`, and `struct ib_header` model packed wire headers, with unaligned 64-bit fields handled by `ib_u64_get()`/`ib_u64_put()` and specific RETH/atomic accessors. LRH helpers return LNH, SC, SL, DLID, SLID, and link version. UD helpers get QKey/SQPN. BTH helpers return pad, P_Key, opcode, ack request, migration request, solicited event, PSN, QPN, FECN/BECN, transport version, and migration/solicited booleans.

Control flow: low-level drivers and packet-processing paths cast packet bytes to these packed structs, use endian/unaligned helpers to inspect headers, and branch on opcode, QPN, PSN, ACK/NAK, path migration, and congestion bits. TID RDMA subheaders are available through the extended header union.

State and persistence: no state is stored; the header exposes wire-format interpretation of caller-owned packet buffers.

Dependencies and integration points: depends on Linux unaligned access helpers, endian conversion, `ib_verbs.h`, and `tid_rdma_defs.h`. It integrates HCA drivers, software RDMA transports, and packet analyzers with InfiniBand wire headers.

Risks and test signals: risks include packed layout drift, unaligned 64-bit access bugs, endian conversion mistakes, duplicate macro definitions, QPN/PSN mask errors, and trusting malformed packet lengths before accessing extended headers. Test with compile-time layout/offset checks, packet encode/decode vectors, ACK/NAK and congestion packets, TID RDMA packets, sanitizers for unaligned access, and fuzzed short packets in receive paths.
