# Research: subset-b-005218

Work item covering the zfcp S/390 Fibre Channel Protocol driver files under `sources/distributed-fs/ceph-client/drivers/s390/scsi/`. Each file section is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_dbf.h -->
# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_dbf.h`

## Purpose

`zfcp_dbf.h` declares the zfcp debug-feature record layouts and small inline tracing classifiers used across the zfcp driver. It is the common schema for recovery, SAN, HBA, SCSI, and payload debug areas, and it supplies convenience wrappers that choose debug tags and levels for FSF and SCSI events. The file is hardware-driver observability infrastructure rather than core I/O logic, but it is deeply integrated with ERP, FSF request handling, FC ELS/CT handling, and SCSI completion/error paths.

## Important APIs, Types, And Data

- `ZFCP_DBF_TAG_LEN` fixes trace tags at seven bytes. All call sites pass short stable identifiers such as `fs_rerr`, `rsl_err`, or `erardy1`, so tag length is a compatibility constraint for trace tooling.
- `ZFCP_DBF_INVALID_WWPN` and `ZFCP_DBF_INVALID_LUN` provide sentinel values for trace records where a port or LUN is not applicable.
- `enum zfcp_dbf_pseudo_erp_act_type` adds pseudo ERP action ids for rport add/delete trace records, distinct from real `enum zfcp_erp_act_type`.
- `struct zfcp_dbf_rec_trigger`, `struct zfcp_dbf_rec_running`, and `struct zfcp_dbf_rec` define recovery trace records: requested versus required ERP action, queue depths, current FSF request id, action status, step, and per-target adapter/port/LUN status.
- `struct zfcp_dbf_san` records CT/ELS/SAN request/response metadata with request id, destination id, payload length, and a compact payload prefix.
- `struct zfcp_dbf_hba_res`, `struct zfcp_dbf_hba_uss`, `struct zfcp_dbf_hba_fces`, and `struct zfcp_dbf_hba` cover FSF responses, unsolicited status, bit-error payloads, and FC Endpoint Security changes.
- `struct zfcp_dbf_scsi` captures SCSI id/LUN, result, retry counters, FCP response info, command opcode, FSF request id, host-scribble request id, optional response payload, and high LUN bits.
- `struct zfcp_dbf_pay` is the unformatted payload trace record, capped by `ZFCP_DBF_PAY_MAX_REC`.
- `struct zfcp_dbf` owns debug area handles (`pay`, `rec`, `hba`, `san`, `scsi`), per-area spinlocks, and reusable preallocated record buffers.
- Inline APIs:
  - `zfcp_dbf_hba_fsf_resp_suppress()` identifies benign FCP residual-under responses with good SCSI status so default HBA tracing can be less noisy.
  - `zfcp_dbf_hba_fsf_resp()` checks debug level before calling the out-of-line formatter.
  - `zfcp_dbf_hba_fsf_response()` classifies FSF completions into request errors, protocol errors, FSF errors, open completions, QTCB log-bearing completions, or normal completions.
  - `_zfcp_dbf_scsi()`, `zfcp_dbf_scsi_result()`, `zfcp_dbf_scsi_fail_send()`, `zfcp_dbf_scsi_abort()`, `zfcp_dbf_scsi_devreset()`, and `zfcp_dbf_scsi_nullcmnd()` centralize SCSI trace level/tag choices.

## Control Flow And Integration

This header is included by FSF and FC paths to trace request submission and completion decisions. `zfcp_dbf_hba_fsf_response()` is called from `zfcp_fsf_protstatus_eval()` before FSF protocol status is interpreted. Its branching means high-severity request/protocol/FSF errors are visible at low debug levels, while normal traffic is usually level 6. SCSI wrappers are invoked from FCP completion, abort, and reset paths in the SCSI/FSF code so that SCSI mid-layer outcomes can be correlated with FSF request ids and FCP response data.

The record structures are packed because they are written into debugfs/s390 debug feature buffers as binary records. They mirror fields from `zfcp_def.h`, `zfcp_fsf.h`, libfc, and SCSI structures, so layout and width changes in any of those domains can affect trace compatibility.

## State And Persistence

The file itself has no persistent runtime state beyond the `struct zfcp_dbf` fields embedded in each adapter. Debug data persists only in kernel debug buffers for the lifetime of the adapter/debug area. Reusable record buffers in `struct zfcp_dbf` are protected by per-area spinlocks in the implementation. The inline functions read live adapter, SCSI, and FSF request state but do not mutate driver state except indirectly through out-of-line trace calls.

## Dependencies

The header depends on:

- Linux s390 debug feature types (`debug_info_t`) through the driver definitions.
- SCSI FCP definitions such as `struct fcp_resp_with_ext`, `FCP_RESID_UNDER`, `FCP_TMF_TGT_RESET`, and SCSI status constants.
- `zfcp_ext.h` declarations for the out-of-line debug functions.
- `zfcp_fsf.h` for FSF status, QTCB, and qualifier constants.
- `zfcp_def.h` for `struct zfcp_fsf_req`, `struct zfcp_adapter`, and status bits.

## Risks And Edge Cases

- Trace tag strings must fit `ZFCP_DBF_TAG_LEN`; longer tags will be truncated or overflow if callers mishandle fixed-size buffers.
- Packed binary record layouts are ABI-like for diagnostics. Adding fields or changing widths without trace decoder updates can break tooling.
- `zfcp_dbf_hba_fsf_resp_suppress()` assumes an IO QTCB with a valid FCP response when `qtcb_type == FSF_IO_COMMAND`; bad or corrupted QTCBs could make the classifier misleading.
- `_zfcp_dbf_scsi()` obtains the adapter from `scmd->device->host->hostdata[0]`; callers must pass a valid SCSI command with attached host data.
- The file intentionally suppresses common benign residual-under FSF errors at default levels, so tests or support procedures must know when to raise debug levels for full visibility.

## Test Signals

Useful validation signals include:

- FSF completion cases produce expected tags: `fs_rerr`, `fs_perr`, `fs_ferr`, `fs_open`, `fs_qtcb`, and `fs_norm`.
- FCP residual-under with SAM good is suppressed to level 5 while other FSF errors remain level 1.
- SCSI completion paths emit `rsl_err`, `rsl_ret`, or `rsl_nor` according to result/retry state.
- Target and LUN reset traces prefix tags with `tr_` or `lr_`.
- Debug buffers remain parseable after record changes and do not race under concurrent FSF/SCSI completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_dbf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_def.h -->
# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_def.h`

## Purpose

`zfcp_def.h` is the central data-model header for the zfcp driver. It defines shared status bits, ERP action types and steps, adapter/port/LUN state containers, latency accounting structures, and the base `struct zfcp_fsf_req` request object used to send commands to the FCP adapter. Most zfcp modules include it directly or indirectly, making it the primary contract between CCW/QDIO transport, FSF command handling, FC discovery, SCSI integration, diagnostics, sysfs, and ERP.

## Important APIs, Types, And Data

- Common status bits (`ZFCP_STATUS_COMMON_RUNNING`, `ERP_FAILED`, `UNBLOCKED`, `OPEN`, `ERP_INUSE`, `ACCESS_DENIED`, `ACCESS_BOXED`, `NOESC`) occupy the high 12 bits and are shared by adapter, port, and LUN-like objects.
- Adapter-only status bits track QDIO state, SIOSL logging, exchange-config success, host-connection initialization, pending ERP, link unplugged, and data-div support.
- Port-only status bits track physical-open state and active ADISC link tests.
- FSF-request status bits track request errors, cleanup ownership, abort outcome, task-management failure, dismissed requests, and incomplete exchange data.
- `enum zfcp_erp_act_type` defines LUN, port, forced-port, and adapter reopen actions. Values must fit into `u8` for debug record storage.
- `enum zfcp_erp_steps` records active ERP substeps: physical port closing, port closing/opening, and LUN closing/opening.
- `struct zfcp_erp_action` stores the queued/running recovery action, target object pointers, action status, current step, FSF request id, and timeout timer.
- `struct zfcp_adapter_mempool` groups mempools for ERP, GID_PN, SCSI, abort, status-read, status-read data pages, QTCBs, and FC requests.
- `struct zfcp_adapter` is the driver root object. It contains CCW/QDIO pointers, hardware feature data, SCSI host, port list and lock, request ids and request list, abort lock, status-read state, ERP queues/thread/wait queues, FC generic service ports, debug feature state, mempools, statistics buffers, work items, service level, event queue, scan throttling, diagnostics, and version-change work.
- `struct zfcp_port` represents a remote FC port and stores the device object, FC transport rport, adapter pointer, unit list, status, WWNN/WWPN/D_ID/handle, ERP action, capability/security fields, GID_PN/ADISC/rport work, and target id.
- `struct zfcp_unit` is the sysfs-configured LUN object; runtime I/O state lives in `struct zfcp_scsi_dev`.
- `struct zfcp_scsi_dev` is SCSI transport-private LUN state: status, FSF LUN handle, ERP action/counter, latency counters, and owning port.
- `sdev_to_zfcp()` returns the SCSI transport private zfcp LUN state.
- `zfcp_scsi_dev_lun()` converts a Linux SCSI LUN into the 64-bit FCP LUN encoding used in FSF commands.
- `struct zfcp_fsf_req` stores one FSF command/status-read request, including list node, request id, adapter, QDIO queue metadata, completion, status bits, QTCB pointer, private data, timer, ERP action, allocation pool, issue timestamp, and completion handler.
- `zfcp_adapter_multi_buffer_active()` and `zfcp_fsf_req_is_status_read_buffer()` are small state classifiers.

## Control Flow And Integration

This header does not implement flows directly, but it defines the state that all flows operate on. FSF request creation fills `struct zfcp_fsf_req` and embeds a `struct zfcp_qdio_req`; QDIO completion uses the request id to locate the request and calls the request handler. ERP queues and mutates `struct zfcp_erp_action` embedded in adapter, port, or SCSI-device state. FC discovery and link testing mutate `struct zfcp_port` D_ID, WWNN, capability, and security fields. The SCSI mid-layer reaches zfcp LUN state through `sdev_to_zfcp()`.

Status propagation is a key design point. ERP setter/clearer functions in `zfcp_erp.c` apply common status bits from adapter to ports and LUNs, and from ports to LUNs. This header's bit layout makes that possible with `ZFCP_COMMON_FLAGS`.

## State And Persistence

All structures are in-kernel runtime state tied to adapter probe/lifetime, port objects, SCSI devices, and outstanding FSF requests. Important persistent-in-memory state includes:

- Monotonic FSF request ids (`adapter->req_no`) and FSF sequence numbers.
- Adapter hardware/configuration data from exchange-config and exchange-port-data.
- Port discovery/cache data (`wwpn`, `wwnn`, `d_id`, `handle`, capability/security fields).
- LUN handles and latency counters.
- ERP counters and total/low-memory ERP counters.
- Debug, workqueue, and diagnostic pointers.

There is no on-disk persistence here; sysfs configuration and SCSI transport objects are managed by other modules.

## Dependencies

The header pulls in Linux block, delay, timer, slab, mempool, scatterlist, ioctl, SCSI core, SCSI transport FC/BSG, s390 CCW/debug/EBCDIC/sysinfo, and zfcp FSF/FC/QDIO headers. This makes it a high-fanout include; changes can trigger broad rebuilds and cross-module coupling.

## Risks And Edge Cases

- Status bit reuse is deliberate. New common bits must stay within `ZFCP_COMMON_FLAGS`, while object-specific bits must not collide semantically with shared high bits.
- `enum zfcp_erp_act_type` and `enum zfcp_erp_steps` have storage-size constraints because debug records store them as `u8`/`u16`.
- `sdev_to_zfcp()` assumes SCSI transport-private data was initialized; using it during early or torn-down states can dereference invalid memory.
- `zfcp_scsi_dev_lun()` casts a local `u64` as `struct scsi_lun`; any endianness or layout assumptions must match SCSI/FCP expectations.
- Request lifetime is subtle: asynchronous FSF requests with cleanup status may be freed on completion, so callers must obey the "do not touch after send" convention implemented in `zfcp_fsf.c`.

## Test Signals

Good tests and runtime signals include:

- Adapter, port, and LUN common status propagation matches parent changes.
- ERP action types and steps still decode correctly in debug traces.
- SCSI devices can round-trip through `sdev_to_zfcp()` and FCP LUN conversion.
- FSF request ids remain unique and request-list lookup/removal works under completion races.
- Multi-buffer status toggles correctly when QDIO open detects hardware capability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_diag.c -->
# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_diag.c`

## Purpose

`zfcp_diag.c` implements adapter diagnostic-buffer storage and refresh logic. It caches exchange-port-data and exchange-config-data QTCB bottoms behind small headers, rate-limits refreshes by age, serializes concurrent refresh attempts, and exposes synchronous update functions used by sysfs/diagnostic consumers. The actual data acquisition is delegated to FSF exchange commands; this file owns cache lifecycle and concurrency.

## Important APIs And Functions

- `zfcp_diag_adapter_setup()` allocates `struct zfcp_diag_adapter`, initializes the port/config diagnostic headers, points headers at embedded data buffers, sets buffer sizes, initializes spinlocks, and seeds timestamps so the first freshness check fails.
- `zfcp_diag_adapter_free()` frees the adapter diagnostics block and nulls the adapter pointer.
- `zfcp_diag_update_xdata()` publishes newly captured data into a diagnostic buffer under `access_lock`, records timestamp and incomplete flag, and refuses to move timestamps backward.
- `zfcp_diag_update_port_data_buffer()` synchronously runs `zfcp_fsf_exchange_port_data_sync()` and treats `-EAGAIN` as success with incomplete data already recorded in the header.
- `zfcp_diag_update_config_data_buffer()` is the config-data counterpart using `zfcp_fsf_exchange_config_data_sync()`.
- `__zfcp_diag_update_buffer()` is the serialization helper. If another caller is updating, it performs an interruptible wait under the lock; otherwise it marks `updating`, drops the lock for the sleeping update function, reacquires, clears `updating`, and wakes waiters.
- `__zfcp_diag_test_buffer_age_isfresh()` checks for future timestamps and max-age expiration.
- `zfcp_diag_update_buffer_limited()` loops until the buffer is fresh enough or the current caller performed an update. It returns `0`, `-EINTR`, or the underlying update error.

## Control Flow

A diagnostic reader calls `zfcp_diag_update_buffer_limited(adapter, hdr, update_fn)`. The function locks the header, checks whether cached data is fresh relative to `adapter->diagnostics->max_age`, and either returns quickly or enters update serialization. Only one caller executes the supplied update function. Other callers sleep on the global `__zfcp_diag_publish_wait` wait queue and retry freshness when the active updater finishes. FSF completion handlers publish new QTCB-bottom data via `zfcp_diag_update_xdata()`, including the incomplete flag for link-down/incomplete exchange data.

`zfcp_diag_update_xdata()` captures `jiffies` before locking so the timestamp reflects acquisition time. It only writes when the captured timestamp is not older than the existing one, preventing older concurrent results from replacing newer data.

## State And Persistence

State is per adapter in `adapter->diagnostics`:

- `max_age` defaults to 5000 ms.
- Each diagnostic buffer has `access_lock`, `updating`, `incomplete`, `timestamp`, `buffer`, and `buffer_size`.
- Port and config data are embedded in the diagnostics allocation, so there is one stable cache address for each.

The global wait queue is shared across all diagnostic headers and adapters. It does not store data; it coordinates waiters.

## Dependencies And Integration

The file depends on Linux spinlocks, jiffies, errno, slab allocation, and zfcp FSF exchange APIs. It integrates with:

- `zfcp_fsf_exchange_config_data_handler()` and `zfcp_fsf_exchange_port_data_handler()`, which publish data into these buffers.
- SCSI host update code, because exchange handlers may update SCSI host state while also updating diagnostics.
- Sysfs or other diagnostic consumers that need fresh but rate-limited hardware data.

## Risks And Edge Cases

- `zfcp_diag_adapter_setup()` overwrites `adapter->diagnostics` only after allocation succeeds, but callers must avoid double setup leaks or concurrent readers during replacement.
- `__zfcp_diag_publish_wait` is global; wakeups are broad. Correctness relies on rechecking each header's `updating` and freshness state under its own lock.
- Waiters receive `-EAGAIN` when another thread completed an update; `zfcp_diag_update_buffer_limited()` intentionally loops to recheck freshness. Incorrect callers of the internal helper would misinterpret it.
- Update functions sleep, so the lock must be dropped. Any new update function must publish through the expected FSF handler path or directly call `zfcp_diag_update_xdata()`.
- Freshness uses jiffies; wraparound is handled through time macros, but future timestamps are treated as stale.

## Test Signals

Validation should cover:

- First update is forced after setup because timestamps are seeded old.
- Concurrent callers result in one FSF exchange and waiters either return fresh data or `-EINTR` if interrupted.
- Incomplete FSF exchange data maps to `hdr->incomplete` with a `0` public diagnostic update return.
- Older concurrent publish attempts do not overwrite newer timestamps/data.
- Freeing diagnostics nulls `adapter->diagnostics` and tolerates partial setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_diag.h -->
# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_diag.h`

## Purpose

`zfcp_diag.h` declares the diagnostic cache structures and public diagnostic update API for the zfcp driver. It defines the common metadata header used to protect and age diagnostic buffers, the adapter-level container for exchange-port/config data, and a feature predicate for SFP reporting support.

## Important APIs, Types, And Data

- `struct zfcp_diag_header` is the common diagnostic-buffer header:
  - `access_lock` protects all metadata and buffer contents.
  - Bitfields `updating` and `incomplete` track an active producer and partial data.
  - `timestamp` stores the last capture time in jiffies.
  - `buffer` and `buffer_size` point to the implementation-specific payload.
- `struct zfcp_diag_adapter` stores:
  - `max_age`, the freshness window in milliseconds.
  - `port_data.header` plus cached `struct fsf_qtcb_bottom_port`.
  - `config_data.header` plus cached `struct fsf_qtcb_bottom_config`.
- `zfcp_diag_adapter_setup()` and `zfcp_diag_adapter_free()` manage per-adapter diagnostic storage.
- `zfcp_diag_update_xdata()` publishes a diagnostic payload into a header.
- `typedef zfcp_diag_update_buffer_func` defines the synchronous refresh callback shape.
- `zfcp_diag_update_config_data_buffer()` and `zfcp_diag_update_port_data_buffer()` are concrete refresh callbacks.
- `zfcp_diag_update_buffer_limited()` is the public rate-limited refresh coordinator.
- `zfcp_diag_support_sfp()` returns true when `adapter->adapter_features` includes `FSF_FEATURE_REPORT_SFP_DATA`.

## Control Flow And Integration

Consumers use the header in two layers. General code calls the rate-limited update coordinator with one of the concrete update callbacks. FSF exchange handlers use `zfcp_diag_update_xdata()` to publish returned QTCB-bottom data. The cached buffers are the same FSF data structures used by SCSI host update and sysfs diagnostics, so this header is a bridge between hardware exchange commands and user-visible diagnostic attributes.

## State And Persistence

The header describes per-adapter in-memory caches only. The buffer pointer points at embedded storage in `struct zfcp_diag_adapter`; it is not separately allocated. The incomplete flag persists until a later successful publish updates the header. `max_age` persists for the adapter lifetime and can be used by all diagnostic readers.

## Dependencies

The header includes Linux spinlocks, `zfcp_fsf.h` for QTCB-bottom and feature constants, and `zfcp_def.h` for the adapter declaration. Because `zfcp_def.h` also contains a diagnostics pointer, include-order coupling matters.

## Risks And Edge Cases

- `updating` and `incomplete` are `u64` bitfields. Code must mutate them under `access_lock`; bitfield layout should not be exposed externally.
- `buffer` is a raw `void *`; publishers must provide data matching `buffer_size` and the intended payload type.
- `zfcp_diag_support_sfp()` depends on adapter features already being populated by exchange-config-data.
- Adding new diagnostic buffers should follow the same embedded-data plus header pattern to avoid lifetime mismatches.

## Test Signals

Look for:

- Correct header initialization for both config and port buffers.
- SFP sysfs/reporting paths disabled until `FSF_FEATURE_REPORT_SFP_DATA` appears.
- Diagnostic readers hold or coordinate on `access_lock` while copying data.
- Incomplete flag is visible after incomplete exchange data and clears after complete data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_erp.c -->
# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_erp.c`

## Purpose

`zfcp_erp.c` implements zfcp Error Recovery Procedures. It is the recovery state machine for adapters, FC ports, and LUNs. It blocks targets, chooses the minimal required recovery severity, queues one embedded ERP action per target, drives FSF close/open/exchange commands, handles timeouts and low-memory retries, propagates common status bits, and re-enables SCSI transport objects after successful recovery.

## Important APIs And Functions

- Public recovery entry points:
  - `zfcp_erp_adapter_reopen()`, `zfcp_erp_adapter_shutdown()`, and `zfcp_erp_adapter_reset_sync()`.
  - `zfcp_erp_port_reopen()`, `zfcp_erp_port_forced_reopen()`, `zfcp_erp_port_shutdown()`, and `zfcp_erp_port_forced_reopen_all()`.
  - `zfcp_erp_lun_reopen()`, `zfcp_erp_lun_shutdown()`, and `zfcp_erp_lun_shutdown_wait()`.
  - `zfcp_erp_port_forced_no_port_dbf()` records recovery need when no `zfcp_port` object exists.
- ERP queue/thread APIs:
  - `zfcp_erp_thread_setup()`, `zfcp_erp_thread_kill()`, and `zfcp_erp_wait()`.
  - `zfcp_erp_notify()` moves a running action back to ready after FSF completion or timeout.
  - `zfcp_erp_timeout_handler()` is used by ERP-owned FSF request timers.
- Status APIs:
  - `zfcp_erp_set_adapter_status()` / `clear_adapter_status()` propagate common bits to ports and SCSI devices.
  - `zfcp_erp_set_port_status()` / `clear_port_status()` propagate common bits to child SCSI devices.
  - `zfcp_erp_set_lun_status()` / `clear_lun_status()` mutate per-SCSI-device zfcp status.
- Core selection/setup:
  - `zfcp_erp_required_act()` escalates requested LUN/port actions to a parent action when parent state is blocked.
  - `zfcp_erp_handle_failed()` suppresses new recovery for targets already marked ERP failed.
  - `zfcp_erp_setup_act()` takes object references, marks `ERP_INUSE`, initializes the embedded action, and notes close-only mode when target is not running.
  - `zfcp_erp_action_enqueue()` inserts into `erp_ready_head`, sets adapter pending status, and emits recovery trigger traces.
- Strategy functions:
  - Adapter strategy closes QDIO/requests/WKA ports, opens QDIO, exchanges config and port data, registers SCSI host, resizes status-read pools, posts status reads, and schedules port scans/name updates.
  - Port strategy closes/open ports, triggers GID_PN lookup when D_ID is missing, handles point-to-point peer ports, and can force physical close.
  - LUN strategy closes/open LUNs and clears access-denied status before reopen.

## Control Flow

Recovery starts when another subsystem detects a fault and calls a public reopen/shutdown entry. The target is blocked by clearing `UNBLOCKED` and optional clear masks, SCSI rports are scheduled blocked for adapter/port faults, and a queued ERP action is created under `adapter->erp_lock`. The ERP thread waits on `erp_ready_wq`, picks the first ready action, and calls `zfcp_erp_strategy()`.

`zfcp_erp_strategy()` first reconciles outstanding FSF request state with `zfcp_erp_strategy_check_fsfreq()`. If dismissed or timed out, it exits or fails. Otherwise it moves the action to the running list and calls the type-specific strategy without holding the ERP lock. Type-specific strategies typically issue one asynchronous FSF command and return `ZFCP_ERP_CONTINUES`; the FSF handler later calls `zfcp_erp_notify()`, which moves the action back to the ready queue. When a strategy returns final success/failure/exit, the result is checked against target counters, state-change races, and follow-up rules. Success at adapter level schedules port recovery; success at port level schedules child LUN recovery.

Adapter reopen has the richest flow: close existing queues if open, dismiss all outstanding FSF requests, reset sequence number, force WKA ports offline, open QDIO, exchange config data with retries for host-connection-initializing, optionally exchange port data, register/update the SCSI host, set up point-to-point port, resize status-read pools, refill status reads, and mark adapter open/unblocked.

## State And Persistence

ERP uses persistent in-memory state embedded in adapter/port/SCSI-device objects:

- One `struct zfcp_erp_action` per adapter, port, and SCSI device.
- `erp_ready_head` and `erp_running_head` lists per adapter.
- Wait queues for ready actions and overall ERP completion.
- Status bits for running/open/unblocked/failed/in-use/access states.
- Retry counters per adapter/port/LUN, capped by `ZFCP_MAX_ERPS`.
- `erp_total_count` and `erp_low_mem_count` to detect all-active low-memory stalls.
- FSF request id in the ERP action to reconcile outstanding asynchronous commands.

References are held for adapters (`kref_get`), ports (`get_device`), and SCSI devices (`scsi_device_get`) while actions are active, except the explicit no-reference shutdown-wait path.

## Dependencies And Integration

ERP depends on FSF command APIs for all hardware recovery operations, QDIO close/open, request-list lookup for outstanding FSF requests, diagnostic cache data for delayed SCSI host updates, FC port discovery/link scan/name update logic, SCSI rport block/register scheduling, service-level registration, mempool resizing, kernel threads, timers, wait queues, and debug tracing.

ERP is the integration point for errors reported by QDIO, FSF status/protocol evaluation, FC link events, SCSI error handling, sysfs removal, and adapter teardown.

## Risks And Edge Cases

- Locking is delicate: `erp_lock`, `port_list_lock`, `host_lock`, request-list lock, and FSF timers interact. New code must not sleep while holding spin/rw locks except through the established wait macros that release locks.
- Embedded action objects mean only one ERP action per target can be active; overlapping child actions are dismissed when parent recovery starts.
- FSF request pointers can complete concurrently. ERP stores only request ids and uses request-list locking to avoid use-after-free.
- Low-memory handling can escalate to adapter reopen if all actions are stuck in low-memory state.
- `zfcp_erp_lun_shutdown_wait()` intentionally skips `scsi_device_get()`; correctness depends on waiting for ERP completion before the SCSI device disappears.
- State-change detection can enqueue new actions if running/close-only intent changed while an action was executing.
- Adapter exchange-config incomplete data intentionally avoids full shutdown so link-up events can still be recognized.

## Test Signals

Key signals include:

- Requested recovery escalates correctly: LUN recovery to port/adapter when parents are blocked, forced port close before normal port open, adapter recovery dismissing children.
- ERP action lists transition ready -> running -> ready/final without leaks, and `ZFCP_STATUS_ADAPTER_ERP_PENDING` clears when both lists are empty.
- FSF timeout marks action timed out and leads to request dismissal/recovery retry.
- After more than `ZFCP_MAX_ERPS` failures, adapter/port/LUN is marked `ERP_FAILED` and remains blocked.
- Successful adapter recovery reopens QDIO, posts status reads, registers service level, schedules port scan, and updates symbolic name.
- Successful port/LUN recovery unblocks rport only after non-failed child LUNs are unblocked and no newer ERP is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_erp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_ext.h -->
# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_ext.h`

## Purpose

`zfcp_ext.h` is the external declaration hub for the zfcp driver. It declares cross-file functions, global driver objects, cache pointers, templates, and sysfs attribute groups. It does not implement behavior, but it documents module boundaries and the major integration surface between adapter/CCW setup, debug tracing, ERP, FC services, FSF commands, QDIO transport, SCSI integration, sysfs, and unit management.

## Important APIs And Integration Points

- `zfcp_aux.c`: adapter/port allocation and lookup, adapter release/unregister.
- `zfcp_ccw.c`: CCW driver object and adapter lookup/reference helpers.
- `zfcp_dbf.c`: debug feature registration/unregistration and trace emitters for recovery, HBA, SAN, and SCSI events.
- `zfcp_erp.c`: all public recovery entry points, ERP thread lifecycle, wait/notify, timeout handler, status propagation, and synchronous adapter reset.
- `zfcp_fc.c`: FC event queueing/posting, port scan, incoming ELS handling, D_ID lookup, PLOGI evaluation, ADISC link tests, WKA GS setup/destruction, BSG CT/ELS execution, symbolic name update, and scan throttling helpers.
- `zfcp_fsf.c`: QTCB cache, FSF open/close/exchange/status-read/SCSI/abort/task-management commands, request cleanup, FC host link-down update, request-id completion, and FC security formatting.
- `zfcp_qdio.c`: QDIO setup/open/close/destroy, SBAL acquisition/send, scatterlist-to-SBAL mapping, SCSI host queue-limit update, and SIOSL logging.
- `zfcp_scsi.c`: transport template, adapter registration, rport work, rport block/register scheduling, DIF/DIX helpers, and SCSI host update callbacks.
- `zfcp_sysfs.c`: sysfs attribute groups and port-removal predicate.
- `zfcp_unit.c`: unit add/remove/find, SCSI-device lookup, SCSI scan queueing, and unit status.

## Control Flow Implications

The declarations reveal the main driver flow:

1. CCW/aux code creates an adapter and sets up debug, QDIO, diagnostics, FC GS, SCSI transport, and ERP.
2. ERP drives QDIO open and FSF exchange-config/port-data.
3. FSF/QDIO handle hardware request submission and completion.
4. FC code manages discovery, WKA name-server ports, CT/ELS traffic, and BSG passthrough.
5. SCSI code registers hosts, rports, and devices, then sends commands through FSF.
6. Debug, sysfs, and diagnostics observe and expose internal state.

## State And Persistence

The header exposes global runtime objects (`zfcp_ccw_driver`, `zfcp_fc_req_cache`, `zfcp_fsf_qtcb_cache`, `zfcp_scsi_transport_template`, `zfcp_transport_functions`, `zfcp_experimental_dix`, sysfs groups, and `zfcp_sysfs_port_units_mutex`). Persistent state itself lives in the modules and structures declared elsewhere. Because this header is included widely, it is a stable in-driver ABI for symbol names and signatures.

## Dependencies

It includes Linux types/sysfs, FC ELS definitions, and `zfcp_def.h`/`zfcp_fc.h`. That creates circular-seeming but guarded include relationships with the central zfcp headers. The header depends on many forward-declared kernel types from included headers: `ccw_device`, `ccw_driver`, `bsg_job`, `scsi_device`, `scsi_cmnd`, `fc_function_template`, and FSF QTCB structures.

## Risks And Edge Cases

- This file has high fanout. Signature changes must be applied consistently across many modules.
- It exposes internal globals and implementation functions, so adding declarations can increase coupling rather than preserving module boundaries.
- The include of `zfcp_def.h` means many declarations rely on full structure definitions rather than forward declarations, increasing compile coupling.
- Some APIs have strict context expectations not visible from the signature, such as QDIO request-lock requirements, FSF async lifetime rules, and ERP lock requirements.

## Test Signals

Build-time validation is the primary signal: all declarations must match definitions across modules. Runtime integration tests should exercise adapter probe/remove, ERP recovery, FC scans, BSG CT/ELS jobs, SCSI command/abort/TMF paths, sysfs add/remove, and diagnostics to catch cross-module signature or lifetime drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_ext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_fc.c -->
# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_fc.c`

## Purpose

`zfcp_fc.c` implements Fibre Channel service logic above FSF transport: FC event posting, name-server CT requests, incoming ELS handling, remote-port discovery and validation, ADISC link tests, WKA generic-service port lifecycle, symbolic port-name synchronization, and FC BSG CT/ELS passthrough. It bridges the zfcp hardware command layer with Linux FC transport semantics.

## Important APIs And Functions

- Module parameters:
  - `no_auto_port_rescan` disables automatic port rescans unless inverse conditional scan is requested.
  - `port_scan_backoff` and `port_scan_ratelimit` throttle and jitter port scanning.
- Port scan helpers:
  - `zfcp_fc_port_scan_backoff()`, `zfcp_fc_conditional_port_scan()`, and `zfcp_fc_inverse_conditional_port_scan()`.
  - `zfcp_fc_scan_ports()` sends GPN_FT through the directory service WKA port and attaches/removes ports.
- FC event handling:
  - `zfcp_fc_enqueue_event()` allocates an event in IRQ context and queues work.
  - `zfcp_fc_post_event()` posts queued events via `fc_host_post_event()`.
- WKA port lifecycle:
  - `zfcp_fc_wka_port_get()` opens a WKA port on demand and increments refcount.
  - `zfcp_fc_wka_port_put()` schedules delayed close after refcount drops to zero.
  - `zfcp_fc_wka_port_offline()` sends close-port after a short idle delay.
  - `zfcp_fc_wka_ports_force_offline()`, `zfcp_fc_gs_setup()`, and `zfcp_fc_gs_destroy()` initialize/tear down generic-service WKA ports.
- Incoming ELS:
  - `zfcp_fc_incoming_els()` traces ELS and dispatches PLOGI, LOGO, and RSCN.
  - RSCN handling tests matching known ports and triggers scans; PLOGI/LOGO force reopen by WWPN.
- Name-server lookup:
  - `zfcp_fc_ns_gid_pn_request()` sends GID_PN for a port's WWPN.
  - `zfcp_fc_port_did_lookup()` runs in workqueue, updates D_ID, and reopens or fails the port.
  - `zfcp_fc_trigger_did_lookup()` queues that work with a port device reference.
- Link test:
  - `zfcp_fc_test_link()` queues `zfcp_fc_link_test_work()`.
  - `zfcp_fc_adisc()` sends ADISC to cached D_ID and clears D_ID before send to force fresh lookup on failure.
  - `zfcp_fc_adisc_handler()` validates WWPN/open state and triggers forced or normal port recovery as needed.
- Discovery:
  - `zfcp_fc_eval_gpn_ft()` parses GPN_FT response pages, skips WKA/local ports, enqueues new ports, reopens them, waits for ERP, and unregisters invalid no-escape ports.
- Symbolic name:
  - `zfcp_fc_sym_name_update()` reads current symbolic name with GSPN_ID and, in NPIV mode, writes a Linux-specific name with RSPN_ID.
- BSG:
  - `zfcp_fc_exec_bsg_job()` dispatches FC_BSG ELS/CT jobs.
  - `zfcp_fc_exec_els_job()` resolves rport or host D_ID and sends ELS.
  - `zfcp_fc_exec_ct_job()` opens the proper WKA port and sends CT.
  - `zfcp_fc_timeout_bsg_job()` returns `-EAGAIN` because hardware timeout tracking owns the timeout.

## Control Flow

Adapter recovery schedules scans and name updates after a successful open. Port scanning first rate-limits the next scan time, opens the directory-service WKA port, allocates SG pages for GPN_FT, retries transient name-server rejections, evaluates returned ports, and releases the WKA port. New ports are marked `NOESC` while being validated; ports still no-escape and without class/unit evidence after the scan are moved to a remove list, shut down, and unregistered.

Incoming ELS from FSF status-read buffers can trigger targeted recovery. RSCN maps FC address-format ranges to masks and ADISC-tests matching known ports; broad RSCNs also retry failed ports with missing D_ID and schedule a scan. PLOGI/LOGO find by WWPN and force reopen.

WKA ports are demand-opened with a mutex-protected state machine (`OFFLINE`, `OPENING`, `ONLINE`, `CLOSING`) and wait queues for open/close completion signaled by FSF handlers. Refcounting keeps WKA ports open across CT users; delayed close avoids churn.

## State And Persistence

Persistent runtime state includes adapter scan throttle (`next_port_scan`), `adapter->events` list and lock, WKA port state/refcount/handle/work, port D_ID/WWNN/capability fields, and work items for GID_PN/ADISC/rport. FC request objects are allocated from `zfcp_fc_req_cache` or mempools and may be freed in async handlers.

## Dependencies And Integration

The file depends on Linux workqueues, kmem cache, random backoff, BSG, libfc/FC ELS/NS structures, SCSI FC transport, FSF CT/ELS APIs, ERP recovery APIs, zfcp debug tracing, and adapter workqueue infrastructure. It is called by FSF status-read handling for incoming ELS and by ERP after adapter recovery.

## Risks And Edge Cases

- D_ID caching is inherently racy. ADISC clears `port->d_id` before sending to force lookup if the port changes, but comments note open-port response data can be stale.
- WKA open/close waits depend on FSF handlers always waking the proper wait queue.
- Event allocation uses `GFP_ATOMIC`; allocation failure silently drops FC events.
- GPN_FT response parsing spans chained SG pages; page/entry arithmetic must stay aligned with `ZFCP_FC_GPN_FT_ENT_PAGE`.
- `zfcp_fc_sg_setup_table()` error cleanup passes the current SG pointer with count of already allocated entries; changes here need careful leak testing.
- BSG job timeout units are converted with `job->timeout / HZ`; very small timeouts could become zero.
- `zfcp_fc_job_wka_port()` returns NULL for unsupported CT GS types; callers must not put a NULL WKA port.

## Test Signals

Useful signals include:

- Port scan attaches new non-local, non-WKA FCP ports and unregisters stale no-escape ports.
- RSCN/PLOGI/LOGO incoming ELS paths trigger ADISC, forced reopen, or rescan as expected.
- WKA port refcount opens once for concurrent users and closes after the delayed idle path.
- GID_PN lookup sets D_ID and reopens the target port, or marks it ERP failed if no D_ID is found.
- BSG CT jobs release WKA refs on completion and ELS jobs choose rport D_ID or host-request D_ID correctly.
- NPIV symbolic name update reads GSPN, appends device/node information, and sends RSPN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_fc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_fc.h -->
# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_fc.h`

## Purpose

`zfcp_fc.h` declares Fibre Channel helper structures and inline FCP command/response conversion routines for zfcp. It defines CT/ELS request containers, GPN_FT sizing constants, WKA port state, FC event queue infrastructure, and the logic that maps Linux SCSI commands to FCP command IUs and FCP responses back to SCSI result/sense/residual state.

## Important APIs, Types, And Data

- GPN_FT constants compute CT response capacity:
  - `ZFCP_FC_CT_SIZE_PAGE`, `ZFCP_FC_GPN_FT_ENT_PAGE`, `ZFCP_FC_GPN_FT_NUM_BUFS`, `ZFCP_FC_GPN_FT_MAX_SIZE`, and `ZFCP_FC_GPN_FT_MAX_ENT`.
- `ZFCP_FC_CTELS_TMO` defines default CT/ELS timeout from FC R_A_TOV.
- `struct zfcp_fc_event` and `struct zfcp_fc_events` queue FC HBAAPI events from IRQ context to workqueue context.
- CT request/response containers: `zfcp_fc_gid_pn_req/rsp`, `zfcp_fc_gpn_ft_req`, `zfcp_fc_gspn_req/rsp`, and `zfcp_fc_rspn_req`.
- `struct zfcp_fc_req` is the internal FC request envelope containing `struct zfcp_fsf_ct_els`, request/response SG entries, and a union of embedded payloads for ADISC, GID_PN, GPN_FT, GSPN, and RSPN.
- `enum zfcp_fc_wka_status` and `struct zfcp_fc_wka_port` model WKA generic-service ports with open/close wait queues, state, refcount, D_ID, FSF handle, mutex, and delayed close work.
- `struct zfcp_fc_wka_ports` groups management, time, directory, and alias service WKA ports.
- Inline helpers:
  - `zfcp_fc_scsi_to_fcp()` fills an FCP command IU from `struct scsi_cmnd`, including LUN, task attribute, data direction, CDB, transfer length, and DIF Type 1 protection overhead.
  - `zfcp_fc_fcp_tm()` creates an FCP task-management command for a SCSI device and TM flag.
  - `zfcp_fc_eval_fcp_rsp()` evaluates an FCP response IU into SCSI result, sense buffer, residual count, and host-byte errors.

## Control Flow And Integration

FSF SCSI command setup calls `zfcp_fc_scsi_to_fcp()` before queueing an FSF FCP command. FSF task-management setup calls `zfcp_fc_fcp_tm()`. FSF FCP completion calls `zfcp_fc_eval_fcp_rsp()` after basic FSF status handling to translate remote SCSI/FCP response semantics into the Linux SCSI command. `struct zfcp_fc_req` is used by `zfcp_fc.c` when sending internal CT/ELS commands through `zfcp_fsf_send_ct()` and `zfcp_fsf_send_els()`.

## State And Persistence

Most structures are short-lived request or event containers. WKA port objects persist per adapter in `adapter->gs`. The inline FCP response evaluator mutates the live `struct scsi_cmnd`: `result`, sense buffer, and residual.

## Dependencies

The header depends on FC ELS/FCP/NS definitions, SCSI command and tagged command headers, and zfcp FSF CT/ELS structures. It also assumes SCSI protection helpers such as `scsi_get_prot_type()`, `scsi_bufflen()`, and `scsi_set_resid()`.

## Risks And Edge Cases

- `zfcp_fc_scsi_to_fcp()` copies `scsi->cmd_len` bytes into `fc_cdb`; callers must ensure the CDB length fits the FCP command IU.
- DIF Type 1 length adjustment assumes 8 protection bytes per logical block and uses `sector_size`; invalid sector size would corrupt FCP_DL.
- `zfcp_fc_eval_fcp_rsp()` treats non-`FCP_TMF_CMPL` response-info codes as `DID_ERROR` and returns before sense/residual evaluation.
- Sense data pointer arithmetic depends on whether response-info length is present and on big-endian length fields.
- Residual-under with good SCSI status is promoted to `DID_ERROR` when transferred bytes are below `underflow` and no sense data is present.

## Test Signals

Coverage should verify:

- FCP command IUs contain correct LUN encoding, read/write flags, CDB, FCP_DL, and protection-adjusted length.
- Task-management IUs set only LUN and TM flags needed by FSF.
- FCP response evaluation copies bounded sense data, handles TMF completion/failure, sets residual underflow, and flags residual overrun errors.
- GPN_FT sizing constants match page-sized SG response allocation and parsing in `zfcp_fc.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_fc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_fsf.c -->
# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_fsf.c`

## Purpose

`zfcp_fsf.c` implements Fibre Channel Support Function command handling for zfcp. It creates, queues, completes, and frees FSF requests; interprets FSF protocol/status responses; handles unsolicited status-read events; implements adapter/port/LUN open/close/exchange commands for ERP; sends CT/ELS commands for FC services and BSG; sends SCSI FCP commands, aborts, and task-management commands; and ties request completion back into QDIO, ERP, diagnostics, debug tracing, and SCSI completion.

## Important APIs And Functions

- Request lifetime:
  - `zfcp_fsf_req_create()` allocates `struct zfcp_fsf_req` and QTCB, initializes request id/sequence/type/header, and starts QDIO request layout.
  - `zfcp_fsf_req_send()` adds to `adapter->req_list`, timestamps, queues through QDIO, increments sequence/request ids, and enforces the async "do not touch after send" rule.
  - `zfcp_fsf_req_complete()` handles status-read special cases, deletes timers, evaluates protocol/FSF status, invokes the command handler, notifies ERP, and either frees or completes the request.
  - `zfcp_fsf_req_free()` releases request/QTCB memory via mempool or kmem cache.
  - `zfcp_fsf_req_dismiss_all()` dismisses all outstanding requests after QDIO shutdown.
  - `zfcp_fsf_reqid_check()` maps returned response SBAL request ids to requests and panics on unknown ids.
- Status-read:
  - `zfcp_fsf_status_read()` posts an unsolicited status-read buffer.
  - `zfcp_fsf_status_read_handler()` handles port-closed, incoming ELS, bit-error threshold, link down/up, notification lost, feature update alert, and version change, then refills status-read work.
  - `zfcp_fsf_fc_host_link_down()` resets FC host/link metadata.
- Status evaluation:
  - `zfcp_fsf_protstatus_eval()` handles QTCB version, sequence, duplicate id, link down, queue reestablish, and unsupported protocol statuses.
  - `zfcp_fsf_fsfstatus_eval()` and `zfcp_fsf_fsfstatus_qual_eval()` interpret high-level FSF statuses and recommendations.
  - `zfcp_fsf_link_down_info_eval()` logs link-down reasons, blocks rports, clears FC host data, and marks adapter failed.
- Exchange commands:
  - `zfcp_fsf_exchange_config_data()` / `_sync()` and handler update adapter features, topology, diagnostic config data, SCSI host data, QTCB version compatibility, and link-down incomplete state.
  - `zfcp_fsf_exchange_port_data()` / `_sync()` and handler update diagnostic port data, SCSI host port data, and FC Endpoint Security algorithms.
- CT/ELS:
  - `zfcp_fsf_send_ct()` and `zfcp_fsf_send_els()` build request/response SBALs, start timers, trace SAN payloads, and call CT/ELS completion handlers.
  - `zfcp_fsf_setup_ct_els_sbals()` supports unchained, chained, and multi-buffer data-router layouts.
- Open/close:
  - `zfcp_fsf_open_port()`, `close_port()`, `close_physical_port()`, `open_lun()`, and `close_lun()` are ERP-owned async commands with handlers that mutate port/LUN handles and status.
  - `zfcp_fsf_open_wka_port()` and `close_wka_port()` support FC generic-service WKA port lifecycle and wake WKA wait queues.
- SCSI I/O and error handling:
  - `zfcp_fsf_fcp_cmnd()` creates and sends FCP I/O commands from `struct scsi_cmnd`, including DIF/DIX protection SGs.
  - `zfcp_fsf_fcp_cmnd_handler()` evaluates FSF/FCP status, sets SCSI result/sense/errors, records latency and blktrace data, emits SCSI debug, clears host_scribble, and calls `scsi_done()`.
  - `zfcp_fsf_abort_fcp_cmnd()` sends abort for an old FSF request id from `host_scribble`.
  - `zfcp_fsf_fcp_task_mgmt()` sends TMF commands and `zfcp_fsf_fcp_task_mgmt_handler()` marks TM failure.
- Miscellaneous:
  - `zfcp_fsf_convert_portspeed()` maps FSF speed bits to FC transport speed bits.
  - `zfcp_fsf_scnprint_fc_security()` formats FC Endpoint Security flags.

## Control Flow

All active FSF commands follow a common pattern: lock QDIO request queue, wait for/free an SBAL, create request/QTCB, fill command-specific QTCB bottom and SBAL entries, set a handler/timer/status bits, send through QDIO, and then never dereference async requests after send. QDIO response interrupts call `zfcp_fsf_reqid_check()`, which removes each request from `adapter->req_list` and completes it. Completion first classifies transport/protocol status, then command-specific FSF status, then calls the handler. ERP-owned requests notify their ERP action so the ERP thread can continue.

Status-read buffers are special requests with no QTCB. They return unsolicited events from firmware and are freed/refilled continuously. Link and notification events often trigger FC event posting, port scans, rport blocking, adapter reopen, or version-change work.

SCSI commands are asynchronous cleanup requests. On completion, the handler holds `adapter->abort_lock` until after `scsi_done()` to prevent abort/completion races. For synchronous exchange commands, the caller waits on `req->completion`, checks request status, then frees the request.

## State And Persistence

FSF persists state in adapter fields (`req_no`, `fsf_req_seq_no`, feature flags, hardware versions, topology/peer info, status-read counters, FC security algorithms), port fields (handles, open/physical-open/access/security state), SCSI-device fields (LUN handle, latency counters), request-list membership, and diagnostic buffers. Request objects themselves are temporary but their ids are used as the durable correlation token between QDIO SBALs, SCSI `host_scribble`, ERP action `fsf_req_id`, and debug traces.

## Dependencies And Integration

The file integrates with QDIO for queueing/SBAL layout, ERP for recovery and timers, zfcp request list for completion lookup, FC for CT/ELS and incoming ELS handling, diagnostics for xconfig/xport caches, SCSI transport for host/rport/link updates, SCSI mid-layer for command completion, block layer for blktrace driver data, and debug feature tracing for HBA/SAN/SCSI records.

## Risks And Edge Cases

- Unknown request ids in `zfcp_fsf_reqid_check()` trigger a kernel panic because they imply possible memory corruption.
- Request lifetime is highly race-sensitive. Async requests may complete and be freed immediately after QDIO submission; code after send must not touch them.
- `zfcp_fsf_req_send()` removes requests on QDIO send failure by id and logs if already gone; this protects against unexpected list races.
- Incomplete exchange-config/port data is not fatal but must mark diagnostics incomplete and link down while still allowing later link-up events.
- FSF status handling mixes recoverable, retryable, fatal, and informational statuses. Incorrect classification can either cause needless adapter shutdowns or miss required recovery.
- CT/ELS chained SBAL layout depends on hardware features and data-router state; mismatch can cause `FSF_SBAL_MISMATCH` or unsupported operation.
- SCSI command `host_scribble` stores the FSF request id cast through pointer-sized storage; build-time size assertion protects this.
- Protection/DIF directions and SG layout must match hardware expectations or data integrity errors are reported.
- `zfcp_fsf_req_trace()` updates latency only when measurement data is supported and request succeeded; tests must not assume latency on every command.

## Test Signals

Important validation signals include:

- Every FSF command sets correct QTCB command/type, port/lun handles, data direction, and SBAL flags.
- Status-read events trigger expected actions: link down blocks rports and marks adapter failed; link up reopens adapter; notification lost triggers scan/work; bit-error threshold optionally shuts down.
- Synchronous exchange functions return `0`, `-EIO`, `-EAGAIN`, `-ENOMEM`, or `-EOPNOTSUPP` according to request and incomplete status.
- ERP-owned requests notify ERP exactly once and clear `fsf_req_id` on send failure/dismissal.
- SCSI FCP completion sets SCSI status/sense/residual/DID codes correctly and calls `scsi_done()` under abort-lock protection.
- Abort and TMF paths distinguish succeeded, not-needed, transport error, and task-management failure states.
- FC security changes generate debug/log messages only when old and new representations differ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_fsf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_fsf.h -->
# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_fsf.h`

## Purpose

`zfcp_fsf.h` defines the hardware-facing FSF command constants, status values, qualifiers, feature bits, QTCB wire layouts, status-read payload layouts, port/config data layouts, block trace metadata, and CT/ELS request envelope used by the zfcp FSF implementation. It is the protocol contract between zfcp and the FCP adapter firmware.

## Important APIs, Types, And Data

- FSF command constants include FCP command, abort, open/close port/LUN, close physical port, send ELS/generic CT, exchange config/port data, and control file commands.
- QTCB type constants distinguish IO, support, config, and port commands.
- Protocol status constants (`FSF_PROT_*`) and FSF status constants (`FSF_*`) drive recovery and error classification in `zfcp_fsf.c`.
- Status qualifier constants define recommendations and detailed link/security reasons.
- Status-read constants define unsolicited status payload types and subtypes for port closed, incoming ELS, sense data, bit errors, link down/up, notification lost, feature update, and version changes.
- Feature constants expose adapter capabilities such as notification lost, HBAAPI management, chained CT/ELS SBALs, update alerts, SFP data, FC security, DIF/DIX, and NPIV mode.
- `struct fsf_status_read_buffer` is the unsolicited status buffer with queue designator, D_ID, LUN, and a large payload union for raw data, link-down info, bit errors, and version changes.
- `union fsf_prot_status_qual`, `union fsf_status_qual`, `struct fsf_qtcb_prefix`, `struct fsf_qtcb_header`, and `struct fsf_qtcb` define the QTCB exchanged with hardware.
- `struct fsf_qtcb_bottom_io`, `_support`, `_config`, and `_port` define command-specific bottoms for SCSI I/O, support commands, adapter config, and local port data.
- `struct zfcp_blk_drv_data` stores zfcp blktrace metadata: magic, flags, QDIO usage, channel latency, and fabric latency.
- `struct zfcp_fsf_ct_els` is the software envelope for CT/ELS requests: SG request/response, completion handler/data, optional port, status, and destination id.

## Control Flow And Integration

This header is consumed primarily by `zfcp_fsf.c`, which fills QTCBs according to the command constants and interprets status/qualifier values according to these definitions. QDIO carries QTCB pointers and status-read buffers. FC code fills `zfcp_fsf_ct_els` to send CT/ELS requests. Diagnostics cache `fsf_qtcb_bottom_config` and `fsf_qtcb_bottom_port`. SCSI command setup fills `fsf_qtcb_bottom_io`.

## State And Persistence

The types are wire/data layouts, not active state machines. Runtime state appears when these structures are embedded in allocated QTCBs, status-read data pages, diagnostic caches, and block trace records. Most structs are packed to match adapter firmware layout, so their field offsets are persistent protocol contracts.

## Dependencies

The header depends on Linux scatterlist/PFN helpers and libfc/SCSI FC structures. It uses big-endian encoded fields and 24-bit FC IDs manipulated by libfc helpers in implementation files.

## Risks And Edge Cases

- Packed protocol structures must match firmware exactly. Reordering or changing padding breaks hardware communication.
- Several constants share values or semantics across features, for example measurement/request-SFP feature bits; implementation must interpret them in the correct context.
- FSF status additions require updates in `zfcp_fsf.c` handlers, debug formatting, and test expectations.
- `FSF_STATUS_READ_PAYLOAD_SIZE` drives status-read buffer allocation and debug payload assumptions.
- `FSF_FCP_CMND_SIZE` and `FSF_FCP_RSP_SIZE` are checked against FCP structures in implementation; any upstream FCP struct growth can break build-time assertions.
- Security and link-down qualifier values are used for user-visible logs and recovery choices.

## Test Signals

Validation should include:

- Build-time size/layout assertions for FCP command/response structures and QTCB sizes.
- Hardware or simulator exchange-config/port-data parses into expected adapter and port fields.
- FSF status and qualifier values map to correct recovery/logging paths.
- Packed status-read buffers decode ELS, bit-error, link, and version-change payloads correctly.
- Blktrace data magic/flags/latency fields are stable for block-layer consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_fsf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_qdio.c -->
# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_qdio.c`

## Purpose

`zfcp_qdio.c` implements setup, open/close, interrupt processing, accounting, SBAL allocation, scatterlist mapping, send, and teardown for the zfcp QDIO transport queues. It is the lower transport layer between FSF request objects and the s390 QDIO/CIO hardware interface.

## Important APIs And Functions

- Module parameter `datarouter` (`enable_multibuffer`) requests hardware data-router/multi-buffer support.
- Error and accounting:
  - `zfcp_qdio_handler_error()` converts QDIO errors into SIOSL logging, adapter shutdown, or adapter reopen.
  - `zfcp_qdio_zero_sbals()` clears queue buffers after completion or rollback.
  - `zfcp_qdio_account()` accumulates request-queue utilization over TOD-clock time.
- Interrupt/tasklet processing:
  - `zfcp_qdio_int_req()` handles request queue errors.
  - `zfcp_qdio_request_tasklet()` inspects output queue completions, frees SBALs, updates accounting, wakes waiters, and arms a rescan timer.
  - `zfcp_qdio_request_timer()` schedules request completion scanning.
  - `zfcp_qdio_int_resp()` processes input/response queue completions, logs multi-buffer default errors, calls `zfcp_fsf_reqid_check()` for each returned SBAL, and reposts input buffers.
  - `zfcp_qdio_irq_tasklet()` polls input queue and restarts QDIO interrupts.
  - `zfcp_qdio_poll()` schedules IRQ tasklet from QDIO polling.
- SBAL helpers:
  - `zfcp_qdio_sbals_from_sg()` maps a scatterlist into chained SBAL/SBALE entries and rolls back on exhaustion.
  - `zfcp_qdio_sbal_get()` waits up to five seconds for a free request SBAL while holding/releasing `req_q_lock`.
  - `zfcp_qdio_send()` submits prepared SBALs to the output queue and updates queue indices/free count.
- Lifecycle:
  - `zfcp_qdio_setup()` allocates and initializes `struct zfcp_qdio`, queues, locks, tasklets, and timer.
  - `zfcp_qdio_open()` establishes QDIO, reads SSQD capabilities, configures data division/multi-buffer flags, posts response buffers, enables tasklets, and updates SCSI host queue limits.
  - `zfcp_qdio_close()` clears QDIOUP under the request lock, wakes waiters, disables tasklets/timers/IRQs, shuts down QDIO, clears used outbound SBALs, and resets free count.
  - `zfcp_qdio_destroy()` kills tasklets, frees QDIO structures and buffers.
  - `zfcp_qdio_shost_update()` sets SCSI host SG table size and max sectors from QDIO limits.
  - `zfcp_qdio_siosl()` triggers hardware logging once per shutdown cycle.

## Control Flow

FSF callers hold `qdio->req_q_lock`, get an SBAL, initialize a `zfcp_qdio_req`, fill QTCB/data SG entries, and call `zfcp_qdio_send()`. Send accounts current queue fill, subtracts used SBALs, calls `qdio_add_bufs_to_output_queue()`, rolls back on failure, schedules request-completion scanning when the queue is low or arms a timer otherwise, and advances the request queue index.

On response interrupts, the IRQ tasklet inspects the input queue and `zfcp_qdio_int_resp()` calls FSF request-id completion for each returned SBAL, then reposts the buffers. On output/request completion, the request tasklet inspects the output queue, zeros completed SBALs, adds them back to `req_q_free`, and wakes waiters.

Errors from QDIO usually reopen the adapter. Severe SLSB-state errors trigger SIOSL and adapter shutdown. Response errors under multi-buffer mode also collect returned SBAL pointers for debug tracing before recovery.

## State And Persistence

The persistent per-adapter QDIO state lives in `struct zfcp_qdio`: request/response queue buffer arrays, current request index, atomic free count, utilization counters, full counter, wait queue, tasklets, timer, adapter pointer, and per-request element limits. Adapter status bits track QDIOUP, SIOSL issued, data division enabled, and multi-buffer active.

## Dependencies And Integration

The file depends on Linux tasklets, timers, lockdep, QDIO/CIO APIs, s390 SSQD descriptors, zfcp ERP for recovery, zfcp FSF for request completion, zfcp debug feature for default error traces, and SCSI host update through adapter fields.

## Risks And Edge Cases

- Request queue lock and IRQ-disabled context requirements are strict. `zfcp_qdio_send()` asserts IRQs disabled because accounting is protected differently from tasklet context.
- `zfcp_qdio_sbal_get()` can sleep while using `wait_event_interruptible_lock_irq_timeout`; callers must be in process context.
- If output queue completion stalls, SBAL wait timeout increments `req_q_full` and triggers adapter reopen.
- `zfcp_qdio_sbals_from_sg()` must roll back partially filled chained SBALs on exhaustion; missed zeroing would corrupt later requests.
- Closing clears QDIOUP before shutdown so no new output buffers are submitted during `qdio_shutdown()`.
- Unknown or failed response queue reposting triggers adapter reopen; response buffers must be reposted reliably to keep status reads flowing.
- Multi-buffer limits affect SCSI host `sg_tablesize`; bad capability detection can cause overlarge I/O requests.

## Test Signals

Useful signals include:

- QDIO open detects data-division and multi-buffer capabilities and sets adapter status/limits accordingly.
- Request queue free count, index, and zeroed SBALs remain consistent across send, output completion, send failure, and close.
- Scatterlists spanning multiple pages/SBALs map correctly and fail cleanly when exceeding request limits.
- Response queue completion calls FSF request-id checking for each returned SBAL and reposts buffers.
- QDIO error injection triggers expected adapter reopen/shutdown and SIOSL only once.
- SCSI host limits update after QDIO open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_qdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_qdio.h -->
# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_qdio.h`

## Purpose

`zfcp_qdio.h` declares the zfcp QDIO queue state, per-request SBAL cursor state, and inline helpers for constructing QDIO request queue buffers. It is used by FSF command code to lay out request ids, QTCBs, CT/ELS payloads, SCSI data SGs, chaining flags, data-router division counts, and multi-buffer scount values before submission.

## Important APIs, Types, And Data

- `ZFCP_QDIO_SBALE_LEN` defines one SBALE data capacity as `PAGE_SIZE`.
- `ZFCP_QDIO_MAX_SBALS_PER_REQ` caps one request at 36 SBALs for chaining.
- `struct zfcp_qdio` stores response/request queue buffer arrays, request queue index/free count, accounting and request locks, utilization counters, full counter, wait queue, tasklets, request timer, adapter pointer, and per-SBAL/per-request element limits.
- `struct zfcp_qdio_req` stores the in-progress request's SBAL type, number, first/last/limit indices, current SBALE index, and outbound queue usage snapshot.
- `zfcp_qdio_sbale_req()` returns element zero for the current request SBAL, used for request id/control metadata.
- `zfcp_qdio_sbale_curr()` returns the current SBALE cursor.
- `zfcp_qdio_req_init()` initializes a request in the current free SBAL, writes request id into element zero, sets command/type flags, computes SBAL limit from free count, and optionally writes the first data block.
- `zfcp_qdio_fill_next()` adds another data block within a single SBAL and BUGs on overflow.
- `zfcp_qdio_set_sbale_last()` marks the current entry as the last entry.
- `zfcp_qdio_sg_one_sbale()` returns true when a scatterlist fits in one SBALE.
- `zfcp_qdio_skip_to_last_sbale()` moves the cursor to the last element of the current SBAL.
- `zfcp_qdio_sbal_limit()` restricts how many SBALs the request may use.
- `zfcp_qdio_set_data_div()` writes the data division count into the first SBALE length field.
- `zfcp_qdio_real_bytes()` totals scatterlist bytes.
- `zfcp_qdio_set_scount()` writes multi-buffer SBAL count into the first SBALE.

## Control Flow And Integration

FSF command setup starts with `zfcp_qdio_req_init()` under `qdio->req_q_lock`, then appends command-specific buffers using inline helpers and/or `zfcp_qdio_sbals_from_sg()` from `zfcp_qdio.c`. The first SBALE carries request id and command flags. Later helpers mark the last entry, limit chaining for ELS, set data division counts for separated protection/data SGs, and set scount for multi-buffer requests. Finally `zfcp_qdio_send()` submits the prepared request.

## State And Persistence

`struct zfcp_qdio` persists per adapter after setup. `struct zfcp_qdio_req` is embedded in each `struct zfcp_fsf_req` and persists for the FSF request lifetime. Inline functions mutate queue buffer memory directly, so the queue buffer contents are transient but hardware-visible until QDIO completion.

## Dependencies

The header depends on Linux interrupt/tasklet definitions, s390 QDIO buffer structures and constants, and scatterlist helpers. It assumes the including code has the full `struct zfcp_adapter` definition available when dereferencing adapter-related fields indirectly.

## Risks And Edge Cases

- `zfcp_qdio_req_init()` computes `sbal_limit` from current free count; callers must hold `req_q_lock` through final send to keep the free-count view valid.
- `zfcp_qdio_fill_next()` is only for single-SBAL requests and BUGs if it would cross the SBAL boundary.
- `zfcp_qdio_set_data_div()` and `zfcp_qdio_set_scount()` overload fields in the first SBALE according to hardware conventions; misuse can corrupt command interpretation.
- `zfcp_qdio_real_bytes()` walks until `sg_next()` returns NULL; malformed SG chains can overrun expectations.
- Request ids are converted with `u64_to_dma64()` and recovered from DMA addresses on completion; this encoding is central to FSF request lookup.

## Test Signals

Validation should cover:

- Initial request layout: first SBALE request id, command/type flags, optional QTCB pointer/length, and correct cursor values.
- Last-entry and chaining flags appear at expected entries for single and multi-SBAL requests.
- SBAL limits prevent ELS/CT layouts from exceeding hardware-supported chains.
- Data division and scount values match SG counts and SBAL count for data-router/multi-buffer cases.
- Free count and request queue index remain stable when building under lock until `zfcp_qdio_send()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_qdio.h -->
