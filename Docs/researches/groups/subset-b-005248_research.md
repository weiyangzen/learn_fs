# Research: subset-b-005248

This grouped report covers QLogic/Broadcom NetXtreme II FCoE and iSCSI offload driver files. Each section is source-path aligned for reconciliation into the corresponding per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_io.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_io.c

## Purpose

`bnx2fc_io.c` is the FCoE offload driver's SCSI I/O manager. It owns the per-XID `struct bnx2fc_cmd` pool, maps SCSI scatterlists into firmware buffer descriptors, posts FCP commands to target send queues, handles completions, and drives SCSI error handling through ABTS, cleanup requests, and FCP task management functions.

## Important APIs, Types, and Functions

Externally used entry points include `bnx2fc_cmd_mgr_alloc()`, `bnx2fc_cmd_mgr_free()`, `bnx2fc_cmd_alloc()`, `bnx2fc_elstm_alloc()`, `bnx2fc_cmd_release()`, `bnx2fc_queuecommand()`, `bnx2fc_post_io_req()`, `bnx2fc_eh_abort()`, `bnx2fc_eh_device_reset()`, `bnx2fc_eh_target_reset()`, `bnx2fc_initiate_abts()`, `bnx2fc_initiate_cleanup()`, `bnx2fc_initiate_seq_cleanup()`, `bnx2fc_process_scsi_cmd_compl()`, `bnx2fc_process_abts_compl()`, `bnx2fc_process_cleanup_compl()`, `bnx2fc_process_tm_compl()`, and `bnx2fc_build_fcp_cmnd()`.

The file revolves around `struct bnx2fc_cmd`, `struct bnx2fc_cmd_mgr`, `struct io_bdt`, `struct bnx2fc_mp_req`, `struct fcoe_task_ctx_entry`, `struct fcoe_bd_ctx`, and SCSI/libfc objects such as `struct scsi_cmnd`, `struct fc_lport`, `struct fc_rport`, and `struct fc_rport_priv`.

## Control Flow

Normal I/O enters through `bnx2fc_queuecommand()`. It verifies remote-port readiness, local-port link state, session readiness, and target retry delay, then allocates a command under `tgt_lock` and calls `bnx2fc_post_io_req()`. Posting sets direction flags and counters, maps the SCSI SG list into BD entries, initializes the firmware task context, starts an I/O timeout when enabled, adds the XID to the SQ, links the command on `active_cmd_queue`, and rings the target doorbell.

Completions arrive from the hardware path into `bnx2fc_process_scsi_cmd_compl()`. The completion path suppresses duplicate timeout races with `BNX2FC_FLAG_IO_COMPL`, cancels timeout work, parses the FCP response and sense/RQ data, moves the command to `io_retire_queue`, unmaps DMA, sets SCSI result and residual, applies retry-delay throttling for BUSY/TASK_SET_FULL, calls `scsi_done()`, and drops the command reference.

Error handling is multi-stage. `bnx2fc_cmd_timeout()` issues ABTS for timed-out SCSI commands, invokes cleanup when ABTS itself times out, and handles ELS timeout callbacks. `bnx2fc_eh_abort()` removes a command from the active queue, initiates ABTS, waits for `abts_done`, and falls back to cleanup before returning control to the SCSI mid-layer. Device and target resets call `bnx2fc_initiate_tmf()`, which sends a TMF FCP command and then aborts matching active commands on successful LUN or target reset completion.

## State and Persistence Behavior

No durable state is written. Runtime state is held in per-adapter command pools, per-target active/TMF/ELS/retire queues, per-command refcounts and flags, delayed timeout work, DMA-coherent BD tables, and `bnx2fc_priv(sc_cmd)->io_req` back-pointers. Firmware-visible task context is indexed by XID. Timer holds are explicit `kref` references released by timeout cancellation or execution.

## Dependencies and Integration Points

The file integrates with the Linux SCSI mid-layer, libfc remote-port state, FCoE task-context helpers from `bnx2fc_hwi.c`, CNIC DMA resources through the PCI device, and target/session state from `bnx2fc_tgt.c`. It depends on hardware constants and command structures from `bnx2fc.h`, FCP status layouts, FC frame headers, workqueues, completions, krefs, and DMA mapping APIs.

## Risks and Edge Cases

Race handling is delicate because timeout work, SCSI error handlers, firmware completions, and session flush can all see the same command. Incorrect flag ordering can double-complete a SCSI command or leak a command reference. BD splitting must stay under `BNX2FC_FW_MAX_BDS_PER_CMD`; otherwise the mid-layer sees host busy. `bnx2fc_parse_fcp_rsp()` assumes a single RQ buffer is normally enough for response and sense data and truncates invalid lengths. Cleanup/ABTS interactions rely on firmware behavior that one completion may suppress the other. Queue accounting uses atomics plus per-list locks, so missed `kref_put()` or queue removal can stall session upload.

## Test Signals

Useful validation includes SCSI read/write I/O with direct and split SG entries, zero-length/control commands, induced BD overflow, FCP sense data and residual handling, BUSY/TASK_SET_FULL retry delay, command timeout with ABTS success and failure, cleanup timeout, LUN and target reset while I/O is active, ELS timeout callbacks, session flush with active commands, and reference/DMAMAP leak checks during link flap and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_tgt.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_tgt.c

## Purpose

`bnx2fc_tgt.c` manages FCoE target sessions for the NetXtreme II offload driver. It reacts to libfc remote-port events, allocates connection IDs and queue-pair/session resources, sends offload/enable/disable/destroy requests to firmware, and flushes outstanding I/O during upload or failure.

## Important APIs, Types, and Functions

Primary entry points are `bnx2fc_rport_event_handler()`, `bnx2fc_tgt_lookup()`, and `bnx2fc_flush_active_ios()`. Internal helpers include `bnx2fc_offload_session()`, `bnx2fc_upload_session()`, `bnx2fc_init_tgt()`, `bnx2fc_alloc_conn_id()`, `bnx2fc_free_conn_id()`, `bnx2fc_alloc_session_resc()`, `bnx2fc_free_session_resc()`, and the offload/upload wait timers.

Important state is in `struct bnx2fc_rport`, `struct bnx2fc_hba`, `struct fcoe_port`, `struct fc_rport_priv`, firmware queues SQ/CQ/RQ/XFERQ/CONFQ/LCQ, page block lists, and connection DB memory.

## Control Flow

On `RPORT_EV_READY`, `bnx2fc_rport_event_handler()` filters out directory server, non-FCP, and non-target ports, then serializes with `hba_mutex`. It initializes the target, allocates DMA resources, sends a session offload request and waits for completion, maps doorbells, sends enable, and marks `BNX2FC_FLAG_SESSION_READY` on success. Context allocation failures are retried a few times.

On `RPORT_EV_LOGO`, `RPORT_EV_FAILED`, or `RPORT_EV_STOP`, the handler clears session-ready state and calls `bnx2fc_upload_session()`. Upload sends disable, waits for completion, flushes active I/O/TMF/ELS/retire queues, sends destroy if disable succeeded, waits for destroy, frees session resources, and releases the connection ID.

`bnx2fc_flush_active_ios()` marks `flush_in_prog`, removes commands from active queues, cancels timers, completes waiters where needed, either issues firmware cleanup or locally processes cleanup when disable failed, clears RRQ flags on retire queue entries, then waits for `num_active_ios` to drain.

## State and Persistence Behavior

The file maintains runtime-only target state: `hba->tgt_ofld_list`, `hba->next_conn_id`, `hba->num_ofld_sess`, target flags, queue indexes, DMA queue memory and PBLs, doorbell headers, wait queues, and timers. No data is persisted, but firmware-visible DMA allocations and connection IDs must be released on all failed offload and upload paths.

## Dependencies and Integration Points

It integrates with libfc remote-port events, the bnx2fc firmware request helpers in hardware-specific files, PCI DMA allocation, MMIO doorbell mapping, and SCSI I/O cleanup from `bnx2fc_io.c`. It also coordinates link-down shutdown through `hba->shutdown_wait`.

## Risks and Edge Cases

Offload and upload are blocking flows protected by `hba_mutex`; any missed wakeup on completion flags can stall remote-port processing until timer fallback. Upload timer deliberately fakes completion, so later paths must handle partially disabled firmware state. `bnx2fc_alloc_session_resc()` returns `-ENOMEM` without freeing partial allocations itself, relying on the caller's error path. Flush processing can race late firmware completions and SCSI aborts. Connection-ID allocation returns `-1` through an unsigned type, so callers must consistently compare against `(u32)-1` or assigned `-1`.

## Test Signals

Validate successful target login/offload/enable, context allocation retry, offload timeout, enable failure, rport logout/upload/destroy, disable failure, active I/O flush during link down, no leaked DMA queues after failed allocations, `tgt_lookup()` behavior for deleted rports, and shutdown wakeups when the last offloaded session disappears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_tgt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/57xx_iscsi_constants.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/57xx_iscsi_constants.h

## Purpose

`57xx_iscsi_constants.h` defines firmware HSI constants for NetXtreme II iSCSI offload. It supplies opcode, status, task-type, queue-doorbell, page-size, digest, and connection-type values consumed by `bnx2i_hwi.c` and the firmware ABI structures in `57xx_iscsi_hsi.h`.

## Important APIs, Types, and Functions

The file has no functions or types. Important definitions include cleanup request/response opcodes, iSCSI task type encodings for read/write/middle-path commands, initial CQ sequence numbers, KWQE layer/opcodes for firmware init, connection offload/update/destroy, KCQE opcodes for offload/update/init/cleanup/TCP/iSCSI errors, completion status codes, SQ/RQ/CQ doorbell structure sizes, page-size encodings, iSCSI header/digest sizes, and the 577xx iSCSI connection type.

## Control Flow

There is no executable control flow. Runtime code uses these constants when building KWQEs, SQ WQEs, KCQE dispatch switches, error classification, queue page-table offsets, and doorbell headers.

## State and Persistence Behavior

No state is stored. The constants are firmware ABI and must remain stable for driver and firmware compatibility.

## Dependencies and Integration Points

Included by `bnx2i.h`, which in turn feeds all bnx2i implementation files. `bnx2i_send_fw_iscsi_init_msg()` uses init opcodes, page-size encodings, and error masks. `bnx2i_indicate_kcqe()` and error handlers dispatch on KCQE opcodes/status values. 577xx queue setup uses the SQ/RQ/CQ DB size constants.

## Risks and Edge Cases

Wrong numeric values would route KWQEs to the wrong firmware operation, misclassify fatal protocol errors as warnings, corrupt 577xx page-table offsets, or break doorbell programming. Because these values are not type checked, regressions usually appear only at runtime on specific hardware/firmware combinations.

## Test Signals

Build coverage is necessary but insufficient. Useful signals include firmware init success, offload/update/destroy KCQE dispatch, command cleanup response handling, license-error reporting, protocol warning versus recovery behavior under `error_mask1/2`, and 577xx doorbell/page-table operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/57xx_iscsi_constants.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/57xx_iscsi_hsi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/57xx_iscsi_hsi.h

## Purpose

`57xx_iscsi_hsi.h` is the iSCSI host/firmware interface layout header. It defines endian-aware C structures for firmware send-queue work entries, completion-queue entries, kernel work/completion queue entries, buffer descriptors, connection offload/update/destroy requests, and iSCSI protocol message variants.

## Important APIs, Types, and Functions

There are no functions. Core ABI structures include `struct iscsi_bd`, `struct bnx2i_cmd_request`, `struct bnx2i_cmd_response`, `struct bnx2i_fw_mp_request`, `struct bnx2i_cleanup_request`, `struct bnx2i_cleanup_response`, `struct iscsi_kcqe`, `struct iscsi_kwqe_header`, `struct iscsi_kwqe_init1`, `struct iscsi_kwqe_init2`, `struct iscsi_kwqe_conn_offload1/2/3`, `struct iscsi_kwqe_conn_update`, `struct iscsi_kwqe_conn_destroy`, `struct bnx2i_login_request/response`, `struct bnx2i_logout_request/response`, `struct bnx2i_nop_in_msg`, `struct bnx2i_nop_out_request`, `struct bnx2i_reject_msg`, `struct bnx2i_tmf_request/response`, `struct bnx2i_text_request/response`, and unions `iscsi_kwqe`, `iscsi_request`, and `iscsi_response`.

Most structures include bit-mask macros colocated with fields, such as ITT index/type fields, final/read/write flags, digest/update flags, response residual flags, connection-update negotiation flags, and page-size/layer-code fields.

## Control Flow

No executable flow exists, but the structures define the runtime data path. `bnx2i_hwi.c` casts SQ memory to request structures before ringing doorbells and casts CQ memory to response structures when KCQ notifications report new completions. The KWQE structures are submitted through CNIC to initialize firmware, offload connections, update negotiated parameters, and destroy contexts.

## State and Persistence Behavior

The header stores no state itself. Its layouts describe DMA-shared state between host and firmware, so field order, width, alignment, and endian-specific placement are effectively persistent ABI contracts across hardware generations.

## Dependencies and Integration Points

The file depends on fixed-width Linux integer types and compile-time `__BIG_ENDIAN`/`__LITTLE_ENDIAN` selection. It is included via `bnx2i.h`. It integrates with libiscsi headers indirectly because runtime code copies between standard iSCSI headers and these firmware-specific WQEs/CQEs.

## Risks and Edge Cases

Endian branches duplicate many fields and masks; a field-order mismatch on one endian target can silently corrupt firmware messages. Several macros are repeated for request and response variants with the same names, so include ordering and local context matter. Flexible protocol state is compressed into packed bit fields, making wrong shifts difficult to diagnose. Runtime code often casts raw queue memory to these types, so size or alignment changes can break real hardware without compiler errors.

## Test Signals

Useful signals include compile testing on little and big endian, firmware init/offload/update/destroy success, successful login/text/logout/NOP/TMF/SCSI command exchange, residual and sense-data handling, protocol error KCQE decoding, and structure size/alignment audits against the firmware specification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/57xx_iscsi_hsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/Kconfig

## Purpose

`Kconfig` declares the `SCSI_BNX2_ISCSI` tristate option for QLogic NetXtreme II iSCSI offload support.

## Important APIs, Types, and Functions

There are no runtime APIs. The configuration symbol is `SCSI_BNX2_ISCSI`, with prompt `QLogic NetXtreme II iSCSI support`.

## Control Flow

Selecting the option allows the kernel build to compile the bnx2i module or link it built-in. The symbol depends on `NET` and `PCI`, and selects `SCSI_ISCSI_ATTRS`, `NETDEVICES`, `ETHERNET`, `NET_VENDOR_BROADCOM`, and `CNIC`.

## State and Persistence Behavior

The only persistent effect is the kernel configuration value stored in the build configuration. No runtime state exists in this file.

## Dependencies and Integration Points

The option ensures the SCSI iSCSI transport attributes and Broadcom CNIC networking support are present before building `bnx2i.o`. It integrates with `drivers/scsi/bnx2i/Makefile`, which uses `obj-$(CONFIG_SCSI_BNX2_ISCSI)`.

## Risks and Edge Cases

If dependencies or selects drift from actual code needs, builds may fail or runtime registration with CNIC/libiscsi may be unavailable. Over-selecting networking symbols can force in larger dependency sets than expected.

## Test Signals

Validate `m`, `y`, and disabled builds; allmodconfig coverage; dependency resolution when `NET` or `PCI` is disabled; and module load with CNIC present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/Makefile

## Purpose

`Makefile` defines how the bnx2i iSCSI offload driver is built.

## Important APIs, Types, and Functions

The composite object `bnx2i-y` consists of `bnx2i_init.o`, `bnx2i_hwi.o`, `bnx2i_iscsi.o`, and `bnx2i_sysfs.o`. `obj-$(CONFIG_SCSI_BNX2_ISCSI) += bnx2i.o` connects the composite object to the Kconfig symbol.

## Control Flow

There is no runtime flow. At build time, Kbuild compiles the listed objects into `bnx2i.o` when `SCSI_BNX2_ISCSI` is enabled.

## State and Persistence Behavior

No runtime state exists. The file controls build artifact composition.

## Dependencies and Integration Points

It integrates with the kernel Kbuild system and the local Kconfig. The listed objects provide module init/CNIC registration, hardware queue and completion handling, libiscsi transport operations, and sysfs attributes.

## Risks and Edge Cases

Omitting any object can produce missing symbols or a module that registers but lacks required transport or sysfs behavior. Adding objects in the wrong directory or with mismatched config guards can break incremental builds.

## Test Signals

Build with `CONFIG_SCSI_BNX2_ISCSI=m` and `y`, inspect that `bnx2i.o` includes all four objects, and run modpost for unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i.h

## Purpose

`bnx2i.h` is the shared private header for the NetXtreme II iSCSI offload driver. It defines driver limits, queue sizes, device-family flags, doorbell constants, statistics helpers, adapter/connection/endpoint/queue structures, global variables, and cross-file prototypes.

## Important APIs, Types, and Functions

Major structures include `struct generic_pdu_resc`, `struct bd_resc_page`, `struct io_bdt`, `struct bnx2i_cmd`, `struct bnx2i_conn`, `struct iscsi_cid_queue`, `struct bnx2i_stats_info`, `struct bnx2i_hba`, queue entry wrappers `struct sqe/rqe/cqe`, 577xx doorbell structures, `struct qp_info`, `struct ep_handles`, `struct bnx2i_endpoint`, `struct bnx2i_work`, and `struct bnx2i_percpu_s`.

Important enums and flags include adapter states, endpoint states, device-family bits for 5706/5708/5709/57710, mailbox access modes, and queue doorbell offsets. Prototypes expose CNIC callbacks, HBA allocation, connection lookup, QP allocation, WQE send routines, completion processing, endpoint lookup, doorbell mapping, and per-CPU I/O thread entry.

## Control Flow

The header defines the driver layering. `bnx2i_init.c` owns module and CNIC lifecycle, `bnx2i_hwi.c` owns hardware WQE/CQE handling, `bnx2i_iscsi.c` owns libiscsi transport/session/endpoint operations, and `bnx2i_sysfs.c` exports attributes. Runtime code threads through `struct bnx2i_hba` to `struct bnx2i_endpoint`, `struct bnx2i_conn`, and `struct bnx2i_cmd`.

## State and Persistence Behavior

All state is runtime-only. Persistent-looking data includes adapter lists, CNIC registration state, per-HBA CID queues, endpoint lists, QP DMA memory, generic PDU DMA buffers, command BD tables, statistics, adapter state bits, endpoint state bits, per-CPU work queues, and firmware context IDs. The header also declares module parameters such as queue sizes, event coalescing, delayed ACK, and error masks.

## Dependencies and Integration Points

It includes Linux PCI, networking, kthread, CPU hotplug, SCSI, libiscsi, iSCSI transport, CNIC, HSI, and bnx2x management firmware request headers. It is the common contract across all bnx2i source files and the CNIC callback table.

## Risks and Edge Cases

Structure layout and constants directly drive firmware-visible DMA and MMIO behavior. Queue size limits vary by device family, and 577xx doorbells/page tables differ from 570x devices. State bits are shared across process context, softirq/KCQ callbacks, kthreads, timers, and network events, so locking expectations must be respected by all users. Statistics helpers differ for 32-bit and 64-bit builds.

## Test Signals

Useful signals include all architecture builds, structure size/alignment checks for firmware layouts, queue-size module parameter tests, adapter state transitions under netdev up/down, endpoint state transitions through connect/disconnect, per-CPU completion processing, stats retrieval, and sparse/lockdep coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i_hwi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i_hwi.c

## Purpose

`bnx2i_hwi.c` implements the hardware interface for bnx2i. It sizes and allocates queue pairs, builds firmware KWQEs and SQ WQEs, rings doorbells, processes CQEs and KCQEs, handles TCP/iSCSI error notifications, and provides the CNIC ULP callback table.

## Important APIs, Types, and Functions

Externally used functions include `bnx2i_arm_cq_event_coalescing()`, `bnx2i_get_rq_buf()`, `bnx2i_put_rq_buf()`, `bnx2i_send_iscsi_login()`, `bnx2i_send_iscsi_tmf()`, `bnx2i_send_iscsi_text()`, `bnx2i_send_iscsi_scsicmd()`, `bnx2i_send_iscsi_nopout()`, `bnx2i_send_iscsi_logout()`, `bnx2i_update_iscsi_conn()`, `bnx2i_ep_ofld_timer()`, `bnx2i_send_cmd_cleanup_req()`, `bnx2i_send_conn_destroy()`, `bnx2i_send_conn_ofld_req()`, `bnx2i_alloc_qp_resc()`, `bnx2i_free_qp_resc()`, `bnx2i_send_fw_iscsi_init_msg()`, `bnx2i_process_scsi_cmd_resp()`, `bnx2i_percpu_io_thread()`, and `bnx2i_map_ep_dbell_regs()`.

Important internal handlers include CQE processors for login, text, TMF, logout, NOP-In, async, reject, cleanup, fast-path notifications, connection update, TCP/iSCSI errors, offload completion, and destroy completion. The global `bnx2i_cnic_cb` exports callbacks to CNIC.

## Control Flow

Firmware init is started by `bnx2i_send_fw_iscsi_init_msg()`, which adjusts QP sizes, builds INIT1/INIT2 KWQEs, sets tolerated protocol error masks, and submits them through CNIC. Connection offload uses either 570x or 5771x KWQE layout, with different page-table offsets and additional 5771x WQE data. After login negotiation, `bnx2i_update_iscsi_conn()` sends negotiated digest, burst, PDU length, R2T, and ERL parameters.

Outbound iSCSI PDUs are written into the current SQ entry by `bnx2i_send_iscsi_*()` routines and posted by `bnx2i_ring_dbell_update_sq_params()`. The doorbell path updates SQ producer pointers, increments active command count, flushes WQE memory with `wmb()`, and either writes 570x doorbell registers or 577xx host-memory doorbell structures plus MMIO trigger.

Incoming KCQ notifications are dispatched by `bnx2i_indicate_kcqe()`. Fast-path notifications call `bnx2i_process_new_cqes()`, which walks CQEs by expected sequence number, dispatches by iSCSI opcode, queues SCSI command responses to per-CPU threads, handles middle-path responses inline, replenishes RQ entries, advances CQ pointers, and re-arms CQ event coalescing.

## State and Persistence Behavior

No durable storage is used. Runtime state includes QP DMA memory/page tables, CQ expected sequence number, SQ/RQ/CQ producer and consumer pointers, 577xx doorbell host-memory areas, endpoint state bits, active command counters, generic PDU response buffers, per-connection violation notification masks, per-CPU work queues, and HBA protocol error masks/statistics.

## Dependencies and Integration Points

The file depends on `bnx2i.h`, HSI structures, libiscsi task lookup and completion APIs, SCSI command/request CPU affinity, CNIC KWQE/KCQE callbacks, netdev events, PCI MMIO mapping, DMA allocation, timers, kthreads, and iSCSI offload netlink messaging.

## Risks and Edge Cases

Queue memory is shared with firmware; ordering before doorbell writes is critical. CQ processing relies on monotonically advancing `cq_req_sn`; missed or stale CQEs stall completions. SCSI completions are offloaded to per-CPU kthreads, but allocation failure falls back to inline processing. RQ accounting must match firmware behavior for zero-length unsolicited PDUs. Error masks can turn protocol violations into warnings, affecting recovery. 570x and 577xx page-table and doorbell formats differ substantially. Endpoint state transitions are woken by timers, CNIC callbacks, network events, and KCQEs, so missed wakeups can hang connect or teardown.

## Test Signals

Validate firmware init, queue-size adjustment, 570x and 577xx offload, doorbell mapping, login/text/logout/NOP/TMF/SCSI PDUs, SCSI sense data through RQ, CQ sequence wrap, per-CPU completion path and CPU offline fallback, event coalescing behavior, protocol warning/recovery masks, TCP FIN/RST/error recovery, netdev up/down/change events, and QP allocation/free failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i_hwi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i_init.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i_init.c

## Purpose

`bnx2i_init.c` owns module-level lifecycle and adapter registration for the bnx2i iSCSI offload driver. It registers the libiscsi transport and CNIC ULP, creates per-CPU completion threads, handles CNIC start/stop/init/exit callbacks, tracks adapters globally, and exposes module parameters.

## Important APIs, Types, and Functions

Exported or callback functions include `bnx2i_identify_device()`, `get_adapter_list_head()`, `bnx2i_find_hba_for_cnic()`, `bnx2i_start()`, `bnx2i_stop()`, `bnx2i_ulp_init()`, `bnx2i_ulp_exit()`, and `bnx2i_get_stats()`. Internal helpers include `bnx2i_chip_cleanup()`, `bnx2i_init_one()`, `bnx2i_cpu_online()`, `bnx2i_cpu_offline()`, `bnx2i_mod_init()`, and `bnx2i_mod_exit()`.

Global state includes `adapter_list`, `adapter_count`, `bnx2i_dev_lock`, module parameters for event coalescing, delayed ACK, error masks, SQ/RQ sizes, `iscsi_error_mask`, the per-CPU `bnx2i_percpu` storage, and the CPU hotplug state handle.

## Control Flow

Module init prints the version, normalizes `sq_size`, registers the bnx2i iSCSI transport, registers the CNIC iSCSI ULP callbacks, initializes per-CPU work lists, and registers CPU hotplug callbacks that start `bnx2i_thread/%d` completion threads. Module exit removes adapters, unregisters CNIC devices, frees HBAs, removes CPU hotplug state, and unregisters transport/CNIC driver.

CNIC calls `bnx2i_ulp_init()` for devices; it allocates an HBA, identifies PCI/device state through `bnx2i_init_one()`, registers with CNIC, and links the adapter into `adapter_list`. `bnx2i_start()` sends firmware iSCSI init and polls up to about one second for `ADAPTER_STATE_UP` or init failure. `bnx2i_stop()` sets going-down state, drops all sessions, waits for offload/destroy lists and active connections to drain, performs chip cleanup if needed, and clears adapter up/down bits.

## State and Persistence Behavior

The file stores runtime adapter and module state only. Adapter registration state persists while the module is loaded or the CNIC device remains present. Per-CPU threads persist while CPUs are online. Module parameters persist for the module lifetime and affect firmware init, queue sizing, delayed ACK, coalescing, and error classification.

## Dependencies and Integration Points

It integrates with libiscsi transport registration, CNIC ULP registration, CPU hotplug, kthreads, netdev/CNIC device lifetimes, PCI IDs, HBA allocation/free in `bnx2i_iscsi.c`, and hardware init/cleanup in `bnx2i_hwi.c`. Stats are copied to CNIC-provided stats memory.

## Risks and Edge Cases

The adapter list is global and must remain protected by `bnx2i_dev_lock`. Stop paths must handle absent or slow user-space iSCSI daemon cleanup by forcefully disconnecting hardware endpoints. CPU offline drains queued completion work inline before stopping the thread, but new queueing must be blocked first. Module exit ordering unregisters transport before CNIC driver in init failure paths but the normal exit unregisters CNIC after transport removal, so lifetime assumptions across callbacks need care. Firmware init can fail when downloaded firmware lacks iSCSI support.

## Test Signals

Validate module load/unload, CNIC device hotplug, duplicate registration failures, firmware init success and license/init failure, network down cleanup with active sessions, per-CPU thread creation/removal, CPU hotplug while completions are queued, stats retrieval, module parameter effects, and absence of adapter/HBA leaks after CNIC exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i_init.c -->
