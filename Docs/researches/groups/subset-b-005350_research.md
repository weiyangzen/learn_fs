# subset-b-005350 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_debugfs.c

Purpose: provides the SCSI-specific blk-mq debugfs request printer used when `CONFIG_BLK_DEBUG_FS` wires `scsi_show_rq()` into the SCSI `blk_mq_ops`. It formats SCSI command metadata that the generic block layer cannot know: CDB text, retry counters, result code, timeout age, command flags, and whether the command is currently linked on host error-handling lists.

Important APIs/types/functions: `scsi_show_rq(struct seq_file *m, struct request *rq)` is the only externally declared function. It obtains the command with `blk_mq_rq_to_pdu()`, formats initialized CDBs through `__scsi_format_command()`, and prints `cmd->retries`, `cmd->allowed`, `cmd->result`, request timeout, allocation age, and `SCMD_*` flag names. `scsi_flags_show()` maps set bits to `TAGGED`, `INITIALIZED`, and `LAST` where known. `scsi_cmd_list_info()` scans `shost->eh_abort_list` and `shost->eh_cmd_q` under `host_lock` to annotate commands already owned by error handling.

Control flow: debugfs calls into `scsi_show_rq()` for a live request. The function only emits command details if `SCMD_INITIALIZED` is set, then always emits the flag set. Error-handler list detection is a read-only locked walk and returns a constant string, so no list state changes occur.

State and persistence: this file has no durable state. It reads volatile request, command, jiffies, and host error-handler list state and writes only to the supplied `seq_file`.

Dependencies and integration: depends on block request private data layout from `scsi_lib.c`, CDB formatting from `scsi_logging.c`, SCSI host locking, and blk debugfs registration in `scsi_mq_ops`.

Risks: output is diagnostic but runs against live commands, so lock coverage for error-handler lists matters. Unknown command flag bits are printed numerically, which is robust but can make newly added flags less readable until the table is updated.

Test signals: enable block debugfs, issue normal and timed-out SCSI I/O, and inspect request debugfs output for initialized commands, passthrough commands, commands on `eh_abort_list`/`eh_cmd_q`, and unknown flag-bit formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_debugfs.h

Purpose: declares the SCSI debugfs request formatting hook shared between the SCSI queueing code and the small implementation in `scsi_debugfs.c`.

Important APIs/types/functions: forward declares `struct request` and `struct seq_file`, then exposes `void scsi_show_rq(struct seq_file *m, struct request *rq);`.

Control flow: there is no executable logic. Inclusion allows `scsi_lib.c` to assign `.show_rq = scsi_show_rq` in blk-mq operations when block debugfs support is enabled.

State and persistence: no state is stored or persisted.

Dependencies and integration: intentionally avoids pulling full block or seq headers into includers by using forward declarations. It integrates `scsi_debugfs.c` with blk-mq debugfs setup in `scsi_lib.c`.

Risks: the declaration must stay synchronized with the implementation and the block-layer callback signature. Any signature drift will be caught at compile time.

Test signals: build with `CONFIG_BLK_DEBUG_FS` enabled and disabled to ensure the declaration remains sufficient for both configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_devinfo.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_devinfo.c

Purpose: maintains SCSI device quirk information, historically known as the blacklist/whitelist. It combines a large built-in table of vendor/model patterns with boot/module parameters, optional `/proc/scsi/device_info` updates, and keyed lists for subsystems that need their own devinfo namespace.

Important APIs/types/functions: `struct scsi_dev_info_list` stores padded vendor/model keys, `blist_flags_t flags`, and a compatibility-match flag. `struct scsi_dev_info_list_table` groups entries by key. `scsi_init_devinfo()` creates the global list, parses `scsi_dev_flags`, imports `scsi_static_device_list[]`, and creates the proc entry when configured. `scsi_get_device_flags_keyed()` returns matching flags, device-specific defaults, or global defaults. Exported mutators include `scsi_dev_info_list_add_keyed()`, `scsi_dev_info_add_list()`, and `scsi_dev_info_remove_list()`.

Control flow: initialization creates the global table, applies dynamic parameter entries first, then appends static compatible entries. Lookup trims leading/trailing spaces for compatible entries, matches vendor exactly, and treats model as a prefix; non-compatible entries are exact padded matches and are inserted at the head so runtime entries override older ones. The proc reader walks all tables with a two-list cursor; the proc writer copies a page-sized userspace string, parses `vendor:model:flags` entries, and adds non-compatible overrides.

State and persistence: runtime state lives in global linked lists, `scsi_default_dev_flags`, and the module parameter buffer. It is not durable across boot, but static entries are rebuilt on each init and user-provided module/proc entries persist for the lifetime of the module/core instance.

Dependencies and integration: scan code calls `scsi_get_device_flags*()` while creating `struct scsi_device`, and later SCSI paths consume `sdev->sdev_bflags` for LUN scanning, VPD, retry, queue, locking, DIF, and ULD attachment behavior. The file depends on procfs, module parameters, kernel lists, and SCSI devinfo flag definitions.

Risks: quirk matching is global and order-sensitive; a broad compatible prefix can alter discovery or I/O behavior for unrelated devices. Runtime list mutation is not visibly protected by a lock in this file, so callers must rely on init-time/proc-time usage patterns. This source snapshot also shows duplicated lines in the matching/write-adjacent code, which is a compile-time risk if present in the active tree.

Test signals: compile with and without `CONFIG_SCSI_PROC_FS`; boot with `scsi_dev_flags=` overrides; read and write `/proc/scsi/device_info`; scan devices that exercise compatible prefixes, exact runtime overrides, wildcard-like model strings from the static table, keyed list add/remove, and unsupported `__BLIST_UNUSED_MASK` rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_devinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_dh.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_dh.c

Purpose: implements SCSI device-handler registration and attachment. Device handlers provide array/path-management behavior such as ALUA, EMC, HP active/passive, or RDAC handling and are used by multipath and the SCSI midlayer to activate paths, set handler parameters, and interpret sense.

Important APIs/types/functions: `scsi_dh_blist[]` maps vendor/model prefixes to handler module names; `scsi_dh_find_driver()` prefers ALUA when target port group support is advertised. `scsi_register_device_handler()` and `scsi_unregister_device_handler()` maintain the global `scsi_dh_list`. `scsi_dh_add_device()` auto-attaches a known handler during device setup, while `scsi_dh_attach()`, `scsi_dh_activate()`, `scsi_dh_set_params()`, and `scsi_dh_attached_handler_name()` operate from a `request_queue`.

Control flow: lookup first scans registered handlers under `list_lock`; explicit attach can call `request_module("scsi_dh_%s")` and retry. Attach pins the handler module, calls its `attach()` method, maps `SCSI_DH_*` errors to Linux errno values, and stores `sdev->handler` on success. Release calls handler `detach()` and drops the module reference. Queue-based exported APIs resolve `struct scsi_device` through `scsi_device_from_queue()`, validate device state, call handler methods, then release the device reference.

State and persistence: persistent state is in-memory only: the registered handler list and `sdev->handler` pointers with module references. There is no disk state, but handler attachment changes live path-management behavior for the device.

Dependencies and integration: integrates with `scsi_lib.c` for queue-to-device resolution and with handler modules under `drivers/scsi/device_handler/`. Device handlers are called from request preparation, sense processing, multipath activation, and sysfs/dm paths.

Risks: handler name matching uses `strncmp(tmp->name, name, strlen(tmp->name))`, so prefix ambiguity must be avoided. Unregister removes a handler from the list but live devices rely on module references from attachment. Callback completion for `activate()` may run synchronously, so callers must not hold locks needed by completion.

Test signals: register/unregister each handler module, auto-attach by TPGS and by vendor/model blacklist, explicit attach to an already handled device, invalid handler name, activation on offline/cancelled devices, parameter setting, and module unload while devices are attached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_dh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_error.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_error.c

Purpose: owns SCSI timeout and error recovery. It decides whether failed commands are retried, requeued, completed, escalated to the host error-handler thread, recovered through REQUEST SENSE/TUR/START UNIT/reset actions, or failed after taking devices offline.

Important APIs/types/functions: timeout intake is `scsi_timeout()`, `scsi_abort_command()`, `scmd_eh_abort_handler()`, `scsi_eh_scmd_add()`, and `scsi_schedule_eh()`. Sense and disposition are handled by `scsi_check_sense()`, `scsi_decide_disposition()`, `scsi_noretry_cmd()`, and `scsi_eh_completed_normally()`. EH command hijacking uses exported `scsi_eh_prep_cmnd()` and `scsi_eh_restore_cmnd()`, with `scsi_send_eh_cmnd()` for REQUEST SENSE, TUR, and START UNIT. Reset escalation is `scsi_eh_ready_devs()` through device, target, bus, and host reset helpers. The per-host kernel thread is `scsi_error_handler()`. Userspace reset support is `scsi_ioctl_reset()`.

Control flow: normal completions call `scsi_decide_disposition()` from `scsi_lib.c`; timeout calls may schedule abort work or enqueue the command on `shost->eh_cmd_q`. Once all failed commands are no longer busy, `scsi_eh_wakeup()` wakes the EH thread. The default `scsi_unjam_host()` splices the host EH queue, optionally fetches sense, tries readiness recovery, escalates resets from narrow to broad scope, offlines devices that cannot recover, then flushes the done queue by retrying or completing commands. `scsi_restart_operations()` restores host state, wakes waiters, relocks removable media if needed, and reruns queues.

State and persistence: recovery state is volatile but central: `shost->host_failed`, `host_eh_scheduled`, `last_reset`, `eh_deadline`, `eh_cmd_q`, `eh_abort_list`, `eh_action`, `tmf_in_progress`; command `eh_eflags`, retries, result, sense buffers, and saved EH command state; device flags such as `was_reset`, `expecting_cc_ua`, `changed`, UA counters, pending event bits, and offline state. No durable storage is written.

Dependencies and integration: depends on low-level driver `scsi_host_template` callbacks for abort, reset, queuecommand, timeout policy, and retry policy; transport class `eh_strategy_handler`; device handlers for sense decisions; `scsi_lib.c` for queueing/completion; `scsi_logging.c` for diagnostics; runtime PM; blk-mq timeouts; and SCSI event delivery.

Risks: this is high-risk concurrency code. Correctness depends on host lock ordering, RCU ordering between inflight clearing and `host_failed`, balanced command hijack/restore, and avoiding missed EH wakeups. Reset escalation can disrupt many devices, while deadlines can force skipping recovery. Sense classification directly affects data-path retry/failfast behavior, capacity-change events, and device offlining.

Test signals: inject command timeouts, abort success/failure, REQUEST SENSE required and auto-sense paths, UNIT ATTENTION events, queue full ramp-down/ramp-up, failfast flags, duration-limit sense, ALUA/device-handler sense decisions, each reset handler level, EH deadline expiry, runtime PM resume failure, SG_SCSI_RESET authorization/escalation, and removable media relock after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_ioctl.c

Purpose: implements common SCSI ioctl handling and userspace passthrough compatibility for block/SCSI devices. It supports SG_IO, deprecated `SCSI_IOCTL_SEND_COMMAND`, CDROM packet commands, door lock/eject/start/stop, host/device identification, SG timeout/reserved-size controls, and reset dispatch.

Important APIs/types/functions: `scsi_ioctl()` is the exported dispatcher. `sg_io()` builds a passthrough request from `struct sg_io_hdr`, maps userspace I/O with `blk_rq_map_user_io()`, executes it, and fills status/sense fields. `sg_scsi_ioctl()` implements the old page-limited ABI. `get_sg_io_hdr()` and `put_sg_io_hdr()` translate native and compat SG headers. `scsi_cmd_allowed()` enforces unprivileged command filtering. `scsi_set_medium_removal()` sends ALLOW MEDIUM REMOVAL and updates `sdev->locked`.

Control flow: the dispatcher warns on deprecated ioctls, handles generic SG commands directly, routes reset to `scsi_ioctl_reset()`, and falls back to low-level driver ioctl callbacks. SG_IO validates interface id, transfer direction, transfer size, command length, permissions, and timeout, allocates a SCSI request, maps userspace buffers, executes synchronously, records duration, copies sense data back, unmaps the bio, and frees the request. CDROM packet ioctl is converted into an SG_IO-like request.

State and persistence: ioctl calls mutate runtime fields such as `sdev->sg_timeout`, `sg_reserved_size`, `lockable`, `locked`, and `changed`. They may also trigger device-visible media removal, start/stop, eject, and reset operations. There is no local durable persistence.

Dependencies and integration: depends on blk-mq request allocation from `scsi_lib.c`, command execution helpers, sense printing, Linux user-copy/compat APIs, cdrom and sg ABI structs, capability checks in `scsi_cmd_allowed()`, and error-handler reset support.

Risks: this file is a security boundary because unprivileged users can submit a restricted subset of CDBs. Command allowlisting, write-open checks, compat pointer conversion, length validation, and sense copying are key. Deprecated ioctls have fixed command length and PAGE_SIZE data limits. This source snapshot shows duplicated lines around reserved size and the old ioctl declaration, which should be compile-tested.

Test signals: run SG_IO read-only and write commands as privileged and unprivileged users, compat 32-bit SG_IO/CDROM paths, invalid command lengths and directions, oversize transfers, sense-buffer copyout, deprecated ioctl warning paths, door lock/unlock on removable media, reset permission failures, and driver ioctl fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_lib.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_lib.c

Purpose: is the SCSI midlayer queueing library. It bridges block-mq requests, SCSI command allocation, queue-depth budgeting, low-level driver `queuecommand()` calls, completion disposition, retries, request sense buffers, mode/TUR helper commands, device state transitions, SCSI event uevents, block/quiesce APIs, SG helpers, and VPD identifier extraction.

Important APIs/types/functions: request helpers include `scsi_alloc_request()`, `scsi_execute_cmd()`, `scsi_alloc_sgtables()`, `scsi_free_sgtables()`, `scsi_done()`, and `scsi_done_direct()`. blk-mq integration is `scsi_mq_setup_tags()`, `scsi_queue_rq()`, `scsi_complete()`, `scsi_mq_get_budget()`, and the `scsi_mq_ops` tables. Command outcome handling is `scsi_io_completion()`, `scsi_queue_insert()`, `scsi_result_to_blk_status()`, and passthrough retry matching through `scsi_check_passthrough()` plus `scsi_failures_reset_retries()`. Management helpers include `scsi_mode_select()`, `scsi_mode_sense()`, `scsi_test_unit_ready()`, `scsi_device_set_state()`, event APIs, device/target/host block and quiesce APIs, `scsi_kmap_atomic_sg()`, VPD helpers, and `scsi_build_sense()`.

Control flow: blk-mq obtains a budget token from the device bitmap, checks device/target/host readiness, prepares or reuses `struct scsi_cmnd`, allocates SG tables, calls ULD or device-handler preparation, starts the request, and dispatches to the low-level driver. Completion goes through `scsi_complete()`, which updates counters, asks `scsi_decide_disposition()`, then finishes, requeues, or hands commands to EH. `scsi_io_completion()` handles partial completion, block status mapping, retry/reprep decisions, ALUA transition delay, and failfast behavior. Queue restart paths manage starved devices and single-LUN targets.

State and persistence: runtime state spans the global sense-buffer cache, command flags/state, sense buffers, retries, SG tables, request flags, host/device/target busy counters, budget tokens, starved lists, queue stopped/quiesced markers, `sdev_state`, event lists/pending bits, VPD RCU pointers, and disk-event disable depth. No durable storage is written.

Dependencies and integration: integrates tightly with blk-mq, block integrity, DMA/SG APIs, SCSI ULD drivers, low-level host templates, device handlers, `scsi_error.c`, `scsi_logging.c`, transport classes, uevents, runtime PM users, and optional KUnit inclusion of `scsi_lib_test.c`.

Risks: request lifecycle is delicate: budget tokens, target busy counts, inflight state, SG allocation, `RQF_DONTPREP`, and driver-private command state must unwind correctly on every dispatch failure. State transitions gate I/O during removal, PM, transport loss, and recovery. VPD parsing trusts descriptor lengths from cached device data and relies on RCU lifetime. Several `BUG_ON`/`WARN_ON` paths indicate invariants that can panic or flag regressions in malformed requests.

Test signals: blk-mq dispatch under queue full/host busy/device busy, partial completions, failfast and no-retry behavior, passthrough retry definitions, SG allocation failures, DIX integrity requests, reserved commands, single-LUN fairness, state transitions across quiesce/block/offline/delete, mode sense fallback, TUR unit attention, event uevents, VPD page 0x80/0x83 parsing, and `CONFIG_SCSI_LIB_KUNIT_TEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_lib_dma.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_lib_dma.c

Purpose: contains the DMA-dependent SCSI library helpers that map and unmap a command's data scatterlist for low-level drivers.

Important APIs/types/functions: `scsi_dma_map(struct scsi_cmnd *cmd)` checks `scsi_sg_count(cmd)`, maps `scsi_sglist(cmd)` against `cmd->device->host->dma_dev` with `cmd->sc_data_direction`, returns the mapped segment count, returns zero for no SG list, and returns `-ENOMEM` if `dma_map_sg()` returns zero. `scsi_dma_unmap(struct scsi_cmnd *cmd)` performs the matching `dma_unmap_sg()` when an SG list exists. Both are exported.

Control flow: drivers call `scsi_dma_map()` after the midlayer has built the command SG table and before programming hardware descriptors. On completion or error unwind they call `scsi_dma_unmap()` with the same command.

State and persistence: no local state is stored. The DMA API records mapping state in architecture/IOMMU internals, and the command's SG entries may be updated with DMA addresses by the mapping call.

Dependencies and integration: depends on `scsi_alloc_sgtables()` in `scsi_lib.c` having populated the SG list, on the host's `dma_dev`, and on the Linux DMA mapping API. Low-level SCSI drivers consume these helpers in their queue paths.

Risks: map/unmap balance is critical; leaking mappings or unmapping unmapped SG lists can corrupt IOMMU state. Direction must match the command. Returning zero for no data and negative for mapping failure means callers must distinguish no-transfer commands from failure.

Test signals: run read/write I/O with zero, one, and many SG segments under IOMMU debugging; inject `dma_map_sg()` failure; verify low-level driver unwind paths unmap exactly once; exercise DMA directions for read, write, and no-data commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_lib_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_lib_test.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_lib_test.c

Purpose: provides KUnit coverage for the passthrough retry policy implemented by the static `scsi_check_passthrough()` helper in `scsi_lib.c`. It is included directly by `scsi_lib.c` when `CONFIG_SCSI_LIB_KUNIT_TEST` is enabled so the tests can reach that static helper.

Important APIs/types/functions: the suite `scsi_lib` contains `scsi_lib_test_check_passthough()`, which calls focused subtests for multiple sense definitions, wildcard sense/status/host/result matching, total retry limits, mixed per-failure and total limits, and retry reset behavior. Test commands are synthetic `struct scsi_cmnd` instances with local sense buffers populated by `scsi_build_sense()`.

Control flow: each subtest builds `struct scsi_failure` arrays, wraps them in `struct scsi_failures`, sets `sc.result` and sense data, then asserts whether `scsi_check_passthrough()` returns `-EAGAIN` or zero. Retry-limit tests call the helper repeatedly to verify per-entry `retries` and aggregate `total_retries` accounting, then use `scsi_failures_reset_retries()` to reset state.

State and persistence: only in-test stack objects are mutated. The tests intentionally exercise mutation of `failure->retries` and `failures->total_retries`; no kernel device state or persistent data is used.

Dependencies and integration: depends on KUnit, SCSI protocol constants, `struct scsi_failure`, `scsi_build_sense()`, and direct inclusion from `scsi_lib.c`. The test validates behavior used by `scsi_execute_cmd()` callers that pass `scsi_exec_args.failures`.

Risks: because it is included into `scsi_lib.c`, symbol visibility and compile options matter. The test name contains the misspelling `passthough`, which is harmless but easy to miss in test filtering. It does not cover concurrent callers or real request execution.

Test signals: enable `CONFIG_SCSI_LIB_KUNIT_TEST` and run the `scsi_lib` KUnit suite. Extend cases when new wildcard constants, retry counters, or passthrough failure semantics are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_lib_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_logging.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_logging.c

Purpose: centralizes SCSI command, device, result, and sense logging. It produces consistent `dev_printk()` prefixes containing disk name and request tag, formats CDB opcode/service-action names, and decodes normalized sense key/ASC/ASCQ data for diagnostics.

Important APIs/types/functions: exported print helpers are `sdev_prefix_printk()`, `scmd_printk()`, `__scsi_format_command()`, `scsi_print_command()`, `scsi_print_sense_hdr()`, `__scsi_print_sense()`, `scsi_print_sense()`, and `scsi_print_result()`. Internal helpers reserve small GFP_ATOMIC buffers, build headers with `sdev_format_header()`, map opcodes through `scsi_opcode_sa_name()`, and format or dump sense data through `scsi_format_sense_hdr()`, `scsi_format_extd_sense()`, and `scsi_log_dump_sense()`.

Control flow: callers request a log buffer, prefix it with optional disk name and tag, append formatted command/result/sense text, emit via `dev_printk()`, and free the buffer. Long CDBs are split into multiple hex-dump lines. Sense logging first tries `scsi_normalize_sense()`; normalized sense prints decoded key and additional sense text, otherwise raw sense bytes are hex dumped.

State and persistence: no persistent state is maintained. Logging reads command, request, device, sense, jiffies, and opcode tables, allocates transient buffers, and writes kernel log messages.

Dependencies and integration: used by SCSI error handling, queueing, ioctl handling, ULDs, and debugfs. It depends on SCSI opcode/sense lookup helpers, request tag/disk metadata, kernel printk/device logging, and `SCSI_SENSE_BUFFERSIZE`.

Risks: runs in atomic and error paths, so allocation uses `GFP_ATOMIC` and silently drops logs on allocation failure. The fixed 128-byte buffer can truncate verbose output; WARN checks catch overflow assumptions. Logging must avoid dereferencing missing `rq->q`/disk metadata, handled by `scmd_name()`.

Test signals: enable SCSI logging levels, issue normal CDBs, vendor/reserved opcodes, variable-length CDBs, long CDBs, normalized and malformed sense buffers, recovered errors, and failed commands with old request tags to verify readable non-overflowing log output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_logging.c -->
