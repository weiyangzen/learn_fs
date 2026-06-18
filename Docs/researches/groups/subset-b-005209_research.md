# subset-b-005209 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_vt220.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/sclp_vt220.c

Purpose: implements the s390 SCLP VT220 TTY and optional console backend, exposing `ttysclp0` and routing terminal input/output through SCLP VT220 event buffers.

Important APIs/types/functions: defines `struct sclp_vt220_request` and `struct sclp_vt220_sccb`; registers output/input `struct sclp_register` entries; implements tty operations `sclp_vt220_open`, `close`, `write`, `put_char`, `flush_chars`, `write_room`, `chars_in_buffer`, and `flush_buffer`; console support uses `sclp_vt220_con_write`, `sclp_vt220_notify`, and `sclp_vt220_con_device`.

Control flow: output pages sit on `sclp_vt220_empty`, become `sclp_vt220_current_request` while filling, move to `sclp_vt220_outqueue`, and are submitted with `sclp_add_request`. Completion callback inspects SCCB response codes, retries recoverable SCLP equipment checks once, returns the page to the empty queue, and starts the next queued request. Input SCLP event buffers distinguish session start/end/data, pass data to the tty flip buffer, and optionally interpret Ctrl-O as Magic SysRq.

State and persistence: all runtime state is in static queues, a tty port, a timer, and page-backed SCCBs guarded by `sclp_vt220_lock`; nothing is persisted. Console init and tty init share the SCLP registration/page pool through `sclp_vt220_init_count`.

Dependencies and integration: depends on `sclp.h`, `ctrlchar.h`, Linux tty/console APIs, panic/reboot notifiers, SCLP core request queues, `sclp_sync_wait`, and global console buffering knobs such as `sclp_console_pages`, `sclp_console_drop`, and `sclp_console_full`.

Risks: output paths may block in sync wait when buffers are exhausted unless `may_fail` is set; panic/reboot flushing deliberately avoids taking an already-held spinlock; buffer-drop behavior can lose console output when configured; malformed or unexpected SCLP response codes are mostly treated as completion after limited retry.

Test signals: boot with `console=ttysclp0`, interactive tty open/write/read, Magic SysRq over SCLP, panic/reboot flush tests, SCLP equipment-check retry tests, and stress of full output buffers with and without console dropping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_vt220.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/tape.h -->
# sources/distributed-fs/ceph-client/drivers/s390/char/tape.h

Purpose: central private header for the s390 channel-attached tape driver, defining shared device/request state, discipline hooks, operation enums, debug helpers, and CCW construction helpers.

Important APIs/types/functions: declares `enum tape_medium_state`, `enum tape_state`, `enum tape_op`, `enum tape_request_status`, `struct tape_request`, `struct tape_discipline`, `struct tape_char_data`, and `struct tape_device`. Exposes core APIs such as `tape_alloc_request`, `tape_do_io*`, `tape_cancel_io`, `tape_open`, `tape_release`, `tape_mtop`, `tape_generic_probe/online/offline/remove`, and frontend/discipline init functions. Inline helpers include `tape_ccw_cc`, `tape_ccw_end`, `tape_ccw_repeat`, and IDAL variants.

Control flow: this header describes the layering: frontends allocate `tape_request`s, disciplines build CCW chains and interpret interrupts, and `tape_core.c` queues and dispatches those requests through the common I/O layer.

State and persistence: `struct tape_device` holds list membership, ccw device binding, class devices for rewinding/non-rewinding minors, mutexes/wait queues, medium/tape state, request queue, refcount, block size/IDAL buffers, delayed work, and long-busy timer. State is in-memory and tied to ccw device lifetime.

Dependencies and integration: includes s390 `ccwdev`, `debug`, `idals`, Linux `mtio`, workqueue, interrupt, and module interfaces. It is consumed by the tape core, char frontend, 3490 discipline, proc reporting, and standard command builder.

Risks: the public macros assume `TAPE_DBF_AREA` is defined by each translation unit; CCW helpers rely on DMA-addressable buffers; state transitions and request status are shared across interrupt, workqueue, and process contexts and must be lock-disciplined by users.

Test signals: compile coverage across all tape objects, request lifecycle tests, MTIO command mapping tests, IDAL block-size tests, and debug/proc/sysfs state reporting consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/tape.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/tape_3490.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/tape_3490.c

Purpose: implements the IBM 3490/34xx tape discipline, including ccw_driver registration, medium sensing, device setup/cleanup, MTIO command table entries specific to 3490, and sense-data error recovery.

Important APIs/types/functions: defines `struct tape_3490_block_id`, `tape_3490_medium_sense`, `tape_3490_medium_sense_async`, `tape_3490_irq`, `tape_3490_unit_check`, `tape_3490_setup_device`, `tape_3490_cleanup_device`, `tape_3490_mttell`, `tape_3490_mtseek`, `tape_3490_init`, and `tape_3490_exit`. The exported discipline is `tape_discipline_3490`; the ccw driver is named `tape_34xx`.

Control flow: probe is delegated to generic tape probe; online calls `tape_generic_online` with the 3490 discipline. Setup assigns the tape through `tape_std_assign` and then senses medium state. Normal interrupts call `tape_3490_irq`, which handles unsolicited ready interrupts by scheduling asynchronous medium sense, maps unit exceptions and unit checks, and returns core request outcomes such as success, retry, stop, or long error codes.

State and persistence: per-device state lives in `struct tape_device`; this file updates medium state and generic status bits for loaded/unloaded/write-protected/online conditions. Delayed medium-sense work holds a tape-device reference until the queued work completes.

Dependencies and integration: depends on `tape_core.c` queueing, `tape_std.c` standard CCW builders, the ccw bus, and s390 debug feature. It exports its debug area and registers a ccw device id for 3490 device/control-unit pairs.

Risks: error recovery contains many device-specific sense and ERPA code interpretations; incorrect mappings can surface as false ENOSPC/EIO/EACCES or missed retries. Async medium-sense is required because the interrupt path cannot synchronously issue tape I/O. Assignment has to handle devices already assigned elsewhere.

Test signals: 3490 online/offline cycles, insertion/removal unsolicited interrupts, read/write/write-protect/end-of-volume paths, MTSEEK/MTTELL block id behavior, and injected sense-byte/ERPA cases for retry and failure decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/tape_3490.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/tape_char.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/tape_char.c

Purpose: character-device frontend for the tape subsystem, exposing rewinding and non-rewinding tape minors and implementing read, write, open, release, and MTIO ioctls.

Important APIs/types/functions: defines `tape_fops`, `tapechar_setup_device`, `tapechar_cleanup_device`, `tapechar_read`, `tapechar_write`, `tapechar_open`, `tapechar_release`, `__tapechar_ioctl`, `tapechar_ioctl`, `tapechar_init`, and `tapechar_exit`.

Control flow: setup registers `ntibmN` and `rtibmN` class devices for the assigned minor pair. Open resolves minor to `tape_device`, calls `tape_open`, and stores the device in `private_data`. Reads terminate pending writes first, choose fixed or variable block size, allocate/check IDAL buffers, let the discipline build a read request, execute it, and copy IDAL data to userspace. Writes split input into fixed-size blocks when configured, copy userspace data into IDAL buffers, reuse the discipline write request, and update required tape marks. Release rewinds rewinding minors and writes required tape marks before dropping buffers and references.

State and persistence: tracks per-device `char_data.block_size`, IDAL buffer arrays, and `required_tapemarks`; file private data holds the active device reference. No persistent storage is created.

Dependencies and integration: depends on tape core request APIs, `tape_std_terminate_write`, `tape_mtop`, `register_tape_dev`, Linux mtio helpers such as `put_user_mtget`/`put_user_mtpos`, and IDAL user-copy helpers.

Risks: required tapemarks must be flushed before reads, seeks, and close to maintain tape format; partial writes at ENOSPC require discipline EOV processing; reads infer transferred bytes from CPA/residual count; block-size and userspace buffer constraints return EINVAL/EFAULT.

Test signals: open exclusivity via core state, fixed and variable block reads/writes, rewinding vs non-rewinding close behavior, MTIOCTOP/MTIOCGET/MTIOCPOS ioctls, ENOSPC partial-write handling, and IDAL allocation boundary at `MAX_BLOCKSIZE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/tape_char.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/tape_class.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/tape_class.c

Purpose: small class-device helper for s390 tape character devices under class `tape390`.

Important APIs/types/functions: exports `register_tape_dev`, `unregister_tape_dev`, `tape_class_init`, and `tape_class_exit`; uses `struct tape_class_device` from `tape_class.h`.

Control flow: registration sanitizes device and mode names, allocates a cdev, attaches file operations, adds the cdev, creates the class device, and creates a sysfs link from the physical ccw device to the logical mode. Unregister reverses link, class device, cdev, and allocation.

State and persistence: maintains per-registered tape logical device state in `struct tape_class_device`; sysfs class device and links exist only while the tape device is online.

Dependencies and integration: used by `tape_char.c` for rewinding and non-rewinding minors; depends on Linux cdev, class, device_create, and sysfs link APIs.

Risks: error unwind must not leak cdevs or class devices; names containing `/` are rewritten to `!` to keep sysfs paths valid; callers must tolerate `ERR_PTR` results.

Test signals: online/offline tape device registration, sysfs link existence/removal, cdev open path through both modes, and failure injection in cdev_add/device_create/sysfs_create_link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/tape_class.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/tape_class.h -->
# sources/distributed-fs/ceph-client/drivers/s390/char/tape_class.h

Purpose: declares the tape class-device abstraction used by the character frontend to create logical tape devices.

Important APIs/types/functions: defines `TAPECLASS_NAME_LEN`, `struct tape_class_device`, and prototypes for `register_tape_dev`, `unregister_tape_dev`, `tape_class_init`, and `tape_class_exit`.

Control flow: callers pass the physical `struct device`, target dev_t, file operations, logical device name, and mode/link name; implementation registers a cdev and class device and returns a handle for cleanup.

State and persistence: the structure stores cdev pointer, class device pointer, and fixed-size copied names. State is runtime-only and owned by online tape devices.

Dependencies and integration: included by tape core/char frontend; depends on Linux fs, cdev, device, kdev_t, module/init headers.

Risks: fixed name buffers require bounded copies; caller must not pass stack-owned data expecting later reference because names are copied; cleanup must receive the same physical parent used to create sysfs links.

Test signals: compile compatibility with `tape_class.c`, class init/exit order during tape module load/unload, and cleanup of both rewinding and non-rewinding device handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/tape_class.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/tape_core.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/tape_core.c

Purpose: core s390 tape driver, owning ccw device probe/remove, online/offline transitions, tape device lifetime, request allocation, request queueing, interrupt dispatch, state/medium events, and module init/exit.

Important APIs/types/functions: exports `tape_generic_probe`, `tape_generic_remove`, `tape_generic_online`, `tape_generic_offline`, `tape_alloc_request`, `tape_free_request`, `tape_do_io`, `tape_do_io_async`, `tape_do_io_interruptible`, `tape_cancel_io`, `tape_open`, `tape_release`, `tape_mtop`, `tape_state_set`, `tape_med_state_set`, and `tape_dump_sense_dbf`.

Control flow: probe allocates `struct tape_device`, creates sysfs attributes, stores drvdata, and installs `__tape_do_irq`. Online installs a discipline, calls its setup, assigns minors, creates char devices, and moves to `TS_UNUSED`. Requests are added under the ccw device lock; the first request starts via `ccw_device_start`, later requests queue. Interrupts copy status into the request, update generic online status, call discipline `irq`, and then end, retry, cancel, or mark long-busy. Completion invokes callbacks, wakes waiters, drops queued refs, and starts the next request.

State and persistence: maintains global sorted `tape_device_list` under `tape_device_lock`, per-device request queues, state wait queues, delayed work for next request, long-busy timer, medium-state work and uevents, refcounts, mode byte, minor allocation, and debug areas. Runtime-only; sysfs attributes expose current state.

Dependencies and integration: integrates with ccw_device APIs, s390 debug feature, sysfs attributes, tape class/char/proc/3490 modules, Linux workqueues/timers/wait queues, and mtio status bits.

Risks: concurrency spans process, interrupt, timer, and workqueue contexts; request refcount drops must match queue insertion/removal; `TS_NOT_OPER` prevents state resurrection; interrupt handling of error-pointer IRBs and unsolicited long-busy ready events is fragile; module init does not unwind partial frontend/discipline registration failures in this source.

Test signals: ccw probe/remove while idle and in-use, online/offline busy rejection, sync/async/interruptible I/O completion and cancellation, long-busy timeout/ready interrupt handling, request queue ordering, sysfs state/operation/blocksize attributes, and module load/unload ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/tape_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/tape_proc.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/tape_proc.c

Purpose: optional procfs reporting for tape devices through `/proc/tapedevices`.

Important APIs/types/functions: defines `tape_proc_show`, seq iteration callbacks, `tape_proc_seq`, `tape_proc_init`, and `tape_proc_cleanup`.

Control flow: the seq iterator walks possible tape device indexes up to `256 / TAPE_MINORS_PER_DEV`; each row uses `tape_find_device`, locks the ccw device, prints bus id, CU/device type/model, block size, tape state, current queued operation, and medium state, then drops the device reference.

State and persistence: keeps only the proc entry pointer. Output reflects live tape state and no data is persisted.

Dependencies and integration: compiled under `CONFIG_PROC_FS`; depends on tape core device lookup, state/op verbose tables, ccw device fields, and seq_file/proc APIs.

Risks: proc output is best-effort and skips missing indexes; it must hold the ccw lock while peeking at request queue state; medium-state enum indexing assumes valid values from core/discipline.

Test signals: presence/removal of `/proc/tapedevices`, output with no devices, output with one or more online tapes, state/op changes during active I/O, and cleanup during module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/tape_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/tape_std.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/tape_std.c

Purpose: implements common IBM tape CCW command builders and MTIO operation handlers shared by tape disciplines.

Important APIs/types/functions: exports `tape_std_assign`, `tape_std_unassign`, `tape_std_read_block_id`, `tape_std_terminate_write`, MT operations for load, set block, reset, forward/backward spacing, write EOF, rewind/offline/unload, EOM, retension, erase, compression, `tape_std_read_block`, `tape_std_write_block`, and `tape_std_process_eov`.

Control flow: functions allocate `tape_request`s, fill CCW chains using helpers from `tape.h`, execute through `tape_do_io*`, then free requests. Repeated spacing/write-mark operations build repeated CCWs. `tape_std_terminate_write` writes pending tapemarks then backs over one. Assign uses an interruptible request with a 2-second timer that cancels stuck assignments. Read/write block builders map IDAL buffer arrays into chained READ_FORWARD/WRITE CCWs.

State and persistence: updates per-device mode-set byte, fixed block size, and `required_tapemarks`. No persistent state beyond the tape medium effects of commands such as write marks, erase, rewind, unload, and EOV handling.

Dependencies and integration: depends on tape core request execution, IDAL buffer arrays, `tape_std.h` command constants, mtio operation numbers, and discipline command tables such as 3490's `mtop_array`.

Risks: large `mt_count` can allocate large CCW arrays unless upper layers chunk selected operations; assignment timeout races with normal completion; retension intentionally ignores the first command return; EOM scanning depends on FSR returning positive over tapemarks; compression mutates mode-set byte before executing.

Test signals: MTIO command coverage, fixed/variable block read/write builders, assignment busy timeout, EOV write behavior, set-block validation against `MAX_BLOCKSIZE`, and residual-count behavior for FSR/BSR over tapemarks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/tape_std.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/tape_std.h -->
# sources/distributed-fs/ceph-client/drivers/s390/char/tape_std.h

Purpose: declares standard tape command constants, sense-byte masks, common tape operation prototypes, and the small s390 tape-type enum.

Important APIs/types/functions: defines `MAX_BLOCKSIZE`, CCW opcodes including `READ_FORWARD`, `WRITE_CMD`, `WRITETAPEMARK`, `ASSIGN`, `LOCATE`, `MODE_SET_DB`, and `READ_BLOCK_ID`; defines sense masks such as `SENSE_WRITE_PROTECT`, `SENSE_DRIVE_ONLINE`, and `SENSE_RECORD_SEQUENCE_ERR`; declares all `tape_std_*` helpers.

Control flow: no executable flow; the constants drive request construction in `tape_std.c` and sense interpretation in `tape_3490.c`.

State and persistence: no state. Constants describe hardware command and status layout.

Dependencies and integration: included by tape core, standard command builder, and 3490 discipline; prototypes expect `struct tape_device` and `struct tape_request` from `tape.h`.

Risks: constants are hardware ABI; wrong values break real tape operations or error handling. `MAX_BLOCKSIZE` bounds IDAL buffer allocation and userspace-visible MTSETBLK behavior.

Test signals: compile-time consumers, tape command execution on supported hardware/emulation, sense-code injection against 3490 recovery, and MTSETBLK boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/tape_std.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/uvdevice.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/uvdevice.c

Purpose: misc-device UAPI bridge that lets userspace issue selected s390 Ultravisor calls through validated ioctls when the UV facility is present.

Important APIs/types/functions: defines ioctl-to-UVC support mapping, global `uvdev_info`, `uvio_ioctl`, `uvio_copy_and_check_ioctl`, and handlers `uvio_uvdev_info`, `uvio_attestation`, `uvio_add_secret`, `uvio_list_secrets`, `uvio_lock_secrets`, and `uvio_retr_secret`. Registers misc device `UVIO_DEVICE_NAME`.

Control flow: ioctl entry validates direction/type/number/size, copies `struct uvio_ioctl_cb`, rejects flags/reserved data, dispatches by ioctl number, performs per-command size/address sanity checks, builds the matching UV control block, calls `uv_call` or `uv_call_sched`, stores UV return/reason codes, and copies the ioctl control block back to userspace.

State and persistence: persistent module state is only supported-command metadata and the miscdevice registration. Secret-store effects are persisted inside the Ultravisor, not in this driver. Sensitive retrieved-secret buffers are freed with `kvfree_sensitive`.

Dependencies and integration: depends on `asm/uvdevice.h`, `asm/uv.h`, UV facility detection via `module_cpu_feature_match`, Linux miscdevice and user-copy APIs, vmalloc/kzalloc allocation paths, and UV command availability bits in `uv_info.inst_calls_list`.

Risks: this is a privileged platform ABI surface; validation must prevent kernel memory corruption while leaving semantic UV errors in `uv_rc/uv_rrc`. List-secret loop bounds must not overrun the user buffer. Attestation copies several user-provided buffers and lengths. Retrieve-secret maps a UAPI index and output into one mutable buffer.

Test signals: ioctl ABI tests for all invalid command/type/size/reserved cases, UVDEV_INFO support mask on systems with varying UV command lists, attestation length/address failures, add/list/lock/retrieve secret return-code propagation, and secret-buffer zeroing checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/uvdevice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/vmcp.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/vmcp.c

Purpose: exposes a `/dev/vmcp` misc device for privileged userspace to issue z/VM CP commands through diagnose 8 (`cpcmd`) and read back CP responses.

Important APIs/types/functions: defines `struct vmcp_session`, CMA reservation helpers `early_parse_vmcp_cma` and `vmcp_cma_reserve`, session response alloc/free helpers, file ops `vmcp_open`, `vmcp_release`, `vmcp_read`, `vmcp_write`, and `vmcp_ioctl`, and device init `vmcp_init`.

Control flow: open requires `CAP_SYS_ADMIN`, allocates a per-file session, and defaults the response buffer to one page. Write copies a command up to 240 bytes, allocates response memory if needed, records the command in debug, calls `cpcmd`, stores response size/code, resets file offset, and returns the command length. Read drains the current response through `simple_read_from_buffer`. Ioctls get CP code, set next response buffer size, or get response size.

State and persistence: state is per-open session: response pointer, buffer size, CMA/allocation flag, response size/code, and mutex. CMA area size is configured early by `vmcp_cma=` and reserved only under z/VM. No command history is persisted except debug events.

Dependencies and integration: depends on z/VM detection, `asm/cpcmd.h`, `asm/vmcp.h`, s390 debug feature, miscdevice, CMA for large contiguous response buffers, and user-copy APIs.

Risks: CP commands are powerful, hence CAP_SYS_ADMIN gate; response buffers require physically adjacent pages for diagnose 8 and may fail for large sizes; `VMCP_SETBUF` caps order at 8; command text is debug-logged.

Test signals: load under z/VM vs non-VM, permission checks, command length boundary, SETBUF/GETSIZE/GETCODE ioctls, large response allocation via CMA fallback, repeated writes resetting read offset, and concurrent per-session locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/vmcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/vmlogrdr.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/vmlogrdr.c

Purpose: character driver for reading z/VM system service records from LOGREC, ACCOUNT, and SYMPTOM services through IUCV.

Important APIs/types/functions: defines `struct vmlogrdr_priv_t`, static `sys_ser[]` service descriptors, IUCV callbacks `vmlogrdr_iucv_path_complete`, `vmlogrdr_iucv_path_severed`, `vmlogrdr_iucv_message_pending`, CP recording helper `vmlogrdr_recording`, file ops `vmlogrdr_open`, `release`, `read`, sysfs attributes `autopurge`, `purge`, `autorecording`, `recording`, and driver/device registration helpers.

Control flow: module init checks z/VM, discovers recording privilege class, allocates minors and buffers, registers IUCV driver/class/devices, and adds one cdev covering three minors. Open is blocking-only and single-user per service, optionally starts CP recording, connects to the service over IUCV, and waits for connection completion/sever. Pending-message callback stores the IUCV message metadata and wakes readers. Read receives one record or record fragment into the page buffer, prefixes total length, appends `EOR` when complete, and copies buffered data to userspace.

State and persistence: each service keeps path pointer, connection/sever flags, pending message, receive count, page buffer position/remaining/residual, single-open flag, sysfs device pointers, and auto recording/purge settings. CP RECORDING state and queues exist in z/VM outside the driver.

Dependencies and integration: depends on z/VM, CP command interface, IUCV bus, EBCDIC-related headers, Linux cdev/class/device sysfs, wait queues, atomics, spinlocks, and user-copy APIs.

Risks: service buffers are only one page minus framing; oversized IUCV records rely on residual-length continuation. Some state updates such as `dev_in_use` cleanup are not always under the same spinlock used on open. CP command parsing expects English response text. Blocking open/read semantics require wakeups on severed paths.

Test signals: load only under VM, one-open enforcement, auto recording on/off and purge sysfs behavior, IUCV connect/sever wakeups, fragmented large record reads with length/EOR framing, queue-empty blocking read, and cleanup after partial init failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/vmlogrdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/vmur.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/vmur.c

Purpose: z/VM virtual unit-record device driver for reader, punch, and printer devices, exposed as character devices mapped directly by minor number to VM device number.

Important APIs/types/functions: defines ccw driver `ur_driver`, class `vmur`, debug area, reference helpers `urdev_alloc/get/put`, write CCW helpers `alloc_chan_prog`, `free_chan_prog`, `do_ur_io`, interrupt handler `ur_int_handler`, diagnose helpers for reader files, file ops `ur_open`, `ur_release`, `ur_read`, `ur_write`, `ur_llseek`, and ccw lifecycle methods `ur_probe`, `ur_set_online`, `ur_set_offline`, `ur_remove`.

Control flow: probe allocates `struct urdev`, creates `reclen`, uses diagnose 0x210 to validate VM class, stores drvdata, and installs interrupt handler. Online creates cdev and class node named `vmrdr-*`, `vmpun-*`, or `vmprt-*`. Writes build chained WRITE CCWs with a final NOP and synchronously wait for interrupt completion. Reads use diagnose 0x14 to position/read spool pages, optionally inject file record length into the first page, and copy page chunks to userspace.

State and persistence: `struct urdev` holds ccw device, record length, VM class, char device, open flag/wait queue, refcount, I/O completion pointer, and uevent work. `struct urfile` stores per-open access data and file record length. Spool file/device state lives in z/VM.

Dependencies and integration: depends on ccw bus/device APIs, z/VM diagnose calls 0x14/0x210, `asm/scsw.h`, Linux cdev/class, completions, mutexes, wait queues, and direct minor-to-devno mapping with 65,536 minors.

Risks: only one opener is allowed per device; read seek offsets must be page-aligned; writes require integral record lengths and cap to 511 records per I/O; offline refuses active references unless forced by remove; unsolicited device-end uevents hold references through workqueue scheduling.

Test signals: z/VM-only module load, reader vs punch/printer access-mode rejection, blocking/nonblocking open contention, diag14 EOF/no-medium cases, write record-length validation and interrupt status mapping, online/offline with active file descriptors, and unsolicited DE uevents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/vmur.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/vmur.h -->
# sources/distributed-fs/ceph-client/drivers/s390/char/vmur.h

Purpose: private declarations and constants for the z/VM unit-record character driver.

Important APIs/types/functions: defines VM unit-record class constants, supported default device types, packed `struct file_control_block`, spool-file status flags, `struct urdev`, `struct urfile`, minor/count limits, `MAX_RECS_PER_IO`, write command opcode, debug macro `TRACE`, ccw id helper `CCWDEV_CU_DI`, and `FILE_RECLEN_OFFSET`.

Control flow: no executable flow; structures are consumed by `vmur.c` for diagnose file metadata, ccw device state, and per-open state.

State and persistence: `urdev` persists for each probed ccw unit-record device while present; `urfile` is per open. VM spool file metadata in `file_control_block` is read from CP and not stored persistently by Linux.

Dependencies and integration: includes Linux refcount/workqueue and expects ccw, cdev, completion, mutex, waitqueue, and device definitions from implementation includes.

Risks: packed FCB layout and `FILE_RECLEN_OFFSET` are ABI-sensitive to z/VM spool page format; direct minor-to-devno mapping consumes a large minor range; record count limit protects channel program size.

Test signals: compile with `vmur.c`, FCB parsing for held/in-use/CP dump files, supported 2540/1403 device matching, and write count capping to 511 records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/vmur.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/zcore.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/zcore.c

Purpose: zfcp/nvme/eckd dump support module that exposes HSA memory access and re-IPL controls for creating dumps after an s390 dump IPL.

Important APIs/types/functions: defines `memcpy_hsa_iter`, `memcpy_hsa_kernel`, `init_cpu_info`, `release_hsa`, debugfs file ops for `reipl` and `hsa`, `check_sdias`, `zcore_reipl_init`, reboot/panic notifier `zcore_reboot_and_on_panic_handler`, and init `zcore_init`.

Control flow: init runs only for dump IPL without oldmem data, initializes SCLP SDIAS, verifies HSA size, checks the dumped system was 64-bit, copies boot CPU registers from HSA, loads and validates saved IPL parameter block and OS info flags, creates debugfs `zcore/reipl` and `zcore/hsa`, and registers reboot/panic notifiers. HSA copy reads pages through `sclp_sdias_copy` under a mutex and streams into an iterator.

State and persistence: tracks HSA availability, saved IPL block page, debugfs dentries, OS info flags, and a single aligned page buffer protected by mutex. Writing `0` to debugfs `hsa` releases HSA through diag308; reboot/panic also releases it.

Dependencies and integration: depends on SCLP SDIAS, diag308 IPL/release calls, lowcore offsets, save_area register plumbing, debugfs, panic/reboot notifiers, checksum helpers, `memcpy_real`, and dump IPL metadata in `ipl_info`.

Risks: HSA copy is explicitly not reentrant; releasing HSA is irreversible for dump extraction. Corrupted OS info/IPIB data is tolerated in places but bad checksum disables re-IPL block use. Module refuses 32-bit dumped systems for the 64-bit dump tool.

Test signals: dump IPL boot paths for FCP/NVMe/ECKD, debugfs hsa read/write, HSA memory copy through iterator, checksum failure handling, reipl write invoking correct diag308 subcode, and notifier release on panic/reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/zcore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/Makefile

Purpose: builds the s390 common I/O subsystem objects and optional CIO-related drivers.

Important APIs/types/functions: not code, but defines object composition for built-in CIO core (`airq.o`, `blacklist.o`, `cio.o`, `css.o`, `ccwreq.o`, tracing/debugfs and others), compound objects `ccw_device.o`, `qdio.o`, and `vfio_ccw.o`, and config-gated objects for CCWGROUP, QDIO, VFIO_CCW, SCM, EADM, CHSC, and CIO injection.

Control flow: kbuild collects always-built `obj-y` pieces, assembles multi-object drivers through `*-objs`, and adds optional objects based on Kconfig symbols. It also adds local include paths for generated trace headers.

State and persistence: no runtime state; it defines build-time composition.

Dependencies and integration: integrates this directory with Kbuild, trace header include resolution, and config-driven s390 driver selection.

Risks: missing an object here can silently omit subsystem functionality; trace objects require `-I$(src)` for local `define_trace.h` inclusion; optional compound object ordering matters for link dependencies.

Test signals: s390 kernel builds across key configs, especially `CONFIG_CCWGROUP`, `CONFIG_QDIO`, `CONFIG_VFIO_CCW`, trace-enabled builds, and allyesconfig/allmodconfig link checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/airq.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/airq.c

Purpose: supports s390 adapter interrupts and interrupt-vector allocation for CIO users such as QDIO and other adapter-backed devices.

Important APIs/types/functions: exports `register_adapter_interrupt`, `unregister_adapter_interrupt`, `airq_iv_create`, `airq_iv_release`, `airq_iv_alloc`, `airq_iv_free`, and `airq_iv_scan`; initializes interrupt handling with `init_airq_interrupts` and DMA pool with `airq_init`.

Control flow: registration validates handler/ISC, allocates a local-summary indicator when missing, registers the ISC, and RCU-adds the descriptor to the ISC list. Thin interrupt handler gets `tpi_info`, traces it, walks the ISC hlist under RCU, and calls handlers whose summary indicator is nonzero. Interrupt vectors may be cacheline DMA, guest-provided, or CIO DMA allocated; optional availability, bitlock, pointer, and data side arrays are allocated based on flags.

State and persistence: maintains one RCU hlist per ISC, a spinlock for list mutation, a DMA pool for cacheline vectors, and per-vector allocation metadata. No persistent storage.

Dependencies and integration: uses s390 `THIN_INTERRUPT`, ISC registration, CIO DMA helpers, dummy irq chip, tracepoints, RCU hlist APIs, DMA pools, and inverted-bit operations.

Risks: unregister must synchronize RCU before freeing indicators; `airq_iv_create` error unwind must match allocation mode, especially guest vectors; `airq_iv_alloc/free/scan` use inverted bit semantics; handlers are called only when summary indicators are nonzero.

Test signals: register/unregister across ISCs, interrupt delivery to multiple descriptors, RCU lifetime under concurrent interrupts, vector allocation/free/scan with all flag combinations, and DMA-pool failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/airq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/blacklist.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/blacklist.c

Purpose: implements `cio_ignore=` and `/proc/cio_ignore` device blacklisting so selected s390 channel devices are hidden from Linux or re-enabled later.

Important APIs/types/functions: defines bitmap `bl_dev`, parser helpers `blacklist_range`, `pure_hex`, `parse_busid`, `blacklist_parse_parameters`, setup hook `blacklist_setup`, exported query `is_blacklisted`, proc write parser `blacklist_parse_proc_parameters`, seq operations for displaying ignored ranges, and proc init.

Control flow: boot parsing accepts comma-separated old-style devnos, full bus ids, ranges, `all`, `ipldev`, `condev`, and `!` inversion. It sets or clears per-SSID device bits. Proc writes accept `free`, `add`, or `purge`; freeing schedules conditional CSS evaluation for offline devices, and purge calls `ccw_purge_blacklisted`. Proc reads coalesce contiguous blacklisted devices into range output.

State and persistence: blacklist state is an in-memory bitmap covering each ssid/devno. It is initialized from boot parameters and mutable via procfs; not persisted across boot except via kernel command line.

Dependencies and integration: used by CIO subchannel validation through `is_blacklisted`; depends on IPL metadata, console devno, CSS evaluation, ccw purge, procfs/seq_file, and CIO debug logging.

Risks: parser validates cssid but only stores ssid/devno, consistent with this bitmap shape; invalid ranges return warnings at boot and EINVAL via proc. Proc input is capped at 64 KiB and trims trailing whitespace. Mutating blacklist while devices exist depends on CSS re-evaluation/purge behavior.

Test signals: command-line forms and inversions, `ipldev`/`condev` expansion, proc add/free/purge, range coalescing output across ssid boundaries, invalid bus ids/ranges, and device discovery behavior after freeing ignored devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/blacklist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/blacklist.h -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/blacklist.h

Purpose: tiny private CIO header exposing blacklist lookup to the rest of the common I/O subsystem.

Important APIs/types/functions: declares `is_blacklisted(int ssid, int devno)` and wraps it in include guards.

Control flow: no executable flow; consumers call the function during subchannel/device validation.

State and persistence: no state in the header; implementation state is the bitmap in `blacklist.c`.

Dependencies and integration: included by CIO files that need to check whether a device should be ignored.

Risks: the declaration uses plain `int` parameters and assumes callers pass values within bitmap bounds; bounds are enforced by parser/discovery paths rather than this header.

Test signals: compile coverage for CIO consumers and blacklist lookup behavior through `blacklist.c` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/blacklist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/ccwgroup.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/ccwgroup.c

Purpose: implements the ccwgroup bus, allowing multiple ccw slave devices to be grouped into one higher-level device for drivers that need multi-subchannel units.

Important APIs/types/functions: exports `ccwgroup_set_online`, `ccwgroup_set_offline`, `ccwgroup_create_dev`, `dev_is_ccwgroup`, `ccwgroup_driver_register`, `ccwgroup_driver_unregister`, `ccwgroup_probe_ccwdev`, and `ccwgroup_remove_ccwdev`. Defines sysfs attributes `online` and `ungroup`, symlink helpers, bus type `ccwgroup_bus_type`, and notifier-driven ungroup work.

Control flow: create parses comma-separated bus ids, gets ccw devices, verifies same driver and driver_info, prevents devices from being in multiple groups by setting ccw drvdata under lock, optionally calls group driver setup, adds the group device, and creates bidirectional sysfs links. Online/offline call group driver hooks under an atomic on/off gate. Ungroup removes sysfs links and unregisters the group only when offline.

State and persistence: `struct ccwgroup_device` owns the grouped ccw device references, online/offline state, registration mutex, on/off atomic gate, and ungroup work. State is runtime-only and removed on ungroup or slave removal.

Dependencies and integration: depends on ccw device lookup and locks, Linux driver core bus/driver/device APIs, sysfs links, bus notifiers, and external `struct ccwgroup_driver` definitions from asm headers.

Risks: create/unwind must clear drvdata and put device refs via release; online/offline/ungroup races are serialized with `onoff`; if any slave ccw device disappears, the whole group is unregistered; bus id parsing is strict and ignores cssid in stored id beyond parsed fields.

Test signals: group creation with valid/invalid bus lists, duplicate grouping rejection, sysfs online/offline/ungroup, group driver unbind notifier, slave removal teardown, and driver register/unregister paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/ccwgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/ccwreq.c -->
# sources/distributed-fs/ceph-client/drivers/s390/cio/ccwreq.c

Purpose: implements the common internal CCW request engine for CIO device procedures, including path selection, retry, timeout, cancellation, interrupt status interpretation, and callback completion.

Important APIs/types/functions: exports/defines `lpm_adjust`, `ccw_request_start`, `ccw_request_cancel`, `ccw_request_handler`, `ccw_request_timeout`, and `ccw_request_notoper`; internal helpers include `ccwreq_next_path`, `ccwreq_stop`, `ccwreq_do`, `ccwreq_status`, and `ccwreq_log_status`.

Control flow: start initializes mask/retry/done/cancel state, adjusts the logical path mask, and calls `ccwreq_do`. The executor tries paths until retries are exhausted, starts I/O through `cio_start`, clears temporary improper status, moves to next path on access/path errors, and stops with callback on terminal errors. Interrupt handler accumulates/senses status, applies optional request filter and driver unit-check handler, optionally calls request check callback, then completes, restarts, or moves to another path. Timeout logs missing-interrupt details per channel path, clears the subchannel, and may record a final `-ETIME`.

State and persistence: state lives in `cdev->private->req` plus accumulated IRB in the ccw device DMA area. No persistent state; timeouts are configured through ccw device timeout machinery.

Dependencies and integration: uses low-level CIO `cio_start`, `cio_clear`, `cio_update_schib`, ccw device timeout and sense accumulation helpers, per-cpu `cio_irb`, subchannel data, CIO tracing, and optional ccw driver `uc_handler`.

Risks: path-mask and retry semantics are subtle, especially singlepath mode using `0x8080` to try all paths twice; cancellation maps killed I/O to `-EIO`; `drc` can override non-ENODEV errors after timeout; status filters/check callbacks can redirect restart/path decisions.

Test signals: no-path start, successful request, channel/device status errors, command reject/unit-check handler decisions, retry exhaustion, singlepath path rotation, cancellation before completion, timeout logging/clear, and not-oper completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/cio/ccwreq.c -->
