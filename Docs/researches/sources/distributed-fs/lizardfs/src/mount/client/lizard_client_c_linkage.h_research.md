# sources/distributed-fs/lizardfs/src/mount/client/lizard_client_c_linkage.h

## Purpose
`lizard_client_c_linkage.h` declares unmangled functions exported by `lizardfsmount_shared` for dynamic lookup by the C++ `Client` wrapper.

## Important APIs, Types, And Functions
The header declares `extern "C"` wrappers for filesystem init/term, metadata operations, directory operations, file IO, special inode reads, xattrs, goals, snapshots, statfs, chunks/chunkservers, and POSIX lock operations. Return conventions are integer LizardFS status codes or `std::pair<status,value>` for value-returning calls.

## Control Flow
The header is a dynamic ABI contract: `client.cc` uses `decltype(&lizardfs_*)` typedefs and `dlsym` names that must match these declarations exactly.

## State And Persistence
No state is declared. The functions operate on underlying singleton `LizardClient` state.

## Dependencies And Integration Points
It includes `mount/lizard_client.h` and `protocol/lock_info.h`. It intentionally bridges C++ singleton code and dynamic library instance isolation.

## Risks
- Despite `extern "C"`, many signatures use C++ standard-library types, so this is not a portable C ABI.
- The comment warns implementations should not throw; any uncaught exception crossing the dynamic boundary would be dangerous.
- Header and implementation drift affects runtime symbol calls.

## Test Signals
ABI tests should compile both producer and consumer, run `dlsym` for every symbol, and exercise representative pair-returning functions.
