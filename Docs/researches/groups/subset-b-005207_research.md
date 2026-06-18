# subset-b-005207 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_genhd.c -->
# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_genhd.c

Purpose: provides the DASD driver's Linux block-device registration glue: disk naming, blk-mq tag-set/disk allocation, major registration, readonly propagation, and partition scan/destruction helpers.

Important APIs/types/functions: `dasd_name_format()` generates `dasda...` names from `devindex`; `dasd_gendisk_alloc()` configures `struct blk_mq_tag_set`, queue limits, `struct gendisk`, minors, `dasd_device_operations`, sysfs links, and `device_add_disk()`; `dasd_gendisk_free()` tears down disk/tag state; `dasd_scan_partitions()` opens the whole disk and calls `bdev_disk_changed()`; `dasd_destroy_partitions()` forces partition invalidation and drops the scan-time open; `dasd_gendisk_init()`/`exit()` register major 94.

Control flow: a DASD block object reaches this file during online setup. The code allocates blk-mq resources, assigns the fixed DASD major/minor range, derives the disk name, marks readonly if the device or feature map says so, publishes the disk, then later scans partitions by temporarily opening the disk. Offline paths remove partitions before freeing the disk and tag set.

State and persistence behavior: persistent state is kernel block-layer state only: `block->gdp`, `block->tag_set`, and `block->bdev_file`. `queue_depth` and `nr_hw_queues` are read-only module parameters for newly allocated disks. No on-disk metadata is changed here.

Dependencies and integration points: depends on Linux blk-mq, gendisk, partition rescan, DASD devmap/indexing, `dasd_mq_ops`, `dasd_device_operations`, and ccw device parent objects.

Risks and test signals: name formatting and minor exhaustion must be tested near `DASD_PER_MAJOR`; error paths must free tag sets exactly once. Partition scan/offline race behavior hinges on `block->bdev_file` and open-count accounting. Test with readonly devices, failed `blk_mq_alloc_disk()`, failed `device_add_disk()`, hot offline while partition scanning, and high devindex values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_genhd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_int.h -->
# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_int.h

Purpose: central internal contract for the DASD subsystem. It defines DASD device states, request structures, discipline callbacks, block/device state containers, profiling data, stop/flag bits, chunk allocators, path-state helpers, and cross-file prototypes.

Important APIs/types/functions: key structures are `struct dasd_ccw_req`, `struct dasd_discipline`, `struct dasd_device`, `struct dasd_block`, `struct dasd_path`, `struct dasd_profile`, and copy-relation structs. Important helpers include `dasd_get_device()`/`dasd_put_device()`, static chunk-list alloc/free helpers, `dasd_check_blocksize()`, `dasd_get_callback_data()`, EER stubs/entry points, and the many `dasd_path_*` bitmask helpers.

Control flow: no standalone runtime loop lives here, but the header encodes the subsystem state machine from `NEW` through `ONLINE` and the callback table that each discipline uses for probing, analysis, I/O building, formatting, ERP, ESE, PPRC, path events, and info/ioctl handling. Inline path helpers mutate per-channel flags and aggregate path masks used by the core and disciplines.

State and persistence behavior: state is in-memory per-device/per-block state: CCW queues, timers, tasklets/work items, path flags, refcounts, profile counters, copy-pair metadata, and feature bits copied from devmap. Persistent media changes are delegated to discipline operations such as format, release-space, and copy-pair swap.

Dependencies and integration points: binds DASD core, devmap, gendisk, ioctl, proc, ERP, EER, ECKD/FBA/DIAG disciplines, s390 ccw/cio APIs, debugfs/s390 debug, blk-mq, and userspace ABI structs from `asm/dasd.h`.

Risks and test signals: macro/inline helpers are widely shared, so path-bit changes can affect failover, HPF disablement, FC security reporting, and path verification. Static chunk allocators require lock discipline by callers. Compile coverage across `CONFIG_DASD_EER` and `CONFIG_DASD_PROFILE`, path failover tests, reference-count leak checks, and blocksize boundary tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_ioctl.c

Purpose: implements the DASD block-device ioctl surface for administrative actions, formatting, format checking, ESE space release, copy-pair swap, profiling, CMB data, API version reporting, and exported DASD information.

Important APIs/types/functions: `dasd_ioctl()` dispatches `BIODASD*` and `DASDAPIVER` commands; helpers cover enable/disable, quiesce/resume, `abortio`/`allowio`, `dasd_format()`, `dasd_check_format()`, `dasd_ioctl_release_space()`, `dasd_ioctl_copy_pair_swap()`, profile reset/read, `__dasd_ioctl_information()`, `dasd_set_read_only()`, `dasd_ioctl_readall_cmb()`, and exported `dasd_biodasdinfo()`.

Control flow: ioctls first resolve the `dasd_device` from the gendisk and then enforce capability, whole-disk, readonly, and user-buffer checks as needed. Most operations delegate to discipline callbacks. Disable deliberately lowers the target state to `BASIC` so `dasdfmt` can still issue format I/O. Information paths combine discipline data with ccw identifiers, state, open counts, and queue length.

State and persistence behavior: quiesce/resume adjust stop bits, abort/allow toggles `DASD_FLAG_ABORTALL`, disable changes target state and disk capacity, formatting and ESE release can mutate media, copy-pair swap mutates copy relation state, readonly changes devmap features unless hardware readonly blocks it, and profiling ioctls read/reset in-memory counters.

Dependencies and integration points: depends on DASD discipline callbacks, Linux block ioctl conventions, `CAP_SYS_ADMIN`, ccw/CMB APIs, `copy_{to,from}_user()`, partition detection consumers via exported `dasd_biodasdinfo()`, and userspace tools such as `dasdfmt`.

Risks and test signals: user pointer and partition rejection paths are security-sensitive. `dasd_release_space()` uses `if (!device->discipline->is_ese && !device->discipline->is_ese(device))`, which risks a NULL callback call and looks intended to be an OR-style guard. Test privileged/unprivileged callers, partition vs whole disk, readonly media, malformed reserved copy-pair data, profile-disabled builds, CMB size variants, and ESE/non-ESE devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_proc.c -->
# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_proc.c

Purpose: provides the legacy `/proc/dasd` interface, listing DASD devices and exposing global profiling statistics controls/output when profiling is configured.

Important APIs/types/functions: `dasd_devices_show()` is the seq-file renderer for `/proc/dasd/devices`; `dasd_devices_seq_ops` iterates devindices; profile helpers switch all block profiles on/off/reset; `dasd_stats_proc_show()` prints histograms; `dasd_stats_proc_write()` parses `set on`, `set off`, and `reset`; `dasd_proc_init()`/`exit()` create/remove proc entries.

Control flow: proc init creates `/proc/dasd`, `devices`, and `statistics`. Device listing iterates up to `dasd_max_devindex`, obtains referenced devices, prints ccw name, discipline, major/minor, disk name, features, and state/capacity. Statistics reads snapshot the global profile under lock; writes parse a bounded copied string and update global plus per-block profile state.

State and persistence behavior: proc files are runtime-only. Writing statistics toggles in-memory profiling and resets counters; it does not persist configuration across boot. Device listing reflects live DASD state and devmap configuration.

Dependencies and integration points: integrates with DASD devmap lookup, profile support in `dasd.c`, procfs/seq_file, user-copy helpers, and the global `dasd_probeonly`/`dasd_max_devindex` knobs.

Risks and test signals: profile writes can partially enable block profiles before a later failure, so rollback behavior matters. Device iteration must drop references on every path. Test with holes in devindex space, devices without `block`/`gdp`, `CONFIG_DASD_PROFILE=n`, oversized writes, parse errors, and concurrent online/offline while reading proc files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dasd_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dcssblk.c -->
# sources/distributed-fs/ceph-client/drivers/s390/block/dcssblk.c

Purpose: implements the s390 DCSS memory block driver. It lets users load named DCSS segments through sysfs, expose them as no-partition block disks, optionally enable DAX for aligned ranges, switch shared/exclusive access, save modified segments, and remove devices.

Important APIs/types/functions: `struct dcssblk_dev_info` tracks one block device and segment list; `struct segment_info` tracks each loaded DCSS. Sysfs stores are `dcssblk_add_store()`, `dcssblk_remove_store()`, `dcssblk_shared_store()`, and `dcssblk_save_store()`. I/O paths are `dcssblk_open()`, `dcssblk_release()`, `dcssblk_submit_bio()`, `dcssblk_dax_direct_access()`, and `dcssblk_dax_zero_page_range()`.

Control flow: init registers a root device, `add`/`remove` files, a dynamic block major, and loads module-param segments. Add parses colon-separated segment sets, loads each segment shared, checks uniqueness/continuity/type compatibility, allocates a disk, registers a device, maps DAX if subsection-aligned, adds the disk, and sets readonly based on segment type. Remove requires idle use count, unloads segments, removes DAX/disk/device state, and frees resources.

State and persistence behavior: runtime state is the protected `dcssblk_devices` list, per-device use count, `is_shared`, `save_pending`, loaded segment ranges, DAX mapping, and gendisk. `save` persists segment contents only for savable segment types. Shared/exclusive mode changes are live segment access-mode changes.

Dependencies and integration points: depends on s390 `extmem` segment APIs, block layer bio submission, DAX/dev_pagemap, root devices/sysfs, semaphores, direct kernel virtual mappings of DCSS ranges, and module parameter parsing.

Risks and test signals: I/O requires sector and bio segment page alignment; misaligned bios fail. Shared-mode write checks depend on segment type. Error paths mix device, DAX, pgmap, disk, module ref, and segment unload cleanup. Test multi-segment continuity/type mismatch, duplicate names, DAX-aligned and unaligned segments, busy remove/save, shared-to-exclusive failures, readonly writes, and parameter parsing with `(local)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/dcssblk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/scm_blk.c -->
# sources/distributed-fs/ceph-client/drivers/s390/block/scm_blk.c

Purpose: implements the blk-mq block driver for s390 storage class memory increments, batching block requests into EADM asynchronous operation blocks with MSB/AIDAW descriptors.

Important APIs/types/functions: global pools are `inactive_requests` and `aidaw_pool`; `struct scm_request` wraps an AOB and request array. Key functions include `scm_alloc_rqs()`, `scm_request_fetch()`/`done()`, `scm_request_prepare()`, `scm_blk_request()`, `scm_blk_irq()`, `scm_blk_handle_error()`, `scm_blk_dev_setup()`, `scm_blk_dev_cleanup()`, `scm_blk_set_available()`, and module init/exit.

Control flow: module init registers a dynamic major, preallocates request/AIDAW resources, sets up s390 debug, and registers the SCM bus driver. Per-device setup allocates a blk-mq tag set and disk. Queueing aggregates up to `nr_requests_per_io` block requests into one AOB, maps pages through AIDAWs, starts EADM, and completes/requeues original requests from the interrupt callback.

State and persistence behavior: persistent state is block-layer device state only. Runtime state includes preallocated request objects, queued request counts, per-device `SCM_OPER` vs `SCM_WR_PROHIBIT`, pending hctx aggregate request, and debug logs. Write-prohibited state is set after an EADM response and cleared by SCM availability notification.

Dependencies and integration points: integrates blk-mq with s390 EADM (`eadm_start_aob`, `struct aob/msb/aidaw`), the SCM bus driver in `scm_drv.c`, s390 debug, DMA64 address conversion, mempools, and Linux request completion/requeue APIs.

Risks and test signals: request pooling bounds throughput and can return `BLK_STS_RESOURCE`; AIDAW capacity must match queue limits; `nr_requests_per_io` is limited to 1..64 but `nr_requests` can stress memory. Test read/write batches, resource exhaustion, fake timeouts, write-prohibited responses, availability recovery, hot remove with queued I/O, and init failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/scm_blk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/scm_blk.h -->
# sources/distributed-fs/ceph-client/drivers/s390/block/scm_blk.h

Purpose: shared header for the SCM block driver, defining per-device/request state, exported setup/cleanup/interrupt contracts, and debug logging helpers.

Important APIs/types/functions: `struct scm_blk_dev` contains request queue, gendisk, tag set, SCM device, lock, queued count, state, and finished list. `struct scm_request` contains AOB/AIDAW batching state and original request pointers. Public functions include `scm_blk_dev_setup()`, `scm_blk_dev_cleanup()`, `scm_blk_set_available()`, `scm_blk_irq()`, `scm_aidaw_fetch()`, `scm_drv_init()`, and `scm_drv_cleanup()`.

Control flow: the header has no independent runtime flow; it defines the seam between the SCM bus-facing driver (`scm_drv.c`) and the block queue implementation (`scm_blk.c`). `SCM_LOG_STATE()` packages SCM address, operational state, and rank for debug traces.

State and persistence behavior: all state is volatile per-device or per-request block I/O state. The enum `SCM_OPER`/`SCM_WR_PROHIBIT` controls whether writes are accepted.

Dependencies and integration points: depends on blkdev/blk-mq, spinlocks, lists, interrupts, s390 EADM definitions, and s390 debug feature.

Risks and test signals: structure layout is shared across files and interrupt callbacks, so mismatched assumptions break completions. Compile tests plus probe/remove/notify tests validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/scm_blk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/scm_drv.c -->
# sources/distributed-fs/ceph-client/drivers/s390/block/scm_drv.c

Purpose: provides the SCM bus driver binding for the SCM block driver: probe, remove, event notify, and EADM interrupt handler registration.

Important APIs/types/functions: `scm_notify()` handles `SCM_CHANGE` and `SCM_AVAIL`; `scm_probe()` validates operational state, allocates `struct scm_blk_dev`, and calls `scm_blk_dev_setup()`; `scm_remove()` calls block cleanup and frees state; `scm_drv` supplies `.notify`, `.probe`, `.remove`, and `.handler = scm_blk_irq`; `scm_drv_init()`/`cleanup()` register/unregister.

Control flow: module init in `scm_blk.c` calls `scm_drv_init()`. For each good SCM increment, probe stores driver data and creates a block disk. Availability notifications restore write access through `scm_blk_set_available()`. Removal tears down the disk and clears driver data.

State and persistence behavior: maintains only per-device driver data pointer and block-device lifetime. SCM hardware capability changes are logged but not persisted.

Dependencies and integration points: depends on the s390 SCM driver model (`struct scm_driver`, `scm_driver_register()`), EADM event delivery, and the block implementation exported by `scm_blk.c`.

Risks and test signals: probe rejects non-good operational state; notify assumes driver data exists for availability events. Test probe failure cleanup, remove after partial setup failure, `SCM_AVAIL` recovery from write-prohibited mode, and event logging for capability changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/block/scm_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/s390/char/Kconfig

Purpose: defines configuration symbols for s390 character-device drivers, including 3215/3270 terminals, SCLP tty/console variants, HMC drive FTP support, UV userspace API, tape, z/VM monitor/CP/unit-record drivers, and crash dump support dependencies.

Important APIs/types/functions: Kconfig symbols include `TN3270`, `TN3270_FS`, `TN3270_CONSOLE`, `TN3215`, `TN3215_CONSOLE`, `CCW_CONSOLE`, `SCLP_TTY`, `SCLP_CONSOLE`, `SCLP_VT220_TTY`, `SCLP_VT220_CONSOLE`, `HMC_DRV`, `S390_UV_UAPI`, `S390_TAPE`, `VMLOGRDR`, `VMCP`, `VMCP_CMA_SIZE`, `MONREADER`, `MONWRITER`, and `S390_VMUR`.

Control flow: no runtime flow. Configuration choices determine which objects the adjacent Makefile builds and whether terminal/console paths are built in or modular.

State and persistence behavior: the generated kernel `.config` is the only state. Defaults bias many platform facilities to built-in or module when dependencies are available.

Dependencies and integration points: integrates with CCW, TTY, S390, IUCV, CMA, CRC16, and terminal console selections. `HMC_DRV` selects `CRC16` for FTP command parsing.

Risks and test signals: console symbols require built-in availability in some cases, especially `TN3270_CONSOLE` depending on `TN3270=y`. Test allmodconfig, built-in console configs, dependency-disabled configs, and modular HMC/tape/vm drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/Makefile -->
# sources/distributed-fs/ceph-client/drivers/s390/char/Makefile

Purpose: maps s390 character-driver Kconfig symbols to Kbuild objects and applies sanitizer/tracing exclusions for early SCLP code.

Important APIs/types/functions: always-built objects include `ctrlchar.o`, `keyboard.o`, `defkeymap.o`, and core SCLP objects. Conditional entries build 3270/3215 tty/fullscreen, SCLP terminal variants, tape composite `tape_s390.o`, VM and monitor drivers, crash dump helpers, UV device, and the composite `hmcdrv.o`.

Control flow: no runtime behavior. Kbuild evaluates `obj-*`, composite object lists, and per-object flags. `hmcdrv-objs` links module core, misc device, FTP parser/cache, DIAG backend, and SCLP backend.

State and persistence behavior: build graph only; no runtime state.

Dependencies and integration points: ties Kconfig selections to source files. Early SCLP core disables ftrace, gcov, kcov, UBSAN, KASAN, fortify, and expoline flags where needed for boot constraints.

Risks and test signals: object-list drift breaks link-time symbol resolution, especially composite `hmcdrv` and `tape_s390`. Test built-in and modular combinations for terminal, HMC, tape, and crash-dump configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/con3215.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/con3215.c

Purpose: implements the IBM 3215 line-mode terminal as a CCW-backed tty and optional console, including output buffering, read attention handling, sysrq/control-character handling, and panic/reboot flushing.

Important APIs/types/functions: `struct raw3215_info` holds tty port, ccw device, circular output buffer, input buffer, queues, flags, wait queue, timer, and line position. `struct raw3215_req` holds CCW chains. Key functions include request allocation, `raw3215_mk_read_req()`, `raw3215_mk_write_req()`, `raw3215_start_io()`, `raw3215_irq()`, `raw3215_write()`, startup/shutdown/probe/remove, tty ops, `con3215_write()`, and `con3215_notify()`.

Control flow: console init can create the console ccw device early and register a console. TTY init registers the ccw driver and `ttyS` driver. Writes expand tabs, convert ASCII to EBCDIC, append to a ring, build write CCWs, and start immediately or after a timer. Attention interrupts queue reads; read completions convert EBCDIC to ASCII and feed tty flip buffers or sysrq/control characters.

State and persistence behavior: state is runtime-only: one `raw3215` slot, freelist of request structs, circular buffers, throttled/stopped/timer/flush flags, and `con3215_drop` from early param/sysfs. No terminal data persists.

Dependencies and integration points: integrates CCW device model, tty core, console subsystem, panic/reboot notifiers, EBCDIC conversion tables, z/VM `cpcmd` console mode setup, and `ctrlchar_handle()`.

Risks and test signals: `raw3215_alloc_req()` assumes freelist availability; buffer-full behavior can drop output when `con3215_drop` is enabled or busy-wait otherwise. Panic notifier uses trylock to avoid deadlock. Test console and tty mode, throttling/unthrottling, stopped output, large writes with tabs/newlines, sysrq/control sequences, VM console mode, buffer pressure, and panic/reboot flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/con3215.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/con3270.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/con3270.c

Purpose: implements IBM 3270 tty and optional console views on top of `raw3270`, translating tty output and ANSI-like escape sequences into 3270 screen orders while handling input, recall, scrolling history, resize, and console panic flushing.

Important APIs/types/functions: `struct tty3270` contains raw view, tty port, write/read requests, timer, screen ring, attributes, prompt/input/status state, tasklets, keyboard data, escape parser, recall lines, and char buffer. Key functions include update builders, `tty3270_update()`, read tasklet/callback, `tty3270_irq()`, view allocation/free/resize, install/open/cleanup, escape parser, tty write/put/termios/throttle/ioctl ops, console write/notify/init, and notifier callbacks.

Control flow: tty init registers a dynamic raw3270-backed tty driver. First open creates a raw3270 view, allocates screen/recall/input buffers, initializes keyboard handlers, and activates the view. Writes update the in-memory screen and set dirty flags; a timer batches status/input/line fragments into raw3270 write requests. Attention interrupts issue read-modified requests; tasklets process AID keys, feed keyboard keycodes, reset the keyboard, and recycle read requests.

State and persistence behavior: runtime state includes the screen-history ring, cursor, current/saved attributes, pending update flags, prompt/input mode, recall buffer, throttle/attention flags, and outstanding raw3270 requests. No persistent device state is stored, though console setup changes z/VM terminal mode.

Dependencies and integration points: depends on `raw3270`, tty core, console subsystem, keyboard/keymap support, EBCDIC conversion, CCW/CIO, panic/reboot notifiers, and z/VM `cpcmd` for console mode.

Risks and test signals: screen resizing reallocates multiple coupled buffers; raw3270 request ownership uses `xchg()` and view refs; escape coverage is partial; panic flushing must avoid lockups. Test open/close/refcount, resize, heavy output, ANSI attributes/colors, alternate charset, read AID keys, throttled attention, command recall, scrollback, fullscreen-view conflicts, and console panic paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/con3270.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/ctrlchar.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/ctrlchar.c

Purpose: centralizes handling of special leading console input sequences for s390 terminals, converting `^c`, `^d`, `^z`, and optionally `^-<key>` sysrq sequences.

Important APIs/types/functions: `ctrlchar_handle()` inspects a short input buffer and returns `CTRLCHAR_NONE`, `CTRLCHAR_SYSRQ`, or a tty control character ORed with `CTRLCHAR_CTRL`. With `CONFIG_MAGIC_SYSRQ`, `schedule_sysrq_work()` schedules `ctrlchar_handle_sysrq()` using a static `sysrq_work`.

Control flow: terminal drivers call `ctrlchar_handle()` after converting input to ASCII. The function accepts two- or three-character buffers beginning with ASCII `^` or codepage-037 hat, maps control requests through `INTR_CHAR()`, `EOF_CHAR()`, and `SUSP_CHAR()`, or schedules sysrq work for `^-x`.

State and persistence behavior: only transient static sysrq work state exists. No persistent data.

Dependencies and integration points: used by 3215 and related terminal input paths; depends on tty special character settings, workqueues, and magic sysrq when enabled.

Risks and test signals: comment notes sysrq handling is racy because a single static work object/key is reused. Test all accepted lengths, EBCDIC hat variant, lowercase/uppercase control chars, nonmatching input passthrough, and concurrent sysrq sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/ctrlchar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/ctrlchar.h -->
# sources/distributed-fs/ceph-client/drivers/s390/char/ctrlchar.h

Purpose: declares the control-character helper API and return-code encoding used by s390 terminal drivers.

Important APIs/types/functions: declares `ctrlchar_handle()`, defines `CTRLCHAR_NONE`, `CTRLCHAR_CTRL`, `CTRLCHAR_SYSRQ`, and `CTRLCHAR_MASK`; with `CONFIG_MAGIC_SYSRQ`, defines `struct sysrq_work` and `schedule_sysrq_work()`.

Control flow: no standalone control flow. Callers mask `ctrlchar_handle()` results with `CTRLCHAR_MASK` and either inject the low byte into tty input, ignore sysrq, or process input normally.

State and persistence behavior: no state beyond the optional work struct type.

Dependencies and integration points: includes tty, sysrq, and workqueue headers; shared by console/tty drivers that want uniform s390 control sequence handling.

Risks and test signals: return values combine high-bit tags with low-byte characters, so callers must mask correctly. Compile with and without `CONFIG_MAGIC_SYSRQ`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/ctrlchar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/defkeymap.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/defkeymap.c

Purpose: generated default EBCDIC keyboard map for s390 3270 keyboard handling, including plain/shift/control maps, function-key strings, and accent composition table.

Important APIs/types/functions: exports `ebc_plain_map`, `ebc_key_maps`, `ebc_keymap_count`, `ebc_func_buf`, `ebc_funcbufptr`, `ebc_funcbufsize`, `ebc_funcbufleft`, `ebc_func_table`, `ebc_accent_table`, and `ebc_accent_table_size`.

Control flow: no executable logic; consumers index tables to translate keycodes and function keys. The file is generated from `defkeymap.map` via `loadkeys --mktable`.

State and persistence behavior: static table state only. Function buffer pointers can be used by keyboard code for runtime keymap string management, but defaults are compiled in.

Dependencies and integration points: includes Linux keyboard/kd/kbd headers, diacritic structures, and local `keyboard.h`; consumed by s390 keyboard/3270 tty code.

Risks and test signals: manual edits would be overwritten by regeneration and can desynchronize with `defkeymap.map`. Test keyboard input translation, function keys, diacritic composition, and builds after regenerating the table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/defkeymap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/diag_ftp.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/diag_ftp.c

Purpose: implements the z/VM DIAGNOSE X'2C4' backend for HMC FTP services used by `hmcdrv`.

Important APIs/types/functions: `struct diag_ftp_ldfpl` is the load-file parameter list; `diag_ftp_handler()` handles external service interrupts; `diag_ftp_2c4()` issues the inline `diag` instruction; `diag_ftp_cmd()` prepares a DMA page, starts the async transfer, waits for completion, and maps status codes; `diag_ftp_startup()`/`shutdown()` register interrupt handling and service-signal subclass.

Control flow: callers serialize access externally. A command allocates an aligned DMA LDFPL, copies the HMC file identifier, fills buffer real address, length, and offset, issues DIAG X'2C4', then waits unconditionally for the external interrupt because cancellation is unavailable. Completion status determines byte count or errno.

State and persistence behavior: global completion and `diag_ftp_subcode` are transient backend state. File transfers affect remote HMC media according to the command, not local persistent kernel state.

Dependencies and integration points: used by `hmcdrv_ftp.c` on z/VM; depends on s390 diag instruction support, external IRQ registration, service-signal subclass, DMA-addressable pages, and HMC FTP command specs.

Risks and test signals: non-reentrant globals require caller mutexing; a lost interrupt would block forever; filename length and DMA alignment are critical. Test startup/shutdown, busy/permission/I/O/status mappings, invalid long names, zero-length transfers, and concurrent caller exclusion through `hmcdrv_ftp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/diag_ftp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/diag_ftp.h -->
# sources/distributed-fs/ceph-client/drivers/s390/char/diag_ftp.h

Purpose: declares the DIAG X'2C4' HMC FTP backend interface.

Important APIs/types/functions: declares `diag_ftp_startup()`, `diag_ftp_shutdown()`, and `diag_ftp_cmd(const struct hmcdrv_ftp_cmdspec *, size_t *)`.

Control flow: no runtime flow. The header marks backend functions as non-reentrant in comments, leaving serialization to callers.

State and persistence behavior: no state in the header.

Dependencies and integration points: includes `hmcdrv_ftp.h` and is consumed by `hmcdrv_ftp.c` to select z/VM transfer operations.

Risks and test signals: compile-time contract must stay aligned with `diag_ftp.c` and `hmcdrv_ftp.c`; test z/VM backend builds with `CONFIG_HMC_DRV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/diag_ftp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/fs3270.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/fs3270.c

Purpose: implements the 3270 fullscreen character device (`/dev/3270/tub*`) that lets one userspace program take a raw fullscreen view of a 3270 terminal.

Important APIs/types/functions: `struct fs3270` extends `raw3270_view` with owner pid, read/write commands, attention flag, activation state, init request, wait queue, and saved read-buffer IDAL. Key functions include `fs3270_do_io()`, activate/deactivate callbacks, `fs3270_irq()`, `fs3270_read()`, `fs3270_write()`, `fs3270_ioctl()`, open/close, notifier create/destroy callbacks, and module init/exit.

Control flow: open resolves either a direct minor or minor 0 through the current tty3270, rejects concurrent fullscreen users, allocates a view and restore buffer, activates it, and stores private data. Reads wait for attention, issue configured read CCW, and copy IDAL data to userspace. Writes copy userspace data into an IDAL and issue configured write CCW. Deactivation saves the 3270 buffer and activation restores or clears it.

State and persistence behavior: per-open state includes owner pid, command choices, activation flag, saved screen buffer size, and outstanding request. The driver sends `SIGHUP` to the owner when restore/save fails or the view is released. No persistent kernel state remains after close.

Dependencies and integration points: depends on `raw3270`, IDAL buffers, fs3270 ioctl ABI, IBM major numbers, tty3270 minor multiplexing, ccw/CIO status, and `class3270` device nodes.

Risks and test signals: view ownership/refcounting and activation/deactivation request reuse are delicate; read waits can be interrupted before I/O; saved-buffer manipulation intentionally shifts IDAL data by five bytes. Test single-owner enforcement, minor 0 mapping, ioctl command changes, attention read flow, write residuals, close during active I/O, SIGHUP on failure, and raw3270 hot unplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/fs3270.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_cache.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_cache.c

Purpose: provides a small non-reentrant read/directory cache for HMC drive FTP transfers, reducing repeated backend reads for `dir`, `nls`, and `get`.

Important APIs/types/functions: `struct hmcdrv_cache_entry` stores command id, filename, file size, cached offset, timeout, content pointer, and cache length. Main functions are `hmcdrv_cache_get()`, `hmcdrv_cache_do()`, `hmcdrv_cache_cmd()`, `hmcdrv_cache_startup()`, and `hmcdrv_cache_shutdown()`.

Control flow: cached commands first try to satisfy the requested file range from a valid, unexpired cache. Misses call the supplied backend transfer function, optionally using the cache buffer as a larger transfer target, update file metadata and content position, and copy requested bytes to the original buffer. Write/error paths invalidate cached read state.

State and persistence behavior: one global cache entry stores transient file metadata and optional DMA-capable content pages. Timeout is 30 seconds. No file data persists beyond module lifetime.

Dependencies and integration points: used by `hmcdrv_ftp_do()` under the FTP mutex; depends on page allocation, jiffies, `hmcdrv_ftp_cmdspec`, and backend function callbacks.

Risks and test signals: global state is not internally locked; correctness depends on external serialization. Cache length uses requested size but allocation uses page order, so effective allocation may be larger than recorded. Test disabled cache, partial range hits/misses, timeout expiry, file-size EOF behavior, write invalidation, backend errors, and startup allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_cache.h -->
# sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_cache.h

Purpose: declares the HMC drive cache API and default cache sizing.

Important APIs/types/functions: defines `HMCDRV_CACHE_SIZE_DFLT`, typedefs `hmcdrv_cache_ftpfunc`, and declares `hmcdrv_cache_cmd()`, `hmcdrv_cache_startup()`, and `hmcdrv_cache_shutdown()`.

Control flow: no standalone flow. The cache wraps a backend FTP function supplied by `hmcdrv_ftp.c`.

State and persistence behavior: no state in the header; implementation maintains a global transient cache.

Dependencies and integration points: includes memory-zone sizing and HMC FTP command definitions; used by HMC module core and FTP layer.

Risks and test signals: default size depends on `MAX_ORDER_NR_PAGES`, so memory-fragmentation behavior should be tested at module load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_dev.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_dev.c

Purpose: exposes HMC drive FTP access through a misc character device named `/dev/hmcdrv`.

Important APIs/types/functions: `hmcdrv_dev_fops` implements open, release, llseek, read, and write. `hmcdrv_dev_open()` starts FTP services; `hmcdrv_dev_release()` shuts them down; `hmcdrv_dev_seek()` resets command state on `SEEK_END`; `hmcdrv_dev_read()` and `hmcdrv_dev_write()` call `hmcdrv_dev_transfer()`; `hmcdrv_dev_init()`/`exit()` register/deregister the misc device.

Control flow: open rejects nonblocking and read-only access, pins the module, and starts backend FTP. The first write stores a NUL-terminated FTP command string in `file->private_data`. Later reads/writes transfer data for that command at the file offset, retrying `-EBUSY` three times with 500 ms sleeps. `SEEK_END` clears the command so the next write supplies a new command.

State and persistence behavior: per-file state is the current command string and file offset. FTP backend refcount state is managed by `hmcdrv_ftp_startup()`/`shutdown()`. No local persistent data is stored.

Dependencies and integration points: depends on miscdevice, VFS file ops, user-copy helpers, module refs, and `hmcdrv_ftp_cmd()`.

Risks and test signals: API semantics are unusual because the first write is command setup and subsequent writes may be file data. Read-only/nonblocking rejection, command reset via seek, retry timing, and cleanup on startup failure need tests. Multiple openers rely on FTP-layer serialization/refcounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_dev.h -->
# sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_dev.h

Purpose: declares the HMC drive misc-device lifecycle interface.

Important APIs/types/functions: `hmcdrv_dev_init()` creates `/dev/hmcdrv`; `hmcdrv_dev_exit()` removes it.

Control flow: no standalone flow. Module init/exit code calls these functions.

State and persistence behavior: no state in the header.

Dependencies and integration points: consumed by the HMC driver module core; implementation depends on miscdevice.

Risks and test signals: compile/link coverage ensures module core and device implementation remain aligned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_ftp.c -->
# sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_ftp.c

Purpose: implements the common HMC drive FTP command parser, backend selection, serialization, cache integration, userspace transfer wrapper, and exported kernel FTP API.

Important APIs/types/functions: `struct hmcdrv_ftp_ops` abstracts startup/shutdown/transfer backend operations. `hmcdrv_ftp_cmd_getid()` maps command text via CRC16 table; `hmcdrv_ftp_parse()` parses `<cmd> <filename>`; `hmcdrv_ftp_do()` serializes cached backend transfers; `hmcdrv_ftp_probe()` probes service availability; `hmcdrv_ftp_cmd()` copies user buffers and dispatches read/write/delete commands; `hmcdrv_ftp_startup()`/`shutdown()` manage backend selection and refcounting.

Control flow: startup chooses DIAG FTP on z/VM or SCLP FTP on LPAR/KVM, starts the backend once, and increments a reference count. Userspace commands are parsed, a DMA buffer is allocated, data is copied in for put/append or copied out for dir/nls/get, and `hmcdrv_ftp_do()` calls the selected backend through the cache. Shutdown decrements the refcount and stops the backend at zero.

State and persistence behavior: global state is `hmcdrv_ftp_funcs`, `hmcdrv_ftp_refcnt`, and `hmcdrv_ftp_mutex`, plus cache state in `hmcdrv_cache.c`. Remote HMC files/media may be read or modified by FTP commands; local kernel state is transient.

Dependencies and integration points: integrates `hmcdrv_dev.c`, exported kernel users, cache layer, DIAG backend, SCLP backend, CRC16, machine-type detection, user-copy helpers, and DMA page allocation.

Risks and test signals: command hashing depends on fixed table order and CRC modulo with known collision avoidance; `hmcdrv_ftp_shutdown()` unconditionally decrements refcount and assumes balanced startup. Test parser edge cases, all command IDs, backend selection on VM/LPAR/KVM/unsupported machines, concurrent openers, startup failure, probe mappings, large transfer allocation order, user-copy failures, and cache invalidation after writes/errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_ftp.c -->
