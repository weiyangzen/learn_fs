# sources/distributed-fs/ceph-client/include/linux/sctp.h

Purpose: `sctp.h` defines in-kernel SCTP wire-format structures, chunk and parameter identifiers, error causes, and helper macros shared by the SCTP protocol implementation. It mirrors RFC-defined packet layouts for common headers, chunks, TLV parameters, PR-SCTP, ADD-IP, AUTH, stream reset, ndata, and UDP encapsulation support.

Important APIs/types/functions: Core types include `struct sctphdr`, `sctp_hdr()`, `struct sctp_chunkhdr`, `enum sctp_cid`, `struct sctp_paramhdr`, `enum sctp_param`, data chunk structs (`sctp_data_chunk`, `sctp_idata_chunk`), INIT/SACK/heartbeat/shutdown/error chunks, PR-SCTP forward-TSN structs, ADD-IP structs, AUTH structs, stream reset request/response structs, `struct sctp_infox`, and `struct sctp_new_encap_port_hdr`. Macros include chunk/parameter action masks, `sctp_test_T_bit()`, SCTP DATA flags, DSCP/flowlabel masks, `SCTP_PAD4()`, and `SCTP_TRUNC4()`.

Control flow: Receive paths cast skb transport headers and chunk bodies to these structures after length validation. Chunk type high bits determine how unknown chunks are handled: discard, discard with error, skip, or skip with error. Parameter high bits do the equivalent for unknown TLVs. Association setup consumes INIT/INIT-ACK parameters; SACK and FWD-TSN update reliability state; AUTH validates protected chunks; ASCONF and RECONF update addresses or streams.

State and persistence behavior: The header owns no runtime state. Its structures encode transient packet state that drives SCTP association state machines elsewhere. Some structures use flexible arrays for variable TLVs, so state ownership belongs to skb buffers and association objects.

Dependencies and integration points: It depends on IPv4/IPv6 address structs, skbuff transport header access, UAPI SCTP definitions, endian types, and SCTP association internals. It integrates with netfilter, socket options, LSM SCTP hooks, checksum handling, and transport address management.

Risks: Wire structs use mixed endianness and packed protocol lengths; missing `ntohs`/`hton` style conversion or insufficient length checks can cause protocol bugs or out-of-bounds reads. Flexible arrays require 4-byte padding via `SCTP_PAD4()`. Unknown action bits must be honored exactly for interoperability.

Test signals: Fuzz chunk and parameter lengths, unknown chunk/parameter actions, INIT/COOKIE/SACK association setup, PR-SCTP FWD-TSN, ndata I-DATA/I-FWD-TSN, AUTH unsupported HMAC error, ADD-IP ASCONF serial handling, stream reset responses, UDP encapsulation restart cause, and skb header offset assumptions.
