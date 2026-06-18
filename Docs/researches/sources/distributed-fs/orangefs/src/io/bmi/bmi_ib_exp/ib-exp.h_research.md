# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/ib-exp.h

## Purpose
Provides the private shared contract for the experimental BMI InfiniBand method. It defines connection, buffer, work, memory-cache, wire-message, provider callback, and device-wide state types used by `ib-exp.c`, `mem-exp.c`, `util-exp.c`, `openib-exp.c`, and `vapi-exp.c`.

## Important APIs, Types, And Functions
Key constants are `DEFAULT_EAGER_BUF_NUM`, `DEFAULT_EAGER_BUF_SIZE`, `MEMCACHE_BOUNCEBUF`, `MEMCACHE_EARLY_REG`, and debug/assert helpers. Core types include `ib_connection_t`, `struct buf_head`, `ib_method_addr_t`, `sq_state_t`, `rq_state_t`, `msg_type_t`, `memcache_entry_t`, `ib_buflist_t`, `struct ib_work`, message headers (`msg_header_common_t`, `msg_header_eager_t`, `msg_header_rts_t`, `msg_header_cts_t`, `msg_header_rts_done_t`), `struct bmi_ib_wc`, `struct ib_device_func`, and `ib_device_t`. The header declares utility, memory-cache, and provider-facing helper functions.

## Control Flow
The enums define the transport's state-machine vocabulary. Send states move from waiting for an eager buffer through eager completion, RTS/CTS waiting, RDMA completion, RTS_DONE buffer/completion, user test, cancel, or error. Receive states are bit flags that represent waiting for user post, waiting for unexpected test, waiting for CTS buffer/send completion, waiting for RTS_DONE, user-testable completion, cancellation, and error. The message header definitions encode the eager and rendezvous wire protocol; `endecode_fields_*` declarations generate byte-order-aware encode/decode helpers used by both generic and provider-specific files.

## State And Persistence
The header owns no storage except conditional debug name arrays when `__util_exp_c` is defined. It defines the in-memory state that persists for the lifetime of the BMI module: global `ib_device`, per-connection eager buffers and credits, outstanding work queues, registered memory keys, and provider-private resources. Pointer/integer conversion macros preserve work request ids across 32-bit and 64-bit platforms.

## Dependencies And Integration Points
It includes BMI types, OrangeFS quicklist and gossip APIs, PVFS debug/types/encode stubs, and exposes the function-pointer ABI that OpenIB and VAPI providers must fill. `mem-exp.c` consumes `memcache_entry_t` and `ib_buflist_t`; `util-exp.c` relies on the conditional name arrays; `ib-exp.c` depends on all state and message definitions.

## Risks And Test Signals
ABI drift here affects every implementation file. The CTS layout uses a variable-length payload of remote addresses, lengths, and keys and must remain aligned with provider RDMA code. `rq_state_t` is bitmask-based while `rq_state_name()` performs exact-name lookup, so combined states may print as unknown. `MEMCACHE_EARLY_REG` is enabled and `MEMCACHE_BOUNCEBUF` disabled at compile time, leaving alternate branches stale. Test signals include compiling all provider combinations, encode/decode round trips for every message header, state transition logging sanity, and 32-bit pointer/id conversion coverage.
