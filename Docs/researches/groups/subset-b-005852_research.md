# subset-b-005852 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/devm-helpers.h -->
# sources/distributed-fs/ceph-client/include/linux/devm-helpers.h

## Purpose
Provides tiny device-managed helpers for workqueue objects that should be cancelled automatically when a driver detaches. It exists to reduce bugs caused by mixing manual work cancellation with devm-managed resources such as IRQs.

## Important APIs, Types, And Functions
The file defines `devm_delayed_work_autocancel()` and `devm_work_autocancel()`. Both initialize caller-owned work storage with `INIT_DELAYED_WORK()` or `INIT_WORK()` and register a devres action through `devm_add_action()`. The cleanup callbacks are `devm_delayed_work_drop()` and `devm_work_drop()`, which call `cancel_delayed_work_sync()` and `cancel_work_sync()`.

## Control Flow
Drivers call the helper during probe after allocating a `struct delayed_work` or `struct work_struct`. On device release, devres invokes the registered cancellation callback after normal remove processing. Cancellation synchronously drains any running callback and prevents later queued execution.

## State And Persistence
State is the initialized work item and the devres action attached to the `struct device`. There is no durable persistence. The important lifetime rule is that the work object must remain valid until devres cleanup runs.

## Dependencies And Integration Points
Depends on `linux/device.h`, `linux/workqueue.h`, and the device resource manager. It integrates with drivers that already use devm-managed IRQs, memory, clocks, or other resources and want work cancellation to share the same lifetime.

## Risks And Edge Cases
The header warns that devm cleanup may happen after `remove()` returns. If `remove()` manually frees data used by a devm-cancelled work item before devres runs, an IRQ or other source can still queue work against freed state. Callers must ensure work storage and callback dependencies outlive the devres action or explicitly order cleanup.

## Test Signals
Compile coverage is enough for the inline helpers. Runtime tests should exercise probe failure unwind, driver remove with queued work, running work during detach, and combinations with devm-managed IRQs that can schedule the work until IRQ teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/devm-helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/devpts_fs.h -->
# sources/distributed-fs/ceph-client/include/linux/devpts_fs.h

## Purpose
Declares the internal devpts interface used by the Unix98 pty implementation to allocate, publish, and remove pseudo-terminal slave nodes in the devpts filesystem.

## Important APIs, Types, And Functions
With `CONFIG_UNIX98_PTYS`, the header exposes `struct pts_fs_info`, `devpts_mntget()`, `devpts_acquire()`, `devpts_release()`, `devpts_new_index()`, `devpts_kill_index()`, `devpts_pty_new()`, `devpts_get_priv()`, `devpts_pty_kill()`, and `ptm_open_peer()`. Without Unix98 ptys, `ptm_open_peer()` is an inline stub returning `-EIO`.

## Control Flow
PTY master open paths acquire a devpts instance, reserve an index, create the slave dentry with private tty data, and later unlink and release the index when the tty is torn down. `ptm_open_peer()` lets the master side open the peer slave with supplied file flags.

## State And Persistence
State lives in the devpts mount, `pts_fs_info`, allocated pty indices, dentries, and private data attached to devpts nodes. It is filesystem/runtime state, not durable storage.

## Dependencies And Integration Points
Depends on VFS types such as `struct file`, `struct vfsmount`, and `struct dentry`, and on tty internals. It is used by `drivers/tty/pty.c` and devpts filesystem code.

## Risks And Edge Cases
Incorrect acquire/release or index kill ordering can leak pty numbers or leave stale dentries. Namespace and mount-instance handling are sensitive because devpts instances can be per-namespace. The `CONFIG_UNIX98_PTYS=n` stub must keep callers from assuming peer open support.

## Test Signals
PTY tests should cover `/dev/ptmx` open, peer open, close/unlink, multiple devpts mounts, namespace isolation, index reuse, and disabled Unix98 pty builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/devpts_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dfl.h -->
# sources/distributed-fs/ceph-client/include/linux/dfl.h

## Purpose
Defines the public driver-model API for Intel FPGA Device Feature List devices on the DFL bus.

## Important APIs, Types, And Functions
The main types are `enum dfl_id_type`, `struct dfl_device`, and `struct dfl_driver`. `struct dfl_device` carries bus device state, FIU type, feature id, revision, MMIO resource, IRQ list, container device, matched id entry, DFH version, and copied parameter block. Driver helpers include `to_dfl_dev()`, `to_dfl_drv()`, `dfl_driver_register()`, `__dfl_driver_register()`, `dfl_driver_unregister()`, `module_dfl_driver()`, and `dfh_find_param()`.

## Control Flow
DFL bus enumeration creates `struct dfl_device` objects for discovered features. A `struct dfl_driver` supplies an id table plus `probe()` and optional `remove()` callbacks. `module_dfl_driver()` wires normal module init/exit to DFL registration and unregistration.

## State And Persistence
State is per-device kernel state: MMIO/IRQ resources, feature metadata, a pointer to the FPGA container, and feature parameter memory. The header defines no persistence; hardware feature state lives behind MMIO and the container driver.

## Dependencies And Integration Points
Depends on the Linux driver model, module ownership, `mod_devicetable.h`, resources, and DFL FPGA container code. It integrates accelerator feature drivers with FPGA FME and PORT feature units.

## Risks And Edge Cases
Drivers must match the correct FIU type and feature id. Misusing the copied `params` block or assuming a DFH version can break feature probing. IRQ array lifetime and MMIO resource bounds are provided by the bus and must be respected by child drivers.

## Test Signals
Build DFL drivers as modules and built-ins, verify modalias/id-table binding, probe/remove ordering, resource exposure, IRQ counts, `dfh_find_param()` lookup, and failed-probe unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dfl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dibs.h -->
# sources/distributed-fs/ceph-client/include/linux/dibs.h

## Purpose
Defines the Direct Internal Buffer Sharing abstraction, where clients exchange data through Direct Memory Buffers owned by local DIBS devices and writable by authorized remote DIBS devices on the same fabric.

## Important APIs, Types, And Functions
Core data structures are `struct dibs_dmb`, `struct dibs_event`, `struct dibs_client_ops`, `struct dibs_client`, `struct dibs_dev_ops`, and `struct dibs_dev`. Client entry points are `dibs_register_client()` and `dibs_unregister_client()`. Device-driver entry points are `dibs_dev_alloc()`, `dibs_dev_add()`, and `dibs_dev_del()`. Per-client device storage is accessed with `dibs_set_priv()` and `dibs_get_priv()`.

## Control Flow
DIBS clients register callbacks and are notified of existing and future devices via `add_dev()`. A client queries fabric reachability, registers a DMB for a remote GID, receives IRQ/event callbacks, and unregisters the DMB during teardown. Sending uses `move_data()` to write synchronously into a remote DMB and optionally signal a bit in the target mask. Optional flows support VLAN membership, software events, and memory-mapped remote DMB attach/detach.

## State And Persistence
Runtime state includes device GIDs, fabric ids, per-client subscriptions, DMB indices, DMB tokens, allocated CPU buffers, optional DMA addresses, and per-client private pointers. `struct dibs_dev` protects client/DMB arrays with a spinlock. There is no filesystem persistence; tokens and GIDs are stable only within the fabric lifetime described by the driver.

## Dependencies And Integration Points
Depends on `struct device`, UUIDs, DMA addresses, lists, spinlocks, and fabric-specific DIBS device drivers. Consumers integrate through the DIBS layer rather than calling hardware drivers directly.

## Risks And Edge Cases
The contract depends on strong access control by the fabric: each DMB has one owner and one authorized remote writer. IRQ callbacks run in IRQ context, so clients must not sleep. `add_dev()`/`del_dev()` ordering controls device usability, and clients must stop using a device after `del_dev()`. Optional mmap-style DMB support requires all three related ops to be present or absent. Deprecated VLAN fields must not be treated as security-critical on devices that ignore VLANs.

## Test Signals
Tests should cover client register/unregister with preexisting devices, device add/delete notifications, DMB register/unregister, token uniqueness, loopback fabric behavior, move-data bounds and zero-length writes, IRQ/event coalescing, per-client private storage, optional attach/detach support, and concurrent device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dibs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/digsig.h -->
# sources/distributed-fs/ceph-client/include/linux/digsig.h

## Purpose
Declares compact public-key and signature header formats plus the kernel digital signature verification entry point.

## Important APIs, Types, And Functions
Defines `enum pubkey_algo`, `enum digest_algo`, packed `struct pubkey_hdr`, packed `struct signature_hdr`, and `digsig_verify()`. The only public algorithms in this header are RSA, SHA1, and SHA256. If signature support is not built, `digsig_verify()` returns `-EOPNOTSUPP`.

## Control Flow
Callers provide a keyring, signature blob, digest pointer, and digest length. The implementation validates the signature header, locates a matching key, and checks that the signature covers the supplied digest. The stub path fails immediately.

## State And Persistence
The header defines serialized blob layouts but owns no mutable state. Key persistence is handled by the kernel keyring subsystem.

## Dependencies And Integration Points
Depends on `linux/key.h`, packed binary formats, and the asymmetric-key/signature code selected by `CONFIG_SIGNATURE`.

## Risks And Edge Cases
The packed flexible-array formats are length-sensitive; callers must validate `siglen`, `digestlen`, algorithm fields, MPI counts, and key IDs. SHA1 support may be legacy-sensitive. Stub behavior must be handled by consumers that can build without signature verification.

## Test Signals
Validation should include supported and unsupported algorithms, malformed short headers, bad MPI counts, keyring misses, correct and incorrect digests, module and built-in signature configurations, and the `CONFIG_SIGNATURE=n` stub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/digsig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dim.h -->
# sources/distributed-fs/ceph-client/include/linux/dim.h

## Purpose
Defines Dynamic Interrupt Moderation data structures and APIs for network and RDMA drivers to adapt completion interrupt coalescing based on measured traffic.

## Important APIs, Types, And Functions
Important types include `struct dim_cq_moder`, `struct dim_irq_moder`, `struct dim_sample`, `struct dim_stats`, and `struct dim`. State enums describe CQ period mode, algorithm state, tune state, stats verdict, and step result. Network APIs include `net_dim_init_irq_moder()`, `net_dim_free_irq_moder()`, `net_dim_setting()`, `net_dim_work_cancel()`, moderation profile getters/setters, and `net_dim()`. RDMA uses `rdma_dim()`. Helpers include `dim_update_sample()`, `dim_update_sample_with_comps()`, `dim_calc_stats()`, `dim_turn()`, and parking helpers.

## Control Flow
Consumers periodically capture packet, byte, event, and completion counters into `dim_sample`. `net_dim()` or `rdma_dim()` waits for enough events, computes deltas with wraparound handling, compares current stats with previous stats, and transitions the tuning state. When a new profile is needed, it schedules the embedded work item so the driver can apply new CQ moderation outside the fast path.

## State And Persistence
Each `struct dim` stores the algorithm state, previous stats, start/measuring samples, profile index, CQ mode, step direction, and parking counters. Network devices may hold RCU-protected RX/TX profile arrays in `struct dim_irq_moder`. There is no persistence beyond live driver state.

## Dependencies And Integration Points
Depends on workqueues, RCU, `ktime_get()`, kernel bit helpers, and net/RDMA driver CQ moderation controls. It integrates with ethtool coalesce support through profile and coalesce capability flags.

## Risks And Edge Cases
Counter wraparound and small time deltas can produce unreliable stats. The worker must be cancelled during teardown. Profile index bounds are fixed by network and RDMA profile counts. RCU profile replacement must not expose freed moderation tables. Applying moderation in the wrong context can race with device reset or queue teardown.

## Test Signals
Tests should simulate increasing/decreasing traffic, counter wraparound, unchanged traffic parking, event-count gating, RX and TX profile selection, RDMA completion-only sampling, RCU profile update/free, and teardown with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dio.h -->
# sources/distributed-fs/ceph-client/include/linux/dio.h

## Purpose
Declares the HP300 DIO/DIO-II bus model, device IDs, resource helpers, and driver registration API.

## Important APIs, Types, And Functions
Key types are `dio_id`, `struct dio_dev`, `struct dio_bus`, `struct dio_device_id`, and `struct dio_driver`. APIs include `dio_find()`, `dio_scodetophysaddr()`, `dio_create_sysfs_dev_files()`, `dio_register_driver()`, `dio_unregister_driver()`, `dio_get_drvdata()`, and `dio_set_drvdata()`. Macros encode select-code address ranges, register offsets, primary/secondary IDs, resource helpers, and memory-region request/release.

## Control Flow
The DIO core scans select codes, reads ID/IPL registers from mapped DIO address space, creates `dio_dev` objects, matches drivers by ID table or wildcard, and calls probe/remove through the driver model. Drivers claim the memory resource with `dio_request_device()` and release it on teardown.

## State And Persistence
State is per-bus and per-device kernel state: the single `dio_bus`, device lists, resource windows, select code, encoded ID, interrupt priority, name, and memory resource. No durable state is maintained.

## Dependencies And Integration Points
Depends on HP300 architecture definitions, 8-bit I/O accessors, resources, and the Linux driver model. It integrates legacy HP DIO serial, LAN, HP-IB, SCSI, framebuffer, VME, and miscellaneous board drivers.

## Risks And Edge Cases
DIO-II support is only partially described; comments note the address space is too large to map fully. Secondary IDs matter mainly for framebuffers and must be encoded consistently. Select-code holes, HP320 maximum select code, and resource lengths differ between DIO and DIO-II. Incorrect `in_8()` base handling can misidentify hardware.

## Test Signals
Build HP300 configurations, validate scan results for known ID tables, resource start/end/length calculations, secondary framebuffer IDs, driver probe/remove, sysfs files, and memory-region conflict handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dirent.h -->
# sources/distributed-fs/ceph-client/include/linux/dirent.h

## Purpose
Defines the kernel-visible layout of `struct linux_dirent64`, the 64-bit directory entry record used by getdents-style interfaces.

## Important APIs, Types, And Functions
The only type is `struct linux_dirent64` with inode number `d_ino`, offset `d_off`, record length `d_reclen`, type `d_type`, and flexible array filename `d_name[]`.

## Control Flow
The header has no executable control flow. VFS directory iteration code fills records into userspace buffers using this layout.

## State And Persistence
The structure describes transient syscall output. Directory persistence is owned by the filesystem, not this header.

## Dependencies And Integration Points
Depends on fixed-width kernel integer types and integrates with Linux directory syscalls, VFS filldir logic, and libc consumers that parse `linux_dirent64`.

## Risks And Edge Cases
Record length must account for variable name length and alignment. Copying more bytes than the user buffer allows or reporting wrong `d_off` can break directory iteration. `d_type` may be unknown depending on filesystem support.

## Test Signals
Directory syscall tests should cover long names, alignment, buffer-boundary truncation, EOF continuation using `d_off`, and filesystems with and without native file-type reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dirent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dlm.h -->
# sources/distributed-fs/ceph-client/include/linux/dlm.h

## Purpose
Declares the in-kernel Distributed Lock Manager API for creating lockspaces and acquiring, converting, and releasing distributed locks.

## Important APIs, Types, And Functions
The header includes UAPI DLM definitions and adds `struct dlm_slot`, `struct dlm_lockspace_ops`, `dlm_new_lockspace()`, `dlm_release_lockspace()`, `dlm_lock()`, and `dlm_unlock()`. Release options include `DLM_RELEASE_NO_LOCKS`, `DLM_RELEASE_NORMAL`, `DLM_RELEASE_NO_EVENT`, and `DLM_RELEASE_RECOVER`. `DLM_LSFL_SOFTIRQ` selects softirq-safe AST/BAST callbacks.

## Control Flow
Users create or join a named lockspace, optionally receive recovery callbacks, submit asynchronous lock or conversion requests, and receive completion through AST callbacks with status in `struct dlm_lksb`. Blocking ASTs notify a holder that another request is blocked. Unlock requests are also asynchronous and complete through AST.

## State And Persistence
DLM state is cluster runtime state: lockspaces, membership slots, lock resources, lock IDs, LVB length, recovery generation, and local callbacks. Lock resources survive local function calls but not lockspace release or cluster teardown.

## Dependencies And Integration Points
Depends on UAPI DLM structures, cluster communication, and kernel users such as clustered filesystems. It integrates with callback context rules, cluster membership recovery, and lockspace generation tracking.

## Risks And Edge Cases
Callbacks may run in softirq or DLM request context, so callers must not block unexpectedly or call back into DLM while holding locks that callbacks need. Lock completion can fail asynchronously after `dlm_lock()` returns 0. All nodes must agree on lockspace flags and LVB length. Release options have cluster-visible consequences, especially no-event and recover release.

## Test Signals
Cluster tests should cover lockspace join mismatch, recovery callbacks, async success/failure ASTs, BAST delivery, conversions, parent locks, noqueue failure, unlock with outstanding sublocks, communication errors, and all lockspace release modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dlm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dlm_plock.h -->
# sources/distributed-fs/ceph-client/include/linux/dlm_plock.h

## Purpose
Declares the DLM POSIX lock bridge used to coordinate file-region locks across a distributed lockspace.

## Important APIs, Types, And Functions
The API consists of `dlm_posix_lock()`, `dlm_posix_unlock()`, `dlm_posix_cancel()`, and `dlm_posix_get()`. Each takes a `dlm_lockspace_t`, a numeric resource identifier, a `struct file`, and a `struct file_lock`, with `dlm_posix_lock()` also taking the POSIX lock command.

## Control Flow
Filesystem lock paths translate VFS file locks into DLM plock operations. Lock, unlock, cancel, and query calls communicate through the DLM plock subsystem and update or inspect the distributed POSIX lock state.

## State And Persistence
State is distributed lock state keyed by lockspace and resource number plus VFS file-lock metadata. No on-disk persistence is defined here.

## Dependencies And Integration Points
Depends on UAPI DLM plock definitions, `struct file`, `struct file_lock`, and clustered filesystem locking paths.

## Risks And Edge Cases
The resource number must map consistently to the filesystem object on all nodes. Cancellation and get operations must race correctly with blocked locks. File lifetime and lockspace lifetime must outlive the operation.

## Test Signals
Tests should cover shared/exclusive byte-range locks across nodes, unlock, cancel of blocking requests, `F_GETLK` semantics, lockspace failure, and concurrent process exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dlm_plock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-bufio.h -->
# sources/distributed-fs/ceph-client/include/linux/dm-bufio.h

## Purpose
Declares Device Mapper's block-buffer cache API for metadata-like I/O on block devices.

## Important APIs, Types, And Functions
Opaque types are `struct dm_bufio_client` and `struct dm_buffer`. APIs create/destroy/reset clients, set sector offsets, read/get/new buffers, prefetch, release, mark dirty fully or partially, asynchronously or synchronously write dirty buffers, issue flush/discard, forget buffers, set minimum buffers, and query block/client metadata. `DM_BUFIO_CLIENT_NO_SLEEP` controls allocation behavior.

## Control Flow
A DM target creates a client for a block device and block size, then obtains buffer references through `read`, `get`, or `new`. Modified buffers are marked dirty, released, and later written by explicit flush/write calls or memory pressure. Prefetch starts background reads without waiting. Destroy tears down the cache after references and I/O are gone.

## State And Persistence
State includes cached blocks, dirty ranges, reference counts, auxiliary per-buffer data, reserved buffer accounting, and the sector offset mapping logical buffer numbers to device sectors. Dirty data persists only after writeback and optional device flush.

## Dependencies And Integration Points
Depends on block devices, DM low-level I/O, sectors, and callback hooks for buffer allocation and write completion. It is used by DM metadata-heavy targets.

## Risks And Edge Cases
Deadlock constraints are explicit: only one thread may hold up to the reserved buffer count, other threads may hold at most one buffer unless using `dm_bufio_get()`. Dirty buffers can be written before the explicit write-dirty call under memory pressure. Sector offset must not change while I/O is active. Forget calls are hints and ignore busy or dirty buffers.

## Test Signals
Tests should cover cache hits/misses, read/new/get semantics, dirty full and partial writes, async writeback, flush/discard propagation, minimum-buffer cleanup, sector offset mapping, memory pressure, and misuse patterns that would exceed reserved-buffer rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-bufio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-dirty-log.h -->
# sources/distributed-fs/ceph-client/include/linux/dm-dirty-log.h

## Purpose
Defines the Device Mapper dirty region log interface used by mirror-like targets to track clean, dirty, in-sync, and resync-needed regions.

## Important APIs, Types, And Functions
Defines `region_t`, `struct dm_dirty_log`, and `struct dm_dirty_log_type`. Log implementations provide constructor/destructor, suspend/resume hooks, region-size query, `is_clean()`, `in_sync()`, `flush()`, mark/clear, resync work assignment, region sync updates, sync counts, status, and remote-recovery checks. Registry and factory APIs are `dm_dirty_log_type_register()`, `dm_dirty_log_type_unregister()`, `dm_dirty_log_create()`, and `dm_dirty_log_destroy()`.

## Control Flow
DM targets create a named log type during table construction, mark regions dirty during writes, flush log state when needed, query which regions are synchronized, assign resync work, mark resync completion, and destroy the log when the target is removed.

## State And Persistence
Dirty log state may be in memory, on disk, or clustered depending on the implementation. It tracks region dirtiness, sync state, recovering regions, and callback context. Persistent log implementations must commit state through `flush()`.

## Dependencies And Integration Points
Depends on Device Mapper target types, module registration, status reporting, and mirror recovery workers. Cluster logs integrate with remote recovery and may block.

## Risks And Edge Cases
`in_sync()` can return `-EWOULDBLOCK` when state is unknown without blocking, requiring daemon handling. Mark/clear may rarely block. `get_resync_work()` assigns work and must not be confused with `in_sync()`. Cluster recovery must avoid local writes racing with remote resync.

## Test Signals
Tests should cover log type registration conflicts, constructor failure, suspend/resume, dirty marking, persistent flush, resync work assignment, region sync count, status output, remote recovery detection, and blocking vs nonblocking `in_sync()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-dirty-log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-io.h -->
# sources/distributed-fs/ceph-client/include/linux/dm-io.h

## Purpose
Declares Device Mapper's low-level multi-region I/O helper for reading or writing one memory source to one or more block-device regions.

## Important APIs, Types, And Functions
Key types are `struct dm_io_region`, `struct page_list`, `enum dm_io_mem_type`, `struct dm_io_memory`, `struct dm_io_notify`, `struct dm_io_client`, and `struct dm_io_request`. APIs are `dm_io_client_create()`, `dm_io_client_destroy()`, and `dm_io()`. Memory can be represented as a page list, bio, VMA, or kernel memory.

## Control Flow
Callers create a client with private pools, fill a `dm_io_request` with operation flags, memory description, optional callback, and regions, then call `dm_io()`. If `notify.fn` is NULL the call is synchronous and can report per-region errors through `sync_error_bits`; otherwise completion is delivered asynchronously.

## State And Persistence
State is transient I/O request state and client memory pools. Persistent effects depend on the submitted block operation and target device.

## Dependencies And Integration Points
Depends on block operation flags, bios/pages, block devices, and DM targets needing low-level metadata or copy I/O.

## Risks And Edge Cases
Regions with zero count are ignored. The `sync_error_bits` mapping must match region ordering. Memory type, offset, and length must describe enough data for all regions. Callback context and client lifetime must outlive async I/O.

## Test Signals
Tests should cover sync and async reads/writes, multiple regions, ignored zero-length regions, all memory types, per-region error bits, ioprio propagation, and client teardown only after async completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-kcopyd.h -->
# sources/distributed-fs/ceph-client/include/linux/dm-kcopyd.h

## Purpose
Declares kcopyd, a Device Mapper service for copying or zeroing block-device regions synchronously with optional asynchronous completion.

## Important APIs, Types, And Functions
Defines `DM_KCOPYD_MAX_REGIONS`, `DM_KCOPYD_IGNORE_ERROR`, `DM_KCOPYD_WRITE_SEQ`, `struct dm_kcopyd_throttle`, `DECLARE_DM_KCOPYD_THROTTLE_WITH_MODULE_PARM()`, `struct dm_kcopyd_client`, `dm_kcopyd_client_create()`, `dm_kcopyd_client_destroy()`, `dm_kcopyd_client_flush()`, `dm_kcopyd_copy()`, `dm_kcopyd_prepare_callback()`, `dm_kcopyd_do_callback()`, and `dm_kcopyd_zero()`.

## Control Flow
Targets create a client, submit copy jobs from one source region to up to eight destination regions, and receive read/write error status through a callback. Zero jobs write zeroes to destination regions. Callback preparation can allocate in sleepable context and later complete from interrupt context through the kcopyd thread.

## State And Persistence
Runtime state includes job queues, client pools, optional shared throttle counters, and submitted block I/O. Persistent effects are copied or zeroed sectors after completion and flushes requested by higher layers.

## Dependencies And Integration Points
Builds on `dm-io`, block devices, module parameters for throttling, and DM targets such as snapshots, mirrors, and thin provisioning.

## Risks And Edge Cases
Destination count is bounded by `DM_KCOPYD_MAX_REGIONS`. `write_err` is a bitset indexed by destination. Throttle structs may be shared across clients and must be initialized. `dm_kcopyd_prepare_callback()` must not be called in interrupt context, while `dm_kcopyd_do_callback()` may be.

## Test Signals
Tests should cover single and multiple destination copies, read errors, per-destination write errors, ignore-error behavior, sequential write flag behavior, zeroing, throttling, client flush/destroy ordering, and interrupt-context callback submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-kcopyd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-region-hash.h -->
# sources/distributed-fs/ceph-client/include/linux/dm-region-hash.h

## Purpose
Declares Device Mapper's dirty-region hash interface, used to coordinate write tracking and resynchronization by region.

## Important APIs, Types, And Functions
Opaque types are `struct dm_region_hash` and `struct dm_region`. Region states are `DM_RH_CLEAN`, `DM_RH_DIRTY`, `DM_RH_NOSYNC`, and `DM_RH_RECOVERING`. APIs create/destroy hashes, access the dirty log, convert bios to regions and regions to sectors, inspect context/key/size, get/set/update state, flush, increment/decrement pending counts, delay bios, mark nosync, and control recovery lifecycle.

## Control Flow
The target creates a region hash with dispatch and wakeup callbacks, increments pending state for writes, delays conflicting bios, updates states after I/O completion, flushes the log, and runs recovery by preparing regions, starting a quiesced region, and ending recovery with success or error.

## State And Persistence
The hash tracks per-region dirty/nosync/recovering state, pending I/O counts, delayed bios, recovery-in-flight count, and a pointer to the dirty log. Persistent sync state is delegated to the dirty log.

## Dependencies And Integration Points
Depends on `dm-dirty-log`, bios, bio lists, and DM mirror-style recovery workers. Integration callbacks wake workers and dispatch delayed bios when regions quiesce.

## Risks And Edge Cases
State transitions must keep dirty-log state consistent. Nonzero `errors_handled` leaves regions `NOSYNC`. Delayed bios must be released exactly once. Recovery must quiesce regions before copying to avoid concurrent writes.

## Test Signals
Tests should cover bio-to-region mapping, pending inc/dec, dirty/nosync transitions, delayed bio dispatch, flush errors, recovery prepare/start/end, remote recovery interaction through the log, and error handling that preserves NOSYNC state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-region-hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-verity-loadpin.h -->
# sources/distributed-fs/ceph-client/include/linux/dm-verity-loadpin.h

## Purpose
Connects dm-verity root digests with LoadPin so the security subsystem can trust files loaded from verified block devices.

## Important APIs, Types, And Functions
Declares global `dm_verity_loadpin_trusted_root_digests`, `struct dm_verity_loadpin_trusted_root_digest`, and `dm_verity_loadpin_is_bdev_trusted()`. The digest struct has a list node, length, and counted flexible data array. Without `CONFIG_SECURITY_LOADPIN_VERITY`, the trust check returns false.

## Control Flow
dm-verity or security setup populates the trusted digest list. LoadPin asks whether a block device is trusted; the implementation checks the device's verity root digest against the trusted list.

## State And Persistence
State is the in-kernel list of trusted root digests. Trust is runtime security policy; the underlying verity metadata persists on block devices outside this header.

## Dependencies And Integration Points
Depends on lists, block devices, dm-verity, and LoadPin security configuration.

## Risks And Edge Cases
Digest length and list lifetime must be validated. The disabled-config stub must not accidentally grant trust. Race-free list updates and block-device identity checks are critical to avoid trusting the wrong device.

## Test Signals
Tests should cover trusted and untrusted root digests, malformed digest lengths, list update/removal, block-device teardown, and builds with LoadPin verity disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-verity-loadpin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm9000.h -->
# sources/distributed-fs/ceph-client/include/linux/dm9000.h

## Purpose
Defines platform data for the Davicom DM9000 Ethernet controller driver.

## Important APIs, Types, And Functions
Platform flags describe bus width and board quirks: `DM9000_PLATF_8BITONLY`, `16BITONLY`, `32BITONLY`, `EXT_PHY`, `NO_EEPROM`, and `SIMPLE_PHY`. `struct dm9000_plat_data` carries flags, optional Ethernet address, and optional replacement block I/O callbacks `inblk`, `outblk`, and `dumpblk`.

## Control Flow
Board code supplies `dm9000_plat_data` through platform-device data. The driver selects I/O width, PHY/EEPROM behavior, MAC address source, and block transfer functions during probe.

## State And Persistence
This is static platform configuration. MAC address persistence, if any, comes from platform firmware, EEPROM, or board code, not this header.

## Dependencies And Integration Points
Depends on Ethernet address sizing from `linux/if_ether.h` and integrates platform devices with the DM9000 net driver.

## Risks And Edge Cases
Conflicting width flags can misprogram I/O accesses. Missing EEPROM or external PHY flags must match board wiring. Custom block callbacks must honor MMIO ordering and byte counts.

## Test Signals
Board tests should verify probe with each bus width, no-EEPROM MAC fallback, external/simple PHY behavior, and custom block I/O transfers under RX/TX load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm9000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-buf-mapping.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-buf-mapping.h

## Purpose
Declares helper functions for converting physical-vector DMA-buf mappings into scatter-gather tables and freeing them.

## Important APIs, Types, And Functions
The APIs are `dma_buf_phys_vec_to_sgt()` and `dma_buf_free_sgt()`. Inputs include a `dma_buf_attachment`, optional peer-to-peer provider, an array of `struct phys_vec`, range count, total size, and DMA direction.

## Control Flow
Importers/exporters build an SG table from physical ranges for an attachment and direction, use it for DMA, then free it through the paired helper.

## State And Persistence
State is transient SG table mapping state associated with an attachment. No persistence is defined.

## Dependencies And Integration Points
Depends on `dma-buf.h`, DMA directions, physical-vector and PCI P2P concepts. It integrates DMA-buf sharing with peer-to-peer or physical-range backed exporters.

## Risks And Edge Cases
Range count, total size, and direction must match the buffer and DMA operation. Peer-to-peer ranges may not have normal pages, so importers must support that path. Free must pair with successful conversion to avoid mapping leaks.

## Test Signals
Tests should cover single/multiple ranges, P2P and non-P2P providers, invalid size/count, every valid DMA direction, and error cleanup after partial SG construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-buf-mapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-buf.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-buf.h

## Purpose
Defines the DMA-BUF sharing framework API for exporting buffers as file descriptors and attaching devices for cross-driver DMA and CPU access.

## Important APIs, Types, And Functions
Key types are `struct dma_buf_ops`, `struct dma_buf`, `struct dma_buf_attach_ops`, `struct dma_buf_attachment`, and `struct dma_buf_export_info`. Export/import APIs include `dma_buf_export()`, `dma_buf_fd()`, `dma_buf_get()`, `dma_buf_put()`, `dma_buf_attach()`, `dma_buf_dynamic_attach()`, `dma_buf_detach()`, pin/unpin, map/unmap attachment, invalidate mappings, CPU-access bracketing, mmap, vmap/vunmap, unlocked helpers, and iteration over exported buffers.

## Control Flow
An exporter fills `dma_buf_export_info` and provides mandatory ops such as `map_dma_buf`, `unmap_dma_buf`, and `release`. Userspace receives an fd. Importers get the buffer, attach a device, map an attachment for a DMA direction, perform access while obeying implicit synchronization fences in `dmabuf->resv`, then unmap, detach, and put references. Dynamic importers use invalidate callbacks and reservation locking rather than permanent pinning.

## State And Persistence
`struct dma_buf` stores invariant size, file reference, attachment list protected by the reservation lock, ops, vmap refcount/cache, exporter name, optional userspace name, owner module, global list node, private data, reservation object, poll wait queue, and fence callbacks. State is refcounted runtime sharing state; persistence is only via open file descriptors.

## Dependencies And Integration Points
Depends on files, scatterlists, DMA mapping, DMA fences, DMA reservation objects, wait queues, iosys maps, P2P DMA, mmap, and module ownership. It is central to DRM, V4L2, media, accelerator, and heap exporters.

## Risks And Edge Cases
Exporter and importer locking rules are strict. Dynamic mapping callbacks are called with `dma_resv` locked; non-dynamic importers pin storage. Exporters must guarantee backing storage availability and zeroing for non-dynamic paths. CPU access must be bracketed for cache coherency. Mmap exporters may need private address-space handling to zap PTEs. Attachment invalidation can race with device access unless importers add fences for non-revocable work.

## Test Signals
Tests should cover export/fd/get/put reference lifetime, attach failures, dynamic and static map/unmap, pin/unpin, fence-based implicit sync, CPU begin/end access, mmap size rejection, vmap refcounting, poll readiness, buffer naming, P2P attachments, and module unload/refcount behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-buf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-direct.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-direct.h

## Purpose
Declares internals of the direct DMA mapping implementation used by DMA core and IOMMU code.

## Important APIs, Types, And Functions
Defines `struct bus_dma_region`, `zone_dma_limit`, address translation helpers `translate_phys_to_dma()`, `translate_dma_to_phys()`, `dma_range_map_min()`, `dma_range_map_max()`, `phys_to_dma_unencrypted()`, `phys_to_dma()`, `dma_to_phys()`, `force_dma_unencrypted()`, `dma_capable()`, and direct allocation/support APIs such as `dma_direct_alloc()`, `dma_direct_free()`, page allocation/free, and `dma_direct_supported()`.

## Control Flow
Direct mapping converts CPU physical addresses to bus DMA addresses using an optional range map, memory encryption address transforms, and device masks. Allocation functions obtain CPU memory, produce a DMA handle, and free it through the paired direct path.

## State And Persistence
State is per-device DMA range maps, DMA masks, bus DMA limits, memory encryption mode, and global DMA zone limits. There is no durable persistence.

## Dependencies And Integration Points
Depends on DMA mapping core, DMA map ops internals, memblock low PFN, memory encryption helpers, SWIOTLB, and architecture overrides for `phys_to_dma`.

## Risks And Edge Cases
Missing range-map translation returns `DMA_MAPPING_ERROR` so `dma_capable()` fails. 32-bit DMA address limitations reject RAM below translated low memory. Encryption and unencrypted bounce buffers require correct address-bit handling. `addr + size - 1` needs valid nonzero sizes.

## Test Signals
Tests should cover devices with and without `dma_range_map`, mask and bus-limit boundaries, encrypted and unencrypted mappings, SWIOTLB fallback, 32-bit DMA address checks, allocation/free pairing, and required-mask computation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-direct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-direction.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-direction.h

## Purpose
Defines the standard DMA data direction enum and validation helper.

## Important APIs, Types, And Functions
`enum dma_data_direction` contains `DMA_BIDIRECTIONAL`, `DMA_TO_DEVICE`, `DMA_FROM_DEVICE`, and `DMA_NONE`. `valid_dma_direction()` accepts the first three and rejects `DMA_NONE`.

## Control Flow
DMA APIs use the enum to decide ownership transfer and cache-maintenance direction. `DMA_NONE` is a sentinel and should not reach actual map/sync operations.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by nearly every DMA mapping, DMA-BUF, and dmaengine interface that maps memory for device access.

## Risks And Edge Cases
Using the wrong direction can skip required cache invalidation or flush stale data. Passing `DMA_NONE` into map/unmap/sync paths should be rejected by callers or debug code.

## Test Signals
Build and DMA API debug coverage should flag invalid directions. Runtime tests should verify cache-coherency behavior for to-device, from-device, and bidirectional mappings on non-coherent platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-direction.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-fence-array.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-fence-array.h

## Purpose
Defines a DMA fence container that represents completion of an array of fences, either all fences or any fence depending on initialization.

## Important APIs, Types, And Functions
Types are `struct dma_fence_array_cb` and `struct dma_fence_array`. Helpers include `to_dma_fence_array()`, `dma_fence_array_for_each`, `dma_fence_array_alloc()`, `dma_fence_array_init()`, `dma_fence_array_create()`, `dma_fence_match_context()`, `dma_fence_array_first()`, and `dma_fence_array_next()`.

## Control Flow
Callers allocate/create an array fence with child fence pointers, a context, seqno, and `signal_on_any` policy. The array attaches callbacks to children and signals the base fence when the pending count reaches the selected condition. Iterators either walk children or treat a non-array head as a single fence.

## State And Persistence
State includes the base fence, spinlock, child count, atomic pending count, child fence array, IRQ work, and per-child callbacks. Lifetime is refcounted through the base fence and child references.

## Dependencies And Integration Points
Depends on `dma-fence.h` and IRQ work. Used by reservation objects, DRM schedulers, and sync-file style aggregation.

## Risks And Edge Cases
Child fence references and callback removal must be balanced. Empty arrays, already signaled children, and signal-on-any semantics need careful handling. Recursive container nesting is avoided by deeper unwrap helpers.

## Test Signals
Tests should cover all-children and any-child signal modes, already signaled children, mixed errors, context matching, iterator behavior for array and non-array fences, callback removal, and release cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-fence-array.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-fence-chain.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-fence-chain.h

## Purpose
Defines a DMA fence container that chains fences into a timeline while avoiding deep recursion.

## Important APIs, Types, And Functions
The main type is `struct dma_fence_chain`, which embeds a base fence, RCU previous pointer, previous seqno, contained fence, lock, and callback or IRQ work union. Helpers include `to_dma_fence_chain()`, `dma_fence_chain_contained()`, `dma_fence_chain_alloc()`, `dma_fence_chain_free()`, `dma_fence_chain_for_each`, `dma_fence_chain_walk()`, `dma_fence_chain_find_seqno()`, and `dma_fence_chain_init()`.

## Control Flow
A new chain node wraps a current fence and points to a previous chain/fence. Walkers hold references while traversing. Finding by seqno walks backward until it reaches the requested timeline point. Signaling uses callbacks or IRQ work to avoid lock inversion.

## State And Persistence
Runtime state is the chain node graph and referenced fences. `prev_seqno` preserves ordering when previous nodes are garbage-collected. There is no persistence.

## Dependencies And Integration Points
Depends on `dma-fence.h`, IRQ work, slab allocation, and RCU. Used by GPU and DMA reservation code to publish timeline dependencies compactly.

## Risks And Edge Cases
Reference handling in `dma_fence_chain_for_each` requires callers to drop references when breaking out. Initialized chains must be released through `dma_fence_put()`, while uninitialized allocations can use `dma_fence_chain_free()`. RCU previous pointers and sequence comparisons must handle garbage-collected nodes.

## Test Signals
Tests should cover chain initialization, walking, early loop break reference cleanup, find-by-seqno before/after garbage collection, contained-fence extraction, signaling order, and release paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-fence-chain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-fence-unwrap.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-fence-unwrap.h

## Purpose
Declares helpers to flatten nested DMA fence containers such as arrays and chains.

## Important APIs, Types, And Functions
Defines `struct dma_fence_unwrap`, `dma_fence_unwrap_first()`, `dma_fence_unwrap_next()`, `dma_fence_unwrap_for_each`, `__dma_fence_unwrap_merge()`, `dma_fence_dedup_array()`, and macro `dma_fence_unwrap_merge()`.

## Control Flow
The iterator starts from a head fence, descends through chain and array containers, and returns concrete underlying fences one at a time. Merge unwraps several input fences, deduplicates them, and returns a flat fence array representing the combined dependency set.

## State And Persistence
Iterator state is the current chain, current array, and array index. Merge uses stack cursor arrays through the macro and returns a refcounted fence object. No persistence exists.

## Dependencies And Integration Points
Depends conceptually on `dma-fence`, array fences, and chain fences. It integrates users that need to wait on or merge dependencies without recursive container handling.

## Risks And Edge Cases
Deduplication must preserve correct dependency coverage without leaking references. Deeply nested containers should not recurse on the C stack. Stack allocation in `dma_fence_unwrap_merge()` is proportional to argument count.

## Test Signals
Tests should cover plain fences, arrays, chains, nested array-chain combinations, duplicate fences, empty merge inputs, allocation failure, and iterator correctness after container children signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-fence-unwrap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-fence.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-fence.h

## Purpose
Defines the DMA fence synchronization primitive used to represent asynchronous DMA or hardware work completion across drivers.

## Important APIs, Types, And Functions
Core types are `struct dma_fence`, `struct dma_fence_cb`, and `struct dma_fence_ops`. APIs cover initialization, refcounting, RCU-safe get, locking, signaling, default waits, callbacks, software signaling, driver/timeline names, signaled/status checks, seqno ordering helpers, error setting, timestamp access, waits on one or any fence, deadlines, stub fences, context allocation, and container type checks.

## Control Flow
Drivers initialize a fence with ops, context, and seqno before publishing it. Waiters add callbacks or call wait functions, which may enable software signaling through the implementation. Producers set any error before signaling, then signal with timestamp, waking callbacks and waiters. Consumers compare seqnos only within the same context.

## State And Persistence
A fence stores an ops pointer, callback list until signaling, timestamp after signaling, RCU release state after destruction, context, seqno, flags, refcount, and optional negative error. It is transient synchronization state and can detach driver ops after signaling depending on callbacks.

## Dependencies And Integration Points
Depends on wait queues, spinlocks, krefs, RCU, timekeeping, lockdep, and seq files. It integrates DMA-BUF, DMA reservation objects, GPU schedulers, sync files, and drivers with hardware completion interrupts.

## Risks And Edge Cases
The lifetime contract is strict: external driver data behind ops must not be accessed after signaling unless protected by RCU. `enable_signaling()` can race with immediate signal and should take a reference if hardware interrupt handling needs it. Error must be set before signal. Custom wait/release ops keep modules loaded longer. Sequence comparisons across contexts are invalid, and 32-bit seqno wrap depends on flags.

## Test Signals
Tests should cover callback add/remove, wait timeout and interruptible wait, already signaled fences, error status, timestamp ordering, software-signaling enable races, RCU-safe get, context allocation, seqno wrap, deadline callbacks, stub fences, and lockdep signaling annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-fence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-heap.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-heap.h

## Purpose
Declares the DMA-BUF heaps allocation infrastructure, where named heaps allocate DMA-BUF objects for userspace or kernel consumers.

## Important APIs, Types, And Functions
Defines `struct dma_heap_ops` with mandatory `allocate()`, `struct dma_heap_export_info`, `dma_heap_get_drvdata()`, `dma_heap_get_name()`, `dma_heap_add()`, and global `mem_accounting`.

## Control Flow
A heap provider registers a named heap with private data and allocation ops. Consumers request allocations by heap name through the heap framework; the provider returns a `struct dma_buf` or an error pointer.

## State And Persistence
State is the registered heap object, provider private data, and allocations returned as DMA-BUFs. Heap registrations and buffers are runtime objects.

## Dependencies And Integration Points
Depends on DMA-BUF and heap provider drivers such as system, CMA, or vendor heaps. Integrates with userspace heap device nodes and memory accounting policy.

## Risks And Edge Cases
Heap names must be unique and stable. Allocation must validate length, fd flags, and heap flags. Providers must return proper error pointers and export DMA-BUFs with correct ops and reservation objects.

## Test Signals
Tests should cover heap registration, duplicate names, allocation success/failure, fd flags, heap private data lookup, name lookup, memory accounting toggles, and DMA-BUF lifetime after heap provider removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-heap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-map-ops.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-map-ops.h

## Purpose
Defines internal DMA mapping operation hooks and helpers for architecture and DMA core implementations. It is not intended for normal drivers using the public DMA API.

## Important APIs, Types, And Functions
`struct dma_map_ops` defines allocation, free, map/unmap phys and SG, sync, mmap, sgtable, mask, mapping-size, and merge-boundary callbacks. The header also declares `get_dma_ops()`, `set_dma_ops()`, CMA helpers, declared/global coherent memory helpers, common mmap/sgtable/remap/page helpers, DMA pool helpers, direct offset setup, coherence helpers, kmalloc DMA-safety helpers, architecture allocation/sync hooks, setup/teardown hooks, DMA debug hooks, and `dma_dummy_ops`.

## Control Flow
The public DMA API resolves per-device or architecture DMA ops, then calls these callbacks or direct/common helpers. Optional configuration blocks compile in CMA, declared coherent memory, global pools, architecture cache sync, direct map overrides, and debug tracing.

## State And Persistence
State includes per-device `dma_ops`, CMA areas, declared coherent pools, global coherent pools, device coherence flags, DMA skip-sync state, and debug mapping tables. It is runtime kernel/platform state.

## Dependencies And Integration Points
Depends on DMA mapping public API, page tables, slab alignment, CMA, architecture hooks, coherent memory pools, and DMA debug. It is the integration point between generic DMA code, IOMMUs, SWIOTLB, and arch-specific cache maintenance.

## Risks And Edge Cases
Normal drivers must not include this header. Non-coherent DMA with unaligned kmalloc buffers can corrupt adjacent cachelines; the bounce heuristics must be respected. Coherent pool fallbacks differ by config. Arch sync hooks may be no-ops on coherent systems. Setup/teardown ordering matters for hotplugged devices.

## Test Signals
Tests should cover builds with and without arch DMA ops, CMA allocation/free, declared/global coherent memory, non-coherent cache sync, kmalloc bounce heuristics, DMA debug mapping dumps, direct-map overrides, and device DMA ops setup/teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-map-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-mapping.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-mapping.h

## Purpose
Declares the public DMA mapping API used by drivers to map CPU memory, pages, scatterlists, resources, and coherent allocations for device DMA.

## Important APIs, Types, And Functions
The header defines DMA attributes, `DMA_MAPPING_ERROR`, `DMA_BIT_MASK()`, `struct dma_iova_state`, mapping-error and debug hooks, page/phys/SG/resource map/unmap APIs, coherent allocation APIs, mask APIs, mapping size queries, noncontiguous allocation/vmap/mmap helpers, optional IOVA APIs, cache sync APIs, page allocation helpers, single-buffer wrappers, sgtable sync/unmap helpers, coherent allocation wrappers, and per-structure `DEFINE_DMA_UNMAP_*` debug fields.

## Control Flow
Drivers map memory for a device with a direction and attributes, check `dma_mapping_error()`, hand the returned DMA address to hardware, synchronize ownership when required, and unmap after device use. Coherent allocation returns CPU and DMA addresses with a longer-lived ownership model. Noncontiguous and IOVA APIs separate address reservation/linking from mapping on IOMMU systems.

## State And Persistence
State is per-mapping DMA address, optional IOVA state, debug records, cache ownership, DMA masks, and allocated coherent/noncoherent pages. There is no persistence beyond live mappings and allocations.

## Dependencies And Integration Points
Depends on devices, pages, scatterlists, VMAs, DMA directions, cache alignment, IOMMU DMA, DMA API debug, and architecture DMA backends. It is used by almost all device drivers.

## Risks And Edge Cases
Mapping vmalloc memory through `dma_map_single_attrs()` is rejected. Attributes such as `SKIP_CPU_SYNC`, `MMIO`, `REQUIRE_COHERENT`, and `CC_SHARED` have strong platform constraints. Direction errors cause stale data or lost writes. SG unmap must use original nents. Noncoherent systems require correct sync calls unless the device can skip sync.

## Test Signals
DMA API debug, noncoherent platform tests, IOMMU and no-IOMMU builds, map/unmap leak checks, SG table round trips, resource/MMIO mappings, coherent mmap, noncontiguous vmap/mmap, mask boundary tests, and invalid vmalloc mapping warnings are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-mapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-resv.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-resv.h

## Purpose
Defines reservation objects that hold DMA fences for DMA-BUF, TTM, GEM, and other buffer managers.

## Important APIs, Types, And Functions
Defines `enum dma_resv_usage`, `dma_resv_usage_rw()`, `struct dma_resv`, and `struct dma_resv_iter`. Locking helpers wrap ww_mutex operations. APIs initialize/finalize objects, reserve fence slots, add/replace/copy/get fences, iterate fences locked or unlocked, wait/test by usage, set deadlines, and describe state.

## Control Flow
Writers lock the reservation object, reserve enough slots before point-of-no-return submission, then add fences with usage classifications. Readers either hold the reservation lock or use RCU lockless iterators that may restart. Wait/test helpers gather fences up to the requested usage ordering.

## State And Persistence
State is the ww_mutex lock and RCU fence list. Fence usage ordering is `KERNEL < WRITE < READ < BOOKKEEP`, and queries for one usage include lower usages. This is live synchronization state, not persistent storage.

## Dependencies And Integration Points
Depends on ww_mutex deadlock handling, DMA fences, slab, seqlock/RCU, and DMA-BUF implicit synchronization. It integrates dynamic buffer placement, command submission, and cross-driver buffer sharing.

## Risks And Edge Cases
Lock acquisition can return `-EDEADLK`, requiring callers to drop all locks in the ww acquire context and use slowpath locking. Fence slots must be reserved before adding because add cannot fail. Usage can be promoted but not degraded. Lockless iteration may restart, so accumulated statistics must check `dma_resv_iter_is_restarted()`.

## Test Signals
Tests should cover lock/trylock/interruptible/deadlock slowpath, reservation slot accounting, add and replace by context, usage filtering, lockless iterator restart, wait timeout, signaled tests, deadline propagation, fence copy, and debug max-fence reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-resv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/amd_xdma.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/amd_xdma.h

## Purpose
Declares AMD XDMA user interrupt helper APIs for platform devices.

## Important APIs, Types, And Functions
The API consists of `xdma_enable_user_irq()`, `xdma_disable_user_irq()`, and `xdma_get_user_irq()`, each operating on a `struct platform_device` and a user IRQ index or number.

## Control Flow
Platform consumers resolve a user IRQ with `xdma_get_user_irq()`, enable it when ready to receive interrupts, and disable it during teardown or masking.

## State And Persistence
State is controller-managed IRQ enablement and platform-device IRQ routing. There is no persistence.

## Dependencies And Integration Points
Depends on platform devices and interrupt infrastructure. It integrates AMD XDMA DMAengine/controller users with out-of-band user IRQ delivery.

## Risks And Edge Cases
Invalid IRQ indices or teardown races can enable the wrong line or leave interrupts active after resources are freed. Enable/disable must be balanced around handler lifetime.

## Test Signals
Tests should cover valid and invalid IRQ lookup, enable/disable balance, interrupt delivery after enable, no delivery after disable, and device removal with IRQs enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/amd_xdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/dw.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/dw.h

## Purpose
Declares the platform-facing interface for Synopsys DesignWare DMA and Intel iDMA32 controllers.

## Important APIs, Types, And Functions
`struct dw_dma_chip` describes controller device, instance id, IRQ, MMIO registers, clock, core private pointer, and platform data. APIs are `dw_dma_probe()`, `dw_dma_remove()`, `idma32_dma_probe()`, and `idma32_dma_remove()`, with stubs returning `-ENODEV` or 0 when the core is disabled.

## Control Flow
Platform glue fills `dw_dma_chip`, maps registers, provides clock/platform data, then calls the probe function. The core populates `chip->dw` and registers DMAengine channels. Remove tears down those resources.

## State And Persistence
State is the chip descriptor, MMIO mapping, clock handle, platform data, and core private `struct dw_dma`. No persistence exists.

## Dependencies And Integration Points
Depends on clocks, devices, DMAengine, and DesignWare platform data. It integrates platform/ACPI/PCI glue with the common DW DMA core.

## Risks And Edge Cases
Missing clock, bad IRQ, or wrong platform data can leave channels nonfunctional. Stub behavior must be handled by glue drivers when the core is not built.

## Test Signals
Build with and without `CONFIG_DW_DMAC_CORE`, probe/remove platform instances, DMAengine channel registration, IRQ handling, clock enable/disable, and iDMA32-specific probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/dw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/edma.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/edma.h

## Purpose
Declares the Synopsys DesignWare eDMA controller platform interface.

## Important APIs, Types, And Functions
Defines `EDMA_MAX_WR_CH`, `EDMA_MAX_RD_CH`, `struct dw_edma_region`, `struct dw_edma_plat_ops`, `enum dw_edma_map_format`, `enum dw_edma_chip_flags`, and `struct dw_edma_chip`. APIs are `dw_edma_probe()` and `dw_edma_remove()` with disabled stubs.

## Control Flow
Platform code describes register base, IRQ mapping, write/read linked-list regions, data regions, doorbell interrupt emulation, map format, and flags, then calls `dw_edma_probe()`. The core initializes DMAengine channels and stores private state in `chip->dw`.

## State And Persistence
State includes per-channel linked-list and data memory regions, IRQ vectors, register mapping format, local endpoint flag, non-linked-list config flag, and core private state. No persistence exists.

## Dependencies And Integration Points
Depends on devices, DMAengine, PCI address translation, and platform-specific IRQ/address ops. It integrates DW PCIe root/endpoint controllers with eDMA core code.

## Risks And Edge Cases
Write/read channel counts must not exceed eight. PCI address translation may be unnecessary or mandatory depending on iATU/DMA_BYPASS. Map-format mismatches can corrupt register access. Local endpoint flags affect address interpretation.

## Test Signals
Tests should cover each map format, IRQ-vector mapping, PCI address translation, channel-count boundaries, linked-list region setup, local endpoint mode, non-linked-list mode, and probe stubs when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/edma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/hsu.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/hsu.h

## Purpose
Declares the Intel High Speed UART DMA platform interface.

## Important APIs, Types, And Functions
`struct hsu_dma_chip` carries device, IRQ, MMIO base, register length, register offset, and core private pointer. APIs are `hsu_dma_get_status()`, `hsu_dma_do_irq()`, `hsu_dma_probe()`, and `hsu_dma_remove()`, with no-op or disabled stubs when `CONFIG_HSU_DMA` is off.

## Control Flow
Platform glue fills the chip descriptor, calls probe, forwards hardware interrupt status through `hsu_dma_do_irq()`, and can query per-channel status. Remove tears down DMAengine state.

## State And Persistence
Runtime state is the chip descriptor, MMIO range, channel status, and core private `struct hsu_dma`. No persistence exists.

## Dependencies And Integration Points
Depends on platform data, device/MMIO infrastructure, IRQ handling, and DMAengine core.

## Risks And Edge Cases
Status helper stubs return success when disabled, so callers must not assume real hardware handling unless probe succeeded. Register offset/length mistakes can read wrong status bits. IRQ forwarding must match channel numbers.

## Test Signals
Tests should cover build stubs, probe/remove, status query for valid and invalid channels, IRQ dispatch, register offset handling, and teardown with pending transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/hsu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/idma64.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/idma64.h

## Purpose
Provides the platform driver name constant for Intel LPSS iDMA64.

## Important APIs, Types, And Functions
Defines `LPSS_IDMA64_DRIVER_NAME` as `"idma64"`.

## Control Flow
No runtime control flow. Platform or ACPI glue can use the constant to register or match the iDMA64 driver name.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Integrates Intel LPSS platform code and the iDMA64 DMAengine driver through a shared string constant.

## Risks And Edge Cases
Changing the string would break driver binding for consumers that depend on the exact name.

## Test Signals
Build coverage and platform-driver binding tests for LPSS iDMA64 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/idma64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/imx-dma.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/imx-dma.h

## Purpose
Defines i.MX DMA/SDMA peripheral metadata used by slave drivers and DMAengine channel selection.

## Important APIs, Types, And Functions
Defines `enum sdma_peripheral_type`, `enum imx_dma_prio`, `struct imx_dma_data`, helpers `imx_dma_is_ipu()` and `imx_dma_is_general_purpose()`, and `struct sdma_peripheral_config` for multi-FIFO audio devices.

## Control Flow
Slave drivers pass request lines, peripheral type, and priority in `imx_dma_data`. Audio drivers can pass `sdma_peripheral_config` to describe FIFO counts, strides, words per FIFO, and software done behavior. Helpers identify IPU and general-purpose SDMA/DMA channels by device or driver names.

## State And Persistence
State is static per-transfer or per-channel configuration. No persistence is defined.

## Dependencies And Integration Points
Depends on DMAengine channels, scatterlists, devices, and i.MX SDMA/DMA driver naming. Integrates serial, MMC, audio, display, I2C, SPI, ATA, memory, and other i.MX peripherals with DMAengine.

## Risks And Edge Cases
Name-based helpers are brittle if driver names change. Multi-FIFO audio configuration must match hardware FIFO layout and channel count. Secondary request lines and priority must match SoC data.

## Test Signals
Tests should cover channel matching, request-line setup, all relevant peripheral types, multi-FIFO SAI/micfil capture/playback, stride and wrap behavior, software-done mode, and driver-name helper behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/imx-dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/k3-event-router.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/k3-event-router.h

## Purpose
Declares a minimal TI K3 event-router callback structure for routing DMA events.

## Important APIs, Types, And Functions
`struct k3_event_route_data` stores private data and a `set_event()` callback that programs a selected event.

## Control Flow
A consumer receives route data and calls `set_event(priv, event)` to configure event routing for a DMA or peripheral path.

## State And Persistence
State is provider private data and hardware event-router programming. No persistence exists.

## Dependencies And Integration Points
Depends only on kernel integer types and integrates TI K3 DMA/peripheral glue with event-router providers.

## Risks And Edge Cases
The callback must validate event IDs and provider lifetime. Consumers must not call after the provider is removed.

## Test Signals
Tests should cover valid/invalid event selection, provider removal, multiple consumers, and event delivery after routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/k3-event-router.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/k3-psil.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/k3-psil.h

## Purpose
Defines TI K3 PSI-L endpoint configuration metadata used to configure UDMA/PKTDMA threads.

## Important APIs, Types, And Functions
Defines `K3_PSIL_DST_THREAD_ID_OFFSET`, `enum udma_tp_level`, `enum psil_endpoint_type`, `struct psil_endpoint_config`, and `psil_set_new_ep_config()`. Config fields cover endpoint type, throughput level, packet vs TR mode, TDCM suppression, EPIB, PDMA ACC32/BURST, PS data size, mapped channel id, flow range, and default flow id.

## Control Flow
SoC/peripheral code registers or overrides endpoint configuration by device and name. UDMA setup consumes the endpoint config when pairing source/destination PSI-L threads and flows.

## State And Persistence
State is endpoint configuration associated with a device/name. It reflects runtime driver configuration of DMA thread behavior, not durable storage.

## Dependencies And Integration Points
Depends on devices and TI K3 UDMA/PKTDMA PSI-L topology. It integrates DMA controller setup with peripheral endpoint requirements.

## Risks And Edge Cases
Mapped channel and flow ranges must be internally consistent. Packet mode, EPIB, PS data size, and PDMA flags must match peripheral protocol. Destination thread IDs need the documented offset.

## Test Signals
Tests should cover native and PDMA endpoint types, throughput levels, packet/TR modes, mapped and unmapped channel flows, default flow validation, and invalid endpoint-name handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/k3-psil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/k3-udma-glue.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/k3-udma-glue.h

## Purpose
Declares TI K3 UDMA glue APIs that let network and peripheral drivers manage TX/RX channels, rings, descriptors, flows, and address conversions.

## Important APIs, Types, And Functions
TX types include `struct k3_udma_glue_tx_channel_cfg` and opaque TX channels, with request/release, push/pop, enable/disable, teardown, reset, descriptor size, completion queue id, IRQ, DMA-device, and CPPI5 address conversion APIs. RX types include `struct k3_udma_glue_rx_flow_cfg`, `struct k3_udma_glue_rx_channel_cfg`, opaque RX channels, flow selector constants, request/release, enable/disable, teardown, push/pop, flow init/enable/disable, FDQ/flow/IRQ queries, reset, DMA-device, and address conversion APIs.

## Control Flow
Drivers request TX or RX channels by name or thread id, configure rings/flows, push CPPI5 host descriptors to rings, pop completed descriptors, enable channels for traffic, and tear down/reset channels during stop. RX can allocate flow ranges dynamically, use RX channel id as flow id, or attach to a remote-owned channel.

## State And Persistence
State includes channel objects, ring configuration, flow ids, FDQ/RXQ ring ids, descriptor DMA addresses, teardown state, and remote-channel mode. It is runtime hardware/channel state.

## Dependencies And Integration Points
Depends on TI K3 ring accelerator, CPPI5 descriptors, device tree nodes, DMA addresses, and UDMA/PKTDMA controllers. Integrates Ethernet and other K3 peripheral drivers with NAVSS DMA.

## Risks And Edge Cases
Descriptor ownership and address conversion must be exact. Remote RX channels forbid normal channel operations and only allow attach/configure behavior. Flow id base/count/default settings must match hardware allocation. Reset cleanup callbacks must release any descriptors still in rings.

## Test Signals
Tests should cover TX/RX request by name and thread id, descriptor push/pop, IRQ queries, flow init/enable/disable, dynamic and fixed flow ranges, remote RX behavior, teardown sync/async, reset cleanup, CPPI5/DMA address conversion, and stop/remove with pending descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/k3-udma-glue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/mxs-dma.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/mxs-dma.h

## Purpose
Defines MXS DMA PIO control bits and a wrapper for preparing PIO transfers through DMAengine.

## Important APIs, Types, And Functions
Macros are `MXS_DMA_CTRL_WAIT4END` and `MXS_DMA_CTRL_WAIT4RDY`. `mxs_dmaengine_prep_pio()` wraps `dmaengine_prep_slave_sg()` by casting an array of PIO words to a scatterlist pointer when using PIO-style transfers.

## Control Flow
Drivers prepare PIO command words and call the wrapper with a DMA channel, word count, transfer direction, and flags. The MXS DMAengine interprets the passed words as PIO instructions when the direction indicates the special mode expected by the controller.

## State And Persistence
State is transient DMA descriptor/PIO word state. No persistence exists.

## Dependencies And Integration Points
Depends on DMAengine and MXS controller semantics. The wrapper exists to make the unusual PIO-as-SG cast explicit at call sites.

## Risks And Edge Cases
The cast is intentionally nonstandard; only MXS DMAengine consumers should use it. Direction and `npio` must match the controller's expectations, and the PIO word storage must remain valid until the descriptor is prepared.

## Test Signals
Tests should cover PIO command preparation, wait-for-end/ready flags, correct word count, invalid direction rejection by the DMAengine driver, and transfer completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/mxs-dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/pxa-dma.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/pxa-dma.h

## Purpose
Defines PXA DMA channel request metadata.

## Important APIs, Types, And Functions
`enum pxad_chan_prio` describes highest, normal, low, and lowest channel priority. `struct pxad_param` contains a DRCMR requestor line and minimal mandatory priority.

## Control Flow
Slave drivers pass `pxad_param` when requesting a DMA channel. The PXA DMA driver grants a channel with priority at least as strong as requested and programs the requestor line.

## State And Persistence
State is per-channel request configuration. No persistence exists.

## Dependencies And Integration Points
Integrates PXA peripheral drivers with the PXA DMAengine driver and SoC requestor-line routing.

## Risks And Edge Cases
Wrong DRCMR line routes transfers to the wrong peripheral. Priority is a minimum requirement, so callers should not assume an exact priority if a stronger channel is allocated.

## Test Signals
Tests should cover channel allocation for each priority, invalid requestor lines, priority fallback, and transfer routing for representative peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/pxa-dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/qcom-gpi-dma.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/qcom-gpi-dma.h

## Purpose
Defines Qualcomm GPI DMA peripheral configuration records for SPI and I2C transfers.

## Important APIs, Types, And Functions
SPI uses `enum spi_transfer_cmd` and `struct gpi_spi_config` with loopback, polarity, packing, word length, clock, chip select, fragmentation, config flag, command, and RX length fields. I2C uses `enum i2c_op` and `struct gpi_i2c_config` with packing, clock counts, address, stretch, config flag, RX length, operation, and multi-message flag.

## Control Flow
Peripheral drivers attach these configs to DMA descriptors so the GPI engine can perform protocol-aware SPI or I2C transactions. `set_config` indicates when static peripheral configuration should be emitted along with a transfer.

## State And Persistence
State is descriptor-level protocol configuration. No persistence exists beyond queued DMA transactions.

## Dependencies And Integration Points
Integrates Qualcomm SPI/I2C controller drivers with the GPI DMAengine.

## Risks And Edge Cases
Clock and polarity fields must match the peripheral controller setup. RX length and command/op fields must match buffer descriptors. Multi-message I2C transfers need correct repeated-start/sequence semantics.

## Test Signals
Tests should cover SPI TX/RX/duplex, chip-select fragmentation, packing, loopback, I2C read/write, multi-message transfers, clock-count programming, and invalid RX length handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/qcom-gpi-dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/qcom_adm.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/qcom_adm.h

## Purpose
Defines Qualcomm ADM DMA peripheral configuration.

## Important APIs, Types, And Functions
`struct qcom_adm_peripheral_config` contains `crci` and `mux` fields used to select peripheral request and mux routing.

## Control Flow
Peripheral drivers pass the config to the ADM DMA driver when requesting or configuring a DMA channel. The DMA driver programs CRCI and mux settings for the hardware path.

## State And Persistence
State is channel routing configuration. No persistence exists.

## Dependencies And Integration Points
Depends on Qualcomm ADM DMA controller semantics and peripheral request routing.

## Risks And Edge Cases
Incorrect CRCI or mux values route DMA requests incorrectly or prevent transfers. The structure has no validation by itself.

## Test Signals
Tests should cover representative peripherals, valid/invalid CRCI values, mux selection, and transfer completion after channel setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/qcom_adm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/qcom_bam_dma.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/qcom_bam_dma.h

## Purpose
Defines Qualcomm BAM DMA command element layout and helpers for preparing register read/write command descriptors.

## Important APIs, Types, And Functions
`struct bam_cmd_element` contains little-endian command/address, data, mask, and reserved words. `enum bam_command_type` defines write and read commands. Helpers `bam_prep_ce_le32()` and `bam_prep_ce()` pack a 24-bit target address and 8-bit command into `cmd_and_addr`, set data, and set a full mask.

## Control Flow
Drivers allocate command elements, prepare them with a register address, command type, and data or destination address, then submit them through BAM DMA command paths.

## State And Persistence
State is the command descriptor contents consumed by BAM hardware. No persistence exists after command completion.

## Dependencies And Integration Points
Depends on endian conversion and BAM DMA hardware command element format. Integrates peripheral register programming with DMA command streams.

## Risks And Edge Cases
Only the low 24 bits of address are encoded; higher bits are truncated. Data must be in little-endian form when using `_le32`. The helper does not initialize `reserved`, so callers may need to clear descriptors before use.

## Test Signals
Tests should verify command/address packing, endian conversion, read and write command elements, mask value, high-address truncation behavior, and hardware execution of register writes/reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/qcom_bam_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/sprd-dma.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/sprd-dma.h

## Purpose
Defines Spreadtrum DMA flags, two-stage transfer modes, request/interrupt modes, and link-list metadata.

## Important APIs, Types, And Functions
`SPRD_DMA_FLAGS()` packs channel mode, trigger mode, request mode, and interrupt type. Enums define channel roles for two-stage transfer, trigger points, request granularity, and interrupt types. `struct sprd_dma_linklist` carries virtual, physical, and wrap addresses for link-list mode.

## Control Flow
Slave drivers configure a DMA channel with packed flags. For two-stage transfers, source channel completion triggers a destination channel based on trigger mode. For link-list transfers, descriptors in always-on IRAM or coherent memory point to the next configuration, with the last node wrapping to the first.

## State And Persistence
State is DMA channel configuration and link-list descriptor memory. It persists only while the DMA channel and descriptor memory remain active.

## Dependencies And Integration Points
Integrates Spreadtrum peripheral drivers with the Spreadtrum DMA controller and DMAengine. Link-list mode depends on coherent or always-on memory visible to the controller.

## Risks And Edge Cases
Flag packing must match hardware bit fields. The comments contain transfer-state requirements: two-stage transfers require matching channel and trigger modes, and link lists must wrap correctly to avoid loading invalid configuration after the last descriptor. Descriptor memory must remain DMA-visible for the whole transfer.

## Test Signals
Tests should cover each request mode, interrupt type, two-stage trigger mode, source/destination channel pairing, link-list wrap behavior, config-error interrupt, and descriptor memory lifetime across suspend or clock gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/sprd-dma.h -->
