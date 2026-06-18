# Research: subset-b-004025

Grouped research for device-mapper linear, dirty-log, multipath, path-selector, and persistent-cache source files. Each file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-linear.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-linear.c

## Purpose
Implements the device-mapper `linear` target: a simple remapping layer that maps a contiguous logical target range onto a contiguous range of one underlying block device. It is a foundational target used directly by dm tables and by other targets as the simplest example of target construction, status, ioctl forwarding, zoned reporting, and DAX passthrough.

## Important APIs, Types, And Functions
`struct linear_c` stores the backing `dm_dev` and starting sector. `linear_ctr()` parses `<dev_path> <offset>`, opens the backing device with the table mode, and configures flush/discard/secure erase/write zeroes counts. `linear_map_sector()` applies `dm_target_offset()`. `linear_map()` rewrites the bio device and sector and returns `DM_MAPIO_REMAPPED`. `linear_status()` emits table and IMA state. `linear_prepare_ioctl()` forwards ioctls only when the target covers the full underlying device from sector zero. Optional hooks include `linear_report_zones()` and DAX direct-access, zero, and recovery-write wrappers. `linear_target` registers the target through `dm_linear_init()`/`dm_linear_exit()`.

## Control Flow
Construction validates two arguments, allocates context, stores the start sector, opens the device, and attaches context to `ti->private`. Runtime bio mapping is synchronous and stateless: calculate target offset, set `bio->bi_bdev`, update `bi_sector`, and return. Zoned and DAX operations translate the target position and delegate to the lower device. Destruction drops the device reference and frees context.

## State And Persistence
Only per-target runtime state exists: the backing device reference and starting sector. There is no on-disk metadata. Persistence and data ordering are inherited from the underlying block device; flushes bypass mapping because the target has a single lower device.

## Dependencies And Integration Points
Depends on device-mapper target registration, `dm_get_device()`/`dm_put_device()`, block bio APIs, zoned block helpers, DAX helpers, and IMA status formatting. It advertises integrity, nowait, host-managed zoned, crypto, and atomic-write passthrough features.

## Risks
Sector parsing and overflow checks are the main constructor risk. Ioctl forwarding is deliberately conservative because forwarding partition or device-size-sensitive ioctls through an offset mapping would be unsafe. DAX page-offset translation must include both the target offset and lower-device start sector. Feature flags assume the lower device capabilities are correctly constrained by dm core queue-limit merging.

## Test Signals
Exercise table creation with invalid counts, invalid offsets, very large offsets, full-device and offset mappings, bio read/write remapping, flush/discard/write-zeroes/secure-erase passthrough, ioctl forwarding refusal on partial maps, zoned report translation, DAX enabled/disabled builds, IMA/table status output, and target register/unregister paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-linear.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-log-userspace-base.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-log-userspace-base.c

## Purpose
Implements the `userspace` dirty-log type for dm mirror-style targets. It delegates dirty-region-log policy and persistence to a userspace daemon over the dm-log-userspace connector protocol while preserving the kernel `dm_dirty_log_type` interface expected by device-mapper mirror code.

## Important APIs, Types, And Functions
`struct log_c` stores target/device references, UUID/LUID identity, cached constructor string, region size/count, pending mark/clear lists, flush mempool, reconnect metadata, optional integrated-flush workqueue, and `in_sync_hint`. `userspace_ctr()` validates `<UUID> [integrated_flush] <daemon args>`, sends `DM_ULOG_CTR`, fetches region size, optionally opens a returned log device, and initializes flush batching. `userspace_do_request()` wraps `dm_consult_userspace()` and reconnects on `-ESRCH`. Log operations implement clean/sync queries, mark/clear queues, grouped `userspace_flush()`, resync work, sync count, remote recovery, suspend/resume, status, and destructor. `_userspace_type` registers with `dm_dirty_log_type_register()`.

## Control Flow
Constructor strips the UUID and optional `integrated_flush`, builds a daemon constructor string prefixed with target length, initializes pending-request lists, sends create and region-size requests, then saves context. Mark and clear operations enqueue `dm_dirty_log_flush_entry` objects under `flush_lock` rather than always contacting userspace. Flush drains mark/clear lists, sends grouped requests up to `MAX_FLUSH_GROUP_COUNT`, commits with `DM_ULOG_FLUSH`, and optionally combines mark payloads with integrated flush. Query paths call userspace synchronously and return conservative answers on failure.

## State And Persistence
The kernel stores runtime queues and identity only; actual log state and durable metadata live in userspace or its chosen log device. Pending mark/clear entries are volatile until flushed. `in_sync_hint` caches a lower bound for optimization and resets on resume. Integrated flush schedules delayed work for clear-only batches.

## Dependencies And Integration Points
Depends on `dm-log-userspace-transfer.c`, `linux/dm-log-userspace.h` request codes, dirty-log registration in `dm-log.c`, mempools/slab caches, workqueues, dm target events, and optional lower log devices returned by the userspace daemon.

## Risks
Userspace daemon loss can stall reconnect loops. Conservative failure behavior can force resync or table events but avoids falsely clean/in-sync results. `userspace_clear_region()` uses GFP_ATOMIC and may skip clearing, intentionally causing later resync. Grouped flush failure falls back only for non-integrated grouped mark/clear traffic. Correctness depends on daemon protocol compatibility, NUL-terminated returned device names, and flushing pending delayed work during suspend/destruction.

## Test Signals
Test module init/exit, missing daemon, daemon restart/reconnect, constructor argument validation, long UUID rejection, returned device open/close, integrated and non-integrated flush paths, mark/clear batching, clear allocation failure behavior, suspend/resume ordering, remote recovery throttling, status fallback on communication failure, and mirror resync behavior after daemon errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-log-userspace-base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-log-userspace-transfer.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-log-userspace-transfer.c

## Purpose
Provides the low-level connector/netlink transport for dm userspace dirty logs. It serializes kernel requests into `struct dm_ulog_request`, sends them to the userspace log daemon, waits for matching replies or ACKs, retries on timeout or `-EAGAIN`, and exposes a single `dm_consult_userspace()` API to the userspace dirty-log implementation.

## Important APIs, Types, And Functions
Global state includes `dm_ulog_seq`, preallocated 512-byte connector/request buffer, connector id `CN_IDX_DM/CN_VAL_DM_USERSPACE_LOG`, `dm_ulog_lock`, and `receiving_list` protected by `receiving_list_lock`. `struct receiving_pkg` is a stack-resident waiter containing sequence, completion, error, and return-data buffer. `dm_ulog_sendto_server()` fills `cn_msg` and calls `cn_netlink_send()`. `fill_pkg()` matches replies by sequence and copies ACK or payload results. `cn_ulog_callback()` validates `CAP_SYS_ADMIN`, decodes messages, and completes waiters. `dm_consult_userspace()` builds a request, links a waiter, sends, waits up to `DM_ULOG_RETRY_TIMEOUT`, and retries as needed. `dm_ulog_tfr_init()`/`dm_ulog_tfr_exit()` allocate buffers and register connector callbacks.

## Control Flow
Each request is serialized by `dm_ulog_lock` because the message buffer is shared. A waiter is added before send so a fast reply can complete it. On send failure the waiter is removed and the error is returned. On timeout the waiter is removed, a warning is emitted, and the request is rebuilt with a new sequence. Empty connector messages are treated as ACKs; non-empty messages are expected to contain a complete `dm_ulog_request` payload.

## State And Persistence
All state is volatile kernel memory. There is no persistence. Sequence values are process-lifetime counters. Waiters are stack objects visible through the receiving list only while `dm_consult_userspace()` is active.

## Dependencies And Integration Points
Depends on Linux connector, netlink credentials, completions, spinlocks, mutexes, dm-log-userspace protocol structures, and device-mapper logging macros. It is initialized by `dm-log-userspace-base.c` before the dirty-log type is registered.

## Risks
Connector is unreliable, so retry behavior can wait indefinitely if the daemon never responds. The fixed preallocated size limits payloads; callers must stay below the calculated capacity. Stack-resident waiters are safe only because list removal is synchronized. Capability checks protect callbacks, but daemon/protocol mismatches can return wrong data sizes. ACK `msg->ack` is negated into an errno, so userspace must follow connector ACK conventions.

## Test Signals
Exercise callback registration failure, oversized payload rejection, timeout and retry, `-EAGAIN` retry, ACK-only and payload replies, insufficient receive buffer handling, incomplete message logging, concurrent callers serialized through `dm_ulog_lock`, unauthorized callback messages, and module unload while no waiters remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-log-userspace-transfer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-log-userspace-transfer.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-log-userspace-transfer.h

## Purpose
Private header for the userspace dirty-log transport layer. It provides the shared message prefix and declares the connector transport lifecycle and request API used by `dm-log-userspace-base.c`.

## Important APIs, Types, And Functions
Defines `DM_MSG_PREFIX` as `dm-log-userspace` for logging. Declares `dm_ulog_tfr_init()`, `dm_ulog_tfr_exit()`, and `dm_consult_userspace(const char *uuid, uint64_t luid, int request_type, char *data, size_t data_size, char *rdata, size_t *rdata_size)`.

## Control Flow
The header has no runtime control flow. The userspace dirty-log module calls `dm_ulog_tfr_init()` before registering its dirty-log type, uses `dm_consult_userspace()` for each daemon request, and calls `dm_ulog_tfr_exit()` during module unload.

## State And Persistence
No state is defined in the header. Transport state is owned by `dm-log-userspace-transfer.c`; log metadata persistence is handled by userspace.

## Dependencies And Integration Points
Consumers must include kernel integer and size definitions through surrounding includes. The declarations bind the userspace dirty-log base implementation to the connector-backed transport implementation and the dm-log-userspace protocol structures from kernel headers.

## Risks
The API exposes raw `char *` payload pointers and value-result sizes, so caller and transport must agree on request-specific layouts and buffer capacities. The header-level `DM_MSG_PREFIX` affects logging in any file that includes it before using dm logging macros.

## Test Signals
Build `dm-log-userspace-base.c` and `dm-log-userspace-transfer.c` together, verify no duplicate message-prefix conflicts, and compile module init/exit paths with connector support enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-log-userspace-transfer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-log-writes.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-log-writes.c

## Purpose
Implements the `log-writes` device-mapper target, which forwards I/O to a data device while recording completed writes, flushes, FUA writes, discards, metadata writes, and user marks to a sequential log device. The log is intended for replay tools that validate filesystem consistency at chosen points.

## Important APIs, Types, And Functions
On-media structures are `struct log_write_super` and `struct log_write_entry`. `struct log_writes_c` tracks data/log devices, sector size, next log sector, entry count, pending/logging queues, inflight counters, logging state, and the logger kthread. `struct pending_block` holds copied write data or mark payloads. `log_writes_ctr()` opens devices and starts `log_writes_kthread()`. `log_writes_map()` copies write bio contents into private pages, records flush/FUA/discard flags, and maps the original bio to the data device. `normal_end_io()` moves completed writes to unflushed or logging queues. `log_one_block()`, `write_metadata()`, `write_inline_data()`, and `log_super()` write log entries. `log_writes_message()` supports `mark <data>`.

## Control Flow
Writes are logged after lower-device completion. Non-FUA writes enter `unflushed_blocks`; FUA and flush-associated writes enter `logging_blocks` immediately. A pure flush splices all unflushed blocks ahead of the flush marker so the log approximates durable order. The kthread drains `logging_blocks`, reserves space, writes metadata and data to the log device, updates the super on FUA/mark entries, and disables logging on log I/O errors or log-device exhaustion. Reads and uninteresting bios pass through.

## State And Persistence
Runtime state lives in queues, counters, and copied bio pages. Persistent state is a simple sequential log: sector 0 superblock with magic/version/entry count/sector size, followed by one-sector entries and optional data payloads. Log writes are append-only until the log device fills.

## Dependencies And Integration Points
Depends on device-mapper target hooks, block bio submission/completion, kthreads/freezer, DAX passthrough, queue-limit hints, target messages, and user-space replay tooling that understands the log format.

## Risks
The target must copy bio data before forwarding because original pages may disappear. Log space accounting must match metadata/data sector conversion. If log writes fail, logging is disabled while data I/O continues, so status must be monitored. Discards are logged by completion order and can be emulated if the data device lacks discard support. Superblock updates are synchronous via completion to avoid stale entry counts.

## Test Signals
Run write/flush/FUA/discard ordering tests, mark message tests, log replay validation, log-device-full behavior, log I/O error behavior, teardown with pending blocks, pure flush and flush-with-data cases, unsupported discard emulation, status output, ioctl forwarding size checks, DAX hook builds, and freezer/kthread stop handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-log-writes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-log.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-log.c

## Purpose
Provides the dirty-region-log registry plus built-in `core` and `disk` dirty-log implementations used by dm mirror-style targets to track clean, dirty, syncing, and recovering regions. The `core` log is volatile; the `disk` log persists clean-region state on a log device.

## Important APIs, Types, And Functions
Registry APIs are `dm_dirty_log_type_register()`, `dm_dirty_log_type_unregister()`, `dm_dirty_log_create()`, and `dm_dirty_log_destroy()`. `get_type()` requests `dm-log-<type>` modules with suffix fallback. `struct log_c` stores region geometry, clean/sync/recovering bitsets, sync mode, dm-io request state, and disk-log header/device fields. Disk metadata uses `struct log_header_disk` with `MIRROR_MAGIC`, version, and region count. Constructors include `core_ctr()` and `disk_ctr()` via `create_log_context()`. Operations cover resume, flush, mark/clear, clean/in-sync queries, resync work, region sync updates, sync count, and status.

## Control Flow
Creation loads and references a log type, allocates context, validates region size, allocates bitsets, and optionally opens/initializes a log device and dm-io client. Disk resume reads the on-disk header, handles new/incompatible logs, adjusts region bits for grown/shrunk devices, copies clean bits to sync bits, and writes/flushed the updated header. Runtime mark clears clean bits; clear sets clean bits unless a previous flush failure made cleanliness unknowable. Resync scans zero sync bits while avoiding regions already marked recovering.

## State And Persistence
`core` state is entirely in memory and lost on reload. `disk` state persists header plus clean bitset in the log device starting after `LOG_OFFSET`; sync and recovering bitsets remain runtime. Flags `log_dev_failed`, `log_dev_flush_failed`, and `flush_failed` influence status and conservative behavior.

## Dependencies And Integration Points
Depends on dm dirty-log interfaces, dm-io, vmalloc bitsets, module loading, device-mapper table events, and mirror callbacks for flushing target data before marking regions clean on persistent logs.

## Risks
Region-size validation and bitset sizing must match target length. Disk flush failure forces all regions dirty because clean state cannot be trusted. Persistent header version is not backward-compatible except little-endian v1 promotion. Error paths must fail the log device and trigger table events. Bit operations use little-endian layout to preserve disk format.

## Test Signals
Test registry duplicate/unregister behavior, module autoload fallback names, core and disk constructors, invalid region sizes, sync/nosync modes, disk log read/write/flush failures, device grow/shrink handling, resync scanning and recovering bits, status for healthy/degraded/flush-failed logs, and mirror behavior after flush callback failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-mpath.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-mpath.c

## Purpose
Implements the device-mapper `multipath` target. It routes I/O across multiple paths grouped into priority groups, delegates path choice to pluggable path selectors, integrates SCSI device handlers for path-group activation, handles failover/reinstatement, supports request-based and bio-based queue modes, and exposes messages/status/ioctls for multipath management.

## Important APIs, Types, And Functions
`struct pgpath` wraps a `dm_path`, active flag, fail count, owning priority group, and activation work. `struct priority_group` owns a `path_selector` and path list. `struct multipath` tracks flags, current/next PG/path, valid path count, queue mode, hardware-handler settings, work items, queued bios, wait queues, and no-path timer. Constructor parsing is split across `parse_features()`, `parse_hw_handler()`, `parse_priority_group()`, `parse_path_selector()`, and `parse_path()`. Mapping uses `multipath_clone_and_map()` for request-based mode and `multipath_map_bio()`/`__multipath_map_bio()` for bio mode. Path state changes use `fail_path()`, `reinstate_path()`, `bypass_pg()`, `switch_pg_num()`, and `pg_init_done()`.

## Control Flow
Constructor parses feature arguments, chooses queue mode, attaches path selectors/devices, initializes SCSI device-handler activation where needed, and sets the initial priority group. Mapping selects `current_pgpath` or calls `choose_pgpath()`, queues/requeues if path-group initialization is needed or no paths are available, and invokes selector `start_io`. End I/O reports selector `end_io`, fails paths on transport errors, and requeues or completes based on queue-if-no-path and valid-path state. Workqueues resubmit queued bios, run path activation, and trigger dm events.

## State And Persistence
All state is runtime only: flags, valid path counts, fail counts, selected PG/path, queued bios, handler activation counters, and timer state. There is no disk metadata. Userspace multipathd or dm table reloads are responsible for persistent policy.

## Dependencies And Integration Points
Depends on dm core target hooks, request-based dm-rq, per-bio metadata, path-selector registry, SCSI device handler APIs, block-mq request allocation, uevents, workqueues, timers, module parameters, and dm ioctl command `DM_MPATH_PROBE_PATHS`.

## Risks
Concurrency is complex: spinlocks, atomics, workqueues, timers, and suspend paths coordinate path switching and queued I/O. Incorrect queue-if-no-path handling can hang I/O indefinitely or fail I/O prematurely. Hardware handler activation may need retries and delayed switching. Bio-based queued bios require saved/restored bio details. Path selector callbacks must be balanced for start/end I/O. `queue_if_no_path_timeout_secs` changes failure behavior globally.

## Test Signals
Exercise both `queue_mode rq/mq` and `queue_mode bio`, path selector modules, no-path queueing and timeout, fail/reinstate/switch/disable/enable messages, SCSI handler success/retry/temp-busy/offline errors, suspend/resume with and without noflush, path probing ioctl, path failure during map/end I/O, status/IMA output, and concurrent path changes under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-mpath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-mpath.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-mpath.h

## Purpose
Shared private header for multipath path objects. It defines the minimal path structure visible to path selector modules and declares the callback used by hardware handler path-group initialization completion.

## Important APIs, Types, And Functions
`struct dm_path` contains a read-only `struct dm_dev *dev` and opaque `pscontext` for path-selector-private state. `dm_pg_init_complete(struct dm_path *path, unsigned int err_flags)` is declared for device-handler users that need to report path-group initialization completion.

## Control Flow
The header has no runtime flow. `dm-mpath.c` embeds `struct dm_path` in its internal `struct pgpath`, passes it to path selector callbacks, and converts back with `container_of()`. Path selectors store per-path state through `pscontext`.

## State And Persistence
Only in-memory path references are represented. There is no persistence and no ownership management in this header; target construction/destruction in `dm-mpath.c` owns device references.

## Dependencies And Integration Points
Included by `dm-path-selector.h` and path selector implementations. It bridges multipath internals and selector modules while keeping most multipath state private to `dm-mpath.c`.

## Risks
The `dev` field is documented read-only; selector modules must not drop or replace the device reference. `pscontext` lifetime must be managed consistently by selector `add_path`, `fail_path`, `reinstate_path`, and `destroy` callbacks.

## Test Signals
Compile all path selector modules against this header, validate selector private context lifetime on path add/fail/reinstate/destroy, and verify any users of `dm_pg_init_complete()` match the multipath path lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-mpath.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-path-selector.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-path-selector.c

## Purpose
Implements the registry for dm multipath path selector types. Selectors such as round-robin or service-time register a `struct path_selector_type`; the multipath target looks them up by name during table construction.

## Important APIs, Types, And Functions
`struct ps_internal` copies a public `path_selector_type` and links it into `_path_selectors`. `_ps_lock` is an rwsem protecting the registry. `__find_path_selector_type()` searches by name. `dm_get_path_selector()` tries the current registry, requests module `dm-<name>` if absent, and returns a module-referenced type. `dm_put_path_selector()` drops the module reference if the type remains registered. `dm_register_path_selector()` rejects duplicate names and stores a copied descriptor. `dm_unregister_path_selector()` removes and frees the internal copy.

## Control Flow
Path selector modules call register at module init and unregister at exit. Multipath construction calls `dm_get_path_selector()`, then invokes the returned type's `create` and `add_path` callbacks. Destruction calls selector `destroy` and `dm_put_path_selector()`. Lookup uses a read lock plus `try_module_get()`; registration/unregistration use the write lock.

## State And Persistence
State is a process-lifetime in-kernel linked list of registered selector descriptors. There is no persistence. The registry stores a copy of the descriptor, not the caller's original object.

## Dependencies And Integration Points
Depends on Linux module reference counting, rwsems, list APIs, slab allocation, and `dm-path-selector.h`. It integrates directly with `dm-mpath.c` constructor/destructor flows and selector modules named for `request_module("dm-%s")`.

## Risks
Unregistering a selector still in use would be unsafe unless module references prevent module exit. The copied descriptor means later mutations to the original type object are not reflected. `dm_put_path_selector()` searches by name before module_put; mismatched names or double unregister can trigger warnings or leaks.

## Test Signals
Test duplicate registration, unregister unknown selector warning, module autoload by name, module reference balancing across table create/destroy failures, concurrent lookup/register/unregister, and multipath table construction with missing selector modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-path-selector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-path-selector.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-path-selector.h

## Purpose
Defines the path selector interface used by the dm multipath target and selector modules. It abstracts how a priority group chooses a path and how selector-specific state is created, updated, reported, and notified of I/O lifecycle.

## Important APIs, Types, And Functions
`struct path_selector` stores a selector type and opaque context. `struct path_selector_type` contains the selector name, owning module, feature flags, status argument counts, and callbacks: `create`, `destroy`, `add_path`, `select_path`, `fail_path`, `reinstate_path`, `status`, optional `start_io`, and optional `end_io`. `DM_PS_USE_HR_TIMER` requests high-resolution bio timing for selectors that use elapsed I/O time. Registry functions are declared: `dm_register_path_selector()`, `dm_unregister_path_selector()`, `dm_get_path_selector()`, and `dm_put_path_selector()`.

## Control Flow
Multipath obtains a selector type, calls `create`, adds each path with selector arguments, calls `select_path` during mapping, notifies `start_io`/`end_io` around I/O where implemented, calls failure/reinstate callbacks on path state changes, and asks `status` to format table/info/IMA details.

## State And Persistence
The header defines contracts for in-memory selector contexts only. Persistence is outside this interface and normally represented by dm table arguments emitted through `status`.

## Dependencies And Integration Points
Includes `linux/device-mapper.h` and `dm-mpath.h` for `struct dm_path`. It is consumed by `dm-mpath.c`, the selector registry, and individual selector modules.

## Risks
Selector callbacks run in performance-sensitive and sometimes constrained contexts. `select_path` returning NULL drives failover/no-path behavior. `start_io` and `end_io` must be balanced and tolerate requeue/error paths. Status argument counts must match emitted table/info fields or userspace parsers break.

## Test Signals
Compile selector modules, validate callback contracts with path failures and requeues, verify high-resolution timing flag behavior in bio mode, check table/status argument counts, and run multipath I/O tests for every registered selector.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-path-selector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/Kconfig

## Purpose
Adds the `DM_PCACHE` kernel configuration option for an experimental persistent-cache device-mapper target that uses persistent memory or DAX-capable devices as a low-latency cache in front of block devices.

## Important APIs, Types, And Functions
Defines `config DM_PCACHE` as a tristate named "Persistent cache for Block Device (Experimental)". It depends on `BLK_DEV_DM` and `DEV_DAX`. The help text identifies persistent memory/CXL/DAX devices as cache media and warns that the feature is experimental.

## Control Flow
Kconfig participates in build-time selection only. When enabled as built-in or module, the `Makefile` builds `dm-pcache.o` from the persistent-cache source set. When disabled, none of the pcache target code is compiled.

## State And Persistence
No runtime state is defined here. The option controls whether pcache's runtime and on-media metadata code can exist in the kernel build.

## Dependencies And Integration Points
Integrates with the Linux Kconfig system under device-mapper drivers. `BLK_DEV_DM` supplies the target framework and `DEV_DAX` supplies direct-access persistent-memory support required by `cache_dev.c`.

## Risks
The feature is marked experimental and depends on DAX; enabling it without suitable hardware or test coverage risks exposing unfinished target behavior. Missing dependency declarations would cause build failures because the source uses DAX and dm APIs directly.

## Test Signals
Run Kconfig builds with `DM_PCACHE=n/m/y`, verify dependencies select or hide the option correctly, build with `DEV_DAX` disabled to ensure exclusion, and load the module only on systems with appropriate DAX-capable cache devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/Makefile -->
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/Makefile

## Purpose
Defines how the persistent-cache device-mapper target is built. It aggregates the pcache target, cache device, segment, backing device, cache metadata, garbage collection, writeback, cache segment, key, and request handling objects into one `dm-pcache.o` module or built-in object.

## Important APIs, Types, And Functions
`dm-pcache-y` lists component objects: `dm_pcache.o`, `cache_dev.o`, `segment.o`, `backing_dev.o`, `cache.o`, `cache_gc.o`, `cache_writeback.o`, `cache_segment.o`, `cache_key.o`, and `cache_req.o`. `obj-$(CONFIG_DM_PCACHE) += dm-pcache.o` binds the aggregate to the Kconfig option.

## Control Flow
This is build-system control flow only. If `CONFIG_DM_PCACHE` is enabled, Kbuild compiles the listed objects and links them as the pcache module or built-in component.

## State And Persistence
No runtime state. The object list determines which source files contribute runtime state and on-media metadata handlers to the final target.

## Dependencies And Integration Points
Integrates with Kbuild and the `DM_PCACHE` Kconfig symbol. The aggregate depends on source-level initialization ordering inside `dm_pcache.o` and module init/exit functions.

## Risks
Forgetting an object causes unresolved symbols or missing behavior, especially because the visible files call helpers in `segment`, `cache_writeback`, `cache_segment`, and `dm_pcache`. Adding new source files requires updating this list.

## Test Signals
Build `CONFIG_DM_PCACHE=m` and `=y`, inspect linked symbols for all pcache subsystems, and run modpost to catch missing or stale object entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/backing_dev.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/backing_dev.c

## Purpose
Implements asynchronous I/O submission and completion handling for pcache's backing block device. It creates cloned requests from upper bios or kmem-backed bios for cache writeback/read-miss operations, submits them to the lower device, and completes pcache request accounting.

## Important APIs, Types, And Functions
Global slab caches are `backing_req_cache` and `backing_bvec_cache`. `backing_dev_start()` initializes request/bvec mempools, submit/complete lists, work items, inflight counters, and backing device size. `backing_dev_stop()` waits for inflight requests and flushes work. `backing_dev_req_alloc()`, `backing_dev_req_init()`, and `backing_dev_req_create()` build either `BACKING_DEV_REQ_TYPE_REQ` cloned-bio requests or `BACKING_DEV_REQ_TYPE_KMEM` mapped-memory bios. `backing_dev_req_submit()` queues or directly submits bios. `backing_dev_bio_end()` records errno and queues completion. `backing_dev_req_end()` invokes callbacks, releases upper requests or bvecs, frees the request, and wakes shutdown waiters. `backing_dev_flush()` issues a lower flush.

## Control Flow
Requests are allocated from mempools and increment `inflight_reqs`. Non-direct submissions are added to `submit_list` and drained by `req_submit_fn()` on the pcache workqueue. Bio completion moves the request to `complete_list` and queues `req_complete_fn()`, which calls final callbacks and releases references. Type-specific initialization trims cloned upper bios or maps kernel memory/vmalloc/DAX-backed memory into bio vectors.

## State And Persistence
All state is runtime queueing and request accounting. There is no metadata persistence here. Data persistence is achieved through lower-device bios and explicit flushes invoked by higher layers.

## Dependencies And Integration Points
Depends on block bio APIs, dm device references initialized by `dm_pcache`, pcache request refcounting, mempools/slab caches, workqueues, vmalloc page translation, DAX/vmap range flushing, and cache/backing ownership macros.

## Risks
Mapped kmem/vmalloc ranges must be represented by valid pages and bio vector counts. Inflight accounting must balance on every allocation/free path or shutdown can hang. Direct submission bypasses the submit workqueue but still completes asynchronously. The use of `BUG_ON` in bio mapping and type dispatch turns unexpected inputs into kernel crashes. Request trimming requires sector-aligned offsets and lengths.

## Test Signals
Test req and kmem request types, inline and pooled bvec paths, vmalloc and direct-mapped memory, direct versus queued submit, completion callback errors, upper request refcount balancing, shutdown waiting with inflight I/O, lower flush, allocation failure paths, and sector alignment assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/backing_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/backing_dev.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/backing_dev.h

## Purpose
Declares pcache backing-device request structures and APIs. It is the contract between cache request handling/writeback code and the lower block-device I/O layer implemented in `backing_dev.c`.

## Important APIs, Types, And Functions
`struct pcache_backing_dev_req` embeds a `bio`, request type, backing-device pointer, callback/private data, list node, result, and either upper-request clone metadata or kmem bvec metadata. `struct pcache_backing_dev` stores dm device, mempools, submit/complete queues, work items, inflight counters, waitqueue, and device size. `struct pcache_backing_dev_req_opts` describes request allocation/init options for upper-request or kmem I/O. APIs include `backing_dev_start()`, `backing_dev_stop()`, `backing_dev_req_submit()`, `backing_dev_req_end()`, allocation/init/create helpers, `backing_dev_flush()`, and module-level slab init/exit. `backing_dev_req_coalesced_max_len()` limits vmalloc/DAX-page coalescing to a single pgmap run.

## Control Flow
Callers allocate and initialize requests from options, submit directly or via queueing, and receive callback completion with an errno-style result. Shutdown uses inflight accounting exposed through `pcache_backing_dev`.

## State And Persistence
Defines runtime request and queue state only. No on-media metadata is represented.

## Dependencies And Integration Points
Includes device-mapper and pcache internal definitions. It integrates cache miss/read/writeback logic with block-device submission while hiding bio construction details.

## Risks
The embedded bio and union require callers to select the correct type and option fields. `backing_dev_req_coalesced_max_len()` is important for vmalloc mappings across device-private page maps; ignoring it could create invalid bios. Callback ownership of `priv_data` must be precise to avoid leaks or double puts.

## Test Signals
Compile all users of both request types, stress vmalloc coalescing boundaries, verify callback/private-data lifetime, and validate inflight accounting across allocation failures and completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/backing_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache.c

## Purpose
Initializes and tears down the core pcache cache state: cache metadata discovery, segment initialization, tail/head positions, request key trees, per-CPU data heads, writeback/GC scheduling, and global cache-key slab setup.

## Important APIs, Types, And Functions
`key_cache` is the global slab for `pcache_cache_key`. `cache_info_init()` finds the latest persisted `pcache_cache_info`, validates immutable options such as data CRC, or creates defaults. `cache_info_write()` writes the next indexed metadata copy with CRC/sequence. `cache_pos_encode()`/`cache_pos_decode()` persist and recover key/dirty tail positions. `cache_init()`, `cache_segs_init()`, `cache_tail_init()`, and `cache_init_req_keys()` allocate runtime structures, initialize segments, decode or create tail positions, build request trees/ksets, allocate per-CPU data heads, and replay persisted keys. `pcache_cache_start()` wires cache/backing/cache-dev state, starts writeback and GC, marks init done, and persists cache info. `pcache_cache_stop()` flushes ksets, stops GC/writeback, destroys trees, and frees memory.

## Control Flow
Startup first allocates arrays/bitmaps/locks/work, points metadata addresses into the DAX cache device, initializes cache info, walks segment chains, initializes tails, replays keysets into rbtrees, initializes writeback, writes `INIT_DONE`, and queues GC. Shutdown flushes pending keysets, cancels GC, flushes clean work, exits writeback, destroys request keys if initialized, and frees segment state.

## State And Persistence
Persistent metadata includes redundant cache-info records, cache control tail positions, segment metadata, and keysets stored in DAX media. Runtime state includes segment arrays, bitmaps, rbtrees, per-CPU allocation heads, locks, work items, and writeback/GC contexts.

## Dependencies And Integration Points
Depends on `cache_dev` DAX mappings, backing-device size, segment helpers, metadata CRC helpers from pcache internals, key replay in `cache_key.c`, request handling in `cache_req.c`, writeback, and GC.

## Risks
Startup ordering is critical: tail decode and key replay depend on segments being initialized. Data CRC mode cannot change after formatting. New-cache initialization reserves segment 0 for metadata and writes redundant tail metadata. Failure cleanup must match partially initialized structures. `n_subtrees` scales with backing size and can become large.

## Test Signals
Test first-format and existing-cache starts, data_crc option mismatch, corrupted cache info/tails, segment-chain errors, key replay failures, low-memory cleanup paths, writeback init failure, clean shutdown with pending ksets, GC scheduling, and `pcache_cache_set_gc_percent()` bounds/persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache.h

## Purpose
Defines the pcache cache data model, on-media metadata formats, cache modes, segment/key/keyset structures, tree-walk contracts, and public APIs shared by cache initialization, key replay, request handling, GC, writeback, and segment management.

## Important APIs, Types, And Functions
Key constants define GC thresholds, subtree size, keyset limits, segment limits, writeback/GC intervals, cache modes, and metadata flags. On-media structures include `pcache_cache_pos_onmedia`, `pcache_cache_seg_ctrl`, `pcache_cache_info`, `pcache_cache_key_onmedia`, and `pcache_cache_kset_onmedia`. Runtime structures include `pcache_cache_pos`, `pcache_cache_segment`, `pcache_cache_subtree`, `pcache_cache_tree`, `pcache_cache_key`, `pcache_cache_kset`, `pcache_cache`, `pcache_cache_ctrl`, and per-CPU `pcache_cache_data_head`. Inline helpers cover subtree selection, media addresses, keyset selection, key state, position copying, segment-control detection, key trimming/deletion, CRC checks, cache mode/GC percent fields, key ranges, and tail encode/decode wrappers.

## Control Flow
The header establishes contracts rather than running logic. Request handling uses `cache_subtree_walk()` callback slots to classify before/after/overlap cases. Writers append keysets, readers submit miss requests, GC advances tails and segment references, and writeback advances dirty tails using the declared APIs.

## State And Persistence
This header describes both volatile and persistent state. Persistent state is stored in DAX cache media with CRC/sequence protection for selected records and keyset CRCs. Runtime state includes rbtrees, locks, refs, delayed work, segment maps, and per-CPU heads.

## Dependencies And Integration Points
Depends on `segment.h`, pcache metadata helpers, kernel rbtrees, mempools, workqueues, CRC32C, DAX flush assumptions, backing/cache-dev structures, and `dm_pcache` ownership macros.

## Risks
On-media layouts are ABI-like; changing sizes or fields can break existing cache devices. Inline key deletion erases rb nodes and drops refs, so callers must hold tree locks. `cache_key_invalid()` relies on segment generations advanced by GC. Subtree selection assumes requests are split at 4 MiB boundaries. Several helpers use `BUG_ON`, reflecting strict internal invariants.

## Test Signals
Build all pcache objects, validate on-media struct sizes/CRCs, exercise each cache mode flag, subtree boundary splitting, key trimming/deletion under locks, generation invalidation, tail encode/decode redundancy, GC percent field bounds, and data CRC enabled/disabled replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_dev.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_dev.c

## Purpose
Initializes and manages the persistent-memory/DAX cache device used by pcache. It maps the DAX device into kernel virtual memory, formats or validates the pcache superblock, zeros metadata areas on first format, and tracks free cache segments.

## Important APIs, Types, And Functions
`cache_dev_dax_init()` validates minimum size, tries `dax_direct_access()` for a contiguous mapping, and falls back to `build_vmap()` for non-contiguous PFNs. `cache_dev_dax_exit()` unmaps vmap fallback. `cache_dev_zero_range()` zeroes and flushes DAX memory. Superblock helpers `sb_read()`, `sb_write()`, `sb_init()`, and `sb_validate()` handle magic, CRC, endian flags, segment count, and metadata zeroing. `cache_dev_start()` maps DAX, reads/formats/validates the superblock, initializes segment bitmap, and writes the new superblock after successful init. `cache_dev_stop()` frees bitmap and mapping. `cache_dev_get_empty_segment_id()` allocates a free segment id under `seg_lock`.

## Control Flow
Startup maps the full DAX block device, reads the superblock with machine-check-safe copy, formats if magic is zero, validates magic/CRC/endian, allocates the segment bitmap, and persists the superblock only after all validation/initialization succeeds. Formatting computes segment count from bytes after metadata offsets and zeroes cache-info/control metadata regions.

## State And Persistence
Persistent state includes `pcache_sb` at `PCACHE_SB_OFF`, cache-info/control areas, and data segments. Runtime state includes mapping pointer, `use_vmap`, segment count, segment bitmap, dm device, and segment lock.

## Dependencies And Integration Points
Depends on DAX direct access/read locking, PFN validity, vmap/vunmap, persistent-memory flush primitives, machine-check-safe copies, block device size helpers, CRC32C, and pcache cache metadata layout macros from `cache_dev.h`/`cache.h`.

## Risks
The full-device DAX mapping assumes stable direct access during target lifetime. Endianness is a format constraint; moving media across endian types is rejected. Formatting occurs when magic is zero and destroys prior metadata areas. Segment allocation only sets bits; freeing is handled by cache GC/segment code. `pfn_valid()` rejection limits device compatibility.

## Test Signals
Test too-small devices, contiguous and vmap DAX mappings, `dax_direct_access()` errors, invalid PFNs, blank-device format, corrupted magic/CRC/endian flags, segment count computation, metadata zeroing/flushing, bitmap allocation failure cleanup, segment allocation exhaustion, and stop/unmap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_dev.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_dev.h

## Purpose
Declares the pcache DAX cache-device layout, superblock format, runtime cache-device state, and cache-device management APIs.

## Important APIs, Types, And Functions
Defines `PCACHE_MAGIC`, superblock/cache-info/cache-control/segment offsets and sizes, minimum cache device size, 16 MiB segment size, and address macros such as `CACHE_DEV_SB()`, `CACHE_DEV_CACHE_INFO()`, `CACHE_DEV_CACHE_CTRL()`, `CACHE_DEV_SEGMENTS()`, and `CACHE_DEV_SEGMENT()`. `PCACHE_SB_F_BIGENDIAN` records media endianness. `struct pcache_sb` stores CRC, flags, magic, and segment count. `struct pcache_cache_dev` stores flags, segment count, DAX mapping, vmap mode, dm device, segment lock, and segment bitmap. APIs include `cache_dev_start()`, `cache_dev_stop()`, `cache_dev_zero_range()`, and `cache_dev_get_empty_segment_id()`.

## Control Flow
No runtime flow is implemented here. Other pcache files use these macros to locate persistent metadata and segment data within the mapped DAX device.

## State And Persistence
The header defines the persistent layout root for pcache. Offsets reserve space for redundant metadata and then segment data. Runtime state mirrors the mapped device and allocation bitmap.

## Dependencies And Integration Points
Depends on device-mapper device references, DAX-capable lower devices, and pcache internal ownership macros. `cache.c`, `cache_key.c`, `cache_gc.c`, and segment code use the layout macros to persist and replay cache state.

## Risks
Offset and size definitions are on-media format contracts. Changing them without migration would make existing cache devices unreadable. Segment size and minimum size determine capacity and metadata overhead. Endianness flags must be validated before interpreting metadata.

## Test Signals
Validate layout offsets, segment address calculations, superblock CRC coverage, endian flag handling, minimum-size enforcement, and successful compilation of all users of the runtime struct and APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_gc.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_gc.c

## Purpose
Implements pcache garbage collection for keyset metadata and cache segment references. It advances the key tail after the dirty tail has moved far enough and the used-segment percentage crosses the configured GC threshold, releasing segment references held by old cache keys.

## Important APIs, Types, And Functions
`cache_key_gc()` drops the segment reference for a decoded key. `need_gc()` compares dirty-tail and key-tail positions, reads the next keyset from DAX media, validates magic and CRC, and checks used segment count against `pcache_cache_get_gc_percent()`. `last_kset_gc()` handles `PCACHE_KSET_FLAGS_LAST` records by moving the key tail to the next segment and clearing the old segment bit. `pcache_cache_gc_fn()` is the delayed-work entry that loops through eligible keysets, decodes each key, releases references, advances and persists key tail, and requeues itself.

## Control Flow
GC snapshots dirty tail and key tail under their mutexes, calls `need_gc()`, then either handles a segment-transition keyset or walks each key in the current keyset. Decode failure increments `gc_errors` and permanently stops future GC to avoid retrying partially processed metadata. Successful processing advances `cache->key_tail` by the keyset on-media size and writes the new tail position. When no more work is needed, delayed work is queued after `PCACHE_CACHE_GC_INTERVAL`.

## State And Persistence
Persistent state affected by GC is the encoded key-tail position and segment allocation bitmap state indirectly represented by segment metadata. Runtime state includes `gc_errors`, `gc_kset_onmedia_buf`, segment references, and `seg_map`.

## Dependencies And Integration Points
Depends on keyset CRC helpers, cache position encode/decode, segment references from cache segment code, DAX `copy_mc_to_kernel()`, dirty-tail advancement by writeback, and pcache stopping state.

## Risks
GC correctness depends on dirty tail never lagging behind data that still needs writeback. Decode errors stop GC to avoid corrupting state but can fill the cache. `last_kset_gc()` clears segment map bits after moving to the next segment; incorrect tail comparisons could reuse live key metadata. Used-segment threshold controls aggressiveness and defaults to 70 percent.

## Test Signals
Test threshold behavior below/above GC percent, corrupted keyset magic/CRC, last-keyset segment transitions, dirty-tail equals key-tail no-op, decode failure setting `gc_errors`, stopping behavior, repeated requeue interval, segment reference release, and persistence of advanced key tail across restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_gc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_key.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_key.c

## Purpose
Manages pcache cache keys: allocation/refcounting, on-media encode/decode, keyset append/flush, rb-tree search and overlap fixup, invalid-key cleanup, keyset replay during startup, and cache tree lifecycle.

## Important APIs, Types, And Functions
`cache_key_alloc()`, `cache_key_get()`, and `cache_key_put()` manage mempool-backed keys. `cache_key_encode()`/`cache_key_decode()` convert between runtime keys and `pcache_cache_key_onmedia`, optionally checking data CRCs. `cache_kset_close()` writes accumulated keysets to the key-head position, inserts `LAST` keysets when crossing segments, and flushes persistent memory. `cache_key_append()` selects a kset by offset and schedules delayed flushing or closes full/FUA keysets. `cache_subtree_search()` and `cache_subtree_walk()` provide ordered overlap traversal. `cache_key_insert()` fixes overlapping keys before rb insertion. `clean_fn()` removes generation-invalid keys. `kset_flush_fn()` retries failed keyset closure. `cache_replay()` scans persisted keysets from key tail and rebuilds request trees.

## Control Flow
Writes/read-miss fills append keys to per-kset buffers, which are written to DAX media as keysets. On insertion with fixup, existing overlapping keys are trimmed, split, or deleted so the tree contains non-overlapping current ranges. Replay reads keysets until invalid magic/CRC, follows `LAST` records across segments, decodes valid keys, marks used segments, inserts keys if their segment generation is current, and updates key head to the replay stop point.

## State And Persistence
Persistent state is the sequence of keysets in cache segments, including `LAST` records linking segments. Runtime state is rbtrees partitioned by logical range, key refs, kset buffers, delayed flush work, and segment refs. Generation numbers allow GC to invalidate old keys lazily.

## Dependencies And Integration Points
Depends on cache metadata/CRC helpers, segment allocation/refcounting, persistent memory flushes, rbtrees, mempools, workqueues, DAX safe copy, and request/GC/writeback code that consumes trees.

## Risks
Overlap fixup is subtle and tree-lock dependent; incorrect trimming can expose stale data or lose current data. `cache_kset_close()` can return `-EBUSY` when no segment is available, requiring retry. Replay trusts keyset CRC/magic boundaries and optional data CRC. There is a likely typo in `SUBTREE_WALK_RET_RESEARCH`, but it consistently means restart search. Several paths use `BUG()` for impossible states.

## Test Signals
Test insertion overlap cases (tail/head/contain/contained), empty placeholder behavior, keyset full and forced closure, segment rollover with `LAST`, replay after restart, corrupted keyset and data CRC, invalid generation cleanup, allocation fallback with preallocated keys, delayed flush retry on `-EBUSY`, and large tree teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_req.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_req.c

## Purpose
Handles pcache read/write requests against the in-memory key tree and persistent-memory cache data. Reads are satisfied from cached keys when possible and otherwise issue backing-device reads that can populate cache placeholders. Writes allocate cache space, copy bio data into persistent memory, insert replacement keys, and append key metadata.

## Important APIs, Types, And Functions
`cache_data_head_init()` and `cache_data_alloc()` allocate data space from per-CPU cache segment heads without crossing segment boundaries. `cache_copy_from_req_bio()` and `cache_copy_to_req_bio()` transfer data between bios and cache segments while checking segment generation. Miss handling uses `cache_miss_req_alloc()`, `cache_miss_req_init()`, `submit_cache_miss_req()`, `cache_miss_req_free()`, and `miss_read_end_req()`. Read overlap callbacks (`read_before`, `read_overlap_tail`, `read_overlap_contain`, `read_overlap_contained`, `read_overlap_head`) drive `cache_subtree_walk()`. `cache_read()` splits requests by subtree and submits backing reads for misses. `cache_write()` allocates keys/data and inserts/appends them. `pcache_cache_flush()` closes all ksets. `pcache_cache_handle_req()` dispatches flush/read/write.

## Control Flow
Reads build a temporary requested key and walk the relevant subtree. Cached non-empty keys copy data into the upper bio; empty placeholder keys cause backing reads without inserting new placeholders; missing gaps allocate backing reads with empty keys that are inserted before submission. On read completion, a still-empty placeholder is allocated cache data, filled from the upper bio, marked clean, appended to keysets, and retained unless a write deleted it meanwhile. Writes split at 4 MiB subtree boundaries, allocate data space, copy bio contents to DAX cache, insert with overlap fixup, and append key metadata, forcing keyset close on FUA.

## State And Persistence
Runtime state includes per-CPU data heads, pending backing requests, placeholders, tree locks, and request refs. Persistent state is data copied into cache segments plus keysets appended by `cache_key_append()`. Flush closes keysets but lower backing flush/writeback is handled by other subsystems.

## Dependencies And Integration Points
Depends on backing-device request APIs, segment copy helpers, cache key/tree APIs, pcache request refcounting, bio flags, and writeback/GC generation management.

## Risks
Read-miss placeholder races with concurrent writes are handled by checking `cache_key_empty()` under the tree lock, but this is a critical correctness path. Segment generation checks prevent copying from reclaimed data; failure deletes stale keys and restarts. Data allocation may shorten keys at segment boundaries, requiring outer loops. Error paths must release segment refs and key refs exactly. Prefetch reads populate cache from the same upper bio data after backing completion, so request lifetime is important.

## Test Signals
Test full hits, full misses, mixed overlap reads, concurrent read miss and write overwrite, stale generation deletion/research, subtree boundary splits, segment boundary splits, FUA forced keyset close, flush-only requests, allocation failures for preallocated miss requests, backing read errors deleting placeholders, and data CRC replay after writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_req.c -->
