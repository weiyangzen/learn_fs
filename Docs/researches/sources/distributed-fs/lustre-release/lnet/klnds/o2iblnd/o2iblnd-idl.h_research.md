<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd-idl.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd-idl.h

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd-idl.h_research.md`.

Purpose: defines the o2iblnd InfiniBand wire protocol message layouts, magic/version constants, message type IDs, connection parameters, RDMA descriptors, completions, and rejection reasons.

Important APIs/types/functions: packed structs `kib_connparams`, `kib_immediate_msg`, `kib_rdma_frag`, `kib_rdma_desc`, `kib_putreq_msg`, `kib_putack_msg`, `kib_get_msg`, `kib_completion_msg`, `kib_msg`, and `kib_rej`. Constants include `IBLND_MSG_MAGIC`, protocol versions 1/2, message types `CONNREQ`, `CONNACK`, `NOOP`, `IMMEDIATE`, `PUT_REQ/NAK/ACK/DONE`, `GET_REQ/DONE`, and reject reasons for races, resources, fatal errors, incompatibility, stale peers, RDMA-frag mismatch, queue-size mismatch, invalid service ID, and early NI state.

Control flow: not executable; send/receive code packs these structures into sender byte order and receivers must flip as needed. `kib_msg` has a fixed leading magic/version pair, common routing/checksum/NID/stamp header, and a union payload selected by `ibm_type`.

State and persistence behavior: wire structs carry transient protocol state: connection queue depth/frags/message size, LNet headers, RDMA keys/fragments, completion cookies/status, source/destination incarnations, and rejection metadata. No kernel memory state is stored here.

Dependencies and integration: includes UAPI LNet IDL for `lnet_hdr_nid4` and `LNET_PROTO_IB_MAGIC`. Used by both external and generated in-kernel o2iblnd builds.

Risks: all structures are `__packed`, and comments note misaligned `u64` RDMA fragment addresses; direct dereference/alignment assumptions are unsafe. Wire compatibility requires preserving first fields and version/type values. Extending variable-length payloads/descriptors must keep `ibm_nob` and checksum logic synchronized.

Test signals: interop between protocol version 1 and 2 peers, endian-swap tests, packed layout/sizeof assertions, immediate payload bounds, RDMA fragment count/key handling, completion status propagation, and each rejection reason during connection setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd-idl.h -->
