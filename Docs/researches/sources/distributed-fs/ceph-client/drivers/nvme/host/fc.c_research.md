# sources/distributed-fs/ceph-client/drivers/nvme/host/fc.c

## Purpose
This file implements the Linux NVMe over Fibre Channel host transport. It exposes the LLDD-facing registration API for FC local and remote ports, owns FC-NVMe association and connection setup through Link Service requests, maps blk-mq NVMe requests into FC-NVMe command IUs, handles completions and transport errors, and registers the `fc` NVMe fabrics transport. It also provides a temporary FC class device used for NVMe discovery uevents and optional blk-cgroup FC appid plumbing.

The file is the bridge between the generic NVMe core/fabrics layers and Fibre Channel low-level drivers. The NVMe core sees a `struct nvme_ctrl` with `nvme_ctrl_ops` and blk-mq operations; LLDDs see `struct nvme_fc_port_template` callbacks and `nvmefc_ls_req`, `nvmefc_ls_rsp`, and `nvmefc_fcp_req` work items.

## Important APIs, Types, And Functions
Exported LLDD entry points are `nvme_fc_register_localport()`, `nvme_fc_unregister_localport()`, `nvme_fc_register_remoteport()`, `nvme_fc_unregister_remoteport()`, `nvme_fc_rescan_remoteport()`, `nvme_fc_set_remoteport_devloss()`, `nvme_fc_rcv_ls_req()`, and `nvme_fc_io_getuuid()`. Module initialization registers `nvme_fc_transport` with `nvmf_register_transport()` so userspace can create controllers using `transport=fc`.

Core private objects are `struct nvme_fc_lport`, `struct nvme_fc_rport`, `struct nvme_fc_ctrl`, `struct nvme_fc_queue`, `struct nvmefc_ls_req_op`, `struct nvmefc_ls_rcv_op`, and `struct nvme_fc_fcp_op`. `struct nvme_fc_fcp_op` embeds `struct nvme_request` as its first member to satisfy NVMe core request-private layout requirements. Controller flags include `ASSOC_ACTIVE`, `ASSOC_FAILED`, and `FCCTRL_TERMIO`; queue flags include `NVME_FC_Q_CONNECTED` and `NVME_FC_Q_LIVE`.

Connection setup is centered on `nvme_fc_create_association()`, `nvme_fc_connect_admin_queue()`, `nvme_fc_connect_queue()`, `nvme_fc_create_io_queues()`, and `nvme_fc_recreate_io_queues()`. Request submission uses `nvme_fc_queue_rq()`, `nvme_fc_start_fcp_op()`, `nvme_fc_map_data()`, `nvme_fc_fcpio_done()`, `nvme_fc_complete_rq()`, and `nvme_fc_timeout()`. Error and lifecycle code includes `nvme_fc_error_recovery()`, `nvme_fc_delete_association()`, `__nvme_fc_abort_outstanding_ios()`, `nvme_fc_reset_ctrl_work()`, `nvme_fc_reconnect_or_delete()`, and `nvme_fc_delete_ctrl()`.

## Control Flow
LLDDs first register local ports with `nvme_fc_register_localport()`. The function validates required template callbacks, reattaches a previously deleted matching local port when possible, otherwise allocates a new lport, assigns a port number with `ida_alloc()`, stores LLDD private memory after the object, and adds it to `nvme_fc_lport_list`. Remote-port registration similarly reattaches suspended deleted rports within `dev_loss_tmo` or allocates a new rport under the local port, then emits discovery uevents for discovery-capable targets.

Controller creation starts from `nvme_fc_create_ctrl()`, which parses host and target FC WWN pairs from fixed-format traddr strings, finds matching online lport/rport objects, and calls `nvme_fc_init_ctrl()`. Controller initialization allocates `struct nvme_fc_ctrl`, initializes the admin queue, registers with the NVMe core, creates an admin tag set, links the controller to the rport, transitions to `NVME_CTRL_CONNECTING`, and queues `connect_work`.

`nvme_fc_create_association()` creates the link-side association and then makes the NVMe controller live. It creates the admin hardware queue through the LLDD, sends a Create Association LS, runs `nvmf_connect_admin_queue()`, enables and finishes the controller, checks FC-specific constraints such as no `icdoff` and mandatory SGL support, initializes AEN operations, creates and connects I/O queues, transitions to `NVME_CTRL_LIVE`, and starts the NVMe controller. On failure it sends Disconnect Association, clears association state, responds to any pending received disconnect LS, deletes hardware queues, clears active counters, and lets reconnect logic decide what happens next.

The blk-mq request path starts in `nvme_fc_queue_rq()`. It rejects nonready paths, builds the NVMe command with `nvme_setup_cmd()`, determines data direction from physical segments, and calls `nvme_fc_start_fcp_op()`. That helper checks remote-port liveness, gets a controller reference, fills FC-NVMe CMD IU fields including connection ID and CSN, maps request data into an SG table, syncs the command IU for DMA, marks the op active, starts the request, and hands it to `lport->ops->fcp_io()`. Completion returns through `nvme_fc_fcpio_done()`, which validates response lengths, ERSP IU fields, transfer length, command ID, and LLDD status before completing the NVMe request or scheduling reset.

Receive-side LS handling is asynchronous. `nvme_fc_rcv_ls_req()` copies the incoming request and allocates a response buffer, maps the response for DMA, queues the operation on `rport->ls_rcv_list`, and schedules `lsrcv_work`. `nvme_fc_handle_ls_rqst_work()` dispatches supported LS commands. Disconnect Association is validated, matched against an active controller association, and either rejected immediately or deferred until `nvme_fc_delete_association()` has aborted outstanding exchanges.

## State And Persistence
Persistent runtime state is in global lists and IDAs (`nvme_fc_lport_list`, `nvme_fc_local_port_cnt`, `nvme_fc_ctrl_cnt`), per-port krefs and active counters, rport LS request/receive/control lists, controller queue arrays, work items, and NVMe core state. State is in-memory only; link identifiers such as association ID, connection ID, queue CSN, controller number, port number, and dev-loss deadline are recreated as ports and controllers are registered or reconnected.

FC association state is deliberately split across link-side objects and NVMe core state. `ASSOC_ACTIVE` gates whether a controller currently owns an association on the rport; `ASSOC_FAILED` records connection failure while setup is in progress; `FCCTRL_TERMIO` tracks termination so aborted operations can decrement `iocnt` and wake `ioabort_wait`. Queue state uses connected/live bits plus LLDD queue handles. Rport state includes `dev_loss_end`, allowing remote-port deletion to trigger reconnect attempts until the timeout expires.

DMA mappings are per LS request, per received LS response, per request command IU/response IU, and per data SG table. The fcloop special case passes `dev == NULL`; wrapper helpers intentionally no-op or pseudo-map DMA for that mode.

## Dependencies And Integration Points
The file depends on NVMe core and fabrics helpers from `nvme.h` and `fabrics.h`, FC-NVMe wire structures from UAPI FC headers and `linux/nvme-fc.h`, LLDD contracts from `linux/nvme-fc-driver.h`, blk-mq, DMA mapping, SCSI FC transport naming, sysfs/device class APIs, krefs, IDAs, workqueues, timers, and optional blk-cgroup appid support.

Important integration points include LLDD callbacks (`localport_delete`, `remoteport_delete`, `ls_req`, `ls_abort`, `xmt_ls_rsp`, `create_queue`, `delete_queue`, `fcp_io`, `fcp_abort`, `map_queues`), NVMe fabrics connect helpers, NVMe core controller lifecycle, request timeout/error handling, discovery uevents, and sysfs attributes under the temporary `fc` class.

## Risks
The highest risk is lifecycle concurrency. Local ports, remote ports, controllers, LS requests, received LS operations, AENs, blk-mq requests, reconnect work, reset work, and module exit all hold independent references and locks. Bugs can produce use-after-free, stale LLDD handles, double delete callbacks, stuck reconnects, or IO that never completes.

Protocol correctness is also sensitive. Create Association/Create Connection accept responses are manually validated by descriptor tags, lengths, command echo, association IDs, and connection IDs. Any missing validation or endian mistake can make host and target disagree about association state. Disconnect Association is intentionally asynchronous and deferred after ABTS, which is correct for cleanup but makes ordering fragile.

Request completion is strict about transfer length, ERSP IU length, response result, and command ID. Invalid responses schedule controller reset, which is safe but can amplify transient LLDD bugs into repeated reconnects. Timeout handling starts an LLDD abort and returns `BLK_EH_RESET_TIMER`; if the LLDD never completes the aborted exchange, teardown can wait indefinitely.

Other risks include traddr parser assumptions, global discovery list retry limits, no-op DMA behavior for NULL devices differing from real DMA behavior, and optional appid parsing accepting only a narrow `hex:appid` shape.

## Test Signals
Useful tests include LLDD port register/unregister/re-register, remote-port dev-loss and reappearance, discovery uevent contents, controller create/delete by FC traddr, duplicate connect rejection, admin and I/O queue connection validation, reconnect after remote-port loss, reconnect timeout expiry, module unload with live controllers, received Disconnect Association LS during normal I/O, and LS abort during remote-port deletion.

I/O tests should cover reads, writes, compare, no-data commands, write zeroes with no physical payload, AEN submission, request timeout and abort completion, LLDD `fcp_io()` returning `-EBUSY` versus hard errors, bad ERSP lengths, bad transferred lengths, and blkcg appid retrieval when `CONFIG_BLK_CGROUP_FC_APPID` is enabled. Runtime signals include lockdep, KASAN, refcount warnings, stuck workqueues, controller state transitions, queue live/connected bits, and FC target logs for association/connection IDs.
