# sources/distributed-fs/lizardfs/src/mount/client/client.h

## Purpose
`client.h` declares the public C++ `lizardfs::Client` wrapper API and its dynamic linkage state.

## Important APIs, Types, And Functions
- Type aliases expose `LizardClient` concepts: `FsInitParams`, `Inode`, `JobId`, `Context`, `EntryParam`, `ReadResult`, directory/trash/reserved replies, and `FlockWrapper`.
- `Stats` mirrors statfs fields.
- `FileInfo` extends `LizardClient::FileInfo` with inode/opendir session id and an intrusive-list hook.
- Public methods cover group updates, lookup/create/link/symlink/mkdir/unlink/rmdir/rename, open/read/write/flush/fsync/release, directory ops, trash/reserved reads, attributes, snapshots, goals, statfs, xattrs, rich ACLs, chunk/chunkserver info, and POSIX locks.
- Protected typedefs store function-pointer types for every dynamic C-linkage symbol.

## Control Flow
The class presents paired overloads for most operations: throwing and `std::error_code&`. Initialization loads symbols, stores them in member function pointers, and calls the dynamic filesystem init.

## State And Persistence
Members include all resolved function pointers, `dl_handle_`, an intrusive `FileInfoList`, a mutex, and `nextOpendirSessionID_`. `instance_count_` coordinates library loading across instances. Filesystem state is external.

## Dependencies And Integration Points
It depends on the C-linkage export header, RichACL, Boost intrusive lists, and dynamic library path `LIB_PATH "/liblizardfsmount_shared.so"`. C API implementation uses this class as the high-level client object.

## Risks
- The API exposes raw `FileInfo*`; ownership is manual and must pair with `release`/`releasedir`.
- Function pointer members must match `lizard_client_c_linkage.h` exactly or runtime calls become undefined.
- Thread-safety is limited to fileinfo list modifications; underlying singleton state may not be safe for arbitrary concurrent operations.

## Test Signals
Tests should compile consumers of the header, validate C++ method overload resolution, and exercise handle ownership and dynamic symbol coverage.
