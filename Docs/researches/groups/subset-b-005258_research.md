# Research: subset-b-005258

Grouped research for the ESAS2R management/SCSI paths, generic ESP SCSI core, and FCoE build hook requested by `subset-b-005258`. Each file section is bounded by the reconciliation markers and preserves the source path as its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_ioctl.c

## Purpose

`esas2r_ioctl.c` implements the ATTO ExpressSAS R6xx user-management interface. It bridges SCSI-device ioctls, `/proc/scsi/esas2r/ATTOnode`, and sysfs binary attributes to several firmware protocols: flash/FM API, FS API, VDA, CSMI, SMP passthrough, HBA ioctls, NVRAM parameter writes, and firmware core-dump retrieval. The file is not on the normal block I/O fast path, but it can issue firmware requests, build scatter/gather lists, allocate coherent DMA buffers, reset adapters, upload/download firmware data, and expose target inventory.

## Important APIs, Types, and Functions

The exported entry points are `esas2r_ioctl_handler()`, `esas2r_ioctl()`, `esas2r_write_params()`, `esas2r_read_fw()`, `esas2r_write_fw()`, `esas2r_read_vda()`, `esas2r_write_vda()`, `esas2r_read_fs()`, and `esas2r_write_fs()`. `handle_hba_ioctl()` is externally used by the sysfs `hw` binary attribute in `esas2r_main.c`.

Important internal helpers include `handle_buffered_ioctl()`, `handle_smp_ioctl()`, `handle_csmi_ioctl()`, `handle_hba_ioctl()`, `do_fm_api()`, `allocate_fw_buffers()`, `free_fw_buffers()`, and completion callbacks such as `complete_buffered_ioctl_req()`, `complete_fm_api_req()`, `complete_nvr_req()`, `vda_complete_req()`, and `fs_api_complete_req()`. `struct esas2r_buffered_ioctl` describes a reusable DMA-buffered command: adapter, source ioctl pointer, buffer length and offset, request-builder callback, and optional completion postprocessor.

The file owns module-global coherent-buffer state for buffered ioctls: `esas2r_buffered_ioctl`, `esas2r_buffered_ioctl_addr`, `esas2r_buffered_ioctl_size`, `esas2r_buffered_ioctl_pcid`, serialized by `buffered_ioctl_semaphore`. It also manipulates per-adapter firmware-transfer buffers under `a->firmware`, VDA buffers under `a->vda_buffer`, and FS API buffers under `a->fs_api_buffer`.

## Control Flow

`esas2r_ioctl_handler()` is the top-level dispatch. It validates that `arg` is present and `cmd` is in the Express ioctl range, copies a fixed `struct atto_express_ioctl` from userspace, checks `EXPRESS_IOCTL_SIGNATURE`, selects an adapter either from `hostdata` or `ioctl->header.channel`, then switches on the command. Simple commands return channel lists, adapter channel info, current/default NVRAM, or kernel pointers in `GET_MOD_INFO`. Request-producing commands call firmware helpers and translate negative kernel errors to ATTO ioctl return codes before copying the fixed ioctl structure back to userspace.

The shared buffered path is `handle_buffered_ioctl()`. It serializes all users with `down_interruptible()`, grows or allocates a global coherent buffer large enough for the command, copies the ioctl payload into that buffer, allocates an internal request, initializes an S/G context whose physical-address callback maps offsets into the coherent buffer, invokes the operation-specific callback, and waits on `a->buffered_ioctl_waiter` if the callback started asynchronous firmware work. On success it optionally runs a done callback and copies the coherent buffer back into the original ioctl object.

CSMI handling mixes local response filling and firmware tunneling. Local `GET_DRVR_INFO`, `GET_CNTLR_CFG`, `GET_CNTLR_STS`, SCSI-address lookup, and device-address lookup are handled from PCI and `targetdb` state. PHY, SMP/SSP/STP passthrough, link-error, connector, SATA signature, and task-management requests are tunneled through VDA ioctl requests with `VDA_IOCTL_CSMI`. The tunnel completion temporarily replaces the request completion callback so target ID and LUN returned by firmware are restored before the original completion path runs.

HBA ioctl handling similarly supports local adapter info, adapter address, firmware coredump trace upload/reset/info, SCSI passthrough, device address, adapter control, and limited device info, while tunneling selected functions when `HBAF_TUNNEL` is set or when the operation is backend-specific. SCSI passthrough builds a SCSI VDA request, copies CDB, LUN, direction, queue-tag flags, sense buffer pointer, and data length from the ioctl, then uses `scsi_passthru_comp_cb()` to map firmware `RS_*` status to ATTO passthrough status and advance enumeration to the next present target.

Firmware read/write uses a stateful cache. `esas2r_write_fw()` validates a flash image header at offset 0, caches command headers for upload/status queries, allocates coherent image storage for downloads, accumulates chunks, and calls `do_fm_api()` when the final byte arrives. `esas2r_read_fw()` either returns cached status, starts an upload into coherent storage, or executes an upload-size query against a temporary coherent header buffer. VDA and FS APIs follow a sysfs-like write-then-read model: writes cache the request in coherent memory; a read at offset 0 allocates a request, builds SG lists, starts firmware processing, waits for completion when needed, and then copies data back to the caller.

## State and Persistence Behavior

No on-disk state is written directly, but firmware/NVRAM state can be changed. `EXPRESS_IOCTL_WRITE_PARAMS` and `write_live_nvram` paths call `esas2r_nvram_write()` via `esas2r_write_params()`. Firmware flash paths can upload/download flash images or query flash state through FM/FS/VDA APIs. Adapter reset can be triggered by `ATTO_FUNC_ADAP_CTRL` with `ATTO_AC_AF_HARD_RST`.

Runtime state is kept in coherent buffers and per-adapter wait flags. The buffered ioctl buffer is global, reused across adapters, and protected by one semaphore. FM API, FS API, VDA, and NVRAM paths use per-adapter completion flags plus wait queues. Firmware upload/download state is kept in `a->firmware.state`, `header`, `data`, `orig_len`, and DMA addresses. The VDA and FS buffers are kept until driver unload or until reallocated larger.

## Dependencies and Integration Points

The file depends on Linux userspace copy helpers, coherent DMA APIs, PCI config/PCIe capability reads, wait queues, mutexes, semaphores, SCSI ioctl plumbing, and many ESAS2R helpers from `esas2r.h`: request allocation/free, VDA/FS/FM/NVRAM builders, SG-list construction, adapter reset, target database lookup, target enumeration, model-name helpers, and endian conversion helpers. It integrates with `esas2r_main.c` through SCSI host template `.ioctl`, `/proc` ioctl forwarding, and sysfs binary attribute read/write functions.

The firmware integration points are `esas2r_start_request()`, `esas2r_process_vda_ioctl()`, `esas2r_process_fs_ioctl()`, `esas2r_fm_api()`, `esas2r_nvram_write()`, and `esas2r_build_ioctl_req()`. User-space integration is with ATTO Express ioctl structures from `atioctl.h` and VDA structures from `atvda.h`.

## Risks and Edge Cases

The top-level ioctl copies only `sizeof(struct atto_express_ioctl)` from userspace and later uses embedded variable lengths for firmware/VDA/HBA payloads; compatibility depends on those payloads fitting the fixed union layout passed by this driver. Length arithmetic for buffered ioctls, firmware images, VDA, and FS API requests must stay bounded or coherent-buffer copies can overrun or silently truncate. Several waits use `wait_event_interruptible()` inside `while` loops without checking signal interruption, so interrupted management tools may still leave firmware work in flight.

Global buffered ioctl storage is keyed only by one semaphore and one `pcid`; reuse across adapters is serialized but still couples DMA memory lifetime to the adapter that last allocated it. Degraded-mode checks are present in selected tunnel/VDA paths but not uniformly before local operations. Adapter reset from an ioctl can race with other sysfs/proc management activity. CSMI and HBA address paths read `targetdb` entries, sometimes under `mem_lock` and sometimes without it, so target discovery/removal races are worth stress testing.

## Test Signals

Useful signals are successful Express signature validation and channel selection, GET_CHANNELS output for multiple adapters, READ/WRITE/DEFAULT_PARAMS behavior, FM firmware upload/download/status flows, FS BEGIN/read/write requests, VDA GSV/config/management/CLI/flash operations, CSMI local status/config/address commands, tunneled CSMI PHY/SMP/STP/task-management commands, HBA GET_ADAP_INFO including PCIe link fields and interrupt mode, HBA SCSI passthrough with data-in, data-out, no-data, sense data, and residuals, firmware coredump trace upload/reset/info, sysfs `fw`, `fs`, `vda`, `hw`, `live_nvram`, and `default_nvram` attributes, and failure injection for allocation failure, invalid versions/functions, degraded mode, bad target IDs, unsupported LUN encodings, and copy_to_user faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_log.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_log.c

## Purpose

`esas2r_log.c` implements the ESAS2R driver's small logging subsystem. It gates events by a module parameter, formats messages with optional device identity, translates ESAS2R log levels to kernel log priorities, and emits messages or hexdumps to the kernel log.

## Important APIs, Types, and Functions

The externally visible functions are `esas2r_log()`, `esas2r_log_dev()`, and `esas2r_log_hexdump()`. `esas2r_log_master()` is the shared formatter, declared with `__printf` checking and passed a `va_list`. `translate_esas2r_event_level_to_kernel()` maps `ESAS2R_LOG_CRIT`, `WARN`, `INFO`, `DEBG`, and `TRCE` to `KERN_CRIT`, `KERN_WARNING`, `KERN_INFO`, and `KERN_DEBUG`.

The module parameter `event_log_level` defaults to `ESAS2R_LOG_DFLT` from `esas2r_log.h`; normal builds log critical and warning events, while trace builds default to trace verbosity. A single `event_buffer[1024]` and `event_buffer_lock` are used to serialize formatted messages.

## Control Flow

Callers invoke `esas2r_log()` for plain driver messages or `esas2r_log_dev()` for messages that include device driver, bus, and device name fields. Both wrappers start a varargs list and call `esas2r_log_master()`. The master helper first checks `level <= event_log_level`; skipped messages do no formatting. For emitted messages it takes `event_buffer_lock` with IRQ save, zeroes the shared buffer, writes either `"<level>esas2r: "` or `"<level>esas2r [driver, bus, dev]"`, advances to the remaining buffer area, appends the caller's formatted message with `vsnprintf()`, calls `printk("%s\n", event_buffer)`, and releases the spinlock.

`esas2r_log_hexdump()` performs the same level check, then calls `print_hex_dump()` with offset prefixes, 16-byte rows, one-byte groups, and ASCII output enabled.

## State and Persistence Behavior

The file has no persistent storage. State is module-global: current log level, one formatting buffer, and one spinlock. The log level is readable through module-parameter permissions and affects all adapters in the module. Because formatting is centralized through one shared buffer, messages from multiple CPUs are serialized.

## Dependencies and Integration Points

The file depends on kernel logging, module parameters, `struct device`, spinlocks, and hex dump helpers through `esas2r.h`. The macros in `esas2r_log.h` compile debug and trace calls either to these functions or to no-ops depending on `ESAS2R_DEBUG` and `ESAS2R_TRACE`.

## Risks and Edge Cases

The formatter holds a spinlock while calling `printk()`, which is simple but can lengthen interrupt-disabled critical sections when logging heavily. Messages longer than the remaining fixed 1024-byte buffer are truncated by `vsnprintf()` but still emitted. `esas2r_log_hexdump()` returns `1` when it logs or skips, unlike `esas2r_log()` returning `0` on success; callers should not treat it as a conventional errno-style helper. Device formatting omits a separator after the device tuple before the caller message, so log readability depends on caller text.

## Test Signals

Validation signals include module loading with `event_log_level` values 0 through 5, critical/warning default output, debug/trace builds honoring macro expansion, device and non-device log prefixes, long-message truncation without overflow, hexdump formatting, and concurrent logging under interrupt and process contexts without interleaved shared-buffer output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_log.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_log.h

## Purpose

`esas2r_log.h` is the public logging interface for the ESAS2R driver. It defines the ESAS2R log-level enum, declares checked printf-style logging functions, and provides compile-time debug and trace macros used throughout the driver.

## Important APIs, Types, and Definitions

The level enum defines `ESAS2R_LOG_NONE`, `CRIT`, `WARN`, `INFO`, `DEBG`, and `TRCE`. `ESAS2R_LOG_DFLT` is `TRCE` when `ESAS2R_TRACE` is defined and `WARN` otherwise. Exported declarations are `esas2r_log()`, `esas2r_log_dev()`, and `esas2r_log_hexdump()`.

When `ESAS2R_DEBUG` is enabled, `esas2r_debug()` and `esas2r_hdebug()` call `esas2r_log(ESAS2R_LOG_DEBG, ...)`; otherwise they compile away. When `ESAS2R_TRACE` is enabled, `esas2r_bugon()` logs a trace message, dumps the stack, and calls `BUG()`, while `esas2r_trace_enter()`, `esas2r_trace_exit()`, and `esas2r_trace()` include function, file, and line metadata. Without tracing these macros also compile away.

## Control Flow

This header has no runtime control flow by itself, but it controls instrumentation compiled into other ESAS2R files. Debug builds route extra messages through `esas2r_log.c`; trace builds add function-entry/exit calls and make `esas2r_bugon()` fatal. Normal builds remove these calls at preprocessing time, which keeps fast paths and interrupt paths free of debug logging overhead.

## State and Persistence Behavior

There is no state in the header. The main behavioral state is the build configuration: `ESAS2R_DEBUG` and `ESAS2R_TRACE` determine whether macro call sites exist in the compiled driver, while `event_log_level` in `esas2r_log.c` determines runtime emission for compiled-in calls.

## Dependencies and Integration Points

The header forward declares `struct device` and relies on kernel `__printf` annotations. It is included by `esas2r.h`, which is then included across the ESAS2R driver. This means changes to macro behavior affect ioctl, target discovery, request completion, interrupt, and reset paths.

## Risks and Edge Cases

Trace builds are intentionally intrusive: `esas2r_bugon()` becomes a stack-dumping `BUG()` and trace logging may heavily affect timing. Because debug/trace macros compile away in normal builds, code must not rely on macro arguments having side effects. The default log level changes between trace and non-trace builds, so reproducing log volume requires knowing build flags as well as module parameters.

## Test Signals

Useful checks include building with and without `ESAS2R_DEBUG` and `ESAS2R_TRACE`, verifying no side-effect dependencies in macro arguments, confirming compile-time format checking on logging declarations, checking default log level in each build mode, and validating that trace call sites do not break performance-sensitive request or interrupt paths when enabled for diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_main.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_main.c

## Purpose

`esas2r_main.c` is the ESAS2R driver's Linux SCSI/PCI integration layer. It registers the PCI driver and SCSI host template, validates module parameters, probes and removes adapters, exposes sysfs and proc management entry points, queues SCSI commands, implements SCSI error-handling callbacks, manages request allocation/completion, converts firmware status to SCSI mid-layer status, handles target add/remove notifications, and runs timer/tasklet/event-work infrastructure.

## Important APIs, Types, and Functions

Primary entry points include module init/exit `esas2r_init()` and `esas2r_exit()`, PCI callbacks `esas2r_probe()` and `esas2r_remove()`, SCSI callbacks `esas2r_queuecommand()`, `esas2r_eh_abort()`, `esas2r_device_reset()`, `esas2r_target_reset()`, `esas2r_bus_reset()`, and `esas2r_host_reset()`, proc ioctl forwarding `esas2r_proc_ioctl()`, information callbacks `esas2r_show_info()` and `esas2r_info()`, and request lifecycle helpers `esas2r_alloc_request()`, `esas2r_free_request()`, `esas2r_complete_request_cb()`, and `esas2r_req_status_to_error()`.

The static `driver_template` wires this file into the SCSI mid-layer. Sysfs binary attributes are generated by `ESAS2R_RW_BIN_ATTR()` for `fw`, `fs`, `vda`, `hw`, and `live_nvram`; `default_nvram` is read-only. Module parameters include SGL page count, number of SG lists, SG table size, request counts, AE request count, per-LUN queue depth, adapter queue depth, maximum sectors, and interrupt mode.

## Control Flow

Module init clamps user-supplied module parameters to supported ranges, zeros the global `esas2r_adapters[]`, and registers `esas2r_pci_driver`. PCI probe enables the device, allocates a `Scsi_Host` with adapter and request storage in hostdata, initializes host limits and queue settings, calls `pci_set_master()`, delegates hardware setup to `esas2r_init_adapter()`, stores hostdata in PCI drvdata, calls `scsi_add_host()`, enables firmware events, scans the SCSI host, and creates sysfs binary files. Remove calls `esas2r_kill_adapter()` and decrements the adapter count.

SCSI command submission starts in `esas2r_queuecommand()`. It rejects commands immediately in degraded mode, allocates a request, maps direction flags and CDB into the VDA SCSI request, stores target ID, LUN, sense buffer, and transfer length, maps the SCSI scatterlist with `scsi_dma_map()`, uses `get_physaddr_from_sgc()` plus `esas2r_build_sg_list()` to translate the Linux scatterlist into firmware S/G entries, and starts the request. Completion in `esas2r_complete_request_cb()` unmaps DMA, maps non-success `RS_*` status to SCSI result and residual, completes the command with `scsi_done()`, and returns the request to the free list.

Error handling searches driver queues and issues task-management requests when needed. `esas2r_eh_abort()` scans `defer_list` and `active_list`; pending non-active commands are removed locally, while active commands allocate an abort request using the original handle. Host and bus resets call `esas2r_reset_adapter()` or `esas2r_reset_bus()` and wait for `AF_OS_RESET` to clear. Device and target resets allocate task-management requests, send logical-unit or target reset functions, wait for completion, and retry on `RS_BUSY`.

Tasklet and timer flow is split between flags. The timer periodically sets `AF2_TIMER_TICK` and schedules the tasklet. `esas2r_adapter_tasklet()` services timer ticks, pending interrupts, and other deferred work until no tasklet bits remain. Firmware target-state events are queued as delayed work outside interrupt context. `esas2r_target_state_changed()` maps target states to add/remove/LUN-change work, and the worker calls SCSI add/remove helpers or emits firmware asynchronous-event logs.

## State and Persistence Behavior

Persistent device configuration is exposed through the `live_nvram` and `default_nvram` sysfs attributes and through ioctl paths implemented in `esas2r_ioctl.c`, but this file mainly manages runtime state. Global state includes `found_adapters`, `esas2r_adapters[]`, one proc-host pointer, and one proc major. Per-adapter state includes queues, request free list, target database, sysfs-created flags, firmware-event list, timer, tasklet flags, PCI device, SCSI host, NVRAM pointer, firmware revision strings, local ioctl buffer, and memory-window base.

The target database is reflected into SCSI devices by queued firmware events. `buffered_target_state` is used by `/proc` show output, while target add/remove events call the SCSI mid-layer. Request objects are reused from the hostdata-allocated pool; `esas2r_rq_init_request()` and `esas2r_rq_destroy_request()` reset firmware-facing request state at allocation/free time.

## Dependencies and Integration Points

This file depends on PCI driver registration, SCSI host templates, SCSI DMA mapping, sysfs binary attributes, procfs, char-device registration, timers, tasklets, workqueues, wait/completion primitives, and ATTO firmware helper functions declared in `esas2r.h`. It integrates with `esas2r_ioctl.c` for sysfs/proc/ioctl management, `esas2r_targdb.c` for target enumeration, lower-level hardware files for adapter init/kill/interrupt/reset/deferred processing, and VDA/NVRAM helpers for firmware state.

## Risks and Edge Cases

Several probe error paths call `scsi_host_put()` but do not visibly undo all earlier PCI enable/master state in this file; correctness relies on lower-level initialization failure cleanup or PCI core behavior. `esas2r_info()` lazily registers one global proc/char-device endpoint tied to the first host that calls it, so multi-adapter behavior depends on channel selection in the ioctl payload. `esas2r_queuecommand()` returns host busy on allocation, DMA map, or SGL-build failure, so queue-pressure tests should verify no request or DMA leaks. Reset and abort loops poll with sleeps and depend on firmware completion status transitions; stuck firmware can hold EH paths for a long time. Firmware-event work uses allocated delayed-work objects and `fw_events_off`; removal must ensure queued work cannot touch freed adapter state.

## Test Signals

Good signals include module-parameter clamping logs, PCI probe and `scsi_add_host()` success, sysfs binary file creation flags, SCSI scan results for discovered targets, normal read/write/inquiry command completion, scatterlist-heavy I/O, request-pool exhaustion behavior, abort of queued and active commands, device/target/bus/host reset under load, degraded-mode command rejection, firmware target add/remove/LUN-change events causing SCSI rescan/removal, proc `ATTOnode` ioctl routing, `show_info` target listing, status-to-error mapping for all `RS_*` values, and driver unload with pending timer/tasklet/event work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_targdb.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_targdb.c

## Purpose

`esas2r_targdb.c` manages the ESAS2R in-memory target database. It initializes target slots, adds RAID logical devices and passthrough physical devices during discovery, removes targets, reports state transitions to the SCSI integration layer, and provides lookup/count helpers by SAS address, identifier, virtual target ID, and next present target.

## Important APIs, Types, and Functions

Externally used functions include `esas2r_targ_db_initialize()`, `esas2r_targ_db_remove_all()`, `esas2r_targ_db_report_changes()`, `esas2r_targ_db_add_raid()`, `esas2r_targ_db_add_pthru()`, `esas2r_targ_db_remove()`, `esas2r_targ_db_find_by_sas_addr()`, `esas2r_targ_db_find_by_ident()`, `esas2r_targ_db_find_next_present()`, `esas2r_targ_db_find_by_virt_id()`, and `esas2r_targ_db_get_tgt_cnt()`.

The central data type is `struct esas2r_target`, stored in the adapter's `a->targetdb` range. The file manipulates target state fields (`target_state`, `buffered_target_state`, `new_target_state`), addressing fields (`virt_targ_id`, `phys_targ_id`, `sas_addr`, `identifier`), geometry fields (`block_size`, `inter_byte`, `inter_block`), and flags such as `TF_PASS_THRU` and `TF_USED`.

## Control Flow

Initialization walks all target entries, clears them, and sets stable absent/invalid states. Discovery calls either `esas2r_targ_db_add_raid()` for RAID groups or `esas2r_targ_db_add_pthru()` for passthrough devices. RAID add validates the virtual ID and RAID dimensions, rejects already-present slots, fills block/interleave geometry, sets invalid physical ID, clears passthrough state, marks the entry used and present, and returns the target. Passthrough add first tries to find an existing target by device identifier to preserve identity across discovery, otherwise uses the current virtual ID if available, copies the identifier, records physical and virtual IDs, marks passthrough/used, and sets present.

Removal is intentionally minimal: `esas2r_targ_db_remove()` marks `target_state` as `TS_NOT_PRESENT`. `esas2r_targ_db_remove_all()` iterates present targets, calls remove under `mem_lock`, and optionally calls `esas2r_target_state_changed()` so the SCSI layer removes the device. `esas2r_targ_db_report_changes()` skips reporting while discovery is pending, then compares each target's `buffered_target_state` with `target_state` under `mem_lock`; changed states are copied to the buffered field and reported outside the lock.

Lookup helpers do straightforward linear scans over the target database. `find_next_present()` returns the first present target ID after a supplied ID or `ESAS2R_MAX_TARGETS` when no later target exists, which is used by ioctl enumeration.

## State and Persistence Behavior

The target database is volatile runtime state derived from firmware discovery. It persists in memory across command handling until discovery, removal, reset, or driver teardown changes it. `buffered_target_state` acts as a reporting latch so the SCSI layer is notified once per state change. Passthrough identifiers help reuse target slots for devices that were seen before. No disk state is written.

## Dependencies and Integration Points

The file depends on `struct esas2r_adapter`, `struct esas2r_disc_context`, target flags/states, `mem_lock`, debug/trace macros, and `esas2r_target_state_changed()` from `esas2r_main.c`. It is consumed by discovery code, SCSI add/remove event code, CSMI/HBA ioctl address lookup, and passthrough enumeration.

## Risks and Edge Cases

Most lookup helpers are lockless and rely on callers to hold `mem_lock` when needed; the call sites are inconsistent, so discovery or removal races can expose transient target data. `add_pthru()` can reuse a target found by identifier even if discovery's current virtual ID differs, which preserves identity but requires stale fields to be fully overwritten. `remove()` leaves flags and identity data intact, so absent entries can still match identifier/SAS lookups unless callers also check `target_state`. `add_raid()` rejects zero block size/interleave but does not validate interleave divisibility beyond computing `interleave / block_size`.

## Test Signals

Useful signals include initialization clearing all targets, RAID add rejecting invalid dimensions and duplicate present slots, passthrough add preserving identity across rediscovery, remove-all with and without notification, report-changes suppression during `AF_DISC_PENDING`, SCSI add/remove notifications for `TS_PRESENT`, `TS_NOT_PRESENT`, and LUN-change states, CSMI/HBA address lookup while targets are present and absent, and concurrent discovery/reset/ioctl stress around `mem_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_targdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_vda.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_vda.c

## Purpose

`esas2r_vda.c` builds and completes ESAS2R VDA firmware requests. It validates user-supplied VDA ioctl functions and versions, maps ioctl payloads into firmware request unions, constructs S/G lists for flash, CLI, management, config, and asynchronous-event requests, performs host/firmware endian conversion for management/config/event data, and starts requests through the common request engine.

## Important APIs, Types, and Functions

The main external API is `esas2r_process_vda_ioctl()`, used by ioctl/sysfs VDA read paths to prepare a firmware request. Other exported builder helpers are `esas2r_build_flash_req()`, `esas2r_build_mgt_req()`, `esas2r_build_ae_req()`, `esas2r_build_ioctl_req()`, and `esas2r_build_cfg_req()`. Internal helpers are `esas2r_complete_vda_ioctl()` and `clear_vda_request()`.

`esas2r_vdaioctl_versions[]` is the function-version compatibility table, indexed by VDA function. The request target is `rq->vrq`, a `union atto_vda_req`, with companion response state in `rq->func_rsp` and data buffer state in `rq->data_buf` / `rq->vda_rsp_data`.

## Control Flow

`esas2r_process_vda_ioctl()` starts by setting host-visible success and pending VDA status. It rejects unknown function indexes, too-new versions, and degraded adapters. Non-SCSI functions clear the VDA request while preserving the firmware handle. The request function, interrupt callback, and callback context are installed, then a switch fills the function-specific request.

Flash ioctl accepts file read, write, and info subfunctions, copies the filename, sets length and subfunction, and uses the flash file SGE as the first data SGE for read/write. CLI sets command/response length and data length. Management has the most complex flow: for health and metrics requests it may build a payload SGL separately from the management command SGL; for device-info variants it treats the ioctl data area as the command data; other data-bearing management functions are rejected. Config only supports `VDA_CFG_GET_INIT` through this ioctl path, copies config input data, and endian-converts it before firmware submission. GSV is local: it returns the version table and marks VDA status success without starting firmware work.

When a data length is present, the function initializes an S/G context at the selected first SGE, sets the length, builds the S/G list, and returns an out-of-resources status on failure. For firmware-submitted commands it calls `esas2r_start_request()` and returns true to tell the caller to wait for completion.

`esas2r_complete_vda_ioctl()` copies firmware response fields back into the ioctl. Flash read/info updates file size. Management updates scan generation, device index, optional returned data length, and endian-converts management data back. Config GET_INIT builds user-visible firmware release/version strings and numeric fields. CLI updates command response length.

The builder helpers are used by lower-level driver flows as well as ioctl flows. They clear the request, set the VDA function/subfunction/length, choose legacy SGE versus PRDE layout based on `AF_LEGACY_SGE_MODE`, and copy or endian-convert payloads as needed.

## State and Persistence Behavior

The file does not persist data itself, but VDA requests can query or mutate firmware configuration, RAID groups, flash contents, device health, and asynchronous-event state. Request-local state is stored in `rq->vrq`, `rq->req_stat`, `rq->interrupt_cb`, `rq->interrupt_cx`, `rq->data_buf`, and request list linkage. `clear_vda_request()` preserves the request handle while clearing the rest of the request and data buffer, then initializes the list head to keep non-started requests safe.

## Dependencies and Integration Points

The file depends on VDA ABI types and constants from `atvda.h`, ATTO ioctl definitions, ESAS2R request and SG helpers, adapter degraded/legacy flags, endian conversion helpers in `esas2r_main.c`, and the common firmware start path. It integrates with `esas2r_ioctl.c` for sysfs/ioctl VDA requests and with event/discovery code for management and asynchronous-event requests.

## Risks and Edge Cases

Function-version validation relies on the version table matching firmware ABI expectations. Management requests change `sgc->cur_offset` in non-obvious ways to build payload and command SGLs from different portions of the ioctl buffer; offset mistakes can DMA the wrong user payload. `clear_vda_request()` preserves only the SCSI handle, so callers must reinitialize every required field. GSV completes locally and returns success without starting a request; callers must honor the boolean return. Endian conversion helpers are symmetric in practice but named `nuxi`; applying them twice or missing them on a path will corrupt fields. Builder helpers use `if (vrq->length)` on a little-endian field, which works for nonzero checks but is stylistically fragile.

## Test Signals

Useful tests include invalid function/version/degraded-mode rejection, GSV local completion, flash FINFO/FREAD/FWRITE with file-size response, CLI command length round trip, management health/metrics payload SGLs, device-info management variants, config GET_INIT firmware-release formatting, legacy SGE and PRDE modes, out-of-SGL-resource failure, asynchronous-event request layout, and endian-correct values for capacities, block sizes, target IDs, scan generation, and firmware version fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esas2r/esas2r_vda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esp_scsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/esp_scsi.c

## Purpose

`esp_scsi.c` is the generic core for NCR/Symbios ESP-family SCSI host adapters. Platform front-end drivers provide register/DMA operations and hardware resources; this file provides chip reset/probing, SCSI command queueing, target/LUN tag management, SCSI phase/event handling, DMA progression, synchronous/wide negotiation, reselection/disconnect support, autosense, interrupt handling, SCSI error handling, and SPI transport integration.

## Important APIs, Types, and Functions

Exported symbols are `scsi_esp_template`, `scsi_esp_register()`, `scsi_esp_unregister()`, `scsi_esp_intr()`, `scsi_esp_cmd()`, and, when PIO support is enabled, `esp_send_pio_cmd()`. Front-end drivers allocate a `Scsi_Host` using `scsi_esp_template`, initialize `struct esp`, install `struct esp_driver_ops`, map command DMA memory, register `scsi_esp_intr()` as the interrupt handler, then call `scsi_esp_register()`.

Important internal groups include chip setup (`esp_set_clock_params()`, `esp_get_revision()`, `esp_reset_esp()`, `esp_bootup_reset()`), DMA state (`esp_map_dma()`, `esp_unmap_dma()`, `esp_cur_dma_addr()`, `esp_cur_dma_len()`, `esp_advance_dma()`, `esp_dma_length_limit()`), command scheduling (`esp_queuecommand_lck()`, `esp_get_ent()`, `esp_put_ent()`, `find_and_prep_issuable_command()`, `esp_maybe_execute_command()`), completion (`esp_cmd_is_done()`), phase engine (`esp_process_event()`), interrupt handling (`__esp_interrupt()`, `scsi_esp_intr()`), reconnect handling (`esp_reconnect()`, `esp_reconnect_with_tag()`), negotiation (`esp_setsync()`, `esp_msgin_sdtr()`, `esp_msgin_wdtr()`, `esp_msgin_reject()`), and EH (`esp_eh_abort_handler()`, `esp_eh_bus_reset_handler()`, `esp_eh_host_reset_handler()`).

## Control Flow

Registration sets host transport state, defaults tag count, sets max LUN and per-LUN command count, computes clock conversion/timeout/sync defaults, probes chip revision by config register behavior and ID family, initializes lists and target negotiation goals, resets the ESP and SCSI bus, waits for the bus reset settle time, adds the SCSI host, and scans targets.

`esp_queuecommand_lck()` allocates or reuses an `esp_cmd_entry`, attaches the `scsi_cmnd`, queues it, and calls `esp_maybe_execute_command()`. If no command is active and the chip is not resetting, command selection chooses an issuable entry whose LUN tag rules allow dispatch. `esp_maybe_execute_command()` maps DMA, saves data pointers, builds identify/tag/negotiation messages and CDB bytes, chooses select-with-ATN, select-and-stop, or select-with-ATN3, programs target sync/config registers, and starts the command via FIFO or platform DMA.

Interrupts drive the SCSI phase machine. `scsi_esp_intr()` takes `host_lock`, checks front-end `irq_pending()`, calls `__esp_interrupt()`, and loops briefly for quick follow-up interrupts. `__esp_interrupt()` snapshots status, sequence, and interrupt registers, detects reset/gross/spurious/DMA errors, handles FASHME FIFO snapshots, finishes selection or reconnects on reselection, then repeatedly calls `esp_process_event()`. The event engine transitions through command, data-in/out, data-done, status, message-in/out, free-bus, check-phase, and reset events. It starts DMA transfers with chip/front-end limits, computes actual bytes sent from counters/FIFO residuals, advances scatterlist state, processes SCSI messages, handles disconnects by clearing `active_cmd`, and completes commands or launches autosense on CHECK CONDITION.

Autosense is local to the driver. When a command completes with CHECK CONDITION and is not already autosensing, the entry is marked `ESP_CMD_FLAG_AUTOSENSE`, a REQUEST SENSE command is built against the same target/LUN and sense buffer, and completion restores CHECK CONDITION semantics while providing sense data to the original command.

EH abort first tries to remove a still-queued command. For the active command it sends an ABORT_TASK_SET message by asserting ATN and waits up to five seconds for completion. Disconnected commands are not directly aborted and are left to bus/host reset. Bus reset issues ESP SCSI bus reset and waits for reset completion; host reset performs a bootup chip reset and cleanup.

## State and Persistence Behavior

All state is volatile in memory and hardware registers. `struct esp` tracks register/DMA resources, front-end operations, active command, queued/active lists, command entry pool, command DMA buffer, data DMA length, last hardware status registers, per-target negotiation state, FIFO snapshot, event log, message buffers, chip revision, flags, clock parameters, selection/event state, and EH reset completion. `struct esp_target_data` stores negotiated and desired sync/wide state per target. `struct esp_lun_data` stores the non-tagged command, tagged command table, tag count, and hold state per LUN. `struct esp_cmd_priv` stores scatterlist progression per SCSI command.

Negotiation state persists across commands until reset or transport settings change. Reset cleanup forces renegotiation by clearing per-target sync/wide bits and setting `ESP_TGT_CHECK_NEGO`. The event log is an in-memory ring used for diagnostics and dumped on errors.

## Dependencies and Integration Points

The file depends on Linux SCSI mid-layer APIs, SCSI transport SPI domain validation and attributes, DMA mapping APIs, host locks, completions, module parameters, and platform-specific ESP front-end operations. It exports a reusable core for platform drivers such as SBus, Mac, or other ESP-family adapters. Integration contracts with front-ends are strict: `irq_pending()`, `send_dma_cmd()`, `dma_error()`, `dma_drain()`, `dma_invalidate()`, register access, and optional DMA length limiting must accurately reflect hardware behavior.

## Risks and Edge Cases

The code is a hardware state machine with many chip-revision quirks. Wrong front-end IRQ or DMA-error reporting can cause missed interrupts, spurious resets, or data corruption. Reselection with tags is polling-heavy and assumes quick follow-up interrupts; timeouts force reset. DMA byte accounting depends on ESP counters, FIFO state, wide mode, residual-byte quirks, and front-end drain/invalidate semantics. Disconnected command abort is not implemented, so error recovery may escalate to bus reset. The PIO path casts DMA addresses to CPU pointers and is only valid when the front-end sets `ESP_FLAG_NO_DMA_MAP` and supplies virtual-address style transfers. Heavy debug logging and command-log dumps can be noisy under error storms.

## Test Signals

Important signals include registration on each supported chip revision, correct clock/timeout values, boot reset and bus settle, SCSI scan, basic CDB dispatch, scatterlist DMA progression across segment and 24-bit/16-bit boundaries, data-in/out under FIFO and DMA modes, disconnect/reconnect with and without tags, sync and wide negotiation including message reject fallback, autosense on CHECK CONDITION, queue-full feedback, abort of queued and active commands, bus reset and host reset cleanup, FASHME FIFO handling, ESP100/FAS/AM53c974 quirks, PIO transfers when configured, and front-end fault injection for DMA error, spurious IRQ, illegal command, gross error, and reselection timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esp_scsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esp_scsi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/esp_scsi.h

## Purpose

`esp_scsi.h` defines the hardware register map, bitfields, commands, status/interrupt values, timing formulas, chip revisions, private SCSI command state, target/LUN state, front-end operation contract, main `struct esp`, state-machine constants, and exported entry points for the generic ESP SCSI core.

## Important APIs, Types, and Definitions

The header defines ESP register offsets such as `ESP_TCLOW`, `ESP_FDATA`, `ESP_CMD`, `ESP_STATUS`, `ESP_INTRPT`, `ESP_SSTEP`, `ESP_FFLAGS`, `ESP_CFG1` through `ESP_CFG4`, HME/FAS aliases, and `SBUS_ESP_REG_SIZE`. It defines config bits, command opcodes (`ESP_CMD_FLUSH`, `RC`, `RS`, `TI`, `ICCSEQ`, `MOK`, `SATN`, `SELA`, `SELAS`, `SA3`, `DMA`), SCSI phase masks (`ESP_DOP`, `DIP`, `CMDP`, `STATP`, `MOP`, `MIP`), interrupt bits, sequence-step values, FIFO flags, clock conversion constants, and sync defaults.

Core types are `struct esp_cmd_priv` for per-command scatterlist residue, `enum esp_rev` for ordered chip capability levels, `struct esp_cmd_entry` for queued/active command state and autosense metadata, `struct esp_lun_data` for tag/non-tagged command tracking, `struct esp_target_data` for negotiated and desired transfer settings, `struct esp_event_ent` for diagnostic event log entries, `struct esp_driver_ops` for platform callbacks, and `struct esp` for the main controller instance.

Exported declarations are `scsi_esp_template`, `scsi_esp_register()`, `scsi_esp_unregister()`, `scsi_esp_intr()`, `scsi_esp_cmd()`, and `esp_send_pio_cmd()`.

## Control Flow and Design Role

The header encodes the front-end driver recipe in comments: allocate a host with `scsi_esp_template`, fill `struct esp`, hook `esp->ops`, set capability flags, map registers and DMA, map the command block, register the interrupt handler, populate SCSI ID/clock/bus properties, perform pre-programming DMA setup, set drvdata if needed, and call `scsi_esp_register()`. The core C file then uses these definitions to drive hardware commands and SCSI phase transitions.

State-machine constants in `struct esp` and macros define the legal software events and selection states used by `esp_process_event()` and `__esp_interrupt()`. Register bit definitions must match hardware exactly because front-end `esp_read8()`/`esp_write8()` calls use these offsets and values directly.

## State and Persistence Behavior

The header itself stores no state, but it defines all persistent runtime state for the core. `struct esp` persists for the lifetime of a host adapter. `struct esp_target_data` persists per target and survives across commands until reset or SPI transport reconfiguration. `struct esp_lun_data` persists per SCSI device and tracks outstanding tags. `struct esp_cmd_entry` persists while a command is queued, active, disconnected, or autosensing. Timing fields (`cfreq`, `cfact`, `ccycle`, `ctick`, `neg_defp`, min/max periods) persist after registration and chip probing.

## Dependencies and Integration Points

The header assumes Linux SCSI core types, scatterlists, DMA addresses, completions, list heads, MMIO pointers, and IRQ return types are available through includers. It is included by `esp_scsi.c` and platform front-end drivers. The most important integration boundary is `struct esp_driver_ops`: incorrect implementation of register access, IRQ pending, DMA setup, DMA drain/invalidate, reset, or DMA error reporting breaks the core state machine.

## Risks and Edge Cases

Many constants are chip ABI. Incorrect bit definitions, enum ordering, or structure field interpretation can produce hardware commands with wrong phases or corrupt negotiation state. `ESP_MAX_TARGET`, `ESP_MAX_LUN`, and `ESP_MAX_TAG` bound arrays directly. `ESP_CMD_PRIV(cmd)` assumes the SCSI host template reserved `cmd_size = sizeof(struct esp_cmd_priv)`. Front-end drivers must honor the setup checklist, especially command block DMA mapping and accurate SCSI ID mask. PIO support requires `fifo_reg` and virtual-address transfer assumptions that are not valid for normal DMA front-ends.

## Test Signals

Signals include successful compile of front-end drivers against `struct esp_driver_ops`, host allocation with the expected command-private size, correct register access on 1-byte and wider register spacing front-ends, target counts within `ESP_MAX_TARGET`, tag allocation within `ESP_MAX_TAG`, SPI transport attributes reflecting negotiated width/period/offset, reset clearing state constants, and front-end conformance to the registration checklist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esp_scsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fcoe/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/fcoe/Makefile

## Purpose

`drivers/scsi/fcoe/Makefile` defines the kbuild object composition for the FCoE driver directory. It selects the standalone FCoE initiator object and the shared libfcoe object based on kernel configuration symbols.

## Important APIs, Types, and Functions

There are no C APIs or runtime functions. The build rules are the important interface:

- `obj-$(CONFIG_FCOE) += fcoe.o` builds the FCoE driver object when `CONFIG_FCOE` is enabled.
- `obj-$(CONFIG_LIBFCOE) += libfcoe.o` builds the shared FCoE library object when `CONFIG_LIBFCOE` is enabled.
- `libfcoe-objs := fcoe_ctlr.o fcoe_transport.o fcoe_sysfs.o` links the library from controller, transport, and sysfs support objects.

## Control Flow

Kbuild evaluates the `obj-*` variables during the kernel build. If the relevant config symbol is `y`, the object is built into vmlinux; if `m`, it is built as a module; if unset, it is omitted. `libfcoe.o` is not a source file, but a composite object linked from the three listed component objects.

## State and Persistence Behavior

The file has no runtime state and no persistence behavior. It controls which compiled objects exist and therefore which runtime FCoE code can be loaded or built in.

## Dependencies and Integration Points

The Makefile integrates with the SCSI/FCoE Kconfig symbols and kernel kbuild. `fcoe.o` depends on the source file that implements the FCoE initiator driver. `libfcoe.o` groups common library functionality used by FCoE code, including controller logic, transport glue, and sysfs exposure.

## Risks and Edge Cases

Build failures can occur if Kconfig allows `CONFIG_FCOE` without the necessary library dependencies or if source object names drift from the Makefile. Because `libfcoe.o` is composite, missing one component can remove controller, transport, or sysfs functionality from every user of the library. Module/built-in combinations must satisfy symbol visibility between `fcoe.o` and `libfcoe.o`.

## Test Signals

Validation is kbuild-oriented: build with FCoE disabled, with `CONFIG_LIBFCOE=m`, with `CONFIG_FCOE=m`, and with built-in variants; verify `libfcoe.o` contains `fcoe_ctlr.o`, `fcoe_transport.o`, and `fcoe_sysfs.o`; run `modpost` for unresolved symbols; and confirm the expected modules or built-in objects appear in the build output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fcoe/Makefile -->
