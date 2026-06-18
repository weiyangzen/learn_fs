# subset-b-005963 research

Grouped research for trace generation and trace event headers under `sources/distributed-fs/ceph-client/include/trace`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/define_remote_events.h -->
# sources/distributed-fs/ceph-client/include/trace/define_remote_events.h

## Purpose
`define_remote_events.h` is the remote-event analogue of the kernel tracepoint generator. It consumes a header named by `REMOTE_EVENT_INCLUDE_FILE` and expands each `REMOTE_EVENT()` declaration into a packed event-format structure, a printer, field metadata, and a `struct remote_event` registration object.

## Important APIs, types, and functions
The important surface is macro based: `REMOTE_EVENT_INCLUDE()`, `REMOTE_PRINTK_COUNT_ARGS()`, `remote_printk()`, `RE_PRINTK()`, `re_field()`, and `REMOTE_EVENT()`. It depends on `REMOTE_EVENT_FORMAT()` and `struct remote_event` from the remote trace event support headers. `__REMOTE_EVENT_SECTION()` optionally places generated descriptors in a named linker section when `REMOTE_EVENT_SECTION` is defined.

## Control flow
The file includes the remote-event declaration file twice. The first pass defines `REMOTE_EVENT()` to emit a `remote_event_print_<name>()` function that casts the raw event record to `struct remote_event_format_<name>` and writes to a `trace_seq`. The second pass redefines `re_field()` and `REMOTE_EVENT()` to emit a field-array, print-format string, and initialized `remote_event_<name>` descriptor.

## State and persistence behavior
There is no runtime mutable state in this header. Persistent build artifacts are generated C symbols: per-event field arrays, format strings, print callbacks, and optional linker-section entries. The trace data state lives in remote-event producers and consumers.

## Dependencies and integration points
It integrates with `<linux/trace_events.h>`, `<linux/trace_remote_event.h>`, `<linux/trace_seq.h>`, `is_signed_type()`, `__COUNT_ARGS`, `CONCATENATE`, and `__stringify`. Users must define `REMOTE_EVENT_INCLUDE_FILE`, and their event declarations must be valid under both passes.

## Risks and test signals
Risks are macro ABI drift, mismatched `re_field()` declarations versus binary payload layout, malformed `RE_PRINTK()` arguments, and section-name mistakes that silently drop descriptors from discovery. Test signals are compile coverage of a remote-event declaration file, inspection of generated `remote_event_fields_*` arrays, remote trace formatting through `trace_seq`, and linker-map checks when `REMOTE_EVENT_SECTION` is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/define_remote_events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/define_trace.h -->
# sources/distributed-fs/ceph-client/include/trace/define_trace.h

## Purpose
`define_trace.h` is the tracepoint definition pass coordinator. Event headers include it outside their include guards so a translation unit that defines `CREATE_TRACE_POINTS` can instantiate storage and callback wiring for the tracepoints declared in the same event header.

## Important APIs, types, and functions
This header rewrites `TRACE_EVENT`, `TRACE_EVENT_FN`, `TRACE_EVENT_SYSCALL`, `DEFINE_EVENT`, `DEFINE_EVENT_FN`, `DEFINE_EVENT_PRINT`, `DECLARE_TRACE`, and related condition/nop forms into `DEFINE_TRACE*()` invocations. It also optionally maps `DEFINE_RUST_DO_TRACE()` to `__DEFINE_RUST_DO_TRACE()` when `CREATE_RUST_TRACE_POINTS` is set.

## Control flow
When `CREATE_TRACE_POINTS` is absent, the header emits nothing. When present, it undefines the flag to prevent recursive definition, includes the target event header again under `TRACE_HEADER_MULTI_READ`, then includes trace-event, perf, and BPF probe generation headers if `TRACEPOINTS_ENABLED` is defined. Finally it restores macro state and redefines `CREATE_TRACE_POINTS` so later trace headers can be processed.

## State and persistence behavior
The persistent result is compiled tracepoint symbols and generated metadata. It has no runtime state of its own; it controls C preprocessor state and linker-visible tracepoint objects.

## Dependencies and integration points
The include target is derived from `TRACE_SYSTEM`, optionally overridden by `TRACE_INCLUDE_FILE` and `TRACE_INCLUDE_PATH`. The header integrates with `<linux/stringify.h>`, `tracepoint.h` declarations, `trace/trace_events.h`, `trace/perf.h`, `trace/bpf_probe.h`, and the kernel build convention that exactly one C file defines `CREATE_TRACE_POINTS`.

## Risks and test signals
Risks include recursive inclusion if the guard protocol is broken, wrong `TRACE_INCLUDE_PATH` relative semantics, duplicate symbol definitions from multiple `CREATE_TRACE_POINTS` users, and ABI changes in tracepoint macro signatures. Test signals are successful module/kernel builds, exactly one exported tracepoint definition per event, generated format files under tracingfs, and perf/BPF attachment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/define_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/9p.h -->
# sources/distributed-fs/ceph-client/include/trace/events/9p.h

## Purpose
`9p.h` defines tracepoints for the Plan 9 filesystem client protocol. It captures client request/response traffic, small protocol payload dumps, and fid reference-count transitions.

## Important APIs, types, and functions
The header exports `P9_MSG_T` and `P9_FID_REFTYPE` enum/string tables through `TRACE_DEFINE_ENUM()`, defines `enum p9_fid_reftype`, and exposes `show_9p_op()` and `show_9p_fid_reftype()` print helpers. Events are `9p_client_req`, `9p_client_res`, `9p_protocol_dump`, and `9p_fid_ref`.

## Control flow
Call sites in the 9p client invoke request events before sending, response events after receipt, protocol dump around raw `struct p9_fcall` buffers, and fid reference events when `struct p9_fid` reference ownership changes. `9p_protocol_dump` copies at most `P9_PROTO_DUMP_SZ` bytes into a dynamic array.

## State and persistence behavior
The header stores no state. Event records snapshot client pointers, protocol type/tag/error, a bounded PDU byte array, fid id, current refcount, and reference operation type. Persistent observability is through tracingfs/perf/BPF event records.

## Dependencies and integration points
It depends on `<linux/tracepoint.h>` and protocol symbols from the 9p client. It integrates with ftrace formatting, user-visible enum maps, and any debugging tools correlating tags across request/response pairs.

## Risks and test signals
Risks include protocol enum drift, pointer values being useful only for correlation within one boot, truncated dumps hiding payload errors beyond 32 bytes, and refcount races if call sites are misplaced. Test signals are trace output showing matching request/response tags, symbolic operation names, correct bounded hex dump length, and fid refcount transitions around create/get/put/destroy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/9p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/afs.h -->
# sources/distributed-fs/ceph-client/include/trace/events/afs.h

## Purpose
`afs.h` is the AFS/YFS client tracepoint contract. It covers RPC construction and completion, rxrpc receive/send progress, callback invalidation, directory edit validation, file lock state, cell/server/volume/address-list reference lifetimes, probing, server rotation, and netfs read receive paths.

## Important APIs, types, and functions
The file defines protocol operation enums for AFS FS, VL, CM, and YFS CM operations, plus many trace enums such as `afs_call_trace`, `afs_server_trace`, `afs_volume_trace`, `afs_cell_trace`, `afs_alist_trace`, `afs_estate_trace`, `afs_cb_break_reason`, `afs_dir_invalid_trace`, `afs_edit_dir_op`, `afs_eproto_cause`, `afs_io_error`, `afs_file_error`, `afs_flock_event`, `afs_flock_operation`, and `afs_rotate_trace`. Major events include `afs_receive_data`, `afs_notify_call`, `afs_cb_call`, `afs_call`, `afs_make_fs_call*`, `afs_make_vl_call`, `afs_call_done`, `afs_send_data`, `afs_sent_data`, directory/vnode validity events, protocol/io/file error events, flock events, callback break/miss events, object lifetime events, probe events, `afs_rotate`, `afs_make_call`, and `afs_read_recv`.

## Control flow
The tracepoints follow AFS operation flow from call allocation/reference changes, FS/VL/CM call construction, rxrpc send/receive, state transitions, completion, and error handling. Directory and vnode events fire around local cache validation and edits. Flock events trace VFS lock operations and remote lock state. Probe and rotate events trace server/address selection and retry decisions before a call is finally made.

## State and persistence behavior
No state is owned by the header. Event payloads snapshot debug ids, refs, active counts, operation ids, FIDs, volume ids, names truncated to 23 bytes, data-version values, error/abort codes, rxrpc addresses, probe RTTs, lock ranges, and operation flags. These records persist only as trace output but encode enough state to reconstruct subsystem progress.

## Dependencies and integration points
It depends on AFS internal structures (`afs_call`, `afs_operation`, `afs_vnode`, `afs_server`, `afs_volume`, `afs_cell`, address lists and endpoint state), rxrpc address helpers, VFS `qstr`, `file_lock`, netfs read-subrequest fields, and tracing macros. It integrates AFS with ftrace/perf/BPF and with userspace symbolic enum decoding through `TRACE_DEFINE_ENUM()`.

## Risks and test signals
Risks include stale enum mappings as AFS/YFS protocol operations evolve, exposing only truncated names, dereferencing partially initialized call/vnode objects from trace call sites, and losing diagnostic value if debug ids are not unique enough. Test signals are trace-enabled AFS mount, lookup, read, write, lock, callback-break, server-failover, and cell-management scenarios; expected output should show call ids moving through make/send/receive/done, rotation reasons, and balanced object get/put/free events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/afs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/alarmtimer.h -->
# sources/distributed-fs/ceph-client/include/trace/events/alarmtimer.h

## Purpose
`alarmtimer.h` traces alarmtimer suspend decisions and alarm lifecycle events. It is used to debug wakeup timers and freezer-aware alarm classes.

## Important APIs, types, and functions
The header exports alarm type enum values with `TRACE_DEFINE_ENUM()`, defines `show_alarm_type()`, and declares `alarm_class` for `alarmtimer_fired`, `alarmtimer_start`, and `alarmtimer_cancel`. Under `CONFIG_RTC_CLASS`, it also defines `alarmtimer_suspend`.

## Control flow
Suspend tracing records the expiration and alarm type considered during suspend. Runtime alarm events snapshot the `struct alarm *`, `alarm->type`, `alarm->node.expires`, and the current `ktime_t now` supplied by the caller.

## State and persistence behavior
The header has no persistent state. It records alarm object addresses and expiry/current time values at event emission.

## Dependencies and integration points
It depends on `<linux/alarmtimer.h>`, `<linux/rtc.h>`, and `<linux/tracepoint.h>`. It integrates with the alarmtimer core, RTC class suspend behavior, tracingfs, and tooling that correlates wakeup source timing.

## Risks and test signals
Risks include missing suspend events when RTC class support is disabled, confusing bitflag formatting because the stored event value is an enum index later shifted for printing, and pointer-only alarm identity. Test signals are start/cancel/fire sequences for realtime and boottime alarms and suspend traces with expected expiration values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/alarmtimer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/amdxdna.h -->
# sources/distributed-fs/ceph-client/include/trace/events/amdxdna.h

## Purpose
`amdxdna.h` defines tracepoints for AMD XDNA driver debugging: generic debug points, DRM scheduler jobs, mailbox head/tail updates, and mailbox IRQ handling.

## Important APIs, types, and functions
Events are `amdxdna_debug_point`, `xdna_job`, `mbox_set_tail`, `mbox_set_head`, and `mbox_irq_handle`. `xdna_mbox_msg` is the shared event class for mailbox head/tail updates.

## Control flow
Driver call sites emit debug points with a name, number, and string; job events snapshot scheduler fence context/sequence plus a driver sequence; mailbox events trace channel id, opcode, and message id; IRQ handling traces device/mailbox name and IRQ number.

## State and persistence behavior
No state is stored by the header. Events snapshot dynamic strings, DRM fence identifiers, mailbox ids, and IRQ numbers for later correlation.

## Dependencies and integration points
It depends on `<drm/gpu_scheduler.h>` and `<linux/tracepoint.h>`. It integrates with the DRM scheduler, AMD XDNA mailbox code, and generic trace consumers.

## Risks and test signals
Risks include null or invalid `sched_job->s_fence`, string lifetime assumptions before `__assign_str()`, and event names that are too generic outside the `amdxdna` trace system. Test signals are traces around job submission/completion, mailbox doorbell activity, and IRQ execution with matching message ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/amdxdna.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/asoc.h -->
# sources/distributed-fs/ceph-client/include/trace/events/asoc.h

## Purpose
`asoc.h` traces ALSA System-on-Chip DAPM power sequencing, widget/path walking, and jack reporting. It helps diagnose audio routing, power transitions, and jack state changes.

## Important APIs, types, and functions
The header defines DAPM formatting helpers `DAPM_DIRECT` and `DAPM_ARROW()`, exports `SND_SOC_DAPM_DIR_OUT`, and declares event classes for DAPM bias levels, DAPM start/done, and widget power/events. Individual events include `snd_soc_dapm_walk_done`, `snd_soc_dapm_path`, `snd_soc_dapm_connected`, `snd_soc_jack_irq`, `snd_soc_jack_report`, and `snd_soc_jack_notify`.

## Control flow
Tracepoints fire at the beginning and end of DAPM bias and graph walks, for widget event start/done/power changes, while checking graph paths, and when jack IRQ/report/notify paths run. Event assignment copies card/component/widget/jack names into trace strings.

## State and persistence behavior
The header owns no state. Records snapshot DAPM context names, card stats counters, widget/path connection flags, stream direction, jack mask/value, and event ids.

## Dependencies and integration points
It depends on ASoC internals via forward-declared card/widget/path structures, `<sound/jack.h>`, `<sound/pcm.h>`, and tracepoint support. It integrates with DAPM graph debugging and userspace trace analysis of audio power behavior.

## Risks and test signals
Risks include dereferencing incomplete DAPM paths, assuming jack->jack is valid, and truncated diagnostic value when names are missing. Test signals are trace sequences for stream startup/shutdown, widget power events, path counts, and jack IRQ-to-report transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/asoc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/avc.h -->
# sources/distributed-fs/ceph-client/include/trace/events/avc.h

## Purpose
`avc.h` exposes a SELinux AVC audit tracepoint for permission-check audit decisions.

## Important APIs, types, and functions
The single event is `selinux_audited`. It records fields from `struct selinux_audit_data`: requested, denied, audited, and result, plus source context, target context, and target class strings.

## Control flow
SELinux audit code calls this event after constructing audit data and context strings. The tracepoint copies strings with `__assign_str()` and emits a formatted record.

## State and persistence behavior
There is no header-owned state. Each event snapshots one audited access decision and its string contexts.

## Dependencies and integration points
It depends on SELinux audit data definitions available to the call site and `<linux/tracepoint.h>`. It integrates SELinux decisions with ftrace/perf/BPF monitoring.

## Risks and test signals
Risks include leaking sensitive security contexts to trace readers, string lifetime mistakes at call sites, and missing non-audited denials. Test signals are SELinux policy tests that produce audited allow/deny decisions and verify requested/denied/audited bitmasks and result codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/avc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/bcache.h -->
# sources/distributed-fs/ceph-client/include/trace/events/bcache.h

## Purpose
`bcache.h` defines tracing for the bcache block cache: request submission/completion, bypass decisions, reads/writes, journal pressure, btree operations, allocator behavior, garbage collection, and background writeback.

## Important APIs, types, and functions
Event classes include `bcache_request`, `bcache_bio`, `bkey`, `btree_node`, `cache_set`, and `btree_split`. Events include `bcache_request_start/end`, `bcache_bypass_*`, `bcache_read`, `bcache_write`, `bcache_read_retry`, `bcache_cache_insert`, journal events, btree read/write/alloc/free/split/compact/root/keyscan/insert events, GC events, allocator invalidate/alloc/fail events, and writeback collision events.

## Control flow
Tracepoints are arranged by bcache subsystem files: request path, journal, btree, allocator, and background writeback. Request and bio events use block-layer helpers to snapshot device, sector, size, and rwbs flags; btree and key events extract bucket, key inode/offset/size/dirty state; allocator events snapshot cache bucket and free-list pressure.

## State and persistence behavior
The header stores no state. Event records snapshot bio positions, cache-set UUIDs, bkey contents, btree node bucket/level, bucket offsets, free FIFO sizes, and ref/operation status.

## Dependencies and integration points
It depends on bcache internal types/macros (`struct bcache_device`, `cache_set`, `bkey`, `btree`, `cache`, `KEY_*`, `PTR_BUCKET_NR`, `GC_SECTORS_USED`) and block helpers such as `blk_fill_rwbs()` and `bio_dev()`. It integrates bcache diagnostics with block tracing.

## Risks and test signals
Risks include assumptions about bcache internal layout, confusing `bcache_write` print text naming writeback as hit, and pointer/bucket identity being transient. Test signals are cache hit/miss workloads, sequential/congested bypass, journal-full injection, btree split/GC scenarios, allocation failure pressure, and writeback collision traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/bcache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/block.h -->
# sources/distributed-fs/ceph-client/include/trace/events/block.h

## Purpose
`block.h` is the block layer tracepoint schema. It records request and bio lifecycle events, queue plug/unplug behavior, remapping, splits, completions, errors, buffer-head touches, zone management, and zoned write plug activity.

## Important APIs, types, and functions
Event classes include `block_buffer`, `block_rq_completion`, `block_rq`, `block_bio`, `block_unplug`, and `block_zwplug`. Events include `block_rq_requeue`, `block_rq_complete`, `block_rq_error`, request insert/issue/merge/io-start/io-done, `block_bio_complete`, bio back/front merge and queue events, `block_getrq`, zone append update, plug/unplug, split, bio/request remap, `blkdev_zone_mgmt`, `disk_zone_wplug_add_bio`, and `blk_zone_wplug_bio`.

## Control flow
Call sites in buffer, bio, request, scheduler, mapper, and zoned-device paths emit events as I/O moves from bio creation, queueing, merging, request allocation, issue, completion/error, and remap/split transformations. Completion events convert `blk_status_t` to errno and preserve ioprio fields.

## State and persistence behavior
The header has no state. Records snapshot device ids, sectors, byte counts, rwbs strings, command placeholder strings, current task command, ioprio class/hint/level, old mapping device/sector, queue depth, zone number, and errors.

## Dependencies and integration points
It depends on block core types and helpers from `<linux/blkdev.h>`, `<linux/blktrace_api.h>`, buffer heads when configured, and uapi ioprio definitions. It is a stable integration point for blktrace-style tooling, ftrace, perf, BPF, and storage performance analysis.

## Risks and test signals
Risks include tracepoint ABI sensitivity, stale comments versus modern blk-mq behavior, null disk handling in some request events, and using event timing as a proxy without accounting for batching. Test signals are fio or xfstests workloads with expected queue/issue/complete ordering, remap traces through dm/md, split traces on limits, zone-management traces on zoned devices, and ioprio decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/block.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/bpf_test_run.h -->
# sources/distributed-fs/ceph-client/include/trace/events/bpf_test_run.h

## Purpose
`bpf_test_run.h` defines tracepoints used by BPF test execution paths, including a trigger event and a writable finish event where supported.

## Important APIs, types, and functions
Events are `bpf_trigger_tp` and `bpf_test_finish`. `bpf_test_finish` is generated through `BPF_TEST_RUN_DEFINE_EVENT()`, which expands to `DEFINE_EVENT_WRITABLE()` when available and otherwise to `DEFINE_EVENT()`.

## Control flow
Tests emit `bpf_trigger_tp` with a nonce to drive attached BPF programs. Finish tracing reads `*err` from an integer pointer and, in writable configurations, exposes a writable field size of `sizeof(int)` for BPF mutation tests.

## State and persistence behavior
No state is stored in the header. Event records snapshot the nonce or error value; writable-event behavior may allow attached programs to affect the pointed error in supported builds.

## Dependencies and integration points
It depends on `<linux/tracepoint.h>` and tracepoint macro support for writable events. It integrates with BPF selftests and kernel BPF test-run infrastructure.

## Risks and test signals
Risks include pointer validity for `err`, behavior differences when `DEFINE_EVENT_WRITABLE` is not defined, and tests accidentally depending on a writable tracepoint in non-writable builds. Test signals are BPF selftests that attach to the trigger and finish events and verify nonce/error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/bpf_test_run.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/bridge.h -->
# sources/distributed-fs/ceph-client/include/trace/events/bridge.h

## Purpose
`bridge.h` traces Linux bridge forwarding database and multicast database events. It helps diagnose FDB add/delete/update paths, externally learned entries, and MDB capacity issues.

## Important APIs, types, and functions
Events are `br_fdb_add`, `br_fdb_external_learn_add`, `fdb_delete`, `br_fdb_update`, and `br_mdb_full`. They record bridge/port device names, MAC addresses, VLAN ids, netlink flags, FDB flags, and multicast group identity.

## Control flow
Bridge management and learning paths emit FDB events during netlink add, external learn, delete, and update operations. `br_mdb_full` records multicast group information, converting IPv4 addresses to IPv4-mapped IPv6 arrays and handling raw MAC groups when no protocol is set.

## State and persistence behavior
The header stores no state. Records snapshot names, MAC/group bytes, flags, VLAN ids, and address family at the point of bridge database mutation or failure.

## Dependencies and integration points
It depends on `<linux/netdevice.h>`, tracepoint support, and bridge private structures via `../../../net/bridge/br_private.h`. It integrates with network tracing, netlink bridge management, multicast snooping diagnostics, and BPF consumers.

## Risks and test signals
Risks include private-header coupling, IPv6 fields being compiled only when `CONFIG_IPV6` is enabled, and device-name snapshots changing after rename. Test signals are bridge FDB netlink operations, learned source updates, FDB delete paths, and MDB-full reproductions with IPv4, IPv6, and MAC groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/btrfs.h -->
# sources/distributed-fs/ceph-client/include/trace/events/btrfs.h

## Purpose
`btrfs.h` is the Btrfs filesystem tracepoint schema. It covers transactions, inode lifecycle, extent maps and file extent items, ordered extents and writeback, sync operations, block groups/chunks, delayed refs, COW, allocation and free-space search, space reservation and flushing, workqueues, qgroups, backref prelim refs, extent state bits, tree locking, RAID56, and extent-map shrinker behavior.

## Important APIs, types, and functions
The file defines helpers for root/ref/chunk/group/extent/flush/qgroup enum formatting and fsid-aware macros `TP_STRUCT__entry_btrfs()`, `TP_fast_assign_btrfs()`, and `TP_printk_btrfs()`. Major event classes include `btrfs__inode`, file extent item classes, `btrfs__ordered_extent`, writepage, delayed tree/data/ref-head, chunk, reserved/reserve extent, work/workqueue, qgroup reservation/extent, prelim ref, block group, dump space info, sleep tree lock, locking events, space-info update, and RAID56 bio.

## Control flow
Tracepoints are placed through Btrfs operations: transaction commit, inode create/request/evict, extent lookup and extent item display, ordered extent add/start/finish/remove, writeback hooks, sync file/fs, block group creation/removal/reclaim, delayed ref enqueue/run, chunk alloc/free, COW/search-slot restart, reservation/flush and ticket handling, free extent search and cluster setup, workqueue queue/schedule/done, qgroup accounting and reserve conversions, extent state bit changes, tree lock wait/unlock, RAID56 bio mapping, RAID extent tree changes, and extent-map shrinker scan/removal.

## State and persistence behavior
The header owns no state, but its event payloads are rich snapshots of live Btrfs state: fsid, root ids, inode numbers, generations, extent offsets/lengths/flags/compression, ordered extent refs/bytes left, block group flags/used bytes, delayed ref identity/action/seq, qgroup counters/reservations, space-info counters, tree lock wait timestamps, RAID stripe identity, and shrinker cursor fields.

## Dependencies and integration points
It depends on many Btrfs internal types and helpers, writeback control, mm flag formatting, refcounts, spinlocks, atomic/percpu counters, bio fields, and tracepoint infrastructure. It integrates Btrfs internals with tracingfs/perf/BPF and is used by filesystem developers and xfstests diagnostics.

## Risks and test signals
Risks include high ABI surface area, dereferencing internal objects that may be in teardown, fsid/root formatting assumptions, lock-side effects in qgroup meta free tracing, and expensive counter snapshots if enabled on hot paths. Test signals are Btrfs xfstests and targeted workloads for fsync, delalloc/writeback, ENOSPC/flush tickets, delayed refs, qgroups, block-group reclaim, tree-lock contention, RAID56 I/O, and shrinker pressure, with trace output showing expected root/fsid and counter transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/btrfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/cachefiles.h -->
# sources/distributed-fs/ceph-client/include/trace/events/cachefiles.h

## Purpose
`cachefiles.h` defines tracepoints for the CacheFiles backend of fscache/netfs. It tracks object references, lookup and directory operations, coherency checks, read/write/truncate preparation, active/failed/inactive marking, VFS/I/O errors, and on-demand cache file protocol operations.

## Important APIs, types, and functions
The header declares enums for object reference reasons, object kill reasons, coherency reasons, truncate reasons, read preparation reasons, and error locations. Events include `cachefiles_ref`, `cachefiles_lookup`, `cachefiles_mkdir`, `cachefiles_tmpfile`, `cachefiles_link`, `cachefiles_unlink`, `cachefiles_rename`, `cachefiles_coherency`, `cachefiles_vol_coherency`, `cachefiles_prep_read`, `cachefiles_read`, `cachefiles_write`, `cachefiles_trunc`, active/failed/inactive marks, VFS/I/O errors, and on-demand open/copen/close/read/cread/fd-write/fd-release.

## Control flow
Object lifecycle paths emit ref and lookup/create/link/unlink/rename events. Coherency paths compare auxiliary data, content state, xattrs, and volume metadata. Read preparation determines whether data exists, holes are present, no backing file exists, or seek failed. I/O paths trace read/write/truncate and error locations. On-demand mode traces requests and replies exchanged with userspace cache handlers.

## State and persistence behavior
The header stores no state. Event records snapshot object/cookie/volume debug ids, usage counts, backing inode numbers, coherency aux values, content/source enums, offsets/lengths, error codes, message ids, object ids, file descriptors, and flags.

## Dependencies and integration points
It depends on CacheFiles internals, fscache object kill reasons, `netfs_sreq_sources`, VFS dentries/inodes, endian helpers for inline aux data, and tracepoint macros. It integrates the cache backend with netfs/fscache diagnostics and the on-demand cachefiles userspace protocol.

## Risks and test signals
Risks include stale enum mappings, dereferencing optional objects/backers, duplicate macro text in the source around some prototypes that would be caught at build time, and leaking cache object ids or inode numbers to trace consumers. Test signals are fscache/cachefiles mount and read/write workloads, coherency mismatch injection, VFS error injection, object withdrawal/culled paths, and on-demand open/read/close flows with matching msg/object ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/cachefiles.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/capability.h -->
# sources/distributed-fs/ceph-client/include/trace/events/capability.h

## Purpose
`capability.h` traces Linux capability checks after the kernel determines whether credentials are capable in a target user namespace.

## Important APIs, types, and functions
The single event is `cap_capable`. It records `const struct cred *`, target user namespace, capable namespace, capability number, and return code.

## Control flow
The common capability code emits the event after a check. The assignment stores `capable_ns` only on success (`ret == 0`); failures record it as `NULL`, making successful namespace derivation explicit.

## State and persistence behavior
The header stores no state. Event records contain pointer identities, capability id, and success/failure code.

## Dependencies and integration points
It depends on credential and user-namespace headers plus tracepoints. It integrates with security debugging, audit-adjacent observability, and BPF tools that inspect capability decisions.

## Risks and test signals
Risks include sensitive pointer/context exposure, pointer identity being boot-local, and high event volume on systems tracing all capability checks. Test signals are namespace capability tests for root/user namespaces, success and denial paths, and verification that failed checks show a null capable namespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/capability.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/ceph.h -->
# sources/distributed-fs/ceph-client/include/trace/events/ceph.h

## Purpose
`ceph.h` defines CephFS client tracepoints for MDS request lifecycle and capability message handling.

## Important APIs, types, and functions
It defines `enum ceph_mdsc_suspend_reason` with symbolic mappings for no map, no active MDS, rejected, and session suspension. Events are `ceph_mdsc_submit_request`, `ceph_mdsc_suspend_request`, `ceph_mdsc_resume_request`, `ceph_mdsc_send_request`, `ceph_mdsc_complete_request`, and `ceph_handle_caps`.

## Control flow
MDS request events follow submit, suspend, resume, send, and completion. Submit derives inode identity from `req->r_inode` or `req->r_dentry`; suspend records the target MDS when a session is present; complete calculates latency from request start/end timestamps. Capability handling records MDS, cap op, vino, and sequence fields.

## State and persistence behavior
The header owns no state. Records snapshot request tid, operation id/name, inode number and snap id, MDS rank, error, latency, capability vino, and seq/mseq/issue_seq.

## Dependencies and integration points
It depends on CephFS internal MDS request/session/client/inode/cap structures and helpers such as `ceph_mds_op_name()`, `ceph_cap_op_name()`, `ceph_ino()`, and `ceph_snap()`. It integrates CephFS with ftrace/perf/BPF diagnostics.

## Risks and test signals
Risks include incomplete inode identification when neither inode nor dentry is available, latency underflow if timestamps are not ordered, and suspend reason enum drift. Test signals are MDS operation workloads showing submit/send/complete sequences, forced session/map suspension, error completions, and cap messages with expected sequence numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/ceph.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/cgroup.h -->
# sources/distributed-fs/ceph-client/include/trace/events/cgroup.h

## Purpose
`cgroup.h` traces cgroup hierarchy, lifecycle, task migration, populated/frozen notifications, and rstat locking.

## Important APIs, types, and functions
Event classes are `cgroup_root`, `cgroup`, `cgroup_migrate`, `cgroup_event`, and `cgroup_rstat`. Events include setup/destroy/remount root, mkdir/rmdir/release/rename/freeze/unfreeze cgroup, attach/transfer tasks, notify populated/frozen, and rstat lock contended/locked/unlock.

## Control flow
Cgroup core emits root events around hierarchy setup and teardown, cgroup events around directory state changes, migration events when tasks move, notification events when populated/frozen counters change, and rstat events around stats lock acquisition and release.

## State and persistence behavior
The header stores no state. Records snapshot hierarchy id, subsystem mask, cgroup id/level/path, destination cgroup, task pid/comm, notification value, CPU, and contended flag.

## Dependencies and integration points
It depends on `<linux/cgroup.h>` and tracepoint infrastructure. It integrates with scheduler/resource-control diagnostics, cgroup v1/v2 tooling, and BPF consumers of cgroup state changes.

## Risks and test signals
Risks include path string lifetime at call sites, high volume on task migrations, and rstat contention tracing changing timing when enabled. Test signals are cgroup create/rename/remove/freeze/migrate operations with expected ids and paths, plus rstat contention workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/cgroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/clk.h -->
# sources/distributed-fs/ceph-client/include/trace/events/clk.h

## Purpose
`clk.h` traces common clock framework operations: enable/disable, prepare/unprepare, rate changes, rate constraints, parent changes, phase, duty cycle, and rate request evaluation.

## Important APIs, types, and functions
Event classes include `clk`, `clk_rate`, `clk_rate_range`, `clk_parent`, `clk_phase`, `clk_duty_cycle`, and `clk_rate_request`. Events include start/complete pairs for enable, disable, prepare, unprepare, set-rate, set-parent, set-phase, set-duty-cycle, plus min/max/range and rate-request start/done.

## Control flow
Clock framework call sites emit events before and after operations. Assignment copies clock names, parent names, rates, min/max constraints, phase, duty numerator/denominator, and best-parent request fields.

## State and persistence behavior
The header owns no state. Event records snapshot `clk_core` names and clock parameter values at the operation boundary.

## Dependencies and integration points
It depends on common clock framework internal types (`clk_core`, `clk_rate_request`, `clk_duty`) and tracepoint support. It integrates with platform power/performance debugging and clock tree tracing tools.

## Risks and test signals
Risks include null parent/core handling in some but not all events, string value changes after rename, and high event volume during DVFS. Test signals are clock enable/disable and set-rate tests showing paired start/complete events with expected names/rates/parents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/cma.h -->
# sources/distributed-fs/ceph-client/include/trace/events/cma.h

## Purpose
`cma.h` traces Contiguous Memory Allocator release and allocation attempts, including retry on busy ranges.

## Important APIs, types, and functions
Events are `cma_release`, `cma_alloc_start`, `cma_alloc_finish`, and `cma_alloc_busy_retry`. They record area name, PFN, page pointer, counts, alignment, available/total counts, and error code.

## Control flow
CMA allocation emits start with requested and available/total pages, may emit busy retry events for contested ranges, and emits finish with final PFN/page/count/align/error. Release records the returned PFN/page/count.

## State and persistence behavior
No state is stored by the header. Records snapshot allocator state and selected pages for one allocation/release operation.

## Dependencies and integration points
It depends on basic Linux types, `struct page`, and tracepoints. It integrates with memory-management tracing and device-driver debugging for contiguous DMA allocations.

## Risks and test signals
Risks include high trace volume during allocation retry loops and pointer/PFN sensitivity. Test signals are CMA allocation success, allocation failure, busy retry under pinned pages, and release events with matching counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/cma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/compaction.h -->
# sources/distributed-fs/ceph-client/include/trace/events/compaction.h

## Purpose
`compaction.h` traces memory compaction isolation, migration, suitability, deferral, and kcompactd wake/sleep behavior.

## Important APIs, types, and functions
Event classes are `mm_compaction_isolate_template`, `mm_compaction_suitable_template`, `mm_compaction_defer_template`, and `kcompactd_wake_template`. Events include isolate migrate/free/fast-free pages, migratepages, begin/end, try-to-compact-pages, finished/suitable, deferred/defer/reset, kcompactd sleep, and kcompactd wakeup/wake.

## Control flow
Compaction code emits isolation events as PFN ranges are scanned, begin/end around a compaction run, migratepages after migration attempts, suitability/deferral decisions per zone/order, and daemon sleep/wake events. Some events are only compiled under `CONFIG_COMPACTION`.

## State and persistence behavior
The header stores no state. Records snapshot PFN ranges, scan/take counts, compact control cursors, sync mode, gfp mask, priority, node/zone/order, compaction status, deferral counters, and kcompactd wake parameters.

## Dependencies and integration points
It depends on MM zone/compaction types, `<trace/events/mmflags.h>` for GFP/zone/status formatting, and tracepoints. It integrates with page allocator and memory-fragmentation diagnostics.

## Risks and test signals
Risks include ABI constraints on printed names such as `classzone_idx`, event availability depending on `CONFIG_COMPACTION`, and overhead on hot memory-management paths. Test signals are high-order allocation stress, compaction success/failure cases, deferred compaction behavior, and kcompactd wake/sleep traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/compaction.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/context_tracking.h -->
# sources/distributed-fs/ceph-client/include/trace/events/context_tracking.h

## Purpose
`context_tracking.h` traces transitions between kernel and userspace context tracking.

## Important APIs, types, and functions
It defines the `context_tracking_user` event class and two events: `user_enter` and `user_exit`. The dummy integer field exists to satisfy trace event macro requirements.

## Control flow
`user_enter` fires when the kernel resumes to userspace after a syscall or exception. `user_exit` fires when userspace enters the kernel through a syscall or exception.

## State and persistence behavior
The header owns no state and records only a dummy field; the useful information is timestamp, CPU, task, and ordering supplied by the tracing framework.

## Dependencies and integration points
It depends on `<linux/tracepoint.h>` and context tracking call sites. It integrates with RCU/nohz/context-tracking diagnostics.

## Risks and test signals
Risks include very high event volume and low payload detail. Test signals are syscall/exception workloads where user exit precedes kernel work and user enter follows return-to-user paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/context_tracking.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/coredump.h -->
# sources/distributed-fs/ceph-client/include/trace/events/coredump.h

## Purpose
`coredump.h` defines a stable tracepoint emitted when a coredump attempt starts.

## Important APIs, types, and functions
The single event is `coredump`. It records the triggering signal number and current task command name.

## Control flow
Coredump code emits this event at the beginning of a dump attempt, before the rest of dump generation succeeds or fails.

## State and persistence behavior
No state is stored by the header. Records snapshot `sig` and `current->comm`; success, file path, and dump size are not recorded here.

## Dependencies and integration points
It depends on scheduler task state and tracepoints. It integrates with observability tools that monitor process crashes without parsing kernel logs.

## Risks and test signals
Risks include assuming the event means a core file was written and relying on `comm` rather than pid/exe path. Test signals are crash tests that trigger core-dumping signals and verify the event appears before dump completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/coredump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/cpuhp.h -->
# sources/distributed-fs/ceph-client/include/trace/events/cpuhp.h

## Purpose
`cpuhp.h` traces CPU hotplug state-machine callbacks and results.

## Important APIs, types, and functions
Events are `cpuhp_enter`, `cpuhp_multi_enter`, and `cpuhp_exit`. They record CPU id, target/state, step index, callback pointer, and return code.

## Control flow
The hotplug core emits enter events before invoking single-instance or multi-instance callbacks and emits exit after a step returns. Function pointers are printed symbolically via `%ps`.

## State and persistence behavior
The header stores no state. Records snapshot step and callback identity for one CPU hotplug transition.

## Dependencies and integration points
It depends on CPU hotplug internals and tracepoints. It integrates with CPU online/offline debugging, module hotplug callback validation, and latency analysis.

## Risks and test signals
Risks include pointer/symbol exposure, callbacks being unloaded after trace capture, and partial visibility if failures abort later steps. Test signals are CPU online/offline tests showing enter/exit pairs and nonzero returns on injected failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/cpuhp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/csd.h -->
# sources/distributed-fs/ceph-client/include/trace/events/csd.h

## Purpose
`csd.h` traces call-single-data and smp-call-function activity.

## Important APIs, types, and functions
Events are `csd_queue_cpu`, `csd_function_entry`, and `csd_function_exit`. `csd_function` is the shared class for callback entry and exit.

## Control flow
The queue event records the target CPU, callsite, callback function, and CSD pointer when work is queued to another CPU. Entry and exit events bracket the callback execution on the receiving CPU.

## State and persistence behavior
The header has no state. Records snapshot pointers and CPU id; ordering and timestamps come from trace infrastructure.

## Dependencies and integration points
It depends on SMP call function types (`smp_call_func_t`, `call_single_data_t`) and tracepoint support. It integrates with inter-processor-call debugging and latency analysis.

## Risks and test signals
Risks include pointer/symbol exposure and very high volume on IPI-heavy systems. Test signals are smp_call_function workloads where queue, entry, and exit can be correlated by CSD pointer and function symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/csd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/damon.h -->
# sources/distributed-fs/ceph-client/include/trace/events/damon.h

## Purpose
`damon.h` traces DAMON monitoring and DAMOS scheme activity: scheme statistics, estimated size, before-apply details, interval tuning, and aggregated region observations.

## Important APIs, types, and functions
Events are `damos_stat_after_apply_interval`, `damos_esz`, `damos_before_apply`, `damon_monitor_intervals_tune`, and `damon_aggregated`. `damos_before_apply` is conditional on a `do_trace` argument.

## Control flow
DAMON emits aggregate stats after each apply interval, estimated size events for schemes, conditional per-region details before a scheme applies, monitor interval tuning events, and region aggregation events after sampling.

## State and persistence behavior
The header stores no state. Records snapshot context/scheme/target indices, DAMOS stat counters, region start/end/accesses/age, number of regions, estimated size, and sample interval.

## Dependencies and integration points
It depends on `<linux/damon.h>` structures and tracepoint support. It integrates with memory access monitoring, DAMOS policy debugging, and BPF/ftrace consumers.

## Risks and test signals
Risks include high volume when `damos_before_apply` is enabled, potentially sensitive address ranges in traces, and unit confusion between base-point and raw access counters. Test signals are DAMON selftests/workloads with known regions, scheme apply counts, interval tuning, and conditional event suppression when `do_trace` is false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/damon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/devfreq.h -->
# sources/distributed-fs/ceph-client/include/trace/events/devfreq.h

## Purpose
`devfreq.h` traces device frequency scaling decisions and monitor samples.

## Important APIs, types, and functions
Events are `devfreq_frequency` and `devfreq_monitor`. They record device name, selected or previous frequency, busy time, total time, and polling interval where applicable.

## Control flow
Devfreq governors/core emit monitor events when sampling device load and frequency events when frequency changes. Print formatting computes load as `100 * busy_time / total_time`, guarding zero total time.

## State and persistence behavior
The header owns no state. Event records snapshot values from `struct devfreq`, including `last_status`, `previous_freq`, and profile polling interval.

## Dependencies and integration points
It depends on `<linux/devfreq.h>` and tracepoints. It integrates with power-management diagnostics, governor tuning, and performance analysis.

## Risks and test signals
Risks include stale `last_status` data if drivers do not update it consistently, zero total-time samples reporting load 0, and event volume from short polling intervals. Test signals are devfreq governor tests that force load changes and frequency transitions with expected load percentages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/devfreq.h -->
