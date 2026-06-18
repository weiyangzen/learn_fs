# subset-b-005205 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_3990_erp.c -->
# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_3990_erp.c

## Purpose

`dasd_3990_erp.c` implements IBM 3990/ECKD DASD error recovery procedures for `struct dasd_ccw_req` requests. It is the discipline-specific recovery decision tree used after channel programs fail: it interprets 24-byte and 32-byte sense data, builds additional ERP requests, retries on alternate channel paths, blocks queues while waiting for state-change readiness, issues Diagnostic Control commands, handles PAV alias recovery, and finally marks the original request done or failed.

## Important APIs, Types, and Functions

- `struct DCTL_data` is the packed payload for Diagnostic Control (`CCW_CMD_DCTL`) requests, mainly used with Inhibit Write modifiers.
- `dasd_3990_erp_action()` is the exported/main entry point. It is called with the DASD queue lock held and returns either the original request or a new ERP-chain head.
- `dasd_3990_erp_add_erp()` creates a default ERP. In command mode it builds a NOOP/TIC chain to the failed CCW. In transport mode it clones the TCW and supplies a fresh TSB so original sense data is preserved.
- `dasd_3990_erp_inspect()` routes recovery through alias inspection, control-check handling, 24-byte sense handling, or 32-byte sense handling.
- `dasd_3990_erp_inspect_24()` dispatches classic sense bits such as command reject, intervention required, equipment check, data check, overrun, invalid track format, EOC, environmental data, no-record-found, and file-protected.
- `dasd_3990_erp_inspect_32()` handles SIM sense data, compound program action codes, and single program action codes such as fatal error, intervention required, logging required, action 1B write restart, state-change pending, and busy.
- `dasd_3990_erp_action_1()`, `dasd_3990_erp_action_4()`, and `dasd_3990_erp_action_5()` implement common recovery strategies: alternate path retry, queue blocking with timer, and retry-before-further-recovery.
- `dasd_3990_erp_action_1B_32()` and `dasd_3990_update_1B()` build/update a DE/LO/TIC ERP to resume an interrupted write from precise sense information.
- `dasd_3990_erp_further_erp()` chooses second-stage handling once retries are exhausted.
- `dasd_3990_erp_handle_sim()` logs SIM source reference codes and is callable outside the main ERP path.

## Control Flow

The main flow starts in `dasd_3990_erp_action(cqr)`. If the request actually completed with clean channel/device status, the request is marked `DASD_CQR_DONE`. Otherwise the code checks whether the same error already appears in the current ERP chain via `dasd_3990_erp_in_erp()`. A new error gets a default ERP through `dasd_3990_erp_additional_erp()`, followed by sense inspection. A repeated error reuses the matching ERP through `dasd_3990_erp_handle_match_erp()`, freeing successful leading ERP blocks and either retrying, updating special ERP data, or invoking `dasd_3990_erp_further_erp()` when retries reach zero.

The 24-byte sense path is a priority-ordered bit dispatch. Command rejects usually fail permanently unless environmental data suggests retry, writes are inhibited, or the request is invalid on a copy-pair secondary. Equipment and data checks select alternate-path, state-change wait, or action-5 retry depending on write-inhibited, environmental-data, permanent-error, and retry-exhausted bits. Some unrecoverable states, such as no-record-found, file-protected, invalid format without environmental data, or EOC, clean up the ERP and fail the original request. Correctable data checks with potentially incorrect data panic because the block layer cannot report "possibly wrong" data to the application.

The 32-byte path first logs SIM data when present. Compound action codes run in phases: set retry count from byte 25, optionally try alternate path, optionally issue DCTL or wait, then report configuration errors. Single action codes either retry, fail, run intervention-required handling, run logging-required handling, build action 1B restart ERP, or wait for state-change/busy.

Alias inspection runs before sense dispatch. If the failed request started on an alias device while its block base differs from `startdev`, the code may remove and reload a stale dynamic PAV alias, rewrites the CQR to base I/O with `dasd_eckd_reset_ccw_to_base_io()`, and restarts ERP on the base device.

## State and Persistence Behavior

The file mutates in-memory request and device state only; it has no persistent on-disk state. It changes `cqr->status`, `retries`, `function`, `refers`, `lpm`, `expires`, and ERP list membership. It manipulates device stop bits (`DASD_STOPPED_PENDING`), block/device timers, path masks, path error counters, and path error timestamps. Path autodisable state is reflected in `device->path[]` and operational path masks. ERP chains are explicit linked stacks through `refers`; successful intermediate ERP requests are removed from lists and freed.

## Dependencies and Integration Points

This code is tightly coupled to DASD core request handling (`dasd_alloc_erp_request`, `dasd_free_erp_request`, timers, queue status values), ECKD channel program data (`DEFINE_EXTENT`, `LOCATE_RECORD`, `PFX`, PSF, TIC), S/390 channel status and sense helpers (`scsw_*`, `dasd_get_sense`), path management (`dasd_path_get_opm`, `dasd_path_remove_opm`, `dasd_path_add_ifccpm`), extended error reporting (`dasd_eer_write`), and alias management (`dasd_alias_remove_device`, `dasd_reload_device`). It also respects user/devmap features such as `DASD_FEATURE_ERPLOG`, `DASD_FEATURE_PATH_AUTODISABLE`, and verification flags.

## Risks

The code is safety-critical and table-driven by hardware sense-byte conventions; small byte-index mistakes can cause wrong recovery, permanent I/O failure, or repeated retries. ERP chains require careful lifetime handling because requests are freed while list links and `refers` relationships are rewritten. Correctable-data cases intentionally panic, so regressions around sense classification can turn recoverable or reportable errors into system crashes. Path autodisable must avoid disabling the last path and must correctly account IFCC windows. Alias rerouting is race-sensitive because a dynamic PAV mapping can change while I/O and recovery are in progress.

## Test Signals

Useful test evidence would include fault-injection or hardware/z/VM tests for 24-byte and 32-byte sense classifications, action 1 alternate-path sequencing, action 4 timer/queue-block behavior, action 1B DE/LO restart construction, repeated-error chain matching, path threshold/autodisable behavior, and alias-to-base retry after PAV mapping changes. Logs from `DASD_FEATURE_ERPLOG`, DBF events, SIM messages, EER PPRC suspend events, and final CQR statuses are the primary observability signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_3990_erp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_alias.c -->
# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_alias.c

## Purpose

`dasd_alias.c` manages Parallel Access Volume alias devices for the DASD ECKD discipline. It keeps a server/LCU/PAV-group model, connects devices to LCUs as they are discovered, moves serviceable devices into active PAV groups, selects alias devices for I/O load distribution, refreshes unit-address configuration, and handles summary unit check recovery.

## Important APIs, Types, and Functions

- The file-level `aliastree` is an `alias_root` containing all known storage servers and protected by a spinlock.
- `_find_server()`, `_find_lcu()`, and `_find_group()` locate the storage server, logical control unit, and PAV group matching a DASD UID.
- `_allocate_server()`, `_allocate_lcu()`, `_free_server()`, and `_free_lcu()` allocate and release alias-management structures and embedded work/CQR resources.
- `dasd_alias_make_device_known_to_lcu()` creates or reuses the server and LCU for a device and links the device into the LCU inactive list.
- `dasd_alias_disconnect_device_from_lcu()` cancels pending workers that reference the device, unlinks the device, and frees empty LCU/server structures.
- `dasd_alias_add_device()`, `dasd_alias_update_add_device()`, and `dasd_alias_remove_device()` mark devices active or inactive for PAV use.
- `read_unit_address_configuration()` sends PSF/RSSD commands to populate the LCU unit-address configuration (`uac`).
- `_lcu_update()`, `lcu_update_work()`, and `_schedule_lcu_update()` refresh PAV mode and group membership asynchronously.
- `dasd_alias_get_start_dev()` selects a usable alias for a base device.
- `dasd_alias_handle_summary_unit_check()` and `summary_unit_check_handling_work()` stop devices, flush alias queues, reset summary unit check, restart base devices, and trigger an LCU refresh.

## Control Flow

Discovery calls `dasd_alias_make_device_known_to_lcu()`. The function reads the device UID via the ECKD discipline, creates the server and LCU outside the global lock when needed, then rechecks under lock to handle races. The device is initially linked into `lcu->inactive_devices` and records the LCU in its private data.

When a device becomes serviceable, `dasd_alias_add_device()` checks whether the device UID type matches the current LCU unit-address data. If the LCU is current, `_add_device_to_lcu()` updates the device UID from `uac`, determines the LCU PAV mode, creates/fetches a PAV group, and moves the device into a base or alias list. If the LCU data is stale, the device goes to `active_devices`, `UPDATE_PENDING` is set, and `_schedule_lcu_update()` queues a delayed worker using a referenced device.

The update worker first dissolves existing PAV groups back into `active_devices`, reads UAC data using PSF/RSSD, determines `NO_PAV`, `BASE_PAV`, or `HYPER_PAV`, and rebuilds groups. Hyper PAV uses a single group, while base PAV groups by base unit address and VDUIT. If another update is requested during the read, the worker leaves grouping incomplete and retries later.

For each I/O, `dasd_alias_get_start_dev()` checks that PAV is enabled and not pending update, verifies prefix support, finds the base device's PAV group, advances the round-robin `group->next` pointer, and returns an alias only if its outstanding count is lower than the base, it is not stopped, and it is not offline.

Summary unit check recovery is a separate work path. The entry function sets `DASD_STOPPED_SU` on all LCU devices, marks UAC update pending, stores the reason, and schedules work. The worker flushes alias queues without holding the LCU lock during blocking flushes, clears stop bits on the reporting device to issue RSCK, unstops devices, restarts base devices, and schedules a UAC refresh.

## State and Persistence Behavior

All state is in memory. Important state includes the global alias tree, LCU flags (`NEED_UAC_UPDATE`, `UPDATE_PENDING`), the LCU `uac` table, PAV mode, active/inactive device lists, PAV group base/alias lists, per-device `private->lcu` and `private->pavgroup`, worker-owned referenced devices, and summary unit check reason. The code uses reference counts (`dasd_get_device`/`dasd_put_device`) around asynchronous workers and cancels workers during disconnect to avoid use-after-free.

## Dependencies and Integration Points

The implementation depends on ECKD-specific UID and CCW definitions from `dasd_eckd.h`, core request allocation/sleep helpers, Linux workqueues, spinlocks, CCW device locks, and DASD scheduling helpers. It is used by the ECKD discipline during check/add/remove and by the ERP code when an alias request must recover on the base device. It also coordinates with device stop bits and block/device bottom halves to pause and restart I/O.

## Risks

The highest risks are concurrency and lifetime issues: devices can go offline while update or summary-unit-check work is pending, and list membership changes while queues are flushed unlocked. UAC reads can fail transiently or be unsupported; the code must distinguish retryable failure from `-EOPNOTSUPP`. Alias selection is intentionally simple and can underutilize aliases if `count`, stop bits, or offline flags lag. Stale dynamic PAV mappings can route work to the wrong alias until a reload/update path runs.

## Test Signals

Important signals include correct server/LCU/group construction for base PAV and Hyper PAV, worker cancellation on disconnect, no leaked references after update and summary-unit-check paths, alias selection only returning online unstopped aliases with lower load, recovery from UAC mismatch, and RSCK/UAC refresh after summary unit check. DBF warnings, stop-bit state, list membership, and device reference counts are the main runtime evidence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_alias.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_devmap.c -->
# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_devmap.c

## Purpose

`dasd_devmap.c` owns DASD device mapping and much of the user-visible device configuration surface. It parses `dasd=` boot/module parameters, maps CCW bus IDs to stable DASD device indexes and feature flags, creates and deletes `struct dasd_device` instances, manages PPRC/copy-pair metadata, exposes sysfs attributes, and creates per-path sysfs kobjects.

## Important APIs, Types, and Functions

- `struct dasd_devmap` stores the bus ID, stable device index, feature bitmask, current `struct dasd_device *`, copy relation pointer, and autoquiesce mask.
- Global state includes `dasd_page_cache`, `dasd_probeonly`, `dasd_autodetect`, `dasd_nopav`, `dasd_nofcx`, `dasd_hashlists[256]`, `dasd_max_devindex`, and the `dasd_devmap_lock`.
- Parameter parsing is implemented by `dasd_call_setup()`, `dasd_busid()`, `dasd_feature_list()`, `dasd_parse_keyword()`, `dasd_evaluate_range_param()`, `dasd_parse_range()`, and `dasd_parse()`.
- Mapping/lifetime APIs include `dasd_add_busid()`, `dasd_busid_known()`, `dasd_device_from_devindex()`, `dasd_create_device()`, `dasd_delete_device()`, `dasd_device_from_cdev_locked()`, `dasd_device_from_cdev()`, `dasd_add_link_to_gendisk()`, and `dasd_device_from_gendisk()`.
- Copy relation support is implemented by `dasd_devmap_set_device_copy_relation()`, `dasd_devmap_get_pprc_status()`, `dasd_devmap_check_copy_relation()`, `dasd_copy_pair_show/store()`, and `dasd_copy_role_show()`.
- `dasd_dev_groups` exports the sysfs attribute groups for the ccw device, including base attributes, `capacity`, and `extent_pool`.
- `dasd_get_feature()` and `dasd_set_feature()` read/update devmap feature bits and mirror them into a live device.
- Path sysfs support is provided by `dasd_path_create_kobj()`, `dasd_path_create_kobjects()`, and `dasd_path_remove_kobjects()`.

## Control Flow

Boot/module parsing stores comma-separated `dasd=` tokens, then `dasd_parse()` processes each token as either a keyword or range. Keywords toggle global behavior such as autodetect, probeonly, nopav, nofcx, or fixed DMA page cache creation. Ranges are parsed from old-style devnos, full bus IDs, or `ipldev`; optional feature lists set readonly, diag, raw, erplog, and failfast bits. Each expanded bus ID is inserted with `DASD_FEATURE_INITIAL_ONLINE`.

Device creation starts from a CCW device. `dasd_devmap_from_cdev()` finds or creates a devmap, `dasd_alloc_device()` allocates a DASD device, and `dasd_create_device()` installs the device under `dasd_devmap_lock`, assigns the devindex and features, references the ccw device, stores driver data under the CCW lock, and creates the `paths_info` kset. Deletion removes the devmap pointer first, clears driver data, removes copy relation state, drops three creation references, waits for the refcount to reach zero, releases discipline data, unregisters path ksets, drops the ccw device, and frees the DASD device.

Sysfs attributes either operate on persistent devmap feature state, live device state, or discipline callbacks. Feature-style attributes include `failfast`, `readonly`, `erplog`, `use_diag`, `raw_track_access`, `aq_requeue`, `reservation_policy`, and `path_autodisable`. Live attributes include status, discipline, alias/vendor/uid, EER enablement, timeouts/retries, block timeout, host access count, path masks, path reset, HPF, path thresholds/intervals, FC security, copy role, ping, autoquiesce settings, and extent-pool/capacity callback values. Some toggles, notably `use_diag` and raw track access, are only accepted while the device is offline and mutually exclusive with the other mode.

Copy-pair setup parses `primary,secondary`, ensures the sysfs device is one side of the pair, creates devmaps for both sides, requires the secondary to be offline, links both devmaps to a shared `dasd_copy_relation`, and if the primary is already online validates PPRC state through the discipline. Clearing is allowed only when all secondary devices are offline, then devmaps and live device copy pointers are detached and references dropped.

## State and Persistence Behavior

The file persists desired DASD state for the lifetime of the module in devmap entries: bus ID to devindex, feature flags, autoquiesce masks, and configured copy relation metadata. Live `struct dasd_device` pointers are transient and protected by `dasd_devmap_lock` or CCW locks depending on access path. Sysfs writes update the devmap so settings can outlive a device going offline and also update the live device when present. There is no disk persistence in this file; persistence is kernel-memory lifetime and boot/module parameter replay.

## Dependencies and Integration Points

The code integrates with the CCW bus (`struct ccw_device`, `dev_set_drvdata`, `ccw_device_set_offline`), Linux block layer (`gendisk->private_data`, queue request timeout, readonly disk state), DASD core allocation/refcount/discipline APIs, DASD EER, path helpers, PPRC discipline callbacks, sysfs/kobject infrastructure, IPL metadata for `ipldev`, and module parameter/init setup. The exported feature and device lookup helpers are used by DASD disciplines and other DASD core code.

## Risks

This file contains many lock/refcount transitions; device creation/deletion and sysfs reads must avoid stale live device pointers. Several sysfs stores return after acquiring a device reference; error paths must put references consistently. Copy-pair setup is sensitive because misconfigured PPRC relations could route I/O to the wrong mirror side, so the code cross-checks all related devices. `use_diag`/raw toggles are intentionally constrained because changing discipline mode online would invalidate live state. Path kobjects are kept for device lifetime and must only be removed in offline context, as documented in the file.

## Test Signals

Useful validation includes parsing `dasd=` keywords/ranges/feature lists including `ipldev`, duplicate bus ID insertion preserving stable devindex, create/delete refcount drain, sysfs show/store behavior for each feature and live attribute, readonly propagation to gendisk, offline-only rejection for diag/raw mode changes, copy-pair setup/clear with online/offline combinations, PPRC validation failures, path kobject create/remove on path availability, and absence of devmap leaks after `dasd_devmap_exit()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_devmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_diag.c -->
# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_diag.c

## Purpose

`dasd_diag.c` implements the DASD `DIAG` discipline for z/VM virtual DASD devices. Instead of using normal SSCH channel programs, it uses z/VM DIAG 0x250 calls to initialize block I/O, submit read/write block lists, terminate the DIAG environment, and complete asynchronous I/O through external interrupts.

## Important APIs, Types, and Functions

- `struct dasd_diag_private` stores per-device DIAG state: read-device-characteristics data, reusable RW and init I/O blocks, partition-table/label block offset, and CCW device ID.
- `struct dasd_diag_req` is embedded in `dasd_ccw_req->data` and holds a block count plus flexible array of DIAG bio descriptors.
- `__dia250()` is the inline assembly wrapper around `diag ...,0x250`, with exception-table handling and return-code composition.
- `dia250()` increments the DIAG statistic and calls `__dia250()`.
- `mdsk_init_io()` and `mdsk_term_io()` issue `INIT_BIO` and `TERM_BIO`.
- `dasd_start_diag()` fills `struct dasd_diag_rw_io`, submits `RW_BIO`, and maps return codes to synchronous success, asynchronous in-I/O, or error recovery.
- `dasd_ext_handler()` handles CP service external interrupts for 31-bit and 64-bit DIAG interrupt parameters and completes or requeues requests.
- `dasd_diag_check_device()` probes a device for DIAG support, reads characteristics, determines FBA/ECKD label block, finds block size, reads CMS label data, initializes block metadata, and starts the DIAG environment.
- `dasd_diag_build_cp()` converts a Linux block request into a `dasd_ccw_req` containing one `dasd_diag_bio` per DASD block.
- `dasd_diag_discipline` registers the discipline callbacks used by DASD core.

## Control Flow

Module init rejects non-z/VM machines, converts the discipline EBCDIC name, registers the CP service external interrupt handler, and publishes `dasd_diag_discipline_pointer`.

Device checking allocates private and block structures, calls `diag210()` for virtual device characteristics, selects label position (`pt_block` 1 for FBA, 2 for ECKD), terminates any old DIAG environment, and probes block sizes from 512 bytes through `PAGE_SIZE`. For each candidate it initializes DIAG I/O, reads the expected CMS label block synchronously, and terminates DIAG again. If a CMS1 label is found, the block size and count come from the label; otherwise the reported DIAG `end_block` is used. A final `mdsk_init_io()` sets the runtime block size; return code 4 marks the device read-only but is not fatal.

Request building validates read/write direction, computes first/last DASD record from request sectors and `s2b_shift`, verifies every bio segment is block-aligned, counts blocks, allocates enough request data for all DIAG bio entries, and fills each entry with type, 1-based DIAG block number, and buffer pointer. Start I/O then submits the whole bio list asynchronously by default. DIAG rc 0 means synchronous completion and returns `-EACCES` to signal only bottom-half scheduling is needed; rc 8 means asynchronous I/O started; other codes trigger DIAG ERP and `-EIO`.

The external interrupt handler filters DIAG subcodes, resolves the interrupt parameter to a CQR, verifies the request magic against the discipline, takes the CCW-device lock, handles pending clear, marks success or requeues on subcode error, optionally starts the next queued request immediately, manages timers, and schedules the device bottom half.

## State and Persistence Behavior

The discipline stores all device state in memory under `device->private` and `device->block`. Runtime state includes the DIAG I/O environment, block size/count, read-only flag, reusable I/O blocks, request retry counts, timers, status fields, and external interrupt completion timestamps. It has no durable persistence. `dasd_diag_erp()` tears down and reinitializes the DIAG environment after errors, and can update the read-only flag if z/VM reports access changed.

## Dependencies and Integration Points

The file integrates with z/VM DIAG 0x250 and DIAG 0x210, S/390 external interrupt registration, DASD core discipline callbacks, block request iteration, VTOC/CMS label formats, request allocation/free helpers, device timers, bottom-half scheduling, path verification, and generic DASD ERP postaction handlers. `dasd_diag.h` defines the packed ABI structures shared with the DIAG call.

## Risks

DIAG parameter structures are ABI-sensitive and packed/aligned; field or alignment regressions can break hypervisor calls. The code assumes full-block I/O and rejects partial-block segments. The external interrupt path trusts the interrupt parameter as a CQR after magic validation, so stale or corrupted interrupt parameters are critical. The block-size probing loop issues real synchronous reads and must clean up label/bio allocations on every failure. A correct distinction between rc 0, rc 4, rc 8, and exception rc 3 is essential for read-only detection, async completion, and unsupported 64-bit DIAG behavior.

## Test Signals

Useful signals include z/VM-only module load behavior, successful diag210 characteristic reads for FBA/ECKD virtual disks, block-size probing with and without CMS1 labels, read-only rc 4 handling, request build rejection for partial blocks or invalid direction, sync rc 0 and async rc 8 start paths, interrupt completion and fast-start of the next queued request, clear-pending completion, DIAG ERP reinitialization, and max-sector calculation from the static two-page request buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_diag.h -->
# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_diag.h

## Purpose

`dasd_diag.h` defines the constants, numeric request codes, block-number typedefs, and packed/aligned parameter structures used by the z/VM DIAG DASD discipline in `dasd_diag.c`. It is the local ABI description for DIAG 0x250 block I/O and DIAG 0x210 characteristics data.

## Important APIs, Types, and Functions

- `MDSK_WRITE_REQ` and `MDSK_READ_REQ` identify per-block write/read entries in a DIAG bio list.
- `INIT_BIO`, `RW_BIO`, and `TERM_BIO` are the function selectors passed to DIAG 0x250 for setup, I/O, and teardown.
- `DEV_CLASS_FBA` and `DEV_CLASS_ECKD` classify supported virtual DASD device types.
- `DASD_DIAG_CODE_31BIT` and `DASD_DIAG_CODE_64BIT` identify external-interrupt subcodes and therefore how the interrupt parameter is decoded.
- `DASD_DIAG_RWFLAG_ASYNC` and `DASD_DIAG_RWFLAG_NOCACHE` control runtime I/O behavior.
- `DASD_DIAG_FLAGA_FORMAT_64BIT` and `DASD_DIAG_FLAGA_DEFAULT` select the 64-bit parameter format used by this driver.
- `blocknum_t` and `sblocknum_t` provide unsigned/signed 64-bit block numbering.
- `struct dasd_diag_characteristics` is the DIAG 0x210 characteristics layout.
- `struct dasd_diag_bio` is one block operation descriptor: type, status, ALET, block number, and buffer pointer.
- `struct dasd_diag_init_io` describes DIAG block I/O initialization/termination state including device number, block size, offset, start block, and end block.
- `struct dasd_diag_rw_io` describes an RW request, including device number, key, flags, block count, interrupt parameter, and pointer to a bio list.

## Control Flow

The header has no executable control flow. Its structures are populated by `dasd_diag.c`: initialization calls fill `dasd_diag_init_io`, request start fills `dasd_diag_rw_io`, and request build fills arrays of `dasd_diag_bio`. The external interrupt handler uses the DIAG subcode constants to interpret 31-bit versus 64-bit interrupt parameters.

## State and Persistence Behavior

The header defines transient in-memory layouts only. State is held by instances embedded in `struct dasd_diag_private`, allocated request payloads, or temporary stack/heap objects in the DIAG discipline. The explicit `packed` and `aligned` attributes are part of the ABI contract with z/VM and are more important than normal C layout convenience.

## Dependencies and Integration Points

The definitions depend on Linux fixed-width integer types and are included by `dasd_diag.c`. The layouts integrate directly with S/390 DIAG instructions, z/VM minidisk I/O conventions, and the DASD discipline's request conversion path. `struct dasd_diag_characteristics` is cast-compatible with the DIAG 0x210 call site.

## Risks

The principal risk is ABI drift. Changing field order, size, signedness, pointer width assumptions, packing, or alignment can make DIAG 0x250 or 0x210 fail or corrupt I/O. The default 64-bit format must remain consistent with the interrupt subcode handling in `dasd_diag.c`. The pointer in `struct dasd_diag_bio` and `bio_list` in `struct dasd_diag_rw_io` mean addressability and format flags must match the running architecture/hypervisor expectations.

## Test Signals

Compile-time structure-size/alignment checks, successful 64-bit DIAG initialization, correct external interrupt parameter decoding, valid block count/end block results, and read/write completion against z/VM virtual FBA/ECKD disks are the relevant signals. Runtime failures often surface as DIAG rc 3 exceptions, unsupported-device errors, or missing asynchronous completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_diag.h -->
