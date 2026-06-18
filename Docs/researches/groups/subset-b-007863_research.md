# subset-b-007863 Research

Grouped research for the OrangeFS kernel/VFS and protocol encoding files assigned to `subset-b-007863`. Each file section preserves the original source path for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/super.c -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/super.c

## Purpose
Implements OrangeFS/PVFS2 Linux superblock operations, mount/remount/unmount handling, inode allocation/destruction hooks, statfs forwarding, export file-handle support, mount option parsing, and optional filesystem key caching. It is the main bridge between Linux VFS superblock lifecycle callbacks and the user-space `pvfs2-client-core` service-operation channel.

## Important APIs, Types, and Functions
Key exported or externally referenced entry points include `pvfs2_s_ops`, `pvfs2_read_inode`, `pvfs2_remount`, `pvfs2_fill_sb`, version-dependent `pvfs2_get_sb`/`pvfs2_mount`, `pvfs2_kill_sb`, and optional `fsid_key_table_initialize`/`fsid_key_table_finalize`. Internal helpers include `parse_mount_options`, `pvfs2_alloc_inode`, `pvfs2_destroy_inode`, `pvfs2_statfs`, `pvfs2_statfs_lite`, `pvfs2_dirty_inode`, `pvfs2_flush_sb`, and optional export helpers `pvfs2_fh_to_dentry`/`pvfs2_encode_fh`. The file depends heavily on `pvfs2_sb_info_t`, `pvfs2_mount_sb_info_t`, `pvfs2_kernel_op_t`, `PVFS_object_kref`, Linux `struct super_block`, `struct inode`, `struct dentry`, and conditional kernel-version macros.

## Control Flow
Mounting starts by sending `PVFS2_VFS_OP_FS_MOUNT` through `service_operation`, validating returned `fs_id` and root handle, then passing temporary mount metadata to `pvfs2_fill_sb`. `pvfs2_fill_sb` allocates `s_fs_info`, parses options, configures flags and xattr handlers, initializes VFS superblock fields, constructs the root inode via `pvfs2_get_custom_core_inode`, creates the root dentry, and installs export operations. Remount from VFS only reparses options and updates flags; `pvfs2_remount` additionally reissues a priority mount upcall so a restarted client core can rebuild mount state. `pvfs2_statfs` allocates a statfs operation, sends it to userspace, and copies returned capacity counters into `kstatfs`, truncating for older 32-bit `statfs` layouts when necessary. Unmount calls `pvfs2_flush_sb`, `pvfs2_unmount_sb`, removes the superblock from the global list, prunes dcache, runs generic cleanup, checks inode allocation counters, and frees private superblock data.

## State and Persistence
Persistent in-kernel state includes `pvfs2_superblocks`, private `PVFS2_SB(sb)` fields such as `root_khandle`, `fs_id`, `id`, `devname`, saved mount `data`, `mnt_options`, `mount_pending`, and inode allocation counters. Optional fs-key support maintains a module-lifetime `qhash_table` keyed by `PVFS_fs_id`; entries are created lazily via `PVFS2_VFS_OP_FSKEY` and released at module finalize. The file does not persist data to disk; it mirrors remote filesystem state and client-core mount identity inside kernel memory.

## Dependencies and Integration Points
This file integrates VFS super operations, OrangeFS inode helpers, dentry operations, xattr handler registration, bufmap size queries, export/NFS callbacks, global superblock list helpers, and the request queue service path in `waitqueue.c`. It also depends on client-core semantics for mount, remount, statfs, unmount, and fs-key upcalls.

## Risks
Mount option parsing uses a static options array and fixed-length copies; overflow checks exist but concurrent mounts share the static parser buffer. Error paths after partial `s_fs_info` allocation can leak private data in some branches. Fs-key cache access is not visibly protected by a lock in this file. File-handle encoding has compatibility branches and a suspicious connectable dentry variant that sets `len = 6` after writing parent data through `fh[9]`, so NFS export behavior needs focused coverage. Unmount manually calls both `kill_litter_super` and `dput(sb->s_root)` in some configurations, which is sensitive to kernel API expectations.

## Test Signals
Exercise successful and failed mounts with valid and invalid config servers, mount options `intr`, `acl`, `noatime`, `nodiratime`, and unsupported options. Test client-core restart remount, statfs with large counters on 32-bit-compatible paths, unmount after dirty atime updates, repeated mount/unmount leak counters, fs-key cache hit/miss behavior, and NFS file-handle encode/decode round trips when export operations are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/symlink.c -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/symlink.c

## Purpose
Defines inode operations for OrangeFS symlinks and adapts symlink-follow behavior across multiple Linux kernel `follow_link` APIs. The core behavior is to return or install `PVFS2_I(inode)->link_target` as the target path known from OrangeFS inode attributes.

## Important APIs, Types, and Functions
The file provides version-dependent `pvfs2_follow_link` implementations and the global `pvfs2_symlink_inode_operations`. The operations table wires `.readlink = generic_readlink`, `.follow_link = pvfs2_follow_link`, `.setattr = pvfs2_setattr`, `.getattr = pvfs2_getattr`, `.listxattr = pvfs2_listxattr`, and either `generic_setxattr` or `pvfs2_setxattr`. With generic ACL-capable xattrs it also installs `.permission = pvfs2_permission`.

## Control Flow
VFS symlink resolution calls `pvfs2_follow_link`. Older kernels return `vfs_follow_link(nd, link_target)`, intermediate kernels call `nd_set_link(nd, link_target)` and return `NULL`, and newer callback forms return `target` while storing it in `*cookie`. All paths read the cached link target from the OrangeFS inode-private structure and do not issue a new network request here.

## State and Persistence
No state is allocated in this file. It relies on inode-private `link_target` lifetime being valid for the symlink inode and populated by earlier getattr/lookup paths. The symlink target itself represents remote filesystem metadata cached in memory.

## Dependencies and Integration Points
Depends on `pvfs2-kernel.h`, `pvfs2-bufmap.h`, `pvfs2-internal.h`, the OrangeFS inode-private accessor `PVFS2_I`, generic VFS readlink helpers, attribute callbacks, xattr callbacks, and optional permission handling.

## Risks
The implementation trusts `link_target` to be non-NULL and properly NUL-terminated. Stale or freed targets would surface as bad path resolution. Behavior differs by kernel API, so compatibility macro coverage matters. The symlink operations table does not define `.get_link` for modern kernels, indicating this file targets old 2.6-era compatibility layers.

## Test Signals
Create and read symlinks with short, long, relative, and absolute targets; resolve symlinks after inode cache eviction; verify xattr and setattr callbacks on symlink inodes; and compile-test all supported `follow_link` macro branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/upcall.h -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/upcall.h

## Purpose
Defines the sanitized kernel-to-client-core upcall request ABI for OrangeFS Linux kernel operations. It collects fixed-width request payload structs and the top-level `pvfs2_upcall_t` union used by the kernel device/request queue to describe work for user-space servicing.

## Important APIs, Types, and Functions
The header declares request structs for I/O, lookup, create, symlink, getattr, setattr, remove, mkdir, readdir, readdirplus, rename, statfs, truncate, readahead flush, fs mount/unmount, xattr get/set/list/remove, cancel, fsync, runtime parameter get/set, performance counters, filesystem key lookup, and feature negotiation. `pvfs2_upcall_t` contains caller identity fields (`type`, `uid`, `gid`, `pid`, `tgid`), optional trailer metadata for extended I/O, and a union named `req`. Enums `pvfs2_param_request_type`, `pvfs2_param_request_op`, and `pvfs2_perf_count_request_type` define ioctl/control-plane request classes.

## Control Flow
Kernel VFS paths allocate `pvfs2_kernel_op_t` objects, fill `op->upcall.req.<operation>`, and hand them to `service_operation`. The device side exposes these fixed-layout structs to client-core, which performs the remote OrangeFS system call and later returns a matching downcall. This header does not implement flow itself; it defines the memory contract that flow depends on.

## State and Persistence
No persistent state is kept in the header. Layout is state-critical: fixed-width integers, explicit padding fields, `PVFS2_ALIGN_VAR` around trailer pointers, and bounded inline arrays such as `PVFS2_NAME_LEN` and `PVFS_MAX_XATTR_NAMELEN` are used to stabilize 32/64-bit kernel-user interactions.

## Dependencies and Integration Points
Includes `pvfs2-sysint.h` and uses shared protocol types including `PVFS_object_kref`, `PVFS_sys_attr`, `PVFS_ds_position`, `PVFS_fs_id`, `PVFS_keyval_pair`, uid/gid types, and `PVFS_size`. It is consumed by kernel operation setup code, the device file implementation, waitqueue servicing, and client-core downcall matching.

## Risks
This is an ABI-sensitive file: changing field order, type width, padding, enum values, or array sizes can break kernel/client-core compatibility. Pointer-bearing fields such as `trailer_buf` require careful translation and cannot be treated as stable user-space addresses. Request structs with inline names depend on callers enforcing NUL termination and length limits.

## Test Signals
Compile and run 32-bit kernel with 64-bit client-core compatibility tests where supported, validate each operation's upcall size and field offsets, fuzz boundary-length names/xattr keys, test parameter and perf-count requests, and exercise cancel and trailer-based readx/writex requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/upcall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/waitqueue.c -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/waitqueue.c

## Purpose
Implements in-kernel operation queuing, blocking waits, retry behavior, purge handling, and cancellation waits for OrangeFS upcalls. It is the synchronization core between VFS callers and `pvfs2-client-core` downcalls.

## Important APIs, Types, and Functions
Primary functions are `service_operation`, `wait_for_matching_downcall`, `wait_for_cancellation_downcall`, `pvfs2_clean_up_interrupted_operation`, and `purge_waiting_ops`. It manipulates `pvfs2_kernel_op_t`, global `pvfs2_request_list`, `pvfs2_request_list_lock`, `request_semaphore`, per-op wait queues and locks, the operations-in-progress hash table, `pvfs2_bufmap_init_waitq`, and operation state helpers such as `op_state_waiting`, `set_op_state_purged`, and `set_op_state_interrupted`.

## Control Flow
`service_operation` stamps process identity on the upcall, optionally masks signals, optionally enters `request_semaphore`, increments attempts if the daemon is not in service, queues the op on the normal or priority request list, and returns immediately for asynchronous operations. Synchronous calls wait either for cancellation downcall or normal matching downcall. On success the downcall status is normalized to errno format. On unserviced `-EAGAIN`, non-shared-memory operations are requeued immediately; shared-memory operations wait briefly for bufmap initialization and return `-EAGAIN` so the caller can repopulate shared buffers.

## State and Persistence
Operation state is transient but concurrency-sensitive. Ops move through waiting, in-progress, serviced, purged, and interrupted states under per-op locks and list/hash locks. `attempts` controls retry and timeout behavior. `op->downcall.status` is the persistent result visible to callers after the wait completes.

## Dependencies and Integration Points
Integrates with device close/purge behavior, client-core service status checks, request-list insertion/removal, in-progress hash removal, signal masking helpers, bufmap initialization, and VFS operations throughout the kernel module. Mount remount priority operations in `super.c` rely on `PVFS2_OP_PRIORITY` and `PVFS2_OP_NO_SEMAPHORE` behavior here.

## Risks
Lock ordering is explicitly sensitive: cleanup locks op first, then list/hash helpers, while purge scans under request-list lock and then op lock. Incorrect changes can deadlock. Signal masking must be balanced on every exit. Timeout/retry paths can return `-EAGAIN`, `-EIO`, `-EINTR`, or `-ETIMEDOUT`; callers must handle each correctly. Shared-memory restart handling depends on `get_bufmap_init()` and can fail user I/O after the configured wait.

## Test Signals
Test normal lookup/getattr/statfs service, signal interruption of interruptible and non-interruptible operations, client-core shutdown purge and restart, repeated purge retry limit, cancellation requests with pending signals, daemon-not-in-service timeout behavior, priority remount ordering, and shared-memory operation recovery after bufmap reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/waitqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/xattr-default.c -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/xattr-default.c

## Purpose
Implements the generic/default extended attribute namespace handler for OrangeFS, including unprefixed xattr names. It maps Linux xattr get/set callbacks to OrangeFS inode xattr operations using `PVFS2_XATTR_NAME_DEFAULT_PREFIX`.

## Important APIs, Types, and Functions
Provides `pvfs2_xattr_set_default`, `pvfs2_xattr_get_default`, and, for generic xattr kernels, `pvfs2_xattr_default_handler`. Callback signatures are selected by kernel feature macros covering 4.4-style handler arguments, 2.6.33-style handler flags, and older inode-based callbacks. It calls `convert_to_internal_xattr_flags`, `pvfs2_inode_setxattr`, and `pvfs2_inode_getxattr`.

## Control Flow
Set rejects an empty xattr name, denies operation unless the inode is a regular file or a non-sticky directory, converts Linux create/replace flags to internal flags, and forwards prefix/name/value/size to the inode-level setter. Get rejects empty names and forwards prefix/name/buffer/size to the inode-level getter.

## State and Persistence
No local state is stored. Successful operations persist xattr key/value state in the remote OrangeFS object through inode-level upcalls. The handler object is static registration metadata for the VFS.

## Dependencies and Integration Points
Compiled only under `HAVE_XATTR`; the handler is used by `xattr.c` and by `super.c` when it installs `sb->s_xattr = pvfs2_xattr_handlers`. It depends on VFS mode bits, sticky directory semantics, Linux xattr flags, and OrangeFS xattr prefix constants.

## Risks
The default handler deliberately catches empty-prefix names, so prefix routing order in `pvfs2_xattr_handlers` is important. Permission policy is local and narrow: sticky directories are denied, but other access checks depend on higher VFS layers and server behavior. Kernel-signature compatibility branches can drift.

## Test Signals
Set/get unprefixed xattrs on regular files and directories, reject empty names, reject sticky directory and non-regular/non-directory targets, validate create/replace flag mapping, and compile-test all supported handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/xattr-default.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/xattr-trusted.c -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/xattr-trusted.c

## Purpose
Implements OrangeFS handling for the Linux `trusted.*` extended attribute namespace. It enforces `CAP_SYS_ADMIN` locally before forwarding trusted xattr gets and sets to the OrangeFS inode-level xattr implementation.

## Important APIs, Types, and Functions
Provides `pvfs2_xattr_set_trusted`, `pvfs2_xattr_get_trusted`, and optional `pvfs2_xattr_trusted_handler`. Like the default handler, callback signatures vary by kernel feature macros. It calls `capable(CAP_SYS_ADMIN)`, `convert_to_internal_xattr_flags`, `pvfs2_inode_setxattr`, and `pvfs2_inode_getxattr` with `PVFS2_XATTR_NAME_TRUSTED_PREFIX`.

## Control Flow
Set logs the requested name and size, rejects empty names, denies callers without admin capability, converts flags, then forwards to the inode setter. Get follows the same empty-name and capability checks before forwarding to the inode getter.

## State and Persistence
No local state is kept. Trusted xattr data is persisted remotely through OrangeFS xattr upcalls. The static handler is registration metadata used by generic xattr routing.

## Dependencies and Integration Points
Compiled under `HAVE_XATTR` and registered by `xattr.c` when generic xattr handlers are available. It integrates with Linux capability checks and server-side OrangeFS xattr storage. Older callback paths are reached through the manual prefix router in `xattr.c`.

## Risks
Local capability checks must match Linux trusted-xattr semantics; any bypass in older manual routing would expose trusted namespace data. The code relies on the name passed after prefix stripping in older paths and after handler routing in generic paths. No object-type restrictions are enforced here beyond what VFS/server layers provide.

## Test Signals
Verify trusted xattr get/set success as an admin-capable caller, `-EPERM` as an unprivileged caller, `-EINVAL` for empty suffixes, create/replace flag behavior, and both generic-handler and manual-prefix builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/xattr-trusted.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/xattr.c -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/xattr.c

## Purpose
Coordinates Linux VFS extended attribute operations for OrangeFS. In generic xattr/ACL builds it exports the handler array for superblock registration; otherwise it provides manual get/set prefix dispatch for older kernels plus list/remove wrappers.

## Important APIs, Types, and Functions
Defines `pvfs2_xattr_handlers` with ACL access/default handlers, trusted handler, default handler, and NULL terminator when generic xattrs and POSIX ACL support are enabled. Older builds define `pvfs2_strcmp_prefix`, `pvfs2_setxattr`, and `pvfs2_getxattr`. All supported builds define `pvfs2_listxattr` and `pvfs2_removexattr` under `HAVE_XATTR`.

## Control Flow
Generic-handler builds route by VFS handler prefix. Older set/get paths test `trusted.` first, then ACL prefixes; ACL requests return `-EOPNOTSUPP` if the inode ACL flag is disabled, otherwise they fall through to default xattr handling. Default handling receives the original full name except trusted passes the stripped suffix. Listing delegates to `pvfs2_inode_listxattr`; removal delegates to `pvfs2_inode_removexattr` with `XATTR_REPLACE`.

## State and Persistence
No local state is stored. Handler arrays are static metadata. Persistent xattr state lives in OrangeFS objects and is accessed through inode-level get/set/list/remove upcalls.

## Dependencies and Integration Points
Integrates with ACL xattr handlers, default/trusted handlers, inode ACL flag helper `get_acl_flag`, Linux xattr callback signatures, `super.c` superblock registration, and symlink/directory/file inode operation tables that expose list/get/set/remove callbacks.

## Risks
Manual prefix dispatch treats ACL-enabled old-kernel operations by falling through to default handling rather than dedicated ACL handler logic, so behavior depends on surrounding ACL code. `pvfs2_removexattr` passes `NULL` prefix and the full name, which must match inode-level expectations. Handler ordering matters because the default empty prefix must come last.

## Test Signals
List and remove xattrs across namespaces, confirm generic handler array order, test ACL prefix behavior with ACL mount option on and off, verify trusted routing strips prefixes correctly in old builds, and compare behavior between generic and legacy xattr configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/PINT-le-bytefield.c -->
# sources/distributed-fs/orangefs/src/proto/PINT-le-bytefield.c

## Purpose
Implements the little-endian bytefield protocol encoder/decoder module for OrangeFS server requests and responses. It registers the concrete `PINT_encoding_functions` behind `le_bytefield_table`, handles one-buffer BMI send encodings, validates consumed decode sizes, and releases dynamically decoded structures.

## Important APIs, Types, and Functions
Main functions are `lebf_initialize`, `lebf_finalize`, `lebf_encode_calc_max_size`, `encode_common`, `lebf_encode_req`, `lebf_encode_resp`, `lebf_decode_req`, `lebf_decode_resp`, `lebf_encode_rel`, `lebf_decode_rel`, `check_req_size`, `check_resp_size`, `zero_capability`, and `zero_credential`. Important module state is `max_size_array` indexed by `PVFS_server_op` and `initializing_sizes`. It uses generated inline encode/decode functions from `pvfs2-encode-stubs.h` and `endecode-funcs.h`.

## Control Flow
Initialization allocates the max-size table, builds representative request/response structs for every server op, initializes variable-size fields such as distributions, hints, credentials, arrays, and strings, temporarily sets huge placeholder sizes, then encodes representative messages to compute maximum request/response sizes. Runtime encode calls `encode_common`, writes the generic header, encodes common request/response fields, switches on `op`, encodes operation-specific payload, records actual total size, and checks against the precomputed maximum. Runtime decode reads common fields, switches by operation, decodes the operation-specific payload, and verifies the pointer consumed exactly `input_size` bytes. Decode release frees operation-specific arrays, distributions, credentials, signatures, capabilities, object attributes, event/perf arrays, and certificate buffers.

## State and Persistence
The module owns a process-lifetime max-size cache and no durable storage. Encoded messages allocate one BMI send buffer with `BMI_memalloc`, except during size initialization where plain `malloc` is used. Decoded strings and keyvals may point into the input buffer, while arrays and nested variable fields are heap allocated and must be released through `lebf_decode_rel`.

## Dependencies and Integration Points
Integrated by `PINT-reqproto-encode.c` through `le_bytefield_table`. Depends on BMI memory allocation, byte-swap helpers, request protocol structs, distribution lookup, request descriptions, hints, security credential/capability helpers, object attribute encoders, and server op enum completeness.

## Risks
Every protocol operation must be present in initialization, encode, decode, and release switches; omissions cause size underestimates, leaks, or protocol errors. Decode performs consumed-size validation only after operation decoding, so generated decoders must not overrun malformed input. Some release cases contain copy/paste-sensitive fields, such as `PVFS_SERV_ATOMICEATTR` checking `resp->u.geteattr.val`, which deserves review. The max-size method depends on representative worst-case inputs and protocol limit constants staying accurate.

## Test Signals
Round-trip encode/decode every `PVFS_server_op`, including error-status responses that skip payload decode; run malformed-size and trailing-byte protocol tests; memory-check decode release for every op; test max-size calculations against boundary arrays/hints/xattrs; and verify protocol version changes accompany any field-layout change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/PINT-le-bytefield.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/PINT-reqproto-encode.c -->
# sources/distributed-fs/orangefs/src/proto/PINT-reqproto-encode.c

## Purpose
Provides the public protocol encode/decode dispatcher for OrangeFS request protocol messages. It initializes the supported encoding table, stamps/validates generic protocol headers, dispatches to concrete encoder modules, and releases encoded/decoded resources.

## Important APIs, Types, and Functions
Exports `PINT_encode_initialize`, `PINT_encode_finalize`, `PINT_encode`, `PINT_decode`, `PINT_encode_release`, `PINT_decode_release`, and `PINT_encode_calc_max_size`. Internal state is `PINT_encoding_table[ENCODING_TABLE_SIZE]`. The file currently supports `ENCODING_LE_BFIELD` via `le_bytefield_table`. Macros `ENCODE_EVENT_START` and `ENCODE_EVENT_STOP` define event timestamp hooks but are not used in the shown implementation.

## Control Flow
Initialization installs `le_bytefield_table`, calls its `init_fun`, writes an 8-byte generic header containing `PVFS2_PROTO_VERSION` and encoding type in BMI byte order, and records the table entry's `enc_type`. Encode records destination and encoding type on `PINT_encoded_msg`, then dispatches request or response encode by message type. Decode validates that the message is at least the generic header size, extracts protocol version and encoding type, rejects unsupported encoding, rejects incompatible major versions, rejects too-new request minor versions and too-old response minor versions, then dispatches to the matching table entry with the payload pointer after the header. Release functions dispatch to concrete release hooks if the encoding type is valid.

## State and Persistence
The encoding table is process-global initialization state. Encoded/decoded buffers are owned by concrete modules and released via dispatcher release APIs. No durable persistence exists.

## Dependencies and Integration Points
Depends on BMI address types, byte swapping, request protocol constants, event/id utilities, `PINT_encoding_table_values`, and the little-endian bytefield module. It is the API used by clients, servers, and BMI send/receive paths that need serialized `PVFS_server_req` and `PVFS_server_resp` messages.

## Risks
Only one concrete encoding is installed; unsupported types fail. `PINT_encode` assumes initialization has populated the table. Header parsing uses unaligned integer casts that may be unsafe on strict-alignment platforms. Minor-version compatibility is directional: requests can be older but not newer than server; responses can be newer but not older than client. Release on invalid decodes quietly returns only for `enc_type == -1`.

## Test Signals
Initialize/finalize repeatedly under leak checking, encode/decode both request and response messages, reject short messages, reject bad encoding type, reject incompatible major/minor protocol versions, call release after failed decode, and verify max-size dispatch for every operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/PINT-reqproto-encode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/PINT-reqproto-encode.h -->
# sources/distributed-fs/orangefs/src/proto/PINT-reqproto-encode.h

## Purpose
Declares the public OrangeFS request protocol encoding API and the carrier structures used for encoded and decoded messages.

## Important APIs, Types, and Functions
Defines `struct PINT_encoded_msg`, `struct PINT_decoded_msg`, `enum PINT_encode_msg_type`, aliases `PINT_DECODE_REQ` and `PINT_DECODE_RESP`, and prototypes for initialize/finalize, encode/decode, release, and max-size calculation. `PINT_encoded_msg` records destination, encoding type, BMI buffer type, buffer/size lists, total size, and internal single-buffer stub fields. `PINT_decoded_msg` records decoded buffer pointer, encoding type, current pointer, and an inline union for request or response storage.

## Control Flow
Callers initialize the subsystem, call `PINT_encode` before BMI send, release encoded buffers after send, call `PINT_decode` after receive, consume `target_msg->buffer` as request or response, then call `PINT_decode_release`.

## State and Persistence
The structs carry transient ownership and pointer state. Decoded message storage uses an inline request/response union, while nested variable-length decoded fields may point into the receive buffer or heap memory managed by release hooks.

## Dependencies and Integration Points
Includes `pvfs2-req-proto.h` and `bmi.h`. It is consumed by client/server protocol layers and implemented by `PINT-reqproto-encode.c` plus modules such as `PINT-le-bytefield.c`.

## Risks
Callers must respect release pairing and must not free concrete buffers manually. `buffer_list`, `size_list`, and `alloc_size_list` may point to internal stubs for the single-buffer encoder, so copying the struct by value can create aliasing bugs. `PINT_DECODE_REQ` equals `PINT_ENCODE_REQ`, so callers must pass the correct direction despite shared enum values.

## Test Signals
Compile all users against the header, verify ABI expectations of `PINT_encoded_msg`/`PINT_decoded_msg`, test release pairing with both request and response messages, and ensure decode consumers do not outlive input receive buffers for pointer-backed strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/PINT-reqproto-encode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/PINT-reqproto-module.h -->
# sources/distributed-fs/orangefs/src/proto/PINT-reqproto-module.h

## Purpose
Defines the internal plugin interface for protocol encoding modules. It abstracts concrete encoders behind function pointers and describes the generic message header shared by all encoded buffers.

## Important APIs, Types, and Functions
Defines `PINT_encoding_functions` with request/response encode, request/response decode, encode/decode release, and max-size callbacks. Defines `PINT_ENC_GENERIC_HEADER_SIZE` as 8 bytes and `PINT_encoding_table_values`, which carries the function table, module name, init/finalize hooks, generic header storage, and numeric encoding type. Declares external `le_bytefield_table`.

## Control Flow
The dispatcher initializes module table entries, calls each module's init/finalize functions, uses `generic_header` as the prefix copied into encoded buffers, and calls the operation callbacks based on encoding type and message direction.

## State and Persistence
No standalone state is stored here. Concrete modules provide global table values whose header bytes and `enc_type` are initialized at runtime.

## Dependencies and Integration Points
Consumed by `PINT-reqproto-encode.c` and implemented by `PINT-le-bytefield.c`. It depends on request/response structs, `PINT_encoded_msg`, `PINT_decoded_msg`, `PVFS_BMI_addr_t`, and `PVFS_server_op` being visible to compilation units that include it.

## Risks
The interface has no version field beyond the generic header populated elsewhere. Callback implementations must agree on buffer ownership and release semantics. Adding another encoding requires increasing or fitting within the dispatch table size in `PINT-reqproto-encode.c`.

## Test Signals
Compile a module against the interface, initialize and dispatch through `PINT_encoding_table_values`, verify the 8-byte header layout, and check release callback behavior for failed partial encodes/decodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/PINT-reqproto-module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/endecode-funcs.c -->
# sources/distributed-fs/orangefs/src/proto/endecode-funcs.c

## Purpose
Provides non-inline wrapper functions for primitive encode/decode operations. These wrappers adapt typed macro encoders to generic function-pointer shapes that accept `void *`.

## Important APIs, Types, and Functions
Defines `encode_func_uint64_t`, `decode_func_uint64_t`, `encode_func_int64_t`, `decode_func_int64_t`, `encode_func_uint32_t`, `decode_func_uint32_t`, `encode_func_int32_t`, `decode_func_int32_t`, `encode_func_string`, and `decode_func_string`. It includes `endecode-funcs.h` with `__PINT_REQPROTO_ENCODE_FUNCS_C` set and `pvfs2-encode-stubs.h`.

## Control Flow
Each wrapper casts the generic `void *x` to the concrete expected pointer type and invokes the corresponding macro from `endecode-funcs.h`, advancing `*pptr` as the macro writes or reads wire data.

## State and Persistence
No state is stored. Functions operate on caller-provided encode/decode cursors and buffers.

## Dependencies and Integration Points
Used where encode/decode functions need to be referenced as symbols rather than header-only static inline macros. It depends on primitive byte-order macros and string encoding semantics defined in `endecode-funcs.h`.

## Risks
The wrappers trust callers to pass correctly typed storage. Passing a scalar value instead of a pointer, or a pointer with insufficient lifetime for decoded strings, will corrupt memory or produce dangling references.

## Test Signals
Unit-test primitive round trips through wrapper functions, verify pointer advancement for each primitive width and string alignment, and compile/link consumers that require `encode_func_*`/`decode_func_*` symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/endecode-funcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/endecode-funcs.h -->
# sources/distributed-fs/orangefs/src/proto/endecode-funcs.h

## Purpose
Defines the macro framework used to generate OrangeFS wire encode/decode functions near protocol type declarations. It covers primitive endian conversion, string/keyval layout, decode allocation helpers, fixed-field struct encoders, array-bearing struct encoders, and enum-union dispatch.

## Important APIs, Types, and Functions
Primitive macros include `encode_uint64_t`, `decode_uint64_t`, `encode_int64_t`, `decode_int64_t`, `encode_uint32_t`, `decode_uint32_t`, `encode_int32_t`, `decode_int32_t`, `encode_char`, `decode_char`, `encode_skip4`, `decode_skip4`, `encode_string`, `decode_string`, `encode_here_string`, `decode_here_string`, `encode_PVFS_ds_keyval`, and `decode_PVFS_ds_keyval`. Structure-generation macros range from `endecode_fields_1` through larger fixed-field forms and specialized array forms such as `endecode_fields_1a`, `endecode_fields_2aa_struct`, `endecode_fields_4aaa_struct`, `endecode_fields_3a2a_struct`, and `endecode_fields_5aa_struct`. It also defines `decode_malloc`, `decode_free`, `DEFINE_STATIC_ENDECODE_FUNCS`, and `encode_enum_union_2_struct`.

## Control Flow
Generated encoders write fields in declared order and advance a `char **` cursor. Generated decoders read fields in the same order, allocate arrays based on decoded counts, and advance the cursor. String decoding points into the encoded buffer instead of allocating, while `decode_here_string` copies into existing struct storage. Array forms encode count fields first, then loop through arrays, sometimes aligning to 8-byte boundaries.

## State and Persistence
No persistent state exists. The macros define a wire format and transient decode allocations. Because decoded strings/keyvals can alias the input buffer, the receive buffer lifetime is part of decoded state.

## Dependencies and Integration Points
Included by generated stubs and protocol headers such as `pvfs2-attr.h`. It depends on BMI byte-order helpers, `roundup8`/`align8` availability from included stubs or surrounding headers, C compiler support for `typeof` outside Windows, and consistent protocol version management.

## Risks
This file is protocol-critical: any field-order or alignment change must update `PVFS2_PROTO_VERSION`. Most decoders trust decoded counts before allocation, so malformed or hostile input can request huge allocations unless upstream size checks constrain it. String size-check macro uses `strlen(*pbuf) + 5`, while actual encoding rounds to 8, so max-size callers must include padding elsewhere. Some macros allocate zero-count arrays differently from later special forms, which can affect release code.

## Test Signals
Round-trip primitive, string, keyval, fixed-field, and array-bearing structs; fuzz decode counts and lengths; run alignment tests on strict-alignment architectures; verify `PVFS2_PROTO_VERSION` changes when generated wire layout changes; and memory-check all decode/release paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/endecode-funcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/module.mk.in -->
# sources/distributed-fs/orangefs/src/proto/module.mk.in

## Purpose
Build-system fragment that adds the protocol encoding implementation files to the relevant OrangeFS build variables.

## Important APIs, Types, and Functions
No C APIs are defined. The fragment sets `DIR := src/proto`, appends `PINT-reqproto-encode.c` and `PINT-le-bytefield.c` to both `LIBSRC` and `SERVERSRC`, and appends `endecode-funcs.h` plus `endecode-funcs.c` to `LIBBMISRC`.

## Control Flow
When included by the parent make system, this fragment ensures the request protocol dispatcher and little-endian bytefield module are built into library and server targets, while primitive encode/decode wrappers are included in BMI-related library sources.

## State and Persistence
No runtime state. Build variables persist within the make evaluation context.

## Dependencies and Integration Points
Integrates the `src/proto` encoder files with the broader OrangeFS make/autoconf build. Source inclusion here must match headers and symbols referenced by client, server, and BMI components.

## Risks
Missing a source from the correct variable can produce link failures only in specific build targets. Adding a new encoder module requires updating this fragment and likely the dispatcher table. Listing a header in `LIBBMISRC` may rely on existing build rules tolerating header entries.

## Test Signals
Run full library, server, and BMI builds; inspect link lines for `PINT-reqproto-encode.o`, `PINT-le-bytefield.o`, and `endecode-funcs.o`; and test clean rebuilds after touching the listed files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/pvfs2-attr.h -->
# sources/distributed-fs/orangefs/src/proto/pvfs2-attr.h

## Purpose
Defines OrangeFS object attribute masks, object-specific attribute structures, and protocol encode/decode logic for `PVFS_object_attr`. It is the central protocol contract for common metadata, metafile distribution/datafile lists, datafile sizes, symlink targets, directory hints, distributed-directory metadata, and capabilities.

## Important APIs, Types, and Functions
Defines common masks (`PVFS_ATTR_COMMON_*`), object-specific masks (`PVFS_ATTR_META_*`, `PVFS_ATTR_DATA_SIZE`, `PVFS_ATTR_SYMLNK_TARGET`, `PVFS_ATTR_DIR_*`, `PVFS_ATTR_DISTDIR_ATTR`, `PVFS_ATTR_CAPABILITY`), and `PVFS_STATIC_ATTR_MASK`. Important structs include `PVFS_metafile_hint`, `PVFS_metafile_attr`, `PVFS_datafile_attr`, `PVFS_dirhint_server_list`, `PVFS_dirhint_layout`, `PVFS_directory_hint`, `PVFS_directory_attr`, `PVFS_symlink_attr`, and `PVFS_object_attr`. Under `__PINT_REQPROTO_ENCODE_FUNCS_C`, it defines encoders/decoders for distribution fields, dfile arrays, mirror dfile arrays, directory attrs, and full object attrs. It also defines extra-size constants used by max-size calculations.

## Control Flow
`encode_PVFS_object_attr` writes common owner/group/perms/time/mask/type fields, conditionally writes capability, conditionally writes metafile stuffed size for stuffed metafiles, then conditionally writes distribution, dfile arrays and hints, mirror dfile arrays, datafile size, symlink target, distributed-directory bitmap/handles, and directory attributes based on mask bits and object type. Decode mirrors the same mask-driven order and allocates arrays for distributions, dfile handles, mirror handles, distributed-directory bitmaps, and dirdata handles.

## State and Persistence
The header defines in-memory representations of object metadata and their wire representation. Attribute data is persisted by OrangeFS servers; this header controls how client/server messages carry that state. Decode allocations become transient ownership that higher-level release paths must free.

## Dependencies and Integration Points
Depends on internal PVFS types, storage types, distribution descriptors, security/capability definitions, and the encode macro framework. It is included by request protocol stubs and used heavily by create/getattr/setattr/listattr/tree operations and the bytefield encoder's release logic.

## Risks
The mask-driven wire format is highly order-sensitive. Any new mask or field requires protocol version updates, max-size updates, release-path updates, and compatibility tests. Decode trusts counts such as `dfile_count`, `mirror_copies_count`, bitmap size, and server count before allocating. `PVFS_STATIC_ATTR_MASK` defines fields that should not change after creation, so setter code must respect it outside this header. Extra-size constants must remain conservative for `PINT-le-bytefield.c` preallocation.

## Test Signals
Round-trip `PVFS_object_attr` for metafile, datafile, directory, symlink, stuffed/unstuffed, mirrored, distributed-directory, and capability combinations; fuzz masks with inconsistent object types; memory-check release of all decoded nested allocations; validate max encoded sizes at protocol limits; and require protocol-version review for every field or mask change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/pvfs2-attr.h -->
