# sources/distributed-fs/lizardfs/src/mount/client/lizardfs_c_api.cc

## Purpose
`lizardfs_c_api.cc` implements the public C API declared in `lizardfs_c_api.h` on top of the C++ `lizardfs::Client`. It converts opaque C handles to C++ objects, provides POSIX-style return values, manages caller-visible allocation layouts, and stores a thread-local last LizardFS error.

## Important APIs, Types, And Functions
- `liz_set_default_init_params` initializes `liz_init_params_t` with `LizardClient::FsInitParams` defaults and enum compatibility checks.
- `gLastErrorCode` backs `liz_last_err`.
- Conversion helpers `to_entry`, `to_attr_reply`, and `to_stat` map C++ reply structs to C structs.
- Context/instance lifecycle: `liz_create_context`, `liz_create_user_context`, `liz_destroy_context`, `liz_init`, `liz_init_with_params`, `liz_destroy`.
- File/directory operations: `liz_open`, `liz_read`, `liz_readv`, `liz_write`, `liz_release`, `liz_flush`, `liz_opendir`, `liz_readdir`, `liz_destroy_direntry`, `liz_releasedir`.
- Metadata operations: lookup, mknod, link, symlink, mkdir, rmdir, unlink, undel, rename, getattr, setattr, readlink, reserved/trash listing, goals, snapshots, statfs.
- Xattr/ACL operations: set/get/list/remove xattr, ACL create/destroy/print/add/get/apply/set/get.
- Cluster/lock operations: chunks info, chunkservers info, set/get/interrupt locks.

## Control Flow
Most functions cast opaque pointers to `Client`, `Context`, or `FileInfo`, call the matching `Client` nonthrowing overload, write `gLastErrorCode = ec.value()`, and return `0`/`-1`, byte counts, or pointers according to C API convention. Initialization translates passwords to MD5 digests and copies all compatible init parameters into `FsInitParams`.

Returned directory/named-inode/chunk/chunkserver arrays use packed allocation patterns: names or part tables are allocated in one buffer attached to the first returned element, then freed by paired destroy functions. `liz_readv` converts `ReadCache::Result` into small-vector iovecs and copies into the caller’s iovec.

## State And Persistence
The file owns no global client state except thread-local `gLastErrorCode`. Opaque `liz_t` points to a heap `Client`; contexts and ACLs are heap-allocated C++ objects. Persistent filesystem effects occur through the client. Some returned result buffers allocate memory that the caller must release through matching C API destroy functions.

## Dependencies And Integration Points
It depends on the public C header, common error codes, MD5 helpers, `small_vector`, `iovec_traits`, and `client.h`. It is compiled into `lizardfs-client`.

## Risks
- `liz_error_conv` and `liz_error_string` call themselves recursively because their names shadow common helpers; calls will recurse indefinitely unless qualified or renamed.
- Many API functions rely on `assert` for null pointer validation; release builds can crash or corrupt memory on invalid arguments.
- `liz_get_acl_entry` checks `(size_t)n > richacl.size()` but should reject `n == size()`; current code can advance to end and dereference.
- `liz_readlink` copies at most `size` bytes but returns the full link length without reporting truncation.
- Packed allocation destroy functions free memory through the first element; callers must not pass shifted pointers.
- `liz_get_chunkservers_info` does not set `chunks_count` even though the public struct contains it.

## Test Signals
Tests should cover lifecycle, last-error isolation per thread, parameter default parity, password/md5 handling, every allocation/destroy pair, short-buffer behavior, null/zero-size validation, readv copying, ACL boundary checks, chunks/chunkservers ownership, lock interrupt callback flow, and recursion hazards in error helper functions.
