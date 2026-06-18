# Research Report: subset-b-005667

This grouped report covers the FUSE and GFS2 source files assigned to `subset-b-005667`. Each file section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/ioctl.c -->
# sources/distributed-fs/ceph-client/fs/fuse/ioctl.c

## Purpose
Implements FUSE file ioctl handling, including normal and compat ioctls, CUSE-compatible retry iovec marshalling, fs-verity special argument setup, and private ioctl helpers used by file attribute get/set operations.

## Important APIs, Types, And Functions
`fuse_do_ioctl()` is the exported core that builds `FUSE_IOCTL` requests, copies user iovec payloads into temporary folios, handles server `FUSE_IOCTL_RETRY`, and copies reply data back to user buffers. `fuse_ioctl_common()`, `fuse_file_ioctl()`, and `fuse_file_compat_ioctl()` provide VFS-facing wrappers with access and bad-inode checks. `fuse_send_ioctl()` centralizes request submission and translates `-ENOSYS` to `-ENOTTY`. `fuse_copy_ioctl_iovec_old()` supports legacy pre-minor-16 iovec ABI and compat iovec layout. `fuse_copy_ioctl_iovec()` validates modern `struct fuse_ioctl_iovec` base/length values and compat truncation. `fuse_setup_measure_verity()` and `fuse_setup_enable_verity()` derive correct iovec lengths and extra salt/signature user buffers for fs-verity ioctls. `fuse_priv_ioctl()`, `fuse_priv_ioctl_prepare()`, and cleanup helpers open a temporary FUSE file handle for internal file-attribute ioctls. `fuse_fileattr_get()` and `fuse_fileattr_set()` adapt VFS fileattr APIs to `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`, `FS_IOC_FSGETXATTR`, and `FS_IOC_FSSETXATTR`.

## Control Flow
Restricted ioctls initialize in/out iovecs from `_IOC_DIR` and `_IOC_SIZE`; unrestricted ioctls start with no deep-copy areas and allow the server to request retry iovecs. `fuse_do_ioctl()` allocates folio buffers up to `fc->max_pages`, copies requested input user memory, sends a `FUSE_IOCTL` request, and either retries after parsing returned iovecs or finalizes by copying output pages into user memory. Retry paths verify iovec count and cumulative lengths before looping. Private fileattr ioctls take a temporary open reference, submit a simple non-retry ioctl, and release the file.

## State And Persistence
The file itself stores no persistent filesystem state. It mutates request-local `fuse_args_pages`, folio arrays, and `outarg.result`. File attribute operations may persist remote filesystem state through the userspace server. `FUSE_IOCTL_32BIT`, `FUSE_IOCTL_COMPAT`, `FUSE_IOCTL_DIR`, and fs-verity-derived iovecs define ABI-visible request state.

## Dependencies And Integration Points
Depends on FUSE request infrastructure in `fuse_i.h`, page/folio allocation, `iov_iter`, Linux compat ABI helpers, `fileattr`, and fs-verity ioctl structures. Exports `fuse_do_ioctl()` for use elsewhere in FUSE. Integrates with VFS ioctl and fileattr operations and with userspace FUSE/ CUSE servers.

## Risks
Iovec validation is security-critical because server-provided retry vectors drive user-memory copying. Overflow checks in `fuse_verify_ioctl_iov()` and max page enforcement are important DoS boundaries. Compat ABI handling can reject valid-looking data when client/server bitness assumptions mismatch. Restricted mode deliberately forbids retry; accepting retry there would allow excessive deep-copy authority. fs-verity salt/signature sizes are capped at 256 pages to bound memory use.

## Test Signals
Exercise normal ioctl, compat ioctl, restricted and unrestricted retry, malformed iovec sizes, excessive iovec lengths, `ENOSYS` translation to `ENOTTY`, fs-verity measure/enable with and without salt/signature, and fileattr get/set paths against a FUSE server that records request fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/iomode.c -->
# sources/distributed-fs/ceph-client/fs/fuse/iomode.c

## Purpose
Coordinates per-inode FUSE I/O modes so cached page-cache access, uncached direct I/O, mmap fallback, and passthrough backing-file access do not run in unsafe combinations.

## Important APIs, Types, And Functions
`fuse_file_cached_io_open()` enters cached mode and blocks new parallel direct writes while waiting for existing uncached writers to drain. `fuse_inode_uncached_io_start()` starts an uncached section and optionally installs a `struct fuse_backing` on the inode. `fuse_inode_uncached_io_end()` drops uncached references, clears backing state when the counter returns to zero, and wakes waiters. `fuse_file_passthrough_open()` validates `FOPEN_PASSTHROUGH` combinations and opens a backing file. `fuse_file_io_open()` is the main open-time policy decision. `fuse_file_io_release()` releases cached or uncached mode references according to `ff->iomode`.

## Control Flow
Open requests bypass mode logic for DAX or servers without `OPEN`. Existing inode backing requires all future opens to request passthrough. Direct I/O without passthrough remains uncached but does not enter inode mode here; cached and passthrough opens take explicit references. Cached opens wait while `iocachectr` is negative and no backing file exists, set `FUSE_I_CACHE_IO_MODE`, and increment `iocachectr`. Passthrough opens first obtain a backing file then enter uncached mode; failure releases the backing handle.

## State And Persistence
The core state is `fi->iocachectr`: positive for cached users, zero for no mode, negative for uncached users. `FUSE_I_CACHE_IO_MODE` advertises cache-mode exclusion. `fuse_inode_backing(fi)` holds at most one backing object while passthrough is active. `ff->iomode` records the per-open reference that must be released.

## Dependencies And Integration Points
Depends on FUSE inode/file structures, direct-I/O wait queues, passthrough backing-file helpers, and `FOPEN_*` open flags returned by the server. Integrates with open/release paths and mmap/direct-I/O paths that need cache exclusion.

## Risks
Incorrect counter transitions can deadlock cached opens or allow page-cache and passthrough access to coexist. Server misuse of `FOPEN_PASSTHROUGH` or `FOPEN_PARALLEL_DIRECT_WRITES` intentionally turns into user-visible `EIO`. Multiple backing files for the same inode are rejected with `EBUSY`, so caller cleanup must be exact.

## Test Signals
Test concurrent cached opens and direct writes, passthrough first-open with later non-passthrough open rejection, multiple backing IDs on one inode, release balancing, `FOPEN_DIRECT_IO` flag normalization, and wait/wake behavior when uncached writers drain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/iomode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/passthrough.c -->
# sources/distributed-fs/ceph-client/fs/fuse/passthrough.c

## Purpose
Implements FUSE passthrough operations that satisfy read, write, splice, and mmap through a kernel backing file while keeping FUSE inode metadata coherent.

## Important APIs, Types, And Functions
`fuse_passthrough_read_iter()`, `fuse_passthrough_write_iter()`, `fuse_passthrough_splice_read()`, `fuse_passthrough_splice_write()`, and `fuse_passthrough_mmap()` wrap `backing_file_*` helpers using `struct backing_file_ctx`. `fuse_file_accessed()` invalidates FUSE atime after backing reads. `fuse_passthrough_end_write()` updates FUSE write attributes. `fuse_passthrough_open()` resolves a server-supplied backing ID, opens a per-FUSE-file backing handle, and stores backing credentials. `fuse_passthrough_release()` drops the file and credential references.

## Control Flow
Read and splice-read operations short-circuit zero length and otherwise dispatch to backing-file helpers with access callbacks. Write and splice-write take the FUSE inode lock around backing writes so size and write metadata updates remain serialized. `mmap` delegates to `backing_file_mmap()`. Open validates a positive `backing_id`, looks up the shared `fuse_backing`, opens a per-file backing view at the FUSE path, stores it in `ff`, and returns the backing object for inode-mode ownership.

## State And Persistence
Per-open state is `ff->passthrough` and `ff->cred`. Persistent data is written by the lower backing file. FUSE metadata is adjusted through atime invalidation and write attribute updates so cached inode state reflects lower-file operations.

## Dependencies And Integration Points
Depends on `linux/backing-file.h`, FUSE backing lookup/refcounting, and iomode code that decides when passthrough can be enabled. Integrates with the FUSE file operations table for passthrough-capable files and with `fuse_file_io_open()`/release.

## Risks
Credential handling is security-sensitive because lower-file access runs under backing credentials. Writes must keep FUSE inode size/ctime/mtime coherent with lower writes. Open failure paths must release both `fuse_backing` and per-file backing handles. Passthrough mmap can bypass ordinary FUSE page-cache semantics, so it relies on iomode exclusion.

## Test Signals
Validate reads, writes, splice I/O, mmap faults, credential-denied backing opens, zero-length I/O, size and timestamp updates after writes, atime invalidation after reads, and cleanup after failed passthrough open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/passthrough.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/readdir.c -->
# sources/distributed-fs/ceph-client/fs/fuse/readdir.c

## Purpose
Implements FUSE directory iteration with optional READDIRPLUS lookup/linking and an inode page-cache-backed directory-entry cache for `FOPEN_CACHE_DIR`.

## Important APIs, Types, And Functions
`fuse_readdir()` selects cached or uncached paths. `fuse_readdir_uncached()` sends `FUSE_READDIR` or `FUSE_READDIRPLUS` and parses returned buffers. `fuse_use_readdirplus()` decides plus mode from connection flags, auto mode, and inode advisory bits. `parse_dirfile()` validates and emits plain dirents. `parse_dirplusfile()` emits entries and links returned attributes into the dcache/inode cache. `fuse_direntplus_link()` handles inode lookup, alias splicing, attr refresh, ACL invalidation, lookup refcounts, and entry timeouts. `fuse_readdir_cached()`, `fuse_add_dirent_to_cache()`, `fuse_readdir_cache_end()`, `fuse_parse_cache()`, and `fuse_rdc_reset()` maintain the page-backed readdir cache.

## Control Flow
Uncached reads allocate a bounded buffer, choose plus or plain opcode, lock the inode around the request, parse replies, mark cache complete on EOF, and invalidate atime. Plus parsing continues linking entries even after the caller buffer is full to avoid leaking lookup counts; failed links trigger forced `FORGET`. Cached reads verify seek position, refresh mtime at directory start when auto invalidation is enabled, validate cache version/mtime/iversion, map cached pages, parse dirents, and fall back to uncached if the requested position is not represented.

## State And Persistence
`fi->rdc` stores directory-cache lock, `cached` completion flag, version, size, stream position, mtime, and inode version. `ff->readdir` stores each open file's cache offset, directory position, and observed cache version. READDIRPLUS mutates dcache/inode state, `nlookup`, entry timeout, attr versioning, and ACL cache.

## Dependencies And Integration Points
Depends on FUSE read request builders, inode attr/version helpers, dcache APIs, ACL cache invalidation, page-cache APIs, and FUSE forget semantics. Integrates with directory file operations and lookup coherency.

## Risks
Directory entry parsing is corruption-sensitive: invalid lengths, slash-containing names, zero names, and oversized names return `EIO`. READDIRPLUS lookup reference accounting must send `FORGET` on failed linkage. Cache invalidation relies on mtime and i_version; stale or racing cache pages reset the cache. Auto READDIRPLUS policy changes latency and lookup behavior.

## Test Signals
Cover plain readdir, readdirplus, auto-plus first read and advisory bit behavior, invalid dirent buffers, cache fill/EOF, seek and rewind, mtime/i_version invalidation, dcache alias replacement, forced forget on link failure, and caller buffer overflow behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/readdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/sysctl.c -->
# sources/distributed-fs/ceph-client/fs/fuse/sysctl.c

## Purpose
Registers `/proc/sys/fs/fuse` tunables for global FUSE request sizing and timeout limits.

## Important APIs, Types, And Functions
`fuse_sysctl_table` exposes `max_pages_limit`, `default_request_timeout`, and `max_request_timeout` through `proc_douintvec_minmax`. `fuse_sysctl_register()` registers the table under `fs/fuse`. `fuse_sysctl_unregister()` unregisters it and clears the header pointer.

## Control Flow
Module initialization calls register, which stores the returned `ctl_table_header`; teardown unregisters the same header. Each entry enforces a minimum and a u16-compatible maximum.

## State And Persistence
The file modifies global variables declared elsewhere: `fuse_max_pages_limit`, `fuse_default_req_timeout`, and `fuse_max_req_timeout`. Values live in kernel memory and affect future FUSE connection/request behavior but are not persistent across boot unless managed by userspace sysctl configuration.

## Dependencies And Integration Points
Depends on Linux sysctl infrastructure and FUSE global config variables. Integrates with FUSE initialization/exit code.

## Risks
Too-large limits would exceed protocol field widths, so upper bounds are u16-derived. Runtime tuning can affect memory use and hung-request behavior across all FUSE mounts.

## Test Signals
Verify sysctl registration, unregister cleanup, min/max enforcement, read/write permissions, and that changed limits affect new FUSE request negotiation/timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/trace.c -->
# sources/distributed-fs/ceph-client/fs/fuse/trace.c

## Purpose
Materializes FUSE tracepoint definitions by defining `CREATE_TRACE_POINTS` and including `fuse_trace.h`.

## Important APIs, Types, And Functions
There are no runtime functions in this file. It includes internal FUSE headers needed by tracepoint field definitions and `linux/pagemap.h`, then instantiates tracepoint storage and metadata.

## Control Flow
Compile-time only: the tracepoint macro expansion creates trace event definitions for other FUSE code to call.

## State And Persistence
No persistent filesystem state. It contributes static tracepoint objects to the kernel/module image.

## Dependencies And Integration Points
Depends on `dev_uring_i.h`, `fuse_i.h`, `fuse_dev_i.h`, and `fuse_trace.h`. Integrates with ftrace/perf/BPF tracing and any FUSE code that emits those events.

## Risks
Tracepoint structure changes affect observability ABI expected by tools. Missing includes or type drift breaks tracepoint compilation.

## Test Signals
Build with tracing enabled, list FUSE tracepoints, and exercise FUSE requests while confirming trace events can be enabled without runtime faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/virtio_fs.c -->
# sources/distributed-fs/ceph-client/fs/fuse/virtio_fs.c

## Purpose
Implements the virtio-fs transport and filesystem registration layer: discovers virtio filesystem devices, exposes them in sysfs, maps FUSE requests onto virtqueues, handles completions and forgets, optionally sets up DAX shared memory, and mounts virtiofs through the common FUSE superblock path.

## Important APIs, Types, And Functions
`struct virtio_fs` stores device instance state: tag, virtqueues, CPU-to-queue map, DAX device, and shared memory window. `struct virtio_fs_vq` stores per-virtqueue lock, queued/end request lists, work items, FUSE device pointer, connection flag, and in-flight count. Probe/remove are handled by `virtio_fs_probe()` and `virtio_fs_remove()`. Queue setup and teardown use `virtio_fs_setup_vqs()`, `virtio_fs_init_vq()`, `virtio_fs_map_queues()`, `virtio_fs_start_all_queues()`, `virtio_fs_stop_all_queues()`, and drain helpers. Request transport uses `virtio_fs_send_req()`, `virtio_fs_enqueue_req()`, SG counting/init helpers, `copy_args_to_argbuf()`, `copy_args_from_argbuf()`, completion workers, and response verification. Forget handling uses the hiprio queue via `virtio_fs_send_forget()` and `send_forget_request()`. Mount integration uses `virtio_fs_init_fs_context()`, `virtio_fs_parse_param()`, `virtio_fs_get_tree()`, `virtio_fs_fill_super()`, `virtio_kill_sb()`, and `virtio_fs_conn_destroy()`. DAX support uses `virtio_fs_setup_dax()`, `virtio_fs_direct_access()`, and `virtio_fs_zero_page_range()`.

## Control Flow
Device probe allocates an instance, reads and validates the tag, creates virtqueues, maps request queues to CPUs, optionally maps the DAX cache window, marks the virtio device ready, and publishes the instance in sysfs/list state. Mount lookup finds an instance by tag, creates FUSE connection/mount objects, caps `max_pages_limit` by virtqueue size, shares superblocks per instance, allocates one `fuse_dev` per queue, fills the common FUSE superblock, installs devices, restarts queues, and sends FUSE INIT. Request submission assigns a unique ID, selects a request queue from `mq_map`, builds scatterlists from headers/argbuf/folios, adds the request to the virtqueue and FUSE processing hash, and kicks the device. Full queues move requests to per-vq queued lists for workqueue retry. Completion workers collect buffers, verify response length and unique ID, copy out args, zero short page replies when requested, end FUSE requests, and decrement in-flight counts. Remove/unmount paths stop queues, drain in-flight work, reset virtio queues, and release FUSE devices and instance refs.

## State And Persistence
Global state includes `virtio_fs_instances`, `virtio_fs_mutex`, and `/sys/fs/virtiofs` kset state. Per-device state includes tag, virtqueues, CPU mapping, DAX window mapping, sysfs kobjects, and queue connection/in-flight counters. Per-request transient state includes `req->argbuf`, `FR_SENT`, processing-list membership, and virtqueue buffer ownership. The file does not persist filesystem contents itself; persistence is provided by the host virtiofs daemon/backing store.

## Dependencies And Integration Points
Depends on virtio core, FUSE connection and device queues, fs_context parsing, sysfs/kobject APIs, DAX/dev_pagemap infrastructure, workqueues, scatterlists, CPU affinity helpers, and common FUSE superblock code. Integrates as a `virtio_driver` for `VIRTIO_ID_FS` and a `file_system_type` named `virtiofs`.

## Risks
Transport correctness depends on SG layout matching the FUSE protocol and virtqueue direction conventions. Response verification prevents misdelivered or malformed replies but converts failures to `EIO`. Queue-full retry paths must preserve in-flight accounting exactly. Remove/unmount races are controlled by `virtio_fs_mutex`, connected flags, and queue drains. DAX setup maps device memory into kernel address space and must reject missing or busy cache windows. Suspend/resume is not supported and returns `EOPNOTSUPP`.

## Test Signals
Test probe/remove, duplicate tags, invalid/newline tags, mount by tag, no-source mount failure, multiqueue CPU mapping, full virtqueue retry, malformed response headers, forget queue pressure, unmount while requests are in flight, DAX `dax=always/never/inode` behavior, sysfs attributes and uevents, and max_pages limiting by vring size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/virtio_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/xattr.c -->
# sources/distributed-fs/ceph-client/fs/fuse/xattr.c

## Purpose
Implements FUSE extended attribute get, set, list, and remove operations plus the generic xattr handler table used by VFS.

## Important APIs, Types, And Functions
`fuse_setxattr()` sends `FUSE_SETXATTR`, including extended `setxattr_flags` when negotiated. `fuse_getxattr()` sends `FUSE_GETXATTR`, supporting size-query and value-fetch modes. `fuse_listxattr()` sends `FUSE_LISTXATTR`, validates returned name lists, and enforces permission/bad-inode checks. `fuse_removexattr()` sends `FUSE_REMOVEXATTR`. `fuse_verify_xattr_list()` validates NUL-separated xattr names. `fuse_xattr_get()` and `fuse_xattr_set()` implement `struct xattr_handler`; `fuse_xattr_handlers` registers a catch-all empty-prefix handler.

## Control Flow
Each operation checks cached `fc->no_*` capability flags, builds a FUSE request with inode nodeid and name/value args, and maps `-ENOSYS` to `-EOPNOTSUPP` while caching the unsupported operation. Get/list with size zero request only the returned size structure; nonzero calls allow variable-length output. Set/remove update inode ctime after success.

## State And Persistence
Unsupported-operation booleans in `struct fuse_conn` are updated after `ENOSYS`. Successful set/remove persist xattr changes through the userspace server and update local ctime state. List validation does not persist state.

## Dependencies And Integration Points
Depends on FUSE request helpers, Linux xattr and POSIX ACL xattr headers, inode state helpers, and VFS xattr handler dispatch.

## Risks
Malformed xattr list responses are treated as `EIO`. Server `ENOSYS` disables future attempts for the connection. Size-query paths clamp to `XATTR_SIZE_MAX` and `XATTR_LIST_MAX`, which callers should observe. Permission checks exist for listxattr but get/set wrappers rely on VFS and bad-inode checks.

## Test Signals
Exercise set/get/remove/list success, unsupported server fallback, size-only get/list, malformed list without NUL terminator, ctime updates, bad inode behavior, and extended setxattr flag negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/Kconfig -->
# sources/distributed-fs/ceph-client/fs/gfs2/Kconfig

## Purpose
Defines build-time configuration for GFS2 filesystem support and optional DLM cluster locking support.

## Important APIs, Types, And Functions
`config GFS2_FS` is a tristate enabling the GFS2 filesystem and selecting buffer heads, POSIX ACLs, CRC32, quota control, and iomap support. `config GFS2_FS_LOCKING_DLM` enables the DLM locking module when GFS2, networking, configfs, sysfs, and compatible DLM availability are present.

## Control Flow
Kconfig dependency resolution decides whether GFS2 can be built in, modularized, or disabled. The DLM option is only offered when its dependency expression is satisfied.

## State And Persistence
No runtime state. It controls compiled features and therefore persistent kernel/module capabilities.

## Dependencies And Integration Points
Feeds the kernel build system and `fs/gfs2/Makefile`. Selected symbols ensure required VFS, ACL, CRC, quota, and iomap support is present.

## Risks
Incorrect dependency constraints can allow invalid builds or hide cluster support. DLM depends on networking/configfs/sysfs because clustered locking requires those subsystems.

## Test Signals
Run Kconfig build combinations for built-in/module GFS2, DLM enabled/disabled, missing DLM/network prerequisites, and verify selected symbols propagate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/Makefile -->
# sources/distributed-fs/ceph-client/fs/gfs2/Makefile

## Purpose
Builds the `gfs2.o` composite object from GFS2 implementation files and conditionally includes DLM locking support.

## Important APIs, Types, And Functions
`ccflags-y := -I$(src)` adds local include search path. `obj-$(CONFIG_GFS2_FS) += gfs2.o` binds the object to the Kconfig symbol. `gfs2-y` enumerates core object files. `gfs2-$(CONFIG_GFS2_FS_LOCKING_DLM) += lock_dlm.o` adds DLM support when enabled.

## Control Flow
Kbuild expands the object lists according to configuration and links all listed `.o` files into the GFS2 module or built-in object.

## State And Persistence
No runtime state. It controls which implementation units are present in the resulting kernel/module.

## Dependencies And Integration Points
Integrates with Kbuild and Kconfig. The file list couples public headers and cross-file symbols among ACL, bmap, dir, glock, log, quota, recovery, rgrp, super, transaction, and utility components.

## Risks
Omitting an object causes unresolved symbols or missing runtime behavior. Adding DLM unconditionally would break non-cluster builds.

## Test Signals
Build GFS2 as module and built-in, with and without `CONFIG_GFS2_FS_LOCKING_DLM`, and run modpost for unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/acl.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/acl.c

## Purpose
Implements POSIX ACL get/set support for GFS2 by mapping ACLs to system extended attributes under the inode glock.

## Important APIs, Types, And Functions
`gfs2_acl_name()` maps `ACL_TYPE_ACCESS` and `ACL_TYPE_DEFAULT` to POSIX ACL xattr names. `__gfs2_get_acl()` reads ACL xattr data with `gfs2_xattr_acl_get()` and converts it via `posix_acl_from_xattr()`. `gfs2_get_acl()` is the VFS-facing getter and acquires a shared inode glock if needed. `__gfs2_set_acl()` serializes an ACL with `posix_acl_to_xattr()`, writes it through `__gfs2_xattr_set()`, and updates the cached ACL. `gfs2_set_acl()` validates ACL entry count, obtains quota accounting, takes an exclusive glock if needed, updates mode bits for access ACLs, writes the ACL, and marks the inode dirty if mode changed.

## Control Flow
Get rejects RCU lookup with `-ECHILD`, avoids disk access when no extended attributes exist, and conditionally locks. Set checks maximum ACL entries, acquires quota state, locks exclusively unless already held, possibly rewrites inode mode, writes xattr state, then unwinds lock and quota references.

## State And Persistence
ACLs persist as GFS2 system xattrs. Access ACL updates may persist inode mode changes, ctime, and dirty inode state. Cached ACL state is updated after successful writes.

## Dependencies And Integration Points
Depends on GFS2 xattr, glock, quota, transaction/inode dirtying paths, and Linux POSIX ACL conversion APIs. Used by inode operation tables elsewhere in GFS2.

## Risks
Set must coordinate quota and glock state or cluster-visible ACL/mode updates can race. Entry-count limits scale with block size. RCU ACL lookup is unsupported. Mode updates must remain consistent with ACL xattr writes.

## Test Signals
Test access/default ACL get/set/remove, oversized ACL rejection, mode-bit changes from access ACLs, concurrent cluster lookup under glocks, no-eattr fast path, and quota failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/acl.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/acl.h

## Purpose
Declares GFS2 POSIX ACL helpers and defines the block-size-scaled maximum ACL entry count.

## Important APIs, Types, And Functions
`GFS2_ACL_MAX_ENTRIES(sdp)` computes the maximum ACL entries from superblock block-size shift. Declarations include `gfs2_get_acl()`, `__gfs2_set_acl()`, and `gfs2_set_acl()`.

## Control Flow
No runtime control flow beyond macro expansion.

## State And Persistence
No state. The macro constrains ACL state stored by `acl.c`.

## Dependencies And Integration Points
Includes `incore.h` for `struct gfs2_sbd` access and is consumed by ACL and inode operation code.

## Risks
The macro must match xattr storage capacity; underestimating rejects valid ACLs, overestimating risks impossible xattr writes.

## Test Signals
Compile users of ACL helpers and test ACL entry limits across supported GFS2 block sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/aops.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/aops.c

## Purpose
Provides GFS2 address-space operations for buffered reads, readahead, writeback, dirtying, bmap, invalidation, and folio release, with separate behavior for ordinary/ordered data and journaled-data files.

## Important APIs, Types, And Functions
`gfs2_read_folio()` dispatches to iomap, stuffed-file read, or mpage read for jdata. `gfs2_readahead()` selects mpage or iomap readahead and skips stuffed files. `gfs2_writepages()` uses `iomap_writepages()` with `gfs2_writeback_ops` and can force AIL flush. `gfs2_jdata_writepages()` and helpers batch dirty folios inside GFS2 transactions before log flush/retry. `gfs2_jdata_writeback()` writes journaled data when the inode glock is exclusive. `gfs2_internal_read()` reads internal files through the page cache. `adjust_fs_space()` updates statfs state after filesystem growth. `gfs2_bmap()` maps logical blocks under a shared glock. `gfs2_invalidate_folio()` and `gfs2_release_folio()` handle buffer-head cleanup for jdata. `gfs2_set_aops()` chooses `gfs2_aops` or `gfs2_jdata_aops`.

## Control Flow
Ordinary files use iomap read/writeback/dirty/release paths. Journaled-data writeback walks tagged dirty folios, starts transactions before locking batches, adds checked folios to the transaction, writes via block helpers, and flushes the log for data-integrity sync. Stuffed reads copy inline data from the dinode into a folio. Invalidation discards journal buffer state for full or partial folio ranges. Release refuses folios with active, dirty, pinned, or transaction-owned buffers.

## State And Persistence
Mutates folio dirty, checked, uptodate, writeback, and buffer-head journal state. Updates GFS2 transaction logs, AIL flush flags, inode dirty state, statfs master/local counters, and rindex freshness. Persistent data reaches disk through iomap/mpage writeback or the GFS2 journal.

## Dependencies And Integration Points
Depends on `bmap.c` iomap/writeback operations, glocks, log, transactions, metadata I/O, quota/resource-group code, and Linux folio/writeback APIs. Selected by inode setup and used by VFS page cache.

## Risks
Journaled-data mode must start transactions before folio locks to avoid lock-order problems. Dirty buffers in AIL can stall `balance_dirty_pages()` unless AIL flush is forced. Stuffed/jdata paths use buffer heads while ordinary files use iomap, so aops selection must track inode mode. Folio release must not free journal-owned buffers.

## Test Signals
Test buffered reads for stuffed, jdata, and ordinary files; readahead; WB_SYNC_NONE and WB_SYNC_ALL writeback; log flush after jdata sync; bmap under glock; folio invalidation/release with pinned/dirty buffers; filesystem grow statfs adjustment; and withdrawn filesystem `EIO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/aops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/aops.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/aops.h

## Purpose
Declares the GFS2 address-space helper functions exported from `aops.c`.

## Important APIs, Types, And Functions
`adjust_fs_space()` updates filesystem free-space accounting after rindex growth. `gfs2_jdata_writeback()` writes journaled-data mapping contents under writeback control.

## Control Flow
No local runtime flow; this header provides declarations.

## State And Persistence
No state in the header. Declared functions mutate statfs/journal/page-cache state in `aops.c`.

## Dependencies And Integration Points
Includes `incore.h` and is consumed by bmap/grow and GFS2 writeback code.

## Risks
Prototype drift would break cross-file callers. Keeping only necessary declarations avoids broader include coupling.

## Test Signals
Compile all GFS2 objects and exercise filesystem grow plus jdata writeback callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/aops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/bmap.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/bmap.c

## Purpose
Maps GFS2 logical file blocks to disk blocks, allocates extents through iomap, unstuffs inline files, handles truncation/hole punching/deallocation, computes allocation requirements, and builds journal extent caches.

## Important APIs, Types, And Functions
`struct metapath` records the metadata-tree path and buffers. `gfs2_unstuff_dinode()` moves stuffed inline data into normal blocks. `find_metapath()`, `lookup_metapath()`, `fillup_metapath()`, and `release_metapath()` traverse indirect metadata. `__gfs2_iomap_get()` maps inline, hole, or mapped extents; `gfs2_iomap_begin()`, `gfs2_iomap_end()`, and `gfs2_iomap_ops` integrate with iomap. `__gfs2_iomap_alloc()` allocates indirect/data blocks and grows tree height/depth. `gfs2_block_map()`, `gfs2_get_extent()`, and `gfs2_alloc_extent()` provide buffer-head and extent mapping APIs for other GFS2 code. `trunc_start()`, `punch_hole()`, `trunc_end()`, `do_shrink()`, `do_grow()`, and `gfs2_setattr_size()` implement size changes. `gfs2_map_journal_extents()` caches journal file extents. `__gfs2_punch_hole()` supports fallocate-style punching and zeroing partial blocks. `gfs2_writeback_ops` maps folios for iomap writeback.

## Control Flow
Mapping starts with the dinode buffer, handles stuffed files inline, computes target tree height, walks existing metadata, reports holes or extents, and optionally reserves quota/resource groups to allocate. Allocation is a state machine: grow tree height, fill missing depth, then install data block pointers. Iomap end releases reservations, unlocks quotas, cleans up partially written new blocks by punching the unwritten tail, and marks glocks dirty. Truncation first zeroes partial blocks, marks truncate-in-progress, changes i_size, truncates page cache or journaled ranges, deallocates blocks bottom-up by resource group, updates statfs/quota, and clears truncate-in-progress. Hole punching separately zeroes unaligned edges, waits for page cache writeback, truncates cache/jdata ranges, updates timestamps, and deallocates whole blocks.

## State And Persistence
Persists dinode height, size, disk flags, block pointers, inode block counts, journal revokes, statfs/quota changes, resource-group bitmaps, and journal extent lists. Uses `GFS2_DIF_TRUNC_IN_PROG` to support recovery/resume after interrupted truncation. Page cache is truncated or zeroed to match on-disk deallocation.

## Dependencies And Integration Points
Depends on GFS2 glocks, metadata I/O, resource groups, quota, transactions, directory buffer allocation, iomap, buffer heads, and writeback. Provides core mapping services to aops, dir, file, journal, and inode code.

## Risks
This is one of the highest-risk GFS2 files. Metadata-tree updates must be journaled in recoverable order. Resource-group locking is split to reduce contention but must avoid freeing blocks under the wrong rgrp. Partial write failures must deallocate just-created blocks. Journaled-data truncation must split revoke-heavy work into bounded transactions. Stuffed-to-unstuffed transitions must preserve data and mode-specific journaling. Direct I/O intentionally falls back when a write would hit holes or stuffed data.

## Test Signals
Test block mapping of holes, inline data, single/multi-level extents, allocation across indirect boundaries, partial write failures, direct-I/O fallback, grow and shrink truncate, crash/recovery with truncate-in-progress, fallocate punch hole including unaligned edges, journal extent mapping, quota/statfs updates, and resource-group contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/bmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/bmap.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/bmap.h

## Purpose
Declares GFS2 block mapping, iomap, allocation, truncation, journal extent, and punch-hole APIs, plus the write reservation estimation helper.

## Important APIs, Types, And Functions
`gfs2_write_calc_reserv()` estimates data and indirect blocks needed for a write based on block size, dinode pointers, and indirect fanout. Externs include `gfs2_iomap_ops`, `gfs2_iomap_write_ops`, `gfs2_writeback_ops`, unstuffing, block mapping, iomap get/alloc, extent get/alloc, size changes, truncate resume, file deallocation, allocation-required checks, journal extent mapping/freeing, and `__gfs2_punch_hole()`.

## Control Flow
Only inline reservation calculation executes locally. It rejects directory inodes and accumulates indirect levels while data blocks exceed dinode direct pointers.

## State And Persistence
No header-local state. Declared functions mutate allocation, transaction, inode, journal, quota, and page-cache state.

## Dependencies And Integration Points
Includes iomap and inode headers and is consumed by aops, dir, file, inode, recovery, and journal code.

## Risks
Reservation underestimation can cause transaction exhaustion; overestimation reduces concurrency. Prototype drift risks subtle cross-file breakage.

## Test Signals
Compile all users, test reservation estimates for small/large writes and multiple block sizes, and exercise all exported mapping APIs through filesystem operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/bmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/dentry.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/dentry.c

## Purpose
Provides GFS2 dentry operations for cluster-coherent dentry revalidation, name hashing, and dentry deletion hints.

## Important APIs, Types, And Functions
`gfs2_drevalidate()` verifies that a dentry still matches its parent directory entry under the parent inode glock. `gfs2_dhash()` computes GFS2's on-disk CRC hash for dentry names. `gfs2_dentry_delete()` asks VFS to drop dentries whose iopen glock is being demoted. `gfs2_dops` registers these operations.

## Control Flow
Revalidation rejects RCU mode, rejects bad inodes, bypasses checks when no lock module mount operation exists, conditionally takes the parent shared glock, and calls `gfs2_dir_check()`. Positive dentries are valid on successful check; negative dentries are valid only when the name is still absent. Delete returns true only for positive dentries with initialized iopen glock marked for demotion.

## State And Persistence
No persistent writes. It observes directory entries and glock state and influences dcache retention. Name hash must match directory-entry hash persisted on disk.

## Dependencies And Integration Points
Depends on directory checking, glocks, lock module state, dcache operations, and GFS2 hash helpers. Used by inode/super operation setup for dentries.

## Risks
Skipping RCU revalidation is required because glock locking can sleep. Incorrect negative-dentry validation would hide newly created remote names. Hash mismatch with `dir.h` would break lookup consistency.

## Test Signals
Test positive and negative dentry revalidation after remote create/delete/rename, bad inode handling, lockless/nolock mount behavior, iopen demote deletion, and hash compatibility with directory entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/dentry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/dir.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/dir.c

## Purpose
Implements GFS2 directory storage and operations, including stuffed linear directories, extendible-hash directories, dirent scanning/validation, lookup, readdir cookies, insert/delete/rename updates, hash-table caching, leaf splitting/doubling, and exhash deallocation.

## Important APIs, Types, And Functions
Public functions include `gfs2_dir_search()`, `gfs2_dir_check()`, `gfs2_dir_add()`, `gfs2_dir_del()`, `gfs2_dir_read()`, `gfs2_dir_mvino()`, `gfs2_dir_exhash_dealloc()`, `gfs2_diradd_alloc_required()`, `gfs2_dir_get_new_buffer()`, and `gfs2_dir_hash_inval()`. Internal helpers handle directory data I/O (`gfs2_dir_write_data()`, `gfs2_dir_read_data()`), hash-table cache (`gfs2_dir_get_hash_table()`), dirent validation/scanning (`gfs2_dirent_scan()` and scan callbacks), leaf access (`get_leaf*()`), conversion (`dir_make_exhash()`), leaf split (`dir_split_leaf()`), hash doubling (`dir_double_exhash()`), new chained leaves (`dir_new_leaf()`), sorted cookie emission (`do_filldir_main()`), and leaf deallocation (`leaf_dealloc()`).

## Control Flow
Small directories are stuffed in the dinode after `struct gfs2_dinode`. When space runs out, `dir_make_exhash()` allocates an initial leaf, copies dirents, and replaces inline data with a hash table of leaf block pointers. Exhash lookups compute an index from the name hash, scan the first leaf and chained leaves, and validate every dirent. Adds first search saved free space from preflight, otherwise convert/split/double/add-chain until space exists. Reads gather dirents, compute stable cookies from hash or local leaf offsets, sort collision runs when needed, and emit through `dir_emit()`. Deletes merge record length into the previous dirent or sentinel the first entry, update leaf and directory entry counts, and adjust nlink for directories. Exhash deallocation walks hash table leaves, locks relevant rgrps, frees metadata, zeroes hash-table pointers, updates dinode, and can change mode to regular file on final dealloc to avoid double free after crash.

## State And Persistence
Persists directory entries, hash table pointers, leaf metadata (`lf_depth`, `lf_entries`, `lf_next`, timestamps, distance), inode `i_entries`, `i_depth`, `GFS2_DIF_EXHASH`, inode size, link counts, timestamps, inode block counts, resource-group metadata, quota/statfs effects, and the in-memory `i_hash_cache`.

## Dependencies And Integration Points
Depends on bmap extent allocation, unstuffing, metadata I/O, glocks, transactions, quotas, rgrps, CRC hashing, sort/vmalloc, and VFS `dir_context`. Used by lookup, create/link/unlink/rename, dentry revalidation, NFS export name lookup, and directory teardown.

## Risks
Dirent record-length validation is corruption-critical. Hash-table cache invalidation must happen whenever pointer tables change. Readdir cookies must be stable across hash collisions and large directories. Conversion, split, and doubling are multi-block metadata transactions where crash consistency depends on journal ordering. Exhash leaf deallocation must avoid freeing the same leaf twice when multiple hash slots point to it.

## Test Signals
Test stuffed lookup/read/add/delete, conversion to exhash, leaf split, hash-table doubling, chained leaves at max depth, hash collisions and seek cookies, `loccookie` on/off, rename `..` updates via `gfs2_dir_mvino()`, corrupt dirent lengths/counts, hash-cache invalidation, and exhash deallocation/recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/dir.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/dir.h

## Purpose
Declares GFS2 directory APIs, directory-add preflight state, hash helpers, and qstr-to-dirent initialization.

## Important APIs, Types, And Functions
`struct gfs2_diradd` carries allocation preflight results: number of blocks required, saved dirent, saved buffer, and whether to save location. Public declarations cover search, check, add, no-add cleanup, delete, read, move-inode update, exhash deallocation, allocation-required preflight, new directory buffer allocation, and hash-cache invalidation. `gfs2_disk_hash()` computes CRC32-based directory hashes. `gfs2_str2qstr()` fills qstr fields. `gfs2_qstr2dirent()` initializes an empty dirent with hash, record length, name length, type zero, and copied name. `gfs2_qdot` and `gfs2_qdotdot` are exported qstrs.

## Control Flow
Inline helpers compute hashes and initialize on-disk dirent fields. `gfs2_dir_no_add()` releases a preflight buffer when insertion is abandoned.

## State And Persistence
No header-owned state except exported qstr declarations. Inline dirent initialization sets on-disk fields before callers fill inode/type.

## Dependencies And Integration Points
Includes dcache and CRC32 APIs. Used by directory implementation, dentry hashing, export parent lookup, inode operations, and rename/link paths.

## Risks
Hash function must remain compatible with on-disk directory hashes. `gfs2_qstr2dirent()` leaves inode/type empty by design; callers must fill them before exposing the entry. Saved `gfs2_diradd` buffers must be released if not consumed.

## Test Signals
Compile all users, verify hash consistency with `dentry.c`, test abandoned add preflight cleanup, and inspect created dirents for correct hash/name/record fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/dir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/export.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/export.c

## Purpose
Implements GFS2 export operations for NFS/exportfs file handles, including encoding inode identities, resolving handles back to dentries, finding parents, and deriving a child's name within a parent directory.

## Important APIs, Types, And Functions
`gfs2_encode_fh()` writes small or large file handles containing child and optional parent formal inode numbers and block addresses. `get_name_filldir()` is a `dir_context` actor that finds a matching inode number during directory scan. `gfs2_get_name()` locks the parent directory and uses `gfs2_dir_read()` to discover the child name. `gfs2_get_parent()` looks up `..`. `gfs2_get_dentry()` resolves an inum via `gfs2_lookup_by_inum()` and wraps it with `d_obtain_alias()`. `gfs2_fh_to_dentry()` and `gfs2_fh_to_parent()` decode handle variants. `gfs2_export_ops` registers the callbacks.

## Control Flow
Encoding validates caller buffer length, writes child identity, and optionally appends parent identity unless the inode is the root. Decode accepts current small/large and old handle sizes, reconstructs big-endian 64-bit identifiers, rejects malformed short handles or zero formal inode numbers, and obtains aliases. Name lookup scans the parent directory under shared glock until a matching inode number is emitted.

## State And Persistence
File handles persist GFS2 inode identity externally for NFS clients. The file itself does not change disk state. Directory scanning observes current directory entries under glock protection.

## Dependencies And Integration Points
Depends on exportfs, GFS2 directory reading, lookup by inum, glocks, qdotdot, and inode identity fields. Used when GFS2 is exported over NFS or other exportfs consumers.

## Risks
Stale handles must return `ESTALE`/NULL behavior rather than aliasing wrong inodes. `gfs2_get_name()` matches only `no_addr` in the filldir callback even though it stores formal inode too; uniqueness assumptions rely on block address identity. Parent handles require larger buffers. Directory scan cost can be high for large directories.

## Test Signals
Test NFS export encode/decode for root and non-root, parent handle decode, stale/deleted inode handles, rename after handle creation, large directory get_name scans, and old handle size compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/export.c -->
