# sources/distributed-fs/orangefs/src/io/bmi/bmi_rdma/rdma.h

## Purpose
`rdma.h` is the private shared header for the OrangeFS BMI RDMA implementation. It defines the central connection, work-item, memory-cache, wire-protocol, and device-state data structures used by `rdma.c`, `util.c`, and the RDMA memory-cache implementation. It also declares internal helper APIs and wraps common debugging, assertion, pointer conversion, and compiler-attribute helpers.

## Important APIs, Types, and Definitions
The header sets default eager-buffer sizing with `DEFAULT_EAGER_BUF_NUM` and `DEFAULT_EAGER_BUF_SIZE`. The default is 20 buffers of 16 KiB per connection; the actual eager payload is reduced by the eager header size in `rdma.c`.

`rdma_connection_t` represents one peer connection. It links into the global device connection list, stores the peer BMI method address and `rdma_conn_info`, owns contiguous eager send/receive buffers plus corresponding free lists and `buf_head` arrays, tracks cancellation/refcount/closed state, tracks send and return credits, stores RDMA CM id/QP/MRs, and caches the BMI address registered with the BMI layer.

`struct buf_head` is the per-eager-buffer descriptor. It links into free lists, records an ordinal, owning connection, associated send or receive work item, and the backing buffer pointer. Completions use the buffer-head pointer as a work request id.

`rdma_method_addr_t` is the RDMA-specific `method_data` stored in a BMI method address. It stores hostname, port, current connection pointer, reconnect policy, and a reference count used by `BMI_DROP_ADDR`.

The send state machine is `sq_state_t`: waiting for eager buffer, waiting for eager send completion, waiting for RTS send completion, waiting for CTS, waiting for RDMA data send completion, waiting for RTS_DONE buffer/send completion, waiting for user test, cancelled, and error. The receive state machine is `rq_state_t`, a bitmask covering eager/RTS waiting-for-user-post states, waiting-for-test states, CTS-send and RTS_DONE states, waiting for incoming data, cancelled, and error. `msg_type_t` defines the on-wire message set: eager send, eager unexpected, RTS, CTS, RTS_DONE, CREDIT, and BYE.

When included by `util.c` with `__util_c` defined, the header also instantiates `name_t` arrays mapping send states, receive states, and message types to strings. Other files get only the state enums and function declarations.

`memcache_entry_t` describes one registered or registerable memory range, including list linkage, buffer pointer, length, reference count, and RDMA memory keys (`mrh`, `lkey`, `rkey`). `rdma_buflist_t` wraps a send or receive scatter/gather list, total length, and a parallel array of memory-cache entries.

`struct rdma_work` is the shared outstanding operation record for both sends and receives. It contains BMI type, owning `method_op`, connection, buflist, inline single-buffer storage, current eager buffer head, BMI tag, send/receive state union, unexpected flag, RTS mop id, and actual receive length.

The wire headers are `msg_header_common_t`, `msg_header_eager_t`, `msg_header_rts_t`, `msg_header_cts_t`, and `msg_header_rts_done_t`. Each is paired with `endecode_fields_*` declarations so the normal OrangeFS little-endian field encoder can serialize and deserialize messages. `MSG_HEADER_CTS_BUFLIST_ENTRY_SIZE` documents the per-receive-buffer variable CTS payload layout: address, length, and rkey.

`struct bmi_rdma_wc` normalizes verbs completions into a local form with id, status, byte length, and opcode (`BMI_RDMA_OP_SEND`, `BMI_RDMA_OP_RECV`, `BMI_RDMA_OP_RDMA_WRITE`). `rdma_device_t` owns global method state: listener id/address, connection/send/recv lists, memcache handle, eager sizing, verbs context/CQ/PD/completion channel, NIC capabilities, SG scratch array, and unsignaled-send counters.

The header declares utility functions from `util.c`, memory-cache functions from `mem.c`, the global `rdma_device`, pointer/integer conversion macros, `qlist_upcast`, branch-prediction macros, `debug`, and `bmi_rdma_assert`.

## Control Flow and Integration
`rdma.h` does not execute code, but it defines the control contracts used by the rest of the RDMA method. `rdma.c` moves `struct rdma_work` instances through the `sq_state_t` and `rq_state_t` states while processing BMI posts, RDMA completions, and user tests. It fills and decodes the message headers defined here for every eager, RTS/CTS, credit, and shutdown control message.

The endecode declarations integrate with `pvfs2-encode-stubs.h` and require `rdma.c` to define `__PINT_REQPROTO_ENCODE_FUNCS_C` before including protocol headers so encoder definitions are available. The named-state arrays are intentionally emitted only in `util.c` to avoid multiple definitions while still keeping enum-to-string data close to the enum declarations.

The memory-cache declarations are consumed by both the BMI method and the cache implementation. `rdma.c` supplies registration callbacks that fill `memcache_entry_t.memkeys`; `mem.c` is expected to manage allocation, caching, registration reference counts, preregistration, deregistration, and cache flushing.

## State and Persistence Behavior
All types represent process-local volatile state. Nothing in this header implies durable persistence. The strongest ownership relationships are: `rdma_device_t` owns global lists and verbs resources; each `rdma_connection_t` owns per-peer eager memory and queue-pair resources; each `struct rdma_work` owns one outstanding BMI operation's protocol state; `memcache_entry_t` owns or references one registered memory range.

The receive state enum is a bitmask, not a simple sequential enum. Code can set multiple receive bits simultaneously, for example waiting for RTS_DONE, CTS send completion, and user test. The send state enum is a single-state progression. This difference is central to interpreting state checks in `rdma.c`.

## Dependencies
The header depends on OrangeFS BMI types, quicklist, gossip logging, debug definitions, encode stubs, PVFS types, and RDMA CM. It also assumes libibverbs types through RDMA CM and through users that include verbs before or after the header. The debug macro depends on `GOSSIP_BMI_DEBUG_IB`.

## Risks and Edge Cases
The include guard and helper macros use double-underscore identifiers such as `__rdma_h`, `__hidden`, and `__unused`, which are reserved by C implementations. Existing project style may tolerate this, but it is not portable C hygiene.

The state-name arrays are `static` definitions conditional on `__util_c`; this works for one translation unit but is brittle if another source defines `__util_c` accidentally. `entry` is also a generic macro name, though it is undefined after use.

`ptr_from_int64` and `int64_from_ptr` cast through `unsigned long`. Comments acknowledge truncation behavior on 32-bit architectures. The code assumes work request ids and stored MR handles can round-trip through this representation; 32-bit support should be treated cautiously.

The CTS wire layout exposes raw remote addresses and rkeys. The header documents the layout but not any authentication or bounds protection. Correctness depends on RDMA RC connection trust and higher-level configuration.

`bmi_rdma_assert` logs through `error` but does not abort. In debug builds, failed assertions may leave execution continuing in a corrupt state.

## Test Signals
Compile tests should include `rdma.h` in more than one translation unit to catch accidental multiple-definition or macro exposure problems. State-name tests can verify every enum value maps to a non-unknown string in `util.c`. Protocol encoding tests should round-trip every wire header and verify CTS variable payload offsets match `MSG_HEADER_CTS_BUFLIST_ENTRY_SIZE`.

Static analysis should focus on pointer/work-request-id casts, reserved macro names, and bitmask use of `rq_state_t`. Integration tests need to confirm the constants and state definitions match the behavior expected by `rdma.c` and `mem.c`.
