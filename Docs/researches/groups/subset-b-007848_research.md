# Group Research: subset-b-007848

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/ib.c -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/ib.c

## Purpose
`ib.c` is the provider-neutral core of OrangeFS/PVFS2's BMI InfiniBand method. It exposes the `bmi_ib_ops` method table to BMI, owns global method state, manages TCP-assisted connection setup, and drives the send/receive state machines used by both OpenIB and VAPI backends. It implements eager messages for small payloads and a rendezvous RTS/CTS/RDMA-write protocol for large payloads.

## Important APIs, Types, and Functions
The public integration point is `const struct bmi_method_ops bmi_ib_ops`, whose entries map BMI operations to static functions such as `BMI_ib_initialize`, `BMI_ib_finalize`, `BMI_ib_post_send`, `BMI_ib_post_recv`, `BMI_ib_test`, `BMI_ib_testsome`, `BMI_ib_testcontext`, `BMI_ib_testunexpected`, `BMI_ib_cancel`, and `BMI_ib_method_addr_lookup`.

Provider operations are accessed through `ib_device->func` macros such as `new_connection`, `post_sr`, `post_sr_rdmaw`, `check_cq`, `mem_register`, and `check_async_events`. This keeps common BMI behavior in this file while delegating verbs/VAPI-specific work to `openib.c` or `vapi.c`.

Core helpers include `ib_check_cq`, `encourage_send_waiting_buffer`, `encourage_send_incoming_cts`, `encourage_recv_incoming`, `send_cts`, `encourage_rts_done_waiting_buffer`, `post_send`, `post_recv`, `test_sq`, `test_rq`, `ib_new_connection`, `ib_close_connection`, `ib_tcp_client_connect`, `ib_tcp_server_init_listen_socket`, `ib_tcp_server_accept_thread`, and `ib_block_for_activity`.

## Control Flow
Initialization allocates the global `ib_device`, chooses OpenIB first and VAPI second at compile/runtime depending on macros, initializes the memory cache, and optionally starts a TCP listen socket plus accept thread for server mode. Client-side connections are established lazily by `ensure_connected` when a send or receive is posted.

Posting a send allocates an `ib_work` send queue item and `method_op`, validates the buffer list total, assigns an id through `id_gen_fast_register`, queues it on `ib_device->sendq`, and calls `encourage_send_waiting_buffer`. If the payload fits `eager_buf_payload`, the code encodes `MSG_EAGER_SEND` or `MSG_EAGER_SENDUNEXPECTED`, copies data into an eager send buffer, and posts a provider SEND. Larger sends encode `MSG_RTS`, optionally early-register user buffers, then wait for `MSG_CTS`; after CTS, the provider posts one or more RDMA writes and this file sends `MSG_RTS_DONE`.

Posting a receive either matches an already-arrived eager/RTS receive item or allocates a waiting receive queue item. Eager data is copied from the held eager receive buffer into the user's buflist. RTS data triggers `send_cts`, which registers the receive buflist and sends remote addresses, lengths, and rkeys to the sender. Completion testing polls the CQ, advances all eligible state machines, and reaps completed items only when the matching BMI context or op id asks for them.

Unexpected traffic is handled by `BMI_ib_testunexpected`, which finds `RQ_EAGER_WAITING_USER_TESTUNEXPECTED`, copies the data into a newly allocated buffer returned to BMI, reposts the eager receive buffer, and removes the internal receive item.

## State and Persistence Behavior
The file maintains process-local state only: `ib_device`, send/receive queues, connection list, memory cache pointer, TCP listen state, and accept thread flags. Per-connection state includes eager send/receive buffer pools, credits, refcounts, and `remote_map` links. There is no durable persistence. Operation lifetime is guarded by BMI op ids and `ib_connection_t.refcnt`; connection close is deferred until all queue entries referencing the connection are reaped.

The credit protocol uses `send_credit` to bound posted sends to peer receive buffers and `return_credit` to piggyback replenishment on outgoing message headers. `post_rr` increments returned credit and can send an explicit `MSG_CREDIT` when credits accumulate.

## Dependencies and Integration Points
This file depends on BMI method support, BMI method callbacks, the id generator, quicklists, PVFS locks, pthreads, TCP sockets, `pint-hint.h`, bytefield encode/decode stubs, and provider vtables defined in `ib.h`. It registers accepted server-side addresses through `bmi_method_addr_reg_callback` and parses BMI addresses of the form `ib://hostname:port/filesystem`.

It integrates tightly with `mem.c` for registration caching, `util.c` for logging/list/copy helpers, and `openib.c`/`vapi.c` for QP, CQ, memory registration, and provider-specific event handling.

## Risks and Edge Cases
The implementation is highly stateful and uses a single global mutex around most BMI entry points; provider callback threads and accept threads make lock ordering important. Many `error()` calls only log and do not abort, so callers may continue after serious invariants fail unless the local code returns immediately. Cancellation drains the QP and marks in-flight operations cancelled, but correctness depends on matching all memory registration states for early registration and RDMA completion. `BMI_ib_test` assumes `id_gen_fast_lookup` succeeds and does not visibly guard against invalid ids. Address lookup increments `ref_count`, while `BMI_DROP_ADDR` frees only when the count reaches zero; remote maps attached to live connections are intentionally retained for process lifetime.

The TCP handshake is used only for connection bootstrap; peer identity and network byte order parsing must remain consistent with both provider backends. `ib_block_for_activity` polls provider CQ and async fds but no longer polls the TCP listen socket directly because accept is handled by a separate thread.

## Test Signals
Useful tests would exercise eager expected send/recv, eager unexpected send/testunexpected, large RTS/CTS/RDMA transfers with single and list buffers, cancellation during each send/recv state, connection close by `MSG_BYE`, credit exhaustion/refill, failed TCP connect, invalid BMI address parsing, server accept/finalize thread shutdown, and both OpenIB and VAPI provider selection paths. Runtime validation should inspect debug logs for state transitions and verify no memory registrations remain after finalize.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/ib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/ib.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/ib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/mem.c -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/mem.c

## Purpose
`mem.c` implements the memory allocation and memory registration cache used by the BMI InfiniBand method. Its goal is to reduce expensive HCA memory registration churn for large BMI buffers and to recycle large buffers allocated through BMI memory APIs.

## Important APIs, Types, and Functions
The private `memcache_device_t` stores active registered entries, a free-chunk list for reusable large allocations, a mutex, and provider callbacks for registering and deregistering memory. Static helpers include `memcache_add`, `memcache_del`, `memcache_lookup_cover`, and `memcache_lookup_exact`.

Exported internal functions declared in `ib.h` are `memcache_memalloc`, `memcache_memfree`, `memcache_register`, `memcache_preregister`, `memcache_deregister`, `memcache_init`, `memcache_shutdown`, and `memcache_cache_flush`.

## Control Flow
`memcache_init` builds the cache object and records provider callbacks. `memcache_memalloc` first tries to recycle a large free chunk of the exact requested length when the allocation exceeds the eager limit. If none exists, it calls `malloc`; large new buffers are immediately added to the active cache and registered through the provider callback. `memcache_memfree` finds an exact active cache entry, requires its reference count to be one, deregisters it when the count reaches zero, and moves it to `free_chunk_list` instead of freeing it. Non-cached or eager-sized allocations are freed normally.

`memcache_register` is used by send/receive paths for user-provided buflists. It allocates the buflist's `memcache` pointer array, then for each range finds an existing covering registration or creates/registers a new one. `memcache_deregister` decrements each referenced entry and deregisters when the count reaches zero, then frees the buflist's pointer array. `memcache_cache_flush` removes zero-refcount cached entries and is used by OpenIB when registration fails with `ENOMEM`.

## State and Persistence Behavior
State is process-local and protected by `memcache_device_t.mutex`. Active registrations live in `list`; reusable BMI-allocated chunks live in `free_chunk_list`. Registration reference counts allow overlapping or repeated buffer use without immediate deregistration. Free-list entries retain allocated memory and may retain metadata until shutdown or flush.

## Dependencies and Integration Points
This file depends on PVFS locks, quicklist through `ib.h`, and provider-specific `mem_register`/`mem_deregister` callbacks supplied by `openib.c` or `vapi.c`. `ib.c` calls it for BMI memory allocation APIs, RTS/CTS buffer registration, early registration, cancellation cleanup, and finalize cleanup.

## Risks and Edge Cases
The cache uses linear list scans and comments note that an rbtree or dreg-style consistency checking would be better. User buffers can be freed or reused outside this cache, and the code does not validate that an old covering registration still maps valid application memory. `memcache_preregister` immediately returns and therefore disables optimistic preregistration despite `BMI_OPTIMISTIC_BUFFER_REG` calling it. Several paths call `error()` rather than returning detailed errors, so a failed partial registration can leave callers with limited recovery information. `memcache_register` allocates `buflist->memcache` before registering entries; if a later entry fails, cleanup responsibility is not clearly propagated to callers.

## Test Signals
Useful tests include repeated large `BMI_memalloc`/`BMI_memfree` reuse, exact free validation, overlapping buflist registration hits, registration miss and deregistration reference count behavior, provider registration failure with cache flush, shutdown with active and free-list entries, and confirmation that `BMI_OPTIMISTIC_BUFFER_REG` currently has no preregistration effect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/module.mk.in -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/module.mk.in

## Purpose
`module.mk.in` is the build-system fragment for the BMI InfiniBand method. It conditionally contributes source files and compiler flags to the OrangeFS build when configure enables legacy VAPI and/or OpenIB support.

## Important APIs, Types, and Functions
This file defines Make variables rather than C APIs. `DIR` points at `src/io/bmi/bmi_ib`. `cfiles` always starts with `ib.c util.c mem.c` when either IB backend is enabled. `BUILD_IB` adds `vapi.c` and `-DVAPI`; `BUILD_OPENIB` adds `openib.c` and `-DOPENIB`. The computed `src` list is appended to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC`.

Backend include flags are assigned with `MODCFLAGS_$(DIR)/vapi.c := -I@IB_INCDIR@` and `MODCFLAGS_$(DIR)/openib.c := -I@OPENIB_INCDIR@`. `MODCFLAGS_$(DIR)/ib.c := $(apis)` passes the selected provider macros to the common implementation.

## Control Flow
The outer `ifneq (,$(BUILD_IB)$(BUILD_OPENIB))` prevents any BMI IB files from entering the build unless at least one backend is configured. Within that block, provider-specific conditionals extend the source list and macro list. The top-level make system consumes the accumulated source and per-file CFLAGS variables.

## State and Persistence Behavior
There is no runtime state. The fragment persists configure-time decisions into generated make variables. Build artifacts depend on whether `BUILD_IB`, `BUILD_OPENIB`, `IB_INCDIR`, and `OPENIB_INCDIR` were substituted or set by configure.

## Dependencies and Integration Points
The fragment integrates the `bmi_ib` directory with the repository's top-level build variables. It assumes configure has discovered the proper include directories and that the C sources use `VAPI` and `OPENIB` macros to expose provider initialization functions to `ib.c`.

## Risks and Edge Cases
If both providers are enabled, both backend source files are built and `ib.c` tries OpenIB before VAPI. If include directory substitutions are wrong, backend files fail to compile even though the common files may compile. If neither provider is enabled, no common BMI IB code is built. The file does not add provider libraries itself, so link flags must be supplied elsewhere in the build system.

## Test Signals
Build tests should cover OpenIB-only, VAPI-only, both-provider, and no-provider configurations. The resulting compile commands should show `-DOPENIB` and/or `-DVAPI` only for `ib.c`, and backend-specific include paths only for their respective source files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/openib.c -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/openib.c

## Purpose
`openib.c` implements the `ib_device_func` provider backend for the Linux libibverbs/OpenIB stack. It opens an active HCA port, creates device-wide protection domain/completion queue/channel state, creates per-connection RC queue pairs, normalizes work completions for `ib.c`, and registers memory for eager and RDMA paths.

## Important APIs, Types, and Functions
Provider-private state is split between `struct openib_device_priv` and `struct openib_connection_priv`. The device struct holds `ibv_context`, `ibv_cq`, `ibv_pd`, port number, LID or GID, completion channel, hardware limits, temporary SGE array, unsignaled-send counters, and transport type (`IB` or `ROCE`). The connection struct holds an `ibv_qp`, eager send/recv MRs, remote LID/GID, and remote QP number.

Key functions are `openib_ib_initialize`, `openib_ib_finalize`, `openib_new_connection`, `init_connection_modify_qp`, `openib_post_sr`, `openib_post_rr`, `openib_post_sr_rdmaw`, `openib_check_cq`, `openib_prepare_cq_block`, `openib_ack_cq_completion_event`, `openib_mem_register`, `openib_mem_deregister`, `openib_check_async_events`, `return_active_nic_handle`, and `parse_bmi_opts_get_ib_port`.

## Control Flow
Initialization parses `ib_port`, selects an active device/port, determines whether the link layer is InfiniBand or Ethernet/RoCE, queries device limits, installs the provider vtable into `ib_device->func`, allocates a protection domain, creates a completion channel and CQ, and makes the async and completion fds nonblocking.

New connection setup registers the common eager buffers as MRs, creates a reliable-connected QP attached to the single CQ, records SGE and send-WR limits, exchanges local LID/GID and QP number over the TCP bootstrap socket, transitions the QP through INIT, RTR, and RTS, posts all eager receive buffers, then performs a final TCP sync so both sides have receives posted.

`openib_post_sr` posts eager/control SEND work requests. `openib_post_rr` reposts eager receive buffers. `openib_post_sr_rdmaw` consumes the sender buflist and the receiver CTS address/length/rkey array, creating as many RDMA write work requests as necessary; only the final segment is signaled with the `struct ib_work` id so common code can deregister memory and send RTS_DONE. `openib_check_cq` maps `ibv_wc` opcodes into the generic `bmi_ib_wc` consumed by `ib.c`.

## State and Persistence Behavior
All state is in memory. Device-wide resources live until `openib_ib_finalize`; per-connection QPs and eager MRs live until `openib_close_connection`. Registered user memory handles are stored in `memcache_entry_t.memkeys`. CQ and async events are edge notifications integrated with `ib_block_for_activity`.

## Dependencies and Integration Points
The file depends on `<infiniband/verbs.h>`, BMI byte swapping helpers, PVFS debug formatting, and common helpers from `ib.h`/`util.c`. It is selected by `module.mk.in` when `BUILD_OPENIB` defines `OPENIB`; `ib.c` calls `openib_ib_initialize` first when available.

## Risks and Edge Cases
The code contains compatibility branches for older `ibv_get_devices` APIs and newer device-list APIs; some identifiers in the older branch appear stale compared with the current struct names, so that path requires build coverage. The unsignaled-send counter in `openib_post_sr` is effectively unused because SENDs are always posted signaled. Many provider errors log and return without fully unwinding partially allocated connection resources. RDMA write segmentation must stay consistent with `ib.h` CTS layout and with memory registration refcounts. RoCE path assumes GID index zero. `return_active_nic_handle` returns early on some per-device failures without freeing the device list.

## Test Signals
Tests should cover active-port selection, `ib_port` option parsing, InfiniBand LID and RoCE GID handshakes, QP transition failures, eager send/receive, large list-buffer RDMA writes with more SGEs than a single WR can hold, CQ opcode/status translation, async event polling, registration failure with cache flush, and clean finalize after multiple connections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/openib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/util.c -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/util.c

## Purpose
`util.c` provides shared support routines for the BMI InfiniBand implementation: logging wrappers, allocation checks, quicklist helpers, debug name lookups, buflist copy helpers, and full-length socket read/write loops used during TCP bootstrap handshakes.

## Important APIs, Types, and Functions
Logging helpers are `error`, `error_errno`, `error_xerrno`, `warning`, `warning_errno`, and `warning_xerrno`. Allocation and list helpers are `bmi_ib_malloc`, `qlist_del_head`, and `qlist_try_del_head`. Debug lookup helpers are `sq_state_name`, `rq_state_name`, and `msg_type_name`, backed by arrays materialized from `ib.h` when `__util_c` is defined. Data movement helpers are `memcpy_to_buflist` and `memcpy_from_buflist`. Socket helpers are `read_full` and `write_full`.

## Control Flow
The logging functions format messages into a fixed stack buffer and send them to the gossip logging system; `error` also emits a backtrace but does not exit. `bmi_ib_malloc` rejects zero-byte allocations and logs allocation failures. The qlist helpers remove the first list item, either logging on empty (`qlist_del_head`) or returning null (`qlist_try_del_head`).

`memcpy_to_buflist` copies a bounded contiguous source into a receive buflist, stopping when the requested length has been copied. `memcpy_from_buflist` flattens all send buflist entries into a contiguous destination. `read_full` and `write_full` loop until the requested byte count is consumed, an error occurs, or read returns EOF.

## State and Persistence Behavior
The file maintains no persistent state of its own. It reads static name arrays emitted through `ib.h` and operates on caller-owned buffers, lists, and file descriptors.

## Dependencies and Integration Points
`ib.c`, `openib.c`, `vapi.c`, and `mem.c` all rely on these helpers. The socket full-read/full-write routines are part of the TCP exchange protocol used by both provider backends to trade QP connection data. The debug name functions are used throughout queue state logging.

## Risks and Edge Cases
The logging functions use `vsprintf` into 2048-byte buffers, so long formatted messages can overflow. `error()` no longer exits, which makes it important that callers return or otherwise recover after invariant failures. `read_full` and `write_full` do not retry on `EINTR` internally; callers must handle negative returns if interruption matters. `write_full` stores `num` in an `int total`, which can truncate very large sizes, though current handshake writes are small.

## Test Signals
Unit tests can validate state/message name mapping, list removal on empty and non-empty lists, buflist copy behavior with partial final buffers, and full read/write behavior over pipes or socketpairs including EOF and interrupted system calls. Static analysis should flag unbounded formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/vapi.c -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/vapi.c

## Purpose
`vapi.c` implements the legacy Mellanox VAPI/EVAPI backend for the BMI InfiniBand method. It provides the same provider vtable as `openib.c`, but through VAPI types and calls, including HCA discovery, PD/CQ/QP setup, memory registration, CQ event bridging, async-event reporting, and RDMA write posting.

## Important APIs, Types, and Functions
Provider state is stored in `struct vapi_device_priv` and `struct vapi_connection_priv`. The device struct holds HCA handle, CQ, PD, local LID, temporary SGE array, max outstanding WRs, async and completion event handler handles, and pipes used to expose events to `poll`. The connection struct holds QP handle/number, eager MRs and lkeys, unsignaled WR counter, remote LID, and remote QP number.

Key functions are `vapi_ib_initialize`, `vapi_ib_finalize`, `vapi_new_connection`, `verify_prop_caps`, `init_connection_modify_qp`, `vapi_drain_qp`, `vapi_close_connection`, `vapi_post_sr`, `vapi_post_rr`, `vapi_post_sr_rdmaw`, `vapi_check_cq`, `vapi_prepare_cq_block`, `vapi_ack_cq_completion_event`, `vapi_wc_status_to_bmi`, `vapi_mem_register`, `vapi_mem_deregister`, `reinit_mosal`, `async_event_handler`, and `cq_event_handler`.

## Control Flow
Initialization first calls `reinit_mosal` to work around old MOSAL library state after daemon forks. It lists HCAs, selects the first, allocates provider-private state, installs the vtable, obtains an HCA handle, registers async handlers, validates the port is active, allocates a PD, queries HCA capacity, creates a CQ, creates pipes for completion and async events, registers a completion event handler, and initializes SGE limits.

New connections register eager buffers, create an RC QP, verify returned QP capabilities, exchange local LID/QP number over the TCP bootstrap socket, transition the QP through INIT, RTR, and RTS, post all eager receive buffers, and perform a final synchronization exchange. SEND and receive posting functions translate common `buf_head` values into VAPI descriptors. RDMA writes are segmented using CTS remote buffer metadata exactly like OpenIB, with the final RDMA write signaled so `ib.c` can observe completion.

VAPI completion and async callbacks run in provider-created threads and write small records into pipes; common blocking code polls the read side through `vapi_prepare_cq_block`.

## State and Persistence Behavior
All state is runtime-only. Event pipes queue readiness notifications in process memory/kernel pipe buffers. Device resources are released in `vapi_ib_finalize`, while connection resources are released in `vapi_close_connection`. Registered memory handles are stored in `memcache_entry_t.memkeys`.

## Dependencies and Integration Points
This file depends on VAPI/EVAPI headers, optional `wrap_common.h`, `libmosal.so` dynamic symbols, BMI byte swapping, BMI method support, and the common BMI IB header. It is compiled when `BUILD_IB` defines `VAPI`; `ib.c` falls back to `vapi_ib_initialize` if OpenIB initialization is unavailable or fails.

## Risks and Edge Cases
VAPI support is legacy and contains hard exits through `error_verrno`, unlike the nonfatal `error()` helper. `reinit_mosal` uses `dlopen`/`dlsym` and internal MOSAL symbols when available, which is fragile across library versions. VAPI port selection is fixed at `VAPI_PORT` rather than using the OpenIB-style `ib_port` option. Event handlers write to pipes and log errors from callback context; pipe backpressure or closed descriptors during shutdown would be sensitive. RDMA segmentation and registration lifetimes must match the shared RTS/CTS state machine. Some retry/count constants differ from OpenIB, so provider behavior can diverge under loss or RNR pressure.

## Test Signals
Provider tests should cover HCA discovery failure, inactive port detection, MOSAL reinitialization paths, QP capability verification across multiple connections, eager and large RDMA transfers, completion pipe wakeups, async event pipe reads, VAPI status-to-BMI conversion, and finalize cleanup of handlers, pipes, CQ, PD, HCA handle, and memory registrations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib/vapi.c -->
