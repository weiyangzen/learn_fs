# Group Research: group_484_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_n_23760273d504

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is in subset A. All five listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_client.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_client.c

## Purpose

`nfs_client.c` contains shared illumos NFS client support used by the NFSv2 and NFSv3 client implementations. It is not a vnode-op table itself; it provides common cache validation, attribute caching, page-cache invalidation, async I/O queues, mount lifecycle cleanup, lock-manager cleanup, kstats, and direct delmap bookkeeping.

The file is central to client correctness because it coordinates rnode state, VM cache state, NFS attribute freshness, async writeback, cross-zone teardown, and lock-manager uncertainty.

## Main Interfaces

Important cache and attribute functions:

- `nfs_validate_caches`, `nfs3_validate_caches`
- `nfs_waitfor_purge_complete`
- `nfs_purge_caches`, `nfs_purge_rddir_cache`
- `nfs_attr_cache`, `nfs3_cache_wcc_data`
- `nfs_attrcache`, `nfs3_attrcache`, `nfs_attrcache_va`
- `nfs_cache_fattr`, `nfs3_cache_fattr3`
- `nfs_getattr_otw`, `nfs3_getattr_otw`
- `nfsgetattr`, `nfs3getattr`
- `nattr_to_vattr`, `fattr3_to_vattr`

Important async and VM helpers:

- `nfs_async_manager`, `nfs_async_manager_stop`
- `nfs_async_readahead`
- `nfs_async_putapage`
- `nfs_async_pageio`
- `nfs_async_readdir`
- `nfs_async_commit`
- `nfs_async_inactive`
- `nfs_async_stop`, `nfs_async_stop_sig`
- `writerp`
- `nfs_putpages`
- `nfs_invalidate_pages`

Mount/module, zone, and statistics helpers:

- `nfs_clntinit`, `nfs_clntfini`
- `nfs_mi_zonelist_add`, `nfs_mi_zonelist_remove`
- `nfs_free_mi`
- `nfs_mnt_kstat_init`
- `mnt_kstat_update`

Locking and mapping helpers:

- `nfs_lockrelease`
- `nfs_lockcompletion`
- `nfs_add_locking_id`
- `nfs_remove_locking_id`
- `nfs_init_delmapcall`
- `nfs_find_and_delete_delmapcall`
- `nfs_free_delmapcall`

## Cache And Attribute Model

Attribute caching is adaptive. `nfs_attrcache_va()` stores the returned `vattr_t`, computes an expiration time from how recently file data changed, and clamps that time by mount options such as `acregmin`, `acregmax`, `acdirmin`, and `acdirmax`. `MI_NOAC` and `VNOCACHE` force immediate expiration.

`nfs_attr_cache()` and `nfs3_attr_cache()` compare new server attributes against cached rnode state. If mtime, ctime, or size indicates a change, they purge page data, readlink cache, readdir cache, DNLC entries as needed, access cache, and cached ACL/security attributes.

Cache purge is serialized through `rp->r_serial` and `RINCACHEPURGE` so another thread cannot observe an updated file size and then read stale or zero-filled cached pages while invalidation is still in progress. `nfs_waitfor_purge_complete()` lets fast-path cache validation wait for that purge to complete.

`nfs3_cache_wcc_data()` uses NFSv3 weak cache consistency data. If before and after attributes are both available, it validates against the pre-operation values and then caches the after values. If post-operation attributes are missing, it expires the attribute cache.

## Attribute Conversion

`nattr_to_vattr()` converts NFSv2 wire attributes into illumos `vattr_t`, including NFS nobody uid/gid mapping, vnode type mapping, NFSv2 device-number expansion, FIFO compatibility handling, time conversion, and 32-bit time overflow checks.

`fattr3_to_vattr()` performs the NFSv3 equivalent, including large-file checks with `NFS3_SIZE_OK`, vnode type mapping, `makedevice()` for special files, block count calculation from `used`, and 32-bit time overflow checks.

Both conversion paths deliberately keep the remote file size in the temporary `vattr_t` for cache validation, while `nfsgetattr()` and `nfs3getattr()` finally return the client-side `rp->r_size` view to callers.

## Async I/O Model

The async subsystem is per mount. `nfs_async_manager()` owns worker creation and shutdown. Work is queued by operation type, and workers process queues round-robin with clustering counters so a run of write-like operations can be serviced together.

Supported async request types include readahead, putapage, pageio, readdir, commit, and inactive cleanup. The queue state is protected by `mi_async_lock`; rnode active I/O counters are tracked with `r_count` and `r_awcount`.

The manager thread exists partly for zone correctness. Global-zone pageout and fsflush can need to initiate work against an NFS mount in another zone, but cross-zone direct NFS calls are disallowed. The async manager and workers run in the mount’s zone and drain work before zone or unmount teardown.

Fallback behavior is conservative:

- If async allocation fails for readahead, it simply skips readahead.
- If async putpage/pageio cannot run from pageout or fsflush, dirty pages are re-marked rather than doing blocking network I/O in those contexts.
- If cross-zone synchronous page writeback would be required, pages are unlocked with error handling instead of issuing the call from the wrong zone.
- `nfs_async_commit()` re-marks pages as needing commit if commit cannot be safely sent from the current context.

## VM And Page Cache Behavior

`writerp()` moves user data into cached pages in page-sized chunks while holding the NFS write lock. It sets `RMODINPROGRESS` while the last-page contents and `r_size` are in flux, preventing pageout from writing an incorrectly sized EOF page. After `uiomove()` or `vpm_data_copy()`, it updates `r_size`, clears `RMODINPROGRESS`, and marks `RDIRTY`.

`nfs_putpages()` writes or invalidates dirty cached pages over a range or whole file. It forces invalidation when `ROUTOFSPACE` is set or the VFS is unmounted. It carefully clears and restores `RDIRTY` around full-file flushes so concurrent dirtying is not lost.

`nfs_invalidate_pages()` serializes truncation/invalidation with `RTRUNCATE`, records the truncation address, invalidates pages via `pvn_vplist_dirty()`, and wakes waiters afterward.

## Zone And Mount Lifecycle

The file uses a per-zone `mi_globals` list of NFS mounts. `nfs_mi_shutdown()` walks that list during zone shutdown, purges DNLC entries for each filesystem, disables async thread creation, wakes async workers, sets `MI_ASYNC_MGR_STOP`, and marks mounts `MI_DEAD`.

`nfs_mi_destroy()` defers freeing per-zone state if VFS cleanup has not yet removed all mounts. `nfs_mi_zonelist_remove()` completes that deferred cleanup after the last mount disappears.

`nfs_free_mi()` asserts async manager and workers are stopped, removes the mount from the zone list, releases lock-manager config, destroys locks and condition variables, destroys rnode lists, releases the zone reference, and frees `mntinfo_t`.

## Lock Manager Integration

`nfs_lockrelease()` is called when closing a vnode to release remote locks and share reservations held by the current process. It uses the local `r_lmpl` list to detect lock-manager uncertainty: if the client may be out of sync with the server, it issues an unlock for the whole file even if local lock state is not definitive.

`nfs_add_locking_id()` records uncertain lock or share ownership in the rnode. `nfs_remove_locking_id()` removes matching entries and optionally returns share-owner data for `F_UNSHARE`.

`nfs_lockcompletion()` updates `VNOCACHE` depending on whether the lock manager says cached mapping is safe. It also purges attributes after lock acquisition because open-time attributes may already be stale.

## Diagnostics And Kstats

`nfs_write_error()` rate-limits ENOSPC and EDQUOT console messages per mount and prints filehandle data using `nfs_printfhandle()`. It suppresses output during forced unmount or zone shutdown to avoid console flooding.

`nfs_mnt_kstat_init()` creates per-mount NFS I/O and `mntinfo` kstats. `mnt_kstat_update()` reports protocol, version, flags, security mode, transfer sizes, retransmission settings, attribute-cache timers, timeout estimator state, failover counters, remap counters, and current server hostname.

## Notable Invariants

- Attribute cache validation and data-cache invalidation are serialized through `r_statelock`, `r_serial`, and `RINCACHEPURGE`.
- `rp->r_mtime` is a client-side “last detected change” time, not a direct server timestamp comparison.
- `r_size` is the client’s authoritative local size view while dirty cached data exists.
- Async work queues are per mount and drained before unmount or zone teardown completes.
- Pageout/fsflush paths avoid blocking synchronous network writes when async dispatch is unavailable.
- Lock-manager uncertainty is stored per rnode and cleaned up on close.
- Cross-zone NFS operations are avoided or deferred through async mount-zone workers.

## Dependencies

This file depends on:

- NFS/rnode definitions from `nfs_clnt.h`, `rnode.h`, `nfs.h`, `nfs_acl.h`, and `lm.h`
- NFSv2 and NFSv3 RPC helpers such as `rfs2call`, `rfs3call`, `nfslookup`, `nfs3lookup`, `geterrno`, and `geterrno3`
- VM and segmap APIs: `pvn_*`, `page_*`, `segmap_*`, `vpm_data_copy`
- DNLC APIs and vnode page-cache helpers
- Zone APIs and kernel thread creation
- Kstat APIs
- Lock-manager APIs such as `lm4_frlock`, local lock registration, and share locking

## Research Notes

This file is a shared correctness layer under the version-specific NFS client code. The most important audit areas are cache purge serialization around file-size changes, async writeback fallback behavior, cross-zone inactive/writeback handling, `RMODINPROGRESS` races, delayed write error reporting, and lock-manager uncertainty cleanup.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_cmd.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_cmd.c

## Purpose

`nfs_cmd.c` implements kernel-side support for NFS daemon commands delivered through a per-zone door. In this file, the main consumer is export character-set mapping: the kernel asks userland, normally `mountd`, whether a specific exported path and client address require filename character-set conversion.

The file also caches positive and negative character-map lookup results in `exportinfo_t`, then applies `kiconv` conversions to individual names and directory entries.

## Main Interfaces

Door and lifecycle interfaces:

- `nfscmd_args`
- `nfscmd_init`
- `nfscmd_fini`
- `nfscmd_send`

Character-map interfaces:

- `nfscmd_findmap`
- `nfscmd_charmap`
- `nfscmd_insert_charmap`
- `nfscmd_convname`
- `nfscmd_convdirent`
- `nfscmd_convdirplus`
- `nfscmd_countents`
- `nfscmd_dropped_entrysize`

Per-zone state is held in `nfscmd_globals_t`, which contains a mutex and a `door_handle_t`.

## Door Handling

`nfscmd_args()` installs or replaces the per-zone door handle from a door id supplied through the NFS command interface. Existing handles are released with `door_ki_rele()`.

`nfscmd_send()` sends an `nfscmd_arg_t` to the door and reads an `nfscmd_res_t` response. It handles several failure modes:

- If no door has been registered, it retries for `NFSCMD_DR_TRYCNT` iterations before returning `NFSCMD_ERR_DROP`.
- `EAGAIN` sleeps and retries.
- `EINTR` checks whether the door was revoked. If revoked, it clears the cached handle and retries so SMF can restart the daemon and register a new door.
- Stale handles or unexpected errors get one final retry before returning `NFSCMD_ERR_FAIL`.

The function holds a reference on the door while issuing the upcall so concurrent replacement cannot free the handle prematurely.

## Character-Set Cache

`nfscmd_findmap()` first checks whether the export has `EX_CHARMAP`. If not, it is a no-op. If charset mapping is enabled, it searches `exi->exi_charset` for a cached client-address entry.

On cache miss, `nfscmd_charmap()` asks userland for a mapping using `NFSCMD_CHARMAP_LOOKUP`, passing the export path and client address. It then inserts either:

- A positive mapping with `inbound = kiconv_open("UTF-8", name)` and `outbound = kiconv_open(name, "UTF-8")`
- A negative cache entry with null converters when lookup fails

This means both “mapping exists” and “mapping does not exist” are cached per export/client pair.

## Name Conversion

`nfscmd_convname()` converts a single name buffer. If `inbound` is true, it converts from the client code set into UTF-8. Otherwise it converts from UTF-8 to the client code set. If no mapping exists, or the relevant converter is unavailable, it returns the original name pointer. If conversion fails, it frees the temporary buffer and returns `NULL`.

`nfscmd_convdirent()` handles a single `dirent64` record. It copies the fixed part of the dirent, converts the name with the outbound converter, recomputes `d_reclen`, and returns either the converted buffer, the original buffer, or `NULL`. If conversion fails due to `E2BIG`, it can report `NFS3ERR_NAMETOOLONG`.

`nfscmd_convdirplus()` converts a sequence of directory entries into a new buffer bounded by `maxsize`. Entries that fail with `EILSEQ` are skipped. The return value is the number of entries represented after conversion and skipped-entry accounting, while `*ndata` points at the new buffer.

## Directory Helpers

`nfscmd_countents()` walks a `dirent64` buffer using `d_reclen` and counts entries.

`nfscmd_dropped_entrysize()` computes how many bytes would be removed from the tail of a directory-entry buffer if a given number of entries were dropped. This supports fitting converted directory data into protocol response limits.

## Notable Invariants

- Door handles are per-zone.
- Character-map cache entries are per export and client address.
- Negative character-map results are cached to avoid repeated userland upcalls.
- Returned converted names may be newly allocated or may be the original pointer, so callers must understand ownership.
- Directory conversion must preserve `dirent64` layout and recompute record lengths after name conversion.

## Dependencies

This file depends on:

- Door kernel interfaces: `door_ki_lookup`, `door_ki_hold`, `door_ki_rele`, `door_ki_upcall`, `door_ki_info`
- Export structures from `nfs/export.h`
- NFS command definitions from `nfs/nfs_cmd.h`
- Kernel iconv APIs: `kiconv_open`, `kiconv`
- `dirent64` layout and NFSv3 status definitions

## Research Notes

The main correctness concerns are retry behavior around revoked doors, lifetime/ownership of converted name buffers, bounds handling in directory conversion, and the use of cached negative charset mappings. This file participates in NFS server/export behavior rather than the NFS client vnode path.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_common.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_common.c

## Purpose

`nfs_common.c` is the loadable-module wrapper and common client support file for illumos NFS. It registers the NFS syscall, NFS dynamic root filesystem, NFSv2 client filesystem, NFSv3 client filesystem, and NFSv4 filesystem linkage. It also provides root-mount fallback logic, transfer-size helpers, mount option updates, and the direct-I/O toggle.

## Main Interfaces

Module entry points:

- `_init`
- `_fini`
- `_info`

Dynamic root filesystem:

- `nfsdyninit`
- `nfsdyn_mountroot`

Common sizing and option helpers:

- `nfstsize`
- `nfs3tsize`
- `nfs3_tsize`
- `rfs3_tsize`
- `nfs_setopts`
- `nfs_directio`

The file defines module linkage for:

- `nfssys`
- `nfsdyn`
- `nfs`
- `nfs3`
- externally supplied `modlfs4`

## Module Initialization

`_init()` calls `nfs_clntinit()` first. That initializes common NFS client state, VFS state, NFSv4 client state, and NFS command-door state. It then creates `nfsstat_zone_key` and installs all module linkages.

If installation fails, `_init()` deletes the stats zone key, calls `nfs_clntfini()`, and explicitly runs cleanup for NFSv4, NFSv3, and NFSv2 filesystem registration work that may have been performed indirectly by `mod_install()`.

`_fini()` always returns `EBUSY`, preventing unload.

## Dynamic NFS Root Mount

The pseudo filesystem `nfsdyn` exists only for diskless boot root mounting. `nfsdyn_mountroot()` tries to mount the root filesystem as NFSv4 first, then falls back to NFSv3, then NFSv2 if the previous attempt fails with `EPROTONOSUPPORT`.

For each attempt it:

1. Sets the VFS operations to the candidate NFS version.
2. Fills `struct nfs_args` with server address, filehandle storage, netconfig storage, and hostname storage.
3. Calls `mount_root()` with the requested version.
4. On non-version-mismatch failure, restores `nfsdyn_vfsops`, frees temporary state, and returns the error.
5. On success, frees temporary state and calls the real `VFS_MOUNTROOT()` through the selected filesystem operations.

`ROOT_REMOUNT` is treated as a panic condition; `ROOT_UNMOUNT` is a no-op.

## Transfer Size Helpers

`nfstsize()` returns `NFS_MAXDATA` for NFSv2.

`nfs3tsize()` returns a global maximum NFSv3 transfer size, defaulting to 1 MiB.

`nfs3_tsize()` chooses an NFSv3 client transfer size by transport semantics:

- connection-oriented transports: 1 MiB
- RDMA: 1 MiB
- connectionless transports: 32 KiB

`rfs3_tsize()` performs the equivalent server-side calculation from `svc_req` transport type.

## Mount Option Updates

`nfs_setopts()` updates a live mount’s `mntinfo_t` from `struct nfs_args`. It handles flags and parameters including:

- `NFSMNT_NOAC`
- `NFSMNT_NOCTO`
- `NFSMNT_LLOCK`
- `NFSMNT_GRPID`
- `NFSMNT_RETRANS`
- `NFSMNT_TIMEO`
- `NFSMNT_RSIZE`
- `NFSMNT_WSIZE`
- attribute cache min/max values
- `NFSMNT_LOOPBACK`

Invalid negative retrans values, nonpositive timeouts, and nonpositive read/write sizes return `EINVAL`. Attribute-cache values are clamped to configured maximums and converted from seconds to high-resolution time units.

When `NOAC` is enabled, the root vnode attribute cache is purged.

## Direct I/O

`nfs_directio()` toggles per-rnode direct I/O through `RDIRECTIO`.

When enabling direct I/O, it takes the vnode write lock to avoid racing an active cached write. If dirty cached data or async writes exist, it flushes and invalidates the page cache with `VOP_PUTPAGE(B_INVAL)`. ENOSPC and EDQUOT errors are stored in `rp->r_error` if no previous async write error is recorded.

Disabling direct I/O simply clears `RDIRECTIO`.

## Notable Invariants

- The NFS module is not unloadable after initialization.
- `nfsdyn` is only a bootstrap shim; successful root mounting replaces the VFS ops with the real NFS version.
- NFSv4 root is attempted before NFSv3 and NFSv2, but fallback only happens for protocol-version unsupported cases.
- Direct I/O enablement must flush dirty cached pages while holding the vnode write lock.
- Runtime mount option updates clamp attribute-cache timers and transfer sizes rather than blindly replacing limits.

## Dependencies

This file depends on:

- NFS client initialization/finalization from `nfs_client.c`
- NFSv2, NFSv3, and NFSv4 VFS init/fini and VFS ops
- Boot-time `mount_root()` support from `nfs_dlinet.c`
- VFS module registration APIs
- NFS mount argument definitions
- Rnode and mntinfo state from `nfs_clnt.h` and `rnode.h`

## Research Notes

This file is mostly module and mount plumbing, but `nfsdyn_mountroot()` is important for diskless boot behavior and `nfs_directio()` is important for cache correctness. The highest-risk logic is cleanup after partial module installation failure and the transition from cached I/O to direct I/O while writes may be dirty or outstanding.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_dlinet.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_dlinet.c

## Purpose

`nfs_dlinet.c` implements diskless boot networking and NFS root mounting support. It configures the boot network interface, discovers the client identity and root server through boot properties, DHCP, RARP, and bootparams, obtains NFS filehandles through the mount protocol, chooses UDP or TCP, and builds NFS mount arguments for root.

This file is built as a miscellaneous module named “Boot diskless” and exports the `mount_root()` entry used by `nfs_common.c`’s dynamic root mount path.

## Main Interfaces

Module entry points:

- `_init`
- `_fini`
- `_info`

Root mount and server discovery:

- `mount_root`
- `getfile`
- `mountnfs`
- `mountnfs3`
- `ping_prog`
- `init_mountopts`

Network/bootstrap configuration:

- `init_config`
- `bp_netconfig`
- `dhcpinit`
- `cacheinit`
- `cacheinfo`
- `whoami`
- `revarp_myaddr`
- `revarp_start`
- `revarpinput`
- `dlifconfig`
- `ifioctl`
- `rtioctl`
- `setifflags`

RPC/XDR helpers:

- `pmap_kgetport`
- `pmap_rmt_call`
- `mycallrpc`
- `myxdr_fhstatus`
- `myxdr_fhandle`
- `myxdr_mountres3`
- `myxdr_mountres3_ok`
- `myxdr_fhandle3`
- `myxdr_rmtcall_args`
- `myxdr_rmtcallres`
- `myxdr_pmap`

Utility helpers:

- `init_netbuf`
- `free_netbuf`
- local `inet_ntoa`, `inet_aton`, `isdigit`, `atoi`

## Root Mount Flow

`mount_root()` is called with a logical name such as `root`, a path buffer, an NFS protocol version, NFS mount arguments, and VFS flags.

The flow is:

1. Initialize boot network configuration once with `init_config()`.
2. Allocate a server address netbuf.
3. Repeatedly call `getfile()` until it does not return `ETIMEDOUT`.
4. Depending on requested NFS version:
   - NFSv2: call `mountnfs()` through mount protocol v1.
   - NFSv3: call `mountnfs3()` through mount protocol v3.
   - NFSv4: ping NFS program version 4 over TCP and use the standard NFS port.
5. Reject NFSv4 root when `nfs4_no_diskless_root_support` is set.
6. Choose TCP or UDP `knetconfig`.
7. Parse root mount options with `init_mountopts()`.
8. Copy the selected netconfig into caller-provided `args->knconf`.

The file prefers TCP when a server responds to NFS NULLPROC over TCP, otherwise it uses UDP.

## Boot Configuration Sources

`init_config()` extracts the boot network device path, interface name, and physical point of attachment from `rootfs`. It sets clone-device `rdev` values for UDP and TCP, then tries three configuration sources in order:

1. `bp_netconfig()` from boot properties
2. `dhcpinit()` from an OBP-provided DHCP ACK packet
3. `whoami()` through RARP and bootparamd

If all fail, it warns that the interface did not respond.

`bp_netconfig()` uses boot properties such as host IP, subnet mask, router IP, server path, server name, root options, and server IP. If enough data is present, it configures the interface and adds a default route.

`dhcpinit()` parses the cached DHCP ACK packet, sets hostname and NIS domain when provided, configures netmask and broadcast, brings up the interface with `IFF_DHCPRUNNING`, and adds router routes.

`cacheinit()` extracts NFS root server path/name/IP and root options from boot properties and DHCP vendor options. It understands root path forms such as `nfs://server/path`, `server:/path`, and `/path`.

`whoami()` uses RARP to discover the client IP address, broadcasts a bootparams WHOAMI request, sets hostname/domain name, records the bootparam server address, and adds a router if bootparamd provides one.

## RARP And Interface Setup

`revarp_myaddr()` opens the boot network device through LDI, attaches and binds DLPI to `ETHERTYPE_REVARP`, obtains the Ethernet address, sends RARP requests, and sets the resulting IP address on the network interface.

`revarp_start()` formats a DLPI unitdata request containing an Ethernet RARP packet and sends it. It loops until `revarpinput()` fills the client IP address.

`revarpinput()` waits with a timeout for DLPI messages, validates message structure, accepts only IP RARP replies for the local Ethernet address, and copies the target protocol address into the caller’s netbuf.

`dlifconfig()` sets address, broadcast address, netmask, and interface flags using kernel stream ioctls.

## NFS Mount Protocol

`mountnfs()` discovers the mount daemon port for mount protocol v1 through `pmap_kgetport()`, sends `MOUNTPROC_MNT`, receives a v2 filehandle, then sets the server port to `NFS_PORT`. It defaults to UDP but switches to TCP if `ping_prog()` succeeds for NFSv2 over TCP.

`mountnfs3()` does the same for mount protocol v3. It handles `RPC_PROGVERSMISMATCH` as `EPROTONOSUPPORT`, decodes the variable-length v3 filehandle, frees XDR-allocated mount result state, and switches to TCP if NFSv3 NULLPROC succeeds over TCP.

NFSv4 does not use the mount protocol here; it simply verifies that NFS program version 4 responds over TCP and uses `NFS_PORT`.

## Portmapper And RPC Helpers

`pmap_kgetport()` first queries the old portmapper `PMAPPROC_GETPORT`. If portmapper is unavailable, it falls back to rpcbind `RPCBPROC_GETADDR` and converts the universal address to a port.

`pmap_rmt_call()` supports broadcast-style remote calls. It first tries portmapper `PMAPPROC_CALLIT`, then rpcbind remote call if portmapper is unavailable. It updates response address and port on success.

`mycallrpc()` creates a kernel TLI RPC client, performs one RPC call with a given timeout/retry count, destroys the auth handle and client, and returns the RPC status.

The local XDR routines are minimal copies needed for early boot because the full generated mount XDR code is not directly used here.

## Root Mount Options

`init_mountopts()` starts with defaults:

- `NFSMNT_NOCTO`
- `NFSMNT_LLOCK`
- `NFSMNT_INT`
- attribute-cache min/max defaults

It optionally obtains `rootopts` through `getfile("rootopts")`, then parses an option list mirroring the userland NFS mount command.

Handled options include readonly/readwrite, soft/hard/semisoft, grpid, intr/nointr, noac, nocto, rsize, wsize, timeo, retrans, actimeo, acreg/acdir min/max, llock, version, proto, noprint, and forcedirectio.

Some options are ignored because they are defaults or not meaningful during root boot. Unsafe root options such as nosuid, nodevices, nosetuid, noexec, and remount produce warnings. Security options are ignored because root is mounted with AUTH_UNIX in this path.

Read size is bounded: if unspecified, NFSv4 defaults to 32 KiB and older NFS defaults to 8 KiB. Values below 512 are raised, and UDP values above 56 KiB are trimmed.

## Notable Invariants

- Diskless boot uses IPv4-only assumptions throughout this file.
- The root network interface must be configured before server discovery and mount protocol calls.
- NFSv4 diskless root is deliberately disabled by `nfs4_no_diskless_root_support`.
- TCP is preferred when available, but UDP remains the fallback.
- Boot property and DHCP cached data can bypass bootparam RPC discovery.
- Root mount option parsing is single-threaded and stores root options in static buffers.
- Portmapper fallback to rpcbind is built into both port lookup and remote-call paths.

## Dependencies

This file depends on:

- Kernel TLI and RPC client APIs
- DLPI/LDI for direct network-device RARP during boot
- Boot properties and DHCP option parsing
- NFS mount argument structures and NFS protocol constants
- Portmapper/rpcbind protocol definitions
- Kernel stream ioctls for interface and route configuration
- `nfs_common.c` dynamic root flow, which calls `mount_root()`

## Research Notes

This file is early-boot infrastructure rather than ordinary runtime NFS client code. The audit hotspots are static global boot state, string and option parsing, IPv4-only assumptions, XDR allocation/freeing for mount v3 results, netbuf lifetime, route/interface ioctl error handling, and the protocol fallback rules that determine whether diskless boot proceeds or falls back to another NFS version.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_dlinet.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_dump.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_dump.c

## Purpose

`nfs_dump.c` implements panic-time crash dump writes to an NFS swap/dump file. It sends NFS WRITE RPCs directly over a connectionless transport with minimal dependencies because normal kernel services, context switching, and timeout behavior are constrained after a panic.

It supports NFSv2 and NFSv3 dump targets.

## Main Interfaces

Primary entry point:

- `nfs_dump`

Internal helpers:

- `nd_init`
- `nd_send_data`
- `nd_get_reply`
- `nd_poll`
- `nd_auth_marshall`
- `nd_log`

Static dump state includes:

- `nfsdump_cf`
- `nfsdump_addr`
- `nfsdump_fhandle2`
- `nfsdump_fhandle3`
- `nfsdump_maxcount`
- `nfsdump_version`

## Dump Flow

`nfs_dump()` initializes the transport state through `nd_init()`, then writes one page at a time. For each page, it sends an NFS WRITE request with `nd_send_data()`, polls for a reply with `nd_poll()`, and decodes/validates replies with `nd_get_reply()`.

Retries are controlled by `RETRIES` and a timeout that grows with the retry count. Bad or unrelated messages are ignored and polling continues until the matching reply arrives or retry limits are exceeded.

## Initialization

`nd_init()` lazily fills static dump state from the dump vnode if not already initialized:

- NFS protocol version from `mi_vers`
- v2 or v3 filehandle from the vnode
- maximum dump file size from `dumpvp_size`
- server netbuf and netconfig from current server info

If the original transport is not connectionless, `nd_init()` attempts to convert INET/INET6 TCP-style config to UDP/UDP6 by constructing a clone device. Non-INET non-connectionless transports fail with `EIO`.

It then opens the transport with `t_kopen()` and binds a reserved port for INET/INET6, or performs a generic `t_kbind()` otherwise.

## WRITE RPC Encoding

`nd_send_data()` creates an RPC call header, allocates a one-page dump buffer, and attaches two mblks:

- a fixed header buffer containing the XDR-encoded RPC/NFS WRITE arguments
- a continuation mblk containing the page data copied from the dump source address

For NFSv2 it encodes `RFS_WRITE`, the filehandle, begin offset, offset, length, and byte-array length.

For NFSv3 it encodes `NFSPROC3_WRITE`, the NFSv3 filehandle, 64-bit offset, count, `FILE_SYNC` stable mode, and byte-array length.

It refuses to extend the dump file beyond `nfsdump_maxcount` and trims the final write if it would cross the file size.

## Reply Handling

`nd_get_reply()` receives UDP data with `t_krcvudata()`, tolerates `EBADMSG` as a bad message, validates that the message type is `T_DATA`, initializes XDR over the received mblk, and decodes the RPC reply.

The accepted-reply result decoder depends on NFS version:

- NFSv2 uses `xdr_attrstat`
- NFSv3 uses `xdr_WRITE3res`

The function checks the reply XID against the call XID, converts RPC-level errors with `_seterr_reply()`, and verifies the NFS status is success. It frees any auth verifier returned by the server and frees the received mblk after successful decode.

## Polling

`nd_poll()` uses `t_kspoll()` in a loop until data is available or the timeout expires. It briefly lowers interrupt priority with `spl0()`/`splx()` before checking the transport because the network transports do not support true polled I/O here. It calls `runqueues()` inside the wait loop.

If the maximum retry count is reached without an event, it reports that the server is not responding and returns `EIO`.

## Authentication

`nd_auth_marshall()` writes AUTH_UNIX credentials directly into the XDR stream using `XDR_INLINE()`. It uses:

- current high-resolution time seconds
- `utsname.nodename`
- uid 0
- gid 0
- empty group list
- AUTH_NULL verifier

This is a minimal panic-time credential path, not the normal RPC auth stack.

## Notable Invariants

- Dump writes are page-sized except for trimming at dump file EOF.
- NFSv3 writes are sent as `FILE_SYNC`.
- The dump code does not extend a swap-backed dump file.
- Only NFSv2 and NFSv3 are supported.
- The code tries to force dumping over UDP-style connectionless transport.
- Reply XIDs must match the sent call XID; unrelated replies are ignored.
- The path is designed for panic context and avoids normal blocking abstractions where possible.

## Dependencies

This file depends on:

- NFS filehandle and mntinfo/rnode structures
- Kernel TLI APIs: `t_kopen`, `t_kbind`, `t_ksndudata`, `t_krcvudata`, `t_kspoll`
- RPC/XDR routines: `xdr_callhdr`, `xdr_replymsg`, `xdr_fhandle`, `xdr_nfs_fh3`, `xdr_WRITE3res`
- STREAMS mblk APIs
- Dump globals such as `dumpvp_size`
- Network config and address state from the NFS mount

## Research Notes

The key risk areas are panic-context allocation failures, mblk lifetime on send or encode errors, transport conversion to UDP/UDP6, retry behavior around bad or unrelated replies, and correctness of file-size trimming. This code is intentionally narrow and bypasses most normal NFS client machinery.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_dump.c -->