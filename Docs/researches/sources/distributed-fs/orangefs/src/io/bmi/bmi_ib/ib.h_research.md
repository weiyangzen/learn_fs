# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/ib.h

## Purpose
`ib.h` is the private contract shared by the BMI InfiniBand implementation files. It defines connection state, work queue state machines, wire message headers, memory registration cache metadata, buffer-list descriptors, the provider vtable, and internal helper prototypes.

## Important APIs, Types, and Functions
The central types are `ib_connection_t`, `struct buf_head`, `ib_method_addr_t`, `memcache_entry_t`, `ib_buflist_t`, `struct ib_work`, `struct bmi_ib_wc`, `struct ib_device_func`, and `ib_device_t`. `ib_connection_t` records the BMI peer map, eager buffers, free lists, cancellation/refcount/closed flags, credits, provider-private state, and `BMI_addr_t`. `struct ib_work` represents either a send or receive operation, with a `method_op` back pointer, buflist, eager buffer head, tag, state union, unexpected flag, RTS mop id, and actual receive length.

The send state enum `sq_state_t` covers buffer wait, eager send completion, RTS/CTS/RDMA/RTS_DONE phases, user-test completion, cancellation, and error. The receive state bitmask `rq_state_t` covers eager and RTS waits for user post, testunexpected, CTS buffer/send completion, RTS_DONE, incoming wait, cancellation, and error. `msg_type_t` defines the on-wire message kinds: eager, unexpected eager, RTS, CTS, RTS_DONE, CREDIT, and BYE.

Message header structs and `endecode_fields_*` macros define the encoded wire ABI for common headers, eager, RTS, CTS, and RTS_DONE messages. `struct ib_device_func` is the provider abstraction filled by OpenIB or VAPI.

## Control Flow
The header itself has no runtime control flow, but it determines the legal control flow in `ib.c`: BMI posts allocate `struct ib_work` items, provider CQ completions are normalized to `struct bmi_ib_wc`, common code dispatches by `msg_type_t`, and provider-specific functions are called through `ib_device_t.func`. The CTS header format also drives provider RDMA write loops by carrying remote buffer addresses, lengths, and keys after the fixed header.

## State and Persistence Behavior
All structures represent in-memory process state. No durable data is stored. `ib_device_t` is the global method/device singleton and carries connection/send/recv lists plus memory cache state. `memcache_entry_t.count` is the registration reference count. `ib_method_addr_t.ref_count` tracks BMI address references independently from live connection references.

## Dependencies and Integration Points
The header includes BMI type definitions, quicklist, gossip debugging, PVFS debug/types, and encode stubs. Its prototypes bind `util.c`, `mem.c`, `ib.c`, `openib.c`, and `vapi.c` together. The provider vtable is the main integration boundary between common BMI logic and low-level InfiniBand APIs.

## Risks and Edge Cases
The header encodes several ABI-sensitive assumptions: message headers must stay 64-bit aligned, state enum names are used for debug formatting, and the CTS variable payload layout must match the decoder and provider RDMA loops. `memkeys.mrh` stores either a pointer or provider handle in a `uint64_t`, so `ptr_from_int64` and `int64_from_ptr` must be valid on target architectures. The receive state enum is a bitmask while send state is not; mixing equality and bit tests incorrectly would break progression.

## Test Signals
Compile-time signals include successful builds with both `OPENIB` and `VAPI`, generated encode/decode functions for all message headers, and no struct size/alignment regressions. Runtime tests should validate all message type names, state name formatting, CTS variable-length layout, and pointer/handle round trips on 32-bit and 64-bit targets if those are supported.
