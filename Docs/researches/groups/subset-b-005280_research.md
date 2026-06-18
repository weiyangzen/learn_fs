# subset-b-005280 research

Grouped research for the SCSI iSCSI and libsas files in `sources/distributed-fs/ceph-client/drivers/scsi`. Each section preserves the original source path and is intended to be split into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libiscsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/libiscsi.c

## Purpose

`libiscsi.c` is the transport-independent iSCSI initiator library used by software and partial-offload iSCSI low-level drivers. It owns SCSI command queueing, iSCSI task allocation, CmdSN/StatSN bookkeeping, management PDU dispatch, PDU completion, timeout handling, SCSI error-handler integration, session/connection lifecycle, and sysfs parameter plumbing. Transport drivers provide the `struct iscsi_transport` callbacks for PDU allocation, task initialization, transmit, cleanup, optional ITT parsing, and protection checking.

## Important APIs, Types, and Functions

Exported queueing and PDU helpers include `iscsi_queuecommand()`, `iscsi_conn_send_pdu()`, `iscsi_complete_pdu()`, `__iscsi_complete_pdu()`, `iscsi_complete_scsi_task()`, `iscsi_prep_data_out_pdu()`, `iscsi_requeue_task()`, `iscsi_verify_itt()`, `iscsi_itt_to_task()`, and `iscsi_itt_to_ctask()`. Host/session/connection lifecycle is provided by `iscsi_host_alloc()`, `iscsi_host_add()`, `iscsi_host_remove()`, `iscsi_host_free()`, `iscsi_session_setup()`, `iscsi_session_remove()`, `iscsi_session_free()`, `iscsi_session_teardown()`, `iscsi_conn_setup()`, `iscsi_conn_bind()`, `iscsi_conn_start()`, `iscsi_conn_stop()`, `iscsi_conn_unbind()`, and `iscsi_conn_teardown()`.

Error-handling APIs include `iscsi_eh_cmd_timed_out()`, `iscsi_eh_abort()`, `iscsi_eh_device_reset()`, `iscsi_eh_recover_target()`, `iscsi_eh_session_reset()`, `iscsi_session_failure()`, `iscsi_conn_failure()`, and `iscsi_session_recovery_timedout()`. Parameter APIs include `iscsi_set_param()`, `iscsi_session_get_param()`, `iscsi_conn_get_param()`, `iscsi_conn_get_addr_param()`, `iscsi_host_get_param()`, `iscsi_host_set_param()`, and `iscsi_switch_str_param()`.

The main runtime state is in `struct iscsi_host`, `struct iscsi_session`, `struct iscsi_conn`, `struct iscsi_task`, `struct iscsi_pool`, `struct iscsi_cmd`, and protocol headers from `iscsi_proto.h`. Session state values such as `ISCSI_STATE_LOGGED_IN`, `ISCSI_STATE_IN_RECOVERY`, `ISCSI_STATE_FAILED`, `ISCSI_STATE_RECOVERY_FAILED`, and `ISCSI_STATE_TERMINATE` gate queueing and recovery. Task states include free, pending, running, completed, requeued to SCSI, and aborted variants.

## Control Flow

Normal I/O starts at `iscsi_queuecommand()`. It validates class-session readiness, session state, leading connection presence, TX suspension, and CmdSN window space under `frwd_lock`. A task is pulled from the session `cmdpool` FIFO, attached to `iscsi_cmd(sc)->task`, and either transmitted immediately or queued on `conn->cmdqueue` for `iscsi_xmitworker()`. `iscsi_prep_scsi_cmd_pdu()` builds the SCSI Command PDU, including LUN, CDB or extended CDB AHS, immediate data length, unsolicited R2T state, read/write flags, transfer length, CmdSN, and transport-specific task initialization. The transmit worker prioritizes saved partial tasks, management PDUs, requeued Data-Out work, then new commands.

Receive-side completion enters `iscsi_complete_pdu()` or `__iscsi_complete_pdu()` under `back_lock`. It verifies ITT age/index, handles reserved-ITT async/NOP/reject PDUs, dispatches SCSI responses and Data-In status to `iscsi_scsi_cmd_rsp()` or `iscsi_data_in_rsp()`, forwards login/text/logout/async payloads to the iSCSI transport class via `iscsi_recv_pdu()`, and completes management/TMF tasks. CmdSN and ExpStatSN are updated from target responses, sense data is copied for CHECK CONDITION, residuals are checked, and task refs are released through `iscsi_complete_task()` and `iscsi_free_task()`.

Management PDUs are built by `iscsi_alloc_mgmt_task()` and sent through `iscsi_send_mgmt_task()`. Login and Text reuse a preallocated connection login task; other management tasks come from the command pool and require logged-in state. NOP-Outs serve both target-requested replies and initiator pings. Reject handling can resend target-triggered NOP-Outs or complete a rejected ping while treating unsupported or malformed reject payloads as protocol errors.

Error handling is serialized by `eh_mutex`. Command timeout handling first checks whether the task or older commands have made progress, then uses NOP-Out pings to distinguish slow I/O from dead transport before allowing SCSI EH escalation. Abort and reset paths issue immediate TMF PDUs, wait on `ehwait` with a timer, and interpret `TMF_SUCCESS`, `TMF_NOT_FOUND`, `TMF_FAILED`, or `TMF_TIMEDOUT`. Device and target reset suspend TX, fail affected tasks, clear the TMF header, and restart TX. Session reset asks userspace recovery to relogin and waits for the session to become logged in or terminal.

Connection lifecycle is userspace driven through the transport class. `iscsi_conn_bind()` marks the connection bound and resets command-number windows. `iscsi_conn_start()` validates negotiated burst and timeout parameters, transitions to logged-in, arms the transport timer, handles recovery age changes, unblocks the SCSI session, and wakes EH waiters. `iscsi_conn_stop()` moves the session to recovery or terminate, deletes timers, suspends TX, blocks the session for recovery, fails SCSI and management tasks, and clears TMF state. Host/session teardown coordinates class device removal with `ihost->num_sessions` and a removal waitqueue.

## State and Persistence Behavior

The file maintains volatile kernel state only. Persistent user configuration is not stored here; userspace writes negotiated or configured values through transport-class attributes and `iscsi_set_param()`. Session fields persist for the life of the class session: target names, CHAP strings, initiator/interface/boot metadata, CmdSN windows, negotiated burst/data-ordering settings, ERL, reset/abort timeouts, command pool, and TMF state. Connection fields persist for the class connection: timeouts, digest flags, max segment lengths, ExpStatSN, persistent address/port, local address, queues, counters, and the login buffer.

Concurrency is split between `frwd_lock` for queueing/transmit/session state and `back_lock` for receive completion/task freeing. Refcounts protect tasks that may be racing between transmit, receive, timeout, and EH paths. The session `age` is embedded into ITTs unless a transport provides its own parser, preventing stale completions from a previous login from completing new-session tasks.

## Dependencies and Integration Points

This file integrates the SCSI midlayer, SCSI EH, scsi_transport_iscsi class, kernel workqueues/timers/waitqueues/kfifo/refcounting, net TCP definitions, and protocol structures from `iscsi_proto.h`. It expects low-level drivers such as software TCP iSCSI, bnx2i, cxgbi, or other offloads to provide `struct iscsi_transport` callbacks for PDU allocation, transmit, cleanup, task initialization, ITT parsing, optional T10 PI checks, and endpoint disconnect coordination. Userspace open-iscsi controls login, parameter negotiation, stop/start, recovery, and receives async/login/text/logout PDUs through the transport class.

## Risks and Edge Cases

The highest-risk areas are task lifetime races across transmit retry, receive completion, abort, and connection stop. `cleanup_queued_task()` has to remove tasks from command, management, requeue, saved-transmit, and running-aborted slots without double completion. CmdSN accounting is subtle for pending tasks, non-immediate management PDUs, and failed direct transmit paths. TMF restrictions must allow required Data-Out only when safe and reject affected LUN I/O during abort/reset. Timeout handling depends on `last_xfer`, `last_timeout`, NOP timers, and receive progress; wrong updates can cause premature EH or hung commands.

Parameter setters use simple parsing and string replacement, so callers must provide valid negotiated values before `iscsi_conn_start()`. Several getters emit nullable string fields with `%s`, making initialization expectations important. `iscsi_host_remove()` waits for userspace/class session teardown; broken recovery or session destruction can stall removal. Recovery age is four bits and wraps at 16, so stale ITT protection relies on timely cleanup as well as age comparison.

## Test Signals

Useful signals include SCSI I/O under direct-transmit and workqueue transports, CmdSN window full behavior returning `SCSI_MLQUEUE_TARGET_BUSY`, immediate and unsolicited write data, R2T requeue interaction in TCP transports, login/text/logout passthrough to userspace, NOP ping timeout and reject handling, session relogin after `STOP_CONN_RECOVER`, shutdown/host-removal behavior, and sysfs parameter round-trips. EH testing should cover abort success, abort timeout, LUN reset, target reset fallback to session reset, commands completing while EH holds references, and recovery with stale completions from a previous session age.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libiscsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libiscsi_tcp.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/libiscsi_tcp.c

## Purpose

`libiscsi_tcp.c` is the TCP data-path companion to `libiscsi.c`. It handles stream segmentation, scatterlist mapping, padding, header/data digest calculation and verification, Data-In placement, R2T processing, Data-Out generation, per-task R2T pools, TCP connection setup, and statistics for software or TCP-like iSCSI transports.

## Important APIs, Types, and Functions

Segment helpers include `iscsi_tcp_segment_done()`, `iscsi_tcp_segment_unmap()`, `iscsi_segment_init_linear()`, `iscsi_segment_seek_sg()`, `iscsi_tcp_dgst_header()`, `iscsi_tcp_hdr_recv_prep()`, `iscsi_tcp_recv_segment_is_hdr()`, and `iscsi_tcp_recv_skb()`. Task and transmit APIs include `iscsi_tcp_task_init()`, `iscsi_tcp_task_xmit()`, `iscsi_tcp_cleanup_task()`, `iscsi_tcp_r2tpool_alloc()`, `iscsi_tcp_r2tpool_free()`, and `iscsi_tcp_set_max_r2t()`. Connection APIs include `iscsi_tcp_conn_setup()`, `iscsi_tcp_conn_teardown()`, and `iscsi_tcp_conn_get_stats()`.

The core structures are `struct iscsi_tcp_conn`, `struct iscsi_tcp_task`, `struct iscsi_segment`, `struct iscsi_r2t_info`, base `struct iscsi_conn`, base `struct iscsi_task`, and SCSI scatterlists. The file consumes the base transport callbacks `init_pdu()`, `alloc_pdu()`, `xmit_pdu()`, and `caps` for digest/padding offload.

## Control Flow

Receive starts with `iscsi_tcp_hdr_recv_prep()`, which initializes a linear segment over the connection header buffer. `iscsi_tcp_recv_skb()` walks the skb with `skb_seq_read()`, copies stream bytes into the current segment, and calls the segment completion callback when the expected bytes are present. Segment completion transparently advances through scatterlist elements, consumes iSCSI padding, and splices in data or header digest bytes when software digesting is active.

When a full header is available, `iscsi_tcp_hdr_recv_done()` reads extra AHS bytes if `hlength` is nonzero, verifies the header digest if needed, and calls `iscsi_tcp_hdr_dissect()`. Dissection validates data length, ITT, unsupported AHS for R2T, and opcode-specific expectations. SCSI Data-In looks up the command task, checks DataSN and target offset via `iscsi_tcp_data_in()`, and if data is present sets the receive segment to the SCSI command's scatterlist at the target offset. SCSI responses, login/text/reject/async payloads, logout, NOP-In, and TMF responses either prepare a linear receive buffer or immediately delegate completion to `libiscsi`.

R2T processing is handled in `iscsi_tcp_r2t_rsp()`. It validates the task, direction, datalen, R2TSN sequencing, logged-in state, nonzero length, negotiated burst expectations, and SCSI buffer bounds. It then takes an R2T object from the task's pool, fills target transfer tag, offset, length, StatSN, and DataSN state, queues it on the task's R2T FIFO, and requeues the task for transmit.

Transmit starts in `iscsi_tcp_task_init()`, which initializes management or SCSI command PDUs and immediate data. `iscsi_tcp_task_xmit()` flushes the current PDU through the transport's `xmit_pdu()`, returns for read or management tasks, and for writes repeatedly obtains unsolicited or target-requested R2T state, allocates a Data-Out PDU, calls `iscsi_prep_data_out_pdu()`, initializes the data segment at the requested offset, and flushes again until no R2T work remains.

## State and Persistence Behavior

All state is volatile. `struct iscsi_segment` tracks one in-progress stream segment: current data pointer or scatterlist entry, copied counts, total size, digest buffers, padding, and completion callback. `struct iscsi_tcp_task` tracks expected DataSN/R2TSN, current Data-In offset, current R2T, a per-task R2T pool, R2T queue, and locks that protect pool-to-queue and queue-to-pool transitions. `struct iscsi_tcp_conn` tracks input header/data parsing state and CRC accumulators. Connection counters in `struct iscsi_conn` are accumulated for transport stats.

Scatterlist highmem mappings are intentionally short-lived. Receive maps pages atomically and unmaps before returning from the skb path. Transmit may use `sendpage_ok()` to avoid mapping pages that the network layer can handle, and otherwise uses a sleepable mapping.

## Dependencies and Integration Points

The file depends on CRC32C, skb sequence helpers, highmem page mapping, scatterlists, libiscsi task/session APIs, SCSI command data buffers, and `iscsi_tcp.h`. It calls back into `libiscsi` for CmdSN updates, task lookup, PDU completion, connection failure, Data-Out header preparation, and connection setup/teardown. It integrates with transports that implement socket send/receive and expose digest or padding offload capabilities.

## Risks and Edge Cases

Stream parsing is sensitive to partial skb delivery, AHS length expansion, 4-byte padding, and digest splicing. Data-In validation must reject bad DataSN or offsets before setting up scatterlist writes. R2T handling must tolerate early command completion by holding a task reference and must not leak R2T objects when cleanup races with requeue/transmit. `iscsi_tcp_set_max_r2t()` frees and reallocates per-task pools after negotiation; callers must not change it while tasks are active. Header/data digest errors trigger connection failure, so offload capability bits must match what hardware actually handled.

The code accepts R2T data lengths greater than `max_burst` with a debug message and attempts execution, which is compatibility-oriented but worth testing with strict targets. Management payloads larger than `ISCSI_DEF_MAX_RECV_SEG_LEN` are rejected even though the protocol can represent larger segments. The host SMP-style scatterlist limitation does not apply here, but multi-sg Data-In correctness depends on `iscsi_segment_seek_sg()` finding a valid offset.

## Test Signals

Key tests include fragmented header and data reception across multiple skbs, header/data digest success and mismatch paths, padding consumption, Data-In into multi-entry scatterlists at nonzero offsets, SCSI response with and without sense payload, login/text/reject/async payload reception near the default receive buffer limit, R2T sequencing, R2T pool exhaustion, unsolicited write data followed by solicited Data-Out, `max_r2t` reconfiguration, and stats counters for tx/rx octets and PDU classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libiscsi_tcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/libsas/Kconfig

## Purpose

This Kconfig file defines the build-time feature switches for the libsas helper library. It exposes the core SAS domain-device transport helper, optional libata/SATA support, and optional host-side SMP interpretation.

## Important APIs, Types, and Functions

The symbols are `SCSI_SAS_LIBSAS`, `SCSI_SAS_ATA`, and `SCSI_SAS_HOST_SMP`. `SCSI_SAS_LIBSAS` is a tristate depending on `SCSI` and selecting `SCSI_SAS_ATTRS`. `SCSI_SAS_ATA` is a bool depending on libsas and on libata being built-in or matching the libsas linkage, and it selects `SATA_HOST`. `SCSI_SAS_HOST_SMP` is a bool defaulting to yes when libsas is enabled.

## Control Flow

There is no runtime control flow. The symbols determine which objects the libsas Makefile links into `libsas.o`. The dependency `ATA = y || ATA = SCSI_SAS_LIBSAS` prevents building libsas ATA support in a linkage combination that cannot satisfy libata references.

## State and Persistence Behavior

The file persists only kernel configuration choices. Runtime state is created by the C files selected through these symbols.

## Dependencies and Integration Points

`SCSI_SAS_LIBSAS` integrates with the SCSI core and SAS transport attributes. `SCSI_SAS_ATA` integrates libsas with libata and SATA host infrastructure. `SCSI_SAS_HOST_SMP` integrates host-side SMP request handling used by the SAS transport BSG path.

## Risks and Edge Cases

The main risk is invalid build composition. Disabling `SCSI_SAS_ATA` removes SATA/STP support from libsas even if discovery sees SATA devices. Disabling `SCSI_SAS_HOST_SMP` saves a small amount of code but removes the virtual SMP interpreter for SAS hosts.

## Test Signals

Build matrix signals are core libsas as built-in/module, ATA enabled and disabled, host SMP enabled and disabled, and verification that selected symbols produce the expected objects and exported symbols without unresolved references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/libsas/Makefile

## Purpose

This Makefile assembles the libsas helper library object. It defines the always-included core libsas source files and conditionally includes SATA and host SMP support based on Kconfig symbols.

## Important APIs, Types, and Functions

`obj-$(CONFIG_SCSI_SAS_LIBSAS) += libsas.o` creates the libsas composite object. The core `libsas-y` members are `sas_init.o`, `sas_phy.o`, `sas_port.o`, `sas_event.o`, `sas_discover.o`, `sas_expander.o`, `sas_scsi_host.o`, and `sas_task.o`. `libsas-$(CONFIG_SCSI_SAS_ATA)` adds `sas_ata.o`; `libsas-$(CONFIG_SCSI_SAS_HOST_SMP)` adds `sas_host_smp.o`. `ccflags-y` defines `DEBUG` and adds `drivers/scsi` to the include path.

## Control Flow

There is no runtime flow. Kbuild expands the composite object membership according to configuration and compiles all libsas objects with the listed flags.

## State and Persistence Behavior

The file persists build composition only. It does not define runtime state.

## Dependencies and Integration Points

It integrates with the kernel Kbuild system and the libsas Kconfig symbols. The include path supports internal SCSI headers used by libsas sources.

## Risks and Edge Cases

Because `sas_event.o`, `sas_discover.o`, and `sas_expander.o` are core members, topology discovery and event handling are always present with libsas. If `CONFIG_SCSI_SAS_ATA` is unset, references to SATA helper functions must be excluded by preprocessor guards or alternate stubs elsewhere. The unconditional `-DDEBUG` can enable debug code paths or messages expected by this older source tree.

## Test Signals

Build signals include `libsas.o` link membership under each Kconfig combination, absence of unresolved references when ATA or host SMP are disabled, and expected module/built-in generation for `CONFIG_SCSI_SAS_LIBSAS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_ata.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_ata.c

## Purpose

`sas_ata.c` bridges libsas domain devices to libata so SATA/STP devices behind SAS controllers can be discovered, reset, power-managed, issued ATA commands, and represented as SCSI devices. It translates libata queued commands into `struct sas_task`, translates SAS completion status back into ATA error masks/result taskfiles, coordinates ATA EH with libsas revalidation, and adds SATA-specific SCSI device sysfs attributes.

## Important APIs, Types, and Functions

Command execution and completion are centered on `sas_ata_qc_issue()`, `sas_ata_task_done()`, `sas_to_ata_err()`, and `sas_ata_qc_fill_rtf()`. Reset/readiness functions include `smp_ata_check_ready_type()`, `smp_ata_check_ready()`, `local_ata_check_ready()`, `sas_ata_wait_after_reset()`, `sas_ata_hard_reset()`, `sas_ata_prereset()`, `sas_ata_schedule_reset()`, and `sas_try_ata_reset()` integration through other files. Device setup and discovery functions include `sas_ata_init()`, `sas_ata_add_dev()`, `sas_discover_sata()`, and `sas_probe_sata()`.

EH and lifecycle helpers include `sas_ata_internal_abort()`, `sas_ata_post_internal()`, `sas_ata_sched_eh()`, `sas_ata_end_eh()`, `sas_ata_task_abort()`, `sas_ata_strategy_handler()`, `sas_ata_eh()`, `sas_ata_wait_eh()`, `sas_ata_device_link_abort()`, `sas_suspend_sata()`, `sas_resume_sata()`, and `sas_execute_ata_cmd()`. The libata port operations table is `sas_sata_ops`. The exported SCSI device attribute group is `sas_ata_sdev_attr_group`.

## Control Flow

Libsas discovery calls `sas_ata_init()` to allocate an `ata_host` and one `ata_port` for a SATA domain device, set SAS/SATA/NCQ flags, wire the port to the SAS host, and add the libata transport port. For expander-attached SATA, `sas_ata_add_dev()` may first lower link rate via SMP PHY control if the device exceeds the parent pathway rate, then reads REPORT PHY SATA data, initializes the domain device, allocates an end-device rphy, queues it for discovery, and calls `sas_discover_sata()`.

Libata command issue calls `sas_ata_qc_issue()` with the ATA port lock held. The function temporarily drops the lock, allocates a SAS task, fills STP ATA FIS and optional ATAPI packet, computes transfer length/scatterlist metadata, sets `qc->lldd_task`, links SCSI commands to the SAS task when present, and submits through the low-level driver's `lldd_execute_task()`. Completion arrives at `sas_ata_task_done()`, which races against libsas EH and libata freezing by checking `done_lock`, `SAS_HA_FROZEN`, `ata_port_is_frozen()`, and `qc` state. It copies ending FIS data for protocol responses or good status, maps SAS transport errors to ATA error masks, completes the queued command, and frees the SAS task.

Reset flow uses libata hardreset callbacks. `sas_ata_hard_reset()` invokes the low-level `lldd_I_T_nexus_reset()`, waits for readiness either through a local low-level `lldd_ata_check_ready()` callback or SMP rediscovery polling behind an expander, records the classified ATA device class, and marks the cable SATA. EH scheduling marks `SAS_DEV_EH_PENDING` and increments `ha->eh_active`; `sas_ata_end_eh()` clears it. `sas_ata_strategy_handler()` runs ATA port EH asynchronously for all SATA devices while revalidation is disabled, then reenables revalidation to process deferred topology changes.

Power management iterates SATA devices under the discovery mutex, calls `ata_sas_port_suspend()` or `ata_sas_port_resume()`, waits for EH, and fails probes whose devices are disabled. `sas_ata_eh()` extracts SATA commands from the SCSI EH work queue per device, hands them to libata command EH, and cleans any leftover stack-local list entries. Sysfs attributes proxy NCQ priority supported/enabled state to libata only for SATA-backed SCSI devices.

## State and Persistence Behavior

Runtime state lives in `domain_device.sata_dev`, the libata `ata_host`, `ata_port`, `ata_link`, queued command fields, `sas_task` fields, and SAS HA EH counters. The last device-to-host FIS is kept in `dev->sata_dev.fis` and is used to fill ATA result taskfiles. `SAS_DEV_EH_PENDING`, `SAS_DEV_GONE`, and `SAS_HA_ATA_EH_ACTIVE` coordinate removal, reset, and discovery deferral. No state is persisted outside kernel objects.

## Dependencies and Integration Points

The file depends on libata, SCSI EH, SAS transport classes, libsas internal structures, low-level libsas driver callbacks, SMP expander helpers, and block request aborts. It is compiled only when `CONFIG_SCSI_SAS_ATA` is selected. It is the main integration layer between SAS topology discovery and the ATA device model.

## Risks and Edge Cases

The highest-risk areas are ownership races for `sas_task` and `ata_queued_cmd` during completion, libata port freeze, SCSI EH abort, and internal ATA command abort. `sas_ata_internal_abort()` warns that failed low-level aborts may leak tasks because libsas is not prepared to recover if a driver keeps owning the task. Readiness polling differs for local versus expander-attached devices and must tolerate SATA pending states. Wide-port/link-rate adjustments behind expanders can fail and abort discovery. Revalidation is intentionally deferred during ATA EH; missing reenabling would suppress hotplug processing.

## Test Signals

Useful tests include SATA device discovery both direct-attached and behind expanders, ATAPI and NCQ command issue/completion, ending-FIS error propagation, SAS transport error translation, libata hardreset through local and SMP readiness paths, port freeze races with command completion, SCSI EH command extraction for SATA devices, internal command timeout/abort, suspend/resume with failed devices, link-rate lowering behind expanders, NCQ priority sysfs visibility and toggling, and hot-remove aborting in-flight commands quickly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_ata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_discover.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_discover.c

## Purpose

`sas_discover.c` drives libsas domain discovery, device registration, unregistration, suspend/resume handling, and discovery work scheduling for SAS ports. It creates root domain devices from port-attached identify/FIS frames, delegates to end-device, SATA, or expander discovery, notifies low-level drivers, manages rphy lifetime, and cleans up devices after hotplug or port teardown.

## Important APIs, Types, and Functions

Device initialization and notification APIs include `sas_init_dev()`, `sas_notify_lldd_dev_found()`, `sas_notify_lldd_dev_gone()`, `sas_free_device()`, `sas_unregister_dev()`, `sas_unregister_domain_devices()`, `sas_destruct_devices()`, `sas_device_set_phy()`, and `sas_fail_probe()` integration. Discovery work functions are `sas_discover_domain()`, `sas_revalidate_domain()`, `sas_discover_event()`, and `sas_init_disc()`. Helpers include `sas_get_port_device()`, `sas_probe_devices()`, `sas_suspend_devices()`, `sas_resume_devices()`, `sas_destruct_ports()`, and `sas_abort_device_scsi_cmds()`.

The primary data structures are `struct asd_sas_port`, `struct asd_sas_phy`, `struct sas_discovery`, `struct sas_discovery_event`, `struct domain_device`, `struct sas_rphy`, `struct sas_ha_struct`, and low-level driver callbacks in `struct sas_internal`.

## Control Flow

A discovery event queues `sas_discover_domain()` on the discovery workqueue. If the port has no `port_dev`, `sas_get_port_device()` allocates a domain device, copies the received frame from the first port phy, classifies SATA versus SAS OOB, initializes type-specific fields, allocates the correct rphy, fills identify data, records link rates/pathways, sets the target on each port phy, and places the device on either the discovery list or device list. Root end devices and SATA devices are staged on `disco_list`; expanders go directly to `dev_list`.

`sas_discover_domain()` then delegates to `sas_discover_end_dev()`, `sas_discover_root_expander()`, or `sas_discover_sata()`. On failure it frees the rphy, removes list entries, drops the device, and clears `port_dev`. Regardless of initial result, `sas_probe_devices()` moves staged devices into `dev_list`, probes SATA links with libata, adds rphys to the SAS transport, and fails probes that cannot be surfaced.

Revalidation runs under `ha->disco_mutex`, skips active ATA EH by leaving the pending bit set, and calls `sas_ex_revalidate_domain()` for expander roots. After revalidation it destructs pending devices and ports and probes newly staged devices. Suspend work disables SATA devices, notifies low-level drivers that devices are gone, calls optional `lldd_port_deformed()` for each phy, and marks phys/port suspended. Resume work resumes SATA devices.

Unregistration marks devices destroyed, aborts in-flight SCSI commands for gone non-expander devices, unlinks rphys, moves devices to `destroy_list`, and later `sas_destruct_devices()` removes children, deletes rphys, notifies low-level drivers, removes list links, ends SATA EH if needed, and drops references. Root and child device references are balanced through krefs, rphy device refs, parent refs, and phy refs.

## State and Persistence Behavior

Discovery state is held in `port->port_dev`, `port->disc.pending`, `port->disco_list`, `port->dev_list`, `port->destroy_list`, `port->sas_port_del_list`, root discovery fields such as `fanout_sas_addr`, `eeds_a`, `eeds_b`, and `max_level`, and per-device state bits like `SAS_DEV_FOUND`, `SAS_DEV_DESTROY`, `SAS_DEV_GONE`, and `SAS_DEV_EH_PENDING`. No persistent storage is written; all state is in kernel memory and SAS transport devices.

## Dependencies and Integration Points

This file integrates with SCSI transport SAS rphy/port objects, libata helpers when SATA is enabled, low-level libsas driver callbacks `lldd_dev_found`, `lldd_dev_gone`, and `lldd_port_deformed`, block tagset busy iteration for fast abort on removal, and libsas expander discovery/revalidation. It relies on event queuing from `sas_event.c` and topology details from `sas_expander.c`.

## Risks and Edge Cases

Root device classification depends on the first phy's received frame and OOB mode; a PHY-down race returns `-ENODEV`. Discovery must handle devices that fail before `sas_rphy_add()` differently from devices already visible to the transport class. Reference balancing is subtle when low-level drivers accept devices and `SAS_DEV_FOUND` adds a kref. Revalidation is deferred during ATA EH to avoid conflicting with SATA resets; pending bits must be preserved so the event is replayed. Device removal with active I/O relies on aborting tagset commands quickly for gone devices.

## Test Signals

Signals include direct SAS end-device discovery, direct SATA discovery, root expander discovery, failed rphy allocation/add paths, low-level `lldd_dev_found()` rejection, hot-remove with active I/O aborts, revalidation deferral during ATA EH and replay after `sas_enable_revalidation()`, suspend/resume notifications, rphy unlink/delete order, and cleanup of devices that never reached `sas_rphy_add()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_discover.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_event.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_event.c

## Purpose

`sas_event.c` provides libsas asynchronous event queuing, workqueue draining, deferred-event replay, runtime PM pairing, and revalidation gating around ATA error handling. It is the bridge between low-level PHY/port notifications and the libsas event/discovery workers.

## Important APIs, Types, and Functions

Exported or externally used APIs include `sas_queue_work()`, `sas_queue_deferred_work()`, `sas_drain_work()`, `sas_disable_revalidation()`, `sas_enable_revalidation()`, `sas_notify_port_event()`, and `sas_notify_phy_event()`. Internal helpers include `sas_queue_event()`, `__sas_drain_work()`, `sas_port_event_worker()`, `sas_phy_event_worker()`, and `sas_defer_event()`.

The key structures are `struct sas_ha_struct`, `struct sas_work`, `struct asd_sas_event`, `struct asd_sas_phy`, and HA state bits `SAS_HA_REGISTERED`, `SAS_HA_DRAINING`, `SAS_HA_RESUMING`, and `SAS_HA_ATA_EH_ACTIVE`.

## Control Flow

Low-level drivers call `sas_notify_port_event()` or `sas_notify_phy_event()`. The function allocates an event, takes a runtime PM reference with `pm_runtime_get_noresume()`, initializes the event work item with the appropriate worker and event ID, optionally defers events for new phys during resume, and queues the event under the HA lock. The worker dispatches through `sas_port_event_fns[event]` or `sas_phy_event_fns[event]`, drops the PM reference, and frees the event.

`sas_queue_work()` refuses events before registration, appends them to `ha->defer_q` while draining, or queues them to `ha->event_q`. `sas_drain_work()` serializes with `drain_mutex`, marks the HA draining, flushes submitters with a lock round trip, drains both event and discovery workqueues, clears draining, and requeues deferred work. If deferred work can no longer be queued, the code drops the PM reference and frees the event.

ATA EH calls `sas_disable_revalidation()` to set `SAS_HA_ATA_EH_ACTIVE` under `disco_mutex`. `sas_enable_revalidation()` clears the bit and scans all ports for pending domain revalidation; when found and a phy is present, it synthesizes a broadcast-received port event to replay the deferred topology check.

## State and Persistence Behavior

State is volatile and centered on HA workqueues, `defer_q`, HA state bits, and per-event allocations. Runtime PM references are paired across event allocation and worker/free paths. Revalidation deferral persists only as pending discovery bits and the `SAS_HA_ATA_EH_ACTIVE` HA bit.

## Dependencies and Integration Points

The file depends on libsas event function tables from internal code, kernel workqueues, runtime PM, HA locking, and discovery state in each port. It integrates tightly with `sas_discover.c` for revalidation events and with `sas_ata.c` for ATA EH deferral.

## Risks and Edge Cases

PM reference balancing is critical when an event is deferred, queued, rejected, or freed. During drain, the lock round trip is used to flush submitters before workqueue drain; incorrect locking would allow work to escape teardown. `sas_defer_event()` only defers during resume for phys not marked suspended, so resume sequencing depends on correct phy suspended flags. `sas_enable_revalidation()` synthesizes events only if a port has a phy; empty ports keep no replay target.

## Test Signals

Useful tests include notification before and after HA registration, event queueing during drain, deferred queue replay, failed requeue cleanup PM balance, runtime suspend/resume event deferral, ATA EH revalidation suppression and replay, and concurrent port/phy notifications while draining workqueues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_expander.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_expander.c

## Purpose

`sas_expander.c` implements libsas expander management: SMP command execution, expander and PHY discovery, route table configuration, topology validation, breadth-first discovery through expander trees, broadcast-change revalidation, hotplug add/remove, and BSG SMP forwarding to expanders. It is the main topology engine for SAS domains behind expanders.

## Important APIs, Types, and Functions

SMP execution helpers are `smp_execute_task_sg()`, `smp_execute_task()`, `alloc_smp_req()`, and `alloc_smp_resp()`. Discovery helpers include `sas_ex_general()`, `sas_ex_manuf_info()`, `sas_ex_phy_discover()`, `sas_expander_discover()`, `sas_discover_expander()`, `sas_discover_root_expander()`, `sas_ex_discover_devices()`, `sas_ex_discover_dev()`, `sas_ex_discover_end_dev()`, and `sas_ex_discover_expander()`.

Routing and PHY helpers include `sas_smp_phy_control()`, `sas_configure_phy()`, `sas_configure_parent()`, `sas_configure_routing()`, `sas_disable_routing()`, `sas_ex_disable_phy()`, `sas_ex_disable_port()`, `sas_smp_get_phy_events()`, `sas_get_report_phy_sata()`, `sas_get_phy_attached_dev()`, `sas_find_attached_phy_id()`, and `sas_ex_to_ata()`. Revalidation helpers include `sas_find_bcast_dev()`, `sas_find_bcast_phy()`, `sas_rediscover()`, `sas_rediscover_dev()`, `sas_discover_new()`, `sas_unregister_ex_tree()`, and `sas_ex_revalidate_domain()`. BSG integration is `sas_smp_handler()`.

The central structures are `struct domain_device`, `struct expander_device`, `struct ex_phy`, `struct sas_expander_device`, `struct sas_task`, `struct smp_*_resp`, `struct discover_resp`, `struct sas_phy`, `struct sas_port`, and discovery state in `struct sas_discovery`.

## Control Flow

Expander discovery begins with `sas_discover_root_expander()` adding the root rphy, setting level zero, and calling `sas_discover_expander()`. That notifies the low-level driver, issues REPORT GENERAL to learn change count, route table capacity, number of phys, self-configuration state, and enclosure ID, reads manufacturer info, allocates `ex_phy`, and performs DISCOVER for every expander PHY. Each DISCOVER response is normalized by `sas_set_ex_phy()`, which creates SAS PHY objects as needed, tracks attached type/address/linkrate/routing/change count, handles SATA pending detection, and logs meaningful changes.

After initial expander interrogation, topology validation checks subtractive boundaries and parent-child routing compatibility. Device discovery proceeds breadth-first by expander level. Each usable PHY is filtered for parent/backlink, duplicate domain addresses, empty/disabled/reset-problem states, unknown device types, and route configuration. Wide ports are joined when another PHY already points at the same attached SAS address. End devices become SATA/STP via `sas_ata_add_dev()` or SSP via `sas_ex_add_dev()`. Child expanders allocate a new SAS port and expander rphy, are added to the port device list, recursively discovered, and linked into the parent's child list.

Routing table configuration walks from a child expander up through parents. For each parent table-routed PHY leading toward the child, `sas_configure_present()` scans REPORT ROUTE INFORMATION entries for the target SAS address or a free slot, and `sas_configure_set()` sends CONFIGURE ROUTE INFORMATION to include or exclude the route. Self-configuring expanders skip explicit route table programming.

Broadcast-change revalidation starts at `sas_ex_revalidate_domain()`. It finds the expander whose change count and PHY change count changed, then iterates changed PHYs. `sas_rediscover_dev()` reads current attached address/type, removes old devices for vacant/no-phy/empty/communication-loss cases, treats SATA pending/end-device type flutter as reset noise, and otherwise unregisters the old device and discovers the new one. Removal tears down child expander subtrees recursively, disables routing for removed SAS addresses, removes PHYs from wide ports, and queues empty SAS ports for later deletion.

`sas_smp_handler()` services BSG SMP requests. If there is no rphy it delegates to the host SMP interpreter. For expander rphys it finds the matching domain device, rejects multi-segment payloads, executes the SMP task through the low-level driver, and reports received length based on underrun.

## State and Persistence Behavior

Expander state is volatile in `domain_device.ex_dev`: number of phys, route indexes, change count, t2t support, route-table configuration mode, self-configuring flag, enclosure logical ID, allocated `ex_phy` array, parent port, and child list. Each `ex_phy` stores attached SAS address, attached type/protocols, link rates, routing attribute, change count, last direct-address route index, SAS PHY object, SAS port, and phy state. Discovery-level state stores fanout and edge-expander boundary addresses and maximum BFS level. Route table changes are programmed into expanders and therefore affect hardware fabric state, but this file does not persist data across driver reloads.

SMP commands are serialized per expander by `ex_dev.cmd_mutex` and bracketed by runtime PM references. Slow tasks have timers and completions; failed or timed-out tasks are aborted through low-level callbacks.

## Dependencies and Integration Points

The file depends on libsas task execution callbacks, SAS transport rphy/phy/port objects, SMP protocol definitions, libata SATA helper hooks, SCSI BSG jobs, runtime PM, and the low-level driver's `lldd_execute_task()` and `lldd_abort_task()`. It calls into `sas_discover.c` for device notification/unregistration and into `sas_ata.c` for SATA/STP device creation and SATA FIS reporting.

## Risks and Edge Cases

SMP execution retries and timeout handling are delicate: the function frees tasks after completion, abort, underrun, overrun, or unknown-device responses and has a `BUG_ON` if retry accounting leaves a task live. `sas_set_ex_phy()` intentionally avoids mutating much state while ATA EH is active and instead marks revalidation pending; missing this guard can conflict with libata reset polling. Topology rules for fanout, edge expanders, table/subtractive routing, EEDS, and duplicate SAS addresses can disable ports or phys; incorrect detection may hide devices. Route table scanning uses the first free slot or remembered direct-address index, so expanders with inconsistent REPORT ROUTE INFO behavior can cause failed routing. Wide-port removal must avoid unregistering the child until the last PHY disappears.

## Test Signals

Strong test signals include REPORT GENERAL/manufacturer/DISCOVER parsing, discovery through multi-level expanders, SATA pending transitions, wide-port creation/removal, duplicate SAS address disabling, fanout and edge topology rule enforcement, route table include/exclude programming, self-configuring expander behavior, broadcast-change hot-add/hot-remove, subtree removal, PHY error counter reads, REPORT PHY SATA endian fixups, BSG SMP passthrough and host fallback, SMP timeouts/underruns/overruns, and runtime PM balance during SMP tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_expander.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_host_smp.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_host_smp.c

## Purpose

`sas_host_smp.c` implements a virtual SMP target for SAS hosts when no expander rphy is targeted. It lets BSG SMP requests query and control host PHY state, report host manufacturer information, report SATA information for directly attached SATA devices, and optionally write GPIO registers through low-level driver callbacks.

## Important APIs, Types, and Functions

The top-level handler is `sas_smp_host_handler()`. Request handlers include `sas_host_smp_discover()`, `sas_report_phy_sata()`, `sas_phy_control()`, and `sas_host_smp_write_gpio()`. GPIO bit helpers are `to_sas_gpio_gp_bit()` and exported `try_test_sas_gpio_gp_bit()`.

Important structures are `struct sas_ha_struct`, `struct asd_sas_phy`, `struct sas_phy`, `struct sas_rphy`, `struct bsg_job`, `struct dev_to_host_fis`, and low-level driver callbacks `lldd_write_gpio` and `lldd_control_phy`.

## Control Flow

`sas_smp_host_handler()` validates minimum request and response payload sizes, copies the BSG request sglist into a linear buffer, allocates a response buffer large enough for known frames, validates `SMP_REQUEST`, initializes a default unknown-function response, and switches on the SMP function code. REPORT GENERAL returns the host phy count. REPORT MANUFACTURER INFORMATION returns the SCSI host template name and a fixed virtual product string. DISCOVER reports per-phy link rates, SAS addresses, attached addresses, and attached device protocol/type from the current port device. REPORT PHY SATA returns directly attached SATA information and converts the saved D2H FIS into the response byte order. WRITE GPIO delegates raw register writes to `lldd_write_gpio()`. PHY CONTROL validates the operation and forwards it to `lldd_control_phy()`, except link reset may be satisfied by libata reset coordination via `sas_try_ata_reset()`.

The handler copies the response back to the reply sglist and completes the BSG job with the selected response length. Unsupported functions generally complete with `SMP_RESP_FUNC_UNK`; invalid frame lengths fail the job.

## State and Persistence Behavior

The file does not own persistent state. It reads current HA PHY topology, current `sas_phy` linkrate limits, attached SAS addresses, rphy identify fields, and saved SATA FIS data from the port device. GPIO writes and PHY control requests may change hardware state through low-level callbacks, but no configuration is stored here.

## Dependencies and Integration Points

The file depends on the SAS transport BSG path, libsas HA/PHY/port state, SMP protocol constants, low-level driver callbacks for GPIO and PHY control, and libata reset coordination through `sas_try_ata_reset()`. It is compiled when `CONFIG_SCSI_SAS_HOST_SMP` is selected and is also used as fallback by `sas_expander.c` when an SMP BSG job has no target rphy.

## Risks and Edge Cases

Many responses are best-effort snapshots without global topology locking. `sas_report_phy_sata()` assumes a port and `port_dev` exist after checking only the phy's port pointer, so host topology transitions must keep those pointers consistent. Only single linear request/response copies are used through temporary buffers sized from BSG payload lengths. GPIO bit layout is nonintuitive and depends on SFF-8485 register indexing. PHY CONTROL can trigger disruptive link/hard resets or disables if authorized by userspace and the low-level driver.

## Test Signals

Test signals include BSG REPORT GENERAL, REPORT MANUFACTURER INFO, DISCOVER for valid and invalid phy IDs, REPORT PHY SATA for SATA and non-SATA phys, WRITE GPIO with and without a low-level callback, GPIO bit extraction across register indexes, PHY CONTROL operations including invalid op and no-phy cases, libata-coordinated link reset, and response length/error handling for undersized request or reply payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_host_smp.c -->
