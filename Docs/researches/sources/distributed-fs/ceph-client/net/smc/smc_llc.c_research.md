# sources/distributed-fs/ceph-client/net/smc/smc_llc.c

## Purpose
`smc_llc.c` implements SMC-R Link Layer Control protocol handling. It sends and receives LLC messages for confirm-link, add-link, delete-link, test-link, confirm-rkey, and delete-rkey flows, manages local and remote LLC flow serialization, coordinates multi-link failover and redundancy state, exchanges RMB rkeys for new links, and registers LLC receive handlers with the SMC WR layer.

## Important APIs, Types, and Functions
The file defines packed wire structures for all LLC message variants and `struct smc_llc_qentry`. Public functions include `smc_llc_send_confirm_link()`, `smc_llc_send_add_link()`, `smc_llc_send_delete_link()`, `smc_llc_srv_delete_link_local()`, `smc_llc_lgr_init()`, `smc_llc_lgr_clear()`, `smc_llc_link_init()`, `smc_llc_link_active()`, `smc_llc_link_clear()`, `smc_llc_do_confirm_rkey()`, `smc_llc_do_delete_rkey()`, `smc_llc_flow_initiate()`, `smc_llc_flow_stop()`, `smc_llc_wait()`, `smc_llc_cli_add_link()`, `smc_llc_srv_add_link()`, `smc_llc_add_link_local()`, `smc_llc_eval_conf_link()`, and `smc_llc_init()`.

## Control Flow
Incoming WR completions enter `smc_llc_rx_handler()`, which validates length and enqueues messages. Responses are matched immediately to the active local flow; requests are processed on `system_highpri_wq`. Add-link flows allocate an alternate link, initialize RDMA state, map and register existing buffers, exchange rkeys through continuation messages for v1 or in v2 extensions, perform confirm-link handshakes, and update link-group type to single, symmetric, or asymmetric. Delete-link flows switch connections away from a link, send or forward delete messages, clear links, and may terminate the group or trigger a new asym add-link. Rkey flows run as remote or local flows and update the core rtoken table. Test-link work periodically sends keepalives and schedules link-down on timeout.

## State and Persistence
LLC state is held inside `struct smc_link_group`: event queue, delayed event pointer, flow lock, local and remote flow structs, wait queues, configuration rwsem, add/delete/event work items, testlink interval, and termination reason. Per-link state includes testlink delayed work and completion. This is all transient and tied to link-group lifetime.

## Dependencies and Integration Points
LLC depends on RDMA WR transmit/receive slot management, SMC core link and buffer APIs, IB QP state transitions, PNET alternate RoCE discovery, CLC constants, and core rtoken helpers. It is initialized through `smc_llc_init()` by registering WR receive handlers for v1 and v2 LLC message types. Core calls LLC for link-group initialization, link activation/clear, rkey registration/deletion, add-link invitations, and link-delete-all on termination.

## Risks
This file has dense concurrency: tasklet-context receive handling, workqueue request handling, wait queues, delayed events, local and remote flows, and `llc_conf_mutex` must agree. Unexpected parallel add/delete messages can be delayed or dropped; mistakes can deadlock link reconfiguration or lose a protocol message. Packed wire structure lengths differ between v1 and v2, and v2 shared receive buffers require copying before interpretation. Rkey exchange must stay synchronized with buffer lists and link indexes. Test-link false positives can tear down healthy links if completions are delayed.

## Test Signals
Run SMC-R v1 and v2 with one and two RoCE paths, add-link and delete-link initiated by client and server, asymmetric-to-symmetric transitions, link failure under load, rkey confirm/delete for newly allocated and freed RMBs, LLC protocol violation injection, testlink timeout, short/invalid LLC message drops, and high connection counts during add-link rkey exchange. Lockdep and fault injection around WR slot allocation are valuable.
