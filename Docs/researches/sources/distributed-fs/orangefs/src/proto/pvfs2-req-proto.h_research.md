# sources/distributed-fs/orangefs/src/proto/pvfs2-req-proto.h

## Purpose
Defines the OrangeFS/PVFS2 server wire request protocol. The file assigns stable numeric server operation codes, protocol version numbers, request-size limits, per-operation request and response structures, encode/decode macros, extra-buffer sizing macros, and client-side fill macros for constructing `PVFS_server_req` messages. It is the central ABI contract shared by clients, servers, generated encoders, and server dispatch.

## Important APIs, Types, And Functions
The top-level protocol constants are `PVFS2_PROTO_MAJOR`, `PVFS2_PROTO_MINOR`, `PVFS2_PROTO_VERSION`, `PINT_SMALL_IO_MAXSIZE`, and many `PVFS_REQ_LIMIT_*` bounds for paths, layouts, key/value lists, handles, directory entries, security material, and management arrays. `enum PVFS_server_op` assigns operation numbers from `PVFS_SERV_CREATE` through `PVFS_SERV_MGMT_GET_USER_CERT_KEYREQ`; its order must match `PINT_server_req_table` in `pvfs2-server-req.c`.

The file declares per-op structs such as `PVFS_servreq_create`, `PVFS_servreq_io`, `PVFS_servreq_small_io`, `PVFS_servreq_mkdir`, `PVFS_servreq_tree_remove`, `PVFS_servreq_mgmt_split_dirent`, and matching `PVFS_servresp_*` payloads. Most are bound to generated-style `endecode_fields_*_struct` macros. Complex variable payloads, including mirror, normal I/O, small I/O, and certificate requests, provide explicit `encode_*` and `decode_*` macros under `__PINT_REQPROTO_ENCODE_FUNCS_C`. `PVFS_REQ_COPY_CAPABILITY` copies capabilities into outgoing requests, and `PINT_SERVREQ_*_FILL` macros initialize operation-specific request fields.

## Control Flow
This header does not run control flow itself; it defines how control moves over the network. A caller fills a `PVFS_server_req` by selecting an op code, copying a capability and hints, and assigning the union member matching the op. Encoding first emits the generic request header (`op`, padding, capability, hints), then the op-specific payload selected by `op`. Server-side decoding reconstructs the generic request and leaves dispatch to `pvfs2-server.c`/`pvfs2-server-req.c`.

For normal and small I/O, decode macros also unpack nested `PINT_Request` structures so later state machines can traverse the file-request tree. Small-write request decoding points `buffer` directly into the decoded message body instead of copying it, so state-machine lifetime must keep the decoded buffer alive. Management, tree, directory, key/value, and security requests all follow the same pattern: bounded variable-length arrays are represented by pointer/count pairs and sized by companion `extra_size_*` macros.

## State And Persistence
No persistent state is stored in this header. Its persistent effect is protocol compatibility: op values, struct fields, field order, alignment skips, extra-size bounds, and protocol version numbers become durable wire-format commitments. The generic `PVFS_server_req` and `PVFS_server_resp` unions define the in-memory decoded state carried by server operation state machines.

## Dependencies And Integration Points
The header integrates with `pvfs2-types.h`, `pvfs2-attr.h`, `pint-distribution.h`, `pvfs2-request.h`, `pint-request.h`, `pvfs2-mgmt.h`, `pint-hint.h`, UID/security headers, and the generated encoding system. Server dispatch in `pvfs2-server-req.c` must stay synchronized with `enum PVFS_server_op`. State machines and client system-interface code depend on the fill macros and specific union member names.

## Risks And Test Signals
The largest risk is ABI drift: changing an op number, field order, size limit, or encode/decode behavior without a coordinated protocol version bump can break mixed client/server deployments. Several fill macros mutate or copy caller-provided attribute structures, so callers must understand ownership and side effects. The small I/O decode path depends on decoded-message lifetime and correct `total_bytes` validation. The macro `PVFS_REQ_LIMIT_DFILE_COUNT_IS_VALID` rejects exactly `PVFS_REQ_LIMIT_DFILE_COUNT`, which is intentional only if the maximum is exclusive. Test signals include request encode/decode round trips for every op, mixed-endian key/value and ACL payloads, max-size boundary tests for variable arrays, small I/O read/write payload lifetime tests, and build checks that `PVFS_SERV_NUM_OPS` still matches the request table.
