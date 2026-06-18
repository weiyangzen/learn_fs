# sources/distributed-fs/ceph-client/include/linux/sunrpc/rpc_rdma.h

Purpose: defines common RPC-over-RDMA version-one wire constants, connection-private data, procedure/error values, and segment encode/decode helpers.

Important APIs and types: constants include `RPCRDMA_VERSION`, inline size defaults, header size limits, and max XDR quad sizes for fixed headers and chunks. `enum rpcrdma_errcode` and `enum rpcrdma_proc` define RDMA_ERROR causes and message procedures. Pre-XDR constants provide big-endian procedure/error values. `struct rpcrdma_connect_private` is the packed RDMA-CM private extension with magic, version, flags, and encoded send/recv sizes. Helpers encode/decode 1 KiB-based buffer sizes and XDR RDMA/read segments.

Control flow: connection setup exchanges private data; send/receive paths parse RDMA_MSG/NOMSG/MSGP/DONE/ERROR and encode or decode chunk segment descriptors with XDR helpers.

State and persistence: no state is stored; this is a wire ABI and helper header.

Dependencies and integration points: depends on integer and bit APIs and `xdr_encode_hyper()`/`xdr_decode_hyper()` from SUNRPC XDR. Shared by client and server RPC/RDMA.

Risks and test signals: risks include packed layout drift, endianness mistakes, unsupported chunk combinations, buffer-size encoding underflow, and version negotiation errors. Test with RPC/RDMA interoperability, RDMA-CM private data, malformed chunks, and big-endian/little-endian builds.
