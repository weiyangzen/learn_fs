# subset-b-007849 Research

Grouped research for the listed OrangeFS BMI InfiniBand experimental and MX build files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/ib-exp.c -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/ib-exp.c

## Purpose
Implements the shared, provider-independent half of the experimental OrangeFS BMI InfiniBand method. It exposes `bmi_ib_exp_ops`, translates BMI send/receive/test/cancel/address calls into an internal sendq/recvq protocol, manages eager buffers and credits, accepts or creates TCP control connections, and drives either OpenIB or VAPI provider callbacks through `ib_device->func`.

## Important APIs, Types, And Functions
The BMI method table maps the public BMI surface to `BMI_ib_initialize`, `BMI_ib_finalize`, `BMI_ib_post_send`, `BMI_ib_post_send_list`, `BMI_ib_post_sendunexpected`, `BMI_ib_post_sendunexpected_list`, `BMI_ib_post_recv`, `BMI_ib_post_recv_list`, `BMI_ib_test`, `BMI_ib_testsome`, `BMI_ib_testcontext`, `BMI_ib_testunexpected`, `BMI_ib_cancel`, `BMI_ib_method_addr_lookup`, `BMI_ib_memalloc`, `BMI_ib_memfree`, and `BMI_ib_set_info`/`BMI_ib_get_info`. Internal protocol helpers include `ib_check_cq`, `encourage_send_waiting_buffer`, `encourage_send_incoming_cts`, `encourage_recv_incoming`, `send_cts`, `encourage_rts_done_waiting_buffer`, `test_sq`, `test_rq`, `ib_new_connection`, `ib_close_connection`, `ib_tcp_client_connect`, and the server accept/process threads. The file relies on shared structures from `ib-exp.h`: `ib_device_t`, `ib_connection_t`, `ib_work`, `buf_head`, and encoded message headers.

## Control Flow
Initialization allocates `ib_device`, tries `openib_ib_initialize(options)` first when compiled with `OPENIB`, falls back to `vapi_ib_initialize(options)` when compiled with `VAPI`, initializes the memory registration cache, and optionally starts a TCP listen socket plus an accept thread for server mode. Address lookup parses `ib_exp://hostname:port/filesystem`, reuses existing connections when possible, or creates reconnect-capable method addresses.

Posting a send creates an `ib_work` and `method_op`, validates buffer-list totals, rejects unexpected sends larger than the eager payload, links the work on `sendq`, and calls `encourage_send_waiting_buffer`. Small messages are sent as `MSG_EAGER_SEND` or `MSG_EAGER_SENDUNEXPECTED` in an eager buffer. Large messages use a rendezvous path: send `MSG_RTS`, register the local buffer list, wait for `MSG_CTS`, issue provider RDMA writes, then send `MSG_RTS_DONE`.

Posting a receive either matches an already-arrived eager/RTS entry or creates an `RQ_WAITING_INCOMING` work item. Incoming eager data is copied into the posted BMI buffers and the receive buffer is reposted. Incoming RTS data records the remote operation id and sends CTS once a matching BMI receive and send buffer are available. `ib_check_cq` is the central progress loop: it polls provider completions, decodes receive headers, returns credits, advances send/receive states, deregisters buffers after RDMA completion, and reposts receive buffers. Test calls reap completed work, while `testcontext` and `testunexpected` can block through `ib_block_for_activity`, which uses provider CQ and async fds.

## State And Persistence
State is process-local and protected mostly by `interface_mutex`. `ib_device` owns the listen socket, connection list, sendq, recvq, provider-private state, eager buffer sizing, and memory cache. Each connection owns eager send/receive buffer pools, credit counters, a refcount that defers provider teardown while work requests are outstanding, cancellation/closed flags, and its BMI address. No durable disk state is written; persistence across calls is entirely in BMI method addresses, queues, registered-memory cache entries, TCP accept state, and provider QP/CQ resources.

## Dependencies And Integration Points
This file integrates BMI method support (`bmi-method-support.h`, `bmi-method-callback.h`), OrangeFS id generation, quicklists, gen locks, gossip logging, PVFS encode stubs, TCP sockets, pthread accept threads, and provider implementations in `openib-exp.c` and `vapi-exp.c`. It depends on `mem-exp.c` for registration caching and `util-exp.c` for logging, list, buffer-copy, and full-read/write helpers. The wire protocol and provider callback table are defined in `ib-exp.h`.

## Risks And Test Signals
The implementation is an experimental transport with several high-risk surfaces: a hand-rolled state machine, refcounted connection teardown, deferred memory deregistration, and multi-threaded TCP accept code entering a global interface lock. The CQ error path contains a suspicious `bh-c->closed` expression that looks like a typo for `bh->c->closed` and would produce invalid pointer arithmetic semantics if compiled. `BMI_ib_test` assumes `id_gen_fast_lookup(id)` succeeds before dereferencing. `error()` logs but no longer exits, so paths that expect fatal behavior may continue in inconsistent state. The rendezvous path relies on exact CTS byte counts and registered-memory lifetime. Useful tests are provider build coverage for both OpenIB and VAPI, server/client connection handshakes, eager expected/unexpected sends, large RTS/CTS/RDMA transfers with scattered buffers, cancellation during each send/recv state, disconnect/BYE handling, credit exhaustion/replenishment, and finalize with outstanding completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/ib-exp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/ib-exp.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/ib-exp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/mem-exp.c -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/mem-exp.c

## Purpose
Implements memory allocation, registration caching, deregistration, and cache flushing for the experimental InfiniBand BMI method. It reduces repeated HCA memory registration cost by keeping active and reusable memory-region entries around `memcache_entry_t` records.

## Important APIs, Types, And Functions
The private `memcache_device_t` holds active entries, a mutex, a free-chunk list, and provider callbacks for register/deregister. Internal helpers are `memcache_add`, `memcache_del`, `memcache_lookup_cover`, and `memcache_lookup_exact`. Public internal entry points are `memcache_memalloc`, `memcache_memfree`, `memcache_register`, `memcache_preregister`, `memcache_deregister`, `memcache_init`, `memcache_shutdown`, and `memcache_cache_flush`.

## Control Flow
`memcache_memalloc` first looks for an exact-size reusable free chunk for allocations larger than the eager limit. On a miss it calls `malloc`, then registers large buffers immediately through the provider callback. `memcache_memfree` keeps registered large allocations in `free_chunk_list` instead of freeing them, deregistering when their refcount drops to zero. `memcache_register` is used for user-provided send/receive buflists: each segment is matched against an existing covering registration or registered as a new region, and the resulting entries are stored in `buflist->memcache`. `memcache_deregister` decrements the stored entries after RDMA completion or cancellation and invokes provider deregistration when counts reach zero. `memcache_shutdown` frees active and cached free chunks, while `memcache_cache_flush` discards zero-refcount cached entries after provider registration pressure.

## State And Persistence
All state is runtime memory under `memcache_device_t`. Active and free lists keep `memcache_entry_t` objects with buffer address, length, refcount, and provider memory keys. Free-list entries may retain the actual malloced buffer for reuse, so memory persists beyond BMI `memfree` until shutdown or flush.

## Dependencies And Integration Points
The module depends on OrangeFS gen locks, quicklists via `ib-exp.h`, provider-specific memory registration callbacks supplied by `openib-exp.c` or `vapi-exp.c`, and generic allocation/error helpers. `ib-exp.c` calls it for BMI memory allocation, optimistic buffer registration, RTS/CTS/RDMA paths, cancellation cleanup, and final shutdown.

## Risks And Test Signals
The comments explicitly note the absence of a dreg-style consistency check for user buffers that may be freed or reused outside BMI. `memcache_preregister` returns immediately with "Can not do this any more", so `BMI_OPTIMISTIC_BUFFER_REG` is effectively disabled despite being accepted. `memcache_register` allocates `buflist->memcache` before all provider registrations are known to succeed, and failures log through non-fatal `error()`, leaving callers without a clear error return. Reusing free chunks can retain substantial pinned memory. Test signals include refcount accounting under overlapping buflists, registration failure/ENOMEM flush behavior, repeated memalloc/memfree reuse, cancellation deregistration for every RDMA state, and leak checks at shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/mem-exp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/module.mk.in -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/module.mk.in

## Purpose
Build-system fragment for the experimental BMI InfiniBand transport. It conditionally contributes the common IB method sources and whichever provider-specific source files are enabled by configure.

## Important APIs, Types, And Functions
The make variables are `DIR`, `cfiles`, `apis`, `src`, `LIBSRC`, `SERVERSRC`, `LIBBMISRC`, and per-file `MODCFLAGS_*`. Common sources are `ib-exp.c`, `util-exp.c`, and `mem-exp.c`. `BUILD_IB` adds `vapi-exp.c` and `-DVAPI`; `BUILD_OPENIB` adds `openib-exp.c` and `-DOPENIB`.

## Control Flow
The entire fragment is skipped unless `BUILD_IB` or `BUILD_OPENIB` is non-empty. Enabled sources are path-qualified under `src/io/bmi/bmi_ib_exp` and appended to the library, server, and BMI library source lists. Provider include directories are injected only for their provider files through `@IB_INCDIR@` and `@OPENIB_INCDIR@`. `ib-exp.c` receives compile-time API availability flags through `MODCFLAGS_$(DIR)/ib-exp.c`.

## State And Persistence
This file has no runtime state. Its persistent effect is generated build configuration: which transport provider objects are compiled and which preprocessor symbols select initialization branches in `ib-exp.c`.

## Dependencies And Integration Points
It depends on configure substitutions and top-level OrangeFS make variables. It integrates the shared IB transport into the library, server, and BMI library build products and must stay synchronized with the provider function declarations in `ib-exp.c`.

## Risks And Test Signals
Provider combinations matter: `BUILD_OPENIB` only, `BUILD_IB` only, both, and neither exercise different code paths. Stale provider branches are possible because inactive files are excluded entirely. Build tests should verify include paths, `-DOPENIB`/`-DVAPI` propagation to `ib-exp.c`, and successful linking of `bmi_ib_exp_ops` with the selected provider initializer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/openib-exp.c -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/openib-exp.c

## Purpose
Implements the OpenIB/libibverbs provider backend for the experimental BMI InfiniBand method. It opens an active verbs device, creates shared PD/CQ/completion-channel resources, brings up per-connection RC queue pairs, registers eager and RDMA buffers, posts SEND/RECV/RDMA_WRITE work requests, converts work completions into the generic `bmi_ib_wc` format, and handles async/CQ event fds for blocking progress.

## Important APIs, Types, And Functions
Provider-private state is held in `struct openib_device_priv` and `struct openib_connection_priv`. Major functions include `openib_ib_initialize`, `openib_ib_finalize`, `openib_new_connection`, `exchange_data`, `init_connection_modify_qp`, `openib_drain_qp`, `openib_close_connection`, `openib_post_sr`, `openib_post_rr`, `openib_post_sr_rdmaw`, `openib_check_cq`, `openib_prepare_cq_block`, `openib_ack_cq_completion_event`, `openib_wc_status_string`, `openib_wc_status_to_bmi`, `openib_mem_register`, `openib_mem_deregister`, `return_active_nic_handle`, `parse_bmi_opts_get_ib_port`, and `openib_check_async_events`.

## Control Flow
Initialization chooses an IB port from the BMI options string or the default, locates an active HCA/port, detects whether the link layer is InfiniBand or Ethernet/RoCE, queries device capabilities, allocates a protection domain, creates a completion channel and CQ, marks async and CQ fds nonblocking, and installs provider callbacks into `ib_device->func`.

`openib_new_connection` registers per-connection eager send/receive regions, creates an RC QP with bounded WR and SGE caps, exchanges LID or GID plus QP number over the TCP control socket, transitions the QP through INIT, RTR, and RTS, posts all eager receive buffers, and performs a final TCP synchronization. `openib_post_sr` sends eager/protocol messages. `openib_post_rr` reposts eager receive buffers. `openib_post_sr_rdmaw` decodes CTS remote buffer descriptors and emits one or more RDMA writes that gather from the sender buflist and walk the receiver buflist, signaling only the final WR so generic code can deregister memory and send RTS_DONE.

## State And Persistence
Device state persists for the BMI method lifetime: verbs context, CQ, PD, completion channel, selected port/id, SGE scratch array, device caps, and unsignaled-send counters. Per connection, the backend keeps a QP, eager memory regions, remote LID/GID, and remote QP number. Registered user-memory handles are stored in `memcache_entry_t.memkeys.mrh/lkey/rkey` and released through `openib_mem_deregister`.

## Dependencies And Integration Points
The file depends on libibverbs (`infiniband/verbs.h`), BMI byte swapping, shared helpers in `ib-exp.h`/`util-exp.c`, and memory-cache callbacks in `mem-exp.c`. It is selected by `BUILD_OPENIB` and called only through the callback table set during `openib_ib_initialize`.

## Risks And Test Signals
There are clear stale-code risks in conditional branches: one `HAVE_IBV_GET_DEVICES` path references fields/symbols such as `hca_port` and `od->nic_lid` that do not match the current `openib_device_priv` shape. Disabled `MEMCACHE_BOUNCEBUF` and `!MEMCACHE_EARLY_REG` branches call `memcache_register` with an outdated extra argument. Runtime risks include single-HCA selection, fixed GID index 0 for RoCE, exact QP capability assumptions across connections, manual SGE splitting, and non-fatal provider-post error handling. Test signals include building both modern and legacy verbs discovery paths, IB and RoCE connection setup, malformed `ib_port` options, inactive-port fallback, CQ polling/event blocking, async event logging, registration ENOMEM flush retry, scattered large RDMA transfers, and provider teardown after cancellation/finalize.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/openib-exp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/util-exp.c -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/util-exp.c

## Purpose
Provides small utility routines shared by the experimental BMI InfiniBand implementation: logging wrappers, checked allocation, quicklist head removal, state-name formatting, buffer-list copying, and full-length TCP read/write helpers.

## Important APIs, Types, And Functions
Logging functions are `error`, `error_errno`, `error_xerrno`, `warning`, `warning_errno`, and `warning_xerrno`. Other helpers are `bmi_ib_malloc`, `qlist_del_head`, `qlist_try_del_head`, `sq_state_name`, `rq_state_name`, `msg_type_name`, `memcpy_to_buflist`, `memcpy_from_buflist`, `read_full`, and `write_full`. Defining `__util_exp_c` before including `ib-exp.h` materializes the state/message name tables consumed by `name_lookup`.

## Control Flow
Logging wrappers format into fixed local buffers and write to the OrangeFS gossip error stream. `error()` additionally emits a backtrace but does not exit. `bmi_ib_malloc` rejects zero-byte requests and logs allocation failure. The quicklist helpers remove the first list entry, either strictly or with an empty-list NULL return. The copy helpers walk `ib_buflist_t` scatter/gather arrays to copy eager payloads into or out of contiguous eager buffers. `read_full` and `write_full` loop until EOF/error or the requested byte count is transferred for TCP handshake records.

## State And Persistence
No persistent state is owned here beyond the static name arrays compiled from `ib-exp.h`. The routines operate on caller-provided lists, buflists, file descriptors, and buffers.

## Dependencies And Integration Points
This file depends on standard C/POSIX headers, OrangeFS gossip logging via `ib-exp.h`, and `pvfs2-internal.h` formatting helpers. It supports all generic and provider-specific files, particularly TCP connection exchange and debug logging of state-machine transitions.

## Risks And Test Signals
The logging routines use `vsprintf` into 2048-byte buffers, so long formatted messages can overflow. `error()` and related functions have `exit(1)` commented out, which changes many caller assumptions from fatal to log-and-continue. `read_full` and `write_full` do not retry `EINTR`, so signal interruption can fail handshakes. State-name lookup only matches exact enum values, not combined receive bitmasks. Test signals include compiler format warnings, long-message handling, interrupted TCP read/write simulations, buflist copy bounds checks, and debug output for combined receive states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/util-exp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/vapi-exp.c -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/vapi-exp.c

## Purpose
Implements the legacy Mellanox VAPI provider backend for the experimental BMI InfiniBand method. It mirrors the OpenIB backend for older VAPI/EVAPI stacks: HCA discovery, PD/CQ setup, QP creation and transitions, eager buffer registration, SEND/RECV/RDMA_WRITE posting, completion conversion, memory registration, and pipe-based event forwarding.

## Important APIs, Types, And Functions
Provider state is stored in `struct vapi_device_priv` and `struct vapi_connection_priv`. Major functions include `vapi_ib_initialize`, `vapi_ib_finalize`, `vapi_new_connection`, `exchange_data`, `verify_prop_caps`, `init_connection_modify_qp`, `vapi_drain_qp`, `vapi_close_connection`, `vapi_post_sr`, `vapi_post_rr`, `vapi_post_sr_rdmaw`, `vapi_check_cq`, `vapi_prepare_cq_block`, `vapi_ack_cq_completion_event`, `vapi_wc_status_string`, `vapi_wc_status_to_bmi`, `vapi_mem_register`, `vapi_mem_deregister`, `error_verrno`, `async_event_handler`, `cq_event_handler`, `reinit_mosal`, and `vapi_check_async_events`.

## Control Flow
Initialization reinitializes MOSAL state to survive daemon fork behavior, lists HCAs through EVAPI, chooses the first HCA, installs callback functions in `ib_device->func`, obtains an HCA handle, registers an async handler, verifies port state, allocates a PD, creates a CQ, builds nonblocking pipes for CQ and async events, registers the CQ event handler, and initializes scratch SGE limits for the first connection.

`vapi_new_connection` registers eager receive and send buffers, creates an RC QP, verifies global SGE/outstanding-WR assumptions, exchanges LID and QP number over TCP, transitions the QP through INIT/RTR/RTS, posts initial receive buffers, and performs a final synchronization. `vapi_post_sr` and `vapi_post_rr` submit protocol SENDs and eager RECVs. `vapi_post_sr_rdmaw` decodes CTS descriptors and issues gathered RDMA writes over possibly multiple WRs, signaling the final WR so generic code can advance to RTS_DONE. Completion polling maps VAPI CQE opcodes into `BMI_IB_OP_SEND`, `BMI_IB_OP_RECV`, and `BMI_IB_OP_RDMA_WRITE`.

## State And Persistence
Device state persists in the HCA handle, CQ, PD, local LID, scratch SGE array, outstanding-WR caps, event handler handles, and pipe fds. Per connection, the backend stores QP handle/number, eager MR handles and lkeys, unsignaled counter, remote LID, and remote QP number. Registered memory keys are stored in the generic memcache entries.

## Dependencies And Integration Points
This file depends on VAPI/EVAPI headers, optional `wrap_common.h`, `libmosal.so` symbols through `dlopen`/`dlsym`, OrangeFS byte swapping and internal formatting, and shared BMI IB helpers. It is selected by `BUILD_IB`, while `ib-exp.c` calls it only if the OpenIB initializer did not succeed or was not compiled.

## Risks And Test Signals
VAPI is legacy and contains several environment-specific hacks. `reinit_mosal` reaches into libmosal internals or exported ioctl functions and can fail hard if library symbols differ. VAPI-specific fatal errors call `exit(1)` through `error_verrno`, unlike generic `error()`. Event handlers write to pipes from callback threads and can fail if pipes fill. The code ignores the `options` argument and always uses `VAPI_PORT`. As with OpenIB, disabled bounce-buffer branches may be stale. Test signals include VAPI-only build/link on a matching stack, daemon fork/startup, HCA absence/multiple-HCA behavior, port inactive errors, TCP QP exchange, CQ/async pipe event delivery, RDMA scatter/gather transfers, retry-exceeded error mapping, and clean handler/pipe teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/vapi-exp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_mx/module.mk.in -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_mx/module.mk.in

## Purpose
Build-system fragment for the OrangeFS BMI MX transport. It conditionally adds the MX implementation source to the library, server, and BMI library builds when configure enables MX support.

## Important APIs, Types, And Functions
The relevant make variables are `BUILD_MX`, `DIR`, `cfiles`, `src`, `LIBSRC`, `SERVERSRC`, `LIBBMISRC`, and `MODCFLAGS_$(DIR)`. The only source listed is `mx.c`, and MX headers are supplied through `-I@MX_INCDIR@`.

## Control Flow
If `BUILD_MX` is empty, the fragment contributes nothing. Otherwise it sets `DIR := src/io/bmi/bmi_mx`, expands `mx.c` to a source-tree path, appends that source to all three build source lists, and applies the configured MX include directory to the module.

## State And Persistence
This file has no runtime state. Its persistent effect is generated build metadata deciding whether the MX BMI transport is compiled and linked.

## Dependencies And Integration Points
It depends on configure detecting MX and substituting `@MX_INCDIR@`. It integrates the sibling `bmi_mx/mx.c` transport with the same top-level build variables used by other BMI modules.

## Risks And Test Signals
The main risks are stale configure detection, missing MX headers, and accidental omission from one of the build products if top-level variable semantics change. Test signals include a configure/build with `BUILD_MX` enabled, compile checks for `mx.c` against `@MX_INCDIR@`, and a disabled-MX build confirming the fragment is skipped cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_mx/module.mk.in -->
