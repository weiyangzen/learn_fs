# subset-b-007787 research

Grouped research report for the requested OpenAFS source subset. Each source file section is wrapped with reconciliation markers so the per-file documents can be derived without changing the source tree shape.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_dir.c -->
## sources/distributed-fs/openafs/src/libafscp/afscp_dir.c

Purpose: Implements directory reading, lookup, path resolution, symlink handling, and AFS mountpoint traversal for `libafscp`. It converts raw AFS directory files into `afscp_dirent` iteration results and maps path strings to `afscp_venusfid` objects.

Important APIs and functions: `afscp_SetDirMode` selects root interpretation between `DIRMODE_CELL` and `DIRMODE_DYNROOT`. `afscp_OpenDir`, `afscp_ReadDir`, `afscp_RewindDir`, and `afscp_CloseDir` expose a small directory stream API. `afscp_DirLookup` and `afscp_ResolveName` look up names inside a directory. `afscp_ResolvePath` and `afscp_ResolvePathFromVol` perform full path resolution. Internal helpers include `_DirUpdate`, `dir_get_entry`, `namehash`, `gettoproot`, `getvolumeroot`, `fidstack_*`, `_ResolvePath`, and `afscp_HandleLink`.

Control flow: `afscp_OpenDir` validates status with `afscp_GetStatus`, allocates a stream, and calls `_DirUpdate`. `_DirUpdate` checks the current data version, consults `volume->dircache` via `tfind`, fetches the directory file with `afscp_PRead` when stale, and stores the buffer in `tsearch`. `afscp_ReadDir` walks the on-disk hash table and chained `DirEntry` records. Path resolution splits path components in place, uses a FID stack for `..`, follows normal symlinks through recursive `_ResolvePath`, and treats non-executable AFS symlinks as volume mountpoints.

State and persistence: State is process-local. Directory buffers are cached in each `afscp_volume` tree and keyed by vnode/unique plus data version. `dirmode` is a process-global setting. The code does not persist anything beyond network-side reads.

Dependencies and integration: Depends on AFS directory layout from `<afs/dir.h>`, volume lookup from `afscp_volume.c`, FID allocation from `afscp_fid.c`, network reads from `afscp_file.c`, and status caching from `afscp_fid.c`. Root traversal depends on VLDB volume names such as `root.afs` and `root.cell`.

Risks: `_DirUpdate` stores the stream's `dirbuffer` pointer directly in the cache, while `afscp_CloseDir` only frees the stream, so ownership is intentionally cache-oriented but easy to misuse. `fidstack_push` silently drops entries on realloc failure, which can break `..` traversal without setting `afscp_errno`. Symlink recursion is capped at 5 per component but recursive path calls can still be complex. Directory parsing trusts on-disk structures after limited bounds checks.

Test signals: Exercise cached and uncached directory reads, stale data version refresh, dynamic-root absolute paths, mountpoints `%` and `#` style, normal symlink terminal and non-terminal behavior, `.` and `..`, ELOOP, ENOTDIR, ENODEV, ENOENT, and large directory rejection with `EFBIG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_dirops.c -->
## sources/distributed-fs/openafs/src/libafscp/afscp_dirops.c

Purpose: Provides write-side directory and file-system operation wrappers for `libafscp`, mapping create, mkdir, symlink, lock, remove-file, and remove-dir operations onto RXAFS file server RPCs.

Important APIs and functions: Public functions are `afscp_CreateFile`, `afscp_MakeDir`, `afscp_Symlink`, `afscp_Lock`, `afscp_RemoveFile`, and `afscp_RemoveDir`. They accept directory or object FIDs, names or targets, and AFS store status structures, then return status through `afscp_errno` and optional new FID output parameters.

Control flow: Each operation resolves the containing volume with `afscp_VolumeById`, iterates volume server indexes, resolves each `afscp_server`, iterates that server's RX connections, and invokes the matching `RXAFS_*` RPC. Successful create and mkdir calls update parent stat cache via `_StatStuff`, add callbacks for new objects with `afscp_AddCallBack`, and optionally allocate a new `afscp_venusfid`. Remove operations invalidate or refresh parent status depending on the RPC result. `afscp_Lock` chooses `RXAFS_ReleaseLock` for `LockRelease` and `RXAFS_SetLock` for read, write, or extend locks.

State and persistence: No local durable state. The file-server RPCs mutate AFS namespace state. Local state changes are cache updates for statuses and callbacks, plus global `afscp_errno`.

Dependencies and integration: Integrates with volume/server lookup and RX connection creation from `afscp_volume.c` and `afscp_server.c`, callback bookkeeping from callback code outside this subset, and status cache routines from `afscp_fid.c`.

Risks: The retry loops treat any nonnegative RPC code as a loop break but later require `code == 0`, so unusual positive server results stop failover. `afscp_MakeDir` and `afscp_Symlink` do not explicitly validate null arguments like `afscp_CreateFile` does. On create/mkdir, `server` is used for callbacks after loops and assumes it still identifies the successful endpoint. Write operations depend on the caller choosing a writable volume.

Test signals: Mock or integration tests should verify server failover, null argument handling, parent stat refresh and invalidation, callback addition after create/mkdir, lock error mapping from AFS EAGAIN variants to `EWOULDBLOCK`, and read-only or missing-volume failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_dirops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_fid.c -->
## sources/distributed-fs/openafs/src/libafscp/afscp_fid.c

Purpose: Owns FID allocation helpers and status cache behavior for `libafscp`. It converts `AFSFetchStatus` into POSIX `stat`, stores and invalidates cached fetch status entries, and exposes callback waiting helpers.

Important APIs and functions: `afscp_MakeFid`, `afscp_DupFid`, `afscp_FreeFid`, `afscp_WaitForCallback`, `afscp_GetStatus`, `afscp_Stat`, `afscp_CheckCallBack`, `_StatInvalidate`, `_StatStuff`, and `afscp_StoreStatus`.

Control flow: FID constructors allocate shallow structures that point at existing `afscp_cell` objects. `afscp_GetStatus` first searches `volume->statcache`; if present, it copies cached status, wakes waiters, and returns. On a miss, it walks volume servers and connections, calls `RXAFS_FetchStatus`, then records the returned callback and status. `_StatStuff` inserts a newly allocated `afscp_statent` in the tree. `_StatInvalidate` removes an entry and either frees it immediately or marks it for cleanup after waiters leave. `afscp_WaitForCallback` waits on the cached entry's condition variable until invalidation or timeout.

State and persistence: Maintains per-volume process-local stat caches keyed by vnode and unique. Cache entries contain mutexes, condition variables, waiter counts, cleanup flags, and copied AFS status. No disk persistence.

Dependencies and integration: Uses `tsearch` trees, pthread synchronization, RXAFS file server calls, volume/server lookup, and callback tracking from `afscp_callback.c`. POSIX `stat` conversion integrates with consumers expecting local metadata semantics.

Risks: `_StatStuff` calls `tsearch` and unconditionally overwrites the slot with a new allocation when `cached != NULL`; if an entry already existed, the old object can be orphaned. Comparator keys ignore volume and cell, relying on per-volume trees. `afscp_CheckCallBack` computes an unsigned-ish remaining expiration value that can underflow if expired. Thread-safety is partial: tree operations themselves are not globally locked.

Test signals: Cover cache hit and miss, callback invalidation with and without waiters, timed waits, `stat` mode mapping for files/directories/symlinks, store-status cache refresh, concurrent lookup and invalidation, and missing volume failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_fid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_file.c -->
## sources/distributed-fs/openafs/src/libafscp/afscp_file.c

Purpose: Implements positional read and write operations against AFS file server data RPCs for `libafscp`.

Important APIs and functions: `afscp_PRead` fetches a byte range using `StartRXAFS_FetchData`, RX stream reads, `EndRXAFS_FetchData`, and callback registration. `afscp_PWrite` stores a byte range using `RXAFS_FetchStatus` for current length, `StartRXAFS_StoreData`, RX stream writes, and `EndRXAFS_StoreData`.

Control flow: Both functions resolve the volume from the FID, walk all candidate servers and addresses, create or use an RX call, and return after the first successful transfer. Reads first receive the file-server encoded byte count, then drain the stream into the caller buffer and add a callback if the fetch completes. Writes reject non-RWVOL volumes, fetch current status to calculate final file size, set client modification time, stream the caller buffer, and end the store RPC.

State and persistence: Persistent data changes occur only through successful store RPCs. Local state is temporary RX call state, callback/stat side effects, and `afscp_errno`.

Dependencies and integration: Uses volume/server lookup, RX call streaming, generated AFS RPC stubs, and callback registration. Directory code depends on `afscp_PRead` to read directory files and symlink contents.

Risks: The file notes both paths are not 64-bit clean; `count`, `offset`, stream byte counts, and `int bytesremaining` can truncate large transfers. `rx_Read` and `rx_Write` request all remaining bytes at once, which may be too large after truncation. Writes fetch status but do not add a callback from that status, and do not call `_StatStuff` after successful store. Positive nonzero RPC return handling follows the same failover caveat as other wrappers.

Test signals: Validate short reads, exact reads, large transfer boundaries, partial RX read/write handling, read from replicated volumes, write rejection on RO/BACK volumes, final length calculation for extending writes, and callback/status cache side effects after successful fetch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_init.c -->
## sources/distributed-fs/openafs/src/libafscp/afscp_init.c

Purpose: Initializes and finalizes the RX runtime and callback service required by `libafscp`.

Important APIs and functions: `afscp_Init` starts RX with `rx_Init(0)`, starts a callback server through `start_cb_server`, and optionally sets the default cell. `afscp_Finalize` returns callbacks, frees cell and server registries, finalizes RX, and closes the callback service socket. `start_cb_server` creates a null server security object and an RX service using `RXAFSCB_ExecuteRequest`.

Control flow: Initialization is guarded by a static `init` state. Calls after successful initialization return immediately. `start_cb_server` registers service id 1 named `afs` and invokes `rx_StartServer(0)`. Finalization does not reset `init`, so it is effectively a terminal cleanup path rather than a restartable lifecycle.

State and persistence: Maintains static RX security class and service pointers, plus `init`. It also triggers cleanup of global callback, cell, and server process state. No durable persistence.

Dependencies and integration: Depends on RX, rxnull, callback server dispatch from `afscp_internal.h`, and the server/cell/callback modules. Must be called before network operations that expect RX connections and callback handling.

Risks: `afscp_Finalize` dereferences `serv` after `rx_Finalize`; if callback server startup partially failed, finalization assumptions may not hold. The `init` flag is not cleared, preventing clean reinitialization in the same process. `rx_StartServer(0)` behavior is global and may interact with embedding applications already using RX.

Test signals: Check idempotent double initialization, initialization with explicit and default cells, callback server creation failure, finalize after partial init, and repeated init/finalize expectations for embedded users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_internal.h -->
## sources/distributed-fs/openafs/src/libafscp/afscp_internal.h

Purpose: Declares private cross-file interfaces for `libafscp` and provides optional debug logging.

Important APIs and types: Declares `RXAFSCB_ExecuteRequest`, `_GetSecurityObject`, `_GetVLservers`, `_StatInvalidate`, and `_StatStuff`. Defines `afs_dprintf(x)` as either empty or `printf x` depending on `AFSCP_DEBUG`.

Control flow: This header has no runtime control flow. It centralizes private prototypes needed by initialization, security, VLDB setup, and status cache maintenance across compilation units.

State and persistence: No state. It exposes functions that mutate cell security/VLDB state and stat caches.

Dependencies and integration: Includes AFS parameter, interface, and cell configuration headers. It resolves a header conflict by declaring the callback request executor instead of including the conflicting callback interface header.

Risks: Private prototypes are not type namespaced beyond leading underscores, and `_GetSecurityObject`/`_GetVLservers` depend on callers passing initialized `afscp_cell` structures. The `afs_dprintf` macro evaluates its argument only in debug builds, so debug-only expressions must not have side effects.

Test signals: Build coverage with and without `AFSCP_DEBUG`, Kerberos-enabled and Kerberos-disabled builds, and compilation units that include both AFS client and callback interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_server.c -->
## sources/distributed-fs/openafs/src/libafscp/afscp_server.c

Purpose: Manages process-global cells and file servers for `libafscp`, including default cell/realm selection, VLDB address resolution, RX connection creation, and server lookup by UUID, address, or index.

Important APIs and functions: `afscp_FreeAllCells`, `afscp_FreeAllServers`, `afscp_CellById`, `afscp_CellByName`, `afscp_DefaultCell`, `afscp_SetDefaultRealm`, `afscp_SetDefaultCell`, `afscp_CellId`, `afscp_ServerById`, `afscp_ServerByAddr`, `afscp_AnyServerByAddr`, `afscp_ServerByIndex`, and `afscp_ServerConnection`.

Control flow: `afscp_CellByName` searches existing cells, grows the cell array, initializes security through `_GetSecurityObject`, initializes VLDB clients through `_GetVLservers`, then assigns the cell id. Default cell resolution reads local client configuration unless `defcell` is set. Server lookup grows per-cell and global server arrays, asks the VLDB for UUID or address mappings with `ubik_VL_GetAddrsU`, and creates one RX connection per returned address.

State and persistence: Uses global arrays `allcells` and `allservers`, global default cell/realm strings, and global `afscp_errno`. Cells own VLDB clients, security classes, server pointer arrays, and volume trees. Servers own RX connections. No on-disk persistence.

Dependencies and integration: Uses OpenAFS config directory APIs, ubik VLDB RPCs, RX connections, Kerberos realm routines for default realm, and volume lookup code that stores server indexes.

Risks: Free routines release arrays but not all nested allocations and connections. Error paths in `afscp_ServerById` can leave partially attached server entries in `fsservers`. `afscp_FreeAllServers` only frees the pointer array, not server objects or RX connections. There is no locking around global registries. Address byte order assumptions are subtle: public address lookup takes host order and stores network order.

Test signals: Exercise duplicate cell/server lookup, VLDB UUID and address resolution, fallback direct address connections when VLDB lookup fails, default cell configuration failures, realm replacement, global index bounds, and cleanup under valgrind or ASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_util.c -->
## sources/distributed-fs/openafs/src/libafscp/afscp_util.c

Purpose: Builds client security objects and VLDB ubik clients for `libafscp` cells. It supports rxnull anonymous mode, Kerberos credential cache authentication, and server-local KeyFile authentication as an arbitrary AFS user.

Important APIs and functions: Public controls are `afscp_Insecure`, `afscp_AnonymousAuth`, `afscp_LocalAuthAs`, and `afscp_SetConfDir`. Private helpers are `_GetCellInfo`, `_GetNullSecurityObject`, `_GetLocalSecurityObject` when Kerberos is available, `_GetSecurityObject`, and `_GetVLservers`.

Control flow: `_GetSecurityObject` obtains cell config, optionally tries local auth if `authas_name` is set, otherwise derives a Kerberos realm, opens the default credential cache, tries `afs/cell@realm` then `afs@realm`, derives a DES key, and creates an rxkad client security object at clear or crypt level. If Kerberos is disabled or auth fails and `try_anonymous` is set, it returns rxnull security. `_GetVLservers` creates RX connections to configured VLDB servers and initializes a ubik client.

State and persistence: Maintains global `insecure`, `try_anonymous`, `authas_name`, and `confdir`. These influence all later cell creation. It reads local OpenAFS and Kerberos configuration but does not persist changes.

Dependencies and integration: Uses OpenAFS auth config, rxnull, rxkad, rx identity, Kerberos 5 APIs, hcrypto DES derivation, and ubik client initialization. Called during `afscp_CellByName`.

Risks: Security behavior is process-global and order-dependent. Anonymous fallback only occurs when explicitly enabled. `afscp_SetConfDir` ignores open failure except by leaving `confdir` null for later calls. The nested `if (realm) if (realm == NULL)` branch is unreachable and suggests stale logic. Kerberos DES derivation limits interoperability to rxkad-compatible tickets.

Test signals: Test Kerberos credential success, service principal fallback, local auth, anonymous fallback, insecure clear mode, invalid impersonation names, alternate conf directories, missing CellServDB, and cleanup after repeated confdir changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_volume.c -->
## sources/distributed-fs/openafs/src/libafscp/afscp_volume.c

Purpose: Resolves AFS volumes by name or id and caches volume metadata in each `afscp_cell`. It converts VLDB entries into `afscp_volume` structures with server index lists.

Important APIs and functions: `afscp_VolumeByName` and `afscp_VolumeById`. Internal comparators `icompare` and `ncompare` key `tsearch` trees by volume id and by name plus type. `union allvldbentry` supports multiple VLDB wire formats.

Control flow: Lookup first probes the relevant cache tree. On miss, the code tries the newest VLDB entry RPC and falls back through older `N` and original formats when it receives `RXGEN_OPCODE`. It selects the requested or detected volume type, copies the volume id/name, filters server entries by VLDB flags, resolves each server by UUID or address, stores server indexes, then inserts the same volume object into both name and id caches.

State and persistence: Per-cell `volsbyname` and `volsbyid` trees cache heap allocated `afscp_volume` structures. Volumes carry stat and directory cache roots used by other files. No durable persistence.

Dependencies and integration: Depends on ubik VLDB clients, server lookup from `afscp_server.c`, AFS volume constants, and consumers in directory, file, fid, and dirops modules.

Risks: `ncompare` has a suspicious condition `if (vb->voltype < va->voltype)` instead of directly testing `va->voltype < vb->voltype`; equivalent for strict ordering in common cases but easy to misread. `afscp_VolumeById` tries `ubik_VL_GetEntryByNameU` using a decimal id string before ID fallback, which may be intentional compatibility but is surprising. Missing `nservers` or zero id returns `EIO` only in name lookup; ID lookup does not perform the same explicit validation. Tree operations are not synchronized.

Test signals: Cover cache hit paths, RW/RO/BACK selection, fallback across VLDB entry versions, UUID and IPv4 server entries, missing volume, volumes with no matching servers, id-to-type detection, and cross-check by name after id lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_volume.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafsrpc/Makefile.in -->
## sources/distributed-fs/openafs/src/libafsrpc/Makefile.in

Purpose: Builds the `libafsrpc` aggregate RPC library in static, PIC archive, and optional shared forms.

Important targets and variables: `LT_current`, `LT_revision`, and `LT_age` define libtool versioning. `LT_objs` aggregates fsint, rx, rxkad, crypto, comerr, util, rxstat, sys, lwp compatibility, opr, and optional rxgk libraries. `LT_libs` includes hcrypto, roken, threading, and optional GSSAPI libs. Targets include `all`, `libafsrpc.la`, `libafsrpc_pic.la`, `libafsrpc.a`, top libdir install rules, `install`, `dest`, and `clean`.

Control flow: `all` builds shared libraries when configured plus static and PIC archives. The shared-library rule links with `LT_LDLIB_shlib_only_NOQ`, with an AIX-specific branch adding the syscall import list `../sys/afsl.exp`. Static archive creation also adds `afsl.exp` on AIX. Install and dest targets place archives and optional shared artifacts in configured lib directories, then remove installed `.la` files for shared installs.

State and persistence: Produces build artifacts in the object tree and installs them to top libdir, DESTDIR libdir, or DEST lib. No runtime state.

Dependencies and integration: Integrates many lower-level OpenAFS libraries into a consumable RPC library. Conditional rxgk support is injected by configure substitutions.

Risks: Aggregate link order and platform-specific import-list handling are fragile. The `.libs/libafsrpc_pic.a` path assumes libtool internals. Libtool version increments require maintainer discipline.

Test signals: Build on AIX and non-AIX, shared and static configurations, rxgk enabled and disabled, install/dest packaging, and consumers linking against both `libafsrpc.a` and `libafsrpc_pic.a`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafsrpc/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/Makefile.common.in -->
## sources/distributed-fs/openafs/src/libuafs/Makefile.common.in

Purpose: Common make logic for building the userspace AFS client library `libuafs`, a PIC archive, a link smoke-test, and optional SWIG Perl bindings.

Important targets and variables: `MODULE_CFLAGS`, `LT_objs`, `MODULE_INCLUDE`, source directory variables, `all`, `libuafs.a`, `libuafs_pic.la`, `linktest`, `LIBUAFS_BUILD_PERL`, `PERLUAFS/ukernel.*`, `clean`, `install`, `dest`, and `h`. `LT_objs` aggregates AFS cache manager, vnode operation, RX, rxkad, auth, rxstat, generated XDR/RPC, utility, and UKERNEL support objects.

Control flow: Platform `MakefileProto.*` files define compiler and OS flags, then include this file. The `h` target generates a fake `h/` include tree before object compilation. Each `.lo` rule compiles a source file from its original subsystem into the libuafs object set. `linktest` links a small program against `libuafs.a` and required support libraries. Optional Perl bindings run SWIG on `ukernel_swig.i`, compile the wrapper with Perl embed flags, and link it with `libuafs_pic.a`.

State and persistence: Produces archives, generated `h/`, `PERLUAFS/`, `AFS_component_version_number.c`, linktest, and installed libraries/bindings. No runtime persistence.

Dependencies and integration: Bridges kernel-oriented AFS cache manager code into userspace by compiling with `-DKERNEL -DUKERNEL` and UKERNEL headers. It depends on generated fsint, vlserver, auth, and rxstat files in the object tree.

Risks: This file is build-system critical and highly coupled to source layout. The fake header tree is an intentional workaround and can mask include hygiene problems. SWIG/Perl embedding is optional but sensitive to platform flags. The object list must track subsystem changes manually.

Test signals: Full libuafs builds on each platform proto, `linktest`, Perl binding build when enabled, install/dest contents, clean idempotence, and rebuild after generated RPC files change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/Makefile.common.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.AIX.in -->
## sources/distributed-fs/openafs/src/libuafs/MakefileProto.AIX.in

Purpose: Supplies AIX-specific compiler, archive, and test-link settings before including `Makefile.common`.

Important variables: `DEFINES=-DKERNEL -DUKERNEL`, `AR=/usr/bin/ar`, `ARFLAGS=-r`, `RANLIB=/bin/ranlib`, `CC=$(MT_CC)`, `DEF_LIBPATH`, `TEST_CFLAGS`, `TEST_LDFLAGS`, `TEST_LIBS`, and `AFS_OS_CLEAN`.

Control flow: The file includes generated OpenAFS make configuration, sets install tool substitutions, declares AIX flags, and delegates all real targets to `Makefile.common`.

State and persistence: Controls generated build outputs only. AIX-specific clean removes export files such as `*.exp` and `export.h`.

Dependencies and integration: Integrates with threaded AIX compiler settings and pthread libraries. It relies on the common file for all object compilation, linktest, install, and dest logic.

Risks: Hard-coded tool paths and `DEF_LIBPATH` can become stale on newer AIX installations. The test link uses `-lpthreads`, which is platform-specific and can differ from modern pthread naming.

Test signals: AIX build of `libuafs.a`, `libuafs_pic.a`, and `linktest`; clean removes AIX export artifacts; install/dest match common expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.AIX.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.DARWIN.in -->
## sources/distributed-fs/openafs/src/libuafs/MakefileProto.DARWIN.in

Purpose: Defines Darwin/macOS flags for the common libuafs build.

Important variables: `DEFINES=-D_REENTRANT -DKERNEL -DUKERNEL`, empty `KOPTS`, `UAFS_CFLAGS=$(ARCHFLAGS)`, `TEST_CFLAGS` with pthread environment and architecture flags, `TEST_LDFLAGS=$(XLDFLAGS) $(ARCHFLAGS)`, and empty `TEST_LIBS`.

Control flow: Includes config and install substitutions, sets platform flags, then includes `Makefile.common` for the actual build graph.

State and persistence: Build artifacts are those produced by common rules. Architecture flags propagate to library objects, `linktest`, and optional SWIG binding compilation.

Dependencies and integration: Integrates with Darwin multi-architecture support in `lwp/Makefile.in` and libtool configuration. `ARCHFLAGS` is the key platform-specific input.

Risks: Missing or inconsistent `ARCHFLAGS` can produce linktest or binding architecture mismatches. Empty `TEST_LIBS` assumes system libraries satisfy pthread and runtime needs via compiler/linker defaults.

Test signals: Single-arch and multi-arch Darwin builds, linktest execution/link success, optional Perl binding architecture compatibility, and install packaging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.DARWIN.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.DFBSD.in -->
## sources/distributed-fs/openafs/src/libuafs/MakefileProto.DFBSD.in

Purpose: Provides DragonFly BSD-specific settings for libuafs.

Important variables: `CC=@CC@`, `DEFINES=-D_REENTRANT -DKERNEL -DUKERNEL`, empty `KOPTS`, `TEST_CFLAGS=-D_REENTRANT -DAFS_PTHREAD_ENV -DAFS_DFFBSD_ENV $(XCFLAGS)`, empty `TEST_LDFLAGS`, and `TEST_LIBS=-lpthread`.

Control flow: After configuration and install substitutions, the file declares platform flags and includes `Makefile.common`.

State and persistence: Only influences common build outputs. No runtime state.

Dependencies and integration: Integrates with DragonFly pthread and OpenAFS environment macros. The `<all>` marker is part of OpenAFS's makefile prototype filtering system.

Risks: The environment macro spelling `AFS_DFFBSD_ENV` is easy to confuse with other BSD variants and must match source conditionals. The direct `-lpthread` dependency assumes system naming.

Test signals: DragonFly build, linktest, conditional compilation paths selected by `AFS_DFFBSD_ENV`, and prototype preprocessing around `<all>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.DFBSD.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.FBSD.in -->
## sources/distributed-fs/openafs/src/libuafs/MakefileProto.FBSD.in

Purpose: Provides FreeBSD-specific settings for the common libuafs build.

Important variables: `CC=@CC@`, `DEFINES=-D_REENTRANT -DKERNEL -DUKERNEL`, empty `KOPTS`, `TEST_CFLAGS=-D_REENTRANT -DAFS_PTHREAD_ENV -DAFS_FBSD_ENV $(XCFLAGS)`, empty `TEST_LDFLAGS`, and `TEST_LIBS=-lpthread`.

Control flow: It includes base config, defines install tools, sets compiler/test flags, and delegates to `Makefile.common`.

State and persistence: Produces only the common libuafs artifacts.

Dependencies and integration: Selects FreeBSD conditionals in cache manager and UKERNEL sources through `AFS_FBSD_ENV`. The linktest inherits pthread linkage.

Risks: FreeBSD ABI and pthread flag expectations vary across releases; direct `-lpthread` may need to remain aligned with configure output. Kernel-style code compiled in userspace is sensitive to platform macro drift.

Test signals: FreeBSD libuafs build, `linktest`, optional Perl binding build, and source conditionals compiled under `AFS_FBSD_ENV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.FBSD.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.HPUX.in -->
## sources/distributed-fs/openafs/src/libuafs/MakefileProto.HPUX.in

Purpose: Supplies HP-UX and IA64 HP-UX specific compiler and linker settings for libuafs.

Important variables: `CC=/opt/ansic/bin/cc`, `DEFINES=-D_REENTRANT -DKERNEL -DUKERNEL`, platform-filtered `KOPTS`, platform-filtered `TEST_CFLAGS`, empty `TEST_LDFLAGS`, and `TEST_LIBS=-lnsl -lm -lpthread -ldld -lc`.

Control flow: Uses OpenAFS prototype tags such as `<hp_ux102 hp_ux110 hp_ux11i>`, `<ia64_hpux1122 ia64_hpux1123>`, and `<all>` to select proper options before including `Makefile.common`.

State and persistence: Only controls build outputs.

Dependencies and integration: Integrates with HP ANSI C compiler, HP-UX linker archive/shared modes, POSIX thread macros, network services libraries, and dynamic loader library.

Risks: Hard-coded compiler path and legacy `+DA1.0`, `+z`, and `-Wp,-H200000` flags are fragile on modern HP-UX or cross-build setups. Prototype filtering must select exactly one viable branch.

Test signals: HP-UX PA-RISC and IA64 builds, linktest, prototype filtering, static/PIC archive creation, and runtime symbol resolution for pthread/nsl/dld dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.HPUX.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.IRIX.in -->
## sources/distributed-fs/openafs/src/libuafs/MakefileProto.IRIX.in

Purpose: Provides IRIX-specific compiler and test-link flags for libuafs.

Important variables: `CC=cc`, `DEFINES=-D_SGI_MP_SOURCE -DKERNEL -DUKERNEL`, `TEST_CFLAGS=-D_SGI_MP_SOURCE -DAFS_PTHREAD_ENV -Dirix -DAFS_SGI_ENV $(XCFLAGS)`, `TEST_LDFLAGS=-ignore_minor`, and `TEST_LIBS=-lpthread -lm`.

Control flow: Standard prototype structure: include config, set install tools, define platform flags, include `Makefile.common`.

State and persistence: Controls common build outputs only.

Dependencies and integration: Selects SGI multiprocess and OpenAFS SGI conditionals. Linktest depends on pthread and math libraries plus IRIX linker behavior.

Risks: IRIX-specific flags are legacy and hard-coded. `-ignore_minor` can hide library version mismatches that should be visible in modern diagnostics.

Test signals: IRIX compile/link, linktest, source paths conditioned by `AFS_SGI_ENV`, and clean/install behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.IRIX.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.LINUX.in -->
## sources/distributed-fs/openafs/src/libuafs/MakefileProto.LINUX.in

Purpose: Defines Linux settings for libuafs builds.

Important variables: `DEFINES=-D_REENTRANT -DKERNEL -DUKERNEL`, empty `KOPTS`, `SYS_NAME=@AFS_SYSNAME@`, conditional `UAFS_CFLAGS=-fPIC` for `ppc64_linux26`, `TEST_CFLAGS=-pthread -D_REENTRANT -DAFS_PTHREAD_ENV -DAFS_LINUX_ENV $(XCFLAGS)`, empty `TEST_LDFLAGS`, and `TEST_LIBS=-lpthread @LIB_crypt@`.

Control flow: Includes generated config and install substitutions, applies Linux flags, then includes `Makefile.common`.

State and persistence: Controls generation of libuafs archives, linktest, and optional Perl bindings.

Dependencies and integration: Selects Linux-specific UKERNEL and cache manager conditionals and links pthread plus configure-selected crypt library.

Risks: The ppc64 PIC special case is narrow and may not cover all architectures requiring PIC. `-pthread` and `-lpthread` are both present through flags/libs, which is common but should be checked against toolchain behavior.

Test signals: Linux builds across x86, amd64, ppc64, and other supported sysnames; linktest; optional Perl binding; crypt dependency presence; and PIC archive link checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.LINUX.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.NBSD.in -->
## sources/distributed-fs/openafs/src/libuafs/MakefileProto.NBSD.in

Purpose: Provides NetBSD-specific settings for libuafs.

Important variables: `CC=gcc`, `DEFINES=-DKERNEL -DUKERNEL`, empty `KOPTS`, `TEST_CFLAGS=-DAFS_NBSD_ENV $(XCFLAGS)`, empty `TEST_LDFLAGS`, and empty `TEST_LIBS`.

Control flow: Includes config and install substitutions, defines the minimal NetBSD platform flags, then includes `Makefile.common`.

State and persistence: Only affects common build outputs.

Dependencies and integration: Selects NetBSD conditionals in userspace AFS code. Unlike several other BSD protos, it does not define `AFS_PTHREAD_ENV` or link pthreads here.

Risks: Lack of explicit pthread flags is notable because common code and linktest may depend on threading depending on configuration. Hard-coded `gcc` ignores `@CC@`, which can limit modern toolchain selection.

Test signals: NetBSD build and linktest, no-pthread configuration coverage, and compatibility with configured compiler expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.NBSD.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.OBSD.in -->
## sources/distributed-fs/openafs/src/libuafs/MakefileProto.OBSD.in

Purpose: Provides OpenBSD-specific settings for libuafs.

Important variables: `CC=gcc`, `DEFINES=-DKERNEL -DUKERNEL`, empty `KOPTS`, `TEST_CFLAGS=-DAFS_OBSD_ENV $(XCFLAGS)`, empty `TEST_LDFLAGS`, and empty `TEST_LIBS`.

Control flow: Standard platform proto: include generated config, define install tools and OS flags, include `Makefile.common`.

State and persistence: Controls common build artifacts only.

Dependencies and integration: Selects OpenBSD source conditionals through `AFS_OBSD_ENV`. Does not explicitly opt into pthread environment.

Risks: Hard-coded `gcc` and no pthread flags may not match current OpenBSD compiler/linker defaults. Because common rules compile kernel-style sources in userspace, missing reentrancy flags could expose platform-specific build failures.

Test signals: OpenBSD build, linktest, optional Perl binding if supported, and source conditionals selected by `AFS_OBSD_ENV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.OBSD.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.SOLARIS.in -->
## sources/distributed-fs/openafs/src/libuafs/MakefileProto.SOLARIS.in

Purpose: Supplies Solaris-specific flags for libuafs.

Important variables: `DEFINES=-D_REENTRANT -DKERNEL -DUKERNEL`, `TEST_CFLAGS=-mt -DAFS_PTHREAD_ENV -Dsolaris -DAFS_SUN5_ENV $(XCFLAGS)`, empty `TEST_LDFLAGS`, and `TEST_LIBS=-lsocket -lnsl -lthread -lm -ldl`.

Control flow: Includes config and install substitutions, declares Solaris threading and networking flags, and delegates to `Makefile.common`.

State and persistence: Controls common build artifacts only.

Dependencies and integration: Selects Solaris 5 conditionals and links socket, nsl, thread, math, and dl libraries for linktest and related test binaries.

Risks: Uses legacy `-mt` and `-lthread` conventions; modern Solaris-like environments may prefer pthread defaults. Network library order matters on Solaris.

Test signals: Solaris libuafs build, linktest, source conditionals with `AFS_SUN5_ENV`, and install/dest packaging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/MakefileProto.SOLARIS.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/afsload/afsload -->
## sources/distributed-fs/openafs/src/libuafs/afsload/afsload

Purpose: Shell front-end for running libuafs load tests under MPI.

Important logic: Defines installed paths for `afsload_check.pl`, `afsload_run.pl`, and Perl include path, reads `MPIRUN` and `LIBMPI` environment overrides, parses `-q`, `-p <nprocs>`, and `-t <test.conf>`, optionally validates the config, then launches MPI with one additional director process.

Control flow: `-p` is incremented by one because rank 0 is the director. Unless `-q` is set, it runs the checker with the expanded process count. It verifies `mpirun` exists and `LIBMPI` is a file, then runs `mpirun -np "$procs"` with `/bin/sh -c "LD_PRELOAD=$LIBMPI $ALPERL $ALRUN $conf"`.

State and persistence: Writes no state directly. The invoked Perl runner writes per-node logs according to config and mutates AFS test paths.

Dependencies and integration: Depends on MPI, a preloadable MPI library, installed afsload Perl modules, and the libuafs Perl binding.

Risks: Paths are hard-coded to `/usr/local/lib/afsload`. The shell command embeds `$conf` in a string, so whitespace or shell metacharacters in the config path are risky. It assumes `LD_PRELOAD` is the correct MPI binding mechanism.

Test signals: CLI validation, quiet vs checked mode, missing mpirun, missing LIBMPI, process count adjustment, config paths with spaces, and full simple.conf execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/afsload/afsload -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/afsload/afsload_check.pl -->
## sources/distributed-fs/openafs/src/libuafs/afsload/afsload_check.pl

Purpose: Validates an afsload configuration for a given MPI process count before execution.

Important APIs and functions: Calls `AFS::Load::Config::check_conf($np, $conf_file)`. Local `usage` enforces the argument form `-p <NP> <testconfig.conf>`.

Control flow: The script requires at least three arguments, validates the first is `-p`, validates process count as decimal digits, prints a status line, calls `check_conf`, and prints success if no fatal error is thrown.

State and persistence: No persistent state. Warnings and fatal parse errors are emitted to stdout/stderr.

Dependencies and integration: Depends on the `AFS::Load::Config` Perl module and shares the same config grammar as the runtime runner. The shell front-end invokes this unless quiet mode is requested.

Risks: Only validates syntactic/config coverage rules, not filesystem availability, cache directory existence, MPI readiness, or action runtime semantics. Argument parsing is positional and minimal.

Test signals: Bad argument count, nonnumeric `-p`, invalid flag, malformed config, node range warnings, and successful validation for provided simple and large example configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/afsload/afsload_check.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/afsload/afsload_run.pl -->
## sources/distributed-fs/openafs/src/libuafs/afsload/afsload_run.pl

Purpose: Runtime MPI harness for afsload. Rank 0 acts as the director and Test::More reporter; all other ranks initialize `AFS::ukernel` and execute configured filesystem actions.

Important logic: Uses `Parallel::MPI::Simple`, `AFS::Load::Config`, and on worker ranks `AFS::ukernel`. Maintains `@steps` and `%nodeconf`, where default logfile is `/dev/null` and default AFS config uses a rank-specific cache directory.

Control flow: Initializes MPI, loads the config using `rank-1` because user node 0 maps to MPI rank 1, validates at least one step, and initializes Test::More on rank 0. Worker ranks redirect stdout/stderr, call `uafs_Setup`, `uafs_ParseArgs`, and `uafs_Run`. For every step, workers run their assigned actions sequentially, collect failures as arrays, synchronize at barriers, gather all results to rank 0, and rank 0 emits one pass/fail per step with diagnostics. Workers shut down `AFS::ukernel` before `MPI_Finalize`.

State and persistence: Worker logs are appended to configured files. AFS cache directories and test filesystem paths are mutated by actions. MPI process memory stores step/action state.

Dependencies and integration: Depends on config parsing, action classes, MPI gather/barrier semantics, Test::More, and the SWIG-generated libuafs Perl binding.

Risks: Director has no AFS client and never runs actions. Any worker `die` can abort MPI execution. Results are gathered only after a barrier, so hung actions hang the step. Log files are append-only and can grow.

Test signals: MPI size less than two, rank mapping, one failing worker action, multiple failures, named and unnamed steps, log redirection, uafs setup errors, and shutdown/finalize behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/afsload/afsload_run.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/afsload/examples/large.conf -->
## sources/distributed-fs/openafs/src/libuafs/afsload/examples/large.conf

Purpose: Larger afsload scenario that exercises create, read, copy, concatenate, truncate, append, rename, hard-link, symlink, failure expectation, cleanup, and directory removal across multiple nodes.

Important structure: Starts with `nodeconfig` applying `afsconfig` and `logfile` to all nodes, then a sequence of `step` blocks. It uses wildcard node ranges, specific node ids, named step `"read newly created file"`, and actions from `AFS::Load::Action`.

Control flow: All nodes enter `/afs/.localcell/afsload`, node 0 creates a scratch directory, all nodes enter it, several nodes create files, all nodes validate reads, node 0 copies 1M from `/dev/urandom` into AFS, all nodes read multiple files, node 1 mutates `foo`, subsequent steps validate rename/link/symlink semantics, expected ENOENT is asserted after unlinking the hard-link target, and cleanup removes generated files and directory.

State and persistence: Creates and removes a `scratch` directory under the configured AFS path, uses `/tmp/afsload/cache.$RANK` and logs `/tmp/afsload/log.$RANK`, and reads local `/dev/urandom`.

Dependencies and integration: Depends on all relevant action classes, working AFS write permissions, cache directories already existing, and at least nodes 0, 1, and 2 being present for node-specific steps.

Risks: Not isolated if a previous failed run leaves `scratch` or files behind. Uses `.localcell` and assumes writable `/afs/.localcell/afsload`. The `1M` random copy may be slow or nondeterministic in timing.

Test signals: Good integration test for afsload parser and runtime, especially multi-node synchronization, link semantics, negative assertions, and cleanup reliability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/afsload/examples/large.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/afsload/examples/simple.conf -->
## sources/distributed-fs/openafs/src/libuafs/afsload/examples/simple.conf

Purpose: Minimal afsload scenario that validates core create, read, truncate, unlink, and expected failure behavior.

Important structure: Global `nodeconfig` sets rank-specific cache and log paths. Steps perform a chdir into `/afs/.localcell/afsload`, create `foo`, read it from all nodes, truncate/write from node 1, unlink from node 0, then verify `access_r foo` fails with `ENOENT`.

Control flow: Each `step` is a synchronization boundary. Some actions run on all nodes with `node *`; others run on single nodes. The named read step demonstrates human-readable Test::More output.

State and persistence: Mutates one file named `foo` under the selected AFS directory and writes rank logs under `/tmp/afsload`. Cache directories must exist before run.

Dependencies and integration: Uses `chdir`, `creat`, `read`, `truncwrite`, `unlink`, `fail`, and `access_r` action implementations plus MPI and libuafs runtime.

Risks: Assumes the target path exists and is writable. A failed run can leave `foo`, causing later `creat` with `O_EXCL` to fail. Requires at least two worker nodes because node 1 is referenced.

Test signals: Useful smoke test for config parsing, step naming, wildcard ranges, single-node actions, expected failure handling, and basic AFS visibility across nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/afsload/examples/simple.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/afsload/lib/AFS/Load/Action.pm -->
## sources/distributed-fs/openafs/src/libuafs/afsload/lib/AFS/Load/Action.pm

Purpose: Defines the afsload action framework and all built-in filesystem action classes used by configuration `node` directives.

Important APIs and classes: Base `AFS::Load::Action` provides `_interpret_impl`, `parse`, `new`, and `do`. Action packages include `chdir`, `creat`, `read`, `cat`, `cp`, `truncwrite`, `append`, `unlink`, `rename`, `hlink`, `slink`, `access_r`, `fail`, `ignore`, `mkdir`, and `rmdir`.

Control flow: `parse` maps the action name to package `AFS::Load::Action::<name>`, calls its constructor, and attaches action index. Each action validates argument count during construction. `do` delegates to `doact`. Most `doact` implementations call one or more `AFS::ukernel::uafs_*` functions and return `(0,0)` on success or `(errno_or_code, message)` on failure. `fail` wraps another action and succeeds only if it returns the expected error. `ignore` wraps another action and always succeeds.

State and persistence: Action objects store only arguments. Runtime actions mutate AFS or local filesystem state: files, directories, links, and working directory. `cp` can bridge local files and AFS depending on path form.

Dependencies and integration: Depends on POSIX constants, `AFS::ukernel`, `Errno`, and `Number::Format` for `cp` sizes. Instantiated by `AFS::Load::Config` and executed by `afsload_run.pl`.

Risks: `fail` only treats a single digit string as numeric because it uses `/^\d$/`, so multi-digit numeric errno values are interpreted as symbolic names. `cp` opens local files via two-argument `open` with interpolated paths, which is shell-like and unsafe for special characters. Some write checks use string `eq` for numeric byte counts. Error reporting relies heavily on `$!` after XS calls.

Test signals: Constructor arity checks for every action, success and failure paths for each `uafs_*` call, `fail` with symbolic and numeric errors, `ignore`, local-to-AFS and AFS-to-local `cp`, partial write/read behavior, and unsafe path handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/afsload/lib/AFS/Load/Action.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/afsload/lib/AFS/Load/Config.pm -->
## sources/distributed-fs/openafs/src/libuafs/afsload/lib/AFS/Load/Config.pm

Purpose: Parses and validates afsload configuration files, including node ranges, node configuration directives, step boundaries, names, and actions.

Important APIs and functions: `check_conf($np, $conf_file)` validates a full configuration for a process count. `load_conf($rank, $conf_file, $stepsref, $nodeconfref)` parses config for one logical worker rank. Internal helpers `_range_check`, `_range_match`, and `_nextword` implement range semantics and token walking.

Control flow: `load_conf` reads the full file, tokenizes it with `Text::ParseWords::parse_line`, appends a sentinel `step`, then walks top-level directives. In `nodeconfig`, matching node ranges assign key/value settings. In `step`, optional `name` is captured and matching node action directives are converted into action objects. Skipped directives are scanned until the next `node` or `step`. After parsing, `$RANK` substitutions are applied to node config values. `check_conf` calls `load_conf` with a negative pseudo-rank to validate ranges and records nodes that have actions.

State and persistence: Module globals `@saw_nodes` and `$in_nodeconfig` track validation state. No persistent output.

Dependencies and integration: Depends on `Text::ParseWords` and `AFS::Load::Action`. Consumed by both config checker and MPI runner.

Risks: Global validation state is not reset between calls, so repeated checks in one interpreter can leak `@saw_nodes`. The whole file is tokenized at once and comments are not explicitly handled. Skipping unknown action arguments relies on `node` and `step` tokens not appearing as data. Negative-rank validation is clever but fragile.

Test signals: All range forms, invalid ranges, nodeconfig matching, `$RANK` substitution, named steps, skipped unmatched nodes, missing actions for nodes warnings, repeated `check_conf` calls, and quoted strings containing whitespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/afsload/lib/AFS/Load/Config.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/linktest.c -->
## sources/distributed-fs/openafs/src/libuafs/linktest.c

Purpose: Link-only smoke program for `libuafs.a`.

Important APIs and functions: `main` calls `uafs_SetRxPort`, `uafs_Setup`, `uafs_ParseArgs`, `uafs_Run`, `uafs_RxServerProc`, and `uafs_Shutdown`.

Control flow: The program sets RX port to 0, initializes the userspace AFS client with null mount and argument defaults, starts it, enters the RX server procedure, then shuts down. A comment states it is not intended to be run; its purpose is to prove that a program can link with libuafs and its dependencies.

State and persistence: If run, it would initialize userspace AFS runtime state and may interact with cache/config defaults. In intended build use, it only creates a binary.

Dependencies and integration: Includes socket/stat/types, RX, OpenAFS sysincludes, and `afs_usrops.h`. Built by `Makefile.common` as `linktest` against `libuafs.a`, `libcmd`, `libafsutil`, `libopr`, crypto, roken, crypt, and platform test libs.

Risks: Because it calls runtime initialization and server loop functions, accidentally executing it may block or perform unintended client setup. It ignores return codes, which is acceptable for link testing but not runtime diagnostics.

Test signals: Successful compilation and link are the primary signal. A secondary controlled run can verify symbol resolution, but should be treated carefully because the program was not designed as an execution test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/linktest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/make_h_tree -->
## sources/distributed-fs/openafs/src/libuafs/make_h_tree

Purpose: Generates a local `h/` include tree for libuafs userspace builds by mapping legacy `#include <h/foo.h>` references to stubs including `<sys/foo.h>`.

Important logic: Creates directory `h`, scans `*.c` files in each argument directory, extracts include names matching `h/<name>`, sorts and uniques them, and writes `h/<name>` containing `#include <sys/<name>>`.

Control flow: The script runs with `sh -e`, so command failures abort. For each source directory argument, it uses `cat`, `sed`, `sort`, and `uniq`, then writes one stub per discovered header.

State and persistence: Creates and populates `h/` in the current working directory. Existing `h` will make `mkdir h` fail under `-e`, so callers usually remove it first.

Dependencies and integration: Called by `Makefile.common` target `h` after removing any existing `h`. Supports compiling kernel-ish AFS sources in userspace without changing their include names.

Risks: Uses command substitution over unquoted header names, though extracted names exclude slash and quotes. It scans only `.c` files directly under each provided directory. It overwrites stubs with `>` and assumes no conflicting real files in `h/`.

Test signals: Given sample C files with `#include <h/socket.h>`, verify `h/socket.h` contains `#include <sys/socket.h>`. Check failure on pre-existing `h`, multi-directory duplicate handling, and no-output behavior for sources without matching includes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libuafs/make_h_tree -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/log/Makefile.in -->
## sources/distributed-fs/openafs/src/log/Makefile.in

Purpose: Builds and installs OpenAFS authentication/token command-line tools `unlog`, `tokens`, `tokens.krb`, `pagsh`, and `pagsh.krb`.

Important targets and variables: `PROGRAMS`, `INCLS`, `LT_deps`, `LT_krb_deps`, `all`, `pagsh`, `pagsh.krb`, `unlog`, `tokens`, `tokens.krb`, `install`, `dest`, `clean`, and `test`.

Control flow: Normal tools link against rxkad, auth, cmd, util, and opr static libtool libraries. Kerberos variants use `liboafs_auth_krb.la` and compile `pagsh.c` with `AFS_KERBEROS_ENV`. Install places user commands in `bindir`, token tools in server bindir as well, and pagsh variants in bindir. `test` descends into `src/log/test`.

State and persistence: Produces binaries and component version source. Installs into client and server binary locations.

Dependencies and integration: Uses pthread make config, roken, threading libs, auth/rxkad/cmd/util/opr libraries, and component version generation.

Risks: `tokens.krb` reuses `tokens.o`, while `pagsh.krb` has a separate object with Kerberos macro. Install duplicates token binaries into server paths, so packaging mistakes can affect client and server images. The `PROGRAMS` variable omits pagsh despite `all` building it.

Test signals: Build all five binaries, install/dest layout, Kerberos and non-Kerberos link dependencies, clean idempotence, and `make test` in log/test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/log/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/log/pagsh.c -->
## sources/distributed-fs/openafs/src/log/pagsh.c

Purpose: Starts a shell in a new AFS PAG, optionally also creating a new Kerberos token PAG in Kerberos builds.

Important APIs and functions: `main` uses `getuid`, `getpwuid`, `setpag`, optional `ktc_newpag`, and `execvp`.

Control flow: On AIX it installs full-dump signal actions for better core files. It determines the current uid and passwd entry, but the code leaves shell as hard-coded `/bin/sh` rather than using `pw_shell`. It calls `setpag` and reports errors, calls `ktc_newpag` in `AFS_KERBEROS_ENV`, then replaces the process image with the shell while preserving argument vector after rewriting `argv[0]`.

State and persistence: Mutates the process credential/PAG state before exec. No files are written.

Dependencies and integration: Built as `pagsh` and `pagsh.krb` by `src/log/Makefile.in`. Depends on AFS auth/sys prototypes and RX headers.

Risks: Shell selection ignores the user's passwd shell. If `setpag` fails, the program still execs a shell, which may surprise callers expecting failure. `argv` is passed through to `/bin/sh`, so pagsh arguments become shell arguments.

Test signals: Run and inspect PAG change, failure behavior when `setpag` is unavailable, Kerberos build invoking `ktc_newpag`, AIX signal setup compilation, and exec argument handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/log/pagsh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/log/test/Makefile.in -->
## sources/distributed-fs/openafs/src/log/test/Makefile.in

Purpose: Builds legacy test programs for AFS token and authentication interfaces.

Important targets and variables: `LDIRS`, `LIBS`, `all`, `testlog`, `gettoktest`, `clean`, `install`, and `dest`.

Control flow: Includes config and LWP make settings, then builds `testlog` and `gettoktest` with `AFS_LDRULE` against auth, rxkad, des, sys, rx, lwp, cmd, afsutil, and platform extra libs. Install and dest are intentionally empty.

State and persistence: Produces test binaries in the test directory. Running those binaries can modify token state, but the makefile itself only builds.

Dependencies and integration: Uses legacy libraries and LWP runtime rather than pthread make config. Invoked by `src/log/Makefile.in` target `test`.

Risks: Library names are old-style `-lauth -lrxkad -ldes` and depend on `TOP_LIBDIR` and `DESTDIR` search order. Empty install/dest means tests are build-tree tools only.

Test signals: `make -C src/log/test`, link success, clean removes binaries, and runtime tests in a controlled AFS environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/log/test/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/log/test/gettoktest.c -->
## sources/distributed-fs/openafs/src/log/test/gettoktest.c

Purpose: Legacy diagnostic program for the cellular Venus token interface.

Important APIs and functions: `main` calls `U_CellGetLocalTokens` first in non-cellular mode, then iterates cellular entries until `errno == EDOM`.

Control flow: Prints a header, calls `U_CellGetLocalTokens` with `useCellEntry=0`, reports returned Vice ID or error, then loops cell indexes from 0 up to 1000 while the end-of-list condition has not been reached. For each cellular token it prints Vice ID, cell id, and primary flag.

State and persistence: Read-only with respect to tokens. It prints current cache manager token state.

Dependencies and integration: Includes legacy headers `itc.h`, `r/xdr.h`, and `afs/comauth.h`. Built by `src/log/test/Makefile.in`.

Risks: K&R style `main` and explicit `extern int errno` reflect old C conventions. The upper bound of 1000 prevents infinite loops but is arbitrary. The file includes `sys/file.h` and legacy RPC headers that may be portability pain points.

Test signals: Run with no tokens, one token, multiple cellular tokens, end-of-list EDOM, and non-EDOM error conditions from cache manager calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/log/test/gettoktest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/log/test/testlog.c -->
## sources/distributed-fs/openafs/src/log/test/testlog.c

Purpose: Legacy interactive test for authenticating to an AFS cell, setting local tokens in the cache manager, and restoring original tokens.

Important APIs and functions: Uses `U_GetLocalTokens`, `U_CellGetLocalTokens`, `GetLocalCellName`, `U_InitRPC`, `U_CellAuthenticate`, `U_SetLocalTokens`, and `U_CellSetLocalTokens`.

Control flow: Captures existing non-cellular and cellular tokens, discovers local cell, parses optional `-x`, user, password, and `-c cellname` arguments, optionally looks up the local passwd entry, initializes RPC, prompts for password if absent, authenticates to the AuthServer, sets tokens through both non-cellular and cellular APIs, then iterates saved tokens and restores them.

State and persistence: Temporarily mutates cache manager token state, then attempts to restore original tokens. It also erases a password argument from `argv` after copying it.

Dependencies and integration: Built by `src/log/test/Makefile.in`. Uses old auth/comauth interfaces and local cell config globals.

Risks: Old C syntax, fixed-size buffers, and `strcpy` usage carry overflow risk. A bug in the `-c` comparison checks `argv[currArg]` instead of the following cell value, so local-cell detection is suspect. Restore is best-effort; failures can leave token state changed. Password handling is primitive.

Test signals: Controlled test with valid and invalid credentials, explicit remote cell, `-x`, password prompt and password argument paths, token restoration after failures, and no-existing-token startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/log/test/testlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/log/tokens.c -->
## sources/distributed-fs/openafs/src/log/tokens.c

Purpose: Implements the `tokens` command, printing rxkad tokens held by the cache manager and their expiration status.

Important APIs and functions: `main` uses `ktc_ListTokensEx`, `ktc_GetTokenEx`, `token_extractRxkad`, and `token_FreeSet`.

Control flow: Rejects any argument except help-style usage by printing `Usage: tokens [-help]`. It prints a heading, then iterates token entries by cell number. For each cell, it fetches token data, extracts an rxkad token and client principal, formats user identity from name and instance, prints cell and expiration state, then frees the token set. End of list prints `--End of list--`.

State and persistence: Read-only with respect to token state. Allocated `cellName` strings are freed each iteration.

Dependencies and integration: Uses auth, ktc, token, rx/xdr, and component version infrastructure. Built as both `tokens` and `tokens.krb`, though source behavior is not separately conditional here.

Risks: Uses `strcpy`/`strcat` into `UserName` sized for expected ktc principal fields. Only rxkad tokens are printed; other token types in the set are ignored. Any argument prints usage and exits success, which may mask invalid usage.

Test signals: No tokens, expired token, normal user principal, empty principal, `AFS ID` and `Unix UID` display branches, token extraction failure, and multiple-cell iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/log/tokens.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/log/unlog.c -->
## sources/distributed-fs/openafs/src/log/unlog.c

Purpose: Implements `unlog`, removing all tokens or selected cell tokens from the cache manager.

Important APIs and functions: Command entry is `CommandProc` via the OpenAFS cmd package. `main` creates syntax with optional `-cell` list. Helpers are `unlog_ForgetCertainTokens`, `unlog_NormalizeCellNames`, `unlog_CheckUnlogList`, and `unlog_VerifyUnlog`.

Control flow: Without `-cell`, it calls `ktc_ForgetAllTokens`. With cells, it accepts up to 20 names, normalizes each through client cell configuration, lists and saves all current token sets, marks matching cells for deletion, warns for requested cells without tokens, forgets all tokens, then re-registers the token sets not marked deleted.

State and persistence: Mutates cache manager token state. Allocates normalized cell names and token set arrays; some allocations intentionally live until process exit.

Dependencies and integration: Uses OpenAFS cmd, auth/cellconfig/util/token/ktc libraries. Built by `src/log/Makefile.in`.

Risks: Selective deletion is not atomic from the cache manager perspective; there is a window where all tokens are removed before preserved tokens are restored. `MAXCELLS` is fixed at 20. Memory for normalized names and token sets is not fully released before exit. Restoration failures are reported but do not roll back.

Test signals: No-argument remove-all, one cell, multiple cells, unknown cell normalization, requested cell with no token warning, restoration failure, and concurrent token changes during selective unlog.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/log/unlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/Makefile.in -->
## sources/distributed-fs/openafs/src/lwp/Makefile.in

Purpose: Builds the legacy LWP cooperative threading library, compatibility shared/PIC libraries, installs LWP headers, and runs LWP tests.

Important targets and variables: `LIBOBJS`, `LT_objs`, `LT_deps`, `all`, `depinstall`, `liblwp.a`, `liboafs_lwpcompat.la`, `liblwpcompat_pic.la`, `process.o`, `test`, `install`, `dest`, `buildtools`, and `clean`.

Control flow: Builds core objects `lwp.o`, `process.o`, `iomgr.o`, `timer.o`, `threadname.o`, and version object into `liblwp.a`, with libtool objects `waitkey`, `fasttime`, and `lock` added from `.lwp`. `process.o` is selected through a large `SYS_NAME` case that chooses architecture-specific assembly or C context-switch implementation. Header install targets publish `afs_lock.h`, `lwp.h`, and version source.

State and persistence: Produces static/PIC/shared compatibility artifacts, installed headers, generated `process.s` intermediates, and test binaries.

Dependencies and integration: Includes LWP-specific make config and tool config, assembler/preprocessor toolchain, opr library, and platform-specific process context files.

Risks: `process.o` selection is highly platform-sensitive. Assembly preprocessing leaves many architecture branches with custom cleanup. Darwin universal builds rely on `lipo` and arch flags. Static archive rule reaches into `.lwp/` libtool object paths.

Test signals: Build across representative sysnames, LWP test directory, header install, process assembly cleanup, shared/PIC compatibility link, and `AFS_LWP_STACK_SIZE` runtime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/afs_lock.h -->
## sources/distributed-fs/openafs/src/lwp/afs_lock.h

Purpose: Public userspace lock API for Vice/OpenAFS code, supporting read, write, shared, and boosted lock modes over either pthread condition variables or LWP event waits.

Important APIs and types: `struct Lock` contains wait state bits, exclusive lock bits, reader count, waiter count, and pthread mutex/condition variables when `AFS_PTHREAD_ENV` is enabled. Declares `Afs_Lock_Obtain`, release/wakeup helpers, `Lock_Init`, and `Lock_Destroy`. Macros implement `ObtainReadLock`, no-block variants, `ObtainWriteLock`, `ObtainSharedLock`, `BoostSharedLock`, `UnboostSharedLock`, release macros, `ConvertWriteToReadLock`, and lock state queries.

Control flow: Fast-path macros acquire the underlying mutex when applicable, check lock state inline, and call `Afs_Lock_Obtain` only when they must wait. Release macros clear state bits and call wakeup helpers when waiters exist.

State and persistence: Lock state is entirely in `struct Lock`. No persistence.

Dependencies and integration: Non-kernel only; explicitly errors under `KERNEL`. Uses opr mutex/cv wrappers in pthread builds and LWP wait/signal functions in non-pthread builds.

Risks: Counters and state fields are `unsigned char`, so extreme waiter/reader counts can overflow. Macro-heavy API evaluates its `lock` argument multiple times. Correctness depends on callers matching release mode to obtain mode. Shared-to-boost transitions are subtle.

Test signals: Reader concurrency, writer exclusion, shared lock behavior, boost/unboost, no-block paths, conversion write-to-read, waiter wake preferences, pthread and LWP builds, and overflow stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/afs_lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/fasttime.c -->
## sources/distributed-fs/openafs/src/lwp/fasttime.c

Purpose: Compatibility time API for LWP-era code. Historical comments describe memory-mapped kernel time, but the current implementation falls back to `gettimeofday`.

Important APIs and functions: `FT_Init`, `FT_GetTimeOfDay`, `TM_GetTimeOfDay`, `FT_AGetTimeOfDay`, and `FT_ApproxTime`. Global `FT_LastTime` stores the last successful time value, and `ft_debug` is available for diagnostics.

Control flow: `FT_Init` tracks an enum init state and returns failure for real initialization because mmap support is not implemented. `FT_GetTimeOfDay` calls `gettimeofday`, clamps microseconds into select-compatible range, and updates `FT_LastTime`. `FT_AGetTimeOfDay` returns cached time if available. `FT_ApproxTime` returns `time(0)` under pthread builds and cached seconds under LWP builds, initializing cache if needed.

State and persistence: Process-local `initState` and `FT_LastTime`. No durable state.

Dependencies and integration: Used by LWP timer and I/O manager code for timeouts and approximate time. Provides compatibility alias `TM_GetTimeOfDay`.

Risks: Cached approximate time can be stale in non-pthread builds until another exact time call occurs. `FT_Init(notReally=1)` returns success while leaving state as tried. Timezone requests are passed through to `gettimeofday`.

Test signals: Microsecond clamping, first approximate call, cached approximate call, pthread vs LWP behavior, explicit init before and after use, and error path if `gettimeofday` fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/fasttime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/iomgr.c -->
## sources/distributed-fs/openafs/src/lwp/iomgr.c

Purpose: Implements the LWP I/O manager, allowing cooperative lightweight processes to wait on select file descriptors, timeouts, Unix signals, and software signals.

Important APIs and functions: Public functions include `IOMGR_Initialize`, `IOMGR_Finalize`, `IOMGR_Select`, `IOMGR_Poll`, `IOMGR_Cancel`, `IOMGR_Signal`, `IOMGR_CancelSignal`, `IOMGR_Sleep`, `IOMGR_AllocFDSet`, `IOMGR_FreeFDSet`, and `IOMGR_SoftSig`. Core internal functions include `IOMGR`, `SignalIO`, `SignalTimeout`, `SigHandler`, and `SignalSignals`.

Control flow: `IOMGR_Initialize` initializes LWP support if needed, creates a timer list, and starts an `IO MANAGER` LWP. `IOMGR_Select` either performs immediate polling select or constructs an `IoRequest`, inserts it into the timer queue, records it in the active PCB, and `LWP_QWait`s. The manager loop handles delivered signals, expires timers, builds aggregate fd sets, runs `select`, signals matching requests, and dispatches runnable LWPs. `IOMGR_Cancel` removes a pending request and wakes the waiting process with result `-2`.

State and persistence: Maintains global request timer list, request free list, fd_set pool, signal handler state, soft signal slots, aggregate fd sets, and the IOMGR process id. No disk persistence.

Dependencies and integration: Depends on LWP queues, timer package, fasttime, POSIX select/signal APIs, and platform-specific fd_set representation.

Risks: Global state is not pthread-safe and is intended for cooperative LWP use. `FD_SETSIZE` is forced to 65536 on non-Windows, so fd_set memory is large. Signal handling races are acknowledged in comments. `IOMGR_Poll` logs allocation failure but can still dereference null fd sets. Request lifetime invariants are delicate because the selector frees requests after wakeup.

Test signals: Blocking select wake by fd readiness, timeout wake, cancel, Unix signal delivery, software signal process creation, high fd values, invalid timeval correction, finalize cleanup, and Windows/Linux max-wait behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/iomgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/lock.c -->
## sources/distributed-fs/openafs/src/lwp/lock.c

Purpose: Implements the wait and wake slow paths for `struct Lock` declared in `afs_lock.h`.

Important APIs and functions: `Lock_Init`, `Lock_Destroy`, `Afs_Lock_Obtain`, `Afs_Lock_WakeupR`, `Afs_Lock_ReleaseR`, `Afs_Lock_ReleaseW`, and non-pthread atomic wait helpers `LWP_WaitProcessR`, `LWP_WaitProcessW`, and `LWP_WaitProcessS`.

Control flow: `Afs_Lock_Obtain` handles four modes. Read waits while a write lock is present, write waits while any exclusive or reader state exists, shared waits while any exclusive lock exists, and boosted waits while readers remain. In pthread builds it waits on read or write condition variables under the caller-held mutex. In LWP builds it waits on event addresses. Release helpers choose whether to wake readers or exclusive waiters, with `ReleaseR` preferring readers and `ReleaseW` preferring exclusive lockers.

State and persistence: Mutates only the supplied `struct Lock`.

Dependencies and integration: Bridges `afs_lock.h` macros to pthread opr condition variables or LWP wait/signal calls. Used by userspace OpenAFS code that needs kernel-style lock semantics outside the kernel.

Risks: Wait-state bits are coarse, so broadcasts can wake more waiters than can proceed. Fairness depends on which release helper is used. Non-pthread atomic wait helpers are only atomic because LWP is cooperative, not because a real mutex is held. Caller misuse of lock mode can corrupt state.

Test signals: All obtain/release modes under contention, pthread and LWP builds, boost with active readers, wake preference differences, no-block macro compatibility, and lock destroy after waiters drain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/lwp.c -->
## sources/distributed-fs/openafs/src/lwp/lwp.c

Purpose: Implements the core non-preemptive lightweight process scheduler for OpenAFS, including process creation/destruction, cooperative dispatch, event waiting/signaling, stack management, and per-process rocks.

Important APIs and functions: Public APIs include `LWP_InitializeProcessSupport`, `LWP_CreateProcess`, `LWP_CreateProcess2` on AIX, `LWP_DestroyProcess`, `LWP_DispatchProcess`, `LWP_WaitProcess`, `LWP_MwaitProcess`, `LWP_INTERNALSIGNAL`, `LWP_QWait`, `LWP_QSignal`, `LWP_CurrentProcess`, `LWP_ThreadId`, `LWP_GetProcessPriority`, `LWP_TerminateProcessSupport`, `LWP_StackUsed`, `LWP_NewRock`, and `LWP_GetRock`. Internal helpers manage queues, PCBs, stacks, dispatcher context, and signaling.

Control flow: Initialization creates the main PCB and dispatcher anchor. Process creation allocates a PCB and stack, initializes stack guard/use tracking, inserts it into a priority runnable queue, then uses architecture-specific `savecontext` to build a start context. `Dispatcher` checks stack overflow, rotates the current runnable queue, selects the highest priority non-empty runnable queue, and `returnto`s that context. Wait calls move the active process to blocked or qwaiting queues; signal calls scan blocked processes and move satisfied waiters back to runnable.

State and persistence: Global scheduler state includes runnable queues by priority, blocked and qwaiting queues, current PCB pointer, LWP control anchor, stack sizing knobs, next process index, and overflow behavior. No durable persistence.

Dependencies and integration: Requires `savecontext` and `returnto` from platform process assembly/C code. IOMGR and lock code build on its wait/signal/dispatch APIs.

Risks: Cooperative scheduling means blocking system calls outside IOMGR block all LWPs. Stack setup is architecture-specific and fragile. Stack overflow checks assume downward-growing stacks except special HP handling. `LWP_TerminateProcessSupport` must run from the original process. Event matching is pointer identity based. No pthread safety.

Test signals: Process creation and completion, priority scheduling, wait on one and multiple events, quick wait/signal, destroy self and other process, stack overflow diagnostics, rock set/get behavior, environment-driven minimum stack size, and architecture context-switch tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/lwp.c -->
