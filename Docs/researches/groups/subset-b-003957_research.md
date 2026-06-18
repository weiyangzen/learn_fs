# subset-b-003957 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/iscsi_iser.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/iscsi_iser.c

Purpose: Implements the open-iscsi initiator transport named `iser`, wiring libiscsi/SCSI host operations to the iSER RDMA data mover. It owns module parameters, task lifecycle callbacks, connection/session creation, endpoint connect/poll/disconnect, negotiated parameter validation, and module init/exit.

Important APIs/types/functions: Registers `iscsi_iser_transport` and `iscsi_iser_sht`. Main transport callbacks include `iscsi_iser_session_create()`, `iscsi_iser_conn_create()`, `iscsi_iser_conn_bind()`, `iscsi_iser_conn_start()`, `iscsi_iser_conn_stop()`, `iscsi_iser_ep_connect()`, `iscsi_iser_ep_poll()`, `iscsi_iser_ep_disconnect()`, `iscsi_iser_task_init()`, `iscsi_iser_task_xmit()`, and `iscsi_iser_cleanup_task()`. `iscsi_iser_recv()` validates iSCSI PDU payload length and completes the PDU into libiscsi. Module parameters include `debug_level`, `max_lun`, `max_sectors`, `always_register`, and `pi_enable`.

Control flow: Module init creates the global TX descriptor cache, initializes global device/connection lists, creates a release workqueue, and registers the iscsi transport. Endpoint connect allocates an iscsi endpoint plus separate `iser_conn`, initializes it, and starts RDMA CM connection establishment through `iser_connect()`. Session creation allocates a SCSI host, derives queue depth and SG limits from the already-connected endpoint when available, exposes T10-PI protection when supported, adds the host, and calls `iscsi_session_setup()`. Binding validates the userspace endpoint handle with `iscsi_lookup_endpoint()`, checks `ISER_CONN_UP`, allocates RX/fastreg resources, and swaps `conn->dd_data` from libiscsi private state to `iser_conn`. Task xmit sends management tasks through `iser_send_control()`, sends SCSI commands through `iser_send_command()`, then sends any unsolicited Data-Out PDUs through `iser_send_data_out()`. Cleanup unmaps the task header and finalizes RDMA registrations unless the RDMA device was already removed.

State and persistence: Persistent module state lives in global `ig`, the release workqueue, the descriptor kmem cache, and the registered iscsi transport. Per-session state is a SCSI host and libiscsi session. Per-connection state is externalized through `iser_conn`, protected by `state_mutex` and synchronized with `stop_completion`, `ib_completion`, and `up_completion`. Per-task state is `iscsi_iser_task`, embedded in libiscsi task private memory, holding mapped headers, RDMA direction flags, registration state, and SCSI command references.

Dependencies and integration: Depends on libiscsi, SCSI midlayer, iscsi transport class, RDMA CM/verbs through the helper files, and T10-PI SCSI protection APIs. It integrates with userspace open-iscsi through endpoint handles, visible iscsi host/connection/session parameters, and negotiated digest/marker restrictions. It relies on `iser_initiator.c` for PDU send/receive completions, `iser_memory.c` for DMA/fastreg, and `iser_verbs.c` for RDMA connection and resource management.

Risks: Connection teardown is race-sensitive: `iscsi_iser_conn_stop()` serializes with device removal through `state_mutex` and `unbind_iser_conn_mutex`, while `iscsi_iser_ep_disconnect()` may queue deferred release if the iscsi connection is bound. `iscsi_iser_ep_connect()` allocates `iser_conn` separately from the endpoint because RDMA cleanup is asynchronous; failure paths must not leak either object. Header DMA mappings are skipped if `device` is already NULL after device removal, so double-unmap avoidance relies on `mapped` and device lifetime. Negotiation rejects header/data digests and markers, which is correct for iSER but sensitive to userspace parameter handling. Test signals include login/full-feature session bring-up, nonblocking endpoint poll timeout and signal interruption, device removal during SCSI error handling TMF, max_sectors reduction, PI-enabled host capability exposure, discovery sessions, and module unload with live-connection cleanup warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/iscsi_iser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/iscsi_iser.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/iscsi_iser.h

Purpose: Defines the iSER initiator private ABI shared by the transport, initiator PDU, memory-registration, and verbs files. It contains constants for queue sizing and PDU layout, debug macros, connection/task/device structures, registration pools, global state, function prototypes, and CQE container helpers.

Important APIs/types/functions: Major types are `iser_device`, `ib_conn`, `iser_conn`, `iscsi_iser_task`, `iser_tx_desc`, `iser_rx_desc`, `iser_login_desc`, `iser_fr_desc`, `iser_fr_pool`, `iser_data_buf`, `iser_mem_reg`, and `iser_global`. Enums describe connection state, task status, data direction, and TX descriptor type. Constants size SCSI command queues, send/recv WRs, fast registration WR budget, RX payload/login buffers, and SG table limits. Inline helpers `to_iser_conn()`, `iser_rx()`, `iser_tx()`, and `iser_login()` recover owner objects from embedded RDMA callbacks.

Control flow: The header establishes contracts rather than executing flow. TX descriptors carry iSER/iSCSI headers plus optional immediate/control payload SGE and optional invalidation/registration WRs chained before the send. RX descriptors carry receive buffers and CQEs. `iser_conn` aggregates transport state, RDMA resources, login buffers, RX descriptors, completion objects, and negotiated remote invalidation. `iscsi_iser_task` tracks per-command DMA buffers and registered memory for inbound and outbound directions.

State and persistence: Device state is refcounted globally in `ig.device_list`; connection state is tracked in `ig.connlist` and `iser_conn.state`; fast-reg resources persist per connection in `ib_conn.fr_pool`; task state persists for libiscsi task lifetime. Boolean fields such as `mapped`, `sig_protected`, `pi_support`, and `snd_w_inv` are important lifetime and capability guards.

Dependencies and integration: Includes Linux SCSI/libiscsi, iscsi transport, DMA mapping, RDMA verbs/CM, and the common iSER protocol header. Function prototypes connect the four iSER implementation files and expose transport callbacks for receive, send, RDMA setup/finalize, fast registration, connection handling, and PI status checks.

Risks: Queue-size macros are coupled to libiscsi `ISCSI_DEF_XMIT_CMDS_MAX`, RDMA device `max_qp_wr`, and assumptions about inflight Data-Outs; mismatches can under-provision the QP or overstate `max_cmds`. `ISER_RX_PAD_SIZE` depends on packed layout and can break if descriptor fields change. Container helpers assume CQEs are embedded exactly as declared. Test signals include compile-time layout/build coverage, QP sizing under low `max_qp_wr`, PI and non-PI configurations, SG gaps capability variation, and sparse/lockdep coverage around shared structure fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/iscsi_iser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/iser_initiator.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/iser_initiator.c

Purpose: Implements iSER initiator PDU construction, login/RX buffer allocation, command/control/Data-Out sending, receive completions, remote invalidation handling, and per-task RDMA finalization.

Important APIs/types/functions: Public entry points are `iser_alloc_rx_descriptors()`, `iser_free_rx_descriptors()`, `iser_send_command()`, `iser_send_data_out()`, `iser_send_control()`, `iser_login_rsp()`, `iser_task_rsp()`, `iser_cmd_comp()`, `iser_ctrl_comp()`, `iser_dataout_comp()`, `iser_task_rdma_init()`, and `iser_task_rdma_finalize()`. Internal helpers include `iser_prepare_read_cmd()`, `iser_prepare_write_cmd()`, `iser_create_send_desc()`, `iser_alloc_login_buf()`, `iser_post_rx_bufs()`, and `iser_check_remote_inv()`.

Control flow: A SCSI READ maps and registers the Data-IN buffer, sets `ISER_RSV`, and publishes read STag/VA for target RDMA write. A SCSI WRITE maps and registers Data-OUT memory, optionally sets `ISER_WSV` and write STag/VA for target RDMA read, and attaches immediate data as the second SGE. Commands are then posted through `iser_post_send()`, which may chain memory registration WRs first. Data-Out PDUs allocate a transient TX descriptor from `ig.desc_cache`, map headers, attach the registered buffer slice by offset, validate bounds, and free on completion. Control/login sends optionally copy login payload into the DMA login request buffer, post login receive, post full-feature RX buffers after the final login request, and send the control descriptor. Receive completions sync DMA to CPU, pass PDUs to libiscsi, sync back to device, and repost buffers.

State and persistence: RX descriptors and login buffers persist for connection lifetime after bind. Fast-reg descriptors are allocated in `iser_alloc_rx_descriptors()` via the verbs pool. Task state persists in `iscsi_iser_task`; `command_sent` prevents duplicate command PDU sends, `status` controls RDMA cleanup, and direction flags drive unregistration/unmapping. Remote invalidation updates `need_inval` on the relevant MR through the fast-reg descriptor.

Dependencies and integration: Uses libiscsi task/request helpers, SCSI scatterlists and protection SG lists, RDMA DMA mapping and CQ completions, iSER protocol flags, and functions from `iser_memory.c` and `iser_verbs.c`. Completion handlers are installed into `ib_cqe.done` fields and run from CQ polling context.

Risks: `iser_reg_desc_get_fr()` assumes the fastreg free list is non-empty; command concurrency must match pool sizing. Remote invalidation is protocol-sensitive: an unexpected invalidation when `snd_w_inv` is false or a mismatched rkey triggers connection failure. Login/full-feature RX posting deliberately skips and later posts the first RX descriptor; off-by-one failures can starve receives. `iser_ctrl_comp()` recovers the owning task through pointer arithmetic based on libiscsi private memory layout. Test signals include READ/WRITE with immediate and unsolicited data, multiple Data-Out PDUs, discovery session login, full-feature transition receive posting, remote invalidation positive and bogus-rkey cases, send completion failures, and DMA leak checking on failed sends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/iser_initiator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/iser_memory.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/iser_memory.c

Purpose: Provides initiator-side DMA mapping and memory registration for SCSI data and protection buffers, including fast registration, optional unsafe DMA-key shortcut, T10-DIF signature MR setup, local invalidation chaining, and PI status checking support.

Important APIs/types/functions: Public functions are `iser_dma_map_task_data()`, `iser_dma_unmap_task_data()`, `iser_reg_mem_fastreg()`, `iser_unreg_mem_fastreg()`, and `iser_reg_comp()`. Core helpers include `iser_reg_dma()`, `iser_fast_reg_mr()`, `iser_reg_sig_mr()`, `iser_set_sig_attrs()`, `iser_set_dif_domain()`, `iser_set_prot_checks()`, and `iser_inv_rkey()`.

Control flow: Mapping records the direction flag, maps the command data SG list with `ib_dma_map_sg()`, and maps the protection SG list when present. Registration uses the unsafe global DMA rkey only for a single DMA segment when allowed by `all_imm` or `!iser_always_reg` and the command has no PI operation. Otherwise it removes a fast-reg descriptor from the connection pool, either maps a normal MR with `ib_map_mr_sg()` and prepares `IB_WR_REG_MR`, or builds signature attributes, maps data plus protection SGs with `ib_map_mr_sg_pi()`, and prepares `IB_WR_REG_MR_INTEGRITY`. If the selected MR still needs invalidation, a local invalidate WR is chained before the registration WR and then the send WR.

State and persistence: `iser_mem_reg` records the SGE, rkey, and descriptor used by each task direction. Fast-reg descriptors cycle between an available list and active command ownership. `mr->need_inval` and `sig_mr->need_inval` persist across uses and decide whether local invalidation is required. `sig_protected` marks descriptors requiring signature MR status checks before returning to the pool.

Dependencies and integration: Depends on RDMA verbs MR APIs, SCSI protection metadata helpers, scatterlist DMA mapping, and task send descriptors from `iscsi_iser.h`. It integrates with `iser_post_send()` through pre-populated `inv_wr` and `reg_wr` chains, and with cleanup/protection callbacks through `iser_unreg_mem_fastreg()` and `iser_check_task_pi_status()` in `iser_verbs.c`.

Risks: The DMA-key shortcut returns `rkey = 0` unless the PD has `IB_PD_UNSAFE_GLOBAL_RKEY`; targets must not attempt RDMA using an invalid remote key in unsupported cases. PI paths must always check signature MR status before descriptor reuse if the task completes outside a normal SCSI response. Mapping/unmapping of protection SGs is conditional on `scsi_prot_sg_count()`, so mismatched command state can leak or double-unmap. Test signals include single-SGE DMA shortcut with `always_register=0`, multi-SGE fast registration, PI READ/WRITE insert/strip/pass, local invalidation reuse, map failure unwinds, and timeout/error cleanup of signature-protected commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/iser_memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/iser_verbs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/iser_verbs.c

Purpose: Owns initiator-side RDMA verbs and RDMA CM lifecycle: device discovery/refcounting, PD/event handler allocation, fast-reg pool allocation, CQ/QP creation, connection establishment/termination, send/recv posting, PI status translation, and workqueue-based resource release.

Important APIs/types/functions: Public functions include `iser_device_find_by_ib_device()`, `iser_alloc_fastreg_pool()`, `iser_free_fastreg_pool()`, `iser_conn_init()`, `iser_connect()`, `iser_conn_terminate()`, `iser_conn_release()`, `iser_release_work()`, `iser_post_recvl()`, `iser_post_recvm()`, `iser_post_send()`, `iser_check_task_pi_status()`, and `iser_err_comp()`. Internal RDMA CM handlers include `iser_addr_handler()`, `iser_route_handler()`, `iser_connected_handler()`, `iser_cleanup_handler()`, and `iser_cma_handler()`.

Control flow: Address resolution finds or creates a shared `iser_device`, allocates a PD with optional unsafe global rkey, registers async events, negotiates PI capability, computes SCSI SG/MR sizing, and resolves the route. Route resolution creates CQ/QP resources, prepares iSER CM private data advertising unsupported ZBVA and optional send-with-invalidate, and calls `rdma_connect_locked()`. ESTABLISHED records remote invalidation support and completes `up_completion`. Disconnect/address-change/timewait events terminate the connection, optionally signal libiscsi failure, free QP/CQ and connection resources, and complete `ib_completion`. Device removal additionally releases device-owned resources and returns nonzero so RDMA CM destroys the id. Sends sync header DMA, populate an `IB_WR_SEND`, and post either invalidation, registration, or send as the first WR in the chain.

State and persistence: `iser_device` objects persist globally by IB node GUID with a refcount. `ib_conn` holds `cma_id`, QP, CQ, CQ size, device pointer, fast-reg pool, PI support, and registration CQE. `iser_conn` state transitions from INIT to PENDING to UP to TERMINATING/DOWN under `state_mutex`. Fast-reg pool descriptors persist from bind until RX descriptor/free path. Release work waits for both iscsi stop and IB cleanup before marking DOWN and freeing the connection.

Dependencies and integration: Uses RDMA CM, verbs PD/CQ/QP/MR APIs, CQ pool, SCSI protection capability fields, libiscsi queue suspension/failure callbacks, and shared structures from `iscsi_iser.h`. It is the connection substrate for `iscsi_iser.c`, `iser_initiator.c`, and `iser_memory.c`.

Risks: `iser_connect()` waits for `up_completion` while holding `state_mutex` in blocking mode; correctness depends on use patterns and RDMA CM callback locking. Device lookup keys on node GUID, so multi-port or same-GUID behavior follows that sharing model. CQ/QP WR sizing clamps to device `max_qp_wr`, which reduces `max_cmds` and must remain consistent with SCSI queue setup. `iser_free_fastreg_pool()` warns when descriptors are still registered but still destroys all descriptors in `all_list`; active task cleanup ordering is critical. Test signals include RDMA CM address/route/connect errors, rejection, disconnect, device removal, PI and non-PI QP creation, low `max_qp_wr` devices, remote invalidation negotiation, drain on teardown, and CQ completion failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/iser_verbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/isert/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/isert/Kconfig

Purpose: Declares the build configuration option for the iSER target transport.

Important APIs/types/functions: Defines `CONFIG_INFINIBAND_ISERT` as a tristate option labelled "iSCSI Extensions for RDMA (iSER) target support".

Control flow: When enabled as built-in or module, Kbuild compiles the adjacent `ib_isert.o` target transport. The option is only visible when its dependency stack is satisfied.

State and persistence: Build-time configuration only; no runtime state.

Dependencies and integration: Requires `INET`, `INFINIBAND_ADDR_TRANS`, `TARGET_CORE`, and `ISCSI_TARGET`, expressing that the module bridges RDMA address translation with the kernel target-core iSCSI target.

Risks: Missing dependencies can break builds or expose the option without target/RDMA infrastructure. Test signals include `allmodconfig`/`allyesconfig`, dependency-disabled configs, and module load with target-core/iSCSI target enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/isert/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/isert/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/isert/Makefile

Purpose: Provides the Kbuild rule for the iSER target module.

Important APIs/types/functions: Binds `obj-$(CONFIG_INFINIBAND_ISERT)` to `ib_isert.o`.

Control flow: Kbuild compiles and links `ib_isert.c` into the `ib_isert` object when `CONFIG_INFINIBAND_ISERT` is enabled.

State and persistence: Build metadata only.

Dependencies and integration: Integrates directly with the Kconfig symbol from the same directory and relies on headers from RDMA core, target-core, and iscsi target through the source file includes.

Risks: If additional source files are added later, this object list must be updated or code will be omitted. Test signals include module build and modpost unresolved-symbol checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/isert/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/isert/ib_isert.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/isert/ib_isert.c

Purpose: Implements the kernel iSER target transport (`IB/iSER`) for target-core iscsi. It accepts RDMA CM connections, performs login PDU exchange, binds accepted RDMA connections to `iscsit_conn`, receives iSCSI PDUs, performs RDMA READ/WRITE for SCSI data, sends responses and control PDUs, handles PI offload, and tears connections/listeners down.

Important APIs/types/functions: Registers `iser_target_transport` with callbacks such as `isert_setup_np()`, `isert_accept_np()`, `isert_free_np()`, `isert_wait_conn()`, `isert_free_conn()`, `isert_get_login_rx()`, `isert_put_login_tx()`, `isert_immediate_queue()`, `isert_response_queue()`, `isert_get_dataout()`, `isert_put_datain()`, `isert_put_response()`, `isert_aborted_task()`, and `isert_get_sup_prot_ops()`. RDMA/verbs helpers include `isert_device_get()`, `isert_create_qp()`, `isert_alloc_rx_descriptors()`, `isert_connect_request()`, `isert_cma_handler()`, `isert_post_recvm()`, `isert_post_recv()`, and `isert_rdma_rw_ctx_post()`.

Control flow: Listener setup creates an `isert_np`, binds and listens with RDMA CM, and stores it in `np->np_context`. On CONNECT_REQUEST, the driver rejects disabled portals, allocates `isert_conn`, gets a shared RDMA device/PD, maps login buffers, negotiates initiator depth and send-with-invalidate support, creates CQ/QP, posts login receive, accepts the RDMA connection, and places the connection on the accepted list. ESTABLISHED moves it to pending and wakes `isert_accept_np()`, which binds it to an `iscsit_conn` and sets login socket information. Login receive completions copy request headers/payloads into target login buffers; login transmit sends response PDUs and, when login completes, allocates/posts full-feature RX descriptors and moves to `ISER_CONN_FULL_FEATURE`. Full-feature receive completions parse iSER control flags for read/write STag and VA, dispatch by iSCSI opcode, and call target-core setup/sequence helpers. SCSI Data-IN posts RDMA WRITE, optionally chained to a SCSI response send; SCSI Data-OUT posts RDMA READ and executes the command on completion. Control responses are sent via normal send WRs, with completion work used for task management/logout/text/reject post-handlers.

State and persistence: Shared `isert_device` objects persist in `device_list` by RDMA node GUID and own PD plus PI capability. Per-listener `isert_np` owns the RDMA listening id, semaphore, and accepted/pending lists. Per-connection `isert_conn` stores state, negotiation values, PI support, login buffers, RX descriptor pool, target connection pointer, QP/CQ, kref, completions, release work, logout flag, remote invalidation capability, and device-removal wait state. Per-command `isert_cmd` stores remote STags/VAs, invalidation rkey, mapped PDU payload DMA, RDMA RW context, embedded TX descriptor, RX descriptor ownership, and completion work.

Dependencies and integration: Depends on RDMA CM/verbs, `rdma_rw` helpers, target-core `se_cmd`, iscsi target transport APIs, Linux workqueues, krefs, and SCSI/T10-PI metadata. It integrates with target-core through `iscsit_transport`, command sequencing, dataout timers, session command counters, and target command execution/failure callbacks.

Risks: Connection lifetime is complex: accepted/pending lists, krefs, release work, RDMA CM callbacks, device removal waits, and target-core teardown must agree. `isert_free_np()` has an explicit workaround for connections that completed RDMA establishment but never started iscsi login; listener shutdown should be stress tested. `isert_put_unsol_pending_cmds()` uses a static `drop_cmd_list`, which is unusual and should be reviewed under concurrent connection teardown. `isert_exit()` destroys `isert_login_wq` after flushing it and then destroys it again after unregistering the transport, which is a notable teardown risk in this code snapshot. Data receive paths return after `iscsit_*` helpers but do not always repost RX descriptors immediately because command ownership controls reposting; leaks/starvation can occur if error paths miss cleanup. Test signals include connect reject/accept, login multi-PDU flow, full-feature transition, READ and WRITE with RDMA WRITE/READ, immediate and unsolicited Data-Out, PI offload errors, send-with-invalidate negotiation, logout wait, abort/TMF/reject/text responses, RDMA errors, listener shutdown with pending connections, device removal, and module unload workqueue teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/isert/ib_isert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/isert/ib_isert.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/isert/ib_isert.h

Purpose: Defines private structures, constants, inline buffer helpers, connection states, descriptor types, and debug macros for the iSER target implementation.

Important APIs/types/functions: Major types are `iser_rx_desc`, `iser_tx_desc`, `isert_cmd`, `isert_conn`, `isert_device`, and `isert_np`. Inline helpers convert CQEs to descriptors (`cqe_to_rx_desc()`, `cqe_to_tx_desc()`), recover `isert_cmd` from TX descriptors, and compute aligned iSER/iSCSI header/data offsets in RX buffers (`isert_get_iser_hdr()`, `isert_get_hdr_offset()`, `isert_get_iscsi_hdr()`, `isert_get_data()`). Constants define PDU sizes, QP send/recv DTO budgets, minimum posted RX threshold, and SG table limits.

Control flow: RX buffers allocate extra space so the data payload can be 512-byte aligned after iSER and iSCSI headers. TX descriptors carry a control or Data-IN response header plus optional second payload SGE. `isert_cmd` links target-core command state to one RX descriptor, one TX descriptor, remote keys/addresses, and an RDMA RW context. `isert_conn` models state transitions from INIT through UP, BOUND, FULL_FEATURE, TERMINATING, and DOWN.

State and persistence: Header structs define all persistent runtime state for the target transport: listener accepted/pending lists, per-device PD/refcount, per-connection login/RX/QP/CQ/kref/work state, and per-command RDMA state. `in_use` on RX descriptors prevents double reposting.

Dependencies and integration: Includes RDMA verbs/CM/RW helpers and the shared iSER protocol header. It is consumed only by `ib_isert.c` and matches target-core private command allocation through `priv_size = sizeof(struct isert_cmd)`.

Risks: RX header/data alignment math is critical; any change to `ISER_RX_SIZE`, `ISER_HEADERS_LEN`, or descriptor layout can break 512-byte payload alignment. QP constants assume `ISCSI_DEF_XMIT_CMDS_MAX` is a power of two and that send/recv WR budgets match implementation behavior. Test signals include build coverage, alignment assertions from `isert_get_data()`, RX repost idempotence, PI and non-PI command struct paths, and state-machine transition coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/isert/ib_isert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/Kconfig

Purpose: Defines Kconfig symbols for the RDMA Transport (RTRS) core, client, and server modules.

Important APIs/types/functions: Symbols are `INFINIBAND_RTRS` as an internal tristate core, `INFINIBAND_RTRS_CLIENT` as the user-visible "RTRS client module", and `INFINIBAND_RTRS_SERVER` as the user-visible "RTRS server module". Both client and server select the core.

Control flow: Selecting either client or server enables the shared RTRS core. The help text describes the client as a reliable RDMA transport and multipathing layer intended for a block storage initiator, and the server as the request processor for consumers such as RNBD server.

State and persistence: Build-time state only; no runtime state.

Dependencies and integration: All symbols depend on `INFINIBAND_ADDR_TRANS`, reflecting RDMA address translation requirements. The client/server options integrate with the Makefile aggregates for `rtrs-client.o`, `rtrs-server.o`, and `rtrs-core.o`.

Risks: Because the core is selected rather than user-visible, dependency drift in client/server can hide build failures. Test signals include client-only, server-only, both-enabled, and dependency-disabled kernel configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/Makefile

Purpose: Defines Kbuild object aggregation for RTRS core, client, server, stats, sysfs, and trace components.

Important APIs/types/functions: `rtrs-client-y` includes `rtrs-clt.o`, `rtrs-clt-stats.o`, `rtrs-clt-sysfs.o`, and `rtrs-clt-trace.o`. `rtrs-server-y` includes corresponding server objects. `rtrs-core-y` includes `rtrs.o`. Trace objects add `-I$(src)` so generated trace headers can include local files.

Control flow: Kbuild links aggregates into `rtrs-core.o`, `rtrs-client.o`, and `rtrs-server.o` according to `CONFIG_INFINIBAND_RTRS`, `CONFIG_INFINIBAND_RTRS_CLIENT`, and `CONFIG_INFINIBAND_RTRS_SERVER`.

State and persistence: Build metadata only.

Dependencies and integration: Couples the client sysfs/stats/trace helper files to the main client object and mirrors that layout for the server. The local include flag is required by Linux tracepoint generation patterns.

Risks: Omitting trace CFLAGS can break trace include generation. Missing object entries silently drop sysfs/stats/trace behavior. Test signals include modular and built-in builds, tracepoint compilation, and modpost symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt-stats.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt-stats.c

Purpose: Implements RTRS client statistics collection, formatting, reset operations, and per-path stats allocation.

Important APIs/types/functions: Exports `rtrs_clt_update_wc_stats()`, `rtrs_clt_inc_failover_cnt()`, string formatters for CPU migration, reconnects, and RDMA stats, reset helpers for RDMA/CPU migration/reconnect/all stats, `rtrs_clt_update_all_stats()`, and `rtrs_clt_init_stats()`.

Control flow: Work completion stats compare `con->cpu` with `raw_smp_processor_id()`; if completion migrated, the current CPU's `to` counter increments and the original CPU's atomic `from` counter increments. RDMA update adds request user/data lengths to per-CPU READ or WRITE totals and increments `inflight` for min-inflight multipath policy. Formatters aggregate per-CPU counters into sysfs strings. Reset helpers require an enabled boolean, zero selected per-CPU/global stats, and reset `inflight` for reset-all.

State and persistence: `rtrs_clt_stats` owns per-CPU stats, reconnect counters, and an atomic inflight counter. `rtrs_clt_init_stats()` allocates per-CPU memory and initializes `successful_cnt` to `-1` until the first session establishment sets it to zero.

Dependencies and integration: Depends on `rtrs-clt.h` structures, Linux percpu counters, atomics, and sysfs formatting helpers. The sysfs file uses these formatter/reset functions through `STAT_ATTR` declarations in `rtrs-clt-sysfs.c`; client IO paths call update functions.

Risks: Mixed atomic and non-atomic per-CPU fields assume correct CPU-local access and serialization through `get_cpu_ptr()` or `this_cpu_*`. Resetting stats while IO updates are active can yield transient partial values. `inflight` is incremented here but must be decremented elsewhere in the client core; policy accounting tests need both sides. Test signals include CPU migration under IRQ/workqueue affinity changes, concurrent sysfs reads/resets during IO, failover counter increments, reconnect success/failure formatting, and per-CPU allocation failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt-stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt-sysfs.c

Purpose: Exposes RTRS client session and path controls/statistics through sysfs. It creates root client attributes, per-path kobjects, per-path stats kobjects, read-only path identity/state/latency attributes, and writable controls for reconnect, disconnect, remove path, add path, multipath policy, and reconnect-attempt limits.

Important APIs/types/functions: Public functions are `rtrs_clt_create_path_files()`, `rtrs_clt_destroy_path_files()`, `rtrs_clt_create_sysfs_root_files()`, and `rtrs_clt_destroy_sysfs_root()`. Attribute handlers include `max_reconnect_attempts_*`, `mpath_policy_*`, `add_path_*`, `rtrs_clt_state_show()`, `rtrs_clt_reconnect_store()`, `rtrs_clt_disconnect_store()`, `rtrs_clt_remove_path_store()`, HCA/address/latency show functions, and stats attributes built with `STAT_ATTR`.

Control flow: Root sysfs creation adds `max_reconnect_attempts`, `mpath_policy`, and `add_path` to the client device. Per-path creation formats the source/destination address as the kobject name, initializes the path kobject under `clt->kobj_paths`, creates the path attribute group, initializes a nested `stats` kobject, and creates the stats group; failures unwind by deleting/putting kobjects and removing groups. Destruction removes stats and path kobjects, using `sysfs_remove_file_self()` when a remove operation is initiated by the sysfs file itself. Store handlers parse integers or strings, validate input, and call client core operations.

State and persistence: Kobject lifetime is tied to `rtrs_clt_path` and `rtrs_clt_stats` through `ktype_sess.release` and `ktype_stats.release`. Path release calls `free_path()`. Stats release frees per-CPU stats and the stats object. Root files persist for the `rtrs_clt_sess` device lifetime; `clt->kobj_paths` is removed in root destroy.

Dependencies and integration: Depends on RTRS private/client/log headers, address parsing/formatting helpers, client core operations such as path create/remove/reconnect/close, stats formatter/reset helpers, and Linux kobject/sysfs APIs.

Risks: Kobject reference ordering is delicate; failed nested stats creation must not leak either kobject or free path state too early. Writable sysfs controls can race with path teardown and reconnect state changes, especially `remove_path` using self-removal. `mpath_policy_store()` accepts both numeric and string aliases; ambiguous input handling should be tested. Test signals include sysfs creation failure injection at each step, add/remove path from sysfs, reconnect/disconnect writes, policy alias parsing (`rr`, `mi`, `ml` and full names), reconnect-attempt boundary values -1 and 9999, concurrent stats reset/read with IO, and path object release after final kobject put.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt-trace.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt-trace.c

Purpose: Instantiates RTRS client tracepoints declared in `rtrs-clt-trace.h`.

Important APIs/types/functions: Defines `CREATE_TRACE_POINTS` after including RTRS helper headers, then includes `rtrs-clt-trace.h` to emit tracepoint definitions.

Control flow: There is no runtime logic beyond tracepoint registration generated by the kernel trace infrastructure. The file must include `rtrs.h` and `rtrs-clt.h` before the trace header so helper types and state names are visible.

State and persistence: Tracepoint metadata persists for module lifetime as generated by `define_trace.h`; no independent state is stored in this file.

Dependencies and integration: Depends on Linux tracepoint generation conventions and the Makefile's `CFLAGS_rtrs-clt-trace.o = -I$(src)`. The generated events are consumed by ftrace/perf/BPF tooling and emitted by client code call sites.

Risks: Include ordering is important: the trace header intentionally comes last. Missing local include path or duplicate `CREATE_TRACE_POINTS` definitions would break builds. Test signals include compiling with tracing enabled/disabled and verifying expected `rtrs_clt` events appear under tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt-trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt-trace.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt-trace.h

Purpose: Declares trace events for RTRS client connection/path state transitions and reconnect/error-recovery diagnostics.

Important APIs/types/functions: Defines `TRACE_SYSTEM rtrs_clt`, declares enum symbols for `RTRS_CLT_*` states, maps them through `show_rtrs_clt_state()`, declares event class `rtrs_clt_conn_class`, and instantiates `rtrs_clt_reconnect_work`, `rtrs_clt_close_conns`, and `rtrs_rdma_error_recovery` events via `DEFINE_CLT_CONN_EVENT()`.

Control flow: Each event takes a `struct rtrs_clt_path *`, captures the path state, reconnect attempts, session max reconnect attempts, fail/success reconnect counters, and kobject session/path name, then formats a trace line with symbolic state and counters.

State and persistence: The header stores no runtime state itself, but it defines trace event fields copied from `rtrs_clt_path`, `rtrs_clt_sess`, and path stats at the emission point.

Dependencies and integration: Depends on Linux tracepoint macros plus `rtrs-clt.h` definitions being visible in the translation unit that creates tracepoints. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE rtrs-clt-trace` match the local trace header build pattern.

Risks: The `memcpy()` of `kobject_name(&clt_path->kobj)` into a fixed `NAME_MAX` array assumes a valid, NUL-terminated name within bounds; trace output can be confusing if kobject lifetime is racing with path destruction. Enum mappings must stay synchronized with client state enum values. Test signals include trace event enablement during reconnect, close, and RDMA error recovery; state-name formatting for each enum; and build coverage when trace headers are included multiple times.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt-trace.h -->
