# sources/distributed-fs/ceph-client/drivers/scsi/scsi_debug.c lines 1-8968

## Chunk Scope

This chunk covers the first 8,968 lines of `drivers/scsi/scsi_debug.c`, which is nearly the full Linux `scsi_debug` pseudo low-level SCSI adapter driver. The remaining file tail after this chunk contains the final queue-depth, timeout/failure, queuecommand, host-template, probe/remove, and bus-type glue, so this document intentionally focuses on the declarations, command emulation, storage model, state management, sysfs/debugfs/proc controls, initialization, and host/store lifecycle visible in this range.

## Purpose

`scsi_debug.c` implements an in-kernel synthetic SCSI host adapter for testing SCSI mid-layer, block-layer, error-handling, protection information, logical block provisioning, zoned block, tape, and queueing behavior without real hardware. It can expose one or more pseudo hosts, targets, and LUNs, optionally backed by RAM, and emulates many SPC/SBC/ZBC/SSC commands using a table-driven opcode dispatcher.

The driver is intentionally configurable and fault-injectable. Module parameters and driver sysfs attributes control host count, device size, fake vs RAM-backed I/O, queue depths, command latency, data-integrity modes, LBP/UNMAP behavior, ZBC model, tape device behavior, unit attentions, and injected errors. Debugfs files allow per-device command-error injection and per-target reset-failure injection.

## Core Types and Global State

The source defines SCSI sense constants, option bit masks, command flags, ZBC constants, tape block markers, default module parameters, and opcode metadata. The most important local types are:

- `struct opcode_info_t`: command dispatch metadata. Each entry stores opcode, optional service action, device-type selector, data direction/behavior flags, a response function pointer, optional sub-command array, and CDB length/mask data used for supported-opcode reporting and strict validation elsewhere in the file.
- `struct sdebug_dev_info`: per-logical-unit state. It tracks channel/target/LUN, LU UUID, owning host, unit-attention bitmap, stopped/not-ready state, ZBC zone state, tape partition/location/media fields, debugfs entry, and per-device RCU error-injection list.
- `struct sdebug_host_info`: per-pseudo-adapter state. It links into the global host list, records the backing-store xarray index, owns the `Scsi_Host`, owns the pseudo `struct device`, and holds the host's device-info list.
- `struct sdeb_store_info`: RAM backing store and metadata. It owns `storep` for data, `dif_storep` for T10 protection information, `map_storep` for logical block provisioning state, plus data/meta/sector rwlocks.
- `struct sdebug_defer` and `struct sdebug_scsi_cmd`: per-command private state used for delayed completions via hrtimer, workqueue, or blk-mq poll. Fields record completion timestamp, issuing CPU, defer type, and abort state.
- `struct sdebug_err_inject`: per-device debugfs error injection rule with type, count, command opcode, and extra result/sense fields for queuecommand failure or completed-command failure.
- `struct sdeb_zone_state`: per-zone ZBC type, condition, non-sequential-write flag, start, size, and write pointer.

Global state is extensive and mostly module-parameter-backed: `sdebug_num_hosts`, `sdebug_*` tunables, `sdeb_zbc_*` ZBC settings, queue timing settings, `sdebug_host_list`, `per_store_arr`, store indexes, global command/reset/stat counters, `writes_by_group_number`, `sdebug_debugfs_root`, and the pseudo driver/bus/root device objects.

## Command Dispatch Data

The chunk builds a table-driven command model:

- `opcode_ind_arr[256]` maps raw CDB opcode byte to a `SDEB_I_*` index.
- `opcode_info_arr[]` is the canonical command table. Entries cover INQUIRY, REPORT LUNS, REQUEST SENSE, TEST UNIT READY, MODE SENSE/SELECT, LOG SENSE, READ CAPACITY, READ/WRITE variants, START STOP UNIT, service-action commands, REPORT SUPPORTED OPERATION CODES/TMFs, UNMAP, WRITE SAME, COMPARE AND WRITE, PRE-FETCH, ZONE IN/OUT, ATOMIC WRITE, and SSC tape commands.
- Sub-arrays such as `read_iarr`, `write_iarr`, `vl_iarr`, `maint_in_iarr`, `zone_in_iarr`, and `zone_out_iarr` model service-action or opcode-family variants.
- Flags such as `F_D_IN`, `F_D_OUT`, `F_FAKE_RW`, `F_M_ACCESS`, `F_SKIP_UA`, `F_DELAY_OVERR`, and `F_SYNC_DELAY` encode data direction, media access, unit-attention behavior, fake-I/O eligibility, and timing overrides.

`resp_rsup_opcodes()` uses the same table to synthesize REPORT SUPPORTED OPERATION CODES output, so command support reporting and real dispatch share a single metadata source.

## Important APIs and Functions

### Sense and Buffer Helpers

- `mk_sense_buffer()`, `mk_sense_invalid_fld()`, `mk_sense_invalid_opcode()`, and `mk_sense_info_tape()` centralize sense construction. They honor `sdebug_dsense` except tape information sense, which is fixed-format in this chunk.
- `fill_from_dev_buffer()` and `p_fill_from_dev_buffer()` copy response data into the command's scatterlist and set residuals.
- `fetch_to_dev_buffer()` copies data-out buffers from initiator scatterlists.
- `make_ua()` converts the first pending per-LU unit-attention bit into sense data, clears it, and applies special LUNS CHANGED behavior depending on emulated SCSI level.

### Inquiry, VPD, Capacity, Mode/Log Pages

- `resp_inquiry()` builds standard INQUIRY and EVPD pages. It reports disk/tape/ZBC identity, version descriptors, protection support, TPGS behavior, VPD page lists, device identifiers, management addresses, SCSI ports, ATA info, block limits, block characteristics, logical block provisioning, ZBC characteristics, and block limits extension data.
- `inquiry_vpd_83()`, `_84()`, `_85()`, `_88()`, `_89()`, `_b0()`, `_b1()`, `_b2()`, `_b6()`, and `_b7()` are VPD-specific builders.
- `resp_readcap()` and `resp_readcap16()` report capacity, logical block size, physical block exponent, alignment, LBP bits, ZBC RC basis, and DIF protection fields. `get_sdebug_capacity()` allows `virtual_gb` to override RAM store size for non-ZBC use.
- `resp_mode_sense()` and mode-page helpers build direct-access, SAS, control, caching, informational exception, grouping, compression, and tape partition pages. It supports both 6- and 10-byte mode sense and handles block descriptors.
- `resp_mode_select()` accepts writable mode pages. It mutates global caching/control/informational-exception pages, write protect, descriptor sense, tape density/block size, tape compression, and pending tape partition parameters. It sets `SDEBUG_UA_MODE_CHANGED` when persistent emulated mode state changes.
- `resp_log_sense()` returns supported log pages, temperature, informational exception, and environmental reporting pages.

### Disk Data Path

- `devip2sip()` resolves a device to its backing `sdeb_store_info` or returns NULL for fake I/O. It BUGs if a caller that must not run under fake I/O asks for a store while `sdebug_fake_rw` is enabled.
- `do_device_access()` performs RAM-backed scatterlist copies for READ/WRITE operations, wraps LBAs modulo the finite RAM store, updates write counters by group number, and uses a simplified lock model: one atomic write or many non-atomic accesses plus per-sector read/write locks.
- `resp_read_dt0()` parses READ(6/10/12/16/32), XDWRITEREAD(10), validates protection and access constraints, injects short transfers and medium errors, optionally verifies/copies DIX/DIF protection data, copies backing-store bytes, and can inject recovered/DIF/DIX errors.
- `resp_write_dt0()` parses WRITE variants, validates protection and write constraints, verifies DIX/DIF, writes backing store, updates LBP map and ZBC write pointers, records group-number write stats, and handles injected recovered/protection errors.
- `resp_write_scat()` implements WRITE SCATTERED(16/32): fetches range descriptors from the front of the data-out buffer, validates each range, optionally verifies protection, atomically writes each listed range, updates LBP/ZBC metadata, and handles injected error modes.
- `resp_write_same_10()`, `resp_write_same_16()`, and `resp_write_same()` implement WRITE SAME and WRITE SAME with UNMAP/NDOB, using LBP unmap or one-sector replication.
- `resp_comp_write()` implements COMPARE AND WRITE by fetching compare+write payload, comparing the current store through `comp_write_worker()`, writing only on match, and setting MISCOMPARE sense on mismatch.
- `resp_verify()` implements VERIFY with BYTCHK handling, including BYTCHK=3 one-block-repeated compare.
- `resp_unmap()`, `resp_get_lba_status()`, `map_region()`, `unmap_region()`, `map_state()`, and LBA/map-index helpers maintain and report logical block provisioning state.
- `resp_sync_cache()` models immediate or delayed cache synchronization using the global `write_since_sync` flag.
- `resp_pre_fetch()` validates range and uses `prefetch_range()` on the RAM store before returning CONDITION MET.
- `resp_atomic_write()` validates the ATOMIC WRITE feature flag, alignment, granularity, boundary, and length constraints, then writes through `do_device_access(..., atomic=true)`.

### DIF/DIX Protection

Protection logic is integrated into reads and writes:

- `dif_compute_csum()` uses either IP checksum or CRC-T10DIF based on `sdebug_guard`.
- `dif_verify()` checks guard and reference tags for configured T10 PI type.
- `dif_copy_prot()` copies stored protection tuples between the backing metadata store and the command protection scatterlist.
- `prot_verify_read()` verifies store protection data for reads and then copies protection information to the initiator.
- `prot_verify_write()` walks data and protection scatterlists together, verifies protection tags unless WRPROTECT bypass is requested, copies protection information into `dif_storep`, and updates counters.

The code treats the driver as both initiator and target, so some protection cases verify even when a real target might only pass through information.

### Tape Emulation

When `sdebug_ptype == TYPE_TAPE`, device configuration allocates `TAPE_UNITS` `struct tape_block` entries. The chunk supports:

- `resp_read_tape()` and `resp_write_tape()` for READ(6)/WRITE(6), fixed and variable block modes, residual handling, filemark/EOD/EOP/ILI sense, and early warning.
- `resp_locate()`, `resp_space()`, `resp_read_position()`, and `resp_rewind()` for tape positioning.
- `resp_write_filemarks()`, `resp_format_medium()`, `resp_erase()`, `partition_tape()`, and `process_medium_part_m_pg()` for marks, erase, formatting, and partition state.
- `scsi_tape_reset_clear()` resets tape density, block size, current partition, compression, position, and pending partition state on resets.

Tape media data is sparse/minimal: each block stores only a size/mark word and 4 bytes of data, so this is a behavioral simulator rather than full tape payload persistence.

### ZBC/Zoned Emulation

ZBC state is per `sdebug_dev_info`:

- `sdebug_device_create_zones()` derives zone size/capacity, conventional and sequential counts, optional gap zones, max-open limit, and initializes every `sdeb_zone_state`.
- `zbc_zone()` maps LBA to zone, accounting for gap zones when zone capacity is smaller than zone size.
- `check_zbc_access_params()` enforces host-managed/read/write rules: reads cannot cross zone-type boundaries, writes cannot target gaps, writes to conventional zones cannot cross into sequential zones, sequential-write-required zones must write at the write pointer and not cross zone boundaries, and empty/closed zones may be implicitly opened within resource limits.
- `zbc_open_zone()`, `zbc_close_zone()`, `zbc_set_zone_full()`, and `zbc_inc_wp()` maintain open/closed/full counts and write pointers.
- `resp_report_zones()` reports zone descriptors filtered by reporting options.
- `resp_open_zone()`, `resp_close_zone()`, `resp_finish_zone()`, and `resp_rwp_zone()` implement ZONE OUT service actions over one zone or all zones.

These functions are protected by metadata locks when they read or mutate zone state.

### Device, Target, Host, Store Lifecycle

- `sdebug_target_alloc()` allocates target-private state, creates a debugfs directory, and exposes `fail_reset`. `sdebug_target_destroy()` schedules asynchronous debugfs removal/freeing on `sdebug_async_domain`.
- `sdebug_device_create()` allocates reusable `sdebug_dev_info` slots, assigns UUIDs depending on `uuid_ctl`, creates ZBC zones if enabled, initializes tape defaults, records creation time, initializes `stopped` for `tur_ms_to_ready`, and links into the host device list.
- `find_build_dev_info()` finds an existing used device slot matching channel/target/LUN, reuses an unused slot, or allocates a new one. It sets POWER ON OCCURRED unit attention on new associations.
- `scsi_debug_sdev_configure()` ensures `hostdata` is populated, initializes tape media, applies CDB length preferences, sets `no_uld_attach` and `allow_restart`, and creates per-device debugfs `error` injection file.
- `scsi_debug_sdev_destroy()` clears injection rules with RCU callbacks, removes debugfs, frees tape block storage, marks the reusable device slot unused, and clears `sdp->hostdata`.
- `sdebug_add_store()` allocates an xarray store entry, RAM disk storage, optional partition table, optional DIF metadata, optional LBP bitmap, and initializes locks.
- `sdebug_erase_store()` and `sdebug_erase_all_stores()` free store memory and remove xarray entries.
- `sdebug_add_host_helper()` creates a host-info object, preallocates device-info slots based on `num_tgts * max_luns`, links it into the global host list, registers the pseudo adapter device, and increments host count.
- `sdebug_do_add_host()` optionally creates a new store and then adds a host.
- `sdebug_do_remove_host()` begins host removal by selecting the newest host, marking a unique per-host store as not-in-use for possible reuse when not in final shutdown, unlinking the host from the global list, and then continuing outside the chunk into the tail for device unregister/scsi host cleanup.

### Timing, Abort, Reset, and Deferred Completion

- `schedule_resp()` is the convergence point for response execution and completion scheduling. It handles missing device state, immediate responses, command response invocation, injected TASK SET FULL, transport-error injection, command-abort injection, random or fixed delay, high-resolution timers, workqueue completions, and polled completions.
- `sdebug_q_cmd_complete()`, `sdebug_q_cmd_hrt_complete()`, and `sdebug_q_cmd_wq_complete()` complete deferred commands via `scsi_done()` unless the command was marked aborted, in which case they call `blk_abort_request()`.
- `scsi_debug_stop_cmnd()` cancels hrtimers/work items/polled completions where possible.
- `scsi_debug_abort_cmnd()` uses reserved internal command infrastructure to request cancellation by unique tag.
- `stop_all_queued()` and `scsi_debug_stop_all_queued()` iterate busy blk-mq tags for all hosts or one device and submit aborts.
- `scsi_debug_abort()`, `scsi_debug_device_reset()`, `scsi_debug_target_reset()`, `scsi_debug_bus_reset()`, and `scsi_debug_host_reset()` update counters, optionally print noise, set unit attentions, reset tape state, stop queued work at the relevant scope, and consult injection/debugfs controls for forced failures.

### User-Facing Controls

The chunk defines many `module_param_named()` and `MODULE_PARM_DESC()` entries. It also defines driver attributes under `/sys/bus/pseudo/drivers/scsi_debug`, collected in `sdebug_drv_attrs`, with richer side effects than raw module parameters:

- Timing: `delay`, `ndelay`, `random`.
- Error/fault controls: `opts`, `every_nth`, `statistics`, `group_number_stats`.
- Topology and capacity: `add_host`, `num_tgts`, `max_luns`, `lun_format`, `virtual_gb`, `per_host_store`.
- Behavior toggles: `ptype`, `dsense`, `fake_rw`, `no_lun_0`, `no_rwlock`, `vpd_use_hostno`, `removable`, `host_lock`, `strict`, `cdb_len`.
- Read-only or fixed-at-init views: `dev_size_mb`, `num_parts`, `host_max_queue`, `no_uld`, `scsi_level`, `sector_size`, `submit_queues`, `dif`, `dix`, `guard`, `ato`, `uuid_ctl`, `tur_ms_to_ready`, `zbc`, `map`.

`scsi_debug_show_info()` emits proc-style diagnostics including parameters, reset counters, protection counters, queue stats, busy tag ranges by submit queue, host list, and per-store xarray state. `scsi_debug_write_info()` lets privileged users update `opts` through `/proc/scsi/scsi_debug/<host_id>`.

## Control Flow

Initialization in `scsi_debug_init()` validates parameters, normalizes timing, sector size, DIF/guard/ATO/LUN format/queue limits/ZBC mode, computes store sectors and capacity, derives BIOS-like geometry, clamps LBP settings, initializes the store xarray, optionally allocates the initial store, registers the pseudo root device, bus, and driver, creates debugfs root, and adds the requested number of hosts.

Runtime command flow visible in this chunk is:

1. A SCSI command is matched in the later queuecommand path against `opcode_ind_arr` and `opcode_info_arr`.
2. The selected response function and initial result are passed to `schedule_resp()`.
3. `schedule_resp()` may execute the response immediately in the submission thread or before scheduling a deferred completion.
4. Response functions parse the CDB, validate CDB fields, device type, access ranges, unit state, ZBC/LBP/protection constraints, and data direction.
5. Data-in responses copy synthetic buffers to the SCSI scatterlist; data-out commands fetch from the scatterlist into RAM store or command-specific buffers.
6. If delayed, completion is represented by `sdebug_defer` as hrtimer, workqueue, or poll state; otherwise `scsi_done()` is called in-thread.
7. Error injection can change queue behavior, completed result, timeout/abort/reset behavior, transport sense, short transfer, medium error, protection error, or TASK SET FULL behavior depending on global `opts`, `every_nth`, and per-device debugfs rules.

Host/device lifecycle flow is:

1. `scsi_debug_init()` registers pseudo infrastructure and calls `sdebug_add_host_helper()` or `sdebug_do_add_host()`.
2. Host helper preallocates reusable `sdebug_dev_info` slots and registers an adapter device on the pseudo bus.
3. The later probe path creates a `Scsi_Host`; device scanning invokes `scsi_debug_sdev_configure()`.
4. Device configure binds a `sdebug_dev_info` to the `scsi_device`, initializes optional tape state, and creates debugfs files.
5. Destroy/removal clears debugfs and marks slots reusable; final exit removes hosts, unregisters driver/bus/root, erases stores, destroys xarray, and removes debugfs root.

## State and Persistence Behavior

All device data is volatile kernel memory. There is no persistence across module unload/reload.

RAM-backed data lives in `sdeb_store_info.storep`. Multiple hosts may share one store, or new hosts may get per-host stores depending on `fake_rw` and `per_host_store`. When `fake_rw` is enabled, media I/O can be skipped and store-backed functions must not run. Store indexes are managed in `per_store_arr`, with `SDEB_XA_NOT_IN_USE` marking reusable per-host stores after host removal.

LBP state lives in `map_storep`, a bitmap whose granularity/alignment comes from module parameters. Writes call `map_region()`, UNMAP clears bits through `unmap_region()`, and unmapped data may be zeroed or filled with `0xff` depending on `lbprz`.

DIF/DIX state lives in `dif_storep`, parallel to logical blocks. Reads and writes copy/check this metadata through protection scatterlists when enabled.

ZBC state is per device, not per store. Zone conditions, write pointers, open counts, and non-sequential resource flags mutate with writes and ZONE OUT commands.

Tape state is per device: partitioning, current partition, location per partition, density, block size, compression bit, and allocated `tape_blocks`. Tape block payload is intentionally minimal.

Unit attentions are per device in `uas_bm`; mode select, capacity changes, LUN format/LUN count changes, reset paths, microcode write-buffer modes, device creation, and ready transitions set bits that are consumed by later command handling.

Global mutable state includes response timing, options, statistics counters, reset counters, write-since-sync, mode pages, write protect, and shared UUID state. Several sysfs stores mutate global settings while devices are live, sometimes with queue blocking or busy checks.

## Dependencies and Integration Points

The file integrates tightly with Linux kernel SCSI and block APIs:

- SCSI mid-layer: `struct scsi_cmnd`, `struct scsi_device`, `struct Scsi_Host`, `scsi_done()`, sense helpers, queue-depth and host template callbacks in the tail.
- Block layer/blk-mq: request tags, busy iteration, reserved internal commands, polled requests, queue blocking/unblocking.
- Scatterlist APIs: `sg_copy_buffer`, `scsi_sg_copy_to_buffer`, protection scatterlists, `sg_mapping_iter`.
- Kernel storage/protection helpers: `crc_t10dif`, `ip_compute_csum`, T10 PI tuple layout.
- Kernel infrastructure: `module_param`, driver attributes, debugfs, proc/seq_file output, xarray, hrtimer, workqueue, async domain, root device and bus registration, RCU, spinlocks, rwlocks, atomics, random number generation, and `prefetch_range`.
- SCSI standards headers and constants from `<scsi/scsi.h>`, `<scsi/scsi_cmnd.h>`, `<scsi/scsi_device.h>`, `<scsi/scsi_host.h>`, `<scsi/scsi_eh.h>`, `<scsi/scsi_tcq.h>`, and local `sd.h`/`scsi_logging.h`.

External user-visible integration points include module parameters under `/sys/module/scsi_debug/parameters`, driver attributes under `/sys/bus/pseudo/drivers/scsi_debug`, proc output under `/proc/scsi/scsi_debug`, debugfs under `scsi_debug`, SCSI scan paths, and block devices attached by upper-level drivers unless `no_uld` is set.

## Risks and Review Notes

- This file intentionally has many global mutable parameters. Runtime sysfs writes can affect all devices, while per-device state persists across reusable `sdebug_dev_info` slots; changes need careful UA and locking treatment.
- Several paths use `BUG_ON()` for invariants such as fake-RW misuse, malformed UNMAP payloads, and protection scatterlist assumptions. That is acceptable for a debug driver but high-impact if reachable from untrusted inputs.
- `sdebug_no_rwlock` bypasses actual locking while preserving sparse annotations, so data-race behavior is intentionally user-selectable.
- `comp_write_worker()` returns boolean comparison/write success and handles wraparound store access manually; changes here risk subtle compare-and-write and VERIFY regressions.
- ZBC zone capacity smaller than zone size introduces gap zones and adjusted LBA-to-zone mapping; write-boundary and report-zones behavior is easy to break.
- Tape behavior uses simplified payload storage and many position/sense edge cases. Regression tests should emphasize residuals and filemark/EOD/EOP sense.
- The LBP map and store bytes are updated under metadata/data locks in some commands, but lock ordering varies by command. Any new operation touching data, map, DIF, or ZBC state must preserve ordering to avoid deadlocks.
- `schedule_resp()` mixes response execution, injected result changes, timing policy, polled completion state, and abort injection. Small changes can affect timeout, abort, and completion ordering semantics.
- `add_host_store()`, `fake_rw_store()`, and host/store removal share xarray marks and store indexes. Per-host-store reuse is a sensitive lifecycle area, especially around partial add failures.
- This chunk ends in the middle of `sdebug_do_remove_host()`. Full host teardown correctness depends on the tail chunk.

## Test Signals

Useful test coverage and runtime signals for this chunk include:

- Load/unload `scsi_debug` with default options and with combinations of `dev_size_mb`, `sector_size`, `num_tgts`, `max_luns`, `submit_queues`, `fake_rw`, `per_host_store`, and `no_uld`.
- Exercise `/sys/bus/pseudo/drivers/scsi_debug/add_host` for positive and negative host deltas, including per-host-store reuse.
- Run `sg_inq`, EVPD page queries, `sg_readcap`, `sg_modes`, `sg_logs`, REPORT LUNS, REPORT SUPPORTED OPERATION CODES, and REPORT SUPPORTED TMFs against disk, tape, and ZBC modes.
- Run read/write/verify/compare-and-write/write-same/write-scattered workloads and confirm residuals, data persistence, group-number stats, and protection behavior.
- Test `lbpu/lbpws/lbpws10` with `sg_unmap` and GET LBA STATUS; inspect `map` attribute.
- Test DIF/DIX modes with valid and invalid guard/reference tags; watch `dix_reads`, `dix_writes`, and `dif_errors`.
- Test ZBC with host-aware and host-managed modes: REPORT ZONES filters, sequential write-pointer enforcement, OPEN/CLOSE/FINISH/RESET WRITE POINTER, max-open exhaustion, gap-zone errors, and reads crossing zone type boundaries.
- Test tape ptype with READ/WRITE(6), LOCATE, SPACE, READ POSITION, WRITE FILEMARKS, FORMAT MEDIUM, ERASE, mode select partition/compression pages, and resets.
- Use debugfs `error` to inject timeout, queue failure, completed-command failure, abort failure, and LUN reset failure; use target `fail_reset` for target reset failures.
- Use `opts` and `every_nth` to trigger medium errors, short transfers, recovered errors, transport errors, TASK SET FULL, host busy, command abort, and unaligned write injection.
- Validate delayed completion modes: `delay=0`, positive jiffy delay, `ndelay`, negative delay/workqueue, random delay, polled queues, aborts, and reset while commands are outstanding.
- Inspect `/proc/scsi/scsi_debug/<host>` and driver attributes for counters, busy tags, host/store lists, reset counts, and parameter reflection.
