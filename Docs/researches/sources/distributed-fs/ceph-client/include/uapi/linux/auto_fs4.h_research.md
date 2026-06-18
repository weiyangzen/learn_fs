<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/auto_fs4.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/auto_fs4.h

## Purpose
Compatibility wrapper for autofs version 4 userspace includes. It re-exports the definitions from `linux/auto_fs.h`.

## Important APIs, Types, And Functions
No new ABI is defined. Including this header provides the `auto_fs.h` protocol constants, packet structs, helper functions, and ioctls.

## Control Flow
Consumers that historically included `auto_fs4.h` compile against the unified autofs ABI without changing source.

## State And Persistence
No separate state. Runtime state is the autofs state described by `auto_fs.h`.

## Dependencies And Integration Points
Depends directly on `<linux/auto_fs.h>`. Integrates with older automount source code expecting the v4 header name.

## Risks And Edge Cases
The main risk is assuming it only contains v4 definitions; it actually exposes the unified current autofs ABI.

## Test Signals
Compile compatibility tests for old autofs userspace includes and confirmation that expected v4/v5 symbols are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/auto_fs4.h -->
