# Research: subset-b-005269

Grouped research for IBM virtual SCSI client/server sources, the shared SRP target helper, and the Iomega MatchMaker parallel-port SCSI host adapter. Each section is bounded by the exact source-path markers required by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/ibmvscsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/ibmvscsi.c

## Purpose

`ibmvscsi.c` is the IBM POWER virtual SCSI initiator driver. It presents a Linux `Scsi_Host` for a VIO `"vscsi"` device and speaks SRP over the platform Command/Response Queue (CRQ) hypervisor transport. The driver converts SCSI midlayer commands into SRP information units, advertises client capabilities through VIOSRP management datagrams, handles partition migration and adapter reset events, and exposes host metadata through SRP transport/sysfs attributes.

## Important APIs, Types, and Functions

- Module parameters tune topology and behavior: `max_id`, `max_channel`, `init_timeout`, `max_requests`, `fast_fail`, and `client_reserve`.
- `ibmvscsi_init_crq_queue()`, `ibmvscsi_reset_crq_queue()`, `ibmvscsi_reenable_crq_queue()`, and `ibmvscsi_release_crq_queue()` own CRQ page allocation, DMA mapping, hypervisor `H_REG_CRQ`/`H_FREE_CRQ`/`H_ENABLE_CRQ`, IRQ setup, tasklet setup, and teardown.
- `initialize_event_pool()`, `get_event_struct()`, and `free_event_struct()` manage the fixed pool of SRP event slots and coherent IU storage used as CRQ correlation tokens.
- `ibmvscsi_queuecommand_lck()` builds SRP_CMD IUs, maps scatterlists with `scsi_dma_map()`, formats direct or indirect SRP descriptors, and sends the event through `ibmvscsi_send_srp_event()`.
- `ibmvscsi_send_srp_event()` enforces server request-limit credit, reserves final slots for task management, copies the IU into DMA-visible storage, links the event into `hostdata->sent`, installs optional timers, and calls `H_SEND_CRQ`.
- `ibmvscsi_handle_crq()` dispatches initialization messages, transport events, and command responses. It validates correlation tokens against the event pool, updates request credits, calls the event completion callback, removes the event from `sent`, and frees it.
- Management sequence functions include `send_mad_adapter_info()`, `adapter_info_rsp()`, `enable_fast_fail()`, `send_mad_capabilities()`, `capabilities_rsp()`, `send_srp_login()`, and `login_rsp()`.
- Error recovery hooks are `ibmvscsi_eh_abort_handler()`, `ibmvscsi_eh_device_reset_handler()`, `ibmvscsi_eh_host_reset_handler()`, and `ibmvscsi_host_reset()`.
- Probe/remove and runtime integration are handled by `ibmvscsi_probe()`, `ibmvscsi_remove()`, `ibmvscsi_resume()`, `ibmvscsi_module_init()`, and `ibmvscsi_module_exit()`.

## Control Flow

Probe allocates a SCSI host, maps persistent capabilities and adapter-info buffers, starts a reset work thread, registers and enables the CRQ, initializes the event pool, registers with the SCSI midlayer and SRP transport, sends the initial CRQ init message, waits up to `init_timeout` for a positive request limit, and scans the host if login completed.

CRQ interrupts are edge-oriented. `ibmvscsi_handle_event()` disables VIO interrupts and schedules `srp_task`; `ibmvscsi_task()` drains all valid CRQ entries, clears their valid bits with barriers, reenables interrupts, and rechecks the queue to avoid losing arrivals between drain and enable.

The normal I/O path is SCSI midlayer `queuecommand` -> event allocation -> SRP_CMD construction -> data descriptor mapping -> request-limit accounting -> `H_SEND_CRQ` -> CRQ response interrupt -> `handle_cmd_rsp()` -> SCSI completion. For multiple SG entries, the driver embeds up to `MAX_INDIRECT_BUFS` descriptors in the IU and allocates an external coherent descriptor table for larger lists, using the table descriptor VA to point either into the IU or the external table.

Initialization is a management handshake: adapter info is exchanged first; AIX servers may get an enable-fast-fail MAD; then capabilities are exchanged; finally SRP login negotiates the request-limit delta and unblocks queued SCSI requests. CRQ transport events block SCSI requests and either reenable after migration (`format == 0x06`) or reset the CRQ. The kthread serializes reset, reenable, and unblock actions outside interrupt context.

## State and Persistence

Persistent per-adapter state lives in `struct ibmvscsi_host_data`: CRQ queue, event pool, `sent` list, request-limit atomic, action state for the work thread, cached MAD adapter information, capabilities, and DMA addresses for persistent MAD buffers. Module-global state stores local partition name/number and the adapter list. There is no on-disk persistence; state is recreated at probe and module load. Runtime-visible state is exposed through SCSI host attributes such as `vhost_loc`, `vhost_name`, `srp_version`, `partition_name`, `partition_number`, `mad_version`, and `os_type`.

`request_limit` is the main flow-control state. It starts at `-1`, moves to `0` while login is pending, and is set to the server-provided delta after `SRP_LOGIN_RSP`; responses add their `req_lim_delta`. Reset paths set it back to `0` or `-1` and purge outstanding requests.

## Dependencies and Integration Points

The file depends on PowerPC VIO and PHYP hypercalls (`H_SEND_CRQ`, `H_REG_CRQ`, `H_FREE_CRQ`, `H_ENABLE_CRQ`), Open Firmware properties for partition metadata and location codes, Linux DMA mapping APIs, tasklets, kthreads, timers, SCSI midlayer APIs, and `scsi_transport_srp`. Protocol definitions come from `<scsi/viosrp.h>` and the local `ibmvscsi.h`.

The driver registers a `vio_driver` for `"IBM,v-scsi"`, a `scsi_host_template`, and an SRP transport template. It reports desired DMA memory to VIO through `get_desired_dma()`.

## Risks and Edge Cases

- Request credit accounting is concurrency-sensitive. `ibmvscsi_send_srp_event()` assumes `host_lock` protection, and the final two request slots are reserved for reset/abort except for very small server limits.
- Correlation tokens are raw event pointers echoed by the hypervisor/server. The file validates pointer range/alignment and free state, but stale or duplicate tokens are serious protocol errors.
- The CRQ interrupt path relies on memory barriers around valid bits and on drain/reenable/recheck sequencing to avoid lost edge-triggered interrupts.
- External indirect descriptor allocation can fail under constrained memory; CMO firmware suppresses some error logs but returns busy.
- Timeout handling for internal commands resets the whole adapter connection.
- Probe error paths must unwind in the right order: CRQ, tasklet, kthread, persistent DMA mappings, event pool, SCSI host, and SRP transport.
- Migration and partner failure handling purposely purges or requeues requests; regressions here can cause hangs during LPAR mobility or stale I/O completions.

## Test Signals

Useful validation signals include successful module load only when `FW_FEATURE_VIO` is present, CRQ init/login logs, `SRP_LOGIN succeeded`, nonzero request-limit before scan, SCSI scan/device discovery, host sysfs attributes populated with server adapter data, clean unload with no event-pool in-use warning, abort/LUN reset paths returning `SUCCESS`, simulated `H_CLOSED` causing host-busy/retry, migration CRQ causing reenable and re-login, and DMA mapping failure tests returning busy without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/ibmvscsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/ibmvscsi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/ibmvscsi.h

## Purpose

`ibmvscsi.h` defines the private data structures and constants for the IBM POWER virtual SCSI initiator driver. It bridges Linux SCSI host state, SRP events, VIO CRQ transport state, and persistent VIOSRP management buffers used by `ibmvscsi.c`.

## Important APIs, Types, and Constants

- `MAX_INDIRECT_BUFS` is the number of SRP direct descriptors that can be embedded alongside an indirect descriptor in `struct srp_cmd::add_data`.
- Queue and capacity defaults include `IBMVSCSI_MAX_REQUESTS_DEFAULT`, `IBMVSCSI_CMDS_PER_LUN_DEFAULT`, `IBMVSCSI_MAX_SECTORS_DEFAULT`, `IBMVSCSI_MAX_CMDS_PER_LUN`, and `IBMVSCSI_MAX_LUN`.
- `struct crq_queue` stores the DMA-mapped CRQ ring, current consumer index, DMA token, size, and spinlock.
- `struct srp_event_struct` is the per-request event slot. It contains the coherent transfer IU pointer, local IU image, associated `scsi_cmnd`, CRQ header, completion callback, SCSI completion callback, list node, timer, optional sync response pointer, and optional external indirect descriptor list.
- `struct event_pool` owns the event-slot array and coherent IU storage.
- `enum ibmvscsi_host_action` defines deferred work actions: none, reset, reenable, and unblock.
- `struct ibmvscsi_host_data` is the per-adapter aggregate: adapter list node, request-limit atomic, migration flag, current action, device pointer, event pool, CRQ queue, tasklet, sent list, SCSI host, work thread/waitqueue, MAD adapter info, capabilities buffer, and DMA addresses for persistent MAD data.

## Control Flow and State

The header does not implement logic, but its fields encode the driver control model. `crq_queue` is consumed by the interrupt tasklet. `event_pool` slots are allocated under SCSI host locking, sent through the CRQ, and returned from `ibmvscsi_handle_crq()` by pointer correlation. `ibmvscsi_host_data::action` is the handoff from interrupt/error contexts to the kthread that performs reset, reenable, or unblock work. `caps_addr` and `adapter_info_addr` keep pre-mapped management buffers available for login-time MAD exchange.

## Dependencies and Integration Points

The header imports Linux list/completion/interrupt primitives and `<scsi/viosrp.h>`, and forward-declares `struct scsi_cmnd` and `struct Scsi_Host`. All structures are internal to the `ibmvscsi` initiator and are consumed by the implementation file rather than exported as a public API.

## Risks and Edge Cases

- `srp_event_struct` embeds both local and DMA-visible IU pointers; confusing `iu`, `xfer_iu`, and `sync_srp` can cause stale DMA payloads or use-after-completion.
- `MAX_INDIRECT_BUFS` must remain consistent with the space available in the SRP IU additional data area.
- `request_limit` and `sent` list semantics depend on external locking in the C file, not on encapsulation in the structures.
- The host action enum is intentionally small; new actions must be handled in the work-thread predicates and dispatcher.

## Test Signals

Compile-time structure layout checks in `ibmvscsi.c` (`BUILD_BUG_ON(sizeof(evt_struct->iu.srp) != SRP_MAX_IU_LEN)`) indirectly validate these definitions. Runtime tests should exercise embedded and external indirect descriptor paths, kthread action transitions, and event pool exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/ibmvscsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/Makefile

## Purpose

This Kbuild makefile builds the IBM virtual SCSI target/server module when `CONFIG_SCSI_IBMVSCSIS` is enabled. It combines the target fabric implementation and the local SRP helper into one module object.

## Important APIs and Build Rules

- `obj-$(CONFIG_SCSI_IBMVSCSIS) += ibmvscsis.o` selects the module or built-in object according to the kernel configuration.
- `ibmvscsis-y := libsrp.o ibmvscsi_tgt.o` links `libsrp.o` and `ibmvscsi_tgt.o` into the final `ibmvscsis` composite object.

## Control Flow, State, and Persistence

There is no runtime control flow or persistent state. The only behavior is build composition. Because `libsrp.c` is linked into `ibmvscsis`, its non-static symbols are available to `ibmvscsi_tgt.c` without creating a separate module dependency.

## Dependencies and Integration Points

The file integrates with Linux Kbuild and the kernel config symbol `CONFIG_SCSI_IBMVSCSIS`. It assumes `libsrp.c`, `libsrp.h`, `ibmvscsi_tgt.c`, and `ibmvscsi_tgt.h` are in the same directory.

## Risks and Edge Cases

- Any rename or split of `libsrp.o` or `ibmvscsi_tgt.o` must update this composition rule or the module will fail to link.
- Since `libsrp` is not built as a separately selectable object here, other users cannot depend on it through this makefile without refactoring.

## Test Signals

Build coverage is the key signal: enabling `CONFIG_SCSI_IBMVSCSIS=m` should produce `ibmvscsis.ko`; enabling it built-in should include both object files in vmlinux. Link errors around `srp_transfer_data`, `srp_target_alloc`, or target fabric callbacks indicate this rule or object ordering is broken.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/Makefile -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/ibmvscsi_tgt.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/ibmvscsi_tgt.h

## Purpose

`ibmvscsi_tgt.h` defines the private protocol constants, state flags, command structures, target-port structures, DMA-window metadata, and hypervisor-call wrappers used by the IBM virtual SCSI target driver.

## Important APIs, Types, and Constants

- Queue sizing: `MAX_CMD_Q_PAGES`, `CRQ_PER_PAGE`, `DEFAULT_CMD_Q_SIZE`, `MAX_CMD_Q_SIZE`, `MAX_NUM_PORTS`, `MAX_H_COPY_RDMA`, and `MAX_EYE`.
- Protocol support constants include `SUPPORTED_FORMATS`, `SRP_VIOLATION`, `SCSI_LUN_ADDR_METHOD_FLAT`, `SRP_VERSION`, message word indexes, and solicited-notification bit positions.
- `struct dma_window` and `struct target_dds` store local/remote DMA window LIOBNs plus partition identity used by `H_COPY_RDMA`.
- `struct client_info` caches client SRP, partition, MAD, and OS metadata.
- `struct timer_cb` tracks the hrtimer used to retry responses when the client CRQ is full.
- `struct cmd_queue` represents the DMA-mapped CRQ ring.
- `enum cmd_type`, `struct iu_rsp`, and `struct ibmvscsis_cmd` describe command pool entries and their Target Core `se_cmd` embedding.
- `struct ibmvscsis_nexus` wraps the Target Core session; `struct ibmvscsis_tport` wraps the fabric WWN/TPG state.
- `struct scsi_info` is the core per-adapter state object with lists, flags, locks, queue metadata, request credits, client info, workqueue, completions, VIO device pointer, SRP target pool, target port, and tasklet/work items.
- State/flag macros such as `NO_QUEUE`, `WAIT_ENABLED`, `WAIT_CONNECTION`, `CONNECTED`, `SRP_PROCESSING`, `UNCONFIGURING`, `WAIT_IDLE`, `ERR_DISCONNECT`, `ERR_DISCONNECT_RECONNECT`, `ERR_DISCONNECTED`, `UNDEFINED`, `RESPONSE_Q_DOWN`, `CLIENT_FAILED`, and `PREP_FOR_SUSPEND_*` define the adapter state machine.
- Hypercall wrappers `h_copy_rdma`, `h_vioctl`, `h_reg_crq`, `h_free_crq`, and `h_send_crq` wrap `plpar_hcall_norets()`.

## Control Flow and State

The header encodes the target driver's state machine. `TARGET_STOP()` combines terminal/disconnecting states and scheduling flags so the interrupt handler can stop consuming CRQ entries. `IS_DISCONNECTING`, `DONT_PROCESS_STATE`, `BLOCK`, `PREP_FOR_SUSPEND_FLAGS`, and `PRESERVE_FLAG_FIELDS` make disconnect and suspend behavior consistent across the implementation.

Command lifecycle state moves through `free_cmd`, `schedule_q`, `active_q`, and `waiting_rsp`; each `ibmvscsis_cmd` carries the SRP IU entry, Target Core command, response tag/format/length, optional abort relationship, and flags for fast-fail or delayed send. `scsi_info` also records PHYP lock-release accounting fields to preserve state changes made while the command queue lock is dropped.

## Dependencies and Integration Points

The header includes Linux interrupt primitives, the local `libsrp.h`, Target Core types via the implementation, and SRP/VIOSRP structures through included helper headers. It is tightly coupled to `ibmvscsi_tgt.c` and not a general exported kernel interface.

## Risks and Edge Cases

- State and flag values are bit masks used in compound tests; changing values can silently alter `TARGET_STOP()` or disconnect behavior.
- `struct scsi_info` contains copied `struct device` and a VIO device pointer; lifecycle ordering must keep both valid for sysfs, DMA, IRQ, and workqueue operations.
- The `vio_iu()` macro assumes every `iu_entry` has a valid `sbuf` and SRP buffer.
- `READ_CMD` and `WRITE_CMD` use opcode low bits for fast-fail heuristics; they are intentionally narrow and should not be reused as full SCSI command classifiers.
- Hypercall wrappers hard-code the argument forms used by this driver; adding VIOCTL arguments requires checking the wrapper signature.

## Test Signals

Compile coverage should catch missing Target Core or SRP type dependencies. Runtime validation should exercise every major state and flag transition: enable, init, login, SRP processing, wait idle, reconnect, error disconnect, suspend prepare/resume, and unconfigure. Debug logs that include state/flag dumps are useful for validating that macros classify the adapter correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/ibmvscsi_tgt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/libsrp.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/libsrp.c

## Purpose

`libsrp.c` provides small SRP target-side utilities for the IBM virtual SCSI target module. It allocates DMA-coherent SRP IU receive buffers, manages a FIFO-backed pool of IU entries, parses SRP data descriptor formats, maps Target Core scatterlists, and drives target-specific RDMA callbacks for direct and indirect SRP data movement.

## Important APIs and Functions

- `srp_target_alloc()` initializes `struct srp_target`, allocates a ring of coherent SRP buffers, creates an IU entry FIFO, and stores the target in device driver data.
- `srp_target_free()` tears down the ring and IU pool.
- `srp_iu_get()` and `srp_iu_put()` pop/push `struct iu_entry` pointers through a locked `kfifo`.
- `srp_transfer_data()` chooses the active SRP descriptor direction and format, locates the direct or indirect descriptor in `srp_cmd::add_data`, and calls the supplied `srp_rdma_t` callback.
- `srp_data_length()` returns the data length encoded in a direct or indirect descriptor.
- `srp_get_desc_table()` returns the command data direction and encoded data length for Target Core submission.
- Internal helpers include `srp_iu_pool_alloc()`, `srp_ring_alloc()`, `srp_direct_data()`, `srp_indirect_data()`, and `data_out_desc_size()`.

## Control Flow

Allocation first creates an array of `struct srp_buf *`, then allocates each `struct srp_buf` and its coherent buffer. The IU pool is a separate array of `struct iu_entry` objects plus a FIFO of pointers to free entries; each entry is pre-associated with one SRP buffer.

For data transfer, `srp_transfer_data()` exits early when Target Core has no data SG entries, calculates the additional CDB-aligned offset, adjusts for data-out descriptors when handling data-in, and dispatches based on `SRP_NO_DATA_DESC`, `SRP_DATA_DESC_DIRECT`, or `SRP_DATA_DESC_INDIRECT`. Direct descriptors use one memory descriptor. Indirect descriptors either use the embedded descriptor list or, when the table is external and `ext_desc`/`dma_map` allow it, allocate coherent memory, copy the external descriptor table from the client through the RDMA callback, then transfer data.

## State and Persistence

All state is in memory: `srp_target` owns the ring, FIFO, device pointer, and optional caller data; each `iu_entry` records its target, remote token, flags, buffer, and IU length. No state persists beyond target allocation/free.

## Dependencies and Integration Points

The implementation uses Linux `kfifo`, DMA coherent allocation, scatterlist DMA mapping, and `<scsi/srp.h>` descriptor definitions. It includes `ibmvscsi_tgt.h` because the RDMA callback type operates on `struct ibmvscsis_cmd`. The target driver supplies `ibmvscsis_rdma()` as the concrete RDMA function.

## Risks and Edge Cases

- `srp_ring_free()` assumes all ring entries were allocated; it is safe for normal teardown but not a partial ring unless the caller follows the allocation error path.
- Data transfer uses `DMA_BIDIRECTIONAL` for SG mapping regardless of final direction, which is conservative but may hide direction-specific bugs.
- External indirect descriptor handling allocates coherent memory sized by the client-provided table descriptor length; callers must validate protocol limits before reaching this path.
- `srp_get_desc_table()` infers a single direction by checking data-in before data-out. Mixed bidirectional descriptors are not represented as true bidirectional Target Core operations.
- Pointer arithmetic depends on `srp_cmd::add_data` being byte-addressable; the file enforces this with `BUILD_BUG_ON()`.

## Test Signals

Unit-style tests should cover pool exhaustion/reuse, partial allocation failure, direct read/write descriptors, embedded indirect descriptors, external indirect descriptor copy, invalid descriptor formats, zero-SG commands, and descriptor lengths that do not match command data lengths. Integration tests should observe `ibmvscsis_rdma()` calls split according to SRP descriptor count and SG list shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/libsrp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/libsrp.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/libsrp.h

## Purpose

`libsrp.h` declares the local SRP target helper interface and protocol constants shared by `libsrp.c` and `ibmvscsi_tgt.c`. It is not the kernel-wide SRP protocol header; it wraps Linux `<scsi/srp.h>` with IBM vSCSI target-specific queue and RDMA helper types.

## Important APIs, Types, and Constants

- Enumerations define CRQ valid values (`srp_valid`), payload formats (`srp_format`), init message formats (`srp_init_msg`), transport events (`srp_trans_event`), message statuses (`srp_status`), MAD version, OS type, SRP task attributes, and task-management response codes.
- `struct srp_buf` pairs a coherent buffer pointer with its DMA address.
- `struct srp_queue` contains IU pool storage and a locked `kfifo`.
- `struct srp_target` stores device pointer, command queue list, IU size, IU queue, receive ring, and caller-private `ldata`.
- `struct iu_entry` tracks one active IU buffer, including target pointer, remote token, flags, `sbuf`, and IU length.
- `srp_rdma_t` is the callback contract used by SRP descriptor helpers to move data between target scatterlists and client SRP memory descriptors.
- Public functions are `srp_target_alloc()`, `srp_target_free()`, `srp_iu_get()`, `srp_iu_put()`, `srp_transfer_data()`, `srp_data_length()`, and `srp_get_desc_table()`.
- `srp_cmd_direction()` returns `DMA_TO_DEVICE` when the high nibble of `buf_fmt` has a data-out descriptor; otherwise it returns `DMA_FROM_DEVICE`.

## Control Flow and State

The header defines the state objects consumed by the target implementation. A target allocates `srp_target`, obtains `iu_entry` objects for incoming CRQ payload copies, passes their SRP buffers into parser/Target Core paths, and returns them after the response is sent or the command is discarded. Data transfer flows through `srp_transfer_data()` into an `srp_rdma_t` callback supplied by the target driver.

## Dependencies and Integration Points

It includes Linux list and kfifo APIs plus `<scsi/srp.h>`. It forward-declares `struct ibmvscsis_cmd`, tying the generic-looking SRP helper to the IBM vSCSI target command type. Users must provide an RDMA callback matching the IBM target command structure.

## Risks and Edge Cases

- `srp_cmd_direction()` treats absence of data-out as data-in, so callers must separately handle no-data cases when that distinction matters.
- The enums mirror VIOSRP/IBM protocol values; mismatches with `<scsi/viosrp.h>` or firmware expectations break wire compatibility.
- `struct srp_target::cmd_queue` is declared here but command scheduling is mostly owned by `ibmvscsi_tgt.c`; ownership needs to remain clear.
- Because the RDMA typedef references `ibmvscsis_cmd`, this header is not a reusable generic SRP library boundary without refactoring.

## Test Signals

Build tests should catch enum/type drift with the C files. Runtime validation is indirect: successful target allocation, IU get/put cycling, SRP login, and read/write descriptor transfer all demonstrate that these declarations match the implementation and protocol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/libsrp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/imm.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/imm.c

## Purpose

`imm.c` is a low-level SCSI host adapter driver for the Iomega MatchMaker parallel-port SCSI interface embedded in ZIP Plus drives. It registers as a parport driver, probes compatible devices, exposes a single-command SCSI host, manually drives parallel-port control/data/status registers, and uses delayed work as a polling engine because the adapter does not provide usable interrupts.

## Important APIs, Types, and Functions

- `imm_struct` is the per-adapter state: parport device, base/base_hi I/O ports, transfer mode, current SCSI command, delayed work, start jiffies, transfer flags, parport arbitration state, device number, waitqueue pointer, SCSI host, and list node.
- Parport arbitration functions are `imm_pb_claim()`, `imm_pb_dismiss()`, `imm_pb_release()`, `imm_wakeup()`, and `got_it()`.
- Register/protocol primitives include `imm_wait()`, `imm_negotiate()`, `epp_reset()`, `ecp_sync()`, `imm_cpp()`, `imm_connect()`, `imm_disconnect()`, and `imm_select()`.
- Data movement helpers are `imm_byte_out()`, `imm_nibble_in()`, `imm_byte_in()`, `imm_out()`, `imm_in()`, and `imm_completion()`.
- SCSI engine and host callbacks include `imm_send_command()`, `imm_engine()`, `imm_interrupt()`, `imm_queuecommand_lck()`, `imm_abort()`, `imm_reset()`, `imm_biosparam()`, `imm_show_info()`, and `imm_write_info()`.
- Probe/remove are implemented by `__imm_attach()`, `imm_attach()`, `imm_detach()`, and `module_parport_driver(imm_driver)`.

## Control Flow

Module load registers a parport driver. On each matching parport, `__imm_attach()` allocates `imm_struct`, registers a parport device callback, claims the parport or waits briefly for ownership, initializes the hardware through `imm_init()`, allocates a SCSI host, stores `imm_struct *` in host private data, adds the host, and scans it.

Command execution starts in `imm_queuecommand_lck()`: it records `cur_cmd`, initializes the private `scsi_pointer` phase to zero, schedules delayed work immediately, and attempts to claim the parport. `imm_interrupt()` repeatedly calls `imm_engine()`; if the engine returns "still working", the delayed work is rescheduled one tick later. When the engine finishes, it disconnects if needed, releases the parport, clears `cur_cmd`, and calls `scsi_done()`.

`imm_engine()` is a phase machine: wait for parport ownership, connect to the MatchMaker interface, select the target SCSI ID, send the CDB in byte pairs, set up the scatterlist cursor, detect data direction and data phase, optionally negotiate IEEE 1284 mode for reads, transfer data in bursts or byte/nibble loops, perform post-data handshakes, read status/message bytes, and set `cmd->result`.

`device_check()` probes SCSI IDs, optionally tries EPP mode first during autodetect, sends Test Unit Ready, falls back to the original mode on failure, and resets/disconnects the device before returning success or probe failure.

## State and Persistence

State is volatile and per adapter. The only user-tunable persistent-for-module state is the `mode` module parameter; `/proc/scsi/imm/N` `write_info` can change `dev->mode` at runtime. `cur_cmd` enforces `can_queue = 1`. The SCSI command private `scsi_pointer` stores phase, SG cursor, residual bytes, and data pointer. No on-disk state is written.

The global `imm_hosts` list assigns stable ascending device numbers during attach and locates devices during detach. `arbitration_lock` protects `wanted` and parport claim state across callback and command contexts.

## Dependencies and Integration Points

The file depends on Linux parport APIs, raw I/O port accessors, delayed work, SCSI midlayer APIs, scatterlist helpers, and the local `imm.h` register/mode macros. It registers `imm_template` with SCSI, including queuecommand, abort, host reset, BIOS geometry, proc show/write hooks, `can_queue = 1`, `sg_tablesize = SG_ALL`, and private command size `sizeof(struct scsi_pointer)`.

## Risks and Edge Cases

- Hardware timing is manual and fragile: many paths use `udelay()`, polling loops, and magic control-register sequences.
- The EPP input path uses word/long I/O depending on mode and alignment; regressions can corrupt data or leave EPP timeout bits set.
- Odd SG residual lengths are rounded up to even bytes to satisfy byte-pair output, which can be surprising near buffer boundaries.
- Abort is only possible before the command reaches the SCSI bus; later aborts fail because the interface ties SCSI_MESSAGE high.
- `imm_completion()` intentionally yields after about one jiffy to avoid monopolizing CPU; changing this affects latency and fairness.
- Probe claims the parport with a bounded wait; ports owned too long cause attach failure.
- Raw port I/O and `base_hi` ECP handling are platform/hardware dependent.
- `/proc` write mode changes have minimal validation beyond string prefix and can switch modes while hardware behavior is marginal.

## Test Signals

Expected signals include successful parport registration, probe messages showing discovered SCSI ID and selected transfer mode, SCSI scan discovering the ZIP device, successful READ/WRITE commands in all supported modes, clean behavior when no device is present, timeout logs from `imm_wait()` on disconnected hardware, abort success only in phases 0-1, host reset pulsing and recovering the device, and detach cancelling delayed work without completing a freed command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/imm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/imm.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/imm.h

## Purpose

`imm.h` supplies version history, transfer mode constants, low-level parallel-port register macros, timing constants, and small declarations used by the Iomega MatchMaker (`imm`) SCSI host adapter implementation.

## Important APIs, Types, and Constants

- `IMM_VERSION` identifies the driver version string used in proc output.
- Transfer modes are `IMM_AUTODETECT`, `IMM_NIBBLE`, `IMM_PS2`, `IMM_EPP_8`, `IMM_EPP_16`, `IMM_EPP_32`, and `IMM_UNKNOWN`.
- `IMM_MODE_STRING[]` maps mode values to display strings.
- Tuning constants include `IMM_BURST_SIZE`, `IMM_SELECT_TMO`, `IMM_SPIN_TMO`, `IMM_DEBUG`, and `IN_EPP_MODE()`.
- `CONNECT_EPP_MAYBE` and `CONNECT_NORMAL` parameterize `imm_connect()`.
- Register read/write macros wrap raw `inb()`/`outb()` for data, status, control, EPP, FIFO, and ECR registers. `w_ctr()` optionally uses `outb_p()` under `CONFIG_SCSI_IZIP_SLOW_CTR`.
- `imm_scsi_pointer()` returns the command-private `struct scsi_pointer` allocated through the SCSI host template.
- The header forward-declares `imm_engine()`.

## Control Flow and State

The header does not implement command flow, but its constants drive `imm.c` probing and transfer paths. Mode constants choose between nibble, PS/2 byte, and EPP data paths. Register macros are used by every hardware phase: CPP connect/disconnect, target select, command output, data transfer, status reads, reset pulses, and ECP/EPP cleanup. `imm_scsi_pointer()` centralizes access to per-command phase and scatterlist cursor state.

## Dependencies and Integration Points

It includes kernel, module, I/O port, delay, proc, block, scheduler, interrupt, asm I/O, and SCSI host headers expected by `imm.c`. It assumes `imm_struct` is already defined before inclusion, which is why `imm.c` declares the typedef before including this header.

## Risks and Edge Cases

- `IMM_MODE_STRING` is defined in the header as a `static` array; this is acceptable for the single including C file but would create per-translation-unit copies if included elsewhere.
- Register macros perform raw I/O with no locking; callers must own the parport and preserve timing.
- `imm_scsi_pointer()` assumes the SCSI host template `cmd_size` reserves `struct scsi_pointer`; mismatches would corrupt command-private memory.
- `IMM_SPIN_TMO` and select timeout values directly affect timeout behavior on slow hardware.
- The header depends on include ordering for `imm_struct`, making it non-standalone.

## Test Signals

Build success validates include ordering and command-private sizing. Runtime proc output should show `IMM_VERSION` and a valid `IMM_MODE_STRING` entry. Mode-specific read/write tests exercise the register macros, while slow-control builds validate the `CONFIG_SCSI_IZIP_SLOW_CTR` branch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/imm.h -->
