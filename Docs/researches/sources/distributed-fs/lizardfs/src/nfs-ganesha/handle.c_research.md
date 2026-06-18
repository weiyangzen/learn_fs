# sources/distributed-fs/lizardfs/src/nfs-ganesha/handle.c

## Purpose
Implements object-handle operations for the LizardFS FSAL: namespace manipulation, file open/read/write/commit/close, attributes, links, locks, and handle serialization.

## Important APIs, Types, And Functions
`lzfs_fsal_handle_ops_init` installs the object operation table. Major functions include lookup/readdir/mkdir/mknode/symlink/readlink/getattrs/rename/unlink/link, `handle_to_wire`, `handle_to_key`, `open2`, `reopen2`, `read2`, `write2`, `commit2`, `setattr2`, `close2`, `status2`, `merge`, and `lzfs_fsal_lock_op2`. Internal helpers manage `lzfs_fsal_fd` open/close, share reservations, and `fsal_find_fd` integration.

## Control Flow
Directory and metadata operations translate FSAL parameters to LizardFS C API calls through `liz_cred_*`, convert attributes with `posix2fsal_attributes_all`, and wrap results in `lzfs_fsal_handle`. Open flows either open an existing handle/name or create with `mknod`, handle exclusive verifier checks, set requested attributes, and maintain share counters for stateful opens. Read/write find or temporarily open a usable FD, call LizardFS I/O, optionally fsync for stable writes, then close temporary descriptors and unlock Ganesha object locks. `setattr2` maps FSAL attr masks to LizardFS set masks and handles ACL updates. Lock operations convert FSAL locks to `liz_lock_info_t`, set lock owner on fileinfo, and call getlk/setlk.

## State And Persistence Behavior
Each FSAL object stores inode, unique key, optional global FD, export pointer, and share state. Per-open state stores an FD in `lzfs_fsal_state_fd`. Persistent namespace, attribute, lock, and file data changes are delegated to LizardFS master/client APIs.

## Dependencies And Integration Points
Depends on Ganesha FSAL commonlib/share helpers, `common/lizardfs_error_codes.h`, `context_wrap`, `lzfs_internal`, and ACL helpers. It is the core bridge from NFS requests to LizardFS client operations.

## Risks And Edge Cases
Share counter updates and FD reopen/close paths are subtle; error unwinds must undo reservations. `close2` updates share counters using `lzfs_obj->fd.openflags` rather than the state FD, which may be wrong for stateful descriptors. `read2` treats `offset == -1` as error even though offset is unsigned. Some create paths unset and restore `ATTR_MODE` on caller-provided attr lists, so side effects must be expected. Lock operations retry once on `ERR_FSAL_DELAY`, but temporary FD cleanup and leaked context risk in `liz_cred_getlk` matter.

## Test Signals
Needs broad FSAL integration tests: create/open/exclusive verifier, directory pagination, stable write/commit, setattr size/truncate, ACL get/set, link/rename/unlink, and lock conflict/probe behavior.
