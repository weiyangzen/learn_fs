# sources/distributed-fs/ceph/src/rgw/rgw_ssd_driver.cc

## Purpose
`rgw_ssd_driver.cc` implements the SSD-backed D4N cache driver. It maps RGW cache keys into a local filesystem hierarchy, stores cached data in ordinary files, stores RGW/cache metadata in extended attributes, exposes synchronous and POSIX AIO-backed read/write paths, and restores dirty/clean cache records after restart.

## Important APIs, Types, and Functions
Static helpers split `CACHE_DELIM` keys, derive `<cache>/<bucket_id>/<object>/<version[_offset_len]>`, create directories through temporary names and atomic rename, and return final paths. `SSDDriver::initialize()` prepares or evicts the cache directory and initializes libc aio tunables. `put()`, `get()`, `append_data()`, `delete_data()`, and `rename()` implement the core file operations. Template `get_async()` and `put_async()` wrap `AsyncReadOp` and `AsyncWriteRequest` in `ceph::async::Completion`; public `get_async()`/`put_async()` adapt those operations to `rgw::Aio`. Attribute methods use `listxattr()`, `getxattr()`, `setxattr()`, and `removexattr()`.

## Control Flow
Writes create a temporary file path, prepare an `aiocb`, copy the bufferlist into heap memory, submit `aio_write()`, set xattrs on the temporary file in the callback, refresh free-space accounting, then rename the temp file into the final version path. Reads open the resolved path, allocate a bufferlist-backed buffer, submit `aio_read()`, and dispatch the completion with the data. Synchronous wrappers either run the async path on a yield executor or block through `ceph::async::use_blocked`.

`restore_blocks_objects()` scans the cache directory by bucket and object, parses version or block filenames, reads dirty/local-weight/metadata xattrs, rebuilds object keys, decodes ACL owner information, and calls supplied object/block callbacks.

## State and Persistence Behavior
Persistent state is the local directory tree plus file xattrs. The driver tracks `Partition`, `free_space`, `cct`, an `admin` flag, and a mutex for free-space updates. Data writes are made atomic at file-name level by temp-write plus rename, but xattr writes happen before the rename. Dirty cached objects store enough metadata to reconstruct object callbacks.

## Dependencies and Integration Points
The file depends on `CacheDriver`, RGW AIO throttling, `DoutPrefixProvider`, `rgw::sal::Attrs`, RGW cache xattr names, ACL decoding, URL encode/decode helpers, `std::filesystem`, POSIX file I/O, xattrs, and libc AIO. It is the file-backed cache backend used by D4N cache code and administrative restore flows.

## Risks
The key parser only handles 3- and 5-token forms, so malformed keys can yield empty paths. `get_attr()` returns positive `errno` in some paths while other methods return negative errors. Write callbacks assign errors from `ret` after attr failure even though `ret` may be zero. `malloc()` failure closes the fd but returns the old open result. Directory creation/removal races are partially handled, but path-based operations remain sensitive to concurrent deletes. `get()` allocates a stack small_vector sized by caller length, which can be large.

## Test Signals
Exercise initialization with and without eviction, admin mode, key parsing for head and block keys, temp-file rename atomicity, xattr round trips, read/write/append/delete paths, ENOENT retry on write, concurrent delete/write races, restore of dirty and clean entries, ACL decode failures, reserve-space accounting, and AIO error callbacks.
