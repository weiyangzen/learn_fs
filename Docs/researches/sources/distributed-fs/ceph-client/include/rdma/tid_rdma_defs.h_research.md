# sources/distributed-fs/ceph-client/include/rdma/tid_rdma_defs.h

Purpose: Defines on-wire packet layouts and opcodes for Intel TID RDMA extensions carried under the InfiniBand opcode space.

Important APIs/types/functions: Packet structs cover TID RDMA read request/response, write request/response/data, resync, and ACK. Each includes KDETH words and fields such as RETH, AETH, TID flow PSN/QP, verbs PSN, and verbs QP. `IB_OPCODE_TID_RDMA` and enum entries create specific opcodes via `IB_OPCODE()`. `IB_WR_TID_RDMA_WRITE` and `IB_WR_TID_RDMA_READ` map to reserved verbs work request opcodes.

Control flow and state: This is a format contract. Drivers encode/decode TID flow and verbs flow state across request, response, data, resync, and ACK messages. The structs mix little-endian KDETH fields and big-endian IB fields, so callers must preserve byte ordering.

Dependencies and integration: Depends on `rdma/ib_pack.h`; used by hfi1/rdmavt style drivers implementing TID RDMA acceleration.

Risks and test signals: Risks include struct layout drift, endian mistakes, opcode collisions, and mismatched TID/verbs PSN tracking. Tests should include packet encode/decode golden vectors, sparse endian checking, write/read ACK sequencing, resync recovery, and interop with non-TID paths.
