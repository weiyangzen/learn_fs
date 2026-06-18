<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/ibmvscsi_tgt.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/ibmvscsi_tgt.c

## Purpose

`ibmvscsi_tgt.c` is the IBM POWER virtual SCSI server/target fabric driver. It binds to VIO `"v-scsi-host"` devices, registers an LIO/TCM target fabric named `ibmvscsis`, accepts SRP requests from a client partition over CRQ, copies SRP IUs and data through PHYP RDMA hypercalls, submits SCSI CDBs and task-management requests into Target Core, and returns SRP responses to the client.

## Important APIs, Types, and Functions

- Module/global configuration includes `IBMVSCSIS_VERSION`, `INITIAL_SRP_LIMIT`, `DEFAULT_MAX_SECTORS`, `MAX_TXU`, `max_vdma_size`, `system_id`, `partition_name`, and `partition_number`.
- Adapter lifecycle: `ibmvscsis_probe()`, `ibmvscsis_remove()`, `ibmvscsis_init()`, and `ibmvscsis_exit()`.
- CRQ and transport state: `ibmvscsis_create_command_q()`, `ibmvscsis_destroy_command_q()`, `ibmvscsis_enable_change_state()`, `ibmvscsis_establish_new_q()`, `ibmvscsis_reset_queue()`, `ibmvscsis_free_command_q()`, and `ibmvscsis_unregister_command_q()`.
- Interrupt handling: `ibmvscsis_interrupt()` disables interrupts and schedules `work_task`; `ibmvscsis_handle_crq()` drains CRQ entries; `ibmvscsis_poll_cmd_q()` covers arrivals while interrupts were disabled.
- State machine helpers: `ibmvscsis_post_disconnect()`, `ibmvscsis_disconnect()`, `ibmvscsis_adapter_idle()`, `ibmvscsis_trans_event()`, `ibmvscsis_ready_for_suspend()`, and `connection_broken()`.
- Protocol handlers: `ibmvscsis_init_msg()`, `ibmvscsis_mad()`, `ibmvscsis_process_mad()`, `ibmvscsis_adapter_info()`, `ibmvscsis_cap_mad()`, `ibmvscsis_srp_login()`, `ibmvscsis_srp_i_logout()`, `ibmvscsis_srp_cmd()`, and `ibmvscsis_parse_command()`.
- Target Core integration: `ibmvscsis_parse_cmd()`, `ibmvscsis_parse_task()`, `ibmvscsis_write_pending()`, `ibmvscsis_queue_data_in()`, `ibmvscsis_queue_status()`, `ibmvscsis_queue_tm_rsp()`, `ibmvscsis_release_cmd()`, and `ibmvscsis_aborted_task()`.
- Data movement: `ibmvscsis_copy_crq_packet()` copies the SRP IU from client memory into a local SRP buffer; `ibmvscsis_rdma()` copies payload data between client descriptors and target scatterlists; `srp_build_response()` constructs an SRP_RSP and copies it back to the client.
- Configfs fabric functions: `ibmvscsis_make_tport()`, `ibmvscsis_drop_tport()`, `ibmvscsis_make_tpg()`, `ibmvscsis_drop_tpg()`, `ibmvscsis_enable_tpg()`, and `ibmvscsis_wwn_version_show()`.

## Control Flow

Module init gathers system Open Firmware metadata, registers a sysfs class, registers the Target Core fabric template, then registers the VIO driver. Probe allocates `struct scsi_info`, reads local and remote DMA window LIOBNs, adds the adapter to a global list for configfs lookup, allocates an SRP IU pool and matching command pool sized by `INITIAL_SRP_LIMIT`, creates the CRQ page, maps a scratch page for partner info, initializes tasklet/completions/workqueue/timer, requests the VIO IRQ, and starts in `WAIT_ENABLED`.

The target portal group is enabled through configfs. `ibmvscsis_enable_tpg(true)` registers the CRQ with PHYP, moves to `WAIT_CONNECTION`, enables interrupts, checks for an early init message, and sends an init message if needed. Init complete moves the adapter to `CONNECTED`. SRP login validates IU length, port IDs, multichannel flags, and descriptor format support, creates a Target Core session nexus, sends login response or rejection, and moves to `SRP_PROCESSING` on success.

For normal I/O, the CRQ tasklet copies the client IU through `H_COPY_RDMA`, parses it, obtains a free command and IU entry, increments debit for request-limit accounting, queues work, and the workqueue calls either `target_submit_cmd()` for SCSI CDBs or `target_submit_tmr()` for task management. Target Core callbacks perform write data-in from the client before execution, read data-out to the client after execution, build SRP responses, and place responses on `waiting_rsp`. `ibmvscsis_send_messages()` sends CRQ response notices in order and handles full response queues with an hrtimer retry.

Disconnect and recovery are explicit state-machine work. Transport events, PHYP RDMA errors, full queues, client failure pings, unconfigure, and suspend/resume events all funnel through `ibmvscsis_post_disconnect()`. The queued disconnect worker waits for active/scheduled/waiting commands to drain when required, calls `ibmvscsis_adapter_idle()`, and either frees the CRQ, resets/re-registers it, waits for reconnection, or completes device removal.

## State and Persistence

Runtime state lives in `struct scsi_info`, especially `state`, `flags`, `cmd_q`, `request_limit`, `credit`, `debit`, `waiting_rsp`, `schedule_q`, `active_q`, `free_cmd`, `client_data`, `client_cap`, DMA window data, timers, workqueue, Target Core tport/nexus, and the SRP target pool. The state constants distinguish no queue, enabled-but-not-connected, connected, SRP processing, wait-idle, error disconnect, reconnect, disconnected, unconfiguring, and undefined. Flag bits record MAD exclusivity, queue closure, client failure, transport events, response-queue-down, pending disconnect work, suspend preparation, and PHYP lock-release accounting.

There is no disk persistence. System identity and partition data are read from the device tree at module init and exposed via the `ibmvscsis` class attributes. Client data is learned from PHYP partner info and adapter-info MADs and is cleared selectively when the client closes.

## Dependencies and Integration Points

The file depends on PowerPC VIO/PHYP hypercalls (`H_REG_CRQ`, `H_FREE_CRQ`, `H_SEND_CRQ`, `H_COPY_RDMA`, `H_VIOCTL`, suspend-related VIOCTLs), Linux Target Core fabric APIs, configfs fabric registration, DMA mapping, hrtimers, tasklets, workqueues, Open Firmware properties, and SRP/VIOSRP protocol definitions. It uses `libsrp.c` helpers for IU pool allocation and SRP descriptor data transfer.

The external control plane is configfs: an admin creates a fabric WWN matching a VIO device name, creates a `tpgt_N`, maps LUNs through Target Core, and enables the TPG. VIO probe alone allocates the adapter but does not make it serve I/O until the TPG is enabled.

## Risks and Edge Cases

- The state machine is complex and lock-sensitive. `ibmvscsis_free_command_q()` intentionally drops `intr_lock` around PHYP calls and records `phyp_acr_state`/`phyp_acr_flags` to avoid losing concurrent disconnect requests.
- CRQ interrupts are edge-triggered; both tasklet and polling paths recheck after reenabling interrupts to avoid stranded entries.
- Request-limit accounting uses `debit`, `credit`, and SRP response `req_lim_delta`; mismatches can let clients overrun command resources or stall.
- Response queue full (`H_DROPPED`) handling can wait indefinitely during SRP processing but is bounded during unconfigure-like cases by `MAX_TIMER_POPS`.
- PHYP RDMA failures must distinguish malformed descriptors from client failure. Several paths use `connection_broken()` ping to decide whether to mark `CLIENT_FAILED`.
- `ibmvscsis_rdma()` must correctly walk both client memory descriptors and server scatterlists while respecting `max_vdma_size`.
- Login rejection still needs an SRP response notice; failures while copying rejection/response must schedule disconnects.
- Target Core task-management ordering is subtle: abort responses can be delayed behind the command being aborted by `abort_cmd` and `DELAY_SEND`.
- Remove waits on `unconfig`; losing a disconnect transition can hang removal, which is why PHYP accounting exists.

## Test Signals

Build and load tests should show class registration, Target Core fabric registration, and VIO driver binding. Configfs tests should be able to create a WWN matching `dev_name(&vdev->dev)`, create/enable `tpgt_N`, and observe CRQ registration plus init/login. Functional tests should cover read/write data movement, task management abort and LUN reset, client logout, response queue full retry, partner failure/migration transport events, prepare/resume suspend events, unconfigure while active I/O is outstanding, and removal without waiting forever. Error-injection around `H_COPY_RDMA`, `H_SEND_CRQ`, and DMA mapping should produce disconnect/reconnect or clean failure without leaking command/IU resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/ibmvscsi_tgt.c -->
