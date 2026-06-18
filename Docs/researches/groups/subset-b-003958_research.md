# Research: subset-b-003958

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt.c

## Purpose
Implements the RTRS client kernel module: session/path creation, RDMA CM connection setup, permits, RDMA read/write request submission, failover, reconnect, heartbeat handling, and exported client APIs from `rtrs.h`.

## Important APIs, Types, And Functions
Exports `rtrs_clt_open()`, `rtrs_clt_close()`, `rtrs_clt_get_permit()`, `rtrs_clt_put_permit()`, `rtrs_clt_request()`, `rtrs_clt_rdma_cq_direct()`, and `rtrs_clt_query()`. Internal key paths include `init_path()`, `init_conns()`, `rtrs_send_path_info()`, `rtrs_rdma_conn_established()`, `rtrs_clt_read_req()`, `rtrs_clt_write_req()`, `complete_rdma_req()`, `fail_all_outstanding_reqs()`, and reconnect/close work handlers. It uses `struct rtrs_clt_sess`, `struct rtrs_clt_path`, `struct rtrs_clt_con`, `struct rtrs_clt_io_req`, and `struct rtrs_permit` from `rtrs-clt.h`.

## Control Flow
Open allocates a client device, creates one path per address, establishes all CM/QP connections, sends an info request over connection 0, receives exported server buffers, posts receive WRs, creates sysfs path files, then allocates global permits. Requests acquire a permit externally, choose a connected path by multipath policy, copy user control payload into an IU, map/fast-register SG data if present, and send an RDMA write-with-immediate to the server. Completions decode immediate payloads, process IO responses, handle rkey refresh responses, invalidate local MRs when needed, unmap DMA, and call the upper-layer confirmation callback.

## State And Persistence
State is in memory only: path state machine, RCU path list/per-CPU current path, bitmap-backed permits, request arrays, stats, workqueue items, and sysfs kobjects. Reconnects preserve path/session identity, but connection and memory registration state is rebuilt.

## Dependencies And Integration Points
Depends on RDMA CM, IB verbs, RTRS core helpers, private wire format, client stats/sysfs/trace modules, and upper-layer callbacks. It integrates with sysfs for manual path operations and with heartbeats from `rtrs.c`.

## Risks
High-risk areas are request lifetime/refcounting around local invalidation, reconnect races, failover using copied request metadata, immediate-data bit packing, send/recv WR sizing, and RCU/per-CPU path pointer replacement. Queue depth changes across reconnect deliberately disable auto-reconnect.

## Test Signals
Exercise module load/unload, open/close with multiple paths, read/write success and error callbacks, permit exhaustion/wakeups, server disconnect and reconnect, device removal, sysfs reconnect/path removal, multipath policies, direct CQ polling, malformed info/rkey responses, and MR invalidation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt.h

## Purpose
Defines the private client-side RTRS model shared by client implementation, client stats, sysfs, and trace code.

## Important APIs, Types, And Functions
Declares `enum rtrs_clt_state` for connection lifecycle and `enum rtrs_mp_policy` for path selection. Core data structures are `struct rtrs_clt_stats`, `struct rtrs_clt_con`, `struct rtrs_permit`, `struct rtrs_clt_io_req`, `struct rtrs_rbuf`, `struct rtrs_clt_path`, and `struct rtrs_clt_sess`. Inline helpers convert embedded core types (`to_clt_con()`, `to_clt_path()`), compute permit size, and locate a permit in the packed permit arena. It also declares sysfs entry points, reconnect/path management hooks, IB event handling, and client stats helpers implemented in sibling files.

## Control Flow
The header encodes ownership boundaries. `rtrs-clt.c` owns session/path/request state transitions; stats code owns the `rtrs_clt_stats` counters; sysfs code manipulates reconnect and dynamic path operations through declared hooks. Permits carry both a `mem_id` and immediate-data offset, tying request slots to server remote buffers.

## State And Persistence
All state is volatile kernel memory exposed partly through sysfs. `rtrs_clt_sess` persists for the open session and owns paths, global queue parameters, permit map, callbacks, and kobjects. `rtrs_clt_path` persists per RDMA route and owns connection arrays, remote buffer descriptors, request slots, reconnect work, heartbeat state via embedded `rtrs_path`, and path stats.

## Dependencies And Integration Points
Includes `rtrs-pri.h` and Linux device APIs. It is consumed by client core, client sysfs/stats, and potentially trace code.

## Risks
The types embed concurrency-sensitive fields: RCU lists, per-CPU path pointers, wait queues, work items, refcounted IO requests, and kobjects. Any layout or semantic change affects multiple compilation units.

## Test Signals
Build coverage for all client sibling files, sysfs path operations, stats reset/read, multipath IO, and reconnect/failover behavior validates this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-log.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-log.h

## Purpose
Provides small logging wrappers that prefix RTRS log messages with the session/path name.

## Important APIs, Types, And Functions
Defines `rtrs_log(fn, obj, fmt, ...)` and severity/rate-limited wrappers: `rtrs_err`, `rtrs_err_rl`, `rtrs_wrn`, `rtrs_wrn_rl`, `rtrs_info`, and `rtrs_info_rl`.

## Control Flow
Callers pass an object with a `sessname` member, typically `struct rtrs_path` or a compatible session-like object. The macro calls the supplied kernel printk function with `"<%s>: "` prefixing the caller message.

## State And Persistence
No state is stored. The only persistent effect is kernel log output.

## Dependencies And Integration Points
Relies on kernel `pr_*` functions and on object layout conventions used across RTRS client/server/core code. The source files set `pr_fmt` before including it, so line/module prefixes combine with this session prefix.

## Risks
Because this is macro-based and assumes `obj->sessname`, passing an incompatible pointer causes compile failures or worse if hidden behind casts. Format-string correctness remains the caller's responsibility. Rate-limited variants are essential in hot error paths to avoid log floods during transport failures.

## Test Signals
Compile-time use across all RTRS files is the main guard. Runtime signals are readable, rate-limited logs during connection failure, heartbeat loss, malformed messages, and sysfs-triggered disconnects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-pri.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-pri.h

## Purpose
Defines the private RTRS protocol ABI, shared core transport structures, immediate-data encoding, and internal helper prototypes used by both client and server.

## Important APIs, Types, And Functions
Key constants include protocol version, `MAX_SESS_QUEUE_DEPTH`, immediate-data bit widths, service queue depth, max paths, minimum chunk size, heartbeat cadence, magic, and encoded protocol version. Defines `enum rtrs_imm_type`, `enum rtrs_msg_types`, flags, `struct rtrs_rdma_dev_pd`, `struct rtrs_ib_dev`, `struct rtrs_con`, `struct rtrs_path`, `struct rtrs_iu`, wire messages (`rtrs_msg_conn_req/rsp`, `info_req/rsp`, `rkey_rsp`, `rdma_read/write`, `rtrs_sg_desc`), core helper prototypes, immediate packing helpers, and sysfs stats macros.

## Control Flow
Client and server agree on connection private data, info exchange, IO request layout, immediate-data payloads, and heartbeat messages through this header. `rtrs_to_imm()` reserves 4 high bits for type and 28 bits for payload; IO response payloads split errno and message id.

## State And Persistence
Defines in-memory connection/path/IU state and on-wire little-endian protocol structures. No persistent storage is used, but changes here are protocol compatibility changes.

## Dependencies And Integration Points
Includes RDMA CM/verbs, UUID, and public `rtrs.h`. Core implementation in `rtrs.c` provides the declared helpers; client/server implementations consume both protocol structures and helper functions.

## Risks
Wire layout, endian annotations, private-data size limits, and immediate-data bit packing are critical. Queue depth and chunk size must fit in the 28-bit immediate payload. Stats macros depend on kobject layout.

## Test Signals
Version negotiation, malformed message rejection, queue-depth/chunk-size boundary tests, endian-sensitive interop, heartbeat traffic, and build coverage across client/server/core validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-pri.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv-stats.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv-stats.c

## Purpose
Implements server-side RDMA statistics reset and formatting for sysfs.

## Important APIs, Types, And Functions
`rtrs_srv_reset_rdma_stats()` zeros each CPU's `struct rtrs_srv_stats_rdma_stats` when userspace writes an enabling value through the sysfs macro-generated attribute. `rtrs_srv_stats_rdma_to_str()` folds per-CPU read/write counters and byte totals into a single line.

## Control Flow
The server hot path updates per-CPU counters through `rtrs_srv_update_rdma_stats()` from `rtrs-srv.h`. Sysfs show calls aggregate all possible CPUs without locking individual counters, trading exact snapshots for low overhead. Store calls only accept the reset-enabled path; disabling returns `-EINVAL`.

## State And Persistence
Stats live in per-CPU kernel memory under each `rtrs_srv_stats`. They are resettable and not persisted across path teardown or module unload.

## Dependencies And Integration Points
Depends on `rtrs-srv.h`, Linux per-CPU iteration, and `sysfs_emit()`. Exposed through `rtrs-srv-sysfs.c` via `STAT_ATTR(struct rtrs_srv_stats, rdma, ...)`.

## Risks
Aggregation can race with live updates, so values are observational rather than transactionally consistent. Counter growth uses `u64`, but very long-lived high-throughput sessions can still wrap eventually.

## Test Signals
Validate sysfs `stats/rdma` output format, counter increments for server READ and WRITE events, reset behavior with `echo 1`, rejection of invalid reset values, CPU hotplug-adjacent possible-CPU iteration, and teardown after stats kobject release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv-stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv-sysfs.c

## Purpose
Creates and destroys server sysfs objects for sessions, paths, path attributes, disconnect control, and stats.

## Important APIs, Types, And Functions
Exports `rtrs_srv_create_path_files()` and `rtrs_srv_destroy_path_files()`. Defines kobject release callbacks for paths and stats, attributes `disconnect`, `hca_port`, `hca_name`, `src_addr`, `dst_addr`, and the generated `rdma` stats attribute. Helper functions create/destroy one-time session root folders and per-path stats files.

## Control Flow
When the server completes info request processing, it calls `rtrs_srv_create_path_files()`. This registers the session device under class `rtrs-server` once, creates a `paths` kobject, adds a path kobject named from source/destination addresses, attaches path attributes, and then adds a `stats` child. Writing `1` to `disconnect` removes that sysfs file first with `sysfs_remove_file_self()` and queues path close to avoid deadlock.

## State And Persistence
Sysfs mirrors live in-memory server session/path state. `dev_ref` counts active path users of the session device. Kobject release frees `srv_path`; stats kobject release frees per-CPU stats and the stats object.

## Dependencies And Integration Points
Depends on `rtrs-pri.h`, `rtrs-srv.h`, `rtrs-log.h`, address formatting from `rtrs.c`, `close_path()` from server core, and stats helpers from `rtrs-srv-stats.c`.

## Risks
Kobject/device reference ordering is delicate, especially on error unwind and disconnect from sysfs. Attribute names expose address formatting choices as ABI. `src_addr`/`dst_addr` intentionally present peer/local directions from the server perspective and can be confusing.

## Test Signals
Check sysfs tree creation/removal across first and additional paths, read all attributes, write disconnect, stats reset/read, error injection in kobject creation, and close during active IO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv-trace.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv-trace.c

## Purpose
Instantiates server tracepoints declared in `rtrs-srv-trace.h`.

## Important APIs, Types, And Functions
Includes public, private, and server RTRS headers, then defines `CREATE_TRACE_POINTS` before including `rtrs-srv-trace.h`. This causes the tracepoint storage and registration code for `TRACE_EVENT(send_io_resp_imm)` to be emitted in exactly one compilation unit.

## Control Flow
There is no runtime control flow beyond tracepoint registration generated by the kernel trace framework. The server response path calls `trace_send_io_resp_imm()` from `send_io_resp_imm()` in `rtrs-srv.c`; this file supplies the generated tracepoint implementation.

## State And Persistence
Tracepoint enablement/state is managed by the kernel tracing subsystem. This file owns no driver state and persists no data outside trace buffers when tracing is enabled.

## Dependencies And Integration Points
Depends on header include order so helpers such as `to_srv_path()` and protocol definitions are visible to trace event assignment code. Integrates with ftrace/perf/tracefs through `TRACE_EVENT`.

## Risks
Multiple `CREATE_TRACE_POINTS` inclusions would cause duplicate definitions; omitting this file would leave trace call sites unresolved. Header changes must preserve availability of types used by trace macros.

## Test Signals
Build/link success with tracing enabled, presence of `rtrs_srv:send_io_resp_imm` under tracefs, enabling the event during RDMA responses, and module unload without tracepoint lifetime warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv-trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv-trace.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv-trace.h

## Purpose
Declares RTRS server trace events, currently focused on immediate IO responses.

## Important APIs, Types, And Functions
Sets `TRACE_SYSTEM rtrs_srv`, forward-declares server types, defines symbolic names for `enum rtrs_srv_state`, provides `show_rtrs_srv_state()`, and declares `TRACE_EVENT(send_io_resp_imm)`. The event records direction, invalidation mode, message id, WR count, signal interval, path state, errno, and session name.

## Control Flow
`send_io_resp_imm()` calls the generated trace hook before posting response WRs. `TP_fast_assign` walks from `struct rtrs_srv_op` to connection, common path, and server path, snapshots state and counters, and copies the kobject session name for formatted output.

## State And Persistence
No driver state is owned by the header. Event data is transient and captured only when tracing is active.

## Dependencies And Integration Points
Requires Linux tracepoint infrastructure and server/core type definitions to be available before macro expansion. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE rtrs-srv-trace` support kernel trace header generation.

## Risks
Trace event fields are a user-visible tracing ABI. The event dereferences `id->con` and kobject name, so call sites must only trace valid live operations. Copying `NAME_MAX` bytes assumes the destination has that bound.

## Test Signals
Compile with tracepoints, inspect generated event format, enable event while issuing read/write responses, verify symbolic state/direction formatting, and test with both `always_invalidate` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv-trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv.c

## Purpose
Implements the RTRS server kernel module: listener setup, session/path acceptance, exported server APIs, server memory buffer registration, IO request dispatch to upper layers, responses, heartbeat handling, stats, and cleanup.

## Important APIs, Types, And Functions
Exports `rtrs_srv_open()`, `rtrs_srv_close()`, `rtrs_srv_resp_rdma()`, `rtrs_srv_set_sess_priv()`, `rtrs_srv_get_path_name()`, and `rtrs_srv_get_queue_depth()`. Major internal functions include `rtrs_rdma_connect()`, `get_or_create_srv()`, `__alloc_path()`, `create_con()`, `process_info_req()`, `process_io_req()`, `process_read()`, `process_write()`, `send_io_resp_imm()`, `rdma_write_sg()`, `map_cont_bufs()`, and `rtrs_srv_close_work()`.

## Control Flow
`rtrs_srv_open()` registers an IB client; on first IB device, the server creates IP and IB CM listeners. Connect requests validate magic/version/cids, find or create a session by paths UUID, create or find a path by session UUID, allocate QPs, then accept with queue/max IO metadata. After the client sends `INFO_REQ`, the server posts receives, validates pathname uniqueness, registers and advertises memory regions, creates sysfs, marks the path connected, starts heartbeat, and invokes link callbacks. Client IO arrives as RDMA-write-with-immediate into a registered chunk; immediate payload identifies buffer and offset. The server decodes read/write messages, calls `ops.rdma_ev()`, and later upper layers complete via `rtrs_srv_resp_rdma()`, which posts either an immediate status or RDMA writes data back to the client's SG descriptor.

## State And Persistence
State is volatile: global listener context, sessions keyed by paths UUID, paths keyed by session UUID, registered MRs, per-buffer chunks, DMA address array, operation IDs, inflight percpu refs, workqueue close state, and sysfs objects.

## Dependencies And Integration Points
Uses RDMA CM, IB verbs, RTRS core helpers, private wire structs, server sysfs/stats/trace modules, and upper-layer `rtrs_srv_ops`.

## Risks
Important risks are CM lifetime, duplicate path/session handling, zombie connecting paths, memory registration invalidation/rkey refresh, send queue backpressure wait list, operation ID lifetime, and immediate-data bounds. Module parameters must preserve immediate payload encodability.

## Test Signals
Test listener creation on IP and IB port spaces, valid/invalid connection private data, duplicate path rejection, info handshake, read/write callbacks, response queuing under send queue pressure, `always_invalidate` on/off, heartbeat timeout, sysfs disconnect, device removal, and module parameter boundary checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv.h

## Purpose
Defines private server-side RTRS state shared by server core, stats, sysfs, and trace code.

## Important APIs, Types, And Functions
Declares `enum rtrs_srv_state`, stats structures, `struct rtrs_srv_con`, `struct rtrs_srv_op`, `struct rtrs_srv_mr`, `struct rtrs_srv_path`, `struct rtrs_srv_sess`, `struct rtrs_srv_ctx`, and `struct rtrs_srv_ib_ctx`. Provides `to_srv_path()` and `rtrs_srv_update_rdma_stats()`. Declares `close_path()`, IB event handler, stats helpers, and sysfs create/destroy functions.

## Control Flow
The header defines the data model used by `rtrs-srv.c`: a server context owns sessions; sessions own paths and preallocated chunk pages; paths own RDMA connections, memory regions, operation IDs, stats, and kobjects. `rtrs_srv_op` is the handle passed to upper-layer callbacks and later returned to `rtrs_srv_resp_rdma()`.

## State And Persistence
All structures represent live kernel memory. `refcount_t` protects sessions, `percpu_ref` protects inflight operation IDs during path close, and kobjects expose parts of the state to sysfs.

## Dependencies And Integration Points
Includes device/refcount/percpu Linux APIs and `rtrs-pri.h`. It is consumed by server implementation, sysfs, stats, and tracepoint declarations.

## Risks
Changes to these structures affect lifetime management across multiple files. `rtrs_srv_op` contains embedded WR/SG objects reused for response posting, so concurrent reuse is controlled by queue depth and operation ID lifetime. Stats updates are per-CPU and intentionally low overhead.

## Test Signals
Build all server compilation units, run sysfs/stat operations, issue concurrent IO and close, verify operation completion/ref release, and enable tracepoints using `to_srv_path()`-based state extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs.c

## Purpose
Implements common RTRS core helpers shared by client and server: IU allocation/posting, CQ/QP creation, heartbeat transport, address parsing/formatting, and RDMA device/protection-domain pooling.

## Important APIs, Types, And Functions
Exports IU helpers (`rtrs_iu_alloc/free/post_recv/post_send/post_rdma_write_imm`), empty receive posting, `rtrs_cq_qp_create/destroy()`, heartbeat helpers (`rtrs_init_hb/start/stop/send_hb_ack()`), address helpers (`rtrs_addr_to_sockaddr()`, `sockaddr_to_str()`, `rtrs_addr_to_str()`), and device pool helpers (`rtrs_rdma_dev_pd_init/deinit()`, `rtrs_ib_dev_find_or_add()`, `rtrs_ib_dev_put()`).

## Control Flow
IU allocation creates DMA-mapped buffers with completion callbacks. Send helpers optionally chain caller-provided WRs before/tail after RTRS WRs. CQ/QP creation uses a dedicated CQ for direct poll queues and CQ pool for interrupt/workqueue contexts. Heartbeat work sends RDMA-write-with-immediate heartbeat messages on connection 0, tracks missed acknowledgements, and calls the side-specific error handler when the missed limit is exceeded.

## State And Persistence
Maintains per-connection QP/CQ fields, heartbeat delayed work fields in `struct rtrs_path`, and a refcounted pool of `struct rtrs_ib_dev` entries keyed by IB device GUID with shared PDs. No disk persistence exists.

## Dependencies And Integration Points
Uses RDMA CM, IB verbs, inet address parsing, RTRS private definitions, and logging macros. Client/server modules provide pool init/deinit callbacks for IB event handlers.

## Risks
DMA map/unmap symmetry, WR chain correctness, CQ ownership differences, heartbeat false positives, address parsing prefixes, and `node_guid`-based device pooling are key risk areas.

## Test Signals
Validate IU allocation failure unwind, zero-length SG rejection, CQ/QP creation for softirq/direct/workqueue poll contexts, heartbeat ack/loss recovery, address parse/format round trips for `ip:` and `gid:`, and refcounted PD cleanup on module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs.h

## Purpose
Defines the public RTRS API used by kernel upper layers to open client sessions, submit RDMA requests, run servers, and convert addresses.

## Important APIs, Types, And Functions
Forward-declares opaque client/server handles and defines `struct rtrs_addr`, client link events, `struct rtrs_clt_ops`, permit wait/type enums, `struct rtrs_clt_req_ops`, `struct rtrs_attrs`, server link events, and `struct rtrs_srv_ops`. Public functions cover client open/close/permit/request/query/direct CQ polling; server open/close/respond/set private data/query path name/query depth; and address string conversions.

## Control Flow
Client users call `rtrs_clt_open()`, get permits, submit `rtrs_clt_request()` with control kvec and optional SG data, receive completion through `conf_fn`, and return permits. Server users call `rtrs_srv_open()`, receive link callbacks and RDMA events through `rtrs_srv_ops`, then complete each event with `rtrs_srv_resp_rdma()`.

## State And Persistence
The header exposes opaque handles only; implementation state is private and volatile. User private pointers are stored in sessions and returned to callbacks.

## Dependencies And Integration Points
Depends on Linux socket and scatterlist types. It is the API boundary between RTRS and consumers such as RNBD-like block/storage layers.

## Risks
Callback contracts are central: server `rdma_ev()` returning nonzero triggers error response, while async success requires later response with the provided op id. Permit misuse can stall or corrupt queue slot ownership. Address strings must use supported prefixes.

## Test Signals
Compile external consumers, verify callback ordering, permit exhaustion/release, request size limits surfaced by query attrs, server response semantics, link events, and address conversion error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srp/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srp/Kbuild

## Purpose
Defines the kernel build object for the InfiniBand SRP upper-layer protocol driver.

## Important APIs, Types, And Functions
Contains one build rule: `obj-$(CONFIG_INFINIBAND_SRP) += ib_srp.o`. No C APIs or runtime types are defined here.

## Control Flow
Kbuild includes `ib_srp.o` in the build when `CONFIG_INFINIBAND_SRP` is enabled as built-in or module. The actual source aggregation is handled by surrounding kernel build conventions and the `ib_srp` source file(s).

## State And Persistence
No runtime state. Its only persistent effect is build graph selection.

## Dependencies And Integration Points
Tied directly to the `INFINIBAND_SRP` Kconfig symbol declared in the adjacent `Kconfig`. Integrates with the kernel's `obj-y`/`obj-m` mechanism.

## Risks
Renaming the object or mismatching the Kconfig symbol would silently drop or misbuild SRP support. This file is intentionally minimal, so risk is mostly build configuration drift.

## Test Signals
Run kernel config builds with `CONFIG_INFINIBAND_SRP=y`, `m`, and unset; verify `ib_srp.o` is built only in enabled cases and module packaging names remain expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srp/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srp/Kconfig

## Purpose
Declares the configuration option for the InfiniBand SCSI RDMA Protocol driver.

## Important APIs, Types, And Functions
Defines `config INFINIBAND_SRP` as a tristate named "InfiniBand SCSI RDMA Protocol". It depends on `SCSI` and `INFINIBAND_ADDR_TRANS`, selects `SCSI_SRP_ATTRS`, and includes help text describing SRP storage access over InfiniBand.

## Control Flow
During kernel configuration, this symbol becomes available only when the SCSI core and RDMA address translation support are enabled. Selecting it causes the adjacent Kbuild to compile `ib_srp.o`; selecting it also forces common SCSI SRP attributes.

## State And Persistence
The symbol value persists in the kernel `.config` and controls whether SRP support is absent, built-in, or a module. It has no direct runtime state.

## Dependencies And Integration Points
Integrates SCSI, RDMA address translation, and the kernel build system. The help text points to INCITS T10 as the SRP protocol authority.

## Risks
Dependency mistakes can expose an unbuildable option or hide valid configurations. The `select` assumes `SCSI_SRP_ATTRS` has no unmet dependencies that need user visibility.

## Test Signals
Exercise menuconfig/allmodconfig paths, dependency-disabled configurations, built-in and module builds, and verify `SCSI_SRP_ATTRS` is selected when SRP is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srp/Kconfig -->
