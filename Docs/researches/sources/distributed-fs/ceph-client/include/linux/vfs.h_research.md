# sources/distributed-fs/ceph-client/include/linux/vfs.h

## Purpose
This lightweight header includes filesystem statfs definitions under the traditional `linux/vfs.h` include path.

## Important APIs, types, and functions
No new APIs are defined directly. It re-exports `linux/statfs.h` types and constants to callers that include `linux/vfs.h`.

## Control flow, state, and persistence
There is no control flow or state. Filesystem behavior is entirely in the included statfs and VFS implementation headers/sources.

## Dependencies and integration points
It depends on `linux/statfs.h` and integrates with legacy include users in filesystem and VFS code.

## Risks and test signals
The main risk is assuming this wrapper contains broader VFS definitions. Build coverage for include users is the relevant signal.
