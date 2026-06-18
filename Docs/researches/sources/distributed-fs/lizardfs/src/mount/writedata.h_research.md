# sources/distributed-fs/lizardfs/src/mount/writedata.h

## Purpose
Declares the mount client's write-data API implemented in `writedata.cc`.

## Important APIs, Types, And Functions
The API initializes and tears down the write subsystem (`write_data_init`, `write_data_term`), creates and releases per-inode write handles (`write_data_new`, `write_data_end`), writes buffered data (`write_data`), flushes data by handle or inode (`write_data_flush`, `write_data_flush_inode`), exposes cached maximum file length (`write_data_getmaxfleng`), and coordinates truncate with master/chunkserver state (`write_data_truncate`). `write_data_truncate` returns updated `Attributes`.

## Control Flow
Callers initialize once with cache size, retry count, worker count, write window, chunkserver timeout, and per-inode cache percentage. File operations obtain a `void*` inode handle, pass write ranges to `write_data`, flush as needed, and close with `write_data_end`.

## State And Persistence Behavior
The header intentionally hides `inodedata`; all persistent effects are delegated to the implementation and master/chunkserver writes.

## Dependencies And Integration Points
Depends only on `common/platform.h`, integer types, and `common/attributes.h`, keeping the public mount API small for FUSE/client users.

## Risks And Edge Cases
The `void*` handle API requires correct pairing of `write_data_new` and `write_data_end`; misuse can leak or prematurely free inode state. Return values are LizardFS status/error codes, not standard errno in all paths.

## Test Signals
Covered indirectly by write subsystem tests and call sites that validate flush/truncate semantics.
