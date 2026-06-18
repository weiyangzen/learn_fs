# sources/distributed-fs/ceph-client/include/linux/sunrpc/xdr.h

Purpose: declares the kernel SUNRPC XDR buffer model, stream encoder/decoder, common RPC pre-encoded constants, and helpers for scalar, opaque, string, array, page-backed, and scatter/gather XDR processing.

Important APIs and types: `XDR_UNIT` and `XDR_QUADLEN()` define 32-bit alignment. `struct xdr_netobj` represents counted opaque data. `struct xdr_buf` models head/tail kvecs plus page/bvec-backed payload with flags `XDRBUF_READ`, `XDRBUF_WRITE`, and `XDRBUF_SPARSE_PAGES`. Pre-XDR constants encode RPC auth/message/status values. `struct xdr_array2_desc` describes generic array encode/decode. `struct xdr_stream` tracks current pointer, buffer, end, iov, scratch buffer, page pointer/kaddr, remaining decode words, and request pointer. APIs reserve/commit/truncate/restrict streams, read/write pages, create subsegments, move/zero ranges, process buffers with scatterlists, encode/decode auth, strings, opaque values, booleans, u32/u64/be32, arrays, and optional item discriminators.

Control flow: callers initialize encode or decode streams over an `xdr_buf`, reserve contiguous space or inline-decode bytes, use scratch buffers when page-boundary data must be linearized, write/read page payloads, and return `-EMSGSIZE` or `-EBADMSG` on overflow.

State and persistence: XDR state is per-message runtime state in caller-provided buffers/pages. Duplicated netobjs allocate caller-owned memory.

Dependencies and integration points: depends on kvec/uio, byteorder, unaligned access, scatterlists, pages/folios, RPC message constants, and request objects. It is the shared wire-encoding layer for SUNRPC client, server, RDMA, NFS, and generated XDR code.

Risks and test signals: risks include alignment/padding mistakes, page boundary linearization bugs, buffer length under/over-accounting, max length validation after pointer exposure, sparse page handling, and endian mistakes. Test with XDR selftests, malformed/truncated RPCs, page-spanning opaque fields, large NFS READ/WRITE payloads, RDMA chunks, and big-endian builds.
