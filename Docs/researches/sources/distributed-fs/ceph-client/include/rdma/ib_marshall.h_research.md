# sources/distributed-fs/ceph-client/include/rdma/ib_marshall.h

Purpose: declares marshalling helpers that copy kernel RDMA objects into userspace ABI structures for uverbs and userspace SA consumers.

Important APIs and types: `ib_copy_qp_attr_to_user()` converts `struct ib_qp_attr` to `struct ib_uverbs_qp_attr`; `ib_copy_ah_attr_to_user()` converts `struct rdma_ah_attr` to `struct ib_uverbs_ah_attr`; `ib_copy_path_rec_to_user()` converts `struct sa_path_rec` to `struct ib_user_path_rec`.

Control flow: uverbs query paths and SA user responses call these helpers after obtaining kernel attributes, before copying ABI-formatted data to userspace. The helpers centralize transport-specific field mapping and byte-order/packing details.

State and persistence: no state is kept. Destination buffers are caller-owned and typically short-lived ABI responses.

Dependencies and integration points: depends on kernel verbs types, SA path records, and user ABI headers `ib_user_verbs.h` and `ib_user_sa.h`. It integrates RDMA core kernel state with stable userspace structure layouts.

Risks and test signals: risks include missing fields when kernel structs evolve, endian or width truncation, exposing uninitialized padding, and RoCE/OPA path fields not represented correctly in legacy user records. Test uverbs QP/AH query output, SA path query output, ABI padding initialization checks, cross-architecture 32/64-bit builds, and RoCE/IB/OPA conversion cases.
