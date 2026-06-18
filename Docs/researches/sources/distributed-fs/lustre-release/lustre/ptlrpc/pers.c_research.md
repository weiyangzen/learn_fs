# sources/distributed-fs/lustre-release/lustre/ptlrpc/pers.c

Purpose: fills an LNet memory descriptor for one PTLRPC bulk descriptor segment, including empty descriptors used to send only an LNet header.

Important APIs/types/functions: `ptlrpc_fill_bulk_md(struct lnet_md *md, struct ptlrpc_bulk_desc *desc, int mdidx)` is the only function. It maps `ptlrpc_bulk_desc` fields `bd_md_max_brw`, `bd_md_count`, `bd_iov_count`, `bd_mds_off`, `bd_is_rdma`, `bd_enc_vec`, and `bd_vec` into `lnet_md` fields.

Control flow: assertions verify the descriptor index and I/O vector count. If `mdidx` is beyond `bd_md_count`, the function emits a zero-length KIOV descriptor. Otherwise it sets GPU address options for RDMA bulk, computes the vector start and length from `bd_mds_off`, marks the MD as KIOV-backed, and points at encrypted or plain vectors depending on `bd_enc_vec`.

State/persistence: mutates only the passed `lnet_md`; no retained state. The descriptor references existing bulk vectors and does not own their lifetime.

Dependencies/integration: integrates PTLRPC bulk transfer descriptors with LNet memory descriptor posting. It is used by bulk I/O paths that split large BRW vectors across multiple network descriptors.

Risks/test signals: off-by-one errors in `bd_mds_off` or `bd_md_count` would post wrong page ranges. Tests should cover first/middle/last segment length calculation, zero-length header-only descriptors, encrypted vector selection, RDMA GPU option propagation, and assertion coverage for invalid `mdidx` or excessive vector counts.
