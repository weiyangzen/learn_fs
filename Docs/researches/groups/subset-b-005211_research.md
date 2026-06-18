# subset-b-005211 grouped research

Grouped research for s390 CIO, QDIO, EADM, SCM, trace, and vfio-ccw support files. Each source file section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/device_fsm.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/device_fsm.c

Purpose: implements the CCW device finite state machine for recognition, online/offline transitions, path verification, timeout recovery, disconnection, boxed devices, and interrupt delivery to upper drivers.

Important APIs/types/functions: exports `ccw_device_set_timeout()` and provides core entry points `ccw_device_timeout()`, `ccw_device_recognition()`, `ccw_device_online()`, `ccw_device_offline()`, `ccw_device_verify_done()`, `ccw_device_notify()`, `ccw_device_trigger_reprobe()`, and `ccw_device_kill_io()`. `dev_jumptable[NR_DEV_STATES][NR_DEV_EVENTS]` maps `enum dev_state` and `enum dev_event` to action handlers. Helpers such as `ccw_device_call_handler()`, `ccw_device_irq()`, `ccw_device_w4sense()`, and `ccw_device_online_verify()` bridge accumulated IRBs, delayed SENSE, and path verification.

Control flow: recognition enables the subchannel, starts SENSE ID, and finishes through `ccw_device_recog_done()` into offline, boxed, or not-operational states. Online setup enables the subchannel and starts PGID/NOOP path verification. Normal interrupts in `DEV_STATE_ONLINE` accumulate IRB status, optionally start basic sense, and call the driver handler only when the status policy permits. Timeouts stop the request with cancel/halt/clear and may move to `DEV_STATE_TIMEOUT_KILL` while waiting for completion. Path events can defer verification until current I/O has delivered final status.

State and persistence behavior: mutable state lives in `struct ccw_device_private` flags, path masks, `intparm`, `async_kill_io_rc`, wait queue, timer, and DMA IRB buffer; `struct subchannel` contributes `lpm`, `opm`, `vpm`, and SCHIB configuration. No disk persistence exists. Hardware state is refreshed with `stsch()`/`cio_update_schib()` and committed through CIO helpers.

Dependencies and integration points: depends on `device.h` states, request handling from the CCW request layer, `device_id.c`, `device_pgid.c`, `device_status.c`, CIO low-level operations, CSS work scheduling, channel-path registration, CMF retry helpers, and driver callbacks `notify`, `path_event`, and `handler`.

Risks and test signals: high-risk behavior is around lost interrupts, fake IRB delivery while verification is active, timeout stop escalation, path mask drift, and notifier decisions for disconnected or boxed devices. Test signals include recognition success/failure/timeout, online/offline with and without path grouping, unit-check delayed sense, unsolicited interrupts, not-operational events, reprobe on disconnected devices, CMF transition states, and timeout logging via `ccw_timeout_log`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/device_fsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/device_id.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/device_id.c

Purpose: performs CCW device SENSE ID discovery and normalizes returned control-unit/device identity data for the device FSM.

Important APIs/types/functions: `ccw_device_sense_id_start()` builds a SENSE ID CCW in the device DMA area and starts it through the internal `ccw_request` engine. `snsid_init()`, `snsid_check()`, and `snsid_callback()` validate response length, `reserved == 0xff`, CU type, and extended CIW availability. On z/VM, `diag210_get_dev_info()` and `diag210_to_senseid()` provide a fallback mapping for older virtual devices.

Control flow: SENSE ID setup clears the DMA `senseid` buffer, places `0xffff` as an incomplete sentinel, configures timeout/retry/path mask, and calls `ccw_request_start()`. The request check restarts incomplete responses with `-EAGAIN`, marks extended sense ID when CIWs are present, or rejects incompatible payloads. The callback may retry via DIAG 0x210 on VM and then completes through `ccw_device_sense_id_done()`.

State and persistence behavior: state is transient in `cdev->private->dma_area->senseid`, `flags.esid`, and the internal request. `ccw_device_update_sense_data()` in the FSM later copies it into persistent in-memory `cdev->id` for driver matching. No persistent storage is written.

Dependencies and integration points: relies on `io_sch.h` DMA layout, `ccw_request_start()`, SENSE ID command definitions, `machine_is_vm()`, `diag210()`, CIO tracing, and FSM completion.

Risks and test signals: incomplete or malformed SENSE ID can loop until retry exhaustion; VM fallback mappings must stay accurate for common virtual devices such as OSA and printers. Test real and VM paths, SSID nonzero rejection for DIAG 0x210, extended CIW detection, incompatible `reserved` values, timeout to boxed state, and retry behavior for short responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/device_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/device_ops.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/device_ops.c

Purpose: exports the public CCW device operation API used by s390 device drivers to start, halt, clear, resume, query, and allocate DMA memory for CCW and transport-mode I/O.

Important APIs/types/functions: option APIs include `ccw_device_set_options_mask()`, `ccw_device_set_options()`, and `ccw_device_clear_options()`. I/O APIs include `ccw_device_start_timeout_key()`, wrappers for default key/timeout, `ccw_device_halt()`, `ccw_device_clear()`, `ccw_device_resume()`, `ccw_device_tm_start_timeout_key()` and wrappers, and `ccw_device_tm_intrg()`. Query/allocation helpers include `ccw_device_get_ciw()`, path and channel descriptor getters, `ccw_device_get_id()`, `ccw_device_get_schid()`, `ccw_device_pnso()`, CSSID/IID/CHPID/CHID getters, and `ccw_device_dma_zalloc()`/`ccw_device_dma_free()`.

Control flow: start paths validate device/subchannel state, optionally queue a fake command or transport IRB if verification is underway, mask caller path selection against `sch->lpm`, apply CIO options, and call `cio_start_key()` or `cio_tm_start_key()`. Halt/clear/resume validate online or W4SENSE states before invoking low-level CIO instructions. Query helpers read sense-id CIWs, SCHIB path fields, channel-path descriptors, or CSS metadata.

State and persistence behavior: updates in-memory driver options, `private->intparm`, timers, fake IRB flags, QDIO data pointer indirectly, and device reference counts for DMA allocations. Hardware state is changed through CIO start/halt/clear/resume and CHSC/PNSO calls; no long-term persistence exists.

Dependencies and integration points: integrates `ccw_device_private`, `subchannel`, low-level CIO operations, channel-path descriptors, CHSC PNSO, transport-command support from FCX, and exported symbols consumed by CCW class drivers, QDIO users, and vfio-ccw.

Risks and test signals: state validation and fake IRB queuing are sensitive to races with verification. Path masks must not allow varied-off paths. `ccw_device_get_util_str()` assumes a valid channel path object after `chpid_to_chp()`. Tests should cover all state-dependent return codes, path mask filtering, mutually exclusive early/report-all options, transport start with timeout, DMA allocation reference balancing, and descriptor queries for missing paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/device_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/device_pgid.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/device_pgid.c

Purpose: performs CCW path verification and path-group management using NOOP, SENSE PGID, SET PGID, DISBAND, and steal-lock channel programs.

Important APIs/types/functions: `ccw_device_verify_start()` starts the verification workflow, while `ccw_device_disband_start()` tears down path groups for offline. Internal flows are split across `verify_start()`, `nop_do()`/`nop_callback()`, `snid_do()`/`snid_callback()`/`snid_done()`, `spid_do()`/`spid_callback()`, `pgid_wipeout_start()`, and `verify_done()`. `ccw_device_stlck()` performs an unconditional reserve/release sequence for forced lock stealing.

Control flow: verification initializes `sch->vpm`, `sch->lpm`, PGID buffers, and path masks. Without path grouping it runs NOOP one path at a time and records paths that work, time out, or reject access. With path grouping it senses PGIDs, analyzes mismatch/reservation/reset state, fills target PGID data, then issues SET PGID establish/resign commands until `pgid_todo_mask` is empty. Unsupported multipath/pathgroup modes cause fallback and restart.

State and persistence behavior: state is in `pgid_valid_mask`, `pgid_todo_mask`, `pgid_reset_mask`, `path_noirq_mask`, `path_notoper_mask`, `flags.pgid_unknown`, `flags.pgroup`, `flags.mpath`, and `sch->vpm/config.mp`. PGID hardware grouping persists until disbanded or reset by hardware; driver state is in memory.

Dependencies and integration points: depends on internal `ccw_request`, `struct pgid` from CSS, CIO config commit, global CSS PGID, FSM callbacks `ccw_device_verify_done()` and `ccw_device_disband_done()`, and CCW commands `NOOP`, `SENSE_PGID`, `SET_PGID`, `STLCK`, and `RELEASE`.

Risks and test signals: path group state can become partially unknown after timeouts, requiring wipeout. Reserved-by-other paths return `-EUSERS`, mismatched PGIDs disable grouping, and multipath configuration must match `sch->config.mp`. Tests should inject per-path timeout/access/unsupported results, all-reserved paths, mismatched PGIDs, reset PGIDs, disband failures, forced lock stealing, and correct `vpm`/`lpm` outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/device_pgid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/device_status.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/device_status.c

Purpose: accumulates interruption-response-block status for CCW command-mode I/O and starts/finalizes basic sense when concurrent sense data is absent.

Important APIs/types/functions: public helpers are `ccw_device_accumulate_irb()`, `ccw_device_do_sense()`, `ccw_device_accumulate_basic_sense()`, and `ccw_device_accumulate_and_sense()`. Internal helpers copy ECW/ESW fields, validate ESW presence, detect control checks, and handle path-not-operational bits.

Control flow: `ccw_device_accumulate_irb()` ignores IRBs without status pending, logs channel/interface checks, updates path masks when PNO is present, copies transport-mode IRBs wholesale, and otherwise accumulates solicited command-mode SCSW/ESW/ECW fields into the device DMA IRB. Unit check without concurrent sense sets `flags.dosense`. `ccw_device_do_sense()` starts the static SENSE CCW only after device/subchannel activity has ended. W4SENSE completion copies sense information and clears delayed-sense state.

State and persistence behavior: state is accumulated in `cdev->private->dma_area->irb`, `flags.dosense`, `flags.doverify`, and `sch->lpm`. It reflects pending runtime I/O status only and is cleared by the FSM after handler delivery.

Dependencies and integration points: used by `device_fsm.c` online and W4SENSE interrupt handling, by internal request handling, and by CIO low-level start. Depends on SCSW/ESW architecture helpers, `to_io_private(sch)->dma_area->sense_ccw`, and path verification event routing.

Risks and test signals: status validity rules are subtle; copying invalid ESW/ECW fields can mislead drivers. Sense start during active I/O must return busy. Tests should cover command versus transport IRBs, clear-function reset of accumulated status, PNO-triggered verification, unit check with concurrent sense, unit check needing basic sense, activity-pending sense deferral, and channel-control-check logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/device_status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/eadm_sch.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/eadm_sch.c

Purpose: registers and manages s390 Extended Asynchronous Data Mover subchannels and exposes `eadm_start_aob()` for SCM-style asynchronous operation blocks.

Important APIs/types/functions: exported `eadm_start_aob()` selects an idle ADM subchannel, programs an EADM ORB, and starts subchannel I/O. Core callbacks include `eadm_subchannel_probe()`, `eadm_subchannel_irq()`, `eadm_subchannel_timeout()`, `eadm_quiesce()`, and CSS driver methods for remove/shutdown/events. Global `eadm_list` and `list_lock` maintain a simple round-robin pool.

Control flow: probe allocates `struct eadm_private`, sets ISC, enables the subchannel, and adds it to the idle list. Starting an AOB marks a chosen private object busy, arms a timeout, fills EADM ORB fields, and calls `ssch()`. IRQ handling maps SCSW clear/error status to block status, stops the timeout, calls `scm_irq_handler()` with the AOB, returns the subchannel to idle, and completes quiesce waiters. Timeout clears the subchannel.

State and persistence behavior: per-subchannel state is `EADM_IDLE`, `EADM_BUSY`, or `EADM_NOT_OPER`, plus ORB, timer, optional completion, and list node. Hardware AOB execution state exists in the subchannel and is cleared during timeout/remove/shutdown. No persistent storage exists.

Dependencies and integration points: depends on CSS ADM subchannel matching, low-level `ssch()`/`csch()`, ISC registration, debug feature logging, EADM ORB format from `orb.h`, `asm/eadm.h`, and SCM completion callback `scm_irq_handler()`.

Risks and test signals: pool selection and state changes rely on lock ordering between `list_lock` and subchannel locks. Timeout and remove must not leave active AOBs orphaned. Tests should cover unavailable EADM facility, start with no idle subchannel, start failure marking not-operational, timeout clear, unsolicited IRQ, quiesce during busy I/O, and event recovery from `EADM_NOT_OPER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/eadm_sch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/eadm_sch.h -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/eadm_sch.h

Purpose: declares the private per-subchannel state used by the EADM subchannel driver.

Important APIs/types/functions: `struct eadm_private` contains the cached `union orb`, state enum `EADM_IDLE/EADM_BUSY/EADM_NOT_OPER`, optional quiesce completion, owning `struct subchannel *`, timeout timer, and list node. `get_eadm_private()` and `set_eadm_private()` wrap subchannel device driver data.

Control flow: the header itself has no runtime flow, but its accessors are used by probe, start, timeout, IRQ, remove, shutdown, and event paths in `eadm_sch.c`.

State and persistence behavior: state is per-subchannel, in memory, aligned to 8 bytes, and bound to `sch->dev` through driver data. It is allocated at probe and freed at remove.

Dependencies and integration points: includes completion, device, timer, list, and ORB definitions. It is private to CIO EADM/SCM plumbing and should remain synchronized with the EADM driver's locking and lifecycle.

Risks and test signals: misuse risk is mostly lifetime-related: callers must not read private data after remove or without the expected subchannel lock/list lock. Tests are indirect through EADM probe/remove/start/quiesce coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/eadm_sch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/fcx.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/fcx.c

Purpose: provides exported helper functions for constructing and finalizing FCX transport-command-word control blocks.

Important APIs/types/functions: getters and setters include `tcw_get_intrg()`, `tcw_get_data()`, `tcw_get_tccb()`, `tcw_get_tsb()`, `tcw_set_intrg()`, `tcw_set_data()`, `tcw_set_tccb()`, and `tcw_set_tsb()`. Builders include `tcw_init()`, `tccb_init()`, `tsb_init()`, `tccb_add_dcw()`, `tcw_add_tidaw()`, and `tcw_finalize()`. Internal helpers compute TCA size, DCW data counts, and CBC padding for output TIDALs.

Control flow: callers initialize TCW/TCCB/TSB, add DCWs and optional TIDAWs, set pointers, and call `tcw_finalize()`. Finalization terminates the TIDAW list, writes a TCAT into the TCCB, computes input/output counts, transport count, CBC padding, and `tccbl`.

State and persistence behavior: functions mutate caller-supplied memory only. Address fields are converted through DMA32/DMA64 virtual-address helpers and have no persistent backing beyond the supplied buffers.

Dependencies and integration points: consumed by transport-mode CCW drivers and `itcw.c`; relies on `asm/fcx.h` layout contracts, DMA address conversion helpers, Linux error pointers, and exported symbols for loadable modules.

Risks and test signals: buffer sizing and alignment are caller-sensitive. `tcw_finalize()` assumes TCCB `tcal` is current and TIDAW storage is contiguous without TTICs. Tests should cover DCW chaining and non-chaining, `-ENOSPC`, read and write counts, output TIDAL CBC insertion, zero TIDAWs, and pointer round-trips through DMA helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/fcx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/idset.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/idset.c

Purpose: implements a bitmap-backed set of subchannel IDs used by CSS/CIO scanning logic.

Important APIs/types/functions: `struct idset` stores SSID and ID dimensions plus a flexible bitmap. Public functions allocate/free sets, fill them, add/delete/check subchannel IDs, delete subsequent IDs in an SSID range, test emptiness, and OR one set into another.

Control flow: `idset_sch_new()` sizes the set from global `max_ssid` and `__MAX_SUBCHANNEL`. Operations map `(ssid, sch_no)` to `ssid * num_id + id` and then use bitmap primitives. `idset_sch_del_subseq()` clears from a given subchannel number to the end of that SSID.

State and persistence behavior: state is heap/vmalloc bitmap memory only. The set persists until `idset_free()` and has no locking of its own, so callers own synchronization.

Dependencies and integration points: depends on `css.h` for `max_ssid`, `asm/schid.h` for `struct subchannel_id`, and Linux bitmap/vmalloc helpers. It is a local utility for channel-subsystem evaluation.

Risks and test signals: callers must not pass out-of-range SSIDs or subchannel numbers. `idset_add_set()` only ORs the minimum shared bit length, so differently sized sets truncate to the smaller dimension. Tests should cover allocation sizing, fill/empty, add/delete/contains across multiple SSIDs, subsequence clearing, and OR of mismatched dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/idset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/idset.h -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/idset.h

Purpose: declares the opaque subchannel-ID set API implemented by `idset.c`.

Important APIs/types/functions: forward-declares `struct idset` and exposes creation, destruction, fill, subchannel add/delete/delete-subsequent/contains, empty check, and set-union functions.

Control flow: no direct control flow; callers allocate with `idset_sch_new()`, mutate/check, then free.

State and persistence behavior: hides bitmap storage details from users, keeping state opaque and in memory.

Dependencies and integration points: includes `asm/schid.h` for subchannel IDs and is consumed by CSS/CIO code that tracks scan/evaluation sets.

Risks and test signals: API lacks explicit bounds or locking in the header contract, so caller misuse can corrupt bitmap state. Compile coverage should ensure all users include the header rather than depending on implementation details.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/idset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/io_sch.h -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/io_sch.h

Purpose: defines private data structures for I/O subchannels, internal CCW requests, sense-id buffers, and CCW-device private state.

Important APIs/types/functions: `struct io_subchannel_private` stores the active ORB, child CCW device pointer, channel-program options, and subchannel DMA area. `struct ccw_request` is the reusable internal request descriptor with timeout/retry/path/check/filter/callback fields. `struct senseid`, `struct ccw_device_dma_area`, and `struct ccw_device_private` define the shared memory/state layout used by device FSM, ID, PGID, status, QDIO, CMF, and todo code. Inline helpers get/set subchannel private data and child device.

Control flow: no executable flow beyond inline accessors, but the structures determine how internal requests are started and completed, how SENSE ID/PGID/IRB data is shared, and how state flags drive the FSM.

State and persistence behavior: all state is in memory and either tied to subchannel device data or a CCW device. DMA areas hold architecture-visible channel-program data below the required addressing limits.

Dependencies and integration points: includes CSS, ORB, CCW device UAPI, IRQ class definitions, and is a central private contract for `device_fsm.c`, `device_id.c`, `device_pgid.c`, `device_status.c`, `device_ops.c`, QDIO, and I/O subchannel code.

Risks and test signals: bitfield packing, DMA alignment, and flag semantics are ABI-sensitive within the driver. Tests should indirectly validate every state flag transition, internal request cancellation/retry, fake IRB delivery, QDIO data ownership, DMA pool lifetime, and subchannel private-data lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/io_sch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/ioasm.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/ioasm.c

Purpose: wraps s390 channel-subsystem machine instructions in C helpers with condition-code normalization, tracepoint emission, and limited exception handling.

Important APIs/types/functions: exported or local wrappers include `stsch()`, `msch()`, `tsch()`, `ssch()`, `csch()`, `tpi()`, `chsc()`, `rsch()`, `hsch()`, `xsch()`, and `stcrw()`. Internal `__*` helpers issue inline assembly and return transformed condition codes; STSCH/MSCH/SSCH/CHSC use exception-table recovery for operand exceptions.

Control flow: each public wrapper calls the assembly helper, emits the matching `trace_s390_cio_*` tracepoint, and returns the condition code or `-EIO` on trapped exception for helpers that can trap. `stcrw()` optionally consumes injected CRWs when `CONFIG_CIO_INJECT` is enabled before falling back to the hardware instruction.

State and persistence behavior: functions do not own persistent state. They read or write caller-provided architecture blocks such as SCHIB, IRB, ORB, CHSC area, TPI info, and CRW.

Dependencies and integration points: used by nearly all CIO/CSS layers. Depends on s390 inline assembly constraints, `asm-extable`, trace definitions, `cio_inject`, `orb.h`, and architecture status structures.

Risks and test signals: register clobber lists and condition-code transformation are architecture-critical. `__ssch()` initializes an exception variable but ignores it, returning the condition code path even on exception, which deserves scrutiny against architectural guarantees. Tests require s390 build/boot coverage, tracepoint validation, CHSC exception handling, CRW injection, and instruction return-code mapping for not-operational/status-pending/busy cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/ioasm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/ioasm.h -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/ioasm.h

Purpose: declares low-level CIO instruction wrapper functions and pulls in tracepoint definitions for users.

Important APIs/types/functions: declares wrappers for STSCH, MSCH, TSCH, SSCH, CSCH, TPI, CHSC, RSCH, HSCH, XSCH, and STCRW against s390 subchannel, ORB, IRB, TPI, CHSC, and CRW structures.

Control flow: no runtime flow; the header establishes the callable interface implemented by `ioasm.c`.

State and persistence behavior: no state. All state belongs to caller-supplied instruction blocks and hardware.

Dependencies and integration points: included by CIO device, CSS, EADM, QDIO, trace, and machine-check code needing raw channel-subsystem instructions.

Risks and test signals: prototypes must stay synchronized with `ioasm.c` and architecture headers. Compile coverage across all users is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/ioasm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/isc.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/isc.c

Purpose: reference-counts s390 I/O interruption subclass enablement.

Important APIs/types/functions: exports `isc_register()` and `isc_unregister()`. Global `isc_refs[MAX_ISC + 1]` and `isc_ref_lock` protect per-ISC user counts. First registration sets control register bit 6, `31 - isc`; last unregister clears it.

Control flow: register validates range, increments under spinlock, and enables the mask only for the first user. Unregister validates range and nonzero count, disables the mask for the last user, and decrements.

State and persistence behavior: state is in-memory reference counts and system control-register mask bits. Hardware mask state follows runtime registrations and is not persisted.

Dependencies and integration points: used by EADM, QDIO adapter interrupts, and other s390 I/O facilities. Depends on `asm/isc.h`, `system_ctl_set_bit()`, and `system_ctl_clear_bit()`.

Risks and test signals: unregister misuse warns and leaves state unchanged. Tests should cover multiple users of one ISC, first/last transitions, invalid ISC warnings, and absence of interrupt-context callers per the API contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/isc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/itcw.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/itcw.c

Purpose: provides an incremental builder for FCX transport command words and associated TCCB, TSB, TIDAW, and optional interrogate structures inside one caller-provided buffer.

Important APIs/types/functions: `struct itcw` tracks the main TCW, optional interrogate TCW, TIDAW counts, and capacities. Exports `itcw_get_tcw()`, `itcw_calc_size()`, `itcw_init()`, `itcw_add_dcw()`, `itcw_add_tidaw()`, `itcw_set_data()`, and `itcw_finalize()`. Internal `fit_chunk()` handles alignment and optional 4K crossing avoidance.

Control flow: callers calculate required size, allocate low-address DMA-capable storage, initialize with read/write operation and optional interrogate support, add DCWs and TIDAWs, optionally override data pointer, and finalize. Initialization lays out ITCW metadata, aligned TCWs, optional interrogate TCW, TIDAW lists, TSBs, and TCCBs. `itcw_add_tidaw()` inserts TTIC TIDAWs when the next TIDAW would land on a new page.

State and persistence behavior: all state is in the supplied buffer and is zeroed by `itcw_init()`. No internal allocation or persistence occurs.

Dependencies and integration points: builds on exported FCX helpers from `fcx.c`, `asm/fcx.h`, `asm/itcw.h`, and s390 DMA/physical address constraints. Used by transport-mode I/O consumers that need safe control-block layout.

Risks and test signals: the 2GB physical limit, 4K boundary handling, TTIC insertion, and capacity accounting are the key risks. Tests should cover undersized buffers, read/write modes, interrogate TCW generation, page-boundary TIDAW insertion, `-ENOSPC`, final count fields, and invalid high physical addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/itcw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/orb.h -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/orb.h

Purpose: defines packed operation-request-block layouts for command-mode, transport-mode, and EADM subchannel starts.

Important APIs/types/functions: `struct cmd_orb`, `struct tm_orb`, `struct eadm_orb`, and `union orb` model the architecture fields passed to SSCH, including interrupt parameter, storage key, path mask, mode flags, CCW/TCW/AOB address, priority, compatibility bits, and format fields.

Control flow: no executable flow; instances are filled by CIO, CCW, QDIO, FCX, and EADM code and passed to `ssch()`.

State and persistence behavior: ORBs are transient in-memory hardware command blocks, aligned and packed for architecture consumption.

Dependencies and integration points: used by `io_sch.h`, `ioasm.c`, `eadm_sch.c`, low-level CIO start helpers, and any code starting command or transport I/O.

Risks and test signals: bitfield layout, packing, alignment, and DMA address width are ABI-critical. Tests are architecture compile/runtime coverage of command-mode start, transport-mode start, EADM start, and tracepoint copying of ORB data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/orb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/qdio.h -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/qdio.h

Purpose: defines QDIO internal state, buffer-state constants, low-level EQBS/SQBS helpers, queue/IRQ structures, and shared helper macros.

Important APIs/types/functions: `enum qdio_irq_states`, SLSB state constants, SIGA/QEBSM flags, inline `do_sqbs()` and `do_eqbs()`, `struct qdio_q`, `struct qdio_irq`, performance-stat structures, queue iterators, buffer-number helpers, and prototypes for setup, thin interrupts, debug buffer state, and `qdio_int_handler()`.

Control flow: inline assembly EQBS/SQBS manipulates storage-list state for QEBSM queues. Helper macros decide thin-interrupt eligibility, required SIGA operations, queue iteration, and interrupt delivery. `qdio_deliver_irq()` disables further delivery atomically and invokes the upper `irq_poll` callback or records discarded interrupts.

State and persistence behavior: `struct qdio_irq` owns the lifecycle state, QIB/QDR pointers, queues, CHSC page, original CCW handler, DSCI pointer, debugfs entry, poll bit, and performance counters. `struct qdio_q` owns SLSB, SBAL pointers, queue position, usage counter, and batch tracking. Runtime-only, no persistent storage.

Dependencies and integration points: central private contract for `qdio_main.c`, `qdio_setup.c`, `qdio_debug.c`, and `qdio_thinint.c`; depends on `asm/qdio.h`, CHSC descriptors, CCW devices, debug feature, CSS characteristics, and adapter interrupt support.

Risks and test signals: cache alignment, atomic buffer accounting, SLSB state values, and EQBS/SQBS inline assembly are correctness-critical. Tests should cover QEBSM and non-QEBSM paths, input/output queue state transitions, thin interrupt delivery, polling disable/enable, queue iteration bounds, and perf-stat toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/qdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_debug.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_debug.c

Purpose: provides QDIO debug feature areas and debugfs views for per-device queue state, SSQD descriptors, and performance statistics.

Important APIs/types/functions: initializes global debug areas through `qdio_debug_init()` and frees them through `qdio_debug_exit()`. Per-device debug areas are managed by `qdio_allocate_dbf()` and a reuse list. Debugfs setup/removal uses `qdio_setup_debug_entries()` and `qdio_shutdown_debug_entries()`. Show/write functions include `qstat_show()`, `ssqd_show()`, `qperf_show()`, and `qperf_seq_write()`.

Control flow: module init creates `/sys/kernel/debug/qdio` and debug feature buffers. Per-device setup creates a directory, statistics file, SSQD file, and one file per input/output queue. Queue state reads call `debug_get_buf_state()` for each SBAL and print symbolic states. Statistics writes of 0 clear counters and disable perf accounting; writes of 1 enable it.

State and persistence behavior: debug state is in debug feature buffers, debugfs dentries, a list of per-device debug areas, and optional performance counters in `struct qdio_irq`/`struct qdio_q`. It is volatile and removed on shutdown/exit.

Dependencies and integration points: depends on debugfs, seq_file, s390 debug feature, QDIO internal structures, SSQD query API, and queue buffer-state helpers.

Risks and test signals: debug-area reuse by device name must not leak stale pointers; debugfs reads race with teardown unless lifecycle ordering is correct. Tests should cover repeated allocate/free for the same device, statistics enable/disable, queue state formatting for all SLSB states, SSQD errors, and module exit with live/removed devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_debug.h -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_debug.h

Purpose: declares QDIO debug feature globals, logging macros, and debugfs lifecycle hooks.

Important APIs/types/functions: exposes `qdio_dbf_setup`, `qdio_dbf_error`, log levels `DBF_ERR/DBF_WARN/DBF_INFO`, macros `DBF_EVENT`, `DBF_ERROR`, `DBF_DEV_EVENT`, hex helpers, and prototypes for per-device/global debug lifecycle functions.

Control flow: macro calls format bounded 32-byte text events and send them to global or per-device debug feature areas when the requested level is enabled.

State and persistence behavior: the header owns no state except external declarations. Debug output is runtime-only.

Dependencies and integration points: included by QDIO setup, main, thin interrupt, and debug implementation files. Depends on `asm/debug.h`, `asm/qdio.h`, and `qdio.h`.

Risks and test signals: macros evaluate device debug pointers and should only be used after debug areas are initialized. Compile coverage and boot-time QDIO debug initialization are primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_main.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_main.c

Purpose: implements QDIO runtime queue processing, SIGA/EQBS/SQBS operations, interrupt handling, exported queue API, and module lifecycle.

Important APIs/types/functions: exported APIs include `qdio_get_ssqd_desc()`, `qdio_shutdown()`, `qdio_free()`, `qdio_allocate()`, `qdio_establish()`, `qdio_activate()`, `qdio_inspect_input_queue()`, `qdio_inspect_output_queue()`, `qdio_add_bufs_to_input_queue()`, `qdio_add_bufs_to_output_queue()`, `qdio_start_irq()`, and `qdio_stop_irq()`. Internal core helpers handle SIGA read/write/sync, EQBS/SQBS state extraction, inbound/outbound frontier discovery, activation errors, cleanup cancellation, and PCI/thin interrupt delivery.

Control flow: consumers allocate QDIO storage, establish queues with CIW EQUEUE, optionally enable thin interrupts, wait for establish IRQ, query SSQD/QEBSM capability, initialize SLSB states, activate with CIW AQUEUE, then add/inspect buffers. Inbound processing returns CU-empty buffers, signals input if needed, inspects primed/error buffers, acknowledges batches, and lets polling restart IRQs safely. Outbound processing marks buffers CU-primed, handles IQDIO SIGA-W/WRITEM/WRITEQ, syncs or fast-requeues for non-IQDIO, and inspects completion/error/pending states.

State and persistence behavior: lifecycle state is `qdio_irq->state` from inactive through established/active/stopped/cleanup/error. Queue state is SLSB ownership/state bytes or QEBSM-managed state, `first_to_check`, `nr_buf_used`, input batch windows, poll-disabled bit, timers via CCW wait queues, and perf counters. All state is runtime memory and hardware queue state.

Dependencies and integration points: depends on CCW start/halt/clear APIs, CIWs from SENSE ID, QDIO setup/debug/thinint helpers, CHSC SSQD/SADC, adapter interrupts, IPL LGR logging, and upper-layer qdio handlers such as qeth/zfcp.

Risks and test signals: QDIO is concurrency-sensitive around poll-state transitions, adapter interrupts, buffer ownership, busy-bit retry loops, and shutdown while I/O is active. Tests should cover allocate/establish/activate/shutdown/free, missing CIWs, setup validation failures, establish timeout/error/retry, QEBSM and non-QEBSM buffer states, IQDIO AOB alignment, SIGA busy and ENOBUFS paths, pending/error SLSB states, and no-lost-interrupt `qdio_start_irq()` rescans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_setup.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_setup.c

Purpose: allocates QDIO queue storage and initializes QIB, QDR, storage-list, SSQD, debug, and CCW handler setup state.

Important APIs/types/functions: exported buffer helpers are `qdio_alloc_buffers()`, `qdio_free_buffers()`, and `qdio_reset_buffers()`. Internal lifecycle functions include `qdio_allocate_qs()`, `qdio_free_queues()`, `qdio_setup_get_ssqd()`, `qdio_setup_ssqd_info()`, `qdio_setup_irq()`, `qdio_shutdown_irq()`, `qdio_print_subchannel_info()`, `qdio_setup_init()`, and `qdio_setup_exit()`.

Control flow: buffer allocation gets pages and maps array entries to per-page `struct qdio_buffer` slots. Queue allocation uses a 256-byte-aligned slab cache and one page per queue for SLIB/SL. Setup fills SBAL pointers, SLIB links, storage-list elements, QIB fields, QDR descriptors, SSQD capability information, and installs `qdio_int_handler()` as the CCW device handler. Shutdown restores the original handler and intparm.

State and persistence behavior: state is in allocated queue pages, QDIO IRQ structure, QIB/QDR fields, SSQD descriptor, CHSC page, and CCW handler pointer. It is freed by `qdio_free()` and has no persistence.

Dependencies and integration points: depends on slab/page allocation, EBCDIC conversion for QIB name, CHSC SSQD, CSS characteristics for QEBSM, CCW device SCHID queries, and QDIO debug/perf state.

Risks and test signals: allocation cleanup must unwind partially allocated queues and pages correctly. QIB/QDR address fields must respect DMA/addressing constraints. Tests should cover buffer counts across page boundaries, input/output queue allocation failure unwind, SSQD invalid capability flags, QEBSM enable/disable decisions, handler install/restore, and printed capability flags for AI/QEBSM/PRI/TDD/SIGA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_thinint.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_thinint.c

Purpose: implements QDIO adapter thin interrupt registration, device-state-change indicators, and delivery to QDIO polling callbacks.

Important APIs/types/functions: `qdio_thinint_init()` allocates indicators and registers `tiqdio_airq`; `qdio_thinint_exit()` unregisters it. `qdio_establish_thinint()` assigns a DSCI, programs subchannel indicators, and adds the IRQ to `tiq_list`; `qdio_shutdown_thinint()` removes and resets it. `test_nonshared_ind()` helps the IRQ restart path avoid missed interrupts.

Control flow: up to 63 subchannels get non-shared indicators, while later users share one indicator. The adapter interrupt handler clears the shared indicator once, walks the RCU list, checks each DSCI, clears non-shared indicators with `xchg()`, calls `qdio_deliver_irq()`, records interrupt time, and updates stats. CHSC SADC programs or clears summary/subchannel indicator addresses.

State and persistence behavior: state is in `q_indicators` counts and indicator words, the RCU `tiq_list`, global `last_ai_time`, and per-IRQ `dsci` pointer/list entry. Hardware indicator registration is runtime-only and reset on shutdown.

Dependencies and integration points: depends on adapter interrupt infrastructure, ISC `QDIO_AIRQ_ISC`, CHSC SADC, RCU list semantics, QDIO IRQ structures, and CSS AI capability decisions.

Risks and test signals: shared indicator fan-out can cause extra scans, while non-shared indicators must be cleared atomically to avoid lost work. Tests should cover non-thin fallback, first 63 versus shared indicators, establish SADC failure cleanup, shutdown RCU synchronization, adapter interrupt delivery/discard when polling is disabled, and `qdio_start_irq()` rescan behavior with a set non-shared indicator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_thinint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/scm.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/scm.c

Purpose: discovers, represents, updates, and dispatches events for s390 storage class memory devices.

Important APIs/types/functions: exports `scm_driver_register()`, `scm_driver_unregister()`, and `scm_irq_handler()`. Defines the `scm` bus type, sysfs attributes for SCM metadata, `scm_update_information()`, `scm_process_availability_information()`, and helpers for setup/update/find/add.

Control flow: subsystem init registers the SCM bus and root device, then queries CHSC SCM information. `scm_update_information()` pages through CHSC SALE entries using a resume token, updating existing devices by storage address or registering new `struct scm_device`s. Attribute reads lock the device and expose current fields. EADM AOB completion calls `scm_irq_handler()`, which unwraps the request header and calls the bound SCM driver completion handler.

State and persistence behavior: devices persist in the Linux device model until removal/reboot. `struct scm_device` stores address, size, max block count, and attributes from SALE entries. Updates modify rank/oper_state and issue driver notify plus userspace `KOBJ_CHANGE` when changed.

Dependencies and integration points: depends on CHSC SCM info, EADM AOB request layout, Linux bus/device/driver model, sysfs, and SCM block/storage drivers that bind to the `scm` bus.

Risks and test signals: CHSC length arithmetic and paged resume-token iteration must match firmware. Update only treats rank and operational state as change signals. Tests should cover empty/multiple CHSC pages, duplicate address update, new device registration failure cleanup, sysfs reads under lock, SCM_AVAIL notifications, SCM_CHANGE notifications, and AOB completion error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/scm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/trace.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/trace.c

Purpose: instantiates and exports s390 CIO tracepoints declared in `trace.h`.

Important APIs/types/functions: defines `CREATE_TRACE_POINTS`, includes `trace.h`, and exports tracepoint symbols for STSCH, MSCH, TSCH, TPI, SSCH, CSCH, HSCH, XSCH, RSCH, and CHSC.

Control flow: no runtime control flow beyond tracepoint instantiation. The wrappers in `ioasm.c` invoke the tracepoints after low-level instructions.

State and persistence behavior: tracepoint state is managed by the kernel tracing subsystem; this file owns no runtime data.

Dependencies and integration points: depends on `asm/crw.h`, `cio.h`, and `trace.h`. Consumers are ftrace/perf/BPF and in-kernel modules that need exported CIO tracepoint symbols.

Risks and test signals: exported symbol list must match declared and used tracepoints. Test with s390 build, enabled trace events for CIO instructions, and module users resolving exported tracepoint symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/trace.h -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/trace.h

Purpose: declares trace events for s390 CIO instructions, I/O interrupts, adapter interrupts, CHSC calls, and channel report words.

Important APIs/types/functions: event classes include `s390_class_schib` for STSCH/MSCH and `s390_class_schid` for CSCH/HSCH/XSCH/RSCH. Individual events include `s390_cio_tsch`, `s390_cio_tpi`, `s390_cio_ssch`, `s390_cio_chsc`, `s390_cio_interrupt`, `s390_cio_adapter_int`, and `s390_cio_stcrw`. Events copy SCHIB, IRB, ORB, TPI, CHSC request/response, and CRW fields into trace entries.

Control flow: trace macros define payload assignment and printk formatting for instruction wrappers and interrupt code. CHSC tracing copies bounded request and response payloads from the CHSC block.

State and persistence behavior: no driver-owned state. Trace buffers are managed by the kernel tracing subsystem and reflect runtime events only.

Dependencies and integration points: included by `trace.c` and `ioasm.h`; depends on Linux tracepoint infrastructure, s390 UAPI IDs, CIO structures, ORB layouts, and SCSW helper accessors.

Risks and test signals: trace payload copying must avoid overread when CHSC length fields are malformed; the code uses bounded `min_t()` lengths but trusts the response header position. Tests should enable each event, verify formatted fields for representative instruction calls, check trace compile with `TRACE_HEADER_MULTI_READ`, and validate CHSC request/response output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_async.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_async.c

Purpose: registers the vfio-ccw asynchronous command region used by userspace to issue async requests to the vfio-ccw FSM.

Important APIs/types/functions: `vfio_ccw_register_async_dev_regions()` registers subtype `VFIO_REGION_SUBTYPE_CCW_ASYNC_CMD` with read/write flags and `vfio_ccw_async_region_ops`. Region callbacks read/write a `struct ccw_cmd_region` and trigger `VFIO_CCW_EVENT_ASYNC_REQ`.

Control flow: reads validate offset/count, lock `io_mutex`, copy the region to userspace, and unlock. Writes validate bounds, use `mutex_trylock()` to avoid blocking concurrent I/O, copy data from userspace, dispatch the async FSM event, and return either `region->ret_code` or the byte count.

State and persistence behavior: state is the registered region data, usually `private->cmd_region`, and the vfio-ccw private FSM state. It is runtime-only.

Dependencies and integration points: depends on vfio region registration, vfio-ccw private region tables, user copy helpers, and `vfio_ccw_fsm_event()`.

Risks and test signals: partial writes can trigger async requests with partially updated command regions if userspace writes slices intentionally. `mutex_trylock()` returns `-EAGAIN`, so userspace must retry. Tests should cover out-of-bounds access, EFAULT copy paths, concurrent write rejection, FSM event side effects, ret_code propagation, and readback consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_async.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_chp.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_chp.c

Purpose: exposes vfio-ccw channel-path related status regions for SCHIB state and queued channel report words.

Important APIs/types/functions: `vfio_ccw_register_schib_dev_regions()` registers read-only subtype `VFIO_REGION_SUBTYPE_CCW_SCHIB`; `vfio_ccw_register_crw_dev_regions()` registers read-only subtype `VFIO_REGION_SUBTYPE_CCW_CRW`. Region ops include SCHIB read and CRW read; writes always return `-EINVAL`.

Control flow: SCHIB reads validate bounds, lock `io_mutex`, refresh the subchannel with `cio_update_schib()`, copy SCHIB into the region, and copy to userspace. CRW reads pop the first queued `struct vfio_ccw_crw` if present, lock `io_mutex`, copy its value into the region, copy to userspace, clear the region field, free the popped CRW, and signal the eventfd again if more CRWs remain.

State and persistence behavior: SCHIB state is live hardware/subchannel state copied on demand. CRW state is an in-memory queue `private->crw` plus optional trigger eventfd; each read consumes one queued CRW.

Dependencies and integration points: depends on vfio-ccw private data, CIO `cio_update_schib()`, subchannel parent linkage, Linux list handling, eventfd signaling, and vfio region registration.

Risks and test signals: CRW list manipulation happens before `io_mutex`, so the queue needs external serialization from vfio-ccw core. SCHIB read can fail with `-ENODEV` if the subchannel is gone. Tests should cover partial reads, out-of-bounds reads, SCHIB refresh failure, CRW empty read clearing zero, queued CRW consumption order, eventfd retrigger with remaining entries, and write rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_chp.c -->
