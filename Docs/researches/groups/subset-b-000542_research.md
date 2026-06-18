# Research: subset-b-000542

Grouped research for BeeGFS client module remoting, node-store, OS-compatibility, and page/buffer toolkit files. Each section preserves the source path and is wrapped with reconciliation markers for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsRemoting.c -->
## sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsRemoting.c

**Purpose:** Implements the BeeGFS kernel client's remote filesystem operations: metadata RPCs, file open/close, locking, striped read/write dispatch, fsync/statfs, xattr operations, lookup-intent, hardlink, refresh, file-version, and file-state changes. It is the main bridge from VFS-facing helpers to BeeGFS metadata/storage network messages.

**Important APIs/types/functions:** Key public functions include `FhgfsOpsRemoting_initMsgBufCache`, `destroyMsgBufCache`, `listdirFromOffset`, `statRoot`, `statAndGetParentInfo`, `setAttr`, `mkdir`, `rmdir`, `mkfileWithStripeHints`, `unlinkfile`, `openfile`, `closefileEx`, `flock*Ex`, `writefileVec`, `rwChunkPageVec`, `readfileVec`, `rename`, `truncfile`, `fsyncfile`, `statStoragePath`, `listXAttr`, `getXAttr`, `setXAttr`, `lookupIntent`, `hardlink`, `refreshEntry`, `bumpFileVersion`, `getFileVersion`, and `SetFileState`. Static helpers include `rrpeer_from_entryinfo`, `__FhgfsOpsRemoting_getChunkOffset`, `__FhgfsOpsRemoting_writefileVerify`, and iterator adapters for commkit state.

**Control flow:** Most metadata methods build a typed message from `EntryInfo`, wrap it in `RequestResponseArgs`, select a `RequestResponseNode` from the entry's direct owner or mirror buddy group, call `MessagingTk_requestResponseNodeRetryAutoIntr`, cast the response, map its result to `FhgfsOpsErr`, log selected server errors, and free response buffers. `openfile` adds quota/access-check flags, retries `FILEACCESS_DENIED` based on server file-state compatibility data unless `O_NONBLOCK` was requested, stores returned handle ID/path info/stripe pattern, and closes the remote handle if an invalid pattern is received. Locking registers a wait-ack, sends flock messages, waits or resends on delayed grants, releases `eiRLock` while waiting, and handles interrupt races after unregister. Vector writes split user data by stripe chunks, allocate `FileOpVecState` from a mempool, dispatch storage operations through `FhgfsOpsCommKit_writefileV2bCommunicate`, verify each target's result, update `firstWriteDone`, and advance the caller's iterator only for successful bytes. Reads reserve a safe sink for pipe iterators, split by stripe set, dispatch parallel target reads, treat short positive results as EOF, return partial bytes before errors, and release pages/sink state on all exits.

**State and persistence behavior:** Module-global state consists of the message buffer slab/mempool and `writefileStatePool`, initialized during module load and destroyed during unload. Per-handle state is carried in `RemotingIOInfo`: remote handle ID, stripe pattern, path info, access flags, first-write bitset, max-used target index, user/group IDs, and optional NVFS flag. Persistent cluster state is changed only through server RPCs: creates, removes, truncates, xattrs, file version bumps, file state, lock state, close/fync effects, and file data writes. Directory capability state is cached on `FsDirInfo` for buffer-size listing mode. The first-write bitset is an in-memory client-side signal used to detect storage cache loss behavior, not durable metadata.

**Dependencies and integration points:** Depends on `App` for config, loggers, node stores, target state stores, buddy mappings, counters, local node identity, and ack store. It integrates with BeeGFS message classes, `MessagingTk`, `FhgfsOpsCommKit`/`FhgfsOpsCommKitVec`, `StripePattern`, `PathInfo`, `BitStore`, `FhgfsChunkPageVec`, `BeeGFS_ReadSink`, kernel `iov_iter`, VFS page writeback/read completion, quota config, idmapped mount helpers, and optional NVFS/RDMA support.

**Risks:** The file has many cleanup paths where response buffers, page sinks, mempool objects, and NVFS references must be released exactly once. Stripe offset math assumes power-of-two chunk sizes for bit-mask modulo. Short writes/reads across multiple targets can leave later successful target writes unreported to userspace. The open retry loop depends on modern server compatibility flags; older servers return access denied without retry. `listdirFromOffset` must keep all parsed vectors length-aligned or clear partial contents. Fsync negates storage node results, so sign conventions must stay consistent with commkit state. Xattr size/name limits are client-side protocol guards and must match message-size expectations.

**Test signals:** Exercise metadata RPC success/error mappings, buddy-mirrored and direct owner routing, listdir capability auto-detection, open retry behavior for every data state, invalid pattern rollback, interrupted lock waits, vector write/read stripe splitting at chunk boundaries, partial target results, pipe-backed reads, fsync across primary and mirror targets, statfs with ignored target errors, xattr range/toolong cases, lookup-intent create/open/stat combinations, and module init/unload pool lifetime under fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsRemoting.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsRemoting.h -->
## sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsRemoting.h

**Purpose:** Declares the BeeGFS client remoting API used by filesystem/VFS code to perform metadata RPCs and storage IO. It also provides small inline wrappers that adapt raw user or kernel buffers into `iov_iter` objects.

**Important APIs/types/functions:** Defines `enum Fhgfs_RWType`, `struct FileOpVecState`, `union RWFileVecState`, lifecycle functions for message-buffer caches, metadata operations, open/close/locking APIs, vector/page IO APIs, xattr APIs, lookup-intent/hardlink/refresh/version/file-state APIs, and the internal lock helper `__FhgfsOpsRemoting_flockGenericEx`. Inline helpers include `FhgfsOpsRemoting_writefile`, `writefile_kernel`, `readfile_user`, `readfile_kernel`, and `statDirect`.

**Control flow:** Callers include this header, initialize a `RemotingIOInfo`, and then call public remoting functions. The inline read/write wrappers allocate stack-local `iov_iter`/`iovec` or `kvec` compound literals through `STACK_ALLOC_BEEGFS_ITER_*`, then delegate to `readfileVec`/`writefileVec`.

**State and persistence behavior:** The header itself owns no state. It exposes state-bearing structures from `RemotingIOInfo`, `FileOpState`, and page-vector helpers. Persistent filesystem effects occur in the `.c` implementation through remote RPCs.

**Dependencies and integration points:** Includes BeeGFS filesystem info types, storage definitions/errors, `MetadataTk`, `FileEvent`, commkit declarations, `RemotingIOInfo`, `os/iov_iter.h`, and page-vector wrappers. It is a central interface between VFS operation files and network/storage layers.

**Risks:** The header contains both a `static inline` declaration and an `extern` declaration for `FhgfsOpsRemoting_statDirect`, which is unusual but used to publish the inline definition. Stack iterator wrappers rely on compound-literal lifetime staying within the call expression. The internal `__FhgfsOpsRemoting_flockGenericEx` is exposed to allow specialized callers but is easy to misuse because ack IDs and initialized message types must match.

**Test signals:** Compile all remoting callers across supported kernel versions, validate user/kernel buffer wrappers for read/write paths, and check that every declared RPC has exactly one compatible implementation and expected response type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsRemoting.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/filesystem/RemotingIOInfo.h -->
## sources/distributed-fs/beegfs/client_module/source/net/filesystem/RemotingIOInfo.h

**Purpose:** Defines `RemotingIOInfo`, the per-open/per-IO context passed through BeeGFS remote file operations. It bundles application context, remote handle state, striping data, path info, access flags, write-tracking state, ownership IDs, and optional NVFS state.

**Important APIs/types/functions:** Public inline routines are `RemotingIOInfo_initOpen`, `RemotingIOInfo_initSpecialClose`, `RemotingIOInfo_freeVals`, `RemotingIOInfo_getNumPagesPerStripe`, and `RemotingIOInfo_getNumPagesPerChunk`. The struct fields include `app`, `fileHandleID`, `pattern`, `pathInfo`, `accessFlags`, `needsAppendLockCleanup`, `maxUsedTargetIndex`, `firstWriteDone`, `userID`, `groupID`, and optional `nvfs`.

**Control flow:** Normal callers initialize an object for open, then `FhgfsOpsRemoting_openfile` fills handle ID, path info, and possibly pattern. Special-close initialization is used after partial atomic-open/lookup-open failures when only a remote close is needed. IO paths read stripe geometry from `pattern`, update `maxUsedTargetIndex`, and consult `firstWriteDone`.

**State and persistence behavior:** The struct is transient in-memory handle state. `freeVals` destroys the stripe pattern, frees the duplicated remote handle ID, and uninitializes path info if present. The max-target and first-write pointers generally point into inode handle state, so this struct may not own them.

**Dependencies and integration points:** Depends on `App`, `PathInfo`, `StripePattern`, and `BitStore`. It is consumed heavily by `FhgfsOpsRemoting.c`, commkit storage messages, inode handle management, and buffered/native IO paths.

**Risks:** Ownership is mixed: `fileHandleID`/`pattern` may be owned by this context in special direct-open flows, while `pathInfo`, bitsets, and atomics are often external. Calling `freeVals` on an inode-managed context could free objects still owned elsewhere. Page count helpers assume a valid stripe pattern and chunk size divisible by `PAGE_SIZE`.

**Test signals:** Cover direct-open cleanup, special close after partial open failures, IO with external inode-managed state, page-per-chunk calculations for supported chunk sizes, and null-pattern guard behavior in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/filesystem/RemotingIOInfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/message/NetMessageFactory.c -->
## sources/distributed-fs/beegfs/client_module/source/net/message/NetMessageFactory.c

**Purpose:** Implements deserialization and factory construction for network messages received by the BeeGFS kernel client. It maps wire message type IDs to concrete client-side message structs and validates headers/payloads.

**Important APIs/types/functions:** `NetMessageFactory_createFromBuf` decodes a raw buffer into an allocated message. `NetMessageFactory_deserializeFromBuf` deserializes into a caller-provided expected message object. `NetMessageFactory_createFromMsgType` maps `NETMSGTYPE_*` IDs to `NETMESSAGE_CONSTRUCT(TYPE)` calls. Static `__NetMessageFactory_deserializeRaw` copies the header, checks feature-flag compatibility, and invokes the message-specific `deserializePayload`.

**Control flow:** A raw receive buffer is wrapped in `DeserializeCtx`, the generic header is decoded, a concrete message object is created by switch, and the payload is decoded only if the type is recognized and compatible. Incompatible feature flags or payload decode failures mark the message invalid. Preallocated deserialization first checks that the wire type equals the expected type.

**State and persistence behavior:** No durable state is stored here. The factory allocates message objects that callers must later destruct/free. Wire compatibility is enforced through message header feature flags and typed payload deserializers.

**Dependencies and integration points:** Includes all response/control/node/storage/session messages that the client can receive, plus optional NVFS RDMA response support. It is used by messaging/commkit receive paths and must stay synchronized with the protocol enum and message constructors.

**Risks:** Missing a new message type turns a valid server response into `NETMSGTYPE_Invalid`. Header deserialization appears unconditional; callers must ensure buffer length is large enough for the header. The default invalid path still allocates a `SimpleMsg`, so allocation failure behavior depends on `os_kmalloc`. Feature-flag compatibility is checked before payload decode, which is correct but requires each message class to declare supported flags accurately.

**Test signals:** Test creation for every mapped message type, invalid/unknown types, expected-type mismatch, incompatible feature flags, malformed payloads, optional `BEEGFS_NVFS` mappings, and memory ownership/destruction of both typed and invalid messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/message/NetMessageFactory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/message/NetMessageFactory.h -->
## sources/distributed-fs/beegfs/client_module/source/net/message/NetMessageFactory.h

**Purpose:** Declares the kernel-client message factory interface for creating or deserializing `NetMessage` objects from receive buffers or message type IDs.

**Important APIs/types/functions:** Exposes `NetMessageFactory_createFromBuf`, `NetMessageFactory_deserializeFromBuf`, and `NetMessageFactory_createFromMsgType`.

**Control flow:** Callers provide an `App`, buffer pointer, buffer length, and optionally a preallocated output message plus expected type. Implementations in the `.c` file handle header decode, type dispatch, compatibility checks, and payload decode.

**State and persistence behavior:** The header owns no state. It defines allocation/ownership expectations: `createFromBuf` and `createFromMsgType` return heap-allocated messages owned by the caller; `deserializeFromBuf` fills a caller-owned object.

**Dependencies and integration points:** Depends on `common/Common.h` and the generic `NetMessage` declaration. It is included by networking receive code and RPC helpers that need protocol message construction.

**Risks:** The interface does not encode buffer mutability or ownership beyond raw `char*`, so callers must ensure the buffer remains valid during deserialization. Expected message type is an unsigned short protocol constant; mismatches fail without richer diagnostics.

**Test signals:** Compile users against the header, validate caller cleanup of allocated messages, and test that preallocated response deserialization fails cleanly for wrong message types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/net/message/NetMessageFactory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/nodes/NodeStoreEx.c -->
## sources/distributed-fs/beegfs/client_module/source/nodes/NodeStoreEx.c

**Purpose:** Implements a thread-safe kernel client node store for metadata/storage/management nodes. It tracks active nodes by numeric ID, updates aliases/interfaces on heartbeat/list refreshes, handles root metadata owner selection, references nodes safely, and synchronizes the store against ordered master lists.

**Important APIs/types/functions:** Key functions are `NodeStoreEx_init`, `construct`, `uninit`, `addOrUpdateNode`, `referenceNode`, `referenceRootNode`, `referenceNodeByTargetID`, `deleteNode`, `getSize`, `referenceFirstNode`, `referenceNextNodeAndReleaseOld`, `getRootOwner`, `setRootOwner`, `waitForFirstNode`, `syncNodes`, and `__NodeStoreEx_handleNodeVersion`.

**Control flow:** Adds/updates take the write lock, reject numeric ID 0, find existing nodes, update aliases when non-empty incoming aliases differ, clone/update NIC lists and heartbeat time, or insert new nodes and mark them active. References take the read lock, find a node, increment its kref, and return it for later `Node_put`. Root references resolve mirror buddy groups to primary target IDs before looking up the node. `syncNodes` compares sorted active/master iterators under lock to compute added/removed IDs, then unlocks and performs deletion/addition in a second phase to avoid virtual-method style reentrancy issues.

**State and persistence behavior:** The store maintains in-memory `NodeTree`, `RWLock`, optional `newNodeAppeared` completion pointer, `_rootOwner`, and `storeType`. Node additions consume ownership of the incoming node pointer and null it. Deletions erase from the active tree and rely on node reference counting for lifetime. No persistent configuration is written here; it reflects management-provided cluster state.

**Dependencies and integration points:** Uses `App` logging and buddy mapper, `Node`, `NodeTree`, `NodeList`, `TargetMapper`, NIC capability helpers, `RWLock`, kernel completions, and `MirrorBuddyGroupMapper`. Remoting paths use node stores to route request/response traffic and stat root.

**Risks:** Callers must release referenced nodes or leak refs; debug builds warn on very high reference counts. `waitForFirstNode` supports a single waiter through `newNodeAppeared` and warns if reused concurrently. `syncNodes` assumes the master list is ordered and removes nodes from it while building `addLaterNodes`. Root buddy resolution depends on up-to-date buddy mappings.

**Test signals:** Test add/update alias changes, invalid ID rejection, NIC update behavior, reference/release lifetime, root owner direct and mirrored lookup, target-ID mapping failures, wait-for-first-node timeout and completion, sorted sync add/remove/unchanged cases, and concurrent readers during updates/deletes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/nodes/NodeStoreEx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/nodes/NodeStoreEx.h -->
## sources/distributed-fs/beegfs/client_module/source/nodes/NodeStoreEx.h

**Purpose:** Declares `NodeStoreEx`, the kernel client node-store abstraction corresponding to userspace node stores, with APIs for insertion, lookup, iteration, root-owner tracking, waiting, and synchronization.

**Important APIs/types/functions:** Defines `struct NodeStoreEx` with `App*`, `RWLock`, optional completion pointer, `NodeTree`, `_rootOwner`, and `storeType`. Declares all lifecycle and lookup/sync functions plus inline `NodeStoreEx_getStoreType`.

**Control flow:** Callers construct/init a store for a `NodeType`, add or update owned `Node*` instances, reference nodes by numeric ID or target ID, iterate by first/next, and synchronize against management lists. The header's contract makes reference ownership explicit: returned nodes require later release.

**State and persistence behavior:** State is in-memory only and protected by `rwLock`. `_rootOwner` may represent a direct node or mirror buddy group. The store type is applied to nodes when they enter the store.

**Dependencies and integration points:** Pulls in BeeGFS logging, `App`, lists, `EntryInfo`, storage errors, threading primitives, `Node`, `NodeTree`, `TargetMapper`, and kernel completion/rwsem headers. It is consumed by app initialization, management synchronization, and remoting routing.

**Risks:** The header declares `NodeStoreEx_referenceNextNode` but the inspected `.c` file implements `referenceNextNodeAndReleaseOld`; callers or other translation units must provide/use the correct symbol. Incorrect release discipline can leak or prematurely drop node references. `_rootOwner` validity relies on `NodeOrGroup` semantics outside this file.

**Test signals:** Build all users to catch declaration/definition drift, run lockdep/concurrency tests for reference and sync operations, and validate root-owner state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/nodes/NodeStoreEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/os/OsCompat.c -->
## sources/distributed-fs/beegfs/client_module/source/os/OsCompat.c

**Purpose:** Provides compatibility implementations for Linux kernel APIs missing or differently shaped on supported older kernels. It lets the BeeGFS client module compile across a wide kernel-version matrix.

**Important APIs/types/functions:** Implements fallback `memdup_user`, `bdi_setup_and_register`, old `find_get_pages_tag`, `d_make_root`, `d_materialise_unique`, `OsCompat_initKmemCache`, postorder rbtree helpers, `os_generic_write_checks`, and fallback `have_submounts`/`d_walk`.

**Control flow:** Most functions are compiled conditionally behind `KERNEL_HAS_*` feature macros. Allocation/copy shims mimic upstream behavior. `OsCompat_initKmemCache` chooses the proper `kmem_cache_create` signature and flags. `have_submounts` walks the dentry tree under rename seqlock and dentry locks, searching for a mount point.

**State and persistence behavior:** No persistent state is kept. `bdi_setup_and_register` uses a static atomic sequence to create unique BDI registration names on kernels lacking the helper.

**Dependencies and integration points:** Depends on kernel mm, backing-dev, pagemap, uio, writeback, rbtree, dcache, and BeeGFS logging/config headers. It is used by module init, inode/dentry/page paths, and memory-cache setup.

**Risks:** Compatibility code must match kernel locking rules for each era; the fallback `d_walk` is especially sensitive to rename locking and dentry list layout differences. Feature macro mistakes can create duplicate symbol definitions or missing shims. `os_generic_write_checks` adapts iterator-based APIs and must update both offset and size correctly.

**Test signals:** Build against representative old/new kernels, run dentry submount tests under rename pressure, test BDI registration/unregistration, validate write-check behavior, and exercise fallback cache creation signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/os/OsCompat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/os/OsCompat.h -->
## sources/distributed-fs/beegfs/client_module/source/os/OsCompat.h

**Purpose:** Declares and defines kernel-version compatibility wrappers for VFS permissions, writeback errors, ACL xattrs, page completion, iterator write checks, rbtree traversal, umask, mmap locks, inode locks, access checks, and RDMA NUMA node lookup.

**Important APIs/types/functions:** Provides `fhgfs_set_wb_error`, `os_generic_permission`, `os_inode_permission`, `is_32bit_api`, UID/GID accessors for older kernels, `OsCompat_initKmemCache` prototypes, list/rbtree fallback macros, `os_posix_acl_from_xattr`, `os_posix_acl_to_xattr`, `page_endio`, `os_generic_write_checks`, `beegfs_hasMappings`, `os_inode_lock`, `os_inode_unlock`, `os_access_ok`, and optional `ibdev_to_node`.

**Control flow:** Most helpers select the correct kernel API variant using feature macros. Permission helpers choose idmapped mount, user-namespace mount, or legacy signatures. Page completion records mapping-level writeback errors and completes read/write pages appropriately.

**State and persistence behavior:** The header itself stores no state. Its wrappers manipulate kernel state such as inode permissions, mapping writeback error sequences, page uptodate/writeback flags, and mmap/inode locks.

**Dependencies and integration points:** Included widely by BeeGFS filesystem code. Integrates with Linux VFS, ACL, mmap, writeback, namespace/idmap, RDMA, and list/rbtree APIs.

**Risks:** Permission wrappers must be used in the right context; `os_inode_permission` is documented for helpers/ioctls and direct `generic_permission` should remain inside `->permission` paths to avoid recursion. Writeback error migration from page flags to `mapping_set_error` must be consistent with wait/check callers. Compile-time feature detection must track kernel API changes precisely.

**Test signals:** Compile against kernels before and after idmapped mounts, Linux 6.12 writeback changes, iterator write-check changes, mmap tree layout changes, inode lock renames, and RDMA header moves. Runtime tests should cover permission checks on idmapped mounts, page read/write error propagation, and mmap mapping detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/os/OsCompat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/os/OsDeps.c -->
## sources/distributed-fs/beegfs/client_module/source/os/OsDeps.c

**Purpose:** Provides debug-only operating-system dependent stack trace helpers for the BeeGFS kernel client.

**Important APIs/types/functions:** Under `BEEGFS_DEBUG`, defines `os_saveStackTrace`, `os_freeStackTrace`, and `os_printStackTrace`. When stacktrace support or compatible architecture support is missing, stubs return NULL or print a support warning.

**Control flow:** On supported debug kernels, `os_saveStackTrace` allocates a `struct stack_trace` plus entries array with `GFP_NOFS`, skips its own frame, and calls `save_stack_trace`. The print helper selects `print_stack_trace` or `stack_trace_print` based on feature macros. Free releases both allocations.

**State and persistence behavior:** Stack traces are transient heap allocations owned by callers. No persistent state is stored.

**Dependencies and integration points:** Used by debug code such as `NoAllocBufferStore` to record which task acquired a buffer and diagnose recursive/deadlocking buffer-store use.

**Risks:** The implementation is disabled for `CONFIG_ARCH_STACKWALK` because newer stack walking APIs differ; debug diagnostics may silently degrade. Allocation failures return NULL and callers must tolerate missing traces. These helpers are debug-only and should not be relied on for production behavior.

**Test signals:** Build debug and non-debug configurations, with and without `CONFIG_STACKTRACE` and `CONFIG_ARCH_STACKWALK`; verify saved traces are printed and freed by buffer-store debug paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/os/OsDeps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/os/OsDeps.h -->
## sources/distributed-fs/beegfs/client_module/source/os/OsDeps.h

**Purpose:** Declares OS-dependent utility helpers and inline allocation/string wrappers used throughout the kernel client.

**Important APIs/types/functions:** In debug builds declares stack-trace helpers. Defines `os_kmalloc`, `os_kzalloc`, and `os_strnicmp`.

**Control flow:** Allocation wrappers first attempt `kmalloc`/`kzalloc` with `GFP_NOFS`; if allocation fails, they log a warning and retry with `__GFP_NOFAIL`. `os_strnicmp` uses `strnicmp` when available, otherwise `strncasecmp`.

**State and persistence behavior:** No state is stored. Allocation wrappers can block indefinitely on no-fail retry, which is an intentional emergency behavior for call sites that cannot handle NULL.

**Dependencies and integration points:** Included by many BeeGFS kernel client files, especially constructors and small data-structure helpers. Relies on `FhgfsOps_versions.h` feature macros and core kernel module/slab headers.

**Risks:** `__GFP_NOFAIL` in `GFP_NOFS` context can cause long stalls under memory pressure; call sites using these wrappers may assume success and skip NULL handling. The warning uses `%d` for size after cast to int, truncating very large sizes in diagnostics.

**Test signals:** Low-memory/fault-injection tests should validate that critical paths tolerate stalls, constructors work with wrapper allocations, and string comparison behavior is stable across kernel versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/os/OsDeps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/os/OsTypeConversion.h -->
## sources/distributed-fs/beegfs/client_module/source/os/OsTypeConversion.h

**Purpose:** Provides inline conversions between Linux/VFS types and BeeGFS protocol/internal types for open flags, directory entry types, and file lock types.

**Important APIs/types/functions:** Defines `OsTypeConv_openFlagsOsToFhgfs`, `OsTypeConv_dirEntryTypeToOS`, and `OsTypeConv_flockTypeToFhgfs`.

**Control flow:** Open flags map `O_RDWR`, `O_WRONLY`, default read, append, truncation, direct, sync, and nonblocking to `OPENFILE_ACCESS_*` flags. Paged write-only opens are upgraded to read-write to support read-modify-write page updates. Directory entry types map BeeGFS file kinds to `DT_*`. Lock conversion maps `F_RDLCK`/`F_WRLCK`/other to shared/exclusive/unlock and sets `ENTRYLOCKTYPE_NOWAIT` when `FL_SLEEP` is absent.

**State and persistence behavior:** No state is stored; these conversions affect subsequent remote open/lock RPC semantics.

**Dependencies and integration points:** Depends on BeeGFS storage definitions, time/common helpers, Linux fs/filelock headers, and `FhgfsCommon_getFileLockType/Flags`. Used by VFS open, readdir, and lock paths before calling remoting.

**Risks:** Incorrect flag mapping changes server-side handle permissions or lock blocking behavior. The paged-mode write-only upgrade is necessary for page-cache correctness but may surprise tests expecting strict write-only handles. Unknown directory entry types intentionally return `DT_UNKNOWN`.

**Test signals:** Test all open flag combinations including paged write-only, nonblocking, direct/sync, all BeeGFS dir entry kinds, and POSIX lock conversions with/without `FL_SLEEP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/os/OsTypeConversion.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/os/atomic64.c -->
## sources/distributed-fs/beegfs/client_module/source/os/atomic64.c

**Purpose:** Supplies a fallback generic 64-bit atomic implementation for kernels/architectures that do not provide `atomic64_t`.

**Important APIs/types/functions:** When `ATOMIC64_INIT` is absent, implements `atomic64_read`, `atomic64_set`, `atomic64_add`, `atomic64_add_return`, `atomic64_sub`, `atomic64_sub_return`, `atomic64_dec_if_positive`, `atomic64_cmpxchg`, `atomic64_xchg`, and `atomic64_add_unless`.

**Control flow:** Each operation obtains the per-object spinlock from `lock_addr`, disables interrupts with `spin_lock_irqsave`, reads/modifies `counter`, and unlocks with saved flags. The BeeGFS version uses a lock embedded in each `atomic64_t` rather than the upstream hashed lock table.

**State and persistence behavior:** State lives in each fallback `atomic64_t` as a `long long counter` plus `spinlock_t lock`. No global state is used in the active BeeGFS fallback path.

**Dependencies and integration points:** Included only on kernels lacking native atomic64 support. The companion header defines the fallback type and `atomic_init`. Any BeeGFS code using atomic64 APIs relies on either native kernel definitions or these functions.

**Risks:** The fallback is slower than native atomic instructions and depends on every object being initialized with `atomic_init` so the embedded spinlock is valid. Because it is conditionally compiled, build coverage on modern kernels will not exercise it.

**Test signals:** Build on a configuration without `ATOMIC64_INIT`, run concurrent increment/decrement/cmpxchg/add-unless tests, verify interrupt-safe locking under lockdep, and ensure all fallback atomic64 objects are initialized before use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/os/atomic64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/os/atomic64.h -->
## sources/distributed-fs/beegfs/client_module/source/os/atomic64.h

**Purpose:** Declares the fallback `atomic64_t` type and operation prototypes/macros for kernels that lack native 64-bit atomics.

**Important APIs/types/functions:** Defines fallback `atomic64_t` with `counter` and `spinlock_t lock`, declares all atomic64 operations implemented in `atomic64.c`, defines convenience macros such as `atomic64_inc`, `atomic64_dec`, and `atomic64_inc_not_zero`, and provides `atomic_init`.

**Control flow:** On kernels with native `ATOMIC64_INIT`, the file contributes nothing. Otherwise, callers use the familiar atomic64 API and the fallback implementation handles locking.

**State and persistence behavior:** Each atomic object stores its own counter and lock. `atomic_init` initializes both, replacing disabled upstream `ATOMIC64_INIT`.

**Dependencies and integration points:** Depends on `asm/atomic.h` feature availability and kernel spinlocks. It provides compatibility for BeeGFS modules built on older or weaker architectures.

**Risks:** The fallback `atomic_init` name may collide conceptually with generic atomic initialization APIs on some kernels, though it is only compiled in the missing-atomic64 path. Static initialization via `ATOMIC64_INIT` is intentionally unavailable in this fallback, so all objects need runtime initialization.

**Test signals:** Compile fallback and native paths, validate macro semantics, and audit all atomic64 users for explicit initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/os/atomic64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/os/iov_iter.c -->
## sources/distributed-fs/beegfs/client_module/source/os/iov_iter.c

**Purpose:** Implements `BeeGFS_ReadSink`, a helper that converts difficult read destinations, especially pipe iterators, into safe bvec-backed iterators for parallel BeeGFS storage reads.

**Important APIs/types/functions:** Provides `beegfs_readsink_reserve` and `beegfs_readsink_release`, with internal `beegfs_readsink_reserve_no_pipe`, `compute_max_pagecount`, and `beegfs_readsink_reserve_pipe` when pipe iterators are supported.

**Control flow:** Non-pipe iterators are copied and truncated to the requested size. Pipe iterators allocate page and bio_vec arrays, call `iov_iter_get_pages` or `iov_iter_get_pages2`, build a `bio_vec` view over returned pages, and initialize `sanitized_iter` as an `ITER_BVEC`. Release puts every reserved page, frees arrays, and zeroes the struct.

**State and persistence behavior:** The read sink temporarily owns page references and metadata arrays between reserve and release. It does not advance the original iterator; callers advance the original after completed reads.

**Dependencies and integration points:** Used by `FhgfsOpsRemoting_readfileVec` before splitting reads across stripe targets. Depends on kernel `iov_iter`, pages, bvecs, slab allocation, and feature macros for pipe and `iov_iter_get_pages2`.

**Risks:** Low-memory allocation failure leaves a sanitized iterator with count zero, so callers must handle empty state. A failed second allocation leaks the first allocation until release is called, which the intended call pattern does. Pipe iterator APIs can auto-advance in newer kernels, so the code copies the iterator for `get_pages2` to avoid double-advancement.

**Test signals:** Read into normal iovec, kvec, bvec, and pipe destinations; force allocation failures; verify page refs are released; validate no double advancement with `iov_iter_get_pages2`; and exercise partial reserve sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/os/iov_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/os/iov_iter.h -->
## sources/distributed-fs/beegfs/client_module/source/os/iov_iter.h

**Purpose:** Provides kernel-version shims and BeeGFS convenience helpers for `iov_iter` use, plus the `BeeGFS_ReadSink` structure declaration.

**Important APIs/types/functions:** Defines iterator feature requirements, shims for `iter_iov_addr`, `iter_iov_len`, `iov_iter_type`, `iov_iter_is_pipe`, wrappers `BEEGFS_IOV_ITER_KVEC` and `BEEGFS_IOV_ITER_BVEC`, stack allocation macros `STACK_ALLOC_BEEGFS_ITER_IOV`/`KVEC`, and internal initializer helpers.

**Control flow:** Callers create one-segment user or kernel iterators through stack macros, inspect iterator type/count/segments through wrappers, and use `BeeGFS_ReadSink` for pipe-safe reads. The direction/type flag handling adapts kernels that include or exclude iterator type flags in the direction parameter.

**State and persistence behavior:** The header defines transient iterator construction only. `BeeGFS_ReadSink` contains temporary page/bvec arrays and a sanitized iterator, managed by functions in `iov_iter.c`.

**Dependencies and integration points:** Required by remoting read/write wrappers and storage commkit code. It depends on kernel uio/uaccess/bvec APIs and BeeGFS feature macros.

**Risks:** The stack macros return pointers to compound literals and must be used only within the full expression/scope where those literals live. Compile-time `#error` guards intentionally reject kernels lacking required iterator features. Direction/type flag compatibility is subtle across kernel releases.

**Test signals:** Build on supported kernels before and after iterator API changes, run stack-macro read/write wrapper tests, pipe read tests, and static analysis for escaping stack iterator pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/os/iov_iter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/program/Main.c -->
## sources/distributed-fs/beegfs/client_module/source/program/Main.c

**Purpose:** Defines the BeeGFS kernel client module entry and exit routines, including subsystem initialization, filesystem registration, procfs setup, and cleanup.

**Important APIs/types/functions:** `init_fhgfs_client` is registered with `module_init`; `exit_fhgfs_client` is registered with `module_exit`. The file also declares module license, description, author, alias, and version metadata.

**Control flow:** Initialization uses a fail-label cascade: fault injection, native emergency pools, commkit emergency pools, socket one-time init, inode cache, RWPages workqueue, remoting message buffers, page-list vector cache, filesystem registration, and procfs creation. On any failure it unwinds only the subsystems already initialized. Exit performs the reverse cleanup order and asserts filesystem unregister succeeds.

**State and persistence behavior:** Module load creates kernel caches, pools, workqueues, socket state, procfs entries, and filesystem registration. Unload destroys them. No on-disk state is written here.

**Dependencies and integration points:** Integrates all major client module subsystems: fault injection, native IO, commkit, sockets, inode/page caches, remoting, procfs, and VFS registration.

**Risks:** Initialization order is a contract: later subsystems may assume earlier pools/caches exist. Cleanup labels must remain synchronized with added initialization steps. Returning `-EPERM` for all init failures loses specific error detail. `BUG_ON` during unregister can panic if teardown invariants are violated.

**Test signals:** Test module load/unload, forced failure at each initialization step, double-load prevention through kernel module machinery, procfs creation/removal, filesystem mount after registration, and leak checks for all pools/caches/workqueues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/program/Main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/BitStore.c -->
## sources/distributed-fs/beegfs/client_module/source/toolkit/BitStore.c

**Purpose:** Implements a dynamically sizable bit-vector used by the client for compact flags such as per-stripe first-write tracking.

**Important APIs/types/functions:** Implements `BitStore_setBit`, `setSize`, `clearBits`, `serialize`, `deserializePreprocess`, `deserialize`, `copy`, and `copyThreadSafe`.

**Control flow:** Bits are stored in `lowerBits` for the first machine word and optional `higherBits` for additional blocks. `setBit` bounds-checks then uses atomic kernel bit operations. `setSize` frees/reallocates higher blocks when block count changes and rounds `numBits` to full block capacity. Serialization writes bit count, 8-byte alignment padding, lower/higher blocks, and extra 32-bit padding when needed for cross-arch compatibility. Preprocess validates serialized length and advances the deserialize context.

**State and persistence behavior:** In-memory state is `numBits`, `lowerBits`, and optional `higherBits`. Serialized format is stable across 32/64-bit block size differences by using full 64-bit aligned blocks. `setSize` does not preserve or initialize existing bits; callers usually clear after resizing.

**Dependencies and integration points:** Depends on BeeGFS serialization helpers and `os_kmalloc`. Used by remoting IO handle state to track whether each stripe target has seen its first write.

**Risks:** Thread-safe copy intentionally does not resize and may truncate if destination has fewer blocks. `copy` assumes destination allocation succeeds through no-fail wrappers. `getBit` returns false out of range while `setBit` triggers a bug macro. Serialization/deserialization must stay compatible across word sizes and endianness assumptions in serialization helpers.

**Test signals:** Test set/get/clear across lower and higher blocks, resizing up/down, serialization round-trips on 32-bit and 64-bit builds, malformed deserialize lengths, copy truncation behavior, and concurrent bit set/get paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/BitStore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/BitStore.h -->
## sources/distributed-fs/beegfs/client_module/source/toolkit/BitStore.h

**Purpose:** Declares the `BitStore` bit-vector structure and inline helpers for construction, destruction, bit lookup, and bit-index arithmetic.

**Important APIs/types/functions:** Defines `bitstore_store_type`, block-size constants, `struct BitStore`, inline `BitStore_init`, `initWithSizeAndReset`, `uninit`, `getBit`, `getBitBlockIndex`, `getBitIndexInBitBlock`, and `calculateBitBlockCount`, plus external mutating/serialization functions.

**Control flow:** Callers initialize with a default one-block capacity, optionally resize/reset, perform atomic bit lookups via `test_bit`, and uninitialize optional heap storage.

**State and persistence behavior:** Stores a rounded capacity in `numBits`, one inline lower block, and optional heap-backed higher blocks. The header's inline `getBit` treats out-of-range reads as false.

**Dependencies and integration points:** Used anywhere compact dynamic bitsets are needed, notably `RemotingIOInfo.firstWriteDone`. Depends on BeeGFS common macros and serialization types.

**Risks:** `BitStore_init(this, false)` leaves `lowerBits` uninitialized until callers clear or deserialize. `BitStore_uninit` frees `higherBits` without nulling, so destroyed objects must not be reused without reinit. The block type is machine word sized, so serialized compatibility relies on `.c` conversion logic.

**Test signals:** Build with debug bug macros, test initialized-without-clear paths for callers, validate block index math around word boundaries, and run leak/use-after-free checks for init/uninit cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/BitStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/FhgfsChunkPageVec.c -->
## sources/distributed-fs/beegfs/client_module/source/toolkit/FhgfsChunkPageVec.c

**Purpose:** Implements error-completion helpers for `FhgfsChunkPageVec`, a page-vector abstraction used by BeeGFS buffered IO.

**Important APIs/types/functions:** Provides `FhgfsChunkPageVec_iterateAllHandleWritePages` and `FhgfsChunkPageVec_iterateAllHandleReadErr`.

**Control flow:** Both helpers repeatedly call `FhgfsChunkPageVec_iterateGetNextPage`. The write helper ends writeback for each page through `FhgfsOpsPages_endWritePage` with the supplied Linux error code. The read-error helper unmaps, unlocks, and releases each page through `FhgfsPage_unmapUnlockReleaseFhgfsPage`.

**State and persistence behavior:** These functions consume the vector's iterator state. They do not persist data; they finalize page state after failed or remaining IO.

**Dependencies and integration points:** Called by remoting page-vector IO when allocation or communication fails and pages must not remain locked or under writeback. Depends on `FhgfsOpsPages` and `FhgfsPage` helpers.

**Risks:** Because iteration state advances, callers needing another pass must reset the iterator. Passing the wrong error sign to write completion would record incorrect writeback status. Missing these helpers on error paths can leave pages locked or writeback-pending.

**Test signals:** Fault-inject page-vector read/write failures and verify every page is unlocked, unmapped, released, and has expected writeback/error state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/FhgfsChunkPageVec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/FhgfsChunkPageVec.h -->
## sources/distributed-fs/beegfs/client_module/source/toolkit/FhgfsChunkPageVec.h

**Purpose:** Defines `FhgfsChunkPageVec`, a chunk-bounded list of page-vector blocks used to batch consecutive pages for BeeGFS buffered read/write operations.

**Important APIs/types/functions:** Inline APIs include create/destroy, init/uninit, `addPageListVec`, `getFirstPageListVec`, `pushPage`, `getSize`, `getInode`, `getFirstPageFileOffset`, iterator get/reset, iterator index, data-size helpers, and `_getChunkPageOffset`.

**Control flow:** Initialization creates the first `FhgfsPageListVec`, using a mempool for the first allocation if supplied. `pushPage` rejects full vectors and non-consecutive page indexes, appends to the current list-vector, allocates another list-vector if full, initializes first-page offsets/chunk offset, and tracks last-page size. Iteration walks list-vector entries and resets only when explicitly requested.

**State and persistence behavior:** State is transient in-memory page references, mapped page data pointers held in child `FhgfsPageListVec` entries, file/page indexes, chunk offset, and iterator cursors. Uninit destroys all list-vector blocks but page release/unmap is handled by IO completion helpers rather than this destructor alone.

**Dependencies and integration points:** Integrates `FhgfsPage`, `FhgfsPageListVec`, kernel mempools/slab caches, inode/page APIs, and remoting page-vector IO.

**Risks:** `_getChunkPageOffset` assumes `numChunkPages` is a power of two. `getDataSize` and `getRemainingDataSize` assume `size`/remaining pages are nonzero. The mempool pointer is stored only when first allocation used it; destroy must free all blocks through the right allocator. Non-consecutive pages are refused, so callers must split batches correctly.

**Test signals:** Test page pushing across list-vector boundaries, full chunk refusal, non-consecutive refusal, first-page offset/chunk offset, iterator reset, error cleanup, debug-mode forced allocation failures, and power-of-two chunk assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/FhgfsChunkPageVec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/FhgfsPage.h -->
## sources/distributed-fs/beegfs/client_module/source/toolkit/FhgfsPage.h

**Purpose:** Defines a small wrapper around a kernel `struct page` with mapped data and used length for BeeGFS page-vector IO.

**Important APIs/types/functions:** Defines `struct FhgfsPage` and inline helpers `FhgfsPage_unmapUnlockReleasePage`, `FhgfsPage_unmapUnlockReleaseFhgfsPage`, `getFileOffset`, `zeroPage`, and `getPageIndex`.

**Control flow:** Page-list code maps pages with `kmap`; cleanup helpers `kunmap`, unlock, and `put_page`. Offset/index helpers read kernel page metadata. `zeroPage` clears the entire mapped page data.

**State and persistence behavior:** Holds a borrowed/referenced page pointer, mapping address, and used byte count. Page contents are real filesystem data; helper state is transient.

**Dependencies and integration points:** Used by `FhgfsPageListVec`, `FhgfsChunkPageVec`, remoting page IO, and buffered read/write completion paths.

**Risks:** Cleanup assumes the page was kmapped and locked and has a held reference. Calling cleanup twice or on an unmapped page would corrupt page state. `zeroPage` clears the full page, so callers must ensure that is intended for partial-page handling.

**Test signals:** Validate map/unmap/unlock/refcount lifecycle, page offset/index values, zeroing behavior for partial pages, and error cleanup idempotence expectations in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/FhgfsPage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/FhgfsPageListVec.h -->
## sources/distributed-fs/beegfs/client_module/source/toolkit/FhgfsPageListVec.h

**Purpose:** Defines a fixed-size page-vector block containing `FhgfsPage` entries, linked into larger chunk page vectors.

**Important APIs/types/functions:** Defines `BEEGFS_LIST_VEC_MAX_PAGES`, `struct FhgfsPageListVec`, and inline create/destroy/init/uninit, `pushPage`, `getMaxPages`, and `getFhgfsPage`.

**Control flow:** Creation first tries slab-cache allocation and, if provided and necessary, falls back to a mempool allocation for guaranteed first vector availability. Debug builds intentionally simulate allocation failure on odd `jiffies`. `pushPage` maps the page with `kmap`, stores page/data/length, and increments `usedPages`.

**State and persistence behavior:** Each block stores up to 16 pages in debug builds or 32 normally, plus list linkage. It owns allocation of the block object but not final page release; page lifecycle is completed by chunk/page IO helpers.

**Dependencies and integration points:** Used exclusively by `FhgfsChunkPageVec` and page IO paths. Depends on kernel mempool, slab cache, list, and kmap APIs.

**Risks:** Destroy chooses mempool free if a pool pointer is supplied, not per-object allocation provenance; the parent must pass the correct allocator context. `getFhgfsPage` has no bounds check. Debug allocation failure changes timing and must not trigger false production assumptions.

**Test signals:** Test slab and mempool allocation paths, push up to capacity and refusal after capacity, kmap/unmap lifecycle through parent cleanup, and debug failure simulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/FhgfsPageListVec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/InodeRefStore.c -->
## sources/distributed-fs/beegfs/client_module/source/toolkit/InodeRefStore.c

**Purpose:** Provides the pointer comparator used by `InodeRefStore`'s red-black tree.

**Important APIs/types/functions:** Implements `__InodeRefStore_keyComparator`, ordering inode pointer keys by address.

**Control flow:** Returns -1, 0, or 1 based on raw pointer comparison.

**State and persistence behavior:** No state is stored in this file.

**Dependencies and integration points:** The comparator is passed to `PointerRBTree_init` in `InodeRefStore_init` and determines ordering for inode reference tracking.

**Risks:** Ordering by pointer address is suitable only for identity, not inode number or lifetime ordering. Reused inode memory addresses after removal are fine because the store holds references while entries exist.

**Test signals:** Tree insertion/removal tests should confirm duplicate pointer detection and stable iteration ordering while references are held.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/InodeRefStore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/InodeRefStore.h -->
## sources/distributed-fs/beegfs/client_module/source/toolkit/InodeRefStore.h

**Purpose:** Defines a mutex-protected inode reference store for async cache flush and similar workflows that need to hold at most one reference per inode.

**Important APIs/types/functions:** Defines `struct InodeRefStore` containing a pointer RB tree and mutex. Inline APIs include init/construct/uninit/destruct, `addAndReferenceInode`, `addOrPutInode`, `getAndRemoveFirstInode`, `getAndRemoveNextInode`, `removeAndReleaseInode`, and `getSize`.

**Control flow:** Add-and-reference inserts only if absent, then calls `ihold` inside the mutex. Add-or-put assumes caller already has a reference and drops it with `iput` if the inode is already present. Get-and-remove returns an inode without dropping the held reference, transferring release responsibility to caller. Next-iteration can temporarily insert the old inode pointer as a search key when it is no longer in the tree.

**State and persistence behavior:** The store persists only transient inode references in memory. Uninit iterates all remaining entries and calls `iput`, then destroys the tree and mutex.

**Dependencies and integration points:** Depends on `PointerRBTree`, `Mutex`, kernel inode reference APIs, and `os_kmalloc`. Used by async flushing or cache invalidation logic outside this subset.

**Risks:** Caller ownership differs by method: removed returned inodes still need `iput`, while explicit remove releases immediately. Temporary insertion in `getAndRemoveNextInode` must not call `ihold` and relies on pointer ordering only. Holding `iput` inside the mutex avoids races but may have side effects if final inode teardown is expensive.

**Test signals:** Test duplicate insertion, add-or-put reference balancing, iteration/removal order, remove-and-release races with add, uninit releasing leftovers, and lockdep behavior around `iput`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/InodeRefStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/NoAllocBufferStore.c -->
## sources/distributed-fs/beegfs/client_module/source/toolkit/NoAllocBufferStore.c

**Purpose:** Implements a fixed-size buffer pool that allocates all buffers during initialization and performs no memory allocation during normal get/put operations.

**Important APIs/types/functions:** Implements lifecycle functions, `NoAllocBufferStore_waitForBuf`, `instantBuf`, `addBuf`, internal `__NoAllocBufferStore_initBuffers`, getters for availability/size, and debug-only task tracking helpers.

**Control flow:** Initialization allocates the pointer array and `vmalloc`s each buffer, then marks all buffers available. `waitForBuf` locks, checks debug recursive-use state, waits on a condition while empty, pops a buffer, records debug ownership, and unlocks. `instantBuf` returns NULL if empty without waiting. `addBuf` validates non-NULL, signals waiters, pushes the buffer, removes debug ownership, and unlocks.

**State and persistence behavior:** State includes buffer pointer stack, total count, buffer size, available count, mutex, condition variable, and optional debug RB tree keyed by task PID with stack traces. Buffers exist only for module/runtime lifetime and are freed on uninit.

**Dependencies and integration points:** Used by IO paths that need emergency/no-allocation buffers. Depends on BeeGFS mutex/condition wrappers, `vmalloc`/`vfree`, pointer RB trees, current task PID, and debug stack trace helpers from `OsDeps`.

**Risks:** `addBuf` does not bounds-check `numAvailable` against `numBufs`, so double-return can corrupt the stack. `uninit` frees only currently available buffers; buffers still checked out at teardown leak or worse. `waitForBuf` can deadlock if a task recursively waits while holding a buffer; debug mode detects this. Init error cleanup frees all array entries but leaves pointer array cleanup to caller path.

**Test signals:** Test pool init/uninit with zero and nonzero buffers, blocking wait/wakeup, instant empty behavior, double-add detection expectations, checked-out buffer teardown, debug recursive acquisition warnings, and allocation failure during init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/NoAllocBufferStore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/NoAllocBufferStore.h -->
## sources/distributed-fs/beegfs/client_module/source/toolkit/NoAllocBufferStore.h

**Purpose:** Declares the no-allocation buffer pool interface for BeeGFS client code.

**Important APIs/types/functions:** Declares opaque `NoAllocBufferStore`, lifecycle functions, blocking and nonblocking buffer acquisition, buffer return, `getNumAvailable`, and `getBufSize`.

**Control flow:** Callers initialize/construct the store with a fixed buffer count and size, borrow buffers through `waitForBuf` or `instantBuf`, return them through `addBuf`, and destroy the store only when all buffers are returned.

**State and persistence behavior:** The header hides internal state. Runtime state is a finite pool of `vmalloc` buffers with no normal-path allocation.

**Dependencies and integration points:** Includes BeeGFS thread primitives and common definitions. Used by networking/IO code that needs bounded emergency buffers.

**Risks:** The opaque interface cannot enforce return discipline. `waitForBuf` may sleep, so it must not be called from atomic contexts. Callers must not return foreign or duplicate buffers.

**Test signals:** Compile users for sleep-context correctness, validate all borrowed buffers are returned before destruction, and stress concurrent get/put operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/NoAllocBufferStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/StatFsCache.c -->
## sources/distributed-fs/beegfs/client_module/source/toolkit/StatFsCache.c

**Purpose:** Implements a small cache for `statfs` free-space totals to avoid querying every storage target on each syscall.

**Important APIs/types/functions:** Implements `StatFsCache_getFreeSpace`.

**Control flow:** Reads `tuneStatFsCacheSecs` from config. If caching is enabled and `lastUpdateTime` is nonzero and not expired, returns cached total/free values under the read lock. Otherwise it releases the lock, calls `FhgfsOpsRemoting_statStoragePath` with `ignoreErrors=true`, zeroes outputs on failure, and on success updates cached values/time under the write lock.

**State and persistence behavior:** Caches total/free byte counts and last update time in memory. Values are approximate and may be concurrently refreshed by multiple threads; the code intentionally allows racing remote calls and last-writer-wins cache updates.

**Dependencies and integration points:** Depends on `App` config and `FhgfsOpsRemoting_statStoragePath`, which aggregates storage target stats. Used by VFS statfs handling.

**Risks:** Cache staleness is controlled only by config seconds and may hide fast capacity changes. Ignoring per-target errors can produce partial totals. Concurrent misses can fan out multiple expensive stat-storage requests. Failed refresh clears caller outputs but does not invalidate old cached values explicitly.

**Test signals:** Test disabled cache, first miss, hit before expiry, refresh after expiry, remoting failure, partial target errors, and concurrent statfs calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/StatFsCache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/StatFsCache.h -->
## sources/distributed-fs/beegfs/client_module/source/toolkit/StatFsCache.h

**Purpose:** Declares and defines the `StatFsCache` structure and lifecycle helpers for cached filesystem free-space reporting.

**Important APIs/types/functions:** Defines `struct StatFsCache` with `App*`, `RWLock`, `Time lastUpdateTime`, `cachedSizeTotal`, and `cachedSizeFree`. Inline APIs include `StatFsCache_init`, `construct`, and `destruct`; external API is `StatFsCache_getFreeSpace`.

**Control flow:** Construction allocates and initializes lock/time state. Consumers call `getFreeSpace` to obtain cached or freshly queried totals. Destruction frees the wrapper object.

**State and persistence behavior:** State is in-memory only and starts with zero time to mark the cache uninitialized. Cached totals are stored in bytes.

**Dependencies and integration points:** Depends on BeeGFS storage errors, `RWLock`, `Time`, and `os_kmalloc`. Integrated into filesystem statfs paths through the app object.

**Risks:** `StatFsCache_destruct` frees without explicit lock uninit; this relies on `RWLock` not requiring teardown or on module conventions. Callers must not use the cache after `App` teardown. Cache validity depends on configuration read by the `.c` implementation.

**Test signals:** Construct/destruct under leak checking, verify zero-time initial miss, test cached byte outputs, and run lockdep around concurrent statfs access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/toolkit/StatFsCache.h -->
