# sources/distributed-fs/lizardfs/src/mount/client/lizard_client_c_linkage.cc

## Purpose
`lizard_client_c_linkage.cc` exposes unmangled wrapper functions around the singleton `LizardClient` namespace so `client.cc` can load them with `dlsym`. It catches exceptions and returns LizardFS integer status codes or status/value pairs.

## Important APIs, Types, And Functions
- `lizardfs_fs_init`/`lizardfs_fs_term` start and stop `LizardClient`.
- Metadata wrappers include lookup, mknod, link, symlink, mkdir, rmdir, unlink, undel, rename, getattr, setattr, goals, snapshots, xattrs, and statfs.
- IO wrappers include open, read, read special inode, write, release, flush, fsync, opendir/readdir/releasedir.
- Cluster wrappers include chunks info and chunkserver list.
- Lock wrappers include getlk, setlk send/recv, and interrupt.

## Control Flow
Each wrapper calls the corresponding `LizardClient` function in a `try` block. `RequestException` is converted to its embedded LizardFS error code; other exceptions become `LIZARDFS_ERROR_IO` except termination, which suppresses all exceptions. Pair-returning functions return `{status, default_value}` on failure. `lizardfs_readdir` updates the readdir session with the last returned inode and `releasedir` drops that session.

## State And Persistence
The file does not own state directly but operates on global/singleton `LizardClient` state. It mutates filesystem metadata/data through underlying calls and updates readdir session state.

## Dependencies And Integration Points
It depends on `mount/lizard_client.h`, lock protocol types, and `lizard_client_c_linkage.h`. It is compiled into `lizardfsmount_shared`, which `Client` dynamically loads.

## Risks
- C-linkage functions return C++ types such as `std::pair`, `std::vector`, and `std::string` references; this is intended for same-toolchain dynamic loading, not a stable C ABI.
- Catch-all conversion to IO can obscure programming errors.
- `Context` is passed by value for some wrappers and by reference for others; consistency matters for context mutations.
- ABI mismatch between this file and `client.h` function pointer typedefs will fail at runtime or worse.

## Test Signals
Tests should verify every declared symbol is exported and loadable, each wrapper maps `RequestException` to status, generic exceptions to IO, readdir session updates/drop calls, and lock send/recv sequencing.
