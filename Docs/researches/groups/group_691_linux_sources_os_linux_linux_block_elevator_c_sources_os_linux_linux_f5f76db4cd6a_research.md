# Group Research: group_691_linux_sources_os_linux_linux_block_elevator_c_sources_os_linux_linux_f5f76db4cd6a

Scope confirmed against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`, which is included in subset A. The referenced grouped report file did not exist, so this report is produced from direct full-file reads.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/elevator.c -->
# File Research: sources/os/linux/linux/block/elevator.c

Implements the block-layer elevator/I/O scheduler core: scheduler registration, queue attachment/detachment, request merge helpers, scheduler sysfs exposure, and runtime scheduler switching.

Key responsibilities:
- Maintains the global registered scheduler list under `elv_list_lock`.
- Provides merge primitives around `q->last_merge`, the elevator hash, scheduler-specific merge callbacks, and request RB-tree helpers.
- Owns `struct elevator_queue` allocation/release, including module references and kobject lifetime.
- Registers scheduler attributes under queue sysfs as `iosched` and coordinates debugfs registration.
- Switches schedulers through queue freeze/quiesce, `q->elevator_lock`, and `tag_set->update_nr_hwq_lock`.

Important functions:
- `elv_merge()`, `elv_attempt_insert_merge()`, `elv_merged_request()`, `elv_merge_requests()` implement the core merge path.
- `elv_rqhash_*()` and `elv_rb_*()` provide reusable scheduler indexing primitives.
- `elv_register()` / `elv_unregister()` manage scheduler types and optional `io_cq` slab caches.
- `elevator_change()`, `elevator_switch()`, `elv_update_nr_hw_queues()` handle scheduler replacement.
- `elv_iosched_show()` / `elv_iosched_store()` back the queue scheduler sysfs attribute.
- `elevator_set_default()` defaults single-queue or shared-tag devices to `mq-deadline` when available.

Concurrency/lifetime notes:
- Scheduler switch paths freeze the queue, cancel blk-mq work, and serialize via `elevator_lock`.
- Sysfs attribute access is blocked once `ELEVATOR_FLAG_DYING` is set.
- Old scheduler resources are released only after unregistering sysfs/debugfs and freeing blk-mq scheduler resources.
- Module lookup/loading is intentionally done before freezing to avoid self-deadlock when the target module resides on the same queue.

Research relevance:
- This is the central policy plug-in layer for Linux block scheduling.
- It links generic request merging with concrete schedulers such as `mq-deadline` and `kyber`.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/elevator.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/elevator.h -->
# File Research: sources/os/linux/linux/block/elevator.h

Defines the public internal interface between the block elevator core and blk-mq I/O scheduler implementations.

Key declarations:
- `enum elv_merge` defines no/front/back/discard merge outcomes.
- `struct elevator_tags` and `struct elevator_resources` carry allocated scheduler tag state and private scheduler data.
- `struct elv_change_ctx` carries state through scheduler changes, including old/new queues and allocated resources.
- `struct elevator_mq_ops` is the scheduler callback table for init/exit, hctx setup, merge, insertion, dispatch, completion, depth limiting, and ICQ lifecycle hooks.
- `struct elevator_type` describes a scheduler implementation, its sysfs/debugfs attributes, module owner, alias, and optional ICQ cache.
- `struct elevator_queue` is the per-request-queue scheduler instance, with private data, kobject, sysfs lock, flags, and merge hash.

Notable constants:
- `ELV_NAME_MAX` limits scheduler names.
- `ELV_HASH_BITS` sizes the merge hash.
- `ELEVATOR_INSERT_*` defines scheduler insertion modes used by blk-mq paths.
- `ELEVATOR_FLAG_REGISTERED` and `ELEVATOR_FLAG_DYING` gate exported lifecycle state.

Research relevance:
- This header is the contract used by `elevator.c`, `mq-deadline.c`, `kyber-iosched.c`, and blk-mq scheduler glue.
- The callback table shows which scheduler operations are mandatory versus optional.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/elevator.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/fops.c -->
# File Research: sources/os/linux/linux/block/fops.c

Implements the default file operations for block special files, including open/release, direct and buffered read/write, mmap preparation, fsync, fallocate, and io_uring command entry.

Key responsibilities:
- Converts file flags to `blk_mode_t` with `file_to_blk_mode()`.
- Opens block devices through `bdev_permission()`, `blkdev_get_no_open()`, and `bdev_open()`.
- Implements direct I/O using bios, including simple inline-bvec, async single-bio, and multi-bio paths.
- Handles buffered I/O through iomap or buffer-head based address-space operations depending on `CONFIG_BUFFER_HEAD`.
- Enforces block-size alignment for direct I/O.
- Truncates reads/writes at device size and rejects writes past end.
- Blocks writes to read-only devices and active swap devices except hibernate resume devices.
- Implements fallocate zero/punch/write-zeroes over block-device ranges.

Important functions:
- `blkdev_direct_IO()`, `__blkdev_direct_IO_simple()`, `__blkdev_direct_IO_async()`, `__blkdev_direct_IO()` build and submit bio-based direct I/O.
- `blkdev_read_iter()` and `blkdev_write_iter()` are the main file data paths.
- `blkdev_fsync()` flushes the block device and treats unsupported flush as success.
- `blkdev_fallocate()` validates flags/ranges and issues zeroout/write-zeroes.
- `def_blk_fops` exports the default block-device `file_operations`.
- `def_blk_aops` exports the block-device address-space operations.
- `blkdev_init()` initializes the direct-I/O bioset.

Concurrency/lifetime notes:
- Buffered I/O takes `inode_lock_shared()` to avoid races with block size changes and page-cache invalidation.
- Direct write invalidates cached pages before and after I/O.
- Async direct I/O stores private state in bioset-backed `struct blkdev_dio` and completes via kiocb callbacks.
- Polling direct I/O stores the bio in `iocb->private`.

Research relevance:
- This is the user-visible block special file data path, tying VFS I/O to bio submission.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/fops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/genhd.c -->
# File Research: sources/os/linux/linux/block/genhd.c

Implements gendisk registration, device lifetime, major/minor allocation, disk/partition sysfs and proc exports, disk sequence numbers, and disk teardown.

Key responsibilities:
- Maintains block major registrations and optional legacy autoload probes.
- Allocates extended minors with an IDA.
- Registers disks as block-class devices, sets sysfs attributes, creates `holders`/`slaves` directories, registers queues and backing devices, and scans partitions.
- Removes disks, marks them dead, drops partitions, drains queues, unregisters queues/BDI, and releases resources.
- Exposes `/proc/partitions`, `/proc/diskstats`, and sysfs attributes such as `size`, `stat`, `inflight`, `diskseq`, `partscan`, `badblocks`, and read-only state.
- Allocates and releases `struct gendisk` and its `part0` block device.

Important functions:
- `set_capacity()` and `set_capacity_and_notify()` update disk capacity and send resize uevents.
- `__register_blkdev()` / `unregister_blkdev()` manage block major names.
- `disk_scan_partitions()` triggers partition rescans with exclusive-claim coordination.
- `add_disk_fwnode()` / `device_add_disk()` register disks.
- `del_gendisk()` and `__del_gendisk()` remove disks and coordinate queue draining.
- `__alloc_disk_node()` and `__blk_alloc_disk()` allocate gendisks and queues.
- `put_disk()` drops the final disk reference.
- `set_disk_ro()` changes disk read-only state and emits uevents.

Concurrency/lifetime notes:
- Disk add/remove around blk-mq uses `tag_set->update_nr_hwq_lock` and `memalloc_noio`.
- Deletion disables elevator switching before queue teardown.
- Disk death sets `GD_DEAD`, may set `QUEUE_FLAG_DYING`, sets capacity to zero, starts queue drain, and notifies block devices.
- `diskseq` is monotonic and helps userspace distinguish reused block names.

Research relevance:
- This file is the central Linux block-device object model and lifecycle implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/genhd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/holder.c -->
# File Research: sources/os/linux/linux/block/holder.c

Implements deprecated holder/slave sysfs link helpers between a claimed slave block device and a holding disk.

Key responsibilities:
- Tracks holder links in `struct bd_holder_disk`, keyed by the slave block device holder directory.
- Creates reciprocal sysfs links:
  - holder disk `slaves/<slave>`
  - slave bdev `holders/<holder>`
- Reference-counts duplicate links between the same slave and holder.
- Keeps an extra reference on `bd_holder_dir` so links can be cleaned up after disk deletion starts.

Important functions:
- `bd_link_disk_holder()` validates inputs, keeps holder directory lifetime, creates sysfs links, and records/refcounts the link.
- `bd_unlink_disk_holder()` decrements the refcount and removes links when it reaches zero.

Concurrency/lifetime notes:
- `blk_holder_mutex` serializes holder-list changes.
- The slave disk `open_mutex` is used to verify the slave disk is still live while acquiring the holder directory reference.
- Self-links are rejected.

Research relevance:
- This is a small compatibility bridge for block stacking visibility, used by existing holder users such as device-mapper style relationships.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/holder.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/ioctl.c -->
# File Research: sources/os/linux/linux/block/ioctl.c

Implements generic block-device ioctls, compat ioctl handling, persistent reservation ioctls, partition add/delete/resize ioctls, discard/secure erase/zeroout, and a block io_uring command for discard.

Key responsibilities:
- Validates user ranges, alignment, permissions, and device capabilities.
- Handles partition table manipulation through `BLKPG`.
- Implements discard, secure discard, and zeroout after invalidating relevant page-cache ranges.
- Provides common geometry, size, block-size, read-only, readahead, zone, crypto, trace, and persistent reservation ioctls.
- Falls back to driver-specific `fops->ioctl` / `compat_ioctl` when generic handling returns `-ENOIOCTLCMD`.
- Implements `BLOCK_URING_CMD_DISCARD`.

Important functions:
- `blkpg_do_ioctl()` validates and dispatches add/delete/resize partition operations.
- `blk_validate_byte_range()` centralizes byte-range validation.
- `blk_ioctl_discard()`, `blk_ioctl_secure_erase()`, `blk_ioctl_zeroout()` implement destructive range operations.
- `blkdev_common_ioctl()` handles generic native/compat-compatible commands.
- `blkdev_ioctl()` and `compat_blkdev_ioctl()` handle ABI-specific commands.
- `blkdev_pr_*()` wrappers implement persistent reservation operations.
- `blkdev_bszset()` changes soft block size, using exclusive open if needed.
- `blkdev_uring_cmd()` supports async discard via io_uring command.

Concurrency/lifetime notes:
- Destructive range operations take inode and invalidate locks before truncating cache and issuing device operations.
- Persistent reservation operations are denied on partitions and gate unprivileged access by open mode.
- Nonblocking io_uring discard rejects multi-bio cases with `-EAGAIN` to avoid hidden partial errors.

Research relevance:
- This file defines much of the userspace administrative ABI for block devices.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/ioprio.c -->
# File Research: sources/os/linux/linux/block/ioprio.c

Implements the `ioprio_set` and `ioprio_get` syscalls for per-task I/O priority.

Key responsibilities:
- Validates I/O priority class and level.
- Requires `CAP_SYS_ADMIN` or `CAP_SYS_NICE` for realtime I/O priority.
- Supports process, process group, and user selection modes.
- Returns raw priority for single-process lookup to preserve historical behavior.
- Returns the best priority across process-group or user queries.

Important functions:
- `ioprio_check_cap()` validates class/level and privilege.
- `SYSCALL_DEFINE3(ioprio_set)` applies priority to selected tasks.
- `get_task_ioprio()` enforces LSM checks and returns effective task priority.
- `get_task_raw_ioprio()` returns explicitly stored task I/O priority or default.
- `SYSCALL_DEFINE2(ioprio_get)` queries selected tasks.

Concurrency/lifetime notes:
- Uses RCU while locating tasks/users/process groups.
- Uses `tasklist_lock` for process-group iteration.
- Uses `task_lock()` around task I/O context access.
- Calls `security_task_getioprio()` for LSM mediation.

Research relevance:
- This provides the userspace policy input consumed by schedulers such as `mq-deadline`.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/ioprio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/kyber-iosched.c -->
# File Research: sources/os/linux/linux/block/kyber-iosched.c

Implements the Kyber blk-mq I/O scheduler, a latency-control scheduler that throttles per-domain queue depth using scalable bitmaps and latency feedback.

Key responsibilities:
- Classifies requests into read, write, discard, and other scheduling domains.
- Limits each domain with `sbitmap_queue` tokens.
- Maintains per-CPU latency histograms for total and device I/O latency.
- Periodically calculates p90/p99 latency buckets and resizes domain token depths.
- Uses per-hctx/per-context queues to preserve merge opportunities and scalable insertion.
- Dispatches requests in domain batches while respecting token availability.

Important structures:
- `struct kyber_queue_data` stores queue-wide tokens, latency targets, per-CPU latency, and timer state.
- `struct kyber_hctx_data` stores per-hctx request queues, current domain, batching, context maps, and wait entries.
- `struct kyber_ctx_queue` stores per-context domain request lists under a spinlock.

Important functions:
- `kyber_timer_fn()` aggregates latency samples and adjusts depths.
- `kyber_init_sched()` / `kyber_exit_sched()` enable/disable accounting and scheduler state.
- `kyber_init_hctx()` / `kyber_exit_hctx()` manage per-hctx scheduler data.
- `kyber_insert_requests()` queues requests by domain/context.
- `kyber_dispatch_request()` rotates through domains and batches dispatch.
- `kyber_completed_request()` records latency samples and schedules adjustment.
- `kyber_get_domain_token()` integrates token acquisition with sbitmap wait queues.

Interfaces:
- Sysfs exposes read/write latency targets.
- Debugfs exposes token state, per-domain request lists, wait state, current domain, and batching.
- Registers as elevator `"kyber"`.

Research relevance:
- Kyber is a concrete example of blk-mq scheduling focused on latency feedback rather than purely positional ordering.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/kyber-iosched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/mq-deadline.c -->
# File Research: sources/os/linux/linux/block/mq-deadline.c

Implements the multi-queue deadline I/O scheduler, adapting classic deadline scheduling to blk-mq with I/O priority classes.

Key responsibilities:
- Maintains per-priority read/write RB trees ordered by sector and FIFO lists ordered by expiration.
- Supports realtime, best-effort, and idle I/O priority classes.
- Prefers reads but limits write starvation through `writes_starved`.
- Batches sequential requests with `fifo_batch`.
- Ages lower-priority requests through `prio_aging_expire`.
- Supports front/back merge through elevator hash and RB-tree lookup.

Important structures:
- `struct deadline_data` stores global scheduler state, dispatch list, tunables, and lock.
- `struct dd_per_prio` stores per-priority sort lists, FIFO lists, latest positions, and stats.
- `struct io_stats_per_prio` tracks inserted, merged, dispatched, and completed counts.

Important functions:
- `dd_dispatch_request()` selects the next request across dispatch list, aged lower-priority work, and priority order.
- `__dd_dispatch_request()` implements core deadline read/write selection.
- `dd_insert_requests()` / `dd_insert_request()` place requests into FIFO/RB/hash state.
- `dd_request_merge()`, `dd_bio_merge()`, `dd_merged_requests()` implement scheduler merging.
- `dd_finish_request()` updates completion stats.
- `dd_init_sched()` / `dd_exit_sched()` allocate and validate scheduler state.

Interfaces:
- Sysfs exposes `read_expire`, `write_expire`, `writes_starved`, `front_merges`, `fifo_batch`, and `prio_aging_expire`.
- Debugfs exposes priority/direction FIFO lists, next request, dispatch list, queued counts, and owned-by-driver counts.
- Registers as `"mq-deadline"` with alias `"deadline"`.

Research relevance:
- This is the default elevator selected by `elevator_set_default()` for single-queue/shared-tag devices.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/mq-deadline.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/opal_proto.h -->
# File Research: sources/os/linux/linux/block/opal_proto.h

Defines constants, enums, packet headers, and discovery feature layouts for TCG OPAL self-encrypting drive protocol support.

Key contents:
- Security protocol identifiers for TCG `SECP`.
- OPAL atom/token encodings and masks for tiny/short/medium/long atoms.
- OPAL UID and method enum indexes used by OPAL command construction.
- OPAL token constants for tables, locking ranges, MBR control, properties, and session/list delimiters.
- Locking-state, parameter, and revert constants.
- Packet structures for com packets, packets, data subpackets, response headers, and stack reset.
- Discovery 0 feature codes and structures for TPer, locking, geometry, enterprise SSC, datastore, single-user, OPAL v1, and OPAL v2 features.

Important structures:
- `struct opal_header` nests OPAL com packet, packet, and data subpacket headers.
- `struct d0_features` is the variable-length discovery descriptor wrapper.
- Feature structs use big-endian fields matching the wire format.

Research relevance:
- This header is protocol schema, not behavior.
- It supports block-layer OPAL management code elsewhere by providing wire-compatible layouts and symbolic constants.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/opal_proto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/Kconfig -->
# File Research: sources/os/linux/linux/block/partitions/Kconfig

Defines kernel configuration options for partition table parsers.

Key responsibilities:
- Groups options under `menu "Partition Types"`.
- Provides `PARTITION_ADVANCED` to reveal less common/foreign partition formats.
- Enables architecture-default partition formats, such as Acorn on `ARCH_ACORN`, Amiga on `AMIGA`, Atari on `ATARI`, Mac on Mac/PPC, SGI, Sun, Ultrix, and SYSV68.
- Keeps common `MSDOS_PARTITION` and `EFI_PARTITION` default-enabled.
- Adds dependencies for subformats such as BSD/Minix/Solaris/Unixware under MSDOS partition support.
- Includes command-line and device-tree fixed partition support.

Notable options in this group:
- Acorn subformats: Cumana, EESOX, ICS, ADFS, PowerTec, RISCiX.
- AIX, OSF, Amiga, Atari, IBM DASD, Mac, MSDOS, BSD, Minix, Solaris x86, Unixware, LDM, SGI, Ultrix, Sun, Karma, EFI/GPT, SYSV68, CMDLINE, and OF partitioning.

Research relevance:
- This file controls which parser objects from `block/partitions` are compiled.
- It documents expected platform associations and user-facing intent for each parser.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/Makefile -->
# File Research: sources/os/linux/linux/block/partitions/Makefile

Builds the block partition parser objects according to Kconfig selections.

Key contents:
- Always builds `core.o` when `CONFIG_BLOCK` is enabled.
- Conditionally builds parser objects for Acorn, Amiga, Atari, AIX, cmdline, Mac, LDM, MSDOS, OF, OSF, SGI, Sun, Ultrix, IBM, EFI, Karma, and SYSV68 partition formats.

Research relevance:
- This is the compile-time binding between partition Kconfig symbols and parser source files.
- It confirms that the files in this group are individually optional parser modules within the built-in block partition subsystem.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/acorn.c -->
# File Research: sources/os/linux/linux/block/partitions/acorn.c

Implements multiple Acorn/RISC OS partition table parsers, each conditional on its Kconfig subformat.

Supported formats:
- Cumana/ADFS chained style.
- Native ADFS/FileCore.
- RISCiX subpartition table.
- Linux partitions embedded in Acorn partition regions.
- ICS partition table with checksum.
- PowerTec SCSI partition table with checksum.
- EESOX SCSI partition table with XOR-obfuscated table.

Important functions:
- `adfs_partition()` validates an ADFS boot block and emits a partition from its disc record.
- `riscix_partition()` parses RISCiX records and subpartitions.
- `linux_partition()` parses Acorn Linux native/swap records.
- `adfspart_check_CUMANA()`, `adfspart_check_ADFS()`, `adfspart_check_ICS()`, `adfspart_check_POWERTEC()`, `adfspart_check_EESOX()` are the exported parser entry points declared in `check.h`.

Format notes:
- Several parsers read fixed sectors such as sector 6, sector 0, or sector 7.
- ICS uses a checksum seeded with `0x50617274`.
- PowerTec rejects PC/BIOS MBR-looking sectors before checksum validation.
- EESOX derives partition sizes from adjacent start addresses because the table lacks explicit sizes.
- RISCiX and Linux parsing may emit nested partition entries.

Research relevance:
- This file shows the partition layer’s legacy format support pattern: format probe, diagnostic text in `pp_buf`, and calls to `put_partition()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/acorn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/aix.c -->
# File Research: sources/os/linux/linux/block/partitions/aix.c

Implements basic AIX LVM partition discovery for contiguous logical volumes.

Key responsibilities:
- Reads an AIX LVM record from sector 7.
- Supports LVM header version 1.
- Locates VGDA metadata, logical volume descriptors, logical volume names, and physical volume descriptors.
- Reconstructs logical volumes only when their physical partitions are contiguous.
- Emits each contiguous logical volume as a Linux partition.

Important structures:
- `struct lvm_rec` describes the sector-7 LVM record.
- `struct vgda` describes volume group metadata.
- `struct lvd` describes logical volume descriptors.
- `struct lvname` stores names.
- `struct pvd` contains physical partition entries.
- Local `struct lv_info` tracks expected/found physical partitions and contiguity.

Important functions:
- `read_lba()` reads arbitrary byte counts by repeatedly reading 512-byte sectors.
- `alloc_pvd()` and `alloc_lvn()` allocate and load metadata blocks.
- `aix_partition()` is the parser entry point.

Limitations:
- Non-contiguous logical volumes are not emitted and produce warnings.
- Unsupported LVM versions are reported but not parsed.
- The parser is for simple contiguous cases, not full AIX LVM mapping.

Research relevance:
- This is a partition parser that translates an LVM-like foreign metadata layout into plain block partitions when safe.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/aix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/amiga.c -->
# File Research: sources/os/linux/linux/block/partitions/amiga.c

Implements Amiga Rigid Disk Block partition table parsing.

Key responsibilities:
- Scans early disk blocks up to `RDB_ALLOCATION_LIMIT` for an `IDNAME_RIGIDDISK` block.
- Validates RDB checksums, with a compatibility retry for Windows-damaged bytes.
- Follows the RDB partition list and validates each `PartitionBlock`.
- Converts Amiga block/cylinder geometry into 512-byte Linux sectors.
- Performs overflow checks before calculating start and size.
- Emits up to 16 partition entries.

Important functions:
- `checksum_block()` computes the big-endian summed-long checksum.
- `amiga_partition()` is the parser entry point.

Safety details:
- Uses `check_mul_overflow()` and `check_add_overflow()` for multi-field geometry math.
- Warns when a partition exceeds 32-bit AmigaDOS limits.
- Skips invalid partition blocks or partitions with zero size.
- Emits DOS type and environment info into parser output for mounting diagnostics.

Research relevance:
- This file is a robust legacy parser example with explicit overflow hardening around old-disk geometry fields.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/amiga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/atari.c -->
# File Research: sources/os/linux/linux/block/partitions/atari.c

Implements Atari AHDI and ICD/Supra partition table parsing.

Key responsibilities:
- Rejects devices whose logical block size is not 512 bytes.
- Reads the root sector and validates at least one primary partition entry.
- Emits primary AHDI partitions.
- Follows `XGM` extended partition chains.
- Optionally parses ICD/Supra extra partitions from the root sector.

Important logic:
- `VALID_PARTITION()` checks active flag, alphanumeric ID, and bounds within disk size.
- `OK_id()` accepts `GEM`, `BGM`, `LNX`, `SWP`, and `RAW` IDs for ICD partitions.
- Extended `XGM` parsing reads linked root sectors and emits subpartitions relative to the extended base.

Safety/limitations:
- No strong magic exists for Atari root sectors, so validation is heuristic.
- Extended partition parsing stops on invalid flags, wrong IDs, read failures, or partition limit.
- ICD parsing is attempted only when no AHDI extended partition was seen.

Research relevance:
- This parser illustrates heuristic legacy partition detection and linked extended-partition traversal.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/atari.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/atari.h -->
# File Research: sources/os/linux/linux/block/partitions/atari.h

Defines Atari root sector and partition entry wire layouts.

Key structures:
- `struct partition_info` contains flag byte, 3-byte partition ID, big-endian start sector, and big-endian size.
- `struct rootsector` contains boot-code padding, 8 ICD partition entries, disk size, 4 primary partition entries, bad-sector-list metadata, and checksum.

Research relevance:
- This header provides packed on-disk structures consumed by `atari.c`.
- The layout reflects both primary AHDI entries and ICD/Supra extended entries.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/atari.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/check.h -->
# File Research: sources/os/linux/linux/block/partitions/check.h

Defines the shared interface for block partition parsers.

Key contents:
- `struct parsed_partitions` stores the target disk, partition name prefix, output partition array, limit, beyond-EOD flag, and sequence buffer for diagnostic output.
- `Sector` wraps a folio reference returned by `read_part_sector()`.
- `read_part_sector()` reads one sector for parser use.
- `put_dev_sector()` drops the folio reference.
- `put_partition()` records a partition start/size and appends its name to parser output.
- Declares parser entry points for all supported partition formats.

Research relevance:
- This header is the minimal parser ABI: parsers read sectors, call `put_partition()`, and return probe status.
- It also centralizes parser result storage and diagnostic string construction.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/check.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/cmdline.c -->
# File Research: sources/os/linux/linux/block/partitions/cmdline.c

Implements partition definitions supplied through the kernel command line via `blkdevparts=`.

Key responsibilities:
- Parses mtdparts-like definitions into block-device-specific partition lists.
- Supports explicit sizes, remainder size with `-`, optional start offsets with `@`, optional names in parentheses, and flags.
- Applies matching definitions by disk name.
- Emits partition metadata including volume name and read-only flag.
- Warns when command-line partitions overlap.

Important structures:
- `struct cmdline_subpart` stores name, byte offset, byte size, flags, and linked-list pointer.
- `struct cmdline_parts` stores a disk name and linked subpartition list.

Important functions:
- `parse_subpart()` parses one partition definition.
- `parse_parts()` parses one block-device definition.
- `cmdline_parts_parse()` parses the full semicolon-separated command line.
- `cmdline_parts_set()` maps byte ranges to sector-based partition entries.
- `cmdline_parts_verifier()` detects overlaps.
- `cmdline_partition()` is the parser entry point.
- `cmdline_parts_setup()` registers the `blkdevparts=` boot parameter.

Flags:
- `ro` maps to `ADDPART_FLAG_READONLY`.
- `lk` is parsed as `PF_POWERUP_LOCK` but not otherwise applied in this file.

Research relevance:
- This is the block partition path for fixed-layout embedded systems without on-disk partition tables.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/cmdline.c -->