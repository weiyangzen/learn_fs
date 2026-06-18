# subset-b-005278 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/task.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/task.c

Purpose: implements Intel ISCI libsas task submission and task-management callbacks, bridging `struct sas_task` and libsas error handling into SCI controller requests, tags, remote-device state, and completions.

Important APIs and functions: `isci_task_execute_task()` is the normal I/O entry point; it looks up `isci_remote_device`, checks `IDEV_IO_READY` or NCQ recovery, allocates a tag, builds an `isci_request`, and calls `isci_request_execute()`. `isci_task_abort_task()`, `isci_task_lu_reset()`, and `isci_task_I_T_nexus_reset()` are libsas error-handler paths. `isci_task_execute_tmf()` sends SSP task-management requests with a stack completion and timeout. `isci_task_request_complete()` is the SCI completion hook for TMFs. Unsupported callbacks such as clear nexus and task-set operations currently return `TMF_RESP_FUNC_FAILED`.

Control flow: submission refuses missing devices with `SAS_DEVICE_UNKNOWN`, refuses unready devices or tag exhaustion as `SAS_QUEUE_FULL`, and frees tags if a command never reaches hardware. Abort first validates `task->lldd_task` under host and task locks, suspends and terminates the remote node context, then either completes locally for SMP/SATA/already-complete/gone targets or sends SSP abort TMF. LUN reset terminates pending I/O and either schedules SATA reset or sends SSP LUN reset. I_T nexus reset performs phy hard reset/local reset after terminate.

State and persistence: state is in live kernel objects only: task flags, request flags (`IREQ_COMPLETE_IN_TARGET`, `IREQ_TERMINATED`, abort-path bits), controller tags, RNC/device flags, and TMF completion/status fields. No persistent on-disk state exists.

Dependencies and integration: depends on libsas, SCSI midlayer status conventions, ISCI host/device/request APIs, SCI controller calls, port/phy reset helpers, and kernel completions/spinlocks. It is invoked by the SAS domain template and by SCI completion code.

Risks and test signals: race coverage around task completion versus abort is critical because stale `lldd_task` or double tag free would corrupt I/O state. Validate missing-device, tag-exhaustion, NCQ recovery, SATA reset, SSP abort, TMF timeout, hot-unplug, and eventq wakeup paths. Dynamic signals include `dev_dbg/dev_warn`, successful SCSI retry behavior on queue full, and no leaked tags after failed `isci_request_execute()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/task.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/task.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/task.h

Purpose: declares the ISCI task-management interface used between libsas callbacks, request construction, and SCI task completion, plus the compact TMF object used by `task.c`.

Important APIs and types: `enum isci_tmf_function_codes` maps ISCI TMF names to libsas TMF opcodes for abort-task and LUN-reset. `struct isci_tmf` carries a completion pointer, SAS protocol, LUN bytes, managed I/O tag, TMF code, completion status, and a response union large enough for SSP response IU or SATA D2H FIS. Public prototypes expose task execution, abort, abort/clear task set, query, LUN reset, nexus reset, completion, and SSP task request accessors.

Control flow role: the header is not executable policy, but it fixes the data contract used when `task.c` builds a TMF, stores a stack completion in `tmf->complete`, and later copies response data in `isci_task_request_complete()`. `isci_print_tmf()` is an inline diagnostic branch that formats either SATA or SSP response fields according to `tmf->proto`.

State and persistence: `struct isci_tmf` is transient per management operation. The response union must remain last because it overlays protocol-specific response layouts and includes the max SSP response buffer. No persistent state exists.

Dependencies and integration: includes libsas ATA helpers and ISCI host definitions. Prototypes bind to libsas domain-template callbacks and SCI request helper functions implemented elsewhere in the ISCI driver.

Risks and test signals: protocol selection must be set before response logging/copying or the wrong union member is interpreted. Future TMF additions need corresponding construct and completion handling. Compile coverage should catch signature drift; runtime debug logs from `isci_print_tmf()` help verify SSP/SATA status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/task.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/unsolicited_frame_control.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/unsolicited_frame_control.c

Purpose: manages ISCI unsolicited-frame DMA memory layout and release ordering for frames delivered by the SCU hardware outside normal request context.

Important APIs and functions: `sci_unsolicited_frame_control_construct()` lays out frame buffers, header table, and address table inside `ihost->ufi_buf`/`ihost->ufi_dma`. `sci_unsolicited_frame_control_get_header()` and `_get_buffer()` validate frame indices and return header data or payload buffer pointers. `sci_unsolicited_frame_control_release_frame()` marks a frame released and advances the software get pointer only when all earlier frames are releasable.

Control flow: construction starts buffers at the beginning of the UFI region, headers after `SCI_UFI_BUF_SIZE`, address table after `SCI_UFI_HDR_SIZE`, then fills `SCU_MAX_UNSOLICITED_FRAMES` entries with consecutive 1 KiB DMA buffers. Release computes ring index and cycle from `uf_control->get`, skips null address-table slots, rejects invalid indices, marks the target released, and only advances contiguous released entries to empty before writing an enabled get pointer value.

State and persistence: state is volatile in `sci_unsolicited_frame_control`: `get`, address-table entries, per-frame `state`, and virtual/physical table pointers. Hardware consumes the DMA addresses and get pointer. No disk persistence.

Dependencies and integration: depends on ISCI host allocation of UFI memory, SCU register bit macros, DMA address sizing, and controller code that writes `uf_control->get` to hardware after release.

Risks and test signals: the release loop is sensitive to ring off-by-one behavior and null table assumptions; a bad last null entry triggers `BUG_ON`. Tests should exercise in-order release, out-of-order release, invalid indices, all frames wrapping the cycle bit, and address/header alignment. Hardware bring-up should confirm no unsolicited-frame starvation after partial release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/unsolicited_frame_control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/unsolicited_frame_control.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/unsolicited_frame_control.h

Purpose: defines the data structures and sizing macros for ISCI SCU unsolicited-frame buffers, headers, and address tables.

Important APIs and types: `struct scu_unsolicited_frame_header` mirrors the hardware header word plus 15 dwords of received frame header data. `enum unsolicited_frame_state` tracks empty, in-use, released, and max states. `struct sci_unsolicited_frame` binds state, header pointer, and payload buffer. Header, buffer, and address-table array wrappers carry virtual arrays and DMA addresses. `struct sci_unsolicited_frame_control` aggregates the software get pointer plus those arrays. `SCI_UFI_BUF_SIZE`, `SCI_UFI_HDR_SIZE`, and `SCI_UFI_TOTAL_SIZE` define allocation sizing.

Control flow role: consumer code constructs the layout, retrieves headers/buffers by frame index, processes unsolicited arrivals, and releases frames using the prototypes declared here. The header’s first control word is explicitly separate from `data[]`, which is why `get_header()` returns `header->data`.

State and persistence: all fields describe DMA-backed runtime memory and software queue state. The hardware address table contains 64-bit DMA pointers to 1 KiB frame buffers; the state enum gates when software may advance the get pointer.

Dependencies and integration: depends on ISCI constants such as `SCU_MAX_UNSOLICITED_FRAMES` and `SCU_UNSOLICITED_FRAME_BUFFER_SIZE`, Linux `dma_addr_t`, and SCI status definitions.

Risks and test signals: structure layout and alignment must match silicon requirements. Watch for 32/64-bit DMA pointer assumptions, bitfield compiler layout, and stale frame states. Useful tests validate total allocation size, frame index bounds, and that release does not make a buffer reusable before older frames are processed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/unsolicited_frame_control.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/iscsi_boot_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/iscsi_boot_sysfs.c

Purpose: provides a reusable sysfs library for exporting firmware/iBFT iSCSI boot information under firmware ksets, with target, ethernet, initiator, and ACPI table attribute groups.

Important APIs and functions: exported constructors include `iscsi_boot_create_kset()`, `iscsi_boot_create_host_kset()`, `iscsi_boot_create_target()`, `iscsi_boot_create_ethernet()`, `iscsi_boot_create_initiator()`, and `iscsi_boot_create_acpitbl()`. `iscsi_boot_destroy_kset()` tears down all child kobjects. `struct iscsi_boot_attr` binds sysfs attribute name/mode to an `ISCSI_BOOT_*` type and caller-provided `show` handler. Visibility callbacks delegate each attribute to driver-provided `is_visible()`.

Control flow: a caller creates a kset, then child kobjects through `iscsi_boot_create_kobj()`. That helper allocates `iscsi_boot_kobj`, initializes and adds the kobject, stores data/show/visibility/release callbacks, creates the group, emits `KOBJ_ADD`, and appends to `kobj_list`. Reads go through `iscsi_boot_show_attribute()`, require `CAP_SYS_ADMIN`, and call the provider’s `show(data, type, buf)`. Destroy walks the list safely, removes groups, drops kobject refs, unregisters the kset, and frees the wrapper.

State and persistence: sysfs objects persist while the module/driver keeps krefs; provider data is released via callback from `iscsi_boot_kobj_release()`. No durable state is written, but exported attributes expose boot configuration to user space.

Dependencies and integration: integrates with Linux kobjects/sysfs, `firmware_kobj`, iSCSI boot enum definitions, module exports, and drivers such as iBFT or NIC firmware providers.

Risks and test signals: access control matters because CHAP secrets are represented as readable attributes to admin-only callers. Error paths intentionally null `release` after group creation failure to avoid freeing data the caller still owns. Tests should cover hidden attributes, permission denial for non-admin, create/destroy cycles, failed allocation/group creation, and absence of use-after-free during concurrent sysfs reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/iscsi_boot_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/iscsi_tcp.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/iscsi_tcp.c

Purpose: implements the software iSCSI-over-TCP initiator transport data path, connecting libiscsi/libiscsi_tcp session and PDU machinery to a userspace-supplied TCP socket.

Important APIs and functions: socket callbacks are installed/restored by `iscsi_sw_tcp_conn_set_callbacks()` and `_restore_callbacks()`. Receive runs through `iscsi_sw_tcp_data_ready()`, optional `recvwork`, `tcp_read_sock()`, and `iscsi_tcp_recv_skb()`. Transmit is driven by `iscsi_sw_tcp_pdu_init()`, header/data prep helpers, `iscsi_sw_tcp_pdu_xmit()`, and `iscsi_sw_tcp_xmit_segment()`. Transport callbacks create/destroy sessions and connections, bind sockets, set/get params, gather stats, and register as `iscsi_transport` named `tcp`.

Control flow: userspace creates a session, creates a connection, and binds a TCP socket fd. Bind validates TCP, binds libiscsi connection state, stores the socket under `sock_lock`, tunes socket flags, installs callbacks, and primes header receive state. Data-ready either reads in softirq callback context or queues `recvwork`. Write-space chains to the old callback and queues iSCSI transmit. Stop suspends TX, shuts down the socket, restores callbacks, suspends RX, clears the pointer, and calls `iscsi_conn_stop()`.

State and persistence: runtime state is in `iscsi_sw_tcp_conn`: socket pointer, callback backups, mutex, work item, send segment, digest CRCs, and counters. Session state is linked through `iscsi_sw_tcp_host`. No on-disk persistence; parameters are exposed through transport sysfs/netlink.

Dependencies and integration: depends on TCP sockets, SCSI host/session lifecycle, libiscsi task management, libiscsi_tcp segment/digest helpers, tracepoints, and block queue limits. Data digest enables stable writes in `sdev_configure()`.

Risks and test signals: callback locking and socket lifetime are the main hazards, especially stop/destroy races with data-ready and param reads. Test digest on/off, queued versus softirq receive, partial sends/EAGAIN, socket close with pending receive memory, bind failure, local/peer address reads, module unload, and stable-write feature with data digests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/iscsi_tcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/iscsi_tcp.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/iscsi_tcp.h

Purpose: declares private data structures for the software iSCSI TCP transport.

Important APIs and types: `struct iscsi_sw_tcp_send` contains the current outgoing header pointer, active segment, and data segment. `struct iscsi_sw_tcp_conn` stores the bound socket, `sock_lock`, receive work and queuing flag, outgoing send state, original socket callbacks, TX/RX CRC accumulators, and custom stats counters. `struct iscsi_sw_tcp_host` links a SCSI host to its iSCSI session. `struct iscsi_sw_tcp_hdrbuf` reserves a base iSCSI header plus AHS and digest space for task headers.

Control flow role: `iscsi_tcp.c` allocates these as per-connection, per-host, and per-task private areas through libiscsi setup calls. Send prep writes into `out.segment`/`out.data_segment`; callback installation uses the saved function pointers to restore the socket later.

State and persistence: all structures are in-memory lifecycle state tied to sessions, connections, and tasks. The socket pointer is guarded for netlink/sysfs access by `sock_lock`.

Dependencies and integration: includes `libiscsi.h` and `libiscsi_tcp.h`, and relies on kernel socket, workqueue, mutex, and CRC types.

Risks and test signals: structure sizing must match allocations in `iscsi_tcp_conn_setup()` and task `dd_data`; header max calculations reserve digest space. Validate that every successful callback install has a restore path and that stats fields remain coherent across reconnects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/iscsi_tcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/jazz_esp.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/jazz_esp.c

Purpose: platform front-end for NCR ESP SCSI on MIPS JAZZ systems, wiring the generic `esp_scsi` core to JAZZ memory-mapped registers, VDMA, IRQ, and platform-device resources.

Important APIs and functions: `jazz_esp_ops` provides register read/write, interrupt-pending, DMA reset/drain/invalidate, DMA command submission, and DMA error callbacks to the ESP core. `esp_jazz_probe()` allocates `Scsi_Host`, initializes `struct esp`, obtains register and DMA resources, allocates a coherent command block, requests IRQ, sets SCSI ID and clock, and registers the ESP host. `esp_jazz_remove()` unregisters and frees those resources.

Control flow: DMA command submission programs transfer count registers, disables VDMA, selects VDMA direction using ESP write semantics, programs address/count, enables VDMA, then sends the ESP command. Probe unwinds in reverse order on resource failures. Remove unregisters from SCSI first, then frees IRQ, command block, and host.

State and persistence: state lives in the allocated SCSI host/private ESP object, hardware registers, VDMA controller, and coherent command block. No persistent state exists.

Dependencies and integration: depends on MIPS JAZZ platform headers, `jazzdma` VDMA helpers, platform-device resources, shared IRQ handling through `scsi_esp_intr`, and the generic ESP SCSI core.

Risks and test signals: direction mapping between ESP write and DMA mode is hardware-specific and easy to regress. Tests/signals include successful platform probe, IRQ delivery, DMA error reporting for `R4030_MEM_INTR`/`R4030_ADDR_INTR`, command completion under read/write workloads, and correct cleanup after probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/jazz_esp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lasi700.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/lasi700.c

Purpose: PARISC LASI front-end for NCR 53c700/53c710 SCSI chips, configuring chip parameters and registering the generic `53c700` SCSI core as a PARISC driver.

Important APIs and functions: `lasi700_probe()` allocates `NCR_700_Host_Parameters`, maps LASI SCSI registers, selects clock/endian/chip710/burst parameters based on `sversion`, calls `NCR_700_detect()`, requests IRQ, stores driver data, and scans the host. `lasi700_driver_remove()` removes the host, releases the core, IRQ, mapping, and host parameters. `lasi700_init()`/`lasi700_exit()` register and unregister the PARISC driver.

Control flow: matching is by PARISC device IDs for LASI 700 and 710. Probe builds `base = hpa.start + LASI_SCSI_CORE_OFFSET`, sets 32-bit DMA mask, maps 0x100 bytes, and follows standard SCSI host registration. Failure unwinds through `scsi_host_put`, `iounmap`, and `kfree`.

State and persistence: state is in `hostdata`, MMIO mapping, SCSI host fields, and PARISC driver data. No durable state exists.

Dependencies and integration: depends on PARISC firmware/device model, generic 53c700 core, SCSI transport/SPI headers, shared IRQ handling via `NCR_700_intr`, and `scsi_scan_host()`.

Risks and test signals: version-specific parameters must match hardware; endian forcing for LASI700 and burst/DMODE for LASI710 are key. Tests should cover probe/remove on both device IDs, IRQ request failure cleanup, DMA mask behavior, host scanning, and no leaked ioremap/hostdata on detection failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lasi700.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libfc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/libfc/Makefile

Purpose: defines how the Fibre Channel libfc library object is built when `CONFIG_LIBFC` is enabled.

Important build API: `obj-$(CONFIG_LIBFC) += libfc.o` makes libfc conditional on kernel config. `libfc-objs` composes the library from `fc_libfc.o`, discovery, exchange, ELS/CT, frame, local-port, remote-port, FCP, and NPIV objects.

Control flow role: this file controls link composition, not runtime behavior. It ensures cross-file symbols such as exchange manager APIs, discovery callbacks, ELS/CT sending, FCP I/O, and NPIV support are linked into the single module/library object.

State and persistence: no runtime state. Build output depends on Kbuild and config state.

Dependencies and integration: integrates with kernel Kbuild and the SCSI/FCoE stack. Object order can matter for init/exit symbol availability and diagnostics but normal C linking resolves internal references across listed objects.

Risks and test signals: missing an object would cause unresolved symbols or disabled functionality; extra objects can change module footprint. Build tests with `CONFIG_LIBFC=m/y` are the primary signal, plus module load coverage for exported symbols used by LLDDs such as fcoe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libfc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libfc/fc_disc.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/libfc/fc_disc.c

Purpose: implements libfc target discovery for FC-4/FCP ports, including full fabric name-server scans, RSCN handling, single-port rediscovery, retry, and remote-port login/logoff decisions.

Important APIs and functions: `fc_disc_init()` initializes mutex, delayed work, and rport list. `fc_disc_config()` installs transport-template callbacks for start/stop/final-stop/request receive. Internally, `fc_disc_start()` and `fc_disc_restart()` launch discovery; `fc_disc_gpn_ft_req()` sends GPN_FT through `elsct_send`; `fc_disc_gpn_ft_resp()` parses multi-frame CT responses; `fc_disc_single()` and `fc_disc_gpn_id_req()` handle RSCN port-specific checks; `fc_disc_done()` reconciles rport generations.

Control flow: full discovery increments nonzero odd `disc_id`, sends GPN_FT for FCP, parses returned FIDs/WWPNs, creates or updates rports with the current generation, and on completion logs in current rports or logs off stale ones. RSCN validates payload pages, accepts the ELS, builds a temporary list of changed port IDs for GPN_ID when possible, and falls back to full rediscovery for area/domain/fabric notifications or allocation/error cases. Errors retry up to three times with delay, treating name-server “FC-4 type not registered” as success.

State and persistence: `struct fc_disc` holds `pending`, `requested`, retry count, generation `disc_id`, partial GPN_FT record buffer, sequence count, delayed work, callback, and rport list. State is live only and protected by `disc_mutex`.

Dependencies and integration: depends on libfc local-port readiness, ELS/CT transport, FC name-server structures, rport lifecycle, delayed work, and libfc locking order.

Risks and test signals: partial CT response parsing, discovery restart during callbacks, and rport kref handling are high-risk. Test RSCN malformed frames, full and partial GPN_FT sequences, timeout/retry exhaustion, zoning rejection, WWPN change on same FCID, stop/final-stop flushing, and lockdep for disc/rport/lport ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libfc/fc_disc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libfc/fc_elsct.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/libfc/fc_elsct.c

Purpose: provides the libfc helper for sending ELS and CT requests with the proper payload encoding, FC header fields, exchange allocation, response callback, and timeout.

Important APIs and functions: `fc_elsct_send()` is exported and selected into `lport->tt.elsct_send` by `fc_elsct_init()`. `fc_els_resp_type()` turns ELS/CT response frames or encoded exchange errors into diagnostic strings.

Control flow: `fc_elsct_send()` classifies opcodes in the ELS range and calls `fc_els_fill()`, otherwise calls `fc_ct_fill()`, allowing CT fill to rewrite destination to directory or management service. On encoding failure it frees the frame. On success it fills the FC header with request F_CTL and sends through `fc_exch_seq_send()`, which creates the exchange and arms the response timeout. `fc_els_resp_type()` inspects `IS_ERR` values, FC frame type, ELS opcode, or CT command to return accept/reject/timeout/unknown descriptions.

State and persistence: no standalone state; state is carried in the frame, local port, exchange manager, callback argument, and timeout.

Dependencies and integration: depends on `fc_encode.h`, FC ELS/GS/NS headers, `fc_fill_fc_hdr()`, and exchange manager APIs. Used by discovery, local-port login, remote-port flows, and FDMI/name-server registration code.

Risks and test signals: opcode classification must stay aligned with FC definitions, and CT destination rewrite is essential for management versus directory service. Test each ELS helper, common CT NS and FDMI opcodes, frame-free on invalid op, timeout callback, and response-type strings for short CT frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libfc/fc_elsct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libfc/fc_encode.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/libfc/fc_encode.h

Purpose: inline construction library for libfc ELS, name-server CT, and FDMI management CT request payloads.

Important APIs and types: `FC_FCTL_REQ` and `FC_FCTL_RESP` define common frame-control flags. `struct fc_ct_req` overlays supported CT request payloads. Helpers include `fc_adisc_fill()`, `fc_ct_hdr_fill()`, `fc_ct_ns_fill()`, `fc_ct_ms_fill()`, `fc_ct_fill()`, `fc_plogi_fill()`, `fc_flogi_fill()`, `fc_fdisc_fill()`, `fc_logo_fill()`, `fc_rtv_fill()`, `fc_rec_fill()`, `fc_prli_fill()`, `fc_scr_fill()`, and dispatcher `fc_els_fill()`.

Control flow: ELS helpers zero the frame payload and populate command-specific fields from `fc_lport` identity, service parameters, exchange IDs, and timeout values. Name-server CT supports GPN_FT/GPN_ID and registration of FC-4 type, features, node name, port symbolic name, and node symbolic name. FDMI CT builds RHBA, RPA, DPRT, and DHBA payloads with many fixed-length attributes from FC host sysfs attributes, OS name/release, and port state. `fc_ct_fill()` chooses management service for `FC_FID_MGMT_SERV`, otherwise directory service.

State and persistence: functions write only into the provided frame payload. They snapshot lport/host fields such as WWPN, WWNN, port ID, speed, symbolic names, and FDMI version.

Dependencies and integration: depends on FC protocol headers, unaligned big-endian helpers, `fc_frame_payload_get()`, SCSI FC host attribute accessors, and `init_utsname()`.

Risks and test signals: payload length math and fixed FDMI attribute stepping are easy to break. Test buffer sizing for FDMI v1/v2, symbolic-name truncation and zero-fill, endian encoding of IDs/WWNs, invalid opcode returns, and that ELS/CT headers match expected R_CTL/type values when sent through `fc_elsct_send()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libfc/fc_encode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libfc/fc_exch.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/libfc/fc_exch.c

Purpose: implements libfc Fibre Channel exchange and sequence management: XID allocation, frame send/receive routing, response callbacks, abort/REC/RRQ recovery, reset, statistics, and exchange-manager lifecycle.

Important APIs and functions: exported APIs include `fc_seq_send()`, `fc_seq_start_next()`, `fc_seq_set_resp()`, `fc_seq_exch_abort()`, `fc_exch_done()`, `fc_seq_els_rsp_send()`, `fc_seq_assign()`, `fc_seq_release()`, `fc_exch_seq_send()`, `fc_exch_update_stats()`, `fc_exch_mgr_add/del/list_clone/alloc/free/reset()`, `fc_exch_recv()`, `fc_exch_init()`, `fc_setup_exch_mgr()`, and `fc_destroy_exch_mgr()`. Core types are private `fc_exch_mgr`, per-CPU `fc_exch_pool`, `fc_exch_mgr_anchor`, and libfc `fc_exch`/`fc_seq`.

Control flow: send of a new exchange allocates from the first matching exchange-manager anchor, chooses a per-CPU XID slot, initializes exchange/sequence, fills OX_ID/RX_ID/SEQ fields, optionally sets FCP DDP, sends via `frame_send`, and arms a timer. Receive selects an EM by XID, trims fill bytes, then dispatches BLS, originated-sequence responses, recipient responses, or new requests. BLS handles ACK, ABTS, BA_ACC/BA_RJT. Timeouts invoke upper-layer response with `-FC_EX_TIMEOUT`, clear response handlers, and send ABTS. Completed exchanges are removed from pools and released through mempool refs.

State and persistence: exchange state is live in per-CPU XID arrays, `ex_list`, refcounts, sequence counters, `esb_stat`, `state`, OXID/RXID/SID/DID/OID, response callback fields, delayed timeout work, and recovery-qualifier refs. Manager stats are atomics folded into host stats. No disk persistence.

Dependencies and integration: depends on libfc frame/local-port/FCP/rport services, mempool/slab/percpu allocation, ordered workqueue, FC-FS frame semantics, and LLDD `frame_send` callbacks. Offload drivers can add EM anchors with match functions and XID ranges.

Risks and test signals: this is concurrency-heavy. Key risks are refcount imbalance between timers, recovery qualifiers, pool holds, and callback holds; XID reuse while quarantined; response-handler races; reset while callback active; and ABTS/RRQ/REC corner cases. Test high CPU counts/XID ranges, timeout then ABTS response, REC/RRQ accept/reject, lport reset, NPIV destination lookup, DDP setup teardown on send error, invalid EOF drops, and stats increments for not-found/busy/no-free paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/libfc/fc_exch.c -->
