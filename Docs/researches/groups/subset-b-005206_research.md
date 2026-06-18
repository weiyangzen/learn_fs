# subset-b-005206 grouped research

Work item `subset-b-005206` covers the s390 DASD ECKD, EER, ERP, and FBA support files under `sources/distributed-fs/ceph-client/drivers/s390/block/`. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_eckd.c -->
# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_eckd.c

## Purpose
This file is the S/390 DASD ECKD block-device discipline and ccw driver. It binds ECKD-compatible CKD devices, validates per-path configuration, builds channel programs for normal, raw-track, transport-mode, format, reserve/release, PPRC, CUIR, and ESE operations, and plugs those operations into the generic DASD core through `struct dasd_discipline`. It is the high-complexity data path for CKD DASD on s390, including PAV/HyperPAV alias selection and zHPF transport-mode optimization.

## Important APIs, Types, and Functions
The exported discipline is `dasd_eckd_discipline`; the bus binding is `dasd_eckd_driver` with `dasd_eckd_ids`. Startup and device identity are handled by `dasd_eckd_probe()`, `dasd_eckd_check_characteristics()`, `dasd_eckd_read_conf()`, `dasd_eckd_generate_uid()`, `dasd_eckd_validate_server()`, and `dasd_eckd_alloc_block()`. Geometry and layout detection flow through `dasd_eckd_analysis_ccw()`, `dasd_eckd_start_analysis()`, `dasd_eckd_end_analysis()`, and `recs_per_track()`.

Channel-program construction is split among `define_extent()`, `locate_record()`, `locate_record_ext()`, `prefix()`, `prefix_LRE()`, `prepare_itcw()`, `dasd_eckd_build_cp_cmd_single()`, `dasd_eckd_build_cp_cmd_track()`, `dasd_eckd_build_cp_tpm_track()`, `dasd_eckd_build_cp_raw()`, `dasd_eckd_build_cp()`, and `dasd_eckd_build_alias_cp()`. Formatting and checking use `dasd_eckd_build_format()`, `dasd_eckd_format_process_data()`, `dasd_eckd_check_device_format()`, and `dasd_eckd_format_evaluate_tracks()`. ESE support uses `dasd_eckd_read_vol_info()`, `dasd_eckd_read_ext_pool_info()`, `dasd_eckd_ese_format()`, `dasd_eckd_ese_read()`, and `dasd_eckd_release_space()`. Error, attention, and management paths include `dasd_eckd_erp_action()`, `dasd_eckd_check_for_device_change()`, `dasd_eckd_dump_sense()`, `dasd_eckd_handle_cuir()`, `dasd_eckd_handle_oos()`, `dasd_eckd_handle_hpf_error()`, `dasd_eckd_query_pprc_status()`, and `dasd_eckd_copy_pair_swap()`.

## Control Flow
Module init converts the discipline name to EBCDIC, allocates global fallback request buffers and a raw-track padding page, then registers the ccw driver. Probe sets ccw options for force, path grouping, and multipath, then delegates to generic DASD probe. Online attaches the ECKD discipline through `dasd_generic_set_online()`.

`dasd_eckd_check_characteristics()` is the main bring-up path. It requires an established channel path group, allocates or clears `dasd_eckd_private`, reads configuration data on every operational path via RCD, identifies NED/SNEQ/GNEQ records, builds a stable UID, reads device characteristics, configures PPRC copy relation state, allocates a block device only for base devices, registers the device with alias/LCU handling, validates server characteristics with PSF-SSC, rereads configuration after LCU setup, records Fibre Channel security, reads feature codes, reads ESE volume and extent-pool data, checks raw-track support, calculates real cylinder count, derives zHPF maximum data size, and marks read-only devices.

Block analysis is asynchronous on first entry. The driver submits an initial READ COUNT chain for track 0 and track 1; the callback stores an analysis status and kicks the state machine. The second pass interprets count records to distinguish CDL from Linux disk layout, rejects unformatted or unsupported layouts, computes block size, shift, records per track, and total blocks. Raw mode bypasses disk-label interpretation and exposes fixed 4 KiB blocks over 64 KiB tracks.

Request building first computes record and track spans. It prefers zHPF transport-mode track I/O if feature bits and `fcx_max_data` allow it, falls back to command-mode track data when prefix and read/write track data are supported, and finally uses single-record CCW chains. CDL special records force single-record handling because keys and short records on early tracks need command variants and padding. Raw-track requests require 64 KiB track granularity for writes and use padding pages for read misalignment.

Path and attention work is deferred. Path verification rereads per-path RCD, compares UIDs to catch cabling or hyperswap changes, updates path masks, records no-HPF paths, and creates path kobjects. CUIR and out-of-space attentions are read from the message buffer in workqueue context; CUIR quiesce/resume walks active, inactive, and PAV-group devices in the LCU, while OOS messages update extent-pool state and may resume stopped devices when space returns.

## State and Persistence
State is volatile kernel memory plus device-controller state. `struct dasd_eckd_private` caches RDC data, parsed configuration pointers, count-area samples, layout status, cache/prestage attributes, feature bytes, ESE volume query data, extent-pool summary, real cylinder count, UID, PAV group/LCU pointers, active alias request count, `fcx_max_data`, and summary-unit-check reason. Per-path configuration is stored in `device->path[]` and freed/replaced on rereads. Reservation state, readonly flags, stopped flags, path masks, and copy-relation state live in generic DASD objects and devmap/copy structures.

No disk persistence is implemented by this source. Hardware-visible changes include reserve/release/steal-lock, PSF-SSC server settings, PAV alias grouping effects, DSO release allocated space, formatting, cache attribute use in future Define Extent CCWs, and CUIR responses. Runtime caches can be invalidated by hyperswap, path events, summary unit checks, or reloads.

## Dependencies and Integration Points
The file depends on the s390 ccw bus, CIO path management, DASD core allocation/queue/state helpers, alias handling declared in `dasd_eckd.h`, 3990-specific ERP, block-layer request iteration, IDAL/TIDAW/ITCW helpers, EBCDIC conversion, debug feature logging, CHSC path security, and devmap/PPRC copy relation support. It integrates through the `dasd_discipline` callbacks for analysis, I/O construction/freeing, formatting, ioctl handling, ERP, path verification, ESE operations, host access reporting, HPF handling, and copy-pair swap. User-visible interfaces include DASD ioctls for attributes, performance, reserve/release/steal-lock, SNID, Symmetrix PSF/RSSD passthrough, host access seq output, kernel logs, and block-device behavior.

## Risks and Test Signals
Risk areas are broad. UID and path configuration parsing must be correct because wrong comparisons can disable good paths or accept mis-cabled paths. Alias/PAV request counting is concurrency-sensitive and caps channel queue depth at four per start device. XRC timestamp handling can return `-EAGAIN`, forcing request rebuild later. zHPF feature negotiation and path-specific max-data verification must avoid issuing TCWs on incapable paths. CDL special-record handling has unusual key/length behavior on early tracks. ESE error handling can zero-fill reads or trigger automatic format requests; track extraction from sense data and format-list locking are safety-critical. DSO RAS extent splitting depends on valid extent-size metadata and copy-relation state. Attention handling walks LCU lists and path masks, so lock ordering and last-path checks matter.

Useful test signals include successful probe on supported 3380/3390/9345 devices, RCD failure and `-EOPNOTSUPP` paths, multipath path-add/path-loss events, UID mismatch/cabling diagnostics, CDL/LDL/raw analysis results, blocksize rejection, regular read/write across track boundaries, CDL early-track reads and writes, zHPF enabled and fallback modes, no-HPF path disablement, ESE no-record read zero-fill, ESE write auto-format and duplicate-format suppression, release-space full and range modes, CUIR quiesce/resume with last-path denial, OOS warn/exhaust/relieve events, PPRC status and copy-pair swap, reserve/release/steal-lock ioctls, and sense-dump suppression flags for expected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_eckd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_eckd.h -->
# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_eckd.h

## Purpose
This header defines the ECKD-specific command codes, controller order/suborder constants, packed channel-program payloads, Read Subsystem Data payloads, ESE extent-pool records, CUIR/OOS attention messages, PPRC/host-access records, DSO release-space records, and PAV alias management structures shared by the ECKD discipline and alias code.

## Important APIs, Types, and Functions
The first section enumerates ECKD CCWs such as READ/WRITE, DEFINE EXTENT, LOCATE RECORD, LOCATE RECORD EXTENDED, PREFIX, READ CONFIGURATION DATA, READ SUBSYSTEM DATA, SENSE SUBSYSTEM STATUS, RESERVE/RELEASE, and DSO. PSF and DSO order constants cover PRSSD, CUIR response, SSC, Query Host Access, PPRC Extended Query, Volume Storage Query, Logical Configuration Query, and Release Allocated Space.

Core packed channel payloads are `struct eckd_count`, `struct ch_t`, `struct chr_t`, `struct DE_eckd_data`, `struct LO_eckd_data`, `struct LRE_eckd_data`, and `struct PFX_eckd_data`. Device and configuration records are represented by `struct dasd_eckd_characteristics`, `struct dasd_ned`, `struct dasd_sneq`, `struct vd_sneq`, `struct dasd_gneq`, `struct dasd_conf_data`, and `struct dasd_conf`. Subsystem query records include `struct dasd_rssd_features`, `struct dasd_rssd_messages`, `struct dasd_rssd_vsq`, `struct dasd_ext_pool_sum`, `struct dasd_rssd_lcq`, `struct dasd_psf_query_host_access`, and `struct dasd_psf_prssd_data`. ESE release-space payloads use `struct dasd_dso_ras_data` and `struct dasd_dso_ras_ext_range`.

PAV/alias state is defined by `enum pavtype`, `struct alias_root`, `struct alias_server`, `struct alias_lcu`, `struct alias_pav_group`, `struct summary_unit_check_work_data`, and `struct read_uac_work_data`. `struct dasd_eckd_private` is the ECKD discipline's per-device private state. External hooks declared here connect to alias code and ECKD I/O reset helpers.

## Control Flow
The header has no executable control flow, but its structures dictate the binary layout consumed by `dasd_eckd.c`. Define Extent and Locate Record payloads are filled before READ/WRITE/FORMAT CCWs. Prefix payloads combine Define Extent and Locate Record Extended data and carry PAV base verification bits. PSF PRSSD payloads precede RSSD reads for feature, message, host-access, PPRC, volume-storage, and logical-configuration queries. CUIR and OOS structures are interpreted after RSSD message-buffer reads. Alias structures organize devices by storage server, LCU, and PAV group so path and alias operations can walk related devices.

## State and Persistence
Most definitions are packed views over hardware, firmware, or channel-program memory and do not store state by themselves. The persistent in-memory state carrier is `struct dasd_eckd_private`: it caches device characteristics, configuration-data pointers, analyzed count records, CDL status, cache attributes, features, ESE metadata, UID, alias/LCU links, active request count, zHPF max data size, and summary-unit-check reason. The controller-visible data represented by these structures can outlive one kernel request, but the header itself provides no persistence policy.

## Dependencies and Integration Points
The header assumes Linux kernel integer types, list/completion/workqueue types, and DASD core types are available through includers. It is tightly coupled to IBM storage-controller ECKD layouts, s390 channel command encoding, DASD alias management, and the generic DASD UID/copy/path abstractions. Its exported declarations are consumed by `dasd_eckd.c`, ECKD alias-management code, and any code needing to reset alias-built channel programs back to base-device I/O.

## Risks and Test Signals
The main risks are binary layout drift and bitfield ambiguity. Almost every hardware-facing structure is `packed`, so field order, size, endian assumptions, and bit meanings must match the architecture specification. Incorrect constants can produce invalid channel programs or misinterpret subsystem messages. Alias structures mix locks, lists, completions, and request pointers, so changes must preserve lifetime and lock assumptions in the implementation. Test signals are compile-time size/layout coverage where available, successful RCD/RSSD/PSF/DSO command execution, correct UID generation from NED/GNEQ/SNEQ data, CUIR/OOS message parsing, host-access output sanity, and PAV alias grouping behavior under path changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_eckd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_eer.c -->
# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_eer.c

## Purpose
This file implements DASD extended error reporting for ECKD devices. It exposes a misc character device named `dasd_eer`, keeps one event ring buffer per open file, and exports hooks that DASD device code calls to record fatal errors, PPRC suspension, no-path/no-space/autoquiesce conditions, and state changes.

## Important APIs, Types, and Functions
`struct eerbuffer` owns one reader's ring buffer: page vector, buffer size, page count, head, tail, residual bytes for partial record delivery, and list linkage. `struct dasd_eer_header` prefixes every emitted record with total size, trigger id, wall-clock timestamp, and DASD bus id. Ring helpers are `dasd_eer_get_free_bytes()`, `dasd_eer_get_filled_bytes()`, `dasd_eer_write_buffer()`, `dasd_eer_read_buffer()`, and `dasd_eer_start_record()`.

Event producers use exported `dasd_eer_write()` and `dasd_eer_snss()`. Enabling/disabling per device uses `dasd_eer_enable()` and `dasd_eer_disable()`. Trigger encoders are `dasd_eer_write_standard_trigger()` and `dasd_eer_write_snss_trigger()`. The SNSS request callback is `dasd_eer_snss_cb()`. Userspace file operations are `dasd_eer_open()`, `dasd_eer_close()`, `dasd_eer_read()`, and `dasd_eer_poll()`, registered by `dasd_eer_init()` and removed by `dasd_eer_exit()`.

## Control Flow
Opening `/dev/dasd_eer` allocates an `eerbuffer`, validates the module parameter `eer_pages`, allocates page backing storage, attaches the buffer to `filp->private_data`, and links it into the global `bufferlist` under `bufferlock`. Closing removes it from the list and frees the pages.

When a DASD driver calls `dasd_eer_write()`, the function first checks whether EER is enabled for that device through `device->eer_cqr`. Standard triggers compute record size from the header plus any valid 32-byte sense buffers found along the CQR reference chain, then write the record to every open buffer and wake readers. Triggers without immediate sense data write only the header and `EOR` marker. State-change triggers are special: `dasd_eer_snss()` queues a preallocated SNSS request, and `dasd_eer_snss_cb()` writes the result or a header-only state-change record when the request completes.

Reads deliver complete records when possible but allow userspace to read a record in chunks. If a partial record is being delivered, `residual` tracks remaining bytes. If old records are discarded while a reader still has residual bytes, the residual is marked invalid and the next read fails with `-EIO`. Blocking reads wait on `dasd_eer_read_wait_queue`; nonblocking reads return `-EAGAIN`. `poll()` reports readable when head and tail differ.

## State and Persistence
All state is volatile. Global state consists of `eer_pages`, `bufferlist`, `bufferlock`, `dasd_eer_read_wait_queue`, a shared one-page `readbuffer`, and its mutex. Each open file has independent buffered history. Each EER-enabled DASD device owns one preallocated SNSS `dasd_ccw_req` in `device->eer_cqr`; the flags `DASD_FLAG_EER_IN_USE` and `DASD_FLAG_EER_SNSS` serialize and coalesce SNSS requests. No event data is persisted after readers close or the module exits.

## Dependencies and Integration Points
The file depends on the DASD core, ECKD SNSS command constant from `dasd_eckd.h`, miscdevice registration, file operations, wait queues, spinlocks, mutexes, EBCDIC-capable bus ids from ccw devices, and kernel timekeeping. It integrates with the broader DASD error path through exported symbols, `device->eer_cqr`, `device->ccw_queue`, `dasd_schedule_device_bh()`, and DASD trigger ids.

## Risks and Test Signals
Risk areas include global `bufferlock` contention across all readers and writers, record eviction while userspace reads partial records, unchecked return values from `dasd_eer_start_record()` in writer paths, very large or invalid `eer_pages` settings, SNSS disable races where an in-flight request must be freed by the callback, and the use of a single global read staging page protected by a mutex. Test signals include open/read/close leak checks, multiple independent readers receiving the same trigger, blocking and nonblocking read behavior, poll wakeups, partial-record reads followed by overwrite producing `-EIO`, enable rejection for non-ECKD or offline devices, SNSS coalescing under repeated state changes, and EER disable while SNSS is in flight.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_eer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_erp.c -->
# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_erp.c

## Purpose
This file provides the default DASD error-recovery primitives shared by DASD disciplines. It allocates ERP requests from per-device ERP memory, retries requests when no specialized recovery exists, collapses ERP chains back to the original request, and delegates sense-data logging to the active discipline.

## Important APIs, Types, and Functions
`dasd_alloc_erp_request()` and `dasd_free_erp_request()` manage `struct dasd_ccw_req` objects from `device->erp_chunks`. `dasd_default_erp_action()` is the generic retry action. `dasd_default_erp_postaction()` frees all ERP requests in a chain and transfers final success/failure state back to the original CQR. `dasd_log_sense()` handles user-visible sense logging, while `dasd_log_sense_dbf()` logs to s390 debug feature. The allocation, free, default action, default postaction, and sense logging helpers are exported.

## Control Flow
ERP allocation validates that data and CCW arrays fit within a page, computes an aligned object layout containing `dasd_ccw_req`, optional CCWs, and optional data, then allocates from the device ERP chunk pool under `device->mem_lock`. It initializes list heads, zeroes memory, stores the discipline magic after converting it to EBCDIC, sets `DASD_CQR_FLAGS_USE_ERP`, and takes a DASD device reference.

The default ERP action either resets a request to `DASD_CQR_FILLED` for retry, refreshing the path mask unless this is a path-verification request, or marks it failed when retries are exhausted. Postaction starts from the current ERP head, remembers final timing and start device, frees every ERP request until it reaches the original request (`refers == NULL`), and marks the original done or failed. Sense logging checks timeout and transport errors specially, then calls the discipline's `dump_sense` or `dump_sense_dbf` callback when available.

## State and Persistence
The file stores no global state. ERP request state lives in per-device chunk pools, CQR chains, CQR status fields, retry counters, path masks, and device references. There is no persistence beyond the lifetime of recovery processing.

## Dependencies and Integration Points
This file depends on DASD core request structures, per-device memory chunks, device refcounting, ccw layout, s390 debug support, EBCDIC conversion, and discipline callbacks. ECKD and FBA both select the default ERP postaction; FBA uses the default action directly, while ECKD chooses between 3990-specific and default ERP based on controller type.

## Risks and Test Signals
Risk areas include BUG_ON page-size assumptions for ERP payloads, matching every successful allocation with the device refcount decrement in `dasd_free_erp_request()`, preserving original request timing/status correctly while freeing a chain, and avoiding retries on stale path masks. Test signals include allocation failure paths, ERP chain cleanup with multiple linked requests, retry exhaustion logs, timeout and transport-error sense handling, discipline-specific dump callback invocation, and refcount/chunk leak checks under repeated recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_erp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_fba.c -->
# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_fba.c

## Purpose
This file implements the S/390 DASD FBA discipline and ccw driver for fixed-block architecture DASD devices. Compared with ECKD, it has a simpler linear block model: read device characteristics, expose one block device, build Define Extent plus Locate plus READ/WRITE channel programs, support discard/write-zeroes, and use default DASD ERP.

## Important APIs, Types, and Functions
The binding is `dasd_fba_driver` with `dasd_fba_ids`; the discipline is `dasd_fba_discipline`. Per-device state is `struct dasd_fba_private`, containing only `struct dasd_fba_characteristics`. Startup and geometry use `dasd_fba_check_characteristics()`, `dasd_fba_do_analysis()`, and `dasd_fba_fill_geometry()`. Channel-program helpers are `define_extent()`, `locate_record()`, `dasd_fba_build_cp_regular()`, `dasd_fba_build_cp_discard()`, and `dasd_fba_build_cp()`. Cleanup and diagnostics use `dasd_fba_free_cp()`, `dasd_fba_dump_sense()`, and `dasd_fba_dump_sense_dbf()`.

## Control Flow
Module init converts the discipline name to EBCDIC, allocates a DMA-capable zero page for discard workarounds, registers the ccw driver, and waits for probing. Online attaches the FBA discipline through the generic DASD online path.

`dasd_fba_check_characteristics()` allocates private state and a DASD block object, reads 32 bytes of FBA characteristics, sets default timeout/retries, marks all paths allowed with `LPM_ANYPATH`, sets read-only state when appropriate, enables the DASD discard feature bit, and logs capacity and block size. `dasd_fba_do_analysis()` validates the hardware block size, sets `block->blocks`, `bp_block`, and the 512-sector-to-block shift. Geometry uses a synthetic 16-head layout with sectors scaled by block size.

Normal read/write request building validates full-block bio segments, computes first and last logical records, decides whether IDALs are needed, allocates a CQR, writes a Define Extent for the requested range, emits one Locate Record for data-chaining devices or one per block for devices lacking data chaining, then emits one READ or WRITE CCW per block. Discard and write-zeroes requests are implemented as WRITE commands: unaligned leading/trailing parts write real zero data from `dasd_fba_zero_page`, while page-aligned middle ranges use a zero-length WRITE command that z/VM treats as block discard/zeroing.

## State and Persistence
State is volatile per-device private data plus the generic DASD block object. The zero page is global module state. FBA characteristics determine block count, block size, feature behavior, and data-chain behavior. Hardware state is affected only by normal write/discard I/O; the driver does not maintain persistent metadata.

## Dependencies and Integration Points
The file depends on the ccw bus, DASD core, block request iteration, IDAL helpers, DASD page-cache bounce buffering, generic path verification, and default ERP helpers. It integrates through `dasd_discipline` callbacks for analysis, I/O construction/freeing, max sectors, geometry, state-change detection, sense dumping, and information reporting. User-visible behavior is a standard DASD block device with discard support and FBA information from DASD ioctls.

## Risks and Test Signals
Risk areas include block-size validation, request segments that are not multiples of the FBA block size, IDAL and optional page-cache bounce cleanup, different Locate Record chaining for devices without data chaining, discard alignment workarounds for z/VM, and zero page lifetime. The init path currently frees the zero page only in cleanup; if `ccw_driver_register()` fails after zero-page allocation, the failure path should be checked for leakage. Test signals include probe on 3370/9336 IDs, readonly flag handling, blocksize rejection, read/write across multi-segment requests, devices with and without data chaining, IDAL-needed memory, page-cache bounce reads/writes, discard and write-zeroes for unaligned/aligned ranges, state-change attention handling, default ERP retry exhaustion, and sense dump output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_fba.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_fba.h -->
# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_fba.h

## Purpose
This header defines the fixed-block architecture DASD payloads used by `dasd_fba.c`: maximum request chaining, Define Extent data, Locate data, and the Read Device Characteristics layout for FBA devices.

## Important APIs, Types, and Functions
`DASD_FBA_MAX_BLOCKS` caps the number of blocks chained in one request. `struct DE_fba_data` is the FBA Define Extent payload with permissions, block size, extent locator, beginning block, and ending block. `struct LO_fba_data` is the Locate payload with operation nibble, auxiliary byte, block count, and block number. `struct dasd_fba_characteristics` maps the device characteristic data returned by the hardware, including mode bits such as data chaining, feature bits such as removable/shared/MAM, block size, blocks per cycle/boundary, base device size, and related controller fields.

## Control Flow
The header has no executable control flow. `dasd_fba.c` fills `DE_fba_data` before each request to define the logical extent and fills `LO_fba_data` before READ/WRITE commands to select the range inside that extent. The characteristics structure is populated by `dasd_generic_read_dev_chars()` during device check and drives later block-size, capacity, and data-chain decisions.

## State and Persistence
The structures describe transient channel-program payloads or cached hardware characteristics. They do not implement persistence. `dasd_fba_characteristics` becomes part of the device's in-memory private state and information ioctl output.

## Dependencies and Integration Points
The header relies on kernel fixed-width integer types provided by includers and is private to the DASD FBA discipline. It is coupled to s390 FBA channel command payload layouts and the generic DASD block/request model used by `dasd_fba.c`.

## Risks and Test Signals
The primary risks are packed-layout drift, incorrect bitfield interpretation, and mismatches between `DASD_FBA_MAX_BLOCKS` and the discipline's channel-program sizing assumptions. Test signals include successful characteristic reads, correct capacity calculation from `blk_bdsa` and `blk_size`, correct behavior on devices with `data_chain` clear or set, and compile/runtime validation that Define Extent and Locate payload sizes match the expected 16-byte and 8-byte CCW counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_fba.h -->
